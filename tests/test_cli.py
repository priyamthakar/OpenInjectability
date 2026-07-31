import json
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
    assert "predicted fluid-resistance force" in report.read_text(encoding="utf-8")


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
