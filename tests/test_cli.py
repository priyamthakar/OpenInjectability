import json
import zipfile
from pathlib import Path

from openinjectability.cli import main


def test_cli_generates_json_and_html(tmp_path):
    source = Path(__file__).parents[1] / "examples" / "formulation.csv"
    output = tmp_path / "assessment.json"
    report = tmp_path / "assessment.html"
    code = main(
        [
            "assess",
            str(source),
            "--results",
            str(output),
            "--report",
            str(report),
        ]
    )
    assert code == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["results"][0]["model_id"] == "newtonian_hagen_poiseuille_v1"
    report_text = report.read_text(encoding="utf-8")
    assert "predicted fluid-resistance force" in report_text
    assert "Package version: `0.1.1`" in report_text
    assert "example supplier drawing" in report_text
    assert "experimental_validation_pending" in report_text


def test_validation_status_is_conservative(capsys):
    assert main(["validation-status", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["experimental_status"] == "experimental_validation_pending"


def test_optional_pdf_and_plot_outputs(tmp_path):
    __import__("matplotlib")
    __import__("reportlab")
    source = Path(__file__).parents[1] / "examples" / "formulation.csv"
    output = tmp_path / "assessment.json"
    report = tmp_path / "assessment.pdf"
    plot = tmp_path / "force.png"
    code = main(
        [
            "assess",
            str(source),
            "--results",
            str(output),
            "--report",
            str(report),
            "--plot",
            str(plot),
        ]
    )
    assert code == 0
    assert report.read_bytes().startswith(b"%PDF")
    assert plot.read_bytes().startswith(b"\x89PNG")


def test_synthetic_formulation_screening_workflow(tmp_path):
    source = Path(__file__).parents[1] / "examples" / "formulation_screening.csv"
    output = tmp_path / "screening.json"
    report = tmp_path / "screening.md"
    plot = tmp_path / "screening.png"
    audit = tmp_path / "screening.zip"

    code = main(
        [
            "assess",
            str(source),
            "--results",
            str(output),
            "--report",
            str(report),
            "--plot",
            str(plot),
            "--audit-bundle",
            str(audit),
        ]
    )

    assert code == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert len(payload["results"]) == 3
    assert all(
        row["normalized_input"]["newtonian_evidence"] == "SYNTHETIC_EXAMPLE_NOT_EVIDENCE"
        for row in payload["results"]
    )
    assert "not total injection force" in report.read_text(encoding="utf-8")
    assert plot.read_bytes().startswith(b"\x89PNG")
    assert audit.read_bytes().startswith(b"PK")


def test_complete_report_plot_and_audit_artifact_set(tmp_path):
    source = Path(__file__).parents[1] / "examples" / "formulation_screening.csv"
    results = tmp_path / "assessment.json"
    report = tmp_path / "assessment.html"
    plots = tmp_path / "figures"
    audit = tmp_path / "assessment.zip"

    assert (
        main(
            [
                "assess",
                str(source),
                "--results",
                str(results),
                "--report",
                str(report),
                "--plots-dir",
                str(plots),
                "--audit-bundle",
                str(audit),
            ]
        )
        == 0
    )

    figure_names = sorted(path.name for path in plots.glob("*.png"))
    assert figure_names == [
        "force-vs-needle-geometry.png",
        "pressure-vs-flow-rate.png",
        "scenario-comparison.png",
        "sensitivity-synthetic-screen-25g.png",
        "sensitivity-synthetic-screen-27g.png",
        "sensitivity-synthetic-screen-29g.png",
    ]
    html = report.read_text(encoding="utf-8")
    for required in (
        "Equations and assumptions",
        "Run ID",
        "Generated UTC",
        "Deterministic sensitivity",
        "Rejected rows",
        "References",
        "Reproducibility",
        "data:image/png;base64,",
    ):
        assert required in html

    payload = json.loads(results.read_text(encoding="utf-8"))
    assert payload["rejected"] == []
    assert payload["results"][0]["provenance"]["source_file_sha256"]
    assert payload["results"][0]["diagnostic_reasons"] == {}
    sensitivity = payload["results"][0]["sensitivity"][0]
    assert "needle_pressure_drop_pa" in sensitivity
    assert "analytical_force_elasticity" in sensitivity

    with zipfile.ZipFile(audit) as archive:
        names = set(archive.namelist())
        required_entries = {
            "input/original.csv",
            "input/normalized.csv",
            "config/effective_config.json",
            "results/assessment.json",
            "reports/assessment.html",
            "reports/assessment.md",
            "provenance/environment.json",
            "provenance/validation_manifest.json",
            "manifest.sha256",
        }
        assert required_entries <= names
        assert all(f"figures/{name}" in names for name in figure_names)
        manifest = json.loads(archive.read("manifest.sha256"))
        assert manifest["algorithm"] == "sha256"
        assert set(manifest["files"]) == names - {"manifest.sha256"}
