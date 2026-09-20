"""WP-9.2 — the composer's two loops. Every test is named for the finding it protects.

`compose.repair` is the DECLARED loop now (build/revise.py with place=False), in its old
position; the PLACED loop runs on the returned candidates after ranking and re-scores them on
the PLACED record AT BOTH ENDS (WP-14.2), so `score` and `score_before` are one instrument and
both read the house the loop works on and the sheet draws. That sentence said "on the declared
record" until 20 Sep 2026 and the ruling reversed it: the pair is still one instrument, a
DIFFERENT one, and this file's own guard below was asserting the retired contract.
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
        """RE-CUT ONTO THE INSTRUMENT WP-14.2 RULED, NOT RE-PINNED TO ITS NUMBERS.

        This asserted that `counts` reproduces `PC.check(strip_placement(plan))` -- the
        DECLARED reading -- under a docstring saying a drawn finding never enters the
        composite. The 20 Sep ruling moved the verdict onto the PLACED house, so the
        contract this guard held is the retired one; it went red at `serious 23 == 58`,
        which is exactly the movement WP-14.2's report published.

        The SUBJECT is unchanged and is the reason this is a re-cut: `score` and
        `score_before` are one instrument. What moved is which house that instrument reads.
        So the after end is RE-DERIVED here independently -- re-check the returned plan AS
        IT STANDS and match `counts` element for element -- and the before end is held by
        its key, which is the cheapest independent reader of `counts_before`. The two ends
        have different strengths and the docstring says so rather than letting a reader
        read one green tick as two.

        AND THE OLD FATAL LINE COULD NOT HAVE REPORTED THIS. Measured on this brief, both
        candidates read the same fatal count on both readings (1 and 2) and differ on
        serious, minor and info -- `a fixture where both branches return the same number
        guards neither` (WP-11.15), met in the line above the one that fired. The whole
        `counts` dict is asserted here, and the premise that the two readings differ at all
        is asserted too: where they coincide this guard distinguishes nothing, and it says
        so loudly instead of passing.
        """
        import copy
        OP = mc.load("openings", os.path.join(BUILD, "openings.py"))
        PC = mc.load("plan_check", os.path.join(BUILD, "plan_check.py"))
        C = PC.load_corpus()
        for c in composed["candidates"]:
            axes = {a["axis"] for a in c["score_axes"]}
            assert "connections" in axes
            plan = c["plan"]
            assert any(r.get("geometry") for lv in plan["levels"] for r in lv["rooms"]), \
                f"{c['parti']}: the returned plan carries no placement, so every assertion " \
                f"below would be about the wrong house"
            placed = PC.check(copy.deepcopy(plan), C)
            assert placed["counts"] == c["counts"], (
                f"{c['parti']}: `counts` is not a re-derivable reading of the returned "
                f"placed record: {placed['counts']} against {c['counts']}")
            stripped = OP.strip_placement(copy.deepcopy(plan))
            stripped.pop("revision_report", None)
            strip = PC.check(stripped, C)
            assert strip["counts"] != c["counts"], (
                f"{c['parti']}: the placed and stripped readings agree ({strip['counts']}), "
                f"so the assertion above passes under either instrument and this guard is "
                f"distinguishing nothing. Drive a candidate whose placement moves the "
                f"verdict rather than deleting the line that noticed.")
            # THE RULING, POSITIVELY: the instrument carries drawn verdicts now. Asserting
            # only that the placed reading matches would stay green on a `counts` that had
            # quietly gone back to a house with no drawn finding in it.
            assert [f for f in placed["findings"]
                    if f["layer"] == "drawn" and f["severity"] != "info"], \
                f"{c['parti']}: the verdict's own reading carries no drawn finding above info"
            # The BEFORE end, held by its key rather than re-derived: the record the loop
            # started from is gone by now. [fatal, serious, minor] is `critique.key_of`'s
            # first three elements and `counts_before` is the same critique's counts, so a
            # `score_before` computed on any other reading parts them.
            kb = c["drawn_key_before"]
            cb = c["counts_before"]
            assert [cb.get("fatal", 0), cb.get("serious", 0), cb.get("minor", 0)] == list(kb[:3]), \
                f"{c['parti']}: `counts_before` and `drawn_key_before` are two readings: {cb} / {kb}"

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
        """RE-CUT 16 Sep 2026, AND ITS OLD MESSAGE NAMED THE WRONG LAYER. It read
        `the loop dropped a must_have room ({must}) from {c['parti']}` and went red at the
        WP-13.3 merge on `library` -- and the loop had dropped nothing. Measured with
        `revise=False`, so no round ever runs: BOTH of this brief's must_have rooms are absent
        AS COMPOSED. The composer never placed them, which is what it is built to do --
        CLAUDE.md, *"it will not invent a room the parti has no place for"* -- and it SAYS so,
        twice, in its own voice:

            JUDGMENT: the brief requires a library and this diagram has no place for one.
            Not added -- the position matters more than the presence.

        **So the corpus was honest and the assertion was wrong**: it demanded a guarantee the
        composer explicitly declines, and attributed the absence to the one layer that had not
        touched it. This class is named for the LOOP's invariants, so that is what it asserts
        now -- a must_have room the composer DID place must survive every round, and one it
        refused must carry its stated reason.

        WHAT CHANGED AT WP-13.3 was neither the loop nor the composer's refusal but WHICH
        partis come back. Measured on a `git archive` of 49e2389 against this tree:

            WP-13.2   centre-passage-double-pile, five-part-palladian   both rooms, both rooms
            now       side-hall-townhouse, courtyard-and-portal          neither, neither

        That is a product property that is now false and it is NOT this test's to assert:
        `oq/the-composer-returns-a-set-that-satisfies-neither-must-have-room`.

        AND THE SILENT-DROP FINDING I NEARLY PUBLISHED WAS A FALSE POSITIVE. The first sweep
        matched the type id `breakfast-room` and found a stated refusal for the library and
        none for the breakfast room. The log writes *"a breakfast room"* with a space. Both are
        stated; re-deriving with the looser needle is the only reason that is not in a report.
        """
        import jsonschema
        ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        schema = json.load(open(os.path.join(ROOT, "schema", "plan.schema.json")))
        brief = _brief("family-georgian")
        musts = brief.get("must_have") or []
        assert musts, "COULD NOT EVALUATE: this brief states no must_have room"
        placed_somewhere = 0
        for c in composed["candidates"]:
            jsonschema.validate(c["plan"], schema)
            types = {r["type"] for lv in c["plan"]["levels"] for r in lv["rooms"]}
            log = " ".join(str(x) for x in (c.get("decisions") or []))
            for must in musts:
                if must in types:
                    placed_somewhere += 1
                    continue
                # Not present. The loop may not be the reason, so the composer must have said
                # so. The needle is the room's WORDS and not its hyphenated id -- the log reads
                # "a breakfast room", and matching the id alone is what produced a false
                # finding on the first sweep.
                words = must.replace("-", " ")
                assert words in log.lower() or must in log.lower(), (
                    f"{c['parti']} has no {must} and its decision log does not say why. A "
                    f"must_have room absent with no stated refusal is the silent drop this "
                    f"test exists for; an absence the composer NAMES is the corpus working.")
            assert all(r.get("width_ft", 0) > 0 and r.get("length_ft", 0) > 0
                       for lv in c["plan"]["levels"] for r in lv["rooms"])
            ids = [r["id"] for lv in c["plan"]["levels"] for r in lv["rooms"]]
            assert len(ids) == len(set(ids)), "a room id was duplicated by a move"
        # THE PREMISE, so a set that happens to place none of them cannot pass this vacuously:
        # the reader is told which half of the test actually ran.
        print(f"must_have rooms PLACED across the set: {placed_somewhere} of "
              f"{len(musts) * len(composed['candidates'])}")

    def test_the_revised_set_is_in_the_composers_order_and_rank_before_is_stated(self, composed, compose_module):
        cands = composed["candidates"]
        keys = [_composer_order(c) for c in cands]
        assert keys == sorted(keys)
        assert {c["rank_before"] for c in cands} == set(range(1, len(cands) + 1))

    def test_the_revise_budget_is_the_sets_and_a_candidate_it_does_not_reach_says_so(self, compose_module):
        """Per candidate, 21 candidates on the proving engine at 600 s each was four hours of
        the one-worker pool for one metered submission (the session's audit). The budget is
        the set's, shared equally across the candidates left, and a candidate the budget does
        not reach is returned as composed, with the reason on the record."""

    def test_the_sets_budget_is_shared_and_not_taken_whole_by_the_leader(self, compose_module, monkeypatch):
        """Measured on a CP-capable box with the set's 120 s spent in rank order: the leader's
        loop took all of it and three of four candidates came back as composed. Each
        candidate's loop is handed an equal share of what is left."""
        RV = mc.load("revise", os.path.join(BUILD, "revise.py"))
        seen = []
        orig = RV.revise

        def spy(plan, **kw):
            if kw.get("place"):              # the PLACED loop; repair's declared loop calls this too
                seen.append(kw.get("budget_s"))
            return orig(plan, **kw)
        monkeypatch.setattr(RV, "revise", spy)
        compose_module.compose(_brief("family-georgian"), candidates=3, revise=True,
                               revise_rounds=1, revise_engine="heuristic", revise_budget_s=90)
        assert len(seen) == 3
        assert seen[0] <= 90 / 3 + 0.01, f"the leader was handed {seen[0]:.1f} s of a 90 s set budget"
        assert all(s >= 1.0 for s in seen)

    def test_the_candidate_the_budget_does_not_reach_is_read_by_rank_not_by_list_position(self, compose_module):
        """SPLIT OUT OF THE SHARE TEST, 16 Sep 2026, BECAUSE IT WAS SHIELDED BY IT. Both halves
        lived in one body with the 90 s three-candidate sweep first, so every mutation that
        starves a candidate trips `seen[0] <= 30` and this half is NEVER REACHED -- measured,
        two mutations (reverse the spend order; hand the leader the whole budget) both died on
        that line at `seen[0] == 90.0`. That is WP-12.4's own finding: a guard that runs only
        where the bug cannot occur. Split, the reverse-order mutation reaches this body and
        bites it at the `by_rank[1]` line.

        AND THE RETIRED ASSERTION IS RED IN BOTH STATES, WHICH IS NOT THE FAILURE MODE I
        EXPECTED. `res["candidates"][0]["revision"] is not None` reads False on the pristine
        tree (list[0] is `courtyard-and-portal`, rank 2, skipped for budget) AND False under
        the mutation (list[0] is `side-hall-townhouse`, rank 1, skipped) -- because the
        candidate that got the budget is the one that re-ranks, so list position follows the
        revision and never the funding. A guard that cannot be GREEN carries exactly as much
        information as one that cannot be RED: it convicts the code whatever the code does.

        1.2 s for two: the first gets its share (floored at 1 s), its first critique and one
        round overrun it, and less than a second is left for the second -- which says so."""
        res = compose_module.compose(_brief("family-georgian"), candidates=2, revise=True,
                                     revise_rounds=1, revise_engine="heuristic", revise_budget_s=1.2)
        # RE-CUT 16 Sep 2026: THIS READ LIST POSITION WHERE IT MEANS RANK. It took
        # `res["candidates"][0]` as "the leader who was funded" -- and **the budget is spent in
        # RANK order while the returned list is in the composer's order AFTER revision**, so the
        # moment a revised candidate changes places the two are different houses. Measured, two
        # trials agreeing: `list[0]` is `courtyard-and-portal` with `rank_before=2`, skipped for
        # want of budget, and `list[1]` is `side-hall-townhouse` with `rank_before=1`, which got
        # its share and ran. The loop was right and the assertion was reading the wrong candidate.
        # `test_the_revised_set_is_in_the_composers_order_and_rank_before_is_stated` is green
        # over exactly this, which is why nothing else noticed.
        by_rank = {c.get("rank_before"): c for c in res["candidates"]}
        assert set(by_rank) == {1, 2}, f"rank_before is not a permutation of 1..2: {sorted(by_rank)}"
        first, second = by_rank[1], by_rank[2]
        assert first["revision"] is not None, (
            "the candidate ranked FIRST got no share of the set's budget (this is rank_before "
            f"== 1, which is list position {res['candidates'].index(first)})")
        assert second["revision"] is None and "budget" in second["revision_skipped"]
        assert "score_before" in second and second["score_before"] == second["score"]
        assert any(l.startswith("REVISION SKIPPED:") for l in second["decisions"])
        assert any(e["kind"] == "disclosure" for e in second["decisions_structured"] if e["statement"].startswith("REVISION SKIPPED"))
        # the first candidate got what there was: a loop that stopped on the budget
        assert first["revision"] is None or first["revision"]["stop_reason"] in ("budget", "no-rounds", "round-cap", "converged", "no-applicable-move")
