"""The guards WP-12.8's adversarial audit earned.

Every assertion in this file exists because something was WRONG and nothing could see it. They
are collected here rather than scattered into the three package suites for one reason: each is a
guard against a defect that survived a package whose own tests were green, so a reader deciding
whether to trust this layer should be able to read the failures in one place.

The four that matter most, in the order they were found:

1. **A dressing member on the north or east face was drawn one wall thickness INSIDE its wall.**
   `_face_extrude` returns the LOW face, which is the outside face on S and W and the inside one
   on N and E. 1,763 solids corpus-wide, including the entire doorcase of `spec-builder-colonial`,
   whose entrance front is the N face. It is WP-12.2's own defect with the sign reversed.
2. **`_chimneys` read `grade_to_cap_ft`, a key nothing in this repository writes**, so every
   stack on every plan was drawn at an editorial 2 ft above the ridge -- 41.03 ft against a
   stated 47.03 on the Tidewater record, BELOW the 6 ft minimum the same roof record judges
   `ok: True`, and six feet from where the elevation plate puts the same stack.
3. **`_entrance_agreement` compared the elevation's `u` against a clear-frame plan coordinate**,
   so every published gap was short by one exterior wall and a house whose two records AGREE
   would have been convicted by `t_ext`.
4. **`bounds` stopped being the envelope the moment it became the union of what is drawn**, and
   `frame.js::modelAt` still read it as the envelope -- sliding the Tidewater E plate 2.166 ft
   along its own horizontal with nothing red anywhere.

`build/scene.py` is loaded through `modcache` for the reason `validate.py` records: a by-path
loader here returns a fresh module per call and pulls geometry, structure, roof and elevation in
behind it.
"""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

SC = modcache.load("scene", os.path.join(ROOT, "build", "scene.py"))
PLANS = ("tidewater-georgian-careful", "spec-builder-colonial")

# A member that dresses a wall stands on that wall's OUTSIDE face. An `opening-frame` is
# deliberately not in this list: its thickness IS the wall, so it spans from the low face and
# that is correct on every face.
DRESSING = ("muntin", "sash", "shutter", "surround", "entablature")


@pytest.fixture(scope="module")
def scenes():
    """Both shipped plans on the HEURISTIC, for `tests/test_scene.py`'s stated reason: `auto`
    reaches a proof on one machine and spends its budget on another."""
    out = {}
    for name in PLANS:
        s, section, err = SC._build_from_plan(
            os.path.join(ROOT, "plans", f"{name}.json"), engine="heuristic")
        assert not err, f"{name}: {err}"
        out[name] = (s, section)
    return out


def _wall_faces(scene):
    """Each face's (low, high) coordinate across the wall, read off the wall solids themselves
    rather than off the section -- so this reader and the one under test cannot agree by both
    quoting `section.footprint`."""
    out = {}
    for s in scene["solids"]:
        if s["class"] != "wall" or not s.get("face"):
            continue
        ax = 1 if s["face"] in ("S", "N") else 0
        g = s["geometry"]
        lo = g["origin"][ax]
        out[s["face"]] = (lo, lo + g["size"][ax])
    return out


def _depth_of(solid, face):
    """Where a member sits across its wall: the outer coordinate for an extrusion, the plane's
    own coordinate for a flat one."""
    g = solid["geometry"]
    ax = 1 if face in ("S", "N") else 0
    if g["type"] == "extrude":
        return g["at"] if face in ("S", "W") else g["at"] + g["thickness"]
    if g["type"] == "plane":
        return g["vertices"][0][ax]
    return None


# ------------------------------------------------------- 1. the outside face


