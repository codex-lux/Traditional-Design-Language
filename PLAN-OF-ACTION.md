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
| **8 — The register, the backlog and the scopes nothing reads** | **WP-8.1**, **8.2**, **8.3**, **8.4**, **8.6**, **8.7**, **8.8**, **8.9**, **8.10**, **8.11**, **8.12**, **8.13**, **8.14** *(no 8.5 — see the note in CLAUDE.md; it shipped as `6f9e7c7` before the numbering existed)* | **8.1-8.4, 8.6 complete (28 Aug 2026); 8.7-8.14 complete (2-4 Sep); OQ 51's delivery half FINISHED and AUDITED** — **WP-8.8** made the baked-snapshot class knowable (135 judged, 0 stale, 8 unjudgeable for want of a recorded binding) and found the evaluator the question asked for had existed in two places all along. **WP-8.9** measured OQ 51's flip before building it and found the ruling had been taken on `unendorsed` — a count of ROLE GAPS — where the thing a gate stops is DELIVERIES: 2,899 slots, not ~223, a factor of thirteen. Put back with the numbers, Lucas ruled *stage it pack by pack* and *a separate field*; the `--stranding` meter and the `delivery: opt-in` / `inherits_packs` mechanism shipped inert. **WP-8.10** landed the first flip and built the loudness the ruling required: `trim-classical` is opt-in, six vouched nodes admit it, 10 slots over 10 nodes are stranded, and every stranded slot in the corpus (2,889 of 2,889) now NAMES the pack withheld and why. It found the meter's gate and the mechanism's gate were different predicates (10 against 15, one of the five a shipped reference plan), that `measure()` could not see a flip at all, and that the flip was sold on a corpus-level writer count that described no node — the same wrong-grain error as WP-8.9's, one package later. — **WP-8.1, WP-8.2 and WP-8.3 are COMPLETE**: the open-question register is a DIRECTORY, one file per question, because a single shared file is where two parallel sessions' answers to "what is the next id" both survive a merge — four times in four days, and nothing in the corpus checked for a duplicate id at all. `check_ids.py`, a generated index, a CI gate that fires before the merge rather than after it, and §1 amended so open questions and work packages are ids like every other. **OQ 90 closed on the way**: this branch's chain moved 5.7→5.11, 5.8→5.12, 5.9→5.13, 5.10→5.14 and main's atlas kept 5.7 — 53 of WP-5.7's 87 references moved, each attributed by `git blame` rather than by `sed`. **WP-8.2** built OQ 51's refusal half (`declined_packs`), refused the per-edge deny on measurement, and found the meter wrong by 27 in the flattering direction — 222 unendorsed was really 249 and 71 endorsed really 38. Ten declines moved `unendorsed` by zero, which is why `judged` is now a floor. It raised **`oq/forbidden-stops-the-pack-cascade`**: 787 pack rules dimensioning a slot the kit forbids, not one of them chosen by a human. **WP-8.3** made `forbidden` stop the pack cascade too (`oq/forbidden-stops-the-pack-cascade`) and found that `elevation.py` reaches packs by `PE.resolve` and never through the resolver — a second path nothing had named, 46 pairs, 16 refused and 24 disclosed. **WP-8.4** read the exception preconditions -- 331 records, 123 naming a construction, and not one line of code had ever consulted any of them. `granted_when` (renamed from a second `applies_when` in the same schema), a closed 61-token construction vocabulary over variant ids that already exist, three verdicts with the unjudged case judged BOTH WAYS and reported unjudged only where the two rules disagree. It also collided head-on with main, which had shipped its own OQ 88 scope, its own OQ 99 and its own WP-8.1: **ruled -- main's `scope` field survives and this vocabulary is ported into it**, after measuring that main's substring classifier over the cladding disagreed with each node's own `construction_type` on 13 of 164 styles, `cape-dutch` among them, which is OQ 88's own bug surviving inside OQ 88's fix. OQ 86 closed (`kit_vs_pack` read the node's own file, 62 -> 1,231), OQ 90 closed at its third option (a WP number is a label; cite the report), and OQ 89's remainder swept up: `elevation.py` read `shutter` and `window_head_masonry` off the RAW kit under a comment naming `shutter` as needing the cascade. Report: `docs/reports/wp-8.4-the-exception-precondition.md` · new questions: `oq/applies-when-means-two-things`, `oq/a-baked-pack-value-is-a-second-delivery-path` **WP-8.11** flipped `facade-gable` (32 slots over 29 nodes, 29 of them `cornice_return`, whose only writer in the corpus is that pack) and found that BOTH suites drove the opt-in gate through the very pack about to be flipped -- a counterfactual that becomes the status quo, stays green and stops testing anything. **WP-8.12** flipped `sash-light` (70 slots over 34 nodes) and falsified WP-8.11's own two-point claim that the refill is roughly proportional: 4 gaps from a 10-slot flip, 13 from a 32-slot one, 10 from a 70-slot one. The refill is now landing ENTIRELY on the five packs whose `applies_to` arms a live gate (3 of 13, then 10 of 10), which follows from the staging order rather than chance and is worth a ruling before the remaining flips. `judged` is 249 after all three flips and 136 withheld arrivals: zero cases read. Reports: `docs/reports/wp-8.1{0,1,2}-*.md`. **AND THE THREE-FLIP FIGURES ABOVE ARE THAT MOMENT'S, NOT THIS TREE'S** -- WP-8.13 and WP-8.14 flipped the remaining five, and the live meter on the merged tree reads role_gaps **222**, inherited_packs **2,762**, unendorsed **180**, `judged` **250** and **396** withheld arrivals over all eight flipped packs. The row's own status cell said 8.7-8.14 complete while its narrative stopped at 8.12; re-measured at the 7 Sep merge rather than left to be read as current. |
| **9 — Arrangement** | **WP-9.1, 9.5, 9.6, 9.7** complete · **9.2 text half done, image half waiting on Lucas's download** · **9.3 part built** · **9.4 COMPLETE AND ITS OWN PREMISE REFUSED** (`docs/reports/wp-9.4-the-unit-was-not-the-problem.md` — cite the FILENAME, two WP-9.4s exist) | **In progress (1 Sep 2026; this row was corrected on 3 Sep, having said "9.2, 9.3, 9.4, 9.5 not started" while four of those five had moved and two more packages had shipped with no section of their own — see `docs/reports/project-review-2026-09-03.md` §VII. The 9.4 cell in that same correction still said NOT STARTED and was itself wrong — the package had run on 1 Sep and refused `parti_slice` with its measurement, a probe taking fatals 3 to 8. Corrected again hours later; see that review's §IX, which is about this exact line)** — raised by Lucas against a rendered sheet, and the founding failure mode one level above Phase 6: a 10 x 30 ft kitchen, a portico off the axis of its passage, a dining room landlocked mid-house. The corpus already stated every band the sheet broke and **twenty-seven of the twenty-eight plan-measurable faults came back UNJUDGED** because nothing had ever supplied a plan-arrangement variable. **WP-9.1 is the arbiter and only the arbiter** — no solver, no renderer, both reference plans byte-identical — because seven of the solver's eight arrangement score terms had no critic counterpart at all, against `plan_check.py`'s own stated principle that the search charges preferences and the critic is the arbiter. Six of Lucas's seven complaints are named; the seventh (the passage) the corpus declines to call a fault, which is stated rather than invented around. A plant-room zero was built, convicted BOTH reference plans and was withdrawn; the first shape check convicted the GOOD plans and lost the direction the corpus does not state. Report: `docs/reports/wp-9.1-the-arbiter-for-arrangement.md` · new question: `oq/a-daily-route-is-an-editorial-model` |
| **10 — The second massing element** | **WP-10.1** | **Complete, and two of its three packages withdrawn by its own audit (3 Sep 2026)** — OQ 40 ruled a dependency a second massing element and the machinery ships and is DORMANT: the block placer, `exterior_score(bounds=)`, plan schema 0.5.0, both reference plans byte-identical. The service strip and the hyphen-as-a-room were WITHDRAWN when the audit found eight blocking defects, five of which reduce to **six layers below the placer reading the main block as the whole building** — a garage window drawn 14 ft from the garage, a span manufactured across the hyphen gap, a house reporting `lot_capped: true` at 34 ft wider than its lot. CP-SAT refuses a multi-element plan rather than flattening it (which had also flattered a number this session published); `geometry_report.multi_element` discloses the six. Report: `docs/reports/wp-10.1-the-audit-of-the-dependency.md` · new question: `oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it` |
| **11 — The drawn sheet** | **WP-11.1 … WP-11.8** · the rest planned | **WP-11.1 complete (4 Sep 2026)** — raised by Lucas against a rendered sheet set beside four exemplar plans, and diagnosed before he said what was wrong. The finding that organises it: **the instrument already owned a written graphic standard and the plan sheet did not obey it** — `tokens.css` has carried Graphic Standard No. 1 verbatim since WP-5.2 while `render_plan.py` drew in a dark instrument palette that `svg_theme.py` translated on the way to the browser, so the sheet had the standard's COLOURS and none of its GRAMMAR. `build/sheet_style.py` is the one spelling (52 hex literals in the four renderers → 0, all ten sheets byte-identical across the move); the wall is a BODY at the three thicknesses `structure.wall_thickness` has computed since WP-3.1 and no drawing had ever read, so the sheet now says which walls CARRY; an opening is a hole cut from `derive_openings`' own spans; the room washes are gone and the paper is the room; and the six banner lines are a margin schedule below a ruled border. **Two registers, ruled by Lucas 4 Sep**: `presentation` for a reader, `working` for the marks, one renderer, the plate saying which. **Three existing guards had selectors this package retired and all three would have passed vacuously**, and widening the fourth opened a hole a mutation found — `LIGHT` vouched for itself. Reports: `docs/reports/wp-11.1-the-sheet-in-its-own-standard.md` and `docs/reports/wp-11.2-the-pen-ladder-and-the-wall-the-record-states.md` · new question: `oq/the-placement-carries-no-wall-bands`. **WP-11.2** put the workbench's own sheet on the same ladder (19 inline stroke widths → 0) and gave both renderers ONE wall to read — `footprint.wall`, plan schema 0.5.1, from `build/assemblies.py`, a leaf on `storeys.py`'s precedent. **The browser walk ran for the first time in a session on this branch** and caught a defect 81 unit tests and a clean build both missed |
| **11 — The house the sheet should have drawn** | **WP-11.1 through 11.9, 11.11 and 11.12 COMPLETE · 11.10 PART-BUILT (its container question answered and REFUSED; the three shape terms remain) · then the adversarial audit of 11.9-11.11** | **In progress (4-7 Sep 2026); all five rulings taken the same day** — raised by Lucas against the workbench's own sheet for `tidewater-georgian-careful` with the instruction to diagnose before building. The diagnosis is `docs/reports/tidewater-layout-diagnosis-2026-09-04.md` (cite the filename): fifty-one findings in ten tiers, eight root causes, and the finding that decides the order — the sheet's *"PLACEMENT PROVED (CP-SAT) AGAINST THE RECORD'S DECLARED FACTS"* sits over a placement that set aside SIXTEEN declared exterior walls (both ends of the passage among them) and whose compositional objective never ran (`objective: null`, "best of 1"), so every soft term the corpus has was inert on the engine the bench draws by default, and the search it refuses to draw scores 712.6 against the proof's 835.0. All five of the phase's questions were ruled on 4 Sep and **11.1 through 11.9 and 11.11 have shipped**, 11.10 is part-built, and an adversarial audit of the last three found 38 things (`docs/reports/audit-2026-09-07-the-things-the-session-did-not-measure.md`); **this row still read "11.1 through 11.5 COMPLETE" after the 7 Sep merge**, which is the board going stale at exactly a merge for the sixth time; the container (11.6) is unblocked by the four rulings of `oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it`, taken the same day. **This sentence said the container WAITED on those four rulings in the same breath as saying all five were taken** -- a contradiction inside one sentence, corrected by WP-11.5 and the same class as WP-11.6's own status line below. The phase's own section carries the ruling on each. **WP-11.12 is not about the house**: Lucas raised the corpus job at 39 min 32 s, which was the whole wall-clock of a pull request, and it is six parallel shards at about seven minutes now -- `pytest tests/` was 87% of it, and 46 s of the checkers were `jsonschema.validate()` rebuilding the same validator 2,400 times a build |
| **11 — The precedent bench** | **COMPLETE — WP-11.1 through 11.7** | **Every buildable node carries a precedent and every node at every rank cites a source (5-7 Sep 2026)** — Lucas asked where the research is thin and for each style's most beautiful and iconic precedents with links. The corpus WAS templated on the surface when surveyed (2-4 exemplars, 4-5 sources, 5 constraints on every buildable node; the three tranches moved the exemplar clause to 800 and moved none of the other three) and what discriminates was tracked nowhere: 542 `measured` kit figures with no source (536 today — six were sourced to a building under Ruling A), an exemplar with no locator, 24 nodes citing only what ANOTHER NODE cites ("a sibling" until WP-11.7 corrected it in ten places across eight files). `precedents/` is the building's own record now, `check_precedents.py` and `check_research.py` are the guards, `tdl_precedents` the 27th tool; the research ran in four tranches. **Tranche 4 (WP-11.7, 7 Sep) wrote 156 sources over the 32 higher-rank nodes — 111 citations of 109 DISTINCT works new to the corpus, plus 45 reuses — and took `sourceless_nodes` 32 → 0**, and found the layer has no identities: 422 free strings, 0 URLs, one confirmed fiction cited by five nodes, and 23 works under 51 spellings whose correction would redden the `shared_only` ceiling by six. Report: `docs/reports/wp-11.1-the-bench-without-a-literature.md` |
| **12 — The sheet in the round** | **WP-12.0 through 12.8** | **WP-12.0 through 12.4 complete (8-9 Sep 2026); 12.5 through 12.8 not started** — raised by Lucas against Dilum Sanjaya's post on 2D schematics transitioning into 3D, with the question whether SVG remained the medium. **The brief is the PRD**, `docs/prd/phase-12-the-sheet-in-the-round.md` (cite the filename; it is the first document in a new `docs/prd/`). The answer is WP-5.11's, one dimension up: the format was never the constraint, and the missing thing is a constructed-3D layer between the record and the camera — `build/scene.py` — with three.js drawing what Python models and the SVG plates staying authoritative and held to it. **All nine rulings taken the day they were put, and an APPROACH perspective view added to v1.** The review that adopted the PRD found the defect that made WP-12.0: **the drawing set is not one building** — the elevation and roof plates are built with no section, so they take `structure.build_section`'s heuristic default while the plan beside them is a CP proof, under a banner WP-6.4 wrote saying one drawing set is one building or it is nothing. It also found that `render_elevation` has taken a `face` since WP-3.2 and no client has ever sent one, so three of the four elevations this system can draw have never been seen |

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

**It shards since WP-11.12 and CI runs six of them.** `python3 build/check_all.py --shard 2/6` is one sixth of the same work and `--list-units --shard 1/6` prints the assignment; a bare `check_all.py` is `--shard 1/1` and is the run it always was. Run the bare one before declaring a package done -- a shard is green about its own sixth, and the operating rule above is about the suite.

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

**Ruled 8 Sep 2026 (Phase 12), all nine on the day they were put:**

