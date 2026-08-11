"""CSV, config, CLI exit-code, and packaging edge-path tests on shipped code."""

from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path

import pytest

from openinjectability import (
    AssessmentInput,
    InputValidationError,
    ScientificBoundaryError,
    ValidationRegistryError,
    assess,
)
from openinjectability.audit import write_audit_bundle
from openinjectability.cli import _exit_for_error, main
from openinjectability.config import load_config
from openinjectability.io import read_csv


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    headers = list(rows[0].keys())
    lines = [",".join(headers)]
    for row in rows:
        lines.append(",".join(row[h] for h in headers))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _good_row(**changes: str) -> dict[str, str]:
    row = {
        "scenario_id": "s1",
        "formulation_id": "f1",
        "viscosity_value": "35",
        "viscosity_unit": "cP",
        "viscosity_temperature_c": "25",
        "use_temperature_c": "25",
        "rheology_class": "newtonian",
        "newtonian_evidence": "R1",
        "needle_id_mm": "0.21",
        "needle_length_mm": "12.7",
        "needle_geometry_source": "draw",
        "barrel_id_mm": "6.35",
        "barrel_geometry_source": "syr",
        "volume_ml": "2",
        "injection_time_s": "15",
        "flow_rate_ml_s": "",
        "density_kg_m3": "1000",
        "force_ceiling_n": "",
        "force_ceiling_source": "",
        "notes": "",
        "needle_gauge_label": "",
    }
    row.update(changes)
    return row


def test_read_csv_rejects_duplicate_and_missing_required(tmp_path):
    path = tmp_path / "dup.csv"
    _write_csv(path, [_good_row(), _good_row()])
    with pytest.raises(InputValidationError, match="duplicate scenario_id"):
        read_csv(path)

    empty = tmp_path / "empty.csv"
    empty.write_text("scenario_id,formulation_id\n", encoding="utf-8")
    with pytest.raises(InputValidationError, match="no data rows|missing required"):
        read_csv(empty)

    bad = tmp_path / "bad.csv"
    _write_csv(path=bad, rows=[_good_row(viscosity_value="not-a-number")])
    with pytest.raises(InputValidationError, match="numeric|CSV row"):
        read_csv(bad)


def test_read_csv_accepts_valid_example():
    source = Path(__file__).parents[1] / "examples" / "formulation.csv"
    cases = read_csv(source)
    assert len(cases) == 1
    assert cases[0].scenario_id == "example-newtonian-27g"


def test_load_config_defaults_and_errors(tmp_path):
    assert load_config(None).model_id == "newtonian_hagen_poiseuille_v1"
    with pytest.raises(InputValidationError, match="not found"):
        load_config(tmp_path / "missing.json")
    weird = tmp_path / "cfg.txt"
    weird.write_text("{}", encoding="utf-8")
    with pytest.raises(InputValidationError, match="must be .json"):
        load_config(weird)
    bad_json = tmp_path / "bad.json"
    bad_json.write_text("{", encoding="utf-8")
    with pytest.raises(InputValidationError, match="invalid config"):
        load_config(bad_json)
    array = tmp_path / "arr.json"
    array.write_text("[1,2]", encoding="utf-8")
    with pytest.raises(InputValidationError, match="object"):
        load_config(array)
    schema = tmp_path / "schema.json"
    schema.write_text(json.dumps({"schema_version": "9.9"}), encoding="utf-8")
    with pytest.raises(InputValidationError, match="schema_version"):
        load_config(schema)
    sens = tmp_path / "sens.json"
    sens.write_text(
        json.dumps({"sensitivity": {"relative_changes": []}}),
        encoding="utf-8",
    )
    with pytest.raises(InputValidationError, match="relative_changes"):
        load_config(sens)
    sens_type = tmp_path / "sens2.json"
    sens_type.write_text(json.dumps({"sensitivity": "nope"}), encoding="utf-8")
    with pytest.raises(InputValidationError, match="sensitivity"):
        load_config(sens_type)


def test_cli_exit_codes_for_domain_errors(tmp_path, capsys):
    # scientific boundary
    path = tmp_path / "nn.csv"
    _write_csv(path, [_good_row(rheology_class="shear_thinning")])
    code = main(["assess", str(path), "--results", str(tmp_path / "out.json")])
    assert code == 3
    assert "error:" in capsys.readouterr().err


