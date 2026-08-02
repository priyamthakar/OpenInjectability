"""Deep pull: Zenodo + Figshare APIs for syringe injection force / viscosity CSV/XLS."""
from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

CTX = ssl.create_default_context()
UA = {"User-Agent": "OpenInjectability-deep-pull/1.0 (research; local)"}
OUT = Path(__file__).resolve().parent / "_repo_deep_pull_raw.json"


def get_json(url: str, timeout: int = 90):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, context=CTX, timeout=timeout) as r:
        return json.load(r)


def zenodo_search(q: str, size: int = 25, page: int = 1, type_filter: str | None = "dataset"):
    params = {"q": q, "size": str(size), "page": str(page)}
    if type_filter:
        params["type"] = type_filter
    url = "https://zenodo.org/api/records?" + urllib.parse.urlencode(params)
    return get_json(url)


def summarize_zenodo_hit(h: dict) -> dict:
    m = h.get("metadata") or {}
    files = h.get("files") or []
    keys = [f.get("key", "") for f in files]
    tabular = [
        k
        for k in keys
        if k.lower().endswith(
            (".csv", ".xlsx", ".xls", ".tsv", ".txt", ".json", ".zip", ".tar", ".tar.gz", ".gz")
        )
    ]
    return {
        "id": h.get("id"),
        "doi": m.get("doi") or h.get("doi"),
        "title": m.get("title"),
        "access_right": m.get("access_right"),
        "resource_type": (m.get("resource_type") or {}).get("type"),
        "resource_subtype": (m.get("resource_type") or {}).get("subtype"),
        "creators": [c.get("name") for c in (m.get("creators") or [])[:6]],
        "keywords": m.get("keywords"),
        "description_snip": (m.get("description") or "")[:400],
        "n_files": len(files),
        "file_keys": keys[:20],
        "tabularish_files": tabular[:20],
        "record_url": f"https://zenodo.org/records/{h.get('id')}",
    }


def figshare_article(aid: str, version: int | None = None):
    if version is not None:
        url = f"https://api.figshare.com/v2/articles/{aid}/versions/{version}"
    else:
        url = f"https://api.figshare.com/v2/articles/{aid}"
    return get_json(url)


