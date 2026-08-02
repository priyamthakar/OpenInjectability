# Literature scrape assessment for Phase D (2026-08-02)

## Request

Obtain independent experimental data for Phase D validation without a lab
collaborator, by scraping public literature if needed.

## Protocol bar (must all hold)

From [validation-protocol-lock.md](validation-protocol-lock.md):

- Newtonian fluid with measured dynamic viscosity and temperature
- Traceable needle **inner diameter** and length (not gauge-only)
- Barrel inner diameter
- Volume and flow rate or injection time
- Measured **fluid-side** force or pressure (friction-separated or pressure transducer)
- Development fixtures must not be reused as the “experimental” set
- No invented numbers; no silent correction factors

## PubMed / PMC scrape (2026-08-02, no fabrication)

**Yes, PubMed can be searched programmatically** (and we did):

| Channel | What we used | Artifact |
|---|---|---|
| EuropePMC REST | Open-access title/abstract + full-text XML | `scripts/pubmed_scrape_probe.py`, `scripts/pubmed_scrape_narrow.py`, `docs/pubmed-scrape-probe.json`, `docs/pubmed-scrape-candidates.json` |
| NCBI E-utilities | PubMed free-full-text filter | `scripts/pubmed_esearch.py`, `docs/pubmed-esearch.json` |

### Hit counts (real API results)

| Query theme | Hits |
|---|---:|
| OA: (glide force OR injection force OR injectability) + viscosity + needle | **319** |
| OA: glycerol/glycerin/newtonian + injection/glide force + needle/syringe | **15** |
| OA: Hagen–Poiseuille + injection/glide force + syringe | **6** |
| OA: friction + glide/injection force + viscosity + needle | **0** |
| PubMed free full text: injection/glide force + viscosity + glycerol/newtonian | **4** |

### Full-text XML screen (15 OA candidates)

Automated flags on EuropePMC fullTextXML (needle ID, barrel, flow, friction, Hagen, Newtonian):

- **Almost all** are hydrogel / in-situ gel / cement / dental / cancer injectables — wrong product class for Phase D.
- **Zero** papers in this OA panel published a complete machine-readable panel of  
  \(\mu\), measured needle \(d\), \(L\), barrel \(D_b\), \(Q\) or \(t\), and **fluid-only** force/pressure.
- Near-miss example: PMC8550001 (*microfluidic* BSA “syringe-on-chip”) — microfluidic geometry, not a clinical needle+barrel validation panel; not usable as Phase D rows without overclaiming.
- PubMed free-full-text glycerol/newtonian filter returned only 4 PMIDs, all gels/microfluidics, not friction-corrected needle fluid resistance.

### What PubMed scrape *can* and *cannot* do

| Can | Cannot |
|---|---|
| Find open-access papers and PMC full text legally | Invent missing needle ID / friction-free force |
| Cite DOI/PMCID and quote published tables when complete | Treat total glide force as \(F_f\) |
| Feed a future literature registry of *candidates* | Unlock `independently_validated` without the protocol bar |

## What was searched (earlier web pass)

Public / open sources reviewed (representative):

| Source | What it reports | Usable for Phase D? |
|---|---|---|
| Deokar et al., *J Pharm Sci* 2020 (PMC7491461) | Viscosity + total glide/break-loose force for high-concentration IgG1 in 27G TW ½″ PFS; extension rate given | **No** — total injection/glide force includes friction; protein formulations often non-Newtonian; needle ID not independently tabulated as measured ID |
| Zhang et al., *AAPS PharmSciTech* 2018 | Total work / DGF / Fmax for HPMC & PEO; barrel Ø 9 & 13 mm; 18G/21G bore stated | **No** — polymers are non-Newtonian; metric is total work/force, not fluid-only force |
| RheoSense app notes (public PDFs) | Theory for viscous force component; state friction is separate and highly variable | **No experimental panel** — equations only (aligns with our model; not independent experiment) |
| Verwulgen et al. (ID injection devices; institutional PDF snippets) | Water–glycerol Newtonian mixtures; friction subtraction mentioned; needle gauges | **Incomplete for reuse** — full row-level geometry + force table not freely available as a citable, complete machine-readable dataset in the scrape |
| Allmendinger et al., *Eur J Pharm Biopharm* 2014 | Classic HP vs measured forces for Newtonian + protein | **Paywalled / not fully extractable** here as complete open tabular inputs+outputs |

## Scientific reason scrape ≠ Phase D

OpenInjectability predicts **only** idealized needle **fluid-resistance force**
\(F_f = 32 \mu L Q D_b^2 / d^4\).

Published **glide force / injection force / total work** almost always include:

- stopper–barrel friction and break-loose,
- device losses,
- sometimes tissue/backpressure (in vivo).

Therefore:

\[
F_{\mathrm{glide}} = F_f + F_{\mathrm{friction}} + \cdots \ge F_f
\]

Comparing our model directly to scraped glide-force tables would:

1. systematically **under-predict** total force (expected bias, not a model bug),
2. **fail the protocol** (wrong measurand),
3. risk a false “validation” claim if `validation_status` were advanced.

This is why the project deliberately excludes friction and refuses to label the
result “total injection force.”

## What was **not** done (correctly)

- Did **not** invent viscosity/geometry/force rows to fill gaps.
- Did **not** treat internal hand-calculated fixtures as experimental validation.
- Did **not** set `validation_status` to `independently_validated`.
- Did **not** scrape private or behind-login lab repositories.
- Did **not** digitize incomplete figures as if they were measured fluid-only forces.

## Minimal dataset that *would* unblock Phase D

For each row, all of:

1. Fluid identity + measured \(\mu\) (Pa·s) at stated temperature + Newtonian attestation  
2. Measured needle ID \(d\) (mm) and length \(L\) (mm) with source  
3. Measured barrel ID \(D_b\) (mm) with source  
4. \(Q\) or \(t\) and \(V\)  
5. \(F_{\mathrm{exp}}\) defined as **fluid resistance only** (e.g. pressure drop × barrel area, or glide force minus empty-syringe friction measured on the same hardware)  
6. Citation DOI + table/figure ID + access date  

Acceptable sources: open supplementary CSV/XLS from a paper that already
separates hydrodynamic contribution; or a public repository dataset with the
fields above; or a short benchtop campaign (glycerol–water + pressure transducer).

## Interim product status

| Item | Status |
|---|---|
| Phases A–C software | Complete (`v0.1.0`) |
| Phase D experimental validation | **Still blocked** — no compliant open dataset found by scrape |
| Phase E public “validated” claim | Blocked on D |
| `validation_status` | Remains `internal_validation; experimental_validation_pending` |

## Recommended next actions (human)

1. **Cheapest path:** one afternoon of glycerol–water runs with a traceable needle, measured ID, load cell, and empty-syringe friction baseline; log rows in the schema above.  
2. **Literature path:** obtain full text + SI of a paper that publishes friction-corrected hydrodynamic force (not total glide force) and digitize only complete rows.  
3. **Do not** publish OpenInjectability as experimentally validated from total-force tables.

## Hash note

This document is the durable record of the 2026-08-02 scrape decision. Any
future accepted dataset must be versioned separately under
`validation/experimental/` with its own SHA-256 manifest and must not reuse
`tests/reference_data/reference_case.json` as experimental evidence.
