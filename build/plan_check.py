#!/usr/bin/env python3
"""Plan validator — the critic, and the fitness function a composer will need.

Reads a plan record and reports every violation it can find across five layers:
rooms, groupings, faults, code, and style. Style exceptions are honoured throughout,
so a Georgian five-foot portico is not reported as the four-foot-porch fault.

  python3 build/plan_check.py plans/<id>.json [--json] [--layer room] [--min-severity serious]
"""
from __future__ import annotations
import json, os, glob, re, sys, argparse, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEV_ORDER = ["fatal", "serious", "minor", "advisory", "info"]
STRENGTH_SEV = {"hard": "fatal", "strong": "serious", "preferred": "minor"}
# Constraint severity (hard/soft/advisory, schema/constraint.schema.json) uses a different
# vocabulary than room-adjacency STRENGTH_SEV; mapped to match the STYLE layer's own existing
# choice of "serious" for a forbidden-slot violation, not room-adjacency's "fatal" for hard --
# a single wrong roof pitch is a serious style violation, not grounds to fail the whole plan
# the way a duplicate room id is.
CONSTRAINT_SEV = {"hard": "serious", "soft": "minor", "advisory": "advisory"}

def _load(name, path):
    # Delegates to build/modcache.py so a module is executed once per process
    # rather than once per call. Same signature, same standalone-script
    # behaviour; see that file's header for why (OQ 28). Loaded by path here
    # because this file is itself usually loaded by path, so `build/` is not
    # necessarily on sys.path yet.
    import sys as _sys
    _b = os.path.join(ROOT, "build")
    if _b not in _sys.path:
        _sys.path.insert(0, _b)
    import modcache as _mc
    return _mc.load(name, path)

# Genuinely interchangeable room types. A landing IS the stair hall at the head of the stair;
# a walk-in closet satisfies a rule written for a closet. Without this the validator flags
# correct plans for using the better of two words.
EQUIVALENT = [
    {"stair-hall", "landing"},
    {"closet", "walk-in-closet", "linen-press"},
    {"bathroom", "primary-bathroom"},
    {"dining-room", "eat-in-kitchen-area", "breakfast-room"},
    {"parlor", "living-room", "sitting-room", "family-room", "great-room", "drawing-room", "best-parlor"},
    {"entrance-hall", "vestibule", "stair-hall"},
    {"kitchen", "scullery"},
    {"pantry", "butlers-pantry", "larder"},
    {"bedroom", "bedchamber", "primary-bedroom"},
]
def _alias(t):
    out = {t}
    for grp in EQUIVALENT:
        if t in grp: out |= grp
    return out

def load_corpus():
    C = {"rooms": {}, "groupings": {}, "styles": {}, "faults": {}, "massings": {}, "slots": {}, "kits": {}}
    for f in sorted(glob.glob(f"{ROOT}/rooms/*.json")): r = json.load(open(f)); C["rooms"][r["id"]] = r
    for f in sorted(glob.glob(f"{ROOT}/groupings/*.json")): g = json.load(open(f)); C["groupings"][g["id"]] = g
    for f in sorted(glob.glob(f"{ROOT}/styles/*.json")): s = json.load(open(f)); C["styles"][s["id"]] = s
    for f in sorted(glob.glob(f"{ROOT}/faults/*.json")): x = json.load(open(f)); C["faults"][x["id"]] = x
    for f in sorted(glob.glob(f"{ROOT}/kits/*.kit.json")): k = json.load(open(f)); C["kits"][k["style"]] = k
    C["massings"] = {m["id"]: m for m in json.load(open(f"{ROOT}/massings/catalog.json"))}
    for g in json.load(open(f"{ROOT}/elements/slots.json"))["groups"]:
        for s in g["slots"]: C["slots"][s["id"]] = s
    return C

# ---------------------------------------------------------------- helpers
def style_chain(style_id, C):
    """Every id that 'this style' legitimately answers to: itself, its containers, its kit ancestors."""
    out, cur = set(), C["styles"].get(style_id)
    for _ in range(8):
        if not cur: break
        out.add(cur["id"])
        for e in cur.get("lineage", []):
            if e.get("inherits_kit"): out.add(e["target"])
        cur = C["styles"].get(cur.get("member_of") or "")
    return out

