"""Both renderers of a plan record must draw the same openings (WP-6.1).

The other half of this contract is workbench/app/src/derive.test.mjs, which runs the
JavaScript renderer over the same fixtures. Read tests/fixtures/sheet_symbols/README.md
for why the placement inside a fixture is frozen rather than solved here.

These tests also pin the three specific lies the sheet used to tell, by name, so that
fixing them cannot be quietly undone:
  · a door narrower than 3.2 ft was never drawn, though the solver would prove it
  · a door with no drawable wall was dropped in silence
  · a window and an exterior door were placed on the same masonry, window painted last
"""
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIX = ROOT / "tests" / "fixtures" / "sheet_symbols"
sys.path.insert(0, str(ROOT / "build"))

import modcache  # noqa: E402  (the project's one module loader — never a local copy)

render_plan = modcache.load("render_plan", str(ROOT / "build" / "render_plan.py"))

FIXTURES = sorted(p for p in FIX.glob("*.json"))


def _fixtures():
    assert FIXTURES, "no sheet-symbol fixtures — generate.py has not been run"
    return FIXTURES


@pytest.mark.parametrize("path", _fixtures(), ids=lambda p: p.stem)
def test_python_renderer_matches_the_contract(path):
    """render_plan.derive_openings reproduces the frozen fixture exactly."""
    fx = json.loads(path.read_text())
    W = fx["footprint"]["width_ft"]
    H = fx["footprint"]["depth_ft"]
    for lv in fx["levels"]:
        got = render_plan.derive_openings(lv["rooms"], W, H)
        assert got == lv["expected"], (
            f"{path.stem} level {lv['id']}: the Python renderer no longer draws what the "
            f"contract says. If this change is intended, regenerate the fixtures and read "
            f"the diff — workbench/app/src/derive.test.mjs must change with it."
        )


@pytest.mark.parametrize("path", _fixtures(), ids=lambda p: p.stem)
def test_every_declared_door_is_drawn_or_named(path):
    """No declared door may simply vanish. Either it is drawn, or it is on the undrawable
    list with a reason — the state this file exists to make impossible is the third one,
    where the record holds a door and the sheet holds neither the door nor a word about it.
    """
    fx = json.loads(path.read_text())
    for lv in fx["levels"]:
        exp = lv["expected"]
        drawn = {tuple(sorted(d["pair"])) for d in exp["interior"]}
        named = {tuple(sorted((u["from"], u["to"]))) for u in exp["undrawable"]}
        ext_drawn = sum(1 for _ in exp["exterior"])
        ext_named = sum(1 for u in exp["undrawable"] if u["to"] == "exterior")

        declared_pairs, declared_ext = set(), 0
        for r in lv["rooms"]:
            for d in (r.get("doors") or []):
                if d["to"] == "exterior":
                    declared_ext += 1
                else:
                    declared_pairs.add(tuple(sorted((r["id"], d["to"]))))

        missing = declared_pairs - drawn - named
        assert not missing, f"{path.stem} {lv['id']}: doors neither drawn nor named: {sorted(missing)}"
        assert ext_drawn + ext_named == declared_ext, (
            f"{path.stem} {lv['id']}: {declared_ext} exterior door(s) declared, "
            f"{ext_drawn} drawn and {ext_named} named"
        )
        for u in exp["undrawable"]:
            assert u["reason"].strip(), "an undrawable door must say WHY it could not be drawn"


