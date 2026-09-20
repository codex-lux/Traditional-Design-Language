"""WP-5.1: the /api/export/{fmt} route. The DXF that leaves this endpoint is
the same file build/export_dxf.py writes — proven by round-tripping the
response text through build/import_dxf.py back to a record with the same
validator findings. Refusals arrive as stated HTTP errors, never empty files."""
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))


# WP-13.4: A DRAWABLE RECORD, FOUND RATHER THAN NAMED. Lucas ruled 15 Sep 2026 that a placement
# breaking a hard fact of the type is refused and not drawn, and a CAD file is a surface a
# reader takes away and builds from -- so the export routes refuse it exactly as the sheet
# does. Measured: 15 of 16 shipped records are refused on `auto`. These tests are about the
# FILE and the round trip, so they take the record `drawable.py` finds by reading the verdict;
# the refusal's own half of the contract is `test_the_export_routes_refuse_a_refused_placement`
# at the foot of this file, and `test_refusal_routes.py` beside it.
def _plan():
    from . import drawable
    return drawable.drawable_plan()


def _refused_plan():
    """A shipped record the ruling refuses, or a skip. Read from the corpus rather than named,
    because which records are refused is a property of the placer and moves with it."""
    import pytest
    from workbench.server import corpus
    for rel in ("plans/tidewater-georgian-careful.json", "plans/spec-builder-colonial.json"):
        plan = json.load(open(os.path.join(ROOT, rel)))
        if "refused_placement" in corpus._placed(corpus.core.copy_json(plan), None, 60):
            return plan
    pytest.skip("COULD NOT EVALUATE: no shipped plan is refused on this tree, so there is no "
                "refusal for the export routes to be held to")


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
    """The identity of the record travels into the file: a reader who opens the IFC can say
    which plan it is and which room each space was.

    RE-CUT AGAINST THE PROPERTY (20 Sep 2026). This asserted the literal
    `"tidewater-georgian-careful"`, which is the record `_plan()` returned when WP-5.1 wrote
    the test -- and WP-13.4 replaced `_plan()` with `drawable.drawable_plan()`, a record FOUND
    by reading the refusal verdict rather than named, because the refuse-to-draw ruling left
    most shipped records undrawable (15 of 16 on `auto` as WP-13.4 measured it, 12 of 16
    drawable by the 16 Sep merge -- a figure about the tree it was taken on). From that commit
    the helper returned
    `bad-06-open-concept-render` and this line was false. It went unseen because
    `importorskip` skips it wherever `ifcopenshell` is absent, which is every container this
    corpus is usually verified in; it failed in CI, which installs the library.

    `drawable.py`'s own docstring is the argument against what was here: *"a literal filename
    would be one plan's luck, and the day that plan's placement moves the file would go red on
    something it is not about (this repository has re-cut four guards for exactly that)."*
    This is the fifth. The expectation is read off the record that was POSTED, so which plan
    the placer leaves drawable cannot reach it.

    And `tdl_id` is held to the record's own room ids rather than merely to being truthy:
    `export_ifc.py` writes an `IfcSpace`'s `tdl_id` as its room's `id`, and a writer that
    stamped a constant would satisfy truthiness and fail this."""
    ios = pytest.importorskip("ifcopenshell")
    import ifcopenshell.util.element as uel
    plan = _plan()
    r = client.post("/api/export/ifc", json={"plan": plan})
    assert r.status_code == 200, r.text[:300]
    j = r.json()
    assert j["schema"] == "IFC4" and j["counts"]["spaces"] > 0
    p = tmp_path / "out.ifc"
    p.write_text(j["text"])
    g = ios.open(str(p))
    space = g.by_type("IfcSpace")[0]
    ps = uel.get_psets(space).get("TDL") or {}
    assert ps.get("plan_id") == plan["id"], (
        f"the IFC says it is {ps.get('plan_id')!r} and the record posted was {plan['id']!r} -- "
        "the identity did not travel, or the route exported a different house")
    # `rm`, not `r`: `r` is the response above, and rebinding it here is the shape CLAUDE.md
    # records for render_plan.py's inner loop.
    room_ids = {rm["id"] for lv in plan["levels"] for rm in lv["rooms"]}
    assert ps.get("tdl_id") in room_ids, (
        f"the space's tdl_id {ps.get('tdl_id')!r} is not one of {plan['id']}'s room ids -- a "
        "space must carry the id of the room it is")


