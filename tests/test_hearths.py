"""WP-11.4 — the fire, which the plan layer did not have.

`docs/reports/tidewater-layout-diagnosis-2026-09-04.md` D1: no fireplace anywhere in the plan
layer — not a field on a room, not a thing the placer reserves, not a line on the plate — while
`massings/catalog.json` said `hearth: gable-end-paired` and *"Paired end chimneys serve four
fireplaces per floor"*, and `roof.py` and `elevation.py` drew the stacks over rooms containing no
fire. Two records of one house, which is OQ 85's shape one layer down.

The design rule these tests exist to hold: **a hearth is AUTHORED and never inferred.**
`rooms/bedchamber.json` says *"or none at all: unheated chambers are historically normal and
should be said out loud rather than quietly given a register"*, so a checker that demanded a fire
wherever a room type usually has one would invent exactly what that sentence forbids.
"""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))

import modcache  # noqa: E402

HE = modcache.load("hearths", os.path.join(ROOT, "build", "hearths.py"))
PC = modcache.load("plan_check", os.path.join(ROOT, "build", "plan_check.py"))
GEO = modcache.load("geometry", os.path.join(ROOT, "build", "geometry.py"))
RF = modcache.load("roof", os.path.join(ROOT, "build", "roof.py"))
ST = modcache.load("structure", os.path.join(ROOT, "build", "structure.py"))


@pytest.fixture(scope="module")
def C():
    return PC.load_corpus()


def tidewater():
    return json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))


# ------------------------------------------------------------------ reading the massing
class TestTheMassingsHearth:
    def test_the_forms_it_acts_on(self):
        assert HE.massing_hearth({"hearth": "gable-end-paired"})["readable"] is True
        assert HE.massing_hearth({"hearth": "central-stack"})["rule"]["central"] is True
        assert HE.massing_hearth({"hearth": "gable-end-paired"})["rule"]["walls"] == ("E", "W")

    def test_a_compound_is_refused_rather_than_resolved(self):
        """*"gable-end-paired or central-stack"* is a real statement about a type that admits
        both arrangements. Choosing between them here would be authoring on the corpus's
        behalf, so it is refused BY NAME — the same discipline `massing_bays` applies to
        `"5-7 main"`."""
        for prose in ("gable-end-paired or central-stack", "central or none",
                      "interior or end", "gable-end or corner", "party-wall or end",
                      "central or end", "distributed", "living-room-focal", "central-mass"):
            mh = HE.massing_hearth({"hearth": prose})
            assert mh["readable"] is False, prose
            assert mh["stated"] == prose, "the refusal must still carry what was said"

    def test_a_massing_with_no_hearth_field_is_unreadable_not_empty(self):
        assert HE.massing_hearth({})["readable"] is False
        assert HE.massing_hearth({})["stated"] is None


# ------------------------------------------------------------------ reading the room
class TestWhatTheRoomRecordSays:
    def test_four_verdicts_because_the_records_make_four_statements(self, C):
        assert HE.wants_a_hearth(C["rooms"]["drawing-room"])["verdict"] == "stated"
        assert HE.wants_a_hearth(C["rooms"]["bedchamber"])["verdict"] == "optional"
        assert HE.wants_a_hearth(C["rooms"]["centre-passage"])["verdict"] == "none"
        assert HE.wants_a_hearth(C["rooms"]["bedroom"])["verdict"] == "unstated"

    def test_the_verdict_that_a_two_state_reader_would_have_lost(self, C):
        """`centre-passage`'s *"Historically none. The passage is the unheated buffer between
        two heated rooms"* carries no fireplace word at all, so a reader looking for one files
        it under `unstated` and goes looking for a fire the corpus has explicitly refused it."""
        v = HE.wants_a_hearth(C["rooms"]["centre-passage"])
        assert v["verdict"] == "none"
        assert "Historically none" in v["quote"]

    def test_the_optional_verdict_carries_the_sentence_that_forces_the_design(self, C):
        v = HE.wants_a_hearth(C["rooms"]["bedchamber"])
        assert "said out loud" in v["quote"]

    def test_a_modern_room_type_states_ductwork_and_not_a_fire(self, C):
        """The records speak two vocabularies and the split is not accidental: rooms that
        predate central heating state a fire, and rooms that do not state ducts. A Georgian
        plan built from modern room types therefore has NO room-level statement about its
        fires, which is a fact about this corpus and not a gap in these tests."""
        for rid in ("bedroom", "primary-bedroom", "breakfast-room"):
            assert HE.wants_a_hearth(C["rooms"][rid])["verdict"] == "unstated"


