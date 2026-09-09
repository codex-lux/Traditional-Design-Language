# oq/the-massing-states-its-hearth-in-prose-and-a-substring-test-reads-it — two vocabularies for one fact

*Status: OPEN · Raised in: WP-11.4, the threshold and the stacks (4 September 2026)*

**OPEN — a massing's `hearth` field and a kit's `hearth_position` slot are two vocabularies for one
fact, and one of them is prose that a substring test reads.**

`elements/slots.json` defines `hearth_position` and every kit that binds it names VARIANT IDS from
a closed list — `exterior-end`, `gable-end-paired`, `interior-paired-flanking-ridge`,
`central-stack` — fifteen of them in use across the corpus. `massings/catalog.json` states the same
fact in a free-text `hearth` field, in a DIFFERENT vocabulary of fifteen values, **seven of the
forty massings stating a DISJUNCTION in six distinct words**:

| massing | `hearth` |
|---|---|
| `hall-single-cell` | `gable-end or corner` |
| `hall-and-parlor` | `gable-end-paired or central-stack` |
| `gambrel-block` | `gable-end-paired or central-stack` |
| `side-hall-double-pile` | `party-wall or end` |
| `creole-cottage` | `central or end` |
| `shotgun` | `central or none` |
| `foursquare` | `interior or end` |

**A disjunction names two positions and chooses neither**, and two of them put the stack at
opposite ends of the plan.

**`build/roof.py::chimney_positions` reads this field with `"gable-end" in hearth`.** That answers
TRUE for `gable-end or corner` and for `gable-end-paired or central-stack`, so a massing that
declines to choose is read as having chosen. It is not a corner case: the massing is the FALLBACK
that fires wherever a node's own kit states no canonical chimney, which is **135 of 159 styles**.
Neither shipped reference plan is affected — both are `four-over-four`, whose `hearth` is the
unambiguous `gable-end-paired` — which is why nothing has ever caught it.

**What WP-11.4 did.** `build/threshold.py` carries two CLOSED TABLES, `SIDE_OF` for the kit's
variant ids and `MASSING_HEARTH` for the massing's words, each mapping a token to
`(side, at_a_gable_end, why)` with `None` meaning UNJUDGED in either column.
`build/check_threshold.py` proves both total over the corpus and fails the build on a token neither
names — it earned that on its first run, on twelve massing values written in a vocabulary the kit
slot does not use. Under those tables a disjunction is unjudged and no stack is drawn from one.

**`roof.py` IS NOT CHANGED, deliberately.** It decides a chimney's HEIGHT, changing it moves real
output on three massings, and that measurement belongs to whoever makes it. So there are now two
readings of one field in one repository, which is the shape this corpus refuses everywhere else,
and it is recorded here rather than left to be discovered.

**What a ruling has to settle.**

1. **Whether the massing may state a hearth at all**, or whether the fact belongs only in
   `hearth_position` and the massing should point at it. Two vocabularies for one fact is the
   root; everything else is consequence.
2. **What a disjunction MEANS.** "This type occurs both ways" is a true statement about a type and
   a useless one for a building. If it stays, it needs to be a list of variant ids rather than a
   sentence, so a reader can see that it is two answers.
3. **Whether `roof.py` moves onto the table.** Measured before it does: three massings change from
   placing a stack to reporting an unjudged one, on the 135 styles where the fallback fires.
