"""WP-11.9 — the aspect sixty records state and nothing read.

Three things are guarded here and they fail on different mutations, which is why all three exist:
the ARITHMETIC of plan north and the sector match; the AUTHORED readings, held against the prose
they quote; and the CHECK, driven on fixtures rather than read off the shipped corpus, because a
fixture that is accidentally the shipped corpus is a statement about this tree and not about the
rule (WP-8.11, and it has bitten this repository twice).
"""
import copy
import glob
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(name, path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


CMP = _load("compass", f"{ROOT}/build/compass.py")
PC = _load("plan_check", f"{ROOT}/build/plan_check.py")


# --------------------------------------------------------------- plan north
class TestPlanNorth:
    def test_no_bearing_means_plan_north_is_true_north(self):
        n = CMP.plan_north({})
        assert n["bearing_deg"] == 0.0
        assert n["stated"] is False
        # THE RULING'S COST. The convention is only honest if the reader is told it was applied.
        assert "true-N" in n["why"]
        assert "street_bearing_deg" in n["why"]

    def test_a_stated_bearing_turns_the_plan(self):
        # front on plan-S, and that front faces due west on the ground: the plan is turned 90.
        n = CMP.plan_north({"site": {"street_bearing_deg": 270},
                            "context": {"entrance_faces": "S"}})
        assert n["bearing_deg"] == 90.0
        assert n["stated"] is True
        assert CMP.face_token("S", n) == "W"
        assert CMP.face_token("N", n) == "E"

    def test_a_bearing_with_no_front_is_unjudged_and_not_the_default(self):
        # Taking axis.DEFAULT_FRONT here would rotate a real house by whatever the difference
        # happened to be, silently. The whole compass block reports could-not-evaluate instead.
        n = CMP.plan_north({"site": {"street_bearing_deg": 270}})
        assert n["bearing_deg"] is None
        assert CMP.face_bearing("S", n) is None
        assert CMP.read({"applies": True, "prefer": ["N"], "basis": "x"},
                        ["S"], n)["verdict"] == "unjudged"

    def test_the_sector_is_the_eight_point_compass(self):
        n = CMP.plan_north({})
        assert CMP.matches("S", "S", n)
        assert not CMP.matches("S", "SE", n)
        # a 45 degree turn puts plan-S on SW exactly, and it is SW rather than S or W
        n45 = CMP.plan_north({"site": {"street_bearing_deg": 225},
                              "context": {"entrance_faces": "S"}})
        assert CMP.face_token("S", n45) == "SW"
        assert CMP.matches("S", "SW", n45)
        assert not CMP.matches("S", "S", n45)


# ----------------------------------------------------------- the authored readings
@pytest.fixture(scope="module")
def rooms():
    out = {}
    for p in sorted(glob.glob(f"{ROOT}/rooms/*.json")):
        d = json.loads(open(p).read())
        out[d["id"]] = d
    return out


class TestTheAuthoredReadings:
    def test_every_room_record_has_been_read(self, rooms):
        # The finding of the package: all sixty state an aspect in words. A record that grows a
        # new `orientation` without an `aspect` beside it is unjudged, and this says so loudly.
        unread = sorted(rid for rid, d in rooms.items()
                        if (d.get("daylight") or {}).get("orientation")
                        and not (d.get("daylight") or {}).get("aspect"))
        assert unread == [], f"orientation prose with no aspect beside it: {unread}"

    def test_every_basis_is_verbatim_in_the_prose_it_claims_to_read(self, rooms):
        for rid, d in rooms.items():
            a = (d.get("daylight") or {}).get("aspect")
            if not a:
                continue
            assert a["basis"] in d["daylight"]["orientation"], rid

    def test_a_refusal_carries_its_reason_or_is_self_explaining(self, rooms):
        # A refusal's value is its reason (WP-11.4). "Any" and "None" explain themselves; every
        # other declining record has to say what it answered with instead.
        for rid, d in rooms.items():
            a = (d.get("daylight") or {}).get("aspect")
            if not a or a["applies"]:
                continue
            assert a.get("note"), f"{rid} declines the compass and says nothing about why"

    def test_the_split_is_the_published_one(self, rooms):
        # Sixty read: 35 state an aspect, 5 of those hard, 25 answer with something that is not a
        # compass. A number in a report is worth what a test holds it to.
        asp = [(d.get("daylight") or {}).get("aspect") for d in rooms.values()]
        asp = [a for a in asp if a]
        assert len(asp) == 60
        assert sum(1 for a in asp if a["applies"]) == 35
        assert sum(1 for a in asp if a.get("strength") == "hard") == 5
        assert sum(1 for a in asp if not a["applies"]) == 25

    def test_prefer_and_avoid_never_name_the_same_aspect(self, rooms):
        for rid, d in rooms.items():
            a = (d.get("daylight") or {}).get("aspect") or {}
            both = set(a.get("prefer") or []) & set(a.get("avoid") or [])
            assert not both, f"{rid} wants and avoids {sorted(both)}"

    def test_a_declining_record_carries_no_reading(self, rooms):
        for rid, d in rooms.items():
            a = (d.get("daylight") or {}).get("aspect") or {}
            if a and not a.get("applies"):
                assert not a.get("prefer") and not a.get("avoid") and not a.get("strength"), rid

    def test_the_four_the_diagnosis_named(self, rooms):
        # Part VI's four compass rules, by name, so a later edit that quietly drops one is caught.
        assert rooms["library"]["daylight"]["aspect"]["prefer"] == ["N", "NE"]
        assert rooms["kitchen"]["daylight"]["aspect"]["avoid"] == ["W"]
        assert rooms["drawing-room"]["daylight"]["aspect"]["prefer"] == ["S", "W"]
        assert rooms["walk-in-closet"]["daylight"]["aspect"]["avoid"] == ["S", "W"]


# ------------------------------------------------------------------- the reading
def _plan(room_type, walls, **kw):
    """A DRIVEN fixture. Deliberately not a shipped plan: a fixture that is the corpus makes
    every assertion below a statement about this tree rather than about the rule."""
    p = {"id": "compass-fixture", "name": "Compass Fixture", "style": "tidewater-georgian",
         "context": {"climate_zone": "3A"},
         "levels": [{"level": 0, "floor_to_ceiling_ft": 10, "rooms": [
             {"id": "r1", "type": room_type, "name": "Test Room",
              "width_ft": 14, "length_ft": 16,
              "windows": [{"wall": w, "count": 1} for w in walls],
              "doors": [{"to": "exterior", "width_ft": 3}]},
         ]}]}
    p.update(kw)
    return p


# THE TWO KINDS BY NAME, NOT BY PREFIX (audit, 7 Sep 2026). This read
# `str(kind).startswith("room-o")`, which happens to select exactly these two today and is a
# prefix over an OPEN namespace: `room-without-a-hearth` misses by one letter and any future
# `room-over-*` kind would silently join every count in `TestTheCheck`.
ASPECT_KINDS = ("room-off-the-aspect-its-record-wants", "room-on-an-aspect-its-record-avoids")


def _kinds(plan):
    return [f for f in PC.check(plan)["findings"] if f.get("kind") in ASPECT_KINDS]


class TestTheCheck:
    def test_a_south_library_is_convicted_and_says_so(self):
        f = _kinds(_plan("library", ["S"]))
        assert len(f) == 1
        assert f[0]["kind"] == "room-on-an-aspect-its-record-avoids"
        assert f[0]["severity"] == "minor"           # the library's NORTH is shouted and licensed
        assert "plan-S is S" in f[0]["statement"]

    def test_a_north_library_is_clear(self):
        """AND THE CENSUS IS READ, because `== []` alone cannot fail (audit, 7 Sep 2026).

        Every mutation that silences the aspect block yields `[]` for every plan, so a bare
        empty-list assertion passes on the checker being deleted. Three of the four `== []`
        tests in this class carry a positive assertion beside them; this one did not. The
        census is the positive half: it says the room WAS read and came back satisfied, which
        is a different fact from nothing having been asked.
        """
        plan = _plan("library", ["N"])
        assert _kinds(plan) == []
        cen = [f for f in PC.check(plan)["findings"] if f.get("kind") == "aspect-census"][0]
        assert "1 satisfied" in cen["statement"], cen["statement"]

    def test_a_north_east_library_is_clear_because_the_record_names_it(self):
        # A window's `wall` enum is N/E/S/W, so NE is not sayable on a wall -- it is reachable
        # only through a rotation, which is the one thing that turns a plan face into an
        # intercardinal. A house turned 45 degrees puts its plan-N wall on NE, and the library
        # record names NE outright ("A north or north-east library is the historic preference").
        turned = _plan("library", ["N"], site={"street_bearing_deg": 225})
        turned["context"]["entrance_faces"] = "S"          # plan-S faces SW, so plan-N faces NE
        assert CMP.face_token("N", CMP.plan_north(turned)) == "NE"
        assert _kinds(turned) == []

    def test_the_assumption_is_printed_in_the_finding_and_not_merely_held(self):
        # The stated cost of the 5 Sep ruling. A reader told a library faces south deserves to
        # know whether the record said so or whether the checker assumed it.
        f = _kinds(_plan("library", ["S"]))[0]
        assert "true-N" in f["statement"]
        assert f["plan_north_stated"] is False

    def test_a_bearing_moves_the_verdict(self):
        # The same plan, turned so that its plan-S wall faces NORTH on the ground: the library is
        # then correct, and the check must follow the bearing rather than the letter on the wall.
        turned = _plan("library", ["S"], site={"street_bearing_deg": 0})
        turned["context"]["entrance_faces"] = "S"
        f = _kinds(turned)
        assert f == [], [x["statement"] for x in f]
        # and the other way: plan-N glazing on a house whose plan-N faces south
        wrong = _plan("library", ["N"], site={"street_bearing_deg": 0})
        wrong["context"]["entrance_faces"] = "S"
        g = _kinds(wrong)
        assert len(g) == 1 and g[0]["kind"] == "room-on-an-aspect-its-record-avoids"
        assert g[0]["plan_north_stated"] is True

    def test_a_hard_reading_is_serious_and_a_preferred_one_is_minor(self):
        hard = _kinds(_plan("sunroom", ["N"]))
        assert len(hard) == 1 and hard[0]["severity"] == "serious"
        soft = _kinds(_plan("study", ["S"]))
        assert len(soft) == 1 and soft[0]["severity"] == "minor"

    def test_wanting_and_avoiding_are_two_different_findings(self):
        # `study` wants north or east and names nothing to avoid: a south study takes none of the
        # light it asks for, which is a different defect from carrying light it rules out.
        f = _kinds(_plan("study", ["S"]))
        assert f[0]["kind"] == "room-off-the-aspect-its-record-wants"
        g = _kinds(_plan("nursery", ["W"]))
        assert g[0]["kind"] == "room-on-an-aspect-its-record-avoids"

    def test_a_record_that_declines_the_compass_takes_no_finding_and_is_counted(self):
        # `garage`: "Any". A two-state reader turns that into a gap and hunts it for an aspect
        # the record refuses. It is a JUDGED verdict and it appears in the census, not the list.
        plan = _plan("garage", ["N"])
        assert _kinds(plan) == []
        cen = [f for f in PC.check(plan)["findings"] if f.get("kind") == "aspect-census"]
        assert len(cen) == 1
        assert "not a compass" in cen[0]["statement"]

    def test_a_room_with_no_window_is_unjudged_rather_than_clear(self):
        plan = _plan("library", [])
        assert _kinds(plan) == []
        cen = [f for f in PC.check(plan)["findings"] if f.get("kind") == "aspect-census"]
        assert "1 that could not be evaluated" in cen[0]["statement"]

    def test_an_unread_room_record_is_an_info_and_not_a_silence(self):
        plan = _plan("library", ["S"])
        C = PC.load_corpus()
        saved = copy.deepcopy(C["rooms"]["library"]["daylight"])
        try:
            C["rooms"]["library"]["daylight"].pop("aspect")
            f = [x for x in PC.check(plan, C=C)["findings"]
                 if x.get("kind") == "aspect-unstated"]
            assert len(f) == 1 and "UNJUDGED" in f[0]["statement"]
        finally:
            C["rooms"]["library"]["daylight"] = saved


class TestTheCorpusReading:
    def test_the_shipped_corpus_reads_as_published(self):
        # RATCHET-STYLE PINS on deterministic figures. These read the DECLARED record only --
        # nothing here is placed -- so they do not drift the way an `auto` figure does.
        tot = {"room-off-the-aspect-its-record-wants": 0,
               "room-on-an-aspect-its-record-avoids": 0}
        serious = 0
        serious_at = []
        for p in sorted(glob.glob(f"{ROOT}/plans/**/*.json", recursive=True)):
            d = json.loads(open(p).read())
            if "levels" not in d:
                continue
            for f in PC.check(d)["findings"]:
                if f.get("kind") in tot:
                    tot[f["kind"]] += 1
                    serious += f["severity"] == "serious"
                    if f["severity"] == "serious":
                        serious_at.append((os.path.basename(p)[:-5], f.get("room")))
        assert tot == {"room-off-the-aspect-its-record-wants": 40,
                       "room-on-an-aspect-its-record-avoids": 23}
        # ONE hard conviction in the whole corpus, and it is true: good-04's enclosed porch is a
        # north sunroom, which rooms/sunroom.json calls a cold glass box unusable in January.
        #
        # ITS IDENTITY IS ASSERTED AND NOT ONLY ITS COUNT (audit, 7 Sep 2026). `serious == 1`
        # was justified in this comment by naming a plan and a room and then checked neither, so
        # any regression that made a different room hard-serious while good-04's stopped firing
        # kept it green -- a verdict asserted and its reason not, which is the shape this file
        # is otherwise careful about.
        assert serious == 1
        assert serious_at == [("good-04-rambling-porch-farmhouse", "enclosed-porch")], serious_at


# ------------------------------------------------- the two grouping rules given a test (WP-11.9)
#
# Part VI's table again, two rules further down: "Both ends of the passage have doors" and "The
# stair rises in the passage or in a hall opening off it". Both are DECLARED facts, so both are
# answerable on a record with no placement, and both are driven here rather than read off the
# shipped corpus -- on which they PASS, which is the finding and is exactly why a fixture that was
# the corpus would make every assertion below vacuous.
ARR = _load("arrangement", f"{ROOT}/build/arrangement.py")


# `rooms=` REMOVED (audit, 7 Sep 2026): it was never referenced in the body, so a future test
# passing it to vary the room types would have got the default fixture and a green result for
# the wrong reason -- the "fixture never enters the code under test" shape, pre-loaded.
def _passage_plan(passage_doors, stair_doors=("passage",)):
    rs = [{"id": "passage", "type": "centre-passage", "name": "Passage",
           "width_ft": 10, "length_ft": 40,
           "doors": [{"to": t, "width_ft": 3.5} for t in passage_doors]},
          {"id": "stair", "type": "stair-hall", "name": "Stair Hall",
           "width_ft": 10, "length_ft": 14,
           "doors": [{"to": t, "width_ft": 3.5} for t in stair_doors]},
          {"id": "porch", "type": "entry-porch", "name": "Porch",
           "width_ft": 8, "length_ft": 20, "doors": [{"to": "exterior", "width_ft": 3.5}]},
          {"id": "dining", "type": "dining-room", "name": "Dining Room",
           "width_ft": 16, "length_ft": 18, "doors": [{"to": "passage", "width_ft": 3}]}]
    return {"id": "passage-fixture", "name": "Passage Fixture", "style": "tidewater-georgian",
            "context": {"climate_zone": "3A"}, "groupings": ["centre-passage-core"],
            "levels": [{"level": 0, "floor_to_ceiling_ft": 10, "rooms": rs}]}


class TestTheTwoGroupingRules:
    def test_a_front_door_through_a_porch_counts_as_an_end(self):
        # NOT a loosening. The Tidewater passage's front door is `to: porch` because the porch is
        # a room in this model, so a reader counting only `to: exterior` would find ONE end where
        # the record states two -- and would report the diagnosis's own B4 against a record that
        # does not commit it.
        v = ARR.grouping_vars(_passage_plan(["porch", "exterior", "dining", "stair"]))
        assert v["passage_ends_with_a_door"] == 2.0

    def test_a_passage_closed_at_the_back_is_convicted(self):
        plan = _passage_plan(["porch", "dining", "stair"])
        f = [x for x in PC.check(plan)["findings"]
             if x["severity"] == "serious" and "Both ends of the passage" in x["statement"]]
        assert len(f) == 1
        assert "measured 1.0 against at-least 2.0" in f[0]["statement"]

    def test_a_stair_hall_reached_only_from_a_room_is_convicted(self):
        plan = _passage_plan(["porch", "exterior", "dining"], stair_doors=("dining",))
        assert ARR.grouping_vars(plan)["stair_hall_opens_off_the_passage"] == 0.0
        f = [x for x in PC.check(plan)["findings"]
             if x["severity"] == "serious" and "The stair rises in the passage" in x["statement"]]
        assert len(f) == 1
        assert "measured 0.0 against at-least 1.0" in f[0]["statement"]

    def test_the_door_is_read_in_either_direction(self):
        # The passage doors to the stair on the Tidewater record and the stair doors back to the
        # passage on the spec plan's shape; one relation, stated by whichever room happens to
        # carry it. Reading only one way would convict half the corpus of a drafting convention.
        a = _passage_plan(["porch", "exterior", "stair"], stair_doors=())
        b = _passage_plan(["porch", "exterior"], stair_doors=("passage",))
        assert ARR.grouping_vars(a)["stair_hall_opens_off_the_passage"] == 1.0
        assert ARR.grouping_vars(b)["stair_hall_opens_off_the_passage"] == 1.0

    def test_a_plan_with_no_passage_supplies_neither_and_is_unjudged(self):
        # `spec-builder-colonial` carries this grouping and has an entrance hall rather than a
        # passage: both rules report could-not-evaluate, which is not a pass.
        plan = _passage_plan(["porch", "exterior"])
        plan["levels"][0]["rooms"][0]["type"] = "entrance-hall"
        v = ARR.grouping_vars(plan)
        assert "passage_ends_with_a_door" not in v
        assert "stair_hall_opens_off_the_passage" not in v
        f = [x for x in PC.check(plan)["findings"]
             if "passage_ends_with_a_door" in x["statement"]]
        assert len(f) == 1 and f[0]["severity"] == "info"
        assert "Not a pass" in f[0]["statement"]

    def test_every_shipped_plan_still_reads_as_measured(self):
        """The Tidewater record PASSES both, and that is the finding: the diagnosis's B4 -- "a
        centre passage whose rear door read as a window" -- is a defect of the DRAWING, not of
        the record, which states doors at both ends and a stair hall opening off the passage.

        RENAMED AND WIDENED (audit, 7 Sep 2026). It was called `test_both_shipped_plans_...`
        and read ONE, so a reader auditing coverage from the name would conclude the spec
        Colonial was pinned. It is not, and it cannot be by this rule: it carries no passage.
        The sweep says so explicitly rather than leaving the absence to be inferred -- one of
        the sixteen records carries a passage at all, which is the fact that makes every other
        test in this class a DRIVEN one.
        """
        speaks, silent = {}, []
        for p in sorted(glob.glob(f"{ROOT}/plans/**/*.json", recursive=True)):
            d = json.loads(open(p).read())
            if "levels" not in d:
                continue
            v = ARR.grouping_vars(d)
            name = os.path.basename(p)[:-5]
            if "passage_ends_with_a_door" in v:
                speaks[name] = (v["passage_ends_with_a_door"],
                                v.get("stair_hall_opens_off_the_passage"))
            else:
                silent.append(name)
        assert speaks == {"tidewater-georgian-careful": (2.0, 1.0)}, speaks
        assert len(silent) == 15, (
            f"{len(silent)} of the plan records carry no ground-floor passage for this rule to "
            f"read. If that changed, the new record is now the second thing this rule speaks "
            f"on and belongs in the dict above rather than in a count")

    def test_the_alignment_half_is_named_and_not_silently_passed(self):
        # Splitting the rule left an untested half. A rule with no test and no `reported_by` gets
        # the grouping layer's "check by hand" info -- which is the honest state and is what stops
        # the COUNT passing from reading as the ALIGNMENT passing too.
        g = json.loads(open(f"{ROOT}/groupings/centre-passage-core.json").read())
        align = g["internal_rules"][1]
        assert "aligned" in align["statement"]
        assert "test" not in align
        f = [x for x in PC.check(_passage_plan(["porch", "exterior"]))["findings"]
             if "check by hand" in x["statement"] and "are aligned" in x["statement"]]
        assert len(f) == 1
        # AND THE BRANCH THAT SAYS SO HAD TO BE WIDENED TO REACH IT. It read `elif hard`, so a
        # `strong` rule with no test emitted nothing at all -- 28 of the corpus's 86 grouping
        # rules, silent. The severity is in the sentence now, so a reader can tell a hard rule
        # handed over from a preference handed over.
        assert "(strong, no machine test)" in f[0]["statement"]

    def test_the_corpus_holds_28_tested_1_reported_and_57_by_hand(self):
        """The census of the DATA. It is not a test of the checker and no longer claims to be.

        This assertion used to live inside `test_every_grouping_rule_speaks` under a docstring
        saying "deleting the widened branch sends 28 of them quiet again and this is what
        notices". IT DID NOT NOTICE (audit, 7 Sep 2026). Every count here is read out of
        `groupings/*.json` and is independent of `build/plan_check.py`, so reverting `else:` to
        `elif hard:` changed none of them; the `"silent": 0` key was never incremented on any
        path, a literal tautology on the word the test was named after; and the source-substring
        assert beside it passes with the f-string intact and the branch reverted -- on exactly
        the mutation it was written to catch.

        The census is worth keeping, as a census. The behavioural half is the test below.
        """
        n = {"test": 0, "reported": 0, "by_hand": 0}
        for gp in sorted(glob.glob(f"{ROOT}/groupings/*.json")):
            for r in (json.loads(open(gp).read()).get("internal_rules") or []):
                if r.get("test"):
                    n["test"] += 1
                elif (r.get("measures") or {}).get("reported_by"):
                    n["reported"] += 1
                else:
                    n["by_hand"] += 1
        assert n == {"test": 28, "reported": 1, "by_hand": 57}

    def test_every_grouping_rule_speaks(self):
        """EVERY testless rule of every grouping a plan names is EMITTED, counted off the run.

        The count is of hand-offs the checker actually produced, held against the rules the
        named groupings actually carry -- so a rule losing its test cannot be paid for by a rule
        gaining one (WP-11.7's lesson, where a removed serious and an added duplicate cancelled
        and 63 stayed 63), and reverting the branch fails this by the number of `strong` and
        `preferred` rules in the groupings under test rather than by nothing at all.

        Mutation-checked: `else:` -> `elif hard:` in `plan_check.py`'s grouping loop turns this
        red naming the shortfall.
        """
        plan = _passage_plan(["porch", "exterior"])
        C = PC.load_corpus()
        want, hard_want = 0, 0
        for gid in plan.get("groupings", []):
            for r in C["groupings"][gid]["internal_rules"]:
                if r.get("test") or (r.get("measures") or {}).get("reported_by"):
                    continue
                want += 1
                hard_want += r.get("severity") == "hard"
        assert want > 0 and hard_want < want, (
            f"the fixture names groupings with {want} testless rules of which {hard_want} are "
            f"hard; with no non-hard rule among them the `elif hard` revert would be invisible "
            f"here and this test would prove nothing")
        got = [f for f in PC.check(plan)["findings"]
               if f.get("kind") == "grouping-rule-by-hand"]
        assert len(got) == want, (
            f"{len(got)} of {want} testless rules were handed to a reader; the rest emitted "
            f"nothing at all, which reads exactly like a rule that passed")
        # And the severity is IN the sentence, so a reader can tell a hard rule handed over
        # from a preference handed over. Asserted on the emitted text, not on the source.
        assert any("(strong, no machine test)" in f["statement"] for f in got)
        assert all("no machine test" in f["statement"] for f in got)

    def test_the_worst_passage_is_taken_and_not_the_best(self):
        # Reporting the best would be the flattering direction -- the OQ 52 family. Driven,
        # because one of the sixteen records carries a passage at all and it carries exactly one.
        plan = _passage_plan(["porch", "exterior"])
        plan["levels"][0]["rooms"].append(
            {"id": "passage2", "type": "centre-passage", "name": "Second Passage",
             "width_ft": 8, "length_ft": 20,
             "doors": [{"to": "dining", "width_ft": 3}]})
        assert ARR.grouping_vars(plan)["passage_ends_with_a_door"] == 0.0

    def test_a_cross_passage_does_not_dilute_a_centre_passage(self):
        # Where a record carries both, the grouping is about the centre passage and the other is
        # likely a service run; pooling them would judge the wrong room.
        plan = _passage_plan(["porch", "exterior"])
        plan["levels"][0]["rooms"].append(
            {"id": "service", "type": "cross-passage", "name": "Service Passage",
             "width_ft": 5, "length_ft": 20,
             "doors": [{"to": "dining", "width_ft": 3}]})
        assert ARR.grouping_vars(plan)["passage_ends_with_a_door"] == 2.0

    def test_the_upper_passage_is_not_asked_for_ends(self):
        # The Tidewater record's second `centre-passage` is the landing corridor a storey up.
        d = json.loads(open(f"{ROOT}/plans/tidewater-georgian-careful.json").read())
        assert sum(1 for lv in d["levels"] for r in lv["rooms"]
                   if r["type"] == "centre-passage") == 2
        assert ARR.grouping_vars(d)["passage_ends_with_a_door"] == 2.0


class TestWhereTheAspectFindingsGoInTheCritique:
    """A new finding kind reaching the critique with another rule's refusal is the shape WP-11.4
    records as *a refusal with one message for three causes*, and the daylight layer's fall-through
    handed all nine of these "the depth rule does not govern this room type"."""

    def test_the_aspect_is_the_architects_and_says_so_in_its_own_words(self):
        CR = _load("critique", f"{ROOT}/build/critique.py")
        d = json.loads(open(f"{ROOT}/plans/tidewater-georgian-careful.json").read())
        res = CR.classify(d, PC.check(d))
        a = res[0] if isinstance(res, tuple) else res
        hits = [i for c in a for i in a[c] if str(i.get("kind", "")).startswith("room-o")]
        assert len(hits) == 9
        assert {i["class"] for i in hits} == {"architect"}
        assert all("depth rule" not in str(i.get("why")) for i in hits)
        assert all("aspect" in str(i.get("why")) or "light its record asks for" in str(i.get("why"))
                   for i in hits)


# ---------------------------------------------- the CHECKER, driven, not the corpus it happens to pass
#
# **THE VALIDATOR IN `build/check_rooms.py` HAD NO TEST AND ITS WHOLE 44-LINE BLOCK COULD BE
# DELETED WITH THE SUITE GREEN** — found by an adversarial audit of this session's own work, and
# reproduced before it was fixed: `check_rooms.py` came back `OK errors=0` and `test_compass.py`
# stayed green with the block removed.
#
# The reason is worth more than the fix. The four tests above (`test_every_basis_is_verbatim...`,
# `test_a_refusal_carries_its_reason...`, `test_prefer_and_avoid_never_name_the_same_aspect`,
# `test_a_declining_record_carries_no_reading`) assert those rules DIRECTLY over `rooms/*.json`.
# They guard the CORPUS and they are worth having — but a checker is guarded only by being made
# to fire, and on a clean corpus a deleted checker and a working one emit exactly the same
# nothing. **Assert what the checker DOES, not what the data happens to be.**
CR = _load("check_rooms", f"{ROOT}/build/check_rooms.py")


def _room_fixture(**aspect):
    """A minimal room record the checker will accept, with the aspect under test spliced in.

    DRIVEN, never a shipped record: a fixture that is the corpus makes every assertion below a
    statement about this tree rather than about the rule (WP-8.11, and it has bitten twice).
    """
    return {
        "id": "workshop", "name": "Workshop", "function_class": "work", "privacy_rank": 3,
        "confidence": "high", "description": "x", "dimensions": {"area_sf": [100, 200]},
        "daylight": {"depth_multiplier": 2.25, "sides_lit": 1,
                     "orientation": "North for even light on a bench",
                     "aspect": dict(aspect) if aspect else None},
        "adjacency": {}, "servicing": {},
    }


def _run_checker(room):
    rep = CR.Report()
    u = CR.build_universe()
    CR.check_room(rep, f"{ROOT}/rooms/workshop.json", room, u, {"workshop"})
    return rep


class TestTheCheckerFires:
    def test_a_basis_that_is_not_in_the_prose_is_an_error(self):
        r = _run_checker(_room_fixture(applies=True, strength="preferred", prefer=["N"],
                                       basis="North for even light on a workbench",
                                       judgment=True))
        assert any("not verbatim" in m for _w, m in r.errors), r.errors

    def test_a_verbatim_basis_is_accepted(self):
        # The control. Without it the test above passes on a checker that errors on everything.
        r = _run_checker(_room_fixture(applies=True, strength="preferred", prefer=["N"],
                                       basis="North for even light on a bench", judgment=True))
        assert not [m for _w, m in r.errors if "aspect" in m], r.errors

    def test_prefer_and_avoid_naming_the_same_aspect_is_an_error(self):
        r = _run_checker(_room_fixture(applies=True, strength="preferred", prefer=["N"],
                                       avoid=["N"], basis="North for even light on a bench",
                                       judgment=True))
        assert any("wants and avoids" in m for _w, m in r.errors), r.errors

    def test_applies_true_with_no_reading_is_an_error(self):
        # "a pass wearing a verdict": applies says the room is held to an aspect and then names none
        r = _run_checker(_room_fixture(applies=True, strength="preferred",
                                       basis="North for even light on a bench", judgment=True))
        assert any("neither a preferred nor an avoided" in m for _w, m in r.errors), r.errors

    def test_applies_false_carrying_a_reading_is_an_error(self):
        r = _run_checker(_room_fixture(applies=False, prefer=["N"],
                                       basis="North for even light on a bench",
                                       note="x", judgment=True))
        assert any("carries a reading" in m for _w, m in r.errors), r.errors

    def test_a_refusal_with_no_note_is_an_error(self):
        r = _run_checker(_room_fixture(applies=False, basis="North for even light on a bench",
                                       judgment=True))
        assert any("gives no note" in m for _w, m in r.errors), r.errors

    def test_judgment_must_be_true(self):
        # Asserted by NOTHING before this: translating a sentence into tokens is a reading, and a
        # reading that does not say it is one is the laundering this corpus names first.
        r = _run_checker(_room_fixture(applies=True, strength="preferred", prefer=["N"],
                                       basis="North for even light on a bench", judgment=False))
        assert any("judgment: true" in m for _w, m in r.errors), r.errors

    def test_orientation_prose_with_no_aspect_beside_it_is_a_warning(self):
        room = _room_fixture()
        room["daylight"].pop("aspect")
        r = _run_checker(room)
        assert any("unread" in m for _w, m in r.warnings), r.warnings

    def test_an_aspect_with_no_orientation_to_have_read_is_an_error(self):
        room = _room_fixture(applies=True, strength="preferred", prefer=["N"],
                             basis="anything", judgment=True)
        room["daylight"].pop("orientation")
        r = _run_checker(room)
        assert any("no daylight.orientation" in m for _w, m in r.errors), r.errors


# ------------------------------------------------------- the term that entered the scored key
class TestTheAspectIsInTheScoredKey:
    """WP-11.9 changed `compose`'s fitness function and its report does not say so.

    The aspect findings are `serious`/`minor`, not `info`; `compose.SCORE_LAYERS` maps
    `daylight` to the 18-point `rooms` axis; so the day that layer shipped, the composer began
    ranking candidates on it. Measured by the audit of 7 Sep 2026: the rooms axis moves by up to
    3.00 of 18 points on the shipped plans, and on a real compose at 8 candidates the ORDER below
    the winner changes on both shipped briefs. `oq/the-composer-ranks-on-an-assumed-bearing`
    carries the question and the numbers.

    THESE TESTS DO NOT PIN THE DELTAS. They are properties of 16 plan records and would go red
    on any authoring change, which is WP-9.6's rule about ratcheting a number that drifts. What
    is pinned is the two facts a reader of the register needs to still be true: that the layer is
    IN the key, and that removing it MOVES the key -- so the day someone excludes it, or the day
    it goes inert, this says so instead of the open question quietly becoming false.
    """

    def _axis(self, CO, plan):
        res = PC.check(plan)
        n = sum(len(lv["rooms"]) for lv in plan["levels"])
        a = CO._axis_from_layers(res, "rooms", n)
        return a["share"] if isinstance(a, dict) else a

    def test_the_daylight_layer_is_mapped_to_a_scored_axis(self):
        CO = _load("compose", f"{ROOT}/build/compose.py")
        assert CO.SCORE_LAYERS.get("daylight") == "rooms", (
            "the aspect findings stopped feeding the score. If that was deliberate, close "
            "oq/the-composer-ranks-on-an-assumed-bearing rather than leaving it saying they do")

    def test_the_aspect_findings_are_not_info_and_so_reach_the_key(self):
        plan = json.loads(open(f"{ROOT}/plans/tidewater-georgian-careful.json").read())
        sev = {f["severity"] for f in PC.check(plan)["findings"]
               if str(f.get("kind") or "").startswith("room-o")}
        assert sev and sev <= {"serious", "minor"}, sev

    def test_suppressing_the_aspect_reading_moves_the_rooms_axis(self):
        """The measurement, driven -- and the guard against the way it was first got wrong.

        The first attempt patched a `compass` reached through a SECOND modcache instance, so the
        suppression never landed and every delta read 0.00, which is indistinguishable from an
        inert term. The `assert after == 0` below is what makes the comparison mean anything:
        it proves the patch reached the module the checker is using before any delta is read.
        """
        CO = _load("compose", f"{ROOT}/build/compose.py")
        plan = json.loads(open(f"{ROOT}/plans/tidewater-georgian-careful.json").read())
        live = PC._load("compass", f"{ROOT}/build/compass.py")   # the checker's OWN object
        real = live.read
        before_share = self._axis(CO, plan)
        before_n = sum(1 for f in PC.check(plan)["findings"]
                       if str(f.get("kind") or "").startswith("room-o"))
        try:
            live.read = lambda *a, **k: {"verdict": "unstated", "reason": "suppressed"}
            after_n = sum(1 for f in PC.check(plan)["findings"]
                          if str(f.get("kind") or "").startswith("room-o"))
            assert before_n > 0 and after_n == 0, (
                f"the suppression did not reach the checker's compass ({before_n} -> {after_n}); "
                f"the comparison below would be vacuous")
            after_share = self._axis(CO, plan)
        finally:
            live.read = real
        assert after_share > before_share, (
            f"suppressing every aspect verdict left the rooms axis at {before_share}; the layer "
            f"has gone inert in the score and the open question no longer describes the code")
