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


def test_a_record_with_no_cornice_draws_none_and_says_why(elev, tmp_path):
    """A record dimensioning no eave cornice: nothing drawn, and the reason SAID on the sheet.

    The reason rode on `cornice_marks` and no surface printed it (WP-15.8's audit, auditor D), and
    the sheet could not draw such a record at all -- its profile inset read `members[0]` and
    raised. No shipped record reaches this (`build_elevation` sums a cornice's height into the true
    eave, so every record it builds has one), so it is DRIVEN, with the shipped record as the
    control. The words are the test's own, not read back out of the function."""
    EL = _m("elevation")
    el = copy.deepcopy(elev)
    el["eave_cornice"]["members"] = []
    cm = EL.cornice_marks(el, "S")
    assert not cm["applicable"] and "no eave cornice" in cm["why"]
    for tag, rec, drawn in (("control", elev, True), ("none", el, False)):
        ink, _pl, said = _svg(rec, "S", tmp_path, tag)
        boxes = [it for it in ink.select("rect") if {"bd", "fz"} <= set(it.classes)
                 or {"bd", "w-prof"} <= set(it.classes)]
        lines = [it for it in ink.items if "cm" in it.classes]
        inset = [f for f in ink.frames() if f.get("id") == "inset"]
        assert bool(boxes) == bool(lines) == bool(inset) == drawn, (tag, len(boxes), len(lines), inset)
        assert ("CORNICE NOT DRAWN" in said and "NO EAVE CORNICE" in said) == (not drawn), tag
        assert ("SEE INSET FOR PROFILE" in said) == drawn, ("the legend points at an inset", tag)


def test_a_record_with_no_cornice_is_said_in_the_dxf_too(elev, tmp_path):
    ezdxf = pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
    EX = _m("export_dxf")
    el = copy.deepcopy(elev)
    el["eave_cornice"]["members"] = []
    # AND A RECORD WITH ITS MEMBERS AND NO HEIGHT (WP-15.8's audit pass, auditor ab601): the sheet
    # leaves the cornice and its inset out, and the DXF drew the full-size profile anyway and
    # titled the face "CORNICE None IN (8 MEMBERS)"
    nh = copy.deepcopy(elev)
    nh["eave_cornice"]["cornice_height_in"] = None
    assert nh["eave_cornice"]["members"], "the premise: the height-less record keeps its members"
    for tag, rec, drawn in (("control", elev, True), ("none", el, False), ("no-height", nh, False)):
        path = str(tmp_path / f"{tag}.dxf")
        assert "error" not in EX.export_elevation_dxf(rec, path, face="S")
        msp = ezdxf.readfile(path).modelspace()
        layers = {e.dxf.layer for e in msp}
        eave = {"TDL-ELEV-FRIEZE", "TDL-ELEV-CORNICE", "TDL-ELEV-CORNICE-MEMBER",
                "TDL-ELEV-CORNICE-PROFILE"} & layers
        assert bool(eave) == drawn, (tag, sorted(eave))
        said = " ".join(e.dxf.text if e.dxftype() == "TEXT" else e.plain_text().replace("\n", " ")
                        for e in msp.query("TEXT MTEXT"))
        assert ("CORNICE NOT DRAWN" in said and "NO EAVE CORNICE" in said) == (not drawn), tag
        assert ("MEMBERS)" in said) == drawn, ("the title counts the members of a cornice", tag)
        assert ("NO CORNICE DRAWN" in said) == (not drawn), tag


# ------------------------------------------------------------------ the frieze, driven
# EACH SURFACE IN A TEST OF ITS OWN (WP-15.8's audit, auditor B): these two tests called
# `importorskip("ezdxf")` at their top, so where ezdxf is absent -- every CI corpus shard -- their
# SHEET halves were skipped with the DXF's, and V25 cannot reach either case, because the pack
# states the frieze flush. A frieze drawn flush whatever the record stated passed 10 of 10 with the
# ezdxf import shadowed. The sheet halves need no ezdxf and run everywhere now.
def _frieze_driven(elev, tmp_path, proj):
    el = copy.deepcopy(elev)
    el["eave_cornice"]["frieze_projection_in"] = proj
    ink, pl, said = _svg(el, "S", tmp_path, "fz-%s" % proj)
    (fz,) = [it for it in ink.select("rect") if {"bd", "fz"} <= set(it.classes)]
    return el, _box_ft(pl, fz), said


