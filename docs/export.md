# Export — DXF and IFC (WP-5.1)

The IR leaves the system in the two formats a drafter and a BIM tool actually
open. Both are generated from the same records the SVG renderers draw from —
`geometry.solve()`, `structure.build_section()`, `roof.build_roof()`,
`elevation.build_elevation()` — never re-derived, never traced off a screen.

```
python3 build/export_dxf.py plans/tidewater-georgian-careful.json --outdir dist/dxf
python3 build/export_ifc.py plans/tidewater-georgian-careful.json
python3 build/import_dxf.py dist/dxf/tidewater-georgian-careful-plan.dxf --out roundtrip.json
python3 build/export_dxf.py selftest     # the round-trip acceptance, both check plans
python3 build/export_ifc.py selftest     # the IFC acceptance surface, both check plans
```

Both are also live in the workbench's Details & Export surface
(`POST /api/export/dxf`, `POST /api/export/ifc`).

## The DXF set

One file per sheet — plan, section, roof plan, elevation — model space in
**inches** ($INSUNITS=1, architectural units; the record's feet × 12), model y
north, levels overlaid at the origin on level-suffixed layers a drafter
toggles. Layers are per element group: `TDL-L0-WALL`, `TDL-L0-ROOM`,
`TDL-L0-WINDOW`, `TDL-L0-DOOR`, `TDL-L0-ANNO`, `TDL-GRID`, `TDL-SITE`,
`TDL-TITLE`, `TDL-META`; `TDL-SECT-*`, `TDL-ROOF-*` (eave / ridge / hip /
gambrel-break / cross on their own layers), `TDL-ELEV-*`.

Two deliberate departures from the SVG renderers, because a DXF is a measured
drawing and the SVG is a presentation: window openings are drawn at **true
recorded width** (the SVG shrinks to 0.9× for legibility), and door openings at
the door's **own recorded width** (the SVG uses a fixed 3 ft). A test pins the
first (`tests/test_export.py::test_windows_drawn_at_true_width_not_the_svg_shrink`).

## What the DXF carries, and where

The judgment the whole package rests on, stated in `export_dxf.py`'s header:

- **Geometry comes from geometry.** Rooms, footprint, openings, grid, lot —
  drawn entities at true size.
- **Facts of record ride on the entities they describe**, the way a sheet
  carries its schedules: each room polyline carries its own record (minus
  solved geometry) as XDATA under appid `TDL`; the plan's non-room facts
  (style, massing, groupings, context, site, declared, measurements,
  adjacencies) ride on a `TDL-META` marker at the origin. Solver output
  (`geometry`, `footprint`, `geometry_report`) is never carried — the
  round-trip returns the *authored* record.
- **The linework validates the data.** Drawn window and door entities carry
  cross-reference headers, and the importer refuses when drawing and carried
  record disagree — a tampered window width is a refusal with the disagreement
  named, not a silent preference for either side.

## The round-trip, which is the acceptance

`build/import_dxf.py` reads a TDL-emitted plan DXF back into a plan record and
`plan_check` must return **the same findings** — pinned exactly, plus the
stronger property that the rebuilt record deep-equals the authored one
(`tests/test_export.py`). The reader is deliberately minimal: it reads this
exporter's conventions and refuses anything else by name — a general drafter-
drawing importer is WP-5.5, which will generalize it.

## The IFC model

IFC4, lengths in **feet** (a conversion-based unit; if the unit API refuses,
the file falls back to SI metres and the result says so). Walls (exterior /
bearing / partition thickness from `structure.wall_thickness()`, exterior
walls with their inner face on the clear line), floor slabs, spaces per placed
room, windows with `IfcOpeningElement`/`IfcRelFillsElement` in their exterior
walls, doors on their shared walls, and the roof. Every product carries a
`TDL` property set with `plan_id`, `style` and its `tdl_id`, so any element
traces back to the record.

## What is honestly not modelled, per element

- **Roof geometry beyond the plain gable family.** A hip, gambrel or
  cross-gable roof is an `IfcRoof` with form, pitch and ridge heights as
  properties and a `geometry_note` naming the gap — not a guessed solid. The
  spec Colonial's *unjudged pitch* takes the same path: a note, no planes, and
  a test pins that.
- **Vertical opening data the record does not state.** A window without
  `height_ft` is an `IfcWindow` carrying its record and the reason it has no
  body. Where geometry is emitted, the sill preference chain is: the record's
  own `sill_ft` first (the schema has carried it since 0.1.0 — OQ 36 was
  corrected on exactly this point),
  else `window_head_ft − height_ft` when the record states a head, else an
  editorial 2.5 ft default *named as editorial in the Pset* — same for the
  6 ft 8 in door leaf.
- **The elevation DXF inherits WP-3.2's scope gate.** A style outside the
  classical-front family gets the generator's own stated refusal, rendered as
  a refusal — never a guessed facade.
- Chimneys, stairs, trim, materials — out of scope, see the WP report.

## Dependencies, honestly optional

`ezdxf` and `ifcopenshell` are the toolchain's first third-party dependencies,
and they are **optional**: every entry point refuses with a stated
`could not export … not installed` (`unexported: true` — the OQ 35 pattern),
the workbench endpoint returns that refusal as a 501, and the two selftests
exit 3, which `check_all.py` reports as `N/EV — COULD NOT EVALUATE`, listed by
name and never counted as a pass. Unjudged is not passed, applied to the check
suite itself.
