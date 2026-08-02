# Open repository search — syringe/needle injection force datasets (Phase D)

**Date:** 2026-08-02  
**Scope:** Downloadable experimental datasets (CSV/XLS preferred) on syringe/needle **injection force** with **viscosity** and **geometry** for **Newtonian** fluids. No fabrication.  
**Machine-readable twin:** [agent-open-datasets.json](agent-open-datasets.json)  
**Related:** [literature-scrape-assessment.md](literature-scrape-assessment.md), [validation-protocol-lock.md](validation-protocol-lock.md)

---

## Protocol field bar (must all hold)

For a repository deposit to unlock Phase D, each experimental row needs:

| Field | Meaning |
|---|---|
| **μ** | Measured dynamic viscosity + temperature; Newtonian attestation |
| **d** | Needle **inner diameter** (traceable; not gauge-only) |
| **L** | Needle length (traceable) |
| **barrel** | Barrel / plunger ID |
| **Q** | Volumetric flow rate, or volume + controlled injection time |
| **F_fluid** | Fluid-side force **or** pressure (friction-separated or ΔP × barrel area) |

OpenInjectability predicts only idealized needle fluid resistance  
\(F_f = 32\,\mu\,L\,Q\,D_b^2 / d^4\). Total glide/injection force is a **different measurand**.

---

## Channels searched

### 1. Zenodo API (`https://zenodo.org/api/records`)

| Query theme | Outcome |
|---|---|
| `syringe injection force viscosity needle` (type=dataset) | Large hit counts; top results are syringe **services programs**, MD glycerol viscosity, filtration robots, fracture sensors — **no injection-force panel** |
| glycerol + needle + injection force / glide force / Hagen–Poiseuille | Same noise class; MD viscosity of aqueous glycerol, not syringe force |
| Exact: `"injection force" AND (syringe OR needle) AND (viscosity OR glycerol OR Newtonian)` | **0 hits** |
| Exact: glide force / break-loose / expulsion force + syringe/needle | **0 hits** |
| `syringeability OR injectability force viscosity` (type=dataset) | **0 hits** |
| `title:(injection AND force) AND (syringe OR needle OR viscosity)` | **0 hits** |

**Conclusion:** No Zenodo dataset of experimental syringe injection force vs viscosity/geometry.

### 2. DataCite API (`https://api.datacite.org/dois`)

| Query | Outcome |
|---|---|
| `injection force syringe` | 43 DOIs; useful subset → Springer Nature Figshare collections for **intravitreal** syringe force papers (Ackermann, Felfeli) |
| glycerol / glide force / syringeability | Hundreds of unrelated materials/MD hits; no complete Phase D panel |

### 3. Dryad API (`https://datadryad.org/api/v2/search`)

- Query: `syringe injection force viscosity` → **count = 0**
- Web-style Dryad queries for injection force + syringe/needle + viscosity → empty

### 4. Figshare / Springer Nature Figshare

Discovered via DataCite + web (`site:figshare.com injection force syringe viscosity`):

- Collection: *Guiding syringe selection for intravitreal injections…* (SYFOVRE) — **raw force XLSX**
- Collection: *Syringe design and cannula dimensions… time-force curve…* (Ackermann) — SI stats; raw on request
- T&F Figshare: Rini et al. large-volume autoinjector (Newtonian viscosities; **time**, not force)

Generic Figshare keyword search API returned mostly unrelated recent uploads; targeted DOIs/collections above were inspected via `api.figshare.com/v2/articles/{id}`.

### 5. EuropePMC (`HAS_DATA`-style query)

- Query: `injection force syringe viscosity HAS_DATA:y` → large hitCount; flag not reliably discriminating.
- Top OA papers: Ackermann 2026 (`10.1186/s40942-026-00833-2`), Felfeli 2026 (`10.1186/s40942-026-00832-3`).
- Many articles still say data **upon request**, not a complete public CSV panel.

### 6. Other web / dataset-style queries

