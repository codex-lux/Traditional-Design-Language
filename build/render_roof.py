#!/usr/bin/env python3
"""Render a WP-3.3 roof record to SVG -- a plan-view roof plan, drawn only from the record
build/roof.py's own build_roof() already produced (the same discipline build/render_section.py
states for the section record: nothing here re-derives a number, it only draws the ones already
in `roof["outline"]`, `roof["chimneys"]`, and `roof["main"]`).

  render_roof(roof, path)
"""
import os

# Palette duplicated from build/render_plan.py / build/render_section.py rather than imported --
# every build/*.py module in this corpus is loaded standalone via importlib, so importing
# another renderer for one colour dict is not worth the coupling.
PAL = {"ground": "#0B1B29", "paper": "#0F2536", "rule": "#24455E", "ink": "#EDE7DA", "ink2": "#9FB3C2",
       "ink3": "#63808F", "brass": "#D8B26A", "verd": "#7FB3A3", "copper": "#C4734A", "iron": "#C4553A"}

LINE_CLASS = {"eave": "ev", "ridge": "rg", "hip": "hp", "gambrel-break": "gb", "cross-ridge": "cr"}

def _esc(t): return (t or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _style_block():
    return (f'<style>'
            f'text{{font-family:"Archivo",-apple-system,"Segoe UI",sans-serif;fill:{PAL["ink2"]}}}'
            f'.dm{{font-size:7.5px;fill:{PAL["ink3"]};font-family:ui-monospace,Menlo,monospace}}'
            f'.hd{{font-family:"Bodoni Moda",Georgia,serif;font-size:19px;fill:{PAL["ink"]}}}'
            f'.lb{{font-family:ui-monospace,Menlo,monospace;font-size:8.5px;letter-spacing:.14em;fill:{PAL["ink3"]}}}'
            f'.ev{{stroke:{PAL["ink"]};stroke-width:2.2;fill:none}}'
            f'.rg{{stroke:{PAL["brass"]};stroke-width:2.4;fill:none}}'
            f'.hp{{stroke:{PAL["ink3"]};stroke-width:1.2;fill:none;stroke-dasharray:4 3}}'
            f'.gb{{stroke:{PAL["verd"]};stroke-width:1.2;fill:none;stroke-dasharray:2 3}}'
            f'.cr{{stroke:{PAL["copper"]};stroke-width:2.0;fill:none}}'
            f'.chm{{fill:{PAL["iron"]};stroke:{PAL["ink"]};stroke-width:0.6}}'
            f'</style>')

def render_roof(roof, path, scale=7.0):
    fp = roof["footprint"]
    W, H = fp["width_ft"], fp["depth_ft"]
    pad, top = 42, 78
    pw, ph = W * scale, H * scale
    # the canvas is sized to the FOOTPRINT, and the legend below it is a fixed 99-character
    # string ~445px wide at .dm — so on anything under about 56 ft the key was clipped by
    # the viewBox and the reader was never told what the red dot means
    LEGEND = ("EAVE (SOLID) · RIDGE (BRASS) · HIP (DASHED GREY) · "
              "GAMBREL BREAK (DASHED GREEN) · CHIMNEY (RED DOT)")
    total_w = max(pad * 2 + pw, pad * 2 + len(LEGEND) * 4.55)
    total_h = top + ph + 60

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w:.0f}" height="{total_h:.0f}" '
         f'viewBox="0 0 {total_w:.0f} {total_h:.0f}" style="background:{PAL["ground"]}">']
    s.append(_style_block())
    s.append(f'<text class="hd" x="{pad}" y="26">{_esc(roof.get("plan_id",""))} — ROOF PLAN</text>')
    m = roof["main"]
    pitch_txt = f'{m["pitch_rise_per_12"]}:12' if m.get("pitch_rise_per_12") else "pitch unjudged"
    s.append(f'<text class="lb" x="{pad}" y="42">{_esc(roof.get("style",""))} · {_esc(m.get("form",""))} · {pitch_txt}</text>')

    ox, oy = pad, top
    X = lambda v: ox + v * scale
    Y = lambda v: oy + (H - v) * scale   # model y-north-up, screen y-down -- same convention as render_plan.py/render_section.py

    s.append(f'<rect x="{X(0):.1f}" y="{Y(H):.1f}" width="{pw:.1f}" height="{ph:.1f}" fill="{PAL["paper"]}" stroke="none"/>')

    for ln in roof["outline"]:
        cls = LINE_CLASS.get(ln["kind"], "ev")
        s.append(f'<line class="{cls}" x1="{X(ln["x1"]):.1f}" y1="{Y(ln["y1"]):.1f}" x2="{X(ln["x2"]):.1f}" y2="{Y(ln["y2"]):.1f}"/>')

    for c in roof.get("chimneys", {}).get("positions", []):
        r = 3.2
        s.append(f'<circle class="chm" cx="{X(c["x_ft"]):.1f}" cy="{Y(c["y_ft"]):.1f}" r="{r:.1f}"/>')

    legend_y = oy + ph + 18
    s.append(f'<text class="dm" x="{ox:.1f}" y="{legend_y:.1f}">{LEGEND}</text>')

    checks = roof.get("checks", {})
    line2 = []
    w = checks.get("wing_step_down", {})
    if w.get("computed"):
        line2.append(f"WING RIDGE {w['ratio']*100:.0f}% OF MAIN — {'OK' if w['ok'] else 'FAIL'}")
    cape = checks.get("cape_eave", {})
    if cape.get("computed"):
        line2.append(f"CAPE EAVE {'OK' if cape['ok'] else 'FAIL'}")
    gb = checks.get("gambrel_break", {})
    if gb.get("applicable"):
        line2.append(f"GAMBREL BREAK {'OK' if (gb['diff_ok'] and gb['break_ok']) else 'FAIL'}")
    if line2:
        s.append(f'<text class="dm" x="{ox:.1f}" y="{legend_y+14:.1f}">{" · ".join(line2)}</text>')

    s.append('</svg>')
    open(path, "w").write("\n".join(s))
    return path
