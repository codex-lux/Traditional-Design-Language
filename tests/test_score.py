"""The composite score, pinned.

WHY THIS FILE EXISTS. The published figure was a demerit total -- 100 a fatal, 8 a serious,
1 a minor, less 20 a point of style fidelity -- shown in the workbench in a 26px numeral
labelled SCORE. It was LOWER IS BETTER, had no ceiling, and its magnitude tracked how many
times a plan happened to be checked rather than how good it was: 36 on one brief and 208 on
another for plans of comparable merit. Every reader took the biggest number for the winner.

WHY IT WAS REWRITTEN. Its first version was audited by mutation -- twenty deliberately wrong
scorers run against it -- and THIRTEEN SURVIVED. Among them: counting unjudged faults as
clear (the exact leak one test was named for, whose assertion turned out to be an algebraic
identity that no input could falsify); scoring an unevaluated axis as a full pass; a minor
finding costing nothing; the rooms and connections axes, 34 points of the 100, measuring
nothing at all; and swapping two weights, which changed which plans the composer recommends
while the whole suite stayed green. Every test below was checked against the mutant it is
supposed to kill. A test that cannot fail is worse than no test, because it is counted.
"""
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _brief(name):
    with open(os.path.join(ROOT, "briefs", f"{name}.json")) as f:
        return json.load(f)


def _res(findings=(), rooms=0, fault=None, constraint=None, counts=None):
    """A minimal validator result, so an axis can be exercised on a stated input rather than
    only on whatever the two shipped briefs happen to produce."""
    return {"rooms": rooms, "counts": counts or {}, "findings": list(findings),
            "fault_summary": fault or {"present": 0, "clear": 0, "unjudged": 0},
            "constraint_summary": constraint or {"present": 0, "clear": 0, "unjudged": 0}}


def _plan(declared=None, groupings=(), massing=None, levels=None):
    return {"declared": declared or {}, "groupings": list(groupings), "massing": massing,
            "levels": levels if levels is not None else [{"rooms": []}]}


FP_CLEAN = {"notes": [], "tests_run": 2, "tests_failed": 0}


class TestTheWeightsAreDeliberate:
    """A weight vector is not an implementation detail: swapping two of them changed which
    plans the composer recommends, with every other test still green. They are pinned as
    LITERALS here so that moving one is a deliberate act with a diff attached."""

    EXPECTED = {"solecisms": 20, "rooms": 18, "connections": 16, "fidelity": 25,
                "area": 7, "bedrooms": 4, "canon": 5, "buildability": 5}

    def test_the_weights_are_exactly_these(self, compose_module):
        got = {n: w for n, w, _ in compose_module.SCORE_AXES}
        assert got == self.EXPECTED, (
            "SCORE_AXES moved. That re-ranks the corpus — see docs/reports/"
            "candidate-score-composite.md for how fidelity's weight was measured, and "
            "re-measure before re-pinning rather than pinning whatever it now says.")

    def test_the_axes_are_a_hundred(self, compose_module):
        assert sum(w for _, w, _ in compose_module.SCORE_AXES) == 100

    def test_fidelity_can_outweigh_the_spread_of_everything_else(self, compose_module):
        """The measured basis for fidelity's 25, restated as a property. Fidelity's full
        swing is its weight; the non-fidelity subtotal's observed spread between clean
        candidates is 18.0 points on family-georgian and 22.0 on bungalow-small. At 18 the
        axis could not span the field it exists to outweigh, and a tidewater-georgian brief
        came back recommending an octagon — the sentence WP-4.5 was written to delete."""
        fid = next(w for n, w, _ in compose_module.SCORE_AXES if n == "fidelity")
        assert fid >= 22, (
            f"fidelity at {fid} is below the largest measured non-fidelity spread (22.0), "
            f"so being the right diagram cannot decide against being a tidier wrong one")

    def test_the_scoring_constants_are_pinned(self, compose_module):
        """Every one of these survived mutation in the first version of this file."""
        assert compose_module.SEV_CREDIT == {
            "fatal": 0.0, "serious": 0.0, "minor": 0.5, "advisory": 1.0, "info": 1.0}
        assert compose_module.MAX_FIT == 7.0, "3.0 native + 2.0 canonical + 1.0 beds + 1.0 area"
        assert compose_module.FOOTPRINT_TESTS == 2
        assert compose_module.BEDROOM_TYPES == {
            "bedroom", "primary-bedroom", "bedchamber", "garret-chamber", "nursery"}, (
            "dressing-room and sleeping-porch share function_class 'sleeping' and are not "
            "bedrooms anybody counts")

    LAYERS = {"fault": "solecisms",
              "room": "rooms", "furniture": "rooms", "daylight": "rooms",
              "servicing": "rooms", "plan": "rooms",
              "adjacency": "connections", "circulation": "connections",
              "privacy": "connections", "completeness": "connections",
              "style": "canon", "grouping": "canon",
              "code": None,
              # WP-6.2 added the `drawn` layer and mapped it to connections. Re-pinned only
              # after measuring what this pin exists to protect: the RETURNED SETS on both
              # shipped briefs are unchanged, in membership and in order, and so is every
              # score — family-georgian still returns centre-passage-double-pile 70.60,
              # five-part-palladian 61.10, side-hall-town-house 56.30,
              # living-hall-picturesque 55.80. It has to be a no-op today, because the drawn
              # layer judges a PLACEMENT and the composer does not place its candidates, so
              # the only finding it can emit here is the `info` that says it could not
              # evaluate — and an info is pulled out of every axis's fraction already. The
              # mapping is for the day a placed plan is scored, when a room nothing reaches
              # must cost a candidate something.
              "drawn": "connections"}

    def test_every_layer_is_mapped_to_the_axis_it_is_mapped_to(self, compose_module):
        """SCORE_LAYERS is as load-bearing as the weights and was not pinned at all. An
        independent mutation audit moved `grouping` from canon to rooms and the composer
        returned a DIFFERENT SET on family-georgian — tower-villa in place of
        living-hall-picturesque — with the whole suite green. That is verbatim the failure
        this file's own docstring says was closed. One layer is 5 to 34 points moving between
        two axes of different weight, so remapping one is a re-ranking of the corpus."""
        assert compose_module.SCORE_LAYERS == self.LAYERS, (
            "SCORE_LAYERS moved. That re-ranks the corpus — a finding layer is worth a "
            "different number of points on a different axis. Re-measure the returned sets "
            "before re-pinning.")

    def test_exactly_one_layer_is_deliberately_unscored(self, compose_module):
        """The code layer, and only the code layer: plan_check.py's own note calls code
        findings advisory and jurisdictional. Any OTHER layer mapping to None would be a
        finding quietly excused."""
        assert [k for k, v in compose_module.SCORE_LAYERS.items() if v is None] == ["code"]


