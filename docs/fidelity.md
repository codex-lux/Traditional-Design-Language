# Fidelity — the ink held to its plates

Phase 14's layer doc (WP-14.1 onward). Lucas asked whether the drawn trim, casings, column and
entablature profiles, and every other drawn figure, reflect the plates and dimensions researched
to source them, on **every** surface that generates SVG. This file is the standard that question
is answered to, and the live answer.

The precedent is WP-5.11 (`docs/reports/wp-5.11-real-2d-geometry.md`), whose adversarial addendum
found that *"a green suite proved the model and said nothing about the drawing"*: 245 arcs were
drawn as their own mirror while every check interrogated the model. So nothing here asks a
renderer what it meant to draw. It reads the SVG a reader is served, back through
`tests/inkread.py`, and holds that to the record.

## The chain

Every architectural drawing here is the last of three translations, and a figure can go wrong at
each one. The words printed beside the ink are a fourth thing that can disagree, and the same
object drawn on two surfaces is a fifth.

| link | from → to | what holds it |
|---|---|---|
| 1 | the source plate → the record | the record's own quoted figures, its arithmetic, its invariants and its module conversions (WP-14.5); the plates themselves are unreachable from here (§ Sources) |
| 2 | the record → the model | `proportion_engine.resolve()`, `dimension()`, `stack_for()`; `profiles.pack_geometry()` |
| 3 | the model → the ink | each renderer, read back from its emitted SVG |
| 4 | the ink → the words | labels, dimension strings, captions, provenance lines |
| 5 | surface ↔ surface | one object drawn in two places draws one way |

## The verdicts

Every check answers one of three things, and the population it was asked over is printed beside
it, so a zero reads as a zero and not as a pass:

- **agrees**;
- **disagrees**, with the figures;
- **could not evaluate**, with the reason. *Unjudged is not passed.*

Every defect falls into one of four classes, and the class decides the remedy:

- **A. The ink does not draw the record.** Fixed.
- **B. The record does not say what its own quoted authority says.** Fixed only where the
  corpus's own quotation proves it (OQ 81's precedent); otherwise an open question or a line in
  `Plan Examples/Plates/WANTED.md`.
- **C. The record states it and no surface draws it.** Drawn.
- **D. An unpublished, apportioned, editorial or judgment figure drawn as if it were measured.**
  Marked on the plate and said in words.

## The known disagreements are held by identity, with their figures

`tests/fixtures/ink_known_disagreements.json` names every row that disagrees today and what it
measured, and `tests/test_svg_census.py` holds the live map **equal** to it. A new disagreement
fails the build. A fixed one fails it too, until it is removed from the file. So does one whose
figures moved, until a commit re-pins it and says which way and why. That is the one-way door
`build/measured_unsourced_grandfathered.json` already uses. It was chosen over `xfail`, which
passes whether or not the defect is still there, and over a permanently red build, because a
suite already red for one cause cannot report a second (WP-13.8's finding about three
`test_composer.py` rows that absorbed a second regression in silence).

**The figures are pinned because ids alone were measured blind.** The first version held only
the ids. Corrupting V1's own rung table, and making V5 count the wrong muntins, both left the
build green: every V1 and V5 row already disagreed, so a change in *what* a row reported could
not be seen. The same finding, one level down: a row red for one cause cannot report a second
unless its figures are held as well as its verdict.

## Running it

```
python3 tests/svg_census.py              # the summary: one line per check
python3 tests/svg_census.py --json       # every row, with its figures
python3 tests/svg_census.py --write-doc  # regenerate the two tables below
```

The census runs on the standard library, in about half a minute: 25.8 s on 27 Sep 2026, on
the WP-14.5 tree. This sentence said "under a second" from WP-14.1, when the census read the
profile plates alone, and it went on saying so while the census grew to sixty checks over the
building sheets. It reads the COMMITTED plates, which are what `/corpus/assets/generated/*.svg`
serves; `P12` holds them to the renderer's current output, so a plate nobody re-rendered is a
disagreement rather than a silent drift.

## Every surface that draws

A claim about *every* surface is only as good as the list it is made over, so the list is data:
`REGISTRY` in `tests/svg_census.py`. `tests/test_svg_census.py` greps every tracked file for
anything that emits SVG and fails on a file the registry does not name, so a new surface cannot
join the app without either a census row or a stated reason it is not an architectural drawing.

