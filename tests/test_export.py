"""WP-5.1. The DXF/IFC export, and the round-trip that is its acceptance line.

The acceptance in PLAN-OF-ACTION.md: "Round-trip test: DXF -> plan record ->
validator gives the same findings." These tests pin that, and the honesty
properties around it:

  * the round-trip is exact — not just the findings but the whole rebuilt
    record equals the authored one, solved geometry stripped;
  * the importer REFUSES when drawing and carried record disagree (a tampered
    window width) rather than trusting either side silently;
  * the importer refuses a DXF that is not TDL-emitted (that is WP-5.5's job);
  * without ezdxf/ifcopenshell the exporters refuse with a stated
    "could not export" and their selftests exit 3 (COULD NOT EVALUATE) —
    never a silent pass;
  * every IFC product carries its TDL ids in the "TDL" Pset, and a roof whose
    pitch is unjudged gets a stated geometry_note, not a guessed solid.
"""
import copy
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
if BUILD not in sys.path:
    sys.path.insert(0, BUILD)

import modcache as mc

EX = mc.load("export_dxf", os.path.join(BUILD, "export_dxf.py"))
IM = mc.load("import_dxf", os.path.join(BUILD, "import_dxf.py"))
PC = mc.load("plan_check", os.path.join(BUILD, "plan_check.py"))

PLANS = ["plans/spec-builder-colonial.json", "plans/tidewater-georgian-careful.json"]


def _load(rel):
    return json.load(open(os.path.join(ROOT, rel)))


# ------------------------------------------------------------------ DXF

@pytest.fixture(scope="module")
def dxf_sets(tmp_path_factory):
    pytest.importorskip("ezdxf")
    out = {}
    for rel in PLANS:
        plan = _load(rel)
        td = tmp_path_factory.mktemp(os.path.basename(rel).replace(".json", ""))
        res = EX.export_all(copy.deepcopy(plan), str(td))
        out[rel] = (plan, res)
    return out


def test_dxf_export_writes_the_named_sheets(dxf_sets):
    for rel, (plan, res) in dxf_sets.items():
        assert "error" not in res, res
        for kind in ("plan", "section", "roof"):
            sheet = res["sheets"][kind]
            assert "error" not in sheet, (rel, kind, sheet)
            assert os.path.exists(sheet["path"])
        # the elevation may be a stated refusal for a style outside the
        # classical-front family — but never a silent absence
        assert "elevation" in res["sheets"]


def test_dxf_round_trip_record_is_exact(dxf_sets):
    for rel, (plan, res) in dxf_sets.items():
        back = IM.read_plan_dxf(res["sheets"]["plan"]["path"])
        assert "error" not in back, (rel, back.get("error"))
        a = json.dumps(plan, sort_keys=True)
        b = json.dumps(back["plan"], sort_keys=True)
        assert a == b, f"{rel}: rebuilt record differs from the authored one"
        # the cross-checks actually ran — linework was verified, not skipped
        assert back["cross_checks"]["window_leaves"] > 0
        assert back["cross_checks"]["doors"] > 0


def test_dxf_round_trip_findings_identical(dxf_sets):
    C = PC.load_corpus()
    for rel, (plan, res) in dxf_sets.items():
        back = IM.read_plan_dxf(res["sheets"]["plan"]["path"])
        f0 = PC.check(copy.deepcopy(plan), C)
        f1 = PC.check(back["plan"], C)
        assert json.dumps(f0, sort_keys=True, default=str) == \
               json.dumps(f1, sort_keys=True, default=str), \
               f"{rel}: validator findings differ after the round-trip"


def test_import_refuses_tampered_window_width(dxf_sets, tmp_path):
    ezdxf = pytest.importorskip("ezdxf")
    _, res = dxf_sets["plans/tidewater-georgian-careful.json"]
    doc = ezdxf.readfile(res["sheets"]["plan"]["path"])
    msp = doc.modelspace()
    line = next(e for e in msp if e.dxftype() == "LINE"
                and e.dxf.layer.endswith("-WINDOW"))
    s, t = line.dxf.start, line.dxf.end
    line.dxf.end = (s[0] + (t[0] - s[0]) * 2, s[1] + (t[1] - s[1]) * 2, 0)
    p = str(tmp_path / "tampered.dxf")
    doc.saveas(p)
    back = IM.read_plan_dxf(p)
    assert "error" in back and "disagree" in back["error"]


def test_import_refuses_a_foreign_dxf(tmp_path):
    ezdxf = pytest.importorskip("ezdxf")
    doc = ezdxf.new("R2018")
    doc.modelspace().add_line((0, 0), (100, 0))
    p = str(tmp_path / "foreign.dxf")
    doc.saveas(p)
    back = IM.read_plan_dxf(p)
    assert "error" in back and "WP-5.5" in back["error"]


