"""OQ 52 — the generators must not state measurements they never took.

The finding these tests protect, in one sentence: `build/elevation.py` supplied twelve
measurements as constants — a dormer count, five chimney plan dimensions, a stack cap and its
shadow lines, a raking-cornice member count, and a gutter's outlets and scuppers — and the fault
corpus then adjudicated real houses on all of them. On each shipped reference plan that was five
convictions and two passes, and the flagship case is worth stating in full because it is the
shape of the whole class: `build/roof.py`'s dormer_rhythm_check REFUSES to judge dormers, in its
own words, because no plan schema field authors one; `elevation.py` then wrote `dormer_count: 0`
over that refusal, and `dormers-off-the-bay`'s secondary test (`dormer_count % 2 == 1`) reported
"Dormers Off the Rhythm" as PRESENT and serious on a house with no dormers modelled.

This is the project's own first discipline running backwards — unjudged reported as judged — and
CLAUDE.md names it as the one collapse the corpus least survives. So these tests pin it from
three directions: the generator's own declared limits, the seven faults that were being decided
on fabricated evidence, and the evaluator's reading of a null.

UPDATED 27 Aug 2026 (WP-5.13). The dormer half of that finding is now MODELLED rather than
refused: `declared.dormer` gives a plan record three states — absent (could not evaluate), the
string "none" (a measured zero), and an object (a house with dormers) — and both reference plans
state none, with their evidence in their own `note`. Three of the seven therefore leave the
unjudged list legitimately, which is the opposite of the failure this file was written for and
has to be told apart from it. The way it is told apart: delete the declaration and all three must
return to unjudged. That round trip is asserted, and it is the only assertion that can prove the
three states are three.

The same commit found the failure trying to come back in through the new field. `dormer_count: 0`
is a legitimate measurement, and `dormer-off-the-bay`'s parity secondary is `dormer_count % 2 ==
1`, so the first run after both houses could say "none" convicted both of "Dormers Off the
Rhythm: 0 against equals 1". Zero dormers is not an even number of dormers. Fault tests may now
carry an `applies_when` precondition on a MEASUREMENT (schema/fault.schema.json), a test that
declines is not run rather than passed, and a fault whose every test declines comes back under a
fourth state, `not_applicable` — which exists because such a fault previously appeared in no list
at all, and a fault absent from every list reads exactly like a clear one.
"""
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The faults that were adjudicated on fabricated numbers before 26 Aug 2026. Five were reported
# PRESENT on both reference plans and two CLEAR — a fabricated failure and a fabricated pass
# sitting beside each other, which is what made the class hard to see from the output alone.
FABRICATED_SEVEN = (
    "capless-stack",
    "cornice-gutter-without-a-liner",
    "dormer-off-the-bay",
    "dormer-wall",
    "overscaled-dormer",
    "raking-cornice-that-does-not-match",
    "vestigial-chimney-chase",
)

# THREE OF THE SEVEN MOVED ON 27 AUG 2026 (WP-5.13), and the reason is the opposite of the one
# that put them here. They were unjudged because no plan record could state a dormer at all, so
# `dormer_count: 0` was a fabricated constant standing over a refusal. `declared.dormer` exists
# now, both reference houses STATE they carry none, and a stated zero is a measurement -- so the
# critic may use it. What it may NOT do is convict on it, and the difference is exactly what the
# tests below hold:
#
#   dormer-off-the-bay   NOT APPLICABLE. Every one of its three tests is now preconditioned on
#                        `dormer_count >= 1`. A house with no dormers has no rhythm to be off, and
#                        before the guard its parity secondary (`dormer_count % 2 == 1`) reported
#                        "Dormers Off the Rhythm: 0 against equals 1" on both houses the moment
#                        they could say none -- OQ 52's flagship failure returning through the
#                        very field built to prevent it.
#   dormer-wall          CLEAR, on a real measurement: 0 in of dormer face over the building
#                        width is 0, which is at most 0.4. A roof with no dormers has not become
#                        a storey, and the evidence for saying so is a number this corpus took.
#   overscaled-dormer    CLEAR, on the same measurement (its first secondary is dormer-wall's
#                        primary, verbatim -- a duplication that predates this package).
#
# Delete the declaration and all three go straight back to unjudged. That round trip is asserted
# below, because it is the only thing that proves the three states are three and not two.
STILL_UNJUDGED = ("capless-stack", "cornice-gutter-without-a-liner",
                  "raking-cornice-that-does-not-match", "vestigial-chimney-chase")
JUDGED_ON_A_STATED_ZERO = {"dormer-off-the-bay": "not_applicable",
                           "dormer-wall": "clear",
                           "overscaled-dormer": "clear"}

REFERENCE_PLANS = ("tidewater-georgian-careful", "spec-builder-colonial")


@pytest.fixture(scope="module")
def elevation_mod():
    import elevation
    return elevation


def _plan(name):
    return json.load(open(os.path.join(ROOT, "plans", f"{name}.json")))


@pytest.fixture(scope="module")
def supplied(elevation_mod):
    """The measurements the elevation layer actually hands the critic, per reference plan."""
    out = {}
    for name in REFERENCE_PLANS:
        rec = elevation_mod.build_elevation(_plan(name))
        out[name] = rec["measurements"]
    return out


class TestTheGeneratorDeclaresItsLimits:
    def test_not_modelled_is_not_empty_and_carries_a_reason_each(self, elevation_mod):
        """The list is documentation with teeth: every entry says WHY the thing is not modelled,
        because the only honest way to remove an entry is to model the thing and delete it in the
        same commit."""
        assert elevation_mod.NOT_MODELLED, "the declared-limits list must not be silently emptied"
        for name, reason in elevation_mod.NOT_MODELLED.items():
            assert isinstance(reason, str) and reason.strip(), f"{name} needs a stated reason"

    @pytest.mark.parametrize("plan_name", REFERENCE_PLANS)
    def test_no_unmodelled_measurement_ever_reaches_the_critic(self, plan_name, supplied,
                                                               elevation_mod):
        """The structural half of the fix. _derive_measurements filters NOT_MODELLED on the way
        out, so reintroducing one of these by a careless m.update() cannot put it back in front
        of the fault corpus — this test is what notices if that filter is removed."""
        leaked = sorted(set(supplied[plan_name]) & set(elevation_mod.NOT_MODELLED))
        assert not leaked, (
            f"{plan_name}: the elevation supplied {leaked}, which it does not model. "
            "A measurement nobody took must be ABSENT, not zero — see OQ 52.")

    @pytest.mark.parametrize("plan_name", REFERENCE_PLANS)
    def test_a_supplied_measurement_is_never_null(self, plan_name, supplied):
        """A thing modelled but unmeasurable on this house is dropped, not sent as null. Sending
        null would put the critic in the position of comparing against nothing."""
        nulls = sorted(k for k, v in supplied[plan_name].items() if v is None)
        assert not nulls, f"{plan_name}: null measurements supplied: {nulls}"


