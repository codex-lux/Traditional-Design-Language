# oq/the-prover-draws-a-centre-passage-that-does-not-go-through — the type's facts became hard and the through-axis stopped being drawn

*Status: OPEN · Raised in: the merge of Phase 13 into the second Phase 11 line (17 September 2026)*

**On the merged tree the PROVER draws `tidewater-georgian-careful`'s centre passage 17.00 ft wide
and 22.00 ft deep in a 45 x 37 ft main block — stopping fifteen feet short of the back wall — so
`axis.spine` returns COULD NOT EVALUATE with the reason *"no placed circulation room reaches the
boundary at both ends, so the house has no through-axis to be off"*. Main's prover draws the same
house's passage 10.00 x 37.00, spanning, and the reader says `on-centre`. A centre-passage house
whose passage does not go through is the thing the axis vocabulary was written to catch, and this
is the first time anything has looked at the PROOF and seen it.**

## The measurement

`engine="cp"`, `time_limit_s=60`, on `git archive` checkouts of both parents and on the merged
tree. Ground-floor rectangles, `x / y / width / depth`:

| tree | block | passage | porch | stair | `spine` |
|---|---|---|---|---|---|
| main `9eb71c4` | 45 x 37 | 21.00 / 0.00 / **10.00 / 37.00** | 31/0/14/6 | 31/27/14/10 | **on-centre** |
| this branch `ed5ef72` | 45 x 37 | 18.00 / 0.00 / **17.00 / 22.00** | 35/0/10/7 | 35/7/10/11 | could-not-evaluate |
| **merged** | 45 x 37 | 18.00 / 0.00 / **17.00 / 22.00** | 35/0/10/7 | 35/7/10/11 | could-not-evaluate |

**The merged placement is byte-identical to this branch's**, so the merge did not cause it — it
made it visible, because the guard that asks the question is main's and this branch had none.

**It is not the budget.** At the 40 s batch default the solve returns FEASIBLE on this box (three
runs); at 60 s and at 90 s it closes **OPTIMAL**, in 21.2 s and 18.0 s, and the spine reads
COULD NOT EVALUATE in every one of the five runs. A closed proof draws a passage that does not go
through.

## What is likely doing it, and why that is a guess

WP-13.3 made the type's facts HARD on the prover in a stated precedence, and WP-13.5's container
took the main block to 45 ft. A passage 10 ft wide in a 45 ft block leaves two 17.5 ft strips; at
17 ft it leaves two 14 ft strips. Which of the seven ranks prefers the wider, shorter passage has
NOT been established here — the room's own proportion band admits both (22/17 = 1.29 and
37/10 = 3.70, against `centre-passage`'s stated ceiling of 5.0), so the band is not deciding it.
**Naming the rank is the first piece of work and it is not done**; this entry records the
measurement, not the cause.

## The question

**Should the through-axis be a fact of the type on the prover, as tiling, stacks, bearing
continuity and the hearth already are?**

WP-11.3 swept a `centre_bay_score` and deleted it, with the finding that *"a door in the centre
bay is a property of a plan organised about an axis, not of a placement scored for one"* — and
that argues the same way here: a spanning passage is a property of the diagram. But the whole of
WP-13.3 is the ruling that the type's facts belong in the HARD set rather than in a score, and a
centre passage that does not reach the back wall fails the parti's own account of itself more
plainly than a stack that misses by a foot. The two readings are not reconciled.

Three things would have to be settled first, and none is:
1. **Which rank is choosing the wider passage.** Until that is measured, any constraint added is
   aimed at a mechanism nobody has identified.
2. **What the fact IS.** "Reaches the boundary at both ends" is `axis.spine`'s own test and is a
   reading of the drawn rectangle; whether the hard form is that, or the room's declared
   `exterior_walls` naming an opposite pair, is a modelling choice with different failure modes.
3. **Whether it can co-hold.** WP-11.7 measured a centred passage INFEASIBLE in 0.9 s with every
   wall pin already released, because a 10.2 ft passage centred on a 60 ft front left two strips
   holding 2,000 sf of programme in 1,992 sf of floor. That was a different footprint and the
   figure does not transfer, but the shape of the risk does.

## What must not happen

- **Do not re-point the guard at the SEARCH.** The search reads `could-not-evaluate` on this
  record too and for a different reason (WP-11.17's entry: the passage stands behind its own
  porch). A guard moved onto the engine that also fails proves nothing about either.
- **Do not widen `axis.spine`'s tolerance** or loosen its both-ends test to make the verdict
  return. The reader is right; the placement is what moved.
- **Do not quote this branch's figures as the merge's cost.** They are identical across the merge
  and the table above is the evidence.
