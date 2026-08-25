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
python3 build/check_all.py     # 25 checks incl. tests/ AND workbench/server/tests. Must be green.
                               # (the two CAD-export selftests report N/EV — COULD NOT
                               #  EVALUATE — without the optional ezdxf/ifcopenshell;
                               #  that is a named unjudged state, never a pass)
```

Individual pieces: `build/validate.py`, `build/check_kits.py`, `build/check_constraints.py`,
`build/check_pack_bindings.py --strict`, `build/check_rooms.py`, `build/check_faults.py`,
`build/proportion_engine.py selftest`, `build/export_dxf.py selftest`,
`build/export_ifc.py selftest`. Useful while authoring:
`python3 build/resolve_kit.py <style-id> --verbose` shows a kit's full provenance chain.

## Where the work stands (25 Aug 2026)

Phases 0, 1, 2, 3 complete — **WP-2.3 landed 25 Aug**: `geometry.solve()` is CP-SAT
(`build/geometry_cp.py`, OR-Tools optional behind an honest fallback), the record's declared
facts are hard constraints, an infeasible plan returns a named conflict set plus the labelled
least-bad drawing, and every wall pin the flat footprint provably cannot hold is downgraded
*stated* (`solver.refinements`) — the exposure idiom finding is OQ 37. A same-day adversarial
audit (four independent auditors; findings + fixes in the WP-2.3 report's audit section)
closed a door-constraint hole, over-broad downgrades, and a set of protocol-honesty gaps.
Phase 4 complete through WP-4.3.
Phase 5 started out of order: **WP-5.2 complete** — the workbench is live in `workbench/`
(FastAPI over `mcp_server/core.py` + a Vite/React frontend; an approved divergence from
the package text's self-contained `dist/` HTML file). **WP-5.1 complete (25 Aug)** —
DXF/IFC export with a proven round-trip (DXF → record → identical findings), optional
deps behind honest refusals, live in the workbench's Export card (`docs/export.md`).
**WP-5.5 complete (25 Aug)** — drawing-to-record ingestion: the Transcription surface
(⑪), the drafter-DXF extractor (candidates + named gaps, never guesses), plan schema
0.2.0's `provenance` object (`docs/ingestion.md`). WP-5.3 not started (waiting on
Phase 4 breadth by choice); WP-5.4 deferred until the plan-development partnership exists.

164 nodes · 95 slots (ontology 0.5.0) · 40 massings · 58 rooms · 16 groupings ·
**12 partis naming only 39 of 132 styles** · 36 packs (129 of 132 nodes bound) ·
660 constraints migrated, 61.5% of hard ones tested · 209 faults · **159 of 159 kits
populated** · 322 image records, 0 sourced · 14 reference plans · 24 MCP tools ·
340 tests · 39 workbench server tests (in `workbench/server/tests/`, now run by check_all too).

**Next — two tracks that can run in parallel:**

*The main line, in order:*
1. ~~**WP-2.3 — a real solver.**~~ **Done 25 Aug 2026** — see the status paragraph above
   and `docs/geometry.md`'s "The real solver".
2. **WP-4.5 — partis.** 39 of 132 now gates the composer's reach harder than kits ever did;
   a style with a canonical massing but no native parti cannot be composed for at all. Note
   the package text is stale on rooms — all 58 already carry `style_variation`.
3. **WP-4.6** (missing packs; list ready, OQ 30 names the Islamic/Moorish system as the
   most-corroborated gap), then **WP-4.4** (HABS images).

*The platform track — unblocked now, no Phase 4 coupling (§6 hangs Phase 5 off
Phases 1–3, all complete):*
- ~~**WP-5.1 — DXF/IFC export.**~~ **Done 25 Aug 2026** — see the status paragraph above.
- ~~**WP-5.5 — drawing-to-record ingestion.**~~ **Done 25 Aug 2026** — the pipeline that
  lets HABS drawings and a builder's back catalogue become records now exists; WP-4.4's
  image sourcing can feed it.
- **WP-5.3 — generated guidelines** waits for WP-4.4/4.6 by choice, not dependency: it is
  generated from data, so regeneration is free, and a book generated today is mostly
  `wanted` images and unjudged calls. **WP-4.7** stays scope-only by design.

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
- **The composer refuses on purpose.** It will not invent a room the parti has no place for,
  will not present an assumption as fact, and will not call a plan good. Refusals belong in
  the decision log, stated. Do not "fix" a refusal into a guess.
- **Open questions are live.** `docs/open-questions.md` (38). OQ 27, 29, 30, 31, 32–34, 36, 37, 38 and
  the `hybridizes_with` problem await Lucas's ruling. OQ 31 is a new category the corpus has
  no vocabulary for: not "unjudged", but *judged where the judgment does not apply*. OQ 32–34
  are the workbench's findings: validator findings carry no stable id, geometry relaxations
  are counted but not located, and the composer's decision log is prose lines, not records.

## Conventions

Commits are written in the project's own voice: what changed, what was found, and what was
deliberately not done. Findings belong in the message, not just the diff. Branch is `main`,
remote is `origin` (github.com/codex-lux/Traditional-Design-Language, private).
