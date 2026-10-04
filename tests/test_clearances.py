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


def test_of_two_windows_whose_leaves_meet_in_a_narrow_pier_one_keeps_them():
    """RE-CUT 1 OCT 2026 (WP-16.7, R7): this was `..._are_both_refused`. A 24 in pier holds one leaf,
    not two, so one of the pair keeps its leaves: with no entrance on the face the centre of
    composition is the face's own, at 200 in, and dining's window (centre 98 in) is nearer it than
    parlor's (38 in)."""
    a, b = _win(20.0, "parlor"), _win(80.0, "dining")    # a 24 in pier holds one leaf, not two
    EL._clearances([a, b], 400.0)
    assert "would lie over one another in a 24.0 in pier" in a["shutters_refused"]
    assert b["shutter_leaf_width_in"] == LEAF and "shutters_refused" not in b, b.get("shutters_refused")
    assert a["shutters_decided_by"] == b["shutters_decided_by"] == "outward"


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


def test_the_largest_set_that_can_all_be_hung_is_hung_and_the_window_between_names_both():
    """RE-CUT 1 OCT 2026 (WP-16.7, R7). This was `..._is_decided_before_any_leaf_is_withdrawn_and_
    says_so`, which pinned the reading before the ruling and said it would change WITH the ruling:
    three windows in a row with 24 in and 30 in piers, A's and B's leaves meeting in the first, B's
    and C's in the second, and every refusal decided against the leaves AS COMPOSED, so C lost its
    leaves to B's, which were not drawn. Lucas ruled (29 Sep 2026): a refused pair no longer blocks
    its neighbour, and the largest set that can all be hung is hung. That is A and C; B is refused,
    and its refusal names both, because both are hung. No tie-break is needed: no other set holds
    two, so the count decides each of the three."""
    a, b, c = _win(20.0, "parlor"), _win(80.0, "dining"), _win(146.0, "study")
    EL._clearances([a, b, c], 400.0)
    assert a["shutter_leaf_width_in"] == LEAF and c["shutter_leaf_width_in"] == LEAF, (
        a.get("shutters_refused"), c.get("shutters_refused"))
    assert b["shutter_leaf_width_in"] is None
    reason = b["shutters_refused"]
    assert "parlor" in reason and "study" in reason, reason
    assert _classes(b, ["leaf"]), b.get("shutters_refused_by")
    assert {x["shutters_decided_by"] for x in (a, b, c)} == {"count"}


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
    # THE SPEC COLONIAL SINCE WP-16.4 (30 Sep 2026). The Tidewater entrance composed its pair until
    # the kit's own ban was read at the house's 1765 (georgian-colonial-american forbids the
    # sidelights for 1700-1780), so it composes none now and this premise went false; the spec
    # Colonial composes and draws its pair, and the corner is the same question on either front.
    el = elevations["spec-builder-colonial"]
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

# ------------------------------------------------------------------ R7, ruled 29 Sep 2026 (WP-16.7)
# "A refused pair no longer blocks its neighbour. Among equally good sets, prefer one symmetric
# about the front's centre line, then work outward from the entrance." Each key is driven alone
# here, on a face built so that it and no other key decides, with the control beside it. The
# shipped sheets reach almost none of this: since WP-16.6 seats two windows at least the wider
# window's width apart, a wall that wide holds both neighbours' half-width leaves.

def test_a_hard_refused_pair_no_longer_blocks_its_neighbour():
    """A window whose leaf would lie over an opening keeps no leaves in any set, and its leaves
    stand in nobody's way: the neighbour whose leaves would only have met them keeps its own. Under
    the rule before WP-16.7 the neighbour was refused for leaves that are not drawn."""
    beside = _win(66.0, "parlor")                     # 66..102; its right leaf 102..119.5
    hard = _win(120.0, "dining")                      # 120..156; its right leaf 156..173.5 meets
    closet = _win(160.0, "closet", leaf=None, w=10.0)  # the closet's glass, 160..170
    EL._clearances([beside, hard, closet], 400.0)
    assert hard["shutter_leaf_width_in"] is None and "opening" in hard["shutters_refused_by"]
    assert beside["shutter_leaf_width_in"] == LEAF and "shutters_refused" not in beside, beside.get(
        "shutters_refused")
    # the hard-refused window's leaves would lie over beside's, which ARE hung, and it says so
    assert "parlor" in hard["shutters_refused"] and "leaf" in hard["shutters_refused_by"]


