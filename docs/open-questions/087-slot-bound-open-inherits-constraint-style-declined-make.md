# OQ 87 — a slot bound `open` inherits the constraint the style declined to make

*Status: OPEN · Raised in: From the four rulings (WP-5.14, 27 Aug 2026)*

**OPEN — a slot bound `open` inherits the constraint the style declined to make.** `resolve_slots`
stops its walk only on `specified` or `forbidden`; `open` is skipped entirely and the walk continues.
So a style that says "I do not constrain this slot" gets its nearest ancestor's constraints in full,
which is the opposite of what the word means anywhere else in this corpus.

Found at `colonial-revival`'s `dormer` slot, bound `open` / `status: empty`, which therefore resolved
the whole slot from `english-cottage-vernacular`: `eyebrow-swept-dormer-within-thatch` **canonical**,
and `boxed-dormer` — the only dormer such a house is ever built with — **forbidden**, on a `c01, hard.`
A production Colonial Revival could not declare its own dormer, and the elevation generator drew a
thatched cottage's on it with full confidence. That instance is fixed (the style now binds the slot
`specified`), but the mechanism is untouched and reaches all 97 slots.

It is OQ 51's question in the kit layer rather than the proportion layer, and it should probably be
settled with OQ 51's opt-in flip rather than before it: making `open` stop the walk today would strand
every slot that is `open` and relying on the cascade, which is most of them. What is wanted first is
the count — how many `open` slots resolve to an ancestor's record, and how many of those carry a
`forbidden` the node would not have written.
