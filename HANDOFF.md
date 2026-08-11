# OpenInjectability handoff

**Snapshot date:** 2026-08-11

**Repository version:** `0.1.1` release candidate

**Public version:** `0.1.0` alpha on PyPI

**Lifecycle state:** 0.1.1 prepared locally; experimental validation still pending

**PyPI:** https://pypi.org/project/openinjectability/

## Product destination

See [PROJECT_GOAL.md](PROJECT_GOAL.md). Result is always **predicted fluid-resistance force**, never total device force.

## Phase status

| Phase | Status |
|---|---|
| A — v0.1 hardening | **Done** |
| B — spec completion | **Done** |
| C — release gates | **Done locally for 0.1.1** (73 tests; 90.05% branch coverage; Ruff, format, mypy, build, Twine, installed-wheel smoke, rendered PDF review) |
| D — independent experimental validation | **Literature `experimental_comparison` only** (digitized Allmendinger 2014); **not** independently validated |
| E — public alpha release | **0.1.0 on PyPI**; 0.1.1 publication awaits Trusted Publisher setup and GitHub release |

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

## 0.1.1 maintenance candidate

- Single package-version source with agreement tests
- Provenance-rich Markdown, HTML, and PDF reports
- Synthetic formulation-scientist screening walkthrough
- Repository-wide Ruff lint and format gates
- GitHub OIDC Trusted Publishing workflow; local token upload removed
- Complete reports, four required plot classes, row-level rejections and full audit bundle
- Property-based tests and standalone arithmetic cross-implementation

Requirement-level status: [COMPLETION_AUDIT.md](COMPLETION_AUDIT.md).

## Next objectives (honest)

1. **Optional stronger D:** author SI tables or wet-lab friction-subtracted Newtonian rows → re-run `validate-experimental`; only then consider advancing validation vocabulary.
2. **Release:** configure the PyPI Trusted Publisher and protected GitHub `pypi`
   environment, then publish GitHub release `v0.1.1`; all local gates pass.
3. **Security:** revoke the former PyPI API token; 0.1.1 publishing does not use
   `~\.pypirc` or token environment variables.
4. **Product:** use/monitor PyPI installs and collect formulation-scientist feedback
   without overclaiming validation.

## Scientific boundary

Never label results as total injection force, safe, or compliant. Non-Newtonian inputs fail closed.
