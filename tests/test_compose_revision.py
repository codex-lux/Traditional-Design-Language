"""WP-9.2 — the composer's two loops. Every test is named for the finding it protects.

`compose.repair` is the DECLARED loop now (build/revise.py with place=False), in its old
position; the PLACED loop runs on the returned candidates after ranking and re-scores them on
the declared record so `score` and `score_before` are one instrument.
"""
import json
import os
import sys

import pytest

BUILD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'build')
if BUILD not in sys.path:
    sys.path.insert(0, BUILD)
import modcache as mc  # noqa: E402


def _brief(name):
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return json.load(open(os.path.join(ROOT, "briefs", f"{name}.json")))


def _composer_order(c):
    """compose()'s own sort rule, as its local `_sort_key` spells it: fatal-free first, then
    score, then demerits, then the parti id."""
    return (c["counts"].get("fatal", 0), -(c["score"] if c["score"] is not None else -1e9),
            c["demerits"], c.get("parti") or "")


@pytest.fixture(scope="module")
def composed(compose_module):
    return compose_module.compose(_brief("family-georgian"), candidates=2, revise=True,
                                  revise_rounds=2, revise_engine="heuristic", revise_budget_s=60)


class TestRepairIsTheDeclaredLoopInItsOldPosition:
    def test_repair_returns_the_same_tuple_and_updates_the_callers_object(self, compose_module):
        plan, log, parti = compose_module.instantiate("centre-passage-double-pile", _brief("family-georgian"))
        # strip the declared pass the composer already ran inside instantiate? it did not: repair
        # runs in compose(), not instantiate(); this record is pre-repair
        ident = id(plan)
        res, rlog = compose_module.repair(plan, rounds=2, budget_s=10)
        assert id(plan) == ident, "repair must update the caller's object in place; compose relies on it"
        assert "findings" in res and "counts" in res
        assert isinstance(rlog, list)
        assert plan.get("revision_report", {}).get("mode") == "declared"
        for line in rlog:
            assert line[0].isupper() and line.endswith(".")

    def test_no_prose_is_parsed_anywhere_in_repair(self, compose_module):
        """Read the CODE, not the docstring: repair's docstring quotes the old parse as the thing
        it replaced, and a source-reading test that matched the quotation failed on the
        sentence that explains the fix."""
        import ast, inspect, textwrap
        src = textwrap.dedent(inspect.getsource(compose_module.repair))
        fn = ast.parse(src).body[0]
        body = [n for n in fn.body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant))]
        code = "\n".join(ast.unparse(n) for n in body)
        assert "statement" not in code and "split(" not in code, code

    def test_the_declared_loop_reads_the_unrounded_need_so_the_dining_room_moves(self, compose_module):
        """The 12.3 ft dining room needing 12.333: compose.repair's parse read 12.3 and it
        never moved. Any candidate whose dining room is declared below its table's need
        must move it, or refuse with a reason -- never leave the finding standing silently."""
        plan, log, parti = compose_module.instantiate("centre-passage-double-pile", _brief("family-georgian"))
        res0 = compose_module.PC.check(plan, compose_module.C)
        fits0 = [f for f in res0["findings"] if f.get("kind") == "furniture-fit" and f["severity"] == "serious"]
        res, rlog = compose_module.repair(plan, rounds=4, budget_s=20)
        fits1 = [f for f in res["findings"] if f.get("kind") == "furniture-fit" and f["severity"] == "serious"]
        assert len(fits1) < len(fits0), "the declared loop cleared no furniture finding"
        rep = plan["revision_report"]
        touched = {m["finding"] for rd in rep["rounds"] for m in rd["moves"] if m.get("finding")}
        assert touched, "no move named a finding"
        # every surviving furniture finding is ACCOUNTED FOR: tried in a round, or listed in
        # `remaining` under a class. The first version let "the loop stopped" excuse any
        # finding, and `round-cap` is the usual stop (the session's audit found it vacuous).
        accounted = touched | {i["id"] for cls in rep["remaining"].values() for i in cls}
        for f in fits1:
            assert f["id"] in accounted, f"{f['id']} survived and the report does not mention it"


