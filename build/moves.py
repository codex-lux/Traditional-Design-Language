#!/usr/bin/env python3
"""moves.py — the corrective revisions a plan record may take (WP-9.2).

The registry is DATA: moves/registry.json says what each move answers, what corpus sentence it
executes (quoted, verified by build/check_moves.py), which declared fields it may touch, and
whether the record has to be re-placed afterwards. This file is the CODE: one `apply` function
per registered id, and `answering(finding, plan)` -- the one place that decides which moves
answer a finding, matching on the finding's STRUCTURED evidence (WP-9.1) and never its prose.

A move returns either a change -- {"changed": [{path, from, to}], "log": "<one line in the
composer's own voice>", "basis": ...} -- or a refusal with its reason. It edits the record it
is handed, in place, and touches nothing a placement wrote: build/revise.py strips the placement
and re-solves after any move whose registry entry says `re-place`.

    python3 build/moves.py                 # list the registry with each move's basis
"""
from __future__ import annotations

import copy
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(ROOT, "moves", "registry.json")


def _mod(name, path):
    b = os.path.join(ROOT, "build")
    if b not in sys.path:
        sys.path.insert(0, b)
    import modcache as _mc
    return _mc.load(name, path)


_REG = None


def registry():
    global _REG
    if _REG is None:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as fh:
            _REG = json.load(fh)
    return _REG


def move(mid):
    return next((m for m in registry()["moves"] if m["id"] == mid), None)


# ------------------------------------------------------------------ helpers
def _rooms(plan):
    for lv in plan.get("levels", []):
        for r in lv.get("rooms", []):
            yield lv, r


def _room(plan, rid):
    for _lv, r in _rooms(plan):
        if r["id"] == rid:
            return r
    return None


def _level_of(plan, rid):
    for lv, r in _rooms(plan):
        if r["id"] == rid:
            return lv
    return None


def _name(r):
    return r.get("name") or r["id"]


def _band(C, rtype):
    rt = (C or {}).get("rooms", {}).get(rtype) or {}
    dims = rt.get("dimensions") or {}
    return dims.get("area_sf") or [40, 900], dims.get("width_ft"), dims.get("length_ft")


def _corpus(C):
    if C is not None:
        return C
    PC = _mod("plan_check", os.path.join(ROOT, "build", "plan_check.py"))
    return PC.load_corpus()


def _set_dims(r, w, l):
    """Width is the SHORT dimension by schema; keep it so."""
    w, l = round(min(w, l), 1), round(max(w, l), 1)
    ch = []
    if r.get("width_ft") != w:
        ch.append({"path": f"levels[].rooms[{r['id']}].width_ft", "from": r.get("width_ft"), "to": w})
        r["width_ft"] = w
    if r.get("length_ft") != l:
        ch.append({"path": f"levels[].rooms[{r['id']}].length_ft", "from": r.get("length_ft"), "to": l})
        r["length_ft"] = l
    return ch


def _required_number(required):
    """'at-least 7.0' -> 7.0 ; 'between 0.66 and 0.76' -> 0.66 ; 'at-most 1' -> 1"""
    try:
        return float(str(required).split()[1])
    except Exception:
        return None


# ------------------------------------------------------------------ the moves
def _widen_for_furniture(plan, f, C, ctx):
    r = _room(plan, f.get("room"))
    if not r or f.get("need_ft") is None or f.get("have_ft") is None:
        return {"refused": "the finding carries no need_ft/have_ft"}
    need, have = float(f["need_ft"]), float(f["have_ft"])
    if need <= have:
        return {"refused": "the room already has what the item needs"}
    lo_hi, _w, _l = _band(C, r["type"])
    target = round(need + 0.05, 1)
    w, l = r.get("width_ft") or 0, r.get("length_ft") or 0
    if f.get("axis") == "length":
        nw, nl = w, max(l, target)
    else:
        nw, nl = max(w, target), l
        if nw > nl:
            nl = nw
    if nw * nl > lo_hi[1] * 1.25:
        return {"refused": f"widening {_name(r)} to {target} ft for its {f.get('item')} would take it to "
                           f"{nw * nl:.0f} sf, past 1.25 x its {lo_hi[1]} sf band ceiling -- handed to the architect"}
    before = (w, l)
    ch = _set_dims(r, nw, nl)
    if not ch:
        return {"refused": "no dimension changed"}
    return {"changed": ch,
            "log": f"Widened {_name(r)} from {before[0] if f.get('axis') != 'length' else before[1]} to "
                   f"{target} ft so it takes its {f.get('item')}."}


