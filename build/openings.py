#!/usr/bin/env python3
"""openings.py — put every opening, the stair and the wet-room fixtures SOMEWHERE (WP-6.2).

Until this module a door was an unordered graph edge with an optional width. It had no
wall, no position, no hand: `{"to": "kitchen"}` and nothing else. So each renderer invented
a position — the midpoint of whatever shared wall the solver happened to leave — and each
invented it slightly differently, and a door the placement gave no wall was dropped in
silence by both. The record could not say where a door was, so nothing could check where a
door was, and every question a reader asks of a plan ("can I get to the kitchen?", "why is
the front door under a window?") was unanswerable from the data.

This runs AFTER placement, from build/geometry.py::solve, so both engines and every
consumer get the same answer. What it cannot place it marks `unplaced` with a reason —
never deletes. That is the same discipline the checkers keep: unjudged is not passed, and
an opening nobody could place must not read as an opening nobody declared.

  python3 build/openings.py plans/<id>.json      # place and print what it did
"""
from __future__ import annotations

import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _mod(name, path):
    # build/modcache.py, never a local loader (OQ 28; tests/test_modcache.py counts loads)
    b = os.path.join(ROOT, "build")
    if b not in sys.path:
        sys.path.insert(0, b)
    import modcache as _mc
    return _mc.load(name, path)


# The jamb allowance and the solid between openings are ONE number each, shared with the
# renderers (build/render_plan.py) and with the CP engine's door floor (WP-6.3), so the
# drawing, the proof and this pass can never again disagree about what fits (OQ 41/63).
JAMB_FT = 0.35
MIN_SOLID_FT = 1.0


def required_wall_ft(width_ft):
    return width_ft + 2 * JAMB_FT


_GRAMMAR = None


def grammar():
    global _GRAMMAR
    if _GRAMMAR is None:
        with open(os.path.join(ROOT, "openings", "grammar.json"), "r", encoding="utf-8") as fh:
            _GRAMMAR = json.load(fh)
    return _GRAMMAR


def placement_rule(rid):
    for p in (grammar().get("placement_rules") or []):
        if p["id"] == rid:
            return p
    return {}


# --------------------------------------------------------------------- geometry helpers
def _rect(r):
    g = r.get("geometry")
    if not g:
        return None
    return (g["x_ft"], g["y_ft"], g["width_ft"], g["depth_ft"])


def _shared(a, b, tol=0.4):
    """(wall_of_a, at, lo, hi) where two placed rooms touch, or None."""
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    if abs((ax + aw) - bx) <= tol:
        lo, hi = max(ay, by), min(ay + ah, by + bh)
        if hi > lo:
            return ("E", ax + aw, lo, hi)
    if abs((bx + bw) - ax) <= tol:
        lo, hi = max(ay, by), min(ay + ah, by + bh)
        if hi > lo:
            return ("W", ax, lo, hi)
    if abs((ay + ah) - by) <= tol:
        lo, hi = max(ax, bx), min(ax + aw, bx + bw)
        if hi > lo:
            return ("N", ay + ah, lo, hi)
    if abs((by + bh) - ay) <= tol:
        lo, hi = max(ax, bx), min(ax + aw, bx + bw)
        if hi > lo:
            return ("S", ay, lo, hi)
    return None


_OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}


def _boundary_walls(rect, W, H, tol=0.6):
    """Which of a room's own walls lie on the footprint boundary, with their runs."""
    x, y, w, h = rect
    out = {}
    if y <= tol:
        out["S"] = (x, x + w)
    if y + h >= H - tol:
        out["N"] = (x, x + w)
    if x <= tol:
        out["W"] = (y, y + h)
    if x + w >= W - tol:
        out["E"] = (y, y + h)
    return out


def _free(lo, hi, blocked):
    free = [(lo, hi)]
    for a, b in blocked:
        nxt = []
        for s, e in free:
            if b <= s or a >= e:
                nxt.append((s, e))
                continue
            if a > s:
                nxt.append((s, min(a, e)))
            if b < e:
                nxt.append((max(b, s), e))
        free = nxt
    return [(s, e) for s, e in free if e - s > 1e-6]


