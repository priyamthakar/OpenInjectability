# OpenInjectability final product goal

## Final goal

OpenInjectability will be a validated, transparent decision-support toolkit for
predicting the **fluid-resistance component of injection force** for declared
Newtonian injectable formulations and syringe/needle geometries.

It will let formulation and device-development scientists screen how viscosity,
needle inner diameter and length, syringe barrel diameter, injection volume, and
flow rate or injection time influence pressure drop and predicted
fluid-resistance force. Every result must remain traceable to declared inputs,
published equations, versioned software, and explicit scientific assumptions.

## Scientific boundary

The supported result is **predicted fluid-resistance force**, not total device
force. OpenInjectability must not infer or claim:

- syringe friction or break-loose force;
- device, connector, tissue, or backpressure losses;
- usability, pain, human-factor, or administration-success outcomes;
- non-Newtonian behaviour from Newtonian equations; or
- experimental validation that has not been completed.

Non-Newtonian inputs must fail closed. Shear-thinning or other rheology models
may be added only after their implementation and applicability have independent
experimental validation.

## Definition of complete

The final product is complete when it provides:

1. independently verified pressure-drop and fluid-resistance calculations;
2. strict, typed, finite, unit-aware and provenance-aware input validation;
3. deterministic sensitivity and needle-geometry comparisons that rerun the
   same validated scientific core;
4. structured single-case and batch results with stable error codes;
5. CLI and Python APIs plus JSON, Markdown, HTML and PDF reporting;
6. conservative feasibility warnings that do not become device-performance
   claims;
7. reproducible builds, installed-wheel tests, static typing, coverage and the
   supported Python-version CI matrix; and
8. an independent experimental-validation record before any validated-device
   or predictive-accuracy claim.

## Immediate evidence-gated objective

**v0.1.0 alpha is complete and published** on
[PyPI](https://pypi.org/project/openinjectability/0.1.0/): hardening, spec
completion, release gates, literature comparison pipeline, and public install
path.

**Next evidence-gated objective:** obtain independently traceable Newtonian
experimental rows (author SI tables or wet-lab friction-subtracted force) under
[docs/validation-protocol-lock.md](docs/validation-protocol-lock.md), re-run
`validate-experimental`, and only then consider advancing package
`validation_status` beyond `experimental_validation_pending`.

See [HANDOFF.md](HANDOFF.md) for the current engineering checkpoint and
[VALIDATION.md](VALIDATION.md) for the present evidence boundary.
