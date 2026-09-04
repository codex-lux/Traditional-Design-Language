#!/usr/bin/env python3
"""WP-3.3 -- roof geometry.

Takes a plan already walled and sectioned by build/structure.py (outside-to-outside footprint,
storey heights, a grade-to-eave/grade-to-ridge estimate under the single-ridge simplification
that file's own roof_heights() states plainly) and derives what that file deliberately did not
attempt: the roof's actual FORM -- gable, hip, gambrel, cross-gable -- as real plan-view outline
geometry and a per-face elevation silhouette, the dependency-and-hyphen ridge step-down applied
to a subordinate wing, chimney placement and height against the style's own structural
constraint, and three photograph-corpus checks that are naturally a roof-layer concern (the Cape
eave-to-sill relation, the gambrel break, dormer rhythm against the bay grid).

Every height number this file adds is built ON TOP of structure.py's own grade_to_eave_ft (and,
for the forms where the single-ridge simplification already gives the right answer -- hip and
any single-ridge gable, see the module docstring's own geometry note below -- grade_to_ridge_ft
too), never re-derived independently, so the two files cannot silently disagree about the same
building's height. Where this file's own geometry genuinely produces a different ridge height
(gambrel, cross-gable) that divergence is stated in the record's own note, not silently swapped
in as if it had always been the number.

  python3 build/roof.py plans/tidewater-georgian-careful.json [--parti ID] \
      [--out plans/<id>.roof.json] [--svg dist/<id>-roof.svg]
"""
from __future__ import annotations
import json, os, math, re, sys, argparse, importlib.util

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
C = PC.load_corpus()

# DEFAULT_ROOF_FORM moved to build/threshold.py with roof_form_for, its only reader. A
# second copy of a default here is how two files come to disagree about the same building.
DEFAULT_CHIMNEY_HEIGHT_ABOVE_RIDGE_IN = 72.0   # matches storey-graduation-adjacent kit default seen on tidewater-georgian's own chimney slot
# Gambrel geometry has no single universal migrated constraint the way roof_pitch_rise_per_12
# does -- but the SAME numbers ("lower slope 60-72 degrees, upper slope 18-30 degrees, break at
# 55-70% of the half-span") appear, independently authored, in both dutch-colonial-american.c03
# and new-jersey-dutch-gambrel.c01's own statement prose. Two independently-written style nodes
# agreeing on the same figures is itself evidence this is the family's real sourced number, not
# one style's private judgment -- used here as the fallback for any style that does not carry
# its own migrated roof_slope_lower_deg constraint (see _style_gambrel_geometry).
GAMBREL_LOWER_SLOPE_DEFAULT_DEG = 66.0   # midpoint of 60-72
GAMBREL_UPPER_SLOPE_DEFAULT_DEG = 24.0   # midpoint of 18-30
GAMBREL_BREAK_FRACTION_DEFAULT = 0.625   # midpoint of 55-70% of the half-span
WING_RIDGE_RATIO_DEFAULT = 0.7           # midpoint of dependency-and-hyphen.json's own 0.6-0.8 band

FACES = ("S", "N", "E", "W")

# ---------------------------------------------------------------- helpers duplicated by design
# _style_roof_pitch is byte-for-byte the same logic as build/structure.py's own function of the
# same name. Duplicated rather than imported -- this file is loaded standalone via _mod(), the
# same reason build/geometry.py's lot_usable_width_ft and build/structure.py's own
# _shared_segment are each a second, independent copy rather than a cross-module import.
def _style_roof_pitch(style):
    node = C["styles"].get(style, {})
    for c in node.get("constraints", []):
        t = c.get("test") or {}
        if t.get("expression") != "roof_pitch_rise_per_12": continue
        if t.get("direction") == "between":
            return (t["threshold"] + t["upper"]) / 2.0, c["id"], f"{t['threshold']}:12 to {t['upper']}:12"
        if t.get("direction") in ("at-least", "at-most"):
            return float(t["threshold"]), c["id"], f"{t['direction']} {t['threshold']}:12"
    return None, None, None

def _between_range(pack_test):
    """Pulls (threshold, upper) off a structured {expression, direction:'between', threshold,
    upper} test dict -- the same shape faults/*.json and styles/*.json constraints both use."""
    if pack_test and pack_test.get("direction") == "between":
        return float(pack_test["threshold"]), float(pack_test["upper"])
    return None

def _parse_prose_between(statement, var_hint=None):
    """groupings/*.json's own internal_rules carry their test as a plain sentence
    ('dependency_ridge_ft / main_ridge_ft between 0.6 and 0.8'), not the structured
    {expression, direction, threshold, upper} object faults and style constraints use -- there
    is no schema for grouping-level tests in this corpus. Rather than hand-transcribe the two
    numbers a second time (structure.py's graduation_check() bug #3 was exactly that mistake),
    pull them out of the sentence itself, so a future edit to the grouping file's own wording is
    what this reads, not a copy of it made once and then stale.

    THE PARSER ITSELF MOVED TO build/arrangement.py (WP-9.1), which had to read all four forms
    these rules use -- `between`, `at-least`, `at-most`, `equals` -- to evaluate the nineteen
    hard grouping rules nothing had ever run. This one handled `between` alone. Two parsers for
    one sentence form is the defect this codebase has been bitten by three times, so this
    delegates and keeps its own (lo, hi) return shape for its callers. The local regex remains
    only as the fallback for a tree where arrangement.py cannot be loaded."""
    try:
        b = os.path.join(ROOT, "build")
        if b not in sys.path:
            sys.path.insert(0, b)
        import modcache as _mc
        _arr = _mc.load("arrangement", os.path.join(ROOT, "build", "arrangement.py"))
        p = _arr.parse_rule_test(statement)
        if p and p.get("direction") == "between":
            return float(p["threshold"]), float(p["upper"])
        if p:
            return None
    except Exception:
        pass
    m = re.search(r"between\s+([\d.]+)\s+and\s+([\d.]+)", statement or "")
    if not m: return None
    return float(m.group(1)), float(m.group(2))

