# OQ 55 — reserved voids in both placement engines

*24 Aug 2026. Ruled by Lucas: option (a) — "both engines carry outdoor rooms as placed,
dimensioned voids, excluded from the area budget and the heated envelope, drawn as open."*

## What was wrong

`geometry.py::prepare_rooms` and `solver.py` both dropped every room whose `function_class` was
`outdoor` before placement. For a terrace that is right. For a courtyard it is a contradiction of
the diagram: in the nodes whose canonical massing is `courtyard-full` or `courtyard-u` the court
is the thing the house is built around, and the composed plan scored, placed and rendered as a
solid block with rooms packed where the void should be. WP-4.5 made it the dominant case by
adding `courtyard-and-portal`, which is native to sixteen nodes.

## What was built

**Data.** A `void` block on the four outdoor rooms, carrying two independent facts:
`within_footprint` (does it take a rectangle inside the block?) and `roofed` (may anything sit
above it?). Courtyard `(true, false)`, loggia `(true, true)`, piazza `(true, true)`, terrace
`(false, false)`. Each carries a `note` deriving the answer from the room's own description —
the loggia's is its own stated distinction, "cut INTO the building's mass rather than attached to
its face."

This is **not** option (b), the `void` function_class the ruling rejected. `function_class` is
untouched and nothing was re-typed. A room with **no** `void` block defaults to
`within_footprint: false` — which is exactly the pre-ruling behaviour — because a room nobody has
judged must not be silently promoted into the footprint.

**Placement.** `prepare_rooms` now yields within-footprint voids alongside indoor rooms, each
carrying `_void`. They are placed, dimensioned and scored like any other room.

**Areas.** `footprint.area_sf` keeps its meaning — the gross block, what the roof spans and the
lot must hold. `void_area_sf` and `heated_area_sf` are new and state what it heats. The three are
derived from each other rather than rounded independently, so the record adds up.

**Nothing over an open void.** A room placed over an unroofed void has no floor under it and the
roof it needs is the hole. `geometry.py` charges 40 and names it; `solver.py` states it as a hard
disjunction of four separations, and reports `open-void:<room>~<void>` in `unmet_requirements`
with prose. That difference — a penalty the search may buy its way out of, a constraint the
solver may not — is the two engines behaving as they are each meant to. A **roofed** void is
deliberately exempt: a Charleston single's upper piazza sits on its lower one, and charging that
would be the check misfiring on the case it was written for.

**Structure.** A wall between a room and an unroofed void is tagged `role: exterior`,
`wall: court`. It is weather-facing, on the thermal envelope, and bearing. That is the structural
point of a courtyard house and it was invisible while the court was not placed at all. On the
test plan the ground level went from 10 bearing lines to 20.

**Roof.** `main_roof` gains `openings`, recording each unroofed void with its dimensions and
saying plainly that every ridge and eave figure in the record was computed for a roof spanning
the whole block, which over a court it is not.

**Drawing.** An unroofed void is filled with the ground colour and hatched (an SVG `<pattern>`,
so it cannot spill past the rect) and labelled "open to sky"; a roofed one keeps a faint fill and
reads "roofed, unheated".

## Three findings from building it, each of which changed the implementation

**1. On a courtyard massing, `depth_rooms` describes the range, not the block.** Both courtyard
massings read `single-pile`, correctly — the ranges around a court *are* one room deep. Feeding
the court's area into a 22 ft depth target produced a **121 × 24.6 ft strip with the patio inside
it**: the right area, a shape that is not the diagram, a house nobody could build. The massing's
own `footprint` field distinguishes them (`courtyard` has ranges both sides of the void, `U` one),
so the block's depth target became `ranges × pile + void_band`, recomputed inside the growth loop
because the void band's depth is its area over the block width.

**2. The growth loops optimise the block and the court is what matters.** With the depth target
fixed, the shrink loop still took the block to 4 bays and made the court **16 × 40** — in band
for area, and out of band for the one ratio `rooms/courtyard.json` calls "THE RATIO... the number
that decides whether the room works at all", banded 1.0–2.2. On a ring massing the bay count is
now re-chosen against that band. The court comes out 25.9 × 25.0, aspect 1.04.

**3. The heuristic structurally cannot find a ring.** Four thousand candidates put the court in
the block's SW corner against two exterior walls, every time. Isolating one room into the
innermost cell of a four-deep nesting is not a thing random guillotine partitions do, so a scoring
penalty alone would have charged for a defect no candidate could avoid — a check that can only
lose. A ring *is* guillotine-decomposable (cut at the court's south and north edges for three
bands, then cut the middle band at its west and east), so `courtyard_slice()` states that tree
instead of searching for it, and the ordinary search still slices the four ranges. The court's
depth is not chosen: `ring_depth()` solves it from the court's own declared area against the block.

`solver.py` needed nothing for this. It reads its topology off the heuristic's layout (WP-2.3's
own finding), so it inherited the ring and refined it — the court came out at (20, 22), 18.25 × 22
in a 55 × 54 block, enclosed.

## What it refuses to do

`ring_depth` returns `None` when the discriminant goes negative or the ranges come out under 7 ft
deep, and the ordinary slicer runs instead. The report then says the court is a notch in the
block, not a court, and to read the drawing before believing the plan. That is a real answer
rather than a fallback dressed as one.

## Deliberately not done

- **The roof over a court is stated, not derived.** Ranges, four eaves, valleys, and the
  inward-falling pitch that drains to the court are not modelled. Raised as **OQ 60**.
- **The portal range is one rectangle and cannot be.** A continuous roofed walk around four sides
  of a court is one room record, so it is placed along one side and the other three ranges are
  entered from nothing. The validator does not see it because it never reads `room.geometry`.
  Raised as **OQ 61** rather than fixed, because the obvious fix changes what a room *is*.
- **Terraces stay out of placement**, which for a terrace is the right answer, not a limitation.

## Found in passing, unrelated

Five of twenty-one partis carry **fatal** findings against their own native style
(`cape-central-chimney` 4, `five-part-palladian` 4, `charleston-single-piazza` 2,
`creole-gallery` 2, `ranch-tripartite` 1), so the composer will not recommend them for the styles
they were written for. Verified pre-existing against the tree before this work. Raised as **OQ 59**.

## Verification

`python3 build/check_all.py` — 22 checks, 375 tests green. `tests/test_voids.py` is new (15
tests) and pins: the four rooms' declarations; that an unjudged room is not promoted; that the
Tidewater plan's terrace is still not placed and its record is unchanged; that the court is
placed, enclosed, and in its own proportion band; that `ring_depth` refuses a block that cannot
hold the court; the vertical rule and the roofed exemption; that a court-facing wall is exterior
and bearing; that the roof records the hole; that the drawing hatches it open; and that both
engines build the void report from one shared function rather than two copies.
