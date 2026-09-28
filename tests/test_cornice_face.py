"""Phase 15, WP-15.7: the eave drawn as its record states it, on the sheet and in the DXF.

Lucas, of the drawn Tidewater front (27 Sep 2026): "the cornice not being represented on this
export". The face drew ONE rectangle from the wall head to the true eave at the cornice's
projection, with one line in it. So the frieze stood 10.5 in proud of a wall its own record
(facade-classical's `elevation` assembly) says it is flush with, and the eight members
`eave_cornice` dimensions were drawn on the inset and nowhere on the face.

`elevation.cornice_marks` is the one spelling both surfaces draw from now, and census V25 and X4
read the ink. What the corpus cannot reach is driven here, each case asserting its own premise:
- a frieze stated proud, and one stated by no record (said, on both surfaces);
- the toothed band's layout, whose anchors are never a whole number of pitches apart on any face
  the elevation draws, and whose tooth width no pack states.
"""
import copy
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import modcache as mc  # noqa: E402
import inkread as IR  # noqa: E402


def _m(name):
    return mc.load(name, os.path.join(ROOT, "build", name + ".py"))


@pytest.fixture(scope="module")
def elev():
    G, ST, RF, EL = _m("geometry"), _m("structure"), _m("roof"), _m("elevation")
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    p = G.solve(plan, engine="heuristic")
    sec = ST.build_section(p, None, geometry_result=p)
    rf = RF.build_roof(p, None, section=sec)
    return EL.build_elevation(p, None, section=sec, roof=rf)


def _svg(el, face, tmp_path, tag="s"):
    out = str(tmp_path / f"{tag}-{face}.svg")
    _m("render_elevation").render_elevation(el, out, face=face)
    ink = IR.Ink(open(out, encoding="utf-8").read())
    pl = next(f for f in ink.frames() if f.get("proj") == "elevation")
    said = " ".join(" ".join(t.split()) for t, _a, _i in ink.texts() if t).upper()
    return ink, pl, said


def _box_ft(pl, it):
    b = it.bbox()
    (u0, v0), (u1, v1) = IR.to_model(pl, b[0], b[3]), IR.to_model(pl, b[2], b[1])
    return min(u0, u1), min(v0, v1), max(u0, u1), max(v0, v1)


# ------------------------------------------------------------------ the marks, on the shipped record
def test_the_marks_are_the_records_frieze_box_and_members(elev):
    EL = _m("elevation")
    cor = elev["eave_cornice"]
    cm = EL.cornice_marks(elev, "S")
    assert cm["applicable"]
    true_eave = elev["grade_to_true_eave_in"] / 12.0
    wall_top = elev["roof_record"]["main"]["grade_to_eave_ft"]
    spring = true_eave - cor["cornice_height_in"] / 12.0
    # the frieze: flush, as facade-classical's own member states it (projection_parts 0.0)
    assert cor["frieze_projection_in"] == 0.0
    fz = cm["frieze"]
    assert (fz["u0"], fz["h0"], fz["h1"]) == (0.0, wall_top, spring)
    assert fz["u1"] == elev["footprint"]["width_ft"] and fz["why"] is None
    # the box: the envelope's figure, the one the face has always drawn (OQ 79 is not chosen here)
    co = cm["cornice"]
    assert co["projection_in"] == cor["envelope_projection_in"] and co["why"] is None
    assert abs(co["u0"] + cor["envelope_projection_in"] / 12.0) < 1e-12
    assert (co["h0"], co["h1"]) == (spring, true_eave)
    # the members: every one, in order, end to end from the springing to the true eave
    ms = cm["members"]
    assert [m["id"] for m in ms] == [m["id"] for m in cor["members"]] and len(ms) == 8
    assert abs(ms[0]["h0"] - spring) < 1e-9 and abs(ms[-1]["h1"] - true_eave) < 1e-9
    assert all(abs(a["h1"] - b["h0"]) < 1e-9 for a, b in zip(ms, ms[1:])), "members that do not abut"
    # the modillions: the record states their pitch and not their width, so the band is solid, said
    t = cm["teeth"]
    assert t["member"] == "corn_modillion" and t["solid"] and "width" in t["reason"]
    assert any(n.startswith("MODILLION BAND DRAWN SOLID") for n in cm["notes"])


def test_a_record_with_no_cornice_draws_none_and_says_why(elev):
    EL = _m("elevation")
    el = copy.deepcopy(elev)
    el["eave_cornice"]["members"] = []
    cm = EL.cornice_marks(el, "S")
    assert not cm["applicable"] and "no eave cornice" in cm["why"]


