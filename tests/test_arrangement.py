"""The arrangement layer (WP-9.1).

Raised by Lucas against a rendered sheet: a 10 x 30 ft kitchen, a 27 x 7 ft breakfast room,
a portico off the axis of the passage it serves, a dining room landlocked in the middle of
the house. Every part well-formed, the whole meaningless.

EVERY TEST HERE IS PAIRED. A check that fires on a bad house and cannot stay quiet on a good
one is a check that convicts everything, and a check that stays quiet on a bad house is the
thing WP-8.6 found nine of. So each finding is asserted twice: it fires on a constructed
offender and it is SILENT on a constructed conformer that differs in exactly the one fact
the rule is about. Reverting any of the derivations to a constant breaks the offender half;
loosening any of them breaks the conformer half.
"""
import copy
import importlib.util
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _mod(name, path):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def pc():
    return _mod("_pc_arr", "build/plan_check.py")


@pytest.fixture(scope="module")
def arr():
    return _mod("_arr", "build/arrangement.py")


# ---------------------------------------------------------------- constructed houses
def _house(**over):
    """A small, schema-shaped centre-passage house. Every test mutates one fact of it."""
    p = {
        "id": "t", "name": "t", "style": "tidewater-georgian",
        "footprint": {"width_ft": 60.0, "depth_ft": 40.0},
        "levels": [{"level": 0, "floor_to_ceiling_ft": 9, "rooms": [
            {"id": "porch", "type": "entry-porch", "width_ft": 8, "length_ft": 20,
             "geometry": {"x_ft": 20.0, "y_ft": 0.0, "width_ft": 20.0, "depth_ft": 8.0, "area_sf": 160},
             "doors": [{"to": "exterior", "width_ft": 3.5, "wall": "S", "position_ft": 30.0},
                       {"to": "passage", "width_ft": 3.5, "wall": "N", "position_ft": 30.0}]},
            {"id": "passage", "type": "centre-passage", "width_ft": 10, "length_ft": 30,
             "geometry": {"x_ft": 25.0, "y_ft": 8.0, "width_ft": 10.0, "depth_ft": 30.0, "area_sf": 300},
             # A REAL centre passage reaches the boundary at BOTH ends -- styles/
             # tidewater-georgian.json c03 (hard) and groupings/centre-passage-core.json both
             # demand it, and openings/grammar.json[op-passage-axis] binds only where it holds.
             # Without the rear door this fixture has no through-axis and the axis rule
             # correctly declines to judge it.
             "doors": [{"to": "porch", "width_ft": 3.5, "wall": "S", "position_ft": 30.0},
                       {"to": "exterior", "width_ft": 3.5, "wall": "N", "position_ft": 30.0},
                       {"to": "dining", "width_ft": 3.0, "wall": "W", "position_ft": 20.0}]},
            {"id": "dining", "type": "dining-room", "width_ft": 16, "length_ft": 18,
             "geometry": {"x_ft": 0.0, "y_ft": 10.0, "width_ft": 16.0, "depth_ft": 18.0, "area_sf": 288},
             "doors": [{"to": "passage", "width_ft": 3.0, "wall": "E", "position_ft": 20.0}],
             "windows": [{"wall": "W", "count": 2, "width_ft": 3, "positions_ft": [14.0, 24.0]}]},
        ]}],
    }
    p.update(over)
    return p


def _rooms(plan):
    return {r["id"]: r for lv in plan["levels"] for r in lv["rooms"]}


def _drawn(pc, plan, needle):
    return [f for f in pc.check(plan)["findings"]
            if f["layer"] == "drawn" and needle in f["statement"]]


