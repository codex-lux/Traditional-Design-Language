# Site & settlement (WP-2.4)

*A style is not only a building. Detached from its settlement pattern it becomes a costume* — `elements/slots.json`'s own note on the Site & Settlement slot group, and the reason this layer exists at all. Everything above this doc — the room catalogue, the constraint corpus, the composer, the geometry solver — can produce a building that is correct in every internal measurement and still be wrong for its lot: a five-bay Georgian does not fit a 40 ft town lot, however faithfully its bays are proportioned.

## What was added

**`schema/plan.schema.json` and `schema/brief.schema.json` both gained a `site` object.** `context.lot_width_ft`, `context.lot_depth_ft` and `context.entrance_faces` were not moved — they were established first (WP-0.1) and are already load-bearing across the 14-record reference corpus (`plans/reference/`) and the composer's own tests, and moving them would have broken all of that for no gain. `site` instead holds the fields this package actually needed and `context` never had: `street_bearing_deg`, `setback_front_ft`/`setback_side_ft`/`setback_rear_ft`, `slope_direction_deg`, `cross_slope_pct`, `prevailing_summer_wind_deg`, `piazza_bearing_deg`, `party_wall_condition` (`freestanding` / `party-wall-one-side` / `party-wall-both-sides` / `row`), and a free-text `note`. A plan or brief that states no site data simply omits the object — nothing requires it, and every existing plan record keeps validating unchanged.

This is a real deviation from PLAN-OF-ACTION.md's literal phrasing ("Extend `brief.schema.json` and `plan.schema.json` with a `site` object: lot width and depth, street bearing, setbacks…" reads as though lot width belongs on the new object too). It is named here rather than silently done, in keeping with this session's practice everywhere else a brief's letter and its intent diverged (see `docs/constraints.md`'s `CONSTRAINT_SEV` note for the same discipline applied to WP-1.2). `derive_constraint_vars` and the composer both read `lot_width_ft`/`lot_depth_ft` from `context` first, falling back nowhere else — there is exactly one place a plan states its lot size.

**`build/constraint_vocabulary.py`'s site scope grew by four names**: `setback_side_ft`, `setback_rear_ft`, `slope_direction_deg` (the compass bearing of the downhill direction, distinct from `cross_slope_pct`'s magnitude), and `prevailing_summer_wind_deg`. The site scope was seven names before this package (`lot_width_ft`, `lot_depth_ft`, `street_bearing_deg`, `piazza_bearing_deg`, `party_wall_condition`, `setback_front_ft`, `cross_slope_pct`) and is eleven now — coincidentally close to, but not the same list as, `elements/slots.json`'s seven site-and-settlement *slots* (`street_relationship`, `setback_rule`, `orientation_rule`, `outbuilding_types`, `fence_wall`, `landscape_idiom`, `grade_relationship`). The two sevens are different things that happen to share a headline number: one is constraint-test variables a plan or site states as a fact, the other is kit-of-parts slots a *style* binds. Worth not conflating them in conversation even though PLAN-OF-ACTION.md's own prose sits them next to each other.

**`build/plan_check.py`'s `derive_constraint_vars`** now folds every key of `plan.site` straight into the constraint namespace, the same way it already did for `context.lot_width_ft`/`lot_depth_ft`. This is the same "unambiguous plan structure, not an inference" discipline WP-1.2 established: every `site` field is a fact the plan record itself asserts, so it passes through unconditionally; a plan that omits `site` leaves those constraints exactly as unjudged as before, never silently passed.

That one change is what made the two already-migrated site-scope constraints evaluable for the first time: `charleston-georgian.c01` (the piazza must face within 45° of southwest) and `pennsylvania-bank-house.c01` (cross-slope at least 1:8). Both existed since WP-1.1 with a real `test`, and both sat permanently `unjudged` before this package because nothing fed `context`/`site` data into the namespace `_eval_test` reads — the mechanism from WP-1.2 was already generic enough to cover them the moment the data had somewhere to come from. `tests/test_site.py`'s `TestSiteScopeConstraintsEvaluate` pins both directions (a piazza facing southwest clears; one facing northeast fails at `serious`, per `CONSTRAINT_SEV["hard"]`).

