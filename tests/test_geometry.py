"""Pins the geometry solver's spanning rule — see docs/geometry.md: 'a room
with exterior walls on OPPOSITE sides has to run the full depth or width...
which is exactly what a centre passage is, and why slicing it like any other
room produces a treemap instead of a plan.' Only circulation rooms span —
a porch with three exterior walls wants the south edge, not a slab through
the middle of the house.
"""
import json
import os
import re

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestSpanningRule:
    def test_circulation_room_with_opposite_exterior_walls_spans(self, geometry_module):
        room = {"id": "cp", "type": "centre-passage", "exterior_walls": ["S", "N"]}
        result = geometry_module.spanning([room], "y")
        assert result is not None
        assert result["id"] == "cp"

    def test_circulation_room_with_one_exterior_wall_does_not_span(self, geometry_module):
        room = {"id": "cp", "type": "centre-passage", "exterior_walls": ["S"]}
        assert geometry_module.spanning([room], "y") is None

    def test_non_circulation_room_with_opposite_walls_does_not_span(self, geometry_module):
        """A porch is not circulation — even with walls on both opposite
        sides it must not become a slab through the house."""
        room = {"id": "porch", "type": "entry-porch", "exterior_walls": ["S", "N", "E"]}
        assert geometry_module.spanning([room], "y") is None

    def test_spans_on_x_axis_for_east_west_walls(self, geometry_module):
        room = {"id": "cp", "type": "centre-passage", "exterior_walls": ["E", "W"]}
        assert geometry_module.spanning([room], "x") is not None
        assert geometry_module.spanning([room], "y") is None


class TestSolveSmoke:
    """A minimal end-to-end check that solve() still runs on the shipped,
    carefully-composed Tidewater plan and returns dimensioned, placed rooms
    with every relaxation off the bay grid counted rather than silently
    absorbed — decision not to undo #11."""

    def test_solve_places_every_room_and_counts_relaxations(self, geometry_module):
        """Pins the current relaxation count (11, as of 23 Aug 2026 — the
        state-of-project review's narrative number of 10 had already drifted
        by one; this test protects the number that's actually live, and a
        deliberate change to the solver should update it in the same commit).
        WP-2.3 was that deliberate change: solve() now dispatches to the
        CP-SAT engine by default, so the 11 is pinned against the HEURISTIC
        engine explicitly — it is the slicer's own number, and the heuristic
        remains the labelled fallback and cross-check. tests/test_solver.py
        covers the CP engine's own properties.
        Both levels are solved and scored TOGETHER (decision #11) — this is
        what 'vertical_score' being present and nonzero-capable proves; an
        upper floor solved independently could not know about walls below."""
        import json
        import os
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        plan = json.load(open(os.path.join(root, "plans", "tidewater-georgian-careful.json")))
        result = geometry_module.solve(plan, engine="heuristic")
        report = result["geometry_report"]
        # 5, moved from 7 by WP-11.2, and the reason is the BAY GRID rather than the slicer: the plan now names its parti, so the placement takes the diagram's own 9 ft module instead of the placer's 10 ft default, and the massing's `bays: "5"` makes the count odd -- seven bays of 9 ft (63.0 x 38.2) where it was six of 10 (60.0 x 40.1). A cut is a relaxation when it misses the bay module, so changing the module changes which cuts miss. It is a smaller number and it is NOT thereby an improvement in the house: the same change costs about three fatal findings on this engine (8-seed means 6.2 -> 9.2, all unreachable rooms) and zero on CP-SAT. Read `docs/reports/wp-11.2-the-diagram-reaches-the-record.md` before moving it again. Previously: 7, moved from 9 by WP-7.4 -- the span term charges an over-capacity clear span, and the only way the slicer can create a bearing line is to cut ON the bay module -- so a term aimed at structure pulls cuts onto the grid, and a cut on the grid is not a relaxation. Measured on this plan with the two terms off and on: 9 -> 7 here and 7 -> 4 on spec-builder-colonial. It is an improvement and it is still a number that must not move BY ACCIDENT. Previously: 9, moved from 11 by WP-7.1 (OQ 95). The upper level is now sliced against the ground layout instead of blind, so an upper cut lands on a wall below where one is within tolerance — and a cut that lands on a wall below is not a compromise, because a relaxation is defined in geometry.py's own prose as a joist run that does not land on a bearing wall. The code had approximated that as 'misses the bay module', and 18 of 30 ground wall lines are themselves off the bay grid. Measured corpus-wide on 14 composed plans: relaxations 96 -> 76, transfer beams 166 -> 109.
        # STAYS 7. WP-9.4 measured a corrected clamp (geometry._clamp_cut) that would move it
        # to 8, and REFUSED it: the same change takes the entry porch's clear depth 6.0 -> 5.0
        # and re-fires `porch-nobody-can-sit-on`, which WP-7.4 had cleared. Read _clamp_cut's
        # docstring before trying it again -- the arithmetic there is right and the shipped
        # expression is wrong, and shipping the fix alone still makes the corpus worse.
        # STAYS 5, AND WP-11.5 MEASURED WHAT WOULD MOVE IT. Declared stacking as a RULE rather
        # than a charge (`geometry.STACK_HARD`, default False) takes this number to 6: the
        # strict candidate costs 17.0 points here and carries one more off-grid cut, while
        # taking this plan's broken stacking claims from 1 to 0. It is defaulted off because on
        # `spec-builder-colonial` the same rule introduces two over-capacity clear spans where
        # there were none, the worst 40.0 ft against a 20 ft capacity. Read
        # `docs/reports/wp-11.5-stacking-as-a-rule.md` before flipping it; clear `_SOLVE_CACHE`
        # between settings, because the cache is keyed on call arguments and not on constants.
        assert report["relaxations"]["count"] == 5
        assert "vertical_score" in report, "both levels must be scored together, not independently"
        placed_rooms = [
            r for lv in result["levels"] for r in lv["rooms"]
        ]
        unplaced = [r for r in placed_rooms if "geometry" not in r]
        # Outdoor rooms (a terrace, a porch modelled as open-air) are outside
        # the indoor bay-grid solve by design — is_indoor() filters them out.
        # Every INDOOR room must come back placed.
        unplaced_indoor = [r for r in unplaced if r["type"] != "terrace"]
        assert not unplaced_indoor, f"indoor rooms with no placed geometry: {unplaced_indoor}"
        assert len(placed_rooms) - len(unplaced) > 20, "expected the bulk of the plan to be placed"


