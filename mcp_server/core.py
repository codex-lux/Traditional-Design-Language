"""Traditional Design Language — query core.

Pure functions over the corpus. The MCP server is a thin wrapper on this, so the same
logic is testable without a protocol and reusable from a notebook or a platform.

Design rule throughout: return the SMALLEST thing that answers the question, and tell the
caller what else is available. An agent consulting this mid-conversation has a context
budget, and a tool that returns 40 KB when 400 bytes would do is worse than no tool.
"""
from __future__ import annotations
import json, os, glob, re, functools, math, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _mod(name, path):
    """Load a sibling module by path, once per process.

    Delegates to build/modcache.py (OQ 28): the by-path pattern this corpus
    uses everywhere returns a fresh module object per call, which meant
    _data()'s lru_cache below was rebuilt from the whole corpus on every
    entry point. Same signature and same standalone behaviour, one execution.
    """
    import sys as _sys
    _b = os.path.join(ROOT, "build")
    if _b not in _sys.path:
        _sys.path.insert(0, _b)
    import modcache as _mc
    return _mc.load(name, path)

def _load_engine():
    return _mod("pe", os.path.join(ROOT, "build", "proportion_engine.py"))

@functools.lru_cache(maxsize=1)
def _data():
    styles = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "styles", "*.json"))):
        n = json.load(open(f)); styles[n["id"]] = n
    faults = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "faults", "*.json"))):
        n = json.load(open(f)); faults[n["id"]] = n
    slots, groups = {}, []
    sd = json.load(open(os.path.join(ROOT, "elements", "slots.json")))
    for g in sd["groups"]:
        groups.append({"id": g["id"], "name": g["name"], "count": len(g["slots"])})
        for s in g["slots"]: slots[s["id"]] = {**s, "group": g["id"], "group_name": g["name"]}
    massings = {m["id"]: m for m in json.load(open(os.path.join(ROOT, "massings", "catalog.json")))}
    try: assets = json.load(open(os.path.join(ROOT, "assets", "manifest.json")))["assets"]
    except Exception: assets = []
    kits = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "kits", "*.kit.json"))):
        k = json.load(open(f)); kits[k["style"]] = k
    rooms, groupings = {}, {}
    for f in sorted(glob.glob(os.path.join(ROOT, "rooms", "*.json"))):
        r = json.load(open(f)); rooms[r["id"]] = r
    for f in sorted(glob.glob(os.path.join(ROOT, "groupings", "*.json"))):
        g = json.load(open(f)); groupings[g["id"]] = g
    return {"styles": styles, "faults": faults, "slots": slots, "groups": groups,
            "massings": massings, "assets": assets, "kits": kits,
            "rooms": rooms, "groupings": groupings,
            "ontology_version": sd["version"], "engine": _load_engine()}

_PARTIS_CACHE = None


def _disclosures():
    return _mod("disclosures", os.path.join(ROOT, "build", "disclosures.py"))


def _partis():
    """The parti records by id. `_data()` does not carry them — it is the STYLE-side corpus —
    and `load_parti` reads one by id from a caller-supplied string, which is deliberately the
    only path that joins a caller's value to a path (see its docstring). This is the read-all
    accessor, cached, used by the disclosure that asks whether the parti a plan names lists the
    style the sheet judged it as."""
    global _PARTIS_CACHE
    if _PARTIS_CACHE is None:
        out = {}
        for f in sorted(glob.glob(os.path.join(ROOT, "partis", "*.json"))):
            try:
                rec = json.load(open(f))
                out[rec["id"]] = rec
            except Exception:
                continue
        _PARTIS_CACHE = out
    return _PARTIS_CACHE


def _yr(v):
    if v is None: return "?"
    return f"{-v} BC" if v < 0 else str(v)

def _style_card(n):
    p = n["period"]
    return {"id": n["id"], "name": n["name"], "rank": n["rank"], "in": n.get("member_of"),
            "years": f"{_yr(p['floruit_start'])}–{_yr(p['floruit_end'])}",
            # The whole list, and a count where a reader can see it. `[:3]` was harmless
            # while this fed a one-line caption, and became a lie the moment anything drew
            # from it: 82 of 164 styles carry more than three regions, so a card showing
            # three of nine looked like a complete list with no ellipsis and no number. It is
            # the same truncation `corpus.py::phylogeny()` carried, fixed there this session
            # and missed here — the Phylogeny screen contradicted itself, the map placing a
            # style from its full region list while the panel beside it named three. Found by
            # an adversarial audit. Every consumer (find_style, get_style summary,
            # compare_styles, overview traditions, StyleRecord, the Phylogeny panel) gets the
            # list the record actually holds.
            "regions": n["geography"]["regions"],
            "short": n["description"]["short"]}

# ----------------------------------------------------------------- overview
def overview():
    D = _data(); S = D["styles"]; F = D["faults"]
    by_rank = {}
    for n in S.values(): by_rank[n["rank"]] = by_rank.get(n["rank"], 0) + 1
    packs = {}
    for p in D["engine"].PACKS.values(): packs[p["kind"]] = packs.get(p["kind"], 0) + 1
    filled = [k for k, v in D["kits"].items()
              if any(s.get("status") not in (None, "empty") for s in (v.get("slots") or {}).values())]
    return {
      "what_this_is": ("An evolutionary taxonomy of traditional architecture with an executable "
                       "proportioning grammar, a kit-of-parts directory per style, and a corpus of "
                       "named errors. Built to be consulted mid-conversation while advising a human "
                       "on a real house."),
      "how_to_use_it": [
        "1. tdl_find_style to locate a style, or tdl_compare_styles when the client is between two.",
        "2. tdl_get_style for the record; ask for the sections you need, not all of them.",
        "3. tdl_resolve_kit for what the style actually specifies, slot by slot, with the ancestor each value came from.",
        "4. tdl_get_proportions to dimension anything classical at a real module and ceiling height.",
        "5. tdl_find_room and tdl_get_grouping when the question is about the plan rather than the elevation.",
        "6. tdl_find_faults BEFORE recommending a detail, and tdl_check_measurements when you have numbers or a photograph.",
      ],
      "counts": {"styles": len(S), "by_rank": by_rank, "lineage_edges": sum(len(n.get("lineage", [])) for n in S.values()),
                 "element_slots": len(D["slots"]), "slot_groups": len(D["groups"]),
                 "massings": len(D["massings"]), "proportion_packs": packs,
                 "rooms": len(D["rooms"]), "room_groupings": len(D["groupings"]),
                 "faults": len(F), "faults_with_a_numeric_test": sum(1 for f in F.values() if f.get("test")),
                 "image_records": len(D["assets"]), "kits_populated": len(filled)},
      "the_model": {
        "ranks": "tradition > family > style > variant. Variant is where a kit is actually buildable.",
        "member_of": "single-parent containment, for browsing only. It does NOT carry inheritance.",
        "lineage": "a DAG with typed edges. Multiple parents are normal.",
        "edge_types": {
          "descends_from": "real transmission of building practice — carries the kit cascade",
          "regional_of": "variant to its parent style — carries the cascade",
          "hybridizes_with": "reticulation, a co-parent of comparable weight",
          "references": "CLAIMED ancestry, quoted without descent — does NOT carry the cascade",
          "reacts_against": "defined by inversion of a predecessor",
          "revives": "deliberate resurrection after a gap"},
        "why_it_matters": ("Greek Revival references Athens and descends from Federal practice via Asher "
                           "Benjamin's pattern books. If you let the reference edge carry construction, you "
                           "produce an archaeological reconstruction instead of the style someone asked for."),
        "massing_is_not_style": ("An American Foursquare can wear Craftsman, Colonial Revival or Prairie with no "
                                 "change of volume. Massings are a separate catalogue joined by affinity."),
        "rooms_and_groupings": ("Rooms are style-independent like massings — a parlor and a living room may be "
                                "the same volume doing different social work. What a room constrains is dimension, "
                                "daylight, adjacency and servicing. A GROUPING is the middle scale nobody designs "
                                "without: a hall-and-parlor pair, a service core, a primary suite, an entry sequence."),
        "a_style_is": ("a set of bindings and constraints on universal element slots, not a parts list. "
                       "Children inherit and override selectively, like a cascade."),
        "judgment_slots": ("Some rules are marked judgment:true because the sources do not determine them. "
                           "Say so to the human rather than inventing a number — a rules engine that cannot "
                           "admit ignorance will produce houses that violate no constraint and are still dead.")},
      "slot_groups": D["groups"],
      "ontology_version": D["ontology_version"],
      "traditions": [_style_card(S[i]) for i in
                     ["classical-mediterranean","british-isles","northern-european-vernacular",
                      "iberian-mediterranean","north-american"] if i in S],
      "kits_populated": filled,
    }

# ----------------------------------------------------------------- styles
def find_style(query="", rank=None, region=None, year=None, tradition=None, limit=20):
    D = _data(); q = (query or "").lower().strip()
    out = []
    for n in D["styles"].values():
        if rank and n["rank"] != rank: continue
        if year is not None and not (n["period"]["floruit_start"] - 30 <= year <= n["period"]["floruit_end"] + 30): continue
        if region and not any(region.lower() in r.lower() for r in n["geography"]["regions"]): continue
        if tradition:
            cur, ok = n, False
            for _ in range(6):
                if cur["id"] == tradition: ok = True; break
                cur = D["styles"].get(cur.get("member_of") or "", None)
                if not cur: break
            if not ok: continue
        score = 0
        if q:
            hay = " ".join([n["name"], n["id"], " ".join(n.get("aka", [])), n["description"]["short"],
                            " ".join(n.get("defining_characteristics", [])), " ".join(n.get("diagnostic_tells", [])),
                            " ".join(n["geography"]["regions"])]).lower()
            if q not in hay: continue
            score = (3 if q in n["name"].lower() else 0) + (2 if q in n["id"] else 0) + 1
        out.append((score, n))
    out.sort(key=lambda x: (-x[0], x[1]["period"]["floruit_start"]))
    return {"matches": len(out), "returned": min(limit, len(out)),
            "results": [_style_card(n) for _, n in out[:limit]],
            "next": "tdl_get_style with an id, or tdl_resolve_kit to see what a style specifies"}

STYLE_SECTIONS = ["summary","description","characteristics","lineage","proportion","massing",
                  "constraints","exemplars","sources"]

def get_style(style_id, sections=None):
    D = _data(); n = D["styles"].get(style_id)
    if not n:
        near = [s for s in D["styles"] if style_id.lower() in s][:6]
        return {"error": f"no style '{style_id}'", "did_you_mean": near,
                "hint": "use tdl_find_style to search by name, region, or year"}
    sec = sections or ["summary","description","characteristics","lineage"]
    out = {"id": n["id"], "available_sections": STYLE_SECTIONS}
    if "summary" in sec: out["summary"] = _style_card(n) | {"status": n.get("status"), "confidence": n.get("confidence")}
    if "description" in sec: out["description"] = n["description"]
    if "characteristics" in sec:
        out["defining_characteristics"] = n.get("defining_characteristics", [])
        out["diagnostic_tells"] = n.get("diagnostic_tells", [])
        out["distinguished_from"] = n.get("distinguished_from", [])
    if "lineage" in sec:
        out["lineage"] = n.get("lineage", [])
        out["descendants"] = [{"id": m["id"], "type": e["type"]} for m in D["styles"].values()
                              for e in m.get("lineage", []) if e["target"] == style_id]
        out["cascade"] = _cascade(style_id)
    if "proportion" in sec:
        out["proportion_packs"] = n.get("proportion_packs", [])
        out["proportional_system"] = n.get("proportional_system", {})
    if "massing" in sec:
        out["massing_affinities"] = [m | {"massing_name": D["massings"].get(m["massing"], {}).get("name")}
                                     for m in n.get("massing_affinities", [])]
    if "constraints" in sec: out["constraints"] = n.get("constraints", [])
    if "exemplars" in sec: out["exemplars"] = n.get("exemplars", [])
    if "sources" in sec: out["sources"] = n.get("sources", [])
    out["kit"] = f"tdl_resolve_kit('{style_id}')" if style_id in D["kits"] else "no kit directory"
    return out