- **The Round's nine rulings** (PRD §12, `docs/prd/phase-12-the-sheet-in-the-round.md`). Ruled as recommended: **R1** `three` is the workbench's third runtime npm dependency, pinned exactly and reachable only through a dynamic `import()` in one module, with `check_frontend.py` holding it out of the entry chunk; **R2** the plan cut is 4′-0″ above finished floor, `kind: editorial`, one named constant printed in the caption; **R3** the cornice is swept to the envelope rule with the order's own projection drawn as a construction-weight ghost and both named on the plate, and the overhang is the swept cornice and nothing more; **R4** porch columns are placed only where a bound pack states an intercolumniation, never inferred from a width; **R5** the door height where the record states none is `export_ifc.py`'s own editorial constant, imported rather than restated; **R6** the Round lives on the Drawing Set, with a chip from the Plan Workbench; **R7** the phase stays in JS/JSX with JSDoc types — a TypeScript migration is an app-wide package with its own ruling, and mixing conventions in one folder is what WP-5.6 spent a package removing; **R8** the axon is true isometric, as a token so a dimetric ruling is a one-line change; **R9** grade is drawn flat in v1 and the caption says so.
- **And one addition to the PRD: an APPROACH view is in v1, not v2.** A perspective camera at 5′-6″ on the entrance axis, named in the view bar, its dimensions and datums withheld with the caption saying why — a perspective dimension is never true. It is a camera and the camera is a serialiser; no geometry changes to carry it.
- *Each of these is recorded on the day it was given rather than the day it was expected, which is `docs/reports/wp-8.14-the-number-nobody-policed.md`'s sibling finding: an unverified ruling reads exactly like a ruling, and nothing in this tree checks one.*

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

**Status: THE NAMING STEP IS DONE AND ITS OWN FIGURES WENT STALE IN EIGHT FILES (2 Sep 2026).** The step every list still named as WP-4.4's next — giving the asset records their `provenance.building` names — finished on 31 Aug, and a dry run now assigns **zero**: 786 of 1,850 records name a building across 305 queries, 180 of them inside HABS's charter. Twelve claims across eight files still said 322, 845, 330 and 188, two of them instructions to do work that was finished, while `check_counts.py` reported 0 stale in the same run — every stale figure sat in a field no claim covered, and **this file was not in the checker's list at all**. Four values are computed now and nineteen claims guard them. `check_assets.py` also gained the check it never had: a building name must be an exemplar of a node the record depicts, its location that exemplar's own, on a photograph that is not `role: incorrect` — **all 786 pass, including the 161 written by hand**. **The 72 records on 18 exemplar-less higher-rank nodes are named as of WP-11.6** (5 Sep 2026): Ruling B gave every family type specimens derived from its members' icons, so those nodes have exemplars to deal from, and the ruling this sentence asked for is the one that arrived. Nothing is left for this step offline; the acceptance line (≥100 sourced, zero `license: unknown`) stands at 73 and 1,716 and needs the network. Report: `docs/reports/wp-4.4-the-record-that-said-322.md`.

**Status (31 Aug 2026): THE HARVEST IS STILL BLOCKED; 73 RECORDS WERE NEVER BLOCKED AND ARE NOW SOURCED, AND THE MANIFEST NOW COVERS THE CORPUS.** `322 wanted / 0 sourced` over three style nodes is `1,777 / 73` over 142 — the manifest was a frozen snapshot and the generator had been tracking the corpus all along. **858 records now name a real building** across 312 distinct queries, where 161 named eleven; 183 of those queries are within HABS's US charter. The acceptance line — "at least 100 sourced or generated" — is NOT met by the 73 drawn plates, and widening the authored assembly filter to reach it was refused rather than done. The eleven carry a `generated_from` block naming a proportion pack, and `build/render_profile.py` draws them from the corpus's own geometry — no network, no rights clearance, and everything needed has been present since WP-5.11. The harvester's four defects were also fixed, none of them findable by running it: a rate limit three times loc.gov's ceiling that would have returned 0 after being blocked, an unconditional `license: public-domain` the source does not state, a selector that preferred a record holding no images, and 161 records collapsing onto eleven queries behind a guard testing the opposite condition. Report: `docs/reports/wp-4.4-the-eleven-that-were-never-blocked.md`. **The routes question is ruled** at `oq/fetching-through-a-tier-the-proxy-denies`, and CI — the only tier that can fetch bytes — has not run since 29 Aug.

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

### WP-8.14 The audit of the four flip packages (OQ 51)

**Status: COMPLETE, 4 September 2026.** Report:
`docs/reports/wp-8.14-the-number-nobody-policed.md`.

Adversarial audit of WP-8.10 through 8.13, by this repository's own three techniques: re-derive the
number rather than re-read the sentence, revert each fix and watch the suite, and assert the
mutation landed before believing the colour.

**The arithmetic held**, which is unusual here — all eight per-pack stranding figures re-derive
exactly, the combined 202 reproduces, un-flipping all eight returns the corpus to 7,830 (the
pre-flip baseline, to the slot), the branch order is guarded, and both of WP-8.13's own gate-lift
fixes bite under mutation.

**What it found is one stale number and the reason it was possible.** `check_counts.py` derives six
OQ 51 values and holds the prose to each; `unreached` was the seventh and was derived by nothing.
`CLAUDE.md` said **111 slots survive a flip whatever it does** for three flips after it stopped
being true (179 → 111 → 96 → **47**), while `tests/test_stranding.py` was re-pinned at every one.
Closed as a three-link chain — the constant joins `STRANDING` where the sweep holds it to the
corpus, `check_counts` holds the prose to the constant, and a test holds the key in the dict.

Also: three spent instructions still written in the present tense (WP-6.4's rule at the scale of a
whole entry), and WP-8.13's *"the sum is a bound in neither direction"* asserted from a
one-directional measurement — the other direction is 223 against 181 and 202, so the inequality
inverts with the direction and **a per-pack figure is a property of the corpus it was measured
against, not of the pack.**

**§VI, added after the audit was committed: the audit corrected those spent instructions in
`CLAUDE.md` and did not sweep, and SIX survived across five files.** The substantive ones are the
two surfaces `check_inheritance.py` PRINTS — its `--strict` footer (a superseded ruling, a spent
instruction, and two counterfactuals that re-derive to 0) and its `--stranding` argparse help —
plus the falsified `judged` comment corrected 700 lines away in the same file. **`check_counts.py`
reads markdown only and never opens `build/*.py`**, so a number a checker prints sat outside every
guard for exactly the structural reason `unreached` did. The companion rule: §III says name the
figure the checker does not derive; §VI says **name the SURFACE the checker does not read.** Fixed
by carrying no number — the illustrations are deleted from the CLI and kept in the past tense in
`CLAUDE.md`, where they are the record of why the order was chosen. No checker was extended to
scan `build/*.py`, and the reason is stated.

### WP-8.13 The last five packs, and the finding the flip dissolved (OQ 51)

**Status: COMPLETE, 4 September 2026 — OQ 51's delivery half is FINISHED.** Report:
`docs/reports/wp-8.13-the-programme-that-dissolved-its-own-finding.md`.

Lucas re-ruled the staging on 4 Sep: the five live-gate packs go in ONE package, not five.
WP-8.12 had measured the refill concentrating entirely on them (3 of 13 new gaps at the second
flip, 10 of 10 at the third) — a property of the staging order, which back-loaded exactly the rows
whose adjudication authorises a behaviour change. Staging them singly would have spread the one
decision that mattered over five packages.

`opening-proportion`, `facade-classical`, `storey-graduation`, `timber-bay` and `gibbs-ionic`
declare `delivery: opt-in`. **26 opt-ins, 202 slots over 62 nodes**, and all eight packs the
programme ever named are flipped.

Four findings. **The combined flip strands MORE than the sum of its parts** (per-pack 181,
combined 202) because the five rehouse each other — the sum bounds it in neither direction, and
this is the third instance of the wrong-grain shape and the first caught before publication.
**The flip dissolved WP-8.12's own finding**: refill 4/13/10/36 across the four flips, but 0 of
36 on a live-gate pack against 10 of 10 last time. **`judged` moved 249 → 250 and `measure()`'s
own comment said it could not** — via `endorsed`, not `declined`, when a vacated role
re-attributes to a pack the node opted into and whose `applies_to` names it; one instance, pinned
by name. **An opt-in needs two conditions and this package first wrote one** — `check_opt_ins`
refused 14 of 40 because `applies_to` says a pack is FOR a style and says nothing about whether
the cascade delivers it there; all 14 were no-ops, proved by every stranding figure staying
byte-identical.

Also: the driven-fixture rule **expires** ("scheduled last" has nowhere to point once the schedule
empties — it is "not scheduled at all" now), and the `CLAUDE.md` trap that **an unverified ruling
reads exactly like a ruling**, raised because this session published a ruling in a PR body before
it had been made.

### WP-8.12 The third flip, and the refill that was not proportional (OQ 51)

**Status: COMPLETE, 3 September 2026.** Report:
`docs/reports/wp-8.12-the-refill-that-was-not-proportional.md`.

`sash-light` flipped: seven opt-ins, **70 slots over 34 nodes**, two-gate gap 70 against 84.

**Two findings worth carrying.** The refill is NOT proportional to the flip — 4, 13, then 10 from
10-, 32- and 70-slot flips — which falsifies WP-8.11's own two-point reading one package later.
And **it is concentrating on the gated packs**: ten of ten promoted `opening-proportion`, against
three of thirteen last time, because the gated packs flip last and therefore inherit every role the
earlier flips vacate. The order chosen to make the early flips safe back-loads the rows whose
adjudication authorises a behaviour change. **Put that to Lucas before the gated packs come up.**

Also: a driven fixture should name a pack scheduled LAST (WP-8.11 pointed one at the very next
pack), and the ruling table's `>= 150 rows` vacuity floor became a cross-check between the pack
headings' own counts and the parsed rows.

### WP-8.11 The second flip, and the fixture that would have gone quiet (OQ 51)

**Status: COMPLETE, 3 September 2026.** Report:
`docs/reports/wp-8.11-the-second-flip-and-the-fixture-that-would-have-gone-quiet.md`.

Closes `oq/a-pack-can-be-the-only-writer-a-node-has` on Lucas's ruling — no new rule, stage by
size — and flips `facade-gable`: two opt-ins, **32 slots over 29 nodes**, of which 29 are
`cornice_return`, the pack being its only writer in the corpus. That is the ruling exercised.

**The finding is about tests.** Both suites drove the gate through `facade-gable` *because* the
corpus left it on `cascade`; flipping it for real would have made every assertion a statement
about the shipped corpus — green, and vacuous. Both fixtures moved to `trim-craftsman`, and the
rule is now in their docstrings: **a driven fixture must name a pack nobody has flipped.** That
sentence ended *"check it before flipping `sash-light`"* until WP-8.12 flipped it; with the
schedule empty (WP-8.13) the durable form is a pack nobody PLANS to flip, and the fixtures name
one.

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
**Status: TEXT HALF DONE, IMAGE HALF STILL WAITING ON LUCAS'S DOWNLOAD.** *(4 Sep 2026, WP-11.1: the six
buildings' HABS written data now lives in `precedents/` as records with quotes and `as_printed` figures —
`gunston-hall`, `westover`, `drayton-hall` seeded from this package's own extracts, the rest in Tranche 1 —
so the text half has a home in the data rather than in a report's table. The sheets are still not here.)*
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

> **MERGED WITH THE OTHER PHASE 11 ON 8 SEPTEMBER 2026.** This board and the precedent bench's
> board below it both stand, neither renumbered, exactly as the two Phase 9 boards do. The
> reconciliation is not a work package and has no WP number; its record is
> `docs/reports/the-merge-of-the-two-phase-11s-2026-09-08.md`, and **it is the one to read before
> quoting a figure either line published**, because almost every pin either side held is now a
> third value belonging to neither parent. Two open questions came out of it —
> `oq/the-bay-parity-and-the-band-ranking-compose-worse-than-either` (the one real cost, worse
> than either parent on one axis) and
> `oq/the-measurement-that-defaulted-the-stacking-rule-has-inverted`.

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

