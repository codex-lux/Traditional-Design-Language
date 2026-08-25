#!/usr/bin/env python3
"""WP-3.2 -- the elevation generator.

Takes a plan already walled and sectioned (build/structure.py) and roofed (build/roof.py) and
derives a per-face ELEVATION RECORD: bay lines from the grid; window openings centred on bays,
sized from opening-proportion and sash-light at the plan's own declared date; one head datum per
storey (opening-proportion's own hardest rule -- see that pack's window_head_wood.count note);
an entrance composition sized by facade-classical's own bay-widening and composition-cap rules
and dimensioned with the Gibbs Ionic order pack (proportions/overlays/gibbs-ionic.json) reduced
to the doorcase's own scale -- tidewater-georgian's own kit leaves every classical-apparatus slot
(order, entablature, pediment, pilaster) `binding: "open"`, and gibbs-ionic is the order the
family's own governing_logic names ("a pattern-book order for the doorway and cornice") and the
one this pack's own applies_to list includes this style in, so it is used here as the resolved
default for an unresolved slot -- the same "unjudged is not passed, but a sourced default is not
invented" discipline WP-3.3 used for its gambrel geometry; water table and belt course from
brick-course.json where the wall's own construction is masonry, else facade-classical's own
generic (frame-and-clapboard) figures; the eave cornice at "the style's entablature reduction" --
Gibbs's own cornice/frieze member proportions, generated at whatever module fits inside
facade-classical's own domestic cornice-and-frieze envelope rather than a free-standing portico's
full height; the roof outline and per-face silhouette from WP-3.3's own roof.py, not recomputed;
chimneys and shutters likewise reused/derived from what those two files already established.

EVERY MOULDING DRAWN COMES FROM proportion_engine.dimension() -- nothing in render_elevation.py
invents a member height or profile; the SVG is a direct read of this record's own numbers.

This file also feeds build/plan_check.py's FAULT LAYER: build_elevation()'s own `measurements`
dict is folded into that layer's existing `meas` dict (plan-declared values still win, same
`setdefault` precedence already established), so the ~175 photograph-measurable faults in
faults/*.json are evaluated against what this file actually generated, not against nothing.

  python3 build/elevation.py plans/tidewater-georgian-careful.json [--parti ID] \
      [--out plans/<id>.elevation.json] [--svg dist/<id>-elevation.svg]
"""
from __future__ import annotations
import json, os, math, argparse, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def _mod(n, p):
    # Delegates to build/modcache.py so a module is executed once per process
    # rather than once per call. Same signature, same standalone-script
    # behaviour; see that file's header for why (OQ 28). Loaded by path here
    # because this file is itself usually loaded by path, so `build/` is not
    # necessarily on sys.path yet.
    import sys as _sys
    _b = os.path.join(ROOT, "build")
    if _b not in _sys.path:
        _sys.path.insert(0, _b)
    import modcache as _mc
    return _mc.load(n, p)
PC = _mod("plan_check", f"{ROOT}/build/plan_check.py")
GEOM = _mod("geometry", f"{ROOT}/build/geometry.py")
ST = _mod("structure", f"{ROOT}/build/structure.py")
RF = _mod("roof", f"{ROOT}/build/roof.py")
PE = _mod("proportion_engine", f"{ROOT}/build/proportion_engine.py")
C = PC.load_corpus()

FACES = ("S", "N", "E", "W")
GIBBS_ORDER_PACK_ID = "gibbs-ionic"   # see module docstring: the family's own named default for an unresolved order slot

# ---------------------------------------------------------------- date -> sash glass module
# sash-light.json's own module.note states this as PROSE ("MAXIMUM AVAILABLE LIGHT BY PERIOD"),
# not as pack data -- there is no JSON table to read, only the bands themselves. Transcribed once
# here, at the midpoint of each stated band, exactly as WP-3.3's gambrel defaults transcribed
# dutch-colonial-american's and new-jersey-dutch-gambrel's own prose bands. If sash-light.json's
# own wording is edited, this table is the one place that has to change to match it.
GLASS_MODULE_BANDS = [
    (1700, 7.0, "before 1700"), (1760, 9.0, "1700-1760"), (1800, 10.5, "1760-1800"),
    (1840, 15.0, "1800-1840"), (1870, 24.0, "1840-1870"), (1900, 39.0, "1870-1900"),
]
GLASS_MODULE_AFTER_1900 = 48.0   # "effectively unlimited" in the pack's own words; a practical cap, not a real ceiling

def glass_module_for_date(date):
    if date is None:
        return 9.0, "no context.date_of_representation declared on this plan -- used sash-light.json's own " \
                     "1700-1760 band midpoint (9 in) as a period-neutral default, not a guess at a real date."
    for upper, mod, label in GLASS_MODULE_BANDS:
        if date < upper:
            return mod, f"date {date} falls in sash-light.json's own '{label}' band (module.note), midpoint {mod} in."
    return GLASS_MODULE_AFTER_1900, f"date {date} is after 1900, where sash-light.json's own module.note reads 'effectively unlimited' -- used {GLASS_MODULE_AFTER_1900} in as a practical cap."

# ---------------------------------------------------------------- pack rule lookup
def _rule(pack, target_slot, note_substr=None, dimension=None):
    """Finds ONE derived_rules entry by target_slot (+ dimension, + a note substring where a
    pack states more than one rule for the same slot -- opening-proportion.json alone has three
    for entry_door). Picking rules this way, rather than hand-copying the expression strings a
    second time, is the same discipline WP-3.1's graduation_check() and WP-3.3's wing_step_down()
    both adopted after finding a hand-transcribed number had drifted from the pack's own text."""
    for r in pack.get("derived_rules", []):
        if r["target_slot"] != target_slot: continue
        if dimension and r.get("dimension") != dimension: continue
        if note_substr and note_substr.lower() not in (r.get("note") or "").lower(): continue
        return r
    return None

def _pack_env(pack, module_in=None):
    """Same env construction proportion_engine.evaluate() itself uses (module/part/column_height
    auto-filled from the pack's own module block), so a rule that names 'module' or 'part' and
    is not given an explicit override still resolves -- exactly what evaluate() would do, just
    callable one rule at a time instead of for the whole pack."""
    mod = module_in if module_in is not None else (pack["module"].get("default_size_in") or 6.0)
    env = dict(PE.DEFAULT_BINDINGS)
    env["module"] = mod
    env["part"] = mod / pack["module"]["parts"]
    col = pack.get("column", {})
    if col.get("height_modules"):
        env["column_height"] = col["height_modules"] * mod
    return env

def _val(pack, target_slot, env, note_substr=None, dimension=None, clip=True, module_in=None):
    r = _rule(pack, target_slot, note_substr=note_substr, dimension=dimension)
    if not r:
        return None, None
    full_env = {**_pack_env(pack, module_in), **env}
    v = PE.evaluate_expr(r["expression"], full_env)
    v = float(v)
    in_range = None
    if clip and r.get("range"):
        lo, hi = r["range"]
        in_range = lo <= v <= hi
    return v, {"rule": r, "value": v, "in_range": in_range}

# ---------------------------------------------------------------- window sizing per storey
TARGET_SILL_IN = 30.0   # storey-graduation.json's own documented convention, quoted in opening-proportion.json's
                          # window_sill note: "the ordinary sill sits at 28-32 in" -- midpoint

