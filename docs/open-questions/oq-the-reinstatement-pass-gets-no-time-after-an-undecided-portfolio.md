# oq/the-reinstatement-pass-gets-no-time-after-an-undecided-portfolio — four cores give back fewer facts than one

*Status: OPEN · Raised in: the audit of Phase 17 (30 October 2026), finding 9*

**OPEN — on a box with more than one core, a house the worker portfolio cannot decide reaches the
reinstatement pass after that pass's deadline has already passed, so not one fact the ladder released
is offered back. Every type fact released on the ladder's undecided scout stays CARRIED, and the house
is refused for all of them at once. On one core the same house reaches the pass in time and wins facts
back.** It is DISCLOSED, not fixed: the pass now writes its own line on `downgrade_rounds` saying how
many released pins it offered back and how many it never reached, and the facts account files each
one `carried` (`geometry_cp._reinstate_note`, `geometry_cp.facts_account`).

## The arithmetic

`geometry_cp._reinstate_deadline(now, started, T)` is `min(now + 0.15 T, started + 0.6 T)`: its own
share from when it starts, and never into the polish's guaranteed 0.4 T. The portfolio's undecided
steps run to `started + BUDGET_SHARE_PORTFOLIO * T` = `started + 0.75 T`, and the ladder that follows
is given a fresh `now + 0.45 T` (WP-17.5, the fix for the ladder's own starvation in the Phase 17
report §VII). So any placement the ladder returns after an undecided portfolio reaches
`_finish_feasible` at or after 0.75 T, the cap of 0.6 T is behind it, and the first `_try` returns at
once. The fix to the ladder's starvation moved the starvation onto the reinstatement pass.

## What was measured

By the audit's verifier, at T = 40 s on `briefs/family-georgian.json`'s composed candidates, a
`CpSolver.Solve` spy recording each step's start, cap and end. One run each on a shared four-core box,
so the timings are a band and not a figure to ratchet.

| candidate | workers | portfolio | the ladder places | reinstatement | polish |
|---|---|---|---|---|---|
| centre-passage-single-pile | 4 | hard1, +2 ft, +4 ft all UNKNOWN; ends 30.2 s | `r1+ H:OPTIMAL` at 38.8 s | no `R:` attempt at all | polish-a capped 4.4 s (0.11 T); polish-h skipped |
| foursquare-quadrant | 4 | the same shape; ends 30.1 s | `r1+ OPTIMAL` at 38.3 s | no `R:` attempt | polish-a 4.4 s |
| centre-passage-single-pile | 1 | does not run | `r1+ OPTIMAL` at 15.5 s | 15.5–21.5 s (0.15 T), 9 `R:` attempts, restoring `bearing element 0 x` | polish-a 10.2 s; polish-h attempted |

On the four-worker single pile the facts released on the round-1 scout -- 2 tiling, 3 stack and
2 bearing pins -- and 12 wall pins all stayed carried. On one worker the same house won a bearing fact
back. Where the portfolio is INFEASIBLE fast (the careful Tidewater record, the composed double pile,
`geometry_cp._multi_element_fixture`), the ladder starts early and reinstatement runs normally.

The disclosure was driven end to end on the two-storey fixture with the pass's window forced shut
(`tests/test_cp_portfolio.py::test_a_pass_with_no_time_left_says_so_on_the_record`): 24 released pins,
offered back 0, 24 never reached, every downgraded fact filed carried.

## The ruling it stands under

R12 of 30 October 2026, as the audit-fix task records it: the compose budget becomes a REAL ceiling --
each first placement bounded by its share, a round that cannot fit in what is left refused and said --
and **the reinstatement pass gets no share of its own**, so this finding is disclosed rather than
re-anchored. This entry exists so that the cost of that ruling is written where it can be weighed.

## What would have to be ruled to change it

1. **Re-anchor the pass's share from when it starts**, as WP-17.5 re-anchored the ladder's:
   `now + 0.15 T` wherever `started + 0.6 T` has passed. On an undecided house the wall time stacks to
   about 0.75 + 0.45 + 0.15 T before the polish, past the 1.2 T the Phase 17 report accepted, and it
   collides with R12's real ceiling and with `BUDGET_COMPOSE_S`. That is the option R12 declined.
2. **Carve the pass's share out of the ladder's own re-anchored 0.45 T**, so the wall time does not
   grow; the ladder then has 0.30 T to release ranks and place, and the ladder's starvation the
   Phase 17 report §VII fixed may return on the multi-element fixture.
3. **End the portfolio's undecided steps before 0.6 T** (`BUDGET_SHARE_PORTFOLIO` down from 0.75),
   so a ladder placement can still land inside the pass's window -- at the price of the grown-box step
   the portfolio exists for, which the composed foursquare needed 11-29 s of 60 to decide.
4. **Leave it**, accepting that on a multi-core box an undecided house keeps every released fact
   carried and is refused for all of them, while a single-core box can return the same house with
   more facts held.

## What is not known

- Whether the facts a re-anchored pass would win back would make any of these candidates drawable.
  The one-worker run won back one bearing fact; nobody measured whether the house then held its other
  facts, and the refusal names several.
- How often a composed set's candidates take this path. The two measured were both undecided on the
  portfolio; the rate over a brief's whole pool was not counted.
