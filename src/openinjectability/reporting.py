"""Markdown and self-contained HTML reports from structured results."""

from __future__ import annotations

import html
from pathlib import Path
from typing import Iterable

from .models import AssessmentResult


DISCLAIMER = (
    "This is the predicted fluid-resistance force from an idealized Newtonian "
    "needle-flow model. It excludes syringe friction, break-loose force, device "
    "losses, tissue backpressure, and human factors. Experimental verification is required."
)


def markdown_report(results: Iterable[AssessmentResult], source_sha256: str) -> str:
    items = list(results)
    lines = [
        "# OpenInjectability assessment",
        "",
        f"**Input SHA-256:** `{source_sha256}`  ",
        f"**Scenarios:** {len(items)}",
        "",
        f"> {DISCLAIMER}",
        "",
    ]
    for result in items:
        output = result.outputs
        inp = result.normalized_input
        lines.extend(
            [
                f"## {inp['scenario_id']}",
                "",
                f"- Status: `{result.status}`",
                f"- Model: `{result.model_id}`",
                f"- Validation: `{result.validation_status}`",
                f"- Needle pressure drop: {output['needle_pressure_drop_pa'] / 1e6:.6g} MPa",
                (
                    "- Predicted fluid-resistance force: "
                    f"{output['fluid_resistance_force_n']:.6g} N"
                ),
                f"- Injection time: {output['injection_time_s']:.6g} s",
                f"- Wall shear rate: {output['wall_shear_rate_s_1']:.6g} s^-1",
                "",
                "### Warnings",
                "",
            ]
        )
        if result.warnings:
            lines.extend(f"- `{warning.code}` — {warning.message}" for warning in result.warnings)
        else:
            lines.append("- None")
        lines.extend(["", "### Exclusions", ""])
        lines.extend(f"- {item}" for item in result.exclusions)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def html_report(results: Iterable[AssessmentResult], source_sha256: str) -> str:
    markdown = markdown_report(results, source_sha256)
    # Deliberately small renderer: escape first, then support only headings/list/quote/code.
    body: list[str] = []
    list_open = False
    for raw in markdown.splitlines():
        line = html.escape(raw)
        if line.startswith("- "):
            if not list_open:
                body.append("<ul>")
                list_open = True
            body.append(f"<li>{line[2:]}</li>")
            continue
        if list_open:
            body.append("</ul>")
            list_open = False
        if line.startswith("### "):
            body.append(f"<h3>{line[4:]}</h3>")
        elif line.startswith("## "):
            body.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("# "):
            body.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("&gt; "):
            body.append(f"<aside>{line[5:]}</aside>")
        elif line:
            body.append(f"<p>{line}</p>")
    if list_open:
        body.append("</ul>")
    return (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        "<title>OpenInjectability assessment</title>"
        "<style>body{font:16px/1.5 system-ui;max-width:900px;margin:2rem auto;padding:0 1rem}"
        "aside{border-left:4px solid #8a4b08;padding:1rem;background:#fff4e5}"
        "code{background:#eee;padding:.1rem .25rem}h2{margin-top:2rem}</style></head><body>"
        + "\n".join(body)
        + "</body></html>\n"
    )


def write_report(
    results: Iterable[AssessmentResult], source_sha256: str, path: str | Path
) -> None:
    destination = Path(path)
    suffix = destination.suffix.lower()
    materialized = tuple(results)
    if suffix in {".md", ".markdown"}:
        text = markdown_report(materialized, source_sha256)
    elif suffix in {".html", ".htm"}:
        text = html_report(materialized, source_sha256)
    elif suffix == ".pdf":
        _write_pdf(materialized, source_sha256, destination)
        return
    else:
        raise ValueError("report extension must be .md, .html, or .pdf")
    destination.write_text(text, encoding="utf-8")


def _write_pdf(
    results: tuple[AssessmentResult, ...], source_sha256: str, destination: Path
) -> None:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    except ImportError as exc:  # pragma: no cover - depends on optional environment
        raise RuntimeError(
            "PDF output requires the 'reports' extra: "
            "pip install openinjectability[reports]"
        ) from exc

    styles = getSampleStyleSheet()
    story = [
        Paragraph("OpenInjectability assessment", styles["Title"]),
        Spacer(1, 4 * mm),
        Paragraph(f"Input SHA-256: {html.escape(source_sha256)}", styles["BodyText"]),
        Paragraph(f"Scenarios: {len(results)}", styles["BodyText"]),
        Spacer(1, 3 * mm),
        Paragraph(f"<b>Scientific boundary:</b> {html.escape(DISCLAIMER)}", styles["BodyText"]),
    ]
    for result in results:
        output = result.outputs
        inp = result.normalized_input
        story.extend(
            [
                Spacer(1, 5 * mm),
                Paragraph(html.escape(str(inp["scenario_id"])), styles["Heading2"]),
                Paragraph(f"Status: {result.status}", styles["BodyText"]),
                Paragraph(f"Model: {result.model_id}", styles["BodyText"]),
                Paragraph(
                    f"Needle pressure drop: {output['needle_pressure_drop_pa'] / 1e6:.6g} MPa",
                    styles["BodyText"],
                ),
                Paragraph(
                    "Predicted fluid-resistance force: "
                    f"{output['fluid_resistance_force_n']:.6g} N",
                    styles["BodyText"],
                ),
                Paragraph(
                    f"Injection time: {output['injection_time_s']:.6g} s",
                    styles["BodyText"],
                ),
            ]
        )
        for warning in result.warnings:
            story.append(
                Paragraph(
                    f"Warning {html.escape(warning.code)}: {html.escape(warning.message)}",
                    styles["BodyText"],
                )
            )
    document = SimpleDocTemplate(
        str(destination),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="OpenInjectability assessment",
        author="OpenInjectability",
    )
    document.build(story)
