#!/usr/bin/env python3
"""What a `stacks_over` claim means, and what happens to one nobody can judge — ONE spelling.

**A LEAF, on `build/storeys.py`'s and `build/assemblies.py`'s precedent, and it must stay one.**
`geometry.py` loads `plan_check.py` at import time, so `plan_check` cannot load `geometry`, and
those are exactly the two files that have to agree about this. Every helper here imports no
sibling; what it needs from the corpus (`is_placed`) is passed in.

THE FIELD, AND THE SPLIT MADE AT PLAN SCHEMA 0.8.0
--------------------------------------------------
`stacks_over` is a STRUCTURAL claim: this room's plan sits over the plan of a room on the level
ONE BELOW. It is judged by CONTAINMENT (`lands`, below: the smaller rectangle at least 90%
inside the larger), charged at `geometry.STACK_W` by the search through the same function, and
reported by `plan_check`'s drawn layer. Until WP-13.2 it was judged by strict positive rectangle
intersection, under which a 0.16 sf corner was a landed stack -- the gate
(`tests/test_sheet_coherence.py`) measured the shipped Tidewater upper passage at 38% of itself
over the passage and the tally called it kept. The prover's soft penalty
(`geometry_cp.py`) still means intersection until WP-13.3 makes the stack hard there.

Until 0.8.0 the field's own description read *"room id on the level below, for plumbing and
structure"* — two duties in one field — and `plans/tidewater-georgian-careful.json` used it for
a ground-level powder room naming a ground-level cellar stair, which is the plumbing duty and
cannot be the structural one. The servicing duty is `wet_stack_with` now: any level, including
the claimant's own, and the target need not itself be wet, because a stack needs a vertical
chase and a stair shaft is one.

WHY A TALLY EXISTS AT ALL
-------------------------
Measured 5 Sep 2026, before this module: **`stacks_over` had seven readers and four different
definitions of "below", and every one of them declined in silence.**

  build/geometry.py `vertical_score`   iterates the UPPER rects and looks the target up in the
                                       GROUND rects, so an unanswerable claim is a bare
                                       `continue` — level 0 hard-wired as "below"
  build/geometry.py `bias`             the same, and it steers CANDIDATE GENERATION, not only
                                       the ranking
  build/geometry_cp.py                 keys `(1, r["id"])` / `(0, so)` — the same hard-wiring
  build/plan_check.py drawn layer      `if level_of[rid] == level_of[so]: continue`, with no
                                       note beside it
  build/plan_check.py reachability     minted an edge to the stair room with NO level test at
                                       all, so a same-level claim could forge one
  build/plan_check.py servicing        read the field level-blind, for the PLUMBING meaning
  build/check_partis.py                the target id must exist; the level relation unchecked

So the shipped Tidewater record carried FOUR claims of which THREE were judged, and no surface
anywhere said which three. An unjudged claim that reads exactly like a satisfied one is the
OQ 52 family, and this module is the answer to it: `claims == kept + broken + unjudged`, and
every unjudged entry carries the reason it could not be answered.

THE VERDICT IS READ OFF THE PLACED RECORD, NOT RE-DERIVED
---------------------------------------------------------
This is deliberately not a third transcription of the overlap test living inside each scorer:
it reads the coordinates the engines wrote back. So the tally cannot disagree with the
placement it describes, and the test it applies (`lands`) is the one `geometry.declared_stack_breaks`
charges by and `plan_check.drawn_layer` reports by -- for the reason `vertical_score`'s comment
already gives, that the search and the critic may not convict and acquit the same house.
"""

# The closed set of reasons a claim cannot be judged, each NAMED and the tuple built from the
# names. `judge` below reads the names; nothing indexes the tuple by position, because a reorder
# would then silently swap two reasons and every reader downstream -- including the one that
# decides whether a claim is `stack-unplaced` or `stack-unjudged` -- would change its answer with
# no test moving. Closed on
# `build/construction_vocabulary.py`'s precedent: a reader needing a reason that is not here
# must add it here and nowhere else, so the count of unjudged claims can never be a count of
# claims that took a branch nobody named.
NO_SUCH_ROOM = "the record declares no room with that id"
THIS_ROOM_UNPLACED = "this room is not placed"
TARGET_UNPLACED = "the room it names is not placed"
SAME_LEVEL = "the room it names is on this room's own level"
TOO_FAR_BELOW = "the room it names is more than one level below"
NOT_BELOW = "the room it names is not below this room at all"

STACK_UNJUDGED_REASONS = (NO_SUCH_ROOM, THIS_ROOM_UNPLACED, TARGET_UNPLACED,
                          SAME_LEVEL, TOO_FAR_BELOW, NOT_BELOW)

