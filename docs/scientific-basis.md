# Scientific basis (v0.1)

OpenInjectability v0.1 implements an idealized laminar capillary-flow model for
**Newtonian** liquids delivered through a circular needle.

## Governing relations

Flow rate from volume and time:

\[ Q = V / t \]

Needle pressure drop (Hagen–Poiseuille):

\[ \Delta P_n = 128 \mu L Q / (\pi d^4) \]

Predicted fluid-resistance force at the plunger from needle pressure only:

\[ F_f = \Delta P_n A_b = 32 \mu L Q D_b^2 / d^4 \]

where \(A_b = \pi D_b^2 / 4\).

Apparent wall shear rate:

\[ \dot{\gamma}_w = 32 Q / (\pi d^3) \]

Optional Reynolds number when density is supplied:

\[ \mathrm{Re} = \rho v d / \mu,\quad v = 4Q/(\pi d^2) \]

## Result naming

The calculated force is always **predicted fluid-resistance force**. It is not
total injection force, device force, or a statement of human capability.

## Exclusions

The model excludes syringe friction and break-loose force; device drivetrain
losses; connectors and minor losses; tissue backpressure; and human factors.

## Inverse screening quantities

When the user supplies a provenance-backed force ceiling, the package may report
model-derived \(Q_{\max}\) and \(t_{\min}\). These are screening quantities only;
no default ceiling is shipped.

## Validation

See [VALIDATION.md](../VALIDATION.md). Independent experimental validation remains
pending.
