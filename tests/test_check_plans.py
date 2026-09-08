"""WP-11.2 — a plan record against the parti it names, and the bay count the massing states.

Two defects, one package. `plans/tidewater-georgian-careful.json` carried three of its parti's
five `stacks_over` claims and dropped the two that organise its upper floor — the passage over the
passage and the landing over the stair — so `plan_check`'s stacking layer, which reads that field
faithfully, had nothing to read and the sheet drew a landing over the library. Nothing could have
caught it: `compose.py` copies those claims onto every candidate it emits, and NOTHING checked a
plan the composer did not write. Both shipped reference plans are hand-authored.

And `massings/catalog.json`'s `four-over-four` says `bays: "5"`, which no code had ever read, so
the same plan was placed six bays wide — and an even count has no middle bay, which is where a
Georgian door goes.
"""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))

import modcache  # noqa: E402

CP = modcache.load("check_plans", os.path.join(ROOT, "build", "check_plans.py"))
GEO = modcache.load("geometry", os.path.join(ROOT, "build", "geometry.py"))


def tidewater():
    return json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))


def parti(pid="centre-passage-double-pile"):
    return json.load(open(os.path.join(ROOT, "partis", f"{pid}.json")))


# ------------------------------------------------------------------ the record against the parti
class TestThePlanAgainstItsParti:
    def test_the_shipped_plan_names_its_parti(self):
        """The field is the whole mechanism: without it there is nothing to check against, and
        the plan is silent about the diagram it is an instance of."""
        assert tidewater().get("parti") == "centre-passage-double-pile"

    def test_the_two_stacking_claims_that_organise_the_floor_are_in_the_record(self):
        rooms = CP.rooms_of(tidewater())
        assert rooms["upperpassage"].get("stacks_over") == "passage"
        assert rooms["landing"].get("stacks_over") == "stair"

    def test_a_dropped_stacks_over_is_a_finding(self):
        """The defect, reproduced: remove one claim and the checker must name it. This is the
        assertion that would have caught the shipped record."""
        plan = tidewater()
        for lv in plan["levels"]:
            for r in lv["rooms"]:
                if r["id"] == "upperpassage":
                    r.pop("stacks_over", None)
        found = CP.check_plan(plan, parti())
        assert any(f["kind"] == "stacks-over" and f["room"] == "upperpassage" for f in found)

    def test_the_shipped_plan_has_no_topology_finding_left(self):
        hard = [f for f in CP.check_plan(tidewater(), parti())
                if f["kind"] not in CP.REPORTED]
        assert hard == [], f"a topology finding on a shipped plan: {hard}"

    def test_exposure_disagreements_are_reported_and_not_failed(self):
        """A parti states TOPOLOGY and roles, never massing (decision #3), and
        `exterior_walls` speaks exposure in the fully-massed house. The Tidewater record's back
        hall is a hyphen and its kitchen a dependency; the parti has neither. Erasing that to
        quieten a checker would delete the record's own account of the house."""
        found = CP.check_plan(tidewater(), parti())
        exposure = [f for f in found if f["kind"] == "exterior-walls"]
        assert {f["room"] for f in exposure} == {"backhall", "kitchen"}
        assert len(exposure) <= CP.EXPOSURE_CEILING

    def test_a_missing_room_the_parti_requires_is_a_finding(self):
        plan = tidewater()
        plan["levels"][0]["rooms"] = [r for r in plan["levels"][0]["rooms"] if r["id"] != "stair"]
        found = CP.check_plan(plan, parti())
        assert any(f["kind"] == "missing-room" and f["room"] == "stair" for f in found)

    def test_an_optional_room_the_plan_omits_is_not_a_finding(self):
        """`library` and `breakfast` carry `required: false`. A diagram is a skeleton, not a
        census, and a checker that demanded every optional room would refuse a smaller house."""
        plan = tidewater()
        for lv in plan["levels"]:
            lv["rooms"] = [r for r in lv["rooms"] if r["id"] != "library"]
        found = CP.check_plan(plan, parti())
        assert not any(f["room"] == "library" for f in found)

    def test_a_repeating_template_room_is_never_missing(self):
        """`chamber` and `chambercl` carry `repeats_with_bedrooms`; the composer instantiates
        them as chamber2, chamber3 …, so the parti's own id is never in a plan and its absence
        would be a finding on every plan of this diagram."""
        found = CP.check_plan(tidewater(), parti())
        assert not any(f["room"] in ("chamber", "chambercl") for f in found)

    def test_a_style_the_parti_does_not_name_is_a_finding(self):
        plan = tidewater()
        plan["style"] = "shotgun-house"
        assert any(f["kind"] == "style" for f in CP.check_plan(plan, parti()))

    def test_a_plan_naming_no_parti_is_unjudged_and_not_clean(self):
        """The finding this file exists for was a record that said nothing. A checker that read
        silence as agreement would reproduce it."""
        import subprocess
        out = subprocess.run([sys.executable, os.path.join(ROOT, "build", "check_plans.py")],
                             capture_output=True, text=True, cwd=ROOT)
        assert "UNJUDGED" in out.stdout
        assert "unjudged." in out.stdout


