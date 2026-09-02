# WP-9.4 — The adversarial audit of WP-9.1 through WP-9.3: the things the reports said were checked

*2 September 2026. Three read-only explorers built the claim-to-guard matrix for every sentence
in the three Phase 9 reports; three auditors in isolated worktrees reverted each fix one at a
time and watched the suites; every finding below was reproduced before it was fixed, and the
mutation that proved it is named beside it. **Six blocking defects, nine tests that could not
fail, fourteen sentences in the reports that were false or stale**, and a re-measurement of
every number the phase published. The three findings worth reading first are the ones that
say something about how this corpus fails.*

## The three findings worth reading if you read nothing else

**1. A declaration nobody connected to behaviour, under a sentence saying it was tested.**
WP-9.2's report: *"the `changed` paths are checked against `touches` at apply time by
`tests/test_moves.py`, so a move cannot declare one path and write another."* No such test
existed anywhere in the repository. `touches` was a string held against an allow-list — a
constraint on the registry's TEXT — and nothing ever compared it to what an apply function
wrote. Auditor A deep-diffed the record before and after every move and found three of the
twenty-one writing outside their declaration. The worst: `add-the-grammar-door` ran the
composer's `symmetrise_doors` and `derive_openings` over the WHOLE plan for one door. On the
placed Tidewater plan that was **253 paths written in 25 rooms, reported as 2**, and nine of
them were authored window counts — `dining.windows[0].count 2 -> 1`, `drawing.windows[1] 2 ->
3` — the silent overwrite of an author's intent that WP-6.2's whole package existed to remove,
back through a move the ruling had granted. `derive_openings` is scoped now (`rooms=`,
`doors=`, `windows=`, `pairs=`); a move derives the openings it added and nothing else; and
`apply()` diffs the record, holds every written path against `touches` in the registry's
spelling, and **refuses, restoring the record, on a write outside it or one `changed` does not
report**. The test the report described exists now. The rule: a declaration a checker reads
is documentation until something compares it to the code.

**2. A flag written where nobody reads it, and a published rate measured through the gap.**
`revise.py` wrote a lever's `refused_by_measurement` on the ROUND and never wrote `accepted`
on a lever at all — and the summary, the sweep's per-move table, the CLI print and the bench's
`round` event all read the MOVE ENTRY. So an accepted proof counted as **0 moves applied** on
an improved key, a proof rolled back by measurement reached the bench as *"applied; its
finding persisted"*, and the refusal rate WP-9.2 published — 135 of 277, 48.7% — was counted
through the gap. Re-measured after the fix: **131 of 273, 48.0%**. Auditor B proved it with
`_improves` forced False on an `auto` run; Auditor C printed the SSE event's move entry with
no flag on it. The rule is WP-8.6's again: two records built from different rules, and nothing
compared them.

**3. Both new routes handed a caller-supplied parti RECORD straight to geometry.**
`critique()` and `revise()` read `core.load_parti(parti) if isinstance(parti, str) else
parti` — right for the sweep, which passes the templates it read itself — and the WP-9.3
routes passed `body.get("parti")` through raw. Auditor C posted `{"scaling":
{"bay_module_ft": 0.5, "max_bay_count": 200}}` and got a 200 in 2.7 s with **114 bays of half
a foot** and a key of `[12, 41, 63, 18]`; `"abc"` and `[1, 2, 3]` were 500s. The evaluate route
had always been safe (`load_parti` unconditionally). `test_parti_confinement.py` could not see
it: every escape it tries is a string, and the revise route was not in its endpoint list. A
parti is an ID over the wire now, refused as a record by both routes and by
`core.critique_plan`/`core.revise_plan`; both routes are in the confinement list with a
dict-escape case. **A confined loader is only as confined as the `isinstance` in front of it.**

**And a sixth, found by this audit's own measurement rather than by reading.** The bounded
CP-SAT run handed back the Tidewater plan at `[0, 40, 65, 20] -> [0, 22, 58, 19]` with
`engine.final: null` — an accepted state that carried **no placement at all**. A proof had
timed out inside a round; `critique()` reported the placement as could-not-evaluate and its
key from the DECLARED check, which has no drawn findings in it and is lower for that reason
alone; `_improves` compared the two keys and took it. **Unjudged read as passed, in the loop's
own acceptance rule** — the corpus's cardinal error, inside the mechanism built to hold the
line. A critique whose placement could not be evaluated is never an improvement now, and a
placed loop whose FIRST placement cannot be evaluated stops before its first round and says
so (`stop_reason: placement-could-not-be-evaluated`, `placement_unjudged` on the report).
The row is re-measured below.

