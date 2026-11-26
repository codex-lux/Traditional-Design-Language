"""The line grid (26 Nov 2026): the tiling restated on the lines the walls stand on.

`geometry_cp._build` states "the rooms of a level tile their element" as a sum of area products
over a `NoOverlap2D`, which propagates nothing: on the stock Georgian brief's composed diagrams the
prover neither found a house nor proved there was none, and on one worker all five measured were
refused for bearing, stacks and tiling. `_line_grid` restates the same fact after `_build`: each
(level, element) has at most n + 1 distinct lines an axis, every room edge is one of them, and every
cell is covered by at most one room -- by exactly one under that group's own tiling literal.

It is REDUNDANT, and that is what these hold: nothing the ruled model admits is lost and nothing it
refuses is admitted, the built model does not move, the full-cover half follows the tiling literal
and nothing else, and what the hard steps say of "every type fact held together" is read off their
statuses, never off the clock. Every solve built here is bounded by deterministic time.
"""
import hashlib
import importlib.util
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("geometry_cp_lg", ROOT / "build" / "geometry_cp.py")
GC = importlib.util.module_from_spec(spec)
spec.loader.exec_module(GC)
from conftest import deterministic_solver  # noqa: E402

cp_model = pytest.importorskip(
    "ortools.sat.python.cp_model",
    reason="COULD NOT EVALUATE: the CP-SAT engine needs OR-Tools")

FEASIBLE = (cp_model.OPTIMAL, cp_model.FEASIBLE)


def _two_storey():
    """`geometry_cp._feasible_fixture` with an upper floor that stacks over the ground
    (`tests/test_cp_portfolio.py`'s fixture, restated because a test file is not imported)."""
    p = GC._feasible_fixture()
    p["massing"] = "four-over-four"
    p["levels"].append({"id": "upper", "index": 1, "floor_to_ceiling_ft": 9, "rooms": [
        {"id": "landing", "type": "landing", "width_ft": 8, "length_ft": 12,
         "stacks_over": "hall", "doors": [{"to": "chamber"}, {"to": "chamber2"}]},
        {"id": "chamber", "type": "bedroom", "width_ft": 13, "length_ft": 16,
         "exterior_walls": ["S", "W"], "stacks_over": "parlor", "doors": [{"to": "landing"}]},
        {"id": "chamber2", "type": "bedroom", "width_ft": 12, "length_ft": 14,
         "exterior_walls": ["N"], "stacks_over": "kitchen", "doors": [{"to": "landing"}]},
        {"id": "bath", "type": "bathroom", "width_ft": 8, "length_ft": 10,
         "exterior_walls": ["N", "E"], "doors": [{"to": "landing"}]},
    ]})
    return p


def _built(plan, release=("wall", "axis"), grid=True):
    """A model as the prover's walls-released hard step builds it: `_build`, the named kinds
    released, then the grid (or not). Returns (model, rooms, reqs, grid_counts)."""
    levels, prep = GC.GEO.prep_rooms(plan)
    fpd = GC._snap_fpd(GC.GEO.derive_footprint(plan, None, prep))
    ew = GC.GEO.entrance_walls(plan)
    m, rooms, reqs = GC._build(plan, prep, fpd, ew, frozenset(), objective=False)
    down = frozenset(GC._dk(k, key) for _l, _t, k, key in reqs.lits if k in release and key)
    m, rooms, reqs = GC._build(plan, prep, fpd, ew, down, objective=False)
    counts = GC._line_grid(m, rooms, reqs, plan, prep, fpd) if grid else None
    return m, rooms, reqs, counts


def _fix(model, rooms, vals):
    for key, (x, y, w, h) in vals.items():
        v = rooms[key]
        model.Add(v["x"] == x)
        model.Add(v["y"] == y)
        model.Add(v["w"] == w)
        model.Add(v["h"] == h)


def _solve(model, det=40):
    s = deterministic_solver(det)
    return s.Solve(model), s


@pytest.fixture(autouse=True)
def _grid_on(monkeypatch):
    monkeypatch.delenv("TDL_CP_LINE_GRID", raising=False)
    monkeypatch.setattr(GC, "LINE_GRID", True)