@pytest.mark.parametrize("path", _fixtures(), ids=lambda p: p.stem)
def test_no_opening_is_drawn_over_another(path):
    """A door and a window may not occupy the same masonry.

    On the shipped Tidewater sheet this fired twice — the centre passage's front door and
    the kitchen's back door were each drawn at their wall's midpoint, and each had a single
    declared window on the same wall, also at the midpoint. WindowMark paints a filled rect
    and DoorMark paints a 0.7 ft break, so the window swallowed the door and a reader saw a
    house whose passage has no door at either end.
    """
    fx = json.loads(path.read_text())
    for lv in fx["levels"]:
        exp = lv["expected"]
        spans = {}
        for d in exp["exterior"]:
            spans.setdefault((d["room"], d["wall"]), []).append(
                ("door", d["at_ft"] - d["width_ft"] / 2, d["at_ft"] + d["width_ft"] / 2))
        for w in exp["windows"]:
            spans.setdefault((w["room"], w["wall"]), []).append(
                ("window", w["at_ft"] - w["width_ft"] / 2, w["at_ft"] + w["width_ft"] / 2))
        for key, items in spans.items():
            items.sort(key=lambda t: t[1])
            for (k1, a1, b1), (k2, a2, b2) in zip(items, items[1:]):
                assert a2 >= b1 - 1e-6, (
                    f"{path.stem} {lv['id']} {key[0]} wall {key[1]}: {k1} "
                    f"[{a1:.2f},{b1:.2f}] overlaps {k2} [{a2:.2f},{b2:.2f}]"
                )


def test_a_narrow_door_is_drawn_at_its_own_width():
    """OQ 41/63, the renderer half. The old test was a flat 3.2 ft for every door, so a
    2.2 ft closet door the CP engine proves on a 2 ft shared wall was held as a fact and
    appeared in no drawing. The test is now the leaf plus its jambs."""
    assert render_plan.required_wall_ft(2.2) == pytest.approx(2.9)
    a = {"x_ft": 0, "y_ft": 0, "width_ft": 10, "depth_ft": 10}
    b = {"x_ft": 10, "y_ft": 0, "width_ft": 10, "depth_ft": 3.0}   # 3.0 ft of shared wall
    assert render_plan._shared(a, b, width_ft=2.2) is not None, "a closet door fits 3.0 ft"
    assert render_plan._shared(a, b, width_ft=3.5) is None, "a 3.5 ft leaf does not"
    # and the historical default is unchanged for callers that state no width
    assert render_plan._shared(a, b) is None


def test_the_kitchen_keeps_its_doors_on_the_record_even_when_undrawable():
    """The reported symptom, pinned. On the Tidewater placement the kitchen's five interior
    doors have no drawable shared wall, so the sheet drew the kitchen with one exterior door
    and nothing else — a room reachable only from outdoors — and said nothing at all. They
    must now every one be named."""
    fx = json.loads((FIX / "tidewater-georgian-careful.json").read_text())
    ground = next(lv for lv in fx["levels"] if lv["index"] == 0)
    named = {tuple(sorted((u["from"], u["to"]))) for u in ground["expected"]["undrawable"]}
    kitchen = {p for p in named if "kitchen" in p}
    assert len(kitchen) >= 5, f"expected the kitchen's undrawable doors to be named; got {kitchen}"


def test_a_relaxation_mark_is_drawn_on_the_wall_it_is_true_of_or_not_drawn():
    """The JS half is `relaxationMarks` in derive.test.mjs, and the two must agree.

    A CP mark carries `runs` rather than a from/to extent, and both renderers used to drop
    such a mark at the MIDDLE OF THE PLAN: on the Tidewater placement that put a dashed tick
    and a triangle inside the drawing room, on a line that has no wall anywhere near it.
    Those are the arrows Lucas reported as pointing "to anything and everything"."""
    W, H = 60, 40
    heur = {"off_ft": 2, "axis": "y", "at_ft": 27, "level": 0, "from_ft": 10, "to_ft": 20}
    cp = {"off_ft": 3, "axis": "y", "at_ft": 27, "level": 0, "runs": [[51, 60], [0, 4]]}
    nowhere = {"off_ft": 4, "axis": "y", "at_ft": 27, "level": 0}
    other = {"off_ft": 5, "axis": "x", "at_ft": 13, "level": 1, "runs": [[0, 40]]}

    drawn, unlocated = render_plan.relaxation_marks([heur, cp, nowhere, other], 0, W, H)
    assert len(drawn) == 2, "the level-1 mark belongs to the other plate"
    assert [m["off_ft"] for m in unlocated] == [4], "a mark on no wall is named, never placed"

    (_m0, runs0, at0), (_m1, runs1, at1) = drawn
    assert runs0 == [(10, 20)] and at0 == pytest.approx(15)
    assert len(runs1) == 2, "both measured pieces of the line are drawn"
    assert at1 == pytest.approx(55.5), "the triangle hangs on the longest real run"
    assert at1 != pytest.approx(W / 2), "and never at the middle of the plan"

    # a run off the plate is clipped; one with nothing left locates nothing
    drawn, unlocated = render_plan.relaxation_marks(
        [{"off_ft": 2, "axis": "x", "at_ft": 5, "level": 0, "runs": [[-8, 12]]},
         {"off_ft": 2, "axis": "x", "at_ft": 6, "level": 0, "runs": [[80, 96]]}], 0, W, H)
    assert [r for _m, r, _a in drawn] == [[(0, 12)]]
    assert len(unlocated) == 1


