#!/usr/bin/env python3
"""axis.py — the centre line, the bay a door stands in, and the mirror about it (WP-11.3).

`build/plan_check.py` says it in its own comment: *"There is no axis vocabulary anywhere in this
codebase."* This file is that vocabulary, in ONE place, read by the critic and by both engines.

What it is for. `docs/reports/tidewater-layout-diagnosis-2026-09-04.md` B1: the sheet's "centre
passage" was the whole WEST bay of a six-bay house, and the one executable rule the corpus has
about a passage — its width as a share of the facade, 0.18 to 0.27 — PASSED it, at 11/60 = 0.183,
because that rule measures the passage's WIDTH and not its PLACE. Nothing anywhere could see that
a centre passage was in an end bay, that a front door was in no middle bay, or that a six-bay
front has no middle bay to put one in.

THE TOLERANCE, AND ITS STANDING. Half a bay module for the passage's centreline; NONE for the
door's bay. Ruled by Lucas on 4 September 2026 and **editorial**: no source states it. It is
chosen so that the period's own *"slightly off-center"* passages are admitted — Westover's and
Wilton's, where the off-centre passage makes one pair of rooms larger than the other, which every
survey of those houses records as a deliberate asymmetry — and a passage in an end bay is not. The
door's bay carries no tolerance because a door is in a bay or it is not.

EVERY FUNCTION HERE RETURNS COULD NOT EVALUATE RATHER THAN A ZERO. A plan whose passage reaches
the boundary at only one end has no through-axis, and a house with an even bay count has no middle
bay: in both cases the question does not arise, and the corpus's fourth state is what says so. A
zero here would read as "on the axis" and "in the centre bay", which are the two claims this file
exists to stop anyone making by accident.
"""
from __future__ import annotations

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The entrance front's default. `context.entrance_faces` states it per plan; south is the
# convention every renderer in this tree already draws to (x east, y north, origin at the
# building's south-west corner).
DEFAULT_FRONT = "S"

# The passage's centreline may sit this far from the footprint's, in bay modules. Editorial,
# ruled 4 Sep 2026, and marked as judgment wherever it is reported. See the module docstring.
CENTRE_TOL_BAYS = 0.5


def front_of(plan):
    return ((plan.get("context") or {}).get("entrance_faces") or DEFAULT_FRONT).upper()


def axis_runs_x(front):
    """The axis of a house entered on its south or north front runs in X: the centre line is a
    constant x, and everything mirrors left to right about it."""
    return front in ("S", "N")


def footprint_centre(plan):
    """The centre of the MAIN BLOCK, and that qualifier matters on a multi-element house: a
    dependency's rooms sit outside `footprint.width_ft`, and a centre line taken over the built
    extent would move with the wing. `geometry_report.multi_element` names the layers that read
    the main block as the whole building AND SHOULD NOT (six at WP-10.1, two after WP-11.6's
    layers 1-4); this one reads it ON PURPOSE and is not in that list. The count is deliberately
    not repeated here -- it fell twice while this sentence said six."""
    fp = plan.get("footprint") or {}
    w, d = fp.get("width_ft"), fp.get("depth_ft")
    if w is None or d is None:
        return None
    return {"x_ft": w / 2.0, "y_ft": d / 2.0}


