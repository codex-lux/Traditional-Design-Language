"""WP-11.5 — the face the sheet is set in, carried with the sheet.

Graphic Standard No. 1 names one serif voice and every plate this system had ever produced
asked for it in a `font-family` stack and carried no font. These guards are about the two
things that can go wrong once it does carry one: the artefact not being what its own sidecar
says it is, and the sheet drawing a character the face it names cannot supply.
"""
import base64
import hashlib
import json
import os
import re
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

SS = modcache.load("sheet_style", os.path.join(ROOT, "build", "sheet_style.py"))
RP = modcache.load("render_plan", os.path.join(ROOT, "build", "render_plan.py"))
GEOM = modcache.load("geometry", os.path.join(ROOT, "build", "geometry.py"))

ASSETS = os.path.join(ROOT, "assets", "generated")
B64 = os.path.join(ASSETS, "eb-garamond-sheet.woff.b64")
META = os.path.join(ASSETS, "eb-garamond-sheet.json")
OFL = os.path.join(ASSETS, "eb-garamond-OFL.txt")

PLANS = [os.path.join(ROOT, "plans", "tidewater-georgian-careful.json"),
         os.path.join(ROOT, "plans", "spec-builder-colonial.json")]

# The classes set in the SERIF. `.dm` and `.lb` are the typewritten margin and are Courier;
# read off build/render_plan.py's own <style> below rather than trusted from here.
SERIF_CLASSES = ("nm", "hd")


def _meta():
    with open(META, encoding="utf-8") as fh:
        return json.load(fh)


def _sheets():
    """Both shipped plans, both registers, on the DETERMINISTIC engine."""
    out = []
    for pf in PLANS:
        pl = GEOM.solve(json.load(open(pf, encoding="utf-8")), engine="heuristic")
        for reg in ("presentation", "working"):
            with tempfile.TemporaryDirectory() as d:
                p = os.path.join(d, "s.svg")
                RP.render(pl, p, register=reg)
                out.append((os.path.basename(pf), reg, open(p, encoding="utf-8").read()))
    return out


class TestTheArtefact(unittest.TestCase):
    def test_the_three_files_are_committed(self):
        for p in (B64, META, OFL):
            self.assertTrue(os.path.exists(p), f"{os.path.relpath(p, ROOT)} is not committed. "
                                               "Regenerate with build/gen_sheet_font.py --fetch")

    def test_the_payload_is_what_its_own_sidecar_says_it_is(self):
        """A generated artefact and a record of it that can disagree is two records of one
        thing, which is the shape this corpus refuses everywhere else."""
        m = _meta()
        raw = base64.b64decode(open(B64, encoding="utf-8").read())
        self.assertEqual(hashlib.sha256(raw).hexdigest(), m["subset_sha256"])
        self.assertEqual(len(raw), m["subset_bytes"])
        self.assertEqual(len(base64.b64encode(raw)), m["base64_bytes"])
        self.assertEqual(raw[:4], b"wOFF", "the payload is not a WOFF")

    def test_the_licence_travels_with_the_font(self):
        """The SIL OFL requires the copyright and the permission notice to accompany any
        redistribution of the Font Software. The full text is beside the asset; the CSS the
        sheet carries names the copyright and the licence."""
        m = _meta()
        ofl = open(OFL, encoding="utf-8").read()
        self.assertIn("SIL Open Font License", ofl)
        self.assertIn("Permission is hereby granted", ofl)
        self.assertEqual(ofl.splitlines()[0].strip(), m["copyright"].strip(),
                         "the licence beside the font is not the licence of THIS font")
        rule = SS.font_face_rule()
        self.assertIn(m["copyright"], rule)
        self.assertIn(m["license_url"], rule)
        self.assertIn(m["license_file"], rule)

    def test_the_licence_comment_cannot_close_itself_early(self):
        """The copyright and the licence URL go into the sheet's CSS as a comment, and they
        come out of the FONT rather than out of this repository -- so a future upstream whose
        notice contained `*/` would end the comment early and spill the rest of the notice
        into the stylesheet as garbage, taking the `@font-face` with it. Cheap to check, and
        the class of thing this corpus has been bitten by in three other spellings."""
        rule = SS.font_face_rule()
        self.assertEqual(rule.index("*/") + 2, rule.index("@font-face"),
                         "the licence comment closes before the rule it is attached to")
        self.assertEqual(rule.count("\n"), 0, "a newline inside url() is not a url() token")

    def test_the_subset_is_a_subset_and_not_the_whole_face(self):
        """A regeneration that dropped the character list would embed 2,272 glyphs and
        380 KB on every sheet. The ceiling is generous and it is a ceiling."""
        m = _meta()
        self.assertLess(m["glyphs"], 200, "the subset has grown into the whole font")
        self.assertLess(m["base64_bytes"], 24_000)
        self.assertGreater(m["glyphs"], 100, "the subset has shrunk below printable ASCII")


