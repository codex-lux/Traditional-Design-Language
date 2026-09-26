# oq/the-worked-house-has-no-plan-that-places — Tidewater Georgian is the guided example, and neither shipped plan may be drawn

*Status: CLOSED 25 September 2026 (WP-14.21) — answer 3, the refusal is the example, on evidence · Raised in: WP-14.0 (24 September 2026)*

**CLOSED ON ANSWER 3, AFTER ANSWER 1 WAS ATTEMPTED AND FAILED.** Lucas ruled on 25 September:
*"Try to author one, with a stop rule"*. WP-14.21 tried both starting points and five variants, and
stopped on the rule. No plan places. The fact that decides it is the house's own, and it waits on a
ruling this question does not own. The amendment at the foot of this entry has the evidence. The
reading below is kept as it was written, because it is the account of what was asked.

**The finding.** Phase 14's audit found that the corpus holds one complete worked house and never
presents it as one: Tidewater Georgian has a brief (`briefs/family-georgian.json`), a plan
(`plans/tidewater-georgian-careful.json`), exemplars with precedent records, and the Four-Foot
Porch as the vision's own type specimen. Tranche 1 labels it *the guided example* on the front door
and in the rail. **The example cannot be walked to the end**, because the house it would arrive at
is refused at placement — and two documents still describe that plan as the clean one.

## Measured on this tree (`d565dea`, 24 September 2026)

**The declared record, `python3 build/plan_check.py --json`:**

| plan | fatal | serious | minor | info | drawn layer |
|---|---|---|---|---|---|
| `tidewater-georgian-careful` | **3** | 30 | 76 | 29 | not evaluated — *"no placement on this record"* |
| `spec-builder-colonial` | **5** | 60 | 80 | 25 (+1 advisory) | not evaluated |

The three Tidewater fatals are all facade faults: *The Front With No Centre* (`even-bay-front`,
0 against equals 1), *The Bay That Broke the Symmetry* (`one-bay-symmetry-break`, 3 against
at-most 0) and *Windows That Do Not Stand On Each Other* (`storeys-out-of-vertical-alignment`,
90.0 against at-most 2.0).

**The placement, `geometry.solve`, one run each:**

| plan | `engine="heuristic"` (deterministic) | `engine="auto"` at the 40 s batch budget |
|---|---|---|
| `tidewater-georgian-careful` | refused — bearing, hearth, stacks | CP-SAT FEASIBLE, refused — hearth, tiling |
| `spec-builder-colonial` | refused — bearing, stacks | CP-SAT FEASIBLE, refused — bearing, stacks, tiling |

CP-SAT under a wall clock is not reproducible, so the `auto` column is one reading and the FACTS
named may differ on another run; that both plans are refused on both engines is what has held
across every measurement this register records. `workbench/app/e2e/walk.mjs:91-113` carries the
same account from the 19 September pass: its first measurement listed eleven of the sixteen plan
records refused on `auto`, both shipped plans among them, and the drawable set re-derived at that
package's audit was **three** —
`bad-02-flex-room-craftsman` (colonial-revival), `bad-06-open-concept-render`
(contemporary-traditional) and `good-03-parlor-drawing-room-house` (greek-revival-american) — all
one level, none with a hearth, none placing a stoop, and none of them Georgian. The bench reads the
verdict through one module, `workbench/app/src/sheet/refusal.js`, and draws the conflict set where
the plate would be.

**Two documents describe the plan as clean, and neither is policed.** `README.md:51`: *"Two worked
examples ship with it: a deliberately ordinary production Colonial (4 fatal) and the same corpus
applied carefully (0 fatal)."* Measured today the careful plan is **3 fatal** and the Colonial
**5**. `STATE-OF-THE-PROJECT.md:62` calls it *"the same corpus applied carefully"* and gives no
count, so it is not false, but it is the sentence a reader will take the README's figure into.
`build/check_counts.py` polices figures derived from the corpus and does not read either.

