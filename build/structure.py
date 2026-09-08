#!/usr/bin/env python3
"""WP-3.1 — walls, structure, storeys.

Takes a plan already solved by build/geometry.py (every indoor room has a `geometry` rect)
and derives what geometry.py deliberately does not attempt: wall thickness and bearing role
from a `construction/` catalog keyed by the plan's own declared `construction_type`; an
outside-to-outside footprint alongside the clear one geometry.py already produces (rooms keep
their clear dimensions -- nothing here rewrites a room rect); which interior walls are bearing
and which spans between them exceed a plausible joist or bay-module capacity; storey heights
derived from `proportions/modules/storey-graduation.json`'s own ceiling-height rule, inverted;
grade-to-eave and grade-to-ridge heights consistent with the style's own migrated roof-pitch
constraint where one exists; and stair rise/run/riser-count/landing checked against
`proportions/modules/storey-graduation.json`'s stair_type rule and
`groupings/stair-and-landing-core.json`'s own hard rules.

Every number here is advisory, the same discipline schema/brief.schema.json's own `jurisdiction`
field already states for code checks generally, and construction/floor-structure.json says for
itself: this is "no silent pass" honesty at the structural layer, not a stamped calculation.

  python3 build/structure.py plans/tidewater-georgian-careful.json [--parti ID] \
      [--out plans/<id>.section.json] [--svg dist/<id>-section.svg] [--bearing-svg dist/<id>-bearing.svg]
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
C = PC.load_corpus()

DEFAULT_CONSTRUCTION_TYPE = _mod("assemblies", f"{ROOT}/build/assemblies.py").DEFAULT_CONSTRUCTION_TYPE
# WP-9.6: the storey derivation moved to build/storeys.py so `openings.py` can share it
# without closing an import cycle (this file loads geometry.py, which calls
# openings.stair_pass). Re-exported under the old names so every existing caller and
# tests/test_structure.py keep working, and so there is exactly ONE implementation.
STOREYS = _mod("storeys", f"{ROOT}/build/storeys.py")
# WP-11.9. Which massing element a room stands in, and each element's own envelope. A LEAF, so
# loading it at import time here closes no cycle (this file already loads geometry, which loads
# plan_check; elements loads nothing).
ELEMENTS = _mod("elements", f"{ROOT}/build/elements.py")
STOREY_CEILING_FRACTION = STOREYS.STOREY_CEILING_FRACTION
storey_heights = STOREYS.storey_heights
DEFAULT_GRADE_TO_FIRST_FLOOR_FT = 2.0          # storey-graduation.json's foundation_expression default (part*2.4 on a 10 ft storey)
IRC_MAX_RISER_IN = 7.75
IRC_MIN_TREAD_IN = 10.0
IRC_MIN_HEADROOM_IN = 80.0

# ---------------------------------------------------------------- construction catalog
# WP-11.2: the catalogue read and `wall_thickness` moved to build/assemblies.py so the DRAWING
# can share them without closing an import cycle -- this file loads geometry.py, which calls
# openings.stair_pass, so anything in the placement or drawing path reaching for `structure`
# closes it. Same move, same reason and the same re-export as WP-9.6's build/storeys.py, whose
# header states the rule: a leaf, and nothing in it may import a sibling. Re-exported under the
# old names so every existing caller and tests/test_structure.py keep working, and so there is
# exactly ONE implementation.
ASSEMBLIES = _mod("assemblies", f"{ROOT}/build/assemblies.py")
load_construction = ASSEMBLIES.load_construction
wall_thickness = ASSEMBLIES.wall_thickness
_mid = ASSEMBLIES._mid

# ---------------------------------------------------------------- wall lines
def _touches(rect, wall, W, H, tol=0.6):
    x, y, w, h = rect
    if wall == "S": return y <= tol
    if wall == "N": return y + h >= H - tol
    if wall == "W": return x <= tol
    if wall == "E": return x + w >= W - tol
    return False

def _shared_segment(a, b, tol=0.4):
    """Same rule as build/render_plan.py's own _shared() -- kept as a second, independent copy
    for the reason build/geometry.py's lot_usable_width_ft already documents: this file is
    loaded standalone via _mod() and importing render_plan.py for one helper is not worth the
    coupling. Returns (axis, position_ft, lo_ft, hi_ft) for the full shared segment, not just
    its midpoint (render_plan.py only ever needed the midpoint, for a door mark; this file
    needs the whole run, to draw and dimension a wall line)."""
    ax, ay, aw, ah = a["x_ft"], a["y_ft"], a["width_ft"], a["depth_ft"]
    bx, by, bw, bh = b["x_ft"], b["y_ft"], b["width_ft"], b["depth_ft"]
    if abs((ax + aw) - bx) <= tol or abs((bx + bw) - ax) <= tol:
        x = bx if abs((ax + aw) - bx) <= tol else ax
        lo, hi = max(ay, by), min(ay + ah, by + bh)
        if hi - lo > 1.0: return ("x", x, lo, hi)
    if abs((ay + ah) - by) <= tol or abs((by + bh) - ay) <= tol:
        y = by if abs((ay + ah) - by) <= tol else ay
        lo, hi = max(ax, bx), min(ax + aw, bx + bw)
        if hi - lo > 1.0: return ("y", y, lo, hi)
    return None

def wall_lines(level_rooms, W, H, elements=None):
    """Every wall segment on one level: the exterior boundary edges of EVERY massing element,
    plus every interior segment two placed rooms actually share. Each is tagged 'exterior' or
    'interior' here; bearing_lines() below tags interior segments 'bearing' or 'partition'.

    `elements` is `[(x, y, W, H), ...]` -- one entry per massing element, ruling 1 of WP-11.9
    (5 Sep 2026): *an element has its own envelope, and the union is reported beside it*. Omit
    it and the whole building is one rectangle at the origin, which is every plan in this corpus
    and is exactly what this function did before the argument existed.

    Before WP-11.9 the four walls were the MAIN BLOCK's, and a dependency 37 ft west of it got
    no envelope at all while its interior partitions became bearing lines out beyond the block:
    `span_check` then measured a clear span ACROSS THE HYPHEN GAP between two buildings. That is
    the second of the six layers named by
    `oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it`, and it was wrong in
    both directions at once -- structure invented where there was none, and modelled none where
    there was structure. (That slug is on ONE line on purpose: `check_citations.py` reads line by
    line, so a slug wrapped across a newline is a dangling citation to it. It caught this one.)
    """
    placed = [r for r in level_rooms if r.get("geometry")]
    walls = []
    # Axis convention matches _shared_segment() below: axis "x" is a VERTICAL wall (constant x,
    # running along y); axis "y" is a HORIZONTAL wall (constant y, running along x). So the S/N
    # boundary walls (constant y=0 / y=H, running the full width W) are axis "y"; the W/E
    # boundary walls (constant x=0 / x=W, running the full depth H) are axis "x". Getting this
    # backwards (an earlier version of this function did) plants each exterior wall's own
    # position value into the WRONG axis's break-point list in span_check() below -- e.g. the N
    # wall's y=H position leaking in as a bogus x-axis break point -- which silently fabricates
    # spans that do not exist on the actual footprint. Caught by running this file for the first
    # time against plans/tidewater-georgian-careful.json and inspecting the raw span list.
    for ex, ey, eW, eH in (elements or [(0.0, 0.0, W, H)]):
        for wall, axis, pos, lo, hi in (("S", "y", ey, ex, ex + eW),
                                        ("N", "y", ey + eH, ex, ex + eW),
                                        ("W", "x", ex, ey, ey + eH),
                                        ("E", "x", ex + eW, ey, ey + eH)):
            walls.append({"role": "exterior", "wall": wall, "axis": axis,
                          "position_ft": round(pos, 4),
                          "lo_ft": round(lo, 4), "hi_ft": round(hi, 4)})
    seen = set()
    for i, r in enumerate(placed):
        for o in placed[i + 1:]:
            seg = _shared_segment(r["geometry"], o["geometry"])
            if not seg: continue
            key = (seg[0], round(seg[1], 1), round(seg[2], 1), round(seg[3], 1))
            if key in seen: continue
            seen.add(key)
            # OQ 55: a wall between a room and a reserved void that is open to the sky is an
            # EXTERIOR wall. It is weather-facing, it is on the thermal envelope, and it is
            # bearing -- which is the whole structural point of a courtyard house and was
            # invisible while the court was not placed at all. Calling it an interior partition
            # would put the court inside the envelope, which is the error this ruling exists to
            # end. A ROOFED void does not do this: a loggia is under the same roof, and the wall
            # behind it is the ordinary interior/exterior question it always was.
            def _open_void(room):
                v = (room.get("geometry") or {}).get("void")
                return bool(v) and not v.get("roofed")
            if _open_void(r) != _open_void(o):
                court = r if _open_void(r) else o
                walls.append({"role": "exterior", "wall": "court", "axis": seg[0],
                              "position_ft": round(seg[1], 2), "lo_ft": round(seg[2], 2),
                              "hi_ft": round(seg[3], 2), "rooms": [r["id"], o["id"]],
                              "why": f"faces {court['id']}, which is open to the sky"})
                continue
            walls.append({"role": "interior", "axis": seg[0], "position_ft": round(seg[1], 2),
                          "lo_ft": round(seg[2], 2), "hi_ft": round(seg[3], 2),
                          "rooms": [r["id"], o["id"]]})
    return walls

def outside_to_outside_footprint(clear_footprint, wall):
    """Rooms keep their clear (interior) dimensions -- geometry.py's own rects are untouched.
    This is the outer envelope those clear dimensions sit inside once the exterior wall
    thickness wraps them, per the hand-off brief's own instruction: 'extend the plan record so
    rooms keep clear dimensions while the footprint becomes outside-to-outside.'"""
    grow_ft = wall["exterior_in"] / 12.0
    return {
        "width_ft": round(clear_footprint["width_ft"] + 2 * grow_ft, 2),
        "depth_ft": round(clear_footprint["depth_ft"] + 2 * grow_ft, 2),
        "clear_width_ft": clear_footprint["width_ft"], "clear_depth_ft": clear_footprint["depth_ft"],
        "exterior_wall_thickness_in": wall["exterior_in"],
    }