**PLAN-OF-ACTION.md names two other site-scope examples** — "the Tidewater chimney position relative to the prevailing wind, the Creole gallery orientation" — that this package deliberately did *not* wire up, because they don't exist as evaluable data yet. `tidewater-georgian.c01` is a real, migrated constraint about chimney position, but it is `scope: elevation`, has no wind term in it, and is prose describing gable-end placement, not a bearing comparison. No Creole style (`creole-cottage-vernacular`, `raised-creole-plantation`) has *any* migrated constraint at all — WP-1.1 migrated two families (`english-classical`, `american-colonial`) of the corpus's ~27; Creole is not one of them. `prevailing_summer_wind_deg` is in the vocabulary now, named and ready, specifically so that whichever future migration batch reaches the Tidewater or Creole families can write that test without a second vocabulary pass — but nothing references it yet, and this doc does not pretend otherwise.

## The composer: honouring lot width

**`build/compose.py` gained `lot_usable_width_ft(plan)`**: `site.lot_width_ft` (falling back to `context.lot_width_ft`) minus both side setbacks, or `None` if the plan states no lot width at all — `None` means "unconstrained," never "zero." `footprint(plan, parti)` uses it to cap the bay count a candidate may reach, independent of the parti's own catalogue `max_bay_count`:

- If the lot allows fewer bays than the parti's catalogue maximum, the candidate is simply narrower than it would otherwise be, with a note explaining why (`"Lot caps this diagram at 3 bays instead of its usual 7…"`).
- If the lot cannot hold even the diagram's minimum of 3 bays, `footprint()` flags `lot_infeasible: true`, and `compose()` drops that candidate entirely — not merely outscores it. It is recorded in the result's `dropped_lot_infeasible` list (parti id, name, and the reason) rather than vanishing silently; `how_to_read_this` gains a line naming how many were dropped when any were.

Tested directly against PLAN-OF-ACTION.md's own example: a 40 ft lot with 5 ft side setbacks (30 ft usable) run through `briefs/family-georgian.json` (style `tidewater-georgian`) caps `five-part-palladian` (catalogue max 7 bays at a 9 ft module) down to 3 bays, drops `foursquare-quadrant` entirely (its 13 ft module needs 39 ft for even 3 bays), and lets `side-hall-townhouse` through unchanged at its natural 3 bays × 8 ft = 24 ft — the brief's own "24 ft town-house parti for a 30 ft lot" illustration, reproduced almost exactly. `tests/test_site.py`'s `TestComposerHonoursLotWidth` pins all three outcomes.

## The geometry solver needed the same fix, independently

`build/compose.py`'s `footprint()` is a quick area/bay estimate used to rank and describe candidates; `build/geometry.py`'s `solve()` is the actual bay-grid placement that gets rendered, and it derives its own bay count from the massing's pile depth (`PILE = {"single-pile": 22.0, ...}`) with **no knowledge of compose.py's estimate at all**. Building this package's first end-to-end smoke test (`compose → geometry.solve → render_plan.render`, rendered to PNG and inspected) surfaced this directly: a "Side-Hall Town House" that compose.py's own `footprint()` correctly estimated at 24 ft wide came back from `geometry.solve()` at **50 ft** — wider than the 40 ft lot itself, drawn straddling the lot line in the rendered SVG. Two independent footprint estimators, one lot-aware and one not, is not a defensible state for a system whose stated purpose is that the drawing is a render of the data (`render_plan.py`'s own docstring: "if a dimension is wrong the picture is wrong in the same way, which is the point").

`geometry.py` gained its own `lot_usable_width_ft(plan)` — a second copy of the same four-line rule rather than an import of compose.py's, because `geometry.py` is loaded standalone via `_mod()` everywhere in this codebase (every test's `geometry_module` fixture, `main()`'s own CLI) and importing the composer into it would pull in the composer's own full corpus load for one helper function. If the two ever drift, that is a real risk worth naming rather than hiding behind a shared import; it is named here, at both call sites, precisely so it gets noticed.

The fix needed more care than a simple cap on the starting bay count, because `solve()`'s own growth loop already has a deliberate escape hatch: it is allowed to grow up to 3 bays *past* the parti's catalogue maximum rather than leave a room too deep (`"grow the footprint before compromising a room — the stated infeasibility ordering"`, the existing comment). A first attempt at this fix capped only the *starting* bay count and left that growth loop's ceiling untouched, which meant a lot-capped starting point of 3 bays could still grow back out to 6 under exactly the same escape hatch — silently erasing the cap it had just applied. The actual fix distinguishes `catalog_maxbay` (the parti's own stated maximum, which the growth loop may still exceed by up to 3, unchanged from before this package) from the lot's cap (a physical fact, not a diagram convention, which bounds that growth loop too — `growth_ceiling = min(catalog_maxbay + 3, lot_maxbay)`). A lot too narrow for even the diagram's minimum 2 bays returns an honest `{"error": "lot too narrow: …"}` rather than a silently oversized or malformed placement. `plan["footprint"]["lot_usable_width_ft"]` and `geometry_report["lot_capped"]` record what happened when a lot was involved at all; a plan with no lot data behaves exactly as it did before this package (`tests/test_site.py`'s `test_unchanged_when_plan_has_no_site_data`, which also re-pins `test_geometry.py`'s own 11-relaxation count on the shipped Tidewater plan to prove nothing regressed for the no-lot case).

