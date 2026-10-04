#!/usr/bin/env python3
"""Render a WP-3.1 section record to SVG. Two views, each drawn only from the record
`build/structure.py`'s `build_section()` already produced -- neither function re-opens a plan,
re-runs `geometry.py`, or re-derives a number the record does not already carry. That is the
hand-off brief's own instruction ('a section SVG rendered only from the record') taken literally,
and it is the same discipline `render_plan.py` already applies to a solved plan.

  render_section(section, path)          -- a vertical building section: grade, storey floor
                                             lines, eave, and the ridge where one is judged.
  render_bearing_diagram(section, path)  -- a plan-view diagram, one panel per level, showing
                                             which interior walls are bearing (on the bay grid)
                                             versus partition, and flagging any span that
                                             span_check() found exceeds its structure's capacity.
"""
import os
import textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def _mod(n, p):
    # Delegates to build/modcache.py so a module is executed once per process rather than
    # once per call (OQ 28). Loaded by path because this file is itself usually loaded by
    # path, so `build/` is not necessarily on sys.path yet.
    import sys as _sys
    _b = os.path.join(ROOT, "build")
    if _b not in _sys.path:
        _sys.path.insert(0, _b)
    import modcache as _mc
    return _mc.load(n, p)
SS = _mod("sheet_style", f"{ROOT}/build/sheet_style.py")
DISC = _mod("disclosures", f"{ROOT}/build/disclosures.py")

# The palette is build/sheet_style.py's now -- ONE spelling, not four. It carried a verbatim
# copy of the same ten-key dict, under a comment saying the duplication was the price of every
# build/*.py module being loadable standalone; modcache.load answers that, and the copies were
# the reason a colour could be changed in one renderer and not in its neighbours. `DARK` is
# byte-for-byte what stood here, proved over all ten sheets corpus.drawing() produces.
PAL = SS.DARK

