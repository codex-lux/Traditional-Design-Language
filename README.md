# Traditional Design Language

An evolutionary taxonomy of traditional architecture, built as a machine-readable graph rather than a document — and designed so that selecting a style resolves to a kit of parts.

**164 taxa · 476 lineage edges · 93 element slots · 40 massings · 58 rooms · 16 groupings · 36 executable proportion packs · 209 named faults · 322 specified images · 12 partis · 23 MCP tools**

**700 BC – AD 2026**

---

## What this is

Three layers that must not be collapsed into one another.

**1. The style graph** (`styles/`, `schema/style-node.schema.json`)
One JSON file per taxon. Four ranks — tradition → family → style → variant. Each node carries dates, geography, a description written to be read by a person, defining characteristics, diagnostic tells, disambiguation against its nearest neighbours, a proportional system, massing affinities, enforceable assembly constraints, real exemplars, and sources.

Nodes relate to each other in two independent ways, and the separation is the point:

- `member_of` — a strict single-parent hierarchy. This is the drawer a node lives in. It exists for browsing and nothing else.
- `lineage` — a directed acyclic graph with typed edges. This is actual descent, and nodes routinely have several parents.

**2. The element ontology** (`elements/slots.json`) and **massing catalog** (`massings/catalog.json`)
82 universal slots in 8 groups, plus 40 style-independent volumetric skeletons. These are orthogonal to the style graph. A style does not *own* a cornice; it *specifies* one. Adding a style should never require adding a slot — if it does, the ontology was incomplete, not the style exotic.

**3. The grammar** (`proportions/`, `build/proportion_engine.py`) — see `docs/proportion.md`
Element slots are the alphabet; a proportion pack is the syntax. 36 packs, and they are **functions, not tables**: give one a module and a context and it emits a fully dimensioned assembly, member by member, with profiles. Vignola's five orders are the spine; Palladio, Gibbs, Chambers and Benjamin are overlays carrying only their deltas. Brick course, timber bay, sash light, storey graduation and log are the non-classical equivalents, because most traditional buildings were proportioned from a material module and not from a column.

```
python3 build/proportion_engine.py compare vignola-doric gibbs-doric benjamin-doric --diameter 12
```

**4. The kit directories** (`kits/`)
One file per style and variant, materializing all 89 slots, ready to populate. This is the folder structure the project development work hangs off — `kits/tidewater-georgian.kit.json` is the address a design conversation resolves to once a client picks a style.

**Georgian Colonial is filled end to end** as the depth-first proof: 89 slots, 398 variant records of which **117 are `forbidden`**, 402 typed parameters, 30 slots with proportion-pack precedence, 5 code conflicts, 4 slots marked `invented` because no precedent exists. Tidewater Georgian is then written as a 21-slot override and resolves 65 of its 89 slots from the parent — `build/resolve_kit.py` prints the provenance with a source column.

**5. Rooms and groupings** (`rooms/`, `groupings/`) — see `docs/rooms.md`
58 style-independent room types with the furniture that has to fit and its clearances, typed directional adjacency, a privacy gradient, and daylight depth. Then 16 groupings — the middle scale people actually design at: a hall-and-parlor pair, a centre-passage core, an entry sequence, a service core, a primary suite. Each grouping's `attaches_to` says how it lands in a massing, which is the join that makes rooms and skeletons composable.

**6. The fault corpus** (`faults/`) — see `docs/faults.md`
209 named errors, **element-first**: they hang off slots, not styles, because the half-width shutter is wrong on every house that has shutters. All 93 slots covered. 846 style exceptions, 496 with numeric bounds — because a Georgian five-foot portico is a fatal fault by Craftsman rules and correct by its own. Every fault carries a `test`, so the corpus is executable: give it measurements from a photograph and it tells you which faults are present, which are clear, and which it could not judge.

Exactly one of 209 faults has `driver: ignorance`. The rest are stock sizes, trade sequences, catalog defaults and code minima — and 32 of them cost money to get wrong.

**7. The plan validator** (`schema/plan.schema.json`, `build/plan_check.py`, `plans/`) — see `docs/plans.md`
The critic, built before the composer, because a composer needs a fitness function and this is it. Reads a hand-authorable plan record and checks it across five layers — rooms, adjacency and privacy, groupings, faults, code and style. Two worked examples ship with it: a deliberately ordinary production Colonial (3 fatal) and the same corpus applied carefully (0 fatal).

**8. The composer** (`schema/brief.schema.json`, `partis/`, `build/compose.py`, `briefs/`) — see `docs/compose.md`
Seeds from 12 canonical partis native to the style, sizes every room from the room catalogue, repairs against the validator until it stops improving, and returns four contrasting candidates ranked by fatal findings then style fidelity — each with what it trades away and a log of every assumption it made.

