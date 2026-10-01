"""The second occurrences WP-15.8's audit pass found of the defects the audit had fixed once.

Auditor F searched the tree for each shape WP-15.8 removed somewhere else. Every one below was
live or reachable, and each test drives the case that showed it, with the shipped record or a
control beside it so the guard cannot pass by never reaching the branch:

- a stack reserved every wall of its LETTER, 31 ft away in another massing element;
- an exterior door was seated before the masonry was reserved, over a stack and inside a breast;
- a door refusal named a declared wall the room never declared, and a cause that did not fail;
- a door on the dependency's south face was "a service door on the entrance front";
- a partly seated front window was counted undrawn whole, and its seated sashes left the mirror;
- three more readers of a window skipped a partly seated one;
- the spine was chosen from every element, so the hyphen became the house's through-axis once
  its partly seated window counted;
- a type fact read HELD when some of its claims could not be judged.

Nothing a test here does writes inside the repository: every record is a deep copy.
"""
import copy
import json
import os

import pytest

from conftest import ROOT

import modcache


def _m(name):
    return modcache.load(name, os.path.join(ROOT, "build", f"{name}.py"))


OP, GEO, AX, TF, TH, FU, PC = (_m(n) for n in ("openings", "geometry", "axis", "typefacts",
                                               "threshold", "furniture", "plan_check"))


@pytest.fixture(scope="module")
def C():
    return PC.load_corpus()


def _placed(pid):
    """The shipped record placed on the heuristic (deterministic), on a private cache."""
    path = next(p for p in (os.path.join(ROOT, "plans", f"{pid}.json"),
                            os.path.join(ROOT, "plans", "reference", f"{pid}.json"))
                if os.path.exists(p))
    saved = GEO._SOLVE_CACHE
    GEO._SOLVE_CACHE = {}
    try:
        return GEO.solve(json.load(open(path)), engine="heuristic")
    finally:
        GEO._SOLVE_CACHE = saved


@pytest.fixture(scope="module")
def tidewater():
    return _placed("tidewater-georgian-careful")


def _fresh(placed):
    """The placed rooms with every opening's placement stripped, ready for `openings.place`."""
    pl = copy.deepcopy(placed)
    for k in ("stair", "opening_report", "threshold", "hearths", "appendages"):
        pl.pop(k, None)
    for lv in pl["levels"]:
        for r in lv["rooms"]:
            r.pop("fixture_layout", None)
            r.pop("furniture_layout", None)
            for d in r.get("doors") or []:
                for k in OP.PLACEMENT_DOOR_KEYS:
                    d.pop(k, None)
            for w in r.get("windows") or []:
                for k in OP.PLACEMENT_WINDOW_KEYS:
                    w.pop(k, None)
    return pl


def _room(pl, rid, level=0):
    return next(r for lv in pl["levels"] if (lv.get("index") or 0) == level
                for r in lv["rooms"] if r["id"] == rid)


# ------------------------------------------------------------------ the stack's own wall line

def test_a_stack_reserves_only_the_wall_line_it_stands_on(tidewater, C):
    """The main block's W stack reserved the west wall of the dependency's pantry, 31 ft away,
    because the reservation matched a room by the wall's LETTER. Driven with a W window on the
    pantry: it is seated now. The control is the library's E wall on the main block, which the E
    stack still takes."""
    pl = _fresh(tidewater)
    _room(pl, "pantry").setdefault("windows", []).append({"wall": "W", "count": 1, "width_ft": 3.0})
    OP.place(pl, C)
    win = [w for w in _room(pl, "pantry")["windows"] if w["wall"] == "W"][0]
    assert win.get("positions_ft") and not win.get("unplaced"), (
        "a window on the dependency's own west wall was refused for a stack on the main block's",
        win.get("unplaced"))
    W, H = pl["footprint"]["width_ft"], pl["footprint"]["depth_ft"]
    rooms = pl["levels"][0]["rooms"]
    spans = OP._masonry_spans(rooms, W, H, OP.envelopes(pl), pl["hearths"], 0)
    stacked = {k for k, _s, what in spans if what == "the chimney stack"}
    assert ("library", "E") in stacked, ("the control: the main block's own E wall", stacked)
    assert not {k for k in stacked if k[0] in ("pantry", "powder")}, stacked


