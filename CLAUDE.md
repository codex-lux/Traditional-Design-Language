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
python3 build/check_all.py     # 22 checks incl. the full pytest suite. ~3 min. Must be green.
```

The data and every checker run on the standard library alone, deliberately — `requirements.txt`
covers only the tooling above the data. `check_all.py` runs the suite as `sys.executable -m
pytest` rather than the bare `pytest`: WP-2.3 found those were different interpreters here, and
sixteen tests were skipping while the run reported success.

Individual pieces: `build/validate.py`, `build/check_kits.py`, `build/check_constraints.py`,
`build/check_pack_bindings.py --strict`, `build/check_rooms.py`, `build/check_partis.py`,
`build/check_faults.py`,
`build/proportion_engine.py selftest`. Useful while authoring:
`python3 build/resolve_kit.py <style-id> --verbose` shows a kit's full provenance chain, and
`python3 build/solver.py <plan> --time 60` places a plan by constraint rather than by search.

## Where the work stands (24 Aug 2026)

Phases 0, 1, 2, 3 complete. Phase 4 complete through WP-4.3 and WP-4.5. Phase 5 not started.

164 nodes · 95 slots (ontology 0.5.0) · 40 massings · 58 rooms · 16 groupings ·
**21 partis naming 129 of 132 styles, 0 uncovered** · 36 packs (129 of 132 nodes bound) ·
660 constraints migrated, 61.5% of hard ones tested · 209 faults · **159 of 159 kits
populated** · 322 image records, 0 sourced · 14 reference plans · 24 MCP tools · 344 tests.

**Next, in order:**
1. **WP-4.6** — missing proportion packs. List ready from WP-4.1; OQ 30 names the
   Islamic/Moorish arch-and-ornament system as the most-corroborated gap, and WP-4.5 has
   just added a courtyard parti for the styles that want it.
2. **WP-4.4** (HABS images), then Phase 5.

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
- **Outdoor rooms are dropped before placement.** `geometry.py` and `solver.py` both filter on
  `is_indoor`, so a courtyard — the void 19 styles are built around — composes and renders as
  solid. Pre-existing, and OQ 33.
- **The composer refuses on purpose.** It will not invent a room the parti has no place for,
  will not present an assumption as fact, and will not call a plan good. Refusals belong in
  the decision log, stated. Do not "fix" a refusal into a guess.
- **Open questions are live.** `docs/open-questions.md` (31). OQ 27, 29, 30, 31 and the
  `hybridizes_with` problem await Lucas's ruling. OQ 31 is a new category the corpus has no
  vocabulary for: not "unjudged", but *judged where the judgment does not apply*.

## Conventions

Commits are written in the project's own voice: what changed, what was found, and what was
deliberately not done. Findings belong in the message, not just the diff. Branch is `main`,
remote is `origin` (github.com/codex-lux/Traditional-Design-Language, private).
