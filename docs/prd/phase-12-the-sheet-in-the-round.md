# PRD — Phase 12: The Sheet in the Round

*A product requirements document for the Traditional Design Language workbench. Written 8 September
2026 against commit `f54c5af` of `codex-lux/Traditional-Design-Language`. It is written to be handed to
Claude Code as the whole of the instruction for a phase of work, in the manner of `PLAN-OF-ACTION.md`,
and it is written to be argued with — every decision below names its reason, and the ones that are
Lucas's to make are gathered in §12 with a recommended default so that no package is blocked on them.*

*Suggested path in the repository: `docs/prd/phase-12-the-sheet-in-the-round.md`. Suggested board entry
and phase heading for `PLAN-OF-ACTION.md`: Appendix A.*

---

## 0. Read this first (for the agent)

1. **Read `CLAUDE.md`, then `PLAN-OF-ACTION.md` §1 "Operating rules for every agent", then `docs/workbench.md`,
   `docs/geometry.md`, `docs/structure.md`, `docs/elevation.md`, `docs/export.md`, `docs/proportion.md`** before
   touching anything. The rules in §1 are not restated here; they apply in full. In particular: the eleven
   decisions not to undo; *unjudged is not passed*; *sources or `kind: editorial`*; ids never renumbered;
   a report per package at `docs/reports/wp-12.<n>-<distinctive-slug>.md`; new questions as
   `docs/open-questions/oq-<slug>.md`, never a number (the numbers are frozen at 99).
2. **Read `docs/reports/tidewater-layout-diagnosis-2026-09-04.md` Parts 0, V and IX**, and
   `docs/reports/wp-5.11-real-2d-geometry.md`. The first says which stratum a fix lives in — everything in
   this phase is Stratum 2, *the instrument*, and is inherited by every style. The second is the precedent
   for the question this document answers (§1).
3. **Run `python3 build/check_all.py` green before starting** any package, so your breakage is
   distinguishable from pre-existing state. Run the bare one, not a shard, before declaring a package done.
4. Packages are ordered by dependency (§8). Take them in order. WP-12.0, WP-12.1 and WP-12.2 need no ruling and can
   begin today; the rulings in §12 have defaults and a package that reaches one proceeds on the default
   and *says so in its report*.
5. **This phase adds the first new npm runtime dependency the workbench has ever taken** (`three`). That
   is ruling R1 in §12. Do not add it before WP-12.4, do not add any other, and load it only behind a
   dynamic `import()` (§7.11).
6. Where this document and the repository disagree, the repository is right and this document is stale —
   say so in the report and proceed from the tree.

---

## 0.1 Review addendum — read this before §1 (8 September 2026)

*This document was written in one session and reviewed in another against the tree at `f54c5af`, on the
day it was written. Everything below is the reviewing session's, not the author's, and it is placed here
rather than folded into the text so that what was claimed stays legible beside what was found — this
project's own convention. **Every symbol, token, constant, file and route §§3, 5, 6 and 7 name was checked
against the tree and exists**, with the eleven exceptions below. The PRD's own rule 6 applies to all of
them: where this document and the repository disagree, the repository is right.*

**Ruled by Lucas, 8 September 2026, at the review.** All nine rulings of §12 (R1 through R9) are **taken
as recommended** — `three` as the third runtime dependency, the 4 ft plan cut, the envelope rule for the
eave, columns only from a stated intercolumniation, the IFC door default imported, the Drawing Set as the
Round's home, JS/JSX rather than TypeScript, the isometric axon as a token, and a flat grade. No package
proceeds on an assumption; each cites this line. **And one addition to §4 and §11: an APPROACH view is in
v1, not v2** — a perspective camera at 5′-6″ eye height on the entrance axis, named `APPROACH` in the view
bar, its dimensions and datums withheld with the caption saying so, exactly as the free view withholds
them. It is a camera, and a camera is a serialiser; no geometry changes. `frame.js::poseFor` grows a
perspective branch, `isNamed` and the `plate` overlay are undefined for it and say so, and
`tokens.css` gains `--approach-eye-ft: 5.5` (editorial, marked). **At a named view the reader sees the
dressed model at rest**, with the 2D plate available as the overlay of §5.4 — the model is what this
phase is for, and the plate is the instrument that keeps it honest, not the resting state.

**Two citations in this document would have failed the build the moment it was committed, and both were
corrected in place rather than left to be discovered.**

1. **Seven `docs/reports/wp-12.<n>-…md` paths named reports that do not exist yet.**
   `build/check_ids.py::check_reports` walks every `.md`, `.py`, `.json`, `.jsx`, `.js` and `.mjs` in the
   tree for `docs/reports/<name>.md` and fails the build on one that does not resolve. **A report for an
   unstarted package is a dangling citation by construction**, which is the same finding CLAUDE.md
   records for the two parallel Phase 11s. The fourteen concrete occurrences are written as bare
   filenames (`wp-12.1-the-scene-record.md`); each package restores its own full path in the commit that
   creates the report. The `<n>`/`<slug>` template forms in §0 and §8 do not match the checker's regex
   and are left exactly as written.
2. **`oq/a-finding-citation-cannot-name-a-finding` was wrapped across a newline in §11.**
   `build/check_citations.py` reads line by line, so the citation was the truncated left half, which
   names no entry. Unwrapped. It is the same mechanism CLAUDE.md records for a code span straddling a
   newline, met in a new place.

**Nine corrections to the text, each verified in the tree.**

3. **THE DRAWING SET IS NOT ONE BUILDING, AND §5.2 ASSUMES IT IS.** `workbench/server/corpus.py` routes
   `plan`, `section` and `bearing` through `_placed` — one `auto` placement, WP-6.4's rule — and then
   calls `EL.build_elevation(plan, pt)` (line 453) and `rf.build_roof(plan, pt)` (line 480) **with no
   section**, so each falls through to `structure.build_section(plan, parti)`, whose engine default is
   the HEURISTIC and whose own comment says that default is *"for INTERNAL callers ONLY"*. The DXF export
   path repeats it (lines 547–552). The elevation reads placement — its porch measurement at
   `elevation.py:1397`, the footprint, the roof outline — so wherever CP-SAT reaches a proof, the
   elevation plate is of a different house from the plan plate beside it. **WP-6.4's own sentence, "one
   drawing set is one building or it is nothing", is published over this.** It is pre-existing and it is
   not the PRD's error; but §5.4's agreement test would have failed on it and blamed the scene. It is
   fixed first, as **WP-12.0**, before the scene is built against it.
4. **`geometry_report.vertical` is PROSE, not a count** (`geometry.py:2428` — `vnotes`, a list of
   sentences). §7.6 and WP-12.5 hold the exploded drop-line count to it. The one spelling of the transfer
   count is `build/disclosures.py::transfers(plan)` (line 216); WP-12.5 reads that.
5. **The dormer field names in §6.3 and WP-12.6 are not the record's.** `elevation.py::dormers()` emits
   `refused`, `forbidden`, `stated`, `count`, `placed_count`, `placement_shortfall_note`, `positions_ft`
   and `variant` — there is no `placeable` and no `not_drawn_reason`. Read the record's own names.
6. **`annotate.js` may not import `label.js`.** §7.7 says to reuse the Sheet's label fitting;
   `sheet/label.js` imports React, and `src/no_bare_imports.test.mjs` walks the static import graph from
   every `*.test.mjs` and refuses a bare specifier — so importing it would turn a green local run into a
   red CI one, which is the trap CLAUDE.md records for `coastTiers.js`. The three pure modules import
   only each other and `sheet/derive.js`; label fitting happens in `RoundPlate.jsx`, which is React
   already.
7. **`render_elevation.py` transcribes the DOOR rectangle too**, at line 451, beside `_window` at 166 and
   `export_dxf._win` at 528. WP-12.2's `opening_rects` covers doors and windows, so the count of
   transcriptions removed is three rather than two.
