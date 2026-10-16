# oq/the-parti-check-places-a-house-the-product-does-not-build — check_partis measures a house on the placer's 10 ft module, and the product builds the same diagram on its own 8 ft one

*Status: OPEN · Raised in: the side-hall front package (16 October 2026)*

**OPEN — `build/check_partis.py`'s composability check instantiates a parti with
`compose.instantiate` and hands the bare plan to `plan_check`, and that plan does not name its
parti. The product's route, `compose.compose`, names it, and the name is how the diagram reaches the
placer (plan schema 0.6.0, WP-11.2). So the check judges a house the product does not build, and
the one parti it convicts is convicted on the difference.**

## What was measured

`partis/side-hall-townhouse.json` against its first native style, `adam-style`, 16 October 2026:

| | check_partis' harness (120 ft lot) | the same brief, parti named | the product on a 30 ft townhouse lot, parti named |
|---|---|---|---|
| footprint | 40.0 x 41.08 ft, **4 bays at the placer's 10 ft module** | 40 ft, **5 bays at the parti's own 8 ft module** | 24 ft, **3 bays at 8 ft** |
| upper openings drawn on the front | 1 | 0 | **0** |
| `even-bay-front` | **FATAL**, *"1 against between 3 and 7"* | **could not be evaluated** | **could not be evaluated**: *"the upper storey draws no opening on the entrance front; a count of zero is not handed to a parity rule or a division that carries no `applies_when`"* |

*(Corrected the same day: the first table of this file compared the harness's 120 ft lot with the product's
30 ft lot and called the difference "3 bays against 4". The lot is what made it three. The module is the
difference naming the parti makes, 10 ft against 8 ft, and the bay count follows it.)*

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

## Ruled and executed the same day (16 October 2026)

Lucas ruled the instrument's two changes, as the recommended option of three (the others were an
unjudged fatal fault *reported beside* the check, and leaving the check as it was):

1. **The check names the parti**, so it judges the house the product builds.
2. **An unjudged fatal fault is a named state of the check, and it FAILS**: printed with its reason,
   differential against the control like a fatal, and not counted as composable. The control has none
   "of its own", because it defines what is standing: every measurement nothing supplies is unjudged
   for it and for every other diagram alike.

`build/check_partis.py` and `tests/test_parti_check_judges_the_product_house.py` carry it. The
shipped catalogue now reads **19 of 21 composable, and two parti listed as unjudged**:

- `side-hall-townhouse`, `even-bay-front`: *"the upper storey draws no opening on the entrance
  front"*. The placer composes no front, so the fault is never asked.
- `cape-central-chimney`, `chimney-omitted`: *"it needs visible_chimney_count"*. `roof.py` models
  gable-end stacks only, and `tests/test_parti_composability.py::test_an_unmodelled_chimney_is_unjudged_not_absent`
  pins that unjudged state as the correct one. **This second parti was not in the question Lucas
  was asked**, and the check lists it because the ruling said any unjudged fatal fault. It was
  green before only because the check counted fatal findings.

## What stays open

The check no longer says anything untrue. What it now says is that two diagrams are not known to
work, and neither can be cleared by editing the diagram: the side-hall's front needs a placer that
composes one (the facade is a result, WP-11.7, and R6 seats an upper window only on the axis of an
opening below it), and the cape needs a roof layer that models a central stack. Clearing
either is a package of that layer's.

`tests/test_parti_composability.py::test_check_partis_runs_the_composability_check_and_is_green`
is unchanged and still red, and it asserts the same thing it always did.

Report: `docs/reports/the-side-hall-front-is-the-placers-2026-10-16.md`.
