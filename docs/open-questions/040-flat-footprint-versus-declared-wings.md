# OQ 40 — the flat footprint versus declared wings

*Status: RULED 3 Sep 2026 · Raised in: From the real solver (WP-2.3, 25 Aug 2026)*

**OPEN — the flat footprint versus declared wings.** `exterior_walls` speaks exposure in the fully-massed house: a porch's three walls, a wing's own corner, a service ell's north light. The corpus uses this idiom everywhere — 10 of 12 partis have two same-level rooms declaring the same corner pair — and one flat rectangle cannot hold it, which is how WP-2.3's first hard-pins build proved both check plans and nearly every composed candidate "infeasible" on facts that are true of the real buildings. The ruling (contested corners downgrade, stated; generalized to any pin-set the solver proves unable to co-hold) bridges the gap honestly, but the structural fix the findings point at is a massing-aware footprint: massings already know their `depth_rooms` and expansion logic — should they carry footprint composition (main block + dependencies/ells) that the solver places rooms into, with `exterior_walls` read against the composed outline rather than one rectangle? That is a schema-and-solver change with a judgment in it, recorded rather than done unilaterally. Surfaced by WP-2.3; worked around in the open (`geometry_report.solver.refinements`), not silently.


## Lucas's ruling, 3 Sep 2026: yes — a dependency is a SECOND MASSING ELEMENT

**The answer to this entry's own question is yes.** Massings carry footprint composition — a main
block plus dependencies and ells — and the solver places rooms into it, with `exterior_walls` read
against the composed outline rather than against one rectangle.

**Ruled here and in `oq/the-parti-dissolved-its-own-dependencies` at the same moment, deliberately.**
Those two entries are the same question from two ends: this one asks what the FOOTPRINT is, that one
asks what the PARTI should stop containing. Ruling one without the other is how they drift, and
this entry has said since 25 August that the fix is "a schema-and-solver change with a judgment in
it, recorded rather than done unilaterally". The judgment is now recorded.

### The two alternatives, and why they lost

**A dependency as a second plan LEVEL was refused on five live failure modes, every one silent.**
`geometry.py`'s `write_record` and `_finish` both read `src = ground if idx == 0 else (upper if
idx == 1 else {})`, so a level with index 2 receives an empty source and is given **no geometry at
all** — drawn nowhere, and no finding raised about it. It contributes nothing to `derive_footprint`'s
`need`, so the block would be sized as though the dependency did not exist. It would be sliced out
of the main block's own rectangle anyway, since every level is cut from the same `0, 0, W, H`.
`structure.py`'s eave sum filters no index, so the dependency's storey height would be **added to the
main block's eave** — the dependency drawn as a third storey on top of the house, the exact inverse
of the ridge step-down its own grouping requires. And `storey_heights` would then judge it against a
band written for a third storey. `plans/reference/bad-03-narrow-lot-townhome.json` already carries a
level 2, so the first of those is not hypothetical.

**A new RECORD KIND was refused as too expensive for what it buys.** It forfeits the `via` bridge —
`plan_check`'s `via` clause matches on the room type of a room in `levels[].rooms[]`, and
`butlers-pantry`'s HARD `must_adjoin kitchen` carries `via: [back-hall, gallery-corridor]`, so a
dependency whose link is not a room in that array fires that rule fatal on every five-part plan. It
also forfeits `attaches_to`, and there is no loader precedent: `plan_check.load_corpus`,
`mcp_server/core.py`, the workbench search index and `check_ids.py` all enumerate record kinds.

### What the winning option already has behind it, which is why it won

Not one of these had to be invented; all of them are authored and unread:

- **`elements/slots.json`'s `wing_strategy`** — "Wing / ell strategy", with the enum this ruling
  needs (`telescoping`, `subordinate-ell`, `flanking-symmetrical-dependencies`, `additive-accretive`,
  `none`). All 159 kits carry the key and 38 state something; six make a five-part variant canonical.
- **`schema/parti.schema.json`'s `grows_by`** already has the value **`adding-a-link`**, declared by
  four partis including `centre-passage-double-pile` itself.
- **The massing catalogue already describes wings in prose** waiting for a reader:
  `"stories": "2-2.5 main / 1-1.5 wings"`, `"bays": "5-7 main"`, `"footprint": "linear-additive"`.
- **`four-over-four`'s own `expansion_logic`**: *"Flanking dependencies connected by hyphens (the
  five-part scheme), or a rear service ell. Growth must respect the axis or the whole logic fails."*
- **`attaches_to[].position`** is an authored per-massing placement statement across 16 massings.
- **`geometry_cp.py`'s `_contested_corners` already emits the diagnosis in a sentence**: *"the massing
  likely has a wing the flat footprint cannot hold"* — on `centre-passage-double-pile` it names
  `backhall`, `breakfast`, `kitchen` and `library`, three of which are service rooms the parti ruling
  strips.

### The shape, and the one constraint on it

Rooms tag to a block by a **narrow sibling field with a closed reader set** — the precedent is
`level_offset_ft` (OQ 56), whose own ruling justifies exactly this: `level` keeps its meaning and
its consumers, and the new field is read only where it must be. `level` continues to mean storey and
nothing else.

**The discipline that governs the build: a plan that declares no second block must place
byte-identically.** Sixteen plans in this corpus have one block, two of them ship, and their
placements and pinned relaxation counts are the regression guard. A second block is an addition to
the model, not a re-derivation of it.

**And `wing_strategy` must be read from the cascade with care.** `roof.py`'s own rule governs: an
inherited `forbidden` is a prohibition an ancestor made and is safe to read; an inherited
**canonical** is a positive claim the descendant never made and is not, until somebody has
adjudicated the slot on that node. `tidewater-georgian` — the shipped brief's style — states nothing
and its chain carries two conflicting canonicals (`english-palladian`'s flanking dependencies and
`georgian-colonial-american`'s subordinate ell). That node needs adjudicating before its wing
strategy is read, and this ruling does not adjudicate it.
