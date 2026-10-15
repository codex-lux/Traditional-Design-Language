# The candidate click and the stale bench (15 Oct 2026)

*Not a numbered work package, and deliberately so: a package number is issued from the working
tree and collides across parallel sessions (OQ 90), and this is a defect report with a fix, not a
planned piece of a phase. It is cited by filename.*

Lucas ran a compose, picked the candidate he preferred, and expected to be taken on to the
drawings. He sent the bench's own screen: **Plan `refused · 0 fatal · 43 serious · 4 unjudged`,
Drawings `blocked: refused`, Export `blocked: refused`**, with the AI panel's last question reading
*"I've selected a candidate but it doesn't update the plan workbench"*. His reading: the solver
finished, no fatal flaw, and the house is still rejected.

Everything below was reproduced by execution before anything was changed.

## I. What was found

**1. A click on a candidate column has only ever selected it.** `CandidateColumn`'s `onClick` is
`onSelect`: the decision log beside it follows the pick and the address records it
(`#/candidates/0`). Nothing loads. The one act that puts a plan on the bench is `open in the
workbench`, a small link at the foot of each card, under the score axes. A reader who picks the
candidate they prefer and waits for the next page has done everything the surface asked of them
and is still on the Candidate Set.

**2. The bench keeps its record across a refresh and across a whole compose, and the journey
counted any plan as "the plan".** `planDoc` persists to localStorage. The screenshot's header says
*"On the bench: Tidewater Georgian, five bays, carefully planned · `tidewater-georgian-careful` ·
the example"*: the plan on the bench was the **example opened earlier**, not the candidate. The
journey's candidates step proceeded on `plan_.state !== 'empty'`, so "Next: Plan" led from the
candidate just picked to that example, which WP-13.4 refuses on both engines. The journey's own
tests already said what the step was meant to do (*"the candidates step offers the way"*: with no
plan, Next reads `open a candidate on the bench`); an example left on the bench defeated it.

**3. "0 fatal" and "may be drawn" are two measures, and the surfaces never said so.** A fatal is a
finding the critic raised. A refusal is a hard fact of the house type that the placement did not
hold (`typefacts`: bearing, stacks, tiling). They are independent: a candidate can carry no fatal
finding and be refused, and the Plan step's `refused · 0 fatal` reads as a contradiction to
anyone who takes "fatal" to mean "wrong".

## II. The measurement behind the third finding

`family-georgian`, four candidates, the composer's own call (`compose(brief, 4)`, the revision
loop on, as the app runs it), on this container. Each candidate's plan was then evaluated the way
the bench does on opening it (`evaluate`, `auto`, the interactive budget, two corrective rounds).

| candidate | at compose | on the bench |
|---|---|---|
| side-hall-townhouse | refused: bearing, stacks, tiling · 0 fatal, 19 serious | refused: bearing, stacks, tiling · 0 fatal, 41 serious |
| foursquare-quadrant | refused: bearing, stacks · 0 fatal, 19 serious | refused: stacks, tiling · 0 fatal, 47 serious |
| octagon-radial | refused, infeasible: bearing, stacks · 0 fatal, 19 serious | refused, infeasible: bearing, stacks · 5 fatal, 46 serious |
| centre-passage-double-pile | refused: bearing, stacks, tiling · 2 fatal, 17 serious | refused: stacks, tiling · 1 fatal, 75 serious |

**All four are refused, twice, and two of them (the side-hall and the foursquare) carry no fatal finding on either surface.** The facts a candidate fails are not the same at compose and on the bench for two of the four: a placement is a different draw each time, and a refusal is a verdict on that draw. The
refusal's own lines for the two probed in detail are specific. The side-hall house: *"3 of 3
judged declared stack(s) are drawn clear of the room they name: landing over stair at 0% of the
smaller room"*, *"3 of 3 upper bearing line(s) stand on no ground bearing line"*, and floor
inside no room, *"78.0 sf in all, in 5 strip(s), each located"*. The centre-passage house: the
landing over its stair at 80% of the smaller room, the upper passage over the passage at 30%,
*"5 clear span(s) exceed the capacity the framing tradition states"*, and *175.4 sf* of floor in
no room.

**It is not the interactive budget.** The same two candidates were re-solved on the prover alone
at 25 s and at 90 s: `side-hall-townhouse` is `bearing, stacks, tiling` downgraded at both;
`centre-passage-double-pile` is `bearing, stacks, tiling` at 25 s and `stacks, tiling` at 90 s,
with bearing held. A longer proof moves one fact on one candidate and refuses both anyway. The
refusal is the placement honestly failing the type's facts, which is what WP-13.4 ruled is not
drawn.

**The set is not reproducible.** Two composes of the same brief on this tree returned a fourth
candidate of `connected-farmstead` and then of `centre-passage-double-pile` (the other three
agreed). CP-SAT under a wall clock is not deterministic, which this file has recorded many times;
quote the table as one run. In a third compose with the revision loop off (the browser check
below), the first candidate was `centre-passage-double-pile` at 66.9 with **no refusal flag at
all**, because the flag is written by the placed revision loop and a compose that does not run it
cannot know. That candidate, opened on the bench, was refused there: `0 fatal · 88 serious · 4
unjudged`, *"3 hard facts of the type downgraded (3 conflicts)"*, Drawings and Export blocked.
That is Lucas's screen, reached by the other road.

