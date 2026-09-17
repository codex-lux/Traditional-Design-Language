#!/usr/bin/env python3
"""The real solver (WP-2.3): room placement as CP-SAT over the bay grid.

Where build/geometry.py's search hill-climbs 250 random slicings toward
strongly-weighted preferences, this engine states the record's own declared
facts as HARD constraints and proves them satisfiable or names the conflict
(the 25 Aug rulings):

  HARD, NEVER DOWNGRADED (the 25 Aug rulings: these are what infeasibility is
  FOR) — no-overlap; containment in the room's own massing element; the
  coverage floor `COVERAGE`; declared doors imply touching rooms; a threshold
  room with an exterior door is the entry and must reach the entrance front;
  each room at roughly its program size; nothing over a void open to the sky
  (OQ 55).

  HARD AND DOWNGRADABLE, in the precedence `_RANK` states (lowest authority
  released first; every downgrade named on the record) — each room's declared
  exterior walls; the spanning passage on the block's through-axis (WP-11.7);
  and, since WP-13.3, the type's own facts, ruled HARD by Lucas on 15 Sep 2026:
  TILING (every element tiles exactly, `TILING`), DECLARED STACKS (a
  `stacks_over` claim holds by containment, the smaller declared room inside
  the larger -- `stacking.lands`' own relation), BEARING (an interior wall on
  the bay grid is bearing only where both storeys have a wall on it, and no
  run between bearing lines exceeds the framing tradition's capacity --
  `structure.bearing_lines` and `span_check` as a fact rather than a charge),
  the HEARTH on its flue (a stated fire's wall on the block face the massing
  puts a flue on -- `hearths.flue_walls`); and the room record's own
  proportion band (`GEO.shape_band`), released last.

  Wall pins carry two stated refinements, both from the same cause —
  `exterior_walls` speaks EXPOSURE in the fully-massed house (porches, ells,
  wings), which a flat rectangular footprint cannot always hold:
    * a PROTRUDING room (3+ walls, or a non-circulation opposite pair) and a
      room in a CONTESTED CORNER (two rooms of one level declaring the same
      corner pair — 10 of 12 partis do this) harden to "reach at least one
      declared wall", the rest scored at the heuristic's own 14 points;
    * any other wall pin stays fully hard UNLESS the solver PROVES a set of
      pins cannot co-hold with the remaining facts — exactly those proven
      pins are downgraded the same way, and every downgrade is stated in the
      result.

  SOFT (weighted, mirrored from WP-2.2's scoring) — bay snapping (relaxations
  stay counted, never forbidden), the entrance hall on the front, principal/
  service zoning, ceremonial depth, wet-over-wet stacking, a centre passage
  near the centre, the area error and the aspect against the room's own band,
  the width floor; and, for every downgradable fact the ladder RELEASED, the
  charge the search pays for the same thing -- 14 points for a wall or a
  hearth wall, `GEO.STACK_W` for a stack, `GEO.SPAN_W` for a span -- so a
  released fact is scored rather than forgotten. A HELD fact needs no charge.

  WHAT A FACT'S THREE STATES MEAN HERE: held (its literal was asserted and the
  placement proved under it), downgraded (the ladder released it and the
  reinstatement pass could not win it back, named on the record with proven /
  carried), unjudged (the model could not STATE it -- a stack whose target is
  not on the level below, a hearth on a wall the massing puts no flue on, a
  framing catalogue that could not be read -- named on the record with its
  reason). Unjudged is never held. `build/typefacts.py` verifies all four on
  the placed record afterwards, for either engine.

Solving is two-phase per footprint: a hard-constraints-only pass finds (or
refutes) a placement fast; the full weighted objective then polishes it with
the phase-A solution as a hint, and if the polish runs out of time the
phase-A placement is returned, scored post-hoc and said so. On INFEASIBLE the
assumption cores drive the downgrade rounds and, when the conflict is real,
a plain-language minimal conflict set. The footprint grows a bay before a
requirement is blamed, per the layer's stated infeasibility ordering.

Determinism: one worker, fixed seed — the same record must yield the same
drawing, because the drawing is a render of the data.

Loaded through geometry.solve()'s dispatcher; not a CLI of its own.
"""
import copy
import math
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _mod(n, p):
    # Delegates to build/modcache.py — one module execution per process (OQ 28).
    import sys as _sys
    _b = os.path.join(ROOT, "build")
    if _b not in _sys.path:
        _sys.path.insert(0, _b)
    import modcache as _mc
    return _mc.load(n, p)

GEO = _mod("geometry", f"{ROOT}/build/geometry.py")
STK = _mod("stacking", f"{ROOT}/build/stacking.py")   # LANDS_FRACTION, read not written
C = GEO.C

U = 1                     # 1-ft integer grid (coarse on purpose: domains half the size)
MIN_DOOR_OVERLAP = 4      # the fallback for a door that declares no width of its own


def _door_overlap(d, v1, v2):
    """How much wall two rooms must share to hold THIS door (WP-6.3, closing OQ 41/63).

    The rule was `min(4, max(2, floor(0.9 * min(maxside))))`, and its comment said it
    "scales to the smaller room: a linen press's whole side may be 2 ft — its door is
    narrower than a parlor's, and demanding 4 ft would refuse real closets". **That branch
    has never once fired.** `maxside` is `max(width_ft, length_ft)` — the LONGER side — so
    dropping below 4 needs a room whose long side is under 3.34 ft, and there are **0 such
    rooms in all 16 plan records** (238 rooms measured). Every interior pair in the corpus
    got a flat 4 ft: the 3 x 5 linen press the comment names got a parlour's requirement,
    and so did `bed2cl`, which is literally 2 x 6. OQ 41's own text quotes the same dead
    expression as though it described behaviour.

    So the floor is now the door's own leaf and its jambs, which is what a door occupies and
    what both renderers and both exporters have measured against since WP-6.1 — one number,
    `openings.required_wall_ft`, in one place. 469 of the corpus's 471 doors declare a width
    (the two that do not are exterior and never reach here), so this is the record speaking
    rather than a constant. Ceiled to the model's integer grid.

    Measured per pair across the corpus: 102 tighter, 3 looser, 128 unchanged."""
    w = d.get("width_ft")
    if not w:
        return MIN_DOOR_OVERLAP
    OP = _mod("openings", f"{ROOT}/build/openings.py")
    need = OP.required_wall_ft(float(w))
    # never demand more shared wall than the smaller room can physically offer, or a wide
    # opening between two small rooms becomes an infeasibility rather than a finding
    room_cap = min(v1["maxside"], v2["maxside"])
    return max(2, min(int(math.ceil(need * U)), int(math.floor(room_cap * U))))
SCALE = 10                # objective weights are WP-2.2's, x10 into integers

# PHASE A'S TACTICAL CAPS (WP-13.3). The BUDGET SHARES are `geometry.BUDGET_SHARE_*`, beside the
# budgets they divide; these three are how a share is spent inside one pass and are named here
# because they were literals in three places. A feasibility round SCOUTS at up to SCOUT_S
# before it is called undecided; the reinstatement pass offers a whole kind back at up to
# RESTORE_KIND_S and a single pin at up to RESTORE_PIN_S, each against the placement just
# found as the solver's hint (a warm start is what makes 2 s a real attempt), and never
# below RESTORE_MIN_S: a slice thinner than that is skipped rather than spent, because a
# quarter-second solve that comes back UNKNOWN is a pin marked carried for no information.
SCOUT_S = 6.0
RESTORE_KIND_S = 4.0
RESTORE_PIN_S = 2.0
RESTORE_MIN_S = 0.5
COVERAGE = 0.97           # the CAPACITY floor -- never downgraded (the 25 Aug rulings)

# THE TILING FACT (WP-13.3), stated as a downgradable literal ABOVE the capacity floor. The type
# says the rooms of a level tile the block they stand in; `COVERAGE` is the floor infeasibility
# is measured against and is never released, and this is the exact fact the ladder may release
# by name. MEASURED FIRST, on the unchanged model with the heuristic hint, on
# `plans/tidewater-georgian-careful.json` at the 40 s batch budget, twice at each floor:
#
#     floor 1.0    OPTIMAL (hard-only) twice, one placement digest both times (3af8998e61dc809d)
#     floor 0.995  UNKNOWN at the budget, twice -- no placement at all
#     floor 0.99   OPTIMAL (hard-only) twice, one digest (929bf7c523e21b27)
#     floor 0.97   OPTIMAL (hard-only) twice, TWO digests (fa8d8c8c / 35572bbb) -- the shipped
#                  floor, whose residue is what the gate read as 26.5 and 48.8 sf of no room
#
# So exact tiling PROVES from the hint that tiles exactly -- `docs/reports/wp-2.3-the-real-
# solver.md` recorded the exact-tiling formulation as undecidable in 240 s WITHOUT one -- and
# the middle floor is the one that does not, which is WP-7.4's "worse in the middle of its range
# than at either end" met in a floor rather than a weight. The tightest floor that proves is
# shipped; `typefacts.tiling` verifies the residue afterwards and any residue over its
# `TILING_TOL_SF` is the fact DOWNGRADED on the record, never a silence. At 1.0 the post-solve
# `_absorb` pass has nothing to grow into on a level that held the fact, and the record says so.
TILING = 1.0

def _ceil_scaled(ceil, scale=None):
    """`(scale, round(ceil * scale))` -- the integer pair a FRACTION is stated to the solver
    with, in one place. The scale defaults to `_BAND_Q`, read late because that constant is
    defined below with the measurement that set it.

    This is NOT only the proportion band's helper: `_lands_literal` states
    `stacking.LANDS_FRACTION` through it, which is a different quantity that happens to want
    the same scale. The band's own two statements read `_BAND_Q` directly, which is what
    `tests/test_shape_pins.py` holds them to."""
    q = _BAND_Q if scale is None else scale
    return q, int(round(float(ceil) * q))

# WP-11.7. The downgrade ladder, LOWEST AUTHORITY FIRST. On INFEASIBLE the round loop takes the
# first kind in this list that appears in the conflict core and releases every live pin of that
# kind (whole-rank, WP-11.7's measurement; core-guided, WP-13.3's), so a round always gives up
# the least authoritative fact it can and never one the core does not name.
#
#   wall     the record's `exterior_walls`  — released first
#   axis     the parti's own through-axis, read onto this plan
#   tiling   every element tiles exactly (`TILING`)                        \
#   stack    a declared `stacks_over` holds by containment                  | WP-13.3, the
#   bearing  bearing continuity on the bay grid, and the span capacity      | ruled sequence
#   hearth   a stated fire's wall on the block face the massing flues       /
#   shape    the room record's own `dimensions.proportion` band — released last
#
# THE FOUR IN THE MIDDLE ARE LUCAS'S RULING OF 15 SEP 2026 (Phase 13): the type's facts become
# hard on the prover "as downgradable constraints in a stated precedence -- authored walls >
# tiling > declared stacks > bearing continuity on the bay grid > hearth on its flue -- each
# downgrade named in the conflict set", and the 5 Sep ruling that the wall releases FIRST and
# the shape band LAST stands at both ends. The hearth ranks ABOVE the wall on purpose: a fire's
# wall is also usually one of the room's declared exterior walls, and a bare `exterior_walls`
# aspiration gives way before a wall a flue has to stand on.
#
# THE ORDER PUTS THE WALL FIRST, AND THAT IS A RULING RATHER THAN AN INTUITION (5 Sep 2026).
# The obvious ranking is the opposite one -- an `exterior_walls` entry is authored on THIS
# record and a proportion band is the corpus's rule about a room TYPE -- and it was written that
# way first. Then it was measured, and the two cannot both be hard:
#
#     shape band held, all 22 wall pins released  ->  OPTIMAL
#     shape band held, wall pins held             ->  INFEASIBLE, at every footprint to 10 bays
#
# and the ladder, ranked the other way, gave up 14 or 15 of the 15 shape pins at EVERY coverage
# floor from 0.97 down to 0.60 -- so coverage and packing are not the blocker and the band simply
# never survived. Measured on the drawing, releasing the walls instead: serious findings 79 -> 58,
# and NO room drawn outside its own band where the worst had been a 13 x 16 ft bedroom drawn
# 45 x 7. The price is relaxations 11 -> 18 and diverged 14 -> 17.
#
# CLAUDE.md has carried the reason all along: "A plan's `exterior_walls` are aspirations, not
# rectangle edges. Three Tidewater ground rooms each declare OPPOSITE walls, so each would have
# to span the full depth of the house. They are weights, at the 14 points `exterior_score`
# charges. Do not promote them to constraints; the corpus does not mean them that way." This
# engine promoted them anyway, from the day it was written, and the shape band is what made the
# contradiction visible rather than merely stated.
#
# A released wall pin is not discarded: it keeps the heuristic's own 14 points in the objective,
# which is what that note says it was always worth.
#
# A kind NOT in this list never downgrades: sizes, doors, the entrance and capacity are what
# infeasibility is FOR (the 25 Aug rulings). Adding a kind here is a decision about authority
# and belongs in a report, not in a diff.
_RANK = ("wall", "axis", "tiling", "stack", "bearing", "hearth", "shape")

# The kinds WP-13.3 added, in `_RANK`'s own order -- the four the record's `facts` block and
# `build/typefacts.py` account for as held / downgraded / unjudged.
TYPE_FACTS = ("tiling", "stack", "bearing", "hearth")


def _dk(kind, key):
    """A downgrade key CARRIES ITS KIND. `downgraded` used to hold bare keys and every reader
    told them apart by ARITY -- `(level, room, wall)` was a wall and `(level, room)` a shape --
    which was wrong before this package added five kinds: the axis pin and the shape pin share
    `(level, room)`, so releasing the passage's axis read as releasing its proportion band in
    `_build`, in the reinstatement labels and in `downgraded_shape_pins`. Typed, a key is
    `(kind, *key)` and is read by its first element everywhere."""
    return (kind,) + tuple(key)


def _label(kind, key):
    """The record's spelling of one downgradable fact. A wall keeps `L{level} {room} {wall}`
    (`hard_fact_violations` and `tests/test_solver.py` parse it); the others say what they are."""
    if kind == "wall":
        return f"L{key[0]} {key[1]} {key[2]}"
    if kind in ("shape", "axis", "stack"):
        return f"L{key[0]} {key[1]}"
    if kind == "tiling":
        return f"L{key[0]} element {key[1]}"
    if kind == "bearing":
        return f"element {key[0]} {key[1]}"
    if kind == "hearth":
        return f"L{key[0]} {key[1]} {key[2]}"
    return " ".join(str(k) for k in key)

# THE SCALE A PROPORTION CEILING IS STATED TO THE SOLVER AT, AND IT WAS A TENTH UNTIL WP-11.16.
# CP-SAT takes integer coefficients, so a band of `c` to 1 is written `Q * mxs <= round(c*Q) * mns`.
# Q WAS 10, AND THE CORPUS STATES ITS BANDS TO TWO DECIMALS -- so `int(round(1.35 * 10))` is 14 and
# the prover asserted a ceiling of **1.4** on every room whose record says 1.35. Measured over all
# 54 banded room types: 4 LOOSE (`bedroom`, `keeping-room`, `morning-room`, `nursery`, all
# 1.35 -> 1.4) and 1 TIGHT (`parlor`, 1.45 -> 1.4). 49 survive the rounding exactly, and
# `GEO.ASPECT_FALLBACK` (2.6) is one of them, which is why this went unnoticed for four packages.
#
# BOTH DIRECTIONS ARE DEFECTS AND THE TIGHT ONE IS THE SHARPER. Loose, the prover PROVES a room
# inside a band it is outside of -- `plans/tidewater-georgian-careful.json` drew `chamber2` at
# 18 x 13 (1.3846) with its pin HELD and `downgraded_shape_pins` naming only `L0 pantry`, because
# 10*18 = 180 <= 14*13 = 182. Tight, the prover can downgrade an AUTHORED wall pin, or report
# INFEASIBLE, to escape a band the room's own record does not state -- a false refusal wearing a
# proof's clothes, which is the OQ 52 family.
#
# `GEO.shape_band()` is unrounded and the hill-climb reads it directly, so this was never a
# heuristic defect; it lived only in the two places the model is built.
#
# It is a CONSTANT and not a literal at each site because there are TWO sites -- the hard pin and
# the soft overshoot term -- and they must never disagree about what the band is. That is this
# corpus's most-repeated bug (a rule written twice), and the reason the one-decimal form survived
# is that both copies were wrong together and so agreed with each other.
#
# AND TWO PARALLEL SESSIONS FOUND AND FIXED THIS INDEPENDENTLY, WHICH IS WHY THE MERGE HAD TO
# CHOOSE A NAME. The other line met the same defect from the other end -- the intermittent red
# in `tests/test_shape_pins.py`, `chamber3` drawn 21 x 15 at exactly 1.40 to 1 with its shape
# pin HELD, `_absorb` the obvious suspect and not the cause -- and named the constant
# differently. ONE NAME SURVIVES AND IT IS THIS ONE, because a rule with two names is the same
# defect as a rule written twice. The other line's `_ceil_scaled` helper survives beside it,
# because `_lands_literal` calls it for a quantity this constant is not about.
_BAND_Q = 100


def _cls(rtype):
    return C["rooms"].get(rtype, {}).get("function_class")


def _fpd_at(fpd, bays):
    """The footprint fpd would have derived at a forced bay count — the
    grow-a-bay-before-blaming-a-requirement loop."""
    out = dict(fpd)
    W = round(bays * fpd["bay"], 2)
    H = round(fpd["need"] / W, 2)
    out.update({"bays": bays, "W": W, "H": H,
                "slack": (W * H) - fpd["need"],
                "grown": fpd["grown"] + list(range(fpd["bays"] + 1, bays + 1))})
    return out


def _protruding(room):
    walls = set(room.get("exterior_walls") or [])
    if len(walls) >= 3:
        return True
    opposite = ({"S", "N"} <= walls) or ({"W", "E"} <= walls)
    return opposite and _cls(room["type"]) != "circulation"


_CORNER_PAIRS = ({"N", "E"}, {"N", "W"}, {"S", "E"}, {"S", "W"})


def _contested_corners(rs):
    """Per the 25 Aug ruling (contested corners downgrade, stated): two or more
    rooms on one level declaring the same corner pair cannot all have the
    corner of one rectangle. Returns {room_id: note}."""
    out = {}
    for pair in _CORNER_PAIRS:
        claim = [r for r in rs
                 if pair <= set(r.get("exterior_walls") or []) and not _protruding(r)]
        if len(claim) > 1:
            names = ", ".join(sorted(r.get("name") or r["id"] for r in claim))
            for r in claim:
                out[r["id"]] = (f"{'/'.join(sorted(pair))} corner is contested ({names}) — "
                                f"the massing likely has a wing the flat footprint cannot hold")
    return out


class _Reqs:
    """Assumption literals: plain-language sentence, kind, and (for every downgradable kind)
    a structured key so a proven-impossible pin can be downgraded by name.

    `unjudged` (WP-13.3) is the third state: a fact the model could NOT STATE -- a stack whose
    target is not on the level below, a fire on a wall the massing puts no flue on, a framing
    catalogue it could not read -- recorded as `(kind, key, reason)` so the record can say so
    beside the held and the downgraded. Unjudged is never held."""

    def __init__(self, model):
        self.model = model
        self.lits = []      # (BoolVar, text, kind, key)
        self.notes = []     # stated model refinements (contested corners, downgrades)
        self.unjudged = []  # (kind, key-or-None, reason)

    def lit(self, text, kind="other", key=None):
        b = self.model.NewBoolVar(f"req{len(self.lits)}")
        self.lits.append((b, text, kind, key))
        return b

    def refuse(self, kind, key, reason):
        self.unjudged.append((kind, key, reason))
        self.notes.append(f"{kind} {(_label(kind, key) + ': ') if key else ''}COULD NOT BE "
                          f"STATED -- {reason}")


