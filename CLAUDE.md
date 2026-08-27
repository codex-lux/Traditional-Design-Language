# Traditional Design Language — working notes for Claude Code

A system that encodes traditional architecture as a language: elements are the alphabet,
proportioning systems are the grammar, a style is a set of bindings and constraints on a
universal slot set, and a named-error corpus catches the things that read as wrong to
someone fluent. The aim is a compiler — brief in, buildable and coherent house out.

## Read these before doing anything

1. **`STATE-OF-THE-PROJECT.md`** — what exists, what is half-built, what is unstarted.
   Revised 24 Aug 2026 against verified counts. Part III is the honest list of gaps.
   Predates WP-5.2 — where it calls the workbench unbuilt, this file is the current word.
2. **`PLAN-OF-ACTION.md`** — the progress board at the top, then §1 "Operating rules for
   every agent" (non-negotiable), then the work package you are doing. Every WP carries a
   **Status** line. Original package text is left as written even where the work is done,
   so what was asked for stays legible beside what was delivered.
3. The `docs/*.md` file for the layer you are touching. `docs/model.md` and
   `docs/inheritance.md` are the two that explain the data model itself.

## The rules that matter most

- **The eleven decisions not to undo** are listed in `PLAN-OF-ACTION.md` §1. They are
  settled. Do not reopen or "improve around" them.
- **Unjudged is not passed.** Every checker must distinguish evaluated-and-failed,
  evaluated-and-passed, and could-not-evaluate, and never collapse the third into the second.
- **Sources or `kind: editorial`.** Never invent a source, date, or measurement. An
  unsupported call is marked `editorial` / `judgment: true` and says so in its own note.
  Laundering a guess as `measured` is the worst thing you can do to this corpus.
- **Ids are stable and never reused.** Wrong id → add the right one, mark the old
  `deprecated_in_favour_of`.
- **Prose stays beside the test.** Making a rule executable adds a `test`; it does not
  replace the human-readable `statement`.
- **Findings matter as much as code.** Finish a work package with a report in
  `docs/reports/<wp-id>-<slug>.md`: what was built, what was found, what was deliberately
  not done, and any new open question appended to `docs/open-questions.md`.

## Verifying

```
python3 -m pip install -r requirements.txt   # ortools, jsonschema, pytest
python3 build/check_all.py     # every checker, then tests/ AND workbench/server/tests. Must be green.
                               # (the two CAD-export selftests report N/EV -- COULD NOT
                               #  EVALUATE -- without the optional ezdxf/ifcopenshell, and the
                               #  workbench suite the same without fastapi/httpx; that is a
                               #  named unjudged state, never a pass)
```

The data and every checker run on the standard library alone, deliberately — `requirements.txt`
covers only the tooling above the data. `check_all.py` runs the suite as `sys.executable -m
pytest` rather than the bare `pytest`: WP-2.3 found those were different interpreters here, and
sixteen tests were skipping while the run reported success.

Individual pieces: `build/validate.py`, `build/check_kits.py`, `build/check_constraints.py`,
`build/check_pack_bindings.py --strict`, `build/check_rooms.py`, `build/check_partis.py`,
`build/check_faults.py`, `build/check_addresses.py` compares what two co-binding packs MEAN at one address, using each rule's
`quantity` (OQ 48, closed at 0 collisions -- run it after adding any rule). `build/check_inheritance.py`
reports what the cascade delivers that nobody bound (OQ 51; `--roles`, `--slots <node>`, and
`--unendorsed` for the ruled work list in leverage order).
`build/check_counts.py` (fails the build when a number in this
file, in `STATE-OF-THE-PROJECT.md`, in `README.md` or in `docs/` disagrees with the data -- run it
with `--fix` to rewrite them), `build/proportion_engine.py selftest`. **When authoring or binding a pack, run
`build/pack_addresses.py <pack-id>`**: it lists every `(slot, dimension)` address the pack shares
with packs it co-binds with and prints both notes side by side. Several rules at one address is
usually right -- a menu within one pack, or two packs meaning the same quantity, which is what
precedence is for. Two packs meaning DIFFERENT quantities is a silent corruption and the fix is a
named dimension. Eight were found this way in WP-4.6; that is OQ 48. Useful while authoring:
`python3 build/resolve_kit.py <style-id> --verbose` shows a kit's full provenance chain, and
`python3 build/geometry.py <plan> --engine cp` places a plan by constraint rather than by search
(`build/geometry_cp.py`; `engine="auto"` is already the default everywhere).

## Where the work stands (26 Aug 2026)

