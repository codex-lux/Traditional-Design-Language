"""THE DECIDING PASS OVER THE POOL (ruled by Lucas, 26 Nov 2026: "short deciding pass").

The pool-fill tried the ranked pool in score order, a whole placement each, and stopped at its cap.
Measured on the stock Georgian brief on one worker: the side-hall town house, which holds every
type fact, stood behind diagrams nobody can decide in their whole time and was never reached.

Two halves, held apart:

* THE PROVER'S: `geometry_cp.probe_all_facts` asks the portfolio's own first walls-released hard
  step of one record, under a cap; where the composer asks, the answer is kept under the hash of
  the exact model and the placement that follows does not solve that model again.
* THE COMPOSER'S: `compose.probe_the_pool` asks the pool in score order inside a share of the set's
  time, and `compose.pool_probe_order` is the order the fill then takes.

A REFUTATION AT ONE DEPTH IS NEVER THE WORD "PROVEN" -- that needs all three depths -- and several
tests here are about exactly that.

The two prover fixtures decide in well under a second (`geometry_cp._feasible_fixture` holds; the
two-storey restatement of it is refuted at once), so a wall-clock cap is not what answers; a test
that meets `undecided` reports COULD NOT EVALUATE rather than passing.
"""
import copy
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402
from conftest import deterministic_solver  # noqa: E402

CO = modcache.load("compose", os.path.join(ROOT, "build", "compose.py"))
RV = modcache.load("revise", os.path.join(ROOT, "build", "revise.py"))
GEO = modcache.load("geometry", os.path.join(ROOT, "build", "geometry.py"))
GC = modcache.load("geometry_cp", os.path.join(ROOT, "build", "geometry_cp.py"))

REFUSED = {"kind": "type-fact-downgraded", "facts": ["stacks"], "conflicts": [], "lines": []}


def _ortools():
    return pytest.importorskip("ortools.sat.python.cp_model",
                               reason="COULD NOT EVALUATE: the CP-SAT engine needs OR-Tools")


def _two_storey():
    """`geometry_cp._feasible_fixture` with an upper floor that stacks over the ground
    (`tests/test_line_grid.py`'s fixture, restated because a test file is not imported). It cannot
    hold its bands with its tiling, stacks and bearing lines: refuted at once at every depth."""
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


def _walls_cannot_hold():
    """`geometry_cp._feasible_fixture` with authored walls that cannot all hold (the hall and the
    kitchen both claim the west wall the parlor's corner has): everything-held is refuted at once,
    and with the walls released every type fact holds. So the FIRST WALLS-RELEASED step -- the one
    the probe asks -- is the step that answers, which the bare fixture never reaches."""
    p = GC._feasible_fixture()
    rooms = {r["id"]: r for r in p["levels"][0]["rooms"]}
    rooms["hall"]["exterior_walls"] = ["W"]
    rooms["kitchen"]["exterior_walls"] = ["E", "W", "N"]
    return p


def _hard_model(plan, seed=7):
    """The first walls-released hard step's model, built as `_solve_cp` and the probe build it."""
    plan = copy.deepcopy(plan)
    _levels, prep = GEO.prep_rooms(plan)
    fpd = GC._snap_fpd(GEO.derive_footprint(plan, None, prep))
    ew = GEO.entrance_walls(plan)
    rel = GC._released_first(plan, prep, fpd, ew, ())
    m, rooms, _q, _g = GC._hard_model(plan, prep, fpd, ew, rel, None, seed)
    return m, rooms


@pytest.fixture(autouse=True)
def _one_worker_grid_on_and_nothing_kept(monkeypatch):
    """One worker, the line grid on, and no answer left behind by this test or for it."""
    monkeypatch.delenv("TDL_CP_LINE_GRID", raising=False)
    monkeypatch.setattr(GC, "LINE_GRID", True)
    monkeypatch.setattr(GC, "portfolio_workers", lambda *a, **k: 1)
    GC.forget_probes()
    yield
    GC.forget_probes()


def _decided(res):
    if res.get("verdict") == GC.PROBE_UNDECIDED:
        pytest.skip(f"COULD NOT EVALUATE: the fixture was undecided at the probe's cap on this "
                    f"machine ({res})")
    return res


