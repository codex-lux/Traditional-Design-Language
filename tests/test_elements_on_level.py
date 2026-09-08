"""WP-11.15 — an element with no rooms on a level has no walls on that level.

The rule is WP-11.9's ruling 1 read one level up. It was spelled three times and written
wrongly a fourth: `structure.build_section` and `export_ifc` each carried a correct copy of the
comprehension, the search built its own map for level 0, and `geometry._disclose_spans` --
written three packages after the rule was established -- handed EVERY level EVERY element.

WHY NOTHING CAUGHT IT. No plan in this corpus carries a `block` tag, so `len(_els) > 1` is
false everywhere and the defective branch is unreachable on all sixteen shipped plans. The
guards here are therefore hand-built records, on WP-11.10's stated precedent: a guard that runs
only where the bug cannot occur is not a guard.

AND THE COUNT DID NOT MOVE. On the tagged Tidewater the phantom level-1 span REPLACED a real
one, so `over_capacity`, `len(marks)` and `worst_span_ft` read identically either way. Only the
contents differ -- which is what `plan_check` names, what `critique` classes and what the plate
prints. Every assertion below is therefore about WHERE a mark is, never about how many.
"""
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "build"))
import modcache  # noqa: E402

EL = modcache.load("elements", str(ROOT / "build" / "elements.py"))
GEO = modcache.load("geometry", str(ROOT / "build" / "geometry.py"))

# The dependency sits WEST of the main block, so its x range is negative and cannot be confused
# with any coordinate inside the main block. That is not decoration: the defect this file exists
# for published a span at -37..-7, and a fixture with both elements at positive x would let a
# wrong answer look plausible.
MAIN = {"id": "main", "role": "main", "x_ft": 0.0, "y_ft": 0.0,
        "width_ft": 40.0, "depth_ft": 42.0, "area_sf": 1680}
DEP = {"id": "service", "role": "dependency", "x_ft": -37.0, "y_ft": 9.0,
       "width_ft": 30.0, "depth_ft": 24.0, "area_sf": 720, "attached_to": "main"}


def _room(rid, rtype, x, y, w, d, block=None):
    r = {"id": rid, "type": rtype, "width_ft": w, "length_ft": d,
         "geometry": {"x_ft": x, "y_ft": y, "width_ft": w, "depth_ft": d}}
    if block:
        r["block"] = block
    return r


def _two_element_plan():
    """A placed record with a ground-floor dependency and a SINGLE-STOREY one at that.

    Level 0 has rooms in both elements; level 1 has rooms in the main block only, which is what
    the placer actually produces -- it reads a `block` tag on the ground level alone.
    """
    return {
        "id": "fixture-two-element", "style": "tidewater-georgian",
        "footprint": {"width_ft": 40.0, "depth_ft": 42.0, "bay_module_ft": 10.0,
                      "blocks": [MAIN, DEP]},
        "levels": [
            {"index": 0, "rooms": [
                _room("drawing", "drawing-room", 0.0, 0.0, 20.0, 21.0),
                _room("dining", "dining-room", 20.0, 0.0, 20.0, 21.0),
                _room("library", "library", 0.0, 21.0, 40.0, 21.0),
                _room("kitchen", "kitchen", -37.0, 9.0, 30.0, 12.0, block="service"),
                _room("pantry", "pantry", -37.0, 21.0, 30.0, 12.0, block="service"),
            ]},
            {"index": 1, "rooms": [
                _room("primary", "primary-bedroom", 0.0, 0.0, 40.0, 21.0),
                _room("chamber2", "bedroom", 0.0, 21.0, 40.0, 21.0),
            ]},
        ],
        "geometry_report": {"span_capacity": {"over_capacity": 0, "charge": 0.0}},
    }


# --------------------------------------------------------------------------- the rule itself

def test_an_element_with_no_rooms_on_a_level_is_not_on_that_level():
    plan = _two_element_plan()
    els = EL.elements(plan)
    assert [e["id"] for e in els] == ["main", "service"]
    g0 = EL.elements_on_level(plan, plan["levels"][0]["rooms"], els)
    g1 = EL.elements_on_level(plan, plan["levels"][1]["rooms"], els)
    assert [e["id"] for e in g0] == ["main", "service"], "the ground floor has both"
    assert [e["id"] for e in g1] == ["main"], (
        "the upper floor has rooms in the main block only, so the dependency has no walls "
        "there -- this is the whole rule")


def test_a_room_in_no_element_votes_for_no_element_and_not_for_the_main_block():
    """`element_of` returning None is COULD NOT EVALUATE. Defaulting it into element zero is
    the defect WP-11.9 names, not the fallback."""
    plan = _two_element_plan()
    els = EL.elements(plan)
    stray = _room("stray", "closet", 500.0, 500.0, 4.0, 4.0)
    assert EL.element_of(plan, stray, els) is None
    assert EL.elements_on_level(plan, [stray], els) == [], (
        "a room standing in no element must not be counted as putting the main block on a level")


