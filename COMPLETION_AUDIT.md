# OpenInjectability completion audit

**Audit date:** 2026-08-11

**Repository candidate:** 0.1.1

**Overall result:** **Not yet complete.** All locally achievable v0.1 software and
artifact requirements are implemented and verified. Independent scientific-review
approval, a qualifying experimental-validation dataset, and publication of the signed
0.1.1 release remain external evidence gates.

## Definition-of-complete ledger

| Requirement | Status | Authoritative evidence |
|---|---|---|
| Independently checked equations | **Pass internally** | Hand fixture plus standalone cross-implementation in `validation/independent_reference.py`; equation, equivalence, scaling, unit and property tests |
| Strict typed/unit/provenance validation | **Pass** | Construction, CSV schema, finite-domain, provenance, temperature, time/flow and unsupported-unit tests; stable error codes |
| Deterministic sensitivity and geometry comparison | **Pass** | Same-core perturbation tests; pressure and force changes plus analytical elasticities; complete plot set |
| Structured single/batch results and rejections | **Pass** | Versioned JSON, provenance, diagnostic null reasons, accepted results and explicit row-numbered rejected records |
| Python/CLI and JSON/Markdown/HTML/PDF | **Pass locally** | Public API tests, CLI tests, self-contained HTML, rendered 10-page PDF and installed-wheel smoke |
| Conservative feasibility warnings | **Pass** | Stable code, severity, field, explanation and remediation; no default force ceiling or device-performance claim |
| Reproducible quality/release gates | **Pass locally** | Python 3.10-3.13 CI definition, Ruff, format, strict mypy, coverage, build, Twine and installed-wheel artifact smoke |
| Independent experimental-validation record | **Blocked on evidence** | No qualifying independent dataset exists in the repository; digitized Allmendinger comparison remains `experimental_comparison` only |

## Specification closure

The 0.1.1 candidate now includes all four required plot classes, report metadata and
equations, original and canonical inputs, diagnostics, sensitivity, warnings,
rejections, exclusions, references and reproduction commands. Audit bundles include
the original and normalized inputs, effective configuration, authoritative results,
Markdown/HTML reports, figures, environment metadata, validation registry and a
SHA-256 manifest that names its algorithm.

Property-based tests cover positive finite outputs, JSON finiteness, inner-diameter
monotonicity and time/flow round trips. The standalone reference implementation imports
no package code. PDF pages were rendered with PyMuPDF because Poppler was unavailable;
all ten pages were visually inspected for clipping, overlap, illegible glyphs and plot
readability.

## Remaining external gates

1. Obtain recorded scientific-review approval of the equations, exclusions, terminology,
   schemas and locked validation protocol.
2. Obtain independently traceable Newtonian rows meeting every required field in
   `docs/validation-protocol-lock.md`; keep development and validation data separate.
3. Run the locked comparison without hidden correction factors, investigate discrepancies,
   and publish the permitted fixtures and hashed validation report.
4. Advance validation vocabulary only to the level supported by that report.
5. Register the PyPI Trusted Publisher (the protected GitHub `pypi` environment is
   configured), merge the green pull request, publish signed/tagged release `v0.1.1`,
   and verify a fresh public-index install.

Until all five gates have direct evidence, the project and active goal must remain open.
