"""A REFUSED SIDELIGHT PAIR IS SAID ON EVERY SURFACE THAT DOES NOT DRAW IT (audit, 27 Sep 2026).

`elevation._clearances` refuses a sidelight pair that would stand over a neighbouring opening and
writes its reason on the door's rect, and the plate says SIDELIGHTS NOT DRAWN. The scene and the
DXF both honoured `sidelights_drawn` and said nothing, so the model and the CAD file each read as
a doorcase that never had sidelights -- the silent absence a refusal must never look like, one
surface over from the one that said it. Each republishes the record's own reason now.

The Tidewater front is the house that refuses its pair (its left sidelight would stand 9 in over
the passage window the plan seats 12 in from the leaf). The premise is asserted, so the day the
placement moves that window the file says so rather than passing over nothing.
"""
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
    saved = GEO._SOLVE_CACHE
    GEO._SOLVE_CACHE = {}
    try:
        placed = GEO.solve(plan, None, 250, engine="heuristic")
    finally:
        GEO._SOLVE_CACHE = saved
    sec = ST.build_section(placed, None, geometry_result=placed)
    roof = RF.build_roof(placed, section=sec)
    elev = EL.build_elevation(placed, None, section=sec, roof=roof)
    face = elev["entrance_face"]
    door = next(r for r in EL.opening_rects(elev, face)["rects"] if r.get("entrance"))
    assert door.get("sidelights_refused") and door.get("sidelights_drawn") is False, \
        "the premise: this front refuses its sidelight pair"
    return placed, sec, roof, elev, face, door


def test_the_scene_says_the_refused_pair_in_the_records_own_words(front):
    placed, sec, roof, elev, _face, door = front
    scene = SC.build_scene(placed, sec, roof, elev)
    said = [n for n in scene["not_modelled"] if n["what"] == "the sidelights"]
    assert len(said) == 1 and said[0]["why"] == door["sidelights_refused"], said
    assert not [s for s in scene["solids"] if "-sidelight-" in s["id"]], "a refused pair was modelled"


def test_the_dxf_carries_the_refusal_on_the_doorcase(front, tmp_path):
    pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
    import ezdxf
    _placed, _sec, _roof, elev, face, door = front
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
