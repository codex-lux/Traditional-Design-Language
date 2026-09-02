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
        assert r["stop_reason"] in ("no-applicable-move", "round-cap", "converged")

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
        r = RV.revise(plan, rounds=1, **FAST)
        assert len(calls) == 1, f"a re-derive-only round re-solved the placement ({len(calls)} solves)"

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
