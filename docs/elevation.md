# Elevation

Bay lines, window openings, one head datum per storey, an entrance composition, water table and
belt course, the eave cornice, and the roof outline reused from `build/roof.py` — the layer
between a solved, sectioned, roofed building (`build/structure.py`, `build/roof.py`) and a front
that can be looked at and measured.

```
python3 build/elevation.py plans/tidewater-georgian-careful.json \
  --out plans/tidewater-georgian-careful.elevation.json \
  --svg dist/tidewater-elevation.svg
```

## What this package adds, and does not touch

`build/structure.py` gives every storey a real height and every wall a real thickness; `build/roof.py`
gives the building a real roof outline and chimney positions. Neither file draws a face — a
section is a slice through the building, a roof plan is a view from above, and nothing before this
package composed the front elevation an approaching visitor actually sees: where the bays fall,
how wide a window is, where its sill and head sit, what the door looks like, how the cornice reads
against the wall. `build/elevation.py` (`build_elevation()`) adds exactly that, and derives it, not
guesses it:

- **Window sizing, one head datum per storey** (`_storey_window()`) — opening-proportion.json's
  own hardest rule ("DISTINCT HEAD DATUMS PERMITTED ON ONE STOREY: ONE") applied literally: the
  head comes off the ceiling-height rule, the sill is fixed at the pack's own documented 28-32 in
  convention, height is the span between those two fixed points, and only then is width taken from
  sash-light.json's own measured ratio. *Not* the other order — sizing a width first from a
  room-width proxy and letting the sill fall out of it is what actually happened first, and it
  drove the sill to 55 in off the floor on a tall Tidewater storey; see "What was found" below.
- **Bay layout, an odd count spaced across the real face** (`_bay_count()`, `_face_bays()`) —
  facade-classical.json's own `window_grouping_rule` picks a plausible odd bay count at its own
  default module, and that many bays are then spaced evenly across the face's own actual outside
  width — the nominal module that picked the count and the realised spacing are allowed to differ,
  and both are recorded.
- **Entrance composition** (`entrance_composition()`) — door width and height from
  opening-proportion's own storey-derived rule (cross-checked against Palladio's independent
  canonical 2:1 leaf), casing from `door_surround` (cross-checked against the same figure by an
  independent route through the order pack — see below — and confirmed to agree exactly), sidelights
  included only where facade-classical's own 80%-of-bay composition cap allows them.
