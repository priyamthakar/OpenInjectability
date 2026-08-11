"""Traceable Markdown, self-contained HTML, and PDF assessment reports."""

from __future__ import annotations

import base64
import html
import mimetypes
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

from ._version import __version__
from .models import AssessmentResult, RejectedAssessment

DISCLAIMER = (
    "This is the predicted fluid-resistance force from an idealized Newtonian "
    "needle-flow model. It is not total injection force. It excludes syringe friction, "
    "break-loose force, device losses, tissue backpressure, and human factors. "
    "Experimental verification is required."
)

ASSUMPTIONS = (
    "single-phase incompressible liquid",
    "time-independent Newtonian viscosity at the declared use temperature",
    "steady, fully developed laminar flow through an ideal circular needle",
    "declared needle inner diameter and length are authoritative",
    "minor losses and every non-fluid device or tissue contribution are excluded",
)


def _require_float(value: float | None) -> float:
    if value is None:
        raise ValueError("expected a numeric assessment output, got None")
    return value


def _pdf_safe(text: str) -> str:
    """Map scientific Unicode to legible ASCII for ReportLab's core fonts."""

    replacements = {
        "Δ": "Delta ",
        "μ": "mu ",
        "π": "pi ",
        "γ̇": "gamma_dot ",
        "·": "*",
        "×": "x",
        "°": " deg",
        "⁻¹": "^-1",
        "¹": "^1",
        "²": "^2",
        "³": "^3",
        "⁴": "^4",
        "–": "-",
        "—": "-",
        "−": "-",
        "≥": ">=",
        "≤": "<=",
    }
    for source, replacement in replacements.items():
        text = text.replace(source, replacement)
    return text.replace("**", "").replace("`", "")


def _input_summary_lines(result: AssessmentResult) -> list[str]:
    """Return original display values plus canonical normalized values."""

    inp = result.normalized_input
    flow = inp.get("flow_rate_ml_s")
    time = inp.get("injection_time_s")
    delivery = (
        f"{flow:.6g} mL/s"
        if isinstance(flow, (int, float))
        else f"{time:.6g} s"
        if isinstance(time, (int, float))
        else "not declared"
    )
    delivery_label = "Flow rate" if isinstance(flow, (int, float)) else "Injection time"
    return [
        f"- Package version: `{result.package_version}`",
        f"- Formulation: `{inp['formulation_id']}`",
        (
            "- Viscosity (declared): "
            f"{inp['viscosity_value']:.6g} {inp['viscosity_unit']} at "
            f"{inp['viscosity_temperature_c']:.6g} °C; use temperature "
            f"{inp['use_temperature_c']:.6g} °C"
        ),
        f"- Viscosity (canonical): {inp['viscosity_pa_s']:.9g} Pa·s",
        f"- Rheology evidence: `{inp['newtonian_evidence']}` (`{inp['rheology_class']}`)",
        (
            "- Needle (declared): "
            f"ID {inp['needle_id_mm']:.6g} mm × {inp['needle_length_mm']:.6g} mm; "
            f"source `{inp['needle_geometry_source']}`"
        ),
        (f"- Needle (canonical): ID {inp['needle_id_m']:.9g} m × {inp['needle_length_m']:.9g} m"),
        (
            "- Barrel (declared): "
            f"ID {inp['barrel_id_mm']:.6g} mm; source `{inp['barrel_geometry_source']}`"
        ),
        f"- Barrel (canonical): ID {inp['barrel_id_m']:.9g} m",
        f"- Volume: {inp['volume_ml']:.6g} mL ({inp['volume_m3']:.9g} m³)",
        f"- {delivery_label}: {delivery}",
    ]


