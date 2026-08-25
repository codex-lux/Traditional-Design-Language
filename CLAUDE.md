# Traditional Design Language — working notes for Claude Code

A system that encodes traditional architecture as a language: elements are the alphabet,
proportioning systems are the grammar, a style is a set of bindings and constraints on a
universal slot set, and a named-error corpus catches the things that read as wrong to
someone fluent. The aim is a compiler — brief in, buildable and coherent house out.

## Read these before doing anything

1. **`STATE-OF-THE-PROJECT.md`** — what exists, what is half-built, what is unstarted.
   Revised 24 Aug 2026 against verified counts. Part III is the honest list of gaps.
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
python3 build/check_all.py     # 23 checks incl. the full pytest suite. ~7 min. Must be green.
```

The data and every checker run on the standard library alone, deliberately — `requirements.txt`
covers only the tooling above the data. `check_all.py` runs the suite as `sys.executable -m
pytest` rather than the bare `pytest`: WP-2.3 found those were different interpreters here, and
sixteen tests were skipping while the run reported success.

Individual pieces: `build/validate.py`, `build/check_kits.py`, `build/check_constraints.py`,
`build/check_pack_bindings.py --strict`, `build/check_rooms.py`, `build/check_partis.py`,
`build/check_faults.py`, `build/check_counts.py` (fails the build when a number in this
file, in `STATE-OF-THE-PROJECT.md`, in `README.md` or in `docs/` disagrees with the data -- run it
with `--fix` to rewrite them), `build/proportion_engine.py selftest`. **When authoring or binding a pack, run
`build/pack_addresses.py <pack-id>`**: it lists every `(slot, dimension)` address the pack shares
with packs it co-binds with and prints both notes side by side. Several rules at one address is
usually right -- a menu within one pack, or two packs meaning the same quantity, which is what
precedence is for. Two packs meaning DIFFERENT quantities is a silent corruption and the fix is a
named dimension. Eight were found this way in WP-4.6; that is OQ 48. Useful while authoring:
`python3 build/resolve_kit.py <style-id> --verbose` shows a kit's full provenance chain, and
`python3 build/solver.py <plan> --time 60` places a plan by constraint rather than by search.

## Where the work stands (25 Aug 2026)

Phases 0, 1, 2, 3 complete. Phase 4 complete through WP-4.3 and WP-4.5. Phase 5 not started.

164 nodes · 96 slots (ontology 0.6.0) · 40 massings · 60 rooms · 17 groupings ·
**21 partis naming 129 of 132 styles, 0 uncovered, and 21 of 21 composable for their own
style** · **53 packs, 131 of 132 nodes bound** — but 50 nodes still have no opening-role pack
and 56 no facade-role pack, which is where WP-4.6's remaining leverage is · 660 constraints
migrated, 61.5% of hard ones tested · 209 faults · **159 of 159 kits populated** · 1,556 kit
parameters (74.6% measured, 10.4% editorial with neither source nor note — that is OQ 18) ·
322 image records, 0 sourced · 14 reference plans · 24 MCP tools · **23 checks, 667 tests**.

**Every open question Lucas has ruled on is executed** as of 25 Aug 2026 — OQ 12, 13, 14, 15,
19, 26, 27, 29, 31, 32, 33, 34, 35, 36, 37, 38, 39, and 40 through 46 besides. **OQ 18** is the
one that stays open on purpose: 162 kit parameters are editorial with neither a source nor a
note, 156 of them on the Georgian kit, and closing it needs real sources rather than more code.
WP-4.6's second tranche raised **no new open question** — the two things it found that are not
done are missing packs, which are work rather than rulings, and they are in the candidate list
in `docs/reports/wp-4.6-missing-proportion-packs.md`.

**Next, in order:**
1. **WP-4.6** — missing proportion packs. **Seventeen of thirty-odd done** (`moorish-arch`,
   `greek-doric`, `adobe-module`, `opening-pointed`, `opening-craftsman`, `trim-prairie`,
   `dutch-gambrel`, `balcony-gallery`, `stone-course`, `facade-arcade`, `timber-panel`,
   `opening-mullioned`, `facade-gable`, `trim-sawn`, `octagon-geometry`, `facade-pavilion`, `jetty-overhang`),
   chosen by measuring leverage rather than by list order; the measurement and what remains are in
   `docs/reports/wp-4.6-missing-proportion-packs.md`. Several list items collapsed into each other
   once measured, which is the tranches' recurring finding: the four-centred Tudor arch and the
   leaded casement turned out to be one window (`opening-mullioned`), four ornament items turned
   out to be one machine (`trim-sawn`), and the French travée facade and the mansard/dormer module
   turned out to be one system (`facade-pavilion`). Remaining by the same measurement: a
   **portada/retablo panel**, a **peripteral/arcuated Greek-Roman system**, and **Mudejar brick
   corbelling**. Items the report
   now names as NOT SUPPORTABLE from this corpus, with the reason stated rather than left silent:
   the Baroque curved/undulating wall (no figure in any of 22 matching nodes), strapwork and
   linenfold, the Romanesque foliate capital, Prairie rectilinear art glass, Alpine carved timber.
2. **WP-4.4** is **environment-blocked**, not deferred — the proxy answers 403 to CONNECT for
   www.loc.gov. `build/harvest_habs.py` is written, dry-run exercised and queued against the day
   the network opens; its own status block in `PLAN-OF-ACTION.md` carries the verbatim denial. The
   network-free next step there is giving the 322 asset records their `provenance.building` names,
   without which every harvest query degrades to a style-name search. Then Phase 5.

WP-2.3 closed Phase 2 on 24 Aug 2026: `build/solver.py` states placement to CP-SAT, enforces
room minimums instead of scoring them, and returns a named conflict set when a brief cannot be
housed. Read `docs/reports/wp-2.3-real-solver.md` before touching geometry — the exact-tiling
formulation the plan of action named does not work (CP-SAT could not decide it in 240 s while
holding a valid solution), and the solver reads the slicing tree off a heuristic layout instead.
`build/geometry.py` remains the default engine everywhere.

## Traps worth knowing before you hit them

- **Module loading.** Everything in `build/` and `mcp_server/` loads siblings *by file path*
  so each script also runs standalone. That returns a fresh module per call and the loads
  nest — one `check()` used to execute plan_check 16x, geometry 8x. `build/modcache.py` now
  caches by realpath and every local `_mod`/`_load` delegates to it. **Do not reinstate a
  local loader**; `tests/test_modcache.py` counts module executions to catch it.
- **`hybridizes_with` transmits a donor's whole kit**, not the one trait the edge was drawn
  for. ~26 real merge problems surfaced this way in WP-4.2, patched node by node. A
  slot-scope allowlist would fix the class — needs a ruling before anyone spends a schema
  change on it.
- **Two placement engines, and the default is the weaker one.** `build/geometry.py` searches
  and `build/solver.py` proves; every caller defaults to the search. The search will place a
  room below the floor of its own band and say nothing — the spec Colonial's dining room comes
  out 26% short on every seed — because `level_score` charges a flat 12 points and a candidate
  can win while paying it. The plan record still reads 12 x 12 and `plan_check.py` never reads
  `room.geometry`, so no layer of the critic sees it. That is OQ 32, unruled.
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
- **Reserved voids, and the two things they break.** OQ 33 is built: an outdoor room whose own
  record says it sits within the block (courtyard, piazza, loggia) is placed and dimensioned,
  excluded from the heated envelope, and drawn open. Two traps came with it. On a courtyard
  massing `depth_rooms` describes the RANGE, not the block, so the block's depth target is
  `ranges × pile + the void band` — read the massing's own `footprint` field, not its pile. And
  **the heuristic cannot find a ring**: four thousand candidates put the court in the block's
  corner every time, so `courtyard_slice()` states the ring as a guillotine tree rather than
  searching for one. `solver.py` inherits it, because it reads its topology off the heuristic.
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
- **Open questions are live.** `docs/open-questions.md` (49, of which 8 are open). Everything
  Lucas ruled on 24 Aug is executed. Still open and needing a ruling: **OQ 49** (a node can need one
rule of a pack without being an instance of its type -- `french-normandy-revival` states
`jetty-overhang`'s material-change rule verbatim and has no jetty, and a binding cannot be scoped to
one slot), **OQ 48** (1,922 rule-address collisions
measured, of which the dangerous kind is two packs meaning DIFFERENT quantities at one address --
four found and fixed, the rest unknown; no checker shipped because a naive one would flag 1,710
correct rules), **OQ 47** (no slot for an exposed
structural member on a wall face -- four packs in WP-4.6 route one through `corner_board`),
**OQ 41** (a fault's
  secondary tests are written for one style and run against every style — why
  `cape-cod-colonial` cannot currently return a clean plan under any diagram), **OQ 42**
  (`types_present` is not aliased), **OQ 40** (`area_weight` is read as a boolean, never as a
  share). **OQ 18** stays open on purpose: 164 parameters are editorial with neither a source
  nor a note, 156 of them on the Georgian kit, and closing it needs real sources rather than
  more code.

## Conventions

Commits are written in the project's own voice: what changed, what was found, and what was
deliberately not done. Findings belong in the message, not just the diff. Branch is `main`,
remote is `origin` (github.com/codex-lux/Traditional-Design-Language, private).
