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
import json, os, math, re, argparse, importlib.util

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
RK = _mod("resolve_kit", f"{ROOT}/build/resolve_kit.py")
PROF = _mod("profiles", f"{ROOT}/build/profiles.py")
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
        # PANELS PER LEAF, from sash-light.json's own rule on `shutter/count`: "Panel count in a
        # panelled (raised-panel) shutter leaf, which follows the sash division roughly but not
        # exactly: a 12/12 window gets a two- or three-panel leaf, a 6/6 gets two." Hardcoded 4
        # until 27 Aug 2026, which no pack supports; Colonial Williamsburg's own reports on the
        # Prentis and John Blair shutters give three on the ground floor and two above, which is
        # what this rule produces at these light counts.
        # The boundary is the pack's own: a 6/6 gets two, a 12/12 gets "two or three". A 15-light
        # sash is larger than the 12/12 the pack tops out at, so it takes three; a 12/12 takes the
        # lower of its two, which is what puts three on the taller ground sash and two on the
        # shorter upper one -- the graduation Colonial Williamsburg records at the Prentis and
        # John Blair houses.
        "shutter_panel_count": (3 if (lights_high or 0) * (lights_across or 0) >= 15 else 2),
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

def blind_bays_behind_stacks(face_rec, stack_axes_ft, stack_width_ft):
    """Mark any bay whose centre a chimney stack stands on as `blind`, in place.

    OQ 85. `roof.py` puts this house's stacks at `y_ft` 21.33 on a gable end 42.66 ft deep -- its
    exact centre line -- and `_face_bays()` independently gives every face an odd bay count evenly
    spaced, which puts a window centre at 21.33 too. The two records were built from different
    rules and nothing compared them, so the elevation drew a window where a chimney stands. It was
    found by drawing the stack from grade for one revision, not by any test.

    Ruled 27 Aug 2026: THE CENTRE BAY IS BLIND. That is what a Chesapeake end wall usually is, and
    it holds whichever way the stack is built -- an exterior stack stands in front of the opening
    and an interior one occupies the wall the opening would need.

    WHAT THIS DOES NOT ASSERT. It does not say a Tidewater gable end always has a blind centre; it
    blinds the bay where THIS RECORD places a stack, and says so. Worth knowing before trusting
    that: the kit makes `paired-and-joined-by-arched-curtain` canonical -- "the tall paired stacks
    joined above the roof by an arched brick curtain" -- which is TWO stacks on one gable end with
    the space between them spanned by an arch, and `roof.py` places a single stack per end at
    mid-depth instead. Correct that simplification and the two stacks would flank the centre bay
    rather than stand on it, and the window might come back. That is a roof-layer question and is
    recorded rather than pre-empted here."""
    if not stack_axes_ft:
        return []
    half = stack_width_ft / 2.0
    blinded = []
    for i, cx in enumerate(face_rec["centres_ft"]):
        if face_rec["kinds"][i] == "door":
            # AN ENTRANCE IS NOT BLINDED, AND IT IS STILL REPORTED. A door on a stack's axis is
            # just as impossible as a window on one, but deleting an entrance is not a decision
            # this generator may take on its own -- the entrance is the composition's whole
            # subject, and a facade silently missing its door is a worse drawing than one showing
            # a conflict. So the bay is left alone AND the collision still reaches
            # `count_of_openings_on_the_axis_of_a_chimney_stack`, which means
            # `window-on-the-chimney-axis` fires and a human decides. Refusing to resolve it is
            # not the same as failing to report it, and this comment used to say only the first
            # half. Guarded in tests/test_drawn_geometry.py.
            continue
        if any(abs(cx - ax) <= half for ax in stack_axes_ft):
            face_rec["kinds"][i] = "blind"
            blinded.append(round(cx, 3))
    return blinded


def stack_axes_for_face(face, chimneys, fp):
    """Where the stacks in THIS wall's plane fall on this face's own horizontal axis.

    The roof's plan frame has x along the ridge and y across it. A gable end's own horizontal axis
    IS that plan y, and a long face's is x -- the same mapping `render_elevation` uses for the
    stacks themselves. A stack counts as being in a wall's plane when it stands at that wall: at a
    ridge END for a gable face, at the near or far wall for a long face. Both of this house's
    stacks are at mid-depth, so they are in the gable walls and in neither long wall, which is why
    the front elevation loses no bay and the ends lose their centre one."""
    W, D = fp["width_ft"], fp["depth_ft"]
    out = []
    for c in (chimneys or {}).get("positions") or []:
        x, y = c.get("x_ft"), c.get("y_ft")
        if x is None or y is None:
            continue
        if face in ("E", "W"):
            if abs(x) < 0.5 or abs(x - W) < 0.5:
                out.append(y)
        else:
            if abs(y) < 0.5 or abs(y - D) < 0.5:
                out.append(x)
    return out


