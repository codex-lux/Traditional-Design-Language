# oq/the-double-piles-service-wing-cannot-tile-on-its-hyphens-face — the native Georgian house is one wing from drawable

*Status: CLOSED 27 November 2026 (four rulings of 26 to 27 November, built the same days) · Raised in: the prover decides (26 November 2026)*

**CLOSED (see the last section). As raised: on the stock brief `briefs/family-georgian.json`, the composed `centre-passage-double-pile`
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

## Measured after the garage moved, 26 November 2026 — the main block is a second cause

With the garage its own mass (commit `2263ab0`), the house was posed again on the prover's hard
step: four workers, line grid on, authored walls and the axis released. The harness is in the
session's scratchpad and not in the tree.

| what was posed | result |
|---|---|
| the whole house, range centred, wing boxes 16 to 24 ft wide by 17 to 27 ft deep | INFEASIBLE, all 30 |
| the wing chain alone (the main block's tiling, bands, stacks and bearing released), 40 boxes from 18 x 17 to 26 x 25 ft | tiles at 22 x 21, 22 x 23, 21 x 23 and 23 x 23 ft only |
| the main block alone (the wing's tiling and its rooms' bands released), range centred, +0, +2, +4, +6 ft | INFEASIBLE in 1.9, 1.9, 4.4 and 7.8 s |
| the same at +0 on the parent commit `cc98832` | INFEASIBLE in 1.7 s |
| the main block alone, centred, +4 ft, one more fact released | holds with the butler's pantry's band released (11.3 s), with `primary` over `drawing` released (6.3 s), with `upperpassage` over `passage` released (37.8 s); INFEASIBLE with the dining room's, the library's or the passage's band released, or bearing |
| the main block alone, +4 ft, the link's band 6, 9 and 12 ft up the flank from centred (the last is flush with the rear wall) | OPTIMAL in 3.0, 18.3 and 14.0 s; 3 ft up is INFEASIBLE |
| **the whole house, every fact held, +4 ft, wing 22 x 21 ft with its rear wall on the main block's rear wall, the link at each of those three positions** | **OPTIMAL in 3.0, 10.0 and 6.5 s** |

**"The main block holds every fact in 7.4 s" above is not reproduced**, on this tree or on the
parent. How that run was posed is not recorded here; the session that made it was asked and had
not answered when this was written. The figure is left standing above as what was published.

The wing's derived box is 18 x 21 ft (two 9 ft bays). It does not tile at 18, 19 or 20 ft wide at
any depth tried, nor at 24 or 26. The depth growth the prover applies to a wing (`flank_grow_ft`)
takes a 22 x 21 ft wing to 22 x 25 ft at +4 ft, which does not tile either.

## Ruled, 26 to 27 November 2026 — the range stands against the rear wall, and the prover finds the wing's box

Asked on 26 November 2026 as two direct questions, with the table above in front of Lucas. The
answers came back in the same dialog as the session's clock passed midnight UTC.

**Asked, 3:** *With the garage its own mass, the double pile is still proven impossible, and the
cause is now the main block: with the service range centred on its axis (as `geometry.blocks_for`
lays every dependency), the main block cannot hold its facts at +0, +2, +4 or +6 ft, on this tree
and on the parent commit. With the range against the rear wall the whole house holds every fact in
3 to 10 s at +4 ft. Where does a single service range stand along the main block's flank?* The
options put:

- *Against the rear wall (recommended).* The wing's rear wall lines up with the main block's rear
  wall, its link centred on the wing. Basis: `groupings/dependency-and-hyphen.json`, hard: "Where
  dependencies are paired they are symmetrical about the main block's axis; where there is one, it
  does not sit on the entrance elevation." Paired dependencies stay centred. Measured: whole house
  OPTIMAL in 3.0, 10.0 and 6.5 s, every fact held.
- *Centred; drop a stack claim.* Withdraw the parti's `primary stacks_over drawing`. Measured on
  the main block alone at +4 ft: holds in 6.3 s. The whole house was not measured this way.
- *Centred; stop here.* The double pile stays refused, with the main block stated as the reason.

**Answered, 3: against the rear wall.**

**Asked, 4:** *The four-room service wing tiles on its own only in a small island of boxes:
22 x 21, 22 x 23, 21 x 23 and 23 x 23 ft. It does not tile at its derived 18 ft width at any
depth, nor at 20, 24 or 26 ft. You ruled the wing is sized for its door set. How should that box
be found?* The options put:

- *The prover finds it (recommended).* Before the house is posed, the prover asks of each
  whole-foot box, smallest first, whether the wing's own rooms tile it inside their bands with
  their doors, and takes the first that does. No factor is written down. The wing is then off the
  9 ft bay module, on the whole-foot grid ruling 4 of 29 October already states for derived
  elements. The search engine, which has no prover, keeps the derived box and says so.
- *A stated rule: the kitchen spans.* The wing is as wide as the longest length the kitchen's own
  band admits, 22 ft. One rule fitted to one house.
- *Keep the 9 ft module.* 18 ft is measured not to tile; the double pile stays refused.

**Answered, 4: the prover finds it.**

What these answers do not say: the rear-wall reading is ruled for a house with dependencies on ONE
flank; a house with a range on each flank keeps the axis. The link's exact place on the wing was
offered as "centred on the wing" and three places were measured to work. No stack claim is
withdrawn, and no band moves.

## Closed, 27 November 2026 — the wing tiles and the house holds every fact

All four rulings are built: `compose.attach_garage`, `geometry.flank_sizes`, `blocks_for` and
`flank_laying`, `geometry_cp.size_wings`, and the record's own `flank_laying` (plan schema 0.14.0).
`TILING`, `COVERAGE`, the bands, `build/typefacts.py` and the parti's rooms and doors are unchanged.

`compose(briefs/family-georgian.json, 4)`, one run at a time on one four-core container:

| workers | runs | returned | not refused | drawable where judged | the native double pile |
|---|---|---|---|---|---|
| 4 | 4 | 6, 6, 6, 6 | 4, 4, 4, 4 | 2, 2, 2, 2 | first of the set, DRAWABLE WHERE JUDGED, every run |
| 1 | 4 | 6, 6, 6, 6 | 3, 3, 3, 3 | 1, 1, 1, 1 | refused UNDECIDED (bearing, stacks, tiling), every run |

The wing's question is answered: it is sized at 21 x 22 ft on the record as first composed (19
boxes posed) and at 21 x 20 ft on the record the composer's declared loop hands on (10 posed), and
it tiles.

What is left is not the wing's and is carried elsewhere:

- **On one worker the house does not decide.** The record the composer hands to the placed loop is
  undecided at all three depths at 60 s and at 120 s. Amended into
  `oq/the-composed-double-pile-cannot-hold-its-facts-at-any-depth-tried`.
- **The shipped Tidewater record is still laid on the axis.**
  `oq/the-shipped-range-is-still-laid-on-the-axis`.
- **A composed linen press as first composed is shorter than its own door.**
  `oq/a-composed-linen-press-is-shorter-than-its-own-door`.

Report: `docs/reports/the-garage-is-its-own-mass-2026-11-26.md`.
