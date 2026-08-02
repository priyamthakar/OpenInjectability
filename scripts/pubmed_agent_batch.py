"""PubMed E-utilities batch: free full text injectability / syringe force searches.

Uses esearch -> esummary -> elink (pubmed_pmc). No experimental numbers fabricated.
"""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "docs" / "agent-pubmed-batch.json"
OUT_MD = ROOT / "docs" / "agent-pubmed-batch.md"
UA = "OpenInjectability/0.1 (literature-batch; research)"
BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

QUERIES = [
    {
        "id": "q1_injection_force_viscosity_needle",
        "label": "Injection/glide force + viscosity + needle/syringe (free full text)",
        "term": (
            '("injection force"[tiab] OR "glide force"[tiab] OR injectability[tiab]) '
            "AND viscosity[tiab] AND (needle[tiab] OR syringe[tiab]) AND free full text[filter]"
        ),
    },
    {
        "id": "q2_glycerol_needle_force",
        "label": "Glycerol/glycerin + needle + force (free full text)",
        "term": (
            "(glycerol[tiab] OR glycerin[tiab]) AND (needle[tiab]) AND (force[tiab]) "
            "AND free full text[filter]"
        ),
    },
    {
        "id": "q3_allmendinger_author",
        "label": "Allmendinger[author] + injection (free full text)",
        "term": "Allmendinger[author] AND injection AND free full text[filter]",
    },
    {
        "id": "q4_hagen_poiseuille_syringe",
        "label": "Hagen-Poiseuille + syringe (free full text)",
        "term": '"Hagen-Poiseuille"[tiab] AND syringe AND free full text[filter]',
    },
]

CLASSIC_CHECKS = [
    {
        "id": "classic_allmendinger_2014",
        "label": "Allmendinger[author] + injection (no free-full-text filter)",
        "term": "Allmendinger[author] AND injection",
        "note": "Includes paywalled classic papers; compare to free full text filter",
    },
    {
        "id": "classic_allmendinger_broader",
        "label": "Allmendinger + injection force / injectability / rheolog*",
        "term": 'Allmendinger[author] AND ("injection force" OR injectability OR rheolog*)',
        "note": "Broader Allmendinger set for OA vs abstract-only classification",
    },
]

POSITIVE = [
    "injection force",
    "glide force",
    "injectability",
    "syringeability",
    "hagen-poiseuille",
    "hagen–poiseuille",
    "needle",
    "syringe",
    "viscosity",
    "rheolog",
    "glycerol",
    "glycerin",
    "newtonian",
    "break-loose",
    "break loose",
    "extrusion force",
    "plunger force",
    "protein formulation",
    "high concentration",
    "subcutaneous",
    "friction",
    "fluid resistance",
    "pressure drop",
]
NEGATIVE = [
    "periodontal",
    "in situ gel",
    "oromucosal",
    "cement",
    "bone cement",
    "dental",
    "hydrogel scaffold",
    "cancer injectable",
    "tumor",
    "3d print",
    "bioprint",
    "microneedle array vaccine",
]


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.load(resp)


def esearch(term: str, retmax: int = 200) -> dict:
    url = (
        f"{BASE}/esearch.fcgi?db=pubmed&retmode=json&retmax={retmax}"
        f"&term={urllib.parse.quote(term)}"
    )
    return fetch_json(url)


def esummary(pmids: list[str]) -> dict:
    out: dict = {"result": {"uids": []}}
    if not pmids:
        return out
    for i in range(0, len(pmids), 100):
        chunk = pmids[i : i + 100]
        url = (
            f"{BASE}/esummary.fcgi?db=pubmed&retmode=json"
            f"&id={','.join(chunk)}"
        )
        data = fetch_json(url)
        time.sleep(0.34)
        for uid in data.get("result", {}).get("uids", []):
            out["result"]["uids"].append(uid)
            out["result"][uid] = data["result"][uid]
    return out


def elink_pmc(pmids: list[str]) -> dict[str, list[str]]:
    """Map PMID -> list of numeric PMC IDs via elink pubmed_pmc (one ID at a time)."""
    mapping: dict[str, list[str]] = {p: [] for p in pmids}
    for p in pmids:
        url = (
            f"{BASE}/elink.fcgi?dbfrom=pubmed&db=pmc&retmode=json"
            f"&linkname=pubmed_pmc&id={p}"
        )
        data = fetch_json(url)
        time.sleep(0.34)
        for linkset in data.get("linksets", []):
            for ldb in linkset.get("linksetdbs") or []:
                name = ldb.get("linkname") or ""
                if ldb.get("dbto") == "pmc" or "pmc" in name:
                    mapping[p] = [str(x) for x in ldb.get("links", [])]
    return mapping


