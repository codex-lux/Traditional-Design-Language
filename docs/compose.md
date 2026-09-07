# The composer

Template-seeded, validator-scored, and it returns several plans rather than one.

```
python3 build/compose.py briefs/family-georgian.json
```

## How it works

**Seed from the canonical partis.** Twelve plan diagrams — centre-passage double and single pile, hall-and-parlor, side-hall town house, Cape with central chimney, Foursquare, Charleston single with piazza, Creole gallery, bungalow, tripartite ranch, five-part Palladian, gable-front-and-wing. Each is descended from something that was actually built, which is the argument for seeding a search rather than starting it from noise.

A parti specifies **topology and roles only** — which rooms, which walls are outside, what connects to what. Dimensions come from the room catalogue, so the library never duplicates room data and can never drift from it.

**Size, revise, reclaim.** Rooms are scaled from the catalogue midpoint toward the target, then clamped to each room's own band, then optional rooms are dropped if it is still too big. The plan then goes through the validator and **the declared revision loop** (`build/revise.py` with `place=False`, in the position `repair()` has always held) applies the registered move each finding's structured evidence names — widen a room that cannot take its furniture, raise a window head that cannot reach the back of the room, grow a room to its band's floor — and rolls a round back byte-identically when the verdict does not strictly improve. Until WP-9.2 this was a forty-line hill-climb that read the findings' prose (`float(statement.split("needs ")[1]...)`), silently skipped any room needing more than 1.8x its width, read a rounded figure back so a 12.3 ft dining room needing 12.333 never moved, and **accepted the worse result on a non-improving round** — there was no rollback. It also shortened a room's length for a daylight finding, a size move for an arrangement finding, which OQ 92 ruled against; that move is retired and the registry says so. Revision spends area, so a reclaim pass gives it back from rooms that are not complaining, shortening length rather than width because width is what the checks care about.