# ------------------------------------------------------------------ the opening
class TestTheOpening:
    def test_the_room_records_own_figure_outranks_morris(self, C):
        """`bedchamber`'s *"30-36 in opening"* is the corpus's own number and is not
        judgment."""
        ow = HE.opening_width_in(C["rooms"]["bedchamber"], 14, 16)
        assert ow["width_in"] == 33.0 and ow["judgment"] is False
        assert ow["band_in"] == [30.0, 36.0]

    def test_morris_is_the_fallback_and_is_always_marked_judgment(self, C):
        ow = HE.opening_width_in(C["rooms"]["drawing-room"], 18, 22)
        assert ow["judgment"] is True
        assert "Morris" in ow["source"]
        assert "may not be published as measured" in ow["why"]

    def test_RULE_II_IS_EXECUTED_AND_NOT_INTERPOLATED(self, C):
        """Morris's own words, from the 1734 first edition: *"add the Length, Breadth and Height
        of the Room together, and extract the Square Root of that Sum, and half that Root will
        be the Breadth of your Chimney."* The first draft carried two ROWS of the table he
        calculated from that rule and drew a straight line between them, which approximates a
        square-root law the source states exactly.

        The two anchors it discarded were (12 ft cube, 36 in) and (22 ft, 49 in), and the rule
        reproduces both. **That is a consistency check and not an independent corroboration** --
        where those anchors came from is not recorded, so a common origin cannot be excluded."""
        rec = C["rooms"]["drawing-room"]
        for side, want in ((12.0, 36.00), (22.0, 48.74)):
            ow = HE.opening_width_in(rec, side, side, ceiling_ft=side)   # a cube room
            # 0.06 because the function rounds to a tenth of an inch, which is a tenth of an
            # inch wider than the discrepancy this is looking for
            assert abs(ow["width_in"] - want) < 0.06, (side, ow["width_in"])
            assert ow["ceiling_assumed"] is False
        # and it is the RULE that is reported, not a table
        ow = HE.opening_width_in(rec, 16.0, 20.0, ceiling_ft=11.0)
        assert "Rule II" in ow["source"] and "executed" in ow["source"]
        assert ow["rule"] == HE.MORRIS_RULE_II
        assert abs(ow["width_in"] - ((16.0 + 20.0 + 11.0) ** 0.5) / 2 * 12) < 0.06
        # THE DIFFERENCE IS AT THE ENDS, AND THAT IS THE HONEST FINDING. Between the two
        # anchors the chord tracked the square root to within 0.3 in, so the interpolation was
        # not badly wrong there and saying it was would be an overstatement. It was CLAMPED:
        # `t = max(0, min(1, ...))`, so every room smaller than a 12 ft cube got 36.0 in and
        # every room larger than a 22 ft cube got 49.0, flat, forever. An 8 ft cube closet was
        # given a 6.6 in wider opening than the rule allows and a 30 ft cube saloon 7.9 in
        # narrower. A fixture that probed only the middle would have found 0.3 in and concluded
        # the change was cosmetic.
        def interp(cube):
            t = max(0.0, min(1.0, (cube - 12.0) / 10.0))
            return 36.0 + t * 13.0

        def ruled(cube):
            return HE.opening_width_in(rec, cube, cube, ceiling_ft=cube)["width_in"]

        assert abs(ruled(17.0) - interp(17.0)) < 0.4, (
            "inside the anchors the chord was close, and this test says so")
        assert ruled(8.0) - interp(8.0) < -6.0, "a small room was given far too wide an opening"
        assert ruled(30.0) - interp(30.0) > 7.0, "a large one far too narrow"

    def test_AN_ASSUMED_CEILING_SAYS_SO_AND_A_STATED_ONE_IS_USED(self, C):
        """Rule II wants three dimensions and a plan states two. The third is editorial where
        the record is silent, and silently substituting it would be the invention this file
        exists to stop -- so it is returned under `ceiling_assumed` and it MOVES the answer."""
        rec = C["rooms"]["drawing-room"]
        blind = HE.opening_width_in(rec, 18.0, 20.0)
        assert blind["ceiling_assumed"] is True
        assert blind["ceiling_ft"] == HE.MORRIS_CEILING_FT
        low = HE.opening_width_in(rec, 18.0, 20.0, ceiling_ft=9.0)["width_in"]
        high = HE.opening_width_in(rec, 18.0, 20.0, ceiling_ft=11.0)["width_in"]
        assert low < blind["width_in"] < high
        # 0.87 in over the 9-to-11 ft range on an 18 x 20 room: small, and not nothing. A
        # square root flattens it -- which is worth knowing before anyone spends a ruling on
        # MORRIS_CEILING_FT, and is why the assertion states the real figure rather than a
        # round one it would pass more comfortably.
        assert 0.8 < high - low < 0.95, (low, high)

    def test_THE_LEVELS_STATED_CEILING_IS_USED_AND_WAS_BEING_INVENTED(self, C):
        """The Tidewater plan states `floor_to_ceiling_ft` of 11 on the ground and 10 above --
        `build/storeys.py` has read that field for two packages -- and `opening_width_in` was
        reaching for `MORRIS_CEILING_FT` on every room of both. Substituting an editorial
        constant for a number the record states, one function away from the comment refusing to
        do exactly that."""
        p = tidewater()
        ground = next(lv for lv in p["levels"] if lv["id"] == "ground")
        assert HE.level_ceiling_ft(ground) == 11
        rep = HE.hearth_report(p, C)
        row = next(r for r in rep["rooms"] if r["room"] == "drawing")
        # 18 x 22 at a stated 11 ft ceiling: sqrt(51)/2 ft
        assert abs(row["rule_width_in"] - ((18 + 22 + 11) ** 0.5) / 2 * 12) < 0.06
        blind = HE.opening_width_in(C["rooms"]["drawing-room"], 18, 22)["width_in"]
        assert abs(row["rule_width_in"] - blind) > 0.5, (
            "if the stated ceiling and the assumed one gave the same answer this proves nothing")

    def test_THE_AUTHORED_OPENINGS_AGREE_WITH_THE_RULE_AT_THE_STATED_CEILING(self, C):
        """The three authored widths are Rule II executed, and this is what makes them
        checkable. They were 46.3 / 43.7 / 41.8 when they came off a clamped interpolation of
        the table; they are 42.8 / 41.1 / 39.8 from the rule at the ground level's stated 11 ft.
        REPORTED AND NEVER ENFORCED elsewhere -- the opening is an authored plan fact and the
        rule is a London figure at one remove, so a checker convicting an author of disagreeing
        with it would have the authority backwards. Here it is the fixture's own consistency."""
        rep = HE.hearth_report(tidewater(), C)
        checked = 0
        for row in rep["rooms"]:
            if row["state"] != "stated":
                continue
            for h in row["declared"]:
                assert abs(h["width_in"] - row["rule_width_in"]) < 0.06, (row["room"], h)
                checked += 1
        assert checked == 3

    def test_a_room_with_no_dimensions_gets_no_number_at_all(self, C):
        ow = HE.opening_width_in(C["rooms"]["drawing-room"], None, None)
        assert ow["width_in"] is None and ow["judgment"] is True


    def test_A_FIGURE_IS_ONLY_READ_WHERE_THE_RECORD_ADMITS_A_FIRE(self, C):
        """THE DEFECT THIS GUARD WAS WRITTEN FOR, found by re-deriving a report claim rather
        than re-reading it. `rooms/closet.json` opens *"None required and none wanted"* and then
        describes a closet ceiling *"drywalled from a stepladder through a 30 in opening"* — an
        air barrier, about a doorway. The bare inch-search took it and returned **30.0 in at
        `judgment: false`**: a room that wants no heat at all publishing a MEASURED fireplace
        opening. The gate is `wants_a_hearth`'s verdict, not a tighter regex, because a regex
        cannot tell a doorway from a chimneypiece and the verdict already can."""
        closet = C["rooms"]["closet"]
        assert "None required and none wanted" in closet["servicing"]["heat"]
        assert "30 in opening" in closet["servicing"]["heat"], (
            "the record moved; this guard is reading air")
        assert HE.wants_a_hearth(closet)["verdict"] == "unstated"
        ow = HE.opening_width_in(closet, 18.0, 20.0)
        assert ow["judgment"] is True, "a closet may not publish a measured fireplace opening"
        assert ow["width_in"] != 30.0

    def test_and_bedchamber_is_then_the_ONLY_own_figure_in_the_corpus(self, C):
        """The complement, and it is the claim `build/hearths.py`'s docstring makes. Before the
        gate it was false — there were two."""
        own = sorted(rid for rid, rec in (C["rooms"] or {}).items()
                     if not HE.opening_width_in(rec, 18.0, 20.0)["judgment"])
        assert own == ["bedchamber"], f"expected bedchamber alone, got {own}"
        assert HE.opening_width_in(C["rooms"]["bedchamber"], 18.0, 20.0)["width_in"] == 33.0


