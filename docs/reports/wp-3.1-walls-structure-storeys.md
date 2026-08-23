# WP-3.1 — Walls, structure, storeys

Full technical detail lives in `docs/structure.md`, which this report points at rather than duplicates. This is the "what was found" record the hand-off brief asks for.

## What was built

A new `construction/` catalog (`wall-assemblies.json`, ten construction types with thickness ranges and bearing role; `floor-structure.json`, a light-frame joist span table scoped to non-timber-bay styles), a new `build/structure.py` (`wall_thickness`, `wall_lines`, `outside_to_outside_footprint`, `bearing_lines`, `span_check`, `storey_heights`, `graduation_check`, `roof_heights`, `stair_geometry`, all orchestrated by `build_section()`), and a new `build/render_section.py` (a vertical section view and a bearing-line plan diagram, both drawn only from the section record). 38 new tests in `tests/test_structure.py`. Both reference plans wired into `build/check_all.py`.

## What was found

**Three real bugs, all caught by actually running the module for the first time rather than by re-reading the code.** `build/structure.py` was written in a single ~230-line pass before this package's testing phase — the risk that flagged in the hand-off summary materialized exactly as expected.

1. **The four exterior walls had their axis and position swapped in `wall_lines()`.** The convention this file's own `_shared_segment()` establishes — axis `"x"` is a vertical wall at a given x, axis `"y"` is a horizontal wall at a given y — was inverted for the S/N/W/E boundary loop. Concretely, on the acceptance-example plan this planted the N wall's y-position into the x-axis break-point list `span_check()` slices spans from, fabricating a bogus interior break point, and planted the E wall's x-position into the y-axis list, producing a span entirely outside the real footprint that `span_check()` then evaluated and reported "ok." Caught by printing the raw wall and span lists after the first CLI run, not by reading the function.

2. **`span_check()` checked the wrong field against `timber-bay.json`'s applies_to list.** That list holds style ids; the function checked `construction_type` (a wall-assembly id) against it, which can never match, silently routing every plan through the light-frame joist table regardless of style — defeating the module's own stated purpose of distinguishing hand-timber framing from dimensional lumber. Caught the same way: running the module against the acceptance-example plan and confirming, via the returned `member` field, which branch actually ran.

3. **`graduation_check()`'s third/second-storey band was hand-transcribed as the wrong one of `storey-graduation.json`'s four bands** — the ground-under-piano-nobile band (0.60–0.85) instead of the actual third/second band (0.70–0.88). Fixed by reading the bands directly from the pack's own `derived_rules` at call time instead of re-transcribing them, so this cannot drift out of sync with a future edit to the pack again.

Each has a dedicated regression test in `tests/test_structure.py` (`TestWallLinesExteriorOrientation`, `TestSpanCheckFramingBasis`, `TestGraduationCheck`) rather than being fixed silently.

**A fourth item is a genuine tension between two data signals, recorded rather than resolved — the same discipline WP-2.2's dining-room finding used.** Bug #2's fix (key `timber_framed` off style) is correct for the acceptance-example plan, a masonry-walled Georgian house whose floor framing is genuinely period hand-timber. But the corpus's second reference plan, `spec-builder-colonial.json` (style `colonial-revival`, a *revival* style, declaring no `construction_type` at all), surfaces a real disagreement: its 23.39 ft ground-floor bay fails the 20 ft hand-timber cap the style's presence in `timber-bay.json`'s applies_to list selects, but would pass cleanly against an engineered I-joist, which is very plausibly what a real spec-built colonial-revival house is actually framed with. This corpus records no field stating floor-framing method independently of style or wall construction, so the two signals can genuinely disagree for exactly this shape of plan. `build_section()` now computes a `framing_basis` note stating the tension explicitly whenever it arises, rather than silently applying the bay-module cap as settled fact. Not resolved here — see `docs/structure.md`'s own "New open questions" for what a real fix would need (most plausibly a `hand_framed` field on the wall-assembly catalog, independent of style).

**A real, separately-recorded finding on the stair.** The acceptance-example plan's own stair-hall (10.0 × 10.62 ft, solved by `geometry.py`) cannot fit a single straight flight covering the ground storey's full 12.28 ft rise (21 risers, 200 in of run) without a landing shorter than the room itself. `stair_geometry()` correctly reports this as a landing-rule violation. Whether this means the reference plan's stair-hall is genuinely undersized, or whether a real Tidewater Georgian house of this depth would use a switchback this module's single-flight model cannot check, is left open — see "What was deliberately not done" in `docs/structure.md`.

## What was deliberately not done

- Only a single straight stair flight is modelled — no switchback, winder, or landing-mid-flight geometry, which is exactly what the stair finding above would need to resolve differently.
- Stair headroom is flagged as "not independently verified" rather than computed — the floor structure depth above a run is not yet reconciled against the run's own geometry.
- Roof FORM (hip/gable/gambrel, ridge step-down between massing volumes, dormers) is explicitly out of scope — `roof_heights()` produces only grade-to-eave/ridge numbers for the section record under a stated simplifying assumption (single ridge, shorter footprint dimension). WP-3.3's own work package.
- Per-storey wythe step-down in a masonry bearing wall is not modelled — one thickness per construction type for the whole building.
- Basements are not modelled — `grade_to_floor_ft` is only assigned to storeys at or above the ground floor.
- The construction catalogs carry no JSON Schema, consistent with the rest of this corpus's proportion/module packs.

## New open questions

1. Should `construction/wall-assemblies.json` gain a field stating hand-timber-vs-light-frame floor structure independently of `bearing`/id, so `span_check()`'s `framing_basis` tension can resolve per-plan rather than only being flagged? Not decided here.
2. Is `tidewater-georgian-careful.json`'s stair-hall genuinely undersized for its storey height, or does this style's real stair convention want a switchback this module cannot yet check? Not decided here — flagged for whoever owns the reference corpus's editorial content.
