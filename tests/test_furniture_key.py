"""The furniture key: every mark on the plan sheet carries its name (WP-13.2).

Until this package a furniture mark was a rectangle with a <title> tooltip -- invisible in
print, in a PDF and on the plate Lucas read, where fifty-six of fifty-six placed items were
unnamed (tests/test_sheet_coherence.py::test_every_furniture_mark_carries_its_name is the gate
row). `build/render_plan.py` now puts a numeral on every mark and a KEY in the room -- one line
per item, the numeral and the item's name as recorded, in a clear corner the fitter chooses --
and sends a key no corner can hold to the margin schedule under the room's name.

What is guarded here, and how each guard can fail:

  * the fitter's own contract, driven on hand-built boxes (a clear corner, a push past a sofa,
    a turn that must earn its letter, a refusal that is about the room and not the size);
  * the rendered Tidewater sheet on the DETERMINISTIC engine: every key line inside its room
    and naming its item whole, every entry numbered, no key line drawn over a room name, a
    mark or a wall body -- read back from the ink, not from the fitter's own record of what
    it meant to do -- and every refused key stated in the margin, inside the canvas;
  * parity with the browser sheet's port (`workbench/app/src/furnitureKey.test.mjs`), on
    one fixture spelled in both files;
  * one spelling of the room label's fit, read by both the label loop and the key.

The refused-room count is a CEILING on the heuristic sheet, never the `auto` one -- the same
rule `tests/test_furniture_drawn.py` states for its figures.
"""
import json
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "build"))
import modcache  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(name):
    return modcache.load(name, os.path.join(ROOT, "build", f"{name}.py"))


RP = _load("render_plan")

# ------------------------------------------------------------------ the record's own words

def test_a_count_is_read_from_the_records_own_words_by_a_closed_rule():
    assert RP.key_count("nightstands, pair") == 2
    assert RP.key_count("sofas, pair, facing") == 2
    assert RP.key_count("two chairs and a table") is None, "a conjunction joins a second item"
    assert RP.key_count("six to eight side chairs, set against the walls") is None, "a band"
    assert RP.key_count("eight to twelve chairs, movable") is None
    assert RP.key_count("shelf, 14 in deep") is None, "a figure inside the name is a dimension"
    assert RP.key_count("table, seats 4") is None, "seats are not tables"
    assert RP.key_count("queen bed") is None
    assert RP.key_count("four hall chairs") == 4
    assert RP.key_count("") is None and RP.key_count(None) is None


def _room():
    return {
        "id": "parlor", "name": "Parlor",
        "geometry": {"x_ft": 10, "y_ft": 5, "width_ft": 20, "depth_ft": 15, "area_sf": 300},
        "fixture_layout": [
            {"item": "small sink", "x_ft": 28, "y_ft": 5, "width_ft": 1.5, "depth_ft": 1.3, "wall": "S"},
            {"item": "unplaced basin", "unplaced": {"reason": "no wall"}},
        ],
        "furniture_layout": [
            {"item": "sofa, pair", "x_ft": 10, "y_ft": 17.2, "width_ft": 7, "depth_ft": 2.8,
             "wall": "N", "marks": [{"rect": [10, 17.2, 7, 2.8]}]},
            {"item": "tea table", "x_ft": 18, "y_ft": 11, "width_ft": 3.5, "depth_ft": 2.5,
             "marks": [{"rect": [18, 11, 3.5, 2.5]}]},
            {"item": "unplaced chair", "unplaced": {"reason": "no floor"}},
        ],
    }


def test_entries_are_numbered_in_drawing_order_and_the_unplaced_take_no_numeral():
    e = RP.key_entries(_room())
    assert [(n, f["item"], k) for n, f, k in e] == [
        (1, "small sink", "fixture"), (2, "sofa, pair", "furniture"), (3, "tea table", "furniture")]


