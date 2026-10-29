"""WP-17.2: the composer poses a programme the type's own facts can hold (`compose.compose_to_the_type`).

Measured on Lucas's brief of 29 Oct 2026 (tidewater-georgian, 3,200 sf, four bedrooms, 3.5 baths):
every composed two-storey candidate was refused a drawing, and a read-only spike holding every fact,
band, size and door hard on CP-SAT drew the foursquare with every room in band once its upper gallery
corridor was sized from its own record -- the composer had sized it from the midpoint of a 150-3,000 sf
band, 13.5 x 87.6 ft, 57% of the upper programme. These hold what the pass does to the record.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

CO = modcache.load("compose", os.path.join(ROOT, "build", "compose.py"))
OP = modcache.load("openings", os.path.join(ROOT, "build", "openings.py"))

BRIEF = {"id": "lucas-29-oct", "style": "tidewater-georgian", "target_area_sf": 3200,
         "bedrooms": 4, "bathrooms": 3.5}


def _rooms(plan):
    return {r["id"]: (lv["index"], r) for lv in plan["levels"] for r in lv["rooms"]}


def _heated(plan):
    return sum(r["width_ft"] * r["length_ft"] for _l, r in _rooms(plan).values()
               if CO.C["rooms"].get(r["type"], {}).get("function_class") != "outdoor")


def test_an_open_band_corridor_is_sized_from_what_it_is_for():
    plan, log, _p = CO.instantiate("foursquare-quadrant", BRIEF)
    _l, hall = _rooms(plan)["upperhall"]
    area, wb, lb, _pr = CO._bands(hall["type"])
    assert area[1] >= CO.OPEN_BAND_FACTOR * area[0], "the premise: the corridor's band is open"
    assert hall["width_ft"] == wb[0], "its record's working width, the width band's floor"
    run = sum(OP.required_wall_ft(float(d.get("width_ft") or 3.0)) for d in hall.get("doors") or []) / 2
    assert hall["length_ft"] >= run - 0.01 and hall["length_ft"] * hall["width_ft"] >= area[0] - 0.01
    assert hall["width_ft"] * hall["length_ft"] < 0.2 * _heated(plan), (
        "a corridor is not a fifth of the house -- it was 57% of the upper programme")
    assert any(l.startswith("Sized Upper Hall from what it is for") for l in log)


def test_a_closed_band_room_is_not_resized_as_circulation():
    plan, _log, _p = CO.instantiate("centre-passage-double-pile", BRIEF)
    _l, passage = _rooms(plan)["passage"]
    area, _wb, _lb, _pr = CO._bands(passage["type"])
    assert area[1] < CO.OPEN_BAND_FACTOR * area[0], "the premise: the passage's band is closed"
    assert passage["width_ft"] > 4.0, "a centre passage keeps its own width"


def test_a_room_that_stands_over_another_takes_its_plan_inside_its_own_bands():
    seen = 0
    for pid in ("foursquare-quadrant", "centre-passage-double-pile", "side-hall-townhouse"):
        plan, log, _p = CO.instantiate(pid, BRIEF)
        rooms = _rooms(plan)
        for rid, (lvl, r) in rooms.items():
            so = r.get("stacks_over")
            if not so or so not in rooms or rooms[so][0] != lvl - 1:
                continue
            t = rooms[so][1]
            assert (r["width_ft"], r["length_ft"]) == CO._clamp_dims(t["width_ft"], t["length_ft"], r["type"]), (
                pid, rid, so)
            seen += 1
        assert any(l.startswith("JUDGMENT (editorial):") and "which it stands over" in l for l in log), pid
    assert seen >= 6, f"the premise: the three diagrams declare structural stacks ({seen})"


def test_the_area_the_corridor_gave_back_is_grown_back_toward_the_brief():
    for pid in ("foursquare-quadrant", "side-hall-townhouse"):
        plan, log, _p = CO.instantiate(pid, BRIEF)
        grew = [l for l in log if l.startswith("Grew the rooms the type pass did not size")]
        assert grew, f"the premise: the pass left {pid} short of the brief"
        tol = BRIEF.get("area_tolerance", 0.12)
        assert abs(_heated(plan) - BRIEF["target_area_sf"]) <= tol * BRIEF["target_area_sf"], (pid, _heated(plan))
        for _lid, (_l, r) in _rooms(plan).items():
            area, *_ = CO._bands(r["type"])
            if area:
                assert r["width_ft"] * r["length_ft"] <= area[1] + 0.5, (pid, r["id"])


def test_every_composed_plan_names_its_parti():
    named = 0
    for pid in CO.PARTIS:
        try:
            plan, _log, _p = CO.instantiate(pid, BRIEF)
        except Exception:
            continue                      # a diagram this brief cannot seed is not this test's
        assert plan["parti"] == pid
        named += 1
    assert named >= len(CO.PARTIS) - 2, f"the premise: the catalogue seeds on this brief ({named})"


def test_a_bathroom_shortfall_is_said_and_nothing_is_invented():
    plan, log, _p = CO.instantiate("foursquare-quadrant", BRIEF)
    n_baths = sum(1 for _l, r in _rooms(plan).values() if r["type"] in ("bathroom", "primary-bathroom"))
    said = [l for l in log if "asks for 3.5 bathrooms" in l]
    assert said and "Not added" in said[0]
    plan2, log2, _p = CO.instantiate("foursquare-quadrant", {**BRIEF, "bathrooms": 1})
    assert not [l for l in log2 if "bathrooms and this diagram" in l]
    assert n_baths == sum(1 for _l, r in _rooms(plan2).values() if r["type"] in ("bathroom", "primary-bathroom"))


def test_growing_back_never_takes_a_room_past_its_own_area_band():
    """Driven at a brief larger than the diagram grows into, where the growth meets the bands: on
    Lucas's 3,200 sf no grown room reaches its ceiling, so that brief cannot see the clamp."""
    big = {**BRIEF, "target_area_sf": 6400}
    plan, log, _p = CO.instantiate("foursquare-quadrant", big)
    assert any(l.startswith("Grew the rooms the type pass did not size") for l in log), "the premise"
    at_ceiling = 0
    for _lid, (_l, r) in _rooms(plan).items():
        area, *_ = CO._bands(r["type"])
        if area:
            a = r["width_ft"] * r["length_ft"]
            assert a <= area[1] + 0.5, (r["id"], round(a), area)
            at_ceiling += a >= area[1] - 1.0
    assert at_ceiling, "the premise: some room grew to its band's ceiling"


