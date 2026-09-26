# oq/the-link-ink-reads-below-aa — every link in the workbench is set in an ink that falls short of the common legibility floor

*Status: CLOSED 26 September 2026 (WP-14.33) — answer 2, links are set in ink with the gilt underline · Raised in: WP-14.16 (25 September 2026)*

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

## Ruled and executed 26 September 2026: answer 2 (WP-14.33)

Lucas ruled that **links are set in `--ink` with the gilt underline.** No colour value changed.

**The tokens.** `--link`, `--link-hover` and `--link-on-paper` resolve to `--ink`, and
`--link-underline` stays the gilt hairline. The new `--link-underline-hover` (`--gilt-deep`)
makes the underline a full gilt rule on hover. On each paper, `--ink` reads:

| Paper | Contrast |
|---|---|
| `--paper` | 9.48 : 1 |
| `--paper-mat` | 8.90 : 1 |
| `--paper-deep` | 8.44 : 1 |
| `--paper-lit` | 10.09 : 1 |

**The elements, found by what they draw rather than by a list.**

- Nine link-styled buttons and spans drew the link underline under `--gilt-deep` text, in
  `AiRail`, `FindingRow`, `ShortcutCard`, the atlas (two), the bench's filter clear, the family
  tree (two) and the chrome's filter clear. All nine take `var(--link)` now.
- Three anchors set their own `--gilt-deep` over the `a` rule's ink: the dossier's
  corpus-faults link, and its two head links. All three take `var(--link)`.
- The current pack in the Proportions index was told by gilt text. It is told by a 2 px gilt
  underline now, as the two-spine map already tells the current page.
- The candidate set's "open in the workbench" navigates. It is a link now, with the underline.

**The guard is `src/inks.test.mjs`, in three parts.**

1. `--link` must read 4.5 : 1 or better on all four papers, and the `a` rule must be underlined in
   the gilt.
2. Every style block in `src` that draws `var(--link-underline)` must set its own text colour, and
   every ink that colour can take, both arms of a conditional included, must read 4.5 : 1 on
   `--paper`.
3. Every colour an anchor sets for itself is held to the same floor.

Each part was driven by mutation: `--link` back to gilt, one button back to gilt, one anchor back
to gilt. All three went red.

**The remainder, stated.** Eighteen elements still set `--gilt-deep` text that is not a link:

- eyebrows and labels in `FaultCard`, `SlotRow`, `FindingRow`'s class tag, `ToolTrace` and
  `ProvenanceTrace`;
- three controls that act in place (a fold toggle, `revoke`, a slot chip).

They read 4.09 : 1 on paper, which is the same shape, and they are not links, which is what was
ruled. The WP-14.33 report names them. A ruling on gilt as a text ink at all would move them.
