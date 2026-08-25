"""Behaviour tests for the constraint solver (WP-2.3, build/solver.py).

Each test protects one finding from `docs/reports/wp-2.3-real-solver.md` or one clause of the
package's own acceptance text in PLAN-OF-ACTION.md, and is named for it. The costly ones —
those that actually run CP-SAT — carry a time budget chosen so the suite stays inside its
five-minute bar; the budgets are the reason a couple of the assertions are stated as
inequalities against the heuristic rather than as pinned numbers.
"""
import copy
import os
import sys

import pytest

from conftest import ROOT, load_plan, minimal_plan

# Long enough for CP-SAT to beat the heuristic on the shipped plans; measured, not guessed.
# Below about 15 s the spec Colonial falls back to the heuristic (correctly, and reported).
TEST_BUDGET_S = 18.0


def _layout(plan_out):
    ground, upper = {}, {}
    for i, lv in enumerate(plan_out["levels"]):
        idx = lv.get("index", i)
        for r in lv["rooms"]:
            g = r.get("geometry")
            if g:
                (ground if idx == 0 else upper)[r["id"]] = (
                    g["x_ft"], g["y_ft"], g["width_ft"], g["depth_ft"])
    return ground, upper


# A CP solve is the expensive thing in this file, so the ones that can be shared are solved
# once for the whole session. Tests that need their own (determinism, the second shipped plan)
# say so by not using these.
@pytest.fixture(scope="session")
def cp_tidewater(solver_module):
    pytest.importorskip("ortools")
    return solver_module.solve(load_plan("tidewater-georgian-careful"), None,
                               time_budget_s=TEST_BUDGET_S)


@pytest.fixture(scope="session")
def overstuffed_plan():
    plan = minimal_plan(
        [
            {"id": "drawing", "type": "drawing-room", "width_ft": 18, "length_ft": 22,
             "exterior_walls": ["S"], "doors": [{"to": "passage"}]},
            {"id": "library", "type": "library", "width_ft": 16, "length_ft": 18,
             "exterior_walls": ["E"], "doors": [{"to": "passage"}]},
            {"id": "dining", "type": "dining-room", "width_ft": 16, "length_ft": 20,
             "exterior_walls": ["N"], "doors": [{"to": "passage"}]},
            {"id": "kitchen", "type": "kitchen", "width_ft": 14, "length_ft": 18,
             "exterior_walls": ["N"], "doors": [{"to": "dining"}]},
            {"id": "passage", "type": "centre-passage", "width_ft": 8, "length_ft": 30,
             "exterior_walls": ["S", "N"], "doors": []},
        ],
        style="tidewater-georgian", massing="center-passage-single-pile")
    plan["context"] = {"entrance_faces": "S"}
    plan["site"] = {"lot_width_ft": 34, "setback_side_ft": 5}
    return plan


@pytest.fixture(scope="session")
def cp_conflict(solver_module, overstuffed_plan):
    pytest.importorskip("ortools")
    plan = copy.deepcopy(overstuffed_plan)
    return solver_module.solve(plan, None, time_budget_s=TEST_BUDGET_S), plan


class TestFallbackIsReportedNeverSilent:
    """The rule the module was built around: a plan placed by a different engine than the
    caller thinks is a lie about the drawing. This test needs no OR-Tools — it is the one
    that must run everywhere."""

    def test_missing_ortools_falls_back_to_the_heuristic_and_says_so(self, solver_module,
                                                                    monkeypatch):
        import builtins
        real_import = builtins.__import__

        def no_ortools(name, *args, **kwargs):
            if name.startswith("ortools"):
                raise ImportError("simulated: ortools not installed")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", no_ortools)
        out = solver_module.solve(load_plan("tidewater-georgian-careful"), None,
                                  time_budget_s=TEST_BUDGET_S)
        sv = out["geometry_report"]["solver"]
        assert sv["engine"] == "heuristic-fallback"
        assert sv["status"] == "ortools-missing"
        assert sv["fallback_reason"], "a fallback with no stated reason is a silent fallback"
        assert "requirements" in sv["fallback_reason"]
        # and it is still a usable plan, not an error
        assert out["footprint"]["width_ft"] > 0
        assert any(r.get("geometry") for lv in out["levels"] for r in lv["rooms"])


