# oq/the-double-piles-service-wing-cannot-tile-on-its-hyphens-face — the native Georgian house is one wing from drawable

*Status: IN PROGRESS · Raised in: the prover decides (26 November 2026)*

**OPEN — on the stock brief `briefs/family-georgian.json`, the composed `centre-passage-double-pile`
is proven unable to hold its type's facts, and the whole proof sits in its service wing. The main
block holds every fact on both storeys. The wing cannot be tiled in any box tried, because of where
its doors are, and the three smallest composition changes that might fix it were each measured.
Which of them is right is a statement about the type, and nobody has ruled it.**

## What was measured

Every figure is from 26 November 2026, on one four-core container, with the line grid on
(`geometry_cp.LINE_GRID`) and the authored walls and the axis released, as the prover's own hard
steps pose the house. The harness is not in the tree; the report names each run.

- **The whole house:** INFEASIBLE in 0.3 s at the derived depth and at 2 and 4 ft deeper.
  `solver.all_facts` reads `proven-impossible`, and the refusal is PROVEN (ruled the same day).
- **The main block alone**, with the wing's tiling and its rooms' bands set aside: **OPTIMAL in
  7.4 s at the derived depth**, with tiling, stacks, bearing and every band held on both storeys.
- **The wing alone.** The minimised conflict core, three times over, names only wing rooms: the
  tiling of the `service` element; the bands of the pantry, the breakfast room, the mudroom, the
  powder room and the kitchen; the kitchen's contested corner; and seven doors (back hall to
  kitchen, to powder room and to mudroom; kitchen to pantry, to breakfast room and to mudroom;
  mudroom to garage).
- **No box tiles it.** With the brief's two-car garage in the wing (`compose.attach_garage` joins
  the garage and its mudroom to the element their anchor stands in), 36 boxes from 27 x 33 to
  45 x 26 ft were each INFEASIBLE in 0.1 s. With room sizes free from 0.7 to 1.5 of their declared
  area the core is the same.
- **Why, by hand.** The hyphen (`backhall`, 5 x 16 ft) meets the wing on a 16 ft band of a face 25
  to 28 ft long, centred. The powder room must open off that band and is at most about 4 x 8 ft
  inside its own band, so it cannot reach a corner of the wing from there. The pocket it leaves
  on the face can be filled only by a room that must also touch the kitchen, or by the garage,
  which is one rectangle.

## The three changes measured

Each was made to the composed record in a scratch copy, never to the parti, and the whole house was
then posed with every fact hard.

| change | with the garage | without it |
|---|---|---|
| the powder room stands in the main block | INFEASIBLE, 0.2 s | INFEASIBLE, 0.2 and 3.9 s |
| the back hall runs the wing's whole depth | INFEASIBLE, 0.1 s | **OPTIMAL, 18.7 s: every fact held** |
| the powder room opens off the kitchen | INFEASIBLE, 0.2 s | INFEASIBLE, 0.6 and 7.1 s |

Without the garage and with no change at all, the four-room wing tiles only where its box is about
40% larger than its rooms (22 x 22 or 24 x 21 ft for 348 sf).

## What each answer would change

1. **The garage is its own mass.** A carriage house beyond the kitchen dependency, linked by the
   mudroom, is the arrangement the five-part type already has. It moves `compose.attach_garage`,
   and `geometry.flank_sizes` would lay a second east element. This is the only reading that
   touches the garage case, and it is not measured: no record states such an element.
2. **The hyphen is as deep as the wing it serves.** Measured to work without the garage. It
   contradicts `groupings/dependency-and-hyphen.json`, which the placer reads as "lower and
   shallower than both", and it does nothing for the garage case.
3. **Fewer rooms open off the hyphen.** The parti gives the back hall doors to the butler's pantry,
   the kitchen and the powder room, and the garage adds the mudroom. A hyphen that one wing room
   opens off is the measured type. Which doors go is a statement about the parti.
4. **Leave it.** The house stays refused on this brief, proven, with this conflict named.

## What it is not

- Not a budget question. Every answer above came back in under twenty seconds.
- Not the wing's size. `oq/the-tiling-fact-cannot-hold-on-a-rounded-or-derived-massing-element`
  asks whether a wing should be sized for its door set (ruling 4 of 29 October, third part). Here
  no size works, so that ruling alone would not draw this house.

Report: `docs/reports/the-prover-decides-2026-11-26.md`.

## Ruled, 26 November 2026 — the garage is its own mass, and the wing is sized for its door set

Two questions were put to Lucas the same day this was raised, before any record or code was
changed. The questions and the answers are two acts, and both are recorded here as they were put.
This file stays IN PROGRESS until the build lands.

**Asked, 1:** *On a brief with a garage (family-georgian), where does the centre-passage double
pile's 2-car garage stand? Today `compose.attach_garage` puts the garage and its mudroom inside the
service wing, and that wing is proven untileable in all 36 boxes and every variant measured.* The
options put:

- *Own mass, mudroom link (recommended).* A carriage house beyond the kitchen wing on the same
  flank: main block, back hall, wing, mudroom, garage. The Georgian kit permits
  `linked-by-hyphen`, and `groupings/garage-and-hyphen.json` already says the garage is reached
  only through its link, never from the kitchen. Not yet measured. The mudroom's 7 to 10 ft gap is
  short of the 12 to 20 ft hyphen rule, as the back hall's already is.
- *Own mass, detached.* No link and no door to the house, at the kit's 25 ft: the Georgian kit's
  canonical `detached-in-the-dependency-position`. Not yet measured.
- *Keep it in the wing.* Change only doors or the hyphen. Every variant measured with the garage
  in the wing came back INFEASIBLE.
- *Measure first, then ask.*

**Answered, 1: own mass, mudroom link.**

**Asked, 2:** *With the garage and mudroom out, the four-room wing (kitchen, pantry, breakfast
room, powder room) still does not tile at its derived box: the powder room on the back hall's 16 ft
band leaves a pocket nothing can fill. Which remedy for the wing?* The options put:

- *Size the wing for its doors (recommended).* Build the unbuilt third part of ruling 4 of
  29 October 2026 ("a wing is sized for its door set"). Measured to tile at 22 x 22 or 24 x 21 ft
  for 348 sf of rooms, every room still inside its own band. No band, `TILING` or `COVERAGE` moves.
- *Full-depth back hall.* Measured OPTIMAL in 18.7 s without the garage. It contradicts the hard
  rule in `groupings/dependency-and-hyphen.json`.
- *Move the powder room's door.* Off the kitchen, or into the main block. Each was measured
  INFEASIBLE alone at the derived box.
- *Decide after measuring.*

**Answered, 2: size the wing for its doors.**

What the answers do not say, because each is a way to over-read them: the hyphen's depth is not
ruled and stays as `groupings/dependency-and-hyphen.json` states it; the powder room's door is not
moved; and the "about 40% larger" above is a measurement of two boxes, not a factor anyone ruled.