def _cascade(i, seen=None):
    """The kit cascade, DELEGATED to `build/resolve_kit.chain_for` rather than re-walked.

    THIS WAS A SECOND AND TRUNCATED IMPLEMENTATION, and it had been one since 23 Aug. It
    walked `lineage` edges carrying `inherits_kit` and nothing else, so it never spliced in a
    style's FAMILY-rank ancestors -- which `build/build.py::family_of` has done for every
    style since WP-4.2, one day later. Measured 28 Aug 2026: all 132 buildable styles got a
    shorter chain here than in `resolve_kit.chain_for`, **1,308 ancestors dropped and 0
    added**, and the two disagreed about whether a slot is forbidden on **206 (style, slot)
    records**.

    It was served to users twice -- `tdl_resolve_kit`, which `tdl_overview` advertises as
    "what the style actually specifies, slot by slot", and `GET /api/kit/{style_id}`, the
    workbench Kit surface. Concretely: `resolve_kit('appalachian-log-house', slot='order')`
    answered `specified`, source `english-palladian`, canonical `ionic`, quoting Palladio's
    *I Quattro Libri* -- on an Appalachian log house -- because `nordic-alpine-vernacular`,
    which binds `order` FORBIDDEN, is a family node and was absent from this chain.

    And this file had become self-contradictory: WP-8.4 added `_resolved_kit()` below, which
    uses `rk.resolve_slots` and is right, so core.py carried two cascades and one of them was
    wrong. Two spellings of one rule is what this codebase has paid for four times.

    `_style_chain` (fault applicability) already walked `member_of` separately, so correcting
    this widens it too: measured at 7 additional fault applications corpus-wide, each one a
    fault written for a family reaching a member of it. Found by the WP-8.4 adversarial audit.

    Returns the ancestors, nearest first, WITHOUT the node itself -- the contract its three
    callers were written against (`[style_id] + _cascade(style_id)`).
    """
    rk, g = _kit_graph()
    if i not in (g.get("nodes") or {}):
        return []
    return [x for x in rk.chain_for(g, i) if x != i]

def compare_styles(a, b):
    D = _data()
    A, B = D["styles"].get(a), D["styles"].get(b)
    if not A or not B: return {"error": "unknown style id", "missing": [x for x, y in ((a, A), (b, B)) if not y]}
    dfrom = [d for d in A.get("distinguished_from", []) if d["node"] == b] + \
            [d for d in B.get("distinguished_from", []) if d["node"] == a]
    shared = set(_cascade(a)) & set(_cascade(b))
    return {"a": _style_card(A), "b": _style_card(B),
            "explicit_disambiguation": dfrom or "none recorded — fall back on the tells below",
            "tells_a": A.get("diagnostic_tells", []), "tells_b": B.get("diagnostic_tells", []),
            "shared_ancestry": sorted(shared),
            "a_descends_from_b": any(e["target"] == b for e in A.get("lineage", [])),
            "b_descends_from_a": any(e["target"] == a for e in B.get("lineage", []))}

# ----------------------------------------------------------------- slots & kits
def get_slot(slot_id):
    D = _data(); s = D["slots"].get(slot_id)
    if not s:
        return {"error": f"no slot '{slot_id}'",
                "did_you_mean": [k for k in D["slots"] if slot_id.lower() in k][:8],
                "hint": "tdl_overview lists the eight slot groups"}
    specifiers = []
    for sid, k in D["kits"].items():
        rec = (k.get("slots") or {}).get(slot_id)
        if rec and rec.get("status") not in (None, "empty"): specifiers.append(sid)
    faults = [{"id": f["id"], "name": f["name"], "severity": f["severity"], "frequency": f.get("frequency")}
              for f in D["faults"].values() if slot_id in f["slots"]]
    return {"slot": s, "specified_by_styles": specifiers,
            "faults_on_this_slot": sorted(faults, key=lambda x: ("fatal","serious","minor").index(x["severity"])),
            "note": "Slots are universal. A style does not own a cornice; it specifies one."}

def resolve_kit(style_id, group=None, slot=None, ceiling_height=108.0, only_specified=True):
    D = _data(); n = D["styles"].get(style_id)
    if not n: return {"error": f"no style '{style_id}'"}
    chain = [style_id] + _cascade(style_id)
    have = [c for c in chain if c in D["kits"]]
    resolved, source = {}, {}
    for cid in reversed(have):                      # furthest ancestor first, nearest wins
        for sid, rec in (D["kits"][cid].get("slots") or {}).items():
            if rec.get("status") in (None, "empty") and rec.get("binding", "open") == "open": continue
            if rec.get("binding") == "extends" and sid in resolved:
                base = json.loads(json.dumps(resolved[sid]))
                base.setdefault("parameters", {}).update(rec.get("parameters") or {})
                for v in rec.get("variants", []):
                    lst = base.setdefault("variants", [])
                    idx = next((k for k, x in enumerate(lst) if x.get("id") == v.get("id")), None)
                    op = v.get("op", "add")
                    if op == "remove" and idx is not None: lst.pop(idx)
                    elif idx is not None: lst[idx] = v
                    else: lst.append(v)
                if rec.get("rule_append"): base["rule"] = (base.get("rule", "").rstrip(". ") + ". " + rec["rule_append"])
                for k2 in ("code_conflict", "packs", "note", "judgment", "invented"):
                    if k2 in rec: base[k2] = rec[k2]
                resolved[sid] = base; source[sid] = f"{source.get(sid, '?')} + {cid} (extends)"
            else:
                resolved[sid] = rec; source[sid] = cid
    if slot: keys = [slot] if slot in resolved else []
    elif group: keys = [k for k in resolved if D["slots"].get(k, {}).get("group") == group]
    else: keys = list(resolved)
    rows = []
    for k in sorted(keys):
        r = resolved[k]
        if only_specified and r.get("binding") == "open": continue
        forb = [v["id"] for v in r.get("variants", []) if v.get("status") == "forbidden"]
        canon = [v["id"] for v in r.get("variants", []) if v.get("status") == "canonical"]
        rows.append({"slot": k, "group": D["slots"].get(k, {}).get("group"),
                     "binding": r.get("binding"), "source": source.get(k),
                     "rule": r.get("rule"), "canonical": canon, "forbidden": forb,
                     "parameters": r.get("parameters") if slot else ("%d parameters" % len(r.get("parameters") or {})),
                     "code_conflict": r.get("code_conflict") if slot else bool(r.get("code_conflict")),
                     "judgment": r.get("judgment", False), "invented": r.get("invented", False),
                     "packs": r.get("packs") if slot else None})
    prov = {}
    for k in keys: prov[source.get(k, "?")] = prov.get(source.get(k, "?"), 0) + 1
    return {"style": style_id, "kits_in_chain": have, "cascade": chain,
            # slots_total is the ONTOLOGY's own count, sent live. The workbench used to
            # render `${slots_returned} of 95 slots` against a literal, and the ontology has
            # been at 97 since 0.7.0 — so the surface printed "97 of 95 slots shown", a
            # sentence that contradicts itself on screen. A number the corpus knows should
            # never be retyped into a component.
            "slots_total": len(D["slots"]),
            "provenance": prov, "slots_returned": len(rows), "slots": rows,
            "hint": "pass slot='<id>' for the full record including parameters and pack bindings"}

# ----------------------------------------------------------------- proportion
def get_proportions(pack_id, column_diameter=None, module=None, ceiling_height=108.0,
                    opening_width=36.0, include_rules=True, assembly=None):
    D = _data(); pe = D["engine"]
    try: pk = pe.resolve(pack_id)
    except Exception:
        return {"error": f"no pack '{pack_id}'",
                "available": sorted(pe.PACKS.keys()),
                "hint": "order packs are <authority>-<order>, e.g. gibbs-ionic"}
    dpm = pe.diameters_per_module(pk)
    mod = module if module is not None else ((column_diameter * dpm) if column_diameter else None)
    d = pe.dimension(pk, mod, [assembly] if assembly else None)
    out = {"pack": pk["id"], "name": pk["name"], "authority": pk.get("authority", {}).get("source"),
           "resolved_from": pk.get("_resolved_from", [pk["id"]]),
           "module_in": d["module_in"], "parts": d["parts"], "part_in": round(d["part_in"], 4),
           "diameters_per_module": dpm, "totals": d["totals"],
           # PER-ASSEMBLY ATTRIBUTION, because `authority` above is the PACK's and an overlay
           # inherits what it does not state. `palladio-tuscan` states no entablature on purpose
           # -- that is OQ 7 -- so this tool served Vignola's cornice members under Palladio's
           # citation, on the assembly the open question exists for. `states_no_own` names the
           # pack that actually gives the figures, and is absent where the pack gives them
           # itself.
           "assemblies": [dict({"id": a["id"], "height_modules": a["height_modules"],
                                "height_in": a["height_in_stated"],
                                "members": a["members"] if assembly else len(a["members"])},
                               **({} if not pe.assembly_owner(pk["id"], a["id"])
                                     or pe.assembly_owner(pk["id"], a["id"]) == pk["id"]
                                  else {"inherited_from": pe.assembly_owner(pk["id"], a["id"]),
                                        "authority": pe.assembly_authority(pk["id"], a["id"])[0]}))
                          for a in d["assemblies"]],
           "invariants": pe.check_invariants(pk)}
    if include_rules:
        ev = pe.evaluate(pk, mod, {"ceiling_height": ceiling_height, "opening_width": opening_width})
        # `quantity` (OQ 48) names what the rule MEASURES, which is what makes (slot, dimension)
        # not the real address. Omitting it here left every MCP consumer seeing two rules that the
        # corpus deliberately distinguishes as if they were the same address. `calibrated_for`
        # carries a rule's own statement that it is out of band. Both were dropped by a fixed key
        # list -- the same bug as proportion_engine's, found in the same audit, 25 Aug 2026.
        # A FIXED KEY LIST DROPS WHATEVER IT DOES NOT NAME, silently. `error` was outside
        # it, so a rule proportion_engine.evaluate() could not evaluate reached the workbench
        # with its refusal removed and Proportions.jsx drew "null in" -- a refusal rendered as
        # a measurement. Adding `error` fixed one instance and left two: `authority_note`,
        # which 730 of the corpus's 900 derived rules carry and which says WHICH authority the
        # figure comes from, and `diagnostic`. Both are in schema/proportion-pack.schema.json's
        # own rule object and both were being dropped from every tdl_get_proportions call.
        # tests/test_score.py::test_rule_keys_publishes_every_key_the_pack_schema_defines
        # keeps the list from drifting again -- the drift, not any one key, is the bug.
        # `scope` and the two states the engine derives from it join the list at OQ 88. A
        # consumer that reads a value must be able to see that the value is not about its
        # building -- publishing the figure and withholding "this rule is stated for a frame
        # wall" would be the same silent delivery this field was added to end.
        # `out_of_calibration` ADDED 28 AUG 2026 BY THE AUDIT. It is the engine's stated
        # reason for leaving a rule with a band unjudged, and dropping it delivered
        # `in_range: null` beside a stated range with nothing saying why -- the band cell for
        # an unjudged rule byte-identical to the band cell for a passing one, on every
        # `tdl_get_proportions` caller and on the Proportions plate. Same shape as the
        # `error` key beside it, whose omission `Proportions.jsx` records as "a refusal
        # rendered as a measurement".
        RULE_KEYS = ("target_slot", "dimension", "quantity", "expression", "value", "units",
                     "judgment", "range", "in_range", "note", "calibrated_for",
                     "out_of_calibration",
                     "authority_note", "diagnostic", "error",
                     "scope", "out_of_scope", "scope_unjudged")
        out["derived_rules"] = [{k: r.get(k) for k in RULE_KEYS} for r in ev["rules"]]
        out["judgment_rules"] = [r["target_slot"] for r in ev["rules"] if r.get("judgment")]
    out["conflicts"] = pk.get("conflicts", [])
    if not assembly: out["hint"] = "pass assembly='cornice' (or capital, base, entablature, pedestal) for member-by-member dimensions"
    return out

