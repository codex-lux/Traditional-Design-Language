"""WP-9.2 — the revision loop. Every test is named for the finding it protects.

compose.repair had no rollback: on a non-improving round the record was already mutated and the
WORSE result was accepted. build/revise.py rolls a refused round back byte-identically, marks the
(move, finding) pairs tabu, and continues -- and it stops for a stated reason, never because it
gave up quietly.
"""
import copy
import json
import os
import sys

import pytest

from conftest import load_plan, minimal_plan

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
if BUILD not in sys.path:
    sys.path.insert(0, BUILD)
import modcache as mc  # noqa: E402

RV = mc.load("revise", os.path.join(BUILD, "revise.py"))
MV = mc.load("moves", os.path.join(BUILD, "moves.py"))
OP = mc.load("openings", os.path.join(BUILD, "openings.py"))
GEO = mc.load("geometry", os.path.join(BUILD, "geometry.py"))
EX = mc.load("export_dxf", os.path.join(BUILD, "export_dxf.py"))

FAST = dict(engine="heuristic", candidates=120)


def _declared(plan):
    p = copy.deepcopy(plan)
    p.pop("revision_report", None)
    return json.dumps(OP.strip_placement(p), sort_keys=True)


class TestAcceptanceAndRollback:
    def test_a_round_that_does_not_strictly_improve_is_rolled_back_byte_identically(self, monkeypatch):
        """Drop the deepcopy snapshot in build/revise.py and this fails: a refused move's edit
        survives in the returned record."""
        monkeypatch.setattr(RV, "_improves", lambda new, old: False)
        plan = load_plan("tidewater-georgian-careful")
        r = RV.revise(plan, rounds=2, **FAST)
        assert _declared(r["plan"]) == _declared(plan)
        assert all(not rd["accepted"] for rd in r["rounds"])
        assert r["key_after"] == r["key_before"]

    def test_a_refused_pair_is_tabu_and_the_loop_continues(self, monkeypatch):
        monkeypatch.setattr(RV, "_improves", lambda new, old: False)
        r = RV.revise(load_plan("tidewater-georgian-careful"), rounds=4, **FAST)
        seen = []
        for rd in r["rounds"]:
            for m in rd["moves"]:
                if m.get("finding"):
                    pair = (m["move"], m["finding"])
                    assert pair not in seen, f"{pair} was tried twice"
                    seen.append(pair)
        assert len(r["rounds"]) >= 2, "the loop stopped on the first refused round"
        # every declared move is refused and every lever is refused or spent, so the loop
        # runs out of things to try before the cap: one reason, not a disjunction (WP-9.4)
        assert r["stop_reason"] == ("round-cap" if len(r["rounds"]) == 4 else "no-applicable-move"), \
            (r["stop_reason"], len(r["rounds"]))

    def test_the_budget_stops_the_loop_and_keeps_the_accepted_state(self):
        plan = load_plan("tidewater-georgian-careful")
        r = RV.revise(plan, rounds=6, budget_s=0.0, **FAST)
        assert r["stop_reason"] == "budget"
        assert r["rounds"] == []
        assert _declared(r["plan"]) == _declared(plan)
        assert r["plan"]["revision_report"]["summary"]["stop_reason"] == "budget"

    def test_a_repeated_declared_hash_stops_as_oscillation(self, monkeypatch):
        monkeypatch.setattr(RV, "_hash", lambda plan: "same")
        r = RV.revise(load_plan("tidewater-georgian-careful"), rounds=6, **FAST)
        if not any(rd["accepted"] for rd in r["rounds"]):
            pytest.skip("COULD NOT EVALUATE — no round was accepted on this engine, so no hash was revisited")
        assert r["stop_reason"] == "oscillation"

    def test_attribution_uses_stable_ids_and_sums(self):
        r = RV.revise(load_plan("tidewater-georgian-careful"), rounds=3, **FAST)
        acc = [rd for rd in r["rounds"] if rd["accepted"]]
        if not acc:
            pytest.skip("COULD NOT EVALUATE — no accepted round on this engine")
        for rd in acc:
            assert set(rd["cleared"]).isdisjoint(rd["persisted"])
            assert set(rd["opened"]).isdisjoint(rd["persisted"])
            assert set(rd["cleared"]).isdisjoint(rd["opened"])
            assert all(isinstance(i, str) and i for i in rd["cleared"] + rd["opened"] + rd["persisted"])
            # the sums: what was there is cleared or persisted; what is there persisted or opened
            before = {f["id"] for f in r["critique_before"]["check"]["findings"]
                      if f["severity"] not in ("info", "advisory")} if rd["n"] == 1 else None
            if before is not None:
                assert set(rd["cleared"]) | set(rd["persisted"]) == before

    def test_a_move_that_opens_a_fatal_is_refused(self):
        RV_ = RV
        before = {"key": [0, 10, 5, 2], "check": {"findings": [{"id": "a", "severity": "serious"}]}}
        after = {"key": [0, 9, 5, 2], "check": {"findings": [{"id": "drawn:x", "severity": "fatal"}]}}
        assert not RV_._improves(after, before), "a better key with a NEW fatal was accepted"
        after2 = {"key": [0, 9, 5, 2], "check": {"findings": []}}
        assert RV_._improves(after2, before)
        equal = {"key": [0, 10, 5, 2], "check": {"findings": []}}
        assert not RV_._improves(equal, before), "an equal key is a trade, not an improvement"


