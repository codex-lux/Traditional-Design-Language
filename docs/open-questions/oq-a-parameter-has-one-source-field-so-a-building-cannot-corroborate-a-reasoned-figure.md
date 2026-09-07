# oq/a-parameter-has-one-source-field-so-a-building-cannot-corroborate-a-reasoned-figure — Ruling A can only reach a figure that cites nothing

*Status: OPEN · Raised in: WP-11.5, closing Tranche 3 (5 Sep 2026)*

**OPEN — and it is why Europe's 280 records produced ZERO new citations under Ruling A.** A kit
parameter has one `source` field. Ruling A lets a `measured` figure carry
`source: "precedents/<id>#measurements[<n>]"`, so a figure that already cites something must have
that citation **overwritten** to gain a building. Measured across the whole corpus:

| `measured` parameters citing… | count |
|---|---|
| an INTERNAL source — a constraint id, the node's own `proportional_system typical_ratios` | **489** |
| a PRECEDENT (Ruling A, applied by hand) | 6 |
| nothing at all (the grandfathered set) | 536 |

**So Ruling A's reachable set is exactly the 536, and the 489 are closed to it.** The corpus's
most-reasoned figures — the ones whose author took the trouble to say *"adam-style proportional_system
typical_ratios: 'Columns …'"* or *"german-fachwerk.c03"* — are precisely the ones no building may
corroborate. That is backwards: a figure reasoned from the node's own constraint is exactly the figure
a surveyed building most usefully agrees or disagrees with.

**Found by adjudicating Tranche 3's candidates, and it accounts for most of them.** Twelve research
agents returned **18** `citable` candidates — a measurement stating a number in the same quantity and
unit as a kit parameter. Not one was applied:

- **Five** sit on a parameter that already carries an internal source (`english-palladian`'s two
  `ceiling_height_rule` figures, `english-baroque.column.storeys_embraced`,
  `italian-villa-vernacular.height_proportion.block_plan_ratio`,
  `german-fachwerk.height_proportion.jetty_projection`). Citing the building would delete the
  reasoning. **This question.**
- **`english-georgian.composition_parti.bay_count`** is a `set` of `[3, 5, 7]`, and
  `kit_source_agrees` compares a `range` or a scalar `value` and nothing else, so a set returns
  could-not-compare however good the evidence. Five candidates pointed at it — and two of them,
  Royal Crescent at **four** bays and Kedleston at **eleven**, say the set is incomplete rather than
  unsourced. That is a second, separate gap:
  **the mechanism cannot compare a `set`-shaped parameter at all.**
- **`cotswold-vernacular.window_lite_pattern.light_count`** [2, 5] has three candidates inside the
  band and **two of the node's own exemplars outside it** — Owlpen Manor and Grevel's House both at
  six lights. Citing the agreeing three while two contradict would be cherry-picking, so all five
  were refused and the two contradictions go to
  `oq/a-survey-contradicts-a-kit-figure-and-nothing-decides-it`.
- **One** proposes a NEW parameter (`swiss-chalet`, a 6.90 m square plan measured by building
  archaeologists during the 2001 dismantling). Ruling A is about sourcing figures that exist;
  authoring a band from one building is a different act with one building's authority.
- **One** is `german-fachwerk.jetty_projection`, which both carries an internal source AND
  contradicts (500 mm against a 400 mm ceiling) AND cannot be parsed, because the measurement
  `unit` enum has no millimetre while the kit's does.

**Three options.**
1. **A second field — `corroborates`, a list of precedent pointers, beside `source`.** The reasoning
   keeps its citation and the buildings accumulate beside it, which is what a band wants: `[20, 30]`
   corroborated by two surveyed exemplars is a stronger claim than either alone.
   `kit_source_agrees` runs over every entry and the verdicts aggregate. The cost is a schema field
   on a hot record and a checker loop where there was a scalar.
2. **Make `source` a list.** Smaller schema change, and it destroys the distinction between the
   thing a figure was DERIVED from and the thing that later AGREED with it — which is precisely the
   distinction `kind: derived` versus `kind: measured` exists to keep.
3. **Leave it.** Ruling A reaches the 536 and no more. Honest, and it caps the bench's reach at
   figures nobody has reasoned about, which is the least useful half.

Recommended: **(1)**, and not urgently — the 536 are unworked and Ruling A has six citations against
a measured ceiling of about a dozen, so the reachable set is not the binding constraint yet. It
becomes urgent the moment somebody works the 536 down, or the moment a tranche produces a
measurement for a figure a node has already reasoned about, which Tranche 3 did five times.

**And the `set` gap is smaller and sharper and may deserve fixing first**, because it is one branch
in `kit_source_agrees`: a `set` member equal to the measurement is an agreement, and a measurement
matching no member is the finding that the set is incomplete — which is exactly what Royal Crescent
and Kedleston are telling this corpus and nothing is recording.