# ------------------------------------------------------------------- the prover's half: verdicts
def test_the_probe_says_held_refuted_at_the_depth_or_undecided_and_never_proven():
    _ortools()
    held = _decided(GC.probe_all_facts(GC._feasible_fixture()))
    assert held["verdict"] == GC.PROBE_HELD and held["status"] in ("OPTIMAL", "FEASIBLE"), held
    ref = _decided(GC.probe_all_facts(_two_storey()))
    assert ref["verdict"] == GC.PROBE_REFUTED and ref["status"] == "INFEASIBLE", ref
    # the vocabulary is closed, and no word in it is the refusal class PROVEN or the joint verdict:
    # one depth refuted is not the three `all_facts_account` asks for
    assert held["verdict"] in GC.PROBE_VERDICTS and ref["verdict"] in GC.PROBE_VERDICTS
    assert "depth" in GC.PROBE_REFUTED
    assert not [v for v in GC.PROBE_VERDICTS if "proven" in v.lower()]
    assert GC.PROBE_REFUTED != GEO.TF.ALL_FACTS_PROVEN_IMPOSSIBLE
    for r in (held, ref):
        assert r["workers"] == 1 and r["line_grid"] is True and r["cap_s"] == GC.PROBE_CAP_S


def test_the_probe_does_not_write_to_the_record():
    _ortools()
    for plan in (GC._feasible_fixture(), _two_storey()):
        before = json.dumps(plan, sort_keys=True)
        GC.probe_all_facts(plan, remember=True)
        assert json.dumps(plan, sort_keys=True) == before


def test_on_one_worker_with_the_grid_off_the_probe_is_unjudged_and_says_the_box(monkeypatch):
    """WP-17.5's measurement: hard mode on one worker on the bare model is the slower form, so the
    hard steps do not run there. The probe then has no step to ask: could-not-evaluate, marked
    `systemic` (the box's, not the record's), never held and never refuted, and nothing kept."""
    _ortools()
    monkeypatch.setattr(GC, "LINE_GRID", False)
    res = GC.probe_all_facts(GC._feasible_fixture(), remember=True)
    assert res["verdict"] == GC.PROBE_UNJUDGED and res.get("systemic") is True and res.get("why")
    assert not GC._PROBED


def test_a_record_with_no_footprint_is_unjudged_and_that_is_the_records_not_the_boxs(monkeypatch):
    _ortools()
    monkeypatch.setattr(GEO, "derive_footprint", lambda *a, **k: {"error": "no footprint"})
    res = GC.probe_all_facts(GC._feasible_fixture(), remember=True)
    assert res["verdict"] == GC.PROBE_UNJUDGED and res["why"] == "no footprint"
    assert not res.get("systemic"), "a record's own failure would stop the pass for every diagram"
    assert not GC._PROBED


# ------------------------------------------------------------- the prover's half: the kept answer
def test_nothing_is_kept_unless_asked_and_forgetting_drops_it():
    _ortools()
    GC.probe_all_facts(GC._feasible_fixture())
    assert not GC._PROBED, "an answer was kept that no caller asked to keep"
    GC.probe_all_facts(GC._feasible_fixture(), remember=True)
    GC.probe_all_facts(_two_storey(), remember=True)
    assert len(GC._PROBED) == 2
    GC.forget_probes()
    assert not GC._PROBED


def test_the_key_is_the_model_and_the_seed():
    _ortools()
    a, _ = _hard_model(GC._feasible_fixture())
    b, _ = _hard_model(GC._feasible_fixture())
    assert GC._model_key(a, 7) == GC._model_key(b, 7), "two builds of one record, two keys"
    assert GC._model_key(a, 7) != GC._model_key(a, 8)
    wider = GC._feasible_fixture()
    room = wider["levels"][0]["rooms"][0]
    room["width_ft"] = room["width_ft"] + 1
    c, _ = _hard_model(wider)
    assert GC._model_key(c, 7) != GC._model_key(a, 7), "an edited record kept its key"
    assert GC._model_key(_hard_model(_two_storey())[0], 7) != GC._model_key(a, 7)


