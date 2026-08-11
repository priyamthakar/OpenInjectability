"""Verify required wheel and source-distribution contents and metadata."""

from __future__ import annotations

import argparse
import ast
import email
import tarfile
import zipfile
from pathlib import Path


def _version(root: Path) -> str:
    tree = ast.parse((root / "src/openinjectability/_version.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "__version__"
                for target in node.targets
            )
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            return node.value.value
    raise SystemExit("could not read package version")


def verify(dist: Path, root: Path) -> None:
    version = _version(root)
    wheel = dist / f"openinjectability-{version}-py3-none-any.whl"
    sdist = dist / f"openinjectability-{version}.tar.gz"
    if not wheel.is_file() or not sdist.is_file():
        raise SystemExit(f"missing distribution files for version {version}")

    with zipfile.ZipFile(wheel) as archive:
        wheel_names = set(archive.namelist())
        required_wheel = {
            "openinjectability/_version.py",
            "openinjectability/validation_registry/manifest.json",
            f"openinjectability-{version}.dist-info/METADATA",
        }
        missing_wheel = required_wheel - wheel_names
        if missing_wheel:
            raise SystemExit(f"wheel missing: {sorted(missing_wheel)}")
        metadata = email.message_from_bytes(
            archive.read(f"openinjectability-{version}.dist-info/METADATA")
        )
        if metadata["Name"] != "openinjectability" or metadata["Version"] != version:
            raise SystemExit("wheel metadata name/version mismatch")

    prefix = f"openinjectability-{version}/"
    with tarfile.open(sdist, "r:gz") as archive:
        sdist_names = set(archive.getnames())
    required_sdist = {
        prefix + "README.md",
        prefix + "COMPLETION_AUDIT.md",
        prefix + "docs/scientific-basis.md",
        prefix + "examples/formulation_screening.csv",
        prefix + "validation/independent_reference.py",
        prefix + "validation/experimental/schema.json",
    }
    missing_sdist = required_sdist - sdist_names
    if missing_sdist:
        raise SystemExit(f"sdist missing: {sorted(missing_sdist)}")

    print(f"verified wheel and sdist contents for openinjectability {version}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dist", nargs="?", type=Path, default=Path("dist"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    verify(args.dist.resolve(), root)


if __name__ == "__main__":
    main()