class TestTheSevenFaultsAreNoLongerDecidedOnFabricatedEvidence:
    def test_the_split_still_covers_all_seven(self):
        """The seven are the historical list and it does not shrink. Splitting it into the four
        still unmeasurable and the three now judged on a stated zero is the kind of edit that
        loses one silently — this is what notices."""
        assert set(STILL_UNJUDGED) | set(JUDGED_ON_A_STATED_ZERO) == set(FABRICATED_SEVEN)
        assert not set(STILL_UNJUDGED) & set(JUDGED_ON_A_STATED_ZERO)

    @pytest.mark.parametrize("plan_name", REFERENCE_PLANS)
    def test_they_come_back_could_not_judge(self, plan_name, plan_check_module):
        """Not present, not clear — unjudged. This is the whole point: the corpus does not know
        whether these houses have gutters, a raking cornice or a stack of a given plan size, and
        it must now say so instead of deciding. The three dormer faults left this list when the
        record gained a way to state a dormer; see JUDGED_ON_A_STATED_ZERO above and the two
        tests below it."""
        result = plan_check_module.check(_plan(plan_name))
        unjudged = {r.get("fault") for r in (result.get("fault_unjudged") or [])}
        for fault_id in STILL_UNJUDGED:
            assert fault_id in unjudged, (
                f"{plan_name}: '{fault_id}' is being adjudicated again. It can only be judged "
                "from a measurement no generator in this corpus takes (OQ 52).")

    @pytest.mark.parametrize("plan_name", REFERENCE_PLANS)
    def test_a_stated_none_is_used_but_never_convicts(self, plan_name, plan_check_module,
                                                      core_module, elevation_mod):
        """The three that moved, each pinned to the state it moved to and to the reason.

        REWRITTEN 28 Aug 2026. The first version read `where.get(fault_id, "clear")` off
        `plan_check.check()`, which returns NO clear list — so "clear" meant "appeared in none of
        the three lists I looked at", which is precisely the collapse this file's own docstring
        says `not_applicable` was invented to prevent. A fault dropped from evaluation entirely
        by a renamed id or an `_applies` change would have passed it silently. Membership is now
        asserted POSITIVELY against `core.check_measurements`, which does return a clear list."""
        rec = elevation_mod.build_elevation(_plan(plan_name))
        r = core_module.check_measurements(rec["measurements"], style=rec["style"], limit=10**6)
        where = {}
        for row in r["faults_present"]: where[row["fault"]] = "present"
        for row in r["faults_clear"]: where[row["fault"]] = "clear"
        for row in r["could_not_judge"]: where[row["fault"]] = "unjudged"
        for row in r.get("not_applicable", []): where[row["fault"]] = "not_applicable"
        for fault_id, expected in JUDGED_ON_A_STATED_ZERO.items():
            assert fault_id in where, (
                f"{plan_name}: '{fault_id}' is in NO list at all — present, clear, unjudged and "
                "not-applicable between them must account for every fault the style reaches, and "
                "a fault in none of them reads exactly like a clear one.")
            assert where[fault_id] == expected, (
                f"{plan_name}: '{fault_id}' came back {where[fault_id]}, expected {expected}.")

    @pytest.mark.parametrize("plan_name", REFERENCE_PLANS)
    def test_deleting_the_declaration_puts_all_three_back_to_unjudged(self, plan_name,
                                                                      plan_check_module):
        """The round trip, which is the only thing that proves the three states are three. Absent
        is could-not-evaluate; "none" is a measured zero; an object is a house with dormers. If
        removing the declaration left these faults judged, the generator would be supplying the
        zero on its own — which is precisely the twelve-constant class OQ 52 closed."""
        plan = _plan(plan_name)
        assert plan["declared"].pop("dormer", None) == "none", "both reference plans ship a stated none"
        result = plan_check_module.check(plan)
        unjudged = {r.get("fault") for r in (result.get("fault_unjudged") or [])}
        for fault_id in JUDGED_ON_A_STATED_ZERO:
            assert fault_id in unjudged, (
                f"{plan_name}: with no declaration at all, '{fault_id}' still came back judged. "
                "A record that says nothing about dormers must yield no dormer measurements.")

    @pytest.mark.parametrize("plan_name", REFERENCE_PLANS)
    def test_no_finding_quotes_the_fabricated_numbers(self, plan_name, plan_check_module):
        """The five convictions, by the sentences they printed. 'The Chimney That Is Not One:
        0.5556 against at-least 0.6' was 20/36 — two constants — and every number in it was
        real-looking, which is exactly why it survived so long."""
        result = plan_check_module.check(_plan(plan_name))
        statements = " ".join(f.get("statement", "") for f in result["findings"])
        for gone in ("Dormers Off the Rhythm", "The Chimney That Is Not One",
                     "The Chimney With No Hat", "The Raking Cornice That Is Not The Cornice",
                     "The built-in gutter with nowhere to fail"):
            assert gone not in statements, (
                f"{plan_name}: '{gone}' is being reported again, and the only evidence for it "
                "would be a measurement nobody took.")


