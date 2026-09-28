"""`elevation._clearances`, DRIVEN (WP-14.6, audit F1 and F6).

What its neighbours leave an opening room to carry: a sidelight pair that would stand over the
next window is refused, and so is a shutter pair whose leaf would hang over another opening,
over another window's leaf, or past the corner of the face. REFUSED, SAID, NEVER NARROWED. The
shipped sheets reach some of this (census V20 reads the ink), but which branch fired on which
sheet is a property of one placement; here each branch is handed the face it answers, with a
control beside it that has the room, so a pass that refused everything could not pass.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

EL = modcache.load("elevation", os.path.join(ROOT, "build", "elevation.py"))
LEAF = 17.5


def _win(x0, room, leaf=LEAF, sill=30.0, head=110.0, w=36.0):
    return {"kind": "window", "room": room, "x0_in": x0, "x1_in": x0 + w, "sill_in": sill,
            "head_in": head, "shutter_leaf_width_in": leaf}


def _door(x0, w=42.0, casing=4.0, side=12.0, present=True):
    return {"kind": "door", "room": "passage", "x0_in": x0, "x1_in": x0 + w, "sill_in": 24.0,
            "head_in": 110.0, "entrance": {"casing_width_in": casing, "sidelight_width_in": side,
                                           "sidelights_present": present}}


def test_a_sidelight_that_would_stand_over_the_next_window_is_refused_and_said():
    door, win = _door(100.0), _win(60.0, "parlor")      # the window runs 60..96; the left
    EL._clearances([door, win], 400.0)                   # sidelight would run 84..96
    assert door["sidelights_drawn"] is False
    assert "the left sidelight would stand 12.0 in over parlor's window" in door["sidelights_refused"]


def test_a_sidelight_pair_with_room_is_drawn():
    door, win = _door(100.0), _win(30.0, "parlor", leaf=None)
    EL._clearances([door, win], 400.0)
    assert door["sidelights_drawn"] is True and "sidelights_refused" not in door


def test_the_pair_goes_together_and_a_window_on_another_storey_is_no_obstacle():
    """The width cap composes both sidelights or neither, so a clash on one side refuses both;
    and an opening whose sill stands above the door's head is not beside it at all."""
    door = _door(100.0)
    upstairs = _win(60.0, "chamber", sill=140.0, head=210.0)
    EL._clearances([door, upstairs], 400.0)
    assert door["sidelights_drawn"] is True
    door2 = _door(100.0)
    EL._clearances([door2, _win(60.0, "parlor")], 400.0)
    assert door2["sidelights_drawn"] is False           # both, though only the left clashed


def test_a_leaf_that_would_hang_over_the_next_windows_glass_is_refused_with_the_rules_width_kept():
    a, b = _win(20.0, "parlor"), _win(70.0, "dining")    # a's right leaf runs 56..73.5
    EL._clearances([a, b], 400.0)
    assert a["shutter_leaf_width_in"] is None and a["shutter_leaf_width_refused_in"] == LEAF
    assert "a 17.5 in leaf would lie 3.5 in over dining's window" in a["shutters_refused"]
    assert b["shutter_leaf_width_in"] is None             # and b's left leaf over a's glass


def test_two_windows_leaves_meeting_in_a_narrow_pier_are_both_refused():
    a, b = _win(20.0, "parlor"), _win(80.0, "dining")    # a 24 in pier holds one leaf, not two
    EL._clearances([a, b], 400.0)
    assert "would lie over one another in a 24.0 in pier" in a["shutters_refused"]
    assert b["shutter_leaf_width_in"] is None


def test_a_leaf_that_would_hang_past_the_corner_is_refused():
    a = _win(5.0, "parlor")                              # its left leaf would start at -12.5
    EL._clearances([a], 200.0)
    assert "a leaf would hang past the corner of the face" in a["shutters_refused"]


def test_pairs_with_wall_to_swing_onto_are_kept_as_the_rule_sizes_them():
    a, b = _win(40.0, "parlor"), _win(140.0, "dining")
    EL._clearances([a, b], 300.0)
    assert a["shutter_leaf_width_in"] == LEAF and b["shutter_leaf_width_in"] == LEAF
    assert "shutters_refused" not in a and "shutters_refused" not in b


