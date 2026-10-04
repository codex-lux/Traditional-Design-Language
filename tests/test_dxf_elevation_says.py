"""THE DXF ELEVATION SAYS AND HIDES WHAT THE SHEET DOES (Phase 15, WP-15.8, the audit).

Two defects of one kind, found by auditors D and M:

- The DXF wrote the five sentences it had been handed one at a time -- the main block, the
  stacks, the wall beside the doorcase, the cornice -- and none of the rest. So the CAD file of
  the Tidewater front never said that its 22 in stack is a judgment, although its stack sentence
  leaves the size out BECAUSE the judgment line states it, nor which of its eleven openings were
  refused and why. Each note was one TEXT line however long it ran, the longest 223 characters,
  far past the drawing. `elevation.face_notes` is the one list both surfaces write now, and the
  DXF breaks each note to the drawing's width as one MTEXT.
- The DXF had no paint order. Every stack was drawn after the roof and nothing was masked, so on
  a gable face the cornice members, the box, the frieze, the rake and the wall head ran through
  the stack standing in front of them, and on a long face the stack's inner edge ran through the
  cornice's return at the corner. A CAD file draws no fill, so where the sheet paints one thing
  over another the DXF sets a WIPEOUT between them, on its own layer.

The sheet is read off its ink here, never out of `face_notes`, so a line the function lost from
both surfaces is a question for the sheet's own guards and a line the DXF lost is this file's.
"""
import glob
import itertools
import json
import os
import re
import sys
import tempfile

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import modcache  # noqa: E402
import inkread as IR  # noqa: E402

ezdxf = pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")


def _L(n):
    return modcache.load(n, os.path.join(ROOT, "build", n + ".py"))


GEO, ST, RF, EL, RE, DX = (_L(n) for n in ("geometry", "structure", "roof", "elevation",
                                           "render_elevation", "export_dxf"))
FACES = ("S", "N", "E", "W")


def _elevation(plan):
    saved = GEO._SOLVE_CACHE
    GEO._SOLVE_CACHE = {}
    try:
        placed = GEO.solve(plan, None, 250, engine="heuristic")
    finally:
        GEO._SOLVE_CACHE = saved
    sec = ST.build_section(placed, None, geometry_result=placed)
    if "error" in sec:
        return None
    rf = RF.build_roof(placed, None, section=sec)
    el = EL.build_elevation(placed, None, section=sec, roof=rf)
    return el if el.get("applicable", True) and "error" not in el else None


@pytest.fixture(scope="module")
def corpus():
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "plans", "*.json"))) + \
            sorted(glob.glob(os.path.join(ROOT, "plans", "reference", "*.json"))):
        with open(f, encoding="utf-8") as fh:
            el = _elevation(json.load(fh))
        if el is not None:
            out[os.path.basename(f)[:-5]] = el
    return out


def _sheet(el, face):
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "e.svg")
        RE.render_elevation(el, path, face=face)
        with open(path, encoding="utf-8") as fh:
            return fh.read()


def _sheet_notes(svg):
    """The sentences the sheet sets beneath its drawing, read off the ink: the monospaced lines
    standing below the legend's GROUND line at its left edge, in the order they are set."""
    lines = [(it.anchor(), " ".join((t or "").split())) for t, _a, it in IR.Ink(svg).texts()
             if "dm" in it.classes]
    (gx, gy), = [a for a, t in lines if t.startswith("GROUND ")]
    return [t for (x, y), t in lines if abs(x - gx) < 0.01 and y > gy + 0.01 and t]


_OUT = []
_SEQ = itertools.count()


@pytest.fixture(scope="module", autouse=True)
def _outdir(tmp_path_factory):
    """Every DXF this file writes goes to pytest's own temporary directory, never the tree."""
    _OUT.append(str(tmp_path_factory.mktemp("dxf-says")))
    yield
    _OUT.pop()


def _dxf(el, face):
    path = os.path.join(_OUT[-1], "%s-%d.dxf" % (face, next(_SEQ)))
    res = DX.export_elevation_dxf(el, path, face=face)
    assert "error" not in res, res
    return path