# ------------------------------------------------------------------ the report
class TestTheHearthReport:
    def test_the_shipped_plan_states_the_three_the_corpus_supports(self, C):
        r = HE.hearth_report(tidewater(), C)
        assert r["census"]["stated"] == 3
        assert r["census"]["absent"] == 0, "a room the corpus says has a fire and the plan does not"
        stated = {row["room"] for row in r["rooms"] if row["state"] == "stated"}
        assert stated == {"drawing", "dining", "library"}

    def test_the_passage_and_the_stair_are_DECLINED_not_unjudged(self, C):
        r = HE.hearth_report(tidewater(), C)
        declined = {row["room"] for row in r["rooms"] if row["state"] == "declined"}
        assert {"passage", "upperpassage", "stair"} <= declined

    def test_the_modern_room_types_are_unjudged_and_counted(self, C):
        r = HE.hearth_report(tidewater(), C)
        assert r["census"]["unjudged"] > 0
        assert sum(r["census"][k] for k in ("stated", "absent", "declined", "unjudged")) == \
            sum(1 for lv in tidewater()["levels"] for _ in lv["rooms"])

    def test_a_room_the_corpus_gives_a_fire_and_the_plan_does_not_is_ABSENT(self, C):
        p = tidewater()
        for lv in p["levels"]:
            for r in lv["rooms"]:
                r.pop("hearth", None)
        rep = HE.hearth_report(p, C)
        assert rep["census"]["absent"] == 3
        assert rep["census"]["stated"] == 0

    def test_a_COMPOUND_massing_hearth_is_refused_by_name_and_convicts_nobody(self, C):
        """`gambrel-block` states *"gable-end-paired or central-stack"*. That is a real statement
        about a type that admits both, and resolving it here would be choosing on the corpus's
        behalf -- so it is refused, and the refusal may not convict a room of a missing fire."""
        p = tidewater()
        p["massing"] = "gambrel-block"
        rep = HE.hearth_report(p, C)
        assert rep["massing_hearth"] == "gable-end-paired or central-stack"
        assert rep["readable"] is False and "compound" in rep["why"]
        assert rep["census"]["absent"] == 0, "an unreadable massing may not convict a room"

    def test_THE_REFUSAL_NAMES_ITS_OWN_REASON_AND_THERE_ARE_THREE(self, C):
        """The first draft gave ONE reason -- *"a compound is a statement about a type that
        admits both"* -- to all three refusals, and 14 of the 16 plan records in this tree got
        it while stating no massing at all. A true sentence about a different situation, which
        is the class of false claim this project keeps finding in its own prose. Each reason is
        held against the case that produces it."""
        no_massing = HE.flue_walls({}, {})[1]
        assert "names no massing" in no_massing and "compound" not in no_massing

        silent = HE.flue_walls({}, {"id": "made-up"})[1]
        assert "states no `hearth` at all" in silent and "compound" not in silent

        compound = HE.flue_walls({}, {"id": "gambrel-block",
                                      "hearth": "gable-end-paired or central-stack"})[1]
        assert "compound" in compound

        assert len({no_massing, silent, compound}) == 3, "three cases, three reasons"

    def test_the_reference_plans_state_no_massing_and_are_told_so(self, C):
        """Measured, because it is a fact about this corpus and not about this file: 14 of the
        16 plan records name no massing, so every massing-gated check in `plan_check` -- the
        grouping `attaches_to` branch, the style `massing_affinities` branch, this one -- is silent on all
        fourteen. Raised as `oq/fourteen-of-sixteen-plans-name-no-massing`."""
        p = json.load(open(os.path.join(
            ROOT, "plans", "reference", "good-01-veranda-gallery-estate.json")))
        assert p.get("massing") is None
        rep = HE.hearth_report(p, C)
        assert rep["readable"] is False
        assert "names no massing" in rep["why"]
        assert rep["census"]["absent"] == 0

    def test_a_massing_hearth_form_this_file_does_not_know_is_refused_too(self, C):
        """`prairie-cruciform` says `central-mass`, which is not one of the six accepted forms.
        Mapping it to the nearest (`central`) would be the guess this whole file exists to stop:
        `massing_bays` reads its own field the same way and for the same reason."""
        p = tidewater()
        p["massing"] = "prairie-cruciform"
        rep = HE.hearth_report(p, C)
        assert rep["massing_hearth"] == "central-mass"
        assert rep["readable"] is False and rep["why"]
        assert rep["census"]["absent"] == 0

    def test_A_DECLINED_ROOM_STAYS_DECLINED_WHEN_THE_MASSING_CANNOT_BE_READ(self, C):
        """THE ORDER OF THE BRANCHES IS LOAD-BEARING AND IS MEASURED, which is WP-8.11's lesson
        about `kit.forbidden` in a new place. `none` is tested BEFORE the unreadable-massing
        branch, so a room the corpus positively refuses a fire — `rooms/centre-passage.json`:
        *"Historically none. The passage is the unheated buffer between two heated rooms"* — is
        `declined` whatever the massing says. Test them the other way round and the corpus's own
        refusal is downgraded to "nobody could tell", which is the fake-unjudged direction and
        is as dishonest as a fake pass."""
        p = tidewater()
        p["massing"] = "prairie-cruciform"          # `central-mass`, refused
        rep = HE.hearth_report(p, C)
        assert rep["readable"] is False
        declined = {r["room"] for r in rep["rooms"] if r["state"] == "declined"}
        assert {"passage", "upperpassage", "stair"} <= declined, (
            "an unreadable massing may not turn the corpus's own refusal into an unjudged")

    def test_octagons_bare_central_IS_read_which_is_the_complement_of_the_two_above(self, C):
        """The refusals above would be worth nothing if the reader refused everything. `octagon`
        states a bare `central` and is read -- walls (), central True."""
        p = tidewater()
        p["massing"] = "octagon"
        rep = HE.hearth_report(p, C)
        assert rep["readable"] is True and rep["central"] is True and rep["walls"] == []


