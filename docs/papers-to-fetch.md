# Papers to fetch (you upload next)

**Goal:** get **absolute** experimental numbers so we can build Phase D rows  
(without wet lab, without inventing data).

Each row we need:

| Field | Required |
|---|---|
| Newtonian viscosity + temperature | yes |
| Measured needle **inner diameter** + length | yes (not gauge-only) |
| Barrel inner diameter | yes |
| Volume + flow rate or injection time | yes |
| **Fluid-only** force or needle pressure (friction subtracted) | yes |

**Already free (no need to buy):**  
- Verwulgen 2018 — DOI `10.1007/s11095-018-2397-2`  
  Free PDF: https://repository.uantwerpen.be/docman/irua/9e7a65/150639_2019_04_19.pdf  
  We already extracted geometry + friction. **Missing:** absolute fluid-only force table (Fig. 6 only).

---

## Priority A — highest chance of usable force + geometry (get these first)

| # | DOI | Why |
|---:|---|---|
| 1 | **10.1016/j.ejpb.2014.01.009** | **Allmendinger 2014** — classic Newtonian glycerol + protein injection forces; HP model; **top target**. Also grab SI if any. |
| 2 | **10.5451/unibas-006323607** | Allmendinger PhD thesis (Basel) — may contain fuller tables than the journal paper. |
| 3 | **10.1007/s11095-018-2397-2** | Verwulgen 2018 — already free; if you have **publisher** PDF with higher-res figures / SI, upload that too (Fig. 4–6). |
| 4 | **10.1016/j.ejpb.2015.01.001** or search PMID **25537343** | Allmendinger tissue back-pressure related; check if SI has base fluid force without tissue. |
| 5 | Any Allmendinger paper with “injection forces” in title (PMID family **24560966**, **25537343**, **34102300**) | Same group; tables sometimes repeat glycerol baselines. |

## Priority B — open or semi-open injectability with force numbers (may be total glide)

Upload if you can; we will **reject total glide** unless friction is subtracted.

| # | DOI | Notes |
|---:|---|---|
| 6 | **10.1186/s40942-026-00832-3** | IVI syringe selection; force vs viscosity |
| 7 | **10.1186/s40942-026-00833-2** | Syringe/cannula time–force; SI may have tables |
| 8 | **10.1208/s12249-018-0963-x** | Zhang et al. injectability / work / DGF (often non-Newtonian polymers) |
| 9 | **10.1007/s42452-021-04767-2** | Microfluidic albumin injection flow (PMC8550001) — wrong geometry class but OA |
| 10 | **10.1371/journal.pone.0344836** | Subretinal flow/pressure model (PMC13004354) |

## Priority C — only if A/B lack tables

| # | DOI / ID | Notes |
|---:|---|---|
| 11 | **10.1016/j.xphs.2020.09.014** | Deokar et al. (PMC7491461) — total glide force, protein |
| 12 | **10.6084/m9.figshare.32195520.v1** | Figshare XLSX IVI force (tissue + total effort) |
| 13 | **10.6084/m9.figshare.20800108.v1** | Figshare SI delivery times vs viscosity |

---

## What to upload (next message)

For each paper you get, best is:

1. **Full PDF**  
2. **Supplementary** CSV/XLS/PDF if present  
3. Optional: screenshots of tables if PDF is image-only  

Name files clearly, e.g.:

```text
allmendinger_2014_ejpb.pdf
allmendinger_2014_si.pdf
verwulgen_2018_publisher.pdf
```

## What we will do after you upload

1. Extract **only** numbers that appear in the files.  
2. Build `validation/experimental/panel_literature_*.json` with citations.  
3. Run `openinjectability validate-experimental …`  
4. Still refuse `independently_validated` until the panel meets the protocol bar.

---

## Minimum successful fetch

If you can only get **one** paper, get:

### **DOI 10.1016/j.ejpb.2014.01.009** (Allmendinger 2014) + any SI