## WP-11.6 (5 Sep 2026): the cap is on the BUILT EXTENT, and two things were still crossing it

**This section supersedes the paragraph above wherever they disagree**, and the paragraph is kept
because its reasoning is why: WP-2.4's argument that the lot "is a physical fact, not a diagram
convention" is the argument this change finishes.

`oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it` item 2, ruled 4 September
2026: **the lot cap is on the built extent, hyphen included** — *"the hyphen is roofed ground; a
building whose covered area overruns its lot has overrun it"*. `derive_footprint` subtracts
`flanking_extent_ft(prep, bay)` from the usable width before deriving `lot_maxbay`, and that
function sums `gap + width` per flanking element from `flank_sizes`, which is the sizing
`blocks_for` already did, lifted out so the cap and the placement read one spelling. Measured on the
Tidewater plan with its service rooms tagged into a west dependency: an 80 ft lot got a **104 ft**
built extent (`lot_capped: false`) and now gets **86 ft** (`lot_capped: true`).

**Two other things were crossing the cap, and only one of them involved massing elements at all.**

1. **The centre-bay parity bump.** WP-11.2 added `if odd_wanted and start % 2 == 0: start += 1`,
   which never consulted `maxbay`. On a **one-rectangle** plan — every plan in this corpus — a lot
   holding six bays built seven, 63 ft on 60 ft. It also made a named refusal unreachable:
   `bay_count_forced_even`'s own comment says *"today the only way here is a lot too narrow to hold
   the odd count"*, and the bump forced the count odd before the lot was consulted while both the
   growth and shrink loops step by two, so `bays % 2 == 0` could never occur. The bump is clamped
   to `lot_maxbay` and the refusal fires for the first time.
2. **The massing's own stated minimum bay count**, which is NOT capped and is disclosed instead.
   `start = max(mb["min"], from_area)` does not consult `maxbay`, so `four-over-four`'s stated five
   bays are built on a lot holding four — 45 ft on 36 ft. Shrinking a main block below the count its
   own massing states is decision #11's ordering run backwards, and nobody has ruled that a lot
   outranks a diagram's floor. `oq/a-lot-too-narrow-for-the-diagrams-own-minimum-bay-count`.

**`geometry_report.lot` is the record, on both engines, in three states.** It carries
`usable_width_ft`, `main_block_ft`, `flanking_ft`, `built_extent_ft`, `over_ft` and a `note`. A plan
that states no lot width gets `over_ft: null` and COULD NOT EVALUATE — the extent is a fact and is
still reported, and nothing is claimed to fit. Where the residue is the massing's floor, the note
names the floor, the count the lot holds and the question above.

**`lot_capped` is kept and is still a boolean about the bay count**, now derived from a
flank-aware `lot_maxbay`. It should not be read as "this house fits its lot": it was published as
`false` over a built extent 24 ft wider than the lot it names, which is what raised all of this. Read
`geometry_report.lot.over_ft`.

## The renderer: showing the lot

`build/render_plan.py`'s `render()` draws, for each level, when the plan states both `lot_width_ft` and `lot_depth_ft` (from `site`, falling back to `context`):

