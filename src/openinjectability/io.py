"""CSV parsing and deterministic JSON writing."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from .models import AssessmentInput, InputValidationError


def _optional_float(row: dict[str, str], name: str) -> float | None:
    value = (row.get(name) or "").strip()
    return None if not value else float(value)


def _required_float(row: dict[str, str], name: str) -> float:
    value = (row.get(name) or "").strip()
    if not value:
        raise InputValidationError(f"missing required CSV value: {name}")
    try:
        return float(value)
    except ValueError as exc:
        raise InputValidationError(f"{name} must be numeric") from exc


def read_csv(path: str | Path) -> list[AssessmentInput]:
    source = Path(path)
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise InputValidationError("CSV must contain a header row")
        cases: list[AssessmentInput] = []
        seen: set[str] = set()
        for row_number, row in enumerate(reader, start=2):
            try:
                scenario_id = (row.get("scenario_id") or "").strip()
                if scenario_id in seen:
                    raise InputValidationError(f"duplicate scenario_id: {scenario_id!r}")
                seen.add(scenario_id)
                cases.append(
                    AssessmentInput(
                        scenario_id=scenario_id,
                        formulation_id=(row.get("formulation_id") or "").strip(),
                        viscosity_value=_required_float(row, "viscosity_value"),
                        viscosity_unit=(row.get("viscosity_unit") or "").strip(),  # type: ignore[arg-type]
                        viscosity_temperature_c=_required_float(
                            row, "viscosity_temperature_c"
                        ),
                        use_temperature_c=_required_float(row, "use_temperature_c"),
                        rheology_class=(row.get("rheology_class") or "").strip(),
                        newtonian_evidence=(row.get("newtonian_evidence") or "").strip(),
                        needle_id_mm=_required_float(row, "needle_id_mm"),
                        needle_length_mm=_required_float(row, "needle_length_mm"),
                        needle_geometry_source=(
                            row.get("needle_geometry_source") or ""
                        ).strip(),
                        barrel_id_mm=_required_float(row, "barrel_id_mm"),
                        barrel_geometry_source=(
                            row.get("barrel_geometry_source") or ""
                        ).strip(),
                        volume_ml=_required_float(row, "volume_ml"),
                        injection_time_s=_optional_float(row, "injection_time_s"),
                        flow_rate_ml_s=_optional_float(row, "flow_rate_ml_s"),
                        needle_gauge_label=(row.get("needle_gauge_label") or "").strip()
                        or None,
                        density_kg_m3=_optional_float(row, "density_kg_m3"),
                        force_ceiling_n=_optional_float(row, "force_ceiling_n"),
                        force_ceiling_source=(
                            row.get("force_ceiling_source") or ""
                        ).strip()
                        or None,
                        notes=(row.get("notes") or "").strip() or None,
                    )
                )
            except (InputValidationError, ValueError) as exc:
                raise InputValidationError(f"CSV row {row_number}: {exc}") from exc
    if not cases:
        raise InputValidationError("CSV contains no data rows")
    return cases


def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(data: Any, path: str | Path) -> None:
    Path(path).write_text(
        json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