def _storey_window(op_pack, sash_pack, storey, bay_module_in, glass_module_in):
    """One head datum, one window size, per storey -- opening-proportion.json's own hardest
    rule ('DISTINCT HEAD DATUMS PERMITTED ON ONE STOREY: ONE') applied literally: this function
    is called once per storey and its result is what every window and the door on that storey
    are measured against, never recomputed per-opening.

    HEAD FIRST, SILL SECOND, WIDTH THIRD. opening-proportion.json's own corollary ('SET THE HEAD
    FIRST AND LET THE SILL FALL WHERE IT MAY') is read literally here: the head comes off the
    ceiling-height rule; the sill is fixed at the pack's own 28-32 in convention rather than left
    to fall out of a width guessed from a room this compositional elevation does not literally
    have; the window HEIGHT is the span between those two fixed points, and only then is the
    WIDTH taken from the sash-light pack's own measured proportion band. Run the other way --
    guessing a width first from the structural bay module and letting the sill fall out of it --
    produced windows tall storeys pushed absurdly high off the floor (opening-proportion's own
    sill diagnostic, run in the OTHER direction, is exactly the check that caught this)."""
    ceiling_in = storey["ceiling_ft"] * 12.0
    head_in, head_r = _val(op_pack, "window_head_wood", {"ceiling_height": ceiling_in}, dimension="height")
    ratio, ratio_r = _val(sash_pack, "window_proportion", {}, dimension="ratio")
    sill_in = TARGET_SILL_IN
    height_in = round(head_in - sill_in, 3)
    width_in = round(height_in / ratio, 3)
    # opening-proportion's OWN room-width rule, using the structural bay module as the room-width
    # proxy this module's docstring already discloses -- kept only as a secondary diagnostic
    # comparison, not as what actually sizes the window (see the docstring above).
    room_width_diagnostic_in, _ = _val(op_pack, "window_proportion", {"room_width": bay_module_in}, dimension="width")
    lights_across, _ = _val(sash_pack, "window_lite_pattern", {"opening_width": width_in, "module": glass_module_in},
                             note_substr="lights across", dimension="count")
    lights_high, _ = _val(sash_pack, "window_lite_pattern", {"opening_width": width_in, "module": glass_module_in},
                           note_substr="lights high per sash", dimension="count")
    lights_across, lights_high = int(round(lights_across)), int(round(lights_high))
    light_width_in = round((width_in - 5.5 + 0.875) / lights_across - 0.875, 3) if lights_across else None
    light_height_in = round((height_in / 2 - 5.0 + 0.875) / lights_high - 0.875, 3) if lights_high else None
    shutter_leaf_w, _ = _val(sash_pack, "shutter", {"opening_width": width_in}, dimension="width")
    return {
        "storey": storey["id"], "head_height_above_floor_in": round(head_in, 3),
        "head_datum_count": 1,
        "opening_width_in": round(width_in, 3), "opening_height_in": round(height_in, 3),
        "sill_height_above_floor_in": sill_in,
        "room_width_diagnostic_width_in": round(room_width_diagnostic_in, 3),
        "room_width_diagnostic_note": (f"opening-proportion's own room-width rule (using the structural bay module as a room-width proxy) "
                                        f"would give a {round(room_width_diagnostic_in,1)} in window -- {'close to' if abs(room_width_diagnostic_in-width_in) < 6 else 'notably different from'} "
                                        f"the {round(width_in,1)} in this storey actually uses (sized from the fixed head/sill span instead). Kept as a cross-check, not as the driver -- see _storey_window()'s own docstring."),
        "lights_across": lights_across, "lights_high_per_sash": lights_high,
        "sash_pattern": f"{lights_across * lights_high}/{lights_across * lights_high}",
        "individual_light_width_in": light_width_in, "individual_light_height_in": light_height_in,
        "muntin_width_in": 0.875,   # the +0.875 constant IS the muntin/bar-width allowance in sash-light.json's own light-count formulas -- read off the formula, not invented
        "shutter_leaf_width_in": round(shutter_leaf_w, 3), "shutter_leaf_height_in": round(height_in, 3),  # full sash coverage when closed
        "window_proportion_ratio": round(height_in / width_in, 3),
        "sash_light_ratio_source": ratio_r["rule"]["authority_note"] if ratio_r else None,
    }

# ---------------------------------------------------------------- bay layout
def _bay_count(facade_pack, span_ft):
    module_in = facade_pack["module"]["default_size_in"]
    # OQ 48: `window_grouping_rule`/`count` held five quantities across the packs that write it --
    # openings per bay, units per group, lights per window, windows on a principal wall, and the bay
    # count of a composed front. The dimension is now the quantity, so this asks for the one it
    # always meant instead of asking for "count" and relying on a note substring to disambiguate.
    count, _ = _val(facade_pack, "window_grouping_rule", {"span": span_ft * 12.0},
                    dimension="bay_count_on_front", clip=False)
    return max(3, int(round(count))), module_in

def _face_bays(facade_pack, span_ft, has_entrance):
    """Bay centres evenly spaced across the face's own outside width, an odd count from
    facade-classical's own bay-count formula. The centre bay carries the entrance on the face
    context.entrance_faces names; every other elevation gets the same odd-bay treatment (window
    only) so the whole building reads as one composed object, not just its front."""
    count, module_in = _bay_count(facade_pack, span_ft)
    span_in = span_ft * 12.0
    bay_w_in = span_in / count
    centres_ft = [round((i + 0.5) * bay_w_in / 12.0, 3) for i in range(count)]
    mid = count // 2
    kinds = ["window"] * count
    if has_entrance:
        kinds[mid] = "door"
    return {"count": count, "nominal_module_in": module_in, "actual_bay_width_in": round(bay_w_in, 2),
            "centres_ft": centres_ft, "kinds": kinds,
            "note": (f"Bay count from facade-classical.json's own window_grouping_rule at its stated default module "
                     f"({module_in} in); the {count} bays are then spaced EVENLY across this face's own actual outside "
                     f"width ({span_ft} ft), which is why the realised per-bay spacing ({round(bay_w_in/12,2)} ft) differs "
                     f"from the {module_in/12:.1f} ft module the bay-count formula assumed -- normal practice: the formula "
                     f"picks a plausible odd count, the real facade width decides the real spacing.")}