def test_symmetry_decides_between_two_equal_sets():
    """Two windows 24 in apart on the left of a 400 in face, one of which must lose its leaves; the
    left one's mirror stands free on the right and keeps its own. Keeping the left one leaves the
    front symmetric about its centre line; keeping the inner one -- the one nearer the face's
    centre, which the outward key alone would keep -- leaves the right window's leaves unanswered.
    Symmetry is the earlier key, so the left one keeps its leaves."""
    l1, l2 = _win(40.0, "parlor"), _win(100.0, "dining")   # centres 58 and 118; 24 in pier
    r1 = _win(330.0, "chamber")      # centre 348, 6 in off 400 - 58: l1's mirror within a foot
    EL._clearances([l1, l2, r1], 400.0)
    assert l1["shutter_leaf_width_in"] == LEAF and r1["shutter_leaf_width_in"] == LEAF
    assert l2["shutter_leaf_width_in"] is None
    assert l1["shutters_decided_by"] == l2["shutters_decided_by"] == "symmetry"
    assert "symmetric about the face's centre line" in l2["shutters_refused"], l2["shutters_refused"]
    assert "parlor" in l2["shutters_refused"]
    # the control: with no mirror on the right, the outward key decides and the inner one keeps them
    m1, m2 = _win(40.0, "parlor"), _win(100.0, "dining")
    EL._clearances([m1, m2], 400.0)
    assert m2["shutter_leaf_width_in"] == LEAF and m1["shutter_leaf_width_in"] is None
    assert m1["shutters_decided_by"] == "outward"


def test_the_mirror_tolerance_is_axis_own(monkeypatch):
    """ONE SPELLING (R7's reading, recorded beside the ruling): a mirror pair is read at
    `axis.MIRROR_TOL_FT`, the tolerance `axis.mirror` judges the front with. The face above, with
    its right window 6 in off l1's reflection, is a pair at a foot and no pair at a tenth of one,
    and then the outward key decides instead."""
    AX = modcache.load("axis", os.path.join(ROOT, "build", "axis.py"))
    assert AX.MIRROR_TOL_FT == 1.0
    monkeypatch.setattr(AX, "MIRROR_TOL_FT", 0.1)
    l1, l2, r1 = _win(40.0, "parlor"), _win(100.0, "dining"), _win(330.0, "chamber")
    EL._clearances([l1, l2, r1], 400.0)
    assert l2["shutter_leaf_width_in"] == LEAF and l1["shutter_leaf_width_in"] is None
    assert l1["shutters_decided_by"] == "outward"


def test_a_symmetric_front_keeps_its_outer_pair_and_names_only_the_hung():
    """Four windows in a row about the face's centre, every pier too narrow for two leaves. The
    two largest sets nearest the centre each keep one inner and one outer window and break both
    mirror pairs; keeping the two OUTER windows breaks none. Symmetry outranks the outward key, so
    the outer pair keeps its leaves -- and each inner window's refusal names the outer neighbour
    whose leaves are hung, never the inner one beside it, whose are not."""
    a, b = _win(92.0, "parlor"), _win(152.0, "dining")      # centres 110 and 170
    c, d = _win(212.0, "study"), _win(272.0, "library")     # centres 230 and 290: the mirrors
    EL._clearances([a, b, c, d], 400.0)
    assert [w["shutter_leaf_width_in"] for w in (a, b, c, d)] == [LEAF, None, None, LEAF]
    assert {w["shutters_decided_by"] for w in (a, b, c, d)} == {"symmetry"}
    assert "parlor" in b["shutters_refused"] and "study" not in b["shutters_refused"], b["shutters_refused"]
    assert "library" in c["shutters_refused"] and "dining" not in c["shutters_refused"], c["shutters_refused"]


