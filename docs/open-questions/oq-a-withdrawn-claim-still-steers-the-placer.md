# oq/a-withdrawn-claim-still-steers-the-placer — a claim withdrawn because it cannot be judged costs three rooms their reachability

*Status: OPEN · Raised in: the merge of Phase 13 into the second Phase 11 line (17 September 2026)*

**`geometry.bias` reads `stacks_over` while the level is being SLICED, so withdrawing a claim
changes which layouts are PRODUCED and not merely which is ranked. WP-13.5 withdrew
`hallbath stacks_over powder` because the powder room had moved into a single-storey dependency,
where `stacking.judge`'s strict rectangle intersection can only ever read BROKEN — a placement
convicted of a failure no placement can avoid, the OQ 52 family. The withdrawal is right. On
main's placer it costs the stair, the landing and the library their reachability.**

## The measurement

`plan_check` fatals on `plans/tidewater-georgian-careful.json`, `engine="heuristic"`
(deterministic), taken on `git archive` checkouts of both parents and on the merged tree:

| tree | `unreachable` | `fault-present` | total fatal |
|---|---|---|---|
| main `9eb71c4` | 7 | 0 | 7 |
| this branch `ed5ef72` | 7 | 3 | 10 |
| **merged** | **10** | 3 | **13** |

The three added are `landing`, `library` and **`stair`** — a house whose stair cannot be reached
from its own front door.

**It is attributable to ONE LINE, and that was measured rather than reasoned.** On main's tree,
untouched, with nothing changed but `hallbath.stacks_over` deleted from its own copy of the
record, the count goes **7 → 10 and the three added are exactly those three**. Our tree carries
the same withdrawal and does NOT pay it: 7 unreachable either way. So this is an interaction
between main's WP-11.17 entrance anchor / WP-11.18 `partition` share and the withdrawal, and not
an inheritance from either.

The merged total reconciles exactly and nothing is unexplained: main's 7, plus the withdrawal's 3
(measured on main alone), plus this branch's 3 `fault-present`, is 13. The merged fatal set is a
strict SUPERSET of both parents' — no finding of either parent was lost.

## Why the obvious repair is forbidden

Restoring the claim makes the placement better and is the move this corpus exists to refuse.
`rooms/` and WP-13.5's own ruling say the powder room is in a single-storey dependency; a
`stacks_over` naming it is unjudgeable by construction, and `stacking.judge` would report it
BROKEN on every placement that can ever be drawn. Re-adding a false claim to buy a better slicing
is reconciling two records by picking the one that makes a checker green — the class
`oq/a-grouping-rule-and-a-room-record-can-disagree` records, met in a placement instead of a band.

## The question

**Should `geometry.bias` read a claim the judging layer cannot evaluate?**

`bias` is a placement heuristic and `stacking.judge` is a verdict, and today they read one field
with two meanings. A claim whose target stands in another massing element, or on the same level,
or on no level at all, steers the slicer exactly as hard as a claim that could be kept — and
contributes nothing a verdict can ever confirm. Three readings, none of them obviously right:

1. **`bias` reads only judgeable claims.** Honest, and it silently changes every placement in the
   corpus that carries an unjudgeable claim — which nobody has counted.
2. **`bias` keeps reading everything, and the record stops carrying unjudgeable claims.** That
   makes the withdrawal above mandatory rather than optional and pushes the cost onto the author.
3. **Neither: the loss is the placer's to fix.** Three rooms unreachable is a door-graph failure,
   and `oq/the-search-loses-the-entrance-front-on-a-multi-element-plan` already records that this
   placer draws this house badly. On that reading the claim is a red herring and the bias term is
   only what exposed it.

**Not decided here, and nothing is changed.** The merge publishes the three numbers and leaves
the placement where both parents' code put it, because repairing a placement inside a merge is
two things done at once and can only be reasoned about as one.

## What must not happen

- **Do not restore the claim.** It is unjudgeable and its withdrawal is ruled.
- **Do not loosen `stacking.LANDS_FRACTION`** to make the claim judgeable; that is a different
  rule, ruled separately at WP-13.2, and lowering it to recover a placement would retire a
  ruling to win a number.
- **Do not re-pin a fatal ceiling downward on a later tree without re-deriving this table**, which
  is three trees and one deleted line, and takes about four minutes.
