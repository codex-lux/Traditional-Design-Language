# Open questions

Decisions deferred rather than made quietly. Two of these came from authoring the Georgian kit end to end, which was the point of doing it.

## From the taxonomy

1. **Should the 1877 sketching-tour styles cascade?** Colonial Revival is typed `references` toward Georgian because its transmission is photography and measured drawings. Shingle Style and Queen Anne Free Classic reach early New England building by exactly the same mechanism — the McKim, Mead, White and Bigelow tour of Marblehead, Salem, Newburyport and Portsmouth — and are typed `descends_from`, so they inherit seventeenth-century assembly. Those offices also employed carpenters who still knew the work, which is the counter-argument. Pick one reading and apply it to all three.
2. **Is `charleston-single-house` a style or a plan type?** It is a variant of Federal, its origin precedes Federal by sixty years, its floruit runs forty years past Federal's decline, and there is already a `charleston-single` massing.
3. **`log-vernacular-american` descends from `german-fachwerk` as a proxy** for Germanic *Blockbau*. A chinked hewn-log Appalachian house currently inherits half-timber-with-infill. A `germanic-blockbau` node fixes it.
4. **Vredeman de Vries's Antwerp engravings are typed both ways** — transmission in `elizabethan` and `jacobean`, quotation in `flemish-vernacular` and `dutch-urban-gable-house`. The model puts pattern books firmly on the transmission side.
5. **`shotgun-house` and `cape-dutch` have real ancestors the graph cannot point at** — Yoruba by way of Saint-Domingue, and Cape/Indonesian. Both gaps are recorded on the nodes. A sixth trunk fixes both and the schema extends to it unchanged.
6. **`mid-century-traditional` spans 1930–1975** and holds Neo-eclectic, which runs to 2000.

## From the proportion layer

7. **Palladio's Tuscan entablature is not dimensioned in the text** and the plate numerals are illegible in every reachable scan. Carried as a judgment rule with a range rather than invented members.
8. **Chambers's individual mouldings for Ionic, Corinthian and Composite** are engraved minute figures that every OCR renders as noise. They inherit from Vignola rather than being guessed. First thing to correct against a good facsimile.
9. **The Composite architrave and cornice corona** in Vignola are the weakest data in the order corpus — three transcriptions all say only "as the Corinthian, fewer and larger details, no brackets." Encoded as two fascias on that authority, with a three-fascia reading recorded as defensible.
10. **Benjamin's 1806 first edition** could not be reached in a legible scan. The packs encode the 1816 third edition and the 1830 *Practical House Carpenter*, and whether the 1806 column heights match is marked unverified rather than assumed.
11. **Palladio and Chambers overlays exist for all five orders; Gibbs and Benjamin do not cover every order** — Benjamin's Doric is Greek and is encoded standalone rather than as a delta, because encoding it as deltas on Vignola would be fiction.

## From authoring the Georgian kit

12. **`window_head` wants splitting.** A gauged brick jack arch is made by the mason, is structural, is cambered by opening/96, is four courses deep, and is laid on a centre before the wall closes. A moulded wood cap is made by the carpenter, is non-structural, and is nailed on afterwards. They share nothing but the opening. The same disease affects `wall_thickness_expression`, `window_surround` (whose correct masonry value is `none`, which is an answer and not an absence), and `corner_treatment` (which conflates the quoin, an order element, with the corner board, a trim element — and that conflation is why `facade-classical` was applying an 18-inch masonry rule to a 6-inch framed condition).
13. **The entablature is scattered across three slot groups** — `cornice` and `frieze` in Envelope, `crown` and `chair_rail` in Interior, `entablature` and `modillion_dentil` in Classical Apparatus. They are the same object at different scales and three of them derive from the same module.
14. **`balustrade` / `porch_rail` / `newel_balustrade`** are three slots, one assembly type, and one code conflict stated three times.
15. **`room_adjacency_rules` holds six rules of four different kinds in one flat set.** No schema change fixes this; it needs the room catalogue.
16. **`rule` still has no merge operator.** `extends` fixed three of four restatement cases. The fourth failed because `rule` is one string: a child adding a clause must replace the whole sentence or leave the resolved rule silent about its own change. `rule_append` is in the schema at 0.2.1 and is not yet used.
17. **Two mechanisms now exist for regional conditionality** — `applies_when.regions` on a parameter, and variant status on a child node — with no guidance on which to use. `service_zone_strategy` states the same Tidewater fact both ways.
18. **`kind: editorial` is carrying 166 of 402 parameters**, which is the migration defaulting honestly rather than claiming a `measured` it could not source. Probably half want a second pass with a source each.
19. **`determined_by` is declarative only.** `porch_ceiling` says it is determined by the order and the entablature, which is better than prose, but nothing resolves it because the schema does not say how the determination works.
20. **The cascade has been proved two levels deep, not twenty.** Georgian's chain is 20 nodes and 18 of them have empty kits. Every inheritance tested so far is one hop. The merge problems will get worse at three levels.
21. **Variant `op`s match on a free string.** A one-character difference turns a `replace` into an `add` and quietly duplicates a record. `check_kits.py` now errors on it, but the failure mode is inherent to the design.

## Structural, unresolved

22. **No date-conditional resolution.** `applies_when.date_range` now exists and is populated, but nothing selects on it. For a style spanning 1700–1800 — 12/12 to 9/6 to 6/6 sash, fanlights after 1780, butt hinges after 1775 — a resolved kit still has to present all the options rather than the ones current at a stated date.
23. **No room or room-grouping catalogue.** The largest remaining gap. `plan-logic` anticipates it and `room_adjacency_rules` is the join point.
24. **Constraints are prose with a kind and a severity.** They are written to be enforceable, with numbers, but they are not yet a rule language.
25. **No fault corpus yet.** 117 forbidden variants on one style is the seed of one, and the asset manifest already treats them as pairs, but a fault is a first-class object with its own id, cause, and cross-style applicability, and it does not exist yet.
