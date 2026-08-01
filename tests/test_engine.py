"""Tests for the side-effect-free backend engine contract."""

from __future__ import annotations

import pytest

from openinjectability import (
    AssessmentConfig,
    AssessmentInput,
    InputValidationError,
    OpenInjectabilityEngine,
    engine_metadata,
)


def case(**changes: object) -> AssessmentInput:
    values: dict[str, object] = {
        "scenario_id": "engine-case",
        "formulation_id": "formulation-1",
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
    return AssessmentInput(**values)  # type: ignore[arg-type]


def test_engine_exposes_immutable_versioned_capabilities():
    metadata = engine_metadata()

    assert metadata.engine_name == "OpenInjectabilityEngine"
    assert metadata.engine_version == "0.1.0"
    assert metadata.supported_rheology_classes == ("newtonian",)
    assert metadata.filesystem_side_effects is False
    assert "syringe friction" in metadata.exclusions[0]
    assert metadata.to_dict()["result_schema_version"] == "1.0"


def test_engine_single_case_reuses_validated_core_with_its_configuration():
    engine = OpenInjectabilityEngine(AssessmentConfig(temperature_tolerance_c=0.2))
    result = engine.assess(case(use_temperature_c=25.1))

    assert result.model_id == "newtonian_hagen_poiseuille_v1"
    assert result.outputs["fluid_resistance_force_n"] > 0
    assert engine.config.temperature_tolerance_c == 0.2


def test_engine_rejects_wrong_programmatic_input_type():
    with pytest.raises(InputValidationError, match="AssessmentInput"):
        OpenInjectabilityEngine().assess("not-an-assessment")  # type: ignore[arg-type]


def test_engine_rejects_an_unimplemented_model_id():
    with pytest.raises(InputValidationError, match="supports only model_id"):
        OpenInjectabilityEngine(AssessmentConfig(model_id="unvalidated_model"))


def test_batch_preserves_accepted_order_and_records_explicit_rejections():
    engine = OpenInjectabilityEngine()
    batch = engine.assess_batch(
        (
            case(scenario_id="first"),
            case(scenario_id="unsupported", rheology_class="shear_thinning"),
            case(scenario_id="third", use_temperature_c=30.0),
            case(scenario_id="fourth"),
        )
    )

    assert [result.normalized_input["scenario_id"] for result in batch.results] == [
        "first",
        "fourth",
    ]
    assert [(item.row_number, item.scenario_id, item.error_type) for item in batch.rejected] == [
        (2, "unsupported", "ScientificBoundaryError"),
        (3, "third", "ScientificBoundaryError"),
    ]
    assert "Newtonian" in batch.rejected[0].message
    assert "temperature" in batch.rejected[1].message


def test_batch_rejects_wrong_input_type_without_losing_later_cases():
    batch = OpenInjectabilityEngine().assess_batch(
        (case(scenario_id="first"), "wrong", case(scenario_id="third"))  # type: ignore[arg-type]
    )

    assert [result.normalized_input["scenario_id"] for result in batch.results] == [
        "first",
        "third",
    ]
    assert batch.rejected[0].row_number == 2
    assert batch.rejected[0].scenario_id is None
    assert batch.rejected[0].error_type == "InputValidationError"


def test_batch_rejects_duplicate_scenario_ids_without_dropping_later_cases():
    batch = OpenInjectabilityEngine().assess_batch(
        (
            case(scenario_id="alpha"),
            case(scenario_id="beta"),
            case(scenario_id="alpha"),
            case(scenario_id="gamma"),
            case(scenario_id="beta"),
        )
    )

    assert [result.normalized_input["scenario_id"] for result in batch.results] == [
        "alpha",
        "beta",
        "gamma",
    ]
    assert [(item.row_number, item.scenario_id, item.error_type) for item in batch.rejected] == [
        (3, "alpha", "InputValidationError"),
        (5, "beta", "InputValidationError"),
    ]
    assert batch.rejected[0].message == "duplicate scenario_id: 'alpha'"
    assert batch.rejected[1].message == "duplicate scenario_id: 'beta'"