# ------------------------------------------------------------------ the breast
class TestTheBreast:
    def test_it_stands_on_the_named_wall_and_projects_into_the_room(self):
        """THIS GUARD WAS BLIND ON ITS FIRST WRITING and a mutation found it. It asserted only
        that the breast lies INSIDE the room's x-extent, which is true of a breast on the west
        wall and equally true of the same breast on the east wall — swapping the two in
        `breast()` left the suite green. The face flush with the named wall is the whole claim,
        so the face is what is asserted, per wall, with the opposite face proved NOT flush."""
        placed = GEO.solve(tidewater(), None, 60, engine="heuristic")
        walls = []
        for lv in placed["levels"]:
            for r in lv["rooms"]:
                for h in (r.get("hearth") or []):
                    b = HE.breast(r, h)
                    if not b or b.get("undrawable"):
                        continue
                    walls.append(b["wall"])
                    g = r["geometry"]
                    lo, hi = g["x_ft"], g["x_ft"] + g["width_ft"]
                    bl, bh = b["x_ft"], b["x_ft"] + b["width_ft"]
                    assert lo - 0.01 <= bl and bh <= hi + 0.01, "the breast leaves the room"
                    if b["wall"] == "W":
                        assert abs(bl - lo) < 0.01, "a west hearth stands on the west wall"
                        assert abs(bh - hi) > 0.5, "and its other face is clear of the east"
                    else:
                        assert abs(bh - hi) < 0.01, "an east hearth stands on the east wall"
                        assert abs(bl - lo) > 0.5, "and its other face is clear of the west"
                    assert b["judgment"] is True, "the projection is Morris's, and is judgment"
        assert len(walls) == 3, f"expected three drawable breasts, got {len(walls)}"
        assert set(walls) == {"E", "W"}, (
            "the fixture must exercise BOTH walls or the per-wall branch above is untested "
            f"— got {sorted(set(walls))}")

    def test_an_unplaced_room_has_no_breast(self, C):
        p = tidewater()
        room = next(r for lv in p["levels"] for r in lv["rooms"] if r.get("hearth"))
        assert HE.breast(room, room["hearth"][0]) is None

    def test_an_interior_hearth_is_undrawable_and_says_why(self):
        placed = GEO.solve(tidewater(), None, 60, engine="heuristic")
        room = next(r for lv in placed["levels"] for r in lv["rooms"] if r.get("hearth"))
        b = HE.breast(room, {"wall": "interior", "width_in": 40})
        assert b["undrawable"] is True and "plausible" in b["why"]


