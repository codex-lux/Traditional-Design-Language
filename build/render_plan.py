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

SS = _mod("sheet_style", f"{ROOT}/build/sheet_style.py")

# The palette is build/sheet_style.py's now -- ONE spelling, not four. It carried a verbatim
# copy of the same ten-key dict, under a comment saying the duplication was the price of every
# build/*.py module being loadable standalone; modcache.load answers that, and the copies were
# the reason a colour could be changed in one renderer and not in its neighbours. `DARK` is
# byte-for-byte what stood here, proved over all ten sheets corpus.drawing() produces.
PAL = SS.DARK
FILL = SS.DARK_FILL

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
# THE ADVANCE WIDTHS OF THE FACE THIS SHEET IS ACTUALLY SET IN (WP-11.5). The table below
# is the estimate that stood while the sheet carried no font -- five branches, one number
# for every capital -- and it is kept, because a tree with no committed asset still has to
# fit a label. `sheet_style.advance_widths()` is the measured alternative, read off the
# subset's own `hmtx`, and the difference is not decorative: EB Garamond's `I` is 0.34 em
# where the estimate says 0.28, its `W` 0.916 where the estimate says 0.86, and its `.` 0.23
# where the estimate says 0.28. `workbench/app/src/sheet/label.js` has measured the real
# glyphs in a canvas since WP-5.2; this is the Python side finally doing the same thing.
_WIDTHS = None


def _widths():
    global _WIDTHS
    if _WIDTHS is None:
        _WIDTHS = SS.advance_widths() or {}
    return _WIDTHS


def _adv(ch):
    w = _widths().get(ch)
    if w is not None:
        return w
    if ch in "iljI.,:;'|!": return 0.28
    if ch in "ft()[]r ": return 0.36
    if ch in "mwMW": return 0.86
    if ch.isupper() or ch.isdigit(): return 0.66
    return 0.53

# THE STANDARD'S OWN `--tr-room`, AND IT HAS TO ENTER THE FIT. Room names are set in
# letterspaced roman capitals -- `.3em` between every pair of letters -- which on a
# twelve-character name is three and a half more ems of width than the glyphs themselves.
# A fitter blind to it computes a size for a label a third narrower than the one it draws,
# which is the label-through-the-wall defect of 26 Aug 2026 arriving by a new road.
ROOM_TRACK = 0.30


def _text_w(text, size, mono=False, track=0.0):
    glyphs = 0.60 * len(text) if mono else sum(_adv(c) for c in text)
    # SVG puts the spacing after the LAST glyph too, which is why the caller nudges a
    # centred label right by half a track; the width it occupies is len(text) tracks.
    return size * (glyphs + track * len(text))

def _balance(words, n, track=0.0):
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
            widest = max(_text_w(l, 1.0, track=track) for l in lines)
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

def _fit_lines(text, max_w, max_h, preferred, floor, lead=1.2, max_lines=3, track=0.0):
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
        lines = _balance(words, n, track)
        if not lines: continue
        widest = max(_text_w(l, 1.0, track=track) for l in lines)
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

# ---------------------------------------------------------------- the wall as a body
# WHAT CHANGED AND WHY. Until this package every wall on this sheet was a single stroke --
# `.wl` at 2.2 px for a room outline, 1 px for a partition -- and the word "thickness" did not
# appear in this file. A plan drawn that way has no figure-ground, so the reader was given room
# fills to tell rooms apart instead: seven washes keyed on what a room is FOR. That is a
# classification, not a drawing, and Graphic Standard No. 1 forbids it in as many words --
# "Duties are exclusive ... Color names things; it never outlines them."
#
# NOTHING HERE IS INVENTED. build/structure.py has computed all three thicknesses since WP-3.1
# and no drawing had ever read one: `wall_thickness(plan)` reads the plan's own
# `declared.construction_type` against construction/wall-assemblies.json (the Tidewater house
# declares `solid-masonry-two-wythe`, so 15.5 / 11.0 / 4.5 in), and `wall_lines()` +
# `bearing_lines()` return every segment on a level already tagged exterior, bearing or
# partition with its reason in its own `why`. So the sheet can now say which walls CARRY --
# a fact the record has held since WP-3.1 and no plate has ever shown.
#
# THE ROOMS ARE CLEAR EXTENTS AND THE PLACEMENT CARRIES NO WALL BANDS. `geometry.py` tiles the
# footprint exactly -- 2,405 sf of programme in a 2,405 sf block, the rooms covering 97.6% of
# it -- so the placement leaves no room for a wall to stand in. The exterior band is therefore
# drawn OUTWARD from the block, which is what `structure.outside_to_outside_footprint()`
# already means by "rooms keep clear dimensions while the footprint becomes outside-to-
# outside"; an interior band is drawn CENTRED on the shared line, taking half its thickness
# from each of the two rooms. A room's stated figure stays the record's and is NOT adjusted to
# match: the drawing shows a wall the placement does not allow for, and the sheet's own
# schedule says so rather than the label quietly changing under the reader. That is
# `oq/the-placement-carries-no-wall-bands`, and it belongs to the geometry layer.

def _wall_axis(wall, W, H):
    """structure.wall_lines()'s convention: "x" is a VERTICAL wall (constant x), "y" a
    horizontal one. Getting this backwards plants a wall's position into the other axis's
    list, which is the silent-span bug that file's own comment records."""
    if wall == "S": return ("y", 0.0)
    if wall == "N": return ("y", H)
    if wall == "W": return ("x", 0.0)
    return ("x", W)


def opening_gaps(op, W, H):
    """Every opening on this level as (axis, position_ft, lo_ft, hi_ft).

    A wall is a body now, so an opening is a HOLE in it and not a mark laid over a line. The
    spans come from `derive_openings` -- the same call the leaves and sills are drawn from, so
    a gap and the door that sits in it cannot disagree about where the opening is. That was
    the whole of WP-6.1's finding one level up: two passes that never looked at each other put
    a window and a door on the same coordinate."""
    gaps = []
    for d in op["interior"]:
        half = d["width_ft"] / 2.0
        gaps.append(("y" if d["horiz"] else "x", d["at_ft"], d["pos_ft"] - half, d["pos_ft"] + half))
    for d in op["exterior"]:
        axis, pos = _wall_axis(d["wall"], W, H)
        half = d["width_ft"] / 2.0
        gaps.append((axis, pos, d["at_ft"] - half, d["at_ft"] + half))
    for win in op["windows"]:
        axis, pos = _wall_axis(win["wall"], W, H)
        half = win["width_ft"] / 2.0
        gaps.append((axis, pos, win["at_ft"] - half, win["at_ft"] + half))
    return gaps


def _runs(lo, hi, cuts, tol=0.02):
    """[lo, hi] with every cut taken out of it, in order. The complement, and nothing else."""
    cuts = sorted((max(lo, a), min(hi, b)) for a, b in cuts if b > lo + tol and a < hi - tol)
    out, cursor = [], lo
    for a, b in cuts:
        if a > cursor + tol: out.append((cursor, a))
        cursor = max(cursor, b)
    if hi > cursor + tol: out.append((cursor, hi))
    return out


# How near an opening's own wall position has to be to a wall line before the two are taken to
# be the same wall. `derive_openings` and `structure.wall_lines` compute a shared edge by two
# independent copies of one rule (structure.py's `_shared_segment` says so in its own
# docstring), each rounding to two places, so they agree to well inside this. It is a
# tolerance and not a search: a door 4 inches from a wall belongs to that wall; one 4 feet
# away belongs to no wall and is counted, not guessed at -- the same discipline
# `relaxation_marks` applies to a mark it cannot place.
GAP_TOL_FT = 0.35


