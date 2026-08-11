"""CSV parsing and deterministic JSON writing."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from .models import (
    AssessmentInput,
    InputSchemaError,
    InputValidationError,
    OpenInjectabilityError,
    RejectedAssessment,
)

_REQUIRED_CSV_COLUMNS = frozenset(
    {
        "scenario_id",
        "formulation_id",
        "viscosity_value",
        "viscosity_unit",
        "viscosity_temperature_c",
        "use_temperature_c",
        "rheology_class",
        "newtonian_evidence",
        "needle_id_mm",
        "needle_length_mm",
        "needle_geometry_source",
        "barrel_id_mm",
        "barrel_geometry_source",
        "volume_ml",
    }
)


def _optional_float(row: dict[str, str], name: str) -> float | None:
    value = (row.get(name) or "").strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError as exc:
        raise InputValidationError(
            f"{name} must be numeric", code="INVALID_NUMERIC_VALUE", field=name
        ) from exc


def _required_float(row: dict[str, str], name: str) -> float:
    value = (row.get(name) or "").strip()
    if not value:
        raise InputValidationError(
            f"missing required CSV value: {name}",
            code="MISSING_REQUIRED_VALUE",
            field=name,
        )
    try:
        return float(value)
    except ValueError as exc:
        raise InputValidationError(
            f"{name} must be numeric", code="INVALID_NUMERIC_VALUE", field=name
        ) from exc


def _assessment_from_row(row: dict[str, str]) -> AssessmentInput:
    return AssessmentInput(
        scenario_id=(row.get("scenario_id") or "").strip(),
        formulation_id=(row.get("formulation_id") or "").strip(),
        viscosity_value=_required_float(row, "viscosity_value"),
        viscosity_unit=(row.get("viscosity_unit") or "").strip(),  # type: ignore[arg-type]
        viscosity_temperature_c=_required_float(row, "viscosity_temperature_c"),
        use_temperature_c=_required_float(row, "use_temperature_c"),
        rheology_class=(row.get("rheology_class") or "").strip(),
        newtonian_evidence=(row.get("newtonian_evidence") or "").strip(),
        needle_id_mm=_required_float(row, "needle_id_mm"),
        needle_length_mm=_required_float(row, "needle_length_mm"),
        needle_geometry_source=(row.get("needle_geometry_source") or "").strip(),
        barrel_id_mm=_required_float(row, "barrel_id_mm"),
        barrel_geometry_source=(row.get("barrel_geometry_source") or "").strip(),
        volume_ml=_required_float(row, "volume_ml"),
        injection_time_s=_optional_float(row, "injection_time_s"),
        flow_rate_ml_s=_optional_float(row, "flow_rate_ml_s"),
        needle_gauge_label=(row.get("needle_gauge_label") or "").strip() or None,
        density_kg_m3=_optional_float(row, "density_kg_m3"),
        force_ceiling_n=_optional_float(row, "force_ceiling_n"),
        force_ceiling_source=(row.get("force_ceiling_source") or "").strip() or None,
        notes=(row.get("notes") or "").strip() or None,
        validated_shear_rate_min_s_1=_optional_float(row, "validated_shear_rate_min_s_1"),
        validated_shear_rate_max_s_1=_optional_float(row, "validated_shear_rate_max_s_1"),
        component_pressure_rating_pa=_optional_float(row, "component_pressure_rating_pa"),
        geometry_tolerance_relative=_optional_float(row, "geometry_tolerance_relative"),
        validated_viscosity_min=_optional_float(row, "validated_viscosity_min"),
        validated_viscosity_max=_optional_float(row, "validated_viscosity_max"),
    )


def read_csv_batch(
    path: str | Path,
) -> tuple[list[tuple[int, AssessmentInput]], list[RejectedAssessment]]:
    """Parse a CSV while preserving every row-level rejection explicitly."""

    source = Path(path)
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise InputSchemaError("CSV must contain a header row", code="MISSING_HEADER")
        missing = sorted(_REQUIRED_CSV_COLUMNS.difference(reader.fieldnames))
        if missing:
            raise InputSchemaError(
                f"CSV is missing required columns: {', '.join(missing)}",
                code="MISSING_REQUIRED_COLUMNS",
            )
        cases: list[tuple[int, AssessmentInput]] = []
        rejected: list[RejectedAssessment] = []
        seen: set[str] = set()
        row_count = 0
        for row_number, row in enumerate(reader, start=2):
            row_count += 1
            scenario_id = (row.get("scenario_id") or "").strip() or None
            try:
                if scenario_id is not None and scenario_id in seen:
                    raise InputValidationError(
                        f"duplicate scenario_id: {scenario_id!r}",
                        code="DUPLICATE_SCENARIO_ID",
                        field="scenario_id",
                    )
                case = _assessment_from_row(row)
                seen.add(case.scenario_id)
                cases.append((row_number, case))
            except (OpenInjectabilityError, ValueError) as exc:
                error = (
                    exc
                    if isinstance(exc, OpenInjectabilityError)
                    else InputValidationError(str(exc), code="INVALID_NUMERIC_VALUE")
                )
                rejected.append(
                    RejectedAssessment(
                        row_number=row_number,
                        scenario_id=scenario_id,
                        error_type=type(error).__name__,
                        error_code=error.code,
                        message=str(error),
                        field=error.field,
                    )
                )
        if row_count == 0:
            raise InputSchemaError("CSV contains no data rows", code="NO_DATA_ROWS")
    return cases, rejected


def read_csv(path: str | Path) -> list[AssessmentInput]:
    cases, rejected = read_csv_batch(path)
    if rejected:
        first = rejected[0]
        raise InputValidationError(
            f"CSV row {first.row_number}: {first.message}",
            code=first.error_code,
            field=first.field,
        )
    return [case for _, case in cases]


def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(data: Any, path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
