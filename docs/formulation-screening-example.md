# Formulation-screening example

This walkthrough demonstrates the OpenInjectability software workflow for a formulation
scientist. Every value in `examples/formulation_screening.csv` is **synthetic and
illustrative**. The file is not experimental evidence, does not represent a supplier
drawing, and must not be used to support a validation claim.

## Run the assessment

From a repository clone with the report dependencies installed:

```powershell
python -m pip install -e ".[dev,reports]"
openinjectability assess examples/formulation_screening.csv `
  --config examples/assessment.json `
  --results screening-results.json `
  --report screening-report.html `
  --plots-dir screening-figures `
  --audit-bundle screening-audit.zip
```

The JSON file is the machine-readable result. The HTML report shows normalized input
provenance, warnings, exclusions, and the predicted fluid-resistance force. The PNG
contains the required geometry, pressure/flow, scenario-comparison and sensitivity
plots. The self-contained HTML embeds those figures. The audit ZIP hashes the original
and normalized inputs, configuration, results, reports, figures, environment and
validation registry.

## Interpret conservatively

This example changes only the illustrative needle inner diameter while holding the other
declared inputs constant. Hagen–Poiseuille resistance scales with the inverse fourth
power of needle inner diameter, so smaller IDs produce a rapidly increasing predicted
fluid-resistance force.

The result is not total injection force. It excludes syringe friction, break-loose force,
device losses, connectors, tissue backpressure, and human factors. The package remains
`internal_validation; experimental_validation_pending`.

For real work, replace every synthetic value with traceable formulation and geometry
measurements. A gauge label is metadata only; a measured or drawing-backed needle inner
diameter is required.
