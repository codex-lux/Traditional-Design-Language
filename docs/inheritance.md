# The kit-of-parts cascade

## The core move

A style is not a bag of parts. It is **a set of bindings and constraints on a universal set of slots**.

There are 82 slots in 8 groups, and they are the same 82 for every style in the taxonomy. Georgian does not own a cornice — it specifies one. Craftsman specifies a different one. Prairie forbids most of the classical apparatus group outright. The slots do not move.

This makes style inheritance work like a cascade. A child style inherits its parent's bindings and overrides selectively. Federal is Georgian with a handful of overrides and one addition. That is a far more compact and far more correct description than two independent parts lists, and it is what makes the system generative rather than merely catalogued.

## Resolution order

For any node, the cascade chain is the transitive closure of its `inherits_kit` edges, walked highest-weight-first, deduplicated, nearest ancestor first. It is precomputed as `_cascade` in `dist/taxonomy.json`.

```
tidewater-georgian
  → georgian-colonial-american
  → english-georgian
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

To resolve slot *S* for node *N*: take *N*'s own binding if `binding` is `specified` or `forbidden`; otherwise walk the chain and take the first specified binding found; otherwise the slot is `open`.

## Binding states

| `binding` | Meaning |
|---|---|
| `specified` | This node fixes the slot. Stops the cascade. |
| `inherited` | Explicitly deferred to the cascade. Documentation, not behaviour. |
| `open` | Unspecified. The default. Cascades; if nothing upstream specifies it, the slot is a free choice. |
| `forbidden` | This node prohibits the slot. Stops the cascade. Prairie forbids most classical apparatus; a Creole cottage forbids a centred entry door. |

`status` tracks editorial progress independently: `empty` → `stub` → `drafted` → `reviewed`.

## Slot groups

| Group | Slots | Note |
|---|---|---|
| Massing & Roof | 12 | Inherits along a different axis than ornament — see the massing catalog |
| Envelope & Wall | 11 | Includes `material_change_rule`, which prevents the brick-front-with-vinyl-returns pathology |
| Openings | 13 | Includes `garage_strategy`, for which no historical precedent exists |
| Classical Apparatus | 8 | Bound only within the classical stream; forbidden or open elsewhere |
| Porch & Threshold | 7 | `entry_sequence` is phenomenologically the most consequential slot in the kit |
| Interior Language | 15 | One coherent trim profile family per style — mixing families is the interior equivalent of mixing typefaces |
| Plan Logic | 8 | The deepest layer; `room_adjacency_rules` is the join point to the future room catalog |
| Site & Settlement | 7 | A style detached from its settlement pattern becomes a costume |

## Two slots that deserve special attention

**`garage_strategy`.** No traditional style has a historical answer, because none had to. The Ranch is the first American type organized around the automobile and it never solved the street elevation. Every traditional style built today inherits the problem. This slot is where a modern kit of parts has to author something genuinely new rather than retrieve it, and it should be `specified` on every contemporary buildable variant.

**`expansion_logic`** (on massings, not slots). How a type grows without breaking. Traditional types encode this — a Cape goes half → three-quarter → full; a telescope house adds a lower and narrower section; a connected farmstead adds a link. Formal styles almost never do. It is the property a generative system most needs and the one most often absent from style descriptions.

## Constraints

Constraints live on the style node, not in the kit, because they are relations between slots rather than values of one. Each has a `kind` (`co-occurrence`, `proportional`, `structural`, `climatic`, `code`, `cultural`) and a `severity` (`hard`, `soft`, `advisory`).

They are currently prose, deliberately written to be enforceable — with numbers and thresholds — pending a rule language:

> *Andalusian Spanish Revival:* window reveal depth not less than 8 inches. A flush window in a stucco wall destroys the expression of mass on which the entire idiom depends. **hard**

> *Charleston Georgian:* the piazza must face within 45 degrees of southwest. A piazza on the north flank is decoration and defeats the type. **hard**

> *Monterey Revival:* the balcony must run the full width of the principal elevation and be not less than 6 feet deep. **hard**

Hard constraints are what stop a generator from producing incoherent houses. They are also the most valuable thing in the dataset, and the part most worth arguing about with plan development leads.
