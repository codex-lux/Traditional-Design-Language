#!/usr/bin/env python3
"""Render a WP-3.2 elevation record (build/elevation.py's build_elevation()) to SVG -- a single
front-on face: wall plane, bay windows with sash/muntin grid and shutters, the entrance
composition (door, surround, entablature, sidelights where present), water table and belt course,
and the roofline (reusing build/roof.py's own elevation_profile(), not re-derived here), plus a
cross-section detail inset that draws the eave cornice's ACTUAL moulded profile.

That inset is the reason this file exists rather than just drawing flat bands everywhere.

WP-5.11 replaced this file's own seg_to()/profile_silhouette_path() -- the line-for-line port of
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

  render_elevation(elev, path, face=None, scale=24.0)   # 1/4 in = 1 ft
"""
import math, os, importlib.util

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
# WP-12.2: the opening rectangle and the loop around it are `elevation.opening_rects`,
# read here rather than transcribed. Loaded through modcache like every other sibling, so
# it is the same module object `build_elevation` came from.
EL = _mod("elevation", f"{ROOT}/build/elevation.py")

SS = _mod("sheet_style", f"{ROOT}/build/sheet_style.py")

# The palette is build/sheet_style.py's now -- ONE spelling, not four. It carried a verbatim
# copy of the same ten-key dict, under a comment saying the duplication was the price of every
# build/*.py module being loadable standalone; modcache.load answers that, and the copies were
# the reason a colour could be changed in one renderer and not in its neighbours. `DARK` is
# byte-for-byte what stood here, proved over all ten sheets corpus.drawing() produces.
# This one is the SUPERSET: the same ten plus four material tones of its own.
PAL = SS.DARK_ELEVATION

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


def _segment(x0, x1, y_spring, rise):
    """The circle a segmental soffit is set out on, in px with y down: (cx, cy, R). It passes
    through both springings, (x0, y_spring) and (x1, y_spring), and through the crown, `rise`
    above their midpoint. R = (span^2 / 4 + rise^2) / (2 x rise), the chord-and-sagitta rule."""
    half = (x1 - x0) / 2.0
    R = (half * half + rise * rise) / (2.0 * rise)
    return (x0 + x1) / 2.0, y_spring - rise + R, R


def _on_circle(cx, cy, R, px, py, R2):
    """The point at radius R2 on the ray from the centre through (px, py), a point at radius R:
    where a radial skewback meets the extrados."""
    return cx + (px - cx) * R2 / R, cy + (py - cy) * R2 / R


def _rect_edges(cls, x0, y0, x1, y1, nd=2):
    """A rectangle written from its EDGES, rounded once (WP-14.3).

    The sash's members abut: a stile's inside face IS the rail's end and the glass's edge. Written
    as `x="{x0:.2f}" width="{x1 - x0:.2f}"` each rectangle rounded its origin and its width
    separately, so two members computed to meet exactly were written up to 0.01 px apart -- a
    hairline of glass through the frame on 15 faces, which census V14 read as a light 0.00 to
    0.02 in wide. Rounding the edges and deriving the width from them makes abutting edges one
    printed number."""
    a, b, c, d = (round(v, nd) for v in (x0, y0, x1, y1))
    return (f'<rect class="{cls}" x="{a:.{nd}f}" y="{b:.{nd}f}" '
            f'width="{c - a:.{nd}f}" height="{d - b:.{nd}f}"/>')

def _style_block():
    # THE WEIGHT LADDER (WP-5.11). Five rungs, and the rung carries the meaning a drawing conveys
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
            # THE LINE LADDER, on the Historic American Buildings Survey's own rungs. HABS
            # specifies, for a sheet plotted at 1/4 in = 1 ft:
            #   0.1 mm  joint lines -- brick coursing, floorboards, shingle courses
            #   0.2 mm  light edges -- a small change in surface plane
            #   0.3 mm  medium edges
            #   0.4 mm  heavy edges -- "indicating major depth change"
            #   0.5 mm  material cut lines
            #   0.6 mm  the GROUND LINE in elevation, the heaviest line on the sheet
            # What carries over is the RATIO -- 6:1 end to end, with adjacent rungs about root 2
            # apart so a reader tells them apart at a glance (ISO 128's own series). The five
            # names below predate WP-5.13 and are kept; `w-ground` is the sixth rung, which this
            # sheet did not have and which HABS makes the heaviest thing on it.
            # THE RUNG RULES THEMSELVES ARE WRITTEN LAST, at the foot of this block, and where they
            # stand is the whole of what they mean (WP-14.3): see the comment there.
            f'.course{{stroke:{PAL["ink3"]};stroke-width:0.3;stroke-opacity:0.42;fill:none}}'
            # A GAUGED ARCH IS DRAWN BRICK BY BRICK -- HABS 4.6.2 names round, jack and flat
            # arches as the one place individual bricks are always drawn even where the rest of
            # the wall is only coursed. Rubbed brick reads slightly LIGHTER than the field, and
            # the arch and the jambs are the only tonal event on a Chesapeake brick front, so it
            # carries a light wash rather than the solid block it was drawn as.
            f'.arch{{fill:{PAL["ink"]};fill-opacity:0.10;stroke:{PAL["ink"]};stroke-opacity:0.8}}'
            f'.vsr{{stroke:{PAL["ink"]};stroke-opacity:0.55;fill:none}}'
            f'.sill{{fill:{PAL["rule"]};stroke:{PAL["ink3"]};stroke-width:0.45}}'
            f'.wtm{{stroke:{PAL["ink"]};stroke-width:0.45;fill:none}}'
            f'text{{font-family:"Archivo",-apple-system,"Segoe UI",sans-serif;fill:{PAL["ink2"]}}}'
            f'.dm{{font-size:7.5px;fill:{PAL["ink3"]};font-family:ui-monospace,Menlo,monospace}}'
            f'.hd{{font-family:"Bodoni Moda",Georgia,serif;font-size:19px;fill:{PAL["ink"]}}}'
            f'.lb{{font-family:ui-monospace,Menlo,monospace;font-size:8.5px;letter-spacing:.14em;fill:{PAL["ink3"]}}}'
            f'.wf{{fill:{PAL["wall"]};stroke:{PAL["ink3"]};stroke-width:0.6}}'
            # GLASS IS A TONE, NOT A HOLE. HABS 4.6.6, and the older drawn practice the manual
            # praises: "Glass areas are black." A pane left the colour of the sheet reads as a
            # gap in the wall; a dark even tone reads as glass, and it is what lets the muntin
            # grid sit ON something. Diagonal glazing hatches are the fastest way to make a
            # careful elevation look like an estate agent's drawing -- HABS forbids generated
            # hatch patterns outright.
            # GLASS IS A TONE, NOT A HOLE -- HABS 4.6.6, and the older drawn practice the manual
            # praises: "Glass areas are black." A pane left the colour of the sheet reads as a gap
            # in the wall; a dark even tone reads as glass and lets the muntin grid sit ON
            # something. No diagonal glazing hatch: HABS forbids generated hatch patterns.
            #
            # POLARITY TRAP, and it cost an hour here on 27 Aug 2026. This file draws in a DARK
            # palette and `workbench/server/svg_theme.py` substitutes it hex-for-hex to the light
            # sheet the workbench actually serves. So a colour that looks dark HERE is light
            # THERE. `PAL["glass"]` exists for exactly this: svg_theme maps it to the coal the
            # Drawn Language reserves for glazing. The convention is about the DELIVERED sheet,
            # and judging these choices from the dark preview inverts every one of them.
            #
            # Do not write the light-theme hex here, even in a comment. test_m3_drawings.py's
            # totality check reads this file for hex literals and cannot tell a comment from
            # code -- and a TARGET colour has no HEX_MAP entry by definition, so naming one is
            # indistinguishable from a renderer colour nobody themed.
            f'.op{{fill:{PAL["glass"]};stroke:{PAL["ink"]};stroke-width:1.1}}'
            # A muntin against dark glass is drawn in the LIGHT colour: it is a solid bar in front
            # of the pane, and at 1/4 in = 1 ft a 7/8 in bar is 1.75 px, which is a real line.
            # The muntin is a solid bar in FRONT of the pane, so it is drawn light against the
            # coal -- `paper` here, which is the sheet's own colour once themed. At 1/4 in = 1 ft
            # a 7/8 in bar is 1.75 px, which is a real line rather than a suggestion.
            f'.mt{{fill:{PAL["paper"]};stroke:none}}'
            # THE SASH'S OWN MEMBERS (WP-14.3), light against the glass as the muntins are, and
            # drawn at their stated widths rather than as lines: a stile is 2 in, the bottom rail 3.
            f'.sf{{fill:{PAL["paper"]};stroke:none}}'
            f'.mj{{stroke:{PAL["ink"]};fill:none}}'
            f'.sh{{fill:{PAL["shutter"]};stroke:{PAL["ink"]};stroke-width:0.6}}'
            f'.dr{{fill:{PAL["copper"]};stroke:{PAL["ink"]};stroke-width:0.8}}'
            f'.cs{{fill:none;stroke:{PAL["brass"]};stroke-width:1.0}}'
            f'.bd{{fill:{PAL["wall"]};stroke:{PAL["ink2"]};stroke-opacity:0.9}}'
            f'.rf{{fill:{PAL["iron"]};fill-opacity:0.28;stroke:{PAL["ink"]};stroke-width:1.4;stroke-linejoin:round}}'
            # A shingle course is a JOINT LINE -- HABS's lightest rung, 0.1 mm, the same weight it
            # gives brick coursing. It is the covering indicated, not the covering drawn.
            f'.shingle{{stroke:{PAL["ink"]};stroke-width:0.4;stroke-opacity:0.5;fill:none}}'
            f'.pnl{{fill:none;stroke:{PAL["ink"]};stroke-opacity:0.75}}'
            f'.gl{{stroke:{PAL["ink"]};fill:none}}'
            f'.shade{{stroke:{PAL["ink"]};stroke-opacity:0.92;fill:none;stroke-linecap:square}}'
            f'.wt{{fill:{PAL["rule"]};stroke:{PAL["ink3"]};stroke-width:0.6}}'
            f'.ch{{fill:{PAL["iron"]};stroke:{PAL["ink"]};stroke-width:0.6}}'
            f'.pf{{fill:{PAL["paper"]};stroke:{PAL["ink2"]};stroke-width:0.7}}'
            # THE RUNGS COME LAST, BECAUSE A RUNG IS A DECISION ABOUT ONE MARK (WP-14.3). A class
            # rule above (`.sh`, `.mt`, `.rf`, `.wt`, `.dr`, `.ch`) sets the width its marks take
            # when nothing more is said; a rung written on the element says more, and must win.
            # Both are one class, so the cascade decides by SOURCE ORDER alone, and with the rungs
            # written first every class rule below them silently beat them: the meeting rail --
            # 'the thickest bar in the window' -- drew at the muntin's 1.0 under its own `w-med`,
            # the roof edge at 1.4 under `w-prof`, the water table at 0.6 under both. Census V1
            # measured it on all 44 elevation sheets, reading the COMPUTED width, which is the only
            # reading that can see an ordering defect: the attribute says what was asked for.
            f'.w-hair{{stroke-width:0.4}}.w-fine{{stroke-width:0.8}}.w-med{{stroke-width:1.2}}'
            f'.w-prof{{stroke-width:1.6}}.w-cut{{stroke-width:2.0}}.w-ground{{stroke-width:2.4}}'

            f'</style>')