def wall_bands(level_rooms, blocks, W, H, bay_module_ft, wall, gaps):
    """Every wall on one level as a body: a rectangle, a thickness, an ink, openings cut out.

    THE EXTERIOR RING IS PER MASSING ELEMENT, not from `wall_lines`'s four boundary entries.
    Those four describe the MAIN BLOCK, and a house with a dependency has a second envelope of
    its own; drawing the main block's ring round a two-element house is the error
    `geometry_report.multi_element` exists to disclose, one layer further down. Interior
    segments still come from `wall_lines`, which sees every placed room whatever element it
    sits in.

    Returns {kind, x_ft, y_ft, width_ft, depth_ft, bearing, why} in model coordinates, plus a
    tally of the openings that matched no wall line, which the caller discloses."""
    ST = _structure()
    ext = wall["exterior_in"] / 12.0
    bear = wall["bearing_interior_in"] / 12.0
    part = wall["partition_in"] / 12.0
    bands, matched = [], set()

    def band(axis, face, centre, lo, hi, t, kind, why, bearing, block=None):
        """One wall line, cut into its solid runs. `face` is where the openings are measured
        (the room's own edge); `centre` is where the body's middle sits, which is the same
        thing for an interior wall and half a thickness outboard for an envelope."""
        mine = [(i, g) for i, g in enumerate(gaps)
                if g[0] == axis and abs(g[1] - face) <= GAP_TOL_FT]
        matched.update(i for i, _g in mine)
        for a, b in _runs(lo, hi, [(g[2], g[3]) for _i, g in mine]):
            # `wall` names WHICH of the three the assembly states, and `t_ft` carries the
            # thickness explicitly. A reader cannot recover either from the rectangle: a pier
            # between two windows is a run SHORTER than the wall is thick, so the short side of
            # the rectangle is its length and not its thickness. Found by the guard that was
            # written to check the thicknesses, on the first run.
            w_name = "exterior" if why == "exterior envelope" else (
                "court" if kind == "masonry" and bearing and why.startswith("faces") else
                ("bearing" if bearing else "partition"))
            if axis == "x":
                bands.append({"kind": kind, "wall": w_name, "t_ft": t,
                              "x_ft": centre - t / 2, "y_ft": a, "width_ft": t,
                              "depth_ft": b - a, "bearing": bearing, "why": why, "block": block})
            else:
                bands.append({"kind": kind, "wall": w_name, "t_ft": t,
                              "x_ft": a, "y_ft": centre - t / 2, "width_ft": b - a,
                              "depth_ft": t, "bearing": bearing, "why": why, "block": block})

    for bi, (bx, by, bw, bh) in enumerate(blocks):
        # S and N run the full OUTER width so the four bands meet at the corners; W and E run
        # only the block's own depth, or each corner would be drawn twice and the cut line
        # struck through its own return. Each carries its element's index, so a reader -- and
        # the guard that this is one envelope PER ELEMENT and not one rectangle across the
        # hyphen gap -- can tell which envelope a band belongs to without deriving a scale.
        band("y", by, by - ext / 2, bx - ext, bx + bw + ext, ext, "masonry", "exterior envelope", True, bi)
        band("y", by + bh, by + bh + ext / 2, bx - ext, bx + bw + ext, ext, "masonry", "exterior envelope", True, bi)
        band("x", bx, bx - ext / 2, by, by + bh, ext, "masonry", "exterior envelope", True, bi)
        band("x", bx + bw, bx + bw + ext / 2, by, by + bh, ext, "masonry", "exterior envelope", True, bi)

    for w in ST.bearing_lines(ST.wall_lines(level_rooms, W, H), bay_module_ft or 10.0):
        if w["role"] == "exterior":
            # the four boundary entries are the ring above, per element. A COURT wall is not:
            # OQ 55 made a wall facing an unroofed void an exterior wall, weather-facing and
            # bearing, and it is an interior LINE of the block -- so it is drawn centred, at
            # the envelope's own thickness, which is what being on the envelope means.
            if w.get("wall") != "court":
                continue
            band(w["axis"], w["position_ft"], w["position_ft"], w["lo_ft"], w["hi_ft"], ext,
                 "masonry", w.get("why") or "faces a court", True)
            continue
        t = bear if w.get("bearing") else part
        band(w["axis"], w["position_ft"], w["position_ft"], w["lo_ft"], w["hi_ft"], t,
             "masonry" if w.get("bearing") else "partition", w.get("why") or "", bool(w.get("bearing")))

    _trim_junctions(bands)
    return bands, [g for i, g in enumerate(gaps) if i not in matched]


def _trim_junctions(bands, tol=0.30):
    """A wall runs to the FACE of the wall it meets, not through it.

    Each interior segment comes out of `wall_lines` running to the shared room edge, which is
    the CENTRE of the wall it butts into -- so its end cap was drawn half a thickness inside
    the other wall's body, as a dark nub across an otherwise continuous face. Real poche
    interlocks and shows no such mark. Trimming the end back to the face is the honest fix and
    the cheap one: it does not move a wall, it stops drawing a line inside another wall's body.

    Cheap in the other sense too -- this is O(n^2) over the ~30 wall segments of a level."""
    vert = [b for b in bands if b["depth_ft"] > b["width_ft"]]
    horiz = [b for b in bands if b["width_ft"] >= b["depth_ft"]]
    for a_, cross in ((vert, horiz), (horiz, vert)):
        for b in a_:
            along_lo = b["y_ft"] if b in vert else b["x_ft"]
            along_hi = along_lo + (b["depth_ft"] if b in vert else b["width_ft"])
            across = (b["x_ft"] + b["width_ft"] / 2) if b in vert else (b["y_ft"] + b["depth_ft"] / 2)
            for c in cross:
                c_lo = c["x_ft"] if b in vert else c["y_ft"]
                c_hi = c_lo + (c["width_ft"] if b in vert else c["depth_ft"])
                if not (c_lo - tol <= across <= c_hi + tol):
                    continue                      # they do not cross at all
                c_mid = (c["y_ft"] + c["depth_ft"] / 2) if b in vert else (c["x_ft"] + c["width_ft"] / 2)
                c_t = c["depth_ft"] if b in vert else c["width_ft"]
                if abs(along_lo - c_mid) <= tol:
                    along_lo = c_mid + c_t / 2
                if abs(along_hi - c_mid) <= tol:
                    along_hi = c_mid - c_t / 2
            if along_hi - along_lo <= 0.01:
                continue                          # a run shorter than the walls it joins: leave it
            if b in vert:
                b["y_ft"], b["depth_ft"] = along_lo, along_hi - along_lo
            else:
                b["x_ft"], b["width_ft"] = along_lo, along_hi - along_lo


# ---------------------------------------------------------------- the sheet
# TWO REGISTERS, RULED BY LUCAS 4 SEP 2026. A presentation sheet carries the drawing and the
# names; a working sheet adds the dimension strings, the divergence marks and the relaxation
# triangles on the field. Both come out of this one function and the title block says which,
# because a printed plate leaves its page prose behind -- the same argument WP-6.4 made for
# naming the ENGINE on the plate rather than beside it.
#
# THE DEFAULT IS `working`, WHICH IS THE CONSERVATIVE DIRECTION AND NOT AN OVERSIGHT. Every
# caller that does not choose gets every disclosure it got before, so no count and no mark can
# go missing because nobody said the word: `tests/test_measurement_honesty.py` counts one
# triangle per relaxation off a bare `render(out, path)`, and a sheet that silently dropped
# them when nobody chose would be WP-6.1's failure ("the drawing lying about the record")
# arriving through a default argument. The workbench asks for `presentation` explicitly,
# because that is the surface a person reads.
REGISTERS = ("presentation", "working")

# The plan scale. 13 px per foot is Graphic Standard No. 1's own `--px-per-ft`, and it is the
# smallest scale at which this sheet's grammar survives: at the previous 7 a 4.5 in partition
# is 2.6 px of body between two 3 px cut lines, so the poche this package exists to draw would
# have been more ink than wall. At 13 the partition is 4.9 px, the bearing wall 11.9 and the
# envelope 16.8, which is the ladder a reader is meant to see.
PX_PER_FT = 13.0


# The wall assembly comes from build/assemblies.py, a LEAF, and the wall LINES from
# build/structure.py, which is not one -- it loads plan_check.py and geometry.py at module
# level and geometry.py loads this file inside its own CLI. So the assembly (which every
# render needs) is a cheap leaf read and the segments (which only a placed level needs) are
# fetched lazily, and a renderer is never in the import path of the solver that calls it.
ASSEMBLIES = _mod("assemblies", f"{ROOT}/build/assemblies.py")


def _structure():
    """build/structure.py, lazily -- for `wall_lines`/`bearing_lines` only."""
    return _mod("structure", f"{ROOT}/build/structure.py")


def _style_block(register):
    """The sheet's own <style>, in Graphic Standard No. 1.

    EVERY PROPERTY SET HERE MUST NOT BE SET AS AN ATTRIBUTE ON ANY ELEMENT CARRYING THE CLASS.
    `tests/test_drawn_labels.py::test_no_class_rule_silently_beats_a_presentation_attribute`
    asserts the general form, because a computed value written as a presentation attribute
    loses to a class rule in the same document and is computed, discarded and never seen --
    five sites in this file were found that way. So a class carries what never varies and
    `style=` carries what does."""
    L, W_, T = SS.LIGHT, SS.LW, SS.TRACK
    return (
        f'<style>'
        # WP-11.5. The face itself, subset and carried, before anything that asks for it.
        # Empty where no asset is committed, and the margin schedule then says the sheet is
        # set in whatever the reader's machine has.
        f'{SS.font_face_rule()}'
        f'text{{font-family:{SS.FACE};fill:{L["ink2"]}}}'
        # the letter: one voice, roman capitals, spaced. "Emphasis is achieved by spacing and
        # size, as on a carved frieze."
        f'.nm{{font-size:11px;fill:{L["ink"]};letter-spacing:{T["room"]}}}'
        f'.dm{{font-size:8px;fill:{L["ink2"]};font-family:{SS.MONO}}}'
        f'.hd{{font-size:21px;fill:{L["ink"]};letter-spacing:{T["drawing"]}}}'
        f'.lb{{font-family:{SS.MONO};font-size:8.5px;letter-spacing:{T["caps"]};fill:{L["ink2"]}}}'
        # the wall as a body: coal skin, salmon flesh. The rect's own outline IS the two wall
        # faces and, at the end of a run, the jamb return into the opening -- so a gap cut in
        # a band returns itself and nothing has to draw a return separately.
        f'.pm{{fill:{SS.POCHE["masonry"]};stroke:{L["coal"]};stroke-width:{W_["cut"]};stroke-linejoin:miter}}'
        f'.pp{{fill:{SS.POCHE["partition"]};stroke:{L["coal"]};stroke-width:{W_["cut"]};stroke-linejoin:miter}}'
        # openings
        f'.sill{{stroke:{L["ink"]};stroke-width:{W_["medium"]};fill:none}}'
        f'.win{{stroke:{L["ink2"]};stroke-width:{W_["fine"]};fill:none}}'
        f'.dr{{stroke:{L["ink"]};stroke-width:{W_["medium"]};fill:none}}'
        f'.sw{{stroke:{L["hair"]};stroke-width:{W_["construction"]};fill:none}}'
        # the fine pen: fixtures, treads, hatching
        f'.fn{{stroke:{L["ink2"]};stroke-width:{W_["fine"]};fill:none}}'
             f'.fu{{stroke:{L["ink2"]};stroke-width:{W_["fine"]};fill:none}}'
        # construction: the bay grid and its extensions, left visible
        f'.gd{{stroke:{L["hair"]};stroke-width:{W_["construction"]};fill:none}}'
        # the sheet as an object
        f'.bd{{stroke:{L["rule"]};stroke-width:1;fill:none}}'
        f'.mk{{fill:{L["paper"]};stroke:{L["ink"]};stroke-width:{W_["fine"]}}}'
        # WP-11.4. The stoop is masonry and the stack is masonry, so both take the wall's own
        # body -- the same poché and the same cut line, because they are the same trade and
        # the reader must not have to learn a second convention for a second brick.
        f'.st{{fill:{SS.POCHE["masonry"]};stroke:{L["coal"]};stroke-width:{W_["cut"]};stroke-linejoin:miter}}'
        f'.ns{{stroke:{L["ink"]};stroke-width:{W_["medium"]};fill:none}}'
        # WP-11.10. An at-grade appendage is a FLOOR and not a mass: the paper is the terrace,
        # exactly as the paper is every room, and its edge is drawn in the fine pen rather
        # than as a cut. Giving it the wall's body would say the house is that shape, which is
        # the one thing `rooms/terrace.json`'s own note is at pains to deny.
        f'.ap{{stroke:{L["ink2"]};stroke-width:{W_["fine"]};fill:none}}'
        f'</style>')