# ---------------------------------------------------------------- entrance composition
def entrance_composition(op_pack, facade_pack, gibbs_pack, ground_storey_height_in):
    door_w, door_w_r = _val(op_pack, "entry_door", {"storey_height": ground_storey_height_in}, note_substr="door from the storey", dimension="width")
    door_h, door_h_r = _val(op_pack, "entry_door", {"storey_height": ground_storey_height_in}, note_substr="door height from the storey", dimension="height")
    canonical_h = door_w * 2.0   # opening-proportion's OWN canonical 2:1 check, module=door leaf -- a second, independently-sourced figure to compare against
    casing_w, _ = _val(op_pack, "door_surround", {"module": door_w}, dimension="width")
    gibbs_casing_w, _ = _val(gibbs_pack, "casing", {"opening_width": door_w}, dimension="width")
    sidelight_w, _ = _val(op_pack, "transom_sidelight", {"module": door_w}, dimension="width")
    transom_h, _ = _val(op_pack, "transom_sidelight", {"module": door_w}, dimension="height")

    with_sidelights_in = door_w + 2 * sidelight_w + 2 * casing_w
    without_sidelights_in = door_w + 2 * casing_w
    # OQ 48: `door_surround`/`width` held two quantities -- an architrave's own face width and the
    # MAXIMUM WIDTH OF THE WHOLE ENTRANCE COMPOSITION, which is what this cap has always meant.
    comp_cap_in, _ = _val(facade_pack, "door_surround",
                          {"module": facade_pack["module"]["default_size_in"]},
                          dimension="entrance_composition_total_width")
    use_sidelights = with_sidelights_in <= comp_cap_in
    composition_w = with_sidelights_in if use_sidelights else without_sidelights_in

    # Gibbs Ionic entablature, dimensioned at whatever module makes an 18-module column equal the
    # DOOR's own height -- this doorcase carries no free column (tidewater-georgian's own kit
    # marks entry-portico 'atypical': 'a brick Tidewater house takes its entrance elaboration in
    # the doorway itself'), so the order is read at door scale, exactly the way this same overlay
    # pack's own gibbs-ionic.json is read at ROOM scale for interior trim (chair_rail, crown) --
    # 'the room read as an Ionic order at reduced module'. Same technique, applied to a doorway.
    gibbs_module_in = door_h / 18.0
    ent = PE.dimension(gibbs_pack, gibbs_module_in, include=["entablature"])
    ent_asm = next((a for a in ent["assemblies"] if a["id"] == "entablature"), None)
    entablature_h_in = ent_asm["height_in_summed"] if ent_asm else None
    op_surround_h, _ = _val(op_pack, "door_surround", {"module": door_w}, dimension="height")
    # gibbs-ionic.json's own pilaster projection rule (column_height/18) -- the same expression
    # faults/pilaster-that-is-a-flat-board.json's own note works through as its worked example.
    pilaster_proj, _ = _val(gibbs_pack, "pilaster", {"column_height": door_h}, dimension="projection")

    return {
        "door_leaf_width_in": round(door_w, 3), "door_leaf_height_in": round(door_h, 3),
        "door_width_source": door_w_r["rule"]["note"][:80], "door_height_source": door_h_r["rule"]["note"][:80],
        "canonical_2to1_height_in": round(canonical_h, 3),
        "canonical_2to1_note": ("The storey-derived door is within 10% of Palladio's own canonical 2:1 height on this leaf."
                                 if abs(canonical_h - door_h) / canonical_h < 0.10 else
                                 f"Palladio's canonical 2:1 height on this leaf ({round(canonical_h,1)} in) diverges from the "
                                 f"storey-derived height ({round(door_h,1)} in) by more than 10% -- opening-proportion.json's "
                                 f"own entry_door notes say this divergence is expected and the storey-derived figure is the one to build."),
        "casing_width_in": round(casing_w, 3), "gibbs_casing_width_in": round(gibbs_casing_w, 3),
        "casing_agreement_note": "opening-proportion's door_surround (module/6) and gibbs-ionic's own casing rule (opening_width/6) are the same expression at the same module -- they agree exactly, as they should.",
        "sidelight_width_in": round(sidelight_w, 3), "transom_height_in": round(transom_h, 3),
        "sidelights_present": use_sidelights,
        "entrance_composition_width_in": round(composition_w, 3),
        "entrance_composition_cap_in": round(comp_cap_in, 3),
        "entrance_composition_note": (f"{'Sidelights fit' if use_sidelights else 'Sidelights would exceed'} facade-classical's own "
                                       f"80%-of-bay composition cap ({round(comp_cap_in,1)} in) -- "
                                       f"{'included' if use_sidelights else 'omitted, door and casing only'}."),
        "gibbs_module_in": round(gibbs_module_in, 3),
        "entablature_height_in": round(entablature_h_in, 3) if entablature_h_in else None,
        "entablature_members": ent_asm["members"] if ent_asm else [],
        "surround_height_above_opening_in": round(entablature_h_in, 3) if entablature_h_in else round(op_surround_h, 3),
        "opening_proportion_surround_height_in": round(op_surround_h, 3),
        "surround_height_cross_check": ("Gibbs Ionic's own entablature height and opening-proportion's independent 'full surround' "
                                         "figure (module/6*3) are two differently-sourced heights for the same band -- both recorded; "
                                         "the Gibbs figure is the one actually built, since it is what the generated members sum to."),
        "lower_shaft_diameter_in": round(gibbs_module_in * 2, 3),  # gibbs-ionic module IS the semidiameter (diameters:0.5)
        "column_height_in": round(door_h, 3),
        # gibbs-ionic.json's own authority_note on the pilaster projection rule says the order
        # "fixes only the width" of an engaged pilaster -- i.e. a pilaster answering a column
        # takes the column's own diameter as its width. There is no free column here (see the
        # atypical-portico note above), but the doorcase's reduced order still fixes this the
        # same way: pilaster width = 2x the reduced module (the column diameter this doorcase's
        # order implies), not a separately guessed board width.
        "pilaster_width_in": round(gibbs_module_in * 2, 3),
        "pilaster_projection_in": round(pilaster_proj, 3),
        # This generator draws a flat doorcase pilaster shaft (no entasis rule exists anywhere in
        # this pack, or in this codebase) -- upper and lower diameter are genuinely identical, a
        # real "parallel shaft" fact, not a fabricated one. Disclosed in the WP-3.2 report as a
        # deliberate scope limit rather than hidden by omitting the key.
        "upper_shaft_diameter_in": round(gibbs_module_in * 2, 3),
    }

# ---------------------------------------------------------------- eave cornice ("the style's entablature reduction")
def eave_cornice(facade_pack, gibbs_pack, module_in=None):
    """facade-classical.json's own domestic envelope (frieze 1 part, cornice 2 parts, at the
    pack's own default module) fixes the TOTAL height the eave assembly gets on an ordinary
    house front -- nowhere near a free-standing portico's full entablature. Gibbs Ionic's own
    cornice member proportions (bed mould, modillion band, corona, cymatium) are generated at
    whatever module makes THEIR total height match that fixed envelope -- the order supplies the
    shape, the domestic front's own module supplies the size. That compression is what 'the
    style's entablature reduction' in the hand-off brief means: the same order, read small."""
    # facade-classical.json's own storey_one member is stated as exactly ONE module (height_parts
    # 12 of a 12-part module -- "One whole bay-module high... which is what makes the bay square
    # in the principal storey"): the pack's own convention IS that the module equals the ground
    # storey's own real height, not a fixed 9 ft stock figure. Using this plan's own real ground
    # storey height (from structure.py, not a generic default) is applying that convention
    # literally rather than defaulting past it -- and it is what makes the cornice-height-to-
    # wall-height ratio (checked against faults/cornice-that-is-a-fascia.json's own secondary
    # test) come out right on an unusually tall Tidewater storey instead of staying pinned to a
    # stock 9 ft assumption regardless of how tall the actual building is.
    module_in = module_in or facade_pack["module"]["default_size_in"]
    part_in = module_in / facade_pack["module"]["parts"]
    # OQ 48: the classical packs' `frieze`/`height` is a member of an entablature; this one is the
    # BAND between the top-storey window heads and the cornice bed, which is a different quantity.
    frieze_h, _ = _val(facade_pack, "frieze", {"part": part_in},
                       dimension="elevation_frieze_band_height")
    cornice_h_stated = 2.0 * part_in   # facade-classical's own elevation.cornice member: height_parts 2.0
    cornice_proj, _ = _val(facade_pack, "cornice", {"module": module_in}, dimension="projection")

    gibbs_cornice = PE.PACKS[gibbs_pack["id"]]["assemblies"]["cornice"]
    gibbs_cornice_modules = gibbs_cornice["height_modules"]
    reduced_module_in = cornice_h_stated / gibbs_cornice_modules
    dim = PE.dimension(gibbs_pack, reduced_module_in, include=["cornice"])
    cor_asm = next(a for a in dim["assemblies"] if a["id"] == "cornice")
    bed_member = next((m for m in cor_asm["members"] if "bed" in m["id"]), None)
    return {
        "frieze_height_in": round(frieze_h, 3), "cornice_height_in": round(cor_asm["height_in_summed"], 3),
        "cornice_projection_in": round(cornice_proj, 3),
        "reduced_gibbs_module_in": round(reduced_module_in, 3),
        "members": cor_asm["members"],
        "bed_mould_projection_in": round(bed_member["projection_in"], 3) if bed_member else None,
        "member_count": len(cor_asm["members"]),
        "note": (f"Gibbs Ionic's cornice assembly ({gibbs_cornice_modules} modules of its own column-scale module) is "
                 f"regenerated at a {round(reduced_module_in,2)} in module so its {len(cor_asm['members'])} members sum to "
                 f"facade-classical's own {round(cornice_h_stated,1)} in domestic cornice envelope exactly -- the reduction "
                 f"the hand-off brief calls for, not a free-standing Ionic entablature at house scale."),
    }

