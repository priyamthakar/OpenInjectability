# Changelog

## 0.1.0 — 2026-08-01

### Added

- Newtonian predicted fluid-resistance force assessment (Hagen–Poiseuille).
- `OpenInjectabilityEngine` side-effect-free backend façade with batch rejections.
- CLI: `assess`, `assess-one`, `compare-geometries`, `validate-input`,
  `validation-status`, `schema`, `version`.
- Markdown, HTML, and PDF reports; geometry comparison plots.
- Deterministic `--audit-bundle` ZIP with `manifest.sha256`.
- Run-level YAML/JSON configuration and multi-step sensitivity.
- Inverse screening quantities from provenance-backed force ceilings.
- Construction-time runtime type validation and claims-to-evidence `VALIDATION.md`.
- CI matrix for Python 3.10–3.13 with pytest, ruff, mypy, build, and wheel smoke.

### Scientific boundary

- Results are named **predicted fluid-resistance force** only.
- Non-Newtonian inputs fail closed.
- Independent experimental validation remains pending.
