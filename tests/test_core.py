import json
import math
from pathlib import Path

import pytest

from openinjectability import (
    AssessmentConfig,
    AssessmentInput,
    InputValidationError,
    ScientificBoundaryError,
    assess,
)


def case(**changes):
    values = {
        "scenario_id": "case-1",
        "formulation_id": "f-1",
        "viscosity_value": 35.0,
        "viscosity_unit": "cP",
        "viscosity_temperature_c": 25.0,
        "use_temperature_c": 25.0,
        "rheology_class": "newtonian",
        "newtonian_evidence": "RHEO-1",
        "needle_id_mm": 0.21,
        "needle_length_mm": 12.7,
        "needle_geometry_source": "drawing-1",
        "barrel_id_mm": 6.35,
        "barrel_geometry_source": "drawing-2",
        "volume_ml": 2.0,
        "injection_time_s": 15.0,
        "density_kg_m3": 1000.0,
    }
    values.update(changes)
    return AssessmentInput(**values)


def test_reference_equation_matches_independent_expression():
    result = assess(case())
    mu, length, flow = 0.035, 0.0127, 2e-6 / 15
    needle_id, barrel_id = 0.00021, 0.00635
    expected_pressure = 128 * mu * length * flow / (math.pi * needle_id**4)
    expected_force = expected_pressure * math.pi * barrel_id**2 / 4
    assert result.outputs["needle_pressure_drop_pa"] == pytest.approx(expected_pressure)
    assert result.outputs["fluid_resistance_force_n"] == pytest.approx(expected_force)


def test_simplified_force_equation_matches_pressure_area_path():
    result = assess(case())
    mu = 0.035
    length = 0.0127
    flow = 2e-6 / 15
    needle_id = 0.00021
    barrel_id = 0.00635
    simplified = 32.0 * mu * length * flow * barrel_id**2 / needle_id**4
    assert result.outputs["fluid_resistance_force_n"] == pytest.approx(simplified)


def test_hand_calculated_reference_fixture_matches_engine():
    fixture_path = Path(__file__).parent / "reference_data" / "reference_case.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    result = assess(AssessmentInput(**fixture["inputs"]))
    expected = fixture["expected"]
    assert result.outputs["dynamic_viscosity_pa_s"] == pytest.approx(
        expected["dynamic_viscosity_pa_s"]
    )
    assert result.outputs["flow_rate_m3_s"] == pytest.approx(expected["flow_rate_m3_s"])
    assert result.outputs["needle_pressure_drop_pa"] == pytest.approx(
        expected["needle_pressure_drop_pa"]
    )
    assert result.outputs["fluid_resistance_force_n"] == pytest.approx(
        expected["fluid_resistance_force_n"]
    )
    assert result.outputs["wall_shear_rate_s_1"] == pytest.approx(
        expected["wall_shear_rate_s_1"]
    )
    assert result.outputs["reynolds_number"] == pytest.approx(expected["reynolds_number"])
    assert result.outputs["fluid_resistance_force_n"] == pytest.approx(
        expected["simplified_force_n"]
    )


@pytest.mark.parametrize(
    ("change", "expected_ratio"),
    [
        ({"viscosity_value": 70.0}, 2.0),
        ({"needle_length_mm": 25.4}, 2.0),
        ({"barrel_id_mm": 12.7}, 4.0),
        ({"needle_id_mm": 0.42}, 1 / 16),
        ({"injection_time_s": 30.0}, 0.5),
    ],
)
def test_analytical_scaling(change, expected_ratio):
    baseline = assess(case()).outputs["fluid_resistance_force_n"]
    changed = assess(case(**change)).outputs["fluid_resistance_force_n"]
    assert changed / baseline == pytest.approx(expected_ratio)


def test_centipoise_and_pascal_second_are_equivalent():
    cp = assess(case(viscosity_value=35.0, viscosity_unit="cP"))
    pas = assess(case(viscosity_value=0.035, viscosity_unit="Pa_s"))
    assert cp.outputs["fluid_resistance_force_n"] == pytest.approx(
        pas.outputs["fluid_resistance_force_n"]
    )


def test_mpa_s_equivalent_to_centipoise():
    cp = assess(case(viscosity_value=35.0, viscosity_unit="cP"))
    mpas = assess(case(viscosity_value=35.0, viscosity_unit="mPa_s"))
    assert cp.outputs["fluid_resistance_force_n"] == pytest.approx(
        mpas.outputs["fluid_resistance_force_n"]
    )


@pytest.mark.parametrize("rheology", ["unknown", "shear_thinning", "non-newtonian"])
def test_non_newtonian_inputs_fail_closed(rheology):
    with pytest.raises(ScientificBoundaryError, match="Newtonian"):
        assess(case(rheology_class=rheology))


