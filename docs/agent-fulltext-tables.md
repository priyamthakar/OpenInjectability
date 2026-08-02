# Agent full-text table extraction (EuropePMC)

**Date:** 2026-08-02  
**Source:** `https://www.ebi.ac.uk/europepmc/webservices/rest/{PMCID}/fullTextXML`  
**Machine-readable twin:** [agent-fulltext-tables.json](agent-fulltext-tables.json)

## Rules (enforced)

- Quote only published table/method content.
- Never invent or estimate missing geometry or force.
- Never convert gauge → ID from undocumented tables.
- A **COMPLETE Phase-D row** requires *all* of: Newtonian μ (+ T), measured needle ID + length, barrel ID, volume + Q or t, and **fluid-only** force/pressure.

## Summary

| Metric | Value |
|---|---:|
| Papers screened | **8** |
| Priority PMCIDs | 7 |
| Expanded from `pubmed-scrape-candidates.json` | 1 (`PMC12843089`) |
| **Usable Phase-D rows** | **0** |

**Verdict:** No paper yielded a complete Phase-D validation row from published numbers alone.

---

## Papers

### 1. PMC8550001 — REJECT

| Field | Value |
|---|---|
| Title | A microfluidic approach to studying the injection flow of concentrated albumin solutions |
| DOI | [10.1007/s42452-021-04767-2](https://doi.org/10.1007/s42452-021-04767-2) |
| Tables | 1 |

**Table 1 — The details of “syringe-on-chip” flow geometries** (as published numbers)

| Flow cell | w_c (μm) | w_t (μm) | d (μm) | L_c (μm) | H | ε_H |
|---|---:|---:|---:|---:|---:|---:|
| 26G | 800 | 47 | 50 | 20 | 17.02 | 2.83 |
| 27G | 800 | 38 | 50 | 20 | 21.05 | 3.05 |

**Score:** viscosity ✗ · needle ID (circular, clinical) ✗ · length (clinical) ✗ · barrel ✗ · flow ✗ · fluid force ✗

**Missing:** Clinical circular needle ID/length; barrel of delivery syringe under test; plunger fluid force; paired μ–force panel.  
**Why:** Planar microfluidic “syringe-on-chip” contractions *labeled* 26G/27G; paper states real syringes are axisymmetric, not planar.

---

### 2. PMC7491461 — REJECT (nearest force+viscosity miss)

| Field | Value |
|---|---|
| Title | Comparison of Strategies in Development and Manufacturing of Low Viscosity, Ultra-High Concentration Formulation for IgG1 Antibody |
| DOI | [10.1016/j.xphs.2020.09.014](https://doi.org/10.1016/j.xphs.2020.09.014) |
| Tables | 6 (Table 2 is injection-relevant) |

**Method (published quotes)**

- Viscosity: Lovis 2000 M/ME rolling-ball micro-viscometer (Anton Paar); values at 25 °C in Table 2.
- Force: UTM LS-1 (Lloyds), 20 N load cell; “friction test” compression; preload 0.5 N @ 21 mm/min; test speed **100 mm/min** up to 26 mm.
- Device: EZ Fill™ **1 mL** USP type 1 glass syringes with **27 Gauge, thin wall** staked needle, **½ inch** length, 3 bevels (Nuova Ompi P/N 7600001.7439).

**Table 2 excerpt — Viscosity and Injection Forces (published)**

| Excipient | Viscosity (cps @ 25 °C) | Glide Force (N) | Break-Loose Force (N) |
|---|---:|---:|---:|
| IgG1 DS ~200 mg/mL (NIL) | 21.9 | 9.5 | 5.5 |
| Arginine HCl 54.7 mg/mL | 16.7 | 3.8 | 3.0 |
| Ammonium chloride 13.9 mg/mL | 13.4 | 4.5 | 2.3 |
| Sodium chloride 15.2 mg/mL | 15.0 | 5.4 | 2.7 |
| Magnesium chloride 25 mg/mL | 19.9 | 5.3 | 2.5 |
| Calcium chloride 14.4 mg/mL | 11.1 | 4.8 | 2.6 |
| Glycine 9.8 mg/mL | 13.6 | 4.2 | 5.0 |
| Proline 15 mg/mL | 11.3 | 5.7 | 5.1 |

**Score:** viscosity ✓ · needle ID measured ✗ (gauge only) · length ✓ · barrel ID ✗ · flow/rate ✓ (extension rate) · force ✓ · **fluid-only force ✗**

**Missing for Phase-D**

1. `needle_id_mm` — only “27 Gauge thin wall”; no measured ID (gauge→ID forbidden).  
2. `barrel_id_mm` — 1 mL EZ Fill only; ID not published.  
3. Newtonian evidence — high-concentration IgG1; not established Newtonian.  
4. Fluid-only force — published Glide / Break-Loose are **total** UTM forces (friction included).

---

### 3. PMC7952281 — REJECT

| Field | Value |
|---|---|
| Title | Container Closure and Delivery Considerations for Intravitreal Drug Administration |
| DOI | [10.1208/s12249-021-01949-4](https://doi.org/10.1208/s12249-021-01949-4) |
| Tables | 5 |

**Table III — Needle Gauge Dimensions from ISO 9626:2016 (Minimum inner diameters)** (published)

| Needle gauge | Regular-wall ID (mm) | Thin-wall ID (mm) | Extra-thin-wall ID (mm) | Ultra-thin-wall ID (mm) |
|---:|---:|---:|---:|---:|
| 30 | 0.133 | 0.165 | 0.190 | 0.240 |
| 32 | 0.089 | 0.105 | 0.125 | 0.146 |

Other tables: approved IVT implants / formulations (catalog), sterilization materials, clinical pipeline — **no experimental μ + geometry + force panel**.

Body discusses Hagen–Poiseuille glide-force equation including **F_friction**, but provides no measured validation rows.

**Missing:** Experimental viscosity, measured needle/barrel geometry under test, flow, fluid-only force.

---

### 4. PMC11717134 — REJECT

| Field | Value |
|---|---|
| Title | In Vitro Analysis of Pressure Resistance in the Paul Glaucoma Implant and Ahmed ClearPath With and Without Polypropylene Thread Restriction |
| DOI | [10.1167/tvst.14.1.2](https://doi.org/10.1167/tvst.14.1.2) |
| Tables | 4 |

**Published experimental context**

- Fluid: **0.9% physiological saline** via syringe pump at **1.0–5.0 µL/min**.
- Measurand: **tube pressure** (mm Hg) of glaucoma drainage device (GDD) lumens ± polypropylene thread.
- Theory: Hagen–Poiseuille / annular-tube variants vs measured pressures (Tables 1, 3, 4).
- Table 2: lumen / thread cross-sectional areas (A, A′, ΔA) — units as published in article table cells.

**Table 1 excerpt — Measured pressures (mm Hg context from body)**

| Flow (µL/min) | PGI (−) | PGI (+) | ACP (−) | ACP (+4) | ACP (+3) |
|---:|---:|---:|---:|---:|---:|
| 1.0 | 0.7 ± 0.4 | 7.5 ± 0.5 | 0.6 ± 0.2 | 2.2 ± 0.8 | 3.3 ± 0.7 |
| 5.0 | 2.3 ± 0.5 | 43.8 ± 8.7 | 1.1 ± 0.3 | 3.1 ± 1.1 | 6.4 ± 0.8 |

**Score:** flow ✓ · pressure ✓ · viscosity value tabulated ✗ · clinical needle+barrel ✗ · plunger force ✗

**Missing:** Published μ (+ T) used in HP; delivery needle ID/length as resistance element (GDD tube is the resistance); barrel ID; F_f.

---

### 5. PMC12113853 — REJECT

| Field | Value |
|---|---|
| Title | Microfluidic Chip for Quantitatively Assessing Hemorheological Parameters |
| DOI | [10.3390/mi16050567](https://doi.org/10.3390/mi16050567) |
| Tables | 1 |

**Table 1** — variables for X_esr / ESR (t0, t1, Q_sp = 5.0 mL/h, etc.). Blood hemorheology chip; HP used to get blood viscosity — **not** syringe injection force.

**Missing:** Needle/barrel injection geometry; fluid-only injection force; Newtonian syringe panel.

---

### 6. PMC13004354 — REJECT (strongest geometry+μ+pressure near-miss)

| Field | Value |
|---|---|
| Title | A theoretical and experimental model of flow characteristics in subretinal injections |
| DOI | [10.1371/journal.pone.0344836](https://doi.org/10.1371/journal.pone.0344836) |
| Tables | 3 |

**Published fluid**

- “Water with **μ = 0.001 Pa·s** was used for the analysis.”
- Table 2 caption: “water solution (**1 mPa.s**)”.

**Table 1 — D, L, R_hyd (published)**

| Component | D ×10⁻³ [m] | L ×10⁻³ [m] | R_hyd ×10¹² [Pa·s/m³] |
|---|---:|---:|---:|
| Distal polyamide Model 3219 | 0.071 | 5 | 8.02 |
| Distal polyamide Model 3255 | 0.071 | 2 | 3.21 |
| Proximal needle 3219/3255 | 0.26 | 35 | 0.31 |
| Extension tube Model 3223 | 0.5 | 150 | 0.10 |

**Table 2 — Q (µL/s) vs injection pressure setting (psi)** (published)

| Cannula | 6 | 8 | 10 | 12 | 14 | 16 | 18 | 20 psi |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 5 mm / 41g polyamide tip (3219) | 0.82 | 2.45 | 4.09 | 5.73 | 7.36 | 9.00 | 10.64 | 12.27 |
| 2 mm / 41g polyamide tip (3255) | 1.91 | 5.72 | 9.53 | 13.34 | 17.16 | 20.97 | 24.78 | 28.60 |
| 0.6 mm / 51g metal tip (3263) | 0.17 | 0.51 | 0.86 | 1.20 | 1.54 | 1.89 | 2.23 | 2.57 |

**Also published:** ΔP = P − P_min with **P_min** = minimum air pressure to overcome **static friction** between piston and cylinder; multi-segment R_hyd series network; 1 mL Microdose Injector (barrel ID **not** tabulated).

**Score:** viscosity ✓ · needle/cannula ID ✓ · length ✓ · barrel ID ✗ · flow ✓ · pressure settings ✓ · **fluid-only plunger force ✗** · single simple needle schema ✗

**Missing for Phase-D:** barrel ID; friction-free fluid force/pressure panel; temperature for μ; single-needle OpenInjectability row (network of VFI + extension + multi-section cannula).

---

### 7. PMC9085397 — REJECT

| Field | Value |
|---|---|
| Title | A simple capillary viscometer based on the ideal gas law |
| DOI | [10.1039/c8ra06006a](https://doi.org/10.1039/c8ra06006a) |
| Tables | 1 |

**Published initial values (excerpt)**

| Sample | Temp (°C) | Known viscosity (10⁻³ Pa·s) | … capillary geometry … |
|---|---:|---:|---|
| Water | 24 | 0.9107 | L_c, r_c etc. published for water row |
| Glycerin 30% | 25 | 2.5748 | partial |
| Glycerin 40% | 26 | 4.1971 | partial |

**Why reject:** Capillary viscometry (measures μ), not syringe injection force / barrel / needle delivery force.

---

### 8. PMC12843089 — REJECT (expanded candidate)

| Field | Value |
|---|---|
| Title | Beyond Strict Physics: Using Poiseuille’s Law as a Practical Framework to Optimize and Personalize Cementoplasty |
| DOI | [10.3390/jpm16010041](https://doi.org/10.3390/jpm16010041) |
| Tables | 2 (Table 1 + symbol glossary) |

**Table 1 — Relative flow rate r⁴/L vs gauge/length (theoretical)**

| Trocar | Length (cm) | Internal radius (mm) | Relative Q vs 13G 15 cm |
|---|---:|---:|---:|
| 8 G | 10 | 1.19 | 11.19 |
| 8 G | 15 | 1.19 | 7.46 |
| 11 G | 10 | 1.00 | 5.58 |
| 11 G | 15 | 1.00 | 3.72 |
| 13 G | 10 | 0.72 | 1.50 |
| 13 G | 15 | 0.72 | 1.00 * |
| 18 G | 9 | 0.41 | 0.18 |

Authors state bone cement is **non-Newtonian** and that Poiseuille is only a didactic framework, not predictive.

**Missing:** Newtonian μ, experimental force/pressure, barrel ID, measured validation panel.

---

## Cross-paper score card

| PMCID | μ | Needle ID meas. | Needle L | Barrel ID | Q/t | Force/P | Fluid-only F | Phase-D |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|---|
| PMC8550001 | ~ | ✗ micro | ✗ | ✗ | partial | ΔP chip | n/a | **REJECT** |
| PMC7491461 | ✓ | ✗ gauge | ✓ ½″ | ✗ | rate ✓ | total glide ✓ | ✗ | **REJECT** |
| PMC7952281 | ✗ | ISO mins only | ✗ | ✗ | ✗ | ✗ | ✗ | **REJECT** |
| PMC11717134 | not tabulated | GDD lumen | GDD | ✗ | ✓ | tube P ✓ | n/a | **REJECT** |
| PMC12113853 | blood/chip | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | **REJECT** |
| PMC13004354 | water 1 mPa·s | ✓ cannula | ✓ | ✗ | model Q | machine psi | ✗ (P_min friction) | **REJECT** |
| PMC9085397 | known μ | capillary r | capillary L | ✗ | ✗ | ✗ | ✗ | **REJECT** |
| PMC12843089 | ✗ | mfr radius | ✓ | ✗ | relative only | ✗ | ✗ | **REJECT** |

## Usable Phase-D rows

**None (zero).**

No complete row of  
μ (+ T, Newtonian) · measured needle *d* · *L* · barrel *D_b* · *Q* or *t* · fluid-only force/pressure  
can be built from these OA full texts without fabrication or undocumented gauge→ID conversion.

## Implications (no status change)

- Confirms literature path remains blocked without a paper that publishes **friction-separated** hydrodynamic force (or needle ΔP + measured barrel area) for a **Newtonian** fluid with **measured** needle ID.
- Nearest future leads (still incomplete as extracted):  
  - PMC7491461-class PFS glide-force studies **if** SI published measured ID, barrel ID, empty-syringe friction baseline, and Newtonian fluid.  
  - PMC13004354-class pressure-driven cannula studies **if** barrel ID + friction-free ΔP and single-segment geometry are published.

## Artifacts

| File | Role |
|---|---|
| `docs/agent-fulltext-tables.json` | Structured extraction + decisions |
| `docs/agent-fulltext-tables.md` | This report |
| `docs/_fulltext_xml/*.xml` | Cached EuropePMC fullTextXML |
| `docs/_table_extract_preview.json` | Intermediate parser dump |
| `docs/_extract_tables.py` | Table extraction helper |