def test_every_dressing_member_stands_on_the_outside_face_of_its_wall(scenes):
    """THE LARGEST DEFECT THE AUDIT FOUND, AND NOTHING IN THE TREE READ THE COORDINATE.

    Every test written for WP-12.6 and WP-12.7 read a dressing member's IN-PLANE extent -- its
    width against the stated leaf width, its light count, its position along the face. Not one
    read the third coordinate, so 1,763 of 3,442 dressing solids stood on the inside face of
    their own wall and every suite was green.

    The tolerance is 0.01 ft because `section.footprint` is rounded to two places and the wall
    boxes carry that residue; the defect this catches is 0.667 ft on the spec Colonial and
    1.292 ft on the Tidewater plan, so a hundredth of a foot separates them by two orders of
    magnitude.
    """
    for name, (scene, _sec) in scenes.items():
        walls = _wall_faces(scene)
        assert walls, f"{name}: no exterior wall solids, so this test is about nothing"
        wrong, seen = [], 0
        for s in scene["solids"]:
            f = s.get("face")
            if s["class"] not in DRESSING or f not in walls:
                continue
            d = _depth_of(s, f)
            if d is None:
                continue
            seen += 1
            outside = walls[f][0] if f in ("S", "W") else walls[f][1]
            # A MEMBER MAY STAND PROUD AND MAY NEVER BE SET BACK. The entablature's architrave
            # and cornice project from the naked by a stated `projection_in`, so their outer
            # coordinate is OUTSIDE the wall face — correct, and the reason this is an
            # inequality rather than an equality. Outward is DECREASING on S and W and
            # increasing on N and E; the defect put every N and E member 0.667 or 1.292 ft the
            # wrong way, which is two orders of magnitude past the 0.01 ft rounding residue
            # `section.footprint` carries.
            behind = (d - outside) if f in ("S", "W") else (outside - d)
            if behind > 0.01:
                wrong.append((s["id"], s["class"], round(d, 3), round(outside, 3)))
        assert seen > 0, f"{name}: no dressing member was examined at all"
        assert not wrong, (
            f"{name}: {len(wrong)} of {seen} dressing members are not on their wall's outside "
            f"face, e.g. {wrong[:4]}")


def test_a_flush_member_sits_exactly_on_the_face_and_a_projecting_one_stands_proud(scenes):
    """The inequality above admits a member that stands a mile off the wall, so the flush ones
    are held to an equality separately. A muntin, a meeting rail, a shutter leaf and a surround
    are flush by construction — the record states no projection for any of them — while an
    entablature member carries its own `projection_in`, and the two must not be conflated."""
    for name, (scene, _sec) in scenes.items():
        walls = _wall_faces(scene)
        flush = proud = 0
        for s in scene["solids"]:
            f = s.get("face")
            if f not in walls:
                continue
            d = _depth_of(s, f)
            if d is None:
                continue
            outside = walls[f][0] if f in ("S", "W") else walls[f][1]
            if s["class"] in ("muntin", "sash", "shutter", "surround"):
                flush += 1
                assert abs(d - outside) < 0.01, (
                    f'{name}: {s["id"]} is flush and sits {abs(d - outside):.3f} ft off its face')
            elif s["class"] == "entablature" and s["geometry"]["type"] == "extrude":
                proud += 1
                out_by = (outside - d) if f in ("S", "W") else (d - outside)
                assert out_by > 0, (
                    f'{name}: {s["id"]} projects and does not stand proud of its wall')
        assert flush > 0, f"{name}: no flush member was examined"
        assert proud > 0, f"{name}: no projecting member was examined"


def test_the_two_plans_between_them_exercise_all_four_faces(scenes):
    """THE PREMISE, AND IT IS WHAT MAKES THE TEST ABOVE AN ASSERTION RATHER THAN A SAMPLE.

    The defect lives only on N and E. A pair of plans dressing S and W alone would pass the
    guard above with the bug fully in place -- which is exactly how it shipped, since every
    existing test asserted the in-plane extent and no face was ever the subject.
    """
    faces = set()
    for _name, (scene, _sec) in scenes.items():
        for s in scene["solids"]:
            if s["class"] in DRESSING and s.get("face"):
                faces.add(s["face"])
    assert faces == {"S", "N", "E", "W"}, (
        f"the shipped plans dress {sorted(faces)} — the guard above cannot see the N/E defect "
        "unless something is drawn there")


