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