# ---------------------------------------------------------------- window / door drawing
def _window(s, rect, lights_across, lights_high, shutter_w, shutter_h, X, Ypx, scale,
            head=None, sill_in=None, panel_count=None, reveal_in=None, muntin_in=None):
    """WP-12.2: THE RECTANGLE IS HANDED TO THIS FUNCTION AND NEVER COMPUTED IN IT.

    `(x0, x1, sill, head)` used to be worked out here, again in `_entrance` below, and a third
    time in `export_dxf._win` — so did the loop around them, which is how the CAD file went on
    drawing a blind bay for as long as it did. It is `elevation.opening_rects(elev, face)` now,
    in inches above grade, and this draws what it is given. The dormer caller builds its own
    rectangle from `dormers()`' numbers, because a dormer window on a roof plane is a different
    rectangle and not this one.
    """
    x0, x1 = X(rect["x0_in"] / 12.0), X(rect["x1_in"] / 12.0)
    yb, yt = Ypx(rect["sill_in"] / 12.0), Ypx(rect["head_in"] / 12.0)
    width_in = rect["x1_in"] - rect["x0_in"]
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
        # THE OPENING'S OWN RISE (WP-14.3): `opening_rects` evaluates brick-course's rule at the
        # width this window is drawn; the storey's figure was taken at another width. A dormer's
        # window carries none and takes the storey's.
        rise_in = rect.get("head_rise_in") if "head_rise_in" in rect else head.get("rise_in")
        if rise_in is None and head.get("rise_band_in"):
            rise_in = sum(head["rise_band_in"]) / 2.0     # a band's midpoint, named in the legend
        rise = (rise_in or 0.0) / 12.0 * scale
        ax0, ax1 = x0, x1                                  # flush with the jambs
        # THE SOFFIT IS A CIRCULAR SEGMENT, drawn as one (WP-14.3, census V7). A head with a rise
        # is set out on the circle through its two springings and its crown; it was drawn as a
        # quadratic Bezier, which is a parabola. On a gauged flat arch's 0.4 in camber the two
        # cannot be told apart at this scale, and that is all WP-14.1's census could see, because
        # its style sweep drew the Tidewater house every time. Drawn as themselves, 13 styles set
        # a head rising 4.2 to 5 in -- 12 keyed segmental arches and one keystoned flat arch at its
        # kit's stated rise -- and every one departed from its circle.
        seg = _segment(ax0, ax1, yt, rise) if rise > 1e-6 else None
        soffit = (f'M {ax0:.2f},{yt:.2f} A {seg[2]:.3f},{seg[2]:.3f} 0 0 1 {ax1:.2f},{yt:.2f}'
                  if seg else f'M {ax0:.2f},{yt:.2f} L {ax1:.2f},{yt:.2f}')
        if "segmental" in head["kind"] and seg:
            # A SEGMENTAL ARCH IS CONCENTRIC. Its extrados is the soffit's circle grown by the
            # arch's own depth, and its skewbacks are RADIAL, so the extrados springs outside
            # the jambs. It was the soffit moved up by the depth with vertical ends, which is a
            # band of brick of constant height and not an arch.
            cx, cy, R = seg
            R2 = R + hd
            (e1x, e1y), (e0x, e0y) = (_on_circle(cx, cy, R, ax1, yt, R2),
                                      _on_circle(cx, cy, R, ax0, yt, R2))
            out.append(f'<path class="arch w-med" d="{soffit} L {e1x:.2f},{e1y:.2f} '
                       f'A {R2:.3f},{R2:.3f} 0 0 0 {e0x:.2f},{e0y:.2f} Z"/>')
        else:
            # A GAUGED FLAT ARCH IS A TRAPEZOID, not a rectangle. Its skewbacks are cut at 60
            # degrees from the horizontal -- the mason's standard for gauged work -- so over the
            # arch's own depth the extrados runs out past the soffit by depth/tan(60) at EACH
            # end. Drawing it square hides the skewback, which is the joint that makes a flat
            # arch stand up, and left the outermost voussoir joints running off into the wall.
            skew = hd / math.tan(math.radians(60.0))
            out.append(f'<path class="arch w-med" d="{soffit} '
                       f'L {ax1+skew:.2f},{yt-hd:.2f} L {ax0-skew:.2f},{yt-hd:.2f} Z"/>')
        # THE VOUSSOIRS. An ODD number, so a single brick sits on the centre line rather than a
        # joint splitting it, and they radiate to a strike point below the soffit -- for a gauged
        # flat arch the skewback is taken at 60 degrees from the horizontal, which puts the strike
        # at (span/2) x tan 60 below. The joints are the whole reading of a gauged arch: they are
        # 1/16 to 1/8 in of lime putty against 3/8 in of mortar in the field, which is why the
        # arch reads as one smooth block of brick from across a street and as radiating lines
        # close up. The COUNT is not published for any measured Chesapeake arch, so it is derived
        # from the corpus's own arch depth at one brick per course-and-a-bit and forced odd, and
        # the sheet says the count is derived rather than measured.
        span_px = ax1 - ax0
        # A voussoir is a rubbed brick set on edge, so its width at the soffit is one brick
        # height -- the corpus's own course figure, 2.75 in, which is the only brick dimension
        # this corpus states. Over this plan's 38.6 in opening that gives thirteen, inside the
        # 11-13 a survey of gauged Chesapeake work would lead you to expect. Deriving it from the
        # ARCH DEPTH instead gave five, which is a voussoir eight inches wide at the soffit: not
        # a brick.
        v_w = (sill_in or 2.75) / 12.0 * scale
        if "segmental" in head["kind"] and seg:
            # A SEGMENTAL ARCH'S JOINTS RADIATE FROM ITS OWN CENTRE, from the soffit to the
            # extrados, at one brick height along the SOFFIT'S ARC. They radiated to the gauged
            # flat arch's 60-degree strike point and began on the chord, below the soffit, so
            # every joint of a segmental head crossed the band of wall under the arch.
            cx, cy, R = seg
            a0 = math.atan2(yt - cy, ax0 - cx)
            a1 = math.atan2(yt - cy, ax1 - cx)
            n_v = max(5, int(round(R * (a1 - a0) / max(v_w, 1e-6))))
            n_v += (1 - n_v % 2)                    # odd: a brick on the centre line, not a joint
            for i in range(1, n_v):
                a = a0 + (a1 - a0) * i / n_v
                ca, sa = math.cos(a), math.sin(a)
                out.append(f'<line class="vsr w-hair" x1="{cx + R * ca:.2f}" y1="{cy + R * sa:.2f}" '
                           f'x2="{cx + (R + hd) * ca:.2f}" y2="{cy + (R + hd) * sa:.2f}"/>')
        else:
            n_v = max(5, int(round(span_px / max(v_w, 1e-6))))
            n_v += (1 - n_v % 2)                    # odd: a brick on the centre line, not a joint
            strike_y = yt + (span_px / 2.0) * math.tan(math.radians(60.0))
            for i in range(1, n_v):
                fx = ax0 + span_px * (i / n_v)
                dx, dy = fx - (ax0 + ax1) / 2.0, yt - strike_y
                if abs(dy) < 1e-6:
                    continue
                tx = fx + dx * (hd / abs(dy)) if dy else fx
                out.append(f'<line class="vsr w-hair" x1="{fx:.1f}" y1="{yt:.1f}" '
                           f'x2="{tx:.1f}" y2="{yt-hd:.1f}"/>')

        if head.get("keystone"):
            # The kit makes a keystone canonical. Its WIDTH may be a band, drawn at its midpoint
            # and said in the legend. An UNSTATED width is not drawn at all (WP-14.3): it fell back
            # to 0.6 x the arch's depth, a figure no record states, under a comment promising a
            # legend line that did not exist. The legend says the keystone is not drawn.
            kw = head.get("keystone_width_in")
            kw = (sum(kw) / 2.0 if isinstance(kw, list) else kw)
            if kw:
                kwp = kw / 12.0 * scale
                out.append(f'<rect class="arch w-med" x="{(x0+x1)/2 - kwp/2:.1f}" y="{yt-hd:.1f}" '
                           f'width="{kwp:.1f}" height="{hd:.1f}"/>')

    # THE SILL. One course of purpose-moulded brick, which is what the kit states; its
    # projection is recorded as a BAND of 0 to 1 in and a band is not a figure, so it is drawn
    # flush rather than given a point value nobody published.
    if sill_in:
        sh = sill_in / 12.0 * scale
        out.append(f'<rect class="sill" x="{x0:.1f}" y="{yb:.1f}" width="{x1-x0:.1f}" height="{sh:.1f}"/>')

    # THE OPENING AT THE SASH'S OWN PRECISION: its edges are the jambs' outer faces, and written
    # to a tenth of a pixel beside members written to a hundredth they missed each other by up to
    # 0.05 px -- the same hairline of glass `_rect_edges` exists to close, one member out.
    out.append(_rect_edges("op", x0, yt, x1, yb))
    # THE MEETING RAIL is the thickest bar in the window -- 1 1/4 in against a 7/8 in muntin --
    # and it is the line that tells a reader the sash is double-hung rather than a fixed grid.
    # THE REVEAL. In solid masonry of this tradition the frame sits BACK from the wall face -- the
    # corpus resolves `none-masonry-reveal` and a 4-8 in reveal -- and that recess is the single
    # thing that makes a brick elevation read as a mass with holes in it rather than as a flat
    # plane with rectangles drawn on. Light over the left shoulder at 45 degrees puts the shadow
    # on the HEAD and the LEFT JAMB, inside the opening, to a depth equal to the reveal.
    #
    # The reveal is a BAND in the corpus (4 to 8 in), not a figure, so what is drawn is the
    # shadow's presence and not a measured depth: the shade line goes on the two edges the
    # geometry puts it on, and the sheet does not claim a number the data does not give.
    if reveal_in:
        out.append(_shade(x0, yt, x1, yb, sides=("top", "left")))

    # THE SASH, AS THE MEMBERS THAT MAKE IT (WP-14.3). `elevation.sash_layout` lays out the jambs,
    # the stiles, the top and bottom rails, each sash's meeting rail and the muntins at the widths
    # sash-light states, and the SVG, the DXF and the scene all draw that one layout. Until then
    # this drew the WHOLE opening divided into equal rectangles by lines of no stated width, and
    # the meeting rail as a line: the glass a reader saw was not the glass the record states, and
    # the 3 in bottom rail that makes a sash read as a sash was not drawn at all. The members are
    # drawn light against the glass, which is what a painted sash is; the glass left between
    # them is each light at the record's own light width.
    layout = rect.get("sash")
    if layout is None:
        # A dormer's window is not a face opening and carries no layout; it takes the same one
        # function at its own rectangle, so a dormer sash cannot drift from a face sash.
        layout = EL.sash_layout(rect["x0_in"], rect["x1_in"], rect["sill_in"], rect["head_in"],
                                lights_across, lights_high, muntin_in)
    if "refused" not in layout:
        for part in layout["members"] + layout["muntins"]:
            px0, px1 = X(part["x0"] / 12.0), X(part["x1"] / 12.0)
            py1, py0 = Ypx(part["y0"] / 12.0), Ypx(part["y1"] / 12.0)
            out.append(_rect_edges("mt" if part["kind"] == "muntin" else "sf", px0, py0, px1, py1))
        # WHERE THE TWO SASHES MEET: a real edge between two members, and the line that tells a
        # reader the window is double-hung rather than a fixed grid.
        my = Ypx(layout["meeting_in"] / 12.0)
        rail = next(p for p in layout["members"] if p["kind"] == "meeting-rail")
        out.append(f'<line class="mj w-hair" x1="{X(rail["x0"] / 12.0):.2f}" y1="{my:.2f}" '
                   f'x2="{X(rail["x1"] / 12.0):.2f}" y2="{my:.2f}"/>')
    # SHUTTERS, where the style carries them. A leaf of None is a style whose kit says it has none
    # -- the solid-brick Chesapeake house is the case, and drawing a pair anyway is drawing a
    # detail four records say was never there. Absent, not zero-width.
    if shutter_w and shutter_h:
        sw, sh = shutter_w / 12.0 * scale, shutter_h / 12.0 * scale
        # THE FRAMING, at this scale. A 2 in stile is 4 px at 1/4 in = 1 ft, so the leaf reads as
        # framing with fielded panels inside it rather than as a plain rectangle with one line.
        # The panels are graduated three-below-two by the sash division (see elevation.py); the
        # stile and rail WIDTHS are not published for any Chesapeake example, so the frame is
        # drawn at the leaf's own proportion and the panels sit inside it -- what is drawn is the
        # panel COUNT, which is sourced, not a stile width, which is not.
        for side, sx0 in ((-1, x0 - sw), (1, x1)):
            out.append(f'<rect class="sh w-med" x="{sx0:.1f}" y="{yt:.1f}" width="{sw:.1f}" height="{sh:.1f}"/>')
            n = max(1, int(panel_count or 2))
            inset = min(sw * 0.16, sh * 0.03)
            for k in range(n):
                py0 = yt + sh * (k / n) + inset
                py1 = yt + sh * ((k + 1) / n) - inset
                if py1 - py0 < 2.0:
                    continue                      # below 2 px a panel is not a panel
                out.append(f'<rect class="pnl w-fine" x="{sx0 + inset:.1f}" y="{py0:.1f}" '
                           f'width="{sw - 2 * inset:.1f}" height="{py1 - py0:.1f}"/>')
    return "".join(out)

