# The graph model

## Ranks

| Rank | Count | What it is | Example |
|---|---|---|---|
| `tradition` | 5 | Civilizational trunk | Classical Mediterranean |
| `family` | 27 | A grouping sharing a generative logic | English Classical |
| `style` | 90 | The nameable thing a client selects | Georgian Colonial (American) |
| `variant` | 42 | The regional or period expression at which a kit is actually buildable | Tidewater Georgian |

The variant level is where the operational value lives. "Georgian" is an abstraction. "Tidewater Georgian in brick, 1740–75" is something you can build, and it differs from New England Georgian in cladding, chimney position, roof pitch, window head, plan depth, and ceiling height — all of which are climatic and all of which are quantifiable.

## The two hierarchies

**`member_of`** is a strict single-parent tree. Traditions have `null`. It exists for browsing, for the left-hand grouping in the chart, and for nothing else. It does not carry inheritance.

**`lineage`** is the real structure: a directed acyclic graph with typed, weighted edges. Multiple parents are normal.

## Edge types

| Type | Meaning | Carries the kit cascade |
|---|---|---|
| `descends_from` | Actual transmission of building practice — builders, pattern books, settlement, trade knowledge | Yes |
| `regional_of` | A variant to its parent style | Yes |
| `hybridizes_with` | Reticulation; a co-parent of comparable weight | Where the kit genuinely blends |
| `references` | Claimed or quoted ancestry the style imitates without descending from | **No** |
| `reacts_against` | Defined by inversion of a predecessor | **No** |
| `revives` | Deliberate resurrection after a gap | **No** |

Each edge carries a `weight` (0–1) for cascade precedence and rendering, an `inherits_kit` flag, and an optional `note` recording the actual mechanism of transmission. The notes are where most of the intellectual content of the graph lives — read a few.

### Why `references` must be a separate edge

A revival style is not its model. Colonial Revival descends from Beaux-Arts professional practice, from the architectural photography and measured-drawing culture of the 1890s onward, and from the millwork catalog. It references Georgian and Federal building. If you let the `references` edge carry the kit cascade, a Colonial Revival house inherits eighteenth-century construction — hand-planed muntins, true divided lites, plaster on riven lath — which is not what Colonial Revival is and not what anyone is asking for when they select it.

The gap between what a style claims and where it comes from is not a defect in the taxonomy. It is the most important fact about the entire eclectic revival period, and a data model that cannot express it will quietly produce wrong buildings.

### Double edges are legitimate

A style commonly both descends from and reacts against the same predecessor. English Palladian reacts against English Baroque and inherits its trades. French Neoclassical repudiates the Baroque surface while continuing its plan types and stonecutting. Model both.

## Chronology

`period` carries `origin` (first appearance), `floruit_start` / `floruit_end` (the period of characteristic production), `decline_end` (last meaningful vernacular production), and `revival_periods[]`. A revival period may name a `revival_node` — the node that *is* that revival, modelled separately.

Years are integers; BC is negative. `circa` is true on nearly every node, and should be: these ranges are scholarly conventions, not facts.

## Invariants the validator enforces

- Every file's `id` matches its filename; ids are unique
- `member_of` resolves, and points to a strictly higher rank
- The `member_of` hierarchy is acyclic
- Every `lineage.target` resolves; no self-edges
- Inheritance edges (`descends_from`, `regional_of`, `hybridizes_with`, `revives`) form a DAG — no cycles
- Every `massing_affinities.massing` exists in the catalog; every `kit` key is a real slot
- `floruit_start <= floruit_end`
- Warning where a node begins more than 25 years before an ancestor it descends from

## Ornament is rationed, not distributed (OQ 50)

Wherever a node in this corpus states a rule about *where* ornament goes, it states
**concentration**: ornament confined to named places — a doorcase, a portada, a wall head, a gable
face, a porch — with a plain field around it that is a designed element in its own right, and often
with a stated minimum size. Twenty-six of the 132 buildable nodes say so, across at least nine
traditions that share no vocabulary: Iberian and colonial Spanish, English Georgian and Palladian,
Victorian American, Scottish, Swiss, Norman, French, Mexican.

Eight of them condemn the opposite in their own words. Even distribution "destroys the hierarchy
that carries the composition"; it "converts the complex into" another style; it is "a revival
misreading"; it "destroys the style outright". **No node requires ornament to be evenly
distributed.**

There is exactly one control case, and it is named by the tradition that most opposes it.
`spanish-plateresque` says "Italian work regulates the whole facade by an order and distributes
ornament across it", and `italian-renaissance`'s own bay rhythm agrees — "even, additive and
non-hierarchical: five to eleven identical bays across a front". That is the pattern's boundary
rather than a counter-example to it.

**What this does not say.** The other 106 nodes are mostly silent, and a node that says nothing about
where ornament goes has not voted. The claim is conditional and should be stated that way. Whether it
should become a fault — `evenly-distributed-ornament`, with `italian-renaissance` exempted — is
open; the fault layer would first need a way to see ornament *zones*, which `elevation.py` does not
model.

## A room is not sized by its furniture (OQ 92, ruled 27 August 2026)

The room catalogue carries 278 furniture items with real footprints and clearances, and 60
`critical_dimension` notes — 22 of them stating an arithmetic that derives a minimum from the
furniture, such as the dining room's *"A table for eight is 40 in wide; a chair pushed back
needs 36 in; passing behind it needs another 18 in. That is 40 + 2(36) + 2(18) = 148 in, so
12 ft 4 in is the absolute floor."* It is tempting to make that arithmetic the room's size.

**It is refused.** Lucas's ruling, in his words: *"room sizing should not be furniture driven —
that's the tail wagging the dog — however furniture arrangements that suit the program / room
name and room size should be placed accordingly."*

So the direction of authority is fixed and runs one way:

- **A room's size comes from its programme and its catalogue band**, and from the author's
  declaration in the plan record. `plan_check`'s furniture layer keeps checking that the
  furniture *fits* the room; it never sizes the room to the furniture.
- **The furniture is arranged into the room as given** — against the walls the room's own
  words name, around the doors and windows the placement put there.

The `critical_dimension` prose stays prose. It is a designer's argument for why a band's floor
is where it is, addressed to a person, and turning it into a constraint would let a derived
number overrule an authored one — the same error class the corpus names in OQ 52.

The one arrangement rule this admits is stated by the corpus rather than inferred:
`needs_uninterrupted_wall_ft` on a furniture item, authored only where the item's own `note`
states the run in words, with the number beside the sentence so the two cannot drift. FIVE items
carry it: the dining room's sideboard, the bedroom's desk, the kitchen's range, the living room's
sofa and the study's camera wall. This paragraph read "One item carries it today" until WP-11.3 --
WP-7.4 had corrected the count to five and neither this file nor `schema/room.schema.json` was
updated, which is the class WP-6.4 exists to name.
