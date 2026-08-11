# Changelog

## 0.1.1 — Unreleased

### Changed

- Centralized the package version and added a packaging/registry agreement test.
- Added normalized input provenance, package version, validation status, warnings, and
  exclusions consistently to human-readable reports.
- Added a synthetic multi-geometry formulation-screening tutorial and acceptance test.
- Completed the four-plot specification surface and embedded plots in HTML/PDF reports.
- Added stable error codes, row-level CSV rejections, explicit provenance and diagnostic
  null reasons to structured results.
- Expanded audit bundles with original/normalized inputs, reports, figures, environment,
  validation registry and a declared SHA-256 manifest.
- Added property-based tests and a standalone equation cross-implementation.
- Expanded CI to enforce repository-wide Ruff linting and formatting.
- Replaced token-based local publication with a GitHub OIDC Trusted Publishing workflow.
- Added repository, issue tracker, changelog, and homepage package metadata.

### Scientific boundary

- Calculation equations and result schema remain unchanged.
- Package status remains `internal_validation; experimental_validation_pending`.
- The new screening example is synthetic software-demonstration data, not validation
  evidence.

## 0.1.0 — 2026-08-02

### Added

- Newtonian predicted fluid-resistance force assessment (Hagen–Poiseuille).
- `OpenInjectabilityEngine` side-effect-free backend façade with batch rejections.
- CLI: `assess`, `assess-one`, `compare-geometries`, `validate-input`,
  `validate-experimental`, `validation-status`, `schema`, `version`.
- Markdown, HTML, and PDF reports; geometry comparison plots.
- Deterministic `--audit-bundle` ZIP with `manifest.sha256`.
- Run-level YAML/JSON configuration and multi-step sensitivity.
- Inverse screening quantities from provenance-backed force ceilings.
- Construction-time runtime type validation and claims-to-evidence `VALIDATION.md`.
- Experimental panel comparison pipeline (`validate-experimental`) with hashed reports;
  report status is never `independently_validated`.
- Literature glycerol comparison panel (Allmendinger 2014, figure-digitized with caveats).
- CI matrix for Python 3.10–3.13 with pytest, ruff, mypy, build, and wheel smoke.

### Published

- **PyPI:** https://pypi.org/project/openinjectability/0.1.0/  
  `python -m pip install openinjectability`

### Scientific boundary

- Results are named **predicted fluid-resistance force** only.
- Non-Newtonian inputs fail closed.
- Package status remains `experimental_validation_pending`; literature
  `experimental_comparison` does not imply independent validation.
