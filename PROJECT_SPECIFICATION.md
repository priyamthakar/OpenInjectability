# OpenInjectability v0.1 — Project Specification

**Document status:** implementation-ready product and scientific specification
**Planned package version:** `0.1.0`
**Prepared:** 2026-07-31
**Primary audience:** formulation scientists, device-development scientists, laboratory scientists, and scientific Python contributors
**Package type:** transparent Python library with a command-line interface and reproducible reports

## 1. Executive summary

OpenInjectability is a transparent toolkit for estimating the hydrodynamic resistance encountered when a Newtonian liquid is delivered through a specified needle at a specified flow rate. It converts formulation viscosity and traceable syringe/needle geometry into:

- needle pressure drop;
- predicted fluid-resistance force at the syringe plunger;
- flow rate or injection time;
- apparent needle-wall shear rate;
- gauge/geometry comparison plots;
- deterministic sensitivity results;
- feasibility warnings; and
- machine-readable results plus Markdown, HTML, and PDF reports.

The v0.1 calculation is an idealized laminar capillary-flow calculation. It is intended for early formulation and experimental planning. It is **not** a complete injection-device model, a human-factors assessment, a clinical recommendation, or a substitute for experimental glide-force testing.

The required result name is **predicted fluid-resistance force**. The shorter phrases “injection force,” “total force,” “required user force,” and “device force” must not be used for the calculated value because they could imply inclusion of syringe friction, stopper mechanics, break-loose force, device drivetrain losses, tissue backpressure, or user capability.

## 2. Why this package should exist

High-concentration protein formulations may become difficult to deliver because viscosity, injection rate, and needle geometry influence pressure and force. Published experimental work also shows that needle dimensions and shear-dependent rheology are important to force prediction. OpenInjectability makes the deliberately narrower Newtonian calculation inspectable, unit-safe, and reproducible.

The package complements rather than duplicates the existing portfolio:

