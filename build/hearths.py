#!/usr/bin/env python3
"""hearths.py — where the fire goes, read from the massing and the room (WP-11.4).

`docs/reports/tidewater-layout-diagnosis-2026-09-04.md` D1: there is no fireplace anywhere in the
plan layer. Not a field on a room, not a thing the placer reserves, not a line on the plate.
`grep -i "hearth|fireplace|chimney"` over `plan_check.py`, `geometry.py`, `geometry_cp.py`,
`compose.py`, `openings.py` and `render_plan.py` finds exactly two hits and both are comments, and
`build/arrangement.py` declares four chimney and firebox measurements NOT_DERIVABLE, one of them on
the ground that *"the plan has no chimney footprint"* -- a reason WP-11.4 had to rewrite, because
it stopped being true while the refusal it justified stayed right.

Meanwhile `massings/catalog.json` says `four-over-four` has `hearth: "gable-end-paired"` and
*"Paired end chimneys serve four fireplaces per floor"*, and `roof.py` and `elevation.py` draw the
stacks. Two records of one house, and the plan under the stacks has no fire in any room — which is
OQ 85's shape (the elevation drew a window where a chimney stands) one layer down.

WHAT THIS FILE DOES AND DOES NOT DECIDE. It reads two things the corpus already states and joins
them; it invents nothing:

  · the MASSING's `hearth`, a closed vocabulary read conservatively — six forms accepted, the
    compound ones ("gable-end-paired or central-stack", "central or none", "interior or end")
    REFUSED by name rather than resolved, because choosing between them is an authoring act;
  · the ROOM's `servicing.heat`, which nineteen room records state in prose — *"One chimneypiece,
    and it is the room's compositional centre"* (drawing room), *"A corner or gable-end fireplace
    with a 30-36 in opening, or none at all: unheated chambers are historically normal and should
    be said out loud"* (bedchamber).

A hearth is AUTHORED on a plan room (`hearth`, plan schema 0.7.0) and never inferred: the corpus
says a room's fire is a decision — the bedchamber record says an unheated chamber is normal and
must be *said out loud* — so a generator that gave every room a fireplace because its type usually
has one would be inventing exactly what that sentence forbids. What this file derives is where a
stated hearth's flue can go, and whether the massing and the record agree.

THE WIDTH IS MORRIS'S OWN RULE, EXECUTED. *Lectures on Architecture* (1734), Lecture VI, RULE II:
*"add the Length, Breadth and Height of the Room together, and extract the Square Root of that Sum,
and half that Root will be the Breadth of your Chimney"* -- `sqrt(L + B + H) / 2` in feet. It is
used ONLY as a fallback, marked `judgment: true`, where neither the record nor the room says
otherwise. It is a London figure in an English treatise and `docs/reports/
wp-9.2-what-the-tradition-actually-does.md` §6 item 6 is explicit that Kerr's dimensions may not be
transplanted into an American vernacular record as though measured; the same caution binds Morris,
and recovering his rule correctly does not weaken it -- an English rule read right is still an
English rule. `bedchamber`'s own *"30-36 in opening"* is the corpus's figure and outranks it. See
the constants below for the provenance, for why the table it replaced was worse at both ends, and
for the one rule (RULE I, and so the DEPTH) that could not be recovered.
"""
from __future__ import annotations

import math
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The massing's `hearth` values this file will act on, and what each says about WHERE a flue can
# stand. Every other value in massings/catalog.json is refused by name below rather than mapped to
# the nearest of these, which is how `massing_bays` reads its own field and for the same reason.
#
#   gable-end-paired  two stacks, one on each gable, serving the rooms either side of them
#   gable-end         one stack per gable end
#   end               a stack on an end wall, interior or exterior not stated by the massing
#   central-stack     one mass at the centre of the block, serving the rooms around it
#   central           the same, where the massing says it that way
#   party-wall        the stack is in the wall shared with the neighbour (a row house)
HEARTH_RULES = {
    "gable-end-paired": {"walls": ("E", "W"), "per_end": 1, "central": False},
    "gable-end": {"walls": ("E", "W"), "per_end": 1, "central": False},
    "end": {"walls": ("E", "W"), "per_end": 1, "central": False},
    "central-stack": {"walls": (), "per_end": 0, "central": True},
    "central": {"walls": (), "per_end": 0, "central": True},
    "party-wall": {"walls": ("E", "W"), "per_end": 1, "central": False},
}

