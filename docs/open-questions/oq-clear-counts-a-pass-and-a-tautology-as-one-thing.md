# oq/clear-counts-a-pass-and-a-tautology-as-one-thing — half the faults this corpus clears are cleared on the generator's own output

*Status: OPEN · Raised in: WP-13.1, the detection layer (15 September 2026)*

`core.check_measurements` sorts every fault into four states and one of them is `clear`. On the two
shipped reference plans that bucket counts **two different things**, and until WP-13.1 nothing in
the tree could tell them apart:

| plan | clear | of which cleared on a test reading a name `critic_suspects` lists as `build/elevation.py`'s own constant |
|---|---|---|
| `tidewater-georgian-careful` | 65 | **26 (40%)** |
| `spec-builder-colonial` | 56 | **27 (48%)** |

The sharpest four are not marginal. They are the generator asserting its own output and the corpus
reading the assertion back as a verdict about the house:

- **`one-bay-symmetry-break`** clears on `count_of_openings_without_a_mirror_twin_about_the_facade_centreline = 0`
  and `width_of_the_largest_asymmetric_element_in = 0.0`, both bare literals, on a generator that
  draws a symmetric facade by construction. The fault cannot fire. It has never been able to fire.
- **`broken-head-datum`** clears on `distinct_head_datums_per_storey_per_elevation = 1`.
- **`brick-front-vinyl-return`** clears on `faces_of_volume_clad_in_primary_material = 4` against
  `faces_of_volume = 4`.
- **`condenser-on-the-entrance-elevation`** clears on
  `equipment_units_visible_on_the_entrance_elevation = 0.0`, on a generator that models no equipment.

## Why this is not simply "twenty-six false passes"

It is not, and saying so would be the flattering error in the other direction. Every one of those
numbers is **true of the house the generator drew**. A block really does have four faces; a facade
this generator composed really is symmetric; a house with no condenser in its model really has no
condenser on its entrance elevation. `critic_suspects.py`'s own docstring is already right about
this: *"Being a suspect is not being wrong."*

What they are is **vacuous as verdicts**. A pass that could not have been a failure carries no
information about the building, and it is counted in the same bucket, and reported by the same
number, as a pass that survived a real measurement. A reader told "65 faults clear" is being told
two things at once: 39 of one kind and 26 of another.

## Why nothing saw it

`build/critique.py::classify` iterates `check["findings"]`. **A fault that passes emits no finding**,
so the critic-suspect machinery — which exists precisely to stop a generator chasing its own
constants — has never been handed a single one of these. It sees the failing half of the class and
is structurally blind to the passing half.

This corpus already recorded the defect as an instance and not a population. `CLAUDE.md`:

> **A fault can be CLEARED by an invented constant, and `NOT_MODELLED` cannot see it.** OQ 52's
> guard polices measurements that are WITHHELD. `shutter-on-an-unshutterable-opening` returned
> clear at `passes: true` on a house whose kit forbids shutters because `total_shutter_leaves` was
> a hardcoded `2.0`.

That was closed at OQ 89 as one fault. It is fifty-three rows over two plans.

## What WP-13.1 did and did not do

It made the question **askable**: `plan_check` now publishes `fault_clear_on_a_generator_constant`,
a list naming each fault and the suspect measurements its passing tests read. It is a REPORT and
decides nothing — no severity, no finding, no score term — because deciding would need the ruling
below.

It did **not** reclassify anything, and the temptation to is the trap worth naming: downgrading
these to could-not-evaluate would be as wrong as leaving them. `count_of_material_changes_on_the_elevation = 0`
is a real fact about a real generated building, and turning a real pass into an unjudged is the
fake-unjudged direction this corpus treats as exactly as dishonest as a fake pass.

## What has to be ruled

1. **Is a vacuous pass a fourth state, or a property of a pass?** A fifth bucket beside present /
   clear / unjudged / not-applicable, or a flag on a `clear` row. The first changes every caller
   that reads `summary.clear`; the second changes none.
2. **Where is the line?** `faces_of_volume = 4` is arithmetic about a rectangular block and is not
   the same kind of thing as `equipment_units_visible = 0.0`, which is an absence the generator
   cannot model. Both are literals; the instrument cannot separate them and a reader can.
3. **Does a vacuous pass belong in `compose.score_candidate`'s fitness?** Today every clear fault
   counts the same. If a pass that could not have failed is worth points, the composer is ranking
   houses on the generator's own constants — the shape
   `oq/the-composer-ranks-on-an-assumed-bearing` records one layer over.
4. **Should the elevation layer withhold instead?** The OQ 52 remedy was `NOT_MODELLED`: when a
   generator has not modelled something, the measurement is ABSENT rather than zero. Applying that
   to `equipment_units_visible_on_the_entrance_elevation` would move `condenser-on-the-entrance-elevation`
   from clear to unjudged on both shipped plans, honestly. **It is not a general answer**, because
   the same move applied to `faces_of_volume` would withhold a number the generator really does
   know, and the ruling has to say which side of the line each name is on.

## Do not close this by moving a ceiling

`critic_suspects.LITERALS_CEILING` is 44 and `RATIOS_CEILING` is 7, and both are ratchets on the
INSTRUMENT, not on this. Lowering either by modelling something is progress and will move this
number as a consequence; lowering this number by blinding the instrument is how WP-9.4 nearly
ratified a blinded detector, in public, in a same-commit ceiling change.