def compare_authorities(order, column_diameter=12.0):
    D = _data(); pe = D["engine"]
    rows = []
    for auth in ["vignola","palladio","gibbs","chambers","benjamin"]:
        pid = f"{auth}-{order}"
        if pid not in pe.PACKS: continue
        pk = pe.resolve(pid); d = pe.dimension(pk, column_diameter * pe.diameters_per_module(pk))
        # THE ENTABLATURE COLUMN OF THIS TABLE WAS NOT ALWAYS THIS AUTHORITY'S. `palladio-tuscan`
        # and `chambers-tuscan` state no entablature of their own, so both rows reported
        # VIGNOLA's 21.0 in and 0.25 ratio as theirs -- while the note below the table said
        # Palladio makes it a fifth. The table contradicted its own note, and the contradiction
        # was the tool inventing an attribution. An inherited figure is reported with the pack
        # it came from and is NOT presented as the authority's own.
        ent_owner = pe.assembly_owner(pid, "entablature") or pe.assembly_owner(pid, "cornice")
        inherited = bool(ent_owner and ent_owner != pid)
        rows.append({"authority": auth, "pack": pid, "year": pk.get("authority", {}).get("year"),
                     "column_diameters": d["totals"].get("column_height_diameters"),
                     "column_in": d["totals"].get("column_height_in"),
                     "entablature_in": d["totals"].get("entablature_height_in"),
                     "entablature_over_column": round(d["totals"]["entablature_height_in"] / d["totals"]["column_height_in"], 4)
                        if d["totals"].get("entablature_height_in") and d["totals"].get("column_height_in") else None,
                     "entablature_is_this_authoritys": not inherited,
                     "entablature_inherited_from": ent_owner if inherited else None,
                     "confidence": pk.get("confidence")})
    if not rows: return {"error": f"no packs for order '{order}'", "orders": ["tuscan","doric","ionic","corinthian","composite"]}
    borrowed = [r["authority"] for r in rows if not r["entablature_is_this_authoritys"]]
    return {"order": order, "at_common_column_diameter_in": column_diameter, "authorities": rows,
            "entablature_caveat": (
                None if not borrowed else
                "%s state no entablature of their own for this order; the figure shown is "
                "inherited through the overlay and is NOT that authority's. Read "
                "`entablature_inherited_from` before comparing." % ", ".join(borrowed)),
            "note": ("Compared at a common column DIAMETER, never a common module — Vignola and Chambers "
                     "measure in the semidiameter and Palladio in the whole diameter. Vignola and Chambers "
                     "make the entablature a quarter of the column; Gibbs and Palladio a fifth; Benjamin "
                     "adds a whole diameter to the column instead, because he is designing for wood at "
                     "small scale and says so in his preface.")}

# ----------------------------------------------------------------- faults
SEV = ("fatal", "serious", "minor")

def _fault_card(f, style_id=None):
    sev = f["severity"]
    why = None
    for s in f.get("severity_by_style", []):
        if s["style"] == style_id: sev, why = s["severity"], s.get("why"); break
    return {"id": f["id"], "name": f["name"], "slots": f["slots"], "severity": sev,
            "severity_note": why, "frequency": f.get("frequency"), "category": f.get("category"),
            "driver": f["cause"]["driver"], "cost_negative": f["cause"].get("cost_negative", False),
            "symptom": f["symptom"],
            "test": f.get("test", {}).get("expression"),
            "measurable_from": f.get("test", {}).get("measurable_from")}

def _style_chain(style_id, D):
    """A style and everything it inherits from, as a set. Extracted from _applies so a TEST can
    be scoped to a style the same way a FAULT is (OQ 63)."""
    chain = set([style_id] + _cascade(style_id))
    cur = D["styles"].get(style_id)
    for _ in range(6):
        if not cur: break
        chain.add(cur["id"]); cur = D["styles"].get(cur.get("member_of") or "")
    return chain


def _test_applies(t, style_id, D):
    """Whether one TEST of a fault is written for this style (OQ 63).

    `applies_to_styles` absent means every style the fault applies to, which is the behaviour
    before the field existed. Present, it is matched against the style AND its inheritance
    chain, so a test scoped to a parent still applies to its descendants.

    This exists because `check_measurements` reports a fault present when ANY of its tests
    fails, and a secondary test written for one style was therefore failing houses of every
    other. `faults/chimney-omitted.json` carries a Tudor Revival chimney-breadth ratio and a
    Prairie visual-mass test whose own notes say so, and both fired on a Cape Cod colonial --
    which is why a parti named `cape-central-chimney` was reported as having no chimney."""
    want = t.get("applies_to_styles")
    if not want: return True
    if not style_id: return False
    return bool(_style_chain(style_id, D) & set(want))


# ---------------------------------------------------------------------------
# AN EXCEPTION IS A LICENCE, AND UNTIL WP-8.4 NOBODY READ ITS PRECONDITION.
#
# `exceptions[].granted_when` (schema/fault.schema.json; called `applies_when`
# until 28 Aug 2026, which is why nothing here read it -- the schema carried two
# fields of that name meaning different things) says what has to be true of the
# WALL, the ROOF or the SITE before the licence is earned. 331 of the corpus's
# 846 exceptions carry one and all three selection sites below matched on
# `e["style"] == style` and nothing else, so `architrave-that-is-not-there`'s
# Pueblo Revival licence -- written for `construction: [adobe, rammed-earth]` --
# was excusing a house whose style resolves canonically to stucco-over-wood-frame.
#
# THREE VERDICTS, AND THE THIRD IS THE POINT. `granted` applies the licence,
# `refused` withholds it and lets the general rule stand, and `unjudged` says the
# question cannot be decided from a style id. Unjudged is NOT a quiet grant and
# NOT a quiet refusal: where the exception carries a `bounds_test` -- which
# REPLACES the fault's primary test -- an unjudged precondition means nobody can
# say which of two tests governs the house, so the fault is reported
# could-not-evaluate rather than being judged by whichever branch we happened to
# take. That is the same rule `openings.py` follows when it marks an opening
# `unplaced` instead of inventing a position.
#
# WHAT IS EVALUATED, AND WHAT IS COUNTED INSTEAD OF EVALUATED.
#   * `construction` -- evaluated, always, against the style's RESOLVED kit
#     through build/construction_vocabulary.py's closed table.
#   * `date_range`   -- evaluated only where the caller supplies a date in
#     `context`. Measured over the corpus: of 102 date preconditions, 23 contain
#     their style's whole floruit and 79 overlap it, and NOT ONE is disjoint from
#     it -- so a date test against a style's floruit can never refuse a licence
#     and would convert 79 decidable questions into unjudged ones on the strength
#     of our own missing input rather than anything about the house.
#   * `regions`      -- not evaluated, and the reason is measured rather than
#     assumed: 78 of the 79 region preconditions name a region that CONTAINS the
#     style's own regions or its hearth ("New England" over a style whose regions
#     are Massachusetts, Connecticut, Rhode Island; "british-isles" over England,
#     Scotland, Ireland), so the key restates the style match at a coarser grain.
#     The one that does not is `lever-on-a-period-door` on `french-eclectic`,
#     whose regions are France and Continental Europe against a style whose own
#     region is the United States, and it is named here rather than left to be
#     found again. Closing this properly needs a gazetteer with containment, not
#     a mapping table; the 45 tokens in use are free text under two spelling
#     conventions and the style corpus's 219 region names are free text too.
#   * `slots`        -- a scope on WHICH slot the licence covers, not a condition
#     on the house. check_faults.py validates it; it is not a precondition.
# The unevaluated keys are DISCLOSED on every verdict and counted by
# `exception_precondition_census()`, never folded into a pass.
#
# AN UNEVALUATED KEY DOES NOT BLOCK A GRANT, and that is a deliberate choice
# stated rather than slipped in. Before this package every one of these
# preconditions was ignored; reading the ones we can read and refusing where they
# refuse is a strict improvement, where treating the ones we cannot read as
# blockers would turn a licence into an unjudged fault on the strength of a
# missing evaluator rather than a fact about the building.
_EXC_EVALUATED_KEYS = ("construction",)
# `slots` IS COUNTED, NOT IGNORED, AND THE DIFFERENCE IS 68 RECORDS. It is a scope on WHICH
# slot the licence covers rather than a condition on the house, so it must not gate the grant
# -- but leaving it out of both lists made `grant_exception` return
# `{"verdict": "granted", "why": "no precondition", "unevaluated": []}` for an exception that
# plainly carries one, which is a false statement about the record. 104 exceptions carry
# `slots`; on 67 it is the SOLE precondition, and 54 of those carry a `bounds_test` that
# REPLACES the fault's primary test on a grant -- so a fault was being judged by the
# exception's looser rule on the strength of a precondition nobody read, which is the exact
# defect this package was built to remove, one key over. The census lost them too: they
# counted in `with_granted_when` and in no verdict bucket. Found by the WP-8.4 adversarial
# audit. Disclosed and counted here; whether a slot scope should ever gate a grant is a
# question for whoever rules on `check_faults.py`'s validation of it.
_EXC_COUNTED_KEYS = ("regions", "date_range", "slots")


@functools.lru_cache(maxsize=1)
def _kit_graph():
    rk = _mod("resolve_kit", os.path.join(ROOT, "build", "resolve_kit.py"))
    return rk, rk.load_graph()


@functools.lru_cache(maxsize=256)
def _resolved_kit(style_id):
    """The style's kit AFTER the lineage cascade, or None if it is not a node.

    The cascade, never `load_kit`. Reading a node's own file instead of what it
    resolves to has already cost this corpus two published wrong numbers
    (build/check_inheritance.py's own comment), and here it would be worse than
    wrong: most styles do not bind `construction_type` at all and inherit it."""
    rk, g = _kit_graph()
    if style_id not in g["nodes"]:
        return None
    return rk.resolve_slots(g, rk.chain_for(g, style_id), rk.scope_for(g, style_id))[0]


