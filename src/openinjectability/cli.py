"""Command-line interface."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, replace
from importlib.resources import files
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, cast

from . import __version__
from .audit import write_audit_bundle
from .config import config_to_serializable, load_config
from .core import assess
from .io import file_sha256, read_csv_batch, write_json
from .models import (
    AssessmentConfig,
    AssessmentInput,
    AssessmentResult,
    InputValidationError,
    OpenInjectabilityError,
    RejectedAssessment,
    ScientificBoundaryError,
    ValidationRegistryError,
)
from .plotting import force_vs_needle_geometry, write_required_plots
from .reporting import html_report, markdown_report, write_report
from .validation_report import load_panel
from .validation_report import write_report as write_experimental_report

INPUT_SCHEMA: dict[str, Any] = {
    "schema_version": "1.0",
    "model_id": "newtonian_hagen_poiseuille_v1",
    "required_fields": [
        "scenario_id",
        "formulation_id",
        "viscosity_value",
        "viscosity_unit",
        "viscosity_temperature_c",
        "use_temperature_c",
        "rheology_class",
        "newtonian_evidence",
        "needle_id_mm",
        "needle_length_mm",
        "needle_geometry_source",
        "barrel_id_mm",
        "barrel_geometry_source",
        "volume_ml",
    ],
    "conditional_fields": ["injection_time_s", "flow_rate_ml_s", "force_ceiling_source"],
    "optional_fields": [
        "needle_gauge_label",
        "density_kg_m3",
        "force_ceiling_n",
        "notes",
        "validated_viscosity_min",
        "validated_viscosity_max",
        "validated_shear_rate_min_s_1",
        "validated_shear_rate_max_s_1",
        "component_pressure_rating_pa",
        "geometry_tolerance_relative",
    ],
    "viscosity_units": ["cP", "mPa_s", "Pa_s"],
    "result_name": "predicted fluid-resistance force",
}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="openinjectability",
        description="Newtonian predicted fluid-resistance assessment",
    )
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    assess_cmd = sub.add_parser("assess", help="assess all scenarios in a CSV")
    assess_cmd.add_argument("input_csv", type=Path)
    assess_cmd.add_argument("--config", type=Path)
    assess_cmd.add_argument("--results", type=Path, default=Path("assessment.json"))
    assess_cmd.add_argument("--report", type=Path)
    assess_cmd.add_argument("--plot", type=Path, help="force-versus-needle geometry plot")
    assess_cmd.add_argument("--plots-dir", type=Path, help="complete required plot set")
    assess_cmd.add_argument("--audit-bundle", type=Path, dest="audit_bundle")

    one = sub.add_parser("assess-one", help="assess a single scenario from CLI flags")
    one.add_argument("--scenario-id", default="cli-one")
    one.add_argument("--formulation-id", default="cli-formulation")
    one.add_argument("--viscosity-value", type=float, required=True)
    one.add_argument("--viscosity-unit", default="cP", choices=["cP", "mPa_s", "Pa_s"])
    one.add_argument("--viscosity-temperature", type=float, required=True)
    one.add_argument("--use-temperature", type=float, required=True)
    one.add_argument("--rheology", default="newtonian")
    one.add_argument("--rheology-evidence", required=True)
    one.add_argument("--needle-id", type=float, required=True)
    one.add_argument("--needle-length", type=float, required=True)
    one.add_argument("--needle-source", required=True)
    one.add_argument("--barrel-id", type=float, required=True)
    one.add_argument("--barrel-source", required=True)
    one.add_argument("--volume", type=float, required=True)
    one.add_argument("--injection-time", type=float)
    one.add_argument("--flow-rate", type=float)
    one.add_argument("--needle-gauge")
    one.add_argument("--density", type=float)
    one.add_argument("--force-ceiling", type=float)
    one.add_argument("--force-ceiling-source")
    one.add_argument("--config", type=Path)
    one.add_argument("--results", type=Path, default=Path("assessment.json"))
    one.add_argument("--report", type=Path)
    one.add_argument("--plots-dir", type=Path)
    one.add_argument("--audit-bundle", type=Path, dest="audit_bundle")

    compare = sub.add_parser(
        "compare-geometries", help="assess CSV and emit a geometry comparison plot"
    )
    compare.add_argument("input_csv", type=Path)
    compare.add_argument("--config", type=Path)
    compare.add_argument("--results", type=Path, default=Path("assessment.json"))
    compare.add_argument("--plot", type=Path, default=Path("geometry-comparison.png"))
    compare.add_argument("--plots-dir", type=Path)
    compare.add_argument("--report", type=Path)
    compare.add_argument("--audit-bundle", type=Path, dest="audit_bundle")

    validate = sub.add_parser("validate-input", help="validate a CSV without writing results")
    validate.add_argument("input_csv", type=Path)
    validate.add_argument("--config", type=Path)

    status = sub.add_parser("validation-status", help="show scientific validation status")
    status.add_argument("--json", action="store_true")

    experimental = sub.add_parser(
        "validate-experimental",
        help=(
            "compare an experimental panel JSON to model fluid-resistance force "
            "(never claims independently_validated)"
        ),
    )
    experimental.add_argument("panel_json", type=Path)
    experimental.add_argument(
        "--out",
        type=Path,
        required=True,
        help="output directory for report JSON, Markdown, and manifest.sha256",
    )

    schema = sub.add_parser("schema", help="print the input schema")
    schema.add_argument("--format", choices=["json", "yaml"], default="json", dest="fmt")

    sub.add_parser("version", help="print package version")
    return parser


def _exit_for_error(exc: BaseException) -> int:
    if isinstance(exc, ValidationRegistryError):
        print(f"error: {exc.code}: {exc}", file=sys.stderr)
        return 5
    if isinstance(exc, ScientificBoundaryError):
        print(f"error: {exc.code}: {exc}", file=sys.stderr)
        return 3
    if isinstance(exc, OpenInjectabilityError):
        print(f"error: {exc.code}: {exc}", file=sys.stderr)
        return 2
    if isinstance(exc, (OSError, ValueError)):
        print(f"error: {exc}", file=sys.stderr)
        return 2
    raise exc


def _validation_registry() -> dict[str, Any]:
    try:
        payload = json.loads(
            files("openinjectability")
            .joinpath("validation_registry")
            .joinpath("manifest.json")
            .read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationRegistryError("validation registry could not be loaded") from exc
    if payload.get("package_version") != __version__:
        raise ValidationRegistryError(
            "validation registry package_version does not match the installed package"
        )
    if payload.get("experimental_status") == "independently_validated":
        raise ValidationRegistryError(
            "installed alpha registry must not claim independently_validated"
        )
    return cast(dict[str, Any], payload)


def _write_outputs(
    results: tuple[AssessmentResult, ...],
    *,
    results_path: Path,
    report_path: Path | None,
    plot_path: Path | None,
    plots_dir: Path | None,
    audit_path: Path | None,
    rejected: tuple[RejectedAssessment, ...],
    input_path: str | None,
    digest: str,
    config_payload: dict[str, object],
) -> None:
    annotated = tuple(
        replace(
            result,
            provenance={
                **result.provenance,
                "source_file_sha256": digest,
                "source_file_reason": None if input_path else "not_applicable_assess_one",
                "source_file": input_path,
            },
        )
        for result in results
    )
    payload: dict[str, object] = {
        "schema_version": "1.0",
        "input_path": input_path,
        "input_sha256": digest,
        "effective_configuration": config_payload,
        "results": [result.to_dict() for result in annotated],
        "rejected": [asdict(item) for item in rejected],
    }
    write_json(payload, results_path)

    reproducibility_command = (
        f"python -m pip install openinjectability=={__version__}; "
        f'openinjectability assess "{input_path}" --results assessment.json'
        if input_path
        else f"python -m pip install openinjectability=={__version__}; openinjectability assess-one ..."
    )
    with TemporaryDirectory(prefix="openinjectability-artifacts-") as temporary:
        audit_plot_dir = Path(temporary) / "figures"
        external_figures: tuple[Path, ...] = ()
        audit_figures: tuple[Path, ...] = ()
        try:
            if annotated and plot_path is not None:
                force_vs_needle_geometry(annotated, plot_path)
            if annotated and plots_dir is not None:
                external_figures = write_required_plots(annotated, plots_dir)
            if annotated and audit_path is not None:
                audit_figures = write_required_plots(annotated, audit_plot_dir)
            report_figures = external_figures or audit_figures
            if report_path is not None:
                write_report(
                    annotated,
                    digest,
                    report_path,
                    source_path=input_path,
                    rejected=rejected,
                    reproducibility_command=reproducibility_command,
                    figure_paths=report_figures,
                )
        except (OSError, RuntimeError, ValueError, ImportError) as exc:
            print(f"error: report generation failed: {exc}", file=sys.stderr)
            raise SystemExit(4) from exc
        if audit_path is not None:
            markdown = markdown_report(
                annotated,
                digest,
                source_path=input_path,
                rejected=rejected,
                reproducibility_command=reproducibility_command,
                figure_paths=audit_figures,
            )
            for figure in audit_figures:
                markdown = markdown.replace(f"]({figure.name})", f"](../figures/{figure.name})")
            extras: dict[str, bytes] = {
                "reports/assessment.md": markdown.encode("utf-8"),
                "reports/assessment.html": html_report(
                    annotated,
                    digest,
                    source_path=input_path,
                    rejected=rejected,
                    reproducibility_command=reproducibility_command,
                    figure_paths=audit_figures,
                ).encode("utf-8"),
                "provenance/reproducibility.txt": (reproducibility_command + "\n").encode(),
            }
            extras.update(
                {f"figures/{figure.name}": figure.read_bytes() for figure in audit_figures}
            )
            if report_path is not None and report_path.is_file():
                extras[f"reports/requested{report_path.suffix.lower()}"] = report_path.read_bytes()
            input_bytes = (
                Path(input_path).read_bytes()
                if input_path is not None and Path(input_path).is_file()
                else None
            )
            write_audit_bundle(
                destination=audit_path,
                results=annotated,
                rejected=rejected,
                input_sha256=digest,
                input_path=input_path,
                input_bytes=input_bytes,
                config=config_payload,
                extra_files=extras,
            )


def _assess_csv(
    input_csv: Path, config: AssessmentConfig
) -> tuple[tuple[AssessmentResult, ...], tuple[RejectedAssessment, ...]]:
    parsed, parse_rejected = read_csv_batch(input_csv)
    results: list[AssessmentResult] = []
    rejected = list(parse_rejected)
    for row_number, case in parsed:
        try:
            results.append(assess(case, config=config))
        except OpenInjectabilityError as exc:
            rejected.append(
                RejectedAssessment(
                    row_number=row_number,
                    scenario_id=case.scenario_id,
                    error_type=type(exc).__name__,
                    error_code=exc.code,
                    message=str(exc),
                    field=exc.field,
                )
            )
    rejected.sort(key=lambda item: item.row_number)
    return tuple(results), tuple(rejected)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "version":
            print(__version__)
            return 0
        if args.command == "schema":
            if args.fmt == "yaml":
                try:
                    import yaml
                except ImportError as exc:
                    raise InputValidationError("YAML schema output requires PyYAML") from exc
                print(yaml.safe_dump(INPUT_SCHEMA, sort_keys=True), end="")
            else:
                print(json.dumps(INPUT_SCHEMA, indent=2, sort_keys=True))
            return 0
        if args.command == "validation-status":
            registry = _validation_registry()
            payload = {
                "package_version": __version__,
                "equation_status": registry["equation_status"],
                "experimental_status": registry["experimental_status"],
                "model_scope": "Newtonian idealized needle-fluid resistance only",
            }
            print(
                json.dumps(payload, indent=2)
                if args.json
                else "\n".join(f"{key}: {value}" for key, value in payload.items())
            )
            return 0

        if args.command == "validate-experimental":
            panel = load_panel(args.panel_json)
            written = write_experimental_report(
                panel,
                args.out,
                panel_path=args.panel_json,
            )
            summary = written["summary"]
            print(
                "experimental report: "
                f"status={summary['status']}; n={summary['n']}; "
                f"out={written['out_dir']}"
            )
            return 0

        config = load_config(getattr(args, "config", None))
        config_payload = config_to_serializable(config)

        if args.command == "assess-one":
            case = AssessmentInput(
                scenario_id=args.scenario_id,
                formulation_id=args.formulation_id,
                viscosity_value=args.viscosity_value,
                viscosity_unit=args.viscosity_unit,
                viscosity_temperature_c=args.viscosity_temperature,
                use_temperature_c=args.use_temperature,
                rheology_class=args.rheology,
                newtonian_evidence=args.rheology_evidence,
                needle_id_mm=args.needle_id,
                needle_length_mm=args.needle_length,
                needle_geometry_source=args.needle_source,
                barrel_id_mm=args.barrel_id,
                barrel_geometry_source=args.barrel_source,
                volume_ml=args.volume,
                injection_time_s=args.injection_time,
                flow_rate_ml_s=args.flow_rate,
                needle_gauge_label=args.needle_gauge,
                density_kg_m3=args.density,
                force_ceiling_n=args.force_ceiling,
                force_ceiling_source=args.force_ceiling_source,
            )
            result = assess(case, config=config)
            digest = "cli-assess-one"
            _write_outputs(
                (result,),
                results_path=args.results,
                report_path=args.report,
                plot_path=None,
                plots_dir=args.plots_dir,
                audit_path=args.audit_bundle,
                rejected=(),
                input_path=None,
                digest=digest,
                config_payload=config_payload,
            )
            print(f"assessed: 1 scenario(s); results: {args.results}")
            return 0

        if args.command == "validate-input":
            results, rejected = _assess_csv(args.input_csv, config)
            if rejected:
                for item in rejected:
                    print(
                        f"rejected row {item.row_number}: {item.error_code}: {item.message}",
                        file=sys.stderr,
                    )
                print(f"valid: {len(results)}; rejected: {len(rejected)}")
                return 2
            print(f"valid: {len(results)} scenario(s)")
            return 0

        if args.command in {"assess", "compare-geometries"}:
            results, rejected = _assess_csv(args.input_csv, config)
            digest = file_sha256(args.input_csv)
            plot_path = (
                args.plot if args.command == "compare-geometries" else getattr(args, "plot", None)
            )
            audit_path = getattr(args, "audit_bundle", None)
            _write_outputs(
                results,
                results_path=args.results,
                report_path=getattr(args, "report", None),
                plot_path=plot_path,
                plots_dir=getattr(args, "plots_dir", None),
                audit_path=audit_path,
                rejected=rejected,
                input_path=str(args.input_csv),
                digest=digest,
                config_payload=config_payload,
            )
            print(
                f"assessed: {len(results)} scenario(s); rejected: {len(rejected)}; "
                f"results: {args.results}"
            )
            for item in rejected:
                print(
                    f"error: row {item.row_number}: {item.error_code}: {item.message}",
                    file=sys.stderr,
                )
            if any(item.error_type == "ScientificBoundaryError" for item in rejected):
                return 3
            return 2 if rejected else 0

        raise InputValidationError(f"unknown command: {args.command}")
    except SystemExit as exc:
        code = exc.code
        return int(code) if isinstance(code, int) else 1
    except OpenInjectabilityError as exc:
        return _exit_for_error(exc)
    except (OSError, ValueError) as exc:
        return _exit_for_error(exc)


if __name__ == "__main__":
    raise SystemExit(main())
