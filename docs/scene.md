# The scene layer — constructed 3D geometry between the record and the camera

*WP-12.1. The brief is `docs/prd/phase-12-the-sheet-in-the-round.md` §§5–6; the report is
`docs/reports/wp-12.1-the-scene-record.md`.*

```
python3 build/scene.py plans/tidewater-georgian-careful.json --engine heuristic
python3 build/scene.py plans/spec-builder-colonial.json --out /tmp/scene.json
python3 build/scene.py selftest          # also runs inside build/validate.py
```

## What it is, and the finding it inherits

WP-5.11 asked whether SVG could carry a drawn cornice or whether the project needed CAD or
BIM underneath, and answered that **the format was never the constraint** — *a format
serialises what is modelled and cannot invent what is not*. The missing thing was the layer
between: constructed 2D geometry, `build/profiles.py`.

This is the same finding one dimension up. A continuous camera — plan to elevation to
axonometric, an orbit, a section plane moved by hand — needs a scene resident in the browser
and re-projected many times a second. What it does **not** need is a modelling kernel, because
everything a camera can show is already in the record. So the geometry is constructed here, in
Python, once, and the viewer only draws it. **JavaScript learns no more about a house than it
knows about a cyma today, which is nothing** (OQ 83).

Blender and IFC stay what they are: export targets. The scene record is the natural input to
both, and `build/export_ifc.py`'s `IfcShapeRepresentation` work that `docs/export.md` names is
a serialisation job against this record rather than a modelling one.

## The frame

**x east, y north, z up, feet throughout. The origin is the main block's SW corner at GRADE** —
the plan frame `render_plan.py` fixed, with z added. `z = 0` is grade; the ground floor sits at
`section.storeys[0].grade_to_floor_ft`. A viewer sets its up vector to +z and transforms
nothing: what the record says is what the camera sees.

**The roof record does not share that origin, and this layer is the first thing that had to put
them in one picture.** `roof_outline` and `elevation_profile` lay the roof out from (0, 0) over
the *outside* footprint; `wall_lines` lays the walls out from (0, 0) over the *clear* one. Both
call their corner the origin and the two are half an exterior wall apart — 1.29 ft on the
Tidewater plan — so read literally the roof sits east and north of the house it covers. It has
never mattered, because the plan sheet draws rooms and the roof plan draws a roof and no
surface drew both. The scene follows `export_ifc.slab_boxes`, whose slabs are already centred
on the clear rectangle, rather than inventing a third convention;
`oq/the-roof-record-and-the-plan-record-do-not-share-an-origin` carries the question of which
record should move.

## The three states

A record that can only say "drawn" is a record that lies by omission, so the scene says three
things and counts all of them:

| state | where | what it means |
|---|---|---|
| **drawn** | `solids[]` | a thing this layer constructed, carrying the record path of the numbers that made it and the **weakest** `kind` among them |
| **not modelled** | `not_modelled[]` | a thing the record holds that this layer cannot construct — a hip's planes, a stair's flights, an opening's reveal — with the reason it cannot |
| **judgment** | `judgment[]` | a figure the sources leave to a person (a chimney's plan size, a breast's projection). Drawn where it is drawn at all, in construction weight, and named |

The record's `note` states the not-modelled count **whether or not it is zero**, because an
empty list is not the question closed (WP-11.6). A scene that models everything must say
"0 things not modelled" rather than fall silent.

## What it may not do

- **Invent a dimension.** Every solid names its source and its weakest provenance.
- **Restate a rule that exists.** It imports `export_ifc.slab_boxes`,
  `structure.wall_thickness`, `hearths.breast`, `elevation.opening_rects`,
  `compass.plan_north`/`assumption`/`face_token` and the storey heights — it re-derives none of
  them. A second transcription is how two records of one building come to disagree, which is the
  defect WP-12.0 removed one layer up and WP-12.2 removed one layer down.
- **Carry a numeric literal that is a dimension.** `tests/test_scene.py` reads this file's
  source and refuses one outside two named constants: `CUT_HEIGHT_FT` (editorial, PRD ruling
  R2) and `DEFAULT_CANDIDATES` (a pool size, named because
  `oq/a-placement-rule-is-free-at-a-pool-the-server-cannot-afford` is about that number).
- **Carry a colour.** `ink` and `tone` are names the viewer resolves from `tokens.css`. Colour
  in this system is nomenclature — salmon is cut masonry and nothing else — and a hex in a
  record is a decision a reader cannot argue with.
- **Approximate a form it cannot construct.** A hip is named, never drawn as the gable this
  layer can build.

## What is in it today, and what is not

