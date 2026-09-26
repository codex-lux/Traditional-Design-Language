# oq/a-refusal-is-drawn-in-two-inks-and-one-is-a-traditions-hue — the refused mark is brick, every refusal card is violet, and violet is North America's hue

*Status: CLOSED 26 September 2026 (WP-14.33) — answer 1, a refusal is brick everywhere · Raised in: WP-14.29 (25 September 2026)*

**The finding.** WP-14.29 gave every mark one meaning, and one meaning still has two inks.
`docs/prd/phase-14-tranche-2.md` §D names the refused mark's form as a *"brick outline"*, and
`workbench/app/src/theme/tokens.css` now declares `--mark-refused:var(--brick)`, drawn as a heavy
open square beside the masthead's refusal word (and wherever `JudgmentMark` is handed the
`refused` state, which no surface does yet). Every OTHER refusal on screen is drawn in `--refusal`, which the same stylesheet declares as
`var(--violet)`: the refusal card, the conflict set, the assistant's refused turn, the Drawing Set's
refused plate, the journey bar's refused step, the sheet's refusal banner, the candidate set's
refusal notes and the export's blocked note. Measured on this tree, shipped code reads
`var(--refusal)` thirteen times, twelve of them a refusal and one the atlas's note that a finer
coastline could not be fetched, which is a failure to load and not a refusal at all. So a reader
meets a refused placement as a brick square in the masthead and a violet rule on the page it links
to.

**And violet is a tradition's hue.** The five tradition swatches are the five quiet colours of the
palette, byte for byte: `--t0` is `--sepia`, `--t1` `--green`, `--t2` `--blue`, `--t3` (since this
package) `--salmon`, and `--t4` is `#837D91`, which is `--violet` -- the ink `--refusal` names. Every
North American style on the family tree and the atlas is drawn in the colour of a refusal. That is
the shape the 25 September ruling removed for `--t3`, which was the brick of the UI's fatal; the
ruling named `--t3` alone and this package changed nothing else.

## What each answer would change

1. **Refusal is brick everywhere.** `--refusal` becomes `var(--brick)`, so the mark and the cards
   agree and a refusal reads as the drawing's fatal, which is how `CLAUDE.md` describes it. Violet
   is then a tradition's hue and nothing else. The cost: brick carries the fatal severity, the
   failed verdict and the forbidden variant already, and a refusal is none of those.
2. **Refusal is violet everywhere.** `--mark-refused` becomes `var(--refusal)`, which reverses the
   PRD's own table, and `--t4` must move off violet to a palette ink no duty holds -- and the
   standard admits no new colours, so there may be none left to take.
3. **Leave the two inks, stated.** The mark is a verdict square and the card is a surface; the key
   says what the square means and the card says it in words. `--t4` stays violet.

Each is a ruling about the standard rather than a defect with an obvious repair, which is why this
package left both inks as they were.

## Related

- `oq/one-duty-per-hatch` -- the ruling this follows, closed by WP-14.29.
- `docs/reports/wp-14.29-one-meaning-per-mark.md` -- the package that found it.

## Ruled and executed 26 September 2026: answer 1 (WP-14.33)

Lucas ruled that **a refusal is brick everywhere**. `--refusal` is `var(--brick)` in
`workbench/app/src/theme/tokens.css`, the same ink as `--mark-refused`. A refused placement now
reads the same on the masthead's mark and on the card, banner and plate it links to. It reads as
the drawing's fatal, which is how the corpus already describes a refusal. Violet is `--t4` and
nothing else.

- **The one non-refusal use of the token is gone.** The atlas's note that a finer coastline could
  not be fetched was a failure to load and never a refusal. It is set in `--ink` now, one step
  heavier than the pending note's `--ink-2`, so the two states stay apart.
- **The guard is `src/marks.test.mjs`.** Reading the stylesheet's own values, it holds three
  things: `--refusal` and `--mark-refused` resolve to one ink; that ink is the brick; and no
  `--t0`..`--t4` resolves to it. Driven three ways: the old violet, a shared non-brick ink, and a
  tradition in brick. Restoring `--refusal:var(--violet)` turns it red, *"a refusal is drawn in
  two inks"*.
- **The cost the entry named is accepted.** Brick now carries the fatal severity, the failed
  verdict, the forbidden variant and the refusal. They are four duties -- five, WP-14.33's audit
  corrected: `--kind-invented` resolves to it as well -- and they are told apart
  by form and by word, never by colour alone, which is WP-14.29's rule.
- **The printed plates were checked and need nothing.** No renderer in `build/` names violet or its
  hex, so the Python sheet had no second refusal ink to move.
