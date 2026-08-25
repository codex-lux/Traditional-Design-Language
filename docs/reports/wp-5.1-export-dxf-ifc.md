# WP-5.1 — Export: DXF and IFC

*25 August 2026. Ruling context: four calls settled with Lucas before the build —
a minimal DXF reader now, scoped to TDL's own emitted files (WP-5.5 generalizes);
the workbench Export card wired live; ezdxf/ifcopenshell as optional dependencies
behind honest refusals; DXF in inches.*

## What was built

- **`build/export_dxf.py`** — one DXF per sheet (plan, section, roof plan,
  elevation), model space in inches, layers per element group (`TDL-Ln-WALL`,
  `-ROOM`, `-WINDOW`, `-DOOR`, `-ANNO`; `TDL-GRID`, `TDL-SITE`, `TDL-TITLE`,
  `TDL-META`; `TDL-SECT-*`, `TDL-ROOF-*`, `TDL-ELEV-*`), levels overlaid on
  level-suffixed layers. The design judgment the package rests on is in the
  module header and `docs/export.md`: geometry is drawn; facts of record ride
  as XDATA on the entities they describe (a room polyline carries its room
  record minus solved geometry; a `TDL-META` marker carries the plan's
  non-room facts); the drawn linework carries cross-reference headers so the
  importer can check drawing against record. Solver output is never carried —
  the round-trip returns the authored record.
- **`build/import_dxf.py`** — the minimal reader, per the ruling. Rebuilds the
  record from carried XDATA, cross-checks every drawn window leaf (count and
  true width) and door against it, and **refuses with the disagreement named**
  on any mismatch, on a non-TDL DXF, and on a missing library. Never guesses,
  never patches.
- **`build/export_ifc.py`** — IFC4, lengths in feet (conversion-based unit,
  stated SI fallback): storeys from `storey_heights`, walls from
  `wall_lines`/`wall_thickness` (exterior walls inner-face on the clear line),
  floor slabs, spaces per placed room, windows with real
  `IfcOpeningElement`/`IfcRelFillsElement` voids in their exterior walls,
  doors on their shared walls, roof as two pitched planes for the plain gable
  family. Every product carries `plan_id`, `style` and its `tdl_id` in a
  `TDL` property set.
- **The acceptance round-trip**, exceeded: DXF → plan record → validator gives
  the same findings on both check plans, *and* the rebuilt record deep-equals
  the authored one. `python3 build/export_dxf.py selftest` runs it; 13 tests in
  `tests/test_export.py` pin it plus the refusal paths; `ezdxf`'s own audit
  reports 0 errors on the emitted files.
- **`check_all.py` learned a third state.** Exit code 3 from a check now
  reports as `N/EV — COULD NOT EVALUATE`, listed by name, not failing the
  suite and *never* printed as OK. The exporters' selftests are checks 21–22;
  without the optional libraries they take that path. Unjudged is not passed,
  applied to the check suite itself.
- **The workbench Export card is live** (`POST /api/export/{dxf,ifc}`,
  `corpus.export_cad()`, the DXF·IFC card moved out of the forthcoming set
  with per-sheet chips; refusals render stated, missing-library as 501). Five
  new server tests (35 total); the e2e walk's assertion moved from "WP-5.1 is
  not built" to "DXF/IFC live".

## What was found

- **A measured drawing exposed two presentation licenses in the SVG
  renderers.** `render_plan.py` draws window openings at 0.9× their recorded
  width and every door at a fixed 3 ft regardless of `width_ft`. Right for a
  presentation drawing, wrong for CAD — the DXF draws true recorded widths,
  the SVGs are left as they are, and a test pins the difference.
- **Exterior door placement is nobody's record.** The plan record says
  `{to: "exterior"}` with no wall; the plan renderer skips these; the
  elevation generator places the entrance by composition, not by the room
  record. In the IFC they are data-only `IfcDoor`s with a `geometry_note`
  saying exactly that.
- **The spec Colonial exercises the honest-roof path for real.** Its style has
  no pitch source, so `roof.py` leaves the ridge unjudged — and the IFC emits
  an `IfcRoof` with a `geometry_note` and no invented planes. A test asserts
  the *absence*.
- **The record has almost no vertical opening data.** Window sills and door
  leaf heights exist nowhere outside the classical elevation generator's
  scope; the IFC uses editorial defaults named as editorial in each Pset.
  Recorded as **OQ 36**.
- **README's "What is deliberately not here yet" was three-quarters stale** —
  it still said compositional constraints were unread (WP-2.2 built them),
  129 kits were skeletons (WP-4.2 filled them), and date-conditional
  resolution selected nothing (WP-1.3 wired it). Repaired to the current
  honest list rather than added to.
- **One pre-existing workbench test is environment-sensitive.**
  `test_example_plan_no_traversal` needs a built frontend (`app/dist`) for the
  SPA catch-all to exist; in a container without the build it 404s. Not a code
  defect and not this package's — noted here so the next agent doesn't chase it.

## What was deliberately not done

- **No MCP export tool.** The rail's 24 tools are unchanged; the workbench
  endpoint wraps `build/` directly. An agent-facing `tdl_export` is additive
  when an agent actually needs one.
- **No DXF DIMENSION entities or paperspace layouts** — annotation is TEXT on
  ANNO layers. A drafter re-dimensions to their office standard anyway; real
  associative dimensions are worth doing when WP-5.5's importer gives them a
  consumer.
- **No hip/gambrel/cross roof solids in IFC**, and no chimneys, stairs, trim
  or materials — each absence stated on the element or in `docs/export.md`,
  none guessed.
- **No bearing-diagram DXF** — the workbench's SVG set has it; the DXF section
  is the vertical slice.
- **`import_dxf.py` reads only TDL-emitted files**, by the ruling; the
  refusal for foreign DXF names WP-5.5 as the package that generalizes it.
- **No committed CAD artifacts** — `dist/dxf/`, `dist/ifc/` are gitignored
  like `dist/plans/*.svg`; the files regenerate from the record.

## Open questions

- **OQ 36** (new): the record carries no vertical opening data — should
  `window_sill_ft` / door leaf heights join the plan schema, or stay the
  elevation layer's judgment? Until ruled, the IFC's editorial defaults are
  named as editorial in every Pset they touch.