class TestWhatTheLoopTouches:
    def test_the_strip_list_is_the_exporters_list_and_a_window_keeps_its_wall(self):
        assert EX._SOLVED_DOOR_KEYS is OP.PLACEMENT_DOOR_KEYS
        assert EX._SOLVED_WINDOW_KEYS is OP.PLACEMENT_WINDOW_KEYS
        assert "wall" not in OP.PLACEMENT_WINDOW_KEYS and "wall" in OP.PLACEMENT_DOOR_KEYS

    def test_revise_never_mutates_its_argument(self):
        plan = load_plan("spec-builder-colonial")
        before = json.dumps(plan, sort_keys=True)
        RV.revise(plan, rounds=1, **FAST)
        assert json.dumps(plan, sort_keys=True) == before

    def test_the_revised_plan_validates_against_schema_0_4_0(self):
        import jsonschema
        r = RV.revise(load_plan("tidewater-georgian-careful"), rounds=2, **FAST)
        schema = json.load(open(os.path.join(ROOT, "schema", "plan.schema.json")))
        assert schema["version"] == "0.4.0"
        jsonschema.validate(r["plan"], schema)
        assert r["plan"]["revision_report"]["schema"] == "0.4.0"

    def test_a_re_derive_move_keeps_the_placement_and_a_re_place_move_strips_it(self, monkeypatch):
        """Count the solves. A round whose only move touches the elevation's inputs must not
        re-solve the placement; a round that moves a wall must."""
        calls = []
        real = GEO.solve

        def counting(*a, **k):
            calls.append(k.get("engine") or (a[4] if len(a) > 4 else None))
            return real(*a, **k)
        monkeypatch.setattr(GEO, "solve", counting)
        plan = load_plan("tidewater-georgian-careful")

        def only_rederive(mid, p, f, C=None, ctx=None):
            if mid == "prove-it" or mid == "search-harder":
                return {"refused": "not in this test"}
            r = next(rm for lv in p["levels"] for rm in lv["rooms"] if rm["id"] == f.get("room")) if f.get("room") else None
            if r is None:
                return {"refused": "no room"}
            return {"changed": [], "log": "no-op", "requires": "re-derive", "move": mid,
                    "basis": "test", "authority": "declared", "kind": "measured"}
        monkeypatch.setattr(MV, "apply", only_rederive)
        # rounds=2: round 1 is the proof asked first and refused here, round 2 the declared
        # move. The first version ran ONE round, which was the refused lever, and its "1 solve"
        # was the initial critique -- no re-derive move was ever applied (WP-9.4)
        r = RV.revise(plan, rounds=2, **FAST)
        assert any(m.get("cleared") is not None or m.get("refused_by_measurement") for rd in r["rounds"] for m in rd["moves"]
                   if m["move"] not in ("prove-it", "search-harder")), "a declared move was applied"
        assert len(calls) == 1, f"a re-derive-only round re-solved the placement ({len(calls)} solves)"
        # ... and the other direction, which the first version never asserted: delete the
        # `if replace: strip_placement` and this half goes red (WP-9.4)
        calls.clear()

        def only_replace(mid, p, f, C=None, ctx=None):
            if mid in ("prove-it", "search-harder"):
                return {"refused": "not in this test"}
            return {"changed": [], "log": "no-op", "requires": "re-place", "move": mid,
                    "basis": "test", "authority": "dimensions", "kind": "measured"}
        monkeypatch.setattr(MV, "apply", only_replace)
        r = RV.revise(plan, rounds=2, **FAST)
        assert any(m["move"] not in ("prove-it", "search-harder") and "refused" not in m
                   for rd in r["rounds"] for m in rd["moves"]), "a declared move was applied"
        assert len(calls) >= 2, f"a re-place round must solve again ({len(calls)} solves)"

    @pytest.mark.parametrize("pid", ["tidewater-georgian-careful", "spec-builder-colonial"])
    def test_revise_on_both_shipped_plans_never_opens_a_fatal(self, pid):
        r = RV.revise(load_plan(pid), rounds=3, **FAST)
        assert r["key_after"][0] <= r["key_before"][0]
        fatal_after = {f["id"] for f in r["critique_after"]["check"]["findings"] if f["severity"] == "fatal"}
        fatal_before = {f["id"] for f in r["critique_before"]["check"]["findings"] if f["severity"] == "fatal"}
        assert fatal_after <= fatal_before

    def test_the_report_states_what_remains_by_class_and_what_was_refused(self):
        r = RV.revise(load_plan("tidewater-georgian-careful"), rounds=2, **FAST)
        rep = r["plan"]["revision_report"]
        assert set(rep["remaining"]) == {"actionable", "placement", "critic_suspect", "architect", "advisory"}
        assert rep["suspects"] and all(i["evidence"] for i in rep["suspects"])
        assert all(h.get("why") for h in rep["handed_to_architect"])
        assert rep["stop_reason"] and rep["summary"]["rounds"] == len(rep["rounds"])
        for m in rep["refused"]:
            assert m.get("refused") or m.get("refused_by_measurement")

    def test_two_calls_at_one_seed_are_equal(self):
        plan = load_plan("tidewater-georgian-careful")
        a = RV.revise(plan, rounds=2, **FAST)
        b = RV.revise(plan, rounds=2, **FAST)
        for k in ("key_before", "key_after", "stop_reason"):
            assert a[k] == b[k]
        assert [[m["move"] for m in rd["moves"]] for rd in a["rounds"]] == \
               [[m["move"] for m in rd["moves"]] for rd in b["rounds"]]