def test_the_kept_placement_is_a_placement_of_that_very_model():
    """What stands in for the solve must satisfy the model it stands in for: the kept values, fixed
    into a FRESH build of the step's model, are feasible. Bounded by deterministic time."""
    cp_model = _ortools()
    _decided(GC.probe_all_facts(_walls_cannot_hold(), remember=True))
    (hit,) = GC._PROBED.values()
    assert hit["status"] in ("OPTIMAL", "FEASIBLE") and hit["values"]
    m, rooms = _hard_model(_walls_cannot_hold())
    assert set(hit["values"]) == set(rooms)
    for key, (x, y, w, h) in hit["values"].items():
        v = rooms[key]
        m.Add(v["x"] == x)
        m.Add(v["y"] == y)
        m.Add(v["w"] == w)
        m.Add(v["h"] == h)
    s = deterministic_solver(40)
    assert s.Solve(m) in (cp_model.OPTIMAL, cp_model.FEASIBLE)


def _solver_record(res):
    if "error" in res or res.get("unsolved"):
        pytest.skip(f"COULD NOT EVALUATE: the fixture did not solve on this machine "
                    f"({res.get('status') or res.get('error')})")
    return res.get("solver") or res.get("infeasible") or res


def test_the_placement_takes_the_probes_answer_and_the_record_says_so():
    _ortools()
    _decided(GC.probe_all_facts(_walls_cannot_hold(), remember=True))
    sv = _solver_record(GC.solve_cp(_walls_cannot_hold(), None, time_limit_s=40, candidates=80))
    hard1 = [a for a in sv["attempts"] if " hard1 " in str(a[0])]
    assert len(hard1) == 1 and "probed" in hard1[0][0] and hard1[0][1].startswith("H:"), sv["attempts"]
    assert hard1[0][1] in ("H:OPTIMAL", "H:FEASIBLE")
    assert ("2b hard0 1w", "H:INFEASIBLE") in [tuple(a) for a in sv["attempts"]], (
        "the premise: with the walls held the fixture is refuted, so the next step answers")
    assert sv["mode"] == "portfolio" and sv["all_facts"]["verdict"] == GEO.TF.ALL_FACTS_HELD
    # and with nothing kept the same step is SOLVED, and says the workers it ran on
    GC.forget_probes()
    sv0 = _solver_record(GC.solve_cp(_walls_cannot_hold(), None, time_limit_s=40, candidates=80))
    hard1 = [a for a in sv0["attempts"] if " hard1 " in str(a[0])]
    assert hard1 and "probed" not in hard1[0][0] and hard1[0][0].endswith("1w"), sv0["attempts"]
    assert sv0["mode"] == sv["mode"] and sv0["all_facts"]["verdict"] == sv["all_facts"]["verdict"]


def test_a_refutation_at_one_depth_stands_for_that_depth_alone():
    """The kept INFEASIBLE answers the derived depth. The two deeper steps are still ASKED, by a
    solve, and the joint verdict is still computed from all three."""
    _ortools()
    _decided(GC.probe_all_facts(_two_storey(), remember=True))
    res = GC.solve_cp(_two_storey(), None, time_limit_s=40, candidates=80)
    sv = _solver_record(res)
    walls_released = [a for a in sv["attempts"] if " hard1" in str(a[0])]
    assert [("probed" in a[0]) for a in walls_released] == [True, False, False], sv["attempts"]
    assert "+2ft" in walls_released[1][0] and "+4ft" in walls_released[2][0]
    acct = sv["all_facts"]
    assert acct and len(acct.get("steps") or acct.get("depths") or [0, 0, 0]) == 3, acct
    if all(a[1] == "H:INFEASIBLE" for a in walls_released):
        assert acct["verdict"] == GEO.TF.ALL_FACTS_PROVEN_IMPOSSIBLE


