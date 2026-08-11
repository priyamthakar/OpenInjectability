# Interpreting results

## What the number means

`fluid_resistance_force_n` is the **predicted fluid-resistance force** attributable
only to idealized Newtonian needle pressure drop acting over the barrel area.

## What it does not mean

It is **not**:

- total injection force;
- a safe / unsafe product claim;
- a compliance determination;
- evidence that a person can administer an injection;
- a substitute for experimental glide-force testing.

## Warnings

Warnings never silently change the equation. Codes include missing density
(laminarity not numerically verified), force ceiling exceeded, shear rate outside
evidence range, viscosity outside a declared evidence range, missing geometry tolerance,
component rating exceedance, geometry metadata inconsistency, and inverse-screening
quantity labels. Every warning includes a field and remediation.

## Sensitivity

One-at-a-time relative perturbations rerun the validated scientific core. Companion
flow/time fields are nulled so volume–time–flow consistency is preserved.
Analytical elasticities: viscosity +1, length +1, barrel ID +2, needle ID −4,
time −1 (fixed volume), flow +1.

Each sensitivity record contains the recalculated pressure and force, their relative
changes, and the analytical force elasticity. These deterministic perturbations are not
probabilistic confidence or uncertainty intervals.

## Reports and audit bundles

`--plots-dir` generates force-versus-geometry, pressure-versus-flow, warning-aware
scenario comparison, and per-scenario tornado plots. HTML embeds the figures. PDF uses
the same report model and includes the figures. The audit ZIP contains original and
normalized inputs, configuration, results, reports, figures, environment and validation
metadata, plus a declared SHA-256 manifest.

## Validation status

Until an independent experimental validation report is published, treat results as
internally verified model outputs with `experimental_validation_pending`.

A literature `experimental_comparison` (e.g. Allmendinger 2014 glycerol panel via
`validate-experimental`) may support engineering confidence but is **not**
independent lab validation and does not change package status.

Install from PyPI: `pip install openinjectability` — still alpha.
