#!/usr/bin/env python3
"""The sheet's graphic standard, in one place — the ink, the pen and the letter.

WHY THIS FILE EXISTS. Graphic Standard No. 1 is written down: `workbench/app/src/theme/
tokens.css` carries it verbatim — a cream ground, a warm graphite ink ladder, five named
line weights, poche as "a body: coal skin, salmon flesh", one serif voice in letterspaced
capitals, and the rule that decides most arguments here: *"Duties are exclusive ... Color
names things; it never outlines them."* The four `build/render_*.py` renderers were written
against a DARK instrument palette instead, each carrying its own copy of the same ten-key
`PAL` dict, and `workbench/server/svg_theme.py` translated the finished SVG into the standard
by literal hex substitution on the way to the browser. So the sheet had the standard's COLOURS
and none of its GRAMMAR, in five spellings: three `PAL` dicts, one hex->hex map, and the CSS.

This module is the one spelling. `DARK` is those dicts, verbatim, so the three renderers that
still draw in the dark register are a rename and nothing else — proved byte-identical over all
ten sheets `workbench/server/corpus.drawing()` produces. `LIGHT`, `LW`, `FACE`, `TRACK`,
`DASH` and `POCHE` are the standard itself, for the renderer that draws in it.

LOADED BY PATH, like every module in `build/`, so each script still runs standalone
(`modcache.load` keeps it to one execution per process — see build/modcache.py and OQ 28).

THE FACE ITSELF LIVES HERE TOO, SINCE WP-11.5 -- `font_face_rule()`, `face_status()` and
`advance_widths()` read a subset committed under assets/generated/ and built by
`build/gen_sheet_font.py`. The standard names one serif voice; until that package every sheet
asked for it in a `font-family` stack and carried no font, so an exported SVG was set in
whatever the reader's machine had and could not say so.

WHAT MUST NOT HAPPEN HERE. A hex literal in a renderer. `workbench/server/tests/
test_m3_drawings.py::test_retokenize_is_total_over_renderer_palettes` reads every `#RRGGBB`
out of the renderer sources AND out of this file, and requires each to be either a key of
`svg_theme.HEX_MAP` (a dark value, translated on the way out) or already a value of `LIGHT`
(a Drawn Language token, which passes through untouched). Before this file existed that test
scanned four sources; moving the palettes here without widening it would have left it passing
over an empty set, which is this repository's most-repeated failure -- a guard that cannot
fire. It is widened in the same commit.
"""

# ---------------------------------------------------------------- the dark register
# Verbatim from build/render_plan.py, render_section.py and render_roof.py, which carried
# three identical copies. The comment each of them gave for the duplication -- "this file,
# like every other build/*.py module in this corpus, is loaded standalone via importlib" --
# is answered by modcache rather than by a fourth copy.
DARK = {
    "ground": "#0B1B29", "paper": "#0F2536", "rule": "#24455E", "ink": "#EDE7DA",
    "ink2": "#9FB3C2", "ink3": "#63808F", "brass": "#D8B26A", "verd": "#7FB3A3",
    "copper": "#C4734A", "iron": "#C4553A",
}

# render_elevation.py's superset: the same ten plus four material tones of its own.
DARK_ELEVATION = dict(DARK, wall="#16344A", glass="#2E5468", sash="#EDE7DA", shutter="#3A5A47")

# render_plan.py's room fills, by the room catalogue's `function_class`. Kept here with the
# rest of the dark register because they are part of it; the presentation sheet does not use
# them at all -- the standard's own rule is that colour names a material, and a wash keyed on
# what a room is FOR is a classification, which is the reader's job and not the ink's.
DARK_FILL = {
    "public": "#1B3A4E", "living": "#1B3A4E", "dining": "#1D4051", "circulation": "#14304a",
    "threshold": "#14304a", "service": "#16303F", "sanitary": "#173544", "sleeping": "#1E3547",
    "work": "#16303F", "storage": "#122A38", "outdoor": "#0E2434",
}
DARK_VOID_ROOFED = "#12293A"     # OQ 55: a loggia is covered where a patio is not
DARK_FILL_DEFAULT = "#16303F"

