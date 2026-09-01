# WP-9.1 — The arbiter for arrangement

*The corpus already knew. Nothing read it.*

**Raised by Lucas, 1 September 2026**, against a rendered workbench sheet of
`tidewater-georgian-careful` on the `centre-passage-double-pile` parti:

> The kitchen is far too narrow, as is the breakfast room. The entrance portico is
> ridiculously narrow and not even aligned with the center passage. There's a dining room off
> of the center passage, but it doesn't get any light because it's directly in the middle of
> the house. The library is narrow. The stair hall is weirdly configured and sized. The stairs
> are shoved off into the corner, and the center passage is huge. […] I think it's because
> it's still being procedurally generated at a lower level than the idiom.

This is the project's founding failure mode — every part well-formed, the whole meaningless —
recurring one level above where Phase 6 left it. Phase 6 made the sheet tell the truth about
the placement and gave the record something to say about an opening. It said in its own report
that it *"does not improve the placement"*, and nobody ever gave the record, the critic or the
solver a vocabulary for **arrangement**.

This package is the arbiter. **It changes no placement engine and no renderer** — both
reference plans render byte-identically — and it was meant to change no generator either. It
changes one thing in `build/compose.py`, because the arbiter's first real finding was a fatal
no candidate could clear; finding 0 below is that story, and it is the strongest evidence the
arbiter was needed. The phase's gate is otherwise unchanged: `build/geometry.py` carries eight geometric
arrangement score terms and `plan_check.py` had a counterpart for exactly one of them
(`stacks_over`), against this file's own stated principle at `plan_check.py:496-501` — *"a
charge is a preference the search trades off; this is the arbiter, and the two are not the same
job."* Seven terms failed that principle. A generator change measured against no arbiter is how
three published refusals in WP-6.3 and WP-7.4 came to be wrong; the instrument comes first.

---

## The reproduction

`geometry.solve()` on the careful plan at the shipped defaults draws this ground floor:

| room | declared | **drawn** | ratio |
|---|---|---|---|
| Kitchen (Dependency) | 16 × 20 | **10.0 × 30.0** | 3.00 |
| Breakfast Room | 12 × 14 | **7.0 × 27.0** | 3.86 |
| Entrance Portico | 6 × 12 | **3.0 × 23.0** | 7.67 |
| Library | 15 × 18 | **10.0 × 24.0** | 2.40 |
| Centre Passage | 12 × 34 | **10.0 × 37.0** | 3.70 |
| Dining Room | 16 × 20 | **17.0 × 17.0** at (23, 7) | 1.00 |

Those are Lucas's numbers, to the foot. The sheet he read is reproducible from the record, so
every claim below is measured on it rather than argued about.

## What the critic said about that sheet before this package

Of the seven complaints, **two**. The breakfast room and the library tripped the room layer's
`width_ft` floor — the only shape check in the file — and everything else was silence.

The mechanism, verified in the code:

- **The room layer read `dimensions.area_sf` and the FLOOR of `dimensions.width_ft`, and
  nothing else** (`plan_check.py:848-859`). Not `length_ft`, not `proportion`. Fifty-four of the
  sixty room records declare a `proportion` band and no line of code had ever read one. A
  kitchen at 10 × 30 holds 300 sf inside a 120-340 band and is exactly at its 10 ft width floor:
  no finding, from a record that states `length_ft [12, 22]` and `proportion [1.05, 1.8]`.
- **Twenty-eight faults carry a test whose `measurable_from` is `plan`** — and they are
  precisely these complaints: `passage-that-is-a-corridor`, `stair-at-the-front-door`,
  `service-route-through-the-formal-plan`, `the-room-nobody-enters`,
  `front-door-into-the-living-room`, `centre-passage-blocked-at-one-end`. **Twenty-seven of the
  twenty-eight came back UNJUDGED** on this corpus's own most carefully authored plan. The fault
  layer's namespace (`plan_check.py:1211-1215`) is `plan.measurements` — empty on fifteen of
  sixteen records — plus the per-room width and length, plus `build/elevation.py`'s ~110
  quantities, every one of which is an elevation measurement. **Not one plan-arrangement
  variable was supplied by anything.** The named-error corpus had the whole vocabulary and no
  measurement layer underneath it.
