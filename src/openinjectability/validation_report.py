"""Experimental panel comparison pipeline (Phase D infrastructure).

Compares model predicted fluid-resistance force against laboratory rows.
Never advances package validation_status to independently_validated.
"""

from __future__ import annotations

import hashlib
import json
import math
import statistics
from collections.abc import Mapping, MutableMapping, Sequence
from pathlib import Path
from typing import Any

from . import __version__
from .core import assess
from .io import file_sha256, write_json
from .models import (
    AssessmentInput,
    InputValidationError,
    OpenInjectabilityError,
    utc_now_iso,
)

PANEL_SCHEMA_VERSION = "1.0"
COMPARABLE_FORCE_DEFINITIONS = frozenset({"fluid_only", "pressure_area"})
REJECTED_FORCE_DEFINITIONS = frozenset({"total_glide", "unknown"})
MEDIAN_ABS_REL_ERROR_CRITERION = 0.20
REPORT_STATUS_INSUFFICIENT = "insufficient_data"
REPORT_STATUS_COMPARISON = "experimental_comparison"
# Explicitly never claimed by this module:
FORBIDDEN_STATUS = "independently_validated"


def load_panel(path: str | Path) -> dict[str, Any]:
    """Load a panel JSON file; require schema_version and a rows list."""

    source = Path(path)
    try:
        raw = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InputValidationError(f"panel is not valid JSON: {exc}") from exc
    if not isinstance(raw, dict):
        raise InputValidationError("panel root must be a JSON object")
    schema_version = raw.get("schema_version")
    if schema_version != PANEL_SCHEMA_VERSION:
        raise InputValidationError(
            f"unsupported panel schema_version: {schema_version!r}; "
            f"expected {PANEL_SCHEMA_VERSION!r}"
        )
    rows = raw.get("rows")
    if not isinstance(rows, list):
        raise InputValidationError("panel.rows must be an array")
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise InputValidationError(f"panel.rows[{index}] must be an object")
    return raw


def _optional_positive(row: Mapping[str, Any], name: str) -> float | None:
    if name not in row or row[name] is None:
        return None
    value = row[name]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InputValidationError(f"{name} must be a finite real number")
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise InputValidationError(f"{name} must be finite and greater than zero")
    return number


def _required_text(row: Mapping[str, Any], name: str) -> str:
    value = row.get(name)
    if not isinstance(value, str) or not value.strip():
        raise InputValidationError(f"{name} must be a non-empty string")
    return value.strip()


def _required_positive(row: Mapping[str, Any], name: str) -> float:
    value = _optional_positive(row, name)
    if value is None:
        raise InputValidationError(f"{name} is required")
    return value


def _experimental_force_n(row: Mapping[str, Any]) -> float:
    """Resolve measured force from fluid force or pressure × barrel area."""

    measured_force = _optional_positive(row, "measured_fluid_force_n")
    measured_pressure = _optional_positive(row, "measured_pressure_pa")
    if measured_force is not None:
        return measured_force
    if measured_pressure is not None:
        barrel_id_m = _required_positive(row, "barrel_id_mm") / 1000.0
        area_m2 = math.pi * barrel_id_m**2 / 4.0
        force = measured_pressure * area_m2
        if not math.isfinite(force) or force <= 0:
            raise InputValidationError(
                "pressure-to-force conversion did not yield a positive finite force"
            )
        return force
    raise InputValidationError("supply measured_fluid_force_n or measured_pressure_pa")


def _row_to_assessment_input(row: Mapping[str, Any]) -> AssessmentInput:
    viscosity_unit = _required_text(row, "viscosity_unit")
    if viscosity_unit not in {"cP", "mPa_s", "Pa_s"}:
        raise InputValidationError(f"unsupported viscosity_unit: {viscosity_unit!r}")
    temperature_raw = row.get("viscosity_temperature_c")
    if isinstance(temperature_raw, bool) or not isinstance(temperature_raw, (int, float)):
        raise InputValidationError("viscosity_temperature_c must be a finite real number")
    temperature = float(temperature_raw)
    if not math.isfinite(temperature):
        raise InputValidationError("viscosity_temperature_c must be finite")
    density = _optional_positive(row, "density_kg_m3")
    if density is None and row.get("density") is not None:
        density = _optional_positive(row, "density")
    return AssessmentInput(
        scenario_id=_required_text(row, "scenario_id"),
        formulation_id=_required_text(row, "fluid"),
        viscosity_value=_required_positive(row, "viscosity_value"),
        viscosity_unit=viscosity_unit,  # type: ignore[arg-type]
        viscosity_temperature_c=temperature,
        use_temperature_c=temperature,
        rheology_class="newtonian",
        newtonian_evidence=_required_text(row, "newtonian_evidence"),
        needle_id_mm=_required_positive(row, "needle_id_mm"),
        needle_length_mm=_required_positive(row, "needle_length_mm"),
        needle_geometry_source=_required_text(row, "needle_geometry_source"),
        barrel_id_mm=_required_positive(row, "barrel_id_mm"),
        barrel_geometry_source=_required_text(row, "barrel_geometry_source"),
        volume_ml=_required_positive(row, "volume_ml"),
        injection_time_s=_optional_positive(row, "injection_time_s"),
        flow_rate_ml_s=_optional_positive(row, "flow_rate_ml_s"),
        density_kg_m3=density,
        notes=_required_text(row, "method_notes"),
    )