def _fallback_band(fell_back, label, band):
    """Record that a corpus lookup missed and a hardcoded band answered in its place (OQ 52).

    Every band in this file is read off the corpus by matching a rule's exact wording -- a
    fault's `expression` string, or the 'between X and Y' in a grouping's prose. A reworded
    rule misses silently, and the fallback beside each lookup then answers with numbers that
    are byte-identical to today's corpus values. That identity is exactly what makes the rot
    undetectable: the record still reports `computed: True` and names the corpus file as its
    evidence, so a stale copy reads as a live reading.

    The fallbacks are kept -- a check that refuses to run is worse than one that says where it
    read from -- but a run that used one now says so, in `bands_read_from_fallback` on its own
    record, and `check_all`'s roof pass prints it. If that list is ever non-empty on a plan the
    corpus does cover, a rule has been reworded and this file did not notice."""
    fell_back.append(label)
    return band

def _grouping(gid):
    return json.load(open(f"{ROOT}/groupings/{gid}.json"))

def _massing(massing_id):
    return C["massings"].get(massing_id, {})

# ---------------------------------------------------------------- roof form
# MOVED TO build/threshold.py (WP-11.4) AND RE-EXPORTED HERE UNDER THE OLD NAMES.
# `roof_form_for` and the ridge axis are pure functions of the plan and the massing -- no
# section, no structure, no ridge height -- and the PLACEMENT layer needs the axis to know
# which two walls are the gable ends before any of this file's machinery exists. Spelling
# that arithmetic a second time down there is the failure this corpus meets most often, so
# there is one spelling and this file reads it. `tests/test_threshold_pass.py` holds the
# whole of build_roof's output over both shipped plans, all fourteen reference plans and a
# 164-style sweep byte-identical across the move.
_TH = None


def _threshold():
    global _TH
    if _TH is None:
        _TH = _mod("threshold", f"{ROOT}/build/threshold.py")
    return _TH


def roof_form_for(plan, massing):
    return _threshold().roof_form_for(plan, massing)


# ---------------------------------------------------------------- main-volume geometry
def _rect_face_axis(form):
    return _threshold().ridge_axis(form)


def main_roof(plan, section, style):
    """The primary roof volume over the whole footprint. Reuses structure.py's own
    grade_to_eave_ft/grade_to_ridge_ft for every form where its single-ridge-over-the-shorter-
    dimension simplification is already the right answer (gable and hip alike -- a symmetric hip
    and a symmetric gable roof of the same footprint and pitch share the same ridge HEIGHT; only
    the plan-view outline differs, see roof_outline()/elevation_profile() below). Gambrel is the
    one form whose ridge height genuinely differs from that simplification, computed
    independently and reconciled explicitly rather than silently substituted."""
    fp = section["footprint"]
    W, D = fp["width_ft"], fp["depth_ft"]
    massing = _massing(plan.get("massing"))
    form, form_note = roof_form_for(plan, massing)
    pitch, pitch_id, pitch_stmt = _style_roof_pitch(style)
    eave_ft = section["roof"]["grade_to_eave_ft"]

    result = {"form": form, "form_note": form_note, "pitch_rise_per_12": pitch,
              "pitch_source": pitch_id, "pitch_statement": pitch_stmt, "grade_to_eave_ft": eave_ft}

    if form in ("gable", "side-gable", "front-gable", "hip", "gable-on-hip", "cross-gable"):
        axis = _rect_face_axis(form if form != "cross-gable" else "side-gable")
        ridge_len_dim, span_dim = (W, D) if axis == "x" else (D, W)
        if form in ("hip", "gable-on-hip"):
            ridge_from, ridge_to = (D / 2.0, W - D / 2.0) if axis == "x" and W >= D else (0.0, ridge_len_dim)
            # A hip roof needs its own dimension to actually be longer than the one it hips in
            # from, or there is no ridge at all (a square hip has a single apex, not a ridge
            # line) -- flagged rather than producing a negative-length ridge silently.
            if W < D:
                ridge_from, ridge_to = 0.0, 0.0
                result["note"] = f"Footprint {W:.1f}x{D:.1f} ft is deeper than it is wide; hip form here needs its own re-derivation (ridge runs the other axis) -- not modelled, ridge collapsed to a point."
        else:
            ridge_from, ridge_to = 0.0, ridge_len_dim
        ridge_ft = section["roof"].get("grade_to_ridge_ft")
        result["ridge"] = {"axis": axis, "position_ft": span_dim / 2.0, "from_ft": round(ridge_from, 2),
                            "to_ft": round(ridge_to, 2), "grade_to_ridge_ft": ridge_ft}
        if ridge_ft is None:
            result["note"] = (result.get("note") or "") + " " + (section["roof"].get("note") or "")
        if form in ("hip", "gable-on-hip"):
            result["hip_lines"] = _hip_lines(W, D, axis, ridge_from, ridge_to)
        if form == "cross-gable":
            result["cross"] = _cross_gable(plan, section, W, D, axis, pitch, eave_ft)

    elif form == "gambrel":
        result.update(_gambrel(plan, section, style, W, D, eave_ft, pitch))

    else:
        result["note"] = f"Roof form '{form}' is not one of gable/hip/gambrel/cross-gable -- geometry not modelled; grade_to_eave_ft is the only number this file adds for it."

    result["openings"] = _roof_openings(plan)
    return result


def _roof_openings(plan):
    """Reserved voids that are open to the sky, as holes in the roof volume above (OQ 55).

    Stated, not modelled -- and the distinction is the point. This file computes ONE ridge over
    one rectangle; a court cuts that volume into ranges with their own eaves, valleys and
    (in the Spanish and Mediterranean cases) inward-falling pitches draining to the court. None
    of that is derived here, and pretending it were would be worse than saying so: every height
    above is computed as if the roof spanned the whole block, which over the court it does not.
    What this DOES do is put the hole in the record with its own dimensions, so no reader and no
    downstream pass can take the single-ridge figures for a complete description of the roof."""
    holes = []
    for lv in plan.get("levels", []):
        for r in lv.get("rooms", []):
            g = r.get("geometry") or {}
            v = g.get("void")
            if not v or v.get("roofed"): continue
            holes.append({"room": r["id"], "name": r.get("name") or r["id"],
                          "x_ft": g["x_ft"], "y_ft": g["y_ft"],
                          "width_ft": g["width_ft"], "depth_ft": g["depth_ft"],
                          "area_sf": g.get("area_sf")})
    if not holes:
        return {"count": 0, "rooms": [], "note": "No opening in the roof volume."}
    return {"count": len(holes), "rooms": holes,
            "note": ("SCHEMATIC, and knowingly incomplete here: the roof volume above has a hole "
                     "in it. Every ridge and eave figure in this record was computed for a single "
                     "ridge over the whole rectangle, which over an open court it is not -- the "
                     "real roof is ranges around the void, each with its own eave, meeting in "
                     "valleys, and in the Spanish and Mediterranean cases falling inward to drain "
                     "to the court. That geometry is not derived by this file. The opening's own "
                     "dimensions are recorded so nobody reads the single-ridge numbers as a "
                     "complete description of the roof (OQ 55).")}

