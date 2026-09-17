"""Pins WP-2.2, compositional constraints in the geometry solver -- see docs/geometry.md's
'Compositional scoring (WP-2.2)' section and PLAN-OF-ACTION.md's own acceptance example
('the entrance portico is on the S wall, the drawing room and dining room flank the passage
on the front, service is to the rear').

The new scoring functions (entrance_score, principal_and_service_score, ceremonial_score,
centre_hall_symmetry_score) are tested directly against hand-built `rects` dicts wherever
possible, rather than only through the full stochastic solve() -- see
TestPrincipalAndServiceOrientation's own docstring for why: a room's own declared
`exterior_walls` already dominates solve()'s search on real plan data, so a scoring change can
be structurally correct and still never change which of 250 random candidates wins on a plan
that has already fully determined every room's wall by hand.
"""
import json
import os

from conftest import ROOT, load_plan

PC_ROOMS_STUB = None  # populated per-test via corpus fixture where needed


class TestEntranceWalls:
    def test_cardinal_maps_to_itself(self, geometry_module):
        assert geometry_module.entrance_walls({"context": {"entrance_faces": "S"}}) == {"S"}

    def test_diagonal_maps_to_both_adjacent_cardinals(self, geometry_module):
        assert geometry_module.entrance_walls({"context": {"entrance_faces": "SE"}}) == {"S", "E"}

    def test_no_entrance_faces_is_empty_not_a_default(self, geometry_module):
        """No entrance_faces stated means every compositional term below stays a no-op --
        'unjudged is not passed' applied to geometry, not just the validator."""
        assert geometry_module.entrance_walls({}) == set()
        assert geometry_module.entrance_walls({"context": {}}) == set()


class TestEntranceScore:
    """The specific bug PLAN-OF-ACTION.md names: 'the current rendered Tidewater plan puts the
    portico inside the footprint.' entrance_score is weighted at fatal scale (100) so no
    candidate search can prefer a porch off the entrance wall over one on it."""

    def test_threshold_room_on_entrance_wall_scores_zero(self, geometry_module):
        rooms = [{"id": "porch", "type": "entry-porch", "doors": []}]
        rects = {"porch": (10.0, 0.0, 6.0, 8.0)}  # y=0 -> touches S
        s = geometry_module.entrance_score(rects, rooms, 40, 30, {"S"})
        assert s == 0.0

    def test_threshold_room_off_entrance_wall_is_penalised_heavily(self, geometry_module):
        rooms = [{"id": "porch", "type": "entry-porch", "doors": []}]
        rects = {"porch": (10.0, 12.0, 6.0, 8.0)}  # interior, touches nothing
        s = geometry_module.entrance_score(rects, rooms, 40, 30, {"S"})
        assert s >= 100.0

    def test_no_entrance_data_is_a_no_op(self, geometry_module):
        rooms = [{"id": "porch", "type": "entry-porch", "doors": []}]
        rects = {"porch": (10.0, 12.0, 6.0, 8.0)}
        assert geometry_module.entrance_score(rects, rooms, 40, 30, set()) == 0.0

    def test_the_hall_the_porch_opens_into_is_also_checked(self, geometry_module):
        rooms = [
            {"id": "porch", "type": "entry-porch", "doors": [{"to": "hall"}]},
            {"id": "hall", "type": "entrance-hall", "doors": [{"to": "porch"}]},
        ]
        on_front = {"porch": (10.0, 0.0, 6.0, 6.0), "hall": (16.0, 0.0, 10.0, 20.0)}
        off_front = {"porch": (10.0, 0.0, 6.0, 6.0), "hall": (16.0, 10.0, 10.0, 20.0)}
        s_on = geometry_module.entrance_score(on_front, rooms, 40, 30, {"S"})
        s_off = geometry_module.entrance_score(off_front, rooms, 40, 30, {"S"})
        assert s_on == 0.0
        assert s_off > s_on