## I — What blocked (fixed, each with the mutation that proved it and the test that now bites)

| # | defect | proved by | fixed; guarded by |
|---|---|---|---|
| 1 | `touches` enforced nowhere; three moves wrote outside it; `add-the-grammar-door` rewrote nine authored window counts | Auditor A: deep diff of the plan around every move; a rogue apply writing `ceiling_ft` under `widen-for-furniture` passed every test | `moves.apply` diffs and refuses; `derive_openings` scoped; `tests/test_moves.py::TestTheDeclarationIsEnforced` (rogue write refused and restored; unreported write refused; Tidewater door leaves every count and every other room alone) |
| 2 | a parti RECORD reaches `geometry.py` unchecked on `/api/plan/critique` and `/api/plan/revise` | Auditor C: 114 bays of 0.5 ft in 2.7 s; 500s on a string and a list | `_parti_id()` 422s; `core.critique_plan`/`revise_plan` refuse a non-string; `test_parti_confinement.py::test_a_parti_record_is_refused_not_used_as_the_template`, and the revise route in `ENDPOINTS` |
| 3 | the lever's verdict on the round, not the move: accepted proof = 0 applied; rolled-back proof reads "applied" | Auditor B: `_improves` forced False on `auto`; Auditor C: the SSE event's move entry carried no flag | the entry carries `accepted` / `refused_by_measurement` / `key_after`; `tests/test_revise.py::TestWhatTheAuditFound` (a refused lever is counted; an accepted proof is one move applied), scripted through a fake critique so no solver runs |
| 4 | `/api/plan/revise` with no `budget_s` is no budget: 8 rounds of proofs on the one-worker pool, against the route's own docstring | Auditor C: `revise()` received `budget_s=None` | a budget always (120 s default, 600 cap), rounds floor 1; `test_a_revise_job_always_has_a_budget_and_at_least_one_round` |
| 6 | a round whose re-placement could not be evaluated reports the declared key, lower by absence, and is accepted | this audit's CP-SAT run: Tidewater accepted at `[0, 22, 58, 19]` with no placement; reproduced with `critique(engine="cp", time_limit_s=0.5)` → key `[0, 29, 60, 19]` against the placed `[3, 44, 70, 19]` | `_improves` refuses an unjudged placement; a placed loop with an unjudged first placement stops and says so; `tests/test_revise.py::TestUnjudgedIsNotBetter` |
| 5 | the literal detector blind to five shapes already in `elevation.py`, and `0.5`/`2.0` exempted as unit conversions | the explorer, by reading; confirmed by running: 35 -> 44, 4 -> 7 | `_literal_value` reads a constant dict by subscript (`SASH_FRAME`, four measurements), a ternary, an `or 3`, `max(1, …)`, a literal one level down a `BinOp` (`4 * width`); both fold sites after `_derive_measurements` read; ceilings re-baselined UP once, named in the checker; `TestTheInstrumentOnTheRealFile` names the shapes on the real file |

## II — Worth fixing (fixed)

- **The tabu was cleared on ANY accepted lever.** `search-harder` changes the candidate
  count, not the engine, and a refusal under 250 candidates says the same under 1,000. Cleared
  only when `engine.ran` changes now; `tabu_forgotten` tested through the scripted critique.
- **`critique_before is critique_after`** whenever no round was accepted — one dict under two
  names, and `remaining`, `handed_to_architect` and `suspects` built from it. A copy now.
- **`revise(rounds=0)` said `stop_reason: "round-cap"`** for a loop that never started, and
  still cost a full placement; `stop = "no-rounds"` now and the two dead lines after the
  `while/else` are gone. The route's floor is 1: a revise of zero rounds is a critique, and
  the critique route exists.
- **An exception in `on_round` killed the job** and discarded the loop's work. `_report`
  records it on the round (`on_round_error`) and continues; a refused lever's entry carries
  its finding id (it was `null` in the SSE event).
- **`passage-to-its-band` on a 4.5 x 5 passage wrote 5 x 6** — `_set_dims` sorts, so 6.0
  became the LENGTH — left the short side under its own band and logged *"widened to 6.0"*.
  The short side goes to 6 and the long side to `max(6, long)`; `length_ft` is in its
  `touches`, truthfully.
