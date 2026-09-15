"""WP-13.2. The DXF's door arcs, read back and held to the record -- the third spelling of the
door swing, after `render_plan.py`'s SVG and `Sheet.jsx`'s.

Until Phase 13 `export_dxf.py` drew every interior door as `add_arc((px - dw, py), 2*dw, 0, 90)`:
hinged on the west or south jamb, swept 0 -> 90 degrees, one arc for a pair, reading neither the
hinge nor `swing_positive` off the opening it had itself derived. The gate
(`tests/test_sheet_coherence.py::test_every_door_arc_in_the_dxf_swings_the_way_the_record_says`)
measured 7 of 13 leaves wrong on the search sheet and 15 of 24 on the prover's -- every leaf whose
record swings negative, and both leaves of every pair. Nothing in `tests/test_export.py` looked
at where the door ink went; its round trip reads FINDINGS and XDATA, and an arc carries neither.

So this file reads the ARC entities back with ezdxf and holds each to the opening
`derive_openings` states, exactly as the gate does, on a DETERMINISTIC placement (the search
engine, the reference plan), so the defect is caught here as well as at the gate. COULD NOT
EVALUATE without ezdxf, never a pass.
"""
import json
import math
import os
import sys

import pytest

from conftest import ROOT

sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

IN = 12.0
# the door types the SVG's `_door` draws with no leaf, spelled as the gate spells them
LEAFLESS = ("cased-opening", "open", "pocket", "garage", "bulkhead")


def _b(name):
    return modcache.load(name, os.path.join(ROOT, "build", name + ".py"))


@pytest.fixture(scope="module")
def dxf(tmp_path_factory):
    ezdxf = pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
    G, EX = _b("geometry"), _b("export_dxf")
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    G._SOLVE_CACHE.clear()
    placed = G.solve(plan, engine="heuristic")
    assert "error" not in placed, placed.get("error")
    path = str(tmp_path_factory.mktemp("doors") / "plan.dxf")
    res = EX.export_plan_dxf(placed, path)      # carries geometry, so drawn as it stands
    assert "error" not in res, res
    return placed, res, ezdxf.readfile(path)


def _level_openings(placed, i, lv):
    """`derive_openings` as `render_plan.render()` and the exporter call it: with the level's
    placed appendages and each room's own element. The bare call is one leaf short on this
    plan (the breakfast-terrace door)."""
    RP, EL = _b("render_plan"), _b("elements")
    apx = {}
    for a in ((placed.get("appendages") or {}).get("placed") or []):
        apx.setdefault(a.get("level", 0), {})[a["room"]] = a["rect"]
    fp = placed["footprint"]
    return RP.derive_openings(lv["rooms"], fp["width_ft"], fp["depth_ft"],
                              appendages=apx.get(lv.get("index", i)),
                              bounds=EL.bounds_index(placed, lv["rooms"]))


def _expected_leaves(placed):
    """(hinge ft, radius ft, closed deg, open deg, label) per leaf the record states -- the
    gate's spelling: a single leaf hinged on the LOW jamb at the full width, a pair as two
    half-width leaves on both jambs, open toward `swing_positive` (+y off a horizontal wall,
    +x off a vertical one), closed along the wall toward the far end of its run."""
    out = []
    levels = [lv for lv in placed["levels"] if any(r.get("geometry") for r in lv["rooms"])]
    for i, lv in enumerate(levels):
        for d in _level_openings(placed, i, lv)["interior"]:
            if d["type"] in LEAFLESS:
                continue
            half = d["width_ft"] / 2.0
            label = f"L{lv.get('index', i)} {d['from']}-{d['to']}"
            if d["horiz"]:
                px, py = d["pos_ft"], d["at_ft"]
                open_deg = 90 if d["swing_positive"] else 270
                if d["type"] == "double":
                    out += [((px - half, py), half, 0, open_deg, label), ((px + half, py), half, 180, open_deg, label)]
                else:
                    out.append(((px - half, py), 2 * half, 0, open_deg, label))
            else:
                px, py = d["at_ft"], d["pos_ft"]
                open_deg = 0 if d["swing_positive"] else 180
                if d["type"] == "double":
                    out += [((px, py - half), half, 90, open_deg, label), ((px, py + half), half, 270, open_deg, label)]
                else:
                    out.append(((px, py - half), 2 * half, 90, open_deg, label))
    return out


def _door_arcs(doc):
    return [e for e in doc.modelspace() if e.dxftype() == "ARC" and e.dxf.layer.upper().endswith("-DOOR")]


def _contains(arc, deg):
    s, e = arc.dxf.start_angle % 360, arc.dxf.end_angle % 360
    span = (e - s) % 360 or 360
    return (deg - s) % 360 <= span + 1e-6, span


def test_the_record_states_leaves_in_every_quadrant_so_no_arm_is_untested(dxf):
    """The vacuity pin. A plan whose doors all swung positive off horizontal walls would have
    been green over the old `0, 90` for every one of them."""
    placed, _res, _doc = dxf
    leaves = _expected_leaves(placed)
    assert len(leaves) >= 6, f"COULD NOT EVALUATE: {len(leaves)} leaves derived"
    seen = {(closed % 180 == 0, open_deg) for _h, _r, closed, open_deg, _l in leaves}
    # (horizontal wall?, open direction): both walls, both swing signs
    want = {(True, 90), (True, 270), (False, 0), (False, 180)}
    assert want <= seen, f"the record exercises {sorted(seen)} and not {sorted(want - seen)}"
    labels = [l for _h, _r, _c, _o, l in leaves]
    assert any(labels.count(l) == 2 for l in labels), \
        "no pair of leaves on this plan -- the half-width, two-hinge branch is untested"


