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


def _t_ext(section):
    """The exterior wall in feet, off the section the scene was built against."""
    return ((section.get("wall") or {}).get("exterior_in") or 0) / 12.0


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
    """RE-CUT AT WP-13.3: the door the surround dresses is the PLAN's placed front door at
    the plan's own width, so the band is that leaf plus two casings -- and on the spec
    Colonial that is NOT the composition's leaf: the plan places a 42.0 in door where
    `entrance_composition` derives a 34.447 in leaf, 7.553 in apart, which the rect states as
    `leaf_width_difference_in` rather than resolving. On the Tidewater plan the two agree to
    0.099 in. The first version compared the band against the composition's leaf, which was
    right for as long as the elevation drew the composition's door."""
    EL = _mod("elevation")
    for pid, (scene, _sol, _sec, ev) in both.items():
        e = ev["entrance"]
        door = next(r for r in EL.opening_rects(ev, ev["entrance_face"])["rects"]
                    if r["kind"] == "door" and r["entrance"])
        band = [s for s in _cls(scene, "surround") if s["id"].endswith("-surround")]
        assert len(band) == 1, f"{pid}: {len(band)} surround bands"
        xs = [v[0] if band[0]["geometry"]["vertices"][0][1] != 0 else v[0]
              for v in band[0]["geometry"]["vertices"]]
        want = (door["width_in"] + 2 * e["casing_width_in"]) / 12.0
        assert abs((max(xs) - min(xs)) - want) < 0.01, (
            f"{pid}: the surround is {max(xs) - min(xs):.3f} ft wide against the placed door "
            f"plus two casings of {want:.3f}")
        assert door["composition_leaf_width_in"] == e["door_leaf_width_in"]
        assert abs(door["leaf_width_difference_in"]
                   - (door["width_in"] - e["door_leaf_width_in"])) < 1e-9
    spec = next(r for r in EL.opening_rects(both["spec-builder-colonial"][3], "N")["rects"]
                if r["kind"] == "door" and r["entrance"])
    assert abs(spec["leaf_width_difference_in"]) > 7.0, (
        "the premise: on the spec Colonial the plan's door and the composition's leaf disagree")


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

def test_the_two_records_of_the_front_door_agree_and_the_scene_files_nothing(both):
    """FOUND BY DRAWING THE STOOP AND THE DOORCASE IN ONE PICTURE AND LOOKING AT IT -- and
    CLOSED at WP-13.3, which is why this test's name and its assertion flipped.

    Until WP-13.3 `elevation._face_bays` wrote `kinds[mid] = "door"` -- the entrance in the
    MIDDLE BAY of the front, always -- while `openings.place` seated the real door where the
    porch room's own wall allows: measured 6.71 ft apart on the Tidewater plan and 22.00 ft
    on the spec Colonial, where the drawn front door stood over the GARAGE
    (`oq/the-elevation-draws-the-front-door-where-the-composition-wants-it`). Lucas's ruling
    of 15 Sep 2026 that the elevation draws the openings the plan PLACED answers it: the
    doorcase stands over the placed door, the stoop under the same door, and
    `_entrance_agreement` -- which files a disclosure only where the two records differ by a
    tenth of a foot -- files nothing. The frame check is kept: the elevation's u and the
    model's x still differ by exactly one exterior wall and nothing else.
    """
    AX = _mod("axis")
    EL = _mod("elevation")
    for pid, (scene, sol, _sec, ev) in both.items():
        f = ev["entrance_face"]
        door = next(r for r in EL.opening_rects(ev, f)["rects"]
                    if r["kind"] == "door" and r["entrance"])
        drawn_u = (door["x0_in"] + door["x1_in"]) / 24.0
        sur = next(s for s in scene["solids"]
                   if s["class"] == "surround" and s["id"].endswith("-surround"))
        along = 0 if f in ("S", "N") else 1
        xs = [v[along] for v in sur["geometry"]["vertices"]]
        drawn = (min(xs) + max(xs)) / 2
        placed = AX.door_bay(sol)["position_ft"]
        # THE FRAME CHECK READS THE ELEVATION'S OWN DATUM (`elevation.face_u_ft`) rather than
        # restating `drawn_u - drawn == t`. On every face today that IS one wall thickness --
        # `FACE_MIRRORED` states the N and W faces read with the plan's axis, as the scene's
        # `_face_extrude` lays them out -- and the day the mirror is ruled the check follows the
        # switch instead of convicting the scene by one width of the front.
        fp = _sec["footprint"]
        expect_u = EL.face_u_ft(f, drawn, fp["clear_width_ft"], fp["clear_depth_ft"], _t_ext(_sec))
        assert abs(drawn_u - expect_u) < 0.01, (
            f"{pid}: the elevation's u {drawn_u:.3f} is not the model x {drawn:.3f} in the "
            f"{f} face's own datum ({expect_u:.3f})")
        assert round(drawn, 1) == round(placed, 1), (
            f"{pid}: the two records of the front door disagree again ({drawn:.2f} against "
            f"{placed:.2f}) -- the elevation has stopped drawing the placed door")
        said = [n for n in scene["not_modelled"] if "axis.door_bay" in n["source"]]
        assert not said, f"{pid}: a disclosure about a disagreement that no longer exists: {said[0]['why'][:160]}"


