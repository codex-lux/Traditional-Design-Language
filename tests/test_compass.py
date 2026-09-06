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


def _kinds(plan):
    return [f for f in PC.check(plan)["findings"] if str(f.get("kind", "")).startswith("room-o")]


class TestTheCheck:
    def test_a_south_library_is_convicted_and_says_so(self):
        f = _kinds(_plan("library", ["S"]))
        assert len(f) == 1
        assert f[0]["kind"] == "room-on-an-aspect-its-record-avoids"
        assert f[0]["severity"] == "minor"           # the library's NORTH is shouted and licensed
        assert "plan-S is S" in f[0]["statement"]

    def test_a_north_library_is_clear(self):
        assert _kinds(_plan("library", ["N"])) == []

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
        for p in sorted(glob.glob(f"{ROOT}/plans/**/*.json", recursive=True)):
            d = json.loads(open(p).read())
            if "levels" not in d:
                continue
            for f in PC.check(d)["findings"]:
                if f.get("kind") in tot:
                    tot[f["kind"]] += 1
                    serious += f["severity"] == "serious"
        assert tot == {"room-off-the-aspect-its-record-wants": 40,
                       "room-on-an-aspect-its-record-avoids": 23}
        # ONE hard conviction in the whole corpus, and it is true: good-04's enclosed porch is a
        # north sunroom, which rooms/sunroom.json calls a cold glass box unusable in January.
        assert serious == 1


# ------------------------------------------------- the two grouping rules given a test (WP-11.9)
#
# Part VI's table again, two rules further down: "Both ends of the passage have doors" and "The
# stair rises in the passage or in a hall opening off it". Both are DECLARED facts, so both are
# answerable on a record with no placement, and both are driven here rather than read off the
# shipped corpus -- on which they PASS, which is the finding and is exactly why a fixture that was
# the corpus would make every assertion below vacuous.
ARR = _load("arrangement", f"{ROOT}/build/arrangement.py")


def _passage_plan(passage_doors, stair_doors=("passage",), rooms=("centre-passage", "stair-hall")):
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

    def test_both_shipped_plans_still_read_as_measured(self):
        # The Tidewater record PASSES both, and that is the finding: the diagnosis's B4 -- "a
        # centre passage whose rear door read as a window" -- is a defect of the DRAWING, not of
        # the record, which states doors at both ends and a stair hall opening off the passage.
        d = json.loads(open(f"{ROOT}/plans/tidewater-georgian-careful.json").read())
        v = ARR.grouping_vars(d)
        assert v["passage_ends_with_a_door"] == 2.0
        assert v["stair_hall_opens_off_the_passage"] == 1.0

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

    def test_every_grouping_rule_speaks(self):
        # 28 of 86 carry a test, 1 reports, and the other 57 are handed to a human BY NAME. None
        # is silent. Deleting the widened branch sends 28 of them quiet again and this is what
        # notices -- a count, so that a rule losing its test cannot be paid for by a rule gaining
        # one (WP-11.7's own lesson, where a removed serious and an added duplicate cancelled and
        # 63 stayed 63).
        n = {"test": 0, "reported": 0, "by_hand": 0, "silent": 0}
        for gp in sorted(glob.glob(f"{ROOT}/groupings/*.json")):
            for r in (json.loads(open(gp).read()).get("internal_rules") or []):
                if r.get("test"):
                    n["test"] += 1
                elif (r.get("measures") or {}).get("reported_by"):
                    n["reported"] += 1
                else:
                    n["by_hand"] += 1
        assert n == {"test": 28, "reported": 1, "by_hand": 57, "silent": 0}
        src = open(f"{ROOT}/build/plan_check.py").read()
        assert "check by hand ({ir.get('severity', 'strong')}, no " in src

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
