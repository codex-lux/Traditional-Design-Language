"""One set of numbers per opening (WP-14.3, step 2).

`elevation._storey_window` works out the light pattern and the shutter leaf ONCE per storey, at
the width it sizes the storey's window from its head and sill. Since WP-13.3 the rectangles every
surface draws are the PLAN's placed openings, at the plan's own widths -- so every window on a
storey was dressed with the lights and the leaves of a window of another width. Census V4 and V5
measured it on 24 and 27 elevation sheets: shutter leaves covering 78 to 117 per cent of the
window they close over, and light counts that are not sash-light's for the width drawn.

`elevation.sash_at` is the one spelling of that arithmetic at a width. `_storey_window` calls it
at the storey's width and `opening_rects` at each opening's own; the SVG, the DXF and the scene
read the opening's numbers off the rectangle. These tests hold the rectangle to the RULE,
evaluated here from the pack's own expressions rather than through `sash_at`, and hold each of
the three surfaces to the rectangle.

The discriminating premise is asserted: a shipped placement where some window's drawn width
differs from its storey's AND the rule gives it a different light count. Without one, every
assertion below would pass with the storey's numbers standing in for the opening's.
"""
import copy
import json
import os
import re
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
sys.path.insert(0, BUILD)
import modcache as mc  # noqa: E402

PLANS = ("tidewater-georgian-careful", "spec-builder-colonial")


def _m(name):
    return mc.load(name, os.path.join(BUILD, f"{name}.py"))


def _build(pid):
    """On the HEURISTIC, as the sibling suites are: `auto` reaches a CP proof on one machine and
    spends its budget on another."""
    G, ST, RF, EL = _m("geometry"), _m("structure"), _m("roof"), _m("elevation")
    plan = json.load(open(os.path.join(ROOT, "plans", pid + ".json")))
    sol = G.solve(json.loads(json.dumps(plan)), engine="heuristic")
    sec = ST.build_section(sol, None, geometry_result=sol)
    rf = RF.build_roof(sol, None, section=sec)
    ev = EL.build_elevation(sol, None, section=sec, roof=rf)
    return sol, sec, rf, ev


@pytest.fixture(scope="module")
def built():
    return {pid: _build(pid) for pid in PLANS}


def _rule(pack, slot, dim, note_word):
    for r in pack.get("derived_rules") or []:
        if (r.get("target_slot") == slot and r.get("dimension") == dim
                and note_word.lower() in (r.get("note") or r.get("authority_note") or "").lower()):
            return r
    raise AssertionError(f"sash-light states no {slot}/{dim} rule mentioning {note_word!r}")


def _by_the_rule(width_in, glass_module_in):
    """sash-light's own expressions, evaluated here -- never through `sash_at`, which is the
    subject."""
    PE = _m("proportion_engine")
    pack = PE.resolve("sash-light")
    env = dict(PE.DEFAULT_BINDINGS)
    env.update(module=glass_module_in, opening_width=width_in)
    across = PE.evaluate_expr(_rule(pack, "window_lite_pattern", "count", "lights across")["expression"], env)
    high = PE.evaluate_expr(_rule(pack, "window_lite_pattern", "count", "lights high per sash")["expression"], env)
    leaf = PE.evaluate_expr(_rule(pack, "shutter", "width", "half the opening")["expression"],
                            {**env, "opening_width": width_in})
    return int(round(float(across))), int(round(float(high))), float(leaf)


def _windows(ev):
    EL = _m("elevation")
    return [(f, r) for f in "SNEW" for r in EL.opening_rects(ev, f)["rects"] if r["kind"] == "window"]


# ------------------------------------------------------------------ the premise
def test_a_shipped_window_is_drawn_at_a_width_whose_lights_differ_from_its_storeys(built):
    """Without this, every test below passes whether the numbers are the opening's or the
    storey's."""
    found = []
    for pid, (_s, _c, _r, ev) in built.items():
        gm = ev["glass_module_in"]
        for f, r in _windows(ev):
            rec = r["record"]
            across, _h, _l = _by_the_rule(r["width_in"], gm)
            if abs(r["width_in"] - rec["opening_width_in"]) > 0.05 and across != rec["lights_across"]:
                found.append((pid, r["id"]))
    assert found, ("no shipped window is drawn at a width whose light count differs from its "
                   "storey's; this file can no longer tell the opening's numbers from the "
                   "storey's and needs a driven case")