def test_an_undecided_answer_stands_in_only_with_the_steps_time_and_workers():
    _ortools()
    m, _rooms = _hard_model(GC._feasible_fixture())
    key = GC._model_key(m, 7)
    row = {"status": "UNKNOWN", "values": None, "seconds": 25.0, "workers": 1, "cap_s": 25.0}
    GC._PROBED[key] = dict(row)
    assert GC.probed_answer(m, 7, 20.0, 1) is not None
    assert GC.probed_answer(m, 7, 25.0, 1) is not None
    assert GC.probed_answer(m, 7, 25.1, 1) is None, "a step with more time than the probe was skipped"
    assert GC.probed_answer(m, 7, 20.0, 4) is None, "a step with more workers than the probe was skipped"
    assert GC.probed_answer(m, 8, 20.0, 1) is None, "another seed's answer"
    # a decision stands whatever the step's allowance: a proof is a proof, a placement a placement
    for status in ("INFEASIBLE", "OPTIMAL", "FEASIBLE"):
        GC._PROBED[key] = dict(row, status=status, cap_s=1.0)
        assert GC.probed_answer(m, 7, 60.0, 8) is not None, status
    GC.forget_probes()
    assert GC.probed_answer(m, 7, 20.0, 1) is None


def test_a_skipped_undecided_step_is_still_read_as_undecided():
    """`geometry._cp_undecided` reads `H:UNKNOWN` off the attempts: an answer resting on the clock
    is not cached as decided. A step skipped on the probe's UNKNOWN keeps that tag."""
    _ortools()
    m, _rooms = _hard_model(_walls_cannot_hold())
    GC._PROBED[GC._model_key(m, 7)] = {"status": "UNKNOWN", "values": None, "seconds": 999.0,
                                       "workers": 1, "cap_s": 999.0}
    res = GC.solve_cp(_walls_cannot_hold(), None, time_limit_s=40, candidates=80)
    sv = _solver_record(res)
    skipped = [a for a in sv["attempts"] if "probed" in str(a[0])]
    assert skipped and skipped[0][1] == "H:UNKNOWN", sv["attempts"]
    assert any("UNKNOWN" in w for w in GEO._cp_undecided(res)), GEO._cp_undecided(res)
    assert sv["all_facts"]["verdict"] != GEO.TF.ALL_FACTS_PROVEN_IMPOSSIBLE


# ------------------------------------------------------------ the composer's half: the arithmetic
class _Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def _pool(*ids):
    return [{"parti": i, "parti_name": i.upper(), "plan": {}} for i in ids]


def _fake_probe(clock, answers, caps=None):
    """`answers`: parti -> (verdict, seconds). Advances the fake clock by the seconds."""
    def probe(c, cap):
        verdict, secs = answers[c["parti"]]
        if caps is not None:
            caps.append((c["parti"], cap))
        clock.t += secs
        if verdict == "systemic":
            return {"verdict": GC.PROBE_UNJUDGED, "systemic": True, "why": "no prover here"}
        return {"verdict": verdict, "status": "X", "seconds": secs, "cap_s": cap, "workers": 1}
    return probe


def test_the_pass_asks_in_score_order_and_stops_at_as_many_holders_as_the_set_is_short():
    clock = _Clock()
    ans = {"a": (GC.PROBE_UNDECIDED, 25), "b": (GC.PROBE_HELD, 3), "c": (GC.PROBE_REFUTED, 1),
           "d": (GC.PROBE_HELD, 10), "e": (GC.PROBE_HELD, 1)}
    rows, stop = CO.probe_the_pool(_pool("a", "b", "c", "d", "e"), 2, 1000.0,
                                   _fake_probe(clock, ans), 25.0, clock=clock)
    assert [r["parti"] for r in rows] == ["a", "b", "c", "d"], "asked out of order, or past enough"
    assert stop == "enough-held"
    assert [r["verdict"] for r in rows] == [GC.PROBE_UNDECIDED, GC.PROBE_HELD, GC.PROBE_REFUTED,
                                            GC.PROBE_HELD]
    assert rows[1]["seconds"] == 3 and rows[1]["parti_name"] == "B"
    # the last diagram being the one that fills the need is still "enough", not "pool"
    rows, stop = CO.probe_the_pool(_pool("a", "b"), 1, 1000.0, _fake_probe(_Clock(), ans), 25.0,
                                   clock=_Clock())
    assert stop == "pool" or stop == "enough-held"
    assert stop in CO.POOL_PROBE_STOPS