def authors_str(r: dict) -> str:
    authors = r.get("authors") or []
    names = [a.get("name", "") for a in authors[:6]]
    s = ", ".join(names)
    if len(authors) > 6:
        s += " et al."
    return s


def format_pmcid(raw: str) -> str:
    xs = str(raw)
    if xs.upper().startswith("PMC"):
        return xs.upper().replace("PMC", "PMC") if xs[:3].upper() == "PMC" else xs
    return f"PMC{xs}"


def build_row(pid: str, r: dict, pmc_map: dict[str, list[str]]) -> dict:
    pmcids_raw = pmc_map.get(pid) or []
    pmc_fmt = [format_pmcid(x) for x in pmcids_raw]
    row = {
        "pmid": pid,
        "title": r.get("title"),
        "pubdate": r.get("pubdate"),
        "source": r.get("source"),
        "authors": authors_str(r),
        "elocationid": r.get("elocationid"),
        "doi": None,
        "pmcid": pmc_fmt[0] if pmc_fmt else None,
        "pmcids": pmc_fmt,
        "has_pmc_fulltext_link": bool(pmc_fmt),
        "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{pid}/",
        "pmc_url": (
            f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_fmt[0]}/"
            if pmc_fmt
            else None
        ),
    }
    eloc = r.get("elocationid") or ""
    if "doi:" in eloc.lower():
        # elocationid like "doi: 10.xxx"
        parts = eloc.split(":", 1)
        if len(parts) == 2:
            row["doi"] = parts[1].strip()
    for aid in r.get("articleids") or []:
        if aid.get("idtype") == "doi":
            row["doi"] = aid.get("value")
        if aid.get("idtype") == "pmc":
            v = aid.get("value") or ""
            if v:
                pmc = v if str(v).upper().startswith("PMC") else f"PMC{v}"
                row["pmcid"] = pmc
                row["pmcids"] = [pmc]
                row["has_pmc_fulltext_link"] = True
                row["pmc_url"] = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc}/"
    return row


def process_query(q: dict, retmax: int = 200) -> dict:
    print(f"\n=== {q['id']} ===")
    print(f"term: {q['term']}")
    search = esearch(q["term"], retmax=retmax)
    time.sleep(0.34)
    er = search.get("esearchresult", {})
    count = int(er.get("count", 0))
    ids = list(er.get("idlist") or [])
    print(f"count={count} returned={len(ids)}")
    summary = esummary(ids)
    time.sleep(0.34)
    pmc_map = elink_pmc(ids)
    rows = []
    for pid in ids:
        r = summary.get("result", {}).get(pid, {})
        row = build_row(pid, r, pmc_map)
        rows.append(row)
        print(f"  {pid} | {row['pmcid'] or 'no-PMC'} | {(row['title'] or '')[:80]}")
    return {
        "id": q["id"],
        "label": q["label"],
        "term": q["term"],
        "count": count,
        "returned": len(ids),
        "ids": ids,
        "rows": rows,
        "note": q.get("note"),
    }


def score_row(row: dict) -> float:
    t = (row.get("title") or "").lower()
    s = 0.0
    high = (
        "injection force",
        "glide force",
        "hagen-poiseuille",
        "hagen–poiseuille",
        "injectability",
    )
    for kw in POSITIVE:
        if kw in t:
            s += 2.0 if kw in high else 1.0
    for kw in NEGATIVE:
        if kw in t:
            s -= 3.0
    if row.get("has_pmc_fulltext_link"):
        s += 0.5
    s += 0.3 * len(row.get("queries") or [])
    if "allmendinger" in (row.get("authors") or "").lower():
        s += 5.0
    return s


