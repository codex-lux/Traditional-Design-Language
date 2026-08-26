# WP-6.2 — Opening semantics: a door becomes a thing with a place

*26 August 2026. Tranche 2 of three. Branch `claude/floor-plan-design-issues-1x19t3`.*

## Why

WP-6.1 stopped the sheet lying about the record. It could not make the record say more
than it knew, and what it knew was almost nothing: **a door was an unordered graph edge**,
`{"to": "kitchen"}`, with an optional width. No wall. No position. No hand. No height. No
rank. Composed plans emitted every door in exactly that form and every window as a
hardcoded 3.2 ft unit, twice, on every lit wall of every room in every style.

So the questions a reader asks of a plan — *can I get to the kitchen? why is the front door
under a window? where does the stair go?* — were unanswerable from the data, and the
renderers answered them by inventing. This tranche makes the record able to answer them.

Per Lucas's ruling, OQ 54 is reopened: the critic may now read the drawn house.

## What was found

**The corpus already knew nearly all of it, and nothing read any of it.**

- `proportions/systems/opening-proportion.json` derives an entry leaf from the storey
  height (`storey_height / 3.5`, Palladio ch. XXV quoted beside it) and explains in its own
  note why a wide one becomes a pair: *"past about 44 in a single leaf becomes unwieldy, so
  the storey's demand is met with two."*
- The same pack carries **`window_width_from_room = room_width / 4.5`**, under a note that
  calls it *"THE RULE MODERN PRACTICE HAS ENTIRELY LOST, and its loss is why so many
  otherwise correct elevations feel under-windowed."* It had never been run.
- The kits grade the doors — `principal 84 in, secondary 80 in, service 78 in` — and
  `faults/every-door-the-same-door.json` requires at least three distinct door
  specifications per house. Neither could be checked, because a door had no rank.
- 53 of 60 room records carry a `glazing_fraction` band, which with a wall's area is a
  complete derivation of how many windows that wall wants. Never run.
- `rooms/stair-hall.json`'s `critical_dimension` contains the entire stair-sizing algorithm
  in prose, worked example included. `build/structure.py` runs the arithmetic *backwards* —
  reading the solved room and reporting whether the run fits — into a section artifact no
  plan ever saw. **No line of stair-drawing code existed anywhere in the system.**
- `rooms/butlers-pantry.json` calls its own door rule *"the rule the room exists for and it
  is almost never written down"* — the kitchen and dining doors must not align — and it sat
  in a prose field with nothing able to act on it.

**What the corpus did NOT know is which kind of opening belongs between which two rooms.**
That is the one genuinely new dataset here, and by ruling it is editorial.

**The reference plan breaks its own style's hard constraint, and could not have satisfied
it.** `styles/tidewater-georgian.json` c03 is hard: *"Centre passage 10–14 ft wide with
exterior doors at both ends, aligned on axis and both operable."* The passage record
declares one `exterior` door and a window on N. With no `wall` field, both renderers put
that door on the first declared exterior wall — S — so the rear door was drawn on the front
and the rear elevation showed a window where the door belongs. That is the reported symptom
("the centre passage shows no door out the back — it's really just a window") and it had
two causes stacked, one in the record and one in the renderers.

## What was built

**Plan schema 0.3.0.** The placed plan is now a record rather than something carried beside
one. Until this, `additionalProperties: false` at the root forbade `geometry`, `footprint`
and `geometry_report`, so a plan the solver had placed **could not validate against its own
schema** — which is precisely why the placement travelled out-of-band and why the critic
never read it. Openings gain `wall`, `position_ft`/`positions_ft`, `hinge`, `swing_into`,
`height_ft`, `rank` and `unit_type`; rooms gain `fixture_layout`; the plan gains `stair`.
Every addition is optional and all 16 existing records validate unchanged.

**`openings/grammar.json`** — 30 rules saying which kind of opening belongs between which
two rooms, with a width band and a rank. `build/check_openings.py` proves **totality** (all
1,890 room pairs plus exterior resolve to a named rule) and, more importantly, **checks
every `basis`**: a rule must name a record that exists and any sentence it quotes must
actually appear in that record. An editorial call whose citation cannot be verified is a
guess wearing a citation, and this file is where that would have been easiest to do.

**`build/openings.py`** — the placement pass, called once from `geometry.solve()` so both
engines and every consumer get the same answer. It seats every door and window, applies the
butler's-pantry offset rule and the passage axis, builds the stair from the storey height,
and packs wet-room fixtures from the room catalogue's own footprints. **What it cannot
place it marks `unplaced` with a reason — never deletes.**

**`compose.py` derives instead of guessing.** Doors take their width, type, rank and height
from the grammar, from the kit graduation, and — where a pack states the quantity — from
the pack's own expression, read and evaluated rather than restated. Windows take their
width from the room they light and their count from that room's glazing fraction, bounded
by `sash-light`'s minimum solid. Every editorial default is a named JUDGMENT line in the
decision log.

