#!/usr/bin/env python3
"""Moulding geometry: the constructions, stated once.

WP-5.7. Every drawn moulding in this corpus used to be one of two things: a square step, or a
Bezier whose control points were hand-tuned fractions (0.58, 0.42, 0.62) chosen because they
looked about right in `build/orders_template.html::segTo`. Seventy per cent of the 502 order-pack
members fell through that function's default branch and were drawn as rectangles -- every fillet,
fascia, corona, dentil band and modillion band among them. A cornice drawn that way is a stepped
knob, which is what the workbench showed and what this module exists to replace.

What a moulding IS, here: a name from `schema/proportion-pack.schema.json`'s 29-value `profile`
enum, a height, and a projection. That is enough to construct the real curve, because the classical
mouldings ARE constructions -- a quarter of a circle, two tangent arcs through the chord's midpoint,
a half round. Nothing here traces a photograph or fits a curve to one; every shape below is drawn
from the member's own two numbers by a rule named in its docstring.

  member_path(profile, x_from, y0, x_face, y1)  -> (segments, x_end) for ONE member
  silhouette(members, naked_at, from_axis)      -> segments for a whole stack, bottom to top
  repeat_positions(run_in, count, spacing_in, width_in)  -> the teeth of a dentil/modillion band
  outer_face(naked, projection_in, from_axis)   -> the OQ 65 datum rule, stated once
  column_radius_at(...)                         -> shaft radius with diminution and entasis
  svg_path(segments, sx, sy)                    -> an SVG `d` string
  dxf_points(segments, tol)                     -> (x, y, bulge) vertices for an LWPOLYLINE

WHERE THE SHAPES COME FROM, and what is construction rather than measurement:

  * ovolo / quarter-round / echinus  a CONVEX quarter, elliptical where the member's height and
                                     projection differ (which is the ordinary case).
  * cavetto / apophyge / conge       a CONCAVE quarter, the same two numbers.
  * cyma-recta                       the gola diritta: hollow BELOW, round ABOVE. Two equal
                                     tangent arcs meeting at the chord's midpoint, vertical
                                     tangents at both ends. Radius falls out of the geometry:
                                     r = (dx^2 + h^2) / (4*dx).
  * cyma-reversa / ogee              the gola rovescia, the same construction reversed: round
                                     BELOW, hollow ABOVE, horizontal end tangents, and therefore
                                     r = (dx^2 + h^2) / (4*h).
  * torus / astragal / bead          a half round: out to the face at mid-height and back.
  * scotia                           a hollow half the member's own height deep, in two quarters
                                     tangent at the throat. THIS ONE CARRIES A CONVENTION: no pack
                                     states a scotia's depth, so the depth is taken as half the
                                     height, which is what a half-round hollow means. It is a
                                     drawing construction, not a measurement, and is said so here
                                     rather than buried in a magic number.
  * fillet, listel, fascia, plinth,  a square step. A corona takes a drip ONLY where the member's
    corona, abacus, metope, flat,    own note asks for one (Gibbs: 'divide the projecting part in
    dentil, modillion, mutule,       two for the Drip') -- the note is read, never assumed.
    triglyph
  * bevel                            the straight line it is.
  * volute, acanthus                 NOT CONSTRUCTED. A volute is a spiral whose construction is
                                     on a plate this corpus cannot reach (the OQ 7-11 class), and
                                     an acanthus is foliage, not a curve. These return a plain
                                     swelling and set `unconstructed`, so a caller can say so.

TWO THINGS A CALLER MUST NOT RE-DERIVE:

  1. `y_bottom_in`/`y_top_in` off proportion_engine.dimension() are ABSOLUTE in the stack -- the
     cumulative sum has already run. Adding an assembly's own base to them a second time is the
     bug that took the Doric order apart in `OrderPlate`.
  2. The projection datum. `outer_face()` below is the ONE implementation of OQ 65's rule; a pack
     declaring `axis` measures its projections from the column's centre line, and a recorded 0
     under that reading is an ABSENT figure, not a flush face. Getting this wrong drew Vignola's
     Ionic 2.25x too wide once already.

CLI:
  python3 build/profiles.py selftest
"""
import math, sys

TAU = math.pi * 2.0
_EPS = 1e-9

