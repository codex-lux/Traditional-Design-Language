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

    # ---------------------------------------------------------------- site scope
    "lot_width_ft": {"units": "ft", "scope": "site", "note": ""},
    "lot_depth_ft": {"units": "ft", "scope": "site", "note": ""},
    "street_bearing_deg": {"units": "deg", "scope": "site", "note": "Compass bearing of the street the principal front faces, 0-359."},
    "piazza_bearing_deg": {"units": "deg", "scope": "site",
                            "note": "Compass bearing the piazza/porch/loggia faces. The Charleston single house's 'within 45 degrees of southwest' constraint is the canonical use."},
    "party_wall_condition": {"units": "enum", "scope": "site", "note": "freestanding / party-wall-one-side / party-wall-both-sides / row."},
    "setback_front_ft": {"units": "ft", "scope": "site", "note": ""},

    # ---------------------------------------------------------------- section scope
    "ceiling_height_ground_in": {"units": "in", "scope": "section", "note": "Shared with the fault corpus's ceiling_height_in where the constraint and a fault are really the same rule at different scope."},
    "reveal_depth_in": {"units": "in", "scope": "section", "note": "Depth of a masonry reveal at a window or door opening."},
    "wall_thickness_in": {"units": "in", "scope": "section", "note": ""},
    "eave_height_ft": {"units": "ft", "scope": "section", "note": "Grade to eave/cornice line, distinct from facade_height_ft (grade to ridge)."},
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
