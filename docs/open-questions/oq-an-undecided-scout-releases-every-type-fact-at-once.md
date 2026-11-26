# oq/an-undecided-scout-releases-every-type-fact-at-once — the ladder's answer to a model it cannot decide

*Status: OPEN · Raised in: WP-13.3, the prover learns the type (16 September 2026)*

**Where a feasibility scout comes back UNKNOWN with any of the type's facts still live,
`geometry_cp.solve_cp` releases EVERY live type fact at once, marks them CARRIED, and lets the
reinstatement pass win back what it can, highest rank first.** A conflict core releases one
rank; an undecided scout releases four. The slice chose that because the state with every fact
held is the expensive one (`tiling + stack + bearing + shape` UNDECIDED at 40 s on the reference
plan where the shape band alone is OPTIMAL in about 9 s) and a ladder that released one rank per
undecided round would spend its whole share deciding nothing.

**Measured cost, both shipped plans, 40 s, one run each** (`docs/reports/wp-13.3-the-prover-learns-the-type.md`):
the reference plan carries 21 of its wall pins where it carried 16 before the package, and every
fact; the spec Colonial carries **12 where it carried 2**, and every fact, with its residual void
35 → 54–58 sf. Both exceed `tests/test_solver.py`'s half bound, which is not loosened. The
reinstatement pass wins one wall back on the reference plan and none of the facts on either.

**What is not measured**: the alternative ladders. Releasing one rank per undecided round
(lowest first, so the walls go before the facts — which is what `_RANK` says the walls are worth),
or releasing the facts one kind at a time from the top of the ladder down, might hold more on
these records inside the same share, or might leave the scout undecided at every step; the
slice's argument for all-at-once is a measurement of the FULL model and not of the intermediate
states. WP-13.5's container edit changes the record the reference plan's figures were taken on,
so any sweep of the alternatives should run there, on both records, before this is ruled.

**What must not happen**: the half bound must not be loosened to fit the all-at-once release,
and `BUDGET_BATCH_S` must not be raised to hide it — the ladder to 90 s reached no proof.

## Amended, 29 October 2026 (Phase 17, WP-17.5)

The prover now poses every fact HARD on a worker portfolio FIRST (`geometry_cp.portfolio_workers`, the
cgroup quota, one solve at a time), with the authored walls and the axis released and the footprint grown
2 and 4 ft before a room is compromised; the assumption ladder, and with it this question's undecided
scout, runs only where the portfolio does not decide. On a quiet four-core box the composed foursquare
decides with every fact held. **The question is not answered**: where the portfolio does not decide (the
centre passages and the five-part at the compose budget) the scout still releases what it released, and
the policy sweep this question asks for was not run in Phase 17's first tranche.

## Amended 19 November 2026: the retry sweep on Lucas's Tidewater brief

The native five-part and single pile, composed once and placed as the composer's retry places them,
four draws at each of 60, 90 and 120 s on one quiet four-core container (CP under a wall clock is a
draw, not a figure): the five-part 0 of 12 placed, every refusal UNDECIDED on bearing, stacks and
tiling (once stacks and tiling); the single pile 0 of 8 at 60 and 90 s and 2 of 4 at 120 s. Every
placement is the prover's. A longer budget scales every stage's share, so it does not move the
reinstatement pass's window; on the five-part, more time bought nothing. Figures:
`docs/reports/the-refusal-that-blamed-the-brief-2026-10-30.md` §X. **Still open.**

## Amended 26 November 2026: the hard steps decide more often, and the scout is unchanged

With the line grid (`geometry_cp.LINE_GRID`) the prover's hard steps now answer on houses they left
undecided, on one worker as well as four, so fewer solves reach this scout at all. Measured over the
14 diagrams composed for `briefs/family-georgian.json`, every fact hard, four workers, 25 s a step:
2 placed, 6 proven impossible at every depth tried, 6 undecided. The six undecided still reach the
scout, and it still releases every type fact at once. The alternative ladders were not swept.
Report: `docs/reports/the-prover-decides-2026-11-26.md`. **Still open.**