def _widen_to_room_floor(plan, f, C, ctx):
    r = _room(plan, f.get("room"))
    if not r or f.get("need_ft") is None:
        return {"refused": "the finding carries no floor"}
    lo = float(f["need_ft"])
    w, l = r.get("width_ft") or 0, r.get("length_ft") or 0
    if w >= lo:
        return {"refused": "the room is already at its floor"}
    ch = _set_dims(r, lo, max(l, lo))
    return {"changed": ch, "log": f"Widened {_name(r)} to the {lo:g} ft floor for its room type."}


def _grow_to_band_floor(plan, f, C, ctx):
    r = _room(plan, f.get("room"))
    if not r or not f.get("need_sf") or not f.get("have_sf"):
        return {"refused": "the finding carries no band"}
    lo, have = float(f["need_sf"]), float(f["have_sf"])
    if have >= lo:
        return {"refused": "the room is already inside its band"}
    k = math.sqrt(lo / have) + 1e-3
    w, l = r.get("width_ft") or 0, r.get("length_ft") or 0
    ch = _set_dims(r, w * k, l * k)
    return {"changed": ch, "log": f"Grew {_name(r)} from {have:.0f} to {lo:.0f} sf, the floor of its catalogue band."}


def _raise_window_head(plan, f, C, ctx):
    r = _room(plan, f.get("room"))
    need, ceil = f.get("need_head_ft"), f.get("ceiling_ft")
    if not r or need is None or not ceil:
        return {"refused": "the finding does not say what head would reach the back of the room"}
    if need > ceil - 0.5:
        return {"refused": f"a {need} ft head would reach the back of {_name(r)}, above its {ceil} ft ceiling"}
    new = round(min(need + 0.05, ceil - 0.5), 1)
    old = r.get("window_head_ft")
    if old is not None and new <= old:
        return {"refused": "the head is already there"}
    r["window_head_ft"] = new
    return {"changed": [{"path": f"levels[].rooms[{r['id']}].window_head_ft", "from": old, "to": new}],
            "log": f"Raised the window head in {_name(r)} to {new} ft to reach the back of the room."}


_OPP = {"N": "S", "S": "N", "E": "W", "W": "E"}


def _light_the_far_end(plan, f, C, ctx):
    r = _room(plan, f.get("room"))
    if not r:
        return {"refused": "no such room"}
    need, ceil = f.get("need_head_ft"), f.get("ceiling_ft")
    if need is not None and ceil and need <= ceil - 0.5:
        return {"refused": "the head can reach; raise-window-head answers this first"}
    ext = set(r.get("exterior_walls") or [])
    lit = {w.get("wall") for w in (r.get("windows") or []) if w.get("wall")}
    for w in sorted(lit):
        opp = _OPP.get(w)
        if opp in ext and opp not in lit:
            unit = copy.deepcopy(next(x for x in r["windows"] if x.get("wall") == w))
            for k in ("position_ft", "positions_ft", "unplaced"):
                unit.pop(k, None)
            unit["wall"] = opp
            r["windows"].append(unit)
            return {"changed": [{"path": f"levels[].rooms[{r['id']}].windows[]", "from": None,
                                 "to": {"wall": opp, "count": unit.get("count"), "width_ft": unit.get("width_ft")}}],
                    "log": f"Lit {_name(r)} from its {opp} wall as well, so the far end is not dark."}
    return {"refused": f"{_name(r)} declares no exterior wall opposite a lit one"}