| Project | Primary responsibility | Boundary with OpenInjectability |
|---|---|---|
| [OpenPKFlow](https://github.com/priyamthakar/openpkflow) | pharmacokinetic, formulation, dissolution, and reporting workflows | does not calculate needle hydrodynamics |
| [OpenPharmaStability](https://github.com/priyamthakar/OpenPharmaStability) | pharmaceutical stability analysis | may provide viscosity observations but does not assess delivery resistance |
| [openfit](https://github.com/priyamthakar/openfit) | model fitting | may be used upstream to characterize data but is not a syringeability workflow |
| [openassay](https://github.com/priyamthakar/openassay) | assay analysis | does not model needle pressure drop |
| [BioEqPy](https://github.com/priyamthakar/BioEqPy) | formal bioequivalence statistics | has no injection-device calculation role |

OpenInjectability must remain independently usable. Integration with other packages may be added through documented adapters only; it must not import their internal APIs into the scientific core.

## 3. Intended users and decisions

### 3.1 Intended users

- formulation scientists comparing measured Newtonian viscosities;
- device scientists screening candidate needle geometries;
- laboratory teams planning benchtop extrusion or glide-force experiments;
- educators demonstrating the strong fourth-power dependence on needle inner diameter;
- reviewers auditing assumptions, units, and provenance.

### 3.2 Supported decisions

The toolkit may support questions such as:

- What idealized pressure drop follows from this viscosity, inner diameter, length, and flow rate?
- What portion of plunger force is predicted from needle fluid resistance alone?
- How does injection time change when an experimentally justified force ceiling is supplied?
- Which input contributes most to local output sensitivity?
- Which candidate geometries should be taken forward to physical testing?

### 3.3 Unsupported decisions

The toolkit must not:

- determine whether a product is safe, acceptable, approvable, or clinically usable;
- declare that a person can administer an injection;
- specify a patient-facing injection time;
- predict pain, leakage, tissue response, dose delivery, or bioavailability;
- qualify a syringe, needle, autoinjector, on-body injector, or combination product;
- infer non-Newtonian behavior from concentration or molecule type;
- estimate total device force without measured device-specific terms;
- replace design verification, usability engineering, or experimental force testing.

## 4. Scientific boundary

### 4.1 v0.1 support statement

v0.1 supports **single-phase, incompressible, time-independent Newtonian liquids** under a steady, fully developed, laminar, circular-capillary approximation. Viscosity must be a measured dynamic viscosity associated with a declared measurement temperature and a declared rheology classification.

### 4.2 Mandatory exclusions

The assessment must fail closed when any of the following is declared or detected:

- shear thinning, shear thickening, yield stress, thixotropy, or viscoelastic flow;
- suspension, emulsion, visible phase separation, or intended particulate content;
- unknown rheology classification;
- viscosity supplied without measurement temperature;
- use temperature missing or incompatible with the measurement temperature;
- missing needle inner diameter;
- a gauge label used as if it uniquely determined inner diameter;
- nonpositive, nonfinite, or dimensionally invalid data;
- mutually inconsistent injection time and flow rate beyond tolerance.

“Rejected: non-Newtonian model required” is a valid scientific result, not a software failure.

### 4.3 Terms not included in the prediction

The v0.1 prediction excludes:

- stopper-to-barrel static and dynamic friction;
- break-loose force;
- plunger-rod, spring, gearbox, motor, or autoinjector losses;
- pressure drop in connectors, tubing, barrel contraction, or noncircular paths;
- needle entrance, exit, minor, inertial, and developing-flow losses;
- tissue backpressure and depot formation;
- needle deformation, clogging, wall slip, cavitation, and compressibility;
- time-dependent viscosity or temperature rise;
- manufacturing tolerances unless explicitly represented in sensitivity inputs.

The report must show this list beside every force result.

## 5. Scientific model

### 5.1 Canonical SI variables

| Symbol | Meaning | Canonical unit |
|---|---|---|
| \(\mu\) | dynamic viscosity | Pa·s |
| \(L\) | needle effective flow length | m |
| \(d\) | measured or traceable needle inner diameter | m |
| \(D_b\) | syringe barrel inner diameter | m |
| \(Q\) | volumetric flow rate | m³/s |
| \(V\) | nominal delivered liquid volume | m³ |
| \(t\) | injection time | s |
| \(\Delta P_n\) | predicted pressure drop across the needle | Pa |
| \(A_b\) | syringe barrel cross-sectional area | m² |
| \(F_f\) | predicted fluid-resistance force | N |

The public API may accept convenient units such as cP, mm, mL, mL/min, and seconds, but all calculations must convert once to SI and serialize both canonical values and display values.

### 5.2 Flow-rate and time relationship

When volume and target time are supplied:

\[
Q = \frac{V}{t}
\]

When volume and flow rate are supplied:

\[
t = \frac{V}{Q}
\]

If time and flow rate are both supplied, the toolkit must check:

\[
\epsilon_Q = \frac{\left|Q - V/t\right|}{\max(|Q|, |V/t|)}
\]

and reject the row when \(\epsilon_Q\) exceeds a configurable tolerance whose default is recorded in the result.

### 5.3 Needle pressure drop

For the declared idealized Newtonian boundary, Hagen–Poiseuille flow gives:

\[
\Delta P_n = \frac{128 \mu LQ}{\pi d^4}
\]

The implementation must use inner diameter, not outer diameter and not gauge number. The \(d^4\) dependence means small dimensional errors can cause large force errors; the report must make this sensitivity visible.

### 5.4 Predicted fluid-resistance force

The barrel area is:

\[
A_b = \frac{\pi D_b^2}{4}
\]

The plunger force attributable only to the modeled needle pressure drop is:

\[
F_f = \Delta P_n A_b
\]

or equivalently:

\[
F_f = \frac{32 \mu LQ D_b^2}{d^4}
\]

The calculation must retain unrounded internal precision and apply rounding only in presentation.

### 5.5 Apparent wall shear rate

For Newtonian flow in a circular capillary:

\[
\dot{\gamma}_w = \frac{32Q}{\pi d^3}
\]

This value is diagnostic. It does not validate that viscosity measured at another shear condition applies at the predicted needle shear rate. The user must attest that the formulation is Newtonian over a relevant shear range; otherwise the assessment is rejected.

### 5.6 Optional laminarity diagnostic

If density \(\rho\) is supplied, mean needle velocity and Reynolds number are:

\[
v = \frac{4Q}{\pi d^2}
\]

\[
\mathrm{Re} = \frac{\rho vd}{\mu}
\]

The package may report Reynolds number as a diagnostic but must not turn a single universal Reynolds cutoff into a product-feasibility claim. If density is absent, the report states `laminarity_not_numerically_verified`. A future validation protocol must define and justify the operational warning threshold used by the software.

### 5.7 Inverse calculations

Given an **experimentally justified fluid-resistance-force ceiling** \(F_{f,\max}\), the idealized maximum flow rate is:

\[
Q_{\max} = \frac{F_{f,\max}d^4}{32\mu L D_b^2}
\]

and the corresponding minimum modeled injection time is:

\[
t_{\min} = \frac{V}{Q_{\max}}
\]

The package must label these as model-derived screening quantities. It must never provide a default human or device force ceiling. A ceiling is valid only when supplied by the user with provenance and purpose.

## 6. Input contract

### 6.1 Preferred tidy CSV schema

One row represents one formulation/device scenario.

| Column | Type | Required | Rule |
|---|---|---:|---|
| `scenario_id` | string | yes | nonempty and unique |
| `formulation_id` | string | yes | nonempty |
| `viscosity_value` | number | yes | finite and greater than zero |
| `viscosity_unit` | enum | yes | `mPa_s`, `cP`, or `Pa_s` |
| `viscosity_temperature_c` | number | yes | finite |
| `use_temperature_c` | number | yes | finite |
| `rheology_class` | enum | yes | must equal `newtonian` in v0.1 |
| `newtonian_evidence` | string | yes | dataset, report, or protocol identifier |
| `needle_id_mm` | number | yes | finite and greater than zero |
| `needle_length_mm` | number | yes | finite and greater than zero |
| `needle_gauge_label` | string | no | metadata only; never used to derive ID silently |
| `needle_geometry_source` | string | yes | drawing, certificate, measurement, or catalog reference |
| `barrel_id_mm` | number | yes | finite and greater than zero |
| `barrel_geometry_source` | string | yes | drawing, certificate, measurement, or catalog reference |
| `volume_ml` | number | yes | finite and greater than zero |
| `injection_time_s` | number | conditional | supply this or `flow_rate_ml_s` |
| `flow_rate_ml_s` | number | conditional | supply this or `injection_time_s` |
| `density_kg_m3` | number | no | enables Reynolds diagnostic |
| `force_ceiling_n` | number | no | no software default; provenance required |
| `force_ceiling_source` | string | conditional | required with `force_ceiling_n` |
| `notes` | string | no | retained verbatim in provenance |

### 6.2 Temperature policy

v0.1 performs no viscosity-temperature correction. By default, `viscosity_temperature_c` and `use_temperature_c` must agree within a documented tolerance. The default tolerance is a software configuration value, not a scientific universal, and must appear in the audit record. Outside that tolerance, the assessment fails and requests viscosity measured at the intended use temperature.

### 6.3 Needle-gauge policy

A nominal gauge label is insufficient to calculate force. A manufacturer, wall construction, and part number can correspond to a particular inner diameter, but gauge-to-ID lookup tables must be provenance-controlled.

v0.1 behavior:

1. `needle_id_mm` is mandatory for every computed scenario.
2. `needle_gauge_label` is optional reporting metadata.
3. A future bundled geometry catalog may fill `needle_id_mm` only when its record has a source, version, effective date, and validation status.
4. A user-provided catalog entry is copied into the audit bundle and hashed.
5. If geometry provenance is absent, calculation is rejected.

### 6.4 YAML/JSON configuration

CSV holds scenarios; a YAML or JSON configuration holds run-level policies:

```yaml
schema_version: "1.0"
calculation_model: "newtonian_hagen_poiseuille_v1"
temperature_tolerance_c: 0.5
time_flow_relative_tolerance: 0.001
sensitivity:
  method: "one_at_a_time"
  relative_changes: [-0.10, -0.05, 0.05, 0.10]
report:
  display_force_unit: "N"
  display_pressure_unit: "MPa"
```

Every effective configuration value must be serialized, including defaults.

## 7. Validation and fail-closed behavior

### 7.1 Hard errors

Hard errors produce no numerical assessment for the affected scenario:

- missing required column;
- duplicate or empty `scenario_id`;
- nonfinite or nonpositive physical quantity;
- unrecognized unit;
- unknown or non-Newtonian rheology;
- missing rheology evidence;
- missing inner diameter or geometry provenance;
- viscosity/use temperature mismatch;
- both time and flow rate missing;
- inconsistent time, volume, and flow rate;
- supplied force ceiling without provenance;
- input schema version newer than the installed package supports.

### 7.2 Warnings

Warnings may accompany a result but never change the equation silently:

- density absent, so Reynolds number was not calculated;
- result is extrapolated beyond a user-declared validated viscosity range;
- apparent wall shear rate lies outside the declared rheology evidence range;
- geometry tolerance was not supplied;
- calculated pressure exceeds a user-provided component rating;
- calculated predicted fluid-resistance force exceeds a user-provided ceiling;
- gauge label and source geometry metadata appear inconsistent;
- sensitivity span extends to a nonphysical input and has been rejected.

Warnings need stable machine-readable codes, severity, affected field, plain-language explanation, and remediation.

### 7.3 No silent data repair

The package must not:

- impute viscosity, temperature, dimensions, time, or flow;
- convert gauge to inner diameter from an undocumented table;
- average duplicate scenarios;
- strip suspect rows and continue without an explicit rejected-row record;
- clip negative values;
- infer units from magnitude;
- substitute water density;
- transform a non-Newtonian viscosity into an “effective” Newtonian value.

## 8. Sensitivity analysis

### 8.1 v0.1 deterministic analysis

The default sensitivity mode is one-at-a-time relative perturbation of:

- viscosity;
- needle length;
- needle inner diameter;
- barrel inner diameter;
- injection time or flow rate.

For each perturbation, the package reruns the same validated scientific core and reports absolute and relative changes in pressure and force. It also reports the model’s analytical log-elasticities:

| Input | Elasticity of \(F_f\) |
|---|---:|
| viscosity \(\mu\) | +1 |
| needle length \(L\) | +1 |
| flow rate \(Q\) | +1 |
| barrel ID \(D_b\) | +2 |
| needle ID \(d\) | −4 |
| injection time \(t\), at fixed volume | −1 |

The analytical values serve as invariant tests for the numerical sensitivity engine.

### 8.2 Uncertainty boundary

v0.1 does not call deterministic perturbations a probabilistic uncertainty interval. Monte Carlo or tolerance-stack simulation is deferred until:

- input distributions have explicit provenance;
- correlated dimensions can be represented;
- reference cases are independently reproduced; and
- coverage and interpretation are documented.

## 9. Structured result contract

The core returns an immutable `AssessmentResult`, independent of plots and reports:

```text
AssessmentResult
├── schema_version
├── package_version
├── model_id
├── run_id
├── generated_at_utc
├── status: passed | passed_with_warnings | rejected
├── normalized_input
├── provenance
│   ├── source_file_sha256
│   ├── geometry_sources
│   ├── rheology_evidence
│   └── effective_configuration
├── outputs
│   ├── flow_rate_m3_s
│   ├── injection_time_s
│   ├── needle_pressure_drop_pa
│   ├── barrel_area_m2
│   ├── fluid_resistance_force_n
│   ├── wall_shear_rate_s_1
│   ├── mean_velocity_m_s
│   └── reynolds_number
├── sensitivity
├── warnings
├── exclusions
└── validation_status
```

JSON uses `null` for a diagnostic that was not calculated and includes a reason code. JSON must never emit `NaN` or infinity.

`validation_status` is conservative:

- `equation_verified`: algebraic/unit/reference-value tests pass;
- `internal_validation`: internal fixtures and cross-implementation checks pass;
- `experimental_validation_pending`: independent experimental agreement has not been completed;
- `independently_validated`: reserved for a version with a published, versioned validation report.

v0.1 must not default to the last status.

## 10. Public Python API

Proposed stable surface:

```python
from openinjectability import (
    AssessmentConfig,
    AssessmentInput,
    AssessmentResult,
    assess,
    assess_file,
)

case = AssessmentInput(
    scenario_id="mab-a-27g",
    formulation_id="mab-a",
    viscosity_value=35.0,
    viscosity_unit="cP",
    viscosity_temperature_c=25.0,
    use_temperature_c=25.0,
    rheology_class="newtonian",
    newtonian_evidence="RHEO-2026-014",
    needle_id_mm=0.21,
    needle_length_mm=12.7,
    needle_gauge_label="27G",
    needle_geometry_source="supplier drawing DRAW-27TW-v3",
    barrel_id_mm=6.35,
    barrel_geometry_source="syringe drawing SYR-1ML-v2",
    volume_ml=2.0,
    injection_time_s=15.0,
)

result = assess(case, config=AssessmentConfig())
```

API rules:

- models are typed and validate on construction;
- the scientific core has no file-system, plotting, or template dependency;
- batch APIs preserve input row order and return explicit rejected rows;
- result serialization is schema-versioned;
- exceptions are typed (`InputSchemaError`, `ScientificBoundaryError`, `UnitError`);
- low-level equations may be public only if their units and assumptions are explicit.

## 11. Command-line interface

### 11.1 Canonical command

```powershell
openinjectability assess formulation.csv `
  --config assessment.yml `
  --report assessment.html `
  --results assessment.json
```

### 11.2 Single-case command

The original gauge-oriented example becomes traceable by requiring geometry:

```powershell
openinjectability assess-one `
  --viscosity "35 cP" `
  --viscosity-temperature "25 degC" `
  --use-temperature "25 degC" `
  --rheology newtonian `
  --rheology-evidence "RHEO-2026-014" `
  --needle-gauge "27G" `
  --needle-id "0.21 mm" `
  --needle-length "12.7 mm" `
  --needle-source "supplier drawing DRAW-27TW-v3" `
  --barrel-id "6.35 mm" `
  --barrel-source "syringe drawing SYR-1ML-v2" `
  --volume "2.0 mL" `
  --injection-time "15 s" `
  --report assessment.html
```

### 11.3 Supporting commands

```text
openinjectability validate-input <file>
openinjectability assess <file>
openinjectability compare-geometries <file>
openinjectability validation-status [--json]
openinjectability schema [--format json|yaml]
openinjectability version
```

Exit codes:

| Code | Meaning |
|---:|---|
| 0 | all requested assessments completed |
| 2 | input or schema error |
| 3 | scientific-boundary rejection |
| 4 | report-generation failure after results were calculated |
| 5 | internal consistency or validation-registry failure |

## 12. Plots and reports

### 12.1 Required plots

1. Predicted fluid-resistance force versus candidate needle geometry, using actual inner diameter on the primary x-axis; gauge labels are annotations only.
2. Pressure drop versus flow rate or injection time.
3. Tornado-style deterministic sensitivity plot.
4. Scenario comparison plot with warnings visually distinguished.

Plots must:

- state “Newtonian idealized needle-fluid model” in the subtitle;
- include units on every axis;
- distinguish measured inputs from calculated outputs;
- avoid green/red “safe/unsafe” semantics;
- include the model ID and scenario ID in metadata or caption;
- remain interpretable in grayscale and with common color-vision deficiencies.

### 12.2 Report formats

- **Markdown:** portable review artifact;
- **HTML:** self-contained, accessible report with embedded figures;
- **PDF:** generated from the same report model and verified for pagination;
- **JSON:** authoritative machine-readable result.

The HTML/Markdown/PDF report must contain:

1. title, timestamp, package version, model ID, and run ID;
2. prominent scientific-boundary statement;
3. source and SHA-256 of the input;
4. normalized inputs and original display values;
5. equations and assumptions;
6. pressure, force, time/flow, and shear diagnostics;
7. sensitivity table and plots;
8. warnings and rejected rows;
9. excluded force components;
10. validation status;
11. references;
12. reproducibility command.

### 12.3 Audit bundle

Optional `--audit-bundle assessment.zip` contains:

```text
input/original.csv
input/normalized.csv
config/effective_config.json
results/assessment.json
reports/assessment.html
reports/assessment.md
figures/*.svg
provenance/environment.json
provenance/validation_manifest.json
manifest.sha256
```

ZIP entries must be deterministic where practical. The manifest records every file hash and the hashing algorithm.

## 13. Proposed architecture

```text
OpenInjectability/
├── pyproject.toml
├── README.md
├── LICENSE
├── CITATION.cff
├── CHANGELOG.md
├── VALIDATION.md
├── PROJECT_SPECIFICATION.md
├── docs/
│   ├── scientific-basis.md
│   ├── input-schema.md
│   ├── interpretation.md
│   └── roadmap.md
├── src/openinjectability/
│   ├── __init__.py
│   ├── models.py
│   ├── units.py
│   ├── validation.py
│   ├── core.py
│   ├── sensitivity.py
│   ├── batch.py
│   ├── reporting.py
│   ├── plotting.py
│   ├── cli.py
│   └── validation_registry/
│       └── manifest.json
└── tests/
    ├── reference_data/
    ├── test_core.py
    ├── test_units.py
    ├── test_validation.py
    ├── test_sensitivity.py
    ├── test_cli.py
    └── test_reports.py
```

Dependency direction:

```text
models + units → validation → core → sensitivity/batch
                                  ↓
                         plotting/reporting/CLI
```

The core must not import CLI, plotting, templating, pandas, or PDF modules.

## 14. Verification and validation strategy

### 14.1 Equation and dimensional tests

- reproduce hand-calculated SI reference cases;
- independently implement the equation in a spreadsheet or second script and compare;
- test the equivalent pressure-area and simplified force forms;
- test dimensional scaling and unit conversion;
- use analytical elasticities as metamorphic properties;
- test \(F\) doubles with viscosity, length, or flow;
- test \(F\) changes by \(2^2\) with barrel ID and \(2^{-4}\) with needle ID;
- test \(F\) halves when time doubles at fixed volume.

### 14.2 Property-based tests

Within the supported positive finite domain:

- pressure and force remain positive;
- results are invariant under equivalent unit representations;
- time and flow inverse calculations round-trip;
- increasing inner diameter strictly lowers modeled pressure;
- serialization never contains nonfinite JSON numbers;
- batch row order is stable.

### 14.3 Boundary tests

Test explicit rejection of:

- zero, negative, infinite, and `NaN` inputs;
- non-Newtonian and unknown rheology;
- missing temperature or geometry provenance;
- time-flow disagreement;
- gauge-only calculation;
- unsupported unit and schema version;
- force ceiling without source.

### 14.4 Literature and experimental validation

The first release may claim equation verification but must mark experimental validation as pending unless the following is completed:

1. Obtain or generate an independently traceable Newtonian reference dataset with viscosity, temperature, measured needle ID/length, barrel ID, volume, rate, and fluid-force or pressure measurements.
2. Predefine comparison metrics and acceptance criteria before running validation.
3. Separate calibration/development data from validation data.
4. Reproduce results without fitting hidden correction factors.
5. Investigate systematic differences attributable to excluded losses.
6. Publish the exact fixtures permitted by licensing and a validation report with hashes.

The non-Newtonian experimental studies in the references establish the importance of rheology and geometry; they do **not** validate silently applying the v0.1 Newtonian equation to shear-thinning formulations.

### 14.5 Release quality gates

Release `0.1.0` only when all pass:

- version values agree across package, CLI, and reports;
- unit, equation, property, boundary, CLI, and report tests pass;
- static checks and type checks pass;
- build and metadata validation pass;
- wheel installs in a clean environment;
- CLI smoke generates JSON, HTML, Markdown, PDF, and plots from a reference fixture;
- PDF pages are rendered and visually inspected;
- validation registry ships inside the wheel;
- public documentation repeats the scientific boundary consistently;
- no “total injection force,” “safe,” “compliant,” or human-capability claim appears;
- fresh install from the intended public index is verified after publication.

## 15. Milestones

### M0 — Charter and reference lock

- approve this scientific boundary;
- choose license and package name;
- freeze terminology and initial schemas;
- establish reference and validation ledgers.

**Exit:** scientific reviewer approves equations, exclusions, and result language.

### M1 — Typed scientific core

- implement units, input models, hard validation, pressure, force, time/flow, and shear diagnostics;
- add hand calculations and property tests.

**Exit:** core tests pass with no file or plotting dependency.

### M2 — Batch, sensitivity, and provenance

- add CSV ingestion, deterministic sensitivity, structured results, rejected-row records, and hashes.

**Exit:** reference batch is reproducible byte-for-byte except documented timestamps/run IDs.

### M3 — CLI and reports

- add CLI, plots, Markdown/HTML/PDF output, audit bundle, and accessibility checks.

**Exit:** clean-environment end-to-end smoke passes.

### M4 — Independent validation

- lock a validation protocol;
- run independently sourced Newtonian cases;
- publish discrepancies and limitations.

**Exit:** validation status is updated only to the level supported by evidence.

### M5 — Public release

- publish documentation, signed/tagged release, wheel, source distribution, and validation artifacts;
- verify a fresh public-index install.

**Exit:** public artifacts and version metadata converge.

## 16. Risks and controls

| Risk | Consequence | Control |
|---|---|---|
| gauge treated as unique ID | large force error due to \(d^4\) term | require traceable inner diameter |
| non-Newtonian formulation accepted | scientifically invalid force | explicit rheology enum and fail-closed validation |
| viscosity used at wrong temperature | misleading prediction | require both temperatures; no correction in v0.1 |
| fluid force mistaken for total force | unsafe or overstated interpretation | fixed terminology and exclusions beside results |
| unverified default force ceiling | implied human/device claim | never ship a universal ceiling |
| software output called regulatory evidence | overclaim | decision-support disclaimer and validation status |
| report differs from JSON | audit inconsistency | render all formats from one immutable result |
| proprietary geometry or data redistributed | licensing breach | store hashes/provenance; publish only permitted fixtures |
| PDF renderer changes content | incomplete report | compare report model and visually inspect rendered pages |

## 17. v0.1 acceptance criteria

The v0.1 package is acceptable when a reviewer can:

1. trace every numerical output to a normalized input and stated equation;
2. see that only Newtonian fluids are accepted;
3. confirm that actual needle ID, not gauge alone, drives the calculation;
4. distinguish predicted fluid-resistance force from total device force;
5. reproduce a result through Python and CLI with equivalent units;
6. identify every default and its source;
7. receive a structured rejection for unsupported science;
8. inspect sensitivity to all primary inputs;
9. generate equivalent JSON, Markdown, HTML, and PDF content;
10. verify hashes and validation status in an audit bundle.

## 18. Deferred roadmap

Deferred features are not implied by v0.1:

- non-Newtonian power-law, Carreau, Cross, Herschel–Bulkley, or other rheology models;
- syringe friction and break-loose modeling;
- device spring/motor and human-factor models;
- needle entrance/minor-loss corrections;
- tissue backpressure and subcutaneous depot models;
- temperature-dependent viscosity interpolation;
- probabilistic tolerance stacks;
- measured-data calibration;
- web application or hosted service.

A shear-thinning model may enter a later version only after:

1. a specific constitutive equation and parameter-identification protocol are chosen;
2. shear-rate coverage requirements are defined;
3. independent experimental validation data are secured;
4. model-selection and extrapolation failure modes are tested;
5. outputs clearly identify the selected rheology model;
6. the Newtonian path remains available and unchanged for validated cases.

## 19. Reference implementation example

Illustrative input (not a validated formulation):

```csv
scenario_id,formulation_id,viscosity_value,viscosity_unit,viscosity_temperature_c,use_temperature_c,rheology_class,newtonian_evidence,needle_id_mm,needle_length_mm,needle_gauge_label,needle_geometry_source,barrel_id_mm,barrel_geometry_source,volume_ml,injection_time_s
mab-a-27g,mab-a,35,cP,25,25,newtonian,RHEO-2026-014,0.21,12.7,27G,DRAW-27TW-v3,6.35,SYR-1ML-v2,2.0,15
```

Expected report language:

> The calculated value is the predicted fluid-resistance force arising from idealized Newtonian flow through the specified needle. It excludes syringe friction, break-loose force, device losses, and tissue backpressure. Experimental verification is required before device or human-use decisions.

No numerical expected value is locked into this specification; a hand-calculated, independently reviewed fixture must be added during M1.

## 20. References and source status

Sources were checked on 2026-07-31. Links should be rechecked before release because guidance, standards, and web pages can change.

1. Müller R, et al. “Rheological characterization and injection forces of concentrated protein formulations: an alternative predictive model for non-Newtonian solutions.” *European Journal of Pharmaceutics and Biopharmaceutics*. 2014;87(1):223–233. PMID 24560966; DOI: [10.1016/j.ejpb.2014.01.009](https://doi.org/10.1016/j.ejpb.2014.01.009); [PubMed record](https://pubmed.ncbi.nlm.nih.gov/24560966/). This study supports the importance of rheology, injection speed, and syringe/needle geometry; it does not justify non-Newtonian support in v0.1.
2. Fischer I, Schmidt A, Bryant A, Besheer A. “Calculation of injection forces for highly concentrated protein solutions.” *International Journal of Pharmaceutics*. 2015;493(1–2):70–74. PMID 26211901; DOI: [10.1016/j.ijpharm.2015.07.054](https://doi.org/10.1016/j.ijpharm.2015.07.054); [PubMed record](https://pubmed.ncbi.nlm.nih.gov/26211901/). The abstract specifically identifies accurate needle dimensions and shear-thinning behavior as vital to prediction.
3. BIPM. *The International System of Units (SI Brochure)*, 9th edition, updated version. [Official SI Brochure](https://www.bipm.org/en/publications/si-brochure). Use for unit definitions and traceability; access checked 2026-07-31.
4. ISO 7886-1. *Sterile hypodermic syringes for single use — Part 1: Syringes for manual use*. [ISO catalogue entry](https://www.iso.org/standard/64790.html). The standard is licensed; implementation must not reproduce protected requirements without authorization.
5. ISO 9626. *Stainless steel needle tubing for the manufacture of medical devices — Requirements and test methods*. [ISO catalogue search](https://www.iso.org/search.html?q=ISO%209626). The current edition and applicable dimensional source must be verified and lawfully accessed before a geometry catalog is shipped.

## 21. Required disclaimer

OpenInjectability is a scientific decision-support and research tool. Its v0.1 model estimates only idealized fluid resistance for declared Newtonian liquids and traceable geometry. It does not predict total injection-device force, does not evaluate human capability or patient outcomes, is not a medical device, and does not establish regulatory compliance. Users remain responsible for experimental verification, device qualification, risk management, and applicable regulatory requirements.
