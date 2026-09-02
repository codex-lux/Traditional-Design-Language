# Traditional Design Language — State of the Project

*Originally written 23 August 2026 against v0.6. **Revised 24 August 2026**, after Phases 0–3 closed and Phase 4 ran through WP-4.2. Everything below was verified by running the toolchain, not by reading the docs — every checker, the proportion engine selftest, both plan validations, both composer briefs, the geometry solver, and the full test suite were executed, and the numbers here are what they returned. Where a figure has moved since the 23 August review, the old figure is named so the direction of travel is visible.*

*Figures reconciled again late on 24 August 2026, after OQ 28 and WP-4.3 landed: 17 groupings (was 16), 31 open questions (was 30), and two rows the appendix had never carried — `construction/` and `docs/reports/`. Then **WP-2.3 closed Phase 2**: `build/geometry_cp.py` (see the 25 Aug merge note in Part III), 330 tests across 17 files (was 291 across 14), 32 open questions, the suite one ~3-minute run. Part III's entries for OQ 28, the garage and the hill-climbing solver are struck through rather than deleted, in this document's own habit of leaving the old reading legible beside the new.*

*Reconciled a third time at the end of 24 August 2026, after **WP-4.5** closed the parti coverage gap and a full pass over the open questions. 21 partis (was 12) naming 129 of 132 styles with **0 uncovered** (was 93 uncovered); 60 rooms (was 58); **22 checks and 419 tests across 22 files** (was 22 and 344); **42 open questions, 8 of them open** — every one Lucas had ruled on is now executed. Three things in Part III are no longer true and are corrected rather than struck through, because each was a claim about behaviour rather than about a count: outdoor rooms are no longer dropped before placement (**OQ 55** — a courtyard is placed, dimensioned, excluded from the heated envelope and drawn open, and the ranges around it are laid out as a stated guillotine tree because the search cannot find a ring); a style with no native parti no longer borrows another style's diagram silently (**WP-4.5**, and `NATIVITY_W` 6 → 20); and a parti is no longer unchecked against the style it was written for (**OQ 59** — five of twenty-one were carrying fatal findings against their own native styles, so a Charleston brief came back with a centre-passage single pile; 21 of 21 compose now). Two findings from that pass are worth carrying forward as warnings rather than as history: **unjudged reported as evaluated-and-failed** was found twice in one package, which is this project's first discipline running backwards; and a rule that a correct plan structurally **cannot** satisfy — a landing required to reach a stair hall on its own storey, a butler's pantry required to touch a kitchen in another building — reads exactly like a plan that is wrong.*

*Reconciled a **fourth** time on **25 August 2026**, and this is the revision a new session should
read first. Two work packages closed and six open questions moved. **WP-4.6 is COMPLETE** —
twenty-one proportion packs, and every item of WP-4.1's list that this corpus can support is now
built; the items it cannot support are named in the report with a reason apiece rather than left
silent. **Ontology 0.7.0, 97 slots** (was 0.6.0/96, was 0.5.0/95): `arch` joined at 0.6.0 and
`expressed_frame` at 0.7.0. **132 of 132 buildable nodes bound** — `DELIBERATELY_UNBOUND` is empty
for the first time — **but read OQ 51 before trusting that number.** 57 packs, 262 pack conflicts,
761 derived rules, **31 checks and 861 tests across 35 files** (was 22 and 419 across 22), plus the workbench app's own 10-case `node --test` suite.
**51 open questions, 7 of them open**, and five of those seven are blocked on a network this
container does not have rather than on anyone's judgment.*

*Two things from that day are warnings rather than history, and both belong at the top. The first:
**a count in this corpus changed nine times when somebody read it instead of grepping it**, and the
ninth would have destroyed good data — a script that looked only at `value` reported 57 kit
parameters as mis-tagged placeholders when 55 carry a `range` and 2 a `set`. A regex proposes and
reading disposes; verify a sample before accepting any number in this document. The second:
**"132 of 132 bound" counts a node's OWN bindings and has never measured what a node RECEIVES.**
The lineage cascade hands every node its ancestors' packs, and `ranch-style` has 69 of its 78
dimensioned slots governed by packs it never bound. That is OQ 51. It was **ruled on 25 August —
adjudicate the 249 unjudged gaps first (233 was a mis-measurement; see WP-8.2), flip pack inheritance to opt-in once they approach zero** —
and it is measured and ratcheted rather than fixed. The ruling makes it the next package, not a
question. Every open question that remains is blocked on the network, not on a judgment.*

*Now maintained as a **living document** (Lucas's ruling, 25 Aug 2026) — updated as work lands rather than re-issued as dated snapshots. **Updated 25 August 2026** after WP-4.3 (the garage), OQ 28 (the module cache), WP-5.2 (the workbench, in `workbench/`), WP-5.1 (DXF/IFC export with a proven round-trip), WP-5.5 (drawing-to-record ingestion: the Transcription surface, the drafter-DXF extractor, plan schema 0.2.0's `provenance`) and WP-2.3 (the real solver — placement as CP-SAT with named conflict sets). The appendix carries the current verified counts; prose below that describes a pre-workbench state is corrected in place where it would now mislead.*

---

## Part I — What this project is trying to be

### The aspiration

The brief for this work describes a role that does not design individual homes but designs *the system that produces them*: catalogs of rooms, groupings and massings as reusable components; rules of assembly that say what connects, what is constrained, and what produces a sound and coherent house; design intuition translated into structured, repeatable patterns; and, in effect, a new programming language for how homes are created.

What has been built answers that brief with a specific thesis, one that the original job description does not state but that the project now embodies and that should be named plainly because it is what makes the work distinctive rather than merely systematic. The thesis is that **a traditional house is a sentence in a language, and the language can be written down**. Elements are the alphabet. The proportioning system is the grammar. A style is a vocabulary and a set of bindings on that alphabet. A plan is a sentence; a grouping is a phrase; a parti is a sentence pattern. And — the layer most systems omit — there are *solecisms*: named, testable errors, the things that make a house read as wrong to someone fluent even when no rule on paper was broken. A system that can generate houses but cannot recognize its own solecisms will produce what Chomsky called colorless green ideas sleeping furiously: syntactically valid, and dead.

