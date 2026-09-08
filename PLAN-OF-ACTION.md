# Traditional Design Language — Plan of Action

*Companion to `STATE-OF-THE-PROJECT.md` (revised 25 August 2026 and since kept current). That document says where the project stands; this one says how to finish it. It is written to be cut up and handed to Claude agents one work package at a time. Each package is self-contained: what to read, what to build, what "done" means, and what not to touch.*

---

## Progress board — as of 3 September 2026

Every package below carries a **Status** line. This is the summary. Original package text is left as written even where the work has since been done, so the record of what was asked for stays legible next to what was delivered; where the delivered result diverged from the acceptance text, the Status line says so rather than quietly restating the goal.

| Phase | Packages | State |
|---|---|---|
| **0 — Consolidation** | WP-0.1, 0.2, 0.3 | **Complete** |
| **1 — Executable constraints** | WP-1.1, 1.2, 1.3 | **Complete** — 660/660 constraints migrated, 61.5% of hard constraints tested (bar was ≥60%) |
| **2 — Composition** | WP-2.1, 2.2, 2.3, 2.4 | **Complete** — placement is CP-SAT with named conflict sets (25 Aug); the hill-climb remains as fallback, cross-check and the workbench's per-gesture engine |
| **3 — The elevation** | WP-3.1, 3.2, 3.3 | **Complete** — WP-3.2 evaluates 83 of a named 100 faults, disclosed |
| **4 — Breadth** | WP-4.1, 4.2, 4.3, 4.5, 4.6 complete · **4.4 environment-blocked, 4.7 not started** | **In progress** |
| **5 — Platform** | WP-5.1, 5.2, 5.5, 5.6, 5.7 complete · **5.3, 5.4 not started** | **In progress** — the workbench is live in `workbench/`, DXF/IFC export ships with a proven round-trip, and drawings ingest through the Transcription surface; guidelines (5.3, waiting on Phase 4 breadth by choice) and the deferred cost layer remain |
| **7 — The three open questions, then their remaining halves** | WP-7.1, 7.2, 7.3, **7.4**, **7.5** | **Complete (27 Aug 2026)** — OQ 95, OQ 92 and OQ 91 (issued as 76, 73 and 72; see the register's 28 August conversion table), each ruled by Lucas and each half-closed with the half that could not be done named; **WP-7.4 then took the halves that were left**. The generator is level-aware and fixed BEARING not stacking (transfer beams 166 → 109), and WP-7.4 charged the stacking directly in both engines; furniture sizing is REFUSED and arrangement goes as far as the rooms' own words, which turned out to be five wall runs rather than the one the register published; a window's ROLE is the plan's to decide and its SASH KIND the style's, with 119 of 159 styles answering through the lineage and the kit vocabulary now merged and ratcheted. **WP-7.4 also found that `span_check` had never read the bearing flag it was handed** — every partition counted as a support, so the corpus under-reported its own structural defects by half. **WP-7.5 is the adversarial audit of WP-7.4** and found two blocking defects it had introduced, one of them a false claim in its own commit message ("the three tests replacing it" — three were added and the nondeterministic one was never removed), plus the same span bug a second time in `render_section.py`; six tests that passed with the fix reverted were made to bite, and OQ 98 was raised for what the audit deliberately did not fix |
| **8 — Keeping the record honest** | **WP-8.1** | **Complete (28 Aug 2026)** — the open-question register has collided across parallel sessions four times in four days, and every renumbering pass after one has used a regex that CANNOT SEE THE SECOND NUMBER IN A LIST: `OQ 82 and 84` renumbers the 82 and leaves the 84, and because the stale id still names a REAL entry nothing dangles and no existence check fires. Three live instances were on main and **one of them was written by a different session on a different branch**, which is what makes it a class. Fixed, the 22 bare-continuation lists normalised so every cited id carries its own prefix, and `build/check_citations.py` added to `check_all` (37 checks) to hold it there. It fixes the AFTERMATH of a collision and deliberately not the cause; the cause is **OQ 99**, which was raised by reading the highest id in this working copy and says so. **OQ 99 was then ruled and executed in the same package**: the numbers are FROZEN AT 99 and every new question is NAMED (`### oq/<slug>`), because a sequential id has to be issued from somewhere and the only shared state two parallel sessions have is the repo they both branched from. A slug is derived from the subject rather than issued, so two sessions picking one have raised the same question and the conflict is the one you want. Check D refuses a numbered entry above the ceiling, so the old mechanism is unavailable rather than discouraged. The legacy numbers are deliberately NOT migrated: nothing parses an OQ id, so a renumber was possible and pointless -- commit messages carry the old numbers and cannot be rewritten, so a uniform scheme was never available. Successor question, and the first under the new scheme: `oq/two-id-namespaces`. Report: `docs/reports/wp-8.1-the-citation-guard.md` |
| **6 — Plan semantics** | WP-6.1, 6.2, 6.3, **6.4 (the audit)** | **Complete (27 Aug 2026)** — raised by Lucas, not by the plan: the rendered sheets were "colorless green ideas sleeping furiously", every part well-formed and the whole meaningless. A door had no wall, no position and no rank; the renderers invented what the record could not say and dropped what it could; nothing checked that you could walk from the front door to a room |
| **8 — The register, the backlog and the scopes nothing reads** | **WP-8.1**, **8.2**, **8.3**, **8.4**, **8.6**, **8.7**, **8.8**, **8.9**, **8.10**, **8.11** *(no 8.5 — see the note in CLAUDE.md; it shipped as `6f9e7c7` before the numbering existed)* | **8.1-8.4, 8.6 complete (28 Aug 2026); 8.7-8.11 complete (2-3 Sep)** — **WP-8.8** made the baked-snapshot class knowable (135 judged, 0 stale, 8 unjudgeable for want of a recorded binding) and found the evaluator the question asked for had existed in two places all along. **WP-8.9** measured OQ 51's flip before building it and found the ruling had been taken on `unendorsed` — a count of ROLE GAPS — where the thing a gate stops is DELIVERIES: 2,899 slots, not ~223, a factor of thirteen. Put back with the numbers, Lucas ruled *stage it pack by pack* and *a separate field*; the `--stranding` meter and the `delivery: opt-in` / `inherits_packs` mechanism shipped inert. **WP-8.10** landed the first flip and built the loudness the ruling required: `trim-classical` is opt-in, six vouched nodes admit it, 10 slots over 10 nodes are stranded, and every stranded slot in the corpus (2,889 of 2,889) now NAMES the pack withheld and why. It found the meter's gate and the mechanism's gate were different predicates (10 against 15, one of the five a shipped reference plan), that `measure()` could not see a flip at all, and that the flip was sold on a corpus-level writer count that described no node — the same wrong-grain error as WP-8.9's, one package later. — **WP-8.1, WP-8.2 and WP-8.3 are COMPLETE**: the open-question register is a DIRECTORY, one file per question, because a single shared file is where two parallel sessions' answers to "what is the next id" both survive a merge — four times in four days, and nothing in the corpus checked for a duplicate id at all. `check_ids.py`, a generated index, a CI gate that fires before the merge rather than after it, and §1 amended so open questions and work packages are ids like every other. **OQ 90 closed on the way**: this branch's chain moved 5.7→5.11, 5.8→5.12, 5.9→5.13, 5.10→5.14 and main's atlas kept 5.7 — 53 of WP-5.7's 87 references moved, each attributed by `git blame` rather than by `sed`. **WP-8.2** built OQ 51's refusal half (`declined_packs`), refused the per-edge deny on measurement, and found the meter wrong by 27 in the flattering direction — 222 unendorsed was really 249 and 71 endorsed really 38. Ten declines moved `unendorsed` by zero, which is why `judged` is now a floor. It raised **`oq/forbidden-stops-the-pack-cascade`**: 787 pack rules dimensioning a slot the kit forbids, not one of them chosen by a human. **WP-8.3** made `forbidden` stop the pack cascade too (`oq/forbidden-stops-the-pack-cascade`) and found that `elevation.py` reaches packs by `PE.resolve` and never through the resolver — a second path nothing had named, 46 pairs, 16 refused and 24 disclosed. **WP-8.4** read the exception preconditions -- 331 records, 123 naming a construction, and not one line of code had ever consulted any of them. `granted_when` (renamed from a second `applies_when` in the same schema), a closed 61-token construction vocabulary over variant ids that already exist, three verdicts with the unjudged case judged BOTH WAYS and reported unjudged only where the two rules disagree. It also collided head-on with main, which had shipped its own OQ 88 scope, its own OQ 99 and its own WP-8.1: **ruled -- main's `scope` field survives and this vocabulary is ported into it**, after measuring that main's substring classifier over the cladding disagreed with each node's own `construction_type` on 13 of 164 styles, `cape-dutch` among them, which is OQ 88's own bug surviving inside OQ 88's fix. OQ 86 closed (`kit_vs_pack` read the node's own file, 62 -> 1,231), OQ 90 closed at its third option (a WP number is a label; cite the report), and OQ 89's remainder swept up: `elevation.py` read `shutter` and `window_head_masonry` off the RAW kit under a comment naming `shutter` as needing the cascade. Report: `docs/reports/wp-8.4-the-exception-precondition.md` · new questions: `oq/applies-when-means-two-things`, `oq/a-baked-pack-value-is-a-second-delivery-path` |
| **9 — Arrangement** | **WP-9.1, 9.5, 9.6, 9.7** complete · **9.2 text half done, image half waiting on Lucas's download** · **9.3 part built** · **9.4 COMPLETE AND ITS OWN PREMISE REFUSED** (`docs/reports/wp-9.4-the-unit-was-not-the-problem.md` — cite the FILENAME, two WP-9.4s exist) | **In progress (1 Sep 2026; this row was corrected on 3 Sep, having said "9.2, 9.3, 9.4, 9.5 not started" while four of those five had moved and two more packages had shipped with no section of their own — see `docs/reports/project-review-2026-09-03.md` §VII. The 9.4 cell in that same correction still said NOT STARTED and was itself wrong — the package had run on 1 Sep and refused `parti_slice` with its measurement, a probe taking fatals 3 to 8. Corrected again hours later; see that review's §IX, which is about this exact line)** — raised by Lucas against a rendered sheet, and the founding failure mode one level above Phase 6: a 10 x 30 ft kitchen, a portico off the axis of its passage, a dining room landlocked mid-house. The corpus already stated every band the sheet broke and **twenty-seven of the twenty-eight plan-measurable faults came back UNJUDGED** because nothing had ever supplied a plan-arrangement variable. **WP-9.1 is the arbiter and only the arbiter** — no solver, no renderer, both reference plans byte-identical — because seven of the solver's eight arrangement score terms had no critic counterpart at all, against `plan_check.py`'s own stated principle that the search charges preferences and the critic is the arbiter. Six of Lucas's seven complaints are named; the seventh (the passage) the corpus declines to call a fault, which is stated rather than invented around. A plant-room zero was built, convicted BOTH reference plans and was withdrawn; the first shape check convicted the GOOD plans and lost the direction the corpus does not state. Report: `docs/reports/wp-9.1-the-arbiter-for-arrangement.md` · new question: `oq/a-daily-route-is-an-editorial-model` |
| **10 — The second massing element** | **WP-10.1** | **Complete, and two of its three packages withdrawn by its own audit (3 Sep 2026)** — OQ 40 ruled a dependency a second massing element and the machinery ships and is DORMANT: the block placer, `exterior_score(bounds=)`, plan schema 0.5.0, both reference plans byte-identical. The service strip and the hyphen-as-a-room were WITHDRAWN when the audit found eight blocking defects, five of which reduce to **six layers below the placer reading the main block as the whole building** — a garage window drawn 14 ft from the garage, a span manufactured across the hyphen gap, a house reporting `lot_capped: true` at 34 ft wider than its lot. CP-SAT refuses a multi-element plan rather than flattening it (which had also flattered a number this session published); `geometry_report.multi_element` discloses the six. Report: `docs/reports/wp-10.1-the-audit-of-the-dependency.md` · new question: `oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it` |
| **11 — The drawn sheet** | **WP-11.1 … WP-11.8** · the rest planned | **WP-11.1 complete (4 Sep 2026)** — raised by Lucas against a rendered sheet set beside four exemplar plans, and diagnosed before he said what was wrong. The finding that organises it: **the instrument already owned a written graphic standard and the plan sheet did not obey it** — `tokens.css` has carried Graphic Standard No. 1 verbatim since WP-5.2 while `render_plan.py` drew in a dark instrument palette that `svg_theme.py` translated on the way to the browser, so the sheet had the standard's COLOURS and none of its GRAMMAR. `build/sheet_style.py` is the one spelling (52 hex literals in the four renderers → 0, all ten sheets byte-identical across the move); the wall is a BODY at the three thicknesses `structure.wall_thickness` has computed since WP-3.1 and no drawing had ever read, so the sheet now says which walls CARRY; an opening is a hole cut from `derive_openings`' own spans; the room washes are gone and the paper is the room; and the six banner lines are a margin schedule below a ruled border. **Two registers, ruled by Lucas 4 Sep**: `presentation` for a reader, `working` for the marks, one renderer, the plate saying which. **Three existing guards had selectors this package retired and all three would have passed vacuously**, and widening the fourth opened a hole a mutation found — `LIGHT` vouched for itself. Reports: `docs/reports/wp-11.1-the-sheet-in-its-own-standard.md` and `docs/reports/wp-11.2-the-pen-ladder-and-the-wall-the-record-states.md` · new question: `oq/the-placement-carries-no-wall-bands`. **WP-11.2** put the workbench's own sheet on the same ladder (19 inline stroke widths → 0) and gave both renderers ONE wall to read — `footprint.wall`, plan schema 0.5.1, from `build/assemblies.py`, a leaf on `storeys.py`'s precedent. **The browser walk ran for the first time in a session on this branch** and caught a defect 81 unit tests and a clean build both missed |

**Revised order for the remaining work** (supersedes the recommended order in Section 0, which assumed nothing had been built):

1. ~~**OQ 28**~~ — **done 24 Aug 2026**: `build/modcache.py`. `check()` 3.06 s → 0.31 s, `compose()` 30-40 s → 7-9 s, the suite back to one run at 2 min 24 s. See `docs/reports/oq-28-module-cache.md`.
2. ~~**WP-4.3**~~ — **done 24 Aug 2026**. See `docs/reports/wp-4.3-the-garage.md`.
3. ~~**WP-2.3**~~ — **done 25 Aug 2026**, closing Phase 2. `build/geometry_cp.py`. See `docs/reports/wp-2.3-the-real-solver.md`. (Two sessions built this package independently; the CP engine dispatched from `geometry.solve()` is the one that survived the 25 Aug merge.)
4. ~~**WP-4.5**~~ — **done 24 Aug 2026**: 21 partis, 129 of 132 styles native, 0 uncovered. See `docs/reports/wp-4.5-partis-to-full-coverage.md`.
5. ~~**The open-question pass**~~ — **done 24 Aug 2026**. Every question Lucas had ruled on is
   executed: OQ 12, OQ 13, OQ 14, OQ 26, OQ 27, OQ 29, OQ 31, OQ 32, OQ 33, OQ 34, OQ 35, OQ 36, and 15, 18, 19, 37, 38, 39
   besides. Reports: `docs/reports/oq-55-reserved-voids.md` and
   `docs/reports/oq-59-partis-that-fail-their-own-style.md`. The two that changed the compiler
   rather than the corpus are **OQ 55** (courtyards are placed, and the heuristic gained a
   stated ring layout because it cannot search for one) and **OQ 59** (`check_partis.py` check
   10 — five of twenty-one partis were carrying fatal findings against the styles they were
   written for, so the composer would not recommend them; 21 of 21 compose now).
6. **WP-4.6 — COMPLETE, twenty-one packs, 25 Aug 2026.** `moorish-arch` (OQ 30's item,
   and the only gap that unblocked a node with no binding at all — `DELIBERATELY_UNBOUND` is down
   from three nodes to one), `greek-doric` (which replaced a binding WP-4.1's own note called
   "the least-bad available approximation"), `adobe-module` (the gap four style nodes had already
   written down in their own binding notes; bound to 9), `opening-pointed` (the opening half of the
   Gothic item — the facade half was measured and found already served), and `opening-craftsman`
   with `trim-prairie`, which are both halves of PB-4's item, `dutch-gambrel`, `balcony-gallery`, `stone-course`, `facade-arcade`, `timber-panel`, `opening-mullioned`, `facade-gable`, `trim-sawn`, `octagon-geometry`, `facade-pavilion`, `jetty-overhang`, `facade-portada`, `facade-peristyle`, `corbel-course` and `facade-medieval-english`. **All six packs this work package's own task
   text names as likely candidates are built, plus the largest item the rest of the list held when it
   was measured.** 132 of 132 nodes bound (OQ 49's slot-scoped binding closed the last); nodes with
   **no opening-role pack 68 → 50** and **no facade-role pack 67 → 46** (the board previously carried the mid-package 56), which is where the
   movement now is, plus one wrong interior binding corrected, which moves no count at all. The
   remaining list, with each item's measured leverage, is in
   `docs/reports/wp-4.6-missing-proportion-packs.md`; next is the Iberian portada, the peripteral Greek-Roman system and Mudejar corbelling. The report now also
   names the items that are **not supportable from this corpus**, the Baroque curved wall first
   among them — no figure for an undulating elevation exists in any of the 22 matching nodes. Then **WP-4.4** (images), which is currently
   environment-blocked — see its own status block.
7. **Phase 5** — the last mile: WP-5.1, 5.2, 5.5, 5.6 and 5.7 are done; 5.3 and 5.4 remain.

**Three open questions want a ruling before or alongside WP-4.6** *(since closed — OQ 62, OQ 63 and OQ 42 all carry rulings as of 25 Aug 2026; kept as written for the record)*, all raised by the pass above
and none of them blocking: **OQ 62** (`area_weight` is read as a boolean and never as a share of
anything, so every parti's weights read as a considered distribution and are not one), **OQ 63**
(a fault's secondary tests are written for one style and run against every style — it is why
`cape-cod-colonial` cannot currently return a clean plan under any diagram), and **OQ 42**
(`types_present` is not aliased, so a plan that models a room under an equivalent name is told it
models none). **OQ 18** is open on purpose and needs sources rather than code.

WP-4.7 stays scope-only by design.

---

## 0. How to use this document

The work is organised into phases and work packages (WPs). *It said "six phases and twenty-two work packages" until 3 Sep 2026, against ten phase headings and more than forty packages; the sentence was written before Phases 6 through 9 existed and is corrected rather than struck, because nothing cites it.* Phases are ordered by dependency, not by effort. A WP inside a phase can usually run in parallel with its siblings; the dependency line on each package says when it cannot.

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

**Ids are stable and never reused.** Never rename a style, slot, room, grouping, parti, fault, pack, **open-question or work-package** id. If an id is wrong, add the right one and mark the old one `deprecated_in_favour_of`.

*The last two were missing from that list until 28 Aug 2026, and their absence is why four open-question blocks were renumbered in four days while nobody thought a rule was being broken. They are ids. They are cited from source, from tests, from commit messages that cannot be edited, and — for OQ 18 — from 197 places inside a single kit file. **No open-question id or work-package number may be renumbered again**, whatever a merge makes convenient. The four conversion tables in `docs/open-questions/README.md` are the record of what it cost.*

**Issuing an id: never by reading the working tree.** Every collision so far came from one habit — find the highest number, add one — which two parallel sessions perform identically and merge without conflict. **Open questions are a directory now**, `docs/open-questions/<nnn>-<slug>.md`, one file per question, exactly as `faults/`, `rooms/`, `partis/`, `proportions/` and `styles/` have always been: two sessions issuing id 99 create the same PATH, and git refuses to auto-resolve an add/add conflict instead of silently juxtaposing two entries under one number. `build/gen_open_questions.py` regenerates the `docs/open-questions.md` index; **edit the question's own file, never the index.** `build/check_ids.py` holds filename, heading and status to each other, and CI compares the branch's id set against its base before a pull request can merge.

**Where two branches did collide, the side that merged first keeps its numbers.** Applied four times before it was ever written down; written down now so it is a rule rather than a precedent. It is never the side still on a branch.

**Unjudged is not passed.** Any checker or validator you write must distinguish "evaluated and failed", "evaluated and passed", and "could not evaluate", and must never collapse the third into the second.

**Prose constraints stay.** When a constraint or rule is made executable, the human-readable `statement` is kept beside the `test`. The test is a formalisation of the statement, not a replacement.

**Sources or `kind: editorial`.** Every numeric parameter you author carries a `source` or is honestly marked `editorial`. Do not launder a guess as `measured`.

**Check suite green, then tests, then docs.** A package is not done until: the check suite is green; the behaviour tests (Phase 0) pass and new behaviour has a test; the relevant `docs/*.md` is updated; and the README counts are right. Doc drift was one of the findings of the review — do not add to it.

**Report format.** Finish every package with a short written report in `docs/reports/<wp-id>-<slug>.md` containing: what was built; what was found (the project's tradition is that the findings matter as much as the code — record them); what was deliberately not done; and any open question that needs Lucas's ruling, added as a NEW FILE in `docs/open-questions/<nnn>-<slug>.md`. **Do not edit `docs/open-questions.md`** — it is generated by `build/gen_open_questions.py`. **Do not take the next number by reading the working tree**: that habit collided four times in four days. Check the base branch (`git ls-tree origin/main -- docs/open-questions/`), take the next free id there, and let `build/check_ids.py` and the CI base-vs-head gate catch you if another session got there first.

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
- ~~**OQ 23, OQ 25**~~ — struck in WP-0.2.

**All ruled, 24 August 2026.** Every question that was blocking a package now has a decision recorded against it in `docs/open-questions.md`; nothing in the remaining plan waits on a judgment.

- **OQ 55 — the courtyard void.** Ruled: reserved voids. Both placement engines carry outdoor rooms as placed, dimensioned voids, excluded from the area budget and the envelope, drawn as open.
- **OQ 57 — vertical adjacency.** Ruled: adjacency rules may declare `relation: above` / `below`, and `plan_check.py` evaluates them across levels. Removes both of WP-4.5's workarounds.
- **OQ 12 and OQ 13 — the ontology changes ruled long ago and never executed.** Ruled: execute both, as ontology 0.6.0 — split `window_head` by trade, enforce the entablature cross-references.
- **OQ 58 — `hybridizes_with`.** Ruled: spend the schema change, a slot-scope allowlist on the edge.
- **OQ 54 — the heuristic's silent under-band placement.** Ruled: report it in `geometry_report`, do not make the heuristic refuse and do not teach `plan_check` to read `room.geometry`.
- **OQ 31 — the garage daylight rule.** Ruled: a `daylight.depth_governs: false` opt-out on the room record.
- **OQ 56 — no half-storey.** Ruled: add an optional `level_offset_ft` beside `level`, which keeps its meaning.
- **OQ 30 — the Islamic/Moorish pack.** Ruled: build it first in WP-4.6.
- **OQ 27 — untagged judgment constraints.** Ruled: tag with `blocked_by` during WP-4.6.
- **OQ 14 — three rail slots.** Ruled: keep the three, state the shared code conflict once. **OQ 26** folds into the same pass.
- **OQ 21 — variant `op` string matching.** Closed: the checker is enough.
- **OQ 29 — the three unbound nodes.** Confirmed; OQ 30's pack retires two of them.
- **OQ 3, OQ 4, OQ 5, OQ 6** — left as standing disclosures. They are recorded uncertainties about history, not defects in the model.

**Ruled 1 Sep 2026 (Phase 9):**

- **The revision loop's authority** (`oq/the-revision-loops-authority-over-topology`). Ruled: the reflection is a DETERMINISTIC loop — a move registry executing corpus rules, `plan_check` re-judging every round, no language model editing the record; it may change dimensions, declared choices, openings and optional rooms — add the door the grammar prescribes to reach a stranded room, drop a room the parti marks optional, split where a grouping says to — and never a room the parti has no place for, a judgment slot, geometry, a critic-suspect, or a measurement the record did not declare; and it runs BY DEFAULT on the returned candidates everywhere a product is made, with `--no-revise` to opt out.

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

**Depends on:** Phase 0. **Needs rulings:** OQ 12, OQ 13, OQ 16, OQ 17. **Size:** medium.

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

**Status: COMPLETE (25 Aug 2026).** `build/geometry_cp.py`: placement as CP-SAT over the bay grid, dispatched from `geometry.solve()` with the heuristic kept as fallback and cross-check per the package text (OR-Tools optional behind the WP-5.1 refusal pattern; `check_all` reports N/EV without it). Hard: no-overlap, containment, coverage, declared doors touch, the entry on its front, rooms at program size, declared exterior walls. Four rulings shaped it — the decisive one taken mid-package when hard wall pins proved both check plans *and* nearly every composed candidate infeasible, because `exterior_walls` is the corpus's idiom for exposure in the massed house (10 of 12 partis double-claim corners): protruding rooms, contested corners, and any pin-set the solver *proves* unable to co-hold downgrade to reach-at-least-one, every downgrade stated in `geometry_report.solver.refinements`; doors, sizes, entrance and capacity never downgrade. On infeasibility: a plain-language minimized conflict set AND the heuristic's least-bad drawing labelled on the sheet (the ruling) — the canonical refusal is the selftest's K5 door graph, non-planar, six door pairs named. The acceptance benchmark is disclosed as adapted: the CP placement must have zero hard-fact violations and beat best-of-800 *or* lose only to a heuristic winner that cheats on hard facts at 14 points apiece. The workbench re-scores with the heuristic per edit gesture (a proof takes seconds; the bench debounces at 400 ms) and gains a *prove placement (CP-SAT)* control with a conflict panel. Report: `docs/reports/wp-2.3-the-real-solver.md` · new open question: OQ 40 (the flat footprint vs declared wings).

**Merged 25 Aug 2026 from a second, independent WP-2.3.** Two sessions built this package in
parallel, against the same task text, without knowing of each other: `build/geometry_cp.py`
(above) and `build/solver.py`. The CP engine dispatched from `geometry.solve()` is the one that
survived, on Lucas's ruling — it is merged, twice audited, and already the default. The other is
deleted rather than kept beside it, so the corpus carries one CP-SAT formulation of one problem.
Three findings from the deleted branch are NOT rediscovered by the surviving one and are kept:
the heuristic silently places the spec Colonial's dining room 26% below its own band on every
seed (**OQ 54**, ruled, and `geometry_report.under_band` now reports it); a plan record's
`exterior_walls` are aspirations rather than rectangle edges, and cannot all be asserted (three
Tidewater ground rooms each declare *opposite* walls — the same idiom finding the surviving
engine reached independently and calls the exposure problem); and `check_all.py` was running the
suite under a different interpreter than its checkers, skipping all sixteen solver tests while
reporting success. Its formulation finding is also worth keeping, because it is a negative
result someone will otherwise re-derive: stating exact tiling arithmetically —
`sum(w*h) == W*H` over a dozen nonlinear products — could not be decided on the shipped spec
Colonial in 240 s with four workers *while holding a hint that was itself a valid tiling*.
Reading the slicing tree off a heuristic layout makes tiling structural rather than arithmetic
and leaves only the cut positions to solve.

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

**Depends on:** Phase 1, WP-1.3. **Needs rulings:** OQ 17, OQ 20. **Size:** very large, parallel by family.

**Tasks.** Fill kits top-down so the cascade pays: first the 27 family nodes (each specifying the slots the family genuinely shares — roof family, construction, trim family, plan logic), then the 90 styles (using `extends` against the family wherever the style adds rather than restates), then the 42 variants as 10–30 overrides. Every `specified` slot needs variants with `status`, `parameters` with units and sources, and `forbidden` where the style forbids. `garage_strategy` is `specified` on every contemporary buildable variant (WP-4.3). Run the three-level cascade test from `docs/plans.md` on each family: if a style's provenance shows 0% from the family, the family kit is dead weight — fix the family, not the style. Mark `kind: editorial` honestly and list parameters needing a source.

**Acceptance.** No kit at `status: "empty"`; `check_kits.py` green; `resolve_kit` shows multi-level provenance on every variant; OQ 20 answered with data (how many merge problems appeared at three levels and what kind).

**Hand-off brief (per family).** *Fill the TDL kits for family `<family-id>`: the family node first, specifying only what every member shares; then each style using `extends` against the family wherever it adds rather than restates; then each variant as overrides. Follow `kits/georgian-colonial-american.kit.json` and `kits/tidewater-georgian.kit.json` for form and depth, `docs/inheritance.md` for the cascade rules. Units and sources on every parameter; `editorial` where you have none. Run `check_kits.py` after every file and `resolve_kit.py` on every variant to confirm the family contributes. Report the provenance percentages and any merge problem you hit.*

### WP-4.3 The garage

**Status: COMPLETE (24 Aug 2026).** `groupings/garage-and-hyphen.json` authored (8 internal rules, 14 `attaches_to` entries incl. one `forbidden` massing); `compose.py`'s `attach_garage()` places by attachment and refuses with a stated reason where the grouping records none; the last 4 living nodes bound, taking the corpus to 58 `garage_strategy` bindings with every living style covered. Acceptance met and tested both ways — the composer cannot produce the garage-beside-bedroom fatal (a composed garage has exactly one interior neighbour, a mudroom), and a guard test asserts the hand-authored spec Colonial still trips that fatal so the acceptance cannot pass because the rule broke. One unsatisfiable daylight finding left standing on purpose and recorded as OQ 31. See `docs/reports/wp-4.3-the-garage.md`.

**Depends on:** WP-4.2 in progress. **Size:** small but consequential.

**Tasks.** Author `garage_strategy` on every contemporary buildable variant from the dependency-and-hyphen rule (hyphen 12–20 ft, ridge 60–80%, doors off the street elevation) and the style's own massing expansion logic; `forbidden` on the street elevation for the styles whose composition cannot absorb it. Add a `garage` room and `garage-and-hyphen` grouping to the catalogs if not present, with `attaches_to` for the relevant massings. Give the composer a rule that the garage is placed by the grouping's `attaches_to`, never by adjacency.

**Acceptance.** The spec Colonial's garage-beside-primary-bedroom fatal cannot be reproduced by the composer; every contemporary variant has a specified strategy.

### WP-4.4 Images from HABS

**Status: THE NAMING STEP IS DONE AND ITS OWN FIGURES WENT STALE IN EIGHT FILES (2 Sep 2026).** The step every list still named as WP-4.4's next — giving the asset records their `provenance.building` names — finished on 31 Aug, and a dry run now assigns **zero**: 786 of 1,850 records name a building across 305 queries, 180 of them inside HABS's charter. Twelve claims across eight files still said 322, 845, 330 and 188, two of them instructions to do work that was finished, while `check_counts.py` reported 0 stale in the same run — every stale figure sat in a field no claim covered, and **this file was not in the checker's list at all**. Four values are computed now and nineteen claims guard them. `check_assets.py` also gained the check it never had: a building name must be an exemplar of a node the record depicts, its location that exemplar's own, on a photograph that is not `role: incorrect` — **all 786 pass, including the 161 written by hand**. What is left offline is **72 records on 18 exemplar-less higher-rank nodes**, needing sources this container cannot reach or a ruling that a child's exemplar may stand for its parent; the acceptance line (≥100 sourced, zero `license: unknown`) stands at 73 and 1,716 and needs the network. Report: `docs/reports/wp-4.4-the-record-that-said-322.md`.

**Status (31 Aug 2026): THE HARVEST IS STILL BLOCKED; 73 RECORDS WERE NEVER BLOCKED AND ARE NOW SOURCED, AND THE MANIFEST NOW COVERS THE CORPUS.** `322 wanted / 0 sourced` over three style nodes is `1,777 / 73` over 142 — the manifest was a frozen snapshot and the generator had been tracking the corpus all along. **786 records now name a real building** across 305 distinct queries, where 161 named eleven; 180 of those queries are within HABS's US charter. The acceptance line — "at least 100 sourced or generated" — is NOT met by the 73 drawn plates, and widening the authored assembly filter to reach it was refused rather than done. The eleven carry a `generated_from` block naming a proportion pack, and `build/render_profile.py` draws them from the corpus's own geometry — no network, no rights clearance, and everything needed has been present since WP-5.11. The harvester's four defects were also fixed, none of them findable by running it: a rate limit three times loc.gov's ceiling that would have returned 0 after being blocked, an unconditional `license: public-domain` the source does not state, a selector that preferred a record holding no images, and 161 records collapsing onto eleven queries behind a guard testing the opposite condition. Report: `docs/reports/wp-4.4-the-eleven-that-were-never-blocked.md`. **The routes question is ruled** at `oq/fetching-through-a-tier-the-proxy-denies`, and CI — the only tier that can fetch bytes — has not run since 29 Aug.

**Status (superseded, 26 Aug 2026):** All 322 asset records are still `wanted` and none can be sourced from here: this container's network policy denies the Library of Congress at the proxy. What has changed is that the package's own named next step is complete — **161 records now carry a `provenance.building` and its location**, taken from the depicted node's own `exemplars`, so the day the network opens `--live --write` works on those instead of refusing on all 322. Two findings came with it, both in `docs/reports/wp-4.4-offline-half-building-names.md`: the image layer covers **three style nodes**, not the corpus (`georgian-colonial-american` 247, `tidewater-georgian` 46, `english-georgian` 18), which no count anywhere says; and **the other 161 cannot be given a building name at all** — 150 are `role: incorrect`, and the corpus names buildings that exemplify a style, never ones that exemplify a fault. That half cannot be harvested from any archive and needs a decision rather than a fetch.

```
curl https://www.loc.gov/pictures/collection/hh/?fo=json
curl: (56) CONNECT tunnel failed, response 403
gateway answered 403 to CONNECT (policy denial or upstream failure)  host www.loc.gov:443
```

`archive.org` is denied identically, so neither the HABS collection nor a scan mirror is reachable. **What would unblock it:** an environment whose network policy permits `www.loc.gov` (and `tile.loc.gov` for the image derivatives, if files are ever to be carried rather than cited).

`build/harvest_habs.py` is committed against that day. It searches the loc.gov HABS collection for the building each record names, and writes back the provenance a `sourced` record needs. **It has never been run against the live API** and says so in its own docstring — the request shape is written from the API's documented behaviour and every field is parsed defensively. `--dry-run` is the DEFAULT and prints the URLs it would request without touching the network or the corpus; `--write` refuses without `--live`.

Two things it will not do, both deliberate. It never sets `status: approved`, because the asset schema defines that as a human having looked at the image. And it skips any record that names no building rather than searching on a style name — **found by running the dry run**, which showed the first four records all producing `?q=english+georgian` because none carries a `provenance.building`. Sourcing those automatically would give one photograph cited by many records, which is worse than none. **Giving the 322 records their building names is real work that does not need the network, and is the right next step on this package.**

**Depends on:** nothing (can run any time). **Size:** medium, repetitive.

**Tasks.** For the `correct` half of each good/bad pair and for every `exemplar` with a HABS number, locate the HABS/HAER sheet or photograph on the Library of Congress site, record `provenance.habs_number`, URL, and `license: public-domain`, and move the record from `wanted` to `sourced`. Do not download into the repo; the manifest points. Generate the `diagram` and `measured detail` records from the proportion engine (SVG, `generated_from` recorded) — these need no sourcing. For the `incorrect` half, write a shot spec good enough for a photographer and leave `wanted`.

**Acceptance.** ≥ 100 records `sourced` or `generated`; zero records with `license: unknown`; `docs/assets.md` counts updated.

### WP-4.5 Rooms, groupings and partis to full coverage

**Status: COMPLETE (24 Aug 2026) on the parti criterion; the `style_variation` clause declared met at the corpus's own bar and out of scope at the literal one.** Partis 12 -> 21, native styles **39 -> 129 of 132**, nodes with a canonical massing and no native parti **90 -> 0**. Nine new diagrams (courtyard-and-portal, living-hall-picturesque, great-hall-h-plan, connected-farmstead, single-cell-hall, tower-villa, shotgun-linear, dogtrot-open-passage, octagon-radial) plus 36 style-list placements into diagrams that already existed. Two rooms authored (`courtyard`, `overlook`), eleven others deliberately not — `hall` already carries the great hall and the living hall, `cross-passage` the screens passage. `build/check_partis.py` added as a 22nd check, because nothing validated this catalogue at all.

Three of the package's named dozen were skipped on the data and are named rather than dropped: `telescope` (canonical for no style — 0 unblocked), `split-level` (0 unblocked, and needs the schema decision now recorded as OQ 56), `foursquare side hall` (<=1, and `foursquare-quadrant` is already `circulation_parti: "side-hall"`).

Four composer bugs found by running the diagrams rather than reading them: pick order was decided by filesystem order; massing affinity ignored `alternate_massings`; half the kits that state a ceiling height were never read; and the 3-bay floor *dropped* a one-room house rather than inflating it. And the finding that mattered most — nativity was worth `fit * 6` against 8 per serious finding, so a borrowed diagram routinely beat a native one, which adding nine partis turned into a Tidewater Georgian brief recommending an octagon. `NATIVITY_W` is now 20. See `docs/reports/wp-4.5-partis-to-full-coverage.md`; OQ 55, OQ 34, OQ 35 raised.

**Depends on:** WP-2.1 (for the missing-room list). **Size:** medium.

**Tasks.** Add the rooms WP-2.1 found missing. Complete `style_variation` for every room across every buildable style that contains it (name, trim grade, position, or `absent`). Add partis so that every style with a `canonical` massing has at least one native parti (currently 39 of 132 are named) — likely a dozen more: telescope, connected farmstead, hall-house, courtyard, gallery-and-cabinet Creole variants, split-level Ranch, Foursquare with side hall, Shingle-style living hall. Add groupings the partis need. Run `check_rooms.py` and the composer on a brief per new parti.

### WP-4.6 Missing proportion packs

**Status: COMPLETE, 21 packs, 25 Aug 2026. Every item of WP-4.1's list that this corpus can support is built; the items it cannot are named in the report with a stated reason apiece, the Baroque curved wall first among them. All six packs this work package's own task text names as likely candidates are built.** Chosen by measured leverage rather than by the order of the list; the measurement and what remains are in `docs/reports/wp-4.6-missing-proportion-packs.md`.

*First tranche, 24 Aug.* `proportions/orders/moorish-arch.json` — OQ 30's item, the most-corroborated gap WP-4.1 found and the only one that unblocked a node with no binding at all; `moorish-andalusian` and `mudejar` come off `DELIBERATELY_UNBOUND`, which is now one node rather than three. `proportions/orders/greek-doric.json` — the gap WP-4.1 had already recorded as a WRONG binding rather than a missing one, `greek-classical` having been bound to `benjamin-doric` under a note calling it "the least-bad available approximation"; Benjamin is demoted and kept, because American Greek Revival buildings really were built from those plates. Raised on the way: **OQ 46**, the ontology has no arch slot — since built, at ontology 0.6.0.

*Second tranche, 25 Aug.* `proportions/modules/adobe-module.json` — the gap **four style nodes had already written down in their own binding notes** before anyone went looking, confirmed by three WP-4.1 batches besides. The module is one adobe laid as a header, so wall thickness comes in whole bricks; the bracing length (≈10× thickness, ≈24 ft) is what makes an adobe plan a chain of ranges, the exact analogue of the log pen's sixteen feet; and the slenderness limit turns out to be a **ceiling and not a generator**, carried as an 8–10 band because 14.7.4 NMAC says ten and `california-mission-colonial`'s own record says eight and both are right. Bound to 9 nodes, and five stale "missing from the corpus" sentences superseded in place. `proportions/systems/opening-pointed.json` — the **opening half** of WP-4.1's "Gothic Revival facade and opening system", built as the strike ratio (radius ÷ span) that is Rickman's arch families in one number. The facade half was **measured before it was built and mostly does not exist**: all four revival nodes already carry `facade-picturesque` and it fits them. It is real for exactly one node, `english-gothic`, which is the medieval building rather than a revival of it — and that turns out to be the same missing pack as the candidate list's pre-Palladian English facade item, seen from the other side. `rural-gothic-villa`, which PB-7a left with **no opening-role pack at all**, has one. `proportions/systems/opening-craftsman.json` — the opening half of PB-4's item, where the measured gap turned out to be **seven** nodes rather than the five the list estimated. Its central assertion is that there is no proportion: one horizontal line at 6 ft 8 in, and every opening on the elevation dies into it, so an opening's height is the datum minus its sill. The module is the framing bay, which `craftsman` names from the structure and `prairie-school` from the opening as the same 24 in. Two nodes were **refused** for stated reasons rather than bound to close a count — `mission-revival`, whose openings are arched, and `arts-and-crafts-british`, whose own governing logic says "there is no repeating bay and no vertical alignment requirement", which denies this pack's central rule outright. Nodes with no opening-role pack: 68 → 60. `proportions/systems/trim-prairie.json` closes the other half of PB-4's item and is the third gap in this package that the corpus had already written into a binding note of its own -- `prairie-school`'s `trim-craftsman` entry said in terms that "no pack here owns a first-principles, non-catalog Prairie interior system, and none should be invented for one", and this one answers the caution by measuring rather than inventing. It shares `trim-craftsman`'s module deliberately, because both families are built from the same 1x4 out of the same mill and the difference is entirely in what the board does -- a casing leg framing an opening against a band crossing a surface; the two packs' invariants state the opposition directly. It binds ONE node and moves no count, which the pack and the report both say plainly: it exists because a wrong binding is worse than a missing one, the argument that justified `greek-doric`. `trim-craftsman` is kept rather than struck, because the plan-book Prairie box really was trimmed from the same catalogue sections as the bungalow next door.

*Third tranche, 25 Aug.* `proportions/modules/dutch-gambrel.json` -- WP-4.1's Dutch gambrel item, scoped at 3 nodes and reaching 6. It carries TWO devices, because the records show they are independent: `hudson-valley-dutch` has a sprung eave over a straight gable and no gambrel, so it is bound for the eave rules alone. Its central finding is a datum nobody stated -- three style records give the break point and NONE says from where, two as a percentage of the half-span and one as a percentage of roof height, and read naively as from-the-eave the first is wrong by nearly a factor of two. Reconciled against the slope bands the same records give, the colonial figure only works measured from the RIDGE; the pack states one canonical datum with the conversions written out, and the style records are left as they are because the ambiguity is theirs and the pack is where it gets resolved once. The test recomputes that reconciliation rather than asserting the pack's prose. `proportions/modules/balcony-gallery.json` closes the DIMENSIONAL half of the cast-iron item, and the measurement disagreed with the item's own name: the corpus's three most iron-heavy records are `monterey-revival`, `monterey-colonial` and `regency`, and the Monterey balcony is WOOD. What they share with the Creole galerie and the Italianate porch is a horizontal deck applied to a wall, so the pack is named for the deck and iron is one material it is made in. Its central claim is that DEPTH FOLLOWS CARRYING STRATEGY -- brackets 30-48 in, cantilevered joists 5-8 ft, posts to grade 6-14 ft -- and `monterey-colonial`'s own 'one-fifth to one-quarter of the building depth' turns out to be the cantilever-to-backspan limit found by feel. The ORNAMENT half of the item stays open: the anthemion, lyre, heart and trellis patterns, the New Orleans foliate panels and PB-6a's wrought grilles are a pattern repertoire and not a proportional system, left on the candidate list on the same principle that kept muqarnas out of `moorish-arch`.

With the six named candidates done, the rest of WP-4.1's list was MEASURED rather than worked in order, and stone coursing was the largest item by a wide margin: 60 buildable nodes describe stone walling and 34 carried three packs or fewer, against 31 and 23 for the next-largest (the half-timber panel). `proportions/modules/stone-course.json` is that pack. It cannot use `brick-course`'s module -- a brick wall has a gauge rod and a rubble wall has no gauge at all -- so the module is a course of the DRESSING, the only stone with a dimension before it is laid. Its central rule is stated twice by the corpus independently and in nearly the same words, `cotswold-vernacular` and `norman-romanesque-english` both saying ashlar is RESERVED for quoins, jambs, lintels and the rest. It is bound to 12 of the 34 on a stated criterion -- whether the stone wall governs or merely occurs -- with the Iberian nodes left to `adobe-module`, the ashlar Georgian fronts to their orders, and the timber-framed nodes to the half-timber panel module still on the list. Nodes carrying two packs or fewer: 36 to 28. Next by the same measurement: the half-timber panel, then a gable geometry system, which the list records as entirely missing.

*Fourth tranche, 25 Aug.* `proportions/systems/facade-arcade.json`, WHICH THE CANDIDATE LIST NEVER CONTAINED. Three packs in this work package asked for it anyway, two of them under the mistaken impression it was already listed. Measured it was the largest remaining item at 33 nodes and 24 thinly bound, and it is the only pack in the package claiming `confidence: high` -- nine unrelated records give its pier-to-span ratio as one third to one half, five countries and six centuries apart. The arch's SHAPE is deliberately not in it, which is what lets it compose with `moorish-arch` and `opening-pointed`. First movement in the facade-role count: 67 to 61.

`proportions/modules/timber-panel.json` is WP-4.1's half-timber panel item, and the list's own phrase 'distinct from `timber-bay`' did more work than it looks: six of the sixteen rules planned for it were already that pack's, and it is bound to seven of the same nodes. So this pack restates none of them and holds only what FILLS the frame. Its central rule is REGIONAL rather than universal -- the panel proportion runs 1:1 German, 1.2 English south-east, 1:3 to 1:4 East Anglian and Norman close studding, and `english-medieval-timber-frame` holds two of those in one sentence -- so there is no correct value, only a correct value for a place. Two nodes refuse themselves in their own words ('no half-timbering', 'without applied half-timbering'). It raised **OQ 47**: the ontology has no slot for an exposed structural member on a wall face, so four rules route through `corner_board`, and four packs in this package have now done the same thing.

`proportions/systems/opening-mullioned.json` closes TWO list items at once -- the four-centred Tudor arch and the leaded-casement-and-mullion system -- because they turn out to be one window, and both had been raised again from inside this package by `opening-pointed`'s own boundary and `opening-craftsman`'s refusal of `arts-and-crafts-british`. Its central rule is that THE WINDOW IS COUNTED AND NOT MEASURED: `styles/tudor.json`'s 'window width is a whole number of lights', so widths are quantised at the light and eight records converge on that light at 400-550 mm. Three cross-pack echoes: the tall unit in a wide band, which is `opening-craftsman`'s inversion four centuries earlier; both traditional opening packs failing IRC R310 on the MULLION rather than the head, which is a fact about the code as much as about the windows; and a glazing ratio that is a history rather than a range, Elizabethan 45-60 and higher at Hardwick, Jacobean explicitly a retreat to 30-45, the revival back at 35-55. Opening-role coverage 60 to 50; nodes carrying two packs or fewer, 36 to 14.

`proportions/systems/facade-gable.json` fills a class the list says the library has NONE of, and absorbs three of its items -- the Cape Dutch holbol, the Low Countries stepped/bell/neck gables and the Scottish crow-step -- because the useful distinction runs across the list's division rather than along it: a gable is either the END OF A ROOF, a PARAPET carried past it, or a SCREEN standing free of it, and four records distinguish those three without any of them talking about the others. Facade-role coverage 61 to 58.

It also forced a proper measurement of the ADDRESS COLLISION `facade-arcade` had found once: 1,922 instances corpus-wide, 75 addresses, 622 pack-pairs. The measurement was MISLEADING and reading it changed the question -- the largest entries are packs colliding with themselves, and those are deliberate MENUS ('SHAPE 1 OF 7', 'METHOD 1 OF 3'), so a naive uniqueness check would have flagged 1,710 correct rules. Only two packs meaning DIFFERENT quantities at one address is a corruption; four were found and fixed. **OQ 48** carries the measurement and both proposals, and NO CHECKER SHIPPED, which is itself the finding.

Two defects its own tests found, both introduced by this package. A SILENT SLOT-ADDRESS COLLISION: `facade-arcade` and `moorish-arch` were both writing to `porch_support`/`height` meaning different quantities -- the impost block's height against the springing line above the floor -- on three nodes that bind both. Two packs putting different quantities into one address is a corruption rather than a conflict, because whichever resolves last wins and nothing reports it, and precedence cannot help. And PRECEDENCE CONTRADICTING ROLE sixteen times across fourteen nodes, twelve of them mine, because every new binding was inserted at the first unused precedence and 0 is nearly always free; `check_pack_bindings.py` checked precedence for being a total order and never for agreeing with role. Both fixed, and the checker now errors on the narrow rule -- measured, `secondary` ahead of a role pack is the corpus's own convention in 253 places across 59 nodes, so only 'nothing outranks a primary' is enforced and the rest is warned.

*Fifth tranche, 25 Aug.* `proportions/systems/trim-sawn.json` closes FOUR ornament items at once -- sawn Gothic bargeboard, the sawn-bracket Victorian, turned Queen Anne millwork and the pierced valance -- because all four are one machine: the scroll saw and the lathe, working stock that comes in quarter-inch steps. `proportions/modules/octagon-geometry.json` was the largest item on the list by its own count, 17 nodes, and much the smallest when measured -- ONE node builds an octagonal plan and the rest carry a canted bay -- so the pack states Fowler's whole-building geometry and Jefferson's room-scale corner cut side by side, and its cost conflict records that Fowler's arithmetic was right (nine per cent less wall for the same floor) and his conclusion was wrong (eight 45-degree corners cost more labour than the wall saves in material). Both packs' notes say so, because a traditional form is not automatically the economical answer to anything.

`proportions/systems/facade-pavilion.json` closes THREE list items, and the merge is the finding rather than a convenience. The list asks separately for a French vertical travee facade system ('French Renaissance Chateau has no fit at all') and for a mansard/dormer massing module ('Second Empire has no fit among the 5 existing modules'), and the second item's own parenthesis -- 'dormer-to-bay proportion' -- names the first item's unit. They are one system: the mansard's dormer is proportioned against the travee and the pavilion is what breaks the travee's repetition. Its central claim is about DIRECTION -- `facade-classical` composes in horizontal layers and this composes in vertical strips, ground storey to the finial of a lucarne that cuts through the cornice -- and two of its rules carry a SINGLE permitted value rather than a band, which is unusual here and deliberate: the openings in a travee share one axis exactly, and the cornice is continuous with the dormer passing through it, and neither has a partial version. It records a cross-pack agreement with `dutch-gambrel`: the same roof in two countries, differing entirely in the BREAK and its datum -- a gambrel's at about a third of the half-span measured horizontally, which that pack had to reconcile from three records that never said from where, and a mansard's at 0.6 to 0.7 of the roof's HEIGHT, which `styles/french-baroque.json` states in those words. The third item folded in is the Baroque one and only half of it: the avant-corps and end pavilion are built, and THE CURVED WALL IS STATED AS NOT SUPPORTABLE -- reading all twenty-two Baroque-matching nodes, not one gives a figure for an undulating elevation. It stays on the list with a reason beside it rather than being quietly dropped or plausibly invented. `french-renaissance-chateau` and `second-empire` gain a facade-role pack, 58 to 56, and `facade-picturesque` is displaced on three nodes whose irregularity is disciplined rather than picturesque. Two address collisions found by `pack_addresses.py` and both renamed: `roof_form`/`break_ratio` off `facade-picturesque`'s roof-width fraction, and `dormer`/`lucarne_height` off `storey-graduation`'s dormer WINDOW.

*Sixth tranche, 25 Aug.* `proportions/modules/jetty-overhang.json` -- THE FIFTH GAP IN THIS PACKAGE THE CORPUS HAD ALREADY WRITTEN DOWN ITSELF. `styles/garrison-colonial.json`'s binding note to `timber-bay` says, before anyone went looking, that 'no pack in this corpus dimensions a framed overhang, and the 14-20 in framed / 2-6 in hewn figures in this node's own record are not recoverable from any of the 36 packs available.' The module is the JOIST and not the bay, because a jetty is not a division of a bay -- it is a cantilever, and every record that gives a rule rather than a number states the projection as a multiple of the joist's depth. AND THE FOUR RULES DISAGREE: about 2x from both garrisons, 1.33x from the English medieval frame, 1.0x from Tudor Revival. The pack does not average them, because the three multiples measure three different failures -- at 2x the limit is visible SAG on a cantilever with generous backspan; at 1.33x it is the LOAD, since the medieval jetty carries a storey of wall on the joist ends; at 1.0x it is PLAUSIBILITY, because a revival jetty carries nothing and the eye is stricter than the structure. That reconciliation also settles what looks like a contradiction in the inches: the medieval joist is TWICE the colonial one, so the English jetty is longer absolutely while being a smaller multiple, and a compiler handed the multiple and the joist gets both right where one handed only inches gets one wrong. Two devices, like `dutch-gambrel`: the framed jetty (a cantilever, 8-24 in) and the hewn overhang (a chamfer cut out of one continuous post, 2-6 in, with nothing for a pendant to be the bottom of). One rule is the exact INVERSE of `facade-pavilion`'s -- same slot, same single-value machinery, opposite instruction: there every opening shares one axis, here the pendant rhythm and the window rhythm must not be reconciled, because one is the frame and the other the fenestration. Bound to 5, refused 3 with stated reasons, and one of those refusals raised **OQ 49**: `french-normandy-revival` states one of the pack's rules verbatim without being an instance of its type, and the binding model has no way to scope a binding to one slot.

*Seventh tranche, 25 Aug.* `proportions/systems/facade-portada.json` -- THE SIXTH GAP THIS PACKAGE FOUND ALREADY WRITTEN INTO THE CORPUS, and this one names the pack by name: `styles/spanish-plateresque.json`'s `moorish-arch` binding note ends 'WP-4.1's own portada/retablo gap is the pack Plateresque actually needs and it is still missing.' Two more bindings on the same two nodes decline the work explicitly -- `vignola-tuscan` bound 'NOT for the ornamental panel, which no order pack in the library should be forced onto', and `room-harmonic` on `churrigueresque` bound as a judgment 'with real doubt'. `churrigueresque` had ONE binding, and it is the style whose entire subject is an ornamental panel. THE MODULE IS THE PANEL AND NOT A MEMBER, which makes this the only top-down pack in the library: everything else here derives from a diameter, a brick, an adobe, a joist, a light or a board, and `styles/spanish-plateresque.json` states the inversion outright -- the columns inside a portada are 'dimensioned to fill their register rather than to any canonical ratio of diameter to height'. A column in a portada has not been proportioned, it has been FITTED, which is why no order pack fits and why two bindings had already worked that out. And the two parent styles DISAGREE about the module in a way that is the difference between them: Churrigueresque re-introduces a member module ('the only continuous dimension in the design is the estipite itself') after Plateresque abolished one, so the later and wilder style is in this one respect the more regular. THE RATIONING RULE IS WHAT SEPARATES THE STYLES AND IT IS AN INTEGER: nine records state it, four as a count, and the corpus's own 'single most frequently confused pair in American architecture' -- mission-revival against spanish-colonial-revival -- differ by that count and by nothing else. One rule dimensions the SILENCE, a minimum 12 ft run of unornamented wall each side, which is the only rule in the corpus that gives absence a minimum size. And its `entablature`/`continuity` = 0.0 is the exact inverse of `facade-pavilion`'s `cornice`/`continuity` = 1.0, authored two packs apart: between them they bracket what a horizontal may do on a facade. Bound to 8, `mission-revival` refused -- and that refusal is **OQ 49's second independent instance in two packs**, which raises the question from a curiosity of one binding to a pattern.

*Eighth tranche, 25 Aug.* `proportions/systems/facade-peristyle.json` -- THE ORDERS ARE NOT THE COLONNADE, and this library had eleven packs for one and none for the other. `greek-classical` and `roman-classical`, the two antique sources of the whole classical corpus, carried NO facade-role pack at all. The module is the axial intercolumniation rather than the diameter, which is what lets one pack hold both traditions: the same twelve-foot bay carries a fat Doric column at 2.45 diameters or a slim Corinthian one at 3.25. ITS CENTRAL QUESTION IS THE SCREEN AND THE WALL AND THE CORPUS GIVES FOUR SETTLEMENTS -- Greece has nothing to reconcile (the peristyle IS the building); Rome lets the wall govern and chooses the intercolumniation 'to suit the required arch span'; the Southern plantation lets the wall govern the other way ('column spacing is set by the bay of the house behind'); and Neoclassical Revival reconciles neither, which its own record calls 'the characteristic mismatch between screen and wall'. That mismatch is arithmetic: four columns over five bays and six over seven, an even screen against an odd wall, agreeing at the centre and nowhere else. This is the FOURTH pack in the tranche to write to `window_grouping_rule` about whether an elevation's systems must agree, and that the axis surfaced four times in four consecutive packs -- from France, New England, Spain and Greece -- is better evidence that it is a real dimension of facade design than any one of them. Two rules are unlike anything else here: `column`/`flank_count` is THE ONLY CLOSED-FORM COUNT RULE in the corpus (n_flank = 2 x n_front + 1, so a Greek temple's plan proportion is computed from one integer rather than chosen), and `column`/`height_by_spacing` is THE ONLY RULE THAT IS A FUNCTION -- Vitruvius gives three points that fall on a line, and the pack states the line and REPORTS ITS RESIDUAL (9.4 against a recorded 9.5) rather than tuning it away. One convergence worth recording: five independent records put the intercolumniation floor at 2.25 diameters EXACTLY, across two countries and a century and a half, which shows the revival is MORE UNIFORM than either of its sources -- because 2.25 is Vitruvius's eustyle and the revival worked from the book while the ancients worked from the buildings. Bound to 9; no portico depth rule is stated at all, deliberately, because that dimension is `balcony-gallery`'s gallery depth and `neoclassical-revival`'s own constraint note says so -- a collision avoided by not writing the rule, which is the cleanest form of the fix. `egyptian-revival` stays unbound, and that is **OQ 49's third instance in three packs**: two of this pack's rules fit it exactly and thirteen do not, so 131 of 132 stands and the cost of the open question is now precise -- its proposal would bind the corpus's LAST unbound node.

*Ninth tranche, 25 Aug.* `proportions/modules/corbel-course.json` -- THE LIST NAMED ONE INSTANCE OF A CLASS AGAIN. WP-4.1 asked for 'a Mudejar brick corbelling module'; measured, the device is in FOUR unrelated traditions with figures -- Mudejar whole-brick bands, the Scottish corbelled bartizan (1.2-2.0 m diameter, out 450-750 mm), the Anglo-American corbelled chimney cap (3-6 in), and the Provencal genoise with its Tuscan twin the gronda (300-600 mm on two to four tile courses). They share no vocabulary, period or country and are all the same move, because a masonry wall has exactly one way to get an overhang. THREE RECORDS HAD WRITTEN THE GAP DOWN: `mudejar`'s own binding note, `queen-anne-patterned-masonry`'s constraint note ('no matching vocabulary variable... and stays prose'), and `stone-course`, which declined the bartizan and quoted its numbers into its notes so they would not be lost. THE PACK IS `jetty-overhang`'S SIBLING and the pair is the point: a timber wall cantilevers a joist and the limit is 1.0-2.2 times its depth; a masonry wall steps a course and the limit is 0.4-1.2 times its depth. Same reconstruction in both -- divide each record's total by its own count -- and both find three traditions agreeing and ONE OUTLIER WITH A MATERIAL REASON: here the tile eave at two to four course depths, because a tile corbel is limited by the unit's LENGTH and not its bed depth. Its module is `brick-course`'s PART exactly, which is the two packs interlocking rather than competing. One rule is pure arithmetic (a unit turned 45 degrees projects 0.2071 of its width, so a dogtooth's projection is not adjustable without changing the brick) and one is A SOCIAL FACT -- the genoise's course count, which `french-provincial-farmhouse` states as 'quite literally, a statement of the owner's standing', the only quantity in this library given as a declaration of wealth. And a finding from the previous pack turned out to be general: `facade-portada` read 'ornament works by being bounded' as an Iberian characteristic and three of this pack's six records say it too with nothing in common, so it looks like a law of this corpus rather than a region's habit. Bound to 6, including the corpus's two thinnest-bound nodes; three refused, two of them because THE WORD CORBEL NAMES TWO THINGS -- a pueblo zapata is a carved wooden bracket, not a stepped course, and a keyword sweep would have taken its figures. Fifth over-count of the package, and the first by ambiguity rather than breadth.

*Tenth tranche, 25 Aug, and the last.* `proportions/systems/facade-medieval-english.json` -- the final item on the list, and 'new' only in that two existing items turned out to be one pack seen from two sides: `opening-pointed` raised it from the Gothic end and `opening-mullioned` from the Tudor end. FIVE OF ITS SIX NODES HAD NO FACADE-ROLE PACK. Its claim is that THE FACADE IS GENERATED FROM BEHIND, and four records state it independently -- 'the bay, not the facade, is the unit of composition'; 'window widths are dictated by the frame rather than the other way round'; 'windows do not establish a rhythm of their own; they sit where the wall can spare the material'; 'windows are placed where rooms need them'. Every classical pack here composes an elevation and lets the plan follow; here the elevation is a RESULT, which is the one thing a compiler built on classical assumptions gets wrong every time. THE ENGLISH MEDIEVAL BAY IS THE LENGTH OF A TREE: four records, four centuries and four structural systems all give 3.0-5.5 m, because the limit is the length of sound oak a carpenter could get and even a stone vault's centering is timber. Set beside `facade-peristyle`'s five revival records converging on 2.25 diameters from a book, that is TWO MECHANISMS OF CONVERGENCE, one textual and one material. THE POINTED ARCH HALVES THE PIER -- the record states its own comparison, 1:4 to 1:6 'against 1:2 to 1:3 in Norman work' -- and the Perpendicular window at half the lancet's proportion is where that process ends. One rule runs BACKWARDS and nothing else in the library does: Elizabethan storeys increase upward at Hardwick, 'the exact inverse of the Georgian rule'. And the Jacobean gable rhythm is the FIFTH instance in this tranche of an elevation's systems declining to agree, the second to use the word CHARACTERISTIC for it. It also brings the ornament-rationing finding to five unrelated traditions, which the report's closing section hands on as a package of its own.

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

**Status: COMPLETE (25 Aug 2026).** `build/export_dxf.py` (one layered DXF per sheet, inches, the record riding on the entities as XDATA), `build/export_ifc.py` (IFC4, feet; walls, slabs, openings, roof, spaces, every product with its TDL ids in a `TDL` Pset), and `build/import_dxf.py` (a minimal reader scoped to TDL-emitted DXF, by ruling — WP-5.5 generalizes it). Acceptance met and exceeded: the round-trip gives identical validator findings on both check plans *and* the rebuilt record deep-equals the authored one; the importer refuses when drawing and carried record disagree. ezdxf/ifcopenshell are optional by ruling — the exporters refuse honestly without them and `check_all.py` gained a third state (`N/EV — COULD NOT EVALUATE`, exit 3) so the missing-library case is named, never counted as a pass. The workbench Export card is live (`/api/export/{dxf,ifc}`). What is honestly not modelled (hip/gambrel roof solids, unstated sill heights, exterior-door placement) is stated per element. Report: `docs/reports/wp-5.1-export-dxf-ifc.md` · layer doc: `docs/export.md` · new open question: OQ 39.

**Depends on:** WP-3.1. **Size:** medium.

Emit DXF (ezdxf) plan, elevation, section and roof plan with layers per element group, and an IFC (ifcopenshell) model with walls, slabs, openings, roof and spaces carrying the TDL ids as property sets. Round-trip test: DXF → plan record → validator gives the same findings.

### WP-5.2 The plan workbench

**Depends on:** WP-1.2; better after WP-2.2. **Size:** large.

A self-contained HTML tool in `dist/` in the manner of `orders.html`: load or sketch a plan record, see findings by layer inline on the drawing, drag a wall on the bay grid and re-score, switch style and watch constraints change, request N candidates from the composer (via the MCP server or a Python port). This is the interface a plan-development lead works in; its absence is a gap in the collaboration, not just the software.

**Status (25 Aug 2026): built, with one approved divergence from the package text.** Delivered as a locally served app in `workbench/` (FastAPI over `mcp_server/core.py` + a Vite/React frontend in the Drawn Language), not a self-contained `dist/` HTML file — the interactions this package names (re-score on a wall drag, style switch, compose on demand) are live calls into the Python toolchain, and a static file would have required JS ports of the validator, composer and geometry solver, compounding the dual-engine tax the orders tool already pays. Divergence approved by Lucas, 25 Aug 2026. The MCP-server-or-Python-port fork the text left open is resolved a third way: the server imports `core.py` directly and the rail's 24 tools are `mcp_server/server.py`'s own wrappers. All ten surfaces live (Phylogeny, Style Record, Kit, Fault Corpus, Proportions, Brief Intake, Candidate Set, Plan Workbench with drag-and-re-score, style switch and assert-a-fact, Drawing Set, Details & Export). The Proportions surface speaks HTTP to the engine rather than reusing the orders tool's JS port; the Drawing Set re-tokenizes the four renderers' SVG into the Drawn Language (re-rendered, never redrawn); Export ships the record, the report and the sheets today and names DXF/IFC (5.1), guidelines/details (5.3) and ingestion (5.5) as forthcoming rather than hiding them. Two additive `build/` touches (`plan_check.check()` returns `fault_unjudged`; `compose()` takes `on_candidate=`), both pinned in `tests/test_workbench_touches.py`. Report: `docs/reports/wp-5.2-the-workbench.md` · layer doc: `docs/workbench.md` · new open questions: OQ 32–35.

### WP-5.3 Generated guidelines, details and modelling conventions

**Status: NOT STARTED (stated 3 Sep 2026; the package had carried no Status line at all in a document
whose first rule is that every one does).** It is the largest unstarted named deliverable in the brief.
The deferral was a choice — "waiting on Phase 4 breadth" — and **that precondition closed on 25 Aug
2026**, so the deferral is now a decision to be re-made rather than a dependency. One caveat the corpus
has since established and this package's text does not know: the **ranked honest/dishonest substitution
sets** its details library is written around are planned structure the corpus does not hold — the 262
recorded pack conflicts carry resolution prose, not ranked sets (the WP-5.2 audit, 25 Aug 2026), so
that deliverable either generates from what exists or authors the structure first.

**Depends on:** Phase 3. **Size:** medium.

Three documents the brief asks for, all generated from data so they cannot drift: a **design guidelines** book per style (constraints, forbidden variants, faults with exceptions, pack bindings, rendered orders and details); a **standard details library** (every `measured detail` asset rendered by the engine, every pack conflict with its ranked substitutions, the `cheap` fix for every fault); and a **modelling conventions** note (how a drafter models against TDL ids in CAD/BIM, layer naming, the bay grid, which dimensions are clear and which are structural). `build/gen_guidelines.py` emits HTML and PDF per style.

### WP-5.4 Cost layer (defer until the plan-development partnership exists)

**Status: NOT STARTED, AND DELIBERATELY SO (stated 3 Sep 2026; it had carried no Status line).** Gated on
a partner's numbers, not on effort. It is the one clause of `VISION.md` §XII that is still false —
"drawings a builder can price" — and it must stay false until somebody with real numbers supplies them,
because authoring costs here would be `VISION.md` §VII's laundering rule broken at the scale of a whole
layer.

Scope only: unit costs by construction type and region; the 32 `cost_negative` faults as savings; candidate comparison by cost per square foot. Do not author costs without a partner's numbers.

### WP-5.5 Drawing-to-record ingestion

**Status: COMPLETE (25 Aug 2026).** Three rulings first: the form is a workbench surface (⑪ Transcription, following WP-5.2's approved divergence, not a `dist/` HTML file); the drafter-DXF importer extracts candidates a human completes in the form, never a guessed record; and plan schema 0.2.0 gains the structured `provenance` object WP-2.1 asked for (`style` stays required — the form holds the draft until a human sets it). `build/ingest_dxf.py` generalizes WP-5.1's reader: closed polylines → candidate rooms (bounding-box honesty flagged), contained text → name hints, everything a drawing cannot state → a named gap; units from a stated header or a room-scale heuristic that labels itself an inference and *refuses to pick* on a tie (feet vs metres is the collision that actually occurs). TDL-emitted sheets short-circuit to the complete cross-checked record. The surface traces on a browser-local backdrop (never uploaded), names every gap between draft and record, and stays inert until the list is empty; `POST /api/ingest/dxf` serves it. Found: schema 0.1.0 had carried `sill_ft` unused since the beginning — the IFC exporter now reads it and OQ 39 was corrected. Report: `docs/reports/wp-5.5-drawing-to-record-ingestion.md` · layer doc: `docs/ingestion.md`.

**Depends on:** WP-2.1 experience. **Size:** medium.

### WP-5.6 The navigation overhaul

**Status: COMPLETE (26 Aug 2026).** Raised by Lucas, not by the plan: *"extraordinarily overwhelming… painfully difficult to navigate… there's no apparent search bar anywhere for anything"*, with the standing constraint that machine usability must not be compromised to serve the human one. Four rulings taken before any code (full restructure over additive aids; both a global palette and per-view filter bars; the Drawn Language kept unchanged; served equally to the fluent author and the newcomer), and three more mid-package (the rail's circled numerals removed, an Overview surface as the landing, the palette indexing entities and surfaces but not the rail's tools).

**The finding that organised it:** the product already had a complete, validated addressing scheme and was not using it to navigate. `routeCite()` turned a citation into `{surface, selection}`; navigation was a `useState` string. So the URL became that pair written down — `#/kit/tidewater-georgian/cornice`, `#/faults?sev=serious`, `#/cite/fault:…` — and the palette, the filters and the back button all fall out of one mechanism rather than three. **One addressing scheme, three audiences**: the reader, the rail, and anything driving the HTTP API.

Built: a hand-rolled hash router and a fourth external store (`state/nav.js`); `GET /api/search/index` over 665 named things with a `⌘K` palette that dispatches by citation; `useFilters` holding filter state in the URL, which retired twelve hand-rolled copies of `setX(x === v ? null : v)`; the `Chip`/`ActionChip`/`ChipGroup`/`FilterGroup` split with the ARIA it never had; a `StylePicker` combobox retiring six 164-option `<select>`s; an `Overview` landing whose every claim comes from `/api/overview`; a left rail regrouped by errand; and the Phylogeny's **map reading** (`?view=map`) placing style origins and drawing lineage as arcs. No new npm dependency — the app still has two.

**Found:** the two halves of the citation grammar disagreed on whether an id may contain a dot, so all **660 constraint ids** validated server-side, streamed as citations and parsed to null in the browser — every `constraint:` chip the rail ever drew was inert, silently. `/api/phylogeny` truncated `regions` to three, silently coarsening the 82 of 164 styles that carry more. The Kit's header claimed 95 slots against an ontology holding 97. A session-scoped test fixture gates every test file sorting after it (OQ 64).

**The map's discipline, because it is the one place this package could have laundered a guess:** the corpus holds no coordinates, so the gazetteer is interface furniture that may never migrate into `styles/*.json`; placement precision is drawn rather than hidden (81 of 164 styles name only a country, which is not a hearth, and those marks are hollow and hatched); a style that cannot be placed is listed, never nudged onto a continent; and 16 lineage edges are not drawn at all because both ends share a hearth. Basemap is public-domain Natural Earth, vendored as 888 points — no map library, no tiles, no network.

**Machine usability, proved rather than asserted:** `rail.py`, `mcp_mount.py`, `citations.py` and `tools.py` are byte-identical to their pre-package state, `mcp_server/` and `build/` untouched, the `/mcp` mount verified live, the citation grammar only widened, and the three-state rule preserved by redesigning no judgment component. Accessibility improved, which serves both audiences at once.

Report: `docs/reports/wp-5.6-navigation-overhaul.md` · layer doc: `docs/workbench.md` (new "Navigation and addressing" section) · new open questions: OQ 64, OQ 65.

**Depends on:** WP-5.2. **Size:** large.

### WP-5.12 The four rulings, and a correction that did not land

**Status: COMPLETE (27 Aug 2026).** Executes Lucas's rulings on the three open questions WP-5.11's adversarial audit raised and the one it widened — and opens by fixing an error in the commit that raised them.

**The correction that did not land.** `529310c` states in its message, in the WP-5.11 report addendum and in the summary given to Lucas that two `width_parts` were corrected to their sources. They were not: the rewrite loop assigned the new value on reaching `spacing_parts`, then kept iterating and copied the file's original value back over it, while the NOTES were rewritten regardless — so two members carried a provenance sentence saying they had been corrected beside values that had not been. Fixed, verified by reading back from disk. **The guard added alongside could not have caught it, and that is the more useful finding:** the ratio invariant relates width to pitch, so halving BOTH preserves it (6.5/17.5 and 13/35 both read 37%). A transcription has to be pinned against its quoted source, not its neighbour — `TestTheTranscribedWidthsAreTheAuthoritiesOwnFigures` now pins all fifteen against the words each was read from, mutation-tested.

**OQ 78 — detect the datum per assembly-GROUP, once.** Two signals, either settling it: a recorded 0 (impossible under the radius reading — what an entablature gives) or nothing in the group reaching its own naked (every member inside the shaft — what a capital gives). Only ever downgrades `axis` to `naked`. Grouping cost a first attempt: judged per assembly, `gibbs-ionic`'s cornice still read `axis` while its frieze read `naked` — an entablature in two coordinate systems, a subtler wrong answer than the one it replaced. `eave_cornice` delegates now, closing the 2.37× divergence between the inset and the plates. **Faces flush with their own naked 192 → 81; 60 assemblies across the 14 axis packs now read naked-relative.** `check_orders.py` gained `note()`, a third reporter beside `err` and `warn`, and prints which assemblies contradict each declaration — the silence was the whole cost of the question.

**OQ 81 — the Benjamin pitches corrected** to 35 and 31, matching each pack's own module block ("Every figure here is in minutes") and its quoted authority; the halving sentences in both notes corrected with them; the rest of the Benjamin members swept and clean.

**OQ 82 — the teeth are drawn.** `repeat_positions()` had two bugs before it had a caller (filled forward only; two anchors double-claimed the teeth between them). The elevation cornice lays its band out anchored on the bay centres. **Where a width is unstated the band draws solid and the sheet prints the reason** — the behaviour three documents described and no surface performed. The ruling is narrower than it looks and the report says so: a section cannot show repetition, so the order plates correctly do not get teeth.

**OQ 83 — the paths are serialised in Python and both JS copies are gone.** `pack_geometry` emits `path` per pack and per face in MODEL inches; the two surfaces apply an SVG `<g transform="… scale(k,-k)">`. **A model-space path has no handedness for a consumer to get wrong** — SVG mirrors the arcs itself. Better than testing two copies against each other, because it removes the thing being tested. Guarded by a source-reading test (comments stripped, so the history stays in prose) plus one asserting Python actually serves paths with arcs in them; both mutation-tested.

Report: `docs/reports/wp-5.12-the-four-rulings-from-the-geometry-layer.md`. **No new open questions.**

### WP-5.11 The geometry layer: moulding constructions, coursing, and repetition

**Status: COMPLETE (26 Aug 2026).** Raised by Lucas against three drawn surfaces — the Drawing Set's front elevation ("bears not even a passing resemblance to a true Georgian tidewater precedent"), the eave cornice inset ("a most abstracted step knob, painfully primitive relative to the actual sophistication of the profiles"), and the order Proportions plate — with the question attached: is SVG capable of this at all, or does the project need a CAD/BIM layer underneath?

**The answer, and the finding the package records: SVG was never the constraint, and CAD/BIM could not have fixed it, because a format serialises what is modelled and cannot invent what is not.** The proof was already in the tree: `export_dxf.py` exported the whole cornice as ONE RECTANGLE, not because DXF cannot hold an arc but because no layer of this corpus held a moulding as geometry. Meanwhile all 502 order members already carried a machine-readable `profile`, and the resolved Tidewater kit already stated a ten-course moulded water table, 2.75 in coursing, gauged arches with rise and camber, and the chimney's plan size — almost none of it drawn. The missing thing was the layer between: constructed 2D geometry.

Built: **`build/profiles.py`**, which constructs each moulding from the member's own two numbers — a quarter of an ellipse for an ovolo, two tangent arcs through the chord's midpoint for a cyma (radius falling out of the geometry, not chosen), a half round for a torus — plus tooth-by-tooth repetition, the OQ 65 datum rule stated once, and serialisers to SVG and to DXF **bulges** so a circular arc reaches CAD exactly. `width_parts` on 14 members, every figure TRANSCRIBED from the member's own note (Lucas ruled editorial authoring acceptable; it was not needed and none was written). The order tool lost `segTo()`/`buildGeometry()` — 106 lines of Bézier constants and a duplicate datum — for a 30-line mapper: geometry is linear in the module, proved not assumed, so it is computed once in Python and scaled by everything that draws it, and **JavaScript no longer knows what a cyma is**. The elevation gained brick coursing, the moulded water table as the assembly it is, gauged flat arches switched on the plan's own date, sills, real projections everywhere, and a five-rung weight ladder. The Proportions plate draws true profiles, **overturning its own in-file ruling** ("those stay in the order tool") on Lucas's word.

**Found:** the inset's curves had NEVER been drawn — `profile_silhouette_path()` called `seg_to()` with `xa == xb` on every member, so every curve degenerated to a vertical face, and `TestSegTo` pinned the control-point arithmetic exactly while being blind to it (**pinning the arithmetic of a curve nobody can see is not a guard**). A pack's declared projection datum is true of its column and NOT of its entablature — `gibbs-ionic` declares `axis` while its frieze records 0 — so reading the declaration literally deletes the bed mould, which is what `dist/orders.html` still does (OQ 78). Gibbs and `facade-classical` give the same cornice two projections 2.3x apart, both sourced (OQ 79). The chimney width was **not a missing measurement but a deferred one** — `judgment: true`, "the mason will build 18 or 27" — so its `NOT_MODELLED` entries STAY, with reasons corrected from "nobody wired it" to "nobody is entitled to", while the renderer's hardcoded 36 in went. And the front elevation still cannot show its chimneys, because `roof.py`'s long-face silhouette stops at the eave; the attempt was **withdrawn** rather than shipped (OQ 80).

**The durable lesson:** OQ 52 swept twelve invented constants out of the measurements and is guarded by a test that reads the measurements dict — which cannot see SVG. The 36 in chimney and the fake pixel projections lived on the other side of that line. **The honesty discipline has to reach the renderers, not just the records.**

Report: `docs/reports/wp-5.11-real-2d-geometry.md` · layer docs: `docs/proportion.md`, `docs/elevation.md`, `docs/export.md` · new open questions: OQ 78, OQ 79 and OQ 80.

**Depends on:** WP-3.2, WP-5.1, WP-5.2. **Size:** large.
### A NOTE ON THE TWO WP-5.7s, AND HOW IT WAS SETTLED

**There were two work packages numbered 5.7 and they were different packages.** Main's is the
atlas and the shell's proportions; this branch's was the geometry layer. The same two sessions
that collided over open-question ids 72-83 collided over the work-package number in the same
three days, by the same mechanism — reading the working tree and adding one — and the OQ block
was renumbered at every merge while the work packages never were.

**RULED and executed 28 Aug 2026 (OQ 90): this branch's chain moved.** WP-5.7 → **5.11**,
5.8 → **5.12**, 5.9 → **5.13**, 5.10 → **5.14**, by the rule this register has now applied to
ids four times — whoever merged first keeps the numbers, and it is never the side still on a
branch. Main's atlas keeps 5.7.

**What it cost, and how the ambiguous half was done.** 5.8, 5.9 and 5.10 name one package each
and converted mechanically: 9, 63 and 45 references. **WP-5.7's 87 did not.** Each was
attributed by `git blame` to the commit that wrote it — `7beb40a`/`529310c` and the chain after
them are the geometry package, `958276b`/`2c77499` the atlas — and the sixteen written by later
commits were read one at a time. The only genuinely unclear one was the check-count claim (*"the
CHECK figure said 32 against a suite of 33 until WP-5.7 read the total"*, in CLAUDE.md,
`build/check_all.py` and `tests/test_counts_guard.py`): `7beb40a` is the only WP-5.7 commit that
touches `check_all.py`, so it is the geometry package's and it moved. Final split: **53 moved,
21 stayed with the atlas.**

**The deferral's own reasoning turned out to be false, which is why it was not deferred again.**
The note this replaces argued that nothing was ambiguous because *"a work package is cited by its
REPORT, never by its number alone."* It was already untrue: `wp-5.8-the-four-rulings.md` and
`wp-5.10-the-four-rulings.md` were **different packages with identical slugs**, told apart only
by the number the argument said not to rely on. Both were renamed to say which four rulings they
carry, and `build/check_ids.py` now fails the build on two reports sharing a slug — and on a
`docs/reports/...md` path cited anywhere in the tree that does not resolve, which found
`wp-2.3-real-solver.md`, cited in two files and never existing.

**Five commit subjects cannot be changed** and still read `WP-5.7:`, `WP-5.8:`, `WP-5.9:` and
`WP-5.10:` — `7beb40a`, `529310c`, `fa4bf90`, `40fc540`, `92fd7f9`, `bfbc7c1`, `f768c02`,
`426ed35`. Read them against the conversion table in `docs/open-questions/README.md`.

**And the cause is fixed rather than recorded this time.** WP numbers and open-question ids are
both on §1's never-reuse list now, and the register is a directory — one file per question, so
two sessions issuing id 99 collide on a PATH that git refuses to auto-merge rather than in a
file it silently juxtaposes.

### WP-5.7 The atlas, and the shell's proportions

**Status: COMPLETE (26 Aug 2026).** Raised by Lucas against a screenshot of the map reading,
zoomed in: *"the map is VERY crude and doesn't take well to zooming in since the resolution
does not scale up as you zoom in"*, with three affordances asked for in the same breath — a
button to make the atlas temporarily full screen, collapse/expand on both the rail and the
left navigation, and windows adjustable by pulling at the margins. All four are built.

**The crudeness was two defects wearing one symptom.** The first was not resolution at all:
`vectorEffect="non-scaling-stroke"` was set on the `<g>` wrapping the land paths and on the
`<g>` wrapping the lineage arcs, and **`vector-effect` is not an inherited property** — so a
`strokeWidth` of 0.7 was 0.7 DEGREES of ink and an arc's 1.5 was about a hundred miles. At the
home view that is two or three pixels and looks deliberate; at the six degrees the old `MIN_W`
allowed it is a seventy-pixel shoreline, which is the band in the screenshot. Third instance in
this codebase of a per-element SVG property set somewhere it does not reach, so the e2e walk
asserts the general form rather than the case. The second was real: one outline —
Natural Earth 110m at 0.55° of simplification, 888 points — held at every scale. There are
three now (`workbench/scripts/make_coastlines.py`, `surfaces/phylo/coastTiers.js`): coarse
110m eagerly, medium 50m below 70° of longitude, fine 10m below 16°, the finer two as dynamic
imports so a reader who never zooms never pays for them. **The honesty the tiers needed:** while
a finer tier is in flight, or if it failed, the legend says what is on the plate rather than
letting a facet pass for a shore. `MIN_W` is 3° because that is what 10m data can honestly
carry. Rings are culled by generated bounding boxes, the graticule steps with the scale, and
the wheel handler is native and non-passive (React's passive `onWheel` meant the page scrolled
while the map zoomed).

**The shell:** `state/layout.js`, a fifth external store — pane width and fold per pane, in
localStorage, deliberately not in the URL. **Eight panes**: the two rails, the Phylogeny's
record, and the five surface index panels that were fixed numbers in their own JSX (330, 340,
430, 250, 360), all wrapped by `components/PullPane.jsx`. The five pull but do not fold, and
`PANES.foldable` says so — folding is right for chrome and wrong for a subject; a Fault Corpus
with the fault list folded away is not a decluttered Fault Corpus, it is a broken one. Both
rails and the Phylogeny's record fold to a 26px spine (never to nothing — a fold whose opener is elsewhere is a trapdoor) and pull
(`components/Splitter.jsx`: a real `role="separator"`, pointer-captured, arrows to nudge, Home
to reset, ten pixels of grab over a one-pixel rule). Widths clamp on READ as well as on write,
so a width stored on a 2560px display cannot strand the nav on a laptop. `[` and `]` join the
key map with the reason written down. Full screen takes the masthead and both rails and asks
the browser for its own as well; `layout.full` is the one piece of layout state that is not
persisted, which is what "temporarily" means.

**Found while building:** the delta encoder dropped a separator that was only safe after a
number carrying a decimal point, which would have shipped a displaced coastline — caught by a
test that parses the deltas back rather than pattern-matching the bytes; the graticule's step
rule shipped inverted inside this package and drew no lines at all at the zooms just made
reachable — caught by a browser probe counting elements, and pinned now; the map's legend was
taking 395px of an 860px window, so the drawing got less than half its own surface.

**Then audited adversarially, and the audit is the more useful half.** Four independent
read-only passes -- edge cases, test meaningfulness, second-order risk, second occurrences of
each fixed pattern -- plus browser probes. **Eleven of the package's forty-three new
assertions passed on the code they were written to guard.** Six findings blocked deployment
and all six are fixed: the guard against the headline `vector-effect` bug could not detect
it (it filtered on an attribute the bug's own shape does not carry, so reverting the fix left
it green); `Splitter`'s keyboard support was written, documented in three places and never
attached; the atlas culled land and cut the graticule to the viewBox while the SVG painted
27.8 degrees outside it, so South America vanished from the home view and a wheel zoom
drifted 3.12 degrees; a moment of a narrow window permanently destroyed every stored pane
width; below 900px the two rails ate the whole window and the canvas was zero pixels wide;
and below 900px every resize event wrote localStorage and re-rendered the shell for no
change. The three unit suites were rewritten against a mutation harness rather than re-read
-- the fine coastline tier could be replaced wholesale by the coarse tier with all 36 tests
green -- and rewriting one of them found a real bug in the shipped code: the graticule's
"does not drift" rounding recovers the right multiple and then puts the error straight back,
because `3 * 0.2` is 0.6000000000000001.

Report: `docs/reports/wp-5.7-the-atlas-and-the-shell.md` (§ the adversarial audit) · new open
question: OQ 72.

**Depends on:** WP-5.2, WP-5.6. **Size:** medium.
A structured transcription form (HTML) that produces a plan record from a drawing by tracing, and a DXF importer that reads a drafter's plan into a record. This is what lets HABS drawings, the reference corpus, and a builder's back catalogue flow into the critic.

---

---

## Phase 6 — Plan semantics

*Goal: a plan that MEANS something. Raised by Lucas on 26 August 2026 against two rendered
Tidewater sheets, in the project's own founding terms: "the Chomsky error of colorless green
ideas sleeping furiously is still very much in play." A kitchen whose only door was to the
outside; a stair hall with no stair; a rear door drawn as a window; door sizes with no rhyme
or reason; triangular arrows pointing at everything; a chamber bath with no access; a passage
grossly oversized; no furniture anywhere. Every part individually well-formed, the whole
meaningless — which is the exact failure this corpus exists to catch in other people's work.*

### WP-6.1 Drawing honesty

**Status: COMPLETE (26 Aug 2026).** The sheet stops lying about the record it renders. Doors
are drawn as the KIND of opening the record says they are (`type` was read by nothing, so a
pair of leaves and a cased opening both drew as one giant hinged leaf); a door is measured
against its own leaf and jambs rather than a flat 3.2 ft, so a closet door draws (the renderer
half of OQ 41/63); `render_plan.py` draws exterior doors, which it never had; windows are laid
into the run the doors leave, ending the collisions that drew the front and back doors as
windows; every opening that cannot be drawn is NAMED with its reason on the sheet, in the DXF
exporter's own words; the △ relaxation mark has a legend; a room drawn off its declaration is
marked and counted; and the plate title stops folding into a different house's name. The
durable half is `tests/fixtures/sheet_symbols/`, a frozen contract both renderers are held to
by two suites at once. Three false claims in the tree were corrected in place — the stair term
`geometry.py` and `docs/geometry.md` both advertised does not exist, and `check_partis.py`
claimed a reachability check the validator did not have.
Report: `docs/reports/wp-6.1-sheet-honesty.md`.

### WP-6.2 Opening semantics

**Status: COMPLETE (26 Aug 2026).** A door becomes a thing with a place. **Plan schema 0.3.0**
admits the placed plan as a record — until then `additionalProperties: false` forbade
`geometry` at the root, so a placed plan could not validate against its own schema and the
placement travelled out-of-band, which is why nothing checked it. Openings gain a wall, a
position, a hand, a leaf height and a rank; rooms gain a fixture layout; the plan gains a
stair. **`openings/grammar.json`** (editorial by ruling, 30 rules, every one quoting the corpus
prose it reads and every quote verified by `build/check_openings.py`) says which kind of
opening belongs between which two rooms. **`build/openings.py`** places them, called once from
`geometry.solve()` so both engines agree, and marks what it cannot place rather than deleting
it. **`compose.py`** derives door widths, types, ranks and heights and window widths and counts
from packs and kits that have always held them and were never read. **`plan_check` gains a
`drawn` layer** — the only layer that reads placement, three-state throughout — which reopens
OQ 54 on Lucas's ruling and turns every one of the reported symptoms into a finding.
Report: `docs/reports/wp-6.2-opening-semantics.md` · new open questions: OQ 91–81 (issued as 72–75).

### WP-6.3 Geometry truth

**Status: COMPLETE (27 Aug 2026) — one of the four planned changes was built and three were
REFUSED on measured evidence, one of them because the defect it proposed to fix does not
exist.** The package text below is left as written; what follows is what happened to it.

**Built: the per-pair door floor**, closing OQ 41/63 from the solver side. The old rule
demanded a flat 4 ft of shared wall for every interior door — its "programme-scaled" branch,
which the comment and OQ 41 itself both describe as protecting closets, **has never once
fired** (`maxside` is the LONGER side; 0 of 238 rooms in the corpus qualify). The floor is
now `openings.required_wall_ft` read from the record, in the model and in
`hard_fact_violations`, which had carried a second copy of the dead expression. **It fixed
the reported problem outright**: `tidewater-georgian-careful` had never been solved by
CP-SAT and now solves OPTIMAL, openings placed 20 → 30, doors with nowhere to go 11 → 1,
unreachable rooms 3 → 0, fatal findings 3 → 0. A stricter rule for most pairs made the model
easier, because the flat 4 ft had been asking a parlour's shared wall of every closet. Cost,
stated: 17 declared wall pins downgraded with refinements, relaxations 11 → 13. The
workbench and the Drawing Set stopped defaulting to the weaker engine — **the sheet that
started this whole program came from the fallback, and every access defect in it was an
artefact of that.**

**Refused: the stair-stacking charge** (inert at every weight — the generator is blind to
the other level, so the score can only re-rank blind candidates; 100x and 10,000x produce
byte-identical output. A hard CP constraint is worse: only wall pins are downgradable, so it
would outrank every authored exterior wall, and measured, it did). **The over-size penalty**
(an identity: because the slicer tiles exactly, an over-band charge IS an under-band charge
plus a constant — three formulations, not one room changed size; and over-size is already
billed symmetrically by `level_score`). **The `_absorb` keep-out for doors and stacks** (the
defect does not exist: `_absorb` only grows, so it cannot violate a lower bound; fuzzed over
4,000 layouts, worst shrink 0.014 ft against a 0.4 ft tolerance).

**Reported instead of charged**, which is where those refusals landed: `over_band` beside
`under_band`, carrying `declared_over_ceiling` so a room the BRIEF made oversized is not
blamed on the placement; and the drawn layer now checks every `stacks_over` claim rather
than only the stair. Two false claims corrected: `geometry_report.solver.hard` said "rooms
at program size" while `_absorb` licenses up to 2.27x, and the divergence threshold said
"more than a tenth" while testing `>=` (the kitchen and library land at exactly -10.00%).

**Found while verifying, and it is one of Lucas's own reported defects: the △ relaxation
marks were not over walls.** The CP counter emitted a line with no extent, refusing to
invent one — correct about the invention, wrong that there was nothing to measure, since it
was looping over the very rectangles whose faces lie on that line. Both renderers therefore
fell back to a tick at **the middle of the plan**, which on this placement put a mark inside
the drawing room six feet clear of any wall, over that room's own name. That is *"the arrows
over walls between spaces … they seem to point to anything and everything"*; WP-6.1 read it
as a missing legend and gave it one, which was owed and was the smaller half. The counter now
carries `runs` — the measured room faces on the line — and a mark it can locate on no wall of
its own level is named in the caption and not drawn. The dashed run was also swallowing the
click that selects the room under it, which had been misread as CP latency until it was
measured.

Report: `docs/reports/wp-6.3-geometry-truth.md` · closes OQ 41 · new open questions: OQ 95 (issued as 76)
(the generator is blind to the other level — the real home of the stacking fix) and OQ 96 (issued as 77)
(`_shared`'s first-match ordering can report a corner kiss as a shared edge).

**Depends on:** WP-6.2. **Size:** medium.

Make the placement honour what the record now says. The stair-stacking term that
`vertical_score` never had, as a real charge in the heuristic and a hard constraint in the CP
engine, reading the `stacks_over` neither engine has ever read. An over-size penalty and an
`over_band` report to match `under_band`, because the slicer tiles exactly and has no
over-size charge at all — the Tidewater upper passage is placed 63% over its declaration and
the linen press 303% over, in silence. `under_band` compared against the DECLARATION as well
as the catalogue floor, so a kitchen placed at 63% of its declared area is visible. The CP
door floor made the per-pair figure from the record's real widths, closing OQ 41/63 from the
solver side. And `_absorb` made unable to undo the guarantees the solve proved, per OQ 55's
precedent that a guarantee which does not survive the post-pass is not a guarantee.

---

## Phase 8 — The register, the backlog, and the scopes nothing reads

### WP-8.1 The register, the id, and OQ 90

**Status: COMPLETE (28 Aug 2026).** The open-question register is a directory —
`docs/open-questions/<nnn>-<slug>.md`, 98 files, filename == id — because that is the only shape
in which two parallel sessions cannot both issue id 99 and have git merge them without a word.
Four collisions in four days came from one habit (read the working tree, add one) and survived
because the register was ONE FILE: a text conflict, which git resolves by juxtaposition. Every
other id family here has been one record per file since the beginning, enforced by seven
checkers. **Open questions were the only ids kept in a shared file and the only ids that ever
collided.** The migration proved itself before writing anything — it reassembles the original
from the split pieces and round-tripped 291,341 characters identical.

**And nothing had ever checked for a duplicate id.** The derivation test parsed the register with
`re.findall` into a **set**, so two entries numbered 78 collapsed to one member and it stayed
green — the guard against the exact failure suffered four times could not see it.
`build/check_ids.py` now fails on a duplicate id, on a status word outside a named vocabulary,
on two reports sharing a slug, and on a `docs/reports/…md` path cited anywhere that does not
resolve (which found `wp-2.3-real-solver.md`, cited twice and never existing).
`build/gen_open_questions.py` generates the index; a CI step compares the branch's ids against
its base and fails the SECOND pull request to issue one, which is the only place the collision
was ever detectable before it cost a renumber.

**OQ 90 closed:** this branch's chain moved 5.7→5.11, 5.8→5.12, 5.9→5.13, 5.10→5.14; main's
atlas keeps 5.7. Its own preferred option — "cite the report, never the number" — was refused
because it was already false: two reports were both `…-the-four-rulings.md`. **§1 amended**: open
questions and work packages are on the never-reuse list, the merged-first rule is written down,
and so is the habit that caused all four.

Report: `docs/reports/wp-8.1-the-register-and-the-id.md` · closes **OQ 90**.

**Depends on:** nothing. **Size:** small — and it ships FIRST, because every package after it
ends by appending an open question.

---

### WP-8.2 OQ 51's refusal half, and the meter that flattered

**Status: COMPLETE (28 Aug 2026) — the mechanism and the first pass; the backlog itself is
ongoing authoring.** A node may now DECLINE a proportion pack that reaches it by descent
(`declined_packs`, per node), with a reason and a verbatim quote from its own record, enforced in
`resolve_kit.resolve_packs` and validated in `check_pack_bindings.py` — including the lie-check
that a decline naming a pack which does not actually reach the node refuses nothing while reading
as an adjudicated refusal.

**THE METER WAS WRONG BY 27 IN THE FLATTERING DIRECTION AND WAS FIXED FIRST.**
`check_inheritance.measure()`'s ROLE loop lacked the `pack not in own_ids` guard its PACK loop
had, so 39 role gaps were attributed to a delivery `resolve_packs` can never make — the node
binds that pack itself at `chain[0]`, so the ancestor's copy is overridden and dead — and the
endorsement test then consulted the wrong pack's `applies_to`, which usually named the node
precisely because the node binds it. **role_gaps 293 → 287, unendorsed 222 → 249, endorsed
71 → 38.** Its RATCHET was also stale-high at 294/3367 against a live 293/3366, and its own
comment claimed the test imported it while the test restated a literal.

**THE PER-EDGE DENY WAS DESIGNED AND REFUSED**, on the measurement that was supposed to justify
it: `english-georgian`'s fifty gaps are **five direct** and forty-five transitive, so there is no
edge to write the refusal on; a subtree deny there would touch 26 receivers to fix 18 with seven
of eight collateral already endorsed, five by the pass that raised the proposal; and
`_cascade_scope` is node-local anyway.

**TEN DECLINES, AND `unendorsed` DID NOT MOVE ONCE** — 249 before and after. Four single-storey
types refuse `storey-graduation`; six Gothic, Tudor and Arts-and-Crafts nodes refuse
`chambers-ionic` on their own words (*"Classical apparatus … is forbidden throughout"*, *"No
classical module"*, *"everything projects less than about two inches"*). `inherited_packs`
3,366 → 3,356, `judged` 38 → 48. Each role re-attributed to the next unjudged ancestor. So the
meter gained a FLOOR — `judged` may only rise — and `unendorsed` is a work list, not a score.
`jacobethan-revival` was deliberately left: *"no classical order except at the entrance porch"*.

**RAISED: `oq/forbidden-stops-the-pack-cascade`**, and it is larger than the backlog beside it. **776 (node, slot) pairs where the
resolved kit binds a slot `forbidden` and a pack dimensions it anyway**, over 118 of 132 nodes,
**776 of 776 by precedence and not one chosen by a human**. Declining does not close it. Ratcheted
apart; fixing it changes dimensions on 118 nodes and is its own package.

Tooling: `--ancestors` (with the DIRECT column that refused the edge mechanism), `--full`,
`--gates` (endorsing is a code change with no diff — the 26 Aug pass armed `graduation_check` on
eleven styles and said so nowhere), `--impact`, `--forbidden`.

Report: `docs/reports/wp-8.2-the-refusal-half.md` · new open question: **`oq/forbidden-stops-the-pack-cascade`**.

**Depends on:** WP-8.1. **Size:** medium.

---

### WP-8.7 The adjudication backlog, first pass (OQ 51)

**Status: THE BACKLOG IS READ (2 Sep 2026). 244 of 244 gaps adjudicated; 117 judged into the corpus,
152 put to a ruling, 73 newly surfaced and named as unread. `judged` 48 → 155.** Every (node, pack)
pair visible when the package started has been read by an agent against the pack's own stated
subject and the node's own record, and **every proposed data change was put to an independent
adversarial check first — which overturned 21 of them, one in five**. 114 declines and 3
endorsements are in the corpus, each decline quoting the node's own file verbatim. No gate pack was
endorsed into, so nothing generated changed. The product is
`oq/the-adjudication-cases-the-records-do-not-decide`: 152 cases grouped by the pack that settles
them all at once, gated packs marked, plus a separately headed list of the 73 pairs the package's
own declines created and nobody has read — because reading 244 gaps produced 73 more, which is the
refill at full scale. **The opt-in flip is NOT taken**: `unendorsed` is 227, nowhere near zero, and
`oq/a-node-that-refuses-a-category-must-decline-it-twenty-six-times` asks whether the loop is the
right shape at all. Two costs are recorded rather than buried: `baked_vs_refused` went 32 → 65
because roughly one decline in five is half-defeated by an ancestor's authored snapshot, and a
decline can hand a slot to a pack that suits the node worse.

**Status (first pass, 2 Sep 2026) — the tooling, fifteen declines, and the finding that
changes how the rest should be planned.** OQ 51 is ruled *adjudicate first, flip second*, and
WP-8.2 built the refusal mechanism. This package worked the backlog for the first time and found
that **it refills as it is worked**: `resolve_packs` fills a role from the nearest ancestor that
binds one, so declining that pack re-attributes the role to the next ancestor rather than closing
it. Fifteen declines moved `unendorsed` 249 → 245 and `judged` 48 → 63. Simulated to fixpoint,
`appalachian-log-house` needs **26 declines over 9 rounds** — five classical orders, a Gothic
pointed-arch pack, a Mudejar corbel course and an Iberian arcade, all arriving at a single-pen log
cabin whose record says an applied proportional system falsifies the type. **249 is what is
visible, not what is required**; eighteen nodes carry a comparable blanket refusal covering 60 of
it, which at that rate is ~470 declines to settle under a quarter of the backlog. Raised as
`oq/a-node-that-refuses-a-category-must-decline-it-twenty-six-times`, because for a node that takes
NONE of what the cascade sends, the adjudication and the opt-in flip reach the same end state.
Built: **`--pair NODE PACK`**, which puts the pack's own stated subject beside the node's own words
and ends in the `--impact` report, and `governed()` hoisted to module scope so it is read rather
than restated. The bar held: **`sash-light` was NOT declined** on either log node, because its
subject is glazing supply rather than a proportional system, and a decline there would have been an
editorial call wearing a `node-record` basis. No endorsements — a property of the two nodes chosen,
not a policy. Report: `docs/reports/wp-8.7-the-backlog-that-refills.md`.

**Depends on:** WP-8.2. **Size:** the first pass is small; the backlog behind it is not.

---

### WP-8.11 The second flip, and the fixture that would have gone quiet (OQ 51)

**Status: COMPLETE, 3 September 2026.** Report:
`docs/reports/wp-8.11-the-second-flip-and-the-fixture-that-would-have-gone-quiet.md`.

Closes `oq/a-pack-can-be-the-only-writer-a-node-has` on Lucas's ruling — no new rule, stage by
size — and flips `facade-gable`: two opt-ins, **32 slots over 29 nodes**, of which 29 are
`cornice_return`, the pack being its only writer in the corpus. That is the ruling exercised.

**The finding is about tests.** Both suites drove the gate through `facade-gable` *because* the
corpus left it on `cascade`; flipping it for real would have made every assertion a statement
about the shipped corpus — green, and vacuous. Both fixtures moved to `trim-craftsman`, and the
rule is now in their docstrings: **a driven fixture must name a pack nobody has flipped.** Check
it before flipping `sash-light`.

Also: a scoping defect WP-8.10 shipped (`--stranding <pack>` counted slots per pack and nodes
corpus-wide), and the refill measured a second time — 4 gaps from a 10-slot flip, **13 from a
32-slot one**, three of them promoting a live-gate pack.

### WP-8.10 The first flip, and the loud stranding it required (OQ 51)

**Status: COMPLETE, 3 September 2026.** Report:
`docs/reports/wp-8.10-the-flip-that-was-sold-on-the-wrong-count.md` · new question:
`oq/a-pack-can-be-the-only-writer-a-node-has`.

OQ 51's ruling of 3 Sep requires the flip to strand LOUDLY. WP-8.9 shipped the mechanism and not
that, so a gated pack produced no row and the address returned a bare absence — a slot reading
UNDIMENSIONED where it should read REFUSED, which is OQ 51's own corruption arriving from the
other direction. Built on WP-8.3's precedent in its own words (THE REFUSED RULE IS MARKED, NOT
DELETED): `withheld_for()` mirrors `refusals_for`, `eval_packs(withheld=)` marks the rules, and
`choose_pack` returns `how: "opt-in.withheld"` — **after** `kit.forbidden`, an order fixed by
measurement rather than taste.

Then the flip: six vouched-by-descent nodes opt in, `trim-classical` declares `delivery: opt-in`,
**10 slots over 10 nodes** lose their dimensioning. Ratchets 264/3158/223 → 258/3123/217 with
`judged` unmoved at 249 — the ceilings falling because deliveries stopped, not because anything
was adjudicated, which is the first real test of the floor WP-8.2 added for exactly that.

**Do not flip a second pack before `oq/a-pack-can-be-the-only-writer-a-node-has` is ruled.**

### WP-8.3 The forbidden slot (`oq/forbidden-stops-the-pack-cascade`)

**Status: COMPLETE (28 Aug 2026), with one half deliberately open and named.** `docs/inheritance.md`'s
binding table has said `forbidden` "stops the cascade" from the beginning. It stopped the KIT
cascade and never the PACK cascade: **776 (node, slot) pairs over 118 of 132 nodes** carried a
pack-supplied dimension for a slot the resolved kit prohibits, **and not one of the 776 was
chosen by a human** — every one by an ancestor's precedence number, no slot carrying a `packs`
ruling. `carpenter-gothic`'s record says *"No pilaster order."* and it published a pilaster width.

**Ruled absolute, with a human override** (the slot's own `packs` block, which `choose_pack`
already calls "the only place a human has said which pack wins"). Zero of the 776 qualify, so the
override strands nothing — stated, and held to the data by a test. **The refused rule is MARKED,
not deleted**: deleting would destroy the measurement itself, and `check_addresses` reads these
rows without ever calling `choose_pack`. `eval_packs`' `kit` argument is **required with no
default**, because a default would let every call site skip the gate by saying nothing.

**THE FINDING: a second path from packs to output that no plan had named.** `build/elevation.py`
never calls `resolve_packs` or `eval_packs` — it reaches packs by `PE.resolve` and reads sixteen
slots straight out of the files, so it is blind to bindings, scopes, declines and `forbidden`,
and the resolver gate reaches **no figure it draws**. Swept over every style: 40 pass its own
scope gate, 15 forbid a slot it reads, **40 (style, slot) pairs**. **16 refused**
(`transom_sidelight` 8, `pilaster` 8 — absent now, not zero). **24 read anyway and DISCLOSED**
in `forbidden_slots_read_from_packs` (`frieze` 9, `belt_course` 6, `water_table` 6, three
singletons): a style whose kit forbids `frieze` while passing a CLASSICAL scope gate is two
records contradicting each other, and zeroing it would pick a winner nobody has chosen. Visible
on a shipped plan at once — `spec-builder-colonial` forbids `transom_sidelight`.

**Found on the way:** the meter counted slots carrying no figure as dimensioned.
`--slots carpenter-gothic` said 75 and now says 64 plus 11 named as refused; `ranch-style` 78/69
became 67/60.

Report: `docs/reports/wp-8.3-the-forbidden-slot.md` · closes **`oq/forbidden-stops-the-pack-cascade`** (drawn half named).

**Depends on:** WP-8.2. **Size:** medium.

---

### WP-8.4 The exception precondition, the construction vocabulary, and the collision with main

**Status: COMPLETE (28 Aug 2026).**

An exception is a LICENCE, and where it carries a `bounds_test` it REPLACES the fault's
primary test. **331 of 846 exceptions carry a precondition on the wall, the roof or the date,
and all three of `core.py`'s selection sites matched on `e["style"] == style` and nothing
else.** `architrave-that-is-not-there`'s Pueblo Revival licence, written for adobe, was
excusing a house whose style resolves canonically to stucco-over-wood-frame.

**Why nobody had read it:** `schema/fault.schema.json` carried TWO fields called
`applies_when` meaning different things — one a precondition on MEASUREMENTS, evaluated since
WP-5.13; one on CONTEXT, evaluated by nothing. The unread one is `granted_when` now, on all 331
records, and `check_faults.py` errors on the old name.

**`build/construction_vocabulary.py` is a mapping table, not an ontology.** 78 tokens were in
use, spelling load-bearing masonry five ways, barrel tile four and wood shingle three. 61 map
onto variant ids that ALREADY EXIST in `kits/`; 17 are recorded UNMAPPABLE with a reason. No
new corpus id is authored on the authority of fault-exception prose. Three rules earned their
place by being wrong first: **slot order is authority order** (a render is not a wall), **a
canonical outranks a permitted** (`jeffersonian-classicism` is canonically brick with clapboard
forbidden, and a permitted `beaded-clapboard` was leaving it undecided), and **a `partial`
token may fail but never hold** (nothing records how thick a stucco is).

**Three verdicts, and the unjudged case is judged BOTH WAYS and compared.** Where the
exception's own numbers and the general rule agree, the unresolved question is immaterial and
the fault is answered; only where they disagree is it could-not-evaluate. Over 164 styles that
is 11 verdicts moving instead of 26.

**THE COLLISION.** Main shipped its own OQ 88 answer (`scope`, decided in
`proportion_engine.rule_scope()`), its own OQ 99 and its own WP-8.1 while this was being
written. **Ruled: main's field survives, this vocabulary is ported into it.** The port is not
cosmetic — main's `construction_of()` classified a node by SUBSTRING MATCH over its cladding
ids and disagreed with each node's own `construction_type` on **13 of 164 styles, in both
directions**. `cape-dutch` is sun-dried brick with timber frame FORBIDDEN and a
`lime-plaster-limewash-white` face carrying no masonry word, so the frame-wall sill rule was
delivered to a mass masonry wall: **OQ 88's own bug surviving inside OQ 88's fix.**

**Also closed:** **OQ 86** — `kit_vs_pack` read `load_kit(nid)`, the node's own file, while
comparing against cascade-assembled rules; reading the cascade takes 62 to **1,231** at 37
distinct addresses. **OQ 90** — at its third option: a work-package number is a LABEL, cite the
report; renumbering a second time touches 199 references and would make the reports disagree
with commit messages that cannot be rewritten. **OQ 89's remainder** — `elevation.py` read
`shutter` and `window_head_masonry` off the RAW kit, under a comment that named `shutter` as
binding empty *"exactly as"* the cascaded dormer slot. `jeffersonian-classicism` was still
clearing `shutter-on-an-unshutterable-opening` on two invented shutters, and
`window_head_masonry` is empty in the raw kit on 66 of 164 styles, so the head radius reached 8
styles where it now reaches 29.

**Found and not fixed, each with a meter:** a pack value BAKED into a kit as `kind: derived` is
a second delivery path no scope reaches (3,176 resolve, **20** deliver a figure the live rule
refuses); `applies_when` still means two things across three schemas, and the kit one is itself
half-read; eight exceptions carry a `construction:`/`region:` pseudo-style id no selection site
can ever match; nine nodes state their construction in prose with an empty variant list, every
one of them a family whose identity IS its construction.

`build/check_division_guards.py` is new: every dividing test against every measurement a
generator supplies as ZERO, swept over all 164 styles. **306 unguarded dividing tests, of which
0 divide by a name that can actually be zero** — pinned there, because that number goes
non-zero the moment a generator states a new zero, which is exactly what WP-5.13 did.

Report: `docs/reports/wp-8.4-the-exception-precondition.md` · new questions:
`oq/applies-when-means-two-things`, `oq/a-baked-pack-value-is-a-second-delivery-path`.

**Depends on:** WP-8.3, and a merge of main. **Size:** large.

---

# PHASE 9 RAN TWICE, IN PARALLEL, AND BOTH LINES ARE REAL

**Two sessions each opened a Phase 9 on 1 September 2026 and each numbered from 9.1. Neither is
a draft of the other and neither is renumbered.** One is ARRANGEMENT — the arbiter, the
precedents, the unit of composition — raised by Lucas against a rendered sheet. The other is THE
CRITIQUE AND THE CORRECTIVE REVISIONS — the analyst, the move registry, the revision loop —
asked for by Lucas the same day. They met at the merge of PR #19 and PR #20.

**So there are two WP-9.1s, two WP-9.2s, two WP-9.3s and two WP-9.4s.** That is `OQ 90` at four
times the scale it was recorded at, and its ruling stands and is the only thing that makes this
navigable: **cite the report by FILENAME and never the bare number.** All eleven Phase 9 reports
carry distinct slugs and coexist in `docs/reports/`, which is why nothing had to be renamed:

| number | arrangement line | critique line |
|---|---|---|
| 9.1 | `wp-9.1-the-arbiter-for-arrangement.md` | `wp-9.1-the-critique.md` |
| 9.2 | `wp-9.2-the-parti-is-not-the-type.md`, `wp-9.2-what-the-tradition-actually-does.md` | `wp-9.2-the-corrective-revisions.md` |
| 9.3 | (no report — part built) | `wp-9.3-the-revision-surfaces.md` |
| 9.4 | `wp-9.4-the-unit-was-not-the-problem.md` | `wp-9.4-the-things-the-reports-said-were-checked.md` |
| 9.5-9.7 | `wp-9.5-…`, `wp-9.6-…`, `wp-9.7-…` | — |

**Renumbering was not available and the reason is the one OQ 90 records**: pushed commit
subjects on both branches name these numbers and cannot be rewritten. A bare "WP-9.2" in this
repository's history is ambiguous BY BRANCH, exactly as a bare "OQ 78" became ambiguous by date.
**The two lines also met in the code**, and that merge is recorded where it happened rather than
here: `plan_check`'s findings carry the critique line's structured evidence AND the arrangement
line's shape and furniture checks; `compose.repair` is the critique line's revision loop, and
the arrangement line's style-layer passage-floor branch was PORTED into the move registry as
`passage-to-the-styles-own-floor` rather than dropped with the function that held it.

## Phase 9 — Arrangement

*Raised by Lucas on 1 September 2026 against a rendered sheet of `tidewater-georgian-careful`:
a 10 x 30 ft kitchen, a 27 x 7 ft breakfast room, an entrance portico off the axis of the
passage it serves, a dining room landlocked in the middle of the house, a stair in the corner
of a misshapen hall. His diagnosis: "it's still being procedurally generated at a lower level
than the idiom … the unit of room organization is already established, and you're playing with
units at a higher level of sense-making." The founding failure mode, one level above Phase 6:
that phase made the sheet honest about the placement and gave the record a vocabulary for an
OPENING. Nobody ever gave the record, the critic or the solver one for ARRANGEMENT.*

**Lucas's rulings at planning (1 Sep 2026):** the arbiter is built first and the precedents run
beside it; HABS sheet images are curated here as a URL list and **downloaded by Lucas** into the
repo (the proxy still answers 403 to CONNECT for `www.loc.gov`, re-verified 1 Sep; the Tavily
tier reaches the survey records and the written-data PDFs but cannot deliver a sheet into this
container); and **grouping-as-unit composition is BUILT this phase rather than deferred** —
"the smaller fixes treat symptoms and this is the disease."

### WP-9.1 The arbiter for arrangement
**Status: COMPLETE (1 Sep 2026).** Report:
`docs/reports/wp-9.1-the-arbiter-for-arrangement.md`.
`build/arrangement.py`, new, in two halves because OQ 54's reversal has a boundary: `declared()`
is geometry-blind and feeds the fault layer; the drawn checks and `grouping_vars()` read the
placement, which only the `drawn` layer may do. A fault is evaluated in exactly one of them.
**Twenty-seven of the twenty-eight plan-measurable faults were UNJUDGED** on this corpus's own
most carefully authored plan, because nothing had ever supplied a plan-arrangement variable.
**Six of Lucas's seven complaints are now named**; the passage's size is the seventh and the
corpus declines to call it a fault, which is stated rather than papered over. **The arbiter
found a real defect on its first run and the package had to fix the generator to ship**:
supplying `passage_clear_width_ft` armed `passage-that-is-a-corridor` -- fatal for a formal
centre-passage style -- on a composer that had been sizing this brief's passage at 7.9 ft for
three phases, which disqualified all three NATIVE partis and returned a side-hall townhouse for
a Tidewater Georgian brief. The formal floor is stated in the fault, the grouping and the
style's own cascaded kit ([10, 14] ft); only the room catalogue's vernacular 6 ft had a reader. Four findings worth
carrying: a plant-room zero was BUILT, convicted both reference plans, and was withdrawn (the
catalogue has no room type for a plant room, so the fault is unjudgeable in both directions);
the first shape check convicted the GOOD reference plans and had to lose the direction the
corpus does not state; the entrance-axis check missed the very sheet that raised the package
because it compared against `max(leaf)` instead of the sum of the half-widths; and
`declared()` was reading `plan["footprint"]`, which the solver writes — a placement leak into
the geometry-blind layer, caught by the test written to pin the boundary. **The drawn passage
band lookup had been dead code since it was written** (`cp.get("rules")` against a record whose
key is `internal_rules`) and was never read, so it changed no verdict and nothing noticed for
three phases. New question: `oq/a-daily-route-is-an-editorial-model`. **It also executes OQ 94's
third branch** — the reference plan is now convicted of its own style's hard two-door passage
rule, un-exempted and with no second door authored. That wants a ruling.
**Depends on:** nothing. **Size:** medium.

### WP-9.2 The precedents
**Status: TEXT HALF DONE, IMAGE HALF STILL WAITING ON LUCAS'S DOWNLOAD.**
TWO reports: `docs/reports/wp-9.2-the-parti-is-not-the-type.md` (the measured half -- HABS written
data, the code, the furniture sweep) and `docs/reports/wp-9.2-what-the-tradition-actually-does.md`
(the study of the compositional literature, with an adversarial sourcing pass and ten questions
for Lucas at §7, none of them answered). The two were produced by different routes and agree where
they touch. `Plan Examples/HABS/WANTED.md` is the download list. The package text below is left as written.
What changed: **loc.gov is reachable through the Tavily MCP tier**, so the HABS *written
historical and descriptive data* — overall dimensions, room-by-room plan descriptions,
structural systems, fenestration counts — could be read now rather than after a download, for
the three exemplars `centre-passage-double-pile` itself names. The finding is that **the parti
asks a Georgian main block to hold twice the rooms any of its exemplars holds**, because six of
its eleven enclosed ground rooms are service and all three exemplars put their service in a
basement, an outbuilding or a wing. That reframes WP-9.3 and WP-9.4: the envelope the generator
produces has a CLEAR extent about 3 ft larger on each dimension than Gunston Hall's (60.0 x 40.0
of wall-less room rectangles against a 56.8 x 37.0 clear extent inside a 60'-10" x 40'-11½"
exterior foundation), and 9 to 14% more clear area, so nothing is wrong with the
footprint or the area, and no score term can undo a program that does not fit the type. **Six** open questions raised (an earlier version of this block named three): `oq/the-parti-dissolved-its-own-dependencies`,
`oq/a-massing-states-its-structure-and-nothing-reads-it`,
`oq/the-passage-is-divided-and-the-corpus-has-no-word-for-it`,
`oq/the-proportion-band-forbids-the-square`, and from the adversarial audit
`oq/a-grouping-rule-and-a-room-record-can-disagree` and
`oq/a-slug-in-a-code-span-is-not-checked`. Lucas ruled a seventh on 1 Sep,
`oq/register-is-not-style` — register is a first-class axis, not style. **Still not done:** no sheet
transcribed, `plans/precedents/` does not exist, no band changed, no parti edited — the first
of those three questions is Lucas's to rule before any of it.

Real period plans, measured, under the partis' own exemplar names
(Drayton Hall, Gunston Hall, Hammond-Harwood, Mount Airy, Shirley, Westover). The 14 "reference
plans" are transcriptions of MODERN plan-book screenshots and there is no period building
anywhere in `plans/`; the asset manifest holds 1,850 records and **zero of kind `plan` or
`measured-drawing`** though the schema allows both. Curate the HABS survey and sheet URLs via
Tavily under `build/harvest_habs.py`'s own selection policy, write the wanted-list for Lucas to
download, transcribe 5-10 centre-passage/Georgian plans into `plans/precedents/` by multimodal
reading with per-field confidence (the WP-2.1 precedent), and measure them with
`build/measure_precedents.py` into the corpus's first SOURCED arrangement dataset. **The
calibration run is the point**: the WP-9.1 critic over every precedent, and any conviction of a
period building is either a band corrected here or a conviction defended by name.
**Depends on:** WP-9.1 for the derivations; Lucas for the sheet images. **Size:** large.

### WP-9.3 The record heard
**Status: PART BUILT. Item (a) SHIPPED in WP-9.6 and item (b) was WITHDRAWN there; what remains
unbuilt is the passage-width clamp and the arrival-aware stair at the foot of this section, and
`min_passage_width` still has zero readers in Python. This line read "NOT STARTED" until 2 Sep
2026 while the body below it already recorded both the build and the withdrawal — a status line
disagreeing with its own section, which is "until X lands is a lie the moment X lands" (WP-6.4)
in the file that tracks the work. Two furniture defects were found by WP-9.2 and belong here,
ahead of any score term, because both are deterministic and both make the critic honest rather
than changing what it wants.** (a) **The furniture layer never sees the drawing.** `plan_check.py:1250-1288`
reads `r["width_ft"]`/`r["length_ft"]` — the DECLARED record — so `breakfast`, declared 12 x 14
and drawn 7.0 x 27.0, passes a check whose own arithmetic says it cannot hold its essential table
(needs 9.0 ft across, has 7.0). That is Lucas's second complaint, and the shortfall itself is never
stated -- the room draws other findings (all 20 such rooms do, and 7 draw a furniture finding about
a different item), so this is a missing FACT rather than an invisible room. Where the check does
fire it quotes the declared figure, so `cl3` reads "has 3 ft" against a rectangle drawn 2.0 ft
wide and every shortfall in the set is understated — the OQ 52 family. Re-run the SAME arithmetic
in the `drawn` layer (the only layer permitted to read placement, OQ 54): one function, two
callers, never a second transcription. **The `openings.required_wall_ft` precedent is about the
DISCIPLINE and not about the mechanism** — that rule is deliberately spelled three times
(`openings.py`, `render_plan.py`, `derive.js`), because one of them is JavaScript and the app
suite may import nothing, and `tests/fixtures/sheet_symbols/` holds all three to one contract so
that changing one fails two suites. Copy the discipline, not the copies: here both callers are
Python in `build/`, so a shared function is available and is the right form.
**Ratchet the DETERMINISTIC figures and name the engine.** The WP-9.2 audit found that the
originally published 133/50 are `engine="auto"` numbers that drift (130, 132, 133 on an unchanged
tree) because `auto` solves 15 of 16 plans with CP-SAT under a time budget. `engine="heuristic"`
gives **86 drawn fails and 25 rooms whose drawn shortfall is never stated**, identical on three
cold runs. Ratchet those, or pin
CP's budget and seed and prove stability first.
(b) **WITHDRAWN, AND THE WITHDRAWAL IS THE POINT (WP-9.6).** This item read "every furniture item
is assumed to rotate ... the kitchen island is turned sideways ... needs a typed field on the item,
AUTHORED". It was wrong: `sorted()` pairs the item's short side with the room's WIDTH and its long
side with the room's LENGTH, which is the paired-axis rule already present, and the island's long
axis fires at 13.0 ft on `bad-03` and `bad-04`. No typed field is wanted. **What was really wrong
was the `elif`** -- the long axis was tested only where the short axis had passed, dropping 41
declared and 15 drawn shortfalls; they are two independent checks now. The item survived three
audit passes because each one re-read the sentence; it died when someone ran the function. A whole-room furnishability test was
tried and REFUSED with its measurement: against-wall runs summed against the room perimeter flag
nothing (the kitchen's five appliances are 12.75 ft against an 80 ft perimeter), because perimeter
is not available wall; a real one needs the placed openings and belongs in the drawn layer.
`docs/reports/wp-9.2-the-parti-is-not-the-type.md` §8.

Deterministic first, no weights: the passage's width clamped to its own
`width_ft` band intersected with the CASCADED kit's `min_passage_width` (never the raw kit —
`oq/the-raw-kit-read`), and an arrival-aware stair, since `openings.stair_pass` anchors every
flight at the room rectangle's origin corner by construction and every stair in the corpus is
therefore in a corner. Then ONE score term, under the full WP-7.4 discipline: `level_score`'s
type-blind `(ar-2.6)*6` replaced by a charge against the room's own `proportion` band — it
currently fines the passage 8.9 points for being what it is and the 27 x 11 kitchen nothing.
Clear `_SOLVE_CACHE` between settings; sweep the whole range including zero and the extremes.
**Depends on:** WP-9.1. **Size:** medium.

### WP-9.4 The unit of composition
**Status: COMPLETE (1 Sep 2026), AND THE PACKAGE'S OWN PREMISE WAS REFUSED WITH ITS MEASUREMENT.** Report: `docs/reports/wp-9.4-the-unit-was-not-the-problem.md`. **This line read "NOT STARTED — the centrepiece" until 3 Sep 2026, above a report that had existed for two days, and a whole-project review then read this line instead of that report and recommended building the refused thing.** What the measurement found: `slice_rect`'s spanning branch ALREADY IS the centre-passage macro-move — 3,000 Tidewater candidates give two east/west signatures and 2,999 are the same one, so the quadrant assignment is not searched but fixed; what varies is the passage's position, which is load-bearing (the argmin sits five feet west of centre and the centre-line bucket is ~100 points worse); and a probe that stated the tree anyway took fatals 3 -> 8. Three of the package's four hypotheses died. Its largest finding is not about the tree at all: over 21 partis, fatals fall **123 -> 36** and unreachable rooms **121 -> 34** by changing nothing but the engine. The original package text is left below as written.
**Superseded by** the dependency work — `oq/the-parti-dissolved-its-own-dependencies`, ruled 2 Sep — which is where the real unit-of-composition question went.

*Original text:* A `parti_slice()` beside
`courtyard_slice()`, on that function's own precedent: the heuristic cannot find a ring, so the
ring is STATED as a guillotine tree rather than searched for. The same move one level up — the
grouping/parti structure states the macro-plan (passage slab, entry zone aligned by
construction, flanking pairs, service in the rear third or ell) and the 250 candidates vary only
within it. **Typed fields only**: parti `exterior_walls`/`function_class`/`level`, grouping
membership, massing `circulation` and `depth_rooms`. `attaches_to[].position` strings stay
unread — missing vocabulary is AUTHORED as a typed field with a basis, never parsed out of
prose. Opt-in per circulation family, with `check_partis` check 10 as the guard that the other
partis are untouched.
**Depends on:** WP-9.1, WP-9.3; calibrated by WP-9.2. **Size:** large.

### WP-9.5 The adversarial audit
**Status: COMPLETE, three passes, 1-2 Sep 2026 against WP-9.1 and WP-9.2.**
`docs/reports/wp-9.5-the-corrections-that-were-themselves-wrong.md`. **42 findings survived
verification, 10 blocking, every blocking one in this session's own work and four of them in
corrections it had ALREADY made** — a first fix that was itself wrong, or right in one file and
left wrong in another. (This line said "24 findings, 8 blocking, four of seven auditors still
reporting" until 2 Sep 2026, against a finished run and its own report's 42 and 10: a status
frozen at the moment it was written while the work went on underneath it. The 8 was WP-8.6's
figure, one package over.)
Highest-yield technique, stated for the next audit: **re-derive the number, do not re-read the
sentence.** Every blocking finding came from running something.
Chief among them: Hammond-Harwood's bay figure was low twice and correcting it moved a conclusion
(the parti's 9 ft is BELOW all three exemplars, not at the low end of their range); Morris turns
out to be Palladio at one remove, so two sources were being counted where there is one; the
headline furniture figure was `engine="auto"` and not reproducible (±3 between runs), and the
deterministic engine gives 86/25 — **and CP-SAT, the engine that proves, draws about 131
unfurnishable items where the search draws 86**; and "nothing else in the pipeline can make the
house bigger" was false, because `compose.repair()` widens a declared width on a furniture finding
— from the DECLARED record, so it never sees the room drawn as a sliver.
Two pre-existing gaps exposed and raised rather than patched:
`oq/a-grouping-rule-and-a-room-record-can-disagree` (five instances, one on the grouping 14 partis
carry) and `oq/a-slug-in-a-code-span-is-not-checked` (65% of the live namespace unguarded, and the
blind spot is load-bearing). Guards mutation-tested and ALIVE are listed too, because "the tests
pass" is not evidence.

The phase tradition (6.4, 7.5, 8.6). Read
`docs/reports/wp-8.6-the-guards-that-could-not-fire.md` first: hunt guards that cannot fire,
readers pointed at the wrong record, and verdicts claiming "no precondition" about records that
carry one. Mutate every new test, re-derive every published number on the current tree, sweep
the styles, and correct every comment the four packages made false in the same commit as the
finding.
**Depends on:** WP-9.1 through 9.4. **Size:** medium.

## Phase 9 — The critique and the corrective revisions

*Asked for by Lucas on 1 Sep 2026: "a critic or an analyst that, once the plan has been drawn,
assesses that layout, points out all of the issues and problems, and then the generator goes on
to fix those, both in plan and elevation … a great deal of corrective revisions and refinements
before the final product is arrived at." Rulings the same day: deterministic; dimensions,
declared choices, openings and rooms; on by default. Layer doc: `docs/revise.md`.*

### WP-9.1 The critique

**Status: COMPLETE (1 Sep 2026).** Report: `docs/reports/wp-9.1-the-critique.md`.

One building inside the critic (`plan_check.check` derives the elevation from the placement the
record carries, and says so; an elevation that cannot be derived is a named `info`, never
silence); the bench's evaluate judges the SOLVED record (the drawn layer had never run on a bench
evaluate); every finding carries the structured evidence a move needs beside its prose, never in
its id; `build/openings.py`'s refusals carry their figures as `needs`/`have`; plan schema 0.4.0;
`build/critique.py`, the analyst, with five classes; `build/critic_suspects.py` and
`check_critic_suspects.py`, the meter for the 35 literals and 4 ratios the elevation generator
states as its own measurements; `wing-pitch-drift`'s near-miss secondary guarded on the slope
count (−1 serious on each shipped plan, re-pinned). Two questions raised.

### WP-9.2 The moves and the loop

**Status: COMPLETE (1 Sep 2026).** Report: `docs/reports/wp-9.2-the-corrective-revisions.md`.

`moves/registry.json` (21 moves, 9 stated refusals, the ruled authority) and `build/moves.py`;
`build/check_moves.py`; `build/revise.py` — accept on strict improvement of `[fatal, serious,
minor, faults present]` with no new fatal, else roll back byte-identically, tabu, continue; the
proof first where it is to be had; `revision_report` on the record; the composer's `repair` is the
declared loop in its old position and the placed loop runs on the returned candidates by
default; `tdl_critique_plan` and `tdl_revise_plan` (24 → 26 tools); the corpus sweep.

### WP-9.3 The surfaces

**Status: COMPLETE (2 Sep 2026).** Report: `docs/reports/wp-9.3-the-revision-surfaces.md`.
`POST /api/plan/critique`, `POST /api/plan/revise` (a job on the compose pool, one `round`
event per round) and `GET /api/jobs/{id}/plan`; the Plan Workbench's critique and two revise
chips, the Revision panel, the engine and class tags on finding rows; the Candidate Set's
`revised` band and event; the e2e walk. Found on the way: the loop reported only two of its
four round-logging paths, the metered-tool pin was red wherever the MCP SDK exists, and the
`revised` event had been dropped on the floor since WP-9.2.

### WP-9.4 The adversarial audit

**Status: COMPLETE (2 Sep 2026).** Report: `docs/reports/wp-9.4-the-things-the-reports-said-were-checked.md`.
Three read-only explorers built the claim-to-guard matrix; three auditors in isolated
worktrees reverted each fix and watched the suites; every finding was reproduced before it was
fixed. Blocking: a parti RECORD reaching geometry unchecked on both new routes; a revise job
with no budget; the lever's verdict on the round rather than the move; `touches` a declaration
nothing enforced, with three moves writing outside it and one rewriting nine authored window
counts; the literal detector blind to five shapes (35 -> 44, 4 -> 7, re-baselined in public).
**Then a second pass over the audit itself** (2 Sep 2026, report §VIII): three more auditors
over the whole session's diff found the WP-9.4 guard blind four ways, a revised plan that
could not be read back from its own DXF, the MCP tools unbounded, and a compose submission
that could hold the one-worker pool for four hours. Fixed, each with the test that bites.

---

## Phase 10 — The second massing element

### WP-10.1 — the dependency, and the audit that withdrew it

**Status: COMPLETE, AND TWO OF ITS THREE PACKAGES WERE WITHDRAWN BY ITS OWN AUDIT (3 September
2026).** Report: `docs/reports/wp-10.1-the-audit-of-the-dependency.md` — cite the filename.

Raised from `docs/reports/project-review-2026-09-03.md` and from Lucas's four rulings of the same
day: a dependency is a second MASSING ELEMENT (OQ 40, not a second plan level); the hyphen is a
room chosen by style; every proportion floor goes to 1.0; correct the record first, then build.

**What shipped.** Package A, the review's own correction — the road recommended a package that had
already run and been refused, and §V drew a model-level conclusion from an engine-level artifact;
both are corrected in that review's §IX, with the two-engine table re-derived on `auto` here rather
than cited from another report. Package B, the 35 proportion floors and `UNBANDED_PROPORTION`.
Package C1, the block machinery: `blocks_for`, `blocks_record`, `exterior_score(bounds=)`,
per-block slicing, plan schema **0.5.0** (`block` on a room, `blocks` on a footprint), and both
shipped plans placing byte-identically through all of it.

**What was withdrawn, and why.** C2 (the six-room strip of `centre-passage-double-pile`) and C3
(the hyphen as a room, `stock_the_dependency`, the tagging) came out. The audit found eight
blocking defects, and five of them reduce to one fact: **six layers below the placer read the main
block as the whole building**, each wrong on a dependency room in its own direction. Patching them
is a package; shipping a dependency that six layers mis-measure is the thing this project exists to
stop. So the machinery stays, dormant — the composer writes no `block` on any room — and
`geometry_report.multi_element` DISCLOSES the six by name in the corpus's own COULD NOT EVALUATE
words, because a caller-supplied record is the only route in and its author is exactly the reader
who cannot know.

**Three findings worth carrying out of it**, all in CLAUDE.md's traps:
- **CP-SAT flattened the dependency and said nothing** — the garage placed at x = 50 of a 0–70
  block while `footprint.blocks` described an element at 84–114. It refuses now. **It also
  invalidated a number this session had published**: "CP-SAT proves the stripped house at 0 fatals"
  was measured while every room was crammed into one rectangle and therefore trivially reachable.
- **A value derived from a threshold and tested against it is un-failable, and `roof.py` has
  three.** `gambrel_break_check`'s was dismissed on a docstring and died on a run. Fixing it then
  printed FAIL for an unjudged verdict on two plates.
- **A mutation that changes nothing means the fixture is blind.** Four guards in this session could
  not fail; two of the four were written by the audit, inside the class that exists to catch that.

**What was deliberately not done.** The six layers are not taught about elements — that is
`oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it`, with the four things that
must be ruled first. `hyphen_length_ft` remains could-not-evaluate and C3's claim to have delivered
it is retracted. 21 HARD fault rules inert via prose `exceptions` (47 of 51 lists fully inert) is
recorded as pre-existing and at scale, and is not this package's.

## Phase 11 — The drawn sheet, and the house under it

*Raised 4 September 2026 by Lucas, against the rendered `tidewater-georgian-careful` sheet set
beside four exemplar plans (one pen-and-ink, three tan-poché). He asked for the diagnosis first and
for the directive second, and then ruled three things on it: the editorial furniture pass is in;
the programme covers BOTH the drawing and the placement under it; and the sheet has two registers.*

**The diagnosis splits the way WP-6.1's did, and that split is what makes a programme possible
rather than one enormous change.** Ten of the twenty-eight items are the PLACEMENT — the passage
west of centre, the kitchen "dependency" and back hall "hyphen" as rooms of one flat rectangle,
twenty-three of twenty-five rooms drawn at a size the record does not declare, nothing stacking,
the terrace never placed. Eighteen are the DRAWING — no poché, room washes doing the work walls
should do, windows as coloured bars, three typefaces, the diagnostics in the drawing field, no
border, no furniture, no chimneys, no steps, no compass, a scale bar of one line.

### WP-11.1 — the sheet in its own standard

**Status: COMPLETE (4 September 2026).** Report:
`docs/reports/wp-11.1-the-sheet-in-its-own-standard.md`. `build/sheet_style.py`, the wall as a
body, openings as holes, the two registers, the margin schedule, the ruled border, the compass
rose, the graphic scale, the bay grid extended past the walls, and room names in the standard's own
letterspaced capitals. New question: `oq/the-placement-carries-no-wall-bands`.

### WP-11.2 — the pen ladder, and the wall the record states

**Status: COMPLETE (4 September 2026).** Report:
`docs/reports/wp-11.2-the-pen-ladder-and-the-wall-the-record-states.md`. `sheet/pen.js` (19 inline
stroke widths in `Sheet.jsx` → 0, and the standard's five weights in use for the first time);
`build/assemblies.py`, a LEAF on `build/storeys.py`'s precedent, so the drawing can read the wall
without closing an import cycle through `structure.py`; `footprint.wall` on the record at plan
schema **0.5.1**, so both renderers read one number instead of two literals matching no assembly
in the catalogue. **The browser walk ran for the first time in a session on this branch** — green
pristine, red on the change, on a defect 81 unit tests and a clean build both missed. OQ 64 is
not closed and is made closable.

### The rest of the A line — the drawing
- **WP-11.3 — furniture. COMPLETE (4 Sep 2026).** `build/furniture.py` (a LEAF, holding the packer
  MOVED out of `fixture_pass` — fixture output byte-identical over all sixteen plans),
  `furniture/grammar.json`, `furniture/symbols.json`, `build/check_furniture.py`. **540 items
  placed, 125 refused with reasons, 216 skipped by kind; 181 rooms furnished where 5 had
  fixtures.** Every rule declares a GRADE — `reading` where the record gives both the rule and the
  figure, `editorial-from-prose` where it gives the rule in words, `editorial` where it says
  nothing — and three rules the corpus states in prose are named STATED AND NOT EXECUTED, which is
  where OQ 92 drew the line. `kind` authored on all 278 items and required by `check_rooms.py`, on
  `placement`'s own WP-7.2 precedent: **a regex over these strings is provably wrong in both
  directions**, and the sweep that proved it returned one hit, a false positive, while missing the
  real one. **The finding that names the report: `rooms/library.json` authored its table
  `against-wall` while its own note says the table is in the MIDDLE of a library and against a wall
  in a study, "and that difference is what distinguishes the two rooms"** — the study's answer, on
  the library's record. Corrected from that sentence, which moved the drawn-furniture ratchet
  86 → 88 with the placement byte-identical. The marks go ON THE RECORD (WP-6.2's rule a layer up),
  so both renderers draw and neither derives. Three defects the guards caught that reading did not:
  a piano arc that left its room 13 times in 1,078 marks while every item rectangle stayed inside,
  a desk drawn as a bed because "bedroom" contains "bed", and a refusal that did not name the rule
  refusing it. **Two of the package's own new guards could not fail and mutation found both.**
  Report: `docs/reports/wp-11.3-the-record-said-against-the-wall-and-its-own-note-said-otherwise.md`
  · new question: `oq/a-furniture-footprint-is-sometimes-one-and-sometimes-the-group`.
- **WP-11.4 — threshold and stacks. COMPLETE (4 Sep 2026).** `build/threshold.py`,
  `threshold/grammar.json`, `build/check_threshold.py`, plan schema **0.7.0**, checks 48 → **49**.
  The stoop's flight at the entrance door and the two gable-end stacks are drawn, in the wall's own
  poché, from the record and from nothing else. **The columns are REFUSED and that refusal is the
  package**: `portico_bays` resolves to 1 on `tidewater-georgian`, and the first clause of its own
  slot rule carries the condition — *"WHERE A PORTICO OCCURS it is one bay wide"* — which that node
  does not meet, its `porch_type` making `stoop-only` canonical and calling the entry portico
  ATYPICAL. Read literally, the instruction above puts a portico on **5 of the 8 nodes that resolve
  a `portico_bays`**, one of them a shipped reference plan. And on the 23 nodes where a portico IS
  canonical the column has no width: **exactly 1 node in 164 states a diameter in inches, and it
  states no bay count** — the intersection of the three facts a drawn column needs is EMPTY.
  **The stack's hardest question was answered by a different slot from the one it was asked of**:
  `chimney` makes both a paired-INTERIOR and an EXTERIOR gable-end stack canonical, and
  `hearth_position`'s own note says why it is the one to ask — *"the ontology separates the roof
  expression from the plan fact"*. `SIDE_OF` and `MASSING_HEARTH` are CLOSED tables proved total by
  the new checker, which **failed on its first run** on twelve massing values in a second
  vocabulary, seven of the forty massings stating a DISJUNCTION their own `hearth` field never
  resolves. Which rooms take a hearth is RAISED, not read. Two of the fourteen reference plans had
  been failing their own plan schema since OQ 55 and nothing had noticed. Report:
  `docs/reports/wp-11.4-the-parameter-whose-condition-nobody-read.md` · new questions:
  `oq/which-rooms-take-the-hearth`, `oq/a-child-band-replaces-an-ancestor-derivation`,
  `oq/the-massing-states-its-hearth-in-prose-and-a-substring-test-reads-it`.
- **WP-11.5 — the face. COMPLETE (5 Sep 2026).** `build/gen_sheet_font.py`, a committed subset
  under `assets/generated/`, and `sheet_style.font_face_rule()` / `face_status()` /
  `advance_widths()`. Graphic Standard No. 1 names one serif voice; every plate had asked for it
  in a stack and carried no font, so an exported SVG was set in Georgia and could not say so.
  **EB Garamond 1.003, printable ASCII plus a named extras list, 127 glyphs, 15,016 bytes WOFF /
  20,024 base64**, carried in each sheet's own `<style>` with the SIL OFL beside it — the
  Tidewater plate goes **43,141 → 63,555 bytes, +47%**, and that is the whole cost. The margin
  now prints `FACE EMBEDDED — EB GARAMOND VERSION 1.003 …`, or `FALLBACK` with the reason, which
  is what "the title block must say so" asked for. **The fitter measures the face it draws in
  for the first time**: `_adv` read a five-branch estimate — one number, 0.66 em, for every
  capital — against a face whose `I` is 0.34 and whose `W` is 0.916, and **34 room labels across
  10 of the 16 plans change size** on the real metrics. **THE ONE FINDING: `∗`, the divergence
  mark the sheet defines in its own margin, is in NEITHER face the sheet names** — not EB
  Garamond (2,091 cmap entries) and not Courier Prime (383) — and renders only because a browser
  falls past both stacks into a system font. Not changed, because the symbol is the standard's:
  `oq/the-divergence-mark-is-in-neither-face-the-sheet-names`. **`recalcTimestamp=False` is the
  whole of why the artefact can be verified**: fontTools writes the save time into `head.modified`
  by default, so two builds of one font differed and `--check` would have been a command that
  always says FAIL. Report: `docs/reports/wp-11.5-the-face-the-sheet-had-always-asked-for.md`.

### The B line — the house under the drawing

Three facts govern it, all measured and on record, and each is a reason a scoring change will not
work: **the declaration reaches both engines as a scalar AREA** (`level_score` reads `r["_area"]`;
CP's only hard side bound is `0.6 × declared short side`; `WIDTH_W` ships at 0.0 with a sweep behind
it); **CP's relaxation ladder harvests only `kind == "wall"`**, so any other hard fact is
unrelaxable by construction, and OQ 95's closure names the designed way past it — a downgradable pin
with its own `kind`, ranked below declared walls; and **on the Tidewater plan the CP objective
cannot reach the drawing at all**, because `_finish_feasible` keeps the unoptimised feasibility
placement. WP-9.4 §1 refused a stated tree that centred the passage, at 100 points and five fatals,
and that refusal is to be ANSWERED — the objective that priced it has no shape term and no axis
term — not stepped around.

- **WP-11.6 — the record says what it means. COMPLETE (5 Sep 2026).** `stacks_over` on the upper
  passage and the landing, which the parti declares and the plan does not; no engine change.
  *The two lines of JSON the package asked for are in, and reading the code before writing them
  turned up four findings.* **`stacks_over` had seven readers and four definitions of "below",
  and every one declined in silence** — the shipped Tidewater record's ground-level powder room
  naming a ground-level cellar stair was dropped by three of them with a bare `continue`, so the
  plan carried four claims of which three were judged and nothing said which three. Plan schema
  **0.8.0** splits the field's two duties: `stacks_over` is STRUCTURAL (one level below, judged
  by rectangle overlap), `wet_stack_with` SERVICING (any level, target need not be wet — a stack
  needs a chase and a stair shaft is one). `build/stacking.py` is the one spelling, a LEAF on
  `storeys.py`'s precedent because `geometry.py` loads `plan_check.py`; `geometry_report.stacking`
  carries `claims == kept + broken + unjudged` with a reason from a closed set on every unjudged
  entry; `build/check_stacking.py` is the 50th check. **Measured, `heuristic`: claims 3 → 5, kept
  1 → 3, serious 62 → 55, fatal 3 → 4, relaxations 7 → 9** — `geometry.bias()` reads the field to
  steer CANDIDATE GENERATION, so a record edit moves the placement with no engine change, and the
  upper floor stops being slivers (the landing 6.0 × 15.4 ft → 12.1 × 13.5). The new fatal is
  `unreachable: chamber3` and is **named, not absorbed** — clearing it means authoring a door
  from a bedroom into a closet. **On `auto` the claims buy nothing**: CP keeps hard-only phase A,
  its objective never runs, and 5 of 5 are broken — Part IV.B's fact (iii) measured on this plan
  for the first time, and the evidence WP-11.7 rests on. **The largest finding is not about
  stacking**: both engines place two levels, `bad-03` declares three, and its level-2 Gameroom
  came back with no geometry, no finding and no note while the sheet drew the house without its
  top floor. Disclosed on `multi_element`'s precedent — and writing that turned up a fifth:
  `multi_element_disclosure` was wired into `write_record` and not into `_finish`, so every
  CP-produced multi-element placement has shipped without it since OQ 40. Report:
  `docs/reports/wp-11.6-the-claim-nobody-could-judge.md` · new questions:
  `oq/the-placer-places-two-levels-and-says-nothing-about-the-third`,
  `oq/a-plan-does-not-name-the-parti-it-was-built-from`,
  `oq/the-frozen-fixture-is-regenerated-by-solving`.
- **WP-11.7 — the shape band and the ranked ladder. COMPLETE (5 Sep 2026).** Planned as per-room
  side bounds at an authored tolerance τ; **built as the room record's OWN `dimensions.proportion`
  band instead**, because the corpus already states the shape rule and τ would have been a number
  nobody could source — measured first, all 23 dimensioned rooms on the Tidewater record declare a
  shape INSIDE their own band, so the pin contradicts no authored record, and it is the band the
  drawn layer already convicts a room for leaving. **The band and the record's `exterior_walls`
  cannot both be hard**: with the band held and all 22 wall pins released the model is OPTIMAL,
  with the pins held it is INFEASIBLE at every footprint to ten bays, and the ladder gives up 14
  or 15 of the 15 shape pins at every coverage floor from 0.97 to 0.60 — so coverage and packing
  are not the blocker and `oq/the-placement-carries-no-wall-bands` is not what is in the way.
  **Ruled by Lucas: the band outranks the pins**, which is what CLAUDE.md has said since WP-2.2
  (*"exterior_walls are aspirations, not rectangle edges … do not promote them to constraints"*)
  and what this engine had never done. `_RANK = ("wall", "axis", "shape")`, released lowest
  first, whole rank at a round (the narrow version needs eight rounds and the intermediate states
  go UNKNOWN at any bench-sized budget; `_reinstate` wins back what holds). **Measured on `auto`:
  serious 79 → 56, stacks kept 0 → 3 of 5, every room inside its own band where the worst had
  been a 13 × 16 ft bedroom drawn 45 × 7, and the passage 22 × 19 → 9 × 40, spanning again.**
  `_absorb` had grown three rooms straight back out of the band CP had just proved — the third
  time that pass has undone a proof — and takes `ratios` now. **The axis pin states the spanning
  half and REFUSES the centring**: `2x + w == W` is INFEASIBLE in 0.9 s with every wall released,
  because the passage centred on a 60 ft front leaves two strips holding 2,000 sf of programme in
  1,992 sf of floor. Cost: `spec-builder-colonial` needs 29.6 s against a 25 s budget and falls
  back to the search, losing its proof —
  `oq/a-shipped-plan-needs-thirty-seconds-and-the-budget-is-twenty-five`. Report:
  `docs/reports/wp-11.7-the-band-the-corpus-already-stated.md`.
- **WP-11.8 — the heuristic follows. COMPLETE (5 Sep 2026).** It follows by RANKING, not by
  refusing: the proportion band a room's own record states is the FIRST key of the candidate
  acceptance and the score is the second. Ruled by Lucas over a sweep and a demotion. Measured
  first, and it is why rejection was never on the table: **zero of 250 candidates conform** on
  the Tidewater ground floor (the distribution runs 3 to 10 out of band, best 3), so "hard"
  cannot mean "refuse" in an engine with no conflict set. **The key counts the band in BOTH
  directions** — the proportion ceiling and the room's own area floor — and the second half was
  forced by a WP-7.4 guard rather than designed: ranked on the ceiling alone this took under-band
  rooms 15 → 21 and put `spec-builder-colonial`'s dining room back below its own floor, which is
  one term winning rather than the room's own record. Corpus-wide, `heuristic`: **rooms drawn
  outside their own band 77 of 219 → 30**, under their own floor 15 → **13**, serious 745 → 681,
  minor 1031 → 992, **fatal 113 → 136**. Every one of the twenty-three new fatals is
  `unreachable` — a squarer room shares less wall, so its declared doors lose their run — and
  **a door-seating count built to rank above the band, to protect the more serious fact, measured
  WORSE on every axis at once** (68 out of band, 131 fatal, 780 serious) because it is a proxy for
  the drawn layer's rule and not the rule; it was deleted rather than reported. **What settled the
  trade is the move registry**: all 81 `unreachable` fatals carry `adjacent_placed`, so
  `add-the-grammar-door` answers every one and the revision loop runs by default, while a room
  outside its band has NO move at all — 49 defects nothing can fix traded for 23 the loop is built
  to clear. `geometry_report.shape_band`
  discloses the residual from `_disclose`, so both engines report it. **The budget is split**
  (`BUDGET_BATCH_S = 40.0`, `BUDGET_INTERACTIVE_S = 25.0` passed by name by the bench evaluate
  and `place_plan`) and `spec-builder-colonial` is CP-solved again with 0 rooms outside its band.
  Pins: relaxations 9 → 8, furniture 86/70 → **65/65** — the first of that file's three moves
  that is an IMPROVEMENT, and it is Lucas's own Phase 9 complaint answered; rooms drawn a tenth or
  more off their declared area 164 → **148 of 231**. **The cost the critic cannot see**:
  over-capacity clear spans 13 → **25**, worst 40.0 → **60.0 ft**, relaxations 64 → 86 — a squarer
  room puts fewer cuts on the bay module, and cutting on it is the only way this slicer makes a
  bearing line. **The full suite refused the package seven times over two runs and not one was a
  pin to bump**: a furniture rectangle judged at full precision and
  written rounded (one drawn collision, latent since the pass was written), the WP-7.4 guard that
  forced the second half of the key, and three guards pinning an OUTCOME the placer is free to
  change (including two requiring `spec-builder-colonial` to flag an over-capacity span, which it
  no longer does) — each rewritten against the behaviour instead, with the capacity and the
  bearing tolerance untouched. Report:
  `docs/reports/wp-11.8-the-search-ranks-what-it-used-to-price.md` · closed:
  `oq/a-shipped-plan-needs-thirty-seconds-and-the-budget-is-twenty-five`,
  `oq/the-frozen-fixture-is-regenerated-by-solving`.
- **WP-11.9 — the dependency. COMPLETE (6 Sep 2026), and its last item REFUSED with a number.**
  All four rulings taken before any code (per-element envelope with the union beside it; the lot
  cap on the built extent, gap excluded; a hyphen is an element and abutment is a constraint;
  `touches` against the room's own element's face), then all six layers taught in the stated
  order with a measurement after each. `build/elements.py` is the one reader, a LEAF.
  **The whole shipped corpus is byte-identical** — placement, footprint, openings, fixtures,
  furniture and findings — because every plan here is one rectangle, and that is the guarantee
  the package is read against; `tests/test_elements.py` pins both digests. Measured on a
  hand-tagged Tidewater: outward openings placed on their own element's real faces **18 → 23**
  with refusals 11 → 6 (five authored windows recovered); exterior walls **4 → 12** on the ground
  and 4 upstairs; unsupported upper wall lines **20 → 27** on one record with only the instrument
  changed (seven had been credited to walls under no upper floor); built extent **97 → 77 ft**,
  because the main block had been sized for rooms that go in the dependency; rooms reaching no
  exterior wall **8 → 1**; one IFC slab per element per storey. **The abutment constraint is
  INERT on everything the placer produces and the test says so in its own name** — tried at five
  hyphen depths and on a composed five-part with five elements, the count is zero, because
  `blocks_for` clamps the hyphen's depth and centres all three on one axis. **The tags are NOT
  authored on the shipped record**, and the reason is one measured fact: tagging is now an
  improvement on every axis (fatal 9 → 6, serious 61 → 53, rooms out of band 6 → 2, where
  WP-10.1 measured the same tags trebling the fatals) but `engine="cp"` REFUSES a multi-element
  plan, so it would trade a proved reference plan for a searched one —
  `oq/the-proving-engine-cannot-place-a-second-massing-element`. Report:
  `docs/reports/wp-11.9-the-six-layers-that-read-one-rectangle.md`.
- **WP-11.10 — the terrace at grade. Status: COMPLETE (7 Sep 2026).** **The gate did not
  apply, and finding that out was the package's first act.** It was written here as gated on
  `oq/the-proving-engine-cannot-place-a-second-massing-element`, on the assumption stated in
  the plan file's Part IV.B5 that an at-grade unroofed thing on the wall of the room it serves
  is a third massing ROLE. The CP refusal keys on the room's `block` TAG (`geometry.py:2399`,
  `is_block_tag`), so a pass that writes no tag never reaches it. **Ruled 7 Sep 2026: an
  at-grade unroofed appendage is NOT a massing element** — it is a plan-level record on
  `plan.threshold`'s precedent, and the question stays open and untouched, still gating the
  shipped-record dependency tags. `build/appendages.py` is a LEAF taking `elements.py`'s two
  readers as arguments; it runs BEFORE the level loop, because `_place_interior` is the first
  pass in it and could not otherwise seat the door the terrace exists for. Plan schema
  **0.9.0**. Three rules, all `reading`, their bases checked through
  `check_openings.check_basis` rather than a 51st checker — `TOTAL_CHECKS` does not move.
  **`exterior_walls` means two different things on an outdoor room** (one record declares three
  free faces, four declare the side of the house) and neither reading resolves the six on its
  own, so the face is the INTERSECTION — a wall declared whose opposite is not — which is
  WP-11.4's "three statements of one depth" rule a layer up. **4 placed, 2 refused by name**
  (`wood-deck-w` declares no door; `wood-deck-e` serves two rooms and leaves E and N both
  admissible) and neither refusal patched into a placement. **The corpus PLACEMENT is
  byte-identical (`151126d0269bbc61`) and the OPENINGS move on purpose** — the inverse of
  WP-11.9's guarantee. **A placed at-grade appendage is OUTSIDE for the reachability walk**:
  one fatal cleared on the Tidewater plan and **27 created — `good-02` 7, `good-04` 10,
  `good-07` 10 — because those three have no placed exterior door at all** and the walk had
  nowhere to start — three COULD-NOT-EVALUATE verdicts became judged, and the single cause is
  named once beside them (`outside-is-only-an-appendage`). fatal 136 → 162, serious 681 → 685,
  info 167 → 164, refused doors 243 → 236. **The door was seated and the sheet said it could
  not be drawn**: `derive_openings` builds its lookup from rooms carrying `geometry` and an
  appendage's room deliberately carries none, so both plates printed a placed door as
  undrawable (`FAMILY–TERRACE` by name); both spellings take an `appendages` argument now
  and the plates read 14 → 13 and 6 → 5. Found by looking at the sheet.
  **Two guards that already existed caught the package, both fifty minutes into the full
  suite**: `test_ingest.py`'s schema-version pin caught the 0.9.0 bump a seventh time, and
  `test_modcache.py` caught a local by-path loader in the new module's `main()` — removed
  rather than routed, because no other leaf in `build/` carries a CLI.
  Three of the new guards could not fire on the first
  mutation pass — every one a branch the shipped corpus cannot reach — and each was given a
  fixture that proves it bites rather than being deleted. New question:
  `oq/an-at-grade-appendage-is-drawn-and-not-judged` (the drawn rectangle is held against no
  band, because the drawn layer reads `room.geometry` and there is none — which is exactly what
  keeps the three filters blind). Report:
  `docs/reports/wp-11.10-the-terrace-that-is-not-a-massing-element.md`.

- **WP-11.11 — the prover learns the massing. Status: COMPLETE (7 Sep 2026).** Closes
  `oq/the-proving-engine-cannot-place-a-second-massing-element`, which WP-11.9 raised and which
  gated the tags on the shipped record. All three of its items ruled as it framed them: **ONE
  coordinate space**, each room bounded by its own element's box (CP-SAT integer variables take
  negative lower bounds, so a west dependency at x = −34 needs no second origin — the shifted
  space the question offered is not used); **an element boundary is NOT downgradable**, stated as
  a plain `m.Add` so it creates no assumption literal and cannot enter a conflict core, `_RANK`
  untouched; and **affordability MEASURED rather than assumed** — a three-element fixture proved
  OPTIMAL in 0.47 s, the tagged Tidewater decided in 1.5 s, both shipped plans keeping their
  status at the batch budget. Eight statements the model made about "the block" are made about
  the room's own element now — containment, the coverage floor, a declared exterior wall, a
  spanning room's through-axis, an exterior door reaching the envelope, the bay grid, the span
  capacity and `_absorb`'s four growth limits. **The guarantee is that the MODEL for a
  one-rectangle house is byte-identical**, pinned as four `CpModel` proto hashes, because CP
  under a wall clock is not reproducible and pinning what it FINDS would pin the machine; the
  corpus's placement, openings and findings are unmoved. **And the tags on the shipped record are
  still refused, for a better reason than WP-11.9's**: `engine="cp"` proves the hand-tagged
  Tidewater INFEASIBLE with a minimized core of ONE DOOR — *"Dining Room and Butler's Pantry
  share a door"* — while `engine="heuristic"` reports the same tagging as an improvement (fatal
  8 → 6, serious 61 → 53). Exactly 2 of the 16 ground-floor door pairs cross main-to-dependency
  without passing through the hyphen, and one is the door the butler's pantry exists for: every
  boundary `blocks_for` can draw through this record cuts a declared door, which is
  `oq/the-parti-dissolved-its-own-dependencies` measured for the first time. **Three defects
  found in the package's own work**, the sharpest being that the guard written to protect
  byte-identity (`if ex:`) created the defect it was guarding against — five untagged rooms in no
  element at all — and that **a measurement taken on the model with that bug reported a proof
  that did not exist** (13.5 s "OPTIMAL", an artefact, one edit from being published as the
  headline). `_absorb` undid a proof for the FOURTH time. Nine mutations, every one biting.
  Report: `docs/reports/wp-11.11-the-prover-learns-the-massing.md` · new question:
  `oq/the-coverage-floor-is-an-exact-cover-per-element`.

- **WP-11.12 — the span nobody was told about. Status: COMPLETE (7 Sep 2026).** OQ 98's
  REPORTING half, and the half that needed no ruling. `structure.span_check` has measured the
  clear span between bearing lines since WP-3.1 and `geometry` has CHARGED it since WP-7.4
  (`SPAN_W = 20`, mirrored soft in CP) — **and `plan_check` had no span or capacity finding of
  any kind**, so the Tidewater upper floor's **60 ft clear run with no bearing line in it**,
  against the 20 ft its framing tradition states, got a clean verdict from the validator the
  bench shows, the fidelity score the composer ranks on, the critique and every
  `revision_report`. `geometry._disclose_spans` writes `geometry_report.span_capacity.marks`
  — `{axis, from_ft, to_ft, span_ft, member, max_span_ft, note, level}` per run, `relaxations`'
  own *counted AND locatable* shape — from `_disclose`, so **both** record writers carry it
  (OQ 40's disclosure shipped in `write_record` alone for two phases). **One arithmetic, two
  adapters**: `over_capacity_spans` (rectangles, what the search holds) converts into
  `spans_over_capacity` (placed records, what a finished plan holds) and `_span_charge` sums the
  first; `span_check` is called from exactly one place and an `ast`-reading test holds it there
  — the first version of that test counted two docstring mentions in `render_section.py` as
  calls. `plan_check.drawn` emits one `serious` per mark with `need_ft`/`have_ft`/`axis`/`level`
  and an `info` `span-unjudged` where the catalogue could not be read, and **reads the record
  rather than recomputing**, because these are the spans `SPAN_W` charged and a second
  computation could convict a placement on numbers it was not chosen by. *Serious rather than
  fatal* on the corpus's own words — `span_check`'s note asks for an intermediate support or an
  engineered member, which is a floor framed differently, not a plan that cannot be walked.
  Both plates print the count **and the zero**, because *"no span exceeds capacity"* is exactly
  the claim the understatement can make falsely. **Every count is a floor and says so**
  (`span_capacity.understated`, in each finding's own statement and on both plates): the
  measurement half of OQ 98 is that a bearing line is credited across the whole plate however
  short the wall runs — the Tidewater upper y-wall runs 20 of the 60 ft it is credited across —
  which under-reports in the direction that looks safe. Measured, `heuristic`, sixteen plans:
  **serious 685 → 708**, exactly the 23 spans on 13 plans, worst **60.0 ft**; fatal, minor, info
  and advisory unchanged; placement `151126d0269bbc61` and openings `770a886c7387f3ab`
  unchanged; solve 0.385 → 0.366 s. **`critique` classes it `placement` and the code says that
  stretches the definition** — every other kind there is decided against something the record
  DECLARES and a plan record states no wall positions at all, so it is classed on the other half
  (an engine setting really does change it), and under CP-SAT `_lever` then says there is none
  left. **WP-11.8's published pair `13 → 25` was an unlabelled `auto` reading**: re-derived on
  `git archive` checkouts, the deterministic pair is **11 → 23** and the worst-span pair
  `40.0 → 60.0` was right; `auto` gives 28 and is not reproducible. Corrected in CLAUDE.md
  beside the original, with the engines named, rather than in WP-11.8's report, which is left as
  written. **One of the ten mutations did not bite on the first pass** and it was the familiar
  shape — `member: None`, where no catalogue member covers the run, a branch no plan in this
  corpus takes and whose prose interpolated the None; it has a fixture, not a deletion. **And
  one new assertion stated a false reason and its own first run caught it**: it said `plan_check`
  cannot load `structure.py`, which it can and does, lazily inside a try, in the elevation block,
  since WP-3.2 — the comment in `plan_check` said the same. No new checker; `TOTAL_CHECKS` does
  not move. Report: `docs/reports/wp-11.12-the-span-nobody-was-told-about.md`.
- **WP-11.13 — the box that could not hold its own rooms. Status: COMPLETE (7 Sep 2026).**
  Closes `oq/the-coverage-floor-is-an-exact-cover-per-element`, **by measurement and without
  changing the number it asked about**. `dependency_sizes` sized a non-main element's box to
  EXACTLY its rooms' declared area (`H = need / W`, zero slack by construction) and
  `geometry_cp._element_boxes` then rounded it INWARD — WP-11.11's deliberate ruling, so nothing
  CP proves sits outside the stated mass — and `blocks_for` centres a dependency on the main
  block's axis, so its origin is a half-foot and BOTH roundings bite. Measured on the hand-tagged
  Tidewater against a floor of 0.97: **dependency 690 sf of box for 701 sf of rooms (1.016),
  hyphen 105 for 112 (1.067)** — the rooms could not fit at all, at any floor. **And the coverage
  floor rounded the same box a SECOND way** (`int(round(...))` against containment's
  `ceil`/`floor`), so the model demanded 97% of the larger be packed inside the smaller: 108.6 sf
  into a box holding 105, infeasible by construction, which is why every tagging of that record
  returned *"the rooms cannot tile any footprint this parti and lot allow, even with every
  declared requirement dropped"*. `elements.integer_box` is the one spelling now, in the leaf both
  the model and the disclosure load; `grid_allowance_ft()` is two quanta per axis, DERIVED by
  solving `(W − 2g)(H − 2g) ≥ need` rather than chosen, and the hyphen takes it in DEPTH only
  because its width is the gap between two masses. **What a floor is stated against depends on how
  the box was derived**: the main block's is grown independently by `derive_footprint`, so the box
  floor is a real question about its rooms; a dependency's is derived FROM its rooms, and the
  quantised answer cannot land (the floor needs the box within 3% of the rooms' area and one foot
  of a 30 ft dependency is 5%), so its floor is stated against the rooms' own declared area.
  **`COVERAGE` is unchanged at 0.97.** `geometry_report.multi_element.element_capacity` puts all
  of it on the record, per element, with `elements_too_small_for_their_own_rooms` beside it.
  **What it bought: the hand-tagged Tidewater — service programme in a west dependency joined by
  the back hall as a hyphen — is proved OPTIMAL in 12.3 s with zero pins downgraded**, which is
  Part I.A item 4 of the Phase 11 diagnosis and the first multi-element house this corpus has
  proved outside a selftest fixture. **The corpus is BYTE-IDENTICAL** (placement
  `151126d0269bbc61`, openings `770a886c7387f3ab`, the four `CpModel` proto hashes) and
  structurally so: 0 of 16 records carry a `block` tag, asserted rather than assumed.
  **The corpus said where the butler's pantry goes a fortnight before anyone tagged it** —
  `rooms/butlers-pantry.json`'s OQ 59 `via` clause, *"in a Tidewater plantation house … the pantry
  is in the block"* — so WP-11.11's refusal was right and its TAGGING was wrong; the two crossings
  are not equivalent (`must_adjoin dining-room` is hard with no `via`, `must_adjoin kitchen` is
  hard with one the plan already carries in full). **The shipped record is still NOT tagged**: it
  is a record edit moving a shipped placement, and a package that does two things can only be
  reasoned about as one — `oq/the-parti-dissolved-its-own-dependencies`.
  **WP-11.11's published "2 of 16 crossing pairs" is 1**, corrected beside the original: the
  second was `breakfast ↔ terrace`, and a terrace takes no rectangle, so it is in no element and
  cannot cross — and the first instrument written here read *no element* as *the main block*,
  reproducing WP-11.9's own defect inside the package auditing WP-11.11. Three existing guards
  were re-cut against the behaviour they name and none bumped, among them a **source grep for the
  very expression that carried the bug**, which went red on the fix. Six mutations, each asserted
  to have landed, all biting — and one bites only the arithmetic test, which the test file says in
  its own words. `capacity_report` reported unjudged as passed twice before it was right (a
  `fits: true` on an empty sum, on a record whose blocks carry no room list; and the main block
  judged on a grid `_snap_fpd` removes), both found by running it. No new checker; `TOTAL_CHECKS`
  does not move. **And rendering the proved sheet found a SEVENTH layer reading one rectangle**:
  both renderers draw an exterior door, its sill and its swing on the FOOTPRINT's wall rather than
  on its own element's, so the tagged sheet puts two doors in open space north of the building
  (`backhall` at 42.0 ft against its own face at 30.0; `kitchen` at 42.0 against 33.02). The
  interior branch three lines above is already right. Named rather than fixed, because the honest
  form adds a key to `derive_openings`' output in both spellings and the frozen sheet-symbols
  fixture holds them to one contract —
  `oq/an-exterior-door-is-drawn-on-the-footprints-wall-and-not-its-rooms`. Report:
  `docs/reports/wp-11.13-the-box-that-could-not-hold-its-own-rooms.md`.

- **WP-11.14 — the seventh layer. Status: COMPLETE (8 Sep 2026).** WP-11.9 taught six layers
  below the placer about massing elements and **the DRAWING was not one of them**: both plan
  renderers put every exterior opening at `0`/`W`/`H`, the FOOTPRINT's edges. Measured on the
  hand-tagged Tidewater — **2 exterior doors drawn in open space** (by 12.00 and 8.98 ft, with
  their sills and swings) and **5 windows standing on their own element's face dropped as
  "off-footprint"**. `_boundary_wall` / `boundaryWall` take the room's own element box from
  `elements.bounds_index`, the same reader `openings.py` has used since WP-11.9, so the placer
  and the drawing answer "which of this room's walls are exterior" with ONE function; and every
  exterior entry carries `edge_ft`, the coordinate ACROSS the wall, which had nowhere to live
  because `at_ft` already means the perpendicular on an INTERIOR entry and the position ALONG
  the wall on an exterior one. **Its fallback is the ROOM's own face and never the footprint's**,
  which is why the package is the IDENTITY on a one-rectangle house: all sixteen shipped sheets
  hash `4cfba3a0885ddccb` before and after, measured on a `git archive HEAD` checkout. Doors
  **2 → 0**, windows drawn **7 → 11**, refusals **16 → 11** — and that 16 was **5 defects and 11
  CORRECT refusals** (the placement put those rooms inland), a split published rather than a
  total, because 16 would have been three times the true figure in the flattering direction.
  **The obstacle WP-11.13 named was not one.** It refused this work because changing
  `derive_openings`' output shape needs the frozen `sheet_symbols` `expected` rewritten and
  regenerating re-solves on `auto` (825 insertions / 804 deletions on the pristine tree with no
  code change). But `freeze()` re-solves only to obtain the ROOMS; `expected` is derived FROM
  them and the rooms are already committed as contract INPUT. `generate.py --expected-only`
  re-derives it with no solver — **verified as a byte-for-byte NO-OP against the pristine
  renderer before it was used**, and it produced **39 insertions, 0 deletions** here. That is
  available to every later package that changes a renderer's output shape.
  **The frozen fixtures cannot hold a multi-element case** (no plan carries a `block` tag), so
  `tests/test_exterior_faces.py` and `workbench/app/src/derive.test.mjs` assert the same three
  numbers on the same two hand-built rectangles, on WP-11.10's precedent.
  **Six mutations; five bit at once and the sixth was the one that mattered** — *the drawing
  ignores `edge_ft`*, the line that put the doors in mid-air, passed every test in the file
  because every assertion read the DERIVATION and none read the DRAWING (WP-11.10's finding, one
  package later, in the same file). The replacement was blind too, stripping both keys at once
  so the windows alone moved the plate; it strips one at a time now. **And the code was really
  wrong in the way the mutation exposed**: `_frame` and `_door` each read the face separately,
  so reverting either still moved the other — one opening has one face, computed once. The
  **And a THIRD guard pinned a literal signature**:
  `test_both_renderers_read_the_record_and_derive_nothing` asserted the whole `derive_openings`
  signature verbatim, so adding an argument after `appendages` broke a guard about appendages
  with a change about elements; its own comment already named the property ("in the same argument
  position") and it reads the parameter ORDER now, mutation-checked by swapping the last two.
  The question is HALF CLOSED: doors and windows are swept, the other exterior marks (the stoop,
  the stacks, the elevation's) are not. Report:
  `docs/reports/wp-11.14-the-seventh-layer.md`.

- **WP-11.15 — the phantom storey the disclosure invented. Status: COMPLETE (8 Sep 2026).**
  Found while COSTING WP-11.16, by tagging the shipped record in a scratch copy and reading what
  came out: `geometry._disclose_spans` published a **30 ft clear span on the upper floor of a
  single-storey wing**, at x −37..−7 where that wing has no rooms. It built its element map as
  `{idx: [every element] for idx in rooms_by_level}` — every level, every element — while
  `spans_over_capacity` takes that map keyed by level *precisely* so this cannot happen and says
  so in its own comment. WP-11.9 had established the rule three packages earlier and
  `structure.build_section` and `export_ifc` both obeyed it: **four spellings, the one written
  last was wrong.** `elements.elements_on_level` is the one spelling now and all three read it;
  the search keeps its own map deliberately, being a different input shape (raw blocks, before a
  record exists, keyed to level 0 because the placer reads a `block` tag on the ground alone).
  **THE COUNT NEVER MOVED**: the phantom REPLACED a real 29.9 ft run rather than adding to one,
  so `over_capacity` 4, `len(marks)` 4 and `worst_span_ft` 40.0 ft read identically either way —
  a ratchet on the count could not have failed, and every guard here asserts WHERE a mark is.
  It falsified WP-11.12's own promise that the marks are the spans `SPAN_W` charged:
  `published == charged` measured **False**, `charged == per-level` **True**. **The shipped
  corpus is BYTE-IDENTICAL** — 23 marks over 13 plans, digest `10c5577097b5ec0e`, measured on
  the pristine tree and again after, and provably so because `len(_els) > 1` is false on all
  sixteen. Guards are hand-built two-element records on WP-11.10's precedent, the dependency at
  negative x on purpose; four mutations, each asserted to have landed, all four bite. No new
  checker; `TOTAL_CHECKS` does not move.
  **The full suite came back `1 of 50 checks failed` and the failure was NOT this package's**:
  `test_shape_pins`'s band guard fails about one run in four on `engine="auto"`, measured at
  **2 of 8 on the PRISTINE tree and 2 of 8 on the working tree**, alternating to control for
  machine load. The discriminator is the solver status — it passes on `FEASIBLE — kept polish`
  and fails on `OPTIMAL (hard-only)`, where a room is drawn 51% over its declared area and
  outside its band while `downgraded_shape_pins` is EMPTY. Raised with the measurement as
  `oq/a-held-shape-pin-is-not-held-on-the-hard-only-path` and deliberately not fixed here: every
  plausible fix moves a placement, and this package's guarantee is that nothing shipped moves.
  Report: `docs/reports/wp-11.15-the-phantom-storey-the-disclosure-invented.md`.

### WP-11.16 — the record edit (NEXT, and it is a record edit only)

**Tag `plans/tidewater-georgian-careful.json`.** WP-11.13 ruled this "a record edit and its own
package" and WP-11.9's lesson is that a package which teaches a layer *and* moves a shipped
placement has done two things. Everything below the placer now knows about massing elements
(seven layers, WP-11.14) and the last false measurement is gone (WP-11.15), so what remains is
the edit.

**The tagging, established by WP-11.13's ladder and re-derived here:** `kitchen`, `pantry`,
`breakfast`, `powder`, `cellarstair` → `block: "service"` (617 sf); `backhall` →
`block: "service"`, `hyphen: true` (112 sf); **`butlers` stays in the BLOCK**, which
`rooms/butlers-pantry.json` has said since OQ 59 — *"in a Tidewater plantation house … the
pantry is in the block"* — and the redundant **direct `butlers↔kitchen` door is dropped on both
sides**, its `must_adjoin kitchen` being satisfied `via` the back hall, which the plan already
carries in full.

**Measured while costing, and to be RE-DERIVED rather than quoted** (WP-11.13's own published
"zero pins downgraded" did not reproduce): `engine="cp"` goes **FEASIBLE at the 40 s budget →
OPTIMAL in 8.9 s**, objective 541.2 → 407.8, wall pins 9 → 7, shape pins **0 → 1** (the Centre
Passage's own proportion band, which is the price). `engine="heuristic"`: fatal **8 → 7**,
serious **65 → 54**, minor 83 → 82.

**A PRECONDITION FOUND BY WP-11.15's AUDIT, and it will fail the suite on day one:**
`geometry_cp._score` calls `_span_charge` with no `elements=`, so a CP placement computes
`over_capacity` footprint-wide while `span_capacity.marks` is per element (3 against 4 on a
two-element fixture; on the tagged Tidewater the CP charge invents a 30 ft span across the
hyphen gap). `tests/test_span_findings.py` asserts `len(findings) == over_capacity`, so it goes
RED the moment a tagged plan is CP-solved. Settle it first; it is a placement change, because
the charge is in the prover's objective.

**What that package must answer rather than absorb**, all three found while costing:
one NEW fatal `unreachable: butlers`; a **severed entrance sequence** (`Entrance Portico joins
no other room on the drawing`); and the main block shrinking to 40 × 42 ft at 4 bays, which is
correct — the service programme left it — but moves every drawn room. It also fires
`test_the_fixture_really_exercises_the_multi_element_branch`, deliberately, and touches the
frozen `sheet_symbols` fixture, whose ROOMS change: `--expected-only` does NOT cover that case
and the README's 825/804 full regeneration does apply. Cost it before starting.

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