class TestTheTwoRivalCorniceRulesNoLongerBothRun:
    """OQ 84, closed 27 Aug 2026 (WP-5.14).

    `cornice-that-is-a-fascia` carries two secondaries on ONE expression — the domestic boxed eave
    at 0.35–0.55 of its own height, and the full entablature-derived case at 0.85–1.2 — so
    whichever is right, the other convicts the house. The fault's own note has always said how to
    choose ("Choose the test by whether an order is present, not by preference"), in prose no
    evaluator could read.

    WP-3.2 worked around it by WITHHOLDING `cornice_projection_in` from the measurements, which
    silenced the fault on a name mismatch: `elevation.py` published
    `cornice_projection_past_wall_face_in` instead, and three of the fault's five tests — the
    primary among them — were skipped for want of a name rather than for want of a number. The
    fault came back "clear" on its wall-height ratio alone, which reads exactly like a fault that
    was actually checked.
    """

    def _tests(self, core_module):
        f = json.load(open(os.path.join(ROOT, "faults", "cornice-that-is-a-fascia.json")))
        return f, [f["test"]] + f["secondary_tests"]

    @pytest.mark.parametrize("plan_name", REFERENCE_PLANS)
    def test_exactly_one_of_the_two_rivals_runs(self, plan_name, core_module, elevation_mod):
        rec = elevation_mod.build_elevation(_plan(plan_name))
        m = rec["measurements"]
        f, tests = self._tests(core_module)
        rivals = [t for t in f["secondary_tests"]
                  if t["expression"] == "cornice_projection_in / cornice_height_in"]
        assert len(rivals) == 2, "the rival pair is what this test is about"
        states = [core_module._eval_test(t, m)["status"] for t in rivals]
        assert sorted(states) == ["evaluated", "not_applicable"], (
            f"{plan_name}: rival cornice tests came back {states}. Exactly one must run — both "
            "running means one of them convicts the house whatever it measures.")

    @pytest.mark.parametrize("plan_name", REFERENCE_PLANS)
    def test_the_name_is_supplied_and_the_primary_actually_runs(self, plan_name, core_module,
                                                                elevation_mod):
        """The half of the fix that is easy to forget. Guarding the rivals while still withholding
        `cornice_projection_in` would leave the fault just as inert and look just as green."""
        m = elevation_mod.build_elevation(_plan(plan_name))["measurements"]
        assert "cornice_projection_in" in m
        f, _ = self._tests(core_module)
        r = core_module._eval_test(f["test"], m)
        assert r["status"] == "evaluated" and r["passes"] is True, (
            f"{plan_name}: the fault's PRIMARY test is still not running — it was skipped for "
            "want of a name, not a number, from WP-3.2 until OQ 84 closed.")

    @pytest.mark.parametrize("plan_name", REFERENCE_PLANS)
    def test_without_the_guard_both_houses_would_be_convicted(self, plan_name, core_module,
                                                              elevation_mod):
        """The trap, pinned so nobody removes the guard believing it decorative. Both reference
        houses measure 0.4286 — inside the domestic band, far outside the entablature one."""
        import copy
        m = elevation_mod.build_elevation(_plan(plan_name))["measurements"]
        f, _ = self._tests(core_module)
        entab = next(copy.deepcopy(t) for t in f["secondary_tests"]
                     if t.get("applies_when", {}).get("direction") == "at-least")
        entab.pop("applies_when")
        r = core_module._eval_test(entab, m)
        assert r["status"] == "evaluated" and r["passes"] is False, (
            "the entablature rule no longer fails these houses, so this test is not pinning the "
            "trap it was written for — check whether the bands or the measurement moved.")

    @pytest.mark.parametrize("plan_name", REFERENCE_PLANS)
    def test_the_discriminator_is_not_the_order_pack_flag(self, plan_name, elevation_mod):
        """`gibbs_order_applies_to_style` is True on tidewater-georgian and means only that Gibbs
        Ionic is the order this style's cornice is GENERATED from. Reading it as "an order is
        applied to this facade" selects the entablature test and convicts the house. Checked
        before the derivation was written, and pinned here because it is the plausible wrong
        answer that a later reader would reach for first."""
        rec = elevation_mod.build_elevation(_plan(plan_name))
        assert rec["order_at_the_eave"] == 0
        assert rec["order_at_the_eave_note"]
        if rec.get("gibbs_order_applies_to_style"):
            assert rec["order_at_the_eave"] == 0, (
                "the order pack applies to this style AND no order reaches its eave — which is "
                "exactly the pair of facts that makes the pack flag the wrong discriminator")

    def test_an_engaged_order_selects_the_other_rule(self, core_module, elevation_mod):
        """Flip the record and the other test runs. Without this the pair could be guarded in a
        way that permanently silences one of them, which would pass every assertion above."""
        import copy
        plan = copy.deepcopy(_plan("tidewater-georgian-careful"))
        plan["declared"]["porch_type"] = "two-tier-engaged-portico"
        rec = elevation_mod.build_elevation(plan)
        assert rec["order_at_the_eave"] == 1
        assert "Drayton Hall" in rec["order_at_the_eave_note"]
        m = rec["measurements"]
        f = json.load(open(os.path.join(ROOT, "faults", "cornice-that-is-a-fascia.json")))
        rivals = [t for t in f["secondary_tests"]
                  if t["expression"] == "cornice_projection_in / cornice_height_in"]
        states = {t["applies_when"]["direction"]: core_module._eval_test(t, m)["status"]
                  for t in rivals}
        assert states == {"at-most": "not_applicable", "at-least": "evaluated"}


class TestTheSolarWorkaroundIsRetired:
    """The same authoring gap, found in the same WP-3.2 pass and worked around the same way:
    `solar_array_area_sqft` was withheld even though its zero was honest, because the array
    secondary would read 0/plane = 0.0 and convict a house of a patchy array it does not have.
    `applies_when` (WP-5.13) gates it now, so the honest zero can be told."""

    @pytest.mark.parametrize("plan_name", REFERENCE_PLANS)
    def test_the_honest_zero_is_supplied_and_declines_its_test(self, plan_name, core_module,
                                                               elevation_mod):
        m = elevation_mod.build_elevation(_plan(plan_name))["measurements"]
        assert m.get("solar_array_area_sqft") == 0.0
        f = json.load(open(os.path.join(ROOT, "faults", "entrance-slope-penetration.json")))
        t = next(t for t in f["secondary_tests"] if "solar_array_area_sqft" in t["expression"])
        assert core_module._eval_test(t, m)["status"] == "not_applicable"


