# oq/a-family-node-has-no-exemplar — 32 higher-rank nodes name no building, 72 asset records wait on them, and every one is `confidence: high`

*Status: RULED 5 Sep 2026, EXECUTION GATED ON TRANCHE 3 · Raised in: WP-11.1, the precedent bench (4 Sep 2026)*

**RULED 5 SEP 2026 BY LUCAS: OPTION 1 -- A FAMILY CARRIES TYPE SPECIMENS, DERIVED FROM ITS MEMBERS'
`standing: icon` EXEMPLARS**, so the list is a REPORT of the members rather than a second authoring.
The 5 traditions stay empty.

**AND THE EXECUTION IS GATED ON TRANCHE 3, WHICH THIS ENTRY COULD NOT HAVE KNOWN.** Measured 5 Sep:
**18 of the 27 families have ZERO `standing: icon` exemplars among their members today**, and every
one of the 18 is European or Iberian-American -- `british-vernacular`, `medieval-british`,
`english-classical`, `tudor-jacobean`, `british-picturesque`, `british-arts-and-crafts`,
`renaissance-classical`, `antique-classical`, `continental-baroque-neoclassical`, `french-vernacular`,
`germanic-vernacular`, `nordic-alpine-vernacular`, `low-countries-vernacular`, `iberian-islamic`,
`iberian-vernacular`, `spanish-classical`, `mediterranean-vernacular`, `colonial-iberian-americas`.
The 46 European buildable nodes carry 182 exemplars and **0 of them carry a `standing`**, because
`standing` is written by the precedent tranches and Europe has not had one.

Executing B now would deliver specimens to 9 families and leave 18 empty -- the ruling half-executed,
needing a second pass over the same 27 nodes. **Tranche 3 first, then B.** That ordering is a
consequence of the measurement and not a further ruling.


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