def _w(weight):
    """A heuristic weight as an integer CP penalty, on this model's x10 SCALE.

    WP-7.4 wrote this as `int(w) * SCALE`, which truncates: a weight of 0.5 became 0 and the
    term silently vanished, and a weight of 40.9 became 40. Rounding the SCALED value keeps
    fractional weights meaningful, and a non-zero weight can never round away to nothing --
    a term that disappears because someone tuned it below 1.0 is the kind of silence this
    corpus exists to prevent."""
    v = int(round(float(weight) * SCALE))
    return v if v or not weight else (1 if weight > 0 else -1)


def _lands_literal(m, a, b, frame):
    """`lands -> stacking.lands(a, b)`: the smaller of the two DRAWN rectangles lies at least
    `stacking.LANDS_FRACTION` of its own area inside the larger, with a strictly positive
    overlap on both axes.

    TRANSCRIBED FROM `build/stacking.py::lands` -- the one spelling `judge` reads for the
    record and `geometry.declared_stack_breaks` reads for the search -- with the fraction READ
    off it rather than written here; `tests/test_type_facts_hard.py` holds the transcription to
    the original by judging a placement proved under the literal with `stacking.judge`, and by
    driving the literal on a pair the rule refuses. The overlap on each axis is clamped at zero
    before the product, because two disjoint rectangles have a NEGATIVE extent on that axis and
    the product of two negatives would read as a landed stack. One product per claim (the
    overlap's); the two areas are the rooms' own `a` variables.

    `frame` is the building's own (gx0, gy0, gx1, gy1) and every domain here is derived from
    it -- the edges of the overlap lie inside the frame the rooms' own `x`/`y` are bounded by,
    its extent inside the frame's width and depth, and the areas inside `gW * gH`, which is the
    domain each room's `a` already carries. The first draft gave them `[-_EXT, _EXT]`, the
    widened domain `_wide` reserves for a multi-element plan, and
    `tests/test_element_awareness.py::test_no_shipped_plan_gets_a_WIDENED_domain` refused it on
    every shipped plan: a domain is an input to presolve, not a comment."""
    gx0, gy0, gx1, gy1 = (int(c) for c in frame)
    gW, gH = gx1 - gx0, gy1 - gy0
    lo_x, hi_x = m.NewIntVar(gx0, gx1, ""), m.NewIntVar(gx0, gx1, "")
    m.AddMaxEquality(lo_x, [a["x"], b["x"]])
    m.AddMinEquality(hi_x, [a["x"] + a["w"], b["x"] + b["w"]])
    lo_y, hi_y = m.NewIntVar(gy0, gy1, ""), m.NewIntVar(gy0, gy1, "")
    m.AddMaxEquality(lo_y, [a["y"], b["y"]])
    m.AddMinEquality(hi_y, [a["y"] + a["h"], b["y"] + b["h"]])
    ix, iy = m.NewIntVar(0, gW, ""), m.NewIntVar(0, gH, "")
    m.AddMaxEquality(ix, [hi_x - lo_x, 0])
    m.AddMaxEquality(iy, [hi_y - lo_y, 0])
    shared = m.NewIntVar(0, gW * gH, "")
    m.AddMultiplicationEquality(shared, [ix, iy])
    # each room's area is already a variable of the model (`a`, the size literal's own), so
    # the only new product is the overlap's
    smaller = m.NewIntVar(0, gW * gH, "")
    m.AddMinEquality(smaller, [a["a"], b["a"]])
    lands = m.NewBoolVar("")
    scale, frac = _ceil_scaled(STK.LANDS_FRACTION)
    m.Add(scale * shared >= frac * smaller).OnlyEnforceIf(lands)
    m.Add(ix >= 1).OnlyEnforceIf(lands)
    m.Add(iy >= 1).OnlyEnforceIf(lands)
    return lands


def _span_capacity(plan):
    """The clear span this plan's framing tradition can make, from the corpus rather than a
    constant: timber-bay.json's 20 ft bay module for the styles that list it, else the deepest
    member in construction/floor-structure.json's light_frame_joist_spans. Mirrors
    structure.span_check's own decision so the two engines charge the same fact."""
    try:
        ST = _mod("structure", f"{ROOT}/build/structure.py")
        if (plan.get("style") or "") in ST._timber_bay_applies_to():
            return 20.0
        tbl = ST.load_construction()["floor"]["light_frame_joist_spans"]
        return max(mm["max_clear_span_ft"] for mm in tbl)
    except Exception:
        return None       # catalogue unreadable: unjudged, so nothing is charged


def _boxes(plan, prep, fpd):
    """`({(level, room_id): (x0, y0, x1, y1)}, main_box)` in integer units — MAIN'S SPELLING,
    DERIVED FROM THIS BRANCH'S `_element_boxes` AT THE MERGE OF THE TWO PHASE 11s (8 Sep 2026).

    Both branches built this map. Main's returned CORNERS and was the name its own tests and
    five call sites read; this branch's `_element_boxes` returns `(x, y, W, H)` and carries the
    inward rounding WP-11.13's coverage floor is stated against. Keeping both would be two maps
    of one fact, which is how the model and the disclosure come to disagree about a box — so
    there is ONE arithmetic and this is the corner VIEW of it.
    """
    Wi, Hi = int(round(fpd["W"] * U)), int(round(fpd["H"] * U))
    # LEVEL 0 ONLY BUILDS ELEMENTS, AND THIS FILE SAID SO IN THREE OTHER PLACES WHILE DOING
    # OTHERWISE HERE. `geometry.py` states the rule three times -- "the placer lays only
    # level 0 into elements, so every upper room is inside the main block" -- and
    # `multi_element` DISCLOSES any room above the ground whose `block` tag the placer does
    # not read. Calling `blocks_for` for level 1 built elements from those unread tags, so
    # an upper room carrying one was bounded by a WING box: measured on the other branch's
    # fixture, a landing at (-86, 8, -14, 33) where every upper room belongs in the main
    # block. Both Phase 11s agree on the rule; only this line disagreed with it.
    els = {lvl: (GEO.blocks_for(plan, fpd, prep, lvl) if lvl == 0
                 else [{"id": "main", "role": "main", "x": 0, "y": 0,
                        "W": fpd["W"], "H": fpd["H"],
                        "rooms": [r["id"] for r in prep.get(lvl) or []]}])
           for lvl in (0, 1) if prep.get(lvl)}
    ebox, gx0, gy0, gx1, gy1 = _element_boxes(els, Wi, Hi)
    # THE SECOND RETURN IS THE MAIN BLOCK'S OWN BOX, NOT THE GLOBAL ENVELOPE, and the difference
    # is the defect this branch's WP-11.11 measured. Bounding a main-block room by the union lets
    # it roam the whole extent: that package found "every MAIN-BLOCK room then had a domain
    # reaching 34 ft west of the house and nothing holding it back -- five untagged rooms placed
    # or absorbed in no element at all". Main's callers read this value as "the box everyone who
    # is not in a wing gets", which is the main block, so the tighter reading is also the one
    # they expect.
    _mains = [e for e in (els.get(0) or []) if e.get("role") == "main"] or (els.get(0) or [])
    if _mains:
        e = _mains[0]
        mx, my, mW, mH = GEO._elements().integer_box(e["x"], e["y"], e["W"], e["H"], U)
        _mb = (mx, my, mx + mW, my + mH)
    else:
        _mb = (gx0, gy0, gx1, gy1)
    return ({k: (x, y, x + W, y + H) for k, (x, y, W, H) in ebox.items()}, _mb)


def _element_fills(boxes, rs, lvl):
    """Each element's own slack: its floor area over the programme its own rooms declare.

    `fill` sets every room's area CEILING (`max(1.20, fill * 1.22)`), and it was the WHOLE
    building's ratio (WP-11.6 item 4). A dependency measured that way is licensed to grow by a
    share of floor that is not in its element -- the cap stops meaning "roughly its program
    size" and starts meaning "roughly its program size, plus a share of the main block". Lifted
    out of `_build` so it can be read: inline, a mutation putting the building's ratio back left
    the whole suite green."""
    out = {}
    for bx in {boxes[(lvl, r["id"])] for r in rs}:
        rs_b = [r for r in rs if boxes[(lvl, r["id"])] == bx]
        area = ((bx[2] - bx[0]) / U) * ((bx[3] - bx[1]) / U)
        out[bx] = area / max(1.0, sum(r["_area"] for r in rs_b))
    return out


def _abuts(a, b):
    """Do two element boxes share a face? (WP-11.6 item 4.)

    Overlapping on one axis and touching on the other. A shared CORNER is not an abutment and
    the strict inequalities say so: no door leaf fits in a point, which is the same reading
    `openings.faces_across_a_gap` takes for the same reason at layer 5. Identical boxes — the
    one-element case, where every room is in the same box — abut, which is what makes the
    door constraint below the one it always was."""
    if a == b:
        return True
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    if ax1 == bx0 or bx1 == ax0:
        return min(ay1, by1) - max(ay0, by0) > 0
    if ay1 == by0 or by1 == ay0:
        return min(ax1, bx1) - max(ax0, bx0) > 0
    return False


def _element_boxes(els, Wi, Hi):
    """`{(level, room_id): (x, y, W, H)}` in integer units, and the global envelope.

    WP-11.11. The CP model built every room as `x = NewIntVar(0, Wi)` with `x + w <= Wi`: one
    rectangle, one non-negative coordinate space, and it REFUSED a plan with a second massing
    element rather than flatten two into one (which flatters the fatal count -- rooms crammed
    into one rectangle are all trivially reachable). Ruled 7 September 2026, taking
    `oq/the-proving-engine-cannot-place-a-second-massing-element`'s own first reading: **each
    room's coordinates are bounded by its OWN element's box**, in ONE coordinate space. CP-SAT
    integer variables take negative lower bounds, so a west dependency at x = -28 needs no
    shift and no second origin -- the alternative the question offered and this does not use.

    Everything the model says about "the block" is read through this: containment, the coverage
    floor, a declared exterior wall, a spanning room's through-axis, and an exterior door
    reaching the envelope. Each of those is a fact about the element the room stands in.

    The global envelope is returned beside it because the VARIABLE DOMAINS have to cover every
    element while the CONSTRAINTS bound each room to its own. Bounding a domain to its element
    would be tighter and is not done: it would put a room's `x` in a domain that excludes the
    origin, and the hint pass (`_hint_heuristic`, `_hint_values`) feeds values from a heuristic
    layout that may disagree by a foot -- a hint outside a domain is a silent model error, not
    a rejected hint.
    """
    box, xs, ys = {}, [0, Wi], [0, Hi]
    for lvl, elist in (els or {}).items():
        for e in elist or []:
            # INWARD to the grid, never outward. This model is integer at 1 ft (`U`) and a
            # dependency's edges are not: `dependency_sizes` sizes the box from its rooms'
            # own areas and lands on 4.6 or -3.7. Rounding to the NEAREST foot lets CP place a
            # room up to half a foot outside the mass the record states, which is the record
            # and the drawing disagreeing about where the house is -- the defect the refusal
            # this package removes was put there to prevent. Ceiling the low edge and flooring
            # the high one makes the integer box a SUBSET of the stated one, so anything proved
            # inside it is really inside; `_absorb` afterwards works in float space against the
            # element's true edges and grows the room back out to them. The main block is
            # already integral (`_snap_fpd`), so this is the identity on every single-element
            # plan in the corpus.
            # WP-11.13: the rule itself lives in `build/elements.py`, the leaf both this
            # model and `geometry.multi_element_disclosure` load, because the disclosure has
            # to report the box the model works in and a second transcription of an inward
            # rounding is exactly what this package found wrong one screen down.
            ex, ey, eW, eH = GEO._elements().integer_box(e["x"], e["y"], e["W"], e["H"], U)
            xs += [ex, ex + eW]
            ys += [ey, ey + eH]
            for rid in e.get("rooms") or []:
                box[(lvl, rid)] = (ex, ey, eW, eH)
    return box, min(xs), min(ys), max(xs), max(ys)