**Status: ALL SIX LAYERS TAUGHT (4–5 Sep 2026), in the ruled order, measuring after each as the
ruling requires, THE PLACER'S HALF OF THE RE-AUTHORING WITH THEM, AND **ITEM 4 — CP-SAT PLACES PER
ELEMENT** (5 Sep). The parti re-authoring is REFUSED BY THE CORPUS (three hard room rules, jointly
unsatisfiable once the elements are real — `oq/three-hard-room-rules-forbid-a-detached-kitchen`).
The entry stays OPEN on the ruling's own two unbuilt items.** `openings` reads the room's own
element, `structure` runs once per element, a cross-element stacking claim is unjudged rather than
charged, the lot cap is on the built extent with the hyphen counted, the critic measures `touches`
against the room's own element, `export_ifc` writes a slab per element, and
`geometry_report.multi_element` names **no** layer, down from six. The falling count is the ruling's
own check and it has fallen to zero. **What is NOT done, and this line says so rather than letting
a reader infer it**: the per-element ROOF with its stated ridge relation (ruling 1's second half)
and the abutment between adjacent elements — plus this package's own remaining part, the parti and
plan re-authoring, which the corpus refuses until
`oq/three-hard-room-rules-forbid-a-detached-kitchen` is ruled. **Ruling 3's "seventh defect" turned out not to need a constraint**: `_build`'s
door rule is ALREADY a hard abutment (`a.x + a.w == b.x`), vacuous while every room shared one
rectangle and real the moment the elements are. What it needed was the other half — a door between
elements that do NOT touch is not the model's fact — because a detached dependency is detached and
proving a buildable house impossible is the one thing a hard constraint here must never do.

**AND THIS LINE SAID "LAYERS 1 THROUGH 4" AND "TWO" THROUGH THE WHOLE OF LAYER 5, IN A PUSHED
COMMIT WHOSE MESSAGE SAYS THE PLAN BOARD WAS UPDATED.** Two replacements went into one script, the
second assertion failed, and the script died before writing — so NEITHER landed; re-running only the
second put the layer-5 section in beneath a status line describing layer 4. It is `65901a2`'s shape
exactly, which CLAUDE.md records as *"the hand correction itself failed to land"*, met again four
paragraphs from where that entry is quoted. **A multi-edit script must write what it can or assert
before it edits anything** — and re-read the file after correcting a number in it, which is the only
thing that has ever caught one of these.

**THE INSTRUMENT FIRST, AND TWO OF ITS PROBES WERE WRONG.** The six defects are measured directly
rather than inferred from the disclosure list, so a name leaving that list is evidence. Baseline on
the reference fixture (the Tidewater plan with its kitchen, pantry and breakfast room tagged into a
west dependency, which is `test_geometry.py`'s own fixture):

| layer | probe | baseline |
|---|---|---|
| openings | dependency openings refused | **9 of 14** |
| structure | dependency partition inside the main wall set / the dependency's own envelope walls | **1 / 0 of 2** |
| vertical_score | upper edges credited to a dependency-only wall line | **0 — NOT REPRODUCED on this fixture** |
| lot_cap | built extent over the lot, uncapped | **24 ft over an 80 ft lot, `lot_capped: null`** — corrected at layer 4 to `false` |
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

**LAYER 2: `structure`.** `build_section` runs `wall_lines`/`bearing_lines`/`span_check` once per
element at that element's own origin. Walls tagged `main` outside the main block **1 → 0**, the
dependency's own envelope walls **0 of 2 → 2 of 2**, and a span across the gap is impossible by
construction. **Its structure, judged for the first time, immediately fails** — 27.0 and 20.07 ft
against a 20 ft cap, which is the ruling's own predicted shield lesson.

**AND TEACHING LAYER 1 MADE LAYER 5'S FINDING DISAPPEAR WITHOUT FIXING LAYER 5.** `plan_check`'s
landlocked test short-circuits at `if seated: continue`, so seating the dependency's windows took
"reaches no exterior wall" from 2 to 0 while the `touches` arithmetic below stayed wrong. A meter
watching the finding would have reported layer 5 taught two layers early. Driven, it convicts 2
rooms. **Three probes in one package had to be corrected and all three would have read a clean
zero.**

**LAYER 3: `vertical_score`, and the entry's own description of it was HALF WRONG.** The support
credit it named — an upper wall within 0.75 ft of a dependency line scoring as continuing to a wall
below — **cannot fire**, because the placer lays only level 0 into elements and the nearest
dependency face is 14 ft from the main block against a 0.75 ft tolerance. Measured and pinned
rather than fixed. What was real is the opposite sign: a `stacks_over` claim naming a room in
another element was **charged 40 points** for a failure no placement could avoid. Unjudged now,
with its reason; `vertical_score` **114 → 74** on a driven fixture. The wet-stack test needed no
change and that was measured too.

**LAYER 4: the lot cap, and its bypass was never about massing elements.** The cap is on the
BUILT EXTENT with the hyphen counted (ruling 2), through `flank_sizes` — the sizing `blocks_for`
already did, lifted out so the cap reads one spelling. On the fixture at an 80 ft lot: main block
**63 → 45 ft**, built extent **104 → 86 ft**, `lot_capped` **false → true**. **The baseline in the
table above was itself wrong** — `lot_capped: null` was read off `footprint.lot_capped`, which does
not exist; the true reading is `false`, which is worse, because `null` looks like a record declining
to judge and `false` is the placer asserting the lot did not constrain a house 24 ft wider than its
lot. **Third probe of six to be wrong, and the second to read a key that is not there.** And chasing it found a second bypass
**on every plan in this corpus, with no dependency involved**: the centre-bay parity bump crossed
the cap (a lot holding six bays, a seven-bay house, 3 ft over), which also made
`bay_count_forced_even` — whose own comment names a lot too narrow for the odd count as the only
way to reach it — **unreachable**. Clamped; it fires for the first time. The massing's own stated
minimum still outranks the lot and that residue is **disclosed, not capped**:
`geometry_report.lot` answers in three states and names
`oq/a-lot-too-narrow-for-the-diagrams-own-minimum-bay-count`. Six mutations, six caught.

**LAYER 5: `plan_check`'s drawn layer — the layer whose symptom had already gone.** Teaching
`openings` at layer 1 seated the dependency's windows and the landlocked test short-circuits at
`if seated: continue`, so *"reaches no exterior wall"* fell **2 → 0** while the arithmetic four
lines below was still wrong. Driven rather than watched: with the placement stripped from those
windows, `kitchen` and `breakfast` read `[]` against the main block and **`['S','W']`** and
**`['S','E']`** against their own element, while `chamber2` and `stair` read `[]` on both — **the
control is what makes it a fix rather than a loosening.** The finding they take instead names the
element, and ruling 4's second half is **reachable here rather than unreproduced**: the breakfast
room's east wall *"is exterior to the weather and interior to the view: it looks across the gap at
the main element"*, while the kitchen's south and west faces take no such note. The diagonal case
is refused by requiring perpendicular overlap. Regression pinned as a digest over every finding's
kind, room and statement — both shipped plans identical. Seven mutations, seven caught.

**LAYER 6: `export_ifc` — a fix that could not have been measured where it was written.**
`ifcopenshell` is optional, absent here and absent in CI, so `export_ifc.py selftest` reports COULD
NOT EVALUATE in every run this project has ever made — a slab rule written inside the writer would
have been "fixed" against a check that never runs. `export_ifc.slab_boxes` is therefore **pure
arithmetic**, computed where a test can read it and emitted where it cannot. The defect: one slab
per storey sized on the MAIN BLOCK while every `IfcSpace` is placed from its room's own ABSOLUTE
rectangle, so the main slab spanning `x[-1.29, 64.29]` left three rooms at `x[-41.0, -14.0]` over
nothing — **3 → 0**, with the single-slab baseline reconstructed as a test of its own so the pair
has something to be measured against. A dependency gets a ground slab and no upper one, which is
the building rather than an omission. Six mutations, six caught.

**AND THE DISCLOSURE REACHES ZERO WITHOUT THE BLOCK VANISHING.** `not_element_aware: []`, and the
note **may no longer say COULD NOT EVALUATE** — with nothing unjudged those words would be a fake
unjudged, as dishonest in their own direction as a fake pass. What it keeps are the two facts that
outlive the six layers: `engine="cp"` still refuses a multi-element plan outright, and the roof is
still the main block's alone.

**ITEM 2, THE PARTI: AUTHORED THREE WAYS AND REFUSED THREE TIMES, EACH BY A HARD ROOM RULE.**
All six service rooms in the dependency, as the package text asks → *"Butler's Pantry does not
reach a dining room through a direct door"*. Butler's pantry back in the main block with a
`gallery-corridor` hyphen → *"Hyphen does not reach a stair hall through a direct door"*. The same
with a `breezeway` → *"Butler's Pantry does not reach a kitchen through a direct door"*. **The
three are jointly unsatisfiable once the elements are real**: the butler's pantry must directly
door both the dining room and the kitchen, and any element boundary between them cuts one.
`partis/five-part-palladian.json` appears to do this correctly and only appears to — it satisfies
every rule because **nothing reads its composition**, no parti carrying a `block` until now.
`oq/three-hard-room-rules-forbid-a-detached-kitchen`. **The change is worth making and that is
measured**: on `family-georgian`, fatal findings **17 → 10**, serious 76 → 72, cross-element doors
unplaced **0 of 1**, the service block and the stair no longer unreachable — while the composer's
own candidate score falls 73.5 → 66.5, rating the better house worse. The parti is REVERTED until
this is ruled.

**AND THE PLACER'S HALF SHIPPED, because it is the prerequisite for any answer.** A parti room may
carry `block` and `hyphen`; `compose.py` copies both onto the plan record as it already copies
`stacks_over`; `geometry.hyphen_anchors` reads the door graph for crossings **through a link** and
`geometry.flank_slice` lays those rooms against the shared face as a **stated strip** —
`courtyard_slice`'s own move and its own reason. **The search cannot find it**: at the shipped 250
candidates the butler's pantry never reaches the face on either seed, at 1,000 it does on both, at
2,000 on one — the fourth package to measure a placement rule whose verdict is a property of the
pool. **Scoped to the LINK**, because four cross-element doors on this package's own fixture cross
open ground where no laying of rooms can place a door; scoping restores that fixture
byte-identically. Six mutations, six caught — the sixth only after a driven test, because the
garage's element inheritance is unreachable from a corpus in which no parti carries a `block`.

**ITEM 4 IS IN (5 Sep): CP-SAT PLACES PER ELEMENT, AND TWELVE DOWNGRADED WALL PINS BECOME FOUR.**
`geometry_cp._boxes` gives each room its own element box, read from `geometry.blocks_for` — the one
spelling both engines share. **With one element every room maps to `(0, 0, Wi, Hi)`**, the pair the
model spelled inline at every site, so the sixteen one-rectangle records take the same path: the
serialised model proto is **byte-identical on all sixteen, hard and objective**, which is a stronger
regression guard than sixteen ninety-second solves and costs nothing — **and was published once
before it was true**, on a harness whose `SerializeToString` threw `AttributeError` on both sides so
that `diff` compared two identical tracebacks. Re-derived, the objective model had moved on seven of
the sixteen, because `_EXT` widened four variable domains unconditionally: a domain is an input to
presolve, not a comment. Measured on the Tidewater
record at 90 s, seed 7: one rectangle **12** downgrades, the same record with the three service
rooms tagged into a west dependency and **nothing else changed 4**, the package's fixture (tagged
and walls re-declared) 5. Twelve to four with not one declared fact touched, which is the
diagnosis's own sentence measured — a service room declaring N/S/W is declaring the exposures of a
WING.

**Two of the three things it found were not about CP at all.** `derive_footprint` sized the main
block from the WHOLE ground programme while `flank_sizes` sized each dependency from the same rooms
and laid it beside the block — the wing's area counted twice, 2,405 sf of block for 1,863 sf of
rooms, 29% over. The hill-climb absorbed it as empty floor; the prover, which has a coverage floor,
called the house INFEASIBLE at every bay count. **A search that tolerates an over-size and a prover
that refuses it are the same defect read twice, and only one of the two says so** — and fixing it
moved every measurement this package had published on its fixture (main block 63 × 38.17 → 45 × 41.4;
layer-1 refusals 9 → 5 → **0**; the three-element built extent 118 → 100 ft with `flanking_ft`
unmoved at 55). The identities held and the literals moved, which is the difference between a guard
and a measurement. And the multi-element DISCLOSURE was attached in `write_record` only — the
heuristic's writer — so the one engine every multi-element plan was sent away from was the only one
that disclosed anything about them.

**The twelfth site was the interval's END variable** (`m.NewIntervalVar(x, w, m.NewIntVar(0, Wi))`),
which carries no constraint of its own, so nothing in the source reads as a bound on where a room
may be. The model came back INFEASIBLE with every assumption cleared and NO CONFLICT TO NAME. Found
by bisecting the model, not by re-reading it. Fifteen mutations, eleven caught, **four missed and
all four now guarded** — the misses share one shape, that satisfiability is a weak instrument: a
looser model is still satisfiable, so every mutation that merely widened a bound passed. Two lessons
worth carrying: an assumption literal is invisible to a test that clears assumptions, and a suite
that only ever builds the HARD model has not tested the objective at all.

**Still to do: item 3** (re-author `tidewater-georgian-careful` with `block` on every room), which
was blocked on item 4 and is now blocked on the parti —
`oq/three-hard-room-rules-forbid-a-detached-kitchen`. Then, outside this package, the two unbuilt items of the ruling itself. (An earlier
version of this line named five items for three layers for as long as it took to re-read it: it
still listed `structure` and `vertical_score`, taught in the two commits above it. A to-do list that
survives the work it describes is the *"until X lands"* class, one file over.)

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

**Status: COMPLETE (5 Sep 2026).** Part VII item 5; findings G1, G2, G3, G5. Report:
`docs/reports/wp-11.7-the-facade-as-a-result.md`. (**This status line said "Blocked on Lucas's Q2
and Q5" while both were RULED on 4 Sep**, in this same file, ninety lines below — the "until X
lands" class one section over.)

`build/facade.py` derives the rhythm the plan's own bays imply, compares the drawn front against
it and REPORTS; it composes nothing, because the ruling's second half is that the sequence is how
findings are EXPLAINED and not how they are resolved. Wired into `plan_check`'s **drawn** layer —
everything it reads is a placement, which is WP-11.4's rule for choosing a layer.

**MEASURED on `tidewater-georgian-careful`: serious 63 → 62 and minor 88 → 101.** The serious is
the ruling's own first commitment landing — `centre-passage-core`'s facade-share test was HARD and
convicted this house at a measured 0.136 against 0.18–0.27, and the share is a consequence to be
reported rather than an input the passage may be sized from. The thirteen new minors are seven bays
of the front carrying no opening and six rooms whose declared window count disagrees with the bays
their front wall spans — `chamber2` spans two bays and declares none. `spec-builder-colonial` does
not move: it names no parti, so it loses one `info` and gains one.

**THE FINDING OF THE PACKAGE IS A COINCIDENCE.** `elevation._face_bays` composed the front from
`facade-classical.json`'s formula and never read `footprint.bays` — two records built from
different rules with nothing comparing them, OQ 85's shape, four hundred lines from OQ 85's own
fix. **They agree on both shipped plans (7/7 and 5/5)**, so the elevation now takes the plan's
count and the corpus output is byte-identical: a second rule removed, not a new answer. Only the
faces spanning the WIDTH take it. Because they agree, the corpus cannot test the join and a
mutation deleting it leaves every natural assertion green — the guard drives the plan to nine bays.

**AND TWO ERRORS CANCELLED.** The first draft emitted a second door-off-the-centre-bay finding
beside WP-11.3's, in zero-based numbering against the existing one-based, so one door would have
carried two bay numbers; removing the facade-share test took a `serious` away at the same moment
and 63 stayed 63. Found by asking why a serious finding had been added and the count had not moved.

**Fifteen of the sixteen plan records name no parti** — every reference plan and
`spec-builder-colonial` — so the layer is silent on 94% of this corpus with an `info` naming the
reason. `oq/fifteen-of-sixteen-plans-name-no-parti`, the sibling of WP-11.4's massing entry, and
it forbids deriving the parti from the massing in the same words.

**Original package text, left as written:**

For a centre-door diagram: the bay rhythm from the bay count and module, the door in the centre
bay, one window per bay per storey aligned, the blind bay under each stack — derived BEFORE the
rooms' windows, which then become the bays each room's front wall spans. Inverts
`centre-passage-core`'s facade-share test (the passage's width is a consequence of the bay it
takes, not a fraction of a facade decided elsewhere).

### WP-11.8 The bench chooses, and says which

**Status: COMPLETE (5 Sep 2026).** Part VII item 7; findings J2, J6. Report:
`docs/reports/wp-11.8-the-bench-chooses-and-says-which.md`. (**This line said "Blocked on one
ruling" while that ruling had been taken on 4 Sep**, in this same file — the second WP status line
in two packages to outlive its own blocker, which is the "until X lands" class and is now worth
sweeping rather than correcting one at a time.)

**THE CASE MOVED TO THE OTHER PLAN, AND WHICH PLAN SHOWS IT IS ITSELF BUDGET-DEPENDENT.** The
ruling was taken on `tidewater-georgian-careful`; on this machine that plan no longer reaches CP at
all (`auto` spends 25 s and falls back, `fallback: budget`). The live case is
**`spec-builder-colonial`** — `cp-sat`, `OPTIMAL (hard-only)`, **`objective: null`**, five declared
exterior walls set aside — the other shipped reference plan, which the diagnosis never named.

**AND "with its demerit score" NEEDED A SECOND NUMBER.** The search scores **592.3** against the
proof's **789.3**, 197 points better, and buys it by breaking **sixteen** declared facts the proof
holds (0 against 16, judged against the SAME downgrade list, because a heuristic record carries
none of its own and charging it for pins CP-SAT proved impossible would rig it the other way).
`hard_fact_violations`' docstring already said so. Both numbers travel together and no surface may
print one without the other — which is the ruling's own intent, since telling a reader they are
choosing a better composition over a proved feasibility requires both halves of the trade.

`geometry._offer_the_alternative` (CP branch, objective-null only, ~0.3 s, and `could-not-evaluate`
WITH ITS REASON on either failure path rather than going quiet); `disclosures.alternative_offered`
(the plate line, straight after `objective_not_run` because it is the second half of one
disclosure; still ONE spelling); `corpus._placed`'s `solver.drawn_by` with an `input_digest` taken
BEFORE the solve, which is finding J6; and `PlanWorkbench.jsx`, which said *"proved, not searched"*
over exactly the placement the ruling says must not be preferred and says **proved feasible** now.

Ten mutations, ten caught. **The fixture is DRIVEN and not the corpus** and the reason is measured:
whether a real solve leaves `objective` null depends on this machine's budget, so a corpus fixture
would make the tests statements about 25 seconds. The JSX is held by a source-reading test because
vite compiles it in CI and there is no `node_modules` here — WP-5.7's own asymmetry.

**Not done, and each is named in the ruling as unruled or is a UI package**: the budget is
unchanged; a placement that set aside sixteen declared facts is still drawn rather than refused
with the conflict named; and the bench offers the alternative in words and numbers rather than
drawing it, though its geometry is on the record for a surface that wants it.

**Original package text, left as written:**

Interim, needing no ruling and buildable with WP-11.1: when the CP objective did not run, the bench
draws the proof with the WP-11.1 banner AND offers the search's placement beside it with its
demerit score; `corpus._placed` records which it drew and why in `geometry_report.solver`.

### WP-11.9 The prose, executed

**Status: COMPLETE (6 September 2026).** Report:
`docs/reports/wp-11.9-the-prose-executed.md` · new open question:
`oq/no-plan-record-states-its-bearing`.

**The four compass rules the table names turned out to be sixty.** Every room record states an
aspect in `daylight.orientation` and nothing in the tree read one. `daylight.aspect` is that
reading, authored beside each sentence and quoting it (`check_rooms.py` holds the quotation against
the record, `openings/grammar.json`'s rule one layer over): **35 state an aspect, 5 of those hard,
25 answer with something that is not a compass** — "Any", a door axis, a climate condition — and
each of the 25 carries a note saying which, because a refusal's value is its reason.
`build/compass.py` is the one reader; **plan-N is true-N unless a bearing says otherwise (ruled
5 Sep)** and the ruling's stated cost is honoured in the FINDING: all 63 print the assumption they
were judged under. It is a ROOM-layer check because a window's `wall` is authored (WP-11.4's rule
— ask what a check READS), which is why it speaks on 16 of 16 plans rather than on the 2 that
carry a placement. Measured: **40 rooms taking none of the light their record asks for, 23 glazed
on an aspect it rules out, ONE serious in the whole corpus** and it is true (a north sunroom on
`good-04`). Two grouping rules were also given a test — the passage's two ends and the stair hall
opening off it — and **both PASS on the Tidewater record, which is the finding**: B4 is a defect of
the drawing, not of the record. Building them found that **28 of the corpus's 86 grouping
`internal_rules` emitted nothing at all**, the no-test branch reading `elif hard`; it speaks for
every rule now, and names the severity. Of the twenty: **6 were already executable, 5 are executed
here, 9 are not done** — and the report's §IV sets all twenty out row by row, each of the nine
with the fact that would have to exist first, because the first draft of that section said
"seven, six and seven" and left three rows of the table in no bucket at all. Read it before
proposing any of the nine.

*The package as originally written:* Part VII item 8; the report's Part VI table.

The twenty prose rules that table lists, each given a `test` beside its `statement` where WP-11.3
and WP-11.4 have not already done so: the stair setback ceiling of 12 ft (E4) from the Georgian
kit, `public-enfilade`'s "rooms diminish or grow in one direction", `entry-sequence`'s "each step
changes one condition", `stair-and-landing-core`'s half-pace window, the library's north, the
closet's "never from the front elevation", the kitchen's east. Every test is scoped by the record
that carries it — a room rule on the room, a grouping rule on the grouping, a style note through
`style_variation` — which is Part IX's stratum discipline made mechanical.

### WP-11.10 The placer's shape terms, on the right box

**Status: PART-BUILT (7 September 2026) — the container question is answered and REFUSED; the
three shape terms are NOT done and are named below.** Report:
`docs/reports/wp-11.10-the-floor-that-cannot-be-enforced.md` · new open question:
`oq/the-depth-a-roof-needs-is-known-and-cannot-be-enforced`.

**Its stated blocker, WP-11.6, is complete** — so the package opened on the container question
Lucas ruled first: give `derive_footprint` a depth floor. **THREE FRAMINGS WERE FALSIFIED IN A
ROW, EACH BY MEASUREMENT.** A floor at the massing's pile moves `spec-builder-colonial`, a shipped
plan, 30.75 → 36.0 ft — 262 sf of empty floor, 17.1% over programme — to satisfy a rule not
convicting it. So the floor is derived from `faults/truss-flattened-pitch.json`'s OWN test
instead (`build/depth_floor.py`, a leaf; the threshold READ, never transcribed; agreeing with the
fault's forward verdict 2–0 with 14 unjudged) — **and the derivation is what shows the fault
cannot carry a cap**: `good-05-lobby-gallery-mansion`, a `good-*` plan, is convicted FATALLY at
0.2509 by a licence naming its SIBLING style, and the floor that implies is 69.31 ft against a
drawn 38.64. A cap would make a known-broken licence a hard constraint on the placer. **Reported
by the instrument, read by nothing**, and the refusal is TESTED rather than asserted.
Four defects found in the building of it, all mine, none by reading — read §IV before touching
this file. **`WIDTH_W`, the flat 12 and the direction-to-the-square remain**, and §VI says what
each needs.

*The package as originally written:* Part VII item 9. Part VII item 9. `WIDTH_W`, the flat 12, and the
direction-to-the-square the 3 Sep ruling opened, measured on the container that can hold the
programme. Not before: a term measured on the wrong box measures the box.

### WP-11.11 The diagnosis as an instrument, and the per-parti pass

**Status: COMPLETE (6 September 2026).** Report:
`docs/reports/precedents-centre-passage-double-pile.md`. No new open question.

**The instrument half shipped with WP-11.2** — `build/diagnose_sheet.py`, with `--baseline` and
`--seeds`. What this package added is the SECOND half, and the finding is that the two halves are
different kinds of thing. **Part II is RESEARCH and cannot be generated**; **Part VI is
ENUMERATION and now is** — `build/parti_prose.py <parti-id> [--md] [--all]` reads a parti's own
groupings, massing and room records and sorts every sentence into `executed` / `reported` /
`by hand`, plus the prose figures no band carries. The diagnosis's twenty-row Part VI took a
session by hand; the equivalent for any of the twenty-one is now one command, and for
`centre-passage-double-pile` it is **50 rows: 24 executed, 6 reported, 20 by hand, 7 prose
figures** — the hand table was a reading of one sheet and caught what that sheet broke, the
generated one is the whole surface. Corpus-wide (`--all`): `five-part-palladian` is the largest at
30/9/26, `single-cell-hall` the smallest at 12 rows.
**All twenty of this parti's room-orientation rows LEFT the by-hand column at WP-11.9** (15
executed, 5 reported), which is the only evidence a generated Part VI is worth having rather than
a list of complaints. **The prose meter is `check_grouping_rules`'s, imported and not
transcribed**, with a source-reading test that fails if this file grows its own regex.
**One of six mutations was BLIND and is recorded rather than patched**: the room filter in
`room_figures` is inert today, because `prose_meter`'s room population is keyed on the GROUPINGS
it is handed, and the test pins that measurement so it stops being true loudly if the meter
changes.
Ruled: **one parti, done properly, as the pattern** — the precedent file carries the method for
the other twenty in §2 and states in §4 that it re-measured nothing, every figure cited to the
pass that established it.

*The package as originally written:* Part IX's method.

`build/diagnose_sheet.py <plan> [--engine]`: prints the diagnosis's Part I tables for any placed
plan — every room's drawn rectangle beside its declared one, its placed and declared exterior
walls, the front's openings per storey and their alignment, the solver's downgrades and objective
status, the six baseline numbers — so the next parti's diagnosis starts from a generated Part I
rather than from pixel-reading a screenshot. Then the per-parti precedent pass, one parti at a
time from `partis/*.json`'s own `exemplars`, each producing a Part II table in
`docs/reports/precedents-<parti-id>.md` and a Part VI list of that parti's prose rules without
tests. Twenty-one, not one hundred and sixty-four.

### The adversarial audit of WP-11.9, WP-11.10 and WP-11.11

**Status: COMPLETE (7 September 2026).** Report:
`docs/reports/audit-2026-09-07-the-things-the-session-did-not-measure.md` · two new open
questions: `oq/the-composer-ranks-on-an-assumed-bearing`,
`oq/the-canon-axis-counts-two-grains-as-one`.

Four read-only auditors, none of them the agent that wrote the code, over the session's whole
diff: edge cases and every consumer; whether each new test would fail with its fix reverted;
second-order risk; and second occurrences of each pattern elsewhere. **Thirty-eight findings,
twenty-four fixed, fourteen deferred with a reason apiece.**

**Two blocked, and both were crashes in code written to guard against the malformation that
crashed it** — `check_rooms.py`'s verbatim-quote check (`None not in "str"` is a TypeError, on a
checker that runs unconditionally after schema validation) and `compass.read`'s `aspect["basis"]`
(escaping through `plan_check.check`, which `critique` and `compose` call unvalidated). Fuzzing
found 30 unhandled exceptions across the three new entry points; all 30 return a verdict now.