def _hip_lines(W, D, axis, ridge_from, ridge_to):
    """Four diagonal hip lines, each running from a footprint corner to the nearest ridge
    endpoint. Plan-view segments only (x,y in the footprint plane) -- height is implied by the
    same eave-to-ridge rise every other roof line in this file already carries."""
    if axis == "x":
        corners = [(0.0, 0.0), (W, 0.0), (W, D), (0.0, D)]
        ends = [(ridge_from, D / 2.0), (ridge_to, D / 2.0)]
        pairs = [(corners[0], ends[0]), (corners[3], ends[0]), (corners[1], ends[1]), (corners[2], ends[1])]
    else:
        corners = [(0.0, 0.0), (W, 0.0), (W, D), (0.0, D)]
        ends = [(W / 2.0, ridge_from), (W / 2.0, ridge_to)]
        pairs = [(corners[0], ends[0]), (corners[1], ends[0]), (corners[2], ends[1]), (corners[3], ends[1])]
    return [{"x1": round(a[0], 2), "y1": round(a[1], 2), "x2": round(b[0], 2), "y2": round(b[1], 2)} for a, b in pairs]

def _cross_gable(plan, section, W, D, main_axis, pitch, eave_ft):
    """A single perpendicular cross-gable wing, centred on the main ridge, one bay module wide.
    Deliberately simplified -- see docs/structure.md's roof section, 'What was deliberately not
    done': no valley-line geometry between the two volumes is computed, only the two ridges
    themselves, because this corpus's own plan/geometry layer solves one rectangular footprint
    and has no second volume to actually cut a valley against."""
    bay_ft = section["footprint"].get("bay_module_ft") or section["geometry"]["footprint"].get("bay_module_ft") or 10.0
    cross_width_ft = min(bay_ft, (D if main_axis == "x" else W) * 0.9)
    rise_ft = (cross_width_ft / 2.0) * (pitch / 12.0) if pitch else None
    cross_ridge_ft = eave_ft + rise_ft if rise_ft is not None else None
    centre = (W / 2.0, D / 2.0)
    if main_axis == "x":
        line = {"x1": round(centre[0], 2), "y1": round(centre[1] - cross_width_ft / 2, 2),
                "x2": round(centre[0], 2), "y2": round(centre[1] + cross_width_ft / 2, 2)}
    else:
        line = {"x1": round(centre[0] - cross_width_ft / 2, 2), "y1": round(centre[1], 2),
                "x2": round(centre[0] + cross_width_ft / 2, 2), "y2": round(centre[1], 2)}
    return {"width_ft": round(cross_width_ft, 2), "ridge_line": line, "grade_to_ridge_ft": round(cross_ridge_ft, 2) if cross_ridge_ft else None,
            "note": "Simplified: a single centred cross-gable wing, no valley geometry against the main roof -- this plan/geometry layer has no second real volume to cut a valley against."}

def _style_gambrel_geometry(style):
    """Prefers the style's OWN migrated roof_slope_lower_deg constraint (dutch-colonial-
    american.c03 is the worked example: a 'between' test, 60-72 deg) over the family-wide
    fallback numbers this module's own constants document -- same precedence discipline
    _style_roof_pitch already uses for the single-pitch case."""
    node = C["styles"].get(style, {})
    lower = upper = break_frac = None
    lower_source = upper_source = break_source = "default (family-wide, see module docstring)"
    for c in node.get("constraints", []):
        t = c.get("test") or {}
        if t.get("expression") == "roof_slope_lower_deg":
            rng = _between_range(t)
            if rng: lower = sum(rng) / 2.0; lower_source = c["id"]
        if t.get("expression") == "roof_slope_upper_deg":
            rng = _between_range(t)
            if rng: upper = sum(rng) / 2.0; upper_source = c["id"]
    if lower is None: lower = GAMBREL_LOWER_SLOPE_DEFAULT_DEG
    if upper is None: upper = GAMBREL_UPPER_SLOPE_DEFAULT_DEG
    if break_frac is None: break_frac = GAMBREL_BREAK_FRACTION_DEFAULT
    return {"lower_slope_deg": lower, "lower_source": lower_source,
            "upper_slope_deg": upper, "upper_source": upper_source,
            "break_fraction": break_frac, "break_source": break_source}

def _gambrel(plan, section, style, W, D, eave_ft, single_pitch):
    """Two slopes per side, ridge along the same axis a side-gable roof would use. Genuinely
    recomputes grade_to_ridge_ft rather than reusing structure.py's single-pitch estimate --
    reconciled explicitly in the returned note, not silently swapped in."""
    geo = _style_gambrel_geometry(style)
    half_span_ft = min(W, D) / 2.0
    break_offset_ft = half_span_ft * geo["break_fraction"]
    lower_rise_ft = break_offset_ft * math.tan(math.radians(geo["lower_slope_deg"]))
    upper_run_ft = half_span_ft - break_offset_ft
    upper_rise_ft = upper_run_ft * math.tan(math.radians(geo["upper_slope_deg"]))
    break_grade_ft = eave_ft + lower_rise_ft
    ridge_grade_ft = break_grade_ft + upper_rise_ft
    axis = "x" if W >= D else "y"
    span_dim = D if axis == "x" else W
    ridge_len_dim = W if axis == "x" else D
    single_pitch_ridge_ft = section["roof"].get("grade_to_ridge_ft")
    note = None
    if single_pitch_ridge_ft is not None:
        note = (f"Recomputed for the gambrel's own two-slope geometry: {ridge_grade_ft:.2f} ft, "
                f"vs structure.py's single-pitch estimate of {single_pitch_ridge_ft:.2f} ft (which assumes one "
                f"straight slope at the style's roof_pitch_rise_per_12 constraint, not this form). This file's "
                f"number is the one that reflects the actual gambrel form; structure.py's own section record is "
                f"not edited by this file.")
    return {
        "ridge": {"axis": axis, "position_ft": span_dim / 2.0, "from_ft": 0.0, "to_ft": round(ridge_len_dim, 2),
                  "grade_to_ridge_ft": round(ridge_grade_ft, 2)},
        "gambrel": {**geo, "half_span_ft": round(half_span_ft, 2), "break_offset_ft": round(break_offset_ft, 2),
                    "break_grade_to_ft": round(break_grade_ft, 2)},
        "note": note,
    }