def _dormers(elev, roof, profile_ft, X, Ypx, scale, face):
    """The dormers, drawn on the roof plane they sit in.

    HOW A DORMER IS DRAWN IN A TRUE ELEVATION, and it is not what most renderings do. The FACE is
    parallel to the picture plane, so it is drawn TRUE -- its real width, its real sash. The
    CHEEKS are perpendicular to it, so in orthographic projection they have no width at all and
    VANISH: a dormer drawn with visible cheeks has been drawn in perspective by accident. What is
    left of the cheek on the sheet is the strip of dormer FACE outboard of the window casing,
    which is a real face and is drawn. And the dormer's own roof is drawn at the MAIN roof's
    pitch, because three Colonial Williamsburg reports give dormer pitch as equal to the main
    roof's.

    `visible_cheek_width_in` still travels in the measurements, because `fat-cheek-dormer` is a
    PHOTOGRAPH test and a photograph is oblique. The elevation and the photograph disagree about
    the cheek on purpose, and both are right about their own projection.

    WHAT WAS ADDED 27 Aug 2026, and why it matters more than it sounds. The first version drew a
    rectangle, a triangle and a six-light grid: the gable sprang straight off the head casing with
    NO CORNICE, the sash carried half its glazing bars, and the roof had none of the shingle
    courses the main roof beside it had. That is the same abstraction WP-5.11 was written to
    remove, reappearing one storey up. The kit's own rule for this slot -- dormers "carry the same
    order as the house at reduced scale" -- says a dormer has the house's cornice on it, and
    build/elevation.py::dormers() now derives that cornice's height and projection from the ratio
    the house's own cornice obeys. Here it is drawn: a cornice band with its true projection and
    its shade line, carried up the rakes and closed as a pediment where the variant is
    `pedimented`, and stopped with returns where it is `gabled`. A dormer with no cornice is not
    a simplified dormer; it is a different building."""
    d = elev.get("dormers") or {}
    if not d.get("count") or d.get("refused"):
        return ""
    if d.get("placeable") is False:
        return ""                      # said in the legend, not swallowed here
    if face != (d.get("face") or elev.get("entrance_face")):
        return ""                      # a dormer on the far slope is not in this elevation
    eave_ft = min(h for _, h in profile_ft)
    ridge_ft = max(h for _, h in profile_ft)
    sill_ft = eave_ft + (d.get("sill_above_eave_in") or 0.0) / 12.0
    fw = d["face_width_in"] / 12.0 * scale
    ww_in = d["window_width_in"]
    head_ft = sill_ft + d["window_height_in"] / 12.0
    p12 = (roof.get("main") or {}).get("pitch_rise_per_12") or 8.0
    casing_in = d.get("casing_width_in") or 0.0
    cor_h_ft = (d.get("cornice_height_in") or 0.0) / 12.0
    cor_pr = (d.get("cornice_projection_in") or 0.0) / 12.0 * scale
    pedimented = (d.get("variant") or "") == "pedimented"

    # The dormer's face runs from where it comes out of the roof to the bed of its own cornice,
    # a casing's width clear of the sash head. Its cornice sits on top of that.
    face_top_ft = head_ft + casing_in / 12.0
    cor_top_ft = face_top_ft + cor_h_ft

    out = []
    for cx in d.get("positions_ft") or []:
        x0, x1 = X(cx) - fw / 2.0, X(cx) + fw / 2.0
        ys = Ypx(sill_ft - casing_in / 12.0)          # the face carries down past the sill
        yft, yct = Ypx(face_top_ft), Ypx(cor_top_ft)
        apex_ft = cor_top_ft + (d["face_width_in"] / 24.0) * (p12 / 12.0)
        if apex_ft > ridge_ft:
            continue                   # a dormer taller than the roof it sits in is not drawn

        # THE FACE, and the strip of it outboard of the casing is what a photograph calls a
        # cheek. Drawn as PAINTED BOARD and not as the wall's own material: nobody builds a brick
        # dormer on a roof, and `fat-cheek-dormer`'s own correct_practice says historic dormers
        # were "framed light and clad in the same shingle or clapboard as the roof and wall".
        # Drawing the face in the wall's colour on a Flemish-bond house asserts a brick dormer,
        # which is a construction that does not exist.
        out.append(f'<rect class="pf w-prof" x="{x0:.1f}" y="{yft:.1f}" '
                   f'width="{fw:.1f}" height="{(ys-yft):.1f}"/>')

        # THE GABLE ABOVE THE CORNICE, and the two canonical variants differ here and nowhere
        # else. A PEDIMENTED dormer closes its gable with a tympanum -- a wall face -- bounded by
        # a RAKING cornice that is the same assembly as the level one. A GABLED dormer leaves the
        # roof plane running up to the ridge and returns its cornice a short way onto the rake.
        # `raking-cornice-that-does-not-match` is a fault in this corpus precisely because a rake
        # that is not the level cornice is the commonest way to get a pediment wrong, so the rake
        # is drawn at the level cornice's own thickness by construction rather than by eye.
        ax0, ax1 = x0 - cor_pr, x1 + cor_pr
        apex_y = Ypx(apex_ft)
        th = max(yft - yct, 1.0)                       # the cornice band's own thickness, in px
        if pedimented:
            # THE PEDIMENT: an outer gable bounded by a raking cornice, with the tympanum inside
            # it. The rake is the SAME assembly as the level cornice -- `raking-cornice-that-does-
            # not-match` exists because it usually is not -- so the tympanum is the outer gable
            # inset by the level cornice's own thickness measured PERPENDICULAR to the rake. That
            # perpendicular is the whole of the geometry and the reason this is not two stroked
            # lines: a band offset in y alone is thinner than the cornice it continues, by the
            # cosine of the pitch, and thinner the steeper the pediment. Two stroked lines were
            # tried first and gave a notch at the apex and two tails hanging below the eaves.
            _rise = max(yct - apex_y, 1e-6)
            _run = max((ax1 - ax0) / 2.0, 1e-6)
            _len = math.hypot(_run, _rise)
            dx_in = th * _len / _rise          # horizontal inset at the base = th / sin(rake)
            dy_in = th * _len / _run           # apex drop                    = th / cos(rake)
            out.append(f'<polygon class="pf w-prof" points="{ax0:.1f},{yct:.1f} '
                       f'{X(cx):.1f},{apex_y:.1f} {ax1:.1f},{yct:.1f}"/>')
            if (ax1 - ax0) - 2 * dx_in > 2.0 and (yct - apex_y) - dy_in > 2.0:
                out.append(f'<polygon class="pf w-fine" points="{ax0+dx_in:.1f},{yct:.1f} '
                           f'{X(cx):.1f},{apex_y+dy_in:.1f} {ax1-dx_in:.1f},{yct:.1f}"/>')
        else:
            out.append(f'<polygon class="rf w-prof" points="{ax0:.1f},{yct:.1f} '
                       f'{X(cx):.1f},{apex_y:.1f} {ax1:.1f},{yct:.1f}"/>')
            # shingle courses on it, at the same exposure and slope as the roof it stands on --
            # the main roof beside it had them and this did not, which is the kind of difference
            # that makes one part of a sheet look drawn and the other part look diagrammed.
            course_ft = (SHINGLE_EXPOSURE_IN / 12.0) * (p12 / math.sqrt(144.0 + p12 * p12))
            if course_ft * scale >= 2.0:
                y = cor_top_ft + course_ft
                half = (ax1 - ax0) / 2.0
                while y < apex_ft - 1e-6:
                    t = (apex_ft - y) / max(apex_ft - cor_top_ft, 1e-6)
                    out.append(f'<line class="shingle" x1="{X(cx)-half*t:.1f}" y1="{Ypx(y):.1f}" '
                               f'x2="{X(cx)+half*t:.1f}" y2="{Ypx(y):.1f}"/>')
                    y += course_ft

        # THE LEVEL CORNICE, across the face at its own projection, with the shade line that is
        # the only thing on a flat sheet that says it projects at all.
        if cor_h_ft > 0:
            out.append(f'<rect class="pf w-prof" x="{ax0:.1f}" y="{yct:.1f}" '
                       f'width="{ax1-ax0:.1f}" height="{th:.1f}"/>')
            out.append(_shade(ax0, yct, ax1, yct + th, sides=("bottom", "right")))
            # A GABLED DORMER'S CORNICE RETURN IS NOT DRAWN, and the reason is the same one
            # that vanishes the cheeks: a return runs PERPENDICULAR to the picture plane, so in
            # orthographic projection it has no width and what is left on the sheet is the level
            # cornice stopping. It was drawn here for one revision as two stubs standing above
            # the cornice at the eave corners, which is a return seen in perspective -- a real
            # member, drawn in the wrong projection, and the same mistake as a visible cheek.

        # THE SASH, drawn by the same renderer as every other window on the sheet so the two
        # cannot drift apart: same stiles, same meeting rail, same muntin weight. No reveal (a
        # dormer is frame, not solid masonry) and no gauged arch (its head is a wood casing).
        # THE CASING, a frame around the opening at the figure the corpus publishes for this
        # house's window casing -- not a dormer-specific one nobody measured. Drawn BEFORE the
        # sash so the sash sits in it rather than over it.
        if casing_in:
            cwp = casing_in / 12.0 * scale
            out.append(f'<rect class="sill w-fine" x="{X(cx)-ww_in/24.0*scale-cwp:.1f}" '
                       f'y="{Ypx(head_ft)-cwp:.1f}" width="{ww_in/12.0*scale+2*cwp:.1f}" '
                       f'height="{(Ypx(sill_ft)-Ypx(head_ft))+2*cwp:.1f}"/>')
        # A SASH WHOSE PATTERN THE KIT DOES NOT STATE IS DRAWN AS GLASS, with no muntins at all,
        # and the legend says so -- the same treatment the window head already gets when the date
        # cannot separate two masonry heads. `_dormer_lights` returns (None, None) there rather
        # than defaulting to 6/6, which is what it did on the first run: a spec-builder colonial's
        # dormers came back with a confident twelve-light pattern no record had stated.
        la, lh = d.get("lights_across"), d.get("lights_high_per_sash")
        # A DORMER'S WINDOW IS NOT A FACE OPENING, so it does not come from `opening_rects`:
        # it sits on a roof plane at a position `dormers()` computed, and its rectangle is built
        # here from those numbers. Same SHAPE, different rectangle, and stated rather than
        # smuggled through the face's own list.
        out.append(_window(out, {"x0_in": (cx - ww_in / 24.0) * 12.0,
                                 "x1_in": (cx + ww_in / 24.0) * 12.0,
                                 "sill_in": sill_ft * 12.0, "head_in": head_ft * 12.0},
                           la or 1, lh or 1, None, None, X, Ypx, scale,
                           head=None, sill_in=None, panel_count=None, reveal_in=None,
                           muntin_in=((elev.get("storey_windows") or [{}])[0]
                                      .get("muntin_width_in"))))
        # and the face's own shade line: it stands proud of the roof plane it sits in
        out.append(_shade(x0, yft, x1, ys, sides=("bottom", "right")))
    return "".join(out)


