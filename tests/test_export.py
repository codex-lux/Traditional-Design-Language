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

# WP-13.4: THE EXPORTER REFUSES A REFUSED PLACEMENT, AND THAT REACHES THIS FILE. Lucas ruled
# 15 Sep 2026 that a placement breaking a hard fact of the type is not drawn, and a CAD file is
# the surface a reader builds from -- so `export_dxf._solved_copy` refuses on both its paths.
# Measured the day it landed: 14 of the 16 shipped records are refused on the search. The round
# trip these tests are for is about the FILE and not about whether the house may be built, so
# they take a record the ruling still lets a surface draw, found by reading the verdict rather
# than named -- which record that is is a property of the placer and moves with it.
#
# `tests/test_refusal.py::test_the_dxf_refuses_a_refused_placement_on_both_paths` is the other
# half, and it is what stops this substitution from reading as the ruling being switched off.
_DRAWABLE = []

# Cheapest first, measured (`bad-06` places in 0.8 s where the Tidewater record spends a whole
# 40 s budget). Every shipped record is tried; this only decides the ORDER, so a stale hint
# costs seconds and can cost nothing else.
_ORDER = ("plans/reference/bad-06-open-concept-render.json",
          "plans/reference/bad-04-log-cabin.json",
          "plans/reference/bad-03-narrow-lot-townhome.json")


def _drawable():
    """The first shipped record `export_dxf` will actually draw.

    ASKED OF THE FUNCTION UNDER TEST rather than of a re-derivation. The first version of this
    ran `GEO.solve(..., engine="heuristic")` and read the verdict off that, while
    `_solved_copy` solves on `auto` -- so it "found" a record the exporter then refused, and
    every test in this file failed on a fixture that had chosen wrong. A selector that asks a
    different question from the code it selects for is the instrument fault this repository
    keeps meeting; `_solved_copy` is the one reader now."""
    if _DRAWABLE:
        return _DRAWABLE[0]
    rels = list(_ORDER)
    for d in ("plans", os.path.join("plans", "reference")):
        for name in sorted(os.listdir(os.path.join(ROOT, d))):
            rel = f"{d}/{name}".replace(os.sep, "/")
            if name.endswith(".json") and rel not in rels:
                rels.append(rel)
    for rel in rels:
        if not os.path.exists(os.path.join(ROOT, rel)):
            continue
        _orig, solved = EX._solved_copy(copy.deepcopy(_load(rel)), None, 60)
        if "error" not in solved:
            _DRAWABLE.append(rel)
            return rel
    pytest.skip(f"COULD NOT EVALUATE: none of the {len(rels)} shipped records is drawable "
                f"under the 15 Sep 2026 ruling, so there is no DXF for this file to round-trip")


def _load(rel):
    return json.load(open(os.path.join(ROOT, rel)))


# ------------------------------------------------------------------ DXF

@pytest.fixture(scope="module")
def dxf_sets(tmp_path_factory):
    pytest.importorskip("ezdxf")
    out = {}
    for rel in [_drawable()]:
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
        # The elevation may be a stated refusal for a style outside the classical-front
        # family -- but NEVER a silent absence.
        #
        # WP-13.4 RE-CUT THE SECOND HALF OF THIS AND THE FIRST IS THE HALF THAT MATTERED. It
        # read "BOTH check plans are classical fronts, so for them a refusal is a regression",
        # which was true of the two shipped plans and is a statement about those RECORDS rather
        # than about the exporter. The drawable record this file now takes is
        # `contemporary-traditional`, outside that family, so its elevation is the stated
        # refusal the comment above already admits -- and asserting the old literal would have
        # convicted the exporter of behaving exactly as documented.
        #
        # What the exporter owes on any record is that the sheet is NAMED either way: a sheet
        # that errors must say `refusal` and why, and a sheet that is simply absent is the
        # silent failure this test exists for.
        assert "elevation" in res["sheets"], (
            f"{rel}: the elevation sheet is absent from the set -- a silent absence, which is "
            f"the one thing a refusal must never look like")
        _el = res["sheets"]["elevation"]
        if "error" in _el:
            assert _el.get("refusal") is True and _el["error"], (rel, _el)
        else:
            assert os.path.exists(_el["path"]), (rel, _el)


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
    _, res = dxf_sets[_drawable()]
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
    res = EX.export_all(_load(_drawable()), "/nonexistent")
    assert res.get("unexported") is True
    assert "could not export" in res["error"]
    assert EX.selftest() == 3   # COULD NOT EVALUATE, never a pass