# ------------------------------------------------------------------ the rectangle holds the rule
def test_every_window_carries_the_rules_own_numbers_at_the_width_it_is_drawn(built):
    n = drawn = refused = 0
    for pid, (_s, _c, _r, ev) in built.items():
        gm = ev["glass_module_in"]
        for f, r in _windows(ev):
            across, high, leaf = _by_the_rule(r["width_in"], gm)
            assert (r["lights_across"], r["lights_high_per_sash"]) == (across, high), (pid, r["id"])
            assert r["sash_width_in"] == r["width_in"], (pid, r["id"])
            if r["record"].get("shutter_leaf_width_in") is None:
                assert r["shutter_leaf_width_in"] is None, (
                    f"{pid} {r['id']}: the storey carries no shutters and the opening was given a leaf")
            else:
                # A PAIR `_clearances` REFUSED (WP-14.6) keeps the rule's figure under
                # `shutter_leaf_width_refused_in` and draws nothing, so the drawn width is None
                # there and the figure is read where the refusal put it. This read the drawn width
                # on every window and went red the day the refusal was written (audit, 27 Sep 2026).
                if r.get("shutters_refused"):
                    assert r["shutter_leaf_width_in"] is None, (pid, r["id"], "refused and drawn")
                    got = r["shutter_leaf_width_refused_in"]
                    refused += 1
                else:
                    got = r["shutter_leaf_width_in"]
                    drawn += 1
                assert got == pytest.approx(leaf, abs=0.001), (pid, r["id"])
                assert got == pytest.approx((r["width_in"] - 1.0) / 2.0, abs=0.001)
            n += 1
    # A FLOOR ON THE POPULATION, so the property is not asserted over nothing. 21 drawn windows
    # over the two plans until WP-16.6 and 17 since (1 Oct 2026): the placer refuses four units by
    # name now -- the Tidewater primary chamber's second upper sash for the axis below it (R6), and
    # three of the spec Colonial's for the pier floor (R5) -- so the floor came down with them.
    assert n >= 15, n
    # NO SHIPPED LEAF IS REFUSED SINCE WP-16.6, so the refused half is DRIVEN below. The spec
    # Colonial's family room stood its sashes a foot apart, and two 17.5 in leaves could not share
    # that wall; the pier floor stands them 1.4 x the window apart now (sash-light's aim, 50.4 in)
    # and every pair hangs. A refusal the corpus stopped reaching is a branch to drive, not a
    # premise to delete.
    assert drawn, ("the premise: some leaves are drawn", drawn, refused)


def test_a_refused_pair_keeps_the_rules_leaf_where_the_refusal_put_it(built):
    """DRIVEN (WP-16.6): the spec Colonial's second family-room sash moved to 20 in from the first,
    where two 17.5 in leaves cannot share the wall. One pair is refused, draws nothing, and keeps
    the rule's figure under `shutter_leaf_width_refused_in`."""
    EL = _m("elevation")
    ev = copy.deepcopy(built["spec-builder-colonial"][3])
    a, b = sorted((p for p in ev["faces"]["S"]["placed"]
                   if p["kind"] == "window" and p["room"] == "family" and p["storey"] == "ground"),
                  key=lambda p: p["cx_in"])
    d = (a["cx_in"] + (a["width_in"] + b["width_in"]) / 2.0 + 20.0) - b["cx_in"]
    b["cx_in"] += d
    b["u_ft"] = round(b["u_ft"] + d / 12.0, 4)
    b["along_ft"] += d / 12.0
    gm = ev["glass_module_in"]
    refused = [r for r in EL.opening_rects(ev, "S")["rects"] if r["kind"] == "window" and r.get("shutters_refused")]
    assert refused, "the drive did not land: no pair was refused"
    for r in refused:
        _a, _h, leaf = _by_the_rule(r["width_in"], gm)
        assert r["shutter_leaf_width_in"] is None, r["id"]
        assert r["shutter_leaf_width_refused_in"] == pytest.approx(leaf, abs=0.001), r["id"]


def test_the_storey_window_is_the_same_function_at_the_storeys_width(built):
    """`_storey_window` was lifted onto `sash_at`, not rewritten: the storey's own record is what
    the one function gives at the storey's width."""
    EL, PE = _m("elevation"), _m("proportion_engine")
    for pid, (_s, _c, _r, ev) in built.items():
        for sw in ev["storey_windows"]:
            got = EL.sash_at(PE.resolve("sash-light"), sw["opening_width_in"], ev["glass_module_in"],
                             height_in=sw["opening_height_in"])
            for k in ("lights_across", "lights_high_per_sash", "individual_light_width_in",
                      "individual_light_height_in"):
                assert got[k] == sw[k], (pid, sw["storey"], k)
            # a storey that carries no shutters says so by carrying no leaf and no panel count
            if sw.get("shutter_leaf_width_in") is not None:
                assert got["shutter_leaf_width_in"] == sw["shutter_leaf_width_in"]
                assert got["shutter_panel_count"] == sw["shutter_panel_count"]