class TestEachAxisActuallyMeasuresSomething:
    """The rooms and connections axes are 34 points of the 100. A mutant that credited every
    flagged room in full — i.e. that measured nothing — passed the first version of this
    file. These exercise each axis on a stated input with a hand-computable answer."""

    def test_a_serious_finding_spends_its_room_and_a_minor_halves_it(self, compose_module):
        f = [{"layer": "room", "severity": "serious", "room": "a"},
             {"layer": "furniture", "severity": "minor", "room": "b"}]
        ax = compose_module._axis_from_layers(_res(f, rooms=4), "rooms", 4)
        # a spends 1.0, b spends 0.5, c and d whole -> 2.5 of 4
        assert ax["clean"] == 2.5 and ax["of"] == 4 and ax["share"] == 0.625

    def test_the_worst_finding_against_a_room_decides_it_not_the_count(self, compose_module):
        many_minors = [{"layer": "room", "severity": "minor", "room": "a"} for _ in range(9)]
        ax = compose_module._axis_from_layers(_res(many_minors, rooms=2), "rooms", 2)
        assert ax["clean"] == 1.5, "nine minors on one room must still cost that one room's half"
        worst = many_minors + [{"layer": "room", "severity": "serious", "room": "a"}]
        ax2 = compose_module._axis_from_layers(_res(worst, rooms=2), "rooms", 2)
        assert ax2["clean"] == 1.0, "a serious among the minors must spend the room outright"

    def test_an_info_finding_is_unjudged_not_a_pass_in_the_room_axes(self, compose_module):
        """Same severity, three treatments, one of them 'unjudged is passed' — which is the
        one direction this corpus must never round in. info is now outside the fraction in
        the room axes exactly as it already was in canon and solecisms."""
        f = [{"layer": "daylight", "severity": "info", "room": "a"}]
        ax = compose_module._axis_from_layers(_res(f, rooms=2), "rooms", 2)
        assert ax["share"] == 1.0 and ax["flagged"] == 0
        assert ax["unjudged"] == 1, "the info must be REPORTED as unjudged, not simply ignored"

    def test_buildability_runs_the_right_way_round(self, compose_module):
        for failed, share in ((0, 1.0), (1, 0.5), (2, 0.0)):
            ax = compose_module._axis_buildability(
                {"notes": [], "tests_run": 2, "tests_failed": failed})
            assert ax["share"] == share and ax["flagged"] == failed

    def test_buildability_does_not_charge_for_a_note_that_is_not_a_test(self, compose_module):
        """footprint() emits four kinds of note and only two are tests. 'Lot caps this diagram
        at 4 bays' is a fact about the lot, not a failure of the plan, and it was costing 2.5
        points of 100 — against a 1.6-point margin on briefs/bungalow-small.json."""
        fp = {"notes": ["Lot caps this diagram at 4 bays instead of its usual 5: …"],
              "tests_run": 2, "tests_failed": 0}
        assert compose_module._axis_buildability(fp)["share"] == 1.0

    def test_the_area_axis_is_measured_against_the_brief_s_own_tolerance(self, compose_module):
        """Invisible on both shipped briefs, where every returned candidate happens to sit at
        miss == 0 — so an audit could delete the division by `tol` entirely and nothing moved.
        The same miss must score differently under a different tolerance or the axis is not
        measuring what it says."""
        def area_share(miss, tol):
            card = compose_module.score_candidate(
                _res(rooms=1), _plan(), {"bedrooms": 0}, 0.0, FP_CLEAN, miss, tol)
            return next(a for a in card["score_axes"] if a["axis"] == "area")["share"]
        assert area_share(0.06, 0.12) == 0.5
        assert area_share(0.06, 0.24) == 0.75, "a looser tolerance must forgive the same miss more"
        assert area_share(0.12, 0.12) == 0.0, "at the tolerance the axis is spent"
        assert area_share(0.0, 0.12) == 1.0

    def test_buildability_clamps_before_it_publishes_not_only_after(self, compose_module):
        """The central ceiling clamp catches an out-of-band SHARE, but `clean` and `flagged`
        are published straight off the tally. An audit deleted the local clamp and got
        `clean: -3, flagged: 5, share: 2.5` onto the record, with the score still legal."""
        ax = compose_module._axis_buildability({"notes": [], "tests_run": 2, "tests_failed": 5})
        assert ax["share"] == 0.0 and ax["clean"] == 0 and ax["flagged"] == 2, ax

    def test_fidelity_is_a_share_of_the_fit_function_s_own_maximum(self, compose_module):
        for fit, share in ((7.0, 1.0), (3.5, 0.5), (0.0, 0.0), (-7.5, 0.0), (99.0, 1.0)):
            card = compose_module.score_candidate(
                _res(rooms=1), _plan(), {"bedrooms": 0}, fit, FP_CLEAN, 0.0, 0.12)
            ax = next(a for a in card["score_axes"] if a["axis"] == "fidelity")
            assert ax["share"] == share, (fit, ax["share"])

    def test_only_real_bedrooms_count_toward_the_bedroom_axis(self, compose_module):
        rooms = [{"type": "bedroom"}, {"type": "primary-bedroom"},
                 {"type": "dressing-room"}, {"type": "closet"}, {"type": "sleeping-porch"}]
        card = compose_module.score_candidate(
            _res(rooms=5), _plan(levels=[{"rooms": rooms}]), {"bedrooms": 4},
            0.0, FP_CLEAN, 0.0, 0.12)
        ax = next(a for a in card["score_axes"] if a["axis"] == "bedrooms")
        assert ax["clean"] == 2, "a dressing room, a closet and a sleeping porch are not bedrooms"

    def test_canon_routes_an_info_finding_to_unjudged_rather_than_failing_it(self, compose_module):
        f = [{"layer": "style", "severity": "info", "rule": "x.c01"}]
        ax = compose_module._axis_canon(
            _res(f, constraint={"present": 0, "clear": 1, "unjudged": 1}),
            _plan(declared={"cornice": "boxed"}))
        assert ax["flagged"] == 0 and ax["unjudged"] >= 1
        assert ax["share"] == 1.0

    def test_the_worst_finding_against_a_canon_rule_decides_it_not_the_best(self, compose_module):
        """The rooms axis has this test (min over per-room credit) and the canon axis did not,
        which an independent audit found by flipping `min` to `max` on `_axis_canon`'s
        per_rule and watching the whole suite stay green while family-georgian's positions 3
        and 4 swapped and every score moved."""
        f = [{"layer": "style", "severity": "minor", "rule": "r1"},
             {"layer": "style", "severity": "serious", "rule": "r1"}]
        ax = compose_module._axis_canon(
            _res(f, constraint={"present": 1, "clear": 3, "unjudged": 0}),
            _plan(declared={"a": "b", "c": "d"}))
        assert ax["clean"] == 5.0, (
            f'a serious and a minor against the same rule must cost the rule outright, '
            f'not credit it with the minor\'s half: clean={ax["clean"]}')

    def test_a_finding_that_names_no_rule_becomes_its_own_opportunity(self, compose_module):
        """`_axis_from_layers` and `_axis_canon` both promise, in comments, that a finding
        naming no room or no rule "becomes its own opportunity, so nothing lands outside the
        denominator". Neither promise had a test; removing `+ len(loose)` from either
        denominator lets a plan-wide finding cost nothing at all."""
        f = [{"layer": "room", "severity": "serious"}]          # no room key
        ax = compose_module._axis_from_layers(_res(f, rooms=2), "rooms", 2)
        assert ax["of"] == 3 and ax["share"] < 1.0, (
            f'a plan-wide finding must widen the denominator and cost something: {ax}')
        g = [{"layer": "grouping", "severity": "serious"}]      # no rule key
        ax2 = compose_module._axis_canon(_res(g), _plan(declared={"a": "b"}))
        assert ax2["of"] == 2 and ax2["share"] < 1.0, ax2

    def test_the_canon_denominator_counts_the_massing_and_the_evaluated_constraints(self, compose_module):
        """Pinned arithmetic, because the `of` expression carries four terms and an audit
        found +1 on it, and the massing term dropped from it, both invisible."""
        ax = compose_module._axis_canon(
            _res(constraint={"present": 1, "clear": 2, "unjudged": 0}),
            _plan(declared={"s1": "v", "s2": "v"}, groupings=["g1"], massing="four-over-four"))
        assert ax["of"] == 2 + 1 + 3 + 1, f'2 slots + 1 grouping + 3 constraints + 1 massing: {ax["of"]}'
        no_massing = compose_module._axis_canon(
            _res(constraint={"present": 1, "clear": 2, "unjudged": 0}),
            _plan(declared={"s1": "v", "s2": "v"}, groupings=["g1"], massing=None))
        assert no_massing["of"] == ax["of"] - 1, "a plan with no massing has one fewer opportunity"

    def test_unjudged_is_reported_at_the_larger_of_its_two_sources(self, compose_module):
        """`max(cs.unjudged, info_findings)`, whose comment says it "keeps the number honest
        if that invariant ever stops holding". Every existing test used inputs where the two
        agree, so `min` passed just as well."""
        ax = compose_module._axis_canon(
            _res([{"layer": "style", "severity": "info", "rule": "r1"}],
                 constraint={"present": 0, "clear": 1, "unjudged": 9}),
            _plan(declared={"a": "b"}))
        assert ax["unjudged"] == 9, f'must not under-report: {ax["unjudged"]}'

    def test_canon_counts_each_unjudged_constraint_once_not_twice(self, compose_module):
        """plan_check increments constraint_summary["unjudged"] AND emits an info finding for
        the same constraint. Seeding from the summary and then adding every info counted them
        twice — the workbench printed 17 where the truth was 13."""
        f = [{"layer": "style", "severity": "info", "rule": f"x.c0{i}"} for i in range(4)]
        ax = compose_module._axis_canon(
            _res(f, constraint={"present": 1, "clear": 0, "unjudged": 4}),
            _plan(declared={"a": "b"}, groupings=["g"], massing="four-over-four"))
        assert ax["unjudged"] == 4, f'double counted: {ax["unjudged"]}'