def test_an_exterior_door_is_seated_clear_of_the_masonry(tidewater, C):
    """An exterior door was seated before the masonry was reserved: a library door driven onto
    its E wall stood on the stack and inside the drawn breast. It keeps out of both now, or is
    refused naming what took the wall."""
    pl = _fresh(tidewater)
    lib = _room(pl, "library")
    lib["exterior_walls"] = ["E"]
    lib["doors"].append({"to": "exterior", "width_ft": 3.0})
    OP.place(pl, C)
    d = [x for x in _room(pl, "library")["doors"] if x["to"] == "exterior"][0]
    W, H = pl["footprint"]["width_ft"], pl["footprint"]["depth_ft"]
    spans = [s for k, s, _w in OP._masonry_spans(pl["levels"][0]["rooms"], W, H,
                                                 OP.envelopes(pl), pl["hearths"], 0)
             if k == ("library", "E")]
    assert spans, "the premise: the library's E wall carries masonry"
    if d.get("unplaced"):
        assert "chimney" in d["unplaced"]["reason"], d["unplaced"]
    else:
        lo, hi = d["position_ft"] - 1.5, d["position_ft"] + 1.5
        assert all(hi <= a or lo >= b for a, b in spans), (d["position_ft"], spans)


def test_a_door_refusal_says_what_failed_and_names_no_wall_the_room_never_declared():
    """`bad-05`'s garage declares no exterior wall, and its one boundary wall is shorter than its
    24 ft door. It was refused for "no declared exterior wall of this room has a free run", with
    a `declared_wall` of S."""
    pl = _placed("bad-05-two-story-spec-colonial")
    g = _room(pl, "garage")
    assert not g.get("exterior_walls"), "the premise: the garage declares no exterior wall"
    d = [x for x in g["doors"] if x["to"] == "exterior"][0]
    u = d.get("unplaced") or {}
    assert "shorter than the door" in u.get("reason", ""), u
    assert "declared" not in u.get("reason", "") and "declared_wall" not in u, u
    assert u["have"]["walls_too_short"] == u["have"]["walls_tried"], u


# ------------------------------------------------------------------ the entrance front

def test_a_door_on_another_elements_face_is_not_on_the_entrance_front(tidewater, C):
    """The kitchen's door stands on the WEST DEPENDENCY's own south face, 5.28 ft behind the
    front, and the stoop pass called it "a service door on the entrance front"."""
    k = [d for d in _room(tidewater, "kitchen")["doors"] if d["to"] == "exterior"]
    assert k and k[0].get("wall") == "S", "the premise: the kitchen's door is on an S wall"
    th = tidewater["threshold"]
    said = [u for u in th["unplaced"] if "kitchen" in u.get("what", "")]
    assert said, "the kitchen's door is not named at all"
    assert not any("ENTRANCE face" in u["reason"] for u in said), said
    assert not any("a service door" in u["reason"] for u in th["unplaced"]), th["unplaced"]
    # the control: the porch's door IS on the entrance front, and is what the stoop stands at
    porch = [d for d in _room(tidewater, "porch")["doors"] if d["to"] == "exterior"][0]
    assert TH._on_the_entrance_front(tidewater, _room(tidewater, "porch"), porch, "S")
    assert not TH._on_the_entrance_front(tidewater, _room(tidewater, "kitchen"), k[0], "S")


# ------------------------------------------------------------------ a partly seated window

def _partial(room, wall, seated, count=2):
    room.setdefault("windows", []).append({
        "wall": wall, "count": count, "width_ft": 3.0, "positions_ft": list(seated),
        "unplaced": {"reason": f"{count - len(seated)} of {count} unit(s) had no clear run"}})


