# oq/two-inks-set-as-small-text-read-below-aa — the gilt of an action and the brick of a refusal are set as small text under the floor the links were raised to

*Status: OPEN · Raised in: WP-14.33's adversarial audit (26 September 2026)*

**The finding.** R3 of 26 September 2026 moved every link's text from `--gilt-deep` into `--ink`,
because a line of small type needs 4.5 : 1 and the gilt read 4.09 on `--paper`. The ruling was about
links. Two other inks are set as small text below the same floor, and a third is at it:

| Ink | `--paper` | `--paper-mat` | `--paper-deep` | `--paper-lit` | Where it is text |
|---|---|---|---|---|---|
| `--refusal` (brick) | 3.50 | 3.29 | 3.11 | 3.72 | "refused" eyebrows, a refused export, a refused ingest, RefusalCard, the journey bar's refused step, the stair note on the sheet |
| `--gilt-deep` | 4.09 | 3.84 | 3.64 | 4.35 | the chips (`Chip`, `ActionChip`), eight controls that act in place, and 15 unconditional label colours |
| `--green-deep` | 3.78 | 3.55 | 3.37 | 4.03 | FindingRow's "assert" control |
| `--ink-2` (for comparison) | 4.85 | 4.55 | **4.32** | 5.16 | the working grey: under the floor on `--paper-deep` alone |

Computed by WCAG relative luminance from the stylesheet's own values, the way `inks.test.mjs`
computes them. The brick was violet until R2, which read 3.32 and 2.96, so R2 made it slightly
better and not good.

**What holds it today.** `inks.test.mjs` holds every clickable element whose own text can take an
ink under 4.5 : 1 BY IDENTITY: 11 rows, 8 actions and 3 chips, and no navigating control. A new one
fails until it is classed. Nothing holds the non-clickable gilt labels, or the refusal text, to a
contrast.

**Two readings of each ink, and they are not the same question.**

- **The refusal.** (a) Set a refusal's WORDS in `--ink` and keep the brick as its mark: the rule, the
  border, the masthead glyph. That is R3's own move, applied to R2's ink. (b) Darken the brick until
  it reads, which moves the colour of the UI's fatal, and so every fatal finding, with it.
- **The gilt.** (a) Set an action's text in `--ink` and mark it the way a chip is marked, by its
  border. (b) Keep the gilt as the accent of an action and accept 4.09 as a UI-component contrast
  (3 : 1), which the standard allows for a control's boundary and not for its label.

**What is also not ruled.** A navigating `ActionChip` ("go to the Plan Workbench", "go to Brief
Intake", "drawings") is a chip whose ink is `Chrome.jsx`'s own, and the clickable reader holds it as a
chip. Whether a chip that navigates is a link in the sense R3 ruled on is this question's too.
