# oq/which-rooms-take-the-hearth — the corpus says the end rooms and never which rooms those are

*Status: OPEN · Raised in: WP-11.4, the threshold and the stacks (4 September 2026)*

**OPEN — the stack is placed and the hearths it serves are not.** `build/threshold.py::hearth_pass`
draws two gable-end stacks on the shipped Tidewater plan, from three records that agree:

| record | what it says |
|---|---|
| `kits/tidewater-georgian.kit.json` `hearth_position.rule` | *"Hearths are at the gable ends, on the outside walls of the end rooms, so the mass of the stack sits outside the heated volume in summer."* |
| `kits/tidewater-georgian.kit.json` `hearth_position.parameters` | `count` 2, `fireplaces_per_stack` [2, 4], both `measured` |
| `massings/catalog.json` `four-over-four.structural_logic` | *"Paired end chimneys serve four fireplaces per floor."* |

Two stacks, two to four fireplaces each, four per floor. **The arithmetic is complete and the
ROOMS are not.** No record in this corpus names a room that takes a hearth. `rooms/*.json` carries
a hearth as FURNITURE in three room types and as a `needs_uninterrupted_wall_ft` in one, and none
of that says *this* room, in *this* parti, is one of the four.

**What PLAN-OF-ACTION.md ruled for WP-11.4**, and what the package therefore did: *"Which rooms
take a hearth is not in any record: raise it, do not read it."* `plan["hearths"]["hearth_rooms"]`
is `null`, beside a note saying so, and `threshold/grammar.json` carries
`th-the-stack-serves-the-end-rooms` in its `stated_rules_not_executed` list.

**Why the obvious reading is not available, and this is the part worth carrying.** "The two rooms
adjoining each stack" is computable from a placement in one line. On the shipped Tidewater plan it
would name the kitchen and the drawing room at the west end — and the parti names eleven enclosed
ground rooms while the placement holds twelve, six of them service
(`oq/the-parti-dissolved-its-own-dependencies`). **The two rooms adjoining the stack are not the
two rooms the TYPE means**; they are the two the placer happened to put there. Reading the record
through a placement the record itself does not endorse is how a guess acquires a citation.

**What a ruling has to settle.**

1. **Where a hearth lives.** A room record's own field (`hearth: true` on `drawing-room`, which is
   a claim about the room TYPE and is false in a Craftsman bungalow); a parti's own list (a claim
   about the DIAGRAM, which is where "the end rooms" actually belongs); or a plan's `declared`
   (a claim about THIS house, which is the most honest and the least reusable).
2. **Whether the number is a constraint or a consequence.** `fireplaces_per_stack` [2, 4] and the
   massing's "four per floor" are the same fact stated twice, and a generator that placed hearths
   would have to satisfy both or be told which governs.
3. **What an unheated room is.** Six of the Tidewater plan's twelve ground rooms are service. A
   rule that gives every principal room a hearth needs the corpus to say which rooms are principal,
   and `function_class` is the nearest thing and is not that.

**What is drawn today, and what is not.** The stack's 22 in square is drawn, in the wall's own
poché, at the mid-depth of each gable end — the point where a double pile's own partition falls
and therefore the one point from which one stack can serve two rooms. **The chimney breast, the
firebox and the hearth are not drawn**, because each of them is a dimension into a room and this
question is about which room. The exemplar plans WP-11 is measured against draw all three.