# ---------------------------------------------------------------- bearing lines and spans
def bearing_lines(walls, bay_module_ft, tol=0.75):
    """A wall is bearing if it is on the building's own envelope, or if it falls on the bay
    grid the parti was built from -- posts, bents and interior bearing partitions in this
    corpus's own framing systems run on the bay lines by construction (proportions/modules/
    timber-bay.json: 'require that partitions ... fall on a 16-20 ft grid'). Anything interior
    that does NOT fall on a bay line is a partition: it can move without touching structure."""
    out = []
    for w in walls:
        if w["role"] == "exterior":
            # WP-7.4 audit: keep a `why` the caller already wrote. `wall_lines` marks a wall
            # facing an unroofed court with "faces <court>, which is open to the sky" (OQ 55),
            # and the blanket "exterior envelope" overwrote it -- including in the IFC property
            # set, which writes `why` verbatim, so the courtyard reasoning was gone from the
            # export. The envelope walls carry no `why` of their own and still get one.
            out.append({**w, "bearing": True, "why": w.get("why") or "exterior envelope"}); continue
        on_grid = abs((w["position_ft"] / bay_module_ft) - round(w["position_ft"] / bay_module_ft)) * bay_module_ft <= tol
        out.append({**w, "bearing": on_grid, "why": ("on the bay grid" if on_grid else "not on the bay grid -- a partition")})
    return out

