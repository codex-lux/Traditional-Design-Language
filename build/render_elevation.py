#!/usr/bin/env python3
"""Render a WP-3.2 elevation record (build/elevation.py's build_elevation()) to SVG -- a single
front-on face: wall plane, bay windows with sash/muntin grid and shutters, the entrance
composition (door, surround, entablature, sidelights where present), water table and belt course,
and the roofline (reusing build/roof.py's own elevation_profile(), not re-derived here), plus a
cross-section detail inset that draws the eave cornice's ACTUAL moulded profile.

That inset is the reason this file exists rather than just drawing flat bands everywhere: the
hand-off brief for WP-3.2 calls for porting orders_template.html's segTo() -- the function that
turns one proportion-engine member (a height, a projection, a profile name) into an SVG path
fragment for that moulding's own cross-section shape -- into Python, "the existing JavaScript/
Python engine agreement". seg_to() below is that port, line for line against the JS original
(build/orders_template.html), and profile_silhouette_path() is the same stepped-member walk
orders_template.html's own silhouettePath()/buildGeometry() do for a column shaft, simplified for
a flat entablature run (no entasis, no diminution -- an eave cornice or a door entablature has
neither): every moulding drawn in the cornice-detail inset comes from proportion_engine.dimension()
member data, not a traced profile.

  render_elevation(elev, path, face=None, scale=6.0)
"""
import os

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
    return (f'<style>'
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

# ---------------------------------------------------------------- moulding profile geometry
# Ported from build/orders_template.html's segTo(profile, xa, ya, xb, yb, sx, sy) (lines ~254-281
# there): xa/ya is the inner (starting) point of the member, xb/yb the outer (finishing) point,
# sx/sy the same screen-space transforms the JS original takes. h and dx below are the run's own
# height and horizontal offset, exactly as in the JS.
def seg_to(profile, xa, ya, xb, yb, sx, sy):
    h = yb - ya
    dx = xb - xa
    def A(x, y): return f"{sx(x):.2f},{sy(y):.2f}"
    if profile in ("ovolo", "quarter-round", "echinus"):
        return f" Q {A(xb, ya)} {A(xb, yb)}"
    if profile == "cavetto":
        return f" Q {A(xa, yb)} {A(xb, yb)}"
    if profile in ("apophyge", "congé", "conge"):
        return f" Q {A(xa, yb)} {A(xb, yb)}"
    if profile == "scotia":
        r = max(abs(dx), h)
        return f" C {A(xa - r * 0.55, ya + h * 0.25)} {A(xa - r * 0.35, yb - h * 0.15)} {A(xb, yb)}"
    if profile == "cyma-recta":
        return f" C {A(xa, ya + h * 0.58)} {A(xb, yb - h * 0.58)} {A(xb, yb)}"
    if profile in ("cyma-reversa", "ogee"):
        return f" C {A(xb, ya + h * 0.42)} {A(xa, yb - h * 0.42)} {A(xb, yb)}"
    if profile in ("astragal", "bead", "torus"):
        b = max(h * 0.62, abs(dx))
        return f" C {A(xa + b, ya)} {A(xa + b, yb)} {A(xb, yb)}"
    if profile == "bevel":
        return f" L {A(xb, yb)}"
    if profile in ("volute", "acanthus"):
        return f" C {A(xa + h * 0.35, ya + h * 0.2)} {A(xb - h * 0.2, yb - h * 0.25)} {A(xb, yb)}"
    # default: fillet, listel, fascia, plinth, corona, abacus, metope, dentil, modillion, mutule, triglyph, flat
    return f" L {A(xb, ya)} L {A(xb, yb)}"

def profile_silhouette_path(members, sx, sy, naked=0.0):
    """The same stepped walk orders_template.html's silhouettePath() does over buildGeometry()'s
    points, minus the column-shaft taper branch: an entablature/cornice run has no entasis or
    diminution (nothing in this codebase computes one for it), so every member's own outer face
    sits at a constant `naked + projection_in` for that member's own height span, and seg_to()
    alone decides the curve between one member's outer face and the next's. `members` must be in
    bottom-to-top order with y_bottom_in/y_top_in/projection_in/profile -- exactly what
    proportion_engine.dimension() returns, unmodified."""
    if not members:
        return ""
    pts = [{"x": naked + m["projection_in"], "y0": m["y_bottom_in"], "y1": m["y_top_in"],
            "profile": m.get("profile")} for m in members]
    d = f"M {sx(naked):.2f},{sy(0.0):.2f}"
    cx, cy = naked, 0.0
    for p in pts:
        if cx != p["x"]:
            d += f" L {sx(p['x']):.2f},{sy(cy):.2f}"
            cx = p["x"]
        d += seg_to(p["profile"], p["x"], p["y0"], p["x"], p["y1"], sx, sy)
        cx, cy = p["x"], p["y1"]
    d += f" L {sx(naked):.2f},{sy(cy):.2f} Z"
    return d

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

def _window(s, cx, y_bottom, y_top, width_in, lights_across, lights_high, shutter_w, shutter_h, X, Ypx, scale):
    x0, x1 = X(cx - width_in / 2 / 12.0), X(cx + width_in / 2 / 12.0)
    yb, yt = Ypx(y_bottom), Ypx(y_top)
    out = [f'<rect class="op" x="{x0:.1f}" y="{yt:.1f}" width="{x1-x0:.1f}" height="{yb-yt:.1f}"/>']
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
        # here from the SAME chimney records drawn below, not a separate guess
        for c in roof["chimneys"]["positions"]:
            if abs(c["x_ft"]) < 0.5 or abs(c["x_ft"] - span_ft) < 0.5:
                top_height_ft = max(top_height_ft, c["total_height_grade_ft"] + ridge_delta_ft)

    pad, top, legend_h = 46, 34, 90
    inset_w = 190
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

    if wtb["applicable"]:
        wt_top_ft = wtb["water_table_height_above_finished_grade_in"] / 12.0
        s.append(f'<rect class="wt" x="{X(0)-4:.1f}" y="{Ypx(wt_top_ft):.1f}" width="{pw+8:.1f}" height="{(wt_top_ft*scale):.1f}"/>')
        if wtb.get("belt_height_above_first_floor_in") is not None:
            belt_ft = floor2_ft
            belt_h_ft = wtb["belt_height_in"] / 12.0
            s.append(f'<rect class="wt" x="{X(0)-2:.1f}" y="{Ypx(belt_ft+belt_h_ft):.1f}" width="{pw+4:.1f}" height="{(belt_h_ft*scale):.1f}"/>')

    # frieze + cornice band, front-on (a plain projecting band here -- its own real moulded
    # profile is drawn full-size in the detail inset on the right, not traced in this small a space)
    s.append(f'<rect class="bd" x="{X(0)-6:.1f}" y="{Ypx(true_eave_ft):.1f}" width="{pw+12:.1f}" height="{(cornice_band_ft*scale):.1f}"/>')

    for cx, kind in zip(front["centres_ft"], front["kinds"]):
        if kind == "door" and face == elev["entrance_face"]:
            s.append(_entrance(elev, cx, floor1_ft, X, Ypx, scale))
        else:
            s.append(_window(s, cx, floor1_ft + gw["sill_height_above_floor_in"]/12.0, floor1_ft + gw["head_height_above_floor_in"]/12.0,
                              gw["opening_width_in"], gw["lights_across"], gw["lights_high_per_sash"],
                              gw["shutter_leaf_width_in"], gw["shutter_leaf_height_in"], X, Ypx, scale))
        s.append(_window(s, cx, floor2_ft + uw["sill_height_above_floor_in"]/12.0, floor2_ft + uw["head_height_above_floor_in"]/12.0,
                          uw["opening_width_in"], uw["lights_across"], uw["lights_high_per_sash"],
                          uw["shutter_leaf_width_in"], uw["shutter_leaf_height_in"], X, Ypx, scale))

    # roofline -- build/roof.py's own elevation_profile() numbers, shifted up by the cornice band
    # this file adds (see ridge_delta_ft above), not re-derived
    pts = " ".join(f"{X(x):.1f},{Ypx(h):.1f}" for x, h in profile_ft)
    s.append(f'<polyline class="rf" points="{pts}"/>')

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
            cw_ft = 36.0 / 12.0
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

    # ---------------- cornice detail inset: the actual moulded profile, drawn from
    # proportion_engine.dimension() members via profile_silhouette_path()/seg_to() above
    iw, ih = inset_w - 30, ph * 0.62
    iox, ioy = ox + pw + 30, oy + 10
    total_h_cor = cornice["cornice_height_in"] + cornice["frieze_height_in"]
    max_proj = max((mm["projection_in"] for mm in cornice["members"]), default=1.0)
    ik = min((iw - 10) / max(max_proj, 1.0), (ih - 10) / max(total_h_cor, 1.0))
    isx = lambda x: iox + x * ik
    isy = lambda y: ioy + ih - y * ik
    s.append(f'<rect class="pf" x="{iox-6:.1f}" y="{ioy-6:.1f}" width="{iw+12:.1f}" height="{ih+30:.1f}"/>')
    s.append(f'<text class="lb" x="{iox:.1f}" y="{ioy-10:.1f}">EAVE CORNICE PROFILE</text>')
    s.append(f'<line x1="{isx(0):.1f}" y1="{isy(0):.1f}" x2="{isx(0):.1f}" y2="{isy(total_h_cor):.1f}" stroke="{PAL["ink3"]}" stroke-width="0.6"/>')
    d = profile_silhouette_path(cornice["members"], isx, isy, naked=0.0)
    if d:
        s.append(f'<path d="{d}" fill="{PAL["brass"]}" fill-opacity="0.55" stroke="{PAL["ink"]}" stroke-width="0.8"/>')
    s.append(f'<text class="dm" x="{iox:.1f}" y="{ioy+ih+16:.1f}">{cornice["member_count"]} MEMBERS · GIBBS IONIC, REDUCED {round(cornice["reduced_gibbs_module_in"],1)} IN MODULE</text>')

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