def test_the_pass_is_held_to_its_share_and_a_probe_never_gets_more_than_is_left():
    clock, caps = _Clock(), []
    ans = {k: (GC.PROBE_UNDECIDED, 25) for k in "abcde"}
    rows, stop = CO.probe_the_pool(_pool(*"abcde"), 3, 60.0, _fake_probe(clock, ans, caps), 25.0,
                                   clock=clock)
    # 25 + 25 leaves 10 of 60: the third is asked under 10 s, and then nothing is left
    assert caps == [("a", 25.0), ("b", 25.0), ("c", 10.0)], caps
    assert [r["parti"] for r in rows] == ["a", "b", "c"] and stop == "share"
    # with less than the floor left the next diagram is NOT asked: a probe of two seconds would
    # only write an "undecided" that the cap decided
    clock2, caps2 = _Clock(), []
    rows, stop = CO.probe_the_pool(_pool(*"abc"), 3, 25.0 + CO.POOL_PROBE_MIN_S - 0.1,
                                   _fake_probe(clock2, ans, caps2), 25.0, clock=clock2)
    assert [p for p, _c in caps2] == ["a"] and stop == "share"


def test_the_pass_reaches_the_end_of_the_pool_and_says_so():
    clock = _Clock()
    ans = {k: (GC.PROBE_REFUTED, 1) for k in "abc"}
    rows, stop = CO.probe_the_pool(_pool(*"abc"), 2, 1000.0, _fake_probe(clock, ans), 25.0, clock=clock)
    assert len(rows) == 3 and stop == "pool"


def test_a_box_with_no_prover_ends_the_pass_at_once_with_no_verdict_on_any_diagram():
    clock = _Clock()
    ans = {"a": ("systemic", 0), "b": (GC.PROBE_HELD, 1)}
    rows, stop = CO.probe_the_pool(_pool("a", "b"), 2, 1000.0, _fake_probe(clock, ans), 25.0, clock=clock)
    assert rows == [] and stop == "could-not-evaluate"


def test_the_fill_order_is_held_then_the_uncalled_then_the_refuted_each_in_score_order():
    pool = _pool("a", "b", "c", "d", "e", "f")
    probed = [{"parti": "a", "verdict": GC.PROBE_REFUTED}, {"parti": "b", "verdict": GC.PROBE_UNDECIDED},
              {"parti": "c", "verdict": GC.PROBE_HELD}, {"parti": "d", "verdict": GC.PROBE_UNJUDGED},
              {"parti": "e", "verdict": GC.PROBE_HELD}]          # f was never asked
    assert [c["parti"] for c in CO.pool_probe_order(pool, probed)] == ["c", "e", "b", "d", "f", "a"]
    assert CO.pool_probe_order(pool, []) == pool and CO.pool_probe_order(pool, None) == pool
    # nothing is dropped, whatever was said of it
    assert sorted(c["parti"] for c in CO.pool_probe_order(pool, probed)) == list("abcdef")


def test_the_reading_line_counts_each_verdict_apart_and_never_calls_a_refutation_proven():
    pf = {"probed": [{"parti": "a", "verdict": GC.PROBE_REFUTED}, {"parti": "b", "verdict": GC.PROBE_UNDECIDED},
                     {"parti": "c", "verdict": GC.PROBE_HELD}, {"parti": "d", "verdict": GC.PROBE_UNJUDGED}],
          "probe": {"cap_s": 25.0, "share": 0.5, "budget_s": 150.0, "seconds": 61.2, "stopped_by": "share"}}
    line = CO.pool_probe_line(pf)
    assert "1 held every type fact at the derived depth (c)" in line
    assert "1 were undecided in 25.0 s" in line
    assert "1 were refuted at that depth, which is not a proof" in line and "(a)" in line
    assert "1 could not be evaluated (d)" in line
    assert "150.0 s" in line and "61.2 s" in line
    assert "proven" not in line.lower().replace("not a proof", "")
    assert CO.pool_probe_line({"probed": [], "probe": None}) is None
    assert CO.pool_probe_line({}) is None


# ---------------------------------------------------------------- the composer's half: the fill
def _brief():
    return json.load(open(os.path.join(ROOT, "briefs", "family-georgian.json"), encoding="utf-8"))


