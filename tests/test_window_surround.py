"""The window surround a kit names and the record cannot decide is said, not chosen (WP-14.3).

The plan for WP-14.3 said a window casing is drawn wherever the resolved surround variant states
one. Measured over the 41 styles the elevation draws, the record states none it can draw: 22 make
an architrave AND a bare opening both canonical, so they do not say which this house has, and 19
make no surround canonical. The first is refused with its reason on the plate and in the model,
the transom's precedent for a record that names two forms; the second is the ordinary answer and
is not said. The reveal is its own slot and is drawn where it is stated.
"""
import copy
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import modcache as mc  # noqa: E402
import inkread as IR  # noqa: E402


def _m(name):
    return mc.load(name, os.path.join(ROOT, "build", name + ".py"))


@pytest.fixture(scope="module")
def built():
    G, ST, RF, EL = _m("geometry"), _m("structure"), _m("roof"), _m("elevation")
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    placed = G.solve(copy.deepcopy(plan), engine="heuristic")
    sec = ST.build_section(placed, None, geometry_result=placed)
    rf = RF.build_roof(placed, None, section=sec)
    return placed, sec, rf, EL.build_elevation(placed, None, section=sec, roof=rf)


def test_the_premise_the_kit_names_two_surrounds(built):
    RK = _m("resolve_kit")
    g = RK.load_graph()
    slots, _ = RK.resolve_slots(g, RK.chain_for(g, "tidewater-georgian"),
                                RK.scope_for(g, "tidewater-georgian"))
    canon = sorted(v["id"] for v in slots["window_surround_masonry"]["variants"]
                   if v.get("status") == "canonical")
    assert canon == ["flat-architrave-with-crown", "none-masonry-reveal"], canon


def test_the_record_refuses_the_choice_and_names_both(built):
    ws = built[3]["window_surround"]
    assert ws["drawn"] is False
    assert "flat architrave with crown" in ws["why"] and "none masonry reveal" in ws["why"]


def test_the_plate_and_the_model_both_say_it(built, tmp_path):
    placed, sec, rf, el = built
    RE, SC = _m("render_elevation"), _m("scene")
    out = str(tmp_path / "S.svg")
    RE.render_elevation(el, out, face="S")
    said = " ".join(t for t, _a, _i in IR.Ink(open(out).read()).texts()).upper()
    assert "WINDOW SURROUND NOT DRAWN" in said and "FLAT ARCHITRAVE WITH CROWN" in said
    scene = SC.build_scene(placed, sec, rf, el)
    assert [c for c in scene["not_modelled"] if c["what"] == "the window surrounds"]


@pytest.mark.parametrize("variants,binding,expect", [
    ([("flat-architrave-with-crown", "canonical")], "specified", "no surface"),
    ([("none-masonry-reveal", "canonical")], "specified", None),
    ([("flat-architrave-with-crown", "permitted")], "specified", None),
    ([("flat-architrave-with-crown", "canonical")], "forbidden", None),
    ([("a-casing", "canonical"), ("b-casing", "canonical"), ("none-plain", "canonical")],
     "specified", "all canonical"),
])
def test_each_state_of_the_slot_is_its_own_answer(variants, binding, expect):
    """DRIVEN: every drawn style is one of two states, so the other three are unreachable."""
    EL = _m("elevation")
    slot = {"binding": binding, "variants": [{"id": i, "status": s} for i, s in variants]}
    ws = EL.window_surround(slot)
    assert ws["drawn"] is False
    if expect is None:
        assert ws["why"] is None
    else:
        assert expect in ws["why"], ws["why"]


MASONRY_ONLY = {"id": "none-masonry-reveal", "status": "canonical",
                "applies_when": {"construction": ["solid-masonry-two-wythe"]}}
ARCHITRAVE = {"id": "flat-architrave-with-crown", "status": "canonical"}


def test_a_variant_whose_own_condition_fails_is_not_canonical_for_this_house():
    """WP-14.6, audit F9. `georgian-colonial-american` makes the bare masonry reveal canonical
    only `applies_when` the wall is solid masonry, and the cascade carries it into the WOOD slot
    with that condition. Unread, a frame house was told its kit names two surrounds "and does not
    say which" -- the frame `good-03` and `good-05`, on the shipped plans. On a frame wall the
    reveal does not apply and the architrave is named alone; on the masonry wall it was written
    for, both are canonical and the choice is still refused."""
    EL = _m("elevation")
    slot = {"binding": "specified", "variants": [dict(ARCHITRAVE), dict(MASONRY_ONLY)]}
    frame = EL.window_surround(slot, "window_surround_wood", construction="platform-frame")
    assert frame["canonical"] == ["flat-architrave-with-crown"] and "is canonical" in frame["why"]
    brick = EL.window_surround(slot, "window_surround_wood", construction="solid-masonry-two-wythe")
    assert brick["canonical"] == ["flat-architrave-with-crown", "none-masonry-reveal"]
    assert "both canonical" in brick["why"]
    # a house that states no construction has not failed the condition: unjudged is not refused
    unstated = EL.window_surround(slot, "window_surround_wood")
    assert "both canonical" in unstated["why"]


def test_a_variant_outside_its_own_date_range_is_not_canonical_at_that_date():
    """`new-england-colonial`'s flat casing is canonical for 1700-1780 and not after; the
    resolver's own `in_period` reads the date, so the two layers cannot disagree about it."""
    EL = _m("elevation")
    dated = {"id": "flat-casing", "status": "canonical", "applies_when": {"date_range": [1700, 1780]}}
    slot = {"binding": "specified", "variants": [dated]}
    assert EL.window_surround(slot, date=1765)["canonical"] == ["flat-casing"]
    assert EL.window_surround(slot, date=1850)["canonical"] == []
    assert EL.window_surround(slot)["canonical"] == ["flat-casing"]


def test_the_shipped_frame_plans_are_told_the_surround_their_kit_names():
    """The premise that makes the two drives above a statement about the corpus: `good-03`'s
    frame wall reaches the masonry-only condition through `greek-revival-american`'s cascade."""
    G, ST, RF, EL = _m("geometry"), _m("structure"), _m("roof"), _m("elevation")
    plan = json.load(open(os.path.join(ROOT, "plans", "reference", "good-03-parlor-drawing-room-house.json")))
    placed = G.solve(copy.deepcopy(plan), engine="heuristic")
    sec = ST.build_section(placed, None, geometry_result=placed)
    assert sec["wall"]["construction_type"] != "solid-masonry-two-wythe", "premise: a frame wall"
    el = EL.build_elevation(placed, None, section=sec, roof=RF.build_roof(placed, None, section=sec))
    assert el["window_surround"]["canonical"] == ["flat-architrave-with-crown"], el["window_surround"]