def test_the_entrance_front_is_read_off_the_diagrams_own_entry():
    """A porch declared S, E and W in front of a passage declared N and S is entered on S. Without
    a stated front every entrance rule downstream -- the search's anchor, the entrance score, the
    hard entry-off-its-front fact -- had nothing to read on a composed plan."""
    plan, log, _p = CO.instantiate("centre-passage-double-pile", BRIEF)
    assert plan["context"]["entrance_faces"] == "S"
    said = [l for l in log if l.startswith("JUDGMENT: the house is entered on its S front")]
    assert said and "into Centre Passage (S/N)" in said[0], said


def test_a_brief_that_states_its_front_keeps_it():
    plan, log, _p = CO.instantiate("centre-passage-double-pile", {**BRIEF, "context": {"entrance_faces": "N"}})
    assert plan["context"]["entrance_faces"] == "N"
    assert not [l for l in log if "entered on its" in l]


def test_a_diagram_whose_entry_does_not_settle_the_front_states_none_and_says_so():
    plan, log, _p = CO.instantiate("bungalow-open-linear", BRIEF)
    assert not plan["context"].get("entrance_faces")
    assert [l for l in log if l.startswith("DISCLOSURE: the diagram's entry does not settle")]


def test_a_composed_plan_validates_against_the_plan_schema():
    """The entrance front was first written as a LIST and the schema states one compass point;
    `geometry.entrance_walls` then raised on every composed plan. Nothing validated a composed
    record before it was placed."""
    import json
    import jsonschema
    schema = json.load(open(os.path.join(ROOT, "schema", "plan.schema.json"), encoding="utf-8"))
    for pid in ("foursquare-quadrant", "centre-passage-double-pile", "side-hall-townhouse", "bungalow-open-linear"):
        plan, _log, _p = CO.instantiate(pid, BRIEF)
        jsonschema.validate(plan, schema)