def compare_row(row: Mapping[str, Any]) -> dict[str, Any]:
    """Compare one panel row to assess(); reject non-fluid force definitions."""

    scenario_id = row.get("scenario_id") if isinstance(row.get("scenario_id"), str) else None
    base: dict[str, Any] = {
        "scenario_id": scenario_id,
        "is_synthetic_smoke_test": bool(row.get("is_synthetic_smoke_test")),
    }
    force_definition = row.get("force_definition")
    if not isinstance(force_definition, str) or not force_definition.strip():
        return {
            **base,
            "status": "rejected",
            "error": (
                "force_definition is required and must be 'fluid_only' or "
                "'pressure_area' for comparison; total_glide and unknown are rejected"
            ),
        }
    force_definition = force_definition.strip()
    if force_definition in REJECTED_FORCE_DEFINITIONS or (
        force_definition not in COMPARABLE_FORCE_DEFINITIONS
    ):
        return {
            **base,
            "status": "rejected",
            "force_definition": force_definition,
            "error": (
                f"force_definition {force_definition!r} is not comparable; "
                "only 'fluid_only' or 'pressure_area' are accepted "
                "(total_glide and unknown are rejected without comparison)"
            ),
        }

    try:
        experimental_force_n = _experimental_force_n(row)
        case = _row_to_assessment_input(row)
        result = assess(case)
        model_force = result.outputs["fluid_resistance_force_n"]
        if model_force is None or not math.isfinite(model_force) or model_force <= 0:
            raise InputValidationError("model force is not a positive finite value")
        relative_error = (model_force - experimental_force_n) / experimental_force_n
        abs_relative_error = abs(relative_error)
    except OpenInjectabilityError as exc:
        return {
            **base,
            "status": "rejected",
            "force_definition": force_definition,
            "error": str(exc),
        }
    except (TypeError, ValueError, KeyError) as exc:
        return {
            **base,
            "status": "rejected",
            "force_definition": force_definition,
            "error": str(exc),
        }

    return {
        **base,
        "status": "compared",
        "force_definition": force_definition,
        "model_fluid_resistance_force_n": model_force,
        "experimental_force_n": experimental_force_n,
        "relative_error": relative_error,
        "abs_relative_error": abs_relative_error,
        "model_id": result.model_id,
        "package_version": result.package_version,
        "assessment_validation_status": result.validation_status,
        "passes_20pct_criterion": abs_relative_error <= MEDIAN_ABS_REL_ERROR_CRITERION,
    }


