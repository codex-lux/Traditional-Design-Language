# Traditional Design Language — State of the Project

*Originally written 23 August 2026 against v0.6. **Revised 24 August 2026**, after Phases 0–3 closed and Phase 4 ran through WP-4.2. Everything below was verified by running the toolchain, not by reading the docs — every checker, the proportion engine selftest, both plan validations, both composer briefs, the geometry solver, and the full test suite were executed, and the numbers here are what they returned. Where a figure has moved since the 23 August review, the old figure is named so the direction of travel is visible.*

*Figures reconciled again late on 24 August 2026, after OQ 28 and WP-4.3 landed: 17 groupings (was 16), 31 open questions (was 30), and two rows the appendix had never carried — `construction/` and `docs/reports/`. Then **WP-2.3 closed Phase 2** the same day: `build/solver.py`, 330 tests across 17 files (was 291 across 14), 32 open questions, the suite one ~3-minute run. Part III's entries for OQ 28, the garage and the hill-climbing solver are struck through rather than deleted, in this document's own habit of leaving the old reading legible beside the new.*

*Reconciled a third time at the end of 24 August 2026, after **WP-4.5** closed the parti coverage gap and a full pass over the open questions. 21 partis (was 12) naming 129 of 132 styles with **0 uncovered** (was 93 uncovered); 60 rooms (was 58); **22 checks and 419 tests across 22 files** (was 22 and 344); **42 open questions, 8 of them open** — every one Lucas had ruled on is now executed. Three things in Part III are no longer true and are corrected rather than struck through, because each was a claim about behaviour rather than about a count: outdoor rooms are no longer dropped before placement (**OQ 33** — a courtyard is placed, dimensioned, excluded from the heated envelope and drawn open, and the ranges around it are laid out as a stated guillotine tree because the search cannot find a ring); a style with no native parti no longer borrows another style's diagram silently (**WP-4.5**, and `NATIVITY_W` 6 → 20); and a parti is no longer unchecked against the style it was written for (**OQ 37** — five of twenty-one were carrying fatal findings against their own native styles, so a Charleston brief came back with a centre-passage single pile; 21 of 21 compose now). Two findings from that pass are worth carrying forward as warnings rather than as history: **unjudged reported as evaluated-and-failed** was found twice in one package, which is this project's first discipline running backwards; and a rule that a correct plan structurally **cannot** satisfy — a landing required to reach a stair hall on its own storey, a butler's pantry required to touch a kitchen in another building — reads exactly like a plan that is wrong.*

---

## Part I — What this project is trying to be

### The aspiration

The brief for this work describes a role that does not design individual homes but designs *the system that produces them*: catalogs of rooms, groupings and massings as reusable components; rules of assembly that say what connects, what is constrained, and what produces a sound and coherent house; design intuition translated into structured, repeatable patterns; and, in effect, a new programming language for how homes are created.

What has been built answers that brief with a specific thesis, one that the original job description does not state but that the project now embodies and that should be named plainly because it is what makes the work distinctive rather than merely systematic. The thesis is that **a traditional house is a sentence in a language, and the language can be written down**. Elements are the alphabet. The proportioning system is the grammar. A style is a vocabulary and a set of bindings on that alphabet. A plan is a sentence; a grouping is a phrase; a parti is a sentence pattern. And — the layer most systems omit — there are *solecisms*: named, testable errors, the things that make a house read as wrong to someone fluent even when no rule on paper was broken. A system that can generate houses but cannot recognize its own solecisms will produce what Chomsky called colorless green ideas sleeping furiously: syntactically valid, and dead.

This matters beyond engineering. The point of encoding the language is not to automate the architect out of the room; it is to make fluency scalable, so that a production builder in the $400B market can build a house that *belongs* — to its place, its climate, its lineage — without a senior classicist standing over every drawing. The project is, in the terms Lucas uses elsewhere, a translation engine: it translates the accumulated wisdom of four centuries of building practice into a form a platform can execute and a human can still argue with.

### The parts and how they tie together

The system is a stack of nine layers. Reading it bottom-up, each layer is a precondition for the one above it, and the order in which they were built — spine first, then breadth — is itself one of the project's most important decisions.

