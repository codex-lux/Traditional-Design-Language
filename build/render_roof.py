#!/usr/bin/env python3
"""Render a WP-3.3 roof record to SVG -- a plan-view roof plan, drawn only from the record
build/roof.py's own build_roof() already produced (the same discipline build/render_section.py
states for the section record: nothing here re-derives a number, it only draws the ones already
in `roof["outline"]`, `roof["chimneys"]`, and `roof["main"]`).

  render_roof(roof, path)
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
        # `ok` is None where the rule could not be judged, and the plate must not read that as a
        # FAIL -- a falsy check here turned an unjudged verdict into a conviction on the drawing,
        # which is the three-state rule breaking on the one surface a reader actually looks at.
        verdict = "UNJUDGED" if w.get("ok") is None else ("OK" if w["ok"] else "FAIL")
        line2.append(f"WING RIDGE {w['ratio']*100:.0f}% OF MAIN — {verdict}")
    cape = checks.get("cape_eave", {})
    if cape.get("computed"):
        line2.append(f"CAPE EAVE {'OK' if cape['ok'] else 'FAIL'}")
    gb = checks.get("gambrel_break", {})
    if gb.get("applicable"):
        # `break_ok` is None where the break fraction is the generator's own default tested
        # against the band it was taken from -- the same circularity the wing ridge carries, and
        # the same rule: an unjudged verdict is not a FAIL. `diff_ok` is a real comparison of two
        # stated pitches and stays boolean, so the two halves are reported separately rather than
        # ANDed into one word that would have to mean three things.
        pitch = "OK" if gb.get("diff_ok") else "FAIL"
        brk = "UNJUDGED" if gb.get("break_ok") is None else ("OK" if gb["break_ok"] else "FAIL")
        line2.append(f"GAMBREL PITCH DIFF {pitch} · BREAK {brk}")
    if line2:
        s.append(f'<text class="dm" x="{ox:.1f}" y="{legend_y+14:.1f}">{" · ".join(line2)}</text>')

    s.append('</svg>')
    open(path, "w").write("\n".join(s))
    return path