- **The fact about the landlocked dining room was already in the record and had no reader.**
  `build/openings.py:358-362` has written `win["unplaced"] = {"reason": "the placement puts this
  room on no such boundary wall"}` since WP-6.2, and `report["windows_unplaced"]` beside it. A
  grep for either found **zero call sites in the tree**. The drawn layer even *skipped* unplaced
  windows when measuring a wall run, so an unplaced window made the sideboard check easier to
  pass. Meanwhile the daylight layer reads the DECLARED window list, and `compose.py:637-644`
  writes a window for every wall the parti declares — so the record claims windows on a room the
  placement put nowhere near a boundary.
- **Nineteen of the fifty hard grouping rules carry a machine test, and the loop surfaced only
  the ones that DON'T.** `plan_check.py:1110-1112` read `if severity == "hard" and not
  ir.get("test")` and emitted "check by hand". So a hard rule *without* a test was handed to a
  human, and a hard rule *with* one was passed over in silence by every layer of the checker.
  Twenty-six of the eighty-four internal rules carry a test; exactly two were evaluated anywhere
  in the tree, both in `build/roof.py` for the ridge step-down. `centre-passage-core`'s own
  `passage_width_ft / facade_width_ft between 0.18 and 0.27` — the rule that says a passage is a
  fifth to a quarter of the front — had never been run on anything.
- **`op-stair-setback` was implemented nowhere.** `openings/grammar.json` has carried it since
  WP-6.2 with a number, a basis naming three records that agree, and a note explaining the gap:
  *"Nothing could evaluate it, because no plan record held a stair."* A plan record has held a
  stair since WP-6.2. **The note went stale in the package that wrote it** and the rule stayed
  unimplemented for three phases. The other three `placement_rules` are in `build/openings.py`.

---

## What was built

`build/arrangement.py`, new, and reads into `build/plan_check.py` at three points.

**The measurement layer is two functions, not one, and the split is a ruling.** OQ 54 was
reversed on 26 Aug with a boundary: the `drawn` layer is the ONLY layer that may read a
placement. So `declared(plan)` is geometry-blind and feeds the fault layer, which judges the
house the record declares and must work on a plan nobody has placed; `grouping_vars()` and the
drawn checks read the placement where the quantity is only knowable once the house is drawn. A
fault is evaluated in exactly one of them. A test pins the boundary: `declared()` must return
the same dict whether or not a placement exists.

### The checks, and the numbers they now produce on that sheet

| complaint | named? | by what |
|---|---|---|
| kitchen too narrow | **yes** | drawn shape: *"DRAWN 10.0 × 30.0 ft — 3.0 to 1, against the 1.05-1.8 band"* |
| breakfast room too narrow | **yes** | drawn shape: 7.0 ft below the 8 ft floor; 3.86 to 1 |
| portico narrow | **yes** | drawn shape: 3.0 ft below the 5 ft floor; 7.67 to 1 |
| portico off the passage axis | **yes** | drawn axis: *"the two openings do not overlap at all"* |
| dining room landlocked | **yes** | drawn daylight: *"drawn in the middle of the house: it reaches no exterior wall on any side"* |
| library narrow | **yes** | drawn shape: 10.0 ft below the 13 ft floor; 2.4 to 1 |
| centre passage | **partly** | grouping: the ratio rule, `serious` |
| stair shoved into a corner | **NO** | see refusals |

Six of seven. The acceptance test asked for five.

**The drawn-shape check is the one that matters most**, and its absence was OQ 54's own sentence
surviving in the one place the drawn layer had not reached. The room layer reads the catalogue
bands off the *declared* record, and the declaration was fine — the brief declares a 16 × 20
kitchen. The placement drew 10 × 30, held the area to within 6%, and the existing
drawn-divergence check compares AREA, so it stayed quiet. **The declared house and the drawn
house are two different houses and only one of them was ever measured against the catalogue.**

---

## Findings

**0. THE ARBITER FOUND A REAL DEFECT ON ITS FIRST RUN, AND THE PACKAGE HAD TO FIX THE
GENERATOR TO SHIP.** This is the finding that justifies the whole package, and it is stated
first because it also breaks this package's own "no generator change" claim, deliberately and
with the reason.

Supplying `passage_clear_width_ft` armed `passage-that-is-a-corridor`, whose test is
`at-least 8.0` and whose severity escalates to **fatal** for a formal centre-passage style. The
composer had been sizing this brief's passage at **7.9 ft** — and a fatal disqualifies a
candidate outright. All three NATIVE Tidewater Georgian partis were eliminated
(`centre-passage-double-pile` at 7.9, `five-part-palladian` at 6.1,
`centre-passage-single-pile`), and the brief came back recommending a **side-hall townhouse at
fit 3.6**. That is WP-4.5's deleted sentence walking back in: *"a Tidewater Georgian brief came
back recommending an octagon."*

**Nothing had ever supplied the measurement, so the fault could not fire, and the defect was
three phases old.** It was caught only because two behavioural tests pin the composer's ranking
(`test_score.py`'s native-dominance guard and `test_site.py`'s presence guard) — and the second
of those exists precisely because an earlier scoring change turned a loop over an empty list
into a test that asserted nothing.

**The corpus states the real floor in three places and nobody had read them together:**

| record | what it says |
|---|---|
| `faults/passage-that-is-a-corridor.json` | `at-least 8.0`, and its note: *"8 ft for a formal centre-passage plan and 6 ft for a northern vernacular one"* |
| `groupings/centre-passage-core.json` | *"Passage width 8 to 14 ft"* |
| `kits/tidewater-georgian.kit.json`, **through the cascade** | `circulation_parti.parameters.passage_width_ft` = **[10, 14]** |

And `rooms/centre-passage.json` bands it at **[6, 14]** — which is *right*, and is why the room
layer passed a 7.9 ft passage in silence. Six to seven feet is a northern vernacular passage
that circulates and the record says so in as many words. **The catalogue floor and the formal
floor are two different rules, and only the catalogue's had a reader.**

The fix is in two halves, both corpus-driven and neither authoring a number: the style layer
reads the floor off the **resolved** kit (never `C["kits"][style]` — `oq/the-raw-kit-read`, which
WP-8.4 and WP-8.6 each found a live instance of) and says so; `compose.repair()` gains a branch
that widens the passage to it, beside the branch that already widens a room to its catalogue
floor. The native diagram returns at fit 7.0. A test pins the two halves against each other by
reading the **emitted statement** rather than the source, because the phrase `repair()` parses
is built from two f-string fragments and is contiguous only at runtime — a source-reading
assertion failed on working code and would equally have passed on a branch nothing reaches.

**The honest account of scope:** this package set out to change no generator, and the arbiter's
first real finding made that impossible. A true fatal that no candidate can clear is not a
critic working; it is a critic that has broken the composer. Shipping the finding without the
repair would have been shipping the regression.

**1. The plant-room zero was built, convicted both reference plans, and was withdrawn.**
The first draft derived `dedicated_plant_room_area_sqft` as a measured zero, arguing that a plan
record states its whole room list so "there is none" is a fact it asserts — the WP-5.13 dormer
precedent. On the first sweep it convicted **both** shipped plans, including the careful
Tidewater Georgian written to see whether the validator stays quiet on a good house. That is the
OQ 52 signature exactly: an invented constant convicting the plans that ship. And the dormer
precedent says *why* it is invented — `declared.dormer` earned its zero by gaining three states,
because *"an absent dormer and an unstatable one were indistinguishable"*. Identical here.
**And the second reason is stronger than the first: there is no room type for a plant room in
this corpus.** The sixty records in `rooms/` hold no `mechanical-room`, no `plant-room`, no
`utility-room`; the nearest neighbours are `cellar`, `workshop` and `laundry`, all rooms a house
has for other reasons. So the plan record cannot state that it HAS one either, and the fault is
unjudgeable in both directions until the catalogue gains the type. Refused, with the reason in
`NOT_DERIVABLE`, and pinned by a test that fails the day somebody adds the type.

**2. The first draft of the room-layer shape check convicted the good reference plans.**
It also charged a room for being *squarer* than its band and *wider* than its band. On the first
corpus run that produced findings on an 18 × 18 dining room, a living room at 1.62 against a
ceiling of 1.6, and a 3 ft closet against a 2-2.33 band — on `good-01` through `good-07`, the
plans this project holds up as good. **No record in this corpus says a room may not be square**;
the prose runs the other way, and the complaint that raised the package was a room stretched into
a band, never one too nearly square. The fix was to delete the direction the corpus does not
state, not to loosen the one it does. Severity is now the file's own two-tier convention for a
figure that has drifted (10% minor / 25% serious), so a room 1% over its band is a decision to
defend and one 67% over is the kitchen Lucas was sent. After: **every `serious` shape finding
lands on a `bad-*` plan; the good plans and the careful plan take only marginal `minor` ones.**

**3. The entrance-axis check missed the sheet that raised the package, by a hair, because the
geometry was wrong.** The first version compared the door offset against `max(leaf)`. Two
openings overlap iff their centres are closer than the **sum of their half-widths**. On the real
sheet the front door sits 3.5 ft from the passage door and both leaves are 3.5 ft: the openings
are exactly edge to edge, touching at a point, overlapping by nothing — no straight walk between
them — and `off > max(leaf)` let it through. Corrected, with both the boundary case and the
overlapping case pinned as tests. The check remains parameter-free: the unit is the doors' own
recorded leaves, so there is no authored number in it.

**4. `declared()` was reading the solver's own output.** It took `main_block_depth_ft` from
`plan["footprint"]`, which `build/geometry.py` writes during a solve — so a geometry-blind
function answered differently once a placement existed, inside the layer OQ 54 ruled must never
see one. Caught by the test written to pin the boundary rather than by reading the code. It now
derives the block from `derive_footprint`, which reads the declaration and the parti and no
placement at all. An author may also declare a footprint by hand and the record cannot
distinguish the two — the same indistinguishability that refuses the plant room.

**5. Four room-type selectors in this package's own first draft named types the catalogue does
not have.** `chamber`, `secondary-bedroom`, `principal-bedroom`, `hall-and-parlor-hall` — every
one a plausible-looking alias of a type that exists under another name (`bedchamber`, `bedroom`,
`primary-bedroom`, `hall`), and every one matching nothing. **Two of the four sat in the selector
for `secondary_bedroom_clear_short_dimension_ft`**, which is the measurement
`closet-depth-taken-from-the-room` judges every house on. `check_openings.py` already states the
principle for the opening grammar — *"a rule keyed on a room type nobody wrote is a rule that
never fires, silently"* — and the same discipline is now in this module's selftest, comparing
every type token in the file against the catalogue. Found by applying that checker's own rule to
new code rather than by anything failing.

**6. A dead lookup that changed no verdict and was therefore invisible for three phases.**
The drawn passage check opened with `for rule in (cp.get("rules") or [])` against
`groupings/centre-passage-core.json`, whose key is `internal_rules`. `band` was `None` on every
plan this checker has ever run — and was then never read, because the two thresholds below it
are hardcoded and came from the ROOM record's prose rather than the grouping's test. **A lookup
whose result is never used cannot fail loudly; it just quietly stops being a lookup.** The
grouping's ratio rule is now evaluated in the grouping layer where the rest of its rules are
judged, and what stays in the drawn layer is the pair of checks that quote
`rooms/centre-passage.json` directly.

**6a. The two shipped plans move apart, which is the differential stated in one line.** The
annotated count pins in `tests/test_plan_validator.py` had to move, and the shape of the move is
the calibration evidence:

| plan | serious | minor | what moved |
|---|---|---|---|
| `spec-builder-colonial` (deliberately ordinary) | **53 → 57** | 60 → 62 | three faults the arrangement layer newly feeds — a 9.5 ft secondary bedroom against an 11 ft floor, a 24 sf entry against 30, a formal entry on no daily route — plus contemporary-service-core's mudroom width, a grouping rule that carried a test nothing ran |
| `tidewater-georgian-careful` (written to be quiet) | **30 → 30** | 60 → 61 | the linen press, 5 ft against its own 2.5-4 ft band |

**Four new serious on the ordinary plan and none on the careful one.** A check that convicts
both alike is measuring something other than quality.

**7. The 164-style sweep is clean, and the differential is the result worth keeping.** Supplying
withheld measurements arms every rule that presupposed them (OQ 89), so the sweep ran before
anything else landed. **No evaluator errors surfaced** — no newly-reachable division by zero.
Across all 164 styles: the careful plan moves **1,034 verdicts from unjudged to CLEAR with zero
convictions**, and the deliberately ordinary spec plan takes **390 convictions** across
`ceremonial-front-door` (164 styles), `closet-depth-taken-from-the-room` (164) and
`front-door-into-the-living-room` (62). The good house stays quiet and the ordinary one does
not, which is the only evidence that the derivations are calibrated rather than merely loud.

**8. The passage is not what Lucas thinks it is, and the corpus says so.** He called it "huge".
Measured against `centre-passage-core`'s own rule it is **10 ft in a 60 ft facade = 0.167,
BELOW the 0.18-0.27 band** — if anything too narrow for its front. At 10 × 37 it is inside every
band its own record declares (`area_sf [130,400]`, `width_ft [6,14]`, `length_ft [20,40]`,
`proportion [2.0,5.0]`). What makes it read as huge is that it runs the full 37 ft depth and
takes 15% of the ground floor where the parti's own `trades_away` says *"roughly a tenth"*.
**No rule in this corpus calls 10 × 37 a fault, and none was invented here to match the
complaint.** The binding condition on this package was to author no new numeric threshold, and
manufacturing one to claim seven of seven would have been the corpus laundering an opinion. It
is stated instead, for Lucas to rule on.

---

## What was deliberately not done

- **No new `arrangement/grammar.json`, and no new grouping rule for the portico axis.** The plan
  for this package called for one editorial `internal_rule` in `centre-passage-core.json`. It was
  **refused on contact with the corpus**: the rule is already stated twice — in
  `rooms/entrance-hall.json` (*"where the plan has a passage the hall is its front end, and the
  axis must continue to a rear opening"*) and in `openings/grammar.json[op-passage-axis]` — and
  the drawn check reads and cites both. A third statement would be the duplication this codebase
  has been bitten by three times (the citation grammar's three spellings, the relaxation marks,
  the parti-id join). `schema/grouping.schema.json` also sets `additionalProperties: false` with
  no `basis` key, so an editorial rule could not carry its citation there anyway.
- **No new numeric threshold anywhere.** Every figure quoted by a new finding is the corpus's
  own: the rooms' bands, the groupings' tests, `op-stair-setback`'s 6.0 read from the grammar
  rather than transcribed (pinned by a test).
- **No placement-engine change and no renderer change.** Both reference plans and the careful
  plan render byte-identically before and after. The one generator change is
  `compose.repair()`'s passage-floor branch, forced by finding 0 and documented there rather
  than smuggled in under the arbiter's heading.
- **The stair's position within its hall is still unmeasured**, which is why complaint seven is
  unnamed. The setback from the front door is checked; *"shoved off into the corner"* is a
  statement about where the flights sit in the room, and `openings.stair_pass` anchors every
  flight at the room rectangle's origin corner **by construction**
  (`openings.py:443,460,486-506`) — so every stair in the corpus is in a corner and a check would
  convict all of them equally. That is a placement defect, and it belongs to WP-9.3's
  arrival-aware stair, not to the arbiter.
- **Six fault variables stay refused**, each with its reason in `NOT_DERIVABLE`: the chimney plan
  dimensions (OQ 52's exact class — no record carries one and the only figure available is
  flagged `judgment: true`), duct runs (no HVAC model exists anywhere), the powder-room sightline
  (needs the dining table placed; OQ 92 refused furniture-driven derivation), the wet-wall
  landing (no plumbing-wall thickness is modelled), and the per-room cornice ratio (no interior
  trim model — **and its expression divides by a count, so it will need an `applies_when` the day
  the denominator becomes suppliable**, which is OQ 89's lesson written down before it bites).

## The OQ 94 conviction, put to Lucas

Deriving `exterior_openings_on_the_passage_axis` executes the third branch of **OQ 94** — *"let
the drawn layer fail it"* — which that question lays out and marks as yours to choose.
`plans/tidewater-georgian-careful.json` declares one exterior passage door where
`styles/tidewater-georgian.json` c03 (hard) and `groupings/centre-passage-core.json` both demand
two aligned operable ones. The reference plan was **not** exempted and the second door was **not**
authored — authoring it would be the composer inventing plan content, which WP-6.2 refused for
this exact case. The gap is visible instead of hidden. It wants a ruling.

## Verifying

```
python3 build/arrangement.py selftest
python3 build/arrangement.py plans/tidewater-georgian-careful.json   # what the record can supply
python3 -m pytest tests/test_arrangement.py -q                        # 25 tests, each paired
python3 build/check_all.py                                            # 40 of 43, at the new total
```

Every new finding is mutation-checked in both directions — it fires on a constructed offender and
is silent on a constructed conformer differing in exactly the one fact the rule is about.
Reverting any derivation to a constant breaks the offender half; loosening any breaks the
conformer half. That discipline is why nine tests in WP-8.6 could be shown not to fail, and it
found the axis-geometry error above before the package shipped.
