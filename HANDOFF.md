# OpenInjectability handoff

**Snapshot date:** 2026-08-02  
**Package version:** `0.1.0`  
**Lifecycle state:** alpha on PyPI; experimental validation still pending  
**PyPI:** https://pypi.org/project/openinjectability/0.1.0/

## Product destination

See [PROJECT_GOAL.md](PROJECT_GOAL.md). Result is always **predicted fluid-resistance force**, never total device force.

## Phase status

| Phase | Status |
|---|---|
| A — v0.1 hardening | **Done** |
| B — spec completion | **Done** |
| C — release gates | **Done** |
| D — independent experimental validation | **Literature `experimental_comparison` only** (digitized Allmendinger 2014); **not** independently validated |
| E — public alpha release | **Done on PyPI** (`0.1.0`); full “validated” release still blocked on true D |

Durable table: [docs/phase-status.md](docs/phase-status.md).

## Install (public)

```powershell
python -m pip install openinjectability==0.1.0
openinjectability --version
openinjectability assess examples/formulation.csv --results out.json --report out.md
```

Repo developers:

```powershell
python -m pip install -e ".[dev,reports]"
python -m pytest --cov=openinjectability --cov-branch --cov-fail-under=87
```

## Phase D artifacts

- Panel: `validation/experimental/panel_allmendinger2014_glycerol_digitized.json`
- Report: `validation/experimental/reports/allmendinger2014_digitized/`
- Notes: `docs/pdf-ingestion-2026-08-02.md`
- Package `validation_status` remains `internal_validation; experimental_validation_pending`

## Next objectives (honest)

1. **Optional stronger D:** author SI tables or wet-lab friction-subtracted Newtonian rows → re-run `validate-experimental`; only then consider advancing validation vocabulary.
2. **Ops:** revoke PyPI token if it was exposed in chat; create a new entire-account token in `~\.pypirc`.
3. **Product:** use/monitor PyPI installs; patch releases as needed without overclaiming validation.

## Scientific boundary

Never label results as total injection force, safe, or compliant. Non-Newtonian inputs fail closed.