class TestRecordContract:
    """The solver emits the same record shape as geometry.py, because everything downstream —
    render_plan, structure, roof, elevation — reads that record and not the engine."""

    def test_footprint_and_report_carry_the_same_fields_the_heuristic_writes(self, cp_tidewater):
        fp = cp_tidewater["footprint"]
        for k in ("width_ft", "depth_ft", "bays", "bay_module_ft", "area_sf", "slack_sf"):
            assert k in fp
        gr = cp_tidewater["geometry_report"]
        for k in ("score", "ground_score", "upper_score", "vertical_score", "bays_grown",
                  "lot_capped", "relaxations", "vertical", "reading"):
            assert k in gr
        assert set(gr["relaxations"]) >= {"count", "max_off_grid_ft", "note"}

    def test_every_indoor_room_is_placed(self, cp_tidewater):
        for lv in cp_tidewater["levels"]:
            for r in lv["rooms"]:
                assert "geometry" not in r or set(r["geometry"]) >= {
                    "x_ft", "y_ft", "width_ft", "depth_ft", "area_sf"}
        assert sum(1 for lv in cp_tidewater["levels"] for r in lv["rooms"] if r.get("geometry")) > 10

    def test_rooms_tile_the_footprint_with_no_overlap_and_no_void(self, cp_tidewater):
        """The property the free-packing model had to state as an equation and could not solve.
        Reading the slicing structure instead makes it true by construction — so if it is ever
        false, the tree walk is broken, not the solver."""
        W = cp_tidewater["footprint"]["width_ft"]
        H = cp_tidewater["footprint"]["depth_ft"]
        for i, lv in enumerate(cp_tidewater["levels"]):
            rects = [(r["geometry"]["x_ft"], r["geometry"]["y_ft"],
                      r["geometry"]["width_ft"], r["geometry"]["depth_ft"])
                     for r in lv["rooms"] if r.get("geometry")]
            if not rects:
                continue
            assert sum(w * h for _, _, w, h in rects) == pytest.approx(W * H, abs=1.0)
            for a in range(len(rects)):
                ax, ay, aw, ah = rects[a]
                assert ax >= -0.01 and ay >= -0.01
                assert ax + aw <= W + 0.01 and ay + ah <= H + 0.01
                for b in range(a + 1, len(rects)):
                    bx, by, bw, bh = rects[b]
                    ox = min(ax + aw, bx + bw) - max(ax, bx)
                    oy = min(ay + ah, by + bh) - max(ay, by)
                    assert not (ox > 0.01 and oy > 0.01), "two rooms occupy the same floor"

    def test_the_svg_renders_from_the_record(self, cp_tidewater, tmp_path):
        sys.path.insert(0, os.path.join(ROOT, "build"))
        import render_plan
        out = tmp_path / "cp.svg"
        render_plan.render(cp_tidewater, str(out))
        svg = out.read_text()
        assert svg.startswith("<?xml") or svg.lstrip().startswith("<svg")
        assert len(svg) > 2000


class TestBeatsTheHeuristicOnItsOwnScoring:
    """PLAN-OF-ACTION.md's acceptance: 'on the two briefs the CP solution scores at least as
    well as the best of 800 heuristic candidates'. Both layouts are scored by geometry.py's own
    functions, so this is one metric and not two engines grading themselves."""

    @pytest.mark.parametrize("plan_name", ["tidewater-georgian-careful", "spec-builder-colonial"])
    def test_cp_scores_at_least_as_well_as_best_of_800(self, solver_module, geometry_module,
                                                       cp_tidewater, plan_name):
        pytest.importorskip("ortools")
        plan = load_plan(plan_name)
        prep, levels = geometry_module.prepare_rooms(copy.deepcopy(plan))
        h = geometry_module.solve(copy.deepcopy(plan), None, 800, 7)
        hg, hu = _layout(h)
        h_score = solver_module.score_layout(
            hg, hu, prep, levels, plan, h["footprint"]["width_ft"],
            h["footprint"]["depth_ft"], h["footprint"]["bay_module_ft"])
        out = (cp_tidewater if plan_name == "tidewater-georgian-careful"
               else solver_module.solve(copy.deepcopy(plan), None, time_budget_s=TEST_BUDGET_S))
        assert out["geometry_report"]["score"] <= h_score["score"]

    def test_the_cross_check_is_actually_performed_not_merely_asserted(self, cp_tidewater):
        cc = cp_tidewater["geometry_report"]["solver"]["cross_check"]
        assert cc is not None
        assert cc["heuristic_candidates"] == 800
        assert isinstance(cc["cp_score"], (int, float))
        assert isinstance(cc["heuristic_score"], (int, float))