def _seat(free, width, prefer):
    """A centreline for an opening of `width` inside the free run, as near `prefer` as the
    masonry allows. Returns None when nothing will hold it."""
    best = None
    for s, e in free:
        lo, hi = s + width / 2, e - width / 2
        if hi < lo - 1e-9:
            continue
        p = min(hi, max(lo, prefer))
        d = abs(p - prefer)
        if best is None or d < best[1]:
            best = (p, d)
    return None if best is None else best[0]


# --------------------------------------------------------------------- the door pass
def _door_pairs(level_rooms):
    """Each declared interior door once, with both of its records so both can be written."""
    idx = {r["id"]: r for r in level_rooms}
    seen, out = set(), []
    for r in level_rooms:
        for d in (r.get("doors") or []):
            to = d["to"]
            if to == "exterior":
                continue
            key = tuple(sorted((r["id"], to)))
            if key in seen:
                continue
            seen.add(key)
            # a door to a room that is not on this level is still a DECLARED door, and it
            # leaves here marked rather than skipped: skipping it left the record carrying
            # a door that was neither placed nor refused, which is the silent third state
            # this whole module exists to abolish
            if to not in idx:
                out.append((r, d, None, None))
                continue
            other = next((x for x in (idx[to].get("doors") or []) if x["to"] == r["id"]), None)
            out.append((r, d, idx[to], other))
    return out


def _place_interior(level_rooms, occupied, report):
    for a, da, b, db in _door_pairs(level_rooms):
        width = da.get("width_ft") or (db and db.get("width_ft")) or 3.0
        if b is None:
            note = {"reason": f"no room '{da['to']}' on this level for this door to reach"}
            da["unplaced"] = note
            report["unplaced"].append({"pair": [a["id"], da["to"]], **note})
            continue
        ra, rb = _rect(a), _rect(b)
        if not ra or not rb:
            note = {"reason": "one of the two rooms is not placed on this level"}
            da["unplaced"] = note
            if db:
                db["unplaced"] = note
            report["unplaced"].append({"pair": [a["id"], b["id"]], **note})
            continue
        seg = _shared(ra, rb)
        if not seg:
            note = {"reason": "the placement leaves these two rooms no shared wall"}
            da["unplaced"] = note
            if db:
                db["unplaced"] = note
            report["unplaced"].append({"pair": [a["id"], b["id"]], **note})
            continue
        wall_a, at, lo, hi = seg
        need = required_wall_ft(width)
        if hi - lo < need:
            note = {"reason": f"they share {hi - lo:.1f} ft; this leaf and its jambs need {need:.1f} ft"}
            da["unplaced"] = note
            if db:
                db["unplaced"] = note
            report["unplaced"].append({"pair": [a["id"], b["id"]], **note})
            continue

        # op-corner-clearance: a leaf must have room to swing off the corner it hangs by
        blocked = occupied.get((a["id"], wall_a), []) + \
            occupied.get((b["id"], _OPPOSITE[wall_a]), [])
        free = _free(lo, hi, blocked)
        pos = _seat(free, width, (lo + hi) / 2)
        if pos is None:
            note = {"reason": "the shared wall is taken by other openings"}
            da["unplaced"] = note
            if db:
                db["unplaced"] = note
            report["unplaced"].append({"pair": [a["id"], b["id"]], **note})
            continue

        # op-doors-must-not-align — rooms/butlers-pantry.json calls this "the rule the room
        # exists for", and it has sat in a prose field with nothing able to act on it since
        # the record was written. A room whose doors face each other on one axis is a room
        # whose whole purpose (a visual lock between kitchen and dining room) has failed.
        off_rule = placement_rule("op-doors-must-not-align")
        min_off = off_rule.get("min_offset_ft", 2.67)
        for room, wall in ((a, wall_a), (b, _OPPOSITE[wall_a])):
            for other in occupied.get((room["id"], _OPPOSITE[wall]), []):
                mid = (other[0] + other[1]) / 2
                if abs(pos - mid) < min_off:
                    shifted = _seat(free, width, mid + min_off) or _seat(free, width, mid - min_off)
                    if shifted is not None and abs(shifted - mid) >= min_off - 1e-6:
                        pos = shifted
                        report["offset"].append({"pair": [a["id"], b["id"]],
                                                 "rule": "op-doors-must-not-align"})

        span = (pos - width / 2 - MIN_SOLID_FT, pos + width / 2 + MIN_SOLID_FT)
        occupied.setdefault((a["id"], wall_a), []).append(span)
        occupied.setdefault((b["id"], _OPPOSITE[wall_a]), []).append(span)

        da["wall"] = wall_a
        da["position_ft"] = round(pos, 3)
        da["swing_into"] = b["id"]
        da["hinge"] = "low"
        da.pop("unplaced", None)
        if db:
            db["wall"] = _OPPOSITE[wall_a]
            db["position_ft"] = round(pos, 3)
            db["swing_into"] = b["id"]
            db["hinge"] = "low"
            db.pop("unplaced", None)
        report["placed"] += 1


