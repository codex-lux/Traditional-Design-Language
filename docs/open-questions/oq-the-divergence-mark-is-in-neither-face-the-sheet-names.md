# oq/the-divergence-mark-is-in-neither-face-the-sheet-names — one character, and the sheet cannot supply it

*Status: OPEN · Raised in: WP-11.5, the face (5 September 2026)*

**OPEN — `∗` is the mark a working sheet puts on every room drawn at a size the record does not
declare, and it is in neither font the sheet names.**

Measured, on the two faces Graphic Standard No. 1 states and `build/sheet_style.py` spells:

| stack | first family | cmap entries | has `∗` U+2217 |
|---|---|---|---|
| `FACE` (`.nm` room names, `.hd` the plate title) | EB Garamond 1.003 | 2,091 | **no** |
| `MONO` (`.dm` dimension strings, `.lb` the margin schedule) | Courier Prime 3.018 | 383 | **no** |

`∗` is U+2217 ASTERISK OPERATOR — a mathematical operator, not the typographic asterisk
U+002A, which both faces carry. Every other character the shipped sheets draw is supplied by
the first family of its own class's stack; this is the only gap, and it is on the one symbol
the sheet defines in its own margin (*"23 ROOM(S) DRAWN AT A SIZE THE RECORD DOES NOT DECLARE,
MARKED ∗"*).

**It renders today, and that is the problem rather than the reassurance.** Chromium draws it by
falling past both declared stacks into a system font, so on this machine the mark appears — in a
third face, at a different weight, in the middle of a Courier string. On a machine whose fallback
chain has no U+2217 it is a box. Either way the plate carries a face nobody chose, which is the
"three typefaces on one plate" complaint that opened Phase 11, at one character instead of a
whole sheet.

**WP-11.5 did not change the mark, deliberately.** The symbol is the standard's, and a renderer
quietly swapping a glyph the standard chose is the same class of edit as a checker reconciling
two records by picking the number that makes it green. The generator RECORDS the gap
(`assets/generated/eb-garamond-sheet.json`, `missing_from_source`) and
`tests/test_sheet_font.py::test_the_divergence_mark_is_in_neither_face_the_sheet_names` pins it
as a SET, so it cannot grow in silence.

**What a ruling has to settle.**

1. **Whether the mark changes.** `*` (U+002A) is in both faces and in every font anyone has;
   `†` is in EB Garamond and not in Courier Prime; a drawn mark (a small triangle or bar, as
   the relaxation △ already is) is in no font at all and is therefore in every reader's hands.
   The third is the only option that cannot fall back, and it is the largest change.
2. **Whether the sheet may name a character no face it carries can draw.** Stated as a rule this
   is checkable and would have caught this before it shipped: every character a renderer emits
   must be supplied by the first family of the stack it is emitted in. `tests/test_sheet_font.py`
   holds the SERIF to that today and cannot hold the MONO to it, because Courier Prime is not
   committed and Courier New cannot be inspected from here at all.
3. **Whether the mono face is carried too.** Courier Prime is OFL and a subset is about 9 KB
   base64 on top of the serif's 20 — the sheet is 43 KB before either. That would make the
   answer to (2) enforceable for both stacks rather than one, and it is the reason the question
   is worth a ruling rather than a patch.
