# OpenInjectability

OpenInjectability is a transparent Python toolkit for estimating the pressure drop and
**predicted fluid-resistance force** for a declared Newtonian liquid flowing through a
specified needle.

The model is intentionally narrow. It excludes syringe friction, break-loose force,
device losses, tissue backpressure, human factors, and non-Newtonian rheology. A needle
gauge label is metadata only; a traceable needle inner diameter is required.

## Quick start

```powershell
python -m pip install -e .
openinjectability assess examples/formulation.csv `
  --results assessment.json `
  --report assessment.pdf `
  --plot force-vs-needle.png
```

PDF and plot output require `python -m pip install -e ".[reports]"`. Markdown and
HTML reports require no optional dependency.

Validate without calculating:

```powershell
openinjectability validate-input examples/formulation.csv
```

Inspect validation status:

```powershell
openinjectability validation-status --json
```

See [PROJECT_SPECIFICATION.md](PROJECT_SPECIFICATION.md) for the scientific basis,
schemas, roadmap, references, and release gates. See [VALIDATION.md](VALIDATION.md) for
the current evidence level.

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
