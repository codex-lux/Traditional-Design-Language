"""Every branch of `elevation.entrance_transom`, DRIVEN (WP-14.6, auditor C).

The corpus reaches two of its six branches: the Tidewater family's canonical rectangular transom,
drawn, and the many kits that make none. The rest -- a slot the kit FORBIDS, two forms named at
once, a fanlight, a composition that states no height -- are reached by no shipped plan, and a
mutation deleting the forbidden-slot branch left every test green. A guard that runs only where
the bug cannot occur is not a guard, so each branch is handed the record it answers.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

EL = modcache.load("elevation", os.path.join(ROOT, "build", "elevation.py"))
PE = modcache.load("proportion_engine", os.path.join(ROOT, "build", "proportion_engine.py"))
SASH = PE.resolve("sash-light")
RECT = "rectangular-multi-light-transom"


def _slot(*canonical, binding="specified"):
    return {"binding": binding, "variants": [{"id": v, "status": "canonical"} for v in canonical]}


def _ent(**kw):
    e = {"transom_height_in": 18.0, "door_leaf_width_in": 42.0, "sidelights_forbidden_by_kit": False}
    e.update(kw)
    return e


def test_premise_the_rectangular_form_is_one_this_generator_draws():
    assert RECT in EL.TRANSOM_DRAWN_FORMS


def test_a_canonical_rectangular_transom_is_drawn_at_its_judged_height_with_the_packs_lights():
    t = EL.entrance_transom(_ent(), _slot(RECT), SASH, 10.5)
    assert t["drawn"] and t["variant"] == RECT and t["judgment"] is True
    assert (t["height_in"], t["width_in"]) == (18.0, 42.0)
    want, _r = EL._val(SASH, "transom_sidelight", {"opening_width": 42.0, "module": 10.5}, dimension="count")
    assert t["lights"] == int(round(want))


def test_a_slot_the_kit_forbids_draws_no_transom_whatever_its_variants_say():
    """The branch the audit found unguarded. `transom_sidelight` holds the sidelights AND the
    transom, and a kit binding it forbidden has no transom -- even where a canonical form is still
    listed under the forbidden binding, which is the case that tells this branch from the next."""
    t = EL.entrance_transom(_ent(sidelights_forbidden_by_kit=True), _slot(RECT), SASH, 10.5)
    assert t == {"variant": None, "drawn": False, "why": None}, t


def test_a_kit_naming_no_transom_draws_none_and_says_nothing():
    t = EL.entrance_transom(_ent(), _slot("sidelights-full-height"), SASH, 10.5)
    assert t == {"variant": None, "drawn": False, "why": None}


def test_two_canonical_forms_are_refused_naming_both():
    t = EL.entrance_transom(_ent(), _slot(RECT, "elliptical-fanlight"), SASH, 10.5)
    assert not t["drawn"] and t["canonical"] == sorted([RECT, "elliptical-fanlight"])
    assert "2 transom forms canonical" in t["why"] and "names none" in t["why"]


def test_a_fanlight_is_refused_because_no_record_states_its_rise():
    t = EL.entrance_transom(_ent(), _slot("elliptical-fanlight"), SASH, 10.5)
    assert not t["drawn"] and t["variant"] == "elliptical-fanlight"
    assert "states its rise" in t["why"] and t["why"].startswith("an elliptical fanlight")


def test_a_composition_stating_no_height_is_refused_and_not_drawn_at_a_default():
    for ent, gm in ((_ent(transom_height_in=None), 10.5), (_ent(door_leaf_width_in=None), 10.5), (_ent(), None)):
        t = EL.entrance_transom(ent, _slot(RECT), SASH, gm)
        assert not t["drawn"] and "states no transom height" in t["why"], t