def test_a_leaf_is_held_to_the_doorcase_as_composed_not_to_the_bare_door():
    """A shutter beside the entrance must clear the casing AND the sidelights where they are
    drawn, and only the casing where they are not."""
    door = _door(100.0)                                  # casing 96..146, sidelights 84..158
    win = _win(170.0, "dining")                          # its left leaf would run 152.5..170
    EL._clearances([door, win], 400.0)
    assert door["sidelights_drawn"] is True
    assert "over passage's door" in win["shutters_refused"]
    door2, win2 = _door(100.0, present=False), _win(170.0, "dining")
    EL._clearances([door2, win2], 400.0)                  # casing alone ends at 146
    assert win2["shutter_leaf_width_in"] == LEAF


# ------------------------------------------------------------------ WP-14.6's second audit
# Each branch below was shown BLIND by a mutation before its test existed: the whole of this file,
# `tests/test_opening_rects.py` and census V20 stayed green under it.
#
# A refusal is read by WHAT it names, never by its whole sentence: the reason prose is the only
# record of the class on this tree, and a reworded tail is not a regression. Where a window's rect
# carries `shutters_refused_by` -- the classes the record states -- the class is read as well.

def _corner_only(reason, side=None):
    """The one refusal a lone opening can meet at the end of its wall: the corner, and nothing
    else joined to it."""
    return (bool(reason) and "; " not in reason and "past the corner" in reason
            and (side is None or side in reason))


def _classes(rect, want):
    """Where the record states its classes of refusal, they are `want`; where it states none, the
    reason prose has been read instead and this adds nothing."""
    got = rect.get("shutters_refused_by")
    return got is None or sorted(got) == sorted(want)

def test_a_leaf_is_held_to_the_sidelights_drawn_and_not_to_the_sidelights_composed():
    """M1. A shutter beside the entrance clears the doorcase AS DRAWN, and a sidelight pair the
    placement refused is not drawn: holding the leaf to the pair the composition merely PRESENTS
    refuses a leaf that has its wall. The test above varies `sidelights_present`, and there the
    pair drawn and the pair composed coincide, so reading the wrong one of the two passed it."""
    door = _door(100.0)                      # casing 96..146; the pair, were it drawn, 84..158
    obstacle = _win(60.0, "passage", leaf=None, w=30.0)   # 60..90: the left sidelight's 84..96
    beside = _win(165.0, "dining")           # its left leaf runs 147.5..165: clear of 146, not of 158
    EL._clearances([door, obstacle, beside], 400.0)
    assert door["sidelights_drawn"] is False and "passage" in door["sidelights_refused"], door.get(
        "sidelights_refused")
    assert beside["shutter_leaf_width_in"] == LEAF and "shutters_refused" not in beside, beside.get(
        "shutters_refused")


def test_a_sidelight_past_either_corner_of_the_face_is_refused_and_said():
    """M2. The sidelight's own corner branch: a door 10 in from the face's left edge (casing 4,
    sidelight 12) would stand its left sidelight at -6..6 in, and one 10 in from the right edge its
    right sidelight past the face. Nothing else stands on either face, so the corner is the only
    reason, and a door the face has room for is the control."""
    left = _door(10.0)
    EL._clearances([left], 400.0)
    assert left["sidelights_drawn"] is False
    assert _corner_only(left["sidelights_refused"], "left"), left["sidelights_refused"]
    right = _door(400.0 - 42.0 - 10.0)       # 348..390; its right sidelight 394..406 on a 400 in face
    EL._clearances([right], 400.0)
    assert right["sidelights_drawn"] is False
    assert _corner_only(right["sidelights_refused"], "right"), right["sidelights_refused"]
    room = _door(100.0)
    EL._clearances([room], 400.0)
    assert room["sidelights_drawn"] is True and "sidelights_refused" not in room