<!-- census:registry:begin -->
| id | role | file | surface / reason |
|---|---|---|---|
| profile-plates | producer | `build/render_profile.py` | 73 moulding-profile plates committed under assets/generated/ |
| orders-tool | producer | `build/orders_template.html` | the order-drawing tool dist/orders.html (half section, mirrored elevation) |
| proportions-plate | producer | `workbench/app/src/surfaces/Proportions.jsx` | the workbench Proportions plate (half section of each order pack) |
| assembly-plate | producer | `workbench/app/src/components/AssemblyPlate.jsx` | the workbench Proportions plate of a pack drawn as assemblies (`drawing: "assemblies"`): each assembly's served faces at the wall datum, one frame each. The other Phase 14's WP-14.9, registered at the merge (27 Sep 2026). NO CENSUS CHECK READS IT, so every figure it draws is unjudged here; its faces are Python's (`profiles.pack_geometry(datum="wall")`) and its layout is held by that line's own `plate/assembly*.test.mjs` |
| elevation | producer | `build/render_elevation.py` | elevation sheets, each with an eave-cornice profile inset |
| section | producer | `build/render_section.py` | the building section and the bearing diagram |
| roof | producer | `build/render_roof.py` | the roof plan |
| plan | producer | `build/render_plan.py` | the plan sheet (presentation and working registers) |
| bench-sheet | producer | `workbench/app/src/sheet/Sheet.jsx` | the Plan Workbench's live sheet, drawn in JavaScript |
| transcription | producer | `workbench/app/src/surfaces/Transcription.jsx` | the Transcription draft canvas (a person's own tracing) |
| sheet-style | helper | `build/sheet_style.py` | the sheets' palette, pens and type, the `data-frame` attribute and the one escape for a double-quoted attribute's value |
| profiles-geometry | helper | `build/profiles.py` | the moulding constructions and their SVG path serialiser |
| drawing-set | carrier | `workbench/app/src/surfaces/DrawingSet.jsx` | injects the server's plan/elevation/section/roof SVG; offers it for download |
| export-details | carrier | `workbench/app/src/surfaces/ExportDetails.jsx` | downloads the server's presentation-register SVG |
| round-plates | carrier | `workbench/app/src/round/RoundPlate.jsx` | lays the Python plates over the 3D model by their data-frame |
| taxonomy-timeline | out-of-scope | `build/template.html` | the taxonomy page's timeline and ruler: a chart of dates, not a drawing of a building |
| phylogeny | out-of-scope | `workbench/app/src/surfaces/Phylogeny.jsx` | the lineage graph: a diagram of influence between styles |
| atlas | out-of-scope | `workbench/app/src/surfaces/phylo/MapView.jsx` | the atlas: coastlines and a graticule, not architecture |
| tokens | out-of-scope | `workbench/app/src/theme/tokens.css` | a stylesheet that names <svg> in a comment; it draws nothing |
<!-- census:registry:end -->

## The checks

<!-- census:checks:begin -->
| check | surface | statement | population | rows | agrees | disagrees | could not evaluate |
|---|---|---|---|---:|---:|---:|---:|
| P1 | profile-plates | the column diameter a plate prints is the diameter it is drawn at | every committed profile plate | 73 | 73 | 0 | 0 |
| P2 | profile-plates | the relief a plate prints is the relief its ink draws | every committed profile plate | 73 | 73 | 0 | 0 |
| P3 | profile-plates | no ink falls inside the assembly's own naked (a moulding bitten into the member it stands on) | every committed profile plate | 73 | 73 | 0 | 0 |
| P4 | profile-plates | every mark of ink is inside the plate's viewBox | every committed profile plate | 73 | 73 | 0 | 0 |
| P5 | profile-plates | every member boundary the record states is a drawn vertex, and the drawn height is the stated height | every committed profile plate | 73 | 73 | 0 | 0 |
| P6 | profile-plates | a member whose face is at its mid-height (a step or a half round) is drawn out to the face its record states | members with a published projection | 73 | 68 | 0 | 5 |
| P7 | profile-plates | a member the record gives no projection for is SAID to have none, not drawn as though measured flush -- and a plate where every member publishes one says that | every committed profile plate | 73 | 73 | 0 | 0 |
| P8 | profile-plates | a member the plate calls NOT CONSTRUCTED has no curve drawn for it | plates holding a volute or acanthus member | 10 | 10 | 0 | 0 |
| P9 | profile-plates | a plate showing another authority's members says whose they are | every committed profile plate | 73 | 73 | 0 | 0 |
| P10 | profile-plates | a member whose record confidence is not high is marked as such on the plate -- in its own label, and by a dashed outline over its own height | plates holding a medium- or low-confidence member | 65 | 65 | 0 | 0 |
| P11 | profile-plates | a curved member drawn as a straight line says so -- curved by its profile kind or by its own name | plates holding a curved member | 65 | 65 | 0 | 0 |
| P12 | profile-plates | the committed plate is the renderer's current output | every committed profile plate | 73 | 73 | 0 | 0 |
| P14 | profile-plates | the review note a plate's record carries is the internal verdict the plate earns now, says the source was not evaluated, and approves nothing | every committed profile plate | 73 | 73 | 0 | 0 |
| P13 | profile-plates | a part the assembly's own members are named for, and no member records, is said on the plate -- not drawn as though the section were the whole | plates whose members are named for a part no member records | 4 | 4 | 0 | 0 |
| E1 | order-stack | the column drawn (base + shaft + capital) is the column height the pack states | order packs stating a column height | 25 | 25 | 0 | 0 |
| E2 | order-stack | the entablature drawn is the one the pack itself states | order packs that state a whole entablature | 25 | 25 | 0 | 0 |
| E3 | order-stack | an assembly offered as an ALTERNATIVE to another is never stacked on it (Benjamin's subplinth stands a column instead of a pedestal) | order packs stating a subplinth | 3 | 3 | 0 | 0 |
| E4 | order-stack | the pedestal's die stands on a face the record gives -- the base's plinth as drawn -- or, where the base publishes none, the geometry says the die is not derived and why, and stands it on the column's own radius rather than on a stand-in figure | order packs drawing a pedestal | 23 | 23 | 0 | 0 |
| O1 | orders-tool | the committed page is what build/render_orders.py builds now | the one page | 1 | 1 | 0 | 0 |
| O2 | orders-tool | the section the page draws is the height the engine dimensions, at every diameter it offers, pedestal on and off | every order pack with a stack x 12/24/36 in x pedestal | 150 | 150 | 0 | 0 |
| O3 | orders-tool | the section reaches as far out as the geometry Python constructed for it, scaled to the diameter drawn | every order pack with a stack x 12/24/36 in x pedestal | 150 | 150 | 0 | 0 |
| O4 | orders-tool | an invariant the engine could not judge is not printed FAIL | driven: one invariant set unjudged (every one of 169 holds today) | 1 | 1 | 0 | 0 |
| O5 | orders-tool | every order pack the page carries can be reached from its controls | every order pack in the page | 26 | 26 | 0 | 0 |
| O6 | orders-tool | the flute lines on the elevation fall where the stated number of flutes projects | fluted order packs, at 12 in, pedestal on | 20 | 20 | 0 | 0 |
| O7 | orders-tool | a member the record publishes no projection for is bracketed at its naked on the orders page and counted in its panel -- and a stack where every member publishes one says that | every order pack with a stack, at 12 in with the pedestal | 25 | 25 | 0 | 0 |
| O8 | orders-tool | a member the orders page calls NOT CONSTRUCTED is drawn as its dashed envelope and counted | every order pack with a stack, at 12 in with the pedestal | 25 | 25 | 0 | 0 |
| O9 | orders-tool | a curved member the orders page draws as a straight line is counted as one | every order pack with a stack, at 12 in with the pedestal | 25 | 25 | 0 | 0 |
| O10 | orders-tool | the datum the orders page states for each assembly is the datum that assembly was drawn on | every order pack with a stack, at 12 in with the pedestal | 25 | 25 | 0 | 0 |
| O11 | orders-tool | what the stack leaves out -- an assembly offered instead of another, an inherited entablature that contradicts the pack's own -- is said on the orders page | every order pack with a stack, at 12 in with the pedestal | 25 | 25 | 0 | 0 |
| R1 | proportions-plate | the plate's frame holds its own ink (the dimension gutter begins where the widest moulding ends) | order packs the plate draws, at 12 in | 25 | 25 | 0 | 0 |
| R2 | proportions-plate | the members the plate says publish no projection are exactly the members whose record states none (the shaft's own body, which is the column, excepted) | order packs the plate draws, at 12 in | 25 | 25 | 0 | 0 |
| R3 | proportions-plate | the datum the plate's caption states for each assembly is the datum that assembly was drawn on | order packs the plate draws, at 12 in | 25 | 25 | 0 | 0 |
| R4 | proportions-plate | what the stack leaves out -- an assembly offered instead of another, an inherited entablature that contradicts the pack's own -- is said on the plate | order packs the plate draws, at 12 in | 25 | 25 | 0 | 0 |
| V1 | elevation | every mark carrying a line-weight rung is drawn at that rung's width | every elevation sheet (plans x faces) | 44 | 44 | 0 | 0 |
| V2 | elevation | nothing the style's resolved kit forbids is drawn, slot or variant (the row names where each prohibition comes from) | every node with a kit, on the Tidewater placement | 159 | 20 | 21 | 118 |
| V3 | elevation | every transom or sidelight variant the style's kit makes canonical is drawn, or the sheet says why it is not | every node with a kit, on the Tidewater placement | 19 | 19 | 0 | 0 |
| V18 | elevation | a drawn transom is divided into sash-light's own count of lights at the width it is drawn, evenly, as the sheet says | every node with a kit whose elevation draws a transom, on the Tidewater placement | 9 | 9 | 0 | 0 |
| V19 | elevation | the elevation draws its roof at the eave and ridge the roof record states -- where the section prints them and the model builds them | every plan whose elevation draws a roof | 11 | 0 | 11 | 0 |
| V4 | elevation | each shutter leaf is (opening - 1 in) / 2, sash-light's own rule, 'so that the pair actually covers the window when closed' | elevation sheets drawing shutters | 15 | 15 | 0 | 0 |
| V5 | elevation | the lights drawn in a sash are sash-light's own count for the width the window is drawn at | elevation sheets drawing a glazed sash | 27 | 27 | 0 | 0 |
| V14 | elevation | a sash is drawn as the members sash-light states -- its jambs, 2 in stiles and top, bottom and meeting rails -- with its glass divided into the lights its rule gives, each at the rule's light width | elevation sheets drawing a glazed sash | 27 | 27 | 0 | 0 |
| V16 | elevation | a window surround the style's kit makes canonical is drawn, or the sheet says why it is not | the shipped plans' fronts, and every node with a kit whose elevation is drawn, on the Tidewater placement | 49 | 49 | 0 | 0 |
| V6 | elevation | a door the plan calls a garage door is not drawn as a six-panel leaf | plans placing a garage door on an elevation face | 4 | 4 | 0 | 0 |
| V17 | elevation | a stack is one stack on every face that draws it: on the square the placement seats, its top at one height, standing as far above the drawn ridge as the record stands it above its own | plans whose elevation draws a stack, every face | 1 | 1 | 0 | 0 |
| V21 | elevation | the eave inset stands clear of the face it details: no mark of the face is drawn inside the inset's box | elevation sheets: shipped plans, every face, and every style's front | 85 | 85 | 0 | 0 |
| V20 | elevation | no window, sidelight, transom, door leaf or shutter leaf is drawn over another, and the doorcase over none of them but its own door | elevation sheets: shipped plans, every face, and every style's front | 69 | 69 | 0 | 0 |
| V22 | elevation | every opening whose record refuses its sidelights or its shutter leaves is said on its own sheet: a SIDELIGHTS NOT DRAWN line for each doorcase refused, one SHUTTERS NOT DRAWN line counting every window refused its leaves and naming every room, and, where the record gives more than one reason, a line for each reason counting and naming its own | elevation sheets whose record refuses a sidelight or shutter pair, or that say one is refused: shipped plans, every face, and every style's front | 53 | 53 | 0 | 0 |
| V23 | elevation | a stack stands on what it stands on: an exterior stack in front of the face stands its foot on the ground line the sheet draws, the ground line runs past it, and it is drawn over no opening; a stack the house hides stands its foot on the roof the sheet draws; and the legend says each of the two it drew and neither it did not | elevation sheets that draw a stack: shipped plans, every face, and every style's front | 19 | 19 | 0 | 0 |
| V24 | elevation | the wall each side of the entrance doorcase, as drawn, touches no flanking window and is at least half the ordinary pier where a parti states the bay; and the legend says each side that touches or falls short, and that the floor is not judged where no parti states the bay | elevation sheets that draw a doorcase with a window beside it: shipped plans, every face, and every style's front | 43 | 42 | 0 | 1 |
| V25 | elevation | the eave is drawn as its record states it: the frieze at its own projection, the cornice's box at the one reading of the band's projection, a line at every member division the record states and no other, the legend saying each band it drew flush for want of a figure, and a stack that overlaps the cornice painted over it where it stands in front of the face and under it where it stands behind | every elevation sheet (plans x faces), and every style's front | 85 | 85 | 0 | 0 |
| V7 | elevation | an arched head is drawn as the circular segment it is set out as, not a parabola | elevation sheets drawing an arched head: shipped plans, and every style's front | 31 | 31 | 0 | 0 |
| V8 | elevation | a figure its own rule marks judgment is not published as a measurement | plans whose elevation draws | 11 | 11 | 0 | 0 |
| V9 | elevation | a size no record gives is neither drawn nor left unsaid: the keystone the kit makes canonical with no width, and a stack the roof places with no plan size | sheets whose record carries a keystone or a stack: shipped plans, and every style's front | 27 | 27 | 0 | 0 |
| V11 | elevation | an opening or a belt that misses the brick courses the sheet draws is said to | masonry elevation sheets | 3 | 3 | 0 | 0 |
| V13 | elevation | the eave inset draws every cornice member at the height and face its record states | elevation sheets drawing the eave inset | 11 | 11 | 0 | 0 |
| S1 | section | exterior walls are drawn as bodies of the thickness the record states | plans whose section draws | 16 | 16 | 0 | 0 |
| S2 | section | each storey's floor structure is drawn between its own ceiling and the floor above it (the eave, at the top storey), at the depth the record states | plans whose section draws and whose storeys state a floor structure | 16 | 16 | 0 | 0 |
| S3 | section | every mark on the section and bearing sheets lies inside the sheet | plans whose section draws: the section and the bearing diagram | 32 | 32 | 0 | 0 |
| F1 | roof | a chimney stack is drawn at the plan size the record states, on BOTH sides, on the square the placement seats, and a judged size is said to be one | plans whose roof plan draws a stack | 1 | 1 | 0 | 0 |
| X1 | elevation | the DXF elevation draws the sidelights the SVG draws beside the doorcase | plans whose entrance SVG draws sidelights | 2 | 2 | 0 | 0 |
| X2 | elevation | the DXF elevation draws every window's sash and the entrance transom's lights member for member as the SVG draws them, and carries the transom's height as a judgment | every face of every plan whose elevation draws a sash or a transom | 27 | 27 | 0 | 0 |
| X3 | elevation | the DXF elevation draws every stack the SVG draws, on the same outline in the face's own inches, stands a stack drawn from grade on its grade line, and carries each stack's square and its judgment | every face of every plan whose elevation draws a stack | 4 | 4 | 0 | 0 |
| X4 | elevation | the DXF elevation draws the eave the SVG draws: the frieze band and the cornice's box on the same outlines in the face's own inches, and a line at every member division the SVG draws, each carrying the member it names | every face of every plan whose elevation draws | 44 | 44 | 0 | 0 |
| P15 | profile-plates | a plate's alt text names the members the plate draws, bottom to top, with the heights the record gives them | every committed profile plate | 73 | 73 | 0 | 0 |
| N0 | record | every note that states a figure has been read into build/note_figures.json, and every row there still quotes its note verbatim | order-pack member notes stating a number; the measured kit parameters the elevation reads whose note states one; every overlay's module note | 424 | 424 | 0 | 0 |
| N1 | record | a figure a member's note states about a recorded figure is the figure the record carries | order-pack members whose note states a figure about a recorded one | 265 | 251 | 14 | 0 |
| N2 | record | an overlay converts every figure it inherits by the factor its own module note states | every overlay pack | 18 | 18 | 0 | 0 |
| N3 | record | a figure a measured kit parameter's note states about the parameter is the figure the parameter carries | measured kit parameters the elevation reads whose note states a figure about theirs | 68 | 62 | 6 | 0 |
| PL1 | plan | a bay grid is drawn on a module the record states, or the sheet says the module is a default | every plan sheet, working register | 16 | 16 | 0 | 0 |
| PL2 | plan | every exterior opening is cut out of the wall body of its OWN element's face, and no exterior wall body is broken where the record places no opening | every exterior door and window on every placed level of every plan sheet, and every break in an exterior wall body, working register | 16 | 16 | 0 | 0 |
| PL3 | plan | no wall body is drawn over another -- a wall two elements share is one wall | every pair of wall bodies on every plate of every plan sheet, working register | 16 | 16 | 0 | 0 |
| B1 | bench-sheet | every window, exterior door and door onto an at-grade appendage the bench draws is cut in its OWN wall: outside its room's own face, as deep as the wall the record states | every exterior opening, and every interior door standing in an exterior wall (a door onto an at-grade appendage), on every placed level of every plan, as the bench computes it | 16 | 16 | 0 | 0 |
| B2 | bench-sheet | the bench is served the plate's own wall bodies for every placed level -- the envelope of every element, the joins, the bearing lines, the partitions and their holes | every placed level of every plan | 16 | 16 | 0 | 0 |
| TR1 | transcription | the tracing canvas draws each traced room at the draft's own feet (y flipped into the screen) and the backdrop at the width stated and its own aspect | every placed room of every plan, traced as a draft, on a backdrop of the plan's own aspect | 16 | 16 | 0 | 0 |
<!-- census:checks:end -->

## What each plate states about itself

A plate that says what its own pixels mean can be read back without re-deriving its scale from
the renderer's arithmetic, which would be checking the renderer against itself. Every plate states
a `data-frame` on its root, in `sheet_style.frame_attr`'s one affine:

    px_x = origin_px[0] + (u - at_origin[0]) * k
    px_y = origin_px[1] + (at_origin[1] - v) * k

with `k` as `px_per_ft` on the plan, section, roof and elevation, and `px_per_in` on a profile
plate. A profile plate's frame (WP-14.1) gives `u` as inches out from the column's axis, with the
assembly's naked at `at_origin_in[0]`, and `v` as inches up the stack. It also carries the `datum`
the assembly was drawn on: `profiles.axis_holds_for`'s per-group answer, which is what `P6`
measures each face from.

Adding the frame moved the 73 plates by that attribute and by nothing else. The committed files
reproduce their 73 manifest digests, and each fresh render with its `data-frame` removed equals
its committed file byte for byte. The digests were re-pinned only after both held.

## Sources

Every host a pack cites refused a CONNECT from here: archive.org, www.loc.gov and tile.loc.gov,
HathiTrust, upload and commons.wikimedia.org, and polito.it each answered `CONNECT tunnel failed,
response 403` on 26 Sep and again on 27 Sep 2026. Tavily is not authorized in this environment.
So link 1 is held by internal checks, never by a reading of the plate, and nothing here may be
closed from a secondary source or a modern redrawing (CLAUDE.md, OQ 7–11). What a person has to
fetch is listed in `Plan Examples/Plates/WANTED.md` (WP-14.5), on the WP-9.2 HABS precedent.

### What the internal checks can say, and what they cannot (WP-14.5)

- **A figure is held to the sentence beside it.** `build/note_figures.json` holds, for every note
  that states a number, what it states about which recorded figure, with the quote it rests on.
  Agents read the notes and the lead verified them. `build/plate_review.py` evaluates both sides
  over the record's own numbers on every run, so the arithmetic is never the table's. Each quote
  is held to be a verbatim substring of its note, so an edited note makes its row stale (N0)
  rather than silently wrong.
- **N1 and N3 say "states", not "quotes from its authority".** Many of these figures are the
  transcriber's own arithmetic on the author's words, and a note is not a plate. An `agrees`
  means the record and the sentence beside it agree. Whether either one agrees with the plate is
  `SOURCE: COULD NOT EVALUATE` on every plate's review note.
- **A note that states nothing cannot disagree.** The population is bounded by what the
  transcriber chose to quote. Gibbs's rule that a pedestal cap projects two thirds of its height
  is quoted in the Tuscan's note, where the cap follows it, and in the Composite's, where N1 sees
  the cap one part short. The Ionic's and Corinthian's caps are short by 1.1 and 1 parts, their
  notes do not quote the rule, and N1 does not see them.
  `oq/a-members-note-states-a-figure-its-record-does-not-carry` records them.
- **A claim counts on the plate whose record it judges.** When one pack's note states a figure
  about another pack's record, the claim reaches that other pack's plate: Palladio's Corinthian
  base note disputes his Doric base's plinth, so it is the Doric plate that reads DISAGREES.
- **An overlay's conversion is read from its output.** N2 compares every figure an overlay
  inherits against the base's figure times the factor its own module note states in words. The
  engine takes its factor from a different record: the module's numeric `diameters` on 25 of the
  26 order packs, and the module's name on the one that states none (`moorish-arch`).
- **What a person must fetch.** Every figure a note disputes is class 0 of
  `Plan Examples/Plates/WANTED.md`, under the book that settles it. That list is generated from
  the same judgment N1 pins.
