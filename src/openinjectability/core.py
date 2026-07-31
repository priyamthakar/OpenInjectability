"""Validated Newtonian needle-flow calculations."""

from __future__ import annotations

import math
import uuid
from collections.abc import Iterable
from dataclasses import asdict, replace

from .models import (
    AssessmentConfig,
    AssessmentInput,
    AssessmentResult,
    AssessmentWarning,
    InputValidationError,
    ScientificBoundaryError,
    SensitivityItem,
    utc_now_iso,
)

EXCLUSIONS = (
    "syringe friction and break-loose force",
    "device drivetrain, spring, motor, and transmission losses",
    "connectors, tubing, entrance, exit, and other minor losses",
    "tissue backpressure and depot formation",
    "human capability, pain, leakage, and clinical outcomes",
)


def _finite_positive(name: str, value: float | None, *, required: bool = True) -> None:
    if value is None:
        if required:
            raise InputValidationError(f"{name} is required")
        return
    if not math.isfinite(value) or value <= 0:
        raise InputValidationError(f"{name} must be finite and greater than zero")


def _required_text(name: str, value: str | None) -> None:
    if value is None or not value.strip():
        raise InputValidationError(f"{name} must be a non-empty string")


def _viscosity_pa_s(value: float, unit: str) -> float:
    if unit == "Pa_s":
        return value
    if unit in {"cP", "mPa_s"}:
        return value / 1000.0
    raise InputValidationError(f"unsupported viscosity_unit: {unit!r}")


def _validate(case: AssessmentInput, config: AssessmentConfig) -> None:
    for name in (
        "scenario_id",
        "formulation_id",
        "newtonian_evidence",
        "needle_geometry_source",
        "barrel_geometry_source",
    ):
        _required_text(name, getattr(case, name))

    for name in (
        "viscosity_value",
        "needle_id_mm",
        "needle_length_mm",
        "barrel_id_mm",
        "volume_ml",
    ):
        _finite_positive(name, getattr(case, name))

    for name in ("viscosity_temperature_c", "use_temperature_c"):
        value = getattr(case, name)
        if not math.isfinite(value):
            raise InputValidationError(f"{name} must be finite")

    if case.rheology_class.strip().lower() != "newtonian":
        raise ScientificBoundaryError(
            "v0.1 supports Newtonian fluids only; non-Newtonian or unknown rheology is rejected"
        )

    if abs(case.viscosity_temperature_c - case.use_temperature_c) > (
        config.temperature_tolerance_c
    ):
        raise ScientificBoundaryError(
            "viscosity measurement temperature and use temperature differ beyond "
            f"{config.temperature_tolerance_c:g} degC; v0.1 performs no temperature correction"
        )

    _finite_positive("injection_time_s", case.injection_time_s, required=False)
    _finite_positive("flow_rate_ml_s", case.flow_rate_ml_s, required=False)
    if case.injection_time_s is None and case.flow_rate_ml_s is None:
        raise InputValidationError("supply injection_time_s or flow_rate_ml_s")

    if case.injection_time_s is not None and case.flow_rate_ml_s is not None:
        implied = case.volume_ml / case.injection_time_s
        error = abs(case.flow_rate_ml_s - implied) / max(abs(case.flow_rate_ml_s), abs(implied))
        if error > config.time_flow_relative_tolerance:
            raise InputValidationError(
                "injection_time_s and flow_rate_ml_s are inconsistent with volume_ml"
            )

    _finite_positive("density_kg_m3", case.density_kg_m3, required=False)
    _finite_positive("force_ceiling_n", case.force_ceiling_n, required=False)
    if case.force_ceiling_n is not None:
        _required_text("force_ceiling_source", case.force_ceiling_source)

    _finite_positive("temperature_tolerance_c", config.temperature_tolerance_c)
    _finite_positive("time_flow_relative_tolerance", config.time_flow_relative_tolerance)
    if not math.isfinite(config.sensitivity_relative_change) or not (
        0 < config.sensitivity_relative_change < 1
    ):
        raise InputValidationError("sensitivity_relative_change must be between zero and one")