# ---------------------------------------------------------------- the drawn shape
def test_a_room_drawn_as_a_sliver_is_named_even_when_its_area_is_right(pc):
    """The defect that raised the package. The Tidewater brief declares a 16 x 20 kitchen;
    the placement drew it 10 x 30, held the area to within 6%, and the drawn-divergence
    check -- which compares AREA -- stayed quiet. The declared house and the drawn house
    were two different houses and only one of them was measured against the catalogue."""
    plan = _house()
    r = _rooms(plan)["dining"]
    r["geometry"] = {"x_ft": 0.0, "y_ft": 10.0, "width_ft": 9.6, "depth_ft": 30.0, "area_sf": 288}
    hits = _drawn(pc, plan, "to 1, against the")
    assert hits, "a dining room drawn 9.6 x 30 at its declared area produced no finding"
    assert any(f["severity"] == "serious" for f in hits)


def test_a_room_drawn_at_its_declared_shape_is_not_named(pc):
    """The other half: a room drawn at the shape it declares draws no proportion finding.

    THE SENTENCE HERE USED TO BE FALSE AND THE ASSERTION WAS ALWAYS RIGHT (corrected 3 Sep 2026).
    It read "16 x 18 is inside the dining room's own 1.15-1.8 band". 18/16 is 1.125, which was
    BELOW that band's floor -- so the docstring described a case the record convicted, while the
    test passed for a different reason: every proportion check in this corpus charges `ar > phi`,
    the ceiling alone, and none has ever read the floor. The docstring, not the code, was the
    thing that would have misled the next reader into thinking the floor was live.

    Lucas ruled every floor to 1.0 on 3 Sep, so 1.125 is now inside the band on the record too and
    the docstring and the assertion finally mean the same thing.
    `oq/the-proportion-band-forbids-the-square`."""
    assert not _drawn(pc, _house(), "to 1, against the")


def test_the_drawn_short_dimension_is_read_against_the_rooms_own_floor(pc):
    plan = _house()
    _rooms(plan)["dining"]["geometry"] = {"x_ft": 0.0, "y_ft": 10.0, "width_ft": 9.0,
                                          "depth_ft": 14.0, "area_sf": 126}
    assert _drawn(pc, plan, "in its short dimension, below the")


def test_a_room_at_its_floor_is_not_named(pc):
    plan = _house()
    _rooms(plan)["dining"]["geometry"] = {"x_ft": 0.0, "y_ft": 10.0, "width_ft": 13.0,
                                          "depth_ft": 16.0, "area_sf": 208}
    assert not _drawn(pc, plan, "in its short dimension, below the")


# ---------------------------------------------------------------- daylight from the placement
def test_a_room_reaching_no_exterior_wall_is_named(pc):
    """Lucas: "a dining room off the center passage, but it doesn't get any light because
    it's directly in the middle of the house." The daylight layer reads the DECLARED window
    list and compose.py writes a window for every wall the parti declares, so the record
    claimed windows on a room the placement put nowhere near a boundary."""
    plan = _house()
    d = _rooms(plan)["dining"]
    d["geometry"] = {"x_ft": 8.0, "y_ft": 10.0, "width_ft": 16.0, "depth_ft": 18.0, "area_sf": 288}
    d["windows"] = [{"wall": "W", "count": 2, "width_ft": 3,
                     "unplaced": {"reason": "the placement puts this room on no such boundary wall"}}]
    assert _drawn(pc, plan, "drawn in the middle of the house")


def test_a_room_on_the_perimeter_with_its_glass_placed_is_not_named(pc):
    assert not _drawn(pc, _house(), "drawn in the middle of the house")
    assert not _drawn(pc, _house(), "drawn with no window")


def test_the_landlocked_finding_never_reads_exterior_walls(pc):
    """`exterior_walls` are aspirations, not rectangle edges -- three Tidewater ground rooms
    each declare OPPOSITE walls, so each would have to span the full depth of the house.
    Promoting them to a constraint would convict houses of a wish. The finding must come
    from what the placement DID: windows the placer could not seat."""
    plan = _house()
    d = _rooms(plan)["dining"]
    d["exterior_walls"] = ["N", "S", "E", "W"]        # an impossible wish
    assert not _drawn(pc, plan, "drawn in the middle of the house"), (
        "the landlocked finding fired off exterior_walls rather than off the placement")


