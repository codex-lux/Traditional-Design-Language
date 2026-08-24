# The kit-of-parts cascade

## The core move

A style is not a bag of parts. It is **a set of bindings and constraints on a universal set of slots**.

There are 95 slots in 8 groups, and they are the same 95 for every style in the taxonomy. Georgian does not own a cornice — it specifies one. Craftsman specifies a different one. Prairie forbids most of the classical apparatus group outright. The slots do not move.

This makes style inheritance work like a cascade. A child style inherits its parent's bindings and overrides selectively. Federal is Georgian with a handful of overrides and one addition. That is a far more compact and far more correct description than two independent parts lists, and it is what makes the system generative rather than merely catalogued.

## Resolution order

For any node, the cascade chain is the transitive closure of its `inherits_kit` edges, walked highest-weight-first, deduplicated, nearest ancestor first — **plus, since WP-4.2 (23 Aug 2026), each style-rank ancestor's own family**, spliced in immediately after that ancestor and before its further lineage ancestors. It is precomputed as `_cascade` in `dist/taxonomy.json` by `build/build.py`.

Family participation is a second, independent mechanism from lineage descent, not a special case of it. `member_of` (which family node a style or variant sits inside) and `lineage` (real, documented transmission of building practice) answer different questions — the README calls `member_of` "the drawer a node lives in... for browsing and nothing else" — and family nodes carry no `lineage` edges of their own at all, so before WP-4.2 a family could never appear in any `_cascade`, no matter how real the sharing it represents. `build/build.py`'s `family_of(i)` walks `member_of` upward from a style or variant to the nearest `rank: family` ancestor (through the parent style, for a variant, without adding that style a second time — it is already reached via lineage if it has a `descends_from`/`regional_of` edge back to it). Every time the lineage walk lands on a style-rank ancestor, that ancestor's own family is inserted right after it — nearest and most-shared first, most distant and most specific descent last:

```
tidewater-georgian
  → georgian-colonial-american        (real lineage: tidewater is a regional_of georgian)
  → american-colonial                 (georgian-colonial-american's own family, WP-4.2)
  → english-georgian                  (real lineage: georgian descends_from english-georgian)
  → english-classical                 (english-georgian's own family, WP-4.2)
  → english-palladian
  → palladian
  → italian-renaissance
  → roman-classical
  → greek-classical
  → italian-villa-vernacular
  → tuscan-vernacular
  → english-baroque
  → jacobean
  → elizabethan
  → tudor
  → english-gothic
  → norman-romanesque-english
  → english-medieval-timber-frame
  → flemish-vernacular
  → german-fachwerk
  → dutch-urban-gable-house
```

To resolve slot *S* for node *N*: take *N*'s own binding if `binding` is `specified` or `forbidden`; otherwise walk the chain (family entries included, in their spliced position) and take the first specified binding found; otherwise the slot is `open`. This is strictly additive to every pre-WP-4.2 resolution — a family entry only ever fills a slot no real ancestor already specified, since it is one more candidate in the walk, never reordered ahead of an already-present real ancestor.

## Binding states

| `binding` | Meaning |
|---|---|
| `specified` | This node fixes the slot. Stops the cascade. |
| `inherited` | Explicitly deferred to the cascade. Documentation, not behaviour. |
| `open` | Unspecified. The default. Cascades; if nothing upstream specifies it, the slot is a free choice. |
| `forbidden` | This node prohibits the slot. Stops the cascade. Prairie forbids most classical apparatus; a Creole cottage forbids a centred entry door. |

`status` tracks editorial progress independently: `empty` → `stub` → `drafted` → `reviewed`.