**9. Geometry** (`build/geometry.py`, `build/render_plan.py`) — see `docs/geometry.md`
Bay-grid slicing with the relaxations counted, both levels solved together so vertical alignment is a constraint rather than an afterthought. Emits coordinates into the plan record and an SVG rendered from them. Produces valid, dimensioned, drawable plans with every compromise reported — not yet plans an architect would sign, and the doc says exactly where the gap is.

**10. The image layer** (`assets/manifest.json`) — see `docs/assets.md`
Format-agnostic records authored **before** the images exist. 292 wanted records, 136 of them good/bad pairs, each generated from a `forbidden` variant, an `invented` slot, a code conflict, or a proportion-pack assembly. Every record carries a shot spec and alt text written to be reasoned from, so the gap is visible, the shot list exists, and an agent can use the record while the file is still missing.

Built outputs live in `dist/`:

| File | For |
|---|---|
| `dist/taxonomy.html` | The interactive phylogeny. Self-contained; open it in a browser. |
| `dist/taxonomy.json` | The whole graph in one file, for platform or agent ingestion. |
| `dist/orders.html` | The live order-drawing tool. Every line is generated by the engine, not traced. |
| `mcp_server/` | **The MCP server — 17 tools.** This is the real answer to "navigable for AI": not a file format, a server. See `mcp_server/README.md`. |
| `dist/taxonomy.agent.md` | A 149 KB context-window digest — one block per node, for dropping into an LLM prompt. |

---

## Why a graph and not a tree

Architectural styles do not cladogenerate cleanly, and a folder tree can only encode one parent.

Shingle Style has at least four ancestors of comparable weight, arriving by different mechanisms — the American Queen Anne, Norman Shaw's Old English by publication, the emerging Colonial Revival by a documented 1877 sketching tour, and Richardson's Romanesque. Assign any one of them as *the* parent and the building stops making sense.

More importantly, styles inherit along **two different kinds of edge**, and conflating them is the single most common error in architectural taxonomy:

- `descends_from` — actual transmission of building practice. Builders trained by builders, pattern books bought by carpenters, trades carried by settlement.
- `references` — claimed ancestry. What a style *quotes* without ever having descended from it.

Greek Revival is the canonical case. It **references** Periclean Athens; no American builder had a line of transmission from Greece. It **descends from** Federal practice — the same carpenters, the same shops. And it **reacts against** Federal attenuation. The mechanism has a name and a date: Asher Benjamin published *The American Builder's Companion* in 1806 as a Federal manual and *The Architect, or Practical House Carpenter* in 1830 as a Grecian one. Same author, same audience, same trade, new plates.

Only `descends_from` and `regional_of` carry the kit-of-parts cascade. `references` does not — which is exactly right, because a Greek Revival house detailed with genuinely Greek construction would be an archaeological reconstruction, not a Greek Revival house.

Full edge semantics: `docs/model.md`.

---

## Why massing is not style

An American Foursquare can be dressed Craftsman, Colonial Revival, Prairie, or Mission with no change to the volume. Massing and ornament inherit along different axes.

The massing catalog is therefore a separate namespace, joined to styles through `massing_affinities` with an explicit strength — `canonical`, `common`, `possible`, `atypical`, `forbidden`. Every massing carries the property that formal styles most conspicuously lack and that a generative system most needs: **expansion logic**, the rule for how the type grows without breaking.

---

## Using it

**As a human.** Open `dist/taxonomy.html`. Click any bar to light its full ancestry and descent and open its record.

**As an agent.** Run the MCP server and call `tdl_overview` first. Without a server, load `dist/taxonomy.agent.md` for orientation and `dist/taxonomy.json` for the full graph, then open `kits/<id>.kit.json` as the working directory for everything downstream.

**As a platform.** `dist/taxonomy.json` is the ingestion artifact. Node ids are stable and never reused. The cascade resolution order for any node is precomputed as `_cascade` — nearest ancestor first.

---

## Extending it

```bash
python3 build/validate.py            # taxonomy: schema, references, acyclicity, chronology
python3 build/check_orders.py        # proportion packs: sums, invariants, overlay integrity
python3 build/check_kits.py          # kits: schema, slot ids, extends ancestry, units
python3 build/proportion_engine.py selftest
python3 build/build.py               # kits/, dist/taxonomy.json, dist/taxonomy.agent.md
python3 build/gen_assets.py          # assets/manifest.json
python3 build/render_html.py         # dist/taxonomy.html
python3 build/check_faults.py        # faults: schema, slot/style refs, test coverage
python3 build/check_rooms.py         # rooms and groupings: adjacency, privacy gradient, massing refs
python3 build/plan_check.py plans/spec-builder-colonial.json
python3 build/compose.py briefs/family-georgian.json
python3 build/render_orders.py       # dist/orders.html
```