def test_a_frieze_stated_proud_is_drawn_proud_on_the_sheet(elev, tmp_path):
    """No record states a frieze proud of the wall, so the figure is driven, with the flush one as
    the control: a surface that ignored the figure would draw the two alike."""
    span = elev["footprint"]["width_ft"]
    tol = 0.02 / 24.0
    _el, flush, said_flush = _frieze_driven(elev, tmp_path, 0.0)
    _el, proud, said_proud = _frieze_driven(elev, tmp_path, 3.0)
    assert abs(flush[0]) < tol and abs(flush[2] - span) < tol, flush
    assert abs(proud[0] + 3.0 / 12.0) < tol and abs(proud[2] - span - 3.0 / 12.0) < tol, proud
    assert "FRIEZE DRAWN FLUSH" not in said_flush and "FRIEZE DRAWN FLUSH" not in said_proud, (
        "a stated frieze was said to be unstated")


def test_a_frieze_stated_proud_is_drawn_proud_in_the_dxf(elev, tmp_path):
    ezdxf = pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
    EX = _m("export_dxf")
    west = {}
    for proj in (0.0, 3.0):
        el = copy.deepcopy(elev)
        el["eave_cornice"]["frieze_projection_in"] = proj
        path = str(tmp_path / f"fz-{proj}.dxf")
        assert "error" not in EX.export_elevation_dxf(el, path, face="S")
        (poly,) = [e for e in ezdxf.readfile(path).modelspace().query("LWPOLYLINE")
                   if e.dxf.layer == "TDL-ELEV-FRIEZE"]
        west[proj] = min(p[0] for p in poly.get_points())
    assert west[0.0] == 0.0 and abs(west[3.0] + 3.0) < 1e-6, west


def test_a_frieze_no_record_states_is_drawn_flush_and_said_on_the_sheet(elev, tmp_path):
    _el, box, said = _frieze_driven(elev, tmp_path, None)
    assert abs(box[0]) < 0.02 / 24.0, "an unstated frieze drawn anywhere but flush"
    assert "FRIEZE DRAWN FLUSH WITH THE WALL — NO RECORD STATES" in said


