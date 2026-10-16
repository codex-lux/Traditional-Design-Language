# oq/the-parti-check-places-a-house-the-product-does-not-build — check_partis measures a 4-bay house at 10 ft, and the product builds the same diagram at 3 bays and 8 ft

*Status: OPEN · Raised in: the side-hall front package (16 October 2026)*

**OPEN — `build/check_partis.py`'s composability check instantiates a parti with
`compose.instantiate` and hands the bare plan to `plan_check`, and that plan does not name its
parti. The product's route, `compose.compose`, names it, and the name is how the diagram reaches the
placer (plan schema 0.6.0, WP-11.2). So the check judges a house the product does not build, and
the one parti it convicts is convicted on the difference.**

## What was measured

`partis/side-hall-townhouse.json` against its first native style, `adam-style`, 16 October 2026:

| | check_partis' harness | the product (`compose.compose`, parti named, 30 ft lot) |
|---|---|---|
| footprint | 40.0 x 41.08 ft, **4 bays** (the placer's 10 ft default) | **3 bays on the parti's own 8 ft module** |
| upper openings drawn on the front | 1 | **0** |
| `even-bay-front` | **FATAL**, *"1 against between 3 and 7"* | **could not be evaluated**: *"the upper storey draws no opening on the entrance front; a count of zero is not handed to a parity rule or a division that carries no `applies_when`"* |

The harness change that makes the two agree is one line: `plan["parti"] = pid` after `instantiate`.
Over all 21 partis it moves exactly one verdict, side-hall-townhouse **1 -> 0 fatal** (20 of 21
composable becomes 21 of 21), and the other twenty are identical. Measured by running
`check_composability` twice, with and without the line.

## Why that line is not the fix

The 0 is not a pass. Named, the fault is `fault_unjudged` with `withheld` pointing at
`elevation.front.withheld`: the placed house draws **no** upper opening on its front, so there is
nothing to count. `check_composability` counts fatal *findings*, and an unjudged fatal fault emits
none, so the check would report 21 of 21 over a parti whose governing fault was never evaluated.
That is the collapse this corpus names first. The composer already keeps the two apart
(`compose.rank_key` ranks judged fatals, then the placement's standing, then **unjudged** fatals);
the check does not read the second kind at all.

## What would be a true instrument

1. **The harness names the parti**, so it judges the house the product builds. Without this its
   verdicts are about a different house.
2. **An unjudged fatal fault is a named state of the check**, printed with its reason and counted
   apart from "composable". Whether it FAILS the check or is reported beside it (the way the
   corpus allowlists its three unjudged checks by name in CI) is a ruling, because the first leaves
   the build red and the second leaves a parti with an unjudged fatal inside a green line.

Neither is done here. Done together they turn the build's known red on this parti into an honest
could-not-evaluate, which is the state the product already reports, and `tests/test_parti_composability.py`
asserts "21 of 21" in a vocabulary that has no word for it.

## What must not be done

**Do not add `plan["parti"] = pid` to the check on its own.** It is the quiet fix: one line, one
red gone, 20 of 21 turned into 21 of 21, and the reason the red went is that the fault stopped being
evaluated.

Report: `docs/reports/the-side-hall-front-is-the-placers-2026-10-16.md`.
