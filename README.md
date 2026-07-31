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

## Status

Version 0.1.0 is an alpha implementation. Its equations and internal reference cases
are tested; independent experimental validation is pending.