- **`move-window-off-the-needed-wall` popped `position_ft`/`positions_ft`/`unplaced` off the
  live record** — a move reaching into placement keys. It requires re-placement and the
  strip before it removes them; the pops are gone.
- **`give-the-room-a-window` half-wrote the record and then exited the interpreter** on a
  style that is not a node (`resolve_kit.chain_for` raises `SystemExit`) — reached through
  `answering()`'s dry run and, in a job, a dead worker thread. It derives before it commits
  and refuses with the style named.
- **The critique route passed `place` raw** where evaluate coerces `bool`; coerced.
  **`setRevising('queued')`** said *queued* on submit whether or not the pool was busy;
  *submitted, waiting for the worker* now — what the client can actually know.
- **`check_basis` never read the key path a citation names.** A real sentence cited under
  the wrong key passed (Auditor A: `critical_dimension:` → `note:`, green). It walks the path
  now — a kit's slots and their parameters included — requires the quote UNDER that key, and
  reports a path it cannot walk as unjudged rather than passed. All 30 grammar rules and 21
  moves cite the key they quote.
- **Two `core` module objects, two corpora, and `/api/dev/reload` invalidating one.**
  `modcache.load` hands back a `sys.modules` module whose file is the realpath asked for;
  `test_modcache.py` pins it and `mcp_mount.py`'s "one copy" claim is true again.
- **`test_mcp_http.py`'s METERED pin skipped whole without the SDK.** The literal lives in
  `metered_args.py` and `test_deploy_fixes_still_hold.py` pins it with no SDK. CI installs the
  SDK from `workbench/requirements.txt` — but CI runs on pushes to `main` only and never ran
  on this branch, so "red in CI" was never observed; the WP-9.3 report is corrected.
- **The `revised` SSE registration had no guard** — the shape of the bug WP-9.3 found, re-armed.
  `sse_handlers.test.mjs` reads `jobs.py` and both JSX call sites with `node:fs` and holds every
  event name the server can put against every `jobEvents(` site, `round` included.
- **`DecisionLogEntry.jsx`** deleted: zero importers, confirmed.
- **Four never-fired moves had no unit test** (`widen-wet-room-for-fixture`,
  `move-window-off-the-needed-wall`, `grow-to-band-floor`, `give-the-room-a-window`) though
  the WP-9.2 report said they had; they have now, and the sweep fired
  `give-the-room-a-window` for the first time once it stopped exiting.

## III — Tests that could not fail, made to bite

Each proved by an auditor applying the mutation and watching the suite stay green.

1. `test_moves.py::test_a_closet_needing_more_than_1_8x…` — `assert ("changed" in res) or
   ("refused" in res and res["refused"])`: every apply returns one of the two. It asserts the
   move applied to the unrounded need now.
2. `test_revise.py::test_a_move_that_opens_a_fatal_is_refused` and its siblings — replace
   `_improves` with `key[:2] <` and all three cases pass. `test_improves_reads_the_whole_key`
   adds minor-only, faults-only and better-key-new-fatal cases.
3. `test_revise.py::test_a_re_derive_move_keeps_the_placement_and_a_re_place_move_strips_it` —
   tested only the re-derive direction, and with ONE round, which was the refused proof: no
   declared move was ever applied and the "1 solve" was the initial critique. Two rounds, both
   directions, and an assertion that a declared move ran.
4. `test_compose_revision.py::test_score_and_score_before_are_one_instrument` — asserted an
   axis existed and a score was in range; `PC.check(placed)` in place of the stripped record
   passed. It re-scores the stripped returned plan and matches the counts now.
5. `test_revise.py::test_a_refused_pair_is_tabu…` — a three-way disjunction on the stop
   reason; one reason now, by whether the cap was reached.
6. `test_revision_routes.py::test_the_round_event_is_built_from_the_record…` — a source grep
   for `.pop(` and `del rnd`; Auditor C mutated the record's `moves` in place with the grep
   green. It compares the report's rounds to the queued events after a real job now.
7. `test_revision_routes.py`'s strip assertion checked three of the four strip tuples; a
   strip that forgot the doors passed (Auditor C: RED only in `test_openings.py`). All four now.