def test_an_unplaced_room_carries_no_element():
    plan = _two_element_plan()
    els = EL.elements(plan)
    unplaced = {"id": "terrace", "type": "terrace", "width_ft": 14.0, "length_ft": 22.0}
    assert EL.elements_on_level(plan, [unplaced], els) == []


# ------------------------------------------------------- the defect, at the site that had it

def _marks(plan):
    GEO._disclose_spans(plan)
    return (plan["geometry_report"]["span_capacity"] or {}).get("marks")


def test_no_span_is_published_on_a_level_where_its_element_has_no_rooms():
    """THE GUARD. Before the fix this record published a 30 ft clear span at -37..-7 on level 1
    -- a joist run over a single-storey wing, on a storey that does not exist."""
    plan = _two_element_plan()
    marks = _marks(plan)
    if marks is None:
        pytest.skip("COULD NOT EVALUATE: construction/floor-structure.json was unreadable")
    dep_x = (DEP["x_ft"], DEP["x_ft"] + DEP["width_ft"])
    phantom = [m for m in marks
               if m["level"] == 1 and m["from_ft"] < dep_x[1] and m["to_ft"] > dep_x[0]]
    assert phantom == [], (
        "a span was published on level 1 inside the dependency's footprint, and the dependency "
        f"has no rooms on level 1: {phantom}")


def test_the_published_marks_are_the_spans_the_search_charged():
    """`_disclose_spans`' own docstring promises these are the spans `SPAN_W` charged, and
    WP-11.12's report says a second computation 'could convict a placement on numbers it was
    not chosen by'. It was a second computation, on different inputs, and it did."""
    plan = _two_element_plan()
    marks = _marks(plan)
    if marks is None:
        pytest.skip("COULD NOT EVALUATE: construction/floor-structure.json was unreadable")
    ST = modcache.load("structure", str(ROOT / "build" / "structure.py"))
    floor = ST.load_construction()["floor"]
    els = EL.elements(plan)
    rooms_by_level = {lv["index"]: lv["rooms"] for lv in plan["levels"]}
    # What the SEARCH charges: the elements the placer built, which it keys to the ground level
    # because a `block` tag is only read there.
    charged = GEO.spans_over_capacity(
        rooms_by_level, 40.0, 42.0, 10.0, plan["style"], floor,
        elements={0: [EL.bounds_of(e) for e in els]})
    assert marks == charged, (
        "the record publishes a different list from the one the placement was chosen by")


def test_the_fixture_really_exercises_the_multi_element_branch():
    """A guard that runs where the bug cannot occur is not a guard. `len(_els) > 1` is the
    condition the whole defect lives behind, and it is false on all sixteen shipped plans."""
    assert len(EL.elements(_two_element_plan())) > 1
    corpus = sorted((ROOT / "plans").glob("*.json")) + \
        sorted((ROOT / "plans" / "reference").glob("*.json"))
    tagged = [p.name for p in corpus
              if any(r.get("block") for lv in (json.loads(p.read_text()).get("levels") or [])
                     for r in (lv.get("rooms") or []))]
    assert tagged == [], (
        "a shipped plan now carries a block tag, so the hand-built fixture above is no longer "
        "the only way to reach this branch -- read WP-11.15's report before changing it")


# ------------------------------------------------- a level nobody can resolve is not one block