# ---------------------------------------------------------------- dependency-and-hyphen wing
def wing_step_down(plan, section, main):
    """Schematic only, and explicitly labelled so: this corpus's plan/geometry layer
    (build/geometry.py) solves a single rectangular footprint and has never placed a real second
    volume, so there is no actual wing footprint to measure. When plan.groupings names
    'dependency-and-hyphen' this still computes and CHECKS the ridge step-down rule the grouping
    states, using a schematic wing depth (one bay module) and its own hyphen-length band, so the
    rule is exercised and tested even though neither shipped reference plan currently triggers
    the real path (see docs/structure.md's own honesty precedent for the WP-3.1 framing_basis
    finding -- this is the same shape of disclosure)."""
    if "dependency-and-hyphen" not in (plan.get("groupings") or []):
        return {"applicable": False}
    grp = _grouping("dependency-and-hyphen")
    ridge_rule = next((r for r in grp["internal_rules"] if r.get("test", "").startswith("dependency_ridge_ft")), None)
    hyphen_rule = next((r for r in grp["internal_rules"] if r.get("test", "").startswith("hyphen_length_ft")), None)
    fell_back = []
    ridge_band = (_parse_prose_between(ridge_rule["test"]) if ridge_rule else None) \
        or _fallback_band(fell_back, "dependency-and-hyphen: dependency_ridge_ft band", (0.6, 0.8))
    hyphen_band = (_parse_prose_between(hyphen_rule["test"]) if hyphen_rule else None) \
        or _fallback_band(fell_back, "dependency-and-hyphen: hyphen_length_ft band", (12.0, 20.0))
    ratio = WING_RIDGE_RATIO_DEFAULT if ridge_band[0] <= WING_RIDGE_RATIO_DEFAULT <= ridge_band[1] else sum(ridge_band) / 2.0

    main_ridge_ft = main.get("ridge", {}).get("grade_to_ridge_ft")
    pitch = main.get("pitch_rise_per_12")
    if main_ridge_ft is None or pitch is None:
        return {"applicable": True, "computed": False,
                "note": "Plan names a dependency-and-hyphen grouping but the main roof has no judged ridge height or pitch to step a wing down from."}

    wing_ridge_ft = round(main_ridge_ft * ratio, 2)
    bay_ft = section["footprint"].get("bay_module_ft") or 10.0
    wing_depth_ft = bay_ft
    wing_eave_ft = round(wing_ridge_ft - (wing_depth_ft / 2.0) * (pitch / 12.0), 2)
    hyphen_length_ft = round(sum(hyphen_band) / 2.0, 2)
    computed_ratio = round(wing_ridge_ft / main_ridge_ft, 4)
    # THE VERDICT IS UNJUDGED, AND IT MUST BE: this check could not fail (3 Sep 2026).
    # `ratio` two lines above is CHOSEN to sit inside `ridge_band` -- the default when the band
    # admits it, the band's own midpoint otherwise -- and `wing_ridge_ft` is then main x ratio.
    # So `computed_ratio` is `ratio` back again to four places, and testing it against the band it
    # was drawn from returned True by construction, on every plan, for as long as the function has
    # existed. That is a pass on a figure nobody measured: the OQ 52 family, and the one thing
    # `unjudged is not passed` most forbids. The schematic figures are kept and still drawn --
    # a reader is better served by a labelled sketch than by a blank -- but the RULE reports
    # could-not-evaluate, in this file's own established shape for that (`ok: None`, as the dormer
    # check returns when no bay count exists). It becomes judgeable when the geometry layer places
    # a real second volume, which is `oq/the-parti-dissolved-its-own-dependencies`'s own subject;
    # until then there is no measured wing ridge for the ratio to be a ratio OF.
    ok = None
    return {
        "applicable": True, "computed": True, "schematic": True,
        "main_ridge_grade_ft": main_ridge_ft, "wing_ridge_grade_ft": wing_ridge_ft, "wing_eave_grade_ft": wing_eave_ft,
        "wing_depth_ft": wing_depth_ft, "hyphen_length_ft": hyphen_length_ft,
        "ratio": computed_ratio, "ratio_band": list(ridge_band), "ok": ok,
        "unjudged_reason": ("the wing ridge is derived from the band this rule tests it against, so a verdict "
                            "would be circular; no placed second volume exists to measure one from"),
        "bands_read_from_fallback": fell_back,
        "note": ("SCHEMATIC AND UNJUDGED: this corpus's geometry solver never places a real second volume, so "
                 "wing_depth_ft is assumed (one bay module) rather than measured off a placed room, and "
                 "wing_ridge_ft is DERIVED from dependency-and-hyphen.json's own 0.6-0.8 band rather than "
                 "measured. The figures are drawn as a labelled sketch; the ratio is reported and deliberately "
                 "not judged, because a rule tested against the band its own input came from cannot fail."),
    }

