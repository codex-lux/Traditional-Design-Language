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

_STOREYS = None


def _storeys():
    """build/storeys.py, loaded lazily and cached. NOT `structure.py`, which is where this
    derivation used to live: structure loads geometry, and geometry calls stair_pass, so
    importing it from here would close a cycle. storeys.py is a leaf for that reason."""
    global _STOREYS
    if _STOREYS is None:
        _STOREYS = _mod("storeys", os.path.join(ROOT, "build", "storeys.py"))
    return _STOREYS


def required_wall_ft(width_ft):
    return width_ft + 2 * JAMB_FT


# THE ONE LIST OF WHAT THIS PASS AND THE SOLVER WRITE ONTO A RECORD (WP-9.1). Two callers
# need to take a placement OFF a record and return it to the authored state: the DXF
# exporter, so the XDATA round-trip returns what the author wrote, and build/revise.py, so a
# revised declared record is re-placed from scratch rather than under a stale geometry.
# These four tuples lived in build/export_dxf.py alone until Phase 9; a second copy in the
# loop would have been the citation grammar's three spellings again. A window has always
# declared its own `wall` — that is an authored fact and is NOT here — while a door had no
# wall at all until 0.3.0, so on a door `wall` is placement output. That distinction cost
# one round-trip failure to find (WP-6.2) and is worth the two constants.
PLACEMENT_PLAN_KEYS = ("footprint", "geometry_report", "stair", "opening_report")
PLACEMENT_ROOM_KEYS = ("geometry", "fixture_layout")
PLACEMENT_DOOR_KEYS = ("wall", "position_ft", "positions_ft", "hinge", "swing_into", "unplaced")
PLACEMENT_WINDOW_KEYS = ("position_ft", "positions_ft", "unplaced")


def strip_placement(plan):
    """Remove every key a placement wrote, IN PLACE, and return the plan. The declared
    record that remains is what the author (or the composer, or the revision loop) stated;
    everything a solver or this pass derived from it is gone, `unplaced` marks included,
    because a mark that a PREVIOUS placement could not seat a door says nothing about the
    next one."""
    for k in PLACEMENT_PLAN_KEYS:
        plan.pop(k, None)
    for lv in plan.get("levels", []):
        for r in lv.get("rooms", []):
            for k in PLACEMENT_ROOM_KEYS:
                r.pop(k, None)
            for d in (r.get("doors") or []):
                for k in PLACEMENT_DOOR_KEYS:
                    d.pop(k, None)
            for w in (r.get("windows") or []):
                for k in PLACEMENT_WINDOW_KEYS:
                    w.pop(k, None)
    return plan


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


def envelopes(plan):
    """`{room_id: (x0, y0, x1, y1)}` -- the rectangle each room's OWN massing element occupies
    (WP-11.6, ruling 1: an element has its own envelope, not the union).

    Every layer below the placer was written when a house was one rectangle. This is the first
    of the six to be told otherwise, and it is first because of the order the ruling states: an
    element-aware `openings` makes a dependency's windows REAL, which turns `structure`'s missing
    envelope walls into a drawn collision instead of a silent absence. Fixing them in the other
    order would leave the shield in place.

    A plan with no `footprint.blocks` -- which is every plan in this corpus -- gets an empty map
    and every caller falls back to the main block, so the one-rectangle case is untouched by
    construction rather than by luck.

    THE JOIN IS THE ROOM'S OWN `block` TAG, NOT A ROOM LIST ON THE BLOCK. `blocks_record` writes
    id, role, x, y, width, depth and area and no membership, so a first version of this read
    `b["rooms"]`, found nothing on every plan, and left all nine refusals in place while
    reporting success. The tag is what the placer itself groups by (`blocks_for` reads
    `r["block"]`), so reading it here keeps one spelling of what an element contains.
    """
    fp = plan.get("footprint") or {}
    by_id = {b["id"]: (b["x_ft"], b["y_ft"], b["x_ft"] + b["width_ft"],
                       b["y_ft"] + b["depth_ft"]) for b in (fp.get("blocks") or [])}
    if len(by_id) < 2:
        return {}
    main = by_id.get("main")
    out = {}
    for lv in plan.get("levels", []):
        for r in lv.get("rooms", []):
            tag = r.get("block")
            env = by_id.get(tag) if tag else main
            # A hyphen room is tagged into the DEPENDENCY's id by the composer and placed in the
            # element `<id>-hyphen`; prefer the element it was actually placed in.
            if tag and f"{tag}-hyphen" in by_id and r.get("hyphen"):
                env = by_id[f"{tag}-hyphen"]
            if env:
                out[r["id"]] = env
    return out