def test_leaves_that_meet_exactly_are_kept_and_so_is_a_leaf_that_meets_an_opening():
    """M3's control. A leaf that ENDS where the next thing begins does not lie over it: two windows'
    leaves meeting in a pier exactly two leaves wide, and a leaf ending at the jamb of an opening
    that carries none, are both hung. Loosening the overlap test by any margin refuses them."""
    a, b = _win(20.0, "parlor"), _win(91.0, "dining")    # 56..73.5 and 73.5..91 meet at 73.5
    EL._clearances([a, b], 400.0)
    assert a["shutter_leaf_width_in"] == LEAF and b["shutter_leaf_width_in"] == LEAF, (
        a.get("shutters_refused"), b.get("shutters_refused"))
    c, d = _win(20.0, "parlor"), _win(73.5, "closet", leaf=None)   # c's leaf ends on d's jamb
    EL._clearances([c, d], 400.0)
    assert c["shutter_leaf_width_in"] == LEAF, c.get("shutters_refused")


def test_the_leaf_refusal_is_decided_before_any_leaf_is_withdrawn_and_says_so():
    """M3's chain, MEASURED AND NOT RULED. Three windows in a row with 24 in and 30 in piers: A's
    and B's leaves meet in the first pier (11 in over one another), so both are refused. C's left
    leaf meets B's right leaf in the second (5 in over) -- and B's leaves are not drawn, so on the
    sheet C's leaf would hang against bare wall. `_clearances` decides every refusal against the
    leaves as COMPOSED, before any is withdrawn, so C is refused for a leaf that is not drawn.

    That is an over-refusal of one reading and the correct refusal of another: withdraw in one
    pass and the answer depends on the order the windows are read, which is a question for a
    ruling and not for this file (reported, WP-14.6's second audit, §XII). What is asserted here is
    the stated reason: C's refusal names B's leaves, and only B's, so a reader can see it was B's
    leaves and not C's wall. If a ruling makes the refusal one-pass, this test changes WITH the
    ruling and says which order it reads."""
    a, b, c = _win(20.0, "parlor"), _win(80.0, "dining"), _win(146.0, "study")
    EL._clearances([a, b, c], 400.0)
    assert a["shutter_leaf_width_in"] is None and b["shutter_leaf_width_in"] is None
    assert c["shutter_leaf_width_in"] is None
    reason = c["shutters_refused"]
    assert "dining" in reason and "parlor" not in reason and "; " not in reason, reason
    assert _classes(c, ["leaf"]), c.get("shutters_refused_by")


# ------------------------------------------------------------------ the join, through `opening_rects`
# M2's second half. `opening_rects` hands `_clearances` the face's own `outside_width_in`, and the
# corner branches read nothing else: called without it, every corner refusal on every sheet goes
# silently unjudged -- a leaf hung in the air past the end of the wall, drawn -- and the unit tests
# above, which call `_clearances` directly with a width, cannot see the join. These drive the real
# call on a real face, alone on it, so the corner is the only thing the opening can meet.

import copy  # noqa: E402
import json  # noqa: E402

import pytest  # noqa: E402


def _m(name):
    return modcache.load(name, os.path.join(ROOT, "build", name + ".py"))


@pytest.fixture(scope="module")
def elevations():
    G, ST, RF = _m("geometry"), _m("structure"), _m("roof")
    out = {}
    for name in ("spec-builder-colonial", "tidewater-georgian-careful"):
        plan = json.load(open(os.path.join(ROOT, "plans", name + ".json")))
        placed = G.solve(copy.deepcopy(plan), engine="heuristic")
        sec = ST.build_section(placed, None, geometry_result=placed)
        rf = RF.build_roof(placed, None, section=sec)
        out[name] = EL.build_elevation(placed, None, section=sec, roof=rf)
    return out


def _alone(el, face, p, x0_in):
    """The elevation with `p` the only opening on `face`, its left jamb at `x0_in`."""
    el = copy.deepcopy(el)
    fr = el["faces"][face]
    q = dict(p, cx_in=x0_in + p["width_in"] / 2.0)
    fr["placed"], fr["placed_refused"], fr["stack_axes_ft"] = [q], [], []
    assert fr.get("outside_width_in"), "the premise: the face states its width"
    return el