# ---------------------------------------------------------------- the Drawn Language
# Lifted verbatim from workbench/app/src/theme/tokens.css, which states them as lifted
# verbatim from Graphic Standard No. 1 (guidelines/the-drawn-language.html; that file and
# uploads/VISUAL-LANGUAGE.html are cited by tokens.css and exist on no reachable disk, so
# tokens.css IS the standard as far as this repository is concerned).
LIGHT = {
    # The ground. No pure white anywhere -- a highlight is reserved paper.
    "paper": "#F1EBDB",          # the sheet itself
    "paper_deep": "#E8DEC7",     # the mat: poche interiors, panels, figure margins
    "paper_mat": "#ECE4CF",      # half-step: alternating rows, hatch tile fields
    "paper_lit": "#F7F2E4",      # a reserved highlight, one step off white
    # The ink ladder -- warm graphite. "The line does the thinking."
    "coal": "#221F1A",           # cut line, glazing, small-scale poche
    "heavy": "#2E2A23",          # profile -- where mass meets air
    "ink": "#3F3A31",            # the working dark: medium line, lettering
    "ink2": "#6C6557",           # graphite: fine line, hatching, asides
    "ink3": "#8C8371",           # tertiary labels
    "hair": "#A69D89",           # hairline: construction, grids, disabled
    "rule": "#A69D89",           # framed edges, borders
    "rule_soft": "#DCD3BD",      # row rules inside a panel
    # The five duties. "Pigment settled into paper, never ink from a screen."
    "salmon": "#DBA28B",         # cut masonry -- the warm flesh of the wall
    "salmon_deep": "#C08066",    # poche in the presentation register
    "sepia": "#B3946A",          # timber and age
    "sepia_pale": "#E6D9BD",     # partition poche, pale warm fields
    "green_deep": "#6B7C5C",     # growth; and, in the margin, cleared
    "blue_deep": "#64828B",      # water
    "brick": "#AF6B50",          # brickwork -- and, in the margin, fatal
    "gilt": "#AF8D49",           # bronze, gilding: the one struck highlight
    "gilt_deep": "#8A6D33",      # gilt legible as text on paper
}

# ---------------------------------------------------------------- the line
# tokens.css, Plate III: five weights, each with a name, a duty and a pen. On screen weight
# and tone fall together -- a lighter line is lighter in tone as well as in width, the way
# graphite behaves -- so INK_FOR pairs each weight with its own step of the ladder and the
# two are never chosen separately.
LW = {
    "construction": 0.7,   # 0.13 mm -- grids, extensions, guides: left visible
    "fine": 1.05,          # 0.18 mm -- furniture, fixtures, hatching, stairs
    "medium": 1.6,         # 0.25 mm -- openings, trim, unseen edges
    "heavy": 2.4,          # 0.35 mm -- profile: where mass meets air
    "cut": 3.0,            # 0.50 mm -- the knife of plan and section; bounds all poche
}
INK_FOR = {
    "construction": LIGHT["hair"], "fine": LIGHT["ink2"], "medium": LIGHT["ink"],
    "heavy": LIGHT["heavy"], "cut": LIGHT["coal"],
}

