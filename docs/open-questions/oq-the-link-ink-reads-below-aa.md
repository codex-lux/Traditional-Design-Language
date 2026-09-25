# oq/the-link-ink-reads-below-aa — every link in the workbench is set in an ink that falls short of the common legibility floor

*Status: OPEN · Raised in: WP-14.16 (25 September 2026)*

**The finding.** `workbench/app/src/theme/tokens.css` sets `--link` to `--gilt-deep` (`#8A6D33`,
commented *"derived: gilt legible as text on vellum"*), and every `a` takes it. On hover a link
turns `--gilt`, which is lighter still. Measured with the WCAG relative-luminance formula:

| Ground | `--gilt-deep` | `--ink-2` |
|---|---|---|
| `--paper` `#F1EBDB` | 4.09 : 1 | 4.85 : 1 |
| `--paper-mat` `#ECE4CF` | 3.84 : 1 | 4.55 : 1 |
| `--paper-deep` `#E8DEC7` | 3.64 : 1 | 4.32 : 1 |
| `--paper-lit` `#F7F2E4` | 4.35 : 1 | 5.16 : 1 |

The common floor for body-size text is 4.5 : 1. Link text in this app is mostly 12–14 px, so every
link falls below that floor on every ground; `--paper-lit` comes closest, at 4.35. `--ink-2`, the secondary text
ink, clears it everywhere but `--paper-deep`.

**Why it is a question and not a fix.** Graphic Standard No. 1 admits no new colours, and tranche 2
changes no ink's value (`docs/prd/phase-14-tranche-2.md` §G). Every available remedy is therefore a
ruling about the standard:

1. **Darken `--gilt-deep`.** One value changes, and so does every other duty `--gilt-deep` carries
   (the accent, focus, minor severity, canonical and editorial marks).
2. **Set links in `--ink` with the gilt underline alone.** The gilt still marks a link, and the text
   reaches 9.48 : 1. Links stop being distinguishable from text by colour and are distinguished by
   the underline only.
3. **Leave it, stated.** The ink is a deliberate choice of the standard, and legibility is carried
   by size and weight.

## What tranche 2 does meanwhile

WP-14.31 moves readable text off `--ink-4` and small `--ink-3` onto `--ink-2`, and leaves the link ink
untouched, pending this ruling.
