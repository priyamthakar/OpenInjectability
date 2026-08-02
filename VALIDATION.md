# Validation status

**Current status:** `internal_validation` with
`experimental_validation_pending`
**Version:** 0.1.0
**Updated:** 2026-08-02

These checks verify implementation behavior. They do not demonstrate agreement with an
independent experimental injection-force dataset. The software must therefore not be
described as an experimentally validated device model.

A **literature comparison** panel (digitized Allmendinger 2014 glycerol forces) can be
reproduced with `openinjectability validate-experimental` and yields report status
`experimental_comparison` only. That pipeline **never** sets package status to
`independently_validated`. Digitized figures are not independently traceable lab data.

The prediction covers only idealized needle-fluid resistance for Newtonian liquids. It
does not include syringe friction, break-loose force, device drivetrain losses, tissue
backpressure, or human capability.

## Claims-to-evidence map

| Claim | Evidence fixture / artifact | Test(s) |
|---|---|---|
| Independent hand-calculated reference values | [`tests/reference_data/reference_case.json`](tests/reference_data/reference_case.json) | `tests/test_core.py::test_hand_calculated_reference_fixture_matches_engine` |
| Equivalence of pressure-area and simplified force equations \(F = 32\mu L Q D_b^2 / d^4\) | same reference inputs; analytic expression in test | `tests/test_core.py::test_simplified_force_equation_matches_pressure_area_path`, `tests/test_core.py::test_reference_equation_matches_independent_expression` |
| SI and common-unit conversion (cP, mPa·s, Pa·s) | unit variants of the reference geometry | `tests/test_core.py::test_centipoise_and_pascal_second_are_equivalent`, `tests/test_core.py::test_mpa_s_equivalent_to_centipoise` |
| Analytical scaling properties (µ, L, \(D_b\), \(d\), \(t\)) | scaled inputs vs baseline | `tests/test_core.py::test_analytical_scaling` |
| Sensitivity elasticities match analytical log-derivatives; flow/time companion nulling | assessed sensitivity list | `tests/test_core.py::test_sensitivity_matches_analytical_elasticities`, `tests/test_core.py::test_sensitivity_nulls_companion_when_both_time_and_flow_supplied`, `tests/test_core.py::test_sensitivity_supports_flow_rate_driven_inputs` |
| Fail-closed rheology | non-Newtonian `rheology_class` values | `tests/test_core.py::test_non_newtonian_inputs_fail_closed` |
| Fail-closed temperature policy | mismatched use temperature | `tests/test_core.py::test_temperature_extrapolation_fails_closed` |
| Fail-closed typed/provenance construction errors | bool/string/NaN/wrong-type fields | `tests/test_core.py::test_construction_rejects_malformed_types`, `tests/test_core.py::test_bool_viscosity_does_not_coerce_silently` |
| Density-absent laminarity warning | `density_kg_m3=None` | `tests/test_core.py::test_missing_density_returns_explicit_warning_and_null_reynolds` |
| CLI and report smoke tests | `examples/formulation.csv` | `tests/test_cli.py::test_cli_generates_json_and_html`, `tests/test_cli.py::test_optional_pdf_and_plot_outputs`, `tests/test_cli.py::test_validation_status_is_conservative` |
| Side-effect-free backend engine single-case, batch-order, explicit rejection | in-memory `OpenInjectabilityEngine` | `tests/test_engine.py` (all tests, including duplicate `scenario_id` rejection) |
| Literature glycerol panel (digitized Allmendinger 2014 Fig. 3A − Table 1 friction; figure-reading caveats; not author SI) | [`validation/experimental/panel_allmendinger2014_glycerol_digitized.json`](validation/experimental/panel_allmendinger2014_glycerol_digitized.json); report [`validation/experimental/reports/allmendinger2014_digitized/`](validation/experimental/reports/allmendinger2014_digitized/); notes [`docs/pdf-ingestion-2026-08-02.md`](docs/pdf-ingestion-2026-08-02.md) | `tests/test_validation_report.py::test_allmendinger2014_digitized_panel_literature_comparison` (n≥10, median \|rel err\| < 0.20, status `experimental_comparison` only; package status remains `experimental_validation_pending`) |

## Status vocabulary

- `equation_verified` / internal algebraic checks: covered by the reference and scaling rows above.
- `internal_validation`: the claims map in this document.
- `experimental_validation_pending`: no independent experimental injection-force dataset has been accepted yet. A digitized literature comparison may exist as `experimental_comparison` without clearing this flag.
- `experimental_comparison` (report-only from `validate-experimental`): at least one comparable panel row was evaluated; **not** a package `validation_status` value.
- `independently_validated`: reserved; never set without a published, versioned validation report with content hashes.
