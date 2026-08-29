# OQ 84 — ruled: take the measurement, then guard both

*Status: CLOSED 27 AUG 2026 · Raised in: From the dormer layer (WP-5.13, 27 Aug 2026)*

**CLOSED 27 Aug 2026 (WP-5.14) — ruled: take the measurement, then guard both.** The fault's own note
has always said how to choose (*"Choose the test by whether an order is present, not by preference"*), in
prose no evaluator could read. `build/elevation.py` now derives
`an_order_is_applied_to_the_wall_carrying_the_eave_cornice` from the style's own `porch_type` and
`pilaster` slots, and both rivals carry an `applies_when` on it, so exactly one can run.
**The plausible wrong answer was checked first and is pinned as a test:** `gibbs_order_applies_to_style`
is True on `tidewater-georgian` and means only that Gibbs Ionic is the order its cornice is GENERATED
from; reading it as "an order is applied here" selects the entablature test on a house measuring
**0.4286** and convicts it. Nor is a portico enough — the style's own rule says "where a portico occurs
it is one bay wide, centred, and carries the bound order", and a one-bay portico's entablature is not
the eave. Only an order engaging the whole wall qualifies, which is a short and quoted list.
**`cornice_projection_in` is supplied now, and that is the point of the exercise.** WP-3.2 had
withheld it to keep the rivals from firing, which silenced the fault on a NAME MISMATCH:
`elevation.py` published `cornice_projection_past_wall_face_in`, and the fault came back "clear" on
its wall-height ratio alone while its primary and two of its four secondaries were skipped for want
of a name rather than a number. Measured: **1 of 5 tests evaluating → 3 evaluated, 1 declined on its
precondition, 1 still needing an unsupplied measurement.** The same field retired a second WP-3.2
workaround in the same commit: `solar_array_area_sqft` is supplied at its honest zero and
`entrance-slope-penetration`'s array secondary declines instead of convicting. The original entry
follows.<br><br>ORIGINALLY: **`cornice-that-is-a-fascia` carries two RIVAL secondary tests, and
whichever is right the other fails.** Its first secondary wants `cornice_projection_in / cornice_height_in` between **0.35** and its
upper bound (*"THE DOMESTIC BOXED CASE. 18 in high and 7 3/4 in out gives 0.43"*); its second wants the
same expression between **0.85** and its own (*"THE FULL ENTABLATURE-DERIVED CASE — where an order is
actually applied, on a portico or a pilastered front. A full cornice projects about its own height"*).
Both notes are explicit that applying either to the other's case is a disaster, and `check_measurements`
reports a fault present when ANY of its tests fails — so on any house that supplies a cornice projection
and a cornice height, one of the two convicts it. Nothing in the corpus is being asked which case this
facade is.

WP-5.13 built `applies_when`, a precondition on the MEASUREMENTS, and used it to close
`docs/elevation.md`'s open question 1 for the other two faults that question named
(`entrance-slope-penetration`'s solar-array secondary, `shutter-on-an-unshutterable-opening`'s
arch-head secondary). **This one it deliberately did not touch**, because guarding it needs a
measurement stating whether an order is applied to this facade — something like
`an_order_is_applied_to_the_facade`, or a count of applied pilasters or columns — and no generator in
this corpus takes one. `build/elevation.py` knows whether a doorcase carries pilasters and whether the
style resolves an order pack, so the measurement is derivable; the question is whether it should be
a boolean the fault corpus tests on, or whether the two secondaries should instead be split into two
faults with different `applies_to`. That is a fault-corpus editorial decision, not a renderer's.

Neither reference plan trips it today, and the reason is not reassuring: the elevation supplies
`cornice_projection_past_wall_face_in` and `main_cornice_height_in`, and the fault tests on
`cornice_projection_in` — a name nothing supplies. The rival pair is inert because of a name mismatch,
and the day anyone fixes the name, both houses acquire a serious fault.