**The renderers read the record.** Both now prefer placed positions; `inferred_positions`
counts what they still have to invent, and on a placed plan it is **0**. Decision 11 —
*"the drawing is a render of the data and nothing is drawn that is not in the record"* — is
literally true of the plan sheet for the first time.

**`plan_check` gains a `drawn` layer**, the only layer permitted to read placement. Three
states throughout: an unplaced record reports COULD NOT EVALUATE and takes no drawn finding
at all.

## Measured

A composed bungalow's door schedule, before and after. Before, every row was `{"to": id}`:

| pair | width | type | rank |
|---|---|---|---|
| living – dining | 3.25 | swing | principal |
| kitchen – nook | 4.5 | cased-opening | secondary |
| dining – kitchen | 2.8 | swing | service |
| hall – primary | 2.75 | swing | chamber |
| hall – hallbath | 2.45 | swing | chamber |
| hall – linen | 2.25 | swing | closet |

Windows now scale with the room they light: a 13.5 ft living room takes 2.96 ft units, a
10 ft kitchen 2.04 ft.

**The grammar fits the hand-authored Tidewater schedule exactly — 30 of 30 dimensioned
doors inside their resolved band.** It fits `spec-builder-colonial` at 19 of 23, and that
gap is the grammar working: that plan's own note calls it *"a deliberately ordinary
production plan, written to see what the validator catches"*, and three of the four
disagreements are its 5 ft, 6 ft and 10 ft openings into formal rooms — the fault
`open-plan-in-a-room-based-style` already names them.

**On the placed Tidewater plan the drawn layer reports what Lucas reported:**

- **3 fatal** — Library, Breakfast Room and Chamber Bath cannot be reached from outside at
  all. *"There's no access point to the chamber bath."*
- **1 serious** — *"Kitchen (Dependency) joins no other room on the drawing — the only way
  in is from outside. The record declares 5 interior door(s) and the placement realised
  none of them."* That is his first sentence, as a finding.
- **20 rooms drawn at a size the record does not declare**, worst the linen press at +303%,
  the back hall at +162%, the upper passage at **+63%** — *"The passage is way oversized."*
- **The stair is not drawn, and says why**: the hall is placed at 10.0 × 10.6 ft and a
  dog-leg for this 12 ft storey's 20 risers needs 11.8 × 7.5 ft. **The room the record
  declares — 9 × 14 ft — would have held it**, so this is the placement shrinking a room
  below its own stair rather than a house too small to have one.
- **The passage takes its rear door.** `op-passage-axis` reads which end already reaches
  the outside (through the porch, at the south) and seats the declared exterior door at the
  **north** end, on the room's centreline. c03 is satisfiable for the first time.

Two findings were sharpened during the work rather than left as first written. A room that
is unreachable was initially reported twice — once as unreachable and once as joined to
nothing — which inflates a plan's troubles with a restatement; the second finding now fires
only for rooms that *are* reachable, which is what makes the kitchen's case distinct.

## Two defects the new guards caught in this package's own work

**The two renderers drifted again within the hour, and the fixture caught it.** The record
first carried one `position_ft` per window *group* and let each renderer re-derive the
spacing of the rest. The two derivations came out 0.7 in apart, and
`tests/test_sheet_symbols.py` failed on the overlap. The record now carries
`positions_ft` — one centreline per unit — because a group of `count` windows is `count`
physical openings, each seated in whatever run the doors left. This is exactly what the
WP-6.1 contract fixture was built for.

**A door to a room that does not exist was left neither placed nor refused.** `spec-builder-
colonial` declares `primary → primarycl` and has no `primarycl`. The placement pass skipped
it, so the record carried a door in the silent third state this module exists to abolish.
It is now marked unplaced with that reason. The declared layer had always reported the
dangling id; the point is that the *placement* must not have a silent state either.

## What was deliberately not done

- **The composer does not invent a second passage door.** c03 wants doors at both ends; the
  record declares one. Placing the one it has at the honest end is a placement decision;
  authoring a second door would be the composer inventing plan content, which is the thing
  it is built to refuse. The gap is now visible instead of hidden.
- **Fixtures are wet rooms and the kitchen only**, packed along one wall. Parlour furniture,
  beds and the arrangement question proper are a new open question, not this tranche.
- **Window `unit_type` is in the schema and nothing fills it.** The ontology's
  `window_type` and `special_window` are whole-house slots; mapping them to a per-opening
  call needs a ruling about where the authority lies, and guessing would be worse than the
  empty field.
- **No door swing physics.** `hinge` is written `low` for every door: the hand is a real
  decision that wants the fixture layout and the furniture wall to be settled first.
- **The 4 remaining spec-builder band disagreements are not tuned away.** Widening a band
  to make a test pass is removing the guard.