# ---------------------------------------------------------------- the entrance axis
def test_a_front_door_off_the_axis_of_its_passage_is_named(pc):
    plan = _house()
    _rooms(plan)["porch"]["doors"][0]["position_ft"] = 18.0
    assert _drawn(pc, plan, "off the axis of")


def test_two_openings_exactly_one_leaf_apart_do_not_overlap_and_are_named(pc):
    """The sheet that raised this package sits exactly here: a 3.5 ft front door and a 3.5 ft
    passage door with centres 3.5 ft apart. They touch at a point and overlap by nothing, so
    there is no straight walk between them. The first draft compared the offset against
    max(leaf) rather than the sum of the half-widths and let this through by a hair."""
    plan = _house()
    _rooms(plan)["porch"]["doors"][0]["position_ft"] = 33.5
    assert _drawn(pc, plan, "off the axis of")


def test_overlapping_openings_read_as_one_axis(pc):
    plan = _house()
    _rooms(plan)["porch"]["doors"][0]["position_ft"] = 31.0    # 1 ft off, still overlapping
    assert not _drawn(pc, plan, "off the axis of")
    assert not _drawn(pc, _house(), "off the axis of")


# ---------------------------------------------------------------- the stair setback
def _with_stair(y):
    """A shallow porch, as on the sheet that raised this package (3 ft deep), so the bottom
    riser CAN stand within 6 ft of the front door face. `y` is where the flight starts."""
    p = _house()
    porch = _rooms(p)["porch"]
    porch["geometry"] = {"x_ft": 20.0, "y_ft": 0.0, "width_ft": 20.0, "depth_ft": 3.0, "area_sf": 60}
    _rooms(p)["passage"]["geometry"] = {"x_ft": 25.0, "y_ft": 3.0, "width_ft": 10.0,
                                        "depth_ft": 35.0, "area_sf": 350}
    p["stair"] = {"room": "passage", "level": 0, "width_ft": 3.5,
                  "well": {"x_ft": 29.0, "y_ft": y, "width_ft": 7.0, "depth_ft": 8.0},
                  "flights": [{"x_ft": 29.0, "y_ft": y, "width_ft": 3.5,
                               "depth_ft": 8.0, "treads": 9, "direction": "N"}]}
    return p


def test_a_bottom_riser_at_the_front_door_is_named(pc):
    """openings/grammar.json has carried op-stair-setback since WP-6.2, with a number, a
    basis naming three records that agree, and a note saying why nothing evaluated it:
    "Nothing could evaluate it, because no plan record held a stair." A plan record has held
    a stair since WP-6.2 -- the note went stale in the package that wrote it."""
    assert _drawn(pc, _with_stair(3.5), "bottom riser")


def test_a_stair_set_back_down_its_hall_is_not_named(pc):
    assert not _drawn(pc, _with_stair(20.0), "bottom riser")


def test_the_setback_number_is_read_from_the_grammar_and_not_transcribed(pc):
    """The 6.0 ft lives in openings/grammar.json, in faults/stair-at-the-front-door.json and
    in a kit parameter. This reads the grammar, so a corpus edit is what changes the check."""
    g = json.load(open(os.path.join(ROOT, "openings/grammar.json")))
    rule = next(p for p in g["placement_rules"] if p["id"] == "op-stair-setback")
    assert rule["min_setback_ft"] == 6.0
    src = open(os.path.join(ROOT, "build/plan_check.py")).read()
    assert "op-stair-setback" in src, "the check no longer names the rule it implements"
    assert "min_setback_ft" in src, "the setback figure is transcribed rather than read"


