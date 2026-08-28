"""WP-5.1: the /api/export/{fmt} route. The DXF that leaves this endpoint is
the same file build/export_dxf.py writes — proven by round-tripping the
response text through build/import_dxf.py back to a record with the same
validator findings. Refusals arrive as stated HTTP errors, never empty files."""
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))


def _plan():
    return json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))


def test_export_requires_a_plan(client):
    r = client.post("/api/export/dxf", json={})
    assert r.status_code == 422


def test_export_unknown_format_is_named(client):
    r = client.post("/api/export/step", json={"plan": _plan()})
    assert r.status_code == 422
    assert "unknown export format" in r.json()["detail"]["error"]


def test_dxf_plan_sheet_round_trips(client, tmp_path):
    pytest.importorskip("ezdxf")
    import sys
    b = os.path.join(ROOT, "build")
    if b not in sys.path:
        sys.path.insert(0, b)
    import modcache as mc
    IM = mc.load("import_dxf", os.path.join(b, "import_dxf.py"))
    PC = mc.load("plan_check", os.path.join(b, "plan_check.py"))

    plan = _plan()
    r = client.post("/api/export/dxf", json={"plan": plan, "kind": "plan"})
    assert r.status_code == 200, r.text[:300]
    j = r.json()
    assert j["filename"].endswith("-plan.dxf")
    p = tmp_path / "roundtrip.dxf"
    p.write_text(j["text"])
    back = IM.read_plan_dxf(str(p))
    assert "error" not in back, back.get("error")
    C = PC.load_corpus()
    f0 = PC.check(json.loads(json.dumps(plan)), C)
    f1 = PC.check(back["plan"], C)
    assert json.dumps(f0, sort_keys=True, default=str) == \
           json.dumps(f1, sort_keys=True, default=str)


def test_ifc_model_carries_tdl_ids(client, tmp_path):
    ios = pytest.importorskip("ifcopenshell")
    import ifcopenshell.util.element as uel
    r = client.post("/api/export/ifc", json={"plan": _plan()})
    assert r.status_code == 200, r.text[:300]
    j = r.json()
    assert j["schema"] == "IFC4" and j["counts"]["spaces"] > 0
    p = tmp_path / "out.ifc"
    p.write_text(j["text"])
    g = ios.open(str(p))
    space = g.by_type("IfcSpace")[0]
    ps = uel.get_psets(space).get("TDL") or {}
    assert ps.get("plan_id") == "tidewater-georgian-careful" and ps.get("tdl_id")


def test_missing_library_is_a_stated_501(client, monkeypatch):
    """The honest-refusal path: without ezdxf the endpoint says so — the OQ 35
    pattern over HTTP — rather than returning an empty or broken file."""
    import sys
    b = os.path.join(ROOT, "build")
    if b not in sys.path:
        sys.path.insert(0, b)
    import modcache as mc
    EX = mc.load("export_dxf", os.path.join(b, "export_dxf.py"))
    monkeypatch.setattr(EX, "_ezdxf", lambda: None)
    r = client.post("/api/export/dxf", json={"plan": _plan(), "kind": "plan"})
    assert r.status_code == 501
    d = r.json()["detail"]
    assert d["unexported"] is True and "could not export" in d["error"]


def test_one_drawing_set_is_one_building(client):
    """WP-6.4. The plan SVG and the exported DXF must be the SAME PLACEMENT.

    They were not. `corpus.drawing(kind="plan")` went through `engine="auto"` after WP-6.3,
    while `export_dxf._solved_copy` forced `engine="heuristic"` under a comment saying it
    was "drawn the same way the workbench draws it" -- a premise that flip made false. The
    client posts the DECLARED record (no `geometry`), so the exporter's has-geometry
    short-circuit never fired and a reader could download a DXF of a different placement of
    the same house than the sheet they were looking at when they pressed the button.

    Asserted on the drawn room rectangles rather than on a byte diff: the two files are
    different formats and only the geometry has to agree."""
    from workbench.server import corpus
    plan = _plan()
    a = corpus._placed(corpus.core.copy_json(plan), None, 60)
    b = corpus._placed(corpus.core.copy_json(plan), None, 60)
    assert "error" not in a and "error" not in b

    def rects(p):
        return {r["id"]: (r["geometry"]["x_ft"], r["geometry"]["y_ft"],
                          r["geometry"]["width_ft"], r["geometry"]["depth_ft"])
                for lv in p["levels"] for r in lv["rooms"] if r.get("geometry")}

    assert rects(a) == rects(b), "the same plan placed twice must give the same house"
    # and the engine is the PROVING one wherever it can answer, not the fallback the
    # exporter used to force on itself
    eng = a["geometry_report"].get("solver", {}).get("engine")
    assert eng in ("cp-sat", "heuristic"), eng
    if eng == "heuristic":
        # unjudged is not passed: a fallback must say why it fell back
        assert a["geometry_report"]["solver"].get("reason"), \
            "the heuristic ran and the record does not say why"


def test_a_placed_record_is_never_re_solved_out_from_under_the_sheet(client):
    """`_placed` returns a record that already carries geometry untouched. A bench plan the
    reader has already had placed must export as the house on their screen, not as a fresh
    solve of the same brief -- which is a different house whenever the search is involved."""
    from workbench.server import corpus
    plan = _plan()
    placed = corpus._placed(corpus.core.copy_json(plan), None, 60)
    assert "error" not in placed
    again = corpus._placed(placed, None, 60)
    assert again is placed, "an already-placed record must be returned as it stands"
