# WP-9.3 — The revision surfaces: the analyst and the loop reach the bench, and three things the first two packages shipped

*Phase 9, package 3 of 4. 2 September 2026. WP-9.1 built the critic's judgment, WP-9.2 the
loop that acts on it, and both reached the MCP and the CLI. This package puts them where a
person edits a plan.*

## What this package is

A person in the Plan Workbench can now ask two questions the corpus could already answer
for an agent and not for them: *what does this finding mean* — a move answers it, or it is
the engine's, or the critic's own invention, or the architect's — and *revise this record*.
The Candidate Set shows what the composer's default revision bought on each candidate, which
it had been told since WP-9.2 and had not been listening to.

Three routes, one job kind, one pure adapter, one panel, two tags on every finding row, a
band on every candidate, and the walk that clicks through all of it.

## I — The server

- **`POST /api/plan/critique`** (synchronous, metered, the exact shape of the evaluate
  route): delegates to `core.critique_plan`; the response carries the assessment by class
  with finding ids, the class counts, the key, and the engine that RAN. Not run per edit on
  purpose — evaluate is this server's bound (the infrastructure audit measured one editor
  at 85% of capacity) — so a classification is asked for, like a proof.
- **`POST /api/plan/revise`**: a job on the existing one-worker pool. `Job` gained a `kind`
  (`compose` | `revise`) and a `plan`; the first two constructor arguments keep their order *(corrected by WP-9.4: the SSE test this cited builds a `Job` with keyword arguments, so nothing enforces the order)*
  for the SSE test that builds one by hand. `_run` dispatches; `_run_revise` calls
  `core.revise_plan(..., on_round=cb)` — the seam that did not exist: `revise()` accepted
  `on_round` and `core.revise_plan` did not forward it. Each `round` event is a NEW dict
  built from the round record (`n`, the engine, accepted, both keys, the moves as
  `{move, finding, cleared, refused?}`, `opened_n`) — never the record, which `revise()` has
  already appended to the report it will return, and never the move logs.
- **`_strip_plans` is one rule now**: any top-level `plan` and any candidate `plan` is popped
  and replaced by `plan_rooms`, in the poll, the `done` event and the late-attach synthesis
  alike. The record travels once, through its own route.
- **`GET /api/jobs/{id}/plan`** returns a done revise job's record with its placement
  STRIPPED (`openings.strip_placement`, the one spelling) and its `revision_report` kept.
  Stripped because `evaluate.py` always re-solves what it is handed and a carried placement
  would lie the moment a wall was dragged. So the bench re-solves the revised declared
  record on `auto` as it does for every load, and the panel says so — and names the engine
  the loop's own key was measured on, because the two can differ.
- No new SSE route (the pin stays at 2; `GZipExceptSSE` already matches `/api/jobs/*/events`);
  the compression table gains the `/plan` path so a job's record is never mistaken for its
  stream; `test_parti_confinement.py`'s endpoint list gains the critique route, which
  reaches `core.load_parti` through `critique.py`.

## II — The app

- **`revision.js`**, React-free, beside `candidateOrder.js`: `engineLabel` (the engine that
  RAN — `auto` is a request, and a label that stored it would call a search a proof),
  `classTag`, `classesById`, `keyDelta` (only the axes that moved; equal keys read
  *unchanged*, never an arrow between two equal numbers), `roundLine` (a round with no move
  says so; nothing renders *undefined*), `adaptRevision`, `revisedLine` (null where the
  compose ran `--no-revise`; *nothing moved* rather than *was X* against the same X),
  `revisedEventLine`. Eleven tests in `revision.test.mjs`, each named for the sentence it
  forbids; `no_bare_imports.test.mjs` walks to it. The app suite reads **73** under
  `node --test` (was 62).
- **`RevisionPanel.jsx`**: the key before and after, the engine, why it stopped; the rounds,
  each move as what it did, which finding it answered (a button that opens the row) and on
  what basis, in the receipt face the decision log uses; a rolled-back round in brick; what
  remains by class; the architect's list with the fault's own right and cheap fixes; the
  suspects styled as **neither verdict**; the refusals folded. While a job runs the panel
  shows the rounds as they land. It reads `plan.revision_report`, so undo takes it away.
  Written in JSX where most of `components/` is compiled `React.createElement`.
