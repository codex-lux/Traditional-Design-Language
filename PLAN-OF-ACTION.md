# Traditional Design Language — Plan of Action

*Companion to `STATE-OF-THE-PROJECT.md` (revised 24 August 2026). That document says where the project stands; this one says how to finish it. It is written to be cut up and handed to Claude agents one work package at a time. Each package is self-contained: what to read, what to build, what "done" means, and what not to touch.*

---

## Progress board — as of 24 August 2026

Every package below carries a **Status** line. This is the summary. Original package text is left as written even where the work has since been done, so the record of what was asked for stays legible next to what was delivered; where the delivered result diverged from the acceptance text, the Status line says so rather than quietly restating the goal.

| Phase | Packages | State |
|---|---|---|
| **0 — Consolidation** | WP-0.1, 0.2, 0.3 | **Complete** |
| **1 — Executable constraints** | WP-1.1, 1.2, 1.3 | **Complete** — 660/660 constraints migrated, 61.5% of hard constraints tested (bar was ≥60%) |
| **2 — Composition** | WP-2.1, 2.2, 2.3, 2.4 | **Complete** — `build/solver.py` beats the best of 800 heuristic candidates by 10–24% and names a conflict set when a brief cannot be housed |
| **3 — The elevation** | WP-3.1, 3.2, 3.3 | **Complete** — WP-3.2 evaluates 83 of a named 100 faults, disclosed |
| **4 — Breadth** | WP-4.1, 4.2, 4.3, 4.5 complete · **4.4, 4.6, 4.7 not started** | **In progress** |
| **5 — Platform** | none | **Not started** |

**Revised order for the remaining work** (supersedes the recommended order in Section 0, which assumed nothing had been built):

1. ~~**OQ 28**~~ — **done 24 Aug 2026**: `build/modcache.py`. `check()` 3.06 s → 0.31 s, `compose()` 30-40 s → 7-9 s, the suite back to one run at 2 min 24 s. See `docs/reports/oq-28-module-cache.md`.
2. ~~**WP-4.3**~~ — **done 24 Aug 2026**. See `docs/reports/wp-4.3-the-garage.md`.
3. ~~**WP-2.3**~~ — **done 24 Aug 2026**, closing Phase 2. `build/solver.py`. See `docs/reports/wp-2.3-real-solver.md`.
4. ~~**WP-4.5**~~ — **done 24 Aug 2026**: 21 partis, 129 of 132 styles native, 0 uncovered. See `docs/reports/wp-4.5-partis-to-full-coverage.md`.
5. ~~**The open-question pass**~~ — **done 24 Aug 2026**. Every question Lucas had ruled on is
   executed: OQ 12, 13, 14, 26, 27, 29, 31, 32, 33, 34, 35, 36, and 15, 18, 19, 37, 38, 39
   besides. Reports: `docs/reports/oq-33-reserved-voids.md` and
   `docs/reports/oq-37-partis-that-fail-their-own-style.md`. The two that changed the compiler
   rather than the corpus are **OQ 33** (courtyards are placed, and the heuristic gained a
   stated ring layout because it cannot search for one) and **OQ 37** (`check_partis.py` check
   10 — five of twenty-one partis were carrying fatal findings against the styles they were
   written for, so the composer would not recommend them; 21 of 21 compose now).
6. **WP-4.6 — IN PROGRESS, eleven packs of thirty-odd, 25 Aug 2026.** `moorish-arch` (OQ 30's item,
   and the only gap that unblocked a node with no binding at all — `DELIBERATELY_UNBOUND` is down
   from three nodes to one), `greek-doric` (which replaced a binding WP-4.1's own note called
   "the least-bad available approximation"), `adobe-module` (the gap four style nodes had already
   written down in their own binding notes; bound to 9), `opening-pointed` (the opening half of the
   Gothic item — the facade half was measured and found already served), and `opening-craftsman`
   with `trim-prairie`, which are both halves of PB-4's item, `dutch-gambrel`, `balcony-gallery`, `stone-course`, `facade-arcade` and `timber-panel`. **All six packs this work package's own task
   text names as likely candidates are built, plus the largest item the rest of the list held when it
   was measured.** 131 of 132 nodes bound; nodes with
   **no opening-role pack 68 → 60**, which is where the movement now is, plus one wrong interior
   binding corrected, which moves no count at all. The remaining list, with each item's measured
   leverage, is in `docs/reports/wp-4.6-missing-proportion-packs.md`; next by the same measurement is a gable
   geometry system (12 nodes, entirely missing), after which the tail is mostly ORNAMENT rather than
   proportion. Then **WP-4.4** (images), which is currently
   environment-blocked — see its own status block.
7. **Phase 5** — the last mile.

