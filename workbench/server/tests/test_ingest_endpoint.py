"""WP-5.5: the /api/ingest/dxf route. A drafter's DXF (sent as text) comes back
as candidates with named gaps; a TDL-emitted sheet comes back a complete record;
ambiguous units and missing bodies are stated HTTP errors, never guesses."""
import io
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))


def _drafter_dxf_text():
    ezdxf = pytest.importorskip("ezdxf")
    doc = ezdxf.new("R2018")
    doc.header["$INSUNITS"] = 4   # mm
    msp = doc.modelspace()
    msp.add_lwpolyline([(0, 0), (4500, 0), (4500, 4000), (0, 4000)],
                       close=True, dxfattribs={"layer": "A-WALL"})
    t = msp.add_text("KITCHEN", dxfattribs={"height": 200})
    t.set_placement((2250, 2000))
    buf = io.StringIO()
    doc.write(buf)
    return buf.getvalue()


def test_ingest_requires_dxf_text(client):
    r = client.post("/api/ingest/dxf", json={})
    assert r.status_code == 422


def test_drafter_dxf_returns_candidates_and_gaps(client):
    r = client.post("/api/ingest/dxf", json={"dxf": _drafter_dxf_text()})
    assert r.status_code == 200, r.text[:300]
    j = r.json()
    assert j["complete"] is False
    assert j["candidates"]["rooms"][0]["name_hint"] == "KITCHEN"
    assert j["units"]["units"] == "mm"
    assert any("room types" in g for g in j["gaps"])


def test_tdl_sheet_returns_the_complete_record(client):
    pytest.importorskip("ezdxf")
    import sys
    b = os.path.join(ROOT, "build")
    if b not in sys.path:
        sys.path.insert(0, b)
    import modcache as mc
    EX = mc.load("export_dxf", os.path.join(b, "export_dxf.py"))
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "tdl.dxf")
        assert "error" not in EX.export_plan_dxf(plan, p)
        text = open(p).read()
    r = client.post("/api/ingest/dxf", json={"dxf": text})
    assert r.status_code == 200
    j = r.json()
    assert j["complete"] is True and j["record"]["id"] == "tidewater-georgian-careful"


def test_unreadable_dxf_is_a_stated_422(client):
    r = client.post("/api/ingest/dxf", json={"dxf": "this is not a dxf"})
    assert r.status_code == 422
    assert "error" in r.json()["detail"]
