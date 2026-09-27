"""The bay grid is drawn on a module somebody stated, or the sheet says whose default it is (WP-14.4).

`geometry.derive_footprint` lays the footprint on the parti's own `bay_module_ft`, or on 10 ft when
no parti states one -- and fifteen of the sixteen shipped plans name no parti. The working sheet
drew that grid and labelled its lines, both registers drew the walls on it as bearing bodies, and
nothing on either plate said the module was the placer's own. The record now carries who stated it
(`geometry_report.bay_module`), `disclosures.bay_module` is the one line both surfaces print, and a
record carrying no module at all gets no grid rather than a silent 10 ft one.
"""
import copy
import json
import os
import re
import sys
import tempfile

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache as mc  # noqa: E402

G = mc.load("geometry", os.path.join(ROOT, "build", "geometry.py"))
RP = mc.load("render_plan", os.path.join(ROOT, "build", "render_plan.py"))
DISC = mc.load("disclosures", os.path.join(ROOT, "build", "disclosures.py"))

LINE = "BAY GRID AT THE PLACER'S DEFAULT"


def _placed(name, engine="heuristic", **kw):
    sub = "plans" if not name.startswith(("good-", "bad-")) else os.path.join("plans", "reference")
    plan = json.load(open(os.path.join(ROOT, sub, name + ".json")))
    G._SOLVE_CACHE.clear()
    return G.solve(copy.deepcopy(plan), engine=engine, **kw)


def _sheet(placed):
    d = tempfile.mkdtemp()
    out = os.path.join(d, "p.svg")
    RP.render(placed, out)
    return open(out).read()


def test_a_parti_that_states_its_module_is_named_and_no_line_is_printed():
    p = _placed("tidewater-georgian-careful")
    bm = p["geometry_report"]["bay_module"]
    assert bm["stated_by"] == p["parti"] and bm["ft"] == p["footprint"]["bay_module_ft"], bm
    assert not [ln for ln in DISC.banner(p) if ln["id"] == "bay-module"]
    assert LINE not in _sheet(p)


def test_a_plan_naming_no_parti_is_drawn_on_the_default_and_says_so():
    p = _placed("spec-builder-colonial")
    assert not p.get("parti"), "the premise: this plan names no parti"
    bm = p["geometry_report"]["bay_module"]
    assert bm["stated_by"] is None and bm["ft"] == 10.0, bm
    assert [ln for ln in DISC.banner(p) if ln["id"] == "bay-module"], "the default is not said"
    svg = _sheet(p)
    assert LINE in svg and svg.count('class="gd"') > 2, "the grid is drawn and its module said"


def test_both_record_writers_carry_it():
    """The proving engine writes its record through `_finish`, the search through
    `write_record`; a disclosure wired into one is the defect `_disclose` exists to prevent."""
    p = _placed("bad-04-log-cabin", engine="cp", time_limit_s=8)
    assert p["geometry_report"]["solver"]["engine"] == "cp-sat", "the premise: the prover placed it"
    assert p["geometry_report"]["bay_module"]["stated_by"] is None


def test_a_record_with_no_module_gets_no_grid_and_says_so():
    """DRIVEN: every record the placer writes carries a module, so a record without one -- one
    ingested from a drawing, or placed before the field existed -- is made by hand."""
    p = _placed("spec-builder-colonial")
    assert p["footprint"].get("bay_module_ft"), "the premise: the placed record carries a module"
    before = _sheet(p)
    q = copy.deepcopy(p)
    del q["footprint"]["bay_module_ft"]
    q["geometry_report"].pop("bay_module", None)
    after = _sheet(q)
    # BAY LINES BY WHAT THEY ARE (WP-14.6, G5): `.gd` is shared with the plate's end lines and the
    # dimension runs, so this asserted "fewer" -- and a sheet drawing half its bay lines on a module
    # nobody stated passed it. A bay line carries `data-bay`, and with no module there are none.
    grid = lambda s: len(re.findall(r'<line class="gd" data-bay=', s))  # noqa: E731
    assert grid(before) > 0, "the premise: the placed record's sheet draws bay lines"
    assert grid(after) == 0, "a bay line was drawn on a module the record does not state"
    assert "NO BAY MODULE ON THE RECORD" in after
    assert "NO BAY MODULE ON THE RECORD" not in before


def test_the_app_prints_the_served_line_and_spells_none_of_its_own():
    """WP-14.6, audit F15. `disclosures.bay_module` is the one line both surfaces print -- the plate
    draws it, the bench shows it in the strip `placement.disclosures` carries -- and the bench
    sheet's caption spelled the same disclosure a third time in its own words ("the placer's own
    ... default -- no parti states a module"). A second spelling of a disclosure is how two of
    them come to disagree; the app may print what it is served and may not compose this one."""
    import subprocess
    src = subprocess.run(["git", "ls-files", "workbench/app/src"], cwd=ROOT, capture_output=True,
                         text=True, check=True).stdout.split()
    hits = []
    for f in src:
        if f.endswith((".js", ".jsx", ".mjs")) and ".test." not in f:
            text = open(os.path.join(ROOT, f), encoding="utf-8").read()
            if re.search(r"no parti states a module", text, re.I):
                hits.append(f)
    assert not hits, "the app spells the bay-module disclosure itself: %s" % hits
    # and the line it is served is the disclosure's own
    assert "NO PARTI STATES A MODULE" in DISC.bay_module(
        {"geometry_report": {"bay_module": {"ft": 10.0, "stated_by": None}}})["text"]