def test_an_opening_frame_still_spans_its_whole_wall(scenes):
    """THE CONTROL. `_on_the_outside_face` must not have moved the frame: its thickness IS the
    exterior wall, so it runs from the low face to the high one on every face, and a fix that
    shifted it too would have swapped one defect for another."""
    for name, (scene, _sec) in scenes.items():
        walls = _wall_faces(scene)
        for s in scene["solids"]:
            if s["class"] != "opening-frame" or s.get("face") not in walls:
                continue
            lo, hi = walls[s["face"]]
            g = s["geometry"]
            assert abs(g["at"] - lo) < 0.01 and abs(g["at"] + g["thickness"] - hi) < 0.01, (
                f'{name}: {s["id"]} runs {g["at"]:.3f} to {g["at"] + g["thickness"]:.3f} '
                f"against a wall of {lo:.3f} to {hi:.3f}")


# ------------------------------------------------------- 2. the stack's height


def test_a_stack_rises_to_the_height_its_own_record_states(scenes):
    """`roof.py` writes `total_height_grade_ft` and `render_elevation.py` reads it. `_chimneys`
    read `grade_to_cap_ft`, which no writer anywhere produces, and fell through `or` onto an
    editorial 2 ft above the ridge -- so the model and the plate drew the same stack six feet
    apart, and the model's broke a style constraint the record passes.

    Read off the ROOF record rather than off a remembered number, so this stays true when the
    placement moves.
    """
    ran = 0
    for name, (scene, section) in scenes.items():
        sol = json.loads(json.dumps(scene))  # not used; the roof is rebuilt below
        del sol
        plan = json.load(open(os.path.join(ROOT, "plans", f"{name}.json")))
        geo = modcache.load("geometry", os.path.join(ROOT, "build", "geometry.py"))
        placed = geo.solve(plan, None, engine="heuristic")
        rf = modcache.load("roof", os.path.join(ROOT, "build", "roof.py"))
        roof = rf.build_roof(placed, None, section=section)
        for i, pos in enumerate((roof.get("chimneys") or {}).get("positions") or []):
            want = pos["total_height_grade_ft"]
            drew = [s for s in scene["solids"]
                    if s["class"] == "chimney" and s["id"].startswith(f"chimney-{i}")]
            assert len(drew) == 1, f"{name}: {len(drew)} solids for stack {i}"
            g = drew[0]["geometry"]
            top = (max(v[2] for v in g["vertices"]) if g["type"] == "plane"
                   else g["origin"][2] + g["size"][2])
            ran += 1
            assert abs(top - want) < 0.01, (
                f"{name}: stack {i} rises to {top:.2f} ft against the record's {want:.2f}")
    assert ran > 0, "no plan in this corpus draws a stack, so this test proves nothing"


def test_the_frame_reaches_the_top_of_the_stack(scenes):
    """And the frame follows it: the height defect dragged `bounds.max[2]` down with it, so a
    viewer framing the model would have cropped the stacks it did draw."""
    for name, (scene, _sec) in scenes.items():
        tops = [(max(v[2] for v in s["geometry"]["vertices"])
                 if s["geometry"]["type"] == "plane"
                 else s["geometry"]["origin"][2] + s["geometry"]["size"][2])
                for s in scene["solids"] if s["class"] == "chimney"]
        if not tops:
            continue
        assert scene["bounds"]["max"][2] >= max(tops) - 0.01, (
            f'{name}: the frame stops at {scene["bounds"]["max"][2]} below a stack at '
            f"{max(tops)}")


# ------------------------------------------------------- 3. the frame and the envelope


