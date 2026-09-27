"""WP-14.3's small fixes to the elevation plate, each DRIVEN, because the corpus reaches none of them.

- The modillion anchors subtracted the plate's PIXEL origin divided by the scale from face feet,
  which put every tooth 23 in off its bay. It was latent for as long as every band was drawn solid,
  and every band is: no cornice member in this corpus states a tooth width.
- A keystone the kit makes canonical with no stated width fell back to 0.6 x the arch's depth, and
  a chimney stack with no stated plan size to 22 in. Both are refused now, and the sheet says so.

Each test asserts its own premise, so the day the corpus reaches one of these branches the suite
says so rather than the fixture quietly becoming redundant.
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
def placed():
    G = _m("geometry")
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    return G.solve(plan, engine="heuristic")


def _elev(placed, style=None):
    ST, RF, EL = _m("structure"), _m("roof"), _m("elevation")
    p = copy.deepcopy(placed)
    if style:
        p["style"] = style
    sec = ST.build_section(p, None, geometry_result=p)
    rf = RF.build_roof(p, None, section=sec)
    return EL.build_elevation(p, None, section=sec, roof=rf)


def _sheet(el, face, tmp_path):
    RE = _m("render_elevation")
    out = str(tmp_path / f"{face}.svg")
    RE.render_elevation(el, out, face=face)
    ink = IR.Ink(open(out).read())
    pl = next(f for f in ink.frames() if f.get("proj") == "elevation")
    said = " ".join(t for t, _a, _i in ink.texts()).upper()
    return ink, pl, said


def _face_ft(pl, x_px):
    """The inverse of `inkread.from_model` along the face."""
    return (x_px - pl["origin_px"][0]) / pl["px_per_ft"] + pl["at_origin_ft"][0]


def test_the_modillions_centre_on_the_bays_they_stand_over(placed, tmp_path):
    el = copy.deepcopy(_elev(placed))
    band = next(m for m in el["eave_cornice"]["members"] if m.get("profile") == "modillion")
    assert band.get("width_in") is None and band.get("spacing_in"), (
        "the premise: the corpus states no modillion width, so the band is drawn solid and the "
        "anchors are unreachable")
    band["width_in"] = 6.0
    ink, pl, _said = _sheet(el, "S", tmp_path)
    tooth_px = 6.0 / 12.0 * pl["px_per_ft"]
    teeth = [it.bbox() for it in ink.select("rect") if "bd" in it.classes and "w-fine" in it.classes
             and abs((it.bbox()[2] - it.bbox()[0]) - tooth_px) < 0.2]
    assert len(teeth) > 5, "the premise: a band with a stated width is drawn as teeth"
    centres = [_face_ft(pl, (b[0] + b[2]) / 2.0) for b in teeth]
    for bay in el["faces"]["S"]["centres_ft"]:
        # a tooth over every bay centre, to the print's 0.1 px
        assert min(abs(c - bay) for c in centres) < 0.1 / pl["px_per_ft"] + 1e-6, (bay, centres)


def test_a_keystone_with_no_stated_width_is_not_drawn_and_is_said(placed, tmp_path):
    el = _elev(placed, "mid-atlantic-georgian")
    heads = [sw.get("head_treatment") or {} for sw in el["storey_windows"]]
    assert all(h.get("keystone") and h.get("keystone_width_in") for h in heads), (
        "the premise: mid-atlantic-georgian's kit states a keystone and its width")
    ink, _pl, said = _sheet(el, el["entrance_face"], tmp_path)
    assert [it for it in ink.select("rect") if "arch" in it.classes], "a stated keystone is drawn"
    assert "KEYSTONE NOT DRAWN" not in said
    el2 = copy.deepcopy(el)
    for sw in el2["storey_windows"]:
        sw["head_treatment"]["keystone_width_in"] = None
    ink2, _pl2, said2 = _sheet(el2, el2["entrance_face"], tmp_path)
    assert not [it for it in ink2.select("rect") if "arch" in it.classes], (
        "a keystone was drawn at a width no record states")
    assert "KEYSTONE NOT DRAWN" in said2


def test_a_stack_with_no_stated_plan_size_is_not_drawn_and_is_said(placed, tmp_path):
    el = _elev(placed)
    face = next(f for f in "EW" if el.get("chimney_stack_plan_in"))
    ink, _pl, said = _sheet(el, face, tmp_path)
    # ANY ELEMENT (WP-14.6): the stack is a polygon now its foot follows the rake, and a `rect`
    # selector here would make the premise fail -- loudly -- and the refusal below pass vacuously
    assert ink.select(cls="ch"), (
        "the premise: this face draws the stacks at their stated size")
    assert "STACKS NOT DRAWN" not in said
    el2 = copy.deepcopy(el)
    el2["chimney_stack_plan_in"] = None
    ink2, _pl2, said2 = _sheet(el2, face, tmp_path)
    assert not ink2.select(cls="ch"), (
        "a stack was drawn at a plan size no record states")
    assert "STACKS NOT DRAWN" in said2
