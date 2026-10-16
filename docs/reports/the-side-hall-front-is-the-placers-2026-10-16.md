# The side-hall front is the placer's, and the parti's data cannot clear it honestly (16 Oct 2026)

*Not a numbered work package, and deliberately so (OQ 90): it is a package that was opened, built,
measured and withdrawn, and it is cited by filename.*

Lucas was asked which of the known reds to take as a work package and chose the side-hall
townhouse's front: `build/check_partis.py` and `tests/test_parti_composability.py`, one finding seen
through two readers (`oq/a-side-hall-front-is-convicted-by-a-band-written-for-centred-fronts`,
reading 1: *the parti's upper floor is under-authored*). The package was built, every claim in it
was measured on both pipelines, and **it was withdrawn: the parti, the schema and the composer are
untouched.** The red stays, and the reason it stays is the finding. What was changed afterwards, by
Lucas's ruling the same day, is the check's instrument (section VII).

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
(`compose.instantiate` then `plan_check`, a 120 ft lot) and the product (`compose.compose`, parti
named, a 30 ft townhouse lot, then the placer). The lots differ because each pipeline's own brief
does; the finding in III does not depend on it, and was re-measured on one brief for both. "Windows" is the data above; "one door" removes the entrance hall's own
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
The product names the parti, and the placer reads the diagram: the parti's **own 8 ft module**. On the
check's own brief (a 120 ft lot) that is five bays at the same 40 ft; on a 30 ft townhouse lot, which is
the lot the product column below was composed on, it is **three bays at 24 ft**. On that house the upper storey draws **no** opening on the front at all, and the fault
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
- **`check_partis` was not changed on its own**, for the reason in III. It was changed afterwards, as
  one ruled step with the unjudged state beside it (section VII).

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

## VII. Afterwards: the instrument, ruled and executed

The decision this package left was put to Lucas as three options and the recommended one was ruled:
**the check names the parti, and an unjudged fatal fault is a named state of the check that fails it.**

- `plan["parti"] = pid` is set before `plan_check` judges the plan, for the parti and for the control.
- An unjudged fatal fault is reported with its reason, differential against the control (keyed on the
  fault alone), and the parti is not counted composable. The control has none of its own: it is the
  definition of a standing gap, and without that exemption twenty unjudged measurements nobody
  supplies land on the one diagram everything else is subtracted against.
- `check_composability` takes a `compose=` seam so the branches can be driven; the shipped catalogue
  reaches them with two parti, and two records whose state may change cannot guard a branch.

**The catalogue now reads 19 of 21 composable, with two parti named as unjudged**, and that second
one is a consequence the question did not show: `cape-central-chimney`'s `chimney-omitted` is
unjudged (*it needs visible_chimney_count*) because `roof.py` models gable-end stacks only, and
`tests/test_parti_composability.py::test_an_unmodelled_chimney_is_unjudged_not_absent` pins that as
the correct state. It was green because the check counted fatal findings; it is listed because the
ruling said any unjudged fatal fault. Neither parti can be cleared by editing the diagram: the
side-hall's front needs a placer that composes one, and the cape needs a roof that models a central
stack.

**A figure in this report's first draft, and in the pull request comment and commit message that
repeated it, was imprecise and is corrected here.** It said the check judges "a 4-bay house at 10 ft"
where the product builds "3 bays at 8 ft". The two columns were composed on different lots (120 ft and
30 ft) and the lot is what made three. What naming the parti changes is the module the placer reads,
10 ft against the diagram's own 8 ft: five bays at the same 40 ft on the check's lot, three at 24 ft on
a townhouse lot. Re-measured on one brief for both; the unjudged verdict is the same on all of them.