def test_the_envelope_is_the_wall_box_and_the_frame_is_bigger_than_it(scenes):
    """TWO QUANTITIES THAT WERE ONE FIELD. `bounds.min/max` is the union of everything drawn;
    `bounds.envelope` is the outside face of the exterior wall, which is what a flat elevation
    plate registers against. While `bounds` came off `section.footprint` they were the same
    number, and WP-12.7 made them different without telling `frame.js::modelAt`.

    The Tidewater plan is the one that separates them: its stoop stands at y = -3.458, three
    and a half feet clear of the house, so the frame reaches past the envelope on that axis and
    a reader of the wrong one misregisters the E and W plates by 2.166 ft.
    """
    apart = 0
    for name, (scene, _sec) in scenes.items():
        b, env = scene["bounds"], scene["bounds"]["envelope"]
        walls = _wall_faces(scene)
        for i, (lo_face, hi_face) in ((0, ("W", "E")), (1, ("S", "N"))):
            assert abs(env["min"][i] - walls[lo_face[0] if isinstance(lo_face, str) else lo_face][0]) < 0.01 \
                or True  # the axis check below is the real one
        # the envelope's plan extent is the wall boxes' own extent
        for i, faces in ((0, ("W", "E")), (1, ("S", "N"))):
            lo = walls[faces[0]][0]
            hi = walls[faces[1]][1]
            assert abs(env["min"][i] - lo) < 0.01, (
                f"{name}: envelope.min[{i}] is {env['min'][i]} against a wall face at {lo}")
            assert abs(env["max"][i] - hi) < 0.01, (
                f"{name}: envelope.max[{i}] is {env['max'][i]} against a wall face at {hi}")
            # the frame contains the envelope, always
            assert b["min"][i] <= env["min"][i] + 1e-9 and b["max"][i] >= env["max"][i] - 1e-9, (
                f"{name}: the frame is inside the envelope on axis {i}")
            if b["min"][i] < env["min"][i] - 0.01 or b["max"][i] > env["max"][i] + 0.01:
                apart += 1
    assert apart > 0, (
        "the frame and the envelope coincide on every axis of both shipped plans, so a reader "
        "of the wrong one would pass this suite — re-derive rather than deleting")


# ------------------------------------------------------- 4. the stoop, and the amplifier


def _step(**kw):
    st = {"room": "porch", "wall": "S", "riser_count": 3, "riser_height_in": 6.0,
          "tread_depth_in": 13.0,
          "flight": {"x_ft": 10.0, "y_ft": -2.167, "depth_ft": 2.167, "width_ft": 5.0}}
    st.update(kw)
    return st


def _porch(steps, section=None):
    states = SC._States()
    sec = section or {"storeys": [{"index": 0, "grade_to_floor_ft": 1.5}]}
    out = SC._porch({"threshold": {"steps": steps}}, sec, states)
    return out, states


def test_a_flight_with_a_non_positive_tread_is_refused_and_not_drawn():
    """THE AMPLIFIER, AND IT IS A REMOTE ONE. `riser_count` is an unbounded `integer` in the
    plan schema and `_porch` draws one solid per riser; the loop's `break` on `inner - lo <= 0`
    is defeated by a tread that is negative or vanishing, because the difference then GROWS.

    Measured through `POST /api/scene` before the fix: a 56 KB body carrying
    `tread_depth_in: -1.0` with `riser_count: 100000` builds 99,999 solids, and `1e-9` with
    500,000 builds 499,999 -- on a server the infrastructure audit measures as one serialised
    core. `riser_count` ALONE is not the amplifier and the first report of this said it was:
    at the shipped tread the flight's own depth stops the loop at two treads whatever the count.
    """
    for td in (-1.0, 0.0):
        out, states = _porch([_step(tread_depth_in=td, riser_count=100000)])
        assert not [o for o in out if o["class"] == "deck"], (
            f"a tread of {td} in drew {len([o for o in out if o['class'] == 'deck'])} risers")
        # 0.0 is caught by the falsy guard above it and -1.0 by the positivity one; what
        # matters is that neither is silent, and that the refusal names the flight.
        assert any("flight at the S door of porch" in n["what"] for n in states.not_modelled), (
            f"a tread of {td} in was dropped in silence")
    out, states = _porch([_step(tread_depth_in=-1.0, riser_count=100000)])
    assert any("not positive is not a step" in n["why"] for n in states.not_modelled), (
        "a NEGATIVE tread — the one the falsy guard admits — is refused without its reason")
    # and the same for a rise and a rectangle
    for kw in ({"riser_height_in": -6.0}, {"flight": {"x_ft": 0, "y_ft": 0, "depth_ft": -2.0,
                                                      "width_ft": 5.0}}):
        out, _ = _porch([_step(**kw)])
        assert not [o for o in out if o["class"] == "deck"], kw


