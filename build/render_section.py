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

# Palette duplicated from build/render_plan.py rather than imported -- this file, like every
# other build/*.py module in this corpus, is loaded standalone via importlib (see structure.py's
# own _mod()), and importing render_plan.py for a colour dict is not worth the coupling.
PAL = {"ground":"#0B1B29","paper":"#0F2536","rule":"#24455E","ink":"#EDE7DA","ink2":"#9FB3C2",
       "ink3":"#63808F","brass":"#D8B26A","verd":"#7FB3A3","copper":"#C4734A","iron":"#C4553A"}

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

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w:.0f}" height="{total_h:.0f}" '
         f'viewBox="0 0 {total_w:.0f} {total_h:.0f}" style="background:{PAL["ground"]}">']
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
    s.append(f'<line class="fl" x1="{ox:.1f}" y1="{total_h-18:.1f}" x2="{ox+10*scale:.1f}" y2="{total_h-18:.1f}" stroke="{PAL["brass"]}"/>')
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

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w:.0f}" height="{total_h:.0f}" '
         f'viewBox="0 0 {total_w:.0f} {total_h:.0f}" style="background:{PAL["ground"]}">']
    s.append(_style_block())
    s.append(f'<text class="hd" x="{pad}" y="26">{_esc(section.get("plan_id",""))} — BEARING LINES</text>')
    s.append(f'<text class="lb" x="{pad}" y="42">HEAVY = BEARING · DASHED = PARTITION · RED = SPAN EXCEEDS CAPACITY</text>')

    for i, lv in enumerate(levels):
        ox = pad + i * (pw + gap); oy = top
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

        for sp in lv.get("spans_exceeding_capacity", []):
            if sp["axis"] == "x":
                x1 = X(0); x2 = X(W); y = Yc((sp["from_ft"] + sp["to_ft"]) / 2)
                s.append(f'<line class="bad" x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" stroke-dasharray="6 3"/>')
            else:
                y1 = Yc(0); y2 = Yc(H); x = X((sp["from_ft"] + sp["to_ft"]) / 2)
                s.append(f'<line class="bad" x1="{x:.1f}" y1="{y1:.1f}" x2="{x:.1f}" y2="{y2:.1f}" stroke-dasharray="6 3"/>')
            lx, ly = (X(0) + 4, Yc((sp["from_ft"] + sp["to_ft"]) / 2) - 4) if sp["axis"] == "x" else (X((sp["from_ft"] + sp["to_ft"]) / 2) + 4, Yc(H) - 4)
            s.append(f'<text class="dm" x="{lx:.1f}" y="{ly:.1f}" fill="{PAL["iron"]}">{sp["span_ft"]} ft &gt; {sp["max_span_ft"]} ft</text>')

        bearing_n = sum(1 for w in lv["walls"] if w["bearing"])
        s.append(f'<text class="dm" x="{ox:.1f}" y="{oy+ph+18:.1f}">{len(lv["walls"])} WALL LINES, {bearing_n} BEARING, '
                  f'{len(lv.get("spans_exceeding_capacity", []))} SPAN(S) OVER CAPACITY</text>')

    s.append('</svg>')
    open(path, "w").write("\n".join(s))
    return path
