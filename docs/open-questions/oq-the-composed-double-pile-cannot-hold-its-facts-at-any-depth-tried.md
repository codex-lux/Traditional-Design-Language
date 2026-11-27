# oq/the-composed-double-pile-cannot-hold-its-facts-at-any-depth-tried — the native Georgian diagram, proven infeasible as composed

*Status: OPEN · Raised in: Phase 17's first tranche, measuring the native diagrams (29 October 2026)*

**OPEN — `centre-passage-double-pile`, composed on Lucas's brief after Phase 17's first tranche (its
corridor and stacked rooms sized to the type, its bath's claim filed as a wet stack, its wing growing
with the house), is PROVEN INFEASIBLE by the prover with every type fact held, at the derived depth and
2 and 4 ft deeper, with the authored walls and the axis released.** The prover's portfolio returns
INFEASIBLE at every step in seconds and its assumption ladder is infeasible through three ranks. It is the
native diagram for a Tidewater Georgian brief, and the set returns borrowed diagrams in its place.

## What was measured (29 Oct 2026, one container, CP-SAT, cores not minimised)

- Main block 45 x 35 ft (five 9 ft bays), service wing 18 x 17 ft.
- **Every fact held, depth 35 ft:** a four-literal core on the butler's pantry -- its size, its 2.4:1
  band, its declared N wall and its door to the back hall.
- **Every fact held, depth 39 ft:** a four-literal core on the centre passage -- a 25.6 ft declared
  length cannot span a 39 ft house from its N wall to its S wall inside its size tolerance and its 5:1 band.
- **Walls and axis released, depths 35, 37 and 39 ft:** INFEASIBLE, with a core naming the three
  structural stacks (landing over stair hall, upper passage over centre passage, principal chamber over
  drawing room), the whole-run bearing fact on both axes of the main block, the upper floor's exact
  tiling of the main block, and the sizes and bands of every upper room.

## What a ruling would choose between

1. **Leave it refused**, as the side hall is (`oq/the-side-hall-partis-stacks-cannot-co-hold-in-band`):
   the composer passes it over and names it.
2. **Let the composer size the upper floor to the block.** The upper programme is 1,359 sf against a
   1,575 sf main block; the foursquare and the living hall, which do decide, carry the same kind of gap.
   Not shown to be the cause.
3. **Re-examine one of the three stacks.** All three are rooms over rooms, so ruling 5 does not reach
   them; any change is an authoring act on the parti.

## Not done

Nothing beyond the measurement. A minimised core is the next step, and it was not taken in this tranche.

## Amended 30 October 2026, after R13 (report §XI)

**"Proven infeasible as composed" is withdrawn.** It was true of the composition measured on 29 October.
R13 then composed the passage to the 8 ft floor its own fault convicts at, and the house changed.

Lucas's brief, compose defaults, one four-core box, nine draws:
- **One draw placed the double pile**, the morning's compose: FEASIBLE on the prover, no room over band,
  no door unplaced, hearth unjudged.
- **Eight refused it**:
  - the afternoon's compose;
  - one solve taken under load;
  - six bare first-placement solves at the compose budget's 60 s, three on `0484917` and three on
    `25f4857`, the tree before the audit's fixes.
- Of those eight, most downgraded tiling alone; some also downgraded bearing and stacks.

So the question is no longer whether the house can hold its facts. One draw shows it can. The question
is whether the prover decides it inside the compose budget on the box it runs on, which it does about
once in nine. That is the class of `oq/the-reinstatement-pass-gets-no-time-after-an-undecided-portfolio`.
The three choices above stand. A fourth is now open: a larger per-placement budget for the native
diagram, which R12's ceiling forbids at four candidates.

## Amended 26 November 2026: on the stock brief the proof is the service wing's

On `briefs/family-georgian.json` the composed double pile is INFEASIBLE in 0.3 s at each of the
three depths the prover tries, on one worker or four. Its main block holds every fact on both
storeys in 7.4 s. The conflict is the service wing's door arrangement on the hyphen's face, with the
brief's garage in the same wing, and it has its own entry:
`oq/the-double-piles-service-wing-cannot-tile-on-its-hyphens-face`. This entry's "about once in
nine" was measured on Lucas's Tidewater brief and is not re-measured here. **Still open.**

## Amended 26 to 27 November 2026: on the stock brief the house holds every fact

The amendment above put the whole proof in the service wing and said the main block held every
fact in 7.4 s. That is not reproduced. With the garage ruled its own mass, the main block alone
could not hold its facts with the range centred on its axis, at the derived depth or 2, 4 or 6 ft
deeper, on that tree or on its parent. Two more rulings followed: the one range stands against the
main block's rear wall, and the prover finds the wing's box. With both built, the composed double
pile on `briefs/family-georgian.json` holds every type fact 4 ft deeper than derived, on four
workers and on one, and the refusal is gone on that brief. The record of all four questions and
answers is `oq/the-double-piles-service-wing-cannot-tile-on-its-hyphens-face`; the runs are in
`docs/reports/the-garage-is-its-own-mass-2026-11-26.md`.

**"On four workers and on one" above is true of one placement and false of the product on one
worker**, measured after it was written. `compose(family-georgian, 4)` at four workers returned
the double pile first and DRAWABLE WHERE JUDGED on four runs of four. At one worker it came back
refused UNDECIDED (bearing, stacks, tiling) on four runs of four. The composer's declared loop
resizes thirteen rooms before the house is placed (the butler's pantry from 5.6 x 9.5 to
9.1 x 11.1 ft among them); that record, placed alone on one worker, is undecided at the derived
depth and 2 and 4 ft deeper at 60 s and again at 120 s, so a longer budget is not the lever. The
record as first composed holds every fact on one worker in 61 s. Which of the thirteen resizes
makes the difference was not measured.

**And at the 40 s batch budget on four workers it does not decide either.** The gate
(`tests/test_sheet_coherence.py`) places the composer's candidate with `engine="cp"` at that budget.
Run alone three times: twice the prover returned no placement (UNKNOWN), once a placement with
facts released. At the composer's 60 s it held on four runs of four. The 2 ft deeper step is
infeasible and slow to prove, and it runs before the 4 ft step that holds.

This entry was raised on Lucas's own Tidewater brief, which is not a file in the tree. It was not
re-measured, so the "about once in nine" above stands as the last measurement of that brief.
**Still open: for the stock brief on one worker and at 40 s, and for Lucas's brief at any worker
count.**
