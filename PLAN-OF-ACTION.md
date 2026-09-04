# Traditional Design Language — Plan of Action

*Companion to `STATE-OF-THE-PROJECT.md` (revised 25 August 2026 and since kept current). That document says where the project stands; this one says how to finish it. It is written to be cut up and handed to Claude agents one work package at a time. Each package is self-contained: what to read, what to build, what "done" means, and what not to touch.*

---

## Progress board — as of 4 September 2026

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
| **11 — The house the sheet should have drawn** | **WP-11.1 through 11.5 COMPLETE · 11.6 through 11.11 planned** | **In progress (4 Sep 2026); all five rulings taken the same day** — raised by Lucas against the workbench's own sheet for `tidewater-georgian-careful` with the instruction to diagnose before building. The diagnosis is `docs/reports/tidewater-layout-diagnosis-2026-09-04.md` (cite the filename): fifty-one findings in ten tiers, eight root causes, and the finding that decides the order — the sheet's *"PLACEMENT PROVED (CP-SAT) AGAINST THE RECORD'S DECLARED FACTS"* sits over a placement that set aside SIXTEEN declared exterior walls (both ends of the passage among them) and whose compositional objective never ran (`objective: null`, "best of 1"), so every soft term the corpus has was inert on the engine the bench draws by default, and the search it refuses to draw scores 712.6 against the proof's 835.0. All five of the phase's questions were ruled on 4 Sep and **11.1 through 11.5 have shipped**; the container (11.6) is unblocked by the four rulings of `oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it`, taken the same day. **This sentence said the container WAITED on those four rulings in the same breath as saying all five were taken** -- a contradiction inside one sentence, corrected by WP-11.5 and the same class as WP-11.6's own status line below. The phase's own section carries the ruling on each |

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

## Phase 11 — The house the sheet should have drawn

*Raised by Lucas on 4 September 2026 against the workbench's own plan sheet for
`tidewater-georgian-careful`, with the instruction to diagnose first and build second. The
diagnosis is `docs/reports/tidewater-layout-diagnosis-2026-09-04.md` — cite the filename — and
this phase is its Part VII, the order of work, turned into packages. Read that report's Parts 0, V
and IX before taking any package here: Part V is the eight root causes, Part IX says which stratum
each fix lives in, and a fix made in the wrong stratum is the homogenising move this project exists
to refuse.*

**Two orders, and they are not the same.** The report's order of work is by DEPENDENCY: the
container first, because twenty-two placer findings sit under ten massing-and-parti findings and
fixing the placer first would arrange slivers more tidily inside the wrong box. The order of START
is by what is UNBLOCKED: three packages need no ruling and can begin today, and the container waits
on four rulings that are Lucas's. The board below carries both. Nothing in this phase proposes a
score term — WP-9.4 swept the terms and moved nothing, and the diagnosis measured why: on the
proving engine the objective the terms live in never ran.

**The one measurement every package in this phase is held to.** Before and after, on
`plans/tidewater-georgian-careful.json` and `plans/spec-builder-colonial.json`, on BOTH engines, the
CLI prints: the plan_check key `[fatal, serious, minor]`, `drawn_summary.diverged` count,
`opening_report.windows_unplaced`, `geometry_report.solver.downgraded_wall_pins` count,
`geometry_report.vertical` transfer count, and the demerit score. The diagnosis's baselines on the
CP engine here are `[0, 73, 80]`, 24 diverged, 27 of 35 windows unplaced, 16 downgraded, 30
transfers, 835.0; on the heuristic the score is 712.6. A package that cannot say which of those it
moved, and in which direction, is not done. (Both engines, because a package that improves the
proof and worsens the search — or the reverse — has to say so; WP-9.6 found the two engines
disagree by 50% on the furniture count.)

### WP-11.1 The sheet says what the solver gave up

**Status: COMPLETE (4 September 2026).** Report:
`docs/reports/wp-11.1-the-sheet-says-what-the-placement-gave-up.md` — cite the filename.
Report's Part VII item 6; findings J1, J2, J3, J5, F1, G1.

**What shipped.** `build/disclosures.py` is the one spelling of every banner line; the printed
plate draws them and the bench renders the same list through `placement.disclosures`. Five facts
the record already carried and nothing read: the declared exterior walls a CP proof set aside
(16 of 35 on the Tidewater plan), the objective that never ran, the undrawn window units (27 of
35), the transfer beams (30), and each ∗ room's declared figure — the last as a table under the
plates, because a per-room line would have shrunk names until they dropped out. The engine line no
longer claims the whole record, and a style-disagreement line fires when the title or the parti
names a style the sheet did not judge by. `build/diagnose_sheet.py` (WP-11.11's first half,
brought forward) prints the phase's six baseline numbers; the four measured baselines are in the
report's own table.

**Four findings, three of them in this package's own work.** The first draft ran a 160-character
line off the edge of the canvas — the defect the package exists to remove, introduced by it, found
by rasterising the plate. The new instrument published "the objective did not run" about the
hill-climb, which is the one engine that always runs it. One of the package's own new guards was
blind and the mutation found it: it compared two heights that differ for a second reason. And the
bench's caption had been claiming the set-aside walls "are named above" when nothing above named
them.

*Original package text follows, as written.*