This matters beyond engineering. The point of encoding the language is not to automate the architect out of the room; it is to make fluency scalable, so that a production builder in the $400B market can build a house that *belongs* — to its place, its climate, its lineage — without a senior classicist standing over every drawing. The project is, in the terms Lucas uses elsewhere, a translation engine: it translates the accumulated wisdom of four centuries of building practice into a form a platform can execute and a human can still argue with.

### The parts and how they tie together

The system is a stack of nine layers. Reading it bottom-up, each layer is a precondition for the one above it, and the order in which they were built — spine first, then breadth — is itself one of the project's most important decisions.

**1. The alphabet.** Three style-independent catalogs that every style draws from but none owns. The *element ontology* (`elements/slots.json`) is 95 universal slots in 8 groups, from `roof_pitch` to `entry_sequence` to `garage_strategy`; a style does not own a cornice, it specifies one. The *massing catalog* (`massings/catalog.json`) is 40 volumetric skeletons, each carrying `expansion_logic` — how the type grows without breaking, the property a generative system most needs and formal style descriptions most often lack. The *room catalog* (`rooms/`) is 60 room types carrying the furniture that must fit with real clearances, daylight depth, typed directional adjacency, a six-rank privacy gradient, and servicing. These three are orthogonal to style by design; the test of the ontology is that adding a style should never require adding a slot.

**2. The grammar.** 57 proportion packs (`proportions/`) implemented as *functions, not tables*. Vignola's five orders are the spine; Palladio, Gibbs, Chambers and Benjamin are overlays carrying only their deltas; brick course, timber bay, sash light, storey graduation and log module are the non-classical equivalents, because most traditional buildings were proportioned from a material unit and not a column. Give a pack a module and a context and it emits a fully dimensioned assembly, member by member. Each pack states its own invariants as evaluable expressions and records conflicts with building today — 262 across the corpus: the 8-foot ceiling against a Corinthian entablature, the IGU that cannot take true divided lites — each with a severity and resolution prose. (Ranked honest/dishonest substitution sets are planned structure the corpus does not yet hold — the WP-5.2 audit established that, 25 Aug 2026.) This is the project's most commercially defensible material: the knowledge that lives only in senior architects' heads, written down as executable rules.

**3. The vocabulary.** The style graph (`styles/`) — 164 taxa in four ranks (5 traditions, 27 families, 90 styles, 42 variants), spanning 700 BC to 2026, related by 476 typed lineage edges in a DAG rather than a tree. The single most important modelling decision in the whole project lives here: `descends_from` (actual transmission of practice) is a different edge from `references` (claimed ancestry), and only the former carries the kit-of-parts cascade. Greek Revival references Athens and descends from Federal carpentry; Colonial Revival references Georgian and descends from Beaux-Arts offices and the millwork catalog. A model that cannot express that gap will quietly produce wrong buildings. Each node also carries 624 massing affinities graded from `canonical` to `forbidden`, 660 enforceable constraints, 482 exemplars, and the binding of the node to its proportion packs.

**4. The bindings.** One kit file per family, style and variant (`kits/`, 159 files), materializing all 95 slots so that selecting a style resolves to a directory of specified, inherited, open or forbidden elements with a source column showing which ancestor each value came from. This is where a style becomes buildable rather than describable. The cascade walks `descends_from` and `regional_of` edges nearest-ancestor-first and — since WP-4.2 — splices each style-rank ancestor's own *family* into the chain alongside them; the `extends` operator lets a child add to a parent's binding rather than restate it.

**5. The solecisms.** The fault corpus (`faults/`) — 209 named errors, hung *element-first* off slots rather than styles, because the half-width shutter is wrong on every house that has shutters. Style enters through 846 exceptions (496 with numeric bounds): a Georgian five-foot portico is fatal by Craftsman rules and correct by its own. Every fault carries a cause with a named driver (exactly one of 209 is ignorance; the rest are stock sizes, trade sequences, catalog defaults and code minima), three tiers of fix (`right`, `cheap`, `dishonest`), two severity axes (how it reads, how it lives), and an executable `test`. The corpus returns *unjudged* for what it cannot evaluate, never *passed*.

**6. The phrase layer.** 17 groupings (`groupings/`, was 16 before WP-4.3 added `garage-and-hyphen`) — the hall-and-parlor pair, the centre-passage core, the entry sequence, the service core, the primary suite — with internal rules carrying severities and tests, and the join field `attaches_to`, which says how the grouping lands in a massing and at what fit. This is the scale people actually design at, and it is the hinge that makes rooms and skeletons composable. Twelve partis (`partis/`) then give canonical sentence patterns: topology and roles only, with dimensions always pulled from the room catalog so nothing can drift.

**7. The critic.** The plan schema and validator (`schema/plan.schema.json`, `build/plan_check.py`): a hand-authorable plan record checked across room, adjacency-and-privacy, grouping, fault, code, style-constraint and elevation layers. Built *before* the composer, because a composer needs a fitness function and this is it. Two worked examples ship — a deliberately ordinary production Colonial and the same corpus applied carefully — alongside a 14-plan reference corpus transcribed from real drawings.