class TestAStatedZeroConvictsNobodyInAnyStyle:
    """The guard the WP-5.13/5.10 work needed and did not have, added 28 Aug 2026 by its own
    adversarial audit — which found two live false convictions it would have caught.

    Every dormer test in this corpus was guarded by reading `test` and `secondary_tests`. There is
    a THIRD test location: `exceptions[].bounds_test`, which `core.check_measurements` substitutes
    for the fault's PRIMARY test on a matching style. `dormer-off-the-bay` and `dormer-wall` both
    carry a Second Empire exception whose bounds_test is `dormer_count / bay_count == 1.0`, and
    once WP-5.13 began supplying `dormer_count` as a stated zero that evaluated to 0.0 and reported
    both faults PRESENT — a Second Empire house convicted of Dormers Off the Rhythm for having no
    dormers. The two reference plans are not Second Empire, so nothing saw it.

    The lesson is the shape of the check, not the two records: verifying a corpus-wide change on
    the two plans that happen to ship is verifying it on 2 of 164 styles. This sweeps them all."""

    @pytest.mark.parametrize("plan_name", REFERENCE_PLANS)
    def test_no_style_convicts_on_a_dormer_measurement_that_is_zero(self, plan_name, core_module,
                                                                    elevation_mod):
        """Scoped to the EXPRESSION, not to a list of fault ids, and the first draft of this test
        got that wrong: listing `even-bay-front` as a dormer fault made it fail on
        `english-georgian-townhouse` for a 5-bay house against a 3-bay townhouse rule — a correct
        conviction on BAY count, from feeding one plan's measurements to another style's rules.
        The invariant is not "no dormer fault fires"; it is that nothing is convicted BY a dormer
        measurement whose value is a stated zero."""
        import re
        m = elevation_mod.build_elevation(_plan(plan_name))["measurements"]
        assert m["dormer_count"] == 0, "the premise: these plans STATE they carry no dormers"
        zero_dormer_names = {k for k, v in m.items() if v == 0 and "dormer" in k}
        assert "dormer_count" in zero_dormer_names, zero_dormer_names
        bad = []
        for style in sorted(core_module._data()["styles"]):
            r = core_module.check_measurements(m, style=style, limit=10**6)
            for row in r["faults_present"]:
                for ev in (row.get("failing") or row["results"]):
                    # the evaluator does not hand back the expression, so re-find the test that
                    # produced this result by its own `required` string
                    d = json.load(open(os.path.join(ROOT, "faults", row["fault"] + ".json")))
                    tests = [d.get("test")] + list(d.get("secondary_tests") or [])
                    tests += [e.get("bounds_test") for e in (d.get("exceptions") or [])]
                    for t in tests:
                        if not t or not t.get("expression"):
                            continue
                        names = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", t["expression"]))
                        if names & zero_dormer_names and core_module._eval_test(t, m) == ev:
                            bad.append(f"{style}/{row['fault']}: {t['expression']} = "
                                       f"{ev.get('value')} against {ev.get('required')}")
        assert not bad, (
            "a house that STATES it carries no dormers was convicted BY that zero:\n  "
            + "\n  ".join(sorted(set(bad))[:10]))

    def test_every_test_location_is_swept_not_just_two(self, core_module):
        """The structural half. A fault's tests live in three places and the audit found the third
        only by accident; this asserts the corpus knows about all three, so that a future guard
        pass has something to enumerate against."""
        import glob
        locations = set()
        for f in sorted(glob.glob(os.path.join(ROOT, "faults", "*.json"))):
            d = json.load(open(f))
            if d.get("test"):
                locations.add("test")
            if d.get("secondary_tests"):
                locations.add("secondary_tests")
            if any(e.get("bounds_test") for e in (d.get("exceptions") or [])):
                locations.add("exceptions[].bounds_test")
        assert locations == {"test", "secondary_tests", "exceptions[].bounds_test"}, locations

    def test_no_live_test_anywhere_divides_by_a_supplied_zero(self, core_module, elevation_mod):
        """DIVISION BY ZERO ONLY, over all three test locations — and the narrow scope is stated
        because the first draft of this docstring called itself "the general form of the bug" and
        was not. A zero DENOMINATOR raises and becomes `status: error`; that is what this catches.
        A zero NUMERATOR is the case that actually convicted Second Empire, and it is a different
        shape — often perfectly legitimate (`sum_of_dormer_face_widths_in / building_width_in` is
        rightly 0 on a house with no dormers) — so it cannot be caught by a rule about zeros and
        is caught by the sweep above instead. Verified: with the Second Empire guards removed this
        test still PASSES and the sweep fails, which is why both exist."""
        import glob
        import re
        m = elevation_mod.build_elevation(_plan("tidewater-georgian-careful"))["measurements"]
        zeros = {k for k, v in m.items() if v == 0}
        assert zeros, "no zero measurements at all — this test would be vacuous"
        offenders = []
        for f in sorted(glob.glob(os.path.join(ROOT, "faults", "*.json"))):
            d = json.load(open(f))
            tests = [d.get("test")] + list(d.get("secondary_tests") or [])
            tests += [e.get("bounds_test") for e in (d.get("exceptions") or [])]
            for t in tests:
                if not t or not t.get("expression") or "/" not in t["expression"]:
                    continue
                denom = t["expression"].rsplit("/", 1)[-1].strip()
                if denom in zeros and not t.get("applies_when"):
                    offenders.append(f"{d['id']}: {t['expression']} (denominator is 0 here)")
        assert not offenders, (
            "a test divides by a measurement this corpus supplies as zero, with no precondition:\n  "
            + "\n  ".join(offenders))