def _esc(t): return (t or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
_attr = SS.attr   # a double-quoted attribute's value; a text node keeps `_esc`

def _fmt(x):
    if x is None: return "?"
    ft = int(x); inch = round((x - ft) * 12)
    if inch == 12: ft += 1; inch = 0
    return f"{ft}'-{inch}\"" if inch else f"{ft}'"

def _style_block():
    return (f'<style>'
            f'text{{font-family:"Archivo",-apple-system,"Segoe UI",sans-serif;fill:{PAL["ink2"]}}}'
            f'.nm{{font-size:9.5px;fill:{PAL["ink"]}}}.dm{{font-size:7.5px;fill:{PAL["ink3"]};font-family:ui-monospace,Menlo,monospace}}'
            f'.hd{{font-family:"Bodoni Moda",Georgia,serif;font-size:19px;fill:{PAL["ink"]}}}'
            f'.lb{{font-family:ui-monospace,Menlo,monospace;font-size:8.5px;letter-spacing:.14em;fill:{PAL["ink3"]}}}'
            f'.wl{{stroke:{PAL["ink"]};stroke-width:2.2;fill:none;stroke-linejoin:miter}}'
            f'.gr{{stroke:{PAL["brass"]};stroke-width:1.6;fill:none}}'
            f'.fl{{stroke:{PAL["ink3"]};stroke-width:0.8;stroke-dasharray:2 3;fill:none}}'
            f'.bad{{stroke:{PAL["iron"]};stroke-width:2.4;fill:none}}'
            # THE CUT WALL IS A BODY (WP-14.3), solid as a section's cut always is, and the floor
            # structure a lighter band at its stated depth -- where the envelope was two lines of
            # no thickness against a record stating 15.5 in.
            f'.wb{{fill:{PAL["ink"]};fill-opacity:0.85;stroke:{PAL["ink"]};stroke-width:0.6}}'
            f'.fs{{fill:{PAL["ink3"]};fill-opacity:0.35;stroke:none}}'
            f'</style>')

# ---------------------------------------------------------------------- vertical section
def render_section(section, path, scale=7.0):
    """A single vertical slice: grade line, each storey's floor line and ceiling label, the
    eave, and the ridge where roof_heights() judged a pitch. The roof span drawn is the span
    roof_heights() raised the ridge over -- the footprint's dimension ACROSS the ridge the roof
    record draws (`threshold.ridge_span`, stated on the record as `span_ft`) -- so the picture and
    the number it illustrates always agree. It was the footprint's shorter dimension whatever
    the roof did until the audit of Phase 16 (WP-16.8): on good-03, whose ridge B9 runs along
    the shorter dimension, the section cut the roof across the house the other way. A record
    from before then states no span and keeps the shorter dimension.

    A REFUSED ROOF IS SAID AS ONE (B8): the record carries `refused` and no ridge, and the sheet
    prints NO ROOF DRAWN with the refusal's own words where it printed RIDGE UNJUDGED -- a roof
    the style's kit forbids is not a roof nobody could judge."""
    fp = section["footprint"]
    roof = section["roof"]
    span_ft = roof.get("span_ft") or min(fp["width_ft"], fp["depth_ft"])
    storeys = [s for s in section["storeys"] if s.get("storey_height_ft") is not None and (s.get("index") or 0) >= 0]
    storeys.sort(key=lambda s: s["index"])
    top_ft = roof.get("grade_to_ridge_ft") or (roof["grade_to_eave_ft"] + 4)

    pad, left_gutter, right_gutter, top_pad, bottom_pad = 42, 92, 130, 60, 46
    # A ROOF FORM THE KIT DECIDED BY A RECORD ITS WRITER FLAGS A JUDGMENT, SAID (T3; WP-16.8, the
    # audit of Phase 16, auditors C and D): the elevation and the roof plan said it and this sheet,
    # which draws the same roof's ridge, did not. A line beneath the title, the drawing lowered by it.
    form_judgment = DISC.roof_form_judgment(roof)
    pw = span_ft * scale
    # AND WRAPPED TO THE SHEET (the audit of WP-16.8's own diff, 3 Oct 2026, auditor B): it was one
    # line, 8.5 px monospace at .14em (6.3 px a character), and on all seven sections that print
    # it the sentence ran 124 to 299 px past a 542-579 px canvas -- the clipped tail being "MARKS
    # THE CALL A JUDGMENT", which is the clause the line exists to say. Wrapped as the bay-module
    # line below is, the top margin growing by the lines it takes.
    fj_lines = (textwrap.wrap(form_judgment, max(24, int((left_gutter + pw + right_gutter) / 6.3)),
                              break_long_words=False, break_on_hyphens=False)
                if form_judgment else [])
    if fj_lines:
        top_pad += 14 + 12 * (len(fj_lines) - 1)
    # WRAPPED, NOT CUT (WP-14.3). An unjudged ridge's note says why, and it was cut at seventy
    # characters -- mid-word, and before the reason on most records. It is wrapped to the span
    # and stands above the eave, so the top margin grows by the lines it takes.
    ridge_lines = []
    if roof.get("grade_to_ridge_ft") is None:
        line, cols = "", max(40, int(pw / 4.55))
        _head = "NO ROOF DRAWN — " if roof.get("refused") else "RIDGE UNJUDGED — "
        for w in (_head + (roof.get("note") or "")).split():
            if line and len(line) + 1 + len(w) > cols:
                ridge_lines.append(line)
                line = w
            else:
                line = f"{line} {w}" if line else w
        if line:
            ridge_lines.append(line)
        top_pad += 10 * max(0, len(ridge_lines) - 1)
    ph = top_ft * scale
    total_w = pad * 2 + left_gutter + pw + right_gutter
    total_h = top_pad + ph + bottom_pad
    ox, oy = pad + left_gutter, top_pad
    Y = lambda h_ft: oy + (top_ft - h_ft) * scale   # grade at bottom, height increases upward

    # WP-12.4: see build/sheet_style.py::frame_attr. `u` is the distance across the span from
    # its left edge, `v` the height above grade -- this drawing's own two axes.
    _frames = {"plates": [{"id": "section", "proj": "section", "px_per_ft": scale,
                           "origin_px": [ox, oy], "at_origin_ft": [0.0, round(top_ft, 3)]}]}
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w:.0f}" height="{total_h:.0f}" '
         f'viewBox="0 0 {total_w:.0f} {total_h:.0f}" data-frame=\'{SS.frame_attr(_frames)}\' '
         f'style="background:{PAL["ground"]}">']
    s.append(_style_block())
    s.append(f'<text class="hd" x="{pad}" y="26">{_esc(section.get("plan_id",""))} — SECTION</text>')
    s.append(f'<text class="lb" x="{pad}" y="42">{_esc(section.get("style",""))} · '
              f'{_esc(section["wall"]["construction_type"])} · SPAN {_fmt(span_ft)}</text>')
    if fj_lines:
        # one <text> carrying a line per <tspan>, every line but the last ending in its space, so
        # the sentence reads back whole off the ink (`tests/inkread.py` joins a text's spans)
        _sp = "".join(f'<tspan x="{pad}" y="{58 + 12 * i}">{_esc(ln)}{" " if i < len(fj_lines) - 1 else ""}'
                      f'</tspan>' for i, ln in enumerate(fj_lines))
        s.append(f'<text class="lb" x="{pad}" y="58">{_sp}</text>')

    # grade
    s.append(f'<line class="gr" x1="{ox-24:.1f}" y1="{Y(0):.1f}" x2="{ox+pw+24:.1f}" y2="{Y(0):.1f}"/>')
    s.append(f'<text class="dm" x="{ox-30:.1f}" y="{Y(0)+3:.1f}" text-anchor="end">GRADE</text>')

    # storey envelope walls (left and right exterior wall lines) and floor lines
    grade_first = storeys[0]["grade_to_floor_ft"] if storeys and storeys[0].get("grade_to_floor_ft") is not None else 2.0
    # THE EXTERIOR WALLS AS BODIES (WP-14.3, census S1). The span drawn is the footprint's
    # OUTSIDE dimension, so each wall stands inward from its own face at the thickness the
    # section states -- `structure.wall_thickness`, the one reader of the construction type.
    # They were two lines of no thickness on all sixteen sections. A section whose record states
    # no thickness keeps the line and says so, rather than drawing a wall of a width nobody gave.
    t_in = (section.get("wall") or {}).get("exterior_in")
    eave_y = Y(roof["grade_to_eave_ft"])
    if t_in:
        tw = t_in / 12.0 * scale
        for wx in (ox, ox + pw - tw):
            s.append(f'<rect class="wb" x="{wx:.2f}" y="{eave_y:.2f}" width="{tw:.2f}" '
                     f'height="{Y(0) - eave_y:.2f}"/>')
    else:
        s.append(f'<line class="wl" x1="{ox:.1f}" y1="{Y(0):.1f}" x2="{ox:.1f}" y2="{eave_y:.1f}"/>')
        s.append(f'<line class="wl" x1="{ox+pw:.1f}" y1="{Y(0):.1f}" x2="{ox+pw:.1f}" y2="{eave_y:.1f}"/>')
        s.append(f'<text class="dm" x="{ox+4:.1f}" y="{Y(0)-6:.1f}">WALLS DRAWN AS LINES — THE '
                 f'RECORD STATES NO EXTERIOR WALL THICKNESS</text>')
        tw = 0.0
    s.append(f'<line class="wl" x1="{ox:.1f}" y1="{Y(0):.1f}" x2="{ox+pw:.1f}" y2="{Y(0):.1f}"/>')

    for st in storeys:
        floor = st.get("grade_to_floor_ft")
        if floor is None: continue
        ceil_line = floor + st["storey_height_ft"]
        # THE FLOOR STRUCTURE AT ITS STATED DEPTH, between this storey's CEILING and the floor
        # above it (the eave, at the top storey), between the walls. `storeys.py` derives
        # `floor_structure_depth_in` as exactly that gap -- the storey height less the clear
        # ceiling -- so that is where the joists are. The first version (WP-14.3) hung the body
        # UNDER the storey's own floor: one storey out on every section, with a ground-storey
        # body standing in the crawl space where the record states only grade-to-floor, and
        # nothing under the eave. Found by rendering the sections and looking (WP-14.6).
        fd = st.get("floor_structure_depth_in")
        if fd:
            s.append(f'<rect class="fs" data-storey="{_attr(str(st.get("index")))}" x="{ox + tw:.2f}" '
                     f'y="{Y(floor + st["storey_height_ft"]):.2f}" '
                     f'width="{pw - 2 * tw:.2f}" height="{fd / 12.0 * scale:.2f}"/>')
        s.append(f'<line class="fl" x1="{ox:.1f}" y1="{Y(floor):.1f}" x2="{ox+pw:.1f}" y2="{Y(floor):.1f}"/>')
        cy = Y((floor + ceil_line) / 2)
        st_label = st["id"] or f'level {st.get("index")}'
        s.append(f'<text class="nm" x="{ox+8:.1f}" y="{cy-2:.1f}">{_esc(st_label)}</text>')
        s.append(f'<text class="dm" x="{ox+8:.1f}" y="{cy+10:.1f}">ceiling {_fmt(st["ceiling_ft"])} · '
                  f'storey {_fmt(st["storey_height_ft"])} · floor structure {st["floor_structure_depth_in"]}"</text>')

    # eave
    eave = roof["grade_to_eave_ft"]
    s.append(f'<line class="gr" x1="{ox-10:.1f}" y1="{Y(eave):.1f}" x2="{ox+pw+10:.1f}" y2="{Y(eave):.1f}"/>')
    s.append(f'<text class="dm" x="{ox+pw+16:.1f}" y="{Y(eave)+3:.1f}">EAVE {_fmt(eave)}</text>')

    # roof
    if roof.get("grade_to_ridge_ft") is not None:
        ridge = roof["grade_to_ridge_ft"]
        mx = ox + pw / 2
        s.append(f'<path class="wl" d="M {ox:.1f} {Y(eave):.1f} L {mx:.1f} {Y(ridge):.1f} L {ox+pw:.1f} {Y(eave):.1f}"/>')
        s.append(f'<text class="dm" x="{mx:.1f}" y="{Y(ridge)-6:.1f}" text-anchor="middle">'
                  f'RIDGE {_fmt(ridge)} · {roof["roof_pitch_rise_per_12"]}:12 ({roof["pitch_source"]})</text>')
    else:
        s.append(f'<line class="fl" x1="{ox:.1f}" y1="{Y(eave):.1f}" x2="{ox+pw:.1f}" y2="{Y(eave):.1f}"/>')
        for i, ln in enumerate(ridge_lines):
            s.append(f'<text class="dm" x="{ox:.1f}" y="{Y(eave) - 8 - 10 * (len(ridge_lines) - 1 - i):.1f}">'
                     f'{_esc(ln)}</text>')

    # scale bar
    # likewise: `.fl` sets a dashed grey stroke, so the scale bar was drawn as a floor line
    s.append(f'<line class="fl" x1="{ox:.1f}" y1="{total_h-18:.1f}" x2="{ox+10*scale:.1f}" y2="{total_h-18:.1f}" style="stroke:{PAL["brass"]};stroke-dasharray:none"/>')
    s.append(f'<text class="dm" x="{ox:.1f}" y="{total_h-6:.1f}">10 ft</text>')
    s.append('</svg>')
    open(path, "w").write("\n".join(s))
    return path