def test_a_key_line_is_the_numeral_and_the_name_whole_never_abbreviated():
    assert RP.key_lines(RP.key_entries(_room())) == ["1 SMALL SINK", "2 SOFA, PAIR", "3 TEA TABLE"]
    long = RP.key_lines([(7, {"item": "  desk (any bedroom   occupied by anyone under twenty-five) "}, "furniture")])
    assert long == ["7 DESK (ANY BEDROOM OCCUPIED BY ANYONE UNDER TWENTY-FIVE)"]


# ------------------------------------------------------------------ the fitter

def test_the_floor_is_the_room_less_the_wall_bodies_decided_by_each_strips_shape():
    # a band along the TOP crosses the left edge too; it must shrink the top and not the left
    floor = RP.clear_floor((0, 0, 200, 150), [(-30, -2, 250, 2), (-2, -30, 2, 200), (198, 20, 202, 90)])
    assert [round(v, 3) for v in floor] == [2, 2, 198, 150]


def test_a_key_sits_flush_in_a_clear_corner_and_is_pushed_past_what_stands_there():
    lines = ["1 SOFA", "2 TEA TABLE"]
    clear = RP.fit_key((0, 0, 260, 195), [], lines)
    assert clear["corner"] == "NW" and clear["turned"] is False
    assert clear["size"] == RP.KEY_PREFERRED_PX
    assert clear["x0"] == RP.KEY_PAD_PX and clear["y0"] == RP.KEY_PAD_PX
    sofa = (0, 0, 91, 36.4)
    pushed = RP.fit_key((0, 0, 260, 195), [sofa], lines)
    assert pushed["size"] == RP.KEY_PREFERRED_PX, "a push does not cost size"
    assert pushed["y0"] >= 36.4 + RP.KEY_PAD_PX - 1e-9 or pushed["x0"] >= 91 + RP.KEY_PAD_PX - 1e-9


def test_a_slot_room_turns_the_key_only_where_turning_earns_a_materially_larger_letter():
    lines = ["1 HALL CHAIRS IN A ROW DOWN ONE SIDE", "2 SETTEE OR BENCH"]
    bw, _bh = RP.key_block_px(lines, RP.KEY_PREFERRED_PX)
    passage = RP.fit_key((0, 0, bw * 0.6, 520), [], lines)
    assert passage["turned"] is True and passage["size"] == RP.KEY_PREFERRED_PX
    square = RP.fit_key((0, 0, bw * 1.5, bw * 1.5), [], lines)
    assert square["turned"] is False


def test_a_key_no_corner_can_hold_at_the_floor_is_refused_and_never_squeezed():
    lines = ["1 HOT WATER CYLINDER, WHERE THE ROOM IS AN AIRING CUPBOARD"]
    bw, bh = RP.key_block_px(lines, RP.KEY_FLOOR_PX)
    assert RP.fit_key((0, 0, bw * 0.8, bw * 0.8), [], lines) is None
    # the refusal is about the room and not the size: a room a hair larger holds it
    assert RP.fit_key((0, 0, bw + 2 * RP.KEY_PAD_PX + 0.1, bh + 2 * RP.KEY_PAD_PX + 0.1), [], lines)


def test_a_numeral_goes_inside_a_mark_that_can_hold_it_and_beside_one_that_cannot():
    room = (0, 0, 260, 195)
    inside = RP.numeral_at((26, 26, 65, 65), "N", 3, room)
    assert inside[2] == "middle" and 26 < inside[0] < 65 and 26 < inside[1] < 65
    thin = RP.numeral_at((0, 39, 5.2, 91), "W", 2, room)      # a hook rail on the west wall
    assert thin[2] == "start" and thin[0] > 5.2, "beside it, on the room side"
    north = RP.numeral_at((39, 0, 117, 4), "N", 1, room)
    assert north[1] > 4, "below the rail, on the room side"
    # a numeral that would land on the label goes beside the mark instead
    dodged = RP.numeral_at((26, 26, 65, 65), None, 4, room, avoid=[(13, 13, 117, 52)])
    assert dodged[4][1] >= 52, f"off the label: {dodged[4]}"
    # and a mark the label covers on every side keeps its numeral INSIDE
    smothered = RP.numeral_at((26, 26, 65, 65), None, 4, room, avoid=[(13, 13, 117, 78)])
    assert smothered[2] == "middle" and 26 < smothered[1] < 65