class TestTheFourthStateCannotLeakIntoTheConstraintLayer:
    """`_eval_test` is SHARED between the fault corpus and the style-constraint layer, and WP-5.13
    gave it a fourth return status. The constraint callers were not updated, because they cannot
    receive it: `schema/constraint.schema.json` sets `additionalProperties: false` on its test
    object and does not list `applies_when`, so no constraint can carry a precondition.

    That is a shield, and this corpus's own rule is that a fix relying on a shield has to look at
    what the shield covers. Both constraint call sites do `if r["status"] != "evaluated": ->
    unjudged`, which would silently file a not-applicable constraint as could-not-judge — a wrong
    answer, though a quiet one. Rather than add a fourth bucket to a path nothing can reach, this
    pins the shield: add `applies_when` to the constraint schema and this test fails, which is the
    moment to decide what those two call sites should do."""

    def test_the_constraint_schema_still_forbids_a_precondition(self):
        s = json.load(open(os.path.join(ROOT, "schema", "constraint.schema.json")))
        t = s["properties"]["test"]
        assert t.get("additionalProperties") is False
        assert "applies_when" not in t.get("properties", {}), (
            "a constraint test may now carry `applies_when`, so core._eval_test can return "
            "not_applicable to check_style_constraints and build/plan_check.py:776 — both of "
            "which currently file it as UNJUDGED. Decide what they should do before shipping it.")

    def test_no_constraint_in_the_corpus_carries_one(self):
        import glob
        offenders = []
        for f in sorted(glob.glob(os.path.join(ROOT, "styles", "*.json"))):
            d = json.load(open(f))
            for c in d.get("constraints") or []:
                if (c.get("test") or {}).get("applies_when"):
                    offenders.append(f"{d['id']}/{c.get('id')}")
        assert not offenders, offenders


class TestTheEvaluatorReadsANullAsMissing:
    def test_null_is_need_measurements_not_error(self, core_module):
        """A key present with a null value is the natural JSON encoding of 'I could not judge
        this'. Reading it by key presence alone let it through to eval, where it became a
        TypeError and then a `status: error` — a real state, but the wrong one. An error says the
        corpus asked something incoherent; this says nobody took the measurement."""
        test = {"expression": "roof_pitch_rise_per_12", "direction": "at-least", "threshold": 7}
        r = core_module._eval_test(test, {"roof_pitch_rise_per_12": None})
        assert r["status"] == "need_measurements"
        assert "roof_pitch_rise_per_12" in r["missing"]

    def test_a_real_value_still_evaluates(self, core_module):
        """The guard above must not swallow a legitimate zero — 0 is a measurement."""
        test = {"expression": "gable_count", "direction": "at-most", "threshold": 2}
        r = core_module._eval_test(test, {"gable_count": 0})
        assert r["status"] == "evaluated" and r["passes"] is True


class TestTheRoofSaysWhereItReadItsBands:
    @pytest.mark.parametrize("plan_name", REFERENCE_PLANS)
    def test_a_band_read_from_a_fallback_names_itself(self, plan_name, roof_module):
        """Four bands in build/roof.py are matched off the corpus by a rule's exact wording, each
        with a hardcoded fallback beside it that is byte-identical to today's corpus values. That
        identity is what makes the rot undetectable: a reworded rule misses, the fallback answers,
        and the record still reports `computed: True` naming the corpus file as its evidence. The
        fallbacks are kept — a check that refuses to run is worse than one that says where it read
        from — but a run that uses one now says so, and on the shipped plans none should."""
        rec = roof_module.build_roof(_plan(plan_name))
        for key in ("cape_eave", "gambrel_break", "wing_step_down"):
            part = (rec.get("checks") or {}).get(key)
            if isinstance(part, dict) and "bands_read_from_fallback" in part:
                assert part["bands_read_from_fallback"] == [], (
                    f"{plan_name}: {key} read {part['bands_read_from_fallback']} from a hardcoded "
                    "fallback, which means a corpus rule has been reworded and roof.py did not "
                    "notice (OQ 52).")


class TestABareRatioIsNeverDeliveredAsADimension:
    """OQ 53. `casing_face_width` is written `opening_width / 6` in inches by trim-classical and
    its peers, and `1 / 6` as a bare ratio by the order packs — whose own notes carry the referent
    ("Of opening_width.") in PROSE, where no evaluator can read it. resolve_kit grouped them as
    rival accounts of one quantity, so a ratio could win on precedence and land in the kit as the
    dimension: `craftsman` and `craftsman-bungalow` resolved `casing` to 0.1667 where 6 in was
    meant, chambers-ionic's `1 / 6` beating palladio-tuscan's `opening_width / 6` — two rules
    saying exactly the same thing, one of them in a form that is not a measurement.
    """

    CTX = {"ceiling_height": 108.0, "storey_height": 120.0,
           "opening_height": 80.0, "opening_width": 36.0, "span": 16.0}

    def _casing_choice(self, rk, style):
        g = rk.load_graph()
        chain = rk.chain_for(g, style)
        slots, _ = rk.resolve_slots(g, chain)
        pack_slots, _ = rk.eval_packs(rk.resolve_packs(g, chain), self.CTX, None, {})
        return rk.choose_pack(slots["casing"], pack_slots.get("casing", []), self.CTX)

    @pytest.mark.parametrize("style", ("craftsman", "craftsman-bungalow"))
    def test_the_two_live_wrong_dimensions_are_fixed(self, style, resolve_kit_module):
        """The two the register named. A casing on a 36 in door is 6 in, not 0.1667 of nothing."""
        chosen = self._casing_choice(resolve_kit_module, style)["chosen"]
        assert chosen["units"] != "ratio", (
            f"{style}: casing resolved to a bare ratio again — that is 0.1667 where a "
            "measurement was meant (OQ 53).")
        assert "opening_width" in chosen["expression"]

    @pytest.mark.parametrize("style", ("craftsman", "craftsman-bungalow"))
    def test_the_demotion_is_recorded_not_silent(self, style, resolve_kit_module):
        """Preferring the measurement is a decision this resolver takes, so it says so. A silent
        preference would be the same class of problem in the other direction: the corpus would
        stop being able to show why one of two agreeing rules was passed over."""
        chosen = self._casing_choice(resolve_kit_module, style)["chosen"]
        assert "ratio_demoted" in chosen
        assert chosen["ratio_demoted"]["pack"] == "chambers-ionic"
        assert "referent" in chosen["ratio_demoted"]["why"]

    def test_a_genuine_ratio_quantity_is_left_alone(self, resolve_kit_module):
        """The guard must stay narrow. Most ratio-valued quantities in this corpus ARE ratios and
        are right in that form — a roof pitch, an opening's height over its width, an arch's rise
        over its span. A first version of the flag fired on all of them, 1,463 times across every
        node, which is a checker crying wolf rather than a finding."""
        g = resolve_kit_module.load_graph()
        chain = resolve_kit_module.chain_for(g, "craftsman")
        slots, _ = resolve_kit_module.resolve_slots(g, chain)
        packs = resolve_kit_module.resolve_packs(g, chain)
        pack_slots, _ = resolve_kit_module.eval_packs(packs, self.CTX, None, {})
        pc = resolve_kit_module.choose_pack(
            slots["roof_pitch"], pack_slots.get("roof_pitch", []), self.CTX)
        chosen = (pc or {}).get("chosen")
        if isinstance(chosen, dict):
            assert "ratio_demoted" not in chosen, (
                "a roof pitch IS a ratio; demoting it would be inventing a referent")


