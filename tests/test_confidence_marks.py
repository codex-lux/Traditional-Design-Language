"""A member whose record is not a stated "high" is marked on every drawing of it (WP-14.2).

The orders page and the workbench's Proportions plate have marked a medium- or low-confidence
member since WP-5.x -- a warmer line, a dashed outline in the bench's `--judge-unjudged`. No
committed profile plate did, and neither did the elevation's cornice inset or the DXF, so a
Palladio cornice apportioned member by member read on those surfaces with the authority of a
measured one. Census P10 found 65 of the 73 plates silent about it.

The mark is the workbench's: a dashed outline over the member's OWN region, built from that
member's own segments (`profiles.band_path`), never re-constructed. And an unstated confidence
is not a high one -- `dimension()` defaulted it to "high", the projection's flattering default
one field over. No member leaves it unstated today (733 of 733), so that half is driven.
"""
import copy
import json
import os
import re
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import modcache  # noqa: E402
import inkread as IR  # noqa: E402

PE = modcache.load("proportion_engine", os.path.join(ROOT, "build", "proportion_engine.py"))
PROF = modcache.load("profiles", os.path.join(ROOT, "build", "profiles.py"))


def test_an_unstated_confidence_travels_as_none_and_is_marked():
    pack = copy.deepcopy(PE.resolve("vignola-tuscan"))
    member = pack["assemblies"]["capital"]["members"][0]
    assert member.get("confidence") == "high", "premise: the member states high"
    del member["confidence"]
    d = PE.dimension(pack, 6.0)
    got = next(m for a in d["assemblies"] if a["id"] == "capital"
               for m in a["members"] if m["id"] == member["id"])
    assert got["confidence"] is None
    assert PROF.is_weak(None) and PROF.is_weak("low") and PROF.is_weak("medium")
    assert not PROF.is_weak("high")


def test_a_plate_marks_each_weak_member_over_its_own_height_and_names_it():
    import ink_surfaces as SURF
    RP = modcache.load("render_profile", os.path.join(ROOT, "build", "render_profile.py"))
    svg, rep = RP.render("palladio-corinthian", "cornice", 12.0)
    rec = SURF.profile_record("palladio-corinthian", "cornice", 12.0)
    weak = {m["id"]: m for m in rec["members"]
            if rec["raw"][m["id"]].get("confidence") != "high"}
    assert weak, "premise: the plate holds a weak member"
    pl = SURF.ProfilePlate(svg)
    marks = [it for it in pl.ink.select("path") if "confidence" in it.classes]
    assert len(marks) == len(weak)
    for it in marks:
        mid = it.attrs.get("data-member")
        vs = [pl.model(p)[1] for p in it.points(n=16, lines=True)]
        assert min(vs) == pytest.approx(weak[mid]["y_bottom_in"], abs=1e-3), mid
        assert max(vs) == pytest.approx(weak[mid]["y_top_in"], abs=1e-3), mid
        assert (it.style.get("stroke-dasharray") or "").strip(), mid
    text = re.sub(r"\s+", " ", " ".join(t or "" for t, _p, _i in pl.ink.texts()))
    assert len(re.findall(r"(?:low|medium) confidence", text)) >= len(weak)
    assert "outlined dashed: their confidence is medium, low or unstated" in text


def test_the_elevation_inset_marks_the_cornices_weak_members_and_counts_them(tmp_path):
    EL = modcache.load("elevation", os.path.join(ROOT, "build", "elevation.py"))
    RE = modcache.load("render_elevation", os.path.join(ROOT, "build", "render_elevation.py"))
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    elev = EL.build_elevation(plan)
    members = elev["eave_cornice"]["members"]
    weak = [m for m in members if PROF.is_weak(m.get("confidence"))
            and m["y_top_in"] > m["y_bottom_in"]]
    assert weak, "premise: the Gibbs cornice carries apportioned members"
    out = str(tmp_path / "e.svg")
    RE.render_elevation(elev, out)
    svg = open(out).read()
    assert svg.count('class="confidence"') == len(weak)
    text = re.sub(r"\s+", " ", " ".join(re.findall(r">([^<]*)</text>", svg)))   # the caption wraps
    assert f"{len(weak)} MEMBER(S) OUTLINED DASHED — CONFIDENCE MEDIUM, LOW OR UNSTATED" in text


def test_the_dxf_carries_each_members_confidence_with_the_profile(tmp_path):
    ezdxf = pytest.importorskip("ezdxf")
    EL = modcache.load("elevation", os.path.join(ROOT, "build", "elevation.py"))
    DX = modcache.load("export_dxf", os.path.join(ROOT, "build", "export_dxf.py"))
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    elev = EL.build_elevation(plan)
    path = str(tmp_path / "e.dxf")
    DX.export_elevation_dxf(elev, path, face=elev.get("entrance_face"))
    doc = ezdxf.readfile(path)
    polys = [e for e in doc.modelspace().query("LWPOLYLINE")
             if e.dxf.layer == "TDL-ELEV-CORNICE-PROFILE"]
    assert len(polys) == 1
    tags = [v for _c, v in polys[0].get_xdata("TDL")]
    assert tags[0] == "TDL::cornice-profile"
    payload = json.loads("".join(tags[1:]))
    by_id = {m["id"]: m for m in payload["members"]}
    for m in elev["eave_cornice"]["members"]:
        assert by_id[m["id"]]["confidence"] == m.get("confidence"), m["id"]
        assert by_id[m["id"]]["projection_in"] == m.get("projection_in"), m["id"]
    assert any(PROF.is_weak(m["confidence"]) for m in payload["members"]), "premise"
