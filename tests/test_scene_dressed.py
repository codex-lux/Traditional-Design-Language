"""The envelope dressed (WP-12.6).

THE TWO ASSERTIONS THIS FILE EXISTS FOR ARE THE ONES THE CORPUS CANNOT REACH. A chimney whose
plan size is NOT a judgment, and a dormer the roof cannot carry, are both states the shipped
plans never produce — so both are driven by hand, on WP-8.11's rule, and each asserts its own
premise so the day a record reaches one the suite says so rather than the fixture quietly
becoming redundant.

AND THE DEFECT THIS PACKAGE ALMOST SHIPPED WAS FOUND BY A COUNT AND BY NOTHING ELSE.
`shutters_carried` is set per STOREY WINDOW (`elevation.py` 1843) and not on the elevation; the
first draft read it off `elev`, got `None` on every house, and drew no shutter anywhere. The sash
bars appeared, the picture looked dressed, and a whole class was simply absent — visible only in
a census of solid classes before and against after. So this file counts classes rather than
asserting that some solid exists.
"""
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
def tidewater():
    sol, sec, rf, ev = _build("tidewater-georgian-careful")
    return SC.build_scene(sol, sec, rf, ev), ev


@pytest.fixture(scope="module")
def spec():
    sol, sec, rf, ev = _build("spec-builder-colonial")
    return SC.build_scene(sol, sec, rf, ev), ev


def _storey_of(sid):
    """`opening_rects` names a rectangle `{face}-{bay}-{storey}` (or `{face}-{bay}-door`), and
    every solid dressing it prefixes that name — so the storey is the third field, for a frame
    and for a sash bar alike.

    THIS USED TO BE `"-ground-" in sid`, WHICH READ A SEPARATOR AND NOT A FIELD. It worked only
    while `_openings` rebuilt the frame's id as `{face}-{bay}-{storey}-{kind}`; the moment the
    frame took the rect's own name — which is the fix for one opening having two names — a frame
    id ended at `ground` and the selector silently matched nothing. A guard that reads a
    separator is a guard that goes blind on the next rename.
    """
    return sid.split("-")[2]


def _classes(scene):
    out = {}
    for s in scene["solids"]:
        out[s["class"]] = out.get(s["class"], 0) + 1
    return out


# ------------------------------------------------------------------ the sash


def test_the_bar_count_is_the_light_count_the_record_states(tidewater):
    """`across - 1` verticals — the two sashes of a double-hung align, so a bar is ONE member —
    and `2 x high - 1` horizontals, of which the middle is the meeting rail."""
    scene, ev = tidewater
    windows = [w for w in ev["storey_windows"]]
    assert windows, "the elevation states no storey window and this test is about nothing"
    c = _classes(scene)
    # one meeting rail per drawn window
    frames = [s for s in scene["solids"] if s["class"] == "opening-frame"]
    win_frames = [s for s in frames if not s["id"].endswith("-door")]
    # THE SCHEMA'S OWN WORDS. A glazing bar is a `muntin`; the middle horizontal is the
    # MEETING RAIL and is a member of the `sash`. The first draft of this package invented
    # `sash-bar` and `meeting-rail` and the schema check refused all 350 at once.
    assert c["sash"] == len(win_frames), (
        f"{c['sash']} meeting rails against {len(win_frames)} windows — a double-hung "
        "has exactly one")
    # and the bars reconcile with the two storeys' own light counts
    per = {}
    for w in windows:
        a, h = w["lights_across"], w["lights_high_per_sash"]
        per[w["storey"]] = (a - 1) + (2 * h - 1) - 1      # less the meeting rail
    counts = {}
    for s in scene["solids"]:
        if s["class"] in ("muntin", "sash"):
            counts[s["id"].rsplit("-bar-", 1)[0]] = 1
    n_ground = sum(1 for s in win_frames if _storey_of(s["id"]) == "ground")
    assert n_ground and n_ground < len(win_frames), (
        f"{n_ground} of {len(win_frames)} window frames read as ground — the storey selector "
        "is matching all or nothing, so the two-storey arithmetic below asserts nothing")
    n_upper = len(win_frames) - n_ground
    want = n_ground * per["ground"] + n_upper * per.get("upper", per["ground"])
    assert c["muntin"] == want, (
        f"{c['muntin']} muntins against {want} implied by {n_ground} ground windows at "
        f"{per['ground']} and {n_upper} upper at {per.get('upper')}")


