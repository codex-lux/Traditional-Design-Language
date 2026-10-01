# oq/the-shutter-fault-clears-on-the-rhythm-while-the-sheet-refuses-the-leaves — two facades, one fault

*Status: OPEN · Raised in: WP-14.6, the adversarial audit of Phase 14 (27 Sep 2026)*

**OPEN — `shutter-on-an-unshutterable-opening` clears on every plan that carries shutters, on a
facade the sheet does not draw, while the sheet beside it refuses the leaves for want of wall.**

The fault's primary test is `shutter_leaves_with_a_leaf_width_of_clear_hinge_side_wall /
total_shutter_leaves`, equal to 1.0, and its own note says what to count: *"Every leaf must have
somewhere to swing. Count leaves; count how many have a full leaf-width of uninterrupted wall on
the hinge side ... A leaf sitting between two units of glass ... fails."* `build/elevation.py`
supplies both counts as `2.0` wherever the storey carries shutters, on the argument that
`pier_width_in` is wider than a leaf. That pier is the RHYTHM's -- the bay spacing the file
composes -- and since WP-13.3 the elevation draws the PLAN's placed openings instead.

WP-14.6's `elevation._clearances` reads the placed openings and refuses a pair whose leaf would
hang over another opening, over another window's leaf, or past the corner of the face. Measured on
every face of the ten shipped plans that carry shutters:

| plan | windows carrying a pair | pairs refused | the fault reads |
|---|---:|---:|---|
| `good-02-portico-library-house` | 9 | 8 | clear, 2 of 2 |
| `good-05-lobby-gallery-mansion` | 11 | 9 | clear |
| `spec-builder-colonial` | 10 | 7 | clear |
| `good-07-diamond-plan-house` | 6 | 5 | clear |
| `bad-01-grilling-porch-ranch` | 3 | 2 | clear |
| `bad-02-flex-room-craftsman` | 3 | 2 | clear |
| `bad-05-two-story-spec-colonial` | 10 | 2 | clear |
| `good-03-parlor-drawing-room-house` | 2 | 2 | clear |
| `bad-03-narrow-lot-townhome` | 4 | 0 | clear |
| `bad-07-octagon-dinette-colonial` | 2 | 0 | clear |
| **total** | **60** | **37** | |

So on eight plans a reader is shown SHUTTERS NOT DRAWN ON N WINDOWS -- no wall to swing onto --
beside a critique in which the fault about exactly that came back clear. It is OQ 89's class (a
fault cleared on a figure the record does not hold) and the OQ 52 family (the plate as evidence
against the finding beside it), reached through the facade the measurements describe rather than
through an invented constant.

**What must be ruled before the measurement moves:**

1. **Which facade the elevation's measurements describe.** Most of `_derive_measurements` still
   reads the storey rhythm; WP-13.3 moved three storey-alignment measurements onto the placed
   openings and left the rest. Moving this one alone puts two facades in one measurement set,
   which is OQ 48's error one layer up; moving them all is a package.
2. **What a refused pair counts as.** Counting it among the leaves the kit calls for makes the
   fault fire on the eight plans above -- the style asks for shutters the placement leaves no wall
   for, which is the fault's own subject. Counting only the leaves drawn makes the ratio 1.0 by
   construction, because `_clearances` removed the others, and that is a tautology cleared as a
   pass (`oq/clear-counts-a-pass-and-a-tautology-as-one-thing`).
3. **Which faces.** The fault is measured from a photograph; the counts above are every face the
   elevation draws. The street front alone gives different figures.

**What WP-14.6 did, and deliberately did not do.** It drew only the leaves that have wall and said
so on each sheet, held the ink to that with census row V20, drove every branch of `_clearances`
by hand, and corrected the comment in `_derive_measurements` that said the pier leaves every leaf
room. It moved no fault verdict, because doing so on eight plans inside an ink audit is two
packages reasoned about as one.

## Amendment, 27 Sep 2026 (the audit of the audit): the SIDELIGHTS are the same question

`elevation._clearances` refuses a sidelight pair on the same ground as a shutter pair, and the same
fault shape follows it. On `tidewater-georgian-careful`, placed on the search as the census draws it,
the plate says SIDELIGHTS NOT DRAWN -- *"the left sidelight would stand 9.0 in over passage's
window, which the plan places 12.0 in from the leaf"* -- while `sidelights-as-storefront-glass`
comes back **clear** on `sidelight_width_in / door_leaf_width_in`, a ratio of the composition's
sidelight to its leaf. The glass the fault judges is glass the sheet refuses to draw. `plan_check`
already lists that verdict in `fault_clear_on_a_generator_constant` (its only read is
`sidelight_width_in`, which `critic_suspects` names as the elevation's own constant), so the
critique does not present it as a finding about the house -- but it counts among the clears.

Both of this question's first two rulings reach it unchanged: which facade the measurements
describe (the composition's, or the placed openings'), and what a refused pair counts as (a pair
the kit calls for and the placement leaves no wall for is the fault's own subject; a pair counted
only where drawn makes the ratio vacuous). Nothing moves here either.

**What the audit did do**: the scene and the DXF, which honoured `sidelights_drawn` and said
nothing, now republish the refusal's own reason (`states.cannot`, and `TDL::sidelights-refused`
XDATA on the doorcase), so no surface shows a doorcase with no sidelights and no word of why --
`tests/test_refused_sidelights_are_said.py`.

## Re-derived 1 Oct 2026 (WP-16.7): the table above is the placement before WP-16.6

The table is a statement about the placement it was measured on. It re-derives exactly, plan by
plan, on `bb3c6de`, the tree before WP-16.6: 60 windows carrying a pair, 37 pairs refused.

After WP-16.6's pier floor and WP-16.7's R7, the same ten plans draw 50 windows, every one carrying
a pair, and refuse **1** pair. That is good-05's upper east face, whose leaf would hang past the
corner.

- The ten windows that went are windows WP-16.6 no longer seats on those faces.
- The refusals fell from 37 to 1 with them, and for the pier floor: a wall of 1.0 x the wider
  window holds both neighbours' half-width leaves exactly. This amendment does not match windows
  across the two placements, so it does not say how many of the 37 were among the ten.
- R7 decides which pairs are refused where they contend, and none contend on these plans.

**The fault still reads clear on every plan that carries shutters**, on the rhythm's figures, and
neither package moved it. So this question stands as asked. What changed is how much the sheet has
to say against the verdict: one refused pair, where it was 37. R7 decided which pairs a sheet
refuses, not what a refused pair counts as, which is this question's ruling 2.
