#!/usr/bin/env python3
"""Render a WP-3.2 elevation record (build/elevation.py's build_elevation()) to SVG -- a single
front-on face: wall plane, bay windows with sash/muntin grid and shutters, the entrance
composition (door, surround, entablature, sidelights where present), water table and belt course,
and the roofline (reusing build/roof.py's own elevation_profile(), not re-derived here), plus a
cross-section detail inset that draws the eave cornice's ACTUAL moulded profile.

That inset is the reason this file exists rather than just drawing flat bands everywhere.

WP-5.7 replaced this file's own seg_to()/profile_silhouette_path() -- the line-for-line port of
orders_template.html's segTo(), whose curves were Beziers with hand-tuned control fractions --
with build/profiles.py, which CONSTRUCTS each moulding: a quarter of an ellipse for an ovolo, two
tangent arcs through the chord's midpoint for a cyma, a half round for a torus. Two things were
wrong with the port beyond the guessed curves, and both are worth knowing:

  * profile_silhouette_path() called seg_to() with xa == xb on EVERY member, so every curve
    degenerated to the vertical face it was drawn between. The cornice was a flight of steps
    whatever the profile names said, which is exactly how it read on the sheet.
  * It drew from a naked of 0 while gibbs-ionic's projections are radii from the column AXIS,
    so the whole radius was drawn as overhang: 24.56 in of relief where the truth is 10.35 in.

Every moulding drawn here still comes from proportion_engine.dimension() member data and nothing
in this file invents a member height, a projection or a profile.

  render_elevation(elev, path, face=None, scale=6.0)
"""
import os, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def _mod(n, p):
    # Delegates to build/modcache.py so a module is executed once per process rather than once
    # per call (OQ 28). Loaded by path because this file is itself usually loaded by path.
    import sys as _sys
    _b = os.path.join(ROOT, "build")
    if _b not in _sys.path:
        _sys.path.insert(0, _b)
    import modcache as _mc
    return _mc.load(n, p)
PROF = _mod("profiles", f"{ROOT}/build/profiles.py")

# Palette duplicated from build/render_roof.py / build/render_plan.py rather than imported -- every
# build/*.py module in this corpus is loaded standalone via importlib (see the _mod() pattern
# throughout the corpus); importing another renderer for one colour dict is not worth the coupling.
PAL = {"ground": "#0B1B29", "paper": "#0F2536", "wall": "#16344A", "rule": "#24455E", "ink": "#EDE7DA",
       "ink2": "#9FB3C2", "ink3": "#63808F", "brass": "#D8B26A", "verd": "#7FB3A3", "copper": "#C4734A",
       "iron": "#C4553A", "glass": "#2E5468", "sash": "#EDE7DA", "shutter": "#3A5A47"}

def _wrap(text, cols):
    """Greedy wrap at word boundaries. `cols` is a character count, which is what a
    monospaced .dm class makes meaningful; a word longer than the measure is left long
    rather than cut, because cutting a word is how a note stops being a note."""
    out, line = [], ""
    for w in str(text).split():
        if line and len(line) + 1 + len(w) > cols:
            out.append(line); line = w
        else:
            line = f"{line} {w}" if line else w
    if line: out.append(line)
    return out


