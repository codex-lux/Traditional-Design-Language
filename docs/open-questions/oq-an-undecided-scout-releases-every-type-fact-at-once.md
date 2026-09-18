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