class TestUnjudgedIsNotPassed:
    def test_unjudged_faults_are_outside_the_fraction_not_inside_it(self, compose_module):
        """The first version of this test asserted `of == clean + flagged`, which is an
        algebraic identity of the code it was checking and could not fail for any input. The
        leak it was named for — counting unjudged as clear — passed it, and took the
        solecisms share from 0.71 to 0.89. Asserted against the arithmetic now."""
        card = compose_module.score_candidate(
            _res(rooms=1, fault={"present": 22, "clear": 54, "unjudged": 129}),
            _plan(), {"bedrooms": 0}, 0.0, FP_CLEAN, 0.0, 0.12)
        ax = next(a for a in card["score_axes"] if a["axis"] == "solecisms")
        # 1e-4: the published share is rounded to four places on the record.
        assert abs(ax["share"] - 54 / 76) < 1e-4, (
            f'solecisms share {ax["share"]} is not clear/(clear+present) = {54 / 76:.4f}; '
            f'{(54 + 129) / 205:.4f} would mean the 129 unjudged had been counted as clear')
        assert ax["of"] == 76 and ax["unjudged"] == 129

    def test_an_axis_with_no_evidence_has_its_weight_dropped_not_passed(self, compose_module):
        """Exercised on a constructed input, because the first version of this test used a
        brief on which every axis happens to be evaluated — so the branch it was written for
        never ran, and a mutant that scored an unevaluable axis 1.0 passed it."""
        card = compose_module.score_candidate(
            _res(rooms=1, fault={"present": 0, "clear": 0, "unjudged": 205}),
            _plan(), {"bedrooms": 0}, 7.0, FP_CLEAN, 0.0, 0.12)
        sol = next(a for a in card["score_axes"] if a["axis"] == "solecisms")
        assert sol["share"] is None and sol["points"] is None and sol["note"]
        assert card["score_weight_unevaluated"] >= 20, "the solecisms weight must be dropped"
        assert card["score_weight_evaluated"] == sum(
            a["weight"] for a in card["score_axes"] if a["points"] is not None)
        assert card["score"] == round(
            100 * sum(a["points"] for a in card["score_axes"] if a["points"] is not None)
            / card["score_weight_evaluated"], 1)

    def test_a_dropped_axis_neither_helps_nor_hurts_the_score(self, compose_module):
        """The renormalisation, stated as the property that makes it honest: a candidate with
        no fault evidence must score what it scores on the rest, not 0 and not 100."""
        common = dict(rooms=4, findings=[{"layer": "room", "severity": "serious", "room": "a"}])
        judged = compose_module.score_candidate(
            _res(common["findings"], rooms=4, fault={"present": 0, "clear": 10, "unjudged": 0}),
            _plan(), {"bedrooms": 0}, 7.0, FP_CLEAN, 0.0, 0.12)
        dropped = compose_module.score_candidate(
            _res(common["findings"], rooms=4, fault={"present": 0, "clear": 0, "unjudged": 10}),
            _plan(), {"bedrooms": 0}, 7.0, FP_CLEAN, 0.0, 0.12)
        # Both inputs drop the same two axes (no bedrooms asked for, nothing declared), so
        # the only difference between them is whether the fault sheet was evidence.
        assert dropped["score_weight_unevaluated"] - judged["score_weight_unevaluated"] == 20
        assert dropped["score"] < judged["score"], (
            "a clean fault sheet must be worth more than no fault sheet at all")
        assert dropped["score"] > 0, "and no fault sheet must not be scored as a failure"