def test_cli_preserves_valid_rows_and_records_rejected_rows(tmp_path, capsys):
    source = tmp_path / "mixed.csv"
    _write_csv(source, [_good_row(), _good_row(scenario_id="bad-2", viscosity_value="")])
    output = tmp_path / "mixed.json"

    assert main(["assess", str(source), "--results", str(output)]) == 2
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert len(payload["results"]) == 1
    assert len(payload["rejected"]) == 1
    rejection = payload["rejected"][0]
    assert rejection["row_number"] == 3
    assert rejection["scenario_id"] == "bad-2"
    assert rejection["error_code"] == "MISSING_REQUIRED_VALUE"
    assert rejection["field"] == "viscosity_value"
    assert "error: row 3" in capsys.readouterr().err

    # input validation (inconsistent time/flow)
    path2 = tmp_path / "bad.csv"
    _write_csv(
        path2,
        [_good_row(injection_time_s="15", flow_rate_ml_s="999")],
    )
    code = main(["assess", str(path2), "--results", str(tmp_path / "out2.json")])
    assert code == 2


def test_cli_validate_input_and_schema_yaml(capsys):
    source = Path(__file__).parents[1] / "examples" / "formulation.csv"
    assert main(["validate-input", str(source)]) == 0
    assert "valid:" in capsys.readouterr().out
    assert main(["schema", "--format", "yaml"]) == 0
    out = capsys.readouterr().out
    assert "result_name" in out
    assert "predicted fluid-resistance force" in out


def test_cli_validation_status_text(capsys):
    assert main(["validation-status"]) == 0
    text = capsys.readouterr().out
    assert "experimental_validation_pending" in text


def test_exit_for_error_helpers():
    assert _exit_for_error(ScientificBoundaryError("x")) == 3
    assert _exit_for_error(InputValidationError("y")) == 2
    assert _exit_for_error(ValidationRegistryError("registry")) == 5
    assert _exit_for_error(ValueError("z")) == 2
    with pytest.raises(RuntimeError):
        _exit_for_error(RuntimeError("boom"))


def test_audit_bundle_with_extra_files(tmp_path):
    case = AssessmentInput(
        scenario_id="a",
        formulation_id="f",
        viscosity_value=35.0,
        viscosity_unit="cP",
        viscosity_temperature_c=25.0,
        use_temperature_c=25.0,
        rheology_class="newtonian",
        newtonian_evidence="R",
        needle_id_mm=0.21,
        needle_length_mm=12.7,
        needle_geometry_source="d",
        barrel_id_mm=6.35,
        barrel_geometry_source="s",
        volume_ml=2.0,
        injection_time_s=15.0,
    )
    result = assess(case)
    dest = tmp_path / "bundle.zip"
    write_audit_bundle(
        destination=dest,
        results=(result,),
        input_sha256="deadbeef",
        extra_files={"notes.txt": b"hello"},
    )
    assert dest.is_file()
    import zipfile

    with zipfile.ZipFile(dest) as zf:
        assert "notes.txt" in zf.namelist()
        assert zf.read("notes.txt") == b"hello"


def test_force_ceiling_exceeded_warning():
    result = assess(
        AssessmentInput(
            scenario_id="ceil",
            formulation_id="f",
            viscosity_value=35.0,
            viscosity_unit="cP",
            viscosity_temperature_c=25.0,
            use_temperature_c=25.0,
            rheology_class="newtonian",
            newtonian_evidence="R",
            needle_id_mm=0.21,
            needle_length_mm=12.7,
            needle_geometry_source="d",
            barrel_id_mm=6.35,
            barrel_geometry_source="s",
            volume_ml=2.0,
            injection_time_s=15.0,
            force_ceiling_n=1.0,
            force_ceiling_source="lab-1",
        )
    )
    codes = {w.code for w in result.warnings}
    assert "USER_FORCE_CEILING_EXCEEDED" in codes
    assert "INVERSE_SCREENING_QUANTITIES" in codes


def test_main_module_entry_reports_version(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["openinjectability", "version"])
    with pytest.raises(SystemExit) as exc:
        runpy.run_module("openinjectability.__main__", run_name="__main__")
    assert exc.value.code == 0
    assert "0.1.1" in capsys.readouterr().out
