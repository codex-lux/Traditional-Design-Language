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

## The known disagreements are held by identity

`tests/fixtures/ink_known_disagreements.json` names every row that disagrees today, and
`tests/test_svg_census.py` holds the live set **equal** to it. A new disagreement fails the build;
a fixed one fails it too until it is removed from the file. That is the one-way door
`build/measured_unsourced_grandfathered.json` already uses. It was chosen over `xfail`, which
passes whether or not the defect is still there, and over a permanently red build, because a
suite already red for one cause cannot report a second (WP-13.8's finding about three
`test_composer.py` rows that absorbed a second regression in silence).

## Running it

```
python3 tests/svg_census.py              # the summary: one line per check
python3 tests/svg_census.py --json       # every row, with its figures
python3 tests/svg_census.py --write-doc  # regenerate the two tables below
```

The census runs in under a second on the standard library. It reads the COMMITTED plates, which
are what `/corpus/assets/generated/*.svg` serves; `P12` holds them to the renderer's current
output, so a plate nobody re-rendered is a disagreement rather than a silent drift.

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
| elevation | producer | `build/render_elevation.py` | elevation sheets, each with an eave-cornice profile inset |
| section | producer | `build/render_section.py` | the building section and the bearing diagram |
| roof | producer | `build/render_roof.py` | the roof plan |
| plan | producer | `build/render_plan.py` | the plan sheet (presentation and working registers) |
| bench-sheet | producer | `workbench/app/src/sheet/Sheet.jsx` | the Plan Workbench's live sheet, drawn in JavaScript |
| transcription | producer | `workbench/app/src/surfaces/Transcription.jsx` | the Transcription draft canvas (a person's own tracing) |
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
| P1 | profile-plates | the column diameter a plate prints is the diameter it is drawn at | every committed profile plate | 73 | 61 | 12 | 0 |
| P2 | profile-plates | the relief a plate prints is the relief its ink draws | every committed profile plate | 73 | 68 | 5 | 0 |
| P3 | profile-plates | no ink falls inside the assembly's own naked (a moulding bitten into the member it stands on) | every committed profile plate | 73 | 67 | 6 | 0 |
| P4 | profile-plates | every mark of ink is inside the plate's viewBox | every committed profile plate | 73 | 71 | 2 | 0 |
| P5 | profile-plates | every member boundary the record states is a drawn vertex, and the drawn height is the stated height | every committed profile plate | 73 | 73 | 0 | 0 |
| P6 | profile-plates | a member whose face is at its mid-height (a step or a half round) is drawn out to the face its record states | members with a published projection | 73 | 68 | 0 | 5 |
| P7 | profile-plates | a member the record gives no projection for is SAID to have none, not drawn as though measured flush | plates holding an unpublished member | 11 | 0 | 11 | 0 |
| P8 | profile-plates | a member the plate calls NOT CONSTRUCTED has no curve drawn for it | plates holding a volute or acanthus member | 10 | 0 | 10 | 0 |
| P9 | profile-plates | a plate showing another authority's members says whose they are | every committed profile plate | 73 | 73 | 0 | 0 |
| P10 | profile-plates | a member whose record confidence is not high is marked as such on the plate | plates holding a medium- or low-confidence member | 65 | 0 | 65 | 0 |
| P11 | profile-plates | a curved member drawn as a straight line says so | plates holding a curved profile kind | 53 | 46 | 7 | 0 |
| P12 | profile-plates | the committed plate is the renderer's current output | every committed profile plate | 73 | 73 | 0 | 0 |
| E1 | order-stack | the column drawn (base + shaft + capital) is the column height the pack states | order packs stating a column height | 25 | 18 | 5 | 2 |
| E2 | order-stack | the entablature drawn is the one the pack itself states | order packs that state a whole entablature | 25 | 21 | 4 | 0 |
| E3 | order-stack | an assembly offered as an ALTERNATIVE to another is never stacked on it (Benjamin's subplinth stands a column instead of a pedestal) | order packs stating a subplinth | 3 | 0 | 3 | 0 |
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