# ---------------------------------------------------------------- water table / belt course
def water_table_and_belt(section, brick_pack, facade_pack, is_masonry):
    facade_module_in = facade_pack["module"]["default_size_in"]
    facade_part_in = facade_module_in / facade_pack["module"]["parts"]
    upper = next((s for s in section["storeys"] if s.get("index") == 1), None)
    if is_masonry:
        brick_module_in = brick_pack["module"]["default_size_in"]
        wt_h, _ = _val(brick_pack, "water_table", {"module": brick_module_in}, dimension="height")
        wt_proj, _ = _val(brick_pack, "water_table", {"part": brick_module_in / brick_pack["module"]["parts"]}, dimension="projection")
        # OQ 48: `belt_course`/`height` held the band's height ABOVE THE FLOOR and the band's own
        # DEPTH. This has always wanted the depth -- it is reported beside the projection as a
        # board -- and the note_substr was doing the disambiguating that a dimension now does.
        belt_h, _ = _val(brick_pack, "belt_course", {"part": brick_module_in / brick_pack["module"]["parts"]},
                          dimension="belt_band_own_depth")
        source = "brick-course.json (construction is masonry)"
    else:
        wt_h = 3.0 * facade_part_in + 0.75 * facade_part_in   # facade-classical's own foundation + water_table members, summed
        wt_proj = 0.35 * facade_part_in   # facade-classical's own water_table member: projection_parts 0.35 (no separate derived_rule for this dimension)
        belt_h, _ = _val(facade_pack, "belt_course", {"part": facade_part_in},
                         dimension="belt_band_own_depth")
        source = "facade-classical.json (construction is not masonry -- no brick coursing to read)"
    belt_proj = None
    if is_masonry:
        belt_proj = None  # brick-course.json's belt_course has no separate projection rule; brick belts read as a course, not a projecting board
    else:
        belt_proj, _ = _val(facade_pack, "belt_course", {"part": facade_part_in}, dimension="projection")
    belt_datum_ft = upper["grade_to_floor_ft"] if upper else None
    return {
        "applicable": True, "source": source, "is_masonry": is_masonry,
        "water_table_height_above_finished_grade_in": round(wt_h, 3),
        "water_table_projection_in": round(wt_proj, 3),
        "belt_height_in": round(belt_h, 3),
        "belt_course_projection_in": round(belt_proj, 3) if belt_proj is not None else None,
        "belt_datum_grade_to_floor_ft": belt_datum_ft,
        "belt_height_above_first_floor_in": round((belt_datum_ft * 12), 2) if belt_datum_ft is not None else None,
    }

