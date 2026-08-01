# OpenInjectability handoff

**Snapshot date:** 2026-08-01  
**Baseline commit:** `7500ccf`  
**Package version:** `0.1.0`  
**Lifecycle state:** alpha; internal verification only

## Product destination

The canonical final goal and definition of complete are in
[PROJECT_GOAL.md](PROJECT_GOAL.md). The project remains deliberately limited to
Newtonian fluid resistance and must never label the result as total device
force.

## Verified baseline

Phases A–C from [project.md](project.md) are closed: 46 tests, Ruff, `mypy
--strict`, package build, ≥87% coverage, wheel install smoke, and CI matrix
enforcement for Python 3.10–3.13. Independent experimental validation remains
pending.

## Closed release gates (formerly open)

1. Sensitivity preserves the flow/time contract via the validated core path.
2. Malformed typed/provenance values return stable domain errors (no bool
   coercion / raw TypeError/AttributeError).
3. Backend batch rejects duplicate scenario identifiers.
4. `VALIDATION.md` is a claims-to-evidence map with
   `tests/reference_data/reference_case.json`.
5. Strict typing and the 3.10–3.13 matrix are enforced in CI.

## Next objective

Phase D: obtain an independently traceable Newtonian experimental dataset under
the locked protocol in [docs/validation-protocol-lock.md](docs/validation-protocol-lock.md).
Do not advance `validation_status` without a published hashed validation report.
Phase E public publish waits on D and registry credentials.

## Verification commands

```powershell
python -m pytest --cov=openinjectability --cov-branch --cov-fail-under=87
python -m ruff check src tests
python -m mypy --strict src
python -m build
```

After building, install the wheel into a fresh environment and run the CLI help,
example assessment, and package import against the installed artifact rather
than the repository source tree.