**1. The alphabet.** Three style-independent catalogs that every style draws from but none owns. The *element ontology* (`elements/slots.json`) is 95 universal slots in 8 groups, from `roof_pitch` to `entry_sequence` to `garage_strategy`; a style does not own a cornice, it specifies one. The *massing catalog* (`massings/catalog.json`) is 40 volumetric skeletons, each carrying `expansion_logic` — how the type grows without breaking, the property a generative system most needs and formal style descriptions most often lack. The *room catalog* (`rooms/`) is 58 room types carrying the furniture that must fit with real clearances, daylight depth, typed directional adjacency, a six-rank privacy gradient, and servicing. These three are orthogonal to style by design; the test of the ontology is that adding a style should never require adding a slot.

**2. The grammar.** 36 proportion packs (`proportions/`) implemented as *functions, not tables*. Vignola's five orders are the spine; Palladio, Gibbs, Chambers and Benjamin are overlays carrying only their deltas; brick course, timber bay, sash light, storey graduation and log module are the non-classical equivalents, because most traditional buildings were proportioned from a material unit and not a column. Give a pack a module and a context and it emits a fully dimensioned assembly, member by member. Each pack states its own invariants as evaluable expressions and records 158 conflicts with building today — the 8-foot ceiling against a Corinthian entablature, the IGU that cannot take true divided lites — each with a severity and a ranked set of honest and dishonest substitutions. This is the project's most commercially defensible material: the knowledge that lives only in senior architects' heads, written down as executable rules.

**3. The vocabulary.** The style graph (`styles/`) — 164 taxa in four ranks (5 traditions, 27 families, 90 styles, 42 variants), spanning 700 BC to 2026, related by 476 typed lineage edges in a DAG rather than a tree. The single most important modelling decision in the whole project lives here: `descends_from` (actual transmission of practice) is a different edge from `references` (claimed ancestry), and only the former carries the kit-of-parts cascade. Greek Revival references Athens and descends from Federal carpentry; Colonial Revival references Georgian and descends from Beaux-Arts offices and the millwork catalog. A model that cannot express that gap will quietly produce wrong buildings. Each node also carries 624 massing affinities graded from `canonical` to `forbidden`, 660 enforceable constraints, 482 exemplars, and the binding of the node to its proportion packs.

**4. The bindings.** One kit file per family, style and variant (`kits/`, 159 files), materializing all 95 slots so that selecting a style resolves to a directory of specified, inherited, open or forbidden elements with a source column showing which ancestor each value came from. This is where a style becomes buildable rather than describable. The cascade walks `descends_from` and `regional_of` edges nearest-ancestor-first and — since WP-4.2 — splices each style-rank ancestor's own *family* into the chain alongside them; the `extends` operator lets a child add to a parent's binding rather than restate it.

**5. The solecisms.** The fault corpus (`faults/`) — 209 named errors, hung *element-first* off slots rather than styles, because the half-width shutter is wrong on every house that has shutters. Style enters through 846 exceptions (496 with numeric bounds): a Georgian five-foot portico is fatal by Craftsman rules and correct by its own. Every fault carries a cause with a named driver (exactly one of 209 is ignorance; the rest are stock sizes, trade sequences, catalog defaults and code minima), three tiers of fix (`right`, `cheap`, `dishonest`), two severity axes (how it reads, how it lives), and an executable `test`. The corpus returns *unjudged* for what it cannot evaluate, never *passed*.

**6. The phrase layer.** 17 groupings (`groupings/`, was 16 before WP-4.3 added `garage-and-hyphen`) — the hall-and-parlor pair, the centre-passage core, the entry sequence, the service core, the primary suite — with internal rules carrying severities and tests, and the join field `attaches_to`, which says how the grouping lands in a massing and at what fit. This is the scale people actually design at, and it is the hinge that makes rooms and skeletons composable. Twelve partis (`partis/`) then give canonical sentence patterns: topology and roles only, with dimensions always pulled from the room catalog so nothing can drift.

**7. The critic.** The plan schema and validator (`schema/plan.schema.json`, `build/plan_check.py`): a hand-authorable plan record checked across room, adjacency-and-privacy, grouping, fault, code, style-constraint and elevation layers. Built *before* the composer, because a composer needs a fitness function and this is it. Two worked examples ship — a deliberately ordinary production Colonial and the same corpus applied carefully — alongside a 14-plan reference corpus transcribed from real drawings.