def grant_exception(exc, style, context=None):
    """Decide whether an exception's licence is earned. -> dict, never a bool.

    `context` is what the caller knows about THIS house rather than about its
    style -- `{"declared": {slot: variant_id}, "date": 1820}`. A plan record's
    own `declared` block is exactly the right thing to pass, and it turns most
    `unjudged` verdicts into real answers.
    """
    out = {"verdict": "granted", "why": "no precondition", "unevaluated": [], "detail": []}
    if not exc:
        return out
    gw = exc.get("granted_when") or {}
    if not gw:
        return out
    context = context or {}
    declared = context.get("declared") or {}
    out["unevaluated"] = [k for k in _EXC_COUNTED_KEYS if gw.get(k)]
    if out["unevaluated"] and not gw.get("construction"):
        # NOT "no precondition". The record carries one and nothing reads it; saying so is the
        # whole of the four-state discipline applied to this field.
        out["why"] = ("granted with %s unevaluated -- this licence states a precondition "
                      "nothing here reads" % ", ".join(out["unevaluated"]))

    tokens = gw.get("construction") or []
    if tokens:
        cv = _mod("construction_vocabulary",
                  os.path.join(ROOT, "build", "construction_vocabulary.py"))
        kit = _resolved_kit(style)
        if kit is None:
            # `style` here is one of the eight `construction:`/`region:` pseudo-ids
            # check_faults.py permits in exceptions[].style. No caller passes one as
            # a style, so the exception is unreachable and its precondition cannot be
            # resolved against anything. Say so rather than granting it.
            out.update(verdict="unjudged",
                       why="%r is not a style node, so there is no kit to read" % style)
            return out
        verdicts = [(t,) + cv.resolve(t, kit, declared) for t in tokens]
        out["detail"] = ["%s: %s (%s)" % (t, v, w) for t, v, w in verdicts]
        kinds = {v for _, v, _ in verdicts}
        # A construction list is a disjunction: the licence is written for a house
        # built in ANY of the ways named.
        if "holds" in kinds:
            out["why"] = "construction " + "; ".join(
                "%s %s" % (t, v) for t, v, _ in verdicts if v == "holds")
        elif kinds <= {"fails"}:
            out.update(verdict="refused",
                       why="the style is built in none of %s" % ", ".join(tokens))
            return out
        elif kinds <= {"fails", "unmappable"}:
            out.update(verdict="unjudged",
                       why="every construction this licence names is either refused by the "
                           "style or absent from the vocabulary")
            return out
        else:
            # A LIST IS A DISJUNCTION AND MUST BE RESOLVED AS ONE. Reducing each token to a
            # verdict and then combining is right at the ends and wrong in the middle: a
            # licence naming `[solid-masonry-two-wythe, adobe, rammed-earth]` on a style that
            # is canonically cob AND clay-lump has each token saying "both ways, cannot
            # decide" while the wall is CERTAINLY one of the three. Consulted only here, so it
            # can turn an unjudged into a grant and can never change a grant or a refusal.
            union = cv.resolve_any(tokens, kit, declared)
            if union:
                out["why"] = union[1]
                return out
            out.update(verdict="unjudged",
                       why="the style permits %s and other constructions too, and nothing "
                           "in front of us says which one this house is"
                           % ", ".join(t for t, v, _ in verdicts if v == "undecidable"))
            return out

    dr = gw.get("date_range")
    if dr and context.get("date") is not None:
        out["unevaluated"] = [k for k in out["unevaluated"] if k != "date_range"]
        lo, hi = dr[0], dr[1]
        if not (lo <= context["date"] <= hi):
            out.update(verdict="refused",
                       why="the house is dated %s, outside this licence's %s-%s"
                           % (context["date"], lo, hi))
            return out
        out["why"] = (out["why"] + "; " if out["why"] != "no precondition" else "") + \
                     "the house is dated %s, within %s-%s" % (context["date"], lo, hi)
    return out


def exception_precondition_census():
    """How many exception preconditions this corpus can and cannot resolve.

    Ratcheted by tests/test_construction_scope.py::TestTheExceptionPreconditionIsRead. The unevaluable figures
    are the ones that matter: they are the honest size of what `granted_when`
    still promises and nothing reads."""
    D = _data()
    out = Counter = {"exceptions": 0, "with_granted_when": 0, "construction": 0,
                     "granted": 0, "refused": 0, "unjudged": 0,
                     "unevaluated_regions": 0, "unevaluated_date_range": 0,
                     # `slots` WAS IN NO BUCKET AT ALL. It counted in `with_granted_when` and
                     # nowhere else, so 68 of the 331 vanished from a census whose own
                     # docstring calls its unevaluable figures the honest size of what this
                     # field promises. `slots_only` is the sharp half: those licences carry a
                     # precondition and NOTHING about them is read, and 54 of them substitute
                     # a `bounds_test` for the fault's primary test on the strength of it.
                     "unevaluated_slots": 0, "slots_only": 0,
                     "substituting_bounds_test": 0, "bounds_test_unjudged": 0}
    for f in D["faults"].values():
        for exc in (f.get("exceptions") or []):
            out["exceptions"] += 1
            gw = exc.get("granted_when") or {}
            if not gw:
                continue
            out["with_granted_when"] += 1
            if gw.get("regions"):
                out["unevaluated_regions"] += 1
            if gw.get("date_range"):
                out["unevaluated_date_range"] += 1
            if gw.get("slots"):
                out["unevaluated_slots"] += 1
            if not gw.get("construction"):
                if set(gw) <= {"slots", "note"} and gw.get("slots"):
                    out["slots_only"] += 1
                continue
            out["construction"] += 1
            g = grant_exception(exc, exc.get("style"))
            out[g["verdict"]] += 1
            if exc.get("bounds_test"):
                out["substituting_bounds_test"] += 1
                if g["verdict"] == "unjudged":
                    out["bounds_test_unjudged"] += 1
    return out


def _applies(f, style_id, D):
    if "universal" in f["applies_to"]: return True
    if style_id in f["applies_to"]: return True
    return bool(_style_chain(style_id, D) & set(f["applies_to"]))

def find_faults(style=None, slot=None, group=None, severity=None, frequency=None,
                measurable_from=None, query=None, limit=25):
    D = _data(); out = []
    for f in D["faults"].values():
        if slot and slot not in f["slots"]: continue
        if group and not any(D["slots"].get(s, {}).get("group") == group for s in f["slots"]): continue
        if severity and f["severity"] != severity: continue
        if frequency and f.get("frequency") != frequency: continue
        if measurable_from and f.get("test", {}).get("measurable_from") != measurable_from: continue
        if query and query.lower() not in json.dumps(f).lower(): continue
        excepted = None
        if style:
            if not _applies(f, style, D): continue
            for e in f.get("exceptions", []):
                if e["style"] == style: excepted = e; break
        card = _fault_card(f, style)
        if excepted:
            # WP-8.4: the licence's own precondition is read before it is published.
            # A card that prints EXCEPTION_FOR_THIS_STYLE is telling an agent it may
            # stop applying the general rule, so a licence whose condition is refused
            # or cannot be decided must not be presented as one that holds.
            g = grant_exception(excepted, style)
            key = {"granted": "EXCEPTION_FOR_THIS_STYLE",
                   "refused": "EXCEPTION_NOT_EARNED_BY_THIS_STYLE",
                   "unjudged": "EXCEPTION_WHOSE_CONDITION_COULD_NOT_BE_JUDGED"}[g["verdict"]]
            card[key] = {"why": excepted["why"], "bounds": excepted.get("bounds"),
                         "bounds_test": excepted.get("bounds_test"),
                         "condition": excepted.get("granted_when"),
                         "verdict": g["verdict"], "because": g["why"],
                         "not_evaluated": g["unevaluated"]}
        for inv in f.get("inverted_by", []):
            if style and inv["style"] == style: card["INVERTED_FOR_THIS_STYLE"] = inv["statement"]
        out.append(card)
    out.sort(key=lambda c: (SEV.index(c["severity"]) if c["severity"] in SEV else 3,
                            ["endemic","common","occasional","rare"].index(c["frequency"]) if c.get("frequency") else 4))
    return {"matches": len(out), "returned": min(limit, len(out)), "faults": out[:limit],
            "note": ("Faults are element-first: most are universal, and style is a facet. Check "
                     "EXCEPTION_FOR_THIS_STYLE (the licence is EARNED), "
                     "EXCEPTION_NOT_EARNED_BY_THIS_STYLE (its condition is refused -- the "
                     "general rule stands) or EXCEPTION_WHOSE_CONDITION_COULD_NOT_BE_JUDGED "
                     "(say so rather than choosing), and INVERTED_FOR_THIS_STYLE, before repeating a rule at "
                     "a client — a five-foot Georgian portico is a fault by Craftsman standards and correct by its own."),
            "next": "tdl_get_fault for the full record with fixes, or tdl_check_measurements if you have numbers"}

def _exception_card(f, style):
    """The exception for this style WITH its precondition read (WP-8.4).

    Returned as a copy carrying `granted`, so a caller reading THIS field cannot take
    the record's `why` for a licence the house has earned.

    IT DOES NOT SANITISE `out["exceptions"]`. `get_fault` returns the whole fault record,
    raw exceptions array included, and a client that reads `f["exceptions"]` directly --
    the workbench Fault Corpus does -- still sees every licence unconditionally. That is
    deliberate: the array is the CORPUS, and a tool that silently hid records would be
    lying about what the corpus contains. What a per-style reader wants is this field, and
    `for_this_style.granted` is where the verdict lives. Found by the WP-8.4 adversarial
    audit, which correctly flagged the earlier wording as claiming more than it did."""
    exc = next((e for e in f.get("exceptions", []) if e["style"] == style), None)
    if not exc:
        return None
    g = grant_exception(exc, style)
    return {**exc, "granted": g["verdict"], "granted_because": g["why"],
            "precondition_not_evaluated": g["unevaluated"]}


def get_fault(fault_id, style=None):
    D = _data(); f = D["faults"].get(fault_id)
    if not f:
        return {"error": f"no fault '{fault_id}'", "did_you_mean": [k for k in D["faults"] if fault_id.lower() in k][:8]}
    out = json.loads(json.dumps(f))
    if style:
        out["for_this_style"] = {
            "applies": _applies(f, style, D),
            "severity": next((s["severity"] for s in f.get("severity_by_style", []) if s["style"] == style), f["severity"]),
            "exception": _exception_card(f, style),
            "inverted": next((i for i in f.get("inverted_by", []) if i["style"] == style), None)}
    return out