# The two reasons above that are the PLACEMENT's rather than the RECORD's. `plan_check` emits
# these as `stack-unplaced` -- the kind it has always used, which `build/critique.py` classes as
# a placement outcome -- and every other reason as `stack-unjudged`, a record error no engine can
# answer. Named rather than sliced out of the tuple by index, because an index into a tuple
# somebody may reorder is a silent re-classification waiting to happen.
PLACEMENT_REASONS = (THIS_ROOM_UNPLACED, TARGET_UNPLACED)


# The placer's own ceiling, and it is written down in two places in `geometry.py`:
# `_finish` does `best["ground"] if idx == 0 else (best["upper"] if idx == 1 else {})`, and
# `solve_heuristic` is written against `prep[0]` and `prep[1]`. TWO levels. A third is not
# placed, and until WP-11.6 nothing said so — measured on
# `plans/reference/bad-03-narrow-lot-townhome.json`, the corpus's only three-level record,
# whose one level-2 room came back with no geometry, no finding and no note while the sheet
# drew the house without its top floor.
PLACED_LEVEL_INDICES = (0, 1)


# The room types that take a rectangle in the block. ONE spelling, and it is here for the same
# reason the rest of this module is: `geometry.is_placed` and the drawn layer's new
# `rooms_unplaced` need the identical answer, and geometry.py cannot be loaded from plan_check.
# The catalogue is passed in (`{room type id: record}`) because this is a leaf.
#
# The two states it separates are BOTH real and both appear on the shipped corpus: a `terrace`
# whose own record puts it outside the footprint takes no rectangle and correctly has none,
# while `bad-03`'s level-2 `great-room` takes one and does not have it. Collapsing them is how
# a missing storey reads as a design decision.
OUTDOOR_FUNCTION_CLASSES = {"outdoor"}


def takes_a_rectangle(rtype, catalogue):
    r = (catalogue or {}).get(rtype) or {}
    if r.get("function_class") not in OUTDOOR_FUNCTION_CLASSES:
        return True                                   # every indoor room
    return bool((r.get("void") or {}).get("within_footprint"))   # OQ 55's reserved voids


def rooms_by_level(plan):
    """`{level index: {room id: room record}}`, from the record's own `levels`.

    `index` where the level states one and the list position where it does not. A function
    rather than four inline comprehensions because the inline ones disagreed: `plan_check`
    read `enumerate` and `geometry` read `lv["index"]`, and a level with no `index` key made
    them answer differently about the same record.
    """
    out = {}
    for i, lv in enumerate(plan.get("levels") or []):
        idx = lv.get("index")
        out[i if idx is None else idx] = {r["id"]: r for r in (lv.get("rooms") or [])}
    return out


def _rect(room):
    g = (room or {}).get("geometry")
    if not g:
        return None
    return (g["x_ft"], g["y_ft"], g["width_ft"], g["depth_ft"])


def overlaps(a, b):
    """Strict positive rectangle intersection -- TOUCHING, kept for the readers that mean it.

    This was the kept/broken test until WP-13.2, and `geometry_cp.py`'s reified stack penalty
    still means exactly this. It is NOT what "the stair hall stacks" means to a reader, which is
    why `judge` reads `lands` below; a caller wanting to know whether two plans touch at all is
    what this function is for now.
    """
    return (min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0]) > 0
            and min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1]) > 0)


# The share of the SMALLER rectangle that must lie inside the larger for a stack to land. 0.9
# is the gate's own figure (`test_declared_stacks_land_by_containment`), editorial, and it is
# a number rather than 1.0 because a landing drawn a few inches proud of its stair hall is a
# landed landing, and a rule that convicts it is a rule nobody will keep.
LANDS_FRACTION = 0.9


def lands(a, b, frac=LANDS_FRACTION):
    """A stack that LANDS: the smaller of the two rectangles lies at least `frac` of its own
    area inside the larger -- what a reader means by "this room stands over that one".

    ONE spelling. `judge` reads it for the record, `geometry.declared_stack_breaks` reads it
    for the search's charge and its strict-candidate selector, so the search and the critic
    cannot convict and acquit the same house. A rectangle of no area cannot land on anything and
    nothing can land on it: that is a refusal, not a division by zero.
    """
    ix = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
    iy = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
    if ix <= 0 or iy <= 0:
        return False
    smaller = min(a[2] * a[3], b[2] * b[3])
    if smaller <= 0:
        return False
    return (ix * iy) / smaller >= frac


