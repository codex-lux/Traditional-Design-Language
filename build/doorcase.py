"""THE ENTRANCE DOORCASE, SPELLED ONCE FOR THE PLACER AND THE ELEVATION (Phase 15, WP-15.6).

Lucas, of the drawn Tidewater front (27 Sep 2026): "there's still no concept of how close windows
can be to doors". The placer seated the centre passage's south window 12 in from the door leaf,
because it reserved the leaf and a foot either side and nothing else, and the elevation then drew
the doorcase's 7.017 in casing around that leaf -- 4.98 in of brick between the casing and the
sash. The corpus states the rule, in facade-classical's `door_surround` rule for the entrance
composition's width: "It is not allowed to touch the flanking windows", and "The residual wall
each side of the entrance composition should not fall below about half the ordinary pier". Nothing
read either sentence, because the composition was computed in `elevation.py` AFTER the placement,
and `elevation.py` cannot be imported by the placer: it loads `geometry`, which loads `openings`.

So this is a LEAF, on `storeys.py`'s and `assemblies.py`'s precedent. It imports only the
proportion engine, which is a leaf itself, and it holds the arithmetic both callers need:

  * `rule`, `pack_env` and `val` -- ONE derived rule read out of a pack. These were
    `elevation._rule`, `_pack_env` and `_val`, moved here unchanged; `elevation.py` keeps the old
    names as aliases.
  * `applies` -- the elevation's own gate (a style inside opening-proportion's and
    facade-classical's `applies_to`): a doorcase exists only where the elevation draws one.
  * `composition` -- the width figures of `elevation.entrance_composition`: the leaf, the casing,
    the sidelights, the width cap and whether the sidelights fit under it.
  * `entrance_index` -- which door is the entrance: the widest, ties to the lower coordinate.
  * `stated_bay_ft` -- the bay a parti states, which the ordinary pier is measured on, or why none.
  * `residual_pier_ft` -- facade-classical's floor on the wall each side of the composition.
"""
from __future__ import annotations

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _mod(n, p):
    import sys as _sys
    if os.path.join(ROOT, "build") not in _sys.path:
        _sys.path.insert(0, os.path.join(ROOT, "build"))
    import modcache as _mc
    return _mc.load(n, p)


PE = _mod("proportion_engine", os.path.join(ROOT, "build", "proportion_engine.py"))


# ---------------------------------------------------------------- one derived rule, read out of a pack
def rule(pack, target_slot, note_substr=None, dimension=None):
    """Finds ONE derived_rules entry by target_slot (+ dimension, + a note substring where a
    pack states more than one rule for the same slot -- opening-proportion.json alone has three
    for entry_door). Picking rules this way, rather than hand-copying the expression strings a
    second time, is the same discipline WP-3.1's graduation_check() and WP-3.3's wing_step_down()
    both adopted after finding a hand-transcribed number had drifted from the pack's own text."""
    for r in pack.get("derived_rules", []):
        if r["target_slot"] != target_slot:
            continue
        if dimension and r.get("dimension") != dimension:
            continue
        if note_substr and note_substr.lower() not in (r.get("note") or "").lower():
            continue
        return r
    return None


def pack_env(pack, module_in=None):
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


def val(pack, target_slot, env, note_substr=None, dimension=None, clip=True, module_in=None):
    r = rule(pack, target_slot, note_substr=note_substr, dimension=dimension)
    if not r:
        return None, None
    full_env = {**pack_env(pack, module_in), **env}
    v = PE.evaluate_expr(r["expression"], full_env)
    v = float(v)
    in_range = None
    if clip and r.get("range"):
        lo, hi = r["range"]
        in_range = lo <= v <= hi
    return v, {"rule": r, "value": v, "in_range": in_range}


# ---------------------------------------------------------------- whether there is a doorcase at all
def applies(style, op_pack, facade_pack):
    """The elevation's own gate, and so whether a doorcase is drawn at all: a DIRECT membership
    check (the style in the pack's `applies_to`, or "universal") on both packs whose rules compose
    the front. 118 of the 159 styles with a kit fall outside it and get no elevation; a placer that
    reserved a doorcase for them would move a placement for a drawing nobody makes."""
    def _direct(pack):
        return "universal" in pack.get("applies_to", []) or style in pack.get("applies_to", [])
    return _direct(op_pack) and _direct(facade_pack)


def forbidden_of(slots):
    """Every slot a RESOLVED kit binds forbidden (`oq/forbidden-stops-the-pack-cascade`, WP-8.3).
    The composition drops the sidelights where `transom_sidelight` is among them."""
    return {sid for sid, rec in (slots or {}).items() if (rec or {}).get("binding") == "forbidden"}


