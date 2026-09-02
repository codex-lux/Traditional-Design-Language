# oq/the-stair-run-is-spelled-three-times — 16, 17 and 21 risers for one house, and the section draws the third

*Status: RULED 2 Sep 2026 · Raised in: WP-9.6 (2 Sep 2026), from a WP-9.2 finding upgraded twice*

**One stair, three spellings, three answers on `plans/tidewater-georgian-careful.json`:**

| spelling | input | result |
|---|---|---|
| `rooms/stair-hall.json` `critical_dimension` | stated in prose | **16 risers at 7.5 in, 15 treads, 12 ft 6 in** |
| `build/openings.py::stair_pass` | `ch = floor_to_ceiling_ft or 9.0` → 120 in | **17 risers at 7.059 in, 13.33 ft run** |
| `build/structure.py::stair_geometry` | `storey_height_ft` 12.279 → 147.3 in | **21 risers at 7.014 in, 16.67 ft run** |

`structure.py` is the one that draws the section. So a reader of this corpus's own most-authored
reference plan can be told the stair has 16, 17 or 21 risers depending which record they open, and
nothing compares them.

**This finding was upgraded twice and each upgrade made it worse.** The WP-9.2 study reported that
`stair_pass` hand-ports the prose while its own docstring says the prose "has been read by nothing"
— two spellings of one rule, unheld. The WP-9.5 second pass measured the drift and made it 16
against 17. WP-9.6 found the third spelling, named in the very docstring `openings.py` quotes, and
measured 21.

## Two independent defects, and only one is the riser constant

**(a) The constant.** `openings.py` and `structure.py` both follow
`proportions/systems/storey-graduation.json`'s `ceil(storey / 7.25)`; the prose works at 7.5 in.

**(b) The STOREY, which is the larger gap and is not about risers at all.** The plan states no
`floor_to_ceiling_ft`, so `openings.py` falls back to a hardcoded **9.0 ft** while `structure.py`
reads the derived **12.279 ft** storey height. That is 3.3 ft of disagreement about the same house,
and it is what produces 17 against 21. Reconciling the riser constant alone would leave it.

## Lucas's ruling, 2 Sep 2026: the PACK is authoritative — 7.25 in

`storey-graduation.json`'s `ceil(storey / 7.25)` governs. Both Python spellings already follow it,
so **this ruling redraws no stair**: what moves is the prose. `rooms/stair-hall.json`'s
`critical_dimension` is rewritten to match, and the two Python copies become one reader with two
callers — the `plan_check.furniture_shortfalls` shape, not the `openings.required_wall_ft` shape
(that rule is deliberately spelled three times because one spelling is JavaScript; here all three
are Python and a shared function is available).

**Ruling (b) is NOT settled by this and must be fixed first or alongside.** Deciding the constant
does nothing about a 9.0 ft fallback standing in for a 12.279 ft storey. The fallback is the same
class as OQ 52 — a generator supplying a number where the record is silent — and the honest form is
to derive the storey once and hand it to both callers, or to report COULD NOT EVALUATE where no
plan states one. **A hardcoded 9.0 that silently replaces a real derived figure is an invented
measurement**, whatever the riser constant says.

## What must not happen

Do not reconcile by editing whichever file is easiest and leaving the third. There are three, the
third was invisible to two audit passes, and a fix that lands in two of them reproduces this entry
exactly. And do not change the prose to 7.25 without also reading whether 7.5 is the figure the
period sources actually support — the ruling settles which record GOVERNS, not which number is
architecturally right, and if 7.5 is right then the pack is what should move.
