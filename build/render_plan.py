#!/usr/bin/env python3
"""Render a plan record with geometry to SVG. The drawing is a render of the data — if a
dimension is wrong the picture is wrong in the same way, which is the point."""
import json, os, importlib.util, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def _mod(n, p):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
C = _mod("plan_check", f"{ROOT}/build/plan_check.py").load_corpus()

PAL = {"ground":"#0B1B29","paper":"#0F2536","rule":"#24455E","ink":"#EDE7DA","ink2":"#9FB3C2",
       "ink3":"#63808F","brass":"#D8B26A","verd":"#7FB3A3","copper":"#C4734A","iron":"#C4553A"}
FILL = {"public":"#1B3A4E","living":"#1B3A4E","dining":"#1D4051","circulation":"#14304a",
        "threshold":"#14304a","service":"#16303F","sanitary":"#173544","sleeping":"#1E3547",
        "work":"#16303F","storage":"#122A38","outdoor":"#0E2434"}

def _fmt(x):
    ft = int(x); inch = round((x-ft)*12)
    if inch == 12: ft += 1; inch = 0
    return f"{ft}'-{inch}\"" if inch else f"{ft}'"

def render(plan, path, scale=7.0):
    levels = [lv for lv in plan["levels"] if any("geometry" in r for r in lv["rooms"])]
    if not levels: raise SystemExit("no geometry on this plan — run build/geometry.py first")
    fp = plan.get("footprint", {})
    W, H = fp.get("width_ft", 40), fp.get("depth_ft", 30)
    pad, gap, top = 42, 58, 96
    pw, ph = W*scale, H*scale
    total_w = pad*2 + len(levels)*pw + (len(levels)-1)*gap
    total_h = top + ph + 84
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w:.0f}" height="{total_h:.0f}" '
         f'viewBox="0 0 {total_w:.0f} {total_h:.0f}" style="background:{PAL["ground"]}">']
    s.append(f'<style>'
             f'text{{font-family:"Archivo",-apple-system,"Segoe UI",sans-serif;fill:{PAL["ink2"]}}}'
             f'.nm{{font-size:9.5px;fill:{PAL["ink"]}}}.dm{{font-size:7.5px;fill:{PAL["ink3"]};font-family:ui-monospace,Menlo,monospace}}'
             f'.hd{{font-family:"Bodoni Moda",Georgia,serif;font-size:19px;fill:{PAL["ink"]}}}'
             f'.lb{{font-family:ui-monospace,Menlo,monospace;font-size:8.5px;letter-spacing:.14em;fill:{PAL["ink3"]}}}'
             f'.wl{{stroke:{PAL["ink"]};stroke-width:2.2;fill:none;stroke-linejoin:miter}}'
             f'.pt{{stroke:{PAL["rule"]};stroke-width:1;fill:none}}'
             f'.win{{stroke:{PAL["brass"]};stroke-width:2.6;fill:none}}'
             f'.dr{{stroke:{PAL["verd"]};stroke-width:1.5;fill:none}}'
             f'</style>')
    s.append(f'<text class="hd" x="{pad}" y="34">{_esc(plan["name"])}</text>')
    s.append(f'<text class="lb" x="{pad}" y="54">{_esc(plan.get("style",""))} · '
             f'{fp.get("bays","?")} BAYS OF {fp.get("bay_module_ft","?")} FT · '
             f'{_fmt(W)} x {_fmt(H)} · {fp.get("area_sf","?")} SF GROSS</text>')
    gr = plan.get("geometry_report", {})
    if gr:
        rl = gr.get("relaxations", {})
        s.append(f'<text class="lb" x="{pad}" y="70" fill="{PAL["copper"] if rl.get("count") else PAL["verd"]}">'
                 f'{rl.get("count",0)} CUT(S) OFF THE BAY LINE'
                 + (f", WORST {rl.get('max_off_grid_ft')} FT" if rl.get("count") else "") + '</text>')

    for i, lv in enumerate(levels):
        ox = pad + i*(pw+gap); oy = top
        # convert model (x east, y north, origin SW) to screen (y down)
        X = lambda v: ox + v*scale
        Y = lambda v: oy + (H - v)*scale
        s.append(f'<text class="lb" x="{ox}" y="{oy-12}">{_esc((lv.get("name") or lv["id"]).upper())}</text>')
        s.append(f'<rect x="{X(0):.1f}" y="{Y(H):.1f}" width="{pw:.1f}" height="{ph:.1f}" fill="{PAL["paper"]}" stroke="none"/>')
        # bay lines
        bm = fp.get("bay_module_ft") or 10
        b = bm
        while b < W - 0.01:
            s.append(f'<line class="pt" x1="{X(b):.1f}" y1="{Y(0):.1f}" x2="{X(b):.1f}" y2="{Y(H):.1f}" stroke-dasharray="3 4"/>')
            b += bm
        for r in lv["rooms"]:
            g = r.get("geometry")
            if not g: continue
            fc = FILL.get(C["rooms"].get(r["type"], {}).get("function_class"), "#16303F")
            x, y, w, h = g["x_ft"], g["y_ft"], g["width_ft"], g["depth_ft"]
            s.append(f'<rect x="{X(x):.1f}" y="{Y(y+h):.1f}" width="{w*scale:.1f}" height="{h*scale:.1f}" '
                     f'fill="{fc}" stroke="{PAL["rule"]}" stroke-width="0.8"/>')
        # walls on top so they read as continuous
        for r in lv["rooms"]:
            g = r.get("geometry")
            if not g: continue
            x, y, w, h = g["x_ft"], g["y_ft"], g["width_ft"], g["depth_ft"]
            s.append(f'<rect class="wl" x="{X(x):.1f}" y="{Y(y+h):.1f}" width="{w*scale:.1f}" height="{h*scale:.1f}" '
                     f'stroke-width="{1.0}"/>')
        s.append(f'<rect class="wl" x="{X(0):.1f}" y="{Y(H):.1f}" width="{pw:.1f}" height="{ph:.1f}"/>')
        # labels
        for r in lv["rooms"]:
            g = r.get("geometry")
            if not g: continue
            x, y, w, h = g["x_ft"], g["y_ft"], g["width_ft"], g["depth_ft"]
            cx, cy = X(x + w/2), Y(y + h/2)
            nm = r.get("name") or r["id"]
            if w*scale < 34 or h*scale < 20:
                if w*scale > 16 and h*scale > 11:
                    s.append(f'<text class="dm" x="{cx:.1f}" y="{cy+3:.1f}" text-anchor="middle">{_esc(nm[:9])}</text>')
                continue
            s.append(f'<text class="nm" x="{cx:.1f}" y="{cy-1:.1f}" text-anchor="middle">{_esc(nm)}</text>')
            s.append(f'<text class="dm" x="{cx:.1f}" y="{cy+11:.1f}" text-anchor="middle">'
                     f'{_fmt(min(w,h))} x {_fmt(max(w,h))} · {g["area_sf"]} sf</text>')
        # windows on exterior walls
        for r in lv["rooms"]:
            g = r.get("geometry")
            if not g: continue
            x, y, w, h = g["x_ft"], g["y_ft"], g["width_ft"], g["depth_ft"]
            for win in (r.get("windows") or []):
                wall = win.get("wall"); n = win.get("count") or 1
                for k in range(n):
                    t = (k+1)/(n+1)
                    ww = (win.get("width_ft") or 3)*scale*0.9
                    if wall == "S" and y <= 0.6:
                        cx = X(x + w*t); s.append(f'<line class="win" x1="{cx-ww/2:.1f}" y1="{Y(0):.1f}" x2="{cx+ww/2:.1f}" y2="{Y(0):.1f}"/>')
                    elif wall == "N" and y+h >= H-0.6:
                        cx = X(x + w*t); s.append(f'<line class="win" x1="{cx-ww/2:.1f}" y1="{Y(H):.1f}" x2="{cx+ww/2:.1f}" y2="{Y(H):.1f}"/>')
                    elif wall == "W" and x <= 0.6:
                        cy = Y(y + h*t); s.append(f'<line class="win" x1="{X(0):.1f}" y1="{cy-ww/2:.1f}" x2="{X(0):.1f}" y2="{cy+ww/2:.1f}"/>')
                    elif wall == "E" and x+w >= W-0.6:
                        cy = Y(y + h*t); s.append(f'<line class="win" x1="{X(W):.1f}" y1="{cy-ww/2:.1f}" x2="{X(W):.1f}" y2="{cy+ww/2:.1f}"/>')
        # doors where two rooms touch
        idx = {r["id"]: r.get("geometry") for r in lv["rooms"] if r.get("geometry")}
        drawn = set()
        for r in lv["rooms"]:
            a = idx.get(r["id"])
            if not a: continue
            for d in (r.get("doors") or []):
                t = d["to"]
                key = tuple(sorted((r["id"], t)))
                if t == "exterior" or t not in idx or key in drawn: continue
                drawn.add(key); b = idx[t]
                seg = _shared(a, b)
                if not seg: continue
                (px, py), horiz = seg
                dw = 3.0*scale/2
                if horiz: s.append(f'<line class="dr" x1="{X(px)-dw:.1f}" y1="{Y(py):.1f}" x2="{X(px)+dw:.1f}" y2="{Y(py):.1f}"/>')
                else: s.append(f'<line class="dr" x1="{X(px):.1f}" y1="{Y(py)-dw:.1f}" x2="{X(px):.1f}" y2="{Y(py)+dw:.1f}"/>')
        # scale bar
        s.append(f'<line class="pt" x1="{X(0):.1f}" y1="{Y(0)+22:.1f}" x2="{X(10):.1f}" y2="{Y(0)+22:.1f}" stroke="{PAL["brass"]}"/>')
        s.append(f'<text class="dm" x="{X(0):.1f}" y="{Y(0)+34:.1f}">10 ft</text>')
        s.append(f'<text class="dm" x="{X(W):.1f}" y="{Y(0)+34:.1f}" text-anchor="end">north is up</text>')
    s.append('</svg>')
    open(path, "w").write("\n".join(s))
    return path

def _shared(a, b, tol=0.4):
    ax, ay, aw, ah = a["x_ft"], a["y_ft"], a["width_ft"], a["depth_ft"]
    bx, by, bw, bh = b["x_ft"], b["y_ft"], b["width_ft"], b["depth_ft"]
    if abs((ax+aw)-bx) <= tol or abs((bx+bw)-ax) <= tol:
        x = bx if abs((ax+aw)-bx) <= tol else ax
        lo, hi = max(ay, by), min(ay+ah, by+bh)
        if hi-lo > 3.2: return ((x, (lo+hi)/2), False)
    if abs((ay+ah)-by) <= tol or abs((by+bh)-ay) <= tol:
        y = by if abs((ay+ah)-by) <= tol else ay
        lo, hi = max(ax, bx), min(ax+aw, bx+bw)
        if hi-lo > 3.2: return (((lo+hi)/2, y), True)
    return None

def _esc(t): return (t or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