def test_a_partly_seated_front_window_counts_its_seated_units_and_only_its_refused_ones():
    """`good-02`'s front read 3 units undrawn where it is 1, and its seated sashes left the mirror
    behind the fatal `one-bay-symmetry-break` (2 of 2 unmatched against the drawn 3 of 4)."""
    pl = _placed("good-02-portico-library-house")
    fo = AX.front_openings(pl, 0)
    front = AX.front_of(pl)
    partial = [(r, w) for lv in pl["levels"][:1] for r in lv["rooms"]
               for w in (r.get("windows") or [])
               if (w.get("wall") or "").upper() == front and w.get("unplaced") and w.get("positions_ft")]
    assert partial, "the premise: good-02's front carries a partly seated window"
    at = {(o["room"], o["pos_ft"]) for o in fo["openings"] if o["kind"] == "window"}
    for r, w in partial:
        for p in w["positions_ft"]:
            assert (r["id"], round(p, 3)) in at, ("a seated sash left the front", r["id"], p)
    want = sum(max(0, int(w.get("count") or 1) - len(w.get("positions_ft") or []))
               for lv in pl["levels"][:1] for r in lv["rooms"] for w in (r.get("windows") or [])
               if (w.get("wall") or "").upper() == front and w.get("unplaced"))
    # 1 -> 2 AT WP-16.6 (1 Oct 2026): the living room's three sashes seat one where they seated
    # two, the other two refused by the pier floor (R5) -- a foot apart they fitted, a window's
    # width apart they do not. The window is still PARTLY seated, which is this test's subject,
    # and the count is still the refused units and not the window's whole count.
    assert fo["declared_but_unplaced"] == want == 2, (fo["declared_but_unplaced"], want)


def test_three_more_readers_take_a_partly_seated_window_by_its_seated_sashes():
    """`through_axis`, the between-the-windows piers and the wall-run check each skipped a window
    carrying `unplaced`, which beside `positions_ft` means only SOME of its units were refused."""
    room = {"id": "hall", "doors": [{"to": "exterior", "wall": "N", "position_ft": 5.0}],
            "windows": []}
    _partial(room, "S", [4.0])
    assert AX.through_axis(room) == ("N", "S")
    assert FU._piers(room) == {"S": [(2.5, 5.5)]}
    # the control: a window refused whole carries no positions and takes no wall
    whole = {"id": "hall", "doors": room["doors"],
             "windows": [{"wall": "S", "count": 1, "width_ft": 3.0, "unplaced": {"reason": "x"}}]}
    assert AX.through_axis(whole) is None and FU._piers(whole) == {}


