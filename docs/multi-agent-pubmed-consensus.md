# Multi-agent PubMed / open-data consensus (2026-08-02)

Four agents ran in parallel. **No experimental numbers were fabricated.**

| Agent | Focus | Artifact |
|---|---|---|
| EuropePMC deep OA search | 25 REST queries, 305 unique OA records | [agent-epmc-deep-search.md](agent-epmc-deep-search.md) |
| Full-text table extraction | 8 PMC fullTextXML papers, all tables scored | [agent-fulltext-tables.md](agent-fulltext-tables.md) |
| Open dataset repositories | Zenodo, DataCite, Dryad, Figshare | [agent-open-datasets.md](agent-open-datasets.md) |
| PubMed eutils batch | 4 free-full-text queries + elink to PMC | [agent-pubmed-batch.md](agent-pubmed-batch.md) |

## Consensus verdict

**Phase D remains blocked.** No open PubMed/PMC paper or public repository dataset supplies a complete, citable panel of:

1. measured viscosity (+ temperature) for a **Newtonian** fluid  
2. measured needle **inner diameter** and length (not gauge-only)  
3. barrel inner diameter  
4. volume + flow rate or injection time  
5. **fluid-only** force or pressure (friction-separated)

## Key evidence by agent

### EuropePMC
- 319 OA injectability/force hits; 15 glycerol/Newtonian+force; **0** OA “empty-syringe friction baseline” hits.
- Classic **Allmendinger 2014** (PMID 24560966) is the best *literature target* but **paywalled / no PMCID**.

### Full-text tables (8 papers)
- **0 usable Phase-D rows.**
- Nearest miss **PMC7491461**: viscosity + total glide force + 27G TW — missing measured ID, barrel ID; force includes friction; protein not Newtonian-validated for our model.
- **PMC13004354**: water + cannula D/L + pressure — multi-segment network, not syringe barrel fluid-resistance panel.

### Repositories
- Figshare near-misses exist (IVI force XLSX, PEG viscosities) but: tissue/total force, gauge-only, or no \(F_f\).
- Zenodo/Dryad: **no** complete μ–geometry–\(F_{\mathrm{fluid}}\) deposit found.

### PubMed free full text
- 24 unique free-full-text PMIDs across four systematic queries.
- Allmendinger free-full-text hits are **unrelated** papers; classic force paper stays abstract-only.
- **No** free-full-text title certifies friction-corrected needle fluid force.

## What multi-agent scrape proves

| Claim | Supported? |
|---|---|
| PubMed/PMC can be searched at scale | **Yes** |
| Open injectability literature is large | **Yes** (hundreds of OA hits) |
| That literature contains Phase-D panels | **No** (wrong measurand / incomplete geometry / wrong fluid) |
| We should advance `validation_status` | **No** |

## Honest unblock paths (unchanged)

1. Benchtop glycerol–water + measured ID + empty-syringe friction baseline.  
2. Licensed SI of a paper that already publishes friction-corrected hydrodynamic force with full geometry.  
3. Do **not** treat total glide-force tables as validation of predicted fluid-resistance force.