# MORRIS 1734, LECTURE VI: HIS OWN RULE, NOT TWO ROWS OF HIS TABLE.
#
# The first draft carried two anchors off the table -- (12 ft cube, 36 in) and (22 ft, 49 in) --
# and interpolated between them linearly. The table is not the rule: Morris says so himself,
# introducing it as *"a Table of all the foregoing Proportions calculated in the [preceding]
# Manner"*. The rule is recoverable and is a square-root law, so a straight line between two of
# its points is an approximation of a source that did not need approximating.
#
#   RULE II. "To find the Breadth of a Chimney from any given Magnitude of a Room, add the
#   Length, Breadth and Height of the Room together, and extract the Square Root of that Sum,
#   and half that Root will be the Breadth of your Chimney."
#
# In feet: breadth = sqrt(L + B + H) / 2. Evaluated at a 12 ft cube that is sqrt(36)/2 = 3.000 ft
# = 36.00 in, and at a 22 ft cube sqrt(66)/2 = 4.062 ft = 48.74 in -- reproducing both discarded
# anchors, the second to a quarter of an inch. **That agreement is a CONSISTENCY CHECK AND NOT AN
# INDEPENDENT CORROBORATION**: where the two anchors originally came from is not recorded here,
# so a common origin cannot be ruled out and must not be claimed.
#
# PROVENANCE, because it decides what may be built on it. The rule text above is OCR of a scan
# of the 1734 first edition (archive.org
# `bim_eighteenth-century_lectures-on-architecture_morris-robert_1734`), reached through the
# agent proxy. Its LOCATION is corroborated independently: Dean Hawkes, "The Origins of Building
# Science in the Architecture of Eighteenth Century England" (Cloud-Cuckoo-Land 33), reports that
# Lecture VI "concludes with a discourse on the calculation of sizes of Chimnies in relation to
# the dimensions of rooms", summarised in "A Table of Harmonick and Arithmetical Proportions for
# Magnitudes of Rooms and Chimnies by Universal Rules". **NO FACSIMILE PAGE HAS BEEN READ HERE**,
# which is the same standing caution as OQ 7-11 and OQ 18's source half, and it is why every
# figure this file derives still carries `judgment: true`. It is a London figure in an English
# treatise besides, and `docs/reports/wp-9.2-what-the-tradition-actually-does.md` §6 is explicit
# that a treatise dimension may not be transplanted into an American vernacular record as
# measured.
MORRIS_RULE_II = "sqrt(length_ft + breadth_ft + height_ft) / 2, in feet"
MORRIS_CEILING_FT = 9.5   # where a plan states no ceiling height. EDITORIAL, named rather than
                          # written inline, and a plan that states its ceiling never uses it.
                          # MEASURED, because a constant nobody has measured is a constant nobody
                          # can argue with: on an 18 x 20 room, 9.0 ft gives 41.1 in and 11.0 ft
                          # gives 42.0 -- 0.87 in across the whole plausible range, because a
                          # square root flattens it. Small, and not nothing. An earlier version
                          # of this comment said "41.0 vs 42.4", which was neither figure.

# THE DEPTH IS STILL TWO INTERPOLATED ANCHORS AND THE RULE FOR IT COULD NOT BE RECOVERED.
# Morris's RULE III is legible -- "To find the Depth of a Chimney ... add the Breadth and Height
# of [the Chimney] together, take one fourth of that Sum, and it is the Depth of the Chimney" --
# but it needs the chimney's HEIGHT, and RULE I, which gives that, is corrupt in the only text
# reachable from here: it reads "add the Length 1 Bo Height of the Room together". It is a
# TWO-term sum (a three-term one would make Rule I and Rule II the same rule) and which two
# cannot be told. So the depth keeps its anchors, and this comment is the record that the rule
# behind them is UNRECOVERED rather than absent. Both anchors are consistent with Rule III on a
# square opening -- (36+36)/4 = 18.0 and (48.74+48.74)/4 = 24.4 against 24.25 -- which is a
# reading, not a reconstruction of Rule I.
MORRIS_DEPTH = ((12.0, 18.0), (22.0, 24.25))    # (room cube in ft, chimney depth in inches)
# Where a hearth states no width at all, only for DRAWING the breast -- `opening_width_in` is the
# way to get a figure and it says where the figure came from. Every shipped hearth states its
# width, so this fires on nothing today; it is 36.0 because that is Rule II at a 12 ft cube, the
# smallest room Morris's own table bothers to tabulate.
DEFAULT_OPENING_IN = 36.0
JAMB_IN = 8.0                # masonry either side of the opening, making the breast's face


