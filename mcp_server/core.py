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
    D = _data(); seen = seen or set(); out = []
    n = D["styles"].get(i)
    if not n: return out
    for e in sorted(n.get("lineage", []), key=lambda e: -e.get("weight", 1)):
        if not e.get("inherits_kit"): continue
        t = e["target"]
        if t in seen or t not in D["styles"]: continue
        seen.add(t); out.append(t); out.extend(_cascade(t, seen))
    return out

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
           "assemblies": [{"id": a["id"], "height_modules": a["height_modules"], "height_in": a["height_in_stated"],
                           "members": a["members"] if assembly else len(a["members"])} for a in d["assemblies"]],
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
        RULE_KEYS = ("target_slot", "dimension", "quantity", "expression", "value", "units",
                     "judgment", "range", "in_range", "note", "calibrated_for",
                     "authority_note", "diagnostic", "error")
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
        rows.append({"authority": auth, "pack": pid, "year": pk.get("authority", {}).get("year"),
                     "column_diameters": d["totals"].get("column_height_diameters"),
                     "column_in": d["totals"].get("column_height_in"),
                     "entablature_in": d["totals"].get("entablature_height_in"),
                     "entablature_over_column": round(d["totals"]["entablature_height_in"] / d["totals"]["column_height_in"], 4)
                        if d["totals"].get("entablature_height_in") and d["totals"].get("column_height_in") else None,
                     "confidence": pk.get("confidence")})
    if not rows: return {"error": f"no packs for order '{order}'", "orders": ["tuscan","doric","ionic","corinthian","composite"]}
    return {"order": order, "at_common_column_diameter_in": column_diameter, "authorities": rows,
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
        if excepted: card["EXCEPTION_FOR_THIS_STYLE"] = {"why": excepted["why"], "bounds": excepted.get("bounds"),
                                                        "bounds_test": excepted.get("bounds_test")}
        for inv in f.get("inverted_by", []):
            if style and inv["style"] == style: card["INVERTED_FOR_THIS_STYLE"] = inv["statement"]
        out.append(card)
    out.sort(key=lambda c: (SEV.index(c["severity"]) if c["severity"] in SEV else 3,
                            ["endemic","common","occasional","rare"].index(c["frequency"]) if c.get("frequency") else 4))
    return {"matches": len(out), "returned": min(limit, len(out)), "faults": out[:limit],
            "note": ("Faults are element-first: most are universal, and style is a facet. Check "
                     "EXCEPTION_FOR_THIS_STYLE and INVERTED_FOR_THIS_STYLE before repeating a rule at "
                     "a client — a five-foot Georgian portico is a fault by Craftsman standards and correct by its own."),
            "next": "tdl_get_fault for the full record with fixes, or tdl_check_measurements if you have numbers"}

def get_fault(fault_id, style=None):
    D = _data(); f = D["faults"].get(fault_id)
    if not f:
        return {"error": f"no fault '{fault_id}'", "did_you_mean": [k for k in D["faults"] if fault_id.lower() in k][:8]}
    out = json.loads(json.dumps(f))
    if style:
        out["for_this_style"] = {
            "applies": _applies(f, style, D),
            "severity": next((s["severity"] for s in f.get("severity_by_style", []) if s["style"] == style), f["severity"]),
            "exception": next((e for e in f.get("exceptions", []) if e["style"] == style), None),
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
        # failure modes the WP-5.10 audit found are refused here too. Omitting `expression` made
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
    return {"status": "evaluated", "value": round(val, 4) if isinstance(val, float) else val,
            "required": required, "passes": ok, "units": t.get("units")}

def _load_constraint_vocab():
    return _mod("constraint_vocabulary", os.path.join(ROOT, "build", "constraint_vocabulary.py"))

def check_style_constraints(style, measurements):
    """Evaluate a style's own constraint tests (schema/constraint.schema.json, WP-1.1) against a
    dict of measurements -- the same present/clear/unjudged shape check_measurements already
    returns for faults, so a caller can ask 'does this style's roof-pitch rule pass at 9:12'
    without building a whole plan record for tdl_check_plan.

    Only 140 of the corpus's ~660 constraints carry a test as of WP-1.1's worked example
    (docs/constraints.md); the rest, and every scope: judgment constraint, come back under
    judgment_only rather than silently ignored."""
    D = _data()
    n = D["styles"].get(style)
    if not n:
        near = [s for s in D["styles"] if style.lower() in s][:6]
        return {"error": f"unknown style '{style}'", "did_you_mean": near}
    present, clear, needed, judgment_only = [], [], [], []
    for c in n.get("constraints", []):
        if c.get("deprecated_in_favour_of"):
            continue
        test = c.get("test")
        if not test:
            if c.get("severity") == "hard":
                judgment_only.append({"id": c.get("id"), "kind": c["kind"], "statement": c["statement"]})
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
            "summary": {"present": len(present), "clear": len(clear), "unjudged": len(needed)},
            "note": ("A constraint only counts as present (violated) when a test actually failed. "
                     "could_not_judge is unknown, not passed. judgment_only lists hard constraints "
                     "with no test at all -- scope: judgment, or simply not yet migrated.")}

def check_measurements(measurements, style=None, slot=None, include_needed=True, limit=40):
    """Evaluate every applicable fault test against a dict of measurements.

    This is the corpus made executable: give it what you can measure from a photograph or a
    drawing and it tells you which faults are present, which are clear, which it could not judge
    because a number is missing, and which are NOT APPLICABLE -- every test preconditioned on a
    measurement this house does not meet, so none ran. Four states, not three; the docstring said
    three for a day after the fourth shipped."""
    D = _data()
    present, clear, needed, not_applicable = [], [], [], []
    for f in D["faults"].values():
        if slot and slot not in f["slots"]: continue
        if style and not _applies(f, style, D): continue
        tests = [f.get("test")] + list(f.get("secondary_tests") or [])
        exc = next((e for e in f.get("exceptions", []) if style and e["style"] == style), None)
        if exc and exc.get("bounds_test"): tests = [exc["bounds_test"]] + tests[1:]
        # OQ 63: a test scoped to another style is not run at all. Not run is not the same as
        # passed -- a test that is not for this house says nothing about this house, and the
        # fault's judgement rests on the tests that ARE for it.
        tests = [t for t in tests if t and _test_applies(t, style, D)]
        results = [r for r in (_eval_test(t, measurements) for t in tests) if r]
        ev = [r for r in results if r["status"] == "evaluated"]
        if not ev:
            miss = sorted({m for r in results if r["status"] == "need_measurements" for m in r["missing"]})
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
                not_applicable.append({"fault": f["id"], "name": f["name"],
                                       "because": sorted({r["because"] for r in declined}),
                                       "required": sorted({r["required"] for r in declined}),
                                       "note": "Every test of this fault is preconditioned on a "
                                               "measurement this house does not meet, so none was "
                                               "run. Not a pass -- the question does not arise."})
                continue
            # `errs` is why this branch exists in this shape. A fault whose every test
            # ERRORED produced no `ev` and no `miss`, so it was appended to nothing: not
            # present, not clear, not unjudged, and absent from the summary counts — a
            # fault that silently vanished, which reads to a caller exactly like clear.
            # That is the one collapse this corpus forbids above all others.
            if include_needed and (miss or errs):
                row = {"fault": f["id"], "name": f["name"], "needs": miss,
                       "measurable_from": f.get("test", {}).get("measurable_from")}
                if errs:
                    row["errors"] = errs
                needed.append(row)
            continue
        failing = [r for r in ev if r["passes"] is False]
        row = {"fault": f["id"], "name": f["name"], "severity": next(
                 (s["severity"] for s in f.get("severity_by_style", []) if s["style"] == style), f["severity"]),
               "slots": f["slots"], "results": ev}
        if failing:
            # The tests that actually failed, kept apart from the ones that merely ran. A fault
            # with secondary tests can have its PRIMARY pass and a secondary fail -- which is
            # the fault being present -- and a caller reporting results[0] then quotes the
            # passing number as the evidence. build/plan_check.py did exactly that: a Cape with
            # two chimneys was reported as "The House With No Fire: 2 against at-least 1", a
            # sentence in which every number is right and the claim is nonsense.
            row["failing"] = failing
            row["symptom"] = f["symptom"]
            row["fix_cheap"] = (f.get("fixes") or {}).get("cheap")
            row["fix_right"] = (f.get("fixes") or {}).get("right")
            if exc: row["exception_applied"] = exc["why"]
            present.append(row)
        else:
            clear.append({"fault": f["id"], "name": f["name"], "results": ev})
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
def find_assets(slot=None, style=None, fault=None, role=None, status=None, limit=20):
    D = _data(); out = []
    for a in D["assets"]:
        dp = a.get("depicts", {})
        if slot and slot not in (dp.get("slots") or []): continue
        if style and style not in (dp.get("nodes") or []): continue
        if fault and fault not in (dp.get("faults") or []): continue
        if role and a["role"] != role: continue
        if status and a["status"] != status: continue
        out.append({"id": a["id"], "kind": a["kind"], "role": a["role"], "status": a["status"],
                    "priority": a.get("priority"), "caption": a["caption"],
                    "alt_text": a["alt_text"], "pair_with": a.get("pair_with"),
                    "file": (a.get("file") or {}).get("path")})
    return {"matches": len(out), "returned": min(limit, len(out)), "assets": out[:limit],
            "note": ("Records with status 'wanted' have no file yet. The alt_text is the machine-readable "
                     "form of the picture and is written to be reasoned from, so use it even when the "
                     "image is missing — and tell the human the image is still outstanding.")}

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
        import jsonschema
    except ImportError:
        # An absent validator is an environment fact, not a verdict about the plan.
        # Collapsing it into "does not match the schema" was OQ 35's exact complaint:
        # a dependency problem laundered as a data judgment.
        return {"error": "could not validate: the jsonschema package is not installed",
                "detail": "pip install jsonschema", "unvalidated": True}
    try:
        jsonschema.validate(plan, json.load(open(os.path.join(ROOT, "schema", "plan.schema.json"))))
    except Exception as e:
        return {"error": "plan does not match the plan schema", "detail": str(e)[:400],
                "hint": "see schema/plan.schema.json; the minimum is id, name, style and one level with rooms"}
    return pc.check(plan, strict=strict)

def _load_plan_checker():
    return _mod("plan_check", os.path.join(ROOT, "build", "plan_check.py"))

def plan_schema():
    return {"schema": json.load(open(os.path.join(ROOT, "schema", "plan.schema.json"))),
            "examples": [os.path.basename(f) for f in sorted(glob.glob(os.path.join(ROOT, "plans", "*.json")))],
            "hint": ("A plan is a topology plus approximate dimensions — enough to check, not enough to build. "
                     "Doors imply adjacency in both directions; the validator derives the graph from them. "
                     "Give width_ft as the SHORT dimension and window_head_ft wherever you can, because "
                     "the daylight and furniture checks are the two that catch the most.")}


# ----------------------------------------------------------------- compose
def _composer():
    return _mod("compose", os.path.join(ROOT, "build", "compose.py"))

def compose(brief, candidates=4, include_plans=False):
    try:
        import jsonschema
        jsonschema.validate(brief, json.load(open(os.path.join(ROOT, "schema", "brief.schema.json"))))
    except Exception as e:
        return {"error": "brief does not match the brief schema", "detail": str(e)[:400],
                "hint": "the minimum is style and target_area_sf; see tdl_brief_schema"}
    res = _composer().compose(brief, candidates)
    if not include_plans:
        for c in res["candidates"]:
            c["plan_rooms"] = sum(len(l["rooms"]) for l in c["plan"]["levels"])
            c.pop("plan")
        res["note"] = "Plans omitted to save context. Call again with include_plans=true for the full records, or pass one to tdl_check_plan."
    return res

def list_partis(style=None, massing=None):
    D = _data()
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "partis", "*.json"))):
        p = json.load(open(f))
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
    return {"schema": json.load(open(os.path.join(ROOT, "schema", "brief.schema.json"))),
            "examples": [os.path.basename(f) for f in sorted(glob.glob(os.path.join(ROOT, "briefs", "*.json")))],
            "hint": ("Only style and target_area_sf are required. Everything absent is decided by the "
                     "composer and reported in the decision log as an assumption, not smuggled in as a fact. "
                     "Put the household in `household` — it is the thing that decides whether the dining room "
                     "gets built and never used.")}


