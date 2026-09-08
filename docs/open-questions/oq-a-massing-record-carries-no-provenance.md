# oq/a-massing-record-carries-no-provenance — `massings/catalog.json` has no `sources`, no `confidence` and no `kind` on any of its 40 records

*Status: OPEN · Raised in: WP-11.1, the precedent bench (4 Sep 2026)*

**OPEN.** Every substantive layer of this corpus carries a provenance vocabulary: `styles/` has `sources`
and `confidence`; `kits/` has `kind` and `source` per parameter and `judgment` per slot; `proportions/`
has a required `authority` with a `strength`; `faults/`, `rooms/`, `groupings/` and `partis/` have
`sources` and `confidence`; `openings/grammar.json` and `moves/registry.json` declare themselves editorial.
`schema/massing.schema.json` has none of these. A massing carries `origin {period, region, note}` and free
`notes`, and its `expansion_logic`, `structural_logic`, `footprint` and `stories` — the fields the composer,
the placer and the roof layer read — are stated as facts with nothing behind them.

Measured 4 Sep 2026: **40 records, 0 sourced.** Beside it, the same audit found `groupings/` internal rules
(85) carry no per-rule source, `openings/grammar.json` was fitted to one plan by its own note, and all 16
plan records have no `provenance` block (the schema gained one in 0.2.0 after they were written).

**Why it matters more than its size.** `roof.py` reads `massing.hearth` as the fallback for chimney
placement when the kit states none; `geometry.py` reads the footprint and pile; `compose.py` reads
`expansion_logic`. A massing is the volumetric skeleton every house is composed on, and it is the one layer
whose claims a reader cannot trace to anything. The precedent bench gives it a natural source: a massing's
own exemplars are buildings, and a building's survey states its over-all dimensions, storeys and plan.

**What wants ruling.** Whether to give the massing schema `sources[]`, `confidence` and an `exemplars[]`
that name `precedents/` records (the cheap half: the schema change and a `check_massings` rule that a
massing with a `footprint` band names at least one surveyed building inside it), or to leave massings as
the corpus's stated editorial skeleton and say so in `docs/model.md`. Not built in WP-11.1.