# ------------------------------------------------------------------ the roof reconciliation
class TestTheStackStandsOverAFire:
    """D3: `roof.py` put a stack at the centre of each gable end, from the RECTANGLE and not
    from the rooms inside it, so the elevation drew stacks over a passage and a kitchen. Closed
    the way OQ 85 closed the window on the chimney axis: read the other record, and disclose."""

    def test_a_placed_plan_moves_its_stacks_onto_the_stated_flues(self):
        placed = GEO.solve(tidewater(), None, 60, engine="heuristic")
        ch = RF.build_roof(placed, section=ST.build_section(placed))["chimneys"]
        assert ch.get("from_stated_hearths") is True
        assert "the PLAN states" in ch["note"]
        ys = sorted(round(c["y_ft"], 2) for c in ch["positions"])
        centre = round(ST.build_section(placed)["footprint"]["depth_ft"] / 2.0, 2)
        assert ys != [centre, centre], "the stacks did not move off the gable centre line"

    def test_two_fires_on_one_flue_are_one_stack(self):
        """The drawing room and the dining room share `west-stack`, which is what a pair of
        paired end chimneys joined by an arched curtain means."""
        placed = GEO.solve(tidewater(), None, 60, engine="heuristic")
        ch = RF.build_roof(placed, section=ST.build_section(placed))["chimneys"]
        assert len(ch["positions"]) == 2, "three fires on two flues must give two stacks"

    def test_a_declared_record_says_it_could_not_position_them(self):
        """THE STATE A TWO-STATE NOTE GOT WRONG ON ITS FIRST RUN. This plan states three
        hearths and an unplaced record cannot position any of them, because a hearth's place
        along its wall comes from the room's placed rectangle. The note said "this record
        states no hearth" about a record carrying three — the class of false claim this whole
        package is fixing."""
        ch = RF.build_roof(tidewater(), section=ST.build_section(tidewater()))["chimneys"]
        assert "STATES 3 hearth(s)" in ch["note"]
        assert not ch.get("from_stated_hearths")

    def test_A_RECONCILIATION_THAT_CANNOT_BE_READ_IS_A_FOURTH_STATE(self, monkeypatch):
        """The first draft wrapped `stack_axes` in a bare `except Exception: axes = None`, which
        reverts to the centre-line rule SILENTLY and then says *"this record states no hearth"*
        about a record carrying three. That is WP-9.1's `except: pass` — two buildings judged as
        one for a phase — and it is the exact false claim this package removes. Four states now:
        positioned / stated-but-unplaced / UNREADABLE / none."""
        placed = GEO.solve(tidewater(), None, 60, engine="heuristic")
        sec = ST.build_section(placed)

        def boom(plan, C):
            raise ValueError("a hearth wall nobody wrote down")

        monkeypatch.setattr(HE, "stack_axes", boom)
        ch = RF.build_roof(placed, section=sec)["chimneys"]
        assert ch.get("hearths_unreadable"), "the failure must be recorded, not swallowed"
        assert "COULD NOT BE READ" in ch["note"]
        assert "a hearth wall nobody wrote down" in ch["note"], (
            "the note must carry the real reason, not a category")
        assert "states no hearth" not in ch["note"], (
            "an unreadable reconciliation is not a record stating none — that collapse is the "
            "whole reason this state exists")
        assert not ch.get("from_stated_hearths")

    def test_a_plan_with_no_hearths_keeps_the_centre_line_rule_and_is_told_so(self):
        p = tidewater()
        for lv in p["levels"]:
            for r in lv["rooms"]:
                r.pop("hearth", None)
        placed = GEO.solve(p, None, 60, engine="heuristic")
        ch = RF.build_roof(placed, section=ST.build_section(placed))["chimneys"]
        assert "states no hearth" in ch["note"]
        assert "not a house with no fires" in ch["note"], (
            "a record that has not said is not a house with none, and the note must say so")