def _give_the_room_a_window(plan, f, C, ctx):
    r = _room(plan, f.get("room"))
    if not r:
        return {"refused": "no such room"}
    ext = list(r.get("exterior_walls") or [])
    if not ext:
        return {"refused": f"{_name(r)} declares no exterior wall to put a window in"}
    if r.get("windows"):
        return {"refused": "the room already declares a window"}
    lv = _level_of(plan, r["id"])
    ch = lv.get("floor_to_ceiling_ft") or r.get("ceiling_ft") or 9.0
    head = r.get("window_head_ft") or round(ch - 1.2, 1)
    r["window_head_ft"] = head
    # 3.2 ft is the composer's own placeholder, which derive_openings replaces with the pack's
    # figure for the room it lights; the count follows the room's own glazing fraction
    r["windows"] = [{"wall": ext[0], "width_ft": 3.2, "height_ft": round(head - 2.4, 1), "count": 1,
                     "operable": True}]
    _rederive_openings(plan, ctx)
    return {"changed": [{"path": f"levels[].rooms[{r['id']}].windows[]", "from": None,
                         "to": {"wall": ext[0], "count": r["windows"][0].get("count")}}],
            "log": f"Gave {_name(r)} a window on its {ext[0]} wall; it declared an exterior wall and no glass."}


def _grow_stair_hall(plan, f, C, ctx):
    r = _room(plan, f.get("room"))
    need = f.get("need_ft") or [None, None]
    if not r or not need[0] or not need[1]:
        return {"refused": "the refusal carries no run"}
    if f.get("declared_fits"):
        return {"refused": "the declared hall would have held the stair; this is the engine's"}
    w, l = r.get("width_ft") or 0, r.get("length_ft") or 0
    nw, nl = max(min(w, l), need[1] + 0.1), max(max(w, l), need[0] + 0.1)
    ch = _set_dims(r, nw, nl)
    if not ch:
        return {"refused": "the hall already has the run"}
    return {"changed": ch, "log": f"Grew {_name(r)} to {r['width_ft']} x {r['length_ft']} ft, the run its "
                                  f"{f.get('risers') or 'storey'}-riser dog-leg needs."}


def _widen_wet_room(plan, f, C, ctx):
    r = _room(plan, f.get("room"))
    need = f.get("need_ft") or [None, None]
    if not r or not need[0] or not need[1]:
        return {"refused": "the refusal carries no footprint"}
    w, l = min(r.get("width_ft") or 0, r.get("length_ft") or 0), max(r.get("width_ft") or 0, r.get("length_ft") or 0)
    nw, nl = w, l
    if l < need[0]:
        nl = need[0] + 0.1
    if w < need[1]:
        nw = need[1] + 0.1
    before = (w, l)
    ch = _set_dims(r, nw, nl)
    if not ch:
        return {"refused": "the declared room would hold the fixture; this is the engine's"}
    return {"changed": ch, "log": f"Widened {_name(r)} from {before[0]} to {r['width_ft']} ft so it takes its {f.get('item')}."}


def _passage_to_its_band(plan, f, C, ctx):
    r = _room(plan, f.get("room"))
    if not r:
        return {"refused": "no such room"}
    d = min(r.get("width_ft") or 0, r.get("length_ft") or 0)
    if d >= 6.0:
        return {"refused": "the passage is declared at its band; the engine drew it narrower"}
    ch = _set_dims(r, 6.0, max(r.get("length_ft") or 0, r.get("width_ft") or 0))
    return {"changed": ch, "log": f"Widened {_name(r)} from {d} to 6.0 ft, the passage that circulates."}


def _move_window_off_wall(plan, f, C, ctx):
    r = _room(plan, f.get("room"))
    if not r:
        return {"refused": "no such room"}
    ext = list(r.get("exterior_walls") or [])
    with_win = [w for w in (f.get("walls_with_windows") or []) if w in ext]
    declared = {w.get("wall") for w in (r.get("windows") or [])}
    free = [w for w in ext if w not in declared]
    if not with_win or not free:
        return {"refused": f"{_name(r)} has no other declared exterior wall to move a window to"}
    src, dst = with_win[0], free[0]
    win = next(x for x in r["windows"] if x.get("wall") == src)
    for k in ("position_ft", "positions_ft", "unplaced"):
        win.pop(k, None)
    win["wall"] = dst
    return {"changed": [{"path": f"levels[].rooms[{r['id']}].windows[].wall", "from": src, "to": dst}],
            "log": f"Moved {_name(r)}'s window from its {src} wall to its {dst} wall, to leave the run its {f.get('item')} needs."}