Tried (representative):

- `"injection force" glycerol water syringe needle` + dataset/supplementary/zenodo/figshare/dryad  
- `"Hagen-Poiseuille" syringe force experiment data OR dataset`  
- `site:osf.io syringe injection force viscosity`  
- `site:data.mendeley.com injection force syringe viscosity`  
- Harvard Dataverse–style queries  

**No** OSF / Mendeley / Dataverse deposit found that is a complete Newtonian μ–geometry–**F_fluid** table.

---

## Datasets actually found (downloadable or open tables)

### A. Felfeli et al. — raw injection force XLSX (Figshare)

| Item | Value |
|---|---|
| **URL** | https://springernature.figshare.com/articles/dataset/Additional_file_10_of_Guiding_syringe_selection_for_intravitreal_injections_injectability_and_stability_analysis_of_compounded_pegcetacoplan_SYFOVRE_and_the_broader_implications_for_high-viscosity_ophthalmic_therapies/32195520 |
| **DOI** | [10.6084/m9.figshare.32195520.v1](https://doi.org/10.6084/m9.figshare.32195520.v1) |
| **License** | CC BY 4.0 + CC0 (Figshare “CC BY + CC0”) |
| **Format** | `40942_2026_832_MOESM10_ESM.xlsx` (~17 KB) |
| **Download** | https://ndownloader.figshare.com/files/64317894 |
| **Parent paper** | `10.1186/s40942-026-00832-3` |

**What is in the file (inspected):**

- Columns: `date`, `syringe`, `fluid_density` (labels **15 cP** / **120 cP**), `EYEID`, `needle` (**27G**), IOP, `inj_max` / `inj_mean` / `inj_time`, plus time-series force samples.
- Real experimental force–time traces for multiple syringe brands.

**Field coverage vs protocol:**

| μ | d | L | barrel | Q | F_fluid |
|:-:|:-:|:-:|:------:|:-:|:-------:|
| partial (cP labels; mimics) | no (gauge only) | no | brand only | no (manual / clinical into eye) | **no** (tissue + friction) |

**Phase D usable?** **No.**

---

### B. Ackermann et al. 2026 — published force tables + SI (OA)

| Item | Value |
|---|---|
| **URL / DOI** | https://doi.org/10.1186/s40942-026-00833-2 · PMC [PMC13063457](https://pmc.ncbi.nlm.nih.gov/articles/PMC13063457/) |
| **Figshare collection** | [10.6084/m9.figshare.c.8411480.v1](https://doi.org/10.6084/m9.figshare.c.8411480.v1) |
| **License** | CC BY 4.0 (article); SI CC BY + CC0 |
| **Format** | Main-text Tables 3–4 (AUC N·s, peak force N); SI DOCX descriptive stats/ANOVA |
| **Raw data** | “Available from the corresponding author upon reasonable request” — **not** a public CSV/XLS deposit |

**Design (from paper):**

- Fluids: BSS, PEG-40 000, PEG-400, Tween-80+BSS with measured **complex viscosity** at 25 °C  
- Cannulas: 30 G × 13 mm, 33 G × 9 mm  
- Plunger diameters: ~2.48 / 4.71 / 4.76 mm  
- Manual force-gauge expulsion of 0.1 mL (not fixed Q)

**Field coverage vs protocol:**

| μ | d | L | barrel | Q | F_fluid |
|:-:|:-:|:-:|:------:|:-:|:-------:|
| partial (η*; PEG/Tween) | no (gauge only) | yes | yes (plunger Ø) | no (manual) | **no** (total resistance) |

**Phase D usable?** **No** (best open *tabular near-miss* for factorial viscosity × geometry × force, wrong measurand).

---

### C. Rini et al. 2022 — Newtonian LVAI supplementary (Figshare)

| Item | Value |
|---|---|
| **URL** | https://tandf.figshare.com/articles/dataset/Enabling_faster_subcutaneous_delivery_of_larger_volume_high_viscosity_fluids/20800108 |
| **DOI** | [10.6084/m9.figshare.20800108.v1](https://doi.org/10.6084/m9.figshare.20800108.v1) |
| **License** | CC BY 4.0 |
| **Format** | DOCX SI (statistical contrasts on **delivery time**; figures) |
| **Parent paper** | `10.1080/17425247.2022.2116425` |

**Strength:** Explicit **Newtonian** solutions 2.3–50 cP.  
**Failure:** Primary outcomes are autoinjector **delivery time** under spring force tiers — not measured \(F_f\) or needle ΔP; gauge/wall type only.

| μ | d | L | barrel | Q | F_fluid |
|:-:|:-:|:-:|:------:|:-:|:-------:|
| yes (Newtonian cP) | no | no | no | partial (time under spring) | **no** |

**Phase D usable?** **No.**

---

## Classic papers (not open datasets)

| Work | Why not counted as repository dataset |
|---|---|
| Allmendinger et al. 2014 (EJPB) — glycerol/water Newtonian + injection force model | Important literature; **no** open CSV/XLS deposit found |
| Verwulgen et al. 2018 (Pharm Res) — ID injection forces; water–glycerol | Institutional PDF / paywalled journal; **no** complete public row-level deposit with full geometry + friction-separated force |
| Zhang et al. 2018 (AAPS PharmSciTech) | HPMC/PEO non-Newtonian; total work metrics |

These remain literature candidates if full SI ever appears with friction-corrected hydrodynamic force and measured IDs — they are **not** usable open repository panels today.

---

## Final verdict (Phase D — repository data availability)

### **NONE USABLE**

**There is no downloadable open-repository experimental dataset (CSV/XLS or equivalent) that supplies Newtonian μ + measured needle d + L + barrel + Q + friction-separated F_fluid (or pressure) for syringe/needle injection.**

What exists:

1. **Real** open XLSX of total injection force into eyes (viscosity labels) — fails geometry + \(F_{\mathrm{fluid}}\).  
2. **Real** open OA tables of total peak force / AUC vs viscosity and plunger diameter — fails measured d, Q, \(F_{\mathrm{fluid}}\).  
3. **Real** open SI with Newtonian viscosities for autoinjector **time** — wrong measurand.  
4. **Zero** Zenodo / Dryad / OSF / Mendeley deposits matching the Phase D panel.

### Implication for project status

| Item | Status |
|---|---|
| Phases A–C software | Unchanged (complete) |
| Phase D experimental validation | **Still blocked** after repository search |
| Phase E “validated” claim | Blocked on D |
| `validation_status` | Must remain `internal_validation; experimental_validation_pending` |

### What would unblock (unchanged from protocol)

1. **Benchtop:** glycerol–water series, traceable needle ID/L, barrel ID, controlled Q, load cell **or** pressure transducer, empty-syringe friction baseline → \(F_{\mathrm{fluid}}\).  
2. **Literature:** obtain a paper whose SI already publishes friction-corrected hydrodynamic force as complete machine-readable rows — digitize only complete rows; version under `validation/experimental/` with hashes.  
3. **Do not** treat total glide/injection force tables (A–C above) as independent validation of \(F_f\).

---

## Search log (compact)

| Channel | Queries tried (summary) | Usable Phase D panel? |
|---|---|---|
| Zenodo API | 7+ formulations (exact + broad + title) | No |
| DataCite | injection force syringe (+ viscosity / glycerol) | No (pointers to near-misses only) |
| Dryad | syringe injection force viscosity | No (0 hits) |
| Figshare | DataCite collections + direct article IDs + site search | Near-misses only |
| EuropePMC | injection force syringe viscosity HAS_DATA | Near-miss OA papers only |
| Web/OSF/Mendeley/Dataverse style | glycerol/Newtonian + force + dataset operators | No complete panel |

*No data were invented. Near-miss files were inspected for fields; none meet the locked protocol bar.*