def test_windows_drawn_at_true_width_not_the_svg_shrink(dxf_sets):
    ezdxf = pytest.importorskip("ezdxf")
    plan, res = dxf_sets[_drawable()]
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
        # equality with the PLACED set, not mere subset — an exporter that
        # drops all but one space would otherwise pass. The exporter's own
        # placement is the deterministic (and cached) heuristic solve.
        GEO = mc.load("geometry", os.path.join(BUILD, "geometry.py"))
        solved = GEO.solve(copy.deepcopy(plan), engine="heuristic")
        placed_ids = {r["id"] for lv in solved["levels"]
                      for r in lv["rooms"] if r.get("geometry")}
        assert space_ids == placed_ids, (rel, placed_ids ^ space_ids)


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
    res = EI.export_ifc(_load(_drawable()), "/nonexistent")
    assert res.get("unexported") is True
    assert "could not export" in res["error"]
    assert EI.selftest() == 3

def test_a_blind_bay_exports_no_opening_to_cad(tmp_path):
    """OQ 85 reached the CAD file, and only because this audit went looking.

    A bay a chimney stack stands on is `blind` and carries no opening at either storey. The SVG
    renderer was taught that; `export_dxf.py`'s bay loop read `if kind == "door" ... else: window`,
    so `blind` fell into the else and the DXF drew the very collision the sheet had stopped
    drawing — the drawing and the CAD file disagreeing about one record.

    The export selftest could not see it: it round-trips FINDINGS, not geometry. Nothing in this
    suite looked at where the ink went in a DXF either, which is the same gap WP-5.11's audit found
    in the SVG layer one file over.

    **THE FACE IS CHOSEN FROM THE READING AND WAS NAMED `E` UNTIL 17 SEP 2026.** This test needs
    a face that carries a blind bay AND draws at least one opening; the E gable of this record
    drew one until the merge of Phase 13 into the second Phase 11 line, and main's WP-11.17
    entrance front then re-placed the ground floor so that the library's E sash is refused and
    the face draws NOTHING. With no rectangle the count assertion passes at 0 == 0 and the axis
    loop below runs zero times, which is why the premise is asserted rather than the face pinned.
    Measured on the shipped record: E has a blind bay and 0 rects, W has a blind bay and 1."""
    ezdxf = pytest.importorskip("ezdxf")
    el = mc.load("elevation", os.path.join(BUILD, "elevation.py"))
    dx = mc.load("export_dxf", os.path.join(BUILD, "export_dxf.py"))
    rec = el.build_elevation(json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json"))))

    blind_faces = [f for f in "SNEW" if "blind" in (rec["faces"][f].get("kinds") or [])]
    assert blind_faces, "no face of this record carries a blind bay -- the test is about nothing"
    usable = [f for f in blind_faces if el.opening_rects(rec, f)["rects"]]
    assert usable, (
        f"faces {blind_faces} carry a blind bay and none of them draws a single opening, so the "
        "axis check below would run zero times. Pick a record or a face that draws one; never "
        "let this pass at 0 == 0.")
    face = usable[0]
    kinds = rec["faces"][face]["kinds"]
    centres = rec["faces"][face]["centres_ft"]
    blind_ft = [c for c, k in zip(centres, kinds) if k == "blind"]

    path = str(tmp_path / "gable.dxf")
    dx.export_elevation_dxf(rec, path, face=face)
    msp = ezdxf.readfile(path).modelspace()
    opens = [e for e in msp if e.dxftype() == "LWPOLYLINE" and "opening" in e.dxf.layer.lower()]
    # RE-CUT AT WP-13.3: the openings are the plan's PLACED openings on the E face, not two
    # per glazed rhythm bay, so the count is the elevation's own rectangles for the face --
    # and a placed window the stack stands on is refused by `opening_rects`, which is the
    # OQ 85 rule reaching a placed opening. Asserted positive first.
    rects = el.opening_rects(rec, face)["rects"]
    assert rects, f"the {face} face draws nothing, so the axis check below is vacuous"
    assert len(opens) == len(rects), (
        f"{len(opens)} opening polylines against {len(rects)} placed-and-drawn openings on {face}")
    stack_half = rec["faces"][face]["stack_half_width_ft"]
    for e in opens:
        pts = [pt[0] for pt in e.get_points("xy")]
        left, right = min(pts) / 12.0, max(pts) / 12.0
        for b in blind_ft:
            assert right < b - stack_half or left > b + stack_half, (
                f"an opening is exported at {left:.2f}-{right:.2f} ft, across the stack's axis ({b} ft)")



# ------------------------------------------------------------------ WP-9.2: a revised plan in a DXF
def test_a_revised_plan_round_trips_its_summary_and_states_the_report_is_absent(tmp_path):
    """XDATA is capped near 16 KB per entity; a six-round revision_report with attribution runs
    past it, and a marker that silently truncated would be a record that lied. The exporter
    carries the SUMMARY under its own name and says what it left out."""
    import json
    import os
    import sys
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(ROOT, "build"))
    import modcache as mc
    EX = mc.load("export_dxf", os.path.join(ROOT, "build", "export_dxf.py"))
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    plan["revision_report"] = {"schema": "0.4.0", "mode": "placed", "stop_reason": "converged",
                               "rounds": [{"n": 1, "moves": [{"move": "x"} for _ in range(400)]}],
                               "summary": {"rounds": 1, "moves_applied": 3, "key_before": [0, 5, 5, 1],
                                           "key_after": [0, 3, 5, 1], "stop_reason": "converged"}}
    meta = EX._plan_meta(plan)
    assert "revision_report" not in meta
    assert meta["revision_summary"]["moves_applied"] == 3 and meta["revision_summary"]["mode"] == "placed"
    assert "NOT carried" in meta["revision_summary"]["note"]
    assert len(json.dumps(meta["revision_summary"])) < 2000