def _trade_width_for_depth(plan, f, C, ctx):
    C = _corpus(C)
    req = _required_number(f.get("required"))
    if not req:
        return {"refused": "the finding states no required depth"}
    cands = [r for _lv, r in _rooms(plan)
             if (C["rooms"].get(r["type"]) or {}).get("function_class") in ("threshold", "outdoor")
             and r.get("width_ft") and r.get("length_ft")]
    porch = next((r for r in cands if min(r["width_ft"], r["length_ft"]) + 1e-6 < req), None)
    if not porch:
        return {"refused": "no threshold or outdoor room is declared shallower than the rule wants"}
    w, l = min(porch["width_ft"], porch["length_ft"]), max(porch["width_ft"], porch["length_ft"])
    area = w * l
    nd = req
    nl = area / nd
    if nl < nd:
        return {"refused": f"{_name(porch)} has only {area:.0f} sf; at {req:g} ft deep it would be narrower than it is deep"}
    ch = _set_dims(porch, nd, nl)
    return {"changed": ch, "log": f"Deepened {_name(porch)} from {w} to {nd:g} ft at constant area, trading width for depth."}


def _replace_forbidden_variant(plan, f, C, ctx):
    slot, canonical = f.get("slot"), f.get("canonical")
    if not slot or not canonical:
        return {"refused": "no single canonical variant to take"}
    decl = plan.setdefault("declared", {})
    old = decl.get(slot)
    if isinstance(old, dict):
        decl[slot] = {**old, "variant": canonical}
    else:
        decl[slot] = canonical
    return {"changed": [{"path": f"declared.{slot}", "from": old, "to": decl[slot]}],
            "log": f"Set declared {slot} to {canonical}, the style's canonical, in place of the forbidden {f.get('variant')}."}


def _shutter_leaf_half(plan, f, C, ctx):
    m = plan.get("measurements") or {}
    if "shutter_leaf_width_in" not in m or "window_opening_width_in" not in m:
        return {"refused": "the plan does not declare both the leaf and the opening"}
    old, new = m["shutter_leaf_width_in"], round(m["window_opening_width_in"] * 0.5, 2)
    if old == new:
        return {"refused": "the leaf is already half the opening"}
    m["shutter_leaf_width_in"] = new
    return {"changed": [{"path": "measurements.shutter_leaf_width_in", "from": old, "to": new}],
            "log": f"Set the declared shutter leaf to {new} in, half the {m['window_opening_width_in']} in opening."}


def _delete_the_shutters(plan, f, C, ctx):
    PC = _mod("plan_check", os.path.join(ROOT, "build", "plan_check.py"))
    rec = (PC._resolved_slots(plan.get("style")) or {}).get("shutter") or {}
    none = next((v for v in rec.get("variants", []) if v.get("id") == "none"), None)
    if none and none.get("status") == "forbidden":
        return {"refused": "the style forbids `none` for the shutter slot"}
    decl = plan.setdefault("declared", {})
    old = decl.get("shutter")
    if old == "none":
        return {"refused": "shutters are already declared none"}
    decl["shutter"] = "none"
    ch = [{"path": "declared.shutter", "from": old, "to": "none"}]
    m = plan.get("measurements") or {}
    if "shutter_leaf_width_in" in m:
        ch.append({"path": "measurements.shutter_leaf_width_in", "from": m.pop("shutter_leaf_width_in"), "to": None})
    return {"changed": ch, "log": "Set declared shutter to none: no shutters is a legitimate historical condition, "
                                  "and half-width leaves are not."}


def _narrow_the_window(plan, f, C, ctx):
    m = plan.get("measurements") or {}
    req = _required_number(f.get("required"))
    if "window_opening_width_in" not in m or not req:
        return {"refused": "the plan does not declare the window width, or the rule states no ratio"}
    h = m.get("window_opening_height_in") or (f.get("value") and m["window_opening_width_in"] * f["value"])
    if not h:
        return {"refused": "no height to keep"}
    old = m["window_opening_width_in"]
    new = round(h / (req + 0.01), 1)
    if new >= old:
        return {"refused": "the declared window is already narrow enough"}
    m["window_opening_width_in"] = new
    ch = [{"path": "measurements.window_opening_width_in", "from": old, "to": new}]
    for _lv, r in _rooms(plan):
        for win in (r.get("windows") or []):
            if win.get("width_ft"):
                ch.append({"path": f"levels[].rooms[{r['id']}].windows[].width_ft", "from": win["width_ft"], "to": round(new / 12.0, 2)})
                win["width_ft"] = round(new / 12.0, 2)
    return {"changed": ch, "log": f"Narrowed the declared window to {new} in, keeping its {h:g} in height."}


