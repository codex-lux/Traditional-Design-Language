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


# The jamb allowance and the solid beside an opening are ONE number each, shared with the
# renderers (build/render_plan.py) and with the CP engine's door floor (WP-6.3), so the
# drawing, the proof and this pass can never again disagree about what fits (OQ 41/63).
# CORRECTED 1 OCT 2026 (WP-16.6): this said "the solid between openings", and since R5 the wall
# between two WINDOWS is not this foot. It is the pier floor `window_pier` reads from the pier
# fault, 1.0 x the wider window, except for the five styles that fault licenses, which keep this
# foot inside one room (R5b). The foot still governs beside a door, the doorcase and the masonry.
JAMB_FT = 0.35
MIN_SOLID_FT = 1.0

_STOREYS = None


def _dc():
    return _mod("doorcase", os.path.join(ROOT, "build", "doorcase.py"))


def _storeys():
    """build/storeys.py, loaded lazily and cached. NOT `structure.py`, which is where this
    derivation used to live: structure loads geometry, and geometry calls stair_pass, so
    importing it from here would close a cycle. storeys.py is a leaf for that reason."""
    global _STOREYS
    if _STOREYS is None:
        _STOREYS = _mod("storeys", os.path.join(ROOT, "build", "storeys.py"))
    return _STOREYS


_THRESH = None


def _thresh():
    """build/threshold.py -- the stoop and the gable-end stacks (WP-11.4). Loaded lazily and
    cached. It is NOT a leaf (it loads `resolve_kit` for the cascade-resolved kit), and that
    closes no cycle: `resolve_kit` reaches only `proportion_engine` and, through it,
    `construction_vocabulary`, and neither reaches `geometry`."""
    global _THRESH
    if _THRESH is None:
        _THRESH = _mod("threshold", os.path.join(ROOT, "build", "threshold.py"))
    return _THRESH


_FURN = None


def _furn():
    """build/furniture.py, the packer and the free-run subtraction. A LEAF: it imports nothing
    from build/, so loading it here closes no cycle."""
    global _FURN
    if _FURN is None:
        _FURN = _mod("furniture", os.path.join(ROOT, "build", "furniture.py"))
    return _FURN


_WPIER = None


def _wpier():
    """build/window_pier.py -- the floor, the aim and the spared styles between two windows
    (WP-16.6). A LEAF beside doorcase.py: it loads proportion_engine and resolve_kit, neither of
    which reaches geometry, so loading it here closes no cycle."""
    global _WPIER
    if _WPIER is None:
        _WPIER = _mod("window_pier", os.path.join(ROOT, "build", "window_pier.py"))
    return _WPIER


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
PLACEMENT_PLAN_KEYS = ("footprint", "geometry_report", "stair", "opening_report",
                       "threshold", "hearths", "appendages")
PLACEMENT_ROOM_KEYS = ("geometry", "fixture_layout", "furniture_layout")
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


def on_main_face(env, face, W, H):
    """Whether a room whose own element occupies `env` -- `(x0, y0, x1, y1)`, from `envelopes`,
    or None for a room in no element -- stands on the main block's `face`.

    THE ELEVATION'S OWN TEST (`elevation.placed_openings`), not element membership: an opening is
    on the main block's face where its element's face lies on the main block's, within 0.01 ft,
    and a room in no element stands in the main block. Asking "which element" instead would part
    from the drawing on a wing built flush with the front. ONE SPELLING for the doorcase
    reservation and the stoop (WP-15.8's audit, auditor F): `threshold._entrance_doors` took
    every door on the entrance-face LETTER to be on the entrance front, and called the Tidewater
    kitchen's door, on the dependency's own south face 5.28 ft back, "a service door on the
    entrance front"."""
    if env is None:
        return True
    main_edge = {"S": 0.0, "N": H, "W": 0.0, "E": W}[face]
    return abs({"S": env[1], "N": env[3], "W": env[0], "E": env[2]}[face] - main_edge) <= 0.01


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


def faces_across_a_gap(plan, env, tol=0.6):
    """`{face: neighbour_element_id}` for the faces of one element that look across a gap at
    ANOTHER element of the same building (WP-11.6, layer 5).

    Ruling 4 of `oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it`: *"where
    a room's exterior wall faces the hyphen gap, the finding says so in its own words rather than
    convicting a landlocked room: exterior to the weather, interior to the view"*. That wall is a
    real exterior wall -- it takes the weather and it can hold a window -- and it is also the wall
    that stares at the side of the house. A critic that says only "exterior" loses the second half.

    A face counts when another element lies WHOLLY BEYOND it and OVERLAPS it on the perpendicular
    axis. The overlap test is what keeps a diagonal neighbour out, and that is the ruling's own
    position on the diagonal case -- refused rather than modelled -- arriving here as one
    condition: a face that looks past the corner of another block is looking at the yard.

    `{}` on a one-rectangle plan, where there is no other element to look at, and `{}` for an
    element with open ground on every side."""
    x0, y0, x1, y1 = env
    out = {}
    for b in ((plan.get("footprint") or {}).get("blocks") or []):
        bx0, by0 = b["x_ft"], b["y_ft"]
        bx1, by1 = bx0 + b["width_ft"], by0 + b["depth_ft"]
        if (abs(bx0 - x0) < tol and abs(by0 - y0) < tol
                and abs(bx1 - x1) < tol and abs(by1 - y1) < tol):
            continue                      # this element itself
        if min(by1, y1) - max(by0, y0) > tol:          # they share a band of latitude
            if bx0 >= x1 - tol: out.setdefault("E", b["id"])
            if bx1 <= x0 + tol: out.setdefault("W", b["id"])
        if min(bx1, x1) - max(bx0, x0) > tol:          # ... of longitude
            if by0 >= y1 - tol: out.setdefault("N", b["id"])
            if by1 <= y0 + tol: out.setdefault("S", b["id"])
    return out


_APPD = None


def _appd():
    """build/appendages.py -- the terrace at grade (WP-11.10). A LEAF; see its header."""
    global _APPD
    if _APPD is None:
        _APPD = _mod("appendages", os.path.join(ROOT, "build", "appendages.py"))
    return _APPD


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
    """`(lo, hi)` minus `blocked`. ONE spelling, in build/furniture.py, which is a leaf.

    WP-11.3 moved the body there because `fixture_pass`'s packer went with it and the two
    belong together; this name stays so every caller in this file, and `tests/test_openings.py`,
    are unchanged. `plan_check.py` carries a third inline copy of the same subtraction in its
    wall-run check -- known, and not this package's to move."""
    return _furn().free_runs(lo, hi, blocked)


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


def _place_interior(level_rooms, occupied, report, appendages=None):
    """Every door between two rooms on one level.

    WP-11.10. `appendages` is `{room_id: (x, y, w, h)}` for the at-grade appendages
    `build/appendages.py` placed OUTSIDE the block -- a terrace, today, and nothing else in
    this corpus. It is threaded in rather than read off `room.geometry` on purpose: an
    appendage takes no rectangle in the footprint, and writing one onto the room would make
    `structure.wall_lines`, `plan_check`'s `rooms_unplaced` and `geometry._record_prep` all
    see a room the placer never placed. This is the ONE reader that needs the rectangle, and
    it is the only one that gets it. `_rect` is deliberately unchanged; six other call sites
    read it and every one of them must go on seeing a terrace as unplaced."""
    appendages = appendages or {}

    def _r(x):
        return _rect(x) or appendages.get(x.get("id"))

    for a, da, b, db in _door_pairs(level_rooms):
        width = da.get("width_ft") or (db and db.get("width_ft")) or 3.0
        if b is None:
            note = {"reason": f"no room '{da['to']}' on this level for this door to reach"}
            da["unplaced"] = note
            report["unplaced"].append({"pair": [a["id"], da["to"]], **note})
            continue
        ra, rb = _r(a), _r(b)
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


