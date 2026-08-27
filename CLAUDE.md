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
in `workbench/`), WP-5.5 (drawing-to-record ingestion), **WP-5.6 (the navigation overhaul)** and
**WP-5.7 (the geometry layer)** have shipped; WP-5.3 and WP-5.4 remain.

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
style** · **57 packs, 132 of 132 nodes bound** (OQ 49; but read OQ 51 before trusting that number -- it counts a node's OWN bindings and the lineage cascade delivers packs nobody bound) — but 49 nodes still have no opening-role pack
and 46 no facade-role pack, down from 68 and 67 (WP-4.6's measured movement) · 660 constraints
migrated, 61.5% of hard ones tested · 210 faults · **159 of 159 kits populated** · 1,556 kit
parameters (74.6% measured, 12.8% editorial of which 0 are now silent — OQ 18's note half) ·
322 image records, 0 sourced · 14 reference plans · 24 MCP tools · **32 checks, 970 tests**
(plus the workbench app suite, `node --test`). The test figure was 762 here and had been stale
for some time -- `check_counts.py` polices counts DERIVED FROM THE CORPUS, and a test count is
not one of them; nor are numbers written into JSX, which is how the Kit's header claimed 95
slots against an ontology holding 97.

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
  is **OQ 51** and is the one with 3,366 instances. Read it before trusting "132 of 132 bound".
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
- **A fault's tests live in THREE places and the third is the one that bites.** `test`,
  `secondary_tests`, and **`exceptions[].bounds_test`**, which `core.check_measurements`
  SUBSTITUTES for the primary on a matching style. OQ 78 and 79 guarded the first two; Second
  Empire's bounds_test `dormer_count / bay_count == 1.0` then convicted a house stating NO dormers
  the moment WP-5.9 began supplying that zero, and `craftsman`'s `dormer_count at-most 1` acquitted
  one. Neither reference plan is Second Empire or Craftsman, so 1,018 green tests saw nothing —
  it took sweeping all 164 styles with one plan's measurements. **Guarding a fault means all three
  locations**, and `tests/test_measurement_honesty.py` now enumerates them so a future pass has
  something to check against.
- **Verifying a corpus-wide change on the plans that happen to ship is verifying it on 2 of 164
  styles.** Three separate defects in WP-5.9/5.10 were invisible to both reference plans and fell
  out of a style sweep in seconds. If a change touches the fault corpus or the measurement set,
  sweep the styles.
- **A NEGATIVE assertion whose selector breaks inverts into a tautology.** `assert 'class="ch"' not
  in text` stopped matching when the stack gained a weight rung, and the suite then held both "no
  chimney on the front" and "two stacks on the front" — green, because only the broken selector
  kept them apart. The same stale pin had been fixed one test earlier in the same diff. Match the
  TOKEN (`class="ch`), and prefer a positive assertion with a count.
- **A fault silenced by a NAME MISMATCH reads exactly like a fault that was checked.**
  `cornice-that-is-a-fascia` carries two RIVAL secondaries on one expression — the domestic boxed
  eave at 0.35–0.55 of its own height and the full entablature case at 0.85–1.2 — so whichever is
  right the other convicts the house. WP-3.2 worked around it by withholding
  `cornice_projection_in` and publishing `cornice_projection_past_wall_face_in` instead: the same
  quantity under a different name. The fault then came back **clear** on one surviving secondary
  while its primary and two others were skipped for want of a NAME rather than a number — 1 of 5
  tests evaluating. Closed at OQ 78 by taking the measurement the fault's own note always asked
  for (*"Choose the test by whether an order is present"*) and guarding both rivals with
  `applies_when`. **The obvious discriminator is a trap and is pinned as a test**:
  `gibbs_order_applies_to_style` is True on `tidewater-georgian` and means only that Gibbs Ionic is
  the order its cornice is GENERATED from — reading it as "an order is applied here" selects the
  entablature test on a house measuring 0.4286 and convicts it. A one-bay portico is not enough
  either; only an order engaging the whole wall makes the eave an entablature.
- **Two records built from different rules, and nothing compared them.** `roof.py` puts the stacks
  at `y_ft` 21.33 on a 42.66 ft gable end — its centre line — and `_face_bays()` independently
  spaces an odd bay count evenly, putting a window centre at 21.33. The elevation drew a window
  where a chimney stands, on every gable elevation this corpus has ever produced, and it was found
  by DRAWING the stack from grade for one revision. Each record is right on its own. OQ 79 closed
  it: the bay a stack stands on is `blind`, no opening at either storey, and
  `window-on-the-chimney-axis` catches the collision where a record states both. The generator
  publishes `count_of_openings_on_the_axis_of_a_chimney_stack` as a MEASURED zero — it resolved a
  collision, it did not fail to have one.
- **A node's own MEASURED parameter can contradict a pack rule at the same address, and OQ 48's
  checker could not see it.** The kit writes `projection_in`; a pack writes dimension `projection`;
  the two never meet under one name. `tidewater-georgian` authored its brick sill at **0–1 in
  measured** while `sash-light` delivered **2.25 in "sloped about 1 in 6"** to the same slot — in a
  node whose kit FORBIDS the sloped sill and says why. `check_addresses.py` gained `kit_vs_pack()`
  and the first measurement is **133, ratcheted** (OQ 80); five nodes carry 116 of them. **And the
  rule reaches a node TWICE** — live through `eval_packs`, and baked into an ancestor's kit file as
  an authored parameter carrying `source: <pack>`. Scoping the binding (`slots_except`, new) closes
  one path only; the other is closed at the child.
- **`open` does not mean open.** `resolve_slots` stops its walk only on `specified` or `forbidden`,
  so a slot bound `open` — the style declining to constrain it — inherits its nearest ancestor's
  record in full. `colonial-revival`'s `dormer` was `open`, and resolved from
  `english-cottage-vernacular` with a thatch dormer canonical and **`boxed-dormer` forbidden**: the
  style could not declare the only dormer it is built with. That instance is bound now; the
  mechanism is OQ 81 and reaches all 97 slots.
- **The moment a record can finally STATE a zero, every rule that presupposed the thing runs on it.**
  WP-5.9 gave the plan schema `declared.dormer` with three states — key absent (could not evaluate),
  `"none"` (a measured zero), an object (a house with dormers) — and both reference houses stated
  none. `dormer-off-the-bay`'s parity secondary is `dormer_count % 2 == 1`, which had never run
  because no generator supplied the number; on the first run after they could, both were convicted
  of **"Dormers Off the Rhythm: 0 against equals 1"**. Zero dormers is not an even number of
  dormers. Fault tests now carry **`applies_when`**, a precondition on the MEASUREMENTS in the same
  shape as a test (`schema/fault.schema.json`), beside `applies_to_styles`'s precondition on the
  style; a test whose precondition fails is **not run**, not passed. **Any test whose expression
  divides by a count needs one**, or it errors on the house that has none. This closed
  `docs/elevation.md`'s own open question 1, which had asked for exactly this field after WP-3.2
  found three instances — two of those three are guarded now, and the third is OQ 78.
- **A fault could vanish from every list, and a fault in no list reads exactly like a clear one.**
  `check_measurements` sorted into present / clear / could-not-judge; a fault whose every test
  declines produces no evaluation, no missing measurement and no error, so it was appended to
  nothing and dropped out of the summary counts too. **`not_applicable` is a fourth returned
  state** (surfaced by `plan_check` as `fault_not_applicable`), carrying which precondition
  declined and what it required. Not a pass: the question does not arise.
- **The slot id is singular because the ontology's is.** `declared.dormer`, not `dormers` —
  `plan_check` reads every key of `declared` as an ontology slot, and a plural one earned both
  reference plans a `minor` finding saying it was not in the ontology. A `declared` value may now
  be an OBJECT for a slot of cardinality `many`, and it states its variant under `variant` so the
  forbidden-variant check still reaches it.
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
- **A test of the MODEL is not a test of the DRAWING, and this corpus has now been caught by that
  twice in two days.** WP-5.7 deleted `TestSegTo` for pinning the control points of curves that
  had silently degenerated to straight lines — then shipped `svg_path()` with an **inverted SVG
  sweep flag**, so every one of the 245 arcs in the corpus was drawn as its own mirror about its
  chord: an ovolo as a cavetto, a torus as a hollow, on all three surfaces at once. It passed 34
  checks, 970 tests, a selftest that proved the constructions, and the browser walk, because every
  one of them interrogated the model and none asked where the ink went. Worse, four constructions
  were ALSO wrong in model space, and the two families of bug **cancelled** on about half the
  corpus — so fixing only the sweep flag would have made the drawings worse, which is
  "a fix that removes a shield is a fix that has to look at what the shield was covering" at
  corpus scale. `tests/test_drawn_geometry.py` is the guard: it reads the emitted path back
  through the W3C endpoint-to-centre rule and asserts the drawn arc is the modelled one. **Both JS copies of the sweep rule are now gone (OQ 77): `build/profiles.py` serves
  finished paths in MODEL space and the two surfaces apply an SVG transform, so a mirror is a
  negative number in a matrix rather than a flag to derive. A source-reading test fails if arc
  arithmetic reappears in either file.**
- **The sweep flag follows the NET handedness of the transform, not the y-flip.** SVG's flag is 1
  when the ellipse's parameter increases in SCREEN space (y down); these angles increase in MODEL
  space (y up). A y-flip reverses it and so does an x-mirror, and two flips cancel. The order tool
  draws its section half with x one way and its mirrored elevation half with x the other, through
  the same y-flip: reading only y gave both halves the same flag and the plate contradicted itself
  down its own centre line.
- **A moulding is CONSTRUCTED, in one place, and JavaScript does not know what a cyma is.**
  `build/profiles.py` turns a member's height and projection into real geometry — a quarter of an
  ellipse for an ovolo, two tangent arcs through the chord's midpoint for a cyma, a half round for
  a torus — and every surface consumes it: `dist/orders.html`, the workbench Proportions plate,
  `render_elevation.py`'s cornice inset and `export_dxf.py` (as bulges, so an arc reaches CAD
  exactly). Pack geometry is **linear in the module**, proved in `tests/test_profiles.py`, which is
  what lets it be computed once and merely scaled. **Do not port these constructions into JS.**
  The file this replaced, `orders_template.html::segTo`, was hand-tuned Beziers — and worse,
  `profile_silhouette_path()` called its Python port with `xa == xb` on EVERY member, so every
  curve degenerated to a vertical face and the cornice drew as steps whatever the data said.
  `TestSegTo` pinned that function's control points exactly and could not see it: **pinning the
  arithmetic of a curve nobody can see is not a guard.** Tests assert geometry — convexity,
  tangency at a cyma's join, scale invariance — never path strings.
- **A pack's `projection_datum` is true of its COLUMN and not of its ENTABLATURE.** OQ 65 declared
  it per pack and `check_orders.py` verifies it against the shaft. But `gibbs-ionic` declares
  `axis` while its frieze face records a projection of **0**, and a frieze cannot stand on the
  column's centre line — so entablature figures there are relief from the naked. Read the
  declaration literally over a cornice and every member narrower than the column radius clamps
  flush, **deleting the bed mould**; `dist/orders.html` still draws it that way. `eave_cornice()`
  detects the entablature's own datum from evidence instead. That is **OQ 72**, open. Beware also
  a coincidence: the wrong reading put the cornice's relief within 1.7% of `facade-classical`'s
  independent figure, and taking that as corroboration would have shipped the bug.
- **The honesty discipline has to reach the RENDERERS, not just the records.** OQ 52 swept twelve
  invented constants out of `elevation.py`'s measurements and is guarded by a test that reads the
  measurements dict — which cannot see SVG. A hardcoded 36 in chimney width and ±4/±2/±6 px fake
  projections lived happily on the other side of that line for as long as the file existed, drawn
  over the top of real figures sitting unread in the record. Both are fixed; the class is not.
  And a figure the corpus flags **`judgment: true`** may be DRAWN but never published as a
  measurement: the chimney's 22 in is a decision the mason still owes ("18 or 27"), so its
  `NOT_MODELLED` entries stay and the sheet labels the figure.
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
- **Open questions are live**, and this line was stale for a day, which is worth knowing before
  trusting any list of them. `docs/open-questions.md` holds **83 entries, of which 21 are open**
  (7, 8, 9, 10, 11, 18, 36, 37, 38, 39, 40, 41, 64, 66, 67, 68, 73, 80, 81, 82, 83). **82 and 83
  came from WP-5.10's own adversarial audit: the sill scope it fixed on one node reaches 27
  masonry nodes and two more pack rules have the same shape (82), and three measurements are still
  withheld to work around gaps `applies_when` now covers while `total_shutter_leaves` is supplied
  as an unconditional constant of 2.0 whether or not the style carries shutters (83).** **78 and 79 closed
  27 Aug (WP-5.10) and raised 80 and 81 between them: 80 is 133 addresses where a node's own
  MEASURED parameter contradicts a pack rule, which OQ 48's pack-versus-pack measurement could
  not see because the two are written under different names; 81 is that a slot bound `open` —
  the style declining to constrain it — inherits its ancestor's constraints in full, because
  `resolve_slots` stops its walk only on `specified` or `forbidden`.** **72, 73 and 74 were
  WP-5.7's, about the geometry layer: the entablature's datum, two sourced rules disagreeing about
  the cornice's projection, and the front elevation that could not draw its own chimneys. 72 and
  74 are closed — 74 by WP-5.9, which found the renderer still asserting in a twelve-line comment
  the flat-eave-line behaviour the roof layer had stopped having earlier in the same package, and
  two invented constants underneath it putting a brick bar in the sky.** **78 and 79 are WP-5.9's,
  from the dormer layer: `cornice-that-is-a-fascia`'s two rival secondaries, where whichever is
  right the other convicts the house — inert today only because it tests on a measurement name
  nothing supplies — and a gable-end-exterior stack standing on the centre line of a gable end
  whose elevation puts a window there, with no layer asking whether they collide.** **69, 70 and 71 were raised AND
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
    **The meter.** `build/check_inheritance.py` pins three numbers that may only go down: **293
    role_gaps**, **3,366 inherited_packs**, **222 unendorsed** (294 / 3,367 / 233 when first
    measured; the first two moved on 27 Aug when `colonial-revival` bound its own dormer slot,
    which is the meter moving the right way). The split matters — a gap whose
    pack `applies_to` already names the node is the cascade delivering what an author INTENDED, and
    counting those 71 as faults would make the work list wrong. `--unendorsed` prints the list by
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
