"""Pins WP-3.1, walls/structure/storeys -- see docs/structure.md and PLAN-OF-ACTION.md's own
WP-3.1 acceptance text ('the Tidewater plan emits an outside-to-outside footprint, wall lines, a
bearing-line diagram, and a section with eave and ridge heights consistent with the style's
pitch constraint; no 2x10 spanning 18 ft passes silently').

Three real bugs were found by actually running build/structure.py for the first time against
the reference corpus rather than by inspection alone, and each has a dedicated regression test
below rather than just being fixed silently:

  1. wall_lines() had the S/N and W/E exterior walls' axis/position swapped, which planted a
     wall's own position value into the WRONG axis's break-point list in span_check() -- see
     TestWallLinesExteriorOrientation.
  2. span_check()'s hand-timber-vs-light-frame decision checked construction_type against
     timber-bay.json's applies_to list, which holds STYLE ids and can never match a
     construction_type value -- silently routing every plan through the light-frame joist
     table regardless of style. See TestSpanCheckFramingBasis.
  3. graduation_check() had the third/second storey band hand-transcribed as (0.60, 0.85),
     which is actually storey-graduation.json's GROUND-UNDER-PIANO-NOBILE band, not its
     third/second one (0.70, 0.88). See TestGraduationCheck.
"""
import json
import math
import os

from conftest import ROOT, load_plan


def _bay_walls(*positions_and_axes):
    """Shorthand for a bearing_walls list span_check() can consume directly."""
    return [{"axis": axis, "position_ft": pos, "bearing": True} for axis, pos in positions_and_axes]


class TestWallThickness:
    def test_declared_construction_type_is_used(self, structure_module):
        plan = {"declared": {"construction_type": "braced-timber-frame"}}
        w = structure_module.wall_thickness(plan)
        assert w["construction_type"] == "braced-timber-frame"
        assert w["bearing"] == "load-bearing-frame"
        assert w["note"] is None

    def test_undeclared_falls_back_with_an_explicit_note(self, structure_module):
        """'Unjudged is not passed' applied to structure: a missing construction_type produces
        a fallback value AND a note saying so, not a silent default indistinguishable from a
        real declaration."""
        w = structure_module.wall_thickness({"declared": {}})
        assert w["construction_type"] == structure_module.DEFAULT_CONSTRUCTION_TYPE
        assert w["note"] is not None and "No construction_type declared" in w["note"]

    def test_unknown_construction_type_falls_back_with_a_different_note(self, structure_module):
        w = structure_module.wall_thickness({"declared": {"construction_type": "geodesic-dome"}})
        assert w["construction_type"] == structure_module.DEFAULT_CONSTRUCTION_TYPE
        assert "not in construction/wall-assemblies.json" in w["note"]

    def test_masonry_thickness_matches_the_slot_note_range(self, structure_module):
        """elements/slots.json's wall_thickness_masonry slot documents 13-18 in for solid
        masonry two-wythe -- the catalog record was cross-checked against it directly."""
        w = structure_module.wall_thickness({"declared": {"construction_type": "solid-masonry-two-wythe"}})
        assert 13 <= w["exterior_in"] <= 18


