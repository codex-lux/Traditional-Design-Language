# oq/the-measurement-that-defaulted-the-stacking-rule-has-inverted — the argument for STACK_HARD being off no longer holds on the plan it was made on

*Status: OPEN · Raised in: the merge of the two Phase 11s (8 September 2026)*

**`STACK_HARD` ships `False`, and the number that decided it was a 40 ft clear span. On the
merged tree that number runs the other way.**

## The measurement, both ways

`spec-builder-colonial`, `engine="heuristic"`, over-capacity clear spans from
`structure.build_section`:

| | rule OFF | rule ON |
|---|---|---|
| main, before the merge | **0** | 2 |
| merged tree | **4** | **2** |

Main's own comment states the argument the default rests on: *"at 250 candidates the strict
candidate on that same plan introduces two over-capacity clear spans where there were none, the
worst 40.0 ft against a 20 ft capacity — a structural defect on a shipped reference plan, traded
for a waste stack."*

On the merged tree the rule **removes** two spans rather than introducing two.

## Why it moved, and why that is not a fix

The rule did not change. **The baseline did.** The other branch's WP-11.8 makes each room's own
proportion band the FIRST key of the candidate acceptance, and a squarer room puts fewer cuts on
the bay module — that report measured the same trade corpus-wide, spans 11 → 23. So with the rule
off, this plan now starts at 4 over-capacity spans rather than 0, and the strict candidate's 2
is an improvement on it rather than a cost against it.

That means the comparison main made is no longer between the same two things. It is not evidence
that the rule became better; it is evidence that the plan it was measured on became worse.

## What must be ruled

1. **Does the default flip?** The stated reason for `STACK_HARD = False` is a structural cost
   this plan no longer shows. `oq/a-placement-rule-is-free-at-a-pool-the-server-cannot-afford` is
   the other half of the same decision and is open; the pool cost is unchanged by any of this.
2. **Is 4-with-the-rule-off acceptable at all?** Ruled 8 Sep 2026 as *accept and record* for the
   merge itself, on the ground that the capacity and the bearing tolerance are untouched and the
   band ranking is a ruled package. That ruling was about not blocking the merge. It is not a
   ruling that a shipped reference plan should carry four over-capacity spans.
3. **Which plan should the default be measured on?** One plan decided it. The Tidewater plan
   moved the other way at WP-11.5 ("2 spans -> 4, but the worst falls 53.9 -> 36.0"), so the two
   shipped plans have disagreed about this rule from the beginning.

## What was NOT done, and why

**The default is unchanged.** Flipping a placement rule while reconciling two branches would be
a third change hidden inside a second one, and the numbers that would justify it are exactly the
numbers the merge disturbed. `tests/test_stacking_rule.py` asserts the inversion in the direction
it now runs, with the comment naming this entry, so it cannot go quiet — and if the rule ever
introduces spans on this plan again, that assertion fails and main's original argument is live.