class TestUnderBandIsReported:
    """OQ 54, ruled 24 Aug 2026. The search may trade a room's size against everything else it
    scores — that is what a heuristic is for — but the plan record still carries the room's
    DECLARED size and nothing downstream reads these coordinates, so the trade was invisible."""

    def test_the_spec_colonials_squeezed_dining_room_is_named(self, geometry_module):
        """The finding OQ 54 was raised about: 90 sf against a 122 sf band floor, on every seed,
        while the plan record still says 12 x 12."""
        import json, os
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        plan = json.load(open(os.path.join(root, "plans", "spec-builder-colonial.json")))

        # engine="heuristic" EXPLICITLY. OQ 54 is a finding about the hill-climb: it charges a
        # flat 12 points for a room under its band and a candidate can win while paying it.
        # `solve()` defaults to CP-SAT since the 25 Aug merge, and the CP engine places this
        # dining room in band — so calling the default here stopped testing the thing the
        # question is about and started testing an engine that does not have the defect.
        out = geometry_module.solve(json.loads(json.dumps(plan)), engine="heuristic")
        ub = out["geometry_report"]["under_band"]
        # WP-7.4: THE DINING ROOM IS IN BAND NOW AND THE STAIR HALL IS NOT, so this asserts the
        # MECHANISM rather than the room. Measured on this plan with the two score terms off and
        # on: under_band 2 (entrance-hall, dining-room) -> 1 (stair-hall). OQ 54's own worked
        # example came right as a side effect of charging spans and stacks, which is worth
        # knowing and is not what this test exists to protect. What it protects is that the
        # hill-climb WILL trade a room below its own catalogue floor, and that the trade is
        # visible: named, measured against the floor it missed, and set beside the size the
        # record still declares. Naming a specific room pinned an accident.
        assert ub["count"] >= 1, (
            "the hill-climb reported no under-band room at all — investigate before "
            "celebrating; this engine has made that trade on this plan since OQ 54 was raised")
        for r in ub["rooms"]:
            assert r.get("type") and r.get("name"), r
            assert r["placed_sf"] < r["band_floor_sf"], r
            # the divergence OQ 54 is actually about: the record still says something else
            assert r.get("declared_sf"), r
            assert r.get("short_by_pct") and r.get("declared_short_by_pct") is not None, r
        # WP-7.4: the dining room is no longer the one squeezed on this plan, so asserting on
        # it by name would pin an outcome the terms just changed. What still holds is that the
        # room the hill-climb DOES squeeze is squeezed materially, not by a rounding.
        #
        # STAYS >= 20, AND WP-11.5 MEASURED THE RULE THAT WOULD MOVE IT TO 16. Declared
        # stacking as a rule (`geometry.STACK_HARD`, default False) subdivides this ground floor
        # differently and the rooms come out markedly better:
        #
        #   off  Stair Hall 36 sf against a 76 sf floor, 53% SHORT; Mud Room 28 vs 34, 16%
        #   on   Stair Hall 64 sf, 16% short; Mud Room 32, 6%; Study 64 vs 76, 16% (new)
        #
        # The worst squeeze more than halves, the stair hall gains 78% of its own area, and total
        # shortfall falls 46 sf -> 30 sf across one more room. It is still defaulted off, because
        # the same candidate introduces two over-capacity clear spans on this plan where there
        # were none -- the worst 40.0 ft against a 20 ft capacity. Better rooms, worse structure,
        # on one plan; the other plan trades the opposite way. That is a ruling and not a default.
        worst = max(ub["rooms"], key=lambda r: r["short_by_pct"])
        assert worst["short_by_pct"] >= 20, worst

        # And the good news, pinned so it cannot regress unnoticed: the CP engine does NOT make
        # this trade on the same record. That is the concrete difference between scoring a
        # room's minimum and enforcing it, on the plan the question was raised about.
        # THIS ASSERTION IS OUTSIDE THE CP GATE ON PURPOSE. An audit found it nested inside
        # `if solver.engine == "cp-sat"`, which meant that with no ortools, on a slower box, or
        # on a CP timeout, the whole test degraded to a shape check that could not detect the
        # WP-7.4 revert at all -- and the sibling test's own docstring records that CP on this
        # plan is wall-clock nondeterministic. It runs on the HEURISTIC result already computed
        # above, which is deterministic, and it is the one assertion here that fails on revert:
        # with the score terms off this plan's under-band set is {entrance-hall, dining-room}.
        assert "dining-room" not in {r["type"] for r in ub["rooms"]}, (
            "the dining room is under band again on the hill-climb; WP-7.4's score terms put "
            "it in band (under_band 2 -> 1, the stair hall taking its place) and something "
            "has undone that")
        # The CP half stays gated, because it genuinely cannot be evaluated without a solve --
        # and it reports COULD NOT EVALUATE rather than passing when the engine did not run.
        cp = geometry_module.solve(json.loads(json.dumps(plan)), engine="auto")
        cp_engine = (cp.get("geometry_report", {}).get("solver") or {}).get("engine")
        if cp_engine == "cp-sat":
            cp_names = {r["type"] for r in cp["geometry_report"]["under_band"]["rooms"]}
            assert "dining-room" not in cp_names, (
                "the CP engine used to place this room in band; if it no longer does, the "
                "room minimum has stopped being enforced")
        else:
            pytest.skip(f"CP did not run (engine={cp_engine!r}) — the CP half is unjudged here, "
                        f"not passed; the heuristic half above still ran")

    def test_a_layout_with_nothing_under_band_says_so_rather_than_going_quiet(self, geometry_module):
        rects = {0: {"a": (0.0, 0.0, 20.0, 20.0)}}
        prep = {0: [{"id": "a", "type": "parlor", "name": "Parlor"}]}
        assert geometry_module.under_band(rects, prep) == []