class TestWallLinesExteriorOrientation:
    """Regression for bug #1: the four exterior walls must carry the axis a HORIZONTAL wall
    (S/N, running along x) vs a VERTICAL wall (W/E, running along y) actually needs, using the
    same convention _shared_segment() establishes for interior walls -- axis 'x' is a vertical
    line at a given x, axis 'y' is a horizontal line at a given y."""

    def test_south_and_north_are_horizontal_axis_y(self, structure_module):
        walls = structure_module.wall_lines([], 60.0, 40.0)
        by_wall = {w["wall"]: w for w in walls if w["role"] == "exterior"}
        assert by_wall["S"]["axis"] == "y" and by_wall["S"]["position_ft"] == 0.0
        assert by_wall["S"]["lo_ft"] == 0.0 and by_wall["S"]["hi_ft"] == 60.0  # spans the WIDTH
        assert by_wall["N"]["axis"] == "y" and by_wall["N"]["position_ft"] == 40.0
        assert by_wall["N"]["lo_ft"] == 0.0 and by_wall["N"]["hi_ft"] == 60.0

    def test_west_and_east_are_vertical_axis_x(self, structure_module):
        walls = structure_module.wall_lines([], 60.0, 40.0)
        by_wall = {w["wall"]: w for w in walls if w["role"] == "exterior"}
        assert by_wall["W"]["axis"] == "x" and by_wall["W"]["position_ft"] == 0.0
        assert by_wall["W"]["lo_ft"] == 0.0 and by_wall["W"]["hi_ft"] == 40.0  # spans the DEPTH
        assert by_wall["E"]["axis"] == "x" and by_wall["E"]["position_ft"] == 60.0
        assert by_wall["E"]["lo_ft"] == 0.0 and by_wall["E"]["hi_ft"] == 40.0

    def test_no_exterior_position_leaks_into_the_wrong_axis_break_points(self, structure_module):
        """The concrete failure mode: before the fix, N's y=H position (40.0) was tagged axis
        'x' and W < 40 < E, so it silently fabricated a bogus interior break point splitting an
        x-axis span that does not exist on the real footprint. Also guards E's x=W position
        (60.0) leaking into the y-axis break points, which produced a completely-out-of-bounds
        span (40.0 to 60.0) on a 40 ft deep footprint."""
        W, H = 60.0, 40.0
        walls = structure_module.wall_lines([], W, H)
        x_positions = {w["position_ft"] for w in walls if w["axis"] == "x"}
        y_positions = {w["position_ft"] for w in walls if w["axis"] == "y"}
        assert H not in x_positions  # N's position must not appear as an x-axis break point
        assert W not in y_positions  # E's position must not appear as a y-axis break point
        assert x_positions == {0.0, W}
        assert y_positions == {0.0, H}


class TestBearingLines:
    def test_exterior_is_always_bearing(self, structure_module):
        walls = structure_module.wall_lines([], 40.0, 30.0)
        bearing = structure_module.bearing_lines(walls, bay_module_ft=10.0)
        assert all(w["bearing"] for w in bearing if w["role"] == "exterior")

    def test_interior_on_the_bay_grid_is_bearing(self, structure_module):
        walls = [{"role": "interior", "axis": "x", "position_ft": 20.0, "lo_ft": 0.0, "hi_ft": 10.0, "rooms": ["a", "b"]}]
        bearing = structure_module.bearing_lines(walls, bay_module_ft=10.0)
        assert bearing[0]["bearing"] is True
        assert "bay grid" in bearing[0]["why"]

    def test_interior_off_the_bay_grid_is_a_partition(self, structure_module):
        walls = [{"role": "interior", "axis": "x", "position_ft": 23.5, "lo_ft": 0.0, "hi_ft": 10.0, "rooms": ["a", "b"]}]
        bearing = structure_module.bearing_lines(walls, bay_module_ft=10.0)
        assert bearing[0]["bearing"] is False
        assert "partition" in bearing[0]["why"]