def span_check(bearing_walls, W, H, style, floor_catalog):
    """Bay-by-bay clear span between consecutive bearing lines, each axis independently, checked
    against a joist member (light frame) or the bay module's own documented capacity (hand-
    timber framing, per proportions/modules/timber-bay.json). This is what makes 'no 2x10
    spanning 18 ft passes silently' (PLAN-OF-ACTION.md's own WP-3.1 acceptance wording) an
    actual, checked claim rather than an aspiration.

    Keyed off the plan's STYLE against timber-bay.json's own applies_to list, not off wall
    construction_type: that pack's own module note defines the bay as 'the span the floor
    joists or the summer beam must make', which is a property of the framing TRADITION a style
    belongs to, not of what the exterior wall happens to be built of -- a masonry-walled
    Tidewater Georgian house (this corpus's own tidewater-georgian-careful.json is exactly this
    case) still frames its floors in hand-hewn joists on the bay module. An earlier version of
    this function checked construction_type against that same list instead, which can never
    match (construction_type values are wall-assembly ids like 'solid-masonry-two-wythe';
    timber-bay.json's applies_to list holds style ids) and silently routed every plan through
    the light-frame joist table regardless of style -- caught by testing this exact plan."""
    timber_framed = style in _timber_bay_applies_to()
    results = []
    for axis, extent in (("x", W), ("y", H)):
        # WP-7.4: `if w["bearing"]` is the whole of this fix, and its absence was measured
        # rather than reasoned about. This function took the list bearing_lines() classifies
        # and read only each wall's POSITION, never the `bearing` flag computed one call
        # earlier -- so every partition was counted as a support and the docstring's "between
        # consecutive bearing lines" described something the code did not do. bearing_lines()
        # was writing `why: "not on the bay grid -- a partition"` onto walls this function then
        # leaned the floor on.
        #
        # Measured on plans/tidewater-georgian-careful.json, the reference plan: the x axis
        # reported a worst gap of 23.37 ft over 7 lines, of which 4 are partitions. Between the
        # 3 real bearing lines the clear span is 49.93 ft, against a 20 ft hand-framed
        # capacity. The check under-reported by 2.1x, in the direction that looks safe -- a
        # defect stated smaller than it is, which is the OQ 52 family (a generator's own
        # refusal overwritten by a confident number) wearing the opposite sign.
        #
        # The capacity and bearing_lines()'s 0.75 ft grid tolerance are deliberately NOT
        # loosened to make the resulting figure smaller. A partition carries no load; that a
        # corrected check convicts a hand-authored reference plan is the check working.
        lines = sorted({0.0, extent} | {w["position_ft"] for w in bearing_walls
                                        if w["axis"] == axis and w.get("bearing")})
        for lo, hi in zip(lines, lines[1:]):
            span_ft = round(hi - lo, 2)
            if span_ft <= 0.1: continue
            if timber_framed:
                cap = 20.0   # proportions/modules/timber-bay.json: module.default_size_in range tops out at 240 in = 20 ft
                member = "hewn joist on the bay module"
                ok = span_ft <= cap
                cap_span = cap
            else:
                member, cap, ok = None, None, False
                for m in floor_catalog["light_frame_joist_spans"]:
                    if m["max_clear_span_ft"] >= span_ft and (cap is None or m["depth_in"] < cap):
                        member, cap = m["member"], m["depth_in"]
                if member is None:
                    ok = False
                    cap_span = max(m["max_clear_span_ft"] for m in floor_catalog["light_frame_joist_spans"])
                else:
                    ok = True; cap_span = next(m["max_clear_span_ft"] for m in floor_catalog["light_frame_joist_spans"] if m["member"] == member)
            results.append({
                "axis": axis, "from_ft": round(lo, 2), "to_ft": round(hi, 2), "span_ft": span_ft,
                "member": member,
                "max_span_ft": cap_span,
                "ok": ok,
                "note": (f"Within the {cap:.0f} ft hand-framed bay-module capacity." if timber_framed and ok else
                         f"Exceeds the {cap:.0f} ft hand-framed bay-module capacity -- this construction type cannot span it on the bay module alone." if timber_framed else
                         f"{member} covers it." if member else
                         f"Exceeds every member in construction/floor-structure.json's light_frame_joist_spans (largest covers "
                         f"{max(m['max_clear_span_ft'] for m in floor_catalog['light_frame_joist_spans']):.0f} ft) -- needs an "
                         f"intermediate bearing support or an engineered member outside this catalog."),
            })
    return results