def _dxf_notes(msp):
    """The MTEXT notes beneath the drawing, top to bottom, each read back whole."""
    return [" ".join(e.plain_text().split())
            for e in sorted(msp.query("MTEXT"), key=lambda e: -e.dxf.insert[1])]


# ------------------------------------------------------------------ what the drawing says
def test_the_dxf_says_every_line_the_sheet_says_beneath_the_drawing_in_its_order(corpus):
    tide = corpus["tidewater-georgian-careful"]
    front = _sheet_notes(_sheet(tide, "S"))
    # the premise, in words this test states: the Tidewater front says its stack is a judgment and
    # names the openings it does not draw, and why -- the lines the DXF never wrote
    for words in ("A JUDGMENT, NOT A MEASUREMENT", "OPENING(S) ON THIS FACE NOT DRAWN",
                  "THE PLACER REFUSED THEM"):
        assert any(words in t for t in front), ("the premise: the sheet says", words, front)
    faces = 0
    for pid, el in sorted(corpus.items()):
        for face in FACES:
            want = _sheet_notes(_sheet(el, face))
            path = _dxf(el, face)
            got = _dxf_notes(ezdxf.readfile(path).modelspace())
            assert got == want, (pid, face, [w for w in want if w not in got][:3],
                                 [g for g in got if g not in want][:3])
            faces += 1
    assert faces >= 40, ("the premise: the corpus draws its elevations", faces)


def test_no_note_runs_past_the_drawing_or_prints_through_the_next(corpus):
    """A note was one TEXT line whatever its length: the Tidewater front's longest ran 223
    characters, 1,070 in of text at 8 in under a drawing 590 in wide. Each is broken to the
    drawing's width now, at the 0.6 of its height a capital takes, and each starts below the
    last one's final line."""
    el = corpus["tidewater-georgian-careful"]
    for face in FACES:
        msp = ezdxf.readfile(_dxf(el, face)).modelspace()
        drawn = [e for e in msp if e.dxftype() in ("LWPOLYLINE", "LINE")]
        xs = [p[0] for e in drawn for p in (e.get_points() if e.dxftype() == "LWPOLYLINE"
                                            else (e.dxf.start, e.dxf.end))]
        width = max(xs) - min(xs)
        notes = sorted(msp.query("MTEXT"), key=lambda e: -e.dxf.insert[1])
        assert len(notes) >= 5, ("the premise: the face says several things", face, len(notes))
        for e in notes:
            h = e.dxf.char_height
            for ln in e.plain_text().split("\n"):
                assert len(ln) * 0.6 * h <= width + 1e-6, (face, len(ln), width, ln[:60])
        # THE PITCH IS THE FORMAT'S, READ OFF THE ENTITY, NEVER THE EXPORTER'S CONSTANT (WP-15.8's
        # audit, auditor ab601): this read `DX.MTEXT_PITCH`, so an exporter that set the pitch to
        # 1.0 -- and printed every note through the next -- moved the test's ruler with it and
        # stayed green. MTEXT sets a line 5/3 of its character height apart at a spacing factor of
        # 1.0, which is the DXF format's own figure, times the factor the entity itself carries.
        for a, b in zip(notes, notes[1:]):
            n = len(a.plain_text().split("\n"))
            factor = a.dxf.get("line_spacing_factor", 1.0)
            bottom = a.dxf.insert[1] - n * (5.0 / 3.0) * factor * a.dxf.char_height
            assert b.dxf.insert[1] <= bottom + 1e-6, ("two notes print through one another", face,
                                                      a.plain_text()[:40], b.plain_text()[:40])


def test_a_note_reads_back_as_what_it_was_given_whatever_it_holds():
    """A note carries room names, which are the record's strings. MTEXT gives meaning to a
    backslash, a brace, a caret (`^I` is a tab) and two percent signs (`%%d` is a degree sign), so
    each is written to read back as itself."""
    hostile = ["A {BRACE} AND A BACK\\SLASH", "100%%D AND %%%C AND 50%", "CARET ^I AND ^^ AND A^ B",
               "PLAIN — WITH A DASH AND `TICKS`", "X" * 300]
    with tempfile.TemporaryDirectory() as td:
        doc = ezdxf.new()
        msp = doc.modelspace()
        for i, s in enumerate(hostile):
            DX._note(msp, "0", s, 0, -100.0 * i, 500.0)
        doc.saveas(os.path.join(td, "n.dxf"))
        back = [e.plain_text().replace("\n", " ") for e in sorted(
            ezdxf.readfile(os.path.join(td, "n.dxf")).modelspace().query("MTEXT"),
            key=lambda e: -e.dxf.insert[1])]
    assert back == hostile, [(a, b) for a, b in zip(back, hostile) if a != b]


