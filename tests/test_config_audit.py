import json
import zipfile
from pathlib import Path

import pytest

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 compatibility
    import tomli as tomllib

from openinjectability import AssessmentInput, InputValidationError, __version__, assess
from openinjectability.audit import write_audit_bundle
from openinjectability.cli import main
from openinjectability.config import load_config


def test_version_source_matches_packaging_results_and_registry():
    root = Path(__file__).parents[1]
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    manifest = json.loads(
        (root / "src/openinjectability/validation_registry/manifest.json").read_text(
            encoding="utf-8"
        )
    )

    assert pyproject["project"]["dynamic"] == ["version"]
    assert pyproject["tool"]["setuptools"]["dynamic"]["version"]["attr"] == (
        "openinjectability._version.__version__"
    )
    assert manifest["package_version"] == __version__
    assert manifest["distribution"] == "https://pypi.org/project/openinjectability/"
    assert assess(_case()).package_version == __version__


def _case(**changes):
    values = {
        "scenario_id": "cfg-1",
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


def test_load_json_config_multi_step_sensitivity(tmp_path):
    path = tmp_path / "cfg.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "calculation_model": "newtonian_hagen_poiseuille_v1",
                "temperature_tolerance_c": 0.25,
                "sensitivity": {"relative_changes": [-0.1, 0.1]},
            }
        ),
        encoding="utf-8",
    )
    config = load_config(path)
    assert config.temperature_tolerance_c == 0.25
    assert config.sensitivity_relative_changes == (-0.1, 0.1)
    result = assess(_case(), config=config)
    assert result.effective_configuration["temperature_tolerance_c"] == 0.25
    assert result.effective_configuration["display_force_unit"] == "N"
    assert result.effective_configuration["display_pressure_unit"] == "MPa"


def test_load_yaml_config(tmp_path):
    path = tmp_path / "cfg.yaml"
    path.write_text(
        "schema_version: '1.0'\n"
        "calculation_model: newtonian_hagen_poiseuille_v1\n"
        "time_flow_relative_tolerance: 0.002\n",
        encoding="utf-8",
    )
    config = load_config(path)
    assert config.time_flow_relative_tolerance == 0.002


def test_load_config_rejects_unknown_model(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text(
        json.dumps({"calculation_model": "not-a-model"}),
        encoding="utf-8",
    )
    with pytest.raises(InputValidationError, match="calculation_model"):
        load_config(path)


def test_audit_bundle_is_deterministic(tmp_path):
    result = assess(_case())
    first = tmp_path / "a.zip"
    second = tmp_path / "b.zip"
    write_audit_bundle(
        destination=first,
        results=(result,),
        input_sha256="abc",
        input_path="in.csv",
        config={"model_id": "newtonian_hagen_poiseuille_v1"},
    )
    write_audit_bundle(
        destination=second,
        results=(result,),
        input_sha256="abc",
        input_path="in.csv",
        config={"model_id": "newtonian_hagen_poiseuille_v1"},
    )
    assert first.read_bytes() == second.read_bytes()
    with zipfile.ZipFile(first) as archive:
        names = archive.namelist()
        assert names == sorted(names)
        assert "manifest.sha256" in names
        manifest = json.loads(archive.read("manifest.sha256"))
        assert manifest["algorithm"] == "sha256"
        assert "results/assessment.json" in manifest["files"]
        assert "input/normalized.csv" in manifest["files"]
        assert "config/effective_config.json" in manifest["files"]
        assert "provenance/environment.json" in manifest["files"]
        assert "provenance/validation_manifest.json" in manifest["files"]


def test_cli_version_and_schema(capsys):
    assert main(["version"]) == 0
    assert capsys.readouterr().out.strip() == "0.1.1"
    assert main(["schema", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["result_name"] == "predicted fluid-resistance force"


def test_cli_assess_one_and_audit_bundle(tmp_path):
    results = tmp_path / "one.json"
    audit = tmp_path / "bundle.zip"
    source = Path(__file__).parents[1] / "examples" / "formulation.csv"
    code = main(
        [
            "assess",
            str(source),
            "--results",
            str(results),
            "--audit-bundle",
            str(audit),
        ]
    )
    assert code == 0
    assert results.is_file()
    assert audit.is_file()
    payload = json.loads(results.read_text(encoding="utf-8"))
    force = payload["results"][0]["outputs"]["fluid_resistance_force_n"]
    assert force > 0
    assert "fluid_resistance_force_n" in payload["results"][0]["outputs"]

    one = tmp_path / "assess-one.json"
    code = main(
        [
            "assess-one",
            "--viscosity-value",
            "35",
            "--viscosity-temperature",
            "25",
            "--use-temperature",
            "25",
            "--rheology-evidence",
            "R1",
            "--needle-id",
            "0.21",
            "--needle-length",
            "12.7",
            "--needle-source",
            "draw",
            "--barrel-id",
            "6.35",
            "--barrel-source",
            "syr",
            "--volume",
            "2",
            "--injection-time",
            "15",
            "--results",
            str(one),
        ]
    )
    assert code == 0
    one_payload = json.loads(one.read_text(encoding="utf-8"))
    assert one_payload["results"][0]["outputs"]["fluid_resistance_force_n"] > 0


def test_cli_compare_geometries(tmp_path):
    __import__("matplotlib")
    source = Path(__file__).parents[1] / "examples" / "formulation.csv"
    plot = tmp_path / "geo.png"
    results = tmp_path / "cmp.json"
    assert (
        main(
            [
                "compare-geometries",
                str(source),
                "--results",
                str(results),
                "--plot",
                str(plot),
            ]
        )
        == 0
    )
    assert plot.read_bytes().startswith(b"\x89PNG")