def compute_summary(comparisons: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Aggregate compared rows; never claim independently_validated."""

    compared = [c for c in comparisons if c.get("status") == "compared"]
    rejected = [c for c in comparisons if c.get("status") == "rejected"]
    n = len(compared)
    if n == 0:
        return {
            "status": REPORT_STATUS_INSUFFICIENT,
            "n": 0,
            "n_rejected": len(rejected),
            "median_abs_relative_error": None,
            "criterion_abs_relative_error": MEDIAN_ABS_REL_ERROR_CRITERION,
            "pass_fail": None,
            "note": (
                "No comparable experimental rows; report is infrastructure-only. "
                f"Status is never {FORBIDDEN_STATUS!r}."
            ),
            "validation_claim": REPORT_STATUS_INSUFFICIENT,
            "contains_synthetic_smoke_test": False,
        }

    abs_errors = [float(c["abs_relative_error"]) for c in compared]
    median_err = statistics.median(abs_errors)
    passed = median_err <= MEDIAN_ABS_REL_ERROR_CRITERION
    return {
        "status": REPORT_STATUS_COMPARISON,
        "n": n,
        "n_rejected": len(rejected),
        "median_abs_relative_error": median_err,
        "criterion_abs_relative_error": MEDIAN_ABS_REL_ERROR_CRITERION,
        "pass_fail": "pass" if passed else "fail",
        "note": (
            "Experimental comparison only. Does not set package validation_status "
            f"to {FORBIDDEN_STATUS!r}. Synthetic smoke-test rows are not evidence."
        ),
        "validation_claim": REPORT_STATUS_COMPARISON,
        "contains_synthetic_smoke_test": any(
            bool(c.get("is_synthetic_smoke_test")) for c in compared
        ),
    }


def _markdown_report(
    *,
    panel_path: str,
    panel_sha256: str,
    summary: Mapping[str, Any],
    comparisons: Sequence[Mapping[str, Any]],
    generated_at: str,
) -> str:
    rows_md: list[str] = [
        "# Experimental comparison report",
        "",
        f"- Generated (UTC): `{generated_at}`",
        f"- Package version: `{__version__}`",
        f"- Input panel: `{panel_path}`",
        f"- Input SHA-256: `{panel_sha256}`",
        f"- Report status: **{summary['status']}**",
        f"- Comparable rows (n): `{summary['n']}`",
        f"- Rejected rows: `{summary['n_rejected']}`",
        (f"- Median absolute relative error: `{summary['median_abs_relative_error']}`"),
        (f"- Criterion (median abs relative error ≤): `{summary['criterion_abs_relative_error']}`"),
        f"- Pass/fail vs criterion: `{summary['pass_fail']}`",
        "",
        "## Important",
        "",
        f"- This report status is **never** `{FORBIDDEN_STATUS}`.",
        "- Package `validation_status` is not advanced by this pipeline.",
        "- Development fixtures under `tests/reference_data/` are not experimental data.",
        f"- {summary['note']}",
        "",
        "## Row results",
        "",
        (
            "| scenario_id | status | force_definition | model F (N) | "
            "exp F (N) | abs rel err | synthetic |"
        ),
        "|---|---|---|---|---|---|---|",
    ]
    for item in comparisons:
        err_cell = item.get("abs_relative_error", item.get("error", ""))
        rows_md.append(
            "| {sid} | {status} | {fdef} | {model} | {exp} | {err} | {syn} |".format(
                sid=item.get("scenario_id") or "",
                status=item.get("status") or "",
                fdef=item.get("force_definition") or "",
                model=item.get("model_fluid_resistance_force_n", ""),
                exp=item.get("experimental_force_n", ""),
                err=err_cell,
                syn=bool(item.get("is_synthetic_smoke_test")),
            )
        )
    rows_md.append("")
    return "\n".join(rows_md) + "\n"


def write_report(
    panel: Mapping[str, Any],
    out_dir: str | Path,
    *,
    panel_path: str | Path | None = None,
) -> dict[str, Any]:
    """Write JSON + Markdown comparison and SHA-256 manifest of inputs/outputs.

    Returns a small dict of written paths and the summary payload.
    Report status is only ``experimental_comparison`` or ``insufficient_data``.
    """

    destination = Path(out_dir)
    destination.mkdir(parents=True, exist_ok=True)

    rows = panel.get("rows")
    if not isinstance(rows, list):
        raise InputValidationError("panel.rows must be an array")

    comparisons = [compare_row(row) for row in rows]
    summary = compute_summary(comparisons)
    if summary["status"] not in {
        REPORT_STATUS_COMPARISON,
        REPORT_STATUS_INSUFFICIENT,
    }:
        raise RuntimeError("internal error: illegal report status")
    if summary.get("validation_claim") == FORBIDDEN_STATUS:
        raise RuntimeError("refusing to claim independently_validated")

    generated_at = utc_now_iso()
    panel_path_str = str(panel_path) if panel_path is not None else ""
    if panel_path is not None:
        panel_sha = file_sha256(panel_path)
    else:
        canonical = json.dumps(panel, sort_keys=True, allow_nan=False, separators=(",", ":"))
        panel_sha = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        panel_path_str = panel_path_str or "<in-memory-panel>"

    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "report_type": "experimental_comparison",
        "package_version": __version__,
        "generated_at_utc": generated_at,
        "input_panel_path": panel_path_str,
        "input_panel_sha256": panel_sha,
        "summary": dict(summary),
        "comparisons": comparisons,
        "disclaimers": [
            f"Report status is never {FORBIDDEN_STATUS}.",
            "Does not advance package validation_status.",
            "tests/reference_data is not an experimental dataset.",
        ],
    }

    json_path = destination / "experimental_comparison.json"
    md_path = destination / "experimental_comparison.md"
    manifest_path = destination / "manifest.sha256"

    write_json(payload, json_path)
    md_path.write_text(
        _markdown_report(
            panel_path=panel_path_str,
            panel_sha256=panel_sha,
            summary=summary,
            comparisons=comparisons,
            generated_at=generated_at,
        ),
        encoding="utf-8",
    )

    digests: MutableMapping[str, str] = {
        "input_panel": panel_sha,
        "experimental_comparison.json": file_sha256(json_path),
        "experimental_comparison.md": file_sha256(md_path),
    }
    manifest_lines = [f"{digest}  {name}" for name, digest in sorted(digests.items())]
    if panel_path is not None:
        manifest_lines.append(f"# input_panel_path  {panel_path}")
    manifest_path.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")

    return {
        "out_dir": str(destination),
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "manifest_path": str(manifest_path),
        "summary": summary,
        "input_panel_sha256": panel_sha,
    }
