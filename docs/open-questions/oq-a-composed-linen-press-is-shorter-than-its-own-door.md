# oq/a-composed-linen-press-is-shorter-than-its-own-door — a door whose leaf and jambs need 2.95 ft, on a room declared 2.9 ft long

*Status: OPEN · Raised in: the garage is its own mass (26 to 27 November 2026)*

**OPEN — the composer sizes a linen press at 1.3 x 2.9 ft and gives it a 2 ft 3 in door. The door's
leaf and jambs need 2.95 ft of shared wall (`openings.required_wall_ft`). So the room as declared
cannot hold its own door, the prover asks for only the 2 ft the room can offer, and whether the
door is seated is left to how the press happens to be drawn.**

## What was measured

`compose.instantiate("centre-passage-double-pile", briefs/family-georgian.json)`, 27 November 2026:

- `linen`: `width_ft` 1.3, `length_ft` 2.9; one door, to `upperpassage`, `width_ft` 2.25.
- `openings.required_wall_ft(2.25)` is 2.95 ft: the leaf and two 0.35 ft jambs.
- `geometry_cp._door_overlap` caps what it asks at the smaller room's longer side, floored to the
  1 ft grid: `floor(2.9)` is 2. Its own comment gives the reason: "never demand more shared wall
  than the smaller room can physically offer, or a wide opening between two small rooms becomes an
  infeasibility rather than a finding".
- First placement on four workers: the press was drawn with 3 ft on the passage, the door was
  seated, and `drawability.assess` read DRAWABLE WHERE JUDGED.
- First placement on one worker, same record, every type fact held: the press was drawn 2 x 2 ft,
  the door was refused ("they share 2.0 ft; this leaf and its jambs need 3.0 ft"), and the house
  read NOT DRAWABLE for that one door.

Five partis carry a linen press. `rooms/linen-press.json` bands its length at 2.5 to 4 ft and says
in its own words that the press "fits in a 14 in deep by 36 in wide recess".

## Why it matters

It is the one thing that stood between the native double pile and a drawable sheet on the
one-worker placement above, and it is not a fact about the house. The report of that package gives
the count over its compose runs.

## Readings, none taken

1. **The composer sizes the press to its own record's recess**, 3 ft long. The room then offers
   3 ft and the prover asks for it. This moves every composed house with a linen press.
2. **The door is narrower.** A 2 ft leaf needs 2.7 ft, inside the 2.9 ft the composer declares.
   `openings/grammar.json` states the leaf, so this is an edit to an editorial rule.
3. **The prover's cap reads the grid.** A 2.9 ft side is drawn 2 or 3 ft on a 1 ft grid, and
   rounding the cap rather than flooring it would ask for 3. It reaches every composed room with a
   fractional long side, and it tightens a hard statement.

Each changes what the prover is asked for on every composed diagram, so each wants its own
measurement before it is chosen.
