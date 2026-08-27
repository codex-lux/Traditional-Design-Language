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

## Where the work stands (27 Aug 2026)

Phases 0, 1, 2, 3 complete. Phase 4 complete through WP-4.3, WP-4.5 and WP-4.6; WP-4.4 is
environment-blocked. **Phase 5 is part-built** — WP-5.1 (DXF/IFC export), WP-5.2 (the workbench
in `workbench/`), WP-5.5 (drawing-to-record ingestion) and **WP-5.6 (the navigation overhaul)**
have shipped; WP-5.3 and WP-5.4 remain. **Phase 6 — plan semantics — is COMPLETE** (WP-6.1,
6.2, 6.3 and **WP-6.4, the audit of the other three**, 26–27 Aug).

**Phase 6 exists because Lucas read two rendered sheets and found them meaningless** — the
project's own founding failure mode, every part well-formed and the whole saying nothing. A
kitchen whose only drawn door was to the outside; a stair hall with no stair; a centre passage
whose rear door read as a window; triangular marks pointing at anything and everything. Every
symptom was reproduced by execution, and they split three ways. **WP-6.1** — the sheet was
lying about the record: interior doors were silently dropped below a flat 3.2 ft of shared
wall, `door.type` was read by nothing, exterior doors went on the first wall a room declared.
**WP-6.2** — the record had nothing to say: a door was `{to, width?}` with no wall, position,
hinge or rank, so each renderer invented one and invented it differently. Plan schema **0.3.0**
admits placed geometry and placed openings; `openings/grammar.json` (30 editorial rules over
all 1,890 room pairs) says what kind of opening belongs between two rooms; `build/openings.py`
places them, the stair and the wet-room fixtures; `plan_check` gained a **`drawn`** layer — the
only layer permitted to read placement — which walks the house from the front door. **WP-6.3**
— the placement itself was the deepest cause, and the workbench was drawing on the weaker of
the two engines. **WP-6.4 audited the other three and found the program's own disease inside
it**: eleven claims in source, schema and docs that 6.1–6.3 falsified and nobody updated, plus
one real defect (a downloaded DXF was a different placement from the sheet on screen) and one
check that was claimed in a comment and never written. Reports:
`docs/reports/wp-6.{1,2,3}-*.md` and `wp-6.4-the-audit.md`; read WP-6.3's refusals before
proposing a score term here, and WP-6.4's closing note before writing "until X lands" in a
comment.

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
**30 opening-grammar rules covering all 1,890 room pairs** (WP-6.2, editorial; every rule quotes the corpus prose it reads and `build/check_openings.py` verifies the quote against the record it names) ·
**21 partis naming 129 of 132 styles, 0 uncovered, and 21 of 21 composable for their own
style** · **57 packs, 132 of 132 nodes bound** (OQ 49; but read OQ 51 before trusting that number -- it counts a node's OWN bindings and the lineage cascade delivers packs nobody bound) — but 50 nodes still have no opening-role pack
and 46 no facade-role pack, down from 68 and 67 (WP-4.6's measured movement) · 660 constraints
migrated, 61.5% of hard ones tested · 209 faults · **159 of 159 kits populated** · 1,556 kit
parameters (74.6% measured, 12.8% editorial of which 0 are now silent — OQ 18's note half) ·
322 image records, 0 sourced · 14 reference plans · 24 MCP tools · **35 checks, 1,006 tests**
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
  is **OQ 51** and is the one with 3,367 instances. Read it before trusting "132 of 132 bound".
  OQ 51 is now RULED -- adjudicate the 233 unjudged gaps first, flip inheritance to opt-in after --
  so this trap is a work list rather than an unanswered question. It is still live until that list
  is worked; nothing about the mechanism has changed yet.
- **`hybridizes_with` transmits a donor's whole kit**, not the one trait the edge was drawn
  for. ~26 real merge problems surfaced this way in WP-4.2, patched node by node. A
  slot-scope allowlist would fix the class — needs a ruling before anyone spends a schema
  change on it.
- **BEARING CONTINUITY AND DECLARED STACKING ARE TWO PROBLEMS, AND OQ 76 CONFLATED THEM
  (WP-7.1).** The generator WAS blind to the other level; `slice_rect` is now called for
  level 1 with the ground layout, and `snap()` prefers a wall line below over a bare bay
  line. Measured corpus-wide over 14 composed plans: **transfer beams 166 -> 109,
  relaxations 96 -> 76**, total score improved. Over 23 plans including both shipped ones,
  transfer beams **205 -> 128**. That is the bearing half, and it is closed for this engine.
  **`stacks_over` did not move: 26/47 broken -> 27/47.** Moving a cut line moves a wall; it
  does not move a room over another room. Do not expect the generator to fix stacking, and
  do not quote WP-6.3's stated reason for refusing the stair charge — *"the search can only
  re-rank blind candidates and can never produce a stacking one"* is FALSE: measured over 24
  seeds the winner satisfies 1-3 of tidewater's 3 claims and 0-2 of spec's 2. The charge was
  inert because it keyed on landing-over-stair and neither shipped plan declares that pair.
  A hard CP constraint stays refused for its own measured reason: `geometry_cp.py` downgrades
  **only** `kind == "wall"` pins, so anything else outranks every authored exterior wall
  (measured: it downgraded an authored kitchen wall to satisfy an inferred stack).
- **The level-aware generator is for the PLACEMENT and not for the CP HINT, and that split
  is measured (WP-7.1).** `solve_heuristic(level_aware=...)` is True everywhere except
  `geometry_cp._hint_heuristic`, which asks for the blind run. A hint's only job is to be
  REPAIRABLE and a placement's is to be right. Also: the two `snap` forms are NOT
  interchangeable — the slab branch snaps a WIDTH and a wall line below is an absolute
  position, and quietly changing one into the other moved the GROUND placement, cost CP-SAT
  its proof of `tidewater-georgian-careful` (OPTIMAL -> UNKNOWN at budget), and took an
  afternoon to find. The blind path must stay byte-identical.
- **The search has NO span term, so `spans_exceeding_capacity` is luck (WP-7.1).**
  `test_no_span_over_capacity_passes_silently_on_the_careful_plan` asserted the careful plan
  had none — measuring `build_section(plan)`'s HEURISTIC default while the product ships CP.
  On the default engine that plan has carried a **29.00 ft span over a 20 ft capacity since
  WP-6.3**, and nothing noticed. The test now asserts what is real: spans are computed, the
  capacity is checked, and an over-capacity span surfaces. Do not restore a zero assertion —
  it pins luck.
- **An over-band charge is an under-band charge plus a constant, because the slicer tiles
  exactly (WP-6.3).** `Sum max(0, got-hi) == (T - Sum hi) + Sum max(0, hi-got)` is an
  identity, verified to under 0.5 sf. Three formulations were run through the whole search
  and **not one room changed size**. Over-size is already billed symmetrically by
  `level_score`'s `abs(got-want)/want*10`. `over_band()` REPORTS and deliberately does not
  charge, and it carries `declared_over_ceiling` because 5 of the 12 rooms over their
  ceiling on the Tidewater placement are over it AS DECLARED too — blaming the placement
  for those is the OQ 52 error in a new place. (SIX rooms are declared over their ceiling;
  `passage` is one and is then placed under it. Two questions, two counts; say which.)
- **`_absorb` can break a keep-out and can never break a contact or a stack (WP-6.3).**
  Every branch moves one face outward and `max(w, cap/h)` floors each candidate at the
  current extent, so there is no shrink path and the shared face is algebraically frozen.
  Growth is monotone: upper bounds are unsafe, lower bounds are safe by construction. That
  is what OQ 55 actually established. Fuzzed over 4,000 layouts — worst shrink 0.014 ft
  against a 0.4 ft tolerance. Do not add a keep-out for doors or stacks; there is nothing
  there to fix.
- **A door's required shared wall is the door's own leaf and jambs, in ONE place
  (WP-6.3, OQ 41 closed).** `openings.required_wall_ft`, used by both renderers, both
  exporters, the CP model and `hard_fact_violations` — which had carried a second
  transcription of the old rule, which is how an arbiter comes to convict placements the
  solver proved legal. The rule it replaced (`min(4, floor(0.9*min(maxside)))`) **never
  once fired its own protective branch**: `maxside` is the LONGER side, and 0 of 238 rooms
  in the corpus qualify, so every closet in the corpus was being asked for a parlour's 4 ft.
  Fixing it let CP-SAT solve `tidewater-georgian-careful` for the first time — a *stricter*
  rule for most pairs made the model easier — and took that plan's undrawable doors from 11
  to 1 and its fatal findings from 3 to 0.
- **"Until X lands" is a lie the moment X lands and is refused (WP-6.4).** Auditing 6.1-6.3
  found **eleven claims in source, schema and docs that those packages falsified and nobody
  updated** — `geometry.py`'s docstring promising a charge WP-6.3 measured and refused;
  `compose.py` saying "a corruption the drawn layer now reports" when nothing in the repo
  compared a door's two records; `plan.schema.json` advertising a `severed_doors` field
  nothing has ever produced; `docs/workbench.md` saying `render_plan.py` "omits [exterior
  doors] entirely" when it has drawn them since WP-6.1. **No test catches any of these,
  because they are prose.** When you refuse a planned change, go back and correct every
  comment that promised it, in the same commit. When a package supersedes a deliverable, say
  *superseded* in the refusals list rather than letting it vanish.
- **A drawing set is ONE building, and it was not (WP-6.4).** `corpus._placed()` places a
  plan once on `auto` and every sheet takes it. Before it: the plan SVG used `auto`,
  `export_dxf._solved_copy` forced `heuristic`, and `structure.build_section` took its own
  heuristic default — so a reader looking at a CP-proved sheet **downloaded a DXF of a
  different placement of the same house**, with a third under the section beside it. The
  client posts the DECLARED record, so the exporter's has-geometry short-circuit never fired.
  `build_section` KEEPS its heuristic default (it is the derivation step inside plan_check's
  elevation layer and the composer's scoring loop — a CP solve there is 25 s x N in
  `check_all`); what changed is that every user-facing caller passes `geometry_result`.
- **The bench draws on `auto` now, and the caption must READ which engine ran rather than
  assert one (WP-6.3, extended WP-6.4).** The disclosure lives on the PLATE in both
  renderers, not only in the page prose beside it: a printed or exported plate leaves prose
  behind, and a reader then cannot tell a proof from a search. Three defaults had to flip, not one: `evaluate.py`, `corpus.py`,
  and `app.py`, whose route default `body.get("engine", "heuristic")` shadowed both others
  and was the one that mattered. The moment it flipped, the sheet's own paragraph — "each
  edit re-scores on the fast search … nothing it draws asserts that feasibility was proved"
  — became false in the direction that matters, because a reader could no longer tell a
  proof from a search. It now reads `geometry_report.solver.engine` and names the fall-back
  reason when `auto` tried the proof and did not get one; `e2e/walk.mjs` checks that claim
  against the API's report, not against a phrase. **The wall drag is the one caller that
  asks for the hill-climb by name**, and there is deliberately no settle-timer re-proof
  behind it: a second render landing mid-gesture replaces the handle under the pointer and
  the drag dies.
- **A relaxation △ goes on a wall or it goes in the caption, and an annotation must not eat
  the click under it (WP-6.3).** The CP counter emitted a line with no extent, refusing to
  invent one; both renderers then drew it as a 5 ft tick at **the middle of the plan**,
  which put a mark inside the drawing room six feet clear of any wall, over that room's own
  name. That is the "arrows over walls between spaces … they seem to point to anything and
  everything" of Lucas's review, and WP-6.1 read it as a missing legend — owed, and the
  smaller half. `_count_relaxations` was looping over the very rectangles whose faces lie on
  the line, so it now carries `runs`: measured, possibly disjoint. **`relaxation_marks`
  (`render_plan.py`) and `relaxationMarks` (`derive.js`) are the one rule** — do not add a
  third. A mark locatable on no wall of its own level is NAMED, never placed somewhere
  plausible. The dashed run carries `pointerEvents: none` because it was swallowing the
  click that selects the room under it: four e2e interaction checks failed for a week and
  were misdiagnosed as CP latency, and a settle timer was written for that wrong cause and
  made it worse. `e2e/walk.mjs` measures each drawn △ against each drawn room.
- **A door is a thing with a place now, and three files must agree about it (WP-6.2).**
  Until 26 Aug a door was `{"to": id}` with an optional width — no wall, no position, no
  rank — so each renderer invented a position and each invented it differently. Plan schema
  **0.3.0** admits the PLACED plan as a record (`geometry`, `footprint`, `stair`,
  `fixture_layout`, and per-opening `wall`/`position_ft`/`positions_ft`/`hinge`/`rank`), and
  `build/openings.py` writes them from **one call site inside `geometry.solve()`** so both
  engines produce the same kind of record. The rule that matters: **an opening the placement
  cannot realise is marked `unplaced` with a reason and never deleted** — and a window's
  DECLARED `count` is never overwritten with what was placed, because losing an author's
  intent to a placement outcome is the silent overwrite this whole package removed. The
  jamb allowance (0.35 ft) and the minimum solid (1.0 ft) are duplicated on purpose in
  `render_plan.py`, `derive.js` and `openings.py`, and
  `tests/fixtures/sheet_symbols/` holds all of them to one contract; change one and two
  suites fail. **The DXF exporter strips placement output from its XDATA** so the round trip
  still returns the AUTHORED record — and `wall` is authored on a WINDOW and solver output on
  a DOOR, which cost one round-trip failure to discover.
- **`openings/grammar.json` is editorial and its citations are CHECKED.** Every rule quotes
  the room-record prose it reads, and `build/check_openings.py` verifies that the record
  exists and that the sentence is really in it. An editorial call whose citation cannot be
  checked is a guess wearing a citation. It also proves totality — all 1,890 room pairs
  resolve to a named rule, the default included, so no opening is ever dimensioned from
  nothing.
- **`plan_check` has a `drawn` layer and it is the ONLY layer that may read placement.**
  OQ 54 ruled the opposite in August and Lucas reversed it on 26 Aug. Every other layer
  stays geometry-blind, which is what keeps the original ruling's real concern intact: an
  unplaced record reports COULD NOT EVALUATE and takes no drawn finding at all. Do not read
  `room.geometry` from any other layer.
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
- **Open questions are live**, and this line was stale for a day, which is worth knowing before
  trusting any list of them. `docs/open-questions.md` holds **78 entries, of which 22 are open**
  (7, 8, 9, 10, 11, 18, 36, 37, 38, 39, 40, 64, 66, 67, 68, 72, 73, 74, 75, 76, 77, 78).
  **Phase 7 half-closed three of them.** OQ 72: two layers decide — the window grammar says a
  window's ROLE, the kit says its SASH KIND, and 119 of 159 styles answer *through the
  lineage* where only 39 answer in the flat kit file. OQ 73: sizing is REFUSED ("the tail
  wagging the dog"), arrangement goes as far as the rooms' own words. OQ 76: the generator is
  level-aware and it fixed BEARING, not stacking.
  **OQ 76 is HALF CLOSED by WP-7.1** — the generator is level-aware and it fixed BEARING
  (transfer beams 166 → 109 corpus-wide) and not STACKING (26/47 → 27/47, flat). **OQ 78 is
  new**: the search has no span term, so clearing the structural capacity is luck, and the
  test that claimed the careful plan cleared it was measuring an engine no reader sees.
  **72-75 come from the plan-semantics program** (WP-6.1/6.2) and are what Lucas's review of two
  rendered sheets turned up that the program did not settle: the per-opening window type and bay
  windows, furniture arrangement beyond wet rooms, the door's hand, and a reference plan that
  cannot satisfy its own style's hard rule about doors at both ends of a passage. **39 and 41 are
  HALF CLOSED by the same program** — a door has a height now, and the renderers learned narrow
  doors — and both stay open because their other halves do. **OQ 54 was RULED AGAIN**: the critic
  reads the drawn house, in one layer and only one. **69, 70 and 71 were raised AND
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