def test_a_window_with_no_light_count_is_refused_and_not_drawn_bare():
    """Driven: no shipped record omits the light count, and a window drawn with no bars would
    read as a fixed sheet of glass — which is a statement about the house."""
    states = SC._States()
    rects = {"S": [{"id": "S-0-ground", "kind": "window", "storey": "ground",
                    "x0_in": 0.0, "x1_in": 36.0, "sill_in": 30.0, "head_in": 100.0,
                    "record": {"lights_across": None, "lights_high_per_sash": None,
                               "muntin_width_in": None}}]}
    out = SC._dress_openings({}, states, rects, 0, 0, 40, 30, 1.0)
    assert out == []
    assert any("sash bars" in n["what"] for n in states.not_modelled)


# ------------------------------------------------------------------ the shutters


def test_shutters_are_drawn_iff_the_storey_window_carries_them(spec, tidewater):
    """TWO LEAVES A WINDOW, and the pair is what makes this a real assertion: the spec Colonial
    carries shutters and the Tidewater house does not, so a change that drew them everywhere or
    nowhere fails on one of the two."""
    s_scene, s_ev = spec
    t_scene, t_ev = tidewater
    assert all(w["shutters_carried"] for w in s_ev["storey_windows"])
    assert not any(w["shutters_carried"] for w in t_ev["storey_windows"])

    sc = _classes(s_scene)
    tc = _classes(t_scene)
    win = len([s for s in s_scene["solids"]
               if s["class"] == "opening-frame" and not s["id"].endswith("-door")])
    assert sc["shutter"] == 2 * win, f"{sc['shutter']} leaves against {win} windows"
    assert "shutter" not in tc, (
        "the Tidewater house draws shutters. Its own kit makes `none` CANONICAL — 'NO EXTERIOR "
        "SHUTTERS on the solid-masonry Tidewater house', adjudicated in WP-5.13 against four "
        "independent records")


def test_it_is_shutters_carried_that_decides_and_not_the_leaf_width(spec):
    """DRIVEN, BECAUSE THE CORPUS CANNOT TELL THE TWO APART (WP-12.8).

    The gate is `rec.get("shutters_carried") and lw_in`, and on both shipped plans those two
    are perfectly coextensive — the Tidewater windows carry `False` with a `None` width, the
    spec Colonial's carry `True` with 14.011 and 11.605. So the width alone does all the work,
    and the mutation audit found that **removing the `shutters_carried` half of the gate
    outright leaves the whole suite green**: a test over the corpus cannot say which condition
    is holding. That is WP-11.15's own rule, that a fixture where both branches return the same
    number guards neither, met in a boolean.

    A record stating a leaf width and declining to carry shutters is the discriminator, and it
    is exactly the record WP-5.13's adjudication describes: the width resolves from the kit
    cascade whether or not the style carries the member.
    """
    states = SC._States()
    rec = {"lights_across": 3, "lights_high_per_sash": 3, "muntin_width_in": 0.875,
           "shutters_carried": False, "shutter_leaf_width_in": 14.0,
           "shutter_panel_count": 2}
    rect = {"id": "S-0-ground", "kind": "window", "storey": "ground", "record": rec,
            "x0_in": 24.0, "x1_in": 60.0, "sill_in": 36.0, "head_in": 96.0}
    out = SC._dress_openings({}, states, {"S": [rect]}, -1.0, -1.0, 40.0, 30.0, 1.0)
    assert not [o for o in out if o["class"] == "shutter"], (
        "a window stating a leaf width and NOT carrying shutters was dressed with two of them "
        "— the gate is reading the width and not the carrying")
    assert [o for o in out if o["class"] in ("muntin", "sash")], (
        "no bars were drawn either, so the fixture never reached the dressing at all and the "
        "assertion above is about nothing")
    # and the same record carrying them does draw two, so the refusal is not unconditional
    rec2 = dict(rec, shutters_carried=True)
    rect2 = dict(rect, record=rec2)
    out2 = SC._dress_openings({}, SC._States(), {"S": [rect2]}, -1.0, -1.0, 40.0, 30.0, 1.0)
    assert len([o for o in out2 if o["class"] == "shutter"]) == 2, (
        "the same window carrying shutters draws no pair, so this test would pass on a "
        "function that never draws one")


