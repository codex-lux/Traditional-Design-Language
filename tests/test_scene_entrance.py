"""The entrance and the porch (WP-12.7).

THE TWO ASSERTIONS THIS FILE EXISTS FOR ARE BOTH ABOUT SOMETHING NOT BEING DRAWN.

A pilaster is not a member of this doorcase, and that is MEASURED rather than assumed: the
composition width reconciles to the door plus two casings plus two sidelights to the
thousandth of an inch, and substituting the stated `pilaster_width_in` misses it by four and a
half inches. A guard that merely asserted "no pilaster solid" would pass with the whole
function deleted, so the arithmetic is asserted too.

And the porch's columns are refused by `build/threshold.py` and NOT by this layer. The Phase 12
PRD asks WP-12.7 to place them "where a bound pack states an intercolumniation ... else refuse
and name the missing rule" -- and that refusal has been in the record since WP-11.4, on both
shipped plans, in the record's own words. Following the brief literally would have written a
second reader of one rule, which is this repository's most-repeated defect. So there is a
source guard here as well as a behavioural one.
"""
import ast
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))

import importlib.util  # noqa: E402


def _mod(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "build", name + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


SC = _mod("scene")


def _build(pid):
    G, ST, RF, EL = _mod("geometry"), _mod("structure"), _mod("roof"), _mod("elevation")
    plan = json.load(open(os.path.join(ROOT, "plans", pid + ".json")))
    sol = G.solve(json.loads(json.dumps(plan)), engine="heuristic")
    sec = ST.build_section(sol, None, geometry_result=sol)
    rf = RF.build_roof(sol, None, section=sec)
    ev = EL.build_elevation(sol, None, section=sec, roof=rf)
    return sol, sec, rf, (None if "error" in ev else ev)


@pytest.fixture(scope="module")
def both():
    out = {}
    for pid in ("tidewater-georgian-careful", "spec-builder-colonial"):
        sol, sec, rf, ev = _build(pid)
        out[pid] = (SC.build_scene(sol, sec, rf, ev), sol, sec, ev)
    return out


def _cls(scene, name):
    return [s for s in scene["solids"] if s["class"] == name]


# ------------------------------------------------------------------ the composition

def test_the_composition_is_the_door_two_casings_and_two_sidelights(both):
    """AND A PILASTER IS NOT IN IT, WHICH IS THE HALF THAT DECIDES WHAT IS DRAWN."""
    for pid, (scene, _sol, _sec, ev) in both.items():
        e = ev["entrance"]
        d, c, s = e["door_leaf_width_in"], e["casing_width_in"], e["sidelight_width_in"]
        stated = e["entrance_composition_width_in"]
        assert abs((d + 2 * c + 2 * s) - stated) < 0.01, (
            f"{pid}: door {d} + 2x casing {c} + 2x sidelight {s} = {d + 2*c + 2*s} against a "
            f"stated composition width of {stated}")
        # the discriminator: the same sum with pilasters is a DIFFERENT number, so the
        # reconciliation above is evidence and not an identity that holds either way
        with_pil = d + 2 * e["pilaster_width_in"] + 2 * s
        assert abs(with_pil - stated) > 1.0, (
            f"{pid}: a pilaster and a casing are the same width here ({with_pil} vs {stated}), "
            "so this test can no longer tell which member the composition holds")
        assert not _cls(scene, "pilaster"), (
            f"{pid}: a pilaster is drawn, and the composition's own arithmetic excludes one")


def test_the_surround_is_the_casing_band_the_sheet_draws(both):
    for pid, (scene, _sol, _sec, ev) in both.items():
        e = ev["entrance"]
        band = [s for s in _cls(scene, "surround") if s["id"].endswith("-surround")]
        assert len(band) == 1, f"{pid}: {len(band)} surround bands"
        xs = [v[0] if band[0]["geometry"]["vertices"][0][1] != 0 else v[0]
              for v in band[0]["geometry"]["vertices"]]
        want = (e["door_leaf_width_in"] + 2 * e["casing_width_in"]) / 12.0
        assert abs((max(xs) - min(xs)) - want) < 0.01, (
            f"{pid}: the surround is {max(xs) - min(xs):.3f} ft wide against a door plus two "
            f"casings of {want:.3f}")


def test_the_surrounds_relief_is_refused_and_names_why(both):
    for pid, (scene, *_rest) in both.items():
        r = [n for n in scene["not_modelled"] if n["source"] == "elevation.entrance.casing_width_in"]
        assert len(r) == 1, f"{pid}: {len(r)} surround-relief refusals"
        assert "second reader" in r[0]["why"]


def test_the_transom_is_stated_and_refused_and_the_premise_is_asserted(both):
    """The record dimensions a rectangular transom and `render_elevation` draws none. Drawing one
    here would make the model and the plate two different doorcases."""
    for pid, (scene, _sol, _sec, ev) in both.items():
        assert ev["entrance"].get("transom_height_in"), (
            f"{pid}: the record no longer states a transom, so this refusal is about nothing")
        r = [n for n in scene["not_modelled"]
             if n["source"] == "elevation.entrance.transom_height_in"]
        assert len(r) == 1, f"{pid}: {len(r)} transom refusals"
    src = open(os.path.join(ROOT, "build", "render_elevation.py")).read()
    lo = src.index("def _entrance(")
    assert "transom" not in src[lo:src.index("\ndef ", lo + 1)], (
        "render_elevation._entrance draws a transom now, so the scene's refusal has become the "
        "disagreement it was written to avoid -- draw it here too")


def test_the_entablature_members_sum_to_their_own_band_and_a_flush_member_is_a_plane(both):
    for pid, (scene, _sol, _sec, ev) in both.items():
        e = ev["entrance"]
        mem = _cls(scene, "entablature")
        assert len(mem) == len(e["entablature_members"]), f"{pid}: {len(mem)} members"
        assert abs(sum(m["height_in"] for m in e["entablature_members"])
                   - e["entablature_height_in"]) < 0.01
        flush = [m for m in e["entablature_members"] if not m.get("projection_in")]
        assert flush, f"{pid}: no member is flush, so the plane branch is not exercised"
        drawn_flat = [s for s in mem if s["geometry"]["type"] == "plane"]
        assert len(drawn_flat) == len(flush), (
            f"{pid}: {len(drawn_flat)} planes against {len(flush)} members of zero projection -- "
            "a member with no relief must not be an extrusion of no thickness")


# ------------------------------------------------------------------ the porch

def test_the_porch_is_inside_the_footprint_so_there_is_no_deck_and_no_porch_roof(both):
    """THE PRD SAYS "deck and roof already in 12.1" AND THERE IS NOTHING TO DRAW.

    Both shipped plans place their `entry-porch` inside the block, so its floor is the ground
    slab and its roof is the main roof. A deck there would be a second floor structure inside
    the house.
    """
    for pid, (scene, sol, sec, _ev) in both.items():
        fp = sec["footprint"]
        porches = [r for lv in sol["levels"] for r in lv["rooms"]
                   if r.get("type") == "entry-porch" and r.get("geometry")]
        assert porches, f"{pid}: no placed entry-porch, so this asserts nothing"
        for r in porches:
            g = r["geometry"]
            assert (g["x_ft"] >= -0.01 and g["y_ft"] >= -0.01
                    and g["x_ft"] + g["width_ft"] <= fp["width_ft"] + 0.01
                    and g["y_ft"] + g["depth_ft"] <= fp["depth_ft"] + 0.01), (
                f"{pid}: the porch has moved OUTSIDE the footprint, so it now has a floor and a "
                "roof of its own and this layer draws neither")
        assert not _cls(scene, "porch-roof"), f"{pid}: a porch roof is drawn"
        decks = _cls(scene, "deck")
        assert all(s["id"].startswith("stoop-") for s in decks), (
            f"{pid}: a `deck` solid that is not a stoop riser: "
            f"{[s['id'] for s in decks if not s['id'].startswith('stoop-')][:3]}")


def test_the_flights_treads_reconcile_and_the_top_riser_lands_on_the_platform(both):
    scene, sol, _sec, _ev = both["tidewater-georgian-careful"]
    steps = (sol.get("threshold") or {}).get("steps") or []
    assert steps, "the Tidewater record places no stoop, so this test is about nothing"
    st = steps[0]
    rc, td = st["riser_count"], st["tread_depth_in"]
    assert abs((rc - 1) * td / 12.0 - st["flight"]["depth_ft"]) < 0.01, (
        f"{rc - 1} treads of {td} in against a flight {st['flight']['depth_ft']} ft deep -- the "
        "top riser no longer lands on the platform")
    risers = [s for s in _cls(scene, "deck") if s["id"].startswith("stoop-")]
    assert len(risers) == rc - 1, f"{len(risers)} risers drawn against {rc} stated"


def test_the_flight_does_not_reach_the_floor_and_the_shortfall_is_reported(both):
    """`riser_count x riser_height_in` is 1.719 ft against a `grade_to_floor_ft` of 2.0. That is
    `oq/a-child-band-replaces-an-ancestor-derivation` reaching its SECOND consumer -- WP-12.6's
    sill was the first -- and a fourth riser invented to close it would be a measurement nobody
    wrote down."""
    scene, sol, sec, _ev = both["tidewater-georgian-careful"]
    st = ((sol.get("threshold") or {}).get("steps") or [])[0]
    g0 = next(s for s in sec["storeys"] if s["index"] == 0)
    rise = st["riser_count"] * st["riser_height_in"] / 12.0
    assert abs(rise - g0["grade_to_floor_ft"]) > 0.01, (
        "the flight reaches its floor now, so this refusal is about nothing -- re-derive it")
    r = [n for n in scene["not_modelled"]
         if n["source"].endswith("riser_count") and "does not reach the floor" in n["why"]]
    assert len(r) == 1, f"{len(r)} shortfall refusals"


# ------------------------------------------------------------------ the two doors

def test_the_two_records_of_the_front_door_disagree_and_the_scene_says_so(both):
    """FOUND BY DRAWING THE STOOP AND THE DOORCASE IN ONE PICTURE AND LOOKING AT IT.

    `elevation._face_bays` writes `kinds[mid] = "door"` — the entrance goes in the MIDDLE BAY of
    the front, always — while `openings.place` seats the real door where the porch room's own
    wall allows. Measured: 5.42 ft apart on the Tidewater plan and **21.33 ft** on the spec
    Colonial, where the drawn front door stands over the GARAGE.

    Each record is right on its own and no surface drew both until the scene. That is WP-12.1's
    own lesson repeated — *"invisible for as long as no surface drew a roof and a room in one
    picture"* — and this time the picture was the approach view, where the stoop stands five and
    a half feet east of the door it serves.

    NOTHING IS MOVED. Correcting the elevation moves sixteen shipped plates and needs a ruling:
    `oq/the-elevation-draws-the-front-door-where-the-composition-wants-it`.
    """
    AX = _mod("axis")
    EL = _mod("elevation")
    for pid, (scene, sol, _sec, ev) in both.items():
        f = ev["entrance_face"]
        door = next(r for r in EL.opening_rects(ev, f)["rects"] if r["kind"] == "door")
        drawn = (door["x0_in"] + door["x1_in"]) / 24.0
        placed = AX.door_bay(sol)["position_ft"]
        assert round(drawn, 1) != round(placed, 1), (
            f"{pid}: the two records of the front door agree now ({drawn:.2f} against "
            f"{placed:.2f}) — the disclosure below is about nothing, so re-derive it rather "
            "than deleting it")
        said = [n for n in scene["not_modelled"] if "axis.door_bay" in n["source"]]
        assert len(said) == 1, f"{pid}: {len(said)} entrance-agreement disclosures"
        # the disclosure states BOTH figures, because either alone reads as a defect in the
        # other record rather than as a disagreement between two
        assert f"{drawn:.2f}" in said[0]["why"] and f"{placed:.2f}" in said[0]["why"], (
            f"{pid}: the disclosure does not name both positions: {said[0]['why'][:120]}")


def test_the_checker_convicts_the_placement_for_what_the_drawing_corrects(both):
    """The sharpest half: `plan_check` emits `drawn-door-off-the-centre-bay` against the PLACED
    door, and the elevation plate a reader turns to draws that door in the middle bay after all.
    The plate is evidence against the finding beside it."""
    PC = _mod("plan_check")
    scene, sol, _sec, ev = both["tidewater-georgian-careful"]
    findings = PC.check(sol)["findings"]
    off = [f for f in findings if f.get("kind") == "drawn-door-off-the-centre-bay"]
    assert len(off) == 1, (
        "the checker no longer convicts this placement of an off-centre door, so the "
        "contradiction this test names has changed — re-derive it")
    EL = _mod("elevation")
    door = next(r for r in EL.opening_rects(ev, ev["entrance_face"])["rects"]
                if r["kind"] == "door")
    bays = sol["footprint"]["bays"]
    span = (door["x0_in"] + door["x1_in"]) / 24.0
    module = (sol["footprint"]["width_ft"] + 2 * 0) / bays
    drawn_bay = int(span // module)
    assert drawn_bay == bays // 2, (
        f"the elevation draws the door in bay {drawn_bay} of {bays}, not the middle one — "
        "the drawing has stopped composing the front and this contradiction is over")


# ------------------------------------------------------------------ one reader of R4

def test_the_portico_refusal_is_the_records_own_and_is_not_re_derived_here(both):
    """`build/threshold.py` has refused the portico's columns since WP-11.4, by name, on both
    plans. This layer republishes that reason and derives nothing."""
    for pid, (scene, sol, _sec, _ev) in both.items():
        unplaced = (sol.get("threshold") or {}).get("unplaced") or []
        col = [u for u in unplaced if "portico" in (u.get("what") or "")]
        assert len(col) == 1, f"{pid}: the record no longer refuses the portico's columns"
        published = [n for n in scene["not_modelled"]
                     if n["source"].startswith("plan.threshold.unplaced[")]
        assert len(published) == len(unplaced), (
            f"{pid}: {len(published)} of {len(unplaced)} threshold refusals reach the scene")
        assert any(n["why"] == col[0]["reason"] for n in published), (
            f"{pid}: the portico refusal is republished with a reason of this layer's own "
            "rather than the record's")
    # AND THE SOURCE GUARD: nothing about a portico is decided in this file.
    src = open(os.path.join(ROOT, "build", "scene.py")).read()
    body = src[src.index("def _porch("):]
    body = body[body.index('"""', body.index('"""') + 3):]      # past the docstring
    for word in ("portico_bays", "intercolumniation", "porch_support", "porch_type"):
        assert word not in body, (
            f"build/scene.py::_porch reads {word!r} -- the portico question is answered in "
            "build/threshold.py and a second reader of it is the defect this package avoided")


def test_the_frame_reaches_the_stoop(both):
    """`bounds` is the union of what is drawn now, rather than the section's footprint plus a
    list of hand-written exceptions. The stoop stands three and a half feet clear of the house."""
    scene, sol, _sec, _ev = both["tidewater-georgian-careful"]
    st = ((sol.get("threshold") or {}).get("steps") or [])[0]
    y = st["flight"]["y_ft"]
    assert y < -1.0, "the stoop is no longer outside the block, so this asserts nothing"
    assert scene["bounds"]["min"][1] <= y + 0.01, (
        f"bounds reaches only y={scene['bounds']['min'][1]} and the stoop starts at {y}")


def test_a_flight_on_any_face_but_the_south_is_refused_by_name():
    """DRIVEN, and the premise is asserted. The step geometry lays treads along −y from the
    flight's outer edge, which is a south face's arithmetic; no shipped record places a stoop
    anywhere else, so the branch is unreachable from the corpus and a guard over the shipped
    plans would pass with the refusal deleted (WP-8.11's rule).

    KEPT rather than generalised: a flight on an east face is a real thing this layer cannot
    lay, and a named refusal is what the reader needs. Generalising it would add three
    arithmetics the corpus cannot exercise.
    """
    states = SC._States()
    plan = {"threshold": {"steps": [{"room": "porch", "wall": "E", "riser_count": 3,
                                     "riser_height_in": 8.0, "tread_depth_in": 11.0,
                                     "flight": {"x_ft": 40.0, "y_ft": 10.0,
                                                "width_ft": 4.0, "depth_ft": 1.833}}]}}
    section = {"storeys": [{"index": 0, "grade_to_floor_ft": 2.0}]}
    out = SC._porch(plan, section, states)
    assert out == [], "a flight was drawn on an east face"
    named = [n for n in states.not_modelled if n["source"].endswith(".wall")]
    assert len(named) == 1 and "E" in named[0]["why"], (
        f"the refusal does not name the face: {[n['why'][:60] for n in states.not_modelled]}")


def test_no_shipped_record_places_a_flight_off_the_south_face(both):
    """The premise of the test above. The day a plan grows an east stoop the suite says so
    rather than that fixture quietly becoming the only case."""
    walls = set()
    for _pid, (_scene, sol, _sec, _ev) in both.items():
        for st in ((sol.get("threshold") or {}).get("steps") or []):
            walls.add(st.get("wall"))
    assert walls <= {"S"}, (
        f"a shipped record now places a flight on {sorted(walls - {'S'})} -- the refusal above "
        "is reachable from the corpus and this layer should lay that flight instead")


def test_the_extent_helper_refuses_a_primitive_it_does_not_understand():
    """A frame computed by silently skipping what it cannot read is a frame that is too small
    and says so nowhere."""
    with pytest.raises(ValueError):
        SC._extent({"type": "lathe", "profile": []})
    with pytest.raises(ValueError):
        SC._extent({"type": "extrude", "plane": "xy", "at": 0, "thickness": 1, "outline": [[0, 0]]})
