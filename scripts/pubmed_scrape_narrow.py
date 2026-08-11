"""Narrow EuropePMC queries + fetch open fulltext snippets for candidate papers."""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "pubmed-scrape-candidates.json"

QUERIES = [
    (
        "glycerol_newtonian_force",
        'TITLE_ABS:(glycerol OR glycerin OR newtonian) AND TITLE_ABS:("injection force" OR "glide force" OR injectability) AND (needle OR syringe) AND OPEN_ACCESS:y',
    ),
    (
        "hagen_poiseuille_force",
        'TITLE_ABS:("Hagen-Poiseuille" OR "Hagen–Poiseuille") AND ("injection force" OR "glide force" OR syringe) AND OPEN_ACCESS:y',
    ),
    (
        "friction_subtract_hydrodynamic",
        'TITLE_ABS:(friction) AND TITLE_ABS:("glide force" OR "injection force") AND viscosity AND needle AND OPEN_ACCESS:y',
    ),
]


def search(q: str, page_size: int = 40) -> dict:
    url = (
        "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query="
        + urllib.parse.quote(q)
        + f"&format=json&pageSize={page_size}&resultType=core"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "OpenInjectability-research/0.1"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.load(resp)


def fetch_html(pmcid: str) -> str:
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
    req = urllib.request.Request(url, headers={"User-Agent": "OpenInjectability-research/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as exc:  # noqa: BLE001
        return f"ERROR: {exc}"


def score_text(text: str) -> dict[str, bool]:
    lower = text.lower()
    return {
        "mentions_newtonian": "newtonian" in lower,
        "mentions_glycerol": "glycerol" in lower or "glycerin" in lower,
        "mentions_viscosity": "viscosity" in lower or "mpa" in lower or "cp" in lower,
        "mentions_needle_id": bool(
            re.search(r"inner diameter|needle id|bore|i\.d\.|mm\s*id", lower)
        ),
        "mentions_barrel": "barrel" in lower or "syringe diameter" in lower,
        "mentions_flow_rate": "ml/min" in lower or "mm/min" in lower or "flow rate" in lower,
        "mentions_friction": "friction" in lower
        or "break-loose" in lower
        or "break loose" in lower,
        "mentions_hagen": "hagen" in lower or "poiseuille" in lower,
        "has_table_like": "<table" in lower or "table " in lower,
    }


def main() -> None:
    report: dict = {"queries": {}, "fulltext_screens": []}
    seen: set[str] = set()
    for name, q in QUERIES:
        data = search(q)
        hits = []
        for res in data.get("resultList", {}).get("result", []):
            pmcid = res.get("pmcid")
            hits.append(
                {
                    "pmid": res.get("pmid"),
                    "pmcid": pmcid,
                    "doi": res.get("doi"),
                    "year": res.get("pubYear"),
                    "title": res.get("title"),
                    "hasSuppl": res.get("hasSuppl"),
                    "license": res.get("license"),
                    "abstract": (res.get("abstractText") or "")[:800],
                }
            )
            if pmcid and pmcid not in seen:
                seen.add(pmcid)
        report["queries"][name] = {"hitCount": data.get("hitCount"), "hits": hits}
        print(name, "hits", data.get("hitCount"))

    # Fulltext screen top unique PMCIDs from first query (up to 15)
    first_hits = report["queries"]["glycerol_newtonian_force"]["hits"]
    for hit in first_hits[:15]:
        pmcid = hit.get("pmcid")
        if not pmcid:
            continue
        print("fetch", pmcid)
        xml = fetch_html(pmcid)
        flags = score_text(xml)
        # Extract numeric-ish snippets around viscosity / force
        snippets = []
        for pat in [
            r".{0,80}viscosity.{0,80}",
            r".{0,80}glide force.{0,80}",
            r".{0,80}injection force.{0,80}",
            r".{0,60}inner diameter.{0,80}",
        ]:
            for m in re.finditer(pat, xml, flags=re.IGNORECASE | re.DOTALL):
                snippets.append(re.sub(r"\s+", " ", m.group(0))[:200])
                if len(snippets) >= 12:
                    break
            if len(snippets) >= 12:
                break
        report["fulltext_screens"].append(
            {
                "pmcid": pmcid,
                "title": hit.get("title"),
                "doi": hit.get("doi"),
                "flags": flags,
                "xml_bytes": len(xml),
                "error": xml.startswith("ERROR"),
                "snippets": snippets[:12],
            }
        )
        print(" ", flags, "bytes", len(xml))

    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