def bay_of(pos_ft, plan):
    """Which bay a position on the entrance front stands in, 0-based from the west, or None
    where the footprint does not state a bay grid."""
    fp = plan.get("footprint") or {}
    bay, bays = fp.get("bay_module_ft"), fp.get("bays")
    if not bay or not bays or pos_ft is None:
        return None
    i = int(pos_ft // bay)
    return max(0, min(int(bays) - 1, i))


def centre_bay(plan):
    """The index of the middle bay, or None where there is not one.

    An EVEN bay count has no middle bay, and that is the finding rather than an error: a
    five-bay Georgian's one non-negotiable move is the door in the centre with two windows
    either side, and six bays cannot carry it. WP-11.2 made the placer keep an odd count where
    the diagram asks for one; this says what to do when it could not."""
    bays = (plan.get("footprint") or {}).get("bays")
    if not bays:
        return None
    bays = int(bays)
    if bays % 2 == 0:
        return None
    return (bays - 1) // 2


def through_axis(room):
    """The pair of opposite walls a circulation room reaches with a placed exterior opening,
    or None. Copied in SPIRIT from `plan_check`'s `_reaches_outside` and deliberately not in
    code: that one asks whether you can get OUT (it follows a door into a porch that has its
    own exterior door), which is a question about walking, and this asks whether the room
    itself spans the block, which is a question about geometry."""
    walls = set()
    for d in (room.get("doors") or []):
        if d.get("to") == "exterior" and not d.get("unplaced") and d.get("wall"):
            walls.add(d["wall"])
    for w in (room.get("windows") or []):
        if not w.get("unplaced") and w.get("wall"):
            walls.add(w["wall"])
    for a, b in (("N", "S"), ("E", "W")):
        if a in walls and b in walls:
            return (a, b)
    return None


def spine(plan, level=0, C=None):
    """The circulation room this house is organised on, and where its centre line falls.

    Returns a dict with `room`, `centre_ft`, `off_ft`, `tol_ft` and `verdict`, or a dict whose
    `verdict` is `could-not-evaluate` and whose `why` says which of the three reasons applies:
    no placed circulation room, no footprint, or no room spanning the block."""
    fp = plan.get("footprint") or {}
    centre = footprint_centre(plan)
    bay = fp.get("bay_module_ft")
    if centre is None or not bay:
        return {"verdict": "could-not-evaluate",
                "why": "the placement states no footprint with a bay module"}
    runs_x = axis_runs_x(front_of(plan))
    best = None
    for lv in plan.get("levels", []):
        if (lv.get("index") or 0) != level:
            continue
        for r in lv.get("rooms", []):
            g = r.get("geometry")
            if not g:
                continue
            if C is not None:
                fc = ((C.get("rooms") or {}).get(r.get("type")) or {}).get("function_class")
                if fc != "circulation":
                    continue
            elif "passage" not in (r.get("type") or ""):
                continue
            if not through_axis(r):
                continue
            # the longest spanning circulation room is the spine where a house has two
            extent = g["depth_ft"] if runs_x else g["width_ft"]
            if best is None or extent > best[0]:
                cl = g["x_ft"] + g["width_ft"] / 2.0 if runs_x else g["y_ft"] + g["depth_ft"] / 2.0
                best = (extent, r, cl)
    if best is None:
        return {"verdict": "could-not-evaluate",
                "why": "no placed circulation room reaches the boundary at both ends, so the "
                       "house has no through-axis to be off"}
    _, room, cl = best
    want = centre["x_ft"] if runs_x else centre["y_ft"]
    off = abs(cl - want)
    tol = bay * CENTRE_TOL_BAYS
    return {"verdict": "on-centre" if off <= tol else "off-centre",
            "room": room["id"], "name": room.get("name") or room["id"],
            "centre_ft": round(cl, 2), "footprint_centre_ft": round(want, 2),
            "off_ft": round(off, 2), "tol_ft": round(tol, 2),
            "tol_basis": "half a bay module — editorial, ruled 4 Sep 2026, no source states it"}


def front_openings(plan, level=0):
    """Every placed opening on the entrance front of one level, west to east.

    An opening the placement could not place is NOT here and is counted separately: the
    elevation shows what was drawn, and a declared window that is not on the wall is not on the
    facade. That count is the sheet's `windows` disclosure (WP-11.1) and this returns it so a
    caller cannot mistake a short list for a sparse facade."""
    front = front_of(plan)
    placed, unplaced = [], 0
    for lv in plan.get("levels", []):
        if (lv.get("index") or 0) != level:
            continue
        for r in lv.get("rooms", []):
            for w in (r.get("windows") or []):
                if (w.get("wall") or "").upper() != front:
                    continue
                if w.get("unplaced"):
                    unplaced += int(w.get("count") or 1)
                    continue
                for x in (w.get("positions_ft") or []):
                    placed.append({"room": r["id"], "kind": "window", "pos_ft": round(x, 3),
                                   "width_ft": w.get("width_ft")})
            for d in (r.get("doors") or []):
                if d.get("to") != "exterior" or d.get("unplaced"):
                    continue
                if (d.get("wall") or "").upper() != front or d.get("position_ft") is None:
                    continue
                placed.append({"room": r["id"], "kind": "door",
                               "pos_ft": round(d["position_ft"], 3),
                               "width_ft": d.get("width_ft")})
    placed.sort(key=lambda o: o["pos_ft"])
    return {"front": front, "openings": placed, "declared_but_unplaced": unplaced}


def door_bay(plan):
    """Which bay the front door stands in, and which bay is the middle one.

    `verdict` is `in-the-centre-bay`, `off-the-centre-bay`, or `could-not-evaluate` with a
    reason — an even bay count being the reason worth reading, because it means the house has
    no middle bay for any door to be in."""
    fo = front_openings(plan, 0)
    doors = [o for o in fo["openings"] if o["kind"] == "door"]
    if not doors:
        return {"verdict": "could-not-evaluate",
                "why": f'no exterior door is placed on the {fo["front"]} front'}
    mid = centre_bay(plan)
    bays = (plan.get("footprint") or {}).get("bays")
    if mid is None:
        return {"verdict": "could-not-evaluate", "bays": bays,
                "why": f'{bays} bays is an even count and has no middle bay, so no door can '
                       f'stand in one'}
    # the widest door on the front is the front door where a plan places more than one
    door = max(doors, key=lambda o: (o.get("width_ft") or 0))
    b = bay_of(door["pos_ft"], plan)
    return {"verdict": "in-the-centre-bay" if b == mid else "off-the-centre-bay",
            "bay": b, "centre_bay": mid, "bays": bays, "room": door["room"],
            "position_ft": door["pos_ft"]}


def mirror(plan, level=0, tol_ft=1.0):
    """How much of the entrance front is mirrored about the footprint's centre line.

    `massings/catalog.json`'s `four-over-four` says *"Facade symmetry is a hard constraint, not
    a preference"* and no reader existed. This counts, for one level, how many placed front
    openings have a partner reflected about the centre within `tol_ft`, and returns the
    unmatched ones by position so a finding can name them."""
    centre = footprint_centre(plan)
    if centre is None:
        return {"verdict": "could-not-evaluate", "why": "the placement states no footprint"}
    if not axis_runs_x(front_of(plan)):
        return {"verdict": "could-not-evaluate",
                "why": "the entrance front is a gable end; the mirror runs the other way and "
                       "this reader has not been shown to be right about that case"}
    fo = front_openings(plan, level)
    xs = [o["pos_ft"] for o in fo["openings"]]
    if not xs:
        return {"verdict": "could-not-evaluate",
                "why": f'nothing is placed on the {fo["front"]} front of this level'
                       + (f' ({fo["declared_but_unplaced"]} declared unit(s) not drawn)'
                          if fo["declared_but_unplaced"] else "")}
    cx = centre["x_ft"]
    unmatched = []
    for o in fo["openings"]:
        want = 2 * cx - o["pos_ft"]
        if not any(abs(x - want) <= tol_ft for x in xs):
            unmatched.append(o)
    return {"verdict": "mirrored" if not unmatched else "not-mirrored",
            "openings": len(xs), "unmatched": unmatched,
            "declared_but_unplaced": fo["declared_but_unplaced"],
            "centre_ft": round(cx, 2), "tol_ft": tol_ft}


def alignment(plan, tol_ft=1.0):
    """Whether each opening on an upper storey's entrance front stands over one below.

    `massings/catalog.json`: *"Window bays must align vertically; a misaligned upper window is
    a structural admission that the plan is not really Georgian."* Authored, and read by
    nothing — not by the critic, not by either engine, not by the sheet."""
    ground = front_openings(plan, 0)
    if not ground["openings"]:
        return {"verdict": "could-not-evaluate",
                "why": "nothing is placed on the ground storey's entrance front, so there is "
                       "no rhythm for an upper opening to stand over"}
    gx = [o["pos_ft"] for o in ground["openings"]]
    rows = []
    for lv in plan.get("levels", []):
        idx = lv.get("index") or 0
        if idx == 0:
            continue
        up = front_openings(plan, idx)
        over = [o for o in up["openings"] if any(abs(o["pos_ft"] - x) <= tol_ft for x in gx)]
        rows.append({"level": lv.get("id"), "index": idx,
                     "openings": len(up["openings"]), "aligned": len(over),
                     "unaligned": [o for o in up["openings"] if o not in over],
                     "declared_but_unplaced": up["declared_but_unplaced"]})
    if not rows:
        return {"verdict": "could-not-evaluate", "why": "this plan has one storey"}
    bad = sum(len(r["unaligned"]) for r in rows)
    return {"verdict": "aligned" if not bad else "not-aligned", "levels": rows,
            "unaligned": bad, "tol_ft": tol_ft}


def report(plan, C=None):
    """Everything above, for one placed plan — the shape a critic layer and a sheet both read."""
    return {"front": front_of(plan), "centre": footprint_centre(plan),
            "spine": spine(plan, 0, C), "door": door_bay(plan),
            "mirror": mirror(plan, 0), "alignment": alignment(plan)}