# Profiles this module constructs from a rule. Anything outside it is a square step, which is
# the honest default: a fillet IS a square step.
CONVEX_QUARTER = ("ovolo", "quarter-round", "echinus")
CONCAVE_QUARTER = ("cavetto", "apophyge", "congé", "conge")
ROUNDS = ("torus", "astragal", "bead")
SQUARE = ("fillet", "listel", "fascia", "plinth", "corona", "abacus", "metope",
          "flat", "dentil", "modillion", "mutule", "triglyph", "other")
UNCONSTRUCTED = ("volute", "acanthus")
# Profiles whose repetition is the point: a band of them is not a solid band.
REPEATING = ("dentil", "modillion", "mutule", "triglyph")


# ---------------------------------------------------------------- segment primitives
def _line(x, y):
    return {"kind": "line", "to": (round(x, 6), round(y, 6))}


def _arc(cx, cy, rx, ry, a0, a1, to):
    """An elliptical arc in MODEL space (y up), parametrised as
    (cx + rx*cos a, cy + ry*sin a). Angles are radians; a1 > a0 means counter-clockwise."""
    return {"kind": "arc", "cx": round(cx, 6), "cy": round(cy, 6),
            "rx": round(abs(rx), 6), "ry": round(abs(ry), 6),
            "a0": a0, "a1": a1, "to": (round(to[0], 6), round(to[1], 6))}


def _ell_arc(cx, cy, rx, ry, p_from, p_to):
    """An elliptical arc through two known points about a known centre, taking the SHORT way.

    Angles are the ellipse's PARAMETRIC angles, not the polar angle of the point -- for rx != ry
    those differ, and using the polar angle is how an arc ends up starting somewhere other than
    where its own construction put it. Every construction in this module produces a quarter or
    less, so the short way is always the right way; anything wanting a major arc states its own
    angles."""
    rx, ry = abs(rx) or _EPS, abs(ry) or _EPS
    a0 = math.atan2((p_from[1] - cy) / ry, (p_from[0] - cx) / rx)
    a1 = math.atan2((p_to[1] - cy) / ry, (p_to[0] - cx) / rx)
    d = (a1 - a0) % TAU
    if d > math.pi:
        d -= TAU
    return _arc(cx, cy, rx, ry, a0, a0 + d, p_to)


def arc_point(seg, t=1.0):
    """A point along an arc segment, t in [0,1] from a0 to a1. Used by the tests to prove
    tangency and by dxf_points() to flatten an ellipse."""
    a = seg["a0"] + (seg["a1"] - seg["a0"]) * t
    return (seg["cx"] + seg["rx"] * math.cos(a), seg["cy"] + seg["ry"] * math.sin(a))


def arc_tangent(seg, t=1.0):
    """Unit tangent along the arc at t, in the direction of travel. The tests use this to prove
    the cyma's two arcs meet smoothly rather than merely meeting."""
    a = seg["a0"] + (seg["a1"] - seg["a0"]) * t
    dx = -seg["rx"] * math.sin(a)
    dy = seg["ry"] * math.cos(a)
    if seg["a1"] < seg["a0"]:
        dx, dy = -dx, -dy
    n = math.hypot(dx, dy)
    return (dx / n, dy / n) if n > _EPS else (0.0, 0.0)


# ---------------------------------------------------------------- the OQ 65 datum rule
def outer_face(naked, projection_in, from_axis):
    """Where a member's outer face actually sits, given the pack's declared datum.

    OQ 65, ruled 26 Aug 2026. Thirteen order packs record `projection_parts` as an offset from
    the member's OWN NAKED and twelve as an absolute radius FROM THE AXIS, split by order rather
    than by authority. Adding a naked to a radius draws the shaft narrower than its own
    mouldings. Under the axis reading a recorded 0 is an ABSENT figure -- the authority did not
    publish that member's projection -- and the honest thing is to draw it at its naked and let
    the caller count it, never to collapse it onto the centre line."""
    p = projection_in or 0.0
    if not from_axis:
        return naked + p
    if p <= 0:
        return naked                       # absent, not flush: see the docstring
    return max(p, naked)