def _place_exterior(level_rooms, occupied, W, H, C, report, envs=None, hearths=None,
                    level_index=0):
    """Exterior doors, and the one rule that fixes the reported symptom.

    op-passage-axis. styles/tidewater-georgian.json c03 is HARD — "Centre passage 10-14 ft
    wide with exterior doors at both ends, aligned on axis and both operable. This is a
    ventilation device, not a hallway" — and groupings/centre-passage-core.json says the
    same. Neither could be satisfied or even checked, because a door had no wall: both
    renderers put every exterior door of a room on the FIRST wall it declared, so a passage
    running front to back had its rear door drawn on its front, under the front door, and
    its actual rear elevation showed a window where the door should be."""
    idx = {r["id"]: r for r in level_rooms}
    masonry = {}
    for key, span, what in _masonry_spans(level_rooms, W, H, envs, hearths, level_index):
        masonry.setdefault(key, []).append((span, what))
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
        stated = [w for w in (r.get("exterior_walls") or []) if w in bw]
        declared = stated or list(bw)
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
            need = width + 2 * MIN_SOLID_FT
            short, took_by = [], set()
            for wall in order:
                if wall in used:
                    took_by.add("its other doors")
                    continue
                lo, hi = bw[wall]
                mas = masonry.get((r["id"], wall), [])
                free = _free(lo, hi, occupied.get((r["id"], wall), []) + [sp for sp, _w in mas])
                # the passage axis wants the door on the room's own centreline
                prefer = (lo + hi) / 2
                pos = _seat(free, width, prefer)
                if pos is not None:
                    seat = (wall, pos)
                    break
                if hi - lo + 1e-9 < need:
                    short.append(wall)
                    continue
                if occupied.get((r["id"], wall)):
                    took_by.add("its other doors")
                took_by.update(w for sp, w in mas if sp[1] > lo and sp[0] < hi)
            if seat is None:
                # THE REASON IS WHAT FAILED (WP-15.8's audit, auditor F). This said "no declared
                # exterior wall of this room has a free run" and named a `declared_wall` for every
                # refusal -- on `bad-05` of a garage that declares no exterior wall at all, whose
                # one boundary wall is 23.63 ft against a 24 ft door: shorter, not taken.
                which = "declared exterior wall" if stated else "exterior wall"
                if short and not took_by:
                    reason = (f"every {which} of this room is shorter than the door and its "
                              f"jambs ({need:.2f} ft)")
                elif took_by:
                    reason = (f"no {which} of this room has a free run left beside "
                              + " and ".join(sorted(took_by)))
                else:
                    reason = f"no {which} of this room is on the footprint boundary"
                d["unplaced"] = {"reason": reason,
                                 **({"declared_wall": stated[0]} if stated else {}),
                                 "needs": {"free_run_ft": round(need, 2)},
                                 "have": {"walls_tried": list(order),
                                          "walls_too_short": short}}
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


# THE PIER BESIDE A CHIMNEY BREAST OR A STACK IS THE SAME MINIMUM SOLID AS BESIDE A DOOR
# (WP-13.2). `MIN_SOLID_FT` is the corpus's one figure for the masonry an opening keeps between
# itself and the next opening, and a sash jamb against a breast needs a pier of masonry for the
# same reason it needs one against a door frame. It is EDITORIAL -- no record states the width of
# a jamb pier -- and it is reused here rather than restated so the plan owns one such figure.
#
# AND ONE QUANTUM MORE, FOR THE RECORD'S OWN PRECISION. A seated position is written
# `round(p, 3)`, so a sash seated flush against a reserved edge lands a half-thousandth either
# side of it: half the time 0.9995 ft of pier where the reader was promised 1.0. The reserved
# run is widened by the quantum the record rounds to, so the written figure cannot fall inside
# the pier -- WP-11.13's `grid_allowance_ft` for the same reason one layer down (a box rounded
# inward could not hold its own rooms; a run rounded outward keeps its own clearance).
MASONRY_PIER_FT = MIN_SOLID_FT
_RECORD_QUANTUM_FT = 0.001


def _reserve_masonry(level_rooms, occupied, W, H, envs, hearths, level_index):
    """Occupy each drawn chimney breast's run on its own wall, and each stack's run on the
    boundary wall it stands on, BEFORE a window is seated there -- with the pier either side.

    Reads what `threshold.hearth_pass` judged and wrote (`plan["hearths"]["breasts"]` and
    `["stacks"]`) and judges nothing itself; a breast the pass REFUSED reserves nothing,
    because nothing is drawn there. Returns `{(room, wall): [what was reserved]}` so a window
    refused for want of a run can say what took the wall."""
    took = {}
    for key, span, what in _masonry_spans(level_rooms, W, H, envs, hearths, level_index):
        occupied.setdefault(key, []).append(span)
        took.setdefault(key, []).append(what)
    return took


def _masonry_spans(level_rooms, W, H, envs, hearths, level_index):
    """`[((room, wall), (lo, hi), what)]`: every run a drawn breast or a stack takes on this
    level, with the pier either side -- the spans `_reserve_masonry` occupies before a window is
    seated and `_place_exterior` keeps a door out of (WP-15.8's audit, auditor F: an exterior
    door was seated before the masonry was reserved, and a library door driven onto its E wall
    stood on the stack and inside the drawn breast)."""
    out = []
    if not hearths:
        return out
    pad = MASONRY_PIER_FT + _RECORD_QUANTUM_FT
    by_id = {r["id"]: r for r in level_rooms}
    for row in (hearths.get("breasts") or []):
        if not row.get("drawn") or row.get("level") != level_index:
            continue
        r = by_id.get(row["room"])
        if r is None or row.get("wall") not in ("N", "E", "S", "W"):
            continue
        run = ((row["y_ft"], row["y_ft"] + row["depth_ft"]) if row["wall"] in ("E", "W")
               else (row["x_ft"], row["x_ft"] + row["width_ft"]))
        out.append(((r["id"], row["wall"]), (run[0] - pad, run[1] + pad), "the chimney breast"))
    # A stack passes through every storey, so its run is reserved on every level's rooms that
    # stand on that wall where it stands.
    #
    # ON THE WALL LINE IT STANDS ON, NOT ON EVERY WALL OF THAT LETTER (WP-15.8's audit, auditor F).
    # This matched a room by the wall's LETTER and the run's overlap along it, so on the shipped
    # Tidewater record the main block's W stack reserved the west wall of the dependency's pantry,
    # 31 ft away, and the E stack the powder room's east wall; a window there would have been
    # refused "beside the chimney stack". `hearth_pass` seats every stack on the MAIN block's face
    # (`_stack_rect` takes the footprint's W and D), so a room's wall is the stack's only where
    # its own element's face is the main block's -- `on_main_face`, the doorcase's and the
    # elevation's test.
    for sk in (hearths.get("stacks") or []):
        wall = sk.get("wall")
        if wall not in ("N", "E", "S", "W"):
            continue
        run = ((sk["y_ft"], sk["y_ft"] + sk["depth_ft"]) if wall in ("E", "W")
               else (sk["x_ft"], sk["x_ft"] + sk["width_ft"]))
        for r in level_rooms:
            rect = _rect(r)
            if not rect:
                continue
            env = (envs or {}).get(r["id"])
            bw = _boundary_walls(rect, W, H, env=env)
            if wall not in bw or not on_main_face(env, wall, W, H):
                continue
            lo, hi = bw[wall]
            if run[1] + pad <= lo or run[0] - pad >= hi:
                continue
            out.append(((r["id"], wall), (run[0] - pad, run[1] + pad), "the chimney stack"))
    return out


def _entrance_door(plan, level_rooms, W, H, envs):
    """`(room, door, face, None)` for the entrance door the elevation dresses, or
    `(None, None, face, why)`: the widest exterior door placed on the main block's entrance face
    (`doorcase.entrance_index`, ties to the lower coordinate), the face being the record's own
    `context.entrance_faces`, default S. ONE reading, for the doorcase reservation and for the
    centre the windows are seated out from (WP-16.6, R5a), lifted out of `_reserve_doorcase`
    with its two refusals' words unchanged."""
    DC = _dc()
    face = (plan.get("context") or {}).get("entrance_faces") or "S"
    if face not in ("N", "S", "E", "W"):
        return None, None, face, f"the record's entrance face {face!r} is not one face of the main block"
    cands = []
    for r in level_rooms:
        rect = _rect(r)
        if not rect or not on_main_face((envs or {}).get(r["id"]), face, W, H) \
                or face not in _boundary_walls(rect, W, H):
            continue
        for d in (r.get("doors") or []):
            if d.get("to") == "exterior" and d.get("wall") == face and d.get("position_ft") is not None:
                cands.append((r, d))
    i = DC.entrance_index([(d.get("width_ft") or 3.5, d["position_ft"]) for _r, d in cands])
    if i is None:
        return None, None, face, f"no exterior door is placed on the main block's {face} face"
    room, door = cands[i]
    return room, door, face, None


