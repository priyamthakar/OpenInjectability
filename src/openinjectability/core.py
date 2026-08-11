"""Validated Newtonian needle-flow calculations."""

from __future__ import annotations

import math
import uuid
from collections.abc import Iterable
from dataclasses import asdict, replace

from ._version import __version__
from .models import (
    AssessmentConfig,
    AssessmentInput,
    AssessmentResult,
    AssessmentWarning,
    InputValidationError,
    ScientificBoundaryError,
    SensitivityItem,
    UnitError,
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
            raise InputValidationError(
                f"{name} is required", code="MISSING_REQUIRED_VALUE", field=name
            )
        return
    if not math.isfinite(value) or value <= 0:
        raise InputValidationError(
            f"{name} must be finite and greater than zero",
            code="NONPOSITIVE_OR_NONFINITE_VALUE",
            field=name,
        )


def _required_text(name: str, value: str | None) -> None:
    if value is None or not value.strip():
        raise InputValidationError(
            f"{name} must be a non-empty string", code="MISSING_PROVENANCE", field=name
        )


def _viscosity_pa_s(value: float, unit: str) -> float:
    if unit == "Pa_s":
        return value
    if unit in {"cP", "mPa_s"}:
        return value / 1000.0
    raise UnitError(
        f"unsupported viscosity_unit: {unit!r}",
        code="UNSUPPORTED_VISCOSITY_UNIT",
        field="viscosity_unit",
    )


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
            raise InputValidationError(f"{name} must be finite", code="NONFINITE_VALUE", field=name)

    if case.rheology_class.strip().lower() != "newtonian":
        raise ScientificBoundaryError(
            "v0.1 supports Newtonian fluids only; non-Newtonian or unknown rheology is rejected",
            code="UNSUPPORTED_RHEOLOGY",
            field="rheology_class",
        )

    if abs(case.viscosity_temperature_c - case.use_temperature_c) > (
        config.temperature_tolerance_c
    ):
        raise ScientificBoundaryError(
            "viscosity measurement temperature and use temperature differ beyond "
            f"{config.temperature_tolerance_c:g} degC; v0.1 performs no temperature correction",
            code="TEMPERATURE_MISMATCH",
            field="use_temperature_c",
        )

    _finite_positive("injection_time_s", case.injection_time_s, required=False)
    _finite_positive("flow_rate_ml_s", case.flow_rate_ml_s, required=False)
    if case.injection_time_s is None and case.flow_rate_ml_s is None:
        raise InputValidationError(
            "supply injection_time_s or flow_rate_ml_s",
            code="MISSING_TIME_OR_FLOW",
            field="injection_time_s",
        )

    if case.injection_time_s is not None and case.flow_rate_ml_s is not None:
        implied = case.volume_ml / case.injection_time_s
        error = abs(case.flow_rate_ml_s - implied) / max(abs(case.flow_rate_ml_s), abs(implied))
        if error > config.time_flow_relative_tolerance:
            raise InputValidationError(
                "injection_time_s and flow_rate_ml_s are inconsistent with volume_ml",
                code="TIME_FLOW_INCONSISTENT",
                field="flow_rate_ml_s",
            )

    _finite_positive("density_kg_m3", case.density_kg_m3, required=False)
    _finite_positive("force_ceiling_n", case.force_ceiling_n, required=False)
    if case.force_ceiling_n is not None:
        _required_text("force_ceiling_source", case.force_ceiling_source)

    for optional_name in (
        "validated_shear_rate_min_s_1",
        "validated_shear_rate_max_s_1",
        "component_pressure_rating_pa",
        "geometry_tolerance_relative",
    ):
        _finite_positive(optional_name, getattr(case, optional_name), required=False)
    if (
        case.validated_shear_rate_min_s_1 is not None
        and case.validated_shear_rate_max_s_1 is not None
        and case.validated_shear_rate_min_s_1 > case.validated_shear_rate_max_s_1
    ):
        raise InputValidationError(
            "validated_shear_rate_min_s_1 must not exceed validated_shear_rate_max_s_1",
            code="INVALID_EVIDENCE_RANGE",
            field="validated_shear_rate_min_s_1",
        )

    _finite_positive("validated_viscosity_min", case.validated_viscosity_min, required=False)
    _finite_positive("validated_viscosity_max", case.validated_viscosity_max, required=False)
    if (
        case.validated_viscosity_min is not None
        and case.validated_viscosity_max is not None
        and case.validated_viscosity_min > case.validated_viscosity_max
    ):
        raise InputValidationError(
            "validated_viscosity_min must not exceed validated_viscosity_max",
            code="INVALID_EVIDENCE_RANGE",
            field="validated_viscosity_min",
        )

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


def _sensitivity_changes(config: AssessmentConfig) -> tuple[float, ...]:
    """Resolve one-at-a-time relative changes from config (multi-step or single)."""

    if config.sensitivity_relative_changes is not None:
        changes = tuple(config.sensitivity_relative_changes)
        if not changes:
            raise InputValidationError("sensitivity_relative_changes must not be empty")
        for change in changes:
            if not math.isfinite(change) or change == 0 or abs(change) >= 1:
                raise InputValidationError(
                    "each sensitivity_relative_changes entry must be nonzero and |delta| < 1"
                )
        return changes
    return (-config.sensitivity_relative_change, config.sensitivity_relative_change)


def _perturbed_outputs(case: AssessmentInput, config: AssessmentConfig) -> dict[str, float | None]:
    """Rerun the validated scientific core for one perturbed case."""

    _validate(case, config)
    return _calculate(case)


def _sensitivity(
    case: AssessmentInput,
    baseline_force: float,
    baseline_pressure: float,
    config: AssessmentConfig,
) -> tuple[SensitivityItem, ...]:
    items: list[SensitivityItem] = []
    changes = _sensitivity_changes(config)
    for field_name in (
        "viscosity_value",
        "needle_length_mm",
        "needle_id_mm",
        "barrel_id_mm",
    ):
        elasticity = {
            "viscosity_value": 1.0,
            "needle_length_mm": 1.0,
            "needle_id_mm": -4.0,
            "barrel_id_mm": 2.0,
        }[field_name]
        for change in changes:
            changed = replace(case, **{field_name: getattr(case, field_name) * (1 + change)})
            perturbed = _perturbed_outputs(changed, config)
            pressure = perturbed["needle_pressure_drop_pa"]
            force = perturbed["fluid_resistance_force_n"]
            assert pressure is not None
            assert force is not None
            items.append(
                SensitivityItem(
                    input_name=field_name,
                    relative_change=change,
                    needle_pressure_drop_pa=pressure,
                    pressure_relative_change=(pressure / baseline_pressure) - 1.0,
                    fluid_resistance_force_n=force,
                    force_relative_change=(force / baseline_force) - 1.0,
                    analytical_force_elasticity=elasticity,
                )
            )
    # Prefer supplied rate field; when both are present, null the companion so the
    # perturbed case remains scientifically consistent with volume and time/flow.
    if case.injection_time_s is not None:
        rate_field = "injection_time_s"
        companion: dict[str, float | None] = {"flow_rate_ml_s": None}
    else:
        rate_field = "flow_rate_ml_s"
        companion = {"injection_time_s": None}
    for change in changes:
        rate_value = getattr(case, rate_field)
        assert rate_value is not None
        changed = replace(
            case,
            **{rate_field: rate_value * (1 + change), **companion},
        )
        perturbed = _perturbed_outputs(changed, config)
        pressure = perturbed["needle_pressure_drop_pa"]
        force = perturbed["fluid_resistance_force_n"]
        assert pressure is not None
        assert force is not None
        items.append(
            SensitivityItem(
                input_name=rate_field,
                relative_change=change,
                needle_pressure_drop_pa=pressure,
                pressure_relative_change=(pressure / baseline_pressure) - 1.0,
                fluid_resistance_force_n=force,
                force_relative_change=(force / baseline_force) - 1.0,
                analytical_force_elasticity=(-1.0 if rate_field == "injection_time_s" else 1.0),
            )
        )
    return tuple(items)


def assess(case: AssessmentInput, config: AssessmentConfig | None = None) -> AssessmentResult:
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
                remediation=(
                    "Supply a traceable density at the use temperature if a Reynolds "
                    "diagnostic is required."
                ),
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
                    remediation=(
                        "Review the user-supplied fluid-force ceiling and the declared "
                        "formulation, geometry, and delivery rate."
                    ),
                )
            )

    force = outputs["fluid_resistance_force_n"]
    assert force is not None

    # Inverse screening quantities when a provenance-backed ceiling is supplied.
    if case.force_ceiling_n is not None:
        mu = outputs["dynamic_viscosity_pa_s"]
        assert mu is not None
        length = case.needle_length_mm / 1000.0
        needle_id = case.needle_id_mm / 1000.0
        barrel_id = case.barrel_id_mm / 1000.0
        volume = case.volume_ml / 1_000_000.0
        q_max = (case.force_ceiling_n * needle_id**4) / (32.0 * mu * length * barrel_id**2)
        outputs = {
            **outputs,
            "max_flow_rate_m3_s_at_force_ceiling": q_max,
            "min_injection_time_s_at_force_ceiling": volume / q_max,
        }
        warnings.append(
            AssessmentWarning(
                code="INVERSE_SCREENING_QUANTITIES",
                severity="info",
                field="force_ceiling_n",
                message=(
                    "max_flow_rate_m3_s_at_force_ceiling and "
                    "min_injection_time_s_at_force_ceiling are model-derived "
                    "screening quantities from the user-supplied force ceiling; "
                    "they are not total device capability."
                ),
                remediation=(
                    "Treat these values as idealized screening outputs and verify them "
                    "against qualified device and experimental evidence."
                ),
            )
        )

    if case.geometry_tolerance_relative is None:
        warnings.append(
            AssessmentWarning(
                code="GEOMETRY_TOLERANCE_ABSENT",
                severity="info",
                field="geometry_tolerance_relative",
                message="Geometry manufacturing tolerance was not supplied.",
                remediation=(
                    "Supply a provenance-backed relative geometry tolerance when available."
                ),
            )
        )

    if (
        case.validated_viscosity_min is not None
        and case.viscosity_value < case.validated_viscosity_min
    ) or (
        case.validated_viscosity_max is not None
        and case.viscosity_value > case.validated_viscosity_max
    ):
        warnings.append(
            AssessmentWarning(
                code="VISCOSITY_OUTSIDE_EVIDENCE_RANGE",
                severity="warning",
                field="viscosity_value",
                message=(
                    "Declared viscosity lies outside the user-declared validated "
                    "viscosity range in the same declared unit."
                ),
                remediation=(
                    "Provide evidence covering the declared viscosity or reject the "
                    "scenario from use."
                ),
            )
        )

    shear = outputs["wall_shear_rate_s_1"]
    assert shear is not None
    if (
        case.validated_shear_rate_min_s_1 is not None
        and case.validated_shear_rate_max_s_1 is not None
        and not (case.validated_shear_rate_min_s_1 <= shear <= case.validated_shear_rate_max_s_1)
    ):
        warnings.append(
            AssessmentWarning(
                code="SHEAR_RATE_OUTSIDE_EVIDENCE_RANGE",
                severity="warning",
                field="wall_shear_rate_s_1",
                message=(
                    "Apparent wall shear rate lies outside the declared rheology evidence range."
                ),
                remediation=(
                    "Provide rheology evidence covering the calculated shear-rate range "
                    "or reject the scenario from use."
                ),
            )
        )

    if (
        case.needle_gauge_label is not None
        and case.needle_geometry_source
        and case.needle_gauge_label.lower() not in case.needle_geometry_source.lower()
        and case.needle_gauge_label.replace("G", "").replace("g", "")
        not in case.needle_geometry_source
    ):
        warnings.append(
            AssessmentWarning(
                code="GAUGE_GEOMETRY_METADATA_INCONSISTENT",
                severity="info",
                field="needle_gauge_label",
                message=(
                    "Gauge label and needle geometry source metadata do not appear "
                    "to reference the same designation; ID remains authoritative."
                ),
                remediation=(
                    "Confirm the gauge label and drawing or measurement identifier; the "
                    "declared inner diameter remains authoritative."
                ),
            )
        )

    pressure = outputs["needle_pressure_drop_pa"]
    assert pressure is not None
    if (
        case.component_pressure_rating_pa is not None
        and pressure > case.component_pressure_rating_pa
    ):
        warnings.append(
            AssessmentWarning(
                code="COMPONENT_PRESSURE_RATING_EXCEEDED",
                severity="warning",
                field="component_pressure_rating_pa",
                message=(
                    "Predicted needle pressure drop exceeds the user-provided "
                    "component pressure rating."
                ),
                remediation=(
                    "Confirm the component rating provenance and reduce the modeled rate "
                    "or revise geometry only through qualified inputs."
                ),
            )
        )

    return AssessmentResult(
        schema_version="1.0",
        package_version=__version__,
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
        provenance={
            "source_file_sha256": None,
            "source_file_reason": "not_applicable_in_memory_api",
            "geometry_sources": {
                "needle": case.needle_geometry_source,
                "barrel": case.barrel_geometry_source,
            },
            "rheology_evidence": case.newtonian_evidence,
            "effective_configuration": asdict(effective),
        },
        outputs=outputs,
        diagnostic_reasons=(
            {"reynolds_number": "LAMINARITY_NOT_NUMERICALLY_VERIFIED"}
            if outputs["reynolds_number"] is None
            else {}
        ),
        sensitivity=_sensitivity(case, force, pressure, effective),
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