# ---------------------------------------------------------------- one member
def member_path(profile, x_from, y0, x_face, y1, note=None):
    """The segments for ONE member, from the current point (x_from, y0) to its own face at y1.

    Returns (segments, x_end). x_end is where the walk now stands, which is NOT always x_face:
    a torus returns to the plane it sprang from, because that is what a half round does.

    Every construction is named in the module docstring. dx may be negative (a member that
    recedes as it rises, which happens above a corona) and every construction below carries the
    sign through rather than assuming a cornice only ever grows."""
    h = y1 - y0
    dx = x_face - x_from
    p = (profile or "flat").lower()
    segs = []

    # A member with no height cannot be drawn as anything but a step to its own face.
    if abs(h) < _EPS:
        if abs(dx) > _EPS:
            segs.append(_line(x_face, y1))
        return segs, x_face

    # No horizontal run: every curve degenerates to the vertical face it actually is. This is
    # the case the old seg_to() hit on EVERY member -- it was always called with xa == xb -- which
    # is why its curves never appeared and the cornice came out a flight of steps.
    if abs(dx) < _EPS and p not in ROUNDS and p != "scotia":
        segs.append(_line(x_face, y1))
        return segs, x_face

    if p in CONVEX_QUARTER:
        # Convex quarter: centre above the start, so the face swells out early and stands
        # vertical where it meets what sits on it.
        segs.append(_ell_arc(x_from, y1, dx, h, (x_from, y0), (x_face, y1)))
        return segs, x_face

    if p in CONCAVE_QUARTER:
        # Concave quarter: centre outboard at the springing, so the face leaves vertical and
        # turns over into the horizontal.
        segs.append(_ell_arc(x_face, y0, dx, h, (x_from, y0), (x_face, y1)))
        return segs, x_face

    if p == "cyma-recta":
        r = (dx * dx + h * h) / (4.0 * dx)
        mx, my = x_from + dx / 2.0, y0 + h / 2.0
        segs.append(_ell_arc(x_from + r, y0, r, r, (x_from, y0), (mx, my)))
        segs.append(_ell_arc(x_face - r, y1, r, r, (mx, my), (x_face, y1)))
        return segs, x_face

    if p in ("cyma-reversa", "ogee"):
        r = (dx * dx + h * h) / (4.0 * h)
        mx, my = x_from + dx / 2.0, y0 + h / 2.0
        segs.append(_ell_arc(x_from, y0 + r, r, r, (x_from, y0), (mx, my)))
        segs.append(_ell_arc(x_face, y1 - r, r, r, (mx, my), (x_face, y1)))
        return segs, x_face

    if p in ROUNDS:
        # A half round: out to the face at mid height, back to the plane it sprang from.
        ym = y0 + h / 2.0
        bulge = dx if abs(dx) > _EPS else h / 2.0
        segs.append(_ell_arc(x_from, ym, bulge, h / 2.0, (x_from, y0), (x_from + bulge, ym)))
        segs.append(_ell_arc(x_from, ym, bulge, h / 2.0, (x_from + bulge, ym), (x_from, y1)))
        return segs, x_from

    if p == "scotia":
        # Two quarters tangent at the throat. The depth is the convention named in the module
        # docstring -- half the member's own height -- because no pack states one.
        ym = y0 + h / 2.0
        x_throat = min(x_from, x_face) - h / 2.0
        segs.append(_ell_arc(x_throat, y0, x_from - x_throat, h / 2.0, (x_from, y0), (x_throat, ym)))
        segs.append(_ell_arc(x_throat, y1, x_face - x_throat, h / 2.0, (x_throat, ym), (x_face, y1)))
        return segs, x_face

    if p == "bevel":
        segs.append(_line(x_face, y1))
        return segs, x_face

    if p in UNCONSTRUCTED:
        # Said plainly rather than drawn confidently: this is a swelling standing in for a shape
        # this corpus does not hold the construction for.
        segs.append(_ell_arc(x_from, y1, dx, h, (x_from, y0), (x_face, y1)))
        segs[-1]["unconstructed"] = p
        return segs, x_face

    # Square step -- fillet, fascia, corona, plinth, abacus, and the repeating members whose
    # section is square even though their elevation is a row of teeth.
    if p == "corona" and note and "drip" in str(note).lower():
        # Gibbs, of the corona: 'divide the projecting part in two for the Drip'. The note asks
        # for it; a corona whose note does not is drawn square.
        segs.append(_line(x_face, y0))
        segs.append(_line(x_face, y0 + h * 0.5))
        segs.append(_line(x_from + dx * 0.5, y0 + h * 0.5))
        segs.append(_line(x_from + dx * 0.5, y0 + h * 0.62))
        segs.append(_line(x_face, y0 + h * 0.62))
        segs.append(_line(x_face, y1))
        return segs, x_face
    segs.append(_line(x_face, y0))
    segs.append(_line(x_face, y1))
    return segs, x_face


