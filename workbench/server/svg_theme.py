"""Dark-instrument SVG → The Drawn Language, by literal substitution.

build/render_{plan,elevation,section,roof}.py each carry their own dark PAL dict
(deliberately duplicated — every build/ script runs standalone), and their SVG output
inlines those hex values. Rather than teaching four renderers a palette parameter
(noted as future work in the WP-5.2 report), the workbench re-tokenizes the finished
SVG: a hex→hex map from every value those files emit to Graphic Standard № 1's
tokens. The geometry is untouched — same lines, same coordinates; only the ink
changes, which is exactly the two-registers rule: re-render, never redraw.

The mapping is EDITORIAL (a judgment about which Drawn Language duty each dark tone
was performing), recorded here value by value so it can be argued with.
"""
import re

HEX_MAP = {
    # grounds
    "#0B1B29": "#F1EBDB",   # ground → vellum: the sheet
    "#0F2536": "#F7F2E4",   # paper → vellum-lit: the drawing field
    "#16344A": "#ECE4CF",   # elevation wall plane → vellum-mat
    "#24455E": "#A69D89",   # rule → hairline: grids, guides, left visible
    # inks (light-on-dark → warm graphite ladder)
    "#EDE7DA": "#3F3A31",   # ink → ink
    "#9FB3C2": "#6C6557",   # ink2 → graphite
    "#63808F": "#A69D89",   # ink3 → hairline (quiet text)
    # accents: building materials age into their Drawn Language duties
    "#D8B26A": "#8A6D33",   # brass → gilt-deep: instruments, windows-in-plan
    "#7FB3A3": "#6B7C5C",   # verdigris → green-deep: doors, cleared
    "#C4734A": "#C08066",   # copper → salmon-deep: serious, relaxations
    "#C4553A": "#AF6B50",   # iron → brick: fatal
    "#2E5468": "#221F1A",   # glass → coal: glazing reads coal, one caught light
    "#3A5A47": "#6B7C5C",   # shutter → green-deep
    # render_plan.py's function-class room fills → pale warm washes on vellum
    "#1B3A4E": "#EDE4CD",   # public / living
    "#1D4051": "#EAE0C6",   # dining
    "#14304a": "#F0EAD8",   # circulation / threshold
    "#16303F": "#E8E2D2",   # service / work
    "#173544": "#DDE0D4",   # sanitary — a breath of the water blue
    "#1E3547": "#ECE2CF",   # sleeping
    "#122A38": "#E6DFCE",   # storage
    "#0E2434": "#E3E2CB",   # outdoor — pale lawn
}

FONT_MAP = {
    '"Archivo"': '"EB Garamond"',
    '"Bodoni Moda"': '"EB Garamond"',
    "ui-monospace,Menlo,monospace": '"Courier Prime",ui-monospace,monospace',
    "ui-monospace, Menlo, monospace": '"Courier Prime", ui-monospace, monospace',
}


def retokenize(svg: str) -> str:
    # hex values appear in both cases in the renderers; normalise the lookup
    lookup = {k.lower(): v for k, v in HEX_MAP.items()}
    svg = re.sub(r"#[0-9A-Fa-f]{6}", lambda m: lookup.get(m.group(0).lower(), m.group(0)), svg)
    for a, b in FONT_MAP.items():
        svg = svg.replace(a, b)
    return svg
