"""WP-11.7 — the facade as a RESULT (`oq/the-facade-is-a-result-not-an-input`, ruled 4 Sep 2026).

The bay rhythm follows the plan's organising move; it is derived from `footprint.bays` and
compared against what the front carries, and the difference is REPORTED. Nothing here composes a
facade, and that is the ruling's own trap written down: *"a derived facade is a facade the
generator can be WRONG about with confidence ... the window that gets invented to complete a
rhythm is this ruling's version of the invented measurement OQ 52 swept out of the elevation."*

So the tests come in two halves. The first holds what the layer DERIVES; the second holds what it
must never do — invent a bay, overwrite a declared count, or pass where it cannot judge.
"""
import copy
import glob
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))

import modcache  # noqa: E402

GEO = modcache.load("geometry", os.path.join(ROOT, "build", "geometry.py"))
FA = modcache.load("facade", os.path.join(ROOT, "build", "facade.py"))
PC = modcache.load("plan_check", os.path.join(ROOT, "build", "plan_check.py"))


def _placed(name="tidewater-georgian-careful"):
    GEO._SOLVE_CACHE.clear()
    p = json.load(open(os.path.join(ROOT, "plans", f"{name}.json")))
    return GEO.solve(p, engine="heuristic")


@pytest.fixture(scope="module")
def tidewater():
    return _placed()


class TestTheRhythmIsDerivedFromThePlansOwnBays:
    def test_every_bay_is_traceable_to_footprint_bays(self, tidewater):
        """The ruling's own condition: *"every bay it states must be traceable to a bay the plan
        states."* The count is the plan's, not a pack formula's — which is the whole inversion.
        `elevation._face_bays` derives an odd count from `facade-classical.json`'s
        `window_grouping_rule` against the face's outside width and never reads this number."""
        r = FA.rhythm(tidewater)
        assert r["verdict"] == "derived", r
        assert len(r["bays_out"]) == tidewater["footprint"]["bays"] == r["bays"]
        assert r["centre_bay"] == r["bays"] // 2
        assert [b["bay"] for b in r["bays_out"]] == list(range(r["bays"]))

    def test_the_door_is_in_the_middle_bay_and_only_there(self, tidewater):
        r = FA.rhythm(tidewater)
        kinds = [b["kind"] for b in r["bays_out"]]
        assert kinds.count("door") == 1, kinds
        assert kinds[r["centre_bay"]] == "door"

    def test_the_bay_centres_span_the_blocks_own_width(self, tidewater):
        r = FA.rhythm(tidewater)
        W = tidewater["footprint"]["width_ft"]
        assert abs(r["realised_bay_width_ft"] * r["bays"] - W) < 0.01
        assert 0 < r["bays_out"][0]["centre_ft"] < r["bays_out"][-1]["centre_ft"] < W


class TestItRefusesRatherThanComposingSomethingPlausible:
    """Five stated grounds, each naming what a reader would have to author. A refusal whose one
    message serves several causes has stopped being a refusal (WP-11.4)."""

    def test_a_plan_that_names_no_parti(self):
        p = _placed()
        p.pop("parti", None)
        r = FA.rhythm(p)
        assert r["verdict"] == "could-not-evaluate"
        assert "names no parti" in r["why"], r["why"]

    def test_a_diagram_that_is_not_a_centre_door_one_IS_NAMED(self, monkeypatch):
        """The ruling is stated for `center-hall` and says the generalisation is NOT made. The
        refusal must name the parti it declined — "side-hall is not center-hall" is a useful
        sentence and "not applicable" is not."""
        p = _placed()
        monkeypatch.setattr(FA, "circulation_parti", lambda plan, C=None: ("side-hall", None))
        r = FA.rhythm(p)
        assert r["verdict"] == "could-not-evaluate"
        assert "side-hall" in r["why"] and "center-hall" in r["why"], r["why"]
        assert "that parti's own to state" in r["why"], r["why"]

    def test_an_even_bay_count_is_a_refusal_and_not_a_pass(self):
        p = _placed()
        p["footprint"]["bays"] = 6
        r = FA.rhythm(p)
        assert r["verdict"] == "could-not-evaluate"
        assert "even count" in r["why"] and "no middle bay" in r["why"], r["why"]

    def test_no_bay_count_and_no_module_give_DIFFERENT_reasons(self):
        p = _placed()
        p["footprint"].pop("bays", None)
        assert "bay count" in FA.rhythm(p)["why"]
        q = _placed()
        q["footprint"].pop("bay_module_ft", None)
        assert "bay module" in FA.rhythm(q)["why"]

    def test_FIFTEEN_OF_SIXTEEN_PLAN_RECORDS_NAME_NO_PARTI(self):
        """The disclosure, measured rather than asserted, and the sibling of WP-11.4's
        `oq/fourteen-of-sixteen-plans-name-no-massing`. The layer is SILENT on 94% of this
        corpus, and silence has to be countable or it reads as agreement."""
        derived, refused = [], []
        for f in sorted(glob.glob(os.path.join(ROOT, "plans", "**", "*.json"), recursive=True)):
            plan = json.load(open(f))
            if "levels" not in plan:
                continue
            GEO._SOLVE_CACHE.clear()
            out = GEO.solve(plan, engine="heuristic")
            (derived if FA.rhythm(out)["verdict"] == "derived" else refused).append(
                os.path.basename(f))
        assert len(derived) == 1 and derived == ["tidewater-georgian-careful.json"], derived
        assert len(refused) == 15, refused