**8. The generator.** The composer (`build/compose.py`) seeds from the partis native to the style, sizes rooms from the catalog, revises against the validator until it stops improving, and returns four contrasting candidates ranked fatal-first then by style fidelity — each with what it trades away and a log of every assumption. **Since Phase 9 (1 Sep 2026) the revision is a loop with a critic in it**: `build/critique.py` judges the DRAWN house and sorts every finding into what a generator can do about it (actionable, the engine's, the critic's own invention, the architect's), and `build/revise.py` applies the registered moves of `moves/registry.json` — each a corpus rule made executable, quoting the sentence it executes — round after round, accepting only a strict improvement and rolling anything else back. It runs on the returned candidates by default, and the workbench can ask for it on the record in hand (WP-9.3: the critique and revise chips, the Revision panel); WP-9.4 audited all three and found the things the reports said were checked, `docs/reports/wp-9.4-the-things-the-reports-said-were-checked.md`. `docs/revise.md`. Geometry (`build/geometry.py`, `render_plan.py`) then places rectangles on the parti's bay grid, both levels solved jointly for vertical alignment, counts every relaxation off the grid, and renders an SVG that is strictly a view of the data. Above it sit walls and structure (`structure.py`), roof (`roof.py`) and the elevation generator (`elevation.py`).

**9. The interfaces.** The MCP server (`mcp_server/`, 26 tools) is the real answer to "navigable by AI": not a file format but a server an agent consults mid-conversation, with progressive disclosure built in. Beside it, `dist/taxonomy.html` (the interactive phylogeny), `dist/orders.html` (the live order-drawing tool, running a JavaScript port of the engine checked to agree with the Python to 0.02 inches), `dist/taxonomy.json` for platform ingestion, and an agent digest. The image layer (`assets/manifest.json`, 322 records) is the evidence layer: good/bad pairs authored from the data before any image exists.

### The pipeline as a whole

Put the layers in motion and the intended flow is:

> **Brief** (area, bedrooms, lot, style) → **Style** resolves to a **kit** and its **constraints** and **packs** → native **partis** seed candidate **plans** assembled from **groupings** of **rooms** on a **massing** → the **validator** scores each against rooms, adjacency, faults, code, style constraints and the elevation → the **composer** repairs and ranks → **geometry** places and dimensions → **structure, roof and elevation** give it walls, a covering and a composed front → *[details, export — not yet built]* → **documents** a builder can price and permit.

The compiler metaphor is exact. The schemas are the language specification. The checkers are the linters. The validator is the type checker. The composer and geometry pass are the compiler front-end. As of the Phase 3 work, the first passes of the back-end exist too — the IR is now framed, roofed and given a front elevation. As of 25 August the last mile is mostly built: the workbench a human can move a wall in is live (`workbench/`, WP-5.2), the drawings leave in the formats a drafter and a BIM tool open (DXF/IFC, WP-5.1, round-trip proven), and drawings flow back in through the Transcription surface and the drafter-DXF extractor (WP-5.5). What remains of it: generated guidelines and details (WP-5.3, waiting on Phase 4 breadth by choice), and the deferred cost layer. The MCP server is the runtime through which a human or agent drives the whole thing.

That is the shape of the vision. The rest of this document is about how much of it is standing.

---

## Part II — What is in place and functional

The following layers run clean, are schema-checked, and do what their documentation says. Each was executed during this review.

**The style graph and its validator.** `validate.py` passes: 164 nodes, schema-valid, all references resolve, inheritance edges form a DAG, one chronology warning that survives by design (Mexican Colonial contains Churrigueresque as a phase). The four-rank structure, the two-hierarchy separation, the typed edges and their cascade semantics are all settled and documented in `docs/model.md` and `docs/inheritance.md`.

**The element ontology and massing catalog.** **97 slots across 8 groups at ontology 0.7.0** (was 95 at 0.5.0, 93 at 0.4.0), all 40 massings carrying expansion logic, both consumed correctly by every downstream layer. Two slots were added on evidence rather than on taste, and each closed an open question: **`arch` at 0.6.0** (OQ 46) holds the arch as a SPANNING MEMBER — its rise against its span, what it springs from, and whether an arch is permitted at all, which is what Egyptian Revival's c03 needed, being a rule about arches stating that there are none. **`expressed_frame` at 0.7.0** (OQ 47) holds a member that IS, or REPRESENTS, structure shown on the outside of a wall, and its `member_status` field — `structural` / `structural-and-expressed` / `applied` / `none` — is the only field in the ontology that records whether a thing is doing the job it appears to do. Before it, the corpus could not tell a frame from a picture of one. It is bound on 14 kits, and **five of those forbid the member**, which is the same argument that got `arch` built.

**The proportion engine.** `selftest` resolves and dimensions all 57 packs with zero problems; `check_orders`, `check_modules` and `check_systems` pass with only explained warnings. Invariants are proved against the data, and the data encodes what the authorities *drew*, not what they said — Vignola's pedestal at 0.35 in Corinthian and Composite is the proof that the engine is honest.

**Proportion packs bound to the vocabulary — 132 of 132 buildable nodes**, and `DELIBERATELY_UNBOUND` is empty for the first time (was 5 at the last review, 129 after WP-4.1, 131 after WP-4.6). WP-4.1 held out three nodes where no pack honestly fitted; `moorish-arch` took two of them, and OQ 49's **scoped binding** took the last. `egyptian-revival` is now bound to `facade-peristyle` **scoped to the two `column` rules that fit** — a distyle-in-antis front count and an intercolumniation band its own 1.5–2.5 sits inside — and excluded from the six that do not, including an entasis its own c04 forbids in so many words. That distinction is the whole reason the binding is defensible rather than a way of reaching 132.

**BUT READ OQ 51 BEFORE USING THIS NUMBER.** It counts a node's OWN `proportion_packs` array. `resolve_kit.resolve_packs` walks the entire `_cascade`, so a node also receives every pack its ancestors bound, judged for the ancestor and never for it. Measured: **287 (node, role) pairs** where an ancestor fills a role the node never bound, of which **249 involve a pack whose own `applies_to` does not name that node**; and **3,356** pack-arrivals purely by descent. (This paragraph published 294/233/3,367 until 28 Aug 2026, when the WP-8.4 adversarial audit found it disagreeing with line 142 of this same file: WP-8.2 corrected the meter -- its ROLE loop lacked the `pack not in own_ids` guard its PACK loop had -- and both figures were wrong in the flattering direction.) `shotgun-house` takes its facade from `facade-peristyle` bound on `roman-classical`; `ranch-style` has 61 of 68 dimensioned slots governed by packs it never bound. `build/check_inheritance.py` reports it, names the ancestor that decided each one, and pins all three numbers. **RULED 25 Aug: adjudicate the 249 first, flip to opt-in inheritance after** — see Part III and Part V.

**The kit mechanism, and now the kits themselves — 159 of 159 populated** (was 3 of 132). WP-4.2 built the missing half of the mechanism first: family nodes had no kit files at all and carry no lineage edges, so a family could never appear in any cascade, and the plan's own instruction to "extend against the family" had nothing behind it. `build/build.py` now generates a kit for every family node and splices a style's own family into the chain via `member_of`, additively, without reordering any real lineage ancestor. Then all 129 remaining style/variant kits were filled in two sub-waves. Corpus-wide: 1,556 `specified`, 330 `extends`, 223 `forbidden` bindings. A variant now resolves through a chain in which every ancestor carries real content — `appalachian-log-house` reaches 34 populated levels.

**Executable style constraints — 660 of 660 migrated, 61.5% of hard constraints tested.** At the last review these were prose that nothing read. WP-1.1 gave them the fault corpus's own `expression`/`threshold`/`direction` pattern plus `scope` and a `one-of` direction, and `build/constraint_vocabulary.py` (87 named variables) is the shared namespace. 365 carry a test; 295 are honestly `scope: judgment` — the sources do not determine them, and the corpus says so rather than inventing a number. WP-1.2 wired the validator to read them.

**The fault corpus.** `check_faults.py` passes: 209 faults, every slot covered, every fault carrying a test.

**Rooms, groupings and partis.** `check_rooms.py` passes. All 60 rooms carry furniture with clearances, daylight, adjacency, privacy rank, and — better than the last review recorded — a `style_variation` block on every one. All 17 groupings carry `attaches_to`. The 21 partis name 129 of 132 styles as native, 0 uncovered (WP-4.5).

**The plan validator.** Both example plans run and produce their documented results. Two-hop adjacency through a hall, rank-transparent circulation, the two-ended daylight correction, the `via` field, style constraints and the elevation layer are all implemented.

**The composer.** Both briefs run and return four ranked candidates with decision logs, trade-away statements and honest refusals. Lot-infeasible candidates are now dropped rather than merely outscored.

**Geometry, and composition within it.** WP-2.2 gave the solver compositional terms — entrance on the entrance front, principal rooms to the best aspect, service to the rear, the approach sequence — read from the style's own `composition_parti` and constraints rather than invented. The Tidewater plan now places its portico on the south wall with the principal rooms flanking the passage on the front.

**Walls, structure and storeys (WP-3.1).** Outside-to-outside footprints, wall lines, a bearing-line diagram, floor-to-floor heights from `storey-graduation`, and a section. No 2×10 spans 18 ft silently.

**The elevation generator (WP-3.2).** A Tidewater front elevation with five bays, a centred doorway composed to Gibbs, sash lights correct for the declared date, one head datum per storey, and a cornice regenerated as the style's own entablature reduction at the plan's real storey height. Its `measurements` feed an elevation layer in the validator. It evaluates 83 of the 177 applicable photograph-measurable faults — short of the acceptance text's named 100, disclosed rather than closed by fabricating data for faults it has no model for.

**Roof (WP-3.3).** Roof plan SVGs for both shipped plans, wing ridges stepping down, pitch inside the style band, chimneys satisfying the Tidewater constraint.

**The site layer (WP-2.4).** `site` objects on the plan and brief schemas — street bearing, setbacks, slope, prevailing wind, piazza bearing, party-wall condition. The composer caps bay count to the lot; the renderer draws the lot boundary, setback envelope and north arrow. This is what finally made the Charleston piazza and Pennsylvania bank-house constraints evaluable.

**The reference corpus (WP-2.1).** 14 of the Plan Examples transcribed into schema-valid plan records — 7 good, 7 bad — and scored. This was the experiment that tested whether the validator agrees with Lucas's eye.

**A real regression suite.** **861 tests across 35 files**, each named for the finding it protects (was 304 across 16, 291 across 14). `make check` runs **31 checkers** then the suite, in one run of about eight minutes. Three of the checkers are newer than the last review and each exists because a class of silent corruption was found: `check_counts.py` fails the build when a number in the prose disagrees with the data; `check_addresses.py` compares what two co-binding packs MEAN at one address; `check_inheritance.py` reports what the lineage cascade delivers that nobody bound.

**The MCP server.** 26 tools registered, imports cleanly, `core.py` callable directly.

**Repository hygiene and documentation.** The repo is consolidated, git-tracked, `_to_delete/` cleared, duplicate root files removed, every README count script-reproducible, and no doc references a path that does not exist.

Taken together: **Phases 0, 1, 2 and 3 are complete, and Phase 4 is complete through WP-4.3.** The language now has an alphabet, a grammar bound to its vocabulary, a full set of bindings, a critic that reads executable rules, a composer, a solver that composes, and a building with walls, a roof and a front.

---

## Part III — What is begun but needs to be fleshed out

**THE LARGEST OUTSTANDING ITEM, NOW RULED AND THEREFORE THE NEXT PACKAGE: the lineage cascade
delivers proportion packs nobody bound (OQ 51).**
Found on 25 August while closing OQ 49, and the way it was found is the point. `egyptian-revival`
was the corpus's one deliberately unbound node, held out under a note saying nothing in the library
fitted its trabeated order — and `facade-peristyle` was already reaching it from **five ancestors**,
unscoped, carrying an entasis rule the node's own c04 forbids. **The deliberate refusal was
cosmetic.** `proportion_packs` being empty on a node means the node's own array is empty;
`resolve_packs` walks the whole cascade.

Measured, not estimated, and RE-measured 28 Aug 2026. **287** (node, role) pairs where an ancestor fills a role the node never
bound — 58 secondary, 51 massing, 49 primary, 43 facade, 42 opening, 26 interior, 25 room. Of
those, **249** involve a pack whose own `applies_to` does not name the node, which is the real
backlog; the other 38 were at least judged by somebody, and 10 more have now been DECLINED. **3,356** pack-arrivals purely by descent. (The 294/233/61 first published, and the 293/222/71 after it, were both wrong in the flattering direction -- see WP-8.2.)
And on every node sampled, **every slot resolved by precedence alone with not one carrying a
human's slot-level ruling** — those precedence numbers were authored on ancestors, for the
ancestors' buildings, with no view of the descendant.

It is the third place inheritance has been found transmitting more than anyone bound.
`hybridizes_with` transmitted a donor's whole kit (OQ 58 scoped it); a BINDING transmitted a pack's
whole rule set (OQ 49 scoped it); `descends_from` still transmits an ancestor's whole set of packs,
and it is the one with 3,356 instances. `build/check_inheritance.py --roles` and `--slots <node>`
report it and name the ancestor that decided each case; all three numbers are pinned so the backlog
cannot grow silently.

**RULED 25 August: adjudicate first, flip second.** Of the four costed options, opt-in inheritance
(`inherits_packs`, mirroring what `inherits_kit` already does for the kit cascade) is the
destination, and going there first was refused: the mechanism is a morning and the fallout is 287
role gaps stranded in a single commit. So the sequence is the other way round. Work the **249**
unendorsed gaps in leverage order; where the inherited pack is right for the node, add the node to
that pack's `applies_to` — that is the adjudication, and it moves the gap from unendorsed to
endorsed; where it is wrong, bind the right pack on the node or scope the edge. When `unendorsed`
approaches zero, flip to opt-in, by which point it is a safety net rather than a cliff.
`check_inheritance.py --unendorsed` prints the work list grouped by pack, because adjudicating one
pack settles every node under it: `storey-graduation` **38**, `opening-proportion` **23**,
`trim-classical` **16**, `chambers-ionic` **15** (on `carpenter-gothic` and both Gothic Revivals),
`facade-gable` **14**, `sash-light` **12**, `brick-course` **11**. The accepted cost is that wrong
dimensions keep arriving while the list is worked — tolerable only because they are counted.

**The address collision, closed but worth knowing about (OQ 48).** A `(slot, dimension)` address
could hold two packs measuring different quantities — `window_head_masonry/height` held six, at
94 in against 7.6 in against 0.37 in, with 44 nodes binding two or more of the packs involved.
Rules now carry a `quantity` naming what they measure, all 74 colliding addresses were read one at
a time, 74 minority rules took their quantity as their dimension, and `check_addresses.py` reports
**0**. The reason it matters going forward: the first estimate of the damage was ~20 and the true
number was **139**, found only by reading all 442 co-binding pairs.

~~**The solver is still a hill-climb, not an optimiser.**~~ **Closed 25 August 2026 (WP-2.3), and with it Phase 2.** `build/geometry_cp.py` states placement to CP-SAT over the same bay grid, dispatched from `geometry.solve(engine="auto")` with the hill-climb kept as fallback and cross-check. *(Two sessions built WP-2.3 independently against the same task text; the surviving engine is the merged, twice-audited one, and the deleted branch's findings are kept in `PLAN-OF-ACTION.md`'s WP-2.3 status block. The benchmark figures below are the deleted branch's own and are left as measured rather than restated for an engine that did not produce them.)* room minimums, the entrance front and the spanning passage are enforced constraints rather than scored preferences, and an infeasible brief now returns a deletion-minimised, named conflict set with no geometry written — *"a 2-bay, 20 x 25.96 ft single pile house cannot hold the dining-room, drawing-room and library at their stated minimums at once, and the lot allows no more bays."* Scored by `geometry.py`'s own functions, it beats the best of 800 heuristic candidates on both shipped plans and both briefs (13.1%, 14.8%, 23.6%, 9.7%), inside 60 s each; the Tidewater plan's transfer beams fell from 16 to 7.

The formulation the plan of action named had to be replaced on evidence, which is the finding worth carrying forward: loose rectangles whose areas sum to the footprint is a tiling stated as `sum(w*h) == W*H` over a dozen nonlinear products, and CP-SAT could not decide it on the spec Colonial in 240 s with four workers *while holding a hint that was itself a valid tiling*. Reading the slicing tree back off a heuristic layout makes tiling structural instead of arithmetic and leaves only the cut positions to solve — linear, and proven optimal in under a second. The heuristic proposes the topology; the solver proves the geometry. Optimality is therefore per topology rather than global, and the record says so. Two further findings: a plan's `exterior_walls` are aspirations rather than rectangle edges and cannot all be asserted at once, and the heuristic silently places the spec Colonial's dining room 26% below its band on every seed tried — OQ 54, and the heuristic is still the default engine. See `docs/reports/wp-2.3-the-real-solver.md`.

~~**The performance ceiling (OQ 28).**~~ **Fixed, later on 24 August 2026.** `plan_check.py`'s `_load()` re-imported `mcp_server/core.py` fresh on every `check()` call, defeating `core._data()`'s own cache; one `check()` executed plan_check 16 times and geometry 8. `build/modcache.py` now caches by realpath and every local `_mod`/`_load` delegates to it. `check()` 3.06 s → 0.31 s, `compose()` 30–40 s → 7–9 s, and the suite is back to a single run at roughly two minutes rather than twelve in three chunks. `tests/test_modcache.py` counts module executions so a reinstated local loader is caught. See `docs/reports/oq-28-module-cache.md`.

~~**The garage.**~~ **Closed, 24 August 2026 (WP-4.3).** The catalog side the package asked for is built: `rooms/garage.json`, `groupings/garage-and-hyphen.json` (8 internal rules, 14 `attaches_to` entries including one `forbidden` massing), and `compose.py`'s `attach_garage()`, which places the garage by the grouping's attachment and refuses with a stated reason where the grouping records none — never by adjacency. All four remaining living nodes were bound, taking the corpus to 58 `garage_strategy` bindings. The acceptance holds and is tested both ways: the composer cannot reproduce the garage-beside-primary-bedroom fatal, and a guard test asserts the hand-authored spec Colonial still trips it, so the acceptance cannot pass because the rule broke. One finding was left standing on purpose — the daylight-depth rule is unsatisfiable for a garage and probably for every non-habitable room, recorded as OQ 31. See `docs/reports/wp-4.3-the-garage.md`.

~~**Partis: still 39 of 132 styles.**~~ **Closed, 24 August 2026 (WP-4.5).** 21 partis, **129 of 132 styles native, 0 uncovered** — every buildable style with a canonical massing now has a diagram of its own. Nine new partis and 36 style-list placements into diagrams that already existed. The gap was also described wrongly here, and the correction is above: such a style was never refused, it was silently served another style's diagram, and WP-4.5 found the reason — nativity was worth `fit * 6` in the composer's ranking against 8 points for a serious finding, so a borrowed diagram routinely beat a native one. Adding nine partis for it to borrow from turned that into a Tidewater Georgian brief recommending an octagon; the weight is now 20. See `docs/reports/wp-4.5-partis-to-full-coverage.md`.

**Missing proportion packs (WP-4.6).** WP-4.1 produced the list; **COMPLETE: twenty-one packs, and every item of the list this corpus can support is built** as of 25 Aug 2026, chosen by measured leverage rather than by list order — `moorish-arch` (OQ 30's item, and the only gap that unblocked a node with no binding at all), `greek-doric` (which replaced a binding WP-4.1 had itself recorded as wrong), `adobe-module` (the gap four style nodes had already written into their own binding notes), `opening-pointed`, `opening-craftsman` and `trim-prairie` (both halves of PB-4's item), `dutch-gambrel` (whose central finding is that three style records give the gambrel's break point three different ways and none of them says from where), `balcony-gallery` (where the measurement disagreed with the item's own name — the corpus's most iron-heavy records are two Monterey variants whose balconies are wood), `stone-course` (the largest item the list held when measured, and it cannot use `brick-course`'s module because a rubble wall has no gauge), `facade-arcade` (never on the list at all; three packs in this package asked for it), `timber-panel`, `opening-mullioned`, `facade-gable`, `trim-sawn`, `octagon-geometry`, `facade-pavilion`, `jetty-overhang`, `facade-portada`, `facade-peristyle`, `corbel-course` and `facade-medieval-english`. **All six packs PLAN-OF-ACTION.md named as likely candidates are built.** The tranches' recurring finding is that list items collapse into each other once measured: the four-centred Tudor arch and the leaded casement were one window, four ornament items were one machine, and the French travée facade system and the mansard/dormer massing module were one system. Nothing remains that the corpus supports. The items it does not support are named in the report with a reason apiece -- the Baroque curved wall, strapwork and linenfold, the Romanesque foliate capital, Prairie art glass, Alpine carved timber and the cast-iron ornament half, and the symmetrical centreless multi-door facade -- each a pattern repertoire or an undocumented form that a proportion pack would have to fabricate numbers for. Several items are now named in the report as **not supportable from this corpus**, with the reason stated rather than left silent — the Baroque curved wall above all, where not one of 22 matching nodes gives a figure for an undulating elevation. **The count to watch is not nodes bound (132 of 132 since OQ 49's slot-scoped binding closed the last) but role coverage: 50 nodes with no opening-role pack, 46 with no facade-role pack.**

**The image layer: 322 records, 0 files.** Unchanged. Every record carries a shot spec, alt text and provenance requirements; none has been sourced. WP-4.4 wants ≥100 `sourced` or `generated` and zero `license: unknown`.

**Two known mechanism limitations surfaced by WP-4.2, patched node-by-node rather than fixed at the root.** A `hybridizes_with` edge drawn to carry one narrow aspect of a donor's practice transmits that donor's *entire* kit, because the cascade cannot partition a donor's bindings by which aspect the edge was for; and deep classical content reaches non-classical branches the same way. About 26 real merge problems across 129 kits, all fixed on the affected node, none at the mechanism level. A slot-scope allowlist on lineage edges would fix the class rather than the instances — a considered future pass, deliberately not attempted mid-fill.

**The code layer** remains advisory IRC model text, which is honest and should stay that way until a plan-development partner defines target jurisdictions.

---

## Part IV — What has yet to be started

**Standard details, design guidelines, modelling best practices.** All three are named deliverables in the brief and none exists as a document. The raw material is unusually rich — 262 recorded pack conflicts (resolution prose, not yet the planned ranked substitution structure), 209 faults with three-tier fixes, and now 2,100+ kit bindings — and much of a details library could be *generated* from the data rather than written, which would keep it from drifting.

~~**Export to the tools builders use.** Outputs are JSON and SVG. No DXF, no IFC, no Revit families, no PDF plan set. Until the IR can leave the system in a format a drafter opens, the platform promise is unfulfilled.~~ *(Done 25 Aug 2026 — WP-5.1: layered DXF per sheet and an IFC4 model, the record riding as XDATA/Psets, with a proven round-trip. Revit families and a PDF plan set remain unbuilt and unclaimed.)*

~~**A human interface for plans.** The taxonomy and the orders have interactive tools; the plan layers are CLI and MCP only. Given that the stated collaborators are plan development leads rather than engineers, this is a gap in the working relationship as much as in the software.~~ *(Done 25 Aug 2026 — WP-5.2: the eleven-surface workbench in `workbench/`.)*

~~**Drawing-to-record ingestion.** WP-2.1 transcribed 14 plans by hand. A pipeline from image or DXF to plan record — even a semi-manual transcription form — is what would let HABS drawings and a builder's existing catalogue flow into the critic at volume.~~ *(Done 25 Aug 2026 — WP-5.5: the Transcription surface and `build/ingest_dxf.py`.)*

**A cost and market layer.** `cost_saved` on faults and `cost_negative` on 32 of them is the seed. No cost model for a composed plan, no price comparison between candidates. Should wait for the partnership.

**Non-Western trunks (WP-4.7).** Five traditions are modelled. Japanese, Islamic, South Asian and African traditions would each be a peer trunk; the schema extends unchanged; `shotgun-house` and `cape-dutch` already point at ancestors the graph cannot name. Scope only, by design.

~~**Continuous integration.** The 304 tests exist; nothing runs them automatically.~~ *(Done — `.github/workflows/ci.yml` runs `check_all.py` and the workbench suite on every push; the count is 861 collected in `tests/`, 91 in the workbench server suite and 10 in the workbench app suite as of 26 Aug 2026 — the 762 stated here until then was stale by 33, counted before the 25 Aug merge.)*

---

## Part V — How it coheres, and what the sequence should be

The shape of the project has changed since the last review, and the change is worth naming precisely. In August the layers that were *done* encoded knowledge, the layers that were *begun* applied it to a single house, and the layers that were *unstarted* turned the result into a building. That is no longer the split. Knowledge is now not only encoded but *bound*: constraints execute, packs attach to styles, kits resolve through real ancestors. The single-house layers all run. The first passes of the back-end — walls, structure, roof, elevation — exist.

What is left divides cleanly into three kinds of work, and they are not equally urgent.

**The rigour gap.** ~~The solver composes by preference, not by proof.~~ *(Closed 25 Aug 2026 — WP-2.3.)* Placement is now CP-SAT: the record's declared facts are hard constraints, an infeasible plan returns a named conflict set beside the labelled least-bad drawing, and the one place the model softens — wall pins the flat footprint provably cannot co-hold, because `exterior_walls` speaks exposure in the massed house — is stated per pin in the result, never silent (OQ 40 records the massing-aware footprint as the structural fix). The system can now tell a builder *early* that a brief cannot be built in a parti, and why — the claim this paragraph said it could not make.

~~**The breadth gap.**~~ **Closed on the data, 25 August 2026.** Partis closed with WP-4.5 (129 of 132 native, 0 uncovered) and packs closed with **WP-4.6**: twenty-one built, and every item of WP-4.1's list this corpus can support is now built. The items it cannot support are named with a reason apiece rather than left silent — the Baroque curved wall first among them, where not one of 22 matching nodes gives a figure for an undulating elevation. Role coverage moved 68 → 49 with no opening-role pack and 68 → 46 with no facade-role pack. What is left of breadth is **unsourced images** (WP-4.4, environment-blocked — the proxy answers 403 to CONNECT for www.loc.gov) and the five source-blocked order questions.

**A new gap the breadth work exposed: the corpus does not know what it has verified.** This is OQ 51 and it is now the largest open item — see Part III. The pattern across the whole of WP-4.6 is worth stating once, because it will recur: **nine separate counts in this corpus changed when somebody read them instead of grepping them**, and every one had been believed. Twenty-four style-scoped tests became six. Twenty-two arch bindings became eight. A hundred and fifteen predicted fatals became zero. Seventeen octagon nodes became one. Twenty predicted address collisions became a hundred and thirty-nine. Four packs routing a member through the wrong slot became three — and that one was in the sentence arguing FOR a change, which is the most dangerous direction. Fifty-seven "mis-tagged placeholders" turned out to be fifty-five correct bands and two correct sets. **A regex proposes and reading disposes**, and the corpus is now large enough that this is a standing hazard rather than an anecdote.

**The last mile.** Details, guidelines, export, a workbench, ingestion. These turn a correct internal representation into something a builder and a plan-development lead can actually hold — and they are what the partnership, when it exists, will judge the system by. *(25 Aug: the workbench, the export and ingestion are done — WP-5.2, WP-5.1, WP-5.5; guidelines and cost remain.)*

So the sequence: ~~fix **OQ 28**~~ (done); ~~close **WP-4.3**~~ (done); ~~build **WP-2.3**, the real solver~~ (done — Phase 2 closed); ~~**WP-4.5** partis~~ (done); ~~**WP-4.6** packs~~ (done — Phase 4 is now complete except for images).

**An adversarial audit of this session's work ran on 25 August, and it is the reason several numbers above moved.** Five independent read-only auditors were pointed at the diff. What they found, in the order that matters: the tests guarding this session's two largest changes asserted that certain STRINGS appeared in the source files, so neutering the scope filter outright left 366 tests green and `egyptian-revival` receiving the entasis rule its own c04 forbids — those are behavioural now, and each was re-run against the mutation to prove it fails. `check_addresses.py` measured own bindings and the result was published as OQ 48's closure. `check_inheritance.py --slots` read the node's own kit where the resolver reads the cascade-resolved record, so two of the three published figures were wrong by one. Both new checks were wired into `check_all.py` without `--strict` and could not fail the build. `build.py` ran LAST, so three checkers validated the previous run's artefact. The engine dropped `calibrated_for` exactly as it had dropped `quantity`, so `stale_calibration` had been permanently `False`. `check_systems.py` still carried the tuple-key bug its sibling had fixed the same day. And 72 of the 162 editorial notes called categorical prose "a bare single figure", which would have sent the one researcher with library access to the wrong 82 records. **All of that is fixed and re-verified.** What is not fixed is recorded as OQ 52 and OQ 53 rather than half-done — chiefly that the elevation generator states chimney and dormer dimensions it never measured, and the fault corpus convicts both reference plans on them.

**What a new session should pick up, in order.**

1. **Work OQ 51's backlog — it is ruled, so this is authoring rather than deliberation.** The ruling of 25 August is *adjudicate first, flip second*: work the **249** role gaps whose pack's own `applies_to` does not name the node; where the inherited pack is right for that node, add the node to the pack's `applies_to`, which is the adjudication and moves the gap from unendorsed to endorsed; where it is wrong, bind the right pack on the node or scope the edge. When `unendorsed` approaches zero, add `inherits_packs` and make pack inheritance opt-in — at which point it is a safety net rather than a cliff that strands 287 gaps at once. `python3 build/check_inheritance.py --unendorsed` prints the work list grouped by pack, because adjudicating one pack settles every node under it: `opening-proportion` **24**, `storey-graduation` **23**, `facade-gable` **16**, `trim-classical` **14**, `timber-bay` **12**, `sash-light` **11**. (Re-measured 28 Aug 2026 by the WP-8.4 adversarial audit; the list published before it was the pre-WP-8.2 meter's and named `chambers-ionic` and `brick-course`, which the corrected attribution moved.) The accepted risk, stated rather than buried: wrong dimensions keep arriving while the backlog is worked, and that is tolerable only because all three numbers are pinned and cannot grow silently.
2. **WP-4.4's offline half.** Giving the 322 asset records their `provenance.building` names needs no network and is the step the package itself names as next; without it every harvest query degrades to a style-name search and one photograph ends up cited by many records.
3. **Phase 5, the last mile.** ~~Export (DXF/IFC), the plan workbench, generated guidelines and details, drawing ingestion. This is what a builder or a plan-development lead would actually judge the system by, and none of it exists.~~ *(25 Aug: WP-5.1, 5.2 and 5.5 shipped. What remains of the last mile is WP-5.3 — generated guidelines, the details library, modelling conventions — and the deliberately partner-gated cost layer, WP-5.4.)*