- **`PlanWorkbench.jsx`**: three chips in the solver fold beside *prove placement* —
  **critique** (`auto`, the sheet's own candidate count), **revise (search)** (rounds 6,
  60 s) and **revise (proof)** (rounds 4, 120 s), so the chip's promise and the walk's poll
  are the same number *(corrected by WP-9.4: nothing ties them; the walk polls 90 s against a 60 s chip)*. A stored critique is keyed to the evaluation it was taken against:
  when a later evaluation lands the tags are dropped and the strip says *run it again*,
  because a class that labelled a finding of an earlier house is a verdict about a house no
  longer on the sheet. The class counts are display only — a clickable class filter would be
  per-surface filter state, which lives in the URL or not at all. On `done` the revised
  record is fetched and loaded through `planDoc.load` — one undo step — **unless the record
  changed while the loop ran**, in which case the revision is not applied and the caption
  says so. Every drawn finding row carries the engine that placed it; every row carries its
  class once a critique has run. A revise error lands on the caption line with `evalError`,
  never swallowed; a job queued behind a running compose says so.
- **`CandidateSet.jsx` / `CandidateColumn.jsx`**: `score_before`, `counts_before`,
  `rank_before`, the drawn keys and `revision` are adapted; the score block shows the
  `revisedLine` under the number and says *the server ranked it N before revision* in words,
  because `rank` on that surface is a position in the CURRENT order and a bare number would be
  read as one. The `revision` decision kind has a tone. Both SSE call sites register the
  `revised` event and the progress strip renders it as a sentence.

## III — Found

Three things the first two packages shipped, each visible only from this side.

1. **The loop reported two of its four rounds.** `revise()` fires `on_round` on the lever
   path and the applied path; the refused-lever path and the nothing-applied path appended
   the round to the log and did not report it. The first revise job on the spec Colonial —
   whose only round on an explicit search was a refused proof — emitted no `round` event at
   all while its report said one round. One reporter now (`_report`), so a fifth path cannot
   skip it; `tests/test_revise.py::TestTheRoundCallback` counts callbacks against the log.
2. **The `revised` event was dropped on the floor from the day it was added.** `jobEvents`
   subscribes only to the names it is handed, and both call sites registered `stage`,
   `candidate`, `done`, `error`. Every revision the composer reported to the bench since
   WP-9.2 was discarded by the browser; had one reached the progress strip it would have read
   *tried undefined*.
3. **A pin that was red wherever the thing it pinned exists.** `test_mcp_http.py` holds
   `mcp_mount.METERED` against a literal of three tools; WP-9.2 took the set to five and did
   not touch the literal. Green here only because the file skips at import without the MCP
   SDK, which was not installed — installed now, and the file's 33 tests run and pass *(WP-9.4: CI installs the SDK, so the pin would have been red there — but CI runs on pushes to `main` only and never ran on this branch; the literal lives in `metered_args.py` now and is pinned without the SDK)*. A pin
   that skips where its subject is absent fires only for someone else.

4. **Two `core` objects in one server.** `workbench/server/corpus.py` imports `core` from
   `sys.path`; `build/critique.py` and `build/revise.py` load the same file through
   `modcache` by path, which is a second module instance — and a second `_data()` corpus
   in memory the first time the analyst runs, against `mcp_mount.py`'s claim of one copy.
   Found because `test_parti_confinement.py`'s spy on the server's `core.load_parti` never
   saw the critique route call it: the confined loader IS what critique calls, on the other
   instance. The test spies on both now and says why. Whether `modcache` should hand back
   an already-imported module of the same realpath is the audit's question, not this
   package's change.

And one thing the plan for this package had wrong, caught by the plan review before a line
was written: `DecisionLogEntry.jsx` is dead code — nothing imports it — and the real
`decisions_structured` renderer is an inline block in `CandidateSet.jsx`. The `revision`
kind went there. The dead file is left for WP-9.4.

## IV — Measured

| | |
|---|---|
| server suite | 186 passed, 2 skipped with the SDK installed (was 147 passed, 8 skipped) |
| app suite | 73 (was 62) |
| root suite | 1,350 collected (one test added) |
| the walk | `E2E WALK GREEN`, exit 0, with the eight new checks in it: the fold's three chips; the critique names every class; **the class counts sum to the findings the sheet shows (105 of 105)** — two routes, one placement through the solve cache; **every drawn finding carries the engine that placed it (15 of 15)**; the panel names why the loop stopped and its round count; the fresh-solve sentence; undo taking the panel away |

## V — Deliberately not done

- **A per-edit critique.** Evaluate stays at its measured cost.
- **Evaluate learning to reuse a carried placement.** The revised record is handed back
  stripped and re-solved, and the panel states that the sheet is a fresh solve. A carried
  placement under a draggable wall is a lie waiting for a gesture.
- **A third SSE route.** Rounds ride the existing job stream.
- **The move logs in the `round` event.** The report carries them; the event is a summary.
- **A clickable class filter.** Filters live in the URL.
- **Deleting `DecisionLogEntry.jsx`.** Named dead here; the audit decides.