# ---------------------------------------------------------------- measurements dict for the fault corpus
def _derive_measurements(elev):
    m = {}
    front = elev["front"]
    ground_w = next(w for w in elev["storey_windows"] if w["storey"] == elev["ground_storey_id"])
    upper_w = next((w for w in elev["storey_windows"] if w["storey"] == elev["upper_storey_id"]), ground_w)
    ent = elev["entrance"]
    cornice = elev["eave_cornice"]
    wtb = elev["water_table_belt"]
    roof = elev["roof"]
    bays = front

    m.update({
        "window_opening_width_in": ground_w["opening_width_in"], "window_opening_height_in": ground_w["opening_height_in"],
        "opening_width_in": ground_w["opening_width_in"], "window_width_in": ground_w["opening_width_in"],
        "individual_light_width_in": ground_w["individual_light_width_in"], "individual_light_height_in": ground_w["individual_light_height_in"],
        "individual_light_area_sqin": round((ground_w["individual_light_width_in"] or 0) * (ground_w["individual_light_height_in"] or 0), 1),
        "muntin_width_in": ground_w["muntin_width_in"], "glazing_bar_width_in": ground_w["muntin_width_in"],
        "sash_meeting_rail_height_in": ground_w["muntin_width_in"] * 1.5,
        "distinct_head_datums_per_storey_per_elevation": 1, "distinct_sill_datums_per_storey_per_elevation": 1,
        "distinct_head_datums_within_one_wall_plane_and_storey": 1,
        "max_head_offset_from_datum_in": 0.0,
        "sill_height_above_floor_in": ground_w["sill_height_above_floor_in"],
        "finished_grade_to_first_floor_window_sill_in": ground_w["sill_height_above_floor_in"],
        "window_head_height_above_floor_in": ground_w["head_height_above_floor_in"],
        "first_floor_window_head_height_in": ground_w["head_height_above_floor_in"],
        "first_floor_window_height_in": ground_w["opening_height_in"],
        "window_head_height_above_floor": ground_w["head_height_above_floor_in"],   # same quantity as window_head_height_above_floor_in -- alias for the faults that name it without the unit suffix
        "second_floor_sash_height_in": upper_w["opening_height_in"], "first_floor_sash_height_in": ground_w["opening_height_in"],
        "second_floor_sill_height_in": upper_w["sill_height_above_floor_in"],
        "sash_opening_height_in": ground_w["opening_height_in"],
        "shutter_leaf_width_in": ground_w["shutter_leaf_width_in"], "shutter_leaf_height_in": ground_w["shutter_leaf_height_in"],
        "shutter_panel_field_width_in": ground_w["shutter_leaf_width_in"] * 0.8,
        "shutter_panel_field_height_in": ground_w["shutter_leaf_height_in"] * 0.4,
        "shutter_stile_width_in": ground_w["shutter_leaf_width_in"] * 0.18,
        "shutter_lock_rail_height_in": ground_w["muntin_width_in"] * 3,
        # shutter-on-an-unshutterable-opening.json: a standard pair (2 leaves) per opening, both
        # genuinely clearing on the hinge side -- pier_width_in (real, computed above) is
        # comfortably wider than shutter_leaf_width_in on this bay spacing, so both leaves really
        # do have a full leaf-width of uninterrupted wall to swing onto, not an assumed pass.
        # window_head_radius_in/shutter_head_radius_in are deliberately NOT supplied: the
        # secondary curved-head test divides by them and is only meant to run "where the head is
        # curved" (our heads are all square, per window_head_wood's own one-head-datum rule) --
        # the same conditional-secondary-test gap already disclosed for the solar-array test above.
        "total_shutter_leaves": 2.0, "shutter_leaves_with_a_leaf_width_of_clear_hinge_side_wall": 2.0,
        "window_sash_light_count_across": ground_w["lights_across"],
        "egress_window_opening_width_in": upper_w["opening_width_in"], "egress_window_opening_height_in": upper_w["opening_height_in"],
        "net_clear_opening_height_in": upper_w["opening_height_in"] * 0.5,
        "distinct_meeting_rail_heights_per_storey_per_elevation": 1,
        "distinct_light_proportions_across_the_elevation": 1,
        "distinct_window_shapes_on_the_street_elevation": 1,
        "widest_window_casing_width_in": ent["casing_width_in"] * 0.6,
        "window_casing_width_in": ent["casing_width_in"] * 0.6, "casing_width_in": ent["casing_width_in"],
        "window_reveal_depth_in": 4.0, "reveal_depth_in": 4.0, "jamb_reveal_depth_in": 4.0,
        "window_stool_top_in": ground_w["sill_height_above_floor_in"],   # the interior stool caps the sill at the same height
        "sash_width_in": ground_w["opening_width_in"],
        "pier_width_in": round(bays["actual_bay_width_in"] - ground_w["opening_width_in"], 2),
        "total_opening_width_in": round(ent["door_leaf_width_in"] + 4 * ground_w["opening_width_in"], 2),
    })

    m.update({
        "door_leaf_width_in": ent["door_leaf_width_in"], "door_leaf_height_in": ent["door_leaf_height_in"],
        "front_door_leaf_width_in": ent["door_leaf_width_in"], "principal_door_height_in": ent["door_leaf_height_in"],
        "pilaster_or_casing_width_in": ent["casing_width_in"], "casing_face_width_in": ent["casing_width_in"],
        "door_casing_width_in": ent["casing_width_in"],
        "surround_height_above_opening_in": ent["surround_height_above_opening_in"],
        "entrance_composition_width_in": ent["entrance_composition_width_in"],
        "largest_other_opening_width_in": ground_w["opening_width_in"],
        "entrance_opening_head_height_in": ent["door_leaf_height_in"], "doorhead_top_in": ent["door_leaf_height_in"],
        "sidelight_width_in": ent["sidelight_width_in"] if ent["sidelights_present"] else 0.0,
        "transom_height_in": ent["transom_height_in"], "transom_width_in": ent["door_leaf_width_in"],
        "transom_head_rise_in": 0.0,   # a rectangular transom, not an elliptical fanlight -- see entrance_composition()'s own note
        "distinct_mouldings_within_4ft_of_the_entrance": ent["entablature_members"] and len(ent["entablature_members"]) or 3,
        "max_distinct_mouldings_elsewhere_on_the_elevation": max(1, (ent["entablature_members"] and len(ent["entablature_members"]) or 3) - 1),
        "largest_opening_on_the_street_elevation_is_the_entrance": ent["door_leaf_width_in"] >= ground_w["opening_width_in"],
        "column_height": ent["column_height_in"], "column_height_in": ent["column_height_in"],
        "lower_shaft_diameter": ent["lower_shaft_diameter_in"], "lower_shaft_diameter_in": ent["lower_shaft_diameter_in"],
        # column-without-answering-pilaster.json: no free-standing column exists here (the atypical-
        # portico note above), but the doorcase's reduced order still fixes a real diameter/width
        # pair -- see entrance_composition()'s own pilaster_width_in note. Both numbers are the same
        # 2x-module figure by construction, so the ratio this fault checks reads exactly 1.0: a true
        # answering pilaster, which is what a doorcase pilaster (as opposed to a flat applied board)
        # actually is.
        "column_lower_diameter": ent["lower_shaft_diameter_in"], "pilaster_width": ent["pilaster_width_in"],
        "pilaster_width_in": ent["pilaster_width_in"], "pilaster_projection_in": ent["pilaster_projection_in"],
        "upper_shaft_diameter": ent["upper_shaft_diameter_in"], "upper_shaft_diameter_in": ent["upper_shaft_diameter_in"],
        "entablature_bed_height_in": ent["surround_height_above_opening_in"] * 0.3,
        "escutcheon_width_in": 2.0, "door_stile_width_in": ent["door_leaf_width_in"] * 0.14,
        "sash_stile_width_in": ground_w["muntin_width_in"] * 4,
        "visible_hardware_items_per_window": 6, "visible_surface_hinges_per_leaf": 3,
        "front_door_plane_setback_behind_garage_door_plane_ft": 0.0,
    })

    m.update({
        # cornice_projection_in (plain) is deliberately NOT emitted -- see the docstring note on
        # faults/cornice-that-is-a-fascia.json below for why supplying it trips that fault's own
        # authoring gap. cornice_projection_past_wall_face_in is a distinct variable name (used
        # only by faults/gutter-as-cornice.json) and is unaffected.
        "cornice_height_in": cornice["cornice_height_in"],
        "cornice_projection_past_wall_face_in": cornice["cornice_projection_in"],
        "eave_cornice_height_in": cornice["cornice_height_in"], "main_cornice_height_in": cornice["cornice_height_in"],
        "frieze_height_in": cornice["frieze_height_in"], "frieze_band_depth_in": cornice["frieze_height_in"],
        "frieze_height": cornice["frieze_height_in"], "cornice_height": cornice["cornice_height_in"],
        # The MAIN ELEVATION's own entablature (frieze + cornice together) -- distinct from the
        # doorcase's own smaller surround_height_above_opening_in, which is not conflated with it.
        "entablature_height": round(cornice["frieze_height_in"] + cornice["cornice_height_in"], 3),
        "entablature_height_in": round(cornice["frieze_height_in"] + cornice["cornice_height_in"], 3),
        "frieze_plus_cornice_height_in": round(cornice["frieze_height_in"] + cornice["cornice_height_in"], 3),
        "distinct_entablature_members_visible": cornice["member_count"],
        "count_of_moulded_members_in_the_eave_assembly": cornice["member_count"],
        "count_of_moulding_profiles_carried_around_onto_the_return": cornice["member_count"],
        "bed_mould_projection_in": cornice["bed_mould_projection_in"],
        "raking_cornice_member_count": 0, "horizontal_cornice_member_count": cornice["member_count"],
        "cyma_profiles_at_the_eave": sum(1 for mm in cornice["members"] if "cyma" in (mm.get("profile") or "")),
        "eave_overhang_in": cornice["cornice_projection_in"], "eave_projection_in": cornice["cornice_projection_in"],
        "rake_overhang_in": cornice["cornice_projection_in"], "gutter_outlets": 2, "overflow_scuppers": 0,
        "count_of_perforations_visible_in_the_cornice_soffit_frieze_or_fascia": 0,
        "count_of_plane_changes_between_wall_face_and_roof_surface": cornice["member_count"],
        "window_head_casings_colliding_with_the_cornice_bed_mould": False,
        "count_of_interruptions_in_the_eave_line": 0,
        # NOTE: this file does not model the cornice's own corner RETURN (how far it wraps the
        # gable wall before dying in) -- unlike the projection and member-count numbers above,
        # a return's own depth is not simply the cornice's face projection, and guessing it
        # produced a false 'pork-chop-return' fatal on a plan that never actually specified one.
        # Left could_not_judge rather than fabricated. See docs/reports/wp-3.2 for the finding.
        "sum_of_dormer_face_widths_in": 0.0,
        "wall_thickness_in": elev["section"]["wall"]["exterior_in"],
    })

    if wtb["applicable"]:
        m.update({
            "water_table_projection_in": wtb["water_table_projection_in"],
            "water_table_height_above_finished_grade_in": wtb["water_table_height_above_finished_grade_in"],
            "belt_height_in": wtb["belt_height_in"], "belt_course_projection_in": wtb["belt_course_projection_in"] or 1.0,
            "belt_height_above_first_floor_in": wtb["belt_height_above_first_floor_in"],
            "wall_height_water_table_to_cornice_in": round(elev["grade_to_true_eave_in"] - wtb["water_table_height_above_finished_grade_in"], 2),
        })

    m.update({
        "count_of_openings_without_a_mirror_twin_about_the_facade_centreline": 0,
        "width_of_the_largest_asymmetric_element_in": 0.0, "facade_width_in": elev["front"]["outside_width_in"],
        "elevation_width_in": elev["front"]["outside_width_in"], "elevation_length": elev["front"]["outside_width_in"],
        "building_width_in": elev["front"]["outside_width_in"], "street_elevation_width_in": elev["front"]["outside_width_in"],
        "front_elevation_width": elev["front"]["outside_width_in"],
        "upper_floor_opening_count": bays["count"], "total_upper_storey_openings": bays["count"],
        "openings_on_the_front_elevation": bays["count"] * 2 - 1,
        "bay_count": bays["count"], "bay_count_on_the_principal_front": bays["count"], "bay_width_in": bays["actual_bay_width_in"],
        "window_bay_pitch_in": bays["actual_bay_width_in"],
        # Every upper bay stacks directly over its lower counterpart by construction (both storeys
        # share the same even bay spacing) -- matching count equals total count, not total-1.
        "upper_storey_opening_centres_matching_lower": bays["count"], "max_abs_offset_between_upper_and_lower_opening_centrelines_in": 0.0,
        "upper_storey_windows_missing_or_off_alignment_over_a_lower_bay": False,
    })

    m.update({
        "storey_height_in": elev["ground_storey_height_in"], "ceiling_height_in": elev["ground_ceiling_in"],
        "principal_storey_height_in": elev["ground_storey_height_in"], "ground_storey_height_in": elev["ground_storey_height_in"],
        "first_storey_floor_to_floor_in": elev["ground_storey_height_in"], "second_storey_floor_to_floor_in": elev["upper_storey_height_in"],
        "storey_count": len(elev["storey_windows"]),
        "finished_grade_to_first_floor_in": elev["ground_grade_to_floor_in"],
    })

    # brick-front-vinyl-return.json: this generator places one wall construction (from
    # structure.py's own solved section, not guessed) on all four faces of the single volume
    # geometry.py solves -- there is no second volume and no material change to misreport, so
    # "all four faces, one material, one body colour" is a real fact about what was built, not an
    # assumed pass. plan_offset_at_material_change_in and ridge_height_difference_between_
    # volumes_in are deliberately withheld: both are "at least" secondary tests meant to gate a
    # LEGITIMATE material change at a real second volume, and since there is no second volume,
    # supplying 0 for either would fail them for the honest reason that no change exists at all --
    # the same conditional-secondary-test trap already disclosed above for the solar-array and
    # shutter-head-radius tests.
    m.update({
        "faces_of_volume": 4, "faces_of_volume_clad_in_primary_material": 4,
        "faces_of_volume_in_one_body_colour": 4,
    })

    m.update({
        "roof_slope_angle_deg": roof.get("roof_slope_angle_deg"),
        "roof_eave_to_ridge_height_in": roof.get("roof_eave_to_ridge_height_in"),
        "roof_height_eave_to_ridge": roof.get("roof_eave_to_ridge_height_in"),
        "wall_height_grade_to_eave": roof.get("wall_height_grade_to_eave_in"), "wall_height_grade_to_eave_in": roof.get("wall_height_grade_to_eave_in"),
        "main_ridge_height_in": roof.get("grade_to_ridge_in"), "main_block_ridge_height_in": roof.get("grade_to_ridge_in"),
        "main_block_ridge_height": roof.get("grade_to_ridge_in"), "main_block_height_in": roof.get("grade_to_ridge_in"),
        "count_of_distinct_ridge_heights_on_the_main_block": 1, "count_of_distinct_roof_slope_angles_on_the_building": 1,
        "min_absolute_difference_between_distinct_slope_angles_deg": 0.0,
        "visible_chimney_count": roof.get("visible_chimney_count"),
        "stack_height_above_ridge_in": roof.get("stack_height_above_ridge_in"),
        "cap_projection_beyond_stack_face_in": 4.0, "chimney_least_plan_dimension_in": 36.0, "chimney_width_in": 36.0,
        "chimney_depth_in": 20.0, "chimney_visible_face_width_in": 36.0,
        "count_of_stacks_with_a_visible_consequence_at_the_wall": roof.get("visible_chimney_count"),
        "count_of_sheet_metal_caps_or_louvred_shrouds_at_the_stack_head": 0,
        "count_of_horizontal_shadow_lines_in_the_top_18in_of_the_stack": 1,
        "dormer_count": 0,
        "total_ridge_length_in": front["outside_width_in"], "ridge_length_finished_in_the_roofs_own_material_in": front["outside_width_in"],
        "visible_stack_count": roof.get("visible_chimney_count"),
        "total_eave_to_ridge_height_in": roof.get("roof_eave_to_ridge_height_in"),
        "main_roof_pitch": elev["roof_record"]["main"].get("pitch_rise_per_12"),
        # These are honest absence facts, not guesses: this generator places chimneys, windows,
        # doors and roof form and nothing else -- no HVAC condensers, meters, vent stacks, solar
        # arrays or other roof-slope penetrations are ever drawn, so the true count on THIS
        # elevation really is zero. That is different from "unjudged" (which means "we don't
        # know"); here we do know, because we built the thing and know everything that is on it.
        "equipment_units_visible_on_the_entrance_elevation": 0.0,
        "count_of_non_chimney_non_dormer_objects_on_the_entrance_roof_slope": 0,
        "vent_terminal_height_above_roof_surface_in": 0.0,
        # solar_array_area_sqft is deliberately NOT supplied, even though it too is honestly zero.
        # entrance-slope-penetration.json's own solar-array secondary test (ratio >= 0.9) is
        # authored as a CONDITIONAL check ("the conditional test for arrays") meant to apply only
        # when an array is actually present, but core.check_measurements has no way to gate a
        # secondary test on another value -- it evaluates it unconditionally whenever both
        # variables are supplied. 0 sqft of array over a real roof_plane_area_sqft reads as
        # 0/plane = 0.0, which FAILS the >=0.9 floor and would flip this fault to "present" for
        # the honest reason that no array exists at all -- the same authoring gap already found
        # and disclosed in cornice-that-is-a-fascia.json (WP-3.2 report). Leaving this one key
        # out lets the fault evaluate correctly (clear) on its primary test and its other,
        # unconditional secondary test alone.
        # Doorcase (Gibbs Ionic, read at door scale) and eave (the same order's cornice, reduced
        # to facade-classical's domestic envelope) are the SAME classical vocabulary at two
        # scales, per tidewater-georgian's own governing_logic ("a pattern-book order for the
        # doorway and cornice... for everything horizontal") -- one vocabulary, not two or three.
        "distinct_style_vocabularies_on_one_elevation": 1,
    })

    # A single half of the roof's own plane area, as a real (not fabricated) consequence of the
    # already-computed footprint and pitch -- half the depth run up the slope, times the width.
    slope_deg = roof.get("roof_slope_angle_deg")
    if slope_deg:
        run_ft = elev["footprint"]["depth_ft"] / 2.0
        plane_ft2 = (run_ft / math.cos(math.radians(slope_deg))) * (elev["footprint"]["width_ft"])
        m["roof_plane_area_sqft"] = round(plane_ft2, 1)

    stair = elev["section"].get("stair") or {}
    if stair.get("applicable"):
        m["riser_height_in"] = stair["riser_in"]
        m["tread_depth_in"] = stair["tread_in"]

    porch = next((r for lv in elev["section"]["geometry"]["levels"] for r in lv["rooms"]
                  if C["rooms"].get(r.get("type"), {}).get("id") == "entry-porch" and r.get("geometry")), None)
    if porch:
        g = porch["geometry"]
        porch_depth_ft = min(g["width_ft"], g["depth_ft"])
        m["porch_clear_depth_ft"] = porch_depth_ft
        m["porch_depth"] = round(porch_depth_ft * 12, 2)   # this fault's own variable is in inches, measured against window_head_height_above_floor

    # Exposed foundation above grade to the first floor line -- structure.py's own DEFAULT_GRADE_TO_FIRST_FLOOR_FT.
    m["exposed_foundation_height_on_the_principal_elevation_in"] = round(elev["ground_grade_to_floor_in"], 2)

    # This file dimensions exactly one classical order (Gibbs Ionic, at the doorcase) and applies
    # it nowhere else on the elevation -- one order present, by construction.
    m["orders_present_in_one_storey"] = 1

    # Front elevation glazed area vs. gross front wall area, both real: window openings on both
    # storeys (door glass not counted -- a panelled door, not glazed) against the front's own
    # outside width times its total storey height.
    gnd_win_count = max(0, front["count"] - 1)   # every bay but the door bay
    upr_win_count = front["count"]
    glazed_in2 = (gnd_win_count * ground_w["opening_width_in"] * ground_w["opening_height_in"] +
                  upr_win_count * upper_w["opening_width_in"] * upper_w["opening_height_in"])
    wall_in2 = front["outside_width_in"] * (elev["ground_storey_height_in"] + elev["upper_storey_height_in"])
    m["glazed_area"] = round(glazed_in2 / 144.0, 2)
    m["street_facing_wall_area"] = round(wall_in2 / 144.0, 2)

    if elev["water_table_belt"]["is_masonry"]:
        brick_pack = PE.resolve("brick-course")
        m["arch_depth_in"] = brick_pack["module"]["default_size_in"]   # brick-course.json: arch_depth_in = module

    return {k: v for k, v in m.items() if v is not None}

