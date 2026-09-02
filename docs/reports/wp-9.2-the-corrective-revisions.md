# WP-9.2 — The corrective revisions: a move registry, a loop that refuses, and what the loop found about its own predecessor

*Phase 9, package 2 of 4. 1 September 2026. WP-9.1 built the half that judges; this is the
half that moves. Ruled by Lucas the same day: a deterministic loop, authority over dimensions,
declared choices, openings and optional rooms, on by default everywhere a product is made.*

## What this package is

A plan is drawn, the critic reads the drawing, the analyst says what each finding means, and
now the generator acts: `build/revise.py` picks a registered move for each finding the
registry can answer, applies it to the DECLARED record, re-places and re-judges, and keeps
the result only if the house is strictly better. Every move names the finding it answered
and the corpus sentence it executed; every refusal is stated; what remains after the loop is
sorted into the engine's, the critic's own, and the architect's, and the record carries the
whole account as `revision_report`.

Three things were built, one was rewritten, and one thing the package was built to replace
turned out to have been quietly making plans worse for as long as it existed.

## I — The registry (`moves/registry.json`, `schema/move.schema.json`, `build/moves.py`)

Twenty-one moves and nine stated refusals. A move is data and code held together:

- **`answers`** matches structured fields only — a layer, a `kind`, an `axis`, a fault or
  constraint id — never a sentence. WP-9.1 put the evidence beside the prose so that this
  could be true; the old `repair` read the prose because there was nothing else to read.
- **`basis`** is a sentence really in the record it names, in the grammar's own citation
  form (`rooms/stair-hall.json critical_dimension: "..."`,
  `faults/porch-too-shallow-to-inhabit.json fixes.cheap: "..."`), verified by the same
  `check_openings.check_basis` that verifies the opening grammar. An editorial move carries
  `judgment: true` and says so. **A move with no quotable basis is not in the registry**:
  `align-upper-walls-to-the-room-below` was wanted and is refused for exactly that reason.
- **`touches`** is a list of record paths validated against a CLOSED allow-list under the
  ruled authority — room dimensions and heads, `windows[]`, `doors[]`, `levels[].rooms`,
  `declared.<slot>`, `measurements.<a name the plan already declares>` — and
  `build/check_moves.py` refuses any path outside it and any placement key at all.
- **`tier`** says when a move executes a fault's own `fixes.right` or `fixes.cheap`, so the
  loop tries the right fix first and falls to the cheap one only when the right one refuses.
- **`requires`** is `re-place` or `re-derive`: a dimension moved strips the placement and the
  house is solved again; a declared choice moved keeps the placement and re-derives the
  elevation at 0.4 s.

`APPLY[id](plan, finding, C, ctx)` returns `{changed: [{path, from, to}], log}` or
`{refused: reason}`. *(Corrected by WP-9.4: the sentence that stood here said the `changed`
paths were checked against `touches` at apply time by `tests/test_moves.py`. No such test
existed, and three of the twenty-one moves wrote outside their declaration — one of them
nine authored window counts on the Tidewater plan. `apply()` diffs the record now and
refuses, restoring it, on any write outside `touches` or unreported in `changed`.)*