def _reduce_dormer_count(plan, f, C, ctx):
    d = (plan.get("declared") or {}).get("dormer")
    if not isinstance(d, dict) or not isinstance(d.get("count"), int) or d["count"] < 2 or d["count"] % 2:
        return {"refused": "declared.dormer states no even count above zero"}
    old = d["count"]
    d["count"] = old - 1
    return {"changed": [{"path": "declared.dormer.count", "from": old, "to": old - 1}],
            "log": f"Reduced the declared dormer count from {old} to {old - 1}, to the rhythm of the bays."}


def _rederive_openings(plan, ctx):
    CO = _mod("compose", os.path.join(ROOT, "build", "compose.py"))
    CO.symmetrise_doors(plan)
    CO.derive_openings(plan, plan.get("style"), [])


def _must_not_adjoin(C, a_type, b_type):
    for x, y in ((a_type, b_type), (b_type, a_type)):
        rt = (C["rooms"].get(x) or {}).get("adjacency") or {}
        for rule in rt.get("must_not_adjoin") or []:
            if rule.get("room") == y:
                return True
    return False


def _add_the_grammar_door(plan, f, C, ctx):
    C = _corpus(C)
    r = _room(plan, f.get("room"))
    if not r:
        return {"refused": "no such room"}
    have = {d["to"] for d in (r.get("doors") or [])}
    cands = [oid for oid in (f.get("adjacent_placed") or []) if oid not in have]
    if not cands:
        return {"refused": f"no placed room shares a door's worth of wall with {_name(r)} that it is not already doored to"}
    def circ(oid):
        o = _room(plan, oid)
        return (C["rooms"].get(o["type"]) or {}).get("function_class") == "circulation" if o else False
    cands.sort(key=lambda oid: (not circ(oid), oid))
    for oid in cands:
        o = _room(plan, oid)
        if not o or _must_not_adjoin(C, r["type"], o["type"]):
            continue
        CO = _mod("compose", os.path.join(ROOT, "build", "compose.py"))
        rule = CO.opening_rule(r["type"], o["type"])
        r.setdefault("doors", []).append({"to": oid})
        _rederive_openings(plan, ctx)
        return {"changed": [{"path": f"levels[].rooms[{r['id']}].doors[]", "from": None, "to": {"to": oid}},
                            {"path": f"levels[].rooms[{oid}].doors[]", "from": None, "to": {"to": r['id']}}],
                "log": f"Added the door the grammar prescribes between {_name(r)} and {_name(o)} ({rule['id']}), "
                       f"so {_name(r)} can be reached.",
                "basis": rule.get("basis")}
    return {"refused": f"every placed neighbour of {_name(r)} is one its room type must not adjoin"}


def _drop_optional_room(plan, f, C, ctx):
    C = _corpus(C)
    parti = (ctx or {}).get("parti")
    r = _room(plan, f.get("room"))
    if not r:
        return {"refused": "no such room"}
    if not parti:
        return {"refused": "no diagram in hand to say which rooms are optional"}
    prow = next((x for x in parti.get("rooms", []) if x["id"] == r["id"] or r["id"].startswith(x["id"])), None)
    if not prow or prow.get("required") is not False:
        return {"refused": f"the diagram does not mark {_name(r)} optional"}
    must = set((ctx or {}).get("must_have") or [])
    if r["type"] in must:
        return {"refused": f"{_name(r)} is a must_have of the brief"}
    load_bearing = set()
    for _lv, x in _rooms(plan):
        for rule in ((C["rooms"].get(x["type"]) or {}).get("adjacency") or {}).get("must_adjoin") or []:
            if rule.get("strength", "strong") == "hard":
                load_bearing.add(rule["room"])
    if r["type"] in load_bearing:
        return {"refused": f"a hard adjacency rule needs a {r['type']}"}
    lv = _level_of(plan, r["id"])
    lv["rooms"] = [x for x in lv["rooms"] if x["id"] != r["id"]]
    for _l, x in _rooms(plan):
        if x.get("doors"):
            x["doors"] = [d for d in x["doors"] if d["to"] != r["id"]]
    plan["adjacencies"] = [a for a in plan.get("adjacencies", []) if r["id"] not in (a.get("a"), a.get("b"))]
    return {"changed": [{"path": "levels[].rooms[]", "from": r["id"], "to": None}],
            "log": f"Dropped {_name(r)}: the diagram marks it droppable and the placement could not reach it."}


