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
    record, so it is driven: the sheet must say the stacks were not drawn."""
    el = copy.deepcopy(elev)
    el["roof_record"].setdefault("elevation_profiles", {})["E"] = []
    svg, marks = _draw(el, "S")
    assert marks == 0
    assert "STACK(S) NOT DRAWN" in svg