class TestItReportsAndNeverWrites:
    def test_check_does_not_touch_a_single_declared_window_count(self, tidewater):
        """WP-6.2's rule stands: *"the DECLARED count is still never overwritten ... where the two
        disagree the record says so, which is a finding and not a silent correction."* Six rooms
        on this plan disagree with the rhythm; not one of their records may move."""
        before = copy.deepcopy(tidewater)
        PC.check(tidewater)
        for lv_b, lv_a in zip(before["levels"], tidewater["levels"]):
            for rb, ra in zip(lv_b["rooms"], lv_a["rooms"]):
                assert [w.get("count") for w in (rb.get("windows") or [])] == \
                       [w.get("count") for w in (ra.get("windows") or [])], rb["id"]

    def test_the_disagreements_are_REAL_on_this_plan(self, tidewater):
        """The control for the test above: if nothing disagreed it would pass vacuously."""
        d = FA.room_front_bays(tidewater, 1)
        assert d["verdict"] == "read"
        by = {x["room"]: x for x in d["rooms"]}
        # a room with two bays of front wall and no window declared on it at all
        assert by["chamber2"]["bays"] == [4, 5] and by["chamber2"]["declares"] == 0
        assert by["chamber2"]["agrees"] is False
        # ...and a room that agrees, so the reading is not simply convicting everything
        assert by["primary"]["agrees"] is True, by["primary"]

    def test_a_room_spanning_NO_bay_is_its_own_state_and_not_an_agreement(self, tidewater):
        """`wants 0, declares 0, agrees` would be a trivial pass hiding a room whose front wall
        the rhythm cannot account for. `agrees` is None there and `spans_no_bay` says why."""
        d = FA.room_front_bays(tidewater, 0)
        none_ = [x for x in d["rooms"] if x["spans_no_bay"]]
        assert none_, [x["room"] for x in d["rooms"]]
        for x in none_:
            assert x["agrees"] is None and x["bays"] == [], x
        assert all(x["room"] not in {y["room"] for y in d["disagreements"]} or x["agrees"] is False
                   for x in none_)

    def test_an_empty_bay_is_reported_and_never_filled(self, tidewater):
        c = FA.compare(tidewater, 0)
        empty = [f for f in c["findings"] if f["kind"] == "front-bay-with-no-opening"]
        assert empty, c
        for f in empty:
            assert "NOT a" in f["statement"] and "instruction to add a window" in f["statement"]

    def test_the_door_finding_is_emitted_ONCE_across_the_whole_critic(self, tidewater):
        """It was emitted twice for one commit — WP-11.3's axis layer owns this question and the
        first draft of `facade.compare` added a second, in ZERO-based numbering against the
        existing one-based, so a sheet would have given one door two bay numbers. It was invisible
        in the totals because the inverted facade-share test removed a `serious` at the same time
        and 63 stayed 63."""
        c = PC.check(tidewater)
        door = [f for f in c["findings"]
                if "centre bay" in (f.get("statement") or "")
                or "centre-bay" in (f.get("kind") or "")]
        assert len(door) == 1, [(f.get("kind"), f["statement"][:60]) for f in door]
        assert door[0]["kind"] == "drawn-door-off-the-centre-bay", door[0]


