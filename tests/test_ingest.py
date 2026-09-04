"""WP-5.5. The drafter-DXF extractor, and the discipline it inherits: extract
candidates, name every gap, never guess a record into existence.

Pinned here:
  * a drafter's file (arbitrary layers, mm units, plain closed polylines with
    text labels) yields candidates at the right sizes in feet, with name hints
    matched by containment and the human's remaining work listed by name;
  * a silent header goes to the room-scale heuristic and says the units are an
    inference; a genuinely ambiguous file is a refusal to pick, not a guess;
  * a non-rectangular polyline is taken as its bounding box and says so;
  * a TDL-emitted sheet short-circuits to WP-5.1's reader and returns the
    complete, cross-checked record;
  * the new `provenance` object (plan schema 0.2.0 — the structured provenance
    WP-2.1 asked for) validates, and a laundered method does not.
"""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
if BUILD not in sys.path:
    sys.path.insert(0, BUILD)

import modcache as mc

ING = mc.load("ingest_dxf", os.path.join(BUILD, "ingest_dxf.py"))


def _drafter_doc(ezdxf, insunits):
    doc = ezdxf.new("R2018")
    doc.header["$INSUNITS"] = insunits
    msp = doc.modelspace()

    def room(x, y, w, h, name):
        msp.add_lwpolyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
                           close=True, dxfattribs={"layer": "A-WALL"})
        t = msp.add_text(name, dxfattribs={"height": 200})
        t.set_placement((x + w / 2, y + h / 2))

    room(0, 0, 4500, 4000, "KITCHEN")        # 14.8 x 13.1 ft in mm
    room(4500, 0, 5500, 4000, "DINING")
    room(0, 4000, 10000, 5000, "LIVING")
    msp.add_line((0, 0), (10000, 0), dxfattribs={"layer": "A-WALL"})
    t = msp.add_text("SHEET A-1", dxfattribs={"height": 300})
    t.set_placement((14000, -2000))          # outside every room
    return doc


@pytest.fixture()
def drafter_mm(tmp_path):
    ezdxf = pytest.importorskip("ezdxf")
    p = str(tmp_path / "drafter.dxf")
    _drafter_doc(ezdxf, 4).saveas(p)
    return p


def test_extracts_candidates_with_named_gaps(drafter_mm):
    res = ING.extract(drafter_mm)
    assert res["complete"] is False
    rooms = res["candidates"]["rooms"]
    assert len(rooms) == 3
    hints = {r.get("name_hint") for r in rooms}
    assert hints == {"KITCHEN", "DINING", "LIVING"}
    kitchen = next(r for r in rooms if r.get("name_hint") == "KITCHEN")
    assert abs(kitchen["w"] - 4500 / 304.8) < 0.05        # mm -> ft
    assert res["units"]["units"] == "mm" and "header" in res["units"]["basis"]
    assert "SHEET A-1" in res["candidates"]["texts_unmatched"]
    gap_text = " ".join(res["gaps"])
    for named in ("room types", "style", "windows and doors", "wall topology"):
        assert named in gap_text, f"gap not named: {named}"


def test_silent_header_is_an_inference_said_so(tmp_path):
    ezdxf = pytest.importorskip("ezdxf")
    p = str(tmp_path / "unitless.dxf")
    _drafter_doc(ezdxf, 0).saveas(p)
    res = ING.extract(p)
    assert res["units"]["units"] == "mm"
    assert "inferred" in res["units"]["basis"]
    assert "inference" in res["units"]["note"]


def test_ambiguous_units_refuse_to_pick(tmp_path):
    ezdxf = pytest.importorskip("ezdxf")
    doc = ezdxf.new("R2018")
    doc.header["$INSUNITS"] = 0
    msp = doc.modelspace()
    # a 10 x 8 unit room is plausible as FEET (10 x 8 ft) and as METRES
    # (32.8 x 26.2 ft) alike — both score 1.0, no clear winner, so the
    # extractor must refuse to pick rather than prefer either
    msp.add_lwpolyline([(0, 0), (10, 0), (10, 8), (0, 8)], close=True)
    p = str(tmp_path / "ambiguous.dxf")
    doc.saveas(p)
    res = ING.extract(p)
    assert res.get("unimported") and "ambiguous" in res["error"]
    assert "scores" in res["units"]
    # …and stating the units resolves it without changing the data
    res2 = ING.extract(p, units="ft")
    assert res2["complete"] is False
    assert res2["units"]["basis"] == "stated by the caller"
    assert res2["candidates"]["rooms"][0]["w"] == 10