The plate reads *"PLACEMENT PROVED (CP-SAT) AGAINST THE RECORD'S DECLARED FACTS"* over a placement
whose solver record carries sixteen declared exterior walls set aside, `objective: null`, and
"best of 1 hard-valid placements". WP-6.4 made the plate say which engine ran; this package makes it
say what the engine gave up. It is the WP-6.1 discipline — the sheet must not lie about the record —
applied to four fields the solver already writes.

**Build.** In `build/render_plan.py`'s banner stack (the block that prints CUT(S), DECLARED DOOR(S),
ROOM(S) DRAWN AT A SIZE, the engine line):
1. Beside the engine line, `N DECLARED EXTERIOR WALL(S) SET ASIDE TO PLACE — <room list>` from
   `geometry_report.solver.downgraded_wall_pins`, in the iron colour, whenever the count is not
   zero; and the engine line itself reads `PLACEMENT PROVED (CP-SAT) AGAINST N OF THE RECORD'S M
   DECLARED EXTERIOR WALLS` when any were dropped.
2. `FIRST FEASIBLE PLACEMENT — THE COMPOSITIONAL OBJECTIVE DID NOT RUN` whenever
   `solver.objective` is null on a CP placement, in copper. A proof of feasibility against a relaxed
   hard set carries no compositional information and the plate has to say so.
3. `N OF M DECLARED WINDOW(S) NOT DRAWN — <reasons>` from `opening_report.windows_unplaced` and the
   per-window `unplaced.reason`s, grouped (no such boundary wall / no clear run).
4. `N UPPER WALL LINE(S) ON NO WALL BELOW` from `geometry_report.vertical`.
5. On every ∗ room, the record's declared `W x L` in the `.dm` face beside the drawn figure, so a
   reader can tell a room the placer ruined from one the author drew small.
6. The same lines in the app's own sheet (`workbench/app/src/sheet/derive.js` and whichever
   component prints the banner — `PlanWorkbench.jsx` around the `bays of` subtitle), because the
   screenshot Lucas read is the app's plate, not `render_plan.py`'s. Two spellings, one contract,
   held together the way `tests/fixtures/sheet_symbols/` holds the jamb allowance — NOT a third copy
   of any rule, only a shared fixture of expected banner text for one placed record.
7. A style/title consistency line: when `plan.style` is not among the parti's `styles` (where the
   drawing route was handed a parti) or the plan's `name` names a style that is not `plan.style`,
   `JUDGED AS <style> — TITLE SAYS <other>`. This is the `palladian` case of the diagnosis's I.4.