def test_the_checker_and_the_plate_now_agree_about_the_off_centre_door(both):
    """The sharpest half, resolved: `plan_check` emits `drawn-door-off-the-centre-bay` against
    the PLACED door, and the elevation plate now draws that door in the bay the finding names
    rather than in the middle bay. The plate is evidence FOR the finding beside it."""
    PC = _mod("plan_check")
    AX = _mod("axis")
    scene, sol, _sec, ev = both["tidewater-georgian-careful"]
    findings = PC.check(sol)["findings"]
    off = [f for f in findings if f.get("kind") == "drawn-door-off-the-centre-bay"]
    assert len(off) == 1, (
        "the checker no longer convicts this placement of an off-centre door, so the "
        "agreement this test names has changed — re-derive it")
    EL = _mod("elevation")
    door = next(r for r in EL.opening_rects(ev, ev["entrance_face"])["rects"]
                if r["kind"] == "door" and r["entrance"])
    bays = sol["footprint"]["bays"]
    t = _t_ext(_sec)
    span = (door["x0_in"] + door["x1_in"]) / 24.0 - t          # back to the clear frame
    module = sol["footprint"]["width_ft"] / bays
    drawn_bay = int(span // module)
    db = AX.door_bay(sol)
    assert drawn_bay == db["bay"] != bays // 2, (
        f"the elevation draws the door in bay {drawn_bay} of {bays} and the checker convicts "
        f"bay {db['bay']} -- they must be one bay, and not the middle one")


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
    and says so nowhere.

    IT RAISES A NAMED CLASS, WHICH IS WHAT LETS `build/validate.py` TELL IT FROM A REFUSAL
    (WP-12.8). That checker wraps the scene selftest in a blanket `except Exception` and prints
    `N/EV -- could not evaluate`, so the only CI consumer of this raise was converting the
    loudest failure this file can produce into one line of text and exiting 0. `ValueError`
    alone could not be separated from a plan whose placement was refused.

    AND `xy` IS NO LONGER AMONG THE REFUSALS, because the schema's plane enum admits it and
    `round/solids.js` builds it: a record three spellings called valid was one the frame
    refused to measure. It is measured now; `sweep` and `lathe` are refused and are also no
    longer in the schema at all (WP-12.9), so this raise is unreachable from any schema-valid
    record and is kept for the records that reach `_extent` without being schema-checked first.
    """
    for bad in ({"type": "lathe", "profile": []},
                {"type": "sweep", "profile": [], "path": [], "scale": 1},
                {"type": "extrude", "plane": "zz", "at": 0, "thickness": 1, "outline": [[0, 0]]}):
        with pytest.raises(SC.UnknownPrimitive):
            SC._extent(bad)
    # it is a ValueError too, so a caller catching the broad class still catches it
    assert issubclass(SC.UnknownPrimitive, ValueError)
    lo, hi = SC._extent({"type": "extrude", "plane": "xy", "at": 3.0, "thickness": 0.5,
                         "outline": [[0, 0], [10, 0], [10, 4], [0, 4]]})
    assert lo == [0, 0, 3.0] and hi == [10, 4, 3.5], (
        f"an xy extrusion measures {lo} to {hi}: u and v are x and y and the extrusion runs z")


def test_the_frame_measures_every_primitive_the_schema_admits_and_no_others():
    """The schema's primitive set and `_extent`'s vocabulary are ONE set, asserted both ways.

    WP-12.9. `sweep` and `lathe` sat in the geometry `oneOf` declared by field NAME alone --
    `profile`/`path`/`scale` and `radius_at`/`axis`/`z0`, with no shape, no units and no frame --
    and nothing in the tree emitted either, so `_extent` could not measure them without first
    inventing their semantics. That is a gap between two spellings of one vocabulary, which is
    exactly what WP-12.8 found between the scene's ink enum and the viewer's pen map, and it is
    closed the same way: by an assertion relating the two, in both directions.

    IT IS DRIVEN RATHER THAN READ OFF THE SOURCE. A guard enumerating `_extent`'s `if t ==`
    branches would be a source-text selector, and this repository has been bitten by four of
    those; this builds a real instance of every kind the schema admits and requires the frame to
    measure it. The samples are VALIDATED against the schema first, so they are the schema's
    shapes rather than my recollection of them -- without `jsonschema` that half reports COULD
    NOT EVALUATE and the measurement half still runs.
    """
    schema = json.load(open(os.path.join(ROOT, "schema", "scene.schema.json")))
    oneof = schema["$defs"]["solid"]["properties"]["geometry"]["oneOf"]
    kinds = {b["properties"]["type"]["const"] for b in oneof}
    assert kinds == {"box", "extrude", "prism", "plane"}, (
        f"the schema admits {sorted(kinds)}. A primitive added here owes `_extent` a rule in "
        f"the same commit -- and a rule that cannot be derived from the schema's own statement "
        f"of the shape is a rule that would have to be invented.")
    assert "sweep" not in kinds and "lathe" not in kinds, (
        "sweep and lathe are removed (WP-12.9): they were declared by field name with no shape, "
        "so no extent rule for them could be derived rather than invented")

    samples = {
        "box": {"type": "box", "origin": [0.0, 0.0, 0.0], "size": [2.0, 3.0, 4.0]},
        "prism": {"type": "prism", "polygon": [[0.0, 0.0], [2.0, 0.0], [2.0, 3.0]],
                  "z0": 1.0, "z1": 5.0},
        "plane": {"type": "plane",
                  "vertices": [[0.0, 0.0, 0.0], [4.0, 0.0, 1.0], [4.0, 2.0, 3.0]]},
        "extrude": {"type": "extrude", "plane": "xz", "at": 1.0, "thickness": 0.5,
                    "outline": [[0.0, 0.0], [3.0, 0.0], [3.0, 2.0]]},
    }
    assert set(samples) == kinds, (
        f"the schema admits {sorted(kinds)} and this test builds {sorted(samples)} -- a "
        f"primitive with no sample here is one this guard silently does not cover")

    try:
        import jsonschema
    except Exception:
        jsonschema = None
    for k, g in samples.items():
        if jsonschema is not None:
            jsonschema.validate(g, {"$defs": schema["$defs"],
                                    "oneOf": schema["$defs"]["solid"]["properties"]["geometry"]["oneOf"]})
        lo, hi = SC._extent(g)                      # must not raise
        assert len(lo) == 3 and len(hi) == 3, (k, lo, hi)
        assert all(hi[i] >= lo[i] for i in range(3)), (
            f"{k} measures {lo} to {hi}, which is inside out")
    if jsonschema is None:
        pytest.skip("jsonschema absent: the samples were measured but NOT validated against the "
                    "schema -- COULD NOT EVALUATE on that half, which is not a pass")