def test_a_control_character_in_a_record_string_is_written_as_the_replacement_character():
    """WP-15.8's audit, auditor E: a room id is a free string, and a NUL or a BEL in one reached
    the elevation DXF as the raw byte -- ezdxf writes it as it is, and many readers take a NUL for
    the end of the value. Both TEXT and MTEXT write U+FFFD in its place, and everything around it
    reads back as it was given."""
    given = "ROOM\x00ID AND\x07BELL\x1fEND\x7f"
    want = "ROOM\ufffdID AND\ufffdBELL\ufffdEND\ufffd"
    with tempfile.TemporaryDirectory() as td:
        doc = ezdxf.new()
        msp = doc.modelspace()
        DX._note(msp, "0", given, 0, 0, 500.0)
        DX._text(msp, "0", given, 0, -100.0)
        path = os.path.join(td, "c.dxf")
        doc.saveas(path)
        raw = open(path, "rb").read()
        back = ezdxf.readfile(path).modelspace()
        mt = [e.plain_text() for e in back.query("MTEXT")]
        tx = [e.dxf.text for e in back.query("TEXT")]
    assert b"\x00" not in raw and b"\x07" not in raw, "a control byte reached the file"
    assert mt == [want] and tx == [want], (mt, tx)


def test_the_generic_ingest_still_reads_an_elevation_dxf(corpus):
    """The WIPEOUT masks and the MTEXT notes are entities the ingest had never met in a TDL file.
    It reads closed polylines and text, and must still open one of these without complaint."""
    from ezdxf import recover
    IG = _L("ingest_dxf")
    el = corpus["tidewater-georgian-careful"]
    for face in ("S", "E"):
        path = _dxf(el, face)
        doc, auditor = recover.readfile(path)
        assert doc.modelspace().query("WIPEOUT"), ("the premise: this face masks something", face)
        assert not auditor.errors, (face, [str(e) for e in auditor.errors][:3])
        got = IG.extract(path)
        assert "error" not in got, (face, got.get("error"))
        assert got["counts"]["texts"] >= len(doc.modelspace().query("MTEXT")), (face, got["counts"])


# ------------------------------------------------------------------ what the drawing hides
def _order(msp):
    return {id(e): i for i, e in enumerate(msp)}


def _pts(e):
    return [(p[0], p[1]) for p in (e.get_points() if e.dxftype() == "LWPOLYLINE"
                                   else [(v[0], v[1]) for v in e.boundary_path_wcs()])]


def test_a_stack_beyond_the_corner_is_drawn_first_and_hidden_where_the_eave_passes_it(corpus):
    """The Tidewater front: a stack stands beyond each gable, and the cornice's return passes in
    front of it at the corner. The sheet paints the stack first and the eave over it; the DXF
    draws the stack before the wall and masks it under the eave, the mask reaching past the
    stack's inner edge, which lies ON the corner: a line on a wipeout's boundary is not hidden."""
    el = corpus["tidewater-georgian-careful"]
    msp = ezdxf.readfile(_dxf(el, "S")).modelspace()
    at = _order(msp)
    (wall,) = [e for e in msp.query("LWPOLYLINE") if e.dxf.layer == "TDL-ELEV-WALL"]
    (box,) = [e for e in msp.query("LWPOLYLINE") if e.dxf.layer == "TDL-ELEV-CORNICE"]
    stacks = [e for e in msp.query("LWPOLYLINE") if e.dxf.layer == "TDL-ELEV-STACK"]
    masks = [e for e in msp.query("WIPEOUT")]
    assert len(stacks) == 2, ("the premise: a stack beyond each gable", len(stacks))
    assert all(m.dxf.layer == "TDL-ELEV-MASK" for m in masks), [m.dxf.layer for m in masks]
    span = max(p[0] for p in wall.get_points())
    bh = [p[1] for p in box.get_points()]
    for st in stacks:
        assert at[id(st)] < at[id(wall)], "a stack beyond the corner is drawn over the wall"
        sx = [p[0] for p in st.get_points()]
        # the edge at the corner: the placement seats the square against the gable, to within
        # the rounding of the two records (0.048 in on the east)
        inner = min((min(sx), max(sx)), key=lambda x: min(abs(x), abs(x - span)))
        assert min(abs(inner), abs(inner - span)) < 0.1, ("the premise: the stack abuts", sx, span)
        cover = [m for m in masks
                 if min(p[0] for p in _pts(m)) < inner < max(p[0] for p in _pts(m))
                 and min(p[1] for p in _pts(m)) <= min(bh) + 1e-6
                 and max(p[1] for p in _pts(m)) >= max(bh) - 1e-6]
        assert cover, ("no mask hides the stack's inner edge under the eave", inner)
        assert all(at[id(st)] < at[id(m)] < at[id(box)] for m in cover), \
            "the mask stands between the stack and the eave drawn over it"