# ---------------------------------------------------------------- chimneys
def chimney_positions(plan, style, section, main):
    """Placement source, in order: THE NODE'S OWN kit `chimney` slot canonical variant
    (tidewater-georgian's is fully specified -- gable-end-exterior, paired-and-joined-by-arched-
    curtain) -- NOT the cascade, and the block below says why that is deliberate rather than an
    oversight; falling back to the massing's own `hearth` field (four-over-four's is
    'gable-end-paired', which every style using that massing inherits structurally whether or
    not its own kit has gotten around to a chimney slot -- colonial-revival's kit chimney slot is
    still `status: empty`, exactly the 'unjudged' case this fallback exists for)."""
    # THE NODE'S OWN KIT, DELIBERATELY, AND THE DOCSTRING ABOVE NOW SAYS SO. The WP-8.4
    # adversarial audit changed this to read the CASCADE -- the docstring had claimed the
    # resolved kit since it was written, and 64 of 164 styles state a canonical chimney only
    # through their lineage -- and then measured what that draws. It is worse, and the reason
    # is the distinction this file should be read for:
    #
    #   An inherited `forbidden` is a prohibition an ancestor made and the descendant never
    #   overturned. An inherited CANONICAL VARIANT is a positive claim the descendant never
    #   made. The first is safe to read from the cascade. The second is not, until somebody
    #   has adjudicated the slot on that node.
    #
    # `colonial-revival` states nothing about chimneys, so the cascade hands it
    # `tall-multiple-vertical-accent` from `british-picturesque` -- a Gothic Revival clustered
    # stack, "thin and numerous and well out of proportion" -- seven steps up. Reading it put
    # a Gothic stack on `spec-builder-colonial`, one of the two shipped plans, and took its
    # placed positions from 1 to 0. Its own record says nothing that would let it be bound
    # honestly, so there is no fix at the node either. The massing's `hearth`
    # (`gable-end-paired`) is the better answer and is what the fallback already produced.
    #
    # OQ 87's mechanism throughout, and the reason `oq/the-raw-kit-read` is not a
    # change-six-call-sites job: flipping a reader before the slot is adjudicated moves a
    # wrong answer INTO the drawing. `build/plan_check.py` reads the cascade and keeps it,
    # because it reads only `forbidden`.
    slots = (C["kits"].get(style, {}).get("slots") or {})
    canonical = [v["id"] for v in ((slots.get("chimney") or {}).get("variants") or [])
                 if v.get("status") == "canonical"]
    massing = _massing(plan.get("massing"))
    hearth = massing.get("hearth")
    source = f"kit chimney slot: {', '.join(canonical)}" if canonical else (f"massing '{massing.get('id')}' hearth: {hearth}" if hearth else None)
    gable_end = bool(canonical and any("gable-end" in v for v in canonical)) or (hearth and "gable-end" in hearth)

    form = main.get("form")
    ridge = main.get("ridge")
    if not source:
        return {"applicable": False, "positions": [], "source": None,
                "note": "No kit chimney slot and no massing hearth field to place chimneys from -- unjudged."}
    if not gable_end:
        return {"applicable": True, "positions": [], "source": source,
                "note": f"Placement source ({source}) does not call for a gable-end chimney -- not placed by this file."}
    if not ridge or ridge.get("grade_to_ridge_ft") is None:
        return {"applicable": True, "positions": [], "source": source,
                "note": (f"Placement source calls for gable-end chimneys ({source}), but the main roof has no "
                         f"judged ridge height to measure a chimney's total height against -- unjudged, not placed.")}

    if form in ("hip", "gable-on-hip"):
        return {"applicable": True, "positions": [], "source": source,
                "note": (f"Placement source calls for gable-end chimneys ({source}), but the roof form here is "
                         f"'{form}', which has no full gable-end wall to run a stack through -- a real design "
                         f"would need an interior or off-ridge chimney solution this file does not model. "
                         f"Flagged rather than silently placed at a wall that is not actually a gable end.")}

    params = ((slots.get("chimney") or {}).get("parameters") or {})
    band = params.get("height_above_ridge_band", {}).get("range")
    height_above_ridge_in = sum(band) / 2.0 if band else (params.get("height_above_ridge_min", {}).get("value") or DEFAULT_CHIMNEY_HEIGHT_ABOVE_RIDGE_IN)

    W, D = section["footprint"]["width_ft"], section["footprint"]["depth_ft"]
    axis, ridge_ft = ridge["axis"], ridge["grade_to_ridge_ft"]
    # ONE spelling of the two gable-end points, in build/threshold.py, read by this file for
    # the stack's HEIGHT and by the placement layer for its PLAN (WP-11.4).
    positions = _threshold().gable_end_points(W, D, axis)

    style_constraint = next((c for c in C["styles"].get(style, {}).get("constraints", [])
                              if (c.get("test") or {}).get("expression") == "chimney_height_above_ridge_ft"), None)
    height_above_ridge_ft = round(height_above_ridge_in / 12.0, 3)
    check = None
    if style_constraint:
        t = style_constraint["test"]
        ok = height_above_ridge_ft >= t["threshold"] if t.get("direction") == "at-least" else None
        check = {"constraint_id": style_constraint["id"], "threshold_ft": t.get("threshold"), "direction": t.get("direction"), "ok": ok}

    chimneys = [{"x_ft": round(x, 2), "y_ft": round(y, 2), "grade_to_ridge_ft": ridge_ft,
                 "height_above_ridge_ft": height_above_ridge_ft, "total_height_grade_ft": round(ridge_ft + height_above_ridge_ft, 2)}
                for x, y in positions]
    return {"applicable": True, "positions": chimneys, "source": source, "style_check": check}

# ---------------------------------------------------------------- Cape eave-to-sill, dormers
def _fault(fid):
    return json.load(open(f"{ROOT}/faults/{fid}.json"))

