# OpenInjectability handoff

**Snapshot date:** 2026-08-02  
**Baseline commit:** see `git log -1` on `main`  
**Package version:** `0.1.0`  
**Lifecycle state:** alpha; internal verification only

## Product destination

The canonical final goal and definition of complete are in
[PROJECT_GOAL.md](PROJECT_GOAL.md). The project remains deliberately limited to
Newtonian fluid resistance and must never label the result as total device
force.

## Verified baseline

Phases **A–C** from [project.md](project.md) are closed: full test suite, Ruff,
`mypy --strict`, package build, ≥87% branch coverage, wheel install smoke, and
CI matrix enforcement for Python 3.10–3.13.

| Phase | Status | Notes |
|---|---|---|
| A — v0.1 hardening | **Done** | Sensitivity contract, construction-time types, batch duplicates, VALIDATION claims map, mypy + CI matrix |
| B — spec completion | **Done** | Config, inverse screening, multi-step sensitivity, warning codes, CLI completion, audit bundle, docs |
| C — release gates | **Done** | Version agreement, language audit, wheel smoke (JSON/MD/HTML/PDF/plot), suite green |
| D — independent experimental validation | **Literature comparison pass only** | Digitized Allmendinger 2014 glycerol panel; report status `experimental_comparison` **pass** vs 20% median abs rel err; **not** `independently_validated` (digitization caveats) |
| E — public release | **Blocked** | Independent D incomplete; PyPI/registry credentials pending; no false publish |

Durable phase table: [docs/phase-status.md](docs/phase-status.md).

## Closed release gates (formerly open)

1. Sensitivity preserves the flow/time contract via the validated core path.
2. Malformed typed/provenance values return stable domain errors (no bool
   coercion / raw TypeError/AttributeError).
3. Backend batch rejects duplicate scenario identifiers.
4. `VALIDATION.md` is a claims-to-evidence map with
   `tests/reference_data/reference_case.json`.
5. Strict typing and the 3.10–3.13 matrix are enforced in CI.

## Phase D status (honest)

A literature comparison pass exists:

- Panel: [`validation/experimental/panel_allmendinger2014_glycerol_digitized.json`](validation/experimental/panel_allmendinger2014_glycerol_digitized.json)
- Report: [`validation/experimental/reports/allmendinger2014_digitized/`](validation/experimental/reports/allmendinger2014_digitized/)
- Ingestion notes: [`docs/pdf-ingestion-2026-08-02.md`](docs/pdf-ingestion-2026-08-02.md)
- Pipeline never advances package `validation_status` to `independently_validated`
- Registry remains `internal_validation` / `experimental_validation_pending`

Do **not** describe the package as experimentally validated. Digitized figures and
friction-subtracted glide forces are not independently traceable lab measurements.

## Next objective

1. **Phase D (remaining):** obtain independently traceable Newtonian measurements
   under [docs/validation-protocol-lock.md](docs/validation-protocol-lock.md);
   reproduce with this package version; publish a hashed validation report before
   any status advance.
2. **Phase E:** public PyPI publish waits on completed independent D **and**
   registry/signing credentials. Annotated tag `v0.1.0` may exist; that is not a
   public-index release.

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

Literature comparison (does **not** advance package validation status):

```powershell
openinjectability validate-experimental `
  validation/experimental/panel_allmendinger2014_glycerol_digitized.json `
  --out validation/experimental/reports/allmendinger2014_digitized
```