**And the composed route does not arrive at a drawable Georgian either.** For the example brief the
composer's returned set has been recorded leading with a refused candidate
(`oq/the-composer-ranks-first-a-house-that-may-not-be-drawn`) and without the native diagram at
all (`oq/the-composer-returns-a-set-that-satisfies-neither-must-have-room`). Not re-measured here;
both entries carry the figures and say which engine they are true of.

## What each answer would change

1. **Author a Tidewater plan that places.** A new record, or a re-authoring of the careful one,
   that the prover draws without a downgraded type fact. This is design work on a shipped record
   and it is not guaranteed to exist: the refusals are the house's own — the two west fires on one
   flue (`oq/a-shared-flue-cannot-stand-behind-two-centred-breasts`) is a statement the record
   makes, not a solver's failure — and a record edited until the refusal goes away is the laundering
   this corpus forbids. It moves every figure pinned to the shipped plan.
2. **Precomputed compose results, labelled as such.** A frozen snapshot of one composition — brief,
   candidates, the chosen placement and its sheets — served as *"precomputed on <commit>, <engine>,
   <date>"* so the guided example reaches a drawing. It is honest only if the label travels with
   every plate and the snapshot is re-derived or refused when the code moves, which is a freshness
   check this repository would have to add; a stale precomputed sheet is WP-6.4's one-building rule
   broken in time rather than in space.
3. **The refusal is the example.** The guided path runs style → brief → candidates → plan and stops
   at a named refusal, and the front door says so in advance. Cheapest, and consistent with *a
   refusal is the system working*; it means the worked house never shows a drawing.
4. **A different worked house.** One of the three records that places. None is Georgian, so the
   dossier's worked style and the journey's worked house would be two different buildings.

## What tranche 1 does meanwhile

Answer 3, without promising more. Tidewater Georgian is labelled the guided example on the front
door and in the rail; the example runs from the dossier to the example brief
(`/api/briefs/examples/{name}`, served by WP-14.4); the journey bar (WP-14.10) states a refused plan
in words at step 3 and shows Drawings and Export as *blocked: refused*, not as links. The plan's
*must not* list forbids a tour promising a house. `README.md:51` is not edited by WP-14.0, which
touches only the register and the plan; the documentation pass is WP-14.15's, and this entry is
its instruction to correct that sentence rather than let it stand.

## Amendment, 25 September 2026: the README sentence is corrected, and the question is not

`README.md`'s *"the same corpus applied carefully (0 fatal)"* now states the measurement instead:
the careful Tidewater record carries 3 fatal findings against the ordinary Colonial's 5, both
re-measured with `build/plan_check.py --json` on the tree that carried WP-14.8, and both are refused
at placement. The figures are dated in the sentence because no checker reads them. That corrects
one of the two documents this entry names; it answers none of the four questions above, and the
entry stays open.

The same pass found the README's and `STATE-OF-THE-PROJECT.md`'s fault-corpus figures unpoliced
and stale — 209 faults against a corpus of 210, and *"every slot covered"* while four are not — and
`build/check_counts.py` now holds the fault count and the two exception counts in both files.

## Amendment (WP-14.14, 25 September 2026): the front door says where the example stops

Answer 3 is now said in advance, on the front door, in a record's words rather than the app's.
The sentence is `glossary/guided-example.json`'s `more` — *"The example stops at the brief. Its
house has no plan that places ..."* — and the front door and the term page both draw it under the
example's definition. Its basis quotes `build/revise.py` and `build/typefacts.py` rather than this
entry, because `build/check_glossary.py` refuses a glossary basis that names the register.

**That makes the record a second place this question's answer lives, and nothing ties the two.**
`check_basis` verifies that the quoted sentences are in those two modules, which stays true
whether or not the worked house ever places; it cannot tell that the `more` has become false. So
whichever answer closes this question must revise that record's `more` and its basis in the same
commit — under answer 1 or 4 the sentence is simply wrong, and under answer 2 it must name the
snapshot. Report: `docs/reports/wp-14.14-the-front-door-and-the-gate.md`.

