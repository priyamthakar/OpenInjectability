"""Probe EuropePMC / PubMed Central for open injectability papers (no fabrication)."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "docs" / "pubmed-scrape-probe.json"

QUERIES = [
    'TITLE_ABS:("glide force" OR "injection force" OR injectability) AND viscosity AND needle AND OPEN_ACCESS:y',
    'TITLE_ABS:("dynamic glide force") AND OPEN_ACCESS:y',
    'TITLE_ABS:("Hagen-Poiseuille") AND (syringe OR needle) AND viscosity AND OPEN_ACCESS:y',
    'TITLE_ABS:(glycerol) AND ("injection force" OR "glide force") AND needle AND OPEN_ACCESS:y',
]


def search(q: str, page_size: int = 25) -> dict:
    url = (
        "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query="
        + urllib.parse.quote(q)
        + f"&format=json&pageSize={page_size}&resultType=core"
    )
    with urllib.request.urlopen(url, timeout=90) as resp:
        return json.load(resp)


def main() -> None:
    report: dict = {"queries": []}
    for q in QUERIES:
        data = search(q)
        hits = []
        for res in data.get("resultList", {}).get("result", []):
            hits.append(
                {
                    "pmid": res.get("pmid"),
                    "pmcid": res.get("pmcid"),
                    "doi": res.get("doi"),
                    "year": res.get("pubYear"),
                    "title": res.get("title"),
                    "isOpenAccess": res.get("isOpenAccess"),
                    "hasPDF": res.get("hasPDF"),
                    "hasSuppl": res.get("hasSuppl"),
                    "license": res.get("license"),
                    "abstract": (res.get("abstractText") or "")[:500],
                }
            )
        report["queries"].append({"query": q, "hitCount": data.get("hitCount"), "hits": hits})
        print(f"hits={data.get('hitCount')} for: {q[:70]}...")
        for h in hits[:8]:
            print(f"  {h['pmcid'] or h['pmid']} {h['year']} {h['title'][:90]}")
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