**Tests, mutation-checked.** `tests/test_sheet_disclosures.py`: for the CP placement of the
Tidewater plan (skip with COULD NOT EVALUATE when OR-Tools is absent, never pass), each banner line
is present with the right count; revert each line's source and the test goes red — assert the
mutation LANDED (WP-9.6's lesson) by reading the count back. For the heuristic placement the
downgrade line is ABSENT, which is the second half of the contract. `e2e/walk.mjs` asserts the app's
banner against `/api/plan/evaluate`'s `geometry_report`, not against a phrase.

**Not in scope.** Changing what the solver does. This package only reports it.

### WP-11.2 The diagram reaches the record, and the record is checked against the diagram

**Status: COMPLETE (4 September 2026).** Report:
`docs/reports/wp-11.2-the-diagram-reaches-the-record.md` — cite the filename. Part VII items 2 (the
half that needs no number) and 4 (the hand-off half); findings A3, F2, E3.

**What shipped.** Plan schema **0.6.0**: a plan may name its `parti`, as an id and never a record,
resolved through `core.load_parti` and never a fourth copy of that join. The massing's own bay
count is read (`massing_bays`, conservative: two forms accepted and five prose forms refused by
name) and its parity survives growth, which steps by TWO on a diagram that wants a centre bay — so
the shipped Tidewater plan is placed SEVEN bays wide instead of six and has a middle bay for the
first time. `build/check_plans.py` holds a hand-authored plan to the parti it names and is in
`check_all` (45 in the loop, 48 in the run).

**What it found, first run.** The record had dropped **two of its parti's five `stacks_over`
claims** — the upper passage over the lower one and the landing over the stair, the two that
organise the floor — so `plan_check`'s stacking layer had nothing to read and the sheet drew a
landing over the library. Nothing could have caught it: `compose.py` copies those claims onto every
candidate, so a composed plan is right by construction and **both shipped reference plans are
hand-authored**. Restored. Two further disagreements are REPORTED rather than failed
(`exterior_walls` is exposure, not topology, and decision #3 puts massing outside a parti's
authority): the plan's back hall is a hyphen and its kitchen a dependency and the parti has neither.

**And the parti's own module contradicts its exemplars.** 9 ft against Gunston Hall's measured
12.17; the style's own prose says *"Facade 48–72 ft, five or seven bays"* and nothing reads it.
`oq/the-partis-bay-module-contradicts-its-own-exemplars`, raised rather than patched.

**And nine tests moved, two of which were wrong before this package touched them** — three calls
passing a SECTION where `build_roof` takes a parti (two buildings, one test, invisible until a
parti reached the footprint) and a hip-ridge pin at `rel_tol=1e-6` that was pinning a rounding
coincidence. `spec-builder-colonial` stopped flagging any over-capacity span (more bays, more
bearing lines, shorter spans) and two tests that asserted on it were re-pointed rather than left
blind. **One ratchet went UP and is recorded rather than absorbed**: the drawn furniture
along-axis ceiling 69 → 74.

**The cost, stated: the odd bay count costs about three fatal findings on the hill-climb** (8-seed
means 6.2 → 9.2), all of them unreachable rooms the search could not door, and **zero on CP-SAT at
a budget that reaches phase B**, where serious goes 73 → 67, transfers 30 → 17 and undrawn windows
27 → 20. Accepted and recorded rather than hidden: the cause is the container, which is WP-11.6's.
**The first before-and-after was taken at ONE SEED and read 3 → 8**, which is a comparison of two
draws; `--seeds` now reports every column as a spread.

*Original package text follows, as written.*

**Build.**
1. **A plan record may name its parti.** `schema/plan.schema.json` gains `parti` (an id, never a
   record — WP-9.4's rule); the two shipped plans name theirs. `derive_footprint` reads the named
   parti's `bay_module_ft` and `max_bay_count` where a caller passed none, so the Tidewater plan is
   placed on the diagram's 9 ft module rather than the 10 ft default. Measure what that does to
   the six baselines; the expectation is that it changes the bay count and therefore everything,
   and the package reports the movement rather than promising it.
2. **The massing's `bays` is read.** `derive_footprint` reads `massings/catalog.json`'s `bays` for
   the plan's massing ("5", or a range) as the starting count, and the parti's `max_bay_count` as
   the ceiling, and for a massing that states an odd count it grows by TWO bays, never one, so the
   centre bay survives growth. Where the lot cannot hold the odd count the record says
   `bay_count_forced_even` in `geometry_report` — a named refusal, not a silent six.
3. **`build/check_plans.py`** (new, in `check_all`): every plan record that names a parti carries
   every `stacks_over` the parti states for a room of that id, every `exterior_walls` the parti
   states, and every door the parti's room list states; a hand-authored plan that dropped one is
   named. The Tidewater record gains `upperpassage.stacks_over: passage` and
   `landing.stacks_over: stair`. (The composer already copies these — `compose.py`'s candidate
   emitter — so this is the check the hand-authored path never had.)
4. `check_counts.py` pattern for the new checker's count, and `TOTAL_CHECKS` moves — read the
   SECOND number, per CLAUDE.md.

**Tests.** `tests/test_check_plans.py`: a fixture plan with one dropped `stacks_over` fails; the
two shipped plans pass after the record fix. `tests/test_geometry.py` gains the odd-bay growth
pin: a massing stating 5 grows to 7, never 6, and the forced-even refusal is written when the lot
allows only 6.

### WP-11.3 The axis

**Status: COMPLETE, WITH ONE DELIVERABLE REFUSED AND MEASURED (4 September 2026).** Report:
`docs/reports/wp-11.3-the-axis.md` — cite the filename. Part VII item 2; findings B1, B2, B4, B5,
G2 (the check half), C3.

**What shipped.** `build/axis.py` is the vocabulary `plan_check` said did not exist: the
footprint's centre line, the bay a door stands in, the mirror about the axis, and vertical
alignment — each returning COULD NOT EVALUATE with a reason rather than a zero. `plan_check`'s
drawn layer is its first reader, publishing a census beside four findings, and the block binds only
where the DIAGRAM claims a centre bay, so a Charleston single house is not judged by it.

**What was refused, with the numbers.** A `centre_bay_score` for the threshold room's distance from
the middle bay: swept at 0, 5, 20 and 60 over five seeds, it is PAID at every weight and moves the
chosen candidate at none. At 1,500 candidates it moves the door from bay 5 to bay 2 of 7 and still
misses the middle. A door in the centre bay is a property of a plan organised about an axis, not of
a placement scored for one — so it goes to WP-11.6 and, on the proving engine, as a hard constraint
rather than a charge. `build/geometry.py` is unchanged; the function was deleted rather than left
inert at weight zero.

**Two things worth carrying.** Symmetry and alignment are REFUSED on an incomplete front — seven of
the Tidewater plan's declared front window units are not drawn, and convicting that facade of
asymmetry would charge the house twice for one cause. And the passage is already ON the centre line
after WP-11.2, so the finding this package was built to raise does not fire on the plan that raised
it, which is stated rather than left as a silence.

*Original package text follows, as written.*

`plan_check.py` says in its own comment that there is no axis vocabulary anywhere in the codebase.
This package writes one, in ONE place, and both engines and the critic read it.

**Build.**
1. `build/axis.py` (a LEAF, like `storeys.py`): given a placed level and the footprint, the
   entrance axis (the front door's centre, from the threshold room's exterior door), the passage
   centreline, the bay index of the door, the footprint's centre, and a mirror map of same-type
   rooms about the axis. Returns COULD NOT EVALUATE when no room reaches both fronts or no front
   door is placed — never a zero.
2. The critic: `plan_check` drawn layer gains `drawn-passage-off-centre` (passage centreline
   against footprint centre, tolerance from the ruling), `drawn-door-off-the-centre-bay` (the door's
   bay index against the middle bay of an odd count), `drawn-facade-unmirrored` (the massing's
   *"Facade symmetry is a hard constraint"* made executable: front openings mirrored about the
   axis within a stated tolerance), and `drawn-windows-unaligned` (the massing's *"Window bays must
   align vertically"*: each upper front window over a lower one within a stated tolerance). Each is
   scoped to `circulation_parti: center-hall` diagrams by reading the parti, never by style —
   stratum 3, not 4. The prose `statement` stays beside every test.
3. Both engines: for a center-hall diagram, the passage centreline within the tolerance of the
   footprint centre and the door in the centre bay become HARD — a constraint in `geometry_cp.py`'s
   `_build` beside the entrance-front block, and in the heuristic a candidate REJECTION, not a
   charge (a charge is what `centre_hall_symmetry_score` already is, at 1.5 points, and it is inert
   on a side passage). The period's *"slightly off-center"* (Westover, Wilton) is admitted as an
   asymmetry of ROOM size across the passage, which costs nothing here because rooms are already
   free to differ.
4. `centre-passage-core.json`'s untested rules *"Both ends of the passage have doors, and they are
   aligned"* and *"their windows align vertically"* gain `test`s that read `axis.py`.

**Tests.** Mutation-checked, both directions: a fixture with a side passage is convicted; the same
fixture with the passage moved to the centre bay passes; a plan whose passage reaches one front
only is UNJUDGED, not convicted and not acquitted.

### WP-11.4 The hearth in the plan

**Status: COMPLETE, 4 September 2026.** Ruled the same day. Report:
`docs/reports/wp-11.4-the-fire.md`. Part VII item 3; findings D1, D2, D3, G5.

**Delivered.** `hearth` as an ARRAY on a plan room (schema **0.7.0**: `wall`, `position_ft`,
`width_in`, `flue`, `note`), `build/hearths.py` reading it against the massing's `hearth` value and
the room record's own `servicing.heat`, `plan_check` publishing a census and two findings from the DECLARED record, `render_plan.py` drawing the breast as poché with the opening in copper, and `roof.py`
standing its stacks over stated flues — which closes D3 the way OQ 85 closed the window on the
chimney axis. Three hearths authored on the Tidewater plan; its two stacks moved 6.2 and 8.6 ft off
the gable centre line onto real fires.

**The rule the package turns on: a hearth is AUTHORED and never inferred.**
`rooms/bedchamber.json` says an unheated chamber is historically normal and *"should be said out
loud rather than quietly given a register"*, so a checker demanding a fire wherever a type usually
has one would invent exactly what that sentence forbids. `wants_a_hearth` returns FOUR verdicts —
`stated` 12, `optional` 1, `none` 5, `unstated` 42 of 60 records — and `none` is the one a
two-state reader loses: *"Historically none"* carries no fireplace word, so the centre passage
would have been filed as unstated and hunted for a fire the corpus refuses it.

**Measured (six numbers, eight seeds, both plans, SEARCH engine).** Everything identical except
the spec plan's minor count, `89–98 → 90–99`: one true new finding, its dining room having no fire
under a massing that draws paired end stacks. **And the six numbers did not see the stacks move** —
two chimneys travelled 6.2 and 8.6 ft on the elevation with every column unchanged. The six are a
plan-layer instrument and a roof change is invisible to them.
**ON CP-SAT THERE ARE READINGS AND NO COMPARISON, DELIBERATELY** — tidewater `0/62/85` and
spec-builder `4/87/96` at a 120 s budget, but a before-and-after needs the same instrument twice
and CP-SAT under a budget is not deterministic under load, so a baseline sharing four cores with
the after run would have been unattributable. The sound argument is a guard instead: nothing
`hearth_report` reads is a placement, and a test holds the census and findings identical on an
unplaced record. What that does NOT cover is the roof's stack reconciliation, which reads each
hearth's room rectangle and has been measured on neither plan under CP.

**Found.** (1) **Fourteen of the sixteen plan records state no `massing` at all**, so every
massing-gated check is silent on 87.5% of them and two others (`plan_check.py`'s grouping
`attaches_to` branch and its style `massing_affinities` branch) do not say so —
`oq/fourteen-of-sixteen-plans-name-no-massing`. Corpus census: 3 stated, 1 absent, 15 declined,
**219 unjudged of 238 rooms**. (2) The refusal gave the WRONG REASON to those fourteen — one
message about compounds handed to plans that named no massing; three cases now carry three
messages, pinned distinct. (3) **This package's own authored data carried a false claim about a
check that does not exist**: the dining hearth's note said its disagreement with
`rooms/dining-room.json` was reported, and the only comparison made is against the massing's stack
walls, which W satisfies. Corrected, scope pinned by test; the obvious prose reader was measured at
**2 of 5 precise** and refused —
`oq/a-room-record-names-the-wall-its-fire-stands-on-and-nothing-compares-it`. (4) **A figure was lifted out of prose about
something else and published as MEASURED**: `rooms/closet.json` returned a 30.0 in fireplace
opening at `judgment: false` from a sentence about an air barrier, in a record whose first four
words are *"None required and none wanted."* Gated on `wants_a_hearth`'s verdict rather than a
tighter regex, and found by re-DERIVING a claim in the report rather than re-reading it. (5) **The
reconciliation swallowed its own failures**: a bare `except Exception` around `stack_axes`
collapsed *"could not read the hearths"* into *"this record states no hearth"*, which is WP-9.1's
`except: pass` in a new place — a fourth note state now. (6) **`hearth_report`'s branch order is
load-bearing**: `none` is tested before the unreadable-massing branch, so the corpus's own refusal
of a fire is not downgraded to "nobody could tell". (7) **The check was put in the one
layer that cannot run it**: `drawn_layer` early-returns without a placement and nothing
`hearth_report` reads is a placement, so the spec plan's fireless dining room produced no finding,
no census and no reason until somebody placed it. Moved beside the other declared layers;
`hearth_summary` is published on an unplaced record and the finding kinds lost their `drawn-`
prefix. (8) **MORRIS'S OWN RULE WAS BEING
INTERPOLATED RATHER THAN EXECUTED, AND THE LEVEL'S STATED CEILING WAS BEING IGNORED.** The width
came off two rows of Morris's table with a CLAMPED linear interpolation, so every room under a
12 ft cube got 36.0 in flat and every room over a 22 ft cube 49.0 flat -- 6.6 in too wide on a
small room, 7.9 too narrow on a large one, and only 0.3 out in the middle where a lazy fixture
would have looked. Lecture VI Rule II is recoverable from the 1734 first edition
(`sqrt(L + B + H) / 2` in feet) and reproduces both discarded anchors; it is executed now. And it
wants a ceiling the plan STATES (`floor_to_ceiling_ft`, 11 and 10) while the code reached for an
editorial constant on every room -- the three authored openings moved 46.3/43.7/41.8 -> 42.8/41.1/
39.8 and a test holds each against the rule. Still `judgment: true`: no facsimile has been read,
and a rule read correctly out of an English treatise is still an English rule. (9)
**Three of twelve guards were blind and the mutation harness itself had a typo** — the breast test held the breast
inside the room rather than on its named wall, nothing drove the off-the-stack-wall finding
(WP-8.11's "a driven fixture must not be the shipped corpus"), and nothing validated a plan against
the schema at all. Twelve of twelve caught on the re-run.

**Deliberately not done.** No move writes a hearth. **The placer reserves nothing for the breast** —
a 12 ft dining room with a 22 in breast has 10.2 ft of clear width and `furniture_shortfalls` has
not been told; reserving it in `geometry.py` alone would give the two engines two different rooms,
so it goes with WP-11.6. An `interior` hearth is counted and not drawn. Exterior versus interior
stacks are not modelled, because the massing vocabulary does not state the difference.

**Original package text, left as written:**

**Build.** A `hearth` on a plan room (`{wall, width_ft, flue}`; width editorial from Morris's table
with `judgment: true` until an American source is read), the massing's `hearth` value read as a
placement rule (`gable-end-paired`: each gable-end principal room's hearth on the gable, upper
chambers stacked on the same flue; `central`: the Cape's stack; `interior-paired`: the Wythe
House's cross-wall), the placer reserving the breast as a keep-out on that wall (OQ 55's mechanism),
`openings.py` treating the breast as blocked wall and centring the flanking windows on it,
`render_plan.py` and `derive.js` drawing it, and `roof.py`'s stacks derived from the plan's flues
rather than from the gable's centre line — which closes D3 the way OQ 85 closed the window on the
chimney axis. `plan_check` gains `drawn-room-without-a-hearth` for a diagram whose massing states
four fireplaces a floor, UNJUDGED on a massing that states no `hearth`.

**Not in scope.** Sizing a flue, or a chimney's construction; the room's hearth is a plan fact and
the stack is the roof layer's.

### WP-11.5 Stacking is a rule on the diagram

**Status: COMPLETE, 4 September 2026** — the mechanism is built, measured both ways and ships
**defaulted OFF** (`geometry.STACK_HARD = False`); flipping it is a ruling and the numbers are
below. The transfer-beam half and the CP hard pin are deliberately not built. Report:
`docs/reports/wp-11.5-stacking-as-a-rule.md`. Part VII item 4; findings F1, F2, F6, E3.

**Delivered.** `geometry.declared_stack_breaks` is the ONE reader of a `stacks_over` claim against
a placement, on `plan_check`'s own rule, so the search, the charge and the critic cannot convict
and acquit the same house. The search keeps TWO incumbents — best overall, and best that breaks no
declared claim — and prefers the second when it exists. It is not a rejection: an emptied pool is a
placement failure where the corpus wants a stated compromise. When no strict candidate exists,
`geometry_report.stacking` says so and names the count. `geometry.STACK_HARD` is the named switch,
because `_SOLVE_CACHE` is keyed on arguments and a rule nobody can sweep is a rule nobody can
refuse.

**THE HEADLINE MEASUREMENT: THE COST OF THE RULE IS A PROPERTY OF THE POOL, NOT OF THE RULE.** One
seed on the spec Colonial — 70.5 points at the shipped 250 candidates, 24.9 at 500, and **nothing
at 1,000**, where the unconstrained winner already satisfies every claim. Broken claims 4 → 1 at
250 and 4 → 0 at 1,000 on that plan; 8 → 2 and 3 → 0 on the Tidewater. That is WP-7.4's finding
arriving on a rule rather than a weight, and it is the third package to measure a term whose
verdict depends on the pool — `oq/a-placement-rule-is-free-at-a-pool-the-server-cannot-afford`.

**THE CRITIC'S KEY DOES NOT CLEARLY REWARD IT AND THE ROOM SIZES DO.** At 1,000 candidates the
spec fatal floor improves by one and its minor floor worsens by six; the Tidewater fatal count is
unchanged with a serious ceiling three worse. But measured on the spec Colonial's own rooms, rule
off against on: the **Stair Hall goes from 36 sf against a 76 sf floor — 53% short — to 64 sf and
16% short**, the Mud Room from 16% to 6%, the Study joins at 16%, and total shortfall falls from
**46 sf to 30 sf**. Forcing the bath over the laundry forced a better subdivision. The
minor-finding count rose while the house got materially better, which is why the report leads with
the rooms.

**THE NUMBER THAT DECIDED THE DEFAULT IS STRUCTURAL.** On `spec-builder-colonial` the strict
candidate introduces **two over-capacity clear spans where there were none, the worst 40.0 ft
against a 20 ft capacity**. On the Tidewater plan the same rule goes the other way: spans 2 → 4
but the worst falls **53.9 ft → 36.0**. Two shipped plans, opposite structural verdicts, at a pool
where the rule is not free. Better rooms against worse structure on one plan and the reverse on
the other is a trade for a person, so the switch ships `False` with the measurement beside it and
a suite that drives the other state. **The one blind guard the package found was that disclosure
itself** — both shipped plans always find a strict candidate at 250, so the branch never ran and
deleting it left the suite green; a pool of ONE drives it, and six of six mutations were caught on
the re-run.

**Not built, with reasons.** The CP hard pin — OQ 95 already built, measured and refused it, and
the blocker is the downgrade loop reading `kind == "wall"` so a stack pin outranks every authored
exterior wall; teaching it a second kind needs an ORDERING ruling between an authored
`stacks_over` and an authored `exterior_walls`. The transfer-beam half — 10 beams to zero on the
Tidewater plan and 45 corpus-wide is a far stronger constraint and is not attempted on one
measurement. Raising the pool — the audit says one evaluate is already ~85% of the server's
capacity at 250, and four times the search on the bench's hot path is a cost decision.

**Original package text, left as written:**

**TWO FINDINGS BEFORE ANY CODE, AND BOTH CHANGE WHAT THIS PACKAGE CAN BE.**

**1. The selector this package names matches NOTHING.** It says *"any massing whose
`structural_logic` states a stacked plan"*. All 40 massings carry a `structural_logic` string and
**not one of them says the upper floor repeats the lower** — they state spans, bearing walls,
ventilation, roof framing and materials. `four-over-four`'s reads *"Two rooms deep requires an
interior bearing wall, which the stair hall supplies. Paired end chimneys serve four fireplaces
per floor."* The corpus's one authored sentence to that effect is on a PARTI —
`centre-passage-double-pile`'s description, *"two rooms either side, **repeated above**"* — and
one instance is not a population a prose reader may be built on
(`oq/a-room-records-prose-states-a-floor-its-own-band-does-not`'s 2-of-5 lesson).
**So no massing-level selector is available, and inventing one is authoring.** The authored,
machine-readable statement already exists and is per-room: `stacks_over`. A room whose author
wrote that claim is the corpus saying this room stacks, and honouring it needs no selector at all.

**2. A HARD STACKING PIN IN `geometry_cp.py` WAS ALREADY BUILT, MEASURED AND REFUSED (OQ 95).**
Its own comment: a hard version *"downgraded an authored kitchen wall to satisfy an inferred
stack"*, because the downgrade loop reads `[key for _t, k, key in core if k == "wall" and key]`
and a non-wall pin can never enter it — so a stack pin outranks every authored exterior wall in
the corpus, and a stack-only core makes the loop `break` and report infeasible. **The blocker is
the loop, not the pin.** This package's real content is to teach the loop a second pin kind and
an ordering, and then to measure both orderings rather than argue one.

**Baseline, measured 4 Sep before any change** (heuristic, one seed, all 16 plan records): 7
declared claims on the two shipped plans, **5 satisfied, 2 broken, 0 unjudged**; **45 transfer
beams** across the 5 records that have an upper level. The claims the diagnosis named are among
them — `spec-builder-colonial`'s Hall Bath over its laundry and the Tidewater Chamber Bath over
its powder room are the two broken.

For `four-over-four` (and any massing whose `structural_logic` states a stacked plan): passage over
passage, landing over stair, wet over wet, and every upper partition on a bearing line below are
HARD in `geometry_cp.py` and rejections in the heuristic, replacing the 40-point `STACK_W` charge for
that massing only. Both engines charge today and the charge did not run (J2). Measure fatals and
the transfer count before and after on both engines; WP-7.4's finding stands as the caution — a
term is worse in the middle of its range than at either end, and a rule is the end.

### WP-11.6 The container the programme describes

**Status: IN PROGRESS (4 Sep 2026) — layer 1 of 6 taught, in the ruled order, measuring after
each as the ruling requires.** `openings` reads the room's own element and
`geometry_report.multi_element` names **five** layers, down from six. The falling count is the
ruling's own check.

**THE INSTRUMENT FIRST, AND TWO OF ITS PROBES WERE WRONG.** The six defects are measured directly
rather than inferred from the disclosure list, so a name leaving that list is evidence. Baseline on
the reference fixture (the Tidewater plan with its kitchen, pantry and breakfast room tagged into a
west dependency, which is `test_geometry.py`'s own fixture):

| layer | probe | baseline |
|---|---|---|
| openings | dependency openings refused | **9 of 14** |
| structure | dependency partition inside the main wall set / the dependency's own envelope walls | **1 / 0 of 2** |
| vertical_score | upper edges credited to a dependency-only wall line | **0 — NOT REPRODUCED on this fixture** |
| lot_cap | built extent over the lot, uncapped | **24 ft over an 80 ft lot, `lot_capped: null`** |
| plan_check.drawn | dependency rooms convicted of reaching no exterior wall | **2** |
| export_ifc | dependency rooms off the slab | **3** |

**Two probes read 0 on the first run and neither zero was a defect's absence.** The openings probe
looked for a window drawn far from its room and found none, because the real defect is a window
REFUSED outright — every dependency opening came back *"the placement puts this room on no such
boundary wall"*. The structure probe read a `bearing_lines_x` key that does not exist. **A probe
pointed at the wrong defect and a probe reading a missing key both report zero, and zero reads as
"nothing wrong".** The lot probe reads 0 honestly on the shipped lot of 140 ft and needed a
narrower one to fire; `vertical_score` still does not reproduce and is recorded as such rather than
as absent.

**LAYER 1: `openings`.** `openings.envelopes()` maps each room to its own element's rectangle and
`_boundary_walls` tests against that. Refused dependency openings **9 → 5**, and the five that
remain are honest — the kitchen's north edge is 23.72 against its element's 29.12 and genuinely
does not reach that face. **The join is the room's own `block` tag, not a room list on the block**:
`blocks_record` writes no membership, so a first version read `b["rooms"]`, found nothing on every
plan, and left all nine refusals in place while reporting success.

**AND THE OLD READING DID NOT LOSE THE DEPENDENCY'S WALLS, IT ASSERTED ONE FORTY-ONE FEET AWAY.**
`x <= tol` is satisfied by any x at or west of 0.6, so a room at x = −41 tested as sitting on the
main block's west face. That is the mechanism behind the entry's *"a window drawn fourteen feet
from the room"*, and it is worse than reporting nothing.

**The one-rectangle regression holds**: both shipped plans place byte-identically, scores 685.3 and
592.3 unmoved, and `envelopes()` returns an empty map below two elements so every caller falls back
to the main block by construction rather than by luck.

**Still to do: layers 2 through 6** (`structure`, `vertical_score`, the lot cap, `plan_check.drawn`,
`export_ifc`), then the parti and plan re-authoring and CP-SAT's per-element solve.

**Original package text, left as written:**

**Status: NOT STARTED. UNBLOCKED — the four rulings of
`oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it` were taken on 4 Sep 2026
and this section carries them in full below.** This line read *"Blocked on the four rulings"* for
a day while the ruling sat 900 lines further down the same file, which is WP-6.4's finding
("until X lands is a lie the moment X lands") inside the plan of action rather than inside a
comment. Nothing checks a status word against a ruling in the same document. Part VII item 1;
findings A1, A2, B3, H1, I1, F7 — and the root of the twenty-two placer findings.

The ruling exists (2–3 Sep: strip the service out, a dependency is a second massing element, the
hyphen is a room chosen by style) and the machinery exists and is dormant (`blocks_for`,
`blocks_record`, plan schema 0.5.0). What is not ruled is the shape of what the six layers below
the placer are taught: whether an element has its own envelope, what the lot cap is on, whether a
hyphen is an element or a joint, and what the drawn layer measures `touches` against.
Recommended answers are in the questions below; the package is:
1. Take the four rulings; teach the six layers in the order the entry names, measuring after each
   (the shield lesson: `openings` first makes `structure`'s missing envelope a drawn collision).
2. Re-author `centre-passage-double-pile`: eleven enclosed ground rooms become four principal rooms
   and a passage in the main block, a portico as an element with its own exposures, and the six
   service rooms in a dependency reached through a hyphen room (`breezeway` or
   `gallery-corridor`, by style). The exemplar list stays.
3. Re-author `tidewater-georgian-careful` on the re-authored parti, with `block` on every room.
4. CP-SAT places per element (it refuses a multi-element plan today; the refusal becomes a
   per-element solve with the hyphen's abutment as a constraint — the seventh defect the entry
   names).

This package is where the sixteen downgrades go to zero, because the exposures the record declares
are a five-part house's and the container finally is one.

### WP-11.7 The facade as a result

**Status: NOT STARTED. Blocked on Lucas's Q2 and Q5 from
`docs/reports/wp-9.2-what-the-tradition-actually-does.md` §7.** Part VII item 5; findings G1, G2,
G3, G5.

For a centre-door diagram: the bay rhythm from the bay count and module, the door in the centre
bay, one window per bay per storey aligned, the blind bay under each stack — derived BEFORE the
rooms' windows, which then become the bays each room's front wall spans. Inverts
`centre-passage-core`'s facade-share test (the passage's width is a consequence of the bay it
takes, not a fraction of a facade decided elsewhere).

### WP-11.8 The bench chooses, and says which

**Status: NOT STARTED. Blocked on one ruling (does WP-6.3's proof-outranks-search transfer from
feasibility to composition?).** Part VII item 7; findings J2, J6.

Interim, needing no ruling and buildable with WP-11.1: when the CP objective did not run, the bench
draws the proof with the WP-11.1 banner AND offers the search's placement beside it with its
demerit score; `corpus._placed` records which it drew and why in `geometry_report.solver`.

### WP-11.9 The prose, executed

**Status: NOT STARTED. Mostly unblocked.** Part VII item 8; the report's Part VI table.

The twenty prose rules that table lists, each given a `test` beside its `statement` where WP-11.3
and WP-11.4 have not already done so: the stair setback ceiling of 12 ft (E4) from the Georgian
kit, `public-enfilade`'s "rooms diminish or grow in one direction", `entry-sequence`'s "each step
changes one condition", `stair-and-landing-core`'s half-pace window, the library's north, the
closet's "never from the front elevation", the kitchen's east. Every test is scoped by the record
that carries it — a room rule on the room, a grouping rule on the grouping, a style note through
`style_variation` — which is Part IX's stratum discipline made mechanical.

### WP-11.10 The placer's shape terms, on the right box

**Status: NOT STARTED. Blocked on WP-11.6.** Part VII item 9. `WIDTH_W`, the flat 12, and the
direction-to-the-square the 3 Sep ruling opened, measured on the container that can hold the
programme. Not before: a term measured on the wrong box measures the box.

### WP-11.11 The diagnosis as an instrument, and the per-parti pass

**Status: NOT STARTED. Unblocked.** Part IX's method.

`build/diagnose_sheet.py <plan> [--engine]`: prints the diagnosis's Part I tables for any placed
plan — every room's drawn rectangle beside its declared one, its placed and declared exterior
walls, the front's openings per storey and their alignment, the solver's downgrades and objective
status, the six baseline numbers — so the next parti's diagnosis starts from a generated Part I
rather than from pixel-reading a screenshot. Then the per-parti precedent pass, one parti at a
time from `partis/*.json`'s own `exemplars`, each producing a Part II table in
`docs/reports/precedents-<parti-id>.md` and a Part VI list of that parti's prose rules without
tests. Twenty-one, not one hundred and sixty-four.

### Questions for Lucas — ALL FIVE RULED, 4 September 2026

**Lucas took every recommendation.** Each answer is recorded below beside the question it settles;
the two that change corpus or bench semantics beyond one package have register entries of their
own (`oq/the-facade-is-a-result-not-an-input`,
`oq/a-proof-of-feasibility-is-not-a-proof-of-composition`), and the four-part massing ruling is
appended to `oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it`, which moves
from OPEN to RULED. The axis tolerance and the hearth schema are package-level authoring decisions
and live here.

**A ruled number with no source is still editorial.** The axis tolerance is half a bay module
because that admits the period's own "slightly off-center" passages and refuses a passage in an end
bay; no source states it, so wherever it lands in the corpus it carries `judgment: true` and says
so, exactly as `storey-graduation`'s 7.5 in riser divisor does.

1. **The axis tolerance (WP-11.3). RULED: half a bay module for the passage; no tolerance for
   the door.** A centre passage's centreline may sit up to half a bay module from the footprint's
   centre — which admits Westover's and Wilton's *"slightly off-center"* passages and refuses a
   passage in an end bay — and the front door is in the centre bay or it is not. Editorial, marked,
   with the period reading in `docs/reports/tidewater-layout-diagnosis-2026-09-04.md` II.2 item 2.
2. **The hearth's schema (WP-11.4). RULED: a LIST on the room, the wall authored, the width
   derived and editorial.** A keeping room can have two; the wall is a plan fact its author states;
   the opening width comes from Morris's Lecture 6 table as an editorial derivation carrying
   `judgment: true` until an American source is read, per the study's §6 item 6 — a London figure
   may not be imported into a Chesapeake record as though it were measured.
   *(Delivered as Morris's own RULE rather than his table: Lecture VI Rule II,
   `sqrt(L + B + H) / 2` in feet, which is what he calculated the table from. The ruling's
   substance is unchanged — the figure is editorial and carries `judgment: true` — and the wording
   is left as it was given. WP-11.4's report has the reason the table was worse: interpolating it
   clamped at both ends.)*
3. **The four questions of `oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it`
   (WP-11.6). RULED, all four, and the entry carries them in full.** An element has its own
   envelope and its own roof with a stated ridge relation; the lot cap is on the BUILT EXTENT
   including the hyphen, which is roofed ground; the hyphen is a THIRD ELEMENT carrying one room
   (it stays a room — that was ruled 3 Sep — and the element is what the room is placed in); and
   the drawn layer measures `touches` against the room's own element, with a wall facing the hyphen
   gap named as exterior-to-the-weather rather than convicted as landlocked. **The order the six
   layers are taught is the operative half of the ruling** and is stated in the entry:
   `openings`, `structure`, `vertical_score`, the lot cap, `plan_check.drawn`, `export_ifc`,
   measuring after each. `geometry_report.multi_element` names six layers today and must name
   five, then four, then none.
4. **Q2 and Q5 of the tradition study (WP-11.7). RULED: the facade IS a result, and the sequence
   is the EXPLANATION, not the architecture.** `oq/the-facade-is-a-result-not-an-input` carries
   both halves and what they cost: `centre-passage-core`'s facade-share test inverts (the passage
   takes a bay and its share is reported, not required), `passage-that-is-a-corridor`'s
   `correct_practice` is wrong in its instruction as well as its number, and the system stays a
   constraint system whose findings are NARRATED in the commitments' order — because Glassie's own
   rule sets are order-independent and a pipeline cannot backtrack when a dependency will not fit
   the lot.
5. **Proof versus search on the bench (WP-11.8). RULED: WP-6.3's principle does not transfer.**
   A CP placement outranks a hill-climb placement on FEASIBILITY and on nothing else; where the
   compositional objective did not run the bench draws both and labels both, and the plate says
   which it drew and why. `oq/a-proof-of-feasibility-is-not-a-proof-of-composition` carries the
   measurement it was taken on and the two things it does NOT rule — whether the budget should
   simply be larger, and whether a placement that set aside sixteen declared facts should be drawn
   at all.


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
