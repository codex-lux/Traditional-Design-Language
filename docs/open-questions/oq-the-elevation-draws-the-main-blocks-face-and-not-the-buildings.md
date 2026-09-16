# oq/the-elevation-draws-the-main-blocks-face-and-not-the-buildings — the wing has no front

*Status: OPEN · Raised in: WP-13.7, auditing Phase 13 against the container (16 September 2026)*

**`build/elevation.py` builds each face from the FOOTPRINT's width and depth. On a house with
one massing element those are the main block's, so the face is the building's. On a house with
a dependency they are not, and every opening the dependency places on that face is outside the
drawing entirely.**

Measured on `tidewater-georgian-careful` at `e0f259f`, after WP-13.5 moved six service rooms
into the west dependency, by the gate row
`tests/test_sheet_coherence.py::test_the_elevations_openings_are_the_plans_placed_openings`:

| sheet | plan places on S | elevation draws | missed, in feet from the block's SW corner |
|---|---|---|---|
| careful · search | 10 | 5 | −26.61, −17.11, −13.11, −9.11, −3.38 |
| careful · prover | 6 | 5 | −3.38 |
| candidate · search | — | — | row green |
| candidate · prover | — | — | row green |

**Every missed opening is at negative x.** The main block starts at 0; the dependency is west
of it. Nothing is misplaced, nothing is drawn twice and no coordinate is wrong — the openings
are simply not on the face the elevation believes in.

## Why it was invisible

This is WP-11.9's finding at a further site, hidden by the same fact that hid every earlier
one: **no record in this corpus carried a second massing element.** WP-11.9 taught six layers
below the placer (`openings`, `structure`, `vertical_score`, the lot cap, `plan_check.drawn`,
`export_ifc`); WP-11.14 found the plan DRAWING was a seventh and fixed it with all sixteen
sheets byte-identical, precisely because on a one-rectangle house the room's own element face
and the footprint's face coincide. The elevation coincides too, on all sixteen, and stops
coinciding the moment a record states a dependency.

**The site is NAMED and not numbered, on purpose.** WP-13.5 called `facade.py`/`axis.py` "an
eighth layer" and then, in the same block, called `entrance_score` and
`principal_and_service_score` "a ninth layer and a seventh" — three sites in one package and
one ordinal used twice. A count that one package can advance by three and reuse is not an
identifier. `oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it` is the
question the whole family belongs to; this entry is one module of it.

The row was GREEN on the merged WP-13.3 tree and is red on the same code with the container in
front of it. The code did not change; the corpus did.

## What has to be ruled before it can be fixed

Not a defect with an obviously right repair. Drawing a dependency's front means deciding what
an elevation of a five-part house IS:

1. **One composed face across the whole built extent** — block, hyphens and wings on one
   datum, which is what a measured drawing of Gunston Hall or Mount Airy shows, and which
   makes `_face_bays`, `opening_rects`, `render_elevation` and the DXF export all take an
   extent that is not the footprint's.
2. **A plate per element** — honest, cheap, and it drops the relation a reader most wants,
   which is how the wing sits against the block.
3. **The main block, with its wings drawn in a lighter register** — the convention most
   pattern books use, and the one that needs a second pen rung the sheet does not have.

Each answer changes what the gate row should assert, so the row is left stating the
disagreement with both counts rather than being re-cut to whichever reading the code
happens to hold.

## What must not happen

- **Do not make the row green by counting only the openings inside the block's width.** That
  is the fake-pass shape: the drawing would go on omitting five real windows and the gate
  would stop saying so.
- **Do not widen the 3 in tolerance.** The misses are 128 to 466 inches; no tolerance reaches
  them, and reaching for one would be tuning the instrument at the defect.
- **Do not derive the face from the built extent without ruling first.** `elements.py` can
  supply that extent today, and using it would silently choose reading 1 — a drawing
  convention chosen by whoever was nearest the keyboard.
