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
`force_ceiling_source`, `notes`.

## Run-level configuration

YAML or JSON (`--config`) may set:

- `temperature_tolerance_c`
- `time_flow_relative_tolerance`
- `sensitivity.relative_changes` (multi-step OAT list)
- `calculation_model` (must be `newtonian_hagen_poiseuille_v1`)

Effective configuration is always serialized with results.

CLI: `openinjectability schema --format json` prints the machine-readable schema.