class TestInfeasibleBriefIsNamedNotDrawn:
    """The package's headline: 'an infeasible brief returns a named conflict set rather than a
    bad plan'. The rooms below overflow a lot too narrow to grow into."""

    def test_it_returns_an_error_and_a_conflict_rather_than_a_plan(self, cp_conflict):
        out, _ = cp_conflict
        assert "error" in out
        assert "conflict" in out

    def test_the_conflict_names_the_rooms_that_cannot_hold_their_minimum(self, cp_conflict):
        out, _ = cp_conflict
        reqs = out["conflict"]["requirements"]
        assert reqs, "a conflict with no named requirement is not a conflict set"
        assert all(r.startswith("room-minimum:") for r in reqs)
        ids = {r.split(":", 1)[1] for r in reqs}
        assert ids <= {"drawing", "library", "dining", "kitchen", "passage"}

    def test_the_prose_names_a_room_and_says_why_the_house_cannot_grow(self, cp_conflict):
        out, _ = cp_conflict
        prose = out["conflict"]["prose"]
        assert any(word in prose for word in ("drawing-room", "library", "dining-room",
                                              "kitchen", "centre-passage"))
        assert "lot" in prose or "parti" in prose
        assert prose == out["error"]

    def test_no_geometry_is_written_for_a_plan_that_cannot_be_built(self, cp_conflict):
        _, plan = cp_conflict
        assert not any(r.get("geometry") for lv in plan["levels"] for r in lv["rooms"])

    def test_minimality_is_claimed_only_when_it_was_proved(self, cp_conflict):
        """Unjudged is not passed, applied to the conflict set itself."""
        out, _ = cp_conflict
        assert isinstance(out["conflict"]["minimal"], bool)
        if not out["conflict"]["minimal"]:
            assert "time budget" in out["conflict"]["note"]


class TestWhatTheDrawingActuallyMeets:
    """`unmet_requirements` is measured from the finished rectangles, not from what the solver
    stopped insisting on — the difference between evaluated-and-failed and could-not-evaluate."""

    def test_unmet_is_reported_and_every_entry_is_a_named_requirement(self, cp_tidewater):
        sv = cp_tidewater["geometry_report"]["solver"]
        assert "unmet_requirements" in sv
        kinds = {u.split(":", 1)[0] for u in sv["unmet_requirements"]}
        assert kinds <= {"room-minimum", "exterior-wall", "adjacency", "entrance-front",
                         "entrance-hall", "spanning", "wet-stack"}

    def test_a_hard_requirement_never_appears_unmet_in_a_solved_plan(self, cp_tidewater):
        """Room minimums are the one requirement the solver will not trade away, so a solved
        plan that reports one unmet would mean the constraint is not doing its job."""
        sv = cp_tidewater["geometry_report"]["solver"]
        if sv["engine"].startswith("cp"):
            assert not [u for u in sv["unmet_requirements"] if u.startswith("room-minimum:")]

    def test_rooms_fit_is_reported_as_proved_or_unsettled_never_assumed(self, cp_tidewater):
        sv = cp_tidewater["geometry_report"]["solver"]
        assert isinstance(sv["rooms_fit_proved"], bool)
        if not sv["rooms_fit_proved"]:
            assert "not settled" in sv["rooms_fit_note"].lower() or \
                   "NOT settled" in sv["rooms_fit_note"]


class TestDeterminism:
    def test_the_same_seed_places_the_same_rooms(self, solver_module):
        """One worker and a fixed seed, because a suite that cannot reproduce a layout cannot
        pin one either."""
        pytest.importorskip("ortools")
        # A short budget on purpose: determinism is about reproducing a layout, not about
        # producing a good one, and two full-budget solves would cost the suite half a minute
        # to prove something a short one proves just as well.
        #
        # `deterministic=True` added 24 Aug 2026, after this test failed intermittently. It was
        # right and the solver was wrong: the topology loop stopped starting new topologies by
        # reading the WALL CLOCK, so a loaded machine tried fewer than an idle one and a
        # different layout won -- the same seed, the same plan, a different house. It passed
        # whenever anyone checked, because checking one test is exactly when the machine is
        # quiet. See TestWallClockModeSaysSoAboutItself below for the other half.
        a = solver_module.solve(load_plan("tidewater-georgian-careful"), None,
                                seed=7, time_budget_s=8.0, workers=1, deterministic=True)
        b = solver_module.solve(load_plan("tidewater-georgian-careful"), None,
                                seed=7, time_budget_s=8.0, workers=1, deterministic=True)
        assert _layout(a) == _layout(b)
        assert a["geometry_report"]["solver"]["deterministic"] is True


class TestWallClockModeSaysSoAboutItself:
    """The default is still wall-clock bounded, because a person waiting for a plan wants the
    promise about time kept. What changed is that the record now says which trade was taken,
    instead of letting a reader assume the seed was enough."""

    def test_the_default_declares_that_its_layout_is_machine_dependent(self, solver_module):
        pytest.importorskip("ortools")
        out = solver_module.solve(load_plan("tidewater-georgian-careful"), None,
                                  seed=7, time_budget_s=8.0, workers=1)
        sv = out["geometry_report"]["solver"]
        assert sv["deterministic"] is False
        assert "depends on how fast this machine was" in sv["deterministic_note"]
        assert "deterministic=True" in sv["deterministic_note"]


