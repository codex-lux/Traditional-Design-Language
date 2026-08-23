# WP-4.2, wave A — family-level kits and the family cascade mechanism

*23 August 2026. Opens the kit-fill work package. Companion to `docs/inheritance.md`'s "Resolution order" section (rewritten by this pass) and the 27 new `kits/<family-id>.kit.json` files.*

## Why this needed a mechanism change before any authoring could start

`PLAN-OF-ACTION.md`'s own task text for WP-4.2 says: "Fill kits top-down so the cascade pays: first the 27 family nodes... then the 90 styles (using `extends` against the family)... then the 42 variants." Before this pass, that instruction had no mechanism behind it. `build/build.py` generated kit files only for `rank: style`/`rank: variant` nodes (132 of them) — a family node had no kit file to author in the first place — and the cascade (`_cascade`, precomputed by `build.py` and walked by `resolve_kit.py`) was built entirely from `lineage` edges carrying `inherits_kit: true`. Family nodes carry no `lineage` edges at all (confirmed by checking directly: every `rank: family` node's `lineage` array is empty) — `member_of`, the field that actually places a style inside a family, was never consulted by the cascade. A style could not "extend against the family" because the family was structurally invisible to `resolve_kit.py`, no matter how real the sharing.

This is not a new problem WP-4.2 discovered — it is exactly what open question 20 named as unbuilt: "the full three-level test that WP-4.2 is written to surface... has not run yet because Phase 4's kit-fill is deliberately deferred." WP-4.2 is that test, so building the mechanism it depends on is this work package's own first task, not a detour from it.

## What was built

`build/build.py`'s kit-directory step now generates a skeleton for `rank: family` nodes too (159 kit files total, up from 132). Its cascade step gained two functions:

- **`family_of(i)`** walks `member_of` upward from a style or variant to the nearest `rank: family` ancestor. A variant's `member_of` points at its parent *style*, not its family directly, so the walk passes through the style without adding it a second time (the style is reached separately, through real lineage, if it has a `descends_from`/`regional_of` edge back to it — which every variant in this corpus does).
- **`cascade_chain(i, seen)`** (the existing lineage walk) now splices a style-rank ancestor's own family in immediately after that ancestor, before continuing into that ancestor's own further lineage ancestors — nearest and most-shared first, most distant and most specific descent last. The top-level `_cascade` assignment does the same for the starting node itself when it is a style.

Family participation is additive and order-preserving: no existing lineage-based cascade entry is reordered or removed, new family entries are only interleaved into the existing sequence. Verified directly — a `resolve_kit.py --json` snapshot of all three pre-existing populated kits (`georgian-colonial-american`, `tidewater-georgian`, `english-georgian`), taken immediately before and after the change, diffs as pure insertions to the `chain` array; every previously-resolved slot value is byte-identical.

`build/check_kits.py` needed **no code change at all** — it already validates any file under `kits/*.kit.json` generically (matching the `style` field, a generic id, against the filename), and it already reads `_cascade` from `dist/taxonomy.json` for whichever node it's checking, whatever rank that node is. Family kits are checked exactly like style/variant kits, including the dangling-`extends` check.

`docs/inheritance.md`'s "Resolution order" section was rewritten to describe the mechanism, with a worked example (`tidewater-georgian → georgian-colonial-american → american-colonial → english-georgian → english-classical → ...`) showing family entries interleaved with real lineage ancestors from a *different* family. `tests/test_kit_cascade.py` gained a `TestFamilyCascade` class (4 new tests: every family has a kit file, a style's own family is the first cascade entry, a variant reaches its family through its parent style without duplicating the style, a family kit regenerates without dropping authored content) and one pre-existing test (`test_tidewater_chain_starts_with_all_three_populated_kits`) was updated — with a dated docstring explaining why — to expect the now-four-level chain rather than three.

## The 27 family kits

