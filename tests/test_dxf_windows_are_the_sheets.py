"""THE DXF DRAWS THE WINDOWS THE PLAN SHEET DRAWS, WHERE IT DRAWS THEM (audit, 27 Sep 2026).

Auditor D (F8), on `oq/the-dxf-draws-its-own-windows`: the plan DXF spaced every declared window
unit evenly along its room's edge (`t = (k+1)/(cnt+1)`) on the FOOTPRINT's face and never read the
placement, so on the twelve drawable reference plans five drew a different number of windows from
the sheet, and every DXF drew units the placer had refused. It is the IFC's defect (D-F7) in the
drawing a drafter opens, and WP-6.4's rule answers both: one drawing set is one building.

The DXF now draws exactly `derive_openings`' windows -- the sheet's -- and looks up only each
unit's identity in the record for its XDATA. So every assertion below reads the DXF's LINEWORK
(where each line lies, how long it is) against the sheet, and the XDATA only for which unit a line
claims to be, which `import_dxf` then holds against the record: the round trip is asserted too.
The premise that both branches run -- units drawn and units the placer refused -- is asserted,
because a corpus in which nothing was refused would not test the half of the fix that matters.
"""
import copy
import glob
import json
import os
import re
import sys

import pytest

ezdxf = pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402


def _L(n):
    return modcache.load(n, os.path.join(ROOT, "build", n + ".py"))


GEO, EX, RP, IM = _L("geometry"), _L("export_dxf"), _L("render_plan"), _L("import_dxf")
PLANS = (sorted(glob.glob(os.path.join(ROOT, "plans", "*.json")))
         + sorted(glob.glob(os.path.join(ROOT, "plans", "reference", "*.json"))))
TOL = 0.01 * 12     # inches; every figure is written at three decimals of a foot or better
_HEAD = re.compile(r"^TDL::window::L(-?\d+)::(.+)::(\d+)::(\d+)/(\d+)$")


@pytest.fixture(scope="module")
def sheets(tmp_path_factory):
    saved = GEO._SOLVE_CACHE
    GEO._SOLVE_CACHE = {}
    out = {}
    try:
        for path in PLANS:
            with open(path, encoding="utf-8") as fh:
                plan = json.load(fh)
            placed = GEO.solve(copy.deepcopy(plan), None, 250, engine="heuristic")
            dxf = str(tmp_path_factory.mktemp("dxf") / "plan.dxf")
            res = EX.export_plan_dxf(copy.deepcopy(plan), dxf, solved=placed)
            if "error" in res:
                continue
            out[os.path.basename(path)[:-5]] = (plan, placed, res, dxf)
    finally:
        GEO._SOLVE_CACHE = saved
    assert len(out) >= 10, sorted(out)
    return out


def _dxf_windows(dxf):
    """(level, room, wall-axis, at_in, edge_in, length_in) of every window line, read off the
    line itself; the room and level off its XDATA header."""
    got = []
    for e in ezdxf.readfile(dxf).modelspace():
        if e.dxftype() != "LINE" or not e.dxf.layer.endswith("-WINDOW"):
            continue
        head = dict(e.get_xdata("TDL"))[1000] if e.has_xdata("TDL") else ""
        m = _HEAD.match(head)
        assert m, ("a window line carrying no unit identity", head)
        (x0, y0, _), (x1, y1, _) = e.dxf.start, e.dxf.end
        if abs(y1 - y0) < 1e-6:        # along x: a S or N wall
            got.append((int(m.group(1)), m.group(2), "x", (x0 + x1) / 2, y0, abs(x1 - x0)))
        else:
            assert abs(x1 - x0) < 1e-6, ("a window line that is neither along x nor along y", head)
            got.append((int(m.group(1)), m.group(2), "y", (y0 + y1) / 2, x0, abs(y1 - y0)))
    return got


def _sheet_windows(placed):
    want, refused = [], 0
    for i, lv in enumerate(placed["levels"]):
        if not any(r.get("geometry") for r in lv["rooms"]):
            continue
        op = RP.openings_of_level(placed, lv, lv.get("index", i))
        refused += op["windows_refused"] + op["windows_off_footprint"] + op["windows_crowded"]
        for w in op["windows"]:
            axis = "x" if w["wall"] in ("S", "N") else "y"
            want.append((lv.get("index", i), w["room"], axis, w["at_ft"] * 12, w["edge_ft"] * 12,
                         w["width_ft"] * 12))
    return want, refused


def _unmatched(want, got):
    got = list(got)
    left = []
    for w in want:
        i = next((i for i, g in enumerate(got) if g[:3] == w[:3]
                  and all(abs(a - b) < TOL for a, b in zip(g[3:], w[3:]))), None)
        if i is None:
            left.append(w)
        else:
            got.pop(i)
    return left, got


def test_the_dxf_draws_exactly_the_windows_the_sheet_draws_where_it_draws_them(sheets):
    drawn = refused = 0
    for pid, (_plan, placed, res, dxf) in sorted(sheets.items()):
        want, n_ref = _sheet_windows(placed)
        got = _dxf_windows(dxf)
        missing, extra = _unmatched(want, got)
        assert not missing and not extra, (pid, "sheet draws, DXF does not:", missing[:4],
                                           "DXF draws, sheet does not:", extra[:4])
        # and every unit the sheet does not draw is said, with its reason, not dropped in silence
        assert len(res.get("windows_not_drawn") or []) == n_ref, (pid, n_ref, res.get("windows_not_drawn"))
        drawn += len(got)
        refused += n_ref
    assert drawn > 0 and refused > 0, ("the premise: some unit drawn and some refused", drawn, refused)


def test_the_dxf_still_reads_back_into_its_record(sheets):
    """`import_dxf` holds every drawn window line to the record by its identity -- the unit
    number against the record's count, the line's length against its width. Drawing only the
    seated units, at their own positions, must leave that round trip whole."""
    n = 0
    for pid, (plan, _placed, _res, dxf) in sorted(sheets.items()):
        back = IM.read_plan_dxf(dxf)
        assert "error" not in back, (pid, back.get("error"))
        n += back["cross_checks"]["window_leaves"]
    assert n > 0


def test_the_notes_under_the_plan_do_not_print_through_one_another(tmp_path):
    """DRIVEN: a record with no bay module and a refused unit carries three notes under the plan.
    They were set at fixed multiples of TITLE_H, 7 in apart for 8 in text."""
    with open(os.path.join(ROOT, "plans", "spec-builder-colonial.json"), encoding="utf-8") as fh:
        plan = json.load(fh)
    saved = GEO._SOLVE_CACHE
    GEO._SOLVE_CACHE = {}
    try:
        placed = GEO.solve(copy.deepcopy(plan), None, 250, engine="heuristic")
    finally:
        GEO._SOLVE_CACHE = saved
    del placed["footprint"]["bay_module_ft"]
    res = EX.export_plan_dxf(copy.deepcopy(plan), str(tmp_path / "p.dxf"), solved=placed)
    assert "error" not in res, res
    notes = sorted((e.dxf.insert[1], e.dxf.height, e.dxf.text) for e in ezdxf.readfile(
        str(tmp_path / "p.dxf")).modelspace() if e.dxftype() == "TEXT" and e.dxf.insert[1] < 0)
    assert len(notes) >= 2, ("the premise: more than one note under the plan", notes)
    for (y0, h0, t0), (y1, _h1, t1) in zip(notes, notes[1:]):
        assert y1 - y0 >= h0, ("two notes print through one another", t0, t1, y1 - y0)
