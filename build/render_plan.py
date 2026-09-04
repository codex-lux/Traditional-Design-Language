#!/usr/bin/env python3
"""Render a plan record with geometry to SVG. The drawing is a render of the data — if a
dimension is wrong the picture is wrong in the same way, which is the point."""
import json, os, importlib.util, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def _mod(n, p):
    # Delegates to build/modcache.py so a module is executed once per process
    # rather than once per call. Same signature, same standalone-script
    # behaviour; see that file's header for why (OQ 28). Loaded by path here
    # because this file is itself usually loaded by path, so `build/` is not
    # necessarily on sys.path yet.
    import sys as _sys
    _b = os.path.join(ROOT, "build")
    if _b not in _sys.path:
        _sys.path.insert(0, _b)
    import modcache as _mc
    return _mc.load(n, p)
C = _mod("plan_check", f"{ROOT}/build/plan_check.py").load_corpus()
DISC = _mod("disclosures", f"{ROOT}/build/disclosures.py")

_PARTIS = None
def _partis():
    """The parti records, by id, read once -- `disclosures.style_disagreement` uses them to
    ask whether the parti a plan names lists the style it is being judged as. Read lazily and
    cached because most sheets never carry a `parti` and a glob per render is a glob per
    render."""
    global _PARTIS
    if _PARTIS is None:
        import glob as _glob
        _PARTIS = {}
        for f in sorted(_glob.glob(f"{ROOT}/partis/*.json")):
            try:
                rec = json.load(open(f))
                _PARTIS[rec["id"]] = rec
            except Exception:
                continue
    return _PARTIS

PAL = {"ground":"#0B1B29","paper":"#0F2536","rule":"#24455E","ink":"#EDE7DA","ink2":"#9FB3C2",
       "ink3":"#63808F","brass":"#D8B26A","verd":"#7FB3A3","copper":"#C4734A","iron":"#C4553A"}
FILL = {"public":"#1B3A4E","living":"#1B3A4E","dining":"#1D4051","circulation":"#14304a",
        "threshold":"#14304a","service":"#16303F","sanitary":"#173544","sleeping":"#1E3547",
        "work":"#16303F","storage":"#122A38","outdoor":"#0E2434"}

# ---------------------------------------------------------------- room lettering
# A room's name has to fit in the room. Until 26 Aug 2026 this renderer set every name
# on one line at 9.5px whatever the room's width, so a name wider than its room ran
# through the walls on both sides -- and the small-room branch answered that by printing
# `nm[:9]`, which does not shorten a name, it amputates one: "Butler's Pantry" was drawn
# "Butler's " and read as the room's actual name. The rule now is the draughtsman's:
# break the name across lines first, shrink it only as far as it stays readable, turn it
# to run with the room where the room is a slot, and never truncate it.
#
# Widths are ESTIMATED -- this renderer has no font metrics, and an estimate that is
# occasionally a few percent wide is a label with a little air around it, where the old
# fixed size was a label through a wall. The advances below are for the sans face the
# sheet sets its names in; the dimension line is monospaced and measures exactly.
def _adv(ch):
    if ch in "iljI.,:;'|!": return 0.28
    if ch in "ft()[]r ": return 0.36
    if ch in "mwMW": return 0.86
    if ch.isupper() or ch.isdigit(): return 0.66
    return 0.53

def _text_w(text, size, mono=False):
    return size * (0.60 * len(text) if mono else sum(_adv(c) for c in text))

def _balance(words, n):
    """Split words into exactly n lines so the widest line is as narrow as it can be."""
    if n == 1: return [" ".join(words)]
    if n > len(words): return None
    best = None
    def walk(depth, start, cuts):
        nonlocal best
        if depth == n - 1:
            lines, prev = [], 0
            for c in cuts: lines.append(" ".join(words[prev:c])); prev = c
            lines.append(" ".join(words[prev:]))
            widest = max(_text_w(l, 1.0) for l in lines)
            if best is None or widest < best[0]: best = (widest, lines)
            return
        for c in range(start + 1, len(words) - (n - 2 - depth)):
            walk(depth + 1, c, cuts + [c])
    walk(0, 0, [])
    return best[1] if best else None

# The exhaustive split is C(W-1, n-1) arrangements, each costed over all W words -- O(W^3)
# at n=3. For a room name that is nothing; for a hostile one it is a CPU bomb, and a plan
# record arrives over HTTP from anyone who can reach /api/drawings. Measured here: 400
# words took 9.2 s, 800 took 73 s, and nothing in the schema bounds a room's name. Beyond
# MAX_WORDS the name is set as it stands rather than balanced -- it is still drawn whole,
# still shrunk to fit, and no longer worth a minute of somebody's server.
MAX_WORDS = 12

# MAX_WORDS bounds how many ARRANGEMENTS are searched. It does not bound how much text each
# arrangement is costed over, and _text_w walks every character of every line for each of the
# C(11,2)=55 arrangements a 12-word name still gets. So the 73-second bomb closed and a
# quieter one stayed open: measured here, twelve words of a thousand characters cost 74 ms and
# twelve words of twenty thousand cost 1466 ms — per room, with room count unbounded by the
# schema, on one POST /api/drawings.
#
# The cap is on the SEARCH, not on the text, because the rule above the function holds: a name
# is drawn whole or not at all. Past MAX_CHARS the name takes the same pre-chunked path a
# too-many-words name takes — still complete, still shrunk to fit, no longer costed 55 times.
MAX_CHARS = 400