**The finding of the pass is that WP-11.9 changed the composer's fitness function and its report
does not contain the word `score`.** Measured: −3.00 of 18 on the cleanest shipped plan, and on a
real compose the order below the winner moves on both briefs. Not reverted; put to a ruling.
**And its first measurement read 0.00 everywhere**, because the harness patched a `compass`
reached through a second `modcache` instance — a zero delta is indistinguishable from an inert
term, which is why the suppression is now asserted before any delta is read.

Also: both new passage variables read the flattering way on `hard` rules; a finding's id did not
include its `kind`, so identity moved when a sibling cleared; and the pre-existing item larger
than everything above — `core.check_plan` rebuilt the jsonschema validator on every call, so
`/api/plan/evaluate` validated the same document twice, 4.2 ms compiled and then **79.1 ms
uncompiled, 23% of the whole server's measured bound.** Eleven tests could not fail, including
the one whose docstring claimed to catch the `elif hard` revert.

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

## Phase 11 — The precedent bench

*Opened 4 Sep 2026 at Lucas's request: where the research is thin and where deepening it would change
what the machine does; the exemplars of each style researched into the most beautiful and iconic
precedents, with links. Cite reports by filename, never the bare number (OQ 90).*

### WP-11.1 The survey, the record and the meter

**Status: BUILT (4 Sep 2026); the research runs as WP-11.2 through 11.4.** Report:
`docs/reports/wp-11.1-the-bench-without-a-literature.md`.

**What was found**, and the exemplar clause is a record of 4 Sep rather than a description of today —
WP-11.2, WP-11.3 and WP-11.5 moved it to 800 exemplars, 4 to 9 a node, and moved none of the other
three.
The corpus WAS TEMPLATED on the surface: all 132 buildable nodes carried 2–4 exemplars
(90 exactly 4), 4 or 5 sources, exactly 5 constraints and 3 `distinguished_from`; a composite of those
spreads 1.5× across the set, so field counts separate nothing. What separates thorough from skeletal was
tracked nowhere: 542 `measured` kit parameters with no source on the parameter or its slot (272 on a
generator-read slot — the census had counted editorial-bare, 0, for a year); an exemplar with no locator
(482, 410 buildings, zero URLs); 24 buildable nodes citing only works ANOTHER NODE cites ("a sibling" until WP-11.7 corrected the word; the true sibling reading is 9); 32 higher-rank nodes
citing nothing, all `confidence: high` (**0 today — WP-11.7 sourced all 32**, and the survey's
reading is kept in the past tense because it is what raised the package); three nodes with no executable constraint; 11 kits with zero
parameters; 16 of 57 packs `reconstructed`, nine from the corpus's own records; 0 of 761 pack rules with a
per-rule source; `massings/` with no provenance vocabulary; no period building anywhere in `plans/`. And
the operational map: `elevation.py` dimensions every house from five hard-coded packs whatever the style
binds, so research on the other 51 changes what the system says and not what it draws.

**What was built.** `schema/precedent.schema.json` and `precedents/` (one record per building: refs with
`retrieved`/`via`, the HABS written data quoted verbatim with figures `as_printed`, `rights_evidence` and
never a `license`); the exemplar's `precedent`, `standing` and `why`; `build/check_precedents.py` (both
directions, id shapes, no licence, kit pointers) and `build/check_research.py` (the meter, ratcheted, the
read-slot set derived and pinned); `check_kits.py`'s census gains `measured-bare`; `tdl_precedents` (27);
the record's refs on the workbench and the atlas; `docs/precedents.md`; five open questions.

**Tranches.** **WP-11.2** Tranche 1 — the 28 nodes the platform exercises or the partis' exemplars belong
to (5 parallel agents, 4 Sep): every existing exemplar gets a record, 5–8 precedents per node with standing,
a survey block for every US building with a HABS data page, then a 10% adversarial re-resolution.
**WP-11.3** Tranche 2 — the rest of North America. **WP-11.4** — the four rulings, executed as mechanism
before any more research was authored. **WP-11.5** Tranche 3 — the British and European ancestors, and the
"links and standing only" this line promised was overtaken by a measurement: a Historic England list entry
is survey-shaped, so Europe carries surveys, quotes and measurements like North America. **WP-11.6** —
Ruling B, the family type specimens. **WP-11.7** Tranche 4 — the families and traditions get a
literature of their own, which is the SOURCES half rather than more precedents: the precedent half
of higher rank was already finished by Ruling B.

**THE ORDER AFTER TRANCHE 3 IS RULED (5 Sep 2026): FINISH PHASE 11.** Put to Lucas against the two
alternatives the 3 Sep project review names — building the register (ruled 1 Sep, nothing built) and
the dependency (`oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it`, unruled) —
both of which unblock the generator the review says has not arrived. **Ruled: Ruling B, then Tranche
4.** So the bench is completed before the generator is resumed. **The first two of those three are
done (WP-11.6): every buildable node and every family carries precedents, and the 72 asset records
are named.** `tdl_precedents` no longer hedges for a family; it still says a walk is a reading for a
TRADITION, and that is the ruling rather than a gap. The register and
the dependency keep their place in the review's ranking and are the work after Phase 11 closes.

**And Tranche 3's own scope note, ruled the same day**: an exemplar row naming a REGIONAL POPULATION
(*"the Leopoldine farmhouses of the Val di Chiana"*, *"the farmhouses of the Simmental"*) takes a
`record_kind: type-model` RECORD and is NOT a `no_precedent` refusal — the closed refusal vocabulary
has no word for a population and does not need one, because the type can carry its own record with
the programme's or the region's own sources.