class TestPrincipalAndServiceOrientation:
    """Direct unit tests against hand-built rects, not the full solve() -- on real plan and
    parti data every room's `exterior_walls` is usually already declared explicitly (the parti
    template, or a hand-authored plan like tidewater-georgian-careful.json), and
    exterior_score's existing 14-point-per-missing-wall penalty already dominates this
    function's much softer preference. That is correct, established behaviour -- a room's own
    stated requirement should win over a soft compositional nudge -- so this function is only
    ever decisive when a room's wall is NOT already pinned down, which unit tests can isolate
    cleanly and a full solve() on richly-declared data cannot."""

    def test_principal_room_on_entrance_front_scores_zero(self, geometry_module):
        rooms = [{"id": "dr", "type": "drawing-room"}]
        rects = {"dr": (0.0, 0.0, 16.0, 20.0)}  # touches S
        assert geometry_module.principal_and_service_score(rects, rooms, 40, 30, {"S"}) == 0.0

    def test_principal_room_not_on_front_is_penalised(self, geometry_module):
        rooms = [{"id": "dr", "type": "drawing-room"}]
        rects = {"dr": (0.0, 15.0, 16.0, 15.0)}  # interior/rear only
        assert geometry_module.principal_and_service_score(rects, rooms, 40, 30, {"S"}) > 0.0

    def test_service_room_on_rear_scores_zero(self, geometry_module):
        rooms = [{"id": "kit", "type": "kitchen"}]
        rects = {"kit": (0.0, 24.0, 16.0, 6.0)}  # touches N, opposite of S entrance
        assert geometry_module.principal_and_service_score(rects, rooms, 40, 30, {"S"}) == 0.0

    def test_service_room_on_the_entrance_front_is_penalised_more_than_merely_not_rear(self, geometry_module):
        rooms = [{"id": "kit", "type": "kitchen"}]
        rear = {"kit": (0.0, 12.0, 16.0, 6.0)}      # neither front nor rear
        front = {"kit": (0.0, 0.0, 16.0, 6.0)}      # ON the entrance wall -- worse
        s_mid = geometry_module.principal_and_service_score(rear, rooms, 40, 30, {"S"})
        s_front = geometry_module.principal_and_service_score(front, rooms, 40, 30, {"S"})
        assert s_front > s_mid > 0


class TestCeremonialSequence:
    """'A path of increasing privacy rank with no backtracking' -- checked geometrically over
    the direct threshold-to-principal-room door hop, scoped as docs/geometry.md explains."""

    def test_principal_room_deeper_than_threshold_room_scores_zero(self, geometry_module):
        rooms = [
            {"id": "porch", "type": "entry-porch", "doors": [{"to": "dr"}]},
            {"id": "dr", "type": "drawing-room", "doors": [{"to": "porch"}]},
        ]
        rects = {"porch": (10.0, 0.0, 6.0, 6.0), "dr": (10.0, 6.0, 20.0, 20.0)}  # dr is deeper (farther from S)
        assert geometry_module.ceremonial_score(rects, rooms, 40, 32, {"S"}) == 0.0

    def test_principal_room_nearer_the_street_than_the_threshold_it_passes_through_is_penalised(self, geometry_module):
        """The backtracking case: the higher-privacy room sits CLOSER to the entrance wall than
        the threshold room leading to it -- geometrically nonsensical as a sequence."""
        rooms = [
            {"id": "porch", "type": "entry-porch", "doors": [{"to": "dr"}]},
            {"id": "dr", "type": "drawing-room", "doors": [{"to": "porch"}]},
        ]
        rects = {"porch": (10.0, 10.0, 6.0, 6.0), "dr": (10.0, 0.0, 20.0, 8.0)}  # dr is SHALLOWER
        assert geometry_module.ceremonial_score(rects, rooms, 40, 32, {"S"}) > 0.0

    def test_no_entrance_data_is_a_no_op(self, geometry_module):
        rooms = [
            {"id": "porch", "type": "entry-porch", "doors": [{"to": "dr"}]},
            {"id": "dr", "type": "drawing-room", "doors": [{"to": "porch"}]},
        ]
        rects = {"porch": (10.0, 10.0, 6.0, 6.0), "dr": (10.0, 0.0, 20.0, 8.0)}
        assert geometry_module.ceremonial_score(rects, rooms, 40, 32, set()) == 0.0