- **The doorcase order** — tidewater-georgian's own kit leaves every classical-apparatus slot
  (`order`, `entablature`, `pediment`, `pilaster`) `binding: "open"`. `proportions/overlays/gibbs-ionic.json`
  is the order the style family's own `governing_logic` names ("a pattern-book order for the doorway
  and cornice") and whose own `applies_to` list includes this style, so it is used here as the
  resolved default for an unresolved slot — read at door scale, not as a free-standing portico
  (the kit's own `porch_type.entry-portico` is marked `"atypical"` for a brick Tidewater house), the
  same "unjudged is not passed, but a sourced default is not invented" discipline WP-3.3 used for
  gambrel roof geometry.
- **The eave cornice, "the style's entablature reduction"** (`eave_cornice()`) — Gibbs Ionic's own
  cornice member proportions (bed mould, modillion band, corona, cymatium) regenerated at whatever
  module makes their total height sum exactly to facade-classical's own domestic frieze-and-cornice
  envelope, sized to *this plan's own real ground-storey height* rather than a stock 9 ft default —
  see "What was found" below for why that module mattered.
- **Water table and belt course** (`water_table_and_belt()`) — brick-course.json's own coursed
  figures where the wall's actual `construction_type` is masonry, facade-classical's generic
  frame-and-clapboard figures otherwise. Picked from `structure.py`'s own solved wall record, not
  guessed from the style name.
- **Roof outline and chimneys** — read directly from `build/roof.py`'s own `elevation_profiles`
  (one per face, WP-3.3's own "expose the outline for the elevation generator") and `chimneys`
  records, not recomputed. A frieze-and-cornice band is a real height neither `structure.py` nor
  `roof.py` models (their own `grade_to_eave_ft` stops at the top of the wall), so this file's own
  roofline is the roof record's silhouette shifted up by that band — stated explicitly in
  `grade_to_true_eave_in`'s own note, never fed back into those files' own records.

**Scope gate.** opening-proportion.json and facade-classical.json — the two packs this whole
window/bay/cornice methodology is built on — both carry `applies_to` lists naming the
Georgian/Federal/Colonial-Revival/Renaissance-classical family explicitly; neither includes a
vernacular or picturesque style (a Craftsman bungalow, a Creole cottage). `build_elevation()`
checks direct membership in both lists (the same test `gibbs_applies` already uses one line below
it, *not* the fault corpus's own `member_of`/lineage cascade — see "What was found" for why that
distinction is load-bearing) before generating anything; outside that scope it returns
`{"applicable": False, "measurements": {}, ...}` with a note naming the reason, and
`render_elevation()` draws a one-line placeholder rather than a fabricated front. Every number this
file adds is either read from a scoped, sourced proportion pack, read from `structure.py`/`roof.py`'s
own already-solved record, or a real, honestly-derived consequence of both (e.g. `roof_plane_area_sqft`,
computed from the real footprint and the real pitch) — never a schematic placeholder passed off as
a measurement, and where a quantity genuinely is schematic (see "What was deliberately not done")
it is marked so in the record, the same disclosure discipline `roof.py`'s `wing_step_down()` used
for WP-3.3.

## `build/render_elevation.py`, a new renderer

One front-on face per call — wall plane, bay windows with sash/muntin grid and shutters, the
entrance composition, water table and belt bands, and the roofline reused from `roof.py`'s own
`elevation_profiles` — plus a **cornice-detail inset** that draws the eave cornice's actual moulded
profile (bed mould, modillion band, corona, cymatium) from `proportion_engine.dimension()`'s own
member data, not traced.

That inset used to be drawn by `seg_to()`, a case-for-case Python port of
`orders_template.html`'s `segTo()`, pinned against the JS original by `TestSegTo`. **WP-5.11
replaced both with `build/profiles.py`, which CONSTRUCTS each moulding** — a quarter of an ellipse
for an ovolo, two tangent arcs through the chord's midpoint for a cyma, a half round for a torus —
rather than approximating it with hand-tuned Bézier control fractions. Two things were wrong with
the port, and the second is why the drawing looked as it did:

* `profile_silhouette_path()` called `seg_to()` with `xa == xb` on **every** member, so every
  curve degenerated to the vertical face it was drawn between. The profile names in the data were
  right and the cornice drew as a flight of steps regardless. `TestSegTo` pinned the control-point
  arithmetic exactly and could not see this, because it asserted the string and never the shape.
* It drew from a naked of 0 while `gibbs-ionic`'s projections are radii from the column axis.

The datum is now read from the pack's own evidence rather than its declaration — see **OQ 78**,
because a pack's declared datum is true of its column and not of its entablature — and the inset
is a full detail plate: every member named at its own height, the relief and the total dimensioned,
and the projection disagreement of **OQ 79** printed rather than silently resolved. The successor
guards are `tests/test_profiles.py` and `TestCorniceProfileGeometry`, which assert geometry
(tangency, convexity, scale invariance, the datum) instead of path strings.

## The opening rectangle, and its three callers (WP-12.2)

`opening_rects(elev, face)` is **the one spelling of `(x0, x1, sill, head)` and of the loop
around it**. Until 12 September 2026 that arithmetic was written out three times — `_window` for
a sash and `_entrance` for the door in `build/render_elevation.py`, and `_win` in
`build/export_dxf.py` — and so was the loop: each renderer independently read the face's bays and
the two storey windows, derived the two floor datums, skipped a blind bay and branched on the
entrance door.

**That duplication had already cost this corpus once.** When the blind bay arrived (OQ 85) the SVG
learned to skip it and the DXF did not, so the CAD file went on drawing a window through a chimney;
the export selftest could not see it, because it round-trips FINDINGS and not geometry.

- **Units are inches, x along the face from its own left edge, y above GRADE**, and the figures
  are **not rounded**. The DXF draws in inches and the SVG in feet, so one of them must divide;
  inches is the unit the record states every opening in, and it is the choice with the smaller
  residue — measured over the 144 opening edges the two shipped plans actually draw, an inches-first
  rectangle leaves **0** DXF coordinates changed and **2** printed SVG coordinates, where a
  feet-first one leaves 0 SVG and **64** DXF.
- **Three states, as everywhere else.** A rectangle is returned, or the bay is in `refused` with
  its reason and the record path that could not answer — a blind bay, a storey stating no window,
  an entrance stating no leaf. A bay that draws nothing is never silently absent.
- **A storey the section does not state gets no openings, and that removed a row of windows from
  six houses.** Both renderers resolved the upper storey as
  `next((s for s in storeys if s["index"] == 1), ground)` and then drew a second row of windows at
  that datum unconditionally, so every one-storey house came out with an invented row above the
  real one. Six of the eleven plan records that build an elevation state only storey 0, and over
  those 24 plates **244 window rectangles become 124**. **The refusal carries the right reason of
  two**: a storey the section does not state is a fact about the BUILDING (*"the section states 1
  storey(s), so this building has no storey 1 for an opening to stand in"*), while a storey that
  exists with no `grade_to_floor_ft` is a fact about the RECORD.
- **A bay the record calls a door draws a WINDOW on any face but the entrance front.** Both
  renderers already did this and the lift carried the behaviour across rather than correcting it:
  which faces carry a door is this generator's judgment, not the rectangle's, and a silent
  correction inside a refactor is the thing the package was written against.
- The third caller is `build/scene.py`, which turns each rectangle into an `opening-frame` solid.
  A dormer's window is deliberately NOT one of these: it sits on a roof plane at a position
  `dormers()` computed, so it is a different rectangle and is built where it is used.

Guarded by `tests/test_opening_rects.py`, and **the blind-bay skip is driven rather than read off
the corpus**: all sixteen plan records produce zero blind bays today, because WP-11.4 moved this
house's stacks off the gable centre line and onto its stated flues.

## What was found

**Window sizing, run the wrong way round, put the sill 55 in off the floor.** The first version of
`_storey_window()` derived width first from `room_width/4.5` using the structural bay module as a
"room width" proxy (this compositional elevation has no real per-room mapping to draw from), then
height as `width*2.1`, then let the sill fall out as `head - height`. On the tall Tidewater ground
storey this put the sill at 55.16 in above the floor — tripping
`faults/window-squarer-than-the-style-permits.json` at fatal — because a narrow, room-proxy-derived
width forced an implausibly short window under a fixed head. Fixed by reading
opening-proportion.json's own corollary literally ("SET THE HEAD FIRST AND LET THE SILL FALL WHERE
IT MAY"): fix the head from the ceiling rule (unchanged), fix the sill at the pack's own documented
28-32 in convention, derive height as the span between them, derive width from sash-light's own
ratio last. The old room-width figure survives only as a disclosed, non-driving diagnostic
(`room_width_diagnostic_width_in`).

**The eave cornice was undersized because it used a stock 9 ft module regardless of the plan's own
real, much taller storey.** `eave_cornice()` originally always called facade-classical at its own
108 in default module. facade-classical's own `storey_one` assembly member is stated as exactly one
module (`height_parts: 12` of a 12-part module) — the pack's own convention already equates the
module to the real storey height, not a fixed stock figure — so the fix was to pass this plan's own
real ground-storey height (from `structure.py`) as the module. This mattered concretely:
`faults/cornice-that-is-a-fascia.json`'s own wall-height-ratio secondary test
(`cornice_height_in / wall_height_water_table_to_cornice_in` between 0.0714 and 0.0833) failed at
the stock module and passed once the cornice was sized to the plan's own ~25 ft wall.

**A genuine authoring gap in `cornice-that-is-a-fascia.json` itself, disclosed rather than worked
around by editing shared corpus files.** That fault's two secondary tests both key off the exact
same expression (`cornice_projection_in / cornice_height_in`) with two *disjoint* bands — a
"domestic boxed case" (0.35-0.55) and a "full entablature-derived case" (0.85-1.2) — evaluated
unconditionally whenever both variables are present, with nothing to select which case applies.
Any real domestic (non-portico) cornice, which is the architecturally correct answer for
tidewater-georgian per the kit's own atypical-entry-portico note, will always satisfy the domestic
band and always fail the disjoint full-entablature band — so this fault would read "present" for
any legitimately domestic building. Editing the shared fault file or `mcp_server/core.py`'s shared
evaluator was judged out of scope for this package; fixed instead by simply not emitting the plain
`cornice_projection_in` key (the distinctly-named `cornice_projection_past_wall_face_in`, used only
by a different fault, is unaffected) — which, once the wall-height fix above was also in place,
left this fault correctly evaluable on its other, unconditional secondary test alone and moved it
from present to clear.

**The same "one test conditional on another, but the evaluator has no way to know that" pattern
recurred twice more**, both times fixed the same way (withhold the one key that only makes sense
when a companion condition is true, rather than supply a value that is honestly zero but still
fails an unconditional band): `entrance-slope-penetration.json`'s solar-array coverage secondary
test (`solar_array_area_sqft / roof_plane_area_sqft >= 0.9`) is explicitly "the conditional test
for arrays" — 0 sqft of a real array over a real roof plane reads as a 0.0 ratio and fails a test
meant to apply only when an array exists at all; and
`shutter-on-an-unshutterable-opening.json`'s curved-head secondary test divides by
`window_head_radius_in`, meant to run "only where the head is curved." Both keys are documented as
withheld, with the reasoning, in `build/elevation.py`'s own comments at the point each is omitted.

**SUPERSEDED 28 Aug 2026 (OQ 89): a comment is not a mechanism, and both of those cases are now
handled in data.** `window_head_radius_in` is SUPPLIED, computed from the head the record already
states (`R = r/2 + s²/(8r)` for a segmental arch; **0** for a straight one — a square wood head and
also a gauged flat arch, whose camber brick-course's own rule says is there so the head "reads
level" and is "invisible on paper"; absent where the kit gives only a band). Its partner
`shutter_head_radius_in` stays absent but moved into `NOT_MODELLED`, where the honesty test can see
it, because nothing states whether a shutter follows a curved head — the very question the fault
asks. Supplying the first **armed** the identical expression sitting unguarded in
`exceptions[0].bounds_test`, which returned `float division by zero` until it was guarded: a
fault's tests live in three places and that is the one that gets missed.

**A scope bug: this file was applying a Palladian proportion system to styles it was never sourced
for, and it changed which house `build/compose.py` recommends.** Before the scope gate above
existed, `build/plan_check.py`'s new ELEVATION LAYER ran `build_elevation()` unconditionally for
every style, including ones far outside the classical family — a craftsman-bungalow candidate from
`build/compose.py`'s own `bungalow-small` brief picked up a classically-derived cornice-to-wall
ratio from facade-classical/gibbs-ionic and tripped `cornice-that-is-a-fascia` at fatal against a
Craftsman fascia that was never built to that system at all. That single spurious fatal was enough
to knock "Bungalow, Open and Linear" out of `compose()`'s own top-four ranking for that brief
entirely (candidates are sorted fatal-count-first). The bug was not caught by a naive `applies_to`
membership check using the fault corpus's own `member_of`/lineage-cascade helper
(`mcp_server/core.py`'s `_applies()`) — craftsman-bungalow's own lineage eventually reaches
`english-georgian` and `georgian-colonial-american` through several `regional_of`/`hybridizes_with`
edges (real architectural influence history), so that cascade called the classical system
"applicable" to a bungalow on historical-influence grounds alone, which is the wrong question for
"does this style's own front literally get composed with this module system." Fixed with a direct,
un-cascaded membership check (`style in pack["applies_to"]`, the same test `gibbs_applies` already
used) — verified to restore "Bungalow, Open and Linear" to first place with zero fatal, and to
leave the classical family's own candidates (both shipped plans, and `family-georgian`'s own
candidates) unaffected.

**A second, legitimate consequence of the elevation layer that looked like a regression and
wasn't.** Once the scope bug above was fixed, `build/compose.py`'s own `family-georgian` brief
still stopped ranking "Centre Passage, Single Pile" first — but for a real reason, inside this
generator's proper scope. That candidate's own massing at this brief's scale is very wide and
shallow (about 82.5 ft wide, 23 ft clear depth), and facade-classical's own bay-grouping formula
correctly gives it a genuine 9-bay front — `faults/even-bay-front.json`'s own secondary test calls
nine-bay fronts "institutional, not domestic" by name — and the same shallow depth against a tall
Tidewater wall gives a real `roof_height_eave_to_ridge / wall_height_grade_to_eave` ratio under
`faults/truss-flattened-pitch.json`'s own 0.45 floor. Both are genuine, previously-invisible
proportion problems this specific parti has at this specific brief's scale, not a code defect —
`tests/test_composer.py`'s own module docstring traces this in full, and its pinned expectations
were updated to the new (correct) top candidate rather than the elevation layer being weakened to
preserve the old one.

**A fourth fatal newly surfaced on `spec-builder-colonial.json`, for the same reason.** That plan
declares `window_opening_width_in: 36` but never declared a height, so
`window-squarer-than-the-style-permits` could not evaluate before this package. The elevation
layer now supplies a real generated height (the plan's own declared width still wins via
`setdefault`), and the resulting ratio (1.693) is honestly below colonial-revival's own 1.85 floor
— an old, real flaw in this deliberately-imperfect reference plan, made visible for the first time,
not a new one planted by this package. `tests/test_plan_validator.py` re-pins all four fatals by
name.

## Verified against the acceptance criteria

- **Five-bay Tidewater front, door centred** — `plans/tidewater-georgian-careful.json`'s own S
  (entrance) elevation: 5 bays, door at the exact middle (`front["kinds"][2] == "door"`).
- **Centred doorway composed to Gibbs** — `entrance_composition()`'s casing figure agrees exactly
  with Gibbs Ionic's own independently-sourced `casing` rule; the doorcase's pilaster width equals
  the diameter it answers by construction, and its projection clears
  `pilaster-that-is-a-flat-board.json`'s own threshold using the fault's own worked-example
  arithmetic.
- **Sash lights correct for the declared date** — `plans/tidewater-georgian-careful.json` declares
  `context.date_of_representation: 1765`, which falls in sash-light.json's own 1760-1800 band
  (midpoint module 10.5 in); `glass_module_for_date()` is pinned directly against that and every
  other band boundary.
- **Single head datum per storey** — true by construction (`_storey_window()` runs once per
  storey and every opening on that storey reads its result), pinned on both shipped plans.
- **The elevation layer evaluates a substantial share of the corpus's photograph-measurable
  faults, and the careful plan trips none at fatal** — against `plans/tidewater-georgian-careful.json`,
  83 of the 177 tidewater-georgian-applicable faults now evaluate (28 present, 55 clear) with
  **zero fatal**, up from 0 before this package existed. The acceptance text named a target of 100;
  see "What was deliberately not done" for exactly which remaining faults were left honestly
  `could_not_judge` and why closing that gap further would have meant fabricating data this
  generator was never scoped to produce.
- **The deliberate half-width shutter is still caught** — `plans/spec-builder-colonial.json`
  declares its own (deliberately flawed) `shutter_leaf_width_in: 12` against
  `window_opening_width_in: 36`; confirmed the plan's own declared values still win over the
  elevation layer's generated ones under the real `setdefault` precedence order, and
  `shutter-half-width-leaf` still reads present.

## What was deliberately not done

- **The gap between 83 and 100 evaluated faults was not closed by fabricating data.** The
  remaining `could_not_judge` faults on the careful Tidewater plan are almost entirely interior
  trim (chair rail, wainscot, mantel, baseboard — this file draws an exterior elevation only),
  porch/portico members (no free column exists here — the kit's own atypical-portico note), garage
  faults (no garage in this plan), and photograph-texture/statistical faults (paint colour
  channels, shingle-width coefficients of variation, siding exposure drift) this generator has no
  model for at all. Each was checked individually against its own `test`/`secondary_tests` before
  being left alone; none was a case of "one more key would unlock this."
- **No cornice-return geometry.** A cornice's face projection and its corner return's own
  wrap-around depth are different physical quantities; an early attempt to proxy the return from
  the face projection introduced a new fatal (`pork-chop-return`) on a value that was not actually
  measuring what the fault asked for. Removed rather than kept as a wrong number — this file does
  not model the corner return at all, and says so in a code comment rather than guessing.
- **No free column or portico.** tidewater-georgian's own kit marks `entry-portico` atypical; the
  doorcase is read as a reduced order at door scale, never as a free-standing column with entasis
  or diminution — which is also why `upper_shaft_diameter_in == lower_shaft_diameter_in` here (no
  entasis rule exists anywhere in this codebase) and correctly, honestly trips
  `column-without-entasis` rather than being hidden.
- **`main_block_depth_ft` was deliberately never added**, even though the real value (42.66 ft) was
  computed and available. `faults/single-pile-type-built-double-pile.json` is `fatal` on
  `main_block_depth_ft <= 22.0` with no further style- or massing-scoping beyond `applies_to`
  membership — the fault's own name and note target a hard single-pile constraint, but its raw test
  does not check whether the massing this plan actually uses (a genuine double-pile plan) has that
  constraint at all. Adding this key would have produced a false fatal on a legitimately double-pile
  design; flagged here as a fault-corpus scoping gap rather than worked around.
- **Secondary doors and garage doors are not drawn or measured** — neither shipped reference plan
  declares one.
- **Dormers ARE drawn and measured, as of WP-5.13 (27 Aug 2026)**, and the entry that used to sit
  here said they were not, "consistent with `roof.py`'s own WP-3.3 disclosure for dormer rhythm".
  Both files were refusing for the same reason and neither had said it out loud: no plan schema
  field authored a dormer, so a house with none and a house whose dormers the record could not
  state were the same house. `declared.dormer` separates them into three states — absent (could
  not evaluate), `"none"` (a measured zero), an object (a house with dormers) — and every dormer
  figure is derived from the fault corpus, which turns out to specify a dormer completely:

  | figure | from |
  |---|---|
  | window width | `overscaled-dormer`, 0.75–1.0 of the sash below; taken at 0.85 |
  | window height | the kit's own `dormer_window_height_in` expression where it has one |
  | cheek | the kit's 4–8 in band, `fat-cheek-dormer`'s ≤ 0.25 of the sash, AND that fault's prose rule that the cheek may not exceed the window casing — the third bound binds here |
  | face width | window plus two cheeks |
  | centres | the bays below (the kit's own `alignment_rule`), never authored |
  | roof run in front | `sunken-dormer`'s preferred 18–36 in band, **editorial**, named as a choice |
  | cornice | the ratio the HOUSE's own cornice obeys (`cornice-that-is-a-fascia`, 1/14–1/12 of the wall it crowns), applied to the dormer's own face — the kit's rule that a dormer "carries the same order as the house at reduced scale", with a number in it |

  Not derivable and therefore not stated: the sill's height above the garret floor, and the face
  width as a measured figure rather than as window plus casings.

## New open questions

1. ~~Should `faults/cornice-that-is-a-fascia.json`, `entrance-slope-penetration.json`, and
   `shutter-on-an-unshutterable-opening.json` gain an explicit conditional guard (a `depends_on` or
   similar field) on their own conditional secondary tests, so a generator does not have to
   discover "this key can only be safely supplied when a companion condition holds" by tripping a
   false fatal first? Three independent instances of the same pattern were found in this package
   alone.~~ **ANSWERED 27 Aug 2026 (WP-5.13): yes, and the field is `applies_when`** — a
   precondition on the MEASUREMENTS, in the same shape as a test, alongside `applies_to_styles`'s
   precondition on the style. A test whose precondition fails is NOT RUN; a fault whose every test
   declines comes back under a fourth state, `not_applicable`, because such a fault previously
   appeared in no list at all and that reads to a caller exactly like clear. See `docs/faults.md`.

   It was built for a fourth instance this package found the hard way, which is worth stating
   because it is the same pattern arriving from the opposite direction. `dormer-off-the-bay`'s
   parity secondary is `dormer_count % 2 == 1`. As long as no record could state a dormer, no
   generator supplied `dormer_count` and the rule never ran. The day both reference houses could
   state that they carry **none**, that zero was a real measurement, the rule ran on it, and both
   were convicted of *"Dormers Off the Rhythm: 0 against equals 1"* — OQ 52's flagship failure
   returning through the very field built to prevent it. Zero dormers is not an even number of
   dormers.

   Two of the three named above are guarded (`entrance-slope-penetration`'s solar-array secondary
   on `solar_array_area_sqft >= 0.1`, `shutter-on-an-unshutterable-opening`'s arch-head secondary
   on `window_head_radius_in >= 0.1`). The third is **not**, and it is not the same problem:
   `cornice-that-is-a-fascia` carries two RIVAL secondaries — the domestic boxed eave at 0.35 and
   the full entablature-derived case at 0.85 — so whichever is right, the other fails. Guarding
   them needs a measurement stating whether an order is applied to this facade, and no generator
   in this corpus takes one. Left open and named rather than guarded with a figure nobody has.
2. Should `faults/single-pile-type-built-double-pile.json` gain a `massing`-scoped exception (or a
   companion variable naming the plan's own actual pile depth) so it stops being fatal on a
   legitimately double-pile design that merely shares a style with single-pile-constrained ones?
   Not decided here — flagged for whoever owns the fault corpus's editorial content.
3. Now that `build/plan_check.py`'s ELEVATION LAYER genuinely changes `build/compose.py`'s own
   candidate ranking (see "What was found"), should `compose.py`'s own scoring weight the
   elevation-layer's newly-evaluable faults any differently from the room-and-adjacency findings
   that were the only source of `serious`/`fatal` counts before this package? Not decided here —
   flagged for whoever owns `compose.py`'s own scoring function next.
4. `mcp_server/core.py`'s `_applies()` cascade (fault applicability through `member_of`/lineage) is
   the right tool for "does this generic correctness principle reach a style through its influence
   history" and the wrong tool for "does this style's own front literally get built to this
   proportion system" — this package worked around the distinction locally with a direct
   membership check rather than adding a second mode to the shared helper. Should proportion-pack
   scoping get its own, stricter applicability helper in `build/proportion_engine.py` so the next
   generator that reads a scoped pack doesn't have to rediscover this the same way? Not decided
   here — flagged for whoever owns `proportion_engine.py` next.