def markdown_report(
    results: Iterable[AssessmentResult],
    source_sha256: str,
    *,
    source_path: str | None = None,
    rejected: Sequence[RejectedAssessment] = (),
    reproducibility_command: str | None = None,
    figure_paths: Sequence[str | Path] = (),
) -> str:
    """Render the complete human-review report model as Markdown."""

    items = list(results)
    lines = [
        "# OpenInjectability assessment",
        "",
        f"**Input source:** `{source_path or 'in-memory / assess-one'}`",
        f"**Input SHA-256:** `{source_sha256}`",
        f"**Accepted scenarios:** {len(items)}",
        f"**Rejected rows:** {len(rejected)}",
        "",
        f"> {DISCLAIMER}",
        "",
        "## Equations and assumptions",
        "",
        "- Flow: `Q = V / t`",
        "- Needle pressure drop: `ΔP = 128 μ L Q / (π d⁴)`",
        "- Barrel area: `A = π D_b² / 4`",
        "- Predicted fluid-resistance force: `F = ΔP A = 32 μ L Q D_b² / d⁴`",
        "- Apparent wall shear rate: `γ̇ = 32 Q / (π d³)`",
        "",
        "Assumptions:",
        "",
        *(f"- {assumption}" for assumption in ASSUMPTIONS),
        "",
    ]
    for result in items:
        output = result.outputs
        inp = result.normalized_input
        reynolds = output["reynolds_number"]
        reynolds_text = (
            f"{reynolds:.6g}"
            if reynolds is not None
            else "not calculated (`LAMINARITY_NOT_NUMERICALLY_VERIFIED`)"
        )
        lines.extend(
            [
                f"## {inp['scenario_id']}",
                "",
                f"- Run ID: `{result.run_id}`",
                f"- Generated UTC: `{result.generated_at_utc}`",
                f"- Status: `{result.status}`",
                f"- Model: `{result.model_id}`",
                f"- Validation: `{result.validation_status}`",
                *_input_summary_lines(result),
                (
                    "- Calculated flow rate: "
                    f"{_require_float(output['flow_rate_m3_s']) * 1_000_000:.6g} mL/s"
                ),
                (
                    "- Needle pressure drop: "
                    f"{_require_float(output['needle_pressure_drop_pa']) / 1e6:.6g} MPa"
                ),
                (
                    "- Predicted fluid-resistance force: "
                    f"{_require_float(output['fluid_resistance_force_n']):.6g} N"
                ),
                f"- Calculated injection time: {_require_float(output['injection_time_s']):.6g} s",
                f"- Wall shear rate: {_require_float(output['wall_shear_rate_s_1']):.6g} s⁻¹",
                f"- Mean needle velocity: {_require_float(output['mean_velocity_m_s']):.6g} m/s",
                f"- Reynolds diagnostic: {reynolds_text}",
                "",
                "### Deterministic sensitivity",
                "",
                "These one-at-a-time perturbations are not probabilistic uncertainty intervals.",
                "",
            ]
        )
        lines.extend(
            (
                f"- `{item.input_name}` {item.relative_change:+.1%}: pressure "
                f"{item.pressure_relative_change:+.2%}, force "
                f"{item.force_relative_change:+.2%}; analytical force elasticity "
                f"{item.analytical_force_elasticity:+.0f}"
            )
            for item in result.sensitivity
        )
        lines.extend(["", "### Warnings", ""])
        if result.warnings:
            lines.extend(
                f"- `{warning.code}` ({warning.severity}, field `{warning.field}`) — "
                f"{warning.message} Remediation: {warning.remediation}"
                for warning in result.warnings
            )
        else:
            lines.append("- None")
        lines.extend(["", "### Exclusions", ""])
        lines.extend(f"- {item}" for item in result.exclusions)
        lines.append("")

    lines.extend(["## Rejected rows", ""])
    if rejected:
        lines.extend(
            f"- CSV row {item.row_number}, scenario `{item.scenario_id}`: "
            f"`{item.error_code}` ({item.error_type}, field `{item.field}`) — {item.message}"
            for item in rejected
        )
    else:
        lines.append("- None")

    if figure_paths:
        lines.extend(["", "## Figures", ""])
        lines.extend(f"![{Path(path).stem}]({Path(path).name})" for path in figure_paths)

    lines.extend(
        [
            "",
            "## References",
            "",
            (
                "- Hagen–Poiseuille circular-capillary relation; implementation and source "
                "status are documented in `docs/scientific-basis.md` and "
                "`PROJECT_SPECIFICATION.md`."
            ),
            "- Package claims-to-evidence map: `VALIDATION.md`.",
            "",
            "## Reproducibility",
            "",
            f"`{reproducibility_command or 'Use the same package version and declared inputs.'}`",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def html_report(
    results: Iterable[AssessmentResult],
    source_sha256: str,
    *,
    source_path: str | None = None,
    rejected: Sequence[RejectedAssessment] = (),
    reproducibility_command: str | None = None,
    figure_paths: Sequence[str | Path] = (),
) -> str:
    """Render a self-contained HTML report, embedding supplied PNG figures."""

    markdown = markdown_report(
        results,
        source_sha256,
        source_path=source_path,
        rejected=rejected,
        reproducibility_command=reproducibility_command,
        figure_paths=figure_paths,
    )
    body: list[str] = []
    list_open = False
    for raw in markdown.splitlines():
        if raw.startswith("!["):
            continue
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
    for raw_path in figure_paths:
        path = Path(raw_path)
        media_type = mimetypes.guess_type(path.name)[0] or "image/png"
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        body.append(
            f'<figure><img src="data:{media_type};base64,{encoded}" '
            f'alt="{html.escape(path.stem)}"><figcaption>{html.escape(path.stem)}</figcaption></figure>'
        )
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        "<title>OpenInjectability assessment</title>"
        "<style>body{font:16px/1.5 system-ui;max-width:960px;margin:2rem auto;padding:0 1rem}"
        "aside{border-left:4px solid #555;padding:1rem;background:#f3f3f3}"
        "code{background:#eee;padding:.1rem .25rem}h2{margin-top:2rem}"
        "img{max-width:100%;height:auto}figure{margin:2rem 0}</style></head><body>"
        + "\n".join(body)
        + "</body></html>\n"
    )


def write_report(
    results: Iterable[AssessmentResult],
    source_sha256: str,
    path: str | Path,
    *,
    source_path: str | None = None,
    rejected: Sequence[RejectedAssessment] = (),
    reproducibility_command: str | None = None,
    figure_paths: Sequence[str | Path] = (),
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    suffix = destination.suffix.lower()
    materialized = tuple(results)
    if suffix in {".md", ".markdown"}:
        text = markdown_report(
            materialized,
            source_sha256,
            source_path=source_path,
            rejected=rejected,
            reproducibility_command=reproducibility_command,
            figure_paths=figure_paths,
        )
    elif suffix in {".html", ".htm"}:
        text = html_report(
            materialized,
            source_sha256,
            source_path=source_path,
            rejected=rejected,
            reproducibility_command=reproducibility_command,
            figure_paths=figure_paths,
        )
    elif suffix == ".pdf":
        _write_pdf(
            materialized,
            source_sha256,
            destination,
            source_path=source_path,
            rejected=rejected,
            reproducibility_command=reproducibility_command,
            figure_paths=figure_paths,
        )
        return
    else:
        raise ValueError("report extension must be .md, .html, or .pdf")
    destination.write_text(text, encoding="utf-8")


def _write_pdf(
    results: tuple[AssessmentResult, ...],
    source_sha256: str,
    destination: Path,
    *,
    source_path: str | None,
    rejected: Sequence[RejectedAssessment],
    reproducibility_command: str | None,
    figure_paths: Sequence[str | Path],
) -> None:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer
    except ImportError as exc:  # pragma: no cover - depends on optional environment
        raise RuntimeError(
            "PDF output requires the 'reports' extra: pip install openinjectability[reports]"
        ) from exc

    styles = getSampleStyleSheet()
    markdown = markdown_report(
        results,
        source_sha256,
        source_path=source_path,
        rejected=rejected,
        reproducibility_command=reproducibility_command,
    )
    story: list[object] = []
    for raw in markdown.splitlines():
        if not raw:
            story.append(Spacer(1, 1.5 * mm))
        elif raw.startswith("# "):
            story.append(Paragraph(html.escape(_pdf_safe(raw[2:])), styles["Title"]))
        elif raw.startswith("## "):
            story.append(Paragraph(html.escape(_pdf_safe(raw[3:])), styles["Heading2"]))
        elif raw.startswith("### "):
            story.append(Paragraph(html.escape(_pdf_safe(raw[4:])), styles["Heading3"]))
        elif raw.startswith("> "):
            story.append(
                Paragraph(
                    f"<b>Scientific boundary:</b> {html.escape(_pdf_safe(raw[2:]))}",
                    styles["BodyText"],
                )
            )
        else:
            story.append(Paragraph(html.escape(_pdf_safe(raw)), styles["BodyText"]))
    for raw_path in figure_paths:
        image = Image(str(raw_path))
        scale = min((170 * mm) / image.drawWidth, (220 * mm) / image.drawHeight, 1.0)
        image.drawWidth *= scale
        image.drawHeight *= scale
        story.extend([Spacer(1, 3 * mm), image])
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

    def footer(canvas: Any, document_template: Any) -> None:
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColorRGB(0.3, 0.3, 0.3)
        canvas.drawString(18 * mm, 10 * mm, f"OpenInjectability {__version__} - research use")
        canvas.drawRightString(
            A4[0] - 18 * mm,
            10 * mm,
            f"Page {document_template.page}",
        )
        canvas.restoreState()

    document.build(story, onFirstPage=footer, onLaterPages=footer)