# ------------------------------------------------------------------ the bay count
class TestTheMassingsBayCount:
    def test_the_massing_bays_reader_takes_only_what_it_is_sure_of(self):
        assert GEO.massing_bays({"bays": "5"}) == {"stated": "5", "readable": True,
                                                   "min": 5, "max": 5}
        assert GEO.massing_bays({"bays": "3-5"})["readable"] is True
        assert GEO.massing_bays({"bays": "3-5"})["max"] == 5
        for prose in ("variable", "irregular", "1 per face", "3 (narrow end to street)",
                      "5-7 main", "2-3 + 2-3"):
            assert GEO.massing_bays({"bays": prose})["readable"] is False, prose
        assert GEO.massing_bays({})["readable"] is False

    def test_a_trailing_word_is_refused_rather_than_guessed(self):
        """`5-7 main` means the MAIN BLOCK of a multi-element house, and a reader that dropped
        the word would state a fact about the wrong thing."""
        mb = GEO.massing_bays({"bays": "5-7 main"})
        assert mb["readable"] is False and mb["stated"] == "5-7 main"

    def test_a_centre_hall_diagram_wants_an_odd_count(self):
        want, why = GEO.wants_a_centre_bay({}, parti(), {"bays": "5"})
        assert want and "5 bays" in why

    def test_the_massings_own_count_outranks_the_circulation_type(self):
        """Two signals and the massing's stated count is the stronger: it is a fact about this
        record's massing, not an inference from its circulation type."""
        _, why = GEO.wants_a_centre_bay({}, parti(), {"bays": "5"})
        assert "massing states" in why

    def test_a_diagram_with_neither_signal_wants_nothing(self):
        want, why = GEO.wants_a_centre_bay({}, {"circulation_parti": "side-hall"},
                                           {"bays": "variable"})
        assert want is False and why is None

    def test_the_shipped_plan_is_placed_on_an_odd_bay_count(self):
        """The sheet Lucas read said SIX bays under a title that says five. An even count has
        no middle bay, so the type's one non-negotiable move — the door in the centre with two
        windows either side — was unavailable before a room was placed."""
        fp = GEO.derive_footprint(tidewater())
        assert fp["bays"] % 2 == 1, f'{fp["bays"]} bays has no centre bay'
        assert fp["wants_centre_bay"] is True
        assert fp["bay_count_forced_even"] is False

    def test_the_partis_own_module_reaches_the_placement(self):
        """`centre-passage-double-pile` states a 9 ft module and every sheet of it was drawn on
        the placer's 10 ft default, because the only route in was a caller passing the parti
        separately and the CLI, the bench's drawing route and both shipped plans all did not."""
        assert GEO.derive_footprint(tidewater())["bay"] == 9

    def test_the_massings_stated_count_is_a_floor_a_small_program_cannot_fall_below(self):
        """AND THE MUTATION THAT FOUND THIS TEST MISSING. Deleting the massing-count reader
        entirely left every assertion in this file green, because on the shipped plan the area
        arithmetic already returns seven and the floor is inert. A reader that never binds is a
        reader nobody can tell is there.

        It binds on a SMALLER program: at 40% of the Tidewater plan's room lengths the area
        arithmetic asks for three bays, and `four-over-four` says five. A three-bay
        four-over-four is not the massing, whatever its area."""
        plan = tidewater()
        for lv in plan["levels"]:
            for r in lv["rooms"]:
                if r.get("width_ft") and r.get("length_ft"):
                    r["length_ft"] = round(r["length_ft"] * 0.4, 2)
        fp = GEO.derive_footprint(plan)
        assert fp["massing_bays"] == "5" and fp["massing_bays_readable"] is True
        assert fp["bays"] == 5, "the massing says five bays and the area asked for three"

    def test_a_plan_naming_no_parti_still_places_on_the_default(self):
        plan = tidewater()
        plan.pop("parti", None)
        assert GEO.derive_footprint(plan)["bay"] == 10.0

    def test_growth_steps_by_two_where_a_centre_bay_is_wanted(self):
        """A five-bay house that will not fit becomes seven and never six.

        THE FIRST VERSION OF THIS TEST WAS VACUOUS AND A MUTATION FOUND IT. It asserted that
        every count in `grown` is odd — and `grown` is EMPTY on the shipped plan, whose starting
        count already satisfies the depth test, so `all(... for b in [])` is True and the test
        passed with the step forced back to 1. A fixture that never enters the loop cannot test
        the loop, so this one enlarges the program until it must grow, and asserts the loop ran
        before asserting anything about what it did."""
        plan = tidewater()
        for lv in plan["levels"]:
            for r in lv["rooms"]:
                if r.get("width_ft") and r.get("length_ft"):
                    r["length_ft"] = round(r["length_ft"] * 1.9, 2)
        fp = GEO.derive_footprint(plan)
        assert fp["grown"], "the fixture is blind: the growth loop never ran"
        assert all(b % 2 == 1 for b in fp["grown"]), fp["grown"]
        assert fp["bays"] % 2 == 1

    def test_growth_steps_by_one_where_no_centre_bay_is_wanted(self):
        """The other half: a diagram with no centre-bay claim keeps the single-bay step, so
        this package changed the growth of exactly the diagrams that asked for it."""
        plan = tidewater()
        plan.pop("parti", None)
        plan["massing"] = "gable-front"          # `bays: "2-3"`, no centre-hall parti passed
        for lv in plan["levels"]:
            for r in lv["rooms"]:
                if r.get("width_ft") and r.get("length_ft"):
                    r["length_ft"] = round(r["length_ft"] * 1.9, 2)
        fp = GEO.derive_footprint(plan)
        assert fp["wants_centre_bay"] is False
        assert fp["grown"], "the fixture is blind: the growth loop never ran"
        steps = {b - a for a, b in zip([fp["grown"][0] - 1] + fp["grown"], fp["grown"])}
        assert steps == {1}, fp["grown"]

    def test_the_parti_is_resolved_through_the_confined_loader(self, monkeypatch):
        """An id in a plan record is caller-supplied exactly as a POST body's is — the bench
        posts plan records — and this repository keeps that join in ONE place. A fourth copy is
        what `workbench/server/tests/test_parti_confinement.py` exists to refuse."""
        core = modcache.load("tdlcore", os.path.join(ROOT, "mcp_server", "core.py"))
        seen = []
        real = core.load_parti

        def spy(pid):
            seen.append(pid)
            return real(pid)

        monkeypatch.setattr(core, "load_parti", spy)
        GEO.parti_for(tidewater())
        assert seen == ["centre-passage-double-pile"]

    def test_a_traversal_in_the_record_reaches_nothing(self):
        plan = tidewater()
        plan["parti"] = "../schema/plan.schema"
        assert GEO.parti_for(plan) is None

    def test_a_caller_supplied_parti_still_wins(self):
        """The record NAMES a diagram; a caller may still place it against another, which is
        what the composer does when it offers candidates on contrasting partis."""
        other = parti("side-hall-townhouse")
        assert GEO.parti_for(tidewater(), other) is other