def _eval_test(t, measurements):
    if not t or not t.get("expression"): return None
    # A TEST MAY BE PRECONDITIONED ON A MEASUREMENT, not only on a style (`applies_to_styles`,
    # OQ 63). Some rules presuppose the thing they measure exists: `dormer-off-the-bay`'s parity
    # secondary is `dormer_count % 2 == 1`, which fires on a house STATED to carry no dormers and
    # reports "Dormers Off the Rhythm: 0 against equals 1" -- the OQ 52 flagship failure walking
    # back in through the front door the moment a record could finally say "none". Zero dormers is
    # not an even number of dormers; it is no dormers, and the parity rule has nothing to say.
    #
    # A precondition that FAILS means the test is NOT RUN -- the same shape `_test_applies` uses,
    # and for the same reason: a rule that is not about this house says nothing about this house.
    # A precondition whose OWN measurements are missing means we cannot tell whether it applies,
    # which is could-not-evaluate and is reported as such rather than quietly skipped.
    when = t.get("applies_when")
    if when:
        # A MALFORMED GUARD IS AN ERROR, NOT A SILENT ANYTHING. `schema/fault.schema.json` now
        # requires expression/direction/threshold, but the schema is only checked when jsonschema
        # is installed and `_eval_test` is the shared evaluator every surface calls -- so the two
        # failure modes the WP-5.14 audit found are refused here too. Omitting `expression` made
        # the precondition vanish and the test run unguarded; omitting `direction` made `passes`
        # None, which read as "declined" and switched the test off permanently. Both were
        # schema-valid, both were silent, and the second is indistinguishable from a design
        # decision now that not-applicable is a normal state.
        if not when.get("expression") or not when.get("direction"):
            return {"status": "error",
                    "detail": "applies_when needs both an expression and a direction; "
                              f"got {sorted(when)}"}
        w = _eval_test({k: v for k, v in when.items() if k != "applies_when"}, measurements)
        if w and w["status"] != "evaluated": return w
        if w and w["passes"] is not True:
            return {"status": "not_applicable", "because": when.get("expression"),
                    "required": f"{when.get('direction')} {when.get('threshold')}",
                    "value": w["value"]}
    expr = t["expression"]
    names = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", expr))
    # A key present with a null value is MISSING, not supplied (OQ 52). `null` is the natural
    # JSON encoding of "I could not judge this", and it is what a generator that models a thing
    # but could not measure it on this house will send. Reading it by key presence alone let it
    # through to eval, where it became a TypeError and then a `status: error` -- a real state,
    # but the wrong one: an error says the corpus asked something incoherent, where this says
    # nobody took the measurement. build/elevation.py already drops its own Nones on the way
    # out; this is for every other caller, the workbench and the MCP tools among them.
    missing = sorted(n for n in names
                     if n not in ("min", "max", "abs", "round")
                     and measurements.get(n) is None)
    if missing: return {"status": "need_measurements", "missing": missing}
    try:
        val = eval(expr, {"__builtins__": {}}, dict(measurements) | {"min": min, "max": max, "abs": abs, "round": round})
    except Exception as e:
        return {"status": "error", "detail": str(e)}
    d, th, up = t.get("direction"), t.get("threshold"), t.get("upper")
    # The comparison below used to sit outside any guard: a test expression returning a
    # value that will not compare against the threshold raised straight out of
    # check_measurements, through check_plan, and became a 500 from /api/plan/evaluate.
    # An uncomparable result is something this evaluator COULD NOT judge, which is a
    # state the corpus already has a word for.
    # 'one-of' exists only on the constraint schema (schema/constraint.schema.json), not the
    # fault schema -- a fault test always fails this lookup harmlessly, since no fault ever
    # sets direction: one-of. Kept in the same shared evaluator rather than forked so faults
    # and style constraints (build/plan_check.py) share one safety-checked eval path.
    try:
        ok = {"at-least": lambda: val >= th, "at-most": lambda: val <= th,
              "equals": lambda: abs(val - th) < 1e-6,
              "between": lambda: th <= val <= (up if up is not None else th),
              "one-of": lambda: str(val) in (t.get("set") or [])}.get(d, lambda: None)()
    except Exception as e:
        return {"status": "error", "detail": f"{val!r} does not compare: {e}"}
    required = f"one-of {t.get('set')}" if d == "one-of" else (
        f"{d} {th}" + (f" and {up}" if d == "between" and up is not None else ""))
    # `expression` rides on the row (WP-9.1): a consumer reading a failing row could see the
    # value and the requirement and not WHICH quantity had failed, so build/plan_check.py's
    # fault finding could not say what to move, and build/critique.py could not tell a
    # measurement the house declared from one the elevation generator derived.
    return {"status": "evaluated", "value": round(val, 4) if isinstance(val, float) else val,
            "required": required, "passes": ok, "units": t.get("units"),
            "expression": t.get("expression")}

def _load_constraint_vocab():
    return _mod("constraint_vocabulary", os.path.join(ROOT, "build", "constraint_vocabulary.py"))

def check_style_constraints(style, measurements):
    """Evaluate a style's own constraint tests (schema/constraint.schema.json, WP-1.1) against a
    dict of measurements -- the same present/clear/unjudged shape check_measurements already
    returns for faults, so a caller can ask 'does this style's roof-pitch rule pass at 9:12'
    without building a whole plan record for tdl_check_plan.

    365 of the corpus's 660 live constraints carry a test; 170 more are hard with none and come
    back under `judgment_only`. **THE REMAINING 125 -- 98 `soft` and 27 `advisory` -- USED TO
    VANISH, AND THIS DOCSTRING SAID THEY DID NOT.** It read "the rest ... come back under
    judgment_only rather than silently ignored", which was false for every one of them: the loop
    below appended a testless constraint only when its severity was `hard`, so a soft or advisory
    one landed in no list, in no summary count, and in nothing a caller could see. Measured on
    `garrison-revival`: 5 live constraints, 3 accounted for, 2 gone.

    That is the same narrowing WP-11.9 removed from `plan_check.py`'s grouping loop one layer up
    (`elif hard` there, `if severity == "hard"` here) -- a rule nobody executes and nobody is told
    about reads exactly like a rule that passed. Found by an adversarial audit of that fix, which
    swept for second occurrences of the pattern; the number was re-derived here before it was
    believed.

    They come back under `not_migrated` now -- a FIFTH list rather than a widened
    `judgment_only`, because that key is documented as hard-with-no-test and quietly changing what
    it contains would move the meaning of a field callers already read."""
    D = _data()
    n = D["styles"].get(style)
    if not n:
        near = [s for s in D["styles"] if style.lower() in s][:6]
        return {"error": f"unknown style '{style}'", "did_you_mean": near}
    present, clear, needed, judgment_only, not_migrated = [], [], [], [], []
    for c in n.get("constraints", []):
        if c.get("deprecated_in_favour_of"):
            continue
        test = c.get("test")
        if not test:
            row = {"id": c.get("id"), "kind": c["kind"], "statement": c["statement"],
                   "severity": c.get("severity")}
            # `if/else`, never `if hard: ... continue`. See the docstring: the narrowed form
            # dropped 125 of 660 constraints and the docstring asserted it did not.
            if c.get("severity") == "hard":
                judgment_only.append(row)
            else:
                not_migrated.append(row)
            continue
        row = {"id": c["id"], "kind": c["kind"], "severity": c.get("severity"), "statement": c["statement"]}
        r = _eval_test(test, measurements)
        if not r or r["status"] != "evaluated":
            row["missing"] = r.get("missing") if r else None
            needed.append(row)
            continue
        row.update(value=r["value"], required=r["required"], units=r.get("units"))
        if r["passes"]:
            clear.append(row)
        else:
            row["note"] = test.get("note")
            present.append(row)
    return {"style": style, "measurements_given": sorted(measurements),
            "constraints_present": present, "constraints_clear": clear,
            "could_not_judge": needed, "judgment_only": judgment_only,
            "not_migrated": not_migrated,
            "summary": {"present": len(present), "clear": len(clear), "unjudged": len(needed),
                        "judgment_only": len(judgment_only),
                        "not_migrated": len(not_migrated)},
            "note": ("A constraint only counts as present (violated) when a test actually failed. "
                     "could_not_judge is unknown, not passed. judgment_only lists HARD constraints "
                     "with no test at all -- scope: judgment, or simply not yet migrated. "
                     "not_migrated lists the soft and advisory ones with no test, which this "
                     "function used to drop entirely while claiming it did not: every live "
                     "constraint on the style now appears in exactly one of the five lists, and "
                     "the summary counts all five.")}

def check_measurements(measurements, style=None, slot=None, include_needed=True, limit=40,
                       context=None):
    """Evaluate every applicable fault test against a dict of measurements.

    This is the corpus made executable: give it what you can measure from a photograph or a
    drawing and it tells you which faults are present, which are clear, which it could not judge
    because a number is missing, and which are NOT APPLICABLE -- every test preconditioned on a
    measurement this house does not meet, so none ran. Four states, not three; the docstring said
    three for a day after the fourth shipped."""
    D = _data()
    present, clear, needed, not_applicable = [], [], [], []

    def _judge(f, tests):
        """Evaluate one test list and say which of the four states it lands in.

        Factored out of the loop by WP-8.4 so a fault whose exception precondition
        cannot be resolved can be judged BOTH WAYS and the two answers compared.
        Returns (state, row)."""
        # OQ 63: a test scoped to another style is not run at all. Not run is not the same as
        # passed -- a test that is not for this house says nothing about this house, and the
        # fault's judgement rests on the tests that ARE for it.
        tests = [t for t in tests if t and _test_applies(t, style, D)]
        results = [r for r in (_eval_test(t, measurements) for t in tests) if r]
        ev = [r for r in results if r["status"] == "evaluated"]
        if not ev:
            miss = sorted({m for r in results if r["status"] == "need_measurements"
                           for m in r["missing"]})
            errs = sorted({r["detail"] for r in results if r["status"] == "error"})
            # THE FOURTH STATE, and it exists for the same reason as the `errs` branch below it.
            # A test may now decline on a MEASUREMENT (`applies_when`), not only on a style: zero
            # dormers means the whole of `dormer-off-the-bay` has nothing to say. With every test
            # declined there is no `ev`, no `miss` and no `errs`, so the fault was appended to
            # nothing -- not present, not clear, not unjudged, absent from the counts, and
            # indistinguishable to a caller from clear. Not applicable is a real answer and gets
            # its own list; it is not a pass, and it is not an unjudged either.
            declined = [r for r in results if r["status"] == "not_applicable"]
            if declined and not miss and not errs:
                return "not_applicable", {
                    "fault": f["id"], "name": f["name"],
                    "because": sorted({r["because"] for r in declined}),
                    "required": sorted({r["required"] for r in declined}),
                    "note": "Every test of this fault is preconditioned on a measurement this "
                            "house does not meet, so none was run. Not a pass -- the question "
                            "does not arise."}
            # `errs` is why this branch exists in this shape. A fault whose every test
            # ERRORED produced no `ev` and no `miss`, so it was appended to nothing: not
            # present, not clear, not unjudged, and absent from the summary counts -- a
            # fault that silently vanished, which reads to a caller exactly like clear.
            # That is the one collapse this corpus forbids above all others.
            if miss or errs:
                row = {"fault": f["id"], "name": f["name"], "needs": miss,
                       "measurable_from": f.get("test", {}).get("measurable_from")}
                if errs:
                    row["errors"] = errs
                return "needed", row
            return "silent", None
        failing = [r for r in ev if r["passes"] is False]
        if not failing:
            return "clear", {"fault": f["id"], "name": f["name"], "results": ev}
        # The tests that actually failed, kept apart from the ones that merely ran. A fault
        # with secondary tests can have its PRIMARY pass and a secondary fail -- which is
        # the fault being present -- and a caller reporting results[0] then quotes the
        # passing number as the evidence. build/plan_check.py did exactly that: a Cape with
        # two chimneys was reported as "The House With No Fire: 2 against at-least 1", a
        # sentence in which every number is right and the claim is nonsense.
        return "present", {
            "fault": f["id"], "name": f["name"],
            "severity": next((s["severity"] for s in f.get("severity_by_style", [])
                              if s["style"] == style), f["severity"]),
            "slots": f["slots"], "results": ev, "failing": failing,
            "symptom": f["symptom"],
            "fix_cheap": (f.get("fixes") or {}).get("cheap"),
            "fix_right": (f.get("fixes") or {}).get("right")}

    for f in D["faults"].values():
        if slot and slot not in f["slots"]: continue
        if style and not _applies(f, style, D): continue
        tests = [f.get("test")] + list(f.get("secondary_tests") or [])
        exc = next((e for e in f.get("exceptions", []) if style and e["style"] == style), None)
        # WP-8.4. A `bounds_test` REPLACES the fault's primary test, so the licence's
        # own precondition decides which of two rules judges this house. Three
        # outcomes:
        #   granted  -> substitute, as before.
        #   refused  -> the general rule stands. This is where a licence stops
        #               excusing a house that never earned it.
        #   unjudged -> nobody can say which of the two rules governs. JUDGE BOTH
        #               WAYS AND COMPARE. Where the two agree the unresolved
        #               precondition changes nothing and the fault is answered --
        #               reporting could-not-evaluate there would be a fake unjudged,
        #               which is as dishonest in its own direction as a fake pass.
        #               Where they disagree the answer really does turn on the
        #               question we cannot resolve, and THAT is could-not-evaluate.
        grant = grant_exception(exc, style, context) if exc else None
        immaterial = None
        if exc and exc.get("bounds_test") and grant["verdict"] != "refused":
            under_exc = [exc["bounds_test"]] + tests[1:]
            if grant["verdict"] == "granted":
                tests = under_exc
            else:
                sa, ra = _judge(f, under_exc)
                sb, rb = _judge(f, tests)
                if sa != sb:
                    if include_needed:
                        needed.append({
                            "fault": f["id"], "name": f["name"], "needs": [],
                            "measurable_from": f.get("test", {}).get("measurable_from"),
                            "exception_unjudged": {
                                "style": exc["style"], "because": grant["why"],
                                "condition": exc.get("granted_when"),
                                "not_evaluated": grant["unevaluated"],
                                "under_the_exception": sa, "under_the_general_rule": sb,
                                "note": "This style carries an exception whose own bounds_test "
                                        "REPLACES the fault's primary test, and whose "
                                        "precondition could not be resolved from the style "
                                        "alone. The two rules disagree about this house, so "
                                        "which one governs decides the verdict and nobody can "
                                        "say which one governs. Supply the house's own "
                                        "construction to settle it."}})
                    continue
                immaterial = {"style": exc["style"], "verdict": grant["verdict"],
                              "because": grant["why"],
                              "note": "The exception's precondition could not be resolved, but "
                                      "its bounds_test and the general rule reach the same "
                                      "verdict on this house, so it does not matter which "
                                      "governs."}

        state, row = _judge(f, tests)
        if state == "present":
            # Only a licence actually EARNED is reported as applied. Until WP-8.4 this
            # printed the exception's `why` beside every failing finding on the style,
            # telling a reader the fault was excused when nothing had checked whether
            # its condition held.
            if exc and grant["verdict"] == "granted":
                row["exception_applied"] = exc["why"]
            elif exc:
                row["exception_not_applied"] = {"why": exc["why"], "verdict": grant["verdict"],
                                                "because": grant["why"]}
            if immaterial:
                row["exception_unjudged_but_immaterial"] = immaterial
            present.append(row)
        elif state == "clear":
            if immaterial:
                row["exception_unjudged_but_immaterial"] = immaterial
            clear.append(row)
        elif state == "not_applicable":
            not_applicable.append(row)
        elif state == "needed" and include_needed:
            needed.append(row)
    present.sort(key=lambda r: SEV.index(r["severity"]) if r["severity"] in SEV else 3)
    return {"style": style, "measurements_given": sorted(measurements),
            "faults_present": present, "faults_clear": clear[:limit],
            "faults_clear_truncated": max(0, len(clear) - limit),
            # NOT truncated. "unjudged is not passed" degrades into "the first forty
            # unjudged are not passed" the moment this list is cut — build/plan_check.py
            # already worked around it by passing limit=10**6; the tool should not need
            # the workaround.
            "could_not_judge": needed,
            "not_applicable": not_applicable,
            "summary": {"present": len(present), "clear": len(clear), "unjudged": len(needed),
                        "not_applicable": len(not_applicable)},
            "note": "A fault only counts as present when a test actually failed. Anything under "
                    "could_not_judge is unknown, not passed. Anything under not_applicable had "
                    "every one of its tests declined by an `applies_when` precondition, so none "
                    "ran: the question does not arise, which is neither a pass nor an unjudged."}

