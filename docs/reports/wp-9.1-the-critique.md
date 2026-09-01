# WP-9.1 — The critique: one building, the evidence a move can read, and the analyst that says what a finding means

*Phase 9, package 1 of 4. 1 September 2026. Ruled by Lucas the same day: the reflection is a
deterministic loop; the loop may move dimensions, declared choices, openings and optional
rooms; it runs by default. This package builds the half of that which JUDGES. WP-9.2 builds
the half that MOVES.*

## What this package is

Lucas asked for recursive self-improvement: once a plan is drawn, a critic assesses the
layout, points out every issue, and the generator fixes them in plan and elevation, so the
final product is the result of many corrective revisions rather than one procedural pass.

The critic existed. `plan_check.check` has fourteen layers and one of them reads the drawing.
What did not exist was anything a generator could ACT on: a finding carried a room and a
sentence, the only consumer that acted on findings re-read the sentence with string slicing,
and the critic itself was judging two buildings at once. This package makes the critic judge
one building, gives every finding the structured evidence a move needs beside its prose, and
adds an analyst — `build/critique.py` — that sorts every finding into what it means to a
generator: something a move answers, something only the engine can change, something the
critic invented, or something that belongs to the architect.

## I — Two buildings in one verdict

`plan_check.check` folded the elevation generator's measurements into the fault layer by
calling `build_elevation(plan)` with no placement (`build/plan_check.py:1227`). Three calls
down, `structure.build_section` then solved a FRESH heuristic placement of the declared
record (`structure.py:434-436`) — while the drawn layer, two hundred lines later in the same
function, read the placement the record actually carried. WP-6.4 had fixed this for the
drawing set (`corpus._placed`: "one drawing set is one building or it is nothing") and not
inside the critic. And the whole block was `except Exception: pass`, so an elevation that
could not be derived was indistinguishable from a style outside the generator's scope, or
from a house with nothing to measure.

**On the shipped plans the two buildings happened to agree, and the fix still moved a
number.** Measured before the fix on the heuristic: 0 of 187 measurement names differed
between the fresh placement and the carried one. Measured after, on the proving engine:
the Tidewater plan's entrance portico is declared 6 x 12 ft and CP-SAT places it at **23 x 3
ft** — the program AREA held (69 sf against 72), the shape a strip along the entrance front —
and the critic now reads `porch_clear_depth_ft` off that placement. `porch-too-shallow-to-inhabit`
reads **3.0 against at-least 7.0** where the old critic read the heuristic's 6.0,
and `porch-nobody-can-sit-on` fires at 3.0 against 6.0 where it had cleared. The house the
reader will be shown is the house the critic now judges. (Whether a Georgian portico should
be judged by that rule at all is
`oq/a-licence-matches-the-style-id-exactly-and-never-its-descendants`, §V.)