def test_the_riser_count_is_bounded_and_the_excess_is_refused_by_name():
    """A record whose flight is deep enough to hold them can still ask for more risers than any
    drawing can carry. The cap is a bound on the WORK and says so; what it must never do is
    truncate in silence, because a stoop drawn with 64 of its 100,000 risers and no note is a
    drawing that lies about its record."""
    out, states = _porch([_step(riser_count=100000, tread_depth_in=1.0,
                                flight={"x_ft": 0.0, "y_ft": -500.0, "depth_ft": 500.0,
                                        "width_ft": 5.0})])
    drawn = [o for o in out if o["class"] == "deck"]
    assert len(drawn) <= SC._MAX_DRAWN_RISERS, f"{len(drawn)} risers drawn"
    assert len(drawn) > 1, "the fixture drew nothing, so the cap is not what stopped it"
    assert any("bound on the work" in n["why"] for n in states.not_modelled), (
        "the excess was truncated without a word")


def test_a_flight_with_no_rectangle_is_refused_rather_than_raising():
    """The guard read four fields and the body read seven, so a flight stating a depth and no
    position raised `KeyError: 'y_ft'` out of `build_scene` -- reaching a caller as
    `{"error": "KeyError: 'y_ft'"}`, which says nothing about their record."""
    for missing in ("x_ft", "y_ft", "width_ft", "depth_ft"):
        f = {"x_ft": 10.0, "y_ft": -2.0, "depth_ft": 2.0, "width_ft": 5.0}
        del f[missing]
        out, states = _porch([_step(flight=f)])
        assert not [o for o in out if o["class"] == "deck"]
        assert any("rectangle to stand on" in n["why"] for n in states.not_modelled), missing


def test_two_flights_in_one_room_do_not_share_solid_ids():
    """`threshold.entrance_pass` appends one step per (room, door) pair on the entrance face, so
    a room with two exterior doors on the front produced colliding ids. The schema says an id is
    unique within a scene and nothing enforces it; all sixteen shipped records are clean, so
    this is driven."""
    out, _ = _porch([_step(), _step()])
    ids = [o["id"] for o in out if o["class"] == "deck"]
    assert len(ids) == len(set(ids)), f"duplicate stoop ids: {ids}"
    assert len(ids) >= 4, f"only {len(ids)} risers, so the collision could not have shown"


def test_a_record_with_no_threshold_block_is_an_unjudged_state_and_says_so():
    """`openings.place` skips `threshold.entrance_pass` on its "no footprint on this record"
    early return, and `corpus._placed` hands a pre-placed record back untouched -- so a plan
    with no `threshold` at all is reachable, and the first version drew nothing, refused nothing
    and said nothing about it."""
    states = SC._States()
    out = SC._porch({}, {"storeys": []}, states)
    assert out == []
    assert [n for n in states.not_modelled if n["source"] == "plan.threshold"], (
        "a record that never went through the threshold pass was silently empty")


def test_a_platform_the_record_states_is_named_even_though_it_is_not_drawn():
    """DRIVEN: `threshold._one_stoop` writes `platform` only where the entrance is NOT carried
    by an `entry-porch` room, and the one shipped record that produces a step at all is a porch.
    A band the record holds and this layer does not draw is a `not_modelled` entry, which is the
    module header's own rule."""
    out, states = _porch([_step(platform={"x_ft": 10.0, "y_ft": -3.0, "depth_ft": 1.0,
                                          "width_ft": 5.0})])
    assert not [o for o in out if o["id"].endswith("platform")]
    assert any("platform is a deck" in n["why"] for n in states.not_modelled)


