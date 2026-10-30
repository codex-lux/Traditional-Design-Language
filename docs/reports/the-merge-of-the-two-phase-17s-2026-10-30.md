# The merge of the two Phase 17s (30 Oct 2026)

*Status: merged. `origin/main` at `d5773cf` (PR #43, the Workbench redrawn as a dark instrument with
vellum plates) into `claude/quirky-babbage-oh3zzd` at `1e3c210` (the candidates that can be drawn),
as a merge commit. Base `6fcc665`.*

## I. Two Phase 17s, neither renumbered

Two sessions opened a Phase 17 from the same base on 29 Oct 2026:

- *The candidates that can be drawn* (this branch): WP-17.0 through 17.9, report
  `docs/reports/wp-17.0-the-house-the-card-describes.md`.
- *The Workbench, redrawn* (main): WP-17.0 through 17.15, reports from
  `docs/reports/wp-17.0-two-grounds-not-a-theme.md` to
  `docs/reports/wp-17.15-the-audit-of-phase-17.md`.

So WP-17.0 through 17.9 each name two packages. This follows the two Phase 9s, 11s and 14s:

- neither line is renumbered;
- pushed commit subjects on both sides carry the numbers;
- both board rows and both `## Phase 17 —` sections stand in `PLAN-OF-ACTION.md`;
- a report is cited by FILENAME.

No report filename collides, so nothing was renamed.

## II. What conflicted, and how each was resolved

Six files conflicted. Main's spelling survived wherever both lines built the same thing.

| File | Conflict | Resolution |
|---|---|---|
| `workbench/server/corpus.py` | `invalidate()`: this branch added `forget_recent_placements()` (the Drawing Set's ten-minute recent map), and main added `reset_front_door()` (the hero plate and the first-drawable memo) on the same line | **Both calls kept.** They clear different caches, and dropping either would let a reload hand a pre-edit answer to the next reader. |
| `CLAUDE.md` | "Where the work stands": two Phase 17 entries | **Both kept**, this line's first. A heading says there are two. |
| `CLAUDE.md` | The two-OQ parenthesis under the candidate-click entry | **Combined.** The composer OQ was closed by this line's pool-fill, and the journey-bar OQ by main's spine. |
| `CLAUDE.md` | Search index count, open-question tally and list | **Re-derived** on the merged tree (§III). |
| `PLAN-OF-ACTION.md` | The board row and the Phase 17 section | **Both rows and both sections kept**, this line's first. |
| `docs/open-questions.md` | The generated tally | **Regenerated** by `build/gen_open_questions.py`. |
| `docs/workbench.md`, `workbench/README.md` | The search index count and bytes | **Re-measured** (§III). |

## III. Every figure is a third value

None of these figures belongs to either parent.

- **Search index: 929 entries and 296,827 bytes.** Measured by Starlette's own JSON encoding of
  `corpus.search_index()`. That is main's 924 plus this line's five glossary records.
  - Neither parent's pair was this tree's.
  - Main had moved the COUNT to 924 and left beside it the 283,092 bytes measured on 26 Sep at an
    older count. That is the one-number-of-a-pair shape `docs/workbench.md` already records about
    `check_counts.py --fix`.
- **Open questions: 288 entries, 161 open.** This line had 288 and 162, and main 284 and 158.
  - Main closed `oq/the-journey-bars-next-jumps-rows-when-the-strip-wraps` by retiring the bar.
  - This line raised four questions and closed `oq/the-composer-returns-sets-in-which-nothing-may-be-drawn`.
  - So 162 - 1 = 158 + 4 - 1 = 161.
- **Python `tests/`: 4,189.** Reconciled by name: this line's 4,188 plus main's one new
  `test_chronology_parity`. The three base ids that main carries and the merge does not are tests this
  line re-cut away: the allowance test ruling 4 retired, and the two Tidewater W cases moved to the
  spec Colonial's W face.
- **App suite: 892, all passing.** That is the base's 816, plus 11 from this line and 65 from main.
  The eight base app tests absent from the merge are ones main removed with the journey bar and the
  old front-door map.
- **Server suite: 521.** That is the base's 467, plus 35 from this line and 19 from main. The merged
  ids equal the union of both parents' ids exactly.

## IV. The one defect the merge made: a word in a pigment

The text merge was clean everywhere outside the six files. The app suite was not: **3 reds in
`grounds.test.mjs`, all one line.**

- This line added the pool-fill's passed-over paragraph to `surfaces/CandidateSet.jsx` with
  `color: 'var(--ink-2)'`.
- Main's register retired every word set in a primitive and moved them onto duties that follow
  their ground (`--text-secondary` here).
- Main's guards caught the one line written before that rule existed on this branch.

Ported to `--text-secondary`, main's spelling. The paragraph's two border marks (`--refusal`,
`--judge-unjudged`) are marks, and the guards pass them. **A line written before a rule existed is
the rule's first customer at a merge.** Only the other side's suite could see it, which is why a
merge runs both.

## V. Checked and left

- **`corpus.first_drawable` reads the verdict, not a list.** Main's front door sweeps the shipped
  plans for the first record `_placed` does not refuse. This line's whole-run bearing rule
  (ruling 8) newly refuses `good-05`, which is fifth in the hero order. The hero takes whichever
  record the merged verdict draws, so nothing is pinned to a name.
- **Two glossary records may describe one state.** Main's `candidate-placed` and this line's
  `placed-and-not-refused` sit on one surface. Both are kept, because ids are stable, and
  `check_glossary.py` passes over both.
  - Whether they mean one thing is a reading left for the next package that touches the card.
  - Deleting either inside a merge would be choosing a side under a merge's name.

## VI. Verification

- **Prose checks:** `check_counts.py` (0 stale), `check_citations.py` (0 dangling), `check_ids.py`
  and `check_glossary.py`, all green on the merged tree.
- **App suite:** 892 of 892.
- **Targeted Python:** the register-derived OQ list, the counts guard, drawability, chronology
  parity and determinism, 340 passed.
- **The server suite and the whole sharded build** are recorded in the merge commit's message,
  attributed by id against both parents' known reds.