Six parallel batches, grouped by trunk (the corpus's own five-tradition grouping, split further where a trunk held too many families for one batch), each batch reading every member style/variant's own node text before authoring — not assuming from the family's own summary prose, which several batches caught overclaiming (see below).

| Batch | Families | Slots specified/forbidden (of 95, per family) |
|---|---|---|
| American high-style/revival | american-colonial 4, early-republic 5, eclectic-revivals 1, romantic-revivals 3, victorian 3 |
| American vernacular/modern | american-arts-and-crafts 24, american-folk-vernacular 3, contemporary-traditional 3, mid-century-traditional 5 |
| British Isles | english-classical 10, tudor-jacobean 5, medieval-british 9, british-picturesque 8, british-vernacular 7, british-arts-and-crafts 12 |
| Classical Mediterranean | antique-classical 5, renaissance-classical 5, continental-baroque-neoclassical 3, mediterranean-vernacular 17 |
| Iberian Mediterranean | colonial-iberian-americas 15, iberian-islamic 10, iberian-vernacular 15, spanish-classical 7 |
| Northern European vernacular | french-vernacular 10, germanic-vernacular 16, low-countries-vernacular 6, nordic-alpine-vernacular 17 |

A family kit is deliberately light, not deep — the opposite instinct from the Georgian exemplar, which was authored before any family kit existed and had to specify everything itself. The instruction given to every batch: bind a slot only where the members' own text genuinely, defensibly agrees; where they disagree, leave the slot open (or record the disagreement as two `permitted` variants) rather than force one member's answer onto the whole family. Every batch found and reported real disagreement rather than papering over it:

- `american-colonial` (21 members spanning six unrelated colonial building cultures) ended at 4/95 — the batch explicitly named this as the corpus's clearest instance of a family that is a browsing container, not a real generative unit, and reported it rather than forcing false commonality.
- `eclectic-revivals` (21 members, the largest and most heterogeneous family) ended at 1/95, with the batch's own note quoting the acceptance criterion back at itself: "if a style's provenance shows 0% from the family, fix the family — I judged that forcing more here would be exactly that failure mode."
- `english-classical`'s batch found and preserved a real, deliberately-established divergence from earlier work (WP-4.1): the family's members use *different* order overlays (Adam→Chambers, Baroque→Gibbs/Vignola, Georgian→Chambers, Townhouse→Gibbs, Regency→none) — the family kit does not bind one order, because binding one would erase a distinction the corpus already went out of its way to draw correctly.
- `tudor-jacobean`'s batch caught the family's own summary text overclaiming strapwork ornament as universal — checked against the members' own `defining_characteristics` directly and found it is Elizabethan/Jacobean-only, Netherlandish-derived, absent from Tudor's own text — and left it unbound rather than repeat the overclaim into a second, now-authoritative-looking place.
- `medieval-british`'s batch caught the same pattern in reverse: the family's own blurb claims "small openings," directly contradicted by `english-gothic`'s entire structural argument (maximizing glazed area via Perpendicular tracery) — left open rather than forced.
- `renaissance-classical` and `mediterranean-vernacular` each found a genuine, sourced contradiction between two members on one slot (`pediment` permitted on a church but forbidden on a house in one; `composition_parti` literally opposite named symmetry classes in the other) and recorded both as `permitted` variants under `binding: open` rather than choosing a side.
- Two families where WP-4.1 had already found no classical-order fit at the proportion-pack layer (`iberian-islamic`'s Moorish/Mudejar cluster, `spanish-classical`'s Churrigueresque/Plateresque cluster) correctly stayed thin on `classical-apparatus` at the kit layer too — the same real gap, not re-litigated or quietly patched over with an invented order at this layer instead.

No source, date, or measurement was invented anywhere in the 27 files; every `kind: "editorial"` and every `judgment: true` flag states honestly, in its own note, why the binding is a considered call rather than a documented figure.

## What the mechanism alone already buys, before any style/variant kit is touched

`resolve_kit.py craftsman --verbose` — a style with an entirely empty kit of its own, `american-arts-and-crafts` family — now resolves 91 of its 95 slots (78 specified, 13 forbidden, only 4 genuinely unresolved), reached through a cascade that touches its own family (25.3% of resolved slots) plus real lineage ancestors' own families all the way up an inheritance chain that happens to run through Georgian Colonial American, English Georgian, and a dozen others. This was true before this session wrote a single style-level `extends` delta — it is the family layer alone, doing exactly the work the plan's own framing describes ("fill kits top-down so the cascade pays"). It also reframes the remaining work: `PLAN-OF-ACTION.md`'s acceptance line ("no kit at `status: 'empty'`") is a per-*slot*-status field, not a per-file one — with the family layer now supplying most of a style's real content by inheritance, a style/variant's own kit file needs enough of its own `extends` deltas to move at least one slot off `empty`, not a full re-specification from nothing.

## Verified against the acceptance criteria

- `check_kits.py` (whole corpus, all 159 files): 0 errors. 2 pre-existing warnings (english-georgian `code_conflict` entries, unrelated to this pass).
- `validate.py`: 0 errors, 1 pre-existing unrelated warning (mexican-colonial's date).
- `pytest tests/test_kit_cascade.py`: 16 of 16 passed, including the 4 new `TestFamilyCascade` tests and the updated four-level chain test.
- Zero regressions confirmed directly: every slot value `resolve_kit.py` resolved for the three pre-existing populated kits before this change is identical after it (diffed, not asserted).
- OQ 20 ("has the cascade been proved three levels deep") is now partially answered with real data rather than left as a test that hadn't run: the mechanism resolves correctly at four real, populated levels (`tidewater-georgian → georgian-colonial-american → american-colonial → english-georgian`) with zero merge problems found in this pass. The fuller answer — how many merge problems appear once all 90 styles and 42 variants carry their own `extends` deltas against a family, not just an empty skeleton sitting in the chain — is still open until wave B (style/variant kit fill) runs.

## What's next

Wave B: fill the 90 style kits (`extends` against their family wherever they add rather than restate) and the 42 variant kits (10-30 overrides), excluding the 3 already-populated exemplars. Batched by family, mirroring the grouping WP-1.1 and WP-4.1 already established for this corpus.

## Files touched

`build/build.py`, `docs/inheritance.md`, `tests/test_kit_cascade.py`, `dist/taxonomy.json`, `dist/taxonomy.agent.md`, and 27 new `kits/<family-id>.kit.json` files (list: american-arts-and-crafts, american-colonial, american-folk-vernacular, antique-classical, british-arts-and-crafts, british-picturesque, british-vernacular, colonial-iberian-americas, contemporary-traditional, continental-baroque-neoclassical, early-republic, eclectic-revivals, english-classical, french-vernacular, germanic-vernacular, iberian-islamic, iberian-vernacular, low-countries-vernacular, medieval-british, mediterranean-vernacular, mid-century-traditional, nordic-alpine-vernacular, renaissance-classical, romantic-revivals, spanish-classical, tudor-jacobean, victorian).