def breast(room, hearth, C=None):
    """The chimney breast as a rectangle in model feet, from a room's PLACED geometry and one
    stated hearth — or None where the room is unplaced.

    `build/arrangement.py` keeps `chimney_breast_projection_or_wall_thickness_in` NOT_DERIVABLE
    and its REASON has changed: it used to say *"no record carries a chimney PLAN dimension"*,
    and there is one now. The refusal stands because the projection is a JUDGMENT -- a judgment
    figure may be drawn and never published as a measurement, which is the standing precedent
    for the chimney's own 22 in. The projection is Morris's own depth column against the room's cube, interpolated
    and marked `judgment` exactly as the opening is — the same London figure with the same
    caution on it.

    The breast stands ON the named wall and projects INTO the room, which is what an interior
    stack does; an exterior stack projects the other way and this file does not model that
    difference, because the massing vocabulary does not state it (`end` says nothing about
    interior or exterior) and guessing would be the invention this layer exists to stop."""
    g = room.get("geometry")
    if not g:
        return None
    w_ft, l_ft = room.get("width_ft"), room.get("length_ft")
    cube = ((w_ft * l_ft) ** 0.5) if (w_ft and l_ft) else \
        ((g["width_ft"] * g["depth_ft"]) ** 0.5)
    (a_ft, a_in), (b_ft, b_in) = MORRIS_DEPTH
    t = max(0.0, min(1.0, (cube - a_ft) / (b_ft - a_ft)))
    depth_ft = (a_in + t * (b_in - a_in)) / 12.0
    opening_in = hearth.get("width_in") or DEFAULT_OPENING_IN
    face_ft = (opening_in + 2 * JAMB_IN) / 12.0
    wall = (hearth.get("wall") or "").upper()
    pos = hearth.get("position_ft")
    if wall in ("E", "W"):
        cy = pos if pos is not None else g["y_ft"] + g["depth_ft"] / 2.0
        y = max(g["y_ft"], min(cy - face_ft / 2.0, g["y_ft"] + g["depth_ft"] - face_ft))
        x = g["x_ft"] if wall == "W" else g["x_ft"] + g["width_ft"] - depth_ft
        return {"x_ft": round(x, 3), "y_ft": round(y, 3), "width_ft": round(depth_ft, 3),
                "depth_ft": round(face_ft, 3), "wall": wall,
                "projection_in": round(depth_ft * 12, 1), "judgment": True}
    if wall in ("N", "S"):
        cx = pos if pos is not None else g["x_ft"] + g["width_ft"] / 2.0
        x = max(g["x_ft"], min(cx - face_ft / 2.0, g["x_ft"] + g["width_ft"] - face_ft))
        y = g["y_ft"] if wall == "S" else g["y_ft"] + g["depth_ft"] - depth_ft
        return {"x_ft": round(x, 3), "y_ft": round(y, 3), "width_ft": round(face_ft, 3),
                "depth_ft": round(depth_ft, 3), "wall": wall,
                "projection_in": round(depth_ft * 12, 1), "judgment": True}
    # `interior` — the dining room's case. The record says which wall it is opposite and this
    # file does not know which of the room's four sides that is, so it is NOT DRAWN and says so
    # rather than being put on a plausible one.
    return {"undrawable": True, "wall": wall,
            "why": "an interior hearth names no side of the room, and putting it on a plausible "
                   "one is the invention this layer exists to stop"}