**Three open questions want a ruling before or alongside WP-4.6**, all raised by the pass above
and none of them blocking: **OQ 40** (`area_weight` is read as a boolean and never as a share of
anything, so every parti's weights read as a considered distribution and are not one), **OQ 41**
(a fault's secondary tests are written for one style and run against every style — it is why
`cape-cod-colonial` cannot currently return a clean plan under any diagram), and **OQ 42**
(`types_present` is not aliased, so a plan that models a room under an equivalent name is told it
models none). **OQ 18** is open on purpose and needs sources rather than code.

WP-4.7 stays scope-only by design.

---

## 0. How to use this document

The work is organised into six phases and twenty-two work packages (WPs). Phases are ordered by dependency, not by effort. A WP inside a phase can usually run in parallel with its siblings; the dependency line on each package says when it cannot.

Every package ends with a **hand-off brief** — a paragraph written to be pasted directly into a fresh agent session, with the repo checked out, as the whole of the instruction. The brief assumes the agent will also read Section 1 (operating rules) and the package's own acceptance criteria. Do not hand an agent a brief without Section 1.

The recommended order is: Phase 0 first and alone (it is short and everything else depends on a clean repo and a test suite); then Phase 1 and WP-2.1 in parallel; then the rest of Phase 2; then Phase 3; then Phase 4 in whatever batches are convenient; then Phase 5. Phase 4 is the largest volume of work and the most parallelisable, and it is deliberately placed *after* the compiler work, because authoring 130 kits against a system that cannot yet read its own constraints produces data that will need a second pass.

---

## 1. Operating rules for every agent

These are not suggestions. An agent that violates one of these has produced work that will be reverted.

**Read first.** Before writing anything, read `README.md`, `docs/model.md`, `docs/inheritance.md`, and the `docs/*.md` file for the layer you are working in. Then run the full check suite (Section 1.3) and confirm it is green before you start, so you can tell your breakage from pre-existing state.

**The eleven decisions not to undo.** These are settled. Do not reopen them; do not "improve" around them.

1. The style graph is a DAG, not a tree. `member_of` is for browsing only and carries no inheritance.
2. `descends_from` and `regional_of` carry the kit cascade. `references`, `reacts_against` and `revives` do not. Never let a `references` edge cascade.
3. Massing is not style. Rooms are not style. Partis specify topology and roles only — never dimensions.
4. A style is a set of bindings and constraints on the universal slot set. Adding a style never adds a slot; if it seems to, the ontology is incomplete and that is a separate, flagged change.
5. Proportion packs are functions, not tables. Vignola is the spine; other authorities are overlays carrying deltas. Comparisons are made at a common column *diameter*, never a common module.
6. Judgment slots (`judgment: true`) are marked, not filled. A rule the sources do not determine is deferred to the human, never invented.
7. Faults are element-first; style is a facet via `exceptions`. Exceptions matter as much as rules.
8. Image records are authored before images exist; `license` never ships as `unknown`.
9. The validator is the fitness function. Nothing generative is added without the validator being able to score it.
10. The composer returns N contrasting candidates, never one, and never calls a plan "good".
11. Geometry is bay-grid with *counted* relaxations; both levels are solved together; the footprint grows before a room is compromised; the drawing is a render of the data and nothing is drawn that is not in the record.

**Ids are stable and never reused.** Never rename a style, slot, room, grouping, parti, fault or pack id. If an id is wrong, add the right one and mark the old one `deprecated_in_favour_of`.

**Unjudged is not passed.** Any checker or validator you write must distinguish "evaluated and failed", "evaluated and passed", and "could not evaluate", and must never collapse the third into the second.

**Prose constraints stay.** When a constraint or rule is made executable, the human-readable `statement` is kept beside the `test`. The test is a formalisation of the statement, not a replacement.

**Sources or `kind: editorial`.** Every numeric parameter you author carries a `source` or is honestly marked `editorial`. Do not launder a guess as `measured`.

**Check suite green, then tests, then docs.** A package is not done until: the check suite is green; the behaviour tests (Phase 0) pass and new behaviour has a test; the relevant `docs/*.md` is updated; and the README counts are right. Doc drift was one of the findings of the review — do not add to it.

**Report format.** Finish every package with a short written report in `docs/reports/<wp-id>-<slug>.md` containing: what was built; what was found (the project's tradition is that the findings matter as much as the code — record them); what was deliberately not done; and any open question that needs Lucas's ruling, appended to `docs/open-questions.md` with the next number.

### 1.3 The check suite

```
python3 build/validate.py
python3 build/check_orders.py
python3 build/check_modules.py
python3 build/check_systems.py
python3 build/check_kits.py
python3 build/check_faults.py
python3 build/check_rooms.py
python3 build/check_partis.py
python3 build/proportion_engine.py selftest
python3 build/plan_check.py plans/spec-builder-colonial.json
python3 build/plan_check.py plans/tidewater-georgian-careful.json
python3 build/compose.py briefs/family-georgian.json
python3 build/build.py
```

After Phase 0, `make check` (or `python3 build/check_all.py`) runs all of this plus `pytest`.

---

## 2. Rulings needed from Lucas

Several packages are blocked on decisions that are design judgments rather than engineering. They should be made before the relevant package starts; the package brief says which ones it needs. From `docs/open-questions.md`:

**Settled since this section was written (24 Aug 2026) — no longer blocking:**

- ~~**OQ 24 — the rule language.**~~ Ruled and built in WP-1.1: the fault corpus's `expression`/`threshold`/`direction` pattern extended with `one-of` and `scope`. See `docs/constraints.md`.
- ~~**OQ 12 — split four conflated slots by trade.**~~ Three split in ontology 0.3.0; the fourth, `wall_thickness_expression`, split in 0.5.0 (WP-1.3).
- ~~**OQ 13 — the entablature scattered across three slot groups.**~~ Resolved in 0.5.0 by `derives_from_module` cross-references rather than a regrouping; enforcement is a noted future step, the field exists and is populated.
- ~~**OQ 16 — `rule_append`.**~~ Built in WP-1.3 (kit schema 0.2.1), wired into `resolve_kit.py`.
- ~~**OQ 17 — `applies_when.regions` versus variant status.**~~ Ruled in WP-1.3 and written up in `docs/inheritance.md`: use a variant node when enough diverges to deserve its own identity, `applies_when.regions` when only a single parameter differs.
- ~~**OQ 20 — the cascade at depth.**~~ Answered with corpus-wide data in WP-4.2 wave B: ~26 real merge problems across 129 kits, of three kinds, none a mechanism failure. See `docs/reports/wp-4.2-wave-b-kit-fill.md`.
- ~~**OQ 23, 25**~~ — struck in WP-0.2.

**All ruled, 24 August 2026.** Every question that was blocking a package now has a decision recorded against it in `docs/open-questions.md`; nothing in the remaining plan waits on a judgment.

- **OQ 33 — the courtyard void.** Ruled: reserved voids. Both placement engines carry outdoor rooms as placed, dimensioned voids, excluded from the area budget and the envelope, drawn as open.
- **OQ 35 — vertical adjacency.** Ruled: adjacency rules may declare `relation: above` / `below`, and `plan_check.py` evaluates them across levels. Removes both of WP-4.5's workarounds.
- **OQ 12 and OQ 13 — the ontology changes ruled long ago and never executed.** Ruled: execute both, as ontology 0.6.0 — split `window_head` by trade, enforce the entablature cross-references.
- **OQ 36 — `hybridizes_with`.** Ruled: spend the schema change, a slot-scope allowlist on the edge.
- **OQ 32 — the heuristic's silent under-band placement.** Ruled: report it in `geometry_report`, do not make the heuristic refuse and do not teach `plan_check` to read `room.geometry`.
- **OQ 31 — the garage daylight rule.** Ruled: a `daylight.depth_governs: false` opt-out on the room record.
- **OQ 34 — no half-storey.** Ruled: add an optional `level_offset_ft` beside `level`, which keeps its meaning.
- **OQ 30 — the Islamic/Moorish pack.** Ruled: build it first in WP-4.6.
- **OQ 27 — untagged judgment constraints.** Ruled: tag with `blocked_by` during WP-4.6.
- **OQ 14 — three rail slots.** Ruled: keep the three, state the shared code conflict once. **OQ 26** folds into the same pass.
- **OQ 21 — variant `op` string matching.** Closed: the checker is enough.
- **OQ 29 — the three unbound nodes.** Confirmed; OQ 30's pack retires two of them.
- **OQ 3, 4, 5, 6** — left as standing disclosures. They are recorded uncertainties about history, not defects in the model.

---

## Phase 0 — Consolidation

*Goal: a repository a collaborator or an agent can trust. Short, sequential, do it first.*

### WP-0.1 Repository consolidation

**Status: COMPLETE** (commit history; `docs/reports/wp-0.1-repo-consolidation.md`).

**Depends on:** nothing. **Size:** small.

The disk folder is the 18 August build with loose 19 August Markdown files; v0.6 exists only inside `traditional-design-language.zip`. `_to_delete/` holds three generations of superseded files. `taxonomy.html`, `orders.html` and `tidewater-georgian-plan.svg` are duplicated at the root.

**Tasks.** Extract the zip over the repo root so that `rooms/`, `faults/`, `groupings/`, `partis/`, `plans/`, `briefs/`, `mcp_server/`, `schema/*.schema.json` (11 files) and the v0.6 `build/` scripts are on disk. Delete `_to_delete/` entirely after confirming nothing in it is absent from the extracted tree. Remove the root-level duplicates of `dist/` outputs, keeping `dist/` as the single home for built artefacts. Move the loose root Markdown (`COMPOSER.md`, `GEOMETRY.md`, `PLAN-VALIDATOR.md`, `MCP-SERVER-SETUP.md`, `OPEN-QUESTIONS.md`) into `docs/` if they are not already identical to the `docs/` versions, and delete them if they are. Add a `.gitignore` for `__pycache__` and `dist/plans/*.svg` scratch output. Run the full check suite. Commit as "v0.6 consolidated".

**Acceptance.** `git status` clean; every path the README mentions exists; check suite green; the zip can be deleted or regenerated from the tree with `build/build.py`.

**Hand-off brief.** *The Traditional Design Language repo on disk is out of date: v0.6 is inside `traditional-design-language.zip` at the root. Extract it over the tree, delete `_to_delete/`, remove root-level duplicates of `dist/` outputs, fold loose root `.md` files into `docs/`, add a `.gitignore`, run every checker listed in the README's "Extending it" section until green, and commit. Do not modify any data file. Report what you deleted.*

### WP-0.2 Documentation reconciliation

**Status: COMPLETE** (`docs/reports/wp-0.2-documentation-reconciliation.md`).

**Depends on:** WP-0.1. **Size:** small.

**Tasks.** Regenerate every count in `README.md` from the data (slots are 93 not 82; MCP tools are 23 not 17; kits, faults, rooms, groupings, partis, packs, exemplars, constraints, massing affinities). Update `mcp_server/README.md` to list all 23 tools with one-line descriptions, grouped by layer. In `docs/open-questions.md`, strike 23 and 25 as resolved with a one-line pointer to the layer that resolved them, and record the rulings already made on 1 and 2. Add a `docs/README.md` index that names each doc and the layer it covers, in stack order. Add a `CHANGELOG.md` starting at v0.6 with one line per layer.

Consider writing a small `build/gen_readme_counts.py` that emits the counts block so it never drifts again.

**Acceptance.** Every number in the README is reproducible by a script; no doc references a path that does not exist; `open-questions.md` has no resolved item listed as open.

**Hand-off brief.** *Reconcile the TDL documentation with the v0.6 data. Recount every figure in `README.md` and `mcp_server/README.md` from the files (not from memory), fix them, strike resolved items in `docs/open-questions.md`, add a `docs/README.md` index in stack order, and add a `CHANGELOG.md`. Write a script that generates the README counts block so they cannot drift. Do not change any data or code beyond that script.*

### WP-0.3 Behaviour tests and a single check entry point

**Status: COMPLETE** — 291 tests across 14 files, `make check` is the entry point. Note: the suite no longer runs in under five minutes (~12 min in three chunks) — not a test-suite defect but OQ 28, see the progress board.

**Depends on:** WP-0.1. **Size:** medium.

The data checkers are good; nothing pins *behaviour*. Every finding the docs record as having "earned its place" is a regression waiting to happen.

**Tasks.** Create `tests/` with pytest. Pin, at minimum: validator results on both shipped plans (exact fatal/serious counts and the three named fatals on the spec Colonial); two-hop-through-a-hall adjacency and rank-transparent circulation (a minimal plan each); two-ended daylight halving; `via` on the kitchen–dining rule (butler's pantry plan passes, direct-door-only plan fails); completeness findings separated from defects; composer ranking on `family-georgian` (single-pile first, 0 fatal on all four); composer refusals (a brief asking for a garage against a parti with none is *reported*); geometry spanning rule (a centre passage with opposite exterior walls spans the footprint); footprint depth from massing pile; `extends` resolution producing three-level provenance for `tidewater-georgian`; `check_kits` catching a `replace` naming an undefined id; cross-engine agreement of the order packs (port the existing 0.02 in check into a test); `core.check_measurements` returning `unjudged` for a missing variable, never `passed`. Add `build/check_all.py` (and a `Makefile` with `check`) that runs every checker then pytest. Add a GitHub Actions workflow if the repo has a remote; otherwise a pre-commit hook.

**Acceptance.** `make check` green from a clean checkout in under five minutes; every test is named for the finding it protects.

**Hand-off brief.** *Write a pytest behaviour suite for the TDL plan validator, composer, geometry solver, kit resolver and fault checker. Each test protects one finding recorded in `docs/plans.md`, `docs/compose.md`, `docs/geometry.md` or `docs/inheritance.md` — read those files and write one test per finding, named for it. Pin the exact counts on the two shipped plans and the ranking on `briefs/family-georgian.json`. Add `build/check_all.py` and a `Makefile` target `check` that runs every checker then pytest. Do not change behaviour to make a test pass; if you find a discrepancy with the docs, report it.*

---

## Phase 1 — Make the constraints executable

*Goal: the 660 style constraints (441 hard) become rules the validator, composer and solver can read. This is the step that turns "rules of assembly" from documentation into code, and it unblocks composition, elevation and the kit fill.*

### WP-1.1 Constraint rule language and migration

**Status: COMPLETE** — 660/660 constraints migrated, 365 tested / 295 honestly `scope: judgment`, **61.5% of hard constraints tested** against a ≥60% bar (corpus was at 17.7%). Two reports: `wp-1.1-constraint-rule-language.md` (the language) and `wp-1.1-remaining-families-migration.md` (the other 25 families).

**Depends on:** Phase 0. **Needs ruling:** OQ 24. **Size:** large.

**Proposed rule language (put to Lucas; proceed on a yes).** Reuse the fault `test` object, which has already proved sufficient at element scale:

```json
{ "expression": "roof_pitch_rise_per_12", "threshold": [7, 9], "direction": "within",
  "units": "in/12", "evaluable_from": ["plan", "elevation", "photograph"], "note": "..." }
```

Extend `direction` with `within`, `one-of`, `equals`, and allow `expression` to reference a **constraint vocabulary** of named variables at plan, elevation and site scale (e.g. `bay_count`, `entrance_bay_index`, `facade_width_ft`, `facade_height_ft`, `piazza_bearing_deg`, `chimney_position`, `window_head_datum_per_storey`, `reveal_depth_in`, `principal_room_aspect`). Add `scope` (`plan` | `elevation` | `site` | `section` | `judgment`). A constraint the sources do not determine numerically gets `scope: judgment` and no test — the same honesty as judgment slots.

**Tasks.** Add `constraint.schema.json` and reference it from `style-node.schema.json` (constraints become objects with `id`, `kind`, `severity`, `statement`, `scope`, optional `test`). Write `build/constraint_vocabulary.py` that emits the canonical variable list with units and the layer that can supply each. Migrate all 660 constraints: keep every `statement` verbatim; add a `test` where the statement already carries a number or an enumerable choice; mark the rest `judgment`. Expect roughly 60–70% to be formalisable. Assign stable ids (`<style-id>.c01`…). Write `build/check_constraints.py` (schema, vocabulary membership, thresholds consistent with `kind`, every hard constraint either tested or explicitly `judgment` with a reason). Update `docs/model.md` and add `docs/constraints.md`.

Batch the migration by family (27 families) so agents can run in parallel; one agent owns the schema and vocabulary and merges.

**Acceptance.** Every constraint has an id and a scope; ≥ 60% of hard constraints carry a test; `check_constraints.py` green; a script can answer "which hard constraints of style X are evaluable from a plan record?"

**Hand-off brief (schema owner).** *Design and implement the TDL constraint rule language: a `constraint.schema.json` reusing the fault `test` object pattern from `schema/fault.schema.json`, extended with `within`/`one-of` directions, a `scope` field, and a named variable vocabulary in `build/constraint_vocabulary.py`. Keep prose `statement`s verbatim. Write `build/check_constraints.py`. Then migrate the constraints of the `english-classical` and `american-colonial` families as the worked example, and write `docs/constraints.md` describing the language and the batch procedure for other agents.*

**Hand-off brief (migration batch).** *Migrate the constraints of the TDL styles in family `<family-id>` to the constraint rule language described in `docs/constraints.md`. For each constraint keep the statement, assign an id, set a scope, and add a `test` only where the statement itself supplies the number or the enumeration — never invent a threshold. Mark the rest `judgment` with a one-line reason. Use only variables from `build/constraint_vocabulary.py`; if a constraint needs a variable that does not exist, list it in your report rather than adding it. Run `check_constraints.py` and `validate.py` green.*

### WP-1.2 The validator reads the constraints

**Status: COMPLETE** (`docs/reports/wp-1.2-validator-reads-constraints.md`).

**Depends on:** WP-1.1. **Size:** medium.

**Tasks.** Extend `schema/plan.schema.json` so a plan record can supply the plan-scope and site-scope variables (orientation, `entrance_faces`, bay count and module, roof form and pitch, chimney positions, piazza bearing, lot bearing). Derive what can be derived (bay count from geometry coordinates when present; facade width from the footprint). In `plan_check.py`, replace the style layer's "list hard constraints for hand review" with evaluation: present / clear / unjudged, with the statement and the value. Keep judgment-scope constraints listed for hand review under their own heading. Extend `core.measurement_vocabulary` and `core.check_measurements` to the constraint vocabulary so the MCP tools cover style constraints too. Teach `compose.py` to score constraint findings (fatal on a hard constraint present; the same 100/8/1 weights).

**Acceptance.** Both shipped plans evaluate their style's constraints; the careful Tidewater plan fails none; a deliberately wrong variant (pitch 12:12 on Tidewater) fails the pitch constraint; tests added.

**Hand-off brief.** *Make `build/plan_check.py` evaluate style constraints. Extend `schema/plan.schema.json` with the plan- and site-scope variables from `build/constraint_vocabulary.py`, derive whatever can be derived from the record, and in the style layer evaluate every tested constraint as present/clear/unjudged — never silently passed. Keep judgment constraints listed for hand review. Extend the MCP `core.py` measurement vocabulary and `check_measurements` to cover constraints. Score constraint findings in `compose.py`. Add tests. Record in `docs/plans.md` which constraints the two shipped plans now trip.*

### WP-1.3 Kit schema operators: `rule_append`, slot splits, date-conditional resolution

**Status: COMPLETE** — kit schema 0.2.1, ontology 0.5.0, `rule_append` built, fourth slot split, date-conditional resolution wired (`docs/reports/wp-1.3-kit-schema-operators.md`).

**Depends on:** Phase 0. **Needs rulings:** OQ 12, 13, 16, 17. **Size:** medium.

**Tasks.** Implement `rule_append` in `resolve_kit.py` so a child can add a clause to an inherited rule without restating it (OQ 16). Execute the slot splits Lucas rules on (OQ 12: `window_head` → masonry head / carpentry cap; `corner_treatment` → quoin / corner board; `window_surround` allowing `none` as a value; `wall_thickness_expression` by trade), bumping the ontology to 0.5.0 and migrating the three filled kits with a script. Resolve the entablature scatter (OQ 13) either by a `derives_from_module` cross-reference between the six slots or by a group move — per the ruling. Add a `date` parameter to `resolve_kit.py` and `tdl_resolve_kit` that filters variants and parameters by `applies_when.date_range` (OQ 22) — the data is already populated. Write guidance for OQ 17 into `docs/inheritance.md`.

**Acceptance.** `check_kits.py` green at the new ontology; `tdl_resolve_kit("georgian-colonial-american", date=1740)` returns 12/12 sash and no fanlight; `date=1790` returns 6/6 and a fanlight; tests added; `docs/inheritance.md` updated.

**Hand-off brief.** *Implement three kit-resolver features in the TDL repo: (1) the `rule_append` operator already declared in kit schema 0.2.1 but unused; (2) the slot splits in `docs/open-questions.md` items 12 and 13 exactly as Lucas has ruled them (the rulings are recorded at the top of that file — if they are not, stop and ask), bumping `elements/slots.json` to 0.5.0 and migrating the three populated kits by script; (3) a `date` parameter on `resolve_kit` and the MCP tool that selects on `applies_when.date_range`. Keep ids stable; deprecate rather than rename. Tests and `docs/inheritance.md`.*

---

## Phase 2 — Composition

*Goal: plans that compose, not merely satisfy. The entrance on the entrance front, the principal rooms on the best aspect, service to the rear, the ceremonial sequence as a constraint. Checked against the reference plans Lucas collected.*

### WP-2.1 The reference corpus: transcribe the Plan Examples

**Status: COMPLETE** — 14 reference plans transcribed (7 good, 7 bad) and scored (`docs/reports/wp-2.1-reference-corpus.md`).

**Depends on:** Phase 0 only — can start immediately and in parallel with Phase 1. **Size:** medium.

`Plan Examples/Good Examples` (18 images) and `Bad Examples` (8) are a reference corpus of what the system should aspire to and what it must refuse. They are currently pixels.

**Tasks.** Transcribe at least six good and all eight bad examples into `plans/reference/<slug>.json` against `plan.schema.json`: room types from the catalog (add a `room_type_unmapped` note where no catalog room fits — that is a finding), approximate dimensions scaled from the drawing, doors, exterior walls, windows where legible, and the declared style (best judgment; record confidence). Record provenance (`source_image`, practice if known, `transcription_confidence`). Run every one through `plan_check.py`. Write `docs/reports/wp-2.1-reference-corpus.md` answering four questions: where does the validator agree with the good/bad labelling; where is it blind (a bad plan it scores clean, a good plan it fails); which catalog rooms are missing (the good examples show galleries, alcoves, cabanas, south porches, gun rooms); and — most important — what compositional rules do the good plans obey that no current rule states. Write those candidate rules in constraint-language form as a proposal for WP-2.2.

**Acceptance.** ≥ 14 reference plan records validating against the schema; a findings report with a proposed compositional rule list; candidate new rooms listed for the catalog with their dimensions from the drawings.

**Hand-off brief.** *Transcribe the floor plans in `Plan Examples/Good Examples` and `Plan Examples/Bad Examples` into TDL plan records (`schema/plan.schema.json`, worked example `plans/tidewater-georgian-careful.json`) under `plans/reference/`. Use catalog room types from `rooms/`; where none fits, note it. Score each with `build/plan_check.py`. Then write a report on where the validator agrees with the good/bad labels, where it is blind, which rooms the catalog lacks, and — above all — what compositional rules the good plans obey that the system does not yet state. Express those rules using the vocabulary in `docs/constraints.md` if it exists, otherwise as statements with numbers. Do not modify the validator.*

### WP-2.2 Compositional constraints in the geometry solver

**Status: COMPLETE, with a caveat that matters** — the compositional terms are in and the Tidewater portico now lands on the south wall, but they are strongly-weighted *preferences a random search converges toward*, not constraints a solver enforces. `docs/geometry.md` says so in its own words. WP-2.3 is what makes them real.

**Depends on:** WP-1.2, WP-2.1. **Size:** large.

**Tasks.** Make `geometry.py` read `composition_parti` on the style node, the brief's `entrance_faces`, and the plan-scope constraints. Add scoring terms (and, where hard, rejection) for: the entry porch and the room it opens into lie on the entrance front; `centre-passage` and `entry-hall` types touch the entrance wall; principal rooms (`drawing-room`, `parlor`, `living-room`, `dining-room`) take the front and the best aspect as the style defines it; service rooms (`kitchen`, `pantry`, `laundry`, `mudroom`) sit on the rear or the service side; the ceremonial sequence approach → porch → passage → principal room is a path of increasing privacy rank with no backtracking; on a centre-hall parti the plan is symmetric about the passage to a stated tolerance; principal rooms are proportioned to `room-harmonic` ratios when the style binds that pack. Place doors by rule rather than by contact: centred on the passage wall for principal rooms, never visible from the lavatory, never in the bay a window occupies. Render door swings. Add the rules proposed by WP-2.1 that Lucas accepts.

**Acceptance.** On `tidewater-georgian-careful`, the entrance portico is on the S wall, the drawing room and dining room flank the passage on the front, service is to the rear, and the reported relaxations do not increase by more than two; on the reference corpus, the solver's re-placement of a good plan's topology scores within one severity band of the transcription; tests added.

**Hand-off brief.** *Teach `build/geometry.py` to compose. Read `composition_parti` from the style node, `entrance_faces` from the brief, and plan-scope constraints via the validator. Add scoring and rejection terms for entrance front, principal rooms on the best aspect, service to the rear, the ceremonial sequence, centre-hall symmetry, and `room-harmonic` proportions where bound. Place doors by rule, not contact. The current rendered Tidewater plan puts the portico inside the footprint — that must be impossible afterwards. Keep every relaxation counted and reported. Run the reference corpus in `plans/reference/` as the benchmark and report before/after scores. Tests and `docs/geometry.md`.*

### WP-2.3 A real solver

**Status: COMPLETE (24 Aug 2026), closing Phase 2 — with the formulation the task text names replaced on evidence.** `build/solver.py` states placement to CP-SAT over the same bay grid, keeps the heuristic as hint, cross-check and reported fallback, and beats the best of 800 heuristic candidates on both shipped plans and both briefs (13.1% / 14.8% / 23.6% / 9.7%), inside 60 s every time. An infeasible brief returns a named, deletion-minimised conflict set and no geometry.

The one departure from the task text is load-bearing and was made on measurement, not preference. "Integer room rectangles on bay multiples, no-overlap" — loose rectangles whose areas sum to the footprint — needs `sum(w*h) == W*H` over a dozen nonlinear products, and CP-SAT could not decide that on the shipped spec Colonial **in 240 s with four workers while holding a hint that was itself a valid tiling**. The slicing tree is read back off a heuristic layout instead, which makes tiling structural rather than arithmetic and leaves only the cut positions to solve — linear, and proven optimal in well under a second. The heuristic proposes the topology; the solver proves the geometry. Optimality is therefore per topology, not global, and the report says so rather than claiming an optimum never established.

Three findings came out of it: the heuristic silently places the spec Colonial's dining room 26% below its band on every seed (OQ 32); a plan record's `exterior_walls` are aspirations rather than rectangle edges, and cannot all be asserted (three Tidewater rooms each declare opposite walls); and `check_all.py` was running the suite under a different interpreter than its checkers, skipping all sixteen solver tests and reporting success. See `docs/reports/wp-2.3-real-solver.md`.

**Depends on:** WP-2.2. **Size:** large. **Optional but recommended.**

**Tasks.** Reformulate placement as a constraint programme over the bay grid (OR-Tools CP-SAT is the obvious choice): integer room rectangles on bay multiples, no-overlap, adjacency as touching constraints, exterior-wall requirements, spanning circulation, vertical alignment across levels, the compositional terms from WP-2.2 as hard or weighted soft constraints. Keep the heuristic as the fallback and as a cross-check. Emit the same plan record and SVG. When infeasible, return the minimal infeasible subset so the report can say *which* requirements conflict — "a 3,200 sf single-pile five-bay house cannot hold a library and a breakfast room on the ground floor at these room minimums; drop one or add a dependency."

**Acceptance.** Same outputs as the heuristic; on the two briefs the CP solution scores at least as well as the best of 800 heuristic candidates; an infeasible brief returns a named conflict set rather than a bad plan; solve time under 60 s per candidate.

**Hand-off brief.** *Replace the randomised slicing in `build/geometry.py` with a CP-SAT formulation over the parti's bay grid, keeping the existing heuristic as a fallback and cross-check, and keeping the plan record and SVG outputs identical in shape. Encode adjacency, exterior walls, spanning circulation, vertical alignment and the compositional terms. On infeasibility return a minimal conflicting subset of requirements in plain language. Benchmark against the heuristic on both briefs and the reference corpus; report.*

### WP-2.4 The site layer

**Status: COMPLETE** — `site` on both schemas, composer caps bay count to the lot, renderer draws lot/setback/north arrow; this is what made the Charleston piazza and bank-house constraints evaluable (`docs/site.md`).

**Depends on:** WP-1.2. **Size:** medium.

**Tasks.** Extend `brief.schema.json` and `plan.schema.json` with a `site` object: lot width and depth, street bearing, setbacks, slope direction, prevailing summer wind, solar orientation, adjacent-building condition (freestanding / party wall / row). Make the composer honour lot width when choosing partis (a 24 ft town-house parti for a 30 ft lot; not a five-bay Georgian on a 40 ft lot). Make site-scope constraints evaluable (the Charleston piazza bearing, the Tidewater chimney position relative to the prevailing wind, the Creole gallery orientation). Place the footprint on the lot in the SVG with setbacks and north arrow. Consume the seven site-and-settlement slots where a kit specifies them (`setback_pattern`, `street_relationship`, and so on).

**Acceptance.** A brief with a 30 ft lot never receives a five-bay candidate; the Charleston piazza constraint is evaluated; the render shows the lot.

**Hand-off brief.** *Add a site layer to TDL. Extend the brief and plan schemas with a `site` object (lot dimensions, street bearing, setbacks, orientation, wind, party-wall condition), make `compose.py` filter partis by lot width, make site-scope constraints in `docs/constraints.md` evaluable in `plan_check.py`, and draw the lot and setbacks in `render_plan.py`. Consume the site-and-settlement slots from the resolved kit where specified. Tests, and a new `docs/site.md`.*

---

## Phase 3 — The elevation

*Goal: the first drawing a client could recognise as a house in a style. This is where the proportion grammar and the plan grammar finally meet.*

### WP-3.1 Walls, structure, storeys

**Status: COMPLETE** (`docs/reports/wp-3.1-walls-structure-storeys.md`).

**Depends on:** WP-2.2. **Needs ruling:** OQ 12 done (WP-1.3). **Size:** large.

**Tasks.** Introduce wall thickness into the plan record from `construction_type` (solid masonry two-wythe, brick veneer on frame, 2×6 frame, log, adobe — a small `construction/` catalog with thicknesses and bearing capacity), distinguishing exterior, bearing interior, and partition. Convert clear room dimensions to a dimensioned footprint with walls. Derive storey heights from `storey-graduation` and the style's ceiling constraints; derive floor structure depth from span and the timber-bay module. Identify bearing lines from the bay grid and the spanning-circulation walls, and report spans that exceed the module's capacity. Stair geometry: rise, run, headroom, landing, against code advisory and the stair-and-landing grouping. Output a `section` record (storey heights, floor depths, eave height, ridge height) and a simple section SVG.

**Acceptance.** Tidewater plan emits an outside-to-outside footprint, wall lines, a bearing-line diagram, and a section with eave and ridge heights consistent with the style's pitch constraint; no 2×10 spanning 18 ft passes silently.

**Hand-off brief.** *Give TDL plans walls and a section. Add a small `construction/` catalog of wall assemblies with thicknesses and bearing roles; extend the plan record so rooms keep clear dimensions while the footprint becomes outside-to-outside; derive storey heights from the bound `storey-graduation` pack and style constraints; identify bearing lines and flag spans beyond the timber-bay capacity; check stairs. Emit a `section` record and a section SVG rendered only from the record. Tests; `docs/structure.md`.*

### WP-3.2 The elevation generator

**Status: COMPLETE, one acceptance figure disclosed short** — the elevation evaluates **83** of the 177 applicable photograph-measurable faults, not the named 100. The shortfall was disclosed rather than closed by fabricating data for faults the generator has no model for (interior trim, porch members, photograph-texture statistics). Everything else in the acceptance line holds (`docs/reports/wp-3.2-elevation-generator.md`).

**Depends on:** WP-3.1, WP-1.3. **Size:** large.

**Tasks.** From the placed, walled plan and the resolved kit, generate an elevation record per face: bay lines from the grid; window openings centred on bays with sizes from `opening-proportion` and lights from `sash-light` at the declared date; one head datum per storey (the Georgian rule the pack already states); entrance composition sized by `facade-classical` and the bound order (Gibbs Ionic at the module the pack derives); water table and belt course from `brick-course` where bound; eave cornice from the bound order at the style's entablature reduction; roof outline from WP-3.3; chimneys from the structural constraint; shutters at the corpus's leaf ratio. Render an elevation SVG using the existing JavaScript/Python engine agreement so every moulding is generated, not traced. Then — the payoff — run the fault corpus's 175 photograph-evaluable tests against the elevation record as an **elevation layer** in `plan_check.py`: the half-width shutter, the flush window in masonry, the porch under seven feet, all evaluable from the drawing the system itself produced.

**Acceptance.** A Tidewater front elevation with five bays, centred doorway composed to Gibbs, sash lights correct for the declared date, a single head datum per storey; the elevation layer evaluates ≥ 100 faults on it and the careful plan trips none at fatal; a deliberate half-width shutter in the record is caught.

**Hand-off brief.** *Build the TDL elevation generator. From a walled plan record and the resolved kit, emit an elevation record per face — bays, openings from `opening-proportion` and `sash-light`, entrance from `facade-classical` and the bound order via `proportion_engine.py`, belt and water table from `brick-course`, cornice from the order — and render an SVG from it with every profile generated by the engine. Then add an elevation layer to `plan_check.py` that runs the photograph-evaluable fault tests against the elevation record. Nothing may be drawn that is not in the record. Tests; `docs/elevation.md`.*

### WP-3.3 Roof

**Status: COMPLETE** (`docs/reports/wp-3.3-roof-geometry.md`).

**Depends on:** WP-3.1. **Size:** medium.

**Tasks.** From the massing's roof form and the style's pitch constraint, generate roof geometry over the footprint: gable, hip, gambrel, cross-gable, with the dependency-and-hyphen ridge step-down rule (60–80%) applied to wings. Place chimneys per structural constraints (gable-end vs interior). Check the Cape eave-to-sill relation, the gambrel break, dormer rhythm against bays. Emit a roof plan and feed the outline to the elevation.

**Acceptance.** Roof plan SVG for both shipped plans; wing ridges step down; pitch within the style band; chimney positions satisfy the Tidewater constraint.

**Hand-off brief.** *Generate roof geometry for TDL plans from the massing's roof form and the style's pitch constraint, including hyphen/dependency ridge step-down and chimney placement from the style's structural constraints. Emit a roof record and SVG, and expose the outline for the elevation generator. Tests; extend `docs/structure.md`.*

---

## Phase 4 — Breadth

*Goal: the system speaks every style it names. High volume, highly parallel, mostly authoring. Start only after Phase 1 so the authored data is born executable.*

### WP-4.1 Proportion-pack bindings for all 132 buildable styles

**Status: COMPLETE — 129 of 132 bound**, three deliberately unbound (`egyptian-revival`, `moorish-andalusian`, `mudejar`) behind a named `DELIBERATELY_UNBOUND` allowlist in `check_pack_bindings.py --strict`. The task text ("do not bind the wrong pack") was honoured over the literal 132-of-132 acceptance line, and the tension recorded as OQ 29 rather than gamed. ~25 missing packs identified for WP-4.6 (`docs/reports/wp-4.1-proportion-pack-bindings.md`).

**Depends on:** Phase 1. **Size:** large, parallel by family. **Highest-leverage authoring in the project.**

The Georgian binding in `styles/georgian-colonial-american.json` is the template: each pack with `role`, `precedence`, optional `authority`, and a note that says *why this authority* (Gibbs because colonial inventories record his book). Only five styles have one.

**Tasks.** For every style and variant node, author `proportion_packs`: primary and secondary orders where classical; the facade system; the opening system; the material module (brick course, timber bay, log) where the style is proportioned from one; trim family; room system; storey graduation. Where a needed pack does not exist (a Gothic Revival facade system; a Craftsman opening system; an adobe module; a Greek Doric order other than Benjamin's), list it — do not bind the wrong pack. Write `build/check_pack_bindings.py`: every buildable node has a binding; every pack id resolves; no node binds both `trim-classical` and `trim-craftsman` as primary; precedence is a total order.

**Acceptance.** 132 of 132 buildable nodes bound; checker green; a list of missing packs with the styles that need them, as input to WP-4.6.

**Hand-off brief (per family).** *Author `proportion_packs` bindings for every style and variant in TDL family `<family-id>`, following the form and reasoning of the binding on `styles/georgian-colonial-american.json` exactly — role, precedence, authority, and a note that says why this authority for this style with a source. Bind only packs that exist in `proportions/`; where the right pack does not exist, list it in your report with what it would need to encode. Run `check_pack_bindings.py` and `validate.py` green.*

### WP-4.2 Kits via `extends`, family level first

**Status: COMPLETE — all 159 kit files populated.** Required a mechanism build first: family nodes had no kit files and carry no lineage edges, so "extend against the family" had nothing behind it until `build.py` learned to generate family kits and splice a style's own family into the cascade via `member_of`. Then 129 style/variant kits filled in two sub-waves. OQ 20 answered with data. Two reports: `wp-4.2-family-kits.md` (wave A, the mechanism) and `wp-4.2-wave-b-kit-fill.md` (wave B, the fill + the merge-problem findings).

**Depends on:** Phase 1, WP-1.3. **Needs rulings:** OQ 17, 20. **Size:** very large, parallel by family.

**Tasks.** Fill kits top-down so the cascade pays: first the 27 family nodes (each specifying the slots the family genuinely shares — roof family, construction, trim family, plan logic), then the 90 styles (using `extends` against the family wherever the style adds rather than restates), then the 42 variants as 10–30 overrides. Every `specified` slot needs variants with `status`, `parameters` with units and sources, and `forbidden` where the style forbids. `garage_strategy` is `specified` on every contemporary buildable variant (WP-4.3). Run the three-level cascade test from `docs/plans.md` on each family: if a style's provenance shows 0% from the family, the family kit is dead weight — fix the family, not the style. Mark `kind: editorial` honestly and list parameters needing a source.

**Acceptance.** No kit at `status: "empty"`; `check_kits.py` green; `resolve_kit` shows multi-level provenance on every variant; OQ 20 answered with data (how many merge problems appeared at three levels and what kind).

**Hand-off brief (per family).** *Fill the TDL kits for family `<family-id>`: the family node first, specifying only what every member shares; then each style using `extends` against the family wherever it adds rather than restates; then each variant as overrides. Follow `kits/georgian-colonial-american.kit.json` and `kits/tidewater-georgian.kit.json` for form and depth, `docs/inheritance.md` for the cascade rules. Units and sources on every parameter; `editorial` where you have none. Run `check_kits.py` after every file and `resolve_kit.py` on every variant to confirm the family contributes. Report the provenance percentages and any merge problem you hit.*

### WP-4.3 The garage

**Status: COMPLETE (24 Aug 2026).** `groupings/garage-and-hyphen.json` authored (8 internal rules, 14 `attaches_to` entries incl. one `forbidden` massing); `compose.py`'s `attach_garage()` places by attachment and refuses with a stated reason where the grouping records none; the last 4 living nodes bound, taking the corpus to 58 `garage_strategy` bindings with every living style covered. Acceptance met and tested both ways — the composer cannot produce the garage-beside-bedroom fatal (a composed garage has exactly one interior neighbour, a mudroom), and a guard test asserts the hand-authored spec Colonial still trips that fatal so the acceptance cannot pass because the rule broke. One unsatisfiable daylight finding left standing on purpose and recorded as OQ 31. See `docs/reports/wp-4.3-the-garage.md`.

**Depends on:** WP-4.2 in progress. **Size:** small but consequential.

**Tasks.** Author `garage_strategy` on every contemporary buildable variant from the dependency-and-hyphen rule (hyphen 12–20 ft, ridge 60–80%, doors off the street elevation) and the style's own massing expansion logic; `forbidden` on the street elevation for the styles whose composition cannot absorb it. Add a `garage` room and `garage-and-hyphen` grouping to the catalogs if not present, with `attaches_to` for the relevant massings. Give the composer a rule that the garage is placed by the grouping's `attaches_to`, never by adjacency.

**Acceptance.** The spec Colonial's garage-beside-primary-bedroom fatal cannot be reproduced by the composer; every contemporary variant has a specified strategy.

### WP-4.4 Images from HABS

**Status: BLOCKED BY THE ENVIRONMENT, 24 Aug 2026 — the harvester is written and queued.** All 322 asset records are still `wanted` and none can be sourced from here: this container's network policy denies the Library of Congress at the proxy.

```
curl https://www.loc.gov/pictures/collection/hh/?fo=json
curl: (56) CONNECT tunnel failed, response 403
gateway answered 403 to CONNECT (policy denial or upstream failure)  host www.loc.gov:443
```

`archive.org` is denied identically, so neither the HABS collection nor a scan mirror is reachable. **What would unblock it:** an environment whose network policy permits `www.loc.gov` (and `tile.loc.gov` for the image derivatives, if files are ever to be carried rather than cited).

`build/harvest_habs.py` is committed against that day. It searches the loc.gov HABS collection for the building each record names, and writes back the provenance a `sourced` record needs. **It has never been run against the live API** and says so in its own docstring — the request shape is written from the API's documented behaviour and every field is parsed defensively. `--dry-run` is the DEFAULT and prints the URLs it would request without touching the network or the corpus; `--write` refuses without `--live`.

Two things it will not do, both deliberate. It never sets `status: approved`, because the asset schema defines that as a human having looked at the image. And it refuses to `--write` while any selected record would be searched on its style name alone — **found by running the dry run**, which showed the first four records all producing `?q=english+georgian` because none carries a `provenance.building`. Sourcing those automatically would give one photograph cited by many records, which is worse than none. **Giving the 322 records their building names is real work that does not need the network, and is the right next step on this package.**

**Depends on:** nothing (can run any time). **Size:** medium, repetitive.

**Tasks.** For the `correct` half of each good/bad pair and for every `exemplar` with a HABS number, locate the HABS/HAER sheet or photograph on the Library of Congress site, record `provenance.habs_number`, URL, and `license: public-domain`, and move the record from `wanted` to `sourced`. Do not download into the repo; the manifest points. Generate the `diagram` and `measured detail` records from the proportion engine (SVG, `generated_from` recorded) — these need no sourcing. For the `incorrect` half, write a shot spec good enough for a photographer and leave `wanted`.

**Acceptance.** ≥ 100 records `sourced` or `generated`; zero records with `license: unknown`; `docs/assets.md` counts updated.

### WP-4.5 Rooms, groupings and partis to full coverage

**Status: COMPLETE (24 Aug 2026) on the parti criterion; the `style_variation` clause declared met at the corpus's own bar and out of scope at the literal one.** Partis 12 -> 21, native styles **39 -> 129 of 132**, nodes with a canonical massing and no native parti **90 -> 0**. Nine new diagrams (courtyard-and-portal, living-hall-picturesque, great-hall-h-plan, connected-farmstead, single-cell-hall, tower-villa, shotgun-linear, dogtrot-open-passage, octagon-radial) plus 36 style-list placements into diagrams that already existed. Two rooms authored (`courtyard`, `overlook`), eleven others deliberately not — `hall` already carries the great hall and the living hall, `cross-passage` the screens passage. `build/check_partis.py` added as a 22nd check, because nothing validated this catalogue at all.

Three of the package's named dozen were skipped on the data and are named rather than dropped: `telescope` (canonical for no style — 0 unblocked), `split-level` (0 unblocked, and needs the schema decision now recorded as OQ 34), `foursquare side hall` (<=1, and `foursquare-quadrant` is already `circulation_parti: "side-hall"`).

Four composer bugs found by running the diagrams rather than reading them: pick order was decided by filesystem order; massing affinity ignored `alternate_massings`; half the kits that state a ceiling height were never read; and the 3-bay floor *dropped* a one-room house rather than inflating it. And the finding that mattered most — nativity was worth `fit * 6` against 8 per serious finding, so a borrowed diagram routinely beat a native one, which adding nine partis turned into a Tidewater Georgian brief recommending an octagon. `NATIVITY_W` is now 20. See `docs/reports/wp-4.5-partis-to-full-coverage.md`; OQ 33, 34, 35 raised.

**Depends on:** WP-2.1 (for the missing-room list). **Size:** medium.

**Tasks.** Add the rooms WP-2.1 found missing. Complete `style_variation` for every room across every buildable style that contains it (name, trim grade, position, or `absent`). Add partis so that every style with a `canonical` massing has at least one native parti (currently 39 of 132 are named) — likely a dozen more: telescope, connected farmstead, hall-house, courtyard, gallery-and-cabinet Creole variants, split-level Ranch, Foursquare with side hall, Shingle-style living hall. Add groupings the partis need. Run `check_rooms.py` and the composer on a brief per new parti.

### WP-4.6 Missing proportion packs

**Status: IN PROGRESS, 11 of ~30 packs, 25 Aug 2026. All six packs this work package's own task text names as likely candidates are built, plus the largest item the remaining list held when it was measured.** Chosen by measured leverage rather than by the order of the list; the measurement and what remains are in `docs/reports/wp-4.6-missing-proportion-packs.md`.

*First tranche, 24 Aug.* `proportions/orders/moorish-arch.json` — OQ 30's item, the most-corroborated gap WP-4.1 found and the only one that unblocked a node with no binding at all; `moorish-andalusian` and `mudejar` come off `DELIBERATELY_UNBOUND`, which is now one node rather than three. `proportions/orders/greek-doric.json` — the gap WP-4.1 had already recorded as a WRONG binding rather than a missing one, `greek-classical` having been bound to `benjamin-doric` under a note calling it "the least-bad available approximation"; Benjamin is demoted and kept, because American Greek Revival buildings really were built from those plates. Raised on the way: **OQ 46**, the ontology has no arch slot — since built, at ontology 0.6.0.

*Second tranche, 25 Aug.* `proportions/modules/adobe-module.json` — the gap **four style nodes had already written down in their own binding notes** before anyone went looking, confirmed by three WP-4.1 batches besides. The module is one adobe laid as a header, so wall thickness comes in whole bricks; the bracing length (≈10× thickness, ≈24 ft) is what makes an adobe plan a chain of ranges, the exact analogue of the log pen's sixteen feet; and the slenderness limit turns out to be a **ceiling and not a generator**, carried as an 8–10 band because 14.7.4 NMAC says ten and `california-mission-colonial`'s own record says eight and both are right. Bound to 9 nodes, and five stale "missing from the corpus" sentences superseded in place. `proportions/systems/opening-pointed.json` — the **opening half** of WP-4.1's "Gothic Revival facade and opening system", built as the strike ratio (radius ÷ span) that is Rickman's arch families in one number. The facade half was **measured before it was built and mostly does not exist**: all four revival nodes already carry `facade-picturesque` and it fits them. It is real for exactly one node, `english-gothic`, which is the medieval building rather than a revival of it — and that turns out to be the same missing pack as the candidate list's pre-Palladian English facade item, seen from the other side. `rural-gothic-villa`, which PB-7a left with **no opening-role pack at all**, has one. `proportions/systems/opening-craftsman.json` — the opening half of PB-4's item, where the measured gap turned out to be **seven** nodes rather than the five the list estimated. Its central assertion is that there is no proportion: one horizontal line at 6 ft 8 in, and every opening on the elevation dies into it, so an opening's height is the datum minus its sill. The module is the framing bay, which `craftsman` names from the structure and `prairie-school` from the opening as the same 24 in. Two nodes were **refused** for stated reasons rather than bound to close a count — `mission-revival`, whose openings are arched, and `arts-and-crafts-british`, whose own governing logic says "there is no repeating bay and no vertical alignment requirement", which denies this pack's central rule outright. Nodes with no opening-role pack: 68 → 60. `proportions/systems/trim-prairie.json` closes the other half of PB-4's item and is the third gap in this package that the corpus had already written into a binding note of its own -- `prairie-school`'s `trim-craftsman` entry said in terms that "no pack here owns a first-principles, non-catalog Prairie interior system, and none should be invented for one", and this one answers the caution by measuring rather than inventing. It shares `trim-craftsman`'s module deliberately, because both families are built from the same 1x4 out of the same mill and the difference is entirely in what the board does -- a casing leg framing an opening against a band crossing a surface; the two packs' invariants state the opposition directly. It binds ONE node and moves no count, which the pack and the report both say plainly: it exists because a wrong binding is worse than a missing one, the argument that justified `greek-doric`. `trim-craftsman` is kept rather than struck, because the plan-book Prairie box really was trimmed from the same catalogue sections as the bungalow next door.

*Third tranche, 25 Aug.* `proportions/modules/dutch-gambrel.json` -- WP-4.1's Dutch gambrel item, scoped at 3 nodes and reaching 6. It carries TWO devices, because the records show they are independent: `hudson-valley-dutch` has a sprung eave over a straight gable and no gambrel, so it is bound for the eave rules alone. Its central finding is a datum nobody stated -- three style records give the break point and NONE says from where, two as a percentage of the half-span and one as a percentage of roof height, and read naively as from-the-eave the first is wrong by nearly a factor of two. Reconciled against the slope bands the same records give, the colonial figure only works measured from the RIDGE; the pack states one canonical datum with the conversions written out, and the style records are left as they are because the ambiguity is theirs and the pack is where it gets resolved once. The test recomputes that reconciliation rather than asserting the pack's prose. `proportions/modules/balcony-gallery.json` closes the DIMENSIONAL half of the cast-iron item, and the measurement disagreed with the item's own name: the corpus's three most iron-heavy records are `monterey-revival`, `monterey-colonial` and `regency`, and the Monterey balcony is WOOD. What they share with the Creole galerie and the Italianate porch is a horizontal deck applied to a wall, so the pack is named for the deck and iron is one material it is made in. Its central claim is that DEPTH FOLLOWS CARRYING STRATEGY -- brackets 30-48 in, cantilevered joists 5-8 ft, posts to grade 6-14 ft -- and `monterey-colonial`'s own 'one-fifth to one-quarter of the building depth' turns out to be the cantilever-to-backspan limit found by feel. The ORNAMENT half of the item stays open: the anthemion, lyre, heart and trellis patterns, the New Orleans foliate panels and PB-6a's wrought grilles are a pattern repertoire and not a proportional system, left on the candidate list on the same principle that kept muqarnas out of `moorish-arch`.

With the six named candidates done, the rest of WP-4.1's list was MEASURED rather than worked in order, and stone coursing was the largest item by a wide margin: 60 buildable nodes describe stone walling and 34 carried three packs or fewer, against 31 and 23 for the next-largest (the half-timber panel). `proportions/modules/stone-course.json` is that pack. It cannot use `brick-course`'s module -- a brick wall has a gauge rod and a rubble wall has no gauge at all -- so the module is a course of the DRESSING, the only stone with a dimension before it is laid. Its central rule is stated twice by the corpus independently and in nearly the same words, `cotswold-vernacular` and `norman-romanesque-english` both saying ashlar is RESERVED for quoins, jambs, lintels and the rest. It is bound to 12 of the 34 on a stated criterion -- whether the stone wall governs or merely occurs -- with the Iberian nodes left to `adobe-module`, the ashlar Georgian fronts to their orders, and the timber-framed nodes to the half-timber panel module still on the list. Nodes carrying two packs or fewer: 36 to 28. Next by the same measurement: the half-timber panel, then a gable geometry system, which the list records as entirely missing.

*Fourth tranche, 25 Aug.* `proportions/systems/facade-arcade.json`, WHICH THE CANDIDATE LIST NEVER CONTAINED. Three packs in this work package asked for it anyway, two of them under the mistaken impression it was already listed. Measured it was the largest remaining item at 33 nodes and 24 thinly bound, and it is the only pack in the package claiming `confidence: high` -- nine unrelated records give its pier-to-span ratio as one third to one half, five countries and six centuries apart. The arch's SHAPE is deliberately not in it, which is what lets it compose with `moorish-arch` and `opening-pointed`. First movement in the facade-role count: 67 to 61.

`proportions/modules/timber-panel.json` is WP-4.1's half-timber panel item, and the list's own phrase 'distinct from `timber-bay`' did more work than it looks: six of the sixteen rules planned for it were already that pack's, and it is bound to seven of the same nodes. So this pack restates none of them and holds only what FILLS the frame. Its central rule is REGIONAL rather than universal -- the panel proportion runs 1:1 German, 1.2 English south-east, 1:3 to 1:4 East Anglian and Norman close studding, and `english-medieval-timber-frame` holds two of those in one sentence -- so there is no correct value, only a correct value for a place. Two nodes refuse themselves in their own words ('no half-timbering', 'without applied half-timbering'). It raised **OQ 47**: the ontology has no slot for an exposed structural member on a wall face, so four rules route through `corner_board`, and four packs in this package have now done the same thing.

Two defects its own tests found, both introduced by this package. A SILENT SLOT-ADDRESS COLLISION: `facade-arcade` and `moorish-arch` were both writing to `porch_support`/`height` meaning different quantities -- the impost block's height against the springing line above the floor -- on three nodes that bind both. Two packs putting different quantities into one address is a corruption rather than a conflict, because whichever resolves last wins and nothing reports it, and precedence cannot help. And PRECEDENCE CONTRADICTING ROLE sixteen times across fourteen nodes, twelve of them mine, because every new binding was inserted at the first unused precedence and 0 is nearly always free; `check_pack_bindings.py` checked precedence for being a total order and never for agreeing with role. Both fixed, and the checker now errors on the narrow rule -- measured, `secondary` ahead of a role pack is the corpus's own convention in 253 places across 59 nodes, so only 'nothing outranks a primary' is enforced and the rest is warned.

Two findings worth carrying forward. **A checker defect:** `check_orders.py` addressed assembly members by `id` and `check_modules.py` did not, so the same invariant expression was legal in an order pack and a `NameError` in a module pack — fixed, and pinned. **An overstated conflict, caught by computing it:** `opening-pointed`'s first draft said the pointed head fails IRC R310. It does not; the **mullion** does. A 36 in equilateral head still leaves about 10 sq ft of clear rectangle, and two lights leave ~13 in clear each against a 20 in minimum. The test now recomputes both figures rather than asserting the sentence.

**Depends on:** WP-4.1's list. **Size:** medium per pack.

**Tasks.** Author the packs WP-4.1 found missing, in the pack schema, as functions with invariants and conflicts. Likely candidates: Greek Doric (Stuart & Revett / Lafever) as a standalone order; a Gothic Revival facade and opening system; a Craftsman opening system and a Prairie trim family; adobe and rammed-earth module; a Dutch gambrel roof system; a cast-iron/ironwork system for Italianate and New Orleans. Each with `selftest` coverage and `check_orders`/`check_systems` green.

### WP-4.7 Non-Western trunks (defer; scope only)

**Status: NOT STARTED — scope only, by design.**

Write the scoping note: which traditions, which families, what the first style in each would be, and confirm from two trial nodes (a Japanese minka, a Yoruba compound house) that the schema extends unchanged. Name the `shotgun-house` and `cape-dutch` ancestors. Do not fill beyond the trial nodes.

---

## Phase 5 — Platform

*Goal: the IR leaves the system in forms builders, drafters and plan-development leads can use.*

### WP-5.1 Export: DXF and IFC

**Depends on:** WP-3.1. **Size:** medium.

Emit DXF (ezdxf) plan, elevation, section and roof plan with layers per element group, and an IFC (ifcopenshell) model with walls, slabs, openings, roof and spaces carrying the TDL ids as property sets. Round-trip test: DXF → plan record → validator gives the same findings.

### WP-5.2 The plan workbench

**Depends on:** WP-1.2; better after WP-2.2. **Size:** large.

A self-contained HTML tool in `dist/` in the manner of `orders.html`: load or sketch a plan record, see findings by layer inline on the drawing, drag a wall on the bay grid and re-score, switch style and watch constraints change, request N candidates from the composer (via the MCP server or a Python port). This is the interface a plan-development lead works in; its absence is a gap in the collaboration, not just the software.

### WP-5.3 Generated guidelines, details and modelling conventions

**Depends on:** Phase 3. **Size:** medium.

Three documents the brief asks for, all generated from data so they cannot drift: a **design guidelines** book per style (constraints, forbidden variants, faults with exceptions, pack bindings, rendered orders and details); a **standard details library** (every `measured detail` asset rendered by the engine, every pack conflict with its ranked substitutions, the `cheap` fix for every fault); and a **modelling conventions** note (how a drafter models against TDL ids in CAD/BIM, layer naming, the bay grid, which dimensions are clear and which are structural). `build/gen_guidelines.py` emits HTML and PDF per style.

### WP-5.4 Cost layer (defer until the plan-development partnership exists)

Scope only: unit costs by construction type and region; the 32 `cost_negative` faults as savings; candidate comparison by cost per square foot. Do not author costs without a partner's numbers.

### WP-5.5 Drawing-to-record ingestion

**Depends on:** WP-2.1 experience. **Size:** medium.

A structured transcription form (HTML) that produces a plan record from a drawing by tracing, and a DXF importer that reads a drafter's plan into a record. This is what lets HABS drawings, the reference corpus, and a builder's back catalogue flow into the critic.

---

## 6. Parallelisation map

```
Phase 0:  WP-0.1 ──► WP-0.2
                 └──► WP-0.3
Phase 1:  WP-1.1 (schema owner + N family batches) ──► WP-1.2
          WP-1.3 (independent; needs rulings)
Phase 2:  WP-2.1 (start with Phase 1, in parallel)
          WP-1.2 + WP-2.1 ──► WP-2.2 ──► WP-2.3
          WP-1.2 ──► WP-2.4
Phase 3:  WP-2.2 + WP-1.3 ──► WP-3.1 ──► WP-3.2
                                     └──► WP-3.3 ──► (feeds 3.2)
Phase 4:  Phase 1 ──► WP-4.1 (27 family batches) ──► WP-4.6
          Phase 1 + WP-1.3 ──► WP-4.2 (27 family batches) ──► WP-4.3
          WP-4.4 any time;  WP-2.1 ──► WP-4.5;  WP-4.7 scope only
Phase 5:  WP-3.1 ──► WP-5.1;  WP-1.2 ──► WP-5.2;  Phase 3 ──► WP-5.3;  WP-5.5 after WP-2.1
```

Agent-count guidance: Phase 0 is one agent, sequential. Phase 1 is one schema owner plus up to nine batch agents (three families each). Phase 2 is one agent per package, sequential within the phase. Phase 3 is one agent per package. Phase 4 is where parallelism pays: one agent per family for 4.1 and 4.2, run in waves of five to nine so the schema owner can merge and the cascade test can be run between waves. Phase 5 is one agent per package.

---

## 7. What "finished" looks like

A brief — 3,200 sf, four bedrooms, Tidewater Georgian, a 120 ft lot facing south, two cars — goes in. The system resolves the kit at the declared date, selects the native partis the lot can hold, composes four candidates whose entrance is on the south front and whose service is to the rear, places them on the bay grid with walls and a section, raises a five-bay front composed to Gibbs with the sash lights correct for 1760 and one head datum per storey, puts the garage in a hyphened dependency with its ridge at 70%, runs 209 faults and 441 hard constraints against the result and reports every one as present, clear, or unjudged, and exports a DXF a drafter can open — with a decision log of every assumption and a list of the judgment calls that belong to the architect. That last list is not a limitation. It is the system knowing the difference between grammar and poetry, and leaving the poetry to the person.