A fifth binding, `extends` (kit schema 0.2.0), stops the cascade like `specified` but merges rather than replaces: parameters merge by key (a child key replaces the inherited one outright), variants apply add/remove/replace ops matched on id, and most other fields replace-if-present-else-inherit. `rule` was the one exception — a single string, so a child adding a clause had to restate the whole sentence or leave the resolved rule silent about its own change — until `rule_append` (0.2.1) gave it a real merge operator (docs/open-questions.md #16, wired into `build/resolve_kit.py` in WP-1.3): a child's `rule_append` value joins onto the resolved rule as an additional sentence, and `resolve_kit.py --slot <id> --verbose` shows which ancestor's delta contributed which clause. See the merge-semantics docstring at the top of `build/resolve_kit.py` for the complete rule, including the ordering of `extends` deltas (farthest ancestor first, so the nearest wins) and how a dangling `extends` with no base to merge into is handled.

## Slot groups

| Group | Slots | Note |
|---|---|---|
| Massing & Roof | 13 | Inherits along a different axis than ornament — see the massing catalog |
| Envelope & Wall | 18 | Includes `material_change_rule`, which prevents the brick-front-with-vinyl-returns pathology, and — since WP-1.3 — the trade-split pairs `corner_quoin`/`corner_board`, `reveal_masonry`/`reveal_frame`, `wall_thickness_masonry`/`wall_thickness_frame` |
| Openings | 17 | Includes `garage_strategy`, for which no historical precedent exists, and the trade-split pairs `window_head_masonry`/`window_head_wood`, `window_surround_masonry`/`window_surround_wood` |
| Classical Apparatus | 8 | Bound only within the classical stream; forbidden or open elsewhere |
| Porch & Threshold | 7 | `entry_sequence` is phenomenologically the most consequential slot in the kit |
| Interior Language | 15 | One coherent trim profile family per style — mixing families is the interior equivalent of mixing typefaces |
| Plan Logic | 10 | The deepest layer; `room_adjacency_rules` is the join point to the room catalog (`rooms/`, since v0.6) |
| Site & Settlement | 7 | A style detached from its settlement pattern becomes a costume |

Four slot pairs — `window_head`, `corner_treatment` (now `corner_quoin`/`corner_board`), `window_surround`, and `wall_thickness_expression` (now `wall_thickness_masonry`/`wall_thickness_frame`) — were originally single slots that conflated two assemblies made by different trades, at different times, in different materials, with different failure modes (docs/open-questions.md #12). Three were split in ontology 0.3.0; the fourth, `wall_thickness_expression`, was the one no one had actually built yet, and was added in 0.5.0 (WP-1.3). Discriminate all of them with `construction_type`.

`cornice`, `frieze` and `modillion_dentil` (Envelope / Classical Apparatus) and `crown` and `chair_rail` (Interior) carry a `derives_from_module` field pointing at `entablature`, added in 0.5.0 (docs/open-questions.md #13). These five are the same object — an entablature's cornice — at different scales, and three of them are literally the same run; the cross-reference is not a regrouping, every id and existing kit binding stays valid, and it exists so a check or the proportion engine can eventually enforce that a chair rail's module actually derives from the same run as the exterior cornice rather than being independently invented (not yet wired into `check_kits.py` — the field exists and is populated, the enforcement is a reasonable follow-up, not yet built).

## Two slots that deserve special attention

**`garage_strategy`.** No traditional style has a historical answer, because none had to. The Ranch is the first American type organized around the automobile and it never solved the street elevation. Every traditional style built today inherits the problem. This slot is where a modern kit of parts has to author something genuinely new rather than retrieve it, and it should be `specified` on every contemporary buildable variant — as of WP-4.3 (24 Aug 2026) it is: 58 bindings across the corpus, every `status: "living"` style and variant covered, each flagged `invented: true` because that is what they are.

The authored answer itself lives in **`groupings/garage-and-hyphen.json`**: the garage as a dependency rather than a room of the house, set off the principal elevation and linked back to the service side, with the ridge at 60-80% of the main ridge and a 12-20 ft hyphen — proportions taken unchanged from `dependency-and-hyphen` rather than invented twice. Its `attaches_to` list is what the composer reads. The rule that matters most is a placement rule, not a dimension: **the garage is placed by the grouping's `attaches_to` against the massing, never by adjacency.** Placing by adjacency asks "what may this room touch?", and every locally plausible answer to that question is how a spec plan ends up with the bays against a bedroom wall. Placing by attachment asks where a dependency lands on this skeleton; the garage then has exactly one interior neighbour, a threshold room, and the bedroom question cannot arise. One consequence worth knowing when authoring: the hyphen is *not* a room in the plan record, because every service room in the catalogue that could model one carries a hard `must_adjoin` on the kitchen that a detached link cannot satisfy. The link is a property of the attachment. See `docs/reports/wp-4.3-the-garage.md`.

**`expansion_logic`** (on massings, not slots). How a type grows without breaking. Traditional types encode this — a Cape goes half → three-quarter → full; a telescope house adds a lower and narrower section; a connected farmstead adds a link. Formal styles almost never do. It is the property a generative system most needs and the one most often absent from style descriptions.

## Two mechanisms for regional conditionality, and when to use which

A single fact — "Tidewater Georgian's service dependencies sit 25 to 80 feet from the main block" — can be stated two structurally different ways, and the kit schema has offered both since 0.2.0 with no guidance on which to reach for. Georgian Colonial's own `service_zone_strategy` slot stated the Tidewater fact both ways at once until this was reconciled (docs/open-questions.md #17, WP-1.3):

**`applies_when.regions` on a parameter**, authored on the *parent* node. A single parameter's value differs by region; everything else about the slot — its binding, its other parameters, its rule — is shared. Georgian Colonial's `service_zone_strategy.parameters.strategy_new_england` / `strategy_mid_atlantic` / `strategy_low_country` are exactly this: one string value each, scoped to a region, with no New England, Mid-Atlantic, or South Carolina/Georgia variant node currently binding this slot to say anything different.

**A binding on a *variant* node**, `specified` or (more often, since a variant usually only refines a few slots) `extends`. The region's divergence is large enough that it already has — or deserves — its own identity: its own massing affinities, its own exemplars, its own name a client would actually choose. Tidewater Georgian is this: a real variant node with its own massing, its own 24-parameter kit override, its own place in `dist/taxonomy.json`. Once that node exists, restating one of its facts as an `applies_when.regions` parameter back on the parent is not a second, complementary way of saying the same thing — it is the same fact duplicated across two mechanisms that can drift apart, which is exactly what had started to happen: the parent's `strategy_tidewater` parameter and the variant's own `service_zone_strategy` binding were two independent places an editor could update the 25-80 ft figure without the other noticing.

**The ruling: use a variant node when enough diverges to deserve its own identity; use `applies_when.regions` when only a single parameter differs and everything else is shared.** This matches how the rest of the taxonomy already behaves — a variant exists because it is materially a different thing, not because one dimension changed. Concretely: if a variant node for the region already exists (check `member_of` on the family's other nodes, or `resolve_kit.chain_for`), state the fact on the variant's own kit binding and do not also carry it as an `applies_when.regions` parameter on the parent — remove the parameter if one is already there, the way `strategy_tidewater` was removed from `georgian-colonial-american.kit.json` in this reconciliation. If no variant node exists for the region and the divergence really is one parameter, `applies_when.regions` on the parent is correct and does not need a variant manufactured just to hold it — `strategy_new_england`, `strategy_mid_atlantic` and `strategy_low_country` are left exactly as they were, because none of Georgian Colonial's New England, Mid-Atlantic or low-country variant nodes currently binds `service_zone_strategy` to say anything different.

Nothing enforces this automatically — a future `check_kits.py` addition could flag a variant node whose own kit binding restates a fact its parent also carries as an `applies_when.regions` parameter for the same region, but that check does not exist yet. This section is the guidance a human (or an agent authoring a new region's kit) should follow by hand until then.

## Constraints

Constraints live on the style node, not in the kit, because they are relations between slots rather than values of one. Each has a `kind` (`co-occurrence`, `proportional`, `structural`, `climatic`, `code`, `cultural`) and a `severity` (`hard`, `soft`, `advisory`).

They are prose, deliberately written to be enforceable — with numbers and thresholds:

> *Andalusian Spanish Revival:* window reveal depth not less than 8 inches. A flush window in a stucco wall destroys the expression of mass on which the entire idiom depends. **hard**

> *Charleston Georgian:* the piazza must face within 45 degrees of southwest. A piazza on the north flank is decoration and defeats the type. **hard**

> *Monterey Revival:* the balcony must run the full width of the principal elevation and be not less than 6 feet deep. **hard**

Hard constraints are what stop a generator from producing incoherent houses. They are also the most valuable thing in the dataset, and the part most worth arguing about with plan development leads.

Since WP-1.1 (23 Aug 2026), a constraint can additionally carry a formal `test` — the fault corpus's own `expression`/`threshold`/`direction` pattern, extended with a `one-of` direction and a `scope` field — so the statement above is no longer only prose a person reads; it can be an expression the validator, composer or geometry solver evaluates directly, with the same "unjudged, not passed" honesty as everything else in this corpus when the sources don't determine a number. See **`docs/constraints.md`** for the full rule language, and note that this is a migration in progress, not a completed conversion: as of this writing 140 of the corpus's 660 constraints (the `english-classical` and `american-colonial` families, as a worked example) have been migrated to carry `id`/`scope`/`test`; the rest are still the prose-with-kind-and-severity shape described above, which remains a perfectly valid record — migration adds fields, it does not invalidate what came before it.


## Scoping an edge to the slots it was drawn for (OQ 36)

A lineage edge may carry a `slots` list. When it does, that edge transmits those slots and
nothing else. When it does not — which is almost every edge — it transmits the ancestor's whole
kit, which is what every edge did before and stays the default.

The problem it answers is specific to `hybridizes_with`. That edge is reticulation: a co-parent
of comparable weight, drawn because two traditions genuinely met. But the meeting is usually
about *one thing* — a porch treatment, a roof form, a decorative vocabulary, a way of ordering
a house from a catalogue — and the cascade had no way to say so, so the edge handed over the
donor's entire kit. WP-4.2 hit about twenty-six real merge problems that way across 129 kits and
patched every one at the node.

**Measured, 24 August 2026:** 36 nodes carry a kit-bearing `hybridizes_with` edge, and on 20 of
them the donor actually wins slots in the resolved kit — **123 slots corpus-wide**. That is the
size of the exposure, and it is why the mechanism was worth a schema version rather than another
node-level patch.

The worked case is `octagon-house hybridizes_with italianate-american`, whose own note is
unusually clear about what it means: *"The octagon is a plan thesis with no ornamental vocabulary
of its own, so nearly every built example wears Italianate dress."* Unscoped, that edge handed
the octagon 21 slots — including `roof_form`, `roof_pitch` and `height_proportion`, which are the
three things an octagon most certainly does not get from Italianate practice. Its roof is eight
hips meeting at a point because its plan is eight-sided; its proportion is Fowler's arithmetic
about wall length per enclosed area. Scoped to the dress, the edge now carries 18 slots and those
three resolve elsewhere.

**Two things to know before scoping an edge.**

First, **an edge's own note usually already says what it carries.** `monterey-colonial
hybridizes_with new-england-colonial` enumerates it outright — braced-frame carpentry, a
wood-shingled hip roof, milled architrave trim, double-hung sash, an interior stair and corridor
— and the scope is a transcription of that sentence. Where a note does not say, do not guess:
leave the edge unscoped and it behaves as it always has.

Second, and this is the honest limit of the mechanism: **scoping stops a wrong donor, it does not
supply a right one.** With the Italianate edge scoped, the octagon's `roof_form` falls through to
the next ancestor in the chain, which is `gothic-revival-american` — better, and still not the
eight-hipped roof the type actually has. That belongs in `kits/octagon-house.kit.json` as the
node's own binding. A scoped edge tells the cascade what NOT to take; what a style genuinely is
still has to be authored.