class TestTheDecisionLogCarriesItsStructureWithoutLosingItsProse:
    """OQ 34. The workbench's DecisionLogEntry renders {field, chose, because}; the composer's
    decision log was prose, so the component rendered a shape the data did not have. Ruled 26 Aug
    2026: structure it and mark the judgment. The judgment is which lines are DECISIONS and which
    are narration, and the rule taken is that the log already classifies itself — a line the
    composer meant as a decision carries a prefix it wrote (JUDGMENT, REFUSED, AUTHORED, NOT
    SOLVED, KNOWN FINDING), and everything else is an assumption taken where the brief was silent.
    """

    def test_the_prose_is_unchanged_and_still_first(self, compose_module):
        """`decisions` must keep its exact shape: a list of sentences. Every consumer that read
        it before this change reads it identically after."""
        s = compose_module.structure_decisions(["Ceiling heights 9.0 ft ground and 8.0 ft above, "
                                                "taken from the style's own kit."])
        assert s[0]["statement"] == ("Ceiling heights 9.0 ft ground and 8.0 ft above, taken from "
                                     "the style's own kit.")

    def test_a_prefix_the_composer_wrote_becomes_the_kind(self, compose_module):
        """The corpus's own vocabulary, not a taxonomy imposed on it."""
        cases = {
            "JUDGMENT: the brief requires a library and this diagram has no place for one.": "judgment",
            "AUTHORED: 2 garage bays placed as a dependency off the Mudroom.": "authored",
            "NOT SOLVED: whether an upper-storey room ends up over the garage.": "unsolved",
            "KNOWN FINDING, not a defect: the garage will report a daylight failure.": "disclosure",
            "Ceiling heights 9.0 ft ground and 8.0 ft above.": "assumption",
        }
        for line, kind in cases.items():
            assert compose_module.structure_decisions([line])[0]["kind"] == kind, line

    def test_a_derived_field_says_it_is_derived(self, compose_module):
        """`field` and `chose` are read off the sentence, not authored at the call site, and the
        record says so. A derived value presented as an authored one would be the same class of
        problem as OQ 52's invented measurements, one layer up."""
        s = compose_module.structure_decisions(
            ["Ceiling heights 11.0 ft ground and 10.0 ft above, taken from the style's own kit."])[0]
        assert s["derived"] is True
        assert s["field"] == "ceiling_heights"
        assert "11.0 ft ground" in s["chose"]
        assert "taken from" in s["because"]

    def test_a_sentence_outside_the_table_keeps_null_fields(self, compose_module):
        """Not force-fitted. A wrong derived value is worse than an absent one, and the prose is
        right there — which is why the two disclosure lines in the live corpus keep field: null."""
        s = compose_module.structure_decisions(["Something the table has never seen before."])[0]
        assert s["field"] is None and s["chose"] is None
        assert s["statement"] == "Something the table has never seen before."

    def test_every_live_decision_line_is_classified(self, compose_module):
        """Against the real composer output, not a fixture: every line gets a kind, and the great
        majority get a field. The two that do not are NOT SOLVED and KNOWN FINDING — disclosures
        that settle no brief field, where null is the correct answer."""
        import glob
        briefs = sorted(glob.glob(os.path.join(ROOT, "briefs", "*.json")))
        assert briefs, "no briefs to compose"
        result = compose_module.compose(json.load(open(briefs[0])), candidates=2, revise=True, revise_engine="heuristic", revise_rounds=1)
        rows = [e for c in result["candidates"] for e in c["decisions_structured"]]
        assert rows, "the composer emitted no structured decisions"
        assert all(r["kind"] for r in rows)
        assert all(r["statement"] for r in rows)
        named = [r for r in rows if r["field"]]
        assert len(named) >= 0.8 * len(rows), (
            f"only {len(named)} of {len(rows)} lines matched the decision vocabulary — the "
            "composer's wording has drifted from _DECISION_PATTERNS")


class TestFindingsCarryAStableServerMintedId:
    """OQ 32. The workbench needed to diff findings across a re-evaluation and to cite one, and
    with no id to hand it derived a key client-side from hash(layer|statement|room). That works
    exactly until somebody improves the wording of a finding, at which point every open row,
    every citation and every diff points at nothing, and the UI reports a finding cleared and a
    new one opened when the only thing that changed was an adjective.

    A finding's identity is what it is ABOUT, so the id is built from the layer, the room, and
    the rule or fault id where one exists — never from the sentence.
    """

    @pytest.mark.parametrize("plan_name", REFERENCE_PLANS)
    def test_every_finding_has_a_unique_id(self, plan_name, plan_check_module):
        result = plan_check_module.check(_plan(plan_name))
        ids = [f["id"] for f in result["findings"]]
        assert all(ids), f"{plan_name}: a finding was minted with no id"
        assert len(set(ids)) == len(ids), (
            f"{plan_name}: {len(ids) - len(set(ids))} duplicate finding id(s) — a diff cannot "
            "tell two rows apart")

    @pytest.mark.parametrize("plan_name", REFERENCE_PLANS)
    def test_the_id_does_not_contain_the_statement(self, plan_name, plan_check_module):
        """The whole point. An id that embeds the prose is the bug with extra steps — and it is
        reachable, because `rule` carries an id on some layers and a paragraph of reasoning on
        others, so only an id-shaped value is allowed into the key."""
        result = plan_check_module.check(_plan(plan_name))
        for f in result["findings"]:
            assert len(f["id"]) <= 96, f"finding id looks like prose: {f['id'][:120]}"
            assert f["statement"][:40] not in f["id"]

    def test_the_id_survives_a_reworded_statement(self, plan_check_module):
        """The regression this exists to prevent, stated as a test rather than as a hope."""
        F = plan_check_module.Findings()
        F.add("serious", "room", "Dining Room is too small.", room="dining", rule="area-floor")
        first = F.items[0]["id"]
        G = plan_check_module.Findings()
        G.add("serious", "room", "The dining room falls below its catalogue band.",
              room="dining", rule="area-floor")
        assert G.items[0]["id"] == first, (
            "rewording a finding changed its id — that is exactly the failure OQ 32 records")

    def test_two_findings_in_one_room_and_layer_stay_distinct(self, plan_check_module):
        F = plan_check_module.Findings()
        F.add("minor", "adjacency", "one", room="hall")
        F.add("minor", "adjacency", "two", room="hall")
        assert F.items[0]["id"] != F.items[1]["id"]