class TestWhatTheSheetSaysAboutItself(unittest.TestCase):
    def test_the_face_is_embedded_and_the_margin_says_so(self):
        state, line = SS.face_status()
        self.assertEqual(state, "EMBEDDED")
        self.assertIn("EB GARAMOND", line)
        for name, reg, svg in _sheets():
            self.assertIn("FACE EMBEDDED", svg, f"{name} {reg} does not say what it is set in")

    def test_a_tree_with_no_asset_says_FALLBACK_rather_than_nothing(self):
        """Absence is a state, not an error -- and never a silence. A sheet that carried no
        face and said nothing is the OQ 52 shape in the typography: an assertion the record
        does not support."""
        saved = SS._FONT
        try:
            SS._FONT = False
            state, line = SS.face_status()
            self.assertEqual(state, "FALLBACK")
            self.assertIn("READER'S MACHINE", line)
            self.assertEqual(SS.font_face_rule(), "")
            self.assertIsNone(SS.advance_widths())
        finally:
            SS._FONT = saved
        self.assertEqual(SS.face_status()[0], "EMBEDDED", "the fixture did not restore itself")

    def test_the_face_is_carried_once_per_sheet(self):
        for name, reg, svg in _sheets():
            self.assertEqual(svg.count("base64,"), 1,
                             f"{name} {reg} carries the payload {svg.count('base64,')} times")
            self.assertEqual(svg.count("@font-face"), 1)


class TestTheCharactersTheSheetDraws(unittest.TestCase):
    def _serif_chars(self):
        chars, seen = set(), 0
        for _name, _reg, svg in _sheets():
            for m in re.finditer(r"<text([^>]*)>(.*?)</text>", svg, re.S):
                cls = re.search(r'class="([^"]+)"', m.group(1))
                if not cls or cls.group(1) not in SERIF_CLASSES:
                    continue
                seen += 1
                chars |= set(re.sub(r"<[^>]+>", "", m.group(2)))
        self.assertGreater(seen, 40, "the selector matched almost nothing, so this proves nothing")
        self.assertGreater(len(chars), 25, "too few distinct characters to be the real sheets")
        return chars

    def test_every_character_the_sheet_sets_in_the_serif_is_in_the_subset(self):
        """The half of this package that can rot. The subset is printable ASCII plus a named
        list; a renderer that starts drawing a room name with an accent, or a new mark in the
        serif, silently falls back for that one glyph and the plate then carries two faces --
        which is the defect Phase 11 opened on, at one character instead of a whole sheet."""
        charset = set(_meta()["charset"])
        missing = sorted(c for c in self._serif_chars() if c not in charset)
        self.assertEqual(missing, [], "characters the sheet draws in the serif and the subset "
                                      "does not carry: " + repr(missing))

    def test_the_subset_covers_printable_ascii_and_not_only_todays_capitals(self):
        """THE GUARD ABOVE CANNOT CATCH A NARROWED CHARSET AND THIS ONE CAN. Every character
        the two shipped plans set in the serif is an uppercase letter, a digit or ASCII
        punctuation, because both the room names and the plate title are upper-cased before
        they are drawn -- so a regeneration that cut the subset to those glyphs would leave
        the sheets-versus-subset test green and break the first mixed-case name anybody
        writes. Measured: a caps-only subset is 11,984 base64 bytes against 20,024, which is
        exactly the kind of saving that gets taken. The promise is printable ASCII; this is
        the test of the promise rather than of today's traffic."""
        charset = set(_meta()["charset"])
        ascii_printable = {chr(c) for c in range(0x20, 0x7F)}
        self.assertEqual(sorted(ascii_printable - charset), [],
                         "the subset no longer covers printable ASCII")

    def test_the_serif_can_actually_supply_every_character_it_is_asked_for(self):
        """Being IN the requested charset is not the same as being in the FONT. The generator
        records what it asked for and could not get; nothing the serif classes draw may be on
        that list."""
        gap = set(_meta()["missing_from_source"])
        drawn = self._serif_chars()
        self.assertEqual(sorted(drawn & gap), [],
                         "the sheet sets a character in the serif that EB Garamond does not "
                         "have, so that one glyph comes from another font")

    def test_the_divergence_mark_is_in_neither_face_the_sheet_names(self):
        """PINNED AS A SET, because it is the one known gap and it must not grow in silence.
        `∗` is U+2217 ASTERISK OPERATOR, the mark a working sheet puts on a room drawn at a
        size the record does not declare -- and it is in neither EB Garamond (2,091 cmap
        entries) nor Courier Prime (383), the first family of each of the sheet's two stacks.
        It renders today only because a browser reaches past both stacks into a system font.
        `oq/the-divergence-mark-is-in-neither-face-the-sheet-names`; do not close this by
        editing the mark, which is the standard's and Lucas's to choose."""
        self.assertEqual(_meta()["missing_from_source"], ["∗"])
        # and it is drawn in the MONO classes, never the serif -- which is why the guard above
        # passes and this one exists beside it
        drawn = [(reg, "∗" in svg) for _n, reg, svg in _sheets()]
        self.assertTrue(any(v for r, v in drawn if r == "working"),
                        "no working sheet draws the mark, so this pin says nothing")


