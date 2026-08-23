#!/usr/bin/env python3
"""The named variable vocabulary for style constraint `test` expressions
(schema/constraint.schema.json, docs/constraints.md).

A constraint's `test.expression` may reference only variables defined here.
This is deliberate and mirrors the fault corpus's own discipline (`test`
objects reference measurements a photograph or a plan can actually supply,
not invented quantities) — a batch agent migrating a family's constraints
that needs a variable not listed here should list the gap in its report
rather than add one silently. The schema owner reconciles additions.

Each entry: {units, scope, note}. `scope` says what kind of record most
naturally supplies the variable — it is a default, not a restriction; a
plan-scope variable might occasionally be derivable from an elevation too,
and `measurable_from` on the individual constraint's `test` object is what
actually governs evaluability in a given tool.

Run with --verbose to print the table; used by check_constraints.py to
validate every test.expression references only these names.
"""
import re
import sys

VOCABULARY = {
    # ---------------------------------------------------------------- plan scope
    "bay_count": {"units": "count", "scope": "plan",
                  "note": "Number of structural/window bays across the principal (usually entrance) front."},
    "entrance_bay_index": {"units": "count", "scope": "plan",
                            "note": "1-indexed position of the entrance bay counting from the near end. bay_count is odd and entrance_bay_index == (bay_count+1)/2 is the common 'centred entrance' test."},
    "room_count_ground_floor": {"units": "count", "scope": "plan", "note": ""},
    "principal_room_aspect": {"units": "compass", "scope": "plan",
                               "note": "Compass orientation (N/S/E/W/NE/NW/SE/SW) the plan assigns to a named principal room, e.g. the drawing room. A categorical (one-of) variable, not numeric."},
    "circulation_parti": {"units": "enum", "scope": "plan",
                           "note": "The plan's circulation type id, e.g. 'centre-passage', 'side-hall'. one-of tests against this."},
    "depth_and_pile": {"units": "enum", "scope": "plan",
                        "note": "single-pile / double-pile / one-and-a-half-pile, as in the massing catalog's depth_rooms."},
    "service_zone_position": {"units": "enum", "scope": "plan", "note": "front / rear / detached-dependency / basement, etc."},

    # ---------------------------------------------------------------- elevation scope
    "facade_width_ft": {"units": "ft", "scope": "elevation", "note": "Outside-to-outside width of the elevation being evaluated."},
    "facade_height_ft": {"units": "ft", "scope": "elevation",
                          "note": "Grade to ridge, or grade to cornice for a flat-roofed reading -- state which in the constraint's note when it matters."},
    "storey_count": {"units": "count", "scope": "elevation", "note": ""},
    "storey_height_diminish_pct": {"units": "percent", "scope": "elevation",
                                    "note": "Percentage by which an upper storey's height is less than the one below it."},
    "roof_pitch_rise_per_12": {"units": "rise_in_12", "scope": "elevation",
                                "note": "Shared naming with the fault corpus's own roof-pitch variables where one exists -- keep them the same variable, not a constraint-only synonym."},
    "sash_proportion_ratio": {"units": "ratio", "scope": "elevation", "note": "Height:width of a typical sash opening, expressed as a single number (height/width)."},
    "void_to_solid_ratio": {"units": "ratio", "scope": "elevation", "note": "Total glazed opening area over total wall area on one elevation."},
    "opening_vertical_alignment_in": {"units": "in", "scope": "elevation",
                                       "note": "Worst-case centreline offset between a storey's openings and the storey above/below. 0 = perfectly aligned."},
    "window_setback_in": {"units": "in", "scope": "elevation", "note": "Depth of the window frame behind the outer wall face."},
    "cornice_projection_in": {"units": "in", "scope": "elevation", "note": "Shared with the fault corpus's cornice_projection_in where applicable."},
    "glazing_bar_width_in": {"units": "in", "scope": "elevation", "note": "Muntin/glazing-bar sight width."},
    "ornament_relief_in": {"units": "in", "scope": "elevation", "note": "Projection depth of applied plaster/wood ornament off the surface it decorates."},
    "wall_plane_advance_recess_in": {"units": "in", "scope": "elevation",
                                      "note": "Depth a bay or pavilion breaks forward or recesses from the main wall plane."},
    "sash_light_pattern": {"units": "enum", "scope": "elevation",
                            "note": "e.g. '12/12', '9/6', '6/6' -- the pane count above/below the meeting rail. Usually paired with applies_when.date_range rather than a bare constraint."},
    "chimney_position": {"units": "enum", "scope": "elevation",
                          "note": "interior-central / gable-end-interior / gable-end-exterior / paired-exterior, etc."},
    "shutter_leaf_to_sash_ratio": {"units": "ratio", "scope": "elevation",
                                    "note": "Deliberately the same concept as the fault corpus's shutter-half-width-leaf test -- reuse fault-style variable names (shutter_leaf_width_in / window_opening_width_in) directly in the expression rather than this alias where a constraint is really just restating an existing fault at style scope."},

    # ---- added in WP-1.1's worked example (english-classical, american-colonial families) ----
    "roof_slope_deg": {"units": "deg", "scope": "elevation",
                        "note": "A single roof plane's pitch in degrees, for styles whose sources state pitch that way rather than as rise-in-12 (roof_pitch_rise_per_12). Not converted between the two -- keep whichever the source used."},
    "roof_slope_lower_deg": {"units": "deg", "scope": "elevation",
                              "note": "For a roof with two stacked planes on one side (gambrel, a gallery/lean-to break), the plane nearer the eave. Position-based naming, not steepness-based -- the lower plane is sometimes the steeper one (a gambrel's lower slope) and sometimes the shallower one (a gallery roof's lower slope)."},
    "roof_slope_upper_deg": {"units": "deg", "scope": "elevation",
                              "note": "Companion to roof_slope_lower_deg: the plane nearer the ridge."},
    "eave_projection_in": {"units": "in", "scope": "elevation",
                            "note": "Roof/eave overhang beyond the wall face -- a structural or spring-eave projection, distinct from cornice_projection_in which is the classical order's own moulded projection. Also used for a pent roof's projection and for viga ends, which are functionally the same kind of overhang."},
    "glazed_area_pct_wall": {"units": "percent", "scope": "elevation",
                              "note": "Total window-and-door glazed area as a percentage of the wall area it punctures. Distinct from void_to_solid_ratio (a bare ratio) -- use whichever form the source states."},
    "wing_height_deficit_pct": {"units": "percent", "scope": "elevation",
                                  "note": "The percentage by which a subordinate massing element's ridge or eave height falls below the main block's -- a service wing, a hyphen, a pavilion. Recurs across the Palladian-descended styles as the hierarchy-of-parts rule."},
    "window_height_ratio_floors": {"units": "ratio", "scope": "elevation", "note": "A second storey's typical window height as a fraction of the first storey's."},
    "clapboard_exposure_in": {"units": "in", "scope": "elevation", "note": "Weather exposure of a clapboard course."},
    "rake_trim_width_in": {"units": "in", "scope": "elevation", "note": "Width of the rake (gable) or eave trim board."},
    "window_head_to_cornice_offset_in": {"units": "in", "scope": "elevation",
                                           "note": "Vertical gap between a window head (usually the uppermost storey's) and the underside of the cornice or eave above it. Distinct from opening_vertical_alignment_in, which is storey-to-storey opening alignment, not opening-to-roofline."},
    "jetty_overhang_in": {"units": "in", "scope": "elevation", "note": "A framed upper storey's cantilevered overhang beyond the storey below, as in First Period jettied construction."},
    "belt_course_projection_in": {"units": "in", "scope": "elevation", "note": "Projection of a belt/string course off the wall plane."},
    "window_head_rise_in": {"units": "in", "scope": "elevation", "note": "Rise (camber) of a gauged or segmental masonry arch over an opening."},
    "window_head_width_in": {"units": "in", "scope": "elevation", "note": "Sight width of a wood architrave window head/casing."},
    "wall_plate_height_ft": {"units": "ft", "scope": "elevation", "note": "Height of the wall plate above the finished floor -- governs how much of the elevation the roof dominates."},
    "pier_width_in": {"units": "in", "scope": "elevation", "note": "Width of a square masonry pier, as in an arcade."},
    "balcony_depth_ft": {"units": "ft", "scope": "elevation", "note": "Projection of a cantilevered or posted balcony from the wall face."},
    "wall_setback_upper_storey_in": {"units": "in", "scope": "elevation", "note": "How far an upper storey's wall plane sets back from the storey below it."},
    "water_table_height_in": {"units": "in", "scope": "elevation", "note": "Height of the masonry water table above grade."},
    "parapet_height_in": {"units": "in", "scope": "elevation", "note": "Height of a parapet concealing a flat or low-pitched roof."},
    "continuous_shed_dormer_present": {"units": "enum", "scope": "elevation", "note": "Whether a full-width shed dormer runs continuously across a roof slope -- one-of [\"yes\", \"no\"]. The diagnostic Colonial Revival marker several colonial types explicitly forbid."},
    "chimney_height_above_ridge_ft": {"units": "ft", "scope": "elevation", "note": "How far a chimney rises above the ridge line."},
    "gallery_depth_ft": {"units": "ft", "scope": "plan",
                          "note": "Depth of a shading/circulation projection measured from the wall face to its outer support line -- covers a galerie, piazza, corredor, posted porch, or lean-to/gallery depth generically; the exact term varies by region but the measurement is the same thing."},
    "corridor_present": {"units": "enum", "scope": "plan", "note": "Whether the principal floor plan has an interior corridor at all -- one-of [\"yes\", \"no\"]. Several climate-driven plans forbid one outright in favour of cross-ventilated rooms opening directly onto each other or a gallery."},
    "front_slope_dormer_count": {"units": "count", "scope": "plan", "note": "Number of dormers on the street/front roof slope."},
    "rear_slope_dormer_count": {"units": "count", "scope": "plan", "note": "Number of dormers on the rear roof slope (e.g. a saltbox's catslide)."},
    "chimney_count": {"units": "count", "scope": "plan", "note": "Total number of chimneys the plan requires."},
    "chimney_inset_ft": {"units": "ft", "scope": "plan", "note": "How far a chimney sits in from a gable end wall, for styles whose chimneys are paired and interior rather than at the gable end itself."},
    "plan_depth_ft": {"units": "ft", "scope": "plan", "note": "Overall depth of the principal floor plan, front to back -- governs whether interior rooms can still get daylight without a light well or setback."},
    "room_clear_span_ft": {"units": "ft", "scope": "plan", "note": "Maximum clear span of a room, as limited by the available beam or viga length before an intermediate support is required."},
    "centre_passage_width_ft": {"units": "ft", "scope": "plan", "note": "Width of a centre passage/hall that is doing ventilation work (doors at both ends, operable, on axis), not merely circulation."},
    "door_opening_width_ft": {"units": "ft", "scope": "plan", "note": "Overall width of a door opening, e.g. a pair of French casement doors."},

    # ---------------------------------------------------------------- site scope
    "lot_width_ft": {"units": "ft", "scope": "site", "note": ""},
    "lot_depth_ft": {"units": "ft", "scope": "site", "note": ""},
    "street_bearing_deg": {"units": "deg", "scope": "site", "note": "Compass bearing of the street the principal front faces, 0-359."},
    "piazza_bearing_deg": {"units": "deg", "scope": "site",
                            "note": "Compass bearing the piazza/porch/loggia faces. The Charleston single house's 'within 45 degrees of southwest' constraint is the canonical use."},
    "party_wall_condition": {"units": "enum", "scope": "site", "note": "freestanding / party-wall-one-side / party-wall-both-sides / row."},
    "setback_front_ft": {"units": "ft", "scope": "site", "note": ""},
    "cross_slope_pct": {"units": "percent", "scope": "site", "note": "Cross-slope of the site across the building's depth -- what a bank house's plan type depends on existing at all."},

    # ---------------------------------------------------------------- section scope
    "ceiling_height_ground_in": {"units": "in", "scope": "section", "note": "Shared with the fault corpus's ceiling_height_in where the constraint and a fault are really the same rule at different scope."},
    "reveal_depth_in": {"units": "in", "scope": "section", "note": "Depth of a masonry reveal at a window or door opening."},
    "wall_thickness_in": {"units": "in", "scope": "section", "note": ""},
    "eave_height_ft": {"units": "ft", "scope": "section", "note": "Grade to eave/cornice line, distinct from facade_height_ft (grade to ridge)."},
    "floor_height_above_grade_in": {"units": "in", "scope": "section", "note": "Height of the finished floor above grade, typically on piers or a raised masonry storey."},
    "wall_height_to_thickness_ratio": {"units": "ratio", "scope": "section", "note": "A mass wall's slenderness -- height divided by thickness -- for unreinforced adobe or rubble construction, where it is the governing structural limit rather than an engineered calculation."},
}


def check_expression(expr):
    """Return the set of vocabulary names an expression references, and any
    tokens that look like variable references but aren't in VOCABULARY."""
    tokens = set(re.findall(r"[a-z_][a-z0-9_]*", expr))
    # strip Python keywords/builtins that might legitimately appear in a math expression
    tokens -= {"and", "or", "not", "in", "abs", "min", "max", "round"}
    known = tokens & VOCABULARY.keys()
    unknown = tokens - VOCABULARY.keys()
    return known, unknown


def main():
    if "--verbose" in sys.argv:
        by_scope = {}
        for name, v in VOCABULARY.items():
            by_scope.setdefault(v["scope"], []).append((name, v))
        for scope in ("plan", "elevation", "site", "section"):
            print(f"\n{scope.upper()} ({len(by_scope.get(scope, []))})")
            for name, v in sorted(by_scope.get(scope, [])):
                print(f"  {name:32s} {v['units']:10s} {v['note'][:70]}")
    else:
        print(f"{len(VOCABULARY)} variables. Run with --verbose to list them.")


if __name__ == "__main__":
    main()
