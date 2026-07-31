# Validation status

**Current status:** `internal_validation` with
`experimental_validation_pending`
**Version:** 0.1.0
**Updated:** 2026-07-31

The implementation is checked using:

- independent hand-calculated reference values;
- equivalence of the pressure-area and simplified force equations;
- SI and common-unit conversion tests;
- analytical scaling properties;
- fail-closed rheology, geometry, temperature, and provenance tests;
- CLI and report smoke tests.

These checks verify implementation behavior. They do not demonstrate agreement with an
independent experimental injection-force dataset. The software must therefore not be
described as an experimentally validated device model.

The prediction covers only idealized needle-fluid resistance for Newtonian liquids. It
does not include syringe friction, break-loose force, device drivetrain losses, tissue
backpressure, or human capability.