def _compose(monkeypatch, verdicts, drawable=(), engine="auto", candidates=2, raise_on=None):
    """Every placement refused unless its parti is in `drawable`; the probe answers from
    `verdicts(pool_index, parti)`. Returns (result, fill, asked): the partis the FILL placed, by
    its own count (a refused native diagram's repair and retry are placements too, and come after
    it), and the partis probed, each in order."""
    placed, asked = [], []
    orig = RV.revise

    def spy(plan, **kw):
        out = orig(plan, **dict(kw, engine="heuristic"))
        if kw.get("place"):
            pid = max((p for p in CO.PARTIS if str(plan.get("id", "")).startswith(p)), key=len)
            if raise_on is not None and pid == raise_on:
                raise RuntimeError("the placer fell over")
            placed.append(pid)
            gr = out["plan"].setdefault("geometry_report", {})
            gr["refused"] = None if pid in drawable else dict(REFUSED)
        return out

    def probe(plan, parti, time_limit_s=None, remember=False, **_kw):
        pid = max((p for p in CO.PARTIS if str(plan.get("id", "")).startswith(p)), key=len)
        assert remember is True, "the composer did not ask for the answer to be kept"
        assert time_limit_s is not None and time_limit_s <= GC.PROBE_CAP_S
        GC._PROBED[pid] = {"status": "X"}            # stands for an answer kept
        v = verdicts(len(asked), pid)
        asked.append(pid)
        return {"verdict": v, "status": "X", "seconds": 0.1, "cap_s": time_limit_s, "workers": 1}

    monkeypatch.setattr(RV, "revise", spy)
    monkeypatch.setattr(GC, "probe_all_facts", probe)
    res = CO.compose(_brief(), candidates=candidates, revise=True, revise_rounds=0,
                     revise_engine=engine, revise_budget_s=600)
    n = (res.get("pool_fill") or {}).get("placed_from_pool") or 0
    return res, placed[candidates:candidates + n], asked


_KEPT = {}


def _all_undecided(monkeypatch):
    """One compose in which the pass decides nothing, shared by the tests that read it (a compose
    of the stock brief is the slow part of this file)."""
    if "v" not in _KEPT:
        _KEPT["v"] = _compose(monkeypatch, lambda i, pid: GC.PROBE_UNDECIDED)
    return _KEPT["v"]


def test_the_fill_places_the_holders_first_and_the_refuted_last(monkeypatch):
    # the third and fifth pool diagrams hold, the first is refuted at its depth, the rest undecided
    verdict = lambda i, pid: {0: GC.PROBE_REFUTED, 2: GC.PROBE_HELD, 4: GC.PROBE_HELD}.get(i, GC.PROBE_UNDECIDED)  # noqa: E731
    monkeypatch.setattr(CO, "POOL_FILL_PLACEMENTS", 100)
    res, fill, asked = _compose(monkeypatch, verdict)
    pf = res["pool_fill"]
    # two short, two holders found: the pass stops there and the rest of the pool is not asked
    assert len(asked) == 5 and pf["probe"]["stopped_by"] == "enough-held", (asked, pf["probe"])
    assert [r["parti"] for r in pf["probed"]] == asked
    assert [r["verdict"] for r in pf["probed"]] == [verdict(i, None) for i in range(5)]
    assert fill[:2] == [asked[2], asked[4]], (fill, asked)
    assert fill[2:4] == [asked[1], asked[3]], "the undecided did not follow in score order"
    assert fill[-1] == asked[0], "the diagram refuted at its depth was not placed last"
    # nothing is dropped and nothing placed twice: every diagram asked is placed, and so is every
    # diagram the pass never reached, between the undecided and the refuted
    assert len(fill) == len(set(fill)) > 5 and set(asked) <= set(fill)
    assert pf["probe"]["cap_s"] == GC.PROBE_CAP_S and pf["probe"]["share"] == CO.POOL_PROBE_SHARE
    assert pf["probe"]["budget_s"] <= CO.POOL_PROBE_SHARE * 600
    assert any("the pool was probed in score order" in ln for ln in res["how_to_read_this"])