def measurement_vocabulary(slot=None, style=None, include_constraints=True):
    """Every variable name the corpus tests on, so a caller knows what to measure.

    Fault-corpus variables are counted by actual test usage across faults/*.json, as before
    WP-1.2. When include_constraints is set (the default), a style's migrated constraint tests
    (schema/constraint.schema.json, WP-1.1 -- 140 of ~660 so far) are folded in the same way and
    each variable is tagged with which corpus tests on it. The two vocabularies were built
    independently and only partially overlap (roof_pitch_rise_per_12 and water_table_height_in
    are shared; most names are not) -- source shows which, so a caller doesn't assume a fault
    variable is also a constraint variable or the reverse. slot has no meaning for a constraint
    (constraints aren't slot-scoped), so a slot-filtered call skips the constraint pass entirely
    rather than mixing a filtered list with an unfiltered one under one used_by count."""
    D = _data(); vocab = {}
    for f in D["faults"].values():
        if slot and slot not in f["slots"]: continue
        if style and not _applies(f, style, D): continue
        for t in [f.get("test")] + list(f.get("secondary_tests") or []):
            if not t or not t.get("expression"): continue
            # A precondition's own variables are variables a caller must measure -- without
            # dormer_count the parity test is could-not-evaluate, so a vocabulary that omitted it
            # would tell a caller to photograph everything except the number that decides whether
            # the question is asked at all.
            # A PRECONDITION'S VARIABLES CARRY THE PRECONDITION'S OWN UNITS, not the test's. The
            # first version tagged them with `t["units"]`, so
            # `an_order_is_applied_to_the_wall_carrying_the_eave_cornice` -- a 0/1 flag declared
            # `units: count` in its own applies_when -- was published to
            # tdl_measurement_vocabulary and GET /api/vocabulary as a `ratio`, because the test it
            # guards measures one. A caller told to measure a ratio will not supply a flag.
            when = t.get("applies_when") or {}
            sources = [(t["expression"], t)] + ([(when["expression"], when)] if when.get("expression") else [])
            for expr, owner in sources:
                for nm in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", expr):
                    if nm in ("min","max","abs","round"): continue
                    v = vocab.setdefault(nm, {"used_by": 0, "units": owner.get("units"),
                                               "measurable_from": t.get("measurable_from"), "source": []})
                    v["used_by"] += 1
                    if "fault" not in v["source"]: v["source"].append("fault")
    if include_constraints and not slot:
        cv = _load_constraint_vocab().VOCABULARY
        styles = [D["styles"][style]] if style and style in D["styles"] else D["styles"].values()
        for n in styles:
            for c in n.get("constraints", []):
                t = c.get("test")
                if not t or not t.get("expression"): continue
                for nm in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", t["expression"]):
                    if nm in ("min","max","abs","round"): continue
                    v = vocab.setdefault(nm, {"used_by": 0, "units": t.get("units"),
                                               "measurable_from": t.get("measurable_from"), "source": []})
                    v["used_by"] += 1
                    if "constraint" not in v["source"]: v["source"].append("constraint")
                    if nm in cv and "note" not in v: v["note"] = cv[nm]["note"]
    return {"variables": dict(sorted(vocab.items(), key=lambda kv: -kv[1]["used_by"])),
            "count": len(vocab),
            "hint": ("pass any subset of these to tdl_check_measurements (fault-sourced findings) "
                     "or tdl_check_style_constraints (constraint-sourced, needs a style); missing "
                     "ones are reported, never assumed.")}

# ----------------------------------------------------------------- assets
def find_assets(slot=None, style=None, fault=None, role=None, status=None, pack=None, limit=20):
    # `pack` because the 73 records that actually HAVE a file depict a proportion pack and an
    # assembly -- never a node or a slot -- and there was no filter that could reach them. Every
    # sourced record in the corpus was unqueryable by every caller: the MCP tool, /api/assets and
    # the app alike. A record nothing can ask for is not sourced in any sense a reader cares
    # about.
    D = _data(); out = []
    for a in D["assets"]:
        dp = a.get("depicts", {})
        if slot and slot not in (dp.get("slots") or []): continue
        if style and style not in (dp.get("nodes") or []): continue
        if fault and fault not in (dp.get("faults") or []): continue
        if pack and pack not in (dp.get("packs") or []): continue
        if role and a["role"] != role: continue
        if status and a["status"] != status: continue
        out.append({"id": a["id"], "kind": a["kind"], "role": a["role"], "status": a["status"],
                    "priority": a.get("priority"), "caption": a["caption"],
                    "alt_text": a["alt_text"], "pair_with": a.get("pair_with"),
                    "file": (a.get("file") or {}).get("path"),
                    "rights": asset_rights(a),
                    "generated_from": a.get("generated_from")})
    return {"matches": len(out), "returned": min(limit, len(out)), "assets": out[:limit],
            "note": ("Records with status 'wanted' have no file yet. The alt_text is the machine-readable "
                     "form of the picture and is written to be reasoned from, so use it even when the "
                     "image is missing — and tell the human the image is still outstanding. "
                     "A record carrying `generated_from` is a DRAWING generated from the corpus's own "
                     "rules, not a photograph of a building; say so if you show it. Every record "
                     "carries `rights`, and `rights.publishable` is false until a person has set a "
                     "licence — a file is not clear to redistribute merely because it exists.")}


def asset_rights(a):
    """What a consumer needs in order to use an image lawfully, served WITH the file path.

    This existed nowhere. `find_assets` returned a `file` path and no licence, no attribution and
    no author, and it is the only programmatic route by which an asset reaches anyone -- the MCP
    tool, the workbench API and the app all read it. So the moment a licensed image entered the
    manifest the corpus would have handed every consumer a file with no way to attribute it, and
    made non-compliance structural rather than merely likely.

    `publishable` is deliberately conservative and deliberately not a licence check: it says a
    PERSON has recorded a conclusion, not that a machine agreed with one. `unknown` is the default on most
    records and it blocks; `rights_evidence` without a `license` is
    evidence a harvester collected and nobody has ruled on, which is also not a clearance."""
    p = a.get("provenance") or {}
    lic = p.get("license")
    # THREE STATES, NOT A BOOL. `False` could not distinguish "nobody has looked" (`unknown`,
    # on 1,716 records) from "a person ruled this share-alike and it may not be redistributed",
    # and this corpus's own rule is that unjudged is never collapsed into judged. And a licence
    # is not a clearance for a file that does not exist: `owned` with `file: null` came back
    # publishable on 61 records.
    if not lic or lic == "unknown":
        publishable = "unjudged"
    elif lic in ("public-domain", "cc0", "owned", "licensed"):
        publishable = "yes" if (a.get("file") or {}).get("path") else "no-file"
    else:
        publishable = "no"          # cc-by / cc-by-sa: obligations this corpus has not accepted
    return {"license": lic or "unknown",
            "publishable": publishable,
            "attribution_required": bool(p.get("attribution_required")
                                         or (lic or "").startswith("cc-by")),
            "attribution_text": p.get("attribution_text"),
            "author": p.get("author"),
            "source": p.get("source"),
            "url": p.get("url"),
            "rights_evidence": p.get("rights_evidence"),
            "rights_evidence_url": p.get("rights_evidence_url")}