_TIMBER_BAY = None
def _timber_bay_applies_to():
    """Cached for the same reason as load_construction: `span_check` calls this ONCE PER
    INVOCATION, and WP-7.4 put span_check inside the placement search's candidate loop -- 500
    reads of one static file per solve on a two-storey plan."""
    global _TIMBER_BAY
    if _TIMBER_BAY is None:
        _TIMBER_BAY = frozenset(json.load(open(f"{ROOT}/proportions/modules/timber-bay.json"))["applies_to"])
    return _TIMBER_BAY

# ---------------------------------------------------------------- storeys and roof
def graduation_check(storeys, style):
    """Checks each consecutive pair of storeys against storey-graduation.json's own
    height_proportion derived rules, only when the style is in that pack's applies_to list --
    a style outside it (log-vernacular-american, say) is not claiming this convention at all,
    and flagging it against a rule it never bound would be inventing a requirement, exactly
    what this corpus's own constraint-migration discipline argues against."""
    pack = json.load(open(f"{ROOT}/proportions/modules/storey-graduation.json"))
    if style not in pack.get("applies_to", []):
        return {"applicable": False, "findings": []}
    ordered = sorted([s for s in storeys if s.get("storey_height_ft") and s.get("index", 0) >= 0], key=lambda s: s["index"])
    # height_proportion carries four derived_rules in the pack: second/first, third/second, an attic-over-below
    # judgment rule, and a ground-under-piano-nobile inversion. Only the first two describe an ordinary ascending
    # stack, which is all this function checks -- read straight from the pack rather than re-transcribed, so a
    # future edit to storey-graduation.json's own ranges cannot silently drift out of sync with this file's copy.
    bands = [tuple(r["range"]) for r in pack["derived_rules"] if r["target_slot"] == "height_proportion"][:2]
    findings = []
    for i in range(1, len(ordered)):
        if i - 1 >= len(bands):
            # No authored band past the third storey (the pack itself does not converge past this point for a
            # plain ascending stack) -- left unjudged rather than reusing the third/second band by assumption.
            break
        lo_band, hi_band = bands[i - 1]
        ratio = ordered[i]["storey_height_ft"] / ordered[i - 1]["storey_height_ft"]
        ok = lo_band <= ratio <= hi_band
        findings.append({
            "lower": ordered[i - 1]["id"], "upper": ordered[i]["id"], "ratio": round(ratio, 3),
            "band": [lo_band, hi_band], "ok": ok,
            "note": (f"{ordered[i]['id']}/{ordered[i-1]['id']} storey ratio {ratio:.2f} is outside storey-graduation.json's "
                     f"{lo_band}-{hi_band} band." if not ok else None),
        })
    return {"applicable": True, "findings": findings}

