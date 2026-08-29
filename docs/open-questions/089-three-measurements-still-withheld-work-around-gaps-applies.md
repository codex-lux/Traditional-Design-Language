# OQ 89 — three measurements are still withheld to work around gaps `applies_when` now covers, and one is supplied as a constant that is not true

*Status: CLOSED · Raised in: From the adversarial audit of WP-5.14 (28 Aug 2026)*

**CLOSED 28 Aug 2026 (WP-5.11) — ruled: state what the record knows, guard what presupposes it, and withhold the rest through the mechanism rather than a comment.** The fourth bullet was a LIVE defect and is worth stating as one: `shutter-on-an-unshutterable-opening` returned **CLEAR, value 1.0, `passes: true`** on `tidewater-georgian`, whose kit makes `none` canonical — a fault cleared on two invented shutters. `shutters_carried` had been computed 500 lines away since WP-5.9 and never consulted. The counts are now conditional (2.0 carried / a measured 0.0 not / absent unstated) and the fault comes back **not-applicable**, naming both preconditions.

`window_head_radius_in` is SUPPLIED, computed from the head the record already states — R = r/2 + s²/(8r) for a segmental arch, **0 for a straight one**, absent where the kit gives only a band. A gauged flat arch counts as straight on brick-course's own words: its camber is there so the head "reads level" and is "invisible on paper". `shutter_head_radius_in` stays absent and moved into `NOT_MODELLED`, because nothing in this corpus says whether a shutter follows a curved head — which is the very question the fault asks, so deriving it would hand the fault its own conclusion.

**And supplying it made one of this entry's own "none is live today" bounds_tests live.** `exceptions[0].bounds_test` is the IDENTICAL expression to the guarded secondary and carried no guard; with the radius supplied as a measured 0 it returned `error: float division by zero`, proved before it was guarded. The WP-5.9 lesson and the WP-5.10 audit's Second Empire finding in one place. The `brick-front-vinyl-return` pair is retired the same way: the record states `count_of_material_changes_on_the_elevation` as a measured 0 and both secondaries are preconditioned on it. **The remaining 14 unguarded dividing bounds_tests are still listed rather than guarded speculatively.** Original entry follows.<br><br>**OPEN — three measurements are still withheld to work around gaps `applies_when` now covers, and one
is supplied as a constant that is not true.** WP-5.10's commit message says "two workarounds retired
by one field". Three more are standing:

- `window_head_radius_in` / `shutter_head_radius_in` (`build/elevation.py`): withheld for exactly the
  reason the solar-array measurement was, and `shutter-on-an-unshutterable-opening`'s arch-head
  secondary **gained** its `applies_when` in the same commit — so the guard exists and the
  measurement that would exercise it still does not, leaving that fault clear on 1 of 2 tests.
- `plan_offset_at_material_change_in`, `ridge_height_difference_between_volumes_in`
  (`brick-front-vinyl-return`), whose comment names the solar and shutter cases as its precedent.
- **`total_shutter_leaves: 2.0` and `shutter_leaves_with_a_leaf_width_of_clear_hinge_side_wall: 2.0`
  are unconditional constants**, supplied whether or not the style carries shutters, so
  `shutter-on-an-unshutterable-opening` reads `2/2 = 1.0` and returns CLEAR on a house whose kit makes
  `none` canonical. That is a fault cleared on two invented shutters — OQ 52's class, inside
  `_derive_measurements`, outside `NOT_MODELLED`'s reach and therefore outside the guard that was
  built to catch exactly this.

**Also counted while there:** 15 `exceptions[].bounds_test` entries divide by a count with no
`applies_when`. None is live today (their denominators are unsupplied or non-zero), and they are
listed rather than guarded speculatively — the four WP-5.10 guarded were guarded because they were
reachable, and guarding the rest without a reachable case would be adding preconditions nobody can
check.

## From the third collision (28 Aug 2026)