# ---------------------------------------------------------------- a whole stack
def silhouette(members, naked_at=None, from_axis=False, close=True):
    """The profile of a stack of members, bottom to top, as segments in inches.

    `members` is exactly what proportion_engine.dimension() puts in an assembly's `members` list
    -- absolute y, a projection, a profile name -- unmodified. `naked_at(y)` gives the plane the
    projections are measured from at a height (constant for an entablature run, the diminishing
    column radius for a shaft); pass a float for a constant. `from_axis` is the pack's declared
    `projection_datum` == "axis".

    Returns {"start": (x, y), "segments": [...], "unconstructed": [ids], "notes": [...]}.
    A caller that wants to SAY which members it could not construct reads `unconstructed`; that
    is the difference between a drawing that is honest about a volute and one that pretends."""
    if not members:
        return {"start": (0.0, 0.0), "segments": [], "unconstructed": [], "notes": []}
    if naked_at is None:
        naked_at = 0.0
    nk = naked_at if callable(naked_at) else (lambda _y, _v=float(naked_at): _v)

    y_start = members[0]["y_bottom_in"]
    x_cur = nk(y_start)
    out, unconstructed = [], []
    for m in members:
        y0, y1 = m["y_bottom_in"], m["y_top_in"]
        face = outer_face(nk((y0 + y1) / 2.0), m.get("projection_in") or 0.0, from_axis)
        segs, x_cur = member_path(m.get("profile"), x_cur, y0, face, y1, note=m.get("note"))
        for s in segs:
            if s.get("unconstructed"):
                unconstructed.append({"id": m.get("id"), "profile": s["unconstructed"]})
        out.extend(segs)
    if close and out:
        y_end = members[-1]["y_top_in"]
        out.append(_line(nk(y_end), y_end))
        out.append({"kind": "close"})
    return {"start": (round(x_cur if not out else nk(y_start), 6), round(y_start, 6)),
            "segments": out, "unconstructed": unconstructed, "notes": []}


# ---------------------------------------------------------------- repetition
def repeat_positions(run_in, count=None, spacing_in=None, width_in=None, centre_on=None):
    """Where the teeth of a dentil, modillion, mutule or triglyph band actually fall along a run.

    A band of dentils drawn as a solid band is a band of no dentils, which is how every cornice
    in this corpus was drawn until now. But a tooth needs a WIDTH, and `width_parts` is null on
    the members whose authority never published one. Rather than invent a width, this returns
    `solid: True` with the reason, and a caller draws the band solid AND SAYS SO.

    `centre_on` (a list of x positions, e.g. column axes) honours Gibbs's rule that 'always the
    centre of a Modillion exactly over the centre of each column' where the caller knows them."""
    if not spacing_in or spacing_in <= 0:
        return {"solid": True, "reason": "no spacing stated for the band", "teeth": []}
    if not width_in or width_in <= 0:
        return {"solid": True, "reason": "tooth width unstated: no `width_parts` on this member",
                "teeth": []}
    if width_in >= spacing_in:
        return {"solid": True, "reason": "stated tooth width fills its own spacing", "teeth": []}

    teeth = []
    if centre_on:
        anchors = [c for c in centre_on if -width_in <= c <= run_in + width_in]
        for a in anchors:
            k = 1
            teeth.append(a)
            while True:                     # fill between the anchors at the stated pitch
                nxt = a + k * spacing_in
                if nxt > run_in or any(abs(nxt - b) < spacing_in * 0.5 for b in anchors):
                    break
                teeth.append(nxt)
                k += 1
    else:
        n = int(count) if count else max(1, int(round(run_in / spacing_in)))
        span = (n - 1) * spacing_in
        x0 = (run_in - span) / 2.0          # a band is centred on its run, not started at one end
        teeth = [x0 + i * spacing_in for i in range(n)]
    teeth = sorted(t for t in teeth if -_EPS <= t - width_in / 2.0 and t + width_in / 2.0 <= run_in + _EPS)
    return {"solid": False, "reason": None, "width_in": width_in, "spacing_in": spacing_in,
            "teeth": [{"x0": round(t - width_in / 2.0, 4), "x1": round(t + width_in / 2.0, 4),
                       "centre": round(t, 4)} for t in teeth]}


