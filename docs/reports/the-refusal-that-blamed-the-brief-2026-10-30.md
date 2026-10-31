# The refusal that blamed the brief — 30 October 2026

*Phase 17 (the candidates that can be drawn), after its audit. No WP number: the two Phase 17s share
17.0 through 17.9 and the Workbench line runs to 17.15, so a new number here would name two packages.
Cite this report by filename.*

## I. The complaint

Lucas composed his Tidewater brief (tidewater-georgian, 3,200 sf, four bedrooms, 3.5 baths) and read
six cards. The first two, the native five-part Palladian and a borrowed octagon, were **refused** with
**fatal 0**. The other four were **placed** with **fatal 1** and DISQUALIFIED. The refusal panel listed
three "hard facts of the type not held" and ended *"The brief or the parti is what changes."* He could
not tell what a refusal is against a fatal, why the refused houses led, or why an open-ended brief had
knocked out the best-scoring native diagram for reasons that read as the generator's inflexibility.

## II. What the two words mean

They are two tests on two different things, and neither implies the other.

- **A fatal is a finding** of the critic (`plan_check`): a fault from the corpus that fires on the drawn
  plan. It is about whether the house is good by the tradition.
- **A refusal is a verdict on the placement** (`typefacts.judge`, ruled 15 Sep 2026): the arrangement
  broke a physical fact of the type, so nothing is drawn. On his card: an upstairs bearing wall at
  x = 36 ft with no wall under it; the landing 0% over its stair and the upper passage 0% over the lower;
  107.5 sf of floor in eight strips belonging to no room.

"Refused, fatal 0" means the rooms connect and pass the rules but that arrangement cannot stand.
"Placed, fatal 1" means it can be drawn and one rule fires.

## III. What was wrong

1. **The order.** `compose.rank_key` put judged fatals first (the 16 Oct key, ruling 7 of 29 Oct), so
   0 < 1 put two houses nobody could open above four that could be.
2. **The refusal blamed his input.** Every refusal ended "the brief or the parti is what changes".
   `build/drawability.py` had classified every release since WP-17.0 — PROVEN, UNDECIDED (the budget
   ran out), MISMATCH (the model and the gate disagree), SEARCH (the fallback hill-climb, told none of
   the facts, drew it) — and its own docstring says three of the four are "the instrument's, not the
   house's". No surface printed the class. WP-17.0's own draw on his brief records the five-part as
   "refused: bearing, stacks (search, after CP UNKNOWN)".
3. **The bearing sentence mixed what decides with what is reported.** "2 clear span(s) exceed the
   capacity" sat in the refusal although capacity has not refused since 16 Sep.
4. **A disqualified card never said which fatal.** "1 fatal finding" with no name.

## IV. The rulings (Lucas, 30 October 2026)

Put as two direct questions; the answers arrived the same session. The questions and the answers are
two acts.

- **Asked:** how should the set be ordered, given two refused houses with no fatal leading four
  drawable ones with one? **Answered: drawable first.** The standing is the first key.
- **Asked:** when a refusal is not proven, what should he be able to do about it? **Answered: the
  composer retries automatically.**

## V. What was built

- **`compose.rank_key`** is `(standing, judged fatals, unjudged fatals, score, demerits, parti)`.
  Within one standing the 16 Oct order holds. `tests/fixtures/candidate_rank.json` reverses its
  fatals-first case and adds a middle-tier case; `candidateOrder.js::order()` applies the standing
  before the disqualification under all three orderings. `how_to_read_this`, `tdl_compose`'s
  description, `docs/compose.md`, the Candidate Set's intro and the `surface-candidates` record say
  the new order.
- **The refusal's class is on the one verdict.** `typefacts.refusal_class` (moved from
  `drawability._class_of`, which delegates) writes `classes`, `class` and `proven` onto every
  refusal. `overall_class` calls a refusal PROVEN only where every downgraded fact is proven or the
  record carries a proven infeasibility.
- **Only a proven refusal says the brief must change.** The conflict panel and the revision panel read
  the class through five new glossary records (`refusal-proven`, `refusal-undecided`,
  `refusal-search`, `refusal-mismatch`, `refusal-class-unstated`); the MCP tool and the server's 422
  read `typefacts.class_sentence`. A refusal that states no class is never read as proven.
  `judgment-refused` and `severity-fatal` now name each other as confusable and say the difference.
- **The capacity half of the bearing sentence says it does not refuse.**
- **Every judged fatal is on the card** (`compose.fatal_findings`, uncapped), and the DISQUALIFIED band
  lists them.