def excepted(rule, chain):
    return bool(set(rule.get("exceptions") or []) & chain)

def derive_constraint_vars(plan):
    """Narrow, conservative auto-derivation of a handful of constraint-vocabulary variables
    (build/constraint_vocabulary.py) directly from unambiguous plan structure.

    Deliberately small. Everything else a constraint's test.expression might reference has
    to come from an explicit plan.measurements entry, or the constraint stays unjudged --
    'unjudged is not passed' applies to constraints exactly as it already does to slots and
    faults elsewhere in this validator. Adding a derivation here is a real claim that the
    value is unambiguous from plan structure alone; when it isn't, leave it out."""
    v = {}
    levels = plan.get("levels") or []
    if levels:
        v["storey_count"] = len(levels)
        ground_idx = min(lv.get("index", 0) for lv in levels)
        ground_lv = next(lv for lv in levels if lv.get("index", 0) == ground_idx)
        ground_rooms = ground_lv.get("rooms", [])
        v["room_count_ground_floor"] = len(ground_rooms)
        gc = ground_lv.get("floor_to_ceiling_ft") or next(
            (r.get("ceiling_ft") for r in ground_rooms if r.get("ceiling_ft")), None)
        if gc:
            v["ceiling_height_ground_in"] = gc * 12
        cp = next((r for r in ground_rooms if r.get("type") == "centre-passage"), None)
        if cp and cp.get("width_ft") and cp.get("length_ft"):
            v["centre_passage_width_ft"] = min(cp["width_ft"], cp["length_ft"])
    ctx = plan.get("context") or {}
    if ctx.get("lot_width_ft") is not None: v["lot_width_ft"] = ctx["lot_width_ft"]
    if ctx.get("lot_depth_ft") is not None: v["lot_depth_ft"] = ctx["lot_depth_ft"]
    # WP-2.4: `site` is unambiguous plan structure exactly the way `context` already is --
    # every field on it is a fact about the lot the plan record itself asserts, not something
    # inferred from geometry -- so every key present passes straight through by name. A plan
    # that omits `site` entirely (nothing required it) simply leaves these unjudged, same as
    # any other constraint variable no measurement supplies.
    site = plan.get("site") or {}
    for k, val in site.items():
        if k == "note" or val is None: continue
        v[k] = val
    return v

class Findings:
    def __init__(self): self.items = []
    def add(self, severity, layer, statement, **kw):
        self.items.append({"severity": severity, "layer": layer, "statement": statement, **kw})
    def sorted(self):
        return sorted(self.items, key=lambda f: (SEV_ORDER.index(f["severity"]) if f["severity"] in SEV_ORDER else 9,
                                                 f["layer"], f.get("room") or ""))