def test_a_stack_in_front_of_its_own_wall_is_drawn_last_over_a_mask_of_itself(corpus):
    """The Tidewater east gable: its own stack stands in front of the wall, over the frieze, the
    cornice's members and the rake. The sheet paints it last with a fill; the DXF sets a mask of
    its outline after everything else it draws and the stack over the mask. The west gable's
    stack stands directly behind it and the house hides the rest, so it is drawn on neither."""
    el = corpus["tidewater-georgian-careful"]
    sm = EL.stack_marks(el, "E")
    assert [m["relation"] for m in sm["marks"]] == ["front"] and sm["hidden"] == 1, (
        "the premise: the face's own stack in front, the far one hidden", sm["hidden"])
    msp = ezdxf.readfile(_dxf(el, "E")).modelspace()
    at = _order(msp)
    (front,) = [e for e in msp.query("LWPOLYLINE") if e.dxf.layer == "TDL-ELEV-STACK"]
    assert re.search(r'"relation":\s*"front"', "".join(str(v) for _c, v in front.get_xdata("TDL")))
    box = lambda pts: [round(f(p[i] for p in pts), 3) for i in (0, 1) for f in (min, max)]
    # THE STACK'S OWN MASK, BY ITS OUTLINE (re-cut 3 Oct 2026, the audit of WP-16.8's own diff):
    # this read the face's ONE wipeout, and every band is masked whole now, as the sheet paints it
    # opaque (auditor B's B10) -- so the face carries a mask per band besides the stack's own, and
    # each of those is a band's box, asserted below rather than ignored
    masks = list(msp.query("WIPEOUT"))
    assert all(m.dxf.layer == "TDL-ELEV-MASK" for m in masks), [m.dxf.layer for m in masks]
    own = [m for m in masks if box(_pts(m)) == box(front.get_points())]
    assert len(own) == 1, ("the mask is the stack's own outline, once", len(own))
    (own,) = own
    bands = [box(e.get_points()) for e in msp.query("LWPOLYLINE") if e.dxf.layer == "TDL-ELEV-BAND"]
    assert bands and all(box(_pts(m)) in bands for m in masks if m is not own), \
        "every other mask on this face is a band's own box"
    behind = [e for e in msp if e.dxf.layer in ("TDL-ELEV-WALL", "TDL-ELEV-ROOF", "TDL-ELEV-CORNICE",
                                                 "TDL-ELEV-FRIEZE", "TDL-ELEV-CORNICE-MEMBER",
                                                 "TDL-ELEV-OPENING", "TDL-ELEV-SASH", "TDL-ELEV-BAND")]
    assert {e.dxf.layer for e in behind} >= {"TDL-ELEV-WALL", "TDL-ELEV-ROOF", "TDL-ELEV-CORNICE",
                                             "TDL-ELEV-FRIEZE", "TDL-ELEV-BAND"}, \
        "the premise: the face draws its eave and its bands"
    assert max(at[id(e)] for e in behind) < at[id(own)] < at[id(front)]