**8. The generator.** The composer (`build/compose.py`) seeds from the partis native to the style, sizes rooms from the catalog, repairs against the validator until it stops improving, and returns four contrasting candidates ranked fatal-first then by style fidelity — each with what it trades away and a log of every assumption. Geometry (`build/geometry.py`, `render_plan.py`) then places rectangles on the parti's bay grid, both levels solved jointly for vertical alignment, counts every relaxation off the grid, and renders an SVG that is strictly a view of the data. Above it sit walls and structure (`structure.py`), roof (`roof.py`) and the elevation generator (`elevation.py`).

**9. The interfaces.** The MCP server (`mcp_server/`, 24 tools) is the real answer to "navigable by AI": not a file format but a server an agent consults mid-conversation, with progressive disclosure built in. Beside it, `dist/taxonomy.html` (the interactive phylogeny), `dist/orders.html` (the live order-drawing tool, running a JavaScript port of the engine checked to agree with the Python to 0.02 inches), `dist/taxonomy.json` for platform ingestion, and an agent digest. The image layer (`assets/manifest.json`, 322 records) is the evidence layer: good/bad pairs authored from the data before any image exists.

### The pipeline as a whole

Put the layers in motion and the intended flow is:

> **Brief** (area, bedrooms, lot, style) → **Style** resolves to a **kit** and its **constraints** and **packs** → native **partis** seed candidate **plans** assembled from **groupings** of **rooms** on a **massing** → the **validator** scores each against rooms, adjacency, faults, code, style constraints and the elevation → the **composer** repairs and ranks → **geometry** places and dimensions → **structure, roof and elevation** give it walls, a covering and a composed front → *[details, export — not yet built]* → **documents** a builder can price and permit.

The compiler metaphor is exact. The schemas are the language specification. The checkers are the linters. The validator is the type checker. The composer and geometry pass are the compiler front-end. As of the Phase 3 work, the first passes of the back-end exist too — the IR is now framed, roofed and given a front elevation. What remains unbuilt is the last mile: details, drawings in the formats a drafter opens, and a workbench a human can move a wall in. The MCP server is the runtime through which a human or agent drives the whole thing.

That is the shape of the vision. The rest of this document is about how much of it is standing.

---

## Part II — What is in place and functional

The following layers run clean, are schema-checked, and do what their documentation says. Each was executed during this review.

**The style graph and its validator.** `validate.py` passes: 164 nodes, schema-valid, all references resolve, inheritance edges form a DAG, one chronology warning that survives by design (Mexican Colonial contains Churrigueresque as a phase). The four-rank structure, the two-hierarchy separation, the typed edges and their cascade semantics are all settled and documented in `docs/model.md` and `docs/inheritance.md`.

**The element ontology and massing catalog.** 95 slots across 8 groups at ontology 0.5.0 (was 93 at 0.4.0 — WP-1.3 split `wall_thickness_expression` by trade), all 40 massings carrying expansion logic, both consumed correctly by every downstream layer.

**The proportion engine.** `selftest` resolves and dimensions all 46 packs with zero problems; `check_orders`, `check_modules` and `check_systems` pass with only explained warnings. Invariants are proved against the data, and the data encodes what the authorities *drew*, not what they said — Vignola's pedestal at 0.35 in Corinthian and Composite is the proof that the engine is honest.

**Proportion packs bound to the vocabulary — 131 of 132 buildable nodes** (was 5 at the last review, 129 after WP-4.1). WP-4.1 bound every style and variant except three where no pack in the library honestly fitted: `egyptian-revival` (trabeated, no arch), `moorish-andalusian` and `mudejar` (Islamic geometric setting-out). WP-4.6 built `moorish-arch` and the last two came off the named `DELIBERATELY_UNBOUND` allowlist in `check_pack_bindings.py --strict`, which is now one node — retiring an allowlist entry when the thing it excused is fixed is the point of having one. `egyptian-revival` stays, its reason untouched. The gap was recorded as OQ 29 rather than gamed, and the ~30 missing packs the exercise identified feed WP-4.6.

**The kit mechanism, and now the kits themselves — 159 of 159 populated** (was 3 of 132). WP-4.2 built the missing half of the mechanism first: family nodes had no kit files at all and carry no lineage edges, so a family could never appear in any cascade, and the plan's own instruction to "extend against the family" had nothing behind it. `build/build.py` now generates a kit for every family node and splices a style's own family into the chain via `member_of`, additively, without reordering any real lineage ancestor. Then all 129 remaining style/variant kits were filled in two sub-waves. Corpus-wide: 1,556 `specified`, 330 `extends`, 223 `forbidden` bindings. A variant now resolves through a chain in which every ancestor carries real content — `appalachian-log-house` reaches 34 populated levels.

