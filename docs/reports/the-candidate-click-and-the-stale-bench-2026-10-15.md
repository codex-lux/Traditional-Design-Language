# The candidate click and the stale bench (15 Oct 2026)

*Not a numbered work package, and deliberately so: a package number is issued from the working
tree and collides across parallel sessions (OQ 90), and this is a defect report with a fix, not a
planned piece of a phase. It is cited by filename.*

Lucas ran a compose, picked the candidate they preferred, and expected to be taken on to the
drawings. He sent the bench's own screen: **Plan `refused · 0 fatal · 43 serious · 4 unjudged`,
Drawings `blocked: refused`, Export `blocked: refused`**, with the AI panel's last question reading
*"I've selected a candidate but it doesn't update the plan workbench"*. Their reading: the solver
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
loop on, as the app runs it), on this container. Each candidate's plan was then put through the
bench's `evaluate` (`auto`, the interactive budget) **with two corrective rounds**.

*(Corrected 16 Oct 2026 by the audit, §VII: this paragraph said that was "the way the bench does on
opening" a candidate. It is not. `PlanWorkbench.jsx` sets its next-evaluate rounds for an example and
for a pasted record only; a candidate opened from the Candidate Set is evaluated with none, and the
route's default is 0. Two rounds is the path the example in Lucas's screenshot took. So the "on the
bench" column below is the bench's evaluation of the same record after two rounds of repair, and not
the first verdict a candidate gets on opening. The third compose below, opened in a browser, is the
real path.)*

| candidate | at compose | on the bench's evaluate, two rounds |
|---|---|---|
| side-hall-townhouse | refused: bearing, stacks, tiling · 0 fatal, 19 serious | refused: bearing, stacks, tiling · 0 fatal, 41 serious |
| foursquare-quadrant | refused: bearing, stacks · 0 fatal, 19 serious | refused: stacks, tiling · 0 fatal, 47 serious |
| octagon-radial | refused, infeasible: bearing, stacks · 0 fatal, 19 serious | refused, infeasible: bearing, stacks · 5 fatal, 46 serious |
| centre-passage-double-pile | refused: bearing, stacks, tiling · 2 fatal, 17 serious | refused: stacks, tiling · 1 fatal, 75 serious |

**All four are refused at compose and refused again on that evaluation, and two of them (the side-hall and the foursquare) carry no fatal finding on either surface.** The facts a candidate fails are not the same at compose and on the bench for two of the four: a placement is a different draw each time, and a refusal is a verdict on that draw. The
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

All in the workbench app; no Python, no corpus record, no checker. Written in two passes: the first
(`6eaa446`, `ad09a47`) and the pass the audit of it forced (§VII, 16 Oct), which is folded in here so
this section says what the tree does.

- **`journey/journey.js`: a plan on the bench leaves the candidates step only where it came from
  this compose** (`planFrom.kind === 'candidate'` and `planFrom.jobId` equal to the session's
  job, both trimmed alike), **and, where a candidate is picked on the Candidate Set, only if it is
  the one picked** (`planFrom.n`; `pickedCandidate(surface, selection)` is the one reader of the pick
  and `App.jsx` and `JourneyBar.jsx` both pass it). The example, a tracing, an earlier job's
  candidate, an entry recording no origin and a stored entry that names another plan all leave the
  step blocked. The job-level test alone could not tell candidate 0 on the bench from the candidate 3
  just picked, and Next led to the first: the original complaint with the right job (§VII, F8).
  Nothing else in the journey moves: the plan, drawings and export are judged on the plan and its
  evaluation exactly as before, and the Plan step itself stays a link.
- **The step's reason says something a reader can follow.** *open a candidate on the bench* remains
  the default; *open the candidate you picked on the bench*, *the candidate you picked is refused*,
  *every candidate is refused, so none can be drawn* and *no candidate was returned* are said where
  they are the case. The old single reason was an instruction with nothing behind it when no
  candidate could be opened.