# ---------------------------------------------------------------- the declared derivations
def test_the_route_model_is_editorial_and_its_citations_are_checked(arr):
    """An editorial call whose basis cannot be checked against the record it claims to read
    is a guess wearing a citation. check_openings.check_basis is CALLED, never copied."""
    assert arr.ROUTE_MODEL["kind"] == "editorial"
    assert len(arr.ROUTE_MODEL["note"]) >= 200
    CO = _mod("_co", "build/check_openings.py")

    class Rep:
        def __init__(self): self.errs = []
        def err(self, where, msg): self.errs.append(f"{where}: {msg}")

    rep = Rep()
    for rule in arr.ROUTE_MODEL["routes"]:
        assert len(rule.get("basis") or "") >= 40
        CO.check_basis(rep, rule, source="build/arrangement.py::ROUTE_MODEL")
    assert not rep.errs, rep.errs


def test_a_refused_measurement_never_reaches_the_fault_corpus(arr):
    """`NOT_DERIVABLE` is filtered where measurements are RETURNED, not at each call site:
    OQ 52's twelve invented constants came back into elevation.py through an m.update()
    after exactly this discipline had been applied per-site."""
    m = arr.declared(_house())
    for name in arr.NOT_DERIVABLE:
        assert name not in m, f"{name} is refused and still reached the measurements"
    assert arr.NOT_DERIVABLE, "the refusal list is empty; every name became derivable at once?"


def test_the_plant_room_zero_stays_refused(arr):
    """It was BUILT, and it convicted both reference plans on the first sweep -- including
    the careful Tidewater Georgian written to see whether the validator stays quiet on a
    good house. An absent plant room and an unmodelled one are indistinguishable in this
    schema, which is the WP-5.13 dormer test, and the zero is invented. To take this name
    off the list, give the schema a way to say "services considered, none enclosed"."""
    assert "dedicated_plant_room_area_sqft" in arr.NOT_DERIVABLE
    assert "dedicated_plant_room_area_sqft" not in arr.declared(_house())


def test_the_corpus_has_no_room_type_that_could_state_a_plant_room(arr):
    """The second and stronger reason the zero is refused. `rooms/` holds 60 records and not
    one of them is a mechanical room -- the nearest neighbours are cellar, workshop and
    laundry, all rooms a house has for other reasons. So the plan record cannot state that
    it HAS a plant room either, and the fault is unjudgeable in both directions until the
    catalogue gains the type. If this test starts failing, somebody added it, and the
    refusal should be revisited in the same commit."""
    import glob
    ids = {json.load(open(f))["id"]
           for f in sorted(glob.glob(os.path.join(ROOT, "rooms", "*.json")))}
    assert not ids & {"mechanical-room", "plant-room", "utility-room"}
    assert "dedicated_plant_room_area_sqft" in arr.NOT_DERIVABLE


def test_the_service_route_measurement_moves_with_the_house(arr):
    """A derivation that returns the same number whatever the house is a constant wearing a
    function's name."""
    direct = _house()
    direct["levels"][0]["rooms"] += [
        {"id": "kitchen", "type": "kitchen", "width_ft": 12, "length_ft": 14,
         "doors": [{"to": "dining", "width_ft": 2.8}]}]
    _rooms(direct)["dining"]["doors"].append({"to": "kitchen", "width_ft": 2.8})
    assert arr.declared(direct).get("service_routes_crossing_a_formal_room") == 0

    through = _house()
    through["levels"][0]["rooms"] += [
        {"id": "parlor", "type": "parlor", "width_ft": 16, "length_ft": 18,
         "doors": [{"to": "passage", "width_ft": 3.0}, {"to": "kitchen", "width_ft": 2.8}]},
        {"id": "kitchen", "type": "kitchen", "width_ft": 12, "length_ft": 14,
         "doors": [{"to": "parlor", "width_ft": 2.8}]}]
    _rooms(through)["passage"]["doors"].append({"to": "parlor", "width_ft": 3.0})
    assert arr.declared(through).get("service_routes_crossing_a_formal_room", 0) >= 1