# THE PARITY FIXTURE -- the same room `workbench/app/src/furnitureKey.test.mjs` builds in feet,
# here in sheet px at the standard's 13 px/ft. A change to either fitter that moves this key
# is caught on both sides. A sofa in the NW corner, a piano in the NE, chairs in the SW, a table
# in the SE, and the label across the middle: every corner has something in it and the NW
# push is the shortest.
PX = 13.0
PARITY = {
    "floor": (0, 0, 20 * PX, 15 * PX),
    "obstacles": [(0, 0, 7 * PX, 2.8 * PX), (13 * PX, 0, 20 * PX, 5 * PX), (0, 10 * PX, 6 * PX, 15 * PX),
                  (14 * PX, 10 * PX, 20 * PX, 15 * PX), (7 * PX, 7 * PX, 13 * PX, 8 * PX)],
    "lines": ["1 SOFAS, PAIR, FACING", "2 GRAND PIANO", "3 TEA TABLE"],
}


def test_the_parity_fixture_agrees_with_the_browser_sheets_port():
    fit = RP.fit_key(PARITY["floor"], PARITY["obstacles"], PARITY["lines"])
    assert fit["corner"] == "NW" and fit["turned"] is False and fit["size"] == 6.0
    assert abs(fit["x0"] - 3.0) < 1e-6 and abs(fit["y0"] - (2.8 * PX + 3.0)) < 1e-6
    assert abs(RP._text_w(PARITY["lines"][0], 6.0, mono=True) - 0.6 * 21 * 6) < 1e-9
    # the sofa alone, with the NE corner free: the nearest clear corner wins over a push
    assert RP.fit_key(PARITY["floor"], PARITY["obstacles"][:1], PARITY["lines"])["corner"] == "NE"
    # and the fixture really is the one the JS file states
    js = open(os.path.join(ROOT, "workbench", "app", "src", "furnitureKey.test.mjs")).read()
    assert "[[0, 0, 7, 2.8], [13, 0, 20, 5], [0, 10, 6, 15], [14, 10, 20, 15], [7, 7, 13, 8]]" in js
    assert "'1 SOFAS, PAIR, FACING', '2 GRAND PIANO', '3 TEA TABLE'" in js


# ------------------------------------------------------------------ the rendered sheet

@pytest.fixture(scope="module")
def sheet(tmp_path_factory):
    """`tidewater-georgian-careful` on the DETERMINISTIC engine, in the presentation register
    the gate and the workbench draw. Rendered once for the module."""
    geo = _load("geometry")
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    geo._SOLVE_CACHE.clear()
    out = geo.solve(plan, None, 250, engine="heuristic")
    path = str(tmp_path_factory.mktemp("key") / "tidewater.svg")
    RP.render(out, path, register="presentation")
    return out, open(path, encoding="utf-8").read()


_KEY = re.compile(r'<text class="dm" data-key="([^"]+)" data-key-item="(\d+)"([^>]*)>([^<]*)</text>')
_NUM = re.compile(r'<text class="dm" data-key-numeral="(\d+)" data-key-room="([^"]+)"[^>]*>(\d+)</text>')
_ATTR = re.compile(r'(\w[\w-]*)="([^"]*)"')


def _frame(svg):
    return json.loads(re.search(r"data-frame='([^']+)'", svg).group(1))["plates"]


def _xy(plate):
    ox, oy = plate["origin_px"]
    ax, ay = plate["at_origin_ft"]
    k = plate["px_per_ft"]
    return (lambda v: ox + (v - ax) * k), (lambda v: oy + (ay - v) * k)


def _placed(out):
    return [lv for lv in out["levels"] if any(r.get("geometry") for r in lv["rooms"])]