def judge(plan):
    """Every `stacks_over` claim, sorted into kept / broken / unjudged-with-a-reason.

    Returns `(kept, broken, unjudged)`, each a list of entries carrying `room`, `over`,
    `field` and `level`; an unjudged entry also carries `reason`. Nothing is dropped: a caller
    can add the three lengths and get the number of claims the record makes.
    """
    by_level = rooms_by_level(plan)
    level_of = {rid: lvl for lvl, rooms in by_level.items() for rid in rooms}
    kept, broken, unjudged = [], [], []
    for lvl in sorted(by_level):
        for rid, r in by_level[lvl].items():
            so = r.get("stacks_over")
            if not so:
                continue
            e = {"room": rid, "over": so, "field": "stacks_over", "level": lvl}
            if so not in level_of:
                unjudged.append(dict(e, reason=NO_SUCH_ROOM))
            elif level_of[so] == lvl:
                unjudged.append(dict(
                    e, reason=SAME_LEVEL,
                    remedy="`wet_stack_with` carries a same-level claim; `stacks_over` cannot."))
            elif level_of[so] > lvl:
                unjudged.append(dict(e, reason=NOT_BELOW))
            elif lvl - level_of[so] > 1:
                unjudged.append(dict(e, reason=TOO_FAR_BELOW))
            elif _rect(by_level[lvl][rid]) is None:
                unjudged.append(dict(e, reason=THIS_ROOM_UNPLACED))
            elif _rect(by_level[level_of[so]][so]) is None:
                unjudged.append(dict(e, reason=TARGET_UNPLACED))
            else:
                (kept if lands(_rect(by_level[lvl][rid]),
                               _rect(by_level[level_of[so]][so])) else broken).append(e)
    return kept, broken, unjudged


# A SHARED CHASE, AND WHAT MAKES ONE (Phase 17, WP-17.1). `wet_stack_with` is the servicing claim:
# the two rooms' waste and supply can run in one vertical chase. That is a weaker relation than a
# structural stack and it is judged as one -- not containment, only that the chase has somewhere to
# run. Across levels the two plans must overlap by more than CHASE_MIN_RUN_FT on BOTH axes: a chase
# rising through a room's floor must come up inside the room above, and it needs a room's width of
# floor to come up through. On one level the two rooms must share a wall: the same two figures
# `structure._shared_segment` and `typefacts` use for a shared wall (facing edges within 0.4 ft, a
# common run longer than 1.0 ft), transcribed here because this module is a leaf and may import
# neither.
#
# THE CROSS-LEVEL TEST WAS `overlaps` UNTIL THE AUDIT OF PHASE 17 (30 Oct 2026), strict positive
# area with no minimum, so a 0.1 x 0.1 ft corner -- 0.01 sf -- read "kept, can share a chase", and a
# 0.001 ft corner too. That is the false "kept" this module's own docstring records for the
# structural relation (a 0.16 sf corner read as a landed stack until WP-13.2). The minimum is
# CHASE_MIN_RUN_FT on each axis, ONE figure for both branches, and it is EDITORIAL: the corpus states
# no chase cross-section, so no new figure is invented -- the same-level branch's own run is reused.
CHASE_EDGE_TOL_FT = 0.4
CHASE_MIN_RUN_FT = 1.0


def shares_chase(a, b, same_level):
    """Can one vertical chase serve both rooms? `a` and `b` are `(x, y, w, h)`."""
    if not same_level:
        ix = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
        iy = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
        return ix > CHASE_MIN_RUN_FT and iy > CHASE_MIN_RUN_FT
    ax0, ay0, ax1, ay1 = a[0], a[1], a[0] + a[2], a[1] + a[3]
    bx0, by0, bx1, by1 = b[0], b[1], b[0] + b[2], b[1] + b[3]
    if abs(ax1 - bx0) <= CHASE_EDGE_TOL_FT or abs(bx1 - ax0) <= CHASE_EDGE_TOL_FT:
        if min(ay1, by1) - max(ay0, by0) > CHASE_MIN_RUN_FT:
            return True
    if abs(ay1 - by0) <= CHASE_EDGE_TOL_FT or abs(by1 - ay0) <= CHASE_EDGE_TOL_FT:
        if min(ax1, bx1) - max(ax0, bx0) > CHASE_MIN_RUN_FT:
            return True
    return False