def _tagged_dependency_plan():
    """A two-element plan, tagged BY HAND rather than composed.

    The composer does not write `block` on any room and deliberately does not: the packages that
    would have taught it to (the parti strip and the dependency stocking) were reverted on 3 Sep
    2026 when an audit found five further defects downstream of them -- openings drawn on the
    wrong wall, the lot cap bypassed, `derive_footprint` sizing the main block for rooms that had
    left it. The block MACHINERY below it stands and is what these tests exercise, so the fixture
    states the tag the composer will one day write. If a future package makes the composer write
    it, these tests should switch to that path and the switch should be visible in the diff --
    which is why this helper is one function rather than a line inlined in three classes.
    """
    import json, os
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    plan = json.load(open(os.path.join(root, "plans", "tidewater-georgian-careful.json")))
    tagged = 0
    for r in plan["levels"][0]["rooms"]:
        if r["type"] in ("kitchen", "pantry", "breakfast-room"):
            r["block"] = "west-dependency"
            r["exterior_walls"] = ["N", "S", "W"]
            tagged += 1
    assert tagged >= 2, "the reference plan's service room types have been renamed"
    return plan


class TestASecondMassingElement:
    """OQ 40, ruled 3 Sep 2026: a dependency is a second massing element, not a second level.

    The discipline the whole change is held to is that a plan declaring no second block must
    place BYTE-IDENTICALLY -- all sixteen plans in this corpus are one rectangle and two of them
    ship, so their placements are the regression guard. These tests pin both halves: that one
    block still goes through the one-block path, and that a second block is actually placed
    outside the first rather than sliced out of it."""

    @staticmethod
    def _plan(name):
        import json, os
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return json.load(open(os.path.join(root, "plans", name + ".json")))


    def test_a_one_block_plan_reports_exactly_one_element_at_the_origin(self, geometry_module):
        g = geometry_module
        plan = self._plan("tidewater-georgian-careful")
        levels, prep = g.prep_rooms(plan)
        fp = g.derive_footprint(plan, None, prep)
        blocks = g.blocks_for(plan, fp, prep, 0)
        assert len(blocks) == 1
        b = blocks[0]
        assert b["role"] == "main"
        # `b["x"] == 0` CANNOT FAIL against a float: `0.0 == 0` is True in Python, so the first
        # version of this assertion pinned the claim its own comment makes and would have stayed
        # green through the very mutation it names. The type is the claim, so the type is what is
        # asserted -- and `bool` is excluded because `True == 1` and `isinstance(True, int)` are
        # both true, which would let a third wrong type through the guard against the second.
        for axis in ("x", "y"):
            v = b[axis]
            assert type(v) is int, (
                f"the main block's {axis} is {v!r} ({type(v).__name__}) -- it must sit at the "
                "INTEGER origin. A float there writes `x_ft: 0.0` where the record carried "
                "`x_ft: 0`: numerically identical, textually not, and it made a placement-hash "
                "comparison report both shipped plans as moved when they had not.")
        assert set(b["rooms"]) == {r["id"] for r in prep[0]}, "every room belongs to the one block"

    def test_a_one_block_plan_writes_no_blocks_key(self, geometry_module):
        """Sixteen records that have never needed the key must not grow one."""
        g = geometry_module
        plan = self._plan("spec-builder-colonial")
        g._SOLVE_CACHE.clear()
        g.solve(plan, engine="heuristic")
        assert "blocks" not in (plan.get("footprint") or {})

    def test_a_tagged_room_is_placed_outside_the_main_block(self, geometry_module):
        """The point of the whole change: a dependency is BESIDE the house, not carved out of it.

        Without this, tagging rooms into a block would be an expensive way of relabelling them
        while the slicer went on cutting one rectangle -- which is what expressing a dependency
        as a level would have done, silently."""
        g = geometry_module
        plan = _tagged_dependency_plan()
        tagged = {r["id"] for r in plan["levels"][0]["rooms"] if r.get("block")}
        assert tagged, "the fixture tagged nothing -- the room types have been renamed"
        g._SOLVE_CACHE.clear()
        g.solve(plan, engine="heuristic")

        blocks = plan["footprint"]["blocks"]
        assert blocks[0]["id"] == "main", "main block is always first"
        dep = next(b for b in blocks if b["id"] == "west-dependency")
        assert dep["role"] == "dependency" and dep["attached_to"] == "main"

        placed = {r["id"]: r.get("geometry") for lv in plan["levels"] for r in lv["rooms"]}
        for rid in tagged:
            gm = placed[rid]
            assert gm, f"{rid} was tagged into a block and then not placed at all"
            assert gm["x_ft"] + gm["width_ft"] <= 0.01, (
                f"{rid} is drawn inside the main block at x={gm['x_ft']} -- a dependency must be "
                "placed outside it, across the hyphen")
        main_x = [gm["x_ft"] for rid, gm in placed.items() if gm and rid not in tagged]
        assert min(main_x) >= 0.0, "no main-block room drifted west of the origin"

    def test_the_gap_between_the_blocks_is_the_hyphens_own_band(self, geometry_module):
        """The separation is not arbitrary: dependency-and-hyphen.json bands hyphen_length_ft at
        12-20 ft and the default sits inside it. When a hyphen ROOM is placed it will state its
        own width and this constant stops being read -- that is the next package, and this test
        is what should notice."""
        g = geometry_module
        assert 12.0 <= g.HYPHEN_DEFAULT_FT <= 20.0
        plan = _tagged_dependency_plan()
        g._SOLVE_CACHE.clear()
        g.solve(plan, engine="heuristic")
        dep = next(b for b in plan["footprint"]["blocks"] if b["id"] == "west-dependency")
        gap = 0.0 - (dep["x_ft"] + dep["width_ft"])
        assert abs(gap - g.HYPHEN_DEFAULT_FT) < 0.01, f"gap {gap} is not the hyphen band's width"
        # The two assertions above are one claim read twice unless the constant is pinned to the
        # RECORD rather than to itself: `12 <= HYPHEN_DEFAULT_FT <= 20` and `gap == HYPHEN_DEFAULT_FT`
        # both stay green if somebody moves the constant to 19 and the grouping's band to 18-24.
        # This reads the band out of the grouping file, which is where the rule actually lives.
        grp = json.load(open(os.path.join(ROOT, "groupings", "dependency-and-hyphen.json")))
        rule = next(r for r in grp["internal_rules"] if "hyphen_length_ft" in (r.get("test") or ""))
        nums = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", rule["test"])]
        assert len(nums) >= 2, f"the hyphen rule no longer states a band: {rule['test']!r}"
        assert nums[0] <= gap <= nums[1], (
            f"the drawn gap {gap} ft is outside the grouping's own hyphen band {nums[0]}-{nums[1]}")

    def test_a_wing_rooms_walls_are_the_wings_own(self, geometry_module):
        """exterior_score must charge a dependency room against the DEPENDENCY's perimeter.
        Charged against the main block's it would be missing walls it actually has, at 14 points
        each, and the solver would pull every wing room back inside to stop paying."""
        g = geometry_module
        # The discriminating wall is the dependency's EAST one -- the face that looks back across
        # the hyphen at the house. A first version of this test used the west wall and could not
        # fail: a room at negative x is already past the main block's west edge, so `W` was
        # satisfied either way and both calls returned 0.0. The test was measuring nothing.
        rooms = [{"id": "k", "exterior_walls": ["N", "S", "E"]}]
        rects = {"k": (-34.0, 0.0, 20.0, 40.0)}          # a west dependency, its east face at -14
        bounds = {"k": (-34.0, 0.0, 20.0, 40.0)}
        assert g.exterior_score(rects, rooms, 60.0, 40.0, bounds=bounds) == 0.0, (
            "against its own element the wing room has all three walls it declares")
        assert g.exterior_score(rects, rooms, 60.0, 40.0) == 14.0, (
            "against the MAIN block's perimeter its east wall is 74 ft away and it is charged one "
            "wall at 14 points -- which is the pull that would drag every dependency room back "
            "inside the house if bounds were not passed")


