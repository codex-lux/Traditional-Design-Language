# OQ 98 — `span_check` credits a bearing wall across the whole floor plate however short it is, and the validator never mentions span capacity at all

*Status: OPEN · Raised in: From the adversarial audit of WP-7.4 (27 August 2026)*

**OPEN — `span_check` credits a bearing wall across the whole floor plate however short it is, and the validator never mentions span capacity at all.** Two halves of one subject, both found by an adversarial audit of the package that fixed the *other* defect in the same function.
**THE MEASUREMENT HALF.** `build/structure.py::span_check` reads each wall's `axis` and `position_ft` and never its `lo_ft`/`hi_ft` — the extent `wall_lines` computes deliberately, and whose own docstring says "this file needs the whole run". So a wall is a break point across the entire opposite dimension or nothing. Every interior bearing wall on both shipped plans is partial: `tidewater-georgian-careful`'s upper y-wall at 30.0 runs **20.00 ft of the 60.00 ft it is credited across**; `spec-builder-colonial`'s upper x-wall at 30.0 runs **4.00 ft of 38.44**. Minimal case: a 40x30 box with ONE 1.5 ft closet wall that happens to land on the 20 ft bay line reports two clean 20 ft spans instead of one 40 ft failure — `_shared_segment` admits any segment over 1.0 ft. Crediting only walls that run 90% or more of their axis takes the two shipped plans from 4 over-capacity spans to 8, and the worst from 40.0 ft to 60.00 ft.
**This is the same class as the bug WP-7.4a fixed, one field away, and in the same direction** — a defect reported smaller than it is. It was NOT fixed with it, deliberately: the honest model is a span per RUN rather than per axis line (joists bearing on a 4 ft wall are supported; the joists beside it are not), which is a different computation rather than a filter, it changes the structural verdict on both reference plans again, and it would re-open the weight sweep that set `geometry.SPAN_W`. It wants a ruling on what a partial bearing wall supports before it wants code.
**THE REPORTING HALF.** `build/plan_check.py` has **no span or structural-capacity finding of any kind**, so the validator verdict the workbench shows and the fidelity score the composer ranks on contain nothing about span capacity: a plan with a 60 ft unsupported run gets a clean verdict. `build/structure.py` also contains no `sys.exit`, so `check_all.py`'s two `structure.py` invocations print and return 0 whatever they find. (The no-exit convention is shared with `plan_check.py`, `roof.py` and `elevation.py`, so this is a convention question rather than a bug in one file.) WP-7.4 built OQ 84's SEARCH half and its `geometry_report.span_capacity` block; the CRITIC half is unbuilt, and OQ 84 was closed without saying so.

---

## New evidence, 5 September 2026 (WP-11.8): the number moved a lot and nobody could have seen it

WP-11.8 made the band a room's own record states the first key of the search's candidate
acceptance. A squarer room puts fewer cuts on the bay module, and the only way this slicer creates
a bearing line is to cut on it — so the placement got better by every measure the critic reports
and **worse by this one**:

| | over-capacity clear spans | worst |
|---|---|---|
| before WP-11.8 | 13 | 40.0 ft |
| after | **25** | **60.0 ft** |

It is WP-7.4's own mechanism running backwards: that package's span term pulled cuts ONTO the
grid and took the Tidewater plan's relaxations 9 → 7, and this one rewards a shape that pulls
them off it (relaxations 64 → 86 corpus-wide).

**The point for this question is not the direction, it is that nothing said so.** `plan_check`
emits no span finding, so twelve more over-capacity spans and a worst case half again as long
appear on no sheet, in no critique, and in no `revision_report` — they were found by two guards
in `tests/test_structure.py` that happened to pin `spec-builder-colonial` flagging one, and that
plan is now the single one in the corpus that flags none. Had those two guards been written
against any other plan, this would have been invisible.

It also sharpens the cost of leaving the question open: a search term that trades against span
capacity cannot be judged by the arbiter, so the trade can only be made in a report.