def get_massing(massing_id=None, style=None, limit=25):
    D = _data()
    if massing_id:
        m = D["massings"].get(massing_id)
        if not m: return {"error": f"no massing '{massing_id}'", "available": sorted(D["massings"])}
        users = [{"style": s["id"], "affinity": a["affinity"]} for s in D["styles"].values()
                 for a in s.get("massing_affinities", []) if a["massing"] == massing_id]
        return {"massing": m, "used_by": users}
    if style:
        n = D["styles"].get(style)
        if not n: return {"error": f"no style '{style}'"}
        return {"style": style, "affinities": [a | {"name": D["massings"].get(a["massing"], {}).get("name"),
                                                    "expansion_logic": D["massings"].get(a["massing"], {}).get("expansion_logic")}
                                               for a in n.get("massing_affinities", [])],
                "note": "Massing is not style. The same skeleton wears a different grammar."}
    return {"massings": [{"id": m["id"], "name": m["name"], "footprint": m["footprint"], "stories": m["stories"],
                          "circulation": m.get("circulation")} for m in list(D["massings"].values())[:limit]],
            "count": len(D["massings"])}


# ----------------------------------------------------------------- rooms & groupings
def find_room(query="", function_class=None, style=None, massing=None, limit=25):
    D = _data(); q = (query or "").lower().strip(); out = []
    for r in D["rooms"].values():
        if function_class and r["function_class"] != function_class: continue
        if massing and massing not in (r.get("massing_fit") or []): continue
        if style:
            sv = next((v for v in r.get("style_variation", []) if v["style"] == style), None)
            if sv and sv.get("present") is False: continue
        if q and q not in (r["name"] + " " + r["id"] + " " + " ".join(r.get("aka", [])) + " " + r["description"]).lower():
            continue
        card = {"id": r["id"], "name": r["name"], "aka": r.get("aka", []),
                "function_class": r["function_class"], "privacy_rank": r["privacy_rank"],
                "area_sf": r["dimensions"]["area_sf"],
                "critical_dimension": r["dimensions"].get("critical_dimension")}
        if style:
            sv = next((v for v in r.get("style_variation", []) if v["style"] == style), None)
            if sv: card["IN_THIS_STYLE"] = sv
        out.append(card)
    out.sort(key=lambda c: (c["privacy_rank"], c["id"]))
    return {"matches": len(out), "returned": min(limit, len(out)), "rooms": out[:limit],
            "note": ("Rooms are style-independent. privacy_rank runs 0 street, 1 threshold, 2 public, "
                     "3 family, 4 private, 5 intimate — a plan that scrambles that gradient will feel wrong "
                     "however well it is detailed.")}

def get_room(room_id, style=None):
    D = _data(); r = D["rooms"].get(room_id)
    if not r: return {"error": f"no room '{room_id}'", "did_you_mean": [k for k in D["rooms"] if room_id.lower() in k][:8]}
    out = json.loads(json.dumps(r))
    out["appears_in_groupings"] = [g["id"] for g in D["groupings"].values()
                                   if any(x["room"] == room_id for x in g["rooms"])]
    if style:
        sv = next((v for v in r.get("style_variation", []) if v["style"] == style), None)
        out["for_this_style"] = sv or {"note": "no style-specific record; the neutral room applies"}
    return out

def get_grouping(grouping_id=None, massing=None, style=None, scale=None, limit=20):
    D = _data()
    if grouping_id:
        g = D["groupings"].get(grouping_id)
        if not g: return {"error": f"no grouping '{grouping_id}'", "available": sorted(D["groupings"])}
        out = json.loads(json.dumps(g))
        out["rooms_detail"] = [{"room": x["room"], "role": x["role"],
                                "name": D["rooms"].get(x["room"], {}).get("name"),
                                "area_sf": D["rooms"].get(x["room"], {}).get("dimensions", {}).get("area_sf")}
                               for x in g["rooms"]]
        if style:
            out["for_this_style"] = next((v for v in g.get("style_variation", []) if v["style"] == style), None)
        return out
    out = []
    for g in D["groupings"].values():
        if scale and g.get("scale") != scale: continue
        if massing and not any(a["massing"] == massing and a.get("fit") != "forbidden" for a in g["attaches_to"]): continue
        if style:
            sv = next((v for v in g.get("style_variation", []) if v["style"] == style), None)
            if sv and sv.get("present") is False: continue
        out.append({"id": g["id"], "name": g["name"], "scale": g.get("scale"),
                    "rooms": [x["room"] for x in g["rooms"]],
                    "privacy_span": g.get("privacy_span"), "typical_area_sf": g.get("typical_area_sf"),
                    "hard_rules": sum(1 for r in g["internal_rules"] if r.get("severity") == "hard"),
                    "description": g["description"][:180]})
    return {"count": len(out), "groupings": out[:limit],
            "note": ("A grouping is the scale people actually design at. Nobody composes a house room by "
                     "room; they compose it from clusters with their own internal logic, and attaches_to "
                     "is the join to the massing catalogue.")}


# ----------------------------------------------------------------- plans
def check_plan(plan, strict=False):
    """Validate a plan record across five layers: rooms, groupings, faults, code, style."""
    pc = _load_plan_checker()
    try:
        detail = _schema_error("plan", plan)
    except ImportError:
        # An absent validator is an environment fact, not a verdict about the plan.
        # Collapsing it into "does not match the schema" was OQ 35's exact complaint:
        # a dependency problem laundered as a data judgment.
        return {"error": "could not validate: the jsonschema package is not installed",
                "detail": "pip install jsonschema", "unvalidated": True}
    if detail:
        return {"error": "plan does not match the plan schema", "detail": detail[:400],
                "hint": "see schema/plan.schema.json; the minimum is id, name, style and one level with rooms"}
    return pc.check(plan, strict=strict)

@functools.lru_cache(maxsize=2)
def validator(name):
    """The COMPILED validator for schema/<name>.schema.json, built once per process.

    `jsonschema.validate(instance, schema)` REBUILDS the validator on every call, and three of
    this module's callers -- `check_plan`, `critique_plan`, `revise_plan` -- sat on the route
    the infrastructure audit measured as the whole server's bound. `workbench/server/app.py`
    learned this at WP-10.1 and compiled the validator at the door; the lesson stopped there,
    so `/api/plan/evaluate` ran a compiled validation at the gate and then an UNCOMPILED one
    inside `check_plan`, on the same document, one of them at 4 ms and the other at 79.

    Measured here, same interpreter, on the record `evaluate()` actually passes (32,389 B, the
    SOLVED plan rather than the declared one):

        jsonschema.validate(plan, schema("plan"))      79.1 ms   -- 23% of the 338 ms budget
        validator("plan").iter_errors(plan)             4.2 ms

    Returns None where jsonschema is absent, which every caller already has a branch for: an
    absent validator is an environment fact and not a verdict about the plan (OQ 35).

    The schema dict comes from `schema()`, which is cached and SHARED. A validator holds a
    reference to it and neither mutates it. Both caches are cleared together by
    `workbench/server/corpus.invalidate()`, which `test_reload_clears_every_cache` enforces by
    walking this module rather than by naming them.
    """
    try:
        import jsonschema
    except ImportError:
        return None
    sch = schema(name)
    return jsonschema.validators.validator_for(sch)(sch)


def _schema_error(name, doc):
    """The first schema error in `doc`, as a string, or None. Raises ImportError with no
    jsonschema, which is a different thing from a plan that does not validate and is why the
    callers catch it separately."""
    v = validator(name)
    if v is None:
        raise ImportError("jsonschema")
    err = next(iter(sorted(v.iter_errors(doc), key=lambda e: list(e.absolute_path))), None)
    if err is None:
        return None
    at = "/" + "/".join(str(x) for x in err.absolute_path)
    return f"{err.message} (at {at})"


@functools.lru_cache(maxsize=8)
def schema(name):
    """One parse of schema/<name>.schema.json per process, shared by every caller.

    check_plan re-read and re-parsed plan.schema.json on EVERY call, and check_plan is what
    /api/plan/evaluate runs behind a 400 ms debounce on every wall drag. Six sites did the
    same thing with two files. The corpus does not change under a running server — that is
    the property the search index already leans on — and /api/dev/reload clears this with
    the rest when it does.

    The returned object is SHARED. jsonschema.validate does not mutate it; a caller who
    hands it onward should copy_json it first, which is what plan_schema/brief_schema do.
    """
    # basename for the same reason load_parti has one, and the irony is recorded rather than
    # quietly fixed: this helper was added in the very commit that reduced the parti join to a
    # single sanitised site, and it reintroduced the shape one screen above that docstring. No
    # caller passes user input today — it is schema("plan") and schema("brief") — so this was
    # never live. It is one endpoint away from being live, which is the whole argument.
    safe = os.path.basename(str(name))
    return json.load(open(os.path.join(ROOT, "schema", f"{safe}.schema.json")))


def _load_plan_checker():
    return _mod("plan_check", os.path.join(ROOT, "build", "plan_check.py"))

def plan_schema():
    return {"schema": copy_json(schema("plan")),
            "examples": [os.path.basename(f) for f in sorted(glob.glob(os.path.join(ROOT, "plans", "*.json")))],
            "hint": ("A plan is a topology plus approximate dimensions — enough to check, not enough to build. "
                     "Doors imply adjacency in both directions; the validator derives the graph from them. "
                     "Give width_ft as the SHORT dimension and window_head_ft wherever you can, because "
                     "the daylight and furniture checks are the two that catch the most.")}


# ----------------------------------------------------------------- compose
def _composer():
    return _mod("compose", os.path.join(ROOT, "build", "compose.py"))

def compose(brief, candidates=4, include_plans=False, revise=True, revise_rounds=4,
            revise_engine="auto", revise_budget_s=120.0):
    try:
        import jsonschema
        jsonschema.validate(brief, schema("brief"))
    except Exception as e:
        return {"error": "brief does not match the brief schema", "detail": str(e)[:400],
                "hint": "the minimum is style and target_area_sf; see tdl_brief_schema"}
    bounded = []
    candidates = int(_bounded("candidates", candidates, 1, COMPOSE_MAX_CANDIDATES, 4, bounded))
    revise_rounds = int(_bounded("revise_rounds", revise_rounds, 0, REVISE_MAX_ROUNDS, 4, bounded))
    revise_budget_s = _bounded("revise_budget_s", revise_budget_s, 0.0, REVISE_MAX_BUDGET_S,
                               REVISE_DEFAULT_BUDGET_S, bounded)
    if revise_engine not in ("heuristic", "cp", "auto"):
        return {"error": f"unknown revise_engine {revise_engine!r} -- one of heuristic, cp, auto"}
    res = _composer().compose(brief, candidates, revise=bool(revise), revise_rounds=revise_rounds,
                              revise_engine=revise_engine, revise_budget_s=revise_budget_s)
    if bounded:
        res["bounded"] = bounded
    if not include_plans:
        for c in res["candidates"]:
            c["plan_rooms"] = sum(len(l["rooms"]) for l in c["plan"]["levels"])
            c.pop("plan")
        res["note"] = "Plans omitted to save context. Call again with include_plans=true for the full records, or pass one to tdl_check_plan."
    return res

@functools.lru_cache(maxsize=1)
def _all_partis():
    """The 21 parti records, parsed once. list_partis re-globbed and re-parsed all of them on
    every call — 0.95 ms of filesystem work per request to /api/partis — which is the same bug,
    one function over, that corpus.search_index's comment describes fixing. Cleared by
    corpus.invalidate() with the rest."""
    return tuple(json.load(open(f))
                 for f in sorted(glob.glob(os.path.join(ROOT, "partis", "*.json"))))


