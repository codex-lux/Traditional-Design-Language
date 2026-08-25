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
- **A passing test is not evidence until you have watched it fail.** Before trusting a test
  you just wrote, revert the line it defends and confirm it goes red. This is not
  ceremony: an audit on 25 Aug found three tests in one session that passed either way —
  one asserted an ordering the sorted globs already guaranteed, one compared a literal
  against the same literal, and one drew its parametrized cases *from the set under test*,
  so shrinking that set shrank the cases and left nothing to fail. All three read as
  thorough. Watch it fail, then trust it.

- **Findings matter as much as code.** Finish a work package with a report in
  `docs/reports/<wp-id>-<slug>.md`: what was built, what was found, what was deliberately
  not done, and any new open question appended to `docs/open-questions.md`.

## Verifying

```
python3 build/check_all.py     # 21 checks incl. the full pytest suite. ~3 min. Must be green.
```

Individual pieces: `build/validate.py`, `build/check_kits.py`, `build/check_constraints.py`,
`build/check_pack_bindings.py --strict`, `build/check_rooms.py`, `build/check_faults.py`,
`build/proportion_engine.py selftest`. Useful while authoring:
`python3 build/resolve_kit.py <style-id> --verbose` shows a kit's full provenance chain.

## Where the work stands (24 Aug 2026)

Phases 0, 1, 3 complete. Phase 2 complete **except WP-2.3**. Phase 4 complete through WP-4.3.
Phase 5 not started.

164 nodes · 95 slots (ontology 0.5.0) · 40 massings · 58 rooms · 16 groupings ·
**12 partis naming only 39 of 132 styles** · 36 packs (129 of 132 nodes bound) ·
660 constraints migrated, 61.5% of hard ones tested · 209 faults · **159 of 159 kits
populated** · 322 image records, 0 sourced · 14 reference plans · 24 MCP tools · 307 tests.

**Next, in order:**
1. **WP-2.3 — a real solver.** The largest remaining structural gap. `docs/geometry.md`
   says it plainly: the compositional terms from WP-2.2 are *strongly-weighted preferences
   a 250-candidate random search converges toward, not hard constraints a solver enforces*.
   An infeasible brief returns the least-bad plan rather than a named conflict set, which is
   the thing a plan-development partner most needs to hear early. CP-SAT over the same bay grid.
2. **WP-4.5 — partis.** 39 of 132 now gates the composer's reach harder than kits ever did;
   a style with a canonical massing but no native parti cannot be composed for at all. Note
   the package text is stale on rooms — all 58 already carry `style_variation`.
3. **WP-4.6** (missing packs; list ready, OQ 30 names the Islamic/Moorish system as the
   most-corroborated gap), then **WP-4.4** (HABS images), then Phase 5.

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
- **Open questions are live.** `docs/open-questions.md` (31). OQ 27, 29, 30, 31 and the
  `hybridizes_with` problem await Lucas's ruling. OQ 31 is a new category the corpus has no
  vocabulary for: not "unjudged", but *judged where the judgment does not apply*.

## Conventions

Commits are written in the project's own voice: what changed, what was found, and what was
deliberately not done. Findings belong in the message, not just the diff. Branch is `main`,
remote is `origin` (github.com/codex-lux/Traditional-Design-Language, private).