class TestTheSweep:
    def test_the_sweep_runs_on_one_parti_and_reports_before_and_after(self):
        res = RV.sweep(engine="heuristic", rounds=1, candidates=120, partis=["hall-and-parlor"])
        rows = [r for r in res["plans"] if "error" not in r]
        assert len(rows) == 3, res["plans"]           # one parti + both shipped plans
        for row in rows:
            assert len(row["key_before"]) == 4 and len(row["key_after"]) == 4
        assert isinstance(res["never_fired"], list)


class TestTheReclaimAfterTheLoop:
    def test_a_reclaim_that_opens_a_fatal_is_rolled_back_and_said(self, monkeypatch):
        """The sweep's first run handed back tower-villa at [3, 36, 46, 0] -> [4, 23, 49, 0]:
        every round had refused a new fatal and the reclaim after the last round re-placed the
        house and opened one. The area discipline does not outrank the rule the rounds were
        held to. Mutation: drop the `kept` restore in revise.py and this reads rolled_back with
        the fatal still in the returned plan."""
        CO = mc.load("compose", os.path.join(BUILD, "compose.py"))
        plan = load_plan("spec-builder-colonial")
        brief = {"target_area_sf": 100, "area_tolerance": 0.0}     # an impossible target: reclaim runs

        def wrecking_reclaim(p, target, tol, res):
            # a reclaim that takes every interior door with it -- what a fatal-opening
            # reclaim looks like at its most legible
            for lv in p["levels"]:
                for r in lv["rooms"]:
                    r["doors"] = [d for d in r.get("doors", []) if d.get("to") == "outside"]
            return res, ["RECLAIMED: every door, to make the point"]
        monkeypatch.setattr(CO, "reclaim", wrecking_reclaim)
        r = RV.revise(plan, rounds=1, brief=brief, place=True, **FAST)
        rec = r["report"]["reclaimed"]
        assert rec and rec["rolled_back"] is True and "opened a fatal" in rec["why"]
        assert rec["key_after"][0] > rec["key_before"][0]
        # the returned plan is the accepted state, doors and all, and the key is its key
        assert any(d.get("to") != "outside"
                   for lv in r["plan"]["levels"] for rm in lv["rooms"] for d in rm.get("doors", []))
        assert r["key_after"] == rec["key_before"]


