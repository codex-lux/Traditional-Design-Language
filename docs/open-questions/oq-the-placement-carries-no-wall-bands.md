# oq/the-placement-carries-no-wall-bands — the rooms tile the footprint exactly, so the walls are drawn where no room allows for them

*Status: OPEN · Raised in: WP-11.1, the sheet in its own standard (4 September 2026)*

**OPEN — `geometry.py` tiles the footprint exactly with room rectangles, so there is nowhere in
the placement for a wall to stand. The sheet now draws walls at the thicknesses the record states,
and every one of them is drawn over ground a room is already using.**

Measured on `plans/tidewater-georgian-careful.json`: 2,405 sf of declared programme in a 2,405 sf
footprint, `slack: -0.2 sf`, the placed rectangles tiling 97.6% of it. `derive_footprint` sets
`need = max(ground area, upper area)` from the rooms' own declared areas and then `H = need / W`,
with **no allowance of any kind for wall thickness** — `docs/geometry.md` says so in its own words:
*"No wall thickness, no structural grid, no roof. Rooms are clear dimensions."*

That was consistent while a wall was a line. WP-11.1 made it a body, from
`structure.wall_thickness(plan)` — 15.5 in of envelope, 11 in of bearing wall and 4.5 in of
partition on this house, from its own `declared.construction_type` — and the two readings now
disagree in two different ways:

- **The envelope is drawn OUTWARD** from the block, which is exactly what
  `structure.outside_to_outside_footprint()` already means by *"rooms keep clear dimensions while
  the footprint becomes outside-to-outside"*. This one is right and costs nothing: the sheet is
  1.29 ft larger on each side than the block, and the block is what the rooms tile.
- **An interior wall is drawn CENTRED on the shared line**, because that line is the only thing the
  placement states about it. So a 4.5 in partition takes 2.25 in out of each of the two rooms it
  divides, and an 11 in bearing wall takes 5.5 in. The room's label still states the record's
  figure, which is the honest thing for the label to state and leaves the drawing and the number
  disagreeing by half a wall.

**The sheet discloses it rather than smoothing it over**: every plate, in both registers, carries
`WALLS <assembly> — ENVELOPE n IN OUTSIDE THE PLACED ROOMS, BEARING n IN AND PARTITIONS n IN
CENTRED ON THEM; ROOM FIGURES ARE THE RECORD'S CLEAR EXTENTS`.

## What has to be decided

1. **Should the placer carry wall bands at all?** The alternative — leave the placement in clear
   dimensions and let every drawing and export apply the wall itself — is what happens today, and
   it means `render_plan.py`, `Sheet.jsx`, `export_dxf.py`, `export_ifc.py` and `structure.py` each
   answer the same question, which is how this corpus's most-repeated defect starts.
2. **What it costs the exact-tiling identity.** `geometry.over_band()`'s refusal rests on
   `Sum(got) == T` — an over-band charge is an under-band charge plus a constant *because the
   slicer tiles exactly*, verified to under 0.5 sf, and three formulations were run through the
   whole search without one room changing size (WP-6.3). Subtracting wall area from the tiling
   breaks that identity, and the refusal built on it would have to be re-derived rather than
   assumed to survive.
3. **What it costs CP-SAT.** `COVERAGE = 0.97` is a HARD constraint in `geometry_cp.py`. Wall bands
   plus a 97% coverage floor is an exact-cover demand on a block that was never sized with slack,
   and the way that fails is INFEASIBLE — four downgrade rounds, then a growth loop, then
   `_extract_conflicts` at 20 s of a 25 s budget.
4. **Whether the footprint grows or the rooms shrink.** Settled decision #11 is *"grow the footprint
   before compromising a room — the stated infeasibility ordering"*, and `derive_footprint`'s own
   comment says so; but the loop it comments on grows the WIDTH at constant area and cannot make a
   house bigger (`oq/the-parti-dissolved-its-own-dependencies` measured 2,405.0 sf at every bay
   count from 4 to 10). So the ordering decision #11 states has no mechanism behind it here, and
   this question cannot be answered without giving it one.

**Do not answer it by adjusting the room labels.** A room's figure is what the record declares, and
a label quietly restated as a clear-between-walls dimension would be the drawing correcting the
record on the reader's behalf — the direction this corpus does not go.