class TestSpanCheckFramingBasis:
    """Regression for bug #2: timber_framed must be decided from STYLE membership in timber-
    bay.json's applies_to list, not from construction_type -- construction_type values
    ('solid-masonry-two-wythe', 'platform-frame', ...) never appear in that list at all, so the
    old code's `construction_type in _timber_bay_applies_to()` was always False."""

    def test_a_timber_bay_style_is_checked_against_the_bay_module(self, structure_module):
        assert "tidewater-georgian" in structure_module._timber_bay_applies_to()
        construction = structure_module.load_construction()
        walls = _bay_walls(("x", 0.0), ("x", 18.0))
        spans = structure_module.span_check(walls, 18.0, 10.0, "tidewater-georgian", construction["floor"])
        x_span = next(s for s in spans if s["axis"] == "x")
        assert x_span["member"] == "hewn joist on the bay module"
        assert x_span["max_span_ft"] == 20.0
        assert x_span["ok"] is True

    def test_a_timber_bay_style_span_beyond_20_ft_fails(self, structure_module):
        construction = structure_module.load_construction()
        walls = _bay_walls(("x", 0.0), ("x", 24.0))
        spans = structure_module.span_check(walls, 24.0, 10.0, "tidewater-georgian", construction["floor"])
        x_span = next(s for s in spans if s["axis"] == "x")
        assert x_span["ok"] is False
        assert "20 ft" in x_span["note"]

    def test_a_non_timber_bay_style_is_checked_against_the_light_frame_table(self, structure_module):
        assert "some-style-not-in-timber-bay" not in structure_module._timber_bay_applies_to()
        construction = structure_module.load_construction()
        walls = _bay_walls(("x", 0.0), ("x", 12.0))
        spans = structure_module.span_check(walls, 12.0, 10.0, "some-style-not-in-timber-bay", construction["floor"])
        x_span = next(s for s in spans if s["axis"] == "x")
        assert x_span["member"] != "hewn joist on the bay module"

    def test_no_2x10_spanning_18ft_passes_silently(self, structure_module):
        """The acceptance text's own literal case. A 2x10 caps at 16 ft (construction/
        floor-structure.json), so an 18 ft span must never be reported as covered by a 2x10 --
        either a deeper/engineered member is correctly selected, or the span fails outright.
        Never both silently passing AND naming an inadequate member."""
        construction = structure_module.load_construction()
        walls = _bay_walls(("x", 0.0), ("x", 18.0))
        spans = structure_module.span_check(walls, 18.0, 10.0, "some-style-not-in-timber-bay", construction["floor"])
        x_span = next(s for s in spans if s["axis"] == "x")
        assert x_span["ok"] is True  # an 18 ft span IS coverable -- just not by a 2x10
        assert x_span["member"] != "2x10"
        member_catalog = {m["member"]: m for m in construction["floor"]["light_frame_joist_spans"]}
        assert member_catalog[x_span["member"]]["max_clear_span_ft"] >= 18.0

    def test_a_span_beyond_every_light_frame_member_fails_loudly(self, structure_module):
        construction = structure_module.load_construction()
        walls = _bay_walls(("x", 0.0), ("x", 30.0))
        spans = structure_module.span_check(walls, 30.0, 10.0, "some-style-not-in-timber-bay", construction["floor"])
        x_span = next(s for s in spans if s["axis"] == "x")
        assert x_span["ok"] is False
        assert x_span["member"] is None
        assert "intermediate bearing support" in x_span["note"]

    def test_build_section_flags_the_style_vs_construction_type_tension(self, structure_module):
        """The concrete case found empirically on plans/spec-builder-colonial.json: style
        'colonial-revival' is in timber-bay.json's applies_to list, but the plan declares no
        construction_type (wall_thickness() defaults to platform-frame). build_section() must
        say so explicitly rather than silently applying the bay-module cap as settled fact."""
        plan = load_plan("spec-builder-colonial")
        section = structure_module.build_section(plan)
        assert "error" not in section
        assert section["framing_basis"] is not None
        assert "colonial-revival" in section["framing_basis"]
        assert "does not resolve" in section["framing_basis"] or "style-level default" in section["framing_basis"]


