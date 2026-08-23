# The graph model

## Ranks

| Rank | Count | What it is | Example |
|---|---|---|---|
| `tradition` | 5 | Civilizational trunk | Classical Mediterranean |
| `family` | 27 | A grouping sharing a generative logic | English Classical |
| `style` | 89 | The nameable thing a client selects | Georgian Colonial (American) |
| `variant` | 43 | The regional or period expression at which a kit is actually buildable | Tidewater Georgian |

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