# The wall is a body: coal skin, salmon flesh.
#
# THE PARTITION IS SEPIA AND NOT SEPIA-PALE, AND THE REASON IS SCALE. tokens.css gives
# `--poche-partition: var(--sepia-pale)`, and that token is right for the register it was
# written in -- a large-scale detail, where a pale warm field reads as a field. At the PLAN
# scale this sheet draws (13 px/ft, the standard's own `--px-per-ft`) a 4.5 in partition is
# 4.9 px of body between two 3 px cut lines, so under two pixels of fill survive, and
# sepia-pale against vellum is a difference of about eight values: measured on the rendered
# sheet, a partition read as a hollow tube -- two parallel lines with paper between them --
# beside an exterior wall that read as a solid body. A drawing that shows a bearing wall as
# mass and a partition as an absence is saying something the record does not.
#
# `--sepia` is the standard's own "timber & age: wood, masonry hatch, warm wash", which is
# what a partition in this corpus's frame houses IS, so this is a choice BETWEEN the
# standard's named duties and not a new colour. It is a judgment about a register the
# standard states for one scale and this sheet draws at another, and it is recorded here
# rather than made silently in a renderer.
POCHE = {
    "masonry": LIGHT["salmon"],        # bearing walls at working scale
    "partition": LIGHT["sepia"],       # non-bearing walls: timber, at plan scale
    "partition_large": LIGHT["sepia_pale"],   # tokens.css's own, for a detail register
    "figure": LIGHT["coal"],           # footprints at site scale; the parti
}

DASH = {
    "hidden": "7 4", "centre": "14 4 2.5 4", "extent": "1.5 5", "grid": "none",
}

# ---------------------------------------------------------------- the letter
# "The sheets speak in letterspaced roman capitals, quietly. One serif family at four
# pitches -- never bold beyond 600, never condensed, never slanted. Emphasis is achieved by
# spacing and size, as on a carved frieze. Courier for token names, hex values, counts and
# ids -- the typewritten margin."
FACE = '"EB Garamond","Cormorant Garamond","Iowan Old Style",Georgia,serif'
MONO = '"Courier Prime","Courier New",ui-monospace,monospace'
TRACK = {
    "title": ".18em", "drawing": ".42em", "room": ".3em", "eyebrow": ".24em", "caps": ".22em",
}

# ---------------------------------------------------------------- the face, carried (WP-11.5)
# THE STACK ABOVE IS A REQUEST AND NOTHING IN THIS SYSTEM HAD EVER ANSWERED IT. Every sheet
# named EB Garamond and carried no font, so an exported SVG was set in Georgia -- or, on a
# machine without that either, in whatever the browser reached for -- and the diagnosis that
# opened Phase 11 read three typefaces on one plate for exactly that reason. The subset is
# built by `build/gen_sheet_font.py` and committed under assets/generated/; this reads it and
# nothing here needs fontTools, a network, or anything outside the standard library.
#
# ABSENCE IS A STATE AND NOT AN ERROR. A tree with no asset draws in the fallback stack and
# the sheet's own margin says so -- `face_status()` is what the title block prints. Silence
# would be the OQ 52 shape in the typography: a sheet asserting a face it does not carry.
import json as _json
import os as _os

_ASSET_DIR = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
                           "assets", "generated")
_FONT_B64 = _os.path.join(_ASSET_DIR, "eb-garamond-sheet.woff.b64")
_FONT_META = _os.path.join(_ASSET_DIR, "eb-garamond-sheet.json")
_FONT = None


def font_asset():
    """The embedded face and its provenance, or None. Cached: the payload is 20 KB of base64
    and a drawing set renders ten sheets in one process."""
    global _FONT
    if _FONT is None:
        if not (_os.path.exists(_FONT_B64) and _os.path.exists(_FONT_META)):
            _FONT = False
        else:
            with open(_FONT_META, encoding="utf-8") as fh:
                meta = _json.load(fh)
            with open(_FONT_B64, encoding="utf-8") as fh:
                meta["base64"] = fh.read().replace("\n", "")
            _FONT = meta
    return _FONT or None


def face_status():
    """What the sheet is actually set in, for the margin to print.

    Two states and never a silence: EMBEDDED names the face and its version, FALLBACK says
    plainly that the reader's own machine chose."""
    a = font_asset()
    if not a:
        return ("FALLBACK", "NO FACE IS CARRIED — THIS SHEET IS SET IN WHATEVER SERIF THE "
                            "READER'S MACHINE HAS")
    return ("EMBEDDED", f'{a["family"].upper()} {a["version"].upper()}, {a["glyphs"]} GLYPHS '
                        f'SUBSET AND CARRIED IN THIS FILE ({a["base64_bytes"] // 1024} KB)')


