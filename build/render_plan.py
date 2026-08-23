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

    # ---------------------------------------------------------- WP-2.4 site / lot geometry
    # Model coordinates already put south (the street side, by the existing window-wall
    # convention below) at y=0 and north at y=H, origin at the building's own SW corner —
    # the lot is the same coordinate system, just usually bigger, with the building inset
    # from its edges by the setbacks. A plan with no lot_width_ft/lot_depth_ft (from `site`,
    # falling back to the older `context` location) renders exactly as before this package —
    # every extra_* stays 0 and nothing about the existing layout changes.
    site = plan.get("site") or {}
    ctx = plan.get("context") or {}
    lot_w = site.get("lot_width_ft"); lot_w = lot_w if lot_w is not None else ctx.get("lot_width_ft")
    lot_d = site.get("lot_depth_ft"); lot_d = lot_d if lot_d is not None else ctx.get("lot_depth_ft")
    has_lot = bool(lot_w and lot_d)
    x_off = y_off = 0.0
    extra_left = extra_right = extra_top = extra_bottom = 0.0
    setback_side = setback_front = setback_rear = None
    if has_lot:
        setback_side = site.get("setback_side_ft")
        x_off = setback_side if setback_side is not None else max(0.0, (lot_w - W) / 2)
        setback_front = site.get("setback_front_ft") or 0.0
        setback_rear = site.get("setback_rear_ft")
        y_off = setback_front
        extra_left = x_off * scale
        extra_right = max(0.0, lot_w - W - x_off) * scale
        extra_bottom = y_off * scale
        extra_top = max(0.0, lot_d - H - y_off) * scale

    pad, gap, top = 42, 58, 96
    pw, ph = W*scale, H*scale
    panel_w = pw + extra_left + extra_right
    total_w = pad*2 + len(levels)*panel_w + (len(levels)-1)*gap
    total_h = top + extra_top + ph + extra_bottom + 84
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
        ox = pad + i*(panel_w+gap) + extra_left; oy = top + extra_top
        # convert model (x east, y north, origin SW) to screen (y down)
        X = lambda v, ox=ox: ox + v*scale
        Y = lambda v, oy=oy: oy + (H - v)*scale
        s.append(f'<text class="lb" x="{ox}" y="{oy-12}">{_esc((lv.get("name") or lv["id"]).upper())}</text>')
        if has_lot:
            lx0, ly0, lx1, ly1 = -x_off, -y_off, lot_w - x_off, lot_d - y_off
            s.append(f'<rect x="{X(lx0):.1f}" y="{Y(ly1):.1f}" width="{(lx1-lx0)*scale:.1f}" height="{(ly1-ly0)*scale:.1f}" '
                     f'fill="none" stroke="{PAL["ink3"]}" stroke-width="1.2" stroke-dasharray="2 3"/>')
            s.append(f'<text class="dm" x="{X(lx0):.1f}" y="{(Y(ly1)-6):.1f}">LOT {_fmt(lot_w)} x {_fmt(lot_d)}</text>')
            # buildable envelope: lot inset by the actual front/side/rear setbacks, which is
            # not always exactly where the building sits (setback_side/setback_rear may be
            # unstated, in which case x_off/y_off above already fell back to a centred guess)
            sf = setback_front or 0.0
            ss = setback_side if setback_side is not None else x_off
            sr = setback_rear if setback_rear is not None else max(0.0, ly1 - H)
            ex0, ey0, ex1, ey1 = ss - x_off, sf - y_off, (lot_w - ss) - x_off, (lot_d - sr) - y_off
            s.append(f'<rect x="{X(ex0):.1f}" y="{Y(ey1):.1f}" width="{(ex1-ex0)*scale:.1f}" height="{(ey1-ey0)*scale:.1f}" '
                     f'fill="none" stroke="{PAL["copper"]}" stroke-width="0.8" stroke-dasharray="5 3"/>')
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
                # WP-2.2: render door swings -- a quarter-circle leaf sweep, hinged at one end
                # of the opening, into whichever of the two rooms sits on the far side (`b`,
                # i.e. `t`/the door's own "to" room, for a consistent convention). Radius is
                # the door's own drawn width (2*dw); direction is read off the two rooms'
                # centres, not assumed, so it swings the right way whichever side b is on.
                swing_r = 2 * dw          # NOT named `r` -- the outer loop variable is `r` (the room)
                if horiz:
                    a_cy = a["y_ft"] + a["depth_ft"] / 2
                    b_cy = b["y_ft"] + b["depth_ft"] / 2
                    up = b_cy > a_cy       # b is north of a -> swing toward model-north -> screen-up
                    hx, hy = X(px) - dw, Y(py)
                    ex, ey = hx, hy + (-swing_r if up else swing_r)
                    sweep = 0 if up else 1
                else:
                    a_cx = a["x_ft"] + a["width_ft"] / 2
                    b_cx = b["x_ft"] + b["width_ft"] / 2
                    right = b_cx > a_cx    # b is east of a
                    hx, hy = X(px), Y(py) - dw
                    ex, ey = hx + (swing_r if right else -swing_r), hy
                    sweep = 1 if right else 0
                s.append(f'<path d="M {hx:.1f} {hy:.1f} A {swing_r:.1f} {swing_r:.1f} 0 0 {sweep} {ex:.1f} {ey:.1f}" '
                         f'fill="none" stroke="{PAL["ink3"]}" stroke-width="0.6" stroke-dasharray="2 2"/>')
                s.append(f'<line x1="{hx:.1f}" y1="{hy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{PAL["ink3"]}" stroke-width="0.6"/>')
        # scale bar
        s.append(f'<line class="pt" x1="{X(0):.1f}" y1="{Y(0)+22:.1f}" x2="{X(10):.1f}" y2="{Y(0)+22:.1f}" stroke="{PAL["brass"]}"/>')
        s.append(f'<text class="dm" x="{X(0):.1f}" y="{Y(0)+34:.1f}">10 ft</text>')
        # north arrow: a real glyph, not just the caption, since screen-up is model-north by
        # this file's own X/Y convention above. street_bearing_deg (WP-2.4, from `site`) is
        # reported as a label rather than used to rotate the drawing -- the room rectangles
        # are axis-aligned to the model frame, not to true north, so an honest arrow points
        # up and says what bearing that up direction actually is on the ground.
        nx, ny = X(W) - 8, Y(0) + 12
        s.append(f'<g stroke="{PAL["brass"]}" fill="{PAL["brass"]}">'
                 f'<line x1="{nx:.1f}" y1="{ny:.1f}" x2="{nx:.1f}" y2="{ny-16:.1f}" stroke-width="1.4"/>'
                 f'<path d="M {nx-3.5:.1f} {ny-11:.1f} L {nx:.1f} {ny-18:.1f} L {nx+3.5:.1f} {ny-11:.1f} Z"/>'
                 f'</g>')
        street_bearing = site.get("street_bearing_deg") if has_lot else None
        cap = "NORTH IS UP" + (f" · STREET BEARS {street_bearing:.0f}°" if street_bearing is not None else "")
        s.append(f'<text class="dm" x="{X(W):.1f}" y="{Y(0)+34:.1f}" text-anchor="end">{cap}</text>')
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
