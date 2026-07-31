import math

import pytest

from openinjectability import (
    AssessmentInput,
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
    assert result.warnings[0].code == "LAMINARITY_NOT_NUMERICALLY_VERIFIED"