def test_a_leaf_is_the_width_the_record_states(spec):
    s_scene, s_ev = spec
    want = {w["storey"]: w["shutter_leaf_width_in"] / 12.0 for w in s_ev["storey_windows"]}
    seen = 0
    for s in s_scene["solids"]:
        if s["class"] != "shutter":
            continue
        storey = _storey_of(s["id"])
        xs = [p[0] for p in s["geometry"]["outline"]]
        assert abs((max(xs) - min(xs)) - want[storey]) < 0.01, (
            f"{s['id']} is {max(xs) - min(xs):.3f} ft wide against a stated "
            f"{want[storey]:.3f}")
        seen += 1
    assert seen > 0, "no shutter was measured, so this asserts nothing"


# ------------------------------------------------------------------ the sill


def test_the_sill_is_refused_and_the_reason_names_the_band(tidewater):
    """`window_sill.projection_in` is a BAND on the node this corpus draws, which is
    `oq/a-child-band-replaces-an-ancestor-derivation` reaching its first consumer."""
    scene, _ = tidewater
    sills = [n for n in scene["not_modelled"] if "sill" in n["what"]]
    assert len(sills) == 1, f"{len(sills)} sill refusals"
    assert "band" in sills[0]["why"].lower()
    assert sills[0]["source"] == "kit.window_sill.projection_in"
    assert not [s for s in scene["solids"] if s["class"] == "sill"]


# ------------------------------------------------------------------ the chimney


def test_a_judged_stack_is_an_axis_and_a_named_judgment_and_never_a_solid(tidewater):
    scene, ev = tidewater
    assert ev.get("chimney_stack_plan_judgment"), (
        "the Tidewater stack's plan size is no longer a judgment, so this test now asserts "
        "nothing about the branch it was written for")
    axes = [s for s in scene["solids"] if s["class"] == "chimney"
            and s["geometry"]["type"] == "plane"]
    assert axes, "no axis was drawn for a stack the record places"
    assert not [s for s in scene["solids"] if s["class"] == "chimney"
                and s["geometry"]["type"] == "box"], (
        "a solid stack was drawn at a plan size the corpus declines to settle")
    assert len(scene["judgment"]) == len(axes)
    assert all(s["kind"] == "judgment" for s in axes)
    assert any("mason will build 18 or 27" in j["why"] for j in scene["judgment"])


def test_a_stack_whose_plan_size_is_stated_is_a_solid():
    """DRIVEN. No node in this corpus states a chimney plan size that is not a judgment, so the
    solid branch is unreachable and a guard over the shipped plans would pass with it deleted."""
    states = SC._States()
    # `total_height_grade_ft` is the key `roof.py` writes and `_chimneys` reads. The first
    # version of this fixture omitted it and the function fell back onto an editorial 2 ft
    # above the ridge -- so the test drove the branch and asserted the PLAN size while nothing
    # anywhere read the stack's HEIGHT, which is how a stack six feet short of its own record
    # shipped through a suite written for exactly this function.
    roof = {"chimneys": {"applicable": True, "positions": [
                {"x_ft": 10.0, "y_ft": 5.0, "grade_to_ridge_ft": 28.0,
                 "height_above_ridge_ft": 8.0, "total_height_grade_ft": 36.0}]},
            "main": {"ridge": {"grade_to_ridge_ft": 28.0}}}
    section = {"footprint": {"width_ft": 40, "depth_ft": 30}, "wall": {"exterior_in": 12}}
    out = SC._chimneys(roof, {"chimney_stack_plan_in": 24.0,
                              "chimney_stack_plan_judgment": False}, section, states)
    assert [s["class"] for s in out] == ["chimney"]
    assert out[0]["geometry"]["type"] == "box"
    assert abs(out[0]["geometry"]["size"][0] - 2.0) < 1e-9, "24 in is 2 ft"
    # AND THE HEIGHT IS THE RECORD'S, WHICH NOTHING ASSERTED (WP-12.8). `_chimneys` read
    # `grade_to_cap_ft` -- a key nothing in this repository writes -- so the `or` fell through
    # to an editorial 2.0 ft above the ridge on every stack on every plan. On the Tidewater
    # record that is 41.03 ft drawn against a stated 47.03, BELOW the 6 ft minimum the same
    # roof record judges `ok: True`, and six feet away from where `render_elevation` puts the
    # same stack. Every test here read the plan size and none read the height.
    assert abs(out[0]["geometry"]["size"][2] - 36.0) < 1e-9, (
        f'the stack rises to {out[0]["geometry"]["size"][2]} against a stated '
        "total_height_grade_ft of 36.0")
    assert states.judgment == [], "a stated size is not a judgment"