def window_centres(plan, level_rooms, W, H, envs):
    """`({line: (along_ft, source)}, why)`: the centre the windows of a face line are seated out
    from where it is not the face's own centre (R5a, ruled 29 Sep 2026: "the centre holds -- the
    entrance where a door is seated, otherwise the face's centre").

    The entrance is the door `_entrance_door` reads, the elevation's own. WHERE THAT DOOR IS A
    GARAGE DOOR THE FACE'S CENTRE HOLDS: no doorcase frames a garage door (`_reserve_doorcase`,
    `elevation._clearances`), and a garage door is no entrance. Taken as recommended under Lucas's
    standing instruction of 1 Oct 2026, never put (U4 in
    `oq/the-placer-seats-windows-a-foot-apart-and-the-corpus-states-the-pier-three-ways`): the
    narrower pedestrian door beside it was the alternative, and choosing it would be a second
    reading of "the entrance door" beside the elevation's."""
    room, door, face, why = _entrance_door(plan, level_rooms, W, H, envs)
    if door is None:
        return {}, why
    if "garage" in str(door.get("type") or "").lower():
        return {}, ("the widest door on the entrance front is a garage door, and a garage door is "
                    "no entrance: the face's centre holds")
    line, _ = face_line((envs or {}).get(room["id"]), face, W, H)
    return {line: (float(door["position_ft"]), f"the entrance door's axis ({room['id']})")}, None


# THE ENTRANCE DOORCASE IS RESERVED BEFORE A WINDOW IS SEATED (Phase 15, WP-15.6). Lucas, of the
# drawn Tidewater front (27 Sep 2026): "there's still no concept of how close windows can be to
# doors". This pass reserved the entrance door's LEAF and `MIN_SOLID_FT` either side, and the
# elevation then drew the doorcase around that leaf -- the casing each side, and the sidelights
# where they fit -- so the centre passage's own sash stood 12 in from the leaf and 4.98 in from the
# casing. facade-classical states the rule the placement never read: the composition "is not
# allowed to touch the flanking windows", and "The residual wall each side of the entrance
# composition should not fall below about half the ordinary pier". Both are applied here, with the
# composition's width from `doorcase.composition` -- the arithmetic the elevation draws.
#
# WHAT WAS NOT RULED WAS NOT APPLIED, AND IT IS RULED NOW. The pier between two WINDOWS was left at
# `MIN_SOLID_FT` here (WP-15.6), because the corpus states that ratio three ways (a style's own 0.6
# to 1.0 times the window, the packs' 1.2 to 2.0 and a 1.4 target, the fault's floor of 1.0):
# `oq/the-placer-seats-windows-a-foot-apart-and-the-corpus-states-the-pier-three-ways`. Lucas ruled
# it on 29 Sep 2026 (R5, R5a, R5b) and `_place_windows` seats to it since WP-16.6, reading
# `build/window_pier.py`. The doorcase's residual pier below is facade-classical's rule and is
# unchanged; the pier at the corner of a doorcase is still not ruled.
def _reserve_doorcase(plan, level_rooms, W, H, envs, report, level_index):
    """The entrance composition's run on the entrance face, and the rooms whose windows must keep
    clear of it, or None where no doorcase is drawn; the verdict either way is written to
    `report["doorcase"]` (`reserved` and the reason, or the door, the figures and their sources).

    The doorcase exists where the elevation draws one: the ground storey, a style inside the
    elevation's own gate (`doorcase.applies`), the entrance face the record names (the elevation's
    own `context.entrance_faces`, default S), and the entrance door the elevation dresses
    (`doorcase.entrance_index`: the widest exterior door on the main block's face, ties to the lower
    coordinate). Its run is the door as PLACED -- the width the elevation draws the leaf at -- plus
    the casing each side and the sidelights each side where `doorcase.composition` fits them."""
    if level_index != 0:
        return None
    DC = _dc()
    rec = {"reserved": False}
    report["doorcase"] = rec
    style = plan.get("style")
    op, fac = DC.PE.resolve("opening-proportion"), DC.PE.resolve("facade-classical")
    if not DC.applies(style, op, fac):
        rec["why"] = (f"no doorcase is drawn for '{style}': it is outside opening-proportion's and "
                      f"facade-classical's own applies_to, so the elevation draws none")
        return None
    room, door, face, why = _entrance_door(plan, level_rooms, W, H, envs)
    if door is None:
        rec["why"] = why
        return None

    def _on_main(r):
        return on_main_face((envs or {}).get(r["id"]), face, W, H)

    if "garage" in str(door.get("type") or "").lower():
        # the elevation's own rule (`elevation._clearances`, `render_elevation`): the widest door on
        # the entrance front is a garage door here, and no doorcase frames a garage door
        rec["why"] = ("the widest door on the entrance front is a garage door, and the elevation "
                      "draws no doorcase around a garage door; it keeps only its leaf's run")
        return None
    ground = next((st for st in _storeys().storey_heights(plan) if st.get("index") == 0), None)
    if not ground or not ground.get("storey_height_ft"):
        rec["why"] = ("the ground storey states no height, so the doorcase the elevation composes "
                      "from it has no width; the door keeps only its leaf's run")
        return None
    slots = _thresh().resolved_slots(style)
    forbids = DC.forbidden_of(slots) if slots is not None else set()
    # THE SIDELIGHTS THE KIT FORBIDS, AT THE HOUSE'S DATE (WP-16.4). `forbids` holds whole-slot
    # bans only, so a style forbidding the sidelights ROW -- the Georgian family's 1700-1780 ban,
    # the Cape's and the saltbox's own -- had its run reserved for sidelights the elevation must
    # not draw. `doorcase.refusals` is the one reading, the elevation's too.
    date = (plan.get("context") or {}).get("date_of_representation")
    refused = DC.refusals(slots, date) if slots is not None else {}
    comp = DC.composition(op, fac, ground["storey_height_ft"] * 12.0, forbids=forbids,
                          refused=refused)
    leaf = door.get("width_ft") or 3.5
    side_in = comp["casing_w_in"] + (comp["sidelight_w_in"] if comp["use_sidelights"] else 0.0)
    half = leaf / 2.0 + side_in / 12.0
    pos = door["position_ft"]
    bay, unstated = DC.stated_bay_ft(plan)
    # EVERY ROOM ON THE MAIN BLOCK'S ENTRANCE FACE, not only the ones the RUN touches (WP-15.8).
    # The keep-out is the run PLUS the residual pier each side, so it reaches past the run into
    # the next room's wall. Recording only the rooms the run touched left a flanking room's window
    # to be seated inside that pier: an 8 ft hall whose door stands at 4 ft, beside a 4.5 ft
    # parlor, seated the parlor's sash 11.95 in from the doorcase against a floor of 33 in, and
    # the refusal sentence and the census never looked at the parlor. Which rooms the band
    # actually reaches is decided per wall, against the run the window is seated in
    # (`_doorcase_keepout`), so a room far down the face is never charged for a doorcase that took
    # none of its wall.
    rooms, touched = {}, set()
    for r in level_rooms:
        rect = _rect(r)
        if not rect or not _on_main(r):
            continue
        run = _boundary_walls(rect, W, H).get(face)
        if not run:
            continue
        rooms[r["id"]] = run
        if run[0] < pos + half and run[1] > pos - half:
            touched.add(r["id"])
    rec.update({
        "reserved": True, "wall": face, "room": room["id"], "position_ft": round(pos, 3),
        "leaf_ft": leaf, "casing_in": round(comp["casing_w_in"], 3),
        "sidelights_in": round(comp["sidelight_w_in"], 3) if comp["use_sidelights"] else None,
        # WHO REFUSED THEM, where the kit did: the run is the narrower one and the record says why
        "sidelights_refused": ((refused.get("transom_sidelight") or refused.get("sidelights"))
                               if comp["sidelights_forbidden"] else None),
        # WHOSE DOORCASE THIS RUN WAS RESERVED FOR: the style and the date it was composed under,
        # which a drawing of this placement under another style cannot assume (WP-16.4)
        "composed_for": {"style": style, "date": date},
        "run_ft": [round(pos - half, 3), round(pos + half, 3)],
        "rooms_touched": sorted(touched),
        "residual": ("half the ordinary pier each side, facade-classical's door_surround rule, at "
                     f"the {bay:g} ft bay the parti states" if bay else
                     f"NOT JUDGED: {unstated}; the run keeps the placer's "
                     f"{MIN_SOLID_FT:g} ft solid each side"),
        "source": ("doorcase.composition (opening-proportion's leaf and casing, facade-classical's "
                   "width cap and sidelights) and doorcase.residual_pier_ft"),
    })
    return {"wall": face, "lo": pos - half, "hi": pos + half, "rooms": rooms,
            "bay_ft": bay, "facade_pack": fac}