def test_the_entrance_is_the_centre_of_composition_where_one_is_drawn():
    """Two windows 24 in apart between the entrance at the left of the face and the face's centre:
    the one nearer the entrance keeps its leaves, though the other is nearer the face's centre.
    The same two windows with no door on the face are the control: there the face's centre decides
    the other way."""
    door = _door(20.0)                                  # 20..62; its pair drawn 4..20 and 62..78
    w1, w2 = _win(100.0, "parlor"), _win(160.0, "dining")   # centres 118 and 178
    EL._clearances([door, w1, w2], 400.0)
    assert door["sidelights_drawn"] is True
    assert w1["shutter_leaf_width_in"] == LEAF and w2["shutter_leaf_width_in"] is None
    assert w2["shutters_decided_by"] == "outward" and "nearest the entrance" in w2["shutters_refused"]
    v1, v2 = _win(100.0, "parlor"), _win(160.0, "dining")
    EL._clearances([v1, v2], 400.0)
    assert v2["shutter_leaf_width_in"] == LEAF and v1["shutter_leaf_width_in"] is None
    assert "nearest the face's centre" in v1["shutters_refused"]


def test_a_garage_door_is_no_entrance_and_the_face_centre_holds():
    """U4's reading, the placer's own (`openings.window_centres`): a garage door is no entrance."""
    garage = dict(_door(20.0, w=96.0), type="garage-door")
    w1, w2 = _win(140.0, "parlor"), _win(200.0, "dining")   # centres 158 and 218; 24 in pier
    EL._clearances([garage, w1, w2], 400.0)
    assert EL.composition_centre([garage, w1, w2], 400.0) == (200.0, "the face's centre")
    assert w2["shutter_leaf_width_in"] == LEAF and w1["shutter_leaf_width_in"] is None


def test_where_no_key_decides_the_order_along_the_face_does_and_says_it_is_no_ruling():
    """Two windows mirrored about the face's centre and too close to hang both: whichever keeps its
    leaves breaks the mirror, both stand at one distance from the centre, and the ruling has
    nothing left to decide with. The order along the face decides -- the left one as drawn -- and
    the refusal says the key is for determinism alone."""
    a, b = _win(150.0, "parlor"), _win(214.0, "dining")     # centres 168 and 232; 28 in pier
    EL._clearances([a, b], 400.0)
    assert a["shutter_leaf_width_in"] == LEAF and b["shutter_leaf_width_in"] is None
    assert a["shutters_decided_by"] == b["shutters_decided_by"] == "face-order"
    assert "which no ruling states" in b["shutters_refused"], b["shutters_refused"]


def test_two_windows_on_two_storeys_are_not_each_others_mirror():
    """A mirror pair stands on one storey. A window at the mirror position one storey up is no
    twin; the same position on the same storey is."""
    a = dict(_win(150.0, "parlor"), storey="ground")                                   # centre 168
    up = dict(_win(214.0, "chamber", sill=140.0, head=210.0), storey="upper")          # centre 232
    assert EL._mirror_twins([a, up], 400.0, 12.0) == {}
    b = dict(_win(214.0, "dining"), storey="ground")
    assert EL._mirror_twins([a, up, b], 400.0, 12.0) == {id(a): id(b), id(b): id(a)}


def test_past_the_bound_the_group_is_refused_as_composed_and_says_so(monkeypatch):
    """U7. The search enumerates every set of a group, so a group is bounded; past the bound
    nothing is chosen and every pair in it is refused as composed, the rule before WP-16.7, under
    its own class, so no sheet can say a hung neighbour that is not there. The same face inside the
    bound is the control."""
    row = [_win(20.0, "parlor"), _win(80.0, "dining"), _win(146.0, "study")]
    EL._clearances(row, 400.0)
    assert [w["shutter_leaf_width_in"] for w in row] == [LEAF, None, LEAF]
    monkeypatch.setattr(EL, "SHUTTER_GROUP_BOUND", 2)
    row = [_win(20.0, "parlor"), _win(80.0, "dining"), _win(146.0, "study")]
    EL._clearances(row, 400.0)
    assert [w["shutter_leaf_width_in"] for w in row] == [None, None, None]
    assert all(w["shutters_refused_by"] == ["bound"] and w["shutters_decided_by"] == "bound" for w in row)
    assert "was not searched" in row[1]["shutters_refused"] and "parlor" in row[1]["shutters_refused"]