def test_a_stack_the_roof_cannot_carry_is_refused(spec):
    """The spec Colonial's massing calls for gable-end stacks and its roof judges no ridge to
    measure one against — and the refusal must SAY that rather than a stack silently not
    appearing.

    THE FIRST VERSION OF THIS TEST ASSERTED ONLY THE ABSENCE, which is the whole finding
    (WP-12.8). Its body was one negative assertion; deleting the refusal outright, and deleting
    `_chimneys` entirely, both left it green and the whole file green. And the refusal it named
    was not even the one this record takes: `_chimneys` returned `[]` on empty `positions`
    before reaching any refusal at all, so a four-over-four whose hearth is `gable-end-paired`
    read as a house that simply has no fires. The roof record had the reason in full and the
    scene dropped it.
    """
    scene, _ev = spec
    assert not [s for s in scene["solids"] if s["class"] == "chimney"]
    said = [n for n in scene["not_modelled"] if n.get("class") == "chimney"]
    assert len(said) == 1, (
        f"{len(said)} chimney refusals — a house whose massing calls for stacks and draws none "
        "owes the reader exactly one reason")
    # the reason is the ROOF's own sentence, republished rather than composed here
    assert said[0]["source"] == "roof.chimneys.note"
    assert "ridge" in said[0]["why"], said[0]["why"]
    # AND THE PREMISE, so this cannot go quiet the day the spec Colonial judges a ridge:
    # the reason must name a stack the record ASKED FOR, not merely a house without one.
    assert "chimney" in said[0]["why"].lower(), said[0]["why"]


# ------------------------------------------------------------------ the dormers


def test_a_dormer_the_roof_cannot_carry_is_named_with_the_records_own_reason():
    """DRIVEN, and the field names are the point. `PLAN-OF-ACTION.md` says this package must not
    read `placeable` or `not_drawn_reason` because they do not exist. They do — `elevation.py`
    1971-1980 — and `render_elevation.py` has read them since they landed."""
    states = SC._States()
    out = SC._dormers({"dormers": {"stated": True, "refused": False, "count": 3, "placeable": False,
                                   "not_drawn_reason": "the roof record could not judge a pitch"}},
                      states)
    assert out == []
    named = [n for n in states.not_modelled if n["source"] == "elevation.dormers.not_drawn_reason"]
    assert len(named) == 1
    assert "could not judge a pitch" in named[0]["why"]


def test_a_record_that_states_no_dormer_says_nothing_at_all():
    """Not a reassuring zero: a house that states no dormers has none to refuse."""
    states = SC._States()
    assert SC._dormers({"dormers": {"stated": False}}, states) == []
    assert states.not_modelled == []