def test_the_cp_counter_gives_every_relaxation_a_wall_to_sit_on():
    """The counter knew which room faces lay on the off-grid line and threw them away, so
    the sheet had nothing to place the mark by and dropped it at the middle of the plan.

    Measured on the counter itself rather than on a frozen placement: `_count_relaxations`
    is a pure function of the rectangles, so this needs no solver and pins the mechanism
    instead of one machine's search result. Two rooms meet on a line at x = 13 that the
    10 ft bay does not carry, and they meet along y 25..40 — nowhere near the middle."""
    cp = modcache.load("geometry_cp", str(ROOT / "build" / "geometry_cp.py"))
    rects = {"a": (0.0, 25.0, 13.0, 15.0), "b": (13.0, 25.0, 27.0, 15.0),
             "c": (0.0, 0.0, 40.0, 25.0)}
    marks = cp._count_relaxations({0: rects}, W=40, H=40, bay=10.0, tol=0.5)
    assert marks, "a wall at 13 ft on a 10 ft bay is a relaxation"
    for m in marks:
        assert m.get("runs"), f"{m} carries no measured wall to sit on"
    line = next(m for m in marks if m["axis"] == "x" and m["at_ft"] == 13.0)
    assert line["runs"] == [[25.0, 40.0]], "the run is where the rooms actually meet"
    drawn, unlocated = render_plan.relaxation_marks(marks, 0, 40, 40)
    assert not unlocated and len(drawn) == len(marks)
    assert all(a >= 25.0 for _m, runs, _at in drawn for a, _b in runs
               if _m["axis"] == "x"), "and not across the room below it"


def _plate_from(fx):
    """The frozen rooms drawn on the Python plate, read back as ink."""
    import os
    import tempfile
    sys.path.insert(0, str(ROOT / "tests"))
    import inkread as IR
    plan = {"id": fx["plan"], "name": fx["plan"], "footprint": dict(fx["footprint"]),
            "levels": [{"id": lv["id"], "index": lv["index"], "rooms": lv["rooms"]} for lv in fx["levels"]]}
    d = tempfile.mkdtemp()
    out = os.path.join(d, "plate.svg")
    render_plan.render(plan, out)
    return IR, IR.Ink(open(out).read())


def _door_key(room_id, d):
    return ("ext", room_id) if d["to"] == "exterior" else ("int",) + tuple(sorted((room_id, d["to"])))


