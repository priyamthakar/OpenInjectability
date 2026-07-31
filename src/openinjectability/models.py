"""Typed models and error types."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal


class OpenInjectabilityError(ValueError):
    """Base class for user-correctable assessment errors."""


class InputValidationError(OpenInjectabilityError):
    """Input is missing, non-finite, non-positive, or internally inconsistent."""


class ScientificBoundaryError(OpenInjectabilityError):
    """Input requests science outside the validated model boundary."""


@dataclass(frozen=True)
class AssessmentConfig:
    """Run-level policies, serialized with every result."""

    temperature_tolerance_c: float = 0.5
    time_flow_relative_tolerance: float = 0.001
    sensitivity_relative_change: float = 0.10
    model_id: str = "newtonian_hagen_poiseuille_v1"


@dataclass(frozen=True)
class AssessmentInput:
    """One formulation and device scenario using convenient input units."""

    scenario_id: str
    formulation_id: str
    viscosity_value: float
    viscosity_unit: Literal["cP", "mPa_s", "Pa_s"]
    viscosity_temperature_c: float
    use_temperature_c: float
    rheology_class: str
    newtonian_evidence: str
    needle_id_mm: float
    needle_length_mm: float
    needle_geometry_source: str
    barrel_id_mm: float
    barrel_geometry_source: str
    volume_ml: float
    injection_time_s: float | None = None
    flow_rate_ml_s: float | None = None
    needle_gauge_label: str | None = None
    density_kg_m3: float | None = None
    force_ceiling_n: float | None = None
    force_ceiling_source: str | None = None
    notes: str | None = None


@dataclass(frozen=True)
class AssessmentWarning:
    code: str
    severity: Literal["info", "warning"]
    message: str
    field: str | None = None


@dataclass(frozen=True)
class SensitivityItem:
    input_name: str
    relative_change: float
    fluid_resistance_force_n: float
    force_relative_change: float


@dataclass(frozen=True)
class AssessmentResult:
    schema_version: str
    package_version: str
    model_id: str
    run_id: str
    generated_at_utc: str
    status: Literal["passed", "passed_with_warnings"]
    normalized_input: dict[str, Any]
    outputs: dict[str, float | None]
    sensitivity: tuple[SensitivityItem, ...]
    warnings: tuple[AssessmentWarning, ...]
    exclusions: tuple[str, ...]
    validation_status: str
    effective_configuration: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RejectedAssessment:
    row_number: int
    scenario_id: str | None
    error_type: str
    message: str


@dataclass(frozen=True)
class BatchResult:
    results: tuple[AssessmentResult, ...] = field(default_factory=tuple)
    rejected: tuple[RejectedAssessment, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