# ---------------------------------------------------------------- entrance composition
def entrance_composition(op_pack, facade_pack, gibbs_pack, ground_storey_height_in, forbids=()):
    """OQ 99 (WP-8.3) reaches this file too, and it had to be brought here separately.

    `elevation.py` never calls `resolve_packs` or `eval_packs` -- it calls `PE.resolve(<pack>)`
    and picks slot dimensions straight out of the pack file. So it is blind to bindings, to
    `slots`/`slots_except`, to `declined_packs`, and to the kit's `forbidden`, and the gate
    WP-8.3 put in the resolver does not reach a single figure drawn here. Measured: 41 styles
    pass this generator's own scope gate, and 46 (style, slot) pairs are one of them reading a
    slot its resolved kit FORBIDS -- `transom_sidelight` 14, `frieze` 9, `pilaster` 8,
    `belt_course` 6, `water_table` 6, and one each of `door_surround`, `cornice`,
    `window_head_wood`. `cape-cod-colonial`'s own pilaster note reads "The whole
    classical-apparatus group is forbidden at the family" and this function read a pilaster
    projection for it.
    """
    door_w, door_w_r = _val(op_pack, "entry_door", {"storey_height": ground_storey_height_in}, note_substr="door from the storey", dimension="width")
    door_h, door_h_r = _val(op_pack, "entry_door", {"storey_height": ground_storey_height_in}, note_substr="door height from the storey", dimension="height")
    canonical_h = door_w * 2.0   # opening-proportion's OWN canonical 2:1 check, module=door leaf -- a second, independently-sourced figure to compare against
    casing_w, _ = _val(op_pack, "door_surround", {"module": door_w}, dimension="width")
    gibbs_casing_w, _ = _val(gibbs_pack, "casing", {"opening_width": door_w}, dimension="width")
    # A FORBIDDEN SIDELIGHT HAS NO WIDTH. The composition already carried the branch -- it chose
    # between with and without on a width cap -- so the kit's refusal simply decides it instead,
    # and the figures are ABSENT rather than zero, exactly as a shutter that is not there has no
    # leaf (WP-5.13). 14 of the 46 pairs are this one slot.
    sidelights_forbidden = "transom_sidelight" in forbids
    if sidelights_forbidden:
        sidelight_w = transom_h = None
    else:
        sidelight_w, _ = _val(op_pack, "transom_sidelight", {"module": door_w}, dimension="width")
        transom_h, _ = _val(op_pack, "transom_sidelight", {"module": door_w}, dimension="height")

    with_sidelights_in = None if sidelights_forbidden else door_w + 2 * sidelight_w + 2 * casing_w
    without_sidelights_in = door_w + 2 * casing_w
    # OQ 48: `door_surround`/`width` held two quantities -- an architrave's own face width and the
    # MAXIMUM WIDTH OF THE WHOLE ENTRANCE COMPOSITION, which is what this cap has always meant.
    comp_cap_in, _ = _val(facade_pack, "door_surround",
                          {"module": facade_pack["module"]["default_size_in"]},
                          dimension="entrance_composition_total_width")
    use_sidelights = (not sidelights_forbidden) and with_sidelights_in <= comp_cap_in
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
    # As the sidelights: a slot the kit forbids yields no figure, not a zero.
    pilaster_proj = None if "pilaster" in forbids else \
        _val(gibbs_pack, "pilaster", {"column_height": door_h}, dimension="projection")[0]

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
        # ABSENT, not zero, where the kit forbids the slot -- the `v is not None` filter at the
        # end of _derive_measurements then drops them, which is how WP-5.13 handled a shutter
        # that is not there. A zero here would be a measured claim that the sidelight is
        # nothing wide, which is a different statement from "this style does not have one".
        "sidelight_width_in": None if sidelight_w is None else round(sidelight_w, 3),
        "transom_height_in": None if transom_h is None else round(transom_h, 3),
        "sidelights_forbidden_by_kit": sidelights_forbidden,
        "sidelights_present": use_sidelights,
        "entrance_composition_width_in": round(composition_w, 3),
        "entrance_composition_cap_in": round(comp_cap_in, 3),
        "entrance_composition_note": (
            ("This style's resolved kit binds `transom_sidelight` FORBIDDEN, so the composition "
             "is the door and its casing and no width cap was consulted.") if sidelights_forbidden
            else (f"{'Sidelights fit' if use_sidelights else 'Sidelights would exceed'} facade-classical's own "
                  f"80%-of-bay composition cap ({round(comp_cap_in,1)} in) -- "
                  f"{'included' if use_sidelights else 'omitted, door and casing only'}.")),
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
        "pilaster_projection_in": None if pilaster_proj is None else round(pilaster_proj, 3),
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

    # WHICH PLANE THESE PROJECTIONS ARE MEASURED FROM, decided on the pack's own evidence.
    #
    # OQ 65 ruled the datum onto the PACK: gibbs-ionic inherits `axis` from vignola-ionic. That
    # declaration is true of the column -- `check_orders.py` verifies it against the shaft, base
    # and capital -- but it is NOT true of the entablature in the same pack, and the pack says so
    # itself: the frieze face records a projection of 0, as does the architrave's lowest fascia.
    # A frieze standing on the column's centre line is impossible, so an entablature member's
    # projection here is relief from its own naked. Reading the pack-level `axis` literally over
    # the cornice clamps every member whose figure is smaller than the column's radius flush with
    # the frieze -- which silently deletes this cornice's bed mould and its fillet.
    #
    # DELEGATED, not detected here. This function used to carry its own copy of the rule, and
    # `build/profiles.py::pack_geometry` -- which feeds both order plates and the DXF exporter --
    # kept the pack's literal declaration, so the SAME cornice was drawn two ways, 2.37x apart,
    # in one product. OQ 78 was ruled on 27 Aug 2026: detect per assembly-group, once, where every
    # consumer sees it. The rule and its evidence now live in axis_holds_for() over there.
    full = PE.dimension(gibbs_pack, reduced_module_in)
    geo = PROF.pack_geometry(full, gibbs_pack.get("column"), full.get("projection_datum"))
    entab_from_axis = geo["assembly_datum"].get("cornice") == "axis"
    datum = dim.get("projection_datum")
    totals = full.get("totals", {})
    col_naked_in = (totals.get("upper_diameter_in") or totals.get("lower_diameter_in") or 0.0) / 2.0
    frieze_naked_in = col_naked_in if entab_from_axis else 0.0
    relief = max((m["projection_in"] for m in cor_asm["members"]), default=0.0) - frieze_naked_in
    return {
        "frieze_height_in": round(frieze_h, 3), "cornice_height_in": round(cor_asm["height_in_summed"], 3),
        "cornice_projection_in": round(cornice_proj, 3),
        "reduced_gibbs_module_in": round(reduced_module_in, 3),
        "projection_datum": datum,
        "entablature_projection_datum": "axis" if entab_from_axis else "naked",
        "frieze_naked_in": round(frieze_naked_in, 3),
        "order_relief_beyond_frieze_in": round(relief, 3),
        # TWO PACKS, ONE ADDRESS, DIFFERENT ANSWERS -- stated rather than silently resolved.
        # Gibbs's own rule ("the projection of the Cornice equal to its height", which he holds
        # for every order but the Doric) makes this cornice project as far as it stands tall.
        # facade-classical's `cornice/projection` rule says module/14 for a domestic front. Both
        # are sourced, they are not the same number, and nothing here is entitled to pick: the
        # order's figure draws the profile plate, the envelope's figure draws the band on the
        # wall, and the sheet says both. This is the OQ 48 class at cascade scope.
        "envelope_projection_in": round(cornice_proj, 3),
        "projection_disagreement_note": (
            f"The order's own cornice projects {round(relief,2)} in (Gibbs: projection equals height); "
            f"facade-classical's domestic envelope rule gives {round(cornice_proj,2)} in. Both are sourced "
            f"and they disagree; neither is chosen here."),
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

    # WP-5.11. Two things the pack has always stated and nothing has ever drawn.
    #
    # THE COURSE. brick-course.json's own invariant fixes one course at module/parts, and its
    # notes say what that is for: "in a brick building there are no free horizontal dimensions
    # above the water table". Every band on a brick elevation lands on a bed joint or it is
    # wrong, and a drawing that cannot show the coursing cannot show that.
    #
    # THE MOULDED COURSE. The water table is not a plain plinth: the pack carries it as an
    # ASSEMBLY -- plinth courses in English bond under a Flemish face, then one purpose-moulded
    # course, ovolo on ordinary work and a cyma reversa on the better grade ("the Westover
    # standard" is the pack's own phrase). It has been drawn as a rectangle with a hardcoded
    # four-pixel overhang.
    course_in = moulded = None
    if is_masonry:
        course_in = brick_module_in / brick_pack["module"]["parts"]
        wt_asm = (brick_pack.get("assemblies") or {}).get("water_table")
        if wt_asm and wt_asm.get("members"):
            # Dimensioned at the brick module, so the moulded course is exactly one course deep
            # and the plinth below it exactly as many as the pack says.
            wt_dim = PE.dimension({**brick_pack, "assemblies": {"water_table": wt_asm}},
                                  brick_module_in, include=["water_table"])
            moulded = wt_dim["assemblies"][0]["members"]
    return {
        "applicable": True, "source": source, "is_masonry": is_masonry,
        "water_table_height_above_finished_grade_in": round(wt_h, 3),
        "water_table_projection_in": round(wt_proj, 3),
        "course_height_in": round(course_in, 4) if course_in else None,
        "water_table_members": moulded,
        "belt_height_in": round(belt_h, 3),
        "belt_course_projection_in": round(belt_proj, 3) if belt_proj is not None else None,
        "belt_datum_grade_to_floor_ft": belt_datum_ft,
        "belt_height_above_first_floor_in": round((belt_datum_ft * 12), 2) if belt_datum_ft is not None else None,
    }

# ---------------------------------------------------------------- measurements dict for the fault corpus
# What this generator does NOT model, declared as data so it can be TESTED rather than
# remembered (OQ 52). Every name here was, until 26 Aug 2026, supplied as a constant, and the
# fault corpus adjudicated real houses on all of them -- five convictions and two passes per
# reference plan, every one of them from a number nobody measured. The filter at the foot of
# _derive_measurements() drops anything on this list, so reintroducing one by a careless
# m.update() cannot put it back in front of the critic; tests/test_measurement_honesty.py
# asserts the list stays out of the supplied measurements and that the faults naming these
# variables come back could-not-judge.
#
# To take a name OFF this list: model the thing, derive it from the record, and delete the
# entry in the same commit. That is the only honest way out, and it is the point of the list.
# The sash frame, quoted from proportions/modules/sash-light.json's own note on
# `window_type/width`: "Sash stile width, both sides. Together with the 2 in top rail, 3 in bottom
# rail and 1 1/4 in meeting rail this is the whole sash frame, and all four numbers are
# near-constant from 1700 to 1900 -- they are set by mortise-and-tenon joinery." The pack states
# them in prose and carries no expression for them, so they are transcribed here in the one place
# that needs them, the way GLASS_MODULE_BANDS transcribes that pack's period table.
SASH_FRAME = {"stile_in": 2.0, "top_rail_in": 2.0, "bottom_rail_in": 3.0, "meeting_rail_in": 1.25}

# Where a dormer face stands up the slope, measured along it. Editorial: the fault corpus
# prefers 18-36 in and requires at least 12; nothing reachable states a figure.
DORMER_SETBACK_ON_SLOPE_IN = 24.0


# THE ORDER-AT-THE-EAVE SET, and it is short because the thing is rare. A variant belongs here
# only when the corpus's own words say the order is structurally integral to the WALL, so that
# the entablature it carries IS the eave. Each entry quotes the note that put it in; a variant
# not listed is not thereby a guess, because the question is only ever asked of a cornice this
# generator measured, and the cornice it measures is the EAVE's.
ORDER_AT_THE_EAVE = {
    # WHAT PUTS AN ENTABLATURE AT THE EAVE, and the entries are quoted from the corpus's own
    # records rather than from a general idea of what a giant order is.
    "two-tier-engaged-portico":
        "tidewater-georgian / porch_type: 'The grandest houses only, structurally integral, "
        "superimposed orders. Drayton Hall is the type case.'",
    "projecting-colossal-order-portico":
        "neoclassical-revival / porch_type: a colossal portico spans every storey, so its "
        "entablature IS the main one",
    "engaged-giant-order":
        "beaux-arts-american / pilaster: 'Articulates the recessed wall plane between advanced "
        "pavilions' -- engaged over the wall's full height",
    "giant-pilaster":
        "english-baroque / pilaster: 'The giant order embraces two or more storeys as often in "
        "pilaster form as in engaged or free-standing column form.'",
    "giant-order-facade-pilaster":
        "'A Beaux-Arts and Neoclassical Revival device across a flat wall' -- a pilastered front",
    "giant-order-two-storey": "order: 'Giant order spanning two storeys.'",
    "giant-order": "order: the giant order, which by definition reaches the entablature",
    "colossal-two-storey-column": "column: a colossal order carried over two storeys",
    "coupled-columns-giant-order":
        "column: 'Coupled columns, usually of a giant order, marking a projecting central "
        "pavilion on a symmetrical front.'",
}

# Anything canonical that READS like an applied order and is not classified above makes the
# question UNJUDGED rather than answered 0. Added 28 Aug 2026 by this package's own adversarial
# audit, which found the hand list missing every one of the corpus's real giant-order variants:
# `beaux-arts-american`, `neoclassical-revival`, `english-baroque` and two more returned 0 with a
# confident note saying every canonical variant was "a void or an attached structure", which
# selects the DOMESTIC cornice band (0.35-0.55) for a front whose cornice legitimately runs
# 0.85-1.2 and convicts it. OQ 84 replaced "both rivals run, one convicts" with "the wrong one
# runs, silently" on five styles. A short hand list is fine for what it names; what it must not do
# is answer confidently about what it does not.
_LOOKS_LIKE_AN_ORDER = re.compile(r"giant|colossal|two-tier|full-height")


def order_at_the_eave(porch_slot, pilaster_slot, declared):
    """Is an order applied to the WALL, so that the eave cornice is an entablature?

    OQ 84. `cornice-that-is-a-fascia` carries two rival secondaries on one expression -- the
    domestic boxed eave at 0.35-0.55 of its own height and the full entablature-derived case at
    0.85-1.2 -- and whichever is right the other convicts the house. The fault states the
    discriminator in its own note ("Choose the test by whether an order is present, not by
    preference") and no generator took the measurement, so both tests sat over every house.

    WHAT THIS IS NOT. `gibbs_order_applies_to_style` is True on tidewater-georgian and means only
    that Gibbs Ionic is the order this style's cornice is GENERATED from. Reading it as "an order
    is applied to this facade" selects the entablature test on a house that measures 0.4286 and
    convicts it. That was checked before this function was written, and it is the whole reason the
    signal is the porch and pilaster slots instead.

    NOR IS A PORTICO ENOUGH. tidewater-georgian's own porch rule says that "where a portico occurs
    it is one bay wide, centred, and carries the bound order" -- a one-bay portico has its own
    entablature, below the eave, and the eave beside it is still a domestic boxed cornice. Only an
    order engaging the whole wall makes the eave an entablature, which is what ORDER_AT_THE_EAVE
    lists and what its quotations justify.

    THREE STATES, as everywhere else in this file: 1 where the record or the style puts such an
    order on the wall, 0 where nothing available to this house could, and ABSENT where the style
    makes one canonical and the record has not chosen -- because then nobody has decided, and a
    guess here picks which of two rival tests judges the house."""
    declared_porch = (declared or {}).get("porch_type")
    if isinstance(declared_porch, dict):
        declared_porch = declared_porch.get("variant")
    if declared_porch:
        hit = declared_porch in ORDER_AT_THE_EAVE
        return (1 if hit else 0), (
            f"The record declares porch_type '{declared_porch}', which "
            + (f"carries the order to the eave -- {ORDER_AT_THE_EAVE[declared_porch]}"
               if hit else "does not engage the wall over its full height, so the eave cornice is "
                           "a domestic boxed one and the order (if any) is the portico's own."))

    # Nothing declared: read what the style could canonically put there.
    canon = set()
    for slot in (porch_slot, pilaster_slot):
        for v in (slot or {}).get("variants") or []:
            if v.get("status") == "canonical":
                canon.add(v["id"])
    if not canon:
        return None, ("Neither the record nor the style states what stands at the threshold, so "
                      "whether an order reaches the eave is unjudged -- and the two rival "
                      "secondaries of cornice-that-is-a-fascia both decline rather than one of "
                      "them judging the house on a guess.")
    engaged = sorted(canon & set(ORDER_AT_THE_EAVE))
    if engaged:
        return None, (f"The style makes {', '.join(engaged)} canonical and the record has not "
                      f"chosen. Somebody must; until then this is unjudged rather than assumed.")
    unclassified = sorted(v for v in canon
                          if v not in ORDER_AT_THE_EAVE and _LOOKS_LIKE_AN_ORDER.search(v))
    if unclassified:
        return None, (
            f"This style makes {', '.join(unclassified)} canonical, which reads like an order "
            "applied over the wall's full height but is not in ORDER_AT_THE_EAVE. Whether it "
            "carries the eave cornice decides which of cornice-that-is-a-fascia's two rival rules "
            "judges the house, so it is left UNJUDGED and both decline. Classify the variant, with "
            "the record's own words, rather than letting a hand list answer by omission.")
    return 0, ("The record states no porch and every variant this style makes canonical "
               f"({', '.join(sorted(canon))}) is a void or an attached structure rather than an "
               "order engaging the wall, so the eave cornice is a domestic boxed one whichever "
               "is built.")


def _dormer_lights(sash_set):
    """(across, high per sash) for a dormer's stated sash pattern, or (None, None).

    "6/6" is six lights in the UPPER sash over six in the lower -- the corpus's own notation and
    the one _storey_window already uses (`lights_high_per_sash`). Reading the 6 as the whole
    opening puts half the glazing bars in, which is what the dormer drawing did on its first
    outing. Six lights go 2 across by 3 high, four go 2 by 2, eight 2 by 4, nine and twelve 3
    across; anything else falls back to the two-wide reading, which is what a dormer sash is.

    A STYLE WHOSE KIT STATES NO PATTERN GETS NONE, not 6/6. `colonial-revival` is such a style,
    and the first version defaulted -- so a spec-builder colonial's dormers came back with a
    confident 6/6 that no record anywhere had said. A glazing pattern nobody stated is a pattern
    the drawing must not assert; the sash is drawn as glass and the sheet says the pattern is
    undeclared."""
    if not sash_set:
        return None, None
    try:
        per = int(str(sash_set[0]).split("/")[0])
    except (ValueError, IndexError):
        return None, None
    across = 3 if per in (9, 12, 15) else 2
    return across, max(1, per // across)


def dormers(plan, kit_slot, faces, upper_w, roof, entrance_face, module_in,
            cornice=None, casing_in=None, house_wall_in=None):
    """The dormers this house carries, or a stated none, or nothing at all.

    THREE STATES, and they are the point. `declared.dormer` absent means the record does not say
    -- every dormer measurement is then ABSENT, because build/roof.py could not tell a house with
    no dormers from a house whose dormers it had no way to state, and writing 0 over that is the
    cape-central-chimney incident (OQ 59): a refusal published as a measurement, which then
    convicted a parti named for the very thing. `"none"` is a house STATED to have none, so
    dormer_count is a real zero the fault corpus may judge. An object is a house that has them.

    EVERY DIMENSION COMES FROM THE CORPUS, and mostly from the fault corpus, which turns out to
    specify a dormer completely:

      overscaled-dormer   dormer window <= the window directly below, correct at 0.75-1.0. A
                          dormer is a small building on a large roof and its window is one
                          storey-step smaller than the sash beneath it.
      fat-cheek-dormer    visible cheek <= 0.25 of the sash width; historic work 0.12-0.25.
      sunken-dormer       at least 12 in of roof in front of the face, 18-36 preferred -- "the
                          strip of roof in front of a dormer is what makes it a dormer".
      dormer-off-the-bay  every dormer centred on a window below, which is also the kit's own
                          alignment_rule, so the centres are DERIVED from the bays rather than
                          authored: a record cannot state a rhythm contradicting its own style.
      dormer-wall         the faces together <= 0.4 of the building width.

    So nothing here is invented. What is NOT derivable is named: the sill's height above the
    garret floor, and the overall face width as a measured figure rather than as window plus two
    cheeks plus two stiles -- no Chesapeake example reachable from here states either."""
    declared = (plan.get("declared") or {}).get("dormer")
    if declared is None:
        return {"applicable": False, "stated": False,
                "note": "This plan does not say whether it carries dormers. Not an absence of "
                        "dormers -- an absence of a statement, so every dormer measurement is "
                        "withheld rather than reported as zero."}
    if declared == "none":
        return {"applicable": True, "stated": True, "count": 0, "positions": [],
                "note": "The plan states this house carries no dormers."}

    count = int(declared.get("count") or 0)
    face = declared.get("face") or entrance_face
    variants = {v["id"]: v.get("status") for v in (kit_slot.get("variants") or [])}
    want = declared.get("variant")
    if want and variants.get(want) == "forbidden":
        return {"applicable": True, "stated": True, "count": count, "positions": [],
                "refused": True,
                "note": f"The plan declares a {want} dormer and this style forbids it."}
    # THE VARIANT IS A CHOICE, AND PICKING THE FIRST CANONICAL ONE IS NOT MAKING IT. The first
    # version took `next(canonical)`, which is dict order dressed as a decision: on
    # `spec-builder-colonial` that returned `eyebrow-swept-dormer-within-thatch` -- a thatched
    # cottage's dormer, on a production colonial, chosen because it happened to sort first in a
    # cascaded slot. Where the record does not state a variant and the style makes more than one
    # canonical, the record has not chosen and this says so, in the same shape the window head
    # already uses when the date cannot separate two masonry heads: the drawing shows the plain
    # gabled form and the legend says the variant is undeclared.
    canonical = [v for v, st in variants.items() if st == "canonical"]
    variant = want or (canonical[0] if len(canonical) == 1 else None)
    variant_undeclared = None if variant else sorted(canonical)
    # AND WHERE THE VARIANT LIST CAME FROM, which on this slot is not a formality. Drawing this
    # for `spec-builder-colonial` returned `eyebrow-swept-dormer-within-thatch` -- a dormer formed
    # within the thatch of an English cottage -- as the ONE canonical dormer of Colonial Revival,
    # with `boxed-dormer` FORBIDDEN. It is not dict order and it is not a bug here:
    # `colonial-revival` binds this slot nothing, and the lineage cascade resolves the whole of it
    # from `english-cottage-vernacular`. That is OQ 51's class arriving in the kit layer rather
    # than the proportion layer, and it reaches the drawing as a confident thatch dormer on a
    # production colonial. Adjudicating it is a corpus decision, not a renderer's; saying where
    # the variant came from costs one field and puts the question on the sheet.
    variant_source = kit_slot.get("_source")

    params = kit_slot.get("parameters") or {}
    cheek_band = (params.get("cheek_width") or {}).get("range")
    sash_set = (params.get("sash_pattern") or {}).get("set") or []
    parity = (params.get("count_parity") or {}).get("value")

    # The window: one storey-step smaller than the sash below, at the top of the band the fault
    # corpus calls correct. Its own height comes from the kit's derived rule where the kit gives
    # one, and from the same 0.75 step where it does not.
    below_w = upper_w["opening_width_in"]
    win_w = round(below_w * 0.85, 3)              # inside 0.75-1.0, and not at the limit
    kh = (params.get("dormer_window_height_in") or {})
    win_h = None
    if kh.get("expr"):
        try:
            win_h = round(PE.evaluate_expr(kh["expr"], {"module": module_in}), 3)
        except Exception:
            win_h = None
    if win_h is None:
        win_h = round(upper_w["opening_height_in"] * 0.75, 3)

    # THE CHEEK sits inside THREE bounds, and the third was found by drawing it. The kit gives an
    # absolute 4-8 in band; `fat-cheek-dormer`'s test caps it at 0.25 of the sash width (historic
    # work runs 0.12-0.25); and that same fault's correct_practice states a rule its test does not
    # encode -- "the finished cheek width should not exceed the width of the window CASING beside
    # it", and where a corner board is unavoidable it should be "the same width as the window
    # casing so that the two read as one member rather than as two competing ones". The kit band's
    # midpoint is 6 in against this house's 4.21 in casing, which breaks that rule; on the sheet
    # it showed as a strip of bare board outboard of the casing, two members where the tradition
    # wants one. Clamped to the casing, the cheek IS the casing and the dormer face is the window
    # plus its two casings exactly -- which is also the face the cornice is sized from below, so
    # the two derivations agree by construction instead of by coincidence.
    _mid = (cheek_band[0] + cheek_band[1]) / 2.0 if cheek_band else win_w * 0.18
    cheek = round(min(_mid, win_w * 0.22, casing_in or _mid), 3)
    face_w = round(win_w + 2 * cheek, 3)

    # THE CENTRES OF THE FACE THE DORMERS ARE ON, which is not always the entrance face. This read
    # `faces[entrance_face]` unconditionally until 28 Aug 2026, when this package's own adversarial
    # audit found it: a record declaring `{"count": 3, "face": "E"}` on the tidewater house got the
    # SOUTH front's bay centres -- 18.774, 31.29, 43.806 ft -- laid out on an east elevation 42.66
    # ft wide, so the third dormer stood 1.15 ft past the corner of the wall and none of the three
    # was over an E-face window. Worse, the generator then published
    # `count_of_dormers_centred_on_a_window_below: 3` against `dormer_count: 3` and
    # `dormer-off-the-bay` cleared the house on a number nobody had measured -- the OQ 52 class,
    # inside the package that closed it.
    #
    # A BLIND BAY IS NOT A CANDIDATE EITHER (OQ 85): a chimney stack stands on that axis, so there
    # is no window below for a dormer to centre on.
    face_rec = (faces or {}).get(face) or {}
    centres = [c for c, k in zip(face_rec.get("centres_ft") or [],
                                 face_rec.get("kinds") or [])
               if k != "blind"]
    if count and len(centres) >= count:
        # Centred on windows below, taken from the middle outward so an odd count sits on the
        # centre bay -- which is what the kit's parity rule is FOR on a five-bay front.
        order = sorted(range(len(centres)), key=lambda i: abs(i - (len(centres) - 1) / 2.0))
        chosen = sorted(order[:count])
        positions = [centres[i] for i in chosen]
    else:
        positions = centres[:count]

    # THE DORMER'S OWN CORNICE, and it is not a new invention: it is the house's cornice, read
    # small. The kit's rule for this slot says so in its own words -- dormers "carry the same
    # order as the house at reduced scale" -- and `overscaled-dormer` says it from the other
    # side ("Dormers carry the same order as the house at reduced scale; at full scale they
    # compete with it"). Until 27 Aug 2026 the drawing had the gable springing straight off the
    # head casing with no cornice at all, which is the abstraction the whole of WP-5.11 to 5.9
    # exists to remove, at dormer scale.
    #
    # HOW BIG. `cornice-that-is-a-fascia`'s third secondary states the rule the HOUSE's cornice
    # obeys -- the crowning assembly is one twelfth to one fourteenth of the wall it crowns, and
    # this house's own comes out at 0.078, inside that band. A dormer face is a small wall, so
    # the same ratio the house itself uses, applied to the dormer's own face, gives the dormer's
    # cornice: one rule used twice, not a second rule for dormers that nobody wrote. The face
    # taken is the window plus its two casings, which is the only part of a dormer's face this
    # corpus dimensions -- an apron below the sill and a frieze above the head are real and
    # unpublished, so they are not added and the figure is the smaller for it.
    #
    # ITS PROJECTION follows by the same ratio, from the house's own cornice projection. A
    # cornice reduced in height and kept at full projection is a different profile, not the same
    # one small, and the rule the kit states is that it is the same one.
    cornice_h = cornice_proj = None
    cornice_ratio_note = None
    if cornice and cornice.get("cornice_height_in") and casing_in and house_wall_in:
        # The wall this house's cornice crowns, water table to cornice -- the same quantity
        # `cornice-that-is-a-fascia`'s own expression names, and the same number
        # _derive_measurements publishes under that name. Passed in rather than re-derived: two
        # derivations of one quantity is how the elevation inset and the order plates came to
        # draw the same cornice 2.37x apart (OQ 78).
        if house_wall_in:
            ratio = cornice["cornice_height_in"] / house_wall_in
            dormer_wall_in = win_h + 2 * casing_in
            cornice_h = round(ratio * dormer_wall_in, 3)
            cornice_proj = round((cornice.get("envelope_projection_in") or 0.0) * (cornice_h / cornice["cornice_height_in"]), 3)
            cornice_ratio_note = (
                f"The house's own cornice is {round(ratio, 4)} of the wall it crowns -- inside "
                f"cornice-that-is-a-fascia's stated 1/14 to 1/12. The same ratio over this "
                f"dormer's face ({round(dormer_wall_in, 1)} in of window plus casings) gives "
                f"{cornice_h} in, projecting {cornice_proj} in. The kit's rule for this slot is "
                f"that a dormer carries the same order as the house at reduced scale; this is "
                f"that rule with a number in it. The wall figure excludes an apron and a frieze "
                f"the corpus does not dimension, so it errs small.")

    return {
        "applicable": True, "stated": True, "count": count, "face": face, "variant": variant,
        "variant_undeclared_choices": variant_undeclared,
        "variant_source_node": variant_source,
        "positions_ft": positions, "window_width_in": win_w, "window_height_in": win_h,
        "cheek_width_in": cheek, "face_width_in": face_w,
        "casing_width_in": casing_in,
        "cornice_height_in": cornice_h, "cornice_projection_in": cornice_proj,
        "cornice_source": cornice_ratio_note,
        # THE SASH, in the same terms the storey windows use, so the dormer is drawn by the same
        # renderer and cannot drift from them. "6/6" is six lights in EACH sash, not six in the
        # window: the drawing had been reading the first number as the whole opening and putting
        # half the glazing bars in.
        "lights_across": _dormer_lights(sash_set)[0],
        "lights_high_per_sash": _dormer_lights(sash_set)[1],
        # THE DECLARED COUNT, NOT THE PLACED ONE. `positions` is capped at the number of bays the
        # face has, so a record declaring 24 dormers on a five-bay front reported the face width
        # of FIVE -- and `dormer-wall`, which is FATAL, read 0.248 instead of 1.188 and cleared a
        # house carrying more dormer face than it has wall. Found 28 Aug 2026 by this package's
        # own adversarial audit. What the record asserts is on the building is what the fault
        # about how much of the building is dormer has to measure.
        "sum_of_face_widths_in": round(face_w * count, 3),
        "placed_count": len(positions),
        "placement_shortfall_note": (
            None if len(positions) >= count else
            f"{count} dormers are declared and this face has {len(positions)} bays free to carry "
            f"them, so {count - len(positions)} are not placed. The measurements still report the "
            f"declared count: the fault corpus judges the house the record describes."),
        "sash_pattern": sash_set[0] if sash_set else None,
        "count_parity_stated": parity,
        "count_parity_ok": (None if not parity else
                            (count % 2 == 1) if parity == "odd" else (count % 2 == 0)),
        # THE STRIP OF ROOF IN FRONT OF THE FACE. `sunken-dormer` wants at least 12 in of it and
        # prefers 18-36 -- "the strip of roof in front of a dormer is what makes it a dormer".
        # Where the face sits up the slope is a POSITIONING CHOICE and no source reachable from
        # here states one for a Chesapeake example, so this is editorial: the lower-middle of the
        # fault corpus's own preferred band, named as a choice rather than derived from the
        # dormer's height, which would have produced 56 in and called it geometry.
        "roof_run_in_front_in": DORMER_SETBACK_ON_SLOPE_IN,
        "roof_run_in_front_source": "editorial: the lower-middle of sunken-dormer's own preferred "
                                    "18-36 in band; no Chesapeake example reachable from here "
                                    "states where the face sits up the slope",
        "source": "the style's kit for the variant, cheek and sash; the fault corpus for the "
                  "window-to-sash step and the rhythm; the bays below for the centres",
    }


NOT_MODELLED = {
    # `dormer_count` and `sum_of_dormer_face_widths_in` LEFT this list on 27 Aug 2026 (WP-5.13),
    # under its own rule: to take a name off you must model the thing in the same commit. They are
    # modelled now -- schema/plan.schema.json gained `declared.dormer` and build/elevation.py
    # gained dormers(). What made them refusable was never the geometry; it was that an absent
    # dormer and an unstatable one were indistinguishable, so any figure at all was a guess. The
    # new field separates them: "none" is a measured zero the fault corpus may judge, an absent
    # key is could-not-evaluate, and these measurements are supplied ONLY in the first case.
    # roof.py's chimney record carries a position and two heights. There is no plan size in it.
    # WP-5.11 corrected these four reasons. brick-course DOES carry `chimney/width` (part * 8,
    # 22 in here) -- so the old reason, that nobody had wired it, was wrong. The real reason is
    # stronger: that rule is flagged `judgment: true` and its own note says a mason will build 18
    # or 27 and "someone should decide which rather than discovering it on site". A judgment slot
    # is marked, not filled, so the figure must not reach the fault corpus and convict a house on
    # a size the sources declined to fix. The elevation record carries it for the DRAWING only,
    # as `chimney_stack_plan_in`, labelled a judgment on the sheet.
    "chimney_width_in": "brick-course states a stack width but flags it judgment: 18 or 27 in is a decision, not a measurement",
    "chimney_depth_in": "no pack states a stack depth distinct from its width; claiming one would invent an aspect ratio",
    "chimney_least_plan_dimension_in": "as chimney_width_in -- the only figure available is a judgment",
    "chimney_visible_face_width_in": "as chimney_width_in -- the only figure available is a judgment",
    "cap_projection_beyond_stack_face_in": "no stack cap is modelled",
    "count_of_sheet_metal_caps_or_louvred_shrouds_at_the_stack_head": "no stack head is modelled",
    "count_of_horizontal_shadow_lines_in_the_top_18in_of_the_stack": "no stack head is modelled",
    # eave_cornice() dimensions the horizontal run only; the rake is never composed.
    "raking_cornice_member_count": "eave_cornice() dimensions the horizontal entablature only",
    # Nothing in this corpus models a gutter: no slot, no kit parameter, no line in a renderer.
    "gutter_outlets": "no gutter is modelled anywhere in the corpus",
    # WP-5.13. These four were SUPPLIED, from ratios of the leaf width and the muntin that exist
    # in no pack, kit or element file: 0.8, 0.4, 0.18 and x3. `shutter-panel-scale` was reading
    # two of them and judging houses on the result. A shutter's framing IS knowable -- period work
    # graduates stile, top rail, lock rail and bottom rail -- but no figure for a Chesapeake
    # example could be established, so the field they leave is not derivable either.
    "shutter_panel_field_width_in": "no pack states a shutter's stile or rail widths, so the "
                                    "field they leave cannot be derived",
    "shutter_panel_field_height_in": "as shutter_panel_field_width_in",
    "shutter_stile_width_in": "no pack states a shutter's stile width",
    "shutter_lock_rail_height_in": "no pack states a shutter's rail widths",
    "overflow_scuppers": "no gutter is modelled anywhere in the corpus",
}

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
        # THE SASH FRAME, read from sash-light.json's own note rather than derived from the muntin.
        # These four were computed as ratios of the muntin width until 27 Aug 2026 -- stile at
        # muntin x 4 (3.5 in, against the pack's stated 2 in: 75% too wide, on the very dimension
        # `muntin-wider-than-its-date` measures) and meeting rail at muntin x 1.5. Neither ratio
        # existed anywhere in kits/, proportions/ or elements/. The pack states all four plainly:
        # "Sash stile width, both sides. Together with the 2 in top rail, 3 in bottom rail and
        # 1 1/4 in meeting rail this is the whole sash frame, and all four numbers are
        # near-constant from 1700 to 1900 -- they are set by mortise-and-tenon joinery."
        # A bottom rail deeper than the top rail is the fastest tell of a wrongly-drawn sash.
        "sash_stile_width_in": SASH_FRAME["stile_in"],
        "sash_top_rail_height_in": SASH_FRAME["top_rail_in"],
        "sash_bottom_rail_height_in": SASH_FRAME["bottom_rail_in"],
        "sash_meeting_rail_height_in": SASH_FRAME["meeting_rail_in"],
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
        "shutter_panel_count_per_leaf": ground_w.get("shutter_panel_count"),
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
        # A zero here means "the cap excluded them"; ABSENT means "this style's kit forbids the
        # slot and no figure exists". Collapsing the second into the first is OQ 52's class.
        "sidelight_width_in": (None if ent.get("sidelights_forbidden_by_kit")
                               else (ent["sidelight_width_in"] if ent["sidelights_present"] else 0.0)),
        # THE WHOLE TRANSOM FAMILY GOES ABSENT TOGETHER, or none of it does. Nulling
        # `transom_height_in` alone left `transom_width_in` and `transom_head_rise_in` supplied,
        # and `fanlight-before-its-date` and `transom-bar-at-the-wrong-height` immediately
        # convicted `spec-builder-colonial` on the half that remained -- two faults that
        # PRESUPPOSE a transom, firing on a house whose kit forbids the slot. That is OQ 52's
        # rule stated the other way round: when the generator does not model a thing, every
        # measurement of that thing must be absent, and a partially-supplied set is worse than
        # either a complete one or none at all, because it reads as evidence.
        "transom_height_in": ent["transom_height_in"],
        "transom_width_in": (None if ent.get("sidelights_forbidden_by_kit")
                             else ent["door_leaf_width_in"]),
        # a rectangular transom, not an elliptical fanlight -- see entrance_composition()'s note
        "transom_head_rise_in": None if ent.get("sidelights_forbidden_by_kit") else 0.0,
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
        "visible_hardware_items_per_window": 6, "visible_surface_hinges_per_leaf": 3,
        "front_door_plane_setback_behind_garage_door_plane_ft": 0.0,
    })

    m.update({
        # cornice_projection_in IS emitted now, and that is OQ 84 closing. It was withheld from
        # WP-3.2 until 27 Aug 2026 because faults/cornice-that-is-a-fascia.json carries two RIVAL
        # secondaries on `cornice_projection_in / cornice_height_in` -- the domestic boxed eave at
        # 0.35-0.55 and the full entablature-derived case at 0.85-1.2 -- so supplying the name
        # meant one of them convicting every house whatever it measured. Withholding it made the
        # fault inert on a name mismatch, which is a workaround wearing the costume of a decision:
        # the primary test and two of the four secondaries were being skipped as well.
        # Both rivals now carry an `applies_when` on
        # `an_order_is_applied_to_the_wall_carrying_the_eave_cornice`, so exactly one of them can
        # run, and the fault is judged on evidence instead of silenced by a typo.
        "cornice_projection_in": cornice["cornice_projection_in"],
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
        # raking_cornice_member_count is NOT supplied (OQ 52). eave_cornice() dimensions the
        # HORIZONTAL entablature run and nothing else; whether those members are carried up the
        # rake to close a pediment is a decision this file never makes and the record never holds.
        # Supplying 0 asserted that they are not -- which convicted every gable-roofed plan of an
        # incomplete-pediment fault on a number nobody measured.
        "horizontal_cornice_member_count": cornice["member_count"],
        "cyma_profiles_at_the_eave": sum(1 for mm in cornice["members"] if "cyma" in (mm.get("profile") or "")),
        "eave_overhang_in": cornice["cornice_projection_in"], "eave_projection_in": cornice["cornice_projection_in"],
        # gutter_outlets and overflow_scuppers are NOT supplied (OQ 52). Nothing in this corpus
        # models a gutter -- no slot, no kit parameter, no line in any renderer -- so "2 outlets
        # and no scuppers" was a sentence with no author. It convicted both reference plans.
        "rake_overhang_in": cornice["cornice_projection_in"],
        "count_of_perforations_visible_in_the_cornice_soffit_frieze_or_fascia": 0,
        "count_of_plane_changes_between_wall_face_and_roof_surface": cornice["member_count"],
        "window_head_casings_colliding_with_the_cornice_bed_mould": False,
        "count_of_interruptions_in_the_eave_line": 0,
        # NOTE: this file does not model the cornice's own corner RETURN (how far it wraps the
        # gable wall before dying in) -- unlike the projection and member-count numbers above,
        # a return's own depth is not simply the cornice's face projection, and guessing it
        # produced a false 'pork-chop-return' fatal on a plan that never actually specified one.
        # Left could_not_judge rather than fabricated. See docs/reports/wp-3.2 for the finding.
        # dormer_count and sum_of_dormer_face_widths_in used to be refused here, on the reasoning
        # that no plan schema field authored a dormer so this generator could not tell a house
        # with none from a house whose dormers the record had no way to state. `declared.dormer`
        # tells them apart now, and both are supplied FROM IT rather than from this block -- see
        # dormers() above and the dormer_m fold at the end of build_elevation, which supplies them
        # only where the record actually stated something.
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

    _open_bays = sum(1 for k in bays["kinds"] if k != "blind")
    _has_door = "door" in bays["kinds"]
    m.update({
        "count_of_openings_without_a_mirror_twin_about_the_facade_centreline": 0,
        "width_of_the_largest_asymmetric_element_in": 0.0, "facade_width_in": elev["front"]["outside_width_in"],
        "elevation_width_in": elev["front"]["outside_width_in"], "elevation_length": elev["front"]["outside_width_in"],
        "building_width_in": elev["front"]["outside_width_in"], "street_elevation_width_in": elev["front"]["outside_width_in"],
        "front_elevation_width": elev["front"]["outside_width_in"],
        # A BLIND BAY IS A BAY AND NOT AN OPENING (OQ 85). `bay_count` counts bays -- the rhythm
        # is five bays whether or not one of them is blinded by a stack -- but an OPENING count
        # must not include a bay with no opening in it. Found 28 Aug 2026 by this package's own
        # adversarial audit: these three read `bays["count"]` and would have reported an opening
        # where the same package had just stopped drawing one. Inert on both reference plans,
        # whose blind bays are on the gable ends rather than the front, and live for any record
        # whose roof puts a stack at the front or back wall.
        "upper_floor_opening_count": _open_bays, "total_upper_storey_openings": _open_bays,
        "openings_on_the_front_elevation": _open_bays * 2 - (1 if _has_door else 0),
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
        # NO CHIMNEY PLAN DIMENSIONS ARE SUPPLIED (OQ 52), and the absence is the point. This
        # file used to state five of them as constants -- a 36 x 20 in stack with a 4 in cap
        # projection and one shadow line -- beside a `visible_chimney_count` that is correctly
        # ABSENT whenever roof.py could not judge it. roof.py's chimney record carries a
        # position and two heights and nothing else: there is no width, no depth, no cap in it,
        # and no kit parameter this file reads for one. `vestigial-chimney-chase` was then
        # adjudicated from 20/36 = 0.5556 against an at-least 0.6 -- a fabricated failure, with
        # its own primary test passing on the same fabricated numbers beside it.
        # When the corpus learns to state a stack's plan size, supply it here from the record.
        "count_of_stacks_with_a_visible_consequence_at_the_wall": roof.get("visible_chimney_count"),
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
        # OQ 85. A MEASURED ZERO, and it is the generator publishing that it resolved a collision
        # rather than that one never existed: on this house's gable ends the bay a stack stands on
        # IS blinded, and this says so in a form `window-on-the-chimney-axis` can check. Any other
        # producer -- an ingested drawing, a hand-authored record -- gets checked against the same
        # rule instead of being trusted. Counted over every face, because the entrance face is not
        # where this happens.
        "count_of_openings_on_the_axis_of_a_chimney_stack": sum(
            1 for f, fa in elev["faces"].items()
            for cx, kind in zip(fa["centres_ft"], fa["kinds"])
            if kind != "blind" and any(
                abs(cx - ax) <= ((elev.get("chimney_stack_plan_in") or 22.0) / 24.0)
                for ax in stack_axes_for_face(f, (elev.get("roof_record") or {}).get("chimneys"),
                                              elev["footprint"]))),
        "vent_terminal_height_above_roof_surface_in": 0.0,
        # solar_array_area_sqft IS supplied now, and its honest zero is the point. This key was
        # withheld for the same reason cornice_projection_in was, and the comment here said so:
        # entrance-slope-penetration's array secondary is "the conditional test for arrays" and
        # core.check_measurements "has no way to gate a secondary test on another value", so a
        # truthful 0 sqft read as 0/plane = 0.0 and convicted the house of a patchy array it does
        # not have. It has a way now -- `applies_when` (WP-5.13) -- and that secondary is
        # preconditioned on the array's own area, so a house with no array declines the test
        # rather than failing it. Two workarounds retired by one field.
        "solar_array_area_sqft": 0.0,
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
    # Blind bays carry no glass (OQ 85); counting their notional windows would inflate the glazed
    # area of a house whose stack stands where the window would have been.
    _open = sum(1 for k in front["kinds"] if k != "blind")
    gnd_win_count = max(0, _open - (1 if "door" in front["kinds"] else 0))
    upr_win_count = _open
    glazed_in2 = (gnd_win_count * ground_w["opening_width_in"] * ground_w["opening_height_in"] +
                  upr_win_count * upper_w["opening_width_in"] * upper_w["opening_height_in"])
    wall_in2 = front["outside_width_in"] * (elev["ground_storey_height_in"] + elev["upper_storey_height_in"])
    m["glazed_area"] = round(glazed_in2 / 144.0, 2)
    m["street_facing_wall_area"] = round(wall_in2 / 144.0, 2)

    if elev["water_table_belt"]["is_masonry"]:
        brick_pack = PE.resolve("brick-course")
        m["arch_depth_in"] = brick_pack["module"]["default_size_in"]   # brick-course.json: arch_depth_in = module

    # Two filters, and they mean different things. A None is a thing this generator models but
    # could not measure on THIS house, and it is dropped so the corpus reports it as
    # could-not-judge rather than comparing against a null. A NOT_MODELLED key is a thing this
    # generator does not model at all: it should never have been built, and the filter is here
    # so that a future edit reintroducing one cannot reach the critic (OQ 52).
    return {k: v for k, v in m.items() if v is not None and k not in NOT_MODELLED}

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

    # WP-5.11: THE STACK'S PLAN SIZE, AND WHY IT STAYS OUT OF THE MEASUREMENTS.
    #
    # Four names sit in NOT_MODELLED saying "the roof record carries no chimney plan dimension",
    # and this looked at first like a wiring job: brick-course DOES carry `chimney/width` as
    # `part * 8`, eight courses square, 22 in on this style. But that rule is flagged
    # `judgment: true`, and its own note says why: "Twenty-two inches on the default coursing is
    # between sizes; the mason will build 18 or 27 and someone should decide which rather than
    # discovering it on site."
    #
    # So this was never a MISSING measurement. It is a DEFERRED one, and the corpus's sixth
    # settled decision is that a judgment slot is marked, not filled. Publishing 22 in into
    # `measurements` would hand the fault corpus a number the sources deliberately declined to
    # fix, and houses would be convicted on it. The entries therefore STAY in NOT_MODELLED, with
    # their reason corrected from "nobody wired it" to "nobody is entitled to".
    #
    # What changes is the DRAWING, which had been asserting a hardcoded 36 in over the top of the
    # very slot the corpus left open. It now draws the pack's own figure and says on the sheet
    # that it is a judgment between two buildable sizes. A drawing may show a deferred figure;
    # it may not pretend the deferral is not there.
    chimney_plan_in = chimney_plan_judgment = None
    if is_masonry:
        try:
            chimney_plan_in, _ = _val(brick_pack, "chimney",
                                      {"part": brick_pack["module"]["default_size_in"] / brick_pack["module"]["parts"]},
                                      dimension="width")
            rule = next((r for r in brick_pack.get("derived_rules", [])
                         if r.get("target_slot") == "chimney" and r.get("dimension") == "width"), None)
            if rule and rule.get("judgment"):
                chimney_plan_judgment = rule.get("note")
        except Exception:
            chimney_plan_in = None

    # WP-5.11: HOW THE HEAD OF AN OPENING IS CARRIED, which on a brick house is the most
    # diagnostic thing on the wall after the bay rhythm.
    #
    # CORRECTED 27 Aug 2026, and the first version was the invented-source failure this corpus
    # names as the worst thing that can be done to it. It hardcoded `"keystone": False` with a
    # comment saying "the kit states keystone: none for this tradition", and cited
    # `brick-course.json window_head_masonry` as the source. brick-course contains the word
    # "keystone" zero times, and the claim is true of ONE style: tidewater-georgian forbids the
    # keystoned flat arch, while mid-atlantic-georgian makes it CANONICAL with a measured 6-9 in
    # keystone and a measured 4-6 in rise. The generator answered `keystone: false` and a 0.4 in
    # camber for it, in a published record, attributed to a pack that says nothing on the subject.
    #
    # It also hardened brick-course's own note -- "the change is roughly 1720-1750 IN THE
    # CHESAPEAKE" -- into a global `< 1750` point test. A band is not a threshold and a regional
    # observation is not a universal one, so a date inside the band now says it cannot choose
    # rather than choosing, and an absent date says that too instead of reporting a definite
    # arch and a source sentence reading "the None date puts it after the change".
    #
    # The style's own kit governs; brick-course supplies dimensions the kit does not state.
    # SHUTTERS, READ FROM THE KIT rather than assumed. `tidewater-georgian` bound this slot empty
    # and the cascade delivered its parent's raised-panel-pair, so every elevation of this style
    # was drawn with shutters -- on a solid-brick Chesapeake house, where Colonial Williamsburg's
    # own report on the Ludwell-Paradise House says "None. (Being a brick building in colonial
    # times shutters appeared only in interiors.)" The gap was adjudicated in the kit on
    # 27 Aug 2026 (WP-5.13, and the OQ 51 idiom); this reads the answer.
    # THE REVEAL, read from whichever of the two slots this construction uses. A band, not a
    # figure -- 4 to 8 in on the masonry kit -- so it travels as a band and the drawing uses its
    # PRESENCE (which edges fall into shadow) rather than claiming a depth the corpus withholds.
    _rv = ((C["kits"].get(style) or {}).get("slots", {}) or {})
    _rvs = (_rv.get("reveal_masonry") if is_masonry else _rv.get("reveal_frame")) or {}
    _rvp = (_rvs.get("parameters") or {}).get("reveal") or {}
    reveal_band_in = list(_rvp["range"]) if _rvp.get("range") else (
        [_rvp["value"], _rvp["value"]] if isinstance(_rvp.get("value"), (int, float)) else None)

    # THE CASCADED dormer slot, not the raw one. `tidewater-georgian` binds this slot EMPTY --
    # exactly as it binds `shutter` -- so `C["kits"]` carries no variants, no cheek band and no
    # parity rule for it, and a check against the raw kit would let a `shed-dormer` through on a
    # style whose parent forbids it. The spec lives on `georgian-colonial-american` and reaches
    # this node only through the lineage. This is the OQ 51 cascade being READ deliberately
    # rather than tripped over.
    try:
        _g = RK.load_graph()
        _slots, _ = RK.resolve_slots(_g, RK.chain_for(_g, style), RK.scope_for(_g, style))
        dormer_slot = _slots.get("dormer") or {}
        porch_slot = _slots.get("porch_type") or {}
        pilaster_slot = _slots.get("pilaster") or {}
        # OQ 99 (WP-8.3): every slot this node's RESOLVED kit forbids. The generator reads slot
        # dimensions straight out of pack files and has never consulted the kit's strongest word.
        forbids = {sid for sid, rec in _slots.items() if rec.get("binding") == "forbidden"}
    except Exception:
        _ks = ((C["kits"].get(style) or {}).get("slots", {}) or {})
        dormer_slot = _ks.get("dormer") or {}
        porch_slot = _ks.get("porch_type") or {}
        pilaster_slot = _ks.get("pilaster") or {}
        forbids = set()   # no cascade: cannot judge, so refuse nothing and say so below

    shutter_slot = ((C["kits"].get(style) or {}).get("slots", {}) or {}).get("shutter") or {}
    _sv = {v["id"]: v.get("status") for v in shutter_slot.get("variants", [])}
    shutters_carried = bool(_sv) and _sv.get("none") != "canonical"
    if not _sv:
        shutters_carried = True          # nothing stated: the older half of the corpus draws them

    head_slot = ((C["kits"].get(style) or {}).get("slots", {}) or {}).get("window_head_masonry") or {}
    head_variants = {v["id"]: v.get("status") for v in head_slot.get("variants", [])}
    head_params = head_slot.get("parameters") or {}
    CHANGE_BAND = (1720, 1750)      # brick-course's own words, as the band it states

    def _head_treatment(w_in):
        if not is_masonry:
            return None
        canonical = [k for k, v in head_variants.items() if v == "canonical"]
        arch_kinds = [k for k in canonical if "arch" in k]
        kind, why = None, None
        if len(arch_kinds) == 1:
            kind, why = arch_kinds[0], "the style's kit makes it the only canonical masonry head"
        elif len(arch_kinds) > 1:
            yr = int(str(date)[:4]) if date else None
            if yr is None:
                why = ("the kit permits more than one masonry head and this plan states no date, "
                       "so which one it is cannot be judged here")
            elif yr < CHANGE_BAND[0]:
                kind = next((k for k in arch_kinds if "segmental" in k), arch_kinds[0])
                why = f"{yr} is before brick-course's stated {CHANGE_BAND[0]}-{CHANGE_BAND[1]} change"
            elif yr > CHANGE_BAND[1]:
                kind = next((k for k in arch_kinds if "flat" in k), arch_kinds[0])
                why = f"{yr} is after brick-course's stated {CHANGE_BAND[0]}-{CHANGE_BAND[1]} change"
            else:
                why = (f"{yr} falls inside brick-course's own {CHANGE_BAND[0]}-{CHANGE_BAND[1]} "
                       f"change band, which is a band and not a threshold — unjudged")
        else:
            why = "the style's kit names no canonical masonry arch"

        # Dimensions. The kit's own measured figure wins over a pack rule derived for another
        # tradition; where the kit gives a band, the band travels rather than its midpoint.
        rise_in = rise_band = None
        kit_rise = head_params.get("arch_rise") or {}
        if isinstance(kit_rise.get("value"), (int, float)):
            rise_in, rise_src = float(kit_rise["value"]), "the style's own kit"
        elif kit_rise.get("range"):
            rise_band, rise_src = list(kit_rise["range"]), "the style's own kit, as a band"
        elif kind:
            dim = "segmental_arch_rise" if "segmental" in kind else "flat_arch_camber"
            rise_in, _ = _val(brick_pack, "window_head_masonry", {"opening_width": w_in}, dimension=dim)
            rise_in, rise_src = round(rise_in, 3), f"brick-course {dim}"
        else:
            rise_src = None
        depth, _ = _val(brick_pack, "window_head_masonry",
                        {"module": brick_pack["module"]["default_size_in"]}, dimension="height")

        out = {"kind": kind, "kind_note": why, "depth_in": round(depth, 3),
               "rise_in": rise_in, "rise_band_in": rise_band, "rise_source": rise_src,
               "source": "the style's kit for the head; brick-course for its dimensions"}
        # KEYSTONE: read, never assumed, and ABSENT where the kit is silent. Present as a
        # measured figure where the kit gives one -- mid-atlantic-georgian states 6-9 in.
        ks = head_params.get("keystone") or head_params.get("keystone_width") or {}
        if ks.get("value") == "none":
            out["keystone"] = False
        elif isinstance(ks.get("value"), (int, float)) or ks.get("range"):
            out["keystone"] = True
            out["keystone_width_in"] = ks.get("value") or list(ks["range"])
        elif any("keystoned" in k for k, v in head_variants.items() if v == "canonical"):
            out["keystone"] = True          # the variant is canonical; its width is unstated
        # else: the kit is silent, and so is this record.
        return out

    for sw in storey_windows:
        sw["head_treatment"] = _head_treatment(sw["opening_width_in"])
        sw["shutters_carried"] = shutters_carried
        sw["reveal_band_in"] = reveal_band_in
        if not shutters_carried:
            # A shutter that is not there has no leaf. Absent, not zero.
            sw["shutter_leaf_width_in"] = None
            sw["shutter_leaf_height_in"] = None
            sw["shutter_panel_count"] = None


    faces = {}
    blinded_bays = {}
    _stack_w_ft = (chimney_plan_in or 22.0) / 12.0
    for f in FACES:
        span_ft = fp["width_ft"] if f in ("S", "N") else fp["depth_ft"]
        faces[f] = _face_bays(facade_pack, span_ft, has_entrance=(f == entrance_face))
        faces[f]["outside_width_in"] = round(span_ft * 12.0, 2)
        # OQ 85: a bay a chimney stands on is BLIND. The two records -- roof.py's chimney plan
        # positions and this file's evenly spaced odd bay count -- were built from different rules
        # and nothing compared them, so a window was drawn where a stack stands.
        axes = stack_axes_for_face(f, roof.get("chimneys"), fp)
        hit = blind_bays_behind_stacks(faces[f], axes, _stack_w_ft)
        if hit:
            blinded_bays[f] = hit
            faces[f]["blind_bay_centres_ft"] = hit
            faces[f]["blind_bay_reason"] = (
                f"A chimney stack stands on {'this axis' if len(hit) == 1 else 'these axes'}: "
                f"{', '.join(str(h) for h in hit)} ft along the face, from the roof record's own "
                f"plan position. An opening there is not drawn.")

    ent = entrance_composition(op_pack, facade_pack, gibbs_pack, ground["storey_height_ft"] * 12.0,
                               forbids=forbids) if gibbs_applies else \
          entrance_composition(op_pack, facade_pack, gibbs_pack, ground["storey_height_ft"] * 12.0,
                               forbids=forbids)
    # OQ 99'S DISCLOSURE. Two of these are refused above; the rest are READ ANYWAY and this is
    # where a reader finds out. Naming them beats a silent figure: `unjudged is not passed`
    # applies to a drawing exactly as it applies to a measurement, and until WP-8.3 nothing
    # anywhere recorded that this generator had overruled a kit's strongest word.
    _READ_FROM_PACKS = ("belt_course", "casing", "chimney", "cornice", "door_surround",
                        "entry_door", "frieze", "pilaster", "shutter", "transom_sidelight",
                        "water_table", "window_grouping_rule", "window_head_masonry",
                        "window_head_wood", "window_lite_pattern", "window_proportion")
    _REFUSED_HERE = ("transom_sidelight", "pilaster")
    forbidden_read = sorted(forbids & set(_READ_FROM_PACKS))

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
        # OQ 59: None, not 0, when the roof pass did not PLACE chimneys as opposed to placing
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

    # THE DORMERS, or the stated absence of them, or the absence of a statement.
    dorm = dormers(plan, dormer_slot, faces, storey_windows[1], roof,
                   entrance_face, ground["storey_height_ft"] * 12.0,
                   cornice=cornice, casing_in=round(ent["casing_width_in"] * 0.6, 3),
                   house_wall_in=round(grade_to_true_eave_in
                                       - wtb["water_table_height_above_finished_grade_in"], 2))
    if dorm.get("count") and not dorm.get("refused"):
        # The strip of roof in front of the face, measured ON THE SLOPE -- `sunken-dormer` wants
        # at least 12 in of it and prefers 18-36, because that strip is what makes a dormer a
        # dormer rather than a wall carried up. Derived from the roof's own geometry: the face
        # stands where its own height fits under the slope with that run left below it.
        # How far the face stands back HORIZONTALLY, and how high its sill sits, both follow from
        # the setback along the slope once the pitch is known -- so the drawing places the dormer
        # from one stated figure rather than from three.
        # A DORMER NEEDS A ROOF TO STAND ON, and where the roof record could not judge one the
        # record must say so rather than the drawing quietly showing none. `spec-builder-colonial`
        # is the case: its roof has no judged pitch and no judged ridge, so `elevation_profile`
        # honestly returns a flat eave line with nothing invented above it -- and the renderer then
        # skipped every dormer with no note, while the measurements went on reporting three of them
        # to the fault corpus. The critic judged three dormers on a sheet that drew none.
        _p12 = (roof.get("main") or {}).get("pitch_rise_per_12")
        _ridge = ((roof.get("main") or {}).get("ridge") or {}).get("grade_to_ridge_ft")
        if not _p12 or _ridge is None:
            dorm["placeable"] = False
            dorm["not_drawn_reason"] = (
                "The roof record could not judge " +
                (" and ".join([x for x in (None if _p12 else "a pitch",
                                           None if _ridge is not None else "a ridge height") if x])) +
                " for this house, so there is no roof surface to place a dormer on. The dormers "
                "the record states are NOT DRAWN; they are not absent, and the count still "
                "reaches the fault corpus.")
        else:
            dorm["placeable"] = True
        if _p12:
            _rr = _p12 / 12.0
            _hyp = math.sqrt(1.0 + _rr * _rr)
            dorm["face_setback_from_eave_in"] = round(DORMER_SETBACK_ON_SLOPE_IN / _hyp, 2)
            dorm["sill_above_eave_in"] = round(DORMER_SETBACK_ON_SLOPE_IN * _rr / _hyp, 2)

    # THE DORMER MEASUREMENTS, supplied only where the plan STATES its dormers. Where it does
    # not, every one of these stays absent -- which is the distinction the whole field exists for.
    dormer_m = {}
    if dorm.get("stated") and not dorm.get("refused"):
        dormer_m["dormer_count"] = dorm.get("count", 0)
        dormer_m["sum_of_dormer_face_widths_in"] = dorm.get("sum_of_face_widths_in", 0.0)
        if dorm.get("count"):
            dormer_m.update({
                "count_of_dormers_centred_on_a_window_below": len(dorm.get("positions_ft") or []),
                "dormer_window_width_in": dorm["window_width_in"],
                "dormer_window_height_in": dorm["window_height_in"],
                "window_width_directly_below_in": storey_windows[1]["opening_width_in"],
                "visible_cheek_width_in": dorm["cheek_width_in"],
                "sash_width_in": dorm["window_width_in"],
                "finished_cheek_width_in": dorm["cheek_width_in"],
                "roof_run_in_front_of_dormer_face_measured_on_slope_in": dorm["roof_run_in_front_in"],
            })

    # OQ 84: which of two rival cornice rules judges this house. Derived from the porch and
    # pilaster slots the style actually resolves, never from `gibbs_order_applies_to_style`.
    order_at_eave, order_at_eave_note = order_at_the_eave(porch_slot, pilaster_slot,
                                                          plan.get("declared") or {})

    elev = {
        "plan_id": plan.get("id"), "style": style, "entrance_face": entrance_face,
        "dormers": dorm,
        "order_at_the_eave": order_at_eave, "order_at_the_eave_note": order_at_eave_note,
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
        # NOT a measurement, and deliberately absent from `measurements` below: brick-course
        # flags this rule `judgment: true`. It is here so the DRAWING can show a stack at the
        # corpus's own figure instead of the 36 in constant it used to assert, and so the sheet
        # can say the size is still a decision.
        "chimney_stack_plan_in": chimney_plan_in,
        "chimney_stack_plan_judgment": chimney_plan_judgment,
        "grade_to_true_eave_in": grade_to_true_eave_in, "eave_reconciliation_note": eave_reconciliation_note,
        "roof": roof_meas, "roof_record": roof,
        # OQ 99 (WP-8.3). Every slot this generator reads out of a pack file that THIS node's
        # resolved kit binds `forbidden`, and what was done about each. Two are refused outright
        # (the sidelights and the doorcase pilaster, both of which the composition already had a
        # branch for); the rest are READ ANYWAY and are named here rather than left silent.
        # Fixing those needs a semantic answer per slot -- a forbidden `frieze` on a style whose
        # kit still passes this generator's classical scope gate is a contradiction between two
        # records, not a number to zero -- and that is OQ 99's remaining half, stated rather
        # than quietly carried.
        "forbidden_slots_read_from_packs": {
            "refused": [x for x in forbidden_read if x in _REFUSED_HERE],
            "read_anyway": [x for x in forbidden_read if x not in _REFUSED_HERE],
            "note": ("This generator reaches packs by PE.resolve and never through resolve_packs, "
                     "so WP-8.3's resolver-side gate does not reach a single figure drawn here. "
                     "`read_anyway` is a measured disclosure, not a pass."),
        },
        "footprint": fp, "section": section,
    }
    elev["measurements"] = _derive_measurements(elev)
    # Folded in AFTER the NOT_MODELLED filter has run, because these are no longer refused names
    # and must not be filtered by their own former entries. setdefault, so a plan's own declared
    # measurement still wins, which is the precedence build/plan_check.py already uses.
    for _k, _v in dormer_m.items():
        if _v is not None:
            elev["measurements"].setdefault(_k, _v)
    # Absent, not zero, where nobody has decided -- and both rival secondaries of
    # cornice-that-is-a-fascia then decline rather than one of them judging on a guess.
    if order_at_eave is not None:
        elev["measurements"].setdefault(
            "an_order_is_applied_to_the_wall_carrying_the_eave_cornice", order_at_eave)
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