**WP-11.3 Status: COMPLETE (5 Sep 2026). NORTH AMERICA IS DONE — 86 of 164 nodes carry precedents,
which is all 85 buildable nodes of the `north-american` tradition plus `scandinavian-log-vernacular`.
The 46 buildable nodes still without one sit under the four European trunks — `british-isles` 19,
`classical-mediterranean` 11, `northern-european-vernacular` 9, `iberian-mediterranean` 7 — and are
Tranche 3.** One `pipeline(clusters, research,
audit)` over 12 clusters, each a union of whole connected components of the shared-building graph, so no
two agents could write one record file — the write race designed out rather than instructed away. 254 new
records (161 → **415**), 78 new surveys (→ **155**), 358 new quotes (→ **723**), 255 new measurements
(→ **526**), 505 of 693 exemplars resolved. Every artefact figure re-derived from git; the one that
disagreed with the agents' own reports was the one describing their action rather than the artefact.
**240 kit readings: 196 silent, 27 agree, 17 CONTRADICT**, three convicted by the node's own exemplar
(`southern-federal`'s 20 ft max depth against Woodlawn's 45; its 4-in chimney standoff against Belle
Grove's *"four inside chimneys"*, which the parameter cannot satisfy at all; the Gamble House's three
chimneys against a singular rule whose slot note cites that very building). **Nothing was applied** —
ruling A is still a ruling nobody has given. 12 per-cluster auditors fixed 57 defects, 82 of them
unsupported `why` sentences; the deepest finding is that `as_printed`-must-be-a-substring proves internal
consistency and NOT fidelity, since a quote edited to fit its own figure passes it. Report:
`docs/reports/wp-11.1-the-bench-without-a-literature.md` §VII.10 and §VII.11 · new open question:
`oq/an-exemplar-that-is-not-one-whole-building`.

**Rulings asked for.** `oq/a-surveyors-prose-may-source-an-envelope-figure`; `oq/a-family-node-has-no-exemplar`;
`oq/a-measured-parameter-with-no-source-is-not-metered` (its parts 1 and 2).

**WP-11.4 Status: COMPLETE (5 Sep 2026) — ALL FOUR RULED AND THREE EXECUTED.** Lucas ruled every
open Phase 11 question the same day. **A** — yes, a survey measurement may source a `measured`
envelope figure at `confidence: medium`; built, and the ruling's own trap closed MECHANICALLY by
requiring the `#measurements[<n>]` form so `kit_source_agrees` can compare the two numbers
(agrees / contradicts / could-not-compare, never a bool). **Six figures cite a building**, the
checker's own count off zero for the first time, and `source_agrees` is a FLOOR so they cannot
quietly vanish. **C part 2** — yes, refuse a new unsourced `measured` parameter; built as a
per-parameter gate against a frozen 542-triple set, because the ratchet that preceded it was a NET
count and passed a commit that sourced one figure while adding another (measured: `check_research`
returned 0 with an unsourced parameter in the tree). **Part 1 NOT ruled and nothing re-kinded.**
**D** — ratify districts and type models as records (`record_kind`) and make a refusal a field
(`no_precedent`); built, with the district exemption now driven by the declaration rather than by a
regex over a title. **B** — families carry type specimens derived from members' icons; RULED and
DEFERRED, because 18 of the 27 families have zero `standing: icon` exemplars today and all 18 are
European: it must follow Tranche 3 or it lands half-executed.
Ratchets: `measured_unsourced` 542 -> 536, `measured_unsourced_read` 272 -> 270.
New question: `oq/a-source-that-agrees-numerically-may-be-the-wrong-quantity`. Deliberately not done: no
sheet transcribed, no band changed, no parti edited, no licence written, no harvest workflow, nothing
sourced from a secondary work for OQ 7–11 or OQ 18, and `elevation.py`'s five packs left as
`oq/the-elevation-reads-five-packs-whatever-the-style-binds`.

**WP-11.5 Status: COMPLETE (5 Sep 2026). TRANCHE 3 FINISHED EUROPE AND WITH IT EVERY BUILDABLE NODE.**
25 agents, 0 errors, 4h27m over the four European trunks — `british-isles` 19,
`classical-mediterranean` 11, `northern-european-vernacular` 9, `iberian-mediterranean` 7. **415 ->
695 records, 155 -> 423 surveys, 723 -> 1,701 quotes, 526 -> 1,309 measurements, and 794 of 800
exemplars resolved across 132 of 132 buildable nodes.** The 32 nodes still without a precedent are the
families and traditions — Ruling B's work and Tranche 4's, not a gap in this one. Six exemplars are
unresolved and Ruling D's field makes the split legible: **3 stated refusals against 3
not-yet-researched**. `record_kind` is carrying the other half of D — 653 buildings, 26 groups, 13
districts, 3 type models — so a regional population is a record with the region's own sources rather
than a refusal the vocabulary has no word for.

**THE PACKAGE'S OWN DEFECT WAS MINE, AND A RESEARCH AGENT DIAGNOSED IT BEFORE IT COULD FIRE.** The
plan widened the `survey` block's DESCRIPTION to admit a national heritage list entry and did not
widen the CODE that reads it: `check_precedents.py` shape-checked every `survey.item` against the
Library of Congress's `xx0000` form and `identity_keys` attributed every one to the `loc-item`
namespace. First global run: `malformed_ids` **0 -> 268**, and **five Medici villas sharing UNESCO
inscription 175 read as one building written five times**, because a UNESCO inscription names a
SERIAL property exactly as a National Register district does. The first research agent simulated the
checker's own regexes over its 24 records, predicted the failure for every European record from all
twelve clusters, named the fix, and **did not touch `build/` because eleven agents were writing** —
which is the protocol working. `survey.register` is the fix: the block says which register issued its
`item`, so it is shape-checked against THAT register's rule and attributed to THAT namespace, and
`unesco`, `institution`, `wikipedia` and `other` are declared SERIAL and may never be an identity.
**271 errors -> 2.**

**THE TWO SURVIVORS WERE REAL, AND THEY ARE THE HOLE THE CLUSTER PARTITION CANNOT CLOSE.** The
partition is over the exemplars that already EXIST; agents also ADD buildings, and two clusters each
added Kedleston Hall (HE 1311507) and Charlotte Square (HES LB28502). Merged as the corpus prescribes
— evidence folded in, the superseded id DEPRECATED and never deleted or reused — which surfaced that
`superseded` was computed in the duplicate pass and read in only ONE of the two loops that needed it,
so a merge done exactly right still convicted itself.