def _build(plan, prep, fpd, ewalls, downgraded=frozenset(), objective=True,
           unproven=frozenset()):
    from ortools.sat.python import cp_model
    m = cp_model.CpModel()
    reqs = _Reqs(m)
    Wi, Hi = int(round(fpd["W"] * U)), int(round(fpd["H"] * U))
    # WP-11.11. `els` is {level: [element, ...]} from `geometry.blocks_for` -- the massing
    # elements this level's rooms are laid into. Absent, or one element, and every box below is
    # `(0, 0, Wi, Hi)`, which is what this model read before the argument existed and is every
    # plan in the shipped corpus.
    # Computed here rather than threaded from `solve_cp`: `_build` has seven call sites in
    # this file and `geometry.blocks_for` is the one reader of which element a room stands in,
    # so a parameter would have been seven chances to pass a different answer.
    # LEVEL 0 ONLY BUILDS ELEMENTS, AND THIS FILE SAID SO IN THREE OTHER PLACES WHILE DOING
    # OTHERWISE HERE. `geometry.py` states the rule three times -- "the placer lays only
    # level 0 into elements, so every upper room is inside the main block" -- and
    # `multi_element` DISCLOSES any room above the ground whose `block` tag the placer does
    # not read. Calling `blocks_for` for level 1 built elements from those unread tags, so
    # an upper room carrying one was bounded by a WING box: measured on the other branch's
    # fixture, a landing at (-86, 8, -14, 33) where every upper room belongs in the main
    # block. Both Phase 11s agree on the rule; only this line disagreed with it.
    els = {lvl: (GEO.blocks_for(plan, fpd, prep, lvl) if lvl == 0
                 else [{"id": "main", "role": "main", "x": 0, "y": 0,
                        "W": fpd["W"], "H": fpd["H"],
                        "rooms": [r["id"] for r in prep.get(lvl) or []]}])
           for lvl in (0, 1) if prep.get(lvl)}
    ebox, gx0, gy0, gx1, gy1 = _element_boxes(els, Wi, Hi)
    gW, gH = gx1 - gx0, gy1 - gy0
    bayU = max(1, int(round(fpd["bay"] * U)))
    tolU = max(1, int(round(fpd["tol"] * U)))
    # BOTH BRANCHES BUILT THIS MAP AND THE MERGE KEEPS ONE OF THEM. `_element_boxes`
    # (this branch, WP-11.11/11.13) returns `(x, y, W, H)` per room in integer units and
    # carries the inward rounding the coverage floor is stated against; main's `_boxes`
    # returned CORNERS. Main's consumers below are written against corners, so the corner
    # form is DERIVED from the one map rather than computed a second time -- two maps of
    # one fact is how the model and the disclosure come to disagree about a box.
    boxes = {k: (x, y, x + W, y + H) for k, (x, y, W, H) in ebox.items()}
    _main_box = (gx0, gy0, gx1, gy1)
    # The widest coordinate any element reaches, so the BUILDING-WIDE soft terms further down
    # can be given honest variable domains. A west wing's x is NEGATIVE, and a domain of
    # [0, span] on a distance-to-the-front is not a worse model, it is an infeasible one.
    _EXT = max([abs(c) for b in boxes.values() for c in b] + [Wi, Hi]) * 2 + 1
    _multi = any(b != _main_box for b in boxes.values())

    def _wide(lo, hi):
        """The domain a building-wide soft term needs, WIDENED ONLY WHERE IT HAS TO BE.

        One element -> exactly the bounds the term always carried, so the sixteen one-rectangle
        records serialise to the same model and take the same presolve. A first version widened
        unconditionally, on the argument that a looser domain cannot change an answer -- and it
        moved the OBJECTIVE proto on seven of the sixteen. A domain is an input to presolve, not
        a comment. More than one element and the widening is not optional: these terms measure
        against the MAIN block in both engines (`entrance_score` and the zoning scorers do, so
        changing the frame in one engine only is how the two come to disagree about one house),
        and a wing's distance to that frame is negative."""
        return (-_EXT, _EXT) if _multi else (lo, hi)

    rooms = {}      # (level, id) -> dict of vars
    penalties = []  # (bool_or_int_expr, weight_x10)

    # WHICH BLOCK FACES THE MASSING PUTS A FLUE ON, read ONCE through `hearths.flue_walls` --
    # the one spelling, with its three refusal reasons -- and only where some room states a fire,
    # so a plan with none loads nothing it does not need.
    _flue_walls, _flue_why = None, None
    if any(r.get("hearth") for lv in (0, 1) for r in (prep.get(lv) or [])):
        HE = _mod("hearths", f"{ROOT}/build/hearths.py")
        _massing = (C.get("massings") or {}).get(plan.get("massing") or "") or {}
        _flue_rule, _flue_why = HE.flue_walls(plan, _massing)
        _flue_walls = tuple(_flue_rule["walls"]) if _flue_rule else None

    for lvl in (0, 1):
        rs = prep.get(lvl) or []
        if not rs:
            continue
        _fills = _element_fills(boxes, rs, lvl)   # the ELEMENT's slack, not the building's
        xiv, yiv = [], []
        for r in rs:
            bx0, by0, bx1, by1 = boxes[(lvl, r["id"])]
            bwU, bhU = bx1 - bx0, by1 - by0
            fill = _fills[(bx0, by0, bx1, by1)]
            dw = (r.get("width_ft") or 10)
            dl = (r.get("length_ft") or 12)
            smin = min(dw, dl)
            # floor scales to the room's own programme — a 1.4 ft linen press is
            # real; clamping it to 3 ft manufactured an infeasibility
            lo_side = max(1, int(math.floor(0.6 * smin * U)))
            # WP-11.11: the ROOM'S OWN element, not the block. `(0, 0, Wi, Hi)` on every
            # single-element plan, which is the whole shipped corpus.
            ex, ey, eW, eH = ebox.get((lvl, r["id"]), (0, 0, Wi, Hi))
            x = m.NewIntVar(gx0, gx1, f"x{lvl}_{r['id']}")
            y = m.NewIntVar(gy0, gy1, f"y{lvl}_{r['id']}")
            w = m.NewIntVar(lo_side, max(lo_side, eW), f"w{lvl}_{r['id']}")
            h = m.NewIntVar(lo_side, max(lo_side, eH), f"h{lvl}_{r['id']}")
            a = m.NewIntVar(0, gW * gH, f"a{lvl}_{r['id']}")
            m.AddMultiplicationEquality(a, [w, h])
            # the room at roughly its program size — ONE requirement per room,
            # so a conflict names the room, not an anonymous inequality
            areaU = r["_area"] * U * U
            pr = reqs.lit(f"{r.get('name') or r['id']} needs roughly its program size "
                          f"({dw:g} x {dl:g} ft, within this layer's tolerance)",
                          kind="size")
            m.Add(a >= int(0.88 * areaU)).OnlyEnforceIf(pr)
            m.Add(a <= int(max(1.20, fill * 1.22) * areaU)).OnlyEnforceIf(pr)
            # containment in the room's OWN element (WP-11.11). The lower bounds are
            # constraints and not domains, for the hint reason in `_element_boxes`.
            # THE LOWER BOUND IS A CONSTRAINT WHENEVER THE DOMAIN IS WIDER THAN THE ELEMENT,
            # AND THE FIRST VERSION OF THIS TESTED `if ex:` INSTEAD. That read "on a
            # one-rectangle house ex is 0 and `x >= 0` is already the domain" -- true of the OLD
            # domain and false of the new one, because `gx0` is the leftmost element's edge and
            # a west dependency puts it at -34. So every MAIN-BLOCK room got a domain reaching
            # 34 ft west of the house and no constraint holding it back: measured on a
            # hand-tagged Tidewater, FIVE untagged rooms were placed or absorbed at a negative
            # x, in no element at all. The guard written to protect byte-identity created the
            # defect it was guarding against. `gx0 < ex` is the honest test -- it is False on
            # every single-element plan, so the model for the shipped corpus is unchanged, and
            # True exactly when the domain really is wider than the box.
            if gx0 < ex:
                m.Add(x >= ex)
            if gy0 < ey:
                m.Add(y >= ey)
            m.Add(x + w <= ex + eW)
            m.Add(y + h <= ey + eH)
            # THE SHORT AND LONG SIDES, BUILT UNCONDITIONALLY (WP-11.7). They used to live
            # inside `if objective:` because only the soft aspect term read them -- and phase A
            # runs with `objective=False`, which is the phase that draws this plan
            # (`_finish_feasible` keeps "hard-only phase A" whenever the polish times out). A
            # shape rule that exists only in the objective is a shape rule this plan never sees.
            mxs = m.NewIntVar(0, max(gW, gH), f"mx{lvl}_{r['id']}")
            mns = m.NewIntVar(0, max(gW, gH), f"mn{lvl}_{r['id']}")
            m.AddMaxEquality(mxs, [w, h])
            m.AddMinEquality(mns, [w, h])

            # THE ROOM'S OWN PROPORTION BAND, HARD (WP-11.7), AND NOT AN INVENTED TOLERANCE.
            # WP-11.7 was planned as per-room side bounds at an authored tolerance tau. It is
            # this instead, because the corpus already states the rule and tau would have been
            # a number nobody could source. Measured before choosing: all 23 dimensioned rooms
            # on `plans/tidewater-georgian-careful.json` declare a shape INSIDE their own type's
            # `dimensions.proportion` band, so binding the band constrains the drawing without
            # contradicting one authored record.
            #
            # It is the band `plan_check`'s drawn layer already convicts a room for leaving, so
            # the placer now proves what the critic tests -- `vertical_score`'s own rule that
            # the search and the arbiter must not convict and acquit the same house. One
            # spelling, `GEO.shape_band`, which the soft term below already reads.
            #
            # DOWNGRADABLE, and RANKED ABOVE A WALL PIN -- see `_RANK`, which carries the
            # measurement that decided it. The two cannot both be hard on this plan, and a
            # released wall pin keeps its 14 points in the objective, which is what CLAUDE.md
            # has always said an `exterior_walls` entry is worth.
            _ceil, _src = GEO.shape_band(r.get("type"))
            _nm = r.get('name') or r['id']
            if _ceil and _dk("shape", (lvl, r["id"])) in downgraded:
                # proven unable to co-hold with the rest: stated, and scored rather than
                # forced, the same shape a downgraded wall pin takes six hundred lines down
                reqs.notes.append(
                    f"{_nm}'s own proportion band ({_ceil:g} to 1) could not co-hold with the "
                    f"other declared facts — downgraded, so this room may be drawn a shape its "
                    f"own record does not admit, and the drawn layer will say so")
            elif _ceil:
                _sh = reqs.lit(f"{_nm} is drawn no longer than {_ceil:g} to 1 — the "
                               f"proportion band its own room record states ({_src})",
                               kind="shape", key=(lvl, r["id"]))
                # STATED ON max/min, AND THE OBVIOUS REWRITE IS SLOWER — MEASURED, BECAUSE IT
                # LOOKS LIKE A FREE WIN AND IS NOT. `max(w,h) <= c * min(w,h)` is exactly
                # `w <= c*h AND h <= c*w` for positive sides, and that form needs no
                # AddMaxEquality/AddMinEquality pair, so it reads as strictly cheaper. Timed on
                # the two shipped plans with all wall pins released and the heuristic hint:
                #
                #     max/min (this form)     spec-builder 29.6 s   tidewater 11.3 s
                #     w <= c*h AND h <= c*w   spec-builder 48.2 s   tidewater 20.4 s
                #
                # CP-SAT's max/min propagators are stronger here than two reified linear
                # constraints, by a factor of about 1.7. The pair is built unconditionally
                # above and the soft aspect term shares it, so it costs nothing to reuse.
                # `_BAND_Q`, not a literal 10: see the constant for the measurement. At a
                # tenth this line asserted 1.4 for every record stating 1.35.
                m.Add(_BAND_Q * mxs <= int(round(_ceil * _BAND_Q)) * mns).OnlyEnforceIf(_sh)
            else:
                # The FLOOR is deliberately not stated: every room record's proportion floor is
                # 1.0 since the 3 Sep ruling, and `mxs >= mns` holds by construction, so a floor
                # constraint would be a branch that can never bite.
                reqs.notes.append(
                    f"{_nm}: its room type states no proportion band, so its drawn SHAPE is "
                    f"unconstrained here and unjudged by the drawn layer too — it may come "
                    f"back any shape at all and nothing will say so")
            if objective:
                # mirror level_score's own terms, term for term: area error
                # (10 x |got-want|/want) and aspect sanity (6 per ratio point
                # past 2.6, linearized against the short side)
                target = int(round(min(max(1.20, fill * 1.10), 1.22) * areaU))
                dev = m.NewIntVar(0, gW * gH, "")
                diff = m.NewIntVar(-gW * gH, gW * gH, "")
                m.Add(diff == a - target)
                m.AddAbsEquality(dev, diff)
                penalties.append((dev, max(1, int(round(10 * SCALE / max(areaU, 1))))))
                mx, mn = mxs, mns      # built above, unconditionally (WP-11.7)
                ov10 = m.NewIntVar(0, 10 * max(gW, gH), "")
                # THE `26` HERE WAS 2.6 x 10 -- THE SAME UNIVERSAL CONSTANT `level_score`
                # CARRIED, SPELLED A SECOND TIME (WP-9.4). Correcting the heuristic alone
                # would have fixed one of the two: `auto` sends 16 of 21 partis through this
                # engine, and the sheet that raised Phase 9 was CP-drawn -- its caption reads
                # "proven ... no placement exists". So the ceiling is read from the room's own
                # `dimensions.proportion` in BOTH engines, from geometry.shape_band(), which
                # is the one spelling. The corpus has been bitten by a rule written twice at
                # least four times; this is not a fifth.
                _ceil, _src = GEO.shape_band(r.get("type"))
                # SCALE-NEUTRAL, DELIBERATELY. `ov10` is in tenths and `penalties` takes an
                # INTEGER weight, so restating this as `ov100 >= 100*mx - ...` would multiply
                # the shape term against every other penalty by ten -- a re-weighting, and a
                # different package. Multiplying the LEFT side instead keeps `ov10`'s units and
                # its weight of 6 while reading the ceiling at `_BAND_Q`; integer division makes
                # the charge a ceiling rather than a floor, which over-charges by under one
                # tenth and is the conservative direction.
                m.Add(10 * ov10 >= _BAND_Q * mx - int(round(_ceil * _BAND_Q)) * mn)
                penalties.append((ov10, 6))
                # The width floor the room's own record states, mirrored from level_score's
                # `(floor - short) * WIDTH_W`. A soft penalty and never a bound: a hard floor
                # here would manufacture the infeasibility `lo_side` above was written to
                # avoid, and WP-6.3 refused hard pins for inferred structure on the stronger
                # ground that only `kind == "wall"` literals are downgradable.
                _floor = GEO.width_floor(r.get("type"))
                if _floor and GEO.WIDTH_W:
                    underw = m.NewIntVar(0, max(gW, gH), "")
                    m.Add(underw >= int(round(_floor * U)) - mn)
                    penalties.append((underw, max(1, int(round(GEO.WIDTH_W)))))
            xiv.append(m.NewIntervalVar(x, w, m.NewIntVar(gx0, gx1, ""), f"xi{lvl}_{r['id']}"))
            yiv.append(m.NewIntervalVar(y, h, m.NewIntVar(gy0, gy1, ""), f"yi{lvl}_{r['id']}"))
            rooms[(lvl, r["id"])] = {"x": x, "y": y, "w": w, "h": h, "a": a, "r": r,
                                     "maxside": max(dw, dl)}
        # ONE NoOverlap2D over the whole level, elements included. Two elements are disjoint
        # rectangles, so every cross-element pair is satisfied trivially and this costs nothing
        # — but it is what makes a HYPHEN real: the link's rooms and the rooms on either side of
        # it stand in the same non-overlap relation as any two rooms, so the door constraint
        # below can ask them to share a face and get a true answer rather than a vacuous one.
        m.AddNoOverlap2D(xiv, yiv)
        # coverage floor: no-overlap + containment + this bounds the void the
        # absorb pass must grow rooms into (the guillotine heuristic tiles exactly)
        upper_area = sum(rooms[(lvl, r["id"])]["a"] for r in rs)
        voids_below = ([r for r in (prep.get(0) or [])
                        if isinstance(r.get("_void"), dict) and not r["_void"].get("roofed")]
                       if lvl == 1 else [])
        if voids_below:
            # An upper storey over a courtyard cannot cover the footprint, and must not be
            # asked to (OQ 55). Without this the coverage floor and the open-void constraint
            # below contradict each other on every courtyard plan: the storey is required to
            # fill 97% of the block AND to leave the hole empty, and CP-SAT correctly reports
            # a brief that is perfectly buildable as infeasible. The hole comes off the target.
            # Written with integer coefficients (x100) because CP-SAT takes no float ones.
            c100 = int(round(COVERAGE * 100))
            void_area = sum(rooms[(0, v["id"])]["a"] for v in voids_below
                            if (0, v["id"]) in rooms)
            m.Add(100 * upper_area + c100 * void_area >= c100 * Wi * Hi)
        elif len(els.get(lvl) or []) > 1:
            # WP-11.11: PER ELEMENT. A coverage floor over the union would let a dependency
            # sit half empty while the main block over-filled to make up the total, which is
            # the "two elements flattened into one" reading this model refuses.
            #
            # WP-11.13 FOUND TWO DEFECTS IN THAT LOOP AND BOTH ARE FIXED HERE.
            #
            # ONE BOX, NOT TWO. It computed the element's box with `int(round(...))` while
            # CONTAINMENT above bounds every room to `_element_boxes`' box, which ceils the low
            # edge and floors the high one. Two roundings of one quantity, and the model then
            # demanded 97% of the LARGER be packed inside the SMALLER: on the hand-tagged
            # Tidewater the hyphen's floor asked for 108.6 sf inside a box holding 105 --
            # infeasible by construction, before a single declared fact was read, and the
            # conflict core duly blamed the tiling. `ebox` is the one spelling now.
            #
            # AND WHAT THE FLOOR IS STATED AGAINST DEPENDS ON HOW THE BOX WAS DERIVED. The main
            # block's box is derived INDEPENDENTLY of its rooms -- `derive_footprint` grows it
            # until the programme fits -- so "fill 97% of your box" is a real question about
            # the rooms. A dependency's box is derived FROM its rooms by `dependency_sizes`, so
            # asking whether those rooms fill it is asking the box about itself, and the
            # quantised answer cannot even be made to land: the floor needs the box within 3%
            # of the rooms' area and one foot of a 30 ft dependency is 5%. For such an element
            # the floor is stated against the rooms' OWN DECLARED AREA, which is the guarantee
            # the floor was for -- rooms may not shrink and leave the element half empty --
            # expressed in a way the grid cannot falsify. Roles are `elements.py`'s.
            for _e in (els or {}).get(lvl, []):
                _ids = [rid for rid in (_e.get("rooms") or []) if (lvl, rid) in rooms]
                if not _ids:
                    continue
                _got = sum(rooms[(lvl, rid)]["a"] for rid in _ids)
                if _e.get("role") == "main":
                    _bx = ebox.get((lvl, _ids[0]))
                    if _bx is None:
                        continue
                    m.Add(_got >= int(COVERAGE * _bx[2] * _bx[3]))
                else:
                    _declared = sum(int(round(rooms[(lvl, rid)]["r"]["_area"] * U * U))
                                    for rid in _ids)
                    m.Add(_got >= int(COVERAGE * _declared))
        else:
            # PER ELEMENT (WP-11.6 item 4). Against the whole building's floor area this floor
            # is either unsatisfiable — a dependency's rooms cannot cover the main block — or
            # vacuous. With one element the loop runs once, over every room in `rs`, against
            # `Wi * Hi`: the line it replaces.
            for _bx in sorted({boxes[(lvl, r["id"])] for r in rs}):
                _area_b = sum(rooms[(lvl, r["id"])]["a"] for r in rs
                              if boxes[(lvl, r["id"])] == _bx)
                m.Add(_area_b >= int(COVERAGE * (_bx[2] - _bx[0]) * (_bx[3] - _bx[1])))

        # ---- TILING, THE FIRST OF THE TYPE'S FACTS (WP-13.3), stated ABOVE the capacity floor
        #
        # The floor above is what infeasibility is measured against and never moves. This is
        # the fact the type states -- the rooms of a level tile the element they stand in --
        # as one literal per (level, element), kind "tiling", released by the ladder only after
        # the walls and the axis and named when it is. With no-overlap and containment already
        # hard, `sum(areas) >= TILING * box` at 1.0 is an exact tiling. On an upper level over
        # an open court the court's own area comes off the target, as the floor's does: the
        # storey must tile everything that is not the hole (OQ 55). `_absorb` then has nothing
        # to grow into on a level that held this, which is the point -- the residue the gate
        # read as a powder room open to the drawing room was the floor's 3%.
        _t100 = int(round(TILING * 100))
        _groups = []
        if els.get(lvl):
            for _ei, _e in enumerate(els[lvl]):
                _ids = [rid for rid in (_e.get("rooms") or []) if (lvl, rid) in rooms]
                if _ids:
                    _groups.append((_ei, _e.get("id") or _e.get("role") or str(_ei),
                                    ebox[(lvl, _ids[0])], _ids))
        else:
            _groups.append((0, "main", (0, 0, Wi, Hi), [r["id"] for r in rs]))
        for _ei, _eid, (_gx, _gy, _gW, _gH), _ids in _groups:
            _got = sum(rooms[(lvl, rid)]["a"] for rid in _ids)
            _key = (lvl, _ei)
            if _dk("tiling", _key) in downgraded:
                reqs.notes.append(
                    f"level {lvl}, element {_ei} ({_eid}): the rooms could not tile it exactly "
                    f"together with the other declared facts — the tiling fact is downgraded, "
                    f"the capacity floor of {COVERAGE:.0%} still holds, and the residue is "
                    f"named on the record as floor inside no room")
                continue
            _tl = reqs.lit(f"the rooms of level {lvl} tile massing element {_ei} ({_eid}) "
                           f"exactly — no floor is no room (the type's own fact, WP-13.3)",
                           kind="tiling", key=_key)
            if voids_below and _eid == "main":
                _void_area = sum(rooms[(0, v["id"])]["a"] for v in voids_below
                                 if (0, v["id"]) in rooms)
                m.Add(100 * _got + _t100 * _void_area >= _t100 * _gW * _gH).OnlyEnforceIf(_tl)
            else:
                m.Add(100 * _got >= _t100 * _gW * _gH).OnlyEnforceIf(_tl)

        # ---- declared exterior walls
        contested = _contested_corners(rs)
        for r in rs:
            v = rooms[(lvl, r["id"])]
            walls = list(r.get("exterior_walls") or [])
            _ex, _ey, _eW, _eH = ebox.get((lvl, r["id"]), (0, 0, Wi, Hi))
            # WP-11.11, and it is WP-11.9's ruling 4 inside the solver: exterior is exterior.
            # A face on the dependency's own boundary carries a window, a sill, a load and the
            # weather, so a room's declared wall is a fact about ITS element.
            pins = {"S": v["y"] == _ey, "N": v["y"] + v["h"] == _ey + _eH,
                    "W": v["x"] == _ex, "E": v["x"] + v["w"] == _ex + _eW}
            diag_ok = [wl for wl in walls if wl in pins]
            if not diag_ok:
                continue
            softened = _protruding(r) or r["id"] in contested
            if softened:
                why = "it protrudes" if _protruding(r) else "its corner is contested"
                if r["id"] in contested:
                    reqs.notes.append(f"{r.get('name') or r['id']}: {contested[r['id']]}")
                lit = reqs.lit(f"{r.get('name') or r['id']} declares exterior walls "
                               f"{'/'.join(walls)} — {why}, so it must reach at "
                               f"least one of them (the others are scored, not forced)",
                               kind="wall-soft")
                touch = []
                for wl in diag_ok:
                    b = m.NewBoolVar("")
                    m.Add(pins[wl]).OnlyEnforceIf(b)
                    touch.append(b)
                m.AddBoolOr(touch).OnlyEnforceIf(lit)
                if objective:
                    # unreached declared walls keep the heuristic's own 14-point score
                    for b in touch:
                        penalties.append((b.Not(), 14 * SCALE // max(1, len(touch))))
            else:
                for wl in diag_ok:
                    key = (lvl, r["id"], wl)
                    if _dk("wall", key) in downgraded:
                        # downgraded pins carry their proof status honestly:
                        # "proven" only after the reinstatement pass tested THIS
                        # pin alone at THIS footprint; a pin the budget never
                        # re-proved says it was carried, never that it was proven
                        how = ("carried — off a conflict core or an undecided round, not individually "
                               "re-proven in budget" if _dk("wall", key) in unproven else
                               "proven — restored alone, no placement exists")
                        reqs.notes.append(
                            f"{r.get('name') or r['id']}'s declared {wl} wall could not "
                            f"co-hold with the other declared facts ({how}) — read as "
                            f"exposure in the massing, scored, not forced")
                        if objective:
                            b = m.NewBoolVar("")
                            m.Add(pins[wl]).OnlyEnforceIf(b)
                            penalties.append((b.Not(), 14 * SCALE))
                    else:
                        lit = reqs.lit(f"{r.get('name') or r['id']} declares an exterior "
                                       f"wall on the {wl} — it must sit on that boundary",
                                       kind="wall", key=key)
                        m.Add(pins[wl]).OnlyEnforceIf(lit)

        idx0 = {r["id"]: r for r in rs}

        # ---- THE SPANNING PASSAGE, ON THE BLOCK'S OWN AXIS (WP-11.7)
        #
        # A circulation room declaring an OPPOSITE PAIR is the centre passage, and this file's
        # own docstring has said since WP-2.3 that "its two pins ARE the spanning rule". They
        # were -- until WP-11.7 ranked the shape band above the wall pins, at which point the
        # first infeasible round releases all 22 of them and the spanning rule goes with them.
        # Measured: the Tidewater passage came back 40 ft wide and 9 ft deep, running across
        # the house instead of through it, and `plan_check`'s entrance-axis census read
        # `passage_has_no_through_axis: 1` and compared nothing.
        #
        # So the rule is stated as itself rather than inferred from two pins that now rank
        # below it: the room SPANS its declared pair, and its centreline is the block's.
        # `kind="axis"`, ranked between wall and shape -- more authored than the corpus's rule
        # about a room type, less authored than nothing (it is read off THIS record's own
        # `exterior_walls`, and it is the diagram the parti is named for).
        #
        # It is one requirement, not two, so a conflict names the passage and its axis rather
        # than an anonymous pair of inequalities -- the same reason the programme size is one
        # literal per room.
        # WHICH room, and it is NOT "every circulation room declaring an opposite pair".
        # Written that way first, and measured: on the Tidewater record it selects TWO -- the
        # Centre Passage and the Back Hall (a `back-hall` is circulation and declares N and S
        # as a hyphen, not as a spine). Two rooms both pinned to the block's centre line cannot
        # both hold, so the round loop released BOTH axis pins and the passage went back to
        # running across the house. An axis rule that names two rooms names none.
        #
        # The one it means is the room the FRONT DOOR OPENS INTO -- which is exactly the
        # relation `plan_check`'s own entrance-axis census walks, threshold room to circulation
        # room, so the placer aims at the thing the critic measures. Where that picks out no
        # room, or more than one, the axis is UNJUDGED and nothing is pinned: a spine the record
        # does not single out is not one this engine may invent.
        _entered = set()
        for r in rs:
            if _cls(r.get("type")) != "threshold":
                continue
            if not any(d.get("to") == "exterior" for d in (r.get("doors") or [])):
                continue
            for d in (r.get("doors") or []):
                t = d.get("to")
                if t and t != "exterior" and (lvl, t) in rooms \
                        and _cls((idx0.get(t) or {}).get("type")) == "circulation":
                    _entered.add(t)
        _spines = [r for r in rs if r["id"] in _entered
                   and ({"S", "N"} <= set(r.get("exterior_walls") or [])
                        or {"W", "E"} <= set(r.get("exterior_walls") or []))]
        if len(_spines) != 1:
            if any(_cls(r.get("type")) == "circulation"
                   and ({"S", "N"} <= set(r.get("exterior_walls") or [])
                        or {"W", "E"} <= set(r.get("exterior_walls") or [])) for r in rs):
                reqs.notes.append(
                    f"level {lvl}: {len(_spines)} circulation room(s) reached from the front "
                    f"door declare an opposite pair, so which one is the spine is UNJUDGED and "
                    f"no axis is pinned — one room, or none")
        for r in _spines:
            walls = set(r.get("exterior_walls") or [])
            v = rooms[(lvl, r["id"])]
            _ex, _ey, _eW, _eH = ebox.get((lvl, r["id"]), (0, 0, Wi, Hi))
            if {"S", "N"} <= walls:
                span, ctr, ext = (v["y"], v["h"], _eH), (v["x"], v["w"], _eW), "N-S"
            elif {"W", "E"} <= walls:
                span, ctr, ext = (v["x"], v["w"], _eW), (v["y"], v["h"], _eH), "E-W"
            else:
                continue
            key = (lvl, r["id"])
            if _dk("axis", key) in downgraded:
                reqs.notes.append(
                    f"{r.get('name') or r['id']}'s through-axis could not co-hold with the "
                    f"other declared facts — downgraded, so it may be drawn across the house "
                    f"rather than through it")
                continue
            _ax = reqs.lit(f"{r.get('name') or r['id']} runs {ext} through the house and sits "
                           f"on its centre line — it declares both {ext.replace('-', ' and ')} "
                           f"walls, which is the spanning rule",
                           kind="axis", key=key)
            m.Add(span[0] == 0).OnlyEnforceIf(_ax)
            m.Add(span[0] + span[1] == span[2]).OnlyEnforceIf(_ax)
            # SPANNING ONLY, AND THE CENTRING IS REFUSED WITH ITS MEASUREMENT.
            #
            # `PLAN-OF-ACTION.md` asks for "the spanning passage pinned on the block axis" and
            # the plan file spells it `2x + w == W`. Built and measured: with the shape bands
            # held and ALL 22 wall pins already released -- the most permissive model this
            # engine can offer -- adding the centring makes it INFEASIBLE in 0.9 s.
            #
            # The arithmetic says why, and it is a fact about the record rather than the
            # solver. The Centre Passage declares 12 x 34 ft; spanning the 40.08 ft depth puts
            # it 10.2 ft wide, and centred on a 60 ft front that leaves two strips of 24.9 ft
            # holding about 2,000 sf of programme in 1,992 sf of floor. That is an exact tiling
            # of both strips, by rooms that must each also sit inside their own proportion
            # band. There is no slack anywhere in it -- which is
            # `oq/the-placement-carries-no-wall-bands` measured from the other side.
            #
            # So the axis pin states the half that HOLDS: the passage runs through the house.
            # Its position along the front is left to the objective, where a centre-passage
            # term has scored it since WP-2.2. Do not reinstate the equality without first
            # re-running this measurement; a symmetric passage needs the footprint to gain the
            # slack that question is about, not a harder constraint.

        # ---- THE HEARTH ON ITS FLUE (WP-13.3), kind "hearth", ranked ABOVE the wall pins
        #
        # A room stating a fire on wall X, where X is a face the massing puts a flue on
        # (`hearths.flue_walls`, the one spelling), has its X edge pinned to its element's X
        # face -- the same equality a declared exterior wall takes, under its own literal, so
        # that when the ladder releases the room's `exterior_walls` (first, by ruling) the wall
        # the flue stands on stays held. On the reference plan the prover had released the
        # dining and drawing rooms' declared W walls and `hearths.breast` then drew their fires
        # 19 and 25 ft inboard of the west face, against a partition, with no exterior wall to
        # carry a flue (WP-13.1's gate, WP-13.2's refusal). Where the massing cannot be read,
        # or X is not a flue wall, the fact is UNJUDGED by name and nothing is pinned -- an
        # interior stack is not modelled and is not invented in its place.
        #
        # THE SHARED FLUE IS NOT THIS PIN'S QUESTION. Two rooms on one flue each pin their own
        # wall; where their breasts then stand 13 ft apart along it, one shaft cannot stand
        # behind both, and that is `oq/a-shared-flue-cannot-stand-behind-two-centred-breasts`,
        # open for a ruling. Nothing here moves a breast or splits a flue.
        _seen_fires = set()
        for r in rs:
            fires = r.get("hearth") or []
            if not fires or (lvl, r["id"]) not in rooms:
                continue
            v = rooms[(lvl, r["id"])]
            _ex, _ey, _eW, _eH = ebox.get((lvl, r["id"]), (0, 0, Wi, Hi))
            _fpins = {"S": v["y"] == _ey, "N": v["y"] + v["h"] == _ey + _eH,
                      "W": v["x"] == _ex, "E": v["x"] + v["w"] == _ex + _eW}
            _nm = r.get("name") or r["id"]
            for h in fires:
                wl = (h.get("wall") or "").upper()
                key = (lvl, r["id"], wl)
                if key in _seen_fires:
                    continue            # two fires on one wall of one room share one pin
                _seen_fires.add(key)
                if _flue_walls is None:
                    reqs.refuse("hearth", key,
                                f"{_nm}'s fire names its {wl or 'unnamed'} wall and {_flue_why}")
                    continue
                if wl not in _fpins or wl not in _flue_walls:
                    reqs.refuse("hearth", key,
                                f"{_nm}'s fire names its {wl or 'unnamed'} wall and the massing "
                                f"puts its flues on {'/'.join(_flue_walls) or 'no exterior wall'}; "
                                f"a fire on a wall no flue stands on is not this model's fact "
                                f"(plan_check's hearth layer reports it as off the stack wall)")
                    continue
                if _dk("hearth", key) in downgraded:
                    how = ("carried — off a conflict core or an undecided round, not individually re-proven in "
                           "budget" if _dk("hearth", key) in unproven else
                           "proven — restored alone, no placement exists")
                    reqs.notes.append(
                        f"{_nm}'s fire on its {wl} wall could not stand on the element's {wl} "
                        f"face together with the other declared facts ({how}) — downgraded, "
                        f"scored at the wall's own 14 points, and the drawn layer will refuse "
                        f"the breast rather than draw a fire with no flue")
                    if objective:
                        b = m.NewBoolVar("")
                        m.Add(_fpins[wl]).OnlyEnforceIf(b)
                        penalties.append((b.Not(), 14 * SCALE))
                    continue
                lit = reqs.lit(f"{_nm}'s fire stands on its {wl} wall, a face the massing puts "
                               f"a flue on — the room's {wl} edge is the element's {wl} face "
                               f"(the hearth on its flue, WP-13.3)",
                               kind="hearth", key=key)
                m.Add(_fpins[wl]).OnlyEnforceIf(lit)

        # ---- doors: declared topology must be geometrically real
        idx = idx0
        seen = set()
        for r in rs:
            v1 = rooms[(lvl, r["id"])]
            for d in (r.get("doors") or []):
                to = d["to"]
                if to == "exterior":
                    lit = reqs.lit(f"{r.get('name') or r['id']} has a door to the exterior "
                                   f"— it must reach the building envelope", kind="door")
                    onb = []
                    _ex, _ey, _eW, _eH = ebox.get((lvl, r["id"]), (0, 0, Wi, Hi))
                    for cond in (v1["y"] == _ey, v1["y"] + v1["h"] == _ey + _eH,
                                 v1["x"] == _ex, v1["x"] + v1["w"] == _ex + _eW):
                        b = m.NewBoolVar("")
                        m.Add(cond).OnlyEnforceIf(b)
                        onb.append(b)
                    m.AddBoolOr(onb).OnlyEnforceIf(lit)
                    continue
                if to not in idx:
                    continue                    # other-level or outdoor: not this model's fact
                key = tuple(sorted((r["id"], to)))
                if key in seen:
                    continue
                seen.add(key)
                # A DOOR ACROSS OPEN GROUND IS NOT THIS MODEL'S FACT EITHER, AND MAKING IT ONE
                # WOULD PROVE A BUILDABLE HOUSE IMPOSSIBLE (WP-11.6 item 4). The constraint
                # below is a hard abutment — `a["x"] + a["w"] == b["x"]` — which is exactly what
                # a hyphen buys and exactly what a detached dependency cannot give: the elements
                # are laid by `blocks_for` with a gap between them, and no placement of rooms
                # inside two separated rectangles can put a leaf across the gap. The heuristic
                # charges such a door and draws it `unplaced` with a reason (measured 5 of 5 on
                # this package's own fixture); the prover must say the same thing rather than
                # return INFEASIBLE, or a diagram whose service block is genuinely detached
                # would come back as a brief that cannot be built.
                if not _abuts(boxes[(lvl, r["id"])], boxes[(lvl, to)]):
                    reqs.notes.append(
                        f"{r.get('name') or r['id']} and {idx[to].get('name') or to} declare a "
                        f"door and stand in massing elements that do not touch — no placement "
                        f"of rooms inside two separated rectangles can put a leaf across the "
                        f"gap, so this door is left to the drawn layer to report unplaced "
                        f"rather than made an infeasibility of the house")
                    continue
                v2 = rooms[(lvl, to)]
                ovr = _door_overlap(d, v1, v2)
                lit = reqs.lit(f"{r.get('name') or r['id']} and {idx[to].get('name') or to} "
                               f"share a door — they must share enough wall for one",
                               kind="door")
                configs = []
                for a1, b1_ in ((v1, v2), (v2, v1)):
                    # overlap >= ovr needs all FOUR bounds: the two end-gap
                    # inequalities alone admit a side narrower than ovr sitting
                    # strictly inside the neighbour's span (a 2 ft landing
                    # against a 34 ft passage passes both and shares 2 ft)
                    b = m.NewBoolVar("")
                    m.Add(a1["x"] + a1["w"] == b1_["x"]).OnlyEnforceIf(b)
                    m.Add(a1["y"] <= b1_["y"] + b1_["h"] - ovr).OnlyEnforceIf(b)
                    m.Add(b1_["y"] <= a1["y"] + a1["h"] - ovr).OnlyEnforceIf(b)
                    m.Add(a1["h"] >= ovr).OnlyEnforceIf(b)
                    m.Add(b1_["h"] >= ovr).OnlyEnforceIf(b)
                    configs.append(b)
                    b2 = m.NewBoolVar("")
                    m.Add(a1["y"] + a1["h"] == b1_["y"]).OnlyEnforceIf(b2)
                    m.Add(a1["x"] <= b1_["x"] + b1_["w"] - ovr).OnlyEnforceIf(b2)
                    m.Add(b1_["x"] <= a1["x"] + a1["w"] - ovr).OnlyEnforceIf(b2)
                    m.Add(a1["w"] >= ovr).OnlyEnforceIf(b2)
                    m.Add(b1_["w"] >= ovr).OnlyEnforceIf(b2)
                    configs.append(b2)
                m.AddBoolOr(configs).OnlyEnforceIf(lit)

        # ---- soft: bay snapping with counted relaxations, per room edge
        if objective:
            for r in rs:
                v = rooms[(lvl, r["id"])]
                # WP-11.11. The DOMAIN spans every element (a west dependency sits at a
                # negative x, and `NewIntVar(0, span)` here would have made a SOFT term
                # infeasible), and the top line the y edge may legitimately sit on is the
                # room's OWN element's, not the main block's.
                _ex, _ey, _eW, _eH = ebox.get((lvl, r["id"]), (0, 0, Wi, Hi))
                for axis, dlo, dhi, top in (("x", gx0, gx1, None),
                                            ("y", gy0, gy1, _ey + _eH)):
                    edges = (v["x"], (v["x"] + v["w"])) if axis == "x" \
                        else (v["y"], (v["y"] + v["h"]))
                    span = max(1, dhi - dlo)
                    for e in edges:
                        ev = m.NewIntVar(dlo, dhi, "")
                        m.Add(ev == e)
                        # AddModuloEquality TRUNCATES toward zero, so a negative dividend
                        # gives a negative remainder and `emod`'s [0, bay-1] domain would make
                        # this SOFT term infeasible on a west dependency. The edge is shifted
                        # by a whole number of bays first -- `dlo` floored to the module, so
                        # the grid's own phase is untouched -- and the modulo sees a
                        # non-negative number. Inert on every plan in the corpus, where
                        # `dlo` is 0.
                        base = (dlo // bayU) * bayU
                        if base:
                            evp = m.NewIntVar(0, max(1, dhi - base), "")
                            m.Add(evp == ev - base)
                        else:
                            evp = ev          # every plan in the corpus; no extra variable
                        emod = m.NewIntVar(0, bayU - 1, "")
                        m.AddModuloEquality(emod, evp, bayU)
                        d = m.NewIntVar(0, bayU, "")
                        m.AddMinEquality(d, [emod, bayU - emod])
                        if axis == "y":
                            # the element's own top edge is a legitimate line even off-module
                            dH = m.NewIntVar(0, span, "")
                            dfH = m.NewIntVar(-span, span, "")
                            m.Add(dfH == ev - top)
                            m.AddAbsEquality(dH, dfH)
                            dmin = m.NewIntVar(0, span, "")
                            m.AddMinEquality(dmin, [d, dH])
                            d = dmin
                        off = m.NewBoolVar("")
                        m.Add(d <= tolU).OnlyEnforceIf(off.Not())
                        penalties.append((off, 15))     # 1.5 per relaxation, x10

    # ---- DECLARED STACKS, HARD BY CONTAINMENT (WP-13.3), kind "stack"
    #
    # A `stacks_over` claim is the record saying this room stands OVER that one, and it is
    # judged by `stacking.lands`: the smaller of the two rectangles at least `LANDS_FRACTION`
    # (90%) of its own area inside the larger. The model states THAT relation, transcribed in
    # `_lands_literal` with the fraction read off `stacking.py`, so a placement proved under the
    # literal lands by construction and `tests/test_type_facts_hard.py` holds the two together
    # by running `stacking.judge` over the proved record.
    #
    # THE LINEAR PROXY WAS TRIED FIRST AND MEASURED OUT. The first draft stated "the room with
    # the smaller DECLARED area lies entirely inside the other" -- four inequalities, no
    # products, and a claim about the rooms the author wrote. On `plans/tidewater-georgian-
    # careful.json` with the walls, hearth, tiling and bearing released, each of the five
    # proxies holds ALONE (OPTIMAL in 5.6 to 23.9 s) and the five together are INFEASIBLE with
    # the sizes and shape bands (the core names all five). Full containment is a stronger
    # statement than the rule, and a fact stated more strongly than the corpus states it
    # refuses a house the corpus admits -- the fake-infeasible direction, which is as
    # dishonest as a fake pass. Three products per claim is the price of saying what the rule
    # says, and CP-SAT carries them as it carries the shape pins' max/min.
    #
    # It replaces the soft intersection penalty WP-7.4 carried here, whose own comment said it
    # waited on the downgrade ladder learning a second kind: a held stack needs no charge and a
    # released one keeps `GEO.STACK_W`, the charge the search pays for the same thing, so the
    # two engines still score one house alike. `wet_stack_with` stays soft above.
    #
    # UNJUDGED BY NAME, NEVER HELD BY ABSENCE: a claim whose target is not on the level below
    # is `stacking.py`'s to explain, and a claim across two massing elements is one no placement
    # this engine makes can keep (it lays only the ground level into elements), so both are
    # refused with their reason rather than pinned or dropped.
    _ground_by_id = {r["id"]: r for r in (prep.get(0) or [])}
    for r in (prep.get(1) or []):
        so = r.get("stacks_over")
        if not so or (1, r["id"]) not in rooms:
            continue
        key = (1, r["id"])
        _nm = r.get("name") or r["id"]
        if (0, so) not in rooms:
            reqs.refuse("stack", key,
                        f"{_nm} declares it stacks over {so!r}, which is not a placed room on the "
                        f"level below (the stacking tally on the record names the reason)")
            continue
        if boxes.get((1, r["id"])) != boxes.get((0, so)):
            reqs.refuse("stack", key,
                        f"{_nm} declares it stacks over {so!r}, which stands in another massing "
                        f"element; the placer lays only the ground level into elements, so no "
                        f"upper room can be placed over it")
            continue
        u, g = rooms[(1, r["id"])], rooms[(0, so)]
        _gname = _ground_by_id[so].get("name") or so
        # THE RELATION IS BUILT ONLY WHERE SOMETHING READS IT. A released stack in the hard-only
        # phase carried its product structures anyway in the first draft -- unconstrained, and
        # not free: the shapes-only state the ladder falls back to went from OPTIMAL in 9 s to
        # UNKNOWN at 10 s on the reference plan with five dangling products in the model.
        if _dk("stack", key) in downgraded:
            how = ("carried — off a conflict core or an undecided round, not individually re-proven in budget"
                   if _dk("stack", key) in unproven else
                   "proven — restored alone, no placement exists")
            reqs.notes.append(
                f"{_nm}'s declared stack over {_gname} could not land together with the other "
                f"declared facts ({how}) — downgraded, charged at {GEO.STACK_W:g} points as the "
                f"search charges it, and the stacking tally on the record will say whether it "
                f"lands")
            if objective:
                lands = _lands_literal(m, u, g, (gx0, gy0, gx1, gy1))
                penalties.append((lands.Not(), _w(GEO.STACK_W)))
            continue
        lit = reqs.lit(f"{_nm} stands over {_gname}: the smaller of the two drawn rooms lies at "
                       f"least {STK.LANDS_FRACTION:.0%} inside the larger — stacking.lands' own "
                       f"relation, as a fact (declared stacks, WP-13.3)",
                       kind="stack", key=key)
        m.AddImplication(lit, _lands_literal(m, u, g, (gx0, gy0, gx1, gy1)))

    # ---- nothing sits over a void open to the sky (OQ 55)
    #
    # This is the guarantee the 25 Aug merge lost. OQ 55 closed with the rule stated in BOTH
    # engines, and the engine that stated it as a HARD constraint -- the deleted build/solver.py
    # -- is the one that did not survive; what was left was geometry.py's 40-point charge, which
    # is a price a candidate can pay and still win. A courtyard is a hole: there is no floor
    # under an upper room placed over it, no bearing, and the roof that room needs is the hole
    # itself. That is not a preference and it is not scoreable, so here it is a constraint.
    #
    # ROOFED voids are deliberately exempt, and the exemption is the reason `roofed` is a
    # separate fact from `within_footprint`: a Charleston single's upper piazza sits squarely on
    # its lower one and is correct. A void over a void is likewise fine -- an upper gallery may
    # open onto the same court.
    #
    # Mirrors geometry.py's vertical_score() term for term, including its 1.0 ft overlap
    # tolerance, so the two engines cannot disagree about what "over" means. The RING remains
    # stated rather than searched (courtyard_slice()'s guillotine tree, which the CP engine
    # inherits through the heuristic hint) -- that half of OQ 55 is a layout problem, not a
    # constraint, and is left stated rather than half-solved.
    ground_rooms = prep.get(0) or []
    upper_rooms = prep.get(1) or []
    open_voids = [r for r in ground_rooms
                  if isinstance(r.get("_void"), dict) and not r["_void"].get("roofed")]
    if open_voids and upper_rooms:
        # STRICT: the rooms may abut the void's edge and may not enter it by any amount.
        # geometry.py charges its 40 points only past a 1.0 ft overlap, and mirroring that
        # tolerance here was a real bug for two reasons. A scoring noise-tolerance is not a
        # placement licence -- 1 ft of bedroom over a courtyard is a foot of floor with nothing
        # under it. And it broke the guarantee downstream: the solver placed a room exactly 1 ft
        # into the court, and _absorb's keep-out limiter only stops a room that has not already
        # crossed the line, so the room grew straight through the hole. Proven, then undone.
        for ur in upper_rooms:
            if isinstance(ur.get("_void"), dict):
                continue                    # void over void is fine
            uv = rooms.get((1, ur["id"]))
            if uv is None:
                continue
            for vr in open_voids:
                gv = rooms.get((0, vr["id"]))
                if gv is None:
                    continue
                lit = reqs.lit(
                    f"{ur.get('name') or ur['id']} cannot sit over "
                    f"{vr.get('name') or vr['id']}, which is open to the sky: no floor under "
                    f"it, no bearing, and the roof it needs is the hole",
                    kind="void")
                # Separated on one axis or the other, by more than the shared tolerance.
                seps = []
                for cond in (uv["x"] + uv["w"] <= gv["x"],
                             gv["x"] + gv["w"] <= uv["x"],
                             uv["y"] + uv["h"] <= gv["y"],
                             gv["y"] + gv["h"] <= uv["y"]):
                    b = m.NewBoolVar("")
                    m.Add(cond).OnlyEnforceIf(b)
                    seps.append(b)
                m.AddBoolOr(seps).OnlyEnforceIf(lit)

    # ---- entrance front. HARD only for the threshold room that actually opens
    # to the exterior — that is the entry. The room catalog classes mudrooms
    # and entrance halls as threshold too, and WP-2.2's entrance_score charges
    # every one of them 100 points off the front (a finding, see the WP-2.3
    # report); those stay SOFT at the same 100 so the engines score alike, but
    # a service threshold can never render a brief infeasible.
    ground = prep.get(0) or []
    Wi0, Hi0 = int(round(fpd["W"] * U)), int(round(fpd["H"] * U))
    if ewalls:
        byid = {r["id"]: r for r in ground}
        for r in ground:
            if _cls(r["type"]) != "threshold" or (0, r["id"]) not in rooms:
                continue
            v = rooms[(0, r["id"])]
            # THE HARD PIN IS ON THE ROOM'S OWN ELEMENT (WP-11.6 item 4). A wing has its own
            # front, and pinning an entry that stands in one to the MAIN block's boundary would
            # prove a buildable house impossible — the one thing a hard constraint here must
            # never do. The SOFT mirrors below keep the main block's frame deliberately, because
            # `entrance_score` and the zoning scorers measure there in BOTH engines and a frame
            # changed in one engine only is how the two come to disagree about one house.
            _p0x, _p0y, _p1x, _p1y = boxes[(0, r["id"])]
            pins = {"S": v["y"] == _p0y, "N": v["y"] + v["h"] == _p1y,
                    "W": v["x"] == _p0x, "E": v["x"] + v["w"] == _p1x}
            opens_out = any(d.get("to") == "exterior" for d in (r.get("doors") or []))
            onb = []
            for wl in ewalls:
                if wl not in pins:
                    continue
                b = m.NewBoolVar("")
                m.Add(pins[wl]).OnlyEnforceIf(b)
                onb.append(b)
            if not onb:
                continue
            if opens_out:
                lit = reqs.lit(f"the entrance faces {'/'.join(sorted(ewalls))} and "
                               f"{r.get('name') or r['id']} is the entry — it must sit "
                               f"on that front", kind="entrance")
                m.AddBoolOr(onb).OnlyEnforceIf(lit)
            elif objective:
                off = m.NewBoolVar("")
                m.AddBoolOr(onb + [off])
                penalties.append((off, 100 * SCALE))
            if objective:
                for d in (r.get("doors") or []):
                    t = d["to"]
                    if t in byid and _cls(byid[t]["type"]) == "circulation" and (0, t) in rooms:
                        vt = rooms[(0, t)]
                        tpins = {"S": vt["y"] <= 1, "N": vt["y"] + vt["h"] >= Hi0 - 1,
                                 "W": vt["x"] <= 1, "E": vt["x"] + vt["w"] >= Wi0 - 1}
                        onbt = []
                        for wl in ewalls:
                            if wl not in tpins:
                                continue
                            bb = m.NewBoolVar("")
                            m.Add(tpins[wl]).OnlyEnforceIf(bb)
                            onbt.append(bb)
                        if onbt:
                            far = m.NewBoolVar("")
                            m.AddBoolOr(onbt + [far])
                            penalties.append((far, 40 * SCALE))

    # ---- soft zoning + ceremonial depth + centre passage + wet stacks
    if objective and ewalls and ground:
        def dist_var(v):
            exprs = []
            for wl in ewalls:
                if wl == "S": exprs.append(v["y"])
                elif wl == "N": exprs.append(Hi0 - (v["y"] + v["h"]))
                elif wl == "W": exprs.append(v["x"])
                elif wl == "E": exprs.append(Wi0 - (v["x"] + v["w"]))
            dv = m.NewIntVar(*_wide(0, max(Wi0, Hi0)), name="")
            m.AddMinEquality(dv, exprs)
            return dv

        OPP = {"S": "N", "N": "S", "W": "E", "E": "W"}
        rear = [OPP[w] for w in ewalls if w in OPP]
        dists = {}
        byid = {r["id"]: r for r in ground}
        for r in ground:
            if (0, r["id"]) not in rooms:
                continue
            v = rooms[(0, r["id"])]
            fc = _cls(r["type"])
            if fc in ("public", "living", "dining", "service", "work") or \
                    C["rooms"].get(r["type"], {}).get("privacy_rank") is not None:
                dists[r["id"]] = dist_var(v)
            if fc in ("public", "living", "dining"):
                p = m.NewBoolVar("")
                m.Add(dists[r["id"]] <= 1).OnlyEnforceIf(p.Not())
                penalties.append((p, 35))
            elif fc in ("service", "work"):
                rd_exprs = []
                for wl in rear:
                    if wl == "S": rd_exprs.append(v["y"])
                    elif wl == "N": rd_exprs.append(Hi0 - (v["y"] + v["h"]))
                    elif wl == "W": rd_exprs.append(v["x"])
                    elif wl == "E": rd_exprs.append(Wi0 - (v["x"] + v["w"]))
                if rd_exprs:
                    rd = m.NewIntVar(*_wide(0, max(Wi0, Hi0)), name="")
                    m.AddMinEquality(rd, rd_exprs)
                    p = m.NewBoolVar("")
                    m.Add(rd <= 1).OnlyEnforceIf(p.Not())
                    penalties.append((p, 20))
                pf = m.NewBoolVar("")
                m.Add(dists[r["id"]] >= 2).OnlyEnforceIf(pf.Not())
                penalties.append((pf, 30))
        for r in ground:
            rank = C["rooms"].get(r["type"], {}).get("privacy_rank")
            if rank is None or r["id"] not in dists:
                continue
            for d in (r.get("doors") or []):
                t = d["to"]
                trank = C["rooms"].get(byid.get(t, {}).get("type", ""), {}).get("privacy_rank") \
                    if t in byid else None
                if trank is None or trank <= rank or t not in dists:
                    continue
                p = m.NewBoolVar("")
                m.Add(dists[t] >= dists[r["id"]] - 1).OnlyEnforceIf(p.Not())
                penalties.append((p, 6 * (trank - rank) * SCALE))
        for r in ground:
            if "centre" in (r["type"] or "") or "center" in (r["type"] or ""):
                v = rooms[(0, r["id"])]
                cd = m.NewIntVar(*_wide(-Wi0 * 2, Wi0 * 2), name="")
                m.Add(cd == 2 * v["x"] + v["w"] - Wi0)
                cda = m.NewIntVar(*_wide(0, Wi0 * 2), name="")
                m.AddAbsEquality(cda, cd)
                penalties.append((cda, 1))

    if objective:
        upper = prep.get(1) or []
        wet_g = [r for r in ground if set(r.get("fixtures") or []) and (0, r["id"]) in rooms]
        for r in upper:
            if not set(r.get("fixtures") or []) or (1, r["id"]) not in rooms:
                continue
            v = rooms[(1, r["id"])]
            over = []
            for g in wet_g:
                vg = rooms[(0, g["id"])]
                b = m.NewBoolVar("")
                m.Add(v["x"] < vg["x"] + vg["w"]).OnlyEnforceIf(b)
                m.Add(vg["x"] < v["x"] + v["w"]).OnlyEnforceIf(b)
                m.Add(v["y"] < vg["y"] + vg["h"]).OnlyEnforceIf(b)
                m.Add(vg["y"] < v["y"] + v["h"]).OnlyEnforceIf(b)
                over.append(b)
            none = m.NewBoolVar("")
            m.AddBoolOr(over + [none])
            penalties.append((none, 8 * SCALE))

    # ---- BEARING CONTINUITY AND THE SPAN CAPACITY, HARD (WP-13.3), kind "bearing"
    #
    # `structure.bearing_lines` calls an interior wall bearing where it falls on the bay grid
    # (within 0.75 ft of a module multiple) and `structure.span_check` asks that consecutive
    # bearing lines be no further apart than the framing tradition's capacity (20 ft for the
    # timber-bay styles, the joist table's deepest member otherwise -- `_span_capacity` reads
    # it as `span_check` decides it). WP-7.4 CHARGED that as a soft term and the gate read the
    # Tidewater upper floor as one 63 ft clear span with no bearing line at all. It is a fact
    # now, one literal per (element, axis):
    #
    #   candidate lines   the module multiples strictly inside the element's box (on the 1 ft
    #                     grid the only positions within 0.75 ft of a multiple ARE the
    #                     multiples), with the box's own edges as bearing by definition
    #   has[level][L]     -> some room edge of that level sits on L (half-reified: a line may
    #                     be claimed only where a wall really stands on it)
    #   bearing[L]        -> has[level][L] for EVERY placed level in the element, so a bearing
    #                     line exists only where both storeys stand a wall on it -- which IS
    #                     continuity by construction, and the upper storey of a one-storey
    #                     element is simply absent from the conjunction
    #   continuity        an UPPER edge on a candidate line needs a ground edge on it: an
    #                     upper partition standing on nothing is a transfer beam, and the
    #                     gate's row reads every upper bearing line against the ground's
    #   capacity          every window of consecutive candidate-or-box lines longer than the
    #                     capacity contains a bearing line strictly inside it
    #
    # RELEASED, the (element, axis) keeps WP-7.4's charge -- `GEO.SPAN_W` per anchor that cannot
    # reach a bearing line, per level, the term this block used to be -- so a released fact is
    # scored as the search scores it rather than forgotten. That charge is NOT the heuristic's
    # quantity and the old comment said so: `geometry._span_charge` charges once per
    # over-capacity span in proportion to its length, this anchors one clause at every grid
    # line (3x against 4x on a 60 ft run at a 10 ft bay); both grow with the span and neither
    # mis-ranks two placements that differ only in span.
    #
    # The `break` in the window loop is sound: for a given `lo_L` the SHORTEST over-capacity
    # window has the fewest inner lines, so its clause is the strictest and every longer
    # window's clause is implied by it. A window with NO candidate line inside it is a box
    # deeper than the capacity between its own two faces, which no wall can fix: the empty
    # clause makes the literal unsatisfiable and the ladder releases the fact by name.
    cap_ft = _span_capacity(plan)
    if cap_ft is None:
        reqs.refuse("bearing", None,
                    "the framing catalogue (construction/floor-structure.json) could not be "
                    "read, so no span capacity is known and no bearing line can be required")
    else:
        capU = int(cap_ft * U)
        _e0 = (els or {}).get(0) or [{"id": "main", "x": 0, "y": 0, "W": Wi / float(U),
                                      "H": Hi / float(U),
                                      "rooms": [r["id"] for r in (prep.get(0) or [])]}]
        for ei, _e in enumerate(_e0):
            _ex, _ey = int(round(_e["x"] * U)), int(round(_e["y"] * U))
            _eW, _eH = int(round(_e["W"] * U)), int(round(_e["H"] * U))
            _box = (_ex, _ey, _eW, _eH)
            # the rooms of each placed level standing in THIS element: the ground by the
            # element's own room list, the upper by its box (every upper room is laid into
            # the main block, so a dependency has a ground storey here and nothing above it)
            _rs_by_lvl = {}
            _g_ids = [r["id"] for r in (prep.get(0) or [])
                      if r["id"] in set(_e.get("rooms") or []) and (0, r["id"]) in rooms]
            if _g_ids:
                _rs_by_lvl[0] = _g_ids
            _u_ids = [r["id"] for r in (prep.get(1) or [])
                      if (1, r["id"]) in rooms and ebox.get((1, r["id"]), (0, 0, Wi, Hi)) == _box]
            if _u_ids:
                _rs_by_lvl[1] = _u_ids
            if not _rs_by_lvl:
                continue
            for axis, lo0, extent in (("x", _ex, _ex + _eW), ("y", _ey, _ey + _eH)):
                lines = list(range(lo0, extent + 1, bayU))
                if lines[-1] != extent:
                    lines.append(extent)
                inner_lines = lines[1:-1]
                key = (ei, axis)

                def _edge_vars(lvl_):
                    out = []
                    for rid in _rs_by_lvl[lvl_]:
                        v = rooms[(lvl_, rid)]
                        lo = v["x"] if axis == "x" else v["y"]
                        sz = v["w"] if axis == "x" else v["h"]
                        out += [lo, lo + sz]
                    return out

                def _windows():
                    for i, lo_L in enumerate(lines):
                        for hi_L in lines[i + 1:]:
                            if hi_L - lo_L <= capU:
                                continue
                            yield [L for L in lines[i + 1:] if L < hi_L]
                            break

                if _dk("bearing", key) in downgraded:
                    how = ("carried — off a conflict core or an undecided round, not individually re-proven in "
                           "budget" if _dk("bearing", key) in unproven else
                           "proven — restored alone, no placement exists")
                    reqs.notes.append(
                        f"element {ei} ({_e.get('id')}), {axis} axis: bearing continuity on the "
                        f"bay grid within the {cap_ft:g} ft capacity could not co-hold with the "
                        f"other declared facts ({how}) — downgraded, charged at "
                        f"{GEO.SPAN_W:g} points per unsupported run as the search charges it, "
                        f"and the record's span count says what was drawn")
                    if objective:
                        for lvl_ in _rs_by_lvl:
                            act = {}
                            for L in inner_lines:
                                faces = []
                                for e_ in _edge_vars(lvl_):
                                    f = m.NewBoolVar("")
                                    m.Add(e_ == L).OnlyEnforceIf(f)
                                    faces.append(f)
                                a_ = m.NewBoolVar("")
                                m.AddBoolOr(faces + [a_.Not()])   # a_ -> some face sits on L
                                act[L] = a_
                            for inner in _windows():
                                viol = m.NewBoolVar("")
                                m.AddBoolOr([act[L] for L in inner] + [viol])
                                penalties.append((viol, _w(GEO.SPAN_W)))
                    continue
                lit = reqs.lit(
                    f"massing element {ei} ({_e.get('id')}), {axis} axis: an interior wall on "
                    f"the bay grid is bearing only where every storey stands a wall on it, and no "
                    f"run between bearing lines exceeds the {cap_ft:g} ft its framing tradition "
                    f"can span (structure.bearing_lines and span_check as a fact, WP-13.3)",
                    kind="bearing", key=key)
                bear = {}
                for L in inner_lines:
                    has = {}
                    for lvl_ in _rs_by_lvl:
                        faces = []
                        for e_ in _edge_vars(lvl_):
                            f = m.NewBoolVar("")
                            m.Add(e_ == L).OnlyEnforceIf(f)
                            faces.append(f)
                        hL = m.NewBoolVar("")
                        m.AddBoolOr(faces + [hL.Not()])       # has -> some face sits on L
                        has[lvl_] = hL
                    if 0 in has and 1 in has:
                        # continuity: no upper edge may stand on L unless a ground edge does
                        for e_ in _edge_vars(1):
                            m.Add(e_ != L).OnlyEnforceIf(has[0].Not(), lit)
                    bL = m.NewBoolVar("")
                    for hL in has.values():
                        m.AddImplication(bL, hL)                # bearing -> every storey
                    bear[L] = bL
                for inner in _windows():
                    m.AddBoolOr([bear[L] for L in inner]).OnlyEnforceIf(lit)

    if objective and penalties:
        m.Minimize(sum(p * wgt for p, wgt in penalties))
    m.AddAssumptions([lit for lit, _t, _k, _key in reqs.lits])
    return m, rooms, reqs


def _hint_heuristic(model, rooms, plan, parti, seed, candidates=40):
    """Warm-start from a heuristic run — the fallback doubles as the guide. The
    soft-blind phase A gets a cheap 40-candidate run; phase B is hinted with the
    full search's placement, which already optimized the SOFT terms and only
    needs its hard violations repaired — a far better basin than phase A's."""
    try:
        # level_aware=False deliberately (WP-7.1): a hint's only job is to be REPAIRABLE.
        # Hinting with the level-aware run took `tidewater-georgian-careful` from OPTIMAL to
        # UNKNOWN at budget -- a hint better by the heuristic's own score, in a basin the
        # proof could not close. See solve_heuristic's docstring.
        h = GEO.solve_heuristic(copy.deepcopy(plan), parti, candidates=candidates, seed=seed,
                                level_aware=False)
    except Exception:
        return
    if "error" in h:
        return
    for lv in h["levels"]:
        idx = lv.get("index", 0)
        for r in lv["rooms"]:
            g = r.get("geometry")
            if not g or (idx, r["id"]) not in rooms:
                continue
            v = rooms[(idx, r["id"])]
            model.AddHint(v["x"], int(round(g["x_ft"] * U)))
            model.AddHint(v["y"], int(round(g["y_ft"] * U)))
            model.AddHint(v["w"], int(round(g["width_ft"] * U)))
            model.AddHint(v["h"], int(round(g["depth_ft"] * U)))


def _hint_values(model, rooms, values):
    for key, (x, y, w, h) in values.items():
        if key not in rooms:
            continue
        v = rooms[key]
        model.AddHint(v["x"], x)
        model.AddHint(v["y"], y)
        model.AddHint(v["w"], w)
        model.AddHint(v["h"], h)


def _absorb(rects, W, H, caps=None, keepout=(), ratios=None, bounds=None,
            x0=0.0, y0=0.0):
    """Grow rooms into the void the coverage floor allows, edges moving outward
    only — a pinned boundary edge is already at its boundary, and a shared edge
    stops exactly at its neighbour, so nothing hard can break. `caps` bounds
    each room at the model's own size band (max area, sf): the solve PROVED
    "rooms at program size", and un-capped absorption was found stretching a
    2.8 sf linen press to 8 sf — a drawing quietly violating its own proof.
    A cap can leave residual void; honest empty floor beats an inflated room.

    `keepout` is a list of (x, y, w, h) this level's rooms may not grow over,
    and it exists because "nothing hard can break" was true only WITHIN a level
    (OQ 55). This pass runs per level with no cross-level view, so on a
    courtyard plan the CP engine proved no upper room sat over the open court
    and then this grew one across it — a guarantee proven and then undone by a
    post-pass, which is the same shape of defect as OQ 52 and just as invisible,
    because the record it writes looks exactly like a solved plan. The keep-out
    rectangles limit growth in all four directions exactly as a sibling room
    does, so the proof survives into the drawing.

    `ratios` is the same guarantee for SHAPE (WP-11.7), and it is the third time this pass has
    been caught undoing a proof the solve had just made. CP now holds each room inside its own
    `dimensions.proportion` band as a hard, downgradable pin; this pass then grew three of them
    straight back out of it -- measured on `plans/tidewater-georgian-careful.json`, the library
    to 1.69 against a ceiling of 1.6, the powder room to 2.66 against 2.2, and a closet to 4.21
    against 4.0, all three with their pin still HELD. A cap here can leave residual void, and
    honest empty floor beats a room the record does not admit; that is the same trade the area
    cap above already makes and it is made the same way.

    A room whose pin was DOWNGRADED is deliberately absent from `ratios`: the record says its
    band could not hold, so this pass has nothing to preserve for it.

    `bounds` is `{room_id: (x, y, W, H)}` -- the room's OWN massing element (WP-11.11), and the
    FOURTH time this pass has been caught undoing what the solve proved. CP now holds every room
    inside its element's box; this pass then grew one straight out of it, measured on a
    hand-tagged `tidewater-georgian-careful`: the breakfast room was proved at y >= 4.95, the
    west dependency's own south edge, and absorbed to y = 1.6 -- 3.35 ft of drawn floor outside
    the mass it belongs to, in a record that looks exactly like a solved plan. The four `lim`
    seeds below are the element's four faces now, and `(0, 0, W, H)` on a one-rectangle house,
    which is every plan in this corpus."""
    ids = list(rects)
    caps = caps or {}
    ratios = ratios or {}
    bounds = bounds or {}

    def _fits(rid, w, h):
        """Would this rectangle still sit inside the band the solve proved for it?"""
        c = ratios.get(rid)
        if not c:
            return True
        lo, hi = min(w, h), max(w, h)
        return hi <= c * lo + 0.01
    if keepout:
        rects = dict(rects)
        for i, ko in enumerate(keepout):
            rects[f"\0keepout{i}"] = tuple(ko)
    for _ in range(8):
        moved = False
        for rid in ids:
            x, y, w, h = rects[rid]
            cap = caps.get(rid, float("inf"))
            # `(x0, y0, W, H)` IS MAIN'S SPELLING OF THE SAME CLAMP AND IT IS THE DEFAULT.
            # Both branches stopped this pass growing a room out of its element: main by
            # calling it once PER ELEMENT with that element's origin, this branch by a
            # per-room `bounds` map. They compose -- a room the map does not cover takes
            # the element rectangle the caller passed -- so both call styles are exact,
            # and `(0.0, 0.0, W, H)` is still what a one-rectangle house gets.
            bx, by, bW, bH = bounds.get(rid, (x0, y0, W, H))
            lim = bx + bW
            for o, (ox, oy, ow, oh) in rects.items():
                if o != rid and oy < y + h - 0.01 and y < oy + oh - 0.01 and ox >= x + w - 0.01:
                    lim = min(lim, ox)
            if lim - (x + w) > 0.01:
                nw = min(lim - x, max(w, cap / max(h, 0.01)))
                if nw - w > 0.01 and _fits(rid, nw, h):
                    w = nw; moved = True
            lim = by + bH
            for o, (ox, oy, ow, oh) in rects.items():
                if o != rid and ox < x + w - 0.01 and x < ox + ow - 0.01 and oy >= y + h - 0.01:
                    lim = min(lim, oy)
            if lim - (y + h) > 0.01:
                nh = min(lim - y, max(h, cap / max(w, 0.01)))
                if nh - h > 0.01 and _fits(rid, w, nh):
                    h = nh; moved = True
            lim = bx
            for o, (ox, oy, ow, oh) in rects.items():
                if o != rid and oy < y + h - 0.01 and y < oy + oh - 0.01 and ox + ow <= x + 0.01:
                    lim = max(lim, ox + ow)
            if x - lim > 0.01:
                nw = min(w + (x - lim), max(w, cap / max(h, 0.01)))
                if nw - w > 0.01 and _fits(rid, nw, h):
                    x -= nw - w; w = nw; moved = True
            lim = by
            for o, (ox, oy, ow, oh) in rects.items():
                if o != rid and ox < x + w - 0.01 and x < ox + ow - 0.01 and oy + oh <= y + 0.01:
                    lim = max(lim, oy + oh)
            if y - lim > 0.01:
                nh = min(h + (y - lim), max(h, cap / max(w, 0.01)))
                if nh - h > 0.01 and _fits(rid, w, nh):
                    y -= nh - h; h = nh; moved = True
            rects[rid] = (round(x, 2), round(y, 2), round(w, 2), round(h, 2))
        if not moved:
            break
    return {k: v for k, v in rects.items() if not k.startswith("\0keepout")}


def _merge_runs(spans, gap=0.05):
    """Merge a list of (lo, hi) into disjoint runs, closing hairline gaps."""
    out = []
    for lo, hi in sorted(spans):
        if out and lo <= out[-1][1] + gap:
            out[-1][1] = max(out[-1][1], hi)
        else:
            out.append([lo, hi])
    return [[round(lo, 2), round(hi, 2)] for lo, hi in out]


def _count_relaxations(rects_by_level, W, H, bay, tol, boxes_ft=None):
    """Interior wall lines off the bay grid — the heuristic's own definition of
    a compromise — counted from the solved placement (per unique line, per axis).

    `boxes_ft` maps (level, room id) to its own massing element as (x0, y0, x1, y1) in FEET
    (WP-11.6 item 4). An element boundary is not an interior wall and its own bay grid starts
    at its own origin, so a west wing counted in the main block's frame reported every one of
    its walls as a compromise and its own two flanks as interior lines. Absent — and on a
    one-element plan, where every room maps to (0, 0, W, H) — this is the frame it always
    used."""
    relax = []
    boxes_ft = boxes_ft or {}
    for lvl, rects in rects_by_level.items():
        for axis in ("x", "y"):
            edges = {}
            for rid, (x, y, w, h) in rects.items():
                bx0, by0, bx1, by1 = boxes_ft.get((lvl, rid)) or (0.0, 0.0, W, H)
                if axis == "x":
                    edges.setdefault((round(x, 1), bx0, bx1), []).append((y, y + h))
                    edges.setdefault((round(x + w, 1), bx0, bx1), []).append((y, y + h))
                else:
                    edges.setdefault((round(y, 1), by0, by1), []).append((x, x + w))
                    edges.setdefault((round(y + h, 1), by0, by1), []).append((x, x + w))
            for (e, lo, hi), spans in edges.items():
                if e <= lo + 0.05 or e >= hi - 0.05:
                    continue
                d = abs((e - lo) - round((e - lo) / bay) * bay)
                if axis == "y":
                    d = min(d, abs(e - hi))
                if d > tol:
                    # Positioned, like the heuristic's (OQ 33). This counter already knew where
                    # the line was -- `e` is the edge coordinate and the level is the loop key --
                    # and threw it away to append a bare float.
                    #
                    # It also knew, and threw away, WHERE ALONG THAT LINE THERE IS A WALL. The
                    # earlier note here refused an extent because "an edge is a wall line shared
                    # by however many rooms abut it, and inventing an extent for it would be a
                    # drawn claim nobody measured" -- correct about the invention, wrong that
                    # there was nothing to measure. `runs` is the union of the room faces that
                    # actually sit on this line: measured, not invented, and possibly several
                    # disjoint pieces, which is why it is a list and not a from/to pair. The
                    # sheet had been drawing an extentless mark at the MIDDLE OF THE PLAN, which
                    # on the Tidewater placement put a dashed tick and a triangle inside the
                    # drawing room with no wall under either -- the "arrows that seem to point to
                    # anything and everything" of Lucas's review, and a mark the room's own click
                    # could not be made through.
                    relax.append({"off_ft": round(d, 2), "axis": axis,
                                  "at_ft": round(e, 2), "level": lvl,
                                  "runs": _merge_runs(spans)})
    return relax


def _score(rects_by_level, prep, levels, plan, fpd, ewalls, relax, bounds=None,
           elements=None):
    """The heuristic's OWN scoring of this placement, term for term, so the
    acceptance comparison is apples to apples.

    `bounds` is `solve_heuristic`'s own `gbounds` — room id to its element's rectangle — and its
    absence here was a real parity gap, not a stylistic one (WP-11.6 item 4): the hill-climb has
    passed it to `exterior_score` since layer 4, so a wing room's declared walls were charged
    against the WING there and against the main block here. Two engines scoring one house by
    two rules is what this function's first sentence exists to forbid. The other scorers take no
    bounds in EITHER engine — they measure the main block — and are left alone deliberately.

    `elements` is the SECOND half of that same parity gap and stood open for five packages
    (WP-11.16's precondition). The hill-climb has passed `_span_elements` to `_span_charge`
    since WP-11.9; this function did not, so on a multi-element CP placement the count and the
    charge were computed with the whole footprint as ONE rectangle while `_disclose_spans`
    wrote `marks` per element -- two numbers about one record, and
    `tests/test_span_findings.py` asserts they are equal. MEASURED on
    `_multi_element_fixture()` before the fix: `over_capacity` **0** against **1** mark, and
    the mark is a 37.5 ft clear run in the dependency against its own 24.0 ft capacity. So it
    was not merely a disagreement -- the record claimed NOTHING exceeded capacity while a run
    half again over it stood in the drawing, which is the OQ 52 family inside the prover's own
    score. `geometry_cp._build`'s span term has been per element since WP-11.11; only this
    post-solve scoring was not."""
    W, H = fpd["W"], fpd["H"]
    gr = rects_by_level.get(0, {})
    ur = rects_by_level.get(1, {})
    sg = (GEO.level_score(gr, prep[0]) + GEO.exterior_score(gr, prep[0], W, H, bounds=bounds)
          + GEO.adjacency_score(gr, prep[0], levels[0]["rooms"])
          + GEO.entrance_score(gr, prep[0], W, H, ewalls)
          + GEO.principal_and_service_score(gr, prep[0], W, H, ewalls)
          + GEO.ceremonial_score(gr, prep[0], W, H, ewalls)
          + GEO.centre_hall_symmetry_score(gr, prep[0], W, H))
    if prep.get(1) and ur:
        su = (GEO.level_score(ur, prep[1]) + GEO.exterior_score(ur, prep[1], W, H)
              + GEO.adjacency_score(ur, prep[1], levels[1]["rooms"])
              + GEO.centre_hall_symmetry_score(ur, prep[1], W, H))
    else:
        su = 0.0
    sv, vnotes = GEO.vertical_score(gr, ur, prep[0], prep.get(1, []), plan)
    # WP-7.4: the span charge belongs HERE too, and leaving it out would quietly falsify this
    # function's own first sentence. `_finish_feasible` chooses among hard-valid placements by
    # this score, so a term the heuristic's candidate loop charges and this one does not is a
    # term the CP path cannot act on however well the CP model is steered by it.
    try:
        _floor = _mod("structure", f"{ROOT}/build/structure.py").load_construction()["floor"]
    except Exception:
        _floor = None
    spc, over = GEO._span_charge(rects_by_level, prep, W, H, fpd["bay"],
                                 plan.get("style"), _floor, elements=elements)
    tot = sg + su + sv + spc + 1.5 * len(relax)
    return {"score": round(tot, 1), "sg": round(sg, 1), "su": round(su, 1),
            "sv": round(sv, 1), "span_charge": round(spc, 1),
            "spans_over_capacity": over, "vnotes": vnotes}


def _values(solver, rooms):
    return {key: (solver.Value(v["x"]), solver.Value(v["y"]),
                  solver.Value(v["w"]), solver.Value(v["h"]))
            for key, v in rooms.items()}


def _solve_assuming(plan, prep, fpd, ewalls, texts, time_s, downgraded=frozenset(),
                    seed=7):
    """One fresh hard-only model asserting only the named requirements;
    returns (status, sufficient-core-texts-or-None)."""
    from ortools.sat.python import cp_model
    model, _, reqs = _build(plan, prep, fpd, ewalls, downgraded, objective=False)
    model.ClearAssumptions()
    by_lit = [(lit, t) for lit, t, _k, _key in reqs.lits if t in texts]
    model.AddAssumptions([lit for lit, _ in by_lit])
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = time_s
    s.parameters.num_search_workers = 1
    s.parameters.random_seed = seed  # the same infeasible record names the same conflicts
    st = s.Solve(model)
    core = None
    if st == cp_model.INFEASIBLE:
        idx = set(s.SufficientAssumptionsForInfeasibility())
        core = [t for lit, t in by_lit if lit.Index() in idx]
    return st, core


# greedy drop order: the likely-removable first, the likely-essential last
_DROP_ORDER = ("program size", "share a door", "door to the exterior",
               "protrudes", "contested", "exterior wall", "is the entry")


def _extract_conflicts(plan, prep, fpd, ewalls, budget_s=20.0, seed_core=None,
                       downgraded=frozenset()):
    """Turn CP-SAT's sufficient core into a plain-language conflict set,
    minimized within a time budget, AT THE NATURAL FOOTPRINT — extracting at
    the growth-ceiling footprint instead was this module's first real bug (a
    wide, shallow footprint manufactures conflicts the natural one never had).

    Two phases: (1) iterate the solver's own sufficient core to a fixpoint —
    one solve per pass, typically a fast collapse; (2) greedy drop-one on the
    remainder, removable-first. If the budget runs out first, the larger
    honest core is returned with minimized=False — the note says so."""
    from ortools.sat.python import cp_model
    deadline = time.monotonic() + budget_s

    if seed_core is None:
        model, _, reqs = _build(plan, prep, fpd, ewalls, downgraded, objective=False)
        s = cp_model.CpSolver()
        s.parameters.max_time_in_seconds = max(2.0, budget_s / 3)
        s.parameters.num_search_workers = 1
        s.parameters.random_seed = 7
        if s.Solve(model) != cp_model.INFEASIBLE:
            return None, False
        idx = set(s.SufficientAssumptionsForInfeasibility())
        by_index = {lit.Index(): t for lit, t, _k, _key in reqs.lits}
        seed_core = [by_index[i] for i in idx if i in by_index]

    kept = list(seed_core)
    while time.monotonic() < deadline:
        st, core = _solve_assuming(plan, prep, fpd, ewalls, set(kept),
                                   min(4.0, max(0.5, deadline - time.monotonic())),
                                   downgraded)
        if st != cp_model.INFEASIBLE or core is None or len(core) >= len(kept):
            break
        kept = core
    minimized = True
    ordered = sorted(kept, key=lambda t: next(
        (i for i, k in enumerate(_DROP_ORDER) if k in t), len(_DROP_ORDER)))
    for t in ordered:
        if time.monotonic() > deadline:
            minimized = False
            break
        if len(kept) <= 1:
            break
        # 1.5s cap: a drop that stays infeasible usually proves fast; a keep
        # unproven in time simply stays kept (the safe direction) — but an
        # UNKNOWN keep is not a PROVEN keep, so it clears the minimized flag
        st, _ = _solve_assuming(plan, prep, fpd, ewalls, set(kept) - {t},
                                min(1.5, max(0.5, deadline - time.monotonic())),
                                downgraded)
        if st == cp_model.INFEASIBLE:
            kept.remove(t)
        elif st == cp_model.UNKNOWN:
            minimized = False
    conflicts = kept or \
        ["the rooms cannot tile any footprint this parti and lot allow, even with "
         "every declared requirement dropped — the programme is too large for the diagram"]
    return conflicts, minimized


def _snap_fpd(fpd):
    """Snap the footprint depth to the integer model grid, so the record's
    footprint and the solved coordinates are the same fact — without this a
    29.6 ft derivation becomes a 30 ft model and the drawn boundary lies by
    the difference."""
    out = dict(fpd)
    H = round(int(round(fpd["H"] * U)) / U, 2)
    out["H"] = H
    out["slack"] = (out["W"] * H) - fpd["need"]
    return out


def solve_cp(plan, parti=None, seed=7, time_limit_s=20.0, candidates=250):
    from ortools.sat.python import cp_model
    levels, prep = GEO.prep_rooms(plan)
    fpd0 = GEO.derive_footprint(plan, parti, prep)
    if "error" in fpd0:
        return {"error": fpd0["error"]}
    fpd0 = _snap_fpd(fpd0)
    if fpd0["H"] < 1 or fpd0["W"] < 1:
        # a sub-1-ft dimension rounds to an empty integer model, whose
        # "infeasible" would be a statement about the rounding, not the plan
        return {"error": f"footprint degenerate at {fpd0['W']} x {fpd0['H']} ft — "
                         f"too small to model on the 1 ft grid", "unsolved": True}
    ewalls = GEO.entrance_walls(plan)
    started = time.monotonic()

    attempts = []
    downgraded = set()      # pins PROVEN unable to co-hold: (level, room, wall) for a wall
                            # pin, (level, room) for a WP-11.7 shape pin. Split by arity
                            # wherever it is read, never by position.
    rank_notes = []         # what each round gave up, and at which rank -- a pin released on
                            # an UNDECIDED round is named there; the reinstatement pass tries
                            # every downgraded pin whichever route released it, and one it
                            # cannot restore or refute alone in budget stays CARRIED on the
                            # record (WP-13.3)
    seed_core = None

    def _feasibility(fpd, tag, budget):
        """Phase A: hard constraints only."""
        model, rooms, reqs = _build(plan, prep, fpd, ewalls, frozenset(downgraded),
                                    objective=False)
        _hint_heuristic(model, rooms, plan, parti, seed, candidates=40)
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = budget
        solver.parameters.num_search_workers = 1
        solver.parameters.random_seed = seed
        status = solver.Solve(model)
        attempts.append((tag, "A:" + solver.StatusName(status)))
        return status, solver, rooms, reqs

    def _reinstate(fpd, vals):
        """A solver core is SUFFICIENT, not minimal — the round loop downgrades
        every pin of the released rank, which over-softens (both walls of one
        room have ridden in one core). So: restore each downgraded pin ALONE,
        at the footprint actually being drawn. Feasible → the downgrade was
        never needed; the pin returns to being a hard fact. INFEASIBLE → that
        is the pin's own proof, at this footprint. UNKNOWN or budget out →
        the downgrade stays but is stated as carried, never as proven.

        BUDGETED (WP-13.3): the pass may spend `GEO.BUDGET_SHARE_REINSTATE` of the
        budget and never the polish's guaranteed share -- it used to run until 2.5 s
        remained, which on the reference plan was 21 restore attempts and a polish
        that never started. It offers the facts back HIGHEST RANK FIRST, because
        the share is finite and a hearth or a bearing line won back is worth more
        than a wall aspiration, which is the whole of what the ranking says."""
        _rank_of = {k: i for i, k in enumerate(_RANK)}
        pending = sorted(downgraded, key=lambda k: (-_rank_of.get(k[0], -1), str(k)))
        deadline = min(time.monotonic() + GEO.BUDGET_SHARE_REINSTATE * time_limit_s,
                       started + (1.0 - GEO.BUDGET_SHARE_POLISH) * time_limit_s)

        def _try(keys, tag, cap):
            left = deadline - time.monotonic()
            if left < RESTORE_MIN_S:
                return None
            trial = frozenset(downgraded - set(keys))
            model, rooms, _reqs2 = _build(plan, prep, fpd, ewalls, trial, objective=False)
            _hint_values(model, rooms, vals)
            s = cp_model.CpSolver()
            s.parameters.max_time_in_seconds = min(cap, left)
            s.parameters.num_search_workers = 1
            s.parameters.random_seed = seed
            st = s.Solve(model)
            attempts.append((tag, "R:" + s.StatusName(st)))
            if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                return _values(s, rooms)
            return st

        # TWO PHASES, EACH SLICED PER KIND, HIGHEST RANK FIRST (WP-13.3). Phase one offers every
        # downgraded kind back WHOLE -- five declared stacks that co-hold cost one solve rather
        # than five, and a hearth pair that cannot (two centred fires on one flue) fails once --
        # inside the first half of the share; phase two offers the pins still down one at a
        # time inside what is left. Each kind's slice is re-derived from the time left when its
        # turn comes, so a kind refuted in half a second hands the rest on.
        #
        # WHY TWO PHASES AND NOT ONE, MEASURED: a first version offered each kind whole and then
        # singly before moving to the next kind. On the two-storey fixture that let six single
        # SHAPE pins (the highest rank) come back before the three stacks were offered as a kind,
        # and the placement those six chose could hold ONE stack -- where wholes-first holds all
        # three stacks AND seven of the eight shapes. A rank orders CONFLICTS; it is not a licence
        # to end with strictly fewer facts held than another order of the same greedy pass.
        # WHY SLICED, MEASURED: the version before that offered the kinds back in rank order until
        # the share was spent, and on the reference plan the three expensive facts (bearing, the
        # stacks, the tiling -- each UNKNOWN in 4 s with a hint) spent the whole share at every
        # budget to 90 s, so not one of the 22 wall pins was ever offered back where the old pass
        # restored 9 to 13 of them: "the walls last" starved the one kind the pass could win.
        # A pin a slice never reaches stays carried, and the record says so.
        refuted = set()
        kinds = [k for k in reversed(_RANK) if any(p[0] == k for p in pending)]
        whole_deadline = time.monotonic() + (deadline - time.monotonic()) * 0.5
        whole = [k for k in kinds if sum(1 for p in pending if p[0] == k) >= 2]
        for n_, kind in enumerate(whole):
            keys_k = [k for k in pending if k[0] == kind and k in downgraded]
            if len(keys_k) < 2:
                continue
            cap = min(RESTORE_KIND_S, (whole_deadline - time.monotonic()) / (len(whole) - n_))
            if cap < RESTORE_MIN_S:
                continue
            got = _try(keys_k, f"restore {kind} x{len(keys_k)}", cap)
            if got is None:
                break
            if isinstance(got, dict):
                vals = got
                downgraded.difference_update(keys_k)
        single = [k for k in kinds if any(p[0] == k and p in downgraded for p in pending)]
        for n_, kind in enumerate(single):
            keys_k = [k for k in pending if k[0] == kind and k in downgraded]
            kind_deadline = time.monotonic() + (deadline - time.monotonic()) / (len(single) - n_)
            for key in keys_k:
                if key not in downgraded:
                    continue
                cap = min(RESTORE_PIN_S, kind_deadline - time.monotonic())
                if cap < RESTORE_MIN_S:
                    break
                # A key carries its kind now (`_dk`), and the label says which: a wall keeps
                # `restore L{level} {room} {wall}`, which `tests/test_solver.py` parses; every
                # other kind is `restore {kind} {label}`.
                got = _try([key], "restore " + (_label("wall", key[1:]) if key[0] == "wall"
                                                 else f"{key[0]} {_label(key[0], key[1:])}"),
                           cap)
                if got is None:
                    break
                if isinstance(got, dict):
                    vals = got
                    downgraded.discard(key)
                elif got == cp_model.INFEASIBLE:
                    refuted.add(key)        # refuted alone at this footprint: proven, not carried
        # PROVEN means refuted ALONE at this footprint and nothing less: a pin the slice never
        # reached, one that came back UNKNOWN, and one refuted only as part of its whole kind
        # are all CARRIED, whether a core named them or an undecided round released them.
        return vals, {k for k in downgraded if k not in refuted}

    def _rects_scored(fpd, vals):
        rects_by_level = {}
        for (lvl, rid), (x, y, w, h) in vals.items():
            rects_by_level.setdefault(lvl, {})[rid] = (x / U, y / U, w / U, h / U)
        # the literals the model states at this footprint, read once for the absorb guard
        _, _, _fact_reqs = _build(plan, prep, fpd, ewalls, frozenset(downgraded),
                                  objective=False)
        _fact_lits = _fact_reqs.lits
        _els2 = {lv: GEO.blocks_for(plan, fpd, prep, lv) for lv in (0, 1) if prep.get(lv)}
        _eb2, _g0x, _g0y, _g1x, _g1y = _element_boxes(_els2, int(round(fpd['W'] * U)),
                                                     int(round(fpd['H'] * U)))
        boxes = {k: (x, y, x + W, y + H) for k, (x, y, W, H) in _eb2.items()}
        _mb = (_g0x, _g0y, _g1x, _g1y)
        # KEYED BY (level, id) for the relaxation counter and by id for the score, because
        # `solve_heuristic`'s `gbounds` is by id and this has to be the same argument. Two
        # levels can carry one room id; the score's map takes the GROUND element, which is
        # where the elements are, and the counter never conflates the two at all.
        boxes_ft = {k: tuple(c / U for c in b) for k, b in boxes.items()}
        bounds_ft = {rid: v for (lvl, rid), v in boxes_ft.items() if lvl == 0}
        # SORTED, so the ground is absorbed before the storey that must avoid its holes.
        for lvl in sorted(rects_by_level):
            rs = prep.get(lvl) or []
            fill = (fpd["W"] * fpd["H"]) / max(1.0, sum(r["_area"] for r in rs))
            caps = {r["id"]: max(1.20, fill * 1.22) * r["_area"] for r in rs}
            # WP-11.7: the SHAPE half of the same guarantee. A room whose proportion pin the
            # ladder released is left out -- the record says its band could not hold, and this
            # pass has nothing to preserve for it.
            ratios = {}
            for r in rs:
                if (lvl, r["id"]) in downgraded:
                    continue
                _c, _ = GEO.shape_band(r.get("type"))
                if _c:
                    ratios[r["id"]] = _c
            keepout = []
            if lvl == 1:
                below = rects_by_level.get(0) or {}
                for gr in (prep.get(0) or []):
                    v = gr.get("_void")
                    if isinstance(v, dict) and not v.get("roofed") and gr["id"] in below:
                        keepout.append(below[gr["id"]])
            # WP-11.11: the room's OWN element bounds the growth. `None` on a one-rectangle
            # house -- the whole shipped corpus -- so `_absorb` takes its `(0, 0, W, H)`
            # default and every absorbed rectangle is unchanged.
            _els = GEO.blocks_for(plan, fpd, prep, lvl)
            _eb = ({rid: (e["x"], e["y"], e["W"], e["H"]) for e in _els for rid in e["rooms"]}
                   if len(_els) > 1 else None)
            # THE ABSORB PASS RUNS AFTER THE SOLVE AND IS OUTSIDE ITS PROOF (WP-13.3, the
            # fifth time this file has had to say it). It moves a room's faces outward into
            # leftover floor, and a face moved is a bearing line an upper wall may no longer
            # stand on, or a stack that no longer lands: measured on the two-storey fixture,
            # a landing proved 90% inside its hall was grown to 83% of it. So on a level
            # where a bearing or stack fact is HELD the proved rectangles are left exactly as
            # proved -- with the tiling fact held there is no leftover to absorb anyway, and
            # where tiling was released the residual floor is disclosed by `type_facts` rather
            # than filled by a pass that would silently unprove the facts still held.
            # (both kinds implicate both storeys: a bearing line is a line BOTH levels
            # stand a wall on, and a stack is an upper room over a ground one)
            if any(k in ("bearing", "stack") and key and _dk(k, key) not in downgraded
                   for _lit, _t, k, key in _fact_lits):
                continue
            rects_by_level[lvl] = _absorb(rects_by_level[lvl], fpd["W"], fpd["H"],
                                          caps=caps, keepout=keepout, ratios=ratios,
                                          bounds=_eb)
        relax = _count_relaxations(rects_by_level, fpd["W"], fpd["H"],
                                   fpd["bay"], fpd["tol"], boxes_ft=boxes_ft)
        # WP-11.16's precondition: the span charge is PER ELEMENT here too. `_els2` is already
        # in hand at the head of this function; this is that same list in the shape
        # `geometry.spans_over_capacity` takes -- keyed by level, holding only the levels that
        # really have more than one element, which is `geometry.py`'s own `_span_elements`
        # built from `blocks_for` in exactly this way. A level with ONE element is ABSENT from
        # the map rather than present with a single entry, so `spans_over_capacity` takes its
        # `[(0, 0, W, H)]` default and the arithmetic is identical; the whole shipped corpus is
        # one rectangle everywhere, passes `None`, and is byte-identical across this change.
        _span_els = {lv: [(b["x"], b["y"], b["W"], b["H"]) for b in bl]
                     for lv, bl in _els2.items() if len(bl) > 1} or None
        sc = _score(rects_by_level, prep, levels, plan, fpd, ewalls, relax,
                    bounds=bounds_ft, elements=_span_els)
        return rects_by_level, relax, sc

    def _polish(fpd, hint, budget, tag):
        model, rooms, reqs = _build(plan, prep, fpd, ewalls, frozenset(downgraded),
                                    objective=True)
        if hint == "heuristic":
            _hint_heuristic(model, rooms, plan, parti, seed, candidates=candidates)
        else:
            _hint_values(model, rooms, hint)
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = max(1.5, budget)
        solver.parameters.num_search_workers = 1
        solver.parameters.random_seed = seed
        statusB = solver.Solve(model)
        attempts.append((tag, "B:" + solver.StatusName(statusB)))
        if statusB in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return _values(solver, rooms), solver.StatusName(statusB),                 solver.ObjectiveValue() / SCALE
        return None, solver.StatusName(statusB), None

    def _facts_account(reqs_notes):
        """The model's own account of the type's four facts: every literal of each kind by
        its label, HELD or DOWNGRADED, and every fact it could not state, UNJUDGED with its
        reason. `build/typefacts.py` verifies the same four on the placed record afterwards;
        this is what the prover was ASKED, that is what it DREW."""
        out = {}
        for kind in TYPE_FACTS:
            keys = sorted({key for _l, _t, k, key in reqs_notes.lits if k == kind and key},
                          key=lambda k: tuple(str(x) for x in k))
            held = [_label(kind, k) for k in keys]
            down = sorted(_label(kind, k[1:]) for k in downgraded if k[0] == kind)
            unj = [{"key": _label(kind, key) if key else None, "why": why}
                   for k, key, why in reqs_notes.unjudged if k == kind]
            out[kind] = {"held": held, "downgraded": down, "unjudged": unj,
                         "status": ("downgraded" if down else "held" if held
                                    else "unjudged")}
        return out

    def _finish_feasible(fpd, valsA, statusA_name):
        """Phase B: polish with the weighted objective, hinted two ways — the
        full heuristic search (soft-optimized, hard-repairable) and phase A's
        own placement (hard-clean). AMONG THE CANDIDATES THAT CARRY AN OBJECTIVE
        THE CP OBJECTIVE RANKS THEM (WP-13.3), and the hard-only phase A
        placement is kept only when no polish produced a solution at all; the
        search's own demerit total (`GEO._score`) is computed for every candidate
        and DISCLOSED as `solver.score`, and no longer decides. It used to: "best
        of N" sorted by that score, so a candidate whose composition had never
        been evaluated could outrank one whose objective had run, on a number
        the objective was not chosen by."""
        unproven = set()
        if downgraded:
            # minimal, individually-proven downgrades at the footprint being
            # drawn — the round loop's cores over-blame (see _reinstate)
            valsA, unproven = _reinstate(fpd, valsA)
        remaining = max(GEO.BUDGET_SHARE_POLISH * time_limit_s * 0.5,
                        time_limit_s - (time.monotonic() - started))
        candidates_out = [("hard-only phase A", valsA, statusA_name + " (hard-only)", None)]
        # PHASE A'S OWN PLACEMENT HINTS THE FIRST POLISH (WP-13.3). It is feasible under the
        # very hard set the polish carries, so the objective has a solution to start from at
        # once; the heuristic's hint has to be REPAIRED first, and with the type's facts in the
        # model that repair came back UNKNOWN in every one of ten runs on the reference plan
        # today (40 to 90 s) while the phase-A polish came back FEASIBLE in every one. The
        # heuristic hint is offered second, with what remains, and the objective ranks them.
        vals1, st1, obj1 = _polish(fpd, valsA, remaining * 0.55, "polish-a")
        if vals1 is not None:
            candidates_out.append(("polish from phase A", vals1, st1, obj1))
        remaining2 = time_limit_s - (time.monotonic() - started)
        if remaining2 > 4.0 and st1 != "OPTIMAL":
            vals2, st2, obj2 = _polish(fpd, "heuristic", remaining2, "polish-h")
            if vals2 is not None:
                candidates_out.append(("polish from the heuristic hint", vals2, st2, obj2))
        scored = []
        for label, vals, stname, obj in candidates_out:
            rects_by_level, relax, sc = _rects_scored(fpd, vals)
            scored.append((sc["score"], label, rects_by_level, relax, sc, stname, obj))
        with_obj = [t for t in scored if t[6] is not None]
        if with_obj:
            with_obj.sort(key=lambda t: (t[6], t[0]))
            _, label, rects_by_level, relax, sc, stname, objective = with_obj[0]
            status_name = (f"{stname} — kept {label} by the CP objective "
                           f"({len(with_obj)} of {len(scored)} hard-valid placements carried one)")
        else:
            _, label, rects_by_level, relax, sc, stname, objective = scored[0]
            status_name = (f"{stname} — kept {label}: no polish produced a placement in "
                           f"budget, so the compositional objective did not run")
        best = {"ground": rects_by_level.get(0, {}), "upper": rects_by_level.get(1, {}),
                "relaxations": relax, **sc,
                "candidates": [{"label": t[1], "status": t[5], "objective": t[6],
                                "search_score": t[0]} for t in scored]}
        _, _, reqs_notes = _build(plan, prep, fpd, ewalls, frozenset(downgraded),
                                  objective=False, unproven=frozenset(unproven))
        return {"best": best, "fpd": fpd, "levels": levels,
                "solver": {"engine": "cp-sat", "status": status_name,
                           "objective": objective,
                           "candidates": best["candidates"],
                           "wall_time_s": round(time.monotonic() - started, 2),
                           "attempts": attempts,
                           # WP-6.3 corrected two words of this claim. It said "rooms at
                           # program size", and the SOLVE does prove that — but `_absorb`
                           # runs after it and grows rooms to `max(1.20, fill*1.22)` times
                           # their programme area, measured at 1.22x on both ground levels
                           # and 2.27x on one upper. The record shipped a proof of programme
                           # size on a drawing that no longer held it. The cap is not the
                           # defect (honest empty floor beats an inflated room, and the cap
                           # is what stops a 2.8 sf linen press reaching 8); the CLAIM was.
                           "hard": "no-overlap; containment; coverage; declared doors "
                                   "share wall enough for their own leaf and jambs; the "
                                   "entry on its front; rooms at or above program size "
                                   "(the post-solve absorb pass grows them into leftover "
                                   "floor, capped, so the drawn size is a floor and not an "
                                   "equality); declared exterior walls (until a set is "
                                   "proven unable to co-hold — then downgraded, stated)",
                           "note": "the compositional terms are constraints and "
                                   "weighted objectives here, not search preferences",
                           # WP-11.7 split these by ARITY and WP-13.3 by KIND: a key is
                           # `(kind, *key)` now (`_dk`), because the axis pin and the shape
                           # pin share `(level, room)` and were read as one another.
                           "downgraded_wall_pins": sorted(
                               _label("wall", k[1:]) for k in downgraded if k[0] == "wall"),
                           "downgraded_shape_pins": sorted(
                               _label("shape", k[1:]) for k in downgraded if k[0] == "shape"),
                           "downgraded_axis_pins": sorted(
                               _label("axis", k[1:]) for k in downgraded if k[0] == "axis"),
                           # THE TYPE'S FOUR FACTS, as the model stated them (WP-13.3): held,
                           # downgraded, or unjudged with a reason. `typefacts.report` on the
                           # placed record is the verifier; this is the claim.
                           "facts": _facts_account(reqs_notes),
                           "downgrade_rounds": list(rank_notes),
                           "refinements": sorted(set(reqs_notes.notes))}}

    # Round loop at the natural footprint: wall pins are hard until PROVEN
    # unable to co-hold; exactly those pins downgrade, stated. Doors, sizes,
    # the entrance and capacity never downgrade — they are what infeasibility
    # is FOR (25 Aug rulings, contested-corners read as a principle).
    #
    # THE FEASIBILITY ROUNDS MAY SPEND `GEO.BUDGET_SHARE_FEASIBILITY` OF THE BUDGET AND NO MORE
    # (WP-13.3). They used to spend "the WHOLE remaining budget" on an UNKNOWN scout -- right
    # when the alternative was giving up, and wrong once it meant the polish never ran: on the
    # reference plan phase A took about 20 s of 40 and the compositional objective got the
    # 1.5 s floor and came back UNKNOWN, under a status reading `OPTIMAL (hard-only)`. A phase A
    # still UNKNOWN at its share is UNSOLVED, and `auto` falls back to the search and says so;
    # the sweep that chose the share is in the WP-13.3 report. One round per rank and one more,
    # because a round releases a whole rank and there are `len(_RANK)` of them.
    a_deadline = started + GEO.BUDGET_SHARE_FEASIBILITY * time_limit_s
    for rnd in range(len(_RANK) + 1):
        budget = min(SCOUT_S, max(2.0, (a_deadline - time.monotonic()) * 0.5))
        status, solver, rooms, reqs = _feasibility(fpd0, f"{fpd0['bays']}b r{rnd}", budget)
        if status == cp_model.UNKNOWN:
            # THE SCOUT COULD NOT DECIDE, AND AN UNDECIDED ROUND IS NOT A PROOF OF ANYTHING.
            # Two ways on, and which is taken is a measurement (WP-13.3). With the type's
            # facts hard, the state every fact is held in is the expensive one -- on the
            # reference plan `tiling + stack + bearing + shape` is UNKNOWN at 40 s on a loaded
            # core, while the state WP-11.7 proved solvable (the shape band alone) is OPTIMAL
            # in about 9 s. So where any of the TYPE'S FACTS is still live, all of them are
            # RELEASED AT ONCE and marked CARRIED -- released on no proof, which the record
            # says in as many words -- and the reinstatement pass wins them back highest rank
            # first, whole kinds before single pins, with the placement just found as the
            # solver's hint. What comes back is proven to co-hold; what stays out is either
            # proven impossible alone or still carried. The walls and the axis are NOT
            # released here: their conflicts arrive as fast INFEASIBLE cores (0.1 s on the
            # reference plan) and are handled by proof above, and the state with them held
            # and the facts released is the one WP-11.7 measured solvable. Where no fact is
            # live, the rest of the share goes on the retry, as before (bailing at the scout
            # cap was a measured mistake, and a 0.6x retry starved the 25-room double-pile
            # too).
            live_facts = sorted({_dk(k, key) for _lit, _t, k, key in reqs.lits
                                 if key and k in TYPE_FACTS}, key=str)
            if live_facts:
                _by = {}
                for k in live_facts:
                    _by.setdefault(k[0], []).append(k)
                rank_notes.append(
                    f"round {rnd}: UNDECIDED at the {budget:.0f} s scout with "
                    + ", ".join(f"{len(v)} {k}" for k, v in
                                sorted(_by.items(), key=lambda kv: _RANK.index(kv[0])))
                    + " pin(s) live — the type's facts released at once, CARRIED and not "
                    f"proven, and offered back highest rank first by the reinstatement pass")
                downgraded.update(live_facts)
            budget = max(2.0, a_deadline - time.monotonic())
            status, solver, rooms, reqs = _feasibility(fpd0, f"{fpd0['bays']}b r{rnd}+", budget)
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return _finish_feasible(fpd0, _values(solver, rooms),
                                    solver.StatusName(status))
        if status == cp_model.UNKNOWN:
            return {"unsolved": True, "status": solver.StatusName(status),
                    "attempts": attempts}
        if status != cp_model.INFEASIBLE:
            # MODEL_INVALID or anything else unexpected: an empty core from it
            # would masquerade as a proof — refuse, stated, instead
            return {"unsolved": True, "status": solver.StatusName(status),
                    "attempts": attempts}
        idx = set(solver.SufficientAssumptionsForInfeasibility())
        core = [(t, k, key) for lit, t, k, key in reqs.lits if lit.Index() in idx]
        seed_core = [t for t, _k, _key in core]
        # THE LADDER IS RANKED (WP-11.7), and it was a single kind until this package.
        # It read `[key for _t, k, key in core if k == "wall" and key]` -- so a wall pin was
        # the only downgradable fact, and every requirement added since would either have been
        # un-downgradable (and taken the whole placement to INFEASIBLE) or would have had to be
        # soft, which on this plan means invisible: `_finish_feasible` keeps the hard-only
        # phase A placement whenever the polish times out, and the objective never runs.
        #
        # RANK IS AUTHORITY, LOWEST FIRST, AND THE ORDER IS THE POINT. An authored exterior
        # wall is the author's own statement about the house; a shape pin is the corpus's rule
        # about the room TYPE; an axis pin is inferred from the parti. So a round gives up the
        # inferred fact before the authored one, and OQ 95's standing requirement -- that an
        # authored wall can never lose to an inferred pin -- holds by construction rather than
        # by everything else being soft.
        #
        # Sizes, doors, the entrance and capacity are still ABSENT from this ladder and still
        # never downgrade: they are what infeasibility is for (the 25 Aug rulings, unchanged).
        # A SOLVER CORE IS SUFFICIENT AND NOT MINIMAL, WHICH IS WHY THE SECOND CLAUSE EXISTS.
        # Measured on `plans/tidewater-georgian-careful.json` the first time the shape pins ran:
        # the core came back as three literals -- the Back Hall's declared N wall, its declared
        # S wall, and its 7 x 16 ft programme -- and NO shape literal, although the shape pin was
        # the new fact that had just made the model infeasible. (A room declaring an opposite
        # pair must span the 40 ft depth; at 112 sf that is 2.8 ft wide, which is 14 to 1 against
        # a band of 5.) Ranking on the kinds the core happens to NAME would therefore have given
        # up two authored walls to save an inferred shape pin -- the exact inversion OQ 95
        # forbids, arrived at by accident.
        #
        # So: A ROUND RELEASES THE WHOLE OF THE LOWEST-RANKED KIND THE CORE NAMES, never the
        # pins the core happens to name and never a kind it does not name. The second half is
        # provable and was measured anyway (WP-13.3): a core is a set of literals that is
        # infeasible together with the model's plain facts, so releasing every pin of a kind
        # the core does not mention leaves the core intact and the model exactly as infeasible
        # -- that round can prove nothing and costs a solve, and a solve that comes back
        # UNKNOWN ends the ladder. The first version of the seven-rank ladder released the
        # first LIVE kind in rank order whatever the core said, and on the reference plan it
        # spent three rounds (tiling, stack, bearing) on cores that named only the hearth and
        # the shape band before it reached the hearth; core-guided, the same plan reaches that
        # release in three rounds of 0.1, 0.1 and 0.9 s. The first half is the whole-rank
        # measurement below, unchanged.
        #
        # The narrow version -- downgrade exactly the cored pins -- was written first and swept.
        # On `plans/tidewater-georgian-careful.json` with the shape band live it needs EIGHT
        # rounds, and the intermediate states (some walls released, the band still held) are the
        # expensive ones: at a 6 s per-round cap round 2 comes back UNKNOWN, so the ladder never
        # converges inside any budget the bench can spend. Releasing the rank whole reaches the
        # same end state in ONE round, and with the heuristic hint that round is OPTIMAL in
        # 12.9 s against 26.1 s unhinted.
        #
        # It over-releases, and the file already has the answer to that: `_reinstate` restores
        # each downgraded pin ALONE at the footprint actually being drawn and keeps the ones
        # that hold, marking the rest carried-not-proven. Its own docstring says why -- "a
        # solver core is SUFFICIENT, not minimal" -- and that reasoning is the same one round
        # larger here. What a round must never do is release a kind that outranks one still
        # live, and it cannot: the loop takes the first kind in `_RANK` with a live pin.
        _downgradable = None
        for _kind in _RANK:
            _named = sum(1 for _t, k, key in core if k == _kind and key)
            if not _named:
                continue
            live = [_dk(_kind, key) for _lit, _t, k, key in reqs.lits
                    if k == _kind and key and _dk(_kind, key) not in downgraded]
            if live:
                _downgradable = (_kind, live, _named)
                break
        if not _downgradable:
            # the core names no downgradable kind: sizes, doors, the entrance and capacity
            # alone cannot co-hold, and no release can change that -- infeasible, stated
            break
        _kind, _keys, _named = _downgradable
        rank_notes.append(
            f"round {rnd}: released all {len(_keys)} live {_kind} pin(s) — the lowest-ranked "
            f"kind still held; the conflict core named {_named} of them, and the rest are "
            f"offered back one at a time by the reinstatement pass "
            f"({', '.join(_label(_kind, k[1:]) for k in sorted(_keys, key=str))})")
        downgraded.update(_keys)

    # capacity may still be the blocker: grow a bay before blaming a requirement
    for bays in range(fpd0["bays"] + 1, fpd0["growth_ceiling"] + 1):
        fpd = _snap_fpd(_fpd_at(fpd0, bays))
        budget = max(2.0, a_deadline - time.monotonic())
        status, solver, rooms, reqs = _feasibility(fpd, f"{bays}b", budget)
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return _finish_feasible(fpd, _values(solver, rooms),
                                    solver.StatusName(status))
        if status == cp_model.UNKNOWN:
            return {"unsolved": True, "status": solver.StatusName(status),
                    "attempts": attempts}

    conflicts, minimized = _extract_conflicts(plan, prep, fpd0, ewalls,
                                              seed_core=seed_core,
                                              downgraded=frozenset(downgraded))
    if conflicts is None:
        return {"unsolved": True, "status": "INFEASIBLE-but-core-extraction-failed",
                "attempts": attempts}
    note = (f"CP-SAT proved these requirements cannot all hold together at any "
            f"footprint this parti and lot allow ({fpd0['bays']}–"
            f"{fpd0['growth_ceiling']} bays tried"
            + (f", with {len(downgraded)} already-downgraded wall pin(s)" if downgraded else "")
            + "). Drop or change one, or change the diagram.")
    if not minimized:
        note += (" The set is a sufficient core, not fully minimized — the "
                 "minimization budget ran out; some listed requirements may be "
                 "removable individually.")
    return {"infeasible": {
        "proven": True,
        "conflicts": conflicts,
        "minimized": minimized,
        "downgraded_wall_pins": sorted(_label("wall", k[1:]) for k in downgraded
                                       if k[0] == "wall"),
        "downgraded_shape_pins": sorted(_label("shape", k[1:]) for k in downgraded
                                        if k[0] == "shape"),
        "downgraded_facts": {kind: sorted(_label(kind, k[1:]) for k in downgraded
                                          if k[0] == kind)
                             for kind in ("axis",) + TYPE_FACTS},
        "downgrade_rounds": list(rank_notes),
        "note": note,
        "attempts": attempts}}


def hard_fact_violations(plan, out, extra_downgraded=None):
    """Count the hard facts a PLACEMENT violates: same-level declared doors with
    no drawable shared wall (render_plan's own 3.2 ft test), non-protruding
    declared walls unreached, the entry off its front. The heuristic trades
    these away at 14 points each; the CP engine cannot — so when the hill-climb
    'outscores' the constrained optimum, this is the number that says what the
    cheaper score actually bought. `out` is a solved plan record. Wall pins the
    solver PROVED unable to co-hold (out's own downgraded_wall_pins, stated
    per the ruling) are not violations — they are the model's stated reading
    of exposure-as-massing, and both engines leave them unreached alike.
    `extra_downgraded` takes another record's downgraded_wall_pins list so two
    engines' placements of the SAME plan are judged against the SAME facts —
    a heuristic record carries no downgrade list of its own, and charging it
    for pins the CP engine PROVED impossible would rig the comparison."""
    gr = out.get("geometry_report") or {}
    pin_strings = list(((gr.get("solver") or {}).get("downgraded_wall_pins") or []))
    # the proven-infeasible path carries its pins under infeasible, not solver
    pin_strings += list(((gr.get("infeasible") or {}).get("downgraded_wall_pins") or []))
    pin_strings += list(extra_downgraded or [])
    downgraded_keys = set()
    for s in pin_strings:
        # "L{level} {room-id} {wall}" — split from BOTH ends, because the
        # schema puts no pattern on room ids and an ingested id may hold spaces
        parts = s.split(" ")
        if len(parts) >= 3 and parts[0].startswith("L"):
            downgraded_keys.add((int(parts[0][1:]), " ".join(parts[1:-1]), parts[-1]))
    levels, prep = GEO.prep_rooms(plan)
    W = out["footprint"]["width_ft"]; H = out["footprint"]["depth_ft"]
    ewalls = GEO.entrance_walls(plan)
    rects_by_level = {}
    for lv in out["levels"]:
        idx = lv.get("index", 0)
        for r in lv["rooms"]:
            g = r.get("geometry")
            if g:
                rects_by_level.setdefault(idx, {})[r["id"]] = (
                    g["x_ft"], g["y_ft"], g["width_ft"], g["depth_ft"])
    v = 0
    for lvl, rs in ((0, prep.get(0) or []), (1, prep.get(1) or [])):
        rects = rects_by_level.get(lvl, {})
        contested = _contested_corners(rs)
        ids = {r["id"] for r in rs}
        maxside = {r["id"]: max(r.get("width_ft") or 10, r.get("length_ft") or 12)
                   for r in rs}
        seen = set()
        for r in rs:
            if r["id"] not in rects:
                continue
            x, y, w, h = rects[r["id"]]
            if not (_protruding(r) or r["id"] in contested):
                for wl in (r.get("exterior_walls") or []):
                    if (lvl, r["id"], wl) in downgraded_keys:
                        continue
                    at = {"S": y <= 0.6, "N": y + h >= H - 0.6,
                          "W": x <= 0.6, "E": x + w >= W - 0.6}.get(wl)
                    # not `is False`: an np.bool_ False from upstream floats
                    # would silently uncount (the ezdxf lesson, WP-5.1)
                    if at is not None and not at:
                        v += 1
            for d in (r.get("doors") or []):
                to = d["to"]
                if to == "exterior" or to not in ids or to not in rects:
                    continue
                key = tuple(sorted((r["id"], to)))
                if key in seen:
                    continue
                seen.add(key)
                ox, oy, ow, oh = rects[to]
                # THE SAME RULE THE MODEL STATED, from the same function. This was a second
                # copy of the old expression, and a second copy of a rule is how an arbiter
                # comes to contradict the solver it arbitrates: change one and this one
                # convicts placements the model proved legal. The 0.05 slack is kept —
                # it is a float-comparison tolerance against integers the model rounded.
                ovr = _door_overlap(d, {"maxside": maxside[r["id"]]},
                                    {"maxside": maxside[to]}) - 0.05
                shared_v = (abs(x + w - ox) <= 0.4 or abs(ox + ow - x) <= 0.4) and                     min(y + h, oy + oh) - max(y, oy) >= ovr
                shared_h = (abs(y + h - oy) <= 0.4 or abs(oy + oh - y) <= 0.4) and                     min(x + w, ox + ow) - max(x, ox) >= ovr
                if not (shared_v or shared_h):
                    v += 1
        if lvl == 0 and ewalls:
            for r in rs:
                if _cls(r["type"]) != "threshold" or r["id"] not in rects:
                    continue
                if not any(d.get("to") == "exterior" for d in (r.get("doors") or [])):
                    continue
                x, y, w, h = rects[r["id"]]
                on = any({"S": y <= 0.6, "N": y + h >= H - 0.6,
                          "W": x <= 0.6, "E": x + w >= W - 0.6}.get(wl, False)
                         for wl in ewalls)
                if not on:
                    v += 1
    return v


# ------------------------------------------------------------------- selftest

def _feasible_fixture():
    """A small plan whose declared facts CAN all hold: unique corners, a real
    entry on the entrance front, satisfiable doors."""
    return {
        "id": "cp-selftest-feasible", "name": "CP selftest, feasible",
        "style": "georgian-colonial-american",
        "context": {"entrance_faces": "S"},
        "levels": [{"id": "ground", "index": 0, "floor_to_ceiling_ft": 9, "rooms": [
            {"id": "porch", "type": "entry-porch", "width_ft": 6, "length_ft": 10,
             "exterior_walls": ["S"], "doors": [{"to": "hall"}, {"to": "exterior"}]},
            {"id": "hall", "type": "entrance-hall", "width_ft": 10, "length_ft": 14,
             "doors": [{"to": "porch"}, {"to": "parlor"}, {"to": "kitchen"}]},
            {"id": "parlor", "type": "parlor", "width_ft": 14, "length_ft": 16,
             "exterior_walls": ["S", "W"], "doors": [{"to": "hall"}]},
            {"id": "kitchen", "type": "kitchen", "width_ft": 12, "length_ft": 14,
             "exterior_walls": ["N"], "doors": [{"to": "hall"}]},
        ]}]}


def _multi_element_fixture():
    """Three massing elements -- a main block, a hyphen, a dependency -- whose door graph is
    consistent with being three masses: every cross-element door goes THROUGH the hyphen, which
    is the only room that touches both of its neighbours.

    WP-11.11. This is the positive half of the acceptance surface: `_k5_fixture` proves the
    model still refuses what cannot be built, and this proves it can now build what can. The
    hand-tagged `tidewater-georgian-careful` is deliberately NOT this fixture -- that record
    declares a door between a main-block dining room and a dependency butler's pantry, so CP
    proves it unbuildable, which is a finding about the record and a bad acceptance test."""
    return {
        "id": "cp-selftest-multi-element", "name": "CP selftest, three massing elements",
        "style": "georgian-colonial-american",
        "context": {"entrance_faces": "S"},
        "levels": [{"id": "ground", "index": 0, "floor_to_ceiling_ft": 9, "rooms": [
            {"id": "porch", "type": "entry-porch", "width_ft": 6, "length_ft": 10,
             "exterior_walls": ["S"], "doors": [{"to": "hall"}, {"to": "exterior"}]},
            {"id": "hall", "type": "entrance-hall", "width_ft": 10, "length_ft": 14,
             "exterior_walls": ["W"],
             "doors": [{"to": "porch"}, {"to": "parlor"}, {"to": "link"}]},
            {"id": "parlor", "type": "parlor", "width_ft": 14, "length_ft": 16,
             "exterior_walls": ["S", "E"], "doors": [{"to": "hall"}]},
            {"id": "link", "type": "gallery-corridor", "width_ft": 8, "length_ft": 12,
             "block": "w-dep", "hyphen": True, "exterior_walls": ["N", "S"],
             "doors": [{"to": "hall"}, {"to": "kitchen"}]},
            {"id": "kitchen", "type": "kitchen", "width_ft": 14, "length_ft": 16,
             "block": "w-dep", "exterior_walls": ["N", "S", "W"],
             "doors": [{"to": "link"}, {"to": "pantry"}]},
            {"id": "pantry", "type": "pantry", "width_ft": 6, "length_ft": 10,
             "block": "w-dep", "exterior_walls": ["W"], "doors": [{"to": "kitchen"}]},
        ]}]}


def _k5_fixture():
    """Five rooms, every pair sharing a door: the door graph is K5, which is
    non-planar — no arrangement of touching rectangles can realize it. A TRUE
    conflict on the one axis that never downgrades (doors are topology)."""
    rooms = []
    ids = [f"r{i}" for i in range(5)]
    for i, rid in enumerate(ids):
        rooms.append({"id": rid, "type": "parlor", "width_ft": 12, "length_ft": 12,
                      "doors": [{"to": o} for o in ids if o != rid]})
    return {"id": "cp-selftest-k5", "name": "CP selftest, K5 doors",
            "style": "georgian-colonial-american",
            "levels": [{"id": "ground", "index": 0, "floor_to_ceiling_ft": 9,
                        "rooms": rooms}]}


def selftest():
    """The solver's acceptance surface on fast fixtures (the full best-of-800
    benchmark lives in tests/test_solver.py). Exit 3 (COULD NOT EVALUATE)
    without OR-Tools — check_all reports that as N/EV, never as a pass."""
    try:
        import ortools  # noqa: F401
    except ImportError:
        print("COULD NOT EVALUATE: the ortools package is not installed (pip install "
              "ortools). The CP-SAT solver was not exercised — this is not a pass; "
              "geometry.solve() falls back to the hill-climb and says so.")
        return 3

    failures = 0

    res = solve_cp(_feasible_fixture(), time_limit_s=25)
    if "best" not in res:
        print(f"  FAIL feasible fixture did not solve: {str(res)[:200]}")
        failures += 1
    else:
        g = res["best"]["ground"]
        W, H = res["fpd"]["W"], res["fpd"]["H"]
        probs = []
        px, py, pw, ph = g["porch"]
        if py > 0.01:
            probs.append("the entry porch is off the S front")
        kx, ky, kw, kh = g["kitchen"]
        if abs((ky + kh) - H) > 0.01:
            probs.append("kitchen is off its declared N wall")
        hx, hy, hw, hh = g["hall"]
        touching = (abs(px + pw - hx) < 0.01 or abs(hx + hw - px) < 0.01
                    or abs(py + ph - hy) < 0.01 or abs(hy + hh - py) < 0.01)
        if not touching:
            probs.append("porch and hall do not share a wall despite their door")
        if probs:
            print("  FAIL feasible fixture: " + "; ".join(probs))
            failures += 1
        else:
            print(f"  OK   feasible fixture: solved, entry on the front, doors touch "
                  f"({res['solver']['status']}, {res['solver']['wall_time_s']}s)")

    res = solve_cp(_k5_fixture(), time_limit_s=25)
    if not res.get("infeasible", {}).get("proven"):
        print(f"  FAIL K5 fixture was not proven infeasible: {str(res)[:200]}")
        failures += 1
    else:
        conflicts = res["infeasible"]["conflicts"]
        if not any("share a door" in c for c in conflicts):
            print(f"  FAIL K5 conflicts do not name the doors: {conflicts[:3]}")
            failures += 1
        else:
            print(f"  OK   K5 fixture: proven infeasible, {len(conflicts)} door "
                  f"conflict(s) named (a non-planar door graph cannot be a floor plan)")

    # WP-11.11 -- the positive half: a plan with three massing elements is PLACED, and every
    # room is inside its own element rather than flattened into the main block.
    res = solve_cp(_multi_element_fixture(), time_limit_s=25)
    if "best" not in res:
        print(f"  FAIL multi-element fixture did not solve: {str(res)[:220]}")
        failures += 1
    else:
        # through `_mod` and therefore through modcache -- CLAUDE.md's standing trap, with
        # `tests/test_modcache.py` behind it, and it caught this line in the full suite
        plan = _multi_element_fixture()
        levels, prep = GEO.prep_rooms(plan)
        els = GEO.blocks_for(plan, res["fpd"], prep, 0)
        owner = {rid: e for e in els for rid in e["rooms"]}
        probs = []
        if len(els) != 3:
            probs.append(f"the fixture makes {len(els)} element(s), not 3")
        worst = 0.0
        for rid, (x, y, w, h) in res["best"]["ground"].items():
            e = owner.get(rid)
            if not e:
                probs.append(f"{rid} belongs to no element")
                continue
            worst = max(worst, e["x"] - x, e["y"] - y,
                        (x + w) - (e["x"] + e["W"]), (y + h) - (e["y"] + e["H"]))
        if worst > 0.01:
            probs.append(f"a room is drawn {worst:.2f} ft outside its own element")
        if probs:
            print("  FAIL multi-element fixture: " + "; ".join(probs))
            failures += 1
        else:
            print(f"  OK   multi-element fixture: 3 elements placed, every room inside its own "
                  f"({res['solver']['status']}, {res['solver']['wall_time_s']}s)")

    if failures:
        print(f"\n{failures} selftest failure(s).")
        return 1
    print("\ngeometry_cp selftest: the solver proves what it places and names what it refuses.")
    return 0


if __name__ == "__main__":
    import sys as _sys
    if len(_sys.argv) > 1 and _sys.argv[1] == "selftest":
        _sys.exit(selftest())
    print(__doc__.split("\n\n")[0])
    print("Run 'python3 build/geometry_cp.py selftest', or use geometry.solve().")