**Executable style constraints — 660 of 660 migrated, 61.5% of hard constraints tested.** At the last review these were prose that nothing read. WP-1.1 gave them the fault corpus's own `expression`/`threshold`/`direction` pattern plus `scope` and a `one-of` direction, and `build/constraint_vocabulary.py` (87 named variables) is the shared namespace. 365 carry a test; 295 are honestly `scope: judgment` — the sources do not determine them, and the corpus says so rather than inventing a number. WP-1.2 wired the validator to read them.

**The fault corpus.** `check_faults.py` passes: 209 faults, every slot covered, every fault carrying a test.

**Rooms, groupings and partis.** `check_rooms.py` passes. All 58 rooms carry furniture with clearances, daylight, adjacency, privacy rank, and — better than the last review recorded — a `style_variation` block on every one of the 58. All 17 groupings carry `attaches_to`. The 12 partis name 39 styles between them as native.

**The plan validator.** Both example plans run and produce their documented results. Two-hop adjacency through a hall, rank-transparent circulation, the two-ended daylight correction, the `via` field, style constraints and the elevation layer are all implemented.

**The composer.** Both briefs run and return four ranked candidates with decision logs, trade-away statements and honest refusals. Lot-infeasible candidates are now dropped rather than merely outscored.

**Geometry, and composition within it.** WP-2.2 gave the solver compositional terms — entrance on the entrance front, principal rooms to the best aspect, service to the rear, the approach sequence — read from the style's own `composition_parti` and constraints rather than invented. The Tidewater plan now places its portico on the south wall with the principal rooms flanking the passage on the front.

**Walls, structure and storeys (WP-3.1).** Outside-to-outside footprints, wall lines, a bearing-line diagram, floor-to-floor heights from `storey-graduation`, and a section. No 2×10 spans 18 ft silently.

**The elevation generator (WP-3.2).** A Tidewater front elevation with five bays, a centred doorway composed to Gibbs, sash lights correct for the declared date, one head datum per storey, and a cornice regenerated as the style's own entablature reduction at the plan's real storey height. Its `measurements` feed an elevation layer in the validator. It evaluates 83 of the 177 applicable photograph-measurable faults — short of the acceptance text's named 100, disclosed rather than closed by fabricating data for faults it has no model for.

**Roof (WP-3.3).** Roof plan SVGs for both shipped plans, wing ridges stepping down, pitch inside the style band, chimneys satisfying the Tidewater constraint.

**The site layer (WP-2.4).** `site` objects on the plan and brief schemas — street bearing, setbacks, slope, prevailing wind, piazza bearing, party-wall condition. The composer caps bay count to the lot; the renderer draws the lot boundary, setback envelope and north arrow. This is what finally made the Charleston piazza and Pennsylvania bank-house constraints evaluable.

**The reference corpus (WP-2.1).** 14 of the Plan Examples transcribed into schema-valid plan records — 7 good, 7 bad — and scored. This was the experiment that tested whether the validator agrees with Lucas's eye.

**A real regression suite.** 304 tests across 16 files, each named for the finding it protects (was 291 across 14 before WP-4.3 and the OQ 28 fix added `test_garage.py` and `test_modcache.py`). `make check` is the single entry point, and since OQ 28 it completes in one run of about two minutes. This did not exist at the last review.

**The MCP server.** 24 tools registered, imports cleanly, `core.py` callable directly.

**Repository hygiene and documentation.** The repo is consolidated, git-tracked (24 commits), `_to_delete/` cleared, duplicate root files removed, every README count script-reproducible, and no doc references a path that does not exist.

Taken together: **Phases 0, 1, 2 and 3 are complete, and Phase 4 is complete through WP-4.3.** The language now has an alphabet, a grammar bound to its vocabulary, a full set of bindings, a critic that reads executable rules, a composer, a solver that composes, and a building with walls, a roof and a front.

---

## Part III — What is begun but needs to be fleshed out

~~**The solver is still a hill-climb, not an optimiser.**~~ **Closed, later on 24 August 2026 (WP-2.3), and with it Phase 2.** `build/solver.py` states placement to CP-SAT over the same bay grid: room minimums, the entrance front and the spanning passage are enforced constraints rather than scored preferences, and an infeasible brief now returns a deletion-minimised, named conflict set with no geometry written — *"a 2-bay, 20 x 25.96 ft single pile house cannot hold the dining-room, drawing-room and library at their stated minimums at once, and the lot allows no more bays."* Scored by `geometry.py`'s own functions, it beats the best of 800 heuristic candidates on both shipped plans and both briefs (13.1%, 14.8%, 23.6%, 9.7%), inside 60 s each; the Tidewater plan's transfer beams fell from 16 to 7.

