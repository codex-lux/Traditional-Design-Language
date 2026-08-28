# OQ 89 — three measurements are still withheld to work around gaps `applies_when` now covers, and one is supplied as a constant that is not true

*Status: OPEN · Raised in: From the adversarial audit of WP-5.14 (28 Aug 2026)*

**OPEN — three measurements are still withheld to work around gaps `applies_when` now covers, and one
is supplied as a constant that is not true.** WP-5.14's commit message says "two workarounds retired
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
listed rather than guarded speculatively — the four WP-5.14 guarded were guarded because they were
reachable, and guarding the rest without a reachable case would be adding preconditions nobody can
check.
