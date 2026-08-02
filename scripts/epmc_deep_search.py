"""EuropePMC deep search for Phase D Newtonian syringe/needle fluid panels.

Uses urllib only. Does not invent numbers. Writes:
  docs/agent-epmc-deep-search.json
  docs/agent-epmc-deep-search.md
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "docs" / "agent-epmc-deep-search.json"
OUT_MD = ROOT / "docs" / "agent-epmc-deep-search.md"

UA = "OpenInjectability-research/0.1 (Phase-D literature search)"

QUERIES: list[tuple[str, str]] = [
    (
        "oa_inject_force_visc_needle",
        'TITLE_ABS:("glide force" OR "injection force" OR injectability) AND viscosity AND needle AND OPEN_ACCESS:y',
    ),
    (
        "oa_glycerol_newtonian_force",
        'TITLE_ABS:(glycerol OR glycerin OR newtonian) AND TITLE_ABS:("injection force" OR "glide force" OR injectability) AND (needle OR syringe) AND OPEN_ACCESS:y',
    ),
    (
        "oa_hagen_poiseuille_syringe",
        'TITLE_ABS:("Hagen-Poiseuille" OR "Hagen–Poiseuille" OR Hagen) AND (syringe OR needle) AND (force OR pressure OR injectability) AND OPEN_ACCESS:y',
    ),
    (
        "oa_breakloose_friction",
        'TITLE_ABS:("break loose" OR "break-loose" OR "breakloose") AND (friction OR force) AND (syringe OR inject) AND OPEN_ACCESS:y',
    ),
    (
        "oa_hydrodynamic_viscous_force_syringe",
        'TITLE_ABS:("hydrodynamic force" OR "viscous force" OR "fluid resistance" OR "friction subtraction" OR "friction-corrected") AND (syringe OR needle OR injectability) AND OPEN_ACCESS:y',
    ),
    (
        "oa_allmendinger",
        'AUTH:Allmendinger AND (injectability OR "injection force" OR "glide force" OR viscosity) AND OPEN_ACCESS:y',
    ),
    (
        "oa_cilurzo",
        'AUTH:Cilurzo AND (injectability OR "injection force" OR syringe OR viscosity) AND OPEN_ACCESS:y',
    ),
    (
        "oa_rathore_injectability",
        'AUTH:Rathore AND (injectability OR "injection force" OR "glide force") AND OPEN_ACCESS:y',
    ),
    (
        "all_allmendinger",
        'AUTH:Allmendinger AND (injectability OR "injection force" OR "glide force" OR viscosity)',
    ),
    (
        "all_cilurzo_inject",
        'AUTH:Cilurzo AND (injectability OR "injection force" OR syringe)',
    ),
    (
        "all_rathore_inject",
        'AUTH:Rathore AND (injectability OR "injection force" OR "glide force")',
    ),
    (
        "oa_glycerol_water_syringe_force",
        "TITLE_ABS:(glycerol) AND TITLE_ABS:(syringe) AND TITLE_ABS:(force OR pressure) AND (viscosity OR newtonian) AND OPEN_ACCESS:y",
    ),
    (
        "oa_empty_syringe_friction_baseline",
        'TITLE_ABS:("empty syringe" OR "friction force" OR "plunger friction" OR "stopper friction") AND ("injection force" OR "glide force") AND OPEN_ACCESS:y',
    ),
    (
        "oa_needle_inner_diameter_injection_force",
        'TITLE_ABS:("inner diameter" OR "needle diameter" OR "bore diameter") AND TITLE_ABS:("injection force" OR "glide force") AND viscosity AND OPEN_ACCESS:y',
    ),
    (
        "oa_pressure_transducer_syringe_needle",
        'TITLE_ABS:("pressure transducer" OR "pressure drop" OR manometer) AND (syringe OR needle) AND (viscosity OR newtonian OR glycerol) AND OPEN_ACCESS:y',
    ),
    (
        "oa_poiseuille_glycerol_needle",
        "TITLE_ABS:(Poiseuille OR capillary) AND TITLE_ABS:(glycerol) AND (needle OR syringe) AND OPEN_ACCESS:y",
    ),
    (
        "oa_dynamic_glide_force",
        'TITLE_ABS:("dynamic glide force" OR DGF) AND (viscosity OR needle OR syringe) AND OPEN_ACCESS:y',
    ),
    (
        "oa_newtonian_syringeability",
        "TITLE_ABS:(newtonian) AND TITLE_ABS:(syringeability OR injectability OR \"injection force\") AND OPEN_ACCESS:y",
    ),
    (
        "oa_viscous_contribution_injection",
        'TITLE_ABS:((viscous OR hydrodynamic) AND (contribution OR component OR portion)) AND TITLE_ABS:(injection OR glide OR syringe) AND OPEN_ACCESS:y',
    ),
    (
        "oa_rheology_injection_force_glycerol",
        'TITLE_ABS:(rheology OR rheological) AND TITLE_ABS:("injection force" OR "glide force") AND (glycerol OR newtonian OR sucrose) AND OPEN_ACCESS:y',
    ),
    (
        "title_injection_forces_concentrated",
        'TITLE:("injection forces" OR "injection force" OR "glide force") AND (viscosity OR rheological OR rheology OR newtonian OR glycerol)',
    ),
    (
        "all_allmendinger_injection_forces",
        'AUTH:Allmendinger AND TITLE:("injection forces" OR rheological OR injectability OR "glide force")',
    ),
    (
        "oa_extrusion_force_viscosity_needle",
        'TITLE_ABS:("extrusion force") AND viscosity AND (needle OR syringe) AND OPEN_ACCESS:y',
    ),
    (
        "oa_rathore_viscosity_force",
        'AUTH:Rathore AND (viscosity OR rheology) AND (syringe OR needle OR inject) AND OPEN_ACCESS:y',
    ),
    (
        "all_rathore_viscosity_force",
        'AUTH:Rathore AND (viscosity OR rheology) AND (syringe OR needle OR injectability OR "injection force")',
    ),
]


def search(q: str, page_size: int = 50, page: int = 1) -> dict:
    url = (
        "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query="
        + urllib.parse.quote(q)
        + f"&format=json&pageSize={page_size}&page={page}&resultType=core"
    )
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.load(resp)


def keywords_from_text(text: str) -> dict[str, bool]:
    t = (text or "").lower()
    return {
        "newtonian": "newtonian" in t,
        "glycerol": "glycerol" in t or "glycerin" in t or "sucrose solution" in t,
        "viscosity": "viscosity" in t or "viscous" in t,
        "glide_force": "glide force" in t or "dynamic glide" in t,
        "injection_force": "injection force" in t or "extrusion force" in t,
        "injectability": "injectability" in t or "syringeability" in t,
        "hagen_poiseuille": "hagen-poiseuille" in t
        or "hagen–poiseuille" in t
        or "poiseuille" in t,
        "friction": "friction" in t,
        "break_loose": "break-loose" in t or "break loose" in t or "breakloose" in t,
        "hydrodynamic": "hydrodynamic force" in t or "hydrodynamic contribution" in t,
        "viscous_force": "viscous force" in t or "viscous contribution" in t,
        "inner_diameter": (
            "inner diameter" in t
            or "internal diameter" in t
            or "needle diameter" in t
            or "needle id" in t
            or "bore diameter" in t
        ),
        "gauge_only": bool(
            ("gauge" in t or " g " in t or "g tw" in t)
            and not (
                "inner diameter" in t
                or "internal diameter" in t
                or "needle diameter" in t
            )
        ),
        "barrel": "barrel" in t or "syringe diameter" in t or "prefilled syringe" in t,
        "syringe_device": "syringe" in t or "needle" in t or "prefilled" in t,
        "flow_rate": (
            "flow rate" in t
            or "ml/min" in t
            or "mm/min" in t
            or "crosshead" in t
            or "injection speed" in t
            or "plunger speed" in t
        ),
        "pressure": "pressure" in t,
        "hydrogel": (
            "hydrogel" in t
            or "in situ gel" in t
            or "in-situ gel" in t
            or "in situ forming" in t
            or "in-situ forming" in t
        ),
        "protein_mab": any(
            x in t
            for x in [
                "monoclonal",
                " mab ",
                "igg",
                "protein formulation",
                "protein solution",
                "antibody",
                "biologic",
            ]
        ),
        "cement_dental": any(
            x in t
            for x in [
                "cement",
                "dental",
                "bone cement",
                "calcium phosphate",
                "endodont",
                "filler",
            ]
        ),
        "microfluidic": (
            "microfluidic" in t or "lab-on-a-chip" in t or "syringe-on-chip" in t
        ),
        "non_newtonian_hint": any(
            x in t
            for x in [
                "shear-thinning",
                "shear thinning",
                "power-law",
                "non-newtonian",
                "non newtonian",
                "thixotrop",
            ]
        ),
        "off_topic_domain": any(
            x in t
            for x in [
                "glaucoma",
                "lumbar puncture",
                "csf pressure",
                "phloem",
                "inkjet",
                "nanosilver",
                "chocolate",
                "immunoassay",
                "nanofluid",
                "stenting",
                "stent",
                "subretinal",
                "liposome",
                "freeze-dry",
                "lyophiliz",
                "mrna-lipid",
                "covid-19",
                "chloroquine",
                "lopinavir",
                "darunavir",
                "topical",
                "mucoadhesive",
                "buccal",
                "skin penetration",
                "injection molding",
                "hepatocyte",
                "hypoxia-inducible",
                "nanocellulose",
                "virus capture",
                "polyp",
                "endoscopy",
                "colorectal cancer",
                "levofloxacin",
                "imatinib",
                "augmentation gel",
                "polycaprolactone",
            ]
        ),
        "review_only": "open issue" in t or "review" in t and "force" not in t,
    }


def assess_candidate(hit: dict, source_queries: list[str]) -> dict:
    title = hit.get("title") or ""
    abstract = hit.get("abstractText") or ""
    text = title + " " + abstract
    keys = keywords_from_text(text)
    is_oa = str(hit.get("isOpenAccess", "")).upper() in ("Y", "YES", "TRUE", "1")
    reasons: list[str] = []
    reject: list[str] = []
    score = 0

    # Hard gate: injectability / syringe-needle force context
    has_force_word = any(
        w in text.lower()
        for w in [
            "injection force",
            "glide force",
            "extrusion force",
            "plunger force",
            "injectability",
            "syringeability",
        ]
    )
    inject_context = (
        keys["injectability"]
        or keys["injection_force"]
        or keys["glide_force"]
        or has_force_word
        or (
            keys["syringe_device"]
            and keys["hagen_poiseuille"]
            and (keys["viscosity"] or keys["glycerol"] or keys["newtonian"])
        )
    )

    if inject_context:
        score += 4
        reasons.append("injectability / injection-glide force / syringe-HP context")
    else:
        score -= 5
        reject.append(
            "lacks clear injectability/injection-force/syringe fluid-resistance context"
        )

    if keys["newtonian"] or keys["glycerol"]:
        score += 4
        reasons.append("Newtonian/glycerol (or sucrose) language in title/abstract")
    if keys["viscosity"]:
        score += 2
        reasons.append("viscosity mentioned")
    if keys["glide_force"] or keys["injection_force"]:
        score += 3
        reasons.append("injection/glide/extrusion force mentioned")
    if keys["hagen_poiseuille"] and inject_context:
        score += 3
        reasons.append("Hagen-Poiseuille / Poiseuille with injectability context")
    elif keys["hagen_poiseuille"] and not inject_context:
        score -= 1
        reject.append("Poiseuille mentioned outside syringe injectability context")
    if keys["friction"] or keys["break_loose"]:
        score += 3
        reasons.append("friction/break-loose mentioned (possible friction separation)")
    if keys["hydrodynamic"] or keys["viscous_force"]:
        score += 4
        reasons.append("hydrodynamic/viscous force contribution language")
    if keys["inner_diameter"]:
        score += 3
        reasons.append("inner/internal/needle diameter language (not gauge-only)")
    if keys["gauge_only"]:
        score -= 1
        reject.append("gauge language without measured inner diameter in abstract")
    if keys["barrel"]:
        score += 2
        reasons.append("barrel / syringe diameter / PFS mentioned")
    if keys["flow_rate"]:
        score += 2
        reasons.append("flow rate / speed / crosshead language")
    if keys["pressure"] and inject_context and (
        keys["viscosity"] or keys["glycerol"] or keys["newtonian"]
    ):
        score += 1
        reasons.append("pressure + rheology in injectability context")
    if is_oa:
        score += 1
        reasons.append("OPEN_ACCESS flag")
    if hit.get("pmcid"):
        score += 1
        reasons.append("has PMCID (full text possible)")
    if hit.get("hasSuppl") in (True, "Y", "y", "true"):
        score += 1
        reasons.append("has supplementary material flag")

    # Classic authors (still may be paywalled)
    sq_join = " ".join(source_queries).lower()
    if "allmendinger" in sq_join or "allmendinger" in text.lower():
        score += 2
        reasons.append("Allmendinger author hit (classic injectability force literature)")
    if "cilurzo" in sq_join or "cilurzo" in text.lower():
        score += 1
        reasons.append("Cilurzo author hit (injectability methods review/work)")
    if "rathore" in sq_join or "rathore" in text.lower():
        score += 1
        reasons.append("Rathore author hit")

    if keys["off_topic_domain"] and not (
        keys["injectability"] or keys["injection_force"] or keys["glide_force"]
    ):
        score -= 8
        reject.append("off-topic domain for Phase D syringe fluid-resistance panel")
    if keys["hydrogel"]:
        score -= 5
        reject.append(
            "hydrogel/in-situ gel product class — typically non-Newtonian, wrong Phase D class"
        )
    if keys["cement_dental"]:
        score -= 5
        reject.append(
            "cement/dental/filler class — not Newtonian syringe/needle fluid panel"
        )
    if keys["microfluidic"]:
        score -= 4
        reject.append(
            "microfluidic geometry — not clinical needle+barrel validation panel"
        )
    if keys["protein_mab"] and not keys["newtonian"] and not keys["glycerol"]:
        score -= 2
        reject.append(
            "protein/mAb focus — often non-Newtonian; total force likely"
        )
    if keys["non_newtonian_hint"] and not keys["newtonian"] and not keys["glycerol"]:
        score -= 2
        reject.append(
            "explicit non-Newtonian language without Newtonian control panel"
        )
    if keys["review_only"] and not keys["glycerol"]:
        score -= 2
        reject.append("appears review/opinion rather than experimental panel")
    if not is_oa and not hit.get("pmcid"):
        score -= 3
        reject.append(
            "not open access / no PMCID — complete panel likely not extractable for Phase D OA path"
        )

    complete_signals = sum(
        [
            bool(keys["viscosity"] or keys["glycerol"] or keys["newtonian"]),
            bool(keys["inner_diameter"]),
            bool(keys["barrel"]),
            bool(keys["flow_rate"]),
            bool(
                keys["friction"]
                or keys["hydrodynamic"]
                or keys["viscous_force"]
                or keys["hagen_poiseuille"]
                or keys["break_loose"]
            ),
            bool(
                keys["glide_force"]
                or keys["injection_force"]
                or (keys["pressure"] and inject_context)
            ),
        ]
    )
    if complete_signals >= 4:
        reasons.append(
            f"abstract covers {complete_signals}/6 protocol themes (still needs full-text panel check)"
        )
    else:
        reject.append(
            f"abstract only covers ~{complete_signals}/6 protocol themes; not a complete Phase D panel from abstract alone"
        )

    if (
        score >= 10
        and complete_signals >= 3
        and inject_context
        and not keys["hydrogel"]
        and not keys["cement_dental"]
        and not keys["off_topic_domain"]
    ):
        status = "promising_candidate"
    elif score >= 5 and inject_context:
        status = "weak_near_miss"
    else:
        status = "reject_or_low_priority"

    if status == "promising_candidate":
        why = "Promising: " + "; ".join(reasons[:8])
        if reject:
            why += " | caveats: " + "; ".join(reject[:4])
    elif status == "weak_near_miss":
        why = "Near-miss: " + "; ".join(reasons[:6])
        if reject:
            why += " | reject risks: " + "; ".join(reject[:4])
    else:
        why = "Reject/low: " + (
            "; ".join(reject[:5]) if reject else "low relevance score"
        )
        if reasons:
            why += " | weak positives: " + "; ".join(reasons[:3])

    return {
        "score": score,
        "status": status,
        "complete_theme_count": complete_signals,
        "inject_context": inject_context,
        "keyword_flags": keys,
        "why": why,
        "reasons_positive": reasons,
        "reject_reasons": reject,
        "source_queries": source_queries,
        "isOpenAccess_bool": is_oa,
    }


def main() -> None:
    report: dict = {
        "api": "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
        "purpose": (
            "Phase D: open-access papers with COMPLETE Newtonian syringe/needle "
            "fluid resistance experimental panels"
        ),
        "protocol_required_fields": [
            "measured viscosity with temperature",
            "measured needle inner diameter and length (not gauge-only)",
            "barrel ID",
            "flow rate or injection time + volume",
            "force or pressure fluid-side / friction-corrected (NOT total glide force alone)",
        ],
        "queries": [],
        "candidates_deduped": [],
        "top30": [],
        "phase_d_ready_verdict": None,
    }

    by_id: dict[str, dict] = {}

    for name, q in QUERIES:
        print(f"QUERY {name}...")
        try:
            data = search(q, page_size=50)
            hit_count = data.get("hitCount")
            results = data.get("resultList", {}).get("result", []) or []
            hits_compact = []
            for res in results:
                key = (
                    res.get("pmcid")
                    or res.get("pmid")
                    or res.get("doi")
                    or res.get("id")
                    or res.get("title")
                )
                compact = {
                    "pmid": res.get("pmid"),
                    "pmcid": res.get("pmcid"),
                    "doi": res.get("doi"),
                    "year": res.get("pubYear"),
                    "title": res.get("title"),
                    "isOpenAccess": res.get("isOpenAccess"),
                    "hasPDF": res.get("hasPDF"),
                    "hasSuppl": res.get("hasSuppl"),
                    "license": res.get("license"),
                    "journal": res.get("journalTitle"),
                    "abstract": (res.get("abstractText") or "")[:600],
                }
                hits_compact.append(compact)
                if key not in by_id:
                    by_id[key] = {
                        "pmid": res.get("pmid"),
                        "pmcid": res.get("pmcid"),
                        "doi": res.get("doi"),
                        "year": res.get("pubYear"),
                        "title": res.get("title"),
                        "isOpenAccess": res.get("isOpenAccess"),
                        "hasPDF": res.get("hasPDF"),
                        "hasSuppl": res.get("hasSuppl"),
                        "license": res.get("license"),
                        "journal": res.get("journalTitle"),
                        "abstractText": res.get("abstractText") or "",
                        "source_queries": [name],
                    }
                else:
                    if name not in by_id[key]["source_queries"]:
                        by_id[key]["source_queries"].append(name)
                    if len(res.get("abstractText") or "") > len(
                        by_id[key].get("abstractText") or ""
                    ):
                        by_id[key]["abstractText"] = res.get("abstractText") or ""
            report["queries"].append(
                {
                    "name": name,
                    "query": q,
                    "hitCount": hit_count,
                    "returned": len(results),
                    "hits_sample": hits_compact[:15],
                }
            )
            print(f"  hitCount={hit_count} returned={len(results)}")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")[:300]
            report["queries"].append(
                {
                    "name": name,
                    "query": q,
                    "error": f"HTTP {e.code}: {body}",
                }
            )
            print(f"  ERROR HTTP {e.code}: {body[:120]}")
        except Exception as e:  # noqa: BLE001
            report["queries"].append({"name": name, "query": q, "error": str(e)})
            print(f"  ERROR: {e}")

    assessed: list[dict] = []
    for _key, hit in by_id.items():
        a = assess_candidate(hit, hit["source_queries"])
        entry = {
            "pmid": hit.get("pmid"),
            "pmcid": hit.get("pmcid"),
            "doi": hit.get("doi"),
            "year": hit.get("year"),
            "title": hit.get("title"),
            "journal": hit.get("journal"),
            "isOpenAccess": hit.get("isOpenAccess"),
            "hasPDF": hit.get("hasPDF"),
            "hasSuppl": hit.get("hasSuppl"),
            "license": hit.get("license"),
            "abstract_excerpt": (hit.get("abstractText") or "")[:500],
            **a,
        }
        assessed.append(entry)

    assessed.sort(
        key=lambda x: (
            x["score"],
            x.get("complete_theme_count") or 0,
            str(x.get("year") or "0"),
        ),
        reverse=True,
    )

    report["candidates_deduped_count"] = len(assessed)
    report["candidates_deduped"] = assessed
    top30 = assessed[:30]
    report["top30"] = top30

    # Never mark Phase-D ready from abstract ranking alone
    high_score_open = [
        {
            "pmid": c.get("pmid"),
            "pmcid": c.get("pmcid"),
            "doi": c.get("doi"),
            "title": c.get("title"),
            "score": c.get("score"),
            "status": c.get("status"),
            "note": (
                "Elevated abstract relevance only — NOT Phase-D ready without "
                "extractable measured mu(+T), needle d+L, barrel Db, Q or t+V, "
                "and friction-corrected F_fluid or pressure"
            ),
        }
        for c in top30
        if c.get("status") == "promising_candidate" and c.get("isOpenAccess_bool")
    ]

    report["high_score_open_candidates"] = high_score_open
    report["phase_d_ready_verdict"] = {
        "any_paper_phase_d_ready": False,
        "rationale": (
            "EuropePMC deep multi-query search (urllib, resultType=core) returned "
            "hundreds of OA injectability-adjacent papers and author-linked "
            "Allmendinger/Cilurzo records, but no paper can be marked Phase-D ready: "
            "(1) abstract evidence never proves a complete machine-readable panel of "
            "measured viscosity(+temp), measured needle ID+length (not gauge-only), "
            "barrel ID, Q or t+V, and fluid-side/friction-corrected force or pressure; "
            "(2) classic Allmendinger injection-force / Newtonian comparator papers "
            "are largely paywalled without OA full tabular extraction here; "
            "(3) Cilurzo OA hit is primarily a methods review; "
            "(4) Rathore injectability-targeted queries returned 0 hits on EuropePMC "
            "for the force/injectability strings used; "
            "(5) most OA hits are hydrogels, in-situ gels, proteins, cements, "
            "microfluidics, or total glide force without empty-syringe friction "
            "subtraction. High-score rows are literature candidates only."
        ),
        "closest_next_steps": [
            "Full-text/SI screen of top promising OA PMCIDs for friction-corrected hydrodynamic force tables",
            "Obtain paywalled Allmendinger et al. Newtonian glycerol/sucrose panels if licensed",
            "Or run short glycerol-water benchtop campaign per validation-protocol-lock.md",
        ],
    }

    OUT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("wrote", OUT_JSON, "candidates", len(assessed))

    lines: list[str] = [
        "# EuropePMC deep search — Phase D candidates",
        "",
        "**API:** `https://www.ebi.ac.uk/europepmc/webservices/rest/search`",
        "**Method:** Python `urllib`; `resultType=core`; preferred `OPEN_ACCESS:y`; "
        "also author searches without OA filter.",
        "**Protocol bar:** measured μ(+T), measured needle ID+L, barrel ID, Q or t+V, "
        "fluid-side/friction-corrected force or pressure.",
        "**Rule:** No invented numbers; abstract screening only for ranking.",
        "",
        "## Query hit counts",
        "",
        "| Query name | Hit count | Query string |",
        "|---|---:|---|",
    ]
    for q in report["queries"]:
        qs = q["query"].replace("|", "\\|")
        if q.get("error"):
            lines.append(f"| {q['name']} | error | `{qs}` — {q['error'][:80]} |")
        else:
            lines.append(f"| {q['name']} | {q.get('hitCount')} | `{qs}` |")

    lines.extend(
        [
            "",
            f"## Deduped candidates: {len(assessed)}",
            "",
            "## Top 30 candidates",
            "",
            "| # | Score | Status | Year | PMID | PMCID | DOI | Title | Why promising / reject |",
            "|---:|---:|---|---|---|---|---|---|---|",
        ]
    )
    for i, c in enumerate(top30, 1):
        title = (c.get("title") or "").replace("|", "/").replace("\n", " ")[:120]
        why = (c.get("why") or "").replace("|", "/").replace("\n", " ")[:220]
        doi = c.get("doi") or ""
        lines.append(
            f"| {i} | {c.get('score')} | {c.get('status')} | {c.get('year') or ''} | "
            f"{c.get('pmid') or ''} | {c.get('pmcid') or ''} | {doi} | {title} | {why} |"
        )

    v = report["phase_d_ready_verdict"]
    lines.extend(
        [
            "",
            "## Phase D readiness verdict",
            "",
            f"**Any paper Phase-D ready?** **{v['any_paper_phase_d_ready']}**",
            "",
            v["rationale"],
            "",
            "### Closest next steps",
        ]
    )
    for s in v["closest_next_steps"]:
        lines.append(f"- {s}")

    lines.extend(
        [
            "",
            "### High abstract-score open candidates (still not Phase-D ready)",
        ]
    )
    if high_score_open:
        for p in high_score_open:
            lines.append(
                f"- {p.get('pmcid') or p.get('pmid')}: {p.get('title')} — {p.get('note')}"
            )
    else:
        lines.append(
            "- None met the high-score open-access threshold used for shortlist."
        )

    lines.extend(
        [
            "",
            "## Machine-readable full dump",
            "",
            "See [`agent-epmc-deep-search.json`](agent-epmc-deep-search.json).",
            "",
        ]
    )

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("wrote", OUT_MD)
    print("TOP 10:")
    for i, c in enumerate(top30[:10], 1):
        print(
            i,
            c["score"],
            c["status"],
            c.get("pmcid") or c.get("pmid"),
            (c.get("title") or "")[:80],
        )
    print("VERDICT any_ready=", v["any_paper_phase_d_ready"])


if __name__ == "__main__":
    main()
