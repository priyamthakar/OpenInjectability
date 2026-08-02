#!/usr/bin/env python3
"""Extract and score tables from EuropePMC fullTextXML (no fabrication)."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET


def local(tag: str) -> str:
    return tag.split("}")[-1] if "}" in tag else tag


def text_of(el) -> str:
    if el is None:
        return ""
    parts: list[str] = []
    if el.text:
        parts.append(el.text)
    for c in el:
        parts.append(text_of(c))
        if c.tail:
            parts.append(c.tail)
    return re.sub(r"\s+", " ", " ".join(parts)).strip()


def find_all(root, name: str):
    return [e for e in root.iter() if local(e.tag) == name]


def extract_tables(root):
    tables = []
    for table_wrap in find_all(root, "table-wrap"):
        label = ""
        caption = ""
        for c in table_wrap:
            t = local(c.tag)
            if t == "label":
                label = text_of(c)
            elif t == "caption":
                caption = text_of(c)
        if not label:
            for lab in table_wrap.iter():
                if local(lab.tag) == "label":
                    label = text_of(lab)
                    break
        if not caption:
            for cap in table_wrap.iter():
                if local(cap.tag) == "caption":
                    caption = text_of(cap)
                    break
        rows = []
        for table in [e for e in table_wrap.iter() if local(e.tag) == "table"]:
            for tr in [e for e in table.iter() if local(e.tag) == "tr"]:
                cells = []
                for cell in list(tr):
                    if local(cell.tag) in ("td", "th"):
                        cells.append(text_of(cell))
                if cells:
                    rows.append(cells)
        if not rows:
            for array in [e for e in table_wrap.iter() if local(e.tag) == "array"]:
                for tr in [e for e in array.iter() if local(e.tag) == "tr"]:
                    cells = []
                    for cell in list(tr):
                        if local(cell.tag) in ("td", "th"):
                            cells.append(text_of(cell))
                    if cells:
                        rows.append(cells)
        tables.append(
            {"label": label, "caption": caption, "n_rows": len(rows), "rows": rows}
        )
    return tables


def get_meta(root):
    title = ""
    for t in find_all(root, "article-title"):
        title = text_of(t)
        break
    doi = ""
    pmcid = ""
    for aid in find_all(root, "article-id"):
        pid = aid.attrib.get("pub-id-type", "")
        if pid == "doi":
            doi = text_of(aid)
        elif pid in ("pmc", "pmcid"):
            pmcid = text_of(aid)
    return title, doi, pmcid


KEYWORDS = {
    "viscosity": re.compile(r"viscos|mPa|cP\b|Pa[\s·\-]?s|\bη\b|\bμ\b", re.I),
    "needle_d": re.compile(
        r"needle.*(ID|inner|diameter|bore|gauge)|gauge|inner diameter|ID\s*\(|needle diameter|bore",
        re.I,
    ),
    "length": re.compile(r"length|½|1/2|\bin\b|\bmm\b|half.?inch", re.I),
    "barrel": re.compile(r"barrel|syringe.*(ID|diameter)|plunger|PFS|prefilled|pre-filled", re.I),
    "flow": re.compile(
        r"flow\s*rate|mL/s|ml/s|mm/s|injection\s*speed|Q\s*=|crosshead|extension\s*rate|injection rate",
        re.I,
    ),
    "force_pressure": re.compile(
        r"force|glide|break.?loose|pressure|\bN\b|newton|MPa|kPa|psi|injection\s*force|work\s*\(",
        re.I,
    ),
}


def score_table(t: dict) -> dict:
    blob = (
        t["label"]
        + " "
        + t["caption"]
        + " "
        + " ".join(" | ".join(r) for r in t["rows"][:40])
    )
    scores = {k: bool(rx.search(blob)) for k, rx in KEYWORDS.items()}
    scores["has_numeric_force"] = bool(
        re.search(r"\d+\.?\d*\s*(N|mN|lbf)\b", blob, re.I)
    )
    scores["has_numeric_visc"] = bool(
        re.search(r"\d+\.?\d*\s*(cP|mPa|Pa\s*s|mPa·s|mPa s|mPas)", blob, re.I)
    )
    scores["has_gauge"] = bool(re.search(r"\d+\s*G\b|gauge", blob, re.I))
    scores["has_needle_id_mm"] = bool(
        re.search(
            r"(inner\s*diameter|ID|bore).{0,30}\d+\.?\d*\s*mm|\d+\.?\d*\s*mm.{0,30}(ID|inner|bore)",
            blob,
            re.I,
        )
    )
    core = ["viscosity", "needle_d", "length", "barrel", "flow", "force_pressure"]
    scores["core_hit_count"] = sum(1 for k in core if scores[k])
    return scores


def main():
    xml_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "docs/_fulltext_xml")
    results = []
    for p in sorted(xml_dir.glob("*.xml")):
        try:
            tree = ET.parse(p)
            root = tree.getroot()
        except Exception as e:
            results.append({"file": p.name, "error": str(e)})
            continue
        title, doi, pmcid = get_meta(root)
        tables = extract_tables(root)
        scored = []
        for t in tables:
            sc = score_table(t)
            scored.append(
                {
                    "label": t["label"],
                    "caption": t["caption"],
                    "n_rows": t["n_rows"],
                    "scores": sc,
                    "rows": t["rows"],
                }
            )
        body = text_of(root)
        # cap body for pattern search
        body_sample = body[:200000]
        results.append(
            {
                "file": p.name,
                "pmcid": pmcid or p.stem,
                "title": title,
                "doi": doi,
                "n_tables": len(tables),
                "tables": scored,
                "body_mentions": {
                    "viscosity": bool(re.search(r"viscos", body_sample, re.I)),
                    "needle": bool(re.search(r"needle", body_sample, re.I)),
                    "barrel": bool(re.search(r"barrel", body_sample, re.I)),
                    "glide_force": bool(
                        re.search(
                            r"glide\s*force|injection\s*force|break.?loose",
                            body_sample,
                            re.I,
                        )
                    ),
                    "hagen": bool(re.search(r"hagen|poiseuille", body_sample, re.I)),
                    "friction": bool(re.search(r"friction", body_sample, re.I)),
                    "newtonian": bool(re.search(r"newtonian", body_sample, re.I)),
                },
            }
        )

    out = Path("docs/_table_extract_preview.json")
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print("papers", len(results))
    for r in results:
        if "error" in r:
            print(r["file"], "ERROR", r["error"])
            continue
        print()
        print(
            "===",
            r["pmcid"],
            "|",
            r["n_tables"],
            "tables |",
            (r["title"] or "")[:80],
        )
        print("  DOI:", r["doi"])
        print("  body:", r["body_mentions"])
        for t in r["tables"]:
            s = t["scores"]
            hits = [k for k, v in s.items() if v and k != "core_hit_count"]
            print(
                f"  {t['label'] or '?'}: {(t['caption'] or '')[:90]!r} "
                f"rows={t['n_rows']} core={s['core_hit_count']} hits={hits}"
            )


if __name__ == "__main__":
    main()
