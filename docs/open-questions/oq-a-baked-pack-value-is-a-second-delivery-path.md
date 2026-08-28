# oq/a-baked-pack-value-is-a-second-delivery-path — a scope on a rule cannot reach the copy of it in a kit

*Status: OPEN · Raised in: From WP-8.4, the construction scope (28 Aug 2026)*

**OPEN — 3,176 kit parameters are snapshots of pack rules, and no scope, refusal or precedence
rule reaches any of them.**

A kit parameter marked `kind: derived` with `source: <pack>` is a pack rule's value copied into
a kit file. `build/check_addresses.py::baked_vs_refused` measures the collision: **20 pairs today** deliver a figure the live rule refuses, across fourteen nodes and two
rules — `opening-proportion`'s `exterior_head_assembly_in` on twelve and `sash-light`'s
`projection_in` on eight (`chateauesque`, `cotswold-cottage-revival`, `egyptian-revival`,
`french-eclectic`, `french-normandy-revival`, `italian-renaissance-revival`,
`italianate-townhouse`, `jacobethan-revival`, `mid-atlantic-georgian`,
`queen-anne-patterned-masonry`, `renaissance-revival-american`, `tudor-revival` among them).

**The measurement itself had to be fixed to see them, and that is worth recording.** The two
refusals are reported two different ways: WP-8.3's kit refusal MARKS the row
(`refused_by_kit`) and OQ 88's scope DROPS it, recording the drop in `scope_dropped`. Reading
only the marked rows made this count report **0** the moment the scope started biting — the
number went to zero because the evidence had been removed, not because the collision had.

Every one is a masonry node resolving `georgian-colonial-american`'s baked `projection_in`
(`expr: "module * 0.25"`, value 2.25 in, `source: sash-light`) or its baked head assembly,
where OQ 88's scope has just ruled the live rule out. **The rule is refused and its snapshot is
delivered.**

**Why it is not patched.** Deleting the baked parameter on the ancestor removes it from every
descendant, and 30 of the 33 nodes that resolve it are frame nodes the rule is right for. What
is wanted is a scope on the PARAMETER, read where `resolve_slots` assembles it — a kit-schema
change and a new reader inside the hottest function in `build/`. The 20 is ratcheted so it
cannot grow in silence while that is decided.

**The general shape is worth stating separately from the 20.** A derived snapshot is a cached
computation with no cache invalidation: it was true of the pack on the day it was written and
nothing re-derives it. `check_addresses` can now see the case where the rule is refused; it
cannot see the case where the rule's VALUE has changed and the snapshot has not.
