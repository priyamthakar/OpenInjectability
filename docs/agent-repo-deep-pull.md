# Repository deep pull — Zenodo + Figshare (Phase D)

**Date:** 2026-08-02  
**Scope:** Downloadable CSV/XLS (or equivalent machine-readable) experimental data on **syringe/needle injection force** with **viscosity** and **geometry**, for Newtonian / fluid-resistance validation.  
**Machine-readable twin:** [agent-repo-deep-pull.json](agent-repo-deep-pull.json)  
**Related:** [agent-open-datasets.md](agent-open-datasets.md), [validation-protocol-lock.md](validation-protocol-lock.md)  
**No fabrication:** only API metadata and files actually downloaded were used.

---

## Phase D field bar (must all hold per experimental row)

| Field | Meaning |
|---|---|
| **μ** | Measured dynamic viscosity + temperature; Newtonian attestation |
| **d** | Needle **inner diameter** (traceable; not gauge-only) |
| **L** | Needle length (traceable) |
| **barrel** | Barrel / plunger ID |
| **Q** | Volumetric flow rate, or volume + controlled injection time |
| **F_fluid** | Fluid-side force **or** pressure (friction-separated or ΔP × barrel area) |

OpenInjectability predicts only idealized needle fluid resistance  
\(F_f = 32\,\mu\,L\,Q\,D_b^2 / d^4\). Total glide / clinical injection force is a **different measurand**.

---

## Verdict

### Phase-D complete dataset found? **No**

No Zenodo or Figshare deposit supplies a downloadable experimental panel with complete  
**μ + measured d + L + barrel + Q + friction-separated F_fluid** (or equivalent pressure).

Near-miss open files exist (ophthalmic total-force XLSX; autoinjector **time** SI; AUC stats DOCX).  
None unlock Phase D.

---

## 1. Zenodo API

**Base:** `https://zenodo.org/api/records`  
**Note:** unauthenticated `size` max is **25** (requesting 50 returns HTTP 400).

### Queries run (dataset filter unless noted)

| Query | `type=dataset` total | Outcome |
|---|---:|---|
| `syringe injection force` | 6678 | False positives (SSP directories, filtration, medical device noise) |
| `syringe force viscosity` | 5752 | Same noise class |
| `injection force needle viscosity` | 7449 | Same |
| `glycerol syringe force` | 5420 | MD glycerol viscosity / surface tension — not syringe force |
| `glycerol needle injection force` | 7122 | Same |
| `injectability viscosity` | 567 | Soil liquefaction injectability, lava dome, blood/rheology CSVs — **not** syringe \(F_f\) |
| `glide force syringe` | 5285 | Unrelated |
| `syringeability viscosity` | 567 | Unrelated |
| `Hagen Poiseuille syringe` | 614 | Numerical HP flow, multi-infusion reports, historical Poiseuille PDFs — no experimental force panel |
| `injection force glycerol` | 6764 | Unrelated / MD |
| `plunger force viscosity` | 5639 | Unrelated |
| `break loose force syringe` | 6443 | Mostly SSP programs |
| `extrusion force syringe` | 5456 | Unrelated |
| `needle diameter viscosity force` | 10033 | Unrelated |
| `Allmendinger injection force` | 6572 | No Allmendinger injection-force deposit; keyword noise |
| `Cilurzo injectability` | 1 | Bibliometric ODF dataset only — not injectability force |
| `Newtonian viscosity syringe force` | 5865 | Unrelated |
| `"injection force" AND (syringe OR needle)` | **0** | Exact phrase empty |
| `"glide force" AND syringe` | **0** | Exact phrase empty |
| `type:dataset AND syringe AND viscosity AND needle AND force` | **0** | Empty |
| `title:"injection force"` | **0** | Empty |
| `title:injectability AND (syringe OR needle)` | **0** | Empty |
| `title:syringeability` | **0** | Empty |
| `title:"glide force"` | 1 | **Dislocation glide force in nickel** (materials), not syringe |
| Broad (no type filter): `syringe injection force` | 60347 | Publications + noise; no usable force×viscosity CSV panel |
| Broad: `glycerol needle force` | 52406 | Noise |
| Broad: `"injection force" viscosity` | 7804 | Noise / non-syringe |

### Zenodo conclusion

- Exact Boolean / title queries for **injection force / glide force / syringeability** + syringe/needle return **0 relevant experimental datasets**.
- Broad keyword totals are large but dominated by **syringe services programs**, MD glycerol, cement/lava **injectability**, blood viscosity, etc.
- Downloadable CSVs that appear under viscosity keywords (e.g. atmospheric particle viscosity, hemolymph) do **not** contain syringe geometry or fluid-resistance force.
- **No Zenodo CSV/XLS** of experimental syringe injection force vs measured viscosity + needle/barrel geometry was found.