- **The composer retries an unproven native refusal** (`compose.retry_decision`, wired into the placed
  loop). UNDECIDED or SEARCH on a native diagram, with the prover not refused by name: placed once more
  at `RETRY_LIMIT_MULTIPLE` (2.0) × the compose budget, bounded by what is left of the set's budget,
  and adopted only where the second placement is not refused. Every branch is said in the decision log
  and on `card.retry`. The multiple is a judgment, not a measurement: the solve cache keys on the
  limit, so a retry at the same limit would return the refused placement unchanged.

## VI. What was measured

One compose of his brief on this tree, production defaults, a four-core box with nothing else
running, **601 s** (WP-17.0's draw on the code before this was 409 s; the two retries below are most of
the difference). CP under a wall clock is a draw, not a figure.

| order | diagram | nativity | standing | fatals (named) | refusal class | retry | `drawability` |
|---|---|---|---|---|---|---|---|
| 1 | living-hall-picturesque | borrowed | placed | 0 | — | — | NOT DRAWABLE (rooms over band) |
| 2 | centre-passage-double-pile | native | placed | 1: *The Front With No Centre: 1 against between 3 and 7* | — | — | drawable where judged |
| 3 | centre-passage-single-pile | native | placed | 1: *The Truss Default: 0.4036 against at-least 0.45* | first: SEARCH | **retried at 120 s, placed (120.7 s)** | drawable where judged |
| 4 | courtyard-and-portal | borrowed | placed | 1: *The cornice that is only a fascia* | — | — | NOT DRAWABLE |
| 5 | five-part-palladian | native | refused: bearing, stacks | 0 | SEARCH | retried at 120 s, refused again (SEARCH) | not drawable |
| 6 | octagon-radial | borrowed | refused: bearing, stacks | 0 | **PROVEN** | not retried (borrowed) | not drawable |

What it shows:

- **The five-part's refusal was the placer's, twice.** SEARCH on both attempts: the prover did not
  answer at 60 s or at 120 s, and both times the hill-climb drew the layout that failed. Its card now
  says *not proven: placed by the search* where it said *the brief or the parti is what changes*. It
  is not evidence that the five-part cannot be drawn on this brief.
- **The retry drew a house.** The native single pile was refused on its first placement (SEARCH) and
  placed on the second; without the retry it would have stood refused at the foot of the set.
- **The octagon's refusal is proven**, so it is the one card that still says the brief or the parti
  must change. It is borrowed, so it was not retried in any case.
- **"Placed" is not "drawable".** The new first key is the standing, which is *not refused*. The
  leader, living-hall-picturesque, is placed and has no fatal, and `drawability.assess` still reads it
  NOT DRAWABLE for rooms past their band. That is the R10 distinction ("not refused" beside
  "drawable where judged", never one count); the ruling is executed on the standing, as asked, and the
  gap is said here rather than closed by a third tier nobody ruled.

## VII. What was deliberately not done

- **The assistant is not told the class.** The client sends the rail `last_eval.refused = {kind,
  facts}`; widening that is a client change and is left.
- **No new WP number** (see the head of this report).
- **The retry multiple is not tuned.** The plan asked for draws at 1×, 1.5× and 2×; one compose of his
  brief takes several minutes and CP under a wall clock is a draw, so the sweep is left to a quiet box.
- **A refused card stays unopenable** (WP-13.4 and the 16 Oct ruling); the retry is the recourse ruled.

## VIII. Tests

`tests/test_refusal_class.py` (14) and `tests/test_refusal_retry.py` (11) are new; four rank tests were
re-cut to the new order. The app suite gained six (`refusal.test.mjs` four, `candidateOrder.test.mjs`
two). Eight mutations of the new guards, each asserted landed, all red.

## IX. The whole build

`python3 build/check_all.py` on the final tree: **`2 of 54 checks failed`**, the suite and
`check_partis.py`, with 23 failing tests, every one attributed by id.

- **20 are the known list**: the 18 `tests/test_sheet_coherence.py` gate rows, `test_solver`'s half
  bound and `test_parti_composability`.
- **3 are not on that list and are not this change's**:
  `test_composition.py::TestSolveIntegration::test_service_rooms_land_toward_the_rear` and two in
  `tests/test_scene_entrance.py` (the flight's treads, and the checker and plate agreeing on the front
  door's bay). Run alone on a clean `git worktree` of the base `d9231d7`, all three fail the same way.
  They are older than this report; the known list in CLAUDE.md does not name them, which is a gap in
  that list and is said here rather than fixed.
- The two CAD selftests are could-not-evaluate (no `ezdxf`/`ifcopenshell` here), as named.
- The app suite is 898 of 898; the test count is reconciled in §VIII and CLAUDE.md.
