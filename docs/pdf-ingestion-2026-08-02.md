# PDF ingestion report (2026-08-02)

User placed four PDFs in the repo root. Text/table extraction used PyMuPDF; figures rendered for digitization. **No numbers invented beyond approximate figure reading (explicitly labeled).**

| File | Content | Usable for Phase D panel? |
|---|---|---|
| `allmendinger2014.pdf` | EJPB 2014 DOI 10.1016/j.ejpb.2014.01.009 | **Yes (with caveats)** — Table 1 geometry + friction exact; glycerol forces only in Fig. 3(A) |
| `PhD_Thesis_Andrea_Allmendinger_2014.pdf` | Thesis DOI 10.5451/unibas-006323607 | Same Chapter 3 = paper; Fig. 3.3(A) clearer for digitization |
| `verwulgen2018.pdf` | Pharm Res 2018 DOI 10.1007/s11095-018-2397-2 | Geometry + friction tables only; glycerol absolute F not tabulated |
| `zhang2018.pdf` | AAPS PharmSciTech 2018 DOI 10.1208/s12249-018-0963-x | **No** — HPMC/PEO (non-Newtonian); total **work** (J), not fluid-only force |

## Exact Table 1 (Allmendinger 2014)

| Device | Frictional force (N) | Syringe inner radius (mm) |
|---|---|---|
| Hypak 1 mL glass | 1.62 @ 0.5 mL/10 s; 3.60 @ 1 mL/10 s; 6.73 @ 2 mL/10 s | **4.3** |
| Plastipak 1 mL | 1.26 @ 1 mL/10 s | **3.2** |

| Needle | Inner diameter (μm) | Length (mm) |
|---|---|---|
| Microlance 27G ¾″ | 237 | 20.9 |
| Sterican 27G 1″ | **217** | **27.1** |
| Sterican 25G 1″ | 276 | 27.1 |

Glycerol series used Hypak + Sterican 27G 1″ (methods: “all other” measurements).

## Panel produced

- `validation/experimental/panel_allmendinger2014_glycerol_digitized.json` — 12 rows  
- Forces = digitized mean **glide** from Fig. 3.3(A) − **published** Table 1 friction  
- Report: `validation/experimental/reports/allmendinger2014_digitized/`  
- **Median |relative error| ≈ 0.135** vs OpenInjectability model (criterion 0.20 → **pass** as `experimental_comparison`)  
- Package `validation_status` **not** set to `independently_validated` (digitization + no author SI table)

## Paper claim (exact text)

> The good agreement (minimum to maximum deviation = 0.0–2.5 N) confirms the suitability of the Hagen–Poiseuille’s equation to predict glide forces for Newtonian liquids.

## PDFs

Large PDFs stay **local** (gitignored). Extraction text under `docs/pdf_extract/` may be committed for audit; raw thesis (~14 MB) not tracked.