def font_face_rule():
    """The `@font-face` for the sheet's own <style>, or "" where no asset is committed.

    The licence travels with the font, which is what the SIL OFL requires of anything that
    redistributes it: the copyright and the licence URL are in the CSS as a comment, and the
    full text is beside the asset as assets/generated/eb-garamond-OFL.txt."""
    a = font_asset()
    if not a:
        return ""
    return (f'/* {a["copyright"]} — SIL Open Font License 1.1, {a["license_url"]}; '
            f'full text at {a["license_file"]} */'
            f'@font-face{{font-family:"EB Garamond";font-style:normal;font-weight:400;'
            f'src:url(data:font/woff;base64,{a["base64"]}) format("woff")}}')


def advance_widths():
    """{character: advance in em} for the face the sheet is drawn in, or None.

    `workbench/app/src/sheet/label.js` measures the real glyphs in a canvas and always has.
    `build/render_plan.py` had a five-branch estimate instead -- "uppercase or a digit -> 0.66
    em" -- which is a guess about a face it did not carry, and in EB Garamond an `I` is 0.34
    em against a `W`'s 0.916. One number for a three-to-one spread."""
    a = font_asset()
    return a["advance_widths_em"] if a else None

# ---------------------------------------------------------------- the sheet as an object
# "Nothing sits flush to the sheet edge: the drawing lives inside a ruled border, and the
# border inside a margin."
SHEET = {
    "margin": 26.0,        # paper edge to the ruled border
    "border_pad": 18.0,    # border to anything drawn inside it
    "gap": 58.0,           # between two level plates
    "title_h": 58.0,       # the title block's band inside the border, under the drawing
}

# The two registers (ruled 4 Sep 2026). A presentation sheet carries the drawing and its
# names; a working sheet adds the dimension strings, the divergence marks and the relaxation
# triangles. Both come from one renderer and the plate says which it is, because a printed
# plate leaves its page prose behind and a reader then cannot tell one from the other -- the
# same argument WP-6.4 made for naming the engine on the plate rather than beside it.
REGISTERS = ("presentation", "working")


def dark_style_block(pal=None):
    """The <style> the three dark renderers share, byte for byte as they each wrote it.

    render_section.py and render_elevation.py build their own on top of these five rules and
    render_plan.py added four drawing classes; only the common head is here, so a caller
    still states what its own sheet draws."""
    p = pal or DARK
    return (f'text{{font-family:"Archivo",-apple-system,"Segoe UI",sans-serif;fill:{p["ink2"]}}}'
            f'.nm{{font-size:9.5px;fill:{p["ink"]}}}'
            f'.dm{{font-size:7.5px;fill:{p["ink3"]};font-family:ui-monospace,Menlo,monospace}}'
            f'.hd{{font-family:"Bodoni Moda",Georgia,serif;font-size:19px;fill:{p["ink"]}}}'
            f'.lb{{font-family:ui-monospace,Menlo,monospace;font-size:8.5px;letter-spacing:.14em;'
            f'fill:{p["ink3"]}}}')


def pen(weight):
    """A stroke as the standard states it: a weight and the tone that falls with it.

    Returned as a dict of SVG attribute names so a caller writes the pair together and
    cannot pick a width from one rung and an ink from another."""
    return {"stroke": INK_FOR[weight], "stroke-width": LW[weight]}


def pen_attrs(weight, dash=None):
    """`pen()` as an attribute string, for the renderers that build SVG by f-string."""
    p = pen(weight)
    d = f' stroke-dasharray="{DASH[dash] if dash in DASH else dash}"' if dash else ""
    return f'stroke="{p["stroke"]}" stroke-width="{p["stroke-width"]}"{d}'


if __name__ == "__main__":
    import json
    print(json.dumps({"dark": DARK, "light": LIGHT, "weights": LW, "poche": POCHE}, indent=1))
