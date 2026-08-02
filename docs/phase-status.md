# Phase status (durable)

**Updated:** 2026-08-02  
**Branch tip (at write time):** see `git log -1` on `main`  
**Package:** `0.1.0` alpha on PyPI — [pypi.org/project/openinjectability/0.1.0](https://pypi.org/project/openinjectability/0.1.0/)

| Phase | Status | Evidence |
|---|---|---|
| A — v0.1 hardening | **Complete** | Sensitivity contract, construction-time types, batch duplicates, VALIDATION claims map, mypy+CI matrix |
| B — spec completion | **Complete** | Config load, inverse screening, multi-step sensitivity, warning codes, CLI completion, audit bundle, docs |
| C — release gates | **Complete** | Version agreement, language audit, wheel smoke JSON/MD/HTML/PDF/plot, suite green |
| D — independent experimental validation | **Literature comparison pass (digitized); not independent** | Allmendinger 2014 panel (12 rows); median \|rel err\| ≈ 13.5%; report `experimental_comparison` only; package still `experimental_validation_pending` |
| E — public release | **Alpha published on PyPI** | `pip install openinjectability==0.1.0` verified; still **not** marketed as independently validated; signed/stable “validated” release waits on true D |

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

- Doc index: [`README.md`](README.md)
- Handoff: [`HANDOFF.md`](../HANDOFF.md)
- Work tracker: [`project.md`](../project.md)
- Protocol: [`validation-protocol-lock.md`](validation-protocol-lock.md)
- PyPI status: [`pypi-publish-blocker.md`](pypi-publish-blocker.md)
- Digitized literature panel report: [`../validation/experimental/reports/allmendinger2014_digitized/`](../validation/experimental/reports/allmendinger2014_digitized/)
- Public package: https://pypi.org/project/openinjectability/0.1.0/
