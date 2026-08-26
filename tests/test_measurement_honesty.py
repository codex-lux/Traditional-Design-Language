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
    @pytest.mark.parametrize("plan_name", REFERENCE_PLANS)
    def test_they_come_back_could_not_judge(self, plan_name, plan_check_module):
        """Not present, not clear — unjudged. This is the whole point: the corpus does not know
        whether these houses have dormers, gutters, a raking cornice or a stack of a given plan
        size, and it must now say so instead of deciding."""
        result = plan_check_module.check(_plan(plan_name))
        unjudged = {r.get("fault") for r in (result.get("fault_unjudged") or [])}
        for fault_id in FABRICATED_SEVEN:
            assert fault_id in unjudged, (
                f"{plan_name}: '{fault_id}' is being adjudicated again. It can only be judged "
                "from a measurement no generator in this corpus takes (OQ 52).")

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
        pack_slots, _ = rk.eval_packs(rk.resolve_packs(g, chain), self.CTX, None)
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
        pack_slots, _ = resolve_kit_module.eval_packs(packs, self.CTX, None)
        pc = resolve_kit_module.choose_pack(
            slots["roof_pitch"], pack_slots.get("roof_pitch", []), self.CTX)
        chosen = (pc or {}).get("chosen")
        if isinstance(chosen, dict):
            assert "ratio_demoted" not in chosen, (
                "a roof pitch IS a ratio; demoting it would be inventing a referent")