def test_a_stated_count_of_zero_is_a_house_with_no_dormers_and_not_a_refusal(tidewater, spec):
    """BOTH SHIPPED PLANS ARE THIS CASE, so it is asserted on the real records rather than driven.

    `stated: True, count: 0` is a MEASURED ZERO — the record considered dormers and says the
    house has none. The first version of `_dormers` gated on `stated` and filed a `not_modelled`
    entry against both, which says this layer failed to model something that is not there. That
    is the fake-unjudged collapse in the direction nobody looks for, and it moved the shipped
    corpus's disclosure counts by one apiece before it was caught.

    `elevation.py` 1954 is the authority and the assertion below states it: `placeable` and
    `not_drawn_reason` are written only where the count is truthy, so a zero-count record cannot
    reach the branch that refuses.
    """
    for scene, ev in (tidewater, spec):
        d = ev["dormers"]
        assert d.get("stated") and not d.get("count"), (
            "a shipped plan has grown dormers, so this test is no longer about the case it was "
            "written for — re-derive it rather than re-pinning it")
        assert d.get("placeable") is None and d.get("not_drawn_reason") is None, (
            "the elevation wrote a placement verdict for a house with no dormers")
        assert not [n for n in scene["not_modelled"] if "dormer" in n["source"]], (
            f"{[n['source'] for n in scene['not_modelled']]} — a house with no dormers has "
            "nothing for this layer to refuse")


def test_a_shortfall_is_named_separately_from_an_unplaceable_roof():
    states = SC._States()
    SC._dormers({"dormers": {"stated": True, "count": 4, "placeable": True,
                             "placement_shortfall_note": "4 declared, 3 bays free"}}, states)
    srcs = {n["source"] for n in states.not_modelled}
    assert "elevation.dormers.placement_shortfall_note" in srcs
    assert "elevation.dormers.not_drawn_reason" not in srcs, (
        "a shortfall and an unplaceable roof are different findings")


# ------------------------------------------------------------------ one spelling


def test_the_face_mapping_is_spelled_once():
    """`_face_extrude` was lifted out of `_openings` because WP-12.6 needed it forty more times
    per plan. A second copy is how the north and east openings came to stand proud of their own
    walls in WP-12.1 — a defect no number in the record disagreed with."""
    src = open(os.path.join(ROOT, "build", "scene.py")).read()
    body = src[src.index("def _face_extrude"):]
    body = body[body.index("\n"):]
    # the mapping's own tell: choosing the plane from the face letter
    assert body.count('"xz", (oy if face ==') == 1, (
        "the face-to-plane mapping is spelled more than once in scene.py")
    assert src.count('"yz", (ox if face ==') == 1


def test_the_key_this_function_reads_is_the_key_the_elevation_writes(tidewater, spec):
    """THE DEFECT THIS PACKAGE SHIPPED AND ITS OWN THREE TESTS COULD NOT SEE.

    `build_elevation` writes `dormers` — plural, `elevation.py` 2012 — and `render_elevation.py`
    reads `elev.get("dormers")` in both of its readers. `scene._dormers` read `dormer`, so it
    took `{}` on every record in the corpus: no dormer drawn, no refusal recorded, no
    disclosure. Nothing failed, because a house that states no dormers and a function that
    cannot find the block it would read are the same empty answer.

    **The three tests above could not catch it and would never have caught it**, because every
    one of them drives `_dormers` with a hand-built dict — and that dict was written from the
    same wrong key as the code, so the fixture and the defect corroborated each other. A driven
    test proves the branch runs; it says nothing about whether anything reaches the branch.

    So this one takes the name off a REAL elevation and hands the function the real block. It is
    deliberately not a source-text grep for the string `dormers`: the property is that the two
    modules agree about where the record lives, and the only way to assert that is to route one
    into the other.
    """
    for scene, ev in (tidewater, spec):
        assert "dormers" in ev, (
            "build_elevation no longer writes a `dormers` block; scene._dormers reads one, and "
            "a reader of a key nobody writes is silent rather than wrong")
        assert "dormer" not in ev, (
            "the elevation has grown a SINGULAR `dormer` key beside its plural one — two names "
            "for one record is how this defect happened in the first place")

    # and the function really does consume that block rather than falling through on shape
    scene, ev = spec
    states = SC._States()
    SC._dormers({"dormers": dict(ev["dormers"], stated=True, refused=False, count=3, placeable=False,
                                 not_drawn_reason="driven")}, states)
    assert any(n["source"] == "elevation.dormers.not_drawn_reason"
               for n in states.not_modelled), (
        "the real record's own block, with one field driven, reaches no branch — so the key "
        "matches and something else about the shape does not")
