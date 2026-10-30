"""WP-17.5: the prover can decide. Assumption literals force CP-SAT onto one sequential worker, and
on the composed two-storey houses a fact-holding placement that four workers find in seconds was
never reached on one. Every fact is posed HARD on a worker portfolio first; the assumption ladder
runs only where that does not decide, for its conflict cores.

These hold the worker count the portfolio reads, its override, and that one solve at a time takes
it -- two portfolio solves on one box would each take every core and both lose.
"""
import importlib.util
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("geometry_cp_pf", ROOT / "build" / "geometry_cp.py")
GC = importlib.util.module_from_spec(spec)
spec.loader.exec_module(GC)


def test_the_override_wins_and_is_floored_at_one(monkeypatch):
    monkeypatch.setenv("TDL_CP_WORKERS", "3")
    assert GC.portfolio_workers() == 3
    monkeypatch.setenv("TDL_CP_WORKERS", "0")
    assert GC.portfolio_workers() == 1, "an override of 0 is one worker, never none"
    monkeypatch.setenv("TDL_CP_WORKERS", "not-a-number")
    assert 1 <= GC.portfolio_workers() <= GC.PORTFOLIO_MAX_WORKERS


def test_the_cgroup_quota_bounds_the_workers_and_not_the_hosts_cores(monkeypatch, tmp_path):
    monkeypatch.delenv("TDL_CP_WORKERS", raising=False)
    import builtins
    real_open = builtins.open
    quota = tmp_path / "cpu.max"

    def fake_open(path, *a, **k):
        if str(path) == "/sys/fs/cgroup/cpu.max":
            return real_open(quota, *a, **k)
        return real_open(path, *a, **k)
    monkeypatch.setattr(builtins, "open", fake_open)
    monkeypatch.setattr(GC.os, "sched_getaffinity", lambda _pid: set(range(16)))
    quota.write_text("200000 100000\n")
    assert GC.portfolio_workers() == 2, "a 2-CPU quota on a 16-core host is two workers"
    quota.write_text("150000 100000\n")
    assert GC.portfolio_workers() == 2, "a fractional quota rounds up"
    quota.write_text("max 100000\n")
    assert GC.portfolio_workers() == min(16, GC.PORTFOLIO_MAX_WORKERS), "no quota: the affinity, capped"


def test_one_solve_holds_the_portfolio_and_a_concurrent_one_runs_on_one_worker(monkeypatch):
    seen = []
    monkeypatch.setattr(GC, "portfolio_workers", lambda: 4)
    monkeypatch.setattr(GC, "_solve_cp", lambda *a, workers=1, **k: seen.append(workers) or {"ok": workers})
    assert GC.solve_cp({}, None) == {"ok": 4}
    assert GC._PORTFOLIO_LOCK.acquire(blocking=False)
    try:
        assert GC.solve_cp({}, None) == {"ok": 1}, "the lock is held: this solve takes one worker"
    finally:
        GC._PORTFOLIO_LOCK.release()
    assert seen == [4, 1]
    monkeypatch.setattr(GC, "portfolio_workers", lambda: 1)
    assert GC.solve_cp({}, None) == {"ok": 1}


def test_a_v1_cgroup_quota_bounds_the_workers_too(tmp_path, monkeypatch):
    """The audit of Phase 17 (30 Oct 2026, finding 13): only cgroup v2's `cpu.max` was read, and
    this box is cgroup v1, so a v1 quota would have been ignored and the host's affinity used."""
    monkeypatch.delenv("TDL_CP_WORKERS", raising=False)
    monkeypatch.setattr(GC.os, "sched_getaffinity", lambda _pid: set(range(16)))
    cpu = tmp_path / "cpu"
    cpu.mkdir()
    (cpu / "cpu.cfs_period_us").write_text("100000\n")
    (cpu / "cpu.cfs_quota_us").write_text("200000\n")
    assert GC.portfolio_workers(_cgroup_root=str(tmp_path)) == 2, "a 2-CPU v1 quota on 16 cores"
    (cpu / "cpu.cfs_quota_us").write_text("150000\n")
    assert GC.portfolio_workers(_cgroup_root=str(tmp_path)) == 2, "a fractional v1 quota rounds up"
    (cpu / "cpu.cfs_quota_us").write_text("-1\n")
    assert GC.portfolio_workers(_cgroup_root=str(tmp_path)) == min(16, GC.PORTFOLIO_MAX_WORKERS), (
        "a v1 quota of -1 is no quota: the affinity, capped")
    (tmp_path / "cpu.max").write_text("100000 100000\n")
    assert GC.portfolio_workers(_cgroup_root=str(tmp_path)) == 1, "where v2 states one, v2 decides"


