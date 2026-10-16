# The side-hall front is the placer's, and the parti's data cannot clear it honestly (16 Oct 2026)

*Not a numbered work package, and deliberately so (OQ 90): it is a package that was opened, built,
measured and withdrawn, and it is cited by filename.*

Lucas was asked which of the known reds to take as a work package and chose the side-hall
townhouse's front: `build/check_partis.py` and `tests/test_parti_composability.py`, one finding seen
through two readers (`oq/a-side-hall-front-is-convicted-by-a-band-written-for-centred-fronts`,
reading 1: *the parti's upper floor is under-authored*). The package was built, every claim in it
was measured on both pipelines, and **it was withdrawn: nothing is committed but this report and two
open-question files.** The red stays, and the reason it stays is the finding.

## I. What was built, and what it did

The parti schema has no way to say how many windows a wall carries; the composer derives the count
from the room's daylight band (`compose.derive_openings`), and for a composed plan it overwrites any
count it finds. So reading 1 needed three things before it could be tried:

- `partis/*.json` `rooms[].windows[]` (`wall`, `count`, `basis`, `judgment`), refused by
  `check_partis` for a wall the room does not light;
- `windows[].count_stated_by: "parti"` on the plan record (schema 0.14.0), so a stated count survives
  `derive_openings` and every revision move that re-derives a room's openings;
- `derive_openings` leaving a stated count alone, still bounded by the wall.

The data was the type's own, quoted and not typed to clear a checker: `faults/even-bay-front.json`
licenses *"A three-bay side-hall front with the door in an end bay is the urban parti and is
composed, not broken."* for `english-georgian-townhouse` and `italianate-townhouse`, bounds it with
*"Three bays with the door in an end bay; not four bays with a door somewhere in them."* and tests
it as `upper_floor_opening_count` equals 3; the parti's own scaling states `max_bay_count: 3` on an
8 ft module; and the massing says `bays: "2-3"`. Of three upper bays one is over the door, so the
upper hall carries one window and the front chamber, over the front parlour, carries two. The
split of bays between rooms is a reading and was marked `judgment: true` and said so.

## II. What the measurements say

Four variants of the parti, each measured on **two pipelines**: the check's harness
(`compose.instantiate` then `plan_check`) and the product (`compose.compose`, parti named, 30 ft
lot, then the placer). "Windows" is the data above; "one door" removes the entrance hall's own
`exterior` door, which leaves the stoop as the only way out to the front.

| variant | check's harness | the product |
|---|---|---|
| the parti as it stands | **fatal** *"1 against between 3 and 7"* | no fatal; the fault **could not be evaluated** |
| one door | **fatal**, same | no fatal; could not be evaluated |
| windows | **fatal** *"0 against equals 1"* | **fatal** *"1 against between 3 and 7"* |
| one door + windows | **no fatal** | **fatal** *"0 against equals 1"* |

**The one variant that clears the check is convicted by the product**, and the variant the product
leaves alone is convicted by the check. A parti tuned to the check is a worse parti for the thing
the check exists to protect, which is what the question's reading 3 warned of in other words.

Why the stated counts do not become a front: the placer seats a window only where it can stand on
the axis of an opening below it (R6) and keep the floor to its neighbour (R5), and the ground front
is whatever the search made. On the harness's windows variant the front chamber's second window was
refused, *"1 of 2 unit(s) could not stand on the axis of the opening below: the wall to the window
beside it would fall below 1 x the wider window"* (rule `alignment`), against a door at 36.5 ft,
and the upper hall's window stood over a parlour window and not over the door. The facade is a
result of the placement and not an input to it (WP-11.7's ruling); no data the parti can state
composes it.

## III. The finding

**The check is judging a house the product does not build.** In the harness the plan does not name
its parti, so the placer lays the house on its own defaults: 40.0 x 41.08 ft, **four bays at 10 ft**.
The product names the parti, and the placer reads the diagram: **three bays on the parti's own 8 ft
module**. On that house the upper storey draws **no** opening on the front at all, and the fault
reports `fault_unjudged`: *"the upper storey draws no opening on the entrance front; a count of zero
is not handed to a parity rule or a division that carries no `applies_when`"*.

So the fatal on the build is the harness's, and in the product the same fault is not failed but
**unevaluated**, which is the more serious statement: the product draws an upper front with nothing
on it, and says so. Naming the parti in the harness (`plan["parti"] = pid`, one line) moves exactly
one verdict over the 21 partis, side-hall-townhouse 1 -> 0, and turns 20 of 21 composable into 21
of 21. **That 0 is the fault ceasing to be evaluated, and the check counts fatal findings, so it
would read as a pass.** It is the first thing this package did not do.

## IV. What was deliberately not done

- **No parti data is committed.** Every variant that passes one pipeline fails the other, and an
  edit that clears the check by convicting the product is the laundering this corpus forbids.
- **The schema fields and the composer's stated-count path are reverted with it.** They had one
  consumer, and that consumer made the product worse; infrastructure with no honest user is a second
  place to be wrong. The design is recorded above and is a short rebuild when the placer composes a
  front.
- **No licence, no precondition on the fault, no change to the band** (the question's readings 2 and
  3, refused there and still refused).
- **`check_partis` is not changed**, for the reason in III, and the decision that belongs to Lucas
  is put under "What would be a true instrument" in `oq/the-parti-check-places-a-house-the-product-does-not-build`.

## V. New open questions

- `oq/the-parti-check-places-a-house-the-product-does-not-build`: the instrument's divergence, the
  quiet one-line fix and why it is wrong, and the two changes that would make it true.
- `oq/a-side-hall-front-is-convicted-by-a-band-written-for-centred-fronts` gains a dated amendment:
  reading 1 was built and measured, and is not sufficient while the placer composes no front.

## VI. Reproducing it

Each number above is two calls and no solver budget:

```
plan, _, _ = compose.instantiate("side-hall-townhouse", brief)        # the harness
res = compose.PC.check(plan, compose.C)                                # fatals, fault_unjudged
plan["parti"] = "side-hall-townhouse"                                  # what the product does
res = compose.PC.check(plan, compose.C)                                # same fault, now unjudged
```

and `compose.compose(brief, candidates=8, revise=False)` with `"parti": "side-hall-townhouse"` and a
30 ft lot for the product column, the placed front read off `geometry.solve(plan, parti=...)`.