def _rehung(fx, mode="high", unseat=False):
    """DRIVEN: every door in the record re-hung, and the contract re-derived from the rooms by the
    one function that states it. `openings.place` writes `hinge: "low"` on every door it seats, so
    no frozen fixture reaches the other jamb -- and a mutation hanging a high leaf from the low jamb
    left the ink check green until this existed. `mode` is "high" (every door) or "mixed"
    (alternate doors, in the sorted order of their keys, so both sides of an interior door agree).

    `unseat` (WP-14.6) also strips each door's seat, so every door is drawn on the paths the
    frozen fixtures never reach: an interior door on the two rooms' shared run, an exterior door
    on the first declared wall the placement put outside. The bench was dropping the record's
    hinge on the second, and nothing on either side read those paths.

    WP-14.6's second audit: THE UNSEATED VARIANT HUNG EVERY DOOR HIGH, so a derivation answering
    "high" on those paths whatever the record said -- the defect's mirror image -- was as green as
    the right one: the contract below is re-derived by the function under test, and the ink agrees
    with whatever it says. It hangs the doors MIXED now, and every derived door is held to the jamb
    its own record names, which a constant cannot satisfy on both."""
    import copy
    fx = copy.deepcopy(fx)
    W, H = fx["footprint"]["width_ft"], fx["footprint"]["depth_ft"]
    keys = sorted({_door_key(r["id"], d) for lv in fx["levels"] for r in lv["rooms"] for d in r.get("doors") or []})
    hinge_of = {k: ("high" if mode == "high" or i % 2 else "low") for i, k in enumerate(keys)}
    for lv in fx["levels"]:
        for r in lv["rooms"]:
            for d in r.get("doors") or []:
                d["hinge"] = hinge_of[_door_key(r["id"], d)]
                if unseat:
                    for k in ("wall", "position_ft", "unplaced"):
                        d.pop(k, None)
        lv["expected"] = render_plan.derive_openings(lv["rooms"], W, H)
        for d in lv["expected"]["interior"]:
            want = hinge_of[("int",) + tuple(sorted(d["pair"]))]
            assert d["hinge"] == want, "%s: %s derived hung %s, its record says %s" % (lv["id"], d["pair"], d["hinge"], want)
        for d in lv["expected"]["exterior"]:
            want = hinge_of[("ext", d["room"])]
            assert d["hinge"] == want, "%s: the %s/%s door derived hung %s, its record says %s" % (
                lv["id"], d["room"], d["wall"], d["hinge"], want)
    assert any(d["hinge"] == "high" for lv in fx["levels"] for d in lv["expected"]["interior"]), (
        "the premise: the re-derived contract hangs its doors from the high jamb")
    if mode == "mixed":
        hung = {d["hinge"] for lv in fx["levels"] for d in lv["expected"]["interior"] + lv["expected"]["exterior"]}
        assert hung == {"low", "high"}, "the premise: a mixed hanging reaches both jambs, not %s" % sorted(hung)
    if unseat:
        assert any(d["inferred_wall"] for lv in fx["levels"] for d in lv["expected"]["exterior"]), (
            "the premise: an unseated exterior door is drawn on an inferred wall")
        assert {d["hinge"] for lv in fx["levels"] for d in lv["expected"]["exterior"] if d["inferred_wall"]} \
            == ({"low", "high"} if mode == "mixed" else {"high"}), (
            "the premise: the inferred-wall doors are hung both ways, or the path is not guarded")
    return fx


