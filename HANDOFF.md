# OpenInjectability handoff

**Snapshot date:** 2026-07-31  
**Baseline commit:** `0add542847977da2ddd723f57a55cee353056c51`  
**Package version:** `0.1.0`  
**Lifecycle state:** alpha; internal verification only

## Product destination

The canonical final goal and definition of complete are in
[PROJECT_GOAL.md](PROJECT_GOAL.md). The project remains deliberately limited to
Newtonian fluid resistance and must never label the result as total device
force.

## Verified baseline

The 2026-07-31 audit confirmed 21 passing tests, Ruff, package builds, 87%
branch coverage, wheel import, Python 3.11/3.13 import smoke tests, and a passing
GitHub Quality run for the baseline commit. Independent experimental validation
remains pending.

## Open release gates

1. Sensitivity changes to injection time must not leave a supplied flow rate
   scientifically inconsistent with volume and time.
2. Malformed typed/provenance values must return stable domain errors rather
   than raw exceptions or silent Boolean-to-number coercion.
3. Backend batch input must reject duplicate scenario identifiers.
4. `VALIDATION.md` claims must map to inspectable independent fixtures and
   tests.
5. Strict static typing and the declared Python 3.10-3.13 compatibility matrix
   must become enforced release gates.

## Next objective

Implement the first three fail-closed defects, add regression tests for each,
then reconcile the validation document and CI gates. Do not broaden the
scientific model during this hardening step.

## Verification commands

```powershell
python -m pytest --cov=openinjectability --cov-branch
python -m ruff check src tests
python -m mypy --strict src
python -m build
```

After building, install the wheel into a fresh environment and run the CLI help,
example assessment, and package import against the installed artifact rather
than the repository source tree.
