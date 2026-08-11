import json
import math

from hypothesis import given, settings
from hypothesis import strategies as st

from openinjectability import AssessmentInput, assess


def _case(**changes: float) -> AssessmentInput:
    values: dict[str, object] = {
        "scenario_id": "property-case",
        "formulation_id": "property-formulation",
        "viscosity_value": 35.0,
        "viscosity_unit": "cP",
        "viscosity_temperature_c": 25.0,
        "use_temperature_c": 25.0,
        "rheology_class": "newtonian",
        "newtonian_evidence": "PROPERTY-TEST",
        "needle_id_mm": 0.21,
        "needle_length_mm": 12.7,
        "needle_geometry_source": "PROPERTY-TEST-GEOMETRY",
        "barrel_id_mm": 6.35,
        "barrel_geometry_source": "PROPERTY-TEST-BARREL",
        "volume_ml": 2.0,
        "injection_time_s": 15.0,
        "density_kg_m3": 1000.0,
    }
    values.update(changes)
    return AssessmentInput(**values)  # type: ignore[arg-type]


positive = st.floats(min_value=1e-3, max_value=1e3, allow_nan=False, allow_infinity=False)


@settings(max_examples=40, deadline=None)
@given(viscosity=positive, length=positive, needle_id=positive, barrel_id=positive)
def test_positive_finite_domain_serializes_without_nonfinite_values(
    viscosity: float, length: float, needle_id: float, barrel_id: float
) -> None:
    result = assess(
        _case(
            viscosity_value=viscosity,
            needle_length_mm=length,
            needle_id_mm=needle_id,
            barrel_id_mm=barrel_id,
        )
    )
    assert result.outputs["needle_pressure_drop_pa"] > 0  # type: ignore[operator]
    assert result.outputs["fluid_resistance_force_n"] > 0  # type: ignore[operator]
    json.dumps(result.to_dict(), allow_nan=False)


@settings(max_examples=40, deadline=None)
@given(needle_id=st.floats(min_value=0.05, max_value=1.0, allow_nan=False, allow_infinity=False))
def test_increasing_inner_diameter_strictly_lowers_pressure(needle_id: float) -> None:
    smaller = assess(_case(needle_id_mm=needle_id))
    larger = assess(_case(needle_id_mm=needle_id * 1.1))
    assert larger.outputs["needle_pressure_drop_pa"] < smaller.outputs["needle_pressure_drop_pa"]  # type: ignore[operator]


@settings(max_examples=40, deadline=None)
@given(volume=positive, time_s=positive)
def test_time_flow_round_trip(volume: float, time_s: float) -> None:
    flow_ml_s = volume / time_s
    by_time = assess(_case(volume_ml=volume, injection_time_s=time_s))
    by_flow = assess(
        _case(volume_ml=volume, injection_time_s=None, flow_rate_ml_s=flow_ml_s)  # type: ignore[arg-type]
    )
    assert math.isclose(
        by_time.outputs["flow_rate_m3_s"],  # type: ignore[arg-type]
        by_flow.outputs["flow_rate_m3_s"],  # type: ignore[arg-type]
        rel_tol=1e-12,
    )
    assert math.isclose(
        by_flow.outputs["injection_time_s"],  # type: ignore[arg-type]
        by_time.outputs["injection_time_s"],  # type: ignore[arg-type]
        rel_tol=1e-12,
    )