def _place_exterior(level_rooms, occupied, W, H, C, report):
    """Exterior doors, and the one rule that fixes the reported symptom.

    op-passage-axis. styles/tidewater-georgian.json c03 is HARD — "Centre passage 10-14 ft
    wide with exterior doors at both ends, aligned on axis and both operable. This is a
    ventilation device, not a hallway" — and groupings/centre-passage-core.json says the
    same. Neither could be satisfied or even checked, because a door had no wall: both
    renderers put every exterior door of a room on the FIRST wall it declared, so a passage
    running front to back had its rear door drawn on its front, under the front door, and
    its actual rear elevation showed a window where the door should be."""
    idx = {r["id"]: r for r in level_rooms}
    for r in level_rooms:
        rect = _rect(r)
        ext_doors = [d for d in (r.get("doors") or []) if d["to"] == "exterior"]
        if not ext_doors:
            continue
        if not rect:
            for d in ext_doors:
                d["unplaced"] = {"reason": "the room is not placed on this level"}
                report["unplaced"].append({"pair": [r["id"], "exterior"], **d["unplaced"]})
            continue
        bw = _boundary_walls(rect, W, H)
        declared = [w for w in (r.get("exterior_walls") or []) if w in bw] or list(bw)
        fc = (C["rooms"].get(r["type"], {}) or {}).get("function_class")

        # Which ends already reach the outside some other way — a door to a porch, a
        # piazza, a vestibule. A passage that is entered through a porch at its south end
        # has its own exterior door at the NORTH one; that is the axis, and it is read off
        # the plan rather than assumed.
        served = set()
        for d in (r.get("doors") or []):
            other = idx.get(d["to"])
            if not other:
                continue
            ofc = (C["rooms"].get(other["type"], {}) or {}).get("function_class")
            if ofc not in ("threshold", "outdoor"):
                continue
            seg = _shared(rect, _rect(other) or (0, 0, 0, 0)) if _rect(other) else None
            if seg:
                served.add(seg[0])
            # a porch on the south end serves the south end even where the shared wall
            # between the two runs east-west
            for w2, run in _boundary_walls(_rect(other), W, H).items() if _rect(other) else []:
                if w2 in bw:
                    served.add(w2)

        axis_pref = []
        if fc == "circulation":
            pairs = [w for w in declared if _OPPOSITE.get(w) in declared]
            axis_pref = [w for w in pairs if w not in served] or pairs
        order = axis_pref + [w for w in declared if w not in axis_pref]

        used = set()
        for d in ext_doors:
            width = d.get("width_ft") or 3.5
            seat = None
            for wall in order:
                if wall in used:
                    continue
                lo, hi = bw[wall]
                free = _free(lo, hi, occupied.get((r["id"], wall), []))
                # the passage axis wants the door on the room's own centreline
                prefer = (lo + hi) / 2
                pos = _seat(free, width, prefer)
                if pos is not None:
                    seat = (wall, pos)
                    break
            if seat is None:
                d["unplaced"] = {"reason": "no declared exterior wall of this room has a "
                                           "free run on the footprint boundary",
                                 **({"declared_wall": declared[0]} if declared else {})}
                report["unplaced"].append({"pair": [r["id"], "exterior"], **d["unplaced"]})
                continue
            wall, pos = seat
            used.add(wall)
            span = (pos - width / 2 - MIN_SOLID_FT, pos + width / 2 + MIN_SOLID_FT)
            occupied.setdefault((r["id"], wall), []).append(span)
            d["wall"] = wall
            d["position_ft"] = round(pos, 3)
            d["swing_into"] = r["id"]
            d["hinge"] = "low"
            d.pop("unplaced", None)
            report["placed"] += 1
            if fc == "circulation" and wall in axis_pref:
                report["axis"].append({"room": r["id"], "wall": wall,
                                       "rule": "op-passage-axis"})