def _esc(t): return (t or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _style_block():
    # THE WEIGHT LADDER (WP-5.7). Five rungs, and the rung carries the meaning a drawing conveys
    # before anyone reads a dimension: what is cut, what stands proud, what is behind. It matters
    # more here than on a plan because at this scale most of a facade's relief is smaller than a
    # pixel -- the water table projects 2 in, which is one pixel at 1/16 scale -- so a projecting
    # member is told apart from a scored line by its WEIGHT, not by its offset. Drawing those
    # offsets four times over-size, which is what this file used to do, is the other way to solve
    # it and it is a lie about a measurement.
    # Deviations per element must be written style="..." and never as a presentation attribute:
    # a class rule beats an attribute silently, and tests/test_drawn_labels.py asserts the
    # general form of that rule.
    return (f'<style>'
            f'.w-cut{{stroke-width:1.7}}.w-prof{{stroke-width:1.15}}.w-med{{stroke-width:0.75}}'
            f'.w-fine{{stroke-width:0.45}}.w-hair{{stroke-width:0.3}}'
            f'.course{{stroke:{PAL["ink3"]};stroke-width:0.3;stroke-opacity:0.42;fill:none}}'
            f'.arch{{fill:{PAL["rule"]};stroke:{PAL["ink"]};stroke-width:0.75}}'
            f'.sill{{fill:{PAL["rule"]};stroke:{PAL["ink3"]};stroke-width:0.45}}'
            f'.wtm{{stroke:{PAL["ink"]};stroke-width:0.45;fill:none}}'
            f'text{{font-family:"Archivo",-apple-system,"Segoe UI",sans-serif;fill:{PAL["ink2"]}}}'
            f'.dm{{font-size:7.5px;fill:{PAL["ink3"]};font-family:ui-monospace,Menlo,monospace}}'
            f'.hd{{font-family:"Bodoni Moda",Georgia,serif;font-size:19px;fill:{PAL["ink"]}}}'
            f'.lb{{font-family:ui-monospace,Menlo,monospace;font-size:8.5px;letter-spacing:.14em;fill:{PAL["ink3"]}}}'
            f'.wf{{fill:{PAL["wall"]};stroke:{PAL["ink3"]};stroke-width:0.6}}'
            f'.op{{fill:{PAL["glass"]};stroke:{PAL["ink"]};stroke-width:1.1}}'
            f'.mt{{stroke:{PAL["ink"]};stroke-width:0.7}}'
            f'.sh{{fill:{PAL["shutter"]};stroke:{PAL["ink"]};stroke-width:0.6}}'
            f'.dr{{fill:{PAL["copper"]};stroke:{PAL["ink"]};stroke-width:0.8}}'
            f'.cs{{fill:none;stroke:{PAL["brass"]};stroke-width:1.0}}'
            f'.bd{{fill:{PAL["paper"]};stroke:{PAL["rule"]};stroke-width:0.6}}'
            f'.rf{{fill:{PAL["iron"]};fill-opacity:0.28;stroke:{PAL["ink"]};stroke-width:1.4;stroke-linejoin:round}}'
            f'.wt{{fill:{PAL["rule"]};stroke:{PAL["ink3"]};stroke-width:0.6}}'
            f'.ch{{fill:{PAL["iron"]};stroke:{PAL["ink"]};stroke-width:0.6}}'
            f'.pf{{fill:{PAL["paper"]};stroke:{PAL["ink2"]};stroke-width:0.7}}'
            f'</style>')

# ---------------------------------------------------------------- window / door drawing
def _sash_grid(s, x0, y0, x1, y1, lights_across, lights_high):
    """One sash's own muntin grid -- lights_across columns by lights_high rows of glass, drawn as
    interior grid lines only (the sash's own outer rail is the opening rectangle already drawn by
    the caller)."""
    out = []
    w, h = x1 - x0, y1 - y0
    for i in range(1, max(1, lights_across)):
        x = x0 + w * i / lights_across
        out.append(f'<line class="mt" x1="{x:.1f}" y1="{y0:.1f}" x2="{x:.1f}" y2="{y1:.1f}"/>')
    for j in range(1, max(1, lights_high)):
        y = y0 + h * j / lights_high
        out.append(f'<line class="mt" x1="{x0:.1f}" y1="{y:.1f}" x2="{x1:.1f}" y2="{y:.1f}"/>')
    return "".join(out)

def _window(s, cx, y_bottom, y_top, width_in, lights_across, lights_high, shutter_w, shutter_h, X, Ypx, scale,
            head=None, sill_in=None):
    x0, x1 = X(cx - width_in / 2 / 12.0), X(cx + width_in / 2 / 12.0)
    yb, yt = Ypx(y_bottom), Ypx(y_top)
    out = []

    # THE HEAD, drawn only where the record could judge one.
    #
    # Two things changed on 27 Aug 2026. The arch used to run `0.06 * opening_width` past each
    # jamb -- 2.32 in a side on this house -- which is a building dimension no record states, and
    # which made the implied skewback vary from window to window because it was tied to the
    # opening's width rather than to the arch's own depth. It is drawn flush now; a bearing rule
    # can put it back when one exists.
    #
    # And `kind` may be None, which is the honest output where the style permits more than one
    # masonry head and the plan's date cannot separate them (brick-course states a 1720-1750
    # CHANGE BAND, not a threshold). An unjudged head is drawn as no head at all rather than as
    # a definite one, and the sheet says so in the legend.
    if head and head.get("kind"):
        hd = head["depth_in"] / 12.0 * scale
        rise_in = head.get("rise_in")
        if rise_in is None and head.get("rise_band_in"):
            rise_in = sum(head["rise_band_in"]) / 2.0     # a band's midpoint, named in the legend
        rise = (rise_in or 0.0) / 12.0 * scale
        ax0, ax1 = x0, x1                                  # flush with the jambs
        if "segmental" in head["kind"]:
            out.append(f'<path class="arch w-med" d="M {ax0:.1f},{yt:.1f} '
                       f'Q {(ax0+ax1)/2:.1f},{yt-2*rise:.1f} {ax1:.1f},{yt:.1f} '
                       f'L {ax1:.1f},{yt-hd:.1f} Q {(ax0+ax1)/2:.1f},{yt-hd-2*rise:.1f} '
                       f'{ax0:.1f},{yt-hd:.1f} Z"/>')
        else:
            # a flat arch: the camber is in the soffit and the extrados is level
            out.append(f'<path class="arch w-med" d="M {ax0:.1f},{yt:.1f} '
                       f'Q {(ax0+ax1)/2:.1f},{yt-2*rise:.1f} {ax1:.1f},{yt:.1f} '
                       f'L {ax1:.1f},{yt-hd:.1f} L {ax0:.1f},{yt-hd:.1f} Z"/>')
        if head.get("keystone"):
            # The kit makes a keystone canonical. Its WIDTH may be a band or unstated; a band is
            # drawn at its midpoint and an unstated one at the arch's own depth, which is the
            # only figure available -- both said in the legend rather than implied by the ink.
            kw = head.get("keystone_width_in")
            kw = (sum(kw) / 2.0 if isinstance(kw, list) else kw) or head["depth_in"] * 0.6
            kwp = kw / 12.0 * scale
            out.append(f'<rect class="arch w-med" x="{(x0+x1)/2 - kwp/2:.1f}" y="{yt-hd:.1f}" '
                       f'width="{kwp:.1f}" height="{hd:.1f}"/>')

    # THE SILL. One course of purpose-moulded brick, which is what the kit states; its
    # projection is recorded as a BAND of 0 to 1 in and a band is not a figure, so it is drawn
    # flush rather than given a point value nobody published.
    if sill_in:
        sh = sill_in / 12.0 * scale
        out.append(f'<rect class="sill" x="{x0:.1f}" y="{yb:.1f}" width="{x1-x0:.1f}" height="{sh:.1f}"/>')

    out.append(f'<rect class="op" x="{x0:.1f}" y="{yt:.1f}" width="{x1-x0:.1f}" height="{yb-yt:.1f}"/>')
    meeting_y = (yb + yt) / 2.0
    out.append(f'<line class="mt" x1="{x0:.1f}" y1="{meeting_y:.1f}" x2="{x1:.1f}" y2="{meeting_y:.1f}"/>')
    out.append(_sash_grid(s, x0, meeting_y, x1, yb, lights_across, lights_high))   # lower sash
    out.append(_sash_grid(s, x0, yt, x1, meeting_y, lights_across, lights_high))   # upper sash
    sw, sh = shutter_w / 12.0 * scale, shutter_h / 12.0 * scale
    for side, sx0 in ((-1, x0 - sw), (1, x1)):
        out.append(f'<rect class="sh" x="{sx0:.1f}" y="{yt:.1f}" width="{sw:.1f}" height="{sh:.1f}"/>')
        panel_x = sx0 + sw / 2.0
        out.append(f'<line class="mt" x1="{panel_x:.1f}" y1="{yt:.1f}" x2="{panel_x:.1f}" y2="{(yt+sh):.1f}"/>')
    return "".join(out)

def _entrance(elev, cx, floor_ft, X, Ypx, scale):
    ent = elev["entrance"]
    out = []
    door_w_in, door_h_in = ent["door_leaf_width_in"], ent["door_leaf_height_in"]
    dx0, dx1 = X(cx - door_w_in / 2 / 12.0), X(cx + door_w_in / 2 / 12.0)
    dyb, dyt = Ypx(floor_ft), Ypx(floor_ft + door_h_in / 12.0)
    out.append(f'<rect class="dr" x="{dx0:.1f}" y="{dyt:.1f}" width="{dx1-dx0:.1f}" height="{dyb-dyt:.1f}"/>')
    for i in (1, 2):   # a six-panel-scaled two-wide reading, schematic only -- panel design itself is out of scope (see docs/reports)
        py = dyt + (dyb - dyt) * i / 3.0
        out.append(f'<line class="mt" x1="{dx0:.1f}" y1="{py:.1f}" x2="{dx1:.1f}" y2="{py:.1f}"/>')
    casing_w = ent["casing_width_in"] / 12.0 * scale
    cs_x0, cs_x1 = dx0 - casing_w, dx1 + casing_w
    ent_h = (ent.get("entablature_height_in") or ent["surround_height_above_opening_in"]) / 12.0 * scale
    out.append(f'<rect class="cs" x="{cs_x0:.1f}" y="{dyt-ent_h:.1f}" width="{cs_x1-cs_x0:.1f}" height="{(dyb-dyt)+ent_h:.1f}"/>')
    if ent["sidelights_present"]:
        slw = ent["sidelight_width_in"] / 12.0 * scale
        for side, sx0 in ((-1, cs_x0 - slw), (1, cs_x1)):
            out.append(f'<rect class="op" x="{sx0:.1f}" y="{dyt:.1f}" width="{slw:.1f}" height="{dyb-dyt:.1f}"/>')
    return "".join(out)

# ---------------------------------------------------------------- main
def render_elevation(elev, path, face=None, scale=6.0):
    if not elev.get("applicable", True):
        # This style is outside the Palladian/classical-front system this generator implements
        # (see build_elevation()'s own scope-gate note) -- an honest one-line placeholder, not a
        # traced or guessed elevation for a building this file was never scoped to draw.
        # The note runs to ~660 characters and this card used to print `[:140]` of it,
        # mid-word, with no ellipsis, into a box only wide enough for ~138 — two
        # amputations stacked, neither signalled, on the one drawing whose whole content
        # IS the refusal. It wraps now and the card grows to hold it: a refusal is
        # content, and a third of a refusal is not a refusal.
        note = (elev.get("note") or "").strip()
        wrapped = _wrap(note, 96) or [""]
        h = max(80, 44 + len(wrapped) * 15)
        s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="640" height="{h}" '
             f'viewBox="0 0 640 {h}" style="background:{PAL["ground"]}">', _style_block(),
             f'<text class="lb" x="16" y="30">{_esc(elev.get("style",""))} -- NOT APPLICABLE</text>']
        for i, ln in enumerate(wrapped):
            s.append(f'<text class="dm" x="16" y="{48 + i * 15}">{_esc(ln)}</text>')
        s.append('</svg>')
        open(path, "w").write("\n".join(s))
        return path
    face = face or elev["entrance_face"]
    front = elev["faces"][face]
    fp = elev["footprint"]
    span_ft = fp["width_ft"] if face in ("S", "N") else fp["depth_ft"]
    gw, uw = elev["storey_windows"][0], elev["storey_windows"][1]
    cornice, wtb = elev["eave_cornice"], elev["water_table_belt"]
    section, roof = elev["section"], elev["roof_record"]
    ground = next(s for s in section["storeys"] if s.get("index") == 0)
    upper = next((s for s in section["storeys"] if s.get("index") == 1), ground)

    floor1_ft, floor2_ft = ground["grade_to_floor_ft"], upper["grade_to_floor_ft"]
    top_of_wall_ft = roof["main"]["grade_to_eave_ft"]              # roof.py's own eave -- no frieze/cornice band yet
    true_eave_ft = elev["grade_to_true_eave_in"] / 12.0             # this file's own top-of-cornice
    cornice_band_ft = true_eave_ft - top_of_wall_ft

    is_gable_end = face in ("E", "W")
    # roof.py's own build_roof() already computes elevation_profiles for all four faces (WP-3.3,
    # "expose the outline for the elevation generator") -- read that record rather than re-derive it
    profile_ft = roof["elevation_profiles"][face]   # [(x_ft, height_ft_above_grade), ...], roof.py's own numbers
    ridge_delta_ft = true_eave_ft - top_of_wall_ft                   # shift the whole silhouette up by the cornice band this file adds on top
    profile_ft = [(x, h + ridge_delta_ft) for x, h in profile_ft]
    top_height_ft = max(h for _, h in profile_ft)
    if is_gable_end and roof.get("chimneys", {}).get("applicable"):
        # reserve enough canvas height for a chimney cap that rises above the ridge -- computed
        # here from the SAME chimney records drawn below, not a separate guess. Gable faces only,
        # because those are the only faces a stack is drawn on: see the chimney note further
        # down for why the front cannot show them yet, and why reserving sky for a stack this
        # sheet then declines to draw would be its own small lie about what is here.
        for c in roof["chimneys"]["positions"]:
            if abs(c["x_ft"]) < 0.5 or abs(c["x_ft"] - span_ft) < 0.5:
                top_height_ft = max(top_height_ft, c["total_height_grade_ft"] + ridge_delta_ft)

    pad, top, legend_h = 46, 34, 90
    inset_w = 250
    pw = span_ft * scale
    ph = top_height_ft * scale
    total_w = pad * 2 + pw + inset_w + 20
    total_h = top + ph + legend_h

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w:.0f}" height="{total_h:.0f}" '
         f'viewBox="0 0 {total_w:.0f} {total_h:.0f}" style="background:{PAL["ground"]}">']
    s.append(_style_block())
    s.append(f'<text class="hd" x="{pad}" y="20">{_esc(elev.get("plan_id",""))} — {face} ELEVATION</text>')

    ox, oy = pad, top
    X = lambda ft: ox + ft * scale
    Ypx = lambda ft: oy + (top_height_ft - ft) * scale   # model y-up (height above grade), screen y-down

    s.append(f'<rect x="{X(0):.1f}" y="{Ypx(top_height_ft):.1f}" width="{pw:.1f}" height="{ph:.1f}" fill="{PAL["paper"]}"/>')
    s.append(f'<rect class="wf" x="{X(0):.1f}" y="{Ypx(top_of_wall_ft):.1f}" width="{pw:.1f}" height="{(top_of_wall_ft*scale):.1f}"/>')
    s.append(f'<line x1="{X(0):.1f}" y1="{Ypx(0):.1f}" x2="{X(span_ft):.1f}" y2="{Ypx(0):.1f}" stroke="{PAL["ink"]}" stroke-width="1.4"/>')

    # PROJECTIONS ARE DRAWN AT THE SIZE THE RECORD STATES. Until WP-5.7 the water table overhung
    # by a hardcoded 4 px, the belt by 2 and the cornice by 6, while `water_table_projection_in`
    # (2.06 in), `belt_course_projection_in` and `cornice_projection_in` (10.5 in) sat unread in
    # the record. At 1/16 the water table's real overhang is one pixel and the cornice's is five;
    # the fake figures drew the small one four times over-size and the large one short. What
    # tells them apart now is the weight ladder, which is what tells them apart on paper.
    proj_px = lambda inches_: (inches_ or 0.0) / 12.0 * scale

    if wtb["applicable"]:
        wt_top_ft = wtb["water_table_height_above_finished_grade_in"] / 12.0
        wt_o = proj_px(wtb.get("water_table_projection_in"))
        s.append(f'<rect class="wt w-prof" x="{X(0)-wt_o:.1f}" y="{Ypx(wt_top_ft):.1f}" '
                 f'width="{pw+2*wt_o:.1f}" height="{(wt_top_ft*scale):.1f}"/>')
        # The moulded courses the pack authors and nothing drew: front-on, each member reads as
        # the line where it meets the one below. The ovolo course is the whole point of a water
        # table's grade -- an ogee is the better work and a plain bevel the cheap.
        for mm in (wtb.get("water_table_members") or [])[:-1]:
            yy = Ypx(mm["y_top_in"] / 12.0)
            mo = proj_px(mm.get("projection_in"))
            s.append(f'<line class="wtm" x1="{X(0)-mo:.1f}" y1="{yy:.1f}" x2="{X(span_ft)+mo:.1f}" y2="{yy:.1f}"/>')
        if wtb.get("belt_height_above_first_floor_in") is not None:
            belt_ft = floor2_ft
            belt_h_ft = wtb["belt_height_in"] / 12.0
            # A brick belt has no projection rule of its own in the pack (it reads as a course,
            # not a board), so it is drawn flush and says so by being flush -- not nudged out.
            bo = proj_px(wtb.get("belt_course_projection_in"))
            s.append(f'<rect class="wt w-med" x="{X(0)-bo:.1f}" y="{Ypx(belt_ft+belt_h_ft):.1f}" '
                     f'width="{pw+2*bo:.1f}" height="{(belt_h_ft*scale):.1f}"/>')

    # BRICK COURSING. brick-course.json fixes one course at module/parts and its own note says
    # why it matters: "in a brick building there are no free horizontal dimensions above the
    # water table". Every sill, head, belt and eave lands on a bed joint or the wall is wrong,
    # and until now the drawing could not show that at all.
    if wtb.get("course_height_in"):
        c_ft = wtb["course_height_in"] / 12.0
        y = (wtb["water_table_height_above_finished_grade_in"] / 12.0) if wtb["applicable"] else 0.0
        n = 0
        while y < top_of_wall_ft - c_ft * 0.5 and n < 400:
            y += c_ft; n += 1
            s.append(f'<line class="course" x1="{X(0):.1f}" y1="{Ypx(y):.1f}" x2="{X(span_ft):.1f}" y2="{Ypx(y):.1f}"/>')

    # frieze + cornice band, front-on, at its own stated projection (its full moulded profile is
    # drawn to scale in the detail inset -- a 24 in run of mouldings cannot be traced in a band
    # five pixels deep, and pretending otherwise is how the inset earned its place).
    co = proj_px(cornice.get("envelope_projection_in") or cornice.get("cornice_projection_in"))
    s.append(f'<rect class="bd w-prof" x="{X(0)-co:.1f}" y="{Ypx(true_eave_ft):.1f}" '
             f'width="{pw+2*co:.1f}" height="{(cornice_band_ft*scale):.1f}"/>')
    # the frieze band's own bed, which is where the cornice assembly actually starts
    fz = cornice.get("frieze_height_in")
    if fz:
        s.append(f'<line class="wtm" x1="{X(0):.1f}" y1="{Ypx(true_eave_ft - (cornice["cornice_height_in"]/12.0)):.1f}" '
                 f'x2="{X(span_ft):.1f}" y2="{Ypx(true_eave_ft - (cornice["cornice_height_in"]/12.0)):.1f}"/>')

    for cx, kind in zip(front["centres_ft"], front["kinds"]):
        if kind == "door" and face == elev["entrance_face"]:
            s.append(_entrance(elev, cx, floor1_ft, X, Ypx, scale))
        else:
            s.append(_window(s, cx, floor1_ft + gw["sill_height_above_floor_in"]/12.0, floor1_ft + gw["head_height_above_floor_in"]/12.0,
                              gw["opening_width_in"], gw["lights_across"], gw["lights_high_per_sash"],
                              gw["shutter_leaf_width_in"], gw["shutter_leaf_height_in"], X, Ypx, scale,
                              head=gw.get("head_treatment"), sill_in=wtb.get("course_height_in")))
        s.append(_window(s, cx, floor2_ft + uw["sill_height_above_floor_in"]/12.0, floor2_ft + uw["head_height_above_floor_in"]/12.0,
                          uw["opening_width_in"], uw["lights_across"], uw["lights_high_per_sash"],
                          uw["shutter_leaf_width_in"], uw["shutter_leaf_height_in"], X, Ypx, scale,
                          head=uw.get("head_treatment"), sill_in=wtb.get("course_height_in")))

    # roofline -- build/roof.py's own elevation_profile() numbers, shifted up by the cornice band
    # this file adds (see ridge_delta_ft above), not re-derived
    pts = " ".join(f"{X(x):.1f},{Ypx(h):.1f}" for x, h in profile_ft)
    s.append(f'<polyline class="rf" points="{pts}"/>')

    # CHIMNEYS, AND THE ONE THING THIS SHEET STILL CANNOT SHOW.
    #
    # The width was a hardcoded 36 in -- the exact class of invented constant OQ 52 removed from
    # the measurements, still being asserted by the drawing where no test could see it. It is now
    # the corpus's own figure (brick-course, eight courses square, 22 in), and because that rule
    # is flagged `judgment: true` the sheet says so rather than presenting a decision as a fact.
    #
    # The stacks are NOT drawn on the front, and the reason is worth writing down rather than
    # leaving as an apparent oversight. On this style they are the most diagnostic thing on the
    # house -- the kit says the paired stacks joined by an arched curtain are "visible from a
    # mile away and conclusive against New England" -- so a front elevation without them is a
    # real loss. But build/roof.py's long-face silhouette is FLAT AT THE EAVE: for the S face of
    # this side-gable house it returns exactly two points, both at 25.44 ft, and models no roof
    # mass above the cornice at all. Without that surface there is nothing to say which part of a
    # 47 ft stack is hidden behind the roof and which part clears it. Drawing the whole stack
    # from the eave up would put 22 ft of brick in front of a roof nobody modelled, which is the
    # same error as reporting an unmodelled chimney as zero. The gable faces, whose silhouettes
    # DO carry the ridge, keep their stacks. This is a roof-layer gap, and it is an open question
    # rather than something this renderer may decide.

    if is_gable_end and roof.get("chimneys", {}).get("applicable"):
        depth_ft = fp["depth_ft"]
        for c in roof["chimneys"]["positions"]:
            # chimney x_ft/y_ft are in the ROOF's own plan-view frame (x along ridge axis, y across
            # it); on a gable-end face the wall's own horizontal axis IS that plan-view y -- only
            # chimneys at THIS gable-end wall (x_ft matching 0 or the far end) actually sit in this
            # face's plane, per roof.py's own WP-3.3 finding (both chimneys are gable-end, one per end)
            if not (abs(c["x_ft"]) < 0.5 or abs(c["x_ft"] - span_ft) < 0.5):
                continue
            near_left = abs(c["x_ft"]) < 0.5
            cx_ft = 3.0 if near_left else depth_ft - 3.0
            # the corpus's own stack, not a 36 in constant (see the note above)
            cw_ft = (elev.get("chimney_stack_plan_in") or 22.0) / 12.0
            cy0, cy1 = c["grade_to_ridge_ft"] - 2.0, c["total_height_grade_ft"]
            s.append(f'<rect class="ch" x="{X(cx_ft-cw_ft/2):.1f}" y="{Ypx(cy1+ridge_delta_ft):.1f}" '
                      f'width="{cw_ft*scale:.1f}" height="{((cy1-cy0)*scale):.1f}"/>')

    legend_y = oy + ph + 22
    m = roof["main"]
    pitch_txt = f'{m["pitch_rise_per_12"]}:12' if m.get("pitch_rise_per_12") else "pitch unjudged"
    s.append(f'<text class="lb" x="{pad}" y="{legend_y:.1f}">{_esc(elev.get("style",""))} · {front["count"]} BAYS · '
              f'{_esc(m.get("form",""))} {pitch_txt} · GLASS MODULE {elev["glass_module_in"]} IN ({_esc(str(elev.get("date_of_representation") or "undated"))})</text>')
    s.append(f'<text class="dm" x="{pad}" y="{legend_y+14:.1f}">GROUND {gw["opening_width_in"]}×{gw["opening_height_in"]} in, {gw["sash_pattern"]} '
              f'· UPPER {uw["opening_width_in"]}×{uw["opening_height_in"]} in, {uw["sash_pattern"]} '
              f'· CORNICE {cornice["cornice_height_in"]} in ({cornice["member_count"]} members) · SEE INSET FOR PROFILE</text>')

    # WHAT THIS SHEET COULD NOT JUDGE, AND WHAT ON IT IS SOMEBODY'S DECISION.
    #
    # Both of these were carried in the record and printed nowhere until 27 Aug 2026. The chimney
    # one is the worse miss: a twenty-line comment in build/elevation.py, this package's own
    # report and its commit message all said the stack size reaches the drawing "labelled a
    # judgment", and the words appeared on no sheet. An assurance stated in three documents and
    # implemented in none is worth less than no assurance at all.
    notes = []
    ht = (gw.get("head_treatment") or {})
    if ht and not ht.get("kind") and ht.get("kind_note"):
        notes.append(f'WINDOW HEAD UNJUDGED — {ht["kind_note"].upper()}')
    elif ht.get("rise_band_in"):
        notes.append(f'HEAD RISE IS A BAND OF {ht["rise_band_in"][0]}–{ht["rise_band_in"][1]}″ '
                     f'({_esc(str(ht.get("rise_source") or ""))}); DRAWN AT ITS MIDPOINT')
    if elev.get("chimney_stack_plan_judgment") and elev.get("chimney_stack_plan_in"):
        notes.append(f'STACK DRAWN {elev["chimney_stack_plan_in"]}″ SQUARE — A JUDGMENT, NOT A '
                     f'MEASUREMENT: THE COURSING PUTS IT BETWEEN SIZES AND A MASON WILL BUILD 18″ OR 27″')
    for i, n in enumerate(notes):
        s.append(f'<text class="dm" x="{pad}" y="{legend_y+26+i*10:.1f}">{_esc(n)}</text>')

    # ---------------- cornice detail inset: the actual moulded profile, constructed by
    # build/profiles.py from proportion_engine.dimension() members.
    #
    # The naked matters here and used to be assumed away. This pack's projections are radii from
    # the column AXIS (it declares projection_datum: "axis"), so drawing them as relief from a
    # naked of 0 drew the whole radius as though it were overhang -- 24.56 in where the true
    # relief beyond the frieze face is 10.35 in, a cornice 2.37x too deep, and out of step with
    # the very band this same sheet draws from facade-classical's own 10.53 in figure. The record
    # now states the datum and the plane, and this reads them.
    # A cornice profile is a TALL, NARROW thing: at Gibbs Ionic reduced, 24.6 in of height against
    # 10.3 in of relief. Fitting it to a box as wide as it is tall left it using a third of the
    # width and reading as a blob. The width belongs to what a detail plate actually uses it for --
    # every member named, at its own height, with the leader that says which shape is which.
    ibox_x, ibox_y = ox + pw + 30, oy + 6
    ibox_w, ibox_h = inset_w - 12, ph * 0.86
    naked_in = cornice.get("frieze_naked_in") or 0.0
    # The ENTABLATURE's own datum, which is not always the pack's declared one -- see
    # elevation.py::eave_cornice. Reading the pack-level `axis` over a cornice whose frieze
    # records a projection of 0 clamps its bed mould flush and deletes it from the drawing.
    from_axis = cornice.get("entablature_projection_datum", cornice.get("projection_datum")) == "axis"
    relief = cornice.get("order_relief_beyond_frieze_in") or max(
        (mm["projection_in"] for mm in cornice["members"]), default=1.0)
    members = cornice["members"]
    drawn_h = max((mm["y_top_in"] for mm in members), default=1.0) or 1.0
    prof_w = ibox_w * 0.34                       # the profile's own column; the rest is legend
    ik = min(prof_w / max(relief, 1.0), (ibox_h - 34) / drawn_h)
    px0, py0 = ibox_x + 16, ibox_y + 20          # profile origin: frieze face, springing of the bed
    isx = lambda x: px0 + (x - naked_in) * ik
    isy = lambda y: py0 + (drawn_h - y) * ik

    s.append(f'<rect class="pf" x="{ibox_x:.1f}" y="{ibox_y:.1f}" width="{ibox_w:.1f}" height="{ibox_h:.1f}"/>')
    s.append(f'<text class="lb" x="{ibox_x+8:.1f}" y="{ibox_y-4:.1f}">EAVE CORNICE PROFILE</text>')
    # The frieze face, which is the plane every projection above is measured against.
    s.append(f'<line x1="{isx(naked_in):.1f}" y1="{isy(0):.1f}" x2="{isx(naked_in):.1f}" y2="{isy(drawn_h):.1f}" '
             f'stroke="{PAL["ink3"]}" stroke-width="0.5" stroke-dasharray="2 2"/>')
    sil = PROF.silhouette(members, naked_at=naked_in, from_axis=from_axis)
    d = PROF.svg_path(sil["segments"], isx, isy, start=sil["start"])
    if d:
        s.append(f'<path d="{d}" fill="{PAL["brass"]}" fill-opacity="0.5" stroke="{PAL["ink"]}" stroke-width="0.9"/>')

    # Member leaders. Each member is named at its own height, decluttered downward so two thin
    # members cannot print over each other -- a label that overlaps its neighbour names nothing.
    # Members arrive bottom-to-top, so screen y DECREASES as the list advances: the declutter
    # pushes each label UP off the one below it. Nudging downward instead walked the whole legend
    # off the bottom of the plate, which is the sort of thing only looking at the drawing finds.
    lx = ibox_x + ibox_w * 0.46
    n_cap = 3 + (1 if sil["unconstructed"] else 0)
    band_top, band_bot = ibox_y + 16, ibox_y + ibox_h - 10 - n_cap * 9
    gap = min(8.4, max(6.2, (band_bot - band_top) / max(len(members), 1)))
    anchors = [isy((m["y_bottom_in"] + m["y_top_in"]) / 2.0) for m in members]
    ys, last = [], None
    for a in anchors:                          # bottom-to-top: each label clears the one below it
        y = a if last is None else min(a, last - gap)
        ys.append(y)
        last = y
    over = ys[0] - band_bot                    # the lowest label is members[0]'s
    if over > 0:
        ys = [y - over for y in ys]
    under = band_top - ys[-1]                  # ... and the highest is the last
    if under > 0:                              # both bounds bite at once: compress onto the band
        span = max(ys[0] - ys[-1], 1e-6)
        ys = [band_bot - (ys[0] - y) * ((band_bot - band_top) / span) for y in ys]
    for m, anchor, my in zip(members, anchors, ys):
        face = isx(PROF.outer_face(naked_in, m.get("projection_in") or 0.0, from_axis))
        s.append(f'<line x1="{face+1:.1f}" y1="{anchor:.1f}" x2="{lx-3:.1f}" y2="{my:.1f}" '
                 f'stroke="{PAL["ink3"]}" stroke-width="0.35"/>')
        nm = (m.get("profile") or "flat").replace("-", " ").upper()
        s.append(f'<text class="dm" x="{lx:.1f}" y="{my+2.6:.1f}">{_esc(nm)} {m["height_in"]:.2f}″</text>')

    # The two dimensions a millworker would take off this plate first.
    dy = isy(drawn_h) - 8
    s.append(f'<line x1="{isx(naked_in):.1f}" y1="{dy:.1f}" x2="{isx(naked_in)+relief*ik:.1f}" y2="{dy:.1f}" '
             f'stroke="{PAL["brass"]}" stroke-width="0.6"/>')
    s.append(f'<text class="dm" x="{isx(naked_in):.1f}" y="{dy-3:.1f}">RELIEF {relief:.1f}″</text>')
    hx = ibox_x + 7
    hym = (isy(0) + isy(drawn_h)) / 2
    s.append(f'<line x1="{hx:.1f}" y1="{isy(0):.1f}" x2="{hx:.1f}" y2="{isy(drawn_h):.1f}" '
             f'stroke="{PAL["brass"]}" stroke-width="0.6"/>')
    s.append(f'<text class="dm" x="{hx-4:.1f}" y="{hym:.1f}" '
             f'transform="rotate(-90 {hx-4:.1f} {hym:.1f})" text-anchor="middle">{drawn_h:.1f}″</text>')

    # Caption, wrapped to the plate's own measure rather than run off its edge. `.dm` is the
    # monospaced class, so a character count is a real width here.
    env = cornice.get("envelope_projection_in")
    cap = [f'GIBBS IONIC · {len(members)} MEMBERS AT A {round(cornice["reduced_gibbs_module_in"],1)}″ MODULE',
           ("PROJECTIONS ARE RADII FROM THE COLUMN AXIS" if from_axis
            else "PROJECTIONS ARE RELIEF FROM THE FRIEZE NAKED")]
    if env and abs(env - relief) > 0.5:
        # Two sourced rules, one address, different answers. The sheet names both rather than
        # letting the reader believe the drawing settled it.
        cap.append(f"ORDER PROJECTS {relief:.1f}″; THE DOMESTIC ENVELOPE RULE SAYS {env:.1f}″ — BOTH SOURCED")
    if sil["unconstructed"]:
        # Never draw a shape this corpus has no construction for without saying which.
        cap.append(", ".join(sorted({u["profile"].upper() for u in sil["unconstructed"]})) + " NOT CONSTRUCTED")
    if sil.get("unrecorded"):
        # A face drawn flush because the authority published no figure looks exactly like a face
        # measured flush. Saying which is the whole difference.
        cap.append(f'{len(sil["unrecorded"])} MEMBER(S) DRAWN AT THE NAKED — NO PROJECTION PUBLISHED')
    lines = [ln for c in cap for ln in _wrap(c, int((ibox_w - 16) / 4.3))]
    for i, ln in enumerate(lines):
        s.append(f'<text class="dm" x="{ibox_x+8:.1f}" '
                 f'y="{ibox_y+ibox_h-6-(len(lines)-1-i)*9:.1f}">{_esc(ln)}</text>')

    s.append('</svg>')
    open(path, "w").write("\n".join(s))
    return path

# ---------------------------------------------------------------- cli
def main():
    import argparse, json, sys
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    from importlib.util import spec_from_file_location, module_from_spec
    def _mod(n, p):
        spec = spec_from_file_location(n, p); m = module_from_spec(spec); spec.loader.exec_module(m); return m
    EL = _mod("elevation_for_render", f"{ROOT}/build/elevation.py")
    ap = argparse.ArgumentParser()
    ap.add_argument("plan"); ap.add_argument("--parti"); ap.add_argument("--out", required=True); ap.add_argument("--face")
    a = ap.parse_args()
    plan = json.load(open(a.plan))
    parti = json.load(open(f"{ROOT}/partis/{a.parti}.json")) if a.parti else None
    elev = EL.build_elevation(plan, parti)
    if "error" in elev:
        print(elev["error"]); sys.exit(1)
    render_elevation(elev, a.out, face=a.face)
    print(f"wrote {a.out}")

if __name__ == "__main__":
    main()
