# Input schema (v0.1)

One CSV row is one formulation/device scenario. Required columns:

| Column | Rule |
|---|---|
| `scenario_id` | nonempty, unique |
| `formulation_id` | nonempty |
| `viscosity_value` | finite, > 0 |
| `viscosity_unit` | `cP`, `mPa_s`, or `Pa_s` |
| `viscosity_temperature_c` | finite |
| `use_temperature_c` | finite; must match measurement temperature within configured tolerance |
| `rheology_class` | must be `newtonian` |
| `newtonian_evidence` | nonempty provenance string |
| `needle_id_mm` | finite, > 0 (gauge labels never replace ID) |
| `needle_length_mm` | finite, > 0 |
| `needle_geometry_source` | nonempty provenance |
| `barrel_id_mm` | finite, > 0 |
| `barrel_geometry_source` | nonempty provenance |
| `volume_ml` | finite, > 0 |
| `injection_time_s` or `flow_rate_ml_s` | at least one; both must be consistent with volume |

Optional: `needle_gauge_label`, `density_kg_m3`, `force_ceiling_n` with
`force_ceiling_source`, `notes`, `validated_viscosity_min`,
`validated_viscosity_max`, `validated_shear_rate_min_s_1`,
`validated_shear_rate_max_s_1`, `component_pressure_rating_pa`, and
`geometry_tolerance_relative`. Evidence-range values use the corresponding declared
input unit and never trigger a silent model change.

## Run-level configuration

YAML or JSON (`--config`) may set:

- `temperature_tolerance_c`
- `time_flow_relative_tolerance`
- `sensitivity.relative_changes` (multi-step OAT list)
- `calculation_model` (must be `newtonian_hagen_poiseuille_v1`)
- `report.display_force_unit` (v0.1: `N`)
- `report.display_pressure_unit` (v0.1: `MPa`)

Effective configuration is always serialized with results.

CSV assessments retain valid rows and serialize every invalid or unsupported row under
`rejected` with row number, scenario ID, stable error code, error type, affected field,
and explanation. Exit code 2 indicates input rejection; exit code 3 indicates a
scientific-boundary rejection.

CLI: `openinjectability schema --format json` prints the machine-readable schema.

Install: `pip install openinjectability` ([PyPI](https://pypi.org/project/openinjectability/)).