def _place_windows(level_rooms, occupied, W, H, report):
    """Windows into the run the doors left, centred on the bay grid where a bay line falls
    inside the free space. build/geometry.py's own header says the bay module is what
    "joists span, windows centre on, the facade composes from" — and no renderer or pass
    had ever centred a window on one."""
    for r in level_rooms:
        rect = _rect(r)
        if not rect:
            for win in (r.get("windows") or []):
                win["unplaced"] = {"reason": "the room is not placed on this level"}
            continue
        bw = _boundary_walls(rect, W, H)
        for win in (r.get("windows") or []):
            wall = win.get("wall")
            n = win.get("count") or 1
            width = win.get("width_ft") or 3.0
            if wall not in bw:
                win["unplaced"] = {"reason": "the placement puts this room on no such "
                                             "boundary wall",
                                   **({"declared_wall": wall} if wall in ("N", "E", "S", "W") else {})}
                report["windows_unplaced"] += n
                continue
            lo, hi = bw[wall]
            placed = []
            for k in range(n):
                free = _free(lo, hi, occupied.get((r["id"], wall), []))
                prefer = lo + (hi - lo) * ((k + 1) / (n + 1))
                pos = _seat(free, width, prefer)
                if pos is None:
                    break
                placed.append(pos)
                occupied.setdefault((r["id"], wall), []).append(
                    (pos - width / 2 - MIN_SOLID_FT, pos + width / 2 + MIN_SOLID_FT))
            if not placed:
                win["unplaced"] = {"reason": "the wall has no clear run left beside its doors"}
                report["windows_unplaced"] += n
                continue
            if len(placed) < n:
                # the DECLARED count is left alone. Overwriting it with what was placed
                # would make the record lose the author's intent to a placement outcome —
                # the same silent overwrite this whole package exists to remove — and the
                # shortfall is already legible as count - len(positions_ft). Caught by the
                # DXF round trip, which asserts the rebuilt record equals the authored one.
                win["unplaced"] = {"reason": f"{n - len(placed)} of {n} unit(s) had no clear "
                                             f"run left on this wall"}
                report["windows_unplaced"] += n - len(placed)
            else:
                win.pop("unplaced", None)
            # every UNIT gets its own centreline. Storing one figure for the group and
            # letting each renderer re-derive the spacing is how the two renderers came out
            # 0.7 in apart on the first plan this was tried on -- a group of `count` windows
            # is `count` physical openings, each seated in whatever run the doors left.
            win["positions_ft"] = [round(p, 3) for p in placed]
            report["windows_placed"] += len(placed)