class TestCPRefusesASecondMassingElement:
    """OQ 40, from the adversarial audit of the change that introduced blocks (3 Sep 2026).

    geometry_cp builds every room as `x = NewIntVar(0, Wi)` with `x + w <= Wi`: one rectangle,
    one non-negative coordinate space. Handed a plan with a dependency it did NOT fail -- it
    placed the dependency's rooms inside the main block (the garage at x = 50 of a 0-70 block)
    while `footprint.blocks` went on describing an element at x = 84-114. The record and the
    drawing disagreed about where the house is.

    It also flattered a measurement: rooms crammed into one rectangle are all reachable, so the
    fatal count read as a proof of the composition when it was a proof of something else. The
    engine refuses now, and `auto` falls back with the reason stated."""

    @staticmethod
    def _plan_with_a_dependency():
        return _tagged_dependency_plan(), None

    def test_engine_cp_refuses_rather_than_flattening_the_dependency(self, geometry_module):
        plan, C = self._plan_with_a_dependency()
        assert any(r.get("block") for lv in plan["levels"] for r in lv["rooms"]), \
            "the fixture must carry a dependency or this proves nothing"
        geometry_module._SOLVE_CACHE.clear()
        out = geometry_module.solve(plan, C, engine="cp")
        assert out.get("error") and "massing element" in out["error"], (
            "CP must refuse a multi-element plan, not place it in one rectangle")
        assert out.get("unsolved") is True

    def test_auto_falls_back_and_says_why(self, geometry_module):
        plan, C = self._plan_with_a_dependency()
        geometry_module._SOLVE_CACHE.clear()
        geometry_module.solve(plan, C, engine="auto")
        solver = plan["geometry_report"]["solver"]
        assert solver["engine"] == "heuristic" and solver.get("fallback") == "engine"
        assert "massing element" in solver["reason"], (
            "the plate reads this reason; it must name the real cause, not 'budget'")

    def test_and_the_fallback_actually_places_the_dependency_outside(self, geometry_module):
        """The point of falling back rather than proceeding: the engine that runs must put the
        dependency where the record says it is."""
        plan, C = self._plan_with_a_dependency()
        geometry_module._SOLVE_CACHE.clear()
        geometry_module.solve(plan, C, engine="auto")
        fw = plan["footprint"]["width_ft"]
        dep = [r for lv in plan["levels"] for r in lv["rooms"] if r.get("block") and r.get("geometry")]
        assert dep
        for r in dep:
            g = r["geometry"]
            assert g["x_ft"] >= fw - 0.01 or g["x_ft"] + g["width_ft"] <= 0.01, (
                f"{r['id']} at x={g['x_ft']} is inside the main block (0..{fw}) while "
                "footprint.blocks says it is a separate element")


