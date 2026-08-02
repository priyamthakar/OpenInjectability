"""Analyze raw Zenodo/Figshare search for Phase-D relevance; inspect Felfeli XLSX deeply."""
from __future__ import annotations

import json
from pathlib import Path

import openpyxl

RAW = Path(__file__).resolve().parent / "_repo_deep_pull_raw.json"
XLSX = Path(__file__).resolve().parent / "_tmp_felfeli_force.xlsx"
OUT = Path(__file__).resolve().parent / "_repo_deep_pull_analysis.json"


def main():
    raw = json.loads(RAW.read_text(encoding="utf-8"))

    need = [
        "injection force",
        "glide force",
        "plunger",
        "syringe force",
        "extrusion force",
        "break-loose",
        "break loose",
        "injectability",
        "syringeability",
        "hagen",
        "poiseuille",
    ]
    noise = [
        "syringe services",
        "ssp",
        "harm reduction",
        "muscle",
        "sarcomere",
        "lava",
        "liquefaction",
        "cement",
        "bone",
        "molecular dynamics",
        "force field",
        "polymer",
        "covert",
        "topology",
        "blood viscosity",
        "multigrade oil",
        "tamarind",
    ]

    cands = raw["candidates_for_download_inspect"]
    scored = []
    for c in cands:
        blob = " ".join(
            [
                str(c.get("title") or ""),
                str(c.get("description_snip") or ""),
                " ".join(c.get("keywords") or []) if c.get("keywords") else "",
                " ".join(c.get("file_keys") or []),
            ]
        ).lower()
        score = sum(2 for k in need if k in blob)
        score -= sum(3 for n in noise if n in blob)
        if "syringe" in blob and "force" in blob:
            score += 1
        if "viscosity" in blob or "glycerol" in blob:
            score += 1
        if any(
            k.lower().endswith((".csv", ".xlsx", ".xls", ".tsv"))
            for k in (c.get("file_keys") or [])
        ):
            score += 2
        scored.append({"score": score, **c})

    scored.sort(key=lambda x: -x["score"])

    # Title scan across all hits
    interesting = []
    seen = set()
    for qe in raw["zenodo_queries"]:
        for h in qe.get("hits") or []:
            title = (h.get("title") or "").lower()
            if h.get("id") in seen:
                continue
            if any(
                x in title
                for x in [
                    "injection force",
                    "glide force",
                    "injectability",
                    "syringeability",
                    "syringe force",
                    "plunger force",
                    "extrusion force",
                    "break-loose",
                    "hagen-poiseuille",
                ]
            ):
                seen.add(h.get("id"))
                interesting.append({"matched_query": qe["query"], **h})

    # Zenodo query totals summary
    query_summary = []
    for qe in raw["zenodo_queries"]:
        query_summary.append(
            {
                "query": qe["query"],
                "type_filter": qe.get("type_filter"),
                "total": qe.get("total"),
                "returned": len(qe.get("hits") or []),
                "error": qe.get("error"),
                "sample_titles": [(h.get("id"), (h.get("title") or "")[:100]) for h in (qe.get("hits") or [])[:5]],
            }
        )

    # Felfeli deep column inspect
    felfeli = None
    if XLSX.exists():
        wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
        sheet = wb.sheetnames[0]
        ws = wb[sheet]
        rows = list(ws.iter_rows(values_only=True))
        header = rows[1] if len(rows) > 1 else None
        data_rows = rows[2:] if len(rows) > 2 else []
        # unique values for key cols
        col_idx = {name: i for i, name in enumerate(header or []) if name is not None and not isinstance(name, (int, float))}
        uniques = {}
        for col in ["syringe", "fluid_density", "needle", "type"]:
            if col in col_idx:
                i = col_idx[col]
                uniques[col] = sorted({str(r[i]) for r in data_rows if r and r[i] is not None})
        # sample exact rows (first 5 full summary cols only)
        sample = []
        for r in data_rows[:8]:
            if not r:
                continue
            sample.append(
                {
                    "date": r[0],
                    "syringe": r[1],
                    "fluid_density": r[2],
                    "EYEID": r[3],
                    "type": r[4],
                    "needle": r[5],
                    "IOP_prior": r[6],
                    "IOP_post": r[7],
                    "inj_max": r[8],
                    "inj_mean": r[9],
                    "inj_time": r[10],
                    "reflux": r[11],
                }
            )
        felfeli = {
            "sheet": sheet,
            "n_data_rows": len([r for r in data_rows if r and r[0]]),
            "header_row": [str(x) if x is not None else None for x in (header or [])[:20]],
            "summary_columns": [
                "date",
                "syringe",
                "fluid_density",
                "EYEID",
                "type",
                "needle",
                "IOP_prior",
                "IOP_post",
                "inj_max",
                "inj_mean",
                "inj_time",
                "reflux",
            ],
            "time_series": "columns Time (s) -> then 0, 0.5, ... force/pressure samples",
            "unique_values": uniques,
            "sample_rows": sample,
            "notes": "Values under raw time series appear numeric pressure-like (inj_max ~87-177); not SI force N confirmed from file alone; labeled as raw injection pressure over time in header row 1.",
        }
        wb.close()

    # Figshare targeted summary
    figshare = raw.get("figshare_targeted") or []

    # Evaluate whether any Phase-D complete
    phase_d_complete = False

    analysis = {
        "zenodo_query_summary": query_summary,
        "exact_phrase_zeros": [
            q["query"] for q in query_summary if q.get("total") == 0
        ],
        "interesting_title_hits": interesting,
        "top_scored_candidates": scored[:20],
        "n_candidates": len(scored),
        "positive_score_count": sum(1 for s in scored if s["score"] > 0),
        "figshare_targeted": figshare,
        "felfeli_xlsx_inspect": felfeli,
        "phase_d_complete_dataset_found": phase_d_complete,
        "verdict_notes": (
            "Exact-phrase Zenodo queries for injection/glide force + syringe returned 0 hits. "
            "Broad keyword dataset searches return thousands of false positives (SSP directories, MD glycerol, "
            "lava dome, cement injectability). No Zenodo deposit with experimental syringe fluid-resistance "
            "force CSV/XLS vs viscosity+geometry. Figshare 32195520 XLSX downloadable with real force/pressure "
            "time series but tissue IVI, gauge-only, no F_fluid. Figshare 20800108 DOCX delivery-time stats only."
        ),
    }
    OUT.write_text(json.dumps(analysis, indent=2), encoding="utf-8")
    print("Wrote", OUT)
    print("exact phrase zeros:", analysis["exact_phrase_zeros"])
    print("interesting titles:", len(interesting))
    for h in interesting[:15]:
        print(" ", h.get("id"), (h.get("title") or "")[:100])
    print("top scores:")
    for s in scored[:10]:
        print(" ", s["score"], s.get("id"), (s.get("title") or "")[:90])
    if felfeli:
        print("Felfeli rows:", felfeli["n_data_rows"], "uniques:", felfeli["unique_values"])
        for r in felfeli["sample_rows"][:3]:
            print(" sample:", r)


if __name__ == "__main__":
    main()
