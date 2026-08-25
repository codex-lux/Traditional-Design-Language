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