# ---------------------------------------------------------------- the column
def column_radius_at(y, shaft_y0, shaft_y1, r_lower, diminution=None, entasis_begins_at=None):
    """The shaft's radius at a height, with diminution and entasis.

    NOT a classical entasis construction. Vignola describes striking the swell from a semicircle
    divided into equal parts and Chambers gives another; no pack in this corpus RECORDS either --
    `column.fluting.profile` and the entasis notes are prose an expression cannot execute, and the
    facsimiles that would settle it are the network-blocked OQ 7-11 class. So this is the smooth
    diminution `orders_template.html` has always drawn, stated as such, and an open question
    carries the real construction."""
    if not diminution or diminution >= 1.0:
        return r_lower
    span = shaft_y1 - shaft_y0
    if span <= 0:
        return r_lower
    begin = shaft_y0 + span * (entasis_begins_at or 0.0)
    if y <= begin:
        return r_lower
    u = (y - begin) / max(shaft_y1 - begin, _EPS)
    u = min(max(u, 0.0), 1.0)
    s = u * u * (3.0 - 2.0 * u)             # smoothstep, NOT an entasis construction
    return r_lower * (1.0 - s * (1.0 - diminution))


# ---------------------------------------------------------------- a whole pack, ready to scale
COLUMN_ASM = ("pedestal", "subplinth", "base", "shaft", "capital")