def test_every_leaf_has_its_arc_on_the_hinge_at_its_radius_swung_the_way_the_record_says(dxf):
    placed, _res, doc = dxf
    arcs = _door_arcs(doc)
    leaves = _expected_leaves(placed)
    bad = []
    for (hx, hy), r, closed, open_deg, label in leaves:
        near = [a for a in arcs
                if math.hypot(a.dxf.center.x - hx * IN, a.dxf.center.y - hy * IN) <= 0.5
                and abs(a.dxf.radius - r * IN) <= 0.5]
        if not near:
            bad.append(f"{label}: no arc centred on ({hx:.2f},{hy:.2f}) ft at r={r:.2f} ft")
            continue
        ok = []
        for a in near:
            in_open, span = _contains(a, open_deg)
            in_closed, _ = _contains(a, closed)
            if in_open and in_closed and abs(span - 90) <= 1e-6:
                ok.append(a)
        if not ok:
            a = near[0]
            bad.append(f"{label}: the arc at the hinge runs {a.dxf.start_angle:.0f}->{a.dxf.end_angle:.0f} deg "
                       f"and the leaf closes at {closed} and opens toward {open_deg}")
    assert not bad, f"{len(bad)} of {len(leaves)} leaves: " + "; ".join(bad[:6])
    # and no arc the record does not state -- the old exporter's one-per-pair would leave
    # a stray at twice the radius beside the two the pair now gets
    assert len(arcs) == len(leaves), f"{len(arcs)} door arcs in the file for {len(leaves)} leaves on the record"


def test_every_leaf_line_runs_from_its_hinge_to_its_open_tip(dxf):
    """Beside each arc a LINE from the hinge to the tip, as the SVG draws the leaf -- so a
    drafter sees a door and not a quarter-circle floating off a wall."""
    placed, _res, doc = dxf
    lines = [e for e in doc.modelspace() if e.dxftype() == "LINE" and e.dxf.layer.upper().endswith("-DOOR")]
    bad = []
    for (hx, hy), r, _closed, open_deg, label in _expected_leaves(placed):
        tx = hx * IN + r * IN * math.cos(math.radians(open_deg))
        ty = hy * IN + r * IN * math.sin(math.radians(open_deg))
        hit = any(math.hypot(ln.dxf.start.x - hx * IN, ln.dxf.start.y - hy * IN) <= 0.5
                  and math.hypot(ln.dxf.end.x - tx, ln.dxf.end.y - ty) <= 0.5 for ln in lines)
        if not hit:
            bad.append(label)
    assert not bad, f"{len(bad)} leaves have no line from hinge to tip: {bad[:6]}"


def test_the_pair_line_still_carries_its_xdata_and_the_importer_cross_checks_it(dxf):
    """The per-pair opening line and its `TDL::door::L<n>::<room>::<di>` header survive the
    rewrite: `import_dxf` reads the header, finds the door in the carried room record, and
    counts it. The count must be the number of interior pairs the derivation drew."""
    placed, _res, doc = dxf
    IM = _b("import_dxf")
    back = IM.read_plan_dxf(doc.filename)
    assert "error" not in back, back.get("error")
    levels = [lv for lv in placed["levels"] if any(r.get("geometry") for r in lv["rooms"])]
    pairs = sum(len(_level_openings(placed, i, lv)["interior"]) for i, lv in enumerate(levels))
    assert pairs >= 6, f"COULD NOT EVALUATE: {pairs} interior pairs"
    assert back["cross_checks"]["doors"] == pairs, (
        f"the importer cross-checked {back['cross_checks']['doors']} doors against {pairs} pairs drawn")


def test_an_undrawable_door_reaches_the_result_with_its_reason(dxf):
    """`derive_openings` names every declared interior door the placement leaves no wall for,
    and the reason travels: the exporter's `doors_not_drawn` used to say `L0 a-b` and nothing
    else. On this placement the gate counts 14 of 31 declared doors undrawable."""
    placed, res, _doc = dxf
    levels = [lv for lv in placed["levels"] if any(r.get("geometry") for r in lv["rooms"])]
    und = [u for i, lv in enumerate(levels) for u in _level_openings(placed, i, lv)["undrawable"]
           if u["to"] != "exterior"]
    if not und:
        pytest.skip("COULD NOT EVALUATE: every declared interior door is drawable on this placement")
    listed = res.get("doors_not_drawn") or []
    assert len(listed) == len(und), f"{len(listed)} listed against {len(und)} undrawable"
    for u in und:
        line = next((s for s in listed if f"{u['from']}-{u['to']}" in s), None)
        assert line, f"{u['from']}-{u['to']} is undrawable and not listed"
        assert u["reason"] and u["reason"] in line, f"{line!r} does not carry the reason {u['reason']!r}"