def _boundary_walls(rect, W, H, tol=0.6, env=None):
    """Which of a room's own walls lie on ITS ELEMENT's boundary, with their runs.

    `env` is `(x0, y0, x1, y1)` for the element the room sits in; absent, it is the main block
    at the origin, which is what `W`/`H` have always meant and what every one-rectangle plan
    still gets. **A dependency room touches none of the main block's boundary** -- on the
    reference fixture at x -41..-14 against a 63 ft block, nine of fourteen declared openings
    came back `unplaced` with "the placement puts this room on no such boundary wall", which is
    a refusal produced by the instrument rather than by the house."""
    x, y, w, h = rect
    x0, y0, x1, y1 = env if env else (0.0, 0.0, W, H)
    out = {}
    if y <= y0 + tol:
        out["S"] = (x, x + w)
    if y + h >= y1 - tol:
        out["N"] = (x, x + w)
    if x <= x0 + tol:
        out["W"] = (y, y + h)
    if x + w >= x1 - tol:
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
            note = {"reason": "the placement leaves these two rooms no shared wall",
                    "needs": {"shared_wall_ft": round(required_wall_ft(width), 2)},
                    "have": {"shared_wall_ft": 0.0}}
            da["unplaced"] = note
            if db:
                db["unplaced"] = note
            report["unplaced"].append({"pair": [a["id"], b["id"]], **note})
            continue
        wall_a, at, lo, hi = seg
        need = required_wall_ft(width)
        if hi - lo < need:
            note = {"reason": f"they share {hi - lo:.1f} ft; this leaf and its jambs need {need:.1f} ft",
                    "needs": {"shared_wall_ft": round(need, 2)},
                    "have": {"shared_wall_ft": round(hi - lo, 2)}}
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
            note = {"reason": "the shared wall is taken by other openings",
                    "needs": {"free_run_ft": round(width + 2 * MIN_SOLID_FT, 2)},
                    "have": {"free_run_ft": round(max([b - a for a, b in free] or [0.0]), 2),
                             "shared_wall_ft": round(hi - lo, 2)}}
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


def _place_exterior(level_rooms, occupied, W, H, C, report, envs=None):
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
        bw = _boundary_walls(rect, W, H, env=(envs or {}).get(r["id"]))
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
            for w2, run in _boundary_walls(_rect(other), W, H,
                                           env=(envs or {}).get(other["id"])).items() \
                    if _rect(other) else []:
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
                                 **({"declared_wall": declared[0]} if declared else {}),
                                 "needs": {"free_run_ft": round(width + 2 * MIN_SOLID_FT, 2)},
                                 "have": {"walls_tried": list(order)}}
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