class TestACompromiseAppearsOnTheDrawingAtItsLocation:
    """OQ 33, and P7 of the interface standard — the one principle the workbench knowingly did
    not meet. "A compromise is counted AND appears on the drawing, at its location." It was only
    ever counted: the solvers recorded a relaxation as a bare float, so the sheet could print an
    honest tally and had nothing to place a mark with, and `RelaxationMarker` — a component built
    for exactly this — had no data to render. The tally was true and the drawing was silent about
    where the truth applied.
    """

    def test_a_relaxation_carries_where_it_is(self, geometry_module):
        out = geometry_module.solve(_plan("tidewater-georgian-careful"),
                                    engine="heuristic", candidates=250)
        rel = out["geometry_report"]["relaxations"]
        assert rel["count"] > 0, "this plan is known to take cuts off the bay line"
        marks = rel["marks"]
        assert len(marks) == rel["count"], "every counted relaxation must be locatable"
        for m in marks:
            assert m["axis"] in ("x", "y")
            assert isinstance(m["at_ft"], (int, float))
            assert m["off_ft"] > 0
            assert m["level"] in (0, 1)

    def test_the_pinned_relaxation_count_did_not_move(self, geometry_module):
        """The count is exactly the kind of number that must not move BY ACCIDENT. It was 11
        from WP-2.3 until WP-7.1, and a first attempt at positions moved it by testing
        `if round(d, 2)` where the original tested `if d`, swallowing a sub-half-inch miss.

        5, moved from 7 by WP-11.2, and the reason is the BAY GRID rather than the slicer: the plan now names its parti, so the placement takes the diagram's own 9 ft module instead of the placer's 10 ft default, and the massing's `bays: "5"` makes the count odd -- seven bays of 9 ft (63.0 x 38.2) where it was six of 10 (60.0 x 40.1). A cut is a relaxation when it misses the bay module, so changing the module changes which cuts miss. It is a smaller number and it is NOT thereby an improvement in the house: the same change costs about three fatal findings on this engine (8-seed means 6.2 -> 9.2, all unreachable rooms) and zero on CP-SAT. Read `docs/reports/wp-11.2-the-diagram-reaches-the-record.md` before moving it again. Previously: 7, moved from 9 by WP-7.4 -- the span term charges an over-capacity clear span, and the only way the slicer can create a bearing line is to cut ON the bay module -- so a term aimed at structure pulls cuts onto the grid, and a cut on the grid is not a relaxation. Measured on this plan with the two terms off and on: 9 -> 7 here and 7 -> 4 on spec-builder-colonial. It is an improvement and it is still a number that must not move BY ACCIDENT. Previously: 9, moved from 11 by WP-7.1 (OQ 95). The upper level is now sliced against the ground layout instead of blind, so an upper cut lands on a wall below where one is within tolerance — and a cut that lands on a wall below is not a compromise, because a relaxation is defined in geometry.py's own prose as a joist run that does not land on a bearing wall. The code had approximated that as 'misses the bay module', and 18 of 30 ground wall lines are themselves off the bay grid. Measured corpus-wide on 14 composed plans: relaxations 96 -> 76, transfer beams 166 -> 109."""
        out = geometry_module.solve(_plan("tidewater-georgian-careful"),
                                    engine="heuristic", candidates=250)
        # STAYS 7. WP-9.4 measured a corrected clamp (geometry._clamp_cut) that would move it
        # to 8, and REFUSED it: the same change takes the entry porch's clear depth 6.0 -> 5.0
        # and re-fires `porch-nobody-can-sit-on`, which WP-7.4 had cleared. Read _clamp_cut's
        # docstring before trying it again -- the arithmetic there is right and the shipped
        # expression is wrong, and shipping the fix alone still makes the corpus worse.
        assert out["geometry_report"]["relaxations"]["count"] == 5

    def test_the_renderer_draws_one_mark_per_relaxation(self, geometry_module):
        """P6 and P7 together: the drawing is a render of the data, so the number of marks on
        the sheet is the number of relaxations in the record, not a number the renderer chose."""
        import modcache
        rp = modcache.load("render_plan", os.path.join(ROOT, "build", "render_plan.py"))
        out = geometry_module.solve(_plan("tidewater-georgian-careful"),
                                    engine="heuristic", candidates=250)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as fh:
            path = fh.name
        rp.render(out, path)
        svg = open(path).read()
        assert svg.count("ft off the bay line") == out["geometry_report"]["relaxations"]["count"]