**A note on the primitives.** There are six — box, extrude, sweep, lathe, prism and **plane** —
and the last was earned. A roof plane was first written as a `prism`, one polygon extruded
vertically between the eave and ridge heights, which is a BOX that spans the roof's rise. Every
agreement figure accepted it because all three measure the plan extent, and in plan a box and a
slope are the same rectangle; the house rendered as a two-storey block with a lid, and that is
how it was found. A sloping plane needs a per-vertex height, so it has a primitive that can hold
one. **A layer that adds a dimension needs at least one assertion in that dimension.**

**In:** floor slabs per storey per massing element; wall boxes with their role, bearing verdict
and pen weight; **the openings, as frames in their own wall (WP-12.2)**; the two roof planes of
the gable family and the gable ends as their own face silhouettes; hearth breasts where a room
authors one; every placed room as a *pick volume* that is never drawn; the datum ladder from
grade to ridge with each label already set in feet and inches; the bay grid; the relaxation marks
at the positions the placement recorded; the compass assumption; the solver's engine and input
digest.

**In since WP-12.6:** sash bars and meeting rails on every drawn window (`across - 1` verticals
and `2 x high - 1` horizontals, the two sashes of a double-hung aligning so a bar is ONE member,
and the middle horizontal a `sash` rather than a `muntin` because a meeting rail is a member and
not glazing); shutter leaves where the storey window carries them; and a chimney where the roof
judges a ridge to carry one.

**Not in, and each says so in the record:** hip, gambrel and cross-gable planes; **the window
sill** — `kit.window_sill.projection_in` resolves to a BAND on the node this corpus draws, and a
sill at the band's midpoint is a measurement nobody authored
(`oq/a-child-band-replaces-an-ancestor-derivation`); the **dormer solids**, whose cheeks, face and
own roof stand on the roof *surface*, which this layer models as two planes rather than as a box
to sit one on; cornices, the water table and the belt; the entrance and the porch (WP-12.7);
stairs, which have plan rectangles and no ARITHMETIC yet — the data is there (`riser_in` 7.367 on
the Tidewater plan, and each flight carrying its own tread count, 9 and 10 against 20 risers), so
what is missing is the derivation and not the record.

**A CHIMNEY WHOSE PLAN SIZE IS A JUDGMENT IS AN AXIS AND NEVER A SOLID.**
`tidewater-georgian`'s `chimney_stack_plan_in` is 22 in carrying `judgment: true` — the mason
still owes 18 or 27 — so the scene draws a two-vertex construction line where the stack stands
and puts the judgment on the record beside it. Drawing a box at 22 in would publish a dimension
the corpus declines to settle, in the one place a reader cannot tell a decision from a
measurement. Where the plan size IS stated the stack is a solid; no node in this corpus states
one, so that branch is driven by hand.

**AN OPENING HAS ONE NAME.** `opening_rects` names every rectangle (`S-0-ground`, `S-3-door`) and
the frame takes that name verbatim; every solid dressing it prefixes the name with a `-`. WP-12.1
rebuilt the frame's name out of four fields while WP-12.6's dressing keyed off the record's own,
so one opening carried two names and no assertion relating a frame to its dressing could hold —
found by a mutation, and restoring the second spelling left every suite in the tree green.

## The openings, and the contract that had to be written down

An opening comes from `elevation.opening_rects(elev, face)` — this layer is its THIRD caller,
beside the SVG renderer and the DXF exporter — and it is drawn as a **frame and not a hole**.
This layer does no boolean subtraction, so the wall stays the box the section describes and the
opening is the rectangle the elevation states, extruded through the wall's own thickness. WP-12.6
dresses it; what is here is the extent, which is what the elevation actually determines.

**`at` IS THE LOW FACE AND THE EXTRUSION ALWAYS RUNS ALONG THE PLANE'S POSITIVE AXIS.** That
sentence is in the schema because the first version did not have it: `at` was written on the
OUTSIDE face of each wall with a thickness that is always positive, so the south and west
openings went into their walls and the north and east ones stood **proud** of them. **The same
error was in the gable ends**, which WP-12.1 had shipped standing a full wall thickness clear of
the east and north walls — a 1.29 ft ledge above the eave, where a reader looks — **and its own
test ratified it**, because that test compared the gable's `at` against the OUTER face of the
wall extent, which is exactly where the wrong contract put it. A test written against the wrong
contract is worse than no test. Both are read from both sides now: a gable must occupy the same
slab of space as the wall it stands on, and every opening must lie inside the building's own
bounds.

