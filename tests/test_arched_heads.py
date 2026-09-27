"""A window head is drawn as the circle it is set out on, at the rise of its own width (WP-14.3).

WP-14.1's census said no arched head departed from a circle, and it said so because its style
sweep drew the Tidewater house every time, whose heads are gauged flat arches cambered 0.4 in.
Drawn as themselves, 13 styles set a head rising 4.2 to 5 in (12 keyed segmental arches and one
keystoned flat arch at its kit's stated rise), and each was a quadratic Bezier -- a parabola. A
segmental head's extrados was the soffit moved up with vertical ends, and its joints radiated to
the flat arch's strike point from the chord.

The rise is brick-course's rule, read here by evaluating the pack's OWN expression at the width
the ink measures, never by transcribing `/ 8` or `/ 96`.
"""
import copy
import json
import math
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


def _rule(dim):
    pack = json.load(open(os.path.join(ROOT, "proportions", "modules", "brick-course.json")))
    exprs = [r["expression"] for r in pack["derived_rules"]
             if r.get("target_slot") == "window_head_masonry" and r.get("dimension") == dim]
    assert len(exprs) == 1, (dim, exprs)
    PE = _m("proportion_engine")
    return lambda w: PE.evaluate_expr(exprs[0], {"opening_width": w})


@pytest.fixture(scope="module")
def placed():
    G = _m("geometry")
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    return G.solve(plan, engine="heuristic")


def _elev(placed, style):
    ST, RF, EL = _m("structure"), _m("roof"), _m("elevation")
    p = copy.deepcopy(placed)
    p["style"] = style
    sec = ST.build_section(p, None, geometry_result=p)
    rf = RF.build_roof(p, None, section=sec)
    el = EL.build_elevation(p, None, section=sec, roof=rf)
    assert el.get("style") == style
    return el


def test_each_window_takes_the_rise_of_its_own_width(placed):
    EL = _m("elevation")
    el = _elev(placed, "tidewater-georgian")
    camber = _rule("flat_arch_camber")
    rects = [r for f in "SNEW" for r in EL.opening_rects(el, f)["rects"] if r["kind"] == "window"]
    assert rects
    widths = {round(r["x1_in"] - r["x0_in"], 3) for r in rects}
    storey = {round(sw["opening_width_in"], 3) for sw in el["storey_windows"]}
    assert widths - storey, "the premise: some window is drawn at a width its storey was not sized at"
    for r in rects:
        # the record carries three places, as every figure in it does
        assert r["head_rise_in"] == round(camber(r["x1_in"] - r["x0_in"]), 3), r["id"]


def _heads(svg):
    ink = IR.Ink(svg)
    pl = next(f for f in ink.frames() if f.get("proj") == "elevation")
    return ink, pl, [h for h in ink.select("path", cls="arch")]


@pytest.mark.parametrize("style", ["colonial-revival", "english-georgian"])
def test_a_segmental_head_is_its_circle_at_the_rise_of_its_span(placed, tmp_path, style):
    EL, RE = _m("elevation"), _m("render_elevation")
    el = _elev(placed, style)
    assert "segmental" in (el["storey_windows"][0].get("head_treatment") or {}).get("kind", ""), (
        "the premise: this style sets a segmental head")
    rise_rule = _rule("segmental_arch_rise")
    face = el["entrance_face"]
    out = str(tmp_path / "e.svg")
    RE.render_elevation(el, out, face=face)
    ink, pl, heads = _heads(open(out).read())
    k = pl["px_per_ft"] / 12.0
    judged = 0
    for h in heads:
        cmds = h.cmds
        assert cmds[1][0] == "A", "the soffit is drawn as an arc, not a Bezier"
        (pts,) = IR.sample_commands([cmds[0], cmds[1]], m=h.ctm, n=48)
        cx, cy, r, _rms = IR.fit_circle(pts)
        assert max(abs(math.hypot(x - cx, y - cy) - r) for x, y in pts) < 0.02
        # the circle passes through both springings and stands the rule's rise above them
        (x0, y0), (x1, y1) = pts[0], pts[-1]
        span_in = abs(x1 - x0) / k
        crown_in = (y0 - min(y for _x, y in pts)) / k
        assert crown_in == pytest.approx(rise_rule(span_in), abs=0.02), (span_in, crown_in)
        judged += 1
    assert judged >= 2


def test_a_segmental_extrados_is_concentric_and_its_joints_radial(placed, tmp_path):
    RE = _m("render_elevation")
    el = _elev(placed, "colonial-revival")
    out = str(tmp_path / "e.svg")
    RE.render_elevation(el, out, face=el["entrance_face"])
    ink, pl, heads = _heads(open(out).read())
    h = heads[0]
    cmds = h.cmds
    # M soffit-left, A soffit, L extrados-right, A extrados, Z
    kinds = [c[0] for c in cmds]
    assert kinds[:4] == ["M", "A", "L", "A"], kinds
    (soff,) = IR.sample_commands([cmds[0], cmds[1]], m=h.ctm, n=48)
    cx, cy, r, _ = IR.fit_circle(soff)
    (ext,) = IR.sample_commands([("M", cmds[2][1], cmds[2][2]), cmds[3]], m=h.ctm, n=48)
    ex, ey, er, _ = IR.fit_circle(ext)
    assert math.hypot(ex - cx, ey - cy) < 0.05, "the extrados is not concentric with the soffit"
    depth_px = er - r
    assert depth_px > 1.0
    # every voussoir joint lies on a radius, from the soffit to the extrados
    # this head's joints are the ones inside this head's own drawn extent; the window over it
    # carries joints of its own at the same x
    hx0, hy0, hx1, hy1 = h.bbox(n=48)
    joints = [it for it in ink.select("line") if "vsr" in it.classes]
    near = [j for j in joints if hx0 - 0.5 <= j.bbox()[0] and j.bbox()[2] <= hx1 + 0.5
            and hy0 - 0.5 <= j.bbox()[1] and j.bbox()[3] <= hy1 + 0.5]
    assert len(near) >= 4 and len(near) % 2 == 0, len(near)   # an odd count of voussoirs
    for j in near:
        pts = j.points(n=2)
        a, b = pts[0], pts[-1]
        ra, rb = math.hypot(a[0] - cx, a[1] - cy), math.hypot(b[0] - cx, b[1] - cy)
        # one end on the soffit's circle, the other on the extrados's, to the print's 0.01 px
        assert abs(min(ra, rb) - r) < 0.05 and abs(max(ra, rb) - er) < 0.05, (ra, rb, r, er)
        # and the joint points at the centre: the cross product of the joint and the radius is 0
        ux, uy = b[0] - a[0], b[1] - a[1]
        vx, vy = a[0] - cx, a[1] - cy
        assert abs(ux * vy - uy * vx) / (math.hypot(ux, uy) * math.hypot(vx, vy)) < 1e-3
