# Roadmap

## Completed (v0.1 Phases A–C)

- Newtonian Hagen–Poiseuille core with fail-closed boundaries
- Engine façade, CLI, reports, plots, audit bundle
- Sensitivity, inverse screening quantities, warning codes
- Internal validation evidence map
- `validate-experimental` panel comparison pipeline (never claims independent validation)

## In progress (Phase D)

- Literature comparison: digitized Allmendinger 2014 glycerol panel
  (`experimental_comparison` report; **not** `independently_validated`)
- Still required: independently traceable lab Newtonian measurements under the locked
  protocol before any package status advance

## Deferred until independent validation

- Non-Newtonian rheology models
- Friction / break-loose / device drivetrain terms
- Tissue backpressure and depot formation
- Probabilistic uncertainty stacks
- Web application hosting
- Public PyPI release (Phase E; also needs registry/signing credentials)

## Next scientific milestone

Obtain an independently traceable Newtonian dataset under
[validation-protocol-lock.md](validation-protocol-lock.md), reproduce without hidden
correction factors, publish a hashed validation report, and only then advance
`validation_status` beyond experimental-pending. See [phase-status.md](phase-status.md).