# --------------------------------------------------- what the record says the solve ran on
# REPLACES A TEST THAT READ SOURCE TOKENS (the audit of Phase 17, 30 Oct 2026, findings 13 and 38).
# `test_the_solver_report_names_the_portfolio_and_its_workers` asserted three literals appear in
# `_solve_cp`'s source -- among them `_harden(m_, q_)` -- so `if workers > 1:` changed to
# `if workers > 99:` (the portfolio never runs) left this file green, and so did a `_harden` reduced
# to `ClearAssumptions()`, which would have had the portfolio solve a model with NO type facts and
# write "every type fact HELD". Both were reproduced before the fix. What replaces it reads the
# record a solve writes and the model `_harden` leaves.

def _two_storey():
    """`geometry_cp._feasible_fixture` with an upper floor that stacks over the ground, a massing
    putting its flues on the gable ends and one stated fire -- `tests/test_type_facts_hard.py`'s
    fixture, small enough to place in seconds on one worker or four."""
    p = GC._feasible_fixture()
    p["massing"] = "four-over-four"
    p["levels"][0]["rooms"][2]["hearth"] = [{"wall": "W", "width_in": 40.0}]
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


def _placed(res, workers):
    if "error" in res or res.get("unsolved") or res.get("infeasible"):
        pytest.skip(f"COULD NOT EVALUATE: the fixture did not place on {workers} worker(s) on this "
                    f"machine ({res.get('status') or res.get('error') or 'infeasible'})")
    return res["solver"]


def test_the_record_names_the_workers_the_mode_and_the_portfolio_ran(monkeypatch):
    pytest.importorskip("ortools", reason="COULD NOT EVALUATE: the CP-SAT engine needs OR-Tools")
    monkeypatch.setattr(GC, "portfolio_workers", lambda *a, **k: 4)
    sv = _placed(GC.solve_cp(_two_storey(), None, time_limit_s=40, candidates=80), 4)
    assert (sv["workers"], sv["workers_available"]) == (4, 4), sv
    assert sv["mode"] in GC.MODES
    assert any(t.startswith("H:") for _tag, t in sv["attempts"]), (
        "four workers and no hard portfolio step: the portfolio did not run", sv["attempts"])
    rounds = sv["downgrade_rounds"]
    assert rounds and rounds[0].startswith("portfolio (4 workers): "), rounds
    if sv["mode"] == "portfolio":
        assert "every type fact HELD" in rounds[0], rounds[0]


def test_a_solve_on_one_worker_of_four_says_so(monkeypatch):
    """A solve that found the portfolio lock held (a compose job on the same box) runs the ladder on
    one worker, and the record says it had four available -- the trace finding 36's cache reads."""
    pytest.importorskip("ortools", reason="COULD NOT EVALUATE: the CP-SAT engine needs OR-Tools")
    monkeypatch.setattr(GC, "portfolio_workers", lambda *a, **k: 4)
    assert GC._PORTFOLIO_LOCK.acquire(blocking=False), "premise: no other solve holds the lock"
    try:
        sv = _placed(GC.solve_cp(_two_storey(), None, time_limit_s=40, candidates=80), 1)
    finally:
        GC._PORTFOLIO_LOCK.release()
    assert (sv["workers"], sv["workers_available"], sv["mode"]) == (1, 4, "ladder"), sv
    assert not any(t.startswith("H:") for _tag, t in sv["attempts"]), sv["attempts"]
    assert not any(r.startswith("portfolio (") for r in sv["downgrade_rounds"])