class TestStoreyHeights:
    def test_inverts_the_ceiling_formula(self, structure_module):
        """storey-graduation.json: ceiling = module - part*1.25, part = module/12, so
        storey = ceiling / (1 - 1.25/12). A 10 ft-ceiling storey should invert to the pack's own
        documented ~11.17 ft-ish storey, not to 10 ft."""
        plan = {"levels": [{"id": "ground", "index": 0, "floor_to_ceiling_ft": 10, "rooms": []}]}
        storeys = structure_module.storey_heights(plan)
        assert storeys[0]["storey_height_ft"] > 10.0
        assert math.isclose(storeys[0]["storey_height_ft"], 10 / structure_module.STOREY_CEILING_FRACTION, rel_tol=1e-4)

    def test_missing_ceiling_is_unjudged_not_defaulted(self, structure_module):
        plan = {"levels": [{"id": "ground", "index": 0, "rooms": [{"id": "r"}]}]}
        storeys = structure_module.storey_heights(plan)
        assert storeys[0]["storey_height_ft"] is None
        assert "unjudged" in storeys[0]["note"]

    def test_falls_back_to_a_room_ceiling_when_the_level_states_none(self, structure_module):
        plan = {"levels": [{"id": "ground", "index": 0, "rooms": [{"id": "r", "ceiling_ft": 9}]}]}
        storeys = structure_module.storey_heights(plan)
        assert storeys[0]["ceiling_ft"] == 9


class TestGraduationCheck:
    """Regression for bug #3: the bands must be read from storey-graduation.json's own
    height_proportion derived_rules (second/first, then third/second), not hand-transcribed --
    an earlier version used (0.60, 0.85) for the third/second pair, which is actually that
    pack's separate ground-under-piano-nobile band."""

    def test_bands_come_from_the_pack_second_then_third(self, structure_module):
        pack = json.load(open(os.path.join(ROOT, "proportions", "modules", "storey-graduation.json")))
        expected = [tuple(r["range"]) for r in pack["derived_rules"] if r["target_slot"] == "height_proportion"][:2]
        assert expected[0] == (0.78, 0.92)
        assert expected[1] == (0.70, 0.88)  # NOT (0.60, 0.85) -- that is the piano-nobile band

    def test_inapplicable_style_is_not_flagged_at_all(self, structure_module):
        storeys = [{"id": "ground", "index": 0, "storey_height_ft": 8.0}, {"id": "upper", "index": 1, "storey_height_ft": 8.0}]
        result = structure_module.graduation_check(storeys, "log-vernacular-american")
        assert result["applicable"] is False
        assert result["findings"] == []

    def test_a_ratio_within_the_second_first_band_is_ok(self, structure_module):
        storeys = [{"id": "ground", "index": 0, "storey_height_ft": 12.0}, {"id": "upper", "index": 1, "storey_height_ft": 12.0 * 0.85}]
        result = structure_module.graduation_check(storeys, "tidewater-georgian")
        assert result["applicable"] is True
        assert result["findings"][0]["ok"] is True

    def test_an_equal_height_stack_fails_the_second_first_band(self, structure_module):
        """storey-graduation.json's own conflict entry: an equal-height stack (ratio 1.0) is
        outside the 0.78-0.92 band and reads as a different building type entirely."""
        storeys = [{"id": "ground", "index": 0, "storey_height_ft": 10.0}, {"id": "upper", "index": 1, "storey_height_ft": 10.0}]
        result = structure_module.graduation_check(storeys, "tidewater-georgian")
        assert result["findings"][0]["ok"] is False

    def test_a_third_storey_uses_the_third_second_band_not_the_second_first_one(self, structure_module):
        storeys = [
            {"id": "ground", "index": 0, "storey_height_ft": 12.0},
            {"id": "second", "index": 1, "storey_height_ft": 12.0 * 0.85},
            {"id": "third", "index": 2, "storey_height_ft": 12.0 * 0.85 * 0.80},
        ]
        result = structure_module.graduation_check(storeys, "greek-revival-american")
        assert len(result["findings"]) == 2
        assert result["findings"][1]["band"] == [0.70, 0.88]
        assert result["findings"][1]["ok"] is True