class TestTheCeilingIsReal:
    def test_a_negative_area_tolerance_cannot_push_the_score_past_a_hundred(self, compose_module):
        """The regression this clamp exists for. `area` clamped only its bottom, and
        schema/brief.schema.json declared area_tolerance with no minimum, so a schema-valid
        brief published a score of 902.8 'out of 100' in a 26px numeral. The schema now
        refuses it AND the scorer clamps it; this pins the second, because a schema is not
        the only way into score_candidate()."""
        card = compose_module.score_candidate(
            _res(rooms=1), _plan(), {"bedrooms": 0}, 0.0, FP_CLEAN, 0.2, -0.1)
        area = next(a for a in card["score_axes"] if a["axis"] == "area")
        assert area["share"] <= 1.0 and area["points"] <= area["weight"]
        assert 0 <= card["score"] <= 100

    def test_the_schema_refuses_the_briefs_that_used_to_produce_it(self, compose_module):
        import jsonschema
        with open(os.path.join(ROOT, "schema", "brief.schema.json")) as f:
            schema = json.load(f)
        for bad in ({"area_tolerance": -0.001}, {"bedrooms": -2},
                    {"target_area_sf": 0}, {"candidates": 0}):
            brief = dict(_brief("family-georgian"), **bad)
            try:
                jsonschema.validate(brief, schema)
            except jsonschema.ValidationError:
                continue
            raise AssertionError(f"schema still accepts {bad}")

    def test_no_axis_can_leave_its_own_band_on_a_real_brief(self, compose_module):
        for name in ("family-georgian", "bungalow-small"):
            for c in compose_module.compose(_brief(name))["candidates"]:
                assert c["score"] is None or 0 <= c["score"] <= 100, c["parti_name"]
                for a in c["score_axes"]:
                    if a["share"] is None:
                        assert a["points"] is None; continue
                    assert 0.0 <= a["share"] <= 1.0 and 0.0 <= a["points"] <= a["weight"], a