def test_non_rectangular_is_bounding_box_and_says_so(tmp_path):
    ezdxf = pytest.importorskip("ezdxf")
    doc = ezdxf.new("R2018")
    doc.header["$INSUNITS"] = 2   # feet
    msp = doc.modelspace()
    # an L-shaped room: half the bbox area
    msp.add_lwpolyline([(0, 0), (20, 0), (20, 8), (10, 8), (10, 16), (0, 16)], close=True)
    p = str(tmp_path / "ell.dxf")
    doc.saveas(p)
    res = ING.extract(p)
    r = res["candidates"]["rooms"][0]
    assert r["rectangular"] is False
    assert "bounding box" in r["note"]


def test_tdl_sheet_short_circuits_to_the_complete_record(tmp_path):
    pytest.importorskip("ezdxf")
    EX = mc.load("export_dxf", os.path.join(BUILD, "export_dxf.py"))
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    p = str(tmp_path / "tdl.dxf")
    out = EX.export_plan_dxf(plan, p)
    assert "error" not in out
    res = ING.extract(p)
    assert res["complete"] is True and res["source"] == "tdl-dxf"
    assert res["record"]["id"] == "tidewater-georgian-careful"


def test_lines_only_drawing_is_an_honest_refusal(tmp_path):
    ezdxf = pytest.importorskip("ezdxf")
    doc = ezdxf.new("R2018")
    msp = doc.modelspace()
    for seg in [((0, 0), (30, 0)), ((30, 0), (30, 20)), ((30, 20), (0, 20)), ((0, 20), (0, 0))]:
        msp.add_line(*seg)
    p = str(tmp_path / "lines.dxf")
    doc.saveas(p)
    res = ING.extract(p)
    assert res.get("unimported") and "closed polylines" in res["error"]


def test_refusal_without_ezdxf(monkeypatch, tmp_path):
    import builtins
    real = builtins.__import__

    def block(name, *a, **k):
        if name == "ezdxf" or name.startswith("ezdxf."):
            raise ImportError("blocked for the test")
        return real(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", block)
    res = ING.extract(str(tmp_path / "whatever.dxf"))
    assert res.get("unimported") is True and "not installed" in res["error"]


# ---------------------------------------------------------------- provenance

def test_provenance_validates_and_gates_method():
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.load(open(os.path.join(ROOT, "schema", "plan.schema.json")))
    # 0.2.0 (WP-5.5) added `provenance`; 0.3.0 (WP-6.2) admits the PLACED plan — geometry,
    # positioned openings, the stair — as record data. Moved with the bump rather than
    # loosened: this pin exists so a schema change cannot pass unnoticed, and pinning the
    # CURRENT version is what makes the next one show up here too.
    # 0.4.0 (WP-9.1/9.2): `unplaced` carries its figures as `needs`/`have` beside the prose, and
    # the record carries the loop's own `revision_report`.
    # 0.5.0 (OQ 40, 3 Sep 2026): a house may be composed of more than one massing element. A room
    # carries an optional `block`, and `footprint` an optional `blocks` -- both additive, so the
    # footprint scalars still describe the main block and every existing reader is untouched. This
    # pin did its job and caught the bump, which is the whole reason it names the current version.
    # 0.6.0 (WP-11.2, 4 Sep 2026): a plan may name the PARTI it is an instance of, as an id and
    # never a record. It is what lets the diagram's own bay module reach the placement, and what
    # build/check_plans.py holds a hand-authored record to. Additive; every existing plan
    # validates unchanged. Caught by this pin again, which is twice in two days.
    # 0.7.0 (WP-11.4, 4 Sep 2026): a plan room may carry `hearth`, an ARRAY of authored fires --
    # wall, position, opening width, flue. Additive; every existing plan validates unchanged.
    # **Caught by this pin for the third time in two days, and this time it was missed at the
    # push**: WP-11.4 bumped the schema and did not run this suite, so the commit went out with
    # the pin red. The pin is not the problem.
    assert schema["version"] == "0.7.0"
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    plan["provenance"] = {
        "source": "HABS VA-1234 sheet 2", "method": "traced",
        "transcription_confidence": "medium",
        "field_confidence": {"levels.0.rooms.kitchen.windows": "low"},
        "style_reasoning": "five-bay symmetry, river-front pediment",
        "traced_by": "test",
    }
    jsonschema.validate(plan, schema)
    plan["provenance"]["method"] = "guessed"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(plan, schema)
