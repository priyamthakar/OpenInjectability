# Phase status (durable)

**Updated:** 2026-08-02  
**Branch tip (at write time):** see `git log -1` on `main`  
**Package:** `0.1.0` alpha — internal verification only

| Phase | Status | Evidence |
|---|---|---|
| A — v0.1 hardening | **Complete** | Sensitivity contract, construction-time types, batch duplicates, VALIDATION claims map, mypy+CI matrix |
| B — spec completion | **Complete** | Config load, inverse screening, multi-step sensitivity, warning codes, CLI completion, audit bundle, docs |
| C — release gates | **Complete** | Version agreement, language audit, wheel smoke JSON/MD/HTML/PDF/plot, suite green |
| D — independent experimental validation | **Blocked after multi-agent PubMed scrape** | Four agents (EuropePMC, full-text tables, Zenodo/Figshare, PubMed eutils): **0** Phase-D rows; consensus in [multi-agent-pubmed-consensus.md](multi-agent-pubmed-consensus.md); `validation_status` unchanged |
| E — public release | **Blocked** | Requires completed D + registry/signing credentials; no false PyPI publish |

## What must not happen while blocked

- Do not invent experimental data.
- Do not set `validation_status` to `independently_validated`.
- Do not claim predictive accuracy or total device force.
- Do not ship a default human/device force ceiling.

## Unblock checklist

1. Confirm and freeze acceptance criteria in the protocol **before** unblinding data.
2. Obtain independently traceable Newtonian measurements (viscosity, geometry, force/pressure).
3. Reproduce with this package version; publish hashed validation report.
4. Only then advance validation status and prepare a signed public release.