class TestTheAuditGapsInTheBlockWork:
    """Three behaviours the block change introduced with NO test, found by the adversarial audit
    of it. Each mutation below left the whole geometry and garage suites green."""

    @staticmethod
    def _dep_plan():
        return _tagged_dependency_plan(), None

    def test_a_block_field_that_is_not_a_string_is_ignored_rather_than_crashing(self, geometry_module):
        """Gap #4, and the one that reached the network. `blocks_for` grouped rooms with
        `by.setdefault(r["block"], [])`, so a `block` arriving as a list or a dict raised
        `TypeError: unhashable type` -- and `POST /api/drawings` takes a plan record verbatim from
        anyone who can reach it, outside the schema, so that is an unauthenticated HTTP 500 from a
        field the schema types `string`.

        Ignoring it puts the room in the main block, which is the conservative answer and the same
        one a record written before this field existed already gets. Asserted per shape, because
        `bool(v)` -- the version this replaced -- is True for a non-empty dict and False for an
        empty one, so a guard tested on only one of them proves nothing about the other."""
        g = geometry_module
        for bad in ([], {}, ["west"], {"id": "west"}, 3, 0, True, None, "", "   "):
            plan = _tagged_dependency_plan()
            for r in plan["levels"][0]["rooms"]:
                if r.get("block"):
                    r["block"] = bad
            g._SOLVE_CACHE.clear()
            out = g.solve(plan, None, engine="heuristic")     # must not raise
            assert "error" not in out, f"block={bad!r} refused the plan: {out.get('error')}"
            assert "blocks" not in (plan.get("footprint") or {}), (
                f"block={bad!r} was read as a massing-element id -- only a non-empty string is one")
            for lv in plan["levels"]:
                for r in lv["rooms"]:
                    gm = r.get("geometry")
                    assert gm is None or gm["x_ft"] >= -0.01, (
                        f"block={bad!r} put {r['id']} outside the single block at x={gm['x_ft']}")

    def test_the_solver_hands_exterior_score_the_per_element_bounds(self, geometry_module):
        """Gap #2, and THE FIRST VERSION OF THIS TEST WAS GREEN ON ITS OWN MUTATION.

        It asserted the consequence its own comment claimed -- 'the solver would pull every
        dependency room back into the main rectangle to stop paying' -- and deleting
        `bounds=gbounds` from the call site left it green. The claim is false: `slice_rect` cuts
        each element's rooms out of THAT ELEMENT'S rectangle, so a dependency room is confined to
        the dependency by construction and no score can relocate it. There was no consequence to
        assert, and asserting one anyway produced a guard that could not fail -- which is the
        exact family this class exists to catch, committed inside the class that catches it.

        What `bounds` really changes is the SCORE, and therefore which candidate wins. That is
        measured here rather than asserted in the abstract: on the winning placement the two
        readings differ by a real margin, so the ranking the solver did is not the ranking it
        would have done. The call site is then read directly. A call-site assertion is the weaker
        form and is used because the stronger one does not exist, which is worth saying out loud.
        """
        g = geometry_module
        plan, _C = self._dep_plan()
        g._SOLVE_CACHE.clear()
        g.solve(plan, None, engine="heuristic")

        levels, prep = g.prep_rooms(plan)
        fpd = g.derive_footprint(plan, None, prep)
        blocks = g.blocks_for(plan, fpd, prep, 0)
        assert len(blocks) == 2, "the fixture must place two elements"
        bounds = {rid: (b["x"], b["y"], b["W"], b["H"]) for b in blocks for rid in b["rooms"]}
        rects = {r["id"]: (r["geometry"]["x_ft"], r["geometry"]["y_ft"],
                           r["geometry"]["width_ft"], r["geometry"]["depth_ft"])
                 for r in plan["levels"][0]["rooms"] if r.get("geometry")}
        bounded = g.exterior_score(rects, prep[0], fpd["W"], fpd["H"], bounds=bounds)
        unbounded = g.exterior_score(rects, prep[0], fpd["W"], fpd["H"])
        assert unbounded > bounded, (
            f"the two readings agree ({bounded}) on this placement, so this fixture no longer "
            "discriminates and the call-site check below is the only thing left standing")
        assert unbounded - bounded >= 14.0, (
            f"the gap is {unbounded - bounded} points, under one wall's charge -- too small to "
            "be sure a mis-ranked candidate would ever change the answer")

        # And that the solver is the one reading it. Wrapping the function is the only way to
        # observe an argument at a call site; the module attribute is restored either way.
        seen = []
        real = g.exterior_score
        def spy(*a, **kw):
            seen.append(kw.get("bounds"))
            return real(*a, **kw)
        g.exterior_score = spy
        try:
            g._SOLVE_CACHE.clear()
            g.solve(plan, None, engine="heuristic")
        finally:
            g.exterior_score = real
        assert seen, "the solver never scored exteriors at all -- this guard has gone blind"
        assert any(b for b in seen), (
            "the solver scores every candidate's exterior walls against the MAIN block's "
            "perimeter: a dependency room is charged 14 points for each wall it really has, on "
            f"every candidate, and the winner is chosen on a score {unbounded - bounded} points "
            "wrong. `bounds=gbounds` is what stops that.")

    def test_a_dependency_is_sized_single_pile_not_against_the_main_blocks_pile(self, geometry_module):
        """Gap #3, AND THE FIRST VERSION OF THIS TEST WAS ALSO GREEN ON ITS OWN MUTATION.

        It ran the tidewater fixture end to end and asserted the dependency's depth was within
        1.25x of `PILE['single-pile']`. Switching the constant to `double-pile` left it green:
        that programme is 542 sf and `round(542/22/10)` and `round(542/36/10)` are BOTH 2, so the
        rule under test made no difference to the fixture's answer. A mutation that changes
        nothing is not evidence that nothing is wrong -- it is evidence the fixture is blind.

        `bays = max(1, round((need/depth)/bay))` only moves where the two quotients straddle a
        rounding boundary, so the areas here are chosen to straddle one: at 400 sf the single-pile
        rule gives 2 bays of 20 x 20, the double-pile rule 1 bay of 10 x 40 -- the 'splinter' the
        code's own comment describes. The end-to-end shape assertion is kept below it, because a
        unit test of the arithmetic does not prove the solver calls it."""
        g = geometry_module
        fp = {"W": 60.0, "H": 40.0, "bay": 10.0, "target_depth": 36.0}
        prep = {0: [{"id": "hall", "type": "hall", "_area": 800.0},
                    {"id": "k", "type": "kitchen", "_area": 250.0, "block": "dep",
                     "exterior_walls": ["W"]},
                    {"id": "p", "type": "pantry", "_area": 150.0, "block": "dep",
                     "exterior_walls": ["W"]}]}
        blocks = g.blocks_for({"levels": []}, fp, prep, 0)
        dep = next(b for b in blocks if b["role"] == "dependency")
        assert (dep["W"], dep["H"]) == (20.0, 20.0), (
            f"400 sf of dependency came out {dep['W']} x {dep['H']} ft. Against a single-pile "
            f"depth of {g.PILE['single-pile']} it is 20 x 20; against the main block's "
            f"{fp['target_depth']} ft it is a 10 x 40 splinter, which is the defect this rule "
            "was written to fix.")

        # And the solver really uses it, on a real plan.
        plan, _C = self._dep_plan()
        g._SOLVE_CACHE.clear()
        g.solve(plan, None, engine="heuristic")
        real = next(b for b in plan["footprint"]["blocks"] if b["role"] == "dependency")
        assert real["width_ft"] >= real["depth_ft"] * 0.5, (
            f"{real['width_ft']} x {real['depth_ft']} ft is a splinter, not a dependency")

    def test_a_multi_element_placement_discloses_what_it_does_not_judge(self, geometry_module):
        """Gap #5, and the reason the block machinery may stay in the tree after the composer
        packages above it were reverted.

        Five layers below the placer read `footprint.width_ft/depth_ft` as the whole building,
        and an adversarial audit measured each one wrong on a dependency room: a garage window
        drawn fourteen feet from the garage, a clear span manufactured across the hyphen gap, an
        upper wall supported by a wall under no upper floor, a lot cap that caps the main block
        while the built extent runs 34 ft past the lot line, and a critic convicting a dependency
        room of reaching no exterior wall. None of that is fixed. The composer emits no `block`,
        so the only way to reach it is a caller-supplied record -- which is precisely the reader
        who cannot know, which is why the record says so itself.

        A one-rectangle plan must carry NO such key: sixteen records that have never needed one
        are the byte-identity guard the whole change is held to."""
        g = geometry_module
        plan = _tagged_dependency_plan()
        g._SOLVE_CACHE.clear()
        g.solve(plan, None, engine="heuristic")
        me = plan["geometry_report"].get("multi_element")
        assert me, "a two-element placement reports the five layers' numbers and discloses nothing"
        assert me["elements"] == 2
        assert set(me["not_element_aware"]) == {
            "openings", "structure", "vertical_score", "lot_cap", "plan_check.drawn", "export_ifc"}
        assert "COULD NOT EVALUATE" in me["note"], (
            "the disclosure must use the corpus's own words for an unjudged state, or a reader "
            "takes it for a caveat rather than a verdict")
        assert "ignored_tags_above_ground" not in me

        # A tag the placer cannot read is named rather than silently dropped. The schema admits
        # `block` on ANY room; `blocks_for` is only ever called with level=0.
        plan = _tagged_dependency_plan()
        upper = plan["levels"][1]["rooms"]
        upper[0]["block"] = "west-dependency"
        g._SOLVE_CACHE.clear()
        g.solve(plan, None, engine="heuristic")
        me = plan["geometry_report"]["multi_element"]
        assert me["ignored_tags_above_ground"] == [upper[0]["id"]], (
            "an upper room tagged into a dependency was placed in the main rectangle and nothing "
            "said so")
        assert upper[0]["geometry"]["x_ft"] >= -0.01, "and it really was placed in the main block"

    def test_a_one_block_plan_discloses_nothing_because_there_is_nothing_to_disclose(self, geometry_module):
        g = geometry_module
        import json as _j, os as _o
        root = _o.path.dirname(_o.path.dirname(_o.path.abspath(__file__)))
        for name in ("tidewater-georgian-careful", "spec-builder-colonial"):
            plan = _j.load(open(_o.path.join(root, "plans", name + ".json")))
            g._SOLVE_CACHE.clear()
            g.solve(plan, engine="heuristic")
            assert "multi_element" not in plan["geometry_report"], (
                f"{name} is one rectangle and grew a key -- the byte-identity guard is broken")

    def test_the_recorded_block_is_measured_on_the_rooms_the_placer_places(self, geometry_module):
        """Gap #6, and it was green on its own mutation until this test existed.

        `blocks_record`'s prep was built inline at two call sites and neither applied
        `is_placed()`, which the slicing path applies in `prep_rooms`. A room the placer never
        gives a rectangle to -- a terrace, any outdoor room without `void.within_footprint` --
        still counted toward its element's area and toward the side its `exterior_walls` vote
        for, so `footprint.blocks` described a rectangle no room occupies. Both call sites read
        `_record_prep` now.

        Driven directly rather than through a plan, because the corpus has no parti that puts an
        unplaced room in a dependency and inventing one to test the filter would be testing the
        fixture. The two sizings must agree: what is sliced is what is recorded."""
        g = geometry_module
        fp = {"W": 60.0, "H": 40.0, "bay": 10.0, "target_depth": 36.0}
        rooms = [{"id": "hall", "type": "hall", "width_ft": 20, "length_ft": 40},
                 {"id": "gar", "type": "garage", "width_ft": 20, "length_ft": 22,
                  "block": "dep", "exterior_walls": ["W"]},
                 {"id": "terr", "type": "terrace", "width_ft": 30, "length_ft": 20,
                  "block": "dep", "exterior_walls": ["E"]}]
        assert g.is_placed("garage") and not g.is_placed("terrace"), (
            "the fixture's premise has moved: this test needs one placed and one unplaced room "
            "in the same element")
        rec = g.blocks_record({"levels": []}, fp, g._record_prep({0: {"rooms": rooms}}))
        dep = next(b for b in rec if b["role"] == "dependency")
        sliced = next(b for b in g.blocks_for(
            {"levels": []}, fp,
            {0: [dict(r, _area=r["width_ft"] * r["length_ft"]) for r in rooms if g.is_placed(r["type"])]}, 0)
            if b["role"] == "dependency")
        assert (dep["width_ft"], dep["depth_ft"]) == (float(sliced["W"]), float(sliced["H"])), (
            f"the record says the dependency is {dep['width_ft']} x {dep['depth_ft']} ft and the "
            f"slicer cut it {sliced['W']} x {sliced['H']} -- the record describes a rectangle no "
            "room occupies")
        assert dep["width_ft"] == 20.0 and dep["depth_ft"] == 22.0, (
            f"{dep['width_ft']} x {dep['depth_ft']} ft: the unplaced terrace's 600 sf is being "
            "counted into the element's area")

    def test_a_second_west_element_does_not_stack_its_hyphen_on_the_first(self, geometry_module):
        """Gap #7. `hx = 0.0 - gap` was a hardcoded origin where the east branch three lines down
        correctly reads `east_edge` -- and the asymmetry was the whole tell. `west_edge` was being
        advanced and never read, so a SECOND west element put its hyphen back at [-gap, 0], on
        top of the first hyphen and, at these sizes, straight through the first dependency.

        One element hid it, because with one element `west_edge` IS 0. That is the shape this
        session keeps meeting: a defect that cannot show while the thing it needs happens only
        once, in a corpus where it has so far happened only once."""
        g = geometry_module
        fp = {"W": 60.0, "H": 40.0, "bay": 10.0, "target_depth": 36.0}
        rooms = [{"id": "hall", "type": "hall", "_area": 800.0}]
        for i in (1, 2):
            rooms += [{"id": f"h{i}", "type": "breezeway", "_area": 120.0, "block": f"dep{i}",
                       "exterior_walls": ["W"], "hyphen": True, "width_ft": 12.0},
                      {"id": f"g{i}", "type": "garage", "_area": 400.0, "block": f"dep{i}",
                       "exterior_walls": ["W"]}]
        blocks = g.blocks_for({"levels": []}, fp, {0: rooms}, 0)
        west = sorted(((b["x"], b["x"] + b["W"], b["id"]) for b in blocks if b["id"] != "main"),
                      key=lambda t: t[0])
        assert len(west) == 4, f"expected two dependencies and two hyphens, got {[b['id'] for b in blocks]}"
        for (x0, x1, a), (y0, _y1, bname) in zip(west, west[1:]):
            assert x1 <= y0 + 0.01, (
                f"{a} spans {x0}..{x1} and {bname} starts at {y0} -- two massing elements overlap")