Phases 0, 1, 2, 3 complete. Phase 4 complete through WP-4.3, WP-4.5 and WP-4.6; WP-4.4 is
environment-blocked. **Phase 5 is part-built** — WP-5.1 (DXF/IFC export), WP-5.2 (the workbench
in `workbench/`), WP-5.5 (drawing-to-record ingestion) and **WP-5.6 (the navigation overhaul)**
have shipped; WP-5.3 and WP-5.4 remain.

**WP-5.6 changed how the workbench is addressed, and it is worth knowing before touching it.**
A place is now a URL, and that URL is the citation grammar written down — `#/kit/craftsman/cornice`,
`#/faults?sev=serious`, `#/cite/fault:porch-too-shallow-to-inhabit`. `app/src/router.js` and
`state/nav.js` hold it; `citeFor()` in `citations.js` is the inverse of `routeCite` and lives
beside it so the two cannot drift. **The grammar is spelled in three places — `REF_RE` and
`CITE_RE` in `workbench/server/`, `parseCite` in the app — and an audit found two of the three
disagreeing about the dot in a constraint id, which is why `test_grammar_agreement.py` now
reads the JavaScript and holds all three against each other. Do not add a fourth copy.** Search is `⌘K` over `/api/search/index` (665 named things,
dispatching by citation); `/` filters the list in front of you; `?` explains both. Filters live
in the query string via `filters/useFilters.js` — do not reintroduce per-surface filter state.
`Chip` is now only ever a filter; acts are `ActionChip`. Report:
`docs/reports/wp-5.6-navigation-overhaul.md`.