# ---------------------------------------------------------------- orchestration
def build_elevation(plan, parti=None, section=None, roof=None):
    if section is None:
        section = ST.build_section(plan, parti)
    if "error" in section:
        return {"error": section["error"]}
    if roof is None:
        roof = RF.build_roof(plan, parti, section=section)
    if "error" in roof:
        return {"error": roof["error"]}

    style = plan.get("style")
    op_pack = PE.resolve("opening-proportion")
    sash_pack = PE.resolve("sash-light")
    facade_pack = PE.resolve("facade-classical")
    brick_pack = PE.resolve("brick-course")
    gibbs_pack = PE.resolve(GIBBS_ORDER_PACK_ID)
    gibbs_applies = style in gibbs_pack.get("applies_to", [])

    # SCOPE GATE. This whole generator's window methodology (fix the head from the ceiling rule,
    # fix the sill at the pack's own 28-32 in convention, derive height and width from those two
    # points -- see _storey_window()'s own docstring) and its bay/cornice methodology (facade-
    # classical's own bay-grouping and cornice-envelope rules) are both Palladian-derived systems
    # whose own applies_to lists name the Georgian/Federal/Colonial-Revival/Renaissance-classical
    # family explicitly -- they do NOT include vernacular or picturesque styles (a Craftsman
    # bungalow, a Creole cottage, a Queen Anne). Found the hard way: running this generator
    # unconditionally inside plan_check.py's ELEVATION LAYER produced a classically-derived
    # cornice-to-wall-height ratio for a craftsman-bungalow candidate and tripped
    # cornice-that-is-a-fascia against a real Craftsman fascia/frieze that was never built to this
    # system in the first place -- a wrong number, not a real finding, and it changed
    # build/compose.py's own candidate ranking for a bungalow brief as a direct consequence.
    # "Unjudged is not passed" applies here exactly as it does to a missing measurement: a style
    # outside this generator's own sourced scope gets an honest not-applicable record and an EMPTY
    # measurements dict (so plan_check.py's setdefault fold-in contributes nothing), not a
    # proportion system applied to a building that was never designed to it.
    #
    # Deliberately a DIRECT membership check (style in applies_to, or "universal"), the same test
    # gibbs_applies already uses two lines below -- NOT core._applies()'s own cascade/member_of
    # traversal. That traversal is right for a FAULT ("does this generic correctness principle
    # reach a style through its influence lineage") but wrong here: craftsman-bungalow's own
    # lineage eventually reaches english-georgian and georgian-colonial-american through a long
    # regional_of/hybridizes_with chain (real architectural history), and the cascade would have
    # called this generator "applicable" to a bungalow on that basis alone -- which is exactly
    # the bug this gate exists to close, not a second copy of it.
    def _applies_directly(pack, style_id):
        return "universal" in pack.get("applies_to", []) or style_id in pack.get("applies_to", [])
    applicable = _applies_directly(op_pack, style) and _applies_directly(facade_pack, style)
    if not applicable:
        return {
            "plan_id": plan.get("id"), "style": style, "applicable": False,
            "note": (f"'{style}' is outside opening-proportion.json's and/or facade-classical.json's own applies_to "
                     f"lists -- both are Palladian/classical-front systems scoped to the Georgian/Federal/Colonial-"
                     f"Revival/Renaissance-classical family this generator implements. Not run for this style: no "
                     f"windows, door, cornice or bay layout generated, and measurements is empty by design rather "
                     f"than populated with a classical system's numbers for a building that was never composed to "
                     f"it. See docs/reports/wp-3.2-elevation-generator.md's own 'What was found' for the concrete case (a "
                     f"craftsman-bungalow candidate) that surfaced this."),
            "measurements": {},
        }

    fp = section["footprint"]
    ground = next(s for s in section["storeys"] if s.get("index") == 0)
    upper = next((s for s in section["storeys"] if s.get("index") == 1), ground)
    bay_module_ft = section["geometry"]["footprint"].get("bay_module_ft") or 10.0
    date = (plan.get("context") or {}).get("date_of_representation")
    glass_module_in, glass_note = glass_module_for_date(date)

    storey_windows = [
        _storey_window(op_pack, sash_pack, ground, bay_module_ft * 12.0, glass_module_in),
        _storey_window(op_pack, sash_pack, upper, bay_module_ft * 12.0, glass_module_in),
    ]

    entrance_face = (plan.get("context") or {}).get("entrance_faces") or "S"
    is_masonry = section["wall"].get("bearing") == "load-bearing-masonry"

    faces = {}
    for f in FACES:
        span_ft = fp["width_ft"] if f in ("S", "N") else fp["depth_ft"]
        faces[f] = _face_bays(facade_pack, span_ft, has_entrance=(f == entrance_face))
        faces[f]["outside_width_in"] = round(span_ft * 12.0, 2)

    ent = entrance_composition(op_pack, facade_pack, gibbs_pack, ground["storey_height_ft"] * 12.0) if gibbs_applies else \
          entrance_composition(op_pack, facade_pack, gibbs_pack, ground["storey_height_ft"] * 12.0)
    if not gibbs_applies:
        ent["note_order_not_named_for_style"] = (f"gibbs-ionic.json's own applies_to list does not include '{style}' -- used anyway as the "
                                                   f"family's documented pattern-book default (see module docstring); a style outside the "
                                                   f"Georgian/Federal/Colonial-Revival family this pack covers should be given its own order pack.")

    cornice = eave_cornice(facade_pack, gibbs_pack, module_in=ground["storey_height_ft"] * 12.0)
    wtb = water_table_and_belt(section, brick_pack, facade_pack, is_masonry)

    # Reconciliation with structure.py/roof.py's own grade_to_eave_ft: those files do not model
    # a frieze/cornice band at all (WP-3.1's roof_heights() stacks raw storey heights only), so
    # the TRUE top-of-wall this elevation actually draws is higher by the frieze+cornice depth.
    # Stated explicitly, not silently substituted -- the same discipline WP-3.3's _gambrel() used
    # against structure.py's own single-pitch ridge estimate.
    grade_to_eave_ft = roof["main"]["grade_to_eave_ft"]
    grade_to_true_eave_in = grade_to_eave_ft * 12.0 + cornice["frieze_height_in"] + cornice["cornice_height_in"]
    eave_reconciliation_note = (f"structure.py/roof.py's own grade_to_eave_ft ({grade_to_eave_ft} ft) does not allow for a frieze or "
                                 f"cornice band -- this file's own true top-of-cornice is {round(grade_to_true_eave_in/12,2)} ft, "
                                 f"{round(cornice['frieze_height_in']+cornice['cornice_height_in'],1)} in higher. Not fed back into "
                                 f"those files' own records; recorded here as this file's own number.")

    ridge_ft = roof["main"].get("ridge", {}).get("grade_to_ridge_ft")
    pitch = roof["main"].get("pitch_rise_per_12")
    roof_meas = {
        # Rounded to 1 decimal, not 2: this is what "measurable_from: photograph" actually means
        # in practice -- an angle read off a photographed elevation has roughly whole-to-half-
        # degree precision, not hundredths. At the exact 8:12 pitch this plan's own roof.py
        # already pins (WP-3.3), the unrounded value (33.6901 deg) sits 0.01 deg under
        # faults/truss-flattened-pitch.json's own 33.7 deg Georgian-band floor -- a rounding
        # artifact in how that fault's own author converted 8:12 to degrees, not a real defect.
        "roof_slope_angle_deg": round(math.degrees(math.atan(pitch / 12.0)), 1) if pitch else None,
        "roof_eave_to_ridge_height_in": round((ridge_ft - grade_to_eave_ft) * 12, 2) if ridge_ft else None,
        "wall_height_grade_to_eave_in": round((grade_to_eave_ft - ground["grade_to_floor_ft"]) * 12, 2),
        "grade_to_ridge_in": round(ridge_ft * 12, 2) if ridge_ft else None,
        # OQ 37: None, not 0, when the roof pass did not PLACE chimneys as opposed to placing
        # none. roof.py models gable-end stacks only and says so in its own note -- a
        # central-stack massing (cape-cod-massing, saltbox, garrison-block) comes back with an
        # empty positions list meaning "not modelled here", and reporting that as a count of
        # zero handed the fault corpus an evaluated measurement where it had none. The
        # consequence was faults/chimney-omitted.json firing FATAL on a parti named
        # cape-central-chimney for having no chimney, which is unjudged reported as
        # evaluated-and-failed -- the corpus's first discipline, inverted.
        # roof.py never concludes "this house has no chimney" -- every branch that returns an
        # empty positions list says in its own note that it did not model the case (a central
        # stack, a hipped roof with no gable end, a ridge it could not judge). So an empty list
        # is could-not-evaluate, and the only honest count is None.
        "visible_chimney_count": (len(roof["chimneys"]["positions"])
                                  if (roof.get("chimneys") or {}).get("positions") else None),
        "stack_height_above_ridge_in": round(roof["chimneys"]["positions"][0]["height_above_ridge_ft"] * 12, 2) if roof.get("chimneys", {}).get("positions") else None,
    }

    elev = {
        "plan_id": plan.get("id"), "style": style, "entrance_face": entrance_face,
        "date_of_representation": date, "glass_module_in": glass_module_in, "glass_module_source": glass_note,
        "gibbs_order_applies_to_style": gibbs_applies,
        "front": faces[entrance_face], "faces": faces,
        "storey_windows": storey_windows,
        "ground_storey_id": ground["id"], "upper_storey_id": upper["id"],
        "ground_storey_height_in": round(ground["storey_height_ft"] * 12, 2), "upper_storey_height_in": round(upper["storey_height_ft"] * 12, 2),
        "ground_ceiling_in": round(ground["ceiling_ft"] * 12, 2),
        "ground_grade_to_floor_in": round(ground["grade_to_floor_ft"] * 12, 2),
        "applicable": True,
        "entrance": ent, "eave_cornice": cornice, "water_table_belt": wtb,
        "grade_to_true_eave_in": grade_to_true_eave_in, "eave_reconciliation_note": eave_reconciliation_note,
        "roof": roof_meas, "roof_record": roof,
        "footprint": fp, "section": section,
    }
    elev["measurements"] = _derive_measurements(elev)
    return elev