The formulation the plan of action named had to be replaced on evidence, which is the finding worth carrying forward: loose rectangles whose areas sum to the footprint is a tiling stated as `sum(w*h) == W*H` over a dozen nonlinear products, and CP-SAT could not decide it on the spec Colonial in 240 s with four workers *while holding a hint that was itself a valid tiling*. Reading the slicing tree back off a heuristic layout makes tiling structural instead of arithmetic and leaves only the cut positions to solve — linear, and proven optimal in under a second. The heuristic proposes the topology; the solver proves the geometry. Optimality is therefore per topology rather than global, and the record says so. Two further findings: a plan's `exterior_walls` are aspirations rather than rectangle edges and cannot all be asserted at once, and the heuristic silently places the spec Colonial's dining room 26% below its band on every seed tried — OQ 32, and the heuristic is still the default engine. See `docs/reports/wp-2.3-real-solver.md`.

~~**The performance ceiling (OQ 28).**~~ **Fixed, later on 24 August 2026.** `plan_check.py`'s `_load()` re-imported `mcp_server/core.py` fresh on every `check()` call, defeating `core._data()`'s own cache; one `check()` executed plan_check 16 times and geometry 8. `build/modcache.py` now caches by realpath and every local `_mod`/`_load` delegates to it. `check()` 3.06 s → 0.31 s, `compose()` 30–40 s → 7–9 s, and the suite is back to a single run at roughly two minutes rather than twelve in three chunks. `tests/test_modcache.py` counts module executions so a reinstated local loader is caught. See `docs/reports/oq-28-module-cache.md`.

~~**The garage.**~~ **Closed, 24 August 2026 (WP-4.3).** The catalog side the package asked for is built: `rooms/garage.json`, `groupings/garage-and-hyphen.json` (8 internal rules, 14 `attaches_to` entries including one `forbidden` massing), and `compose.py`'s `attach_garage()`, which places the garage by the grouping's attachment and refuses with a stated reason where the grouping records none — never by adjacency. All four remaining living nodes were bound, taking the corpus to 58 `garage_strategy` bindings. The acceptance holds and is tested both ways: the composer cannot reproduce the garage-beside-primary-bedroom fatal, and a guard test asserts the hand-authored spec Colonial still trips it, so the acceptance cannot pass because the rule broke. One finding was left standing on purpose — the daylight-depth rule is unsatisfiable for a garage and probably for every non-habitable room, recorded as OQ 31. See `docs/reports/wp-4.3-the-garage.md`.

~~**Partis: still 39 of 132 styles.**~~ **Closed, 24 August 2026 (WP-4.5).** 21 partis, **129 of 132 styles native, 0 uncovered** — every buildable style with a canonical massing now has a diagram of its own. Nine new partis and 36 style-list placements into diagrams that already existed. The gap was also described wrongly here, and the correction is above: such a style was never refused, it was silently served another style's diagram, and WP-4.5 found the reason — nativity was worth `fit * 6` in the composer's ranking against 8 points for a serious finding, so a borrowed diagram routinely beat a native one. Adding nine partis for it to borrow from turned that into a Tidewater Georgian brief recommending an octagon; the weight is now 20. See `docs/reports/wp-4.5-partis-to-full-coverage.md`.