class TestRelaxationRecount:
    """geometry.py counts a relaxation per cut as it takes one; a finished layout has no memory
    of that, so the solver recounts distinct off-grid wall lines. The two are close, not equal,
    and docs/geometry.md says so."""

    def test_an_on_grid_layout_counts_no_relaxations(self, solver_module):
        rects = {"a": (0.0, 0.0, 10.0, 20.0), "b": (10.0, 0.0, 10.0, 20.0)}
        count, offs = solver_module.relaxations_from_rects([rects], 20.0, 20.0, 10.0)
        assert count == 0 and offs == []

    def test_one_off_grid_line_is_counted_once_with_its_distance(self, solver_module):
        rects = {"a": (0.0, 0.0, 7.5, 20.0), "b": (7.5, 0.0, 12.5, 20.0)}
        count, offs = solver_module.relaxations_from_rects([rects], 20.0, 20.0, 10.0)
        assert count == 1
        assert offs == [pytest.approx(2.5)]

    def test_the_footprints_own_edges_are_never_relaxations(self, solver_module):
        rects = {"a": (0.0, 0.0, 25.0, 25.0)}
        count, _ = solver_module.relaxations_from_rects([rects], 25.0, 25.0, 10.0)
        assert count == 0


class TestSlicingStructure:
    """The move that made the package work: read the slicing tree off the layout instead of
    asking CP-SAT to satisfy `sum(w*h) == W*H` over a dozen nonlinear products."""

    def test_a_two_room_slice_is_recovered(self, solver_module):
        items = [("a", (0.0, 0.0, 10.0, 20.0)), ("b", (10.0, 0.0, 10.0, 20.0))]
        tree = solver_module.guillotine_tree(items, 0.0, 0.0, 20.0, 20.0)
        assert tree["axis"] == "x"
        assert tree["cut"] == pytest.approx(10.0)
        assert tree["lo"] == {"leaf": "a"} and tree["hi"] == {"leaf": "b"}

    def test_a_nested_slice_is_recovered(self, solver_module):
        items = [("a", (0.0, 0.0, 10.0, 20.0)),
                 ("b", (10.0, 0.0, 10.0, 10.0)),
                 ("c", (10.0, 10.0, 10.0, 10.0))]
        tree = solver_module.guillotine_tree(items, 0.0, 0.0, 20.0, 20.0)
        assert tree["axis"] == "x"
        assert tree["hi"]["axis"] == "y"

    def test_a_layout_that_is_not_guillotine_is_reported_as_such(self, solver_module):
        """A pinwheel tiles its rectangle and no straight cut crosses it. Nothing in this
        codebase produces one, and the caller checks rather than assuming."""
        items = [("a", (0.0, 0.0, 20.0, 10.0)),
                 ("b", (20.0, 0.0, 10.0, 20.0)),
                 ("c", (10.0, 20.0, 20.0, 10.0)),
                 ("d", (0.0, 10.0, 10.0, 20.0)),
                 ("e", (10.0, 10.0, 10.0, 10.0))]
        assert solver_module.guillotine_tree(items, 0.0, 0.0, 30.0, 30.0) is None


class TestTheHeuristicIsUnchanged:
    """WP-2.3 refactored geometry.py to share derive_footprint/write_record. The pinned
    relaxation count in tests/test_geometry.py is the real guard; this states the contract the
    solver depends on, so a change to it fails here with a name rather than there with a
    number."""

    def test_derive_footprint_and_write_record_are_exported(self, geometry_module):
        assert callable(geometry_module.derive_footprint)
        assert callable(geometry_module.write_record)
        assert callable(geometry_module.prepare_rooms)

    def test_derive_footprint_returns_the_facts_the_solver_reads(self, geometry_module):
        plan = load_plan("tidewater-georgian-careful")
        prep, _levels = geometry_module.prepare_rooms(plan)
        fp = geometry_module.derive_footprint(plan, None, prep)
        for k in ("bay", "bays", "W", "H", "slack", "grown", "lot_maxbay", "catalog_maxbay",
                  "growth_ceiling", "target_depth", "need"):
            assert k in fp

    def test_a_lot_too_narrow_for_two_bays_is_still_refused_by_footprint_derivation(
            self, geometry_module):
        plan = minimal_plan([{"id": "hall", "type": "centre-passage", "width_ft": 8,
                              "length_ft": 20, "doors": []}])
        plan["site"] = {"lot_width_ft": 14, "setback_side_ft": 5}
        prep, _levels = geometry_module.prepare_rooms(plan)
        fp = geometry_module.derive_footprint(plan, None, prep)
        assert "error" in fp and "lot too narrow" in fp["error"]
