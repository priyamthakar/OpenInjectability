"""Command-line interface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .core import assess_many
from .io import file_sha256, read_csv, write_json
from .models import OpenInjectabilityError
from .plotting import force_vs_needle_geometry
from .reporting import write_report


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="openinjectability",
        description="Newtonian predicted fluid-resistance assessment",
    )
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    assess = sub.add_parser("assess", help="assess all scenarios in a CSV")
    assess.add_argument("input_csv", type=Path)
    assess.add_argument("--results", type=Path, default=Path("assessment.json"))
    assess.add_argument("--report", type=Path)
    assess.add_argument("--plot", type=Path, help="force-versus-needle geometry plot")

    validate = sub.add_parser("validate-input", help="validate a CSV without writing results")
    validate.add_argument("input_csv", type=Path)

    status = sub.add_parser("validation-status", help="show scientific validation status")
    status.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "validate-input":
            cases = read_csv(args.input_csv)
            assess_many(cases)
            print(f"valid: {len(cases)} scenario(s)")
            return 0
        if args.command == "validation-status":
            payload = {
                "package_version": __version__,
                "equation_status": "internal_validation",
                "experimental_status": "experimental_validation_pending",
                "model_scope": "Newtonian idealized needle-fluid resistance only",
            }
            print(json.dumps(payload, indent=2) if args.json else "\n".join(
                f"{key}: {value}" for key, value in payload.items()
            ))
            return 0
        cases = read_csv(args.input_csv)
        results = assess_many(cases)
        digest = file_sha256(args.input_csv)
        payload = {
            "schema_version": "1.0",
            "input_path": str(args.input_csv),
            "input_sha256": digest,
            "results": [result.to_dict() for result in results],
        }
        write_json(payload, args.results)
        if args.report:
            write_report(results, digest, args.report)
        if args.plot:
            force_vs_needle_geometry(results, args.plot)
        print(f"assessed: {len(results)} scenario(s); results: {args.results}")
        return 0
    except OpenInjectabilityError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
