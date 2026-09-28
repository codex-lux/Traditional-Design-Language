"""A STACK THE ROOF PLACES AND THE SHEET DOES NOT DRAW IS SAID, FOR EACH REASON (audit, 27 Sep 2026).

WP-14.6 made every elevation face draw a stack from the square the placement seats, and refuse one
it cannot seat. The refusals are said on the sheet -- "N STACK(S) NOT DRAWN -- THE PLACEMENT SEATS
NO SQUARE FOR THEM", republishing the placement's own reason where it wrote one, and "STACKS NOT
DRAWN -- THIS ROOF'S RIDGE RUNS FRONT TO BACK" -- and the audit's test-meaning pass (auditor B,
W4) found neither sentence read by any test, with census V9 reading only unsized stacks and V17
only seated ones: the population this fix emptied was the one nothing looked at. Its own evidence:
47 of the style sweep's roof entries seat no square, drew stacks before WP-14.6, and draw none now,
said only by this line.

No shipped sheet reaches either branch as the census draws it (the one plan with stacks seats both
squares on a side-gable roof), so each is DRIVEN from the Tidewater front, with the premise that
the undriven sheet draws its stacks asserted first.
"""
import copy
import json
import os
import sys
import tempfile

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402


def _L(n):
    return modcache.load(n, os.path.join(ROOT, "build", n + ".py"))


GEO, ST, EL, RE = _L("geometry"), _L("structure"), _L("elevation"), _L("render_elevation")


@pytest.fixture(scope="module")
def elev():
    with open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json"), encoding="utf-8") as fh:
        plan = json.load(fh)
    saved = GEO._SOLVE_CACHE
    GEO._SOLVE_CACHE = {}
    try:
        placed = GEO.solve(plan, None, 250, engine="heuristic")
    finally:
        GEO._SOLVE_CACHE = saved
    sec = ST.build_section(placed, None, geometry_result=placed)
    el = EL.build_elevation(placed, None, section=sec)
    assert _draw(el, "S")[1] > 0, "the premise: the undriven front draws its stacks"
    return el


def _draw(el, face):
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, f"{face}.svg")
        RE.render_elevation(el, out, face=face)
        svg = open(out, encoding="utf-8").read()
    return svg, svg.count('class="ch')


def test_a_stack_with_no_seated_square_is_not_drawn_and_is_said(elev):
    el = copy.deepcopy(elev)
    n = 0
    for c in el["roof_record"]["chimneys"]["positions"]:
        n += bool(c.pop("plan_rect_ft", None))
    assert n == 2, "the premise: two seated squares to withdraw"
    svg, marks = _draw(el, "S")
    assert marks == 0
    assert "2 STACK(S) NOT DRAWN — THE PLACEMENT SEATS NO SQUARE FOR THEM" in svg


def test_the_placements_own_reason_is_republished_not_composed(elev):
    el = copy.deepcopy(elev)
    for c in el["roof_record"]["chimneys"]["positions"]:
        c.pop("plan_rect_ft", None)
    hr = el["section"]["geometry"].setdefault("hearths", {})
    hr["unplaced"] = list(hr.get("unplaced") or []) + [
        {"what": "the stacks", "reason": "a reason only this test writes"}]
    svg, _marks = _draw(el, "S")
    assert "THE PLACEMENT SEATS NO SQUARE FOR THEM: A REASON ONLY THIS TEST WRITES" in svg


def test_a_ridge_running_front_to_back_is_said_and_draws_no_stack(elev):
    el = copy.deepcopy(elev)
    el["roof_record"]["main"]["ridge"]["axis"] = "y"
    svg, marks = _draw(el, "S")
    assert marks == 0
    assert "STACKS NOT DRAWN — THIS ROOF’S RIDGE RUNS FRONT TO BACK" in svg


def test_a_stack_refused_for_another_reason_is_not_dropped_in_silence(elev):
    """THE THIRD REFUSAL, FOUND WRITING THE TWO ABOVE. `_stack_outline` also refuses a stack whose
    roof carries no end profile to foot it on (`no-profile`), and the loop dropped that one with a
    bare `continue` -- counted nowhere, said nowhere. Reachable only through a malformed roof
    record, so it is driven: the sheet must say the stacks were not drawn.

    RE-DRIVEN 27 Sep 2026 (Phase 15, WP-15.5). This drove the FRONT, where both stacks then stood
    on the roof line; they stand on the ground now, and a stack standing on the ground needs no
    roof profile, so the front no longer reaches the refusal (the test below holds that half).
    The stack a profile still foots is the one the house hides: the far stack seen from the other
    gable, driven here by taking the near one off the record. It is drawn from the W face, whose
    own roof reads the W profile, because the E face draws its roof from the very profile this
    empties and has no sheet at all without it -- a crash, not a refusal."""
    el = copy.deepcopy(elev)
    el["roof_record"].setdefault("elevation_profiles", {})["E"] = []
    W = el["footprint"]["width_ft"]
    pos = el["roof_record"]["chimneys"]["positions"]
    el["roof_record"]["chimneys"]["positions"] = [c for c in pos if c["plan_rect_ft"][0] >= W - 1e-6]
    assert len(el["roof_record"]["chimneys"]["positions"]) == 1 and len(pos) == 2, (
        "the premise: one stack outboard of each gable, and the near one taken off")
    assert all(c["plan_rect_ft"][2] <= 1e-6 for c in pos if c["plan_rect_ft"][0] < W - 1e-6)
    svg, marks = _draw(el, "W")
    assert marks == 0
    assert "1 STACK(S) NOT DRAWN — THE ROOF RECORD GIVES NO END PROFILE TO FOOT THEM ON" in svg


def test_a_stack_standing_on_the_ground_is_not_refused_for_a_roof_it_does_not_stand_on(elev):
    """WP-15.5. A stack drawn from grade is decided before the roof is read, so a roof record
    with no end profile refuses only the stacks that profile would foot. Refusing the front's two
    grounded stacks for want of it would be a refusal about something the drawing does not use --
    the fake-unjudged shape this corpus names beside the fake pass."""
    el = copy.deepcopy(elev)
    el["roof_record"].setdefault("elevation_profiles", {})["E"] = []
    svg, marks = _draw(el, "S")
    assert marks == 2, "both exterior stacks, drawn from grade"
    assert "NOT DRAWN — THE ROOF RECORD GIVES NO END PROFILE" not in svg
    assert "EXTERIOR STACKS DRAWN FROM GRADE TO CAP" in svg