def _split_per_grouping(plan, f, C, ctx):
    C = _corpus(C)
    r = _room(plan, f.get("room"))
    if not r:
        return {"refused": "no such room"}
    for gid in plan.get("groupings") or []:
        g = C["groupings"].get(gid) or {}
        logic = g.get("expansion_logic") or ""
        types = {x.get("type") or x.get("room") for x in (g.get("rooms") or [])} | set(g.get("required_rooms") or [])
        if logic.startswith("Split rather than enlarge") and r["type"] in types:
            w, l = min(r["width_ft"], r["length_ft"]), max(r["width_ft"], r["length_ft"])
            half = round(l / 2.0, 1)
            new = {"id": f"{r['id']}-2", "type": r["type"], "name": f"{_name(r)} 2", "width_ft": w, "length_ft": half,
                   "ceiling_ft": r.get("ceiling_ft"), "doors": [{"to": r["id"]}]}
            for k in ("window_head_ft", "exterior_walls"):
                if r.get(k) is not None:
                    new[k] = copy.deepcopy(r[k])
            if r.get("windows"):
                new["windows"] = [{k: v for k, v in win.items() if k not in ("position_ft", "positions_ft", "unplaced")}
                                  for win in r["windows"][:1]]
            r["length_ft"] = half
            _level_of(plan, r["id"])["rooms"].append(new)
            _rederive_openings(plan, ctx)
            return {"changed": [{"path": f"levels[].rooms[{r['id']}].length_ft", "from": l, "to": half},
                                {"path": "levels[].rooms[]", "from": None, "to": new["id"]}],
                    "log": f"Split {_name(r)} into two, as groupings/{gid}.json says to: two smaller rooms rather than one enlarged.",
                    "basis": f"groupings/{gid}.json expansion_logic: \"{logic[:120]}\""}
    return {"refused": "no grouping the plan names says to split this room type"}


def _search_harder(plan, f, C, ctx):
    cur = int((ctx or {}).get("candidates") or 250)
    nxt = 1000 if cur < 1000 else (2000 if cur < 2000 else None)
    if nxt is None:
        return {"refused": "the search is already at 2,000 candidates"}
    return {"lever": {"candidates": nxt}, "log": f"Searched harder: {cur} -> {nxt} candidates, for a placement the smaller pool did not hold."}


def _prove_it(plan, f, C, ctx):
    try:
        from ortools.sat.python import cp_model  # noqa: F401
    except Exception:
        return {"refused": "OR-Tools is not importable here; the proof cannot be asked for"}
    if (ctx or {}).get("engine") == "cp":
        return {"refused": "the proof was already asked for"}
    if (ctx or {}).get("engine") == "heuristic":
        # an EXPLICIT request for the search is a request not to spend a proof -- the bench's
        # drag path, check_all's bounded composer run -- and the lever honours it. Only `auto`
        # leaves the engine to the lever.
        return {"refused": "the search was asked for by name; the proof is not taken behind that request"}
    return {"lever": {"engine": "cp"}, "log": "Asked for the proof: CP-SAT holds the record's declared doors and sizes as hard facts."}