def _doorcase_keepout(doorcase, room_id, wall, width_ft, run):
    """The span a window `width_ft` wide may not enter on `wall` of `room_id`, or None: the doorcase
    run plus the residual pier its own width asks for, and never less than the solid every opening
    keeps (`MIN_SOLID_FT`).

    None ALSO where that span does not reach `run`, the wall run the window is seated in: a room on
    the entrance face whose wall the band stops short of has nothing taken from it, and its refusal
    (if any) must not name the doorcase. That is what makes it safe to record every room on the
    face (WP-15.8) rather than only the ones the doorcase's own run touched."""
    if not doorcase or wall != doorcase["wall"] or room_id not in doorcase["rooms"]:
        return None
    res = MIN_SOLID_FT
    if doorcase["bay_ft"]:
        half = _dc().residual_pier_ft(doorcase["facade_pack"], doorcase["bay_ft"], width_ft)
        if half is not None:
            res = max(res, half)
    band = (doorcase["lo"] - res - _RECORD_QUANTUM_FT, doorcase["hi"] + res + _RECORD_QUANTUM_FT)
    if not (run[0] < band[1] and run[1] > band[0]):
        return None
    return band


def _beside(key, run, door_spans, glazed, took, keep):
    """What took a window's run on its wall, in the words a refusal prints, or None where nothing
    did: the doors whose spans lie on `run`, the windows already seated there (`glazed`, which for
    a partial refusal is the window's own first units), the masonry, and the doorcase band where
    `_doorcase_keepout` returned one (WP-15.8)."""
    lo, hi = run
    names = ["its doors"] if any(s < hi and e > lo for s, e in door_spans.get(key, [])) else []
    names += ["the windows already seated on it"] if key in glazed else []
    names += sorted(set(took.get(key, [])))
    names += ["the entrance doorcase"] if keep else []
    return " and ".join(names) or None


def face_line(env, wall, W, H):
    """`((wall, across), (lo, hi))` for a window on `wall` of a room in `env`: the face it stands
    in -- the wall's letter and the coordinate ACROSS it, read off the room's own element or the
    main block -- and the face's extent ALONG it.

    TWO WINDOWS ARE NEIGHBOURS ONLY ON ONE LINE (WP-16.6). The placer kept its foot between two
    windows inside one ROOM, so two windows either side of a partition could stand a few inches
    apart: on the shipped plans 10 of the 35 window-to-window piers cross a partition. A face line
    is the wall a reader sees, whichever room is behind it; a dependency's south face set back
    from the main block's is another wall, and its windows are not paired across the gap."""
    x0, y0, x1, y1 = env if env else (0.0, 0.0, W, H)
    across = {"S": y0, "N": y1, "W": x0, "E": x1}[wall]
    run = (x0, x1) if wall in ("N", "S") else (y0, y1)
    return (wall, round(across, 3)), run


def opening_axes(level_rooms, W, H, envs):
    """`{line: [(along_ft, kind, room_id), ...]}`: every opening SEATED on one level, by face line,
    sorted along it -- the windows' `positions_ft` and the exterior doors' `position_ft`, as
    written. What the storey above aligns to (R6): the ground opening below a window is a window or
    a door, because the alignment fault measures every drawn opening on the storey below
    (`elevation.storey_alignment` reads both)."""
    out = {}
    for r in level_rooms:
        if not _rect(r):
            continue
        env = (envs or {}).get(r["id"])
        for win in (r.get("windows") or []):
            if win.get("wall") in ("N", "E", "S", "W"):
                line, _ = face_line(env, win["wall"], W, H)
                for p in (win.get("positions_ft") or []):
                    out.setdefault(line, []).append((float(p), "window", r["id"]))
        for d in (r.get("doors") or []):
            if d.get("to") == "exterior" and d.get("wall") in ("N", "E", "S", "W") \
                    and d.get("position_ft") is not None:
                line, _ = face_line(env, d["wall"], W, H)
                out.setdefault(line, []).append((float(d["position_ft"]), "door", r["id"]))
    return {k: sorted(v) for k, v in out.items()}


def _order_assign(n, m, cost):
    """The order-preserving pairing of `n` sorted units with `m` sorted axes that pairs min(n, m)
    of them at the least summed `cost(i, j)`, as `[(i, j)]` index pairs, both increasing. Ties go
    to the lower index, so the answer is a function of the inputs and not of a dictionary's order."""
    if not n or not m:
        return []
    swap = n > m
    p, q = (m, n) if swap else (n, m)              # every one of the p takes one of the q, in order
    c = (lambda i, j: cost(j, i)) if swap else cost
    INF = float("inf")
    best = [[INF] * (q + 1) for _ in range(p + 1)]
    take = [[False] * (q + 1) for _ in range(p + 1)]
    for j in range(q + 1):
        best[0][j] = 0.0
    for i in range(1, p + 1):
        for j in range(i, q + 1):
            skip = best[i][j - 1]
            use = best[i - 1][j - 1] + c(i - 1, j - 1)
            # strictly less: on a tie the pairing already found with the earlier axis stands
            if use < skip:
                best[i][j], take[i][j] = use, True
            else:
                best[i][j] = skip
    pairs, i, j = [], p, q
    while i > 0:
        if take[i][j]:
            pairs.append((i - 1, j - 1))
            i, j = i - 1, j - 1
        else:
            j -= 1
    pairs.reverse()
    return [(jj, ii) for ii, jj in pairs] if swap else pairs


# A unit matched to an axis its own room cannot take costs more than any distance along a wall, so
# the pairing seats every unit it can on an axis its room CAN take before it gives one an axis it
# cannot (`_assign_axes`). A number of feet no wall in this corpus approaches.
_UNTAKEABLE_FT = 1.0e6


def _assign_axes(wins, axes):
    """`{id(unit): (along_ft, kind)}`: the axis of the opening below that each upper unit takes
    (R6), per room wall, among the openings whose axis falls inside that wall's run.

    A unit whose room has NO opening below its run is not here, and is seated where the pier rule
    puts it (R6a): the alignment fault judges it. Where a room has openings below its run, its
    units take them in order, nearest where each would otherwise have been seated, and the
    openings its room can take -- the window inside the room's own run at that axis -- before the
    ones it cannot; a unit left with an opening its room cannot take is refused by name (R6), and
    a unit left with none is R6a's. Taken as recommended under Lucas's standing instruction of
    1 Oct 2026, never put (U1 and U2 in
    `oq/the-placer-seats-windows-a-foot-apart-and-the-corpus-states-the-pier-three-ways`)."""
    out = {}
    groups = {}
    for w in wins:
        groups.setdefault((w["room"]["id"], w["wall"]), []).append(w)
    for _key, ws in groups.items():
        lo, hi = ws[0]["lo"], ws[0]["hi"]
        cands = [(a, kind) for a, kind, _rid in axes if lo - 1e-9 <= a <= hi + 1e-9]
        if not cands:
            continue
        units = sorted((u for w in ws for u in w["units"]), key=lambda u: (u["prefer"], u["k"]))

        def cost(i, j, _u=units, _c=cands, _lo=lo, _hi=hi):
            a, wd = _c[j][0], _u[i]["w"]["width"]
            takeable = _lo - 1e-9 <= a - wd / 2 and a + wd / 2 <= _hi + 1e-9
            return abs(_u[i]["prefer"] - a) + (0.0 if takeable else _UNTAKEABLE_FT)
        for i, j in _order_assign(len(units), len(cands), cost):
            out[id(units[i])] = cands[j]
    return out


def _named_on(span, key, door_spans, took_spans, keep):
    """What stands on `span` of a room's wall, in the words a refusal prints."""
    lo, hi = span
    names = ["its doors"] if any(s < hi and e > lo for s, e in door_spans.get(key, [])) else []
    names += sorted({what for (s, e), what in took_spans.get(key, []) if s < hi and e > lo})
    if keep and keep[0] < hi and keep[1] > lo:
        names.append("the entrance doorcase")
    return " and ".join(names) or None