The **`authority`** block records the ruling verbatim, and the nine **`refusals`** name what
the loop will not do and why: `shorten-for-daylight` (OQ 92 — a size move for an
arrangement finding, retired from `repair`); a move on a critic-suspect (acting on a
finding the critic invented would be laundering the invention into the record); any
`measurements.<name>` the plan did not declare (a generator's number is not the record's to
overwrite); a room the parti has no place for (decision #3); a judgment slot (decision #6); a
placement key (decision #11); `must_have` rooms; `exterior_walls` and `stacks_over`
(aspirations and claims, not fields to edit); and `move-door-to-a-shared-wall`, superseded
by adding the grammar's door rather than re-pointing the author's.

## II — The loop (`build/revise.py`)

Per round: `critique(plan)`; over the `actionable` findings not in the tabu set, **one move
per room per round** (severity first, then registry order), at most six applications, a
lever never batched with a declared move; snapshot; apply; strip the placement if any
applied move requires it; re-critique. **Accept iff the key `[fatal, serious, minor, faults
present]` strictly decreases lexicographically.** On rejection, retry each move as a
singleton in severity order, mark every refused `(move, finding)` pair tabu, restore the
snapshot byte-identically, and CONTINUE. The loop stops for a stated reason — `converged`,
`no-applicable-move`, `round-cap`, `budget` (checked inside a round as well as before it,
accepted state kept), `oscillation` (a sha256 of the stripped declared record seen before) —
never because it gave up quietly.

**Prove first.** Where the placement is the search's and CP-SAT is importable, the proof is
asked for before any declared move, and the tabu earned under the search is forgotten when
the engine changes: a refusal measured under one engine says nothing about the other. Under an
EXPLICIT `--engine heuristic`, `prove-it` refuses — the caller asked for the search by name.

**Acceptance is on the full key in placed mode on purpose.** A declared move that strands a
room on this engine is a worse plan and is refused. That is the guard against accepting a
heuristic artefact, and its cost is that the search engine's own noise refuses good moves;
each such refusal is recorded as `refused_by_measurement` with both keys, and §IV publishes
the rate per engine.

**The reclaim.** With a brief, `compose.reclaim` runs ONCE after the loop under the brief's
area tolerance. An earlier run of the sweep handed back `tower-villa` at
`[3, 36, 46, 0] -> [4, 23, 49, 0]`: six rounds had each refused a new fatal and the reclaim
after the last round re-placed the house and opened one. A reclaim that raises the fatal
count is now rolled back and stated (`revision_report.reclaimed.rolled_back`, with both
keys and the reason). The row no longer reproduces on the current code — the sweep below is
deterministic across processes and hash seeds — so the mechanism is held by
`tests/test_revise.py::TestTheReclaimAfterTheLoop`, which wrecks the reclaim by monkeypatch
and watches the loop hand back the accepted state. **Anything that runs after the acceptance
rule is outside it and has to be held to it separately.**

`_SOLVE_CACHE` is never bypassed and never needs clearing: a declared change is a new key, a
rollback is a hit, and levers change `candidates` or `engine`, which are in the key. WP-7.4's
trap — a sweep over a module constant measuring the first value — does not arise, because the
loop varies call arguments, and the docstring says so.

## III — The composer, the MCP and the CLI

`compose.repair` is a thin wrapper over `revise(place=False)` now, in its old position
before scoring, returning the same `(check, prose_log)` tuple; its prose is in the composer's
own vocabulary and sixteen new `_DECISION_PATTERNS` classify the loop's sentences so
`tests/test_measurement_honesty.py`'s rule — every live decision line is classified — holds.
After ranking, the PLACED loop runs on each returned candidate; the candidate is re-scored on
the stripped declared record so `score` and `score_before` are the same instrument, and it
carries `counts_before`, `rank_before`, `drawn_key_before`/`after`, `revision` (the report
minus the plan) and `REVISED:` decision lines of `kind: "revision"`.

`compose(brief, candidates=4, revise=True, revise_rounds=4, revise_engine="auto",
revise_budget_s=120.0)`; CLI `--no-revise --revise-rounds --revise-engine
--revise-budget-s`. `check_all`'s compose entry runs `--revise-engine heuristic
--revise-rounds 2` so the corpus job stays bounded. MCP: `tdl_critique_plan` and
`tdl_revise_plan` (24 -> 26 tools, both metered), `tdl_compose(..., revise=True)`. The bench's
compose job takes the same options and emits a `revised` event per candidate. CLI
`build/revise.py <plan> [--rounds --engine --candidates --budget-s --declared --json --out]`
and `--sweep`.

## IV — Measured

### The sweep: 21 partis against their first native style, plus both shipped plans, on the search engine, 6 rounds, 250 candidates

| plan | before | after | rounds | applied | refused | stop |
|---|---|---|---|---|---|---|
| bungalow-open-linear / craftsman | [5, 39, 48, 0] | [5, 20, 56, 0] | 6 | 10 | 6 | round-cap |
| cape-central-chimney / cape-cod-colonial | [12, 73, 53, 20] | [3, 59, 59, 20] | 6 | 9 | 9 | round-cap |
| centre-passage-double-pile / beaux-arts-american | [11, 71, 56, 20] | [8, 60, 64, 19] | 6 | 8 | 17 | round-cap |
| centre-passage-single-pile / american-farmhouse-vernacular | [8, 24, 46, 0] | [8, 23, 45, 0] | 3 | 4 | 3 | no-applicable-move |
| charleston-single-piazza / charleston-single-house | [8, 27, 43, 1] | [2, 25, 40, 1] | 2 | 3 | 1 | converged |
| connected-farmstead / french-provincial-farmhouse | [5, 44, 62, 0] | [4, 31, 64, 0] | 6 | 10 | 1 | round-cap |
| courtyard-and-portal / andalusian-courtyard-vernacular | [0, 27, 56, 0] | [0, 21, 55, 0] | 3 | 5 | 1 | converged |
| creole-gallery / creole-cottage-vernacular | [1, 19, 56, 1] | [1, 19, 56, 1] | 1 | 0 | 1 | converged |
| dogtrot-open-passage / dogtrot-vernacular | [0, 8, 27, 0] | [0, 8, 27, 0] | 2 | 0 | 2 | no-applicable-move |
| five-part-palladian / colonial-revival | [14, 101, 70, 20] | [13, 78, 81, 20] | 6 | 10 | 10 | round-cap |
| foursquare-quadrant / craftsman | [8, 56, 47, 0] | [7, 40, 51, 0] | 6 | 5 | 7 | round-cap |
| gable-front-and-wing / american-farmhouse-vernacular | [6, 45, 44, 0] | [1, 31, 48, 0] | 6 | 10 | 11 | round-cap |
| great-hall-h-plan / tudor | [10, 29, 55, 0] | [9, 22, 53, 0] | 6 | 10 | 2 | round-cap |
| hall-and-parlor / american-farmhouse-vernacular | [5, 40, 54, 0] | [5, 35, 56, 0] | 6 | 5 | 11 | round-cap |
| living-hall-picturesque / shingle-style | [8, 31, 53, 0] | [6, 20, 55, 0] | 6 | 9 | 1 | round-cap |
| octagon-radial / octagon-house | [1, 34, 47, 0] | [1, 16, 49, 0] | 6 | 10 | 5 | round-cap |
| ranch-tripartite / ranch-style | [15, 61, 58, 0] | [6, 36, 68, 0] | 6 | 14 | 8 | round-cap |
| shotgun-linear / shotgun-house | [0, 11, 30, 0] | [0, 11, 29, 0] | 2 | 1 | 1 | converged |
| side-hall-townhouse / adam-style | [2, 62, 53, 19] | [1, 52, 54, 19] | 6 | 5 | 3 | round-cap |
| single-cell-hall / norman-vernacular | [0, 9, 20, 0] | [0, 9, 20, 0] | 2 | 0 | 2 | no-applicable-move |
| tower-villa / italianate-villa | [3, 36, 46, 0] | [2, 22, 49, 0] | 6 | 10 | 4 | round-cap |
| tidewater-georgian-careful | [3, 44, 70, 19] | [3, 43, 70, 19] | 5 | 1 | 12 | no-applicable-move |
| spec-builder-colonial | [10, 70, 63, 21] | [6, 68, 64, 20] | 6 | 3 | 17 | round-cap |

Totals over the 23 *(re-measured by WP-9.4 after the lever bookkeeping and the scoped door move; the table above is the re-measurement)*: fatal **135 -> 93**, serious **961 -> 750**, minor **1,157 -> 1,212**;
20 plans improved, 3 unchanged, **0 worse** (the acceptance rule's own guarantee, and the
sweep's reason for existing); 142 moves applied, 131 refused; 68 s in all. **Minor findings
RISE while fatal and serious fall**, and that is the lexicographic key working as designed — a
widened room clears a serious furniture finding and drifts the drawn area outside its declared
band by 12%, which is a minor. Fifteen of 23 stop on the round cap, which says the cap is
binding on the search engine; at 6 rounds the loop is bounded, not finished.

### Per move

| move | applied | cleared its finding | refused |
|---|---|---|---|
| widen-for-furniture | 98 | 25 | 84 |
| widen-to-room-floor | 20 | 17 | 19 |
| raise-window-head | 18 | 11 | 0 |
| light-the-far-end | 2 | 2 | 4 |
| shutter-leaf-at-half-the-opening | 1 | 1 | 0 |
| narrow-the-window-and-keep-the-height | 1 | 1 | 0 |
| delete-the-shutters | 1 | 0 | 0 |
| trade-width-for-depth-at-constant-area | 1 | 0 | 1 |
| grow-to-band-floor | 0 | 0 | 2 |
| give-the-room-a-window | 0 | 0 | 1 |
| grow-stair-hall-to-its-run | 0 | 0 | 1 |
| prove-it | 0 | 0 | 23 (every plan: the sweep asked for the search by name) |

"Applied" counts a move accepted as part of an accepted round; "cleared" counts the ones
whose own finding was gone afterwards. A move applied and not clearing (73 of the 98
`widen-for-furniture`) is one that rode along in an accepted round on another move's
improvement — the room was widened to the figure the finding asked for and the re-placement
put it somewhere the furniture still did not fit. That is the search engine's divergence
(WP-6.3's "the search will place a room below the floor of its own band and say nothing")
seen from the loop's side.

### The refused-round rate, per engine

On the search engine, over the sweep: **131 of 273 applications refused, 48.0%** *(WP-9.4's re-measurement; the 135 of 277 first published was counted through a lever entry that carried no flag)*, nearly all
of them `refused_by_measurement` — the round's key did not strictly improve because the
re-placement moved something else. Under CP-SAT on the Tidewater plan (`--engine cp --rounds
5`): `[0, 40, 65, 20] -> [0, 29, 69, 18]`, 4 rounds, **11 applied, 1 refused**, 160 s *(measured before WP-9.4 found that a round whose proof timed out could be accepted on the declared key; WP-9.4's bounded CP table is the figure to read)*. The
refusal rate is the engine's, not the loop's; a caller reading a high refusal count should
read `revision_report.rounds[].engine` before reading anything into the moves.

### Never fired, and why

`widen-wet-room-for-fixture`, `passage-to-its-band`, `move-window-off-the-needed-wall`,
`replace-forbidden-declared-variant`, `reduce-the-dormer-count-to-the-rhythm`,
`add-the-grammar-door`, `drop-optional-room`, `split-per-grouping`, `search-harder`.

Three reasons, stated so the next reader does not take "never fired" for "does not work":

1. **The precondition did not arise on these 23 plans.** No shipped or instantiated plan
   declares a forbidden variant, an off-rhythm dormer count, a passage under its band or a
   window on the sideboard wall. The moves have unit tests on fixtures that do *(corrected by WP-9.4: four of them had none — `widen-wet-room-for-fixture`, `move-window-off-the-needed-wall`, `grow-to-band-floor`, `give-the-room-a-window` — and have now)*.
2. **The finding is classified `placement` first, and the sweep is on the search engine.**
   An unreachable room, an unplaced fixture, a stair not drawn: WP-9.1 decides these against
   the DECLARED record before anything is called actionable, and on the search engine the
   declared record would have held them — so the finding is the engine's, its lever is
   `prove-it`, and under an explicit `--engine heuristic` that lever refuses. `add-the-grammar-door`,
   `drop-optional-room` and `widen-wet-room-for-fixture` are reached only when a PROVED
   placement still strands the room. That is the ruling's own order — the engine's fault is
   not corrected by editing the author's record — and it means the topology moves the ruling
   granted are exercised under CP-SAT, on demand, and not by this sweep.
3. **`search-harder` is behind `prove-it`** in the lever order wherever CP-SAT is importable,
   which it is here; and where the proof is refused by an explicit engine, so is the search
   lever's reason to exist (the caller chose 250).

### The composer

`python3 build/compose.py briefs/family-georgian.json`:

| | wall clock | winner |
|---|---|---|
| `--no-revise` | ~12 s | Centre Passage, Double Pile, 71.1 |
| `--revise-engine heuristic --revise-rounds 2` (check_all's entry) | 29 s | 71.1 (was 71.1; 1 move; drawn key [10, 51, 72, 21] -> [10, 51, 71, 21]) |
| default (`auto`, 4 rounds, 120 s a candidate), measured earlier in the package | ~5 min | 73.7 (was 71.1; drawn key [10, 51, 73, 21] -> [0, 25, 71, 20]) |

The middle row is the honest one about the fast loop: **after `repair` has run the declared
loop, the placed loop on the search engine has almost nothing left to do**, because what
remains is placement-class and its lever is the proof. The placed loop's value is the proof.
The default row is what a user gets, and it costs minutes; the bench runs it as a job with a
`revised` event per candidate, and `revise: false` is one field away.

**And the default reached the test suite before anything else did.** Thirty-two existing
tests call `compose()` with its defaults — the site tests, the score pins, the garage tests,
the void fixture — and every one of them, the moment the loop was on by default, began
running the placed loop on `auto`: four rounds and up to 120 s a candidate of CP-SAT solves,
per call. The root suite ran 75 minutes of CPU without finishing before that was noticed.
Every one of those callers now says what it wants — `revise=False` where the test is about
something else, the bounded search loop in the one test that checks every live decision line
is classified — because a default that costs minutes is a default a test has to name.
`check_all`'s own compose entry does the same. The library default stays as ruled.

Timings inside: `critique(place=False)` 2.98 s -> 0.91 s after `why_suspect` stopped
re-parsing the elevation's AST per fault (memoised on the file's mtime, per kind — the first
memo evicted the other kind's entry); `repair` 11.2 s -> 2.5 s per pick.

## V — What the loop found about `repair`

`compose.repair` was the only backward edge in the pipeline and the thing this package
replaces. Measured on the family-georgian double-pile candidate before it was rewritten:

- **It accepted the worse result on a non-improving round.** The record was mutated in place
  and the round's verdict compared, and on a worse verdict nothing was restored. Six rounds
  of that is six chances to make the plan worse, taken.
- **`need < width * 1.8`** skipped any room needing more than 1.8x its width, silently — three
  chamber closets at 2.1 ft needing 5.2 ft, every run.
- **It parsed a ROUNDED figure out of prose**, so a 12.3 ft dining room needing 12.333 never
  moved; and the minor branch's "needs about" made `float()` raise and `continue`.
- **One round applied every finding's move from a stale list**: a pantry widened twice, +72%.

None of these was visible from the composer's score, which is taken on the declared record
after `reclaim`. All four are pinned in `tests/test_moves.py` and `tests/test_revise.py` *(corrected by WP-9.4: the stale-list defect was not, and the closet test's primary assertion could not fail; both are pinned now)*.

## VI — Deliberately not done

- **A CP-SAT sweep.** 23 plans x 6 rounds x ~25 s a proof is the better part of an hour and
  the figures would be this container's; the CP numbers published here are the two shipped
  plans'. WP-9.4 ran a bounded one: five plans, four rounds, published in its report.
- **`move-door-to-a-shared-wall`** — refused in the registry: re-pointing an author's door at
  a different room is a change of intent, and adding the grammar's door beside it is not.
  Left open in `oq/the-revision-loops-authority-over-topology`.
- **Running `reclaim` more than once**, or inside the loop. Once, after, under the acceptance
  rule's fatal guard.
- **Acting on a critic-suspect**, or modelling the 35 literal measurements — WP-9.1's OQ.
- **A span finding layer** (OQ 98): `spans_exceeding_capacity` stays an `architect` item.
- **Widening `check_all`'s compose entry to the default loop** — 5 minutes on the corpus job
  for a number `tests/test_revise.py` already holds.

## VII — Raised

- `oq/a-declared-measurement-and-a-window-record-state-one-width-twice` (OPEN):
  `measurements.window_opening_width_in` and `windows[].width_ft` state one width in two
  places nothing holds together; the loop keeps them together by hand for one move.

## VIII — For the audit (WP-9.4)

Things this report asserts that an auditor should try to break: that a refused round is
restored byte-identically (drop the deepcopy); that a move cannot write outside its
`touches` (declare one path, write another); that `search-harder` is never accepted on a key
that improved only in `minor` *(corrected by WP-9.4: lexicographic order PERMITS a
minor-only improvement and §IV shows it accepted; what the audit checked is that the
comparison reads the whole tuple, which it does and which no test had pinned)*; that
`score_before` is taken BEFORE the placed loop *(it is necessarily AFTER `repair`, which is
the composer's declared loop — the "not after repair" half of this sentence was wrong)*;
that the sweep's before and after are different objects *(they were one object whenever no
round was accepted; a copy now)*; that the tabu set is really cleared on an engine change
and not merely reported cleared *(it was cleared on ANY accepted lever, `search-harder`
included; on an engine change only now)*; that the reclaim
guard fires on a rise in `fatal` and not on the whole key (a reclaim that trades a serious
for two minors is kept, on purpose).