def test_harden_poses_every_fact_as_a_hard_clause_and_the_solver_reads_it_so():
    """Deterministic and on any core count: the model `_build` returns poses the type's facts as
    ASSUMPTIONS; `_harden` must clear them and state each as a one-literal clause, so lifting any
    one fact makes the model INFEASIBLE at once. The end-to-end fixture in test_type_facts_hard
    catches a no-op `_harden` only where the portfolio runs (four quiet cores); this does not care."""
    pytest.importorskip("ortools", reason="COULD NOT EVALUATE: the CP-SAT engine needs OR-Tools")
    from ortools.sat.python import cp_model
    plan = _two_storey()
    _levels, prep = GC.GEO.prep_rooms(plan)
    fpd = GC._snap_fpd(GC.GEO.derive_footprint(plan, None, prep))
    m, _rooms, reqs = GC._build(plan, prep, fpd, GC.GEO.entrance_walls(plan), frozenset(),
                                objective=False)
    lits = [lit for lit, _t, _k, _key in reqs.lits]
    kinds = {k for _l, _t, k, _key in reqs.lits}
    assert len(lits) >= 8 and {"tiling", "stack", "bearing", "hearth"} <= kinds, kinds
    assert sorted(m.Proto().assumptions) == sorted(l.Index() for l in lits), (
        "premise: the built model poses every fact as an assumption")
    GC._harden(m, reqs)
    proto = m.Proto()
    assert not list(proto.assumptions), "a hardened model still carries assumptions"
    def _is_clause(c):        # this build's proto helper spells it has_bool_or; protobuf, HasField
        has = getattr(c, "has_bool_or", None)
        return has() if callable(has) else c.HasField("bool_or")
    forced = {c.bool_or.literals[0] for c in proto.constraints
              if _is_clause(c) and len(c.bool_or.literals) == 1 and not list(c.enforcement_literal)}
    missing = [t for lit, t, _k, _key in reqs.lits if lit.Index() not in forced]
    assert not missing, f"{len(missing)} fact(s) not posed hard: {missing[:3]}"
    for kind in ("stack", "bearing"):
        one = next(lit for lit, _t, k, _key in reqs.lits if k == kind)
        trial = m.Clone()
        trial.Add(trial.GetBoolVarFromProtoIndex(one.Index()) == 0)
        s = cp_model.CpSolver()
        s.parameters.max_time_in_seconds = 20
        s.parameters.num_search_workers = 1
        assert s.Solve(trial) == cp_model.INFEASIBLE, f"a lifted {kind} fact is not forced"


# ------------------------------------------- the reinstatement pass and what it says it did
def test_the_reinstatement_deadline_is_its_share_and_never_the_polishs():
    """Held as a pure function and DELIBERATELY NOT RE-ANCHORED (R12 of 30 Oct 2026, as the audit-fix task records it:
    the pass gets no share of its own). After an undecided portfolio, which runs to 0.75 of the
    budget, the cap of 0.6 is already behind the pass and the deadline is in the past -- finding 9,
    disclosed by the pass's own line rather than re-anchored."""
    T, t0 = 40.0, 1000.0
    share = GC.GEO.BUDGET_SHARE_REINSTATE * T
    cap = t0 + (1.0 - GC.GEO.BUDGET_SHARE_POLISH) * T
    assert GC._reinstate_deadline(t0 + 1.0, t0, T) == min(t0 + 1.0 + share, cap)
    assert GC._reinstate_deadline(t0 + 20.0, t0, T) == cap, "the polish's share is never spent"
    after_portfolio = t0 + GC.BUDGET_SHARE_PORTFOLIO * T + 1.0
    assert GC._reinstate_deadline(after_portfolio, t0, T) < after_portfolio, (
        "the measured state finding 9 discloses: no time is left after an undecided portfolio")


def test_the_reinstatement_line_counts_what_it_reached_and_what_it_never_did():
    pend = [("stack", 1, "a"), ("stack", 1, "b"), ("wall", 0, "x", "N")]
    line = GC._reinstate_note(pend, offered=set(), still_down=set(pend), refuted=set(),
                              began_s=31.0, window_s=-7.0, time_limit_s=40)
    assert line.startswith(GC.REINSTATE_NOTE_PREFIX)
    assert "offered back 0 of 3" in line and "3 never reached" in line, line
    assert "no time left" in line and "CARRIED" in line and "0.0 s left" in line, line
    line = GC._reinstate_note(pend, offered=set(pend), still_down={pend[1], pend[2]},
                              refuted={pend[2]}, began_s=1.0, window_s=6.0, time_limit_s=40)
    assert "offered back 3 of 3 (1 restored, 1 refuted alone, 1 still carried)" in line, line
    assert "never reached" not in line, line