def wet_judge(plan):
    """Every `wet_stack_with` claim, sorted into kept / broken / unjudged-with-a-reason.

    The servicing twin of `judge`. Until Phase 17 nothing judged this claim on a placed house:
    `plan_check`'s servicing layer asks only whether the room it names is WET on the declared
    record, and the engines' wet-over-wet charge is generic (any upper wet room over any ground wet
    room). Lucas's ruling 5 (29 Oct 2026) moved BATH-OVER-WET-ROOM claims from `stacks_over` to
    this field. WP-17.1 executed it on a wider class -- every claim whose claimant is a bath, 17 in
    13 partis -- and two of those targets were not wet rooms (octagon-radial's dry pantry,
    connected-farmstead's back hall); Lucas ruled on 30 Oct 2026 that both go back to `stacks_over`,
    which leaves 15 claims in 12 partis (corrected by the audit of Phase 17, findings 33 and 43). A
    claim moved out of a refusing fact must not go quiet: it is still a claim about the placed
    house, so it is judged here and reported by the drawn layer -- as servicing, which refuses
    nothing."""
    by_level = rooms_by_level(plan)
    level_of = {rid: lvl for lvl, rooms in by_level.items() for rid in rooms}
    kept, broken, unjudged = [], [], []
    for lvl in sorted(by_level):
        for rid, r in by_level[lvl].items():
            ws = r.get("wet_stack_with")
            if not ws:
                continue
            e = {"room": rid, "with": ws, "field": "wet_stack_with", "level": lvl}
            if ws not in level_of:
                unjudged.append(dict(e, reason=NO_SUCH_ROOM))
                continue
            a = _rect(r)
            b = _rect(by_level[level_of[ws]][ws])
            if a is None:
                unjudged.append(dict(e, reason=THIS_ROOM_UNPLACED))
            elif b is None:
                unjudged.append(dict(e, reason=TARGET_UNPLACED))
            else:
                (kept if shares_chase(a, b, level_of[ws] == lvl) else broken).append(e)
    return kept, broken, unjudged


def report(plan, weight=None):
    """The block `geometry_report.stacking` carries, from both engines' record writers.

    `claims`, `kept`, `broken` and `unjudged` are the STRUCTURAL claims (`stacks_over`), which
    `typefacts.stacks` reads and a refusal can rest on. The servicing claims (`wet_stack_with`) sit
    beside them under `wet` and refuse nothing (WP-17.1)."""
    kept, broken, unjudged = judge(plan)
    n = len(kept) + len(broken) + len(unjudged)
    note = "This record declares no vertical stack." if not n else (
        f"{len(kept)} of {n} declared stack(s) land (the smaller room at least "
        f"{LANDS_FRACTION:.0%} inside the larger); {len(broken)} are drawn clear of the room "
        f"they name; {len(unjudged)} could not be evaluated and are named individually. "
        "Unjudged is not kept.")
    out = {"claims": n, "kept": kept, "broken": broken, "unjudged": unjudged, "note": note}
    wk, wb, wu = wet_judge(plan)
    if wk or wb or wu:
        out["wet"] = {"claims": len(wk) + len(wb) + len(wu), "kept": wk, "broken": wb,
                      "unjudged": wu,
                      "note": (f"{len(wk)} of {len(wk) + len(wb) + len(wu)} declared wet stack(s) "
                               f"can share a chase (plans overlapping by more than "
                               f"{CHASE_MIN_RUN_FT:g} ft each way across levels, a shared "
                               f"wall on one level); {len(wb)} cannot; {len(wu)} could not be "
                               f"evaluated. Servicing, not structure: none of these refuses a "
                               f"drawing.")}
    if weight is not None:
        out["weight"] = weight
    return out


def multi_level_disclosure(plan, is_placed):
    """Levels the placer never reached, stated on the record. `None` when it reached them all.

    `multi_element_disclosure`'s exact precedent (OQ 40): the layer cannot do the thing, so it
    says so on the record rather than returning numbers from an instrument pointed at half the
    building. `is_placed` is passed in because this is a leaf — it is `geometry.is_placed`, and
    it is what tells a level-2 great room (not placed, a defect) from a terrace outside the
    footprint (not placed, correct).
    """
    missing = []
    for lvl, rooms in sorted(rooms_by_level(plan).items()):
        if lvl in PLACED_LEVEL_INDICES:
            continue
        want = sorted(rid for rid, r in rooms.items() if is_placed(r.get("type")))
        if want:
            missing.append({"level": lvl, "rooms": want})
    if not missing:
        return None
    return {
        "levels_placed": list(PLACED_LEVEL_INDICES),
        "levels_not_placed": [m["level"] for m in missing],
        "rooms_not_placed": [rid for m in missing for rid in m["rooms"]],
        "note": ("COULD NOT EVALUATE: this record declares a level the placer does not place. "
                 "Both engines are written against level 0 and level 1 only, so every room "
                 "named here has no geometry — it is not drawn, it takes no drawn finding, and "
                 "any stack claimed onto or off it is unjudged. The house on the sheet is "
                 "missing a storey and this is the only thing that says so."),
    }