# ---------------------------------------------------------------------------------------------------
# THE OTHER DRAWINGS OF THE SAME PLAN (audit, 27 Sep 2026; auditor D, F9). WP-14.4 made the plan
# sheet refuse the grid and say so; the DXF went on drawing a 10 ft grid under "BAYS OF ? FT" and the
# bearing plate -- whose subject is the walls read off the module -- said nothing. Each surface now
# says the one fact (`disclosures.no_bay_module`) with its own consequence, and a surface on which the
# module decides nothing drawn says nothing on the plate.

ST = mc.load("structure", os.path.join(ROOT, "build", "structure.py"))
RS = mc.load("render_section", os.path.join(ROOT, "build", "render_section.py"))
EL = mc.load("elevation", os.path.join(ROOT, "build", "elevation.py"))
REL = mc.load("render_elevation", os.path.join(ROOT, "build", "render_elevation.py"))


def _withdrawn(name):
    p = _placed(name)
    assert p["footprint"].get("bay_module_ft"), "the premise: the placed record carries a module"
    q = copy.deepcopy(p)
    del q["footprint"]["bay_module_ft"]
    q["geometry_report"].pop("bay_module", None)
    return p, q


def _section(rec):
    return ST.build_section(copy.deepcopy(rec), None, geometry_result=rec)


def _bearing(sec, **kw):
    out = os.path.join(tempfile.mkdtemp(), "b.svg")
    RS.render_bearing_diagram(sec, out, **kw)
    return open(out, encoding="utf-8").read()


def _note_lines(svg):
    """The bearing plate's module note, as the lines it is drawn in, with each line's x.

    BY POSITION, NOT BY WORDING: the note is drawn last, so it is every `.dm` line from the one
    opening "NO BAY MODULE" to the end of the sheet. The first version picked continuation lines by
    how they began, and dropped a wrapped middle line -- a selector on the text being tested."""
    rows = re.findall(r'<text class="dm" x="([\d.]+)" y="([\d.]+)">([^<]*)</text>', svg)
    i = next((i for i, r in enumerate(rows) if r[2].startswith("NO BAY MODULE")), None)
    if i is None:
        return []
    ys = [float(y) for _x, y, _t in rows[i:]]
    assert all(abs(b - a - 10.0) < 1e-6 for a, b in zip(ys, ys[1:])), ("not one note, 10 px a line", ys)
    last = re.search(r'<text[^>]*>([^<]*)</text>\s*</svg>\s*$', svg)
    assert last and last.group(1) == rows[-1][2], "the note is not the last thing on the sheet"
    return [(float(x), t) for x, _y, t in rows[i:]]


def _joined(svg):
    return " ".join(t for _x, t in _note_lines(svg))


def test_the_section_records_whether_its_module_is_the_records():
    p, q = _withdrawn("spec-builder-colonial")
    assert _section(p)["bay_module"] == {"ft": p["footprint"]["bay_module_ft"], "on_record": True}
    assert _section(q)["bay_module"] == {"ft": 10.0, "on_record": False}


def test_the_bearing_plate_says_it_where_the_record_states_no_module():
    p, q = _withdrawn("spec-builder-colonial")
    before, after = _bearing(_section(p)), _bearing(_section(q))
    assert "NO BAY MODULE" not in before
    assert _joined(after) == DISC.no_bay_module(DISC.bearing_off_default(10.0))
    # the walls are the same walls: the note is the only thing the missing module changes here
    assert re.findall(r'class="(?:wl|fl)"', before) == re.findall(r'class="(?:wl|fl)"', after)


def _canvas(svg):
    return (float(re.search(r'<svg[^>]* width="([\d.]+)"', svg).group(1)),
            float(re.search(r'<svg[^>]* height="([\d.]+)"', svg).group(1)))


def test_a_narrow_bearing_plate_wraps_the_note_and_grows_rather_than_running_it_off():
    """DRIVEN: a one-level plate at a small scale is narrower than the sentence. The note must
    wrap inside the canvas (7.5 px monospace, 4.6 px a character -- the renderer's own measure)
    and the canvas must grow by exactly the extra lines."""
    _p, q = _withdrawn("spec-builder-colonial")
    sec = _section(q)
    sec1 = dict(sec, levels=sec["levels"][:1])
    wide, narrow = _bearing(sec1), _bearing(sec1, scale=3.0)
    lines = _note_lines(narrow)
    assert len(lines) > 1, ("the premise: the sentence does not fit this plate on one line", lines)
    w, h = _canvas(narrow)
    for x, t in lines:
        assert x + len(t) * 4.6 <= w, ("a note line runs off the sheet", t, w)
    assert _joined(narrow) == _joined(wide)
    # the plate's own sizing, with the extra lines added and nothing else
    no_note = _bearing(_section(_withdrawn("spec-builder-colonial")[0]) | {"levels": sec["levels"][:1]},
                       scale=3.0)
    assert h == _canvas(no_note)[1] + 10 * (len(lines) - 1)


