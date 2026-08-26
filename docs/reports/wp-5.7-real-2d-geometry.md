# WP-5.7 — The geometry layer: moulding constructions, coursing, and repetition

*26 August 2026. Raised by Lucas against three drawn surfaces: the Drawing Set's front elevation
("bears not even a passing resemblance to a true Georgian tidewater precedent"), its eave cornice
inset ("a most abstracted step knob, painfully primitive relative to the actual sophistication of
the profiles"), and the order Proportions plate. The question attached to it was whether SVG can
carry this at all, or whether the project needs a CAD or BIM layer underneath to make any of it
work.*

---

## The finding the package exists to record

**SVG was never the constraint, and a CAD or BIM layer could not have fixed it, because a format
serialises what is modelled and cannot invent what is not.**

The proof was already in the tree before this package started. `build/export_dxf.py` exported the
entire eave cornice as **one closed rectangle** and a text note saying how many members it had.
That is not a limitation of DXF, which represents arcs exactly. It is that no layer of this corpus
held a moulding as geometry, so there was nothing for any format to carry. A BIM layer bolted on
underneath would have had the same rectangle to export.

Meanwhile the data was far ahead of every drawing:

- All **502 order-pack members** already carried a machine-readable `profile` from a 29-value
  enum — cyma recta, ovolo, scotia, corona, modillion — at 100% coverage.
- The resolved `tidewater-georgian` kit already stated a ten-course moulded water table, brick
  coursing at exactly 2.75 in, gauged arches with their rise and camber as rules of the opening's
  own width, four-panel shutters, and the chimney's plan size.
- Almost none of it was drawn.

What was missing was the layer in between: **constructed 2D geometry**. This package builds it
once, in Python, and every surface — the two order tools, the elevation sheet, and the DXF
exporter — now consumes the same object. CAD became a second serialisation of that object in
about eighty lines, which is the argument made as working code rather than as a claim.

---

## What was built

### `build/profiles.py` — the constructions, stated once

Turns a dimensioned member list into real geometry. Every shape is a construction from the
member's own two numbers, named in the module docstring:

| profile | construction |
|---|---|
| ovolo / quarter-round / echinus | a convex quarter, elliptical where height and projection differ |
| cavetto / apophyge / congé | the concave quarter |
| cyma recta | the *gola diritta*: hollow below, round above. Two equal tangent arcs meeting at the chord's midpoint, vertical end tangents, `r = (dx² + h²) / 4dx` |
| cyma reversa / ogee | the *gola rovescia*, the same construction reversed, `r = (dx² + h²) / 4h` |
| torus / astragal / bead | a half round, out to the face at mid-height and back |
| scotia | a hollow half its own height deep, two quarters tangent at the throat |
| fillet, fascia, corona, plinth… | a square step; a corona takes a drip only where its own note asks for one |
| volute, acanthus | **not constructed**, reported as such |

The radii fall out of the geometry rather than being chosen, which is the difference between a
construction and a fitted curve. The engine also lays out repeating members tooth by tooth,
implements the OQ 65 datum rule in one place, and serialises to SVG (`L`/`A`) and to DXF vertices
with **bulges**, so a circular arc reaches CAD exactly rather than as a polygon.

`tests/test_profiles.py` (49 tests) and `python3 build/profiles.py selftest` assert **geometry,
not strings**: that an ovolo bulges out of its chord and a cavetto falls inside it, that a cyma's
two arcs meet without a kink, that a torus returns to its springing, that pack geometry is linear
in the module, and that every profile name in the corpus has a construction.

### `width_parts`, transcribed rather than authored

A band of dentils drawn as a solid band is a band of no dentils, and no member carried a tooth
width. Lucas ruled that missing figures could be authored `editorial`. **They did not have to
be.** The widths were already in the corpus, in the members' own notes: *"1/9 D wide (4 parts)"*,
*"1/2 D wide (12 parts)"*, *"two of those parts will be the Dentel"*. Fourteen members across ten
packs now carry `width_parts`, every figure transcribed from its own note with the quotation
recorded beside it. The arithmetic checks itself — Vignola's Doric triglyph at 12 parts and metope
at 18 land exactly on the stated 30-part pitch. `check_orders.py` gained a check that a tooth is
narrower than its own pitch. **No editorial figure was needed and none was written.**

### One geometry, four surfaces, no fifth copy

Pack geometry is linear in the module, which the tests prove rather than assume, so it is computed
once in Python and merely scaled by anything that draws it. `build/orders_template.html` lost its
`segTo()` and `buildGeometry()` — 106 lines of Bézier constants and a duplicate datum rule — and
gained a 30-line mapper that knows only lines and arcs. The workbench plate and the DXF exporter
read the same served segments. **JavaScript no longer knows what a cyma is**, which is stronger
than keeping two implementations in step by test.

### The elevation

Drawn strictly from what the record already held or now derives: brick coursing at the pack's
exact course, the moulded water table as the assembly it is (seven plinth courses, an ovolo
course, a weathering course — ten courses, exactly the height the pack states), gauged flat
arches over every opening switched on the plan's own date, sills, real projections everywhere,
and a five-rung line-weight ladder. The Proportions plate draws true profiles, entasis and all.

---

## What was found

**1. The cornice inset's curves had never been drawn at all.** `profile_silhouette_path()` called
`seg_to()` with `xa == xb` on **every member**, so every curve degenerated to the vertical face it
was drawn between. The profile names in the data were correct and the drawing was a flight of
steps regardless. `tests/test_elevation.py::TestSegTo` pinned that function's control-point
arithmetic exactly — and would have passed just as happily on the day the curves stopped
appearing, because it asserted the string and never the shape. That is the lesson worth keeping:
**pinning the arithmetic of a curve nobody can see is not a guard.**

**2. The projection datum is declared per pack and is not uniform inside one.** (OQ 72.) OQ 65 put
`projection_datum` on the pack and had `check_orders.py` verify it against the shaft. True for the
column; **not true for the entablature in the same packs**, and the packs say so themselves —
`gibbs-ionic` declares `axis` while its frieze face records a projection of **0**, as does its
architrave's lowest fascia, and a frieze cannot stand on the column's centre line. Reading the
declaration literally over a cornice clamps every member narrower than the column radius flush
with the frieze, which **deletes the bed mould and its fillet from the drawing**. `dist/orders.html`
has been drawing it that way since OQ 65 closed. The elevation now detects the entablature's own
datum from evidence; the order tool still needs the ruling.

**This one was found by making a mistake and checking it.** The first fix here applied the
pack-level `axis` reading to the cornice, "confirmed" by noticing that the resulting relief
(10.35 in) sat within 1.7% of `facade-classical`'s independent figure (10.53 in). That agreement
was a coincidence, and taking it as corroboration would have shipped a cornice with no bed mould.
What settled it was reading the pack's own frieze projection instead of trusting a number that
happened to match.

**3. Two sourced rules give the cornice two different projections.** (OQ 73.) Gibbs: *"The
projection of the Cornice equal to its height"* — 24.56 in. `facade-classical`'s envelope rule:
`module / 14` — 10.53 in. Both sourced, both about the same cornice, differing by 2.3×. The record
carries both with a disagreement note and the sheet prints both; nothing picks a winner.

**4. The chimney width was not a missing measurement. It was a deferred one.** Four names sat in
`NOT_MODELLED` reading *"the roof record carries no chimney plan dimension"*, and the plan for this
package was to wire the figure through and delete them. brick-course does carry it —
`chimney/width`, `part * 8`, 22 in — **but the rule is flagged `judgment: true`**, and its note
says why: *"the mason will build 18 or 27 and someone should decide which rather than discovering
it on site."* The sixth settled decision is that a judgment slot is marked, not filled. So the
entries **stay**, with their reasons corrected from "nobody wired it" to "nobody is entitled to",
and the figure reaches the drawing only, labelled. Meanwhile the renderer had been asserting a
hardcoded **36 in** over the top of that very slot — an invented constant of exactly the OQ 52
class, surviving in the drawing where no measurement test could see it. That is now the corpus's
own figure.

**5. The front elevation still cannot show its chimneys.** (OQ 74.) `roof.py`'s long-face
silhouette is flat at the eave — two points, both at 25.44 ft — and models no roof mass above the
cornice. An attempt to draw the portion of each stack clearing the roof was **withdrawn**: with the
silhouette at the eave, that rule puts 22 ft of brick in front of a roof nobody modelled, which is
the same error as reporting an unmodelled chimney as zero. For this style the cost is real — the
kit calls the paired stacks *"visible from a mile away and conclusive against New England"* — and
it is a roof-layer decision, not a renderer's.

**6. A drawing can hold an invented constant long after the measurements are clean.** OQ 52 swept
twelve fabricated figures out of `elevation.py` and is guarded by a test that reads the
measurements dict. It cannot see SVG. The 36 in chimney, the ±4/±2/±6 px projections, and the
fitted-then-discarded inset scale all lived on the other side of that line. **The honesty
discipline needs to reach the renderers, not just the records.**

---

## What was deliberately not done

- **Flemish bond and glazed-header chequer.** Lucas ruled editorial authoring acceptable, and it
  was not needed for anything else in this package; the bond remains a prose string with no brick
  length or header alternation, so drawing a chequer would still be invention. Coursing lines,
  which are fully sourced, are drawn instead. Left for a package that authors the bond assembly
  deliberately rather than in passing.
- **Dormers** — no plan-schema field; `roof.py` refuses; six faults stay could-not-judge.
- **Ornament zones** — OQ 50 ruled to stop at the principle.
- **Cornice corner returns** — the pork-chop-return false-fatal trap.
- **Voussoir joints** — no count and no joint width in the corpus; the arch is drawn as the one
  gauged mass it is, and the two faults measuring voussoirs stay unjudged.
- **The volute's true spiral** — the construction is on a plate this corpus cannot reach (OQ 7-11),
  so it is drawn as a swelling and **reported as unconstructed** on the sheet.
- **A classical entasis construction** — same reason; the smoothstep is kept and said to be one.
- **IFC** — the DXF path proves the argument; a swept `IfcShapeRepresentation` from the same
  polyline is the obvious next step and is named in `docs/export.md`, not hidden.

---

## Verification

`python3 build/check_all.py` — **all 34 checks pass** (33 before; `profiles.py selftest` is new).
906 pytest tests pass, 2 skipped. The workbench e2e walk is green, including the order-plate
checks for stack contiguity, frame containment and the projection datum, which now run against
constructed profile edges. The DXF round-trip invariant holds: identical validator findings on
both reference plans.

**Pins that moved, with reasons:** `TestSegTo` and `TestProfileSilhouettePath` (7 tests) were
deleted — the port they pinned no longer exists, and the reason is recorded in the class comment
of `TestCorniceProfileGeometry`, which replaces them with tests that assert the shape rather than
the string. No fault counts moved: nothing entered `measurements`, because the one candidate
turned out to be a judgment slot.

**New guards:** `tests/test_profiles.py` (49), five elevation tests covering the entablature
datum, the closed profile spanning every member, real arcs where the members are curved, the
two-rule disagreement, and the sheet's own disclosure.

---

## What Lucas asked, answered directly

> *we need a massive increment in the SVG drawing capacity employed in this website, or we need to
> consider an alternate route*

Neither, as posed. The drawing capacity was not the bottleneck and the alternate route would have
inherited the same problem. What was missing was a geometry layer, and with it in place the same
SVG renderers draw real mouldings, real coursing and real arches — and the CAD exporter that
carried one rectangle now carries the same profile, arcs intact, because there is finally
something to carry.
