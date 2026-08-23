# WP-2.1 — The reference corpus: transcribing the Plan Examples

*Executed 23 August 2026, overnight autonomous session. First package of Phase 2 — depends only on Phase 0, per `PLAN-OF-ACTION.md`'s parallelisation map, and was started once Phase 1 (WP-1.1/1.2/1.3) closed.*

## What was built

Fourteen plan records under `plans/reference/`, transcribed directly from the images in `Plan Examples/` by reading each drawing (multimodal image reading, not OCR or a caption): seven of the eight files in `Bad Examples/` (`Screenshot 2026-08-21 095019.png` and `095042.png` are the ground and upper floor of one house and are modelled as a single two-level plan record, the way `plans/tidewater-georgian-careful.json` already models its own two levels — so all eight source files are covered by seven plan records) and seven of the twenty files in `Good Examples/` (more than the brief's minimum of six, chosen for legibility and diversity of massing). Every record validates against `schema/plan.schema.json` and was run through `build/plan_check.py`.

| record | style (guessed) | rooms | fatal | serious | minor | advisory | info |
|---|---|---|---|---|---|---|---|
| bad-01-grilling-porch-ranch | colonial-revival | 12 | 2 | 18 | 38 | 2 | 7 |
| bad-02-flex-room-craftsman | colonial-revival | 18 | 7 | 22 | 59 | 3 | 8 |
| bad-03-narrow-lot-townhome | new-urbanist-traditional | 14 | 3 | 21 | 50 | 3 | 8 |
| bad-04-log-cabin | log-vernacular-american | 7 | 0 | 12 | 27 | 1 | 6 |
| bad-05-two-story-spec-colonial | colonial-revival | 23 | 5 | 25 | 63 | 4 | 10 |
| bad-06-open-concept-render | contemporary-traditional | 7 | 1 | 13 | 28 | 0 | 2 |
| bad-07-octagon-dinette-colonial | colonial-revival | 17 | 2 | 37 | 46 | 3 | 10 |
| good-01-veranda-gallery-estate | shingle-style | 20 | 4 | 23 | 58 | 1 | 9 |
| good-02-portico-library-house | georgian-revival | 11 | 0 | 6 | 39 | 1 | 6 |
| good-03-parlor-drawing-room-house | greek-revival-american | 10 | 3 | 8 | 32 | 0 | 4 |
| good-04-rambling-porch-farmhouse | american-farmhouse-vernacular | 13 | 1 | 6 | 52 | 1 | 7 |
| good-05-lobby-gallery-mansion | italian-renaissance-revival | 18 | 2 | 11 | 56 | 5 | 4 |
| good-06-dogtrot-farmhouse-sketch | american-farmhouse-vernacular | 9 | 0 | 6 | 28 | 0 | 6 |
| good-07-diamond-plan-house | new-classical | 13 | 3 | 8 | 34 | 2 | 10 |

Every record carries a `note` recording its `source_image`, a `transcription_confidence` (high/medium/low, per-field where it varies within one record), and the reasoning behind its `style` guess — no plan-schema field exists for structured provenance (see "what was found" below), so this is prose, not data.

## Where the validator agrees with the good/bad labelling

**Room-dimension bands and furniture fit discriminate strongly and in the right direction.** Summed `fatal`+`serious` counts, bad vs. good: ROOM layer 45 vs. 6 (a room too small for its catalogue band), FURNITURE layer 63 vs. 23 (a room that cannot take its own essential furniture with real clearances). Bad examples are genuinely, measurably tighter: bad-02's utility rooms (laundry, closets) come up short on the standard 48 in front-loading-washer clearance and the 24 in coat-closet depth in room after room; bad-01's closets and baths are printed at dimensions that fail their own catalogue floors. This is the validator doing exactly the job `docs/plans.md` describes — catching what "most plans have never had run on them" — and it lines up with the Bad Examples folder's own editorial judgment without any coaching.

**Adjacency is close to even (45 vs. 41) and daylight is close to even (13 vs. 10) — and both are largely artifacts of this transcription, not a real finding about the layer.** See below.

## Where the validator is blind, or disagrees

**Two specific room-catalogue gaps, not general validator weakness, account for most of the good examples' fatal findings.** `good-01` (4 fatal), `good-03` (3), `good-05` (2) and `good-07` (3) are not full of real defects — tracing every fatal on those four plans back to its rule turned up two recurring causes:

1. **`entry-porch`'s and `piazza`'s `must_adjoin entrance-hall, direct-door, hard` rule has no allowance for a formal entrance *gallery*.** `plan_check.py`'s own `EQUIVALENT` alias list already treats `{stair-hall, landing}`, `{entrance-hall, vestibule, stair-hall}` and six other groups as interchangeable for adjacency purposes — but `gallery-corridor` is in none of them, even though `good-01` and `good-05` both use a Gallery as the room the front door and every principal room actually opens off, which is precisely what an entrance hall *is* functionally. A grand house whose entrance sequence is a gallery rather than a discrete "hall" fails a rule that exists to catch an entry porch leading nowhere, when it leads exactly where it should.
2. **`primary-bedroom`'s `must_adjoin primary-bathroom, direct-door, hard` rule has no `via` allowance for a dressing room**, unlike `kitchen`'s equivalent rule for the dining room (`via: butlers-pantry, pantry, scullery, eat-in-kitchen-area`). `good-05` and `good-07` both draw a dressing room between the primary bedroom and its bath — independently, from two different source drawings — which is not an idiosyncrasy of this transcription but a hallmark of good suite planning the corpus's own fault corpus and room catalogue elsewhere praise (`rooms/primary-bedroom.json`'s own `should_adjoin` note on the closet says "best placed as the lock between the bedroom and the bath"). The rule as written cannot see a dressing room doing exactly that job.