def _style_roof_pitch(style):
    """The style's own migrated roof-pitch constraint (rise-in-12), where one has been
    migrated (WP-1.1's worked example covers english-classical and american-colonial; most
    families are not migrated yet -- see docs/constraints.md). Returns None, not a guess, when
    the style has no such constraint -- ridge height is then reported unjudged rather than
    computed off an invented pitch."""
    node = C["styles"].get(style, {})
    for c in node.get("constraints", []):
        t = c.get("test") or {}
        if t.get("expression") != "roof_pitch_rise_per_12": continue
        if t.get("direction") == "between":
            return (t["threshold"] + t["upper"]) / 2.0, c["id"], f"{t['threshold']}:12 to {t['upper']}:12"
        if t.get("direction") in ("at-least", "at-most"):
            return float(t["threshold"]), c["id"], f"{t['direction']} {t['threshold']}:12"
    return None, None, None

def roof_heights(plan, storeys, footprint_outside):
    """A rough grade-to-eave / grade-to-ridge for the SECTION record only -- not roof
    geometry (that is WP-3.3's own work package: hip/gable/gambrel form, ridge step-down,
    dormers). Assumes a single ridge spanning the shorter of the outside footprint's two
    dimensions, which is the common case for a simple gable or hip and is wrong for an
    L-plan, a cross-gable, or a hyphen-and-dependency massing -- flagged in the returned
    record's own note, not silently generalised."""
    grade_to_eave = DEFAULT_GRADE_TO_FIRST_FLOOR_FT + sum(s["storey_height_ft"] for s in storeys if s.get("storey_height_ft"))
    pitch, pitch_rule_id, pitch_statement = _style_roof_pitch(plan["style"])
    if pitch is None:
        return {"grade_to_eave_ft": round(grade_to_eave, 2), "grade_to_ridge_ft": None,
                "roof_pitch_rise_per_12": None, "pitch_source": None,
                "note": f"No migrated roof-pitch constraint for style '{plan['style']}' -- ridge height left unjudged rather than computed off an invented pitch."}
    half_span_ft = min(footprint_outside["width_ft"], footprint_outside["depth_ft"]) / 2.0
    rise_ft = half_span_ft * (pitch / 12.0)
    return {
        "grade_to_eave_ft": round(grade_to_eave, 2), "grade_to_ridge_ft": round(grade_to_eave + rise_ft, 2),
        "roof_pitch_rise_per_12": pitch, "pitch_source": pitch_rule_id, "pitch_statement": pitch_statement,
        "note": "Assumes a single ridge over the shorter footprint dimension (simple gable/hip case); a wing, ell, hyphen or "
                "dependency needs its own ridge and is not modelled here -- see WP-3.3.",
    }

