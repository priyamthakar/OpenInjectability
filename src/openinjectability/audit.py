"""Deterministic audit-bundle ZIP writer."""

from __future__ import annotations

import hashlib
import json
import zipfile
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from .models import AssessmentResult


def _stable_json(data: object) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n").encode(
        "utf-8"
    )


def write_audit_bundle(
    *,
    destination: str | Path,
    results: Iterable[AssessmentResult],
    input_sha256: str,
    input_path: str | None = None,
    config: Mapping[str, Any] | None = None,
    extra_files: Mapping[str, bytes] | None = None,
) -> Path:
    """Write a ZIP with deterministic entry order and manifest.sha256."""

    path = Path(destination)
    materialized = tuple(results)
    entries: dict[str, bytes] = {
        "results.json": _stable_json(
            {
                "schema_version": "1.0",
                "input_path": input_path,
                "input_sha256": input_sha256,
                "results": [item.to_dict() for item in materialized],
            }
        ),
        "effective_configuration.json": _stable_json(config or {}),
        "exclusions.txt": (
            "\n".join(materialized[0].exclusions if materialized else []) + "\n"
        ).encode("utf-8")
        if materialized
        else b"",
    }
    if extra_files:
        for name, content in sorted(extra_files.items()):
            entries[name] = content

    digests: dict[str, str] = {
        name: hashlib.sha256(content).hexdigest() for name, content in sorted(entries.items())
    }
    manifest_body = _stable_json(digests)
    entries["manifest.sha256"] = manifest_body

    # Deterministic archive: sorted names, fixed timestamps.
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(entries):
            info = zipfile.ZipInfo(filename=name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, entries[name])
    return path