def test_every_key_line_is_inside_its_room_and_names_its_item_whole(sheet):
    out, svg = sheet
    plates = _frame(svg)
    keys = [(rid, int(n), dict(_ATTR.findall(a)), t) for rid, n, a, t in _KEY.findall(svg)]
    assert len(keys) >= 40, f"{len(keys)} key lines: the premise has moved"
    want, seen = 0, 0
    for i, lv in enumerate(_placed(out)):
        X, Y = _xy(plates[i])
        for r in lv["rooms"]:
            g = r.get("geometry")
            if not g or g.get("void"):
                continue
            x, y, w, h = g["x_ft"], g["y_ft"], g["width_ft"], g["depth_ft"]
            x0, x1, y0, y1 = X(x) - 1, X(x + w) + 1, Y(y + h) - 1, Y(y) + 1
            mine = [k for k in keys if k[0] == r["id"]]
            for n, f, _kind in RP.key_entries(r):
                want += 1
                line = [k for k in mine if k[1] == n]
                if not line:
                    continue          # refused to the margin: the next test owns that
                seen += 1
                a, t = line[0][2], line[0][3]
                assert x0 <= float(a["x"]) <= x1 and y0 <= float(a["y"]) <= y1, (r["id"], n, a)
                assert " ".join(f["item"].split()).upper() in t, (r["id"], f["item"], t)
                assert "font-size" not in a, "a fitted size written as an attribute does not apply"
    assert want >= 60 and seen >= 50, (want, seen)


def test_every_drawn_item_carries_its_numeral(sheet):
    out, svg = sheet
    nums = {(rid, int(n)) for n, rid, _t in _NUM.findall(svg)}
    want = set()
    for lv in _placed(out):
        for r in lv["rooms"]:
            if r.get("geometry") and not r["geometry"].get("void"):
                for n, _f, _k in RP.key_entries(r):
                    want.add((r["id"], n))
    assert len(want) >= 60, "the premise has moved"
    assert want == nums, sorted(want ^ nums)


def _text_box(attrs, text, mono, default_size, track):
    """A text element's ink, as this renderer estimates it (`_text_w`), honouring a rotation
    stated on the element itself."""
    size = default_size
    m = re.search(r"font-size:([\d.]+)px", attrs.get("style", ""))
    if m:
        size = float(m.group(1))
    w = RP._text_w(text, size, mono=mono, track=track)
    x, y = float(attrs["x"]), float(attrs["y"])
    anchor = attrs.get("text-anchor", "start")
    x0 = x - w / 2 if anchor == "middle" else (x - w if anchor == "end" else x)
    box = (x0, y - 0.8 * size, x0 + w, y + 0.25 * size)
    rot = re.search(r"rotate\(-90 ([\d.]+) ([\d.]+)\)", attrs.get("transform", ""))
    if rot:
        cx, cy = float(rot.group(1)), float(rot.group(2))
        pts = [(cx + (py - cy), cy - (px - cx)) for px, py in
               ((box[0], box[1]), (box[2], box[1]), (box[2], box[3]), (box[0], box[3]))]
        box = (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))
    return box


def _label_boxes(svg):
    """Every room name on the sheet, honouring the `<g transform="rotate(-90 …)">` a turned
    label sits in. An independent reader of the ink, not the fitter's record of it."""
    out, rot = [], None
    for tok in re.finditer(r'<g transform="rotate\(-90 ([\d.]+) ([\d.]+)\)">|<g\b[^>]*>|</g>|'
                           r'<text class="nm"([^>]*)>([^<]*)</text>', svg):
        if tok.group(0).startswith("<g transform"):
            rot = (float(tok.group(1)), float(tok.group(2)))
        elif tok.group(0).startswith("<g"):
            rot = None
        elif tok.group(0) == "</g>":
            rot = None
        else:
            attrs = dict(_ATTR.findall(tok.group(3)))
            box = _text_box(attrs, tok.group(4), False, 11.0, RP.ROOM_TRACK)
            if rot:
                cx, cy = rot
                pts = [(cx + (py - cy), cy - (px - cx)) for px, py in
                       ((box[0], box[1]), (box[2], box[1]), (box[2], box[3]), (box[0], box[3]))]
                box = (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))
            out.append(box)
    return out


def _rect_boxes(svg, cls):
    out = []
    for m in re.finditer(rf'<rect class="{cls}"([^>]*)>', svg):
        a = dict(_ATTR.findall(m.group(1)))
        x, y, w, h = (float(a[k]) for k in ("x", "y", "width", "height"))
        out.append((x, y, x + w, y + h))
    return out