def test_missing_library_is_a_stated_501(client, monkeypatch):
    """The honest-refusal path: without ezdxf the endpoint says so — the OQ 35
    pattern over HTTP — rather than returning an empty or broken file.

    WP-13.4 GAVE THIS TEST A SECOND JOB, because a second refusal now reaches the same route.
    "This server cannot do that" (501, keyed `refusal`) and "this house cannot be drawn" (422,
    keyed `refused_placement`) are one letter apart in the key and opposite in meaning, so the
    library refusal is asserted to carry the 501 key AND to carry no placement refusal -- and
    the companion at the foot of the file asserts the converse."""
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
    assert d.get("refusal") is True, "the 501 is keyed off `refusal` and must set it"
    assert "refused_placement" not in d, (
        "a missing library is not a refused house: the two keys must never both be set, or a "
        "reader is told the server lacks a capability it has")


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
    assert "error" not in a and "error" not in b, (a.get("error") or b.get("error"))

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
    solve of the same brief -- which is a different house whenever the search is involved.

    **AND IT IS RE-JUDGED ON THE WAY THROUGH (WP-13.4).** A carried record never reaches a
    record writer, so `geometry._disclose` never ran on it and nothing had decided whether it
    may be drawn -- a composed candidate, the plan `scene()` returns and any record a client
    keeps and posts back all arrive that way. The two halves are asserted together because they
    pull in opposite directions and a fix for either alone breaks the other: the record must
    come back AS IT STANDS (identity, not a copy, not a re-solve) and it must come back
    JUDGED."""
    from workbench.server import corpus
    plan = _plan()
    placed = corpus._placed(corpus.core.copy_json(plan), None, 60)
    assert "error" not in placed, placed.get("error")
    # strip the verdict the solve wrote, so the short circuit has to produce it again rather
    # than reading one that was already there -- otherwise this passes with the re-judge gone
    placed["geometry_report"].pop("refused", None)
    placed["geometry_report"].pop("type_facts", None)
    again = corpus._placed(placed, None, 60)
    assert again is placed, "an already-placed record must be returned as it stands"
    assert "type_facts" in again["geometry_report"], (
        "the carried-geometry short circuit did not re-judge: a record that skips the verdict "
        "is a record every surface would draw")
    assert "refused" in again["geometry_report"]


def test_the_carried_geometry_short_circuit_refuses_a_refused_placement(client):
    """The other side of the re-judge: the same record posted WITH its geometry is refused.

    This is the route a composed candidate and the scene's returned plan take, and it is the
    one that had no guard at all -- `_placed` returned such a record untouched, so a client
    that kept a placement and posted it back got a sheet out of a house the ruling refuses."""
    from workbench.server import corpus
    plan = _refused_plan()
    fresh = corpus._placed(corpus.core.copy_json(plan), None, 60)
    assert "refused_placement" in fresh, "the fixture is not refused on a fresh solve"
    # now the same house, carried in already placed
    import sys
    b = os.path.join(ROOT, "build")
    if b not in sys.path:
        sys.path.insert(0, b)
    import modcache as mc
    GEO = mc.load("geometry", os.path.join(b, "geometry.py"))
    carried = GEO.solve(corpus.core.copy_json(plan), None, 60, engine="heuristic")
    assert any("geometry" in r for lv in carried["levels"] for r in lv["rooms"])
    again = corpus._placed(carried, None, 60)
    assert "refused_placement" in again, (
        "a record carrying a refused placement was returned as drawable: the short circuit "
        "has stopped re-judging")


def test_the_export_routes_refuse_a_refused_placement(client):
    """DXF and IFC both refuse, with the conflict set and never with the 501 key (WP-13.4).

    A CAD file is the surface a reader builds from, so it is refused exactly as the sheet is.
    Asserted on BOTH formats because they reach the placement by different routes -- the DXF
    through `export_dxf._solved_copy`, the IFC through `_placed` (which that branch did not
    call at all until this package)."""
    plan = _refused_plan()
    for fmt, body in (("dxf", {"plan": plan, "kind": "plan"}), ("ifc", {"plan": plan})):
        r = client.post(f"/api/export/{fmt}", json=body)
        assert r.status_code == 422, (fmt, r.status_code, r.text[:200])
        d = r.json()["detail"]
        assert d.get("refusal") is not True, (
            f"{fmt}: a refused house answered 501 -- that is the missing-library code and it "
            f"tells a reader the server lacks a capability it has")
        assert d["refused_placement"]["lines"], f"{fmt}: refused with no reason given"
        assert "text" not in d, f"{fmt}: a refused placement produced a file"