def test_the_wall_run_check_counts_a_partly_seated_windows_sashes(tidewater, C):
    """Driven through `plan_check` on the placed Tidewater record: the dining room keeps one long
    wall clear for its sideboard. A seated sash of a partly refused pair on that wall must take it
    -- the finding fires -- and the same window refused whole must not. Before the fix the partly
    refused window was skipped whole and the two read alike."""
    pl = copy.deepcopy(tidewater)
    rid = next((r["id"] for lv in pl["levels"][:1] for r in lv["rooms"]
                if any(it.get("needs_uninterrupted_wall_ft")
                       for it in (C["rooms"].get(r["type"], {}).get("furniture") or []))), None)
    if rid is None:
        pytest.skip("COULD NOT EVALUATE: no ground room on this record wants an unbroken wall")
    r = _room(pl, rid)
    g = r["geometry"]
    # every wall of the room taken by a seated sash at its middle, one of them from a partly
    # refused pair; the whole-refusal twin frees exactly that one wall again
    r["doors"] = []
    r["windows"] = []
    mids = {"S": g["x_ft"] + g["width_ft"] / 2, "N": g["x_ft"] + g["width_ft"] / 2,
            "W": g["y_ft"] + g["depth_ft"] / 2, "E": g["y_ft"] + g["depth_ft"] / 2}
    runs = {"S": g["width_ft"], "N": g["width_ft"], "W": g["depth_ft"], "E": g["depth_ft"]}
    for w, m in mids.items():
        r["windows"].append({"wall": w, "count": 1, "width_ft": runs[w] - 1.0, "positions_ft": [m]})
    _partial(r, "N", [mids["N"]])
    r["windows"][-1]["width_ft"] = runs["N"] - 1.0
    r["windows"] = [x for x in r["windows"] if not (x["wall"] == "N" and "unplaced" not in x)]
    whole = copy.deepcopy(pl)
    for x in _room(whole, rid)["windows"]:
        if x.get("unplaced"):
            x["positions_ft"] = []

    def finding(p):
        return [f for f in PC.check(p).get("findings", [])
                if f.get("kind") == "wall-run" and f.get("room") == rid]
    fired, freed = finding(pl), finding(whole)
    assert fired, "a seated sash of a partly refused pair left its wall free for the sideboard"
    assert "N" in fired[0]["walls_with_windows"], fired[0]
    assert not freed or "N" not in freed[0]["walls_with_windows"], freed


# ------------------------------------------------------------------ the spine is the main block's

def test_the_spine_is_chosen_from_the_main_block_only(tidewater, C):
    """With a partly seated window counting, the hyphen's back hall reaches its own S and N walls
    and was taken for the house's through-axis, 26 ft off the main block's centre line.

    WITH THE CATALOGUE, AS `plan_check` CALLS IT: without it the reader takes only a room whose
    TYPE says "passage", the back hall is never a candidate, and this passed with the filter
    deleted -- the one blind mutation of the pass, caught before commit."""
    bh = _room(tidewater, "backhall")
    assert AX.through_axis(bh), "the premise: the hyphen's back hall spans its own element"
    assert C["rooms"][bh["type"]].get("function_class") == "circulation", "the premise"
    sp = AX.spine(tidewater, 0, C)
    assert sp.get("room") != "backhall", sp
    if sp.get("room"):
        els = _m("elements").elements(tidewater)
        main = next(e for e in els if e.get("role") == "main")
        assert _m("elements").element_of(tidewater, _room(tidewater, sp["room"]), els) is main


# ------------------------------------------------------------------ held on part is not held

def test_a_type_fact_held_on_part_of_its_claims_is_unjudged():
    """`typefacts`' own note: "unjudged is never held". Stacks and the hearth returned HELD when
    every JUDGED claim held, whatever could not be judged, and tiling read an unmeasured level as
    no residual at all."""
    def tally(kept, unjudged, broken=0):
        return {"levels": [], "geometry_report": {"stacking": {
            "kept": [{"room": f"k{i}", "over": "x", "level": 1} for i in range(kept)],
            "broken": [{"room": f"b{i}", "over": "x", "level": 1} for i in range(broken)],
            "unjudged": [{"room": f"u{i}", "over": "x", "reason": "no rect"} for i in range(unjudged)]}}}
    assert TF.stacks(tally(1, 0))["status"] == TF.HELD
    assert TF.stacks(tally(1, 1))["status"] == TF.UNJUDGED
    assert TF.stacks(tally(1, 1, broken=1))["status"] == TF.DOWNGRADED
    assert TF.stacks(tally(0, 1))["status"] == TF.UNJUDGED
    lv = lambda v: {"uncovered_sf": v}                                        # noqa: E731
    assert TF.tiling_status({"levels": [lv(0.0), lv(0.0)]}) == TF.HELD
    assert TF.tiling_status({"levels": [lv(0.0), lv(None)]}) == TF.UNJUDGED
    assert TF.tiling_status({"levels": [lv(None), lv(999.0)]}) == TF.DOWNGRADED
    assert TF.tiling_status({"levels": []}) == TF.UNJUDGED