def list_partis(style=None, massing=None):
    D = _data()
    out = []
    for p in _all_partis():
        if style and style not in p["styles"]: continue
        if massing and p["massing"] != massing and massing not in p.get("alternate_massings", []): continue
        out.append({"id": p["id"], "name": p["name"], "massing": p["massing"],
                    "storeys": p.get("storeys"), "area_range_sf": p.get("area_range_sf"),
                    "bedroom_range": p.get("bedroom_range"), "styles": p["styles"],
                    "description": p["description"], "trades_away": p.get("trades_away"),
                    "grows_by": (p.get("scaling") or {}).get("grows_by")})
    return {"count": len(out), "partis": out,
            "note": ("A parti specifies topology and roles only — dimensions come from the room catalogue "
                     "and are scaled to the brief, so the library never duplicates room data. Every one is "
                     "descended from something that was actually built, which is why the composer seeds from "
                     "them rather than searching from noise.")}

def brief_schema():
    return {"schema": copy_json(schema("brief")),
            "examples": [os.path.basename(f) for f in sorted(glob.glob(os.path.join(ROOT, "briefs", "*.json")))],
            "hint": ("Only style and target_area_sf are required. Everything absent is decided by the "
                     "composer and reported in the decision log as an assumption, not smuggled in as a fact. "
                     "Put the household in `household` — it is the thing that decides whether the dining room "
                     "gets built and never used.")}


# ----------------------------------------------------------------- geometry
def load_parti(parti):
    """Read one parti template by id, or None. THE ONLY WAY a caller-supplied parti id
    may become a path — call this, never build the path yourself.

    basename, because `parti` arrives in a POST body: /api/plan/evaluate, /api/drawings/{kind}
    and /api/export/{fmt} pass body.get("parti") straight through, so "../schema/plan" read
    ROOT/schema/plan.json and an ABSOLUTE id won the join outright. The contents are never
    returned — the file becomes a parti template inside geo.solve — but a caller could still
    learn which paths exist and hold JSON, from the 500-vs-422 an unreadable one produces.

    This function exists because the first fix did not close the class. It was applied here,
    in place_plan, with a comment claiming it covered /api/drawings/{kind} — and that endpoint
    does not come through place_plan at all. workbench/server/corpus.py had its own two copies
    of the join, both unsanitised, and they stayed that way. Three copies of one rule is the
    same shape as the citation grammar's three spellings in CLAUDE.md: one implementation,
    every caller through it, and a test that fails if a fourth copy appears.
    """
    if not parti:
        return None
    safe = os.path.basename(str(parti))
    f = os.path.join(ROOT, "partis", f"{safe}.json")
    if not os.path.exists(f):
        return None
    return json.load(open(f))


def place_plan(plan, parti=None, candidates=250, svg_path=None, engine="auto"):
    """Place room rectangles in a footprint. Both levels are solved together.
    engine: "auto" (CP-SAT when available — WP-2.3's real solver, with named
    conflict sets), "cp", or "heuristic" (the fast hill-climb; what the
    workbench uses per edit gesture, where a ~25 s proof per wall drag would
    make the surface unusable — proving is an explicit act there)."""
    geo = _mod("geometry", os.path.join(ROOT, "build", "geometry.py"))
    pt = load_parti(parti)
    # OQ 44: the MCP tool takes the reproducible default deliberately and does not expose a way
    # to turn it off. Everything arriving here is a plan somebody will read, keep or compare
    # against another one, and a record that cannot be re-derived is worth less than the seconds
    # it saves. (The ruling was made against the WP-2.3 solver that did not survive the 25 Aug
    # merge; it is about determinism, not about which engine, so it carries over unchanged.)
    out = geo.solve(copy_json(plan), pt, candidates, engine=engine)
    if "error" in out: return out
    if svg_path:
        rp = _mod("render_plan", os.path.join(ROOT, "build", "render_plan.py"))
        rp.render(out, svg_path); out["svg"] = svg_path
    return placement_summary(out)


def placement_summary(out):
    """The placement payload, projected off a SOLVED record (WP-9.1 split this out of
    place_plan so workbench/server/evaluate.py can solve the full record ONCE, judge THAT
    record with plan_check's drawn layer, and still return the payload the sheet draws --
    one building, judged and drawn from the same placement)."""
    # WP-6.2: the PLACED openings ride with the placement, additively. A door only became a
    # thing with a wall and a position in plan schema 0.3.0, and build/openings.py writes
    # them onto the solved record — which this payload then dropped, so every consumer
    # (the workbench sheet among them) went on inventing positions from the unplaced record
    # it already held. The stair and the fixture layout are here for the same reason: they
    # are placement facts, and there is nowhere else for a reader to get them.
    return {"footprint": out["footprint"], "geometry_report": out["geometry_report"],
            # WP-11.1: what this placement GAVE UP, computed once in build/disclosures.py and
            # rendered by both surfaces -- the printed plate draws these lines and the bench
            # shows the same list, so the two cannot drift the way the citation grammar's three
            # spellings did. Before this the bench's own paragraph told a reader that the walls
            # a proof had to give up "are named above rather than dropped", and nothing above
            # named them: `downgraded_wall_pins` had no reader on any surface.
            "disclosures": _disclosures().banner(out, styles=_data()["styles"],
                                                 partis=_partis()),
            "rooms": [{"level": lv.get("index"), "id": r["id"], "name": r.get("name"),
                       "geometry": r.get("geometry"),
                       "doors": r.get("doors"), "windows": r.get("windows"),
                       "fixture_layout": r.get("fixture_layout")}
                      for lv in out["levels"] for r in lv["rooms"] if r.get("geometry")],
            "stair": out.get("stair"),
            "opening_report": out.get("opening_report"),
            "svg": out.get("svg"),
            "note": ("Coordinates are in feet with the origin at the south-west corner, x east and y north. "
                     "If geometry_report.infeasible is present, read its conflicts FIRST — CP-SAT proved the "
                     "record's declared facts cannot all hold and this placement is the labelled least-bad "
                     "relaxation (WP-2.3). Then read geometry_report.relaxations: each cut taken off the bay "
                     "line is a joist run that does not land on a bearing wall and a window bay that will not "
                     "centre. geometry_report.solver names which engine placed this and why.")}

def copy_json(o): return json.loads(json.dumps(o))


# ----------------------------------------------------------------- the critique and the loop (WP-9)
# THE BOUNDS ON THE LOOP'S KNOBS, spelled once. The HTTP routes clamped rounds, candidates and
# the budget and the MCP tools -- `tdl_revise_plan`, `tdl_critique_plan`, `tdl_compose` --
# passed them raw onto a synchronous threadpool token (the session's audit: one call with a
# thousand rounds on the proving engine held a token for hours, inside the 60/hour meter).
# The routes read these too, so a second spelling cannot drift from this one.
MAX_CANDIDATES = 2000            # geometry.solve's pool; a full placement loop per candidate
REVISE_MAX_ROUNDS = 8
REVISE_DEFAULT_BUDGET_S = 120.0  # compose()'s own default, per returned SET (not per candidate)
REVISE_MAX_BUDGET_S = 600.0
COMPOSE_MAX_CANDIDATES = 24      # the parti catalogue holds 21


def _bounded(name, value, lo, hi, default, bounded):
    try:
        v = float(value) if value is not None else float(default)
    except (TypeError, ValueError):
        v = float(default)
    out = max(lo, min(hi, v))
    if value is None or out != v:
        bounded.append(f"{name}: {value!r} -> {out:g}")
    return out


def critique_plan(plan, engine="auto", candidates=250, place=True, parti=None):
    """The analyst: place the record once (or reuse the placement it carries), judge the
    placed house, and sort every finding into what it means to a generator. See
    build/critique.py. The full findings ride inside each issue; the check's own summary
    counts are returned beside them and the check itself is omitted to spare the caller's
    context -- tdl_check_plan returns it."""
    try:
        _bad = _schema_error("plan", plan)
    except ImportError:
        return {"error": "could not validate: the jsonschema package is not installed", "unvalidated": True}
    except Exception as e:
        return {"error": "the plan schema could not be compiled", "detail": str(e)[:400]}
    if _bad:
        return {"error": "plan does not match the plan schema", "detail": _bad[:400]}
    if parti is not None and not isinstance(parti, str):
        # an ID, resolved through load_parti -- the one confined path from a caller's string
        # to a file. A caller-supplied parti RECORD would become the template geometry reads
        # (bay module, bay count) with no check at all (WP-9.4).
        return {"error": "parti must be a parti id, not a record", "detail": type(parti).__name__}
    bounded = []
    candidates = int(_bounded("candidates", candidates, 1, MAX_CANDIDATES, 250, bounded))
    if engine not in ("heuristic", "cp", "auto"):
        return {"error": f"unknown engine {engine!r} -- one of heuristic, cp, auto"}
    CR = _mod("critique", os.path.join(ROOT, "build", "critique.py"))
    res = CR.critique(plan, engine=engine, candidates=candidates, parti=parti, place=bool(place))
    out = {k: v for k, v in res.items() if k not in ("plan", "check")}
    if bounded:
        out["bounded"] = bounded
    out["check_summary"] = {k: res["check"].get(k) for k in
                            ("counts", "fault_summary", "constraint_summary", "drawn_summary", "elevation_summary")}
    return out


def revise_plan(plan, rounds=6, engine="auto", candidates=250, place=True, include_plan=True,
                budget_s=None, parti=None, on_round=None):
    """The corrective revisions: critique, move, re-place, re-critique, accept or roll back,
    round after round. See build/revise.py. Returns the report (every round, every move with
    its finding and its basis, what remains by class, what was handed to the architect, what
    was refused and why) and, with include_plan, the revised record carrying the same report
    as `revision_report`."""
    try:
        _bad = _schema_error("plan", plan)
    except ImportError:
        return {"error": "could not validate: the jsonschema package is not installed", "unvalidated": True}
    except Exception as e:
        return {"error": "the plan schema could not be compiled", "detail": str(e)[:400]}
    if _bad:
        return {"error": "plan does not match the plan schema", "detail": _bad[:400]}
    if parti is not None and not isinstance(parti, str):
        return {"error": "parti must be a parti id, not a record", "detail": type(parti).__name__}
    bounded = []
    rounds = int(_bounded("rounds", rounds, 1, REVISE_MAX_ROUNDS, 6, bounded))
    candidates = int(_bounded("candidates", candidates, 1, MAX_CANDIDATES, 250, bounded))
    # a budget ALWAYS, and bounded: an absent one was no budget, and a job with none held the
    # worker for as long as the rounds took (the session's audit)
    budget_s = _bounded("budget_s", budget_s, 1.0, REVISE_MAX_BUDGET_S, REVISE_DEFAULT_BUDGET_S, bounded)
    if engine not in ("heuristic", "cp", "auto"):
        return {"error": f"unknown engine {engine!r} -- one of heuristic, cp, auto"}
    RV = _mod("revise", os.path.join(ROOT, "build", "revise.py"))
    # on_round is the bench's seam (WP-9.3): the revise job puts a `round` event per round so
    # a reader watches the loop run rather than a spinner. The MCP tool does not pass it.
    r = RV.revise(plan, rounds=rounds, engine=engine, candidates=candidates, budget_s=budget_s,
                  place=bool(place), parti=parti, on_round=on_round)
    out = {"report": r["report"], "key_before": r["key_before"], "key_after": r["key_after"],
           "stop_reason": r["stop_reason"], **({"bounded": bounded} if bounded else {}),
           "note": ("A lower key is not a good plan. Read handed_to_architect and suspects before "
                    "rounds: what the loop could not do is as much the result as what it did.")}
    if include_plan:
        out["plan"] = r["plan"]
    return out
