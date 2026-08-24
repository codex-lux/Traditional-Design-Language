# The composer

Template-seeded, validator-scored, and it returns several plans rather than one.

```
python3 build/compose.py briefs/family-georgian.json
```

## How it works

**Seed from the canonical partis.** Twelve plan diagrams — centre-passage double and single pile, hall-and-parlor, side-hall town house, Cape with central chimney, Foursquare, Charleston single with piazza, Creole gallery, bungalow, tripartite ranch, five-part Palladian, gable-front-and-wing. Each is descended from something that was actually built, which is the argument for seeding a search rather than starting it from noise.

A parti specifies **topology and roles only** — which rooms, which walls are outside, what connects to what. Dimensions come from the room catalogue, so the library never duplicates room data and can never drift from it.

**Size, repair, reclaim.** Rooms are scaled from the catalogue midpoint toward the target, then clamped to each room's own band, then optional rooms are dropped if it is still too big. The plan then goes through the validator and the composer applies the move each finding implies — widen a room that cannot take its furniture, raise a window head that cannot reach the back of the room, shorten a room deeper than its light. Repair spends area, so a reclaim pass gives it back from rooms that are not complaining, shortening length rather than width because width is what the checks care about.

**Rank by fatal first, then style fidelity.** Score is 100 per fatal, 8 per serious, 1 per minor, less a bonus for how native the diagram is to the style and how canonical the massing.

## What it returns

Four contrasting candidates, each with its counts, its area and how far off target, a footprint check against the bay module, **what the diagram trades away**, and a decision log of everything the composer chose where the brief was silent.

```
Centre Passage, Single Pile     fatal 0  serious 10  3309 sf (3.4%)  score 84
Centre Passage, Double Pile     fatal 0  serious 11  3413 sf (6.7%)  score 114
Side-Hall Town House            fatal 0  serious  9  3319 sf (3.7%)  score 116
Foursquare Quadrant             fatal 0  serious 10  3396 sf (6.1%)  score 122
```

The single-pile winning a Tidewater brief is the right answer and it was not the first one the composer gave. It ranked fourth with a fatal finding until a modelling error was fixed — see below.

## Four things the composer will not do

**It will not invent a room the diagram has no place for.** A brief asking for a garage against a parti with none is reported, not satisfied. Position matters more than presence.

**It will not drop a room that is load-bearing for a rule.** A room satisfying a hard adjacency is not optional however the parti marked it. Dropping the butler's pantry to save area severs the kitchen from the dining room, and the guard is general rather than a special case.

**It will not present an assumption as a fact.** Everything absent from the brief appears in the decision log.

**It will not tell you a plan is good.** A plan with no fatal findings is not therefore alive. The corpus can say what is wrong; the judgement of what is worth building belongs to the human, and returning four candidates rather than one is how that division of labour is enforced.

## What building it found

**`via` on an adjacency rule.** `kitchen must_adjoin dining-room, direct-door` is correct in a house with no butler's pantry and wrong in one that has it — the pantry exists precisely so the kitchen does *not* open onto the dining room. A rule with no named intermediary forbids the very room invented to satisfy it. Adding `via` moved the single-pile Georgian from one fatal finding to none and from fourth place to first, which is the historically correct answer: the Chesapeake stayed single-pile a century past the North for exactly the cross-ventilation reason the diagram encodes.

**Viewing distance is not clearance.** A television and a hung picture are both about four inches deep, and both carried a `clearance_in` that is really a viewing distance. Nothing four inches deep constrains the width of a room, so the fit check now skips anything without real bulk.

**A global scale factor cannot reach a small house.** Catalogue midpoints are generous; scaling them all by one number either overshoots a small brief or drives rooms below their own stated floors. Scaling, then clamping each room to its own band, then dropping optional rooms is what actually converges.

## Next

Geometry. The composer emits topology plus a footprint check; it does not place rectangles. That is a constraint-packing problem and it now has a well-defined input — a plan record whose rooms are already sized and whose adjacencies are already legal.

## The brief's target is heated area (OQ 33, 24 Aug 2026)

`instantiate()` holds reserved voids out of the scaling loop entirely: a court or a corredor
keeps the size its own weight and catalogue give it, and the rooms around it are scaled to reach
`target_area_sf`. `reclaim()` has always measured area with outdoor rooms excluded, so before
this the two passes were sizing against two different quantities and only one of them was the
brief's. On a plan with no placed void the difference is a rounding error. On the courtyard
parti, whose court and four-range corredor are about a third of the block, a 3,000 sf brief came
back as an **1,834 sf house** which the composer reported, correctly, as 38.9% off its own target
and could not fix — from its point of view the area had been spent.

So a courtyard brief now returns a house of the requested heated area inside a visibly larger
block, and `footprint.heated_area_sf` beside `footprint.area_sf` is where the difference is read.