# ------------------------------------------------------------------ it is redundant, both ways
# The two-storey fixture cannot hold its rooms' bands with its tiling, stacks and bearing lines
# (both models say INFEASIBLE at once, which the agreement test below holds), so the placements are
# taken with the shape band released: tiling, stacks, bearing and the hearth all still hard.
CASES = [(GC._feasible_fixture, ("wall", "axis")), (_two_storey, ("wall", "axis", "shape"))]


@pytest.mark.parametrize("fixture,release", CASES)
def test_a_placement_the_bare_model_finds_is_admitted_by_the_grid(fixture, release):
    """Nothing the ruled model admits is lost. A placement found with NO grid, fixed room for room
    into a gridded copy, is still feasible -- with every type fact hardened in both."""
    plan = fixture()
    m, rooms, reqs, _ = _built(plan, release=release, grid=False)
    GC._harden(m, reqs)
    st, s = _solve(m)
    if st not in FEASIBLE:
        pytest.skip("COULD NOT EVALUATE: the bare model did not place the fixture in its work bound")
    vals = GC._values(s, rooms)
    g, grooms, greqs, counts = _built(plan, release=release, grid=True)
    assert counts and counts["groups"] >= 1 and counts["cells"] > 0, counts
    GC._harden(g, greqs)
    _fix(g, grooms, vals)
    st2, _ = _solve(g)
    assert st2 in FEASIBLE, "the grid refused a placement the ruled model admits: it is not redundant"


@pytest.mark.parametrize("fixture,release", CASES)
def test_a_placement_found_with_the_grid_is_the_bare_models_own(fixture, release):
    """Nothing the ruled model refuses is admitted: the grid only adds constraints, and this holds
    that by solving WITH it and fixing the answer into the bare hardened model."""
    plan = fixture()
    g, grooms, greqs, _ = _built(plan, release=release, grid=True)
    GC._harden(g, greqs)
    st, s = _solve(g)
    if st not in FEASIBLE:
        pytest.skip("COULD NOT EVALUATE: the gridded model did not place the fixture in its work bound")
    vals = GC._values(s, grooms)
    m, rooms, reqs, _ = _built(plan, release=release, grid=False)
    GC._harden(m, reqs)
    _fix(m, rooms, vals)
    st2, _ = _solve(m)
    assert st2 in FEASIBLE, "a gridded placement is not a placement of the ruled model"


RELEASES = [("wall", "axis"), ("wall", "axis", "shape"), ("wall", "axis", "tiling"),
            ("wall", "axis", "stack", "bearing"), ("wall", "axis", "shape", "stack"),
            ("wall", "axis", "shape", "bearing"), ("wall", "axis", "shape", "hearth")]


@pytest.mark.parametrize("release", RELEASES, ids=lambda r: "+".join(r[2:]) or "none")
def test_the_grid_and_the_bare_model_give_the_same_decided_answer(release):
    """A REDUNDANT CONSTRAINT CHANGES NO VERDICT. Over the states the ladder passes through on the
    two-storey fixture -- some feasible, some not -- the gridded and the bare hardened models agree
    wherever both decide, and the population holds BOTH answers, so a grid that refused everything
    or admitted everything would fail here."""
    got = {}
    for grid in (False, True):
        m, _rooms, reqs, _c = _built(_two_storey(), release=release, grid=grid)
        GC._harden(m, reqs)
        got[grid] = _solve(m, 60)[0]
    if cp_model.UNKNOWN in got.values():
        pytest.skip("COULD NOT EVALUATE: a model was not decided in its work bound")
    assert (got[True] in FEASIBLE) == (got[False] in FEASIBLE), (release, got)


def test_the_agreement_population_holds_both_answers():
    """The premise of the test above: the release sets it sweeps are not all one verdict."""
    seen = set()
    for release in RELEASES:
        m, _rooms, reqs, _c = _built(_two_storey(), release=release, grid=False)
        GC._harden(m, reqs)
        seen.add(_solve(m, 60)[0] in FEASIBLE)
    assert seen == {True, False}, "the sweep no longer holds a feasible AND an infeasible state"


