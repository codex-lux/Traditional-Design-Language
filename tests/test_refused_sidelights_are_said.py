"""A REFUSED SIDELIGHT PAIR IS SAID ON EVERY SURFACE THAT DOES NOT DRAW IT (audit, 27 Sep 2026).

`elevation._clearances` refuses a sidelight pair that would stand over a neighbouring opening and
writes its reason on the door's rect, and the plate says SIDELIGHTS NOT DRAWN. The scene and the
DXF both honoured `sidelights_drawn` and said nothing, so the model and the CAD file each read as
a doorcase that never had sidelights -- the silent absence a refusal must never look like, one
surface over from the one that said it. Each republishes the record's own reason now.

The Tidewater front WAS the house that refused its pair: its left sidelight would have stood 9 in
over the passage window the placer seated 12 in from the leaf. The premise was asserted, so the day
the placement moved that window the file would say so rather than pass over nothing -- and Phase 15,
WP-15.6 is that day: the placer reserves the doorcase's whole composition and half the ordinary pier
beside it, the window stands 33 in clear of the sidelights, and the pair is drawn. So the refusal is
DRIVEN now, by moving that window back to where the placer used to seat it, and the placed front is
the control: drawn, and said by no surface.
"""
import copy
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402


def _L(n):
    return modcache.load(n, os.path.join(ROOT, "build", n + ".py"))


GEO, ST, RF, EL, SC, EX = (_L("geometry"), _L("structure"), _L("roof"), _L("elevation"),
                           _L("scene"), _L("export_dxf"))


@pytest.fixture(scope="module")
def front():
    with open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json"), encoding="utf-8") as fh:
        plan = json.load(fh)
    # DATED 1790 SINCE WP-16.4 (30 Sep 2026). At the record's own 1765 the KIT refuses this pair
    # outright -- georgian-colonial-american forbids the sidelights for houses of 1700-1780 -- so
    # the placer reserves no room for them and there is no pair left for a neighbouring window to
    # refuse. The same house dated after the ban draws its pair, which is what this file refuses
    # and then says; the kit's own refusal is `tests/test_kit_refusal.py`'s subject.
    plan.setdefault("context", {})["date_of_representation"] = 1790
    saved = GEO._SOLVE_CACHE
    GEO._SOLVE_CACHE = {}
    try:
        placed = GEO.solve(plan, None, 250, engine="heuristic")
    finally:
        GEO._SOLVE_CACHE = saved
    sec = ST.build_section(placed, None, geometry_result=placed)
    roof = RF.build_roof(placed, section=sec)
    placed_elev = EL.build_elevation(placed, None, section=sec, roof=roof)
    face = placed_elev["entrance_face"]
    ctl = next(r for r in EL.opening_rects(placed_elev, face)["rects"] if r.get("entrance"))
    assert ctl.get("sidelights_drawn") and not ctl.get("sidelights_refused"), \
        "the premise: the placed front draws its pair (WP-15.6 keeps the window clear of it)"
    elev = copy.deepcopy(placed_elev)
    # DRIVE the passage window back to where the placer seated it before WP-15.6: its right jamb
    # MIN_SOLID_FT (12 in) from the leaf, every field the rect is read from shifted together
    win = max((p for p in elev["faces"][face]["placed"] if p["kind"] == "window"
               and p["storey"] == ctl["storey"] and p["cx_in"] < ctl["cx_in"]),
              key=lambda p: p["cx_in"])
    d_in = (ctl["x0_in"] - 12.0 - win["width_in"] / 2.0) - win["cx_in"]
    win["cx_in"] += d_in
    win["u_ft"] = round(win["u_ft"] + d_in / 12.0, 4)
    win["along_ft"] += d_in / 12.0
    door = next(r for r in EL.opening_rects(elev, face)["rects"] if r.get("entrance"))
    assert door.get("sidelights_refused") and door.get("sidelights_drawn") is False, \
        "the drive landed: the moved window refuses the sidelight pair"
    return placed, sec, roof, elev, face, door, placed_elev


def test_the_scene_says_the_refused_pair_in_the_records_own_words(front):
    placed, sec, roof, elev, _face, door, _ctl = front
    scene = SC.build_scene(placed, sec, roof, elev)
    said = [n for n in scene["not_modelled"] if n["what"] == "the sidelights"]
    assert len(said) == 1 and said[0]["why"] == door["sidelights_refused"], said
    assert not [s for s in scene["solids"] if "-sidelight-" in s["id"]], "a refused pair was modelled"


def test_the_dxf_carries_the_refusal_on_the_doorcase(front, tmp_path):
    pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
    import ezdxf
    _placed, _sec, _roof, elev, face, door, _ctl = front
    path = str(tmp_path / "front.dxf")
    res = EX.export_elevation_dxf(elev, path, face)
    assert "error" not in res, res
    found = []
    for e in ezdxf.readfile(path).modelspace():
        if e.has_xdata(EX.APPID):
            tags = [v for _c, v in e.get_xdata(EX.APPID)]
            if tags and tags[0] == "TDL::sidelights-refused":
                found.append(json.loads("".join(tags[1:]))["reason"])
    assert found == [door["sidelights_refused"]], found


def test_the_placed_front_draws_its_pair_and_no_surface_says_it_was_refused(front, tmp_path):
    """The control. The pair the placement leaves room for is modelled and drawn, and neither the
    scene nor the DXF carries a refusal for it -- so the two tests above bite on the refusal and not
    on something every front carries."""
    placed, sec, roof, _elev, face, _door, placed_elev = front
    scene = SC.build_scene(placed, sec, roof, placed_elev)
    assert not [n for n in scene["not_modelled"] if n["what"] == "the sidelights"]
    assert [s for s in scene["solids"] if "-sidelight-" in s["id"]], "the drawn pair is modelled"
    pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
    import ezdxf
    path = str(tmp_path / "placed.dxf")
    assert "error" not in EX.export_elevation_dxf(placed_elev, path, face)
    tags = [e.get_xdata(EX.APPID)[0][1] for e in ezdxf.readfile(path).modelspace()
            if e.has_xdata(EX.APPID) and e.get_xdata(EX.APPID)]
    assert "TDL::sidelights-refused" not in tags