def test_a_frieze_no_record_states_is_said_in_the_dxf(elev, tmp_path):
    ezdxf = pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
    EX = _m("export_dxf")
    el = copy.deepcopy(elev)
    el["eave_cornice"]["frieze_projection_in"] = None
    path = str(tmp_path / "absent.dxf")
    assert "error" not in EX.export_elevation_dxf(el, path, face="S")
    # the notes are MTEXT since WP-15.8, broken to the drawing's width: a break reads as a space
    texts = " ".join(e.dxf.text if e.dxftype() == "TEXT" else e.plain_text().replace("\n", " ")
                     for e in ezdxf.readfile(path).modelspace().query("TEXT MTEXT"))
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
@pytest.mark.parametrize("face", ["S", "N", "E", "W"])
def test_the_sheet_draws_a_line_across_the_box_at_every_division_and_no_other(elev, face, tmp_path):
    """Each line is held by both of its ends and its run, not by its first point (WP-15.8's audit,
    auditors B and M): lines collapsed to nothing, stubs off the box and lines spanning the wall and
    not the cornice all passed when only the first point's height was read."""
    ink, pl, _said = _svg(elev, face, tmp_path)
    cm = _m("elevation").cornice_marks(elev, face)
    tol = 0.02 / pl["px_per_ft"]
    lines = {}
    for it in ink.items:
        if "cm" in it.classes:
            (x0, y0), (x1, y1) = it.points(n=1)[0], it.points(n=1)[-1]
            (u0, v0), (u1, v1) = IR.to_model(pl, x0, y0), IR.to_model(pl, x1, y1)
            lines[it.attrs.get("data-member")] = (v0, v1, min(u0, u1), max(u0, u1))
    want = {m["id"]: m["h0"] for m in cm["members"][1:]}
    assert set(lines) == set(want) and len(want) == 7, (face, sorted(lines))
    box = cm["cornice"]
    for k, h in want.items():
        v0, v1, u0, u1 = lines[k]
        assert abs(v0 - h) < tol and abs(v1 - h) < tol, (face, k, v0, v1, h)
        assert abs(u0 - box["u0"]) < tol and abs(u1 - box["u1"]) < tol, (face, k, u0, u1, box)
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
@pytest.mark.parametrize("face", ["S", "N", "E", "W"])
def test_the_dxf_draws_each_member_division_level_across_the_box_carrying_its_member(elev, face, tmp_path):
    """On every face, where this read the south face alone (WP-15.8's audit, C16: every E and W
    division 0.1 in high passed X4's print tolerance and this test, which looked only at S), and
    each line by both ends, its run and the member's own PROFILE as well as its id (C02 slanted,
    C03 half the span and C11 the member below's profile all passed)."""
    ezdxf = pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
    EX = _m("export_dxf")
    path = str(tmp_path / f"e-{face}.dxf")
    assert "error" not in EX.export_elevation_dxf(elev, path, face=face)
    msp = ezdxf.readfile(path).modelspace()
    cm = _m("elevation").cornice_marks(elev, face)
    box = cm["cornice"]
    got = {}
    for e in msp.query("LINE"):
        if e.dxf.layer == "TDL-ELEV-CORNICE-MEMBER":
            x = "".join(str(v) for _c, v in e.get_xdata("TDL"))
            said = json.loads(x[x.index("{"):])
            got[said["member"]] = (e.dxf.start, e.dxf.end, said.get("profile"))
    want = {m["id"]: m for m in cm["members"][1:]}
    assert set(got) == set(want), (face, sorted(got))
    for k, m in want.items():
        (a0, h0, _z0), (a1, h1, _z1), profile = got[k][0], got[k][1], got[k][2]
        assert abs(h0 - m["h0"] * 12.0) < 1e-6 and abs(h1 - m["h0"] * 12.0) < 1e-6, (face, k, h0, h1)
        assert abs(min(a0, a1) - box["u0"] * 12.0) < 1e-6 and abs(max(a0, a1) - box["u1"] * 12.0) < 1e-6, \
            (face, k, a0, a1)
        assert profile == m["profile"], (face, k, profile, m["profile"])
    (poly,) = [e for e in msp.query("LWPOLYLINE") if e.dxf.layer == "TDL-ELEV-CORNICE"]
    assert min(p[1] for p in poly.get_points()) == pytest.approx(box["h0"] * 12.0), (
        "the cornice's box stands on the frieze, not on the wall head")


# ------------------------------------------------------------------ the teeth, driven
def _toothed(elev, spacing_in=27.0, width_in=4.0):
    """The Tidewater record with a tooth width and a pitch planted on its modillion band: no pack
    states a tooth width, and no face's bays are a whole number of the record's 25.58 in pitch
    apart, so no shipped face lays a tooth (WP-15.7). 27 in is a quarter of the front's 108 in
    bay, so the front's anchors are four pitches apart and the band is laid."""
    el = copy.deepcopy(elev)
    band = next(m for m in el["eave_cornice"]["members"] if m["id"] == "corn_modillion")
    band["spacing_in"], band["width_in"] = spacing_in, width_in
    cor = el["eave_cornice"]
    spring = el["grade_to_true_eave_in"] / 12.0 - cor["cornice_height_in"] / 12.0
    # the band's height READ OFF THE RECORD here, never off `cornice_marks`' teeth, which is what
    # both surfaces draw from (a band whose foot is its top drew teeth of no height, C05)
    return el, (spring + band["y_bottom_in"] / 12.0, spring + band["y_top_in"] / 12.0)