class TestNoMalformedInputCanFailAWholeJob:
    """compose() has NO per-candidate try/except: one raise inside score_candidate does not
    spoil one candidate, it fails the job and returns four plans as a single error string.

    THESE THREE TESTS WERE WRITTEN ONCE AND LOST. They were added in an earlier round of this
    work, passed, and were then dropped by a later wholesale rewrite of this file — and
    nothing noticed, because a test that vanishes does not fail. That is the same class as
    everything else this file guards, committed by the same author against his own suite, and
    it is why they carry this note rather than being quietly restored."""

    R = {"rooms": 2, "counts": {}, "findings": [],
         "fault_summary": {"present": 1, "clear": 1, "unjudged": 0},
         "constraint_summary": {"present": 0, "clear": 1, "unjudged": 0}}

    def test_no_malformed_input_can_fail_a_whole_compose_job(self, compose_module):
        """Four of these raised when first measured: a finding with no severity, one with no
        layer, and a None fit, tol or miss — `fit` was guarded in its division and not in the
        label that rounds it. A string `bedrooms` is the fifth: the CLI does not schema-check
        a brief passed to compose() as a library."""
        FP = {"notes": [], "tests_run": 2, "tests_failed": 0}
        R = self.R
        cases = {
            "finding with no severity": ({**R, "findings": [{"layer": "room", "room": "a"}]},
                                         _plan(), {"bedrooms": 2}, 1.0, FP, 0.0, 0.12),
            "finding with no layer": ({**R, "findings": [{"severity": "serious", "room": "a"}]},
                                      _plan(), {"bedrooms": 2}, 1.0, FP, 0.0, 0.12),
            "fit is None": (R, _plan(), {"bedrooms": 2}, None, FP, 0.0, 0.12),
            "fit is NaN": (R, _plan(), {"bedrooms": 2}, float("nan"), FP, 0.0, 0.12),
            "tol is None": (R, _plan(), {"bedrooms": 2}, 1.0, FP, 0.0, None),
            "miss is None": (R, _plan(), {"bedrooms": 2}, 1.0, FP, None, 0.12),
            "miss is inf": (R, _plan(), {"bedrooms": 2}, 1.0, FP, float("inf"), 0.12),
            "bedrooms is a string": (R, _plan(), {"bedrooms": "4"}, 1.0, FP, 0.0, 0.12),
            "bedrooms is None": (R, _plan(), {"bedrooms": None}, 1.0, FP, 0.0, 0.12),
            "fp carries no tally": (R, _plan(), {"bedrooms": 2}, 1.0, {"notes": ["a"]}, 0.0, 0.12),
            "fp carries nothing": (R, _plan(), {"bedrooms": 2}, 1.0, {}, 0.0, 0.12),
            "tests_failed above tests_run": (R, _plan(), {"bedrooms": 2}, 1.0,
                                             {"notes": [], "tests_run": 2, "tests_failed": 9}, 0.0, 0.12),
        }
        for name, args in cases.items():
            card = compose_module.score_candidate(*args)
            json.dumps(card)                       # and it must still serialise
            assert card["score"] is None or 0 <= card["score"] <= 100, name
            for a in card["score_axes"]:
                assert a["share"] is None or 0.0 <= a["share"] <= 1.0, (name, a["axis"], a["share"])

    def test_a_plan_record_with_no_levels_does_not_crash_the_scorer(self, compose_module):
        """score_candidate reads plan["levels"] to count bedrooms. A record that omits it is
        malformed, and the scorer must say it could not count them rather than raise."""
        FP = {"notes": [], "tests_run": 2, "tests_failed": 0}
        card = compose_module.score_candidate(self.R, {}, {"bedrooms": 4}, 7.0, FP, 0.0, 0.12)
        ax = next(a for a in card["score_axes"] if a["axis"] == "bedrooms")
        assert ax["share"] == 0.0 or ax["share"] is None

    def test_an_out_of_band_fit_cannot_push_an_axis_past_its_weight(self, compose_module):
        """pick_partis can return a NEGATIVE fit (a forbidden massing costs 4.0), and a future
        term could push it past MAX_FIT; neither may leave the fidelity axis outside 0..25."""
        FP = {"notes": [], "tests_run": 2, "tests_failed": 0}
        for fit in (-7.5, 0.0, 7.0, 99.0):
            card = compose_module.score_candidate(self.R, _plan(), {"bedrooms": 2}, fit, FP, 0.0, 0.12)
            ax = next(a for a in card["score_axes"] if a["axis"] == "fidelity")
            assert 0.0 <= ax["share"] <= 1.0 and 0.0 <= ax["points"] <= ax["weight"], (fit, ax)


