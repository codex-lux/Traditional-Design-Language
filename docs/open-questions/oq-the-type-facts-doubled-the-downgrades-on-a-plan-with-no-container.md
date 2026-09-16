# oq/the-type-facts-doubled-the-downgrades-on-a-plan-with-no-container — WP-13.3 moved two plans and named one

*Status: OPEN · Raised in: WP-13.5, the container (16 September 2026)*

**Making the type's four facts hard on the prover (WP-13.3) took `plans/spec-builder-colonial.json`
from 2 declared wall pins downgraded to 12 of 19 — over half — and `tests/test_solver.py`'s own
words for that state are "the model is no longer enforcing them and has started narrating them".
WP-13.3's status line named the same movement on the Tidewater plan and said WP-13.5's record edit
was what would change it. WP-13.5 changed the Tidewater plan and cannot change this one: the spec
Colonial names no parti, declares no massing element, and is not a house with a service dependency
to move anything into.**

Measured with `geometry.solve(plan, time_limit_s=60)` on three `git archive` checkouts, one run
each, on the machine WP-13.5 ran on:

| tree | Tidewater | spec Colonial |
|---|---|---|
| `31a7373`, before WP-13.3's prover slice | 12 of 35 ✓, 0 unvouched | **2 of 19 ✓, 0 unvouched** |
| `57e7b72`, the branch head after WP-13.3 | 21 of 35 ✗, 20 unvouched | **12 of 19 ✗, 11 unvouched** |
| WP-13.5, the record edit | 7 of 35 ✓, 0 unvouched | **12 of 19 ✗, 11 unvouched** — the head's figures, unmoved |

These are CP figures under a wall clock and are not a ratchet; the file they come from says so at
length. What is not a wall-clock artefact is the SHAPE: on the middle tree the reinstatement pass
answers UNKNOWN to seven of its restore attempts on this plan, so the pins are carried rather than
proved, and eleven of the twelve refinement notes say neither "proven" nor the words the test
recognises for "carried".

## Two questions, and they are separable

**1. Is a downgrade count above half a real verdict on this plan, or is it the budget?** The
ladder releases a whole rank per round and `_reinstate` offers the pins back one at a time inside
`BUDGET_SHARE_REINSTATE`. On the Tidewater plan, once the container made every round decidable,
the same pass proved 16 restores INFEASIBLE and answered UNKNOWN once — and the count fell to 7.
The spec Colonial's pass is still mostly UNKNOWN. So the honest reading may be that its 12 is an
UNDECIDED reading rather than a measurement, which is the state this corpus refuses to collapse
into either a pass or a failure. If so the remedy is the budget's allocation, not the record's.

**2. Or does that plan's `exterior_walls` need re-reading the way the Tidewater plan's did?**
WP-11.6 item 4's finding is that a service room declaring N/S/W is declaring the exposures of a
WING, and the Tidewater record was carrying a wing's exposures inside one rectangle for two
phases. The spec Colonial may be doing something similar with no container to move them into —
but it is a spec builder's colonial, and it may simply not be that kind of house. Nobody has
read its nineteen declared walls against its own plan.

## What must not be done

**Do not loosen `len(pins) <= declared // 2`.** It is bounded by the plan and not by the clock,
which is the one property that makes it load-independent, and `< declared` was tried and admitted
34 of 35.

**Do not re-cut the PROVEN/CARRIED literal check to match the note WP-13.3 wrote**, at least not
on its own. Eleven of the twelve notes on this plan say *"(carried — off a conflict core or an
undecided round, not individually re-proven in budget)"* and the test's constant is *"carried from
the conflict core — not individually re-proven in budget"*: a closed vocabulary that grew a third
honest case and a transcription of it that did not. That is this repository's most repeated guard
defect — a pinned literal broken by a rewording — and the fix it asks for is the one it always
asks for: read the vocabulary from `geometry_cp.py` rather than copying it. Doing only that
would turn the first red into green and leave the bound above as the visible failure, which is
the right order, but it is a guard redesign and belongs with WP-13.7's audit rather than with a
record edit.

**Do not attribute either movement to WP-13.5.** The middle row of the table is the branch head
with no edit of this package on it, and this plan's HEURISTIC placement — every room rectangle on
both levels — hashes identically across the edit, measured on a `git archive HEAD` checkout
against the working tree.