def massing_hearth(massing):
    """What the massing states about its own hearths, read conservatively.

    Returns {"stated", "readable", "rule"}. `readable` False means the massing said something
    this file may not act on — a compound like *"gable-end-paired or central-stack"* is a real
    statement about a type that admits both, and resolving it here would be choosing on the
    corpus's behalf."""
    stated = (massing or {}).get("hearth")
    out = {"stated": stated, "readable": False, "rule": None}
    if not isinstance(stated, str):
        return out
    key = stated.strip().lower()
    if key in HEARTH_RULES:
        out.update(readable=True, rule=HEARTH_RULES[key])
    return out


def opening_width_in(room_rec, w_ft, l_ft, ceiling_ft=None):
    r"""The fireplace opening, and where the number comes from, said in the return value.

    Order: the ROOM RECORD's own figure if it states one in inches, then Morris's table
    interpolated on the room's cube, and the second is `judgment: true` every time.

    THE FIGURE IS ONLY READ WHERE THE RECORD ADMITS A FIRE, AND THE FIRST DRAFT DID NOT CHECK.
    `rooms/closet.json`'s `servicing.heat` opens *"None required and none wanted"* and then, four
    clauses later, describes a closet ceiling *"drywalled from a stepladder through a 30 in
    opening"* — an air-barrier failure, about a doorway. The bare `(\d{2})\s*in` search took it
    and published **30.0 in at `judgment: false`**, which is a room that wants no heat at all
    stating a measured fireplace opening. A figure lifted out of prose that is about something
    else and published as measured is this corpus's worst sin, and a regex is not competent to
    tell the two apart: `wants_a_hearth` already is, so the gate is its verdict rather than a
    tighter pattern. Only `stated` and `optional` may contribute a figure — of the 60 records,
    that leaves `bedchamber`'s *"30-36 in opening"* as the one and only own-figure in the
    corpus, which is what the module docstring claims and what was not true before this gate."""
    heat = ((room_rec or {}).get("servicing") or {}).get("heat") or ""
    if wants_a_hearth(room_rec)["verdict"] not in ("stated", "optional"):
        heat = ""
    m = re.search(r"(\d{2})\s*[-–]\s*(\d{2})\s*in\b", heat)
    if m:
        lo, hi = float(m.group(1)), float(m.group(2))
        return {"width_in": round((lo + hi) / 2.0, 1), "band_in": [lo, hi],
                "source": "the room record's own servicing.heat", "judgment": False,
                "quote": heat[:160]}
    m = re.search(r"(\d{2})\s*in\b", heat)
    if m:
        return {"width_in": float(m.group(1)),
                "source": "the room record's own servicing.heat", "judgment": False,
                "quote": heat[:160]}
    if not (w_ft and l_ft):
        return {"width_in": None, "source": None, "judgment": True,
                "why": "the room states no dimensions, so even the fallback cannot be computed"}
    # RULE II, EXECUTED, not a line drawn between two of its points. It wants all three of the
    # room's dimensions and the plan states two, so the ceiling comes from the record where it
    # states one and from MORRIS_CEILING_FT where it does not -- which is EDITORIAL and is
    # returned under `ceiling_ft` and `ceiling_assumed` so a reader can see which happened.
    h_ft, assumed = ceiling_ft, False
    if not h_ft:
        h_ft, assumed = MORRIS_CEILING_FT, True
    return {"width_in": round(((w_ft + l_ft + h_ft) ** 0.5) / 2.0 * 12.0, 1),
            "source": "Morris, Lectures on Architecture (1734), Lecture VI, Rule II, executed",
            "rule": MORRIS_RULE_II, "ceiling_ft": h_ft, "ceiling_assumed": assumed,
            "judgment": True,
            "why": "a London figure in an English treatise, used because neither this record "
                   "nor its room type states an opening; no facsimile has been read here and it "
                   "may not be published as measured"}


# The room records speak TWO VOCABULARIES about heat and the split is not by accident: the rooms
# that predate central heating state a fire (`bedchamber`: "A corner or gable-end fireplace with a
# 30-36 in opening"; `centre-passage`: "Historically none. The passage is the unheated buffer
# between two heated rooms"), and the rooms that do not state ductwork (`bedroom`: "over-heated and
# under-cooled by the same duct run"; `breakfast-room`: "Perimeter"). So a Georgian plan built from
# MODERN room types has no room-level statement about its fires at all -- which is a fact about
# this corpus worth knowing before reading a census of `unstated` as a gap in the records.
_FIRE = ("fireplace", "chimneypiece", "hearth", "chimney breast", "chimney piece")
_NO_FIRE = ("historically none", "none of its own", "unheated buffer", "no fireplace")
_OPTIONAL = ("or none", "or not at all", "unheated chambers")