def test_the_dxf_draws_no_grid_and_says_only_that():
    ezdxf = pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
    EX = mc.load("export_dxf", os.path.join(ROOT, "build", "export_dxf.py"))
    p, q = _withdrawn("spec-builder-colonial")
    d = tempfile.mkdtemp()
    got = {}
    for tag, rec in (("before", p), ("after", q)):
        res = EX.export_plan_dxf(copy.deepcopy(rec), os.path.join(d, tag + ".dxf"), solved=rec)
        assert "error" not in res, res
        msp = ezdxf.readfile(os.path.join(d, tag + ".dxf")).modelspace()
        got[tag] = (sum(1 for e in msp if e.dxftype() == "LINE" and e.dxf.layer == "TDL-GRID"),
                    [e.dxf.text for e in msp if e.dxftype() == "TEXT" and "BAY MODULE" in e.dxf.text])
    W, bm = p["footprint"]["width_ft"] * 12.0, p["footprint"]["bay_module_ft"] * 12.0
    want = sum(1 for k in range(1, 100) if k * bm < W - 0.1)
    assert got["before"] == (want, []) and want > 0, got["before"]
    assert got["after"] == (0, [DISC.no_bay_module(DISC.NO_BAY_GRID)]), got["after"]
    assert "BEARING" not in got["after"][1][0], "the DXF tells no wall bearing, so it claims nothing about them"


def test_the_elevation_says_it_in_its_record_and_not_on_its_plate():
    """The storey windows are sized off a head and a sill; the module decides only the room-width
    cross-check the record carries beside them. So the record says which module that read, and the
    plate -- whose ink the module does not touch -- is BYTE-IDENTICAL with the module withdrawn,
    which is the proof the plate had nothing to say."""
    p, q = _withdrawn("spec-builder-colonial")
    ea = EL.build_elevation(copy.deepcopy(p), section=_section(p))
    eb = EL.build_elevation(copy.deepcopy(q), section=_section(q))
    tail = "the placer's default 10 ft: the record states none."
    assert all(not sw["room_width_diagnostic_note"].endswith(tail) for sw in ea["storey_windows"])
    assert all(sw["room_width_diagnostic_note"].endswith(tail) for sw in eb["storey_windows"])
    d = tempfile.mkdtemp()
    for face in ("S", "E"):
        REL.render_elevation(ea, os.path.join(d, "a.svg"), face=face)
        REL.render_elevation(eb, os.path.join(d, "b.svg"), face=face)
        a, b = (open(os.path.join(d, f), encoding="utf-8").read() for f in ("a.svg", "b.svg"))
        assert a == b and "NO BAY MODULE" not in b, face


def test_the_sentence_is_spelled_once():
    """`disclosures.no_bay_module` is the only string in `build/` that says it -- read off the
    syntax tree, so a comment quoting it is not a second spelling and a literal anywhere is."""
    import ast
    import subprocess
    files = subprocess.run(["git", "ls-files", "-co", "--exclude-standard", "build/*.py"], cwd=ROOT,
                           capture_output=True, text=True, check=True).stdout.split()
    hits = set()
    for f in sorted(files):
        tree = ast.parse(open(os.path.join(ROOT, f), encoding="utf-8").read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) \
                    and "NO BAY MODULE ON THE RECORD" in node.value:
                hits.add(f)
    assert hits == {"build/disclosures.py"}, hits
    # and the plan sheet's own line kept its bytes through the move
    assert DISC.no_bay_module(DISC.NO_BAY_GRID, DISC.bearing_off_default(10.0)) == (
        "NO BAY MODULE ON THE RECORD — NO BAY GRID DRAWN; THE BEARING WALLS ARE READ OFF THE "
        "PLACER'S DEFAULT 10 FT")


def test_the_plan_sheet_prints_the_one_spelling_in_both_registers():
    """The plan sheet's line went through the move byte for byte; this holds its CALL SITE to the
    sentence, which the older guard above reads only for its first five words."""
    _p, q = _withdrawn("spec-builder-colonial")
    want = DISC.no_bay_module(DISC.NO_BAY_GRID, DISC.bearing_off_default(10.0))
    for reg in RP.REGISTERS:
        out = os.path.join(tempfile.mkdtemp(), "p.svg")
        RP.render(q, out, register=reg)
        got = re.findall(r">([^<]*BAY MODULE ON THE RECORD[^<]*)<", open(out, encoding="utf-8").read())
        assert got == [want], (reg, got)