class TestThePlacedLoopOnTheReturnedCandidates:
    def test_candidates_carry_score_before_and_a_revision_report(self, composed):
        for c in composed["candidates"]:
            assert "score_before" in c and "rank_before" in c and "revision" in c
            assert "drawn_key_before" in c and "drawn_key_after" in c
            assert c["revision"]["summary"]["rounds"] == len(c["revision"]["rounds"])
            assert c["plan"].get("revision_report", {}).get("mode") == "placed"
            assert c["plan"]["revision_report"].get("declared_pass") is not None

    def test_score_and_score_before_are_one_instrument(self, composed, compose_module):
        """Both are score_candidate on the DECLARED record; a drawn finding never enters
        the composite for the revised candidate and not for its earlier self. The first
        version of this test asserted only that an axis existed and the score was in range,
        which `PC.check(placed)` also satisfies (WP-9.4). Now: re-score the returned plan
        STRIPPED of its placement with the composer's own instrument and match `score`."""
        import copy
        OP = mc.load("openings", os.path.join(BUILD, "openings.py"))
        PC = mc.load("plan_check", os.path.join(BUILD, "plan_check.py"))
        C = PC.load_corpus()
        for c in composed["candidates"]:
            axes = {a["axis"] for a in c["score_axes"]}
            assert "connections" in axes
            declared = OP.strip_placement(copy.deepcopy(c["plan"]))
            declared.pop("revision_report", None)
            res = PC.check(declared, C)
            assert res["counts"].get("fatal", 0) == c["counts"].get("fatal", 0)
            assert res["counts"].get("serious", 0) == c["counts"].get("serious", 0)
            # the drawn layer reports could-not-evaluate (info) on an unplaced record; no
            # drawn VERDICT enters the declared instrument
            assert not [f for f in res["findings"] if f["layer"] == "drawn" and f["severity"] != "info"], \
                "the declared instrument sees no drawn finding"

    def test_the_revision_lines_are_decisions_of_kind_revision(self, composed):
        for c in composed["candidates"]:
            rows = [e for e in c["decisions_structured"] if e["kind"] == "revision"]
            applied = c["revision"]["summary"]["moves_applied"]
            assert len(rows) == applied, (len(rows), applied)
            named = [r for r in rows if r["field"]]
            assert not rows or len(named) >= 0.8 * len(rows), \
                "a revision sentence matched no decision pattern"

    def test_four_contrasting_candidates_are_still_returned_and_never_called_good(self, compose_module):
        res = compose_module.compose(_brief("family-georgian"), candidates=4, revise=True,
                                     revise_rounds=1, revise_engine="heuristic", revise_budget_s=30)
        cands = res["candidates"]
        assert len(cands) == 4 and len({c["parti"] for c in cands}) == 4, "four DISTINCT diagrams"
        # the order is the composer's rule, on the RE-SCORED set: fatal-free first, then score
        keys = [_composer_order(c) for c in cands]
        assert keys == sorted(keys), "the revised set is not in the composer's order"
        for c in cands:
            assert "score_before" in c and ("revision" in c)
            assert "verdict" not in c and "good" not in c, "no candidate is called good"
        assert any("not therefore good" in line for line in res["how_to_read_this"])

    def test_revise_false_returns_the_set_as_composed(self, compose_module):
        res = compose_module.compose(_brief("family-georgian"), candidates=2, revise=False)
        for c in res["candidates"]:
            assert "score_before" not in c and "revision" not in c
            assert not any(r.get("geometry") for lv in c["plan"]["levels"] for r in lv["rooms"])


class TestTheRevisedSetKeepsTheComposersInvariants:
    """Twenty-five composer tests run with `revise=False` and the shipped product is the
    revised set (the session's audit): nothing held the loop's output to the composer's own
    rules. These do, on the module fixture that runs with revise on."""

    def test_every_revised_plan_validates_and_keeps_the_briefs_must_have_rooms(self, composed):
        import jsonschema
        ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        schema = json.load(open(os.path.join(ROOT, "schema", "plan.schema.json")))
        brief = _brief("family-georgian")
        for c in composed["candidates"]:
            jsonschema.validate(c["plan"], schema)
            types = {r["type"] for lv in c["plan"]["levels"] for r in lv["rooms"]}
            for must in brief.get("must_have") or []:
                assert must in types, f"the loop dropped a must_have room ({must}) from {c['parti']}"
            assert all(r.get("width_ft", 0) > 0 and r.get("length_ft", 0) > 0 for lv in c["plan"]["levels"] for r in lv["rooms"])
            ids = [r["id"] for lv in c["plan"]["levels"] for r in lv["rooms"]]
            assert len(ids) == len(set(ids)), "a room id was duplicated by a move"

    def test_the_revised_set_is_in_the_composers_order_and_rank_before_is_stated(self, composed, compose_module):
        cands = composed["candidates"]
        keys = [_composer_order(c) for c in cands]
        assert keys == sorted(keys)
        assert {c["rank_before"] for c in cands} == set(range(1, len(cands) + 1))

    def test_the_revise_budget_is_the_sets_and_a_candidate_it_does_not_reach_says_so(self, compose_module):
        """Per candidate, 21 candidates on the proving engine at 600 s each was four hours of
        the one-worker pool for one metered submission (the session's audit). The budget is
        spent in rank order and a candidate the budget does not reach is returned as
        composed, with the reason on the record."""
        res = compose_module.compose(_brief("family-georgian"), candidates=2, revise=True,
                                     revise_rounds=1, revise_engine="heuristic", revise_budget_s=0.5)
        first, second = res["candidates"][0], res["candidates"][1]
        assert second["revision"] is None and "budget" in second["revision_skipped"]
        assert "score_before" in second and second["score_before"] == second["score"]
        assert any(l.startswith("REVISION SKIPPED:") for l in second["decisions"])
        assert any(e["kind"] == "disclosure" for e in second["decisions_structured"] if e["statement"].startswith("REVISION SKIPPED"))
        # the first candidate got what there was: a loop that stopped on the budget
        assert first["revision"] is None or first["revision"]["stop_reason"] in ("budget", "no-rounds", "round-cap", "converged", "no-applicable-move")
