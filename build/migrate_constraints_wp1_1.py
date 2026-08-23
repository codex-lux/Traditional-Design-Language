#!/usr/bin/env python3
"""One-shot migration script for WP-1.1's worked example: assigns id/scope/
test to the existing (kind, statement, severity) constraints already on the
english-classical and american-colonial families' 28 style/variant nodes.

Not meant to be reused for other families as-is -- MIGRATIONS below is
hand-authored per constraint, the way a migration-batch agent would do it
for its own family. Kept as a script rather than done by hand in the JSON
editor so the id-numbering and the merge are mechanical and auditable, and
so this run is reproducible if a source constraint's statement is corrected
later and the migration needs re-deriving.

Each entry in MIGRATIONS[style_id] is a dict for the constraint at that
list index (0-based, matching the existing constraints array order) with:
  scope: required
  test:  optional dict (expression/direction/threshold/upper/set/units/
         measurable_from/note) -- omitted entirely for scope: judgment
         constraints, and for hard constraints that are honestly compound/
         qualitative enough that no single test would be accurate.

Run: python3 build/migrate_constraints_wp1_1.py [--dry-run]
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

J = "judgment"  # shorthand

MIGRATIONS = {

"adam-style": [
    {"scope": "elevation", "test": {"expression": "ornament_relief_in", "direction": "at-most",
        "threshold": 20, "units": "mm", "measurable_from": "elevation",
        "note": "Source states the figure in millimetres; the vocabulary variable is named _in by convention but its unit here is the units field, mm, not inches."}},
    {"scope": J},
    {"scope": "elevation", "test": {"expression": "glazing_bar_width_in", "direction": "at-most",
        "threshold": 20, "units": "mm", "measurable_from": "elevation",
        "note": "Tests the glazing-bar clause only. The second clause -- cornice/architrave profiles reduced by roughly a third from mid-Georgian section -- has no recorded mid-Georgian baseline value to compare against in this corpus, so it stays prose."}},
    {"scope": J},
    {"scope": "elevation", "test": {"expression": "wall_plane_advance_recess_in", "direction": "between",
        "threshold": 300, "upper": 600, "units": "mm", "measurable_from": "elevation"}},
],

"english-baroque": [
    {"scope": J},
    {"scope": J},
    {"scope": "elevation", "test": {"expression": "sash_proportion_ratio", "direction": "between",
        "threshold": 1.8, "upper": 2.1, "units": "ratio", "measurable_from": "elevation",
        "note": "Tests the sash proportion. The glazing-bar clause (not thinner than 25mm) is a second numeric claim in the same statement and stays prose-only here -- one test per constraint."}},
    {"scope": J},
    {"scope": "elevation", "test": {"expression": "wing_height_deficit_pct", "direction": "at-least",
        "threshold": 30, "units": "percent", "measurable_from": "elevation"}},
],

"english-georgian": [
    {"scope": "elevation", "test": {"expression": "sash_proportion_ratio", "direction": "between",
        "threshold": 1.6, "upper": 2.0, "units": "ratio", "measurable_from": "elevation"}},
    {"scope": "elevation", "test": {"expression": "storey_height_diminish_pct", "direction": "between",
        "threshold": 10, "upper": 20, "units": "percent", "measurable_from": "elevation",
        "note": "States the ground-to-first-floor pair. 'Every storey above diminishes' is the same variable applied storey-pair by storey-pair further up and stays prose beyond the first pair."}},
    {"scope": "elevation", "test": {"expression": "window_setback_in", "direction": "at-least",
        "threshold": 100, "units": "mm", "measurable_from": "elevation",
        "note": "London Building Act of 1709."}},
    {"scope": "elevation", "test": {"expression": "void_to_solid_ratio", "direction": "at-most",
        "threshold": 1, "units": "ratio", "measurable_from": "elevation",
        "note": "Tests the solid-dominates-void clause. 'Openings must align vertically between storeys without exception' has no numeric tolerance stated and stays prose."}},
    {"scope": J},
],

"english-georgian-country-house": [
    {"scope": J},
    {"scope": "elevation", "test": {"expression": "storey_height_diminish_pct", "direction": "between",
        "threshold": 10, "upper": 20, "units": "percent", "measurable_from": "elevation",
        "note": "Same variable and test as english-georgian's storey-height constraint -- this variant restates the parent's rule. The sash-proportion clause (1.7:1-2:1) in the same statement stays prose."}},
    {"scope": J},
    {"scope": "elevation", "test": {"expression": "wing_height_deficit_pct", "direction": "at-least",
        "threshold": 25, "units": "percent", "measurable_from": "elevation"}},
    {"scope": J},
],

"english-georgian-townhouse": [
    {"scope": J},
    {"scope": "elevation", "test": {"expression": "window_setback_in", "direction": "at-least",
        "threshold": 100, "units": "mm", "measurable_from": "elevation",
        "note": "London Building Act of 1709."}},
    {"scope": "elevation", "test": {"expression": "storey_height_diminish_pct", "direction": "between",
        "threshold": 5, "upper": 20, "units": "percent", "measurable_from": "elevation",
        "note": "Here the differential runs the other direction from the usual ground>first hierarchy -- first floor is the tallest, piano-nobile-like storey of a London terrace. Same variable, applied to the first-over-ground pair."}},
    {"scope": "plan", "test": {"expression": "plan_depth_ft", "direction": "at-most",
        "threshold": 12.5, "units": "m", "measurable_from": "plan",
        "note": "Source states the figure in metres directly. The fire-break party wall and no-window-on-party-wall clauses in the same statement are categorical, not numeric, and stay prose."}},
    {"scope": J},
],

"english-palladian": [
    {"scope": J},
    {"scope": J},
    {"scope": J},
    {"scope": J},
    {"scope": "elevation", "test": {"expression": "wing_height_deficit_pct", "direction": "at-least",
        "threshold": 25, "units": "percent", "measurable_from": "elevation"}},
],

"regency": [
    {"scope": J},
    {"scope": "elevation", "test": {"expression": "balcony_depth_ft", "direction": "at-least",
        "threshold": 900, "units": "mm", "measurable_from": "elevation",
        "note": "Tests the balcony/veranda depth clause. The window-to-floor gap (within 150mm) is the same statement's other numeric claim and stays prose."}},
    {"scope": "elevation", "test": {"expression": "glazing_bar_width_in", "direction": "between",
        "threshold": 12, "upper": 18, "units": "mm", "measurable_from": "elevation"}},
    {"scope": "elevation", "test": {"expression": "roof_slope_deg", "direction": "between",
        "threshold": 22, "upper": 30, "units": "deg", "measurable_from": "elevation",
        "note": "The eave-projection figure (450-750mm) stated in the same clause applies only 'where wide eaves are used' and is conditional, so it stays prose rather than being folded into this test."}},
    {"scope": J},
],

"dutch-colonial-american": [
    {"scope": "elevation", "test": {"expression": "chimney_position", "direction": "one-of",
        "set": ["gable-end-interior", "gable-end-exterior"], "measurable_from": "elevation"}},
    {"scope": "elevation", "test": {"expression": "wall_plate_height_ft", "direction": "between",
        "threshold": 7, "upper": 9, "units": "ft", "measurable_from": "elevation"}},
    {"scope": "elevation", "test": {"expression": "roof_slope_lower_deg", "direction": "between",
        "threshold": 60, "upper": 72, "units": "deg", "measurable_from": "elevation",
        "note": "Tests the lower (eave-side) gambrel slope. The upper slope (18-30deg) and the break point (55-70% of half-span) are the same statement's other numeric claims and stay prose -- one test per constraint."}},
    {"scope": "elevation", "test": {"expression": "continuous_shed_dormer_present", "direction": "one-of",
        "set": ["no"], "measurable_from": "elevation"}},
    {"scope": "section", "test": {"expression": "wall_thickness_in", "direction": "between",
        "threshold": 20, "upper": 30, "units": "in", "measurable_from": "section"}},
],

"hudson-valley-dutch": [
    {"scope": "section", "test": {"expression": "wall_thickness_in", "direction": "at-least",
        "threshold": 20, "units": "in", "measurable_from": "section"}},
    {"scope": "elevation", "test": {"expression": "roof_pitch_rise_per_12", "direction": "between",
        "threshold": 12, "upper": 17, "units": "rise_in_12", "measurable_from": "elevation",
        "note": "Tests the roof pitch clause. Wall plate height (7-9ft) is the same statement's other numeric claim, already tested on the parent dutch-colonial-american node, and stays prose here."}},
    {"scope": "elevation", "test": {"expression": "chimney_position", "direction": "one-of",
        "set": ["gable-end-interior", "gable-end-exterior"], "measurable_from": "elevation"}},
    {"scope": "elevation", "test": {"expression": "eave_projection_in", "direction": "between",
        "threshold": 18, "upper": 24, "units": "in", "measurable_from": "elevation"}},
    {"scope": "elevation", "test": {"expression": "glazed_area_pct_wall", "direction": "at-most",
        "threshold": 10, "units": "percent", "measurable_from": "elevation",
        "note": "Tests the glazed-area clause. The sash/casement-by-date clause is date-conditional (OQ 22, no date-conditional resolution exists yet) and stays prose."}},
],

"new-jersey-dutch-gambrel": [
    {"scope": "elevation", "test": {"expression": "roof_slope_lower_deg - roof_slope_upper_deg", "direction": "at-least",
        "threshold": 30, "units": "deg", "measurable_from": "elevation",
        "note": "This variant states the differentiation itself as the enforceable rule ('must differ by at least 30 degrees'), unlike the parent dutch-colonial-american's softer version -- so the difference expression is the more faithful test here, not the raw range."}},
    {"scope": "elevation", "test": {"expression": "eave_projection_in", "direction": "between",
        "threshold": 24, "upper": 36, "units": "in", "measurable_from": "elevation",
        "note": "The sweep radius (4-8ft) is the same statement's other numeric claim and stays prose."}},
    {"scope": "elevation", "test": {"expression": "continuous_shed_dormer_present", "direction": "one-of",
        "set": ["no"], "measurable_from": "elevation"}},
    {"scope": J},
    {"scope": "plan", "test": {"expression": "gallery_depth_ft", "direction": "between",
        "threshold": 8, "upper": 10, "units": "ft", "measurable_from": "plan",
        "note": "A posted porch under the sprung eave is the same depth concept as a galerie/piazza."}},
],

"french-colonial-american": [
    {"scope": "plan", "test": {"expression": "corridor_present", "direction": "one-of",
        "set": ["no"], "measurable_from": "plan",
        "note": "Tests the no-corridor clause. 'Every habitable room must have exterior openings on two walls' is a per-room universal claim the vocabulary has no single variable for and stays prose."}},
    {"scope": "plan", "test": {"expression": "gallery_depth_ft", "direction": "at-least",
        "threshold": 8, "units": "ft", "measurable_from": "plan"}},
    {"scope": "elevation", "test": {"expression": "roof_slope_upper_deg", "direction": "between",
        "threshold": 40, "upper": 50, "units": "deg", "measurable_from": "elevation",
        "note": "Tests the main-roof (ridge-side) pitch. The gallery-roof (eave-side) pitch, 20-30deg, is the same statement's second slope and stays prose."}},
    {"scope": "section", "test": {"expression": "floor_height_above_grade_in", "direction": "at-least",
        "threshold": 18, "units": "in", "measurable_from": "section"}},
    {"scope": "plan", "test": {"expression": "door_opening_width_ft", "direction": "between",
        "threshold": 5.5, "upper": 7.0, "units": "ft", "measurable_from": "plan",
        "note": "Tests the door width clause. Height (full ceiling less 12-18in) and the louvred-blind leaf-width-equals-half-opening clause stay prose."}},
],

"creole-cottage-vernacular": [
    {"scope": "plan", "test": {"expression": "corridor_present", "direction": "one-of",
        "set": ["no"], "measurable_from": "plan"}},
    {"scope": "section", "test": {"expression": "ceiling_height_ground_in", "direction": "at-least",
        "threshold": 132, "units": "in", "measurable_from": "section",
        "note": "11ft converted to inches exactly (132in) to match the vocabulary variable's unit."}},
    {"scope": J},
    {"scope": "section", "test": {"expression": "floor_height_above_grade_in", "direction": "between",
        "threshold": 12, "upper": 36, "units": "in", "measurable_from": "section",
        "note": "The chimney-position clause in the same statement is categorical and stays prose."}},
    {"scope": "elevation", "test": {"expression": "shutter_leaf_to_sash_ratio", "direction": "equals",
        "threshold": 0.5, "units": "ratio", "measurable_from": "elevation"}},
],

"raised-creole-plantation": [
    {"scope": "section", "test": {"expression": "floor_height_above_grade_in", "direction": "at-least",
        "threshold": 72, "units": "in", "measurable_from": "section",
        "note": "8ft is the stated target but 6ft (72in) is the constraint's actual hard floor ('absolute minimum 6 ft') -- tested at the true minimum."}},
    {"scope": "plan", "test": {"expression": "gallery_depth_ft", "direction": "between",
        "threshold": 8, "upper": 14, "units": "ft", "measurable_from": "plan"}},
    {"scope": "elevation", "test": {"expression": "pier_width_in", "direction": "between",
        "threshold": 16, "upper": 24, "units": "in", "measurable_from": "elevation",
        "note": "Tests the masonry pier (below the gallery floor line). The wooden colonnette above (6-9in) is the statement's other member size and stays prose."}},
    {"scope": "plan", "test": {"expression": "corridor_present", "direction": "one-of",
        "set": ["no"], "measurable_from": "plan"}},
    {"scope": "elevation", "test": {"expression": "roof_slope_upper_deg", "direction": "between",
        "threshold": 40, "upper": 50, "units": "deg", "measurable_from": "elevation",
        "note": "Same convention as french-colonial-american: tests the main-body (ridge-side) pitch, not the gallery pitch."}},
],

"georgian-colonial-american": [
    {"scope": "plan", "test": {"expression": "bay_count", "direction": "one-of",
        "set": ["3", "5", "7"], "measurable_from": "plan",
        "note": "The centred-entrance clause is the vocabulary's own documented corollary of an odd bay count (entrance_bay_index == (bay_count+1)/2) rather than a second independent test."}},
    {"scope": "elevation", "test": {"expression": "roof_pitch_rise_per_12", "direction": "between",
        "threshold": 8, "upper": 10, "units": "rise_in_12", "measurable_from": "elevation"}},
    {"scope": J},
    {"scope": "elevation", "test": {"expression": "shutter_leaf_to_sash_ratio", "direction": "equals",
        "threshold": 0.5, "units": "ratio", "measurable_from": "elevation"}},
    {"scope": "elevation", "test": {"expression": "water_table_height_in", "direction": "between",
        "threshold": 24, "upper": 36, "units": "in", "measurable_from": "elevation",
        "note": "Tests the water table height. Brick bond pattern and gauged-arch rise (4-6in) are the same statement's other clauses and stay prose."}},
],

"charleston-georgian": [
    {"scope": "site", "test": {"expression": "abs(piazza_bearing_deg - 225)", "direction": "at-most",
        "threshold": 45, "units": "deg", "measurable_from": "site",
        "note": "225 degrees is due southwest; the expression is the angular distance from it."}},
    {"scope": "section", "test": {"expression": "ceiling_height_ground_in", "direction": "at-least",
        "threshold": 138, "units": "in", "measurable_from": "section",
        "note": "11ft6in converted to inches exactly (138in)."}},
    {"scope": J},
    {"scope": "plan", "test": {"expression": "gallery_depth_ft", "direction": "at-least",
        "threshold": 10, "units": "ft", "measurable_from": "plan"}},
    {"scope": J},
],

"mid-atlantic-georgian": [
    {"scope": "section", "test": {"expression": "wall_thickness_in", "direction": "between",
        "threshold": 13, "upper": 24, "units": "in", "measurable_from": "section",
        "note": "Union of the two material-specific ranges (18-24in stone, 13-18in brick), which are contiguous at 18in with no gap. This tests thickness-is-consistent-with-at-least-one-material; it cannot by itself tell which material's own range was actually used."}},
    {"scope": "elevation", "test": {"expression": "belt_course_projection_in", "direction": "between",
        "threshold": 1.5, "upper": 2.5, "units": "in", "measurable_from": "elevation",
        "note": "Tests the belt course's projection. Its depth (6-9in) is the statement's other dimension and stays prose."}},
    {"scope": "elevation", "test": {"expression": "roof_pitch_rise_per_12", "direction": "between",
        "threshold": 8, "upper": 10, "units": "rise_in_12", "measurable_from": "elevation",
        "note": "The chimney-position clause in the same statement is already covered by chimney_position elsewhere in this family and stays prose here."}},
    {"scope": "elevation", "test": {"expression": "window_head_rise_in", "direction": "between",
        "threshold": 4, "upper": 6, "units": "in", "measurable_from": "elevation",
        "note": "Tests the gauged-brick-arch branch. The dressed-stone-lintel alternative has no numeric claim and stays prose."}},
    {"scope": J},
],

"new-england-georgian": [
    {"scope": "plan", "test": {"expression": "chimney_inset_ft", "direction": "between",
        "threshold": 5, "upper": 12, "units": "ft", "measurable_from": "plan"}},
    {"scope": "elevation", "test": {"expression": "roof_pitch_rise_per_12", "direction": "between",
        "threshold": 9, "upper": 11, "units": "rise_in_12", "measurable_from": "elevation"}},
    {"scope": "elevation", "test": {"expression": "cornice_projection_in", "direction": "between",
        "threshold": 12, "upper": 24, "units": "in", "measurable_from": "elevation",
        "note": "The cornice return, reusing the existing cornice_projection_in variable for this depth dimension."}},
    {"scope": "elevation", "test": {"expression": "window_head_width_in", "direction": "between",
        "threshold": 5, "upper": 6, "units": "in", "measurable_from": "elevation",
        "note": "Tests the wood architrave width. 'Must not appear on a clapboard wall' (masonry heads forbidden) is the statement's categorical clause and stays prose."}},
    {"scope": "elevation", "test": {"expression": "shutter_leaf_to_sash_ratio", "direction": "equals",
        "threshold": 0.5, "units": "ratio", "measurable_from": "elevation",
        "note": "The sash-by-date and fanlight-date clauses in the same statement are date-conditional (OQ 22, unresolved) and stay prose."}},
],

"tidewater-georgian": [
    {"scope": "elevation", "test": {"expression": "chimney_height_above_ridge_ft", "direction": "at-least",
        "threshold": 6, "units": "ft", "measurable_from": "elevation",
        "note": "The interior-end-or-exterior position clause is categorical and stays prose."}},
    {"scope": "elevation", "test": {"expression": "roof_pitch_rise_per_12", "direction": "between",
        "threshold": 7, "upper": 9, "units": "rise_in_12", "measurable_from": "elevation"}},
    {"scope": "plan", "test": {"expression": "centre_passage_width_ft", "direction": "between",
        "threshold": 10, "upper": 14, "units": "ft", "measurable_from": "plan"}},
    {"scope": "elevation", "test": {"expression": "water_table_height_in", "direction": "between",
        "threshold": 24, "upper": 36, "units": "in", "measurable_from": "elevation",
        "note": "Tests the water table height. Bond pattern and the date-conditional arch-rise clause (OQ 22) stay prose."}},
    {"scope": "plan", "test": {"expression": "service_zone_position", "direction": "one-of",
        "set": ["detached-dependency"], "measurable_from": "plan",
        "note": "Tests the categorical placement claim via the existing service_zone_position enum. Distance (25ft+) and hyphen-length figures stay prose."}},
],

"german-pennsylvania-colonial": [
    {"scope": J},
    {"scope": "elevation", "test": {"expression": "roof_pitch_rise_per_12", "direction": "between",
        "threshold": 10, "upper": 12, "units": "rise_in_12", "measurable_from": "elevation"}},
    {"scope": "elevation", "test": {"expression": "eave_projection_in", "direction": "between",
        "threshold": 30, "upper": 42, "units": "in", "measurable_from": "elevation",
        "note": "Tests the pent roof's projection. Pitch (25-35deg) and corner return (12-24in) are the statement's other numeric claims and stay prose."}},
    {"scope": "section", "test": {"expression": "wall_thickness_in", "direction": "between",
        "threshold": 18, "upper": 30, "units": "in", "measurable_from": "section",
        "note": "Tests the wall thickness. The quoin-to-coursing size ratio is a niche one-off comparison and stays prose."}},
    {"scope": J},
],

"pennsylvania-bank-house": [
    {"scope": "site", "test": {"expression": "cross_slope_pct", "direction": "at-least",
        "threshold": 12.5, "units": "percent", "measurable_from": "site",
        "note": "1:8. The fall figure (not less than 6ft) restates the same requirement over the building's actual depth and stays prose."}},
    {"scope": "section", "test": {"expression": "wall_thickness_in", "direction": "at-least",
        "threshold": 22, "units": "in", "measurable_from": "section",
        "note": "Tests the lower-storey wall thickness, the cleanest single claim in a compound statement. The two grade-relationship clauses (finished floor within 12in of downhill grade; uphill wall bermed within 12in of principal floor) stay prose."}},
    {"scope": J},
    {"scope": J},
    {"scope": "elevation", "test": {"expression": "roof_pitch_rise_per_12", "direction": "between",
        "threshold": 12, "upper": 14, "units": "rise_in_12", "measurable_from": "elevation",
        "note": "The pent roof clause restates the same feature already tested on german-pennsylvania-colonial and stays prose here."}},
],

"new-england-colonial": [
    {"scope": "plan", "test": {"expression": "chimney_count", "direction": "equals",
        "threshold": 1, "units": "count", "measurable_from": "plan",
        "note": "Tests the count. Base size (7x7ft minimum, typically 8-12ft square) is a two-dimensional claim the vocabulary has no single variable for and stays prose."}},
    {"scope": "elevation", "test": {"expression": "roof_pitch_rise_per_12", "direction": "between",
        "threshold": 10, "upper": 14, "units": "rise_in_12", "measurable_from": "elevation"}},
    {"scope": "elevation", "test": {"expression": "window_head_to_cornice_offset_in", "direction": "between",
        "threshold": 0, "upper": 8, "units": "in", "measurable_from": "elevation",
        "note": "The no-frieze-band clause (a frieze over 4in converts the elevation to Georgian) is the same statement's other claim and stays prose."}},
    {"scope": J},
    {"scope": "elevation", "test": {"expression": "clapboard_exposure_in", "direction": "between",
        "threshold": 4, "upper": 5, "units": "in", "measurable_from": "elevation",
        "note": "Tests the weather-elevation clapboard exposure. The up-to-6in-elsewhere and coastal shingle-exposure clauses stay prose."}},
],

"cape-cod-colonial": [
    {"scope": "elevation", "test": {"expression": "window_head_to_cornice_offset_in", "direction": "at-most",
        "threshold": 14, "units": "in", "measurable_from": "elevation",
        "note": "Tests the window-head-to-cornice clause. Eave height (8ft-9ft6in) is the statement's other numeric claim and stays prose."}},
    {"scope": "elevation", "test": {"expression": "front_slope_dormer_count", "direction": "equals",
        "threshold": 0, "units": "count", "measurable_from": "elevation"}},
    {"scope": "elevation", "test": {"expression": "roof_pitch_rise_per_12", "direction": "between",
        "threshold": 9, "upper": 12, "units": "rise_in_12", "measurable_from": "elevation"}},
    {"scope": "elevation", "test": {"expression": "rake_trim_width_in", "direction": "at-most",
        "threshold": 6, "units": "in", "measurable_from": "elevation",
        "note": "The corner-return dimension (6-12in) is the statement's other numeric claim and stays prose."}},
    {"scope": "elevation", "test": {"expression": "eave_projection_in", "direction": "at-most",
        "threshold": 8, "units": "in", "measurable_from": "elevation",
        "note": "Tests the overhang clause. Shingle exposure and sill height are the statement's other numeric claims and stay prose."}},
],

"garrison-colonial": [
    {"scope": "elevation", "test": {"expression": "jetty_overhang_in", "direction": "at-most",
        "threshold": 24, "units": "in", "measurable_from": "elevation",
        "note": "Tests the statement's absolute ceiling ('never exceed 24 in'), which covers both the framed (14-20in) and hewn (2-6in) sub-cases without needing to know which construction method is used."}},
    {"scope": J},
    {"scope": "plan", "test": {"expression": "chimney_count", "direction": "equals",
        "threshold": 1, "units": "count", "measurable_from": "plan"}},
    {"scope": "elevation", "test": {"expression": "window_height_ratio_floors", "direction": "between",
        "threshold": 0.80, "upper": 0.90, "units": "ratio", "measurable_from": "elevation"}},
    {"scope": J},
],

"saltbox-colonial": [
    {"scope": "section", "test": {"expression": "eave_height_ft", "direction": "between",
        "threshold": 6.5, "upper": 8.5, "units": "ft", "measurable_from": "section"}},
    {"scope": "elevation", "test": {"expression": "roof_slope_deg", "direction": "between",
        "threshold": 45, "upper": 52, "units": "deg", "measurable_from": "elevation",
        "note": "Tests the front slope. The rear/catslide slope (38-45deg when broken, or matching the front when integral) is the statement's other, conditional claim and stays prose."}},
    {"scope": "elevation", "test": {"expression": "rear_slope_dormer_count", "direction": "equals",
        "threshold": 0, "units": "count", "measurable_from": "elevation"}},
    {"scope": "plan", "test": {"expression": "gallery_depth_ft", "direction": "between",
        "threshold": 10, "upper": 14, "units": "ft", "measurable_from": "plan",
        "note": "Reuses the general shed/lean-to depth concept."}},
    {"scope": "elevation", "test": {"expression": "window_head_to_cornice_offset_in", "direction": "at-most",
        "threshold": 8, "units": "in", "measurable_from": "elevation",
        "note": "Tests the head-to-eave clause. The date-conditional sash pattern (12/12 or 12/8 before c.1750, 9/6 after) is OQ 22 territory and stays prose."}},
],

"spanish-colonial-american": [
    {"scope": "structural" if False else "section", "test": {"expression": "wall_height_to_thickness_ratio", "direction": "at-most",
        "threshold": 10, "units": "ratio", "measurable_from": "section",
        "note": "Tests the looser (adobe, 10x) bound. Unreinforced rubble's stricter 8x limit is the statement's other case -- a rubble wall between 8x and 10x passes this test while still being able to violate its own material's real limit. Flagged as a known imprecision rather than silently resolved."}},
    {"scope": "plan", "test": {"expression": "room_clear_span_ft", "direction": "between",
        "threshold": 12, "upper": 18, "units": "ft", "measurable_from": "plan"}},
    {"scope": "elevation", "test": {"expression": "glazed_area_pct_wall", "direction": "at-most",
        "threshold": 15, "units": "percent", "measurable_from": "elevation"}},
    {"scope": "elevation", "test": {"expression": "roof_pitch_rise_per_12", "direction": "at-most",
        "threshold": 6, "units": "rise_in_12", "measurable_from": "elevation",
        "note": "The statement is a disjunction (flat, or 3:12-5:12 tile) but also gives a single unconditional ceiling ('pitches above 6:12 are foreign') that covers both branches safely -- flat is 0, the pitched range tops out at 5 -- so this is the one clean test, not a union guess."}},
    {"scope": J},
],

"california-mission-colonial": [
    {"scope": "elevation", "test": {"expression": "pier_width_in", "direction": "between",
        "threshold": 30, "upper": 48, "units": "in", "measurable_from": "elevation",
        "note": "2ft6in-4ft converted to inches. The arch-opening-to-pier-width ratio (1.5-2.5x) is the statement's other numeric claim and stays prose."}},
    {"scope": "elevation", "test": {"expression": "roof_pitch_rise_per_12", "direction": "between",
        "threshold": 3, "upper": 5, "units": "rise_in_12", "measurable_from": "elevation",
        "note": "Eave projection (12-20in) is the statement's other numeric claim and stays prose."}},
    {"scope": "section", "test": {"expression": "wall_thickness_in", "direction": "at-least",
        "threshold": 24, "units": "in", "measurable_from": "section",
        "note": "The conditional buttress-spacing clause stays prose."}},
    {"scope": "plan", "test": {"expression": "gallery_depth_ft", "direction": "at-least",
        "threshold": 10, "units": "ft", "measurable_from": "plan"}},
    {"scope": J},
],

"monterey-colonial": [
    {"scope": "elevation", "test": {"expression": "balcony_depth_ft", "direction": "between",
        "threshold": 5, "upper": 7, "units": "ft", "measurable_from": "elevation",
        "note": "The no-posts-to-grade clause is categorical and stays prose."}},
    {"scope": "elevation", "test": {"expression": "wall_setback_upper_storey_in", "direction": "between",
        "threshold": 6, "upper": 12, "units": "in", "measurable_from": "elevation",
        "note": "Ground-storey wall thickness (not less than 24in adobe) is the statement's other numeric claim and stays prose."}},
    {"scope": "elevation", "test": {"expression": "roof_pitch_rise_per_12", "direction": "between",
        "threshold": 4, "upper": 5, "units": "rise_in_12", "measurable_from": "elevation",
        "note": "The hip-not-gable and wood-shingle-not-clay-tile clauses are categorical and stay prose."}},
    {"scope": "elevation", "test": {"expression": "window_head_width_in", "direction": "between",
        "threshold": 4, "upper": 5, "units": "in", "measurable_from": "elevation"}},
    {"scope": J},
],

"new-mexico-adobe": [
    {"scope": "section", "test": {"expression": "wall_thickness_in", "direction": "between",
        "threshold": 24, "upper": 36, "units": "in", "measurable_from": "section",
        "note": "Tests thickness. Wall-height-to-thickness ratio (not exceeding 10x) and glazed area (not exceeding 12%) each have their own variable, already exercised elsewhere in this family, and stay prose here -- one test per constraint."}},
    {"scope": "plan", "test": {"expression": "room_clear_span_ft", "direction": "at-most",
        "threshold": 16, "units": "ft", "measurable_from": "plan"}},
    {"scope": "elevation", "test": {"expression": "parapet_height_in", "direction": "between",
        "threshold": 12, "upper": 24, "units": "in", "measurable_from": "elevation",
        "note": "The no-pitch/no-gable/no-eave clauses are categorical and stay prose; canale drainage rate and projection are the statement's other numeric claims and also stay prose."}},
    {"scope": J},
    {"scope": "elevation", "test": {"expression": "eave_projection_in", "direction": "between",
        "threshold": 12, "upper": 24, "units": "in", "measurable_from": "elevation",
        "note": "Vigas are functionally the same kind of structural roof-member overhang the variable already covers elsewhere. 'Must actually carry the roof' is a structural-truth claim no plan measurement alone confirms and stays prose."}},
],

}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    changed = 0
    for style_id, entries in MIGRATIONS.items():
        path = os.path.join(ROOT, "styles", f"{style_id}.json")
        node = json.load(open(path))
        constraints = node.get("constraints", [])
        if len(constraints) != len(entries):
            print(f"MISMATCH {style_id}: {len(constraints)} constraints on node, "
                  f"{len(entries)} migration entries", file=sys.stderr)
            sys.exit(1)
        for i, (c, m) in enumerate(zip(constraints, entries)):
            c["id"] = f"{style_id}.c{i+1:02d}"
            c["scope"] = m["scope"]
            if "test" in m:
                c["test"] = m["test"]
        if not a.dry_run:
            with open(path, "w") as f:
                json.dump(node, f, indent=2, ensure_ascii=False)
                f.write("\n")
        changed += 1
    print(f"{'would migrate' if a.dry_run else 'migrated'} {changed} style node(s), "
          f"{sum(len(v) for v in MIGRATIONS.values())} constraints")


if __name__ == "__main__":
    main()