# ---------------------------------------------------------------- the checker
def check(plan, C=None, strict=False):
    C = C or load_corpus()
    core = _load("tdlcore", f"{ROOT}/mcp_server/core.py")
    F = Findings()
    seen_pairs = set()
    style = plan.get("style")
    chain = style_chain(style, C)
    if style not in C["styles"]:
        F.add("fatal", "style", f"Unknown style '{style}'.", fix="Use a style id from the taxonomy.")

    # ---- index rooms and build the adjacency graph
    rooms, level_of = {}, {}
    for lv in plan["levels"]:
        for r in lv.get("rooms", []):
            if r["id"] in rooms:
                F.add("fatal", "plan", f"Duplicate room id '{r['id']}'.", room=r["id"])
            rooms[r["id"]] = r; level_of[r["id"]] = lv.get("index", 0)
    adj = {rid: set() for rid in rooms}
    rel = {}
    for rid, r in rooms.items():
        for d in r.get("doors", []):
            t = d["to"]
            if t == "exterior": continue
            if t not in rooms:
                F.add("serious", "plan", f"Door from '{rid}' to unknown room '{t}'.", room=rid)
                continue
            adj[rid].add(t); adj[t].add(rid)
            rel[(rid, t)] = rel[(t, rid)] = "direct-door"
    # Declared relations are kept beside the door-derived ones, not merged under
    # them: a pair can legitimately be joined by a door AND declared
    # not-visible-from (the door sits around a jog). The must-not-adjoin skip
    # below consults both; entered_from keeps reading the door-derived map only.
    # Before this, rel.setdefault meant a direct-door pair could NEVER satisfy
    # "record the relation as 'not-visible-from' if the separation is real" --
    # the exact interaction the finding's own fix text promises.
    declared_rel = {}
    for a in plan.get("adjacencies", []):
        if a["a"] in rooms and a["b"] in rooms:
            adj[a["a"]].add(a["b"]); adj[a["b"]].add(a["a"])
            rel.setdefault((a["a"], a["b"]), a["relation"]); rel.setdefault((a["b"], a["a"]), a["relation"])
            declared_rel[(a["a"], a["b"])] = declared_rel[(a["b"], a["a"])] = a["relation"]
    types_present = {r["type"] for r in rooms.values()}
    def types_adjacent(rid):
        out = set()
        for x in adj[rid]: out |= _alias(rooms[x]["type"])
        return out

    def circulation(x):
        t = C["rooms"].get(rooms[x]["type"])
        return bool(t) and t["function_class"] in ("circulation", "threshold")

    def types_near(rid):
        """Directly adjacent, plus anything one hop further through a hall.

        Rooms in a real house connect THROUGH circulation — a bedroom reaches its bathroom
        across a landing, not through a shared door. Requiring a shared wall for every
        should_adjoin turns the corridor, which is the correct answer, into a fault."""
        out = set(types_adjacent(rid))
        for mid in adj[rid]:
            if circulation(mid):
                for x in adj[mid]:
                    if x != rid: out |= _alias(rooms[x]["type"])
        return out

    # ============================================================ ROOM LAYER
    for rid, r in rooms.items():
        rt = C["rooms"].get(r["type"])
        if not rt:
            F.add("fatal", "room", f"Unknown room type '{r['type']}'.", room=rid,
                  fix="Use an id from the room catalogue, or add the room type.")
            continue
        label = r.get("name") or rt["name"]
        w, l = r.get("width_ft"), r.get("length_ft")
        area = (w * l) if (w and l) else None
        if w and l and w > l: w, l = l, w                     # width is the SHORT dimension

        # dimension bands
        if area:
            lo, hi = rt["dimensions"]["area_sf"]
            if area < lo * 0.9:
                F.add("serious", "room", f"{label} is {area:.0f} sf; the catalogue band for a {rt['name'].lower()} is {lo}-{hi} sf.",
                      room=rid, rule=rt["dimensions"].get("critical_dimension"))
            elif area > hi * 1.25:
                F.add("minor", "room", f"{label} is {area:.0f} sf, well above the {lo}-{hi} sf band. Confirm it is not a room that has stopped being a room.",
                      room=rid)
        if w and rt["dimensions"].get("width_ft"):
            lo, hi = rt["dimensions"]["width_ft"]
            if w < lo:
                F.add("serious", "room", f"{label} is {w} ft in its short dimension; below the {lo} ft floor for a {rt['name'].lower()}.",
                      room=rid, rule=rt["dimensions"].get("critical_dimension"))
        cmin = rt["dimensions"].get("ceiling_min_ft")
        ch = r.get("ceiling_ft") or next((lv.get("floor_to_ceiling_ft") for lv in plan["levels"]
                                          if any(x["id"] == rid for x in lv.get("rooms", []))), None)
        if cmin and ch and ch < cmin:
            F.add("serious", "room", f"{label} ceiling {ch} ft is under the {cmin} ft the room type wants.", room=rid)

        # ---- furniture fit: the check most plans have never had run on them
        for it in rt.get("furniture", []):
            if not it.get("essential", True) or not (w and l): continue
            fw, fl = sorted(it["footprint_in"])
            # Some catalogue entries use clearance_in for a VIEWING or standing distance rather
            # than a physical gap — a television and a hung picture are both about four inches
            # deep. Nothing four inches deep constrains the width of a room, so anything without
            # real bulk is not a fit constraint.
            if fw < 8:
                continue
            cl = it.get("clearance_in") or 0
            # A table needs clearance on both sides; a counter, bench, sideboard or run of
            # casework is against a wall and needs it on one. Treating them alike fails every
            # galley kitchen and butler's pantry against its own rule.
            place = it.get("placement") or ("against-wall" if re.search(
                r"counter|bench|sideboard|cabinet|casework|drawer|shelf|shelv|press|cupboard|vanity|range|refrigerat|sink|washer|dryer|wardrobe|dresser|chest|bookcase|desk|piano|bed\b",
                it["item"], re.I) else "freestanding")
            sides = 1 if place in ("against-wall", "corner", "built-in") else 2
            need_short = (fw + sides * cl) / 12.0
            need_long = (fl + 2 * min(cl, 36)) / 12.0     # ends take chair pull, not full passage
            if w + 1e-6 < need_short:
                F.add("serious", "furniture",
                      f"{label} cannot take its {it['item']}: needs {need_short:.1f} ft across ({fw} in item + {sides} x {cl} in clearance, {place}), has {w} ft.",
                      room=rid, rule=rt["dimensions"].get("critical_dimension"),
                      fix=f"Widen to {need_short:.1f} ft, or accept that the room will not hold a {it['item']}.")
            elif l + 1e-6 < need_long:
                F.add("minor", "furniture",
                      f"{label} is tight along its length for its {it['item']}: needs about {need_long:.1f} ft, has {l} ft.", room=rid)

        # ---- daylight
        # Depth is measured FROM the lit wall, so the rule has to account for how the room is lit:
        # a room with glass on two opposite walls is lit from both ends and only half as deep as it
        # measures, and a cross-lit room tolerates roughly half again the depth of a single-sided one.
        dm = rt["daylight"]["depth_multiplier"]
        wh = r.get("window_head_ft")
        walls = {win.get("wall") for win in r.get("windows", []) if win.get("wall")}
        OPP = {"N": "S", "S": "N", "E": "W", "W": "E", "NE": "SW", "SW": "NE", "NW": "SE", "SE": "NW"}
        two_ended = any(OPP.get(w) in walls for w in walls)
        effective_depth = (l / 2.0) if (two_ended and l) else l
        reach = dm * wh * (1.5 if len(walls) >= 2 and not two_ended else 1.0) if wh else None
        if wh and effective_depth and dm < 10 and reach and effective_depth > reach * 1.05:
            how = ("lit from both ends, so measured at half its length" if two_ended
                   else "cross-lit, so the reach is relaxed by half" if len(walls) >= 2
                   else "lit from one side")
            F.add("serious", "daylight",
                  f"{label} is {effective_depth:.0f} ft deep against a {wh} ft window head ({how}); useful daylight reaches about {reach:.1f} ft.",
                  room=rid, fix="Raise the head, light the far end from another side, or accept the back of the room as a service zone.")
        want_sides = rt["daylight"].get("sides_lit") or 1
        lit_walls = {win.get("wall") for win in r.get("windows", []) if win.get("wall")}
        if r.get("windows") and len(lit_walls) < want_sides:
            F.add("minor", "daylight", f"{label} is lit from {len(lit_walls)} side(s); the room type wants {want_sides}.", room=rid)
        if not r.get("windows") and rt["function_class"] in ("public", "living", "dining", "sleeping", "work"):
            F.add("serious", "daylight", f"{label} has no windows.", room=rid)

        # ---- adjacency, honouring style exceptions
        for kind, key in (("must_adjoin", "must_adjoin"), ("should_adjoin", "should_adjoin")):
            for rule in rt["adjacency"].get(key, []):
                if excepted(rule, chain): continue
                direct = key == "must_adjoin" and rule.get("relation") == "direct-door"
                near = types_adjacent(rid) if direct else types_near(rid)
                if rule["room"] in near: continue
                # A named intermediary satisfies the rule. The butler's pantry is not a failure
                # to connect the kitchen to the dining room; it is the connection.
                if rule.get("via"):
                    ok = False
                    for mid in adj[rid]:
                        if rooms[mid]["type"] in rule["via"] and rule["room"] in types_adjacent(mid):
                            ok = True; break
                    if ok: continue
                sev = STRENGTH_SEV.get(rule.get("strength", "strong"), "serious")
                if key == "should_adjoin": sev = "minor" if sev == "fatal" else sev
                if rule["room"] not in types_present:
                    # Absence is a different claim from non-adjacency. A plan record that does not
                    # model closets is coarse, not wrong, and reporting that at the same severity as
                    # a genuine adjacency failure buries the findings that matter.
                    F.add("minor" if not strict else sev, "completeness",
                          f"{label} wants to adjoin a {rule['room'].replace('-', ' ')} and the plan models none.",
                          room=rid, rule=rule["why"],
                          fix="Either the plan is missing the room, or the record simply does not model it. Run with --strict to treat absence as a failure.")
                else:
                    F.add(sev, "adjacency",
                          f"{label} does not reach a {rule['room'].replace('-', ' ')}"
                          + (" through a direct door." if rule.get("relation") == "direct-door" else " directly or across a hall."),
                          room=rid, rule=rule["why"])
        for rule in rt["adjacency"].get("must_not_adjoin", []):
            if excepted(rule, chain): continue
            if rule["room"] not in types_adjacent(rid): continue
            relation = rule.get("relation", "")
            for other in adj[rid]:
                if rooms[other]["type"] != rule["room"]: continue
                if relation in ("acoustically-separated", "not-visible-from") and (
                        rel.get((rid, other)) == relation
                        or declared_rel.get((rid, other)) == relation):
                    continue
                pair = tuple(sorted((rid, other)))
                if pair in seen_pairs: continue          # a mutual prohibition is one finding, not two
                seen_pairs.add(pair)
                F.add(STRENGTH_SEV.get(rule.get("strength", "strong"), "serious"), "adjacency",
                      f"{label} adjoins {rooms[other].get('name') or rule['room'].replace('-', ' ')}, which it should not.",
                      room=rid, rule=rule["why"],
                      fix=f"Separate them, or record the relation as '{relation}' if the separation is real.")
        ef = rt["adjacency"].get("entered_from")
        if ef:
            froms = {rooms[x]["type"] for x in adj[rid] if rel.get((rid, x)) == "direct-door"}
            ext = any(d["to"] == "exterior" for d in r.get("doors", []))
            if ext: froms.add("exterior")
            bad = froms - set(ef)
            if bad and froms:
                F.add("minor", "adjacency",
                      f"{label} is entered from {', '.join(sorted(b.replace('-', ' ') for b in bad))}; the catalogue expects entry from {', '.join(ef[:4])}.",
                      room=rid)
        if rt["adjacency"].get("never_a_through_room") and len(adj[rid]) > 1:
            F.add("minor", "circulation", f"{label} has {len(adj[rid])} connections and the room type should not be a through room.", room=rid)

        # ---- servicing
        if rt["servicing"].get("plumbing") in ("light", "heavy") and not r.get("fixtures"):
            F.add("info", "servicing", f"{label} is a plumbed room type with no fixtures listed.", room=rid)

    # ---- privacy gradient
    for rid, r in rooms.items():
        rt = C["rooms"].get(r["type"])
        if not rt: continue
        for other in adj[rid]:
            ot = C["rooms"].get(rooms[other]["type"])
            if not ot or rel.get((rid, other)) != "direct-door": continue
            # Circulation is RANK-TRANSPARENT. A corridor at rank 1 opening onto bedrooms at
            # rank 4 is what a corridor is for — it IS the buffer. Flagging it inverts the rule.
            if rt["function_class"] in ("circulation", "threshold") or ot["function_class"] in ("circulation", "threshold"):
                continue
            gap = ot["privacy_rank"] - rt["privacy_rank"]
            if gap >= 3:
                F.add("serious", "privacy",
                      f"A door runs straight from {r.get('name') or rt['name']} (rank {rt['privacy_rank']}) to "
                      f"{rooms[other].get('name') or ot['name']} (rank {ot['privacy_rank']}), jumping {gap} ranks.",
                      room=rid, rule="The public-to-private gradient: 0 street, 1 threshold, 2 public, 3 family, 4 private, 5 intimate.",
                      fix="Insert a buffer — a hall, a vestibule, a closet wall. A plan that scrambles the gradient feels wrong however well it is detailed.")

    # ---- wet-room stacking
    wet = [rid for rid, r in rooms.items()
           if set(r.get("fixtures") or []) & {"wc", "lavatory", "tub", "shower", "sink", "washer", "dishwasher"}]
    for rid in wet:
        r = rooms[rid]
        near = any(x in wet for x in adj[rid]) or (r.get("stacks_over") in wet)
        if not near and len(wet) > 1:
            F.add("minor", "servicing",
                  f"{r.get('name') or rid} is a wet room with no other wet room adjacent or below it.",
                  room=rid, fix="Stack or pair wet rooms. An isolated bath on the far side of a plan is the most expensive plumbing decision most clients make without knowing it.")

    # ============================================================ GROUPING LAYER
    for gid in plan.get("groupings", []):
        g = C["groupings"].get(gid)
        if not g:
            F.add("serious", "grouping", f"Unknown grouping '{gid}'.", fix="Use an id from groupings/.")
            continue
        sv = next((v for v in g.get("style_variation", []) if v["style"] in chain), None)
        if sv and sv.get("present") is False:
            F.add("serious", "grouping", f"The plan declares {g['name']}, which {style} does not have: {sv['note']}", rule=gid)
        for want in g["rooms"]:
            if want["role"] in ("primary",) and want["room"] not in types_present:
                F.add("serious", "grouping",
                      f"{g['name']} requires a {want['room'].replace('-', ' ')} and the plan has none.", rule=gid)
        if plan.get("massing"):
            att = next((a for a in g["attaches_to"] if a["massing"] == plan["massing"]), None)
            if att and att.get("fit") == "forbidden":
                F.add("serious", "grouping",
                      f"{g['name']} is marked forbidden in a {plan['massing'].replace('-', ' ')}: {att.get('note','')}", rule=gid)
            elif not att:
                F.add("info", "grouping", f"{g['name']} has no recorded fit for massing '{plan['massing']}'.", rule=gid)
        span = g.get("privacy_span")
        if span:
            ranks = [C["rooms"][rooms[x]["type"]]["privacy_rank"] for x in rooms
                     if rooms[x]["type"] in {y["room"] for y in g["rooms"]} and rooms[x]["type"] in C["rooms"]]
            if ranks and (min(ranks) < span[0] or max(ranks) > span[1]):
                F.add("minor", "grouping",
                      f"{g['name']} spans privacy ranks {min(ranks)}-{max(ranks)}; the grouping is defined for {span[0]}-{span[1]}.", rule=gid)
        for ir in g["internal_rules"]:
            if ir.get("severity") == "hard" and not ir.get("test"):
                F.add("info", "grouping", f"[{g['name']}] check by hand: {ir['statement']}", rule=gid)

    # ============================================================ CODE LAYER (advisory)
    juris = (plan.get("context") or {}).get("jurisdiction")
    for rid, r in rooms.items():
        rt = C["rooms"].get(r["type"])
        if not rt: continue
        w, l = r.get("width_ft"), r.get("length_ft")
        label = r.get("name") or rt["name"]
        habitable = rt["function_class"] in ("public", "living", "dining", "sleeping", "work")
        if habitable and w and l:
            if w * l < 70: F.add("advisory", "code", f"{label} is {w*l:.0f} sf; IRC R304.1 wants 70 sf for a habitable room.", room=rid, rule="IRC R304.1")
            if min(w, l) < 7: F.add("advisory", "code", f"{label} is {min(w,l)} ft in one dimension; IRC R304.2 wants 7 ft.", room=rid, rule="IRC R304.2")
        ch = r.get("ceiling_ft")
        if habitable and ch and ch < 7:
            F.add("advisory", "code", f"{label} ceiling {ch} ft; IRC R305.1 wants 7 ft.", room=rid, rule="IRC R305.1")
        if rt["function_class"] == "sleeping":
            if not any(win.get("egress") for win in r.get("windows", [])) and not any(d["to"] == "exterior" for d in r.get("doors", [])):
                F.add("advisory", "code", f"{label} has no emergency escape opening. IRC R310.1 requires one in every sleeping room.",
                      room=rid, rule="IRC R310.1", fix="A fixed or high transom window does not count.")
        if r["type"] == "garage":
            for other in adj[rid]:
                ot = C["rooms"].get(rooms[other]["type"])
                if ot and ot["function_class"] == "sleeping":
                    F.add("serious", "code", f"{label} adjoins a sleeping room. IRC R302.5.1 forbids a garage opening into a sleeping room and requires rated separation.",
                          room=rid, rule="IRC R302.5.1")
    if any(f["layer"] == "code" for f in F.items):
        F.add("info", "code", f"Code findings are ADVISORY and jurisdictional{' (' + juris + ' declared)' if juris else ''}. "
                              "They are the IRC model text, routinely amended locally, and must never be treated as a permit review.")

    # ============================================================ STYLE LAYER
    st = C["styles"].get(style)
    constraint_summary = {"present": 0, "clear": 0, "unjudged": 0}
    if st:
        kit = C["kits"].get(style, {}).get("slots", {})
        for slot_id, choice in (plan.get("declared") or {}).items():
            if slot_id not in C["slots"]:
                F.add("minor", "style", f"Declared slot '{slot_id}' is not in the ontology.", rule=slot_id); continue
            rec = kit.get(slot_id) or {}
            if rec.get("binding") == "forbidden":
                F.add("serious", "style", f"{style} forbids the slot '{slot_id}' outright, and the plan declares '{choice}'.", rule=slot_id)
            for v in rec.get("variants", []):
                if v.get("id") == choice and v.get("status") == "forbidden":
                    F.add("serious", "style", f"'{choice}' is a forbidden variant of {C['slots'][slot_id]['name'].lower()} in {style}.",
                          rule=slot_id, fix=v.get("note"))
        cvars = derive_constraint_vars(plan)
        # plan.measurements takes precedence over a derived value, mirroring the fault layer's
        # own practice a few dozen lines below: a number the plan record actually states beats
        # an inference from room geometry.
        c_namespace = {**cvars, **dict(plan.get("measurements") or {})}
        for c in st.get("constraints", []):
            if c.get("deprecated_in_favour_of"):
                continue
            test = c.get("test")
            if not test:
                # No formalised test -- either scope: judgment (schema/constraint.schema.json
                # forbids a test there), or this constraint just hasn't been migrated yet
                # (WP-1.1 migrated 140 of ~660). Unchanged from pre-WP-1.2 behaviour: only a
                # hard constraint gets a check-by-hand note, so the ~520 still-prose constraints
                # produce exactly the findings they always did.
                if c.get("severity") == "hard":
                    # rule is the constraint's own id when it has one (every migrated constraint
                    # does); falls back to style.kind for the pre-migration shape some styles'
                    # constraints may still be in, where no stable per-constraint id exists yet.
                    F.add("info", "style", f"Check by hand: {c['statement']}", rule=c.get("id") or f"{style}.{c['kind']}")
                continue
            r = core._eval_test(test, c_namespace)
            if not r or r["status"] != "evaluated":
                constraint_summary["unjudged"] += 1
                missing = r.get("missing") if r else None
                F.add("info", "style",
                      f"Cannot evaluate {c['id']} ({c['kind']}): {c['statement']}"
                      + (f" [needs {', '.join(missing)}]" if missing else ""),
                      rule=c["id"])
                continue
            if r["passes"]:
                constraint_summary["clear"] += 1
            else:
                constraint_summary["present"] += 1
                sev = CONSTRAINT_SEV.get(c.get("severity", "hard"), "serious")
                units = f" {r['units']}" if r.get("units") else ""
                F.add(sev, "style",
                      f"{c['statement']} (measured {r['value']}{units}, required {r['required']}{units}).",
                      rule=c["id"], fix=test.get("note"))
        if plan.get("massing"):
            aff = next((m for m in st.get("massing_affinities", []) if m["massing"] == plan["massing"]), None)
            if aff and aff["affinity"] == "forbidden":
                F.add("serious", "style", f"{st['name']} marks the {plan['massing'].replace('-', ' ')} massing forbidden: {aff.get('note','')}", rule="massing")
            elif not aff:
                F.add("minor", "style", f"{st['name']} records no affinity for the massing '{plan['massing']}'.", rule="massing")

    # ============================================================ FAULT LAYER
    meas = dict(plan.get("measurements") or {})
    for rid, r in rooms.items():                                  # derive what the plan can supply
        w, l = r.get("width_ft"), r.get("length_ft")
        if w and l:
            meas.setdefault(f"{rid}_width_ft", min(w, l)); meas.setdefault(f"{rid}_length_ft", max(w, l))
    if rooms:
        first = next(iter(rooms.values()))
        if first.get("ceiling_ft"): meas.setdefault("ceiling_height_in", first["ceiling_ft"] * 12)
    # ELEVATION LAYER (WP-3.2): build/elevation.py's own measurements dict is folded in here,
    # under the SAME setdefault precedence as everything else above -- a plan's own declared
    # measurements always win over what the generator derived. Wrapped: a plan that structure.py
    # or geometry.py cannot solve (an incomplete draft, say) should not take the whole validator
    # down with it; it just gets no elevation-derived measurements, same as "unjudged is not
    # passed" everywhere else in this corpus.
    try:
        EL = _load("elevation", f"{ROOT}/build/elevation.py")
        elev = EL.build_elevation(plan)
        if "error" not in elev:
            for k, v in elev.get("measurements", {}).items():
                meas.setdefault(k, v)
    except Exception:
        pass
    # limit lifted from the API default of 40: faults_present was never truncated, and the
    # could_not_judge list (surfaced as fault_unjudged below) has to be the whole list or
    # "unjudged is not passed" degrades into "the first forty unjudged are not passed".
    fr = core.check_measurements(meas, style=style, limit=10**6) if meas else {"faults_present": [], "summary": {"present": 0, "clear": 0, "unjudged": 0}}
    for x in fr.get("faults_present", []):
        F.add(x["severity"] if x["severity"] in SEV_ORDER else "serious", "fault",
              f"{x['name']}: {x['results'][0].get('value')} against {x['results'][0].get('required')}.",
              rule=x["fault"], fix=x.get("fix_cheap"))

    counts = {}
    for f in F.items: counts[f["severity"]] = counts.get(f["severity"], 0) + 1
    return {"plan": plan["id"], "style": style, "rooms": len(rooms),
            "counts": counts, "fault_summary": fr.get("summary"), "constraint_summary": constraint_summary,
            # The could-not-judge detail, not just its count. fault_summary already counts
            # unjudged; without the list itself a caller cannot say WHICH faults were
            # beyond evaluation, and unjudged-is-not-passed needs the which. Additive.
            "fault_unjudged": fr.get("could_not_judge", []),
            "findings": F.sorted(),
            "note": ("Style exceptions are honoured throughout — a rule a style legitimately breaks is not reported. "
                     "Code findings are advisory. Anything the fault corpus could not judge is unknown, not passed.")}

