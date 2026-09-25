# oq/a-parti-states-rooms-and-doors-and-no-positions — any diagram of a plan type invents where its rooms are

*Status: OPEN · Raised in: WP-14.16 (25 September 2026)*

**The question.** Tranche 2's list names a *PartiDiagram*: a small plan-type diagram per candidate,
so that a reader comparing candidates sees the arrangement rather than reads it. The parti library
says what it holds in `mcp_server/core.py`'s own note on it: *"A parti specifies topology and roles
only — dimensions come from the room catalogue and are scaled to the brief."* A parti record names
its rooms, their doors and their declared exterior walls. It states no position, no size and no
adjacency beyond the doors.

**A diagram is a set of positions.** Any drawing of a parti would place its rooms somewhere, and
every such placement is the app's, not the record's. The corpus already has one engine that places
rooms, and its placements are judged, disclosed, and sometimes refused. A second, silent placement
drawn beside every candidate would be a second answer to the question the placer exists to answer.

## What each answer would change

1. **Draw the topology as a graph.** Rooms become nodes and doors become edges, with no floor-plan
   geometry. It is honest, and it reads as a diagram rather than a plan.
2. **Draw the candidate's own placement, thumbnailed.** It is honest where the candidate has been
   placed, and it is refused wherever the placement is refused, which is where a reader most needs
   it.
3. **A parti record gains a stated schematic arrangement.** That would be an authored grid per parti
   (21 records), which is a statement about the type, needs sources, and moves
   `schema/parti.schema.json` and `build/check_partis.py`.

## What tranche 2 does meanwhile

The parti record page (`#/parti/<id>`, WP-14.23) states the topology as a table: rooms, doors and
declared walls. No diagram is drawn. This follows ruling default 5 in
`docs/prd/phase-14-tranche-2.md` §0.3.