def pack_geometry(dim, column=None, projection_datum=None, taper_steps=14):
    """Every assembly of a dimensioned pack as profile geometry, in inches at ITS module.

    This exists so that no drawing surface has to construct a moulding for itself. The corpus
    already keeps four implementations of the dimensioning arithmetic in step by hand (Python's
    proportion_engine, the JS in orders_template.html, this file's own callers, and the
    workbench's Proportions plate); adding a fifth copy of the PROFILE constructions to
    JavaScript would be the same trap one layer down, and the trap has already sprung once --
    OQ 65 was two implementations disagreeing about a datum, and the navigation grammar was
    three copies disagreeing about a dot.

    The way out is that pack geometry is LINEAR IN THE MODULE, which tests/test_profiles.py
    proves rather than assumes: geometry computed at one module is geometry at any other module
    times a constant. So this is computed once, in one language, and a consumer that wants it at
    a different size multiplies. JavaScript keeps no profile knowledge at all.

    `dim` is proportion_engine.dimension()'s output, and which assemblies it contains is the
    caller's choice -- a stack drawn without its pedestal is a different stack, not a crop, since
    the y positions above it all move.

    Datums, per orders_template.html's own rule and for the same reasons:
      pedestal          the die's naked
      base / capital    the column's radius (constant: both sit outside the shaft's taper)
      shaft             the radius AT THAT HEIGHT -- the one assembly whose datum is a function
      everything else   the naked of the frieze, which is the column's top radius
    """
    column = column or {}
    from_axis = projection_datum == "axis"
    totals = dim.get("totals", {})
    R = (totals.get("lower_diameter_in") or 0.0) / 2.0
    dimin = column.get("diminution") or 1.0
    r_top = R * dimin
    asms = {a["id"]: a for a in dim.get("assemblies", [])}

    base = asms.get("base")
    plinth = max([m.get("projection_in") or 0.0 for m in base["members"]], default=0.0) if base else 0.0
    die_naked = (max(R, plinth if from_axis else R + plinth) if plinth else R * 1.2)

    shaft = asms.get("shaft")
    sy0 = shaft["y_bottom_in"] if shaft else 0.0
    sy1 = shaft["y_top_in"] if shaft else 1.0
    ent_at = column.get("entasis_begins_at")
    ent_at = ent_at if ent_at is not None else (1.0 / 3.0)

    def radius_at(y):
        return column_radius_at(y, sy0, sy1, R, dimin, ent_at)

    def datum_for(aid, y):
        if aid in ("pedestal", "subplinth"):
            return die_naked
        if aid == "base":
            return R
        if aid == "capital":
            return r_top
        if aid == "shaft":
            return radius_at(y)
        return r_top

    out = {"module_in": dim.get("module_in"), "projection_datum": projection_datum,
           "lower_radius_in": round(R, 5), "upper_radius_in": round(r_top, 5),
           "die_naked_in": round(die_naked, 5),
           "shaft": ({"y0": sy0, "y1": sy1, "entasis_begins_at": ent_at,
                      "diminution": dimin} if shaft else None),
           "assemblies": [], "unconstructed": []}

    for a in dim.get("assemblies", []):
        aid = a["id"]
        segs, uncon, faces = [], [], []
        x_cur = datum_for(aid, a["y_bottom_in"])
        start = (x_cur, a["y_bottom_in"])
        seen_side = False
        for m in a["members"]:
            # A side-by-side assembly (the Doric frieze) is not a stack: triglyph and metope are
            # each the full height of the frieze. Only the first can own the section.
            if m.get("side_by_side"):
                if seen_side:
                    continue
                seen_side = True
            y0, y1 = m["y_bottom_in"], m["y_top_in"]
            is_shaft_body = aid == "shaft" and (y1 - y0) > (sy1 - sy0) * 0.6
            if is_shaft_body:
                # The taper, sampled. NOT a classical entasis construction -- see
                # column_radius_at()'s own docstring, and the open question it names.
                for i in range(1, taper_steps + 1):
                    yy = y0 + (y1 - y0) * (i / taper_steps)
                    segs.append(_line(radius_at(yy), yy))
                x_taper = [_line(radius_at(y0 + (y1 - y0) * (i / taper_steps)),
                                 y0 + (y1 - y0) * (i / taper_steps))
                           for i in range(1, taper_steps + 1)]
                faces.append({"id": m.get("id"), "x": round(radius_at(y1), 5), "tapered": True,
                              "x_from": round(radius_at(y0), 5), "y0": y0, "y1": y1,
                              "segments": x_taper})
                x_cur = radius_at(y1)
                continue
            face = outer_face(datum_for(aid, (y0 + y1) / 2.0), m.get("projection_in") or 0.0, from_axis)
            x_from = x_cur
            ms, x_cur = member_path(m.get("profile"), x_cur, y0, face, y1, note=m.get("note"))
            # Each member's OWN segments, so a plate that draws band by band (the workbench's
            # does, and its walk asserts one path per member) draws the real moulded edge rather
            # than a straight line between two projections.
            faces.append({"id": m.get("id"), "x": round(face, 5), "tapered": False,
                          "x_from": round(x_from, 5), "y0": y0, "y1": y1, "segments": ms})
            for s in ms:
                if s.get("unconstructed"):
                    uncon.append({"assembly": aid, "id": m.get("id"), "profile": s["unconstructed"]})
            segs.extend(ms)
        out["assemblies"].append({
            "id": aid, "y0": a["y_bottom_in"], "y1": a["y_top_in"],
            "naked_in": round(datum_for(aid, a["y_bottom_in"]), 5),
            "start": (round(start[0], 5), round(start[1], 5)),
            "segments": segs, "faces": faces,
        })
        out["unconstructed"].extend(uncon)
    return out


# ---------------------------------------------------------------- serialisers
def svg_path(segments, sx=None, sy=None, start=None):
    """An SVG `d` string. sx/sy are the same screen transforms every renderer here already uses.

    The sweep flag is computed in SCREEN space, not model space: every plate in this corpus
    flips y (model inches up, screen pixels down), and a flip reverses the direction an arc
    turns. Detecting the flip from the transform itself is what keeps a caller from having to
    remember to invert it."""
    sx = sx or (lambda v: v)
    sy = sy or (lambda v: v)
    flip = sy(1.0) < sy(0.0)
    d = []
    if start is not None:
        d.append(f"M {sx(start[0]):.3f},{sy(start[1]):.3f}")
    for s in segments:
        if s["kind"] == "close":
            d.append("Z")
        elif s["kind"] == "line":
            d.append(f"L {sx(s['to'][0]):.3f},{sy(s['to'][1]):.3f}")
        else:
            ccw = s["a1"] > s["a0"]
            sweep = 0 if (ccw != flip) else 1
            large = 1 if abs(s["a1"] - s["a0"]) > math.pi + _EPS else 0
            # Radii scale with the transform; these plates scale x and y alike.
            rx = abs(sx(s["rx"]) - sx(0.0))
            ry = abs(sy(s["ry"]) - sy(0.0))
            d.append(f"A {rx:.3f} {ry:.3f} 0 {large} {sweep} "
                     f"{sx(s['to'][0]):.3f},{sy(s['to'][1]):.3f}")
    return " ".join(d)