- A dotted lot boundary, sized to the stated lot, with a `LOT W x D` caption.
- A dashed buildable-envelope rectangle, inset from the lot by the front/side/rear setbacks (falling back to a centred guess for whichever setback the plan didn't state).
- A real north-arrow glyph (not just the existing "north is up" caption) plus, when `site.street_bearing_deg` is stated, the bearing itself as text.

A plan with no lot data renders byte-for-byte as it did before this package — every `extra_*` margin computed for the lot defaults to zero, and the existing "north is up" caption is preserved unchanged as the fallback when no bearing is stated (`tests/test_site.py`'s `test_svg_has_no_lot_markup_when_no_site_data`).

**Two simplifications, named rather than hidden.** First, the building is placed inset from the lot's south edge by `setback_front_ft` — the renderer assumes the street is south, which matches this file's own pre-existing coordinate convention (the window-wall logic already treats `S` as the exterior-facing edge closest to y=0) but is not derived from `entrance_faces` or `street_bearing_deg` in any way; a house whose entrance actually faces north would still be drawn with its "front" setback measured from the south edge. Second, `street_bearing_deg` is reported as a **label**, not used to rotate the drawing — the room rectangles are axis-aligned to the model frame (bay lines run parallel to the canvas), and physically rotating a rectangular bay-grid render to true north while keeping every wall axis-aligned on screen is a materially larger piece of work than this package's stated scope. Both are recorded here as the honest state, not silently declared "done."

## Kit-of-parts consumption

PLAN-OF-ACTION.md: *"Consume the seven site-and-settlement slots where a kit specifies them."* Two different mechanisms end up covering all seven, and only one of them is new to this package.

Five of the seven — `street_relationship`, `outbuilding_types`, `fence_wall`, `landscape_idiom`, `grade_relationship` — are `binding: specified` slots with a set of variants, exactly the shape `build/compose.py`'s existing `canonical_choices(style)` already handles generically for every slot group in the kit, not just site. That function predates this package; it was simply never checked against the site group specifically until now. `tests/test_site.py::TestSiteAndSettlementSlotConsumption::test_canonical_choices_already_covers_five_of_seven_site_slots` confirms it does, for `georgian-colonial-american` — the one style whose kit currently authors the site group at all (`tidewater-georgian` inherits two of the five, `grade_relationship` and part of `orientation_rule`'s reasoning, via `extends`; every other style's kit leaves the whole group untouched, `status: empty`).

The other two are not variant-shaped, and were falling through `canonical_choices()` with no trace at all. **`orientation_rule`** is `parameters`-only editorial prose (a `governing_factor`, a `chimney_axis`, a `passage_axis` — text describing *why* a Georgian house orients to its approach rather than the sun, not a value the composer's own room placement reads). **`setback_rule`** is deliberately `binding: open` on the one style that says anything about it — the kit's own note calls it "the cleanest open in the kit": the same Georgian grammar sits on the street line in Annapolis and at the end of a half-mile approach at Westover, and the corpus is right not to invent a number. This package added `site_kit_log(style)`, called from `instantiate()`, which surfaces both into the plan's own decision log — the same `decisions` list a human reads to see what the composer assumed — rather than letting them disappear. It deliberately does **not** compute anything from `orientation_rule`'s prose into the plan's actual room placement; that would be inventing a rule the kit itself left as narrative.

## What was deliberately not done

- **No rotation of the render to true north.** Discussed above; the building stays axis-aligned to the model frame and `street_bearing_deg` is reported as text, not applied geometrically.
- **The "front is south" assumption is not derived from `entrance_faces`.** A future package could make the renderer choose which lot edge is "front" from `entrance_faces`/`street_bearing_deg`; this one keeps the existing single convention and states it plainly instead.
- **The Tidewater chimney/wind and Creole gallery-orientation constraints PLAN-OF-ACTION.md names are not written.** They are not migrated constraints yet at all (Tidewater has a chimney constraint with no wind term; Creole has no migrated constraints of any kind), and authoring them was not this package's job — that belongs to whichever future batch migrates those families under WP-1.1's own methodology. `prevailing_summer_wind_deg` exists in the vocabulary now so that batch does not also need a vocabulary pass.
- **`setback_rule`/`orientation_rule` consumption stops at the decision log.** Nothing in `compose.py`'s room placement or `geometry.py`'s bay-grid solve reads `orientation_rule`'s chimney-axis or passage-axis prose to influence a layout choice — WP-2.2's compositional-constraint work (entrance-front placement, principal-room orientation) is the layer that would eventually act on this, not the site layer itself.
- **No plumbing-through of `site.slope_direction_deg`/`prevailing_summer_wind_deg` into any downstream computation** beyond being an evaluable constraint variable — no style constraint currently references either, so there is nothing yet to compute.

## Tests

`tests/test_site.py`, six classes mapped directly to the pieces above: `TestSiteSchema` (the `site` object validates and rejects what it should), `TestConstraintVocabularyAndDerivation` (the four new vocabulary names, and `derive_constraint_vars` reading `plan.site`), `TestSiteScopeConstraintsEvaluate` (the Charleston piazza and Pennsylvania bank-house constraints, both directions, plus the no-data-stays-unjudged case), `TestComposerHonoursLotWidth` (the acceptance criterion itself, plus the dropped-not-outscored case and the unconstrained-lot regression check), `TestGeometrySolverHonoursLotWidth` (the independent solver-level fix, including the no-site-data regression check against `test_geometry.py`'s own pinned relaxation count), `TestRenderShowsTheLot` (lot markup present/absent), and `TestSiteAndSettlementSlotConsumption` (all seven slots, both mechanisms). 29 tests, all passing alongside the full existing suite (140 total after this package).