class TestRoofHeights:
    def test_pitch_read_from_the_style_and_ridge_computed(self, structure_module):
        storeys = [{"storey_height_ft": 10.0}, {"storey_height_ft": 9.0}]
        footprint = {"width_ft": 40.0, "depth_ft": 30.0}
        roof = structure_module.roof_heights({"style": "tidewater-georgian"}, storeys, footprint)
        assert roof["roof_pitch_rise_per_12"] == 8.0  # midpoint of tidewater-georgian.c02's 7-9:12
        assert roof["grade_to_ridge_ft"] > roof["grade_to_eave_ft"]
        half_span = min(40.0, 30.0) / 2.0
        expected_rise = half_span * (8.0 / 12.0)
        assert math.isclose(roof["grade_to_ridge_ft"], roof["grade_to_eave_ft"] + expected_rise, rel_tol=1e-6)

    def test_no_migrated_pitch_leaves_ridge_unjudged(self, structure_module):
        storeys = [{"storey_height_ft": 9.0}]
        footprint = {"width_ft": 30.0, "depth_ft": 24.0}
        roof = structure_module.roof_heights({"style": "no-such-style-xyz"}, storeys, footprint)
        assert roof["grade_to_ridge_ft"] is None
        assert roof["grade_to_eave_ft"] is not None  # eave never depends on the pitch
        assert "unjudged" in roof["note"]


class TestStairGeometry:
    def test_no_placed_stair_hall_is_not_applicable(self, structure_module):
        geometry_result = {"levels": [{"rooms": []}]}
        result = structure_module.stair_geometry({}, geometry_result, [{"index": 0, "storey_height_ft": 10.0}])
        assert result["applicable"] is False

    def test_a_generously_sized_stair_hall_passes_the_landing_rule(self, structure_module, corpus):
        stair_type = next(t for t, r in corpus["rooms"].items() if r.get("id") == "stair-hall")
        room = {"id": "stair", "type": stair_type, "geometry": {"width_ft": 10.0, "depth_ft": 22.0, "x_ft": 0, "y_ft": 0, "area_sf": 220}}
        geometry_result = {"levels": [{"rooms": [room]}]}
        storeys = [{"index": 0, "storey_height_ft": 9.0}]
        result = structure_module.stair_geometry({}, geometry_result, storeys)
        assert result["applicable"] is True
        assert result["findings"] == []

    def test_a_cramped_stair_hall_fails_the_landing_rule(self, structure_module, corpus):
        """groupings/stair-and-landing-core.json's own hard rule: landing_depth_in at-least
        stair_width_in. A tall storey run inside a small square room cannot satisfy it."""
        stair_type = next(t for t, r in corpus["rooms"].items() if r.get("id") == "stair-hall")
        room = {"id": "stair", "type": stair_type, "geometry": {"width_ft": 10.0, "depth_ft": 10.0, "x_ft": 0, "y_ft": 0, "area_sf": 100}}
        geometry_result = {"levels": [{"rooms": [room]}]}
        storeys = [{"index": 0, "storey_height_ft": 12.0}]
        result = structure_module.stair_geometry({}, geometry_result, storeys)
        assert result["applicable"] is True
        assert any("Landing depth" in f for f in result["findings"])