# ---------------------------------------------------------------- cli
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan"); ap.add_argument("--json", action="store_true")
    ap.add_argument("--layer"); ap.add_argument("--min-severity", default="info")
    ap.add_argument("--strict", action="store_true", help="treat an absent room type as a failure, not a gap in the record")
    a = ap.parse_args()
    plan = json.load(open(a.plan))
    import jsonschema
    jsonschema.validate(plan, json.load(open(f"{ROOT}/schema/plan.schema.json")))
    res = check(plan, strict=a.strict)
    if a.json: print(json.dumps(res, indent=1, ensure_ascii=False)); return
    cut = SEV_ORDER.index(a.min_severity)
    print(f"\n  {plan['name']}   [{res['style']}]   {res['rooms']} rooms")
    print("  " + "  ".join(f"{k} {v}" for k, v in sorted(res["counts"].items(), key=lambda kv: SEV_ORDER.index(kv[0]))))
    last = None
    for f in res["findings"]:
        if SEV_ORDER.index(f["severity"]) > cut: continue
        if a.layer and f["layer"] != a.layer: continue
        if f["layer"] != last: print(f"\n  {f['layer'].upper()}"); last = f["layer"]
        print(f"    [{f['severity']:<8}] {f['statement']}")
        if f.get("rule"): print(f"               why: {f['rule'][:150]}")
        if f.get("fix"): print(f"               fix: {f['fix'][:150]}")
    print()

if __name__ == "__main__":
    main()