def test_a_pass_with_no_time_left_says_so_on_the_record(monkeypatch):
    """The disclosure, end to end on one worker: with the pass's window already behind it (the
    polish's guaranteed share set to the whole budget, so the cap is the start), nothing is offered
    back, the record's own line says every released pin was never reached, and the facts account
    files each downgraded fact CARRIED. The rank notes that used to assert the act do not."""
    pytest.importorskip("ortools", reason="COULD NOT EVALUATE: the CP-SAT engine needs OR-Tools")
    monkeypatch.setattr(GC, "portfolio_workers", lambda *a, **k: 1)
    monkeypatch.setattr(GC.GEO, "BUDGET_SHARE_POLISH", 1.0)
    sv = _placed(GC.solve_cp(_two_storey(), None, time_limit_s=40, candidates=80), 1)
    assert not [a for a in sv["attempts"] if a[1].startswith("R:")], "the pass ran a restore"
    lines = [r for r in sv["downgrade_rounds"] if r.startswith(GC.REINSTATE_NOTE_PREFIX)]
    assert len(lines) == 1, sv["downgrade_rounds"]
    released = sum(1 for k in ("downgraded_wall_pins", "downgraded_shape_pins", "downgraded_axis_pins")
                   for _ in sv[k]) + sum(len(f["downgraded"]) for f in sv["facts"].values())
    assert released and f"offered back 0 of {released}" in lines[0], (released, lines[0])
    assert f"{released} never reached" in lines[0], lines[0]
    assert not any("offered back one at a time by the reinstatement pass" in r
                   or "offered back highest rank first by the reinstatement pass" in r
                   for r in sv["downgrade_rounds"]), "a round line asserts the pass's act for it"
    down = {k: f for k, f in sv["facts"].items() if f["downgraded"]}
    assert down, "premise: the ladder released a type fact on this fixture"
    for kind, f in down.items():
        assert f["carried"] == f["downgraded"] and f["proven"] == [], (kind, f)


def test_the_facts_account_files_each_downgraded_label_proven_or_carried():
    """Finding 14's structural half: `drawability._class_of` read the proof status off prose with
    `any(phrase in note and kind in note)` -- one proven bearing axis made a fact with a carried axis
    PROVEN, and a proven hearth release (whose note never says "hearth") read UNDECIDED. The account
    carries the split now, from the same `unproven` set the notes are written from."""
    from types import SimpleNamespace
    reqs = SimpleNamespace(lits=[(None, "t", "bearing", (0, "x")), (None, "t", "bearing", (0, "y")),
                                 (None, "t", "hearth", (0, "parlor", "W"))], unjudged=[])
    down = {GC._dk("bearing", (0, "x")), GC._dk("bearing", (0, "y")),
            GC._dk("hearth", (0, "parlor", "W"))}
    acc = GC.facts_account(reqs, down, unproven={GC._dk("bearing", (0, "y"))})
    b, h = acc["bearing"], acc["hearth"]
    assert b["downgraded"] == ["element 0 x", "element 0 y"]
    assert (b["proven"], b["carried"]) == (["element 0 x"], ["element 0 y"]), b
    assert (h["proven"], h["carried"]) == (["L0 parlor W"], []), h
    assert sorted(b["proven"] + b["carried"]) == b["downgraded"]
    assert acc["tiling"] == {"held": [], "downgraded": [], "unjudged": [], "status": "unjudged",
                             "proven": [], "carried": []}


def test_a_wing_grows_with_the_house_and_stays_centred():
    """Ruling 4's third part with decision 11: where the prover grows the main block's depth before
    compromising a room, each dependency grows by the same even step, never past the main block,
    and stays exactly centred. Without it the composed centre passage's wing held 306 sf of rooms in
    an 18 x 17 ft box at every depth the prover tried."""
    import sys
    sys.path.insert(0, str(ROOT / "build"))
    import modcache
    CO = modcache.load("compose", str(ROOT / "build" / "compose.py"))
    G = modcache.load("geometry", str(ROOT / "build" / "geometry.py"))
    brief = {"id": "t", "style": "tidewater-georgian", "target_area_sf": 3200, "bedrooms": 4}
    plan, _log, p = CO.instantiate("centre-passage-double-pile", brief)
    _levels, prep = G.prep_rooms(plan)
    fpd = GC._snap_fpd(G.derive_footprint(plan, p, prep))
    base = {e["id"]: e for e in G.blocks_for(plan, fpd, prep, 0)}
    deps = [k for k, e in base.items() if e["role"] == "dependency"]
    assert deps, "the premise: the composed double pile has a service wing"
    grown = {e["id"]: e for e in G.blocks_for(plan, dict(fpd, H=fpd["H"] + 4, flank_grow_ft=4), prep, 0)}
    for k in deps:
        assert grown[k]["H"] == min(base[k]["H"] + 4, fpd["H"] + 4), (base[k], grown[k])
        assert grown[k]["y"] == (fpd["H"] + 4 - grown[k]["H"]) / 2, "exactly centred on the grown block"
    capped = {e["id"]: e for e in G.blocks_for(plan, dict(fpd, H=fpd["H"] + 2, flank_grow_ft=200), prep, 0)}
    assert all(capped[k]["H"] <= fpd["H"] + 2 for k in deps), "never deeper than the main block"