def test_a_toothed_band_laid_is_drawn_at_the_bands_own_height_on_the_sheet(elev, tmp_path):
    """WP-15.8's audit (auditor M, C04 and C05): the teeth were held only along the band, so teeth
    drawn at the frieze's height, or at no height, passed. Driven, with the premise asserted."""
    el, (h0, h1) = _toothed(elev)
    t = _m("elevation").cornice_marks(el, "S")["teeth"]
    assert t and not t["solid"] and len(t["teeth"]) >= 10, ("the premise: the band is laid", t)
    ink, pl, said = _svg(el, "S", tmp_path, "teeth")
    tol = 0.02 / pl["px_per_ft"]
    teeth = [_box_ft(pl, it) for it in ink.select("rect") if {"bd", "w-fine"} <= set(it.classes)]
    assert len(teeth) == len(t["teeth"]), (len(teeth), len(t["teeth"]))
    for (u0, v0, u1, v1), want in zip(sorted(teeth), t["teeth"]):
        assert abs(v0 - h0) < tol and abs(v1 - h1) < tol, ((v0, v1), (h0, h1))
        assert abs(u0 - want["u0"]) < tol and abs(u1 - want["u1"]) < tol, ((u0, u1), want)
    assert "MODILLION BAND DRAWN SOLID" not in said, "a band laid is not said to be drawn solid"


def test_a_toothed_band_laid_is_drawn_in_inches_at_its_height_in_the_dxf(elev, tmp_path):
    """C06: the teeth written in FEET where the drawing is in inches passed, because no test read
    the DXF's tooth layer at all."""
    ezdxf = pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
    el, (h0, h1) = _toothed(elev)
    t = _m("elevation").cornice_marks(el, "S")["teeth"]
    path = str(tmp_path / "teeth.dxf")
    assert "error" not in _m("export_dxf").export_elevation_dxf(el, path, face="S")
    got = sorted((min(p[0] for p in e.get_points()), min(p[1] for p in e.get_points()),
                  max(p[0] for p in e.get_points()), max(p[1] for p in e.get_points()))
                 for e in ezdxf.readfile(path).modelspace().query("LWPOLYLINE")
                 if e.dxf.layer == "TDL-ELEV-CORNICE-TOOTH")
    assert len(got) == len(t["teeth"]) >= 10, (len(got), len(t["teeth"]))
    for (x0, y0, x1, y1), want in zip(got, t["teeth"]):
        assert abs(x0 - want["u0"] * 12.0) < 1e-6 and abs(x1 - want["u1"] * 12.0) < 1e-6, ((x0, x1), want)
        assert abs(y0 - h0 * 12.0) < 1e-6 and abs(y1 - h1 * 12.0) < 1e-6, ((y0, y1), (h0, h1))


def test_the_pitch_tolerance_is_in_inches_and_not_in_pitches():
    """C07: `repeat_positions` compared the drift in PITCHES against a tolerance stated in inches,
    27 times looser at a 27 in pitch. Anchors 108 in apart at a 26.9875 in pitch are 4.0019
    pitches apart: 0.05 in of drift, five times the tolerance, and a hundredth of it in pitches."""
    PROF = _m("profiles")
    cs = [69.5, 177.5, 285.5, 393.5, 501.5]
    drift = PROF.repeat_positions(571.0, spacing_in=26.9875, width_in=4.0, centre_on=cs)
    near = PROF.repeat_positions(571.0, spacing_in=26.999, width_in=4.0, centre_on=cs)
    assert drift["solid"] and not drift["teeth"], "0.05 in of drift laid as a whole number of pitches"
    assert not near["solid"] and near["teeth"], "0.004 in of drift, inside the tolerance, refused"


def test_the_cornice_shade_falls_at_its_soffit(elev, tmp_path):
    """C08: the report says the cornice's shade line moved to its own soffit, where its shadow falls
    on the frieze below; nothing held it there, and putting it back at the frieze's foot passed.
    The line spanning the cornice's box, read off the ink, stands on the box's lower edge."""
    ink, _pl, _said = _svg(elev, "S", tmp_path)
    (box,) = [it for it in ink.select("rect") if {"bd", "w-prof"} <= set(it.classes)]
    (fz,) = [it for it in ink.select("rect") if {"bd", "fz"} <= set(it.classes)]
    bx = box.bbox()
    under = [it for it in ink.items if "shade" in it.classes and it.tag == "line"
             and abs(it.bbox()[0] - bx[0]) < 0.05 and abs(it.bbox()[2] - bx[2]) < 0.05]
    assert len(under) == 1, ("the premise: one shade line across the cornice's box", len(under))
    assert abs(under[0].bbox()[1] - bx[3]) < 0.05 and abs(fz.bbox()[3] - bx[3]) > 1.0, (
        under[0].bbox(), bx, fz.bbox())


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