class TestTheRoundCallback:
    def test_on_round_fires_once_for_every_logged_round_including_a_refused_lever(self):
        """WP-9.3's revise job emitted no `round` event on a plan whose only round was a
        refused proof: two of the four paths that log a round skipped the callback. The
        bench watches the loop through this callback, so a round it does not hear about is
        a round that did not happen to the reader. Mutation: make any path append to the
        log without reporting and the counts differ."""
        seen = []
        r = RV.revise(load_plan("tidewater-georgian-careful"), rounds=2, place=True,
                      on_round=lambda rnd: seen.append(rnd["n"]), **FAST)
        assert len(seen) == len(r["rounds"]) == r["report"]["summary"]["rounds"]
        assert seen == [rd["n"] for rd in r["rounds"]]
        # the explicit search refuses the proof, and THAT round is reported too
        assert any(m.get("move") == "prove-it" and m.get("refused")
                   for rd in r["rounds"] for m in rd["moves"])


class TestWhatTheAuditFound:
    """WP-9.4. Each test is named for the defect the audit reproduced by mutation."""

    @staticmethod
    def _fake_critique(monkeypatch, engines, keys, lever):
        """A critique the loop cannot tell from the real one, scripted: `engines[i]` and
        `keys[i]` are what the i-th call reports, and the assessment offers one actionable
        move (refused by apply, so it goes tabu) and one placement item whose lever is
        `lever`. No solver runs; what is under test is the loop's own bookkeeping."""
        calls = {"n": 0}

        def fake(plan, **kw):
            i = min(calls["n"], len(keys) - 1)
            calls["n"] += 1
            return {"plan": plan, "key": list(keys[i]),
                    "engine": {"requested": kw.get("engine"), "ran": engines[i], "reason": None},
                    "check": {"findings": []}, "placement": {"reused": False},
                    "assessment": {"actionable": [{"id": "furniture:x", "severity": "serious", "room": "x",
                                                   "statement": "scripted", "moves": ["widen-for-furniture"],
                                                   "finding": {"id": "furniture:x"}}],
                                   "placement": [{"id": "drawn:y", "severity": "fatal", "move": lever,
                                                  "statement": "scripted", "finding": {"id": "drawn:y"}}],
                                   "critic_suspect": [], "architect": [], "advisory": []},
                    "counts_by_class": {}, "could_not_evaluate": {"findings": []}}
        monkeypatch.setattr(RV.CR, "critique", fake)
        monkeypatch.setitem(MV.APPLY, "widen-for-furniture", lambda plan, f, C, ctx: {"refused": "scripted"})
        return calls

    def test_a_lever_refused_by_measurement_carries_its_own_verdict_so_the_summary_counts_it(self, monkeypatch):
        """The lever's flags rode on the ROUND and the summary read the MOVE ENTRY: an accepted
        proof counted as 0 moves applied, and a proof rolled back by measurement reached the
        bench as "applied; its finding persisted"."""
        pytest.importorskip("ortools", reason="COULD NOT EVALUATE -- prove-it refuses without CP-SAT importable")
        plan = load_plan("tidewater-georgian-careful")
        self._fake_critique(monkeypatch, engines=["heuristic", "cp-sat"], keys=[[1, 1, 1, 0], [1, 1, 1, 0]],
                            lever="prove-it")
        r = RV.revise(plan, rounds=2, engine="auto", candidates=120, place=True)
        levers = [m for rd in r["rounds"] for m in rd["moves"] if m["move"] == "prove-it"]
        assert levers, [rd["moves"] for rd in r["rounds"]]
        m = levers[0]
        assert m.get("refused_by_measurement") is True and m.get("cleared") is False and "accepted" not in m
        assert m in r["report"]["refused"], "a lever refused by measurement is a refusal the summary counts"
        assert r["report"]["summary"]["moves_refused"] >= 1
        assert r["report"]["summary"]["moves_applied"] == 0

    def test_an_accepted_proof_counts_as_a_move_applied(self, monkeypatch):
        pytest.importorskip("ortools", reason="COULD NOT EVALUATE -- prove-it refuses without CP-SAT importable")
        plan = load_plan("tidewater-georgian-careful")
        self._fake_critique(monkeypatch, engines=["heuristic", "cp-sat"], keys=[[3, 1, 1, 0], [0, 1, 1, 0]],
                            lever="prove-it")
        r = RV.revise(plan, rounds=2, engine="auto", candidates=120, place=True)
        acc = [m for rd in r["rounds"] for m in rd["moves"] if m["move"] == "prove-it" and m.get("accepted")]
        assert acc, [rd["moves"] for rd in r["rounds"]]
        assert acc[0]["cleared"] is True
        assert r["report"]["summary"]["moves_applied"] == 1
        # the proof is asked for FIRST, before any declared move, so there is no tabu yet to
        # forget; what changed is the engine, and the round says so
        rd = next(rd for rd in r["rounds"] if any(m is acc[0] for m in rd["moves"]))
        assert rd["n"] == 1 and rd["engine_after"] == "cp-sat" and "tabu_forgotten" not in rd

    def test_the_tabu_is_forgotten_only_when_the_engine_changes(self, monkeypatch):
        """`search-harder` changes the candidate count and not the engine; a refusal under 250
        candidates says the same thing under 1,000. The first version wiped the tabu on ANY
        accepted lever."""
        plan = load_plan("tidewater-georgian-careful")
        self._fake_critique(monkeypatch, engines=["heuristic", "heuristic", "heuristic"],
                            keys=[[3, 1, 1, 0], [2, 1, 1, 0], [2, 1, 1, 0]], lever="search-harder")
        r = RV.revise(plan, rounds=3, engine="heuristic", candidates=250, place=True)
        acc = [(rd, m) for rd in r["rounds"] for m in rd["moves"] if m["move"] == "search-harder" and m.get("accepted")]
        assert acc, [rd["moves"] for rd in r["rounds"]]
        rd, m = acc[0]
        assert rd["engine_after"] == rd["engine"] == "heuristic"
        assert "tabu_forgotten" not in rd, "a candidates lever must not forget the search's refusals"
        # and the refused declared move stays tabu: no later round retries it
        later = [mm["move"] for r2 in r["rounds"] if r2["n"] > rd["n"] for mm in r2["moves"]]
        assert "widen-for-furniture" not in later

    def test_before_and_after_are_two_objects_even_when_nothing_is_accepted(self, monkeypatch):
        plan = load_plan("tidewater-georgian-careful")
        monkeypatch.setattr(RV, "_improves", lambda new, old: False)
        r = RV.revise(plan, rounds=1, place=True, **FAST)
        assert r["critique_before"] is not r["critique_after"]
        assert r["critique_before"]["key"] == r["critique_after"]["key"]

    def test_zero_rounds_is_not_a_round_cap(self):
        plan = load_plan("tidewater-georgian-careful")
        r = RV.revise(plan, rounds=0, place=True, **FAST)
        assert r["stop_reason"] == "no-rounds"
        assert r["report"]["summary"]["rounds"] == 0 and r["report"]["summary"]["moves_applied"] == 0

    def test_a_reader_that_raises_does_not_discard_the_loops_work(self):
        plan = load_plan("tidewater-georgian-careful")
        r = RV.revise(plan, rounds=1, place=True, on_round=lambda rnd: 1 / 0, **FAST)
        assert r["rounds"], "the loop ran"
        assert all("ZeroDivisionError" in rd.get("on_round_error", "") for rd in r["rounds"])

    def test_improves_reads_the_whole_key(self):
        """Replace `_improves` with a comparison of the first two axes and the three cases the
        loop shipped with all pass. These do not."""
        mk = lambda key, fatal=(): {"key": list(key), "check": {"findings": [{"id": i, "severity": "fatal"} for i in fatal]}}
        assert RV._improves(mk([3, 44, 69, 19]), mk([3, 44, 70, 19])) is True      # minor only
        assert RV._improves(mk([3, 44, 70, 18]), mk([3, 44, 70, 19])) is True      # faults present only
        assert RV._improves(mk([3, 44, 70, 19]), mk([3, 44, 69, 19])) is False
        assert RV._improves(mk([2, 50, 70, 19], fatal=("new",)), mk([3, 44, 70, 19])) is False  # a new fatal