def _entrance(elev, rect, X, Ypx, scale, muntin_in=None):
    """WP-12.2: the door's rectangle is `opening_rects`' too — it was the THIRD transcription of
    the same arithmetic, and the one the PRD did not know about."""
    ent = elev["entrance"]
    out = []
    # AND THE LEAF'S OWN WIDTH AND HEIGHT ARE NOT RE-READ HERE. The first pass of the lift left
    # `door_w_in, door_h_in = ent[...]` and a `cx`/`floor_ft` pair standing above these lines,
    # unused: the rectangle already carries every one of those numbers. A dead local that reads
    # the record field the lift was supposed to centralise is how a second spelling grows back,
    # so `tests/test_opening_rects.py` refuses `sill_height_above_floor_in`,
    # `head_height_above_floor_in` and `door_leaf_width_in` anywhere but `elevation.py`.
    dx0, dx1 = X(rect["x0_in"] / 12.0), X(rect["x1_in"] / 12.0)
    dyb, dyt = Ypx(rect["sill_in"] / 12.0), Ypx(rect["head_in"] / 12.0)
    out.append(f'<rect class="dr w-med" x="{dx0:.1f}" y="{dyt:.1f}" width="{dx1-dx0:.1f}" height="{dyb-dyt:.1f}"/>')
    # THE SIX-PANEL RAISED-AND-FIELDED DOOR, drawn as the arrangement it is. The kit names the
    # type; the arrangement is the one every account of the period gives -- TWO SHORT panels at
    # the top, TWO LONG in the middle, TWO SHORT at the bottom, with the bottom pair equal to or
    # a little taller than the top pair. Two horizontal lines across the leaf, which is what was
    # drawn here before, is a THREE-panel door: it says nothing about the vertical joint that
    # makes it six, and it makes the commonest door of the tradition read as the wrong one.
    #
    # The stile and rail WIDTHS are not published for any measured Virginia example, so the
    # panels are laid out on the leaf's own proportion and inset by a stile that is drawn, not
    # asserted: what this states is the ARRANGEMENT, which is documented, and not a dimension,
    # which is not.
    dw, dh = dx1 - dx0, dyb - dyt
    # A GARAGE DOOR IS NOT A SIX-PANEL LEAF (WP-14.3, census V6). The arrangement below is the
    # panelled entrance door the kit names, and it was drawn on every door this function was
    # handed -- a 192 in garage door came out as six raised panels. The plan says what kind of
    # door it placed (`type`), no record states a garage door's face, and so it is drawn as the
    # opening it is and the sheet says so.
    if "garage" in str(rect.get("type") or "").lower():
        return "".join(out)
    stile = min(dw * 0.115, dh * 0.035)                  # about one seventh of the leaf, halved
    bands = (0.20, 0.46, 0.20)                           # short / long / short, top to bottom
    gap = stile * 0.62
    yy = dyt + stile
    avail = dh - 2 * stile - 2 * gap
    for frac in bands:
        bh = avail * (frac / sum(bands))
        if bh > 2.0 and dw / 2 - stile * 1.5 > 2.0:
            for hx0 in (dx0 + stile, dx0 + dw / 2 + gap / 2):
                pw_ = dw / 2 - stile - gap / 2
                out.append(f'<rect class="pnl w-fine" x="{hx0:.1f}" y="{yy:.1f}" '
                           f'width="{pw_:.1f}" height="{bh:.1f}"/>')
        yy += bh + gap
    # THE DOORCASE DRESSES THE ENTRANCE AND NOTHING ELSE (WP-13.3). A door rect is any placed
    # exterior door on this face now -- the Tidewater plan seats three on its N wall -- and
    # only the one carrying `entrance` is the composition's subject. A back door is a leaf.
    if not rect.get("entrance"):
        return "".join(out)
    casing_w = ent["casing_width_in"] / 12.0 * scale
    cs_x0, cs_x1 = dx0 - casing_w, dx1 + casing_w
    ent_h = (ent.get("entablature_height_in") or ent["surround_height_above_opening_in"]) / 12.0 * scale
    # THE TRANSOM, where the style's kit makes a rectangular one canonical (WP-14.3). The record
    # has dimensioned it since WP-5.x and fed it to two faults, and no surface drew it
    # (`oq/the-record-dimensions-a-transom-and-no-drawing-draws-one`). Its height is a JUDGMENT
    # and the legend says so; its lights are sash-light's own count, dividing the glass evenly
    # because no record states a transom's own frame. The doorcase stands above it: the casing
    # runs up past the transom and the entablature sits on top, which is what a doorcase with a
    # transom is.
    tr = ent.get("transom") or {}
    door_top = dyt                  # the leaf's own head: the sidelights stand to it, not above
    if tr.get("drawn"):
        th = tr["height_in"] / 12.0 * scale
        out.append(f'<rect class="op" x="{dx0:.1f}" y="{dyt - th:.1f}" width="{dx1 - dx0:.1f}" '
                   f'height="{th:.1f}"/>')
        mw = (muntin_in or 0.0) / 12.0 * scale
        # EVENLY, as the legend says: `elevation.even_bars` is the one spelling (WP-14.6; the
        # bar centred on each division of the whole width left the end lights half a bar wider)
        for bx0, bx1 in EL.even_bars(dx0, dx1, tr["lights"], mw)[1]:
            out.append(_rect_edges("mt", bx0, dyt - th, bx1, dyt))
        dyt = dyt - th
    out.append(f'<rect class="cs" x="{cs_x0:.1f}" y="{dyt-ent_h:.1f}" width="{cs_x1-cs_x0:.1f}" height="{(dyb-dyt)+ent_h:.1f}"/>')
    # A SIDELIGHT PAIR THE PLAN LEAVES NO ROOM FOR IS NOT DRAWN (WP-14.6): `opening_rects`
    # refuses it where it would stand over a neighbouring opening, and the notes say why.
    if ent["sidelights_present"] and rect.get("sidelights_drawn", True):
        slw = ent["sidelight_width_in"] / 12.0 * scale
        for side, sx0 in ((-1, cs_x0 - slw), (1, cs_x1)):
            out.append(f'<rect class="op" x="{sx0:.1f}" y="{door_top:.1f}" width="{slw:.1f}" '
                       f'height="{dyb-door_top:.1f}"/>')
    return "".join(out)

# ---------------------------------------------------------------- main
# Wood shingle laid to the weather. Colonial Williamsburg's own figure for its reconstructions
# ("They are laid 5-1/2 to 6 in to the weather"); the 1700s Virginia statute fixes shingle LENGTH
# and says nothing about exposure, so this is conventional practice and not a period measurement.
SHINGLE_EXPOSURE_IN = 5.75


def _shade(x0, y0, x1, y1, sides=("bottom",)):
    """SHADE LINES: relief drawn in line, not in tone.

    The conventional light of architectural drawing comes over the viewer's left shoulder at 45
    degrees, so on a front elevation every projecting member is lit on its top and left and dark
    on its underside and right. The depth of the cast shadow on the wall equals the member's own
    projection exactly -- that is the whole of the geometry, and it is why a water table that
    projects 2 in and a cornice that projects 10 in do not read alike.

    Rendered as WEIGHT rather than as tone, deliberately. HABS's guidelines prohibit shading in
    elevation outright and then bless this instead: accenting the shadowed edge of a member is
    the line-only way to get relief, and it is what its own delineators did. It also suits this
    corpus: it introduces no colour (so `svg_theme.HEX_MAP` stays total), it uses the ladder that
    is already there, and it does not put a wash over a drawing whose whole claim is that every
    line is a measurement.

    Without it a projection is invisible. A band drawn at its true width against a flat wall is
    still a flat wall on the sheet -- which is most of why the elevation read as a diagram."""
    out = []
    if "bottom" in sides:
        out.append(f'<line class="shade w-prof" x1="{x0:.1f}" y1="{y1:.1f}" x2="{x1:.1f}" y2="{y1:.1f}"/>')
    if "right" in sides:
        out.append(f'<line class="shade w-prof" x1="{x1:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}"/>')
    if "left" in sides:
        out.append(f'<line class="shade w-prof" x1="{x0:.1f}" y1="{y0:.1f}" x2="{x0:.1f}" y2="{y1:.1f}"/>')
    if "top" in sides:
        out.append(f'<line class="shade w-prof" x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y0:.1f}"/>')
    return "".join(out)


def _profile_span_at(profile_ft, y):
    """Where a horizontal line at height y enters and leaves a closed roof silhouette.

    A shingle course runs the full width of the plane on a side-gable front and narrows toward
    the ridge on a hip, because the hips cut it. Reading the span off the polygon gets both from
    one rule instead of special-casing the forms."""
    xs = []
    n = len(profile_ft)
    for i in range(n):
        (x1, y1), (x2, y2) = profile_ft[i], profile_ft[(i + 1) % n]
        if y1 == y2:
            continue
        if min(y1, y2) - 1e-9 <= y <= max(y1, y2) + 1e-9:
            xs.append(x1 + (x2 - x1) * (y - y1) / (y2 - y1))
    if len(xs) < 2:
        return None
    return (min(xs), max(xs))