# ------------------------------------------------------------------ the frieze, driven
def test_a_frieze_stated_proud_is_drawn_proud_on_both_surfaces(elev, tmp_path):
    """No record states a frieze proud of the wall, so the figure is driven, with the flush one as
    the control: a surface that ignored the figure would draw the two alike."""
    ezdxf = pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
    EX = _m("export_dxf")
    got = {}
    for tag, proj in (("flush", 0.0), ("proud", 3.0)):
        el = copy.deepcopy(elev)
        el["eave_cornice"]["frieze_projection_in"] = proj
        ink, pl, said = _svg(el, "S", tmp_path, tag)
        (fz,) = [it for it in ink.select("rect") if {"bd", "fz"} <= set(it.classes)]
        u0, _v0, u1, _v1 = _box_ft(pl, fz)
        path = str(tmp_path / f"{tag}.dxf")
        assert "error" not in EX.export_elevation_dxf(el, path, face="S")
        (poly,) = [e for e in ezdxf.readfile(path).modelspace().query("LWPOLYLINE")
                   if e.dxf.layer == "TDL-ELEV-FRIEZE"]
        west = min(p[0] for p in poly.get_points())
        got[tag] = (u0, u1, west, "FRIEZE DRAWN FLUSH" in said)
    span = elev["footprint"]["width_ft"]
    tol = 0.02 / 24.0
    assert abs(got["flush"][0]) < tol and abs(got["flush"][1] - span) < tol and got["flush"][2] == 0.0
    assert abs(got["proud"][0] + 3.0 / 12.0) < tol and abs(got["proud"][1] - span - 3.0 / 12.0) < tol
    assert abs(got["proud"][2] + 3.0) < 1e-6, got
    assert not got["flush"][3] and not got["proud"][3], "a stated frieze was said to be unstated"


def test_a_frieze_no_record_states_is_drawn_flush_and_said_on_both_surfaces(elev, tmp_path):
    ezdxf = pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
    EX = _m("export_dxf")
    el = copy.deepcopy(elev)
    el["eave_cornice"]["frieze_projection_in"] = None
    ink, pl, said = _svg(el, "S", tmp_path, "absent")
    (fz,) = [it for it in ink.select("rect") if {"bd", "fz"} <= set(it.classes)]
    assert abs(_box_ft(pl, fz)[0]) < 0.02 / 24.0, "an unstated frieze drawn anywhere but flush"
    assert "FRIEZE DRAWN FLUSH WITH THE WALL — NO RECORD STATES" in said
    path = str(tmp_path / "absent.dxf")
    assert "error" not in EX.export_elevation_dxf(el, path, face="S")
    texts = " ".join(e.dxf.text for e in ezdxf.readfile(path).modelspace().query("TEXT"))
    assert "FRIEZE DRAWN FLUSH WITH THE WALL" in texts, "the DXF did not say what the sheet says"


def test_the_frieze_projection_is_read_off_the_pack_and_not_written_in(monkeypatch):
    """`eave_cornice` reads the frieze member's own `projection_parts` through the engine, so a
    pack stating another figure moves it. Driven on a copy of the pack: the published one says 0."""
    EL, PE = _m("elevation"), _m("proportion_engine")
    fac = PE.resolve("facade-classical")
    gib = PE.resolve(EL.GIBBS_ORDER_PACK_ID)
    base = EL.eave_cornice(fac, gib, module_in=144.0)
    assert base["frieze_projection_in"] == 0.0, "the premise: the pack states the frieze flush"
    f2 = copy.deepcopy(fac)
    (m,) = [m for m in f2["assemblies"]["elevation"]["members"] if m["id"] == "frieze"]
    m["projection_parts"] = 0.5
    assert EL.eave_cornice(f2, gib, module_in=144.0)["frieze_projection_in"] == pytest.approx(6.0)
    del m["projection_parts"]
    assert EL.eave_cornice(f2, gib, module_in=144.0)["frieze_projection_in"] is None


# ------------------------------------------------------------------ the sheet
def test_the_sheet_draws_a_line_at_every_division_and_no_other(elev, tmp_path):
    ink, pl, _said = _svg(elev, "S", tmp_path)
    cm = _m("elevation").cornice_marks(elev, "S")
    lines = {it.attrs.get("data-member"): IR.to_model(pl, *it.points(n=1)[0])[1]
             for it in ink.items if "cm" in it.classes}
    want = {m["id"]: m["h0"] for m in cm["members"][1:]}
    assert set(lines) == set(want) and len(want) == 7
    assert all(abs(lines[k] - want[k]) < 0.02 / pl["px_per_ft"] for k in want), (lines, want)
    # and they are INK: a class with no stroke rule draws nothing, which is how the first draft of
    # these lines went onto the sheet -- present in the file and absent from the drawing
    for it in ink.items:
        if "cm" in it.classes:
            assert (it.style.get("stroke") or "none") != "none" and float(it.style.get("stroke-width") or 0) > 0


