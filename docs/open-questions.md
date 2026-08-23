# Open questions

Decisions deferred rather than made quietly. Two of these came from authoring the Georgian kit end to end, which was the point of doing it.

Status legend: **OPEN** — awaiting a ruling. **RESOLVED** — ruled, with the ruling recorded inline and a pointer to where it took effect.

## From the taxonomy

1. **RESOLVED — Should the 1877 sketching-tour styles cascade?** Colonial Revival is typed `references` toward Georgian because its transmission is photography and measured drawings. Shingle Style and Queen Anne Free Classic reach early New England building by exactly the same mechanism — the McKim, Mead, White and Bigelow tour of Marblehead, Salem, Newburyport and Portsmouth — and are typed `descends_from`, so they inherit seventeenth-century assembly. Those offices also employed carpenters who still knew the work, which is the counter-argument. **Ruling: apply the `references` reading to all three** — transmission by photography and measured drawing, however skilled the office, is not the same mechanism as a trade lineage, and the model should not blur that distinction for three styles just because the drawings were good. Reflected in `styles/colonial-revival.json`, `styles/shingle-style.json`, `styles/queen-anne-free-classic.json`.

2. **RESOLVED — Is `charleston-single-house` a style or a plan type?** It is a variant of Federal, its origin precedes Federal by sixty years, its floruit runs forty years past Federal's decline, and there is already a `charleston-single` massing. **Ruling: style, under `american-folk-vernacular`** (folk-vernacular family) rather than a Federal variant or a massing-only concept — the piazza orientation constraint, the single-room-deep plan, and the party-wall condition are style facts, not merely volumetric ones, and a massing alone cannot carry `piazza_bearing_deg` as an enforceable constraint. Reflected in `styles/charleston-single-house.json` (`member_of`/`rank`).

3. **OPEN — `log-vernacular-american` descends from `german-fachwerk` as a proxy** for Germanic *Blockbau*. A chinked hewn-log Appalachian house currently inherits half-timber-with-infill. A `germanic-blockbau` node fixes it.

4. **OPEN — Vredeman de Vries's Antwerp engravings are typed both ways** — transmission in `elizabethan` and `jacobean`, quotation in `flemish-vernacular` and `dutch-urban-gable-house`. The model puts pattern books firmly on the transmission side.

5. **OPEN — `shotgun-house` and `cape-dutch` have real ancestors the graph cannot point at** — Yoruba by way of Saint-Domingue, and Cape/Indonesian. Both gaps are recorded on the nodes. A sixth trunk fixes both and the schema extends to it unchanged. Scoping note for a non-Western trunk more broadly: WP-4.7 (not yet run).

6. **OPEN — `mid-century-traditional` spans 1930–1975** and holds Neo-eclectic, which runs to 2000.

## From the proportion layer

7. **OPEN — Palladio's Tuscan entablature is not dimensioned in the text** and the plate numerals are illegible in every reachable scan. Carried as a judgment rule with a range rather than invented members.

8. **OPEN — Chambers's individual mouldings for Ionic, Corinthian and Composite** are engraved minute figures that every OCR renders as noise. They inherit from Vignola rather than being guessed. First thing to correct against a good facsimile.

9. **OPEN — The Composite architrave and cornice corona** in Vignola are the weakest data in the order corpus — three transcriptions all say only "as the Corinthian, fewer and larger details, no brackets." Encoded as two fascias on that authority, with a three-fascia reading recorded as defensible.

10. **OPEN — Benjamin's 1806 first edition** could not be reached in a legible scan. The packs encode the 1816 third edition and the 1830 *Practical House Carpenter*, and whether the 1806 column heights match is marked unverified rather than assumed.

11. **OPEN — Palladio and Chambers overlays exist for all five orders; Gibbs and Benjamin do not cover every order** — Benjamin's Doric is Greek and is encoded standalone rather than as a delta, because encoding it as deltas on Vignola would be fiction.

## From authoring the Georgian kit

12. **RESOLVED — `window_head` wants splitting.** A gauged brick jack arch is made by the mason, is structural, is cambered by opening/96, is four courses deep, and is laid on a centre before the wall closes. A moulded wood cap is made by the carpenter, is non-structural, and is nailed on afterwards. They share nothing but the opening. The same disease affects `wall_thickness_expression`, `window_surround` (whose correct masonry value is `none`, which is an answer and not an absence), and `corner_treatment` (which conflates the quoin, an order element, with the corner board, a trim element — and that conflation is why `facade-classical` was applying an 18-inch masonry rule to a 6-inch framed condition). **Ruling: split all four by trade.** `window_head` → `window_head_masonry` (jack arch / lintel, structural) + `window_head_carpentry` (moulded cap, non-structural); `corner_treatment` → `corner_treatment_masonry` (quoin, an order element) + `corner_treatment_carpentry` (corner board, a trim element); `window_surround` keeps its id and gains `none` as a legitimate value for bare masonry openings; `wall_thickness_expression` splits by construction trade. Executed in WP-1.3 — ontology bumped to 0.5.0, three populated kits migrated by script, old ids `deprecated_in_favour_of` the split ones rather than removed.

13. **RESOLVED — The entablature is scattered across three slot groups** — `cornice` and `frieze` in Envelope, `crown` and `chair_rail` in Interior, `entablature` and `modillion_dentil` in Classical Apparatus. They are the same object at different scales and three of them derive from the same module. **Ruling: add `derives_from_module` cross-references between the six slots; do not regroup them.** The lighter-touch option — every existing id and downstream kit binding stays valid, and the proportion engine gains a cross-reference it can use to enforce that a chair rail's module actually derives from the same run as the exterior cornice, rather than being independently invented. Executed in WP-1.3.

