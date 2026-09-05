#!/usr/bin/env python3
"""gen_sheet_font.py -- the sheet's own face, subset and carried with the drawing (WP-11.5).

Graphic Standard No. 1 asks for one serif voice in letterspaced roman capitals and names it:
EB Garamond. Every sheet this system has ever produced ASKED for it in a `font-family` stack
and carried no font, so an exported SVG opened anywhere but a machine with EB Garamond
installed was set in Georgia or in whatever the reader's browser reached for -- and the
diagnosis that opened Phase 11 read three typefaces on one plate for exactly that reason.

This subsets the face to what a sheet draws and writes it beside the corpus as base64, with
its licence. `build/sheet_style.py` embeds it in the sheet's own `<style>`; nothing at render
time needs fontTools, or a network, or anything outside the standard library. **This script
is the only thing in the repository that needs `fontTools`, and it runs by hand, not in the
build** -- the artefact it writes is committed.

    python3 build/gen_sheet_font.py --fetch          # from Google Fonts, over the network
    python3 build/gen_sheet_font.py --source f.ttf   # from a file you supply
    python3 build/gen_sheet_font.py --check          # rebuild into memory, compare, write nothing

WHAT IT WRITES, all under assets/generated/:
  eb-garamond-sheet.woff.b64   the payload, wrapped, one line of 76 columns
  eb-garamond-sheet.json       the sidecar: provenance, the charset, the characters the
                               SOURCE FONT DOES NOT HAVE, and the advance width of every
                               glyph in the subset
  eb-garamond-OFL.txt          the SIL Open Font License 1.1, as the licence requires

WOFF AND NOT WOFF2, AND NOT THE TTF, AND THE REASON IS MEASURED. Printable ASCII plus this
file's own extras is 26,280 bytes as a TTF (35,040 base64) and 15,016 as WOFF (20,024), on a
sheet that is 43 KB before the font. WOFF2 would be smaller again and needs the Brotli
extension, which is not installed here; WOFF's compression is zlib and is in the standard
library, so the artefact can be verified by anything that can open this repository.

**IT DOES NOT REACH INKSCAPE AND THAT IS NOT A DEFECT OF THE FORMAT.** Inkscape resolves type
through fontconfig and does not load an `@font-face` at all, in any format -- so an embedded
face reaches every browser and no desktop drawing program. A reader who needs the sheet set
correctly in Inkscape installs EB Garamond; the sheet's own margin says which face it is
carrying, so that reader can tell.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "assets", "generated")
B64_PATH = os.path.join(OUT_DIR, "eb-garamond-sheet.woff.b64")
META_PATH = os.path.join(OUT_DIR, "eb-garamond-sheet.json")
OFL_PATH = os.path.join(OUT_DIR, "eb-garamond-OFL.txt")

# The upstream the artefact is cut from. Pinned by URL AND by the sha256 the sidecar records,
# so a rebuild that silently got a different upstream is visible rather than merely different.
CSS_URL = ("https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400&display=swap")
OFL_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl/ebgaramond/OFL.txt"

# ---------------------------------------------------------------- the character set
# PRINTABLE ASCII, WHOLE, AND NOT THE CAPITALS A SHEET HAPPENS TO DRAW TODAY. Measured over
# all sixteen shipped and reference plans in both registers, the serif classes (`.nm` room
# names, `.hd` the plate title) draw 42 distinct characters -- 32 over the two plans that
# ship -- and every one is an uppercase letter, a digit or ASCII punctuation, because both
# the room names and the plate title are upper-cased before they are drawn.
# Subsetting to those is 11,984 base64 bytes against 20,024, and it breaks the first time
# anything is set in the serif without being upper-cased first, or the first time a plan is
# named after a room that carries a lowercase word. The extra 8 KB buys a face that renders
# any name a reader can type in ASCII, and `tests/test_sheet_font.py` holds the shipped sheets
# against the subset so the claim is measured rather than assumed.
BASE = "".join(chr(c) for c in range(0x20, 0x7F))
# The typographic marks the standard and the renderers use. `∗` is here because the sheet's
# divergence mark is U+2217 ASTERISK OPERATOR -- and the source font DOES NOT HAVE IT, which
# this script records rather than passes over; see the sidecar's `missing` and the report.
EXTRA = "′″·–—×°…‘’“”∗△±≈"
CHARSET = BASE + EXTRA


def _fetch(url, what):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (TDL sheet font)"})
    with urllib.request.urlopen(req, timeout=60) as fh:
        data = fh.read()
    print(f"  fetched {what}: {len(data)} bytes from {url}")
    return data


def ttf_url_from_css(css):
    """The one `url(...ttf)` in Google Fonts' own CSS for the weight we ask for. Read rather
    than hardcoded, because the hashed filename changes with every upstream release and a
    stale literal would fetch a font whose version the sidecar then misreports."""
    import re
    m = re.search(r"src:\s*url\((https://fonts\.gstatic\.com/[^)]+\.ttf)\)", css.decode())
    if not m:
        raise SystemExit("Google Fonts' CSS carried no .ttf url -- it may now serve woff2 "
                         "only. Pass --source with a TTF instead.")
    return m.group(1)


def build_subset(raw_ttf):
    """(woff bytes, metadata). Everything the sidecar records is read off the FONT, never
    supplied here -- a provenance block a caller can type is a provenance block that can be
    wrong."""
    try:
        from fontTools import subset
        from fontTools.ttLib import TTFont
    except ImportError:
        raise SystemExit("fontTools is not installed. It is needed only to REGENERATE this "
                         "asset; nothing at render time reads it. pip install fonttools")
    src = TTFont(io.BytesIO(raw_ttf))
    names = {nid: src["name"].getDebugName(nid) for nid in (0, 1, 3, 5, 13, 14)}
    upem = src["head"].unitsPerEm
    cmap = src.getBestCmap()
    missing = [c for c in CHARSET if ord(c) not in cmap]

    opts = subset.Options()
    opts.layout_features = ["kern"]      # the sheet letterspaces caps; ligatures are not wanted
    opts.name_IDs = [0, 1, 2, 3, 4, 5, 6, 13, 14]   # keep the copyright and the licence
    opts.name_legacy = True
    opts.notdef_outline = True           # a character outside the subset must LOOK missing
    opts.drop_tables += ["DSIG"]
    # `recalcTimestamp=False`, AND IT IS THE WHOLE OF WHY THIS ARTEFACT CAN BE CHECKED AT
    # ALL. fontTools writes `head.modified` as the time of the save by default, so two builds
    # of one font from one source differ in four bytes and every hash of the output differs
    # with them -- measured, twice, before this line existed. A generated artefact nobody can
    # rebuild identically is an artefact nobody can verify, and `--check` would have been a
    # command that always says FAIL.
    sub = TTFont(io.BytesIO(raw_ttf), recalcTimestamp=False)
    s = subset.Subsetter(options=opts)
    s.populate(text=CHARSET)
    s.subset(sub)

    # THE ADVANCE WIDTHS, so the Python fitter measures the face it draws in. `sheet/label.js`
    # measures the real glyphs in a canvas; build/render_plan.py had a five-branch estimate
    # ("uppercase or digit -> 0.66") that was a guess about a face it did not have. In EB
    # Garamond an `I` is 0.32 em and a `W` is 0.98 -- a three-to-one spread the estimate
    # answered with one number.
    hmtx, best = sub["hmtx"], sub.getBestCmap()
    widths = {}
    for ch in CHARSET:
        g = best.get(ord(ch))
        if g and g in hmtx.metrics:
            widths[ch] = round(hmtx.metrics[g][0] / upem, 4)

    sub.flavor = "woff"
    buf = io.BytesIO()
    sub.save(buf)
    woff = buf.getvalue()
    meta = {
        "family": names.get(1),
        "subfamily": names.get(2) if 2 in names else "Regular",
        "version": names.get(5),
        "unique_id": names.get(3),
        "copyright": names.get(0),
        "license_url": names.get(14),
        "license_file": "assets/generated/eb-garamond-OFL.txt",
        "format": "woff",
        "source_url": None,          # filled by the caller that fetched it
        "source_sha256": hashlib.sha256(raw_ttf).hexdigest(),
        "source_bytes": len(raw_ttf),
        "subset_sha256": hashlib.sha256(woff).hexdigest(),
        "subset_bytes": len(woff),
        "base64_bytes": len(base64.b64encode(woff)),
        "glyphs": len(sub.getGlyphOrder()),
        "units_per_em": upem,
        "charset": CHARSET,
        "missing_from_source": missing,
        "advance_widths_em": widths,
        "note": ("Regenerate with build/gen_sheet_font.py --fetch. Nothing at render time "
                 "reads fontTools; build/sheet_style.py reads the .b64 and this file. "
                 "`missing_from_source` are characters this script asked for and the upstream "
                 "font does not carry -- they fall back to the next family in the stack."),
    }
    return woff, meta


def wrap_b64(woff, cols=76):
    b = base64.b64encode(woff).decode("ascii")
    return "\n".join(b[i:i + cols] for i in range(0, len(b), cols)) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", help="a TTF to subset")
    ap.add_argument("--fetch", action="store_true", help="fetch the TTF from Google Fonts")
    ap.add_argument("--check", action="store_true",
                    help="rebuild and compare against what is committed; write nothing")
    a = ap.parse_args()
    if not (a.source or a.fetch or a.check):
        print(__doc__)
        return 0
    # `--check` alone means "rebuild from the upstream this asset records and compare". It
    # implies --fetch rather than printing the docstring, which is what it did for one commit
    # and is the shape of a check that reports success by doing nothing.
    if a.check and not a.source:
        a.fetch = True

    if a.fetch:
        url = ttf_url_from_css(_fetch(CSS_URL, "the Google Fonts CSS"))
        raw = _fetch(url, "the TTF")
        ofl = _fetch(OFL_URL, "the OFL")
    else:
        raw = open(a.source, "rb").read()
        url = f"file://{os.path.abspath(a.source)}"
        ofl = open(OFL_PATH, "rb").read() if os.path.exists(OFL_PATH) else None

    woff, meta = build_subset(raw)
    meta["source_url"] = url
    b64 = wrap_b64(woff)

    print(f"  {meta['family']} {meta['version']}")
    print(f"  {meta['glyphs']} glyphs, {meta['subset_bytes']} bytes woff, "
          f"{meta['base64_bytes']} base64")
    if meta["missing_from_source"]:
        print(f"  NOT IN THE SOURCE FONT and therefore not in the subset: "
              f"{''.join(meta['missing_from_source'])} "
              f"({', '.join('U+%04X' % ord(c) for c in meta['missing_from_source'])})")

    if a.check:
        have = open(B64_PATH, encoding="utf-8").read() if os.path.exists(B64_PATH) else None
        old = json.load(open(META_PATH, encoding="utf-8")) if os.path.exists(META_PATH) else {}
        same = (have == b64) and old.get("subset_sha256") == meta["subset_sha256"]
        print("OK  the committed asset is what this script builds" if same else
              "FAIL the committed asset differs from what this script builds")
        return 0 if same else 1

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(B64_PATH, "w", encoding="utf-8") as fh:
        fh.write(b64)
    with open(META_PATH, "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    if ofl:
        with open(OFL_PATH, "wb") as fh:
            fh.write(ofl)
    elif not os.path.exists(OFL_PATH):
        raise SystemExit("no OFL text to write beside the font, and the licence requires it "
                         "to travel with the Font Software. Fetch it, or place it at "
                         + OFL_PATH)
    print(f"  wrote {os.path.relpath(B64_PATH, ROOT)}, "
          f"{os.path.relpath(META_PATH, ROOT)} and {os.path.relpath(OFL_PATH, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