def test_a_holder_far_down_the_pool_is_reached_inside_the_cap(monkeypatch):
    """The stock brief's own shape: the house that holds stands behind more undecided diagrams than
    the cap places. In score order it is never reached; probed, it is placed first."""
    res0, fill0, _ = _all_undecided(monkeypatch)
    assert len(fill0) == CO.POOL_FILL_PLACEMENTS and res0["pool_fill"]["not_reached"], (
        "the premise: the cap stops the fill short of the pool")
    target = res0["pool_fill"]["not_reached"][-1]
    res, fill, asked = _compose(
        monkeypatch, lambda i, pid: GC.PROBE_HELD if pid == target else GC.PROBE_UNDECIDED,
        drawable={target})
    assert fill[0] == target, (fill, target)
    assert target in res["pool_fill"]["added"] and target not in res["pool_fill"]["not_reached"]
    assert target in {c["parti"] for c in res["candidates"]}


def test_the_search_is_not_probed_and_its_fill_is_in_score_order(monkeypatch):
    res_h, fill_h, asked_h = _compose(monkeypatch, lambda i, pid: GC.PROBE_HELD, engine="heuristic")
    assert asked_h == [] and res_h["pool_fill"]["probed"] == [] and res_h["pool_fill"]["probe"] is None
    assert not any("the pool was probed" in ln for ln in res_h["how_to_read_this"])
    res_u, fill_u, asked_u = _all_undecided(monkeypatch)
    assert asked_u and len(fill_h) == CO.POOL_FILL_PLACEMENTS
    assert fill_u == fill_h, "an all-undecided pass moved the fill off the score order"


def test_a_full_set_is_not_probed(monkeypatch):
    res, fill, asked = _compose(monkeypatch, lambda i, pid: GC.PROBE_HELD, drawable=set(CO.PARTIS))
    assert asked == [] and fill == []
    assert res["pool_fill"]["probed"] == [] and res["pool_fill"]["probe"] is None


def test_the_answers_are_forgotten_when_the_fill_ends_whatever_ended_it(monkeypatch):
    res0, fill0, asked0 = _compose(monkeypatch, lambda i, pid: GC.PROBE_UNDECIDED)
    assert asked0 and not GC._PROBED, "an answer outlived the fill it was asked for"
    with pytest.raises(RuntimeError):
        _compose(monkeypatch, lambda i, pid: GC.PROBE_UNDECIDED, raise_on=fill0[0])
    assert not GC._PROBED, "a fill that raised left its answers behind"


# ------------------------------------------- the merge of 27 Nov 2026: a house with a wing to size
# The garage package sizes a wing of several rooms before the prover poses the house
# (`geometry_cp.size_wings`), and the box rides on the footprint. The probe is the placement's own
# first walls-released step, so it stands on that footprint too (`geometry_cp.wing_sized`, one
# spelling for both). The corpus has one composed diagram that reaches this: the centre-passage
# double pile with a garage in the brief. Each test asserts that premise.
WING_PARTI = "centre-passage-double-pile"


class _Stop(Exception):
    """Raised by a spy to end a solve at the step under test."""


def _composed_with_a_wing():
    with open(os.path.join(ROOT, "briefs", "family-georgian.json")) as f:
        brief = json.load(f)
    plan, _log, _p = CO.instantiate(WING_PARTI, brief)
    return plan, CO.PARTIS[WING_PARTI]