# ---------------------------------------------------------------- stairs
def stair_geometry(plan, geometry_result, storeys):
    """Rise/run from proportions/modules/storey-graduation.json's own stair_type rule
    (risers = ceil(storey_height_in / D), D read from that rule -- 7.5 since Lucas ruled on
    2 Sep 2026, and NOT quoted here as a number, because a docstring stating the figure is how
    the last one went stale) and a conventional rise+2*run comfort formula for
    tread, checked against groupings/stair-and-landing-core.json's own hard rules (landing
    depth at least stair width; riser/tread constant through the flight -- this solver only
    ever produces one riser dimension per flight, so that second rule is true by construction)
    and IRC's advisory riser/tread/headroom minimums. Reads the stair-hall's own SOLVED width
    from geometry.py's placement, not an assumption -- the same room the plan and the
    validator already agree exists."""
    idx = {r["id"]: r for lv in geometry_result["levels"] for r in lv["rooms"]}
    stair_room = next((r for r in idx.values()
                       if C["rooms"].get(r["type"], {}).get("id") == "stair-hall" and r.get("geometry")), None)
    ground = next((s for s in storeys if s.get("index") == 0), None)
    if not stair_room or not ground or not ground.get("storey_height_ft"):
        return {"applicable": False, "note": "No placed stair-hall, or no ground-storey height, to check."}
    total_rise_in = ground["storey_height_ft"] * 12
    # READ, never transcribed -- see build/storeys.py::riser_divisor_in. The literal that
    # stood here had a twin in openings.py and moving the pack would have moved neither.
    risers = max(2, math.ceil(total_rise_in / STOREYS.riser_divisor_in()))
    riser_in = round(total_rise_in / risers, 3)
    tread_in = round(max(IRC_MIN_TREAD_IN, 24.0 - 2 * riser_in), 2)
    run_in = round((risers - 1) * tread_in, 2)
    g = stair_room["geometry"]
    stair_width_in = round(min(g["width_ft"], g["depth_ft"]) * 12, 1)
    long_dim_in = round(max(g["width_ft"], g["depth_ft"]) * 12, 1)
    landing_depth_in = round(max(0.0, long_dim_in - run_in), 1)
    findings = []
    if riser_in > IRC_MAX_RISER_IN:
        findings.append(f"Riser {riser_in} in exceeds the IRC advisory maximum of {IRC_MAX_RISER_IN} in.")
    if landing_depth_in < stair_width_in:
        findings.append(f"Landing depth {landing_depth_in} in is less than the stair width {stair_width_in} in "
                         f"-- groupings/stair-and-landing-core.json's own hard rule ('below that it is a turn, not a landing').")
    return {
        "applicable": True, "stair_room": stair_room["id"], "total_rise_in": round(total_rise_in, 1),
        "risers": risers, "riser_in": riser_in, "tread_in": tread_in, "run_in": run_in,
        "stair_width_in": stair_width_in, "room_long_dimension_in": long_dim_in, "landing_depth_in": landing_depth_in,
        "headroom_note": f"Not independently verified: the header depth of the floor structure above (from span_check) is not yet "
                          f"reconciled against the {IRC_MIN_HEADROOM_IN:.0f} in IRC advisory minimum at this run's own geometry.",
        "findings": findings,
    }