8. `test_parti_confinement.py` — every escape a string; the revise route absent.
9. `test_mcp_http.py` — green by absence. Pinned without the SDK.

And two guards credited, both RED under mutation as designed: the byte-identical rollback
(`snapshot = plan` in place of the deepcopy) and the basis quote (one word changed).

## IV — Numbers and sentences that were false or stale, corrected in place

Each correction is marked *(corrected by WP-9.4: …)* beside the sentence in its own report.

- wp-9.1: *TOTAL_CHECKS 43* (44); *the word "drawn" appears nowhere in the app* (WP-9.3 put it
  there); *"decided against the DECLARED record"* for every placement kind — true of four kinds
  and not of five, which are decided by what the record declares that the search did not
  realise; the docstring and the prose say so, and the question is raised as
  `oq/a-placement-finding-is-classed-by-what-the-engine-is-for-five-kinds`.
- wp-9.2: the `touches`-tested sentence; *"All four are pinned"* (the stale-list one was not);
  *"`search-harder` is never accepted on a key that improved only in `minor` — it cannot be, the
  key is lexicographic"* (backwards: lexicographic order PERMITS it and §IV showed it); *"taken
  BEFORE the placed loop and not after `repair`"* (necessarily after `repair`); *"the sweep's
  before and after are different objects"* (they were one); *"forgotten when the engine
  changes"* (on any lever); *"the moves have unit tests on fixtures that do"* (four had none);
  the sweep totals, the per-move table and the refusal rate, re-measured below.
- wp-9.3: *"the first two constructor arguments stay positional for the SSE test"* (that test
  uses keywords); *"the chip's promise and the walk's poll are the same number"* (nothing ties
  them); the "red in CI" claim.

## V — Measured

**The sweep, re-run on the search engine after the fixes** (21 partis + both shipped plans,
6 rounds, 250 candidates):

| | first published | re-measured |
|---|---|---|
| fatal | 135 -> 91 | 135 -> 93 |
| serious | 961 -> 749 | 961 -> 750 |
| minor | 1,157 -> 1,213 | 1,157 -> 1,212 |
| improved / same / worse | 20 / 3 / 0 | 20 / 3 / 0 |
| applications refused | 135 of 277 (48.7%) | 131 of 273 (48.0%) |
| `give-the-room-a-window` | applied 0, refused 1 | applied 1, cleared 1 |
| wall clock | 54 s | 68 s (the apply-time diff) |

The spec Colonial's row moved from `[6, 68, 64, 20]` to `[8, 69, 63, 19]` under the scoped
door move and the passage fix — a different, honest path through the same rule; still 0 worse.
(Re-measured a third time after §VIII's fixes: see the table there — the search asked for by
name no longer spends round 1 on a refused proof, and the successor moves fire.)

**Under CP-SAT, bounded** (four rounds, 200 s a plan, 25 s a proof; the two rows the first
run accepted unplaced are re-measured under the fixed rule):

| plan | before | after | rounds | applied | refused | stop | seconds |
|---|---|---|---|---|---|---|---|
| tidewater-georgian-careful | [0, 40, 65, 20] | [0, 37, 70, 18] | 2 | 2 | 3 | budget | 204 |
| spec-builder-colonial | [4, 64, 69, 22] | [2, 36, 76, 19] | 4 | 18 | 3 | round-cap | 201 |
| hall-and-parlor / american-farmhouse-vernacular | [5, 36, 55, 0] | [0, 11, 65, 0] | 4 | 24 | 0 | round-cap | 151 |
| cape-central-chimney / cape-cod-colonial | [2, 68, 57, 20] | [2, 53, 66, 20] | 4 | 9 | 1 | round-cap | 151 |
| ranch-tripartite / ranch-style | [0, 50, 66, 0] | [0, 24, 73, 0] | 4 | 14 | 1 | round-cap | 222 |

**8 of 75 applications refused under the proof, 10.7%**, every one by measurement and none by
a move — against 48.0% on the search. The Tidewater row's three refusals include rounds whose
proof timed out inside the budget and were refused as unjudged rather than accepted as lower;
its stop is the budget, at 204 s of a 200 s allowance (a proof in flight finishes). The
ranch's `before` reads `[0, 50, 66, 0]` here and `[0, 51, 65, 0]` in the first run: CP-SAT at a
time limit is not deterministic across runs, which the earlier sweep's determinism claim
(search engine only) never covered.