164 nodes · 97 slots (ontology 0.7.0) · 40 massings · 60 rooms · 17 groupings ·
**21 partis naming 129 of 132 styles, 0 uncovered, and 21 of 21 composable for their own
style** · **57 packs, 132 of 132 nodes bound** (OQ 49; but read OQ 51 before trusting that number -- it counts a node's OWN bindings and the lineage cascade delivers packs nobody bound) — but 50 nodes still have no opening-role pack
and 46 no facade-role pack, down from 68 and 67 (WP-4.6's measured movement) · 660 constraints
migrated, 61.5% of hard ones tested · 209 faults · **159 of 159 kits populated** · 1,556 kit
parameters (74.6% measured, 12.8% editorial of which 0 are now silent — OQ 18's note half) ·
322 image records, 0 sourced · 14 reference plans · 24 MCP tools · **33 checks, 1,009 tests**
(plus the workbench app suite, **49** under `node --test`). Those two figures were 970 and 36 until
the infrastructure audit collected them; before that the test figure was 762 and had been stale for
some time, and the CHECK figure said 32 against a suite of 33 until WP-5.7 ran it and read the
total. `check_counts.py` polices counts DERIVED FROM THE CORPUS, and neither a test count nor a
check count is one of them, so **every number in this paragraph goes stale silently** -- nor are
numbers written into JSX, which is how the Kit's header claimed 95 slots against an ontology
holding 97.

**Every open question Lucas has ruled on is executed** as of 25 Aug 2026 — OQ 12, 13, 14, 15,
19, 26, 27, 29, 31, 32, 33, 34, 35, 36, 37, 38, 39, and 40 through 46 besides. **OQ 18** is HALF CLOSED: all 162 silent editorial
parameters now say they are editorial and quote the basis their slot states, so the count of
unexplained numbers is 0; the SOURCE half is environment-blocked and none of the 162 may be given
a source from a secondary work.
WP-4.6 raised **OQ 47, 48 and 49**. **OQ 47 and 49 are CLOSED** — `expressed_frame` at ontology
0.7.0 with a `member_status` field (structural / structural-and-expressed / applied / none), bound
on 14 kits of which five FORBID the member; and a `slots` scope on bindings, which took the corpus
to 132 of 132 by binding `egyptian-revival` to the two `facade-peristyle` rules that fit and
excluding the six that do not. **Closing 49 opened OQ 51, which is larger than either**: the lineage
cascade delivers proportion packs nobody bound, and `ranch-style` has 69 of its 78 dimensioned slots
governed by packs it never bound -- `opening-pointed`, a Gothic arch pack, governing 15 of them.
**OQ 48 is CLOSED AT OWN-BINDING SCOPE, AND THAT QUALIFIER IS THE POINT**: rules carry a
`quantity` naming what they measure, and the 139 corruptions found were renamed minimally -- at
each conflicted address the dominant quantity keeps the dimension and only the 74 minority rules
move. But `check_addresses.py` was measuring each node's OWN bindings while `resolve_packs` walks
the whole cascade, so the published "0 collisions" described a corpus nobody resolves. It now
measures both: **own 442 pairs, 0 collisions, 14 unjudged; cascade 1,264 pairs, 9 collisions, 111
unjudged**, both ratcheted. The 9 are OQ 51's surface, not a regression. **OQ 50 is CLOSED**
at the principle: ornament is rationed and not distributed, stated once in `docs/model.md`; a fault
would need the elevation layer to model ornament zones first, and it does not.

**WP-4.6 is COMPLETE** — twenty-one packs, and **every item of WP-4.1's list that this corpus can
support is built** (`moorish-arch`, `greek-doric`, `adobe-module`, `opening-pointed`,
`opening-craftsman`, `trim-prairie`, `dutch-gambrel`, `balcony-gallery`, `stone-course`,
`facade-arcade`, `timber-panel`, `opening-mullioned`, `facade-gable`, `trim-sawn`,
`octagon-geometry`, `facade-pavilion`, `jetty-overhang`, `facade-portada`, `facade-peristyle`,
`corbel-course`, `facade-medieval-english`). The items it cannot support are named in
`docs/reports/wp-4.6-missing-proportion-packs.md` with a reason apiece rather than left silent — the
Baroque curved wall first among them, where not one of 22 matching nodes gives a figure for an
undulating elevation. **Read that report's closing section before touching this layer**: it carries
the four things the package leaves open, chief among them a finding nobody has raised as a question
yet — five unrelated traditions all say ornament works by being BOUNDED, and it should be tested
against the whole style graph rather than noticed one pack at a time.

**WP-5.7 changed the shell's proportions and the atlas's resolution, and both are worth
knowing before touching the workbench.** Raised by Lucas against a screenshot of the map:
*"the map is VERY crude and doesn't take well to zooming in since the resolution does not
scale up as you zoom in"*, plus full screen, collapsible rails and draggable margins.
**The crudeness was two defects wearing one symptom, and the first is the one to remember:
`vector-effect` is not an inherited property**, so `vectorEffect="non-scaling-stroke"` set on
a `<g>` reached none of the paths inside it, and the coastline's `strokeWidth={0.7}` was 0.7
DEGREES of ink -- seventy pixels at the zoom the reader was complaining about. Third instance
in this codebase of a per-element SVG property set on a parent and ignored; the e2e walk now
asserts the general form (no stroked mark in the atlas may carry a `stroke-width` without a
`vector-effect` of its own). The second defect was real too: one outline at every scale. There
are three now -- `workbench/scripts/make_coastlines.py` generates coarse/medium/fine from
Natural Earth 110m/50m/10m, `surfaces/phylo/coastTiers.js` fetches the one the scale has
earned, and **while a finer tier is in flight or has failed the legend says what is actually on
the plate** rather than letting a facet pass for a shore. `MIN_W` is 3 degrees because that is
what the finest data can honestly draw, not because of taste. Rings are culled by generated
bounding boxes; the graticule steps with the scale (`graticule.js`); the wheel handler is
native and non-passive, because React's passive `onWheel` meant the page scrolled while the
map zoomed. **A per-element SVG property set on a parent is this codebase's most-repeated bug and the
guard against it must read COMPUTED STYLE**: the first version of that guard filtered on
`getAttribute('stroke-width')`, but `stroke-width` IS inherited, so the very marks the bug
lives on were dropped from the population before the test ran and reverting the fix left it
green. **The atlas's viewBox now takes the pane's own shape and its height is DERIVED, not
stored** -- a fixed 134:43 box in a 4:3 pane letterboxed 27.8 degrees of latitude, and the
ring cull, the graticule and the pointer maths all read the viewBox as though it were the
plate: South America vanished from the home view and a wheel zoom drifted 3.12 degrees every
two notches. One mismatch, three defects; do not reintroduce a stored height.
**`state/layout.js` is a fifth external store** -- pane widths and folds, in
localStorage, deliberately NOT in the URL, because a citation that carried the sender's rail
width would be handing the reader the sender's monitor. **It holds TWO numbers per pane** --
what the reader chose, persisted, and what fits this window, derived -- because the first
version had one and let a moment of a narrow window overwrite all eight panes' widths
permanently. **Eight panes pull** — the two rails, the
Phylogeny's record, and the five surface index panels that were fixed numbers in their own JSX
(`components/PullPane.jsx`) — and widths clamp on READ as well as on write. Only the first
three FOLD (`[` and `]`, or the spine): `PANES.foldable` is the difference between chrome and
subject, and a Fault Corpus with its fault list folded away is not a decluttered Fault Corpus. The atlas can take the whole
window; `layout.full` is the one piece of layout state that is not persisted, which is what
"temporarily" means. `--rail-left` and `--rail-ai` are gone from `tokens.css` on purpose -- do
not reinstate them. **The workbench app's `node --test` suite may not import anything from node_modules.**
`check_all.py` runs it with no npm install, so a package import there is a green local run
and a red CI one -- which is exactly what happened to WP-5.7's first audit pass, via
`coastTiers.js` importing React for one hook. The hook lives in `useCoastline.js` now and
`src/no_bare_imports.test.mjs` walks the suite's import graph to keep it that way.
**Four adversarial audits then found eleven of the package's forty-three new assertions
passing on the code they were written to guard** -- among them the fine coastline tier being
replaceable wholesale by the coarse one with the suite green, and a documented keyboard
control that was never wired to its element. Read the report's audit section before adding a
test here; the suites are now mutation-checked and the harness is worth reusing. Report:
`docs/reports/wp-5.7-the-atlas-and-the-shell.md` · new open question: OQ 72.

**THE INFRASTRUCTURE AUDIT (27 Aug 2026) measured the deployment for the first time, and the
headline is that the ceiling is about ONE person, not a handful.** Reading the corpus is
comfortable for dozens (100-560 rps); **editing a plan is the bound**, because
`PlanWorkbench.jsx` re-evaluates on a 400 ms debounce and one evaluate costs 338 ms of CPU, so
one person dragging a wall consumes ~85% of the server's entire evaluate capacity. Two editors
see 899 ms, four see 2.0 s, eight see 4.2 s. Throughput is FLAT across the whole ladder --
~2 evaluates and ~4.5 drawings a second whatever the concurrency -- because it is one core,
fully serialised. `workbench/scripts/load.py` is the harness; run it against a server you
started, with `HEAVY_CALLS_PER_HOUR` raised, or you measure the rate limiter instead.
**Four uvicorn workers buy ~4x and break compose five times in six** (measured: 6 jobs
submitted, 5 answered 404 by a worker that never saw them) -- that is OQ 36, and the audit
supplies the numbers its ruling was missing. **Storage: ~733 MB image, no volume, no database,
and 497 MB of it -- 85.5% of the dependency layer -- is `ezdxf`/`ifcopenshell`/`ortools` and
their transitive `pandas`/`numpy`/`fontTools`.** Report:
`docs/reports/infrastructure-audit.md` · new open questions: OQ 73-77.

**Next, in order:**
1. **WP-4.4** is **environment-blocked**, not deferred — the proxy answers 403 to CONNECT for
   www.loc.gov. `build/harvest_habs.py` is written, dry-run exercised and queued against the day
   the network opens; its own status block in `PLAN-OF-ACTION.md` carries the verbatim denial. The
   network-free next step there is giving the 322 asset records their `provenance.building` names,
   without which every harvest query degrades to a style-name search. Then Phase 5.

WP-2.3 closed Phase 2 on 25 Aug 2026: `build/geometry_cp.py` states placement to CP-SAT, enforces
room minimums instead of scoring them, and returns a named conflict set when a brief cannot be
housed. Read `docs/reports/wp-2.3-the-real-solver.md` before touching geometry — the exact-tiling
formulation the plan of action named does not work (CP-SAT could not decide it in 240 s while
holding a valid solution), and the solver reads the slicing tree off a heuristic layout instead.
`build/geometry.py` remains the default engine everywhere.

## Traps worth knowing before you hit them

- **Module loading.** Everything in `build/` and `mcp_server/` loads siblings *by file path*
  so each script also runs standalone. That returns a fresh module per call and the loads
  nest — one `check()` used to execute plan_check 16x, geometry 8x. `build/modcache.py` now
  caches by realpath and every local `_mod`/`_load` delegates to it. **Do not reinstate a
  local loader**; `tests/test_modcache.py` counts module executions to catch it.
- **Inheritance transmits more than anyone bound, in three places.** `hybridizes_with` transmits a
  donor's whole kit (OQ 58 scoped it); a BINDING used to transmit a pack's whole rule set (OQ 49
  scoped it); and `descends_from` still transmits an ancestor's whole set of proportion packs, which
  is **OQ 51** and is the one with 3,367 instances. Read it before trusting "132 of 132 bound".
  OQ 51 is now RULED -- adjudicate the 233 unjudged gaps first, flip inheritance to opt-in after --
  so this trap is a work list rather than an unanswered question. It is still live until that list
  is worked; nothing about the mechanism has changed yet.
- **`hybridizes_with` transmits a donor's whole kit**, not the one trait the edge was drawn
  for. ~26 real merge problems surfaced this way in WP-4.2, patched node by node. A
  slot-scope allowlist would fix the class — needs a ruling before anyone spends a schema
  change on it.
- **Two placement engines, and the default is the weaker one.** `build/geometry.py` searches
  and `build/geometry_cp.py` proves; every caller defaults to the search. The search will place a
  room below the floor of its own band and say nothing — the spec Colonial's dining room comes
  out 26% short on every seed — because `level_score` charges a flat 12 points and a candidate
  can win while paying it. The plan record still reads 12 x 12 and `plan_check.py` never reads
  `room.geometry`, so no layer of the critic sees it. That is OQ 54, unruled.
- **A plan's `exterior_walls` are aspirations, not rectangle edges.** Three Tidewater ground
  rooms each declare *opposite* walls, so each would have to span the full depth of the house.
  They are weights, at the 14 points `exterior_score` charges. Do not promote them to
  constraints; the corpus does not mean them that way.
- **The composer does NOT refuse a style with no native parti — it borrows another style's
  diagram and says so in a `why` string nobody reads.** WP-4.5 closed the coverage gap (129 of
  132 styles now native) and raised `NATIVITY_W` from 6 to 20 so a borrowed diagram no longer
  routinely outranks a native one — at 6, five serious findings outweighed being the right
  diagram, and a Tidewater Georgian brief came back recommending an octagon. The hard refusal
  still exists only in `core.py`'s `list_partis`.
- **Reserved voids, and the two things they break.** OQ 55 is built: an outdoor room whose own
  record says it sits within the block (courtyard, piazza, loggia) is placed and dimensioned,
  excluded from the heated envelope, and drawn open. Two traps came with it. On a courtyard
  massing `depth_rooms` describes the RANGE, not the block, so the block's depth target is
  `ranges × pile + the void band` — read the massing's own `footprint` field, not its pile. And
  **the heuristic cannot find a ring**: four thousand candidates put the court in the block's
  corner every time, so `courtyard_slice()` states the ring as a guillotine tree rather than
  searching for one. `geometry_cp.py` inherits it, because it reads its topology off the heuristic.
- **The composer refuses on purpose.** It will not invent a room the parti has no place for,
  will not present an assumption as fact, and will not call a plan good. Refusals belong in
  the decision log, stated. Do not "fix" a refusal into a guess.
- **Every parti must work for the style it was written for.** `check_partis.py` check 10
  composes each parti against its own first native style and fails on a fatal. It is
  **differential** against a control diagram: three of the Cape parti's four original fatals
  belonged to `cape-cod-colonial`'s kit and fired for every diagram, and blaming the parti for
  them would make the check a generator of false accusations.
- **Unjudged reported as failed is the dangerous direction.** Twice found in one package.
  `elevation.py` reported an unmodelled chimney as `visible_chimney_count: 0`, so the fault
  corpus failed a parti named `cape-central-chimney` for having no chimney; and a fault finding
  quoted `results[0]`, printing a PASSING measurement as the evidence for a failure. When a
  generator did not model something, the measurement must be **absent**, not zero.
  **Found twelve more times and closed 26 Aug 2026 (OQ 52)** — a dormer count written over
  `roof.py`'s explicit refusal, five chimney plan dimensions, a stack cap and its shadow lines, a
  raking-cornice count and a gutter's outlets, all stated as constants, all convicting both
  reference plans. The rule is now enforced rather than remembered: `elevation.py` declares a
  `NOT_MODELLED` dict with a reason per name and **filters it at the point measurements are
  returned**, so this class cannot come back by an `m.update()`. To add a measurement to that
  file, model the thing first; to remove a name from the list, model it and delete the entry in
  the same commit. `tests/test_measurement_honesty.py` is the guard.
- **A drawing the reader cannot magnify is a drawing whose dimensions do not exist**, and
  three of the workbench's plate surfaces were fixed at whatever width their column of the
  layout happened to be. `components/PlateViewer.jsx` is the loupe — mounted on the
  Proportions plate, the Plan Workbench sheet and the Drawing Set — and it scales the WHOLE
  plate by a CSS transform, so `getScreenCTM()` still maps back to model feet and the wall
  handles keep working. It measures the outer PANE, never the scroller: a scrollbar
  appearing inside the scroller narrows it, which re-fits the plate, which can make the
  scrollbar go away again. That it magnifies the pen along with the drawing is **OQ 66**.
- **A member's `y_bottom_in`/`y_top_in` are ABSOLUTE in the stack** — `proportion_engine
  .dimension()` has already run the cumulative sum. `OrderPlate` added each assembly's own
  base to them a second time and the Doric order came apart in the frame: the base 90 inches
  clear of its plinth, the cornice out through the top. The captions beside it were drawn
  from a separate and correct total, so the plate labelled a gap CAPITAL. All 26 order packs
  are contiguous 0 → stack with no assembly disagreeing with its stated height; if a plate
  shows a gap, the plate is wrong.
- **A projection means two different things in this corpus, and the pack now says which.**
  Thirteen order packs record `projection_parts` as an offset from the member's OWN NAKED,
  twelve as an absolute radius FROM THE AXIS — split by order, not by authority, across all
  five. Adding a naked to a radius draws the shaft narrower than its own mouldings, and
  `dist/orders.html` did exactly that: Vignola's Ionic came out **2.25× too wide**. OQ 67
  closed by declaring `projection_datum` on the pack — seven declarations, nineteen
  overlays inheriting — and **`check_orders.py` verifies the declaration against each
  resolved pack's own geometry rather than trusting it**, so a wrong one errors on the base
  and on every overlay under it. Read the field; never re-derive it.
- **A click on a wall handle used to be a silent record edit** — `pointerup` committed with
  no movement threshold, so a zero-delta release quantised the dimension to the half-foot
  and snapped it up to 0.75 ft to a bay line, onto the DECLARED record and into
  localStorage. It could not fire while the handle was painted over by its own partition;
  making the affordance work made the bug behind it live. A fix that removes a shield is a
  fix that has to look at what the shield was covering.
- **A room name is an untrusted string and the label fitter was O(W³).** 800 words cost 73
  seconds of CPU, and `POST /api/drawings` takes a plan record verbatim from anyone who can
  reach it. Both fitters cap at twelve words and chunk beyond it.
- **A room's name has to fit in the room, and a fitted size written as an SVG `font-size`
  ATTRIBUTE is ignored.** Both plan renderers now break the name across lines before
  shrinking it, turn it along a slot room, and never truncate — `sheet/label.js` measures the
  real face, `build/render_plan.py` estimates from a per-character table. In `render_plan.py`
  the size must be written `style="font-size:…"`: a presentation attribute loses to that
  sheet's own `.nm`/`.dm` rules, so the fit is computed, discarded, and the label runs through
  the wall anyway. Four more of the same were found in `render_plan.py` and
  `render_section.py` — the infeasibility alarm, both scale bars, every interior room
  outline's weight, the section's red over-span figure — and
  `tests/test_drawn_labels.py` now asserts the GENERAL form: for any property a class sets,
  no element carrying that class may also set it as an attribute. `e2e/walk.mjs` asserts no
  label leaves its room — and asserts the room COUNT and the LABEL count first, because a
  selector matching nothing, or a sheet that draws no labels at all, passes it vacuously.
  **The walk now runs in CI** (`workbench/scripts/walk.sh`); until 26 Aug 2026 this file
  called it a guard and no job ran it.
- **A sync generator handed to `StreamingResponse` holds an anyio threadpool token for its
  whole life**, not for the instant it produces a line. Starlette wraps a sync iterator in
  `iterate_in_threadpool`, one token per `next()`, and `jobs.events` blocked in
  `queue.get(timeout=1.0)` — so readers watching a compose contended with every sync `def`
  endpoint against a pool 40 wide for the whole application, `/api/health` included, which is
  what the platform healthcheck polls. Measured at 25 ms / 194 ms / 1021 ms of health latency
  for 8 / 48 / 80 open streams, flat after. `jobs.events` is `async` now, draining with
  `get_nowait()` and awaiting between drains; the queue stays a thread-safe `queue.Queue`
  because the compose worker puts to it from a plain thread, often before any consumer exists.
  **If you add an SSE route, its body must be an async generator** —
  `test_sse_does_not_hold_threads.py` pins it.
- **Compression must skip SSE *and* `/assets`, by PATH.** `GZipExceptSSE` in `app.py` wraps
  Starlette's gzip. THREE SSE routes go round it -- `/api/rail/messages`, `/api/jobs/*/events`
  and **`/mcp`**, which the first version missed and which survived only on a Starlette
  content-type default no requirements pin guarantees. **`/assets` goes round it for a
  different and sharper reason**: compressing the 1.19 MB bundle per request cost 569 ms at
  Starlette's default level 9 and 38 ms even at level 4, against 8 ms plain -- on the EVENT
  LOOP, because `FileResponse` streams 64 KiB chunks and Starlette only offloads at 128 KiB,
  and on a route outside both the auth gate and the rate limiter. One anonymous caller at
  1.76 req/s saturated the core. `workbench/scripts/precompress.py` writes a `.gz` at build
  time and `ImmutableStatic` serves it: 9.6 ms, better ratio, zero per-request CPU.
  **Never pass only `minimum_size` to `GZipMiddleware`** -- `compresslevel` then inherits 9,
  which is 3.5x the CPU of level 4 for 4.6% fewer bytes. **The obvious test for the SSE half
  cannot fail**: Starlette holds a streaming response uncompressed until it exceeds
  `minimum_size` and the first SSE chunk is a few dozen bytes, so asserting
  `content-encoding != gzip` on a real stream passes with the exemption deleted. Assert the
  middleware's dispatch instead.
- **Do not hand-roll a request body limit; Starlette ships `RequestBodyLimitMiddleware`.** A
  hand-rolled one here was wrong four ways, the sharpest being a 500 instead of a 413 on
  `/api/rail/messages` (it reads its body directly, so nothing converted the `ClientDisconnect`
  the middleware induced). **Register it INSIDE the auth gate.** The gate is a
  `BaseHTTPMiddleware`, which wraps `receive` in an anyio task group; the limiter answers 413
  by catching its own `_RequestBodyTooLarge`, and wrapped that way the exception surfaces as an
  `ExceptionGroup` it never matches. Outside the gate: 500 plus a traceback. Inside: a clean
  413. Both measured.
- **`copy_json` is `json.loads(json.dumps(o))`, so caching a cheap build can be slower than the
  build.** An audit cached `corpus.phylogeny()` on the argument that it was "the same bug as
  the search index, one endpoint over" and made it **7.8x slower**: the rebuild walks
  already-in-memory `core._data()` at 0.23 ms, the cached path pays 1.79 ms to copy 157 KB out.
  The endpoint costs ~20 ms end to end and the build was 1.1% of it -- the rest is FastAPI's
  encoder. `search_index()` IS worth caching (2.74 ms rebuild, re-globs 21 files) and returns
  the SHARED object with no copy. Measure before imitating a neighbouring cache.
- **An instrument that cannot fail is worse than a test that cannot fail**, because its output
  is a number rather than a green tick. `workbench/scripts/load.py` misreported three separate
  times: it timed an IDLE server at its most-loaded point (the job had finished and the streams
  had closed), it read 5.0 ms for an endpoint that costs 215 ms (it replayed one plan into
  `_SOLVE_CACHE`), and it measured the UNCOMPRESSED path throughout while being used to say
  compression was free (`urllib` sends no `Accept-Encoding`). It now refuses a point it cannot
  hold, carries a fresh plan id, and asks for gzip.
- **A caller-supplied parti id becomes a path in exactly one place: `core.load_parti`.** Three
  copies of that join existed and two were unsanitised — `core.place_plan` carried the 25 Aug
  `basename` fix and a comment claiming it covered `/api/drawings/{kind}`, which does not route
  through `place_plan` at all. Same shape as the citation grammar's three spellings. Do not add
  a fourth; `test_parti_confinement.py` scans the tree for one.
- **Benchmarking this server has two traps that both report success.** `build/geometry.py`
  keys `_SOLVE_CACHE` on `json.dumps(plan)`, so replaying one plan measures the cache —
  `/api/drawings/plan` read 5.0 ms that way against a real 215 ms, 43x out. And the heavy
  endpoints are metered at 60/hour per identity, so an unmodified sweep measures
  `limits.py`. `load.py` carries a fresh plan id per request; raise `HEAVY_CALLS_PER_HOUR`
  for the run.
- **Open questions are live**, and this line was stale for a day, which is worth knowing before
  trusting any list of them. `docs/open-questions.md` holds **77 entries, of which 22 are open**
  (7, 8, 9, 10, 11, 18, 36, 37, 38, 39, 40, 41, 64, 66, 67, 68, 72, 73, 74, 75, 76, 77).
  **73-77 are the infrastructure audit's.** The tally counts the two HALF CLOSED entries (18,
  68) as open, because a half-closed question is an open one; the file marks 20 with a literal
  `**OPEN`. That list is DERIVED from the file by
  `tests/test_wp46_packs.py::test_claude_md_open_question_list_is_derived_from_the_file_not_asserted_against_a_literal`,
  which also requires the ids to be a bare comma-separated list — putting prose inside the
  parentheses makes its regex match nothing and the assertion fires on an empty set, which is
  how this line was broken and caught while writing it. **69, 70 and 71 were raised AND
  ruled on 26 Aug**, all three from WP-5.6 — and all three were raised on that branch as 64, 65
  and 66, colliding with main's block for the second parallel-session collision in two days;
  main keeps its numbers and these were reissued, with the conversion table at the foot of the
  register. 69 is a session-scoped test fixture that gated every test file sorting after it
  (closed — the token is per-test now, and `test_zz_auth_leak_guard.py` sorts last to keep it
  so); 70 the map's gazetteer (closed — and the check was the smaller half: 59 styles had a
  `geography.hearth` naming somewhere finer than their regions, which nothing was reading, so
  locality placements went 15 → 87 without authoring a single new fact); 71 `test_solver.py`'s
  downgrade pin, which measured 9 against a bound of 8 intermittently (closed — it asserts the
  proof rather than the count, and reports COULD NOT EVALUATE when the machine could not run
  CP-SAT at all). **All three were corrected the same day by an adversarial audit that found the
  first fix of each incomplete — read `docs/reports/wp-5.6-navigation-overhaul.md` §8 before
  trusting any of them.** **Ids 32-41 mean something
  different since the 25 Aug merge** — two sessions ran in parallel and both issued that block, so
  main's ten (deployment, the workbench, the export layer) keep those numbers and this branch's ten
  were reissued as **54-63**, with a conversion table at the foot of the register. A commit message
  or report written before the merge still carries the old number. OQ 48, 50, 51 and 16 closed on
  25 Aug; **52 and 53 were raised the same day by an adversarial audit of this session's own work
  and need a ruling** -- 52 is the elevation generator inventing measurements the fault corpus then
  convicts houses on, 53 is `check_addresses.py` comparing `quantity` without `units`, which has two
  live wrong dimensions. The list is DERIVED from the file by a test rather than asserted against a
  literal, and an unrecognised status word now fails that test rather than counting as settled. **OQ 55 reopened at the merge and CLOSED AGAIN 26 Aug 2026**: it had closed with the
  open-void guarantee stated in BOTH engines, and the engine that stated it as a hard constraint
  was the one that did not survive. `geometry_cp.py` now states it again — 0.0 sf over an open
  court where the heuristic still places 296 sf and pays its 40 points. Two things worth carrying
  forward from that fix: a scoring tolerance is **not** a placement licence (mirroring the
  heuristic's 1 ft charge threshold let a room sit 1 ft into the court), and **`_absorb` runs
  after the solve with no cross-level view**, so it grew that room straight through the hole —
  a guarantee proven and then undone by a post-pass. It takes a `keepout` now.
  - **Environment-blocked, not unstarted: OQ 7, 8, 9, 10, 11**, and the source half of **OQ 18**.
    Every one needs a legible facsimile. `loc.gov`, `archive.org` and `hathitrust` all fail to
    connect from here. **None may be closed from a secondary source or a modern redrawing** —
    that is how a guess gets laundered as `measured`.
  - **OQ 18 (half closed)** — the note half is done: **0** editorial parameters are silent now,
    all 162 say plainly that no source is recorded and quote the basis their slot states. The
    SOURCE half is blocked with 7-11. **The breakdown was reclassified on 25 Aug after an audit and
    the earlier one was wrong**: it read "has a `value` key" as "is a figure" and called 82 records
    bare figures when 72 of them are categorical prose ("bay-or-building", "plain, or pulvinated in
    the Gibbsian manner") that no citation would ever sharpen into a number. True shape of the 162:
    **23 a bare single figure** (the weakest form, and where library access should start -- not 82),
    **82 a categorical call** needing a source that the tradition makes this choice, **55 a band**,
    **2 a set**. The quoted basis was also cut at a hard 150 characters, mid-word 148 times; it now
    cuts at a sentence or clause and marks every elision.
  - **OQ 50** — ornament is rationed and not distributed, in 26 nodes across nine traditions, with
    `italian-renaissance` as the one control case. Ruled 25 Aug to stop at the principle
    (`docs/model.md`); a fault would need the elevation layer to model ornament ZONES, which it
    does not.
  - **OQ 51 (RULED 25 Aug, and the largest thing outstanding — this is the next work)** — the
    lineage cascade delivers packs nobody bound. **Ruling: adjudicate first, flip second.** Work the
    gaps nobody has judged, in leverage order; where the inherited pack is right for the node, add
    the node to that pack's `applies_to` — that IS the adjudication, and it moves the gap from
    unendorsed to endorsed; where it is wrong, bind the right pack or scope the edge. When
    `unendorsed` approaches zero, add `inherits_packs` and make inheritance opt-in, at which point
    it is a safety net rather than a cliff that strands 294 gaps in one commit. Doing it the other
    way round was costed and refused: opt-in now is a morning of mechanism and a corpus-wide
    stranding.
    **The meter.** `build/check_inheritance.py` pins three numbers that may only go down: **294
    role_gaps**, **3,367 inherited_packs**, **233 unendorsed**. The split matters — a gap whose
    pack `applies_to` already names the node is the cascade delivering what an author INTENDED, and
    counting those 61 as faults would make the work list wrong. `--unendorsed` prints the list by
    pack, because adjudicating one pack settles every node under it: `storey-graduation` 38,
    `opening-proportion` 23, `trim-classical` 16, `chambers-ionic` 15 (on `carpenter-gothic` and
    both Gothic Revivals), `facade-gable` 14, `sash-light` 12, `brick-course` 11.
    **The accepted risk, stated because it is real:** wrong dimensions keep arriving while the
    backlog is worked. `--slots ranch-style` shows 69 of 78 dimensioned slots governed by packs it
    never bound. That is tolerable only because it is counted.

## Conventions

Commits are written in the project's own voice: what changed, what was found, and what was
deliberately not done. Findings belong in the message, not just the diff. Branch is `main`,
remote is `origin` (github.com/codex-lux/Traditional-Design-Language, private).