def appendage_rects(plan):
    """Every rectangle WP-11.10 puts outside the block, in the `room.geometry` shape.

    An at-grade appendage is NOT a massing element and takes no rectangle in the footprint,
    so it reaches the plate through this list and through nothing else -- `lv["rooms"]` has
    no geometry for it and must not grow any. Read from `plan["appendages"]`, which
    `build/appendages.py` wrote; derived here from nothing."""
    return [dict(a["rect"], area_sf=round(a["rect"]["width_ft"] * a["rect"]["depth_ft"]))
            for a in ((plan.get("appendages") or {}).get("placed") or [])]


def threshold_rects(plan):
    """Every rectangle WP-11.4 puts outside the block, in the `room.geometry` shape, so the
    plate's own extent code can hold them without knowing what they are. Read from the record
    and derived from nothing: build/threshold.py placed them and this file draws them."""
    out = appendage_rects(plan)
    th = plan.get("threshold") or {}
    for st in (th.get("steps") or []):
        for k in ("platform", "flight"):
            if st.get(k):
                out.append(st[k])
    for sk in ((plan.get("hearths") or {}).get("stacks") or []):
        out.append(sk)
    return out


def render(plan, path, scale=PX_PER_FT, register="working"):
    if register not in REGISTERS:
        raise SystemExit(f"register must be one of {REGISTERS}, not {register!r}")
    working = register == "working"
    L = SS.LIGHT
    levels = [lv for lv in plan["levels"] if any("geometry" in r for r in lv["rooms"])]
    if not levels: raise SystemExit("no geometry on this plan — run build/geometry.py first")
    fp = plan.get("footprint", {})
    W, H = fp.get("width_ft", 40), fp.get("depth_ft", 30)

    # The wall assembly this house is built of, from its own declared construction_type. A
    # plan that declares none gets platform-frame WITH A NOTE saying so -- structure.py's
    # `wall_thickness` refuses to pick a number silently, and the note is printed in the
    # schedule rather than swallowed here.
    wall = ASSEMBLIES.wall_thickness(plan)
    ext_ft = wall["exterior_in"] / 12.0

    # THE DRAWN EXTENT IS NOT THE MAIN BLOCK'S (OQ 40, 3 Sep 2026). `W` and `H` are the main
    # block, and they must stay that: `derive_openings` below reads them to decide which walls
    # are exterior, and widening them there would put windows on interior walls. But the SHEET
    # has to hold every element, and a house with a dependency has rooms outside the main
    # rectangle -- west of it at negative x, or east of it beyond `width_ft`. It also has to
    # hold the exterior wall, which is drawn OUTSIDE the block it wraps: without the `ext_ft`
    # margin below, the envelope's own outer face is off the plate.
    _pts = [r["geometry"] for lv in plan["levels"] for r in lv["rooms"] if r.get("geometry")]
    # ...AND IT IS NOT THE ROOMS' EITHER, SINCE WP-11.4. The stoop stands outside the entrance
    # wall and an exterior stack outside its gable end -- both at negative coordinates or past
    # `width_ft` -- and a plate sized to the rooms would have cut them off the sheet without
    # any error anywhere. `tests/test_sheet_canvas.py` is the guard that would have caught it,
    # and this is what keeps it green.
    _pts = _pts + threshold_rects(plan)
    draw_x0 = min([g["x_ft"] for g in _pts] + [0.0]) - ext_ft if _pts else -ext_ft
    draw_y0 = min([g["y_ft"] for g in _pts] + [0.0]) - ext_ft if _pts else -ext_ft
    draw_W = (max([g["x_ft"] + g["width_ft"] for g in _pts] + [W]) if _pts else W) + ext_ft - draw_x0
    draw_H = (max([g["y_ft"] + g["depth_ft"] for g in _pts] + [H]) if _pts else H) + ext_ft - draw_y0

    # WP-11.10. The appendages, keyed by the level they stand on, so a placed terrace door is
    # drawn instead of being reported undrawable. Keyed on the level's own `index` and not on
    # its position in `levels`, which is FILTERED to the levels carrying geometry.
    _apx = {}
    for _a in ((plan.get("appendages") or {}).get("placed") or []):
        _apx.setdefault(_a.get("level", 0), {})[_a["room"]] = _a["rect"]
    # WP-11.14: each level's rooms over their OWN massing elements -- `elements.bounds_index`,
    # the same reader `openings.py` has used since WP-11.9. A room in no element is ABSENT from
    # the map and `_boundary_wall` then falls back to the footprint, which is the answer a
    # one-rectangle house wants and the one every shipped plan gets.
    _EL = _mod("elements", f"{ROOT}/build/elements.py")
    level_openings = [derive_openings(lv["rooms"], W, H,
                                      appendages=_apx.get(lv.get("index", i)),
                                      bounds=_EL.bounds_index(plan, lv["rooms"]))
                      for i, lv in enumerate(levels)]
    all_undrawable = [u for op in level_openings for u in op["undrawable"]]
    all_diverged = [d for lv in levels for d in declared_divergence(lv["rooms"])]
    all_diverged.sort(key=lambda d: -abs(d["pct"]))
    diverged_ids = {d["id"] for d in all_diverged}
    _rx_all = (plan.get("geometry_report", {}).get("relaxations", {}) or {}).get("marks", [])
    level_marks = [relaxation_marks(_rx_all, i, W, H) for i in range(len(levels))]
    all_unlocated = [m for _d, un in level_marks for m in un]

    blocks = [(b["x_ft"], b["y_ft"], b["width_ft"], b["depth_ft"]) for b in (fp.get("blocks") or [])] \
        or [(0.0, 0.0, W, H)]
    # AN ELEMENT WITH NO ROOMS ON THIS LEVEL GETS NO ENVELOPE ON THIS LEVEL (WP-11.9). The
    # renderer drew every element's ring on every plate, so a house with a ground-floor
    # dependency had a 30 ft poche rectangle enclosing nothing on its UPPER plate -- an envelope
    # around no rooms, which says the house has a storey it does not have. Found by rendering a
    # tagged record and LOOKING at it, after the same defect had been fixed in
    # `structure.build_section` and `export_ifc` the same afternoon; the renderer is the third
    # place it lived and the only one no count would have caught. On a one-rectangle house every
    # room is in element zero and this is the single ring, as before.
    def _blocks_here(rooms):
        if len(blocks) < 2:
            return blocks
        here = [b for b in blocks
                if any((r.get("geometry") or {}) and
                       r["geometry"]["x_ft"] >= b[0] - 0.5 and
                       r["geometry"]["y_ft"] >= b[1] - 0.5 and
                       r["geometry"]["x_ft"] + r["geometry"]["width_ft"] <= b[0] + b[2] + 0.5 and
                       r["geometry"]["y_ft"] + r["geometry"]["depth_ft"] <= b[1] + b[3] + 0.5
                       for r in rooms)]
        return here or blocks
    level_bands, all_stray = [], []
    for i, lv in enumerate(levels):
        gaps = opening_gaps(level_openings[i], W, H)
        bands, stray = wall_bands(lv["rooms"], _blocks_here(lv["rooms"]), W, H,
                                  fp.get("bay_module_ft"), wall, gaps)
        level_bands.append(bands)
        all_stray.extend(stray)

    # ------------------------------------------------------------- the schedule
    # THE DIAGNOSTICS LEAVE THE DRAWING FIELD AND NOT THE SHEET. Until this package six lines
    # of disclosure were set across the top of the plate, in the drawing's own space, and the
    # relaxation legend sat inside it. They are exactly the lines P7 requires ("a compromise is
    # counted AND appears on the drawing, at its location") and none of them is dropped -- they
    # are set in the title block below the border, in the typewritten margin, where a
    # draughtsman puts a note. The MARKS stay on the field, at their locations, in the working
    # register.
    gr = plan.get("geometry_report", {})
    _solver = gr.get("solver") or {}
    schedule = []
    if gr:
        rl = gr.get("relaxations", {})
        schedule.append((L["salmon_deep"] if rl.get("count") else L["green_deep"],
                         f'{rl.get("count", 0)} CUT(S) OFF THE BAY LINE'
                         + (f", WORST {rl.get('max_off_grid_ft')} FT" if rl.get("count") else "")))
        inf = gr.get("infeasible")
        if inf:
            schedule.append((L["brick"], f'INFEASIBLE AS DECLARED — {len(inf.get("conflicts", []))} '
                             f'CONFLICT(S) PROVEN; THIS DRAWING IS THE LEAST-BAD RELAXATION '
                             f'(SEE GEOMETRY_REPORT.INFEASIBLE)'))
        # WP-11.12 (OQ 98's reporting half). `structure.py` has measured the clear span since
        # WP-3.1 and the search has CHARGED it since WP-7.4, and no plate had ever printed it:
        # the Tidewater upper floor is drawn with a 60 ft run and no bearing line in it. The
        # count is a FLOOR and the line says so, because `span_check` credits a bearing wall
        # across the whole plate however short it runs (OQ 98's measurement half, unruled).
        _sp = gr.get("span_capacity") or {}
        if _sp.get("over_capacity") is None:
            schedule.append((L["salmon_deep"], "CLEAR SPAN NOT EVALUATED — THE CONSTRUCTION "
                             "CATALOGUE COULD NOT BE READ; NO SPAN IS CLAIMED CLEAR"))
        elif _sp.get("over_capacity"):
            schedule.append((L["brick"], f'{_sp["over_capacity"]} CLEAR SPAN(S) OVER THE FRAMING '
                             f'CAPACITY, WORST {_sp.get("worst_span_ft", 0):g} FT — AT LEAST '
                             f'THAT MANY: A BEARING LINE IS CREDITED ACROSS THE WHOLE PLATE '
                             f'HOWEVER SHORT THE WALL RUNS'))
        elif _sp:
            # the zero is printed, and with the same caveat, because "no span exceeds capacity"
            # is exactly the claim the credited-across-the-plate reading can make falsely
            schedule.append((L["green_deep"], "0 CLEAR SPAN(S) OVER THE FRAMING CAPACITY — "
                             "AT LEAST NONE FOUND: A BEARING LINE IS CREDITED ACROSS THE WHOLE "
                             "PLATE HOWEVER SHORT THE WALL RUNS"))
    if all_undrawable:
        names = ", ".join(f'{u["from"]}–{u["to"]}' for u in all_undrawable[:6])
        more = f" (+{len(all_undrawable)-6} MORE)" if len(all_undrawable) > 6 else ""
        schedule.append((L["brick"], f'{len(all_undrawable)} DECLARED DOOR(S) WITHOUT A DRAWABLE '
                         f'OPENING — IN THE RECORD, NOT THE LINEWORK: {names.upper()}{more}'))
    if all_diverged:
        w0 = all_diverged[0]
        mark = ", MARKED ∗" if working else ""
        schedule.append((L["salmon_deep"], f'{len(all_diverged)} ROOM(S) DRAWN AT A SIZE THE '
                         f'RECORD DOES NOT DECLARE{mark} — WORST {(w0["name"] or "").upper()} '
                         f'{"+" if w0["pct"] > 0 else ""}{w0["pct"]:.0f}% BY AREA'))
    if _solver.get("engine") == "cp-sat":
        schedule.append((L["green_deep"], "PLACEMENT PROVED (CP-SAT) AGAINST THE RECORD'S DECLARED FACTS"))
    elif _solver.get("engine"):
        _reason = _solver.get("reason")
        schedule.append((L["salmon_deep"], "PLACEMENT SEARCHED, NOT PROVED — HILL-CLIMB" + (
            f" — {_reason.upper()}" if _reason and _reason != "requested" else "")))
    if all_unlocated:
        schedule.append((L["brick"], f'{len(all_unlocated)} CUT(S) OFF THE BAY LINE THE SOLVER '
                         f'LOCATED ON NO WALL OF THEIR LEVEL — COUNTED, NOT DRAWN'))
    _st = plan.get("stair") or {}
    if _st.get("unplaced"):
        schedule.append((L["salmon_deep"], "STAIR NOT DRAWN — " +
                         (str((_st.get("unplaced") or {}).get("reason") or "SEE RECORD")).upper()))
    if all_stray:
        # An opening whose wall the band pass could not find. It is still DRAWN as a leaf or a
        # sill by the passes below -- this says only that no wall body was opened for it, which
        # is a disagreement between two readings of one record and is exactly the class of
        # thing this sheet is built to state rather than to smooth over.
        schedule.append((L["brick"], f'{len(all_stray)} OPENING(S) ON NO WALL LINE OF THEIR OWN '
                         f'LEVEL — DRAWN, BUT NO WALL BODY IS OPENED FOR THEM'))
    # The wall the drawing is drawn with, always, because it is a reading of the record and not
    # a convention of the sheet -- and because a reader comparing a room's figure to the ink
    # has to know that the figure is the record's clear extent and the placement carries no
    # wall bands at all (`oq/the-placement-carries-no-wall-bands`).
    schedule.append((L["ink2"], f'WALLS {wall["construction_type"].upper().replace("-", " ")} — '
                     f'ENVELOPE {wall["exterior_in"]:g} IN OUTSIDE THE PLACED ROOMS, BEARING '
                     f'{wall["bearing_interior_in"]:g} IN AND PARTITIONS {wall["partition_in"]:g} IN '
                     f'CENTRED ON THEM; ROOM FIGURES ARE THE RECORD\'S CLEAR EXTENTS'))
    if wall.get("note"):
        schedule.append((L["salmon_deep"], wall["note"].upper()))

    # THE FACE THE SHEET IS SET IN, ON THE SHEET (WP-11.5). Graphic Standard No. 1 names one
    # serif voice and every plate had asked for it in a stack and carried nothing, so a
    # reader could not tell a sheet set in EB Garamond from one set in Georgia -- which is
    # half of the "three typefaces on one plate" that opened Phase 11. A carried face is
    # named with its version; a fallback says plainly that the reader's own machine chose.
    _face_state, _face_line = SS.face_status()
    schedule.append((L["ink2"] if _face_state == "EMBEDDED" else L["salmon_deep"],
                     f'FACE {_face_state} — {_face_line}'))

    # ------------------------------------------------------------- WP-2.4 site / lot geometry
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

    # ------------------------------------------------------------- the sheet as an object
    # "Nothing sits flush to the sheet edge: the drawing lives inside a ruled border, and the
    # border inside a margin." The title block is a band at the foot of the border and the
    # schedule is set in it, which is where a note belongs on a drawing somebody prints.
    M, BP, gap = SS.SHEET["margin"], SS.SHEET["border_pad"], SS.SHEET["gap"]
    pw, ph = draw_W * scale, draw_H * scale
    panel_w = pw + extra_left + extra_right
    head_h = 54.0                                  # title and its subtitle inside the border
    grid_h = 24.0                                  # the bay figures above each plate
    foot_h = 58.0                                  # scale bar and compass under the plates
    total_w = M * 2 + BP * 2 + len(levels) * panel_w + (len(levels) - 1) * gap

    # THE SCHEDULE WRAPS, AND THE BAND GROWS TO HOLD IT. Set as one line each, the undrawable-
    # door list and the stair's own refusal ran off the right edge and past the border -- the
    # note the reader most needs, half of it not on the sheet. Nothing is shortened to make it
    # fit: the same rule the room labels are held to (a name is drawn whole or not at all)
    # applies to a disclosure, and a disclosure cut off mid-sentence is worse than a label cut
    # off mid-word because the reader cannot see that it was cut.
    sched_w = total_w - 2 * M - 2 * BP
    wrapped = []
    for ink, line in schedule:
        words, cur = line.split(" "), ""
        for word in words:
            trial = (cur + " " + word).strip()
            if cur and _text_w(trial, 8.5, mono=True, track=0.22) > sched_w:
                wrapped.append((ink, cur)); cur = word
            else:
                cur = trial
        wrapped.append((ink, cur))
    schedule = wrapped
    sched_h = 14.0 * len(schedule) + 14.0
    top = M + BP + head_h + grid_h
    total_h = top + extra_top + ph + extra_bottom + foot_h + sched_h + BP + M

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w:.0f}" height="{total_h:.0f}" '
         f'viewBox="0 0 {total_w:.0f} {total_h:.0f}" style="background:{L["paper"]}">']
    s.append(_style_block(register))
    # OQ 55: the hatch a reserved void that is open to the sky is filled with.
    s.append(f'<defs><pattern id="openvoid" width="9" height="9" patternUnits="userSpaceOnUse" '
             f'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="9" '
             f'stroke="{L["hair"]}" stroke-width="0.9" opacity="0.7"/></pattern></defs>')
    # the ruled border, and a hairline inside it
    s.append(f'<rect class="bd" x="{M:.1f}" y="{M:.1f}" width="{total_w - 2*M:.1f}" '
             f'height="{total_h - 2*M:.1f}"/>')
    s.append(f'<rect class="bd" x="{M+4:.1f}" y="{M+4:.1f}" width="{total_w - 2*M - 8:.1f}" '
             f'height="{total_h - 2*M - 8:.1f}" style="stroke:{L["rule_soft"]}"/>')
    s.append(f'<text class="hd" x="{M+BP:.1f}" y="{M+BP+22:.1f}">{_esc((plan["name"] or "").upper())}</text>')
    _date = (ctx.get("date_of_representation") or "")
    s.append(f'<text class="lb" x="{M+BP:.1f}" y="{M+BP+42:.1f}">'
             f'{_esc((plan.get("style","") or "").upper().replace("-", " "))} · '
             f'{fp.get("bays","?")} BAYS OF {fp.get("bay_module_ft","?")} FT · '
             f'{_fmt(W)} x {_fmt(H)} CLEAR · {fp.get("area_sf","?")} SF GROSS'
             f'{" · " + str(_date) if _date else ""} · {register.upper()} REGISTER</text>')

    for i, lv in enumerate(levels):
        ox = M + BP + i * (panel_w + gap) + extra_left; oy = top + extra_top
        X = lambda v, ox=ox: ox + (v - draw_x0) * scale
        Y = lambda v, oy=oy: oy + (draw_H + draw_y0 - v) * scale
        # `data-plate` carries the plate's own top edge. The levels of one house are drawn
        # side by side and share one top margin, and until WP-9.6 they did not: a room-label
        # local named `top` overwrote the SHEET's top margin, so the first plate was placed
        # from the real margin and every plate after it from wherever the last room's label
        # began -- a third of the upper floor outside the viewBox and not drawn. The guard for
        # that measured the paper-ground rect, which this package removed (the room is the
        # paper now), so the plate states its own origin instead of being inferred from a fill.
        s.append(f'<text class="lb" data-plate="{_esc(lv.get("id") or str(i))}" '
                 f'data-plate-top="{oy:.1f}" x="{ox:.1f}" y="{oy-10:.1f}">'
                 f'{_esc((lv.get("name") or lv["id"]).upper())}</text>')
        if has_lot:
            lx0, ly0, lx1, ly1 = -x_off, -y_off, lot_w - x_off, lot_d - y_off
            s.append(f'<rect class="gd" x="{X(lx0):.1f}" y="{Y(ly1):.1f}" width="{(lx1-lx0)*scale:.1f}" '
                     f'height="{(ly1-ly0)*scale:.1f}" style="stroke-dasharray:{SS.DASH["extent"]}"/>')
            s.append(f'<text class="dm" x="{X(lx0):.1f}" y="{(Y(ly1)-6):.1f}">LOT {_fmt(lot_w)} x {_fmt(lot_d)}</text>')
            sf = setback_front or 0.0
            ss_ = setback_side if setback_side is not None else x_off
            sr = setback_rear if setback_rear is not None else max(0.0, ly1 - H)
            ex0, ey0, ex1, ey1 = ss_ - x_off, sf - y_off, (lot_w - ss_) - x_off, (lot_d - sr) - y_off
            s.append(f'<rect class="gd" x="{X(ex0):.1f}" y="{Y(ey1):.1f}" width="{(ex1-ex0)*scale:.1f}" '
                     f'height="{(ey1-ey0)*scale:.1f}" style="stroke:{L["salmon_deep"]};'
                     f'stroke-dasharray:{SS.DASH["hidden"]}"/>')

        # THE GRID IS EVIDENCE, AND IT IS DRAWN AS CONSTRUCTION. The bay lines used to be
        # dashed inside the block and stopped at its edge; the exemplars this sheet is measured
        # against project every structural line thinly past the walls, which is how a reader
        # sees the discipline the plan was composed on rather than only the marks where it was
        # broken. The line is left visible -- that is what the construction weight is FOR.
        bm = fp.get("bay_module_ft") or 10
        b, n = bm, 1
        while b < W - 0.01:
            s.append(f'<line class="gd" x1="{X(b):.1f}" y1="{Y(draw_y0 + draw_H) - 16:.1f}" '
                     f'x2="{X(b):.1f}" y2="{Y(draw_y0) + 16:.1f}"/>')
            s.append(f'<text class="dm" x="{X(b):.1f}" y="{Y(draw_y0 + draw_H) - 20:.1f}" '
                     f'text-anchor="middle" style="font-size:7px;fill:{L["hair"]}">{n * bm:g}</text>')
            b += bm; n += 1

        # the reserved voids, under the walls: a court is drawn OPEN (OQ 55) -- the ground
        # colour and a hatch, so it reads as the outside it is and not as a room nobody labelled
        for r in lv["rooms"]:
            g = r.get("geometry")
            if not g or not g.get("void"): continue
            x, y, w, h = g["x_ft"], g["y_ft"], g["width_ft"], g["depth_ft"]
            if g["void"].get("roofed"):
                s.append(f'<rect x="{X(x):.1f}" y="{Y(y+h):.1f}" width="{w*scale:.1f}" '
                         f'height="{h*scale:.1f}" fill="{L["paper_mat"]}" stroke="none"/>')
            else:
                s.append(f'<rect x="{X(x):.1f}" y="{Y(y+h):.1f}" width="{w*scale:.1f}" '
                         f'height="{h*scale:.1f}" fill="url(#openvoid)" stroke="none"/>')

        # the walls, as bodies
        for bd in level_bands[i]:
            cls = "pm" if bd["kind"] == "masonry" else "pp"
            blk = f' data-block="{bd["block"]}"' if bd.get("block") is not None else ""
            s.append(f'<rect class="{cls}" data-wall="{bd["wall"]}"{blk} x="{X(bd["x_ft"]):.1f}" '
                     f'y="{Y(bd["y_ft"] + bd["depth_ft"]):.1f}" width="{bd["width_ft"]*scale:.1f}" '
                     f'height="{bd["depth_ft"]*scale:.1f}"><title>{_esc(bd["why"])}</title></rect>')

        # ---------------------------------------------------------- the stoop and the stacks
        # WP-11.4, from plan["threshold"] and plan["hearths"] and from nothing else. The
        # STACK is drawn on every plate because it passes through every floor; the STOOP
        # only on the ground, because it is at grade. Both in the wall's own body: they are
        # brick, and this drawing says so with the poché it already has for brick.
        for sk in ((plan.get("hearths") or {}).get("stacks") or []):
            s.append(f'<rect class="st" data-stack="{sk["wall"]}" x="{X(sk["x_ft"]):.1f}" '
                     f'y="{Y(sk["y_ft"] + sk["depth_ft"]):.1f}" '
                     f'width="{sk["width_ft"]*scale:.1f}" height="{sk["depth_ft"]*scale:.1f}">'
                     f'<title>{_esc("chimney stack, %s in square, %s to the %s gable end" % (sk["stack_plan_in"], sk["side"], sk["wall"]))}</title></rect>')
        # ------------------------------------------------- the terrace at grade (WP-11.10)
        # Drawn OPEN -- an edge and a name, no poché and no wash -- which is what OQ 55's
        # reserved voids already do and what all four exemplar plans do with a terrace. On the
        # level the appendage's own record names, NOT hard-coded to the ground: every appendage
        # in this corpus is at grade and a hard-coded plate would HIDE a future one rather than
        # refuse it, which is the silent third state this repository keeps abolishing.
        for ap in [a for a in ((plan.get("appendages") or {}).get("placed") or [])
                   if a.get("level", 0) == lv.get("index", i)]:
            r_ = ap["rect"]
            s.append(f'<g data-appendage="{_esc(ap["room"])}" '
                     f'data-appendage-wall="{_esc(ap["wall"])}">')
            why = ("at grade, unroofed, appended to %s on its %s face"
                   % (", ".join(ap["serves"]), ap["wall"]))
            s.append(f'<rect class="ap" x="{X(r_["x_ft"]):.1f}" '
                     f'y="{Y(r_["y_ft"] + r_["depth_ft"]):.1f}" '
                     f'width="{r_["width_ft"]*scale:.1f}" '
                     f'height="{r_["depth_ft"]*scale:.1f}">'
                     f'<title>{_esc(why)}</title></rect>')
            nm_ = (ap.get("name") or ap["room"]).upper()
            if r_["width_ft"] * scale > 8.5 * len(nm_) and r_["depth_ft"] * scale > 16:
                s.append(f'<text class="nm" text-anchor="middle" '
                         f'x="{X(r_["x_ft"] + r_["width_ft"]/2):.1f}" '
                         f'y="{Y(r_["y_ft"] + r_["depth_ft"]/2) + 4:.1f}">{_esc(nm_)}</text>')
            s.append('</g>')
        if i == 0:
            for st in ((plan.get("threshold") or {}).get("steps") or []):
                # `data-threshold` names the ROOM, as it does in the browser sheet, so a
                # selector written for one renderer finds the same thing in the other; the
                # part is on the rect inside it.
                s.append(f'<g data-threshold="{_esc(st["room"])}">')
                for key, why in (("platform", "stoop platform"),
                                 ("flight", "%s risers at %s in, treads %s in"
                                  % (st["riser_count"], st["riser_height_in"], st["tread_depth_in"]))):
                    r_ = st.get(key)
                    if not r_: continue
                    s.append(f'<rect class="st" data-part="{key}" x="{X(r_["x_ft"]):.1f}" '
                             f'y="{Y(r_["y_ft"] + r_["depth_ft"]):.1f}" '
                             f'width="{r_["width_ft"]*scale:.1f}" height="{r_["depth_ft"]*scale:.1f}">'
                             f'<title>{_esc(why)}</title></rect>')
                for ns in (st.get("nosings") or []):
                    x1, y1, x2, y2 = ns["line"]
                    s.append(f'<line class="ns" x1="{X(x1):.1f}" y1="{Y(y1):.1f}" '
                             f'x2="{X(x2):.1f}" y2="{Y(y2):.1f}"/>')
                s.append('</g>')

        # ---------------------------------------------------------- labels
        # Wrapped, shrunk and where necessary turned to fit the room; never truncated. The
        # names are set in roman capitals and letterspaced, which is the standard's own
        # `--tr-room` and the case every exemplar plan uses -- the previous sheet set them in
        # mixed case with no tracking, in whatever sans the reader's machine substituted for a
        # webfont the SVG never carried.
        for r in lv["rooms"]:
            g = r.get("geometry")
            if not g: continue
            x, y, w, h = g["x_ft"], g["y_ft"], g["width_ft"], g["depth_ft"]
            cx, cy = X(x + w/2), Y(y + h/2)
            nm = (r.get("name") or r["id"]).upper()
            # the label sits INSIDE the room, clear of the partitions that bound it, so the
            # box is the room less half a partition on each side
            inset = wall["partition_in"] / 12.0 * scale
            bw, bh = w*scale - inset - 6, h*scale - inset - 5
            if bw <= 4 or bh <= 5: continue
            tail = ""
            if g.get("void"):
                tail = "roofed, unheated" if g["void"].get("roofed") else "open to sky"
            # ∗ — DRAWN at a size the record does not declare. It is NOT part of `dim`, and
            # that is the point: tests/test_drawn_labels.py freezes this line because OQ 55's
            # void disclosure once rode on it, and anything that LENGTHENS the string shrinks
            # the fitted size until the dimension drops out of every narrow room.
            star = "∗" if (working and r["id"] in diverged_ids) else ""
            dim = f'{_fmt(min(w,h))} x {_fmt(max(w,h))} · {g["area_sf"]} sf'
            show_dim = working

            def lay(box_w, box_h):
                tsize = min(6.5, box_w / (0.60 * len(tail))) if tail else 0
                tsize = max(4.6, tsize) if tail else 0
                dsize = min(8.0, box_w / (0.60 * len(dim))) if show_dim else 0
                want = show_dim and dsize >= 5.6 and box_h >= 26 + (tsize * 1.5 if tail else 0)
                reserve = (dsize * 1.5 if want else 0) + (tsize * 1.5 if tail else 0)
                fit = _fit_lines(nm, box_w, box_h - reserve, 11.0, 6.0, track=ROOM_TRACK)
                if not fit: return None
                lines, size = fit
                show = want and size >= 7.0
                return lines, size, (dsize if show else None), tsize, \
                    len(lines) * size * 1.2 + (dsize * 1.5 if show else 0) \
                    + (tsize * 1.5 if tail else 0)

            flat = lay(bw, bh)
            turned = lay(bh, bw) if h > w * 1.3 else None
            use = turned if (turned and (not flat or turned[1] > flat[1] * 1.15)) else flat
            if not use: continue
            lines, size, dsize, tsize, block = use
            gx = f'<g transform="rotate(-90 {cx:.1f} {cy:.1f})">' if use is turned else '<g>'
            s.append(gx)
            # NAMED `label_top`, AND THE NAME IS THE WHOLE FIX. This was `top`, the SHEET'S TOP
            # MARGIN, read by both `total_h` and `oy`; reassigning it here positioned the first
            # plate from the real margin and every plate after it from wherever the last room's
            # label began. A third of the upper floor was outside the viewBox and simply not
            # drawn. Lucas found it by looking at the sheet; nothing in the suite could.
            label_top = cy - block/2
            # `li`, NOT `i`: the plate loop is `for i, lv in enumerate(levels)` and this inner
            # loop REBOUND IT, so `level_marks[i]` below read the wrong level's marks.
            for li, ln in enumerate(lines):
                # style=, not font-size=: a presentation attribute loses to `.nm`, so a fitted
                # size written as an attribute is computed, ignored, and the label overflows.
                # And the x is nudged by half a track: SVG adds letter-spacing after the LAST
                # glyph too, which walks a centred label left by exactly that much.
                s.append(f'<text class="nm" x="{cx + ROOM_TRACK * size / 2:.1f}" '
                         f'y="{label_top + (li + 0.72) * size * 1.2:.1f}" '
                         f'style="font-size:{size:.2f}px" text-anchor="middle">{_esc(ln)}</text>')
            below = label_top + len(lines) * size * 1.2
            if dsize:
                s.append(f'<text class="dm" x="{cx:.1f}" y="{below + dsize:.1f}" '
                         f'style="font-size:{dsize:.2f}px" text-anchor="middle">{_esc(dim)}</text>')
                if star:
                    sx = cx + 0.30 * dsize * len(dim) + 0.30 * dsize
                    s.append(f'<text class="dm" x="{sx:.1f}" y="{below + dsize:.1f}" '
                             f'style="font-size:{dsize:.2f}px;fill:{L["salmon_deep"]}">{star}</text>')
                below += dsize * 1.5
            elif star:
                s.append(f'<text class="dm" x="{cx:.1f}" y="{below + 5.0:.1f}" '
                         f'style="font-size:5.00px;fill:{L["salmon_deep"]}" '
                         f'text-anchor="middle">{star}</text>')
            if tail:
                s.append(f'<text class="dm" x="{cx:.1f}" y="{below + tsize:.1f}" '
                         f'style="font-size:{tsize:.2f}px;fill:{L["ink3"]}" '
                         f'text-anchor="middle">{_esc(tail)}</text>')
            s.append('</g>')

        # ---------------------------------------------------------- openings
        # A WINDOW IS A BREAK IN THE WALL, NOT A BAR LAID ON IT. Until this package a window
        # was one 2.6 px line in gilt struck along the wall line -- colour outlining a thing,
        # which the standard forbids, and a mark that said nothing about the wall it is in. The
        # body is already opened for it above; what is drawn here is the sill outside the wall
        # and the glazing on its centre line, which is what the two lines of a sash are.
        op = level_openings[i]

        def _frame(wl, at, half_px, glazed, edge=None):
            """The three lines that make an opening READ as an opening.

            The wall body already has a hole cut in it and the hole's own ends are the jamb
            returns. What was missing is the frame: without it a window is a gap with a mark
            beside it, which is what a reader sees as a wall that stops and starts for no
            reason. INNER face, OUTER face, and -- for a window -- the glazing on the centre
            line, which is the two lines of a sash. A door gets the first two and its leaf,
            because a door is an opening you pass through and a window is one you do not."""
            t = ext_ft * scale
            # WP-11.14: `edge` is the room's OWN face, off the record. Falling back to the
            # footprint's is what drew two of the tagged plan's exterior doors, with their
            # sills and swings, in open space north of the building.
            if wl in ("S", "N"):
                cx0 = X(at); y0 = Y(edge if edge is not None else (0 if wl == "S" else H))
                out = t if wl == "S" else -t          # outward from the block
                s.append(f'<line class="dr" x1="{cx0-half_px:.1f}" y1="{y0:.1f}" '
                         f'x2="{cx0+half_px:.1f}" y2="{y0:.1f}"/>')
                s.append(f'<line class="sill" x1="{cx0-half_px-2:.1f}" y1="{y0+out:.1f}" '
                         f'x2="{cx0+half_px+2:.1f}" y2="{y0+out:.1f}"/>')
                if glazed:
                    s.append(f'<line class="win" x1="{cx0-half_px:.1f}" y1="{y0+out/2:.1f}" '
                             f'x2="{cx0+half_px:.1f}" y2="{y0+out/2:.1f}"/>')
            else:
                cy0 = Y(at); x0 = X(edge if edge is not None else (0 if wl == "W" else W))
                out = -t if wl == "W" else t
                s.append(f'<line class="dr" x1="{x0:.1f}" y1="{cy0-half_px:.1f}" '
                         f'x2="{x0:.1f}" y2="{cy0+half_px:.1f}"/>')
                s.append(f'<line class="sill" x1="{x0+out:.1f}" y1="{cy0-half_px-2:.1f}" '
                         f'x2="{x0+out:.1f}" y2="{cy0+half_px+2:.1f}"/>')
                if glazed:
                    s.append(f'<line class="win" x1="{x0+out/2:.1f}" y1="{cy0-half_px:.1f}" '
                             f'x2="{x0+out/2:.1f}" y2="{cy0+half_px:.1f}"/>')

        for win in op["windows"]:
            _frame(win["wall"], win["at_ft"], win["width_ft"] * scale / 2, True,
                   win.get("edge_ft"))

        def _door(px, py, horiz, width, dtype, swing_positive):
            """One opening drawn as the KIND of opening it is. Until WP-6.1 `type` was read by
            no renderer at all, so a pair of doors and a cased opening were both drawn as one
            enormous hinged leaf -- what a reader saw as 'a massive door' with 'no rhyme or
            reason' to its size. The leaf is the medium pen and the arc the construction pen,
            which is the weight ladder doing the work colour used to be asked to do."""
            half = width * scale / 2
            if horiz: ax0, ay0, bx0, by0 = X(px)-half, Y(py), X(px)+half, Y(py)
            else:     ax0, ay0, bx0, by0 = X(px), Y(py)-half, X(px), Y(py)+half

            def jambs():
                t = ext_ft * scale / 2
                for jx, jy in ((ax0, ay0), (bx0, by0)):
                    if horiz: s.append(f'<line class="dr" x1="{jx:.1f}" y1="{jy-t:.1f}" x2="{jx:.1f}" y2="{jy+t:.1f}"/>')
                    else:     s.append(f'<line class="dr" x1="{jx-t:.1f}" y1="{jy:.1f}" x2="{jx+t:.1f}" y2="{jy:.1f}"/>')

            def leaf(hx, hy, radius, tox, toy, sweep):
                if horiz: ex, ey = hx, hy + (-radius if swing_positive else radius)
                else:     ex, ey = hx + (radius if swing_positive else -radius), hy
                s.append(f'<path class="sw" d="M {ex:.1f} {ey:.1f} A {radius:.1f} {radius:.1f} '
                         f'0 0 {sweep} {tox:.1f} {toy:.1f}"/>')
                s.append(f'<line class="dr" x1="{hx:.1f}" y1="{hy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}"/>')

            sw = (0 if swing_positive else 1) if horiz else (1 if swing_positive else 0)
            if dtype == "double":
                mx, my = (ax0 + bx0) / 2, (ay0 + by0) / 2
                leaf(ax0, ay0, half, mx, my, sw)
                leaf(bx0, by0, half, mx, my, 1 - sw)
            elif dtype in ("cased-opening", "open"):
                jambs()                                    # a lining and no leaf
            elif dtype == "pocket":
                jambs()
                if horiz: s.append(f'<line class="sw" x1="{ax0-2*half:.1f}" y1="{ay0:.1f}" x2="{ax0:.1f}" y2="{ay0:.1f}" style="stroke-dasharray:{SS.DASH["extent"]}"/>')
                else:     s.append(f'<line class="sw" x1="{ax0:.1f}" y1="{ay0-2*half:.1f}" x2="{ax0:.1f}" y2="{ay0:.1f}" style="stroke-dasharray:{SS.DASH["extent"]}"/>')
            elif dtype in ("garage", "bulkhead"):
                jambs()
                dash = f' style="stroke-dasharray:{SS.DASH["hidden"]}"' if dtype == "bulkhead" else ''
                s.append(f'<line class="dr" x1="{ax0:.1f}" y1="{ay0:.1f}" x2="{bx0:.1f}" y2="{by0:.1f}"{dash}/>')
            else:
                leaf(ax0, ay0, 2 * half, bx0, by0, sw)

        for d in op["interior"]:
            px, py = (d["pos_ft"], d["at_ft"]) if d["horiz"] else (d["at_ft"], d["pos_ft"])
            _door(px, py, d["horiz"], d["width_ft"], d["type"], d["swing_positive"])
        for d in op["exterior"]:
            wl, p_ = d["wall"], d["at_ft"]
            horiz = wl in ("S", "N")
            # WP-11.14: across the wall from the ROOM's own face, not the footprint's. `W` and
            # `H` remain the fallback for a 0.3.0 record whose entry carries no `edge_ft`, and
            # on a one-rectangle house the two coincide exactly.
            #
            # COMPUTED ONCE AND HANDED TO BOTH, which a mutation pass forced: the frame read
            # `d["edge_ft"]` and the leaf read a local, so reverting either still moved the
            # other and a test comparing two plates could not tell them apart. One opening has
            # one face; two readers of it is how a leaf and its own sill come to disagree.
            _e = d.get("edge_ft")
            if _e is None:
                _e = (0.0 if wl == "S" else H) if horiz else (0.0 if wl == "W" else W)
            _frame(wl, p_, d["width_ft"] * scale / 2, False, _e)
            px, py = (p_, _e) if horiz else (_e, p_)
            _door(px, py, horiz, d["width_ft"], d["type"], wl in ("S", "W"))

        # ---------------------------------------------------------- the stair
        # Drawn from plan["stair"] and from nothing else (WP-6.2). Treads, a nosing on each,
        # and an arrow that says which way is up -- `up_direction` has been on the record since
        # WP-9.6 and no renderer read it, so a stair was a set of parallel lines with a count
        # of risers printed over them.
        st = plan.get("stair")
        if st and (st.get("level") or 0) == i and st.get("flights"):
            for fl in st["flights"]:
                fx, fy = fl["x_ft"], fl["y_ft"]
                fw, fd = fl["width_ft"], fl["depth_ft"]
                s.append(f'<rect class="fn" x="{X(fx):.1f}" y="{Y(fy+fd):.1f}" '
                         f'width="{fw*scale:.1f}" height="{fd*scale:.1f}"/>')
                n = max(1, fl.get("treads") or 1)
                horiz_run = fl["direction"] in ("E", "W")
                for t in range(1, n):
                    if horiz_run:
                        tx = fx + fw * (t / n)
                        s.append(f'<line class="fn" x1="{X(tx):.1f}" y1="{Y(fy):.1f}" '
                                 f'x2="{X(tx):.1f}" y2="{Y(fy+fd):.1f}"/>')
                    else:
                        ty = fy + fd * (t / n)
                        s.append(f'<line class="fn" x1="{X(fx):.1f}" y1="{Y(ty):.1f}" '
                                 f'x2="{X(fx+fw):.1f}" y2="{Y(ty):.1f}"/>')
            f0 = st["flights"][0]
            # the arrow runs the length of the first flight, in its own stated direction
            d0 = f0["direction"]
            ax_, ay_ = X(f0["x_ft"] + f0["width_ft"]/2), Y(f0["y_ft"] + f0["depth_ft"]/2)
            run = (f0["width_ft"] if d0 in ("E", "W") else f0["depth_ft"]) * scale * 0.34
            dx, dy = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}.get(d0, (0, -1))
            hx, hy = ax_ + dx*run, ay_ + dy*run
            s.append(f'<line class="dr" x1="{ax_-dx*run:.1f}" y1="{ay_-dy*run:.1f}" '
                     f'x2="{hx:.1f}" y2="{hy:.1f}"/>')
            s.append(f'<path class="dr" d="M {hx - dx*5 - dy*3:.1f} {hy - dy*5 + dx*3:.1f} '
                     f'L {hx:.1f} {hy:.1f} L {hx - dx*5 + dy*3:.1f} {hy - dy*5 - dx*3:.1f}"/>')
            s.append(f'<text class="dm" x="{ax_ - dy*10:.1f}" y="{ay_ + dx*10 + 3:.1f}" '
                     f'text-anchor="middle">UP {st["risers"]}R</text>')
        elif st and (st.get("level") or 0) == i and st.get("unplaced"):
            # THE NOTE USED TO BE SET ACROSS THE ROOM'S OWN NAME. It was centred on the stair
            # well, and a stair well is inside a stair hall, so on the shipped Tidewater sheet
            # "STAIR NOT DRAWN — SEE RECORD" was drawn straight through "STAIR HALL" and
            # neither could be read. The disclosure is a note, so it goes where the notes go --
            # the schedule below the border -- and what stays on the field is the well itself,
            # drawn as the reserved void it is: hatched, with no stair in it, which is a
            # truer picture than a sentence lying across a label.
            g0 = st.get("well") or {}
            if g0:
                s.append(f'<rect class="gd" x="{X(g0["x_ft"]):.1f}" '
                         f'y="{Y(g0["y_ft"] + g0["depth_ft"]):.1f}" '
                         f'width="{g0["width_ft"]*scale:.1f}" height="{g0["depth_ft"]*scale:.1f}" '
                         f'style="stroke-dasharray:{SS.DASH["extent"]}"><title>the stair well: '
                         f'{_esc(str((st.get("unplaced") or {}).get("reason") or ""))}</title></rect>')

        # fixtures, from room["fixture_layout"] and from nothing else
        for r in lv["rooms"]:
            for f in (r.get("fixture_layout") or []):
                if f.get("unplaced") or f.get("x_ft") is None: continue
                s.append(f'<rect class="fn" x="{X(f["x_ft"]):.1f}" y="{Y(f["y_ft"]+f["depth_ft"]):.1f}" '
                         f'width="{f["width_ft"]*scale:.1f}" height="{f["depth_ft"]*scale:.1f}" '
                         f'style="stroke-dasharray:{SS.DASH["extent"]}"><title>{_esc(f["item"])}</title></rect>')

        # furniture, from room["furniture_layout"] and from nothing else (WP-11.3). The fine
        # pen, SOLID -- the fixtures keep their dash, so a reader can tell a derived wet
        # fixture from a derived furniture arrangement without a legend. The shapes are
        # furniture/symbols.json's, mapped into each item's own rectangle by
        # build/furniture.py::marks_for; this renderer computes no geometry of its own, which
        # is what lets the browser sheet draw the same marks from the same one answer.
        for r in lv["rooms"]:
            for f in (r.get("furniture_layout") or []):
                for m in (f.get("marks") or []):
                    if "rect" in m:
                        mx, my, mw, mh = m["rect"]
                        s.append(f'<rect class="fu" x="{X(mx):.1f}" y="{Y(my + mh):.1f}" '
                                 f'width="{mw * scale:.1f}" height="{mh * scale:.1f}">'
                                 f'<title>{_esc(f["item"])}</title></rect>')
                    elif "line" in m:
                        x1, y1, x2, y2 = m["line"]
                        s.append(f'<line class="fu" x1="{X(x1):.1f}" y1="{Y(y1):.1f}" '
                                 f'x2="{X(x2):.1f}" y2="{Y(y2):.1f}"/>')
                    elif "circle" in m:
                        cx_, cy_, rr = m["circle"]
                        s.append(f'<circle class="fu" cx="{X(cx_):.1f}" cy="{Y(cy_):.1f}" '
                                 f'r="{rr * scale:.1f}"><title>{_esc(f["item"])}</title></circle>')


        # ---------------------------------------------------------- P7, at its location
        # A compromise is counted AND appears on the drawing, at its location (OQ 33). The
        # count is in the schedule below the border; the MARKS stay here, on the cut line, in
        # the working register -- in ink and never in colour, because colour in this drawing
        # names a material and does not flag a condition.
        if working:
            drawn_mk, _unlocated_mk = level_marks[i]
            for mk, runs, at_along in drawn_mk:
                vert = mk.get("axis") == "x"
                at = mk.get("at_ft", 0.0)
                for lo, hi in runs:
                    if vert: x1 = x2 = X(at); y1, y2 = Y(lo), Y(hi)
                    else:    y1 = y2 = Y(at); x1, x2 = X(lo), X(hi)
                    s.append(f'<line class="gd" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" '
                             f'y2="{y2:.1f}" style="stroke:{L["ink2"]};stroke-dasharray:3 3"/>')
                gx0, gy0 = (X(at), Y(at_along)) if vert else (X(at_along), Y(at))
                s.append(f'<path class="mk" d="M {gx0:.1f} {gy0-4.5:.1f} L {gx0+4.0:.1f} '
                         f'{gy0+3.0:.1f} L {gx0-4.0:.1f} {gy0+3.0:.1f} Z"><title>'
                         f'{mk.get("off_ft")} ft off the bay line</title></path>')

    # ------------------------------------------------------------- the foot of the sheet
    foot_y = top + extra_top + ph + extra_bottom + 26
    # A GRAPHIC SCALE, not a line with a number beside it. Alternating cells so a reader can
    # step a dimension off the sheet, which is what a scale bar is for and what one line is not.
    sx0 = M + BP
    cell = 5 * scale                       # five feet a cell
    for k in range(4):
        s.append(f'<rect x="{sx0 + k*cell:.1f}" y="{foot_y:.1f}" width="{cell:.1f}" height="5" '
                 f'fill="{L["ink"] if k % 2 == 0 else L["paper"]}" stroke="{L["ink"]}" stroke-width="0.6"/>')
    for k, ft in ((0, 0), (2, 10), (4, 20)):
        s.append(f'<text class="dm" x="{sx0 + k*cell:.1f}" y="{foot_y + 16:.1f}" '
                 f'text-anchor="middle">{ft}</text>')
    s.append(f'<text class="dm" x="{sx0 + 4*cell + 10:.1f}" y="{foot_y + 16:.1f}">FT</text>')

    # A COMPASS ROSE. The room rectangles are axis-aligned to the model frame and not to true
    # north, so an honest rose points up and SAYS what bearing that up direction has on the
    # ground -- `street_bearing_deg` is reported, never used to rotate the drawing.
    nx, ny = total_w - M - BP - 22, foot_y + 4
    s.append(f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="13" fill="none" stroke="{L["hair"]}" stroke-width="0.7"/>')
    s.append(f'<path d="M {nx:.1f} {ny-13:.1f} L {nx+4:.1f} {ny:.1f} L {nx:.1f} {ny+13:.1f} '
             f'L {nx-4:.1f} {ny:.1f} Z" fill="{L["ink"]}" stroke="none"/>')
    s.append(f'<path d="M {nx:.1f} {ny+13:.1f} L {nx+4:.1f} {ny:.1f} L {nx-4:.1f} {ny:.1f} Z" '
             f'fill="{L["paper"]}" stroke="{L["ink"]}" stroke-width="0.6"/>')
    for lbl, ddx, ddy in (("N", 0, -19), ("S", 0, 22), ("E", 19, 3), ("W", -19, 3)):
        s.append(f'<text class="dm" x="{nx+ddx:.1f}" y="{ny+ddy:.1f}" text-anchor="middle" '
                 f'style="font-size:7px">{lbl}</text>')
    street_bearing = site.get("street_bearing_deg") if has_lot else None
    cap = "NORTH IS UP" + (f" · STREET BEARS {street_bearing:.0f}°" if street_bearing is not None else "")
    # BESIDE the rose, not under it: under it the caption sat on the title block's own rule and
    # the two were drawn through each other.
    s.append(f'<text class="lb" x="{nx - 34:.1f}" y="{ny + 3:.1f}" text-anchor="end">{cap}</text>')

    # ------------------------------------------------------------- the title block
    sched_y = foot_y + 52
    s.append(f'<line x1="{M+BP:.1f}" y1="{sched_y - 14:.1f}" x2="{total_w-M-BP:.1f}" '
             f'y2="{sched_y - 14:.1f}" stroke="{L["rule"]}" stroke-width="1"/>')
    for k, (ink, line) in enumerate(schedule):
        s.append(f'<text class="lb" x="{M+BP:.1f}" y="{sched_y + 14*k:.1f}" '
                 f'style="fill:{ink}">{_esc(line)}</text>')
    # WP-6.1: the △ has been drawn since OQ 33 and was defined only in running prose, so a
    # reader meeting one on the drawing had nothing to read it BY and reported it as arrows
    # that "seem to point to anything and everything". A symbol a drawing uses is a symbol the
    # drawing defines, and the definition belongs in the margin with the rest of the notes.
    if working and (gr.get("relaxations", {}) or {}).get("count"):
        ly = sched_y + 14 * len(schedule)
        s.append(f'<path class="mk" d="M {M+BP+4:.1f} {ly-4.5:.1f} L {M+BP+8:.1f} {ly+3.0:.1f} '
                 f'L {M+BP:.1f} {ly+3.0:.1f} Z"/>')
        s.append(f'<text class="lb" x="{M+BP+16:.1f}" y="{ly+3:.1f}">'
                 f'A CUT OFF THE BAY LINE — NO BEARING WALL UNDER IT</text>')
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

def _edge_of(g, wall, box=None):
    """Where an EXTERIOR opening in this room's `wall` is drawn across the wall. WP-11.14.

    The element's own face where the room's element is known, and the room's face otherwise --
    and that order is the point rather than a default. `render()` draws the exterior poché
    OUTWARD from the element's edge, so an opening cut in that wall belongs on the element's
    face; a room may sit up to `tol` inside it and still be a boundary room. On every shipped
    plan the rooms tile the block exactly, so the two coincide and this is the identity.

    The INTERIOR branch of `derive_openings` uses the room's own shared face, correctly, and
    that asymmetry is why this is a named function: the two questions look identical and are
    not, and a first version of this package answered them with one expression.
    """
    if box:
        bx, by, bW, bH = box
        return {"S": by, "N": by + bH, "W": bx, "E": bx + bW}[wall]
    return {"S": g["y_ft"], "N": g["y_ft"] + g["depth_ft"],
            "W": g["x_ft"], "E": g["x_ft"] + g["width_ft"]}[wall]


def _boundary_wall(g, wall, W, H, tol=0.6, box=None):
    """The run of a room's edge on its OWN element's boundary: (wall, lo, hi, edge_ft).

    WP-11.14. `box` is `(x, y, W, H)` of the massing element the room stands in, from
    `elements.bounds_index` -- the same reader `openings.py` has used since WP-11.9. Without
    it this function asked whether the room touched the FOOTPRINT, which on a one-rectangle
    house is the same question and on a dependency is a different one: a room at x = -30 with
    the block at 0..40 satisfied `x <= tol` for reasons of sign rather than of geometry, and
    matched nothing on its other three faces. Measured on a hand-tagged Tidewater, five
    windows standing on their own element's face were dropped as off-footprint and drawn
    nowhere at all.

    `edge_ft` is the fourth return and it is what WP-11.13 found missing: the coordinate of
    the face ITSELF, so the drawing does not have to re-derive it from a rectangle it no
    longer has. `render()` drew every exterior opening at the footprint's edge -- two doors
    of the tagged plan landed 12.00 and 8.98 ft north of the rooms they belong to, in open
    space -- because the entry carried a position ALONG the wall and nothing across it.
    """
    x, y, w, h = g["x_ft"], g["y_ft"], g["width_ft"], g["depth_ft"]
    bx, by, bW, bH = box if box else (0.0, 0.0, W, H)
    if wall == "S" and y <= by + tol: return ("S", x, x + w, by)
    if wall == "N" and y + h >= by + bH - tol: return ("N", x, x + w, by + bH)
    if wall == "W" and x <= bx + tol: return ("W", y, y + h, bx)
    if wall == "E" and x + w >= bx + bW - tol: return ("E", y, y + h, bx + bW)
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


def derive_openings(rooms, W, H, tol=0.6, appendages=None, bounds=None):
    """Every opening of one level, resolved to where it is drawn -- and every declared
    opening that CANNOT be drawn, with the reason. The second half is the point: a door
    with no drawable shared wall used to be `continue`d over in silence by this renderer
    and by the workbench's, so the Tidewater kitchen's five declared interior doors were
    drawn as none and the sheet said nothing. Only the DXF exporter has ever owned up.

    Where the record carries a placed position (schema 0.3.0), it is READ. Where it does
    not, the position is invented as it always was and `inferred_positions` counts it, so
    the sheet can say which kind of drawing the reader is looking at.

    `rooms` is a list of the level's room records, each carrying `geometry`.

    WP-11.10. `appendages` is `{room_id: rect}` for the at-grade appendages placed OUTSIDE the
    block on this level -- a terrace, today. An appendage's room carries no `geometry` (that is
    the whole mechanism of the ruling; see `build/appendages.py`), so the lookup below found no
    room and called the placed door *"the other room is not placed on this level"*: the record
    said the door was seated and the sheet said it could not be drawn. Two records of one door,
    which is WP-6.1's own finding. The rectangle is needed for the lookup and for the swing
    direction and for nothing else. `workbench/app/src/sheet/derive.js::doors` takes the same
    argument in the same place; the two are held to one answer by
    `tests/fixtures/sheet_symbols/`, and to this branch by a hand-built pair --
    `tests/test_appendages.py` and `derive.test.mjs` -- because the frozen fixture predates the
    pass and regenerating it would be eight hundred lines of solver noise (its own README)."""
    idx = {r["id"]: r for r in rooms if r.get("geometry")}
    for _rid, _rect in (appendages or {}).items():
        idx.setdefault(_rid, {"id": _rid, "geometry": dict(_rect)})
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
                                 # WP-11.14: the coordinate ACROSS the wall, from the room's own
                                 # rectangle. `at_ft` on an exterior entry is the position ALONG
                                 # the wall -- the same key means the perpendicular on an
                                 # INTERIOR entry, which is why there was nowhere to put this
                                 # and the drawing fell back to the footprint's edge.
                                 "edge_ft": round(
                                     _edge_of(a, wall, (bounds or {}).get(r["id"])), 3),
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
                    seat = _boundary_wall(a, wl, W, H, tol, (bounds or {}).get(r["id"]))
                    if seat: break
                if not seat:
                    undrawable.append({"from": r["id"], "to": "exterior", "width_ft": width,
                        "type": dtype,
                        "reason": "no declared exterior wall of this room is on its own "
                                  "massing element's boundary here"})
                    continue
                wl, lo, hi, edge = seat
                used_walls.add(wl)
                mid = (lo + hi) / 2
                exterior.append({"room": r["id"], "wall": wl, "width_ft": width, "type": dtype,
                                 "at_ft": mid, "edge_ft": round(edge, 3), "inferred_wall": True,
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
            seat = _boundary_wall(a, win.get("wall"), W, H, tol, (bounds or {}).get(r["id"]))
            if not seat:
                off_footprint += n
                continue
            wl, lo, hi, edge = seat
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
                                "at_ft": round(p, 3), "edge_ft": round(edge, 3)})
    return {"interior": interior, "exterior": exterior, "undrawable": undrawable,
            "windows": windows, "windows_off_footprint": off_footprint,
            "windows_crowded": crowded, "inferred_widths": inferred_widths,
            "inferred_positions": inferred_positions}

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
