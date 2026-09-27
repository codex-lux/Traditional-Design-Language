"""ONE STACK, ONE SIZE, ON EVERY SURFACE -- AND ON THE CENTRE-LINE PATH TOO (audit, 27 Sep 2026).

WP-14.6 gave every surface the placement's own square (`plan_rect_ft`) and left the SIZE on one
path. `roof.chimney_positions` copied `stack_plan_in`, its judgment and its basis onto the chimney
records only where the plan states its hearths; a centre-line stack -- a record that states no
hearth, whose placement seats one square per gable end -- carried its square and no size. Driven
on the Tidewater record with its hearths stripped, measured on the tree before the fix:

  * the roof plan drew both stacks as a POSITION ONLY under "THE RECORD STATES NO PLAN SIZE OR NO
    SEATED SQUARE FOR THEM", beside a plan sheet drawing those two squares at 22 in, from the same
    stack record;
  * on a FRAME wall the elevation refused both -- "NO RECORD STATES THEIR PLAN SIZE" -- because its
    own figure was a second reading of brick-course's rule, taken on a masonry wall only;
  * and the scene wrote "the plan size is stated as None in".

No shipped plan reaches this (the one plan with stacks states its hearths), which is why nothing
saw it: census V17 and F1 read the shipped sheets. So the house is DRIVEN, on both walls, and its
premise asserted -- the placement's stacks carry a size, so the size is there to be dropped.
"""
import copy
import json
import os
import re
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402


def _L(n):
    return modcache.load(n, os.path.join(ROOT, "build", n + ".py"))


GEO, ST, RF, EL = _L("geometry"), _L("structure"), _L("roof"), _L("elevation")
RE, RR, SC = _L("render_elevation"), _L("render_roof"), _L("scene")
WALLS = (None, "platform-frame")          # the record's own masonry, and a frame wall


def _centre_line_house(wall):
    with open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json"), encoding="utf-8") as fh:
        p = json.load(fh)
    for lv in p["levels"]:
        for r in lv["rooms"]:
            r.pop("hearth", None)
    if wall:
        p.setdefault("declared", {})["construction_type"] = wall
    saved = GEO._SOLVE_CACHE
    GEO._SOLVE_CACHE = {}
    try:
        placed = GEO.solve(p, None, 250, engine="heuristic")
    finally:
        GEO._SOLVE_CACHE = saved
    sec = ST.build_section(placed, None, geometry_result=placed)
    roof = RF.build_roof(placed, section=sec)
    return placed, sec, roof


@pytest.fixture(scope="module", params=WALLS, ids=["masonry", "frame"])
def house(request):
    placed, sec, roof = _centre_line_house(request.param)
    assert placed["hearths"]["placed_from"] == "centre-line", "the premise: no stated hearth"
    stacks = placed["hearths"]["stacks"]
    assert stacks and all(s.get("stack_plan_in") for s in stacks), \
        "the premise: the placement's stacks carry a size, so the size is there to be dropped"
    if request.param:
        assert sec["wall"].get("bearing") != "load-bearing-masonry", "the premise: a frame wall"
    return placed, sec, roof


def test_each_roof_chimney_carries_its_own_squares_size(house):
    placed, _sec, roof = house
    by_wall = {s["wall"]: s for s in placed["hearths"]["stacks"]}
    seated = [c for c in roof["chimneys"]["positions"] if c.get("plan_rect_ft")]
    assert seated
    for c in seated:
        s = next(v for v in by_wall.values() if v.get("side") == c.get("side"))
        for k in ("stack_plan_in", "stack_plan_judgment", "stack_plan_basis"):
            assert c.get(k) == s.get(k), (k, c.get(k), s.get(k))


def test_the_roof_plan_draws_the_stated_square_and_not_a_position(house, tmp_path):
    _placed, _sec, roof = house
    path = tmp_path / "roof.svg"
    RR.render_roof(roof, str(path))
    svg = path.read_text()
    n = len([c for c in roof["chimneys"]["positions"] if c.get("plan_rect_ft")])
    assert len(re.findall(r'<rect class="chm', svg)) == n, "each seated stack drawn as its square"
    assert "NO PLAN SIZE" not in svg and "AS A POSITION ONLY" not in svg


def test_the_elevation_reads_the_size_the_roof_carries_and_draws_the_stacks(house, tmp_path):
    placed, sec, roof = house
    elev = EL.build_elevation(placed, None, section=sec, roof=roof)
    sizes = {c["stack_plan_in"] for c in roof["chimneys"]["positions"] if c.get("stack_plan_in")}
    assert elev["chimney_stack_plan_in"] in sizes
    path = tmp_path / "elev.svg"
    RE.render_elevation(elev, str(path), face="S")
    svg = path.read_text()
    assert 'class="ch' in svg, "the long face draws the stacks the placement seats"
    assert "NO RECORD STATES THEIR PLAN SIZE" not in svg


def test_the_scene_never_states_a_size_it_does_not_have(house):
    placed, sec, roof = house
    elev = EL.build_elevation(placed, None, section=sec, roof=roof)
    scene = SC.build_scene(placed, sec, roof, elev)
    assert "as None in" not in json.dumps(scene)
    assert [s for s in scene["solids"] if s["id"].startswith("chimney-")], "the stacks reach the model"


def test_a_sheet_that_draws_no_stack_does_not_say_it_drew_one_at_a_judged_size(tmp_path):
    """The legend's "STACK DRAWN 22.0" SQUARE -- A JUDGMENT" printed wherever the record carried a
    judged size, drawn or not. Driven: the same masonry house with the roof's stacks withdrawn, so
    the record still carries brick-course's judged 22 in and no stack is drawn."""
    placed, sec, roof = _centre_line_house(None)
    roof = copy.deepcopy(roof)
    roof["chimneys"]["positions"] = []
    elev = EL.build_elevation(placed, None, section=sec, roof=roof)
    assert elev.get("chimney_stack_plan_in") and elev.get("chimney_stack_plan_judgment"), \
        "the premise: the record still carries a judged size"
    path = tmp_path / "elev.svg"
    RE.render_elevation(elev, str(path), face="S")
    svg = path.read_text()
    assert 'class="ch' not in svg
    assert "STACK DRAWN" not in svg
