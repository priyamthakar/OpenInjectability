# Open full-text hunt: Allmendinger 2014 + Verwulgen glycerol/syringe force

**Date:** 2026-08-02  
**Scope:** Legal free full text only (university repos, PMC, Unpaywall, HAL/OSF/ResearchSquare/author manuscripts). No paywalled or illicit copies.  
**Phase-D rule (project):** complete row = Newtonian μ (+ T) + measured needle ID + length + barrel ID + volume/Q or t + **fluid-only** force/pressure. Quote published numbers only.

**Machine-readable twin:** [agent-allmendinger-hunt.json](agent-allmendinger-hunt.json)

---

## Executive return

| Question | Answer |
|---|---|
| Free PDF of Allmendinger et al. 2014 (PMID 24560966)? | **No** |
| Free PDF of Verwulgen et al. 2018 (friction subtraction / glycerol)? | **Yes** |
| Supplementary CSV/tables with complete Newtonian glycerol + syringe geometry + force from either? | **No** (no CSV; Verwulgen has geometry + friction tables; glycerol forces only in a figure) |
| **Complete Phase-D rows extractable** | **0** |

---

## 1. Allmendinger et al. 2014 — CLOSED

### Bibliographic identity (confirmed)

| Field | Value |
|---|---|
| Title | Rheological characterization and injection forces of concentrated protein formulations: An alternative predictive model for non-Newtonian solutions |
| Authors | Andrea Allmendinger, Stefan Fischer, Joerg Huwyler, Hanns-Christian Mahler, Edward Schwarb, Isidro E. Zarraga, Robert Mueller |
| Journal | Eur. J. Pharm. Biopharm. **87**(2):318–328, July 2014 |
| DOI | [10.1016/j.ejpb.2014.01.009](https://doi.org/10.1016/j.ejpb.2014.01.009) |
| PMID | [24560966](https://pubmed.ncbi.nlm.nih.gov/24560966/) |
| PII | S0939-6411(14)00041-1 |
| Publisher | Elsevier BV |
| Affiliations | Roche Basel; University of Basel; Genentech South San Francisco |

### OA status checks (all negative for free full text)

| Source | Result |
|---|---|
| **Unpaywall** (`doi:10.1016/j.ejpb.2014.01.009`) | `is_oa: false`, `oa_status: closed`, `has_repository_copy: false`, `oa_locations: []` |
| **PubMed / PMC** | Abstract only; LinkOut → Elsevier + Ovid only; no PMCID |
| **Europe PMC** | Abstract/MED only; no free full text XML/PDF |
| **Crossref** | Publisher-maintained Elsevier record only; no OA license |
| **ScienceDirect** | Paywalled abstract page (`/science/article/abs/pii/S0939641114000411`) |
| **Ovid** | Full-text / PDF endpoints require login |
| **ResearchGate** | Publication page exists; network blocked security check (no public free PDF confirmed) |
| **Semantic Scholar API** | Rate-limited; no independent OA PDF found via web |
| **CORE / OpenAIRE / HAL / OSF / ResearchSquare / Zenodo** | No free PDF of this article found |
| **Google/web filetype:pdf** | Hits only cite the paper; no legal full-text host of the EJPB article |

### Author thesis (related, also not free)

| Item | Detail |
|---|---|
| Title | *Rheological investigation of manufacturability and injectability of highly concentrated monoclonal antibody formulations* |
| Author | Andrea Martina Allmendinger |
| Year | 2014 |
| Repo | University of Basel edoc: [entity 3408c644-…](https://edoc.unibas.ch/entities/publication/3408c644-0eee-43ce-a730-89e96b93b0d4) |
| DOI | 10.5451/unibas-006323607 |
| File | `PhD_Thesis_Andrea_Allmendinger_2014.pdf` (14.06 MB listed) |
| Access | **“Request a copy”** — not open download. Direct bitstream URL 404. |
| Note | Abstract states Chapter 3 = the EJPB 2014 model paper. Does **not** unlock a legal free full text of the journal article or of tabulated glycerol force data. |

### Publicly citable fragments only (not a full text; **not** Phase-D rows)

From abstract / publisher snippets / secondary citations (do **not** invent unstated table cells):

- Glycerol/water solutions used as Newtonian reference / surrogate liquids.
- Glide forces reported at volumetric flows of **0.5 mL/10 s**, **1 mL/10 s**, and **2 mL/10 s**.
- Example geometry in text/figures: **27G** needle with **R_needle = 0.109 mm** (for shear-rate profile at 1 mL/10 s).
- Water reference: **η_25°C = 0.89 mPa·s**, **ρ_25°C = 1 g/mL** (snippet for model illustration).
- Model includes **F_friction** term (plunger–barrel) added to hydrodynamic contribution.
- Protein solutions modeled with Carreau / power-law non-Newtonian form; Newtonian limit when n = 1.
- **No legally free table** of glycerol % × viscosity × needle × barrel × force was found.
- **No supplementary CSV** found on publisher, Unpaywall, or repositories.

### Phase-D from Allmendinger 2014

| Field | Available legally free? |
|---|---|
| Newtonian μ (+ T) | Partial snippet only (water 0.89 mPa·s at 25 °C); full glycerol panel not free |
| Measured needle ID + L | Snippet R_needle = 0.109 mm (27G); full table not free |
| Barrel ID | Not free |
| Volume / Q or t | Snippet rates 0.5 / 1 / 2 mL per 10 s only |
| Fluid-only force | **Not free** |
| **Complete Phase-D rows** | **0** |

---

## 2. Verwulgen et al. 2018 — FREE AUTHOR MANUSCRIPT

### Bibliographic identity

| Field | Value |
|---|---|
| Title | Assessment of Forces in Intradermal Injection Devices: Hydrodynamic Versus Human Factors |
| Authors | Stijn Verwulgen, Koen Beyers, Timothi Van Mulder, Thomas Peeters, Steven Truijen, Francis Dams, Vanessa Vankerckhoven |
| Journal | Pharm. Res. **35**:120 (2018) |
| DOI | [10.1007/s11095-018-2397-2](https://doi.org/10.1007/s11095-018-2397-2) |
| PMID | [29671074](https://pubmed.ncbi.nlm.nih.gov/29671074/) |

### Free legal PDF (author version)

| Field | Value |
|---|---|
| Host | University of Antwerp IRUA institutional repository |
| URL | **https://repository.uantwerpen.be/docman/irua/9e7a65/150639_2019_04_19.pdf** |
| Type | Archived peer-reviewed **author-version** (tracked-changes manuscript) |
| Handle | https://hdl.handle.net/10067/1506390151162165141 |
| License/status | Institutional repository author version (legal free full text) |
| Local download this hunt | Session path under downloads (`1.pdf`, 31 pages) |

### Exact published numbers extracted (quote only)

#### Syringe geometry

- Syringe: HSW Soft-Ject Low Dead Space Luer Lock, **1 mL**
- **Inner diameter of syringe d_s = 4.67 mm ± 0.03 mm** (calliper, accuracy 0.02 mm)
- Same syringe/plunger used for all experiments to minimize inter-syringe effects

#### Table I — Tested needles (measured and manufacturer’s parameters)

Quoted from author PDF Table I:

| Needle # | Brand | Gauge | Spec. diam. (mm) | Spec. length (mm) | Measured diam. (mm) | Measured length (mm) | Bevel length (mm) |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | BD | 26G | 0.26 | 10 | 0.269 | 15.651 | 1.49 |
| 2 | BD | 26G | 0.26 | 13 | 0.262 | 18.857 | 1.98 |
| 3 | BD | 26G | 0.26 | 16 | 0.256 | 22.290 | 1.90 |
| 4 | EXEL | 27G | 0.21 | 13 | 0.2160 | 19.424 | 1.81 |
| 5 | HSW FINE | 27G | 0.21 | 30 | 0.212 | 38.482 | 1.74 |
| 6 | HSW FINE | 27G | 0.21 | 40 | 0.208 | 44.411 | 1.77 |
| 7 | HSW FINE | 27G | 0.21 | 42 | 0.213 | 48.139 | 1.99 |
| 8 | HSW FINE | 27G | 0.21 | 50 | 0.210 | 56.369 | 1.95 |
| 9 | EXEL | 28G | 0.184 | 20 | 0.203 | 27.130 | 1.39 |
| 10 | EXEL | 30G | 0.159 | 13 | 0.158 (0.157*) | 22.299 | 1.39 |
| 11 | EXEL | 30G | 0.159 | 25 | 0.155 | 33.952 | 1.15 |
| 12 | TSK | 31G | 0.133 | 13 | 0.138 | 18.635 | 1.15 |
| 13 | TSK | 32G | 0.108 | 10 | 0.128 | 17.923 | 1.21 |
| 14 | TSK | 32G | 0.108 | 13 | 0.127 (0.130*) | 18.534 | 1.05 |
| 15 | TSK | 33G | 0.108 | 13 | 0.104 (0.105*) | 18.794 | 0.88 |

\*cross-check electron microscope

Notes from text:

- Needle length measured > manufacturer “spec length” because needles are prolonged internally in the hub (**5–10 mm**).
- Glycerol series used **needle #14** (32G, measured length 18.534 mm).

#### Table II — Friction force of plunger in empty syringe (subtracted for hydrodynamic force)

| Injection speed (mm/min) | Friction force (SD) in Newton |
|---:|---:|
| 50 | 0.561 (0.0722) |
| 125 | 0.766 (0.0932) |
| 175 | 0.829 (0.111) |
| 200 | 0.852 (0.115) |
| 250 | 0.902 (0.148) |
| 350 | 1.014 (0.154) |

Method: empty syringe; 10 repeats; Electromatic ESM301 power bench; force accuracy 0.2% (manufacturer).

#### Hydrodynamic / glycerol experimental design (exact quotes)

- **95 tests**, each with **5 repetitions**.
- **90 tests**: water. Temperature **15.4–18.5 °C**; viscosity corrected for temperature.
- **5 tests**: water–glycerol mixtures with viscosities **1.1 / 1.5 / 2.1 / 2.9 / 4.3 mPa·s**.
- Glycerol tests: **32G–13 mm** needle = **number 14** in Table I.
- All experiments: **d_s = 4.67 mm**; plunger speeds **v̄_s ∈ {50, 125, 175, 200, 250, 350} mm/min**.
- 15 needle types × 6 flow rates (water series).
- Newtonian behavior of water and water–glycerol confirmed on Rheosense device.
- Water–glycerol tested at lab temperature (**±20 °C**).
- Force due to pressure drop: **F_exp − F_fric** (friction subtracted).
- Entrance loss coefficient set **k_e = 1** for primary model; per-needle best-fit also evaluated.
- Model (Eq. 9–10) for plunger force from pressure drop + friction.

#### Table III — Per-needle regression of (F_exp − F_fric) vs F_s (k_e = 1)

| Needle # | d_n (mm) | l_n (mm) | Slope a | Intercept b (N) | R² | Δd_n (mm) |
|---:|---:|---:|---:|---:|---|---:|
| 1 | 0.270 | 15.7 | 0.70 | 0.033* | 99.8%*** | 0.024 |
| 2 | 0.262 | 18.9 | 0.63 | 0.031* | 94.5%*** | 0.032 |
| 3 | 0.256 | 22.3 | 0.81 | −0.030* | 80.9%*** | 0.014 |
| 4 | 0.216 | 19.2 | 0.57 | 0.152 | 97.9%*** | 0.032 |
| 5 | 0.212 | 38.4 | 0.93 | −0.056* | 97.3%*** | 0.004 |
| 6 | 0.209 | 44.6 | 0.91 | 0.043* | 98.4%*** | 0.005 |
| 7 | 0.213 | 48.0 | 1.08 | 0.008* | 99.8%*** | −0.004 |
| 8 | 0.210 | 56.7 | 1.21 | −0.043* | 99.9%*** | −0.010 |
| 9 | 0.203 | 27.1 | 0.55 | 0.002* | 99.9%*** | 0.030 |
| 10 | 0.157 | 22.3 | 1.18 | 0.650* | 99.7%*** | −0.007 |
| 11 | 0.155 | 34.0 | 1.00 | 0.050* | 99.9%*** | 0.000 |
| 12 | 0.138 | 18.6 | 0.64 | 0.088* | 100.0%*** | 0.016 |
| 13 | 0.13 | 17.9 | 0.77 | 0.166 | 99.8%*** | 0.009 |
| 14 | 0.130 | 18.5 | 0.95 | 0.118* | 99.8%*** | 0.002 |
| 15 | 0.105 | 18.8 | 0.96 | 0.023* | 100.0%*** | 0.001 |

\* intercept within 95% CI of 0 (t-distribution); *** significant at 0.001

Overall water regression (90 points, Fig. 4):

- **F_exp − F_fric = 0.91 F_s + 0.020 N**, R² = **95.5%**; intercept not significantly different from 0 (p = 0.70).

#### Glycerol viscosity series (Fig. 6 only — **no force table**)

- 5 data points, viscosities **1.1 / 1.5 / 2.1 / 2.9 / 4.3 mPa·s**, needle #14 (32G, L = 18.5 mm in Table III).
- Regression of measured (F_exp − F_fric) vs calculated F_s: **slope = 0.78**, **intercept = 0.10 N**, **R² = 99.7%**.
- **No tabulated absolute force (N) per viscosity × speed** in the free PDF. Values exist only as a scatter plot (Fig. 6); digits cannot be invented.

#### Viscosity figure (Fig. 3 — qualitative plateaus, not a numeric table)

- Water ≈ **1.1 mPa·s** (Newtonian plateau).
- **20% glycerol** ≈ **2 mPa·s** plateau.
- **30% glycerol** ≈ **2.9 mPa·s** plateau.
- HBVAXPRO vaccine: shear-thinning (non-Newtonian).

#### Human-operator force logs (Fig. 7)

- 10 untrained volunteers; eject **0.7 mL** saline; 26G and 32G; free air ejection (no tissue).
- Time-series force plots only — **not** Phase-D hydrodynamic validation rows.

### Supplementary CSV / publisher SI

- **None found** (no CSV, no separate SI data file with force×viscosity matrices on IRUA, PubMed, or Springer page via public links in this hunt).

### Phase-D assessment for Verwulgen

| Field | Present? | Notes |
|---|---|---|
| Newtonian μ (+ T) | **Partial** | Glycerol μ list 1.1–4.3 mPa·s; T ≈ 20 °C (±); water T 15.4–18.5 °C with μ correction |
| Measured needle ID + L | **Yes** | Table I / III; #14 for glycerol |
| Barrel ID | **Yes** | 4.67 ± 0.03 mm |
| Volume / Q or t | **Partial** | Speeds listed for design; glycerol “5 tests” not paired to a published Q matrix |
| Fluid-only force | **No tabulated values** | Friction subtracted in method; absolute F only in Fig. 4–6 (not tables) |
| **Complete Phase-D rows** | **0** | Cannot quote exact fluid-only force for each (μ, geometry, Q) without inventing figure digits |

**Closest partial panel:** geometry + friction + viscosity list for glycerol on needle #14 — still missing published absolute fluid-only force cells.

---

## 3. Other free glycerol / syringe-force leads checked

| Lead | Free? | Phase-D usable? |
|---|---|---|
| Krayukhina et al. 2020 tapered needle (J Pharm Sci) — glycerin forces | Fulltext exists on jpharmsci.org for some Elsevier OA; not the Allmendinger paper | Separate study; not harvested as Allmendinger SI |
| Shahriar et al. counterpressure (glycerol 50–95%) | Author PDF at pankajrohilla.com | Tissue counterpressure focus; not Allmendinger tables |
| Fischer et al. 2015 “Calculation of injection forces…” | Not free in this hunt | Related Roche/Allmendinger line; closed |
| Allmendinger thesis edoc.unibas.ch | Request-only | Not free |

No supplementary CSV of Allmendinger Newtonian glycerol + force + geometry was found anywhere legal.

---

## 4. Sources searched (aggressive checklist)

- Unpaywall API (correct DOI `10.1016/j.ejpb.2014.01.009`)
- PubMed / Europe PMC / PMC
- ScienceDirect, Ovid, Crossref
- ResearchGate, Semantic Scholar
- University of Basel edoc (thesis + publication list)
- University of Antwerp IRUA (**Verwulgen hit**)
- CORE, Google/web `filetype:pdf`, site-restricted edu/repo queries
- HAL / OSF / ResearchSquare / Zenodo (no hit for Allmendinger 2014 full text)
- Springer Pharm Res path for Verwulgen (author MS via IRUA)

---

## 5. Verdict for OpenInjectability Phase-D

| Metric | Count |
|---|---:|
| Free PDF found for **Allmendinger 2014** | **0** (no) |
| Free PDF found for **Verwulgen 2018** | **1** (yes) |
| Supplementary CSV with glycerol force + geometry | **0** |
| **Complete Phase-D rows** from this hunt | **0** |

**Recommendation:** Verwulgen IRUA PDF is the only legal free full text of the two targets. Use it for geometry + friction subtraction methodology and needle dimensional ground truth. For Phase-D absolute force validation, either (a) request Allmendinger 2014 / thesis via interlibrary loan or author, or (b) digitize Verwulgen Fig. 6 only if project policy later allows figure digitization (currently out of scope: “quote exact numbers only, never invent”).