def test_temperature_extrapolation_fails_closed():
    with pytest.raises(ScientificBoundaryError, match="temperature"):
        assess(case(use_temperature_c=30.0))


def test_missing_density_returns_explicit_warning_and_null_reynolds():
    result = assess(case(density_kg_m3=None))
    assert result.outputs["reynolds_number"] is None
    assert result.status == "passed_with_warnings"
    codes = {warning.code for warning in result.warnings}
    assert "LAMINARITY_NOT_NUMERICALLY_VERIFIED" in codes


def test_sensitivity_nulls_companion_when_both_time_and_flow_supplied():
    both = case(injection_time_s=15.0, flow_rate_ml_s=2.0 / 15.0)
    result = assess(both)
    time_items = [item for item in result.sensitivity if item.input_name == "injection_time_s"]
    assert time_items
    for item in time_items:
        # F ~ t^{-1} at fixed volume: finite-difference relative change is (1+δ)^{-1}-1
        expected = (1.0 + item.relative_change) ** -1 - 1.0
        assert item.force_relative_change == pytest.approx(expected, rel=1e-9, abs=1e-9)


def test_sensitivity_supports_flow_rate_driven_inputs():
    flow_only = case(injection_time_s=None, flow_rate_ml_s=2.0 / 15.0)
    result = assess(flow_only)
    flow_items = [item for item in result.sensitivity if item.input_name == "flow_rate_ml_s"]
    assert flow_items
    for item in flow_items:
        expected = (1.0 + item.relative_change) ** 1 - 1.0
        assert item.force_relative_change == pytest.approx(expected, rel=1e-9, abs=1e-9)


def test_sensitivity_matches_analytical_elasticities():
    result = assess(case())
    by_name = {}
    for item in result.sensitivity:
        by_name.setdefault(item.input_name, []).append(item)

    def assert_power_law(name: str, power: float) -> None:
        for item in by_name[name]:
            expected = (1.0 + item.relative_change) ** power - 1.0
            assert item.force_relative_change == pytest.approx(expected, rel=1e-9, abs=1e-9)

    assert_power_law("viscosity_value", 1.0)
    assert_power_law("needle_length_mm", 1.0)
    assert_power_law("barrel_id_mm", 2.0)
    assert_power_law("needle_id_mm", -4.0)
    assert_power_law("injection_time_s", -1.0)


def test_multi_step_sensitivity_from_config():
    config = AssessmentConfig(sensitivity_relative_changes=(-0.10, -0.05, 0.05, 0.10))
    result = assess(case(), config=config)
    visc = [item for item in result.sensitivity if item.input_name == "viscosity_value"]
    assert [item.relative_change for item in visc] == [-0.10, -0.05, 0.05, 0.10]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"viscosity_value": True},
        {"needle_id_mm": "0.21"},
        {"volume_ml": float("nan")},
        {"viscosity_temperature_c": float("inf")},
        {"newtonian_evidence": 123},
        {"needle_geometry_source": None},
        {"viscosity_unit": "bogus"},
    ],
)
def test_construction_rejects_malformed_types(kwargs):
    with pytest.raises(InputValidationError):
        case(**kwargs)


def test_bool_viscosity_does_not_coerce_silently():
    with pytest.raises(InputValidationError, match="viscosity_value"):
        case(viscosity_value=True)


def test_inverse_screening_quantities_when_ceiling_supplied():
    result = assess(
        case(force_ceiling_n=50.0, force_ceiling_source="lab protocol FORCE-1")
    )
    assert result.outputs["max_flow_rate_m3_s_at_force_ceiling"] is not None
    assert result.outputs["min_injection_time_s_at_force_ceiling"] is not None
    assert any(w.code == "INVERSE_SCREENING_QUANTITIES" for w in result.warnings)
    q_max = result.outputs["max_flow_rate_m3_s_at_force_ceiling"]
    mu, length, d, db = 0.035, 0.0127, 0.00021, 0.00635
    expected_q = 50.0 * d**4 / (32.0 * mu * length * db**2)
    assert q_max == pytest.approx(expected_q)


def test_shear_and_rating_warning_codes():
    result = assess(
        case(
            validated_shear_rate_min_s_1=1.0,
            validated_shear_rate_max_s_1=10.0,
            component_pressure_rating_pa=1.0,
            needle_gauge_label="27G",
            needle_geometry_source="supplier drawing other-gauge",
        )
    )
    codes = {w.code for w in result.warnings}
    assert "SHEAR_RATE_OUTSIDE_EVIDENCE_RANGE" in codes
    assert "COMPONENT_PRESSURE_RATING_EXCEEDED" in codes
    assert "GAUGE_GEOMETRY_METADATA_INCONSISTENT" in codes
    assert "GEOMETRY_TOLERANCE_ABSENT" in codes