## Amendment (WP-14.21, 25 September 2026): answer 1 was attempted, and it closes this on answer 3

Answer 1 was ruled on the day it was asked, with a stop rule: *"Try to author one, with a stop
rule"*. A plan would count as placing only if all of these held:

- the search refuses nothing;
- `auto` at the batch budget refuses nothing on five of five runs;
- the drawing set draws;
- every type fact the careful record judges is held, and none goes unjudged.

It could be reached only by admissible edits, each quoting a corpus file. The laundering the ruling
lists was refused throughout. Report: `docs/reports/wp-14.21-the-worked-house-and-the-dining-fire.md`.

**What was tried.**

- A copy of the careful record (the record itself is untouched).
- Three cumulative variants of it:
  - the hyphen lengthened inside the back hall's band;
  - the west range at its rooms' floors;
  - the brief's fourth bedroom.
- The composer's own native diagram for the example brief, revised on each engine, with the
  massing's three end-wall fires stated.

**What happened.**

- Every placement was refused: by at least two facts on `auto`, and by at least one on the search.
- The one variant on which the prover held all three fires and every stack (V3, four runs, the same
  objective each time) held them by drawing the drawing room at the back of the house. Its return
  to the front was proven infeasible, and it was refused on tiling and bearing.
- The stop was reached on rules (c) and (d).

**The fact that decides it, proved by hand in the report's §III.**

- The four-over-four massing says *"Paired end chimneys serve four fireplaces per floor"*, so the
  dining room's fire is on the west gable.
- The dining room must then span the whole west range to reach the passage.
- The butler's pantry must door the dining room, and stands in the block on its own record's word.
  It then needs a side at least as long as the drawing room's sixteen-foot floor, against its own
  fourteen-foot length ceiling.
- A small solver model agrees:
  - INFEASIBLE with both west fires, with or without the pantry's door to the hyphen;
  - OPTIMAL with only the drawing room's fire on the gable, where it finds a proper four-over-four
    with the pantry on the gable in the hyphen's band.

**Where the remedy lives.** Which wall the dining room's fire stands on is item 4 of
`oq/a-room-record-names-the-wall-its-fire-stands-on-and-nothing-compares-it`:

- the massing says the gable;
- `rooms/dining-room.json` says *"the interior wall opposite the sideboard"*;
- that entry's own trap forbids settling it by moving the fire to clear a finding.

Measured once as a control, the interior fire reads unjudged under the massing's flue walls. So even
that answer does not place the house, and the house is still refused on tiling and bearing.

**The other refusals are the instruments', and each is owned elsewhere:**

- the search is told nothing about the hearth or on-grid bearing:
  `oq/the-search-is-refused-on-type-facts-nothing-tells-it`, raised here;
- the prover's tiling of a massing element it rounded inward, or derived from its own rooms:
  `oq/the-tiling-fact-cannot-hold-on-a-rounded-or-derived-massing-element`, raised here;
- the stacking default: `oq/the-measurement-that-defaulted-the-stacking-rule-has-inverted`.

**Why answer 3 and not a fifth wait.**

- Answer 1 now has a proof that it cannot succeed under the parti and the rooms' bands until item 4
  is ruled.
- Answer 2 would draw a house that no current placement produces.
- Answer 4 changes which house the example is.

The guided example therefore runs style, brief, candidates, plan, and stops at a named refusal. It
now says why, and says that the reason is the house's.

**The glossary record is revised in the same commit, as the WP-14.14 amendment required.**
`glossary/guided-example.json`'s `more` now says why the example stops. Its basis now quotes:

- the massing;
- the parti;
- `rooms/butlers-pantry.json`;
- `rooms/dining-room.json`.

**If item 4 is ruled for the gable, this question does not reopen.** That ruling leaves the proof
standing, and the refusal stays the example. **If it is ruled for the interior wall**, the hearth
fact must first judge a fire on a wall the massing states no flue for. After that, a worked house is
a new attempt under a new question, not a reopening of this one.