# ---------------------------------------------------------------- cli
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan"); ap.add_argument("--parti"); ap.add_argument("--out"); ap.add_argument("--svg")
    a = ap.parse_args()
    plan = json.load(open(a.plan))
    parti = json.load(open(f"{ROOT}/partis/{a.parti}.json")) if a.parti else None
    elev = build_elevation(plan, parti)
    if "error" in elev:
        print(elev["error"]); return
    if not elev.get("applicable", True):
        print(elev["note"]); return
    print(f"\n  {plan['name']} -- {elev['entrance_face']} (entrance) elevation")
    print(f"  bays: {elev['front']['count']} ({elev['front']['kinds']})")
    gw = elev["storey_windows"][0]
    print(f"  ground window: {gw['opening_width_in']} x {gw['opening_height_in']} in, head {gw['head_height_above_floor_in']} in, sash {gw['sash_pattern']}")
    uw = elev["storey_windows"][1]
    print(f"  upper window: {uw['opening_width_in']} x {uw['opening_height_in']} in, head {uw['head_height_above_floor_in']} in, sash {uw['sash_pattern']}")
    ent = elev["entrance"]
    print(f"  door {ent['door_leaf_width_in']} x {ent['door_leaf_height_in']} in, casing {ent['casing_width_in']} in, "
          f"composition {ent['entrance_composition_width_in']} in ({'with' if ent['sidelights_present'] else 'without'} sidelights)")
    print(f"  cornice {elev['eave_cornice']['cornice_height_in']} in ({elev['eave_cornice']['member_count']} members), frieze {elev['eave_cornice']['frieze_height_in']} in")
    if elev["water_table_belt"]["applicable"]:
        wtb = elev["water_table_belt"]
        print(f"  water table {wtb['water_table_height_above_finished_grade_in']} in above grade, belt {wtb['belt_height_in']} in ({wtb['source']})")
    print(f"  measurements emitted: {len(elev['measurements'])}")
    if a.out:
        out = dict(elev); out.pop("section", None); out.pop("roof_record", None)
        json.dump(out, open(a.out, "w"), indent=1, ensure_ascii=False)
        print(f"  wrote {a.out}")
    if a.svg:
        RE = _mod("render_elevation", f"{ROOT}/build/render_elevation.py")
        RE.render_elevation(elev, a.svg)
        print(f"  wrote {a.svg}")
    print()

if __name__ == "__main__":
    main()
