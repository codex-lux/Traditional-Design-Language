# oq/the-canon-axis-counts-two-grains-as-one — "23 could not be evaluated" out of a denominator of 10

*Status: OPEN · Raised in: the adversarial audit of WP-11.9, WP-11.10 and WP-11.11 (7 September 2026)*

`compose._axis_canon` returns, on `tidewater-georgian-careful`:

```
{'share': 1.0, 'of': 10, 'clean': 10, 'flagged': 0, 'unjudged': 23}
```

Full marks, and twenty-three of ten could not be evaluated. The two numbers are counted over
different populations:

- **`of`** counts each declared slot, each **GROUPING**, each evaluated constraint and the massing.
  Four groupings on this plan, so four opportunities.
- **`unjudged`** counts canon-layer `info` findings, which the grouping layer emits one per
  **INTERNAL RULE** — and four groupings carry 86 internal rules between them.

The function's own docstring says *"Not per room: per RULE"*, which is true of the numerator and
false of the denominator. The mismatch is as old as that sentence.

**WP-11.9 made it visible and did not cause it.** Making the 28 silent `strong`/`preferred`
grouping rules speak took the reported figure from 15 to 23 on this plan and 12 to 19 on
`spec-builder-colonial` — a real improvement in what the corpus says about itself, arriving as a
worse-looking number on the card. The function's own comment already records a prior bug of
exactly this shape ("the workbench read '17 canon could not be evaluated' where the true figure
was 13").

**The score does not move.** `info` is excluded from both halves of the fraction, in this axis and
in `_axis_from_layers`; verified by suppression, and `tests/test_score.py` is green. Only the
number a reader sees is wrong.

## What is being asked

Which grain should the canon axis be counted on?

- **Per rule** — what the docstring says. Honest, and it CHANGES `share` on every candidate and
  re-ranks every shipped brief, because a grouping carrying twenty rules would stop being worth
  the same as a declared slot. That is a scoring decision.
- **Per grouping** — what the code does. Then `unjudged` must be counted per grouping too, which
  loses the count of rules nobody could run, which is the number the reader actually wants.
- **Both, named** — what is built today as a holding measure: `share` and `of` untouched,
  `unjudged` published with an `unjudged_of` sentence naming the population it was counted over.

## What must not be done to close it

- **Do not clamp `unjudged` to `of`.** It would make the card read correctly by discarding the
  count, which is the flattering direction: a reader would see "10 of 10, none unjudged" over 23
  rules nobody ran.