# --------------------------------------------------------------------- the stair
def stair_pass(plan, C, report):
    """The stair as an object. rooms/stair-hall.json's own critical_dimension carries the
    whole algorithm in prose and has been read by nothing:

      "A 9 ft finished ceiling with a 12 in floor assembly gives 10 ft 0 in floor to floor.
       At 7.5 in that is 16 risers and therefore 15 treads. At 10 in of run, a STRAIGHT
       flight is 150 in = 12 ft 6 in of horizontal run, plus a 36 in landing at each end...
       Fold it into a U with a half landing and the same sixteen risers become two flights
       of seven and eight treads: 80 in of run plus a 40 in landing = 10 ft 0 in of length
       by (36 + 36 + 6 in well) = 6 ft 6 in of width"

    build/structure.py::stair_geometry does the arithmetic already, but backwards — it
    reads the stair hall's SOLVED rectangle and reports whether the run fits. Here the run
    decides the form, and the flights land in the record so they can be drawn and so the
    landing above can be checked against them."""
    levels = {lv.get("index", 0): lv for lv in plan["levels"]}
    ground = levels.get(0)
    if not ground:
        return None
    room = next((r for r in ground["rooms"]
                 if (C["rooms"].get(r["type"], {}) or {}).get("id") == "stair-hall"
                 and r.get("geometry")), None)
    if not room:
        # a plan with no placed stair hall gets NO stair object, and that is a stated
        # absence rather than a stair of zero flights
        return None
    ch = ground.get("floor_to_ceiling_ft") or 9.0
    storey_in = (ch + 1.0) * 12.0                      # plus the floor assembly
    risers = max(2, math.ceil(storey_in / 7.25))       # storey-graduation.json's own rule
    riser_in = round(storey_in / risers, 3)
    tread_in = round(max(10.0, 24.0 - 2 * riser_in), 2)
    treads = risers - 1

    g = room["geometry"]
    rw, rd = g["width_ft"], g["depth_ft"]
    width_ft = min(3.5, max(3.0, min(rw, rd) / 2.2))   # kit: stair_width_in [36, 48]
    straight_run = treads * tread_in / 12.0
    landing = max(width_ft, 40.0 / 12.0)

    form, flights, well = None, [], None
    if max(rw, rd) >= straight_run + landing:
        form = "straight"
        along_x = rw >= rd
        run = straight_run
        well = {"x_ft": round(g["x_ft"], 3), "y_ft": round(g["y_ft"], 3),
                "width_ft": round(run if along_x else width_ft, 3),
                "depth_ft": round(width_ft if along_x else run, 3)}
        flights = [{**well, "treads": treads, "direction": "E" if along_x else "N"}]
    else:
        # the dog-leg: two flights and a half landing, which is what the record says a
        # 10 x 8 room is FOR
        t1 = treads // 2
        t2 = treads - t1
        run1 = t1 * tread_in / 12.0
        run2 = t2 * tread_in / 12.0
        pair_w = 2 * width_ft + 0.5                    # two flights and a 6 in well
        need = max(run1, run2) + landing
        along_x = rw >= rd
        long_ft, short_ft = (rw, rd) if along_x else (rd, rw)
        if long_ft + 1e-6 < need or short_ft + 1e-6 < pair_w:
            form = "dog-leg"
            well = {"x_ft": round(g["x_ft"], 3), "y_ft": round(g["y_ft"], 3),
                    "width_ft": round(rw, 3), "depth_ft": round(rd, 3)}
            # Would the room the RECORD declares have held it? If so the stair is not
            # missing because the house is too small; it is missing because the placement
            # shrank the room below its own stair, which is a different defect and belongs
            # to the solver rather than to the brief.
            dw, dl = room.get("width_ft"), room.get("length_ft")
            declared_fits = bool(dw and dl and max(dw, dl) + 1e-6 >= need
                                 and min(dw, dl) + 1e-6 >= pair_w)
            report["stair_note"] = (
                f"The stair hall is placed at {rw:.1f} x {rd:.1f} ft and a dog-leg with this "
                f"storey's {risers} risers needs {need:.1f} x {pair_w:.1f} ft. The well is "
                f"recorded as the whole room and the flights are NOT drawn: a flight drawn "
                f"where it does not fit would be a measurement nobody took."
                + (f" The room the record DECLARES — {dw} x {dl} ft — would have held it, so "
                   f"this is the placement shrinking a room below its own stair rather than "
                   f"a house too small to have one." if declared_fits else ""))
            return {"room": room["id"], "level": 0, "form": form, "risers": risers,
                    "riser_in": riser_in, "treads": treads, "tread_in": tread_in,
                    "width_ft": round(width_ft, 3), "run_ft": round(straight_run, 3),
                    "landing_depth_ft": round(landing, 3), "well": well,
                    "unplaced": {"reason": report["stair_note"]},
                    "note": "rooms/stair-hall.json's own critical_dimension is the source of "
                            "this arithmetic."}
        form = "dog-leg"
        if along_x:
            well = {"x_ft": round(g["x_ft"], 3), "y_ft": round(g["y_ft"], 3),
                    "width_ft": round(need, 3), "depth_ft": round(pair_w, 3)}
            flights = [
                {"x_ft": round(g["x_ft"], 3), "y_ft": round(g["y_ft"], 3),
                 "width_ft": round(run1, 3), "depth_ft": round(width_ft, 3),
                 "treads": t1, "direction": "E"},
                {"x_ft": round(g["x_ft"], 3), "y_ft": round(g["y_ft"] + width_ft + 0.5, 3),
                 "width_ft": round(run2, 3), "depth_ft": round(width_ft, 3),
                 "treads": t2, "direction": "W"},
            ]
        else:
            well = {"x_ft": round(g["x_ft"], 3), "y_ft": round(g["y_ft"], 3),
                    "width_ft": round(pair_w, 3), "depth_ft": round(need, 3)}
            flights = [
                {"x_ft": round(g["x_ft"], 3), "y_ft": round(g["y_ft"], 3),
                 "width_ft": round(width_ft, 3), "depth_ft": round(run1, 3),
                 "treads": t1, "direction": "N"},
                {"x_ft": round(g["x_ft"] + width_ft + 0.5, 3), "y_ft": round(g["y_ft"], 3),
                 "width_ft": round(width_ft, 3), "depth_ft": round(run2, 3),
                 "treads": t2, "direction": "S"},
            ]
    up = flights[0]["direction"] if flights else "N"
    return {"room": room["id"], "level": 0, "form": form, "risers": risers,
            "riser_in": riser_in, "treads": treads, "tread_in": tread_in,
            "width_ft": round(width_ft, 3), "run_ft": round(straight_run, 3),
            "landing_depth_ft": round(landing, 3), "up_direction": up,
            "well": well, "flights": flights,
            "note": "Derived from the storey height by storey-graduation's own riser rule; "
                    "the form is chosen by whether the run fits, per rooms/stair-hall.json's "
                    "critical_dimension."}