def test_a_face_with_no_width_has_no_centre_line_and_says_its_symmetry_is_not_judged():
    """With no width there is no centre line and, where no entrance is drawn, no centre of
    composition. Where more than one largest set exists the choice falls through to the order along
    the face, and every window the symmetry could have decided carries the reason it was not
    judged -- not a pass. A face with its width is the control."""
    a, b = _win(150.0, "parlor"), _win(214.0, "dining")
    EL._clearances([a, b], None)
    assert a["shutters_decided_by"] == b["shutters_decided_by"] == "face-order"
    assert a["shutters_symmetry_unjudged"] == b["shutters_symmetry_unjudged"] == EL.SYMMETRY_UNJUDGED
    assert "not a pass" in EL.SYMMETRY_UNJUDGED
    assert "no centre to read" in b["shutters_refused"]
    c, d = _win(150.0, "parlor"), _win(214.0, "dining")
    EL._clearances([c, d], 400.0)
    assert "shutters_symmetry_unjudged" not in c and "shutters_symmetry_unjudged" not in d


def _mirrored_pair(el, leaves):
    """`el` with one face's openings replaced by two copies of one of its windows, mirrored about
    the face's centre with a pier `leaves` of its leaf widths between them: a pair the ruled keys
    cannot choose between. Between one leaf and two the pair contends; at one leaf or less each
    leaf reaches the other window's glass, which refuses both in any set."""
    face = next(f for f in "SNEW" if any(r.get("shutter_leaf_width_in")
                                         for r in EL.opening_rects(el, f)["rects"]))
    leaf = next(r["shutter_leaf_width_in"] for r in EL.opening_rects(el, face)["rects"]
                if r.get("shutter_leaf_width_in"))
    el = copy.deepcopy(el)
    fr = el["faces"][face]
    p = next(x for x in fr["placed"] if x["kind"] == "window")
    half = (p["width_in"] + leaves * leaf) / 2.0
    mid = fr["outside_width_in"] / 2.0
    fr["placed"] = [dict(p, cx_in=mid - half, n=1), dict(p, cx_in=mid + half, n=2)]
    fr["placed_refused"], fr["stack_axes_ft"] = [], []
    return el, face


def test_the_sheet_says_the_rule_and_where_the_order_along_the_face_chose(elevations):
    """The legend is the one list the sheet and the DXF both write (`face_notes`). DRIVEN, on a
    real face: two copies of one of its windows mirrored about the centre, a pier too narrow for
    both pairs of leaves. One keeps its leaves by the order along the face, which no ruling states,
    and the sheet says so, naming both rooms; the refusal's line states the rule. The same pair set
    far enough apart to hang both is the control, and says neither."""
    el, face = _mirrored_pair(elevations["spec-builder-colonial"], 1.5)
    rects = EL.opening_rects(el, face)["rects"]
    assert [r.get("shutters_decided_by") for r in rects] == ["face-order", "face-order"], [
        (r.get("shutters_decided_by"), r.get("shutters_refused_by")) for r in rects]
    notes = EL.face_notes(el, face)
    said = [n for n in notes if n.startswith("SHUTTERS CHOSEN BY ORDER ALONG THE FACE ON 2 WINDOW(S)")]
    assert len(said) == 1 and "WHICH NO RULING STATES" in said[0], notes
    total = [n for n in notes if n.startswith("SHUTTERS NOT DRAWN ON 1 WINDOW(S)")]
    assert total and "A SYMMETRIC SET FIRST, THEN THOSE NEAREST THE FACE’S CENTRE" in total[0], notes
    # and it says whose leaves are in the way: a neighbour's that ARE hung (R7), which the line
    # before WP-16.7 could not say, because the neighbour's need not have been
    assert "ITS LEAVES AND A HUNG NEIGHBOUR’S WOULD LIE OVER ONE ANOTHER" in total[0], total[0]
    ctl, face = _mirrored_pair(elevations["spec-builder-colonial"], 2.5)
    notes = EL.face_notes(ctl, face)
    assert not [n for n in notes if n.startswith(("SHUTTERS CHOSEN BY ORDER", "SHUTTERS NOT DRAWN"))], notes