8. **`Chrome.jsx:48` carries `meta: '5 sheets'` as a typed literal** — a number written into JSX, which
   is the class CLAUDE.md names ("nor are numbers written into JSX, which is how the Kit's header claimed
   95 slots against an ontology holding 97"). WP-12.4 derives it or drops it; it may not simply be
   changed to a bigger literal.
9. **The heavy-call budget is a real constraint on §7.5's `plate` overlay.** Every `/api/drawings/{kind}`
   and the new `/api/scene` is metered at 60 calls an hour per identity (`limits.py`), and `e2e/walk.mjs`
   already prints a notice when it exhausts the budget. Six named views each fetching a plate, plus the
   scene, is seven heavy calls per record change. **WP-12.3 owes a measurement and a decision** — the
   scene response carrying the PLACED record so plate fetches re-solve nothing, or a combined
   drawing-set call — before WP-12.4 wires the overlay.
10. **`openings.JAMB_FT`/`MIN_SOLID_FT` are deliberately spelled twice**, in `openings.py` (41–42) and
    `render_plan.py` (699–700), held together by `tests/fixtures/sheet_symbols/`. §5.5 is right that the
    scene must import rather than copy; it imports from `openings.py`, and it does not "fix" the second
    spelling.
11. **WebGL is available to the walk, measured rather than assumed.** The pre-installed headless Chromium
    at `/opt/pw-browsers/chromium-1194` reports `webgl2: true` on default flags, renders a 61-edge test
    house through ANGLE/SwiftShader at about 1 ms a perspective frame and 0.1 ms orthographic, with ink
    pixels verifiably drawn and read back. So WP-12.4's e2e assertions can run here and in CI. **Where
    `webgl2` is absent the walk must report COULD NOT EVALUATE by name and exit 3** — the convention
    `workbench/scripts/walk.sh` already has for a rate-limited run — never a pass and never a failure of
    the code.

**One package is added, and it comes first.** **WP-12.0 — the drawing set is one building, and the four
faces are addressable** — closes finding 3 and, in the same edit, spends the cheapest visible win the
review found: `render_elevation` has taken a `face` argument since WP-3.2 and `corpus.drawing` has passed
`body.face` since WP-5.1, and **no client has ever sent one**, so three of the four elevations this
system can already draw have never been seen. Its acceptance is that every plate in a set reports the same
`solver.drawn_by.input_digest`. The full package text is in §8, before WP-12.1.

---

## 1. The question, and the answer

Lucas asked two things: to study the interaction in Dilum Sanjaya's post of 7 September 2026 ("Exploring
how 2D schematics can transition naturally into 3D") for the workbench, and to confirm whether SVG is still
the right medium or whether BIM, a Blender API, or something else is now required.

### 1.1 What the post does

There are two clips in the post, not one: a sepia conceptual sheet for a modular timber building ("Timber
Stack Commons") and a blueprint general-arrangement sheet for a vehicle. They share one grammar, and the
grammar is the thing worth taking; the architecture in the first clip is not (Lucas said so, and the
corpus has nothing to say about a container-stacked pavilion). Distilled from roughly twenty frames:

1. **The sheet is the interface.** The whole screen is a drawing sheet — title, subtitle, notes, section
   thumbnails, a plan thumbnail, a detail, a diagram, a title block, a scale bar, a north arrow. The model
   sits inside the sheet like a plate. The furniture stays put while the plate changes.
2. **One model, six named views, and the caption changes to the drawing's proper name.** A small bar of
   chips above the plate — `AXO R · AXO L · TOP · FRONT · BACK · SIDE` — tweens the camera (~0.6–1 s, eased,
   no overshoot) into a *true orthographic* position, and the caption beneath the bar becomes
   "EAST ELEVATION 1:100", "ROOF PLAN 1:100", "AXONOMETRIC — FROM THE FRONT LEFT". The plan view is a
   *cut* plan ("section B-B taken at the turret ring datum"), not a top-down look.
3. **Annotations are anchored to the model, not to the screen.** Leader-line labels attach to points on the
   model and re-leader themselves as the camera moves. During the tween they fade out and settle back in
   once the camera has.
4. **Furniture is view-specific.** Dimension strings appear only where they are true (overall widths in
   plan, level datums on elevations); some panels hide in elevation and return in axon; entourage (trees)
   is suppressed in plan and elevation and during transitions.
5. **Drag to orbit; click a room.** Free orbit is always available. Clicking a room — in the model *or* in
   the plan thumbnail — flies the camera in, ghosts the rest of the building, shows the room's contents
   with labels, and swaps the sheet's notes for a *room card*; `ESC` returns to the whole building. Room
   focus composes with the view bar: FRONT while focused is a sectional elevation of that room alone.
6. **State modifiers compose orthogonally with views.** The vehicle sheet's second row — `EXPLODE`,
   `SKIRTS`, `SMOKE` — applies to any view (an exploded *plan* is a real thing). Hover highlights a part
   with its name, a bounding box and a dimension; a data panel updates live.

### 1.2 The answer on medium

**SVG alone cannot do this, and neither BIM nor Blender is the answer; the answer is a scene layer of
constructed 3D geometry, generated from the record in Python, and a browser renderer that only draws it.**

The reasoning, because WP-5.11 already ruled on a neighbouring question and this must not read as
re-asking it:

- WP-5.11 asked *"is SVG capable of this at all, or does the project need a CAD/BIM layer underneath?"* and
  found that **the format was never the constraint; the missing thing was the layer between** — constructed
  2D geometry (`build/profiles.py`). *A format serialises what is modelled and cannot invent what is not.*
  That finding holds here, unchanged. IFC export (`build/export_ifc.py`) already *is* a 3D model in feet
  with a `tdl_id` on every product, and it draws nothing the record does not hold.
- What is new is not a modelling gap but an *interaction* gap. A continuous camera — the tween from plan to
  elevation to axon, the orbit, the section plane moved by hand — needs a 3D scene resident in the browser
  and re-projected sixty times a second. SVG is a projection, not a scene; the choice is between
  re-rendering SVG on every frame (feasible for a few hundred edges, not for a dressed Georgian front with
  fifteen-light sashes and a swept cornice) and a WebGL scene that carries the geometry once and draws it
  at any pose. The second is the right tool, and it is a small, well-understood one: Three.js, MIT, ESM,
  tree-shakeable, ~170 KB gzipped for what this needs.
- **Blender** is a desktop DCC with a Python API; it renders offline and cannot put a camera under the
  reader's hand in a browser. **IFC** is an interchange format the project already emits; it is a place
  the scene can *leave to*, not a place it can be *seen in* without a viewer, which returns to the same
  question. Both stay what they are: export targets. The scene record this phase builds is the natural
  input to both (a glTF export from the scene is a two-hundred-line job for a later package; the IFC
  exporter's `IfcShapeRepresentation` for orders, named in `docs/export.md`, sweeps the same profiles).
- **SVG keeps every job it has.** The plates (`render_plan.py`, `render_elevation.py`, `render_section.py`,
  `render_roof.py`) remain the authoritative 2D drawings, the DXF and PDF paths, and the printed set. The
  workbench's own plan Sheet (`sheet/Sheet.jsx`) stays the plan the critique is drawn on. The 3D view is
  *held to the plates*: at every named orthographic view the corresponding 2D plate can be laid over the
  model at the same frame, and a test asserts the two agree to the foot. That agreement is the instrument
  that keeps decision #11 true across the new medium.

So: **the same thesis, one dimension up.** WP-5.11 built the constructed 2D layer between the record and
the pen. Phase 12 builds the constructed 3D layer between the record and the camera, and the camera is a
serialiser. Nothing is modelled in JavaScript; JavaScript learns no more about a cornice than it knows
about a cyma today, which is nothing (OQ 83).

### 1.3 The stratum

Everything here is **Stratum 2** of the diagnosis's Part IX: a capability of the instrument, fixed once and
inherited by every style. No package in this phase authors a style rule, a parti rule, a room rule, or a
score term. Where the model needs a fact the record does not hold — a stair's rise per flight, a hip roof's
solid, a porch's column count — it *refuses to draw*, records the refusal in the scene as a named
`not_modelled` entry, and prints the count on the plate. That is P1 applied to a third dimension.

---

## 2. The grammar, translated into this product

What is kept from the post, what is changed, and what is refused, each with its reason.

| Post | Here | Why |
|---|---|---|
| The sheet is the interface | **Kept.** The Round is a plate inside the same sheet chrome `Sheet.jsx` uses (title, interpunct, caption, north, scale). | The Drawn Language is already the whole instrument; the model joins it, it does not replace it. |
| `AXO R · AXO L · TOP · FRONT · BACK · SIDE` | **Kept, renamed by the compass.** `PLAN·L0 · PLAN·L1 … · S · N · E · W · AXON·SW · AXON·SE · AXON·NW · AXON·NE · ROOF`. The entrance face's caption carries the word FRONT. | Plan-N is true-N unless a bearing says otherwise (WP-11.9); "front" is a fact the record states as `context.entrance_faces`, so the chip says the face and the caption says the role. |
| Caption changes to the drawing's proper name | **Kept, and the caption carries the disclosures.** "SOUTH ELEVATION · THE ENTRANCE FRONT" plus every banner line from `build/disclosures.py`. | One spelling of every banner line (WP-11.1, WP-11.8). A third surface consumes `placement.disclosures`; it does not re-derive. |
| Camera tween | **Kept: 520 ms (`--dur-4`), ease-out, no overshoot; `prefers-reduced-motion` cuts.** Labels fade at `--dur-1` and return at `--dur-2` after the camera settles. | "Ink settles; it does not bounce" (`tokens.css`). |
| Annotations anchored to the model | **Kept.** Every label, datum and dimension is a projection of a 3D anchor computed in a Three-free module (`round/frame.js`), drawn as DOM text + an SVG leader layer over the canvas. | Testable under `node --test` with no bundle; the type stays EB Garamond set by the same tokens as the sheet. |
| Dimensions only where true | **Kept, and stricter.** Dimension strings and datums are drawn in *named orthographic views only*; a free orbit withholds them and the caption says "free view · dimensions withheld". | A dimension string is only true parallel to the picture plane. Withholding is P1. |
| Entourage (trees) | **Refused in v1.** No tree, person, car or sky. | The corpus holds no tree; the Drawn Language licences entourage in the presentation register only, and v1 is the working register. |
| Click a room; room card; ESC | **Deferred to v2** (§11) — but every solid carries a `tdl_id` from WP-12.1 so click-to-record works from the first frame. | Lucas ranked it below views and overlays; the ids are cheap and P6 demands them regardless. |
| Explode, state modifiers | **Kept as `explode · levels`, `explode · elements`, `cut`.** They compose with any view. | The exploded plan is exactly the transfer-beam diagram (P7) a builder prices. |
| Hover: bounding box + name + dimension | **Kept as hover outline + a record card** (`tdl_id`, class, dimensions in feet-and-inches, `SourceChip` for the value's `kind`, the record path). | P6: click any mark and get the record that produced it. |
| The "SCHEMATIC" toggle | **Kept as `plate`** — overlays the authoritative 2D SVG plate at the same frame in any canonical view. | This is the agreement instrument (§5.4), not a style. |
| Live data panel (turret azimuth, speed) | **Not kept.** | Nothing in the record moves. |
| Photoreal wash, sky, sepia grain | **Not kept in v1.** Working register: vellum ground, flat face tones, one 45° sun as a 15% flat wash, ink edges at the five pen weights. | The two-registers rule. Presentation register is v2 (§11). |

---

## 3. What already exists, and the four gaps

Verified in the tree at `f54c5af`. This is the inventory a package may build on and must not duplicate.

### 3.1 Already three-dimensional, or one step from it

- **`build/export_ifc.py`** is a 3D model: storeys at `grade_to_floor_ft`, slabs per storey *and per massing
  element* (`slab_boxes()`, pure arithmetic, testable without `ifcopenshell`), walls as boxes with the inner
  face on the clear line, spaces from placed `room.geometry`, window and door openings with
  `IfcRelFillsElement`, two rotated gable planes, all in feet, every product with a `TDL` Pset carrying
  `tdl_id`. Its docstring lists what is honestly *not* modelled. **The scene record reuses `slab_boxes` and
  the wall-placement convention verbatim; it must not re-derive either.**
- **`build/structure.py::build_section`** → `storeys[]` (`grade_to_floor_ft`, `storey_height_ft`,
  `floor_structure_depth_in`), `levels[].walls[]` (role, wall, **axis `"x"` = a vertical wall of constant
  x**, position, lo/hi, bearing), `wall` (thicknesses by construction type), `footprint` outside-to-outside,
  `roof` heights, per element since WP-11.6.
- **`build/roof.py::build_roof`** → `main` (form, pitch rise-per-12, `grade_to_eave_ft`, `ridge` with axis,
  position, endpoints and `grade_to_ridge_ft`, `hip_lines`, `gambrel`, `cross`), `chimneys.positions[]`
  with `total_height_grade_ft`, `outline[]` plan segments, and `elevation_profiles` — one silhouette
  polygon per face, already a roof *plane* on the long faces (OQ 80). **No overhang, rake, soffit or
  fascia anywhere**; the only overhang figure in the system is the cornice projection under three aliases in
  `elevation.py`, and two sourced rules disagree about it (ruling R3).
- **`build/elevation.py::build_elevation`** → all **four** faces (`faces[S,N,E,W]` with bay `centres_ft`
  and `kinds`), `storey_windows[]` (head/sill/width, lights, sash pattern, muntin width, shutter leaf
  sizes, head treatment, reveal band), `entrance` (door leaf, casing, sidelights, transom, pilaster and
  column diameters and heights, `entablature_members`), `eave_cornice` (members with profiles and
  projections, both projection rules named), `water_table_belt`, `dormers` (positions, cheeks, face,
  casing, own cornice, `placeable`), `chimney_stack_plan_in` (a judgment, deliberately outside
  `measurements`). The renderers draw one face per call; the model is four-sided.
- **`build/profiles.py`** → constructed moulding geometry from a member's own two numbers, **linear in the
  module** (proved), `pack_geometry()` returning per-assembly segments and a finished silhouette,
  `column_radius_at()` for entasis, `repeat_positions()` for tooth-by-tooth repetition, `dxf_points()`
  bulges. *JavaScript keeps no profile knowledge.* A 3D consumer extrudes or lathes these segments and
  scales by the module; it never reconstructs a curve.
- **`build/resolve_kit.py`** — the four-call cascade read (`load_graph → chain_for → scope_for →
  resolve_slots → resolve_packs → eval_packs`). Read the **cascade**, never `C["kits"][style]`
  (`oq/the-raw-kit-read`), **except `chimney`**, which `roof.py` deliberately reads from the node's own kit
  (an inherited canonical variant is a claim the descendant never made).
- **`build/disclosures.py`** — the one spelling of every banner line. **`build/compass.py`** —
  `plan_north`, `assumption`, `face_token`; a bearing may never be defaulted, zero is not a measured north.
- **`workbench/server/corpus.py::_placed`** — one placement per drawing set on the proving engine, with
  `solver.drawn_by` and an `input_digest` taken *before* the solve (WP-11.8). A record already carrying
  `geometry` is returned untouched. **Every scene is built from `_placed`'s output and nothing else.**
- **`workbench/app/src/sheet/`** — `Sheet.jsx` (the plan plate as inline JSX SVG, the sheet chrome, the
  `data-*` vocabulary), `derive.js` (record + placement → drawable geometry in feet, a port of
  `render_plan.py` held by `tests/fixtures/sheet_symbols/`), `label.js`. **`components/PlateViewer.jsx`** —
  the loupe (CSS-transform zoom, ⌘/ctrl-wheel, drag-pan, `data-nopan` handshake).
- **`workbench/app/src/theme/tokens.css`** — Graphic Standard № 1 verbatim: `--paper #F1EBDB`, the ink
  ladder, the five pen weights `--lw-construction … --lw-cut`, the duties (`--salmon` cut masonry,
  `--sepia` timber, `--green` growth, `--blue` water), washes, `--shadow-angle:45deg`,
  `--shadow-working`, motion durations, `--tr-*` tracking. **The Round reads these through
  `getComputedStyle` at mount; it defines no colour of its own.**

### 3.2 The four gaps this phase fills

1. **No stable ids on drawn geometry outside IFC.** The four Python renderers emit eight CSS classes and
   zero `data-*` or `id` attributes; click-to-record lives entirely in `Sheet.jsx`. The scene record
   defines the convention, following `export_ifc.py`'s `tdl_id` scheme (`L{idx}-wall-{wi}`,
   `{room}-window-{wi}-{k}`, `{room}-door-{di}`, `floor-L{idx}[-{element}]`, `roof`, `roof-plane-{n}`).
2. **No per-opening rectangle in the elevation record.** `(x0, x1, sill, head)` is transcribed twice
   already — `render_elevation._window` and `export_dxf._win`. The scene would be the third copy, which is
   the class of defect the repository polices hardest. **WP-12.2 lifts it into one function with three
   callers** (precedent: `plan_check.furniture_shortfalls`, one spelling with two callers — *not*
   `openings.required_wall_ft`, which is deliberately spelled three times).
3. **No true section.** `render_section.py` draws a storey stack across `min(W, D)`; nothing is cut. The
   Round's `cut` modifier is a real section plane through the scene with poché caps — derived, not a
   plate, and captioned as such.
4. **No 3D bodies for the things the elevation dimensions.** Sashes, shutters, surrounds, the cornice, the
   entrance, chimneys and dormers exist as numbers and as 2D profiles. WP-12.6 and WP-12.7 stand them up.

### 3.3 Things that look like gaps and are not

- `test_m3_drawings.py::test_unknown_kind_names_the_kinds` posts `/api/drawings/axonometric` and expects
  422. **This phase does not add a drawing kind**; the scene has its own route (§5.3). The negative fixture
  stays true. Do not touch it.
- `svg_theme.py`'s total hex map is 2D-ink-specific and does not port. The Round takes colour from
  `tokens.css`, so nothing new enters the map.
- `build/check_frontend.py`'s 700 KB entry-chunk ceiling and the two-tier coastline assertion are the
  precedent, not an obstacle: `three` goes behind `import()` in one lazy module, exactly as
  `coastTiers.js` does, and the check gains a third assertion (§7.11).
- `docs/reports/project-review-2026-09-03.md` §IX.1 warns against proposing work already refused with a
  measurement. Nothing here has been refused; the nearest ruling (WP-5.11) is *adopted*, not reopened.

---

## 4. Decisions taken

Lucas's answers to the four questions put on 8 September 2026, and what each commits the phase to.

| Question | Answer | Commitment |
|---|---|---|
| Rendering architecture | **Three.js + SVG hybrid** | A Python scene layer; Three.js draws it; SVG plates stay authoritative and are overlaid at named views. |
| Where the code lives | **GitHub `codex-lux/Traditional-Design-Language`** | This document is written against `f54c5af`. |
| 3D fidelity in v1 | **Massing + openings + roof + porch, AND kit elements from the proportion engine** | WP-12.1 (envelope) then WP-12.6 (cornice, windows, chimneys, dormers, trim) and WP-12.7 (entrance, porch). Fidelity is v1 scope, not v2. |
| Must-have interactions | **Named views + camera tween; overlays + modifiers** | WP-12.4 and WP-12.5 are the must-haves. Room focus and findings-in-3D are v2 (§11), with the ids laid now. |
| Frontend | **Vite + React + TypeScript** (Lucas's pick) | **Amended: the repository already has a Vite + React app in plain JS/JSX with a typed-by-convention discipline and a `node --test` suite that runs without `npm install`.** Adding TypeScript would introduce a build convention the rest of the app does not follow. The Round is built *inside* `workbench/app` in the app's own language, with JSDoc types on the scene shapes. If Lucas wants TypeScript, it is a separate, app-wide package, not this one. (Ruling R7 records this as a stated deviation.) |
| Kit elements | **Cornice/entablature + storey datums; windows with sash, surrounds, shutters; entrance with surround and porch columns; chimneys, dormers, roof trim** | All four families are in scope; each is drawn only from what the elevation record and the packs already dimension. Porch columns need a ruling (R4). |
| Camera | **Orthographic canonical views + free orthographic orbit** | No perspective camera in v1. An eye-level "approach" view is v2. |

---

## 5. Architecture

### 5.1 The data flow

```
plan record (client, planDoc)
   │  POST /api/scene  {plan, parti?, candidates?}          ← one call per record change, heavy-metered
   ▼
corpus._placed(plan)                                        ← ONE placement, proving engine, input_digest
   │
   ├─ structure.build_section(placed, geometry_result=placed)
   ├─ roof.build_roof(placed, section=…)
   ├─ elevation.build_elevation(placed, section=…, roof=…)  ← all four faces
   ├─ resolve_kit (cascade) + proportion_engine.dimension + profiles.pack_geometry
   └─ disclosures.banner(placed, …)
   ▼
build/scene.py::build_scene(placed, section, roof, elev, kit, packs)   ← PURE ARITHMETIC
   ▼
scene record (JSON, feet, x east · y north · z up from grade)          ← schema/scene.schema.json
   │
   ▼  {scene, disclosures, digest, timing_ms}
workbench/app/src/round/                                    ← the viewer
   ├─ frame.js      camera poses, ortho framing, tween, projection     (pure; node --test)
   ├─ overlays.js   grid, datums, daylight, wet, privacy, △ marks      (pure; node --test)
   ├─ annotate.js   what furniture a view shows                        (pure; node --test)
   ├─ three-scene.js  scene JSON → Three objects                       (lazy: import('three'))
   ├─ Round.jsx     the canvas host: pointer, tween loop, picking
   └─ RoundPlate.jsx  the sheet chrome around it: view bar, caption, compass, scale, record card
```

Camera moves never touch the server. A record change (style switch, wall drag, assert-a-fact) refetches
the scene on the same 400 ms debounce the bench uses for `/api/plan/evaluate`; while a scene is in flight
the previous one stays up and the caption says "re-modelling…" in the same register as "re-solving…".

### 5.2 The one placement

`corpus._placed` is the only way a scene is built. A bench plan that already carries `geometry` is not
re-solved; a plan without it is placed once on the proving engine and the scene carries
`solver.drawn_by.input_digest`. The Round prints the digest in the caption's engine line beside the engine
name, exactly as the plan plate does, so a reader can tell a scene and a sheet of the same house apart
when their inputs differed (diagnosis J6).

### 5.3 The route

`POST /api/scene` — a new route in `workbench/server/app.py` beside `/api/drawings/{kind}`, behind
`_heavy(request)` and `_plan(body)` (the compiled-validator gate, WP-10.1). Body: `{plan, parti?,
candidates?}`. Response:

```
{ "scene": <scene record>,
  "disclosures": [ …banner lines from build/disclosures.py… ],
  "digest": "<input_digest>",
  "timing_ms": { "place": n, "section": n, "roof": n, "elevation": n, "scene": n } }
```

422 with `{error, …}` when the placer refuses (the same shape `/api/drawings` returns). **Not a sixth
drawing kind**: drawing kinds return SVG through `svg_theme.retokenize` and are enumerated by a test that
uses `axonometric` as its negative example. `api.scene(plan, opts)` joins `api/client.js` as a typed
wrapper; the Round never uses raw `fetch`.

### 5.4 The plate and the model are held to each other

At every canonical orthographic view the corresponding 2D plate exists already: `PLAN·Ln` ↔ the workbench
Sheet (client-drawn) and `render_plan.py` (server-drawn), `S/N/E/W` ↔ `render_elevation.py` for that face,
`ROOF` ↔ `render_roof.py`. The `plate` overlay lays that SVG over the canvas at the same frame, at 60%
opacity, so any disagreement is visible as a double line. For that alignment to be exact rather than
eyeballed, **each Python renderer's root `<svg>` gains one attribute, `data-frame="ox oy scale x0 y0"`**
(the five numbers its own `X`/`Y` lambdas already use), pinned by a test that reads them back. This is the
first `data-*` attribute any Python renderer emits, and it carries no geometry — only the transform the
renderer already applied.

Beyond the overlay, **agreement is asserted, not admired** (§9): the scene's exterior wall outer faces
projected to plan must equal the plan renderer's poché ring; the scene's opening holes on a face must equal
`render_elevation`'s window rectangles (after WP-12.2 they are the same function's output); the scene's
storey datums must equal `section.storeys`. Each is a test that reads both sides.

### 5.5 What the scene may not do

- It may not read `C["kits"][style]` directly, invent a dimension, default a bearing, or draw a roof form,
  stair, hip, overhang or column the record and packs do not dimension. Each refusal is a `not_modelled`
  entry with `why` and `source`, and the count is printed on the plate.
- It may not re-derive a banner line, a relaxation mark position, a jamb allowance, a door width default,
  or a wall thickness. It calls `disclosures.banner`, `render_plan.relaxation_marks`,
  `openings.JAMB_FT`/`MIN_SOLID_FT` (import, do not copy), and `structure.wall_thickness`.
- It may not carry a numeric literal that is a dimension. Named editorial constants are permitted only
  where they already exist in the tree with a note (`DEFAULT_GRADE_TO_FIRST_FLOOR_FT`, the IFC door
  height 6.67 ft, `TARGET_SILL_IN`, `DORMER_SETBACK_ON_SLOPE_IN`) and are *imported*; one new constant is
  proposed (the plan cut height, R2) and it is `kind: editorial` with its note. A source-reading test
  counts numeric literals in `scene.py` the way `tests/test_profiles.py` refuses arc arithmetic in JS.
- It may not call anything good.

---

## 6. The scene record

`schema/scene.schema.json`, version `0.1.0`. Feet throughout; inches only inside `detail` sub-objects that
mirror the elevation record's own inch fields. **Frame: x east, y north, z up, origin at the main block's
SW corner at grade** — the plan frame (`plan.schema.json` `$defs.geometry`) with z added; `z = 0` is grade,
the ground floor sits at `section.storeys[0].grade_to_floor_ft`. The viewer sets Three's up vector to +z
and never transforms coordinates; what the record says is what the camera sees.

### 6.1 Top level

```
{
  "scene_version": "0.1.0",
  "plan_id", "style", "style_name", "parti",
  "frame": { "units": "ft", "x": "east", "y": "north", "z": "up", "origin": "main block SW corner at grade",
             "north": { "plan_north_is_true_north": bool, "bearing_deg": n|null, "assumption": "<compass.assumption()>" } },
  "entrance_face": "S",
  "faces": { "S": { "label": "SOUTH ELEVATION", "role": "THE ENTRANCE FRONT"|null, "token": "<compass.face_token>",
                    "outside_width_ft", "bays": { "centres_ft": [...], "kinds": [...], "note" } }, "N": …, "E": …, "W": … },
  "bounds": { "min": [x,y,z], "max": [x,y,z] },
  "grid":   { "bays": n, "module_ft": n, "x_ft": [...], "y_ft": [...], "source": "footprint" },
  "site":   { "lot": {width_ft, depth_ft}|null, "setbacks": {...}|null, "street_face": "S"|null, "source" },
  "storeys":[ { "id", "index", "floor_z_ft", "ceiling_z_ft", "head_z_ft"|null, "storey_height_ft", "source" } ],
  "datums": [ { "id", "label": "+14′-3″", "z_ft", "class": "floor"|"ceiling"|"head"|"eave"|"ridge"|"grade", "source", "kind" } ],
  "elements":[ { "id": "main"|"<block id>", "role", "rect": {x_ft,y_ft,width_ft,depth_ft} } ],
  "solids": [ … §6.2 … ],
  "spaces": [ … rooms as pick volumes, not drawn … ],
  "marks":  { "relaxations": [ { "id", "at": [x,y,z], "axis", "off_ft", "level", "source": "geometry_report.relaxations.marks[i]" } ],
              "unlocated": [ … named, never placed … ] },
  "not_modelled": [ { "what", "why", "source", "class" } ],
  "judgment":     [ { "what", "why", "source" } ],
  "provenance_counts": { "measured": n, "editorial": n, "derived": n, "judgment": n },
  "solver": { …geometry_report.solver, incl. drawn_by.input_digest… },
  "note": "Nothing here is drawn that is not in the record. <n> things the record holds are not modelled; they are listed, not omitted."
}
```

### 6.2 A solid

Every drawable thing is one of a small set of geometric primitives, so the viewer needs no domain knowledge:

```
{ "id": "L0-wall-3",                       ← stable, unique, the tdl_id convention of export_ifc.py
  "class": "wall"|"slab"|"roof-plane"|"gable"|"opening-frame"|"sash"|"muntin"|"shutter"|"sill"|"surround"
           |"cornice"|"belt"|"water-table"|"column"|"pilaster"|"entablature"|"chimney"|"dormer-cheek"
           |"dormer-face"|"dormer-roof"|"hearth"|"deck"|"porch-roof"|"void-cap",
  "level": 0|1|null, "element": "main"|"<block>", "face": "S"|null, "room": "<room id>"|null,
  "geometry": one of
     { "type": "box",     "origin": [x,y,z], "size": [w,d,h] }
     { "type": "extrude", "plane": "xz"|"yz"|"xy", "at": n, "thickness": n, "outline": [[u,v],…], "holes": [[[u,v],…],…] }
     { "type": "sweep",   "profile": [[u,v],…] | {"segments": […profiles.py segments…], "start": [u,v]},
                          "path": [[x,y,z],[x,y,z]], "scale": n }
     { "type": "lathe",   "radius_at": [[z,r],…], "axis": [x,y], "z0": n }
     { "type": "prism",   "polygon": [[x,y],…], "z0": n, "z1": n }
  "ink": "cut"|"profile"|"seen"|"fine"|"construction",     ← the pen weight class the viewer draws its edges with
  "tone": "paper"|"paper-lit"|"paper-mat"|"paper-deep"|"sepia-pale"|"salmon",   ← face fill, a tokens.css name
  "source": { "record": "section.levels[0].walls[3]", "also": ["section.wall.exterior_in"] },
  "kind": "measured"|"editorial"|"derived"|"judgment",     ← the weakest kind among the numbers that made it
  "note": "…"|null }
```

Rules:

- `ink` and `tone` are **names**, resolved by the viewer from `tokens.css`. A solid never carries a hex.
  Colour is nomenclature: `salmon` only for cut caps and hearth breasts, `sepia-pale` only for timber
  members the record calls timber, the paper tones for everything else. Green and blue never appear on a
  solid; they are overlay washes.
- `kind` is the *weakest* provenance among the numbers that positioned and sized the solid, so a wall
  whose thickness came from a construction-type default and whose length was measured is `editorial`,
  and the record card says which number was the weak one.
- `extrude` with `holes` is how an exterior wall carries its openings: the outline is the wall face in
  its own plane (u along the wall, v = z), the holes are the opening rectangles from WP-12.2. Three's
  `Shape` + `holes` + `ExtrudeGeometry` renders it directly; no CSG.
- `sweep` carries a `profiles.py` segment list *unchanged* and a `scale` (the module ratio). The viewer
  tessellates arcs at draw time; it never reconstructs one.
- `lathe` carries `(z, r)` pairs produced by `profiles.column_radius_at` in Python; the viewer joins them.

### 6.3 What v1 puts in `solids`, by package

| Class | From | Package |
|---|---|---|
| `slab` | `export_ifc.slab_boxes(plan, section, t_ext)` — imported, not copied | 12.1 |
| `wall` (exterior, with holes; interior, plain) | `section.levels[].walls[]`, thickness `section.wall`, height `levels[].floor_to_ceiling_ft`; exterior inner face on the clear line, interior centred (the IFC convention) | 12.1 (holes: 12.2) |
| `gable` | `roof.elevation_profiles[face]` for faces perpendicular to the ridge — the wall above eave to the profile | 12.1 |
| `roof-plane` | `roof.main` — gable/side-gable/front-gable as two planes (the IFC plates, but as `prism` with the true pitched polygon, not a rotated slab); hip and gambrel from `hip_lines`/`gambrel`; cross from `cross` | 12.1 (gable family) · hip/gambrel/cross 12.1 if `roof.py` dimensions them, else `not_modelled` with the form named |
| `deck`, `porch-roof` | rooms whose placed `geometry.void.roofed` is true — the deck at floor datum, the roof plane at the eave with the main pitch, **no columns** until 12.7 | 12.1 |
| `hearth` | `room.hearth[]` via `build/hearths.py` (breast width and the depth `render_plan.py` already draws as poché — import, do not copy) | 12.1 |
| `chimney` | `roof.chimneys.positions[]` to `total_height_grade_ft`; plan size `elev.chimney_stack_plan_in` — **a judgment**: the stack is drawn as a solid only when the plan size is stated; otherwise a vertical construction-weight axis line to its height, and a `judgment` entry | 12.6 |
| `opening-frame`, `sash`, `muntin`, `sill`, `shutter` | `elev.storey_windows[i]` + WP-12.2's rectangles: frame ring at `reveal_band_in`, two sashes with a `lights_across × lights_high_per_sash` muntin grid at `muntin_width_in`, sill, shutter leaves at `shutter_leaf_width_in × shutter_leaf_height_in` when `shutters_carried` | 12.6 |
| `cornice`, `belt`, `water-table` | `elev.eave_cornice.members` → `profiles.pack_geometry` silhouette swept along the eave line of each long face; `water_table_belt` swept along the ground datum on masonry faces; rake **only** where the record states a raking cornice (else `not_modelled`) | 12.6 |
| `dormer-*` | `elev.dormers` where `placeable`; cheeks, face, own window from `_dormer_lights`, own cornice, gable roof at the main pitch unless `variant` says otherwise | 12.6 |
| `surround`, `pilaster`, `entablature`, `column` | `elev.entrance`: door leaf and casing, sidelights and transom where present and not forbidden, pilasters at `pilaster_width_in × pilaster_projection_in`, `entablature_members` swept across `entrance_composition_width_in`, columns lathed from `lower_shaft_diameter_in`/`upper_shaft_diameter_in`/`column_height_in` | 12.7 |
| porch `column` | **ruling R4** — placed by `profiles.repeat_positions` only where a bound pack states an intercolumniation for the porch's order; else the porch keeps deck and roof and a `not_modelled` entry names the missing rule | 12.7 |

`spaces[]` carry every placed room as a `prism` with its `id`, `type`, `name`, `level`, and declared vs
placed dimensions, for picking and (v2) focus. They are never drawn.

### 6.4 Three states, in the record

- **Drawn**: a solid, with its `kind`.
- **Not modelled**: `not_modelled[]` — the record holds it and the model does not draw it, with `why`
  (`"roof form 'hip' — roof.py states the form and pitch; hip plane corners are not dimensioned"`,
  `"stair — flights carry plan rectangles and no rise per flight"`, `"window r.dining.windows[1] — no
  height_ft"`). Printed on the plate as a count and listed in the record card's "not modelled" tab.
- **Judgment**: `judgment[]` — a value the sources leave to the human (`chimney_stack_plan_in`, the cornice
  projection where two rules disagree). Drawn, where drawn, in *construction* weight and named.

The plate caption's last line is always the `note` string above. A scene with an empty `not_modelled`
list prints "0 things not modelled", never nothing (WP-11.6: *an empty list is not the question closed*).

---

## 7. The viewer

### 7.1 Where it lives

**Surface ⑧, the Drawing Set, becomes the Sheet in the Round.** Its first plate is the model; its five
flat plates remain as the `plate` overlay at the matching views and as their own chips below the model for
anyone who wants the flat sheet alone. The surface id stays `drawings`; its label in `Chrome.jsx`'s
"take it out" group becomes `The Drawing Set · in the round`. The Plan Workbench (⑦) keeps its 2D Sheet and
gains one `ActionChip` in its strip — `→ in the round` — which navigates to
`#/drawings?view=axon-sw&level=0` carrying the current selection. In v2 the Round can become an
alternative canvas on ⑦ (§11); in v1 the critique stays where it is and the model stays where drawings are.

Why not a new surface: a thirteenth surface for the same record the eighth already draws is the
"second, worse jump mechanism" `keys.js` warns about, one level up. Why not ⑦: ⑦ is 794 lines and owns the
drag-and-re-score loop; the Round's first job is to be *right*, not to be interactive with the solver.

### 7.2 Addressing

Per WP-5.6, every view is a URL. `router.js`'s `drawings` entry gains no path keys; the state rides in
params through `useFilters`: `view` (`plan-l0|plan-l1|s|n|e|w|axon-sw|axon-se|axon-nw|axon-ne|roof|free`),
`level` (for plan and ghost), `plate` (`0|1`), `ov` (comma list of overlay ids), `explode`
(`levels|elements|none`), `cut` (`x:20.4|y:12|none`). A copied link reproduces the view, the overlays and
the cut. `e2e/router-unit.mjs` gains cases for round-tripping these.

### 7.3 The view bar

A `ChipGroup` of `Chip radio` above the plate, in the sheet chrome, mono eyebrow type: one `PLAN·Ln` per
level (`levels[].index ≥ 0`), then `S · N · E · W` in that order, then `AXON·SW · SE · NW · NE`, then
`ROOF`. Beneath it the plate's proper name in `--tr-drawing` caps, from `annotate.js::caption(view,
scene)`:

- `PLAN·L0` → "GROUND FLOOR PLAN · CUT AT 4′-0″ ABOVE FINISHED FLOOR" (the height from R2)
- `S` → "SOUTH ELEVATION · THE ENTRANCE FRONT" (role from `scene.faces.S.role`)
- `AXON·SW` → "AXONOMETRIC · FROM THE SOUTH-WEST" — never "front-left"; the compass names it
- `ROOF` → "ROOF PLAN"
- `free` → "FREE VIEW · NOT A NAMED DRAWING · DIMENSIONS WITHHELD"

The default view on arrival is the axon that shows the entrance face and the face to its left when facing
it (`entrance S` → `AXON·SW`), computed in `frame.js::defaultAxon(entrance_face)`.

### 7.4 The camera

Orthographic always. `frame.js` is pure and exports:

```
poseFor(view, scene, level)      → { azimuthDeg, elevationDeg, target:[x,y,z], halfHeightFt, cut:{...}|null, hide:{...} }
framing(scene, view, aspect)     → halfHeightFt that fits scene.bounds with the sheet margins Sheet.jsx uses (mL 11, mR 15, mT 15, mB 9 ft, scaled)
tween(a, b, t)                   → a pose; slerp on the orientation, lerp on target and halfHeight; t eased by easeOutCubic
project(pose, viewport, [x,y,z]) → [px, py, depth]      ← labels, leaders and the △ marks use this
unproject(pose, viewport, [px,py], z) → [x,y]           ← the cut handle drag uses this
isNamed(pose, view)              → bool                 ← after an orbit, false; the caption reads "free view"
```

Named poses: plan = azimuth 0, elevation 90 (looking down, north up — screen-up is model-north, exactly the
Sheet's rule); elevations = azimuth per face normal, elevation 0; axons = azimuth ±45/±135, elevation
35.264° (true isometric; the angle is a token `--axon-elevation-deg` in `tokens.css` so a dimetric
30° can be ruled later without a code change); roof = plan without the cut.

Plan views carry a **cut** at `floor_z + CUT_HEIGHT_FT` (R2, default 4.0, editorial) and hide everything
above it; the cut faces are capped in `--salmon` (§7.9). `ghost` (the level below at hairline) is a
chip beside the level chips, as on ⑦.

Orbit: pointer drag on the canvas rotates about the target (azimuth free, elevation clamped to [−10°, 90°]);
⌘/ctrl-wheel zooms (the `PlateViewer` convention — plain wheel scrolls the page); shift-drag pans.
Any orbit sets `view=free`. A named chip snaps back with a tween. Reduced motion: tweens become cuts.
Pointer handling copies `PlateViewer.jsx`'s discipline: listeners on `window`, held in a ref, torn down on
`pointerup`, `pointercancel` and unmount; a drag swallows the click it would otherwise deliver.

### 7.5 Overlays (chips, multi-select; `ov=` in the URL)

Computed in `overlays.js` (pure) from the scene and `lastEval.rooms_meta`, drawn as translucent geometry
or lines by `three-scene.js`:

| id | Draws | Source | Wash / ink |
|---|---|---|---|
| `grid` | bay lines on the grade plane and up every exterior wall to the eave | `scene.grid` | `--draw-grid`, `--lw-construction` |
| `datums` | horizontal lines at each datum on the faces the view shows, labelled `+14′-3″` at the right margin | `scene.datums` | `--draw-dim`; labels `--tr-eyebrow` |
| `daylight` | a translucent green volume from each lit exterior wall inward to `2.25 × window_head_ft` (the corpus's own reach rule, read from `rooms_meta.daylight_multiplier` — never a literal) | `spaces` + `rooms_meta` | `--wash-green-1` |
| `wet` | a blue prism joining the plumbing rooms that share a wall line, floor to floor | `spaces` + `rooms_meta.plumbing` | `--wash-blue-1`; a `--blue-deep` axis where a stack aligns |
| `privacy` | each space's floor washed sepia by `privacy_rank` (unranked left unglazed) | `rooms_meta.privacy_rank` | `--wash-sepia-1` at ⑦'s exact opacity ladder |
| `relaxations` | the hollow △ in ink at each located mark, on the wall, at the level; the unlocated ones named in the caption (always on; the chip hides them) | `scene.marks` | `--draw-seen`; never colour |
| `plate` | the matching 2D SVG plate at the same frame (§5.4), fetched via `api.drawing(kind)` on demand and cached by digest | `/api/drawings/{kind}` | 60% opacity |

Overlays do not exist in `free` view except `grid`, `relaxations` and `privacy` — the ones that are true
from any angle.

### 7.6 Modifiers (chips, multi-select)

- **`explode · levels`** — each storey's solids translate +z by `k × storey_height_ft` with `k` from a
  small drag handle (0…1.5); the roof rides on the top storey; slabs stay with the storey above them;
  interior walls of level 1 that do not continue to level 0 are shown with a dashed drop-line to the floor
  below — that *is* the transfer-beam diagram, and the count in the caption matches
  `geometry_report.vertical`.
- **`explode · elements`** — each massing element (`scene.elements`) translates away from `main` along the
  axis of its `attached_to` face by `k × 12 ft`. Only meaningful on a multi-element house; the chip is
  present and disabled with a note on a one-rectangle plan ("one element — nothing to separate").
- **`cut`** — a section plane. Chips choose the axis (`N–S` = a plane of constant x, `E–W` = constant y,
  `level` = the plan cut's z); a handle on the plate's margin drags the plane along its axis, its position
  printed in feet-and-inches; solids on the camera side are clipped and the cut faces capped in `--salmon`
  with a `--draw-cut` outline. Caption gains "SECTION A–A · CUT AT x = 20′-4″ · DERIVED FROM THE MODEL,
  NOT A PLATE". With `S`/`N`/`E`/`W` selected this is the building section the project does not yet draw in
  2D, and the caption says so.

Modifiers persist across views and are stated in the caption whenever active.

### 7.7 Annotations and furniture (`annotate.js`)

A view shows exactly the furniture that is true in it:

| View | Shown |
|---|---|
| `PLAN·Ln` | room names and dimensions from the Sheet's own `label.js` fitting (import it), overall and bay `DimRun`s along the bottom and right (the Sheet's component, reused), north arrow, scale bar, △ marks |
| `S/N/E/W` | bay centrelines ticked along the base with `faces[f].bays.centres_ft`, overall width, the datums at the right margin, a scale bar; no room names |
| `AXON·*` | three 10 ft rules along x, y and z at the SW-most visible corner (a scale bar is honest along an axis in a parallel projection and nowhere else), the compass, no dimension strings |
| `ROOF` | ridge/eave/hip lines named at construction weight, chimney positions, north arrow, scale bar |
| `free` | compass and nothing measured |

Labels are DOM `<div>`s positioned by `frame.js::project`, set in the sheet's own type; leaders are an SVG
layer over the canvas at `--lw-construction` with the same 45° tick ends as `DimRun`. During a tween
labels fade out at `--dur-1` and in at `--dur-2` after the camera settles. A label whose anchor is
occluded (depth test against the picked solid) is hidden, not drawn through the building.

### 7.8 The record card (P6)

Hover outlines a solid in `--draw-profile`; click pins a card in the plate's margin: the solid's `id`,
`class`, its dimensions in feet-and-inches (`DimensionString`'s `ft()`), a `SourceChip` for its `kind`
naming the weak number, and the `source.record` path as text. `esc` unpins. Clicking a space (through a
transparent hit prism) sets `selection.room` exactly as ⑦'s `onPickRoom` does, so a later v2 can filter
findings by it without a new mechanism. The card reuses `components/SourceChip.jsx` and
`components/DimensionString.jsx`; it introduces no new component.

### 7.9 Ink and tone (the Drawn Language in three dimensions)

- **Ground**: the canvas clear colour is `--paper`; the grade plane is `--paper-mat` to the lot or to the
  footprint plus the sheet margins, ruled with the bay grid when `grid` is on.
- **Faces**: filled with the solid's `tone` token. One directional sun at `--shadow-angle` (45°, upper-left
  of the *sheet*, i.e. fixed to the camera, which is what a drawing's sun is) modulates each face by a flat
  `--shadow-working` (15%) on faces turned from it — flat, never gradient, no cast shadows in v1.
- **Edges**: every solid's edges (Three `EdgesGeometry`, threshold 20°) drawn as screen-space lines at the
  pen width its `ink` names — `--lw-cut` 3 px, `--lw-heavy` 2.4, `--lw-medium` 1.6, `--lw-fine` 1.05,
  `--lw-construction` 0.7 — in the matching `--draw-*` ink, using `LineSegments2`/`LineMaterial` with the
  viewport resolution so **the pen does not magnify with the zoom**. OQ 64 ("the loupe magnifies the pen")
  is answered in the Round by construction; say so in the report. Hidden edges are occluded by faces
  (depth-tested) and not drawn dashed in v1.
- **Cut caps**: where a clipping plane cuts a closed solid, the cap is filled `--salmon` and outlined
  `--draw-cut` using the stencil technique (three.js `webgl_clipping_stencil`); the plan cut is a
  clipping plane, so plan views get poché for free and it is the *same* poché the Sheet draws.
- **No pure white, no black, no colour that is not a token.** A test reads `three-scene.js` and refuses any
  hex or `0x` literal.

### 7.10 The sheet chrome (`RoundPlate.jsx`)

Identical furniture to `Sheet.jsx`, by reuse not by copy: the interpunct title (`derive.interpunctTitle`),
the `styleName · subtitle` line, the 150 px rule, the plate caption with `data-plate-title` /
`data-plate-note`, wrapped in `PlateViewer` for the loupe's frame and controls (zoom is delegated to the
camera rather than a CSS transform; `PlateViewer` gains an optional `onZoom` prop for that, and
`data-nopan` on the canvas so the loupe's pan does not fight the orbit). Plus, new here: the view bar, the
overlay and modifier strips, a **compass** in the corner that turns with the camera and prints
`scene.frame.north.assumption` beneath it, and the model's own disclosure line — "*n* things the record
holds are not modelled — listed in the card" — after the banner lines.

### 7.11 Bundle strategy

`three` (pinned exact, `^0.185` or the current release at the time of WP-12.4) is the app's third runtime
dependency (R1). It is imported **only** from `round/three-scene.js`, and that module is loaded by
`Round.jsx` with `await import('./three-scene.js')`, so Vite emits it as its own chunk with `three` inside.
`build/check_frontend.py` gains a third assertion beside the coastline tiers: a `three-scene-*` (or
`round-*`) chunk must exist, and the entry chunk must still be ≤ 700 KB. `frame.js`, `overlays.js`,
`annotate.js` import nothing but each other and `../sheet/derive.js`, so `src/round.test.mjs` runs under
`node --test` with no `node_modules`, and `no_bare_imports.test.mjs` stays green.

### 7.12 Keyboard, motion, accessibility

No new global keys in v1 (`keys.js`'s own rule). Within the plate: `esc` unpins the card or exits the cut
handle; arrow keys nudge the cut handle by 1 ft (shift: 5 ft) when it has focus, in the manner of
`Splitter.jsx`. All chips carry the `Chip`/`ActionChip` ARIA already established. The canvas has
`role="img"` and an `aria-label` equal to the caption; the view bar is the accessible alternative to the
orbit. `prefers-reduced-motion` zeroes the tween. The `#root` minimum width stays 1380 px; the Round is a
desktop instrument like the rest.

---

## 8. Phase 12 — the packages

*Goal: the drawing set can be turned in the hand — one model, the drawings' own names, the plates held to
it — and nothing is drawn that is not in the record.* Written in the Phase 11 form. Each package ends with
a report at `docs/reports/wp-12.<n>-<slug>.md` (built · found · deliberately not done · new questions as
`oq-<slug>.md` files), a `CHANGELOG.md` entry, and the measurement in §9 before and after. **Order is by
dependency and it is also the order of start.**

### WP-12.0 The drawing set is one building, and the four faces are addressable

*Added by the review of 8 September 2026 (§0.1, finding 3). It is not part of the original PRD and it is
first because §5.4's agreement test is written against a drawing set that is one building, and it is not.*

**Build.**
1. `workbench/server/corpus.py::drawing` — the `elevation` and `roof` branches take the set's own
   placement, as `plan`, `section` and `bearing` already do:
   `placed = _placed(plan, pt, candidates)`, then `section = st.build_section(plan, pt,
   geometry_result=placed)`, then `roof = rf.build_roof(plan, pt, section=section)` and
   `elev = EL.build_elevation(plan, pt, section=section, roof=roof)`. Both branches' `meta` gains
   `solver` from `placed["geometry_report"]["solver"]`, so every plate in a set carries the engine and the
   `input_digest` the plan plate already carries (WP-11.8's J6).
2. `workbench/server/corpus.py::export_cad` — the same, for the `section`, `roof` and `elevation` DXF
   sheets (lines 541–553), which repeat the defect.
3. `workbench/app/src/api/client.js` — `drawing(kind, plan, opts)` as a typed wrapper, since
   `DrawingSet.jsx` is the last raw `fetch` in the app; the surface moves onto it.
4. `workbench/app/src/surfaces/DrawingSet.jsx` — a `face` `ChipGroup` (`role="radio"`, as the sheet chips
   are) shown only for `kind === 'elevation'`: S, N, E and W in that order, the entrance face labelled as
   the entrance front from the response's own `entrance_face`. The per-kind cache keys on `kind + face`.
   The elevation footer prints the engine and the digest.

**Tests, mutation-checked.** `workbench/server/tests/test_drawing_set_one_building.py`: every one of the
five kinds reports the same `solver.drawn_by.input_digest` for one record; reverting the `section=`
argument on either branch turns it red (assert the mutation LANDED by reading the value back); all four
faces return an SVG and two different faces return different SVGs — a `face` argument that is accepted and
ignored is the defect this half exists to remove, and equal output would pass a weaker assertion.
`test_m3_drawings.py::test_unknown_kind_names_the_kinds` is untouched.

**The measurement.** On `spec-builder-colonial` and `tidewater-georgian-careful` under `auto`, before and
after: the digest each plate reports, the footprint the elevation was built on, and
`porch_clear_depth_ft`. A number that does not move is reported as not moving.

**Not in scope.** The scene, the route, the viewer. No renderer changes: `data-frame` is WP-12.4's.

**Hand-off brief.** *In `workbench/server/corpus.py`, make the elevation and roof plates take the drawing
set's own placement, as the plan, section and bearing plates already do — `build_elevation` and
`build_roof` are called with no section today, so each falls into `structure.build_section`'s heuristic
default, whose own comment says that default is for internal callers only, and a CP-proved plan sheet sits
beside an elevation of a different placement. Fix the DXF export path with it, carry the solver's digest
onto both plates' metadata, and give the Drawing Set surface the face chips the server has accepted since
WP-5.1 and no client has ever sent. Measure the digests before and after. Report to
`docs/reports/wp-12.0-the-drawing-set-was-not-one-building.md`.*

**Depends on:** nothing. **Size:** small.

### WP-12.1 The scene record

**Build.**
1. `schema/scene.schema.json` 0.1.0 as in §6, registered in `build/validate.py` beside the plan schema.
2. `build/scene.py` — `build_scene(plan, section, roof, elev, *, kit=None, packs=None) → dict`, **pure
   arithmetic, a leaf** in the manner of `storeys.py`/`axis.py`: imports `export_ifc.slab_boxes`,
   `structure.wall_thickness`, `render_plan.relaxation_marks`, `hearths`, `compass`, `disclosures`; emits
   `slab`, `wall` (holes come in 12.2 — until then exterior walls are plain and the report says so),
   `gable`, `roof-plane` (gable family; hip/gambrel/cross where `roof.py` dimensions their lines, else
   `not_modelled` naming the form), `deck`/`porch-roof` for roofed voids, `hearth`; `spaces`, `datums`,
   `grid`, `faces`, `frame.north` from `compass`, `marks` from the one rule, `not_modelled`, `judgment`,
   `provenance_counts`, `solver`. CLI: `python3 build/scene.py <plan> [--engine cp|heuristic|auto]
   [--out scene.json]` printing the §9 numbers.
3. Stable ids by the `export_ifc.py` scheme, extended for new classes
   (`{room}-window-{wi}-{k}-sash-{upper|lower}`, `cornice-{face}`, `chimney-{n}`, `dormer-{face}-{n}-cheek-{l|r}`).
4. `docs/scene.md` — the layer doc: the frame, the classes, the three states, what is deliberately not
   modelled, and the rule that the viewer knows nothing.
5. A `README.md` row in the built-outputs table and a line in `build/check_all.py`'s `CHECKS`? — **No**:
   put `scene.py selftest` *inside* `validate.py`'s run so `TOTAL_CHECKS` does not move (WP-11.6's
   precedent), and say so.

**Tests, mutation-checked.** `tests/test_scene.py`:
- both shipped plans produce a scene that validates against the schema; every solid id unique; every solid
  carries `source.record` and a `kind`;
- **agreement**: the union of exterior `wall` outer faces projected to z = floor equals the outside-to-
  outside footprint `section.footprint` to 0.001 ft; `datums` equal `section.storeys` values;
  `marks.relaxations` positions equal `render_plan.relaxation_marks` output (read both);
- **three states**: a plan whose roof form is `hip` yields a `not_modelled` entry naming `hip` and no
  `roof-plane` solid (mutate a fixture copy's `declared.roof_form`; assert the entry appears and the solid
  count of class `roof-plane` is 0 — never that "something" changed); a room with `hearth` yields a
  `hearth` solid whose width equals the record's `width_in / 12`;
- **no literal dimensions**: a source-reading test over `build/scene.py` allows numeric literals only in an
  allowlist of named constants with a `# editorial:` note, and fails on any other float;
- the scene of a plan already carrying `geometry` is byte-identical across two builds (determinism, as
  `tests/test_determinism.py` holds for every directory read).

**Not in scope.** Openings in walls (12.2), the route (12.3), anything the elevation record dimensions
(12.6, 12.7), stairs (no rise per flight in the record — `not_modelled`, and an `oq-a-stair-has-treads-and-
no-rise-per-flight.md` question raised), per-element roofs (open items of
`oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it`; refuse and name), overhangs (R3).

**Hand-off brief.** *You are building `build/scene.py`, the constructed-3D layer between the placed plan
record and any camera, in the Traditional Design Language repository. Read `CLAUDE.md`, `PLAN-OF-ACTION.md`
§1, `docs/geometry.md`, `docs/structure.md`, `docs/export.md`, and this PRD §§5–6 and WP-12.1. Run
`python3 build/check_all.py` green first. The module is pure arithmetic, a leaf, and imports the existing
rules — `export_ifc.slab_boxes`, `structure.wall_thickness`, `render_plan.relaxation_marks`,
`disclosures.banner`, `compass` — rather than restating any. It draws nothing the record does not hold and
lists what it does not draw. Produce a scene for both shipped plans on the proving engine, print the §9
numbers, and write `tests/test_scene.py` with each assertion mutation-checked. Report to
`wp-12.1-the-scene-record.md`.*

### WP-12.2 One opening rectangle, three callers

**Build.**
1. `elevation.py::opening_rects(elev, face) → [{id, storey, bay, kind: window|door|blind, x0_in, x1_in,
   sill_in, head_in, source}]` — the one spelling of `(x0, x1, sill, head)` per face, computed from
   `faces[face].centres_ft/kinds`, `storey_windows[i]` and `entrance`, respecting `blind_bay_centres_ft`
   and the `NOT_MODELLED` discipline (a bay with no window record yields no rectangle and a reason).
2. `render_elevation._window` and `export_dxf._win` become callers of it; their inline arithmetic is
   deleted, not left beside it.
3. `scene.py` cuts exterior wall `holes` from it, and adds `opening-frame` placeholders (a ring at the
   reveal) so an elevation reads as an elevation before 12.6 dresses it.

**Tests, mutation-checked.** `tests/test_opening_rects.py`: for both shipped plans and all four faces the
rectangles the SVG renderer draws, the DXF exporter writes and the scene holes equal `opening_rects`
(read all three); a mutation that offsets `x0` by 1 in inside `opening_rects` turns all three red (assert
the mutation *landed* by reading the value back); a blind bay yields no rectangle and its reason. A
source-reading test fails if `x0, x1 = cx - ww/2` reappears in either caller.

**Not in scope.** Dormers' own windows (they carry their own arithmetic in `dormers()`; 12.6 reads it).

**Hand-off brief.** *Lift the elevation's opening rectangle — transcribed twice, in
`build/render_elevation.py::_window` and `build/export_dxf.py::_win` — into one function
`build/elevation.py::opening_rects` with three callers, the third being `build/scene.py`. The precedent is
`plan_check.furniture_shortfalls` (one spelling, two callers), not `openings.required_wall_ft`. Prove
parity across all three by reading each side, mutation-check it, and delete the copies. Report to
`wp-12.2-one-opening-rectangle.md`.*

### WP-12.3 The route

**Build.**
1. `workbench/server/corpus.py::scene(plan, parti=None, candidates=250)` — `_placed`, then
   `build_section(placed, geometry_result=placed)` (pass the placement; the default is for internal
   callers), `build_roof`, `build_elevation`, the cascade read for the style, `build_scene`; returns
   `{scene, disclosures, digest, timing_ms}`; `SystemExit` from the kit read guarded as `moves.apply()`
   guards it.
2. `app.py`: `POST /api/scene` behind `_heavy` and `_plan`; 422 on refusal in the `/api/drawings` shape.
3. `api/client.js::scene(plan, opts)` — and, since the Round's `plate` overlay needs it, `api.drawing(kind,
   plan, opts)` as a typed wrapper for `POST /api/drawings/{kind}`, which `DrawingSet.jsx` today calls with
   raw `fetch` (`DrawingSet.jsx:56`); move that call site onto the wrapper so there is one. `docs/workbench.md`
   endpoint map row; `workbench/README.md`.
4. An `ETag` from `digest` so a repeated fetch of an unchanged record is a 304 and costs no heavy call —
   only if `_heavy` can be told about it without a second metering path; else omit and say so.

**Tests, mutation-checked.** `workbench/server/tests/test_scene_endpoint.py`: 200 and schema-valid for the
example plan; the scene's `solver.drawn_by.input_digest` equals the plan plate's for the same record
(one placement per set); a refused plan is 422 with the kinds-style detail; `_heavy` metering counts a scene
as one heavy call; `/api/drawings/axonometric` is *still* 422 (the negative fixture is untouched).

**Hand-off brief.** *Add `POST /api/scene` to the workbench server, built on `corpus._placed` so the scene
and the drawing set are one placement, returning the scene record from `build/scene.py` with the banner
lines from `build/disclosures.py` and the input digest. It is not a sixth drawing kind. Meter it as heavy.
Report to `wp-12.3-the-scene-route.md`.*

### WP-12.4 The Round: named views, the tween, the plate held to the model

**Build.**
1. `workbench/app/src/round/frame.js`, `annotate.js` — pure (§7.4, §7.7); `src/round.test.mjs`.
2. `round/three-scene.js` — the only file that imports `three`; builds `Group`s per solid from the five
   primitives, edges as `LineSegments2` at token pen widths, tones from `getComputedStyle`; exposes
   `mount(canvas, tokens)`, `load(scene)`, `setPose(pose)`, `setClip(planes)`, `pick(px,py)`, `dispose()`.
3. `round/Round.jsx` — lazy-loads `three-scene.js`; owns pointer, tween loop (rAF only while tweening or
   dragging — an idle plate renders nothing), resize, picking, labels and the leader SVG.
4. `round/RoundPlate.jsx` — the sheet chrome (§7.10); the view bar; the caption from `annotate.caption`
   plus `disclosures`; the compass; the record card.
5. `surfaces/DrawingSet.jsx` — the Round as the first plate; the five flat kinds as chips beneath; the
   `plate` overlay wired to `api.drawing(kind)` and aligned by the renderers' new `data-frame` (add it to
   the four Python renderers, one attribute each, pinned by `tests/test_drawn_geometry.py`).
6. `surfaces/PlanWorkbench.jsx` — the `→ in the round` `ActionChip`.
7. `router.js` params, `Chrome.jsx` label, `state/layout.js` no change (the Round uses ⑧'s pane).
8. `package.json`: `three` pinned exactly (R1). `build/check_frontend.py`: the third lazy-chunk assertion.
9. `e2e/walk.mjs`: on ⑧ — every view chip produces its caption text; `AXON·SW` is the default for an `S`
   entrance; after a drag the caption reads FREE VIEW; `plate` on `S` draws an `<svg>` over the canvas
   whose `data-frame` is present; the entry chunk is under the ceiling; a screenshot per named view to
   `e2e/shots/round-*.png`.

**Tests, mutation-checked.** `src/round.test.mjs` (node, no bundle): `poseFor` returns azimuth 90/0/… per
face and 35.264 elevation for axons; `framing` fits `bounds` with the Sheet's margins; `tween(a,b,1) ===
b` and `tween(a,b,0) === a`; `project`/`unproject` round-trip to 1e-6 ft; `isNamed` false after any
azimuth change ≥ 0.5°; `caption('s', scene)` contains "THE ENTRANCE FRONT" iff `entrance_face === 'S'`;
`defaultAxon` for each of the eight entrance tokens. A source-reading test refuses any hex or `0x`
literal in `three-scene.js` and any `import` of `three` outside it.

**Not in scope.** Overlays and modifiers (12.5); dressed elements (12.6, 12.7); room focus; perspective.

**Hand-off brief.** *Build the Round — the model plate on the Drawing Set surface — in `workbench/app/src/
round/`, in the app's own JS/JSX, with `three` loaded only behind a dynamic `import()` in one module and all
camera, framing, projection and caption logic in Three-free leaves tested under `node --test`. Named
orthographic views tween at `--dur-4` with no overshoot; the caption is the drawing's proper name plus the
banner lines the server sends; the 2D plate overlays the model at the same frame via `data-frame`. Every
colour and pen width comes from `tokens.css`. Extend `build/check_frontend.py` and `e2e/walk.mjs`. Report
to `wp-12.4-the-round.md`.*

### WP-12.5 Overlays and modifiers

**Build.** `round/overlays.js` (pure; §7.5), the clipping planes and stencil caps (§7.6, §7.9), the
explode handles, the cut handle with keyboard nudge, the `ov=`/`explode=`/`cut=` params, the caption
lines for active modifiers, the transfer-beam drop-lines whose count must equal
`geometry_report.vertical`'s.

**Tests, mutation-checked.** `src/overlays.test.mjs`: daylight reach equals `head × daylight_multiplier`
from `rooms_meta` (mutate the multiplier, assert the volume moved); an unranked room yields no privacy
wash; the wet prism joins exactly the rooms `derive.js`'s wet overlay marks on ⑦ (read `rooms_meta` the
same way — one rule); explode offsets are `k × storey_height_ft` per storey and 0 for the roof relative to
its storey; a one-element scene reports `elements: nothing to separate`. e2e: `explode=levels` yields as
many drop-lines as the caption's transfer count; `cut=x:20` produces a caption with "SECTION" and "20′-0″".

**Hand-off brief.** *Add the overlays (bay grid, datums, daylight reach, wet stack, privacy gradient, the △
marks, the 2D plate) and the modifiers (explode by level, explode by element, the section cut with poché
caps) to the Round, each computed in a pure module from the scene and `rooms_meta`, each composing with
any view and stated in the caption when active. Report to `wp-12.5-overlays-and-modifiers.md`.*

### WP-12.6 The envelope dressed

**Build.** In `scene.py`, from the elevation record and the packs, with `kind` and `source` per solid:
windows (frame, sashes, muntin grid, sill, shutters), the cornice swept from `profiles.pack_geometry`
along each eave, the water table and belt on masonry faces, chimneys (solid where the plan size is stated;
an axis line and a `judgment` entry where it is not), dormers where `placeable` (cheeks, face, own window,
own cornice, gable roof), and the eave/rake overhang **per ruling R3**. The viewer's `sweep` and `lathe`
primitives (12.4) draw them; no viewer change beyond bug fixes.

**Tests, mutation-checked.** `tests/test_scene_dressed.py`: sash light counts equal `lights_across ×
lights_high_per_sash × 2` per window; muntin bar width equals `muntin_width_in`; shutters present iff
`shutters_carried`, and a leaf equals `shutter_leaf_width_in`; the cornice sweep's profile equals
`profiles.pack_geometry` for the same members at `reduced_gibbs_module_in` (read both; scale by the
module); a chimney with `chimney_stack_plan_judgment` truthy yields no solid and one `judgment` entry;
a dormer with `placeable: False` yields `not_modelled` naming `not_drawn_reason`; the §9 numbers before
and after, on both plans, both engines.

**Not in scope.** The entrance and the porch (12.7); the raking cornice on a gable end unless the record
states one; mitred corners on the cornice sweep (v2 — butt the runs and say so).

**Hand-off brief.** *Dress the scene's envelope from the elevation record and the proportion packs — sash,
surrounds, shutters, the swept cornice, water table, chimneys, dormers — every solid carrying the number
that made it and its `kind`, refusing where the record is silent. The profiles come from
`build/profiles.py` and are scaled, never reconstructed. Report to
`wp-12.6-the-envelope-dressed.md`.*

### WP-12.7 The entrance and the porch

**Build.** From `elev.entrance`: the door leaf, casing (Gibbs where `gibbs_order_applies_to_style`),
sidelights and transom where present, pilasters, the entablature members swept across the composition
width, columns lathed via `profiles.column_radius_at`. The porch: deck and roof already in 12.1; **columns
per R4** — `profiles.repeat_positions` along the porch's open faces where a bound pack states an
intercolumniation for the order `order_at_the_eave` names, else refuse and name the missing rule. The
Four-Foot Porch becomes visible as a porch a rocking chair cannot fit — that is the point of drawing it at
its real depth.

**Tests, mutation-checked.** door leaf height equals `door_leaf_height_in`; `sidelights_forbidden_by_kit`
yields no sidelight solid; column count equals `repeat_positions`' count for the stated intercolumniation
and a mutation of the spacing changes it; a porch with no intercolumniation rule yields deck, roof, no
columns, one `not_modelled` entry naming the rule.

**Hand-off brief.** *Stand the entrance composition and the porch up in the scene from
`build/elevation.py::entrance_composition` and the packs, with columns placed only by a stated
intercolumniation and refused otherwise. Report to `wp-12.7-the-entrance-and-the-porch.md`.*

### WP-12.8 The adversarial audit of WP-12.0 through 12.7

In the tradition of WP-6.4, 7.5, 8.6 and the 7 September audit: a fresh session reads the eight reports
and the code and looks for the things the packages did not measure — a solid with no source, a literal
that slipped past the allowlist, a plate that disagrees with the model by more than the tolerance, a
caption that says "proved" without "feasible", a tween that overshoots, a colour that is not a token, a
test that passes with its guard reverted. Fix what is fixable in the audit; defer the rest with reasons.
Report: `docs/reports/audit-<date>-the-round.md`.

---

## 9. The measurement contract (Phase 12's own instrument)

Phase 11's six numbers are plan-layer and, as WP-11.4 found, *"did not see two chimneys move eight feet"*.
A phase that moves roofs and elevations needs its own instrument. Before and after every package, on
`plans/tidewater-georgian-careful.json` and `plans/spec-builder-colonial.json`, on **both** engines,
`python3 build/scene.py <plan> --engine <e>` prints, and the report tabulates:

1. **solids** — count by class;
2. **not modelled** — count, and the list of `why` reasons grouped;
3. **judgment** — count;
4. **provenance** — `{measured, editorial, derived, judgment}` counts across solids;
5. **agreement** — max |Δ| in feet between (a) the scene's exterior wall outer faces and the plan
   renderer's poché ring, (b) the scene's opening holes and `opening_rects`, (c) the scene's datums and
   `section.storeys` — each must be 0.000 and the number is printed anyway;
6. **payload** — scene JSON bytes, and the triangle count the viewer would build (computed in Python from
   the primitives with the viewer's tessellation constants, so it is deterministic and needs no browser).

A package that cannot say which of these it moved, and in which direction, is not done. Numbers 5 and 6
are the ones this phase exists to keep honest: agreement stays at zero, and payload growth is the price of
fidelity stated in bytes.

---

## 10. Acceptance for the phase

The phase is done when, on the Drawing Set surface, for both shipped plans:

1. The model plate loads by default in `AXON·SW` (for an `S` entrance) within one heavy call; every named
   chip tweens to a true orthographic view whose caption is the drawing's proper name and carries every
   banner line the plan plate carries, plus the model's own not-modelled count.
2. `plate` on `PLAN·L0`, `S`, `N`, `E`, `W` and `ROOF` overlays the server SVG at the same frame with no
   visible double line, and `tests/test_scene.py`'s agreement assertions hold at 0.000 ft.
3. The overlays and modifiers of §7.5–7.6 each work in every view they are defined for, are addressable in
   the URL, and are stated in the caption when active; the exploded-level drop-line count equals the
   transfer count.
4. Every solid answers a click with its record card, `kind` and source path; every colour and pen width on
   screen resolves to a `tokens.css` name; the pen does not magnify with the zoom.
5. The envelope is dressed from the elevation record and packs (sash lights per date, shutters that could
   close, the style's own cornice at the real storey height, chimneys where stated, dormers where
   placeable, the entrance composed to Gibbs where it applies), and everything the record holds that the
   model does not draw is listed, counted and printed.
6. `python3 build/check_all.py` is green on the bare run; `check_frontend.py` reports the entry chunk under
   700 KB with the Round in its own chunk; `e2e/walk.mjs` passes its new checks; CI's six shards and the
   workbench job are green; `test_unknown_kind_names_the_kinds` is untouched.
7. Nine reports exist, each with the §9 table, and any question this phase could not answer is a file in
   `docs/open-questions/`.

---

## 11. Deferred to v2 (named, not hidden)

- **Room focus** — click a space, fly in, ghost the rest at `--wash`, room card from `tdl_get_room` +
  its findings, `esc` out, focus composing with the view bar (a sectional elevation of one room). The
  spaces and ids are laid in v1; the card and the flight are v2.
- **Findings on the model** — `plan_check` findings anchored at their `at` room/wall in 3D, filtered by
  the same layer chips as ⑦; and the Round as an alternative canvas on ⑦ (`canvas=sheet|round`), which is
  when the drag-and-re-score loop meets the third dimension. Gated on `oq/a-finding-citation-cannot-name-a-finding`
  (1,608 of 1,620 finding ids are unciteable) — a finding you can anchor is a finding you can name.
- **The presentation register** — graded wash, the sun's cast shadow (not just face shading), entourage
  where the Drawn Language licences it, the reserve bench colours. Same geometry, second ink.
- **An eye-level APPROACH view** — perspective camera at 5′-6″ on the entrance axis, the ortho↔perspective
  blend. The first perspective in the product, and it wants its own caption discipline (a perspective
  dimension is never true).
- **Hidden lines dashed** (`--draw-hidden`) and the silhouette at `--draw-profile` — a per-view edge
  classification pass.
- **Mitred cornice corners**, the raking cornice on gable ends where a pack states one.
- **Stairs** — blocked on a rise per flight the record does not carry (question raised in 12.1).
- **Per-element roofs and abutments** — the two open items of
  `oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it`; the scene refuses them until ruled.
- **glTF export of the scene** (`three/addons/exporters/GLTFExporter`, client-side, ~200 lines) and the
  IFC `IfcShapeRepresentation` sweep `docs/export.md` names — the scene record is the input to both.
- **Site**: a graded grade plane from `site.slope_direction_deg`/`cross_slope_pct`; v1's grade is flat and
  says so.

---

## 12. Rulings for Lucas, with the default each package proceeds on

| # | Question | Recommended default (the package proceeds on this and says so) |
|---|---|---|
| **R1** | The workbench has had exactly two runtime npm dependencies since WP-5.2, on purpose. Is `three` (MIT, ESM, pinned, lazy-loaded, ~170 KB gz) the third? | **Yes.** It is the smallest tool that does the job, it is loaded only when the Round mounts, and `check_frontend.py` holds it out of the entry chunk. No other dependency is added in this phase; addons (`LineSegments2`, `LineMaterial`) come from the same package. |
| **R2** | The plan cut height. Drafting convention is 4′-0″ above finished floor; the corpus has no rule. | **`CUT_HEIGHT_FT = 4.0`, `kind: editorial`**, one named constant in `scene.py` with a note, printed in the plan caption. Ruled number with no source is still editorial. |
| **R3** | Two sourced rules disagree about the eave projection (Gibbs: projection = height; `facade-classical`'s domestic envelope) and `elevation.py` chooses neither. Which does the model sweep the cornice to, and what becomes the overhang? | **Sweep to the envelope rule (`envelope_projection_in`), draw the order's own projection as a construction-weight ghost line, name both in the caption; overhang = the swept cornice's projection and nothing more (no soffit, no rake overhang).** Raise `oq-the-eave-has-two-projections-and-the-model-drew-one.md`. |
| **R4** | Porch columns. No portico composition function exists; the porch is a plan rectangle. | **Columns only where a bound pack states an intercolumniation for the order `order_at_the_eave` names; otherwise deck and roof and a named refusal.** Do not invent a count from the width. |
| **R5** | Door height where the record states none. `export_ifc.py` uses 6.67 ft, named editorial. | **Import the same constant; same `kind`; same note.** One editorial default, not two. |
| **R6** | Where the Round lives: the Drawing Set (⑧) or the Plan Workbench (⑦). | **⑧ in v1**, with the `→ in the round` chip on ⑦; ⑦ gains it as a canvas option in v2 with findings. |
| **R7** | TypeScript. Lucas chose "Vite + React + TypeScript"; the app is Vite + React + JS. | **Stay in JS/JSX with JSDoc types for this phase.** A TypeScript migration is an app-wide package with its own ruling; mixing conventions in one folder is the thing WP-5.6 spent a package removing. |
| **R8** | The axon angle: true isometric (35.264°) or a 30° dimetric. | **Isometric**, as a token (`--axon-elevation-deg`) so the ruling is a one-line change. |
| **R9** | Grade. The ground floor sits 2.0 ft above a flat grade by `DEFAULT_GRADE_TO_FIRST_FLOOR_FT`, editorial; the site record has a slope but no elevation model. | **Flat grade in v1, the 2.0 ft imported from `structure.py` with its `kind`, the caption saying "grade drawn flat".** |

---

## Appendix A — the `PLAN-OF-ACTION.md` entries

Board row (add after the two Phase 11 rows):

```
| **12 — The sheet in the round** | **WP-12.0 through 12.8** | **Not started (PRD 8 Sep 2026: `docs/prd/phase-12-the-sheet-in-the-round.md`)** |
```

Phase heading (append after the precedent-bench Phase 11):

```
## Phase 12 — The sheet in the round

*Raised by Lucas on 8 September 2026 against Dilum Sanjaya's "2D schematics transitioning into 3D" post,
with the question whether SVG remained the medium. The PRD — `docs/prd/phase-12-the-sheet-in-the-round.md`,
cite the filename — is this phase's brief; its §1 is the answer (the format was never the constraint, WP-5.11;
the missing thing is a constructed-3D layer between the record and the camera, and the camera is a
serialiser), its §8 is the packages, its §9 the instrument every package is held to, and its §12 the nine
rulings with the default each package proceeds on. Everything here is Stratum 2 of the 4 September
diagnosis's Part IX. Nothing in this phase proposes a score term, a style rule or a parti rule.*
```

Then the nine `### WP-12.n` headings in the Phase 11 form, each opening `**Status: NOT STARTED.**` and
carrying the package text from §8 verbatim after *Original package text follows, as written.*