def _place_windows(level_rooms, occupied, W, H, report, envs=None):
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
        bw = _boundary_walls(rect, W, H, env=(envs or {}).get(r["id"]))
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
                win["unplaced"] = {"reason": "the wall has no clear run left beside its doors",
                                   "needs": {"free_run_ft": round(width + 2 * MIN_SOLID_FT, 2),
                                             "units": n},
                                   "have": {"units_placed": 0}}
                report["windows_unplaced"] += n
                continue
            if len(placed) < n:
                # the DECLARED count is left alone. Overwriting it with what was placed
                # would make the record lose the author's intent to a placement outcome —
                # the same silent overwrite this whole package exists to remove — and the
                # shortfall is already legible as count - len(positions_ft). Caught by the
                # DXF round trip, which asserts the rebuilt record equals the authored one.
                win["unplaced"] = {"reason": f"{n - len(placed)} of {n} unit(s) had no clear "
                                             f"run left on this wall",
                                   "needs": {"free_run_ft": round(width + 2 * MIN_SOLID_FT, 2),
                                             "units": n},
                                   "have": {"units_placed": len(placed)}}
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
    # WP-9.6: TWO INVENTED CONSTANTS REPLACED BY THE CORPUS'S OWN DERIVATION. This read
    #     ch = ground.get("floor_to_ceiling_ft") or 9.0
    #     storey_in = (ch + 1.0) * 12.0                # plus the floor assembly
    # -- a flat twelve inches of floor assembly, and a 9.0 ft ceiling for the case where the
    # record is silent. `build/storeys.py` inverts storey-graduation.json's own
    # ceiling_height_rule instead, which is what `structure.py` has always done: the deduction
    # is 15.35 in at an 11 ft ceiling and 11.86 in at 8.5 ft, and it is not a constant.
    # Measured on plans/tidewater-georgian-careful.json: 144.0 in became 147.3, and this pass
    # now agrees with the section that draws the same stair. (At the 7.25 in divisor that was
    # 21 risers each where the two had read 20 against 21; at the 7.5 in Lucas ruled on 2 Sep
    # it is 20 each. The AGREEMENT is what this change bought -- the count is the pack's.)
    storey_in = _storeys().ground_storey_in(plan)
    if storey_in is None:
        # The record states no ceiling anywhere on the ground level. The number that used to
        # stand here was 9.0 ft, invented -- the OQ 52 class exactly. A stated absence, not a
        # stair of assumed height.
        report.setdefault("refusals", []).append(
            "No stair: the ground level states no floor-to-ceiling height, on the level or on "
            "any of its rooms, so the storey it rises through is unjudged.")
        return None
    # READ from storey-graduation.json's stair_type rule, never transcribed: this was a bare
    # 7.25 here and another in structure.py, each commented "storey-graduation.json's own
    # rule", so moving the pack would have moved neither. Lucas ruled 7.5 on 2 Sep 2026 and
    # the pack is the only place that number now lives.
    risers = max(2, math.ceil(storey_in / _storeys().riser_divisor_in()))
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
                    "unplaced": {"reason": report["stair_note"],
                                 # the same figures the sentence carries, as fields, for a
                                 # move to read (WP-9.1); the prose stays the record
                                 "needs": {"long_ft": round(need, 2), "short_ft": round(pair_w, 2),
                                           "form": "dog-leg", "risers": risers,
                                           "declared_fits": declared_fits},
                                 "have": {"long_ft": round(long_ft, 2), "short_ft": round(short_ft, 2),
                                          "declared": [dw, dl]}},
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