14. **OPEN — `balustrade` / `porch_rail` / `newel_balustrade`** are three slots, one assembly type, and one code conflict stated three times.

15. **OPEN — `room_adjacency_rules` holds six rules of four different kinds in one flat set.** No schema change fixes this; it needs the room catalogue. (The room catalogue now exists — `rooms/`, 58 types — so this is unblocked and should be revisited; not yet done.)

16. **IN PROGRESS — `rule` still has no merge operator.** `extends` fixed three of four restatement cases. The fourth failed because `rule` is one string: a child adding a clause must replace the whole sentence or leave the resolved rule silent about its own change. `rule_append` is in the schema at 0.2.1 and is not yet used. This did not need a ruling — the operator's shape is already declared in the schema — so it is being implemented directly in WP-1.3 rather than put to a decision: a child's `rule_append` value is joined onto the resolved parent rule as an additional sentence, with the join point marked so `resolve_kit.py`'s provenance output can still show which ancestor contributed which clause.

17. **RESOLVED — Two mechanisms now exist for regional conditionality** — `applies_when.regions` on a parameter, and variant status on a child node — with no guidance on which to use. `service_zone_strategy` states the same Tidewater fact both ways. **Ruling: use a variant node when enough diverges to deserve its own identity (massing, program, name, exemplars); use `applies_when.regions` when only a single parameter differs and everything else is shared.** This matches how the rest of the taxonomy already behaves — a variant exists because it is materially a different thing, not because one dimension changed. Guidance written into `docs/inheritance.md` in WP-1.3; `service_zone_strategy` reconciled to state the Tidewater fact once, the way the ruling now specifies.

18. **OPEN — `kind: editorial` is carrying 166 of 402 parameters** (417 as of the 23 Aug count), which is the migration defaulting honestly rather than claiming a `measured` it could not source. Probably half want a second pass with a source each.

19. **OPEN — `determined_by` is declarative only.** `porch_ceiling` says it is determined by the order and the entablature, which is better than prose, but nothing resolves it because the schema does not say how the determination works.

20. **OPEN, but now a test rather than a decision — The cascade has been proved two levels deep, not twenty.** Georgian's chain is 20 nodes and 18 of them have empty kits. Every inheritance tested so far is one hop. The merge problems will get worse at three levels. WP-1.3 exercises this at the depth of the current three populated kits (Georgian Colonial → Tidewater Georgian / English Georgian, two levels); the full three-level test that WP-4.2 is written to surface (family → style → variant, `extends` throughout) has not run yet because Phase 4's kit-fill is deliberately deferred until the constraint layer (Phase 1) has landed and been reviewed.

21. **OPEN — Variant `op`s match on a free string.** A one-character difference turns a `replace` into an `add` and quietly duplicates a record. `check_kits.py` now errors on it, but the failure mode is inherent to the design.

## Structural, unresolved

22. **OPEN — No date-conditional resolution.** `applies_when.date_range` now exists and is populated, but nothing selects on it. For a style spanning 1700–1800 — 12/12 to 9/6 to 6/6 sash, fanlights after 1780, butt hinges after 1775 — a resolved kit still has to present all the options rather than the ones current at a stated date. Targeted by WP-1.3 (a `date` parameter on `resolve_kit`).

23. **RESOLVED — No room or room-grouping catalogue.** This was the largest remaining gap as of the original drafting of this list. It is no longer a gap: `rooms/` (58 style-independent room types with furniture, clearances, typed directional adjacency, a six-rank privacy gradient, daylight depth) and `groupings/` (16 groupings with `attaches_to`) both exist and pass `check_rooms.py`. `room_adjacency_rules` as the join point is item 15 above, still open on its own terms.

24. **RESOLVED — Constraints are prose with a kind and a severity.** They are written to be enforceable, with numbers, but they were not yet a rule language. **Ruling: reuse the fault corpus's `test` object pattern** (`expression` / `threshold` / `direction`), extended with `within` / `one-of` / `equals` directions, a `scope` field (`plan` / `elevation` / `site` / `section` / `judgment`), and a named variable vocabulary — rather than invent a separate rule language for constraints. A constraint the sources do not determine numerically gets `scope: judgment` and no test, the same honesty as judgment slots. Executed in WP-1.1: `constraint.schema.json`, `build/constraint_vocabulary.py`, `build/check_constraints.py`, and the migration of all 660 constraints. See `docs/constraints.md`.

25. **RESOLVED — No fault corpus yet.** This was the seed-stage note as of the original drafting. It is no longer a gap: `faults/` now holds 209 named, tested faults with 846 style exceptions (496 numerically bounded), full slot coverage (93 of 93), and a `test` object on every one. `check_faults.py` is green.

## From writing the behaviour-test suite (WP-0.3)

26. **OPEN — Should the `EQUIVALENT` room-type alias groups in `build/plan_check.py` be documented?** Seven groups treat related room types as interchangeable for adjacency purposes (e.g. `{"entrance-hall", "vestibule", "stair-hall"}`) — real, load-bearing logic that changed how a test fixture had to be built during WP-0.3 (a "stair hall standing between two rooms" fixture accidentally satisfied an entrance-hall adjacency rule through aliasing rather than through the two-hop-through-circulation mechanism actually under test). It exists only as an unexplained list in the source; `docs/plans.md` documents the two-hop widening and the `via` intermediary by name but not this. Should it be documented the same way, and are the seven groups as currently drawn the right ones?