def test_no_shipped_record_carries_a_platform_or_a_second_flight_in_one_room():
    """The premise for the two tests above, so the day a record grows either the suite says so
    rather than the fixtures quietly becoming the only coverage."""
    plats = rooms = 0
    for name in PLANS:
        plan = json.load(open(os.path.join(ROOT, "plans", f"{name}.json")))
        steps = ((plan.get("threshold") or {}).get("steps") or [])
        plats += len([s for s in steps if s.get("platform")])
        seen = [s.get("room") for s in steps]
        rooms += len(seen) - len(set(seen))
    assert plats == 0 and rooms == 0, (
        f"{plats} platform(s) and {rooms} repeated room(s) in the shipped records — both "
        "branches above are reachable now and should be measured rather than driven")


# ------------------------------------------------------- 5. the refusals about nothing


def test_the_sill_refusal_is_about_windows_and_not_about_a_dict():
    """`rects_by_face` is built for all four faces unconditionally, so `if rects_by_face:` is
    `if {"S": [], "N": [], "E": [], "W": []}` -- always true. It would have filed "the sills
    under every window" against a house with no windows, which is WP-12.6's own dormer defect in
    the function immediately below the one it was found in. Latent: the five shipped plans that
    draw no opening refuse their elevation earlier, so this is driven."""
    states = SC._States()
    SC._dress_openings({}, states, {"S": [], "N": [], "E": [], "W": []},
                       -1.0, -1.0, 40.0, 30.0, 1.0)
    assert not [n for n in states.not_modelled if "sills" in n["what"]], (
        "the sills under zero windows were refused")
    # and with one window it IS refused, so the assertion above is not vacuous
    st2 = SC._States()
    rec = {"lights_across": 2, "lights_high_per_sash": 2, "muntin_width_in": 0.875}
    SC._dress_openings({}, st2, {"S": [{"id": "S-0-ground", "kind": "window", "storey": "ground",
                                        "record": rec, "x0_in": 24.0, "x1_in": 60.0,
                                        "sill_in": 36.0, "head_in": 96.0}]},
                       -1.0, -1.0, 40.0, 30.0, 1.0)
    assert [n for n in st2.not_modelled if "sills" in n["what"]], (
        "a real window's sill is no longer refused, so the gate has gone the other way")


def test_an_entrance_that_cannot_be_compared_is_not_an_entrance_that_disagrees(scenes):
    """`states.cannot` is one channel and the `what` is what a plate prints. All three of
    `_entrance_agreement`'s exits shared one `what`, so over the sixteen plans ELEVEN entries
    read as eleven disagreements when four are disagreements and seven are houses whose
    placement seats no exterior door on the entrance front at all."""
    for name, (scene, _sec) in scenes.items():
        ent = [n for n in scene["not_modelled"] if n.get("class") == "entrance"]
        dis = [n for n in ent if n["what"] == "the doorcase and the stoop in one place"]
        cne = [n for n in ent if n["what"].startswith("whether the doorcase")]
        assert not (dis and cne), f"{name}: both states filed at once"
        assert dis, f"{name}: this plan no longer files a disagreement — re-derive"
        for n in dis:
            assert "apart" in n["why"], (
                f"{name}: a disagreement that states no gap: {n['why'][:100]}")

    # AND THE OTHER STATE, WHICH NEITHER SHIPPED PLAN IS IN — so a guard over the pair above
    # cannot see it, and the first version of this test was GREEN under a mutation that gave
    # both states one `what` again. `good-02-portico-library-house` seats no exterior door on
    # its entrance front, and it is a real corpus record rather than a fixture: 7 of the 16
    # plans are in this state and 4 in the other.
    s2, _sec2, err = SC._build_from_plan(
        os.path.join(ROOT, "plans", "reference", "good-02-portico-library-house.json"),
        engine="heuristic")
    assert not err, err
    ent2 = [n for n in s2["not_modelled"] if n.get("class") == "entrance"]
    cne2 = [n for n in ent2 if n["source"] == "axis.door_bay"]
    assert len(cne2) == 1, f"{len(cne2)} could-not-evaluate rows on good-02"
    assert cne2[0]["what"].startswith("whether the doorcase"), (
        "a comparison that could not be made is filed under the same name as one that was made "
        f"and disagreed: {cne2[0]['what']!r}")
    assert "apart" not in cne2[0]["why"]


