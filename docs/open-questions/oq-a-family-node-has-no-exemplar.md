# oq/a-family-node-has-no-exemplar — 32 higher-rank nodes name no building, 72 asset records wait on them, and every one is `confidence: high`

*Status: OPEN · Raised in: WP-11.1, the precedent bench (4 Sep 2026)*

**OPEN — a ruling on what a family's precedent is.** All 27 families and all 5 traditions carry
`exemplars: []` and `sources: []`, by convention rather than by schema — the style-node schema allows both on
any rank. Two things follow that nobody has ruled on.

**The asset layer waits.** `build/name_asset_buildings.py` deals a node's photograph records round its own
exemplars; a node with none leaves its records unnamed, and 72 records over 18 of these nodes are the
remainder WP-4.4 could not name offline (`docs/reports/wp-4.4-the-record-that-said-322.md`). The package's
own words: *"needs either exemplars authored from sources this container cannot reach or a ruling that a
child's exemplar may stand for its parent."* Neither has been given.

**`tdl_precedents` answers with a reading.** Asked for `north-american`, the tool walks the membership tree
down and returns its members' exemplars, icons first, labelled: *"a descendant's precedent stands for its
parent only as a reading; the corpus has not ruled that it may."* That is honest and it is not a ruling.

**And `confidence: high` on every one of the 32.** The schema scopes the field to *"dates and lineage
claims"*, so it is not wrong; it is doing no work at that rank, because a node with no sources has nothing
its confidence could be measured against.

**Three options.**
1. **A family carries TYPE SPECIMENS** — a small set of exemplars marked `standing: canonical`, drawn from
   its members, with a `why` naming which member each stands for. The asset layer then names its 72
   records; the tool stops reading. The cost is 32 more editorial judgments, and a specimen that is really
   one member's icon wearing the family's name.
2. **A child's exemplar may stand for its parent** — ruled once, executed in `name_asset_buildings.py` and
   in the tool, and the family node stays empty. Cheapest; the family's own record then says nothing about
   its buildings, which is the state that raised this.
3. **Neither** — the 72 stay unnamed and the tool keeps saying "a reading". The current state, and it is
   consistent.

Recommended: (1) for the 27 families, with the specimen list derived from members' `standing: icon`
exemplars so it is a REPORT of the members rather than a second authoring; the 5 traditions stay empty.
Tranche 4 of the precedent bench (`PLAN-OF-ACTION.md` Phase 11) is gated on this.