def test_a_revised_plan_read_back_from_its_dxf_validates_against_the_plan_schema(tmp_path):
    """The writer's output was tested and the round trip was not (the session's audit): the
    record `read_plan_dxf` rebuilt carried `revision_summary`, which the plan schema did not
    admit, so a revised plan could be exported and never read back through `check_plan`."""
    import json
    import os
    import sys
    pytest.importorskip("ezdxf")
    jsonschema = pytest.importorskip("jsonschema")
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(ROOT, "build"))
    import modcache as mc
    EX = mc.load("export_dxf", os.path.join(ROOT, "build", "export_dxf.py"))
    IM = mc.load("import_dxf", os.path.join(ROOT, "build", "import_dxf.py"))
    # WP-13.4: a record the ruling still lets the exporter DRAW -- the round trip is what this
    # test is about, and a refused placement produces no file to read back.
    plan = _load(_drawable())
    plan["revision_report"] = {"schema": "0.4.0", "mode": "placed", "stop_reason": "converged",
                               "rounds": [{"n": 1, "moves": [{"move": "x"} for _ in range(400)]}],
                               "summary": {"rounds": 1, "moves_applied": 3, "moves_refused": 1, "key_before": [0, 5, 5, 1],
                                           "key_after": [0, 3, 5, 1], "stop_reason": "converged", "seconds": 4.2}}
    out = EX.export_plan_dxf(plan, str(tmp_path / "revised.dxf"), candidates=20)
    assert "error" not in out, out
    back = IM.read_plan_dxf(str(tmp_path / "revised.dxf"))
    assert "error" not in back, back
    rec = back["plan"] if "plan" in back else back
    assert rec["revision_summary"]["moves_applied"] == 3 and rec["revision_summary"]["mode"] == "placed"
    assert "revision_report" not in rec
    schema = json.load(open(os.path.join(ROOT, "schema", "plan.schema.json")))
    jsonschema.validate(rec, schema)