def cape_eave_check(style, section, main):
    """faults/raised-cape-eave.json's own severity_by_style names which styles this measurement
    is the TYPE's defining one (severity 'fatal') versus merely relevant -- read from that file
    rather than a hand-picked style list, so an editorial change to the fault's severity_by_style
    is what this reads, not a second copy of the same judgment."""
    fault = _fault("raised-cape-eave")
    fatal_styles = {e["style"] for e in fault.get("severity_by_style", []) if e.get("severity") == "fatal"}
    if style not in fatal_styles:
        return {"applicable": False}
    ground = next((s for s in section["storeys"] if s.get("index") == 0), None)
    if not ground or ground.get("grade_to_floor_ft") is None:
        return {"applicable": True, "computed": False, "note": "No ground-storey grade datum to measure the eave against."}
    eave_above_first_floor_in = round((main["grade_to_eave_ft"] - ground["grade_to_floor_ft"]) * 12, 1)
    height_test = next((t for t in fault.get("secondary_tests", []) if t["expression"] == "eave_height_above_finished_first_floor_in"), None)
    fell_back = []
    band = ((height_test["threshold"], height_test["upper"]) if height_test
            else _fallback_band(fell_back, "cape-eave: eave_height_above_finished_first_floor_in band", (96.0, 114.0)))
    ok = band[0] <= eave_above_first_floor_in <= band[1]
    pitch_test = next((t for t in fault.get("secondary_tests", []) if t["expression"] == "roof_slope_angle_deg"), None)
    pitch_band = ((pitch_test["threshold"], pitch_test["upper"]) if pitch_test
                  else _fallback_band(fell_back, "cape-eave: roof_slope_angle_deg band", (36.9, 45.0)))
    slope_deg = math.degrees(math.atan((main.get("pitch_rise_per_12") or 0) / 12.0)) if main.get("pitch_rise_per_12") else None
    pitch_ok = (slope_deg is not None) and (pitch_band[0] <= slope_deg <= pitch_band[1])
    return {"applicable": True, "computed": True, "bands_read_from_fallback": fell_back,
            "eave_height_above_finished_first_floor_in": eave_above_first_floor_in,
            "band_in": list(band), "ok": ok, "roof_slope_angle_deg": round(slope_deg, 1) if slope_deg else None,
            "pitch_band_deg": list(pitch_band), "pitch_ok": pitch_ok,
            "note": None if ok else f"{eave_above_first_floor_in} in is outside the {band[0]}-{band[1]} in band that defines this type ({fault['name']})."}

def gambrel_break_check(main):
    """faults/gambrel-slopes-converging.json's own bands, evaluated against whatever this file
    actually computed in _gambrel() -- a self-consistency check as much as a corpus check, since
    the defaults in _style_gambrel_geometry were themselves chosen inside these same bands, but
    still run explicitly rather than assumed true by construction (a style-sourced
    roof_slope_lower_deg constraint, if one exists, is NOT guaranteed to fall inside this
    secondary fault's own band, since the two are authored independently)."""
    if main.get("form") != "gambrel":
        return {"applicable": False}
    fault = _fault("gambrel-slopes-converging")
    g = main["gambrel"]
    diff = g["lower_slope_deg"] - g["upper_slope_deg"]
    diff_ok = diff >= fault["test"]["threshold"]
    break_test = next((t for t in fault.get("secondary_tests", []) if t["expression"].startswith("break_height_above_eave_in")), None)
    fell_back = []
    break_band = ((break_test["threshold"], break_test["upper"]) if break_test
                  else _fallback_band(fell_back, "gambrel: break_height_above_eave_in band", (0.55, 0.65)))
    # THE BREAK VERDICT IS UNJUDGED, FOR THE SAME REASON `wing_step_down`'s IS (3 Sep 2026).
    # Found by an adversarial audit as the SECOND occurrence of that pattern, three functions
    # above this one. `_style_gambrel_geometry` initialises `break_frac = None` and has no branch
    # that ever sets it -- there is no `break_height_above_eave` constraint reader -- so it is
    # ALWAYS `GAMBREL_BREAK_FRACTION_DEFAULT`, 0.625, and this line tested that constant against
    # the fault's own [0.55, 0.65] band, which it was chosen to sit inside. True by construction,
    # on every gambrel roof this corpus has ever drawn.
    #
    # The docstring above has half-admitted it since it was written ("the defaults ... were
    # themselves chosen inside these same bands") and ran the check anyway. A disclosure in prose
    # beside a `True` in the record is not a disclosure: every reader takes the boolean.
    # It becomes judgeable the day a style states a break height and something reads it.
    #
    # `diff_ok` above is NOT the same case and is left as a boolean: the two slopes are read from
    # independent style constraints (`roof_slope_lower_deg`, `roof_slope_upper_deg`) and their
    # difference is tested against a threshold neither of them came from.
    break_ok = None
    return {"applicable": True, "slope_difference_deg": round(diff, 1), "diff_ok": diff_ok,
            "bands_read_from_fallback": fell_back,
            "break_fraction": g["break_fraction"], "break_band": list(break_band),
            "break_ok": break_ok,
            "break_unjudged_reason": ("the break fraction is a module constant chosen inside this "
                                      "band and no style states one, so testing it against the band "
                                      "would be circular; `break_source` names the constant")}