def test_with_no_glass_module_no_light_is_counted_and_the_rect_says_why(built):
    """Driven: every shipped elevation states a glass module."""
    EL = _m("elevation")
    ev = copy.deepcopy(built["tidewater-georgian-careful"][3])
    assert ev["glass_module_in"] is not None, "premise"
    ev["glass_module_in"] = None
    rects = [r for f in "SNEW" for r in EL.opening_rects(ev, f)["rects"] if r["kind"] == "window"]
    assert rects
    for r in rects:
        assert r["lights_across"] is None and r["shutter_leaf_width_in"] is None
        assert "glass module" in r["sash_unjudged"]


# ------------------------------------------------------------------ each surface reads the rectangle
def test_the_scene_bars_each_window_by_its_own_lights(built):
    SC = _m("scene")
    checked = differs = 0
    for pid, (sol, sec, rf, ev) in built.items():
        ids = {s["id"] for s in SC.build_scene(sol, sec, rf, ev)["solids"]}
        for f, r in _windows(ev):
            # WP-14.3 step 3: the verticals are the muntins dividing each sash's glass, one set
            # per sash, named `{window}-muntin-{sash}-v{n}` for n = 1 .. lights_across - 1
            if f"{r['id']}-stile-l" not in ids:
                continue                        # a window the scene did not dress at all
            for sash in ("upper", "lower"):
                v = sum(1 for i in range(1, 40) if f"{r['id']}-muntin-{sash}-v{i}" in ids)
                assert v == r["lights_across"] - 1, (pid, r["id"], sash, v, r["lights_across"])
            checked += 1
            differs += r["lights_across"] != r["record"]["lights_across"]
    assert checked and differs, (checked, differs)


def test_the_dxf_divides_each_window_by_its_own_lights(built, tmp_path):
    ezdxf = pytest.importorskip("ezdxf")
    EL, DX = _m("elevation"), _m("export_dxf")
    ev = built["tidewater-georgian-careful"][3]
    face = max("SNEW", key=lambda f: len([r for r in EL.opening_rects(ev, f)["rects"] if r["kind"] == "window"]))
    wins = [r for r in EL.opening_rects(ev, face)["rects"] if r["kind"] == "window"]
    assert wins
    path = str(tmp_path / "e.dxf")
    DX.export_elevation_dxf(ev, path, face=face)
    # WP-14.3 step 3: every sash member is a closed rectangle on the sash layer; a vertical
    # muntin is one whose width is the muntin's and whose height exceeds it
    boxes = []
    for e in ezdxf.readfile(path).modelspace():
        if e.dxftype() == "LWPOLYLINE" and "sash" in e.dxf.layer.lower():
            xs, ys = zip(*[p[:2] for p in e.get_points("xy")])
            boxes.append((min(xs), max(xs), min(ys), max(ys)))
    m = ev["storey_windows"][0]["muntin_width_in"]
    for r in wins:
        vert = {round((a + b) / 2.0, 3) for a, b, c, d in boxes
                if abs((b - a) - m) < 1e-6 and (d - c) > m
                and r["x0_in"] < a and b < r["x1_in"] and r["sill_in"] <= c and d <= r["head_in"]}
        assert len(vert) == r["lights_across"] - 1, (r["id"], len(vert), r["lights_across"])


def test_the_sheet_says_when_a_window_is_not_drawn_at_its_storeys_width(built, tmp_path):
    EL, RE = _m("elevation"), _m("render_elevation")
    ev = built["tidewater-georgian-careful"][3]
    face = next(f for f in "SNEW" if any(abs(r["width_in"] - r["storey_pack_width_in"]) > 0.05
                                         for _f, r in _windows(ev) if _f == f))

    def said(e):
        out = tmp_path / "x.svg"
        RE.render_elevation(e, str(out), face=face)
        return " ".join(re.findall(r">([^<]*)</text>", out.read_text()))

    assert "NOT THE STOREY" in said(ev)
    # and not where every window IS its storey's width: driven, by handing the storey's own
    # width to each placed window on this face
    same = copy.deepcopy(ev)
    for p in same["faces"][face]["placed"]:
        if p["kind"] == "window":
            sw = same["storey_windows"][p["level_index"]]
            p["width_in"] = sw["opening_width_in"]
    assert "NOT THE STOREY" not in said(same)
