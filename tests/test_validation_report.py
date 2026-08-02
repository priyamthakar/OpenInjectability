"""Tests for Phase D experimental comparison pipeline infrastructure."""

from __future__ import annotations

import json
from pathlib import Path

from openinjectability.cli import main
from openinjectability.validation_report import (
    FORBIDDEN_STATUS,
    REPORT_STATUS_COMPARISON,
    REPORT_STATUS_INSUFFICIENT,
    compare_row,
    compute_summary,
    load_panel,
    write_report,
)


def _empty_panel() -> dict:
    return {"schema_version": "1.0", "meta": {"purpose": "empty"}, "rows": []}


def _synthetic_smoke_row(**overrides: object) -> dict:
    """Minimal synthetic row for code-path smoke only; not experimental evidence."""

    row = {
        "scenario_id": "synthetic-smoke-1",
        "fluid": "synthetic-newtonian-smoke",
        "viscosity_value": 35.0,
        "viscosity_unit": "cP",
        "viscosity_temperature_c": 25.0,
        "newtonian_evidence": "SYNTHETIC-SMOKE-TEST-NOT-EXPERIMENTAL",
        "needle_id_mm": 0.21,
        "needle_length_mm": 12.7,
        "needle_geometry_source": "synthetic smoke geometry",
        "barrel_id_mm": 6.35,
        "barrel_geometry_source": "synthetic smoke barrel",
        "volume_ml": 2.0,
        "injection_time_s": 15.0,
        # Arbitrary positive measured force for relative-error arithmetic only.
        "measured_fluid_force_n": 40.0,
        "force_definition": "fluid_only",
        "method_notes": "Synthetic smoke-test row; not laboratory data.",
        "citation_or_lab_log": "tests/test_validation_report.py",
        "is_synthetic_smoke_test": True,
    }
    row.update(overrides)
    return row


def test_empty_panel_insufficient_data_no_crash(tmp_path: Path) -> None:
    panel_path = tmp_path / "empty_panel.json"
    panel_path.write_text(json.dumps(_empty_panel()), encoding="utf-8")
    panel = load_panel(panel_path)
    written = write_report(panel, tmp_path / "out", panel_path=panel_path)
    summary = written["summary"]
    assert summary["status"] == REPORT_STATUS_INSUFFICIENT
    assert summary["n"] == 0
    assert summary["validation_claim"] == REPORT_STATUS_INSUFFICIENT
    assert summary["validation_claim"] != FORBIDDEN_STATUS
    assert summary["status"] != FORBIDDEN_STATUS
    report = json.loads(Path(written["json_path"]).read_text(encoding="utf-8"))
    assert report["summary"]["status"] == REPORT_STATUS_INSUFFICIENT
    assert report["summary"]["status"] != FORBIDDEN_STATUS
    assert report["summary"]["validation_claim"] != FORBIDDEN_STATUS
    assert Path(written["markdown_path"]).is_file()
    assert Path(written["manifest_path"]).is_file()
    manifest = Path(written["manifest_path"]).read_text(encoding="utf-8")
    assert "experimental_comparison.json" in manifest
    assert written["input_panel_sha256"]


def test_reject_total_glide_force_definition() -> None:
    row = _synthetic_smoke_row(force_definition="total_glide")
    result = compare_row(row)
    assert result["status"] == "rejected"
    assert "total_glide" in result["error"]
    assert "model_fluid_resistance_force_n" not in result


def test_reject_unknown_force_definition() -> None:
    row = _synthetic_smoke_row(force_definition="unknown")
    result = compare_row(row)
    assert result["status"] == "rejected"
    assert "unknown" in result["error"]