def wants_a_hearth(room_rec):
    """What the ROOM TYPE's own record says about this kind of room having a fire.

    FOUR verdicts, because the records make four statements and collapsing any of them loses
    something the corpus took trouble to say:

      stated    a fire belongs in this room ("One chimneypiece, and it is the room's
                compositional centre")
      optional  a fire is normal AND its absence is normal, and the record says the choice must
                be made out loud -- `bedchamber`: "or none at all: unheated chambers are
                historically normal and should be said out loud rather than quietly given a
                register"
      none      the record positively says this room has no fire of its own -- `centre-passage`:
                "Historically none. The passage is the unheated buffer between two heated rooms
                and that is part of why it stayed a passage"
      unstated  the record does not speak to it, which on a modern room type means it speaks
                about ducts instead

    `none` is the verdict that matters most here and it is the one a two-state reader would have
    lost: "Historically none" carries no fireplace word at all, so a checker looking for one
    would file the centre passage under `unstated` and go looking for a fire the corpus has
    explicitly refused it."""
    heat = ((room_rec or {}).get("servicing") or {}).get("heat") or ""
    if not heat:
        return {"verdict": "unstated", "quote": None}
    low = heat.lower()
    if any(w in low for w in _NO_FIRE):
        return {"verdict": "none", "quote": heat[:200]}
    if not any(w in low for w in _FIRE):
        return {"verdict": "unstated", "quote": heat[:200]}
    if any(w in low for w in _OPTIONAL):
        return {"verdict": "optional", "quote": heat[:200]}
    return {"verdict": "stated", "quote": heat[:200]}


def level_ceiling_ft(level):
    """The level's own stated floor-to-ceiling height, or None.

    IT IS STATED AND THE FIRST DRAFT INVENTED ONE ANYWAY. `plans/tidewater-georgian-careful.json`
    carries `floor_to_ceiling_ft` of 11 on the ground and 10 above, and `opening_width_in` was
    reaching for MORRIS_CEILING_FT on every room of both -- the exact substitution this file
    exists to refuse, committed one function away from the comment refusing it. `build/storeys.py`
    reads the same field and is the precedent for the spelling."""
    return (level or {}).get("floor_to_ceiling_ft")


def flue_walls(plan, massing):
    """Which boundary walls of the main block this massing puts its stacks on, or () for a
    central mass. Returns (rule, why) and refuses a massing it cannot read.

    THREE REASONS TO REFUSE, NOT ONE, AND THE FIRST DRAFT GAVE THE WRONG ONE TO FOURTEEN OF THE
    SIXTEEN PLAN RECORDS IN THIS TREE. It said *"a compound is a statement about a type that
    admits both arrangements"* about plans that state no massing at all — a true sentence about
    a different situation, which is the shape of false claim this project keeps catching in its
    own prose. The three cases are genuinely different to the reader who has to act on them:
    the plan named no massing (author a `massing`), the catalogue's entry states no hearth
    (author the field in `massings/catalog.json`), or the entry states a form this file will not
    resolve (rule on the compound, or add the form). Only the third is about compounds."""
    mh = massing_hearth(massing)
    if mh["rule"] is not None:
        return mh["rule"], None
    if not massing:
        return None, ("this plan names no massing, so there is no statement about where its "
                      "stacks stand — 14 of the 16 plan records in this tree are in that "
                      "position and every massing-gated check is silent on all of them")
    if mh["stated"] is None:
        return None, (f'the massing {massing.get("id")!r} states no `hearth` at all in '
                      f'massings/catalog.json, so it says nothing about where a flue may go')
    return None, (f'the massing states hearth {mh["stated"]!r}, which this file does not read: '
                  f'a compound is a statement about a type that admits BOTH arrangements, and '
                  f'choosing between them here would be authoring on the corpus\'s behalf')


