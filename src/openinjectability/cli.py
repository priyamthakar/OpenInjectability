"""Command-line interface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .audit import write_audit_bundle
from .config import config_to_serializable, load_config
from .core import assess, assess_many
from .io import file_sha256, read_csv, write_json
from .models import (
    AssessmentInput,
    InputValidationError,
    OpenInjectabilityError,
    ScientificBoundaryError,
)
from .plotting import force_vs_needle_geometry
from .reporting import write_report

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

    compare = sub.add_parser(
        "compare-geometries", help="assess CSV and emit a geometry comparison plot"
    )
    compare.add_argument("input_csv", type=Path)
    compare.add_argument("--config", type=Path)
    compare.add_argument("--results", type=Path, default=Path("assessment.json"))
    compare.add_argument("--plot", type=Path, default=Path("geometry-comparison.png"))

    validate = sub.add_parser("validate-input", help="validate a CSV without writing results")
    validate.add_argument("input_csv", type=Path)
    validate.add_argument("--config", type=Path)

    status = sub.add_parser("validation-status", help="show scientific validation status")
    status.add_argument("--json", action="store_true")

    schema = sub.add_parser("schema", help="print the input schema")
    schema.add_argument("--format", choices=["json", "yaml"], default="json", dest="fmt")

    sub.add_parser("version", help="print package version")
    return parser


def _exit_for_error(exc: BaseException) -> int:
    if isinstance(exc, ScientificBoundaryError):
        print(f"error: {exc}", file=sys.stderr)
        return 3
    if isinstance(exc, OpenInjectabilityError):
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if isinstance(exc, (OSError, ValueError)):
        print(f"error: {exc}", file=sys.stderr)
        return 2
    raise exc


def _write_outputs(
    results: tuple[Any, ...],
    *,
    results_path: Path,
    report_path: Path | None,
    plot_path: Path | None,
    audit_path: Path | None,
    input_path: str | None,
    digest: str,
    config_payload: dict[str, object],
) -> None:
    payload: dict[str, object] = {
        "schema_version": "1.0",
        "input_path": input_path,
        "input_sha256": digest,
        "effective_configuration": config_payload,
        "results": [result.to_dict() for result in results],
    }
    write_json(payload, results_path)
    if report_path is not None:
        try:
            write_report(results, digest, report_path)
        except (OSError, RuntimeError, ValueError, ImportError) as exc:
            print(f"error: report generation failed: {exc}", file=sys.stderr)
            raise SystemExit(4) from exc
    if plot_path is not None:
        force_vs_needle_geometry(results, plot_path)
    if audit_path is not None:
        write_audit_bundle(
            destination=audit_path,
            results=results,
            input_sha256=digest,
            input_path=input_path,
            config=config_payload,
        )


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
                    raise InputValidationError(
                        "YAML schema output requires PyYAML"
                    ) from exc
                print(yaml.safe_dump(INPUT_SCHEMA, sort_keys=True), end="")
            else:
                print(json.dumps(INPUT_SCHEMA, indent=2, sort_keys=True))
            return 0
        if args.command == "validation-status":
            payload = {
                "package_version": __version__,
                "equation_status": "internal_validation",
                "experimental_status": "experimental_validation_pending",
                "model_scope": "Newtonian idealized needle-fluid resistance only",
            }
            print(
                json.dumps(payload, indent=2)
                if args.json
                else "\n".join(f"{key}: {value}" for key, value in payload.items())
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
                audit_path=None,
                input_path=None,
                digest=digest,
                config_payload=config_payload,
            )
            print(f"assessed: 1 scenario(s); results: {args.results}")
            return 0

        if args.command == "validate-input":
            cases = read_csv(args.input_csv)
            assess_many(cases, config=config)
            print(f"valid: {len(cases)} scenario(s)")
            return 0

        if args.command in {"assess", "compare-geometries"}:
            cases = read_csv(args.input_csv)
            results = assess_many(cases, config=config)
            digest = file_sha256(args.input_csv)
            plot_path = args.plot if args.command == "compare-geometries" else getattr(
                args, "plot", None
            )
            audit_path = getattr(args, "audit_bundle", None)
            _write_outputs(
                results,
                results_path=args.results,
                report_path=getattr(args, "report", None),
                plot_path=plot_path,
                audit_path=audit_path,
                input_path=str(args.input_csv),
                digest=digest,
                config_payload=config_payload,
            )
            print(f"assessed: {len(results)} scenario(s); results: {args.results}")
            return 0

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