def test_a_hearth_fact_held_on_part_of_its_fires_is_unjudged():
    """The hearth half of the rule, driven on a two-room house under a massing whose flues stand
    on the gable walls: a fire on the W gable, flush with the face, holds; a fire on the N wall is
    one the massing puts no flue on and cannot be judged. Held alone, HELD; with the second fire,
    UNJUDGED -- never HELD on the one fire that could be read."""
    def plan(fires):
        rooms = [{"id": f"r{i}", "geometry": {"x_ft": 0.0 if w == "W" else 12.0, "y_ft": 0.0,
                                                "width_ft": 10.0, "depth_ft": 30.0},
                  "hearth": [{"wall": w}]} for i, w in enumerate(fires)]
        return {"massing": "four-over-four", "footprint": {"width_ft": 40.0, "depth_ft": 30.0},
                "levels": [{"index": 0, "rooms": rooms}]}
    assert TF.flue_walls_of(plan(["W"]))[0] == ("E", "W"), "the premise: gable-end flues"
    assert TF.hearth(plan(["W"]))["status"] == TF.HELD
    assert TF.hearth(plan(["W", "N"]))["status"] == TF.UNJUDGED
    assert TF.hearth(plan(["N"]))["status"] == TF.UNJUDGED


# ------------------------------------------------------------------ the plan DXF says what the sheet says

@pytest.mark.parametrize("pid", ["bad-03-narrow-lot-townhome", "spec-builder-colonial"])
def test_the_plan_dxf_prints_the_sheets_own_lines_and_what_it_leaves_out(pid, tmp_path):
    """The plan DXF wrote its own window line over the levels it draws -- 1 unit on `bad-03`
    where the sheet says 2 of 6 -- and none of the sheet's lines about the default bay grid, the
    spans, the furniture, the transfers or the engine; nor that it draws no exterior door, stair,
    fixture or furniture. It prints the sheet's own `disclosures.banner` lines now, and the grid
    line without the bearing clause, because the DXF tells no wall bearing."""
    ezdxf = pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
    EX, DISC, RP = _m("export_dxf"), _m("disclosures"), _m("render_plan")
    placed = _placed(pid)
    path = str(tmp_path / "p.dxf")
    res = EX.export_plan_dxf(copy.deepcopy(load_or_placed(pid)), path, solved=placed)
    assert "error" not in res, res
    said = {e.dxf.text for e in ezdxf.readfile(path).modelspace() if e.dxftype() == "TEXT"}
    want = [ln["text"] for ln in DISC.banner(placed, styles=RP.C.get("styles"),
                                            partis=RP._partis(), marked=False)
            if ln["id"] not in ("relaxations", "infeasible", "bay-module")]
    assert want, "the premise: the sheet says something of this placement"
    missing = [t for t in want if t not in said]
    assert not missing, missing
    assert EX.DXF_PLAN_OMITS in said
    grid = [t for t in said if t.startswith("BAY GRID AT THE PLACER'S DEFAULT")]
    assert all("BEARING" not in t for t in grid), grid
    # and the SHEETS keep the clause, because they do read their bearing walls off that grid: the
    # fact is shared and the consequence is not (a mutation dropping it from the sheets was blind
    # to every test but the corpus sheet digest)
    sheet = DISC.bay_module(placed)
    if sheet:
        assert grid, "the DXF draws the default grid and does not say so"
        assert sheet["text"].endswith(", AND THE BEARING WALLS ARE READ OFF IT"), sheet
    if pid.startswith("bad-03"):
        w = DISC.windows_not_drawn(placed)
        assert w and w["text"].startswith("2 OF 6") and w["text"] in said, (w, sorted(said))


def load_or_placed(pid):
    path = next(p for p in (os.path.join(ROOT, "plans", f"{pid}.json"),
                            os.path.join(ROOT, "plans", "reference", f"{pid}.json"))
                if os.path.exists(p))
    return json.load(open(path))