def _seat_line(ws, base, pier, centre, aligned, mode):
    """Seat every unit of one face line and return `{id(unit): verdict}` without writing anything.

    `mode` is "pier" (R5: the wall between two windows at least the floor x the wider, every window
    on the line -- whichever room it lights -- counted) or "foot" (the floor spared, R5b: the
    placer's old foot inside one room). In "pier" mode every unit is seated in ONE queue, the units
    nearest the centre of the composition first, so the centre holds and the outer window moves
    (R5a): an aligned unit at EXACTLY the axis of the opening below or refused (R6, and R5 with R6
    read together: "an upper window that, once aligned, would break the upper pier floor cannot be
    taken there, so it is refused by name"), and the rest by the floor and the aim.

    ONE QUEUE SINCE THE AUDIT OF PHASE 16 (WP-16.8, auditor A). WP-16.6 seated every aligned unit
    before any other and attributed that order to R6, which states none. Where an outer aligned
    window and an inner one contend for the floor, R5a's words decide which yields -- "windows
    nearer the entrance keep their places, and on other faces those nearer the face's centre do;
    the outer window moves along its own wall, or is refused by name" -- and the aligned-first
    order refused the INNER window: on spec-builder-colonial's upper south face the primary
    chamber's unit preferring 9.0 ft was refused for the pier so the unit aligned at 6.745 ft could
    keep its axis. In "foot" mode the order is the one the spared styles always had: aligned units
    first, the rest in record order (a reading, named at WP-16.8: R5b spares the floor, and the
    spared styles keep their whole old pass, order and all, and take no aim).

    THE AIM WHERE THE WALL ALLOWS. A unit is seated at the pack's aim (sash-light's
    `opening_width * 1.4`, where it reaches the style) where that costs no window: it takes the
    aim's pier only if the units still to be seated on its line fit as many beside it as they
    would beside the floor's. Otherwise it takes the floor. Read pier by pier, not face by face: a
    first version gave a whole face the floor wherever one unit on it would have been refused at
    the aim, so a crowded living room took the floor away from the library beside it (good-02,
    measured 1 Oct 2026). Taken as recommended under Lucas's standing instruction of 1 Oct 2026,
    never put (U3 in
    `oq/the-placer-seats-windows-a-foot-apart-and-the-corpus-states-the-pier-three-ways`)."""
    WP = _wpier()
    q = _RECORD_QUANTUM_FT
    out = {}

    def spans_for(u, fn, seated):
        w = u["w"]
        key = (w["room"]["id"], w["wall"])
        sp = list(base.get(key, [])) + ([w["keep"]] if w["keep"] else [])
        for pos, wd, rid in seated:
            if mode == "foot":
                if rid == w["room"]["id"]:
                    sp.append((pos - wd / 2 - MIN_SOLID_FT, pos + wd / 2 + MIN_SOLID_FT))
            else:
                p = fn(pier, max(w["width"], wd)) + q
                sp.append((pos - wd / 2 - p, pos + wd / 2 + p))
        return sp

    def seat(u, fn, seated):
        w = u["w"]
        return _seat(_free(w["lo"], w["hi"], spans_for(u, fn, seated)), w["width"], u["prefer"])

    def fits_axis(u, seated):
        w = u["w"]
        axis, wd = aligned[id(u)][0], w["width"]
        ext = (axis - wd / 2, axis + wd / 2)
        free = _free(w["lo"], w["hi"], spans_for(u, WP.floor_ft, seated))
        return ext, any(s - 1e-9 <= ext[0] and ext[1] <= e + 1e-9 for s, e in free)

    def floor_count(units_, seated):
        # every unit still to come, each as it will be seated: an aligned one at its axis or not at
        # all, the rest at the floor
        seated, n = list(seated), 0
        for v in units_:
            if id(v) in aligned:
                if fits_axis(v, seated)[1]:
                    seated.append((aligned[id(v)][0], v["w"]["width"], v["w"]["room"]["id"]))
                    n += 1
                continue
            p = seat(v, WP.floor_ft, seated)
            if p is not None:
                seated.append((p, v["w"]["width"], v["w"]["room"]["id"]))
                n += 1
        return n

    def bare_seat(u):
        w = u["w"]
        key = (w["room"]["id"], w["wall"])
        sp = list(base.get(key, [])) + ([w["keep"]] if w["keep"] else [])
        return _seat(_free(w["lo"], w["hi"], sp), w["width"], u["prefer"])

    seated = []                                         # (pos, width, room_id) on this line
    units = [u for w in ws for u in w["units"]]
    # the distance from the centre is ROUNDED before it orders anything: two units a third of a
    # wall either side of it are equidistant, and which of them the last bit of a double puts
    # first is not a reason to seat one rather than the other
    if mode == "foot":
        queue = (sorted((u for u in units if id(u) in aligned),
                        key=lambda u: (round(abs(aligned[id(u)][0] - centre), 6), aligned[id(u)][0]))
                 + [u for u in units if id(u) not in aligned])    # record order, as it always was
    else:
        def _at(u):
            return aligned[id(u)][0] if id(u) in aligned else u["prefer"]
        # ONE QUEUE, aligned and unaligned units together, nearest the centre first (R5a with the
        # ruled "read together"; WP-16.8, auditor A: this seated every aligned unit first and
        # called the order R6). Of two units equidistant from the centre the lower coordinate goes
        # first (U13, taken as recommended under Lucas's standing instruction of 1 Oct 2026, never
        # put): on the Tidewater hyphen's line it decides which of backhall's two units is refused.
        queue = sorted(units, key=lambda u: (round(abs(_at(u) - centre), 6), _at(u)))
    for i, u in enumerate(queue):
        w = u["w"]
        if id(u) not in aligned:
            if mode == "foot":
                pos, how = seat(u, None, seated), "foot"
            else:
                pos, how = seat(u, WP.floor_ft, seated), "floor"
                if pos is not None and pier.get("aim"):
                    pa = seat(u, WP.aim_ft, seated)
                    if pa is not None and (abs(pa - pos) < 1e-9 or
                                           floor_count(queue[i + 1:], seated + [(pa, w["width"], w["room"]["id"])])
                                           >= floor_count(queue[i + 1:], seated + [(pos, w["width"], w["room"]["id"])])):
                        pos, how = pa, "aim"
            if pos is not None:
                seated.append((pos, w["width"], w["room"]["id"]))
                out[id(u)] = {"pos": pos, "how": how}
                continue
            out[id(u)] = {"refused": "run" if mode == "foot" or bare_seat(u) is None else "pier"}
            continue
        axis, kind = aligned[id(u)]
        wd = w["width"]
        ext, fits = fits_axis(u, seated)
        if fits:
            seated.append((axis, wd, w["room"]["id"]))
            out[id(u)] = {"pos": axis, "how": "aligned", "axis": axis, "below": kind}
            continue
        if ext[0] < w["lo"] - 1e-9 or ext[1] > w["hi"] + 1e-9:
            why = "it would run past the end of its own room's wall"
        else:
            key = (w["room"]["id"], w["wall"])
            bfree = _free(w["lo"], w["hi"], list(base.get(key, [])) + ([w["keep"]] if w["keep"] else []))
            if not any(s - 1e-9 <= ext[0] and ext[1] <= e + 1e-9 for s, e in bfree):
                why = f"{u['beside'](ext) or 'the wall'} stands there"
            elif mode == "foot":
                why = "the window already seated beside it in its room stands there"
            else:
                why = (f"the wall to the window beside it would fall below {pier['floor']:g} x the "
                       f"wider window")
        out[id(u)] = {"refused": "alignment", "axis": axis, "below": kind, "why": why}
    return out


def _seat_a_foot_apart(ws, occupied, glazed, door_spans, took, report):
    """THE PASS BEFORE WP-16.6, VERBATIM: the spared styles' ground storey (R5b). Each window's
    units in record order, each seated against what its room's own wall already carries, a foot
    (`MIN_SOLID_FT`) from the next, and its record written at once, so a refusal names what was
    on the wall when it was refused."""
    for w in ws:
        r, win, wall, n, width = w["room"], w["win"], w["wall"], w["n"], w["width"]
        lo, hi, keep = w["lo"], w["hi"], w["keep"]
        placed = []
        for k in range(n):
            free = _free(lo, hi, occupied.get((r["id"], wall), []) + ([keep] if keep else []))
            prefer = lo + (hi - lo) * ((k + 1) / (n + 1))
            pos = _seat(free, width, prefer)
            if pos is None:
                break
            placed.append(pos)
            occupied.setdefault((r["id"], wall), []).append(
                (pos - width / 2 - MIN_SOLID_FT, pos + width / 2 + MIN_SOLID_FT))
        if placed:
            # before `_beside` is asked, so a partial refusal names the units it did seat
            glazed.add((r["id"], wall))
        beside = _beside((r["id"], wall), (lo, hi), door_spans, glazed, took, keep)
        if not placed:
            win.pop("positions_ft", None)          # refused whole: see `_place_windows`
            win["unplaced"] = {"reason": (f"the wall has no clear run left beside {beside}"
                                          if beside else "the wall is shorter than the window"),
                               "needs": {"free_run_ft": round(width + 2 * MIN_SOLID_FT, 2),
                                         "units": n},
                               "have": {"units_placed": 0}}
            report["windows_unplaced"] += n
            continue
        if len(placed) < n:
            # the DECLARED count is left alone (WP-6.2): see `_place_windows`
            win["unplaced"] = {"reason": f"{n - len(placed)} of {n} unit(s) had no clear "
                                         f"run left on this wall beside {beside}",
                               "needs": {"free_run_ft": round(width + 2 * MIN_SOLID_FT, 2),
                                         "units": n},
                               "have": {"units_placed": len(placed)}}
            report["windows_unplaced"] += n - len(placed)
        else:
            win.pop("unplaced", None)
        win["positions_ft"] = [round(p, 3) for p in placed]
        report["windows_placed"] += len(placed)

