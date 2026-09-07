#!/usr/bin/env python3
"""depth_floor.py — the depth a block needs before its roof stops reading as a truss (WP-11.10).

WHAT THIS IS FOR, AND WHY IT REFUSES TO BE A CAP.

`geometry.derive_footprint` bounds a block's depth from ABOVE (`H <= depth_for(W) * 1.18`) and
from below by nothing at all. Move a programme out into a wing and `need` falls, `H = need / W`
falls with it, and the block gets shallower with no floor -- measured on the re-authored
`centre-passage-double-pile` fixture, a main block of 45 x 28.89 ft, which
`faults/truss-flattened-pitch.json` then convicts at 0.4066 against its own 0.45.

The obvious fix is a floor at the massing's own pile (`geometry.PILE["double-pile"] = 36.0`).
**MEASURED AND REFUSED**: it would move `spec-builder-colonial`, a shipped reference plan, from
30.75 to 36.0 ft -- 262 sf of empty floor, 17.1% more footprint than programme -- to satisfy a
rule that is not convicting it. A pile is a TYPICAL depth, and reading a typical value as a hard
floor is how an invented number enters a corpus.

So the floor is derived from the FAULT'S OWN RULE instead, which is a sourced statement the
corpus already makes:

    roof_height_eave_to_ridge / wall_height_grade_to_eave  at-least  0.45

with `roof_height = (min(W, D) / 2) * (pitch / 12)` (structure.py::roof_heights, a single ridge
over the shorter OUTSIDE dimension) and `wall_height = grade_to_eave - grade_to_floor`. Solving
for the span:

    min_outside_span >= threshold * wall_height_ft * 24 / pitch

**THE THRESHOLD IS READ FROM THE FAULT RECORD, NEVER TRANSCRIBED.** A figure copied out of the
record it comes from is the defect WP-11.7 records (`facade_share` carrying its own band as a
literal beside the rule that states it), and this file would be the obvious next instance.

AND IT IS A DISCLOSURE, NOT A CAP. Three measurements refused the cap, and they are the
package's finding rather than a caveat:

  * **Only 3 of the 16 plan records have a style with a migrated `roof_pitch_rise_per_12`
    constraint at all.** On the other 13 the floor is COULD NOT EVALUATE, and the placer must
    not invent a pitch to get a number -- `structure.roof_heights` already refuses exactly this
    ("ridge height left unjudged rather than computed off an invented pitch").
  * **One of the three is a `good-*` reference plan the fault already convicts FATALLY**:
    `good-05-lobby-gallery-mansion` reads 0.2509 against 0.45. Its style is
    `italian-renaissance-revival` and the fault's licence names `italianate-american` -- a
    SIBLING -- so the exception never reaches it. That is
    `oq/a-licence-matches-the-style-id-exactly-and-never-its-descendants`, recorded and unruled.
  * **The floor that plan implies is 69.31 ft against a drawn 38.64** -- an 80% deeper house,
    demanded of a villa whose low pitch is the point of the style. A cap here would propagate a
    known-broken licence mechanism into the placer, where it would be a hard constraint instead
    of a finding a reader can weigh.

A cap becomes available when that licence question is ruled. Until then the number is published
and nothing acts on it: `oq/the-depth-a-roof-needs-is-known-and-cannot-be-enforced`.

IT IS A LEAF, for `build/storeys.py`'s reason and it must stay one: `structure.py` loads
`geometry.py`, so anything `geometry` imports may not reach back into `structure`. Everything
here is read from JSON directly.
"""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _storeys():
    """`build/storeys.py`, the OTHER leaf. Leaf-to-leaf is allowed and leaf-to-sibling is not:
    `storeys.py`'s own docstring carries the same rule and the same reason."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "tdl_storeys", os.path.join(ROOT, "build", "storeys.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

# structure.py's own constant, TRANSCRIBED, and the transcription is guarded:
# tests/test_depth_floor.py holds it against `structure.DEFAULT_GRADE_TO_FIRST_FLOOR_FT` so the
# two cannot drift. It is transcribed rather than imported because importing `structure` from a
# module `geometry` reads would close the cycle this file exists outside of.
DEFAULT_GRADE_TO_FIRST_FLOOR_FT = 2.0

_FAULT = os.path.join(ROOT, "faults", "truss-flattened-pitch.json")


def substituted_bounds_test(style_id):
    """The `exceptions[].bounds_test` that REPLACES the primary test for this style, or None.

    **A FAULT'S TESTS LIVE IN THREE PLACES AND THE THIRD IS THE ONE THAT BITES** (CLAUDE.md):
    `core.check_measurements` SUBSTITUTES an exception's `bounds_test` for the primary on a
    matching style. Inverting the primary where a bounds_test has replaced it inverts a rule
    nobody is applying.

    **THIS WAS FOUND BY MEASUREMENT, NOT BY READING.** The first version of this file agreed with
    the fault on 2 of 3 judgeable plans and DISAGREED on `good-03-parlor-drawing-room-house`: the
    floor said `ok` while the fault convicted at "22.6 against between 33.7 and 39.8" -- a band in
    different units entirely, because `greek-revival-american` carries an exception whose
    `bounds_test` measures something else. The floor was right about the primary and the primary
    was not the rule in force.

    Matching is `style == e["style"]` because that is what `core.py`'s three selection sites do.
    It is EXACT and never reaches a descendant -- that is
    `oq/a-licence-matches-the-style-id-exactly-and-never-its-descendants`, recorded and unruled --
    so this reads the same way rather than inventing a chain walk the corpus has not ruled on.
    """
    try:
        d = json.loads(open(_FAULT).read())
    except OSError:
        return None
    for e in d.get("exceptions") or []:
        if e.get("style") == style_id and e.get("bounds_test"):
            return e["bounds_test"]
    return None


def fault_threshold():
    """The fault's own floor, READ. Returns (value, direction, expression) or (None, ...).

    Never transcribed. A checker carrying a copy of the number it checks is one rule in two
    places, which is the defect this corpus keeps meeting; and the fault is data, so it can move
    without this file being edited -- which is the whole point of reading it.
    """
    try:
        d = json.loads(open(_FAULT).read())
    except OSError:
        return None, None, None
    t = d.get("test") or {}
    if t.get("expression") != "roof_height_eave_to_ridge / wall_height_grade_to_eave":
        # The rule this file inverts is no longer the rule the fault states. Refuse rather than
        # keep solving an expression nobody asserts any more.
        return None, t.get("direction"), t.get("expression")
    if t.get("direction") != "at-least" or not isinstance(t.get("threshold"), (int, float)):
        return None, t.get("direction"), t.get("expression")
    return float(t["threshold"]), t["direction"], t["expression"]


def style_roof_pitch(style_id):
    """The style's own migrated `roof_pitch_rise_per_12`, or None where it has none.

    **THE FIRST VERSION OF THIS FUNCTION WAS WRONG TWO WAYS AND THAT IS THE ENTRY WORTH KEEPING.**
    It walked `constraints/*.json` filtering on `applies_to_styles`, and it dropped the
    `direction == "between"` branch. `structure._style_roof_pitch` reads the constraints ON THE
    STYLE NODE (`styles/<id>.json`, where the loader has already resolved them) and takes the
    MIDPOINT of a `between`. So this returned None for `tidewater-georgian` where structure
    returns 8.0 -- caught on the first run, by comparing against the function it was copied
    from rather than by reading it.

    It is a THIRD spelling of a walk `structure.py` and `roof.py` already share -- roof.py's own
    comment says "byte-for-byte the same logic as build/structure.py's own function" -- and it
    exists only because this file must stay a LEAF (structure.py loads geometry.py, so anything
    geometry reads may not reach back into structure). **The guard is agreement, not care**:
    `tests/test_depth_floor.py` holds this against `structure._style_roof_pitch` on every style
    in the corpus, which is the mechanism `test_grammar_agreement.py` uses for the citation
    grammar's three spellings. Do not add a fourth without extending that test.
    """
    p = os.path.join(ROOT, "styles", f"{style_id}.json")
    try:
        node = json.loads(open(p).read())
    except (OSError, ValueError, TypeError):
        return None
    for c in node.get("constraints") or []:
        t = c.get("test") or {}
        if t.get("expression") != "roof_pitch_rise_per_12":
            continue
        if t.get("direction") == "between":
            return (t["threshold"] + t["upper"]) / 2.0
        if t.get("direction") in ("at-least", "at-most"):
            return float(t["threshold"])
    return None


def wall_height_ft(plan):
    """grade-to-eave less grade-to-first-floor, which is what the fault's denominator means.

    `structure.roof_heights` builds grade_to_eave as `DEFAULT_GRADE_TO_FIRST_FLOOR_FT + sum(storey
    heights)` and the elevation then subtracts the ground storey's `grade_to_floor_ft`, which IS
    that same constant -- so the two cancel and the denominator is the SUM OF THE STOREY HEIGHTS.
    Derived here rather than assumed: a reader who takes it for the eave height is out by the
    foundation, and that is the sign that flatters.

    **IT TAKES THE PLAN, NOT A LIST OF HEIGHTS, BECAUSE THE FIRST VERSION TOOK THE LIST AND ITS
    OWN CLI THEN FED IT THE WRONG ONE** -- `floor_to_ceiling_ft` (11 + 10 = 21 ft on the Tidewater
    plan) where the denominator wants the STOREY heights `storeys.py` derives from those ceilings
    (12.28 + 11.16 = 23.44). An 11.6% error in the denominator, in the direction that makes the
    floor look smaller and the house look better. A signature that lets a caller supply the wrong
    number is a signature that will be handed the wrong number.

    Returns (wall_ft, reason): `None` with a reason where any level states no ceiling at all --
    `storey_heights` returns `storey_height_ft: None` there on purpose, and summing that as zero
    would be the invented 9.0 ft it removed, arriving from the other side.
    """
    rows = _storeys().storey_heights(plan)
    if not rows:
        return None, "the plan states no levels"
    missing = [r.get("id") or r.get("index") for r in rows if r.get("storey_height_ft") is None]
    if missing:
        return None, (f"level(s) {missing} state no ceiling height, so storeys.py returns no "
                      f"storey height for them and the fault's denominator is unknown. Summing "
                      f"those as zero would be the invented figure storeys.py exists to refuse")
    return sum(r["storey_height_ft"] for r in rows), None


def min_span_ft(wall_ft, pitch, threshold):
    """The shortest OUTSIDE span whose roof still clears the fault, or None where unjudged."""
    if not pitch or threshold is None or not wall_ft:
        return None
    return threshold * wall_ft * 24.0 / pitch


def evaluate(plan, exterior_wall_in=0.0, clear_span_ft=None):
    """FOUR verdicts, and `unjudged` is never collapsed into `ok`.

    Returns a dict carrying `verdict` in {ok, below, unjudged}, the numbers it used, and a
    `reason` on every unjudged answer. `clear_span_ft` is the room extent the placer works in;
    the fault measures the OUTSIDE envelope, so the wall thickness is added before comparing and
    the returned floor is given in BOTH so no caller has to convert one into the other and get it
    wrong.
    """
    thr, direction, expr = fault_threshold()
    if thr is None:
        return {"verdict": "unjudged",
                "reason": f"faults/truss-flattened-pitch.json no longer states the rule this "
                          f"derivation inverts (expression {expr!r}, direction {direction!r}); "
                          f"the floor is not computed off a rule nobody asserts",
                "threshold": None}
    style_id = plan.get("style")
    sub = substituted_bounds_test(style_id)
    if sub is not None:
        return {"verdict": "unjudged", "threshold": thr, "substituted_bounds_test": sub,
                "reason": f"faults/truss-flattened-pitch.json carries an exception for style "
                          f"'{style_id}' whose `bounds_test` REPLACES the primary test, so the "
                          f"rule this floor inverts is not the rule in force on this house. "
                          f"Inverting the primary here would state a floor for a test nobody runs"}
    pitch = style_roof_pitch(style_id)
    if pitch is None:
        return {"verdict": "unjudged", "threshold": thr, "pitch": None,
                "reason": f"style '{style_id}' has no migrated roof_pitch_rise_per_12 constraint, "
                          f"so the ridge height is unknown -- structure.roof_heights refuses the "
                          f"same way rather than computing off an invented pitch. 13 of the 16 "
                          f"plan records in this tree take this branch"}
    wall_ft, why = wall_height_ft(plan)
    if not wall_ft:
        return {"verdict": "unjudged", "threshold": thr, "pitch": pitch,
                "reason": why or "the fault's denominator is unknown"}
    out_floor = min_span_ft(wall_ft, pitch, thr)
    grow = 2.0 * (exterior_wall_in or 0.0) / 12.0
    clear_floor = out_floor - grow
    r = {"threshold": thr, "pitch": pitch, "wall_height_ft": round(wall_ft, 3),
         "min_outside_span_ft": round(out_floor, 3),
         "min_clear_span_ft": round(clear_floor, 3),
         "exterior_wall_in": exterior_wall_in,
         "rule": "min_outside_span >= threshold * wall_height_ft * 24 / pitch, inverted from "
                 "faults/truss-flattened-pitch.json's own test"}
    if clear_span_ft is None:
        r["verdict"] = "unjudged"
        r["reason"] = "no span was supplied to compare the floor against"
        return r
    r["clear_span_ft"] = round(float(clear_span_ft), 3)
    r["verdict"] = "below" if float(clear_span_ft) < clear_floor - 1e-9 else "ok"
    return r


def main(argv=None):
    import argparse, sys
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("plan", nargs="?", help="a plan record to report on")
    a = ap.parse_args(argv)
    thr, direction, expr = fault_threshold()
    print(f"fault threshold (read): {thr} {direction}  [{expr}]")
    if not a.plan:
        return 0
    plan = json.loads(open(a.plan).read())
    print(json.dumps(evaluate(plan), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