@pytest.mark.parametrize("hinge", ["as-frozen", "high", "unseated-mixed"])
@pytest.mark.parametrize("path", _fixtures(), ids=lambda p: p.stem)
def test_the_python_ink_stands_every_leaf_and_window_where_the_contract_does(path, hinge):
    """WP-14.4: THE CONTRACT WAS A CONTRACT ABOUT A MODEL. `derive_openings` was held to the
    fixture and nothing held the INK to either -- the plate could hang a leaf from the other jamb,
    swing it into the other room or stand a window on another face while `expected` stayed green,
    which is the class WP-5.11 names (a green suite proved the model and said nothing about the
    drawing). Every single leaf's hinge and swing, and every window's glazing, is read off the
    rendered plate through the plate's own stated frame and put where the contract says."""
    fx = json.loads(path.read_text())
    if hinge == "high":
        fx = _rehung(fx, "high")
    elif hinge == "unseated-mixed":
        fx = _rehung(fx, "mixed", unseat=True)
    IR, ink = _plate_from(fx)
    plates = {p["level"]: p for p in ink.frames() if p.get("proj") == "plan"}
    wall = render_plan.ASSEMBLIES.wall_thickness({"footprint": fx["footprint"]})
    t = wall["exterior_in"] / 12.0
    leaves, glazing = [], []
    for it in ink.items:
        if it.tag != "line":
            continue
        a = [float(it.attrs[k]) for k in ("x1", "y1", "x2", "y2")]
        (leaves if "dr" in it.classes else glazing if "win" in it.classes else []).append(a)
    checked = 0
    for lv in fx["levels"]:
        pl = plates[lv["index"]]
        ft = lambda x, y: IR.to_model(pl, x, y)  # noqa: E731
        segs = lambda lines: [(ft(a[0], a[1]), ft(a[2], a[3])) for a in lines]  # noqa: E731
        drawn_leaves, drawn_glass = segs(leaves), segs(glazing)
        near = lambda p, q: abs(p[0] - q[0]) < 0.1 and abs(p[1] - q[1]) < 0.1  # noqa: E731
        exp = lv["expected"]
        doors_ = [(d["horiz"], d["pos_ft"], d["at_ft"], d["width_ft"], d["swing_positive"], d["hinge"], d["type"])
                  for d in exp["interior"]]
        doors_ += [(d["wall"] in "SN", d["at_ft"], d["edge_ft"], d["width_ft"], d["wall"] in "SW", d["hinge"], d["type"])
                   for d in exp["exterior"]]
        for horiz, along, across, w, pos, hinge, dtype in doors_:
            if dtype not in ("swing", None):
                continue
            h_along = along - w / 2 if hinge != "high" else along + w / 2
            H = (h_along, across) if horiz else (across, h_along)
            E = (H[0], H[1] + (w if pos else -w)) if horiz else (H[0] + (w if pos else -w), H[1])
            assert any((near(a, H) and near(b, E)) or (near(a, E) and near(b, H)) for a, b in drawn_leaves), (
                f"{path.stem} {lv['id']}: a {w} ft leaf hung {hinge} at {H} swinging to {E} is not on the plate")
            checked += 1
        for win in exp["windows"]:
            wl, along, edge, w = win["wall"], win["at_ft"], win["edge_ft"], win["width_ft"]
            mid_across = edge - t / 2 if wl in "SW" else edge + t / 2
            M = (along, mid_across) if wl in "SN" else (mid_across, along)
            assert any(near(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), M)
                       and abs(((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5 - w) < 0.1
                       for a, b in drawn_glass), (
                f"{path.stem} {lv['id']}: the {w} ft {wl} window of {win['room']} is not glazed at {M}")
            checked += 1
    assert checked > 20, f"only {checked} openings read -- the check would pass on a plate with none"


# ------------------------------------------------------------------ the bench's leaf, held to this file's
# WP-14.6's second audit. `workbench/app/src/sheet/marks.js::leafOf` is the bench's single leaf and
# `pairOf` its pair; `render_plan.sweep_flag` is the plate's sweep rule. Six mutations of the bench's
# door and window geometry left every app test green, and the JS half of this contract could not call
# Python. This runs the bench's own module under node and holds every case a leaf can be -- either
# wall, either jamb, either side, and the pair -- to the plate's points and the plate's flag.

def _node_json(script, payload):
    import shutil
    import subprocess
    if not shutil.which("node"):
        pytest.skip("COULD NOT EVALUATE: node is not installed, so the bench's module cannot be run")
    r = subprocess.run(["node", "--input-type=module", "-e", script], input=json.dumps(payload),
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr[-2000:]
    return json.loads(r.stdout)


def _plate_leaves(horiz, px, py, w, positive, hinge, dtype):
    """The leaves `render_plan._door` draws for one door, in the plate's own screen frame at unit
    scale (x right, y DOWN): its jambs A (low) and B (high), and `leaf()`'s tip and far jamb. The
    flag is `render_plan.sweep_flag`'s, the function itself."""
    half = w / 2.0
    if horiz:
        A, B = (px - half, -py), (px + half, -py)
    else:
        A, B = (px, -py + half), (px, -py - half)

    def leaf(h, radius, to):
        tip = (h[0], h[1] + (-radius if positive else radius)) if horiz else \
              (h[0] + (radius if positive else -radius), h[1])
        return {"hinge": h, "tip": tip, "far": to, "sweep": render_plan.sweep_flag(h, tip, to)}
    if dtype == "double":
        M = ((A[0] + B[0]) / 2.0, (A[1] + B[1]) / 2.0)
        return [leaf(A, half, M), leaf(B, half, M)]
    return [leaf(B, w, A) if hinge == "high" else leaf(A, w, B)]


def test_the_bench_leaf_is_the_plates_leaf_and_turns_by_the_plates_sweep_rule():
    cases = []
    for horiz in (True, False):
        for positive in (True, False):
            for hinge in ("low", "high"):
                cases.append((horiz, positive, hinge, "swing", 3.0))
            cases.append((horiz, positive, "low", "double", 6.0))
    marks = (ROOT / "workbench" / "app" / "src" / "sheet" / "marks.js").as_uri()
    script = (
        "import { leafOf, pairOf } from '%s';\n"
        "let raw = ''; for await (const c of process.stdin) raw += c;\n"
        "const out = JSON.parse(raw).map((d) => (d.type === 'double' ? pairOf(d) : [leafOf(d)])\n"
        "  .map((l) => ({ hinge: l.hinge, tip: l.tip, far: l.far, sweep: l.sweep })));\n"
        "process.stdout.write(JSON.stringify(out));\n") % marks
    descs = []
    for horiz, positive, hinge, dtype, w in cases:
        d = {"x": 10.0, "y": 5.0, "w": w, "horiz": horiz, "hinge": hinge, "type": dtype}
        d["swingUp" if horiz else "swingRight"] = positive
        descs.append(d)
    got = _node_json(script, descs)
    near = lambda p, q: abs(p[0] - q[0]) < 1e-9 and abs(p[1] - q[1]) < 1e-9  # noqa: E731
    flags = set()
    for (horiz, positive, hinge, dtype, w), js in zip(cases, got):
        py = _plate_leaves(horiz, 10.0, 5.0, w, positive, hinge, dtype)
        what = "%s %s wall, hung %s, opening %s" % (dtype, "horizontal" if horiz else "vertical", hinge,
                                                    "+" if positive else "-")
        assert len(js) == len(py), what
        for a, b in zip(js, py):
            for k in ("hinge", "tip", "far"):
                assert near(a[k], b[k]), "%s: the bench's %s is %s, the plate's %s" % (what, k, a[k], b[k])
            assert a["sweep"] == b["sweep"], "%s: the bench turns %s, render_plan.sweep_flag %s" % (
                what, a["sweep"], b["sweep"])
            flags.add(a["sweep"])
    assert flags == {0, 1}, "the premise: the table reaches both flags, or it cannot tell a flag from its inverse"


# ------------------------------------------------------------------ what the bench is served
# WP-14.6's second audit. `mcp_server/core.py::placement_summary` is the placement the bench draws,
# and `Sheet.jsx` read `placement.appendages.placed` from a return that never carried it, so on
# good-02 and good-04 the bench called the terrace door undrawable over the hole the plate cut for it.
# Nothing held what the app READS to what the server SERVES. This does, for every key read off a
# placement anywhere in the app's source.

_SERVED = {}


def _served(pid):
    if pid not in _SERVED:
        import copy
        geo = modcache.load("geometry", str(ROOT / "build" / "geometry.py"))
        core = modcache.load("tdlcore", str(ROOT / "mcp_server" / "core.py"))
        plan = json.loads((ROOT / "plans" / "reference" / (pid + ".json")).read_text())
        placed = geo.solve(copy.deepcopy(plan), engine="heuristic")
        _SERVED[pid] = (placed, core.placement_summary(placed))
    return _SERVED[pid]


# A key the app reads that `placement_summary` does not serve, and why it is still right. Each reason
# is checked below, and an exception that has stopped being needed fails as loudly as a missing key.
_READ_NOT_SERVED = {
    "sketch": "workbench/server/evaluate.py writes it onto the placement it returns behind a wall drag",
    "levels": "derive.js::levelRooms also reads a placed PLAN record, whose rooms are under `levels`; "
              "the Round hands it one (round/overlays.js), and the served placement carries `rooms`",
}


# A KEY READ, AND NOT A METHOD CALL. The served placement is JSON and carries no function, so a
# name followed by `(` is a call on some OTHER value that happens to be called `placed`. The merge
# of the two Phase 14s (27 Sep 2026) brought two: main's `plate/assemblyPlan.js` keeps its label
# positions in a local array named `placed` (`.some`, `.flatMap`, `.map`) and `styles/styleTree.js`
# a Set of the same name (`.has`, `.add`), and this scan -- which neither parent ran against the
# other's files -- read all five as placement keys the server does not serve. The `\b` before the
# lookahead is load-bearing: without it `some(` backtracks to the key `som`.
_READ_RE = r"\bplace(?:ment|d)\??\.([A-Za-z_]\w*)\b(?!\s*\()"


def _app_reads():
    """{key: files} for every key read off a placement in the app's live source (comments stripped).
    A SELECTOR, and its reach is stated: a read off a variable named `placement`, or `placed` --
    the two names the app gives one (`sheet/refusal.js` takes it as `placed`, and reads `sketch`
    only that way, which is why the first version of this scan could not see `sketch` read at all)
    -- that is not called (`_READ_RE`). A read through any other name is outside it."""
    import re
    import subprocess
    files = subprocess.run(["git", "ls-files", "-co", "--exclude-standard", "workbench/app/src"],
                           cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    reads = {}
    for rel in sorted(files):
        if not rel.endswith((".js", ".jsx", ".mjs")) or ".test." in rel:
            continue
        src = (ROOT / rel).read_text(encoding="utf-8")
        live = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
        live = re.sub(r"(^|[^:])//[^\n]*", r"\1", live)
        for m in re.finditer(_READ_RE, live):
            reads.setdefault(m.group(1), set()).add(rel)
    return reads


def test_the_scan_reads_a_key_and_not_a_call_on_another_value_of_the_same_name():
    """The narrowing is driven both ways: a read the sheet makes is still a read, however it is
    spelled, and a call on a local `placed` is not one."""
    import re
    reads = lambda src: [m.group(1) for m in re.finditer(_READ_RE, src)]
    assert reads("const f = placement?.footprint; placed.sketch && x;") == ["footprint", "sketch"]
    assert reads("(placement.walls || []).map(w => w)") == ["walls"]
    assert reads("placement?.hearths?.map((h) => h)") == ["hearths"]
    assert reads("if (placed.some((p) => p.overflow)) p.placed.map(f); placed.has(id); placed.add (id)") == []


def test_every_placement_key_the_app_reads_is_served():
    placed, served = _served("good-02-portico-library-house")
    reads = _app_reads()
    assert {"footprint", "walls", "hearths", "appendages", "sketch"} <= set(reads), (
        "the premise: the scan finds the keys the sheet is known to read, or it is reading nothing: %s"
        % sorted(reads))
    assert "workbench/app/src/sheet/refusal.js" in reads["sketch"], (
        "the premise: `sketch` is read as `placed.sketch` in sheet/refusal.js, the case a scan of "
        "`placement.` alone could not see")
    missing = {k: sorted(v) for k, v in reads.items() if k not in served and k not in _READ_NOT_SERVED}
    assert not missing, ("the app reads a placement key the server does not serve -- a surface drawing "
                         "from a field that is always absent: %s" % missing)
    for k, why in _READ_NOT_SERVED.items():
        assert k in reads, "%s is no longer read by the app; remove its exception (%s)" % (k, why)
        assert k not in served, "%s is served now; remove its exception (%s)" % (k, why)
    evaluate = (ROOT / "workbench" / "server" / "evaluate.py").read_text(encoding="utf-8")
    assert '["placement"]["sketch"]' in evaluate, "the sketch exception's reason no longer holds"
    assert "rooms" in served and "levels" not in served, "the levels exception's reason no longer holds"


def test_the_placement_serves_the_appendages_the_record_places():
    placed, served = _served("good-02-portico-library-house")
    ap = (placed.get("appendages") or {}).get("placed") or []
    assert any(a["room"] == "terrace" for a in ap), "the premise: good-02 places its terrace"
    assert served.get("appendages") == placed.get("appendages"), (
        "the bench draws the terrace and its door from what is served, and it is served nothing")