def _place_windows(level_rooms, occupied, W, H, report, envs=None, hearths=None, level_index=0,
                   doorcase=None, pier=None, centres=None, below=None):
    """Windows into the run the doors, the masonry and the entrance doorcase leave, and NEVER
    nearer the next window than the pier rule allows (WP-16.6).

    THIS DOCSTRING SAID, FROM WP-6.2 UNTIL WP-16.6, THAT WINDOWS WERE "centred on the bay grid
    where a bay line falls inside the free space". No line of this function ever read a bay line:
    each unit was seated at `(k+1)/(n+1)` of its room's wall and pushed to the nearest free run.
    The claim is removed rather than built, because the bay grid is the facade's RESULT
    (`oq/the-facade-is-a-result`, WP-11.7) and no ruling asks the placer to centre on it.

    THE PIER (R5, R5a, R5b, ruled 29 Sep 2026). The wall between two windows on one face line --
    whichever rooms are behind them -- is at least `window_pier.floor` x the wider of the two
    (the pier fault's own 1.0), aiming at sash-light's `opening_width * 1.4` where that pack
    reaches the style and the wall allows it, and a unit that cannot be seated is REFUSED BY NAME,
    `rule: pier`. The units nearest the centre of the composition are seated first -- the
    entrance door's axis on the entrance front, the face's centre elsewhere -- so the centre holds
    and the outer window moves along its own wall. The aim is taken where it costs no window: a
    line whose aim refuses a unit the floor would seat is seated at the floor. The five styles the
    pier fault licenses (`window_pier.spared`) keep the old foot inside one room.

    THE ALIGNMENT (R6, R6a). On a storey above another, a window whose room has an opening of the
    storey below under its wall takes EXACTLY that opening's axis, or is refused by name,
    `rule: alignment`: where its room's wall cannot take it there, or (R5 with R6) where the wall
    to the next window would fall below the floor. A window with no opening below its room's run
    is seated by the pier rule, and the alignment fault judges it.

    AND INTO THE RUN THE MASONRY LEAVES (WP-13.2). `hearths` is the record `hearth_pass`
    wrote before this pass ran; its drawn breasts and its stacks are reserved on their walls
    first, so a sash is seated beside a chimney breast exactly as it is seated beside a door
    rather than dead centre in it. A window that no longer fits is UNPLACED with a reason
    naming what took the wall, and the declared count is never overwritten (WP-6.2).

    THE REASON NAMES WHAT IS ON THE WALL, AND NOTHING ELSE (WP-15.8). `_beside` names the doors
    only where a door's span lies on this run, the windows already seated there, the masonry
    `_reserve_masonry` took it for, and the doorcase where its band reaches the run; a wall
    carrying none of them is shorter than the window. Under R5 a unit that would fit on the wall
    with no window on it is refused for the PIER and says so, so "beside the windows already
    seated on it" is said only by the spared styles' foot, which is the one place it is true."""
    # the doors' spans, snapshotted BEFORE the masonry is reserved into the same lists, so a
    # refusal can tell a wall a door took from one the chimney took
    door_spans = {k: list(v) for k, v in occupied.items() if v}
    took = _reserve_masonry(level_rooms, occupied, W, H, envs, hearths, level_index)
    took_spans = {}
    for key, span, what in _masonry_spans(level_rooms, W, H, envs, hearths, level_index):
        took_spans.setdefault(key, []).append((span, what))
    # what a window meets on an EMPTY face: the doors and the masonry, before any window is seated
    base = {k: list(v) for k, v in occupied.items() if v}
    # A WINDOW REFUSED WHOLE CARRIES NO POSITIONS, WHATEVER IT CAME IN WITH (WP-15.8's audit).
    # `unplaced` beside a non-empty `positions_ft` means a PARTIAL refusal, and three readers take
    # it that way: `plan_check`'s "drawn with no window", the plate's windows line and the
    # elevation's refused list. A record re-solved with its old placement still on it (the bench's
    # evaluate and MCP `place_plan` place whatever they are handed) kept the old positions on a
    # window this pass refused outright, so the serious finding vanished on every shipped plan
    # given stale positions while the sheet drew no such window. Seated windows are overwritten
    # below; the three wholesale refusals drop them here.
    glazed = set()
    wins = []
    for r in level_rooms:
        rect = _rect(r)
        if not rect:
            for win in (r.get("windows") or []):
                win.pop("positions_ft", None)          # refused whole: see the note above
                win["unplaced"] = {"reason": "the room is not placed on this level"}
                # COUNTED, like every other unit the pass does not place (WP-15.8): the plate's
                # line read "1 OF 6 ... NOT DRAWN" over two refused windows on bad-03, whose third
                # storey the placer never places
                report["windows_unplaced"] += win.get("count") or 1
            continue
        env = (envs or {}).get(r["id"])
        bw = _boundary_walls(rect, W, H, env=env)
        for win in (r.get("windows") or []):
            wall = win.get("wall")
            n = win.get("count") or 1
            width = win.get("width_ft") or 3.0
            if wall not in bw:
                win.pop("positions_ft", None)          # refused whole: see the note above
                win["unplaced"] = {"reason": "the placement puts this room on no such "
                                             "boundary wall",
                                   **({"declared_wall": wall} if wall in ("N", "E", "S", "W") else {})}
                report["windows_unplaced"] += n
                continue
            lo, hi = bw[wall]
            line, face_run = face_line(env, wall, W, H)
            w = {"room": r, "win": win, "wall": wall, "n": n, "width": width, "lo": lo, "hi": hi,
                 "line": line, "face_run": face_run,
                 "keep": _doorcase_keepout(doorcase, r["id"], wall, width, (lo, hi))}
            key = (r["id"], wall)
            w["units"] = [{"w": w, "k": k, "prefer": lo + (hi - lo) * ((k + 1) / (n + 1)),
                           "beside": (lambda ext, _key=key, _keep=w["keep"]:
                                      _named_on(ext, _key, door_spans, took_spans, _keep))}
                          for k in range(n)]
            wins.append(w)

    spared = pier is None or pier.get("spared") or pier.get("floor") is None
    mode = "foot" if spared else "pier"
    by_line = {}
    for w in wins:
        by_line.setdefault(w["line"], []).append(w)
    verdicts, written = {}, set()
    seating = report.setdefault("window_seating", [])
    for line in sorted(by_line, key=lambda k: (k[0], k[1])):
        ws = by_line[line]
        given = (centres or {}).get(line)
        # a line with no centre given -- any face line but the entrance front's, a hyphen's among
        # them -- holds about its own run's centre and not the entrance axis (U12, WP-16.8: taken as
        # recommended under Lucas's standing instruction of 1 Oct 2026, never put)
        centre = given[0] if given else (ws[0]["face_run"][0] + ws[0]["face_run"][1]) / 2.0
        aligned = _assign_axes(ws, (below or {}).get(line) or []) if below is not None else {}
        if spared and below is None:
            # THE OLD FOOT, EXACTLY (R5b): the pass before WP-16.6, verbatim, because nothing on a
            # ground storey moves for a spared style -- including WHEN each refusal's sentence is
            # composed, which is why it writes its records here and not with the rest below.
            _seat_a_foot_apart(ws, occupied, glazed, door_spans, took, report)
            written.update(id(w) for w in ws)
            seating.append({"level": level_index, "wall": line[0], "across_ft": line[1],
                            "centre_ft": None, "centre": None, "mode": "foot",
                            "seated": {}, "refused": {}})
            continue
        got = _seat_line(ws, base, pier, centre, aligned, mode)
        verdicts.update(got)
        for u in sorted((u for w in ws for u in w["units"]),
                        key=lambda u: (got[id(u)].get("pos", 0.0))):
            v = got[id(u)]
            if "pos" in v:
                w = u["w"]
                occupied.setdefault((w["room"]["id"], w["wall"]), []).append(
                    (v["pos"] - w["width"] / 2 - MIN_SOLID_FT, v["pos"] + w["width"] / 2 + MIN_SOLID_FT))
        seating.append({"level": level_index, "wall": line[0], "across_ft": line[1],
                        "centre_ft": round(centre, 3), "centre": given[1] if given else
                        "the face's centre", "mode": mode,
                        "seated": {h: sum(1 for v in got.values() if v.get("how") == h)
                                   for h in ("aligned", "aim", "floor", "foot")
                                   if any(v.get("how") == h for v in got.values())},
                        "refused": {c: sum(1 for v in got.values() if v.get("refused") == c)
                                    for c in ("run", "pier", "alignment")
                                    if any(v.get("refused") == c for v in got.values())}})

    floor = (pier or {}).get("floor")
    for w in wins:
        if id(w) in written:
            continue
        r, win, wall, n, width = w["room"], w["win"], w["wall"], w["n"], w["width"]
        placed = sorted(verdicts[id(u)]["pos"] for u in w["units"] if "pos" in verdicts[id(u)])
        refused = [verdicts[id(u)] for u in w["units"] if "pos" not in verdicts[id(u)]]
        if placed:
            # before `_beside` is asked, so a partial refusal names the units it did seat
            glazed.add((r["id"], wall))
        if not refused:
            win.pop("unplaced", None)
            win["positions_ft"] = [round(p, 3) for p in placed]
            report["windows_placed"] += len(placed)
            continue
        parts = []
        for cause in ("run", "pier", "alignment"):
            k = sum(1 for v in refused if v["refused"] == cause)
            if not k:
                continue
            whole = not placed and k == n
            if cause == "run":
                beside = _beside((r["id"], wall), (w["lo"], w["hi"]), door_spans,
                                 glazed if spared else set(), took, w["keep"])
                if whole:
                    txt = (f"the wall has no clear run left beside {beside}" if beside
                           else "the wall is shorter than the window")
                else:
                    txt = (f"{k} of {n} unit(s) had no clear run left on this wall beside {beside}"
                           if beside else f"{k} of {n} unit(s) had no clear run left on this wall")
                parts.append({"units": k, "reason": txt})
            elif cause == "pier":
                txt = ((f"the wall between it and the window beside it would fall below "
                        f"{floor:g} x the wider window") if whole else
                       (f"{k} of {n} unit(s) would leave a wall below {floor:g} x the wider window "
                        f"beside the window next to it"))
                parts.append({"rule": "pier", "units": k, "reason": txt})
            else:
                first = next(v for v in refused if v["refused"] == "alignment")
                txt = ((f"it could not stand on the axis of the {first['below']} below it: "
                        f"{first['why']}") if whole else
                       (f"{k} of {n} unit(s) could not stand on the axis of the opening below: "
                        f"{first['why']}"))
                parts.append({"rule": "alignment", "units": k, "reason": txt})
        rec = {"reason": "; ".join(p["reason"] for p in parts),
               "needs": {"free_run_ft": round(width + 2 * MIN_SOLID_FT, 2), "units": n},
               "have": {"units_placed": len(placed)}}
        if len(parts) == 1 and parts[0].get("rule"):
            rec["rule"] = parts[0]["rule"]
        elif len(parts) > 1:
            rec["parts"] = parts
        if any(p.get("rule") == "pier" for p in parts):
            rec["needs"]["pier_over_the_wider_window"] = floor
        al = [v for v in refused if v["refused"] == "alignment"]
        if al:
            rec["axes"] = [{"axis_ft": round(v["axis"], 3), "opening": v["below"], "why": v["why"]}
                           for v in al]
        win["unplaced"] = rec
        report["windows_unplaced"] += len(refused)
        if placed:
            # the DECLARED count is left alone. Overwriting it with what was placed
            # would make the record lose the author's intent to a placement outcome —
            # the same silent overwrite this whole package exists to remove — and the
            # shortfall is already legible as count - len(positions_ft). Caught by the
            # DXF round trip, which asserts the rebuilt record equals the authored one.
            win["positions_ft"] = [round(p, 3) for p in placed]
            report["windows_placed"] += len(placed)
        else:
            win.pop("positions_ft", None)          # refused whole: see the note above


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