def dormer_rhythm_check(plan, section, main):
    """Whether this house's dormers can sit on its bays -- in the three states the record has.

    WIRED TO THE REAL FIELD, 27 Aug 2026 (WP-5.13). This function used to read `declared_dormers`,
    a key it invented for itself because no schema field authored a dormer, and which therefore
    no record ever carried: it returned not-applicable on every plan in the corpus and its unit
    tests reached it by writing the placeholder in by hand. `declared.dormer` exists now (the
    ontology's own slot id, cardinality many) and carries the distinction that matters -- a house
    STATING it has none is not the same as a house whose dormers nobody could state.

    WHAT IS ACTUALLY JUDGED HERE, and what is not. Positions are NOT authored: the kit's own
    alignment_rule is "each dormer centred on a window of the storey below", so build/elevation.py
    ::dormers() derives the centres from the bays and a record cannot state a rhythm contradicting
    its own style. Measuring those derived centres against the bays they were derived from would
    be a check of arithmetic dressed as a check of design -- vacuously 1.0, every time. The
    question a record CAN get wrong is the count: a front with four bays cannot carry five dormers
    on bays, and no derivation can fix that. That is what is measured, and the note says so rather
    than letting a caller read 1.0 as a verdict on placement.
    """
    decl = (plan.get("declared") or {}).get("dormer")
    if decl is None:
        return {"applicable": False, "stated": False,
                "note": "This plan does not state whether it carries dormers. Not an absence of "
                        "dormers -- an absence of a statement."}
    if decl == "none":
        return {"applicable": True, "stated": True, "dormer_count": 0, "bay_count": None,
                "on_bay_count": 0, "ratio": None, "ok": None,
                "note": "The plan states this house carries no dormers. There is no rhythm to be "
                        "off, which is not the same as a rhythm that was measured and passed."}
    n = int(decl.get("count") or 0)
    fp = section["footprint"]
    # THE ROOF DOES NOT OWN THE BAY RHYTHM AND MUST NOT INVENT ONE. This read
    # `fp.get("bay_module_ft") or 10.0` and divided the width by it, which on a footprint that
    # states no module (both reference plans) is a 10 ft constant of exactly the class this
    # package spent two commits removing. It gave 6 bays on a front the facade pack lays out as
    # FIVE, so at `{"count": 6}` the roof reported `ratio 1.0, ok True` while the fault corpus
    # convicted the same record on 5 of 6 centred -- two records built from different rules that
    # nothing compared, which is OQ 85's own thesis, shipped inside the package that closed it.
    # Found 28 Aug 2026 by this package's adversarial audit.
    #
    # The bay count belongs to the facade layer (`elevation.py::_face_bays`, from
    # facade-classical's own odd-count formula). Where the footprint states a module the roof can
    # read it; where it does not, this is UNJUDGED and says so rather than answering from a
    # constant.
    bay_ft = fp.get("bay_module_ft")
    if not bay_ft:
        return {"applicable": True, "stated": True, "dormer_count": n, "bay_count": None,
                "on_bay_count": None, "ratio": None, "ok": None,
                "note": "This footprint states no bay module, and the bay rhythm is the facade "
                        "layer's (build/elevation.py::_face_bays, from facade-classical's own "
                        "odd-count formula) rather than the roof's. Whether there are bays enough "
                        "to carry the declared dormers is therefore unjudged HERE; the elevation "
                        "layer judges it, and `dormer-off-the-bay` reports it."}
    bay_count = int(fp["width_ft"] // bay_ft)
    on_bay = min(n, bay_count)
    ratio = (on_bay / n) if n else None
    return {"applicable": True, "stated": True, "dormer_count": n, "bay_count": bay_count,
            "on_bay_count": on_bay, "ratio": ratio,
            "ok": (None if not n else ratio >= 1.0),
            "note": ("Centres are derived from the bays below, so placement is right by "
                     "construction; what is measured is whether there are bays enough to carry "
                     f"the declared count -- {n} dormer(s) over {bay_count} bay(s)."
                     if n else
                     "The record declares a dormer object with a count of zero, which states "
                     "none in a longer way; nothing to judge.")}

# ---------------------------------------------------------------- plan-view outline + elevation profiles
def roof_outline(section, main):
    """Plan-view line segments for the roof-plan SVG: the eave rectangle (the outside-to-outside
    footprint itself), the ridge line, hip lines where the form has them, and the gambrel break
    lines (parallel to the ridge, offset by break_offset_ft on each side).

    This docstring promised "and the dependency wing's own ridge where one was computed" until
    3 Sep 2026 and the body has never emitted a wing line of any kind -- there is no second
    footprint to draw one on, which is what `wing_step_down` above says about itself. Prose
    asserting geometry the code does not produce is the class WP-6.4 exists to remove; the
    sentence goes rather than the claim being left to be believed. When a real second volume is
    placed, the line comes back here with the code that draws it."""
    fp = section["footprint"]
    W, D = fp["width_ft"], fp["depth_ft"]
    lines = [{"kind": "eave", "x1": 0.0, "y1": 0.0, "x2": W, "y2": 0.0},
             {"kind": "eave", "x1": W, "y1": 0.0, "x2": W, "y2": D},
             {"kind": "eave", "x1": W, "y1": D, "x2": 0.0, "y2": D},
             {"kind": "eave", "x1": 0.0, "y1": D, "x2": 0.0, "y2": 0.0}]
    ridge = main.get("ridge")
    if ridge:
        axis, pos, a, b = ridge["axis"], ridge["position_ft"], ridge["from_ft"], ridge["to_ft"]
        if axis == "x":
            lines.append({"kind": "ridge", "x1": a, "y1": pos, "x2": b, "y2": pos})
        else:
            lines.append({"kind": "ridge", "x1": pos, "y1": a, "x2": pos, "y2": b})
    for h in main.get("hip_lines") or []:
        lines.append({"kind": "hip", **h})
    if main.get("form") == "gambrel" and "gambrel" in main:
        off = main["gambrel"]["break_offset_ft"]
        axis = ridge["axis"]
        if axis == "x":
            lines.append({"kind": "gambrel-break", "x1": 0.0, "y1": off, "x2": W, "y2": off})
            lines.append({"kind": "gambrel-break", "x1": 0.0, "y1": D - off, "x2": W, "y2": D - off})
        else:
            lines.append({"kind": "gambrel-break", "x1": off, "y1": 0.0, "x2": off, "y2": D})
            lines.append({"kind": "gambrel-break", "x1": W - off, "y1": 0.0, "x2": W - off, "y2": D})
    if main.get("form") == "cross-gable" and main.get("cross"):
        lines.append({"kind": "cross-ridge", **main["cross"]["ridge_line"]})
    return lines

def elevation_profile(section, main, wall):
    """The per-face silhouette WP-3.2 (the elevation generator) is meant to read -- 'expose the
    outline for the elevation generator', per the hand-off brief -- as an ordered list of
    (horizontal_ft, height_ft) points along that wall, height measured above grade. A gable end
    (perpendicular to the ridge) is a triangle peaking at the ridge height; a long face (parallel
    to the ridge) is the RECTANGLE from eave to ridge, because parallel projection of one sloping
    plane fills that band; a hip is a trapezoid (eave flat, then the hip planes rise in at both
    ends to meet the ridge height across the ridge's own shorter span).

    THIS DOCSTRING SAID "a flat eave line for a simple gable" until 28 Aug 2026, nineteen lines
    above the code that stopped doing that in WP-5.13 and explains at length why -- the flat line
    was a PERSPECTIVE argument inside an orthographic renderer. WP-5.14 found and fixed exactly
    this class in `render_elevation.py`'s chimney block and left it standing in the function whose
    behaviour had actually changed. Prose asserting what the code no longer does is the failure
    this corpus polices hardest, and it survived the package that named it twice."""
    fp = section["footprint"]
    W, D = fp["width_ft"], fp["depth_ft"]
    eave = main["grade_to_eave_ft"]
    ridge = main.get("ridge")
    form = main.get("form")
    wall_len = W if wall in ("S", "N") else D
    if not ridge or ridge.get("grade_to_ridge_ft") is None:
        return [(0.0, eave), (wall_len, eave)]   # unjudged ridge -- flat eave line only, nothing invented above it
    ridge_ft = ridge["grade_to_ridge_ft"]
    parallel = (wall in ("S", "N") and ridge["axis"] == "x") or (wall in ("E", "W") and ridge["axis"] == "y")
    if not parallel:
        return [(0.0, eave), (wall_len / 2.0, ridge_ft), (wall_len, eave)]   # gable end: simple triangle
    if form in ("hip", "gable-on-hip"):
        a, b = ridge["from_ft"], ridge["to_ft"]
        return [(0.0, eave), (a, ridge_ft), (b, ridge_ft), (wall_len, eave)]   # trapezoid
    if form == "gambrel":
        g = main["gambrel"]
        off = g["break_offset_ft"]
        return [(0.0, eave), (off, g["break_grade_to_ft"]), (wall_len - off, g["break_grade_to_ft"]), (wall_len, eave)]
    # SIMPLE GABLE, LONG FACE. This returned a flat eave line until 27 Aug 2026, on the reasoning
    # that "the ridge is behind the near roof plane, not visible". That is a PERSPECTIVE argument
    # and this is an ORTHOGRAPHIC projection. The near plane slopes away from the viewer, and
    # parallel projection maps it to a full-width band from the eave up to the ridge -- the ridge
    # is the top edge of the drawing, at its true height. The front elevation of the Tidewater
    # reference plan was short by 14.22 ft: the whole roof was missing from the sheet everyone
    # looks at, which is what made a five-bay Georgian read as a box.
    #
    # A side-gable front is therefore a plain rectangle, eave line to ridge line, and its
    # BLANKNESS is correct -- there is nothing in it but the covering. That is the opposite of the
    # gable end (a triangle) and of the hip (a trapezoid), and all three now come from here.
    return [(0.0, eave), (0.0, ridge_ft), (wall_len, ridge_ft), (wall_len, eave)]

# ---------------------------------------------------------------- orchestration
def build_roof(plan, parti=None, section=None):
    if section is None:
        section = ST.build_section(plan, parti)
    if "error" in section:
        return {"error": section["error"]}
    style = plan.get("style")
    main = main_roof(plan, section, style)
    wing = wing_step_down(plan, section, main)
    chimneys = chimney_positions(plan, style, section, main)
    checks = {
        "wing_step_down": wing,
        "cape_eave": cape_eave_check(style, section, main),
        "gambrel_break": gambrel_break_check(main),
        "dormer_rhythm": dormer_rhythm_check(plan, section, main),
    }
    outline = roof_outline(section, main)
    profiles = {w: elevation_profile(section, main, w) for w in FACES}
    return {
        "plan_id": plan.get("id"), "style": style, "main": main, "chimneys": chimneys,
        "checks": checks, "outline": outline, "elevation_profiles": profiles,
        "footprint": section["footprint"], "section": section,
    }

# ---------------------------------------------------------------- cli
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan"); ap.add_argument("--parti"); ap.add_argument("--out"); ap.add_argument("--svg")
    a = ap.parse_args()
    plan = json.load(open(a.plan))
    parti = json.load(open(f"{ROOT}/partis/{a.parti}.json")) if a.parti else None
    roof = build_roof(plan, parti)
    if "error" in roof:
        print(roof["error"]); return
    print(f"\n  {plan['name']}")
    m = roof["main"]
    print(f"  form: {m['form']}" + (f"  ({m['form_note']})" if m.get('form_note') else ""))
    if m.get("pitch_rise_per_12"):
        print(f"  pitch {m['pitch_rise_per_12']}:12 ({m['pitch_source']})")
    r = m.get("ridge") or {}
    if r.get("grade_to_ridge_ft") is not None:
        print(f"  grade to eave {m['grade_to_eave_ft']} ft, grade to ridge {r['grade_to_ridge_ft']} ft, "
              f"ridge axis {r['axis']} from {r['from_ft']} to {r['to_ft']} ft")
    else:
        print(f"  grade to eave {m['grade_to_eave_ft']} ft, ridge unjudged.")
    ch = roof["chimneys"]
    if ch["positions"]:
        for c in ch["positions"]:
            ok = ch.get("style_check", {}).get("ok")
            print(f"  chimney at ({c['x_ft']}, {c['y_ft']}) ft, total height {c['total_height_grade_ft']} ft"
                  + (f"  [{ch['style_check']['constraint_id']}: {'OK' if ok else 'FAIL' if ok is False else '?'}]" if ch.get("style_check") else ""))
    elif ch.get("note"):
        print(f"  chimneys: {ch['note']}")
    w = roof["checks"]["wing_step_down"]
    if w.get("computed"):
        print(f"  dependency wing ridge {w['wing_ridge_grade_ft']} ft ({w['ratio']*100:.0f}% of main, band {w['ratio_band']}) -- {'UNJUDGED' if w['ok'] is None else ('OK' if w['ok'] else 'FAIL')}")
    cape = roof["checks"]["cape_eave"]
    if cape.get("computed"):
        print(f"  Cape eave-to-first-floor {cape['eave_height_above_finished_first_floor_in']} in vs {cape['band_in']} in band -- {'OK' if cape['ok'] else 'FAIL'}")
    gb = roof["checks"]["gambrel_break"]
    if gb.get("applicable"):
        brk = 'UNJUDGED' if gb['break_ok'] is None else ('OK' if gb['break_ok'] else 'FAIL')
        print(f"  gambrel slope difference {gb['slope_difference_deg']} deg -- {'OK' if gb['diff_ok'] else 'FAIL'}; break at {gb['break_fraction']*100:.0f}% -- {brk}")
    if a.out:
        json.dump(roof, open(a.out, "w"), indent=1, ensure_ascii=False)
        print(f"  wrote {a.out}")
    if a.svg:
        RR = _mod("render_roof", f"{ROOT}/build/render_roof.py")
        RR.render_roof(roof, a.svg)
        print(f"  wrote {a.svg}")
    print()

if __name__ == "__main__":
    main()
