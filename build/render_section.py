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

# The palette is build/sheet_style.py's now -- ONE spelling, not four. It carried a verbatim
# copy of the same ten-key dict, under a comment saying the duplication was the price of every
# build/*.py module being loadable standalone; modcache.load answers that, and the copies were
# the reason a colour could be changed in one renderer and not in its neighbours. `DARK` is
# byte-for-byte what stood here, proved over all ten sheets corpus.drawing() produces.
PAL = SS.DARK

def _esc(t): return (t or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

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
            f'</style>')

# ---------------------------------------------------------------------- vertical section
def render_section(section, path, scale=7.0):
    """A single vertical slice: grade line, each storey's floor line and ceiling label, the
    eave, and the ridge where roof_heights() judged a pitch. The roof span drawn is the
    footprint's own shorter outside dimension -- the same one build_section's roof_heights()
    used to compute the ridge rise, so the picture and the number it illustrates always agree."""
    fp = section["footprint"]
    span_ft = min(fp["width_ft"], fp["depth_ft"])
    roof = section["roof"]
    storeys = [s for s in section["storeys"] if s.get("storey_height_ft") is not None and (s.get("index") or 0) >= 0]
    storeys.sort(key=lambda s: s["index"])
    top_ft = roof.get("grade_to_ridge_ft") or (roof["grade_to_eave_ft"] + 4)

    pad, left_gutter, right_gutter, top_pad, bottom_pad = 42, 92, 130, 60, 46
    pw = span_ft * scale
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

    # grade
    s.append(f'<line class="gr" x1="{ox-24:.1f}" y1="{Y(0):.1f}" x2="{ox+pw+24:.1f}" y2="{Y(0):.1f}"/>')
    s.append(f'<text class="dm" x="{ox-30:.1f}" y="{Y(0)+3:.1f}" text-anchor="end">GRADE</text>')

    # storey envelope walls (left and right exterior wall lines) and floor lines
    grade_first = storeys[0]["grade_to_floor_ft"] if storeys and storeys[0].get("grade_to_floor_ft") is not None else 2.0
    s.append(f'<line class="wl" x1="{ox:.1f}" y1="{Y(0):.1f}" x2="{ox:.1f}" y2="{Y(roof["grade_to_eave_ft"]):.1f}"/>')
    s.append(f'<line class="wl" x1="{ox+pw:.1f}" y1="{Y(0):.1f}" x2="{ox+pw:.1f}" y2="{Y(roof["grade_to_eave_ft"]):.1f}"/>')
    s.append(f'<line class="wl" x1="{ox:.1f}" y1="{Y(0):.1f}" x2="{ox+pw:.1f}" y2="{Y(0):.1f}"/>')

    for st in storeys:
        floor = st.get("grade_to_floor_ft")
        if floor is None: continue
        ceil_line = floor + st["storey_height_ft"]
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
        s.append(f'<text class="dm" x="{ox:.1f}" y="{Y(eave)-8:.1f}">RIDGE UNJUDGED — {_esc((roof.get("note") or "")[:70])}</text>')

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
    pw, ph = W * scale, H * scale
    total_w = pad * 2 + len(levels) * pw + max(0, len(levels) - 1) * gap
    total_h = top + ph + 60

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
         "at_origin_ft": [0.0, round(H, 3)]}
        for i, lv in enumerate(levels)]}
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w:.0f}" height="{total_h:.0f}" '
         f'viewBox="0 0 {total_w:.0f} {total_h:.0f}" data-frame=\'{SS.frame_attr(_frames)}\' '
         f'style="background:{PAL["ground"]}">']
    s.append(_style_block())
    s.append(f'<text class="hd" x="{pad}" y="26">{_esc(section.get("plan_id",""))} — BEARING LINES</text>')
    s.append(f'<text class="lb" x="{pad}" y="42">HEAVY = BEARING · DASHED = PARTITION · RED = SPAN EXCEEDS CAPACITY</text>')

    for i, lv in enumerate(levels):
        ox, oy = _plate_origin(i)      # the SAME function data-frame was built from
        X = lambda v, ox=ox: ox + v * scale
        Yc = lambda v, oy=oy: oy + (H - v) * scale
        s.append(f'<text class="lb" x="{ox:.1f}" y="{oy-10:.1f}">{_esc((lv.get("id") or "").upper())}</text>')
        s.append(f'<rect x="{X(0):.1f}" y="{Yc(H):.1f}" width="{pw:.1f}" height="{ph:.1f}" fill="{PAL["paper"]}" stroke="none"/>')

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
            if sp["axis"] == "x":
                x1, x2 = X(a), X(b); y = Yc(H / 2.0)
                s.append(f'<line class="bad" x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" stroke-dasharray="6 3"/>')
                lx, ly = (x1 + x2) / 2.0, y - 4
            else:
                y1, y2 = Yc(a), Yc(b); x = X(W / 2.0)
                s.append(f'<line class="bad" x1="{x:.1f}" y1="{y1:.1f}" x2="{x:.1f}" y2="{y2:.1f}" stroke-dasharray="6 3"/>')
                lx, ly = x + 4, (y1 + y2) / 2.0
            # style=, not fill=: `.dm` sets a fill and a class rule beats a presentation
            # attribute, so this sheet's own legend promised RED = SPAN EXCEEDS CAPACITY
            # and then drew the failing figure in the same grey as the wall tally
            s.append(f'<text class="dm" x="{lx:.1f}" y="{ly:.1f}" style="fill:{PAL["iron"]}">{sp["span_ft"]} ft &gt; {sp["max_span_ft"]} ft</text>')

        bearing_n = sum(1 for w in lv["walls"] if w["bearing"])
        s.append(f'<text class="dm" x="{ox:.1f}" y="{oy+ph+18:.1f}">{len(lv["walls"])} WALL LINES, {bearing_n} BEARING, '
                  f'{len(lv.get("spans_exceeding_capacity", []))} SPAN(S) OVER CAPACITY</text>')

    s.append('</svg>')
    open(path, "w").write("\n".join(s))
    return path
