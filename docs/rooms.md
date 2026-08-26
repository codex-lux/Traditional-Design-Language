# Rooms and groupings

58 room types and 16 groupings. The layer between the element slot and the massing: a massing is the skeleton, a room is an organ, a grouping is a system.

## Rooms are not style

Like massings, rooms are style-independent. A parlor and a living room may be the same volume in the same position doing different social work, and the same room wears different trim in every style that contains it. What a room actually constrains is **dimension, daylight, adjacency and servicing** — physical facts before they are stylistic ones. Style enters through `style_variation`, which records the name, the trim grade, the position, and whether the room exists in that style at all.

## Four things the catalogue insists on

**Furniture, with clearances.** The real constraint on a room, and almost never written down — which is why so many plans have rooms that dimension correctly and cannot be furnished. A dining table for eight is 40 × 96; a pushed-back chair needs 36 inches; passing behind it needs 18 more. That is 148 inches, so **a 12-foot dining room is a fault dressed as a room**, and it is the commonest dimensional error in production housing. The IRC minimum for a habitable room is less than half the furniture minimum — the clearest case in the house of a floor mistaken for a target.

**History, because rooms are social institutions before they are spaces.** The parlor did not shrink because houses got smaller; it died because the funeral moved out of the house. The great room is not a big living room, it is the medieval hall returning after four centuries with the hearth replaced by a television. The garage moved from the back of the lot to the front of the composition in fifty years and no traditional grammar was updated to receive it.

**Typed, directional adjacency with exceptions.** `must_adjoin`, `should_adjoin`, `must_not_adjoin`, each with a `relation` and a `strength`. The exceptions matter as much as the rules: the Creole cottage and the shotgun are deliberately hall-less, the Charleston single house enters sideways off a piazza, and adjacency rules written for an Anglo centre-passage plan produce nonsense there.

**A privacy gradient that must not be scrambled** — 0 street, 1 threshold, 2 public, 3 family, 4 private, 5 intimate. The validator warns when an `entered_from` jumps three ranks, because a plan that scrambles the gradient will feel wrong however well it is detailed.

## Groupings are the scale people actually design at

Nobody composes a house room by room. They compose it from clusters with their own internal logic: a hall-and-parlor pair, a centre-passage core, an entry sequence, a service core, a primary suite, a piazza core.

Each grouping carries internal rules with `hard` / `strong` / `preferred` severities and a measurable `test` where one exists, and — the important field — **`attaches_to`**, which says how the grouping lands in a massing and at what fit. That join is what makes the room catalogue and the massing catalogue composable, and it is where a kit of parts becomes a plan.

`expansion_logic` appears here as it does on massings. The dependency-and-hyphen grouping has the most robust growth rule in the whole corpus: every subsequent need becomes another lower, narrower section, and the ridge steps down monotonically. It is also the best available answer to the garage — hyphen it off by twelve to twenty feet, drop its ridge to 60–80% of the main block, and the street elevation recovers. That is retrieval of a rule the style already contains; only the numbers are invented.

## What is still missing

Nothing resolves a set of rooms into a plan yet. The catalogue states the constraints; a generator that satisfies them is the next thing to build, and it should be built against `tdl_get_grouping` rather than against the rooms directly.

## The `void` block

Only meaningful on a room whose `function_class` is `outdoor`. Two required booleans:

| field | means |
|---|---|
| `within_footprint` | the void takes a rectangle inside the building's block — the house is built around it or beside it under one outline |
| `roofed` | the void is covered, so something may sit above it |

They are independent, and both are needed to place one. Current values: `courtyard`
(true, false), `loggia` (true, true), `piazza` (true, true), `terrace` (false, false). Each
carries a `note` deriving the answer from the room's own description.

A room with no `void` block is treated as `within_footprint: false` and stays out of placement.
That default is deliberate: it is the behaviour before OQ 55, and a room nobody has judged must
not be silently promoted into the footprint.

This is **not** a second classification axis and it is not the `void` function_class OQ 55
rejected. `function_class` is untouched; the block is descriptive.