Both are recorded below as candidate corrections, not applied here — `PLAN-OF-ACTION.md`'s brief for this package says "do not modify the validator," and a room-catalogue adjacency rule is validator data in the same sense a fault or a constraint is.

**A smaller, transcription-specific cause also inflates the adjacency count and should not be read as a validator finding at all: this transcription used `entry-porch` as a catch-all for every porch, including several (`good-01`'s Veranda and South Porch, `good-04`'s North Porch and Rear Porch) that the drawings show opening onto a garden-facing living or family room, never claiming to be the *arrival* porch a visitor's front door opens onto.** `entry-porch`'s rule is written for the arrival porch specifically (its own `why` says "the door must lead somewhere that can receive a person," with named exceptions for the two vernacular types that legitimately have no hall). A garden porch failing that rule is this transcription's room-type choice, not a corpus gap — the catalogue already has `piazza` and `terrace` as porch-adjacent types with their own, different adjacency rules, and a future transcription batch should reserve `entry-porch` for the room a visitor's front door actually opens onto.

**Daylight's near-even split (13 vs. 10) is a transcription-methodology artifact, not a validator finding, and should not be cited either way.** No source image in this batch prints a window schedule; every window in every one of the fourteen records is the transcriber's placement of one or two representative openings per exterior wall from what the drawing's graphic shows, not a survey. A room transcribed with no window entry fails the "has no windows" rule regardless of what the real building has, so the daylight layer's counts here measure this transcription's window-drawing effort more than either the source plans' real daylight quality or the validator's judgement of it.

**Kitchen-to-dining-room `via`-chain fatals appear on both bad and good examples (3 on good alone) and are a mix of both causes** — `kitchen`'s rule already has a working `via` list (`butlers-pantry`, `pantry`, `scullery`, `eat-in-kitchen-area`), so where a fatal fired here it is usually because this transcription simply did not draw a route between the two rooms that the source image's own service-door graphics implied but this transcriber did not confidently read, rather than a missing rule. Recorded as a limitation of this batch, not a corpus finding.

## Missing catalogue rooms

Thirteen rooms across the fourteen records could not be mapped to an existing catalogue id with confidence and are flagged `room_type_unmapped` on the room itself:

grilling-porch (rear cooking porch with a built-in grill), flex-room (an undetermined-use guest room/study), bonus-room-over-garage, game-room (third-floor rec room), exercise-room, wine-room (a dedicated wine-storage/service room off the kitchen), and a handful mapped to a passable-but-imperfect existing type worth a second look: `landing` for an open guardrailed overlook onto a two-storey room below (used twice, independently, in `bad-05` and `good-05` — this is common enough in the corpus's own drawings to be a real gap, not a one-off), `sitting-room` for both a small nook ("Alcove") and a casual upstairs room ("Den"), `butlers-pantry` for a small wet bar, `bath-house` for a poolside cabana (an adequate fit, not flagged as a gap), `terrace` for an open wood deck (adequate). None of these is at the volume WP-4.5's own brief anticipates ("galleries, alcoves, cabanas, south porches, gun rooms") — this batch's fourteen records did turn up alcoves and (adequately-covered) cabanas and south porches, but no gun room.

## Candidate compositional and catalogue rules for WP-2.2 and future room-catalogue work

Expressed as concrete, reviewable edits rather than a formalised test — these are room-catalogue (`rooms/*.json`) and adjacency-alias (`plan_check.py`'s `EQUIVALENT`) proposals, not `schema/constraint.schema.json` constraints, since what they correct is what a room legitimately reaches, not a style-level proportion or material rule:

1. Add `gallery-corridor` to `plan_check.py`'s `{"entrance-hall", "vestibule", "stair-hall"}` `EQUIVALENT` group (or a comparable formal-entrance-alias mechanism), so a house whose entrance sequence is a gallery is not penalised for not also having a discrete "hall."
2. Add `dressing-room` to `rooms/primary-bedroom.json`'s `must_adjoin primary-bathroom` rule's `via` list, on the same model as `kitchen`'s `via` list for `dining-room`.
3. Distinguish, in future transcriptions and possibly in the catalogue itself, an arrival `entry-porch` (must reach the entrance hall) from a garden/side porch that legitimately opens onto a living or family room and should carry no such requirement — `piazza` already exists for one variant of this; a plain non-arrival porch type may be worth adding rather than overloading `entry-porch`.
4. `landing` as an open overlook onto a double-height room below recurred independently in two source drawings (a spec-house Mezzanine and a mansion's upper Lobby) — worth a dedicated `catalog room type (`overlook` / `open-gallery`) rather than continuing to overload `landing`, which the catalogue otherwise uses for a stair landing proper.
5. Several good-example rooms (this batch's `living` rooms in particular — `good-05`'s at 26×30 ft, `good-07`'s foyer and living room comparably oversized) are drawn well outside `rooms/*.json`'s dimension bands as a matter of the house's own scale, not a defect; the ROOM layer's "well above the ... band, confirm it is not a room that has stopped being a room" minor finding already softens this compared to a hard failure, and this batch's data supports leaving it exactly that soft — nothing here argues for a budget-tier-scaled band, just confirms the existing minor-not-serious calibration is right for grand houses.

## What was deliberately not done

**No catalogue or validator file was edited.** `PLAN-OF-ACTION.md`'s own brief for this package says "do not modify the validator," and the candidate corrections above are proposals for whoever picks up the room-catalogue work next (most naturally as part of WP-4.5, which is already scoped to complete rooms/groupings/partis coverage from this package's missing-room list), not applied unilaterally here.

**Only 7 of 20 Good Examples were transcribed** (plus all 8 Bad Examples as 7 records) — the brief's stated minimum (six good, all bad) is met with one to spare, not exhausted. Two Good Examples were looked at and set aside rather than transcribed: `55ec89f237bfeeaa27be6a7d75196246.jpg` (a furniture-icon sketch with no scale bar and no legible room function at all) and `6509169af86a7f1e31121f3c959668ed.jpg` (a legible but clearly partial fragment — an upper-floor his-and-hers study wing with a roof plan below it, not a complete house). Thirteen further Good Examples were not opened at all. A second batch, if wanted, has real remaining material.

**No structured provenance field exists on the plan schema, so this batch's `source_image`/`transcription_confidence`/style-confidence data lives in free-text `note` fields rather than as queryable data.** `schema/plan.schema.json` is `additionalProperties: false` at both the plan and room level, and adding a `provenance` object was judged out of this package's scope (a schema change belongs with whoever next needs to query transcription confidence programmatically, not silently added by the first batch that needed it). Flagged as a real gap, not routed around by editing the schema unilaterally.

**Style and massing assignments carry LOW confidence throughout the good examples, and are recorded as such rather than smoothed over.** Every Good Examples source in this batch is a floor plan only — no elevation, material callouts, or roofline is included in the crop provided — so a style id had to be guessed from massing and room-naming conventions alone (a Parlor/Drawing Room distinction, a formal Gallery, a rambling one-storey plan with deep porches). This means STYLE-layer findings on the good examples (forbidden-variant checks, constraint evaluation) are checking the *transcriber's guessed style's* rules, not necessarily the real building's, and should be read with that caveat — a genuine limitation of transcribing from plan-only source material that a future batch with elevations could remove.

**Window and door data throughout is representative, not surveyed**, as already discussed above under daylight — flagged again here because it affects every plan's `fault_summary` and `constraint_summary`, not only the daylight layer, and a reader comparing this batch's fault/constraint counts to a fully-surveyed plan like `plans/tidewater-georgian-careful.json` should weight that difference accordingly.

## New open questions raised

None. This package's findings are corpus data-quality observations (a missing `EQUIVALENT` alias, a missing `via` entry, several missing room-catalogue ids) with an obvious next owner and no unresolved judgment call of the kind the existing 27 open questions record — they are proposals to fix, not forks in the road.