def test_the_built_model_does_not_move_and_the_grid_is_added_after_it(monkeypatch):
    """`tests/test_cp_elements.py` hashes what `_build` returns. The grid is applied to a solve's
    own copy afterwards, as `_harden` is, so `_build` serialises identically with it on or off --
    and the gridded copy is a strictly larger model."""
    plan = _two_storey()

    def sha(grid_env):
        if grid_env is None:
            monkeypatch.delenv("TDL_CP_LINE_GRID", raising=False)
        else:
            monkeypatch.setenv("TDL_CP_LINE_GRID", grid_env)
        m, _r, _q, _c = _built(plan, grid=False)
        return hashlib.sha256(str(m.Proto()).encode()).hexdigest(), len(str(m.Proto()))
    on, n_on = sha(None)
    off, n_off = sha("0")
    assert on == off and n_on == n_off > 5000, "`_build` reads the grid switch: its model moved"
    monkeypatch.delenv("TDL_CP_LINE_GRID", raising=False)
    g, _r, _q, counts = _built(plan, grid=True)
    assert len(str(g.Proto())) > n_on and counts["cells"] > 0


def test_the_switch_turns_it_off_and_says_so(monkeypatch):
    plan = GC._feasible_fixture()
    monkeypatch.setenv("TDL_CP_LINE_GRID", "0")
    assert GC.line_grid_on() is False
    assert _built(plan, grid=True)[3] is None, "the grid was added with the switch off"
    monkeypatch.delenv("TDL_CP_LINE_GRID")
    monkeypatch.setattr(GC, "LINE_GRID", False)
    assert GC.line_grid_on() is False
    monkeypatch.setattr(GC, "LINE_GRID", True)
    assert GC.line_grid_on() is True and _built(plan, grid=True)[3]["groups"] >= 1


# ------------------------------------------------ the full-cover half follows the tiling literal
def _short_of_the_box(model, rooms, reqs, plan):
    """Force level 0 to leave floor uncovered: the rooms' areas sum to less than their box."""
    levels, prep = GC.GEO.prep_rooms(plan)
    fpd = GC._snap_fpd(GC.GEO.derive_footprint(plan, None, prep))
    box = int(round(fpd["W"])) * int(round(fpd["H"]))
    model.Add(sum(v["a"] for (lv, _rid), v in rooms.items() if lv == 0) <= box - 1)


def test_full_cover_is_held_only_where_the_tiling_literal_is():
    """THE AT-LEAST-ONE HALF RIDES ON THE GROUP'S OWN TILING LITERAL. A solve that does not assume
    the tiling (the ladder after it releases the fact, `_solve_assuming` naming other requirements)
    must not be held to full cover by the grid, or the grid would be a second, unreleasable tiling
    fact. Forced one square foot short of its box: feasible with the tiling unassumed, infeasible
    with it assumed -- and the same pair on the bare model, so the grid changed neither answer."""
    plan = GC._feasible_fixture()
    seen = {}
    for grid in (True, False):
        for assume_tiling in (False, True):
            m, rooms, reqs, _ = _built(plan, grid=grid)
            assert any(k == "tiling" for _l, _t, k, _key in reqs.lits), "the fixture states no tiling"
            m.ClearAssumptions()
            for lit, _t, k, _key in reqs.lits:
                if k != "tiling" or assume_tiling:
                    m.AddBoolOr([lit])
            _short_of_the_box(m, rooms, reqs, plan)
            st, _ = _solve(m)
            seen[(grid, assume_tiling)] = st
    assert seen[(True, True)] == cp_model.INFEASIBLE, "a tiling one foot short was admitted"
    assert seen[(True, False)] in FEASIBLE, (
        "the grid held full cover with the tiling literal unassumed: it is a second tiling fact")
    assert seen[(False, True)] == cp_model.INFEASIBLE and seen[(False, False)] in FEASIBLE, (
        "the bare model's own pair moved; the control is wrong")


def test_a_released_tiling_is_not_held_to_full_cover_either():
    """The other route to the same state: the ladder RELEASES the tiling (its key in `downgraded`),
    so the group has no literal at all, and the grid adds the at-most-one half alone."""
    plan = GC._feasible_fixture()
    m, rooms, reqs, counts = _built(plan, release=("wall", "axis", "tiling"), grid=True)
    assert not any(k == "tiling" for _l, _t, k, _key in reqs.lits)
    assert counts["groups"] >= 1
    GC._harden(m, reqs)
    _short_of_the_box(m, rooms, reqs, plan)
    st, _ = _solve(m)
    assert st in FEASIBLE, "a released tiling was still held to full cover by the grid"


