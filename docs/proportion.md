# The grammar layer

Element slots give a style its alphabet. A proportion pack gives it syntax. A style with no pack bound has a vocabulary and no grammar, which is exactly the condition most contemporary traditional building is in.

## A pack is a function

The classical orders are a parametric system that predates CAD by two thousand years. Vignola in 1562 gives every dimension in parts of a module; choose Tuscan and a module, and roughly two hundred subordinate dimensions follow deterministically. That is a function, and it is implemented as one.

```
python3 build/proportion_engine.py list
python3 build/proportion_engine.py show gibbs-ionic --module 5 --rules --ceiling 108
python3 build/proportion_engine.py compare vignola-doric gibbs-doric benjamin-doric --diameter 12
python3 build/proportion_engine.py selftest
```

47 packs, in four kinds:

| Kind | Packs | Module |
|---|---|---|
| `order-system` | 5 Vignola orders, 19 authority overlays, Greek Doric, the Moorish arch system | the column semidiameter — or, for Palladio, the whole diameter; for the Moorish system, the generating square's side, because that system has no column proportion at all |
| `module-system` | brick course, timber bay, sash light, storey graduation, log, adobe, Dutch gambrel, the applied balcony, stone course | a material unit — for adobe, one brick laid as a header, which is why a mass wall's thickness comes in whole bricks; for the gambrel, the half-span, which is the one module in the set you cannot hold; for the balcony, the rail bay, and the deck's DEPTH is deliberately not derived from it, because depth follows how the deck is carried; for stone, one DRESSED stone, because a rubble wall has no gauge and only the quoins, jambs and lintels have a dimension before they are laid |
| `facade-system` | classical, picturesque | the bay |
| `room-system` / `trim-system` / `opening-system` | harmonic, vernacular, classical trim, Craftsman trim, Prairie trim, opening proportion, the pointed opening, the Craftsman head datum | the room breadth, the ceiling, the door leaf — for the pointed opening, the span, because a Gothic head's height is a consequence and not a dimension; for the Craftsman system, the framing bay, and the opening's height is not proportioned at all but taken off a single datum |

Non-classical styles are not left out. Most traditional buildings were never proportioned from an order; they were proportioned from a brick course, a joist span, or a pane of glass. Those systems are just as parametric — nobody ever wrote them down because nobody had to.

## Authority is data

Vignola is the spine. Palladio, Gibbs, Chambers and Benjamin are **overlays**: packs carrying only their deltas, with everything unstated inherited. So you can ask which authority you are building to and get a real answer.

At a common 12-inch column, the Ionic entablature is:

| | Vignola 1562 | Palladio 1570 | Gibbs 1732 | Chambers 1759 | Benjamin 1806 |
|---|---|---|---|---|---|
| column | 9 D | 9 D | 9 D | 9 D | **10 D** |
| entablature | 2′-3″ | 1′-9⅝″ | 1′-9⅝″ | 2′-3″ | 1′-9″ |
| rule | ¼ column | ⅕ column | ⅕ column | ¼ column | no rule at all |

Benjamin's is the interesting column. He adds a whole diameter to every order and says so in his preface — *"Experience has taught me that no determinate rule for columns, in all situations, will answer."* His orders are attenuated because they are executed in wood at small scale on modest buildings, and the mouldings are simplified to what a plane can cut in one pass. That is the same pressure acting on production building today, which is why he is worth more attention than his scholarly standing suggests.

### The module trap

Authorities do not share a module, and getting this wrong silently doubles or halves every dimension an overlay inherits. Vignola and Chambers measure in the **semidiameter**; Palladio measures in the **whole diameter** (except his Doric). Every order pack therefore declares `module.diameters`, and the engine normalises the base into the overlay's system before merging anything. Comparisons are made at a common **column diameter**, never a common module.

## Two things the engine proves

**Invariants.** A pack states what it claims about itself as an evaluable expression, and the validator proves the data satisfies it. Vignola's whole achievement reduces to two: the entablature is a quarter of the column, the pedestal a third.

Except that the second is false in his own Corinthian and Composite, where he draws 7 modules against a column of 20 — 0.35, not a third — and confirms it arithmetically by dividing his arcade plate into 32 parts. Esquié calls it out as an explicit exception. **The data encodes what he drew, not what he said**, and the invariant records the exception rather than letting the number lie.

**Cross-engine agreement.** The interactive drawing runs a JavaScript port of the same engine. All 24 order packs are checked to agree to within 0.02 inches between the Python engine and the browser. A drawing generated from the data cannot silently disagree with the dimensions taken from it — if a figure is wrong, the picture is wrong in the same way.

## Judgment slots

`derived_rules` is the bridge from an order to the kit of parts: the crown as a reduced entablature, the chair rail at the pedestal cap, the casing at a sixth of the opening width. Where the sources genuinely do not determine an answer, a rule carries `judgment: true` and defers.

This is not modesty. A generative grammar produces syntactically valid nonsense — *colorless green ideas sleep furiously* — and a rules-based house generator will do the same: houses that violate no constraint and are still dead. The answer is not more rules. It is marking the slots where the system knows it does not know, and saying so.

The chair rail is the honest case. The classical derivation puts it at the pedestal cap, and at a 9-foot ceiling that lands at 23 inches, below the back of a chair. `trim-classical` now carries `calibrated_for: [142.5, 168]` — the derivation only reaches the measured 30–32 inch band at a ceiling of 142½ inches, so it is out of calibration through the whole New England and Chesapeake range and comes good only in Charleston. Below that, set the rail from the window sill and re-derive the base and cornice from the pedestal you actually used.

A rule can also be marked `diagnostic`, meaning it is designed to fail informatively. `opening-proportion`'s sill expression returns a low number to tell you that the storey height and the window proportion cannot both be classical in this room, and one of them has to give. Without the flag it reads as a rule returning a wrong answer.

## Conflicts

Every pack records where it collides with building today, with a severity and a resolution: an 8-foot ceiling against a Corinthian entablature; carved acanthus against any real budget, with four ranked substitutions and a statement of which ones are dishonest; modillion spacing against code-minimum glazing; insulated glazing units that cannot take true divided lites. And a tolerance floor — at a 6-inch module one part is a third of an inch and several fillets are a tenth, so these orders do not work below roughly a 9-inch module in painted wood.

This is the most commercially defensible material in the project. It is the expertise that currently lives only in senior architects' heads.
