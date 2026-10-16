# oq/a-side-hall-front-is-convicted-by-a-band-written-for-centred-fronts — check_partis is red on the merged tree

*Status: OPEN · Raised in: WP-13.3, the prover learns the type (16 September 2026)*

**`build/check_partis.py` fails on the merged tree and the failure is the honest measurement
arriving.** Its composability check instantiates `partis/side-hall-townhouse.json` against its
first native style, `adam-style`, and `faults/even-bay-front.json`'s second secondary —
`upper_floor_opening_count` between 3 and 7, *"Three, five or seven. Nine-bay fronts are
institutional, not domestic"* — convicts it FATALLY at **1**. The control parti does not trip it,
so the check attributes it to the diagram, correctly. Before WP-13.3 that measurement was the
elevation's RHYTHM count, `max(3, ...)` by the pack formula, which never fell below three and so
passed this band on every front the corpus could compose, whatever the front held. It is the
plan's PLACED upper openings on the front now, and on the composed townhouse there is one:

    ground front  hall window · hall door · hall window · parlor window · parlor window · stoop door
    upper front   primary bedroom window (one)

The parti declares no windows at all (`windows: null` on every room); `compose.instantiate`
gives the primary bedroom its type's one front window, the gallery corridor over the entrance
hall declares no exterior wall, and the second chamber declares N and E. So the upper front is a
26 ft windowless corridor and one sash, over a ground front of five openings. That is a front
with no composition, and the fault says so for the first time.

**Three readings, and the corpus states all three somewhere.**

1. **The parti's upper floor is under-authored** — the type's own exemplars put the front
   chamber across the parlour with the parlour's two windows above and a stair-hall window
   over the entrance. Authoring `windows` on the parti's upper rooms is the fix that makes the
   composed house the type; it needs the exemplars read, not a count typed to clear a checker.
   This is `docs/reports/wp-9.2-the-parti-is-not-the-type.md`'s class on the upper floor.
2. **The band is written for a centred front and the fault knows it.** Its first secondary's
   note reads *"landing on a non-central window is a side-hall parti and may be correct"*, and
   its `exceptions[]` license `english-georgian-townhouse`, `italianate-townhouse`,
   `shotgun-house` and `cape-cod-colonial` at two or three openings — but a licence is keyed on
   the STYLE id and matches it exactly (`oq/a-licence-matches-the-style-id-exactly-and-never-its-descendants`),
   while the property being licensed is the PARTI's. `adam-style` names the side-hall townhouse
   as native and carries no licence, and adding one would excuse every Adam-style front,
   centred ones included.
3. **A precondition on the count band** — judge it only where the door stands on the centre bay
   — is the fault's own distinction, but the measurement that states it
   (`horizontal_distance_from_door_centreline_to_centre_window_centreline_in`) is WITHHELD on
   this very house, so the gate would turn the fatal into could-not-evaluate for a reason that is
   not the composition's. That is the fake-unjudged shape and it is refused here.

**Nothing was edited.** The fault is not preconditioned, no licence is added, the parti is not
authored blind, and `check_partis.py` is RED on the merged tree with this one error — beside the
gate, which is red by design until Phase 13 lands. Reading 1 is the one that makes a house; it
needs the bench's exemplars for the type and is Lucas's to rule on or to hand to the precedent
line. Report: `docs/reports/wp-13.3-the-prover-learns-the-type.md`.

## Amendment, 16 October 2026: reading 1 was built and measured, and it is not sufficient

*Status unchanged: OPEN. Report: `docs/reports/the-side-hall-front-is-the-placers-2026-10-16.md`.*

Lucas chose this reading as a work package. It was built (a parti may state how many windows a wall
carries, with a quoted basis; a plan window says the count is the parti's; the composer leaves it
alone) and the type's own statements were used for the data: the fault's licence of the three-bay
side-hall front for `english-georgian-townhouse` and `italianate-townhouse`, its `upper_floor_opening_count`
equals 3, the parti's `max_bay_count: 3` on an 8 ft module. **It was withdrawn, and nothing is committed.**

- **The red is not the parti's.** `check_partis` instantiates the diagram with no parti named, so the
  placer lays a **4-bay house at 10 ft**; the product names the parti and lays **3 bays at 8 ft**. On the
  product's house the fault is not failed but **could not be evaluated**, because the upper storey
  draws no opening on the front: `oq/the-parti-check-places-a-house-the-product-does-not-build`.
- **The data cannot clear it honestly.** Of four variants measured on both pipelines, the one that
  clears the check (one front door, upper hall and chamber windows stated) is convicted by the product,
  and the one the product leaves alone is convicted by the check. The placer seats an upper window only
  on the axis of an opening below it (R6) and the ground front is the search's, so a stated count is
  not a seated opening.
- **The reading is still the right one for the house**, and the remaining cost of it is in the placer
  and not in the diagram: a front that is composed (WP-11.7's *facade is a result* ruling) is what
  turns three stated bays into three drawn ones.
