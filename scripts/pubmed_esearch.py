"""PubMed eutils free-full-text search for injectability candidates."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "docs" / "pubmed-esearch.json"
TERM = (
    '("injection force"[Title/Abstract] OR "glide force"[Title/Abstract]) '
    "AND viscosity AND (glycerol OR glycerin OR newtonian) AND free full text[Filter]"
)


def main() -> None:
    search_url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        f"?db=pubmed&retmode=json&retmax=50&term={urllib.parse.quote(TERM)}"
    )
    req = urllib.request.Request(search_url, headers={"User-Agent": "OpenInjectability/0.1"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        search = json.load(resp)
    ids = search["esearchresult"]["idlist"]
    count = search["esearchresult"]["count"]
    rows = []
    if ids:
        sum_url = (
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            f"?db=pubmed&retmode=json&id={','.join(ids)}"
        )
        req2 = urllib.request.Request(sum_url, headers={"User-Agent": "OpenInjectability/0.1"})
        with urllib.request.urlopen(req2, timeout=60) as resp:
            summary = json.load(resp)
        for pid in ids:
            r = summary["result"][pid]
            rows.append(
                {
                    "pmid": pid,
                    "title": r.get("title"),
                    "pubdate": r.get("pubdate"),
                    "source": r.get("source"),
                    "elocationid": r.get("elocationid"),
                }
            )
    OUT.write_text(
        json.dumps({"term": TERM, "count": count, "ids": ids, "rows": rows}, indent=2),
        encoding="utf-8",
    )
    print("count", count)
    for row in rows[:20]:
        print(row["pmid"], row["pubdate"], (row["title"] or "")[:90])


if __name__ == "__main__":
    main()