def test_synthetic_smoke_calls_assess_and_never_independently_validated(
    tmp_path: Path,
) -> None:
    panel = {
        "schema_version": "1.0",
        "meta": {"purpose": "synthetic smoke only"},
        "rows": [_synthetic_smoke_row()],
    }
    panel_path = tmp_path / "synthetic_panel.json"
    panel_path.write_text(json.dumps(panel), encoding="utf-8")
    written = write_report(panel, tmp_path / "out", panel_path=panel_path)
    summary = written["summary"]
    assert summary["status"] == REPORT_STATUS_COMPARISON
    assert summary["n"] == 1
    assert summary["validation_claim"] != FORBIDDEN_STATUS
    assert summary["status"] != FORBIDDEN_STATUS
    assert summary["contains_synthetic_smoke_test"] is True

    report = json.loads(Path(written["json_path"]).read_text(encoding="utf-8"))
    comparison = report["comparisons"][0]
    assert comparison["status"] == "compared"
    assert comparison["is_synthetic_smoke_test"] is True
    assert comparison["model_fluid_resistance_force_n"] > 0
    assert comparison["assessment_validation_status"] == (
        "internal_validation; experimental_validation_pending"
    )
    assert report["summary"]["status"] != FORBIDDEN_STATUS
    assert report["summary"]["validation_claim"] != FORBIDDEN_STATUS
    assert report["summary"]["status"] in {
        REPORT_STATUS_COMPARISON,
        REPORT_STATUS_INSUFFICIENT,
    }


def test_compute_summary_empty() -> None:
    summary = compute_summary([])
    assert summary["status"] == REPORT_STATUS_INSUFFICIENT
    assert summary["n"] == 0


def test_cli_validate_experimental_empty(tmp_path: Path, capsys) -> None:
    panel_path = tmp_path / "panel.json"
    panel_path.write_text(json.dumps(_empty_panel()), encoding="utf-8")
    out = tmp_path / "report"
    code = main(
        [
            "validate-experimental",
            str(panel_path),
            "--out",
            str(out),
        ]
    )
    assert code == 0
    captured = capsys.readouterr().out
    assert "insufficient_data" in captured
    assert (out / "experimental_comparison.json").is_file()
    assert (out / "manifest.sha256").is_file()


def test_template_panel_loads_as_empty() -> None:
    template = (
        Path(__file__).resolve().parents[1]
        / "validation"
        / "experimental"
        / "panel.template.json"
    )
    panel = load_panel(template)
    assert panel["rows"] == []
    summary = compute_summary([compare_row(r) for r in panel["rows"]])
    assert summary["status"] == REPORT_STATUS_INSUFFICIENT


def test_allmendinger2014_digitized_panel_literature_comparison(
    tmp_path: Path,
) -> None:
    """Regression: real digitized Allmendinger 2014 glycerol panel.

    Literature-derived with digitization caveats. Report may be
    experimental_comparison only — never independently_validated.
    Package validation status remains experimental_validation_pending.
    """

    panel_path = (
        Path(__file__).resolve().parents[1]
        / "validation"
        / "experimental"
        / "panel_allmendinger2014_glycerol_digitized.json"
    )
    assert panel_path.is_file(), f"missing literature panel: {panel_path}"
    panel = load_panel(panel_path)
    assert len(panel["rows"]) >= 10

    written = write_report(panel, tmp_path / "out", panel_path=panel_path)
    summary = written["summary"]

    assert summary["n"] >= 10
    assert summary["median_abs_relative_error"] is not None
    assert summary["median_abs_relative_error"] < 0.20
    assert summary["status"] == REPORT_STATUS_COMPARISON
    assert summary["status"] != FORBIDDEN_STATUS
    assert summary["validation_claim"] == REPORT_STATUS_COMPARISON
    assert summary["validation_claim"] != FORBIDDEN_STATUS
    assert summary["contains_synthetic_smoke_test"] is False

    report = json.loads(Path(written["json_path"]).read_text(encoding="utf-8"))
    assert report["report_type"] == "experimental_comparison"
    assert report["summary"]["status"] == REPORT_STATUS_COMPARISON
    assert report["summary"]["status"] != FORBIDDEN_STATUS
    assert report["summary"]["validation_claim"] != FORBIDDEN_STATUS
    # status / validation_claim must never be the forbidden package claim
    assert report["summary"]["status"] == "experimental_comparison"
    assert report["summary"]["validation_claim"] == "experimental_comparison"
    for comparison in report["comparisons"]:
        if comparison.get("status") != "compared":
            continue
        assert comparison["assessment_validation_status"] == (
            "internal_validation; experimental_validation_pending"
        )
        assert "experimental_validation_pending" in comparison[
            "assessment_validation_status"
        ]
        assert FORBIDDEN_STATUS not in comparison["assessment_validation_status"]
        assert comparison.get("is_synthetic_smoke_test") is False