# ---------------------------------------------------------------- grouping rule tests
def test_every_grouping_test_in_the_corpus_parses_or_is_reported_unjudged(arr):
    """26 of the 84 internal rules carry a test and 19 of those are hard. A rule this reader
    cannot parse must be REPORTED as unparsed, never silently treated as satisfied -- so the
    census here is a live measurement, and a rewording that breaks the parser shows up as a
    number that moved rather than as a rule that quietly stopped being checked."""
    import glob
    total = parsed = 0
    for path in sorted(glob.glob(os.path.join(ROOT, "groupings", "*.json"))):
        for ir in json.load(open(path)).get("internal_rules", []):
            if not ir.get("test"):
                continue
            total += 1
            if arr.parse_rule_test(ir["test"]):
                parsed += 1
    assert total >= 26, f"the corpus lost grouping tests: {total}"
    assert parsed == total, f"only {parsed} of {total} grouping tests parse"


def test_the_parser_handles_a_variable_threshold(arr):
    """`landing_depth_in at-least stair_width_in` compares two measurements. Folded into one
    expression rather than given a second code path."""
    p = arr.parse_rule_test("landing_depth_in at-least stair_width_in")
    assert p and p["direction"] == "at-least" and p["threshold"] == 0.0
    assert "stair_width_in" in p["expression"] and "landing_depth_in" in p["expression"]


def test_the_parser_refuses_a_sentence_it_does_not_understand(arr):
    assert arr.parse_rule_test("the stair rises in the passage") is None
    assert arr.parse_rule_test("") is None
    assert arr.parse_rule_test(None) is None


def test_a_hard_grouping_rule_with_a_test_is_evaluated_not_skipped(pc):
    """The loop read `if severity == "hard" and not ir.get("test")`, so a hard rule WITHOUT a
    machine test was handed to a human and a hard rule WITH one was passed over in silence
    by every layer of this checker."""
    plan = _house(groupings=["centre-passage-core"])
    findings = [f for f in pc.check(plan)["findings"] if f["layer"] == "grouping"]
    assert findings, "the grouping layer produced nothing at all"
    said = " ".join(f["statement"] for f in findings)
    assert "passage_width_ft" in said or "one fifth to one quarter" in said, (
        "centre-passage-core's own ratio rule was neither evaluated nor reported unjudged")


def test_an_unjudged_grouping_rule_is_never_reported_as_a_pass(pc):
    """Unjudged is not passed. A rule whose variables this house cannot supply says which
    name was missing."""
    plan = _house(groupings=["public-enfilade"])
    findings = [f for f in pc.check(plan)["findings"] if f["layer"] == "grouping"]
    unjudged = [f for f in findings if "could not evaluate" in f["statement"]]
    assert unjudged, "a rule with no supplied measurement produced no could-not-evaluate"
    assert all("Not a pass" in f["statement"] or "unjudged" in f["statement"]
               for f in unjudged)


def test_the_dead_passage_band_lookup_is_gone(pc):
    """It read `cp.get("rules")` where the record's key is `internal_rules`, so `band` was
    None on every plan this checker ever ran -- and it was then never read, so the dead
    lookup changed no verdict and nothing noticed for three phases."""
    src = open(os.path.join(ROOT, "build/plan_check.py")).read()
    # The comment above the fixed block QUOTES the mistake on purpose, so match the code
    # form rather than the substring -- a guard that trips on its own documentation is a
    # guard nobody can keep.
    assert 'for rule in (cp.get("rules")' not in src, "the dead lookup is back"
    assert 'band = None' not in src.split("GROUPING LAYER")[0], "the unread band survives"


