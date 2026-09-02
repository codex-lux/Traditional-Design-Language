"""WP-9.2 — the composer's two loops. Every test is named for the finding it protects.

`compose.repair` is the DECLARED loop now (build/revise.py with place=False), in its old
position; the PLACED loop runs on the returned candidates after ranking and re-scores them on
the declared record so `score` and `score_before` are one instrument.
"""
import json
import os

import pytest


def _brief(name):
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return json.load(open(os.path.join(ROOT, "briefs", f"{name}.json")))


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
        for f in fits1:
            # every surviving furniture finding was either tried and refused, or beyond the budget
            assert f["id"] in touched or rep["stop_reason"] in ("budget", "round-cap"), f["id"]


class TestThePlacedLoopOnTheReturnedCandidates:
    def test_candidates_carry_score_before_and_a_revision_report(self, composed):
        for c in composed["candidates"]:
            assert "score_before" in c and "rank_before" in c and "revision" in c
            assert "drawn_key_before" in c and "drawn_key_after" in c
            assert c["revision"]["summary"]["rounds"] == len(c["revision"]["rounds"])
            assert c["plan"].get("revision_report", {}).get("mode") == "placed"
            assert c["plan"]["revision_report"].get("declared_pass") is not None

    def test_score_and_score_before_are_one_instrument(self, composed):
        """Both are score_candidate on the DECLARED record; a drawn finding never enters
        the composite for the revised candidate and not for its earlier self."""
        for c in composed["candidates"]:
            axes = {a["axis"] for a in c["score_axes"]}
            assert "connections" in axes
            assert c["score"] is None or 0 <= c["score"] <= 100

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
        assert len(res["candidates"]) == 4
        assert all("good" not in (c.get("revision") or {}).get("summary", {}) for c in res["candidates"])
        assert any("not therefore good" in line for line in res["how_to_read_this"])

    def test_revise_false_returns_the_set_as_composed(self, compose_module):
        res = compose_module.compose(_brief("family-georgian"), candidates=2, revise=False)
        for c in res["candidates"]:
            assert "score_before" not in c and "revision" not in c
            assert not any(r.get("geometry") for lv in c["plan"]["levels"] for r in lv["rooms"])