class TestTheDataTheRulingCommittedTo:
    def test_the_facade_share_rule_is_a_REPORT_and_no_longer_a_HARD_TEST(self):
        """The ruling's first commitment and *"the one place the ruling makes a currently-
        executable rule less executable, and it is deliberate"*. Sizing the passage FROM the
        facade is backwards; the passage takes a bay and its share follows."""
        g = json.load(open(os.path.join(ROOT, "groupings", "centre-passage-core.json")))
        rule = [r for r in g["internal_rules"]
                if (r.get("measures") or {}).get("quantity") == "passage_width_to_facade_width"]
        assert len(rule) == 1, rule
        r = rule[0]
        assert "test" not in r, "the share is reported, not required"
        assert r["severity"] != "hard", r["severity"]
        assert r["measures"]["advisory_band"] == [0.18, 0.27]
        assert "CONSEQUENCE" in r["statement"] and "reported rather than required" in r["statement"]
        # and the 8 ft floor is a DIFFERENT rule and stays executable
        floor = [x for x in g["internal_rules"]
                 if (x.get("test") or "").startswith("passage_width_ft between")]
        assert floor and floor[0]["severity"] == "hard", floor

    def test_the_fault_no_longer_tells_the_reader_to_size_from_the_facade(self):
        f = json.load(open(os.path.join(ROOT, "faults",
                                        "passage-that-is-a-corridor.json")))
        cp = f["correct_practice"]
        assert not cp.startswith("Size the passage from the facade")
        assert cp.startswith("Take the passage's width from the BAY")
        assert "runs the dependency backwards" in cp
        # the observation itself is kept -- the ruling calls it real
        assert "fifth to a quarter" in cp

    def test_the_share_is_reported_with_its_band_as_an_advisory(self, tidewater):
        s = FA.facade_share(tidewater)
        assert s["verdict"] == "reported"
        assert s["advisory_band"] == [0.18, 0.27]
        # this plan is OUTSIDE the band, and that is now a report rather than a conviction
        assert s["within_advisory"] is False and s["share"] < 0.18, s
        assert "not required" in s["note"]


class TestTheCriticCarriesIt:
    def test_a_plan_that_cannot_be_judged_says_so_as_INFO_and_never_passes(self):
        out = _placed("spec-builder-colonial")
        c = PC.check(out)
        rows = [f for f in c["findings"] if f.get("kind") == "facade-rhythm-unjudged"]
        assert len(rows) == 1, rows
        assert rows[0]["severity"] == "info"
        assert "Not a pass" in rows[0]["statement"]

    def test_the_findings_land_on_the_DRAWN_layer(self, tidewater):
        """Everything here reads the placement, so it belongs to the only layer permitted to
        (OQ 54) — and `drawn` is already mapped in `compose.SCORE_LAYERS`, which is what WP-11.4
        pushed without doing."""
        c = PC.check(tidewater)
        rows = [f for f in c["findings"] if (f.get("kind") or "").startswith("front-")]
        assert rows
        assert {f.get("layer") for f in rows} == {"drawn"}, {f.get("layer") for f in rows}


EL = modcache.load("elevation", os.path.join(ROOT, "build", "elevation.py"))