# --------------------------------------------------------------------- fixtures
# `fixtures` has always been a list of strings and the room catalogue has always carried
# each item's footprint_in and clearance_in. The two vocabularies never met, so a bathroom
# could be checked for whether it COULD hold a tub and never for whether the tub, the WC
# and the lavatory fit together along real walls.
_FIXTURE_ALIASES = {
    "tub": ("alcove bathtub", "bathtub", "freestanding tub", "tub"),
    "shower": ("shower", "shower with bench", "shower stall"),
    "wc": ("water closet", "wc", "water closet compartment"),
    "lavatory": ("lavatory", "vanity", "double vanity", "basin"),
    "sink": ("sink", "kitchen sink"),
    "dishwasher": ("dishwasher",),
    "washer": ("washer", "washing machine", "washer and dryer"),
    "range": ("range", "range, 30 in", "cooker"),
    "refrigerator": ("refrigerator", "fridge"),
}


def _furniture_for(room_type, fixture, C):
    """The room catalogue's own footprint for a named fixture, or None."""
    rt = C["rooms"].get(room_type) or {}
    names = _FIXTURE_ALIASES.get(fixture, (fixture,))
    for item in (rt.get("furniture") or []):
        label = (item.get("item") or "").lower()
        for n in names:
            if n in label:
                fp = item.get("footprint_in")
                if isinstance(fp, list) and len(fp) == 2:
                    return {"item": item["item"], "w_in": fp[0], "d_in": fp[1],
                            "clear_in": item.get("clearance_in") or 0}
    return None


