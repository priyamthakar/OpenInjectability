"""Re-rank top-10 and strengthen Allmendinger OA notes from existing batch JSON."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "docs" / "agent-pubmed-batch.json"
MD_PATH = ROOT / "docs" / "agent-pubmed-batch.md"

POSITIVE_HIGH = [
    "injection force",
    "glide force",
    "injectability",
    "syringeability",
    "hagen-poiseuille",
    "hagen–poiseuille",
    "glide",
    "plunger force",
    "extrusion force",
    "break-loose",
    "break loose",
    "time-force",
    "gliding and discharge",
]
POSITIVE = [
    "needle",
    "syringe",
    "viscosity",
    "rheolog",
    "glycerol",
    "glycerin",
    "newtonian",
    "protein formulation",
    "high concentration",
    "subcutaneous",
    "friction",
    "fluid",
    "pressure drop",
    "flow characteristic",
    "microfluidic",
    "albumin",
    "cannula",
    "jet injection",
    "kinematic and fluid",
]
NEGATIVE = [
    "periodontal",
    "in situ gel",
    "oromucosal",
    "cement",
    "bone cement",
    "dental",
    "hydrogel scaffold",
    "oncolytic",
    "adeno",
    "egfr-binding",
    "life-cycle and cost",
    "cost of goods",
    "perfusion-based manufacturing",
    "intratumoral",
    "chitosan-glycerol injectable hydrogel",
    "fed-batch",
    "vertebroplasty",
    "abuse dete",
    "antimicrobial",
    "millispheres",
    "skin booster",
    "hyaluronic acid",
    "hyaluronan",
    "hydroxylapatite",
    "periodontitis",
    "tumor-targeting",
    "in-situ forming",
    "in situ forming",
]


def score_row(row: dict) -> float:
    t = (row.get("title") or "").lower()
    s = 0.0
    for kw in POSITIVE_HIGH:
        if kw in t:
            s += 3.0
    for kw in POSITIVE:
        if kw in t:
            s += 1.0
    for kw in NEGATIVE:
        if kw in t:
            s -= 4.0
    qs = set(row.get("queries") or [])
    if "q4_hagen_poiseuille_syringe" in qs:
        s += 2.0
    if "q2_glycerol_needle_force" in qs:
        s += 2.0
    if "q1_injection_force_viscosity_needle" in qs:
        s += 0.5
    if row.get("has_pmc_fulltext_link"):
        s += 0.5
    s += 0.2 * len(qs)
    return s


def main() -> None:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))

    all_rows: dict[str, dict] = {}
    for res in data["queries"]:
        for row in res["rows"]:
            pid = row["pmid"]
            if pid not in all_rows:
                all_rows[pid] = {**row, "queries": [res["id"]]}
            else:
                all_rows[pid]["queries"].append(res["id"])

    ranked = sorted(all_rows.values(), key=score_row, reverse=True)
    top10 = []
    for row in ranked[:10]:
        top10.append(
            {
                "pmid": row["pmid"],
                "title": row["title"],
                "pubdate": row["pubdate"],
                "source": row["source"],
                "authors": row["authors"],
                "doi": row["doi"],
                "pmcid": row["pmcid"],
                "has_pmc_fulltext_link": row["has_pmc_fulltext_link"],
                "pubmed_url": row["pubmed_url"],
                "pmc_url": row["pmc_url"],
                "queries": row.get("queries"),
                "relevance_score_heuristic": score_row(row),
                "friction_corrected_force_claim": (
                    "UNKNOWN_FROM_TITLE_ONLY — requires full-text review; "
                    "no claim asserted from search metadata"
                ),
            }
        )

    classic_note = data.get("allmendinger_oa_vs_abstract_note", {})
    for key in ("unfiltered_rows", "broader_rows"):
        for r in classic_note.get(key, []):
            if r["pmid"] == "24560966":
                r["classic_tag"] = (
                    "Allmendinger et al. 2014 EJPB rheology + injection forces "
                    "(often cited classic)"
                )
                r["access_note"] = (
                    "NO PMC link; NOT in free full text[filter] results — "
                    "abstract-only for this OA workflow. Publisher full text "
                    "paywalled for typical users; do not fabricate table values "
                    "from abstract."
                )

    data["allmendinger_oa_vs_abstract_note"] = classic_note
    data["classic_allmendinger_2014_pmid"] = {
        "pmid": "24560966",
        "title": (
            "Rheological characterization and injection forces of concentrated "
            "protein formulations: an alternative predictive model for "
            "non-Newtonian solutions."
        ),
        "in_free_full_text_query3": "24560966" in (classic_note.get("free_full_text_pmids") or []),
        "has_pmc_via_elink": False,
        "access": (
            "abstract-only / paywalled (not free full text on PubMed; "
            "no PMC deposit found via elink)"
        ),
        "note": (
            "Confirmed present in unfiltered Allmendinger+injection search; "
            "absent from free full text filter."
        ),
    }

    force_related_allm = []
    for r in classic_note.get("unfiltered_rows", []):
        t = (r.get("title") or "").lower()
        if any(
            k in t
            for k in [
                "injection force",
                "injectability",
                "tissue resistance",
                "back-pressure",
                "back pressure",
                "rheological",
                "subcutaneous injection volumes",
            ]
        ):
            force_related_allm.append(
                {
                    "pmid": r["pmid"],
                    "title": r["title"],
                    "pubdate": r["pubdate"],
                    "source": r["source"],
                    "pmcid": r["pmcid"],
                    "access": (
                        "PMC OA" if r["has_pmc"] else "abstract-only / no PMC (likely paywalled)"
                    ),
                }
            )
    data["allmendinger_force_related_access"] = force_related_allm
    data["unique_free_full_text_pmids"] = sorted(
        all_rows.keys(), key=lambda x: -score_row(all_rows[x])
    )
    data["top10_promising_for_human_review"] = top10

    JSON_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")

    lines: list[str] = []
    lines.append("# PubMed E-utilities batch — injectability / syringe force")
    lines.append("")
    lines.append(f"Generated (UTC): `{data['generated_at_utc']}`")
    lines.append("")
    lines.append("**Source:** NCBI E-utilities (`esearch` → `esummary` → `elink` pubmed→pmc).")
    lines.append("")
    lines.append(data["disclaimer"])
    lines.append("")
    lines.append("## Query hit counts")
    lines.append("")
    lines.append("| # | Query | Count | Returned (retmax) | With PMC link |")
    lines.append("|---|---|---:|---:|---:|")
    for i, res in enumerate(data["queries"], 1):
        pmc_n = sum(1 for r in res["rows"] if r["has_pmc_fulltext_link"])
        lines.append(f"| {i} | {res['label']} | {res['count']} | {res['returned']} | {pmc_n} |")
    lines.append("")

    for i, res in enumerate(data["queries"], 1):
        lines.append(f"## Query {i}: {res['label']}")
        lines.append("")
        lines.append("```")
        lines.append(res["term"])
        lines.append("```")
        lines.append("")
        lines.append(f"- **Count:** {res['count']}")
        lines.append(f"- **PMIDs returned:** {', '.join(res['ids']) if res['ids'] else '(none)'}")
        lines.append("")
        if not res["rows"]:
            lines.append("_No records returned._")
            lines.append("")
            continue
        lines.append("| PMID | PMCID | Year/Date | Source | Title |")
        lines.append("|---|---|---|---|---|")
        for r in res["rows"]:
            title = (r["title"] or "").replace("|", "\\|")
            lines.append(
                f"| [{r['pmid']}]({r['pubmed_url']}) | {r['pmcid'] or '—'} | "
                f"{r['pubdate'] or '—'} | {r['source'] or '—'} | {title} |"
            )
        lines.append("")

    lines.append("## Allmendinger: open access vs abstract-only")
    lines.append("")
    lines.append(
        "Classic injectability / rheology papers by Allmendinger are often "
        "**publisher-paywalled**. This batch compares PubMed with and without "
        "`free full text[filter]`, and whether `elink` finds a PMC full-text record."
    )
    lines.append("")
    a = data["allmendinger_oa_vs_abstract_note"]
    lines.append(
        f"- **Allmendinger[author] AND injection AND free full text[filter]:** "
        f"count = **{a['free_full_text_filter_count']}**"
    )
    lines.append(f"  - PMIDs: {', '.join(a['free_full_text_pmids']) or '(none)'}")
    lines.append(
        "  - These free-full-text hits are **not** the classic 2014 "
        "injection-force paper (manufacturing / gene therapy topics)."
    )
    lines.append(
        f"- **Allmendinger[author] AND injection (no free-full-text filter):** "
        f"count = **{a['unfiltered_injection_count']}**"
    )
    lines.append(f"  - PMIDs: {', '.join(a['unfiltered_injection_pmids']) or '(none)'}")
    lines.append("")
    lines.append("### Classic Allmendinger 2014")
    lines.append("")
    c = data["classic_allmendinger_2014_pmid"]
    lines.append(f"- **PMID {c['pmid']}** — {c['title']}")
    lines.append(f"- **Access:** {c['access']}")
    lines.append(f"- In free-full-text Query 3: **{c['in_free_full_text_query3']}**")
    lines.append(f"- {c['note']}")
    lines.append("")
    lines.append("### Force / injectability-related Allmendinger papers (unfiltered search)")
    lines.append("")
    lines.append("| PMID | Access | Date | Source | Title |")
    lines.append("|---|---|---|---|---|")
    for r in data["allmendinger_force_related_access"]:
        title = (r["title"] or "").replace("|", "\\|")
        lines.append(
            f"| {r['pmid']} | {r['access']} | {r['pubdate'] or '—'} | "
            f"{r['source'] or '—'} | {title} |"
        )
    lines.append("")
    lines.append(
        "**Conclusion:** The classic Allmendinger 2014 (PMID 24560966) and most "
        "injection-force companion papers are **abstract-only** for free-full-text "
        "PMC workflows. Do **not** invent experimental numbers from abstracts."
    )
    lines.append("")

    lines.append("## Top 10 most promising PMIDs for human review")
    lines.append("")
    lines.append(
        "Heuristic ranking from **title keywords + query provenance** "
        "(boost: injection/glide force, injectability, Hagen–Poiseuille, "
        "glycerol+needle+force; down-rank: hydrogels, gene therapy, COGs, cement)."
    )
    lines.append(
        "**Friction-corrected force:** not asserted from metadata — full-text review required."
    )
    lines.append("")
    lines.append("| Rank | PMID | PMCID | Score | Friction-corrected force? | Title |")
    lines.append("|---:|---|---|---:|---|---|")
    for i, r in enumerate(top10, 1):
        title = (r["title"] or "").replace("|", "\\|")
        lines.append(
            f"| {i} | [{r['pmid']}]({r['pubmed_url']}) | {r['pmcid'] or '—'} | "
            f"{r['relevance_score_heuristic']:.1f} | Unknown (full-text review "
            f"required) | {title} |"
        )
    lines.append("")
    lines.append("### Friction-corrected force claims")
    lines.append("")
    lines.append(
        "From **search metadata alone**, **no paper can be certified** as "
        "reporting friction-corrected / fluid-only needle force."
    )
    lines.append(
        "Human full-text review should look for: empty-syringe friction "
        "subtraction, pressure transducer distal to stopper, or explicit "
        "separation of break-loose/glide friction from Hagen–Poiseuille fluid "
        "resistance."
    )
    lines.append(
        "Prior project assessment already flags that most OA “injection force” "
        "literature reports **total** glide force (includes stopper–barrel "
        "friction)."
    )
    lines.append("")
    lines.append(
        "**None of the free-full-text hits in this batch claim (in the title) "
        "friction-corrected fluid force.** Whether any abstract/full text does "
        "so requires human reading; this agent does not fabricate that claim."
    )
    lines.append("")
    lines.append("## Unique free-full-text PMIDs (all four queries)")
    lines.append("")
    lines.append(f"**Unique PMIDs:** {data['unique_count']}")
    lines.append("")
    for pid in data["unique_free_full_text_pmids"]:
        row = all_rows[pid]
        lines.append(
            f"- **{pid}** ({row.get('pmcid') or 'no PMC'}): "
            f"{(row.get('title') or '')[:120]} — queries: "
            f"{', '.join(row.get('queries') or [])}"
        )
    lines.append("")
    lines.append("## Files")
    lines.append("")
    lines.append("- Machine-readable: [`docs/agent-pubmed-batch.json`](agent-pubmed-batch.json)")
    lines.append("- This report: [`docs/agent-pubmed-batch.md`](agent-pubmed-batch.md)")
    lines.append(
        "- Reproducible script: [`scripts/pubmed_agent_batch.py`](../scripts/pubmed_agent_batch.py)"
    )
    lines.append("")

    MD_PATH.write_text("\n".join(lines), encoding="utf-8")
    print("Updated", JSON_PATH)
    print("Updated", MD_PATH)
    print("TOP 10:")
    for i, r in enumerate(top10, 1):
        print(
            f"{i}. {r['pmid']} {r.get('pmcid')} "
            f"score={r['relevance_score_heuristic']:.1f} "
            f"{(r['title'] or '')[:100]}"
        )
    print("Allmendinger 2014:", data["classic_allmendinger_2014_pmid"]["access"])
    print("Force-related Allmendinger:")
    for r in force_related_allm:
        print(f"  {r['pmid']} | {r['access']} | {(r['title'] or '')[:70]}")


if __name__ == "__main__":
    main()