def test_a_level_whose_rooms_resolve_to_no_element_keeps_every_span():
    """REGRESSION, and it was introduced by this package's own first draft.

    The fix originally ended `... ] or None`. On a level where EVERY room fails `element_of`
    the empty list became `None`, `structure.wall_lines` took its `elements or [(0,0,W,H)]`
    default -- the MAIN BLOCK -- and the dependency's own 30 ft over-capacity span vanished
    from the record. Reachable at 0.51 ft of overshoot, because `elements.TOL` is 0.5 and
    `_absorb` is documented to grow a room past its element.

    The pre-fix code got this right by accident: it never produced an empty list at all. So
    this asserts the SPAN SURVIVES, not that some flag is set -- the flag is how the record
    says so, the span is what a reader loses.
    """
    def rec(overshoot):
        o = overshoot
        return {
            "id": "t", "style": "tidewater-georgian",
            "footprint": {"width_ft": 60.0, "depth_ft": 40.0, "bay_module_ft": 10.0, "blocks": [
                {"id": "main", "role": "main", "x_ft": 0.0, "y_ft": 0.0,
                 "width_ft": 60.0, "depth_ft": 40.0},
                {"id": "dep", "role": "dependency", "x_ft": -40.0, "y_ft": 0.0,
                 "width_ft": 30.0, "depth_ft": 30.0}]},
            "levels": [{"index": 0, "rooms": [
                _room("a", "drawing-room", 0.0 - o, 0.0, 60.0, 40.0),
                _room("b", "kitchen", -40.0 - o, 0.0, 30.0, 30.0)]}],
            "geometry_report": {"span_capacity": {"over_capacity": 0, "charge": 0.0}}}

    inside, outside = rec(0.50), rec(0.51)
    els = EL.elements(outside)
    assert all(EL.element_of(outside, r, els) is None
               for r in outside["levels"][0]["rooms"]), (
        "the fixture no longer reaches the case: some room still resolves to an element")

    m_in, m_out = _marks(inside), _marks(outside)
    if m_in is None or m_out is None:
        pytest.skip("COULD NOT EVALUATE: construction/floor-structure.json was unreadable")

    def dep_span(marks):
        return [m for m in marks if m["from_ft"] < -10.0]
    assert dep_span(m_in), "the fixture's own dependency span is missing at 0.50 ft"
    assert dep_span(m_out), (
        "the dependency's over-capacity span disappeared when its rooms could not be resolved "
        "-- a real defect reported clear, which is the exact failure this package is about")
    assert outside["geometry_report"]["span_capacity"].get(
        "element_membership_unresolved"), "the record must SAY the membership was unjudged"
    assert not inside["geometry_report"]["span_capacity"].get(
        "element_membership_unresolved"), "a resolvable level must not be marked unjudged"


def test_a_level_with_SOME_unresolvable_rooms_keeps_every_span_too():
    """THE CASE THE TEST ABOVE CANNOT SEE, and an audit found it in the fix for that one.

    The first fallback tested `if not here` -- every room on the level unresolvable. The
    realistic case is that SOME are: one stray room can be the last room of an element, the
    element then vanishes from the level, `elements_on_level` still returns a non-empty list,
    and the empty test never fires. Measured on this fixture before the fix: nudging the two
    wing rooms 1.0 ft west lost BOTH of the wing's over-capacity spans and set no flag.

    The main block's rooms stay resolvable here on purpose, so `here` is non-empty and only the
    per-room stray test can catch it.
    """
    plan = _two_element_plan()
    for r in plan["levels"][0]["rooms"]:
        if r.get("block") == "service":
            r["geometry"]["x_ft"] -= 1.0          # past elements.TOL of 0.5
    els = EL.elements(plan)
    on_level = EL.elements_on_level(plan, plan["levels"][0]["rooms"], els)
    assert [e["id"] for e in on_level] == ["main"], (
        "the fixture no longer reaches the case: the dependency must drop out of the level")
    assert on_level, "and the list must NOT be empty, or the other test would catch it"

    marks = _marks(plan)
    if marks is None:
        pytest.skip("COULD NOT EVALUATE: construction/floor-structure.json was unreadable")
    dep = [m for m in marks if m["level"] == 0 and m["from_ft"] < -10.0]
    assert dep, (
        "the dependency's own over-capacity spans vanished when only SOME of its rooms could "
        "not be resolved -- reported smaller than it is, in the flattering direction")
    assert plan["geometry_report"]["span_capacity"].get("element_membership_unresolved"), (
        "a partly-unresolvable level must say so, exactly as a wholly unresolvable one does")


# ------------------------------------------------------------------- one spelling of the rule