# ---------------------------------------------------------------- the composition's width
def composition(op_pack, facade_pack, ground_storey_height_in, forbids=()):
    """The width of the entrance composition, as `elevation.entrance_composition` composes it: the
    storey-derived leaf, the casing each side, the sidelights each side where the kit does not
    forbid them and the whole fits facade-classical's width cap, and whether it does.

    A FORBIDDEN SIDELIGHT HAS NO WIDTH: where the resolved kit binds `transom_sidelight`
    FORBIDDEN the figures are ABSENT rather than zero and no cap is consulted."""
    door_w, door_w_r = val(op_pack, "entry_door", {"storey_height": ground_storey_height_in},
                           note_substr="door from the storey", dimension="width")
    casing_w, _ = val(op_pack, "door_surround", {"module": door_w}, dimension="width")
    sidelights_forbidden = "transom_sidelight" in forbids
    if sidelights_forbidden:
        sidelight_w = transom_h = None
    else:
        sidelight_w, _ = val(op_pack, "transom_sidelight", {"module": door_w}, dimension="width")
        transom_h, _ = val(op_pack, "transom_sidelight", {"module": door_w}, dimension="height")
    with_sidelights_in = None if sidelights_forbidden else door_w + 2 * sidelight_w + 2 * casing_w
    without_sidelights_in = door_w + 2 * casing_w
    # OQ 48: `door_surround`/`width` held two quantities -- an architrave's own face width and the
    # MAXIMUM WIDTH OF THE WHOLE ENTRANCE COMPOSITION, which is what this cap has always meant.
    comp_cap_in, _ = val(facade_pack, "door_surround",
                         {"module": facade_pack["module"]["default_size_in"]},
                         dimension="entrance_composition_total_width")
    use_sidelights = (not sidelights_forbidden) and with_sidelights_in <= comp_cap_in
    return {"door_w_in": door_w, "door_w_rule": door_w_r, "casing_w_in": casing_w,
            "sidelight_w_in": sidelight_w, "transom_h_in": transom_h,
            "sidelights_forbidden": sidelights_forbidden,
            "with_sidelights_in": with_sidelights_in, "without_sidelights_in": without_sidelights_in,
            "cap_in": comp_cap_in, "use_sidelights": use_sidelights,
            "composition_w_in": with_sidelights_in if use_sidelights else without_sidelights_in}


# ---------------------------------------------------------------- which door is the entrance
def entrance_index(doors):
    """The index of the entrance among `doors`, each `(width_ft, u_ft)` on the entrance face at the
    ground storey: THE WIDEST, and where two are equally wide the one at the lower coordinate
    (`axis.door_bay`'s rule, which the elevation restates because that function returns no door on
    an even bay count). None where there is no door. The elevation hands it the face's own `u`; the
    placer hands it the plan coordinate along the wall, which runs the same way while no face is
    mirrored (`elevation.FACE_MIRRORED`), and a test holds the two to one door on every plan."""
    if not doors:
        return None
    return max(range(len(doors)), key=lambda i: (doors[i][0], -doors[i][1]))


# ---------------------------------------------------------------- the wall each side of the composition
# facade-classical's `door_surround` rule for the entrance composition's width, in its
# authority_note: "The residual wall each side of the entrance composition should not fall below
# about half the ordinary pier; below that the flanking windows begin to read as part of the
# doorway." The fraction is PROSE in the pack, not an expression, so it is transcribed here once;
# tests/test_doorcase.py holds this constant to that sentence, so an edit to the pack's words fails
# rather than leaving a stale figure.
RESIDUAL_FRACTION_OF_THE_ORDINARY_PIER = 0.5

# THE MODULE THE ORDINARY PIER IS MEASURED ON, AND WHEN THERE IS NONE. The ordinary pier is one bay
# less one opening, so it needs a bay; the placer lays every house on one (`footprint.bay_module_ft`),
# and where no parti states it that bay is the placer's own 10 ft default (WP-14.4,
# `geometry_report.bay_module.stated_by` null). A floor computed off a default is a convention
# wearing a rule's authority, so the residual is NOT JUDGED there, and the one sentence below says so
# on the placer's record, the sheet and the DXF alike.
UNSTATED_BAY = ("no parti states the bay module this plan is laid on, so the ordinary pier has no "
                "module to be measured on")


def stated_bay_ft(placed):
    """`(bay_ft, None)` where a parti states the bay module a placed record is laid on, else
    `(None, why)`. Three states, never two: a record whose report does not say who stated its bay
    cannot be told from one whose bay is the default, and neither is a bay anybody stated."""
    fp = (placed or {}).get("footprint") or {}
    bay = fp.get("bay_module_ft")
    if not bay:
        return None, "the placed record states no bay module"
    bm = ((placed or {}).get("geometry_report") or {}).get("bay_module")
    if not bm:
        return None, "the placed record does not say who states its bay module"
    if bm.get("stated_by") is None:
        return None, UNSTATED_BAY
    return float(bay), None


def residual_pier_ft(facade_pack, bay_ft, opening_w_ft):
    """The least wall each side of the entrance composition beside an opening `opening_w_ft` wide,
    on a front whose bay is `bay_ft`: half the ORDINARY pier, which is facade-classical's own
    `window_grouping_rule` pier (`module - opening_width`, the module being one bay). None where
    the pack states no such rule. The caller decides what an unstated bay means; this does not."""
    pier_in, _ = val(facade_pack, "window_grouping_rule",
                     {"module": bay_ft * 12.0, "opening_width": opening_w_ft * 12.0},
                     dimension="pier_width", clip=False)
    if pier_in is None:
        return None
    return max(0.0, pier_in * RESIDUAL_FRACTION_OF_THE_ORDINARY_PIER) / 12.0