_ELEM = None


def _elem():
    """build/elements.py, the one reader of which massing element a room stands in. A LEAF:
    it imports nothing from build/, so loading it here closes no cycle (WP-11.9)."""
    global _ELEM
    if _ELEM is None:
        _ELEM = _mod("elements", os.path.join(ROOT, "build", "elements.py"))
    return _ELEM


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
        # WP-11.3: the packer is build/furniture.py::pack_against_walls now, moved there
        # whole so the furniture pass and this one cannot drift. Every comment WP-7.2 and
        # WP-7.4 wrote about why it is shaped as it is went with the code; this call must
        # produce BYTE-IDENTICAL output, and tests/test_furniture_pass.py holds it to that
        # over all sixteen plans.
        entries = []
        for f in fixtures:
            spec = _furniture_for(r["type"], f, C)
            if not spec:
                entries.append({"emit": {"item": f, "unplaced": {
                    "reason": f"rooms/{r['type']}.json lists no furniture item for '{f}', so "
                              f"this corpus does not know how big it is"}}})
                continue
            entries.append({"spec": spec})
        layout, _placed = _furn().pack_against_walls(rect, r["id"], occupied, entries)
        if layout:
            r["fixture_layout"] = layout
            report["fixtures_placed"] += sum(1 for f in layout if "unplaced" not in f)
            report["fixtures_unplaced"] += sum(1 for f in layout if "unplaced" in f)