**All 164 styles through the declared critique** with the Tidewater record re-styled: 164
critiques, 0 exceptions; `actionable` and `architect` non-empty on every style; `placement`
empty on every style (declared mode, by construction); `critic_suspect` non-empty on 41.

**Suites:** root 1,371 collected (was 1,350); server 192 passed, 2 skipped (was 186 and 2); app 76 under `node --test` (was
73); the walk `E2E WALK GREEN` with three new checks in it (every classified row carries its class tag, 105 of 105; after the undo the critique says it is of an earlier evaluation; no row still wears a class from it); `check_all` reads GATE_LINE.

## VI — Deliberately not done

- **A full CP-SAT sweep.** Five plans, bounded, is what the report carries.
- **`_is_placement`'s five engine-name kinds** are documented and raised as a question, not
  changed: what the loop may touch is a ruling.
- **`check_basis` on a key path it cannot walk reports unjudged** rather than inventing a
  walk; today that is zero citations (corrected by §VIII: the count is ratcheted at zero in
  all three checkers now, and was printed above an OK line here).
- **The stale-critique guard in the bench is walked, not unit-tested** — it lives in JSX,
  outside the `node --test` graph.
- **The `_SOLVE_CACHE` 64-entry clear**: a 23-plan sweep crosses it, so "a rollback is a hit"
  is not guaranteed; a miss re-solves deterministically, so correctness holds and only the
  cost moves. The docstring is corrected; nothing else.

## VII — What this says about the discipline

Every one of the five blocking defects was something a report SAID was checked, pinned or
bounded. Four of the nine tests that could not fail were written by the same hand that wrote
the code they guarded, in the same commit, and passed on the first run — which is the
condition under which a test proves least. The audit's two instruments were the same as
WP-8.6's: revert the fix and watch the suite, and deep-diff the record around every move
rather than reading what the move said it did. Both found things in seconds that three
reports and 1,350 green tests had not.


## VIII — The audit of the audit (2 Sep 2026)

Before this session's work was called done, three more auditors read the WHOLE diff
(`f434fe8..2d9a87f`) with the same two instruments — revert and watch, deep-diff the record —
and a fourth re-ran the WP-9.4 verify pass. Everything below was reproduced before it was
fixed; each fix landed with the test named beside it. Introduced by this session unless marked
pre-existing.

### Blocked deployment (fixed)

