# Phase status (durable)

**Updated:** 2026-08-02  
**Branch tip (at write time):** see `git log -1` on `main`  
**Package:** `0.1.0` alpha — internal verification only

| Phase | Status | Evidence |
|---|---|---|
| A — v0.1 hardening | **Complete** | Sensitivity contract, construction-time types, batch duplicates, VALIDATION claims map, mypy+CI matrix |
| B — spec completion | **Complete** | Config load, inverse screening, multi-step sensitivity, warning codes, CLI completion, audit bundle, docs |
| C — release gates | **Complete** | Version agreement, language audit, wheel smoke JSON/MD/HTML/PDF/plot, suite green |
| D — independent experimental validation | **Literature comparison pass (digitized); not independent** | Allmendinger 2014 PDFs ingested; Table 1 exact + Fig. 3(A) digitized glycerol panel (12 rows); median \|rel err\| ≈ 13.5% → report status `experimental_comparison` **pass** vs 20% criterion; package `validation_status` **not** advanced; **not** `independently_validated` (digitization + friction-subtraction caveats); see `docs/pdf-ingestion-2026-08-02.md` |
| E — public release | **Blocked** | Requires completed independent D + registry/signing / PyPI credentials; no false PyPI publish (see [`pypi-publish-blocker.md`](pypi-publish-blocker.md) if present) |

## What must not happen while blocked

- Do not invent experimental data.
- Do not set `validation_status` to `independently_validated`.
- Do not claim predictive accuracy or total device force.
- Do not ship a default human/device force ceiling.
- Do not treat a literature `experimental_comparison` pass as independent validation.

## Unblock checklist

1. Confirm and freeze acceptance criteria in the protocol **before** unblinding data.
2. Obtain independently traceable Newtonian measurements (viscosity, geometry, force/pressure).
3. Reproduce with this package version; publish hashed validation report.
4. Only then advance validation status and prepare a signed public release (credentials required).

## Related artifacts

- Handoff: [`HANDOFF.md`](../HANDOFF.md)
- Work tracker: [`project.md`](../project.md)
- Protocol: [`validation-protocol-lock.md`](validation-protocol-lock.md)
- Digitized literature panel report: [`../validation/experimental/reports/allmendinger2014_digitized/`](../validation/experimental/reports/allmendinger2014_digitized/)
