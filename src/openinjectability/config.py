"""Run-level configuration loading (YAML/JSON)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import AssessmentConfig, InputValidationError

SUPPORTED_SCHEMA_VERSION = "1.0"
SUPPORTED_MODEL = "newtonian_hagen_poiseuille_v1"


def _as_mapping(data: object, source: str) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise InputValidationError(f"{source} must contain a JSON/YAML object")
    return data


def load_config(path: str | Path | None) -> AssessmentConfig:
    """Load AssessmentConfig from YAML or JSON; defaults when path is None."""

    if path is None:
        return AssessmentConfig()
    source = Path(path)
    if not source.is_file():
        raise InputValidationError(f"config file not found: {source}")
    text = source.read_text(encoding="utf-8")
    suffix = source.suffix.lower()
    try:
        if suffix in {".yaml", ".yml"}:
            try:
                import yaml
            except ImportError as exc:  # pragma: no cover
                raise InputValidationError(
                    "YAML config requires PyYAML: pip install openinjectability[reports]"
                ) from exc
            raw = _as_mapping(yaml.safe_load(text), str(source))
        elif suffix == ".json":
            raw = _as_mapping(json.loads(text), str(source))
        else:
            raise InputValidationError("config file must be .json, .yaml, or .yml")
    except (json.JSONDecodeError, ValueError) as exc:
        raise InputValidationError(f"invalid config file {source}: {exc}") from exc

    schema_version = str(raw.get("schema_version", SUPPORTED_SCHEMA_VERSION))
    if schema_version != SUPPORTED_SCHEMA_VERSION:
        raise InputValidationError(
            f"unsupported config schema_version {schema_version!r}; "
            f"supported: {SUPPORTED_SCHEMA_VERSION!r}"
        )
    model = str(raw.get("calculation_model", raw.get("model_id", SUPPORTED_MODEL)))
    if model != SUPPORTED_MODEL:
        raise InputValidationError(f"unsupported calculation_model: {model!r}")

    temperature = float(raw.get("temperature_tolerance_c", 0.5))
    time_flow = float(raw.get("time_flow_relative_tolerance", 0.001))
    sensitivity_block = raw.get("sensitivity") or {}
    if sensitivity_block is None:
        sensitivity_block = {}
    if not isinstance(sensitivity_block, dict):
        raise InputValidationError("sensitivity must be an object when provided")

    relative_changes = sensitivity_block.get("relative_changes")
    single = sensitivity_block.get("relative_change", raw.get("sensitivity_relative_change", 0.10))
    changes_tuple: tuple[float, ...] | None
    if relative_changes is not None:
        if not isinstance(relative_changes, list) or not relative_changes:
            raise InputValidationError("sensitivity.relative_changes must be a nonempty list")
        changes_tuple = tuple(float(item) for item in relative_changes)
        relative_change = abs(changes_tuple[0])
    else:
        changes_tuple = None
        relative_change = float(single)

    report_block = raw.get("report") or {}
    if not isinstance(report_block, dict):
        raise InputValidationError("report must be an object when provided")
    force_unit = str(report_block.get("display_force_unit", "N"))
    pressure_unit = str(report_block.get("display_pressure_unit", "MPa"))
    if force_unit != "N":
        raise InputValidationError("report.display_force_unit supports only 'N'")
    if pressure_unit != "MPa":
        raise InputValidationError("report.display_pressure_unit supports only 'MPa'")

    return AssessmentConfig(
        temperature_tolerance_c=temperature,
        time_flow_relative_tolerance=time_flow,
        sensitivity_relative_change=relative_change,
        sensitivity_relative_changes=changes_tuple,
        model_id=model,
        display_force_unit="N",
        display_pressure_unit="MPa",
    )


def config_to_serializable(config: AssessmentConfig) -> dict[str, Any]:
    """Serialize effective configuration including defaults."""

    from dataclasses import asdict

    return asdict(config)