# ---------------------------------------------------------------- orchestration
def build_section(plan, parti=None, geometry_result=None, engine="heuristic"):
    # engine defaults to the HEURISTIC deliberately (WP-2.3), and the default is for
    # INTERNAL callers ONLY: this function is the derivation step inside plan_check's
    # elevation layer and the composer's scoring loop, where a CP-SAT proof per candidate
    # made the critic crawl — measured, not guessed. Placement as a PRODUCT is proven:
    # geometry.solve(), core.place_plan and the workbench's prove control all default to
    # CP-SAT. The placement's own geometry_report.solver names which engine ran.
    #
    # WP-6.4: EVERY USER-FACING CALLER MUST PASS `geometry_result`. Two did not —
    # workbench/server/corpus.py's section/bearing SVG and its section DXF — so the
    # Drawing Set shipped a plan sheet placed by CP-SAT and a section of the same house
    # placed by the hill-climb, with nothing saying so. A default that is right for a
    # scoring loop and wrong for a drawing is a default that has to name which it is for.
    if geometry_result is None:
        geometry_result = GEOM.solve(json.loads(json.dumps(plan)), parti, engine=engine)
    if "error" in geometry_result:
        return {"error": geometry_result["error"]}
    construction = load_construction()
    wall = wall_thickness(plan, construction)
    clear_fp = geometry_result["footprint"]
    outside_fp = outside_to_outside_footprint(clear_fp, wall)
    bay_module_ft = clear_fp.get("bay_module_ft") or 10.0

    # span_check() decides hand-timber-vs-light-frame from the plan's STYLE against timber-
    # bay.json's own applies_to list (see that function's docstring for why). That is a real,
    # separate judgment from wall.construction_type -- a plan can be a timber-bay style built in
    # anything from log to platform frame, and this corpus records no field that states the
    # FLOOR framing method independently of the wall assembly. Flag the case where the two
    # signals plausibly disagree (a timber-bay style with a declared or defaulted light-frame
    # wall assembly) rather than let the bay-module cap apply silently as if it were settled --
    # see docs/structure.md's 'What was found' for the reference-plan example this caught.
    style_is_timber_bay = plan.get("style") in _timber_bay_applies_to()
    declared_construction = (plan.get("declared") or {}).get("construction_type")
    framing_basis = None
    if style_is_timber_bay and declared_construction is None:
        framing_basis = (f"Floor spans below are checked against timber-bay.json's 20 ft hand-framed bay-module "
                          f"capacity because style '{plan.get('style')}' is in that pack's applies_to list. This plan "
                          f"declares no construction_type at all (wall thickness above assumed '{wall['construction_type']}' "
                          f"by default) -- the bay-module cap is the pack's own style-level default, not a claim this "
                          f"plan is actually hand-timber-framed.")
    elif style_is_timber_bay and construction["assemblies"].get(declared_construction, {}).get("bearing") == "load-bearing-frame" \
            and declared_construction != "braced-timber-frame":
        framing_basis = (f"Floor spans below are checked against timber-bay.json's 20 ft hand-framed bay-module "
                          f"capacity because style '{plan.get('style')}' is in that pack's applies_to list -- but this "
                          f"plan declares construction_type '{declared_construction}', a modern light-frame assembly, "
                          f"not 'braced-timber-frame'. Whether a {declared_construction} building of this style was "
                          f"actually framed with hand-hewn joists on the bay module or with dimensional/engineered "
                          f"lumber against construction/floor-structure.json's own table instead is a real judgment "
                          f"call this file does not resolve; it follows the style, per the pack's own wording, and "
                          f"records the tension here rather than silently picking one reading.")

    # WP-11.9, ruling 1: every massing element gets its own envelope. `elements.py` reads
    # `footprint.blocks` and answers with ONE entry -- the block at the origin -- on every
    # single-rectangle house, which is all sixteen plans in this corpus, so every span, every
    # bearing line and every pinned figure below is byte-identical across the change.
    _all_els = ELEMENTS.elements(geometry_result)
    levels_out = []
    for lv in geometry_result["levels"]:
        W, H = clear_fp["width_ft"], clear_fp["depth_ft"]
        # AN ELEMENT WITH NO ROOMS ON THIS LEVEL HAS NO WALLS ON THIS LEVEL, and the first
        # version of this line did not say so: it handed every level all three elements, so the
        # UPPER floor of a house with a ground-floor dependency grew a dependency envelope with
        # nothing inside it -- 12 exterior walls over 0 dependency rooms, phantom structure of
        # exactly the kind this package removes, one level up. Caught by reading the counts per
        # level rather than in total. On a one-rectangle house every room is in element zero and
        # this is the single block, as before.
        _here = [ELEMENTS.bounds_of(e) for e in
                 ELEMENTS.elements_on_level(geometry_result, lv["rooms"], _all_els)] or None
        walls = wall_lines(lv["rooms"], W, H, elements=_here)
        bearing = bearing_lines(walls, bay_module_ft)
        spans = span_check(bearing, W, H, plan.get("style"), construction["floor"])
        levels_out.append({
            "id": lv.get("id"), "index": lv.get("index"),
            "walls": bearing, "spans": spans,
            "spans_exceeding_capacity": [s for s in spans if not s["ok"]],
        })

    storeys = storey_heights(plan)
    # Grade-relative floor datum for each storey, so the section record (and render_section.py,
    # which draws only from this record) can place a floor line without recomputing
    # DEFAULT_GRADE_TO_FIRST_FLOOR_FT itself. Only assigned for storeys at or above the ground
    # floor (index >= 0) with a known height -- a below-grade level is left unjudged rather than
    # guessed at, since this file does not model basements at all.
    running_ft = DEFAULT_GRADE_TO_FIRST_FLOOR_FT
    for st in sorted([s for s in storeys if (s.get("index") or 0) >= 0], key=lambda s: s["index"]):
        st["grade_to_floor_ft"] = round(running_ft, 3)
        if st.get("storey_height_ft") is not None:
            running_ft += st["storey_height_ft"]
    grad = graduation_check(storeys, plan["style"])
    roof = roof_heights(plan, storeys, outside_fp)
    roof["grade_to_first_floor_ft"] = DEFAULT_GRADE_TO_FIRST_FLOOR_FT
    stair = stair_geometry(plan, geometry_result, storeys)

    return {
        "plan_id": plan.get("id"), "style": plan.get("style"), "wall": wall,
        "footprint": outside_fp, "levels": levels_out, "storeys": storeys,
        "storey_graduation": grad, "roof": roof, "stair": stair,
        "framing_basis": framing_basis,
        "geometry": geometry_result,
    }

