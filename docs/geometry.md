# Geometry

Room rectangles placed in a footprint, both levels solved together.

```
python3 build/geometry.py plans/tidewater-georgian-careful.json \
  --parti centre-passage-double-pile --candidates 900 --svg dist/plans/out.svg
```

## Bay-grid slicing, with the relaxations counted

Rooms snap to the structural bay module the parti declares, because traditional houses **are** built on one — joists span it, windows centre on it, the facade composes from it. Placement is recursive guillotine subdivision along bay lines.

Where a room cannot be made to fit on the grid the cut is allowed off it, and **every such relaxation is counted and reported**. A cut off the bay line is a joist run that does not land on a bearing wall and a window bay that will not centre, so it is a compromise rather than a detail.

## The move that turns a treemap into a plan

The first working version produced perfectly valid rectangles in entirely wrong places. The fix was one rule:

**A circulation room with exterior walls on opposite sides spans the plan.** That is what a centre passage *is* — a slab from front door to back door dividing the house in two, with rooms sliced either side. Treating it as one more rectangle to pack produces a treemap; treating it as a slab produces a Georgian plan.

Two related constraints followed: only circulation may span (a porch with three exterior walls wants the south edge, not a slab through the middle), and a room whose *type* is a centre passage is placed near the centre, because that is what it is named for.

## Both levels together, not one after the other

Candidate layouts are generated for each level and scored **in pairs** on vertical alignment — upper wall lines that continue to a wall below, wet rooms that sit over wet rooms, the stair landing over the stair. An upper layout that would score better on its own is rejected when it leaves walls unsupported.

Every misalignment that survives is named in the report: *"11 upper wall lines do not continue to a wall below; each is a transfer beam."* That is a cost, and it should be visible before anyone prices it.

## When it will not fit

Grow the footprint first — add a bay before compromising a room. A room below its furniture minimum is a defect that survives the whole life of the building; a slightly larger house is just a slightly larger house. Only then shrink rooms toward their bands, and only then drop optional rooms.

Footprint depth comes from the **massing's own pile** — single-pile 22 ft, double-pile 36 ft — rather than from an invented aspect ratio. Getting that wrong produces a house of the right area and the wrong shape, which was the first version's most obvious failure.

## The drawing is a render of the data

`build/render_plan.py` emits SVG from the coordinates: rooms, walls, bay lines, windows on exterior walls, door marks where two rooms share an edge, dimensions, a scale bar. Nothing is drawn that is not in the plan record, so the drawing and the data cannot disagree — the same discipline as the order tool.

## What this does not yet do, stated plainly

It produces **valid, dimensioned, drawable plans with every compromise reported**. It does not yet produce plans an architect would sign.

- **Room placement is adjacency-driven, not composed.** The solver satisfies constraints; it does not compose an elevation. The entrance is not reliably on the entrance front, and the ceremonial sequence — approach, portico, passage, principal room — is not yet a constraint the solver knows about.
- **Search is shallow.** Randomised slicing improves with more candidates (537 → 489 → 463 from 40 to 800) but it is hill-climbing over a heuristic, not a real optimiser. A proper solver would do better and could prove infeasibility.
- **No wall thickness, no structural grid, no roof.** Rooms are clear dimensions. Turning them into a framed building is another pass.
- **Doors are drawn where rooms touch**, not placed by rule. Door position is a real design decision and the corpus has rules for it that the renderer does not yet consult.

The honest summary: the geometry pass makes the composer's output visible and checkable, which is worth a great deal, and it is one or two more passes away from being worth building from.

## Next

Compositional constraints. The solver needs to know that the entrance belongs on the entrance front, that the principal rooms take the best aspect, and that service belongs at the back — none of which are adjacency rules, all of which the taxonomy already states in `composition_parti` and in the style constraints. That is the difference between a plan that satisfies and a plan that composes.