def _fit_lines(text, max_w, max_h, preferred, floor, lead=1.2, max_lines=3):
    """(lines, size) for `text` inside max_w x max_h. The floor is a floor, not a
    target: a name that will not fit at it is still drawn, cramped and complete,
    because a reader can see cramped and cannot see truncated."""
    words = [w for w in str(text).split() if w]
    if not words: return None
    if len(words) > MAX_WORDS or sum(len(w) for w in words) > MAX_CHARS:
        # chunked into max_lines runs rather than balanced: linear, and a name this long
        # has no good arrangement anyway
        k = -(-len(words) // max_lines)
        words = [" ".join(words[i:i + k]) for i in range(0, len(words), k)]
    best = None
    for n in range(1, min(max_lines, len(words)) + 1):
        lines = _balance(words, n)
        if not lines: continue
        widest = max(_text_w(l, 1.0) for l in lines)
        size = min(preferred, max_w / widest if widest else preferred,
                   max_h / (n * lead) if n else preferred)
        if best is None or size > best[1]: best = (lines, size)
        if size >= preferred - 1e-6: break
    if best is None: return None
    return best[0], max(floor, best[1])

def _fmt(x):
    ft = int(x); inch = round((x-ft)*12)
    if inch == 12: ft += 1; inch = 0
    return f"{ft}'-{inch}\"" if inch else f"{ft}'"

def render(plan, path, scale=7.0):
    levels = [lv for lv in plan["levels"] if any("geometry" in r for r in lv["rooms"])]
    if not levels: raise SystemExit("no geometry on this plan — run build/geometry.py first")
    fp = plan.get("footprint", {})
    W, H = fp.get("width_ft", 40), fp.get("depth_ft", 30)

    # THE DRAWN EXTENT IS NOT THE MAIN BLOCK'S (OQ 40, 3 Sep 2026). `W` and `H` are the main
    # block, and they must stay that: `derive_openings` below reads them to decide which walls
    # are exterior, and widening them there would put windows on interior walls. But the SHEET
    # has to hold every element, and a house with a dependency has rooms outside the main
    # rectangle -- west of it at negative x, or east of it beyond `width_ft`.
    #
    # Found by rendering one. The plate is laid out as one panel per level, each `W * scale`
    # wide; a garage dependency placed at model x = 84 landed at SVG x = 630 in a ground panel
    # that ends at 532, so the garage, its mudroom and the breakfast room were drawn ON TOP OF
    # THE UPPER FLOOR'S PLATE. Nothing clipped and nothing complained -- the marks were inside
    # the canvas, just inside the wrong panel. That is this repository's own most expensive
    # class of bug (a third of an upper floor drawn outside its viewBox, found by looking at a
    # sheet rather than by any test), and it was introduced by the change that made a second
    # element placeable and caught by the audit of that change rather than by it.
    _pts = [r["geometry"] for lv in plan["levels"] for r in lv["rooms"] if r.get("geometry")]
    draw_x0 = min([g["x_ft"] for g in _pts] + [0.0]) if _pts else 0.0
    draw_y0 = min([g["y_ft"] for g in _pts] + [0.0]) if _pts else 0.0
    draw_W = (max([g["x_ft"] + g["width_ft"] for g in _pts] + [W]) if _pts else W) - draw_x0
    draw_H = (max([g["y_ft"] + g["depth_ft"] for g in _pts] + [H]) if _pts else H) - draw_y0

    # WP-6.1: resolved up front rather than inside the level loop, because the sheet's
    # banner has to state the totals and the banner is drawn before the plates.
    level_openings = [derive_openings(lv["rooms"], W, H) for lv in levels]
    all_undrawable = [u for op in level_openings for u in op["undrawable"]]
    all_diverged = [d for lv in levels for d in declared_divergence(lv["rooms"])]
    all_diverged.sort(key=lambda d: -abs(d["pct"]))
    diverged_ids = {d["id"] for d in all_diverged}
    # what each of those rooms ASKED for and what it GOT, for the table under the plates
    _decl_pair = {r["id"]: (r["width_ft"], r["length_ft"])
                  for lv in levels for r in lv["rooms"]
                  if r.get("width_ft") and r.get("length_ft")}
    _drawn_pair = {r["id"]: (r["geometry"]["width_ft"], r["geometry"]["depth_ft"])
                   for lv in levels for r in lv["rooms"] if r.get("geometry")}
    _name_unique = {}
    for _d in all_diverged:
        _name_unique[_d["name"]] = _name_unique.get(_d["name"], 0) + 1
    # and the same for the relaxation marks: which ones can be drawn on a wall of their own
    # level is decided here so the banner can state the ones that cannot.
    _rx_all = (plan.get("geometry_report", {}).get("relaxations", {}) or {}).get("marks", [])
    level_marks = [relaxation_marks(_rx_all, i, W, H) for i in range(len(levels))]
    all_unlocated = [m for _d, un in level_marks for m in un]

    # The header has to be as tall as the disclosures it carries. `top` was the constant 96
    # while the banner stack grew from one line to four, at 14 px each from y=70 -- three
    # disclosures already reached 98 and drew THROUGH the top of the first plate. A sheet
    # that hides its own disclosures behind the drawing is the WP-6.1 failure in a new place.
    # WP-6.4: and the plate says WHICH ENGINE placed it. WP-6.3 disclosed that in the
    # workbench's page prose, which is the one place it cannot travel -- this file's whole
    # output is a sheet somebody prints or hands to a builder, and it carried no disclosure
    # at all. A reader could not tell a proof from a search on the drawing itself.
    # WP-11.1: every banner line is computed in build/disclosures.py, and the workbench's
    # disclosure strip reads the SAME list through core.placement_summary. Before this the
    # engine line was built here and nowhere else, and it asserted the placement was proved
    # "against the record's declared facts" while the solver's own record said sixteen of
    # those facts had been set aside to reach it. Four more lines the record already carried
    # -- the set-aside walls, the objective that did not run, the undrawn windows and the
    # transfer beams -- had no reader at all.
    _banner = DISC.banner(plan, undrawable=all_undrawable, diverged=all_diverged,
                          unlocated=all_unlocated, styles=C["styles"], partis=_partis())
    # The banner's HEIGHT is the number of ROWS it wraps to, not the number of lines it holds
    # -- and the row count needs the plate's width, which is computed below and depends on
    # nothing above. So `_n_banner` is resolved after `total_w` rather than here; taking the
    # line count would under-reserve exactly when a line is long enough to wrap, which is the
    # case where a disclosure would then be drawn through the top of the first plate.

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
        extra_right = max(0.0, lot_w - draw_W - x_off) * scale
        extra_bottom = y_off * scale
        extra_top = max(0.0, lot_d - draw_H - y_off) * scale

    pad, gap = 42, 58
    pw, ph = draw_W*scale, draw_H*scale
    panel_w = pw + extra_left + extra_right
    total_w = pad*2 + len(levels)*panel_w + (len(levels)-1)*gap
    _banner_rows = [row for ln in _banner for row in _wrap_banner(ln["text"], total_w - 2*pad)]
    _n_banner = max(0, len(_banner_rows) - 1)   # the first row sits on the fixed y=70 line
    top = max(96, (84 if plan.get("geometry_report") else 70) + 14 * _n_banner + 8)
    # +84 is the footer (scale bar, legend, north arrow). The ∗ table sits below it and its
    # height is COMPUTED, not guessed: a fixed allowance is how a third of the upper floor
    # came to be drawn outside this canvas once already.
    _table_rows = 0
    if all_diverged:
        _cw = max(210.0, (pad*2 + len(levels)*panel_w + (len(levels)-1)*gap - 2*pad) / 3.0)
        _cols = max(1, int((pad*2 + len(levels)*panel_w + (len(levels)-1)*gap - 2*pad) // _cw))
        _table_rows = -(-len(all_diverged) // _cols)
    total_h = top + extra_top + ph + extra_bottom + 84 + (
        (66 - 84 + 15 + _table_rows * 11 + 14) if _table_rows else 0)
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
    # OQ 55: the hatch a reserved void that is open to the sky is filled with.
    s.append(f'<defs><pattern id="openvoid" width="9" height="9" patternUnits="userSpaceOnUse" '
             f'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="9" '
             f'stroke="{PAL["rule"]}" stroke-width="0.9" opacity="0.7"/></pattern></defs>')
    s.append(f'<text class="hd" x="{pad}" y="34">{_esc(plan["name"])}</text>')
    s.append(f'<text class="lb" x="{pad}" y="54">{_esc(plan.get("style",""))} · '
             f'{fp.get("bays","?")} BAYS OF {fp.get("bay_module_ft","?")} FT · '
             f'{_fmt(W)} x {_fmt(H)} · {fp.get("area_sf","?")} SF GROSS</text>')
    gr = plan.get("geometry_report", {})
    # The banner stack. `style=`, not `fill=`: `.lb` sets a fill and a class rule beats a
    # presentation attribute, so a line that computes a colour and writes it as an attribute
    # is drawn in the same quiet grey as every other caption -- a warning the sheet does not
    # give. Found once in WP-6.1 and it applies to every line here.
    banner_y = 70
    for _line in _banner:
        for _row in _wrap_banner(_line["text"], total_w - 2*pad):
            s.append(f'<text class="lb" x="{pad}" y="{banner_y}" '
                     f'style="fill:{PAL[_line["tone"]]}">{_esc(_row)}</text>')
            banner_y += 14

    for i, lv in enumerate(levels):
        ox = pad + i*(panel_w+gap) + extra_left; oy = top + extra_top
        # convert model (x east, y north, origin SW) to screen (y down)
        X = lambda v, ox=ox: ox + (v - draw_x0)*scale
        Y = lambda v, oy=oy: oy + (draw_H + draw_y0 - v)*scale
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
        # One paper ground and one perimeter per MASSING ELEMENT, not one rectangle across the
        # whole drawn extent. `pw`/`ph` are the extent the sheet is SIZED to, which spans the
        # hyphen gap: drawing the building outline at that size claims a 114 ft house where a
        # 70 ft house stands beside a 20 ft dependency, and on a WEST dependency `X(0)` is 34 ft
        # inside the panel so the rect ran 34 ft past its right edge and off the sheet. The
        # elements are what the record states, so the elements are what is drawn.
        _blocks = [(b["x_ft"], b["y_ft"], b["width_ft"], b["depth_ft"]) for b in (fp.get("blocks") or [])] \
            or [(0.0, 0.0, W, H)]
        for _bx, _by, _bw, _bh in _blocks:
            s.append(f'<rect x="{X(_bx):.1f}" y="{Y(_by+_bh):.1f}" width="{_bw*scale:.1f}" '
                     f'height="{_bh*scale:.1f}" fill="{PAL["paper"]}" stroke="none"/>')
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
            # OQ 55: a reserved void is drawn OPEN -- the ground colour, not a room fill, so a
            # court reads as the outside it is rather than as a dark room. A roofed void keeps a
            # faint fill, because a loggia is covered and a patio is not, and the drawing is
            # supposed to be able to tell you which.
            if g.get("void"):
                fc = "#12293A" if g["void"].get("roofed") else PAL["ground"]
            s.append(f'<rect x="{X(x):.1f}" y="{Y(y+h):.1f}" width="{w*scale:.1f}" height="{h*scale:.1f}" '
                     f'fill="{fc}" stroke="{PAL["rule"]}" stroke-width="0.8"/>')
            if g.get("void") and not g["void"].get("roofed"):
                # open to the sky: hatched over the ground colour, so it cannot be mistaken for
                # a room someone forgot to label. A tiling <pattern> rather than clipped lines --
                # the pattern is defined once in <defs> and cannot spill past the rect.
                s.append(f'<rect x="{X(x):.1f}" y="{Y(y+h):.1f}" width="{w*scale:.1f}" '
                         f'height="{h*scale:.1f}" fill="url(#openvoid)"/>')
        # walls on top so they read as continuous
        for r in lv["rooms"]:
            g = r.get("geometry")
            if not g: continue
            x, y, w, h = g["x_ft"], g["y_ft"], g["width_ft"], g["depth_ft"]
            # likewise: `.wl` sets stroke-width 2.2, so this 1.0 was discarded and every
            # interior room outline was drawn at the building perimeter's own weight
            s.append(f'<rect class="wl" x="{X(x):.1f}" y="{Y(y+h):.1f}" width="{w*scale:.1f}" height="{h*scale:.1f}" '
                     f'style="stroke-width:1"/>')
        for _bx, _by, _bw, _bh in _blocks:
            s.append(f'<rect class="wl" x="{X(_bx):.1f}" y="{Y(_by+_bh):.1f}" '
                     f'width="{_bw*scale:.1f}" height="{_bh*scale:.1f}"/>')
        # labels — wrapped, shrunk and where necessary turned to fit the room (see
        # _fit_lines): the name is never truncated and never crosses a wall
        for r in lv["rooms"]:
            g = r.get("geometry")
            if not g: continue
            x, y, w, h = g["x_ft"], g["y_ft"], g["width_ft"], g["depth_ft"]
            cx, cy = X(x + w/2), Y(y + h/2)
            nm = r.get("name") or r["id"]
            bw, bh = w*scale - 8, h*scale - 6
            if bw <= 4 or bh <= 5: continue
            # OQ 55's void disclosure is a statement about what the room IS, not an
            # embellishment on the dimension string -- carrying it as a tail made it ride
            # on `dim`'s fit, and since the tail LENGTHENS `dim` it dropped out for every
            # room under about 19 ft wide, which is most loggias and every piazza in the
            # catalogue. It is its own line now, drawn for every void whatever else fits.
            tail = ""
            if g.get("void"):
                tail = "roofed, unheated" if g["void"].get("roofed") else "open to sky"
            # ∗ — DRAWN at a size the record does not declare. It is NOT part of `dim`,
            # and that is the point: tests/test_drawn_labels.py freezes this line because
            # OQ 55's void disclosure once rode on it, and anything that LENGTHENS the
            # string shrinks the fitted size until the dimension drops out of every narrow
            # room. The mark is drawn beside the string instead, off the same per-character
            # estimate the fitter uses, so the fit is untouched.
            star = "∗" if r["id"] in diverged_ids else ""
            dim = f'{_fmt(min(w,h))} x {_fmt(max(w,h))} · {g["area_sf"]} sf'

            def lay(box_w, box_h):
                tsize = min(6.5, box_w / (0.60 * len(tail))) if tail else 0
                tsize = max(4.6, tsize) if tail else 0
                dsize = min(7.5, box_w / (0.60 * len(dim)))
                want = dsize >= 5.6 and box_h >= 26 + (tsize * 1.5 if tail else 0)
                reserve = (dsize * 1.5 if want else 0) + (tsize * 1.5 if tail else 0)
                fit = _fit_lines(nm, box_w, box_h - reserve, 9.5, 6.0)
                if not fit: return None
                lines, size = fit
                show = want and size >= 7.0
                return lines, size, (dsize if show else None), tsize, \
                    len(lines) * size * 1.2 + (dsize * 1.5 if show else 0) \
                    + (tsize * 1.5 if tail else 0)

            flat = lay(bw, bh)
            # a slot -- a stair, a closet, a hyphen -- takes its name along its length
            turned = lay(bh, bw) if h > w * 1.3 else None
            use = turned if (turned and (not flat or turned[1] > flat[1] * 1.15)) else flat
            if not use: continue
            lines, size, dsize, tsize, block = use
            gx = f'<g transform="rotate(-90 {cx:.1f} {cy:.1f})">' if use is turned else '<g>'
            s.append(gx)
            # NAMED `label_top`, AND THE NAME IS THE WHOLE FIX. This was `top`, which is the
            # SHEET'S TOP MARGIN, computed once at line 183 and read by BOTH `total_h` and, once
            # per level, `oy = top + extra_top`. Reassigning it here meant the FIRST plate was
            # positioned from the real margin and every plate after it from wherever the last
            # room's label block happened to begin. Measured on
            # plans/tidewater-georgian-careful.json: ground plate at y=134, upper plate at
            # y=378.2 -- 244.2 px lower, running to y=658 on a canvas `total_h` had already
            # sized at 498. A third of the upper floor was outside the viewBox and simply not
            # drawn, and the two levels no longer aligned.
            # READ THE COMMENT DIRECTLY BELOW: an inner loop rebinding `i` was found and fixed
            # in this same block, and this rebinding two lines above it was not. Same defect,
            # same eight lines, one of them carrying a paragraph about the other.
            label_top = cy - block/2
            # `li`, NOT `i`: the plate loop at the top of this function is
            # `for i, lv in enumerate(levels)`, and this inner loop REBOUND IT. By the time
            # the relaxation marks are drawn below, `i` was a stale label-LINE index rather
            # than the plate index, so `level_marks[i]` read the wrong level's marks --
            # silently, and only visibly when the two numbers stopped coinciding. Measured
            # on plans/tidewater-georgian-careful.json: the upper plate drew the GROUND
            # level's six marks a second time and neither of its own two, so the sheet
            # carried twelve triangles for eight recorded relaxations. A drawing lying about
            # the record is the whole subject of Phase 6, and this one had been doing it
            # wherever a room's label happened not to wrap to the plate's own index.
            for li, ln in enumerate(lines):
                # style=, not font-size=: a presentation attribute loses to the .nm and
                # .dm rules in the sheet's own <style>, so a fitted size written as an
                # attribute is computed, ignored, and the label overflows anyway
                s.append(f'<text class="nm" x="{cx:.1f}" y="{label_top + (li + 0.72) * size * 1.2:.1f}" '
                         f'style="font-size:{size:.2f}px" text-anchor="middle">{_esc(ln)}</text>')
            below = label_top + len(lines) * size * 1.2
            if dsize:
                s.append(f'<text class="dm" x="{cx:.1f}" y="{below + dsize:.1f}" '
                         f'style="font-size:{dsize:.2f}px" text-anchor="middle">{_esc(dim)}</text>')
                if star:
                    # 0.60 per character is the fitter's own advance estimate, three lines up
                    sx = cx + 0.30 * dsize * len(dim) + 0.30 * dsize
                    s.append(f'<text class="dm" x="{sx:.1f}" y="{below + dsize:.1f}" '
                             f'style="font-size:{dsize:.2f}px;fill:{PAL["copper"]}">{star}</text>')
                below += dsize * 1.5
            elif star:
                # the room is too small to carry its dimension string at all; the mark still
                # belongs on it, because a room drawn off its declaration is exactly the
                # room a reader must not take on trust
                s.append(f'<text class="dm" x="{cx:.1f}" y="{below + 5.0:.1f}" '
                         f'style="font-size:5.00px;fill:{PAL["copper"]}" '
                         f'text-anchor="middle">{star}</text>')
            if tail:
                s.append(f'<text class="dm" x="{cx:.1f}" y="{below + tsize:.1f}" '
                         f'style="font-size:{tsize:.2f}px;fill:{PAL["brass"]}" '
                         f'text-anchor="middle">{_esc(tail)}</text>')
            s.append('</g>')
        # openings -- windows into the run the doors leave, then the doors themselves
        op = level_openings[i]
        for win in op["windows"]:
            ww = win["width_ft"] * scale * 0.9
            wl, p = win["wall"], win["at_ft"]
            if wl in ("S", "N"):
                cx, yy = X(p), Y(0 if wl == "S" else H)
                s.append(f'<line class="win" x1="{cx-ww/2:.1f}" y1="{yy:.1f}" x2="{cx+ww/2:.1f}" y2="{yy:.1f}"/>')
            else:
                cy, xx = Y(p), X(0 if wl == "W" else W)
                s.append(f'<line class="win" x1="{xx:.1f}" y1="{cy-ww/2:.1f}" x2="{xx:.1f}" y2="{cy+ww/2:.1f}"/>')

        def _door(px, py, horiz, width, dtype, swing_positive):
            """One opening drawn as the KIND of opening it is. Until WP-6.1 `type` was read
            by no renderer at all, so a pair of doors and a cased opening were both drawn as
            one enormous hinged leaf with an arc to match -- which is what a reader saw as
            'a massive door' with 'no rhyme or reason' to its size."""
            half = width * scale / 2
            if horiz: s.append(f'<line class="dr" x1="{X(px)-half:.1f}" y1="{Y(py):.1f}" x2="{X(px)+half:.1f}" y2="{Y(py):.1f}"/>')
            else: s.append(f'<line class="dr" x1="{X(px):.1f}" y1="{Y(py)-half:.1f}" x2="{X(px):.1f}" y2="{Y(py)+half:.1f}"/>')
            if horiz: ax0, ay0, bx0, by0 = X(px)-half, Y(py), X(px)+half, Y(py)
            else:     ax0, ay0, bx0, by0 = X(px), Y(py)-half, X(px), Y(py)+half

            def jambs():
                t = 3.0
                for jx, jy in ((ax0, ay0), (bx0, by0)):
                    if horiz: s.append(f'<line x1="{jx:.1f}" y1="{jy-t:.1f}" x2="{jx:.1f}" y2="{jy+t:.1f}" stroke="{PAL["ink3"]}" stroke-width="1"/>')
                    else:     s.append(f'<line x1="{jx-t:.1f}" y1="{jy:.1f}" x2="{jx+t:.1f}" y2="{jy:.1f}" stroke="{PAL["ink3"]}" stroke-width="1"/>')

            def leaf(hx, hy, radius, tox, toy, sweep):
                if horiz: ex, ey = hx, hy + (-radius if swing_positive else radius)
                else:     ex, ey = hx + (radius if swing_positive else -radius), hy
                s.append(f'<path d="M {ex:.1f} {ey:.1f} A {radius:.1f} {radius:.1f} 0 0 {sweep} {tox:.1f} {toy:.1f}" '
                         f'fill="none" stroke="{PAL["ink3"]}" stroke-width="0.6" stroke-dasharray="2 2"/>')
                s.append(f'<line x1="{hx:.1f}" y1="{hy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{PAL["ink3"]}" stroke-width="0.6"/>')

            # sweep flag follows the hinge-to-far-jamb direction, as WP-2.2 established
            sw = (0 if swing_positive else 1) if horiz else (1 if swing_positive else 0)
            if dtype == "double":
                mx, my = (ax0 + bx0) / 2, (ay0 + by0) / 2
                leaf(ax0, ay0, half, mx, my, sw)
                leaf(bx0, by0, half, mx, my, 1 - sw)
            elif dtype in ("cased-opening", "open"):
                jambs()                                    # a lining and no leaf
            elif dtype == "pocket":
                jambs()
                if horiz: s.append(f'<line x1="{ax0-2*half:.1f}" y1="{ay0:.1f}" x2="{ax0:.1f}" y2="{ay0:.1f}" stroke="{PAL["ink3"]}" stroke-width="0.6" stroke-dasharray="3 2"/>')
                else:     s.append(f'<line x1="{ax0:.1f}" y1="{ay0-2*half:.1f}" x2="{ax0:.1f}" y2="{ay0:.1f}" stroke="{PAL["ink3"]}" stroke-width="0.6" stroke-dasharray="3 2"/>')
            elif dtype in ("garage", "bulkhead"):
                jambs()
                dash = ' stroke-dasharray="4 3"' if dtype == "bulkhead" else ''
                s.append(f'<line x1="{ax0:.1f}" y1="{ay0:.1f}" x2="{bx0:.1f}" y2="{by0:.1f}" stroke="{PAL["ink3"]}" stroke-width="1.2"{dash}/>')
            else:
                leaf(ax0, ay0, 2 * half, bx0, by0, sw)

        for d in op["interior"]:
            px, py = (d["pos_ft"], d["at_ft"]) if d["horiz"] else (d["at_ft"], d["pos_ft"])
            _door(px, py, d["horiz"], d["width_ft"], d["type"], d["swing_positive"])
        # exterior doors. This renderer drew NONE of them until WP-6.1 -- it `continue`d on
        # `t == "exterior"` -- so every front and back door in the corpus was missing from
        # every Python-rendered sheet, and the DXF and IFC exports inherited the gap.
        for d in op["exterior"]:
            wl, p = d["wall"], d["at_ft"]
            horiz = wl in ("S", "N")
            px, py = (p, 0.0 if wl == "S" else H) if horiz else (0.0 if wl == "W" else W, p)
            _door(px, py, horiz, d["width_ft"], d["type"], wl in ("S", "W"))

        # WP-6.2 — the stair, drawn from plan["stair"] and from nothing else. There has
        # never been a line of stair-drawing code in this system: a stair hall was an empty
        # rectangle with lettering in it, while rooms/stair-hall.json carried the flight
        # itself as a furniture item ([120, 78] in, "dog-leg with half landing") and
        # build/structure.py computed its risers into a section report no plan ever saw.
        st = plan.get("stair")
        if st and (st.get("level") or 0) == i and st.get("flights"):
            for fl in st["flights"]:
                fx, fy = fl["x_ft"], fl["y_ft"]
                fw, fd = fl["width_ft"], fl["depth_ft"]
                s.append(f'<rect x="{X(fx):.1f}" y="{Y(fy+fd):.1f}" '
                         f'width="{fw*scale:.1f}" height="{fd*scale:.1f}" fill="none" '
                         f'stroke="{PAL["ink3"]}" stroke-width="0.8"/>')
                n = max(1, fl.get("treads") or 1)
                horiz_run = fl["direction"] in ("E", "W")
                for t in range(1, n):
                    if horiz_run:
                        tx = fx + fw * (t / n)
                        s.append(f'<line x1="{X(tx):.1f}" y1="{Y(fy):.1f}" '
                                 f'x2="{X(tx):.1f}" y2="{Y(fy+fd):.1f}" '
                                 f'stroke="{PAL["ink3"]}" stroke-width="0.5"/>')
                    else:
                        ty = fy + fd * (t / n)
                        s.append(f'<line x1="{X(fx):.1f}" y1="{Y(ty):.1f}" '
                                 f'x2="{X(fx+fw):.1f}" y2="{Y(ty):.1f}" '
                                 f'stroke="{PAL["ink3"]}" stroke-width="0.5"/>')
            # the UP arrow, along the first flight, because a stair without a direction is
            # a set of parallel lines
            f0 = st["flights"][0]
            cx0 = X(f0["x_ft"] + f0["width_ft"] / 2)
            cy0 = Y(f0["y_ft"] + f0["depth_ft"] / 2)
            s.append(f'<text class="dm" x="{cx0:.1f}" y="{cy0:.1f}" text-anchor="middle" '
                     f'style="fill:{PAL["brass"]}">UP {st["risers"]}R</text>')
        elif st and (st.get("level") or 0) == i and st.get("unplaced"):
            g0 = st.get("well") or {}
            if g0:
                s.append(f'<text class="dm" x="{X(g0["x_ft"] + g0["width_ft"]/2):.1f}" '
                         f'y="{Y(g0["y_ft"] + g0["depth_ft"]/2) + 10:.1f}" text-anchor="middle" '
                         f'style="fill:{PAL["copper"]}">STAIR NOT DRAWN — SEE RECORD</text>')

        # fixtures, from room["fixture_layout"] and from nothing else
        for r in lv["rooms"]:
            for f in (r.get("fixture_layout") or []):
                if f.get("unplaced") or f.get("x_ft") is None: continue
                s.append(f'<rect x="{X(f["x_ft"]):.1f}" y="{Y(f["y_ft"]+f["depth_ft"]):.1f}" '
                         f'width="{f["width_ft"]*scale:.1f}" height="{f["depth_ft"]*scale:.1f}" '
                         f'fill="none" stroke="{PAL["ink3"]}" stroke-width="0.6" '
                         f'stroke-dasharray="2 2"><title>{_esc(f["item"])}</title></rect>')
        # P7 -- a compromise is counted AND appears on the drawing, at its location (OQ 33).
        # The tally above this level's plate has always been honest; until 26 Aug 2026 the
        # solvers recorded a relaxation as a bare number, so neither this renderer nor the
        # workbench's sheet could say WHERE it applied. Each mark is a cut that missed the
        # structural bay -- a joist run that does not land on a bearing wall -- drawn on the
        # line itself as a hollow triangle in ink, never in colour: colour in this drawing
        # names a material and does not flag a condition.
        #
        # WHERE the mark goes is `relaxation_marks` -- the same rule the workbench's sheet
        # applies through derive.js. A CP mark used to be dropped at the middle of the plan
        # for want of an extent, which put a tick and a triangle inside a room with no wall
        # under either; a mark the solver can locate on no wall of this level is now counted
        # in the banner instead of drawn somewhere plausible.
        drawn_mk, _unlocated_mk = level_marks[i]
        for mk, runs, at_along in drawn_mk:
            vert = mk.get("axis") == "x"
            at = mk.get("at_ft", 0.0)
            for lo, hi in runs:
                if vert:
                    x1 = x2 = X(at); y1, y2 = Y(lo), Y(hi)
                else:
                    y1 = y2 = Y(at); x1, x2 = X(lo), X(hi)
                s.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                         f'stroke="{PAL["ink3"]}" stroke-width="0.7" stroke-dasharray="3 3"/>')
            gx, gy = (X(at), Y(at_along)) if vert else (X(at_along), Y(at))
            s.append(f'<path d="M {gx:.1f} {gy-4.5:.1f} L {gx+4.0:.1f} {gy+3.0:.1f} '
                     f'L {gx-4.0:.1f} {gy+3.0:.1f} Z" fill="{PAL["paper"]}" '
                     f'stroke="{PAL["ink"]}" stroke-width="1"><title>'
                     f'{mk.get("off_ft")} ft off the bay line</title></path>')

        # scale bar
        # and again: `.pt` sets a stroke, so the scale bar was drawn as a partition line
        s.append(f'<line class="pt" x1="{X(0):.1f}" y1="{Y(0)+22:.1f}" x2="{X(10):.1f}" y2="{Y(0)+22:.1f}" style="stroke:{PAL["brass"]}"/>')
        s.append(f'<text class="dm" x="{X(0):.1f}" y="{Y(0)+34:.1f}">10 ft</text>')
        # WP-6.1: the △ has been drawn since OQ 33 and defined only in the banner's running
        # prose. A reader meeting it on the drawing had nothing to read it BY, and reported
        # it as arrows that "seem to point to anything and everything". A symbol a drawing
        # uses is a symbol the drawing defines.
        if (gr.get("relaxations", {}) or {}).get("count"):
            lx, ly = X(0) + 90, Y(0) + 30
            s.append(f'<path d="M {lx:.1f} {ly-4.5:.1f} L {lx+4.0:.1f} {ly+3.0:.1f} '
                     f'L {lx-4.0:.1f} {ly+3.0:.1f} Z" fill="{PAL["paper"]}" '
                     f'stroke="{PAL["ink"]}" stroke-width="1"/>')
            s.append(f'<text class="dm" x="{lx+9:.1f}" y="{ly+3:.1f}">'
                     f'a cut off the bay line — no bearing wall under it</text>')
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
    # WP-11.1 — WHAT THE RECORD ASKED FOR. The plate prints the DRAWN figure, which it must:
    # it is what was drawn. Until this table the declaration it departed from appeared only as
    # a ∗ and a count in the banner, so a reader could not tell a room the placement ruined
    # from a room the author drew small -- and on the shipped Tidewater plan that is 24 of 25
    # rooms. It is a TABLE under the plates rather than a second line inside each room,
    # deliberately: the label fitter reserves space for every line it draws, so a per-room
    # record line would have shrunk names until they dropped out, and a room that loses its
    # name to gain a disclosure has traded one silence for another.
    if all_diverged:
        ty = top + extra_top + ph + extra_bottom + 66
        s.append(f'<text class="lb" x="{pad}" y="{ty:.0f}" style="fill:{PAL["copper"]}">'
                 f'WHAT THE RECORD ASKED FOR — ∗ ROOMS, DRAWN AGAINST DECLARED</text>')
        col_w = max(210.0, (total_w - 2*pad) / 3.0)
        per_col = max(1, -(-len(all_diverged) // max(1, int((total_w - 2*pad) // col_w))))
        for n, d in enumerate(all_diverged):
            cx0 = pad + (n // per_col) * col_w
            cy0 = ty + 15 + (n % per_col) * 11
            g = _decl_pair.get(d["id"])
            asked = f'{_fmt(min(g))} x {_fmt(max(g))}' if g else "—"
            drew = _drawn_pair.get(d["id"])
            got = f'{_fmt(min(drew))} x {_fmt(max(drew))}' if drew else "—"
            # THE ID WHERE THE NAME IS NOT UNIQUE. Two rooms called "Closet" produced two
            # rows a reader could not tell apart -- and one of them was drawn 15 ft long
            # while the other was drawn 14, so the rows differed only in figures nobody
            # could attribute. Same defect class as WP-9.4's two rooms sharing an id, on
            # the surface rather than in the diff guard.
            label = d["name"] if _name_unique.get(d["name"], 0) == 1 \
                else f'{d["name"]} ({d["id"]})'
            s.append(f'<text class="dm" x="{cx0:.1f}" y="{cy0:.1f}">'
                     f'{_esc(label)}: drawn {got}, record {asked} '
                     f'({"+" if d["pct"] > 0 else ""}{d["pct"]:.0f}%)</text>')

    s.append('</svg>')
    open(path, "w").write("\n".join(s))
    return path

# ------------------------------------------------------------------ opening geometry
# WP-6.1. These five numbers and four helpers are the whole of what an opening needs to be
# drawn, and they are duplicated ON PURPOSE in workbench/app/src/sheet/derive.js -- the two
# renderers of one record must not quietly disagree, and until this package they did, about
# exterior doors (this file drew none), about door width (this file hardcoded 3 ft) and
# about door TYPE (neither read it). tests/fixtures/sheet_symbols/*.json is the contract
# they are both held to; a change here that is not made there fails two suites.
JAMB_FT = 0.35              # the reveal either side of a leaf
MIN_SOLID_FT = 1.0          # masonry between two openings on one wall
DEFAULT_DOOR_FT = 3.0
DEFAULT_EXT_DOOR_FT = 3.5

def required_wall_ft(width_ft):
    """A door is the leaf AND its jambs; a wall run shorter than this cannot hold it.

    Replaces a flat 3.2 ft test that refused to DRAW a door the solver would PROVE on
    2 ft, so a closet door held as a fact and appeared in no drawing (OQ 41/63). A closet
    door is genuinely narrower than a parlour's, and now draws at its own width."""
    return width_ft + 2 * JAMB_FT

def _shared_run(a, b, tol=0.4):
    """Where two rooms touch, and over how much run: (at, lo, hi, horiz) or None.
    Whether the run is ENOUGH is the caller's question -- it depends on the door."""
    ax, ay, aw, ah = a["x_ft"], a["y_ft"], a["width_ft"], a["depth_ft"]
    bx, by, bw, bh = b["x_ft"], b["y_ft"], b["width_ft"], b["depth_ft"]
    if abs((ax+aw)-bx) <= tol or abs((bx+bw)-ax) <= tol:
        x = bx if abs((ax+aw)-bx) <= tol else ax
        lo, hi = max(ay, by), min(ay+ah, by+bh)
        if hi > lo: return (x, lo, hi, False)
    if abs((ay+ah)-by) <= tol or abs((by+bh)-ay) <= tol:
        y = by if abs((ay+ah)-by) <= tol else ay
        lo, hi = max(ax, bx), min(ax+aw, bx+bw)
        if hi > lo: return (y, lo, hi, True)
    return None

def _shared(a, b, tol=0.4, need=None, width_ft=None):
    """((px, py), horiz) at the middle of the shared run, or None if it will not hold the
    door. `width_ft` states the leaf so the test is the door's own; `need` overrides the
    run outright. Callers that pass neither keep the historical 3.2 ft floor."""
    if need is None:
        need = required_wall_ft(width_ft) if width_ft else 3.2
    seg = _shared_run(a, b, tol)
    if not seg: return None
    at, lo, hi, horiz = seg
    if hi - lo < need: return None
    return (((lo+hi)/2, at), True) if horiz else ((at, (lo+hi)/2), False)

def _boundary_wall(g, wall, W, H, tol=0.6):
    """The run of a room's edge that lies on the footprint boundary: (wall, lo, hi)."""
    x, y, w, h = g["x_ft"], g["y_ft"], g["width_ft"], g["depth_ft"]
    if wall == "S" and y <= tol: return ("S", x, x + w)
    if wall == "N" and y + h >= H - tol: return ("N", x, x + w)
    if wall == "W" and x <= tol: return ("W", y, y + h)
    if wall == "E" and x + w >= W - tol: return ("E", y, y + h)
    return None

def _free_intervals(lo, hi, blocked):
    free = [(lo, hi)]
    for a, b in blocked:
        nxt = []
        for s, e in free:
            if b <= s or a >= e: nxt.append((s, e)); continue
            if a > s: nxt.append((s, min(a, e)))
            if b < e: nxt.append((max(b, s), e))
        free = nxt
    return [(s, e) for s, e in free if e - s > 1e-6]

def _distribute(free, n, unit_w):
    """k+1 of n+1 spacing -- but over the run the doors have LEFT, not over the whole
    wall. Spacing windows without looking at the doors is how the Tidewater sheet drew a
    window on top of the centre passage's front door and the kitchen's back door."""
    centres = [(s + unit_w/2, e - unit_w/2) for s, e in free]
    centres = [(s, e) for s, e in centres if e - s >= -1e-9]
    if not centres: return []
    total = sum(max(0.0, e - s) for s, e in centres)
    out = []
    for k in range(n):
        t = total * ((k + 1) / (n + 1))
        acc, pos = 0.0, centres[0][0]
        for s, e in centres:
            ln = max(0.0, e - s)
            if t <= acc + ln + 1e-9: pos = s + (t - acc); break
            acc += ln
        out.append(pos)
    kept = []
    for p in out:
        if not kept or p - kept[-1] >= unit_w + MIN_SOLID_FT - 1e-9: kept.append(p)
    return kept

_WALL_AXIS = {"N": "x", "S": "x", "E": "y", "W": "y"}


def _placed_at(d, r, W, H):
    """Where the RECORD says this opening is, if it says. Since plan schema 0.3.0 (WP-6.2)
    build/openings.py writes a wall and a centreline onto every opening it can place, and a
    renderer that reads them is a renderer that draws the plan rather than one that guesses
    a plan of its own. Returns None when the record is silent, and the caller falls back to
    the old invention -- which is what a hand-authored 0.2.0 record still gets."""
    wall, pos = d.get("wall"), d.get("position_ft")
    if wall not in _WALL_AXIS or pos is None:
        return None
    return wall, float(pos)


def derive_openings(rooms, W, H, tol=0.6):
    """Every opening of one level, resolved to where it is drawn -- and every declared
    opening that CANNOT be drawn, with the reason. The second half is the point: a door
    with no drawable shared wall used to be `continue`d over in silence by this renderer
    and by the workbench's, so the Tidewater kitchen's five declared interior doors were
    drawn as none and the sheet said nothing. Only the DXF exporter has ever owned up.

    Where the record carries a placed position (schema 0.3.0), it is READ. Where it does
    not, the position is invented as it always was and `inferred_positions` counts it, so
    the sheet can say which kind of drawing the reader is looking at.

    `rooms` is a list of the level's room records, each carrying `geometry`."""
    idx = {r["id"]: r for r in rooms if r.get("geometry")}
    interior, exterior, undrawable = [], [], []
    inferred_widths = 0
    inferred_positions = 0
    handled = set()
    for r in rooms:
        a = r.get("geometry")
        if not a: continue
        used_walls = set()
        for d in (r.get("doors") or []):
            to = d["to"]
            is_ext = to == "exterior"
            declared_w = d.get("width_ft")
            width = declared_w or (DEFAULT_EXT_DOOR_FT if is_ext else DEFAULT_DOOR_FT)
            if declared_w is None: inferred_widths += 1
            dtype = d.get("type") or "swing"
            # an opening the placement pass could not seat says so in the record, and the
            # drawing repeats it rather than quietly leaving a wall blank
            if d.get("unplaced"):
                key = tuple(sorted((r["id"], to)))
                if not is_ext and key in handled: continue
                if not is_ext: handled.add(key)
                undrawable.append({"from": r["id"], "to": to, "width_ft": width,
                                   "type": dtype, "reason": d["unplaced"]["reason"]})
                continue
            seat_rec = _placed_at(d, r, W, H)
            if is_ext and seat_rec:
                wall, pos = seat_rec
                used_walls.add(wall)
                exterior.append({"room": r["id"], "wall": wall, "width_ft": width,
                                 "type": dtype, "at_ft": round(pos, 3),
                                 "inferred_wall": False,
                                 "inferred_width": declared_w is None})
                continue
            if (not is_ext) and seat_rec:
                key = tuple(sorted((r["id"], to)))
                if key in handled: continue
                handled.add(key)
                if to not in idx:
                    undrawable.append({"from": r["id"], "to": to, "width_ft": width,
                                       "type": dtype,
                                       "reason": "the other room is not placed on this level"})
                    continue
                wall, pos = seat_rec
                horiz = wall in ("N", "S")
                b = idx[to]["geometry"]
                at = (a["y_ft"] + a["depth_ft"]) if wall == "N" else \
                     a["y_ft"] if wall == "S" else \
                     (a["x_ft"] + a["width_ft"]) if wall == "E" else a["x_ft"]
                swing = (b["y_ft"] + b["depth_ft"] / 2) > (a["y_ft"] + a["depth_ft"] / 2) if horiz \
                    else (b["x_ft"] + b["width_ft"] / 2) > (a["x_ft"] + a["width_ft"] / 2)
                interior.append({"pair": list(key), "from": r["id"], "to": to,
                                 "width_ft": width, "type": dtype, "at_ft": at,
                                 "pos_ft": round(pos, 3), "horiz": horiz,
                                 "swing_positive": bool(swing)})
                continue
            inferred_positions += 1
            if is_ext:
                # the record has no field saying WHICH wall an exterior door is on (until
                # WP-6.2), so it is inferred: the first declared exterior wall this
                # placement put on the boundary, and never one already carrying a door
                seat = None
                for wl in (r.get("exterior_walls") or ["S", "N", "W", "E"]):
                    if wl in used_walls: continue
                    seat = _boundary_wall(a, wl, W, H, tol)
                    if seat: break
                if not seat:
                    undrawable.append({"from": r["id"], "to": "exterior", "width_ft": width,
                        "type": dtype,
                        "reason": "no declared exterior wall of this room is on the footprint boundary here"})
                    continue
                wl, lo, hi = seat
                used_walls.add(wl)
                mid = (lo + hi) / 2
                exterior.append({"room": r["id"], "wall": wl, "width_ft": width, "type": dtype,
                                 "at_ft": mid, "inferred_wall": True,
                                 "inferred_width": declared_w is None})
                continue
            key = tuple(sorted((r["id"], to)))
            if key in handled: continue
            handled.add(key)
            if to not in idx:
                undrawable.append({"from": r["id"], "to": to, "width_ft": width, "type": dtype,
                    "reason": "the other room is not placed on this level"})
                continue
            seg = _shared_run(a, idx[to]["geometry"])
            if not seg:
                undrawable.append({"from": r["id"], "to": to, "width_ft": width, "type": dtype,
                    "reason": "the placement leaves these two rooms no shared wall"})
                continue
            at, lo, hi, horiz = seg
            need = required_wall_ft(width)
            if hi - lo < need:
                undrawable.append({"from": r["id"], "to": to, "width_ft": width, "type": dtype,
                    "reason": f"they share {hi-lo:.1f} ft; this leaf and its jambs need {need:.1f} ft"})
                continue
            b = idx[to]["geometry"]
            if horiz:
                swing = (b["y_ft"] + b["depth_ft"]/2) > (a["y_ft"] + a["depth_ft"]/2)
            else:
                swing = (b["x_ft"] + b["width_ft"]/2) > (a["x_ft"] + a["width_ft"]/2)
            interior.append({"pair": list(key), "from": r["id"], "to": to, "width_ft": width,
                             "type": dtype, "at_ft": at, "pos_ft": (lo+hi)/2, "horiz": horiz,
                             "swing_positive": bool(swing)})
    # windows go into what the doors left
    blocked = {}
    for e in exterior:
        blocked.setdefault((e["room"], e["wall"]), []).append(
            (e["at_ft"] - e["width_ft"]/2 - MIN_SOLID_FT, e["at_ft"] + e["width_ft"]/2 + MIN_SOLID_FT))
    windows, off_footprint, crowded = [], 0, 0
    for r in rooms:
        a = r.get("geometry")
        if not a: continue
        for win in (r.get("windows") or []):
            n = win.get("count") or 1
            ww = win.get("width_ft") or 3
            seat = _boundary_wall(a, win.get("wall"), W, H, tol)
            if not seat:
                off_footprint += n
                continue
            wl, lo, hi = seat
            # the record carries one centreline per unit; read them, do not re-space them
            if win.get("positions_ft"):
                pos = [float(p) for p in win["positions_ft"]]
                crowded += max(0, n - len(pos))
            else:
                pos = _distribute(_free_intervals(lo, hi, blocked.get((r["id"], wl), [])), n, ww)
                crowded += n - len(pos)
                inferred_positions += len(pos)
            for p in pos:
                windows.append({"room": r["id"], "wall": wl, "width_ft": ww,
                                "at_ft": round(p, 3)})
    return {"interior": interior, "exterior": exterior, "undrawable": undrawable,
            "windows": windows, "windows_off_footprint": off_footprint,
            "windows_crowded": crowded, "inferred_widths": inferred_widths,
            "inferred_positions": inferred_positions}

# The `.lb` face is monospaced at 8.5px with .14em of letter-spacing, so one character costs
# 8.5*0.60 + 8.5*0.14 px. A banner line longer than the plate is a disclosure the sheet does not
# make: the first WP-11.1 draft ran the undrawn-window line 160 characters and the canvas cut it
# mid-word, which is this repository's oldest class of defect (a mark inside no viewBox) wearing
# the clothes of the package sent to fix it. Wrapping, never truncating -- a disclosure that does
# not fit is still owed.
LB_ADVANCE_PX = 8.5 * (0.60 + 0.14)

def _wrap_banner(text, width_px):
    if width_px <= 0: return [text]
    per_row = max(20, int(width_px // LB_ADVANCE_PX))
    if len(text) <= per_row: return [text]
    rows, line = [], ""
    for word in text.split(" "):
        trial = f"{line} {word}".strip()
        if len(trial) > per_row and line:
            rows.append(line); line = "  " + word     # the continuation is indented, not flush
        else:
            line = trial
    if line: rows.append(line)
    return rows

def declared_divergence(rooms, tol_ft=0.5):
    """Rooms DRAWN at a size their own record does not declare. The sheet prints the placed
    rectangle -- it must, it is what was drawn -- and said nothing about the declaration it
    departed from, so a kitchen declared 16 x 20 and placed at 63% of that area read as a
    measurement of the declared room (OQ 54's silence, on the drawing rather than in the
    report)."""
    out = []
    for r in rooms:
        g = r.get("geometry")
        dw, dl = r.get("width_ft"), r.get("length_ft")
        if not g or not dw or not dl: continue
        short, lng = min(g["width_ft"], g["depth_ft"]), max(g["width_ft"], g["depth_ft"])
        dshort, dlng = min(dw, dl), max(dw, dl)
        if abs(short - dshort) <= tol_ft and abs(lng - dlng) <= tol_ft: continue
        da, pa = dw * dl, g["width_ft"] * g["depth_ft"]
        out.append({"id": r["id"], "name": r.get("name") or r["id"], "declared_sf": da,
                    "placed_sf": pa, "pct": ((pa - da) / da * 100) if da else 0.0})
    out.sort(key=lambda d: -abs(d["pct"]))
    return out

def relaxation_marks(marks, level_index, W, H):
    """Where a relaxation mark may be drawn -- and where it may not.

    A relaxation is one wall line that missed the structural bay. The heuristic records the
    cut it made, so its mark carries a from/to extent. The CP engine records only the line,
    and both renderers used to draw such a mark as a 5 ft tick CENTRED ON THE PLAN: on the
    Tidewater placement that put a dashed tick and a triangle inside the drawing room with
    no wall under either. Those are the "arrows over walls between spaces … they seem to
    point to anything and everything" of Lucas's review -- the mark was not over a wall.

    `runs` (geometry_cp.py) is the measured answer: the room faces that actually lie on that
    line, as disjoint intervals. A mark with runs is drawn along them, with the triangle on
    the longest. A mark with neither extent nor runs is returned in the second list and
    NOT drawn -- picking a plausible spot for it would be the same error in a smaller place.

    Kept in lockstep with `relaxationMarks` in workbench/app/src/sheet/derive.js.
    Returns ([(mark, [(lo, hi), ...], at_along), ...], [unlocated marks]).
    """
    drawn, unlocated = [], []
    for mk in (marks or []):
        if (mk.get("level") or 0) != level_index:
            continue
        if mk.get("from_ft") is not None and mk.get("to_ft") is not None:
            runs = [(mk["from_ft"], mk["to_ft"])]
        elif mk.get("runs"):
            runs = [tuple(r) for r in mk["runs"]]
        else:
            unlocated.append(mk); continue
        span = H if mk.get("axis") == "x" else W
        clipped = [(max(0.0, min(a, b)), min(span, max(a, b))) for a, b in runs]
        clipped = [(a, b) for a, b in clipped if b - a > 0.05]
        if not clipped:
            unlocated.append(mk); continue
        lo, hi = max(clipped, key=lambda r: r[1] - r[0])
        drawn.append((mk, clipped, (lo + hi) / 2.0))
    return drawn, unlocated


def _esc(t): return (t or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