def test_no_module_rederives_element_membership_in_a_nested_loop():
    """`elements_on_level` is the one spelling; this looks for a sixth.

    IT READS THE AST, NOT THE TEXT. The first version of this guard matched the source
    substring `" is e "` -- a LOOP VARIABLE NAME with a trailing space -- and two audits broke
    it three ways at once: `structure.py`'s original wraps the line right after `is e`, so the
    pattern never matched the very copy it policed; renaming `e` to `_el` evaded it; and a
    fresh copy in another module passed all eight tests. Its docstring claimed to read the
    property. It did not.

    The property is the SHAPE: `element_of(...) is <element>` -- an IDENTITY comparison against
    an element -- nested inside two levels of iteration. That is someone asking "which elements
    does this collection of rooms stand in", which is this function's question, and it is what
    all four original copies were.

    IT IS NARROWED TO THE `is` COMPARISON ON PURPOSE, and the first version was not. Testing
    merely for a nested `element_of` call flagged `geometry.multi_element_disclosure`, which
    asks the DIFFERENT question "which rooms belong to each element" for the capacity report --
    it assigns the result and indexes by id rather than comparing identity. Convicting it would
    have been a guard generating a false accusation, which this repository has paid for before
    (`check_partis` check 10 is differential against a control for exactly that reason).

    ITS LIMIT, STATED: a hand-rolled containment test that never calls `element_of` is
    invisible here -- `render_plan._blocks_here` was exactly that, and is covered by the
    BEHAVIOURAL test below instead. Two guards, two failure modes, neither sufficient alone.
    """
    import ast
    offenders = []
    for py in sorted((ROOT / "build").glob("*.py")):
        if py.name == "elements.py":
            continue                      # the one spelling lives here
        tree = ast.parse(py.read_text())
        parents = {}
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                parents[child] = node
        LOOPS = (ast.For, ast.ListComp, ast.GeneratorExp, ast.SetComp, ast.DictComp)
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and
                    getattr(node.func, "attr", getattr(node.func, "id", None)) == "element_of"):
                continue
            depth, identity, cur = 0, False, parents.get(node)
            while cur is not None:
                if isinstance(cur, LOOPS):
                    depth += 1
                # `... is None` is the COULD-NOT-EVALUATE test and is legitimate anywhere --
                # it asks whether one room resolved, not which elements a level has. Only an
                # identity comparison against an ELEMENT is the duplicated shape. The guard
                # convicted this file's own `_stray` line before this clause existed, which is
                # the guard working and the rule being too broad by one case.
                if (isinstance(cur, ast.Compare)
                        and any(isinstance(o, (ast.Is, ast.IsNot)) for o in cur.ops)
                        and not all(isinstance(c, ast.Constant) and c.value is None
                                    for c in cur.comparators)):
                    identity = True
                cur = parents.get(cur)
            if depth >= 2 and identity:
                offenders.append(f"{py.name}:{node.lineno}")
    assert offenders == [], (
        f"{offenders} re-derive per-level element membership; call elements_on_level instead")


def test_the_renderer_draws_no_element_on_a_level_it_has_no_rooms_on():
    """THE BEHAVIOURAL GUARD, and the one that would have caught the live fifth spelling.

    `render_plan.render`'s `_blocks_here` was a hand-rolled containment test with its own 0.5
    literal, written because `blocks` is tuples rather than element dicts. The AST guard above
    cannot see it -- it never calls `element_of` -- and a substring check for
    `elements_on_level` in the file was satisfied by an unrelated line. So this asserts what a
    reader would SEE: the upper plate of a house with a single-storey ground-floor wing draws
    that wing's poche ring on the ground plate and NOT on the upper one.

    Reverting `_blocks_here` to `return blocks` makes plate 2 draw `data-block="1"` and this
    fails. That is WP-11.9's own defect -- "a 30 ft poche rectangle enclosing nothing", found
    by rendering a tagged record and looking at it.
    """
    import re
    import tempfile
    import os

    def _r(rid, t, x, y, w, d, block=None):
        r = _room(rid, t, x, y, w, d, block)
        r["geometry"]["area_sf"] = round(w * d, 1)
        return r

    plan = {
        "id": "two-el", "name": "Two Element", "style": "tidewater-georgian",
        "footprint": {
            "width_ft": 40.0, "depth_ft": 40.0, "bay_module_ft": 10.0,
            "wall": {"exterior_ft": 1.29, "interior_ft": 0.46, "partition_ft": 0.375},
            "blocks": [
                {"id": "main", "role": "main", "x_ft": 0.0, "y_ft": 0.0,
                 "width_ft": 40.0, "depth_ft": 40.0},
                {"id": "dep", "role": "dependency", "x_ft": -30.0, "y_ft": 5.0,
                 "width_ft": 20.0, "depth_ft": 20.0}]},
        "levels": [
            {"index": 0, "id": "ground", "rooms": [
                _r("a", "drawing-room", 0, 0, 40, 20),
                _r("b", "dining-room", 0, 20, 40, 20),
                _r("k", "kitchen", -30, 5, 20, 20, block="dep")]},
            {"index": 1, "id": "upper", "rooms": [
                _r("p", "primary-bedroom", 0, 0, 40, 20),
                _r("q", "bedroom", 0, 20, 40, 20)]}]}

    RP = modcache.load("render_plan", str(ROOT / "build" / "render_plan.py"))
    out = tempfile.mktemp(suffix=".svg")
    try:
        RP.render(json.loads(json.dumps(plan)), out)
        svg = pathlib.Path(out).read_text()
    finally:
        if os.path.exists(out):
            os.remove(out)

    plates = svg.split("data-plate-top")[1:]
    assert len(plates) == 2, f"expected two plates, got {len(plates)}"
    ground = sorted(set(re.findall(r'data-block="(\d+)"', plates[0])))
    upper = sorted(set(re.findall(r'data-block="(\d+)"', plates[1])))
    assert ground == ["0", "1"], f"the ground plate must draw both elements, drew {ground}"
    assert upper == ["0"], (
        f"the upper plate drew {upper}: the dependency has no rooms on level 1, so drawing its "
        "envelope there says the house has a storey it does not have")