class TestBuildSectionEndToEnd:
    """Exercises the acceptance criterion's own named plan end to end."""

    def test_tidewater_plan_outside_to_outside_footprint(self, structure_module):
        plan = load_plan("tidewater-georgian-careful")
        section = structure_module.build_section(plan)
        assert "error" not in section
        fp = section["footprint"]
        assert fp["width_ft"] > fp["clear_width_ft"]
        assert fp["depth_ft"] > fp["clear_depth_ft"]
        assert fp["exterior_wall_thickness_in"] > 0

    def test_tidewater_plan_has_wall_lines_and_bearing_lines(self, structure_module):
        plan = load_plan("tidewater-georgian-careful")
        section = structure_module.build_section(plan)
        for lv in section["levels"]:
            assert len(lv["walls"]) >= 4  # at least the four exterior walls
            assert any(w["bearing"] for w in lv["walls"])
            assert any(w["role"] == "exterior" for w in lv["walls"])

    def test_tidewater_plan_section_eave_and_ridge_consistent_with_style_pitch(self, structure_module):
        plan = load_plan("tidewater-georgian-careful")
        section = structure_module.build_section(plan)
        roof = section["roof"]
        assert roof["grade_to_ridge_ft"] is not None
        assert 7.0 <= roof["roof_pitch_rise_per_12"] <= 9.0  # tidewater-georgian.c02's own band
        assert roof["grade_to_ridge_ft"] > roof["grade_to_eave_ft"] > 0

    def test_no_span_over_capacity_passes_silently_on_the_careful_plan(self, structure_module):
        """This specific hand-authored reference plan's bays are all inside the 20 ft hand-
        framed capacity for its (timber-bay) style -- a genuine, checked pass, not an absence
        of checking. Confirmed by asserting spans were actually computed, not just that none
        failed."""
        plan = load_plan("tidewater-georgian-careful")
        section = structure_module.build_section(plan)
        total_spans = sum(len(lv["spans"]) for lv in section["levels"])
        assert total_spans > 0
        assert all(not lv["spans_exceeding_capacity"] for lv in section["levels"])

    def test_spec_builder_plan_flags_a_span_over_capacity(self, structure_module):
        """The concrete case this file's own CLI run turned up: a 23+ ft clear span checked
        against the bay-module cap fails it, and build_section surfaces that as a finding
        rather than silently reporting 0 problems."""
        plan = load_plan("spec-builder-colonial")
        section = structure_module.build_section(plan)
        flagged = [s for lv in section["levels"] for s in lv["spans_exceeding_capacity"]]
        assert flagged, "expected at least one over-capacity span on spec-builder-colonial.json"

    def test_storeys_carry_a_grade_relative_floor_datum(self, structure_module):
        plan = load_plan("tidewater-georgian-careful")
        section = structure_module.build_section(plan)
        ground = next(s for s in section["storeys"] if s["index"] == 0)
        upper = next(s for s in section["storeys"] if s["index"] == 1)
        assert ground["grade_to_floor_ft"] == structure_module.DEFAULT_GRADE_TO_FIRST_FLOOR_FT
        assert upper["grade_to_floor_ft"] == round(ground["grade_to_floor_ft"] + ground["storey_height_ft"], 3)


class TestRenderSection:
    """Both render functions must draw only from the section record -- see the module
    docstring. Smoke-tested by actually writing and re-reading an SVG, not just calling the
    function and trusting it didn't raise."""

    def test_render_section_writes_a_valid_svg(self, structure_module, render_section_module, tmp_path):
        plan = load_plan("tidewater-georgian-careful")
        section = structure_module.build_section(plan)
        out = tmp_path / "section.svg"
        render_section_module.render_section(section, str(out))
        text = out.read_text()
        assert text.startswith("<svg")
        assert "GRADE" in text
        assert "RIDGE" in text  # this plan has a judged pitch

    def test_render_section_handles_an_unjudged_ridge(self, structure_module, render_section_module, tmp_path):
        plan = load_plan("spec-builder-colonial")  # colonial-revival has no migrated roof-pitch constraint
        section = structure_module.build_section(plan)
        assert section["roof"]["grade_to_ridge_ft"] is None
        out = tmp_path / "section.svg"
        render_section_module.render_section(section, str(out))
        text = out.read_text()
        assert "RIDGE UNJUDGED" in text

    def test_render_bearing_diagram_writes_a_valid_svg_and_flags_over_capacity_spans(self, structure_module, render_section_module, tmp_path):
        plan = load_plan("spec-builder-colonial")
        section = structure_module.build_section(plan)
        out = tmp_path / "bearing.svg"
        render_section_module.render_bearing_diagram(section, str(out))
        text = out.read_text()
        assert text.startswith("<svg")
        assert "BEARING LINES" in text
        assert 'class="bad"' in text  # this plan has a flagged over-capacity span