**RULING A YIELDED NOTHING FROM EUROPE AND THE REASON IS STRUCTURAL RATHER THAN A RESEARCH FAILURE.**
18 `citable` candidates, **0 applied**. A parameter has ONE `source` field, and **489 `measured`
parameters already cite an INTERNAL source** (a constraint id, the node's own `typical_ratios`)
against the 6 that cite a precedent — so Ruling A can only ever reach the 536 that cite nothing, and
the corpus's most-reasoned figures are exactly the ones a building may not corroborate. Five more
candidates point at a `set`-shaped parameter `kit_source_agrees` cannot compare at all, and two of
those — Royal Crescent at FOUR bays, Kedleston at ELEVEN — say the set is INCOMPLETE rather than
wrong. Five more point at a band two of the node's own exemplars break at six lights apiece.
**Contradictions 17 -> 20**, and a fourth kind appeared: not a wrong band, not an unmet
presupposition, not a missing datum, but an incomplete ENUMERATION. New question:
`oq/a-parameter-has-one-source-field-so-a-building-cannot-corroborate-a-reasoned-figure`.

**The audits, and the reconciliation.** 12 per-cluster auditors: 252 of 261 sampled refs confirmed,
671 of 685 sampled quotes verbatim, **0 `as_printed` failures**, 36 unsupported `why` sentences
against Tranche 2's 82 on more records, and **10 manufactured quotations** found by hunting that class
by name after Tranche 2 named it — 24 defects fixed in all. One cluster's records **decline to quote
anything read `via: tavily-search`** and say so in the ref note; that discipline came from an agent
rather than from the protocol and belongs in it. **Records reconcile exactly at 280 new; surveys,
quotes and measurements came in 1, 8 and 4 lower than the agents claimed, and no auditor deleted any,
so the residue is the agents' own tallies. Git is the number.**

**`ids_with_no_shape_rule` 58 -> 216, and 163 of 423 survey blocks sit on a register with no shape
rule.** Raising a ceiling is a deliberate act and this one is honest rather than a slip: Europe
carries ids from ten registers whose format this project has read a statement of exactly once —
Historic England's own *"Every List entry has a unique 7-figure reference number"*. The alternative
was to invent shapes, which is precisely how `NRHP_RE` went wrong. It falls by reading one register's
own statement of its format at a time, never by guessing. Report:
`docs/reports/wp-11.1-the-bench-without-a-literature.md` §XII.

**Deliberately not done:** no band changed on any of the 20 contradictions; no bulk re-kinding of the
536 (Ruling C part 1 is still unruled and the meter is the interim); nothing sourced from a secondary
work or a modern redrawing for OQ 7–11 or OQ 18's source half; no locator resolution sweep, so
**nothing in this tree checks that a locator resolves** and the report says so plainly rather than
implying it was checked.

**WP-11.6 Status: COMPLETE (5 Sep 2026) — RULING B EXECUTED, AND THE DEFERRAL WAS RIGHT.**
121 type specimens over all 27 families, one per member node, derived from the members' own
`standing: icon` rows and deduplicated by building; 121 family names added to 119 precedent
records. **915 of 921 exemplars carry a `precedent`, across 159 nodes** — every buildable node and
all 27 families. The 5 that remain are the TRADITIONS and the ruling says they stay empty, so the
floor may never reach 164 and that is the answer rather than a gap.
**The gate was real**: 18 of 27 families had zero icons under them when the ruling was given and all
18 were European, so executing it before Tranche 3 would have served nine and left eighteen empty.

**The derivation is a module and a CHECK rather than a one-shot script**, which is the substance of
the package. `build/family_specimens.py` derives, `--apply` writes, and `check_precedents.py` fails
the build when a family's stored rows are not the ones its members' icons derive
(`family_specimens_drifted`, hard 0). A derived record nothing can re-derive is a snapshot, and a
snapshot of somebody else's judgment goes stale the moment that judgment moves. The check went
INSIDE an existing checker deliberately, because a new checker moves `check_all.TOTAL_CHECKS`,
`tests/test_counts_guard.py` and CLAUDE.md's `N of M checks passed` illustration together.
The `why` REPORTS and does not restate: it names the member and points at that node for the reason
rather than copying its sentence, because a copied sentence is a second spelling that drifts.
**Two buildings stand for two families each** — Larkin House for `monterey-colonial` and
`monterey-revival`, the American Gothic House for `american-farmhouse-vernacular` and
`folk-victorian` — a style and the revival that quotes it naming one building, which is the graph
saying something true rather than a duplicate to merge.

**THE FULL SUITE CAME BACK WITH THREE FAILURES AND ALL THREE WERE MINE, ALL THE SAME DEFECT**: a
literal in a test duplicating a number the ratchet already held (`== 693` exemplars, an exact
`record_kind` census, `== 58` unshaped ids). Tranche 3 moved all three with nothing being wrong.
Each now holds the durable invariant instead — the corpus against `measure()`'s independent walk,
the vocabulary against the schema's own enum, the count against the ratchet — and every repair was
mutation-checked from a green baseline, by exit code. **The harness caught itself first**: its first
run reported four mutations red against a baseline that was ALREADY red, because an earlier crash
had written a mutation and died before restoring it. *A mutation that silently does not revert makes
every later result meaningless, and it reads as success.* And the obvious repair for the first test
was a tautology — `== total` counted in the same loop cannot fail, because every row increments
exactly one bucket.

**AND UNDERNEATH THE DISTRICT TEST: 51 ARCHIVAL IDENTITIES THE DUPLICATE GUARD IS DROPPING.**
`identity_keys` skips an nrhp/nhl id on an undeclared record whose reference title or note matches
`DISTRICT_RE`. Some drops are right — four Great Smoky Mountains cabins share NRHP 77000111 and two
Cleveland Heights houses share 09000210, where the number names the listing. **Twenty-seven are
wrong**: Marble House, The Elms, Rosecliff, the Boston Athenaeum, Cliveden, Hill-Stead, the Palace
of the Governors, Taos Pueblo and nineteen more, each an individual building losing its own listing
number because its title names a district it contributes to. A false SILENCE and never a false
error, which is why nothing caught it. Counted, ratcheted at 51 and printed every run;
`oq/a-district-number-on-a-contributing-property-is-not-that-buildings-identity`. **Deleting the
fallback is measured and refused** — it would convict the six legitimate sharers as duplicates.

**Deliberately not done:** the 27 were NOT hand-declared `building` to make the number fall, because
that leaves the class open for the next tranche and the question is which fact the corpus is
missing, not which 27 rows to edit. **`build/name_asset_buildings.py` WAS re-run and the 72 asset
records on the 18 exemplar-less higher-rank nodes are named** — 786 → **858 of 1,850**, across 312
queries of which 183 are inside HABS's charter, and a dry run now assigns zero. That was WP-4.4's
own stated next step and it had been waiting on exactly this ruling.

**AND THAT NAMING RUN REDDENED FOUR MORE TESTS, ALL THE SAME DEFECT AS THE THREE ABOVE.** The full
suite read `1 of 49 checks failed`: every checker green, the three named could-not-evaluate states
in place, and four tests carrying literals that the moved figures falsified —
`image_building_named` 786 → 858, `image_queries` 305 → 312, `image_queries_us` 180 → 183, the
residual 72 → 0. **Three repaired one day, four more produced by that day's own change**, and
nothing counts how many remain. **The obvious repair was the tautology just removed**: binding them
to `check_counts.computed()` reads as the same fix and is not, because `computed()` derives
`image_queries` by calling `query_for` — the function under test — and `image_building_named` counts
ALL assets where the harvest test counts WANTED ones. The copies are deleted rather than moved; each
test asserts its own property, and no ratchet is added to `check_assets.py` because a second owner
makes an honest change a two-file edit and a dishonest one invisible. One test's subject was
DISCHARGED rather than moved — it required the residual LINE to exist, and that line prints only
when the count is non-zero, so it failed on its own scaffolding at success. Five mutations, all red
from a proved-green baseline, each restored in a `finally`. Report: `docs/reports/wp-11.1-the-bench-without-a-literature.md` §XIII · new open question:
`oq/a-district-number-on-a-contributing-property-is-not-that-buildings-identity` · closed:
`oq/a-family-node-has-no-exemplar`.

**WP-11.7 Status: COMPLETE (7 Sep 2026) — TRANCHE 4, AND THE APPROVED PROTOCOL WAS BACKWARDS.**
Every family and every tradition cited NOTHING: the one figure `check_research.py` printed on every
run and ratcheted nowhere, which is exactly the shape WP-8.14 is about. **156 sources written over
all 32 nodes — 28 carry five and four carry four — 111 citations of works new to the corpus (109
DISTINCT works, two of them cited by two nodes apiece) and 45 reusing a string the corpus already held; `distinct sources` 314 → 422 and `sourceless_nodes` 32 → 0, pinned tight at 0.**
Ruled 7 Sep: a family's sources are **AUTHORED**, the works that establish the category and never
the union of what its members cite; **sources only**, no `distinguished_from` and no constraints at
higher rank; and the `shared_only` ceiling **keeps its 24 while the WORD is corrected** to "another
node" (the true same-parent sibling reading is **9**, measured).

**THE PLAN'S OWN PROTOCOL WOULD HAVE REDDENED THE BUILD, AND MEASURING IT IS WHAT FOUND THAT.** It
said *"prefer a work the corpus already cites — 95 strings are pre-vetted and automatically safe"*.
The opposite: `shared_only` is computed over all 164 nodes, so a family whose every source is cited
by somebody else IS a `shared_only` node. Measured before a word was authored — giving
`english-classical` Summerson alone took `check_research --strict` from green to **RED**. The safe
contract has two clauses and the plan had neither: at least one source in the LIST must be cited by
no other node, and none may be one of **38 named strings** (cited today by exactly one node which
has no other unique citation, so citing it flips THAT node). `build/family_source_hazard.py` judges
the list — **ok / unsafe / could-not-judge**, never a bool — and **refuses to write an unsafe one**,
because six agents writing in parallel would otherwise each have read the rule from prose. Three of
its five guards could not fail when first written and each is driven through a constructed case now.

**Six auditors, two strings removed of 157 written, and no fabrication by a writing agent.**
`english-classical` cited a book that does not exist (`Dan Cruickshank and Peter Wyld, Georgian
Buildings of Britain and Ireland (1975)` is two real works welded together) — removed, deliberately
not "corrected", and **pre-existing on five buildable nodes where it remains**;
`american-arts-and-crafts` cited a monograph on its own member `prairie-school`, byte-identical to
that node's citation, which is the brief's worked example instantiated; and
`northern-european-vernacular` wrote a book this package had already written under a different
subtitle. **ONE audit reported COULD NOT EVALUATE on existence as its headline** (this line said "two", and
so does `f7d2ee9`'s pushed commit message, which cannot be corrected; the second audit confirmed
every work and recorded a limit on the strength of its YEAR evidence, which is not the same state) — Tavily
answered HTTP 433 (pay-as-you-go limit) to every call in the package and the WebSearch budget went
with it — and removed nothing, reasoning that dropping works they could not check converts
*could-not-evaluate* into *evaluated-and-failed* on the strength of an exhausted quota.

**THE FINDING: 23 WORKS APPEAR UNDER 51 STRINGS, AND CORRECTING THEM REDDENS THE BUILD BY SIX.**
`cited_by` is an exact-string counter, so *A Field Guide to American Houses* is six works to this
corpus (35 / 27 / 12 / 3 / 1 / 1 nodes). Collapsing every group to its commonest spelling takes
`distinct sources` **422 → 394** (28 phantoms, 6.6% of the layer) and `shared_only_nodes` **24 →
30**: `american-farmhouse-vernacular`, `beaux-arts-american`, `craftsman`, `garrison-revival`,
`modern-farmhouse-traditional` and `neo-eclectic` each escape a thin-research meter by a spelling.
`beaux-arts-american`'s only unique citation differs from `beaux-arts-french`'s **by a comma**.
**Nothing was normalised** — making the data more correct is a six-node regression against a live
ratchet, which is a ruling and not a tidy — except the ONE phantom this package minted, normalised
after measuring that neither node flips. A package may not leave its own behind.

**AND A SOURCE IS ADDED BECAUSE IT ESTABLISHES THE CATEGORY, NEVER BECAUSE IT WIDENS A MARGIN.**
`northern-european-vernacular` holds exactly one work no other node cites, against a ceiling with
zero headroom, because two of its five are also cited by its own member families. Two tradition-scope
replacements were researched and confirmed here and **neither was added**: every other node got 4 or
5, this one would have got 6, and the reason would have been that a meter looked tight. Padding a
list to buy headroom on the meter that exists to detect thin research is the failure the whole
protocol was written against.

Report: `docs/reports/wp-11.1-the-bench-without-a-literature.md` §XIV · new open questions:
`oq/a-source-is-a-free-string-and-nothing-can-tell-a-book-from-a-fiction` and
`oq/one-work-is-cited-under-several-strings-and-every-source-count-is-inflated`.

### WP-11.12 The suite that ran on one core

**Status: COMPLETE (7 September 2026).** Report:
`docs/reports/wp-11.12-the-suite-that-ran-on-one-core.md`. No new open question.

**Raised by Lucas against a screenshot of the corpus job**: *"the corpus check has ballooned to
now taking upwards of 40 mins per PR... is there any way to consolidate this?"* -- and the first
finding is that consolidation was the wrong shape for the problem, which only became visible by
measuring. Job by job on run `33908079938`: the corpus step **39 min 32 s**, the workbench job
8 min 17 s, the image 55 s. So the corpus job WAS the wall-clock of a pull request. Inside it,
reproduced locally within 5% of the runner: **`pytest tests/` 2,070 s against 197 s for all 44
checkers.** Nothing in the suite is slow -- the worst checker is 49 s and the average test is
1.3 s. 2,267 s of independent work was running on one core, and had been since `check_all.py`
was written, when the whole thing took three minutes. There was nothing to merge; there were two
things to do.

**FIRST, 46 SECONDS THAT WERE A CONVENIENCE WRAPPER.** `jsonschema.validate(instance, schema)`
rebuilds the validator on every call, and five checkers called it in a loop. `check_assets.py`
was **18% of the whole checker suite** and every second of it was construction: 1,850 records,
**35.70 s -> 0.59 s**; validate.py 5.93 -> 0.40, check_kits 6.25 -> 1.93, check_orders
2.27 -> 0.38, check_constraints 0.78 -> 0.18. `build/schema_validators.py` is the one spelling.
**The defect was already in CLAUDE.md** -- WP-10.1 measured this same wrapper at 60.5 ms a call
and 17.9% of `/api/plan/evaluate` -- and the companion to that entry's *measure what you add to
the hot path* is **then go and look for the shape somewhere else**: a grep would have found all
five on any day in the past year. The risk was never the speed but the MESSAGE: `validate()`
raises `best_match(iter_errors(...))`, every one of these checkers puts `e.message` in front of a
person, and a faster validator choosing a different error would silently change every failure
this corpus can produce. `raise_first()` is that same `best_match`, and the test holds the two
against each other on real records with each required property removed in turn.

**SECOND, SIX JOBS INSTEAD OF ONE.** `build/check_all.py --shard i/N` partitions 126 units -- the
`CHECKS` entries and a glob of `tests/test_*.py` -- longest-first onto N shards. `--shard 1/1` is
`make check`, byte for byte. **SIX IS MEASURED AND NOT CHOSEN**: the makespan is bounded below by
the largest INDIVISIBLE unit and `tests/test_score.py` is **422 s** on its own, so six lands 422
and a seventh buys nothing.

**MEASURED ON THE FIRST SHARDED CI RUN (34162261372): 11 min 17 s against 39 min 32 s -- a 3.5x
CUT AND NOT THE SIXFOLD THE LOCAL COSTS PREDICTED**, all ten jobs green including the aggregate
gate. The six shards came back 306, 315, 346, 423, 465 and **645** s against a predicted flat 421.
**THE COST TABLE'S TOTAL WAS RIGHT TO 0.2% AND ITS DISTRIBUTION WAS WRONG BY FOUR MINUTES, AND
THAT IS THE FINDING**: 2,503 predicted against 2,499 measured, because TWO OPPOSITE ERRORS
CANCELLED IN THE SUM -- the per-file sweep ran three files at a time and inflated most of them
(shards 4-6 at 0.73-0.82 of prediction), while the CP-SAT-bound files are far slower on a smaller
runner (shard 3 at 1.62). **An aggregate that agrees is not evidence that the parts do**, and only
the aggregate was ever checked. `tests/test_score.py` is the one file whose CI cost is known
exactly -- shard 1 held it alone -- at **422.37 s** against a local 431.50, so the floor was right
and everything else was not. Re-costed from that run, six shards balanced at 416-422 s, which was
published as a PREDICTION of 7.5 min.

**AND THE NEXT RUN FALSIFIED IT: 10 min 3 s, makespan 571 s against 421 (run 34163342215).** The
second instrument carried the first's defect one level down. Scaling every file by ITS OWN
SHARD's measured/predicted ratio makes that shard's total right BY CONSTRUCTION, so the total
cannot be evidence, and the shape inside the shard stayed as assumed as before: shard 1, one unit
and an exact CI figure, came in +4%; shard 3, whose largest file carried a spread one, +37%. The
figures are pytest's own now -- `--junitxml` gives a time per test case and the classname names
its module, so `per_file_seconds()` costs a shard's files from that shard's own run, attributing
exactly or not at all and reporting what it cannot attribute. The table is NOT re-costed in that
commit: the figures it needs are CI's and arrive with the next run, and deriving them locally
would be a third instrument measured on the wrong machine. `--list-units` prints the assignment,
so the next person to ask whether seven would help can answer it rather than argue it.

**THE SPLIT IS BY JOB AND THAT IS THE FINDING.** Six test files mutate repository data in place
and restore it in a `finally` -- `test_kit_cascade`, `test_manifest_io`, `test_render_profile`,
`test_ontology`, `test_constraints`, `test_open_question_ids`. `pytest -n auto` in one checkout
would let one worker read `assets/manifest.json` while another has it truncated: intermittent,
and blamed on the reader. Separate runners have separate checkouts and each shard is still one
serial pytest process, which is why this package edits no existing test.

**AND THE FAILURE IT COULD HAVE INTRODUCED IS THIS REPOSITORY'S OWN**: a unit in no shard runs
nowhere and reports success. Nothing is enumerated -- `units()` globs and `assign()` is total onto
`0..N-1`, so a unit is in exactly one shard by construction. `tests/test_check_all_shards.py`
holds it anyway and was mutation-checked four ways, each mutation asserted to have LANDED before
the colour was believed. The guard worth knowing: **`ci.yml`'s matrix against `ci.yml`'s own
`--shard i/N`**, two numbers in one file that nothing else compares, where `[1..5]` against `/6`
runs five sixths of the suite behind five green ticks. Empirically: six isolated checkouts
collected **1,923 tests** between them, exactly the single run's total, with the three permitted
N/EV states landing one each in shards 2, 3 and 6.

**AND THE SUITE CAUGHT THE ONE THING THIS PACKAGE BROKE.** The id gate was lifted out of `ci.yml`
into `.github/scripts/oq_ids_do_not_collide.sh` -- it answers the same for every shard and running
it six times is six chances at a rate limit -- and `tests/test_open_question_ids.py` sliced that
shell OUT OF THE YAML by string index in order to run it against stub registers, so it raised
`ValueError: substring not found` on a guard whose own header records that it exists because
*"a guard nobody runs is a comment."* It reads the script now, which is the thing CI executes, and
a new assertion holds `ci.yml` to still calling it.

**AND THE ONE THING THIS PACKAGE SHIPPED BROKEN IS THE ONE WORTH KNOWING.** `--shard 1/1` is meant
to be `pytest tests/` verbatim; it was not. `assign()` hands a shard its files LONGEST-FIRST and
the branch compared that against a SORTED list, so at 1/1 the comparison was False and the
unsharded run passed pytest 78 explicit paths in cost order. All 1,923 tests ran and passed, every
guard was green, and **the only witness was a line of output** -- `=== pytest tests/ (78 of 78
files) ===` in a forty-minute log. The decision is a pure function now (`pytest_target()`) with
three tests over it, one of which refuses to run if `assign()` ever starts returning sorted files,
because it could then no longer tell the two apart and would be green without being about
anything.

**Kept deliberately**: the aggregate job is still named `corpus - check_all.py` (with the em
dash the file uses), because branch protection and Railway's gate are configured against that
string and a required check that stops existing stops being required. **Refused deliberately**:
caching `compose()`, which is ~60% of the suite's cost and would take it under ten minutes on one
core -- it would make `test_composing_one_brief_does_not_change_another_s_result` pass TRIVIALLY,
and that test's own docstring records an audit having already proved it vacuous once. Three
unfailable guards is not a price worth paying for time six runners buy for nothing.


## Phase 12 — The sheet in the round

*Raised by Lucas on 8 September 2026 against Dilum Sanjaya's post on 2D schematics transitioning into 3D,
with the question attached whether SVG remained the medium. **The PRD is this phase's brief** —
`docs/prd/phase-12-the-sheet-in-the-round.md`, the first document in a new `docs/prd/` directory, cited by
its filename. Its §1 is the answer: the format was never the constraint (WP-5.11's finding, unchanged and
adopted rather than re-asked), and the missing thing is a constructed-3D layer between the record and the
camera — `build/scene.py` — with the camera as a serialiser and JavaScript learning no more about a house
than it knows about a cyma today. Its §0.1 is the reviewing session's addendum, §8 the packages, §9 the
instrument every package is held to, and §12 the nine rulings. Everything here is Stratum 2 of the
4 September diagnosis's Part IX: a capability of the instrument, inherited by every style. **Nothing in
this phase proposes a score term, a style rule, a parti rule or a room rule.***

**ALL NINE RULINGS WERE TAKEN ON 8 SEPTEMBER 2026, THE DAY THEY WERE PUT, AND AN APPROACH VIEW WAS ADDED
TO v1.** R1 `three` as the third runtime npm dependency, pinned and behind a dynamic `import()`; R2 the
plan cut at 4′-0″, editorial and named; R3 the cornice swept to the envelope rule with the order's own
projection drawn as a ghost line and both named; R4 porch columns only from a stated intercolumniation;
R5 the IFC door default imported rather than restated; R6 the Round lives on the Drawing Set; R7 JS/JSX,
not TypeScript, for this phase; R8 the isometric axon as a token; R9 a flat grade, said out loud. The
addition: **an APPROACH view — a perspective camera at 5′-6″ on the entrance axis — is in v1**, with its
dimensions and datums withheld and the caption saying so, because a perspective dimension is never true.
*Recorded on the day it was given rather than the day it was expected, which is
`docs/reports/wp-8.13-the-programme-that-dissolved-its-own-finding.md`'s finding about an unverified
ruling.*

**THE REVIEW FOUND THAT THE DRAWING SET IS NOT ONE BUILDING, AND THAT IS WHY THERE IS A WP-12.0.**
`workbench/server/corpus.py` routes the plan, section and bearing plates through `_placed` — WP-6.4's one
placement per set — and then calls `build_elevation(plan, pt)` and `build_roof(plan, pt)` with no section,
so both fall into `structure.build_section`'s heuristic default, whose own comment says that default is
*"for INTERNAL callers ONLY"*. The elevation reads placement, so wherever CP-SAT reaches a proof the
elevation plate is of a different house from the plan plate beside it, under a banner WP-6.4 wrote saying
*"one drawing set is one building or it is nothing"*. Pre-existing, invisible to every test, and it would
have been discovered as a failure of the scene's own agreement assertion — so it is fixed first. In the
same package the review spends the cheapest visible win it found: **`render_elevation` has taken a `face`
argument since WP-3.2 and `corpus.drawing` has passed `body.face` since WP-5.1, and no client has ever
sent one**, so three of the four elevations this system can already draw have never been looked at.

**And two citations in the PRD would have failed the build the moment it was committed** — seven report
paths for reports that do not exist yet, which `check_ids.py::check_reports` refuses by construction, and
one open-question slug wrapped across a newline, which `check_citations.py` reads line by line and sees as
its truncated left half. Both corrected in place before the commit, and **both guards were then driven to
prove they fire** rather than reasoned about. The concrete report paths are bare filenames until each
report exists; the `<n>`/`<slug>` template forms do not match the checker's regex and were left alone.

The packages below carry the PRD's own text. **The PRD is the authority on scope and the tree is the
authority on fact** (its own rule 6): where a package finds them disagreeing, the tree wins and the report
says so.

### WP-12.0 The drawing set is one building, and the four faces are addressable

**Status: COMPLETE (8 Sep 2026).** Report:
`docs/reports/wp-12.0-the-drawing-set-was-not-one-building.md`. **The defect was real and it landed on the Four-Foot Porch**: on `spec-builder-colonial`, where `auto` reaches a proof, the elevation record was built on a hill-climb placement and published `porch_clear_depth_ft` at **4.75 ft for a porch the plan beside it drew at 4.00** -- the measurement `porch-too-shallow-to-inhabit` reads, three quarters of a foot in the flattering direction, which is the OQ 52 family. **And the drawn half could not have been seen**: the front is drawn on the WIDTH, which does not move between the two placements, and only the gable ends move -- the faces no client could ask for. On `tidewater-georgian-careful` nothing moves at all, because `auto` spends its budget there and falls back to the same engine, so a sweep of one shipped plan would have found nothing. **The two extra placements are free**, measured: `geometry._SOLVE_CACHE` returns the second and third in 0.00 s against the first call's 25.70. **And the first version of the guards passed with the fix reverted** -- they read the plate's reported solver, which comes from `_placed` whatever the plate was built on; a test of what a plate REPORTS is not a test of what it was DRAWN from. Three mutations, each verified to have landed, each caught by exactly one test from a green baseline of seven.

*Original package text follows, as written.*

**Status when written: NOT STARTED.** Added by the review, not in the original PRD, and first because the scene's
agreement test is written against a drawing set that is one building and it is not. The elevation and roof
plates take the set's own placement (`_placed`) in both `corpus.drawing` and `corpus.export_cad`; both
plates carry the solver's engine and `input_digest`; `api.drawing` becomes a typed wrapper and the Drawing
Set gains the four face chips the server has accepted since WP-5.1. Acceptance: every plate in a set
reports the same digest, and two different faces return different SVGs — a `face` argument accepted and
ignored is the defect this half removes, and equal output would pass a weaker assertion.
**Depends on:** nothing. **Size:** small. Full text: PRD §8.

**RE-DERIVED ON THE MERGED TREE, 9 SEP, AND THE DEFECT WAS WORSE THAN PUBLISHED.** The merge with `main` is done, and this package's own closing instruction -- re-derive rather than quote -- was paid: `porch_clear_depth_ft` on the spec Colonial is **6.00 against a drawn 4.00**, fifty per cent over rather than the three quarters of a foot measured on `f54c5af`; and **the Tidewater plan now reaches a proof inside its budget**, so its two placements no longer coincide and **ten** measurements move -- the ridge height, the eave-to-ridge height and the roof plane area among them -- with **all four faces differing** where none did before. Two published sentences are now false of the tree and are corrected in the report's addendum rather than overwritten: *nothing moves on the Tidewater plan*, and *the front is drawn on the width and the width does not move*. The second was never a rule; it was a property of one plan on one tree, and it read as an explanation. The code is unchanged and all 15 tests pass; what changed is how much the fix was worth.

**AND THREE STATES OF THE TREE THIS PACKAGE DID NOT CAUSE.** The browser walk is RED on `main`, measured by walking a worktree of `origin/main` ALONE and comparing: a label spill on the Pantry, twice, and the Plan Workbench's engine-caption parity check. Byte-identical there and on `main` + this package, which also carries this package's six new Drawing Set checks, all passing. **The spill moved rooms between trees** -- the Centre Passage on `f54c5af`, the Pantry on `main` -- because the merge moved the placement, so attributing it by the room name would have been wrong. On `main` at `5869012` every corpus shard, the aggregate gate, the server tests and the docker build are green and the walk is the only red job. *(The other half of this note -- that `main` had moved six commits past the PRD's `f54c5af`, carrying the other Phase 11's merge -- is SPENT: the merge landed on 9 Sep with no conflicts, and re-deriving the figures across it is the addendum above. Left in the past tense rather than deleted, because it is the record of why the re-derivation was owed.)*

### WP-12.1 The scene record

**Status: COMPLETE (9 Sep 2026).** Report: `docs/reports/wp-12.1-the-scene-record.md`; layer doc:
`docs/scene.md`. `build/scene.py` (pure arithmetic, a leaf), `schema/scene.schema.json` 0.1.0,
`tests/test_scene.py` (15 tests, six mutations, all caught). **Measured on the heuristic: 61
solids on the Tidewater plan and 43 on the spec Colonial, 2 and 3 things not modelled, agreement
0.001 ft between the wall envelope and `slab_boxes` and 0.000 between the datums and the storeys,
every placed room inside the envelope by at least half a wall.** The figures are on the heuristic
DELIBERATELY: `auto` reaches a proof on one machine and spends its budget on another, which is
exactly what WP-12.0 measured happening to the elevation between two trees hours earlier.
**THE FINDING IS THAT THE ROOF WAS NEVER OVER THE HOUSE.** `roof_outline` and
`elevation_profile` lay the roof out from (0, 0) over the OUTSIDE footprint while `wall_lines`
lays the walls out from (0, 0) over the CLEAR one -- two origins half an exterior wall apart, so
read literally the roof sits 1.29 ft east and north of what it covers. It has never mattered
because no surface has ever drawn a roof and a room in one picture, and the scene is the first
thing that had to. Resolved by FOLLOWING `export_ifc.slab_boxes`, whose slabs are already centred
on the clear rectangle, rather than inventing a third convention;
`oq/the-roof-record-and-the-plan-record-do-not-share-an-origin` asks which record should move,
and carries the smaller disagreement underneath it -- `section.footprint` and `slab_boxes` differ
by 0.17 ft about the outside depth of one house, and both are called the outside footprint.
**And two of this package's own defects were invisible in every part and obvious in the whole**:
every exterior wall grew INWARD, each one the right thickness in the right place along its own
axis and the envelope 2.58 ft too small, and the east gable stood at a y coordinate. Both were
caught by summing the extent rather than by reading the expression, which is why the guard is an
agreement between two independent derivations rather than a pinned number. The selftest runs
INSIDE `validate.py` so `TOTAL_CHECKS` does not move (WP-11.6's precedent).

**AMENDED 9 SEP 2026 BY WP-12.2, WHICH FOUND THREE THINGS IN THIS PACKAGE AND MOVED ITS
FIGURES.** The solid counts above are pre-openings: with WP-12.2's `opening-frame` solids they are
**101 and 75**, and `not_modelled` is **1 and 2**; the suite is 18 tests. The three defects: an
opening extruded OUT of its wall on the north and east faces, because `at` was written on the
outside face with an always-positive thickness (it is the LOW face now, and the schema says so);
**the same error in the GABLE ENDS**, which stood 1.29 ft clear of the east and north walls above
the eave, **with this package's own test ratifying it** -- `test_a_gable_stands_on_the_face_it_
names` compared the gable's `at` against the OUTER face of the wall extent, which is exactly where
the wrong contract put it; and a `bounds` block that was the right SIZE in the wrong PLACE, offset
by one wall thickness, **which none of the three agreement figures could see, because not one of
them reads `bounds`**. All three were found by drawing the scene and looking at it -- the same
instrument that found the roof that was a box with a lid, now three defects in two packages that
every number in the record accepted.

*Original package text follows, as written.*

**Status when written: NOT STARTED.** `schema/scene.schema.json` 0.1.0 and `build/scene.py` — pure arithmetic, a leaf
in the manner of `storeys.py` and `axis.py`, importing `export_ifc.slab_boxes`,
`structure.wall_thickness`, `render_plan.relaxation_marks`, `openings.JAMB_FT`, `hearths.breast`,
`compass` and `disclosures` rather than restating any of them. Slabs, walls, gables, roof planes for the
gable family, decks and porch roofs, hearths; spaces, datums, grid, faces, marks, `not_modelled`,
`judgment`, `provenance_counts`, `solver`. `scene.py selftest` runs inside `validate.py` so
`TOTAL_CHECKS` does not move (WP-11.6's precedent). A source-reading test refuses any numeric literal that
is a dimension outside a named editorial allowlist. **Depends on:** WP-12.0 for the placement it is built
on. **Size:** large. Full text: PRD §8.

### WP-12.2 One opening rectangle, three callers

**Status: COMPLETE (9 Sep 2026).** Report: `docs/reports/wp-12.2-one-opening-rectangle.md`.
`build/elevation.py::opening_rects(elev, face)` is the one spelling of `(x0, x1, sill, head)`
**and of the loop around it**, with `render_elevation._window`, `render_elevation._entrance`,
`export_dxf._win` and `build/scene.py::_openings` reading it and every copy deleted.
`tests/test_opening_rects.py` (10 tests, 9 mutations, all red from green).
**AND ITS LARGEST FINDING WAS INVISIBLE ON THE TWO SHIPPED PLANS.** Both renderers resolved the
upper storey with a fallback to the GROUND one and then drew a second row of windows at that datum
unconditionally; **six of the eleven plans that build an elevation state only storey 0**, so each
was drawing a row of openings its record does not hold. Corpus-wide, **244 window rectangles become
124 over 24 plates**. The first measurement of this package was taken over the two shipped plans,
which are both two-storey, and reported that the lift changed nothing but four pixels.
**Measured over all 44 elevation plates against `9aa3a35`: 16 of 44 SVG and 20 of 44 DXF
byte-identical**, both sides proved reproducible run-to-run first; on the two shipped plans alone
it is 6 of 8 and 8 of 8. The two that move are one decimal tie -- the
exact value is 203.35 px and `:.1f` resolves a tie by whichever side of it the double lands on --
and **the unit was then chosen by measurement rather than taste**: over the 144 opening edges the
two shipped plans actually draw, an inches-first rectangle moves 0 DXF coordinates and 2 printed
SVG ones, a feet-first one 0 and **64**. Scene solids 61 -> **101** and 43 -> **75**; `not_modelled` 2 -> 1 and 3 -> 2.
**THE BRANCH THIS PACKAGE EXISTS TO GUARD IS UNREACHABLE FROM THE CORPUS.** OQ 85's blind bay is
what the DXF failed to skip; **all sixteen plan records now produce ZERO blind bays**, because
WP-11.4 moved the stacks off the gable centre line and onto the flues the plan states. A parity
test over the shipped plans would pass with the skip deleted, so the guard is driven and asserts
its own premise. It also found three defects in WP-12.1 (see that package's amendment) and two
false claims in `docs/export.md` -- a 0.9x window shrink and a fixed 3 ft door, neither of which
has existed since WP-6.2, **cited to a test that could never have caught it** because that test
asserts the DXF's widths are a SUBSET of the recorded ones, which is true whether or not the SVG
shrinks.

*Original package text follows, as written.*

**Status when written: NOT STARTED.** `elevation.py::opening_rects(elev, face)` as the one spelling of
`(x0, x1, sill, head)`, with `render_elevation._window`, `export_dxf._win` and `scene.py` as its three
callers and the copies deleted. The review found a third transcription the PRD did not name — the DOOR
rectangle at `render_elevation.py:451` — so it is three removed, not two. The precedent is
`plan_check.furniture_shortfalls` (one spelling, two callers), NOT `openings.required_wall_ft`, which is
deliberately spelled three times. **Depends on:** WP-12.1. **Size:** medium. Full text: PRD §8.

### WP-12.3 The scene route

**Status: COMPLETE (9 Sep 2026).** Report: `docs/reports/wp-12.3-the-scene-route.md`.
`workbench/server/corpus.py::scene()` on `_placed`, `POST /api/scene` behind `_heavy` and `_plan`,
`api.scene` in the client, `workbench/server/tests/test_scene_endpoint.py` (8 tests, 77.0 s).
**THE MEASUREMENT THE PACKAGE OWED WAS TAKEN AND IT DECIDES THE SHAPE, ON THE METER AND NOT ON THE
CLOCK.** On `tidewater-georgian-careful` at `auto`: a cold solve **37.48 s**, a record that already
carries `geometry` **0.00 s**, `build_scene` **0.00 s**, all six named views' plates **0.38 s**, the
whole call end to end **38.46 s** -- so everything but the placement is **2.6% of it**, and the
response is **376,574 bytes raw, about 71 KB gzipped**. Six plates fetched one at a time beside the
scene is SEVEN metered calls per record change against `limits.heavy_calls_per_hour()` of 60:
**eight record changes an hour, where one call buys sixty.** A reader who profiled this route would
have concluded the plates were free and reached the opposite design. `SCENE_PLATES` is the six views
that carry a plate -- **APPROACH is deliberately absent, because a perspective dimension is never
true and a view with no true dimensions has no plate to be held to**. The placed record comes back
for a second reason and it is NOT a cache: it is WP-6.4's rule, one placement and every surface
reading the same building, and a client that keeps it pays 0.00 s on every later export or evaluate.
**TWO DEFECTS, AND THE INSTRUCTIVE ONE WAS FOUND BY READING RATHER THAN BY RUNNING.** `B` and `_os`
are per-function LOCALS in the three neighbouring functions that use them, not module names -- two
`NameError`s on the tests' first two runs, and neither visible to a reader because the surrounding
code reads exactly as though they were module-level. The other was the first draft forwarding the
RESOLVED parti record to `drawing()`, which calls `core.load_parti` itself and takes a caller's
STRING: handed a dict it does `os.path.basename(str(dict))`, finds no file and returns `None`, **so
every plate would have been drawn with NO PARTI while the scene beside it used one** -- WP-12.0's own
defect one layer up, reintroduced by the package that depends on WP-12.0, and **invisible to this
package's own digest guard**, because the digest is stamped on the record `_placed` was handed and
that record is the same either way. **And the first plate figure published was 0.70 s against a
reproducible 0.38** -- it was measured in a process that had not yet loaded the drawing pipeline, so
it carried the module loads; those are real and are accounted for in the 0.98 s end-to-end remainder,
where they belong.

*Original package text follows, as written.*

**Status when written: NOT STARTED.** `corpus.scene()` on `_placed`, `POST /api/scene` behind `_heavy` and `_plan`,
`api.scene` in the client. It is **not** a sixth drawing kind: `test_unknown_kind_names_the_kinds` uses
`axonometric` as its negative fixture and stays true. The package owes a measurement the PRD did not ask
for: six named views each fetching a plate plus the scene is seven metered calls per record change against
a budget of sixty an hour, and the walk already exhausts that budget — so it decides how the plate overlay
is fed before WP-12.4 wires it. **Depends on:** WP-12.1. **Size:** small.

### WP-12.4 The Round: named views, the tween, the plate held to the model

**Status: COMPLETE (9 Sep 2026).** Report: `docs/reports/wp-12.4-the-round.md`. `round/frame.js`
(the camera), `round/solids.js` (the record's four primitives as triangles and edges),
`round/annotate.js` (what a drawing is called) are Three-free LEAVES under `node --test`;
`round/three-scene.js` is the only importer of `three` and is reached only by `await import()`,
which puts it in a **564 KB chunk of its own** (entry 460 -> 477 KB against a 700 KB ceiling)
and keeps it out of `no_bare_imports.test.mjs`'s walk. `Round.jsx` and `RoundPlate.jsx` are the
canvas and the sheet chrome; surface 8's first plate is the model and the five flat plates are
chips beneath it. `data-frame` on all four Python renderers states each plate's own affine --
**16 of 16 plates byte-identical across it, WITH THE ATTRIBUTE STRIPPED** -- and that qualifier
is the package's last finding. The corpus sheet hash itself MOVED
(`373d0116be7cecb8 -> 535077ae0bca1ea2`) and three commits shipped red on
`test_no_shipped_sheet_moves`, because the property was verified by hand and the guard that
measures it was not run. Stripped of the attribute the corpus is WP-11.14's value to the
character; the pin asserts the stripped hash FIRST, so a later package cannot buy a green tick by
re-pinning the raw number. App suite 86 -> 117 tests, router-unit 61 -> 63,walk 152 -> 162 check sites, `check_frontend.py` gains a third lazy-chunk assertion, driven both
ways.
**THE APPROACH VIEW IS NOT HERE AND THE VIEW-BAR LINE BELOW IS CORRECTED FOR IT.** The 8 Sep
ruling putting a 5'-6" perspective view in v1 stands; **WP-12.7 lands it**, beside the entrance
and porch it exists to show. At this package the model is an undressed massing and eye height is
where a missing cornice is least forgivable, so `frame.js` carries ONE projection kind. Leaving
the bar's line naming a chip that is not there is the "until X lands" lie in the other direction.
**TWO FINDINGS, BOTH FROM A MUTATION BEING BLIND RATHER THAN FROM READING.** `PLANES.xz` maps
(u, v, n) to (x, z, y) and **x cross z is MINUS y**, so that frame is LEFT-handed while the other
two are right-handed: swept solids came out wound inward while the hand-wound box came out right,
and a flat sun would have lit every opening reveal and gable from inside the house. Orientation is
COMPUTED from the solid's centroid now. And serving the flat plates out of `scene.plates` stored
`got["svg"]` alone, so the bench's elevation silently lost WP-3.2's disclosure, the entrance face
and the engine-and-digest line -- **the browser walk was the only thing that caught it**, on two
checks that read the caption; no Python test saw it, because `test_scene_endpoint.py` was
asserting that the picture was a picture. Also measured: **no plan in this corpus states a lot**
(0 of 16), so `render_plan`'s whole site block is unreachable and its guard had to be driven.
New question: `oq/an-elevation-does-not-state-which-end-of-the-face-it-starts-from`.

*Original package text follows, as written.*

**Status when written: NOT STARTED.** `round/frame.js` and `round/annotate.js` pure and tested under `node --test`;
`round/three-scene.js` the only file that imports `three`, behind a dynamic `import()`; `Round.jsx` and
`RoundPlate.jsx`; the view bar `PLAN·Ln · S N E W · AXON·SW/SE/NW/NE · ROOF · APPROACH`; `data-frame` on
the four Python renderers so the plate overlays the model at the same frame. Every colour and pen width
resolves to a `tokens.css` name, and the pen does not magnify with the zoom — which answers OQ 66 in the
Round by construction and should say so. **`annotate.js` may not import `sheet/label.js`**: that file
imports React and `no_bare_imports.test.mjs` would turn a green local run red in CI, which is the
`coastTiers.js` trap. **The bundle baseline is measured rather than assumed: the entry chunk was 444 KB when this package was planned and is 477 KB today against `check_frontend.py`'s 700 KB ceiling**, with the two coastline tiers already kept out of it -- so there is about 223 KB of headroom, which is not enough for `three` to be allowed into the entry chunk and is why R1's condition is that it is not. **Depends on:** WP-12.3. **Size:** large.

### WP-12.5 Overlays and modifiers

**Status: COMPLETE (9 Sep 2026).** Report: `docs/reports/wp-12.5-overlays-and-modifiers.md`.
Six overlays and three modifiers, each a pure leaf under `node --test`, each stated in the caption
when active and addressable in the URL. `sheet/overlayRules.js` is the one spelling of the three
analytic rules, which lived inline in `Sheet.jsx`'s JSX; `derive.js::elementBounds` and
`corpus.rooms_meta` are two further copies removed before a second surface could make them.
**THE FINDING IS THAT LOOKING AT THE SHEET PRODUCED A FALSE POSITIVE, for the first time in eight
packages.** I read one tone off a screenshot, concluded the privacy overlay drew nothing, and
pushed that as `46f612f` ("AND THEY DRAW NOTHING"). It is false. The canvas states what it built
(`privacy:24, wet:4`, reconciling exactly with the record) and a pixel band gives ONE floor tone
with the overlay off and THREE with it on, on the ramp. **Looking at the sheet finds defects; it
does not adjudicate them** -- on a translucent mark the absent overlay and the faint one are the
same picture. The half that stands: the walk checks asserted the URL and the caption and never
that anything was drawn.
Two defects found by the lift, both unreachable from the corpus and both driven: `|| 2.25` eating
a stated `depth_multiplier: 0` (12 placements, **0 drawing a wash**), and a privacy ramp unbounded
in both directions whose falsy guard covers one bad rank by accident. Three PRD sentences the tree
had overtaken are corrected in the modules rather than followed. App suite 117 -> 147, walk
162 -> 177.

*Original package text follows, as written.*

**Status when written: NOT STARTED.** The bay grid, datums, daylight reach, wet stack, privacy gradient, the △ marks
and the 2D plate as overlays; explode by level, explode by element, and a real section cut with poché
caps as modifiers; each computed in a pure module, each composing with any view, each stated in the
caption when active and addressable in the URL. The exploded drop-line count is held to
`disclosures.transfers(plan)` — **not** to `geometry_report.vertical`, which the review found is prose
rather than a count. **Depends on:** WP-12.4. **Size:** medium.

### WP-12.6 The envelope dressed

**Status: BUILT (9 Sep 2026).** `docs/reports/wp-12.6-the-envelope-dressed.md`. Sashes, meeting rails,
shutters and chimneys: **Tidewater 101 -> 492 solids, the spec Colonial 75 -> 368**, `opening-frame`
unchanged at 40 and 32 — this package changed how an opening is dressed and not which openings exist. The
sill is REFUSED, because `window_sill.projection_in` resolves to a BAND and a drawing cannot draw one
(`oq/a-child-band-replaces-an-ancestor-derivation` reaching its first consumer). A stack whose plan size
carries `judgment: true` is a two-vertex AXIS and never a solid; `judgment` 0 -> 2. The dormer solids and
the swept cornice, water table and belt are NOT built and are refused by name — the cornice goes with the
columns in WP-12.7, where one sweep serves both, and the eave-projection question R3 records goes with it.

**AND THE PARAGRAPH THIS ONE REPLACES CARRIED A FALSE CORRECTION, WHICH IS HOW THE PACKAGE'S SECOND
DEFECT WAS FOUND.** It said to read `refused` / `placed_count` / `placement_shortfall_note` / `positions_ft`
because *"there is no `placeable` and no `not_drawn_reason`, which the PRD assumed"*. Both fields exist:
`elevation.py` 1971-1980 writes them and `render_elevation.py` has read them in two places since the day
they landed. Following the plan would have re-derived `placeable`'s judgment from `refused` — a second
reader of one question. **Reading the writer to verify that claim is what exposed the real defect**: the
key is `dormers`, PLURAL (`elevation.py` 2012), and `scene._dormers` read the singular, so it took `{}` on
every record in the corpus and drew, refused and disclosed nothing. Its own three tests could not see it,
because all three drive the function with a hand-built dict carrying the same wrong key as the code. That
is the SECOND field this package read off the wrong record — `shutters_carried` is per storey window, not
on the elevation, and drew no shutter anywhere until a class census caught it. **Neither was found by
reading the code that consumed it.**
**Depends on:** WP-12.2 and WP-12.4. **Size:** large.

### WP-12.7 The entrance and the porch

**Status: BUILT (9 Sep 2026).** `docs/reports/wp-12.7-the-entrance-and-the-porch.md`. The doorcase and
the stoop, and the APPROACH view the 8 Sep ruling put in v1. Tidewater 492 -> 500 solids, the spec
Colonial 368 -> 374; app suite 147 -> 156.

**THE REFUSAL THIS PACKAGE WAS ASKED TO WRITE HAD BEEN IN THE RECORD SINCE WP-11.4.** R4 asks for porch
columns "placed only by a stated intercolumniation and refused by name otherwise" -- and
`build/threshold.py` already refuses exactly that on both shipped plans, in the record's own words
(*"'tidewater-georgian' states no canonical portico (canonical porch type: stoop-only), and its
`portico_bays` of 1 is conditioned by its own slot rule"*). `_porch` READS `plan.threshold.unplaced` and
republishes each reason; a source guard refuses `portico_bays`, `intercolumniation`, `porch_support` and
`porch_type` in that function. Following this text literally would have written a second reader of one
rule. Re-derived first: 23 nodes make a portico canonical, 8 resolve a bay count, 1 states a diameter,
**0 have all three**.

**AND A PILASTER IS NOT IN THIS DOORCASE, MEASURED.** door + 2 casings + 2 sidelights = 84.199 =
`entrance_composition_width_in` to the thousandth; with pilasters it is 88.875. So the composition's own
arithmetic excludes one, and the entablature, the casing band and the two sidelights are what is drawn.

**THREE MORE OF THE TEXT ABOVE ARE OVERTAKEN.** `order_at_the_eave` NAMES NO ORDER -- it is a
three-state verdict on whether an order engages the WALL, and both plans read 0. The shaft diameters are
equal by a stated, disclosed parallel-shaft fact, so a lathe would invent a taper. And the Four-Foot
Porch cannot become visible as an outbuilding: **both shipped plans place their `entry-porch` INSIDE the
footprint**, so its floor is the ground slab and its roof is the main roof -- `deck` and `porch-roof`
stay unused classes and that is the record rather than a gap. The stoop, which really is outside, is
drawn.

**THE APPROACH IS IN, WITH ITS DIMENSIONS WITHHELD.** Eye at the ruled 5'-6", standing off the front the
record names, at a distance DERIVED from the framing and a field of view that is EDITORIAL and says so.
Four refusals come with it: a point behind the eye returns null rather than a mirrored coordinate, no
flat plate is laid over a perspective, a move between the two projections is a CUT, and the furniture
table gives it a compass and nothing else.
**AND LOOKING AT THE APPROACH VIEW FOUND THE TWO DOORS.** The stoop stands away from the door it
serves, because `elevation._face_bays` puts the entrance in the MIDDLE BAY of the front whatever
the placement did: the elevation draws it at 32.79 ft against a placed 38.21 on the Tidewater
plan and **25.67 against 47.00** on the spec Colonial, where the drawn front door stands over the
GARAGE. The scene is the first surface to draw both, and `plan_check` already convicts the
PLACEMENT for the displacement the DRAWING corrects. Nothing moved -- the disagreement is stated
naming both positions, and
`oq/the-elevation-draws-the-front-door-where-the-composition-wants-it` carries the ruling.
**Depends on:** WP-12.6. **Size:** medium.

### WP-12.8 The adversarial audit of WP-12.0 through 12.7

**Status: COMPLETE (9 Sep 2026) — `docs/reports/wp-12.8-the-adversarial-audit-of-phase-12.md`.**
Four read-only auditors on different angles (call chain and consumers; second-order risk; second
occurrences of the five patterns 12.6 and 12.7 had already fixed once; whether the new tests can fail,
in an isolated worktree with sixty mutations). **Four blocking defects, all introduced by that session,
and three of them one mistake made three ways: a coordinate read in the wrong frame.** Every dressed
member on the north and east faces drawn INSIDE its wall (1,769 of 3,482 solids, the spec Colonial's whole
doorcase, since its entrance front is the N face); `_chimneys` reading `grade_to_cap_ft`, which nothing
writes, so every stack stood 6 ft short of its own record and below a style minimum the same record
judges `ok: true`; `_entrance_agreement` comparing the elevation's `u` against a clear-frame plan
coordinate, so a house whose two records AGREE would have been convicted by one wall thickness; and a
caller-supplied `threshold` able to build half a million solids on `POST /api/scene`.

**NONE WAS VISIBLE TO ANY ASSERTION IN THE TREE, AND THE REASON IS THE FINDING**: every test written for
those two packages read a member's IN-PLANE extent and not one read the third coordinate. When a package
adds a dimension, assert on that dimension.

Also fixed: `_chimneys` nested inside `_roof`'s success path, so a house whose massing calls for stacks
and whose roof judges no ridge had them UNCONSIDERED rather than refused; `bounds` no longer being the
envelope `frame.js::modelAt` reads it as (the Tidewater E plate slid 2.166 ft); no pen for the
`construction` ink, so the corpus's only two `judgment` solids drew as measured edges; a drag on the
approach moving the sun and not the house; the level join, taking solids that state their storey from 57
to 494; and eight smaller refusals-about-nothing and guards-that-could-not-fire. Three published figures
re-derived. **Twenty-three mutations, all red; two of this session's own guards were blind on their
first run and are recorded rather than quietly fixed. Depends on:** all of the above. **Size:** medium.


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

### WP-12.9 The five items WP-12.8 deferred

**Status: COMPLETE (9 Sep 2026) — `docs/reports/wp-12.9-the-deferred-items.md`.** Closes §V of the
audit. Two of the five needed a ruling and both were given the day they were put: *snapshot +
checker + plan disclosure* for the chimney judgment, and *remove them from the schema* for `sweep`
and `lathe`.

**THE FIRST ITEM WAS NOT THE QUESTION THE AUDIT ASKED.** It was deferred as *"a data question about
which record owns the figure"* — the two readers agreeing at 22 in by construction. Measured, they
agree on the NUMBER on all 14 styles that resolve one, 0 disagreements, and disagree on whether it
is a JUDGMENT. **Over the 93 baked snapshots matchable to a source rule, 13 drop a `judgment: true`
and ZERO carry one** — the bake has never carried the flag, and `check_baked_snapshots` was green
over every one because it re-derives the value and compares nothing else. `schema/kit.schema.json`
admitted `judgment` on a SLOT and not a PARAMETER, so the corpus had no way to say the number was a
decision; the data edit failed validation on its first run, which is how that surfaced.
`check_baked_flags` holds every snapshot to its source rule in BOTH directions (93 matched and
agreeing, 50 could not be compared, ratcheted at 50 with the two-unit gap from 52 accounted).

**AND THE PLAN SHEET WAS A THIRD SURFACE THE AUDIT HAD NOT COUNTED** — elevation legend and scene
disclosed, `render_plan.py` and `Sheet.jsx` drew a poché square and called it a measurement. Fixed
through `disclosures.stack_plan_judgment`, one spelling, with the BASIS carried beside the flag.

**Deferred out of it:** `oq/the-plate-does-not-read-the-disclosure-module-it-imports` —
`render_plan.py` imports `disclosures.py` and, before this package, called nothing from it, while
`mcp_server/core.py` calls `banner()`. The two lists have diverged in both directions and all
sixteen sheets move on a reconciliation, so it is its own package with three things to rule first.

**One shipped sheet moved (+296 bytes), and removing the one field this package added gives all
sixteen byte-identical to the previous commit** — the accounting proved rather than reasoned.
**Depends on:** WP-12.8. **Size:** small.
