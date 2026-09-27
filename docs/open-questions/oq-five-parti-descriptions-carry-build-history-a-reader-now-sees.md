# oq/five-parti-descriptions-carry-build-history-a-reader-now-sees — a record's own prose names work packages and code, and the record page shows it

*Status: CLOSED — ruled 26 September 2026 (descriptions are for readers), executed in WP-14.33 · Raised in: WP-14.32 (26 September 2026)*

**The finding.** WP-14.23 gave every parti a record page (`#/parti/<id>`). The page prints the
record's own `description`, and five of the 21 parti descriptions carry build history: a
work-package number, or a code span naming a field or a function.

- `centre-passage-double-pile` is the example met while looking at the page. Its description says
  *"WP-13.5 states the container the description always implied: the kitchen, pantry, breakfast
  room and powder room carry `block: service` … so `geometry.blocks_for` lays the service programme
  into a dependency"*.
- The other four are `courtyard-and-portal`, `great-hall-h-plan`, `living-hall-picturesque` and
  `tower-villa`.
- Measured with a crude pattern (`WP-\d`, `OQ \d`, a backticked `a.b` or `a:`): 5 of 21 partis,
  0 of 17 groupings, 0 of 60 rooms, 0 of 40 massings.

**Why it is a question and not an edit.** WP-14.31 made build history in the APP's reader copy a
failure. That was right because the app writes that copy. A record's `description` is corpus
prose. The history in it is also the record's own account of why its rooms are tagged the way
they are, and a later reader of the data may need exactly that. Moving it out is an authorial
decision about what a record's description is for.

## What each answer would change

1. **Descriptions are for readers.** The history moves to a `note` (or to the report it came
   from), and a check refuses build history in a record's `description`. The descriptions are
   rewritten by hand; they can be generated from nothing.
2. **Descriptions are for both, and the page chooses.** The record page shows the description up
   to the first sentence carrying history. That is a heuristic over prose, and it is the kind of
   reader this corpus refuses.
3. **Leave it.** The page shows the record as the record is.

## Meanwhile

Answer 3: the page prints the record whole.

## Ruled 26 September 2026: a description is for a reader

Lucas ruled that a record's description is for a reader. Its build history moves to a `note`, and a
check refuses a work-package number or a code span in a description.

**Executed in WP-14.33**:

- **Parti schema 0.1.0 → 0.2.0.** A parti gains an optional `note`: build history and
  reconciliation, for maintainers, which the record page does not show.
- **The five partis each moved their history sentence into `note` word for word.** The citations
  it made moved with it, so `check_citations.py` still reads OQ 45. Each description gained one
  sentence in a reader's terms in its place:
  - `centre-passage-double-pile` now says where the service rooms stand and what the main block
    carries.
  - The other four now say what their stated area range is.
  - The type's true size ("runs to 12,000 sf") stays in the description. It is a fact about the
    type, not about the record's history.
- **`build/validate.py` sweeps every description a record page shows**: 466 of them, across 21
  partis, 17 groupings, 60 rooms, 40 massings and 164 style nodes, the short and long text of each
  style counted separately. It refuses a work-package number, an open-question number or slug, and
  any backticked span. It runs inside that checker, so `TOTAL_CHECKS` does not move.
- **The first draft of the code-span rule was too narrow.** It refused only a span holding `.`,
  `:`, `=` or `(`. A mutation putting `area_range_sf` in backticks into a description passed it.
  The page prints plain text, so a reader sees the backticks whatever the span holds.
  - Widened, the rule caught two more descriptions: `groupings/garage-and-hyphen.json` and
    `styles/eclectic-revivals.json`. Both were reworded in a reader's words. The second rewording
    moves `dist/taxonomy.json`.
- **`tests/test_description_history.py` lifts both functions by AST.** It also guards the
  module-level join, because a mutation setting the flag to 0 left every driven test green.
  Five mutations were run and all five go red. Two of them were blind on their first run: the
  backticked identifier and the flag set to 0.

**What the check does not refuse.** A bare file path or slot id in prose, such as the garage
grouping's *"docs/inheritance.md"* and *"garage_strategy"*, is not refused. Neither is build history
in any field other than `description`.