**Blocked on the environment, not on judgment:** OQ 7, OQ 8, OQ 9, OQ 10 and OQ 11 (order figures needing legible facsimiles), OQ 18's source half (162 editorial parameters — the note half is done and none is silent any more), and WP-4.4's harvest. `loc.gov`, `archive.org` and `hathitrust` all fail to connect from this container. **None of them may be closed from a secondary source or a modern redrawing**, which is how a guess gets laundered as `measured`.

That order keeps faith with the project's own founding discipline — validator before composer, spine before breadth, the drawing as a render of the data — and it means that at each step the system produces something more *like a house* rather than merely more data about houses. The aim was never a taxonomy. It was a language fluent enough that a production builder could speak it, and a house built in it would feel, to the people who live there, like it belongs. The grammar for that is written, and now it is bound to its vocabulary. The work now is breadth: the compiler proves what it composes, and the next thing it needs is more sentences it knows how to say.

---

### Appendix — Inventory as of 25 August 2026, verified

*Every figure below was produced by running the toolchain, not by reading the docs. `build/check_counts.py` fails the build when a number in this file, in `CLAUDE.md`, in `README.md` or in `docs/` disagrees with the data — run it with `--fix` to rewrite them.*

| Layer | Artefact | Count | Status |
|---|---|---|---|
| Alphabet | `elements/slots.json` | **97 slots / 8 groups (ontology 0.7.0)** | Complete; `arch` added at 0.6.0, `expressed_frame` at 0.7.0 |
| Alphabet | `massings/catalog.json` | 40, all with expansion logic | Complete |
| Alphabet | `rooms/` | 60, all with `style_variation` | Complete |
| Grammar | `proportions/` | **57 packs, 262 conflicts, 761 derived rules** | **WP-4.6 complete**; bound to **132 of 132** — but read OQ 51 |
| Grammar | rule addresses | own bindings **442 pairs, 0 collisions, 14 unjudged**; cascade **1,264 pairs, 9 collisions, 111 unjudged** | **OQ 48 closed at own scope only** — the cascade figure was never measured until the 25 Aug audit; both now ratcheted |
| Vocabulary | `styles/` | 164 nodes, 660 constraints | Complete; constraints executable |
| Vocabulary | constraints | 660 migrated, 61.5% of hard ones tested | Clears the ≥60% bar |
| Bindings | `kits/` | 159 files, 159 populated, **1,556 parameters** | Complete; **0 editorial parameters are silent** (OQ 18 note half) |
| Bindings | inheritance | **287 role gaps (38 endorsed, 10 declined, 249 not), 3,356 packs by descent** | **OQ 51 — RULED 25 Aug; measured and ratcheted, NOT fixed** |
| Solecisms | `faults/` | 209, all tested | Complete |
| Phrases | `groupings/`, `partis/` | 17 / 21 (129 of 132 native, 0 uncovered) | Complete — WP-4.5 |
| Critic | `plan_check.py` | 7 layers incl. constraints + elevation | Functional; code advisory only |
| Critic | `plans/reference/` | 14 transcribed (7 good, 7 bad) | Complete |
| Generator | `compose.py`, 2 briefs | 4 candidates per brief, lot-aware | Functional |
| Geometry | `geometry.py`, `render_plan.py` | coordinates + SVG | Functional; **the default engine, still a hill-climb** |
| Geometry | `geometry_cp.py` | CP-SAT over the bay grid, named conflict sets | Complete — the WP-2.3 engine that survived the 25 Aug merge (`build/solver.py` deleted; OQ 55's open-void guarantee lapsed with it) |
| Back-end | `structure.py`, `roof.py`, `elevation.py` | walls, section, roof plan, front elevation | Functional |
| Site | `site` on plan/brief schemas | lot, setbacks, bearing, slope | Functional |
| Interface | `mcp_server/` | 26 tools | Functional |
| Evidence | `assets/manifest.json` | **1777 wanted, 73 sourced** | 73 drawn from the packs, over 142 style nodes; the harvest is still environment-blocked |
| Back-end | `construction/` | 2 catalogs | Complete — WP-3.1's data side |
| Governance | `docs/open-questions/` | **103 entries, 33 open** | **A DIRECTORY since 28 Aug 2026 (WP-8.1)** — one file per question, filename == id; `docs/open-questions.md` is a generated index. Four id-collision conversion tables are in its README: ids 32–41 → 54–63, two blocks of 64–66, 72–83 → 78–89, 78–85 → 91–98, plus the work-package renumber 5.7–5.10 → 5.11–5.14 (OQ 90). **FIVE collisions now, and the fifth is why the numbers are FROZEN AT 99** (OQ 99, ruled on main 28 Aug): every question raised since is NAMED `oq/<slug>` and lives in `docs/open-questions/oq-<slug>.md`, because a slug is derived from its subject and cannot be issued twice. The directory and the slug are complementary — one turns a duplicate id into a conflict git REFUSES, the other stops the id being derivable from the working tree. **OQ 90 is closed at its third option**: a work-package number is a LABEL, not an identifier — two packages may share a number, no two may share a report filename, and `check_ids.py` enforces that |
| Provenance | `rule_append` | honoured, with the contributing ancestor recorded | **OQ 16 closed 25 Aug** — the code had shipped; only the label was open |
| Governance | `docs/reports/` | **22 package reports** | One per completed WP |
| Checks | `build/*.py` | **38 checkers** | All pass; incl. `check_counts`, `check_addresses`, `check_inheritance`, `check_ids`, `check_citations`, `check_division_guards`. `check_all` runs **41** — the 38 in its loop plus three appended suites, and the runner's own `len(results)` is the number to read |
| Checks | `tests/` | **1,195 tests, 44 files** | Plus the workbench server suite and 62 under `node --test`; one run, ~40 min; CI on GitHub Actions. These two rows are NOT policed by `check_counts.py`, which covers only counts derived from the corpus, so they go stale silently — `tests/test_counts_guard.py` pins the CLAUDE.md figures instead |

*The four numbers a new session should not trust without re-reading them: **132 of 132 bound** (counts a node's own array, not what it receives — OQ 51); **0 silent editorial parameters** (the notes say no source is recorded, which is not the same as sourced — OQ 18); **61.5% of hard constraints tested** (unchanged since 24 Aug and not re-verified here); and **1777 wanted, 73 sourced** (the 73 were DRAWN from the proportion packs, not fetched; the harvester still has never run against a reachable host).*