def main() -> None:
    results = []
    for q in QUERIES:
        results.append(process_query(q))
        time.sleep(0.5)

    classic = []
    for q in CLASSIC_CHECKS:
        classic.append(process_query(q, retmax=50))
        time.sleep(0.5)

    all_rows: dict[str, dict] = {}
    for res in results:
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

    allm_free = next((r for r in results if r["id"] == "q3_allmendinger_author"), None)
    allm_all = next((r for r in classic if r["id"] == "classic_allmendinger_2014"), None)
    allm_broad = next(
        (r for r in classic if r["id"] == "classic_allmendinger_broader"), None
    )

    allm_oa_note = {
        "free_full_text_filter_count": allm_free["count"] if allm_free else None,
        "free_full_text_pmids": allm_free["ids"] if allm_free else [],
        "free_full_text_rows": allm_free["rows"] if allm_free else [],
        "unfiltered_injection_count": allm_all["count"] if allm_all else None,
        "unfiltered_injection_pmids": allm_all["ids"] if allm_all else [],
        "unfiltered_rows": [
            {
                "pmid": r["pmid"],
                "title": r["title"],
                "pubdate": r["pubdate"],
                "source": r["source"],
                "pmcid": r["pmcid"],
                "has_pmc": r["has_pmc_fulltext_link"],
                "access_note": (
                    "PMC full-text link present (typically open-access deposit)"
                    if r["has_pmc_fulltext_link"]
                    else (
                        "No PMC link via elink — often abstract-only / paywalled "
                        "publisher full text (not free full text on PubMed)"
                    )
                ),
            }
            for r in (allm_all["rows"] if allm_all else [])
        ],
        "broader_rheology_count": allm_broad["count"] if allm_broad else None,
        "broader_rows": [
            {
                "pmid": r["pmid"],
                "title": r["title"],
                "pubdate": r["pubdate"],
                "source": r["source"],
                "pmcid": r["pmcid"],
                "has_pmc": r["has_pmc_fulltext_link"],
                "access_note": (
                    "PMC full-text link present (typically open-access deposit)"
                    if r["has_pmc_fulltext_link"]
                    else (
                        "No PMC link via elink — often abstract-only / paywalled "
                        "publisher full text (not free full text on PubMed)"
                    )
                ),
            }
            for r in (allm_broad["rows"] if allm_broad else [])
        ],
    }

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "NCBI E-utilities (eutils.ncbi.nlm.nih.gov)",
        "endpoints_used": ["esearch.fcgi", "esummary.fcgi", "elink.fcgi"],
        "disclaimer": (
            "No experimental numbers fabricated. Titles and access flags come from "
            "PubMed metadata only. free full text[filter] is a PubMed filter; PMC "
            "link via elink indicates PMC deposit (usually OA). Friction-corrected "
            "fluid force cannot be asserted from title alone."
        ),
        "queries": results,
        "classic_allmendinger_access_checks": classic,
        "allmendinger_oa_vs_abstract_note": allm_oa_note,
        "unique_free_full_text_pmids": sorted(
            all_rows.keys(), key=lambda x: -score_row(all_rows[x])
        ),
        "unique_count": len(all_rows),
        "top10_promising_for_human_review": top10,
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nWrote {OUT_JSON}")

    lines: list[str] = []
    lines.append("# PubMed E-utilities batch — injectability / syringe force")
    lines.append("")
    lines.append(f"Generated (UTC): `{payload['generated_at_utc']}`")
    lines.append("")
    lines.append(
        "**Source:** NCBI E-utilities (`esearch` → `esummary` → `elink` pubmed→pmc)."
    )
    lines.append("")
    lines.append(payload["disclaimer"])
    lines.append("")
    lines.append("## Query hit counts")
    lines.append("")
    lines.append(
        "| # | Query | Count | Returned (retmax) | With PMC link |"
    )
    lines.append("|---|---|---:|---:|---:|")
    for i, res in enumerate(results, 1):
        pmc_n = sum(1 for r in res["rows"] if r["has_pmc_fulltext_link"])
        lines.append(
            f"| {i} | {res['label']} | {res['count']} | {res['returned']} | {pmc_n} |"
        )
    lines.append("")

    for i, res in enumerate(results, 1):
        lines.append(f"## Query {i}: {res['label']}")
        lines.append("")
        lines.append("```")
        lines.append(res["term"])
        lines.append("```")
        lines.append("")
        lines.append(f"- **Count:** {res['count']}")
        lines.append(
            f"- **PMIDs returned:** "
            f"{', '.join(res['ids']) if res['ids'] else '(none)'}"
        )
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
    lines.append(
        f"- **Allmendinger[author] AND injection AND free full text[filter]:** "
        f"count = **{allm_oa_note['free_full_text_filter_count']}**"
    )
    lines.append(
        f"  - PMIDs: {', '.join(allm_oa_note['free_full_text_pmids']) or '(none)'}"
    )
    lines.append(
        f"- **Allmendinger[author] AND injection (no free-full-text filter):** "
        f"count = **{allm_oa_note['unfiltered_injection_count']}**"
    )
    lines.append(
        f"  - PMIDs: "
        f"{', '.join(allm_oa_note['unfiltered_injection_pmids']) or '(none)'}"
    )
    lines.append(
        f"- **Broader Allmendinger + injection force / injectability / rheolog*:** "
        f"count = **{allm_oa_note['broader_rheology_count']}**"
    )
    lines.append("")
    if allm_oa_note["unfiltered_rows"]:
        lines.append("### Unfiltered Allmendinger + injection (access flags)")
        lines.append("")
        lines.append("| PMID | PMCID / access | Date | Source | Title |")
        lines.append("|---|---|---|---|---|")
        for r in allm_oa_note["unfiltered_rows"]:
            access = r["pmcid"] if r["has_pmc"] else "**abstract-only / no PMC link**"
            title = (r["title"] or "").replace("|", "\\|")
            lines.append(
                f"| {r['pmid']} | {access} | {r['pubdate'] or '—'} | "
                f"{r['source'] or '—'} | {title} |"
            )
        lines.append("")
    if allm_oa_note["broader_rows"]:
        lines.append("### Broader Allmendinger rheology/injectability set")
        lines.append("")
        lines.append("| PMID | PMCID / access | Date | Source | Title |")
        lines.append("|---|---|---|---|---|")
        for r in allm_oa_note["broader_rows"]:
            access = r["pmcid"] if r["has_pmc"] else "**abstract-only / no PMC link**"
            title = (r["title"] or "").replace("|", "\\|")
            lines.append(
                f"| {r['pmid']} | {access} | {r['pubdate'] or '—'} | "
                f"{r['source'] or '—'} | {title} |"
            )
        lines.append("")
    lines.append(
        "**Note on Allmendinger 2014 (classic):** If the well-known *Eur J Pharm "
        "Biopharm* injection-force / Hagen–Poiseuille papers appear only without "
        "the free-full-text filter and without a PMCID, treat them as "
        "**abstract-only in this free-text workflow** (full tables not extractable "
        "via PMC). Do not invent their experimental numbers from abstracts."
    )
    lines.append("")

    lines.append("## Top 10 most promising PMIDs for human review")
    lines.append("")
    lines.append(
        "Heuristic ranking from **title keywords only** (injection/glide force, "
        "injectability, Hagen–Poiseuille, glycerol, viscosity, etc.; down-rank "
        "dental/gel/cement)."
    )
    lines.append(
        "**Friction-corrected force:** not asserted from metadata — review "
        "checklist only."
    )
    lines.append("")
    lines.append(
        "| Rank | PMID | PMCID | Score | Friction-corrected force? | Title |"
    )
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
    lines.append("## Unique free-full-text PMIDs (all four queries)")
    lines.append("")
    lines.append(f"**Unique PMIDs:** {len(all_rows)}")
    lines.append("")
    for pid in payload["unique_free_full_text_pmids"]:
        row = all_rows[pid]
        lines.append(
            f"- **{pid}** ({row.get('pmcid') or 'no PMC'}): "
            f"{(row.get('title') or '')[:120]} — queries: "
            f"{', '.join(row.get('queries') or [])}"
        )
    lines.append("")
    lines.append("## Files")
    lines.append("")
    lines.append(
        "- Machine-readable: [`docs/agent-pubmed-batch.json`](agent-pubmed-batch.json)"
    )
    lines.append("- This report: [`docs/agent-pubmed-batch.md`](agent-pubmed-batch.md)")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_MD}")
    print("\nTOP 10:")
    for i, r in enumerate(top10, 1):
        print(
            f"{i}. {r['pmid']} {r['pmcid']} "
            f"score={r['relevance_score_heuristic']:.1f} "
            f"{(r['title'] or '')[:90]}"
        )


if __name__ == "__main__":
    main()