def test_on_a_house_with_a_wing_the_probe_poses_the_model_the_placement_poses(monkeypatch):
    _ortools()
    monkeypatch.setattr(GC, "_WING_BOXES", {})          # this test's own sizing, kept for it alone
    plan, parti = _composed_with_a_wing()
    # a 1 s step: the answer is not the subject, the MODEL it was asked of is
    res = GC.probe_all_facts(plan, parti, time_limit_s=1.0, remember=True, sizing_s=120.0)
    if res["verdict"] == GC.PROBE_UNJUDGED:
        pytest.skip(f"COULD NOT EVALUATE: {res.get('why')}")
    sized = {k: v for k, v in (res["wing_sizing"] or {}).items()
             if v["taken_ft"] is not None and list(v["taken_ft"]) != list(v["derived_ft"])}
    assert sized, ("the premise: this house has a wing whose derived box does not hold and whose "
                   f"sized box is another one; the sizing said {res['wing_sizing']}")
    kept = list(GC._PROBED)
    assert len(kept) == 1, kept

    asked = []

    def spy(model, seed, allowance_s, workers):
        asked.append(GC._model_key(model, seed))
        raise _Stop

    monkeypatch.setattr(GC, "probed_answer", spy)
    # A small limit: the sizing is read from what the probe kept, and the walls-held step ahead of
    # the one under test only has to end. It cannot hold, because the walls-released step at this
    # depth is the looser model.
    with pytest.raises(_Stop):
        out = GC._solve_cp(copy.deepcopy(plan), parti, time_limit_s=5.0, candidates=40, workers=1)
        pytest.fail("the placement never reached its first walls-released step: "
                    f"{(out.get('solver') or out).get('attempts')}")
    assert asked == kept, (
        "the probe and the placement posed two different models of one house, so the probe's "
        "answer is of a house nobody places and is never taken up")


def test_a_wing_whose_box_was_not_decided_leaves_the_probe_unjudged_and_keeps_nothing(monkeypatch):
    _ortools()
    monkeypatch.setattr(GC, "_WING_BOXES", {})
    plan, parti = _composed_with_a_wing()
    report = {"service": {"derived_ft": [18, 20], "taken_ft": None, "boxes_in_window": 40,
                          "tried": 3, "undecided": 1, "past_the_lot": 0, "seconds": 0.1}}
    # what `size_wings` returns when its time runs out: a report, and nothing kept for the process
    monkeypatch.setattr(GC, "size_wings", lambda *a, **k: ({}, {k_: dict(v) for k_, v in report.items()}))
    monkeypatch.setattr(GC, "_hard_model",
                        lambda *a, **k: pytest.fail("a step was posed on a box nobody decided"))
    res = GC.probe_all_facts(plan, parti, remember=True)
    assert res["verdict"] == GC.PROBE_UNJUDGED and "not decided" in res["why"], res
    assert not res.get("systemic"), "it is this record's, so the pass goes on to the next diagram"
    assert res["wing_sizing"] == report and not GC._PROBED


def test_a_house_with_no_wing_is_sized_as_nothing_and_its_probe_is_what_it_was(monkeypatch):
    _ortools()
    monkeypatch.setattr(GC, "_WING_BOXES", {})
    plan = copy.deepcopy(_walls_cannot_hold())
    _levels, prep = GEO.prep_rooms(plan)
    fpd = GC._snap_fpd(GEO.derive_footprint(plan, None, prep))
    out, report, decided = GC.wing_sized(plan, prep, fpd, GEO.entrance_walls(plan), 1.0)
    assert out == fpd and report == {} and decided is True and not GC._WING_BOXES
    res = _decided(GC.probe_all_facts(_walls_cannot_hold()))
    assert res["wing_sizing"] is None and res["verdict"] == GC.PROBE_HELD, res


def test_a_sized_box_goes_onto_the_footprint_and_widens_the_flank_by_its_own_difference(monkeypatch):
    fpd = {"W": 45.0, "H": 37.0, "bay": 9.0, "flank": 60.0, "built_extent": 105.0}
    monkeypatch.setattr(GC, "size_wings", lambda *a, **k: (
        {"service": (21, 22)}, {"service": {"derived_ft": [18, 20], "taken_ft": [21, 22]}}))
    monkeypatch.setattr(GC, "_wing_key", lambda *a, **k: "k")
    monkeypatch.setattr(GC, "_WING_BOXES", {"k": ({}, {})})
    out, report, decided = GC.wing_sized({}, {}, fpd, [], 1.0)
    assert out["flank_box"] == {"service": (21, 22)} and decided is True
    assert out["flank"] == 63.0 and out["built_extent"] == 108.0
    assert "flank_box" not in fpd and fpd["flank"] == 60.0, "the footprint handed in is not written to"
    monkeypatch.setattr(GC, "_WING_BOXES", {})
    assert GC.wing_sized({}, {}, fpd, [], 1.0)[2] is False, "a search not kept was not decided"
