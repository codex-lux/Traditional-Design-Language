# The critique and the corrective revisions (Phase 9)

*A critic that reads the drawn house, an analyst that says what each finding means, and a
generator that revises the record until the critic stops finding things it can fix — every
move named with its basis, every refusal stated, the judgment calls handed to the architect.*

```
python3 build/critique.py plans/tidewater-georgian-careful.json --engine auto      # the analyst
python3 build/revise.py   plans/tidewater-georgian-careful.json --engine auto      # the loop
python3 build/revise.py   --sweep --engine heuristic                              # the corpus
python3 build/compose.py  briefs/family-georgian.json [--no-revise]               # the composer, revising by default
```

## Why

Lucas asked for recursive self-improvement: once a plan is drawn, a critic assesses the layout,
points out every issue, and the generator fixes them in plan and elevation, so the final product
is the result of many corrective revisions rather than one procedural pass. The pipeline was
strictly forward. The only backward edge was `compose.repair`, forty lines that read the
findings' prose and applied three moves before scoring, with no rollback. Nothing ever judged
the drawn house and then changed the record.

## The three pieces

**The critic is unchanged in kind and changed in two facts (WP-9.1).** `plan_check.check` judges
ONE building now: when the record carries a placement, the section, the roof and the elevation
are derived from that placement (until WP-9.1 the fault layer solved a fresh heuristic placement
inside the critic while the drawn layer read the carried one). And every finding carries the
structured evidence a move needs beside its sentence — `kind`, `need_ft`, `have_ft`, `slot`,
`canonical`, `expression`, `source`, the drawn layer's `engine` — never instead of it, and never
in the id. `docs/plans.md` has the field table.

**The analyst (`build/critique.py`).** Places once, or reuses the placement the record carries,
judges the placed house, and sorts every non-info finding into exactly one class, first match
wins:

| class | meaning | what carries it |
|---|---|---|
| `advisory` | the code layer, advisory and jurisdictional by ruling | — |
| `placement` | the DECLARED record would have satisfied the need; the engine did not | the lever: `prove-it`, `search-harder`, or the CP conflict set |
| `critic_suspect` | the failing test reads a figure the elevation GENERATOR states as its own constant | the instrument, the value and the line (`build/critic_suspects.py`) |
| `actionable` | a registered move answers it and its precondition holds on this record | the move, its basis, the line it would write |
| `architect` | everything else — topology, a judgment slot, a fault whose fix is words | the fault's own `right` fix, or the rule's own `why` |

`placement` is decided against the declared record BEFORE anything else — a stair the declared
hall would have held is the engine's, a passage declared at 6 ft and drawn at 4 is the
engine's — and a proved placement with no conflict named goes to the architect with the proof's
account of itself. `info` findings are listed as could-not-evaluate and are never a class. The
result's `key` is `[fatal, serious, minor, faults present]`.

**The moves (`moves/registry.json`, `build/moves.py`).** Each is a corpus rule made executable
against the RECORD — a room's own band, a fault's own `right` or `cheap` fix, the opening
grammar's own pair rule — and each quotes the sentence it executes; `build/check_moves.py`
verifies every quotation against the record it names with the grammar's own verifier, holds
every `touches` path to a closed allow-list that admits no placement key, and holds the data
and the code to each other. A move edits declared fields only; after a move that changes the
plan the placement is stripped (`openings.strip_placement`, the exporter's own list) and
re-solved, so the drawing stays a render of the data. Twenty-one moves and nine stated
refusals; the registry's `authority` block records the ruling of 1 Sep 2026 — dimensions,
declared choices, openings and rooms; never a room the parti has no place for, a judgment slot,
geometry, a critic-suspect, a measurement the record did not declare.

**The loop (`build/revise.py`).** Per round: critique; pick one move per room, severity first;
apply; strip and re-place if any move needs it, else keep the placement and re-derive;
critique again. **Accept only if the key strictly decreases and no new fatal appears.**
Otherwise roll the round back byte-identically, retry each move alone in severity order so a
good move is not lost to a bad neighbour, mark what was refused tabu, and continue. Where the
proof is to be had it is asked for before any declared move — on the search engine a declared
move is judged against re-placement noise and refused, which the first run of this loop
measured — and the tabu earned under one engine is forgotten when the engine changes. A lever
is otherwise tried only when no declared move is left, alone, and through the same acceptance
rule. Stops on: no applicable move, the round cap, the budget (the accepted state is kept), a
declared record seen before, or nothing left but what belongs to the engine, the critic's own
defects, or the architect. The report — every round with its attribution from the stable
finding ids, what remains by class, what was handed to the architect, what was refused and why
— rides on the plan as `revision_report` (schema 0.4.0) and, in a DXF, as `revision_summary`
only (XDATA is capped near 16 KB).

## Where it runs

- **The composer**, twice. `repair()` is the DECLARED loop now (`place=False`) in its old
  position, every pick, before scoring. The PLACED loop then runs on the RETURNED candidates
  after ranking, by default; each is re-scored on its declared record so `score` and
  `score_before` are one instrument, and re-ranked. `--no-revise`, `--revise-rounds`,
  `--revise-engine`, `--revise-budget-s`; `check_all` runs the composer on the fast engine.
- **MCP**: `tdl_critique_plan`, `tdl_revise_plan`; `tdl_compose(revise=...)`.
- **The bench** (WP-9.3): the compose job streams a `revised` event per candidate and the
  Candidate Set shows it — the score before beside the score after, the drawn keys, and the
  server's rank before revision said in words. The Plan Workbench's evaluate judges the solved
  record (the drawn layer runs on every evaluate, and each drawn finding row carries the
  engine that placed it). Three acts in the solver fold: **critique** asks the analyst once
  (`POST /api/plan/critique`) and tags every finding row with its class — a move answers
  it, the engine's, the critic's own, the architect's — and drops the tags the moment a later
  evaluation lands, because a class that labelled a finding of an earlier house is a verdict
  about a house no longer on the sheet; **revise (search)** and **revise (proof)** submit the
  loop as a job (`POST /api/plan/revise`), show each round as it lands, and on `done` load
  the revised record as ONE undo step. The record comes back with its placement stripped and
  the bench re-solves it as it does every load; the Revision panel says that the sheet is a
  fresh solve and names the engine the loop's own key was measured on, because the two can
  differ. The panel is the record's own `revision_report`: undo takes it away. A suspect in
  the panel is styled as neither verdict.

## What it will not do, stated

It will not call a plan good — a lower key is a plan with fewer things the corpus can name
wrong. It will not act on a finding the critic invented: a fault reading one of the 35
literals `build/elevation.py` states (`oq/thirty-five-measurements-the-elevation-states-as-literals`)
is marked and left. It will not accept a drawn size into the declaration, add a room the parti
has no place for, fill a judgment slot, or write a measurement the record did not declare. And
it will not hide what it could not do: `handed_to_architect` and `suspects` are as much the
result as `rounds`.

## Reports

`docs/reports/wp-9.1-the-critique.md` (the analyst, the evidence contract, the one-building
fix, the suspects) and WP-9.2's report (the registry, the loop, the measured movement).