# ----------------------------------------- what the hard steps said of every fact held together
def test_all_facts_is_proven_impossible_only_where_every_depth_was_refuted():
    TF = GC.GEO.TF
    inf = lambda *ds: [(d, "INFEASIBLE") for d in ds]                      # noqa: E731
    assert GC.all_facts_account(inf(0.0, 2.0, 4.0))["verdict"] == TF.ALL_FACTS_PROVEN_IMPOSSIBLE
    # a depth never reached is not a proof about it
    assert GC.all_facts_account(inf(0.0, 2.0))["verdict"] == TF.ALL_FACTS_UNDECIDED
    assert GC.all_facts_account(inf(0.0))["verdict"] == TF.ALL_FACTS_UNDECIDED
    # one step out of time is the clock's, whatever the others proved
    for i in range(3):
        steps = inf(0.0, 2.0, 4.0)
        steps[i] = (steps[i][0], "UNKNOWN")
        assert GC.all_facts_account(steps)["verdict"] == TF.ALL_FACTS_UNDECIDED, steps
    # a hard step that returned the placement holds them all
    assert GC.all_facts_account([(0.0, "OPTIMAL")], mode="portfolio")["verdict"] == TF.ALL_FACTS_HELD
    # nothing asked is nothing said
    assert GC.all_facts_account([]) is None
    assert set(GC.ALL_FACTS_DEPTHS_FT) == {0.0, 2.0, 4.0}


def test_the_hard_steps_line_says_proven_only_where_the_account_does():
    proven = GC.all_facts_note(1, [(0.0, "INFEASIBLE"), (2.0, "INFEASIBLE"), (4.0, "INFEASIBLE")])
    assert "PROVEN" in proven and "no placement exists" in proven
    und = GC.all_facts_note(4, [(0.0, "UNKNOWN"), (2.0, "INFEASIBLE"), (4.0, "UNKNOWN")])
    assert "PROVEN" not in und and "undecided" in und
    assert "+0 ft" in und and "+4 ft" in und and "+2 ft" not in und, und


def _placed(res, workers):
    if "error" in res or res.get("unsolved") or res.get("infeasible"):
        pytest.skip(f"COULD NOT EVALUATE: the fixture did not place on {workers} worker(s) on this "
                    f"machine ({res.get('status') or res.get('error') or 'infeasible'})")
    return res["solver"]


def test_on_one_worker_the_hard_step_runs_with_the_grid_and_not_without(monkeypatch):
    """THE ONE-CORE PATH. WP-17.5 kept the hard steps to a box with more than one core, so on one
    core the only step that can return a house holding every type fact never ran. With the grid on
    they run on one worker and the record says what they found; with it off the path is WP-17.5's
    exactly -- no hard attempt, and nothing said of all the facts together."""
    monkeypatch.setattr(GC, "portfolio_workers", lambda *a, **k: 1)
    sv = _placed(GC.solve_cp(_two_storey(), None, time_limit_s=40, candidates=80), 1)
    hard = [a for a in sv["attempts"] if str(a[1]).startswith("H:")]
    assert hard and sv["workers"] == 1, sv["attempts"]
    assert sv["line_grid"] and sv["line_grid"]["cells"] > 0
    assert sv["all_facts"] and sv["all_facts"]["verdict"] in GC.GEO.TF.ALL_FACTS_VERDICTS
    if sv["mode"] == "portfolio":
        assert sv["all_facts"]["verdict"] == GC.GEO.TF.ALL_FACTS_HELD
    monkeypatch.setattr(GC, "LINE_GRID", False)
    sv0 = _placed(GC.solve_cp(_two_storey(), None, time_limit_s=40, candidates=80), 1)
    assert not [a for a in sv0["attempts"] if str(a[1]).startswith("H:")], sv0["attempts"]
    assert sv0["line_grid"] is None and sv0["all_facts"] is None and sv0["mode"] == "ladder"