def _profile_top_at(profile_ft, x):
    """The highest point of the roof silhouette at horizontal position x, or None off the end.

    The inverse of _profile_span_at, and it is what decides how much of a chimney a roof hides.
    On the long face of a side-gable house the silhouette is a RECTANGLE from eave to ridge (a
    parallel projection of one sloping plane fills the band), so the answer is the ridge at every
    x; on a gable end it is the triangle's own height at x. One rule, both forms, no special
    casing -- and it only became askable at all on 27 Aug 2026, when elevation_profile stopped
    returning a flat eave line for a long face."""
    ys = []
    n = len(profile_ft)
    for i in range(n):
        (x1, y1), (x2, y2) = profile_ft[i], profile_ft[(i + 1) % n]
        if x1 == x2:
            continue
        if min(x1, x2) - 1e-9 <= x <= max(x1, x2) + 1e-9:
            ys.append(y1 + (y2 - y1) * (x - x1) / (x2 - x1))
    return max(ys) if ys else None


def _near_end_last(c, face, fp):
    """Draw order on a gable face: the far end's stack first, so a near one in front of it is
    drawn over it. Plan x runs from the W wall to the E, so the E face's near end is x = W."""
    if face not in ("E", "W"):
        return 0
    at_e = abs((c.get("x_ft") or 0.0) - fp["width_ft"]) < 0.5
    return 1 if (at_e == (face == "E")) else 0


def _stack_outline(face, c, roof, fp):
    """The part of one gable-end stack a face draws: `{"outline": [(u_ft, h_ft), ...]}` in the
    face's own frame and the record's own grade heights -- top left, top right, then the foot
    from right to left -- or `{"refused": why}`.

    ONLY THE PART ABOVE THE ROOF LINE IS DRAWN, and that is a claim about EVIDENCE rather than
    about visibility (WP-5.11). The only width this corpus states is the STACK's -- brick-course's
    22 in, itself a judgment -- and a chimney BREAST at the foot of an exterior end stack is
    several feet across with no figure anywhere; drawing the stack's width down to grade would
    assert a chimney nobody measured. So each face draws the stack's own square (`plan_rect_ft`,
    the placement's, WP-14.6) above the roof line it meets, and the legend says what is not drawn
    below it.

    THE ROOF LINE IS THE GABLE'S RAKE AT THE STACK'S OWN DEPTH, ON EVERY FACE. A gable-end stack
    meets the roof along the rake of the end it stands at, and on a side gable the roof's height
    at plan depth `t` is the end profile's height there whatever `x` is -- so the rake over the
    stack's own depth, `[y0, y1]`, is the roof line it stands above:

      the gable face   projects along the ridge, so the foot FOLLOWS the rake across the stack's
                       width -- a level cut at the centre (the first version) floats the stack
                       clear of the rake on its low side and sinks it into the gable on the high.
                       A stack at the near end stands in front of its gable and one at the far
                       end behind the whole house; on a side gable both are bounded below by the
                       same rake, so the two draw alike.
      the long face    projects across the ridge. An EXTERIOR stack stands wholly outboard of the
                       gable wall and nothing of the roof is in front of it, so its foot is the
                       lowest point of its rake -- the side of the square farther down the slope.
                       An INTERIOR one comes up through the roof, and the plane between the eave
                       and the stack hides it up to that plane's highest point in front of it: the
                       ridge if the stack is beyond the ridge, else the rake at its near face.

    A roof whose ridge runs front to back puts its gable ends on the front and the back, and this
    function draws a stack against a SIDE gable's rake only: that case is refused by name rather
    than drawn from a rule written for the other. It was silent before -- the old test for a
    gable-end stack read `x` alone, found none, and drew nothing without a word."""
    ridge = (roof.get("main") or {}).get("ridge") or {}
    if ridge.get("axis") != "x":
        return {"refused": "not-side-gable"}
    rect = c.get("plan_rect_ft")
    if not rect:
        return {"refused": "unplaced"}
    x0, y0, x1, y1 = rect
    W, D = fp["width_ft"], fp["depth_ft"]
    end = (roof.get("elevation_profiles") or {}).get("E") or []
    if not end:
        return {"refused": "no-profile"}
    top = c["total_height_grade_ft"]

    def rake(t):
        return _profile_top_at(end, min(max(t, 0.0), D))

    def inner(lo, hi):                       # the end profile's own vertices strictly inside
        return sorted({px for px, _h in end if lo < px < hi})

    if face in ("E", "W"):
        us = [y0] + inner(y0, y1) + [y1]
        foot = [(u, min(rake(u), top)) for u in us]
        if all(h >= top - 1e-6 for _u, h in foot):
            return {"refused": "hidden"}
        return {"outline": [(y0, top), (y1, top)] + list(reversed(foot))}
    # a long face
    own = min(rake(y0), rake(y1))            # the rake is highest at the ridge: its least is an end
    if c.get("side") == "exterior" or x1 <= 0.0 + 1e-6 or x0 >= W - 1e-6:
        foot_h = own
    else:
        front = (0.0, y0) if face == "S" else (y1, D)
        ts = [front[0], front[1]] + inner(front[0], front[1])
        hider = max(rake(t) for t in ts) if front[1] > front[0] else own
        foot_h = max(own, hider)
    foot_h = min(foot_h, top)
    if foot_h >= top - 1e-6:
        return {"refused": "hidden"}
    return {"outline": [(x0, top), (x1, top), (x1, foot_h), (x0, foot_h)]}