| finding | auditor | fix | test that bites |
|---|---|---|---|
| `_paths_written` returned at a list whose length changed, so a move that ADDED a room hid every other write behind `levels[].rooms[]`; `split-per-grouping` was still re-deriving openings plan-wide under the guard built to catch exactly that (Library + Parlour with authored counts 7 and 9: the parlour's became 2 and 3) | A, D | the diff descends whatever the length did; the split move re-derives its two rooms and one pair | `test_split_per_grouping_leaves_the_parlours_authored_window_counts_alone` |
| the diff could not see a rewrite of an existing element in a list a move appended to; the Tidewater door test bit by fixture luck (the passage's authored doors lacked `type`) | B | index-diff of the common prefix; pre-existing doors asserted byte-identical | `test_the_diff_sees_a_rewrite_inside_a_list_the_move_appended_to`, the door test's new assertions |
| a revised plan could not be read back from its own DXF: `import_dxf` rebuilt the record with `revision_summary`, which the plan schema did not admit, so `check_plan` refused it | A | the schema admits `revision_summary`, never authored; a real round trip through ezdxf validates the record | `test_a_revised_plan_read_back_from_its_dxf_validates_against_the_plan_schema` |
| `tdl_revise_plan`, `tdl_critique_plan` and `tdl_compose` over `/mcp` passed rounds, candidates and no budget raw onto a synchronous threadpool token — one call with a thousand rounds on the proving engine held it for hours, inside the 60/hour meter | A, C | the bounds live in `core` (`REVISE_MAX_ROUNDS`, `MAX_CANDIDATES`, the budget's default and cap, `COMPOSE_MAX_CANDIDATES`), one spelling the routes read too; a clamped call says `bounded` | `test_core_bounds_every_knob_the_mcp_tools_pass` (also refuses a second spelling in `app.py`) |
| one `/api/compose` submission could hold the one-worker pool for ~4 hours: 21 candidates x (a 25 s proof + a 600 s loop + a 30 s reclaim), metered once | C | `revise_budget_s` is the SET's budget, spent in rank order; a candidate it does not reach is returned as composed with `revision_skipped` and a `REVISION SKIPPED:` decision line; the unbounded parts (first placement, one in-flight critique, the reclaim) are stated in the code | `test_the_revise_budget_is_the_sets_and_a_candidate_it_does_not_reach_says_so` |
| the reclaim after the loop compared fatals alone with no unjudged guard | D | `key[:2]` and `could_not_evaluate`, rolled back and said | `TestTheReclaimIsHeldToTheLoopsRule` |
| `critique()`'s own `could_not_evaluate` was proved only against a scripted critic | B | a test through the real modules with `GEO.solve` returning an error | `test_a_solver_error_through_the_real_critic_is_could_not_evaluate_and_stops_the_placed_loop` |
| the key-path check had no test and its unjudged state was dropped by two checkers | A, B | `UNJUDGED_CEILING = 0` in all three checkers, printed in the OK line, an error above it | `test_a_basis_under_a_wrong_but_walkable_key_errors_and_an_unwalkable_key_is_unjudged` |

### Worth fixing (fixed)

- **Two widen moves read `width_ft` raw** where `plan_check` judges the short side: a 16 x 9
  dining room needing 12 was refused as "already at its floor" by one and "widened from 16 to
  12.4" by the other while its short side grew to 16 (A). Both read the short side now.
- **`narrow-the-window` widened**: one figure onto every window, the bath's authored 2 ft to
  2.73 — squarer, the fault it answers (C). Only a window wider than the figure moves.
- **`drop-optional-room` was refused by the guard on every plan whose adjacencies named the
  room, and invented an empty list on every plan without the key** (A). It declares
  `adjacencies[]` and writes it only where a row named the room.
- **`setdefault("declared", {})` reported a bare `declared`**, refusing `delete-the-shutters`
  and `replace-forbidden-declared-variant` on any record without the key (A). An added dict
  is its leaves.
- **A record with two rooms of one id** made the id-keyed diff blind to the first (C). Ids
  are used only where unique.
- **`add-the-grammar-door` duplicated the door on an asymmetric record** (A). Both sides are
  checked before either is written.
- **`SystemExit` from `resolve_kit` escaped two of the three re-deriving moves** and the job
  worker catches `Exception` (A). One guard in `apply()`: any exception is a refusal naming
  itself, the record restored.
- **The three `_AFTER` moves were unreachable once their predecessor was tabu** (A). The loop
  hands its tabu set to `answering()` through `ctx`; a tabu move is not offered and its
  successor is.
- **Under `--revise-engine heuristic` — what `check_all` runs — every candidate's round 1 was
  `prove-it` refused** (A). `_lever` names `search-harder` behind an explicit search.
- **`critique_after["plan"]` was not the plan returned** after a refused final round or a
  rolled-back reclaim (A). The critique is re-pointed at the restored record, and the return
  asserts it.
- **`modcache._already_imported` handed back a module another thread was still executing**
  (A): `__spec__` is set before the body runs; `_initializing` is the flag. Realpaths are
  memoised per `__file__`.
- **`_run_revise` held the submitted record for the job's life and stored the report twice**;
  the pool's queue was unbounded and a reaped job still ran (C). The record is released to
  the loop, the report is one object, `MAX_QUEUED` bounds the queue (503 with `Retry-After`),
  and a reaped job is skipped.
- **A dropped SSE stream lost a minutes-long revise with no recovery** (C). The bench polls
  the job until it ends; a page refresh still abandons it, and the code says why.
- **The SSE-handler spec regexed string literals** and could not see an event named through a
  variable (B). `jobs.py` declares `COMPOSE_EVENTS`/`REVISE_EVENTS`, every put goes through
  `_put`, which refuses a name outside them, and the spec reads the tuples.
- **The critique route's parti refusal was unobservable** because core refuses too (B). A spy
  asserts core is never reached with a record.
- **`declared_fits` was unread for `stair-not-drawn` and nothing noticed** (B). A synthetic
  check reaches the branch.
- **`TestTheInstrumentOnTheRealFile` forbade the ratchet's own direction** by pinning an AST
  shape and `== 44` (B). Shapes are pinned on fixture strings; the real file is held to a
  frozen list of 44 names it may leave and never join; the ceilings may only fall.
- **Two vacuous assertions in `test_compose_revision.py` and a checker test that induced no
  breach** (B). Tightened; the breach is induced.
- **Twenty-five composer tests run with `revise=False` and nothing held the revised set** (B).
  Three invariant tests on the revised set: every plan validates, keeps the brief's
  `must_have` rooms and unique ids; the set is in the composer's order; `rank_before` is stated.
- **Pre-existing, found on the way: a composed plan for a brief naming `garage_bays` failed
  the plan schema** (`instantiate` copies the brief's context whole; the plan schema's
  context did not admit the key), so `tdl_check_plan` and the bench's revise route refused
  every such candidate. The schema admits it.
- The dead `or True` assertion, the `"12.3" in "112.3"` substring, the round-callback test
  that depended on the refused proof it no longer sees.

### Deferred, with the reason

- **Rounds are accepted on the key, not on the rule each move executed** (C): a leaf set to
  half an opening that a later move narrows. Raised as
  `oq/a-round-is-accepted-on-the-key-and-not-on-the-rule-each-move-executed`; the acceptance
  rule is a ruling.
- **`critique()` is quadratic in plan size through `answering()`'s deep copy per matching
  move per finding** — 90 s on an 800-room record (C). The route's body limit is 8 MB and
  `/api/plan/evaluate` has the same exposure through `geometry.solve` on the same body, so
  this is the pre-existing shape of every heavy route: the meter is the bound. Not changed;
  a room-count cap on the routes is a rule nobody has ruled.
- **The rate limiter's 60/hour x 20 identities/hour/address** (C) is the deployment's
  standing ceiling (OQ 36 and OQ 73 through OQ 77), not this phase's.
- **`RULE_KEYS` versus the runtime row, the grammar's `applies_to` integrity, the duplicated
  2.67 default** (D, 6g/6h): outside the phase's own diff.
- **Moves writing declared measurements** (D, 7b/7c): by ruling they execute the fault's own
  fix on a measurement the plan declared.
- **`setdefault` folds invisible to the instruments** (D, 7e/6c): what they fold is now
  visible to the diff (an added dict is its leaves); the instruments themselves are unchanged.
- **The `_DECISION_PATTERNS` door line splits a room name containing " and "**, the
  `IfExp` branch that can return a tuple, and the route docstring's "always" (A, minor):
  the docstring is corrected; the other two are latent on today's corpus and noted.
- **The dropped-stream recovery is not walked**: simulating a closed EventSource in the e2e
  walk needs a proxy the walk does not have. The code path is small and stated.

**The sweep, re-run a third time after these fixes** (search engine, 21 partis + both shipped
plans, 6 rounds, 250 candidates), against §V's re-measurement:

| | §V (after WP-9.4) | after §VIII |
|---|---|---|
| fatal | 135 -> 93 | 135 -> 83 |
| serious | 961 -> 750 | 961 -> 717 |
| minor | 1,157 -> 1,212 | 1,157 -> 1,231 |
| improved / same / worse | 20 / 3 / 0 | 20 / 3 / 0 |
| applications refused | 131 of 273 (48.0%) | 140 of 302 (46.4%) |
| `search-harder` | never fired | applied 3, cleared 3, refused 6 |
| `light-the-far-end` | never fired | applied 2, cleared 2, refused 4 |
| wall clock | 68 s | 88 s |

Two moves that had never fired on the search now do, for the two reasons §VIII names: the
analyst names `search-harder` behind an explicit search instead of a proof the lever would
refuse, and a successor move is offered once its predecessor is tabu. `prove-it` is in
`never_fired` by design on this engine. The spec Colonial's row is `[10, 70, 63, 21] -> [6,
67, 64, 20]`; the minor axis keeps paying for the other two, as every sweep has shown.

**Suites after the second pass:** root 1,403 collected (was 1,371); server 200 collected (was
194); app 78 under `node --test` (was 76); the walk and `check_all` re-run on the fixed tree,
the runner's own line read.

### What the second pass says

Every one of WP-9.4's blocking findings was something a report SAID was checked; three of
this pass's were things WP-9.4 SAID it had guarded, in the guard it built. A diff that stops
early is a guard that reports what it saw and not what happened, and the one test that seemed
to prove it bit by an accident of the fixture. The instrument that found all three in seconds
was the same again: a fixture built to disagree with the code's assumption, and the record
diffed around the move rather than read from the move's own account.
