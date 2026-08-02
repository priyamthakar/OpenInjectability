# OpenInjectability

OpenInjectability is a transparent Python toolkit for estimating the pressure drop and
**predicted fluid-resistance force** for a declared Newtonian liquid flowing through a
specified needle.

## Scientific boundary

The model is intentionally narrow:

- **In scope:** idealized Hagen–Poiseuille needle-fluid resistance for **Newtonian**
  liquids with traceable viscosity, needle ID/length, barrel ID, volume, and rate.
- **Out of scope:** syringe friction, break-loose force, device drivetrain losses,
  tissue backpressure, human factors, and non-Newtonian rheology.
- A needle **gauge** label is metadata only; a **traceable needle inner diameter** is
  required.
- The result is always named **predicted fluid-resistance force**, never total device
  force, “safe,” or “compliant.”

Non-Newtonian or otherwise unsupported inputs **fail closed** (typed rejection; no
fallback rheology model).

## Quick start

```powershell
python -m pip install -e ".[dev,reports]"
openinjectability assess examples/formulation.csv `
  --config examples/assessment.json `
  --results assessment.json `
  --report assessment.md `
  --plot force-vs-needle.png `
  --audit-bundle audit.zip
```

PDF and plot output require the `reports` extra. Markdown and HTML reports require no
optional dependency beyond the core install.

```powershell
openinjectability version
openinjectability schema --format json
openinjectability validate-input examples/formulation.csv
openinjectability validation-status --json
openinjectability assess-one --viscosity-value 35 --viscosity-temperature 25 `
  --use-temperature 25 --rheology-evidence RHEO-1 --needle-id 0.21 `
  --needle-length 12.7 --needle-source drawing --barrel-id 6.35 `
  --barrel-source syringe --volume 2 --injection-time 15
```

### Literature / experimental panel comparison

Compare a panel JSON of measured fluid-side force (or pressure × barrel area) to the
model. Report status is only `experimental_comparison` or `insufficient_data` — this
command **never** claims `independently_validated` and does **not** advance package
`validation_status`.

```powershell
openinjectability validate-experimental `
  validation/experimental/panel_allmendinger2014_glycerol_digitized.json `
  --out validation/experimental/reports/allmendinger2014_digitized
```

Panel schema and rules: [validation/experimental/README.md](validation/experimental/README.md).

Documentation: [docs/scientific-basis.md](docs/scientific-basis.md),
[docs/input-schema.md](docs/input-schema.md),
[docs/interpretation.md](docs/interpretation.md),
[docs/roadmap.md](docs/roadmap.md), [docs/phase-status.md](docs/phase-status.md),
[VALIDATION.md](VALIDATION.md),
[PROJECT_SPECIFICATION.md](PROJECT_SPECIFICATION.md), [project.md](project.md).

## Backend engine API

For services, notebooks, or another application backend, use the in-memory engine. It
does not read files, produce plots or reports, or invoke the CLI. It preserves the same
Newtonian-only scientific boundary as the command line.

```python
from openinjectability import AssessmentInput, OpenInjectabilityEngine

engine = OpenInjectabilityEngine()
result = engine.assess(case)  # `case` is a validated AssessmentInput
batch = engine.assess_batch([case_a, case_b])
metadata = engine.metadata.to_dict()
```

`assess_batch` preserves accepted input order and records each invalid or unsupported
case as a typed `RejectedAssessment`; it never applies a fallback rheology model. The
returned value remains the predicted fluid-resistance force, not total device force.

## Status

**Version 0.1.0 is alpha.** Development status on PyPI classifiers is `3 - Alpha`.

| Area | State |
|---|---|
| Phases A–C (hardening, spec completion, release gates) | Complete |
| Equations / internal reference cases | `internal_validation` (unit-tested) |
| Independent experimental validation | **Pending** — package `experimental_validation_pending` |
| Literature comparison (Allmendinger 2014 digitized panel) | Report status `experimental_comparison` only; **not** `independently_validated` |
| Public PyPI release (Phase E) | Blocked on independent D + credentials |

- Do **not** describe this release as experimentally validated.
- Digitized figures, geometry setups from papers, or exploratory literature comparisons
  under `validation/experimental/` are **not** accepted independent experimental
  validation evidence.
- See [VALIDATION.md](VALIDATION.md) for the claims-to-evidence map and status
  vocabulary, and [docs/phase-status.md](docs/phase-status.md) for phase tracking.