def test_the_drawn_layer_is_still_the_only_layer_that_reads_placement(pc):
    """OQ 54's boundary. The declared derivations must work on a plan nobody has placed, and
    must produce the same numbers whether or not one exists -- otherwise a fault would be
    judged by the placement from inside a geometry-blind layer."""
    arr = _mod("_arr2", "build/arrangement.py")
    placed = _house()
    unplaced = _house()
    for r in _rooms(unplaced).values():
        r.pop("geometry", None)
    unplaced.pop("footprint", None)
    assert arr.declared(placed) == arr.declared(unplaced), (
        "arrangement.declared() changed its answer because a placement existed")


def test_roof_delegates_to_the_one_parser_rather_than_keeping_its_own(arr):
    """build/roof.py's `_parse_prose_between` read the same sentence form with its own regex.
    Two parsers for one form is the defect this codebase has been bitten by three times, so
    it delegates now -- and this pins that the delegation is LIVE rather than silently
    falling back, which is how it shipped for its first ten minutes: the delegating branch
    used `sys` in a module that never imported it, the bare `except Exception` swallowed the
    NameError, and the old regex answered every call. Both paths return the same tuple for
    the corpus's own wording, so no ordinary test could tell them apart. This one disables
    the local regex and requires the answer to still arrive."""
    roof = _mod("_roof_arr", "build/roof.py")
    sentence = "dependency_ridge_ft / main_ridge_ft between 0.6 and 0.8"
    assert roof._parse_prose_between(sentence) == (0.6, 0.8)
    saved = roof.re
    try:
        roof.re = type("X", (), {"search": staticmethod(lambda *a, **k: None)})()
        assert roof._parse_prose_between(sentence) == (0.6, 0.8), (
            "roof.py fell back to its own regex; the delegation is not live")
    finally:
        roof.re = saved


def test_the_style_states_its_own_passage_floor_and_the_catalogue_does_not_cover_it(pc):
    """THE FINDING THAT COST THIS PACKAGE A REGRESSION AND EARNED THE WHOLE ARBITER.

    rooms/centre-passage.json bands the width at [6, 14] and is right to: six to seven feet
    is a northern vernacular passage that circulates, and the record says so. A FORMAL
    centre-passage plan is a different rule, stated in three places nobody read together --
    the fault's at-least 8.0 (whose note says "8 ft for a formal centre-passage plan and 6 ft
    for a northern vernacular one"), the grouping's "8 to 14 ft", and the style's own kit,
    which for tidewater-georgian resolves passage_width_ft to [10, 14].

    Supplying `passage_clear_width_ft` armed `passage-that-is-a-corridor`, which is FATAL for
    a formal centre-passage style, on a composer that had been sizing this brief's passage at
    7.9 ft for three phases. It disqualified all three NATIVE partis and handed a Tidewater
    Georgian brief to a side-hall townhouse -- WP-4.5's deleted sentence walking back in, and
    caught only because two behavioural tests pinned the ranking.
    """
    plan = _house()
    rooms = _rooms(plan)
    rooms["passage"]["width_ft"] = 7.9
    rooms["passage"]["length_ft"] = 30
    hits = [f for f in pc.check(plan)["findings"]
            if f["layer"] == "style" and f.get("rule") == "circulation_parti"]
    assert hits, "a 7.9 ft passage in a style whose kit asks for 10-14 produced no finding"
    assert "7.9 ft wide" in hits[0]["statement"]

    rooms["passage"]["width_ft"] = 11.0
    assert not [f for f in pc.check(plan)["findings"]
                if f["layer"] == "style" and f.get("rule") == "circulation_parti"], (
        "an 11 ft passage is inside the style's own 10-14 band and must not be flagged")