def hearth_report(plan, C):
    """Every room's hearth, what the record states, and whether the massing agrees.

    Three states per room, never two: `stated` (the record carries a hearth), `absent` (the room
    type's record says a fire belongs here and the plan does not state one), and `unjudged` (the
    room type says nothing, or the massing cannot be read). The count of each is published, so a
    check that cannot fire cannot read as a check that passed."""
    massing = (C.get("massings") or {}).get(plan.get("massing") or "") or {}
    rule, why = flue_walls(plan, massing)
    fp = plan.get("footprint") or {}
    W, H = fp.get("width_ft"), fp.get("depth_ft")
    rows, census = [], {"stated": 0, "absent": 0, "declined": 0, "unjudged": 0,
                        "off_the_stack_wall": 0}
    for lv in plan.get("levels", []):
        for r in lv.get("rooms", []):
            rec = (C.get("rooms") or {}).get(r.get("type")) or {}
            want = wants_a_hearth(rec)
            declared = r.get("hearth") or []
            row = {"level": lv.get("id"), "room": r["id"], "name": r.get("name") or r["id"],
                   "type": r.get("type"), "type_says": want["verdict"],
                   "declared": declared, "quote": want.get("quote")}
            if declared:
                row["state"] = "stated"
                census["stated"] += 1
                # What Morris's Rule II would give for this room, beside what the author wrote.
                # REPORTED AND NEVER ENFORCED: the opening is an authored plan fact and the rule
                # is a London figure at one remove, so a checker that convicted an author of
                # disagreeing with it would have the authority backwards.
                row["rule_width_in"] = opening_width_in(
                    rec, r.get("width_ft"), r.get("length_ft"),
                    ceiling_ft=level_ceiling_ft(lv)).get("width_in")
                # does the wall the record names carry a stack on this massing?
                if rule and rule["walls"]:
                    off = [h for h in declared
                           if (h.get("wall") or "").upper() not in rule["walls"]]
                    if off:
                        row["off_the_stack_wall"] = [h.get("wall") for h in off]
                        census["off_the_stack_wall"] += 1
            elif want["verdict"] == "none":
                # The corpus has REFUSED this room a fire of its own. Not unjudged, not absent.
                row["state"] = "declined"
                census["declined"] = census.get("declined", 0) + 1
            elif rule is None or want["verdict"] == "unstated":
                row["state"] = "unjudged"
                row["why"] = why or ("the room type's record does not say whether it has a fire "
                                     "— on a modern room type it states ductwork instead")
                census["unjudged"] += 1
            elif want["verdict"] == "stated":
                row["state"] = "absent"
                census["absent"] += 1
            else:
                row["state"] = "unjudged"
                row["why"] = ("the room type's record says a fire here is optional — "
                              "an unheated room of this kind is historically normal, and the "
                              "record must say which rather than a checker assuming")
                census["unjudged"] += 1
            rows.append(row)
    return {"massing_hearth": massing.get("hearth"), "readable": rule is not None,
            "why": why, "walls": list(rule["walls"]) if rule else None,
            "central": bool(rule and rule["central"]), "rooms": rows, "census": census,
            "footprint": {"width_ft": W, "depth_ft": H}}


def stack_axes(plan, C):
    """Where the flues stand, DERIVED FROM THE PLAN'S OWN STATED HEARTHS where it states any.

    `roof.py` puts a stack on each gable end at the end wall's centre line, from the massing
    alone — a rule about a rectangle, not about the rooms inside it. Where the plan states
    hearths this returns their walls and positions instead, so a stack stands over a fire
    somebody drew. Returns None when the plan states none, which is the signal to `roof.py` to
    keep its own rule and say so rather than invent a fire."""
    axes = []
    for lv in plan.get("levels", []):
        if (lv.get("index") or 0) != 0:
            continue
        for r in lv.get("rooms", []):
            g = r.get("geometry")
            for h in (r.get("hearth") or []):
                wall = (h.get("wall") or "").upper()
                pos = h.get("position_ft")
                if pos is None and g:
                    pos = (g["y_ft"] + g["depth_ft"] / 2.0 if wall in ("E", "W")
                           else g["x_ft"] + g["width_ft"] / 2.0)
                axes.append({"room": r["id"], "wall": wall, "position_ft": pos,
                             "width_in": h.get("width_in"), "flue": h.get("flue")})
    return axes or None