# ------------------------------------------------------- 5b. the datum a thing stands on


def test_a_hearth_stands_on_its_own_storeys_floor_and_not_at_grade(scenes):
    """FOUND BY RENDERING THE WALK'S OWN SCREENSHOT AND LOOKING AT IT, WHICH IS EIGHT PACKAGES
    RUNNING — and then MEASURED, which is WP-12.5's rule about what a picture is evidence of.

    `hearths.breast` is a PLAN rectangle and carries no z; `_hearths` wrote 0.0. On
    `tidewater-georgian-careful`, whose ground floor is 2.0 ft above grade, that put all three
    fires two feet UNDER the house, lying on the ground outside it. Invisible in every named
    orthographic view — a flat rectangle beneath the floor slab is hidden by the elevation or
    reads as part of the plan cut — and plainly visible in the approach as three pale slabs on
    the lawn at the foot of the west and east walls. Confirmed by projecting the breast
    corners through `frame.js`'s own approach camera before it was called a defect.

    Pre-existing since WP-12.1. The height stays a ZERO: the breast's projection is a judgment
    and this is about the datum.
    """
    seen = 0
    for name, (scene, section) in scenes.items():
        floors = {st["index"]: st.get("grade_to_floor_ft")
                  for st in (section.get("storeys") or [])}
        for s in scene["solids"]:
            if s["class"] != "hearth":
                continue
            seen += 1
            want = floors.get(s.get("level"))
            assert want is not None, f'{name}: {s["id"]} is on a storey the section does not state'
            assert abs(s["geometry"]["origin"][2] - want) < 0.01, (
                f'{name}: {s["id"]} stands at z={s["geometry"]["origin"][2]} against its own '
                f"storey's floor at {want}")
    assert seen > 0, "no plan in this corpus draws a hearth, so this test proves nothing"


def test_the_shipped_floor_is_above_grade_so_that_test_can_fail(scenes):
    """The premise: on a house whose floor IS at grade the assertion above holds with the
    defect fully in place, which is WP-11.15's rule about a fixture where both branches return
    the same number."""
    high = 0
    for _name, (scene, section) in scenes.items():
        if not [s for s in scene["solids"] if s["class"] == "hearth"]:
            continue
        for st in section.get("storeys") or []:
            if (st.get("grade_to_floor_ft") or 0) > 0.5:
                high += 1
    assert high > 0, (
        "every storey carrying a hearth now sits at grade, so the test above cannot tell a "
        "breast on its floor from one on the ground")


# ------------------------------------------------------- 6. a storey is a fact


def test_every_solid_that_stands_on_a_storey_says_which(scenes):
    """`solid.level` is what `three-scene.js` picks an explode offset with, and only slabs,
    walls and hearths carried one -- so `explode: levels` lifted the structure and left every
    window, sash bar, shutter and doorcase behind. The storey is a fact the elevation already
    resolved to lay the opening out; the join had to be made by hand because `opening_rects`
    names a storey by id and `solid.level` is an integer.

    A chimney, a gable and a roof plane carry NO level, and that is right: they are not on a
    storey. Naming them here is what stops this test being satisfied by defaulting.
    """
    ABOVE = {"chimney", "gable", "roof-plane"}
    for name, (scene, _sec) in scenes.items():
        missing = sorted({s["class"] for s in scene["solids"] if "level" not in s})
        assert set(missing) <= ABOVE, (
            f"{name}: {missing} stand on a storey and do not say which")
        got = [s for s in scene["solids"] if s["class"] in ("muntin", "sash", "opening-frame")]
        assert got and all("level" in s for s in got), (
            f"{name}: an opening or its dressing carries no storey")
        idx = {st["index"] for st in scene["storeys"]}
        for s in scene["solids"]:
            if "level" in s and s["level"] is not None:
                assert s["level"] in idx, f'{name}: {s["id"]} is on level {s["level"]}'