def figshare_search(q: str, page_size: int = 20, item_type: int | None = 3):
    # item_type 3 = dataset
    params = {"search_for": q, "page_size": str(page_size)}
    if item_type is not None:
        params["item_type"] = str(item_type)
    url = "https://api.figshare.com/v2/articles/search"
    data = json.dumps(params).encode()
    req = urllib.request.Request(
        url, data=data, headers={**UA, "Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, context=CTX, timeout=90) as r:
        return json.load(r)


def main():
    report: dict = {
        "zenodo_queries": [],
        "figshare_targeted": [],
        "figshare_search": [],
        "candidates_for_download_inspect": [],
    }

    queries = [
        "syringe injection force",
        "syringe force viscosity",
        "injection force needle viscosity",
        "glycerol syringe force",
        "glycerol needle injection force",
        "injectability viscosity",
        "glide force syringe",
        "syringeability viscosity",
        "Hagen Poiseuille syringe",
        "injection force glycerol",
        "plunger force viscosity",
        "break loose force syringe",
        "extrusion force syringe",
        "needle diameter viscosity force",
        '"injection force" AND (syringe OR needle)',
        '"glide force" AND syringe',
        "syringe OR needle AND viscosity AND force AND dataset",
        "Allmendinger injection force",
        "Cilurzo injectability",
        "Newtonian viscosity syringe force",
    ]

    seen_ids = set()
    for q in queries:
        entry = {"query": q, "type_filter": "dataset", "total": None, "hits": [], "error": None}
        try:
            data = zenodo_search(q, size=25, type_filter="dataset")
            entry["total"] = data.get("hits", {}).get("total")
            hits = data.get("hits", {}).get("hits") or []
            for h in hits:
                s = summarize_zenodo_hit(h)
                entry["hits"].append(s)
                if s["id"] not in seen_ids:
                    seen_ids.add(s["id"])
                    # flag potential interest
                    blob = " ".join(
                        [
                            str(s.get("title") or ""),
                            str(s.get("description_snip") or ""),
                            " ".join(s.get("keywords") or []) if s.get("keywords") else "",
                            " ".join(s.get("file_keys") or []),
                        ]
                    ).lower()
                    keys_interest = (
                        "force" in blob
                        or "inject" in blob
                        or "syringe" in blob
                        or "needle" in blob
                        or "glide" in blob
                        or "plunger" in blob
                        or "extrusion" in blob
                    )
                    if keys_interest and s.get("tabularish_files"):
                        report["candidates_for_download_inspect"].append(
                            {"source": "zenodo", "query": q, **s}
                        )
        except Exception as e:
            entry["error"] = f"{type(e).__name__}: {e}"
        report["zenodo_queries"].append(entry)
        print(f"ZENODO q={q!r} total={entry['total']} hits={len(entry['hits'])} err={entry['error']}")

    # Also search without type=dataset for injection force (broader)
    broad_qs = [
        "syringe injection force",
        '"injection force" viscosity',
        "glycerol needle force",
    ]
    for q in broad_qs:
        entry = {"query": q, "type_filter": None, "total": None, "hits": [], "error": None}
        try:
            data = zenodo_search(q, size=25, type_filter=None)
            entry["total"] = data.get("hits", {}).get("total")
            hits = data.get("hits", {}).get("hits") or []
            for h in hits[:15]:
                s = summarize_zenodo_hit(h)
                entry["hits"].append(s)
        except Exception as e:
            entry["error"] = f"{type(e).__name__}: {e}"
        report["zenodo_queries"].append(entry)
        print(f"ZENODO-broad q={q!r} total={entry['total']} hits={len(entry['hits'])}")

    # Figshare targeted DOIs
    for aid, ver in [("32195520", 1), ("20800108", 1), ("32195520", None), ("20800108", None)]:
        try:
            data = figshare_article(aid, version=ver)
            files = data.get("files") or []
            entry = {
                "article_id": aid,
                "version": ver,
                "title": data.get("title"),
                "doi": data.get("doi"),
                "url": data.get("url_public_html") or data.get("url"),
                "defined_type": data.get("defined_type_name") or data.get("defined_type"),
                "license": data.get("license"),
                "description": (data.get("description") or "")[:1500],
                "tags": data.get("tags"),
                "categories": [c.get("title") for c in (data.get("categories") or [])],
                "authors": [a.get("full_name") for a in (data.get("authors") or [])],
                "files": [
                    {
                        "name": f.get("name"),
                        "size": f.get("size"),
                        "download_url": f.get("download_url"),
                        "mimetype": f.get("mimetype"),
                        "is_link_only": f.get("is_link_only"),
                        "id": f.get("id"),
                    }
                    for f in files
                ],
            }
            report["figshare_targeted"].append(entry)
            print(
                f"FIGSHARE {aid} v={ver}: title={entry['title']!r} nfiles={len(files)} doi={entry['doi']}"
            )
            for f in entry["files"]:
                print(f"  file: {f['name']} size={f['size']} url={f['download_url']}")
        except Exception as e:
            report["figshare_targeted"].append(
                {"article_id": aid, "version": ver, "error": f"{type(e).__name__}: {e}"}
            )
            print(f"FIGSHARE ERR {aid} v={ver}: {e}")

    # Figshare keyword search
    for q in [
        "syringe injection force viscosity",
        "injection force glycerol",
        "glide force syringe",
        "injectability viscosity needle",
        "Hagen Poiseuille syringe force",
        "syringe extrusion force viscosity",
    ]:
        try:
            hits = figshare_search(q, page_size=20, item_type=3)
            simplified = []
            for h in hits[:20]:
                simplified.append(
                    {
                        "id": h.get("id"),
                        "title": h.get("title"),
                        "doi": h.get("doi"),
                        "url": h.get("url_public_html"),
                        "defined_type": h.get("defined_type_name"),
                    }
                )
            report["figshare_search"].append({"query": q, "n": len(hits), "hits": simplified})
            print(f"FIGSHARE-search q={q!r} n={len(hits)}")
            for s in simplified[:8]:
                print(f"  {s['id']}: {s['title'][:100]}")
        except Exception as e:
            report["figshare_search"].append({"query": q, "error": f"{type(e).__name__}: {e}"})
            print(f"FIGSHARE-search ERR {q}: {e}")

    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nWrote {OUT}")
    print(f"Candidates for inspect: {len(report['candidates_for_download_inspect'])}")


if __name__ == "__main__":
    main()