class TestNothingIsDroppedSilently:
    def test_every_layer_the_validator_emitted_is_classified(self, compose_module):
        result = compose_module.compose(_brief("family-georgian"))
        for c in result["candidates"]:
            assert c["score_unclassified_layers"] == [], (
                f'{c["parti_name"]} carries findings in {c["score_unclassified_layers"]}, '
                f"which no axis scores — add them to SCORE_LAYERS or say why they are exempt")

    def test_an_unrecognised_layer_is_reported_rather_than_ignored(self, compose_module):
        card = compose_module.score_candidate(
            _res([{"layer": "brand-new-layer", "severity": "fatal", "room": "a"}], rooms=2),
            _plan(), {"bedrooms": 0}, 0.0, FP_CLEAN, 0.0, 0.12)
        assert card["score_unclassified_layers"] == ["brand-new-layer"]

    def test_the_axis_definitions_ride_on_the_result_once(self, compose_module):
        """`what` and the out-of-100 datum were repeated in eight rows per candidate, which
        the MCP tool bills a model for. They live on the result now; the rows must not carry
        them back."""
        result = compose_module.compose(_brief("family-georgian"))
        model = result["score_model"]
        assert model["of"] == 100
        assert [a["axis"] for a in model["axes"]] == [n for n, _, _ in compose_module.SCORE_AXES]
        assert all(a["what"] for a in model["axes"])
        for c in result["candidates"]:
            assert all("what" not in a for a in c["score_axes"])


class TestADroppedCandidateSaysWhyItWasDropped:
    """WP-2.4's guarantee is that a candidate which cannot fit the stated lot is DROPPED and
    reported rather than silently outscored. The report was `fp["notes"][-1]`, and by the time
    a candidate is dropped the last note is almost always "at N bays this diagram is at the
    width it grows to" — an infeasible lot forces the bay count past the maximum, which fires
    that test every time. Measured on a 30 ft lot before the fix: 4 of 4 dropped candidates
    named a reason that was not why they were dropped, in the record the MCP tool and the
    workbench both read."""

    def test_the_reason_is_the_lot_not_whichever_note_landed_last(self, compose_module):
        result = compose_module.compose(
            {"style": "tidewater-georgian", "target_area_sf": 3400, "bedrooms": 4,
             "context": {"lot_width_ft": 30}}, 4)
        dropped = result.get("dropped_lot_infeasible") or []
        assert dropped, "a 30 ft lot must drop candidates; if it no longer does, re-pick the lot"
        for d in dropped:
            assert "does not fit this lot" in d["why"], (
                f'{d["parti"]} was dropped for the lot and reports: {d["why"]!r}')

    def test_footprint_counts_its_tests_rather_than_its_notes(self, compose_module):
        """The same defect's other half: `notes` holds two failed TESTS and two statements
        about the lot, and the buildability axis charged for all four."""
        brief = _brief("family-georgian")
        _plan_, _log, parti = compose_module.instantiate("centre-passage-double-pile", brief)
        plan, _l, _p = compose_module.instantiate("centre-passage-double-pile", brief)
        fp = compose_module.footprint(plan, parti)
        assert fp["tests_run"] == compose_module.FOOTPRINT_TESTS
        assert 0 <= fp["tests_failed"] <= fp["tests_run"]
        assert fp["tests_failed"] <= len(fp["notes"]), "a failed test must have said so in a note"