**Missing proportion packs (WP-4.6).** WP-4.1 produced the list; **nine of about thirty are built** as of 25 Aug 2026, chosen by measured leverage rather than by list order — `moorish-arch` (OQ 30's item, and the only gap that unblocked a node with no binding at all), `greek-doric` (which replaced a binding WP-4.1 had itself recorded as wrong), `adobe-module` (the gap four style nodes had already written into their own binding notes) `opening-pointed` (the opening half of the Gothic item; the facade half was measured and found already served on all four revival nodes) and both halves of PB-4's item — `opening-craftsman`, where the measured gap was seven nodes rather than the five the list estimated, and `trim-prairie`, which binds one node and exists to correct a wrong binding rather than to fill an empty role, in the same shape as `greek-doric` beside `benjamin-doric`. and `dutch-gambrel`, which the list scoped at 3 nodes and which reached 6, and whose central finding is that three style records give the gambrel's break point three different ways and none of them says from where. and `balcony-gallery`, where the measurement disagreed with the item's own name -- the corpus's most iron-heavy records are two Monterey variants whose balconies are wood, so the system is the applied deck and iron is one material it is made in. and `stone-course`, the largest item the list held when it was measured -- 60 nodes describe stone walling and 34 were thinly bound, and it cannot use `brick-course`'s module because a rubble wall has no gauge. **All six packs PLAN-OF-ACTION.md named as likely candidates are built.** Next by the same measurement: a half-timber infill panel module (31 nodes) and a gable geometry system (12 nodes, entirely missing). After those the tail is mostly ornament rather than proportion, plus four the tranches themselves raised — a four-centred Tudor arch system, a leaded-casement-and-mullion system, a medieval/pre-Palladian English facade system that turns out to be two existing list items seen from two sides, and Prairie rectilinear art glass. **The count to watch is not nodes bound (131 of 132, and it will not move much) but role coverage: 60 nodes with no opening-role pack, 67 with no facade-role pack.**

**The image layer: 322 records, 0 files.** Unchanged. Every record carries a shot spec, alt text and provenance requirements; none has been sourced. WP-4.4 wants ≥100 `sourced` or `generated` and zero `license: unknown`.

**Two known mechanism limitations surfaced by WP-4.2, patched node-by-node rather than fixed at the root.** A `hybridizes_with` edge drawn to carry one narrow aspect of a donor's practice transmits that donor's *entire* kit, because the cascade cannot partition a donor's bindings by which aspect the edge was for; and deep classical content reaches non-classical branches the same way. About 26 real merge problems across 129 kits, all fixed on the affected node, none at the mechanism level. A slot-scope allowlist on lineage edges would fix the class rather than the instances — a considered future pass, deliberately not attempted mid-fill.

**The code layer** remains advisory IRC model text, which is honest and should stay that way until a plan-development partner defines target jurisdictions.

---

## Part IV — What has yet to be started

**Standard details, design guidelines, modelling best practices.** All three are named deliverables in the brief and none exists as a document. The raw material is unusually rich — 158 pack conflicts with ranked substitutions, 209 faults with three-tier fixes, and now 2,100+ kit bindings — and much of a details library could be *generated* from the data rather than written, which would keep it from drifting.

**Export to the tools builders use.** Outputs are JSON and SVG. No DXF, no IFC, no Revit families, no PDF plan set. Until the IR can leave the system in a format a drafter opens, the platform promise is unfulfilled.

**A human interface for plans.** The taxonomy and the orders have interactive tools; the plan layers are CLI and MCP only. Given that the stated collaborators are plan development leads rather than engineers, this is a gap in the working relationship as much as in the software.

**Drawing-to-record ingestion.** WP-2.1 transcribed 14 plans by hand. A pipeline from image or DXF to plan record — even a semi-manual transcription form — is what would let HABS drawings and a builder's existing catalogue flow into the critic at volume.

**A cost and market layer.** `cost_saved` on faults and `cost_negative` on 32 of them is the seed. No cost model for a composed plan, no price comparison between candidates. Should wait for the partnership.

**Non-Western trunks (WP-4.7).** Five traditions are modelled. Japanese, Islamic, South Asian and African traditions would each be a peer trunk; the schema extends unchanged; `shotgun-house` and `cape-dutch` already point at ancestors the graph cannot name. Scope only, by design.

**Continuous integration.** The 304 tests exist; nothing runs them automatically.

---

## Part V — How it coheres, and what the sequence should be

The shape of the project has changed since the last review, and the change is worth naming precisely. In August the layers that were *done* encoded knowledge, the layers that were *begun* applied it to a single house, and the layers that were *unstarted* turned the result into a building. That is no longer the split. Knowledge is now not only encoded but *bound*: constraints execute, packs attach to styles, kits resolve through real ancestors. The single-house layers all run. The first passes of the back-end — walls, structure, roof, elevation — exist.

What is left divides cleanly into three kinds of work, and they are not equally urgent.

~~**The rigour gap.**~~ **Closed.** The solver composed by preference; now it proves. WP-2.3 landed the same day, and with it Phase 2 — see Part III. What the package could not do it says plainly rather than implying: optimality is per slicing topology, not global.

**The breadth gap.** Partis are closed (WP-4.5): 129 of 132 styles native, 0 uncovered. What remains is missing packs (WP-4.6, nine of about thirty built, the rest with their leverage measured in `docs/reports/wp-4.6-missing-proportion-packs.md`) and unsourced images (WP-4.4, **environment-blocked** — the proxy answers 403 to CONNECT for www.loc.gov, and `build/harvest_habs.py` is written and queued against the day it opens). WP-4.6 continues.

**The last mile.** Details, guidelines, export, a workbench, ingestion. These turn a correct internal representation into something a builder and a plan-development lead can actually hold — and they are what the partnership, when it exists, will judge the system by.

So the sequence: ~~fix **OQ 28**~~ (done — it pays back on every run after it); ~~close **WP-4.3**~~ (done — it killed a named fatal); ~~build **WP-2.3**, the real solver~~ (done — Phase 2 is closed); then take breadth — **WP-4.5** partis first since they gate composition, then **WP-4.6** packs and **WP-4.4** images; then Phase 5's last mile.

That order keeps faith with the project's own founding discipline — validator before composer, spine before breadth, the drawing as a render of the data — and it means that at each step the system produces something more *like a house* rather than merely more data about houses. The aim was never a taxonomy. It was a language fluent enough that a production builder could speak it, and a house built in it would feel, to the people who live there, like it belongs. The grammar for that is written, and now it is bound to its vocabulary. The work now is breadth: the compiler proves what it composes, and the next thing it needs is more sentences it knows how to say.

---

### Appendix — Inventory as of 24 August 2026, verified

| Layer | Artefact | Count | Status |
|---|---|---|---|
| Alphabet | `elements/slots.json` | 95 slots / 8 groups (ontology 0.5.0) | Complete |
| Alphabet | `massings/catalog.json` | 40, all with expansion logic | Complete |
| Alphabet | `rooms/` | **60**, all with `style_variation` | Complete (+`courtyard`, `overlook` in WP-4.5) |
| Grammar | `proportions/` | 46 packs, 207 conflicts | **Bound to 131 of 132** — but 60 nodes have no opening-role pack, 61 no facade-role pack (WP-4.6) |
| Vocabulary | `styles/` | 164 nodes, 476 edges, 660 constraints, 624 affinities, 482 exemplars | Complete; **constraints executable** |
| Vocabulary | constraints | 660 migrated, 365 tested, **61.5% of hard** | Clears the ≥60% bar |
| Bindings | `kits/` | **159 files, 159 populated** | Complete (was 3 of 132) |
| Solecisms | `faults/` | 209, 846 exceptions, all tested | Complete |
| Phrases | `groupings/`, `partis/` | 17 / **21** (**129 of 132 styles native, 0 uncovered**) | **Complete — WP-4.5** |
| Critic | `plan_check.py` | 7 layers incl. constraints + elevation | Functional; code advisory only |
| Critic | `plans/reference/` | 14 transcribed (7 good, 7 bad) | Complete |
| Generator | `compose.py`, 2 briefs | 4 candidates per brief, lot-aware | Functional |
| Geometry | `geometry.py`, `render_plan.py` | coordinates + SVG, compositional terms | Functional; the default engine, still a hill-climb |
| Geometry | `solver.py` (WP-2.3) | CP-SAT over the bay grid, named conflict sets | **Complete — beats best-of-800 by 10–24%** |
| Back-end | `structure.py`, `roof.py`, `elevation.py` | walls, section, roof plan, front elevation | Functional; elevation evaluates 83 faults |
| Site | `site` on plan/brief schemas | lot, setbacks, bearing, slope | Functional |
| Interface | `mcp_server/` | 24 tools | Functional |
| Interface | `dist/` | html × 2, json, agent.md | Current |
| Evidence | `assets/manifest.json` | 322 wanted, **0 sourced** | Records only — WP-4.4 |
| Back-end | `construction/` | 2 catalogs (wall assemblies, floor structure) | Complete — WP-3.1's data side |
| Governance | `docs/open-questions.md` | 35 items | OQ 20, 24, 28 answered; **27, 29, 30, 31, 32, 33, 34, 35 live** |
| Governance | `docs/reports/` | 17 package reports | One per completed WP, plus OQ 28 |
| Checks | `build/check_*.py`, `validate.py` | 10 checkers (+`check_partis.py`) | All pass |
| Checks | `tests/` | **344 tests, 18 files** | All pass; one run, ~4 min; no CI |