# ------------------------------------------------------------------ the schema
class TestTheSchemaAdmitsIt:
    """THE THIRD BLIND GUARD. Nothing in the first draft validated a plan against
    `schema/plan.schema.json` at all, so replacing the `wall` enum with a bare `type: string`
    left the suite green — the field could have admitted `"northish"` and no test would have
    said so. The schema is what a caller-supplied plan meets at `app._plan(body)` (WP-10.1),
    which is exactly the reader who cannot know."""

    @staticmethod
    def _schema():
        return json.load(open(os.path.join(ROOT, "schema", "plan.schema.json")))

    def test_the_shipped_plan_with_its_three_hearths_validates(self):
        jsonschema = pytest.importorskip("jsonschema")
        jsonschema.validate(tidewater(), self._schema())

    def test_a_wall_outside_the_five_is_REFUSED(self):
        jsonschema = pytest.importorskip("jsonschema")
        p = tidewater()
        room = next(r for lv in p["levels"] for r in lv["rooms"] if r.get("hearth"))
        room["hearth"][0]["wall"] = "northish"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(p, self._schema())

    def test_a_hearth_with_no_wall_at_all_is_REFUSED(self):
        """`wall` is the one required key: a fire whose wall nobody stated cannot be placed,
        and admitting it would put the guess back one layer down."""
        jsonschema = pytest.importorskip("jsonschema")
        p = tidewater()
        room = next(r for lv in p["levels"] for r in lv["rooms"] if r.get("hearth"))
        room["hearth"][0].pop("wall")
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(p, self._schema())

    def test_a_misspelt_key_is_REFUSED_rather_than_silently_carried(self):
        jsonschema = pytest.importorskip("jsonschema")
        p = tidewater()
        room = next(r for lv in p["levels"] for r in lv["rooms"] if r.get("hearth"))
        room["hearth"][0]["width_inches"] = 44
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(p, self._schema())

    def test_the_version_was_raised_with_the_field(self):
        assert self._schema()["version"] == "0.7.0"