# ----------------------------------------------------------------- geometry
def place_plan(plan, parti=None, candidates=250, svg_path=None, engine="auto"):
    """Place room rectangles in a footprint. Both levels are solved together.
    engine: "auto" (CP-SAT when available — WP-2.3's real solver, with named
    conflict sets), "cp", or "heuristic" (the fast hill-climb; what the
    workbench uses per edit gesture, where a ~25 s proof per wall drag would
    make the surface unusable — proving is an explicit act there)."""
    geo = _mod("geometry", os.path.join(ROOT, "build", "geometry.py"))
    pt = None
    if parti:
        # basename, because `parti` arrives in a POST body: /api/plan/evaluate and
        # /api/drawings/{kind} pass body.get("parti") straight through, so "../schema/plan"
        # read ROOT/schema/plan.json. Authenticated and the contents are never returned —
        # the file becomes a parti template inside geo.solve — but it is the one place in the
        # repo where a user-supplied id becomes a path, and the example-plan handler four
        # lines away in app.py already does exactly this. Found by an adversarial audit.
        safe = os.path.basename(str(parti))
        f = os.path.join(ROOT, "partis", f"{safe}.json")
        if os.path.exists(f): pt = json.load(open(f))
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
    return {"footprint": out["footprint"], "geometry_report": out["geometry_report"],
            "rooms": [{"level": lv.get("index"), "id": r["id"], "name": r.get("name"),
                       "geometry": r.get("geometry")}
                      for lv in out["levels"] for r in lv["rooms"] if r.get("geometry")],
            "svg": out.get("svg"),
            "note": ("Coordinates are in feet with the origin at the south-west corner, x east and y north. "
                     "If geometry_report.infeasible is present, read its conflicts FIRST — CP-SAT proved the "
                     "record's declared facts cannot all hold and this placement is the labelled least-bad "
                     "relaxation (WP-2.3). Then read geometry_report.relaxations: each cut taken off the bay "
                     "line is a joist run that does not land on a bearing wall and a window bay that will not "
                     "centre. geometry_report.solver names which engine placed this and why.")}

def copy_json(o): return json.loads(json.dumps(o))