def test_the_passage_floor_is_read_from_the_cascade_not_the_raw_kit(pc):
    """`oq/the-raw-kit-read`, which WP-8.4 and WP-8.6 each found a live instance of. The
    figure must come from the RESOLVED kit -- tidewater-georgian's own file carries
    min_passage_width, but the band this reads is delivered through circulation_parti's
    cascade, and a reader pointed at C["kits"][style] sees a different record."""
    src = open(os.path.join(ROOT, "build/plan_check.py")).read()
    block = src.split("THE PASSAGE FLOOR THIS STYLE STATES")[1][:2000]
    assert "_resolved_slots" not in block or 'C["kits"]' not in block
    assert 'kit.get("circulation_parti")' in block, (
        "the passage floor is no longer read off the resolved kit")


def test_the_passage_floor_the_style_states_has_a_move_that_clears_it(pc):
    """The fix that clears the finding. Without it the fatal is true, unactionable, and how a
    native diagram loses to a borrowed one.

    THIS TEST USED TO READ `build/compose.py` FOR A SOURCE STRING, AND THE MERGE WITH PR #19
    PROVED THAT WRONG TWICE OVER. That PR replaced `compose.repair`'s forty-line prose-parsing
    hill-climb with the move registry, so the branch this asserted no longer exists in that
    file -- the test went red on a fix that had been PORTED, not lost, which is the good half.
    The bad half is that a source-reading assertion would equally have PASSED on a branch
    nothing reaches. So this now tests the mechanism where it lives and, at the end, what it
    actually does to a plan.
    """
    import importlib.util as _il
    spec = _il.spec_from_file_location("moves_t", os.path.join(ROOT, "build/moves.py"))
    MV = _il.module_from_spec(spec); spec.loader.exec_module(MV)

    mid = "passage-to-the-styles-own-floor"
    entry = MV.move(mid)
    assert entry, f"{mid} is not in moves/registry.json; the style's passage floor has no answer"
    assert mid in MV.APPLY, f"{mid} is declared in the registry and has no apply function"
    assert entry["answers"]["kind"] == "passage-below-style-floor"

    # THE EMITTED ROW, NOT THE SOURCE (the proportion_engine RULE_KEYS lesson, WP-8.6).
    plan = _house()
    r = _rooms(plan)["passage"]
    r["width_ft"], r["length_ft"] = 7.9, 30
    emitted = [f for f in pc.check(plan)["findings"]
               if f["layer"] == "style" and f.get("rule") == "circulation_parti"]
    assert emitted, "the style layer emitted no passage-floor finding to repair against"
    f = emitted[0]
    assert f.get("kind") == entry["answers"]["kind"], (
        f"the finding's kind is {f.get('kind')!r} and the move answers "
        f"{entry['answers']['kind']!r} -- the two halves have drifted and the move is inert")
    # The figure the move consumes is STRUCTURED now, not parsed out of the sentence: PR #19's
    # evidence contract exists because reading `12.3` back out of prose for a room needing
    # 12.333 made a move silently never fire.
    assert f.get("need_ft") and f["need_ft"] >= 8.0, (
        f"the finding carries need_ft={f.get('need_ft')!r}, which would not clear the fault")

    # AND IT ACTUALLY WIDENS THE ROOM. A registry entry and a matching kind still prove nothing
    # about what happens to the record.
    before = min(r["width_ft"], r["length_ft"])
    res = MV.APPLY[mid](plan, f, None, {})
    assert res.get("changed"), f"the move refused: {res.get('refused')}"
    after = min(_rooms(plan)["passage"]["width_ft"], _rooms(plan)["passage"]["length_ft"])
    assert after >= f["need_ft"] > before, (
        f"the passage went {before} -> {after} against a floor of {f['need_ft']}")