def test_a_leaf_past_the_corner_is_refused_through_opening_rects(elevations):
    el = elevations["spec-builder-colonial"]
    face = next(f for f in "SNEW" if any(r.get("shutter_leaf_width_in") for r in EL.opening_rects(el, f)["rects"]))
    p = next(x for x in el["faces"][face]["placed"] if x["kind"] == "window")
    clear = EL.opening_rects(_alone(el, face, p, 40.0), face)["rects"]
    assert len(clear) == 1 and clear[0]["shutter_leaf_width_in"], "the control: 40 in from the corner holds a leaf"
    got = EL.opening_rects(_alone(el, face, p, 5.0), face)["rects"]
    assert len(got) == 1 and got[0]["shutter_leaf_width_in"] is None, got
    assert _corner_only(got[0]["shutters_refused"]), got[0]["shutters_refused"]
    assert _classes(got[0], ["corner"]), got[0].get("shutters_refused_by")


def test_a_sidelight_past_the_corner_is_refused_through_opening_rects(elevations):
    el = elevations["tidewater-georgian-careful"]
    face = el["entrance_face"]
    ent = el.get("entrance") or {}
    assert ent.get("sidelights_present") and ent.get("sidelight_width_in"), (
        "the premise: this entrance composes a sidelight pair")
    p = next(x for x in el["faces"][face]["placed"] if x["kind"] == "door" and x.get("entrance"))
    clear = [r for r in EL.opening_rects(_alone(el, face, p, 120.0), face)["rects"] if r["kind"] == "door"]
    assert clear and clear[0]["sidelights_drawn"] is True, "the control: 120 in from the corner holds the pair"
    got = [r for r in EL.opening_rects(_alone(el, face, p, 10.0), face)["rects"] if r["kind"] == "door"]
    assert got and got[0]["sidelights_drawn"] is False, got
    assert _corner_only(got[0]["sidelights_refused"], "left"), got[0]["sidelights_refused"]


def test_a_corner_nobody_measured_is_unjudged_and_not_a_pass():
    """AUDIT, 27 SEP 2026 (the second auditor's latent find). With no face width the corner test
    was skipped in silence, so a leaf or a sidelight past the corner read as clear of it. The
    same openings with a width are the control: there the corner refuses them."""
    leaf, door = _win(5.0, "parlor"), _door(10.0)          # each past the left corner of any face
    EL._clearances([leaf], 200.0)
    EL._clearances([door], 400.0)
    assert "corner" in leaf["shutters_refused_by"] and door["sidelights_drawn"] is False, (
        "the premise: with a width, the corner refuses both")
    assert "shutters_corner_unjudged" not in leaf and "sidelights_corner_unjudged" not in door
    leaf, door = _win(5.0, "parlor"), _door(10.0)
    EL._clearances([leaf], None)
    EL._clearances([door], None)
    assert leaf["shutters_corner_unjudged"] == EL.CORNER_UNJUDGED
    assert door["sidelights_corner_unjudged"] == EL.CORNER_UNJUDGED
    assert "not a pass" in EL.CORNER_UNJUDGED


def test_the_sheet_says_a_corner_nobody_measured(tmp_path):
    """The record's flag reaches the plate. DRIVEN: every shipped face states its width, so the
    width is withdrawn by hand from one real elevation; the same face with its width is the
    control and says nothing."""
    import copy
    import json
    G, ST, RF = (modcache.load(n, os.path.join(ROOT, "build", n + ".py")) for n in ("geometry", "structure", "roof"))
    RE = modcache.load("render_elevation", os.path.join(ROOT, "build", "render_elevation.py"))
    saved = G._SOLVE_CACHE
    G._SOLVE_CACHE = {}
    try:
        p = G.solve(json.load(open(os.path.join(ROOT, "plans", "spec-builder-colonial.json"))), engine="heuristic")
    finally:
        G._SOLVE_CACHE = saved
    sec = ST.build_section(p, None, geometry_result=p)
    el = EL.build_elevation(p, None, section=sec, roof=RF.build_roof(p, None, section=sec))
    face = el["entrance_face"]
    said = {}
    for tag, width in (("measured", el["faces"][face]["outside_width_in"]), ("unmeasured", None)):
        e = copy.deepcopy(el)
        e["faces"][face]["outside_width_in"] = width
        out = str(tmp_path / f"{tag}.svg")
        RE.render_elevation(e, out, face=face)
        said[tag] = "CORNER CLEARANCE NOT JUDGED ON" in open(out, encoding="utf-8").read()
    assert said == {"measured": False, "unmeasured": True}, said