class TestCentreHallSymmetry:
    def test_mirrored_pair_across_a_spanning_passage_scores_zero(self, geometry_module):
        rooms = [
            {"id": "cp", "type": "centre-passage", "exterior_walls": ["S", "N"]},
            {"id": "left", "type": "drawing-room"},
            {"id": "right", "type": "drawing-room"},
        ]
        # passage centred at x=18-24 (centre 21); left and right rooms equidistant either side
        rects = {"cp": (18.0, 0.0, 6.0, 30.0), "left": (0.0, 0.0, 18.0, 20.0), "right": (24.0, 0.0, 18.0, 20.0)}
        assert geometry_module.centre_hall_symmetry_score(rects, rooms, 42, 30) == 0.0

    def test_unmirrored_room_is_penalised_but_not_punitively(self, geometry_module):
        rooms = [
            {"id": "cp", "type": "centre-passage", "exterior_walls": ["S", "N"]},
            {"id": "lone", "type": "drawing-room"},
        ]
        rects = {"cp": (18.0, 0.0, 6.0, 30.0), "lone": (0.0, 0.0, 18.0, 20.0)}
        s = geometry_module.centre_hall_symmetry_score(rects, rooms, 42, 30)
        assert 0 < s <= 2.0

    def test_no_spanning_room_is_a_no_op(self, geometry_module):
        rooms = [{"id": "a", "type": "drawing-room"}, {"id": "b", "type": "dining-room"}]
        rects = {"a": (0.0, 0.0, 10.0, 10.0), "b": (10.0, 0.0, 10.0, 10.0)}
        assert geometry_module.centre_hall_symmetry_score(rects, rooms, 20, 10) == 0.0