def fixture_pass(level_rooms, C, report):
    """Wet rooms and the kitchen only (v1, by ruling). Fixtures are packed along the room's
    longest wall with their clearances respected; anything that will not fit is named."""
    for r in level_rooms:
        fixtures = r.get("fixtures") or []
        rect = _rect(r)
        if not fixtures or not rect:
            continue
        fc = (C["rooms"].get(r["type"], {}) or {}).get("function_class")
        if fc not in ("sanitary", "service"):
            continue
        x, y, w, d = rect
        along_x = w >= d
        run = w if along_x else d
        cursor = 0.0
        layout = []
        for f in fixtures:
            spec = _furniture_for(r["type"], f, C)
            if not spec:
                layout.append({"item": f, "unplaced": {
                    "reason": f"rooms/{r['type']}.json lists no furniture item for '{f}', so "
                              f"this corpus does not know how big it is"}})
                continue
            fw = spec["w_in"] / 12.0
            fd = spec["d_in"] / 12.0
            if cursor + fw > run + 1e-6:
                layout.append({"item": spec["item"], "width_ft": round(fw, 2),
                               "depth_ft": round(fd, 2), "unplaced": {
                    "reason": f"the wall run is {run:.1f} ft and the fixtures before this one "
                              f"take {cursor:.1f} ft of it"}})
                continue
            layout.append({
                "item": spec["item"],
                "wall": ("S" if along_x else "W"),
                "x_ft": round(x + (cursor if along_x else 0.0), 3),
                "y_ft": round(y + (0.0 if along_x else cursor), 3),
                "width_ft": round(fw if along_x else fd, 2),
                "depth_ft": round(fd if along_x else fw, 2),
            })
            cursor += fw
        if layout:
            r["fixture_layout"] = layout
            report["fixtures_placed"] += sum(1 for f in layout if "unplaced" not in f)
            report["fixtures_unplaced"] += sum(1 for f in layout if "unplaced" in f)


# --------------------------------------------------------------------- entry point
def place(plan, C=None):
    """Place every opening, the stair and the wet-room fixtures, in that order.

    Fixtures FIRST within a level, because a door has to know what is against the wall it
    would swing into; then interior doors; then exterior doors, which is where the passage
    axis is decided; then windows, into whatever run the doors have left."""
    if C is None:
        PC = _mod("plan_check", os.path.join(ROOT, "build", "plan_check.py"))
        C = PC.load_corpus()
    fp = plan.get("footprint") or {}
    W = fp.get("width_ft")
    H = fp.get("depth_ft")
    report = {"placed": 0, "unplaced": [], "offset": [], "axis": [],
              "windows_placed": 0, "windows_unplaced": 0,
              "fixtures_placed": 0, "fixtures_unplaced": 0}
    if not W or not H:
        report["note"] = ("no footprint on this record — openings are placed against the "
                          "block the solver produced, and this plan has not been placed")
        plan["opening_report"] = report
        return plan
    for lv in plan["levels"]:
        rooms = [r for r in lv["rooms"]]
        occupied = {}
        fixture_pass(rooms, C, report)
        _place_interior(rooms, occupied, report)
        _place_exterior(rooms, occupied, W, H, C, report)
        _place_windows(rooms, occupied, W, H, report)
    stair = stair_pass(plan, C, report)
    if stair:
        plan["stair"] = stair
    plan["opening_report"] = report
    return plan


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    geometry = _mod("geometry", os.path.join(ROOT, "build", "geometry.py"))
    plan = json.load(open(sys.argv[1]))
    solved = geometry.solve(plan)
    rep = solved.get("opening_report", {})
    print(json.dumps({k: v for k, v in rep.items() if k != "unplaced"}, indent=2))
    for u in rep.get("unplaced", []):
        print(f"  unplaced {u['pair']}: {u['reason']}")
    if solved.get("stair"):
        s = solved["stair"]
        print(f"  stair: {s['form']}, {s['risers']} risers at {s['riser_in']} in, "
              f"{s['treads']} treads at {s['tread_in']} in, in {s['room']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