def test_dxf_refusal_without_ezdxf(monkeypatch):
    monkeypatch.setattr(EX, "_ezdxf", lambda: None)
    res = EX.export_all(_load(PLANS[0]), "/nonexistent")
    assert res.get("unexported") is True
    assert "could not export" in res["error"]
    assert EX.selftest() == 3   # COULD NOT EVALUATE, never a pass


def test_windows_drawn_at_true_width_not_the_svg_shrink(dxf_sets):
    ezdxf = pytest.importorskip("ezdxf")
    plan, res = dxf_sets["plans/tidewater-georgian-careful.json"]
    doc = ezdxf.readfile(res["sheets"]["plan"]["path"])
    widths = {round(((e.dxf.end[0] - e.dxf.start[0]) ** 2
                     + (e.dxf.end[1] - e.dxf.start[1]) ** 2) ** 0.5, 1)
              for e in doc.modelspace()
              if e.dxftype() == "LINE" and e.dxf.layer.endswith("-WINDOW")}
    recorded = {round((w.get("width_ft") or 3) * 12.0, 1)
                for lv in plan["levels"] for r in lv["rooms"]
                for w in (r.get("windows") or [])}
    assert widths and widths <= recorded


# ------------------------------------------------------------------ IFC

@pytest.fixture(scope="module")
def ifc_models(tmp_path_factory):
    ios = pytest.importorskip("ifcopenshell")
    EI = mc.load("export_ifc", os.path.join(BUILD, "export_ifc.py"))
    out = {}
    for rel in PLANS:
        plan = _load(rel)
        p = str(tmp_path_factory.mktemp("ifc") / "out.ifc")
        res = EI.export_ifc(copy.deepcopy(plan), p)
        assert "error" not in res, (rel, res)
        out[rel] = (plan, res, ios.open(p))
    return out


def test_ifc_acceptance_surface(ifc_models):
    for rel, (plan, res, g) in ifc_models.items():
        for cls in ("IfcWall", "IfcSlab", "IfcSpace", "IfcWindow", "IfcDoor",
                    "IfcRoof", "IfcOpeningElement", "IfcBuildingStorey"):
            assert g.by_type(cls), f"{rel}: no {cls}"


def test_ifc_products_carry_tdl_ids(ifc_models):
    import ifcopenshell.util.element as uel
    for rel, (plan, res, g) in ifc_models.items():
        for cls in ("IfcWall", "IfcSlab", "IfcSpace", "IfcWindow", "IfcDoor", "IfcRoof"):
            for el in g.by_type(cls):
                ps = uel.get_psets(el).get("TDL") or {}
                assert ps.get("plan_id") == plan["id"], (rel, cls, el.Name)
                assert "tdl_id" in ps, (rel, cls, el.Name)


def test_ifc_spaces_are_the_placed_rooms(ifc_models):
    import ifcopenshell.util.element as uel
    for rel, (plan, res, g) in ifc_models.items():
        room_ids = {r["id"] for lv in plan["levels"] for r in lv["rooms"]}
        space_ids = {(uel.get_psets(s).get("TDL") or {}).get("tdl_id")
                     for s in g.by_type("IfcSpace")}
        assert space_ids and space_ids <= room_ids


def test_ifc_unjudged_pitch_is_a_note_not_a_solid(ifc_models):
    """The spec Colonial's roof pitch is unjudged (no style source) — the IFC
    must say so on the IfcRoof, and must NOT contain guessed roof planes."""
    import ifcopenshell.util.element as uel
    plan, res, g = ifc_models["plans/spec-builder-colonial.json"]
    roof = g.by_type("IfcRoof")[0]
    ps = uel.get_psets(roof).get("TDL") or {}
    assert "geometry_note" in ps
    assert not [s for s in g.by_type("IfcSlab") if s.PredefinedType == "ROOF"]


def test_ifc_judged_pitch_gets_its_gable_planes(ifc_models):
    plan, res, g = ifc_models["plans/tidewater-georgian-careful.json"]
    planes = [s for s in g.by_type("IfcSlab") if s.PredefinedType == "ROOF"]
    assert len(planes) == 2


def test_ifc_refusal_without_ifcopenshell(monkeypatch):
    EI = mc.load("export_ifc", os.path.join(BUILD, "export_ifc.py"))
    monkeypatch.setattr(EI, "_ifc", lambda: None)
    res = EI.export_ifc(_load(PLANS[0]), "/nonexistent")
    assert res.get("unexported") is True
    assert "could not export" in res["error"]
    assert EI.selftest() == 3
