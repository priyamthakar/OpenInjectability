"""Extra precise Zenodo queries."""
from __future__ import annotations

import json
import ssl
import urllib.parse
import urllib.request

CTX = ssl.create_default_context()
UA = {"User-Agent": "OpenInjectability/1.0"}


def search(q: str, size: int = 10, type_filter: str | None = "dataset"):
    params = {"q": q, "size": str(size)}
    if type_filter:
        params["type"] = type_filter
    url = "https://zenodo.org/api/records?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, context=CTX, timeout=60) as r:
        return json.load(r)


def main():
    queries = [
        'title:"injection force"',
        "title:injectability AND (syringe OR needle)",
        "keywords:injection force",
        '"fluid resistance" syringe',
        '"empty syringe" force viscosity',
        "glycerol water syringe needle force",
        "type:dataset AND syringe AND viscosity AND needle AND force",
        "title:syringeability",
        "title:\"glide force\"",
        "Allmendinger glycerol",
        "\"break-loose\" syringe",
        "\"expulsion force\" needle",
    ]
    for q in queries:
        try:
            data = search(q, size=10, type_filter="dataset")
            total = data.get("hits", {}).get("total")
            hits = data.get("hits", {}).get("hits") or []
            print(f"\nQ={q!r} total={total}")
            for h in hits[:6]:
                m = h.get("metadata") or {}
                files = [f.get("key") for f in (h.get("files") or [])][:5]
                print(f"  {h.get('id')} | {(m.get('title') or '')[:110]}")
                print(f"    files={files}")
        except Exception as e:
            print(f"ERR {q!r}: {e}")


if __name__ == "__main__":
    main()