**And the bounds were the right size in the wrong place.** The frame's origin is the CLEAR SW
corner, so an exterior wall grows outward to `-t` and the outside envelope starts negative;
WP-12.1 stated `min: [0, 0, 0]` with a `max` off the section's outside footprint, offset by one
wall thickness. **None of the three agreement figures could see it**, because all three compare
the walls, the slabs and the datums to each other and not one of them reads `bounds` — a viewer
framing the model from it would simply have drawn the house off centre. It is a containment test
now, to 0.01 ft, which is two and a half times the `section.footprint` rounding residue and three
hundred times smaller than the defect it caught.

Both defects were found the same way as the roof that was a box with a lid: by drawing the scene
and looking at it. **That is now three geometry defects in two packages that every number in the
record accepted.**

## The measurement it is held to

`build/scene.py <plan>` prints the phase's own contract (PRD §9): solids by class, the
not-modelled and judgment counts, the provenance census, the payload in bytes, and
**agreement** — three numbers, printed whether or not they are zero, because a check that only
speaks when it fails cannot be watched for drift.

| | what it compares | Tidewater | spec Colonial |
|---|---|---|---|
| `envelope_vs_slab_ft` | the exterior wall boxes against `slab_boxes`, two routes to one rule | 0.001 | 0.001 |
| `rooms_inside_envelope_ft` | a **containment**: every placed room inside the walls | 1.292 | 0.667 |
| `datums_vs_storeys_ft` | the datum ladder against the section's own storeys | 0.000 | 0.000 |

The residues are rounding: the wall boxes come from the clear footprint plus twice the stated
thickness, the slabs from `slab_boxes`' own arithmetic, the roof from `section.footprint`, which
is rounded to two places. The number is printed rather than a tolerance being asserted and
forgotten.

*(Both figures are on the **heuristic**, deliberately. `auto` reaches a CP proof on one machine
and spends its budget on another, so a suite built on it would assert different geometry on
different runners — which is exactly what WP-12.0 measured happening to the elevation between
two trees.)*

## Where the selftest runs

Inside `build/validate.py`, not as a 51st entry in `check_all.CHECKS`, so `TOTAL_CHECKS` does
not move — the precedent is WP-11.6, which put the family-specimen drift check inside
`check_precedents.py` for the same reason. It is placed after the taxonomy verdict so it cannot
make that verdict read as its own, it exits non-zero on its own account, and a scene that
cannot be built at all reports **N/EV — could not evaluate** with the reason rather than
passing.

## The viewer (WP-12.4)

`workbench/app/src/round/` draws this record, and the division of labour is the same one the
scene layer itself rests on — the part that can be silently wrong is the part that is testable
without a browser:

| file | what it decides | tested by |
|---|---|---|
| `frame.js` | where the camera stands, how the model projects, what is a named view | `node --test` |
| `solids.js` | what a triangle is: the four primitives become faces, edges and an extent | `node --test` |
| `annotate.js` | what the drawing is called, and what furniture is true in each view | `node --test` |
| `three-scene.js` | uploading the above to a GPU. The ONLY importer of `three` | the browser walk |
| `Round.jsx`, `RoundPlate.jsx` | the canvas, the pointer, the sheet chrome | the browser walk |

**Azimuth is the compass bearing of the CAMERA — where the viewer stands, not where they look.**
The south elevation is therefore 180. Getting this backwards draws every elevation as its own
mirror and every axon reflected, and the drawing looks entirely plausible either way: that is
WP-5.11's inverted sweep flag one dimension up, and it is why `round.test.mjs` asserts that east
is on the RIGHT of the south elevation and on the LEFT of the north one rather than asserting
that the projection is self-consistent.

**`three` is loaded only by `await import('./three-scene.js')`.** That is what puts it in a chunk
of its own (545 KB, against an entry chunk of 478 KB and a 700 KB ceiling), so a reader who never
opens the Round never downloads a 3D engine — and it is also what keeps
`no_bare_imports.test.mjs` green, since that walker deliberately does not follow a dynamic
import. `build/check_frontend.py` asserts the chunk exists.

**The pen does not magnify with the zoom.** Edges are drawn with `LineSegments2` at screen-space
width, so OQ 66 — the loupe magnifying the ink along with the drawing — is answered in the Round
by construction rather than by a setting.

**The flat plate is laid over the model by `data-frame`**, which every renderer now writes: see
`build/sheet_style.py::frame_attr`. The renderer states its own affine and says nothing about the
model frame, because which model axis runs along a face is the camera's business and is under
test in `frame.js`. Its elevation case rests on an assumption the record does not state —
`elevation.py::_face_bays` computes bay centres across the span without consulting the face, so
nothing says which model end `u = 0` is. Every face in this corpus is symmetric, so the
assumption cannot be caught out here; the day one is not, read
`oq/an-elevation-does-not-state-which-end-of-the-face-it-starts-from`.