def test_a_front_door_in_the_flank_of_a_through_passage_is_named(pc):
    """THE CASE THE OLD GUARD THREW AWAY (WP-9.4). The first version compared the threshold
    room's own two doors and gave up when they sat on perpendicular walls -- true, that a
    position on an N/S wall runs in x and one on an E/W wall runs in y, and false that
    nothing could therefore be said. Measured over the 21 partis the check fired ZERO times
    and SEVEN of those were this skip. A check that cannot fire reads as a check that passed.

    The corpus makes the widened rule narrow: a change of direction IS a legitimate threshold
    device (groupings/entry-sequence.json) and a side passage is a real exception
    (rooms/centre-passage.json on the Charleston single house), so the rule binds only where
    openings/grammar.json[op-passage-axis] says -- a passage that reaches the boundary at
    BOTH ends."""
    plan = _house()
    porch = _rooms(plan)["porch"]
    # enter from the EAST flank while the passage runs N-S
    porch["doors"][0] = {"to": "exterior", "width_ft": 3.5, "wall": "E", "position_ft": 4.0}
    hits = _drawn(pc, plan, "you arrive")
    assert hits, "a front door square to the passage's own through-axis produced no finding"
    assert "flank" in hits[0]["statement"]


def test_a_passage_with_no_through_axis_is_not_judged_and_says_so(pc):
    """The Charleston exception, and the honest half of the widening. A passage that does not
    reach the boundary at both ends has no axis to arrive on, so the rule does not bind --
    and the census must SAY it declined rather than report a silent zero."""
    plan = _house()
    p = _rooms(plan)["passage"]
    p["doors"] = [d for d in p["doors"] if d.get("to") != "exterior"]   # close the rear end
    porch = _rooms(plan)["porch"]
    porch["doors"][0] = {"to": "exterior", "width_ft": 3.5, "wall": "E", "position_ft": 4.0}
    res = pc.check(plan)
    assert not [f for f in res["findings"] if f["layer"] == "drawn" and "you arrive" in f["statement"]]
    census = res["drawn_summary"]["entrance_axis"]
    assert census["passage_has_no_through_axis"] >= 1, census
    assert census["found"] == 0


def test_the_entrance_axis_census_is_published_so_a_zero_is_never_a_pass(pc):
    """WP-8.6's finding in this package's own badge: the instrument reported 0 across 21
    partis and the 0 was a skip. `fault_not_applicable` exists for exactly this reason -- the
    question did not arise is a fourth state, not a pass -- and the drawn layer now carries
    the same disclosure for its own hardest check."""
    census = pc.check(_house())["drawn_summary"]["entrance_axis"]
    for k in ("no_threshold_room", "no_exterior_door", "passage_has_no_through_axis",
              "compared", "found"):
        assert k in census, f"the census lost {k}"
    assert census["compared"] >= 1, "the conformer house was not even compared"


def test_a_severed_entrance_sequence_is_named_not_skipped(pc):
    """THE ZERO WAS HIDING THIS, AND IT IS WORSE THAN A MISALIGNED AXIS (WP-9.4).

    Measured while widening the axis check: on `centre-passage-double-pile` composed against
    its own native style and placed, the porch's door INTO THE PASSAGE comes back unplaced --
    "the placement leaves these two rooms no shared wall". You enter the portico and there is
    no way into the passage at all. Both rooms stay reachable (the passage has its own rear
    door), so the drawn layer's reachability walk says nothing, and the axis census counted it
    as "nothing to compare" and reported a clean zero."""
    plan = _house()
    porch = _rooms(plan)["porch"]
    porch["doors"][1] = {"to": "passage", "width_ft": 3.5,
                         "unplaced": {"reason": "the placement leaves these two rooms no shared wall"}}
    res = pc.check(plan)
    hits = [f for f in res["findings"] if f["layer"] == "drawn" and "severed" in f["statement"]]
    assert hits, "a front door with no realised opening into the passage produced no finding"
    assert res["drawn_summary"]["entrance_axis"]["entry_door_unplaced"] >= 1


def test_a_placed_entry_door_is_not_called_severed(pc):
    res = pc.check(_house())
    assert not [f for f in res["findings"] if f["layer"] == "drawn" and "severed" in f["statement"]]
    assert res["drawn_summary"]["entrance_axis"]["entry_door_unplaced"] == 0
