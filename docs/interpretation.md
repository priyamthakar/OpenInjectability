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
evidence range, missing geometry tolerance, and inverse-screening quantity labels.

## Sensitivity

One-at-a-time relative perturbations rerun the validated scientific core. Companion
flow/time fields are nulled so volume–time–flow consistency is preserved.
Analytical elasticities: viscosity +1, length +1, barrel ID +2, needle ID −4,
time −1 (fixed volume), flow +1.

## Validation status

Until an independent experimental validation report is published, treat results as
internally verified model outputs with `experimental_validation_pending`.

A literature `experimental_comparison` (e.g. Allmendinger 2014 glycerol panel via
`validate-experimental`) may support engineering confidence but is **not**
independent lab validation and does not change package status.

Install from PyPI: `pip install openinjectability` — still alpha.