**Then, on the RETURNED candidates, the placed revision loop (WP-9.2, on by default — ruled 1 Sep 2026).** Each candidate is placed (the proof where OR-Tools can give one), the critic judges the drawn house with its elevation derived from that placement, the analyst (`build/critique.py`) says what each finding means, and the registry's moves fix what the corpus's own rules can fix — in plan and in elevation — round after round until nothing the loop may do improves the verdict. The candidate is then **re-scored on its declared record**, so `score` and `score_before` are one instrument, and it re-ranks; `rank_before`, `drawn_key_before` / `drawn_key_after` and a `revision` report (every move with the finding it answered and the sentence it executed; what remains by class; what was handed to the architect with the fault's own `right` fix; what was refused and why) ride on the candidate. `--no-revise` returns the set as composed. See `docs/revise.md`.

**Dimension the openings** (WP-6.2). Every door gets a width, a type, a rank and a leaf height; every window a width and a count. Until this, `instantiate` emitted `{"to": id}` for every door — no width, no type, ever — and `{"width_ft": 3.2, "count": 2}` for every window on every lit wall of every room in every style, and both renderers then invented whatever the record failed to say.

None of it is new knowledge. `openings/grammar.json` says which KIND of opening belongs between which two rooms (editorial, and every rule quotes the corpus prose it reads); the kits have always graded the leaves `principal 84 in, secondary 80 in, service 78 in`; `proportions/systems/opening-proportion.json` derives the entry leaf from the storey height and the window from the room it lights — `room_width / 4.5`, under a note calling it *"THE RULE MODERN PRACTICE HAS ENTIRELY LOST"* — and 53 of 60 room records carry a `glazing_fraction` band that gives the count. **A pack's expression is read and evaluated, never restated here**, so the pack stays the one place that fact lives. Where nothing in the corpus states a width, the grammar's band midpoint is taken and the decision log says so by name.

**Rank fatal-free first, then by score.** The two keys are separate on purpose, and the first is the one that is never traded away: a plan carrying a fatal never displaces a clean one from the returned set, however native its diagram.

## The score

**Out of 100, higher is better, and it is a composite rather than a total.**

It was a total once — 100 a fatal, 8 a serious, 1 a minor, less 20 a point of style fidelity, lower is better — and three things were wrong with publishing that under the word "score". It had no ceiling, so the figure was only ever comparative while the workbench's big numeral invited an absolute reading. It ran in the unintuitive direction under a label that promises the other one. And its magnitude tracked corpus density and plan size rather than quality: `bungalow-small`'s candidates run −66 to 146 and `family-georgian`'s 176 to 283, for plans of comparable merit, because a bigger house is simply checked more times — 27 rooms against 14.

Each axis is now a **share of its own denominator** — what came back clean out of what was actually checked. A bigger house puts more rooms in the numerator and the same rooms in the denominator, so size cancels.

| axis | weight | denominator |
|---|---|---|
| solecisms | 20 | the faults the corpus could judge on this plan |
| rooms | 18 | every room, against its catalogue band, furniture, daylight and servicing |
| connections | 16 | every room, against the adjacency, circulation, privacy and completeness rules |
| fidelity | 25 | `pick_partis` fit, out of a possible 7.0 |
| area | 7 | how far off target against the brief's own tolerance |
| bedrooms | 4 | the bedrooms the brief asked for |
| canon | 5 | declared slots, groupings, evaluated constraints, massing affinity |
| buildability | 5 | the two footprint tests |

*(This table read 22 / 20 / 17 / 18 / 8 / 4 / 6 / 5 until 1 Sep 2026 against a `SCORE_AXES` of 20 / 18 / 16 / 25 / 7 / 4 / 5 / 5 — fidelity was moved from 18 to 25 on a measurement recorded in `compose.py`'s own comment, and this doc was not. Found by the Phase 9 exploration; corrected here. `check_counts.py` does not police these numbers.)*

A room is spent by a serious finding, halved by a minor, and left whole by an advisory or an info — the corpus calls those advisory and unjudged respectively, and neither is a failure. **The code layer is deliberately unscored**: it is advisory and jurisdictional and `plan_check.py` says so in its own note, so scoring a house on it would be scoring it against a jurisdiction nobody named.

**The weights are editorial.** They are one judgement about what matters in a house, stated once in `compose.py`'s `SCORE_AXES` rather than buried in a sum. The fault corpus and the two room-level axes are more than half the score because they are what a fluent reader notices walking through. Fidelity is 25 because being the right diagram for the style is the composer's whole argument for preferring one parti to another — at 18 it could not span the spread of the other seven axes on the two shipped briefs (18.0 and 22.0 points), and 25 is deliberately not enough to carry a plan that fails everything else.

**Unjudged is not passed.** An axis with no evidence neither scores zero nor scores full marks: its weight is dropped and the total renormalised over the weight that could be evaluated. `score_weight_unevaluated` reports how much of the hundred that was, so a score taken over 94 points of evidence cannot be read as one taken over 100.

**A fatal finding disqualifies a candidate**, and that is carried *beside* the score rather than inside it: `disqualified` is true and `disqualified_because` says so in words. A disqualified candidate never outranks a clean one whatever it scores — that guarantee lives in the sort's primary key, which is the fatal count, so the score does not have to enforce it a second time. In the workbench every ordering puts a disqualified candidate last, including "highest score first", and its column carries a band saying why.

This was first built the other way, withholding the score entirely on a fatal, and **measuring it killed the idea**. Composed across eight briefs, five returned candidate sets in which *every* candidate carried a fatal — `cape-cod-colonial` and `greek-revival` among them, which OQ 63 already records as styles that cannot return a clean plan under their own native diagram. Every column then read "—" and the four plans could not be told apart at all, which is strictly less than the demerit total gave. Withholding an aggregate while publishing all eight of its components is not a refusal; it is a number hidden from the reader who needed it most.

Within the axes a fatal spends its room exactly as a serious does, because the axes measure the share of checks that came back clean and that is what a failed check costs. The difference between *wrong* and *worse* is carried by `disqualified`, in words.

`demerits` is still on the record — the old lower-is-better total, kept because it is a real quantity and because earlier reports quote it. It ranks nothing.

## What it returns

Four contrasting candidates, each with its counts, its area and how far off target, a footprint check against the bay module, **what the diagram trades away**, and a decision log of everything the composer chose where the brief was silent.

```
1. Centre Passage, Double Pile   score 66.3 of 100   fatal 0  serious 30  minor 77
    15.6 / 22  solecisms          71%  76 faults the corpus could judge on this plan  (129 unjudged)
    10.7 / 20  rooms              54%  27 rooms
     8.2 / 17  connections        48%  27 rooms
    18.0 / 18  fidelity          100%  fit 7.0 of a possible 7.0
     3.5 / 8   area               44%  6.7% off target against the brief's 12.0% tolerance
     4.0 / 4   bedrooms          100%  4 of 4 asked for
     3.7 / 6   canon              61%  declared slots, groupings, evaluated constraints and the massing
     2.5 / 5   buildability       50%  2 footprint tests
```

The single-pile winning a Tidewater brief was the right answer once and is no longer the one the composer gives; WP-4.5's wider pick window found four diagrams with no fatal on that brief and the double pile now leads it. Its own story is below — it ranked fourth with a fatal finding until a modelling error was fixed.

## Four things the composer will not do

**It will not invent a room the diagram has no place for.** A brief asking for a garage against a parti with none is reported, not satisfied. Position matters more than presence.

**It will not drop a room that is load-bearing for a rule.** A room satisfying a hard adjacency is not optional however the parti marked it. Dropping the butler's pantry to save area severs the kitchen from the dining room, and the guard is general rather than a special case.

**It will not present an assumption as a fact.** Everything absent from the brief appears in the decision log.

**It will not tell you a plan is good.** A plan with no fatal findings is not therefore alive. The corpus can say what is wrong; the judgement of what is worth building belongs to the human, and returning four candidates rather than one is how that division of labour is enforced.

## What building it found

**`via` on an adjacency rule.** `kitchen must_adjoin dining-room, direct-door` is correct in a house with no butler's pantry and wrong in one that has it — the pantry exists precisely so the kitchen does *not* open onto the dining room. A rule with no named intermediary forbids the very room invented to satisfy it. Adding `via` moved the single-pile Georgian from one fatal finding to none and from fourth place to first, which is the historically correct answer: the Chesapeake stayed single-pile a century past the North for exactly the cross-ventilation reason the diagram encodes.

**Viewing distance is not clearance.** A television and a hung picture are both about four inches deep, and both carried a `clearance_in` that is really a viewing distance. Nothing four inches deep constrains the width of a room, so the fit check now skips anything without real bulk.

**A global scale factor cannot reach a small house.** Catalogue midpoints are generous; scaling them all by one number either overshoots a small brief or drives rooms below their own stated floors. Scaling, then clamping each room to its own band, then dropping optional rooms is what actually converges.

## Next

Geometry. The composer emits topology plus a footprint check; it does not place rectangles. That is a constraint-packing problem and it now has a well-defined input — a plan record whose rooms are already sized and whose adjacencies are already legal.

## The brief's target is heated area (OQ 55, 24 Aug 2026)

`instantiate()` holds reserved voids out of the scaling loop entirely: a court or a corredor
keeps the size its own weight and catalogue give it, and the rooms around it are scaled to reach
`target_area_sf`. `reclaim()` has always measured area with outdoor rooms excluded, so before
this the two passes were sizing against two different quantities and only one of them was the
brief's. On a plan with no placed void the difference is a rounding error. On the courtyard
parti, whose court and four-range corredor are about a third of the block, a 3,000 sf brief came
back as an **1,834 sf house** which the composer reported, correctly, as 38.9% off its own target
and could not fix — from its point of view the area had been spent.

So a courtyard brief now returns a house of the requested heated area inside a visibly larger
block, and `footprint.heated_area_sf` beside `footprint.area_sf` is where the difference is read.

## What a parti says that nothing executes (WP-11.11)

`build/parti_prose.py <parti-id> [--md] [--all]` reads one parti's own groupings, massing and room records and sorts every sentence into three states: it carries a `test` the grouping layer evaluates (`executed`), it carries `measures.reported_by` and is measured but deliberately not required (`reported`), or it is named to a reader and executed by nobody (`by hand`). Beside them it lists the figures a room's prose states that no band or test carries, using `check_grouping_rules.prose_meter` — **imported, never transcribed**, because a second crude regex is how a corpus ends up with two upper bounds for one question.

It exists because the enumerating, not the executing, was the expensive part of `docs/reports/tidewater-layout-diagnosis-2026-09-04.md` Part VI. That table was twenty rows assembled by hand from one rendered sheet; generated for the same parti it is **fifty** — 24 executed, 6 reported, 20 by hand, 7 prose figures — because the hand table caught what that sheet broke and the generated one is the whole surface.

**A rule with no test is not a defect.** One of them is a REPORT by ruling (`oq/the-facade-is-a-result-not-an-input`), several are genuinely a reader's, and WP-11.9's §IV refuses nine of the diagnosis's twenty with the fact that would have to exist first. The number is a work list in leverage order, which is what `check_inheritance.py --unendorsed` is for the pack cascade one layer over — not a debt to drive to zero.

**A row that leaves the table is the point.** All twenty of `centre-passage-double-pile`'s room-orientation rows moved out of `by hand` when WP-11.9 made `daylight.orientation` executable. That movement is the only thing distinguishing a generated Part VI from a list of complaints.

`docs/reports/precedents-centre-passage-double-pile.md` is the worked pattern for the other twenty, and its §2 is the method: generate Part VI first, then research the parti's own `exemplars`, quote the sentence, mark M/A/via, name what was not reached, and compare the parti's DECLARED record against the precedent — the comparison that produced `oq/the-parti-dissolved-its-own-dependencies` and `oq/the-partis-bay-module-contradicts-its-own-exemplars`.

## Every parti must work for the style it was written for (OQ 59)

`build/check_partis.py` check 10 instantiates each parti against the first style in its own
`styles` array and runs `plan_check` on the result. A fatal is an error. It is **differential**:
each parti is compared against a control diagram run on the same style, keyed on the requirement
rather than the measured value, so a fault that belongs to the style's own kit or elevation is
reported as the style's and not blamed on the diagram.

This exists because five of twenty-one partis were carrying fatal findings against their own
native styles, and a fatal is 100 points against at most 140 for nativity — so the composer,
working exactly as designed, would not recommend them. A Charleston-single-house brief came back
with a centre-passage single pile. See `docs/reports/oq-59-partis-that-fail-their-own-style.md`.

## `area_weight` is a share of the brief's target (OQ 62, 24 Aug 2026)

A room carrying an `area_weight` takes that fraction of `target_area_sf`, clamped to its own
catalogue band, and is **frozen before the scaling loop** — a real share is not renegotiated by a
global factor. Rooms without a weight split whatever is left.

**Partial coverage is normal.** Only the ten partis WP-4.5 authored carry weights at all, and
their sums run from 0.35 to 1.13; the eleven that carry none behave exactly as they did before
this ruling. A sum below 1.0 is meaningful rather than accidental: it says how much of the house
the diagram is deliberately sizing.

A **void**'s weight is a share of the same number, not of a gross the brief never states. The
court is 0.18 of the house that was asked for; that the house also has a court is what makes the
block larger than the brief (OQ 55).

Where a weight is larger or smaller than the room's own band allows, the composer logs a
JUDGMENT naming the room, what the weight asked for and what the band gives, so the area miss
that follows is an explained number. If that shortfall is large, the brief is asking the diagram
for a house it does not grow into by making its rooms bigger — see **OQ 45**.