def dxf_points(segments, start, tol=0.01):
    """(x, y, bulge) vertices for a DXF LWPOLYLINE, in model inches.

    A circular arc survives exactly, as a bulge -- tan of a quarter of the included angle, which
    is what a bulge IS -- so a cornice profile exported to CAD is the same curve the sheet drew,
    not a polygon approximating it. An elliptical quarter has no bulge representation and is
    flattened to the stated tolerance, which is said rather than hidden."""
    pts = [[start[0], start[1], 0.0]]
    for s in segments:
        if s["kind"] == "close":
            continue
        if s["kind"] == "line":
            pts.append([s["to"][0], s["to"][1], 0.0])
            continue
        if abs(s["rx"] - s["ry"]) < 1e-6:                       # true circle: exact
            pts[-1][2] = math.tan((s["a1"] - s["a0"]) / 4.0)
            pts.append([s["to"][0], s["to"][1], 0.0])
            continue
        r = max(s["rx"], s["ry"])                                # ellipse: flatten
        sweep = abs(s["a1"] - s["a0"])
        n = max(2, int(math.ceil(sweep / (2.0 * math.acos(max(-1.0, min(1.0, 1.0 - tol / max(r, _EPS))))))
                       ) if r > tol else 2)
        n = min(max(n, 4), 64)
        for i in range(1, n + 1):
            pts.append(list(arc_point(s, i / n)) + [0.0])
    return [(round(x, 5), round(y, 5), round(b, 6)) for x, y, b in pts]


# ---------------------------------------------------------------- selftest
def _close(a, b, tol=1e-6):
    return abs(a - b) <= tol