## Appendix B — `schema/scene.schema.json`, the shape in brief

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "TDL scene record", "type": "object",
  "required": ["scene_version", "plan_id", "style", "frame", "entrance_face", "faces", "bounds", "grid",
               "storeys", "datums", "elements", "solids", "spaces", "marks", "not_modelled", "judgment",
               "provenance_counts", "solver", "note"],
  "properties": {
    "scene_version": { "const": "0.1.0" },
    "frame": { "type": "object", "required": ["units", "x", "y", "z", "origin", "north"],
               "properties": { "units": { "const": "ft" }, "x": { "const": "east" }, "y": { "const": "north" },
                               "z": { "const": "up" } } },
    "solids": { "type": "array", "items": { "$ref": "#/$defs/solid" } },
    "not_modelled": { "type": "array", "items": { "type": "object",
                      "required": ["what", "why", "source"], "properties": {} } }
  },
  "$defs": {
    "solid": { "type": "object",
      "required": ["id", "class", "geometry", "ink", "tone", "source", "kind"],
      "properties": {
        "id": { "type": "string", "pattern": "^[A-Za-z0-9_.-]+$" },
        "class": { "enum": ["wall","slab","roof-plane","gable","opening-frame","sash","muntin","shutter","sill",
                            "surround","cornice","belt","water-table","column","pilaster","entablature",
                            "chimney","dormer-cheek","dormer-face","dormer-roof","hearth","deck","porch-roof","void-cap"] },
        "ink":  { "enum": ["cut","profile","seen","fine","construction"] },
        "tone": { "enum": ["paper","paper-lit","paper-mat","paper-deep","sepia-pale","salmon"] },
        "kind": { "enum": ["measured","editorial","derived","judgment"] },
        "source": { "type": "object", "required": ["record"] },
        "geometry": { "oneOf": [
          { "properties": { "type": { "const": "box" } },     "required": ["type","origin","size"] },
          { "properties": { "type": { "const": "extrude" } }, "required": ["type","plane","at","thickness","outline"] },
          { "properties": { "type": { "const": "sweep" } },   "required": ["type","profile","path","scale"] },
          { "properties": { "type": { "const": "lathe" } },   "required": ["type","radius_at","axis","z0"] },
          { "properties": { "type": { "const": "prism" } },   "required": ["type","polygon","z0","z1"] } ] }
      } }
  }
}
```

## Appendix C — files touched or created, by package

| Package | Creates | Touches |
|---|---|---|
| 12.1 | `build/scene.py`, `schema/scene.schema.json`, `docs/scene.md`, `tests/test_scene.py`, `wp-12.1-the-scene-record.md` | `build/validate.py` (register + selftest), `README.md` (built-outputs row, extending-it command list), `CHANGELOG.md`, `CLAUDE.md` (where the work stands) |
| 12.2 | `tests/test_opening_rects.py`, `wp-12.2-one-opening-rectangle.md` | `build/elevation.py` (+`opening_rects`), `build/render_elevation.py` (−`_window` arithmetic), `build/export_dxf.py` (−`_win` arithmetic), `build/scene.py` (holes), `docs/elevation.md`, `docs/export.md` |
| 12.3 | `workbench/server/tests/test_scene_endpoint.py`, `wp-12.3-the-scene-route.md` | `workbench/server/corpus.py` (+`scene`), `workbench/server/app.py` (+route), `workbench/app/src/api/client.js` (+`scene`), `docs/workbench.md`, `workbench/README.md` |
| 12.4 | `workbench/app/src/round/{frame,annotate,three-scene}.js`, `round/{Round,RoundPlate}.jsx`, `src/round.test.mjs`, `wp-12.4-the-round.md` | `surfaces/DrawingSet.jsx`, `surfaces/PlanWorkbench.jsx` (chip), `router.js` (params), `Chrome.jsx` (label), `components/PlateViewer.jsx` (`onZoom`), `theme/tokens.css` (`--axon-elevation-deg`), `package.json` (+`three`), `build/check_frontend.py` (third assertion), `build/render_{plan,elevation,section,roof}.py` (`data-frame`), `tests/test_drawn_geometry.py`, `e2e/walk.mjs`, `e2e/router-unit.mjs`, `docs/workbench.md` |
| 12.5 | `round/overlays.js`, `src/overlays.test.mjs`, `wp-12.5-overlays-and-modifiers.md` | `round/*.jsx`, `three-scene.js` (clipping, stencil caps), `router.js`, `e2e/walk.mjs` |
| 12.6 | `tests/test_scene_dressed.py`, `wp-12.6-the-envelope-dressed.md`, `docs/open-questions/oq-the-eave-has-two-projections-and-the-model-drew-one.md` | `build/scene.py`, `docs/scene.md`, `docs/elevation.md` |
| 12.7 | `wp-12.7-the-entrance-and-the-porch.md` (+ an `oq-` file if R4 refuses on both plans) | `build/scene.py`, `tests/test_scene_dressed.py`, `docs/scene.md` |
| 12.8 | `docs/reports/audit-<date>-the-round.md` | whatever it finds |

## Appendix D — the frames studied

Timber Stack Commons (64 s): 0:01 AXO R with the full sheet; 0:07 EAST ELEVATION with element labels and
level datums, trees suppressed; 0:12 ROOF PLAN with room names as flat labels and overall dimensions; 0:17
mid-tween TOP→BACK with labels faded and room names floating as billboards; 0:23 NORTH ELEVATION; 0:30 the
same with entourage restored; 0:38 room focus — PENTHOUSE isolated, contents labelled, the room card
replacing the notes, ESC hint; 0:46 room focus + FRONT = a sectional elevation of one room; 0:54 a room
clicked in the plan thumbnail, camera flying through the building; 0:61 AXO L, "AXONOMETRIC — FROM THE
FRONT LEFT". Vehicle sheet (55 s): 0:03 ISO with key-to-items and instrumentation panels; 0:06 SIDE
ELEVATION with panels hidden, dimensions and a detail circle; 0:09–0:10 the FRONT tween; 0:14 PLAN VIEW
"section B-B taken at the turret ring datum"; 0:17 back to ISO with panels returning; 0:24 hover on the
turret shell — bounding box, name, dimension, the panel updating; 0:29 EXPLODE; 0:35 exploded PLAN; 0:42
exploded 3/4; 0:50 3/4 R with tick-ended dimensions in a second ink.