def fixture_pass(level_rooms, C, report, occupied=None):
    """Wet rooms and the kitchen only (v1, by ruling). Fixtures are packed along the room's
    longest wall with their clearances respected; anything that will not fit is named.

    WP-7.2 — THIS RUNS AFTER THE OPENINGS AND THE DOOR WINS. `place()`'s docstring used to
    say fixtures ran first "because a door has to know what is against the wall it would
    swing into", and `occupied` never held a fixture, so the code did not implement the
    reason its own ordering stated: measured on the CP placements, the powder room's basin
    (1.92 ft) and the principal bath's double vanity (2.7 ft) were drawn with a door through
    them on `spec-builder-colonial`.

    The ordering was inverted rather than the map patched, because the precedence matters
    more than the sequence: a door is AUTHORED in the plan record and a fixture layout is
    DERIVED here, and an authored fact must never lose silently to an inferred one (OQ 52).
    So the openings take their runs first and a fixture that cannot clear them is reported
    `unplaced` with a reason, which is the same three-state treatment every opening gets."""
    occupied = occupied if occupied is not None else {}
    for r in level_rooms:
        fixtures = r.get("fixtures") or []
        rect = _rect(r)
        if not fixtures or not rect:
            continue
        fc = (C["rooms"].get(r["type"], {}) or {}).get("function_class")
        if fc not in ("sanitary", "service"):
            continue
        x, y, w, d = rect
        # WP-7.2: the wall with the longest CLEAR run, not simply the longest wall. Packing
        # against the longest wall regardless of what is already on it reported the powder
        # room's water closet and basin as unfittable because its 11 ft south wall was 9 ft
        # spoken for, while its east wall stood empty. A fixture refused on a wall nobody
        # tried is a false "cannot fit", and this corpus is built to distinguish
        # evaluated-and-failed from not-looked-at.
        cand = []
        for wall in ("S", "N", "W", "E"):
            along = wall in ("S", "N")
            wrun = w if along else d
            wbase = x if along else y
            wfree = sorted(_free(wbase, wbase + wrun, occupied.get((r["id"], wall), [])))
            longest = max((b - a for a, b in wfree), default=0.0)
            # ties break on the longer wall, then S/W, so an unobstructed room packs exactly
            # as it did before this change
            cand.append((-longest, -wrun, ("S", "N", "W", "E").index(wall), wall, along, wrun, wbase, wfree))
        cand.sort()
        # WP-7.4: THE RUN TURNS THE CORNER. WP-7.2 made this pick the wall with the longest
        # CLEAR run instead of simply the longest wall, because "a fixture refused on a wall
        # nobody tried is a false 'cannot fit'". It then packed every fixture onto that one
        # wall -- the same error one level up, and it surfaced the moment WP-7.4's score terms
        # moved a room: `spec-builder-colonial`'s primary bath is 9 x 18 ft, its four fixtures
        # want 22 ft, its longest clear run is 17.2 ft, and its other three walls stood empty.
        #
        # Each wall keeps its own cursor and a fixture tries the wall it is already on first,
        # so a room whose fixtures all fit on one wall packs BYTE-IDENTICALLY to before.
        #
        # A SEAT IS ACCEPTED ONLY IF THE RECTANGLE IT PRODUCES IS REALLY FREE. The first
        # version of this reserved the corner by starting a newly opened wall past the deepest
        # fixture placed anywhere in the room, and called that "conservative". It is not: every
        # wall packs from its LOW end, and the four low ends are four different corners, so the
        # reserve guards the SW corner and does nothing for NE, pushes W into N at NW and S into
        # E at SE. Measured over a sweep of 81 plausible primary-bathroom sizes, 60 came out
        # with a drawn fixture overlapping another or sitting outside the room. Nothing in the
        # corpus's own 16 plans showed it, which is exactly why it needed measuring rather than
        # reasoning about. The approximation is gone: a candidate seat is now turned into its
        # actual rectangle and rejected if it leaves the room or touches anything already
        # placed, which also covers the OPPOSITE-wall case (a 6 ft room cannot hold a 5.5 ft
        # fixture on W and a 5 ft one on E) that no corner rule could ever have caught.
        walls = {c[3]: {"along": c[4], "run": c[5], "base": c[6], "free": c[7],
                        "clear": -c[0], "cursor": 0.0} for c in cand}
        order = [c[3] for c in cand]
        wall = order[0]
        layout = []
        placed = []          # (x, y, w, d) of every fixture actually drawn in this room

        def _seat_rect(cw, seat, fw, fd):
            """The rectangle a seat on `cw` would occupy, or None if it leaves the room."""
            along = walls[cw]["along"]
            if along and fd > d + 1e-6: return None
            if not along and fd > w + 1e-6: return None
            off = (y if cw == "S" else y + d - fd) if along else (x if cw == "W" else x + w - fd)
            return ((seat, off, fw, fd) if along else (off, seat, fd, fw))

        def _clear_of_placed(rect):
            for q in placed:
                if (min(rect[0] + rect[2], q[0] + q[2]) - max(rect[0], q[0]) > 1e-6
                        and min(rect[1] + rect[3], q[1] + q[3]) - max(rect[1], q[1]) > 1e-6):
                    return False
            return True

        for f in fixtures:
            spec = _furniture_for(r["type"], f, C)
            if not spec:
                layout.append({"item": f, "unplaced": {
                    "reason": f"rooms/{r['type']}.json lists no furniture item for '{f}', so "
                              f"this corpus does not know how big it is"}})
                continue
            fw = spec["w_in"] / 12.0
            fd = spec["d_in"] / 12.0
            # the wall it is already on first, then every other wall in clear-run order; and
            # within a wall every free segment, not only the first that is wide enough
            seat = rect = None
            for cw in [wall] + [o for o in order if o != wall]:
                W_ = walls[cw]
                for lo, hi in W_["free"]:
                    start = max(lo, W_["base"] + W_["cursor"])
                    while hi - start >= fw - 1e-6:
                        cand_rect = _seat_rect(cw, start, fw, fd)
                        if cand_rect is not None and _clear_of_placed(cand_rect):
                            seat, rect, wall = start, cand_rect, cw
                            break
                        if cand_rect is None:
                            break        # too deep for this wall's room dimension: no seat fits
                        start += 0.5     # step along and try again past the obstruction
                    if seat is not None: break
                if seat is not None: break
            if seat is None:
                tried = ", ".join(f"{o} {walls[o]['clear']:.1f} ft clear of {walls[o]['run']:.1f}"
                                  for o in order)
                layout.append({"item": spec["item"], "width_ft": round(fw, 2),
                               "depth_ft": round(fd, 2), "unplaced": {
                    "reason": (f"no wall of this room has a clear run left for a {fw:.1f} x "
                               f"{fd:.1f} ft item that does not overlap what is already placed. "
                               f"All four were tried ({tried}); fixtures already placed take "
                               f"{walls[wall]['cursor']:.1f} ft of the {wall} wall"),
                    "needs": {"width_ft": round(fw, 2), "depth_ft": round(fd, 2)},
                    "have": {o: round(walls[o]["clear"], 2) for o in order}}})
                continue
            layout.append({
                "item": spec["item"],
                "wall": wall,
                # WP-7.4 audit: position and extent are rounded to the SAME precision. They
                # were 3dp and 2dp, so a fixture against the far wall came out at
                # 2.333 + 2.67 = 5.003 in a 5.00 ft room -- the "against the wall it names"
                # invariant held only to about 0.005 ft, and an outside-the-room check had to
                # be written with a tolerance loose enough to hide a real 0.04 ft error.
                "x_ft": round(rect[0], 3),
                "y_ft": round(rect[1], 3),
                "width_ft": round(rect[2], 3),
                "depth_ft": round(rect[3], 3),
            })
            placed.append(rect)
            walls[wall]["cursor"] = (seat - walls[wall]["base"]) + fw
        if layout:
            r["fixture_layout"] = layout
            report["fixtures_placed"] += sum(1 for f in layout if "unplaced" not in f)
            report["fixtures_unplaced"] += sum(1 for f in layout if "unplaced" in f)


# --------------------------------------------------------------------- entry point
def place(plan, C=None):
    """Place every opening, the stair and the wet-room fixtures, in that order.

    Interior doors first; then exterior doors, which is where the passage axis is decided;
    then windows, into whatever run the doors have left; then fixtures, into whatever run the
    openings have left.

    WP-7.2 INVERTED THIS. Fixtures used to run first, under a note saying "a door has to know
    what is against the wall it would swing into" — and `occupied` never held a fixture, so
    the code did not do the thing its own comment gave as the reason. What it did instead was
    draw a door straight through a double vanity. Both orderings need the two passes to share
    `occupied`; the question is only which loses when they cannot both fit, and that is
    settled: a door is AUTHORED in the record, a fixture layout is DERIVED here, and an
    authored fact must never lose silently to an inferred one (OQ 52)."""
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
    envs = envelopes(plan)
    for lv in plan["levels"]:
        rooms = [r for r in lv["rooms"]]
        occupied = {}
        _place_interior(rooms, occupied, report)
        _place_exterior(rooms, occupied, W, H, C, report, envs)
        _place_windows(rooms, occupied, W, H, report, envs)
        fixture_pass(rooms, C, report, occupied)
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