When the record carries geometry, `check()` now hands it to `build_section(plan,
geometry_result=plan)` — a solved record IS a geometry result — and the elevation is of
that placement. When it carries none, the fresh heuristic is what the elevation is derived
from, and the record says so. Three `info` findings replace the silence: `elevation-basis`
(which placement, which engine), `elevation-not-derived` (the exception, named),
`elevation-not-applicable` (a style outside the generator's scope). `elevation_summary`
rides on the result beside `drawn_summary`. None is scored and none is pinned; the DXF
round-trip sees them on both sides.

## II — The bench never ran the drawn layer

`workbench/server/evaluate.py` checked the client's DECLARED record, then placed it
separately and returned the placement beside findings that had never seen it. WP-6.2's drawn
layer — reachability, stranded rooms, the stair, the fixtures, the whole reason OQ 54 was
reopened — reported "could not evaluate" on every bench evaluate since it shipped, and the
word "drawn" appears nowhere in `workbench/app/src`. The parity test that pins bench = CLI
compared the declared record against itself and could not see it.

`evaluate()` solves first now, judges the SOLVED record, and projects `placement` off the
same object the sheet draws (`core.placement_summary`, split out of `place_plan`). Every
drawn finding carries `engine` — the drag path places with the search by name, so a fatal
that appears mid-drag and clears on the proof must not read as the house changing. A second
parity test holds the bench to `check_plan(solved)` finding-for-finding and asserts the
drawn layer evaluated; reverting the change fails it. Evaluate costs 0.34 -> ~0.4 s.

## III — The evidence contract

`compose.repair` — the one thing in the repository that acted on a finding — dispatched on
`"needs" in f["statement"]` and read its number with `float(statement.split("needs ")[1]
.split(" ft")[0])`. Read closely, on the family-georgian double-pile candidate it leaves
standing (34 serious -> 27, four serious furniture findings surviving), it has five defects
and none of them is the one an earlier draft of this package's plan blamed:

1. `need < width * 1.8` (`compose.py:1360`) silently skips any room needing more than 1.8x
   its width — three chamber closets at 2.1 ft needing 5.2 ft, skipped without a record.
2. The sentence prints `12.3`; the room needs 12.333 and is declared 12.3; `12.3 > 12.3` is
   false; the dining room never moves and the finding can never clear.
3. The minor branch's sentence says "needs about 12.3 ft", so `float("about 12.3")` raises
   and `continue` swallows it, every time.
4. One round reads a stale findings list and applies every finding's move to the same room:
   a pantry widened 5.3 -> 5.6 -> 9.1 ft in one pass, +72%, no attribution.
5. `:1381-1382`: on a non-improving round the record has already been mutated in place and
   the WORSE result is accepted as `best`. There is no rollback.

Prose parsing is the mechanism behind 2 and 3, and it is gone in WP-9.2 because every
finding now carries what a move needs as fields, beside the sentence and never instead of
it. `Findings.add` already stored arbitrary kwargs; the id (OQ 32) is built from layer, room
and rule only, so evidence never enters it — a test pins that. By layer:

| layer | fields |
|---|---|
| room | `kind` (`area-below-band` / `width-below-floor` / `ceiling-below-min` / `area-above-band`), `need_*`, `have_*`, `band`, `axis` |
| furniture | `kind="furniture-fit"`, `need_ft` UNROUNDED, `have_ft`, `axis`, `item`, `sides`, `clearance_in`, `footprint_in` |
| daylight | `kind` (`daylight-depth` / `no-window` / `sides-lit` / `depth-not-governed`), `depth_ft`, `reach_ft`, `need_head_ft` (the head that WOULD reach the back of the room), `lit_walls`, `two_ended`, `exterior_walls` |
| style | `kind` (`variant-forbidden` / `slot-forbidden` / `constraint-present` / …), `slot`, `variant`, `canonical` (the cascade's single canonical, or None — a judgment), `constraint`, `expression`, `value`, `required` |
| fault | `kind="fault-present"`, `fault`, `expression`, `reads`, `value`, `required`, `fix_right`, `fix_cheap`, `exception`, and `source` — `declared` when every name the failing test reads is in the plan's own `measurements`, `derived` when the elevation generator supplied it |
| drawn | `kind` (`unreachable` / `cut-off` / `drawn-vs-declared` / `stack-broken` / `stair-not-drawn` / `passage-narrow` / `fixture-unplaced` / `wall-run` / …), the figures each check already computed, `adjacent_placed` (rooms sharing a door's worth of wall on the placement), and **`engine`** on every one, set once through a local wrapper so no site can omit it |

`core.check_measurements` attaches `expression` to every result row, which is what lets the
fault finding say WHICH quantity failed. `build/openings.py`'s `unplaced` records carry
`needs` and `have` as fields beside their prose — the stair's `long_ft`/`short_ft` and
`declared_fits`, a door's `shared_wall_ft`, a fixture's `width_ft`/`depth_ft` — and a test
holds every figure to the sentence it rides with, so the two cannot drift. Plan schema
0.4.0 admits them; it also admits `revision_report` for WP-9.2.

The four placement-key tuples that only `export_dxf.py` carried are one spelling now, in
`openings.py` (`PLACEMENT_*_KEYS`, `strip_placement`), imported by the exporter and, in
WP-9.2, by the loop; a source-reading test refuses a second copy in `build/`.

## IV — The critic convicts every classical plan of the same faults, and the numbers are the generator's

Run the fault corpus against both shipped plans and the same fifteen serious faults come
back on both with IDENTICAL values. Those are not two houses sharing a defect. An AST read
of `elevation._derive_measurements` (`build/critic_suspects.py`) finds **35 measurement
names stated as bare numeric literals** and **4 as a real figure scaled by a literal**;
a sweep over the 11 plans the generator will front finds **61 names identical on every
one**. Among the convictions: `surround-that-lies-about-the-wall` reads
`window_reveal_depth_in: 4.0` (a literal), `casing-at-a-third-of-palladio` reads
`casing * 0.6` (a ratio), `doorhead-that-collides-with-the-cornice` reads
`entablature_bed_height_in = surround * 0.3` and returns **−79 in against at-least 12**,
`column-without-entasis` reads a shaft the generator draws parallel because "no entasis
rule exists anywhere in this pack, or in this codebase" (its own comment), and
`wing-pitch-drift` read `min_absolute_difference_between_distinct_slope_angles_deg: 0.0` on
a ONE-slope roof and convicted both houses of "Every Wing Its Own Pitch" on roofs with no
wing — OQ 52's flagship failure, in its exact shape, one field over.

**A revision loop that obeyed these would spend its rounds chasing the generator.** So the
analyst marks a fault whose failing test reads one of these names `critic-suspect`,
attaches the instrument, the value and the line, and WP-9.2's loop never acts on one. The
list is two instruments plus one editorial record: the AST readings (cheap, at critique
time), and `critique/suspects.json` for the pair the instruments cannot see (the parallel
shaft), each entry quoting where the generator says so of itself — verified by the same
`check_basis` the opening grammar uses, which now admits `build/*.py` as a record. `build/
check_critic_suspects.py` is the meter: 35 literals and 4 ratios are ceilings that may only
come down, and the way down is to model the thing, never to rename it. The corpus fix that
belonged here was made: `wing-pitch-drift`'s near-miss secondary carries an `applies_when`
on the slope count (WP-5.13's `dormer-off-the-bay` pattern), and both shipped plans lose
one serious — 53 -> 52 and 30 -> 29, re-pinned with the trace. The other thirty-four are
`oq/thirty-five-measurements-the-elevation-states-as-literals`: being a suspect is not
being wrong, and each is a separate decision.

## V — The analyst

`build/critique.py::critique(plan, engine, candidates, place)` places once (or reuses the
placement the record carries, the rule `corpus._placed` keeps), runs the critic on the
placed record, and sorts every non-info finding into exactly one class, first match wins:
`advisory` (the code layer), `placement` (the DECLARED record would have satisfied the need
and the engine did not — decided against the declared record BEFORE anything else, with the
lever named: the proof, a wider search, or the CP conflict set), `critic-suspect` (§IV),
`actionable` (a registered move answers it — the registry is WP-9.2's, so nothing is
actionable yet and the analyst says which move WOULD answer it), and `architect` (everything
else, with the fault's own `right` fix or the rule's own `why` quoted). A proved placement
with no conflict named is not a placement question any more; it goes to the architect with
the proof's account of itself. `info` findings are listed as could-not-evaluate and are
never a class.

Measured, both shipped plans, both engines (`key` is `[fatal, serious, minor, faults present]`):

| plan | engine | key | placement | suspect | architect | advisory |
|---|---|---|---|---|---|---|
| Tidewater, careful | heuristic | [3, 44, 70, 19] | 28 (lever: the proof) | 5 | 84 | 0 |
| Tidewater, careful | cp-sat | [0, 40, 65, 20] | 0 | 5 | 100 | 0 |
| Spec Colonial | heuristic | [10, 70, 63, 21] | 26 | 4 | 112 | 2 |
| Spec Colonial | cp-sat | [4, 64, 69, 22] | 0 | 4 | 132 | 2 |

Read the first two rows together: the search strands three rooms and draws closets at
+515%, and every one of those 28 findings names the proof as its lever; the proof strands
none, and what remains on it — upper rooms drawn +58..+81% because the upper level has too
few rooms for the footprint the ground floor sets, two stacks nothing under them — is the
record's own consequence, handed over. Of the 84 architect items on the heuristic, 24 name
the move that would answer them (`widen-for-furniture` 11, `light-the-far-end`,
`trade-width-for-depth-at-constant-area`, …); those become `actionable` the moment WP-9.2
registers the moves, which is the whole of what the next package has to do.

**The licence that never arrives.** `porch-too-shallow-to-inhabit` carries a Georgian
licence with a bounds test and a `not-applicable` severity for `georgian-colonial-american`,
and Tidewater Georgian, which is `regional_of` it, gets none of it: every exception site in
`core.py` matches `e["style"] == style` exactly, while a test's own `applies_to_styles`
follows the chain. An earlier reading blamed the bounds test for wanting a width nothing
supplies; that is true and is the smaller half, because the bounds test is never reached.
Raised as `oq/a-licence-matches-the-style-id-exactly-and-never-its-descendants`, and stated
here because WP-9.2's loop will otherwise treat a 6 ft portico as a porch to deepen.

## VI — What was found and not fixed

- **The 35 literals and 4 ratios** (§IV) are named, ratcheted and made harmless to the loop;
  not withdrawn or modelled. Each is a decision — some are measured zeros (OQ 89), some are
  a pack's rule asserted by construction, some are invented proportions.
- **Exceptions do not follow the chain** (§V). Not changed: 846 exceptions were authored
  against the exact-match reading, and some are genuinely narrower than the parent.
- **`compose.repair`'s five defects** (§III) are diagnosed here and replaced in WP-9.2, not
  patched in place: patching a prose parser is how it got to five.
- **The bench shows drawn findings now and labels nothing yet** — the engine badge and the
  Revision panel are WP-9.3's; until then a drag-path fatal that the proof clears reads as
  a finding that came and went.
- **The CP porch** (§I) is a finding about the CP model — "each room at roughly its program
  size" is an area, not an aspect, and a threshold room can be stretched into a strip along
  the front. Reported to the geometry layer's owner; not changed here, because a change
  to what the proof holds hard is a WP-2.3 question and this package is about the critic.

## VII — Verification

- `python3 build/plan_check.py plans/*.json`: declared counts 4 / 52 / 60 and 0 / 29 / 60,
  each serious count down one by `wing-pitch-drift`, re-pinned in `tests/test_plan_validator.py`
  with the trace and corrected in `docs/plans.md` (whose table had drifted to 3 / 49 / 51 and
  0 / 18 / 60 against pins of 4 / 53 and 0 / 30 — the drift its own parenthesis warns of).
- `python3 build/check_critic_suspects.py`: 35 literals, 4 ratios, 61 never-varying over 11
  plans, one editorial suspect verified; registered in `check_all.CHECKS`, TOTAL_CHECKS 43.
- `tests/test_critique.py` (30 tests): the elevation is of the carried placement (spied on
  `build_section`'s argument; reverting §I makes it None); an undrivable elevation is a named
  info; a style outside scope is stated; every figure a move would read appears in its
  sentence; the furniture need is unrounded; a fault finding names what it read and whether
  the house declared it; the id is unchanged by evidence; drawn findings carry the engine
  that RAN, not the one requested; every finding lands in exactly one class; a suspect is
  never actionable; a stair the declared hall would hold is placement; the instrument reads
  the shapes it claims to and refuses a ceiling breach; a misquoted editorial basis is
  refused; `wing-pitch-drift` declines on one slope and still convicts three.
- `tests/test_openings.py` (+7): every numeric need equals the sentence's figure; the stair
  refusal states what it needed; a placed record validates against 0.4.0; `strip_placement`
  removes every solver key and keeps a window's authored wall; no second spelling of the key
  tuples in `build/`.
- `workbench/server/tests/test_evaluate_matches_cli.py` (+1): the placed parity.
- Suites run here: `tests/` in full; the workbench server suite (fastapi, httpx, ortools and
  anthropic installed for the run — every check judged rather than N/EV).

*The move registry, the loop, and the measured movement are WP-9.2's, in its own report.*
