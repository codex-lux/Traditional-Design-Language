# WP-4.1 — Proportion-pack bindings for all buildable styles

*23 August 2026. Opens Phase 4 (breadth). Companion to `build/check_pack_bindings.py` (the checker this pass wrote and wired into `check_all.py`) and the 36 pack files under `proportions/`.*

## Why this ran now

Lucas asked to proceed with Phase 4 after WP-1.1 closed Phase 1 (`docs/reports/wp-1.1-remaining-families-migration.md`). Two clarifying questions were asked and answered before work started: WP-4.2 (kit fill) would run as one large push across all 27 families rather than staged, and — the one that shapes this report — WP-4.1 (proportion-pack bindings) would run corpus-wide *first*, ahead of WP-4.2, rather than family-by-family alongside it. `PLAN-OF-ACTION.md` calls WP-4.1 "the highest-leverage authoring in the project": every kit slot that resolves to a dimension downstream reads a proportion pack's numbers, so an un-bound or wrongly-bound node produces kit content with nothing real underneath it.

## What was built

**The checker.** `build/check_pack_bindings.py` (new file) validates, for every buildable (`rank: style` or `rank: variant`, 132 nodes) node: that `proportion_packs` is present and non-empty; that every `pack` id resolves to a real file under `proportions/{orders,overlays,systems,modules}/`; that `precedence` values are a total order (unique integers, no ties); that no node binds both `trim-classical` and `trim-craftsman` at `role: primary` or `role: trim` (the schema's one hard mutual-exclusion rule); and that every entry carries `pack`, `role`, `note`. It has a `--strict` flag, now wired into `check_all.py`, that fails the build on any unbound node **except** the three named in `DELIBERATELY_UNBOUND` (see "What was deliberately not done," below) — a small module constant with its own dated comment, so a *fourth* unbound node in the future fails loudly while these three specific, checked, documented refusals do not.

**The bindings.** 127 of the 132 buildable nodes (all except the 5 that already carried a binding as WP-4.1's own template — `georgian-colonial-american`, `tidewater-georgian`, `new-england-georgian`, `english-georgian`, and one more from the original Georgian-family authoring pass) were bound in two waves of 15 batches, each an independent agent scoped to a fixed file list, forbidden from touching any field but `proportion_packs`, and required to run `check_pack_bindings.py` and `validate.py` on its own files before reporting:

| Batch | Cluster | Nodes |
|---|---|---|
| PB-1a | Dutch/German/French colonial | 8 |
| PB-1b | New England colonial + Spanish colonial Southwest | 8 |
| PB-2 | English Classical trunk | 7 |
| PB-3 | Early Republic | 8 |
| PB-4 | American folk vernacular + Arts-and-Crafts | 11 |
| PB-6a | Spanish/Mediterranean Revivals | 6 |
| PB-6b | French/English Eclectic Revivals | 7 |
| PB-6c | Colonial/Georgian/Tudor Revivals | 8 |
| PB-7a | Romantic Revivals | 9 |
| PB-7b | Victorian | 9 |
| PB-8 | British traditions | 12 |
| PB-9 | Continental European classical/baroque | 11 |
| PB-10a | Northern European vernacular | 10 |
| PB-10b | Iberian/Mediterranean vernacular + colonial Iberian Americas | 7 |
| PB-11 | Mid-century + contemporary traditional | 6 |
| **Total** | | **127** |

Every batch worked from the same template — `georgian-colonial-american.json`'s own binding (Gibbs Ionic/Doric primary/secondary, facade-classical, opening-proportion, sash-light, trim-classical, storey-graduation, room-harmonic, brick-course, timber-bay — each with `role`, `precedence`, a `note` giving real reasoning, and `authority` where the binding rests on a named source) — and the same anti-fabrication discipline: no invented citations, no pack forced onto a node its own text contradicts, every binding outside a pack's own `applies_to` list flagged in the batch's report as a **judgment binding** with its reasoning stated, and every place none of the 36 packs actually fit named as a **gap** rather than papered over.

Both waves were merged and re-verified together, not just accepted on each batch's self-report: `check_pack_bindings.py` (no argument) and `validate.py` were run corpus-wide after wave 1 (55 nodes) and again after wave 2 (72 nodes), and the full pytest suite (287 tests, chunked across three `pytest` invocations because of the pre-existing OQ 28 performance ceiling) was run once at the end. All green — see "Verified," below.

## What was found

**Judgment bindings were the majority, not the exception, and that's a property of the corpus's own age spread, not a shortfall.** A pack's `applies_to` list was authored once, early, against a partial style graph. As WP-1.1 already found for the constraint vocabulary, the batches that touched the corpus's later-added, more numerous families (revivals, vernacular, Victorian, non-English-source classical) found their nodes largely *absent* from the packs that plainly fit them — georgian-colonial-american's own children are the exception, not the norm, in how often a pack's `applies_to` already names the node being bound. Every batch was told explicitly that binding outside `applies_to` was allowed but had to be flagged with reasoning, never done silently; that discipline held across all 15 reports, and the aggregate is a large, auditable list of "why this pack, for this node, even though the pack's author didn't originally say so" reasoning — real architectural argument, not a rubber stamp.

**Five distinct order lineages were kept genuinely distinct, not homogenized.** Vignola (source/antique), Palladio (direct Renaissance derivation — bound to `italian-renaissance`, `palladian`, `jeffersonian-classicism`), Gibbs (the book colonial American builders actually owned, bound through most of the English Classical and Early Republic trunks), Chambers (the rival Georgian generation, bound where a node's own lineage names Chambers specifically, e.g. `adam-style`, `english-georgian`), and Benjamin (American pattern-book Greek Revival, bound to `greek-revival-*`, `federal-style` and kin, and — the one node in the whole corpus where it's the *only* order that's actually baseless like the style itself needs — `greek-classical`, heavily caveated as a 19th-century wood-construction compromise rather than a scholarly Attic encoding). No batch defaulted to "just use Vignola" or "just use whatever the parent used" without checking whether the node's own stated lineage supported a *different* named source; several batches (PB-2, PB-3) explicitly bound different order overlays to sibling nodes specifically to preserve a real, sourced distinction the corpus's own text draws (e.g. `english-georgian` bound Chambers deliberately *not* Gibbs, to keep it distinct from American Georgian's Gibbs binding).

**A large number of nodes correctly got no order at all, and several correctly got no binding of a system pack in a role the pack's own name suggests it should fill.** Every vernacular, medieval, Gothic, and most 20th-century tradition in the corpus has a hard constraint or a plain prose statement that no classical module applies — Elizabethan, Tudor, Jacobean (pre-Palladian), German/Scandinavian/Alpine log and timber vernacular, Shingle/Stick Style, Craftsman/Prairie, Egyptian Revival, the whole Moorish/Mudejar cluster. In every one of these cases the assigned batch checked and refused rather than forced a pack, and reported the refusal. This is the single largest confirmation that the anti-fabrication instruction actually worked as intended across 15 independently-run agents: the corpus now visibly *shows its restraint* rather than uniformly reaching for the nearest classical order.

**A recurring, name-worthy gap: no pack in the library models an Islamic/Moorish geometric system.** Three separate batches, working on unrelated file lists (PB-1b: Spanish Colonial Southwest / New Mexico adobe; PB-6a: Spanish/Mediterranean Revivals; PB-10b: `moorish-andalusian`, `mudejar`), independently flagged the same absence: no facade, order, or ornament pack in the 36-pack library encodes a horseshoe arch, muqarnas transition, geometric star-polygon setting-out, or the three-tier tile/plaster/timber ornament stratification real to this whole cluster. This is the corpus's clearest single candidate for WP-4.6 (below), because it is the one gap that independently surfaced three separate times without any batch being told to look for it.

## Verified against the acceptance criteria

`PLAN-OF-ACTION.md`'s stated acceptance is "132 of 132 buildable nodes bound; checker green; a list of missing packs with the styles that need them, as input to WP-4.6." Two of these three are met exactly; the first is met at **129 of 132**, and the 3-node shortfall is a direct, deliberate consequence of the *task description in the same paragraph* ("where a needed pack does not exist... list it — do not bind the wrong pack"). `egyptian-revival`, `moorish-andalusian`, and `mudejar` each have a real, checked reason no combination of the 36 packs applies (see "What was deliberately not done"). Binding any of them to satisfy the literal 132-count would have meant forcing a classical order or a room/facade system onto a node whose own text explicitly rules it out — exactly what the plan's own text says not to do. This tension is recorded here rather than resolved by quietly padding the count, matching the discipline WP-1.1 used at its own acceptance bar (61.5% against a ≥60% target, not gamed to a round number).

- `check_pack_bindings.py` (no argument): 129 of 132 bound, 0 errors, 3 warnings (the deliberate 3).
- `check_pack_bindings.py --strict`: 0 errors, exit 0 — the 3 known exceptions are allowlisted by name in `DELIBERATELY_UNBOUND`; any other unbound node would fail the build. Now wired into `check_all.py` in place of the non-strict call used while WP-4.1 was in progress.
- `validate.py`: 0 errors; 1 warning, pre-existing and unrelated (`mexican-colonial`'s date predates its `churrigueresque` ancestor — a taxonomy dating question, not a proportion-pack question).
- Full pytest suite: 287 of 287 passed (chunked into three runs — `test_composer.py`/`test_composition.py`/`test_constraints.py`/`test_core_measurements.py` at 201.67s; `test_elevation.py`/`test_geometry.py`/`test_kit_cascade.py`/`test_ontology.py` at 18.84s; `test_plan_validator.py`/`test_proportion_engine.py`/`test_reference_corpus.py`/`test_roof.py`/`test_site.py`/`test_structure.py` at 401.69s — OQ 28's performance ceiling, not a new issue).
- Both shipped example plans (`plans/spec-builder-colonial.json`, `plans/tidewater-georgian-careful.json`) and the pinned composer brief (`briefs/family-georgian.json`) re-run through `plan_check.py`/`structure.py`/`roof.py`/`elevation.py`/`compose.py`: output unchanged from pre-WP-4.1 baseline. Proportion-pack bindings feed kit resolution and downstream generation (WP-4.2 onward); they are not yet read by any of these five generators directly, so no behavioural change was expected or found — this pass's effect is entirely on `styles/*.json` data, none of it live-read by the pipeline yet.
- A missing-pack list "as input to WP-4.6": consolidated below.

## What was deliberately not done

**Three nodes left with no binding at all, each documented and now allowlisted in the checker:**

- **`egyptian-revival`** — trabeated, archaeological (copied from Denon/*Description de l'Égypte* plates), explicitly not module-derived per its own text; none of the five Vignola-family orders share its structural logic (battered walls, no arch, cavetto cornice, bundled-reed/lotus columns), and it is "almost never for a house" so the domestic room packs don't apply either.
- **`moorish-andalusian`** — its own `governing_logic` states "no order and no absolute module... geometric generation from a square, compass-and-straightedge." `room-vernacular`'s own `applies_to` list excludes this exact node while including its later vernacular descendant, a deliberate boundary in the pack's own original authorship that this pass chose to respect rather than override.
- **`mudejar`** — almost entirely ornament and structural technique (whole-brick corbeling, *par y nudillo* roof carpentry, *alfiz* framing) rather than room- or facade-level proportion; no pack in the library reaches that layer.

**No pack was invented to fill a gap.** Every batch was told explicitly that authoring a new pack is WP-4.6's job, not WP-4.1's, and every batch honored that boundary — gaps are named, not silently patched with a same-named placeholder.

**Downstream wiring was not attempted.** `build/structure.py`, `roof.py`, `elevation.py`, and `compose.py` do not yet read `proportion_packs` off a style node directly (they currently read fixed packs like `gibbs-ionic`/`facade-classical`/`brick-course` by id, as `tidewater-georgian`'s kit specifies them). Making those generators style-aware via each node's own `proportion_packs` binding is real future work, not scoped into WP-4.1's own task text, and not attempted here.

## Consolidated candidate list for WP-4.6

Every "Gaps found" section across all 15 batch reports, deduplicated and grouped. `PLAN-OF-ACTION.md`'s own WP-4.6 already names several of these as "likely candidates" (Greek Doric, a Gothic Revival facade system, a Craftsman opening system, adobe/rammed-earth, a Dutch gambrel system, cast-iron/ironwork) — those are marked below with which batches independently re-confirmed them, real corroboration rather than restating the plan.

**Orders and ornament systems**
- A true baseless, archaeologically-correct Greek Doric order (Stuart & Revett / Lafever) — *confirmed independently by PB-2 (Regency's real diagnostic order) and PB-9 (greek-classical, forced onto benjamin-doric as the least-bad available approximation)*. Named in the plan itself.
- An Islamic/Moorish arch-and-ornament system: horseshoe arch, muqarnas, geometric star-polygon setting-out, tile/plaster/timber stratification — *independently surfaced by PB-1b, PB-6a, and PB-10b on unrelated file lists*. The single most-corroborated gap this pass found.
- A Mudejar-specific whole-brick corbeling/offsetting ornament module, distinct from `brick-course`'s American coursed-wythe logic (different coursing dimension entirely).
- A Roman/Byzantine/Romanesque foliate-capital order, distinct from the five Vignola-family orders (Richardsonian Romanesque).
- A portada/retablo ornament-panel system — ornament confined to a bounded panel against an otherwise plain field, inherited from Spanish Plateresque into Churrigueresque and Mexican Colonial; none of the library's facade systems are panel- rather than order/massing-driven.
- An estipite/simple-impost loggia order (impost directly on an unfluted shaft, no entablature) — Italian villa/Tuscan vernacular loggias use a genuinely simpler logic than any order built around the entablature-as-¼-height invariant.
- Sawn/carved Gothic ornament (bargeboard, drip moulds, pointed/ogee sash heads, stone or timber tracery) — Carpenter Gothic, Gothic Revival American, Rural Gothic Villa.
- Sawn-bracket Victorian trim, distinct from both trim-classical and trim-craftsman (Italianate American/Villa).
- Turned/spindled millwork trim (Queen Anne's lathe-turned posts, spindle friezes, sunburst/terra cotta panels).
- Scottish Baronial's crow-stepped-gable/corbelled-bartizan vocabulary.
- Jacobethan/Tudor/Jacobean strapwork, linenfold panelling, and true period brick-with-stone-dressing dimensions (distinct from `brick-course`'s Georgian-calibrated coursing).
- Alpine bracket/balcony/carved-timber ornament (Swiss Chalet's *Lauben* balustrade, purlin ends, bargeboard).

**Facade / massing systems**
- A Gothic Revival facade and opening system — *named in the plan; independently confirmed absent by PB-7a (Rural Gothic Villa left with no opening-role pack at all as a direct result) and PB-8*.
- A Craftsman opening system and Prairie trim family — *named in the plan; PB-4 confirmed Craftsman/Prairie cluster bound with no opening pack available*.
- A facade system for a windowless peripteral colonnade (Greek) and Rome's arcuated pier-arch-pier bay rhythm.
- A facade system for Baroque's curved-wall, accelerating bay rhythm (contradicts facade-classical's even Palladian rhythm and facade-picturesque's asymmetrical logic alike).
- A French vertical *travée* facade system (window-over-window-over-dormer as the structural bay) — every current facade/opening pack encodes a horizontal, Anglo/Italian-derived logic; French Renaissance Chateau has no fit at all.
- A facade/composition system for symmetrical or near-symmetrical pre-Palladian English fronts (Elizabethan, Tudor, Jacobean) — falls in a genuine gap between facade-classical (Georgian-and-later) and facade-picturesque (asymmetrical).
- A symmetrical, centreless multi-door facade system (some Dutch/French colonial fronts that are symmetrical but have no single dominant entrance bay).

**Modules**
- An adobe and rammed-earth module — *named in the plan; independently confirmed by PB-1b (New Mexico Adobe/Spanish Colonial Southwest) and PB-6a and PB-10b (thick-wall/deep-reveal load-bearing mass generally)*.
- A Dutch gambrel roof geometry system (break point, slope ratio, eave kick) — *named in the plan; confirmed by PB-1a and PB-6c*.
- A cast-iron/ironwork system — *named in the plan; PB-6a additionally flagged wrought-iron for Spanish/Mediterranean Revivals*.
- A half-timber infill/nogging panel module, distinct from `timber-bay`'s larger structural framing bay (German Fachwerk, Norman vernacular, English medieval timber-frame, later brick-nogging patterns).
- A curvilinear (holbol) Cape Dutch gable geometry module, and a separate stepped/bell/neck gable module for Low Countries urban fronts — no "gable geometry" system of any kind currently exists in the library.
- A stone-coursing equivalent of `brick-course`, for dressed or rubble stone rather than brick (Cotswold, French Manoir, Norman Vernacular, Italian/Tuscan villa vernacular).
- A jetty/cantilevered-overhang proportion rule, distinct from `timber-bay`'s general framing bay (Garrison Revival's defining move).
- A mansard/dormer massing module (slope geometry, dormer-to-bay proportion, pavilion projection) — Second Empire has no fit among the 5 existing modules.
- A polygonal/octagonal plan-geometry module (Octagon House's triangular corner residues, unaddressed by `room-harmonic`).
- A settlement-scale walled-precinct massing system, beyond any single-building pack (Mexican Hacienda's *casco*).
- A "reduced classical order, thinned to budget vocabulary" logic — corner boards and a plain fascia standing in for a full entablature — recurring across American Farmhouse Vernacular, Minimal Traditional, and Ranch Style, none of which any existing pack states as its own governing logic rather than an absence.
- A theatrical/sculptural plaster surface system (Storybook Style's rolled eaves, distressed stucco).
- A fixed-picture-window-with-flanking-sash opening system (Ranch Style) — `sash-light`'s muntin arithmetic doesn't reach undivided float glass.

## Files touched

127 `styles/*.json` files (proportion_packs additions only, verified via `git diff` on every batch as pure insertions with no other field touched). `build/check_pack_bindings.py` (new file, extended with `DELIBERATELY_UNBOUND` and `--strict` semantics in this merge pass). `build/check_all.py` (now runs `check_pack_bindings.py --strict`). `docs/reports/wp-4.1-proportion-pack-bindings.md` (this file). `README.md`, `CHANGELOG.md`, `docs/open-questions.md` (see their own diffs for what changed).