class TestUnjudgedIsNotBetter:
    """WP-9.4's own CP-SAT measurement found the loop accepting the Tidewater plan at
    [0, 22, 58, 19] with NO placement: a proof timed out, the critique reported the DECLARED
    key -- no drawn finding, so lower -- and _improves took it. Unjudged read as passed, in
    the loop's own acceptance rule."""

    def test_a_round_whose_placement_could_not_be_evaluated_is_never_an_improvement(self, monkeypatch):
        plan = load_plan("tidewater-georgian-careful")
        calls = {"n": 0}

        def fake(p, **kw):
            calls["n"] += 1
            first = calls["n"] == 1
            return {"plan": p, "key": [3, 44, 70, 19] if first else [0, 29, 60, 19],
                    "engine": {"requested": kw.get("engine"), "ran": "heuristic" if first else None, "reason": None},
                    "check": {"findings": []},
                    "placement": {"reused": False, "could_not_evaluate": None if first else "could not solve (UNKNOWN)"},
                    "assessment": {"actionable": [{"id": "furniture:x", "severity": "serious", "room": "x", "statement": "s",
                                                   "moves": ["widen-for-furniture"], "finding": {"id": "furniture:x"}}],
                                   "placement": [], "critic_suspect": [], "architect": [], "advisory": []},
                    "counts_by_class": {}, "could_not_evaluate": {"findings": []}}
        monkeypatch.setattr(RV.CR, "critique", fake)
        monkeypatch.setitem(MV.APPLY, "widen-for-furniture",
                            lambda plan, f, C, ctx: {"changed": [{"path": "levels[].rooms[x].width_ft", "from": 1, "to": 2}],
                                                     "log": "scripted", "requires": "re-place"})
        r = RV.revise(plan, rounds=1, engine="cp", candidates=120, place=True)
        assert r["key_after"] == [3, 44, 70, 19], "the lower DECLARED key of an unplaced record is not an improvement"
        assert not any(rd["accepted"] for rd in r["rounds"])
        assert r["report"]["engine"]["final"] == "heuristic"

    def test_a_first_placement_that_could_not_be_evaluated_stops_the_placed_loop_and_says_so(self, monkeypatch):
        plan = load_plan("tidewater-georgian-careful")

        def fake(p, **kw):
            return {"plan": p, "key": [0, 29, 60, 19], "engine": {"requested": "cp", "ran": None, "reason": None},
                    "check": {"findings": []}, "placement": {"reused": False, "could_not_evaluate": "UNKNOWN at budget"},
                    "assessment": {"actionable": [], "placement": [], "critic_suspect": [], "architect": [], "advisory": []},
                    "counts_by_class": {}, "could_not_evaluate": {"findings": []}}
        monkeypatch.setattr(RV.CR, "critique", fake)
        r = RV.revise(plan, rounds=3, engine="cp", candidates=120, place=True)
        assert r["stop_reason"] == "placement-could-not-be-evaluated"
        assert r["rounds"] == [] and r["report"]["placement_unjudged"] == "UNKNOWN at budget"