def _calculate(case: AssessmentInput) -> dict[str, float | None]:
    mu = _viscosity_pa_s(case.viscosity_value, case.viscosity_unit)
    length = case.needle_length_mm / 1000.0
    needle_id = case.needle_id_mm / 1000.0
    barrel_id = case.barrel_id_mm / 1000.0
    volume = case.volume_ml / 1_000_000.0
    if case.injection_time_s is not None:
        time_s = case.injection_time_s
        flow = volume / time_s
    else:
        flow = case.flow_rate_ml_s / 1_000_000.0  # type: ignore[operator]
        time_s = volume / flow

    pressure = 128.0 * mu * length * flow / (math.pi * needle_id**4)
    barrel_area = math.pi * barrel_id**2 / 4.0
    force = pressure * barrel_area
    wall_shear = 32.0 * flow / (math.pi * needle_id**3)
    velocity = 4.0 * flow / (math.pi * needle_id**2)
    reynolds = None
    if case.density_kg_m3 is not None:
        reynolds = case.density_kg_m3 * velocity * needle_id / mu

    return {
        "dynamic_viscosity_pa_s": mu,
        "flow_rate_m3_s": flow,
        "injection_time_s": time_s,
        "needle_pressure_drop_pa": pressure,
        "barrel_area_m2": barrel_area,
        "fluid_resistance_force_n": force,
        "wall_shear_rate_s_1": wall_shear,
        "mean_velocity_m_s": velocity,
        "reynolds_number": reynolds,
    }


def _sensitivity(
    case: AssessmentInput, baseline_force: float, relative_change: float
) -> tuple[SensitivityItem, ...]:
    items: list[SensitivityItem] = []
    for field_name in (
        "viscosity_value",
        "needle_length_mm",
        "needle_id_mm",
        "barrel_id_mm",
    ):
        for change in (-relative_change, relative_change):
            changed = replace(case, **{field_name: getattr(case, field_name) * (1 + change)})
            force = _calculate(changed)["fluid_resistance_force_n"]
            assert force is not None
            items.append(
                SensitivityItem(
                    input_name=field_name,
                    relative_change=change,
                    fluid_resistance_force_n=force,
                    force_relative_change=(force / baseline_force) - 1.0,
                )
            )
    rate_field = "injection_time_s" if case.injection_time_s is not None else "flow_rate_ml_s"
    for change in (-relative_change, relative_change):
        changed = replace(case, **{rate_field: getattr(case, rate_field) * (1 + change)})
        force = _calculate(changed)["fluid_resistance_force_n"]
        assert force is not None
        items.append(
            SensitivityItem(
                input_name=rate_field,
                relative_change=change,
                fluid_resistance_force_n=force,
                force_relative_change=(force / baseline_force) - 1.0,
            )
        )
    return tuple(items)


def assess(
    case: AssessmentInput, config: AssessmentConfig | None = None
) -> AssessmentResult:
    """Assess one supported scenario or raise a typed fail-closed error."""

    effective = config or AssessmentConfig()
    _validate(case, effective)
    outputs = _calculate(case)
    warnings: list[AssessmentWarning] = []

    if case.density_kg_m3 is None:
        warnings.append(
            AssessmentWarning(
                code="LAMINARITY_NOT_NUMERICALLY_VERIFIED",
                severity="warning",
                field="density_kg_m3",
                message="Density was not supplied, so Reynolds number was not calculated.",
            )
        )
    if case.force_ceiling_n is not None:
        force = outputs["fluid_resistance_force_n"]
        assert force is not None
        if force > case.force_ceiling_n:
            warnings.append(
                AssessmentWarning(
                    code="USER_FORCE_CEILING_EXCEEDED",
                    severity="warning",
                    field="force_ceiling_n",
                    message=(
                        "Predicted fluid-resistance force exceeds the user-provided "
                        "experimentally justified ceiling."
                    ),
                )
            )

    force = outputs["fluid_resistance_force_n"]
    assert force is not None
    return AssessmentResult(
        schema_version="1.0",
        package_version="0.1.0",
        model_id=effective.model_id,
        run_id=str(uuid.uuid4()),
        generated_at_utc=utc_now_iso(),
        status="passed_with_warnings" if warnings else "passed",
        normalized_input={
            **asdict(case),
            "viscosity_pa_s": outputs["dynamic_viscosity_pa_s"],
            "needle_id_m": case.needle_id_mm / 1000.0,
            "needle_length_m": case.needle_length_mm / 1000.0,
            "barrel_id_m": case.barrel_id_mm / 1000.0,
            "volume_m3": case.volume_ml / 1_000_000.0,
        },
        outputs=outputs,
        sensitivity=_sensitivity(case, force, effective.sensitivity_relative_change),
        warnings=tuple(warnings),
        exclusions=EXCLUSIONS,
        validation_status="internal_validation; experimental_validation_pending",
        effective_configuration=asdict(effective),
    )


def assess_many(
    cases: Iterable[AssessmentInput], config: AssessmentConfig | None = None
) -> tuple[AssessmentResult, ...]:
    """Assess cases in input order; any unsupported case fails the call."""

    return tuple(assess(case, config=config) for case in cases)
