# oq/no-sideways-scroll-at-1280-with-the-assistant-open — the width ruling was measured with the assistant folded, and sixteen pages still scroll inside themselves when it is open

*Status: OPEN · Raised in: WP-14.30 (25 September 2026)*

**The ruling.** On 25 September Lucas ruled that the reading surfaces reflow so that nothing scrolls
sideways at 1280 px, and that the drawing surfaces keep a floor with the masthead held to the
window. WP-14.30 built it (`docs/reports/wp-14.30-the-floor-is-where-the-drawing-is.md`):

- `#root`'s 1380 px floor is gone;
- the reflow and floor lists live in `state/layout.js`;
- the three drawing surfaces keep an 800 px floor on `<main>`'s grid column.

**What was measured.**

| At 1280 × 800 | Before | After |
|---|---|---|
| Document scroll, reflow and floor pages | +100 px | 0 px |
| Masthead width | 1380 px | 1280 px |
| `<main>`, assistant folded (the default below 1500 px when nothing is stored) | — | 1018 px |

**What was not ruled.** A reader who opens the assistant at 1280 gives `<main>` 700 px. Then:

- The three floored pages scroll 100 px inside `<main>`. That is the floor working as ruled.
- **16 of 39 reflow addresses also scroll sideways inside `<main>`**: the dossier's section strip, the
  Faults filter strip, the fault detail, the family-tree plot, and the kit table.

The walk prints these 16 and does not judge them. The question is whether the ruling means
"at 1280 with the shell as it opens" (met) or "at 1280 whatever the reader has opened" (not met).

## What each answer would change

1. **As the shell opens.** The ruling is met. The walk's report of the assistant-open case stays
   informational. Nothing moves.
2. **Whatever is opened.** Each of the 16 needs its own reflow: a wrapping strip, a stacked detail,
   a narrower plot, or a kit table that drops to a list. The walk's report becomes a judged check.
   This is a package of its own, and the kit table is the hard one.
3. **The assistant cannot be opened below some width.** It would open as an overlay instead of
   taking a column. That is a shell change to `state/layout.js` and `RailHost`.

## Meanwhile

Answer 1 is what is built. The walk prints the assistant-open residue on every run, so the number
can be watched even though nothing fails on it.