# ------------------------------------------------------------------ the critic and the plate
class TestTheCriticAndThePlate:
    def test_the_census_is_published(self):
        placed = GEO.solve(tidewater(), None, 60, engine="heuristic")
        c = PC.check(placed)
        h = c.get("hearth_summary")
        assert h and h["massing"] == "gable-end-paired" and h["readable"] is True
        assert h["census"]["stated"] == 3

    def test_IT_IS_NOT_A_DRAWN_CHECK_AND_RUNS_ON_AN_UNPLACED_RECORD(self):
        """THE DEFECT THIS GUARD WAS WRITTEN FOR. The block was first put in `drawn_layer`,
        which early-returns on a record with no placement — so the spec plan's dining room,
        which has no fire under a massing that draws paired end stacks, produced no finding, no
        census and no reason until somebody placed it. A check that could not fire reading
        exactly like a check that passed, inside the package written to stop that.

        Nothing `hearth_report` reads is a placement: the room's authored `hearth`, the
        massing's `hearth`, the room type's `servicing.heat`. `breast` and `stack_axes` DO read
        placement and belong to the renderer and the roof."""
        declared = json.load(open(os.path.join(ROOT, "plans", "spec-builder-colonial.json")))
        assert not any(r.get("geometry") for lv in declared["levels"] for r in lv["rooms"]), (
            "this fixture must be unplaced or it proves nothing")
        c = PC.check(declared)
        h = c.get("hearth_summary")
        assert h is not None, "the census must be present without a placement"
        assert h["census"]["absent"] == 1
        assert [f for f in c["findings"] if f.get("kind") == "room-without-a-hearth"], (
            "the dining room's missing fire is a fact about the RECORD and needs no placement")
        assert "hearths" not in (c.get("drawn_summary") or {}), (
            "it must not also be published under drawn_summary — two spellings of one census "
            "is how a reader comes to quote the one that is silent")

    def test_a_missing_hearth_is_a_finding_that_quotes_the_record(self):
        p = tidewater()
        for lv in p["levels"]:
            for r in lv["rooms"]:
                if r["id"] == "drawing":
                    r.pop("hearth", None)
        placed = GEO.solve(p, None, 60, engine="heuristic")
        c = PC.check(placed)
        f = next((f for f in c["findings"]
                  if f.get("kind") == "room-without-a-hearth" and f.get("room") == "drawing"),
                 None)
        assert f is not None
        assert "chimneypiece" in f["statement"], "the finding must quote the record it rests on"

    def test_a_hearth_off_the_massings_stack_wall_is_REPORTED_and_not_resolved(self):
        """THE SECOND BLIND GUARD OF THIS PACKAGE, and it was blind the way WP-8.11's opt-in
        fixtures were: the check was written, and nothing in the corpus drove it. All three of
        the Tidewater plan's hearths sit on E or W, which is exactly where `gable-end-paired`
        puts its stacks, so deleting the finding entirely left the suite green. It has to be
        driven by a fixture that disagrees with the massing on purpose."""
        p = tidewater()
        for lv in p["levels"]:
            for r in lv["rooms"]:
                if r["id"] == "dining":
                    r["hearth"] = [dict(r["hearth"][0], wall="N")]
        placed = GEO.solve(p, None, 60, engine="heuristic")
        c = PC.check(placed)
        f = next((f for f in c["findings"]
                  if f.get("kind") == "hearth-off-the-stack-wall"
                  and f.get("room") == "dining"), None)
        assert f is not None, "a hearth on N under gable-end-paired must be reported"
        assert "N" in f["statement"] and "E/W" in f["statement"]
        assert "reported rather than resolved" in f["statement"], (
            "rooms/dining-room.json puts the dining fire on the interior wall opposite the "
            "sideboard whatever the massing pairs — both may be right, so this may not convict")

    def test_the_ONLY_comparison_made_is_against_the_massing(self, C):
        """A GUARD AGAINST THIS PACKAGE'S OWN FALSE CLAIM. The Tidewater dining hearth was
        authored with a note saying its disagreement with `rooms/dining-room.json` -- which puts
        the dining fire on *"the interior wall opposite the sideboard"* -- *"is reported by
        build/hearths.py"*. It is not: the only comparison is against the MASSING's stack walls,
        and W is where gable-end-paired puts them, so it passes. The note is corrected and this
        pins the actual scope, so the next reader cannot take the absence of a finding for a
        comparison that was made and came back clean.
        `oq/a-room-record-names-the-wall-its-fire-stands-on-and-nothing-compares-it`."""
        p = tidewater()
        dining = next(r for lv in p["levels"] for r in lv["rooms"] if r["id"] == "dining")
        assert dining["hearth"][0]["wall"] == "W"
        rec = C["rooms"]["dining-room"]
        assert "interior wall" in rec["servicing"]["heat"], "the record still says interior"
        rep = HE.hearth_report(p, C)
        row = next(r for r in rep["rooms"] if r["room"] == "dining")
        assert row["state"] == "stated"
        assert "off_the_stack_wall" not in row, (
            "W agrees with the massing; if this ever fires, the scope changed and the note on "
            "the plan record and the register entry both need re-reading")
        assert "wall_the_record_names" not in row, (
            "no such comparison exists yet — see the register entry before adding one, the "
            "prose reader it needs is 2-of-5 precise")

    def test_and_the_shipped_plan_does_NOT_raise_it(self):
        """The complement, without which the test above proves only that the checker fires."""
        placed = GEO.solve(tidewater(), None, 60, engine="heuristic")
        c = PC.check(placed)
        assert not [f for f in c["findings"]
                    if f.get("kind") == "hearth-off-the-stack-wall"]

    def test_the_plate_draws_the_breast(self, tmp_path):
        RP = modcache.load("render_plan", os.path.join(ROOT, "build", "render_plan.py"))
        placed = GEO.solve(tidewater(), None, 60, engine="heuristic")
        out = str(tmp_path / "sheet.svg")
        RP.render(placed, out)
        svg = open(out, encoding="utf-8").read()
        assert svg.count("fireplace,") == 3, "three stated hearths, three breasts on the plate"
        assert "Morris 1734, judgment" in svg, (
            "the plate must say the projection is a judgment, not a measurement")