## III. What changed

All in the workbench app; no Python, no corpus record, no checker.

- **`journey/journey.js`: a plan on the bench leaves the candidates step only where it came from
  this compose** (`planFrom.kind === 'candidate'` and `planFrom.jobId` equal to the session's
  job). The example, a tracing, an earlier job's candidate, an entry recording no origin and a
  stored entry that names another plan all leave the step blocked with its own words, `open a
  candidate on the bench`. Nothing else in the journey moves: the plan, drawings and export are
  judged on the plan and its evaluation exactly as before, and the Plan step itself stays a link.
  The kind is its own condition, not a consequence of the job id: `readPlanFrom` reads a job id
  for any kind off storage.
- **`candidateCard.js::selectionAction`, and a strip in the Candidate Set.** The strip above the
  columns is always on screen, so the act for the picked column is said there: nothing picked
  says how to pick; a drawable candidate is a link, `open <name> on the bench →`; a refused one
  says `<name> is refused, so it cannot be drawn · <the facts it names> not held` in the refusal's
  ink, and offers no link that does nothing. Words are `JOURNEY_WORDS.selection`, the journey's one
  table; the facts are the refusal's own.
- **A tally beside the set's size: `· 4 refused`**, `candidateCard.js::refusedCount` over the cards
  in hand and the glossary's `refused` word. A set in which nothing may be drawn is found at the
  top, not column by column. Counts only a refusal `readRefusal` read: a body this app cannot read
  is not a refusal, and is not a pass.
- **The refused column's own line now names the facts** (`refused — stacks, tiling; not loadable,
  the conflict set is below`), where it said only that it was refused.

Tests: the app suite is **774 against 767**, reconciled by name, 7 added and none removed:
one in `journey.test.mjs`, one in `journeyBar.test.mjs`, five in the new
`candidateSelection.test.mjs`. Two existing tests were re-cut and not re-pinned:
`journey.test.mjs`'s *"a clean evaluated house proceeds step to step"* now gives its plan an origin
from the compose in hand (that is what lets the step proceed, and the new test holds the other
origins), and `candidateOrder.test.mjs`'s adapter guard holds that the surface imports
`adaptCandidate` from the leaf, where it had held the exact spelling of the import line, which
cannot survive the surface also importing the leaf's other names.

**Twelve mutations of the new guards, all red in the end, one blind on its first run.** Weakening
`kind === 'candidate'` to `kind !== 'traced'` changed nothing, because an example's job id is null
by construction, so the kind looked redundant. It is not: a stored `planFrom` carries a job id for
any kind. The fixture now builds an example and a tracing carrying the session's job id, and the
mutation is red. (An earlier draft of the new journey test also passed `check`, a factory in that
file, instead of `check()`; the evaluation then named no plan and the refused state read
unevaluated. A bug in the test, found by the failing assertion.)

Checked in a real browser (the built app, a live server, Playwright): with the example left on
the bench and a fresh compose, Next from the Candidate Set reads `open a candidate on the bench`
and is not a link; picking each column puts the strip's link in; following it lands on the bench
with `planFrom.kind: candidate` and the candidate's own plan id.

## IV. What was deliberately not done

- **The ranking.** `compose._sort_key` still does not read `refused`. That is
  `oq/the-composer-ranks-first-a-house-that-may-not-be-drawn`, which names three readings and was
  never ruled. The table above is a new measurement on it, added there as a dated amendment, and it
  matters to the choice: on this run reading 2 (exclude the refused) returns **no candidates at
  all**. Moving which house a person is offered first is what this file flags for Lucas every time
  it happens, and it was not done here.
- **Un-refusing anything.** WP-13.4's refusal to draw is Lucas's ruling and stands. Nothing here
  loads a refused candidate or draws a refused record; the strip says why it will not.
- **The placer.** Why these partis cannot hold their stacks, bearing lines and tiling inside a
  budget is the Phase 13 gate's own open work (`tests/test_sheet_coherence.py`, red by design),
  and no change to a surface answers it. This report is evidence for how much that gate costs the
  product: for this brief, on this run, no composed house may be drawn.

## V. What is Lucas's to decide

1. **What the Candidate Set does when every candidate is refused**, and in general whether a
   refused candidate should rank below a drawable one. The recommendation, from this measurement:
   rank refused after drawable within the same fatal tier (reading 1), and keep them in the set,
   since excluding them returns nothing here. Not applied.
2. **Whether a refused candidate may be opened on the bench to be read.** The route that serves a
   candidate's record says in its docstring that a refused record is *"exactly what a reader
   diagnosing a refusal needs to open"*, and the Candidate Set refuses to load it because a record
   no bench surface may draw *"reads as the bench being broken"*. Both are WP-13.4's words and they
   disagree. The conflict set is drawn on the Candidate Set itself, so a reader can diagnose
   without opening; the question is whether they should also be able to.

## VI. What this measurement does not establish

One container, one brief, one compose per table row, CP-SAT under a wall clock. It does not show
that Lucas's own deployment refuses the same candidates, and the screenshot cannot say whether his
candidate 0 was flagged refused at compose or was refused only on the bench; both roads end on the
same screen and the changes above address both. Re-derive the table before quoting it.
