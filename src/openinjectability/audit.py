"""Deterministic audit-bundle ZIP writer."""

from __future__ import annotations

import hashlib
import io
import json
import platform
import sys
import zipfile
from collections.abc import Iterable, Mapping
from dataclasses import asdict
from importlib.resources import files
from pathlib import Path
from typing import Any

from .models import AssessmentResult, RejectedAssessment


def _stable_json(data: object) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def write_audit_bundle(
    *,
    destination: str | Path,
    results: Iterable[AssessmentResult],
    rejected: Iterable[RejectedAssessment] = (),
    input_sha256: str,
    input_path: str | None = None,
    input_bytes: bytes | None = None,
    config: Mapping[str, Any] | None = None,
    extra_files: Mapping[str, bytes] | None = None,
) -> Path:
    """Write a ZIP with deterministic entry order and manifest.sha256."""

    path = Path(destination)
    materialized = tuple(results)
    rejected_items = tuple(rejected)
    normalized = io.StringIO(newline="")
    if materialized:
        import csv

        fieldnames = sorted(materialized[0].normalized_input)
        writer = csv.DictWriter(normalized, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for result in materialized:
            writer.writerow(result.normalized_input)
    validation_manifest = (
        files("openinjectability")
        .joinpath("validation_registry")
        .joinpath("manifest.json")
        .read_bytes()
    )
    entries: dict[str, bytes] = {
        "results/assessment.json": _stable_json(
            {
                "schema_version": "1.0",
                "input_path": input_path,
                "input_sha256": input_sha256,
                "results": [item.to_dict() for item in materialized],
                "rejected": [asdict(item) for item in rejected_items],
            }
        ),
        "input/normalized.csv": normalized.getvalue().encode("utf-8"),
        "config/effective_config.json": _stable_json(config or {}),
        "provenance/environment.json": _stable_json(
            {
                "python_version": platform.python_version(),
                "python_implementation": platform.python_implementation(),
                "platform": platform.platform(),
                "executable": Path(sys.executable).name,
            }
        ),
        "provenance/validation_manifest.json": validation_manifest,
        "provenance/exclusions.txt": (
            "\n".join(materialized[0].exclusions if materialized else []) + "\n"
        ).encode("utf-8")
        if materialized
        else b"",
    }
    if input_bytes is not None:
        entries["input/original.csv"] = input_bytes
    if extra_files:
        for name, content in sorted(extra_files.items()):
            entries[name] = content

    digests: dict[str, str] = {
        name: hashlib.sha256(content).hexdigest() for name, content in sorted(entries.items())
    }
    manifest_body = _stable_json({"algorithm": "sha256", "files": digests})
    entries["manifest.sha256"] = manifest_body

    # Deterministic archive: sorted names, fixed timestamps.
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(entries):
            info = zipfile.ZipInfo(filename=name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, entries[name])
    return path