class TestAFaultIsNotClearedOnShuttersThatAreNotThere:
    """OQ 89. `elevation.py` published `total_shutter_leaves: 2.0` and
    `shutter_leaves_with_a_leaf_width_of_clear_hinge_side_wall: 2.0` as UNCONDITIONAL constants,
    so `shutter-on-an-unshutterable-opening` read 2/2 = 1.0 and came back CLEAR -- `passes: true`
    -- on `tidewater-georgian`, whose kit makes `none` canonical and whose every window record
    already carried `shutters_carried: False` with its leaf dimensions dropped for exactly that
    reason. A fault cleared on two invented shutters.

    This is OQ 52's class one layer in from where OQ 52's guard can see: nothing was being
    WITHHELD, so `NOT_MODELLED` had no purchase on it -- something was being INVENTED, in
    `_derive_measurements`, beside measurements that are real.

    The three assertions are the three states, and the third is the one that makes the fix a fix
    rather than a suppression: a house that carries shutters must still be judged.
    """

    def test_a_style_whose_kit_forbids_shutters_states_a_measured_zero(self, elevation_mod):
        elev = elevation_mod.build_elevation(_plan("tidewater-georgian-careful"))
        assert elev["storey_windows"][0]["shutters_carried"] is False, (
            "fixture drift: this test needs a style that declines shutters")
        m = elev["measurements"]
        assert m["total_shutter_leaves"] == 0, (
            "a house with no shutters has no shutter leaves, and 2.0 is where OQ 89 came from")
        assert m["shutter_leaves_with_a_leaf_width_of_clear_hinge_side_wall"] == 0

    def test_the_fault_does_not_come_back_clear_on_a_shutterless_house(self, core_module,
                                                                        elevation_mod):
        """The conviction that matters. Before the fix this returned `faults_clear` carrying
        `{"value": 1.0, "passes": true}` -- the strongest possible statement that a house is fine,
        made entirely out of numbers nobody measured."""
        elev = elevation_mod.build_elevation(_plan("tidewater-georgian-careful"))
        r = core_module.check_measurements(elev["measurements"], style="tidewater-georgian", limit=400)
        clear = {row["fault"] for row in (r.get("faults_clear") or []) if isinstance(row, dict)}
        assert "shutter-on-an-unshutterable-opening" not in clear, (
            "the fault is CLEAR again on a house whose kit forbids shutters (OQ 89)")
        na = {row["fault"] for row in (r.get("not_applicable") or []) if isinstance(row, dict)}
        assert "shutter-on-an-unshutterable-opening" in na, (
            "not-applicable is the right answer here and could-not-evaluate is not: the "
            "measurements are present and say zero, so the question does not arise")

    def test_a_style_that_does_carry_shutters_is_still_judged(self, core_module, elevation_mod):
        """A guard that silences the fault everywhere would pass the two assertions above."""
        elev = elevation_mod.build_elevation(_plan("spec-builder-colonial"))
        assert elev["storey_windows"][0]["shutters_carried"] is True
        assert elev["measurements"]["total_shutter_leaves"] == 2.0
        r = core_module.check_measurements(elev["measurements"], style=elev["style"], limit=400)
        rows = [row for row in (r.get("faults_clear") or [])
                if isinstance(row, dict) and row["fault"] == "shutter-on-an-unshutterable-opening"]
        assert rows, "a shuttered house must still be judged, not quietly excused"
        assert any(x.get("status") == "evaluated" for x in rows[0]["results"]), (
            "clear must mean a test RAN and passed, not that every test declined")


class TestSupplyingAMeasurementDoesNotArmAnUnguardedDivision:
    """OQ 89, and the reason its first bullet could not simply be done. `window_head_radius_in` is
    supplied now, computed from the head the record already states. Its guarded twin in
    `secondary_tests` has carried an `applies_when` since WP-5.10 -- but the IDENTICAL expression
    sits in `exceptions[0].bounds_test`, which `check_measurements` SUBSTITUTES for the primary on
    a matching style, and that one carried no guard.

    So supplying the measurement made a latent bug live: on a straight-headed house the radius is
    a measured 0 and the bounds_test divides by it. Proved before it was guarded -- the unguarded
    call returned `{'status': 'error', 'detail': 'float division by zero'}`.

    This is the WP-5.9 lesson and the WP-5.10 audit's Second Empire finding in one place: the
    moment a record can state a zero every rule that presupposed the thing runs on it, and a
    fault's tests live in THREE locations of which `exceptions[].bounds_test` is the one that
    gets missed.
    """

    def test_both_copies_of_the_head_radius_test_are_guarded(self):
        fault = json.load(open(os.path.join(ROOT, "faults",
                                           "shutter-on-an-unshutterable-opening.json")))
        copies = [t for t in fault.get("secondary_tests", [])
                  if t["expression"].startswith("shutter_head_radius_in")]
        copies += [e["bounds_test"] for e in fault.get("exceptions", [])
                   if e.get("bounds_test", {}).get("expression", "").startswith("shutter_head_radius_in")]
        assert len(copies) == 2, "fixture drift: expected the expression in two places"
        for t in copies:
            assert t.get("applies_when"), (
                "one copy of the head-radius test is unguarded. Guarding `secondary_tests` and "
                "not `exceptions[].bounds_test` is exactly the omission the WP-5.10 audit found.")

    def test_the_bounds_test_does_not_error_on_a_straight_headed_house(self, core_module,
                                                                        elevation_mod):
        m = dict(elevation_mod.build_elevation(
            _plan("tidewater-georgian-careful"))["measurements"])
        assert m["window_head_radius_in"] == 0, (
            "fixture drift: this test needs a straight-headed house, which is what a gauged flat "
            "arch is -- brick-course's own rule says its camber is there so the head 'reads "
            "level' and is 'invisible on paper'")
        m["shutter_head_radius_in"] = 12.0          # the partner the corpus does not state
        fault = json.load(open(os.path.join(ROOT, "faults",
                                           "shutter-on-an-unshutterable-opening.json")))
        bt = next(e["bounds_test"] for e in fault["exceptions"]
                  if e.get("bounds_test", {}).get("expression", "").startswith("shutter_head_radius_in"))
        got = core_module._eval_test(bt, m)
        assert got["status"] != "error", f"divides by zero again: {got}"
        assert got["status"] == "not_applicable"

    def test_the_partner_measurement_is_withheld_by_the_mechanism_not_a_comment(self,
                                                                                elevation_mod):
        """`shutter_head_radius_in` is genuinely unknowable here -- nothing in this corpus says
        whether a shutter follows a curved head, which is the very question the fault asks. It
        must be withheld through NOT_MODELLED, where the honesty guard can see it, rather than by
        a source comment that no test reads."""
        assert "shutter_head_radius_in" in elevation_mod.NOT_MODELLED
        m = elevation_mod.build_elevation(
            _plan("tidewater-georgian-careful"))["measurements"]
        assert "shutter_head_radius_in" not in m
