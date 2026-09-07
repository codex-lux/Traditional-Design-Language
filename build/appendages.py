#!/usr/bin/env python3
"""appendages.py -- the terrace at grade (WP-11.10).

The last item of the B line. `rooms/terrace.json` is the only record in the corpus with
`void.within_footprint: false`, and its own note says leaving it out of placement "is the
right answer rather than a limitation". It is -- about the BLOCK. A terrace takes no
rectangle in the footprint, is not in the heated envelope, and the building is the same
shape without it. What the note could not know is that the corpus has since grown a second
place to put an at-grade thing: `plan.threshold` (WP-11.4), a plan-level record derived
after the solve, drawn outside the block by both renderers, read by no structural layer.
A terrace belongs there, and not in `footprint.blocks`.

RULED 7 Sep 2026, and the ruling is what makes this package small. An at-grade unroofed
appendage is NOT a massing element. Consequences, each of them a thing this file does not do:
it writes no `block` tag, so `geometry.py`'s CP refusal (which keys on the tag, not on
`footprint.blocks`) never fires and no plan trades its proof for a search; it leaves
`room.geometry` ABSENT, so `structure.wall_lines` (which filters on `geometry`),
`plan_check`'s `rooms_unplaced` (which filters on `takes_a_rectangle`) and
`geometry._record_prep` (which filters on `is_placed`) are all blind to it BY CONSTRUCTION
and WP-11.9's six taught layers are not reopened; and it asks `export_ifc` and the roof for
nothing, because a terrace has no walls, no storey and no roof plane.

The cost of that ruling, stated because it is real: the drawn rectangle this file writes is
never held against the room's own band, because the drawn layer reads `room.geometry` and
there is none. `oq/an-at-grade-appendage-is-drawn-and-not-judged`.

A LEAF, on `build/stacking.py`'s precedent and for the same mechanical reason: this runs
inside `openings.place()`, `geometry.py` calls that, and `structure.py` loads `geometry.py`,
so a sibling import here closes a cycle. What it needs from `build/elements.py` -- which
massing element a room stands in, and which of a room's faces lie on that element's boundary
-- is PASSED IN, exactly as `stacking.multi_level_disclosure` takes `is_placed`.

IT RUNS FIRST, AND THAT IS FORCED RATHER THAN TIDY. `_place_interior` is the first pass in
`place()`'s level loop, so an appendage derived after it can never seat the door it exists
for. `entrance_pass` runs last for the opposite reason -- it READS placed doors.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}
WALLS = ("N", "S", "E", "W")

# Every reason this pass can decline, spelled once. A refusal outside this set is a bug:
# `check_appendages`-style totality is asserted in tests/test_appendages.py, on
# build/construction_vocabulary.py's closed-table precedent.
REFUSALS = {
    "not-an-appendage":
        "this room is not an at-grade appendage: its own record does not put it outside the "
        "block",
    "roofed":
        "the record says this appendage is ROOFED, which makes it a mass with a roof over it "
        "rather than a floor at grade; a roofed appended mass is a massing element and this "
        "pass will not place one (oq/the-proving-engine-cannot-place-a-second-massing-element)",
    "not-on-the-ground":
        "an at-grade appendage stands on the ground and this one is declared above it",
    "no-door":
        "the record declares no door from this appendage to any room, so nothing says which "
        "wall it hangs on",
    "served-room-not-placed":
        "the room this appendage opens to has no rectangle, so it has no face to hang on",
    "no-face-both-readings-admit":
        "the appendage's own `exterior_walls` do not name one face, read as free faces AND as "
        "the side of the house it stands on, that the placement also put on the outside",
    "no-depth":
        "the record states no width for this appendage, and a depth is not a band midpoint",
    "no-run":
        "the record states no length for this appendage",
}


# ------------------------------------------------------------------ the readings

def is_at_grade_appendage(rtype, rooms):
    """An outdoor room whose own record puts it OUTSIDE the block. Today: `terrace`, alone.

    `void.within_footprint` is the field OQ 55 authored for exactly this question and the
    only one that answers it. A room with no `void` block at all defaults to
    `within_footprint: false` in `geometry.void_spec`, and that default is deliberately NOT
    read as "appendage" here: the default means nobody has judged the room, and promoting an
    unjudged room to a drawn rectangle outside the house is the same silent promotion OQ 55
    refused in the other direction."""
    r = (rooms or {}).get(rtype) or {}
    if r.get("function_class") != "outdoor":
        return False
    v = r.get("void")
    return isinstance(v, dict) and v.get("within_footprint") is False


def served_face(appendage, served_rooms_boundaries):
    """Which face of the house this appendage hangs on, or None where the record does not say.

    THE RECORD MEANS TWO DIFFERENT THINGS BY `exterior_walls` ON AN OUTDOOR ROOM, and the
    figure taken is the INTERSECTION of the two readings rather than either of them. Measured
    over the six terrace records in the corpus: `tidewater-georgian-careful`'s terrace declares
    E, N and S, which can only be *the faces that are free* (a rectangle cannot be attached on
    three sides); `good-02`, `good-04` and `good-07` each declare exactly one, which reads much
    more naturally as *the side of the house the terrace is on*. Neither reading resolves all
    six on its own -- the free-face reading turns one declared wall into three candidates, and
    the side-of-the-house reading turns three declared walls into three.

    Read as free faces, the served face is `OPPOSITE(f)` for any `f` the record does NOT
    declare. Read as the side of the house, it is a wall the record DOES declare. Both admit a
    wall `w` exactly when `w` is declared and `OPPOSITE(w)` is not -- one line, and it says
    something true either way: *a face whose opposite is also free cannot be the one against
    the house, and a face nobody declared is not a face the record put outside.*

    That is WP-11.4's rule one layer up -- three statements of one stoop depth, "the figure is
    the intersection and never an average" -- and it is this corpus's standing answer where two
    records disagree: take what both admit, or take nothing.

    The candidate must ALSO be a face the placement actually put on the outside of the served
    room's own massing element (WP-11.9 ruling 4, via `elements.boundary_walls`, passed in).
    Unique after all three, or None -- and None is UNJUDGED, never a plausible guess.
    """
    declared = {w for w in (appendage.get("exterior_walls") or []) if w in WALLS}
    both = {w for w in declared if OPPOSITE[w] not in declared}
    if not both:
        return None
    outside = set()
    for b in served_rooms_boundaries:
        outside |= set(b)
    cands = sorted(both & outside)
    return cands[0] if len(cands) == 1 else None


def rect_for(face, run_lo, run_hi, elem_lo, elem_hi, elem_edge, depth_ft, run_ft):
    """The appendage's rectangle, in the plan's own `(x, y, width, depth)` feet.

    `depth_ft` is the record's `width_ft` and `run_ft` its `length_ft` -- which of the two is
    the depth is stated by the record and not chosen here; see `figures_for`. The run is
    centred on the served rooms' own extent and slid to stay within the element's face; where
    the record asks for more run than the face has, it is clamped and the clamp is disclosed.
    """
    run = min(run_ft, elem_hi - elem_lo)
    mid = (run_lo + run_hi) / 2.0
    lo = mid - run / 2.0
    lo = max(elem_lo, min(lo, elem_hi - run))
    if face == "E":
        return (elem_edge, lo, depth_ft, run)
    if face == "W":
        return (elem_edge - depth_ft, lo, depth_ft, run)
    if face == "N":
        return (lo, elem_edge, run, depth_ft)
    return (lo, elem_edge - depth_ft, run, depth_ft)


def figures_for(appendage, depth_ft, run_ft, run_drawn):
    """Each figure beside the rule that chose it and that rule's grade (WP-11.3's vocabulary).

    Both are READINGS: `rooms/terrace.json`'s own `critical_dimension` names DEPTH as the
    dimension that matters and gives its floor, and its bands are `width_ft [10, 30]` against
    `length_ft [12, 40]` -- so the record itself says which of the two figures is measured out
    from the wall. Nothing here is a band end and nothing is a midpoint."""
    out = {
        "depth_ft": {"value": round(depth_ft, 3), "rule": "ap-the-record-says-which-is-depth",
                     "grade": "reading"},
        "run_ft": {"value": round(run_drawn, 3), "rule": "ap-the-record-says-which-is-depth",
                   "grade": "reading"},
    }
    if run_drawn < run_ft - 1e-6:
        out["run_ft"]["clamped"] = {"need": round(run_ft, 3), "have": round(run_drawn, 3),
                                    "why": "the element's own face is shorter than the run the "
                                           "record declares"}
    return out


RULES = [
    {"id": "ap-hangs-on-the-room-it-opens-to", "grade": "reading",
     "statement": "An at-grade appendage hangs on a room it declares a door to, and on no "
                  "other. Where it declares none, it is not placed.",
     "basis": "rooms/terrace.json adjacency.should_adjoin[breakfast-room].why: \"The summer "
              "extension of the informal eating room, and the reason for a door.\" The record "
              "makes the door the relation, so the door is what says which room the terrace "
              "is appended to."},
    {"id": "ap-the-face-both-readings-admit", "grade": "reading",
     "statement": "The face is a wall the appendage declares exterior whose opposite it does "
                  "not, intersected with the faces the placement put on the outside of the "
                  "served room's own massing element. Unique, or UNJUDGED.",
     "basis": "rooms/terrace.json void.note: \"is appended at grade, and the building would be "
              "the same shape without it.\" Appended at grade is a relation to ONE face of the "
              "house, and `exterior_walls` is the only field on the record that names faces."},
    {"id": "ap-the-record-says-which-is-depth", "grade": "reading",
     "statement": "`width_ft` is the depth measured out from the wall and `length_ft` is the "
                  "run along it; the run is clamped to the element's face and the clamp is "
                  "disclosed.",
     "basis": "rooms/terrace.json dimensions.critical_dimension: \"Depth. A terrace under 10 ft "
              "cannot hold a table and a passage behind the chairs\" -- the record names depth "
              "as the dimension that matters, and its own bands put width_ft [10, 30] against "
              "length_ft [12, 40]."},
]


# ------------------------------------------------------------------ the pass

def appendage_pass(plan, rooms_catalogue, report, bounds_index, boundary_walls):
    """Write `plan["appendages"]` and return `{level_index: {room_id: (x, y, w, h)}}`.

    `bounds_index(plan, level_rooms) -> {room_id: (x, y, W, H)}` and
    `boundary_walls(rect, bounds) -> {wall: (lo, hi)}` are `build/elements.py`'s, passed in
    because this module is a leaf. Nothing else is derived: every figure comes off the record.
    """
    placed, unplaced = [], []
    rects = {}
    for li, lv in enumerate(plan.get("levels") or []):
        # THE LEVEL'S OWN index, not its position in the list. `render_plan` and `Sheet.jsx`
        # both match an appendage to a plate by `lv["index"]`, and on every plan in this corpus
        # the two numbers coincide -- keying on the record's own field is what makes the two
        # readers agree by construction rather than by coincidence.
        lvi = lv.get("index", li)
        level_rooms = lv.get("rooms") or []
        idx = {r.get("id"): r for r in level_rooms}
        eb = bounds_index(plan, level_rooms)
        for r in level_rooms:
            if not is_at_grade_appendage(r.get("type"), rooms_catalogue):
                continue
            rec = (rooms_catalogue or {}).get(r.get("type")) or {}
            void = rec.get("void") or {}
            # the NAME is on the record because both renderers draw it and neither may look
            # it up: an appendage has no `room.geometry`, so the label loop that names every
            # other room never reaches it, and a renderer hunting the level list for a name
            # is a second reader of the plan where there should be one.
            entry = {"room": r.get("id"), "type": r.get("type"), "level": lvi,
                     "name": r.get("name") or r.get("id")}

            def _refuse(code, **extra):
                unplaced.append(dict(entry, reason=REFUSALS[code], code=code, **extra))

            if void.get("roofed"):
                _refuse("roofed")
                continue
            if lvi != 0:
                _refuse("not-on-the-ground")
                continue
            serves = [d.get("to") for d in (r.get("doors") or []) if d.get("to")]
            serves = [s for s in serves if s != "exterior"]
            if not serves:
                _refuse("no-door")
                continue
            served = [idx.get(s) for s in serves]
            if any(s is None or not s.get("geometry") for s in served):
                _refuse("served-room-not-placed",
                        serves=[s for s, o in zip(serves, served)
                                if o is None or not o.get("geometry")])
                continue
            bounds = []
            for s in served:
                g = s["geometry"]
                bounds.append(boundary_walls(
                    (g["x_ft"], g["y_ft"], g["width_ft"], g["depth_ft"]),
                    eb.get(s["id"], (0.0, 0.0, 0.0, 0.0))))
            face = served_face(r, bounds)
            if face is None:
                _refuse("no-face-both-readings-admit", serves=serves,
                        declared=sorted(r.get("exterior_walls") or []),
                        outside=sorted({w for b in bounds for w in b}))
                continue
            depth_ft = r.get("width_ft")
            run_ft = r.get("length_ft")
            if not depth_ft:
                _refuse("no-depth", serves=serves)
                continue
            if not run_ft:
                _refuse("no-run", serves=serves)
                continue
            # the served rooms' own extent along that face, and the element's
            runs = [b[face] for b in bounds if face in b]
            run_lo = min(a for a, _ in runs)
            run_hi = max(b for _, b in runs)
            ex, ey, ew, eh = eb.get(served[0]["id"], (0.0, 0.0, 0.0, 0.0))
            if face in ("E", "W"):
                elem_lo, elem_hi = ey, ey + eh
                elem_edge = ex + ew if face == "E" else ex
            else:
                elem_lo, elem_hi = ex, ex + ew
                elem_edge = ey + eh if face == "N" else ey
            rect = rect_for(face, run_lo, run_hi, elem_lo, elem_hi, elem_edge,
                            float(depth_ft), float(run_ft))
            x, y, w, h = (round(v, 3) for v in rect)
            drawn_run = h if face in ("E", "W") else w
            rects.setdefault(lvi, {})[r["id"]] = (x, y, w, h)
            placed.append(dict(
                entry, serves=serves, wall=face, at_grade=True,
                roofed=bool(void.get("roofed")),
                rect={"x_ft": x, "y_ft": y, "width_ft": w, "depth_ft": h},
                figures=figures_for(r, float(depth_ft), float(run_ft), drawn_run),
                rule="ap-the-face-both-readings-admit", grade="reading"))
    plan["appendages"] = {
        "placed": placed, "unplaced": unplaced, "rules": [dict(x) for x in RULES],
        "note": ("An at-grade appendage is drawn outside the block and is NOT a massing "
                 "element: it has no walls, no storey, no roof plane, and it is not in the "
                 "built extent the lot cap is measured on (WP-11.9, ruling 2). It takes no "
                 "rectangle in the footprint, so its drawn size is not held against its own "
                 "band -- oq/an-at-grade-appendage-is-drawn-and-not-judged."
                 if placed or unplaced else "No at-grade appendage on this plan.")}
    if report is not None:
        report["appendages_placed"] = len(placed)
        report["appendages_unplaced"] = len(unplaced)
    return rects


# NO `main()`, AND THAT IS THE HOUSE STYLE FOR A LEAF RATHER THAN AN OVERSIGHT. The first
# version had one, and it loaded `geometry` with a local `spec_from_file_location` --
# `tests/test_modcache.py::test_no_new_by_path_loader_outside_modcache` failed it, which is
# the guard CLAUDE.md's "do not reinstate a local loader" is written down as. Every other leaf
# in `build/` -- `stacking`, `furniture`, `assemblies`, `storeys`, `elements` -- carries no
# CLI for the same reason, and this pass's whole output is on the record already:
# `plan["appendages"]` and `opening_report.appendages_placed` / `appendages_unplaced`.
#     python3 -c "import json,sys; d=json.load(sys.stdin); print(json.dumps(d['appendages'], indent=1))"
# after `python3 build/geometry.py <plan>` reads it, and goes through the cache like everything
# else.