---

## 2. Figshare API

**Base:** `https://api.figshare.com/v2`  
**Targeted DOIs (user-requested):**

| DOI | Article ID | Downloadable? | Format |
|---|---|---|---|
| [10.6084/m9.figshare.32195520.v1](https://doi.org/10.6084/m9.figshare.32195520.v1) | 32195520 | **Yes** | XLSX ~17 KB |
| [10.6084/m9.figshare.20800108.v1](https://doi.org/10.6084/m9.figshare.20800108.v1) | 20800108 | **Yes** | 2× DOCX (figures + stats tables) |

**Keyword search** (`POST /v2/articles/search`, body `{"search_for": ...}`) also returned Ackermann 2026 SI articles and Felfeli SI siblings (inspected below).

---

### A. Felfeli et al. raw force/pressure XLSX — **downloaded & columns inspected**

| Item | Value |
|---|---|
| **Title** | Additional file 10 of *Guiding syringe selection for intravitreal injections…* (SYFOVRE) |
| **DOI** | 10.6084/m9.figshare.32195520.v1 |
| **Download** | https://ndownloader.figshare.com/files/64317894 |
| **File** | `40942_2026_832_MOESM10_ESM.xlsx` (17 293 bytes) |
| **Sheet** | `wide summary (3)` |
| **Data rows** | **46** experimental injections (after header rows) |
| **Parent paper** | 10.1186/s40942-026-00832-3 |
| **License** | Figshare license object CC BY + CC0 style |

**Columns (exact header row from file):**

Summary block:

`date`, `syringe`, `fluid_density`, `EYEID`, `type`, `needle`, `IOP_prior`, `IOP_post`, `inj_max`, `inj_mean`, `inj_time`, `reflux`

Time-series block (same rows):

header label `Raw injection pressure over time` / `Time (s) ->` then sample times `0, 0.5, 1, …` with numeric pressure/force-like samples.

**Unique values actually present:**

| Column | Values in file |
|---|---|
| `syringe` | BD, ClearJect, StaClear, ZR0.2 |
| `fluid_density` | **15 cP**, **120 cP** (labels only) |
| `needle` | **27G** only |
| `type` | phakic, pseudophakic, ND |

**Example rows (exact values from downloaded XLSX — not invented):**

| date | syringe | fluid_density | EYEID | type | needle | IOP_prior | IOP_post | inj_max | inj_mean | inj_time | reflux |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---|
| Feb-02-2025 | StaClear | 120 cP | 2025-01-OD | phakic | 27G | 23 | 20 | 137 | 85.4 | 7.5 | n |
| Feb-02-2025 | ClearJect | 120 cP | 2025-01-OD | phakic | 27G | 18 | 24 | 177 | 122.7 | 8.39 | y |
| Feb-02-2025 | ZR0.2 | 120 cP | 2025-01-OD | phakic | 27G | 18 | 29 | 104 | 88.8 | 12 | n |

**Why not Phase-D usable:**

| μ | d | L | barrel | Q | F_fluid |
|:-:|:-:|:-:|:------:|:-:|:-------:|
| partial (cP labels; no T; not glycerol panel) | no (27G only) | no | brand only | no (variable `inj_time`; eye injection) | **no** (tissue + friction total; header says pressure into eye) |

Citation for the deposit: Felfeli et al. supplementary file 10, Figshare DOI **10.6084/m9.figshare.32195520.v1**.

---

### B. Rini et al. 2022 LVAI SI — **downloaded & text-inspected**

| Item | Value |
|---|---|
| **Title** | Enabling faster subcutaneous delivery of larger volume, high viscosity fluids |
| **DOI** | 10.6084/m9.figshare.20800108.v1 |
| **Files** | `iedd_a_2116425_sm8405.docx` (figures; delivery **time** in air vs in vivo) |
| | `iedd_a_2116425_sm8404.docx` (Supplemental Table 1: device **contrast estimates** on delivery metrics by viscosity / gauge / spring tier) |
| **Parent paper** | 10.1080/17425247.2022.2116425 |
| **License** | CC BY 4.0 |

**What the SI actually contains (from extracted text):**

- Viscosity levels referenced as **2.3, 5.8, 11.8, 20.4, 31, 39 cP** (and related contrasts).
- Device factors: **27G STW / UTW**, **29G TW**, spring force tiers **SF LOW / SF HIGH**.
- Primary outcomes: **delivery time**, erythema/wheal scores — **not** plunger force or needle ΔP.
- No numeric needle ID, length, barrel ID, or friction-separated fluid force table.

**Why not Phase-D usable:**

| μ | d | L | barrel | Q | F_fluid |
|:-:|:-:|:-:|:------:|:-:|:-------:|
| yes-ish (Newtonian cP series in paper/SI narrative) | no (gauge/wall only) | no | no | partial (time under spring) | **no** |

---

### C. Ackermann et al. 2026 SI (discovered via Figshare search) — **downloaded**

| Article ID | DOI | File | Content |
|---|---|---|---|
| 31976504 | 10.6084/m9.figshare.31976504.v1 | PDF | SI figure package |
| 31976507 | 10.6084/m9.figshare.31976507.v1 | DOCX | Fig S1 AUC illustration (BSS, 33G, Syringe C) |
| 31976510 | 10.6084/m9.figshare.31976510.v1 | DOCX | **Table S1** descriptive AUC [N·s] by cannula/syringe/fluid; ANOVA tables |

**Table S1 (exact means from SI text, units N·s) — sample cells only:**

| Cannula | Syringe | BSS mean | PEG 40,000 mean | PEG 400 mean | Tween mean |
|---|---|---:|---:|---:|---:|
| 30G | A | 3.892 | 16.548 | 60.600 | 30.546 |
| 30G | B | 4.551 | 49.272 | 125.640 | 98.880 |
| 30G | C | 4.504 | 51.140 | 132.080 | 99.694 |
| 33G | A | 5.988 | 64.174 | 211.920 | 149.420 |
| 33G | B | 10.917 | 189.100 | 617.420 | 537.880 |
| 33G | C | 10.477 | 230.280 | 819.220 | 459.260 |

*(n = 5 per cell; full SD/SEM/95% CI in SI. Source: Figshare 10.6084/m9.figshare.31976510.v1.)*

**Why not Phase-D usable despite real force-related numbers:**

| μ | d | L | barrel | Q | F_fluid |
|:-:|:-:|:-:|:------:|:-:|:-------:|
| partial (η* for BSS/PEG/Tween in paper; not in SI CSV) | no (30G/33G only) | lengths in paper not in SI rows | plunger Ø in paper not linked as CSV | no (manual; AUC not fixed Q) | **no** (total force–time AUC; no empty-friction subtraction) |

Raw time-series: paper states available from corresponding author on request — **not** deposited as public CSV/XLS.

---

### D. Other Figshare hits (not usable)

| ID | Note |
|---|---|
| 27412368 | *Flow and injection characteristics… micro-capillary* — API lists **0 files** (no download) |
| 32195514 / 32195496 | Felfeli PNG figures only |
| 32923061 | Full-text PDF of Felfeli paper (not a validation panel) |

---

## 3. What would count as Phase-D complete (not found)

A single public CSV/XLS where each row has at least:

1. μ (mPa·s or Pa·s) + T (°C) + Newtonian statement  
2. Measured needle ID \(d\) and length \(L\)  
3. Barrel/plunger ID  
4. Imposed Q (or V and controlled t)  
5. \(F_{\mathrm{fluid}}\) or ΔP with friction baseline / empty-syringe subtraction  

None of the Zenodo or Figshare deposits inspected meet this bar.

---

## 4. Implication

| Item | Status |
|---|---|
| Phase-D complete open dataset from this deep pull | **No** |
| Best real downloadable near-miss | Felfeli XLSX (total IVI pressure/force) |
| Best factorial force×viscosity×geometry open stats | Ackermann AUC SI (still total force) |
| Newtonian viscosity but wrong measurand | Rini LVAI time SI |
| `validation_status` | Remains `internal_validation; experimental_validation_pending` |

**Unblock path (unchanged):** benchtop glycerol–water + load cell/pressure + empty friction baseline, or a future SI that already publishes friction-corrected hydrodynamic force as complete machine-readable rows.

---

## 5. Search log (compact)

| Channel | Method | Usable Phase D? |
|---|---|---|
| Zenodo REST | 20+ keyword queries + exact phrase/title filters; size≤25; type=dataset and broad | **No** |
| Figshare REST | Direct articles 32195520, 20800108 (+ Ackermann SI 31976504/07/10); search_for keyword | **No** (near-misses only) |
| File inspect | openpyxl on Felfeli XLSX; DOCX XML text extract on Rini + Ackermann SI | Documented columns/rows only |

Supporting raw API dumps (local working files from this pull):  
`_repo_deep_pull_raw.json`, `_repo_deep_pull_analysis.json`, `_repo_deep_pull_figshare_extra.json`.

*No data were invented. Example table cells are either exact XLSX cells or exact SI text extracts with DOI citation.*
