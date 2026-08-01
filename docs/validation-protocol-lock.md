# Validation protocol lock (Phase D pre-requisite)

**Status:** protocol draft locked for future experimental work; **no experimental
dataset has been accepted yet**.

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