def render_elevation(elev, path, face=None, scale=24.0):
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

    # WP-12.2: the GROUND floor datum is no longer read here — `opening_rects` derives every
    # opening's sill and head from the section's own storeys, so a second reading of the same
    # number in this file could only ever disagree with it. `floor2_ft` survives because the
    # belt course stands on it, which is not an opening.
    floor2_ft = upper["grade_to_floor_ft"]
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
    if roof.get("chimneys", {}).get("applicable"):
        # Reserve enough canvas for a stack rising above the ridge -- from the SAME chimney
        # records drawn below, not a separate guess. This used to be gable faces only, in step
        # with a chimney block that drew nothing on the front; both changed together on 27 Aug
        # 2026, and they have to, because reserving sky for a stack the sheet declines to draw is
        # its own small lie and drawing one into sky nobody reserved runs it off the top edge --
        # which is exactly what happened on the first run, at y = -158.
        for c in roof["chimneys"]["positions"]:
            if abs(c["x_ft"]) < 0.5 or abs(c["x_ft"] - fp["width_ft"]) < 0.5:
                top_height_ft = max(top_height_ft, c["total_height_grade_ft"] + ridge_delta_ft)

    pad, top, legend_h = 46, 34, 90
    inset_w = 250
    pw = span_ft * scale
    ph = top_height_ft * scale
    total_w = pad * 2 + pw + inset_w + 20
    total_h = top + ph + legend_h

    # WP-12.4: what this plate's pixels mean in feet, so the Round can lay it over the model.
    # `u` is the distance ALONG the face from its own left edge and `v` is the height above
    # grade -- the two axes this renderer's X and Ypx already use, stated rather than left for
    # a reader to infer. The origin is hoisted here so the attribute and the ink read one pair.
    ox, oy = pad, top
    _frames = {"plates": [{"id": face, "proj": "elevation", "face": face,
                           "px_per_ft": scale, "origin_px": [ox, oy],
                           "at_origin_ft": [0.0, round(top_height_ft, 3)]}]}
    # A FUNCTION, because the eave inset appends a second plate once its own scale is known,
    # far below, and the root element is rewritten then (WP-14.1).
    _head = lambda: (f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w:.0f}" height="{total_h:.0f}" '
                     f'viewBox="0 0 {total_w:.0f} {total_h:.0f}" data-frame=\'{SS.frame_attr(_frames)}\' '
                     f'style="background:{PAL["ground"]}">')
    s = [_head()]
    s.append(_style_block())
    # _esc on `face` too: it arrives as body.get("face") on /api/drawings and /api/export, and
    # this string is rendered into the page by DrawingSet.jsx with dangerouslySetInnerHTML.
    # Nothing was exploitable — elevation.py looks `face` up in FACES ("S","N","E","W") 38 lines
    # earlier and a miss raises KeyError into a 422 — but that guard is incidental to this line,
    # and an unescaped interpolation of request data protected only by a lookup somewhere else
    # is one refactor from being live.
    s.append(f'<text class="hd" x="{pad}" y="20">{_esc(elev.get("plan_id",""))} — {_esc(face)} ELEVATION</text>')

    X = lambda ft: ox + ft * scale
    Ypx = lambda ft: oy + (top_height_ft - ft) * scale   # model y-up (height above grade), screen y-down

    s.append(f'<rect x="{X(0):.1f}" y="{Ypx(top_height_ft):.1f}" width="{pw:.1f}" height="{ph:.1f}" fill="{PAL["paper"]}"/>')
    s.append(f'<rect class="wf" x="{X(0):.1f}" y="{Ypx(top_of_wall_ft):.1f}" width="{pw:.1f}" height="{(top_of_wall_ft*scale):.1f}"/>')
    # THE GROUND LINE. HABS makes this the single heaviest line on an elevation -- 0.6 mm against
    # 0.1 mm for a joint -- and runs it PAST the building at both ends, because it is the ground
    # and not the underside of the wall. Its weight came from an inline attribute until 27 Aug
    # 2026, so it sat off the ladder entirely and could not be reasoned about with the rest.
    s.append(f'<line class="gl w-ground" x1="{X(0)-scale*1.5:.1f}" y1="{Ypx(0):.1f}" '
             f'x2="{X(span_ft)+scale*1.5:.1f}" y2="{Ypx(0):.1f}"/>')

    # PROJECTIONS ARE DRAWN AT THE SIZE THE RECORD STATES. Until WP-5.11 the water table overhung
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
        # Its underside is in shadow: the light is over the left shoulder at 45 degrees and this
        # course projects 2 1/16 in past the wall. Without the shade line a water table drawn at
        # its true projection is a stripe, not a plinth.
        s.append(_shade(X(0)-wt_o, Ypx(wt_top_ft), X(span_ft)+wt_o, Ypx(0)))
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
            s.append(_shade(X(0)-bo, Ypx(belt_ft+belt_h_ft), X(span_ft)+bo, Ypx(belt_ft)))

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
    # The cornice throws the deepest shadow on the building -- its projection is the greatest of
    # any member, and on a Georgian front that band of dark under the eaves is the first thing the
    # eye reads. Drawn as the heaviest shade line on the sheet after the ground.
    s.append(_shade(X(0)-co, Ypx(true_eave_ft), X(span_ft)+co, Ypx(top_of_wall_ft)))
    # THE TEETH. A modillion band drawn as a solid band is a band of no modillions, and until
    # 27 Aug 2026 that is what every cornice in this corpus was: the layout function existed, the
    # widths were authored from the authorities' own notes, and nothing called it. Gibbs's rule
    # is that a modillion centres over each column; this facade has no columns, so the bay centres
    # are the anchors -- which is what the rule means on a wall.
    band = None
    for mm in cornice.get("members", []):
        if (mm.get("profile") or "") in ("modillion", "dentil", "mutule", "triglyph"):
            band = mm
            break
    if band:
        rp = PROF.repeat_positions(
            span_ft * 12.0,
            spacing_in=band.get("spacing_in"),
            width_in=band.get("width_in"),
            # THE BAY CENTRES ARE FACE FEET FROM THE FACE'S OWN LEFT EDGE, and so are the teeth
            # `repeat_positions` returns (drawn at `X(t["x0"] / 12)`). The anchors used to subtract
            # `X(0) / scale` -- the plate's PIXEL origin divided by the scale, 46 / 24 = 1.92 ft --
            # which put every modillion 23 in off its bay (WP-14.3). Latent for as long as every
            # band was drawn solid; driven in tests/test_elevation_small_fixes.py.
            centre_on=[c * 12.0 for c in front["centres_ft"]] or None)
        by0 = true_eave_ft - (cornice["cornice_height_in"] - band["y_bottom_in"]) / 12.0
        bh = (band["y_top_in"] - band["y_bottom_in"]) / 12.0 * scale
        bp = proj_px(band.get("projection_in"))
        if rp["solid"]:
            # Drawn solid AND SAID SO -- the behaviour three documents describe and no surface
            # performed. The reason travels to the legend rather than being swallowed here.
            cornice_band_note = f'{band["profile"].upper()} BAND DRAWN SOLID — {rp["reason"].upper()}'
        else:
            cornice_band_note = None
            for t in rp["teeth"]:
                s.append(f'<rect class="bd w-fine" x="{X(t["x0"]/12.0):.1f}" '
                         f'y="{Ypx(by0 + (band["y_top_in"]-band["y_bottom_in"])/12.0):.1f}" '
                         f'width="{(t["x1"]-t["x0"])/12.0*scale:.1f}" height="{bh:.1f}"/>')
    else:
        cornice_band_note = None

    # the frieze band's own bed, which is where the cornice assembly actually starts
    fz = cornice.get("frieze_height_in")
    if fz:
        s.append(f'<line class="wtm" x1="{X(0):.1f}" y1="{Ypx(true_eave_ft - (cornice["cornice_height_in"]/12.0)):.1f}" '
                 f'x2="{X(span_ft):.1f}" y2="{Ypx(true_eave_ft - (cornice["cornice_height_in"]/12.0)):.1f}"/>')

    # WP-12.2: ONE LOOP, in `elevation.opening_rects`. The blind-bay skip (OQ 85), the
    # door-at-the-entrance-face branch and the two storeys all live there now, so this file and
    # `export_dxf.py` cannot come to disagree about which bays carry an opening — which they did,
    # for as long as it took someone to notice the CAD file drawing a window through a chimney.
    for r in EL.opening_rects(elev, face)["rects"]:
        if r["kind"] == "door":
            s.append(_entrance(elev, r, X, Ypx, scale,
                               muntin_in=((elev.get("storey_windows") or [{}])[0]
                                          .get("muntin_width_in"))))
            continue
        rec = r["record"]
        # THE LIGHTS AND THE LEAVES ARE THE OPENING'S OWN (WP-14.3), computed by `sash_at` at the
        # width this rectangle is drawn -- not the storey record's, which were taken at the width
        # the storey was sized at and divided a 42 in opening into a 38.6 in window's lights.
        s.append(_window(s, r, r["lights_across"], r["lights_high_per_sash"],
                         r["shutter_leaf_width_in"], r["shutter_leaf_height_in"], X, Ypx, scale,
                         head=rec.get("head_treatment"), sill_in=wtb.get("course_height_in"),
                         panel_count=r["shutter_panel_count"],
                         reveal_in=rec.get("reveal_band_in"),
                         muntin_in=rec.get("muntin_width_in")))

    # THE ROOF, drawn as the closed plane it is rather than as a line along its bottom edge.
    #
    # roof.py's own elevation_profile() numbers, shifted by the cornice band this file adds (see
    # ridge_delta_ft above). Until 27 Aug 2026 the long-face profile was two points both at the
    # eave, so this polyline drew a horizontal line and the entire roof was absent from the front
    # sheet -- 14.22 ft of building, on a house whose kit calls its roof canonical.
    #
    # The three silhouettes are each other's opposites and all three come from roof.py:
    #   side-gable, long face   a plain rectangle, eave to ridge; its BLANKNESS is correct
    #   hip, long face          an isosceles trapezoid, the hips at the roof's own nominal pitch
    #   gable end               a triangle
    roof_poly = " ".join(f"{X(x):.1f},{Ypx(h):.1f}" for x, h in profile_ft)
    s.append(f'<polygon class="rf w-prof" points="{roof_poly}"/>')

    # THE COVERING. Wood shingle, laid to a 5 1/2-6 in exposure (Colonial Williamsburg's own
    # figure for its shops; the 18th-c Virginia statute fixes shingle LENGTH and not exposure, so
    # the exposure is conventional and is said so). The courses foreshorten: a plane at pitch
    # theta seen square-on compresses each course to `exposure x sin(theta)`, so they crowd toward
    # the ridge of a steep roof and open out on a shallow one. Drawn only where a course clears
    # the minimum legible spacing for this sheet -- 51 courses at 0.6 px apart is a grey wash, not
    # a drawing, and HABS's own rule is a vignette of the covering rather than a generated hatch.
    slope_deg = roof.get("main", {}).get("roof_slope_angle_deg") or elev.get("measurements", {}).get("roof_slope_angle_deg")
    eave_top_ft = min(h for _, h in profile_ft)
    ridge_top_ft = max(h for _, h in profile_ft)
    if slope_deg and ridge_top_ft - eave_top_ft > 0.1:
        import math as _m
        course_ft = (SHINGLE_EXPOSURE_IN / 12.0) * _m.sin(_m.radians(slope_deg))
        if course_ft * scale >= 2.0:            # below 2 px a course is not a line, it is a tone
            y = eave_top_ft + course_ft
            while y < ridge_top_ft - 1e-6:
                xs = _profile_span_at(profile_ft, y)
                if xs:
                    s.append(f'<line class="shingle" x1="{X(xs[0]):.1f}" y1="{Ypx(y):.1f}" '
                             f'x2="{X(xs[1]):.1f}" y2="{Ypx(y):.1f}"/>')
                y += course_ft

    s.append(_dormers(elev, roof, profile_ft, X, Ypx, scale, face))

    # THE CHIMNEYS. This block asserted, in twelve lines, that the front elevation could not show
    # them: "build/roof.py's long-face silhouette is FLAT AT THE EAVE ... models no roof mass
    # above the cornice at all", and it drew them on the gable ends only. That was true when it
    # was written and stopped being true earlier in this same package -- elevation_profile now
    # returns the near roof PLANE on a long face, because parallel projection fills the band from
    # eave to ridge. Prose asserting what the code no longer does is the failure this corpus
    # polices hardest, and it was sitting in the renderer's own comment.
    #
    # It also drew the stack at a hardcoded 3 ft from the gable wall's front corner, with its base
    # a hardcoded 2 ft below the ridge -- two invented constants of exactly the class OQ 52 swept
    # out of the measurements, still being asserted by the drawing where no test could see them.
    # The record states y_ft (21.33 here, which is mid-depth: a stack on the ridge line) and
    # total_height_grade_ft. On the sheet the 3 ft put a brick bar in the sky at the top-left
    # corner, touching no roof at all.
    #
    # WHERE A STACK STANDS DECIDES WHAT HIDES IT, and the record says which: this style's own kit
    # gives `gable-end-exterior, paired-and-joined-by-arched-curtain`. An EXTERIOR stack is
    # outside the envelope, so nothing hides it and it is drawn from grade -- which is the whole
    # of the reading the kit calls "visible from a mile away and conclusive against New England".
    # A stack that is NOT exterior comes up through the roof, and the near plane hides it to the
    # roof's own height at its plan position, which _profile_top_at answers for either form.
    chimneys_drawn = 0
    _drawn_stack_keys = set()
    _stack_right_px = ox + pw          # the rightmost ink a stack puts past the face (WP-14.6)
    stack_sides = set()
    stacks_unplaced = 0
    stacks_hidden = 0
    stacks_not_side_gable = False
    ch = roof.get("chimneys") or {}
    stacks_unsized = bool(ch.get("applicable") and ch.get("positions")
                          and not elev.get("chimney_stack_plan_in"))
    # NO STACK AT A SIZE NOBODY GAVE (WP-14.3). With no stated plan size this fell back to 22 in
    # and drew it; the stack is refused now and the legend says why.
    if ch.get("applicable") and ch.get("positions") and not stacks_unsized:
        # ONE STACK, ONE SQUARE, EVERY FACE (WP-14.6, audit F3 and F13). This block drew the
        # stack on the long face from the RIDGE up and on the gable face from the rake at its
        # centre, cut level -- two chimneys for one: on the Tidewater plan 8.0 ft of stack on the
        # front and 16.2 ft on the gable end, and on the gable end the level cut floated the stack
        # clear of the rake on its low side. It also chose the stack's side of the wall by
        # reading the word "exterior" in the CHIMNEY slot, which is the slot this corpus reads for
        # the stack's HEIGHT; which face of the wall a stack stands on is the PLAN's fact, written
        # by `threshold._stack_rect` from `hearth_position`, and the roof record now carries that
        # square (`plan_rect_ft`, with its `side`). Every face draws the part of that square that
        # stands above the roof line it meets -- `_stack_outline` -- so the front and the gable
        # end are two views of one prism.
        for c in sorted(ch["positions"], key=lambda c: _near_end_last(c, face, fp)):
            got = _stack_outline(face, c, roof, fp)
            if got.get("refused") == "unplaced":
                stacks_unplaced += 1
                continue
            if got.get("refused") == "not-side-gable":
                stacks_not_side_gable = True
                continue
            if got.get("refused") == "hidden":
                stacks_hidden += 1
                continue
            if got.get("refused"):
                continue
            pts = got["outline"]
            key = tuple((round(u, 3), round(h, 3)) for u, h in pts)
            if key in _drawn_stack_keys:
                continue                   # the far stack stands exactly behind the near one
            _drawn_stack_keys.add(key)
            poly = " ".join(f"{X(u):.1f},{Ypx(h + ridge_delta_ft):.1f}" for u, h in pts)
            s.append(f'<polygon class="ch w-prof" points="{poly}"/>')
            _stack_right_px = max(_stack_right_px, max(X(u) for u, _h in pts))
            (u0, top_h), (u1, _t) = pts[0], pts[1]
            s.append(_shade(X(u0), Ypx(top_h + ridge_delta_ft), X(u1),
                            Ypx(pts[2][1] + ridge_delta_ft), sides=("right",)))
            stack_sides.add(c.get("side"))
            chimneys_drawn += 1

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
    if cornice_band_note:
        notes.append(cornice_band_note)
    # THE ROOF STANDS ON THIS SHEET'S OWN FRIEZE AND CORNICE, AND NO OTHER SURFACE HAS ONE
    # (WP-14.6). `elevation.grade_to_true_eave_in` adds the frieze and the cornice ABOVE roof.py's
    # eave, and this sheet lifts the whole roof silhouette -- and every stack on it -- by that
    # band, while the section prints roof.py's eave and ridge and the model builds its roof planes
    # there. The record has said so since WP-3.2 ("not fed back into those files' own records");
    # the sheet said nothing, so one drawing set showed two heights for one ridge, 2.5 to 3.4 ft
    # apart on every plan that draws an elevation, with no word between them. Census V19 measures
    # it; which height is right is a ruling, and `facade-classical`'s own frieze rule -- the band
    # "between the top-storey window heads and the bed of the cornice" -- is evidence for the
    # other one: `oq/the-elevation-stands-its-roof-on-a-cornice-band-no-other-surface-draws`.
    if cornice_band_ft > 0.005:
        _f = _mod("render_section", f"{ROOT}/build/render_section.py")._fmt
        _ridge = ((roof.get("main") or {}).get("ridge") or {}).get("grade_to_ridge_ft")
        notes.append(f'ROOF DRAWN ON THIS SHEET’S FRIEZE AND CORNICE, {cornice_band_ft * 12.0:.1f}″ '
                     f'ABOVE THE EAVE THE ROOF RECORD, THE SECTION AND THE MODEL STATE ('
                     f'{_f(top_of_wall_ft)}' + (f', RIDGE {_f(_ridge)}' if _ridge else '') +
                     '), WHICH DRAW NO SUCH BAND: EAVE ' + _f(true_eave_ft) +
                     (f', RIDGE {_f(_ridge + cornice_band_ft)}' if _ridge else '') +
                     ' HERE — NOT RECONCILED')
    if elev.get("chimney_stack_plan_judgment") and elev.get("chimney_stack_plan_in"):
        notes.append(f'STACK DRAWN {elev["chimney_stack_plan_in"]}″ SQUARE — A JUDGMENT, NOT A '
                     f'MEASUREMENT: THE COURSING PUTS IT BETWEEN SIZES AND A MASON WILL BUILD 18″ OR 27″')
    if front.get("blind_bay_centres_ft"):
        notes.append('BAY BLIND WHERE A STACK STANDS ON IT — ' +
                     _esc((front.get("blind_bay_reason") or "").upper()))
    # WP-13.3: the openings drawn are the plan's placed openings on this face, and every placed
    # or declared opening the elevation could not draw is named on the plate rather than left
    # as a blank wall a reader would take for a windowless one. The count is read from the same
    # `refused` list every caller of `opening_rects` reports.
    _refused = EL.opening_rects(elev, face)["refused"]
    # THE WINDOW DRAWN IS NOT ALWAYS THE WINDOW THE STOREY WAS SIZED AT (WP-14.3). The line above
    # states each storey's window at the width `_storey_window` sizes from its head and sill; the
    # rectangles are the plan's placed widths. Where they differ the sheet says so, and says that
    # each window's lights and leaves are the rule's at the width drawn.
    _off = sorted({round(r["width_in"], 1) for r in EL.opening_rects(elev, face)["rects"]
                   if r["kind"] == "window" and r.get("storey_pack_width_in") is not None
                   and abs(r["width_in"] - r["storey_pack_width_in"]) > 0.05})
    if _off:
        notes.append('WINDOWS DRAWN AT THE PLAN\u2019S PLACED WIDTHS (' +
                     ", ".join(f"{v:g}" for v in _off[:5]) + (" …" if len(_off) > 5 else "") +
                     ' IN), NOT THE STOREY\u2019S; EACH ONE\u2019S LIGHTS AND SHUTTER LEAVES ARE '
                     'SASH-LIGHT\u2019S RULE AT THE WIDTH IT IS DRAWN')
    _named = [x for x in _refused if x.get("room")]
    if _named:
        _units = sum(int(x.get("units") or 1) for x in _named)
        _rooms = sorted({str(x.get("room")).upper() for x in _named})
        notes.append(f'{_units} OPENING(S) ON THIS FACE NOT DRAWN — ' +
                     _esc(", ".join(_rooms[:6]) + (" …" if len(_rooms) > 6 else "")) +
                     ' — THE PLACER OR A STACK REFUSED THEM; THE ELEVATION RECORD NAMES EACH')
    # THE KEYSTONE AND THE STACK THAT ARE NOT DRAWN (WP-14.3), where each once fell back to a
    # figure no record states.
    if ht.get("keystone") and not ht.get("keystone_width_in"):
        notes.append("KEYSTONE NOT DRAWN \u2014 THE KIT MAKES ONE CANONICAL AND NO RECORD STATES "
                     "ITS WIDTH")
    if stacks_unsized:
        notes.append("STACKS NOT DRAWN \u2014 THE ROOF PLACES THEM AND NO RECORD STATES THEIR "
                     "PLAN SIZE")
    # THE COURSES THE OPENINGS MISS, MEASURED AND SAID (WP-14.3, census V11). brick-course's own
    # note: "in a brick building there are no free horizontal dimensions above the water table.
    # Storey height, sill height, head height, belt course and plate are all whole numbers of
    # courses off a single datum". This sheet draws the courses and draws each window at its
    # storey's own head and sill, which nothing snaps to a course; the misses are the drawing
    # telling the truth about two records that do not meet. Whether the openings should move to
    # the brickwork, or the brickwork is not modelled that closely, is
    # `oq/the-openings-are-not-set-to-the-brick-courses`.
    if wtb.get("course_height_in") and wtb.get("applicable"):
        c_in = wtb["course_height_in"]
        base_in = wtb["water_table_height_above_finished_grade_in"]
        edges = [v for r in EL.opening_rects(elev, face)["rects"] if r["kind"] == "window"
                 for v in (r["sill_in"], r["head_in"])
                 if base_in + c_in <= v <= top_of_wall_ft * 12.0]
        off = [abs(v - (base_in + max(1, round((v - base_in) / c_in)) * c_in)) for v in edges]
        missed = [m for m in off if m > 0.05]
        if missed:
            notes.append(f"{len(missed)} OF {len(edges)} SILLS AND HEADS MISS THE {c_in:g}\u2033 "
                         f"COURSES BY UP TO {max(missed):.2f}\u2033 \u2014 BRICK-COURSE SETS SILL "
                         "AND HEAD HEIGHT IN WHOLE COURSES; THE OPENINGS KEEP THEIR STOREY\u2019S "
                         "OWN HEAD AND SILL, AND SNAPPING THEM IS AN OPEN QUESTION")
    # THE ENTRANCE (WP-14.3): the transom drawn at a judged height, or the reason a canonical one
    # is not; a garage door drawn as its opening; and the panels said to be an arrangement.
    _doors = [r for r in EL.opening_rects(elev, face)["rects"] if r["kind"] == "door"]
    _tr = (elev.get("entrance") or {}).get("transom") or {}
    if any(r.get("entrance") for r in _doors):
        if _tr.get("drawn"):
            notes.append(f'TRANSOM DRAWN {_tr["height_in"]:.1f}\u2033 HIGH \u2014 A JUDGMENT: '
                         'OPENING-PROPORTION MARKS ITS HEIGHT ONE (\u201cTHE MEASURED SPREAD IS '
                         f'ENORMOUS\u201d); ITS {_tr["lights"]} LIGHTS ARE SASH-LIGHT\u2019S COUNT, '
                         'DIVIDING IT EVENLY, AS NO RECORD STATES A TRANSOM\u2019S OWN FRAME')
        elif _tr.get("why"):
            notes.append('TRANSOM NOT DRAWN \u2014 ' + _esc(_tr["why"].upper()))
    # WHAT A NEIGHBOUR LEFT NO ROOM FOR (WP-14.6): a sidelight pair or a shutter pair the plan's
    # placed openings would put over another opening, refused in `opening_rects` and said here.
    for r in _doors:
        if r.get("sidelights_refused"):
            notes.append('SIDELIGHTS NOT DRAWN \u2014 ' + _esc(r["sidelights_refused"].upper()))
    _no_leaves = [r for r in EL.opening_rects(elev, face)["rects"] if r.get("shutters_refused")]
    if _no_leaves:
        _rooms = sorted({str(r.get("room")).upper() for r in _no_leaves})
        notes.append(f'SHUTTERS NOT DRAWN ON {len(_no_leaves)} WINDOW(S) \u2014 ' +
                     _esc(", ".join(_rooms[:6]) + (" \u2026" if len(_rooms) > 6 else "")) +
                     ' \u2014 A LEAF WOULD LIE OVER ITS NEIGHBOUR: THE PIER IS NARROWER THAN '
                     'SASH-LIGHT\u2019S LEAF, AND A LEAF THAT CANNOT SWING ONTO WALL CANNOT BE HUNG')
    if any("garage" in str(r.get("type") or "").lower() for r in _doors):
        notes.append('GARAGE DOOR DRAWN AS ITS OPENING \u2014 NO RECORD STATES ITS FACE')
        # AND WHERE THE GARAGE DOOR IS THE ONE THE COMPOSITION DRESSES, THE DOORCASE IS NOT
        # DRAWN AROUND IT: the entrance is the widest door on the entrance front, and on a plan
        # whose only door there is the garage's that is a garage door, which no doorcase frames.
        if any(r.get("entrance") and "garage" in str(r.get("type") or "").lower() for r in _doors):
            notes.append('THE ENTRANCE FRONT\u2019S ONLY DOOR IS A GARAGE DOOR \u2014 NO DOORCASE, '
                         'SIDELIGHT OR TRANSOM IS DRAWN AROUND IT')
    if any("garage" not in str(r.get("type") or "").lower() for r in _doors) or \
            any(r.get("shutter_leaf_width_in") for r in EL.opening_rects(elev, face)["rects"]):
        notes.append('DOOR AND SHUTTER PANELS ARE DRAWN AS THEIR ARRANGEMENT, NOT THEIR SIZE: NO '
                     'RECORD STATES A STILE OR A RAIL OF EITHER')
    # THE WINDOW SURROUND THE KIT NAMES AND THE RECORD CANNOT DECIDE (WP-14.3). Twenty-two of the
    # styles this sheet draws make an architrave and a bare opening both canonical, so which this
    # house has is not a fact the record holds; the reveal is its own slot and is drawn.
    _ws = elev.get("window_surround") or {}
    if _ws.get("why") and any(r["kind"] == "window" for r in EL.opening_rects(elev, face)["rects"]):
        notes.append("WINDOW SURROUND NOT DRAWN \u2014 " + _esc(_ws["why"].upper()))
    _d = elev.get("dormers") or {}
    if _d.get("count") and not _d.get("refused"):
        if _d.get("placeable") is False:
            notes.append('DORMERS DECLARED BUT NOT DRAWN — ' + _esc((_d.get("not_drawn_reason") or "").upper()))
        if _d.get("variant_undeclared_choices"):
            notes.append('DORMER VARIANT UNDECLARED — THIS STYLE MAKES '
                         f'{len(_d["variant_undeclared_choices"])} CANONICAL AND THE RECORD NAMES '
                         'NONE; DRAWN AS THE PLAIN GABLED FORM')
        _src = _d.get("variant_source_node")
        if _d.get("variant") and _src and _src != elev.get("style"):
            notes.append(f'DORMER VARIANT “{_d["variant"].replace("-", " ").upper()}” IS INHERITED FROM '
                         f'{_src.replace("-", " ").upper()} — THIS STYLE BINDS THE SLOT NOTHING (OQ 51)')
        if not _d.get("lights_across"):
            notes.append('DORMER SASH PATTERN UNDECLARED — THIS STYLE\u2019S KIT STATES NONE, SO THE '
                         'SASH IS DRAWN AS GLASS WITH NO GLAZING BARS RATHER THAN AT A GUESSED 6/6')
    # WHAT THE STACKS ARE, FROM THE STACKS DRAWN (WP-14.6). This line said "THE KIT MAKES THEM
    # GABLE-END EXTERIOR" and "THE 22″ FIGURE" on every sheet that drew a stack, whatever the
    # stack was: fourteen of the fifteen styles the census draws a stack for place it by an
    # interior rule, and the figure is whatever the record states. Words composed from the ink
    # they describe, or they are a second record of it.
    if chimneys_drawn:
        _sz = elev.get("chimney_stack_plan_in")
        _sz_txt = (f'{_sz:g}\u2033' if isinstance(_sz, (int, float)) else 'STATED')
        if stack_sides == {"exterior"}:
            _why = 'THEY STAND OUTSIDE THE GABLE WALL, SO NOTHING HIDES THE BREAST BELOW'
        elif stack_sides == {"interior"}:
            _why = 'THEY RISE INSIDE THE GABLE WALL, SO THE ROOF HIDES THE REST'
        else:
            _why = 'THE PLACEMENT PUTS THEM ON BOTH SIDES OF THE GABLE WALL'
        # the figure is said ONCE: where it is a judgment the judgment line above states it
        _at = ('' if (elev.get("chimney_stack_plan_judgment") and _sz)
               else f', AT THE {_sz_txt} SQUARE THE RECORD STATES')
        notes.append(f'STACKS DRAWN ABOVE THE ROOF LINE ONLY, ON THE SQUARE THE PLACEMENT SEATS'
                     f'{_at} — {_why}; NO RULE IN THIS CORPUS STATES A BREAST\u2019S WIDTH')
    if stacks_unplaced:
        # THE PLACEMENT'S OWN REASON, republished rather than composed a second time (`_porch`'s
        # rule for `plan.threshold.unplaced`, one record over): on 43 of the 47 styles the roof
        # sweep reaches this way it is that no canonical hearth position says which face of the
        # end wall the mass stands on, and a stack drawn anyway would be seated by this sheet.
        _hr = (((elev.get("section") or {}).get("geometry") or {}).get("hearths") or {})
        _why = next((u.get("reason") for u in (_hr.get("unplaced") or [])
                     if u.get("what") == "the stacks" and u.get("reason")), None)
        notes.append(f'{stacks_unplaced} STACK(S) NOT DRAWN — THE PLACEMENT SEATS NO SQUARE FOR THEM'
                     + (': ' + _why.upper() if _why else
                        ', AND WHICH SIDE OF THE GABLE WALL A STACK STANDS ON IS THE PLAN\u2019S FACT'))
    if stacks_not_side_gable:
        notes.append('STACKS NOT DRAWN — THIS ROOF\u2019S RIDGE RUNS FRONT TO BACK, AND THIS SHEET '
                     'DRAWS A STACK AGAINST A SIDE GABLE\u2019S RAKE ONLY')
    for i, n in enumerate(notes):
        s.append(f'<text class="dm" x="{pad}" y="{legend_y+26+i*10:.1f}">{_esc(n)}</text>')
    # THE SHEET GROWS WITH ITS NOTES (WP-14.3). The legend was a fixed 90 px, which holds six
    # notes; a sheet saying more ran its last lines off the canvas, where nothing is read -- a
    # disclosure the sheet does not make. The root element is rewritten after the inset, below,
    # so the height taken here is the one it carries.
    total_h = max(total_h, legend_y + 26 + len(notes) * 10 + 12)

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
    # CLEAR OF WHAT STANDS PAST THE FACE (WP-14.6, audit F12). An exterior end stack stands wholly
    # outboard of its gable wall -- 1.83 ft, 44 px, on the Tidewater plan -- and the inset stood
    # 30 px past the face, so its box was drawn 14 px over the right-hand stack on both long faces.
    # The inset moves out by whatever the stacks overhang, and the sheet grows to hold it.
    _overhang = max(0.0, _stack_right_px - (ox + pw))
    total_w += _overhang
    ibox_x, ibox_y = ox + pw + _overhang + 30, oy + 6
    ibox_w, ibox_h = inset_w - 12, ph * 0.86
    naked_in = cornice.get("frieze_naked_in") or 0.0
    # The ENTABLATURE's own datum, which is not always the pack's declared one -- see
    # elevation.py::eave_cornice. Reading the pack-level `axis` over a cornice whose frieze
    # records a projection of 0 clamps its bed mould flush and deletes it from the drawing.
    from_axis = cornice.get("entablature_projection_datum", cornice.get("projection_datum")) == "axis"
    relief = cornice.get("order_relief_beyond_frieze_in") or max(
        (mm["projection_in"] for mm in cornice["members"]
         if mm.get("projection_in") is not None), default=1.0)
    members = cornice["members"]
    drawn_h = max((mm["y_top_in"] for mm in members), default=1.0) or 1.0
    prof_w = ibox_w * 0.34                       # the profile's own column; the rest is legend
    ik = min(prof_w / max(relief, 1.0), (ibox_h - 34) / drawn_h)
    px0, py0 = ibox_x + 16, ibox_y + 20          # profile origin: frieze face, springing of the bed
    isx = lambda x: px0 + (x - naked_in) * ik
    isy = lambda y: py0 + (drawn_h - y) * ik
    # WP-14.1: THE INSET IS A SECOND PLATE, at its own scale and in INCHES, and it says so. Its
    # pixels are not the face's: a reader holding the face plate's px_per_ft over this profile
    # reads a 24 in cornice as a few inches of building. `u` is inches out from the frieze naked
    # (which sits at u = naked_in), `v` inches up from the cornice's springing; `datum` is the
    # entablature's own. Appended LAST, so a reader selecting the face by its id -- the Round's
    # frameOf -- still finds the face plate first.
    _frames["plates"].append({"id": "inset", "proj": "profile", "unit": "in",
                              "px_per_in": round(ik, 6), "origin_px": [round(px0, 4), round(py0, 4)],
                              "at_origin_in": [round(naked_in, 6), round(drawn_h, 6)],
                              "datum": "axis" if from_axis else "naked"})
    s[0] = _head()

    s.append(f'<rect class="pf" x="{ibox_x:.1f}" y="{ibox_y:.1f}" width="{ibox_w:.1f}" height="{ibox_h:.1f}"/>')
    s.append(f'<text class="lb" x="{ibox_x+8:.1f}" y="{ibox_y-4:.1f}">EAVE CORNICE PROFILE</text>')
    # The frieze face, which is the plane every projection above is measured against.
    s.append(f'<line x1="{isx(naked_in):.1f}" y1="{isy(0):.1f}" x2="{isx(naked_in):.1f}" y2="{isy(drawn_h):.1f}" '
             f'stroke="{PAL["ink3"]}" stroke-width="0.5" stroke-dasharray="2 2"/>')
    sil = PROF.silhouette(members, naked_at=naked_in, from_axis=from_axis)
    # The fill and the ink are two paths, and a member whose projection nobody published is a
    # dashed bracket rather than a face (WP-14.2) -- the profile plates' rule, on the one plate
    # that sits on a building sheet.
    d = PROF.svg_path(sil["segments"], isx, isy, start=sil["start"])
    if d:
        s.append(f'<path d="{d}" fill="{PAL["brass"]}" fill-opacity="0.5" stroke="none"/>')
        ink = PROF.svg_path(sil["segments"], isx, isy, start=sil["start"], ghosts="move")
        s.append(f'<path d="{ink}" fill="none" stroke="{PAL["ink"]}" stroke-width="0.9"/>')
    ghost_ids = {u["id"] for u in sil["unpublished"]}
    ghosts = " ".join(g for g in (PROF.ghost_bracket(u["x"], u["y0"], u["y1"], sil["ghost_tick"],
                                                     isx, isy) for u in sil["unpublished"]) if g)
    if ghosts:
        s.append(f'<path class="ghost" d="{ghosts}" fill="none" stroke="{PAL["ink"]}" '
                 f'stroke-width="0.7" stroke-dasharray="3 2"/>')
    # Confidence, marked as the workbench and the profile plates mark it (WP-14.2).
    weak = [sp for sp in sil["spans"] if PROF.is_weak(sp.get("confidence")) and sp["y1"] > sp["y0"]]
    for sp in weak:
        s.append(f'<path class="confidence" data-member="{_esc(sp["id"])}" '
                 f'd="{PROF.band_path(sp, isx, isy)}" fill="none" stroke="{PAL["ink3"]}" '
                 f'stroke-width="0.8" stroke-dasharray="2 2"/>')
    envs = " ".join(e for e in (PROF.envelope_box(u["x0"], u["y0"], u["x1"], u["y1"], isx, isy)
                                for u in sil["unconstructed"]) if e)
    if envs:
        s.append(f'<path class="envelope" d="{envs}" fill="none" stroke="{PAL["ink"]}" '
                 f'stroke-width="0.7" stroke-dasharray="1.5 2"/>')

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
        face = isx(naked_in if m.get("id") in ghost_ids
                   else PROF.outer_face(naked_in, m["projection_in"], from_axis))
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
    # THE PACK DRAWN, named (WP-14.2): this read 'GIBBS IONIC' as a literal whatever pack
    # elevation.eave_cornice had been handed. A cornice the pack inherits says whose it is.
    pk, owner = cornice.get("order_pack") or "?", cornice.get("cornice_owner")
    who = pk.upper() + ("" if not owner or owner == pk else f" (THE CORNICE {owner.upper()}'S)")
    cap = [f'{who} · {len(members)} MEMBERS AT A {round(cornice["reduced_gibbs_module_in"],1)}″ MODULE',
           ("PROJECTIONS ARE RADII FROM THE COLUMN AXIS" if from_axis
            else "PROJECTIONS ARE RELIEF FROM THE FRIEZE NAKED")]
    if env and abs(env - relief) > 0.5:
        # Two sourced rules, one address, different answers. The sheet names both rather than
        # letting the reader believe the drawing settled it.
        cap.append(f"ORDER PROJECTS {relief:.1f}″; THE DOMESTIC ENVELOPE RULE SAYS {env:.1f}″ — BOTH SOURCED")
    if sil["unconstructed"]:
        # Never draw a shape this corpus has no construction for without saying which.
        cap.append(", ".join(sorted({u["profile"].upper() for u in sil["unconstructed"]}))
                   + " NOT CONSTRUCTED — DRAWN AS THE DASHED BOX THEIR HEIGHT AND PROJECTION BOUND")
    if weak:
        cap.append(f'{len(weak)} MEMBER(S) OUTLINED DASHED — CONFIDENCE MEDIUM, LOW OR UNSTATED')
    if sil["drawn_straight"]:
        # A cyma drawn as a vertical stroke looks exactly like a fascia (WP-14.2).
        cap.append(f'{len(sil["drawn_straight"])} CURVED MEMBER(S) DRAWN STRAIGHT — '
                   f'NO RUN BETWEEN THEIR FACES')
    if sil["unpublished"]:
        # A face drawn flush because the authority published no figure looks exactly like a face
        # measured flush. Saying which is the whole difference.
        cap.append(f'{len(sil["unpublished"])} MEMBER(S) DRAWN AS A DASHED BRACKET AT THE NAKED — '
                   f'NO PROJECTION PUBLISHED')
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