def selftest():
    """Proves the constructions rather than the strings they serialise to."""
    fails = []

    def check(cond, msg):
        if not cond:
            fails.append(msg)

    # 1. A convex quarter bulges OUT of its chord; a concave one falls inside it.
    for prof, want_out in (("ovolo", True), ("cavetto", False)):
        segs, _ = member_path(prof, 0.0, 0.0, 4.0, 4.0)
        mid = arc_point(segs[0], 0.5)
        check((mid[0] > 2.0) == want_out,
              f"{prof}: midpoint {mid} is on the wrong side of its chord")

    # 2. The cyma's two arcs meet, and meet SMOOTHLY. A join that merely touches is a kink, and
    #    a kink is what tells a reader the curve was guessed.
    for prof in ("cyma-recta", "cyma-reversa"):
        segs, xe = member_path(prof, 0.0, 0.0, 3.0, 5.0)
        check(len(segs) == 2, f"{prof}: expected two arcs, got {len(segs)}")
        p1, p2 = arc_point(segs[0], 1.0), arc_point(segs[1], 0.0)
        check(_close(p1[0], p2[0], 1e-6) and _close(p1[1], p2[1], 1e-6),
              f"{prof}: the arcs do not meet ({p1} vs {p2})")
        t1, t2 = arc_tangent(segs[0], 1.0), arc_tangent(segs[1], 0.0)
        check(_close(t1[0], t2[0], 1e-6) and _close(t1[1], t2[1], 1e-6),
              f"{prof}: the arcs meet at a kink ({t1} vs {t2})")
        check(_close(xe, 3.0), f"{prof}: ends at {xe}, not its own face")
        # and the join sits on the chord's midpoint, which is what the construction is for
        check(_close(p1[0], 1.5, 1e-6) and _close(p1[1], 2.5, 1e-6),
              f"{prof}: join at {p1}, not the chord midpoint")

    # 3. A cyma recta is hollow BELOW and round ABOVE; a reversa is the other way up. This is the
    #    gola diritta / gola rovescia distinction and it is the whole difference between them.
    lo_recta = arc_point(member_path("cyma-recta", 0.0, 0.0, 3.0, 5.0)[0][0], 0.5)
    lo_rev = arc_point(member_path("cyma-reversa", 0.0, 0.0, 3.0, 5.0)[0][0], 0.5)
    chord_x = 0.75                                   # chord x at quarter height
    check(lo_recta[0] < chord_x, "cyma-recta: lower half is not hollow")
    check(lo_rev[0] > chord_x, "cyma-reversa: lower half is not round")

    # 4. A half round returns to the plane it sprang from.
    segs, xe = member_path("torus", 2.0, 0.0, 5.0, 6.0)
    check(_close(xe, 2.0), f"torus: ends at {xe}, should return to its springing")

    # 5. The datum rule. Under `axis` a recorded 0 is absent, not flush.
    check(_close(outer_face(10.0, 3.0, False), 13.0), "naked datum: projection is an offset")
    check(_close(outer_face(10.0, 18.0, True), 18.0), "axis datum: projection is a radius")
    check(_close(outer_face(10.0, 0.0, True), 10.0), "axis datum: a recorded 0 must read as absent")

    # 6. Scale invariance -- the claim a proportional system makes, and what lets the geometry be
    #    computed once and mapped by anyone. Segments at module m must be m times those at 1.
    m = [{"id": "a", "profile": "cyma-recta", "y_bottom_in": 0.0, "y_top_in": 2.0, "projection_in": 1.0},
         {"id": "b", "profile": "ovolo", "y_bottom_in": 2.0, "y_top_in": 3.0, "projection_in": 2.0}]
    m5 = [{**d, "y_bottom_in": d["y_bottom_in"] * 5, "y_top_in": d["y_top_in"] * 5,
           "projection_in": d["projection_in"] * 5} for d in m]
    s1 = silhouette(m, 0.0)["segments"]
    s5 = silhouette(m5, 0.0)["segments"]
    check(len(s1) == len(s5), "scale invariance: different segment counts at two modules")
    for a, b in zip(s1, s5):
        check(a["kind"] == b["kind"], "scale invariance: segment kinds diverge")
        if a["kind"] == "line":
            check(_close(a["to"][0] * 5, b["to"][0], 1e-4) and _close(a["to"][1] * 5, b["to"][1], 1e-4),
                  f"scale invariance: {a['to']} x5 != {b['to']}")
        elif a["kind"] == "arc":
            check(_close(a["rx"] * 5, b["rx"], 1e-4) and _close(a["ry"] * 5, b["ry"], 1e-4),
                  "scale invariance: radii do not scale")

    # 7. Repetition says when it cannot draw teeth instead of drawing a solid band silently.
    r = repeat_positions(100.0, count=None, spacing_in=10.0, width_in=None)
    check(r["solid"] and "unstated" in r["reason"], "repeat: an unstated width must say so")
    r = repeat_positions(100.0, count=5, spacing_in=10.0, width_in=6.0)
    check(not r["solid"] and len(r["teeth"]) == 5, f"repeat: expected 5 teeth, got {len(r['teeth'])}")
    check(all(t["x1"] - t["x0"] > 0 for t in r["teeth"]), "repeat: a tooth with no width")

    # 8. An arc survives the round trip to DXF as an arc, not as a polygon.
    segs, _ = member_path("cyma-recta", 0.0, 0.0, 3.0, 5.0)
    pts = dxf_points(segs, (0.0, 0.0))
    check(any(abs(b) > 1e-6 for _, _, b in pts), "dxf: a circular arc lost its bulge")

    # 9. The unconstructed shapes name themselves.
    res = silhouette([{"id": "v", "profile": "volute", "y_bottom_in": 0, "y_top_in": 4,
                       "projection_in": 4}], 0.0)
    check(res["unconstructed"] and res["unconstructed"][0]["profile"] == "volute",
          "volute must report itself unconstructed")

    if fails:
        print("FAIL profiles.py selftest")
        for f in fails:
            print("  -", f)
        return 1
    print(f"OK profiles.py selftest — {9} construction groups proved")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    print(__doc__)