APPLY = {
    "widen-for-furniture": _widen_for_furniture,
    "widen-to-room-floor": _widen_to_room_floor,
    "grow-to-band-floor": _grow_to_band_floor,
    "raise-window-head": _raise_window_head,
    "light-the-far-end": _light_the_far_end,
    "give-the-room-a-window": _give_the_room_a_window,
    "grow-stair-hall-to-its-run": _grow_stair_hall,
    "widen-wet-room-for-fixture": _widen_wet_room,
    "passage-to-its-band": _passage_to_its_band,
    "move-window-off-the-needed-wall": _move_window_off_wall,
    "trade-width-for-depth-at-constant-area": _trade_width_for_depth,
    "replace-forbidden-declared-variant": _replace_forbidden_variant,
    "shutter-leaf-at-half-the-opening": _shutter_leaf_half,
    "delete-the-shutters": _delete_the_shutters,
    "narrow-the-window-and-keep-the-height": _narrow_the_window,
    "reduce-the-dormer-count-to-the-rhythm": _reduce_dormer_count,
    "add-the-grammar-door": _add_the_grammar_door,
    "drop-optional-room": _drop_optional_room,
    "split-per-grouping": _split_per_grouping,
    "search-harder": _search_harder,
    "prove-it": _prove_it,
}

# A move that only makes sense once another has been refused on the same finding, in order.
_AFTER = {"light-the-far-end": "raise-window-head", "delete-the-shutters": "shutter-leaf-at-half-the-opening",
          "drop-optional-room": "add-the-grammar-door"}

# `unreachable` and `cut-off` are one defect in two severities; the door moves answer both.
_KIND_ALIASES = {"cut-off": "unreachable"}


def _matches(ans, f):
    if "class" in ans:
        return False                       # levers are chosen by the loop from the critique class
    if ans.get("layer") and f.get("layer") != ans["layer"]:
        return False
    if ans.get("kind"):
        k = f.get("kind")
        if k != ans["kind"] and _KIND_ALIASES.get(k) != ans["kind"]:
            return False
    if ans.get("axis") and f.get("axis") != ans["axis"]:
        return False
    if ans.get("fault") and f.get("fault") != ans["fault"]:
        return False
    return True


def answering(finding, plan, C=None, ctx=None, check=True):
    """The registered moves that answer this finding, in registry order: those whose
    `answers` match the finding's STRUCTURED fields and -- with `check` on -- whose
    precondition holds, tried on a deep copy of the plan so nothing is written. A move in
    `_AFTER` is offered only once the move it follows has been refused on this finding. Each
    entry carries `would`, the log line it would write. This is the single place that decides
    what answers what; build/critique.py asks it and never re-derives it."""
    out, refused = [], {}
    for m in registry()["moves"]:
        if not _matches(m["answers"], finding):
            continue
        after = _AFTER.get(m["id"])
        if after and after not in refused:
            if not check:
                continue
            # the move it follows was not tried yet on this finding (it did not match, or it
            # applied): it is not offered
            continue
        if not check:
            out.append(m)
            continue
        trial = copy.deepcopy(plan)
        res = APPLY[m["id"]](trial, finding, C, ctx) if m["id"] in APPLY else {"refused": "no apply"}
        if "refused" in res:
            refused[m["id"]] = res["refused"]
            continue
        out.append({**m, "would": res.get("log"), "refused_before": dict(refused)})
    return out


def apply(move_id, plan, finding, C=None, ctx=None):
    """Apply one move to the plan IN PLACE. Returns the change record or a refusal."""
    m = move(move_id)
    if not m:
        return {"refused": f"no move '{move_id}' is registered"}
    fn = APPLY.get(move_id)
    if fn is None:
        return {"refused": f"'{move_id}' is registered and has no apply function"}
    res = fn(plan, finding, C, ctx)
    res.setdefault("move", move_id)
    res.setdefault("basis", m["basis"])
    res["requires"] = m["requires"]
    res["authority"] = m["authority"]
    res["kind"] = m["kind"]
    if m.get("tier"):
        res["tier"] = m["tier"]
    return res


def levers():
    return [m for m in registry()["moves"] if m["answers"].get("class") == "placement"]


if __name__ == "__main__":
    reg = registry()
    print(f"{len(reg['moves'])} moves, {len(reg['refusals'])} refusals. Authority ruled {reg['authority']['ruled']}.\n")
    for m in reg["moves"]:
        print(f"  {m['id']:<42} {m['kind']:<9} {m['requires']:<9} {m['authority']}")
        print(f"      answers {m['answers']}  touches {m['touches']}")
    print("\nRefused:")
    for r in reg["refusals"]:
        print(f"  {r['id']}: {r['why'][:110]}")