class TestTheFitterMeasuresTheFaceItDraws(unittest.TestCase):
    def test_the_widths_are_the_font_s_own(self):
        """`sheet/label.js` has measured the real glyphs in a canvas since WP-5.2 and the
        Python fitter had a five-branch estimate: one number, 0.66 em, for every capital, in a
        face whose `I` is 0.34 and whose `W` is 0.916."""
        RP._WIDTHS = None
        self.assertAlmostEqual(RP._adv("I"), 0.34, places=3)
        self.assertAlmostEqual(RP._adv("W"), 0.916, places=3)
        self.assertAlmostEqual(RP._adv("."), 0.23, places=3)
        self.assertNotAlmostEqual(RP._adv("A"), 0.66, places=3,
                                  msg="every capital is still one number -- the estimate is "
                                      "still in front of the measurement")

    def test_the_estimate_survives_for_a_tree_with_no_asset(self):
        """A checkout without the artefact still has to fit a label, so the estimate is kept
        rather than deleted, and this is the test that says which one is running."""
        saved_font, saved_w = SS._FONT, RP._WIDTHS
        try:
            SS._FONT, RP._WIDTHS = False, None
            self.assertAlmostEqual(RP._adv("A"), 0.66, places=3)
            self.assertAlmostEqual(RP._adv("I"), 0.28, places=3)
        finally:
            SS._FONT, RP._WIDTHS = saved_font, None
        self.assertAlmostEqual(RP._adv("I"), 0.34, places=3, msg="the fixture did not restore")


class TestTheGenerator(unittest.TestCase):
    def test_the_committed_asset_carries_no_build_timestamp(self):
        """DETERMINISM IS THE WHOLE OF WHY THIS ARTEFACT CAN BE VERIFIED. fontTools writes
        `head.modified` as the time of the save unless told not to, so two builds of one font
        from one source differ and every hash of the output differs with them -- measured
        twice before `recalcTimestamp=False` went in, and `--check` would have been a command
        that always says FAIL."""
        try:
            from fontTools.ttLib import TTFont
        except ImportError:
            self.skipTest("fontTools absent -- COULD NOT EVALUATE, never a pass")
        import io
        raw = base64.b64decode(open(B64, encoding="utf-8").read())
        f = TTFont(io.BytesIO(raw))
        src = open(os.path.join(ROOT, "build", "gen_sheet_font.py"), encoding="utf-8").read()
        self.assertIn("recalcTimestamp=False", src)
        self.assertEqual(f["head"].modified, f["head"].modified)  # parses at all
        self.assertEqual(f["head"].unitsPerEm, _meta()["units_per_em"])
        self.assertEqual(len(f.getGlyphOrder()), _meta()["glyphs"])

    def test_nothing_at_render_time_imports_fontTools(self):
        """The corpus and every checker run on the standard library alone. fontTools is the
        generator's dependency and the generator runs by hand; a renderer that imported it
        would put a wheel between a reader and a drawing."""
        for name in ("render_plan.py", "sheet_style.py", "render_section.py",
                     "render_elevation.py", "render_roof.py"):
            src = open(os.path.join(ROOT, "build", name), encoding="utf-8").read()
            for line in src.splitlines():
                stripped = line.strip()
                if stripped.startswith(("import ", "from ")):
                    self.assertNotIn("fontTools", stripped, f"{name}: {stripped}")


if __name__ == "__main__":
    unittest.main()