def furniture_pass(level_rooms, C, report, occupied=None, stair=None, level_index=0, breasts=None):
    """Arrange the DRY rooms' furniture, after the openings, the stair and the fixtures.

    WP-11.3, on OQ 92's ruling. `fixture_pass` owns the wet and service rooms and reads the
    plan record's own `fixtures` list; this owns everything else and reads the room CATALOGUE's
    `furniture` array. The gate is the exact complement of the fixture gate, so no room gets
    two layouts drawn over each other -- the butler's pantry and the kitchen are `service` and
    stay with the fixtures, and the four items `rooms/kitchen.json` carries that no fixture
    list names are reported as not drawn rather than left to be noticed.

    The rules are furniture/grammar.json's and `build/furniture.py` executes them. Every one
    declares a grade there (the census is that file's, and build/check_furniture.py prints it
    every run). Three rules the corpus states in prose are named in that file as STATED AND
    NOT EXECUTED, which is where OQ 92 drew the line -- "seating that makes a group rather
    than a line" needs a fact no record carries, and inventing it would be the confident
    nonsense this program exists to remove.

    `breasts` (WP-13.6) is `threshold.hearth_pass`'s `breasts` list for the whole plan; each
    room is handed ITS OWN rows on its own level, because `furniture.py` is a leaf and may
    read no sibling, and two of its rules -- flanking the breast, the facing pair astride the
    hearth's axis -- read a breast the pass DREW and refuse where there is none.

    THIS PASS NEVER WRITES A DIMENSION. docs/model.md carries the ruling and the direction of
    authority: a room's size comes from its programme and its band, and the furniture is
    arranged into the room as given. tests/test_furniture_pass.py asserts it."""
    occupied = occupied if occupied is not None else {}
    F = _furn()
    for r in level_rooms:
        rect = _rect(r)
        if not rect:
            continue
        rt = C["rooms"].get(r["type"]) or {}
        fc = rt.get("function_class")
        if fc in ("sanitary", "service"):
            # fixture_pass owns these. What it does NOT place in them is counted, so a
            # kitchen island missing from the sheet is a number rather than a silence.
            drawn = {f.get("item") for f in (r.get("fixture_layout") or [])}
            for it in (rt.get("furniture") or []):
                if it["item"] not in drawn and not F.drawable(it):
                    report["furniture_not_reached"] = report.get("furniture_not_reached", 0) + 1
            continue
        if not (rt.get("furniture") or []):
            continue
        blocked = [(f["x_ft"], f["y_ft"], f["width_ft"], f["depth_ft"])
                   for f in (r.get("fixture_layout") or [])
                   if not f.get("unplaced") and f.get("x_ft") is not None]
        if stair and stair.get("level") == level_index and stair.get("well") \
                and stair.get("room") == r["id"]:
            wl = stair["well"]
            blocked.append((wl["x_ft"], wl["y_ft"], wl["width_ft"], wl["depth_ft"]))
        mine = [b for b in (breasts or [])
                if b.get("room") == r["id"] and b.get("level") == level_index]
        layout, skipped = F.arrange_room(r, rt, rect, occupied, blocked, breasts=mine)
        if layout:
            r["furniture_layout"] = layout
            report["furniture_placed"] += sum(1 for f in layout if "unplaced" not in f)
            report["furniture_unplaced"] += sum(1 for f in layout if "unplaced" in f)
        for rule_id, n in skipped.items():
            report["furniture_skipped"][rule_id] = report["furniture_skipped"].get(rule_id, 0) + n

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
    # THE WALL ASSEMBLY GOES ONTO THE RECORD, so both renderers read one number instead of
    # each carrying its own. `workbench/app/src/sheet/derive.js` had `WALL_T = 0.75` and
    # `PART_T = 0.42` -- two literals, a house convention rather than a reading, and neither
    # of them any house in this corpus: the Tidewater plan declares solid masonry two wythe,
    # which is 15.5 in of envelope and 4.5 in of partition. `build/assemblies.py` is a LEAF
    # for exactly this reason (see its header, and build/storeys.py's before it): the drawing
    # needs the number and `structure.py` cannot give it without closing an import cycle.
    if W and H:
        fp["wall"] = _mod("assemblies", os.path.join(ROOT, "build", "assemblies.py")) \
            .wall_thickness(plan)
    report = {"placed": 0, "unplaced": [], "offset": [], "axis": [],
              "windows_placed": 0, "windows_unplaced": 0,
              "fixtures_placed": 0, "fixtures_unplaced": 0,
              "furniture_placed": 0, "furniture_unplaced": 0, "furniture_skipped": {},
              "threshold_steps": 0, "threshold_unplaced": 0,
              "stacks_placed": 0, "stacks_unplaced": 0,
              "appendages_placed": 0, "appendages_unplaced": 0}
    if not W or not H:
        report["note"] = ("no footprint on this record — openings are placed against the "
                          "block the solver produced, and this plan has not been placed")
        plan["opening_report"] = report
        return plan
    # WP-11.10. THE APPENDAGE PASS RUNS BEFORE THE LEVEL LOOP, AND THAT IS FORCED RATHER THAN
    # TIDY: `_place_interior` is the first pass inside it, so a terrace derived afterwards
    # could never seat the door it exists for. `entrance_pass` runs LAST for the opposite
    # reason -- it reads placed doors. Nothing here touches a room's `geometry`, so every
    # placement in this corpus is byte-identical across the package; what moves is the
    # openings on the five plans that declare a terrace, which is the deliverable.
    apx = _appd().appendage_pass(plan, C["rooms"], report,
                                 _elem().bounds_index, _elem().boundary_walls)
    # `envelopes` IS THE ELEMENT MAP, AND THE MERGE KEEPS MAIN'S SPELLING OF IT. Both Phase 11s
    # threaded each room's own element down to these two passes -- this branch as a
    # `bounds_index` of `(x, y, W, H)` per level, main as `envelopes(plan)` of `(x0, y0, x1, y1)`
    # plan-wide. Main's is the one `plan_check` reuses ("layer 1's own map, not a second spelling
    # of the block-tag join"), so it is the one kept; keeping both would have been the third
    # spelling of the join, which is the defect this whole layer is about.
    envs = envelopes(plan)
    # WP-13.2. THE FIRE AND ITS STACK ARE PLACED BEFORE THE WINDOWS, because a sash was being
    # seated dead centre in the chimney breast: the breast's centre (`hearths.breast`), a lone
    # window's position (`_place_windows`, `(k+1)/(n+1)` for n = 1) and the flue axis all
    # default to the room's mid-wall, so on the shipped Tidewater record the dining and
    # library sashes were drawn 100% inside their own breasts and the west stack overlapped a
    # window by 0.79 ft. `hearth_pass` reads the placed rooms and nothing this loop writes, so
    # it can run first; `_place_windows` then reserves each drawn breast's run and each stack's
    # run before it seats a sash, exactly as it seats one beside a door. The STOOP still runs
    # last (below), because it reads the placed exterior doors.
    he = _thresh().hearth_pass(plan, C, report)
    # WP-16.6. THE WALL BETWEEN TWO WINDOWS, AND THE STOREY ABOVE ON THE STOREY BELOW (R5, R5a,
    # R5b, R6, R6a). One reading of the pier per house (`window_pier.rule`, the style's), the
    # centre the entrance front is seated out from (the entrance door's axis, read off the ground
    # storey's seated doors), and each storey's seated openings handed to the storey above, which
    # is why the levels are walked in their record order with the storey below already done.
    pier = _wpier().rule(plan["style"]) if plan.get("style") else None
    report["window_pier"] = _wpier().words(pier)
    centres, below_by_level = None, {}
    holds = []
    for _li, lv in enumerate(plan["levels"]):
        idx = lv.get("index", _li)
        rooms = [r for r in lv["rooms"]]
        occupied = {}
        _place_interior(rooms, occupied, report,
                        appendages=apx.get(idx) or {})
        _place_exterior(rooms, occupied, W, H, C, report, envs,
                        hearths=he, level_index=idx)
        if centres is None and idx == 0:
            centres, why = window_centres(plan, rooms, W, H, envs)
            # where the entrance front is seated out from, or why it is its own face's centre
            report["window_centre"] = [{"wall": k[0], "across_ft": k[1], "along_ft": round(v[0], 3),
                                        "source": v[1]} for k, v in centres.items()] or why
        dc = _reserve_doorcase(plan, rooms, W, H, envs, report, idx)
        # THE STOREY BELOW, where it is placed: a storey whose level below was not walked before
        # it is aligned to nothing, and says so, rather than reading as a storey with no
        # opening below it (R6a is a fact about the house; this would be one about the loop).
        below = None
        if idx > 0:
            below = below_by_level.get(idx - 1)
            if below is None:
                report.setdefault("window_alignment_unjudged", []).append(
                    {"level": idx, "why": f"level {idx - 1} is not placed before level {idx}, so "
                                          f"no window on it is aligned to the storey below"})
        _place_windows(rooms, occupied, W, H, report, envs,
                       hearths=he, level_index=idx, doorcase=dc,
                       pier=pier, centres=centres or {}, below=below)
        below_by_level[idx] = opening_axes(rooms, W, H, envs)
        fixture_pass(rooms, C, report, occupied)
        holds.append((rooms, occupied))
    stair = stair_pass(plan, C, report)
    if stair:
        plan["stair"] = stair
    # WP-11.3. The furniture runs in a SECOND loop, after the stair, and that is not tidiness:
    # `stair_pass` takes the whole plan and runs once after the level loop, so a furniture pass
    # inside that loop could not see the stair and would arrange a stair hall's chairs through
    # its own flights. Running here also leaves every pass before it untouched, which is what
    # keeps the fixture layouts and the placement byte-identical -- tests/test_furniture_drawn.py
    # pins its drawn counts as an EQUALITY over all sixteen plans and re-solves to get them.
    for i, (rooms, occupied) in enumerate(holds):
        # WP-13.6: the hearth pass ran above the level loop, so its drawn breasts are known here
        # and the furniture that the record seats beside or astride a fire can read them.
        #
        # `level_index` IS THE RECORD'S OWN `index` AND NOT THE LOOP POSITION, because
        # `threshold.hearth_pass` writes `{"level": lv.get("index")}` on every breast and
        # `_place_windows` above already takes it that way. The one other reader of this
        # argument is the stair well, and `stair_pass` writes a LITERAL `level: 0` meaning the
        # ground level -- two meanings in one argument, which coincide because every level of
        # all sixteen plans has `index` equal to its position. Measured, and
        # tests/test_furniture_grammar.py asserts that premise, so the day a record states
        # otherwise (a cellar at `index: -1` is what the plan schema documents) the suite says
        # so rather than the well quietly ceasing to be blocked.
        furniture_pass(rooms, C, report, occupied, stair=stair,
                       level_index=plan["levels"][i].get("index", i), breasts=he.get("breasts"))
    # WP-11.4. The stoop is PLAN-level and runs last, after every room-level pass, because it
    # reads the placed exterior doors and writes to no room. (The stacks ran here too until
    # WP-13.2 moved them above the level loop so the windows could be seated clear of them;
    # they read placed rooms only, so nothing they see is written by the loop.)
    th = _thresh().entrance_pass(plan, C, report)
    # counted from the records themselves rather than incremented inside the passes: a
    # counter a pass forgets to bump on an early return is a silence wearing a number, and
    # the two passes have EIGHT early returns between them -- two for a kit or an entrance
    # face the record does not give, six for a hearth the record does not locate.
    report["threshold_steps"] = len(th["steps"])
    report["threshold_unplaced"] = len(th["unplaced"])
    report["stacks_placed"] = len(he["stacks"])
    report["stacks_unplaced"] = len([u for u in he["unplaced"] if "hearth_index" not in u])
    # a breast the placement refused is a fire NOT DRAWN, counted here beside the windows it
    # refused so no surface can read the plan as having every fire it states
    report["hearths_refused"] = len([b for b in he.get("breasts") or [] if not b.get("drawn")])
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