- **`candidateStanding.js` (new leaf): what the type's facts have been asked of a candidate.**
  `refused` is `null` on three different candidates: one the placed loop judged and did not refuse;
  one nobody asked (the first-pass candidate, which `compose.py` writes as `None` on purpose, one the
  set's revise budget did not reach, every candidate of a compose with the loop off); and one whose
  verdict this app cannot read. The first version of this change read `null` as *may be drawn*, which
  collapsed the second and third into the first. `standingOf` is `refused` | `placed` | `unjudged`,
  and `unjudged` is not a pass.
- **`candidateCard.js::selectionAction`, `selectionView`, and a strip in the Candidate Set.** The strip
  above the columns is always on screen, so the act for the picked column is said there: nothing
  picked says how to pick (or, for a set with nothing to pick, that the brief or the parti is what
  changes); a placed candidate is a link, `open <name> on the bench →`; an unjudged one is a link that
  says it is not judged for drawing and may be refused; a refused one says `<name> is refused, so it
  cannot be drawn · <the facts it names> not held` in the refusal's ink and offers no link. The
  element, the ink and the words are decided in the leaf (`selectionView`) and unit-tested; the surface
  renders them. Words are `JOURNEY_WORDS.selection`, the journey's one table.
- **A tally beside the set's size: `· N refused` and `· N not judged for drawing`**, off
  `setStanding`; silent at zero. A set in which nothing may be drawn is found at the top, not column
  by column.
- **A refused column says so where "fatal 0" is read**: a refused mark on the counts line, and its
  foot line now names the facts (`refused — stacks, tiling; not loadable, the conflict set is below`).
- **The open act can fail and says so.** `openInWorkbench` had no `catch`, the server keeps a compose
  for a while and forgets it, and the candidates stay on screen: the link, now the primary route,
  did nothing and said nothing. It holds the act while a request is out, opens the candidate at its
  own index (`c.n`, not a lookup), and says a 404 is a compose the server no longer keeps.

Tests: the app suite is **786 against 767**, reconciled by name against `e00ef29`: 19 added, none
removed (7 in the first pass, 12 in the audit's). Two existing tests were re-cut and not re-pinned:
`journey.test.mjs`'s *"a clean evaluated house proceeds step to step"* now gives its plan an origin
from the compose in hand, and `candidateOrder.test.mjs`'s adapter guard holds that the surface imports
`adaptCandidate` from the leaf, where it had held the exact spelling of the import line.

**Forty-one mutations of the new code, five blind on the first sweep, all red in the end.** The five
were the surface's conditionals (the tally, the unjudged tally, the error line, the failed-open
branch, the column's refused mark): every test of the first pass that touched the surface read its
source for a few literal tokens, so a rewritten condition passed. They are held by pinned joins now
and, truer than a regex, by the walk, which drives each in a browser (below). The first pass's own
mutation record was twelve, one blind (`kind !== 'traced'`, fixed by giving the fixture an example
and a tracing that carry the session's job id).

**The walk, held against a control and then driven.** `e2e/walk.mjs` reads each expectation off the
SERVED job's raw fields, never off the app's own reader. Its compose runs with the loop off, so every
candidate it meets is one nobody judged, and its first-pass check read `want open` against a set with
nothing refused: the refused strip, a tally above zero and the refused column's line were driven by
nothing (§VII, F4). It now rewrites the job on its way to the page, so that one candidate is refused
by the type's facts with no fatal finding and the next was placed and not turned down, puts a stale
EXAMPLE on the bench, and asserts: Next is held with nothing picked; the refused pick says it cannot
be drawn, offers no link, is tallied and marked on its counts line and at its foot; the placed pick
offers a link and Next is still held until it is opened; the open is held while in flight and, when
the plan route answers 404, is said where it was asked and offered again; opening records the
candidate of THIS job at its index; Next then leads on to the plan; and picking the other candidate
holds it again. The bench and the address are put back afterwards.

*The control.* The first pass's two checks (the strip's act, the tally) were run against a pristine
worktree of the parent, `e00ef29`, where both FAIL (*"want open, read null"*; the tally one only
through the presence guard, which is what that guard is for), and against this tree, where both pass.
The rewritten and added checks were run against this tree only: they assert elements the parent
does not render, so a parent run would fail them for that reason and show nothing about them.

*One instrument artefact worth keeping.* A walk's sign-in Gate block starts a second server from the
same checkout on the walk's port plus one, which for a walk on 8179 is 8180. A control server parked
there meets a walk expecting a password and the Gate block reads seven fewer checks. Not code; do not
park another server on a walk's port + 1.

## IV. What was deliberately not done

- **The ranking.** `compose.rank_key` (the sort the composer applies) still does not read `refused`. That is
  `oq/the-composer-ranks-first-a-house-that-may-not-be-drawn`, which names three readings and was
  never ruled. The table above is a new measurement on it, added there as a dated amendment, and it
  matters to the choice: on this run reading 2 (exclude the refused) returns **no candidates at
  all**. Moving which house a person is offered first is what this file flags for Lucas every time
  it happens, and it was not done here. *(16 Oct 2026, later that day: Lucas ruled reading 1 when asked,
  and it is done. §VIII.)*
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
   since excluding them returns nothing here. Not applied; nothing here rules between the readings.
   *(Ruled 16 Oct 2026: reading 1, as recommended. Executed; §VIII.)*
2. **Whether a refused candidate may be opened on the bench to be read.** Now its own question,
   `oq/a-refused-candidates-record-is-served-for-diagnosis-and-the-candidate-set-will-not-load-it`
   (the audit found it living only in this report): the route that serves a candidate's record says
   in its docstring that a refused record is *"exactly what a reader diagnosing a refusal needs to
   open"*, and the Candidate Set refuses to load it because a record no bench surface may draw
   *"reads as the bench being broken"*. Both are WP-13.4's words and they disagree. The conflict set
   is drawn on the Candidate Set itself, so a reader can diagnose without opening.
   *(Ruled 16 Oct 2026: keep a refused candidate unopenable. The route's docstring is corrected to the
   surface's statement. §VIII.)*

## VI. What this measurement does not establish

One container, one brief, one compose per table row, CP-SAT under a wall clock. It does not show
that Lucas's own deployment refuses the same candidates, and the screenshot cannot say whether their
candidate 0 was flagged refused at compose or was refused only on the bench; both roads end on the
same screen and the changes above address both. Re-derive the table before quoting it.

## VII. The audit of this change (16 Oct 2026)

Lucas asked for a genuine adversarial pass before the work was called done. Four auditors read the
diff `e00ef29..ad09a47` from four angles, each briefed neutrally (the intent and the repo's rules, none
of the author's conclusions): regressions and every consumer of a changed contract; whether the new
tests can fail (70 single-edit mutants, run in a worktree of their own); second-order risks and a
sweep for second occurrences of the same patterns; and re-derivation of every claim in the commit
messages, this report, the open-question amendment and CLAUDE.md. Every finding below was checked by
the author before it was acted on, and the ones that were measurable were measured. **No auditor found
a defect that blocks deployment; the audit found a real second-order failure in the change's own
reading of the data (F1), a gap that left the original complaint reproducible with the right job (F8),
and a test layer that could not see the surface it was written for (F4/F5).**

| # | finding | severity | introduced? | outcome |
|---|---|---|---|---|
| F1 | `refused: null` was read as *may be drawn*. It is also what a candidate nobody judged carries (the declared first pass writes `None` on purpose, a candidate the set's revise budget did not reach, every candidate of a `revise: false` compose, a loop whose first placement could not be evaluated, a verdict this app cannot read). The strip said `open X on the bench →` for those and the tally omitted them: the screen the change was written to prevent, by the third road. | worth fixing | introduced | **fixed**: `candidateStanding.js`, a third state (`unjudged`) with its own words and tally |
| F2 | The all-refused set was a dead end whose instructions could not be followed: *"select a candidate to open it"* and *"open a candidate on the bench"* when nothing could be opened. | worth fixing | introduced (copy over a pre-existing gap) | **fixed**: the strip and the step's reason say that every candidate is refused / none was returned, and that the brief or the parti is what changes |
| F3 | `openInWorkbench` had no `catch`. The server forgets a compose after a while while the candidates stay on screen, so the primary link did nothing and said nothing, and a double click loaded twice. | worth fixing | pre-existing, now the primary route | **fixed**: held in flight, a 404 is said, other failures say what the server said; driven in the walk |
| F4 | The walk's compose runs with the loop off, so every candidate it meets is unjudged: the new walk checks read `want open` against a set with nothing refused. The refused strip, a tally above zero and the refused column line were driven by no check. | worth fixing | introduced | **fixed**: the walk rewrites the served job to carry a refused and a placed candidate and asserts both branches in a browser |
| F5 | The surface's conditionals were held by one regex over its source: 5 of 41 mutations passed (§III). | worth fixing | introduced | **fixed**: the decisions are in leaves and unit-tested, the joins are pinned, the walk drives each |
| F6 | The headline fix (Next held for a stale example) had no walk check; the walk's generic Next check reads green whether Next is blocked or leads to the stale plan. | worth fixing | introduced | **fixed**: the walk leaves an example on the bench and asserts Next is held with nothing picked |
| F7 | The `str(origin.jobId) &&` guard (null === null) could be deleted with every test green; and the job comparison trimmed one side only. | minor | introduced | **fixed**: both sides trimmed alike; a both-null table |
| F8 | The Next fix was per job, not per pick. With candidate 0 of this compose on the bench and candidate 3 picked, Next led to candidate 0's plan: the original complaint, with the right job. | worth fixing | introduced (the first pass's scope) | **fixed**: `journeyState({ picked })`, per pick; reasons say which |
| F9 | `docs/prd/phase-14-the-dossier-and-the-journey.md` §G still gave the candidates step's `canProceed` as *plan is not `empty`*: the contract the rule changed. | worth fixing | introduced | **fixed** |
| F10 | This report said each candidate was evaluated *"the way the bench does on opening it ... two corrective rounds"*. It is not: two rounds is an example's or a paste's route; a candidate opened from the set gets none. The "on the bench" column is a different evaluation from what a person gets on opening. | worth fixing | introduced | **corrected in place, dated**, here and in the OQ amendment |
| F11 | The second question in §V (may a refused candidate be opened to be read) lived only in this report and CLAUDE.md. | worth fixing | introduced | **fixed**: its own open question |
| F12 | The OQ amendment overstated: a heading that generalised one run, *"right wherever the set is mixed"* asserting a recommendation as fact, *"the surface now says it"* when the per-column line and the conflict set predate this change, and an italicised paraphrase of Lucas's report that read as a quotation. CLAUDE.md's entry lacked the one-run qualifier. The commit message and report said `compose._sort_key`: it is a local alias of `compose.rank_key`. | minor | introduced | **corrected in place, dated** |
| F13 | `selectionAction` wrote its own words (*cannot all hold*, *not held*) against its own comment; *"stacks cannot all hold"* is ungrammatical for one fact. | minor | introduced | **fixed**: `JOURNEY_WORDS.selection.held(kind, k)` |
| F14 | A refused column's header counts read `fatal 0 serious N minor M` with nothing beside them; the refusal sat at the foot of the card. | minor | pre-existing, exposed | **fixed**: a refused mark on the counts line |
| F15 | `selectionAction().n` was a dead output, and the open used a `findIndex` that happens to equal it. | minor | introduced | **fixed**: the open uses `c.n`; the test that pinned it now pins a consumed value |

**Found and deliberately not fixed, each with its reason** (the first three were put to Lucas as
suggested tasks, queued on a second attempt after the tool timed out on the first; they are written
here in full as well):

- **A composed plan's id is `{parti}-{briefId}`, and every from-scratch brief's id is `new-brief`.**
  The same parti from two composes, or from two different briefs, has one plan id. The new job
  condition rescues `planFrom`; two id-keyed matchers are not rescued: `App.jsx` clears the last
  evaluation only when the plan id changes (opening the same parti from a later compose keeps the
  previous verdict beside the new record until the debounce plus the solve replaces it, up to about
  25 s), and `briefNameOf` matches on a brief id that is always `new-brief`. Pre-existing. A fix is
  either app-side (key the evaluation to the plan's origin as well as its id) or composer-side (ids
  are stable by rule and cited in files, so every consumer must be read first); not decided here.
- **The AI panel is told `fatal 0` for a refused house.** `rail/railContext.js` sends the plan with no
  origin and `last_eval` as counts only, and `rail.py` writes *Latest validator summary* from it.
  This is the original misreading on a second surface, and the assistant's own last line in Lucas's
  screenshot was about this screen. Pre-existing and unrelated to this diff; a payload change on the
  rail, which the tranche rulings freeze per item.
- **A candidate column can only be selected with a mouse** (`<section onClick>`, no tabIndex, role or
  key handler), so the strip's *select a candidate* cannot be followed from a keyboard; nor is the
  strip a live region. Pre-existing; a role on the section would nest around real buttons, so the
  pattern needs choosing.
- **The front door's "Continue" and the nav map still read any plan on the bench as the house in
  hand** (`resume` goes to the plan step whenever one exists, the nav map shows step words with no
  origin). The bar's Plan step does say where the plan came from; the front door does not. Minor.
- **A plan on the bench with no evaluation in hand reads Drawings and Export as *ready*** after a
  reload (the last evaluation is held in React state only). The server still refuses at draw time.
  Pre-existing; minor.
- **A pasted or traced record with the same id as the candidate opened from this compose** inherits
  that candidate's `planFrom`. Needs a hand-built collision; minor.
- **After a compose has been reaped, a plan that really did come from it no longer carries Next**
  from the candidates step (its job is gone). The Plan step stays a link and the page says the
  compose expired; accepted as the honest reading.
- **Layout.** `FilterStrip wrap` lets the strip gain or lose a row as the act's words change on a
  pick, shifting the grid below at 1280 px and under. Not measured in a browser at width; minor.
- **The tally's denominator.** `· N refused` counts the appended named candidate that `returned X of
  Y asked for` does not. Minor.
- **The walk's three red checks.** All three are `trim-classical`'s Proportions plate label overlap
  (check ⑩, 41 of 61 labels and one zone text), red on the parent in this container and untouched by
  this change. The closing record of WP-16.8 (3 Oct 2026) is *702 green, none failed*, and the parent
  here is 699 ok and these three: whether that is this container (a label overlap is a font
  measurement) or a change since 3 Oct is not established here.

**What the audit could not check.** The browser rendering of the strip at narrow widths; Lucas's
deployment; the report's per-candidate figures (an auditor's own compose reproduced the qualitative
result, 4 of 4 refused, and not the table: a different set and order, which is the point of §II).

**Verification after the audit's fixes.**
- App suite **786 of 786**, reconciled by name against `e00ef29` (19 added, none removed), `vite build`
  clean.
- 41 mutations of the new code, run in a worktree of their own, all red; 5 were blind on the first sweep
  (§III) and are closed.
- The browser walk against a live server (Chromium, the built app): 711 ok and 3 failed on the final code, the 3 being `trim-classical`'s
  label-overlap checks (⑩) that are red on the parent too (699 ok and the same three there); 709 ok
  and the same three on the run before the failed-open drive was added. Against a deliberately broken
  build (four mutations of the surface: a link for a refused pick, a silent failed open, a bar that
  ignores the pick, no refused mark on the counts line) the same walk read 706 ok and failed five of
  the new checks beside those three, so they bite.
- Checkers and tests: app suite, `vite build`, `check_counts` (0 stale), `check_citations` (0
  dangling), `check_ids`, `gen_open_questions --check` and the open-question list and counts tests
  are green.
- **The whole `build/check_all.py`, on a clean `git worktree` of `5a0106a` (16 Oct 2026, 1 h 11 m for
  `pytest tests/`), is `2 of 54 checks failed`: 21 failed / 3,787 passed / 132 skipped.** The app
  suite is 786 of 786, the server suite 439 passed / 19 skipped, and three checks could not be
  evaluated, each by name and none a pass: no `dist/` (the frontend's lazy-tier check), and the DXF
  and IFC selftests, because `ezdxf` and `ifcopenshell` are not installed in this container.
  - **Every red is attributed by id against a `git worktree` of the parent `e00ef29`**, the 21 ids run
    alone on both trees. The parent fails 20 of the 21 identically: 18 `test_sheet_coherence.py` gate
    rows, `test_parti_composability.py`'s composability row and `test_solver.py`'s half bound. The
    two failing checks are `check_partis.py` (its `side-hall-townhouse` fatal, the same sentence on
    both) and `pytest tests/`.
  - **The 21st is `test_every_upper_bearing_line_stands_on_a_ground_bearing_line[careful-cp]`**, a
    prover-band row, which the parent passed in the 21-id run. Run alone, it passes 12 of 12 on the
    parent and 11 of 12 on this tree (one failure, in the third round of an alternation). The two
    trees are byte-identical in every file outside `workbench/app/`, `docs/` and `CLAUDE.md`
    (`git diff --name-only e00ef29 HEAD` outside those is empty), so the failing row reads the same
    Python and data on both and the difference can only be the 40 s CP-SAT wall clock. That is the
    row WP-16.4 and WP-16.8 recorded the same way; a failure on the parent was not reproduced here,
    so this is attributed by identity of inputs and not by a red on the control.
  - **132 skipped is this container's, not the change's**: with `ezdxf` and `ifcopenshell` absent
    the DXF- and IFC-gated tests skip (CI installs `ezdxf`). The change touches no Python and no data
    file, so none of those tests reads anything it moved. Judged in CI, unjudged here.

## VIII. The four rulings, and what executed them (16 Oct 2026, `e048a89`)

The audit of §VII left four questions that were Lucas's, and they were put to them directly. All four
were answered as recommended.

| # | question | ruling | where it landed |
|---|---|---|---|
| 1 | Within equal judged fatals, where does a refused candidate rank? | **Last.** | `compose.rank_key`: judged fatals, then the placement's standing (drawable, not yet placed, refused), then the unjudged fatals (R13), then the score |
| 2 | May a refused candidate be opened on the bench to be read? | **No: it stays unopenable.** WP-13.4's refusal to draw stands. | the route's docstring now says what the surface says; the conflict set beside the column is where it is read |
| 3 | How are two composes of one parti told apart, given the plan id is `{parti}-{briefId}`? | **App-side: key the evaluation to where the plan came from. No id changes.** | `journey.js::originKeyOf`, `stampEval`, `evalIsOf` |
| 4 | Is the assistant told a house is refused? | **Yes.** | `lastEvalSummary` sends `{kind, facts}`; `rail.py` writes one sentence for it |

What was found while building them, kept because each changed what was built:

- **The ranking mostly has nothing to rank.** With the app's own compose call (`auto`, the revision
  loop on), every candidate of both shipped briefs was refused in 3 of 4 composes, and the fourth
  refused three of four. The key is right and decides little; the cause is upstream
  (`oq/the-composer-returns-sets-in-which-nothing-may-be-drawn`). The refusal kinds and facts
  measured there are the vocabulary the assistant's payload is validated against.
- **The brief-name collision was smaller than reported.** The brief form derives the brief's id from
  its name, so two briefs rarely share an id. What was real is that the name was read off the draft,
  which moves on after the compose; the job's brief is kept at compose time now.
- **A layout shift the first fix of the strip left.** Picking a refused column and then an open one
  moved the grid under the pointer, 27 px at 1100 and 47 px at 1680, because the act's words are a
  short instruction in one state and a sentence naming facts in the other. The act has a row of its
  own with a floor, and a further 21.5 px came from the journey bar's longer reason wrapping Next onto
  a second row, so the reason was shortened. Measured with a probe at both widths; the bar's wrap is
  not fixed in general (`oq/the-journey-bars-next-jumps-rows-when-the-strip-wraps`).
- **Three walk checks that read red in this container are not this change's.** The ⑩ plate-reader
  checks fail identically at `6873f91`, the commit whose recorded walk is 702 green. The container has
  neither EB Garamond nor Courier Prime installed; the cause is not proven.

## IX. The audit of §VIII (16 Oct 2026)

Lucas asked for the audit again before the work was called done. Three auditors read `3bf9da8..e048a89`,
one on the Python and the composer and the assistant's server, one on the origin keying and the
session, one on the surface and the walk. Each was briefed on the intent and the repo's rules and not
on the author's conclusions. Every finding was reproduced before it was acted on. **One finding
blocked deployment** (row 1); the rest were worth fixing or minor.

| # | finding | severity | introduced? | outcome |
|---|---|---|---|---|
| 1 | `CLAUDE.md`'s open-question list and its entry count were not updated for the three questions this work closed or raised, so `tests/test_wp46_packs.py::test_claude_md_open_question_list_is_derived_from_the_file_not_asserted_against_a_literal` was red and CI would have gone with it | **blocks** | introduced | **fixed**: 282 entries, 157 open, derived from the register |
| 2 | The Candidate Set's own orderings never read the standing, and its default is "highest score first": the composer put the refused house last and the surface put it first again | worth fixing | introduced (the ruling's second reader) | **fixed**: "fatal first" is the composer's key; the other two demote a refused plan first; `tests/fixtures/candidate_rank.json` holds both languages to one table |
| 3 | `how_to_read_this` and `tdl_compose`'s description still said the unjudged fatals decide between equal fatals | worth fixing | introduced | **fixed**, and held by the driven test |
| 4 | The assistant's sentence: `$` admitted a trailing newline; any short lower-case word was a fact; "the counts above" pointed at counts that were absent; the kinds were restated in `rail.py`; a working sketch (the wall drag's quick search) was never said to be one | worth fixing | introduced | **fixed**: facts are the type's own four, read live from the leaf; kinds are `typefacts.REFUSAL_KINDS`; wording follows whether counts exist; a sketch is said to be one, and a refused sketch is not called undrawable |
| 5 | `placement_standing` took any truthy `refused` for a refusal; the app takes only a body of a kind the leaf mints. A body nobody here wrote was `refused` to one reader and `unjudged` to the other | worth fixing | introduced | **fixed**: `compose.reads_as_refusal`, and seven hostile rows in the shared table, held in both languages |
| 6 | The driven compose test's docstring read as though it showed a real mixed set | minor | introduced | **corrected in place** |
| 7 | The ranking question's execution note said 15 mutations; one repeated another | minor | introduced | **corrected in place**: 14 distinct |
| 8 | A late answer for one house was filed against another, and the bench read the unfiltered evaluation for the interval before the shell's clear ran | worth fixing | introduced | **fixed**: `answerIsForHere` drops it before it files anything; every surface and the assistant are handed `lastEvalHere` |
| 9 | An undo across a same-id document change restores the record and not its origin | minor | introduced, rare | **Lucas ruled leave it**: `oq/an-undo-across-a-document-change-restores-the-record-and-not-its-origin` |
| 10 | `clearPlanFrom` cleared an origin that named a different plan, so an undo back to that house found no origin | minor | introduced | **fixed**: it clears only an origin that names the plan being loaded |
| 11 | `jobBrief` kept id and name; the count asked for ("returned 3 of 4") and the household still read the draft | minor | introduced | **fixed**: the job's brief keeps the four things the surface prints |
| 12 | The census of `planDoc.load(` was a text match an alias walks round | minor | introduced | **fixed**: a second guard holds every use of the store to its own name and a known method (driven by three mutations) |
| 13 | The downloaded check report carried the app's own stamp | minor | introduced | **fixed**: `unstampEval` |
| 14 | A comment claimed the grid does not move at the widths the shell is used at; it was measured at two | minor | introduced | **corrected**, and the journey bar's wrap is its own open question |
| 15 | The keyboard check focused the target directly, which reaches an element no key can | worth fixing | introduced | **fixed**: a real Tab traversal |
| 16 | The live-region guard took the first `</span>` after a marker, the inner span's | worth fixing | introduced | **fixed**: a balanced scan, itself driven; the walk asserts the alert is outside the region |
| 17 | The open act was `disabled` while the request was out, dropping the focus the press was made with | minor | introduced | **fixed**: `aria-disabled`; the walk reads that the focus stays |
| 18 | The front door's origin phrase could wrap with its separator alone on a line | minor | introduced | **fixed** |
| 19 | The assistant's context did not carry the sketch flag or the sketch's own refusal (the app's half of row 4) | minor | introduced | **fixed** |
| 20 | The walk's stale-verdict block had a branch that fell through without saying so, and did not assert that the two opens shared a plan id, which is the premise | worth fixing | introduced | **fixed**: every branch says it was not judged, and the premise is asserted |
| 21 | The strip's floor used the `lh` unit | minor | introduced | **fixed**: `2.9em`, held to the token's line height by a test |

**Deliberately not changed.**

- Whether a never-placed candidate belongs between a drawable and a refused one was put to Lucas, who
  ruled to **keep three tiers**.
- Row 9, by ruling.
- The journey bar's Next wrapping onto a second row at narrow widths: a design question with a
  cheap guard and a costly fix; open.
- That the browser walk does not drive row 8's late answer. The decision is a pure function and the
  join is pinned in source in order; the walk drives the nearest observable (the bench's caption
  carries no engine verdict for a house that has not been evaluated).
