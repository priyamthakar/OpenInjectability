# Validation protocol lock (Phase D pre-requisite)

**Status:** protocol draft locked for future experimental work; **no experimental
dataset has been accepted yet**.

**2026-08-02 update:** a public literature scrape was attempted (see
[literature-scrape-assessment.md](literature-scrape-assessment.md)). No open
dataset met the fluid-resistance-only measurand bar; scrape alone does **not**
unlock independent validation.

**2026-08-02 later:** Allmendinger 2014 PDFs were ingested; a **digitized**
glycerol panel supports report-only `experimental_comparison` (see
[pdf-ingestion-2026-08-02.md](pdf-ingestion-2026-08-02.md)). Package
`validation_status` is still pending. Alpha **0.1.0** is on
[PyPI](https://pypi.org/project/openinjectability/0.1.0/).

## Scope

Compare **predicted fluid-resistance force** from OpenInjectability v0.1
(`newtonian_hagen_poiseuille_v1`) against independently measured needle fluid
resistance (or needle pressure drop converted via measured barrel area) for
**Newtonian** liquids only.

## Pre-data rules

1. Acceptance criteria and metrics are fixed **before** any validation dataset is
   analyzed with this package version.
2. Development/reference fixtures in `tests/reference_data/` must not be reused as
   the independent experimental set.
3. No hidden correction factors, gauge-to-ID imputation, or non-Newtonian “effective
   viscosity” substitutions.

## Required measured inputs (each run)

- Dynamic viscosity with temperature and Newtonian evidence
- Traceable needle ID and length with geometry source
- Barrel ID with geometry source
- Delivered volume and flow rate or injection time
- Measured fluid-side force or pressure (method documented)
- Density if Reynolds diagnostics are compared

## Comparison metrics (predefined)

- Relative error on force: \((F_{\mathrm{model}} - F_{\mathrm{exp}})/F_{\mathrm{exp}}\)
- Relative error on pressure when pressure is the primary measurement
- Residual plots vs flow rate and vs \(1/d^4\)

## Acceptance criteria (draft; confirm before unblinding data)

- For the locked Newtonian panel, median absolute relative force error ≤ 20%
  **or** a study-specific criterion published with the protocol revision
- No claim of independent validation until a versioned report with content hashes
  is published and `validation_status` is updated in a release that cites that report

## Status advancement

`validation_status` must remain
`internal_validation; experimental_validation_pending` until the published report
exists. Never set `independently_validated` without that record.

## Comparison pipeline (infrastructure; no dataset accepted)

Panel schema, empty template, and how-to for real lab rows live under
[`validation/experimental/`](../validation/experimental/README.md).

Run a comparison **without** advancing package status:

```bash
openinjectability validate-experimental path/to/panel.json --out path/to/report_dir
```

Outputs: `experimental_comparison.json`, `experimental_comparison.md`, and
`manifest.sha256` (input + output digests). Report status is only
`experimental_comparison` or `insufficient_data` — never `independently_validated`.
Do not use `tests/reference_data/` as an experimental panel.
