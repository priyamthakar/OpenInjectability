# OpenInjectability

OpenInjectability is a transparent Python toolkit for estimating the pressure drop and
**predicted fluid-resistance force** for a declared Newtonian liquid flowing through a
specified needle.

The model is intentionally narrow. It excludes syringe friction, break-loose force,
device losses, tissue backpressure, human factors, and non-Newtonian rheology. A needle
gauge label is metadata only; a traceable needle inner diameter is required.

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

Documentation: [docs/scientific-basis.md](docs/scientific-basis.md),
[docs/input-schema.md](docs/input-schema.md),
[docs/interpretation.md](docs/interpretation.md),
[docs/roadmap.md](docs/roadmap.md), [VALIDATION.md](VALIDATION.md),
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

Version 0.1.0 is an alpha implementation. Its equations and internal reference cases
are tested; independent experimental validation is pending.