class TestTheElevationReadsThePlansBayCount:
    """Item 3 of the ruling — *"the bay rhythm becomes derived"* — at the layer that DRAWS it.

    `_face_bays` took its count from `facade-classical.json`'s `window_grouping_rule` against the
    face's outside width and had never read `footprint.bays`. **The two agree on both shipped
    plans** (7 against 7, 5 against 5), which is why nothing noticed and why this change is
    byte-identical on the corpus: it removes the second rule rather than giving a new answer. It
    is OQ 85's shape exactly — two records built from different rules with nothing comparing them
    — four hundred lines from where OQ 85 itself was fixed."""

    def test_the_front_and_rear_take_the_plans_count_and_say_so(self, tidewater):
        e = EL.build_elevation(tidewater)
        for f in ("S", "N"):
            assert e["faces"][f]["count_from_the_plan"] is True, e["faces"][f]
            assert e["faces"][f]["count"] == tidewater["footprint"]["bays"]
            assert "the PLAN's own footprint.bays" in e["faces"][f]["note"]

    def test_a_GABLE_END_does_not_because_its_span_is_the_depth(self, tidewater):
        """`footprint.bays` counts bays across the WIDTH. Handing it to a face spanning the depth
        would be the OQ 48 error in a new place — one number meaning two quantities."""
        e = EL.build_elevation(tidewater)
        for f in ("E", "W"):
            assert e["faces"][f]["count_from_the_plan"] is False, e["faces"][f]
            assert e["faces"][f]["count"] != tidewater["footprint"]["bays"]

    def test_a_plan_the_facade_layer_REFUSES_keeps_the_pack_formula(self):
        """Fifteen of sixteen records name no parti. The formula stays their reader, and the
        facade layer says the rhythm is unjudged rather than this quietly asserting one."""
        out = _placed("spec-builder-colonial")
        e = EL.build_elevation(out)
        assert all(e["faces"][f]["count_from_the_plan"] is False for f in "SNEW")
        assert FA.rhythm(out)["verdict"] == "could-not-evaluate"

    def test_DRIVEN_the_elevation_FOLLOWS_the_plan_when_the_two_would_disagree(self):
        """**The guard that matters, and the corpus cannot supply it**: the pack formula and the
        plan agree on both shipped plans, so a mutation deleting this join leaves every assertion
        above green (measured — 7 and 5 either way). Driving the plan to a bay count the formula
        would never pick is the only way to see the join at all. WP-8.11's rule."""
        out = _placed()
        formula_count = EL.build_elevation(out)["faces"]["S"]["count"]
        assert formula_count == out["footprint"]["bays"] == 7
        out["footprint"]["bays"] = 9
        e = EL.build_elevation(out)
        assert e["faces"]["S"]["count"] == 9, (
            "the front did not follow the plan's bay count — the elevation is composing its own")
        assert e["faces"]["S"]["kinds"][4] == "door", e["faces"]["S"]["kinds"]
        assert e["faces"]["E"]["count"] == 3, "the gable end must not follow the width's count"


class TestTheBandIsSpelledONCE:
    """Found by `check_rooms.py` rejecting the schema change, and the code half fell out of
    chasing it: `facade_share` had `[0.18, 0.27]` written into it beside the grouping rule that
    states the same pair — one rule in two places, committed inside the package whose subject is
    one rule in two places."""

    def test_the_reader_takes_the_band_from_the_grouping_record(self, tidewater):
        g = json.load(open(os.path.join(ROOT, "groupings", "centre-passage-core.json")))
        rule = next(r for r in g["internal_rules"]
                    if (r.get("measures") or {}).get("quantity") == "passage_width_to_facade_width")
        assert FA.facade_share(tidewater)["advisory_band"] == rule["measures"]["advisory_band"]

    def test_MOVING_the_record_moves_the_reader(self, tidewater, monkeypatch):
        """The control. Both sides reading a hardcoded `[0.18, 0.27]` would pass the test above
        for the wrong reason, which is this repository's own most-repeated shape of blind guard."""
        monkeypatch.setattr(FA, "_advisory_band", lambda *a, **k: [0.10, 0.20])
        s = FA.facade_share(tidewater)
        assert s["advisory_band"] == [0.10, 0.20]
        # this plan's share is 0.1359: OUTSIDE the record's own band and INSIDE the moved one, so
        # the verdict flips with the band. Both halves matter -- a band the reader ignored would
        # leave the verdict where it was.
        assert s["within_advisory"] is True, s

    def test_an_unreadable_band_reports_None_and_never_a_default(self, tidewater, monkeypatch):
        monkeypatch.setattr(FA, "_advisory_band", lambda *a, **k: None)
        s = FA.facade_share(tidewater)
        assert s["advisory_band"] is None
        assert s["within_advisory"] is None, "a share judged against a band nobody could read"
        assert s["advisory_band_source"] == "COULD NOT BE READ"

    def test_no_second_transcription_of_the_band_in_the_tree(self):
        """A source-reading guard, in the shape `test_parti_confinement.py` uses for the parti
        join. **The first version of this test was a bad instrument and is worth recording**: it
        flagged any file containing both "0.18" and "0.27" anywhere, which matched three unrelated
        files' own constants and `facade.py`'s own PROSE about the band. A crude meter that
        convicts prose is the shape `check_grouping_rules.py`'s own note warns about, met while
        writing a guard against a different defect.

        The transcription this is actually about has a shape: the band written as a literal pair
        in code. That is what is searched for."""
        import glob
        import re
        pat = re.compile(r"\[\s*0\.18\s*,\s*0\.27\s*\]")
        hits = [os.path.basename(f) for f in glob.glob(os.path.join(ROOT, "build", "*.py"))
                if pat.search(open(f).read())]
        assert hits == [], hits