def _overlap(a, b, slack=0.0):
    return a[0] < b[2] - slack and a[2] > b[0] + slack and a[1] < b[3] - slack and a[3] > b[1] + slack


def test_no_key_line_is_drawn_over_a_room_name_a_mark_or_a_wall_body(sheet):
    """Read back from the ink. The label boxes come from the `class="nm"` texts (and the
    rotation group a turned name sits in), the marks from `class="fu"`/`"fn"` rects, the wall
    bodies from the poché rects; none of it from the fitter's own plan of what it avoided."""
    _out, svg = sheet
    keys = [_text_box(dict(_ATTR.findall(a)), t, True, 8.0, 0.0) for _r, _n, a, t in _KEY.findall(svg)]
    assert len(keys) >= 40
    labels = _label_boxes(svg)
    assert len(labels) >= 20, "no labels read: the selector has gone blind"
    marks = _rect_boxes(svg, "fu") + _rect_boxes(svg, "fn")
    walls = _rect_boxes(svg, "pm") + _rect_boxes(svg, "pp")
    assert len(marks) >= 60 and len(walls) >= 20
    over = []
    for k in keys:
        for name, boxes in (("label", labels), ("mark", marks), ("wall", walls)):
            # half a pixel of slack: a mark's stroke and a glyph's side bearing may touch
            if any(_overlap(k, b, 0.5) for b in boxes):
                over.append((name, [round(v, 1) for v in k]))
    assert not over, f"{len(over)} key line(s) drawn over other ink: {over[:6]}"


REFUSED_ROOMS_CEILING = 7      # tidewater-georgian-careful, engine="heuristic", presentation


def test_every_refused_key_reaches_the_margin_schedule_inside_the_canvas(sheet):
    out, svg = sheet
    drawn = {rid for rid, _n, _a, _t in _KEY.findall(svg)}
    refused = []
    for lv in _placed(out):
        for r in lv["rooms"]:
            if r.get("geometry") and not r["geometry"].get("void") and RP.key_entries(r) \
                    and r["id"] not in drawn:
                refused.append(r)
    assert refused, "no key was refused on this sheet: the branch is not exercised"
    assert len(refused) <= REFUSED_ROOMS_CEILING, (
        f"{len(refused)} rooms send their key to the margin, up from {REFUSED_ROOMS_CEILING}: "
        + ", ".join(r["id"] for r in refused))
    total_h = float(re.search(r'<svg[^>]*\sheight="(\d+)"', svg).group(1))
    lines = [(dict(_ATTR.findall(a)), t) for a, t in
             re.findall(r'<text class="lb"([^>]*)>([^<]*)</text>', svg) if "FURNITURE KEY" in t]
    for r in refused:
        name = (r.get("name") or r["id"]).upper()
        mine = [t for a, t in lines if t.startswith(f"FURNITURE KEY, {name}")]
        assert mine, f"{r['id']} was refused and no schedule line says so"
        joined = " ".join(mine)
        for line in RP.key_lines(RP.key_entries(r)):
            assert line in joined or line in joined.replace("  ", " "), (r["id"], line)
    # the pre-pass sized the margin: every schedule line is on the canvas, not below it
    for a, _t in lines:
        assert float(a["y"]) < total_h - 20, (a["y"], total_h)


# ------------------------------------------------------------------ one spelling

def test_the_label_loop_and_the_key_read_one_account_of_the_labels_fit():
    """The AST, not a substring: the definition line matches the same text as a call."""
    import ast
    tree = ast.parse(open(os.path.join(ROOT, "build", "render_plan.py")).read())
    lays = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "lay"]
    assert len(lays) == 1, "the label's fit is spelled twice"
    callers = set()
    for fn in ast.walk(tree):
        if not isinstance(fn, ast.FunctionDef):
            continue
        for n in ast.walk(fn):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "_room_label":
                callers.add(fn.name)
    assert callers == {"render", "furniture_key_plan"}, callers
