# Roadmap

## Prepared (v0.1.1 maintenance candidate)

- Centralized package version and version-agreement regression test
- Provenance-rich human-readable reports with unchanged JSON schema
- Synthetic formulation-scientist screening walkthrough
- Repository-wide lint and format enforcement
- GitHub OIDC Trusted Publishing workflow with no local token uploader
- Publication pending PyPI Trusted Publisher and protected environment setup

## Completed (v0.1.0 alpha)

- Newtonian Hagen–Poiseuille core with fail-closed boundaries
- Engine façade, CLI, reports, plots, audit bundle
- Sensitivity, inverse screening quantities, warning codes
- Internal validation evidence map
- `validate-experimental` panel comparison pipeline (never claims independent validation)
- Literature comparison: digitized Allmendinger 2014 glycerol panel
  (`experimental_comparison` only)
- **PyPI alpha:** https://pypi.org/project/openinjectability/0.1.0/

## Still open (scientific)

- Independently traceable lab Newtonian measurements (or author SI tables) under
  [validation-protocol-lock.md](validation-protocol-lock.md)
- Advancing package `validation_status` to `independently_validated`
- Signed “validated” release marketing (not the current alpha)

## Deferred until independent validation of those models

- Non-Newtonian rheology models
- Friction / break-loose / device drivetrain terms
- Tissue backpressure and depot formation
- Probabilistic uncertainty stacks
- Web application hosting

## Next scientific milestone

Obtain author SI or wet-lab friction-subtracted Newtonian rows (not figure
digitization alone), re-run `validate-experimental`, publish a hashed report,
and only then advance `validation_status`. See [phase-status.md](phase-status.md).