To add a taxon: write `styles/<id>.json` against the schema, add the id to `build/registry.json`, run `validate.py` until clean, then `build.py`. The validator enforces that lineage targets resolve, that the `member_of` hierarchy is well-formed and acyclic, that inheritance edges form a DAG, that massing references exist, and that a node does not begin materially before an ancestor it descends from.

To populate a kit: edit `kits/<id>.kit.json`. Set a slot's `binding` to `specified`, list `variants`, add `parameters`, and move `status` from `empty` through `stub` → `drafted` → `reviewed`. Leave a slot alone and it inherits.

---

## What is deliberately not here yet

- **Compositional constraints in the geometry solver.** It satisfies adjacency; it does not compose an elevation. The entrance is not reliably on the entrance front and the ceremonial sequence is not yet a constraint — both are already stated in `composition_parti` and the style constraints, and neither is read.
- **The remaining 130 kits.** Georgian is filled; everything else is a real, versioned skeleton at `status: "empty"`. The point of doing one properly first was to break the schema before filling 130 files against a broken one, and it worked — the exercise produced kit schema 0.2.1 and seven new slots.
- **Formalized constraints.** Constraints are prose with a `kind` and a `severity`, written to be enforceable, but not yet a rule language.
- **Date-conditional resolution.** `applies_when.date_range` exists and is populated; nothing selects on it yet.
- **Non-Western traditions.** Five traditions are modelled, deep on the North American lineage and its European roots. Japanese, Islamic, South Asian, and African traditions would each be a peer trunk, and the schema extends to them without modification. Cape Dutch already carries an acknowledged gap: its Cape and Indonesian strand has no node to point at.

---

## Open questions, flagged rather than silently decided

The dataset was audited adversarially before release. Twelve concrete errors were found and fixed — broken cross-references, cascade flags that contradicted the model, two self-contradicting roof-pitch constraints, four exemplars that were duplicated, misdated, or wrongly attributed. What follows is what the audit surfaced as *judgement calls*, left open because they are design decisions rather than data errors.

**1. Should the 1877 sketching-tour styles cascade?**
Colonial Revival is typed `references` toward Georgian, because its transmission is photography and measured drawings rather than craft. But Shingle Style and Queen Anne Free Classic reach early New England building by exactly the same mechanism — the 1877 McKim, Mead, White and Bigelow tour of Marblehead, Salem, Newburyport and Portsmouth — and are currently typed `descends_from`, so they inherit seventeenth-century assembly. The counter-argument is that those offices also employed local carpenters who still knew the work. Pick one reading and apply it to all three.

**2. Is `charleston-single-house` a style or a plan type?**
It is currently a variant of Federal, but its origin (1720) precedes Federal by sixty years and its floruit runs forty years past Federal's decline. There is already a `charleston-single` massing. It probably belongs under `american-folk-vernacular` as a style, or should be carried entirely by the massing catalog.

**3. `log-vernacular-american` descends from `german-fachwerk` as a proxy.**
The intent is Germanic *Blockbau* horizontal-log craft; the target is half-timber-with-infill. A chinked hewn-log Appalachian house currently inherits the wrong construction system. A `germanic-blockbau` node would fix it.

**4. Vredeman de Vries's Antwerp engravings are typed both ways.**
`elizabethan` and `jacobean` call the prints transmission; `flemish-vernacular` and `dutch-urban-gable-house` call them quotation. The model puts pattern books firmly on the transmission side, which argues for the first reading.

**5. `shotgun-house` has an ancestor the graph cannot point at.**
The node's own description gives Vlach's Yoruba → Saint-Domingue → New Orleans transmission as the substance of the type, and there is no African or Caribbean trunk to target. The gap is now recorded on the node itself. `cape-dutch` carries the same problem from the other direction — its Cape and Indonesian strand has nowhere to attach.

**6. `mid-century-traditional` is doing too much work.**
It currently holds Storybook (1922–35, since moved out), Minimal Traditional (1935–50), Ranch (1945–70), and Neo-eclectic (1970–2000). The last of those extends 25 years past the family's own bounds.

## Known issues

- One chronology warning survives by design: `mexican-colonial` (1550) descends from `churrigueresque` (1700), because Churrigueresque is a phase *inside* Mexican Colonial's three-century span. The validator's chronology check cannot express a containment relationship.
- Confidence is recorded per node. Vernacular dating is genuinely uncertain and several nodes are honestly marked `medium` or `low`; `scandinavian-log-vernacular` in particular rests on a contested dating of the Nothnagle Log House.
- Roughly 90 of 299 North American exemplar rows were individually web-verified, weighted toward the obscure and the doubtful. The famous remainder was read but not separately checked.
- `distinguished_from` entries that compare a style against a *massing* use a `massing:` prefix, since the two live in separate namespaces.
