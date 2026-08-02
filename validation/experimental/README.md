# Experimental validation panel (Phase D pipeline)

This directory holds **real laboratory or literature rows** for comparing OpenInjectability’s
**predicted fluid-resistance force** against independently measured fluid-side force (or
pressure converted by barrel area).

**Status of this tree:** infrastructure only. No experimental panel has been accepted.
Do **not** treat empty templates or synthetic smoke-test rows as validation evidence.

**Literature setup (geometry only):** [`literature_setup_verwulgen_2018.json`](literature_setup_verwulgen_2018.json)
quotes measured needle/barrel IDs and empty-syringe friction from the free Verwulgen
2018 author PDF. It is **not** a validation panel (no absolute fluid-only force table).

## Never use development fixtures as experimental data

| Allowed as experimental panel | Not allowed |
|---|---|
| Rows you enter under `validation/experimental/` with lab logs or literature citations | `tests/reference_data/*` (hand-calc / unit-test fixtures) |
| SHA256-manifested panel JSON + report from `validate-experimental` | Invented or “example” forces copied into a real panel |
| `force_definition` of `fluid_only` or `pressure_area` only | Glide force, break-loose, total plunger force, or unknown measurands |

Reusing `tests/reference_data` as the independent experimental set is **forbidden**. Those
files exist only to verify algebra and packaging.

## How to add real lab rows

1. Copy [`panel.template.json`](panel.template.json) to a new file, e.g.
   `panel_<lab_or_study_id>.json` (keep the template empty of measured values).
2. Fill each row according to [`schema.json`](schema.json). Every row must include:
   - Geometry with provenance (`needle_geometry_source`, `barrel_geometry_source`)
   - Viscosity with temperature and **Newtonian** evidence
   - Volume and **either** `injection_time_s` **or** `flow_rate_ml_s`
   - **Either** `measured_fluid_force_n` **or** `measured_pressure_pa`
   - `force_definition`: `fluid_only` (direct fluid-side force) or `pressure_area`
     (pressure × measured barrel area)
   - `method_notes` and `citation_or_lab_log`
3. Do **not** include rows where the instrument measures total glide / break-loose /
   syringe friction unless you have already isolated the fluid-resistance component and
   document that isolation in `method_notes`. If the measurand is total glide or
   unknown, set `force_definition` accordingly — the pipeline will **reject** the row
   rather than compare it.
4. Optional: `density_kg_m3` when Reynolds diagnostics matter.
5. Optional schema validation against `schema.json` with any JSON Schema validator.
6. Run the pipeline (does **not** advance package `validation_status`):

   ```bash
   openinjectability validate-experimental path/to/panel.json --out path/to/report_dir
   ```

7. Archive the panel JSON, report JSON, report Markdown, and `manifest.sha256` together.

## Schema fields (summary)

| Field | Required | Notes |
|---|---|---|
| `scenario_id` | yes | Unique within the panel |
| `fluid` | yes | Formulation / fluid label (used as `formulation_id` for assessment) |
| `viscosity_value` | yes | |
| `viscosity_unit` | yes | `cP`, `mPa_s`, or `Pa_s` |
| `viscosity_temperature_c` | yes | Use temperature is set equal for v0.1 (no T correction) |
| `newtonian_evidence` | yes | Citation or lab ID establishing Newtonian behavior |
| `needle_id_mm` | yes | Measured ID; not gauge-inferred without documentation |
| `needle_length_mm` | yes | |
| `needle_geometry_source` | yes | Drawing, caliper log, manufacturer cert, etc. |
| `barrel_id_mm` | yes | |
| `barrel_geometry_source` | yes | |
| `volume_ml` | yes | Delivered volume |
| `injection_time_s` | one of time/flow | |
| `flow_rate_ml_s` | one of time/flow | |
| `measured_fluid_force_n` | one of force/pressure | Fluid-side force in newtons |
| `measured_pressure_pa` | one of force/pressure | Needle / fluid pressure in pascals |
| `force_definition` | yes | Only `fluid_only` or `pressure_area` are comparable |
| `method_notes` | yes | How fluid resistance was isolated |
| `citation_or_lab_log` | yes | Traceable source |
| `density_kg_m3` | no | For Reynolds diagnostics |
| `is_synthetic_smoke_test` | no | **Tests only.** Never true in a real panel |

Full formal definition: [`schema.json`](schema.json).

## SHA256 manifest requirement

Every `validate-experimental` run writes under `--out`:

- `experimental_comparison.json` — machine-readable comparison + summary
- `experimental_comparison.md` — human-readable report
- `manifest.sha256` — SHA-256 digests of the **input panel** and the **output** artifacts

The report status is always one of:

- `insufficient_data` — no comparable rows (empty panel or all rejected)
- `experimental_comparison` — at least one comparable row was evaluated

The pipeline **never** emits `independently_validated`. Advancing package
`validation_status` requires a published, versioned report under the locked protocol
(see [`docs/validation-protocol-lock.md`](../../docs/validation-protocol-lock.md)).

## Acceptance criterion (draft, protocol-locked)

For a locked Newtonian panel, **median absolute relative force error ≤ 20%** is the draft
gate used by the report summary. Meeting that metric in a private run is **not** by itself
a claim of independent validation.

## Related

- Protocol: [`docs/validation-protocol-lock.md`](../../docs/validation-protocol-lock.md)
- Claims map: [`VALIDATION.md`](../../VALIDATION.md)
- Package status: `openinjectability validation-status`