class TestAFixedKeyListDoesNotDropWhatItDoesNotName:
    """Not the score, but the same defect this session exists to remove, and the one place
    it recurred. `mcp_server/core.py`'s RULE_KEYS projects each derived proportion rule onto
    a hand-written tuple, so a key nobody remembered is silently deleted on the way to the
    workbench and to every tdl_get_proportions caller. `error` was missing, and an
    unevaluable rule arrived with its refusal removed and drew as "null in". Fixing that one
    key left two more missing — `authority_note`, carried by 730 of the corpus's 900 derived
    rules, and `diagnostic`. The list is the bug, so the list is what gets pinned."""

    def test_rule_keys_publishes_every_key_the_pack_schema_defines(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "core", os.path.join(ROOT, "mcp_server", "core.py"))
        core = importlib.util.module_from_spec(spec); spec.loader.exec_module(core)
        with open(os.path.join(ROOT, "schema", "proportion-pack.schema.json")) as f:
            schema = json.load(f)
        declared = set(schema["properties"]["derived_rules"]["items"]["properties"])
        src = open(os.path.join(ROOT, "mcp_server", "core.py")).read()
        start = src.index("RULE_KEYS = (")
        published = set(eval(src[start + len("RULE_KEYS = "):src.index(")", start) + 1]))
        missing = declared - published
        assert not missing, (
            f"RULE_KEYS drops {sorted(missing)}, which schema/proportion-pack.schema.json "
            f"defines on a rule. A key this list does not name is deleted silently on the "
            f"way to every consumer — add it, or say in the comment why it is withheld.")
        # the engine adds these two on top of the schema's own; they are not optional
        assert {"value", "in_range", "error"} <= published, (
            "value/in_range/error are set by proportion_engine.evaluate(), not by the pack — "
            "dropping `error` is how a refusal became a measurement")

    def test_the_engines_own_row_publishes_every_key_the_pack_schema_defines(self):
        """The rebuild ONE LAYER IN, which the guard above never reached (WP-8.4).

        `proportion_engine.evaluate()` builds its own row key-by-key, and its comment has
        claimed since WP-5.11 that "tests/test_wp46_packs.py compares this dict against the
        schema so it cannot recur". No such test existed: the one that exists is the method
        above, and it reads `mcp_server/core.py`'s RULE_KEYS -- a different rebuild, further
        out. So the function whose own comment tells the story was the one nothing checked,
        and OQ 88's `applies_when` was dropped there exactly as described, leaving a scope
        that refused 0 of 293 deliveries while every check stayed green."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "pe", os.path.join(ROOT, "build", "proportion_engine.py"))
        pe = importlib.util.module_from_spec(spec); spec.loader.exec_module(pe)
        with open(os.path.join(ROOT, "schema", "proportion-pack.schema.json")) as f:
            declared = set(json.load(f)["properties"]["derived_rules"]["items"]["properties"])
        # Read a real row rather than the source: this asserts what the engine ACTUALLY
        # emits, so a key listed in a dict literal but overwritten later still fails.
        pack = pe.resolve("sash-light")
        rows = pe.evaluate(pack, None, {"ceiling_height": 108.0})["rules"]
        assert rows, "sash-light produced no rules"
        emitted = set(rows[0])
        missing = declared - emitted
        assert not missing, (
            f"proportion_engine.evaluate() drops {sorted(missing)}, which "
            f"schema/proportion-pack.schema.json defines on a rule. Every consumer reads "
            f"these rows -- resolve_kit.eval_packs among them -- so a key this rebuild does "
            f"not carry is deleted before anything can act on it.")


class TestAFatalDisqualifies:
    """The first build WITHHELD the score on a fatal, and measuring it killed the idea:
    composed across eight briefs, five returned sets in which EVERY candidate carried a fatal
    -- cape-cod-colonial and greek-revival among them, which OQ 63 already records as styles
    that cannot clear the fault corpus under their own native diagram. Four blank columns is
    less than the demerit total gave. The disqualification is carried in words and in the
    ORDERING instead."""

    def _card(self, compose_module, parti_id="centre-passage-single-pile"):
        brief = _brief("family-georgian")
        plan, _log, parti = compose_module.instantiate(parti_id, brief)
        res = compose_module.PC.check(plan)
        fp = compose_module.footprint(plan, parti)
        return res, compose_module.score_candidate(res, plan, brief, 7.0, fp, 0.0, 0.12)

    def test_a_fatal_finding_is_stated_as_a_disqualification_in_words(self, compose_module):
        res, card = self._card(compose_module)
        assert res["counts"].get("fatal", 0) >= 1, "this parti is pinned as carrying fatals"
        assert card["disqualified"] is True and "fatal" in card["disqualified_because"]

    def test_a_disqualified_candidate_is_still_scored_and_still_measured(self, compose_module):
        _res_, card = self._card(compose_module)
        assert isinstance(card["score"], (int, float))
        assert len(card["score_axes"]) == len(compose_module.SCORE_AXES)

    def test_a_clean_candidate_is_not_marked_disqualified(self, compose_module):
        for c in compose_module.compose(_brief("family-georgian"))["candidates"]:
            if c["counts"].get("fatal", 0) == 0:
                assert c["disqualified"] is False, c["parti_name"]

    def test_a_style_that_cannot_clear_the_fault_corpus_still_returns_a_ranked_set(self, compose_module):
        result = compose_module.compose(
            {"style": "cape-cod-colonial", "target_area_sf": 2400, "bedrooms": 4}, 4)
        cands = result["candidates"]
        assert cands and all(c["counts"].get("fatal", 0) > 0 for c in cands), (
            "this test's premise is that every candidate here is disqualified; if that has "
            "changed, re-pick a style the fault corpus cannot clear rather than re-pinning")
        assert all(isinstance(c["score"], (int, float)) and c["disqualified"] for c in cands)
        assert len({c["score"] for c in cands}) > 1, "a disqualified set must still discriminate"


class TestTheOrderIsWhatItSays:
    def test_a_disqualified_candidate_never_outranks_a_clean_one_however_it_scores(
            self, compose_module, monkeypatch):
        """Exercised through compose()'s OWN sort. The first version of this test retyped the
        implementation's sort key into the test and applied it to a local list — it asserted
        that sorted() sorts, and stayed green under a mutant that stripped the fatal term from
        the real key. Here the scorer is inverted so that every disqualified candidate scores
        higher than every clean one, and compose() must still put the clean ones first."""
        real = compose_module.score_candidate

        def inverted(res, plan, brief, fit, fp, miss, tol):
            card = real(res, plan, brief, fit, fp, miss, tol)
            card["score"] = 99.9 if res["counts"].get("fatal", 0) else 1.0
            return card

        monkeypatch.setattr(compose_module, "score_candidate", inverted)
        cands = compose_module.compose(_brief("family-georgian"), 13)["candidates"]
        fatals = [c["counts"].get("fatal", 0) for c in cands]
        assert 0 in fatals and any(f > 0 for f in fatals), (
            "this test needs a MIXED set; widen the window or pick another brief")
        assert fatals == sorted(fatals), (
            "a candidate scoring 99.9 with a fatal came back above a clean one scoring 1.0 — "
            "the fatal count must stay the primary sort key, ahead of the score")

    def test_returned_fatal_free_first_then_highest_score(self, compose_module):
        """Two independent properties rather than a re-derivation of the implementation's own
        key, which would confirm itself whatever that key said."""
        for name in ("family-georgian", "bungalow-small"):
            cands = compose_module.compose(_brief(name), 13)["candidates"]
            fatals = [c["counts"].get("fatal", 0) for c in cands]
            assert fatals == sorted(fatals), f"{name}: a fatal-bearing plan came back above a cleaner one"
            for group in set(fatals):
                scores = [c["score"] for c in cands if c["counts"].get("fatal", 0) == group]
                assert scores == sorted(scores, reverse=True), (
                    f"{name}: candidates with {group} fatal(s) are not in descending score order")

    def test_the_returned_set_is_native_dominated_not_merely_tidy(self, compose_module):
        """The behavioural guard on FIDELITY's weight specifically — not on the weighting.

        An earlier version of this docstring called it "the one that fails when a weight
        moves". That was half true and the independent audit measured which half: swapping
        `solecisms` and `fidelity` does fail here, because fidelity is what this test is
        about. Swapping `rooms` (18) and `connections` (16) does NOT — it moves every
        published score on both briefs and every behavioural test stays green. Only the
        literal EXPECTED dict in TestTheWeightsAreDeliberate catches that one, and a literal
        pin is a change-detector rather than a defence. Said plainly here rather than left as
        a claim the test cannot support.
        WP-4.5's ruling is that the right diagram wins unless another is genuinely much worse;
        at fidelity 18 this brief returned tower-villa and octagon-radial, both fit 2.0 and
        both borrowed, over the native side-hall town house. An octagon for a Tidewater
        Georgian is the sentence WP-4.5 exists to delete."""
        cands = compose_module.compose(_brief("family-georgian"))["candidates"]
        fits = [c["style_fit"] for c in cands]
        assert fits[0] == 7.0, "the winner must be the fully native, canonically massed diagram"
        assert sum(1 for f in fits if f >= 3.0) >= 3, (
            f"only {sum(1 for f in fits if f >= 3.0)} of {len(fits)} returned diagrams reach "
            f"fit 3.0; fidelity has stopped deciding — fits were {fits}")


class TestTheComposerIsDeterministic:
    """ORDER INDEPENDENCE IS THE POINT OF THE FIXTURE BELOW. Both snapshot-and-compare tests
    here are worthless without it, and an independent audit proved it: with the `list()`
    removed from instantiate(), running this FILE passes 32/32, because a test earlier in it
    composes the same brief first and the snapshot is taken of an already-polluted corpus. In
    CI's order (`pytest tests/`, alphabetical) they could never fail. A deepcopy taken after
    an unknown number of prior compose() calls in a session-scoped module proves nothing."""

    @pytest.fixture(autouse=True)
    def _pristine_partis(self, compose_module):
        import copy
        clean = copy.deepcopy(compose_module.PARTIS)
        yield
        compose_module.PARTIS.clear()
        compose_module.PARTIS.update(clean)


    def test_composing_one_brief_does_not_change_another_s_result(self, compose_module):
        """A pre-existing leak found while calibrating this score, because calibration needs
        stable numbers and did not get them. The plan record took a REFERENCE to the parti's
        own groupings list and attach_garage() appended to it, so one brief asking for a
        garage left five of twenty-one partis declaring a garage grouping for every later
        brief in the process. connected-farmstead moved 146.0 -> 155.0. The workbench runs
        every compose job on one long-lived worker."""
        def sig(name):
            b = _brief(name)
            return {c["parti"]: c["demerits"]
                    for c in compose_module.compose(b, b.get("candidates", 4))["candidates"]}
        first = sig("bungalow-small")
        sig("family-georgian")
        assert sig("bungalow-small") == first, "composing one brief changed another's result"

    def test_a_parti_record_is_not_mutated_by_composing(self, compose_module):
        import copy
        before = copy.deepcopy(compose_module.PARTIS)
        compose_module.compose(_brief("family-georgian"))
        changed = [pid for pid in before if before[pid] != compose_module.PARTIS[pid]]
        assert not changed, f"compose() mutated the shared parti records: {changed}"

    def test_a_plan_never_shares_a_list_object_with_the_parti_it_came_from(self, compose_module):
        """The identity check, and it is the one that actually holds.

        Both tests above are ORDER-DEPENDENT: they snapshot the corpus and compose, so if an
        earlier test in the session has already polluted a parti the snapshot contains the
        pollution and the diff is empty. Mutation-tested — remove the `list()` from
        instantiate() and both of them still pass, because tests earlier in this file compose
        the same brief first. This one cannot be fooled by ordering: it asks whether the plan
        and the parti are looking at the SAME list, which is the defect itself rather than one
        of its symptoms."""
        brief = _brief("family-georgian")
        for parti_id in ("centre-passage-double-pile", "five-part-palladian"):
            plan, _log, _parti = compose_module.instantiate(parti_id, brief)
            parti = compose_module.PARTIS[parti_id]
            assert plan["groupings"] is not parti.get("groupings"), (
                f"{parti_id}: the plan holds the parti's OWN groupings list. attach_garage() "
                f"appends to it, so one brief asking for a garage would change every later "
                f"brief in the process.")
            n_before = len(parti.get("groupings") or [])
            plan["groupings"].append("a-grouping-that-does-not-exist")
            assert len(parti.get("groupings") or []) == n_before, (
                f"{parti_id}: appending to the plan reached the corpus")