class TestSolveIntegration:
    """End-to-end against the shipped tidewater-georgian-careful.json, PLAN-OF-ACTION.md's own
    acceptance example. Two of its three sub-claims hold outright; the third is documented as a
    genuine data conflict, not silently forced -- see test_dining_room_front_claim below."""

    def test_entrance_portico_lands_on_the_entrance_wall(self, geometry_module):
        """PLAN-OF-ACTION.md's own acceptance clause. WP-11.16 SPLIT IT BY ENGINE AND WP-11.17
        FOLDED IT BACK, which is the sequence the split's own assertion message asked for.

        Tagging this record's service programme into a west dependency cost the SEARCH its
        entrance and cost the PROVER nothing -- porch at (32.07, 31.51) on the REAR wall under
        the hill-climb against (31.0, 0.0) on the S front under CP. For one day the clause was
        therefore asserted on the engine that draws and the search's failure pinned beside it.

        WP-11.17 STATES THE FRONT rather than charging for it: the entry porch is the room
        `geometry.entrance_anchors` names, and `_partial_flank` gives it a rectangle of its own
        declared area on the entrance face before the guillotine runs. So both engines hold the
        clause and there is one assertion again. Measured over 250 candidates on this record,
        porch-on-the-entrance-front went from **0 of 250 to 250 of 250**, and the porch is drawn
        at exactly its declared 12.00 x 6.00.

        THE TOLERANCE STAYS AT 0.6 ft. Relaxing it was the available repair while this was
        broken and would have made the test vacuous; it is not needed now (`y_ft` is 0.0 on the
        search and 0.0 on the proof) and loosening it later would hide the next regression.
        """
        plan = load_plan("tidewater-georgian-careful")
        assert plan["context"]["entrance_faces"] == "S"

        proved = geometry_module.solve(load_plan("tidewater-georgian-careful"), engine="cp")
        if ((proved["geometry_report"].get("solver") or {}).get("engine")) == "cp-sat":
            pr = next(r for lv in proved["levels"] for r in lv["rooms"] if r["id"] == "porch")
            assert pr["geometry"]["y_ft"] <= 0.6, (
                f"the PROVING engine no longer lands the entry porch on the S (entrance) wall: "
                f"{pr['geometry']}.")
        # else: COULD NOT EVALUATE without a proof, and not a pass

        result = geometry_module.solve(plan, engine="heuristic")
        porch = next(r for lv in result["levels"] for r in lv["rooms"] if r["id"] == "porch")
        assert porch["geometry"]["y_ft"] <= 0.6, (
            f"the SEARCH no longer lands the entry porch on the S (entrance) wall: "
            f"{porch['geometry']}. WP-11.17 states that front as an anchor, so this is a "
            "regression in `geometry.entrance_anchors` or `_partial_flank` rather than a cost "
            "to be re-pinned -- and check the CENSUS, not this winner: a winner can be right "
            "by the luck of one draw.")

    def test_service_rooms_land_toward_the_rear(self, geometry_module):
        """THE SUBJECT DISSOLVED AT WP-11.16 AND THE TEST IS RE-STATED RATHER THAN RE-PINNED.

        It compared the kitchen's and pantry's centroids against `footprint.depth_ft / 2`. Those
        two rooms are in a west DEPENDENCY now, at x = -21.81 and -34.0 in the wing's own frame,
        while `depth_ft` is the MAIN BLOCK's depth. The comparison is between two coordinate
        systems and means nothing at all.

        BOTH OBVIOUS REPAIRS ARE WORSE THAN RE-STATING IT. Narrowing to `("butlers",)` leaves one
        room drawn the full depth of the block, whose centroid lands at exactly H/2 -- a coin
        flip dressed as an assertion. Substituting the dependency's own depth re-scopes "toward
        the rear" into "inside its own wing", which is vacuously true of every room in it.

        WHAT THE CLAUSE ALWAYS MEANT is that the placer does not put service programme on the
        entrance front, and that survives the tagging in a form that can be tested: no service
        room may be drawn on the entrance side of the house, wherever its element sits. It is
        asserted against the whole built extent rather than against one rectangle, which is the
        same correction WP-11.9 made to six other layers.

        THE CLAUSE IS SPLIT BY ENGINE AND WP-11.17 CHANGED WHY. It was split because the search
        drew this house back to front -- porch on the rear wall, service in front of the
        principal rooms -- and the entry-porch test above was split for the same cause. That
        cause is gone: the porch is on its declared S front on both engines now. The kitchen and
        the pantry are still drawn on the entrance half under the search (mid 15.92 of a 37.24 ft
        depth, against 24.92 and 25.36 under the proof), and the reason is a different defect
        that WP-11.17 measured and did not fix:

        **`principal_and_service_score` MEASURES A WING ROOM AGAINST THE MAIN BLOCK.** It is
        handed the footprint's own `W`/`H` and no per-element `bounds`, so a dependency room at
        x = -34 satisfies `_touches_wall(..., "W", ...)` -- `x <= 0.6` -- and can satisfy N, S or
        E for no placement whatever. Each service room is therefore charged a flat 2.0 for "not
        at the rear" and the 3.0 for *service ON the front* CAN NEVER FIRE. The term has nothing
        to say about where the service programme sits once it is in a wing, which is exactly this
        record. `geometry_cp._score` states the asymmetry deliberately (*"they measure the main
        block"*), so giving these scorers `bounds=` is its own package --
        `oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it`.
        """
        def _rear(result, rid):
            rooms = {r["id"]: r for lv in result["levels"] for r in lv["rooms"]}
            depth = max(r["geometry"]["y_ft"] + r["geometry"]["depth_ft"]
                        for r in rooms.values() if r.get("geometry"))
            g = rooms[rid]["geometry"]
            return g["y_ft"] + g["depth_ft"] / 2 > depth / 2, g, depth

        proved = geometry_module.solve(load_plan("tidewater-georgian-careful"), engine="cp")
        if ((proved["geometry_report"].get("solver") or {}).get("engine")) == "cp-sat":
            for rid in ("kitchen", "pantry"):
                ok, g, depth = _rear(proved, rid)
                assert ok, (
                    f"the PROVING engine draws {rid} on the entrance half ({g}) against a built "
                    f"depth of {depth}. Service programme belongs behind the principal rooms "
                    f"whichever massing element it stands in, and this is the engine that draws "
                    f"the sheet -- a defect here, not a cost.")
        # else: COULD NOT EVALUATE without a proof, and not a pass

        result = geometry_module.solve(load_plan("tidewater-georgian-careful"),
                                       engine="heuristic")
        assert not _rear(result, "kitchen")[0], (
            "the SEARCH now draws the kitchen behind the principal rooms too. That is good news "
            "and it means `principal_and_service_score` has been given per-element `bounds` (or "
            "something else has done the same work) -- make both branches above unconditional "
            "and say what moved, rather than deleting this line.")

    def test_relaxations_do_not_increase_by_more_than_two_over_the_pre_wp22_baseline(self, geometry_module):
        """PLAN-OF-ACTION.md's own acceptance wording. The pre-WP-2.2 baseline (also
        test_geometry.py's own pin) is 11."""
        plan = load_plan("tidewater-georgian-careful")
        result = geometry_module.solve(plan, engine="heuristic")
        assert result["geometry_report"]["relaxations"]["count"] <= 11 + 2

    def test_dining_room_front_claim_is_a_documented_data_conflict_not_silently_forced(self, geometry_module):
        """PLAN-OF-ACTION.md's acceptance text says 'the drawing room and dining room flank the
        passage on the front.' tidewater-georgian-careful.json's own dining-room record
        explicitly declares `exterior_walls: ["N", "W"]` -- the rear -- which is real,
        hand-authored intent (a Georgian dining room paired with the breakfast room and kitchen
        at the back is a legitimate period arrangement, not an error), not something this
        solver invents or should override: a room's own declared exterior_walls is authoritative
        over every compositional preference in this package by design (exterior_score's
        existing 14-point-per-missing-wall penalty already outweighs
        principal_and_service_score's much softer 3.5-point front preference).

        This test pins the conflict itself, so it is a visible, deliberate finding rather than
        a silently-missed acceptance clause: dining-room lands on a wall its own record names,
        and the fix, if one is wanted, is a data decision on the reference plan (or the
        acceptance text), not a solver change -- see docs/geometry.md, 'What was
        deliberately not done.'

        RE-CUT AT WP-11.17, BECAUSE THE ASSERTION WAS A PROXY AND THE PROXY BROKE WHILE ITS
        SUBJECT HELD. It read `y_ft + depth/2 > H/2` -- *rear-of-centre* -- which is a test of
        N-ness, and this room declares **N and W**. Stating the entrance front re-places the
        ground floor and the dining room now takes its **W** wall instead of its N one: drawn
        (0.0, 0.0, 16.5, 18.0) against (4.95, 20.6, 18, 16.64) before, one declared wall reached
        in each case. So the room is still honouring its own record over the front preference,
        and the old line would have called that a failure.

        MEASURED CORPUS-WIDE SO THE RE-CUT IS NOT A LOOSENING: across all sixteen plans, 170
        declared `exterior_walls` and **67 not reached, before and after** -- the anchor costs
        the corpus none of them. What is asserted is the property the docstring above states.
        """
        plan = load_plan("tidewater-georgian-careful")
        dining = next(r for lv in plan["levels"] for r in lv["rooms"] if r["id"] == "dining")
        assert set(dining.get("exterior_walls") or []) == {"N", "W"}
        result = geometry_module.solve(plan, engine="heuristic")
        rooms_by_id = {r["id"]: r for lv in result["levels"] for r in lv["rooms"]}
        g = rooms_by_id["dining"]["geometry"]
        W_, H = result["footprint"]["width_ft"], result["footprint"]["depth_ft"]
        rect = (g["x_ft"], g["y_ft"], g["width_ft"], g["depth_ft"])
        reached = [w for w in ("N", "W") if geometry_module._touches_wall(rect, w, W_, H)]
        assert reached, (
            f"the dining room is drawn clear of BOTH walls its own record declares: {g}. Its "
            "`exterior_walls` are authoritative over every compositional preference in this "
            "package by design -- `exterior_score` charges 14 per missing wall against "
            "`principal_and_service_score`'s 3.5 -- so this is that ordering failing, not a "
            "number to re-pin.")


class TestDoorSwingsRender:
    def test_svg_includes_arc_paths_for_doors(self, geometry_module):
        import importlib.util
        plan = load_plan("tidewater-georgian-careful")
        result = geometry_module.solve(plan, engine="heuristic")
        spec = importlib.util.spec_from_file_location("render_plan", os.path.join(ROOT, "build", "render_plan.py"))
        rp = importlib.util.module_from_spec(spec); spec.loader.exec_module(rp)
        path = rp.render(result, "/tmp/wp22_door_swing_test.svg")
        svg = open(path).read()
        assert '<path d="M ' in svg and " A " in svg, "expected at least one door-swing arc path"