# ---------------------------------------------------------------- cli
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan"); ap.add_argument("--parti"); ap.add_argument("--out")
    ap.add_argument("--svg"); ap.add_argument("--bearing-svg")
    a = ap.parse_args()
    plan = json.load(open(a.plan))
    parti = json.load(open(f"{ROOT}/partis/{a.parti}.json")) if a.parti else None
    section = build_section(plan, parti)
    if "error" in section:
        print(section["error"]); return
    print(f"\n  {plan['name']}")
    fp = section["footprint"]
    print(f"  footprint (outside-to-outside) {fp['width_ft']} x {fp['depth_ft']} ft "
          f"(clear {fp['clear_width_ft']} x {fp['clear_depth_ft']} ft, {fp['exterior_wall_thickness_in']} in exterior wall, "
          f"{section['wall']['construction_type']})")
    if section.get("framing_basis"):
        print(f"  ! {section['framing_basis']}")
    for lv in section["levels"]:
        bad = lv["spans_exceeding_capacity"]
        print(f"  {lv['id']}: {len(lv['walls'])} wall lines, {sum(1 for w in lv['walls'] if w['bearing'])} bearing, "
              f"{len(bad)} span(s) exceeding capacity" + (":" if bad else "."))
        for s in bad: print(f"    ! {s['axis']}={s['from_ft']}-{s['to_ft']} ft: {s['note']}")
    for s in section["storeys"]:
        if s.get("storey_height_ft"):
            print(f"  {s['id']}: ceiling {s['ceiling_ft']} ft, storey {s['storey_height_ft']} ft "
                  f"(floor structure {s['floor_structure_depth_in']} in)")
    r = section["roof"]
    if r.get("grade_to_ridge_ft"):
        print(f"  grade to eave {r['grade_to_eave_ft']} ft, grade to ridge {r['grade_to_ridge_ft']} ft "
              f"(pitch {r['roof_pitch_rise_per_12']}:12, {r['pitch_source']})")
    else:
        print(f"  grade to eave {r['grade_to_eave_ft']} ft, ridge unjudged: {r['note']}")
    st = section["stair"]
    if st["applicable"]:
        print(f"  stair ({st['stair_room']}): {st['risers']} risers @ {st['riser_in']} in, tread {st['tread_in']} in, "
              f"run {st['run_in']} in, landing {st['landing_depth_in']} in vs stair width {st['stair_width_in']} in")
        for f in st["findings"]: print(f"    ! {f}")
    if a.out:
        json.dump(section, open(a.out, "w"), indent=1, ensure_ascii=False)
        print(f"  wrote {a.out}")
    if a.svg or getattr(a, "bearing_svg", None):
        RS = _mod("render_section", f"{ROOT}/build/render_section.py")
        if a.svg: RS.render_section(section, a.svg); print(f"  wrote {a.svg}")
        if a.bearing_svg: RS.render_bearing_diagram(section, a.bearing_svg); print(f"  wrote {a.bearing_svg}")
    print()

if __name__ == "__main__":
    main()