# ---------------------------------------------------------------------- bearing-line plan
def render_bearing_diagram(section, path, scale=7.0):
    """One panel per level: every wall line from wall_lines()/bearing_lines(), bearing walls
    drawn heavy, partitions drawn light and dashed, and any span_check() finding that failed
    drawn as a highlighted bar across the offending bay -- the exact case the WP-3.1 acceptance
    text names ('no 2x10 spanning 18 ft passes silently') made visible, not just logged."""
    fp = section["footprint"]
    W, H = fp["clear_width_ft"], fp["clear_depth_ft"]   # wall_lines() was built in the clear coordinate frame
    levels = section["levels"]
    pad, gap, top = 42, 54, 78
    # EACH PLATE IS THE EXTENT OF THE WALLS IT DRAWS, NOT OF THE MAIN BLOCK (WP-14.6, audit F5).
    # The canvas was the clear footprint, which since WP-11.6 is the main block alone, while
    # `build_section` lays each massing element's walls out in the same frame -- so the tagged
    # Tidewater plan's west dependency, 34 ft west of the block's origin, drew its bearing lines
    # up to 196 px off the left edge of the sheet, where nothing is read. The frame's origin
    # moves with the extent and `data-frame` states it, so a reader of the plate still maps
    # every pixel to the clear frame. On a one-rectangle house every wall lies inside [0, W] x
    # [0, H] and the sheet is byte-identical.
    _xs, _ys = [0.0, W], [0.0, H]
    for lv in levels:
        for w in lv["walls"]:
            (_xs if w["axis"] == "x" else _ys).append(w["position_ft"])
            (_ys if w["axis"] == "x" else _xs).extend((w["lo_ft"], w["hi_ft"]))
    X0, X1, Y0, Y1 = min(_xs), max(_xs), min(_ys), max(_ys)
    _blocks = {b.get("id"): b for b in
               (((section.get("geometry") or {}).get("footprint") or {}).get("blocks") or [])
               if b.get("id") is not None}
    pw, ph = (X1 - X0) * scale, (Y1 - Y0) * scale
    total_w = pad * 2 + len(levels) * pw + max(0, len(levels) - 1) * gap
    # THE MODULE THE BEARING WALLS ARE READ OFF, WHERE THE RECORD STATES NONE (audit, 27 Sep 2026).
    # `build_section` records whether its module is the record's or the placer's default, and this
    # plate -- whose whole subject is the walls read off that module -- said nothing, while the
    # plan sheet has said it since WP-14.4. One spelling, `disclosures.no_bay_module`; WRAPPED to
    # the canvas (7.5 px monospace, 4.6 px a character), because a one-level plate of a narrow
    # house is narrower than the sentence and a line run off the sheet is a disclosure it does not
    # make. The canvas grows by the extra lines; with no note it is byte-identical.
    _bm = section.get("bay_module") or {}
    _bm_lines = (textwrap.wrap(DISC.no_bay_module(DISC.bearing_off_default(_bm["ft"])),
                               max(24, int((total_w - 2 * pad) / 4.6)),
                               break_long_words=False, break_on_hyphens=False)
                 if _bm and not _bm.get("on_record") else [])
    total_h = top + ph + 60 + 10 * max(0, len(_bm_lines) - 1)

    # WP-12.4: one plate per level, so one entry per level -- and the loop below reads the
    # SAME origin function, which is what stops the attribute and the ink drifting apart.
    # NOTE the frame here is the CLEAR one (wall_lines() was built in it), not the outside
    # frame render_plan.py draws; `proj` is what tells the two apart.
    def _plate_origin(i):
        return (pad + i * (pw + gap), top)

    _frames = {"plates": [
        {"id": lv.get("id") or str(i), "proj": "bearing", "level": lv.get("index", i),
         "px_per_ft": scale,
         "origin_px": [round(_plate_origin(i)[0], 3), round(_plate_origin(i)[1], 3)],
         "at_origin_ft": [round(X0, 3) + 0.0, round(Y1, 3)]}
        for i, lv in enumerate(levels)]}
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w:.0f}" height="{total_h:.0f}" '
         f'viewBox="0 0 {total_w:.0f} {total_h:.0f}" data-frame=\'{SS.frame_attr(_frames)}\' '
         f'style="background:{PAL["ground"]}">']
    s.append(_style_block())
    s.append(f'<text class="hd" x="{pad}" y="26">{_esc(section.get("plan_id",""))} — BEARING LINES</text>')
    s.append(f'<text class="lb" x="{pad}" y="42">HEAVY = BEARING · DASHED = PARTITION · RED = SPAN EXCEEDS CAPACITY</text>')

    for i, lv in enumerate(levels):
        ox, oy = _plate_origin(i)      # the SAME function data-frame was built from
        X = lambda v, ox=ox: ox + (v - X0) * scale
        Yc = lambda v, oy=oy: oy + (Y1 - v) * scale
        s.append(f'<text class="lb" x="{ox:.1f}" y="{oy-10:.1f}">{_esc((lv.get("id") or "").upper())}</text>')
        s.append(f'<rect x="{X(X0):.1f}" y="{Yc(Y1):.1f}" width="{pw:.1f}" height="{ph:.1f}" fill="{PAL["paper"]}" stroke="none"/>')

        for w in lv["walls"]:
            cls = "wl" if w["bearing"] else "fl"
            if w["axis"] == "x":
                x1 = x2 = X(w["position_ft"]); y1, y2 = Yc(w["hi_ft"]), Yc(w["lo_ft"])
            else:
                y1 = y2 = Yc(w["position_ft"]); x1, x2 = X(w["lo_ft"]), X(w["hi_ft"])
            s.append(f'<line class="{cls}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>')

        # WP-7.4 audit: THE MARKER IS DRAWN OVER THE BAY THAT FAILS, ON THE AXIS THE SPAN RUNS
        # ALONG. It used to feed an x-axis span's midpoint -- an X coordinate -- into `Yc`, the
        # y mapping, and then draw the line across the WHOLE plate rather than between the two
        # walls the span sits between. On the Tidewater plan that put the 20->60 ft x-axis
        # finding at Yc(40.0), which is 0.6 px inside a 40.08 ft deep panel: a horizontal bar
        # lying on the north exterior wall, with its label above the panel top colliding with
        # the level caption. The wall loop above already draws an axis-"x" wall as a VERTICAL
        # line at X(position); a span BETWEEN two such walls therefore runs along x and its
        # marker is horizontal, from X(from) to X(to).
        #
        # This is a pre-existing error (WP-3.1) that no reference plan ever reached, because
        # both of them reported zero over-capacity spans until WP-7.4a made span_check read the
        # bearing flag. The first thing that fix did was make a wrong drawing visible.
        for sp in lv.get("spans_exceeding_capacity", []):
            a, b = sp["from_ft"], sp["to_ft"]
            # ACROSS THE MIDDLE OF THE SPAN'S OWN ELEMENT (WP-14.6), which `build_section` names on
            # every span it measures per element; the main block's middle is the fallback for a
            # span that names none. The main block's middle put the west dependency's 27 ft span
            # across the hyphen gap, clear of the walls it spans between.
            eb = _blocks.get(sp.get("element"))
            mid_y = (eb["y_ft"] + eb["depth_ft"] / 2.0) if eb else H / 2.0
            mid_x = (eb["x_ft"] + eb["width_ft"] / 2.0) if eb else W / 2.0
            if sp["axis"] == "x":
                x1, x2 = X(a), X(b); y = Yc(mid_y)
                s.append(f'<line class="bad" x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" stroke-dasharray="6 3"/>')
                lx, ly = (x1 + x2) / 2.0, y - 4
            else:
                y1, y2 = Yc(a), Yc(b); x = X(mid_x)
                s.append(f'<line class="bad" x1="{x:.1f}" y1="{y1:.1f}" x2="{x:.1f}" y2="{y2:.1f}" stroke-dasharray="6 3"/>')
                lx, ly = x + 4, (y1 + y2) / 2.0
            # style=, not fill=: `.dm` sets a fill and a class rule beats a presentation
            # attribute, so this sheet's own legend promised RED = SPAN EXCEEDS CAPACITY
            # and then drew the failing figure in the same grey as the wall tally
            s.append(f'<text class="dm" x="{lx:.1f}" y="{ly:.1f}" style="fill:{PAL["iron"]}">{sp["span_ft"]} ft &gt; {sp["max_span_ft"]} ft</text>')

        bearing_n = sum(1 for w in lv["walls"] if w["bearing"])
        s.append(f'<text class="dm" x="{ox:.1f}" y="{oy+ph+18:.1f}">{len(lv["walls"])} WALL LINES, {bearing_n} BEARING, '
                  f'{len(lv.get("spans_exceeding_capacity", []))} SPAN(S) OVER CAPACITY</text>')

    for _k, _ln in enumerate(_bm_lines):
        s.append(f'<text class="dm" x="{pad}" y="{top+ph+36+10*_k:.1f}">{_esc(_ln)}</text>')

    s.append('</svg>')
    open(path, "w").write("\n".join(s))
    return path