def test_the_frieze_and_the_box_meet_on_one_printed_edge(elev, tmp_path):
    """Written from their rounded edges: the frieze's top IS the cornice's soffit."""
    ink, _pl, _said = _svg(elev, "S", tmp_path)
    (fz,) = [it for it in ink.select("rect") if {"bd", "fz"} <= set(it.classes)]
    (box,) = [it for it in ink.select("rect") if {"bd", "w-prof"} <= set(it.classes)]
    assert fz.bbox()[1] == box.bbox()[3], (fz.bbox(), box.bbox())


@pytest.mark.parametrize("face", ["S", "E"])
def test_a_stack_in_front_of_the_face_is_painted_over_the_cornice_and_one_behind_under_it(elev, face, tmp_path):
    """The nearer of two overlapping marks is painted last. On the gable end the exterior stack
    stands in front of the wall and the cornice returns against it; on the front the same stack is
    behind the cornice's return at the corner. Both are the Tidewater record's own faces."""
    ink, pl, _said = _svg(elev, face, tmp_path)
    (box,) = [it for it in ink.select("rect") if {"bd", "w-prof"} <= set(it.classes)]
    bx = _box_ft(pl, box)
    over = [it for it in ink.items if "ch" in it.classes and it.tag in ("polygon", "rect", "path")
            and min(_box_ft(pl, it)[2], bx[2]) > max(_box_ft(pl, it)[0], bx[0])
            and min(_box_ft(pl, it)[3], bx[3]) > max(_box_ft(pl, it)[1], bx[1])]
    assert over, "the premise: a stack overlaps the cornice on this face"
    for it in over:
        assert (it.index > box.index) == (face == "E"), (face, it.index, box.index)


# ------------------------------------------------------------------ the DXF
def test_the_dxf_draws_each_member_division_carrying_its_member(elev, tmp_path):
    ezdxf = pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
    EX = _m("export_dxf")
    path = str(tmp_path / "e.dxf")
    assert "error" not in EX.export_elevation_dxf(elev, path, face="S")
    msp = ezdxf.readfile(path).modelspace()
    cm = _m("elevation").cornice_marks(elev, "S")
    got = {}
    for e in msp.query("LINE"):
        if e.dxf.layer == "TDL-ELEV-CORNICE-MEMBER":
            x = "".join(str(v) for _c, v in e.get_xdata("TDL"))
            got[json.loads(x[x.index("{"):])["member"]] = e.dxf.start[1]
    want = {m["id"]: m["h0"] * 12.0 for m in cm["members"][1:]}
    assert set(got) == set(want)
    assert all(abs(got[k] - want[k]) < 1e-6 for k in want), (got, want)
    (box,) = [e for e in msp.query("LWPOLYLINE") if e.dxf.layer == "TDL-ELEV-CORNICE"]
    assert min(p[1] for p in box.get_points()) == pytest.approx(cm["cornice"]["h0"] * 12.0), (
        "the cornice's box stands on the frieze, not on the wall head")


# ------------------------------------------------------------------ the teeth, driven
def test_teeth_laid_between_anchors_a_whole_number_of_pitches_apart_are_one_row():
    PROF = _m("profiles")
    cs = [69.5, 177.5, 285.5, 393.5, 501.5]
    rp = PROF.repeat_positions(571.0, spacing_in=27.0, width_in=4.0, centre_on=cs)
    xs = [t["centre"] for t in rp["teeth"]]
    assert not rp["solid"] and all(any(abs(x - c) < 1e-9 for x in xs) for c in cs)
    assert {round(b - a, 9) for a, b in zip(xs, xs[1:])} == {27.0}, "a second row laid inside the first"
    assert xs[0] - 2.0 >= 0.0 and xs[-1] + 2.0 <= 571.0 and xs[0] < 27.0 and 571.0 - xs[-1] < 27.0 + 2.0


def test_teeth_whose_anchors_are_not_a_whole_number_of_pitches_apart_are_refused_with_the_figure():
    """The Tidewater front's own numbers: bays 108 in apart, the record's 25.58 in pitch. The old
    layout returned 33 teeth here, in pairs 5.68 in apart."""
    PROF = _m("profiles")
    rp = PROF.repeat_positions(571.0, spacing_in=25.58, width_in=4.0,
                               centre_on=[69.5, 177.5, 285.5, 393.5, 501.5])
    assert rp["solid"] and not rp["teeth"]
    assert "108.00 in apart are 4.22 pitches of 25.58 in" in rp["reason"], rp["reason"]


def test_anchors_that_all_fall_off_the_run_lay_a_centred_band_and_not_an_empty_one():
    """The old code took `centre_on` as given even when every anchor fell off the run, and
    returned `solid: False` with no teeth at all -- a band claimed as laid and drawn empty."""
    PROF = _m("profiles")
    off = PROF.repeat_positions(571.0, spacing_in=27.0, width_in=4.0, centre_on=[-500.0, 900.0])
    none = PROF.repeat_positions(571.0, spacing_in=27.0, width_in=4.0)
    assert not off["solid"] and off["teeth"] == none["teeth"] and len(none["teeth"]) == 21
