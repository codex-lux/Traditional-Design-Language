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
  not done, and any new open question as a NEW FILE in `docs/open-questions/<nnn>-<slug>.md`
  (`docs/open-questions.md` is GENERATED — run `build/gen_open_questions.py`; and take the
  next id from the BASE BRANCH, never from the working tree, which collided four times).

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

## Where the work stands (3 Sep 2026)

**READ `docs/reports/project-review-2026-09-03.md` FIRST if you are about to plan work rather than
do a named package.** It is the second review of the whole project against `VISION.md` and the
UI/UX documents (the first is `project-review-2026-08-26.md`, and both are kept: the earlier one is
the record of what the project looked like before Phases 6 through 9). Its verdict in one line:
**the checker has arrived and the generator has not**, and the three rulings that unblock the
generator — the dependency, the register, and the proportion floor — are recorded and unbuilt. Its
§IV is the current list of things the system says that are not true, and it supersedes any older
ranking of those. **This heading said 27 Aug for a week, above entries dated 2 Sep**, which is the
same class of staleness as the "until X lands" trap below.

Phases 0, 1, 2, 3 complete. Phase 4 complete through WP-4.3, WP-4.5 and WP-4.6; WP-4.4 is
environment-blocked. **Phase 5 is part-built** — WP-5.1 (DXF/IFC export), WP-5.2 (the workbench
in `workbench/`), WP-5.5 (drawing-to-record ingestion), **WP-5.6 (the navigation overhaul)** and
**WP-5.11 (the geometry layer)** have shipped; WP-5.3 and WP-5.4 remain. **Phase 6 — plan semantics — is COMPLETE** (WP-6.1,
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

**Phase 7 is COMPLETE** (WP-7.1 through 7.5, 27 Aug) — the three half-open questions and then
their remaining halves. Reports: `docs/reports/wp-7.{1,2,3,4}-*.md` and
**`wp-7.5-the-adversarial-audit.md`**, which is the audit of WP-7.4 and the one to read first
if you are about to trust a number this phase published: it found two blocking defects WP-7.4
had introduced, one of them a false claim in WP-7.4's own commit message, the same span bug a
second time in `render_section.py`, and six tests that passed with the fix reverted.

**Phase 8** (WP-8.1 through 8.4 and 8.6, 28 Aug; **WP-8.7 2 Sep**) — the register as a directory and
the frozen id (8.1), OQ 51's refusal half (8.2), the forbidden slot (8.3), the construction scope
and the 331 unevaluated exception preconditions (8.4), and
**WP-8.6, the adversarial audit of the other four** —
`docs/reports/wp-8.6-the-guards-that-could-not-fire.md`, and the one to read first if you are
about to trust anything this phase built.

**THERE IS NO WP-8.5, AND THE GAP IS DELIBERATE RATHER THAN A MISSING REPORT.** The plan named
one — OQ 89's withheld measurements and the `total_shutter_leaves` constant — and that work
SHIPPED, as `6f9e7c7`, under its OQ ids and before the WP-8 numbering existed on this branch.
Its subject is `OQ 88 and 89: a fault cleared on shutters that were not there`.
(Quoted as a CODE SPAN, and on ONE LINE, for a reason worth knowing: the subject carries a bare
continuation number, which `check_citations.py` refuses in prose and exempts in a quotation --
but that checker reads line by line, so a code span straddling a newline has no closing backtick
on either line and is not a code span to it. A pushed commit subject cannot be rewritten to suit
a checker written after it, so the quotation has to be shaped to the reader.) So the package has a commit and
a closed question and never had a number. The series is 8.1, 8.2, 8.3, 8.4, 8.6, and then
8.7 (the adjudication passes), 8.8 (the baked snapshots) and 8.9 (OQ 51's delivery half).
Renumbering 8.6
down is not available: `2601c0e`'s subject names it, and a pushed commit subject cannot be
rewritten — the same constraint OQ 90 records for `f768c02` and `426ed35`.
**This entry exists because the audit's own report claimed to cover "WP-8.1 through WP-8.5" and
CLAUDE.md listed a package with no commit, no report and no plan section.** Nothing checks a
range stated in prose, which is the finding WP-8.6 is about, appearing in WP-8.6's own title.
`2601c0e`'s message carries the wrong range and cannot be corrected; it is recorded here
instead. **It found eight blocking defects, and every one was
something CLAIMING to have been checked**: three shipped guards that could not fire (the CI
id-collision gate walked the ids the branch ADDED and then required them to be IN the base
branch — complements, so the loop body was unreachable), two readers pointed at the node's own
kit file where the corpus's answer lives in the cascade (`plan_check`'s style layer was blind to
879 forbidden bindings and 3,661 forbidden variants, on all 132 nodes; `mcp_server/core.py`
carried a second truncated cascade dropping 1,308 ancestors and contradicting 206 forbidden
records, served to users through `tdl_resolve_kit`), and a verdict that said "no precondition"
about 104 records that carry one. **Nine tests could not fail**, each proved by an auditor
mutating the code and watching the suite stay green.

**Three of the four worst findings were invisible to both shipped reference plans** — byte-
identical output before and after. That is not a caution any more; it is the highest-yield
technique in this repository, and it found all three in seconds.

**WP-5.6 changed how the workbench is addressed, and it is worth knowing before touching it.**
A place is now a URL, and that URL is the citation grammar written down — `#/kit/craftsman/cornice`,
`#/faults?sev=serious`, `#/cite/fault:porch-too-shallow-to-inhabit`. `app/src/router.js` and
`state/nav.js` hold it; `citeFor()` in `citations.js` is the inverse of `routeCite` and lives
beside it so the two cannot drift. **The grammar is spelled in three places — `REF_RE` and
`CITE_RE` in `workbench/server/`, `parseCite` in the app — and an audit found two of the three
disagreeing about the dot in a constraint id, which is why `test_grammar_agreement.py` now
reads the JavaScript and holds all three against each other. Do not add a fourth copy.** Search is `⌘K` over `/api/search/index` (666 named things,
dispatching by citation); `/` filters the list in front of you; `?` explains both. Filters live
in the query string via `filters/useFilters.js` — do not reintroduce per-surface filter state.
`Chip` is now only ever a filter; acts are `ActionChip`. Report:
`docs/reports/wp-5.6-navigation-overhaul.md`.

164 nodes · 97 slots (ontology 0.7.0) · 40 massings · 60 rooms · 17 groupings ·
**30 opening-grammar rules covering all 1,890 room pairs** (WP-6.2, editorial; every rule quotes the corpus prose it reads and `build/check_openings.py` verifies the quote against the record it names) ·
**21 partis naming 129 of 132 styles, 0 uncovered, and 21 of 21 composable for their own
style** · **57 packs, 132 of 132 nodes bound** (OQ 49; but read OQ 51 before trusting that number -- it counts a node's OWN bindings and the lineage cascade delivers packs nobody bound) — but 49 nodes still have no opening-role pack
and 46 no facade-role pack, down from 68 and 67 (WP-4.6's measured movement) · 660 constraints
migrated, 61.5% of hard ones tested · 210 faults · **159 of 159 kits populated** · 1,556 kit
parameters (74.6% measured, 12.8% editorial of which 0 are now silent — OQ 18's note half) ·
1850 image records, **73 sourced** (the first ever — drawn by the corpus from its own
proportion packs; 1777 still wanted, and 858 of those can never be harvested) · 14 reference plans · 26 MCP tools · **50 checks, 1,741 tests**
(plus the workbench app suite, **85** under `node --test`). Those figures were 970/36 before the
infrastructure audit collected them and 762 before that, and the CHECK figure said 32 against a
suite of 33 until WP-5.11 read the total. **It said 32 again for an hour on 27 Aug, in this
sentence, for the same reason** — the 27 Aug merge resolved the conflict here by measuring
`len(check_all.CHECKS)`, which is the 32 checks the LOOP runs and excludes the three the runner
appends after it (`pytest tests/`, `pytest workbench/server/tests`, `node --test
workbench/app`). The number to read is the runner's own `len(results)`, printed as "All N checks
passed"; the app-suite figure is the `# tests` line from `node --test`. **And there is a trap in
the line CI actually prints, and it is an IDENTITY rather than a coincidence**: with the CAD
libraries and fastapi absent, exactly three checks are unjudged there (`export_dxf` and
`export_ifc` selftests, `pytest workbench/server/tests`), and `TOTAL_CHECKS` is `len(CHECKS)`
plus the three appended suites -- so the PASS count the corpus job prints is
`TOTAL - 3 = len(CHECKS)`, ARITHMETICALLY, every time. It read "32 of 35 checks passed" on
27 Aug against a `len(CHECKS)` of 32, read "34 of 37 checks passed" earlier on 28 Aug against a
`len(CHECKS)` of 34, read "39 of 42 checks passed" after WP-4.4's asset checker against a
`len(CHECKS)` of 39, read "40 of 43 checks passed" after WP-9.1's critic-suspect meter against a
`len(CHECKS)` of 40, read "41 of 44 checks passed" after WP-9.2's move-registry check against
a `len(CHECKS)` of 41, read "43 of 46 checks passed" after WP-9.7's
grouping-rule checker met PR #19's move-registry check at the merge, against a `len(CHECKS)` of
43, read "44 of 47 checks passed" after WP-8.9's stranding sweep against a `len(CHECKS)`
of 44, read "45 of 48 checks passed" after WP-11.3's furniture grammar, and reads
"46 of 49 checks passed" after WP-11.4's threshold grammar, and reads
"47 of 50 checks passed" after WP-11.6's stacking checker, against a
`len(CHECKS)` of 47. **Two sessions each added a check and each published 44**, which is the fifth time
this number has gone wrong at exactly a merge; the guard caught it here too.
An earlier version of this sentence called that a coincidence, which told the next reader it
probably would not happen to them; it happens at every check ever added. **Read the SECOND
number.** `check_all.TOTAL_CHECKS` and
`tests/test_counts_guard.py` now enforce this -- the latter pins both the published total AND
the largest `N of M checks passed` quoted in this file, so neither the figure nor its
illustration can rot again. Both were re-measured
27 Aug after `check_all.py` itself printed "1 of 35" against this file's 32. **And the guard
then earned itself at the very next merge**: PR #14 brought a 33rd check and 162 more tests, so
35/909 became 36/1,071 on 28 Aug — caught by `TOTAL_CHECKS` at the merge, which is the exact
point this number has gone wrong every single time. **And again at the very next commit**: WP-8.1
added `check_citations.py` and nineteen tests, so 36/1,071 became 37/1,090 — the guard failed
the build before the number could go stale, which is the whole of what it is for. **It has now
earned itself five more times in one day**: the register-as-a-directory added `check_ids.py` and
`gen_open_questions.py --check`, the refusal half a forbidden-slot meter, the forbidden slot its
own tests, and WP-8.4 the construction vocabulary -- each caught at the first run rather than by
the next reader. The rest of the
numbers here are the 27 Aug merge's own measurement (`pytest --collect-only` for the test
total), taken because main and this branch had
drifted to 33/1,009 and 35/1,006 respectively and NEITHER was right. `check_counts.py` polices
counts DERIVED FROM THE CORPUS, and neither a test count nor a check count is one of them, so
**every number in this paragraph goes stale silently** -- and on 3 Sep the HAND CORRECTION
ITSELF FAILED TO LAND: the merge that made the test count stale measured 1,569, edited this
line, and committed the INDEX, which still held 1,546. `git commit` without `-a` takes what was
staged, and the staging had happened before the measurement. `65901a2`'s message says the number
"was measured with pytest --collect-only and corrected here" and its diff contains no such
correction -- a false claim in a pushed commit message, the shape WP-7.5 records for WP-7.4,
committed by the very commit congratulating itself on catching the sixth staleness. **Re-read
the file after correcting a number in it**; the only thing that has ever caught one of these is
looking at what actually landed -- nor are numbers written into JSX, which
is how the Kit's header claimed 95 slots against an ontology holding 97.
**Every open question Lucas has ruled on is executed** as of 25 Aug 2026 — OQ 12, OQ 13, OQ 14, OQ 15,
OQ 19, OQ 26, OQ 27, OQ 29, OQ 31, OQ 32, OQ 33, OQ 34, OQ 35, OQ 36, OQ 37, OQ 38, OQ 39, and 40 through 46 besides. **OQ 18** is HALF CLOSED: all 162 silent editorial
parameters now say they are editorial and quote the basis their slot states, so the count of
unexplained numbers is 0; the SOURCE half is environment-blocked and none of the 162 may be given
a source from a secondary work.
WP-4.6 raised **OQ 47, OQ 48 and OQ 49**. **OQ 47 and OQ 49 are CLOSED** — `expressed_frame` at ontology
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

**WP-5.7 changed the shell's proportions and the atlas's resolution, and both are worth
knowing before touching the workbench.** Raised by Lucas against a screenshot of the map:
*"the map is VERY crude and doesn't take well to zooming in since the resolution does not
scale up as you zoom in"*, plus full screen, collapsible rails and draggable margins.
**The crudeness was two defects wearing one symptom, and the first is the one to remember:
`vector-effect` is not an inherited property**, so `vectorEffect="non-scaling-stroke"` set on
a `<g>` reached none of the paths inside it, and the coastline's `strokeWidth={0.7}` was 0.7
DEGREES of ink -- seventy pixels at the zoom the reader was complaining about. Third instance
in this codebase of a per-element SVG property set on a parent and ignored; the e2e walk now
asserts the general form (no stroked mark in the atlas may carry a `stroke-width` without a
`vector-effect` of its own). The second defect was real too: one outline at every scale. There
are three now -- `workbench/scripts/make_coastlines.py` generates coarse/medium/fine from
Natural Earth 110m/50m/10m, `surfaces/phylo/coastTiers.js` fetches the one the scale has
earned, and **while a finer tier is in flight or has failed the legend says what is actually on
the plate** rather than letting a facet pass for a shore. `MIN_W` is 3 degrees because that is
what the finest data can honestly draw, not because of taste. Rings are culled by generated
bounding boxes; the graticule steps with the scale (`graticule.js`); the wheel handler is
native and non-passive, because React's passive `onWheel` meant the page scrolled while the
map zoomed. **A per-element SVG property set on a parent is this codebase's most-repeated bug and the
guard against it must read COMPUTED STYLE**: the first version of that guard filtered on
`getAttribute('stroke-width')`, but `stroke-width` IS inherited, so the very marks the bug
lives on were dropped from the population before the test ran and reverting the fix left it
green. **The atlas's viewBox now takes the pane's own shape and its height is DERIVED, not
stored** -- a fixed 134:43 box in a 4:3 pane letterboxed 27.8 degrees of latitude, and the
ring cull, the graticule and the pointer maths all read the viewBox as though it were the
plate: South America vanished from the home view and a wheel zoom drifted 3.12 degrees every
two notches. One mismatch, three defects; do not reintroduce a stored height.
**`state/layout.js` is a fifth external store** -- pane widths and folds, in
localStorage, deliberately NOT in the URL, because a citation that carried the sender's rail
width would be handing the reader the sender's monitor. **It holds TWO numbers per pane** --
what the reader chose, persisted, and what fits this window, derived -- because the first
version had one and let a moment of a narrow window overwrite all eight panes' widths
permanently. **Eight panes pull** — the two rails, the
Phylogeny's record, and the five surface index panels that were fixed numbers in their own JSX
(`components/PullPane.jsx`) — and widths clamp on READ as well as on write. Only the first
three FOLD (`[` and `]`, or the spine): `PANES.foldable` is the difference between chrome and
subject, and a Fault Corpus with its fault list folded away is not a decluttered Fault Corpus. The atlas can take the whole
window; `layout.full` is the one piece of layout state that is not persisted, which is what
"temporarily" means. `--rail-left` and `--rail-ai` are gone from `tokens.css` on purpose -- do
not reinstate them. **The workbench app's `node --test` suite may not import anything from node_modules.**
`check_all.py` runs it with no npm install, so a package import there is a green local run
and a red CI one -- which is exactly what happened to WP-5.7's first audit pass, via
`coastTiers.js` importing React for one hook. The hook lives in `useCoastline.js` now and
`src/no_bare_imports.test.mjs` walks the suite's import graph to keep it that way.
**Four adversarial audits then found eleven of the package's forty-three new assertions
passing on the code they were written to guard** -- among them the fine coastline tier being
replaceable wholesale by the coarse one with the suite green, and a documented keyboard
control that was never wired to its element. Read the report's audit section before adding a
test here; the suites are now mutation-checked and the harness is worth reusing. Report:
`docs/reports/wp-5.7-the-atlas-and-the-shell.md` · new open question: OQ 72.

**THE INFRASTRUCTURE AUDIT (27 Aug 2026) measured the deployment for the first time, and the
headline is that the ceiling is about ONE person, not a handful.** Reading the corpus is
comfortable for dozens (100-560 rps); **editing a plan is the bound**, because
`PlanWorkbench.jsx` re-evaluates on a 400 ms debounce and one evaluate costs 338 ms of CPU, so
one person dragging a wall consumes ~85% of the server's entire evaluate capacity. Two editors
see 899 ms, four see 2.0 s, eight see 4.2 s. Throughput is FLAT across the whole ladder --
~2 evaluates and ~4.5 drawings a second whatever the concurrency -- because it is one core,
fully serialised. `workbench/scripts/load.py` is the harness; run it against a server you
started, with `HEAVY_CALLS_PER_HOUR` raised, or you measure the rate limiter instead.
**Four uvicorn workers buy ~4x and break compose five times in six** (measured: 6 jobs
submitted, 5 answered 404 by a worker that never saw them) -- that is OQ 36, and the audit
supplies the numbers its ruling was missing. **Storage: ~733 MB image, no volume, no database,
and 497 MB of it -- 85.5% of the dependency layer -- is `ezdxf`/`ifcopenshell`/`ortools` and
their transitive `pandas`/`numpy`/`fontTools`.** Report:
`docs/reports/infrastructure-audit.md` · new open questions: OQ 73-77.

**Phase 11 — the drawn sheet — is COMPLETE through WP-11.14 (8 Sep 2026).** The A line (the
drawing) is finished: WP-11.1 and WP-11.2 put the sheet in Graphic Standard No. 1 with the wall
as a body, WP-11.3 the furniture, WP-11.4 the threshold and the stacks, WP-11.5 the embedded
face. **The B line — the placement — is WP-11.6 through WP-11.9.** WP-11.6 is a record edit that
moved the placement (`plans/tidewater-georgian-careful.json` now declares the two `stacks_over`
claims its own parti had always made); **WP-11.7** made the room's own proportion band a hard,
downgradable CP pin outranking the record's `exterior_walls`; **WP-11.8** made the band the first
key of the SEARCH's candidate acceptance, in both directions; **WP-11.9** taught the six layers
below the placer about massing elements, on four rulings, with the whole shipped corpus
byte-identical; **WP-11.10** placed the terrace at grade; **WP-11.11** taught the PROVER about
massing elements and closed
`oq/the-proving-engine-cannot-place-a-second-massing-element`; **WP-11.12** gave the critic a span
finding, which is OQ 98's reporting half; **WP-11.13** fixed the element box that could not hold
its own rooms, closing `oq/the-coverage-floor-is-an-exact-cover-per-element` — and the tagged
Tidewater is PROVED; **WP-11.14** taught the DRAWING about massing elements, which is the seventh
layer. Reports: `docs/reports/wp-11.{6,7,8,9,10,11,12,13,14}-*.md`. **This heading said WP-11.10 "is gated on
`oq/the-proving-engine-cannot-place-a-second-massing-element`" and it was not** — that gate
applied only to reading a terrace as a third massing ROLE, and the CP refusal keys on the room's
`block` TAG, which an appendage does not write. The question is still open and still gates the
shipped-record dependency tags, which is the sentence that was true all along and got attached to
the wrong package.

**Phase 8: WP-8.1 THROUGH 8.4 AND 8.6 COMPLETE (28 Aug 2026); WP-8.7 IS THE BACKLOG ITSELF AND IS
IN PROGRESS (2 Sep)** — the register, the refusal half of OQ 51, the forbidden
slot, and **WP-8.4, which read the fault corpus's exception preconditions for the first time**.
331 of 846 exceptions carry a condition on the wall, the roof or the date and all three of
`core.py`'s selection sites matched on the style id alone, so `architrave-that-is-not-there`'s
Pueblo Revival licence — written for adobe — was excusing a house whose style resolves
canonically to stucco-over-wood-frame. The field is `granted_when` now (it was a SECOND
`applies_when` in the same schema, meaning something else, which is why nothing read it);
`build/construction_vocabulary.py` is a CLOSED table mapping 61 of the 78 tokens in use onto
variant ids that already exist and recording 17 as unmappable with a reason; and where a
precondition cannot be resolved AND the exception carries a `bounds_test`, **both rules are run
and compared** — unjudged only where they disagree, which over 164 styles is 11 verdicts moving
instead of 26. A fake unjudged is as dishonest in its own direction as a fake pass. **The
package collided head-on with main**, which had shipped its own OQ 88 scope, its own OQ 99 and
its own WP-8.1: main's `scope` field survives and this vocabulary is ported into it, after
measuring that main's substring classifier over the CLADDING disagreed with each node's own
`construction_type` on 13 of 164 styles — `cape-dutch` is sun-dried brick with timber frame
FORBIDDEN and a lime-plaster face carrying no masonry word, so the frame-wall sill rule went to
a mass masonry wall, which is OQ 88's own bug surviving inside OQ 88's fix. Report:
`docs/reports/wp-8.4-the-exception-precondition.md`.

**Phase 9 — the critique and the corrective revisions — is COMPLETE (2 Sep 2026): WP-9.1,
WP-9.2, WP-9.3 (the surfaces) and WP-9.4 (the adversarial audit of the other three).**
Lucas asked for recursive self-improvement — a critic that reads the drawn house, and a
generator that fixes what it finds, in plan and elevation, through many corrective revisions
rather than one procedural pass — and ruled it the same day: a DETERMINISTIC loop (a named move
registry executing corpus rules, `plan_check` re-judging every round, no language model
editing the record); authority over dimensions, declared choices, openings AND optional rooms,
never a room the parti has no place for, a judgment slot, geometry, a critic-suspect, a
`must_have`, or a measurement the plan did not declare; on by default everywhere a product is
made, `--no-revise` to opt out. **WP-9.1 found the critic was judging two buildings at once**:
`plan_check.check` derived the elevation from a FRESH heuristic placement while its drawn layer
read the placement the record carried, under `except: pass`; on the shipped plans the two
happened to agree on all 187 measurement names, and on the proving engine the Tidewater
portico is placed 23 x 3 ft against a declared 6 x 12 and the porch faults now read 3.0 — the
identity defect becoming a number. The bench's evaluate never ran the drawn layer at all. Every
finding now carries structured evidence beside its prose (`kind`, `need_ft`, `have_ft`,
`expression`, `canonical` from the cascade, `engine` on every drawn finding), and
`build/critique.py` sorts each one into what it means to a generator — `actionable`
(a registry move answers it), `placement` (the declared record would have satisfied the need
and the engine did not; lever: prove-it, search-harder, the conflict set), `critic_suspect`
(the failing test reads one of the **35 numeric literals** `elevation._derive_measurements`
states as its own constants, or one of 4 literal ratios — `build/critic_suspects.py`,
ratcheted by `check_critic_suspects.py`), `architect`, `advisory`. **WP-9.2 is the loop**:
`moves/registry.json` (21 moves, 9 stated refusals, every `basis` a sentence really in the
record it names, held to the code by `build/check_moves.py`) and `build/revise.py`, which
accepts a round only on a strict lexicographic improvement of `[fatal, serious, minor,
faults present]`, rolls a refused round back byte-identically, marks the pair tabu and
CONTINUES, asks for the proof before any declared move where CP-SAT is importable, and writes
`revision_report` (plan schema 0.4.0) naming every move, its basis and every refusal.
`compose.repair` — which parsed prose, skipped any room needing more than 1.8x its width,
double-moved a pantry from a stale list and **accepted the worse result on a non-improving
round** — is a wrapper over the declared loop now; the placed loop runs on the returned
candidates. Measured on the search engine over 21 partis and both shipped plans, 6 rounds:
worst-key movement of the order of `[14, 101, 70, 20] -> [13, 78, 81, 20]`, and
`widen-for-furniture` refused 84 of its 182 applications by re-placement noise — the
refused-round rate is the search engine's, not the loop's; under CP-SAT on Tidewater it is 1
in 12. Reports: `docs/reports/wp-9.1-the-critique.md` and
`docs/reports/wp-9.2-the-corrective-revisions.md`; `docs/revise.md` is the layer doc.
**WP-9.3 put both on the bench** — `POST /api/plan/critique`, `POST /api/plan/revise` as a job
with a `round` event per round, the Plan Workbench's critique and two revise chips (the search
and the proof, honest about cost), a Revision panel that says the sheet is a FRESH solve of the
revised record and names the engine the loop's key was measured on, and class and engine tags on
every finding row — **and found three things the first two packages had shipped**: the loop
reported only two of its four round-logging paths (a plan whose only round was a refused proof
emitted no round at all), the `revised` compose event had been dropped on the floor by the app
since the day it was added, and `test_mcp_http.py`'s metered-tool pin was red wherever the MCP
SDK exists and green here only because the file skips without it. Report:
`docs/reports/wp-9.3-the-revision-surfaces.md`.
**WP-9.4 audited the three and is the one to read first before trusting anything this phase
built** — `docs/reports/wp-9.4-the-things-the-reports-said-were-checked.md`. Three read-only explorers built the
claim-to-guard matrix for every sentence in the three reports; three auditors in isolated
worktrees reverted each fix and watched the suites; every finding was reproduced before it was
fixed. **The worst were things the reports SAID were checked**: the WP-9.2 report said a test
held each move's written paths against its `touches` — none existed, and `add-the-grammar-door`
re-derived openings plan-wide, rewriting **nine authored window counts** on the Tidewater plan
to add one door, the silent overwrite WP-6.2 removed; both new bench routes handed a
caller-supplied parti RECORD straight to geometry (114 bays of half a foot); a revise job could
be submitted with no budget at all against its own docstring; the loop's lever carried its
verdict on the ROUND while every reader read the MOVE, so an accepted proof counted as zero
moves applied and the published refusal rate was wrong; and the literal detector was blind to
five shapes already in `elevation.py` — **35 became 44 and 4 became 7**, re-baselined upward once,
in public. **And the audit's own CP-SAT measurement found a sixth**: a round whose proof timed out
reported the DECLARED key — no drawn findings, so lower — and the loop accepted a state with no
placement at all; unjudged is not an improvement now, and a placed loop whose first placement
cannot be judged stops before its first round and says so. Nine tests could not fail, each
proved by mutation. The sweep re-measured: fatal
135 -> 93, serious 961 -> 750, 131 of 273 refused (48.0%), still 0 worse. **A second pass then audited the audit** (report §VIII): three auditors over the whole session's diff found WP-9.4's own diff guard blind four ways (a list whose length changed, a rewrite inside an appended list, two rooms sharing an id, a dict added whole), `split-per-grouping` still re-deriving plan-wide under it, a revised plan whose DXF round trip failed the plan schema, the MCP tools passing every knob raw onto a threadpool token, and one compose submission able to hold the one-worker pool for four hours. All fixed with tests that bite; the deferred items and the reasons are listed in §VIII.

**Next, in order:**
1. **WP-4.4** is **environment-blocked**, not deferred — the proxy answers 403 to CONNECT for
   www.loc.gov. `build/harvest_habs.py` is written, dry-run exercised and queued against the day
   the network opens; its own status block in `PLAN-OF-ACTION.md` carries the verbatim denial. The
   network-free next step it named — giving the asset records their `provenance.building` names,
   without which every harvest query degrades to a style-name search — **is done**:
   `build/name_asset_buildings.py` deals each node's records round its own `exemplars` and 786 of
   1850 name a building, across 305 queries of which 180 are inside HABS's charter. A dry run now
   assigns zero. What is left offline is **72 records on 18 exemplar-less higher-rank nodes**, and
   that needs sources or a ruling rather than a pass. **The 322 in this sentence was stale for two
   days** and so were 845, 330 and 188 in four other files; `check_counts.py` computes all four
   now. Then Phase 5.

WP-2.3 closed Phase 2 on 25 Aug 2026: `build/geometry_cp.py` states placement to CP-SAT, enforces
room minimums instead of scoring them, and returns a named conflict set when a brief cannot be
housed. Read `docs/reports/wp-2.3-the-real-solver.md` before touching geometry — the exact-tiling
formulation the plan of action named does not work (CP-SAT could not decide it in 240 s while
holding a valid solution), and the solver reads the slicing tree off a heuristic layout instead.
`build/geometry.py` remains the default engine everywhere.

## Traps worth knowing before you hit them

- **THE DRAWING WAS THE SEVENTH LAYER, AND IT TOOK FOUR PACKAGES TO FIND (WP-11.14).**
  WP-11.9 taught six layers below the placer about massing elements; `render_plan.py` and
  `derive.js` were not among them, and drew every exterior opening at `0`/`W`/`H` — the
  FOOTPRINT's edges. On the hand-tagged Tidewater: **2 exterior doors drawn in open space** (by
  12.00 and 8.98 ft) and **5 windows standing on their own element's face dropped as
  "off-footprint"**. Fixed on both sides: `_boundary_wall` / `boundaryWall` take the room's own
  element box from `elements.bounds_index` — **the same reader `openings.py` has used since
  WP-11.9**, so the placer and the drawing answer "which of this room's walls are exterior" with
  one function — and every exterior entry carries `edge_ft`, the coordinate ACROSS the wall.
  Doors 2 → 0, windows drawn 7 → 11. **Found by rendering the sheet and looking at it**, which is
  now seven packages running.
- **`at_ft` MEANT TWO THINGS, WHICH IS WHY THERE WAS NOWHERE TO PUT THE ANSWER (WP-11.14).** On
  an INTERIOR entry `at_ft` is the coordinate ACROSS the wall; on an EXTERIOR entry it is the
  position ALONG it. One key, two meanings, in one returned structure — so the exterior entry had
  no field for the perpendicular and the drawing fell back to the footprint. `edge_ft` is that
  field. **Its fallback is the ROOM's own face and never the footprint's**, which is the whole
  reason the fix is the IDENTITY on a one-rectangle house: all sixteen shipped sheets hash
  `4cfba3a0885ddccb` across it. The interior branch three lines above had been right all along.
- **THE 16 REFUSED WINDOWS WERE 5 DEFECTS AND 11 CORRECT REFUSALS, AND THE SPLIT IS THE
  DELIVERABLE (WP-11.14).** `windows_off_footprint` counts a window whose room the placement put
  inland, which is a real and wanted refusal. Publishing 16 as the defect would have been a
  number three times its true size, in the flattering direction for the fix. Measure which
  refusals stand on the room's OWN element face before calling any of them wrong.
- **THE FROZEN FIXTURE WAS NEVER THE OBSTACLE, AND `--expected-only` IS THE TOOL (WP-11.14).**
  WP-11.13 refused this work because changing `derive_openings`' output shape needs
  `tests/fixtures/sheet_symbols/`'s `expected` rewritten, and regenerating re-solves on `auto` —
  the README measures **825 insertions and 804 deletions on the pristine tree with no code change
  at all**. But `freeze()` re-solves only to obtain the ROOMS; `expected` is derived FROM them
  and the rooms are already committed as contract INPUT. `generate.py --expected-only` re-derives
  `expected` with no solver: **verified as a byte-for-byte NO-OP against the pristine renderer
  before it was used**, and it produced **39 insertions, 0 deletions** for this package. Any
  later package changing a renderer's output shape has this now; do not reach for the full
  regeneration.
- **A MUTATION FOUND THE ONE GUARD THAT MATTERED MISSING, AND THEN FOUND THE REPLACEMENT BLIND
  TOO (WP-11.14).** Six mutations; five bit at once. The sixth — *the drawing ignores `edge_ft`*,
  the single line that put the doors in mid-air — passed every test in the file, because every
  assertion read `derive_openings`' OUTPUT and none read the DRAWING. That is WP-11.10's finding
  one package later in the same file. The replacement (render twice, once with `edge_ft`
  stripped, require the plates to differ) **stripped `exterior` and `windows` at once**, so a
  mutation to the door path alone still moved the plate via the windows: it strips ONE KEY AT A
  TIME now. **And the code was really wrong in the way the mutation exposed** — `_frame` read
  `d["edge_ft"]` while `_door` read a local, so reverting either still moved the other. One
  opening has one face; computing the edge once and handing it to both is what makes the guard
  able to fail.
- **AND A THIRD GUARD PINNED A LITERAL SIGNATURE, IN TWO PACKAGES RUNNING (WP-11.14).**
  `test_both_renderers_read_the_record_and_derive_nothing` asserted
  `"def derive_openings(rooms, W, H, tol=0.6, appendages=None):"` verbatim and its JS twin the
  same way, so adding an argument AFTER `appendages` broke a guard about appendages with a change
  about massing elements. Its own comment already said the property -- *"in the same argument
  position"* -- so it reads the PARAMETER ORDER now (`inspect.signature`, and a regex over the JS
  parameter list), mutation-checked by swapping the last two. With WP-11.13's source grep for
  `">= int(COVERAGE * _eW * _eH)"` that is two in two packages, and the failure modes differ:
  a stale SELECTOR goes quietly blind and a pinned LITERAL fails loudly on an unrelated change.
  The second wastes a reader's afternoon; the first lies. Neither is the property.
- **THE FROZEN FIXTURES CANNOT HOLD A MULTI-ELEMENT CASE, AND BOTH SIDES SAY SO (WP-11.14).** No
  plan in the corpus carries a `block` tag, so every fixture has one element and
  `tests/fixtures/sheet_symbols/` can hold the two renderers to one answer only on the case where
  the defect does not appear. `tests/test_exterior_faces.py` and
  `workbench/app/src/derive.test.mjs` assert the same three numbers on the same two hand-built
  rectangles instead, on WP-11.10's stated precedent. A guard that runs only where the bug cannot
  occur is not a guard.

- **AN EXTERIOR DOOR IS DRAWN ON THE FOOTPRINT'S WALL AND NOT ITS ROOM'S, AND THAT IS A SEVENTH
  LAYER (WP-11.13).** `render_plan.render()` has
  `px, py = (p_, 0.0 if wl == "S" else H) if horiz else (0.0 if wl == "W" else W, p_)` — `W` and
  `H` being the FOOTPRINT's — and `_frame` twenty lines above carries the same two expressions,
  which is why the sill and the glazing float with the leaf. `derive.js` has it too and its own
  docstring states it as intended: *"exterior doors as openings on the footprint edge."* On the
  proved hand-tagged Tidewater that draws **two doors in open space north of the whole building**
  — `backhall` at 42.0 ft against its own face at 30.0, `kitchen` at 42.0 against 33.02. The
  record is right and `openings.place` seated both on their own element's boundary; the drawing
  throws it away, and **the INTERIOR branch three lines up is already correct** and is the model.
  On a one-rectangle house the two lines coincide, so nothing shipped moves.
  `oq/an-exterior-door-is-drawn-on-the-footprints-wall-and-not-its-rooms`. **Found by rendering
  the sheet and looking at it — six packages running.** Not fixed in WP-11.13 because the honest
  form adds a key to `derive_openings`' output in BOTH spellings and
  `tests/fixtures/sheet_symbols/` holds them to one contract against a fixture its own generator
  re-solves on `auto`.
- **AN ELEMENT'S BOX WAS SIZED TO EXACTLY ITS ROOMS AND THEN ROUNDED INWARD, SO IT COULD NOT
  HOLD THEM (WP-11.13).** `dependency_sizes` set `H = need / W` — zero slack by construction —
  and `geometry_cp._element_boxes` then `ceil`s the low edge and `floor`s the high one, which is
  WP-11.11's deliberate ruling so nothing CP proves sits outside the stated mass. `blocks_for`
  centres a dependency on the main block's axis, so its origin is a half-foot and BOTH roundings
  bite. Measured on the hand-tagged Tidewater against a floor of 0.97: **dependency 690 sf of box
  for 701 sf of rooms (1.016), hyphen 105 for 112 (1.067)** — the rooms could not fit AT ALL, at
  any floor. `grid_allowance_ft()` is two quanta per axis, one per inward-rounded edge, DERIVED by
  solving `(W − 2g)(H − 2g) ≥ need` rather than chosen. **The hyphen takes it in DEPTH only**: its
  width is the gap between two masses, a real dimension of the house, and its origin is integral.
- **AND THE COVERAGE FLOOR ROUNDED THE SAME BOX A SECOND WAY (WP-11.13).** The floor computed the
  element's box with `int(round(...))` while containment used `_element_boxes` — one quantity,
  two roundings, so the model demanded 97% of the LARGER be packed inside the SMALLER. On the
  hyphen that is **108.6 sf into a box holding 105: infeasible by construction**, before a single
  declared fact was read, which is exactly why every tagging of that record came back with
  *"the rooms cannot tile any footprint this parti and lot allow, even with every declared
  requirement dropped"*. The engine was right and it was answering a question about arithmetic.
  `elements.integer_box` is the one spelling now, in the leaf both the model and the disclosure
  load. **A conflict core that blames the tiling is the shape this defect makes** — read it as an
  instrument reading before reading it as a fact about the brief.
- **WHAT A COVERAGE FLOOR IS STATED AGAINST DEPENDS ON HOW THE BOX WAS DERIVED (WP-11.13).** The
  main block's box is grown independently by `derive_footprint` until the programme fits, so
  "fill 97% of your box" is a real question about the rooms. A dependency's box is derived FROM
  its rooms, so asking whether they fill it is asking the box about itself — and **the quantised
  answer cannot be made to land: the floor needs the box within 3% of the rooms' area and one
  foot of a 30 ft dependency is 5%.** For a non-main element the floor is stated against the
  rooms' OWN DECLARED AREA, which is the guarantee it was for (rooms may not shrink and leave the
  element half empty) in a form the grid cannot falsify. **`COVERAGE` is unchanged at 0.97**, and
  the question that asked whether 0.97 was the right number for a dependency was aimed one layer
  above the cause.
- **THE CORPUS SAID WHERE THE BUTLER'S PANTRY GOES A FORTNIGHT BEFORE ANYONE TAGGED IT
  (WP-11.13).** WP-11.11 tagged it into the dependency and CP refused; **the refusal was right
  and the tagging was wrong.** `rooms/butlers-pantry.json`'s `must_adjoin kitchen` has carried
  `via: [back-hall, gallery-corridor]` since OQ 59 (24 Aug) with a note saying that in *"a
  Tidewater plantation house … the pantry is in the block and the kitchen is in another
  building"*. **The two crossings are not equivalent and that decides it**: `must_adjoin
  dining-room` is hard with NO `via`, so a pantry in the dependency must cross and cannot;
  `must_adjoin kitchen` is hard WITH one, and the plan already carries `butlers → backhall →
  kitchen` in full. The ladder is the deliverable — butlers in the dependency cores on the dining
  door, butlers in the block cores on the kitchen door, that redundant door dropped proves
  **OPTIMAL in 12.3 s with zero pins downgraded**. **The shipped record is still NOT tagged**:
  that is a record edit moving a shipped placement, and a package doing two things can only be
  reasoned about as one. `oq/the-parti-dissolved-its-own-dependencies`.
- **WP-11.11's "2 OF 16 CROSSING PAIRS" IS 1, AND THE FIRST INSTRUMENT HERE REPRODUCED THE VERY
  DEFECT IT WAS AUDITING (WP-11.13).** The second pair was `breakfast ↔ terrace`, and a terrace
  takes no rectangle (WP-11.10), so it stands in NO element and cannot cross a boundary. The
  sweep written to check this read *no element* as *the main block* — WP-11.9's own rule, broken
  inside the package auditing WP-11.11 — and was corrected by filtering on
  `stacking.takes_a_rectangle`, the way every other reader does, before the number was believed.
- **`capacity_report` REPORTED UNJUDGED AS PASSED TWICE BEFORE IT WAS RIGHT, IN A PACKAGE ABOUT
  DISCLOSURE (WP-11.13).** It returned `fits: true` on an EMPTY SUM — and that was not
  hypothetical: `footprint.blocks` on a placed record carries no room list, so the disclosure's
  first run called every element `rooms: 0, fits: true`. Membership is the geometric join
  (`elements.element_of`) now and an element with no members is `null`. And it judged the MAIN
  BLOCK on the integer grid, convicting it on every heuristic placement — `_snap_fpd` makes the
  footprint integral before any element is built, so a grid figure from an unsnapped record
  describes a box CP never uses. **Both were found by running it, not by reading it.**
- **A GUARD CAN GO RED ON THE RIGHT EDIT, WHICH IS THE SELECTOR FAULT WEARING THE OTHER SIGN
  (WP-11.13).** `test_the_coverage_floor_is_per_element` asserted the literal source string
  `">= int(COVERAGE * _eW * _eH)"` — the very expression carrying the second rounding — so it
  broke on the fix to the defect it was guarding. A guard that reads a selector rather than a
  property can neither survive a rewording nor tell a fix from a regression. Two more in the same
  package pinned a dependency's exact DEPTH as a proxy for the pile rule and for an unplaced
  terrace's area; all three are re-cut against the property they name, none bumped.
- **A MUTATION CAN BITE ONE GUARD AND NOT THE OTHER, AND THE WEAKER ONE MUST SAY SO
  (WP-11.13).** Deleting the depth term from `dependency_sizes` leaves the WIDTH half of the
  allowance in place, and on the tagged Tidewater the actual rounding then loses less than the
  worst case — so the per-plan row still fits and only the arithmetic test
  (`(W − g)(H − g) ≥ need`, the guarantee) goes red. One asserts the guarantee and one asserts
  one plan's luck; both are kept because they fail on different mutations, and the test file
  names which is which so a green row is not read as the arithmetic being proved.

- **THE SEARCH CHARGED A SPAN FOR TWO PHASES AND THE CRITIC HAD NO FINDING FOR IT (WP-11.12).**
  `structure.span_check` has measured the clear span between bearing lines since WP-3.1 and
  `geometry` has CHARGED it since WP-7.4 (`SPAN_W = 20`, mirrored soft in CP) — and `plan_check`
  emitted nothing, so a **60 ft clear run with no bearing line in it** on the Tidewater upper
  floor, against the 20 ft its framing tradition states, got a clean verdict from the validator
  the bench shows, the fidelity score the composer ranks on, the critique and every
  `revision_report`. A quantity a SCORE knows about and a CHECKER does not is invisible in
  exactly the surfaces a person reads. **The finding READS `geometry_report.span_capacity.marks`
  and does not recompute**: these are the spans `SPAN_W` charged, and a second computation could
  convict a placement on numbers it was not chosen by. *Serious rather than fatal* on the
  corpus's own words — `span_check`'s note asks for an intermediate support or an engineered
  member, which is a floor framed differently, not a plan that cannot be walked. Corpus serious
  **685 → 708**, exactly the 23 spans over 13 plans; placement and openings byte-identical.
- **EVERY SPAN COUNT IN THIS CORPUS IS A FLOOR, AND THE COUNT SAYS SO IN FOUR PLACES (WP-11.12).**
  `span_check` reads each wall's `position_ft` and never the `lo_ft`/`hi_ft` extent `wall_lines`
  computes beside it, so a bearing line is credited across the whole plate however short the wall
  runs — the Tidewater upper y-wall at 30.0 runs **20 of the 60 ft** it is credited across. That
  is OQ 98's measurement half, HALF CLOSED and still wanting the ruling it asks for. Publishing
  the reporting half without the caveat would be the OQ 52 family in a new place, so
  `span_capacity.understated` is on the record, inside every finding's own statement, and on both
  plates. **And both plates print the ZERO too**, because *"no span exceeds capacity"* is exactly
  the claim the understatement can make falsely.
- **A `placement` CLASS THAT STRETCHES ITS OWN DEFINITION, SAID IN THE CODE (WP-11.12).**
  `critique._is_placement`'s other five kinds are each decided against something the record
  DECLARES — a door, a stack, a size, a passage width. **A plan record states no wall positions
  at all**, so a clear span has nothing declared to disagree with; it is classed on the other
  half of the definition, that an engine setting really does change it (WP-11.8 roughly doubled
  the count by making rooms squarer, because the only way this slicer creates a bearing line is
  to cut on one), and under CP-SAT `_lever` then honestly says there is no setting left. No move
  answers a span: a move edits the record and cannot ask for a cut.
- **AN UNLABELLED `auto` FIGURE COSTS TWO NUMBERS AND SITS BESIDE A THIRD THAT IS RIGHT
  (WP-11.12).** WP-11.8 published *"over-capacity clear spans 13 → 25 and the worst 40.0 →
  60.0 ft"*. Re-derived on `git archive` checkouts of the commit before it and of it, the
  deterministic pair is **11 → 23** and the worst-span pair was right; `auto` gives 28 on one run
  of the current tree. This file's own standing rule is RATCHET THE DETERMINISTIC FIGURES ONLY,
  and the correction is written beside the original with the engines named rather than into
  WP-11.8's report, which is left as written.
- **A CALL-SITE COUNT THAT READS TEXT COUNTS DOCSTRINGS (WP-11.12).** The guard holding
  `span_check` to one call site in the tree — the point of the one-arithmetic-two-adapters split
  — first counted the string and found three, two of them PROSE in `render_section.py`'s
  docstrings describing what the function does. It walks the AST for real `Call` nodes now. The
  same class as *"a guard that reads a selector rather than a property"*, one layer down: read
  the structure, not the characters.
- **AN ASSERTION CAN STATE A FALSE REASON AND STILL PASS, AND ITS OWN FIRST RUN CAUGHT THIS ONE
  (WP-11.12).** A new test said `plan_check` cannot load `structure.py`; it can and does, lazily
  and inside a try, in the elevation block at the foot of the file, and has since WP-3.2 — and
  the comment in `plan_check` said the same. The reasons the finding reads the record are that
  there is one spelling of the arithmetic and that these are the spans the search was chosen by;
  both are better than the false one. **A test that passes for a reason that is not true teaches
  the next reader the untrue thing.**

- **THE PROVER PLACES A SECOND MASSING ELEMENT NOW, AND THE GUARANTEE IS THE MODEL RATHER THAN
  THE PLACEMENT (WP-11.11).** `geometry_cp` built every room as `x = NewIntVar(0, Wi)` and
  REFUSED a tagged plan; `_element_boxes` is the one reader now and eight statements the model
  made about "the block" are made about the room's own element (containment, the coverage floor,
  a declared exterior wall, a spanning room's through-axis, an exterior door reaching the
  envelope, the bay grid, the span capacity, `_absorb`'s four growth limits). **CP under a
  wall-clock budget is not reproducible, so pinning what it FINDS would pin the machine** — what
  is pinned is what it is ASKED: four `CpModel` proto hashes for both shipped plans in both
  phases, byte-identical across the package (`tests/test_cp_elements.py`). Three guards exist
  only to keep them and each is a CONDITION rather than a branch: `gx0 < ex`,
  `len(els.get(lvl) or []) > 1`, `if base:`.
- **`test_no_new_by_path_loader_outside_modcache` HAS NOW CAUGHT TWO PACKAGES RUNNING, BOTH IN
  THE FULL SUITE (WP-11.10, WP-11.11).** A local `spec_from_file_location` in `appendages.py`'s
  `main()`, and another in `geometry_cp.py`'s new selftest fixture. Each surfaced fifty minutes
  in, and in neither case did a checker, the package's own test file or the app suite notice.
  This file's *"do not reinstate a local loader"* has a test behind it and the test is the only
  thing that reads it. **Run `check_all` whole, not the parts you think you touched.**
- **THE GUARD WRITTEN FOR BYTE-IDENTITY CREATED THE DEFECT IT WAS GUARDING AGAINST (WP-11.11).**
  The containment lower bound first read `if ex:` — *"on a one-rectangle house `ex` is 0 and
  `x >= 0` is already the domain"* — true of the OLD domain and false of the new one, because
  `gx0` is the leftmost element's edge and a west dependency puts it at −34. Every MAIN-BLOCK
  room then had a domain reaching 34 ft west of the house and nothing holding it back: **five
  untagged rooms placed or absorbed in no element at all.** `gx0 < ex` is the honest test.
  **Caught by a probe running `elements.element_of` over every placed room** — not by a test and
  not by reading.
- **AND A MEASUREMENT TAKEN ON THE MODEL WITH THAT BUG REPORTED A PROOF THAT DID NOT EXIST
  (WP-11.11).** The affordability spike reported a tagging as **"SOLVED, OPTIMAL in 13.5 s"** and
  that number was one edit from being the package's headline; it was rooms roaming into negative
  x. With containment enforced the same plan is INFEASIBLE in 1.6 s. *An instrument that cannot
  fail is worse than a test that cannot fail* — and this one produced the FLATTERING number,
  which is the direction that gets published.
- **`_absorb` UNDID A PROOF FOR THE FOURTH TIME (WP-11.11).** CP proved the breakfast room at
  y ≥ 4.95, the west dependency's own south edge; the absorb pass grew it to y = 1.6 — 3.35 ft of
  drawn floor outside the mass it belongs to, in a record that looks exactly like a solved plan.
  It takes `bounds` now beside `caps`, `keepout` and `ratios`, which are the other three. Anything
  that runs AFTER a solve is outside its proof and has to be held to it separately.
- **THE SEARCH REWARDS A TAGGING THE PROVER REFUSES, AND ONE DOOR DECIDES IT (WP-11.11).** On the
  hand-tagged `tidewater-georgian-careful`, `engine="heuristic"` reports an IMPROVEMENT (fatal
  8 → 6, serious 61 → 53) and `engine="cp"` proves it INFEASIBLE in 1.5 s with a minimized core
  of one door — *"Dining Room and Butler's Pantry share a door"*. **That count was published as
  2 of the 16 ground-floor door pairs and it is 1** (corrected by WP-11.13): the second pair was
  `breakfast ↔ terrace`, and a terrace takes no rectangle (WP-11.10) so it stands in no element
  and cannot cross a boundary — the instrument had read *no element* as *the main block*, which
  is the defect the whole of WP-11.9 exists to remove. **And the one real crossing was the
  TAGGING's fault rather than the record's**: `rooms/butlers-pantry.json` has said since OQ 59
  (24 Aug) that in *"a Tidewater plantation house … the pantry is in the block and the kitchen is
  in another building"*. Put where its own record says, the core moves to
  `butlers ↔ kitchen` — whose `must_adjoin` carries `via: [back-hall, gallery-corridor]`, a route
  the plan already holds in full — and dropping that redundant direct door proves OPTIMAL. **Every boundary `blocks_for` can draw through this
  record cuts a declared door**, which is `oq/the-parti-dissolved-its-own-dependencies` measured
  for the first time: a finding about the RECORD, not the engine. So the shipped tags are still
  not authored, and the reason has changed from *the prover cannot look* to *the prover says no*.
  **At the shipped `COVERAGE = 0.97` a second, independent reason binds first** — per-element
  coverage on boxes `dependency_sizes` sizes to exactly their rooms' areas is an exact cover, and
  the core is the tiling rather than the door; below 0.97 the door surfaces.
  `oq/the-coverage-floor-is-an-exact-cover-per-element`. Quote both, and never lower the floor to
  make a refusal go away.
- **TWO SOFT TERMS COULD HAVE DECIDED A PLAN CANNOT BE BUILT (WP-11.11).** `AddModuloEquality`
  truncates toward zero, so the bay-snap term's `[0, bay-1]` remainder domain is INFEASIBLE on a
  negative edge — a scoring preference silently refusing a house. The edge is shifted by whole
  bays first, so the grid's own phase is untouched. And the span-capacity term drew grid lines
  across the gap between two detached elements, which is WP-11.9's `structure.wall_lines` defect
  arriving in the objective. Both found by running, not by reading.
- **A PACKAGE'S OWN GATE CAN BE A CONSEQUENCE OF A READING NOBODY RE-EXAMINED (WP-11.10).**
  `PLAN-OF-ACTION.md` gated the terrace on
  `oq/the-proving-engine-cannot-place-a-second-massing-element` because the plan file called an
  at-grade appendage *"a third massing role"*. The CP refusal keys on the room's `block` TAG
  (`geometry.py:2399`, `is_block_tag`), not on `footprint.blocks`, so a pass that writes no tag
  never reaches it. **Ruled 7 Sep 2026: an at-grade unroofed appendage is NOT a massing element**
  — it is a plan-level record on `plan.threshold`'s precedent, the question stays open and still
  gates the dependency tags, and the gate cost nothing because it was read before it was obeyed.
- **THE ROOM KEEPS NO `geometry`, AND THAT IS THE WHOLE MECHANISM (WP-11.10).** `build/
  appendages.py` places the terrace OUTSIDE the block and writes the rectangle to
  `plan.appendages`, never to the room. Three filters already in the tree then stay blind BY
  CONSTRUCTION — `structure.wall_lines` filters `r.get("geometry")`, `plan_check`'s
  `rooms_unplaced` filters `takes_a_rectangle`, `geometry._record_prep` filters `is_placed` — so
  WP-11.9's six taught layers are not reopened for one rectangle. **Writing the rectangle onto the
  room would be invisible: the drawing would look identical**, and a test mutating it red is the
  only thing that catches it. The stated cost is that the drawn rectangle is held against no band:
  `oq/an-at-grade-appendage-is-drawn-and-not-judged`.
- **THE DOOR WAS SEATED AND THE SHEET SAID IT COULD NOT BE DRAWN (WP-11.10).** With the terrace
  placed and the door in the record carrying a wall, a position and a hinge, BOTH plates went on
  printing it under *"N DECLARED DOOR(S) WITHOUT A DRAWABLE OPENING"* — `good-02`'s schedule named
  `FAMILY–TERRACE` outright. `render_plan.derive_openings` builds `idx` from rooms carrying
  `geometry`, and an appendage's room deliberately carries none, so the lookup missed and fell into
  *"the other room is not placed on this level"*. **The record said seated and the drawing said
  undrawable** — WP-6.1's own finding, arriving through the door this package had just opened. Both
  spellings take an `appendages` argument now (`derive_openings` and `derive.js::doors`, same
  position), and the plates read 14 → 13 and 6 → 5. **Guarded by a HAND-BUILT pair in each language
  rather than through `tests/fixtures/sheet_symbols/`**, because that fixture's generator re-solves
  on `auto` (its own README) and regenerating it for this branch is eight hundred lines of solver
  noise round two rectangles. **And the first guard could not fail**: a test reading
  `derive_openings` directly stayed green with `render()`'s call site reverted, so it reads the
  rendered plate's schedule instead — the number a person actually sees. **Nothing in the suite
  could have caught it and looking at the sheet did**; that is six packages running.
- **THE PASS RUNS FIRST, BECAUSE `_place_interior` DOES (WP-11.10).** `entrance_pass` (WP-11.4)
  runs LAST because it reads placed doors; the appendage pass runs BEFORE the level loop because
  `_place_interior` is the first pass inside it and an appendage derived afterwards could never
  seat the door it exists for. Two at-grade passes, opposite ends of `place()`, for opposite
  reasons. `_rect` is deliberately unchanged and the rectangle is threaded into that ONE reader on
  WP-11.9's `bounds=` precedent — six other call sites must go on seeing a terrace as unplaced.
- **`exterior_walls` MEANS TWO DIFFERENT THINGS ON AN OUTDOOR ROOM, AND THE FIGURE IS THE
  INTERSECTION (WP-11.10).** `tidewater-georgian-careful`'s terrace declares E, N and S, which can
  only be *the free faces* — a rectangle cannot be attached on three sides. `good-02`, `good-04`
  and `good-07` each declare exactly one, which reads as *the side of the house it is on*.
  **Neither reading resolves the six records on its own**: the free-face reading turns one declared
  wall into three candidates and the side-of-the-house reading turns three into three. Both admit
  `w` exactly when `w` is declared and `OPPOSITE(w)` is not, and that one line is what is taken —
  WP-11.4's *"three statements of one depth, the figure is the intersection and never an average"*
  one layer up. Intersected then with the faces the placement put outside (`elements.
  boundary_walls`); unique, or UNJUDGED. **4 placed, 2 refused by name and neither patched.**
- **ONE FATAL CLEARED, TWENTY-SEVEN CREATED, AND THE 27 WERE ALREADY TRUE (WP-11.10).** Seeding the
  reachability walk's `outside` from a placed, at-grade, unroofed appendage clears
  `drawn:breakfast` on the Tidewater plan (its own `unreachable` count 9 → 8) and turns **three
  COULD-NOT-EVALUATE verdicts into 27 `unreachable` fatals** — `good-02` 7, `good-04` 10,
  `good-07` 10 — because **those three plans have NO placed exterior door at all** and the walk had
  nowhere to start. Their whole report of that was one `info` line. fatal 136 → **162**, serious
  681 → 685, info 167 → 164, refused doors 243 → 236: **27 created against 1 cleared, which is the
  net +26**, and both halves are quoted because the net alone hides which way either went.
  **Read it as three plans becoming judgeable, not as 27 new defects**; and because ten fatals with
  one cause is a report a reader has to reconstruct, the cause gets its own finding beside them
  (`outside-is-only-an-appendage`), on those three plans and not on the Tidewater plan, which has a
  front door as well.
- **THE TIDEWATER FATAL HAS TWO CAUSES AND THE TERRACE IS ONE (WP-11.10).** `breakfast` declares
  two doors and both were refused: the kitchen one for want of a shared wall (the placer's, at
  x 0–20 against x 47.5–60, untouched here) and the terrace one because the terrace had no
  rectangle. **Placing the terrace removes the second reason only.** Any report saying this package
  cleared that fatal by seating a door is wrong; it was cleared by the reachability ruling above.
- **TWO EXISTING GUARDS CAUGHT THIS PACKAGE, BOTH FIFTY MINUTES INTO THE FULL SUITE
  (WP-11.10).** Neither appeared in a checker, in the package's own test file or in the app
  suite. `test_ingest.py::test_provenance_validates_and_gates_method` pins the CURRENT plan
  schema version and **caught the bump a seventh time** — its own comment records the sixth in
  the same words. And `test_modcache.py::test_no_new_by_path_loader_outside_modcache` caught a
  local `spec_from_file_location` inside `build/appendages.py`'s `main()`, which is this file's
  own standing trap with a test behind it; **the `main()` was removed rather than routed through
  `modcache`**, because every other leaf in `build/` carries no CLI at all and the pass's whole
  output is already on the record. **Run `check_all` whole, not the parts you think you touched.**
- **THREE NEW GUARDS COULD NOT FIRE, AND ALL THREE WERE BRANCHES THE CORPUS CANNOT REACH
  (WP-11.10).** The `roofed` refusal (no record says `within_footprint: false` AND `roofed: true`),
  the `no-depth`/`no-run` refusals (every terrace record states both figures) and the run clamp
  (none of the four asks for more run than its face has). Each is a real guard against a record
  this corpus does not yet have, so each got a synthetic fixture proving it bites — deleting them
  would have been the other honest answer and leaving them green is not. **Nineteen mutations were
  run and every one now bites.** A fourth assertion was written wrong and died on its own first
  run: a whole-file check that `render_plan.py` never mentions `exterior_walls`, which it
  legitimately does for the openings it derives — a guard that could only ever be deleted.

- **SIX LAYERS READ THE MAIN BLOCK AS THE WHOLE BUILDING, AND ALL SIX ARE TAUGHT NOW
  (WP-11.9).** `build/elements.py` is the ONE reader of which massing element a room stands in —
  a LEAF, on `stacking.py`'s precedent, because `geometry.py` loads `plan_check.py` and
  `structure.py` loads `geometry.py`, so the six sit on three rungs of one import ladder.
  **Four rulings, taken 5 Sep 2026 before any code**: per-element envelope with the union
  reported beside it; the lot cap on the BUILT EXTENT, elements only, gap excluded; a hyphen is
  an element and abutment is a constraint; `touches` is measured against the room's own element's
  face (*exterior is exterior* — a face across a gap is exterior too and is counted separately as
  `faces_across_a_gap`). Measured on a hand-tagged Tidewater, one layer at a time: outward
  openings on their own element's real faces **18 → 23** and refusals 11 → 6 (five AUTHORED
  windows recovered from *"the placement puts this room on no such boundary wall"*); exterior
  walls **4 → 12** on the ground and **4** upstairs; unsupported upper wall lines **20 → 27** on
  one record with only the instrument changed; built extent **97 → 77 ft**; rooms reaching no
  exterior wall **8 → 1**; one IFC slab per element per storey. **A room in NO element is
  unjudged, never assigned to element zero** — defaulting there is the defect itself.
- **THE GUARANTEE IS BYTE-IDENTITY, AND IT IS HOW THAT PACKAGE IS READ (WP-11.9).** Every plan
  in this corpus is one rectangle, so teaching six layers a new concept must be invisible on all
  sixteen: placement, footprint, openings, fixtures, furniture and the corpus findings are all
  unchanged, hashed on a `git archive HEAD` checkout before and the working tree after.
  `geometry_report` is deliberately NOT hashed — it grew `lot_extent`, which is the disclosure.
  **A package that teaches six layers and moves a shipped placement has done two things and can
  only be reasoned about as one.**
- **A DEFINITION CAN LAND TWICE AND THE SECOND ONE WINS (WP-11.9).** Rewriting
  `multi_element_disclosure` left TWO `def`s in `geometry.py`, new above old, and Python took the
  last: the record went on carrying `not_element_aware: [openings, structure, …]` under a
  docstring explaining all six had been taught, while the edit had unambiguously landed and
  re-reading the function's text showed the new words. This file already says *assert that an
  edit landed and then re-read the file*; the corollary is **assert that it landed ONCE**. A test
  counts the definitions.
- **THE MAIN BLOCK WAS SIZED FOR ROOMS THAT GO IN THE DEPENDENCY (WP-11.9).** `derive_footprint`
  summed EVERY ground room into `need`, so a tagged plan got a full-programme main block AND a
  dependency beside it — 3,106 sf of floor for 2,405 sf of rooms, and a 97 ft extent on a 60 ft
  house. `blocks_for`'s own docstring has always said a dependency is sized from its own rooms
  *"never from a share of the main block's"*; this is that sentence applied to the OTHER side of
  the same rule, and it was missing. `dependency_sizes` is the one spelling both readers take.
- **AN ELEMENT WITH NO ROOMS ON A LEVEL HAS NO WALLS ON THAT LEVEL, AND THE FIRST VERSION DID NOT
  SAY SO (WP-11.9).** Handing every level all three elements gave the UPPER storey a dependency
  envelope with nothing inside it — 12 exterior walls over 0 dependency rooms, phantom structure
  of exactly the kind the package removes, one level up. Caught by reading the counts PER LEVEL
  rather than in total. `export_ifc`'s slab loop takes the same rule.
- **THE ABUTMENT CONSTRAINT IS INERT ON EVERYTHING THE PLACER PRODUCES, AND SAYING SO IS THE
  DELIVERABLE (WP-11.9).** `oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it`
  records a hyphen missing its neighbour by 0.64 ft with both doors unplaced. Tried at five
  hyphen depths on a hand-tagged Tidewater and on a composed `five-part-palladian` with FIVE
  elements: the count is zero every time, and deleting the new ranking term changes no outcome
  anywhere in the tree. `blocks_for` clamps the hyphen's depth to the dependency's
  (`hh = min(H, …)`) and centres all three on one axis, so a shared wall exists by construction.
  It shipped as a **guard against a regression in `blocks_for`**, the test says that in its own
  name, and the detector is proved to bite on a hand-built record — because a term that cannot
  fail is worse than no term.
- **TAGGING THE SHIPPED RECORD IS NOW AN IMPROVEMENT AND IS STILL REFUSED (WP-11.9).** With the
  six layers taught, hand-tagging `tidewater-georgian-careful`'s service rooms as a dependency
  gives fatal **9 → 6**, serious **61 → 53**, relaxations 8 → 6, rooms outside their own band
  **6 → 2** — where WP-10.1 measured the same tags TREBLING the fatals. It is not authored
  because `geometry_cp.py` builds every room as `x = NewIntVar(0, Wi)` and REFUSES a
  multi-element plan, so the tag would trade one of the two plans this corpus PROVES for a
  searched one. That is a precondition, not a cost:
  `oq/the-proving-engine-cannot-place-a-second-massing-element`, and WP-11.10 is gated on it too.
- **THE RENDERERS WERE AHEAD OF THE STRUCTURE LAYER FOR TWO PHASES (WP-11.9).**
  `render_plan.py` has drawn the exterior envelope PER ELEMENT since WP-11.1's poché, one ring
  per element with its index on every band, while `structure.wall_lines` still swept every room
  into one envelope and `plan_check` convicted a dependency room of reaching no exterior wall.
  The drawing, the structure layer and the critic each held a different answer about one wall.
- **AND THE THIRD INSTANCE OF THE SAME DEFECT WAS FOUND BY LOOKING AT THE SHEET (WP-11.9).**
  `structure.build_section` and `export_ifc` were both given "an element with no rooms on this
  level has no walls on this level", each caught by reading a COUNT. The renderer had it too and
  publishes no counts: the tagged sheet's UPPER plate carried a **30 ft poché rectangle enclosing
  nothing**, an envelope around no rooms, which says the house has a storey it does not have. It
  was invisible to 1,675 tests and obvious in one screenshot. All sixteen shipped sheets hash
  byte-identical across the fix. **Render the sheet and open it** — that is now five packages
  running where it found something nothing else did.
- **THE SEARCH RANKS THE BAND ABOVE ITS OWN SCORE, BECAUSE IT CANNOT REFUSE TO PLACE (WP-11.8).**
  `SHAPE_W = 6.0` charged a room drawn past its own proportion ceiling and a candidate won while
  paying it — the flat-12 width charge in a second place. Measured: **77 of 219 placed rooms, 35%,
  drawn outside their own band** on the search, worst a dining room at 5.0:1 against a ceiling of
  1.8. **Rejection was never available and that was measured before it was written**: over 250
  slicings of the Tidewater ground floor the distribution of out-of-band rooms runs 3 to 10 and
  **ZERO conform**, so "hard" in an engine with no conflict set means the band is the FIRST KEY of
  the acceptance and the score the second. Corpus-wide 77 → **30**, serious 745 → 681, minor
  1031 → 992, and rooms under their own AREA floor 15 → **13**. **The span-charge prune had to be
  tiered with it** — `if part >= best["_raw"]: continue` across violation tiers would skip a
  candidate with fewer rooms out of band for scoring worse, and the first key would not be a key.
- **AND THE KEY HAD TO COUNT THE BAND IN BOTH DIRECTIONS, WHICH A WP-7.4 GUARD FORCED (WP-11.8).**
  Shipped as the proportion CEILING alone it took under-band rooms **15 → 21** and put
  `spec-builder-colonial`'s dining room back at 87 sf against a 122 sf floor — undoing WP-7.4,
  and caught by the assertion WP-7.4 had left behind saying in as many words *"the dining room is
  under band again … something has undone that"*. **A ranking that honours one band by breaking
  the other is not the room's own record winning; it is one term winning.** Counting both
  (`band_violations` + `under_band`, the same reader the report uses) costs two rooms over their
  ceiling and about 7% of the search's wall clock, and buys eight under their floor — better than
  the BASELINE as well as the intermediate. The intermediate is kept in the code comment because
  it is a correct measurement of a wrong key, and anyone deleting the area half reproduces it.
- **AND THE SAME GEOMETRY HAS A STRUCTURAL PRICE NO CRITIC LAYER REPORTS (WP-11.8).**
  Over-capacity clear spans **11 → 23 and the worst 40.0 → 60.0 ft**; relaxations 64 → 86.
  (**The pair published at the time was "13 → 25" and it was an unlabelled `auto` reading.**
  Re-derived by WP-11.12 on `git archive` checkouts of the commit before WP-11.8 and of WP-11.8
  itself, `engine="heuristic"`, the deterministic pair is 11 → 23; `auto` gave 28 on one run.
  The worst-span pair is right. This file's own rule is RATCHET THE DETERMINISTIC FIGURES ONLY,
  and this is what an unlabelled one costs.) A
  squarer room puts fewer cuts on the bay module, and **the only way this slicer creates a bearing
  line is to cut on it** — which is WP-7.4's own mechanism running backwards (its span term pulled
  cuts ONTO the grid and took relaxations 9 → 7). The 20 ft capacity and `bearing_lines`' 0.75 ft
  tolerance are UNTOUCHED, which this file forbids moving. **`plan_check` has no span finding at
  all**, so none of these twelve reaches a sheet or a critique — OQ 98 — and the cost is disclosed
  in WP-11.8's report and nowhere else. Recorded as a real argument against the ranking rather
  than netted off against what it buys.
- **THE COST IS SIXTEEN FATALS AND THE MOVE REGISTRY IS WHAT SETTLED IT (WP-11.8).** fatal
  113 → 136, and **every one of the twenty-three is `unreachable`** — adjacency (38) and fault (17)
  fatals do not move. A squarer room shares less wall, so its declared doors lose their run. **A
  door-seating count was built and ranked FIRST to protect the more serious fact, and measured
  worse on every axis at once**: 68 out of band, 131 fatal, 780 serious — because it is a PROXY
  for the drawn layer's rule (which seats openings through `openings.place`, reading walls and
  obstructions) and not the rule. Optimising a proxy optimises the proxy; it was deleted rather
  than reported, so nothing reads it as the drawn layer's own number. **What settled the trade is
  what the corpus can DO with each defect**: all 81 `unreachable` fatals carry `adjacent_placed`
  (re-derived after the key changed, not carried over), so `critique._intended_move` answers every
  one with `add-the-grammar-door` and the revision loop runs by default, while
  `drawn-proportion-above-band` returns None — no move exists. 49 defects nothing can fix, traded
  for 23 the loop is built to clear.
- **TWO BUDGETS, BECAUSE ONE NUMBER WAS SERVING TWO CALLERS (WP-11.8, ruled 5 Sep).**
  `BUDGET_BATCH_S = 40.0` is `solve()`'s default — `check_all`, `corpus.drawing()`, the CLI, the
  reference plans, where a proof is worth waiting for. `BUDGET_INTERACTIVE_S = 25.0` is passed BY
  NAME by `workbench/server/evaluate.py` and `mcp_server/core.py`'s `place_plan`, the routes the
  infrastructure audit measured as the whole server's bound with a person waiting behind a 400 ms
  debounce. **`spec-builder-colonial` is CP-solved again at the batch budget**, FEASIBLE in
  40.7 s with 0 rooms outside its band — it had been falling back to the search since WP-11.7 by
  five seconds. Raising the batch number is cheap; raising the interactive one is not.
- **THE FURNITURE RATCHET MOVED FOR THE THIRD TIME AND THIS ONE IS AN IMPROVEMENT (WP-11.8).**
  86/70 → **65/65**. WP-11.3 moved that pair because the CATALOGUE was corrected, WP-11.6 because
  the PLACEMENT moved, and WP-11.8 because the placement got BETTER — twenty-one short-axis and
  five long-axis shortfalls stop existing. Which is Lucas's own opening complaint of Phase 9
  (*"the breakfast room is drawn 7.0 x 27.0 and cannot take its table"*) answered from the placer
  rather than from the furniture layer. **Three moves, three different causes, one number**:
  re-derive which layer moved it every time.
- **A FURNITURE RECTANGLE WAS JUDGED AT FULL PRECISION AND WRITTEN ROUNDED (WP-11.8).**
  `_overlaps` and `_inside` tested the computed rectangle and the record wrote `round(v, 3)`, so
  two hall chairs computed to abut a coat closet exactly were WRITTEN 33.574 against 33.573 — a
  thousandth of a foot of overlap, in the record, on a sheet, latent since the pass was written
  and exposed only by a placement that moved. `furniture.to_record()` rounds ONCE, BEFORE the
  collision and containment tests, so what is judged is what is written; the chairs are a named
  refusal now instead of a drawn collision. **That file's own WP-7.4 note two functions below is
  the same defect one step earlier** (position and extent rounded to different precisions, with an
  outside-the-room guard loosened enough to hide a real 0.04 ft error). Round at the boundary of
  the record, not after it.
- **FOUR GUARDS PINNED AN OUTCOME THE PLACER IS FREE TO CHANGE, AND EACH SAID SO IN ITS OWN
  COMMENT WHILE DOING IT (WP-11.8).** A fixture test required `spec-builder-colonial`'s
  primary bath to use two walls — the bath is drawn 20.00 × 12.44 now instead of 9 × 18 and one
  wall holds all four fixtures honestly. A refusal test required some refusal to state a figure —
  every refusal on the Tidewater plan is "no shared wall", which states none. A stacking test
  required `landing-off-well` to fire — it hangs off the KEPT list by design, and the landing is
  drawn clear. Two more required `spec-builder-colonial` to flag an over-capacity span, and it
  has none now (21 wall lines, 13 bearing, 0 over) while the corpus has 25 — **and that pair is
  the one to read twice, because the honest fix looks exactly like the forbidden one**: the
  capacity and the tolerance did not move, the plan got better and the corpus got worse, and both
  halves are pinned so a regression in either direction shows. **All of them failed on placements
  that had got better.** Each is rewritten against
  the BEHAVIOUR: a synthetic 9 × 14 ft bath no placement can outgrow, a COULD-NOT-EVALUATE skip
  with a pair-wise guard so both plans cannot go quiet at once, and a landing moved onto its stair
  by hand into the strip clear of the well. A fourth was retired outright — an assertion that the
  worst under-band room is ≥20% short is a FLOOR on how bad the engine is, and it is 6% now; it is
  a ceiling instead, failing on a regression and not on an improvement.
- **A NUMBER READ OFF THE DELIVERABLE IS NOT A MEASUREMENT OF THE CHANGE (WP-11.8).** The new
  sheet was rendered and looked at, which is this repository's own highest-yield technique — and
  the Tidewater upper passage is drawn 26′-10″ × 20′-1″, **539 sf against a declared 360**. Read
  beside the record that is damning, and the report very nearly went out saying the first key had
  bought shape with area. **It was 587 sf before**, at 2.74 : 1; it is 539 sf now, at 1.34 : 1 —
  the package REDUCED an overrun by 48 sf and halved the aspect. Corpus-wide the same way: rooms
  drawn a tenth or more off their declared area **164 → 148 of 231**, the BEFORE re-derived on a
  `git archive HEAD` checkout rather than remembered. Looking at the sheet finds a defect; only
  running the old code on the same plan says whether the change caused it. **Both halves are
  required, and this one was nearly published backwards.**
- **AND THE ROOM THAT LOOKS WORST ON THAT SHEET IS CONFORMING (WP-11.8).** The Tidewater ground
  passage is drawn 9.9 × 40.1, **4.05 : 1**, and `band_violations` counts it as inside its band —
  `rooms/centre-passage.json` states a ceiling of 5.0, which is the corpus's own reading of what a
  passage is. The key does what the corpus says, including where the corpus is permissive; do not
  read a long circulation room as evidence the ranking is not working. `centre-passage` states its
  band and is JUDGED; a type that states none (`ASPECT_FALLBACK`) is not counted at all, which is
  *unjudged is not passed* and not a silent pass.
- **TWO AUTHORED FACTS COULD NOT BOTH BE HARD, AND CLAUDE.MD HAD SAID WHICH ONE WINS SINCE
  WP-2.2 (WP-11.7).** CP held every room's declared `exterior_walls` as a pin. WP-11.7 added the
  room record's own `dimensions.proportion` band as a second hard pin and the model went
  INFEASIBLE at every footprint to ten bays. Measured: **band held + all 22 wall pins released →
  OPTIMAL; band held + pins held → INFEASIBLE**, and the ladder gives up 14 or 15 of the 15 shape
  pins at EVERY coverage floor from 0.97 down to 0.60 — **so coverage and packing are not the
  blocker** and `oq/the-placement-carries-no-wall-bands` is not what is in the way. The first
  conflict core says it in three literals: the Back Hall's declared N wall, its declared S wall,
  and its 7 × 16 ft programme — a room declaring an opposite pair must span the 40 ft depth, and
  at 112 sf that is 2.8 ft wide against a band of 5. **The entry six hundred lines below has
  carried the answer all along** — *"exterior_walls are aspirations, not rectangle edges … they
  are weights, at the 14 points `exterior_score` charges. Do not promote them to constraints"* —
  and `geometry_cp.py` promoted them from the day it was written. **Ruled 5 Sep: the band
  outranks the pins**, and a released pin keeps its 14 points in the objective, which is what
  that entry always said it was worth. Measured on `auto`: **serious 79 → 56, stacks kept 0 → 3
  of 5, no room outside its own band** (the worst had been a 13 × 16 ft bedroom drawn 45 × 7),
  and the passage 22 × 19 → **9 × 40, spanning again**. **Not one plan in the corpus has a shape
  pin downgraded** — the band is holdable everywhere it was tried; only the wall pins could not
  co-hold with it. **RATCHET NONE OF THESE**: they are `auto` figures and `auto` is not
  reproducible under a wall-clock budget — two runs of the unchanged baseline gave serious 79 and
  75 on this plan. The heuristic is untouched by the package and its figures are the
  deterministic ones.
- **`_RANK` IS THE LADDER NOW, AND A ROUND RELEASES THE WHOLE OF A RANK (WP-11.7).** It read
  `[key for _t, k, key in core if k == "wall" and key]` — one kind, hard-coded — so any
  requirement added after it was either un-downgradable (taking the placement to INFEASIBLE) or
  soft, which on this plan means INVISIBLE: `_finish_feasible` keeps the hard-only phase A
  placement whenever the polish times out and the objective never runs. `_RANK = ("wall", "axis",
  "shape")`, lowest authority first. **Whole-rank release is measured, not lazy**: downgrading
  only the cored pins needs EIGHT rounds and the intermediate states are the expensive ones —
  at a 6 s per-round cap round 2 returns UNKNOWN and the ladder never converges inside any
  bench-sized budget. `_reinstate` already exists to win back an over-release ("a solver core is
  SUFFICIENT, not minimal") and wins one of 22 back in budget. **`downgraded` now holds keys of
  two ARITIES** — `(level, room, wall)` and `(level, room)` — and three readers unpacked three
  names from every one; `_reinstate`'s own label would have raised IndexError inside the
  reinstatement pass. Split by arity, never by position, and both kinds are on the record.
- **`_absorb` UNDID A PROOF FOR THE THIRD TIME (WP-11.7).** CP proved every room inside its band;
  the post-solve absorb pass grew three straight back out of it — **library 1.69 against a
  ceiling of 1.6, powder room 2.66 against 2.2, a closet 4.21 against 4.0**, all with their pin
  still HELD. That function's docstring already recorded the same defect twice (a 2.8 sf linen
  press stretched to 8; OQ 55's upper room grown across a courtyard). It takes `ratios` beside
  `caps` and `keepout` now, and a room whose pin was RELEASED is deliberately absent from it.
  **Found by a test on its first run, not by reading.** Anything that runs AFTER a solve is
  outside its proof and has to be held to it separately.
- **THE OBVIOUS CP SPEED-UP IS 1.7x SLOWER, AND THE MEASUREMENT THAT SAID SO NEARLY DIDN'T RUN
  (WP-11.7).** `max(w,h) <= c * min(w,h)` is exactly `w <= c*h AND h <= c*w`, needs no
  `AddMaxEquality`/`AddMinEquality` pair, and reads as strictly cheaper. Measured: spec-builder
  **29.6 → 48.2 s**, tidewater **11.3 → 20.4 s**. CP-SAT's max/min propagators beat two reified
  linear constraints here. **The first attempt to measure it reported `exit code 144`, did not
  land, and the timing run after it compared the max/min encoding against ITSELF** — 29.9 s
  against 29.6 s, which is exactly what a null result looks like. A `grep` guarding the edit
  printed nothing and the shell's `&&` swallowed it. **Read the exit code of the EDIT, not only
  the output of the run after it** — the sibling of this file's own "an edit that reports success
  and changes nothing".
- **AN AXIS RULE THAT NAMES TWO ROOMS NAMES NONE (WP-11.7).** "Every circulation room declaring
  an opposite pair" selects TWO on the Tidewater record — the Centre Passage and the Back Hall,
  which is circulation and declares N and S as a HYPHEN. Two rooms pinned to one centre line
  cannot both hold, so the ladder released both and the passage went back to running across the
  house. It is the room the FRONT DOOR OPENS INTO now, which is the relation `plan_check`'s own
  entrance-axis census walks; where that picks out no room or more than one, the axis is UNJUDGED
  and nothing is pinned. **And the centring is REFUSED with its measurement**: `2x + w == W` is
  INFEASIBLE in 0.9 s with every wall pin already released, because a 10.2 ft passage centred on
  a 60 ft front leaves two strips holding 2,000 sf of programme in 1,992 sf of floor. A symmetric
  passage needs the footprint to gain slack, not a harder constraint.
- **`stacks_over` HAD SEVEN READERS AND FOUR DEFINITIONS OF "BELOW", AND EVERY ONE DECLINED IN
  SILENCE (WP-11.6).** Two engine terms and `geometry.bias` hard-wire level 0 as "below";
  `plan_check`'s drawn layer had `if level_of[rid] == level_of[so]: continue` with no note; its
  REACHABILITY reader and its SERVICING reader had no level test at all; `check_partis` checked
  the id and not the relation. The field's own schema description said why —
  *"room id on the level below, **for plumbing and structure**"*, two duties in one field — and
  there was an instance: `plans/tidewater-georgian-careful.json`'s ground-level powder room
  declared `stacks_over` a ground-level cellar stair, which three readers dropped, so **the plan
  carried four claims of which three were judged and no surface said which three**. Plan schema
  **0.8.0** splits it: `stacks_over` STRUCTURAL (exactly one level below, strict positive
  rectangle intersection), `wet_stack_with` SERVICING (any level including its own, and **the
  target need not be wet** — a stack needs a chase and a stair shaft is one; do not "correct" that
  record by re-pointing it at a bathroom). `build/stacking.py` is the one spelling and is a LEAF
  because `geometry.py` loads `plan_check.py`; `geometry_report.stacking` asserts
  `claims == kept + broken + unjudged` with a reason from a CLOSED set on every unjudged entry;
  `build/check_stacking.py` is the 50th check. **It cannot check that a plan states what its
  parti declares, because no plan record names a parti** — 0 of 16 — which is how WP-11.6's own
  two missing claims had to be found by hand: `oq/a-plan-does-not-name-the-parti-it-was-built-from`.
- **A RECORD EDIT MOVES THE PLACEMENT WITH NO ENGINE CHANGE, BECAUSE `bias` READS THE FIELD
  (WP-11.6).** `geometry.py:168` pulls a room toward its `stacks_over` target while the level is
  being SLICED, so authoring two claims changes which layouts are PRODUCED and not merely which is
  ranked. Measured on `heuristic`: claims 3 → 5, kept 1 → 3, serious 62 → 55, fatal 3 → 4,
  relaxations 7 → 9, transfer beams 9 → 14, and the upper floor stops being slivers (the landing
  6.0 × 15.4 ft → 12.1 × 13.5). **On `auto` the same edit buys nothing and costs 6 serious**: CP
  returns `OPTIMAL (hard-only) — kept hard-only phase A`, so its objective never runs and the soft
  stacking term is dead — 5 of 5 broken, `primary → drawing` included, which the search keeps.
  That is the measurement WP-11.7 rests on: **on this plan only a hard constraint moves the engine
  that draws the sheet.** The one new fatal is `unreachable: chamber3` and is NAMED, not absorbed —
  clearing it means authoring a door from a bedroom into a closet, which is a placement failure
  written into the record.
- **THE PLACER PLACES TWO LEVELS AND SAID NOTHING ABOUT THE THIRD (WP-11.6).**
  `_finish` writes `best["ground"] if idx == 0 else (best["upper"] if idx == 1 else {})` and
  `solve_heuristic` is written against `prep[0]`/`prep[1]`. `plans/reference/bad-03-narrow-lot-
  townhome.json` declares three levels; its one level-2 room came back with **no geometry, no
  finding and no note** — all eight findings naming it were DECLARED-layer findings, and the sheet
  drew the house without its top floor in silence. Disclosed now on `multi_element`'s exact
  precedent: `geometry_report.multi_level`, `plan_check.drawn`'s `rooms_unplaced` with a `serious`
  finding, and `check_stacking.py`. **The discriminator already existed and is exact** —
  `geometry.is_placed` tells a terrace outside the footprint (no rectangle, correct) from a level-2
  great room (no rectangle, a defect), and collapsing them is how a missing storey reads as a
  design decision. Placing a third level is NOT built:
  `oq/the-placer-places-two-levels-and-says-nothing-about-the-third` names what must be ruled,
  including what `index: -1` means — the schema documents a cellar and no record uses one, so the
  placed window is not simply "the first N levels".
- **A DISCLOSURE WIRED INTO ONE RECORD WRITER AND NOT THE OTHER IS NO DISCLOSURE (WP-11.6).**
  `multi_element_disclosure` (OQ 40) was called by `write_record` and NOT by `_finish`, so every
  CP-produced multi-element placement has shipped with no disclosure since the day OQ 40 was built.
  Found while adding the second one beside it. There is one `_disclose(plan)` now, called by both
  writers, so a third cannot be added to one and forgotten in the other.
- **WHEN A RATCHET MOVES, RE-DERIVE WHICH LAYER MOVED IT — THE ANSWER CHANGES (WP-11.6).**
  `test_furniture_drawn.py`'s pair went 86 → 88 at WP-11.3 with the placement BYTE-IDENTICAL (the
  catalogue moved) and 88 → **86 / 70** at WP-11.6 with the catalogue byte-identical (the placement
  moved). The two look identical in that file and have nothing in common; both notes are kept side
  by side so the next reader cannot assume the last cause was the cause.
  **And WP-11.4's roof pruning earned itself here**: across a commit that moved the placement, the
  PRUNED hash is unchanged at `0d94e0cd...` while the RAW `build_roof` return goes
  `4335d9e1... -> d8107962...`. The pin said "the roof did not change" about a change to the
  placement, which is exactly what it was re-cut to answer. Do not un-prune it.
- **`tests/fixtures/sheet_symbols/` IS REGENERATED BY SOLVING AND ITS OWN README SAYS WHY THAT
  CANNOT WORK (WP-11.6, found in ordinary work).** The README: *"a fixture generated by solving
  would pin the machine as much as the code."* `generate.py:40`: `geometry.solve(plan)` — no
  engine argument, so `auto`, so CP-SAT under a wall-clock budget. Measured **on the pristine tree
  with no code change at all**: regenerating gives `825 insertions, 804 deletions`, and
  `spec-builder-colonial.json` moves as much as the Tidewater one. So "regenerate and read the
  diff" hands the reader eight hundred lines of solver noise with the renderer's change buried in
  it. **Do not regenerate it to "keep it current"** — it is contract INPUT, never re-solved by the
  suites that read it. `oq/the-frozen-fixture-is-regenerated-by-solving`.
- **DO NOT `git stash` WHILE A BACKGROUND SUITE IS IN FLIGHT (WP-11.6).** A stash run to measure
  the pristine tree landed inside a running `pytest` and produced two failures — `assert 7 == 9`,
  the new source against the old data — that were entirely an artefact of the tree changing under
  the runner. It looks exactly like a real regression. The same three suites had passed minutes
  earlier and passed again after.
- **AN EDIT THAT REPORTS SUCCESS AND CHANGES NOTHING IS INVISIBLE FOR THREE LAYERS (WP-11.3).**
  A step that was to add `marks` to `schema/plan.schema.json` ran a `replace` whose target was
  not in the file, asserted nothing, re-parsed the unchanged JSON successfully and PRINTED ITS
  OWN SUCCESS. The consequence: the solved record failed its own schema, `core.check_plan`
  returned `{"error": ...}`, and `workbench/server/evaluate.py`'s early
  `if "error" in check: return out` sits ABOVE the branch that attaches the placement -- so the
  API answered **200 with neither `placement` nor `placement_error`** and the Plan Workbench sat
  on "placing…" for ever. No exception, no console error, nothing in a log; 1,796 unit tests and
  a clean `vite build` all passed. It took a probe on the evaluate RESPONSE BODY to see that both
  fields were absent. **Assert that an edit landed and then re-read the file** -- this file
  records that rule for a corrected NUMBER and it is exactly as true of a schema key. And when a
  surface hangs with no error, read the response body before reading the code: a 200 that is
  missing a field is the shape an early return makes.
- **A RECORD CAN CONTRADICT ITS OWN NOTE, AND A REGEX CANNOT FIND IT (WP-11.3).**
  `rooms/library.json` authored its table `placement: "against-wall"` while the item's own note
  reads *"the table is in the MIDDLE of a library and against a wall in a study, and that
  difference is what distinguishes the two rooms"* -- the STUDY's answer, on the LIBRARY's record,
  and `rooms/study.json` has its desk correctly against a wall. **The sweep for this class returned
  one hit and it was a false positive** (`nursery`'s glider, whose note says it *cannot* go against
  a wall, agreeing with its `freestanding`) and missed the real one, because the library's note
  names both placements in order to contrast them. That is `check_grouping_rules.py`'s lesson in a
  new place: author the field, never tighten the regex until the number looks better. Correcting
  the one record moved `tests/test_furniture_drawn.py`'s short ceiling **86 -> 88** with the
  placement BYTE-IDENTICAL -- a table in the middle takes clearance on two sides, 6.83 ft becomes
  10.33, and two `good-*` reference plans are convicted correctly. **When a ratchet moves, re-derive
  which layer moved it**: this one was the catalogue and not the drawing, and the byte-identity of
  the fixtures, the geometry and the relaxation counts is how that was isolated rather than guessed.
- **`kind` ON A FURNITURE ITEM, AND THINNESS IS NOT ONE OF ITS VALUES (WP-11.3).** 278 items,
  `object` 241 / `reservation` 23 / `variant` 6 / `placed-elsewhere` 5 / `covering` 3, required by
  `check_rooms.py` on `placement`'s WP-7.2 precedent. `reservation` is OQ 92's own named class --
  *"clearance reservations wearing an item's shape"*, a clear route or a standing person, carrying
  a footprint and a clearance and not being a thing. **`placed-elsewhere` has one member and it is
  the sharp one**: `rooms/stair-hall.json` carries *"the stair itself, dog-leg with half landing"*
  as furniture at 120 x 78 in and `openings.stair_pass` already draws it. `variant` is an
  alternative to an object listed EARLIER in the same room -- `bedroom` states a queen bed, a full
  bed and twin beds, all `essential` by default, and a naive pass draws three beds in one room.
  **A television is an `object` that has no plan bulk**, so thinness is a SCALE rule
  (`fg-too-thin-to-draw`, citing `plan_check.py`'s own `fw < 8`) and not a kind. And
  `footprint_in` means one piece for some items and the whole group for others, over 38 that name
  a count -- drawn once and disclosed,
  `oq/a-furniture-footprint-is-sometimes-one-and-sometimes-the-group`.
- **EVERY FURNITURE RULE DECLARES A GRADE, WHICH IS "UNJUDGED IS NOT PASSED" APPLIED TO
  PROVENANCE (WP-11.3).** `furniture/grammar.json`: `reading` where the record states the rule AND
  the figure, `editorial-from-prose` where it states the rule in words and the number is ours,
  `editorial` where no sentence exists at all. Ten rules -- four editorial, three readings, and
  **three STATED AND NOT EXECUTED** (the library table centred *because it is a library*, the
  parlor's peripheral arrangement, the hall's high table facing down the room), each needing a fact
  no record carries. `build/check_furniture.py` **calls** `check_openings.check_basis` rather than
  copying it -- that function already walks `furniture[<item>].note`, so the reuse needed no change
  -- and an `editorial` rule that QUOTES a record is an error in the other direction, because a
  judgment wearing a citation reads as sourced.
- **THE MARKS GO ON THE RECORD, WHICH IS WP-6.2'S RULE A LAYER UP (WP-11.3).**
  `furniture/symbols.json` states each symbol as primitives in a unit square; `furniture.marks_for`
  maps them into the item's own rectangle ONCE, in Python, and writes the result. Both renderers
  draw what is there and derive nothing -- handing them a symbol id beside a rectangle is exactly
  the invitation that put the two 0.7 in apart on the first plan WP-6.2 tried it on. **The JS port
  was written and then deleted because there was nothing left to port.**
  **THE ARC THAT LEFT THE ROOM IS THE ENTRY'S OWN LESSON**: the piano's first symbol drew a grand's
  bent side as an arc whose radius scaled off the item's SHORT side, and it swept outside the item
  **13 times in 1,078 marks while every item RECTANGLE stayed inside its room the whole time**. The
  rectangle guard could not see it; it was found by looking at the sheet. There are two tests now
  and the second says in its own name that it is not the first. `arc` left the vocabulary with the
  curve, because a primitive no symbol uses is an unreachable branch in two renderers.
  And `symbol_for` matches WHOLE WORDS where `_FIXTURE_ALIASES` matches substrings: bare substrings
  drew *"desk (any BEDroom occupied by anyone under twenty-five)"* as a bed.
- **THE SHEET CARRIES ITS OWN FACE NOW, AND THE MARGIN SAYS WHICH (WP-11.5).** Graphic Standard
  No. 1 names one serif voice and every plate this system had ever produced asked for it in a
  `font-family` stack and carried no font -- which is half of the "three typefaces on one plate"
  that opened Phase 11. `build/gen_sheet_font.py` subsets **EB Garamond 1.003 to printable ASCII
  plus a named extras list: 127 glyphs, 15,016 bytes WOFF, 20,024 base64**, committed under
  `assets/generated/` with the SIL OFL beside it; `sheet_style.font_face_rule()` puts it in each
  sheet's own `<style>`. The Tidewater plate goes **43,141 -> 63,555 bytes, +47%**, per sheet,
  because an exported SVG has to stand alone. `face_status()` is what the margin prints and it has
  TWO states and never a silence -- `FACE EMBEDDED — EB GARAMOND VERSION 1.003 …` or `FALLBACK`
  with the reason. **WOFF and not WOFF2** (Brotli is absent here) **and not the TTF** (26,280
  bytes against 15,016), and **it reaches no desktop drawing program**: Inkscape resolves type
  through fontconfig and loads no `@font-face` in any format, so an embedded face reaches every
  browser and nothing else. `fontTools` is in `requirements.txt` for the GENERATOR alone and a
  test walks the five renderer sources to keep it out of render time.
- **`recalcTimestamp=False`, AND IT IS THE WHOLE OF WHY A GENERATED FONT CAN BE VERIFIED
  (WP-11.5).** fontTools writes `head.modified` as the time of the save by default, so two builds
  of one font from one source differ in four bytes and every hash of the output differs with them
  -- measured twice before the line existed, and `gen_sheet_font.py --check` would have been a
  command that always says FAIL. **A generated artefact nobody can rebuild identically is an
  artefact nobody can verify.** The same `--check` had a second defect of the family: it printed
  the docstring and returned 0 when given no source, which is a check reporting success by doing
  nothing.
- **THE DIVERGENCE MARK IS IN NEITHER FACE THE SHEET NAMES (WP-11.5).** `∗` is U+2217 ASTERISK
  OPERATOR -- not the typographic asterisk U+002A -- and it is the mark a working sheet puts on
  every room drawn at a size the record does not declare, defined in the sheet's own margin.
  Measured: it is in **neither EB Garamond (2,091 cmap entries) nor Courier Prime (383)**, the
  first family of each of the sheet's two stacks, and every OTHER character the shipped sheets
  draw is supplied by its own class's first family. It renders today only because Chromium falls
  past both stacks into a system font -- so the plate carries a third face for one glyph, which
  is Phase 11's own complaint at one character. **NOT CHANGED**: the symbol is the standard's and
  swapping a glyph a standard chose is the same class of edit as reconciling two records by
  picking the number that makes a checker green.
  `oq/the-divergence-mark-is-in-neither-face-the-sheet-names`.
- **THE PYTHON FITTER MEASURES THE FACE IT DRAWS IN, FOR THE FIRST TIME (WP-11.5).**
  `render_plan._adv` was a five-branch estimate -- `uppercase or digit -> 0.66` -- which is one
  number for a three-to-one spread: EB Garamond's `I` is 0.34 em and its `W` is 0.916, and its
  `.` is 0.23 where the estimate said 0.28. `workbench/app/src/sheet/label.js` has measured the
  real glyphs in a canvas since WP-5.2. The widths come off the subset's own `hmtx` into the
  sidecar; **34 room labels across 10 of the 16 plans change size** on them. The estimate is KEPT
  for a tree with no committed asset, and a test says which one is running.
- **A GUARD OVER "WHAT THE SHEETS DRAW TODAY" CANNOT SEE A NARROWED SUBSET, AND SAYING SO IS THE
  FIX (WP-11.5).** `test_every_character_the_sheet_sets_in_the_serif_is_in_the_subset` is the
  obvious guard and it is blind in one direction: every character the two shipped plans set in the
  serif is a capital, a digit or ASCII punctuation, because room names and plate titles are
  upper-cased before they are drawn. A regeneration cut to those 42 glyphs saves 8 KB a sheet
  (11,984 base64 against 20,024), leaves that test GREEN, and breaks the first mixed-case name
  anybody writes. The guard that bites is over the PROMISE -- the subset must cover printable
  ASCII -- not over today's traffic; both are kept and the mutation was run both ways.
- **A PARAMETER'S PRECONDITION CAN BE THE FIRST SIX WORDS OF ITS OWN SLOT'S PROSE, AND NOTHING
  READS PROSE (WP-11.4).** `porch_type.portico_bays` resolves to 1 on `tidewater-georgian` and
  `PLAN-OF-ACTION.md` asked for "columns and their answering pilasters where `portico_bays = 1`".
  Read that way it puts a portico on **5 of the 8 nodes that resolve one** -- all `stoop-only` --
  including a shipped reference plan whose kit calls the entry portico ATYPICAL and says why. The
  condition is the slot rule's own opening clause: *"WHERE A PORTICO OCCURS it is one bay wide"*.
  That is WP-8.4's `granted_when` finding in a new place, and worse, because here the condition is
  not a field at all. **And where a portico IS canonical the column has no width**: 23 nodes have a
  canonical portico, 8 resolve a `portico_bays`, and **exactly 1 of the 159 that carry a kit states a
  diameter in inches**
  (`neoclassical-revival`, and it states no bay count) -- the intersection of the three facts a
  drawn column needs is EMPTY, so this corpus can draw no column anywhere. `build/check_threshold.py`
  re-derives all four numbers every run and WARNS the moment a node acquires all three.
- **THE DRAWN STACK REACHES ONE NODE IN 159, AND THAT IS THE CORPUS RATHER THAN THE CODE
  (WP-11.4).** Swept over all 159 kits with the Tidewater block: 15 styles draw a stoop and **1
  draws stacks**. It decomposes -- **14 of 159 make a hearth position canonical in their OWN kit**
  (the reader `roof.py` argues for at length and this pass adopts), **3 of those name a gable end**,
  **1 names a side**. Do not read a low count here as a thin implementation; read it as the
  measurement it is, and see `oq/which-rooms-take-the-hearth` and
  `oq/the-massing-states-its-hearth-in-prose-and-a-substring-test-reads-it` for the two gaps that
  produce it.
- **THE ANSWER TO A SLOT'S QUESTION CAN LIVE IN A DIFFERENT SLOT, AND THE ONTOLOGY SAYS WHICH
  (WP-11.4).** `tidewater-georgian`'s `chimney` slot makes BOTH `gable-end-paired-interior` and
  `gable-end-exterior` canonical -- the same mass on opposite faces of one wall -- so the
  roof-expression slot cannot decide a plan fact. `hearth_position`'s own note is the authority:
  *"Kept separate from `chimney` because the ontology separates the roof expression from the plan
  fact."* Its canonical `exterior-end` settles it. `build/roof.py` reads `chimney` for the stack's
  HEIGHT; `build/threshold.py` reads `hearth_position` for its PLAN; the split is the ontology's
  and not a convenience.
- **THE MASSING'S `hearth` IS A SECOND VOCABULARY, IN PROSE, AND SEVEN OF FORTY STATE A
  DISJUNCTION (WP-11.4).** Kits name variant ids (`exterior-end`, `gable-end-paired`); massings
  write sentences -- `gable-end or corner`, `gable-end-paired or central-stack`, `party-wall or
  end`, `central or end`, `central or none`, `interior or end`. **`roof.py::chimney_positions`
  reads that field with `"gable-end" in hearth`**, which answers TRUE for two disjunctions, and
  that fallback fires on **135 of 159 styles**; neither shipped plan is affected, which is why
  nothing has caught it. `build/threshold.py` carries `SIDE_OF` and `MASSING_HEARTH` as two CLOSED
  tables, proved total by `check_threshold.py` -- **which failed on its own first run**, on twelve
  massing values the kit vocabulary does not use. `roof.py` is NOT changed: it decides a height and
  the measurement belongs to whoever moves it.
  `oq/the-massing-states-its-hearth-in-prose-and-a-substring-test-reads-it`.
- **A CHILD BAND REPLACES AN ANCESTOR'S DERIVATION AND THE RESOLVED RECORD LOSES IT -- 224 TIMES
  (WP-11.4).** `georgian-colonial-american` derives `steps_and_stoop.riser_count_from_grade` as
  `ceil(part * 2.4 / 6.75)` = 4 from `storey-graduation`; `tidewater-georgian` `extends` the slot
  with a `[3, 6]` band, the child's object replaces the parent's whole object (correct, and what
  `extends` means), and the resolved kit then holds a range where one step up the corpus holds an
  expression with a source pack. `resolve_kit.py federal-style --verbose` prints the 4; the same
  command on `tidewater-georgian` prints nothing. **224 (node, slot, parameter) triples over 58
  nodes and 7 distinct parameters** -- `casing.width_in`, `height_proportion.second_over_first`,
  `pediment.rise_over_span`, `pilaster.projection_in`, `pilaster.width_in`,
  `steps_and_stoop.riser_count_from_grade`, `window_sill.projection_in`.
  `oq/a-child-band-replaces-an-ancestor-derivation`.
- **THREE STATEMENTS OF ONE DEPTH, AND THE FIGURE IS THE INTERSECTION AND NEVER AN AVERAGE
  (WP-11.4).** The stoop's depth is `platform_depth_in` [36, 60] in, `porch_depth.stoop_depth_ft`
  [4, 6] ft and `porch_depth.stoop_min_depth_in` 48 in -- and a 36 in stoop is inside the first and
  below the third. 48 in is the only value all three admit, and it is drawn for that reason rather
  than as anybody's midpoint. Where three statements do not intersect the figure is UNJUDGED and
  nothing is drawn; a test fails when the pass splits the difference. Do not edit any of the three
  to agree with the others -- `oq/a-grouping-rule-and-a-room-record-can-disagree`'s standing rule,
  one layer up in the kit.
- **A BYTE-IDENTITY PIN CAN BE MEASURING THE PLACEMENT AND CALLING IT THE ROOF (WP-11.4).**
  `build_roof`'s return embeds `section`, which embeds the PLACED plan. The pin taken across the
  move of `roof_form_for` / the ridge axis / the two gable-end points into `build/threshold.py`
  went green across the move and RED two commits later, on a change that added two keys to the
  placed record and touched no roof code at all. **A pin that reads "the roof changed" when the
  roof did not is worse than no pin.** It hashes `main`, `chimneys`, `checks`, `outline`,
  `elevation_profiles` and `footprint` now, measured on a `git archive HEAD` checkout of the
  pristine tree and again on the working tree: `0d94e0cd...`, over 180 records.
- **TWO OF THE FOURTEEN REFERENCE PLANS HAD BEEN FAILING THEIR OWN PLAN SCHEMA SINCE OQ 55
  (WP-11.4, found in ordinary work).** `geometry.py` writes `{"heated": false, "roofed": ...}` into
  `geometry.void` and the schema's `void` object forbade `heated` under
  `additionalProperties: false`. **Nothing validates a PLACED plan** except the API's own gate
  (WP-10.1), and a reference plan never goes through it. The `geometry` object's own 0.3.0
  description records the identical shape one nesting level out -- fixed there, left open in its
  child. Admitted at 0.7.0; 16 of 16 validate now, and
  `tests/test_threshold_pass.py::TestThePlacedRecordValidates` is the guard, reporting COULD NOT
  EVALUATE without `jsonschema` rather than passing.
- **THE BROWSER WALK IS RUNNABLE IN A SESSION AND IT CATCHES WHAT THE UNIT TESTS CANNOT
  (WP-11.2).** `workbench/app/e2e/walk.mjs` needs a built app and a live server, and this tree
  ships no `node_modules` -- so it had never been run in a session on this branch. It runs:
  `cd workbench/app && npm install && npm run build` (the registry is reachable),
  `pip install uvicorn fastapi httpx`, and Chromium is already at `/opt/pw-browsers` where
  `walk.sh` looks for it. **151 checks, about two minutes.** It was GREEN on the pristine tree and
  RED on WP-11.2's change, on a defect 81 passing unit tests and a clean `vite build` had both
  missed: `ReferenceError: LABEL_PAD is not defined`, a third use of a constant replaced by a
  function, in the divergence mark for a room too small to carry its dimension string. **There was
  no console error for the first twenty seconds** -- the throw only happens on the render that HAS
  a placement, which arrives after an evaluate, by which time the walk had timed out on
  `svg[role="img"]`. Instrument it with a probe that logs `pageerror` AND every `/api/` response
  and polls for a minute; the error is there, it is just late.
  **And `vite build` WARNS and still builds on a duplicate `style` attribute** -- React keeps the
  last, so the drag handle's gilt stroke was silently dropped and the affordance would have gone
  invisible. Read the build's warnings, not only its exit code.
- **A GUARD THAT READS A SELECTOR RATHER THAN A PROPERTY GOES BLIND ON THE NEXT EDIT, AND THIS IS
  THE FOURTH INSTANCE (WP-11.2).** `walk.mjs`'s drag-preview check filtered lines on the `stroke`
  ATTRIBUTE containing "gilt". The pen ladder moved every stroke into `style=` -- `var(--lw-cut)`
  does not resolve in an SVG presentation attribute, so it had to -- and `getAttribute('stroke')`
  then returns null on every mark on the sheet: the check would have counted zero previews on a
  working drag and passed nothing while looking green. It reads COMPUTED STYLE now, which is what
  the pen check thirty lines below it already does and says why (WP-5.7's `stroke-width` inversion).
  Two more in the same package: `test_every_level_plate_shares_one_top_edge` selected the plate by
  its dark HEX and `test_the_building_outline...` selected `<rect class="wl">`, both retired by
  WP-11.1; and this package's own new band selector over-specified the attribute ORDER and went
  stale the moment the band gained a `data-wall`. Select on the property, and put `[^>]*?` between
  attributes you do not control the order of.

- **THE PLAN SHEET IS DRAWN IN GRAPHIC STANDARD No. 1 NOW, AND THE STANDARD WAS ALREADY WRITTEN
  DOWN (WP-11.1).** `workbench/app/src/theme/tokens.css` has carried it verbatim since WP-5.2 --
  cream ground, a warm graphite ink ladder, five named line weights, poche as *"a body: coal skin,
  salmon flesh"*, letterspaced roman capitals, and *"Color names things; it never outlines them"* --
  and `build/render_plan.py` obeyed none of its GRAMMAR while `svg_theme.py` translated its COLOURS
  on the way to the browser. **`build/sheet_style.py` is the one spelling now**: `LIGHT`, `LW`,
  `INK_FOR`, `POCHE`, `FACE`, `TRACK`, `DASH`, plus `DARK` for the three renderers still in the dark
  register. **Hex literals in the four renderers: 52 -> 0**, and all ten sheets `corpus.drawing()`
  produces hash byte-identical across that move.
  **THE WALL IS A BODY AND NOTHING ABOUT IT IS NEW DATA**: `structure.wall_thickness(plan)` has read
  `declared.construction_type` against `construction/wall-assemblies.json` since WP-3.1 and no
  drawing had ever read it (Tidewater 15.5 / 11 / 4.5 in declared; the spec Colonial 8 / 5.5 / 4.5
  **defaulted, and the sheet says so**). The envelope is drawn OUTWARD from the block because the
  rooms tile it exactly, so the block edge is the wall's INSIDE face; interior walls are centred on
  the shared line and therefore eat half a thickness from each room, which the schedule states on
  every plate -- `oq/the-placement-carries-no-wall-bands`. An opening is a HOLE cut from
  `derive_openings`' own spans, so a gap and the leaf in it cannot disagree.
  **TWO REGISTERS, ruled 4 Sep 2026**: `presentation` (drawing and names) and `working` (dimension
  strings, the `∗`, the `△` on the field). `render()` defaults to **working** and
  `corpus.drawing()` to **presentation**, deliberately -- a machine that does not choose keeps every
  disclosure (`test_measurement_honesty` counts one triangle per relaxation off a bare
  `render(out, path)`), and the surface a PERSON reads is the clean one. Nothing is deleted by
  either: the six banner lines are a MARGIN SCHEDULE below the border on both, wrapped to it.
  **The scale is 13 px/ft, `--px-per-ft` from the standard**, and it is a floor rather than a taste:
  at the old 7 a 4.5 in partition is 2.6 px of body between two 3 px cut lines.
  **ONE TOKEN IS USED AGAINST ITS OWN NAME AND THE REASON IS SCALE**: `--poche-partition` is
  `--sepia-pale`, which reads as a field in a large-scale DETAIL and, at plan scale, leaves under
  two pixels of fill eight values off the vellum -- measured, a partition read as a HOLLOW TUBE
  beside a solid exterior wall, which says something about the record that is not true. The
  partition takes `--sepia` (the standard's own "timber & age"), a choice between named duties and
  not a new colour; `sheet_style.POCHE.partition_large` keeps the token's own value for the
  register it was written for.
  **THREE GUARDS HAD SELECTORS THIS PACKAGE RETIRED AND ALL THREE WOULD HAVE PASSED VACUOUSLY** --
  the plate-top check selected the paper ground BY ITS DARK HEX (the ground is gone; the plate
  states `data-plate-top` now), the per-element outline check read `<rect class="wl">`, and the
  palette-totality check scanned four renderer sources that now hold no hex at all. **And widening
  that last one opened a hole a mutation found: `LIGHT` vouched for itself**, so
  `"smuggled": "#123456"` in it passed. `test_the_light_register_quotes_the_standard_and_does_not_
  invent_it` holds every `LIGHT` value against `tokens.css`. Report:
  `docs/reports/wp-11.1-the-sheet-in-its-own-standard.md`.
- **A SCREENSHOT WHOSE WINDOW IS EXACTLY THE CANVAS SIZE LIES ABOUT THE BOTTOM OF THE SHEET
  (WP-11.1).** Rasterising the new sheet at `--window-size=W,H` for the SVG's own W and H showed the
  title block truncated after two of six lines, and two crops agreed. Every line was in the file, at
  the right `y`, inside the viewBox -- `getBoundingClientRect()` in the page put all six exactly
  where the renderer had -- and the missing 60 px were the page's own body margin pushing the
  document down. **Twenty minutes went into a defect that was not in the drawing.** Shoot with
  padding, and measure the drawing (`getBBox`, `getBoundingClientRect`, a pixel profile) before
  believing a picture of it.

- **A BAKED SNAPSHOT IS NOW JUDGED AGAINST ITS OWN EXPRESSION, AND THE EVALUATOR THE QUESTION
  ASKED FOR HAD EXISTED ALL ALONG IN TWO PLACES (3 Sep 2026).**
  `oq/a-baked-pack-value-is-a-second-delivery-path` said 143 kit parameters carry both an `expr`
  and the `computed_at.value` it produced, that exactly one was of a shape a reader could
  evaluate, and that the count of stale snapshots was therefore "unknown, not zero". It is
  knowable: `check_kits.py::check_baked_snapshots` re-derives each one AT THE CONTEXT THE SNAPSHOT
  RECORDS — **135 judged and all agreeing, 8 that cannot be judged, 0 stale.**
  **`proportion_engine.evaluate_expr` parses every shape in use, and `resolve_kit.eval_parameters`
  has been re-deriving every baked parameter and comparing it to the stored value all along**,
  setting `r["stored"]` on a disagreement. `stored` is a display field: nothing reads it, nothing
  fails on it. What was missing was never an evaluator, it was a verdict.
  **The 8 are unjudged because `computed_at` records three bindings and the expressions read
  five**: seven read `span` and one reads `room_width`, neither ever recorded. They all reconcile
  at a span of 540 — `check_kits.REF_CTX`'s value, and evidently what they were baked at — but
  that is a RECONSTRUCTION of the context, not a record of it, and a check may not convict or
  acquit on a number nobody wrote down. All eight are on `georgian-colonial-american`.
  **THE CHECKER'S OWN RATCHETS CANNOT GUARD IT, which is why the identity of the eight is pinned
  as a SET in `tests/test_baked_snapshots.py`.** Deleting the gap detection sends them to be judged
  against `DEFAULT_BINDINGS`, whose `span` is 240 — measured, that CONVICTS SEVEN as stale and lets
  the eighth pass in silence, both wrong directions from one deletion, while `baked_judged` rises
  135 → 143 (above its floor) and `baked_unjudged` falls 8 → 0 (below its ceiling) and neither
  ratchet notices. The remedy for the eight is one field: `computed_at` reads `<name>_in` as the
  binding `<name>` for ANY key, so writing `span_in` makes them judgeable with no code change.
  **Do not quote this against `baked_vs_refused`**: that is the OTHER half of the same question — a
  snapshot delivering a value the live rule REFUSES, ratcheted at 71 — and a snapshot can be
  perfectly faithful to its expression and still be a delivery nobody authorised. Two halves, two
  meters, neither quotable for the other.
- **THE DIFF GUARD WAS BLIND FOUR WAYS, AND THE MOVES BEHIND IT WERE WRONG IN FIVE MORE (the
  session's audit of WP-9.4).** `_paths_written` stopped at a list whose length changed, so a
  move that ADDED a room hid every other write behind `levels[].rooms[]` and
  `split-per-grouping` re-derived openings plan-wide under the guard built to catch that; it
  could not see a rewrite inside a list a move appended to, a write to the first of two rooms
  sharing an id, or a dict added whole (`setdefault("declared", {})` refused two moves on every
  record without the key). Beside it: two widen moves read the LONG side as the width where
  `plan_check` swaps before judging; `narrow-the-window` widened a bath's 2 ft window to 2.73;
  `add-the-grammar-door` duplicated a door on an asymmetric record; `resolve_kit`'s
  `SystemExit` escaped two of the three re-deriving moves (one guard in `apply()` now); and the
  three successor moves were unreachable once their predecessor was tabu. **The budget of a
  compose is the SET's** (`revise_budget_s`, spent in rank order; a candidate it does not reach
  says `revision_skipped`), the bounds on every loop knob are `core`'s constants and the MCP
  tools read them, and a revised plan's `revision_summary` is admitted by the plan schema so
  the DXF round trip reads back. `tests/test_moves.py::TestTheSessionAuditOfTheGuard` and
  `tests/test_revise.py::TestTheSessionAuditOfTheLoop` are the guards.
- **A CALLER-SUPPLIED PLAN REACHED THE SOLVER UNVALIDATED, AND NINE OF ITS FIELDS CRASHED IT
  (WP-10.1).** `/api/plan/evaluate`, `/api/drawings/{kind}` and `/api/export/{fmt}` read
  `body.plan` and handed it straight to `build/geometry.py`, while their siblings
  `/api/plan/critique` and `/api/plan/revise` validate inside `core`. Fuzzed at `solve()`'s entry:
  **9 of 16 probed fields raise** on a value of the wrong type -- `room.type`, `room.id`,
  `room.width_ft`, `room.length_ft`, `room.exterior_walls`, `room.doors`, `plan.style`,
  `plan.massing`, `plan.levels`. `C["rooms"].get(rtype, {})` on a dict is `TypeError: unhashable
  type`, so it is a 500 and a traceback from an UNAUTHENTICATED route for a field the schema types
  `string`. `app._plan(body)` is the one reader now and answers 422 naming the path. **The half
  that matters more than the refusals is that it refuses nothing**: all 16 plan records in the tree
  and the composer's own DECLARED output validate, checked before the gate went in, because the
  bench client posts the declared record and a gate that rejects its own traffic is worse than the
  crash it replaces. A tenth field, `room.block`, is answered at the GEOMETRY layer instead --
  ignoring a malformed tag is a conservative reading that is available there and is not available
  for `type`: there is no conservative reading of a room whose type is a list. **And the gate had to be COMPILED, which
  is the `copy_json` lesson in the other direction**: `jsonschema.validate(instance, schema)`
  rebuilds the validator on every call, measured at **60.5 ms on the largest shipped plan --
  17.9% added to `/api/plan/evaluate`, which the infrastructure audit measured as the whole
  server's bound**. Compiled once (`app._plan_validator()`), it is **3.9 ms, 1.2%**. Measure what
  you add to the hot path BEFORE you add it.
- **A MASSING ELEMENT IS PLACED AND SIX LAYERS BELOW THE PLACER READ THE MAIN BLOCK AS THE WHOLE
  BUILDING (WP-10.1).** OQ 40 is ruled and `geometry.blocks_for` places a dependency beside the
  house; `openings`, `structure`, `vertical_score`, the lot cap, `plan_check`'s drawn layer and
  `export_ifc` all still read `footprint.width_ft`/`depth_ft`, and each was MEASURED wrong on a
  dependency room in its own direction -- a garage window drawn 14 ft from the garage, a clear span
  manufactured across the hyphen gap, an upper wall "supported" by a wall under no upper floor, a
  house reporting `lot_capped: true` at 34 ft wider than its lot, a critic convicting a dependency
  room of reaching no exterior wall, and IfcSpaces floating clear of their slab.
  **`geometry_report.multi_element` DISCLOSES all six** and names any room above the ground level
  whose `block` tag the placer does not read. `engine="cp"` REFUSES a multi-element plan outright
  (one rectangle, `x = NewIntVar(0, Wi)`) and `auto` falls back saying why -- so on a plan with a
  dependency the engine that PROVES is unavailable and the engine that SEARCHES carries the
  findings. **The composer writes no `block` on any room**: C2/C3 were reverted when the audit found
  five more defects below them, so the only route in is a caller-supplied record, which is exactly
  the reader who cannot know. `oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it`
  carries the four things that must be ruled before this is built. Report:
  `docs/reports/wp-10.1-the-audit-of-the-dependency.md`.
- **A VALUE DERIVED FROM A THRESHOLD AND THEN TESTED AGAINST IT IS UN-FAILABLE, AND THERE ARE THREE
  IN ONE FILE (WP-10.1).** `roof.py::wing_step_down` picked its ratio INSIDE the band it then tested
  against; `gambrel_break_check` tested `GAMBREL_BREAK_FRACTION_DEFAULT = 0.625` against the fault's
  own `[0.55, 0.65]` -- `_style_gambrel_geometry` initialises `break_frac = None` and **has no branch
  that ever assigns it**, so `break_ok` was `True` on all 164 styles, forever. Both report `None`
  with a reason now. The chimney `style_check` is the third and is still un-failable for the one
  style that can run it. **The second was dismissed on a docstring and died on a run**: the hedge
  cited to wave it away is about `diff_ok`, a real comparison of two stated pitches. **And fixing it
  convicted a house on a plate** -- `roof.py`'s CLI and `render_roof.py` both did
  `'OK' if x else 'FAIL'`, so an unjudged verdict printed as FAIL on the one surface a reader looks
  at, one line from where the first fix had been made; `render_roof` had also ANDed the gambrel's
  two halves into one word, so an unjudged break convicted a passing pitch. **One word cannot carry
  three states for two rules.** **Sweeping for the DISPLAY half of the pattern found a THIRD
  FILE**: `proportion_engine.py`'s `show --invariants` printed FAIL for a `holds: None` -- a pack
  convicted of breaking its own invariant on the strength of a crash -- while the SELFTEST twenty
  lines below had always read `is not True` correctly. The tri-state is handled where the number is
  COMPUTED and collapsed where it is DISPLAYED, so sweep the plates and the CLIs, not the checkers.
- **A MUTATION THAT CHANGES NOTHING IS NOT EVIDENCE THAT NOTHING IS WRONG -- IT IS EVIDENCE THE
  FIXTURE IS BLIND (WP-10.1).** Four guards in this session could not fail, and two were written BY
  the audit inside the class that exists to catch that. `b["x"] == 0` **cannot fail against a
  float** (`0.0 == 0` is True) while its own comment claimed to pin the integer origin -- assert the
  TYPE, excluding `bool`. A single-pile sizing guard ran a 542 sf fixture where
  `round(542/22/10)` and `round(542/36/10)` are BOTH 2, so the rule under test made no difference to
  the answer; choose areas that straddle the rounding boundary. A hyphen-gap guard pinned a constant
  to itself rather than to the grouping file the band lives in. **And one asserted a consequence
  that does not exist**: `slice_rect` confines a room to its element, so no score can pull a
  dependency room back into the house -- `bounds=` changes the SCORE (28 points on the winning
  placement) and therefore which candidate wins, and the honest guard measures that and then reads
  the call site, which is the weaker form and says so.
- **A MOVE'S `touches` IS ENFORCED AT APPLY TIME NOW, AND THE REPORT THAT SAID IT WAS TESTED WAS
  WRONG (WP-9.4).** `apply()` diffs the record before and after, holds every written path
  against the move's declaration in the registry's spelling (`levels[].rooms[].windows[].wall`),
  and REFUSES, restoring the record, on a write outside it or one `changed` does not report.
  Before that, `touches` was an allow-list check on a string, and `add-the-grammar-door` ran the
  composer's `derive_openings` over the WHOLE plan for one door: 253 paths in 25 rooms, nine
  authored window counts among them. `derive_openings` takes `rooms=`, `doors=`, `windows=`,
  `pairs=` now and a move derives the openings it added and nothing else. **A caller-supplied
  parti is an ID, never a record**: `critique()`/`revise()` accept a record for the sweep, and
  the routes and `core.critique_plan`/`revise_plan` refuse one — a dict reached
  `geometry.py`'s `bay_module_ft` unchecked.
- **A CRITIQUE WHOSE PLACEMENT COULD NOT BE EVALUATED REPORTS THE DECLARED KEY, WHICH IS LOWER BY
  ABSENCE (WP-9.4).** No placement, no drawn findings, and `[fatal, serious, minor, faults]` falls
  — the Tidewater plan read `[0, 29, 60, 19]` unplaced against `[3, 44, 70, 19]` placed. The loop
  accepted a state with no placement after a proof timed out inside a round. `_improves` refuses
  an unjudged placement and a placed loop with an unjudged first placement does not run
  (`placement-could-not-be-evaluated`). **Any comparison of keys across a could-not-evaluate
  boundary is a comparison of two different instruments**; check `placement.could_not_evaluate`
  before reading a key as better.
- **A LEVER'S VERDICT RIDES ON THE MOVE ENTRY, NOT ONLY ON THE ROUND (WP-9.4).** `revise.py`
  wrote `refused_by_measurement` on the round and `accepted` nowhere for a lever; the summary,
  the sweep's `per_move`, the CLI and the bench's `round` event all read the move entry. An
  accepted proof counted as 0 moves applied; a proof rolled back by measurement reached the
  bench as "applied; its finding persisted". The tabu is forgotten only when the ENGINE
  changes — `search-harder` changes the candidate count and a refusal under 250 says the same
  under 1,000. `before` is a copy: on a run that accepts nothing it was `after` under a
  second name.
- **THE LITERAL DETECTOR READS SIX SHAPES NOW, AND ITS CEILING WENT UP TO SAY SO (WP-9.4).** A
  constant dict read by subscript (`SASH_FRAME["stile_in"]`, four measurements), a ternary with
  a literal branch, an `or 3` fallback, a literal inside `max(1, …)`, a literal one level down a
  `BinOp` (`4 * width`), and `0.5`/`2.0` struck off the unit-conversion exemption — none of
  them a "unit conversion". `LITERALS_CEILING` 35 -> 44 and `RATIOS_CEILING` 4 -> 7, the jump
  named in the checker's own comment. A same-commit ceiling change is how a blinded detector
  gets ratified; `tests/test_critique.py::TestTheInstrumentOnTheRealFile` names the shapes on
  the real file so the count cannot fall by the instrument going blind.
- **THE COMPOSER'S OLD `repair` ACCEPTED THE WORSE RESULT ON A NON-IMPROVING ROUND, AND FOUR
  MORE THINGS BESIDES (WP-9.2).** It parsed a ROUNDED figure out of a finding's prose (a 12.3
  ft dining room needing 12.333 never moved); its `need < width * 1.8` gate silently skipped
  any room needing more (three chamber closets at 2.1 ft needing 5.2); the minor branch's
  "needs about" made `float()` raise and `continue`; one round applied every finding's move
  from a stale list (a pantry widened twice, +72%); and there was no rollback at all. It is a
  wrapper over `build/revise.py` now, which snapshots, applies, re-judges and restores
  byte-identically. **Acceptance is a strict lexicographic improvement of `[fatal, serious,
  minor, faults present]`; a tie is a refusal.** Do not loosen it to "not worse": the
  search engine re-places the house on every declared move and a refused round on the
  heuristic is usually the engine's noise, not the move's — `widen-for-furniture` was refused
  84 of 182 times on the search and 1 in 12 under CP-SAT. Read `revision_report.rounds[].engine`
  before blaming a move.
- **THE RECLAIM AFTER THE LOOP CAN OPEN A FATAL THE LOOP REFUSED ALL DAY (WP-9.2).** The
  sweep's first run handed back `tower-villa` at `[3, 36, 46, 0] -> [4, 23, 49, 0]`: six
  rounds each refused a new fatal, then `compose.reclaim` — run once after the loop under the
  brief's area tolerance — re-placed the house and opened one. A reclaim that raises the fatal
  count is rolled back and stated (`revision_report.reclaimed.rolled_back`); the area
  discipline does not outrank the rule the rounds were held to. Anything else that runs
  AFTER the acceptance rule is outside it, and has to be held to it separately.
- **A FAULT'S EXCEPTION MATCHES THE STYLE ID EXACTLY AND NEVER ITS DESCENDANTS.** All three
  selection sites in `core.py` test `e["style"] == style`, so a licence on
  `georgian-colonial-american` never reaches `tidewater-georgian` — `porch-too-shallow-to-inhabit`
  on the Tidewater plan is not the Georgian licence failing, it is the licence never being
  consulted. `applies_to_styles` walks the chain; `exceptions[].style` does not. That is
  `oq/a-licence-matches-the-style-id-exactly-and-never-its-descendants`, unruled; do not
  "fix" it by copying exceptions down the tree.
- **XDATA IS CAPPED NEAR 16 KB PER ENTITY, AND A `revision_report` CAN BE LARGER.** The DXF
  marker carries `revision_summary` only and says the full report is not in the drawing; the
  round trip returns the declared fields the loop moved, as authored, and not the account of
  why. A plan the loop has worked does not round-trip whole through the DXF, on purpose, and
  the plate says so.
- **`critique(place=False)` IS A DIFFERENT CRITIC FROM `critique(place=True)`, AND THE
  DECLARED ONE SEES NO DRAWN FINDING.** `compose.repair` is the declared loop (0.9 s a
  critique); the placed loop on the returned candidates re-solves on every re-place move
  (0.2 s on the search, ~25 s a proof). A `placement`-class finding is decided against the
  DECLARED record before anything is called `actionable` — a stair the declared hall would
  have held is the engine's, not the record's — and a proved placement with no lever left is
  handed to the architect rather than counted as something a move could fix.

- **Module loading.** Everything in `build/` and `mcp_server/` loads siblings *by file path*
  so each script also runs standalone. That returns a fresh module per call and the loads
  nest — one `check()` used to execute plan_check 16x, geometry 8x. `build/modcache.py` now
  caches by realpath and every local `_mod`/`_load` delegates to it. **Do not reinstate a
  local loader**; `tests/test_modcache.py` counts module executions to catch it.
- **Inheritance transmits more than anyone bound, in three places.** `hybridizes_with` transmits a
  donor's whole kit (OQ 58 scoped it); a BINDING used to transmit a pack's whole rule set (OQ 49
  scoped it); and `descends_from` still transmits an ancestor's whole set of proportion packs, which
  is **OQ 51** and is the one with 3,056 instances. Read it before trusting "132 of 132 bound".
  OQ 51 is now RULED and HALF-BUILT (WP-8.2) -- a node may DECLINE a pack, and the live backlog is **215 unjudged** gaps, not the 233 published --
  so this trap is a work list rather than an unanswered question. It is still live until that list
  is worked; nothing about the mechanism has changed yet.
- **`hybridizes_with` transmits a donor's whole kit**, not the one trait the edge was drawn
  for. ~26 real merge problems surfaced this way in WP-4.2, patched node by node. A
  slot-scope allowlist would fix the class — needs a ruling before anyone spends a schema
  change on it.
- **BOTH ENGINES CHARGE DECLARED STACKING AND OVER-CAPACITY SPANS NOW (WP-7.4, OQ 95 and OQ 97
  CLOSED), AND THE WEIGHTS ARE BALANCED AGAINST EACH OTHER RATHER THAN SET SEPARATELY.**
  `geometry.STACK_W = 40.0` and `SPAN_W = 20.0`; `geometry_cp.py` carries soft mirrors of both
  in its objective block, never pins. Measured over the 14 partis that declare `stacks_over`:
  broken claims **27/49 -> 15/49**, over-capacity spans **29 -> 23** with the worst falling
  **80 -> 60 ft**, `serious` findings **703 -> 685**; the price is fatal 89 -> 90 and rooms
  below their band **17 -> 19**. **Three published refusals died on the way here and none of
  them was wrong as a measurement.** WP-6.3's byte-identical output at 100x and 10,000x was of
  a charge keyed on landing-over-stair, a pair NEITHER shipped plan declares. WP-7.1's
  level-aware generator really did leave stacking flat (26/47 -> 27/47) — moving a cut line
  moves a wall, not a room. What made a term look inert was the POOL: over 2,000 candidates
  instead of the shipped 250 at one seed, 12 tidewater candidates beat the winner's 3 broken
  claims while keeping the porch on the entrance front, at +41.3 points. **OQ 95's CP blocker
  was true of a PIN and never of a PENALTY** — a penalty creates no assumption literal and
  never enters a conflict core, so the `kind == "wall"` downgrade loop is untouched and an
  inferred stack still cannot displace an authored wall.
- **A NEW SEARCH TERM CAN BE WORSE IN THE MIDDLE OF ITS RANGE THAN AT EITHER END (WP-7.4).**
  The span term is byte-identical to no term below weight 2, and between 2 and 20 it is worse
  than both: fatal findings 89 -> 94 at weight 2, 100 at weight 10, back to 90 at 30-60. It
  perturbs the hill-climb into a worse basin long before it is strong enough to steer it into
  a better one. **A sweep that stops at "small weights are safe" ships the worst setting.**
  And the two terms are not separable: at `SPAN_W = 40` a 60 ft span over a 20 ft capacity
  costs 120 points — `entrance_score`'s fatal-tier scale — and swamped the stack term
  completely, `STACK_W = 16, SPAN_W = 40` giving output identical to the span term alone.
- **`geometry._SOLVE_CACHE` IS KEYED ON CALL ARGUMENTS, SO A SWEEP OVER A MODULE CONSTANT
  SILENTLY MEASURES THE FIRST VALUE (WP-7.4).** `STACK_W` and `SPAN_W` are module-level, and
  the cache key is (plan, parti, candidates, seed, engine, time_limit). The first weight sweep
  run came back flat at every weight INCLUDING zero, which read as "the term is inert" and was
  the same conclusion two earlier packages had drawn. Clear the cache between settings.
- **The level-aware generator is for the PLACEMENT and not for the CP HINT, and that split
  is measured (WP-7.1).** `solve_heuristic(level_aware=...)` is True everywhere except
  `geometry_cp._hint_heuristic`, which asks for the blind run. A hint's only job is to be
  REPAIRABLE and a placement's is to be right. Also: the two `snap` forms are NOT
  interchangeable — the slab branch snaps a WIDTH and a wall line below is an absolute
  position, and quietly changing one into the other moved the GROUND placement, cost CP-SAT
  its proof of `tidewater-georgian-careful` (OPTIMAL -> UNKNOWN at budget), and took an
  afternoon to find. The blind path must stay byte-identical.
- **`span_check` NEVER READ THE BEARING FLAG IT WAS HANDED, so every partition counted as a
  support (WP-7.4).** Its docstring said "clear span between consecutive bearing lines" and it
  read every wall's `position_ft`, discarding the `bearing` flag `bearing_lines()` had computed
  one call earlier — including that function's own `why: "not on the bay grid -- a partition"`.
  On the reference plan the x axis reported a worst gap of 23.37 ft over 7 lines, 4 of them
  partitions; between the 3 real bearing lines the clear span is **49.93 ft against a 20 ft
  capacity**. Corpus-wide: spans 236 -> 126, over-capacity 9 -> 20, worst 36.57 -> 60.00 ft.
  **A defect reported SMALLER than it is — the OQ 52 family wearing the safe-looking sign.**
  Both shipped reference plans now fail their own capacity loudly and that is the check
  working. Do not loosen the 20 ft capacity or `bearing_lines`' 0.75 ft tolerance to make the
  number smaller. Nothing pinned it for three packages; two tests do now.
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
- **THE FIXTURE PACKER TURNS THE CORNER NOW, AND THAT UNSHIELDED WHICH WALL IT DREW AGAINST
  (WP-7.4).** WP-7.2 made `fixture_pass` pick the wall with the longest CLEAR run because "a
  fixture refused on a wall nobody tried is a false cannot-fit", then packed everything onto
  that one wall — the same error one level up: `spec-builder-colonial`'s primary bath is 9 x 18
  ft, its four fixtures want 22 ft, its longest clear run is 17.2 ft, its other three walls
  stood empty. **And the off-wall coordinate was the room's LOW edge for all four walls**, so a
  fixture on the N wall was written at the room's south edge and one on the E wall at its west
  edge. That could not show while everything sat on one wall — they were wrong together, so
  nothing overlapped and the drawing merely put the bath on the wrong side of the room. Turning
  the corner made it 5 overlapping pairs immediately; 15 of 67 placed fixtures sit on N or E.
  **A fix that removes a shield has to look at what the shield was covering.** The corner
  reserve is crude and conservative on purpose: a newly opened wall starts past the deepest
  fixture placed anywhere in the room, which OVER-reserves, and the failure that prevents is a
  drawn collision while the failure it causes is a NAMED refusal.
- **`needs_uninterrupted_wall_ft` is a READING and the test enforces that (WP-7.4).** OQ 92
  published that exactly one furniture item states a wall run in words; five do, and the figure
  must appear in the item's own note in feet or inches or the basis test rejects it. It rejected
  a sixth of mine — `keeping-room`'s hearth at 9.0 ft from *"its chimney breast is 9 to 10 ft"*,
  a band explaining why first-period halls are wide rather than a run the hearth requires. The
  figure was withdrawn rather than the test loosened. A room stating a band, or none, is handed
  to the architect.
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
  can win while paying it. **The last two sentences of this entry used to read "the plan record
  still reads 12 x 12 and `plan_check.py` never reads `room.geometry`, so no layer of the critic
  sees it. That is OQ 54, unruled." Every clause of that was false**: OQ 54 was ruled twice, the
  second time on 26 Aug when Lucas reversed the first, and the `drawn` layer described eight
  lines above this one has read `room.geometry` since WP-6.2. The entry contradicted its own
  neighbour for three phases. **The critic now sees the SHAPE too (WP-9.1)** — the drawn layer
  holds each placed rectangle against its room's own `width_ft` floor and `proportion` band, so
  a 16 x 20 kitchen drawn 10 x 30 at the same area is a finding rather than a silence. What
  remains true, and is the reason this entry exists: the SEARCH still charges a flat 12 and
  still wins while paying it. The critic can now name what the search will still do.
- **REGISTER IS A FIRST-CLASS AXIS, NOT STYLE — RULED BY LUCAS 1 SEP 2026, NOTHING BUILT.**
  `oq/register-is-not-style`. His words: *"register is a first-class axis, not style."* Everything
  after this sentence is CONSEQUENCE drawn from that ruling, not more of it. Folk and polite are
  ONE type at two registers, not two styles, so
  register may NOT be encoded by adding style nodes: `styles/` says what a building is made of and
  looks like, register says how far up the social scale this instance sits. What follows -- the
  passage's four contradictory floors, `dining-room`'s 12 ft against the Kerr it cites, the trim
  grade and the service arrangement -- are CONSEQUENCES, not further rulings. **What is NOT ruled
  and must be before anything is built**: where register lives (plan record, brief, or a
  precondition vocabulary on the bands), how many values it takes and whether they are ordered,
  whether it conditions a band or selects between bands, and what a record says when its register
  is unknown (*unjudged is not passed* -- never quietly pick the permissive end). **The predictable
  trap, stated in the entry**: a licence to condition a band is a licence to invent, because
  "16 ft if polite, 12 ft if folk" makes two numbers where one was authored and only one has a
  source.
- **THE MODEL IS A GOOD CHECKER AND A BAD GENERATOR, AND THE STUDY SAYS WHY (WP-9.2, second
  report).** `docs/reports/wp-9.2-what-the-tradition-actually-does.md` is the study Lucas asked
  for before any more generator code -- five research passes over the treatises and the measured
  record, an adversarial sourcing pass that rated the whole "partly-sourced", and a synthesis. Its
  diagnosis, and it is Lucas's own complaint stated precisely: **"an area band plus a width band
  plus a proportion band plus adjacency edges is a good CHECKER and a bad GENERATOR, because a
  band carries no direction of causation."** Four bands over two free variables is
  under-determined and a thousand rectangles satisfy it -- **area was satisfiable at any shape, so
  area is what the generator satisfied.** The tradition never had that freedom because it never
  chose two numbers at once: four period sources (Glassie, Ware, Palladio-and-Scamozzi, Kerr) and
  the corpus's own four-caps reasoning -- which is NOT independent of the corpus -- describe a
  SEQUENCE OF COMMITMENTS
  (establishment -> storey height -> breadth from span/hearth/daylight -> pile -> hall and stair
  -> length from each room's own arithmetic -> doors -> **facade as a RESULT** -> bands as the
  TEST, never the input). **Read §6 "what must not be coded yet" before building anything from
  it**, and read the preface: the period quotations reach the tree at one remove and NO FACSIMILE
  HAS BEEN READ HERE -- strong enough to stop a rule being built, not to build one. Two of the
  study's own claims were corrected on verification and the corrections are in the preface:
  `critical_dimension` is parsed by nothing but `openings.py::stair_pass` HAND-PORTS the
  stair-hall's arithmetic while its own docstring says it has "been read by nothing" (two
  spellings of one rule, unheld); and `room-harmonic.json`'s suite rule is not unreadable, it is
  permanently UNJUDGED by `check_addresses.py` for want of a `quantity`.
- **THE CORPUS FORBADE THE SQUARE AND THE TRADITION PREFERRED IT — RULED AND EXECUTED 3 Sep 2026.**
  **Every floor is 1.0 now; 0 of 60 room records carry a `proportion` lower bound above 1.0.**
  `build/compose.py`'s `UNBANDED_PROPORTION` carries the same floor for the six types that state
  no band, named and commented rather than inline, because a literal `[1.2, 1.4]` in the composer
  would have been a 36th floor surviving the removal of 35. The CEILING is untouched and is the
  well-sourced half. **The measurement that decided it against the study's own preference: of 220
  declared rooms carrying a band across the 16 plans, 38 sat BELOW their floor and 14 of those were
  in `good-*` reference plans — a floor charge in any spelling convicts all seven good plans.**
  What follows is the reading as it stood before the ruling, kept because the argument is why:
  35 of 60 room records
  carried a `proportion` LOWER bound above 1.0 and **29 of those are NON-CIRCULATION** (35 minus the
  6 circulation rooms; the parallel study's "13 of 23 habitable" is a narrower denominator and both
  are right -- an earlier version of this line said "habitable" for the 29, which is wrong): `drawing-room`
  [1.25, 2.0], `hall` [1.3, 2.2], `parlor` [1.1, 1.45], `dining-room` [1.15, 1.8]. Mount Vernon's
  **Front Parlor is 16'9" x 16'6" = 1.015** -- the room Washington called "the best place in my
  House", and whose own FAQ says he "described the room as being 18 feet square" -- and its Dining
  Room is 15 x 17 = 1.133. Both fall BELOW their band. No period source found states a minimum room
  ratio; Palladio's seven shapes begin with the round and the square, Morris 1734 reports "the nearer
  a Room ... is to a Square, the more uniform and commodious" -- **and the audit found the
  grammatical subject of that sentence is PALLADIO, so Morris is Palladio at one remove and NOT an
  independent English witness** -- and Kerr's own recommended bedrooms are 16 square, 16x20, 20
  square, 18x24. **The floors CONVICT nothing today, but they are NOT inert -- an audit
  corrected this**: `compose.room_default_dims()` sizes every instantiated room from
  `ratio = (pr[0] + pr[1]) / 2`, so the FLOOR shapes the declared width and length of every room
  the composer makes -- it does not fail a house, it silently aims every room away from square.
  What convicts nothing is the reading side: `plo` is unpacked at `plan_check.py` 706 and 1237 and used for nothing but
  the message, both checks charge `ar > phi` alone, `geometry.shape_band()` returns the ceiling
  only, `WIDTH_W` ships at 0.0. **WP-9.4 nearly built the charge**, saw it convict both good
  reference plans and deleted it as unsupported -- the truer reason is that it is BACKWARDS, and 29
  records still told the next package to build it again **until the 3 Sep ruling removed the floors
  that were saying so. That sentence is why the ruling was worth taking rather than leaving the
  floors inert: an inert wrong number is an instruction to the next reader.** The ceiling is the well-sourced half and
  it has no floor: Morris's "the Length of no Room exceed a Double Cube" and Scamozzi 1615's same
  2:1 with its reason -- beyond two squares one gets "halls, galleries or passageways rather than
  rooms to live in" -- which makes a room over 2:1 out of CATEGORY rather than out of band, and
  makes the passage exempt BY DEFINITION rather than by a wider band.
  `oq/the-proportion-band-forbids-the-square`. **Provenance, because it decides what may be
  built:** the corpus counts and the Mount Vernon dimensions were verified here directly; the
  Morris/Scamozzi/Palladio/Kerr quotations come through ONE adversarial sourcing pass that checked
  them against reproductions and no facsimile was read -- strong enough to stop a rule being built,
  not strong enough to build one. And Wells 1998's caution travels with them: "Mount Airy is the
  only surviving colonial Virginia house to manifest a clear compositional debt to an English
  pattern book", so the Palladian shape rules are NOT rules of the American tradition.
- **THE FURNITURE CHECK NOW READS THE DRAWING, AND IT IS ONE FUNCTION WITH TWO CALLERS
  (WP-9.6 built this; WP-9.2 found it).** `plan_check.furniture_shortfalls(rt, w, l)` is the ONE
  spelling of the fit arithmetic; the room layer hands it the DECLARED width and length and the
  drawn layer hands it the PLACED rectangle. **Do not transcribe those expressions anywhere else,
  and do NOT cite `openings.required_wall_ft` as the precedent for a shared rule** -- that one is
  deliberately spelled three times, one of them JavaScript, held to one contract by
  `tests/fixtures/sheet_symbols/`; the discipline transfers, the mechanism does not.
  **The measurement that proved the blindness, and it is the cleanest in the phase: the furniture
  layer emitted exactly 137 findings over the sixteen plans WHETHER OR NOT the plan carried
  geometry.** Deterministic, `engine="heuristic"`. After WP-9.6: the drawn layer carries **86
  across-shortfalls and 69 along-shortfalls** (drawn findings 419 -> 574), and the declared
  furniture layer went 137 -> 178 from the `elif` split alone. On `auto` -- the engine that drew
  the sheet Lucas read -- the Tidewater `breakfast` room is drawn 7.0 x 27.0 and the critic now
  says *"cannot take its table, seats 4: needs 9.0 ft"*, which is his second complaint, computed
  since WP-6.2 and stated for the first time. `tests/test_furniture_drawn.py` ratchets 86/69 and
  is mutation-checked four ways. **RATCHET THE DETERMINISTIC FIGURES ONLY**: the same sweep on
  `auto` returned 130, 132 and 133 on one unchanged tree.
  The history below is kept because the defect is instructive: `plan_check.py` read
  `w, l = r.get("width_ft"), r.get("length_ft")` and nothing else. Swept over all 16 plans, not the 2
  that ship: **231 placed rooms and 73 across-fails on the DECLARED record, both deterministic.**
  The DRAWN figure **depends on the engine and the default one is not reproducible**:
  `engine="heuristic"` gives **86 drawn fails and 25 rooms (11%)** failing an item their own record
  passes, identical on three cold runs; `engine="auto"` gives **130, 132, 133** on one unchanged
  tree, because it solves 15 of 16 plans with CP-SAT and CP-SAT under a time budget is not
  deterministic under load. **An earlier version of this entry published 133 and 50 with no engine
  named, and the correction then STOPPED MID-BULLET and left the per-type block and the
  `spec-builder-colonial` illustration below as unlabelled `auto` readings -- a third pass caught
  it.** Per type, on `engine="heuristic"` (deterministic): `entry-porch` 8/16, `bedroom` **8/19**,
  `dining-room` **8/13**, `stair-hall` 7/13, `kitchen` 2/16. On `auto`, one run: `bedroom` 12/19,
  `dining-room` 11/13, `kitchen` 5/16, `closet` 8/11.
  **And the engine comparison is a finding in itself: CP-SAT, the engine that PROVES, draws about
  131 unfurnishable items where the hill-climb draws 86** -- it proves what it is told and nothing
  tells it about shape, which sits exactly opposite WP-9.4's result that the same engine change
  takes fatals 123 -> 36. **RATCHET THE DETERMINISTIC FIGURES (86 and 25), never the `auto` ones**:
  a ratchet on a number that drifts +/-3 is a build that fails for no reason. A dining table needs
  (40 + 2 x 54)/12 = 12.33 ft across; the slicer draws dining rooms 10, 11, 6 ft wide against
  records declaring 14-18. **`spec-builder-colonial`'s `bed3` is engine-dependent and the extreme
  figure is `auto`'s**: `auto` draws it **6.0 x 38.0 ft** with two closets **1.0 ft wide**;
  `heuristic` draws it 8.4 x 22.8 with closets of 6.0 and 4.0 ft. The 1 ft closet is real and it is
  drawn by the engine that PROVES. Where the check DOES fire it quotes the declared figure, so every
  shortfall in the set is understated (the OQ 52 family). Fix in the `drawn` layer — the only layer
  that may read placement (OQ 54) — as ONE function with two callers, never a second
  transcription (**and do NOT cite `openings.required_wall_ft` as the precedent for that: it is
  deliberately spelled three times, one of them JavaScript, held together by
  `tests/fixtures/sheet_symbols/`; the discipline transfers, the mechanism does not**); and ratchet -- see the corrected figures above, NOT 50/133 -- because they are the honest measure
  of whether a placement change helps. **THE "SECOND DEFECT" THIS BULLET USED TO NAME WAS NOT ONE, AND IT
  SURVIVED THREE AUDIT PASSES (corrected WP-9.6).** It said `sorted(it["footprint_in"])` "assumes
  every item rotates", turning the kitchen island `[84, 27]` sideways so a 10 ft kitchen passes at
  9.25 ft where 14.0 is needed. **False.** `sorted()` pairs the item's SHORT side with the room's
  WIDTH and its LONG side with the room's LENGTH -- that IS the paired-axis rule, already there:
  `need_short = (fw + sides*cl)/12` against `w`, `need_long = (fl + 2*min(cl,36))/12` against `l`.
  The island's long axis is checked at 13.0 ft and FIRES on `bad-03` (10x11) and `bad-04` (10x12);
  a 12x16 kitchen holds it and should. The 10 x 30 sliver is caught by the drawn PROPORTION band
  (3.0 against a 1.8 ceiling), not by furniture. **No typed orientation field is wanted** -- the
  correction removes the reason for it, and authoring one would have been the expensive half of
  the mistake. **The real defect was the `elif`**: the long axis was tested only where the short
  axis had PASSED, dropping **41 declared and 15 drawn** shortfalls the check had already
  computed. Both are independent checks now. **The sentence was re-read three times and survived;
  it died the first time anyone executed the function it described.**
  **The relation itself is right and is not the bug: furniture sets FLOORS, never sizes** (OQ 92,
  "the tail wagging the dog"). A whole-room furnishability test was tried and REFUSED with its
  number — against-wall runs summed against the room perimeter flag nothing (the kitchen's five
  appliances are 12.75 ft against an 80 ft perimeter) because perimeter is not available wall; a
  real one needs the placed openings. `docs/reports/wp-9.2-the-parti-is-not-the-type.md` §8.
- **ONE STOREY DERIVATION, AND `build/storeys.py` IS A LEAF ON PURPOSE (WP-9.6).**
  `storey-graduation.json` says *"Dimension the STOREY, not the ceiling"*, and its
  `ceiling_height_rule` (`module - part * 1.25`, `part = module/12`) inverts to give storey height
  from the ceiling a plan states. `structure.py` had always done that. `openings.py::stair_pass`
  instead wrote `storey_in = (ch + 1.0) * 12.0` beside `ch = ... or 9.0` -- **a flat twelve inches
  of floor assembly and an invented ceiling, two constants where the corpus has a derivation.**
  The deduction is NOT constant: 15.35 in at an 11 ft ceiling, 11.86 in at 8.5 ft. On
  `tidewater-georgian-careful` that was 144.0 in against 147.3 -- **20 risers against 21, two
  records of one stair in one house.** Both callers read `storeys.py` now and agree by
  construction (20/20, 17/17 at the ruled divisor; 21/21 at the old one). **It must stay a LEAF**:
  `structure.py` loads `geometry.py`, which calls `openings.stair_pass`, so openings importing
  structure closes a cycle. `structure.py` re-exports `storey_heights` and
  `STOREY_CEILING_FRACTION` under the old names.
  **Where no ceiling is stated the stair is REFUSED with a reason, never assumed** -- 0 of 16
  plans take that branch today, recorded so the refusal is not read as dead code.
  `tests/test_storeys.py` pins the transcribed fraction against the pack's own expression.
- **THE RISER DIVISOR IS READ FROM THE PACK, AND LUCAS MOVED THE PACK TO 7.5 IN (2 Sep 2026).**
  It had been a bare `7.25` in `openings.py` AND in `structure.py`, each commented with the name
  of the pack it was copied from -- so moving the pack would have moved neither, which is the
  whole shape of `oq/the-stair-run-is-spelled-three-times`.
  `build/storeys.py::riser_divisor_in` matches `storey-graduation.json`'s `stair_type` expression
  against `ceil(module / <number>)` and **REFUSES any other shape rather than falling back**; a
  test scans every file in `build/` for a stray divisor. Two data records had to move by hand and
  the second is a trap: the pack's expression, and its **baked copy** in
  `kits/georgian-colonial-american.kit.json` at `/slots/stair_type/parameters/risers_per_storey`
  (`oq/a-baked-pack-value-is-a-second-delivery-path`, met in ordinary work -- **nothing in the
  corpus would have failed had the second been missed**, and the first attempt DID miss half of
  it: the expression moved and the baked `value` beside it did not, so one object read
  `ceil(module / 7.5)` and `17` where 7.5 on its own stated 120 in module gives 16.
  `check_kits.py` came back OK and `check_addresses.py --strict` came back at its ratchet of 32
  with that defect in place -- the first `continue`s on the `value` key by design, the second
  measures a snapshot the live rule REFUSES, which is a different question. **That open question's
  own closing sentence had predicted this exact case four days earlier** and had no instance;
  it has one now. **143 baked derived parameters carry both an `expr` and a `computed_at.value`
  and exactly ONE is of a shape a narrow reader can evaluate** -- the other 142 are UNJUDGED, so
  the count of stale snapshots here is unknown, not zero. The guard added is scoped to this one
  rule on purpose; a general one is that question's to rule on). Measured: only 2 of 16 plans place a
  stair hall, `tidewater-georgian-careful` 21 -> **20 risers at 7.367 in**, `spec-builder-colonial`
  **17 unmoved at 7.092**; neither near the IRC advisory 7.75; and the pack's own 120 in default
  now gives **16 risers at exactly 7.500**, reproducing the worked example in
  `rooms/stair-hall.json`'s `critical_dimension`. **The riser count moved on both engines and NO
  CRITIC LAYER NOTICED** -- `plan_check` has no stair finding, and the pinned reference-plan counts
  are identical at both divisors. **And the ruling leaves the corpus disagreeing with itself,
  recorded in three places and reconciled in none**: that same room record's `conflict` note calls
  the historic comfortable band *"7 to 7.25 in rise"*, so the default stair now sits just outside
  a band the corpus states about itself. It is written into the pack note, the room record's own
  `conflict`, and the register entry. **Do not edit either number to make them agree** -- that is
  `oq/a-grouping-rule-and-a-room-record-can-disagree`'s class and its ruled checker's job.
  **7.5 in is NOT sourced and the ruling does not claim it is**: it is the figure the corpus
  already worked its own example at, which is consistency, not evidence.
- **A MUTATION THAT SILENTLY DOES NOT APPLY LOOKS EXACTLY LIKE A GUARD THAT WORKS (WP-9.6).**
  Mutation-checking the baked-value guard, the replacement matched an EARLIER occurrence of the
  same snippet in a 6,000-line kit file and never touched the parameter under test; the suite
  stayed green and read as "the guard is fine". It is the family this repo keeps meeting -- a
  negative assertion whose selector broke, a `class="ch"` pin that stopped matching -- wearing
  the tester's own clothes. **Assert the mutation LANDED** (count the match, or read the value
  back) before believing the colour. Re-run anchored, the guard went red both ways.
- **A FIGURE FROM A HYPOTHETICAL INPUT IS NOT A MEASUREMENT, AND THE CAVEAT FALLS OFF (WP-9.6).**
  The finding above was first published as "16 / 17 / 21 risers, 3.3 ft apart, because openings
  falls back to a hardcoded 9.0". **Every number in that was wrong.** The 17 came from feeding
  `stair_pass` a 9 ft ceiling BY HAND -- the prose's own worked example -- on a plan that declares
  11. The audit that produced it said "fed the prose's own input" and was honest; **the next pass
  quoted the number without that clause**, and it then travelled into a commit message, this file
  and a register entry as though measured. The gap is 3.3 INCHES of floor assembly, out by a
  factor of twelve, and the `or 9.0` fallback fired on no shipped plan at all. **A caveat that
  survives one paragraph and then drops is worse than none**, because downstream the figure looks
  measured. It was caught by running the function, which is the only thing that has ever caught
  one of these.
- **A LOCAL NAMED `top` OVERWROTE THE SHEET'S TOP MARGIN, AND A THIRD OF THE UPPER FLOOR WAS
  NOT DRAWN (WP-9.6).** `render_plan.render()` computes `top` once, uses it for `total_h` AND for
  `oy = top + extra_top` inside the level loop -- and the room-label block then did
  `top = cy - block/2`. The first plate was placed from the real margin and every plate after it
  from wherever the last room's label began. On `tidewater-georgian-careful` at `engine="auto"`:
  ground plate y=134, **upper plate y=378.2, running to y=658 on a canvas sized 498** -- 160 px
  outside the viewBox, not drawn, and the levels no longer aligned. It is `label_top` now.
  **Eight lines below that assignment sits a paragraph about an inner loop rebinding `i` in the
  same block** -- someone found and fixed that one and did not see this one. **Lucas found it by
  looking at the sheet; nothing in the suite could.** `tests/test_sheet_canvas.py` holds two
  guards and THEIR SENSITIVITIES DIFFER, which is written down because a reader will assume
  otherwise: the plate-alignment test catches this bug (red on the revert), the
  no-rect-leaves-the-canvas test does NOT on `heuristic` (~18 px of drift, inside the sheet's
  84 px of bottom padding) and fires only past that padding. Both are kept because they fail on
  different mutations.
- **THE CITATION GUARD VALIDATES 16% OF THE NAMED NAMESPACE, BY TWO MECHANISMS, AND THE SECOND
  IS BIGGER THAN THE FIRST (WP-9.2 audit, corrected by a later pass).** **The second one first,
  because two audit passes missed it and it GROWS.** `check_citations.py` does not scan the tree:
  `tracked_files()` is `git grep --untracked -lE "OQ [0-9]+"`, so **a file carrying no NUMBERED
  citation is never opened and nothing in it is checked in any context, plain prose included**.
  Mutation-tested: the identical dangling slug in PLAIN PROSE is caught in
  `wp-9.2-the-parti-is-not-the-type.md` and passes SILENTLY in
  `oq-the-proportion-band-forbids-the-square.md`, `oq-the-parti-dissolved-its-own-dependencies.md`
  and `oq-the-passage-is-divided-and-the-corpus-has-no-word-for-it.md` -- three question files this
  session authored. Eleven files are never opened; **eight are entries in the register itself**.
  **And the numbers froze at 99, so a question raised today has no reason to carry an `OQ <n>` at
  all: every new named entry is born outside the guard and the validated share falls with each
  one.** Measured with the checker's own `tracked_files`/`CODE`/`SLUG_CITE`, excluding the
  generated index: **164 mentions = 26 VALIDATED (15.9%), 120 hidden by the code-span exemption,
  15 in never-opened files (9 of them plain prose), 3 in `SPECIMEN`. Unguarded 82.3%.**
  **RE-MEASURE rather than quote these**: every one has moved in every pass that touched the entry,
  and the entry carries the fifteen-line recipe. An earlier
  version of this entry said "two thirds" and "56 in plain prose (checked)"; 26 of those 56 are
  checked. **The fix is not the one the question first proposed**: checking code spans leaves the
  9 prose citations unread and the count climbing, so `tracked_files()` must select on the slug
  pattern too -- one regex, and the cheaper half.
- **AND THE FIRST MECHANISM, WHICH IS STILL REAL: A SLUG IN A CODE SPAN IS NOT CHECKED.**
  `check_citations.py` blanks inline code spans before scanning -- deliberately, so a document can
  write `OQ 82 and 84` to illustrate a bug. **That exemption was written for the NUMBERED namespace
  where prose is the citation form; for slugs the convention is inverted** and
  `` `oq/the-raw-kit-read` `` in backticks IS how this corpus cites a named question. **120 of the
  164 mentions this tree, on the buckets above.** The count MOVES as documents discuss it -- it was
  100 at `025329c` and 113 at `84314fa` -- because every document describing the problem writes
  more slugs in backticks, the finding demonstrating itself, most recently in the correction that
  produced this sentence. **QUOTE ONE DENOMINATOR.** Earlier versions of this bullet published a
  TREE-WIDE walk (126/56/182) beside the checker's own (121/26/165); the difference is almost
  entirely `docs/open-questions.md`, the GENERATED index, which carries 19 mentions and which
  `tracked_files()` excludes by name. The checker's denominator is the one that answers the
  question, because the question is about the checker. Mutation-tested -- a fake slug in prose is
  caught in an opened file, the same fake slug in backticks passes silently. **Do not just delete
  the exemption**: of the 120, 12 name no entry and all are deliberate --
  `oq/no-such-question` is this checker's own test fixture, `oq/span-partial-bearing-wall` is the
  illustrative slug `oq-two-id-namespaces` uses to explain the scheme, and the placeholder below
  accounts for the rest. The blind spot is load-bearing, which is why this is a question and not a
  patch. **And the entry's own proposed fix contained the bug**:
  it offered a slug-shaped placeholder as a safe illustration form, and `SLUG_CITE`
  (`\boq/[a-z0-9][a-z0-9-]*`) matches any such thing exactly. Only a form the character class
  cannot match is safe -- `oq/<slug>` is, because `<` is outside it. **This entry deliberately does
  not repeat the offending string**, because writing it here would raise the unchecked count by one
  in the paragraph reporting the unchecked count.
  `oq/a-slug-in-a-code-span-is-not-checked`. Nothing is dangling today; the guard would not notice
  if it were.
- **A GROUPING RULE AND A ROOM RECORD CAN DISAGREE, AND `check_grouping_rules.py` COUNTS THE
  CLASS NOW (WP-9.2 audit found it; WP-9.7 built the checker).** `check_addresses.py` polices
  pack-vs-pack and kit-vs-pack at one address and **does not see groupings, room bands or fault
  tests at all**, so `build/check_grouping_rules.py` holds a grouping's `internal_rules` against
  the room record it constrains and against a grouping some parti carries alongside it. The join
  is an authored `measures` object on all 26 tested rules of the 84 -- **no grouping test name
  matches any room band key**, so `piazza_depth_ft` has to be TOLD it means that record's
  `width_ft`. Live: **3 band disagreements, 2 co-carried, 22 rules and 35 prose figures COULD NOT
  BE COMPARED**, all ratcheted, plus a `compared` FLOOR because deleting an annotation makes every
  ceiling look better. Report:
  `docs/reports/wp-9.7-the-checker-that-must-not-say-agrees.md`.
  **THE RULING'S OWN SCOPE CLAIM WAS WRONG AND THE MEASUREMENT IS THE ENTRY'S MAIN LESSON**: the
  register said the checker catches five of the six, and it catches THREE -- the passage's figure
  was in prose (authored into a test by WP-9.7, and it then surfaces), the keeping room is
  internal, and **the sleeping porch REPORTS AGREES**, because the rule's 8 and the band's floor
  of 8 coincide exactly while the record's real floor is conditional prose. A green tick on a
  recorded contradiction is worse than a miss, which is why the checker carries a prose meter at
  all. Two more counts moved: the ridge pair is **two** co-carried pairs (`five-part-palladian`
  carries `georgian-service-core` alongside both hyphen groupings) and the keeping room is
  **three** statements, not two -- `rooms/keeping-room.json` says the radiant reach "IS 10 FT"
  beside the grouping's 12 and its test's 14, found by a machine on the first run of a checker
  after the entry had been audited twice.
  **`quantity` is inside `measures` rather than beside it, deliberately**: the ridge pair measures
  a building-level ratio with no room and no band, so a `{room, band}`-only field would have lost
  it. And the pack `units` enum was NOT widened -- it is closed at in/parts/modules/ratio/count,
  761 rules depend on it, and room bands are in feet, so the grouping layer got its own.
  The six instances as first found, all pre-existing, all by hand:
  the passage (**seven statements across five files spanning 3.0 to 10 ft**, and
  `passage-that-is-a-corridor`'s own note contradicting its own unconditional test -- the sharpest
  being `room-vernacular.json`'s rule 8, which carries `quantity: passage_clear_width`, states
  `range: [36.0, 120.0]` in, and has an `authority_note` in the same object saying 6 to 12 ft; its
  ceiling of 10 ft is exactly the Georgian kit's floor); **the piazza**, where `piazza-and-single-house-core`
  demands `piazza_depth_ft at-least 10` HARD while `rooms/piazza.json` bands [8,14] and cites
  *"the measured Charleston piazzas run 8 to 12 ft"* -- so a 9 ft piazza is inside the band, inside
  the cited measurement, and fails a hard rule; **the bedroom**, where the grouping says at-least
  10, the band floor is 11 and the record's own prose says the ABSOLUTE floor is 9 -- on
  `secondary-bedroom-cluster`, which **14 partis carry, more than any other**; the sleeping porch,
  where an unconditional at-least 8 meets a record whose floor is conditional ("NINE FEET IF THE
  BED RUNS ACROSS, seven if it runs along"); **the keeping room, whose own prose and own test
  disagree with no second record involved** (`keeping-room-hearth-cluster` explains why 12 ft is
  the radiant reach of an open hearth and then tests `hearth_to_far_wall_ft at-most 14`); and the
  ridge pair under two names.
  `oq/a-grouping-rule-and-a-room-record-can-disagree`. **The WP-9.2 report originally called the
  ridge pair "the first instance found in it" -- extending the method found three more in twenty
  minutes, and auditing THAT found two more**, which is WP-8.6's lesson applied twice to the same
  report. Nobody knows the true count because nothing counts them.
  **Do not reconcile any of them by picking the stricter or the looser number to make a checker
  green**: three have a source on one side only and it is not consistently the same
  side, and at least one is a conditional floor with no axis to be conditional on, which is
  `oq/register-is-not-style`'s first customer. The three band disagreements are the DELIVERABLE
  and their ratchet is not a debt to pay down; nor are the 22 uncomparable, which are mostly
  correct and permanent -- a building-level quantity has no band to be held against, and binding
  one to a band it does not mean would be the OQ 48 error in a new place.
  **The prose meter is a crude regex that says so, and the way to lower it is to AUTHOR a figure
  into a test, never to tighten the regex until the number looks better.** Its first version
  scanned digits with any unit, returned 50 figures of which ~45 were inch-steps inside an
  arithmetic derivation, and missed the sleeping porch's NINE FEET because it is spelled in
  WORDS -- the single case it exists for. Four different jobs share one syntax in that prose (a
  governing floor, a reasoned two-tier statement, an arithmetic step, a cited measurement of the
  historical population), which is why the residue is a question rather than a patch:
  `oq/a-room-records-prose-states-a-floor-its-own-band-does-not`.
- **THE FOOTPRINT'S AREA IS A PURE FUNCTION OF THE PROGRAM'S AREA, AND ADDING A BAY IS
  AREA-NEUTRAL (WP-9.2 audit).** `derive_footprint` sets `need = max(ground area, upper area)` from
  the rooms' own declared `_area`, then loops `W = bays * bay; H = need / W`. **Because H is DERIVED
  from need, every bay count gives the same area** -- measured 2,405.0 sf at 4, 5, 6, 7, 8, 9 and
  10 bays on the Tidewater plan, identical to a tenth of a square foot. The loop trades DEPTH for
  WIDTH and cannot make a house bigger; its exit condition is a DEPTH test
  (`H <= depth_for(W) * 1.18`), so shape has no vote in the sizing at all. On that plan it did not
  run (`grown: []`, `slack: -0.2 sf`): 2,405 sf of declared program in a 2,405 sf footprint, with
  no allowance for walls -- the placed rectangles tile 97.6% of it. **This is the mechanical root of the slivers in the PLACER.** An audit corrected the
  sweeping version of this claim: `compose.repair()` DOES widen a room's declared `width_ft` on a
  furniture finding (`need + 0.2`) and on a width-floor finding, and since `need` is the sum of the
  rooms' `_area`, that grows the footprint on the next pass. The lever exists in the COMPOSER, not
  the placer -- **and it reads furniture findings computed from the DECLARED record, so it widens
  rooms that were already adequate and never sees the one drawn as a sliver.** Flagged rather than called a defect: the loop's own comment says *"grow the footprint
  before compromising a room -- the stated infeasibility ordering"* (decision #11, settled and not
  to be reopened), and the loop grows the WIDTH at constant area and never the area. A reader who
  takes that comment at face value will believe the generator has a lever it does not have.
- **THE PARTI IS NOT THE TYPE, AND NO SCORE TERM CAN FIX THAT (WP-9.2).**
  `centre-passage-double-pile` names eleven enclosed ground rooms and a porch; **its own three
  named exemplars have six enclosed spaces EACH WHERE THE COUNT IS ESTABLISHED, which is two of
  the three** — Gunston Hall's six are enumerated by HABS VA-141 and Drayton Hall's six are named
  in SC-377; **Hammond-Harwood's is NOT established here** and is a five-part scheme whose main
  block is not comparable to a bare double pile without care. An earlier version of this line said
  "apiece" of all three. Drayton Hall 70'-5" x 52'-2" (HABS SC-377),
  Gunston Hall 60'-10" x 40'-11½" (VA-141), Hammond-Harwood **49 ft wide on the house's own institution's
  figure** (MD-251's 1940 "approximately 44x42'" is an approximation and is low). The placed
  Tidewater plan is 60.0 x 40.0 ft of ROOM EXTENT with no wall thickness, against Gunston Hall's
  60'-10" x 40'-11½" EXTERIOR FOUNDATION over two-foot walls — **a clear extent about 3 ft larger
  on each dimension, and 2,400 sf of clear area against 2,100-2,195, 9 to 14% more** (an earlier
  version of this line said "within a foot on both dimensions", comparing an exterior figure to a
  wall-less model) — and
  puts TWELVE enclosed spaces in it. The envelope is right and the subdivision is not. Six of the
  parti's eleven rooms are service, and all three exemplars house their service in a basement, an
  outbuilding or a wing. **Area was never the binding constraint** (the ground program's own bands
  sum to 1,376-4,402 sf against a 2,400 sf floor); every sliver Lucas named is a room INSIDE its
  area band and OUTSIDE its width or proportion band — the kitchen at 10 x 30 = 300 sf sits inside
  its 120-340 band while standing 67% over its proportion ceiling of 1.8. That is why WP-9.4's
  sweeps moved nothing: **you cannot score your way out of a program that does not fit the type,
  and a stated macro-tree would arrange the wrong twelve rooms more tidily.** The corpus states the
  answer three times and can act on none of them — `four-over-four`'s `expansion_logic`
  ("flanking dependencies connected by hyphens ... growth must respect the axis or the whole logic
  fails") has a counter, an HTML dump and an API echo for readers; `grows_by` has ONE reader,
  `core.py:1364`, echoing it; `structural_logic` has **zero**. The generator's only growth mode is
  widening. `partis/five-part-palladian.json` already does it correctly, with two
  `gallery-corridor` hyphens and the whole service program beyond them.
  `oq/the-parti-dissolved-its-own-dependencies`, and read
  `docs/reports/wp-9.2-the-parti-is-not-the-type.md` before proposing a placement change here.
- **WP-9.5 AUDITED WP-9.1 AND WP-9.2 AND FOUND 8 BLOCKING DEFECTS, ALL IN THIS SESSION'S OWN WORK
  AND FOUR OF THEM IN CORRECTIONS IT HAD ALREADY MADE.**
  `docs/reports/wp-9.5-the-corrections-that-were-themselves-wrong.md`, and the one to read first before trusting a
  number WP-9.1 or WP-9.2 published. **The technique that found every one of them: RE-DERIVE THE
  NUMBER, DO NOT RE-READ THE SENTENCE.** Not one blocking finding came from reading. A first fix
  that is itself wrong, and a fix applied in one file and not its neighbour, were the two commonest
  shapes -- so after correcting a figure, SWEEP EVERY FILE for the retired one.
- **THE HABS WRITTEN DATA IS TEXT AT `tile.loc.gov` (WP-9.2) -- and that loc.gov is reachable at
  all was ALREADY RULED, `oq/fetching-through-a-tier-the-proxy-denies`, 31 Aug 2026, the day
  before. WP-9.2 re-derived it, which is precisely what that entry says it exists to prevent.
  Read the register before announcing a route.**
  The plain proxy still answers 403 to CONNECT for www.loc.gov (that is WP-4.4's block and it
  stands), but `mcp__Tavily__tavily_extract` reaches
  `https://tile.loc.gov/storage-services/master/pnp/habshaer/<st>/<st>NN00/<item>/data/<item>data.pdf`
  and those PDFs carry overall dimensions, room-by-room plan descriptions, structural systems and
  fenestration counts as extractable prose. `va0433` Gunston Hall, `sc0132` Drayton Hall,
  `md0035` Hammond-Harwood, `va0313` Shirley. **One extract does not return the whole document** --
  re-query the same URL with a different `query` and a different span comes back, so an agent that
  queries once and reports "the survey does not say" is wrong. This does NOT close OQ 7-11 or
  OQ 18's source half: those need legible FACSIMILES and this is prose about the plates.
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
  SUBSTITUTES for the primary on a matching style. OQ 84 and OQ 79 guarded the first two; Second
  Empire's bounds_test `dormer_count / bay_count == 1.0` then convicted a house stating NO dormers
  the moment WP-5.13 began supplying that zero, and `craftsman`'s `dormer_count at-most 1` acquitted
  one. Neither reference plan is Second Empire or Craftsman, so 1,018 green tests saw nothing —
  it took sweeping all 164 styles with one plan's measurements. **Guarding a fault means all three
  locations**, and `tests/test_measurement_honesty.py` now enumerates them so a future pass has
  something to check against.
- **Verifying a corpus-wide change on the plans that happen to ship is verifying it on 2 of 164
  styles.** Three separate defects in WP-5.13/5.10 were invisible to both reference plans and fell
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
  tests evaluating. Closed at OQ 84 by taking the measurement the fault's own note always asked
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
  by DRAWING the stack from grade for one revision. Each record is right on its own. OQ 85 closed
  it: the bay a stack stands on is `blind`, no opening at either storey, and
  `window-on-the-chimney-axis` catches the collision where a record states both. The generator
  publishes `count_of_openings_on_the_axis_of_a_chimney_stack` as a MEASURED zero — it resolved a
  collision, it did not fail to have one.
- **A node's own MEASURED parameter can contradict a pack rule at the same address, and OQ 48's
  checker could not see it.** The kit writes `projection_in`; a pack writes dimension `projection`;
  the two never meet under one name. `tidewater-georgian` authored its brick sill at **0–1 in
  measured** while `sash-light` delivered **2.25 in "sloped about 1 in 6"** to the same slot — in a
  node whose kit FORBIDS the sloped sill and says why. `check_addresses.py` gained `kit_vs_pack()`
  and the first measurement was **62** (OQ 86) -- **and that figure described a per-FILE check wearing a per-node name**. `kit_vs_pack` read `load_kit(nid)`, the node's own file, while the rule that contradicts the parameter arrives through the cascade; reading the resolved kit takes it to **1,231, ratcheted, with 1,562 unjudged**. The jump is the instrument, not a regression. **And the
  rule reaches a node TWICE** — live through `eval_packs`, and baked into an ancestor's kit file as
  an authored parameter carrying `source: <pack>`. Scoping the binding (`slots_except`, new) closes
  one path only; the other is closed at the child.
- **AN EXCEPTION IS A LICENCE AND ITS OWN CONDITION IS READ NOW (WP-8.4).**
  `exceptions[].granted_when` — 331 records — was called `applies_when`, which is ALSO the name
  of the test-level precondition on MEASUREMENTS in the same schema, and that collision is why
  nothing read it for a year. Three verdicts, never a bool: `granted` / `refused` / `unjudged`.
  Where an exception carries a `bounds_test` (which REPLACES the primary test) and its
  precondition cannot be resolved, **both rules are run and compared** — the fault is unjudged
  only where they disagree. `granted_when.construction` resolves through
  `build/construction_vocabulary.py`, a CLOSED table: an agent needing a token that is missing
  REPORTS the gap. `regions` is deliberately not evaluated (78 of 79 uses name a region
  containing the style's own) and `date_range` only where a caller supplies a date; both counts
  are ratcheted rather than assumed harmless. `applies_when` still means two different things
  across three schemas — `oq/applies-when-means-two-things`.
- **A SUBSTRING TEST OVER A SURFACE CANNOT ANSWER A QUESTION ABOUT AN ASSEMBLY (WP-8.4).**
  OQ 88's first fix classified a node masonry/frame by matching `"brick"`, `"stone"`,
  `"stucco"`, `"tile"` in its canonical cladding ids. Measured against each node's own
  `construction_type` it was wrong on 13 of 164 styles in both directions: `cape-dutch` is
  `sun-dried-brick-or-rubble-masonry` with braced timber frame FORBIDDEN and clad
  `lime-plaster-limewash-white`, which contains no masonry word — so the frame-wall sill rule
  was delivered to a mass masonry wall, **OQ 88's own bug surviving inside OQ 88's fix**. The
  vocabulary reads `construction_type` FIRST and falls back to cladding only when that slot
  cannot decide, and **a canonical outranks a permitted**: `jeffersonian-classicism` inherits a
  construction_type where everything is merely permitted and is canonically Flemish-bond brick
  with clapboard forbidden.
- **A GUARD CAN NAME THE FUNCTION IT DOES NOT REACH, AND THIS IS THE THIRD INSTANCE.**
  `proportion_engine.evaluate()` rebuilds each rule row key-by-key and its own comment says
  *"tests/test_wp46_packs.py compares this dict against the schema so it cannot recur."* No such
  test existed; the one that does reads `mcp_server/core.py`'s `RULE_KEYS`, a DIFFERENT rebuild
  one layer out. A new rule field was dropped there exactly as described, and the scope built on
  it refused **0 of 293 deliveries with every check green**. Both rebuilds are pinned now, the
  engine's by reading a REAL EMITTED ROW rather than its source — a key present in the literal
  and overwritten below would still pass a source-reading test.
- **THE ELEVATION READ THE RAW KIT FOR TWO SLOTS UNDER A COMMENT NAMING ONE OF THEM (WP-8.4).**
  `build/elevation.py`'s cascade block says *"the CASCADED dormer slot, not the raw one.
  `tidewater-georgian` binds this slot EMPTY — exactly as it binds `shutter`"* and then read
  `shutter` off `C["kits"]` two lines below. `jeffersonian-classicism`'s raw kit says shutters
  are carried and its CASCADE makes `none` canonical, so `shutter-on-an-unshutterable-opening`
  came back CLEAR on two shutters the style declines — OQ 89's own defect, surviving on the one
  node where the two records disagree. `window_head_masonry` was worse: EMPTY in the raw kit on
  **66 of 164 styles**, so the head radius reached 8 styles and now reaches 29.
- **`open` does not mean open.** `resolve_slots` stops its walk only on `specified` or `forbidden`,
  so a slot bound `open` — the style declining to constrain it — inherits its nearest ancestor's
  record in full. `colonial-revival`'s `dormer` was `open`, and resolved from
  `english-cottage-vernacular` with a thatch dormer canonical and **`boxed-dormer` forbidden**: the
  style could not declare the only dormer it is built with. That instance is bound now; the
  mechanism is OQ 87 and reaches all 97 slots.
- **A pack rule may now be OUT OF SCOPE for a building, and the reading lives in ONE place.**
  `derived_rules` carries a `scope` (OQ 88, closed) and `proportion_engine.rule_scope()` decides it,
  beside the numeric `calibrated_for`/`out_of_calibration()` it is modelled on — a reader looking
  for "when does a rule not apply" should find both together, and **nothing may re-derive "is this
  a brick house" anywhere else**; `resolve_kit.scope_facts()` is the one reader of the kit.
  `eval_packs` drops an out-of-scope rule and RECORDS why. **Three answers, not two, and the third
  is the point**: 13 styles the sill rule reaches make BOTH a masonry and a frame cladding
  canonical, so their construction is a fact about the HOUSE — those are delivered with
  `scope_unjudged` attached rather than resolved or dropped. Measured: 102 deliveries dropped, 120
  flagged. **A scope may only rule on variants somebody has classified**: the first draft read
  "not in my list" as OUT and its `any_of` ids were invented from the rule's prose, matching
  nothing the corpus uses — it would have deleted `facade-gable`'s parapet rule on all twelve of
  its own nodes, silently.
- **A fault can be CLEARED by an invented constant, and `NOT_MODELLED` cannot see it.** OQ 52's
  guard polices measurements that are WITHHELD. `shutter-on-an-unshutterable-opening` returned
  clear at `passes: true` on a house whose kit forbids shutters because `total_shutter_leaves` was
  a hardcoded `2.0` — nothing withheld, something INVENTED, in `_derive_measurements`, beside real
  figures (OQ 89, closed). The fact (`shutters_carried`) had been computed 500 lines away since
  WP-5.9 and was never read. **When adding a measurement, ask what the record already knows before
  writing a literal.**
- **Supplying a withheld measurement arms every rule that presupposed it — including the ones a
  register lists as "not live today".** OQ 89 counted unguarded `bounds_test` divisions and said
  none was reachable; supplying `window_head_radius_in` made one reachable in the same change,
  returning `error: float division by zero`. It was the IDENTICAL expression to a secondary guarded
  in WP-5.10, one field over. **Withholding by a source COMMENT is not withholding**: use
  `NOT_MODELLED` (visible to the honesty test) or state the measurement and precondition the tests
  with `applies_when`.
- **The moment a record can finally STATE a zero, every rule that presupposed the thing runs on it.**
  WP-5.13 gave the plan schema `declared.dormer` with three states — key absent (could not evaluate),
  `"none"` (a measured zero), an object (a house with dormers) — and both reference houses stated
  none. `dormer-off-the-bay`'s parity secondary is `dormer_count % 2 == 1`, which had never run
  because no generator supplied the number; on the first run after they could, both were convicted
  of **"Dormers Off the Rhythm: 0 against equals 1"**. Zero dormers is not an even number of
  dormers. Fault tests now carry **`applies_when`**, a precondition on the MEASUREMENTS in the same
  shape as a test (`schema/fault.schema.json`), beside `applies_to_styles`'s precondition on the
  style; a test whose precondition fails is **not run**, not passed. **Any test whose expression
  divides by a count needs one**, or it errors on the house that has none. This closed
  `docs/elevation.md`'s own open question 1, which had asked for exactly this field after WP-3.2
  found three instances — two of those three are guarded now, and the third is OQ 84.
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
  twice in two days.** WP-5.11 deleted `TestSegTo` for pinning the control points of curves that
  had silently degenerated to straight lines — then shipped `svg_path()` with an **inverted SVG
  sweep flag**, so every one of the 245 arcs in the corpus was drawn as its own mirror about its
  chord: an ovolo as a cavetto, a torus as a hollow, on all three surfaces at once. It passed 34
  checks, 970 tests, a selftest that proved the constructions, and the browser walk, because every
  one of them interrogated the model and none asked where the ink went. Worse, four constructions
  were ALSO wrong in model space, and the two families of bug **cancelled** on about half the
  corpus — so fixing only the sweep flag would have made the drawings worse, which is
  "a fix that removes a shield is a fix that has to look at what the shield was covering" at
  corpus scale. `tests/test_drawn_geometry.py` is the guard: it reads the emitted path back
  through the W3C endpoint-to-centre rule and asserts the drawn arc is the modelled one. **Both JS copies of the sweep rule are now gone (OQ 83): `build/profiles.py` serves
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
  flush, **deleting the bed mould**. That is **OQ 78, closed 27 Aug**: the datum is detected per
  ASSEMBLY-GROUP from the pack's own evidence, in `profiles.py::axis_holds_for` and nowhere else —
  `eave_cornice()` had carried a private copy and now delegates, and `dist/orders.html` stopped
  clamping when it stopped computing geometry at all (OQ 83). Beware also
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
- **A sync generator handed to `StreamingResponse` holds an anyio threadpool token for its
  whole life**, not for the instant it produces a line. Starlette wraps a sync iterator in
  `iterate_in_threadpool`, one token per `next()`, and `jobs.events` blocked in
  `queue.get(timeout=1.0)` — so readers watching a compose contended with every sync `def`
  endpoint against a pool 40 wide for the whole application, `/api/health` included, which is
  what the platform healthcheck polls. Measured at 25 ms / 194 ms / 1021 ms of health latency
  for 8 / 48 / 80 open streams, flat after. `jobs.events` is `async` now, draining with
  `get_nowait()` and awaiting between drains; the queue stays a thread-safe `queue.Queue`
  because the compose worker puts to it from a plain thread, often before any consumer exists.
  **If you add an SSE route, its body must be an async generator** —
  `test_sse_does_not_hold_threads.py` pins it.
- **Compression must skip SSE *and* `/assets`, by PATH.** `GZipExceptSSE` in `app.py` wraps
  Starlette's gzip. THREE SSE routes go round it -- `/api/rail/messages`, `/api/jobs/*/events`
  and **`/mcp`**, which the first version missed and which survived only on a Starlette
  content-type default no requirements pin guarantees. **`/assets` goes round it for a
  different and sharper reason**: compressing the 1.19 MB bundle per request cost 569 ms at
  Starlette's default level 9 and 38 ms even at level 4, against 8 ms plain -- on the EVENT
  LOOP, because `FileResponse` streams 64 KiB chunks and Starlette only offloads at 128 KiB,
  and on a route outside both the auth gate and the rate limiter. One anonymous caller at
  1.76 req/s saturated the core. `workbench/scripts/precompress.py` writes a `.gz` at build
  time and `ImmutableStatic` serves it: 9.6 ms, better ratio, zero per-request CPU.
  **Never pass only `minimum_size` to `GZipMiddleware`** -- `compresslevel` then inherits 9,
  which is 3.5x the CPU of level 4 for 4.6% fewer bytes. **The obvious test for the SSE half
  cannot fail**: Starlette holds a streaming response uncompressed until it exceeds
  `minimum_size` and the first SSE chunk is a few dozen bytes, so asserting
  `content-encoding != gzip` on a real stream passes with the exemption deleted. Assert the
  middleware's dispatch instead.
- **Do not hand-roll a request body limit; Starlette ships `RequestBodyLimitMiddleware`.** A
  hand-rolled one here was wrong four ways, the sharpest being a 500 instead of a 413 on
  `/api/rail/messages` (it reads its body directly, so nothing converted the `ClientDisconnect`
  the middleware induced). **Register it INSIDE the auth gate.** The gate is a
  `BaseHTTPMiddleware`, which wraps `receive` in an anyio task group; the limiter answers 413
  by catching its own `_RequestBodyTooLarge`, and wrapped that way the exception surfaces as an
  `ExceptionGroup` it never matches. Outside the gate: 500 plus a traceback. Inside: a clean
  413. Both measured.
- **`copy_json` is `json.loads(json.dumps(o))`, so caching a cheap build can be slower than the
  build.** An audit cached `corpus.phylogeny()` on the argument that it was "the same bug as
  the search index, one endpoint over" and made it **7.8x slower**: the rebuild walks
  already-in-memory `core._data()` at 0.23 ms, the cached path pays 1.79 ms to copy 157 KB out.
  The endpoint costs ~20 ms end to end and the build was 1.1% of it -- the rest is FastAPI's
  encoder. `search_index()` IS worth caching (2.74 ms rebuild, re-globs 21 files) and returns
  the SHARED object with no copy. Measure before imitating a neighbouring cache.
- **An instrument that cannot fail is worse than a test that cannot fail**, because its output
  is a number rather than a green tick. `workbench/scripts/load.py` misreported three separate
  times: it timed an IDLE server at its most-loaded point (the job had finished and the streams
  had closed), it read 5.0 ms for an endpoint that costs 215 ms (it replayed one plan into
  `_SOLVE_CACHE`), and it measured the UNCOMPRESSED path throughout while being used to say
  compression was free (`urllib` sends no `Accept-Encoding`). It now refuses a point it cannot
  hold, carries a fresh plan id, and asks for gzip.
- **A caller-supplied parti id becomes a path in exactly one place: `core.load_parti`.** Three
  copies of that join existed and two were unsanitised — `core.place_plan` carried the 25 Aug
  `basename` fix and a comment claiming it covered `/api/drawings/{kind}`, which does not route
  through `place_plan` at all. Same shape as the citation grammar's three spellings. Do not add
  a fourth; `test_parti_confinement.py` scans the tree for one.
- **Benchmarking this server has two traps that both report success.** `build/geometry.py`
  keys `_SOLVE_CACHE` on `json.dumps(plan)`, so replaying one plan measures the cache —
  `/api/drawings/plan` read 5.0 ms that way against a real 215 ms, 43x out. And the heavy
  endpoints are metered at 60/hour per identity, so an unmodified sweep measures
  `limits.py`. `load.py` carries a fresh plan id per request; raise `HEAVY_CALLS_PER_HOUR`
  for the run.
- **Open questions are live**, and this line was stale for a day, which is worth knowing before
  trusting any list of them. **THE REGISTER IS A DIRECTORY** — `docs/open-questions/<nnn>-<slug>.md`
  for the frozen numbers and `docs/open-questions/oq-<slug>.md` for every question raised after
  28 Aug 2026, one file per question, filename == id, exactly as `faults/` and `rooms/` have
  always worked. `docs/open-questions.md` is a GENERATED INDEX; edit the question's own file and
  run `build/gen_open_questions.py`. It holds **145 entries, of which 60 are open**
  (7, 8, 9, 10, 11, 18, 36, 37, 38, 39, 64, 66, 67, 68, 72, 73, 74, 75, 76, 77, 79, 86, 87, 91, 92, 93, 94, 96, 98, oq/a-baked-pack-value-is-a-second-delivery-path, oq/a-child-band-replaces-an-ancestor-derivation, oq/a-daily-route-is-an-editorial-model, oq/a-declared-measurement-and-a-window-record-state-one-width-twice, oq/a-furniture-footprint-is-sometimes-one-and-sometimes-the-group, oq/a-kit-binding-propagates-to-descendants-nobody-read, oq/a-licence-conditioned-on-the-wrong-axis, oq/a-licence-matches-the-style-id-exactly-and-never-its-descendants, oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it, oq/a-massing-states-its-structure-and-nothing-reads-it, oq/a-material-neutral-assembly-decides-a-material-question, oq/a-node-that-refuses-a-category-must-decline-it-twenty-six-times, oq/a-placement-finding-is-classed-by-what-the-engine-is-for-five-kinds, oq/a-plan-does-not-name-the-parti-it-was-built-from, oq/a-room-count-cap-on-the-heavy-routes, oq/a-room-records-prose-states-a-floor-its-own-band-does-not, oq/a-round-is-accepted-on-the-key-and-not-on-the-rule-each-move-executed, oq/a-slug-in-a-code-span-is-not-checked, oq/an-at-grade-appendage-is-drawn-and-not-judged, oq/an-exterior-door-is-drawn-on-the-footprints-wall-and-not-its-rooms, oq/applies-when-means-two-things, oq/the-adjudication-cases-the-records-do-not-decide, oq/the-divergence-mark-is-in-neither-face-the-sheet-names, oq/the-massing-states-its-hearth-in-prose-and-a-substring-test-reads-it, oq/the-passage-is-divided-and-the-corpus-has-no-word-for-it, oq/the-placement-carries-no-wall-bands, oq/the-placer-places-two-levels-and-says-nothing-about-the-third, oq/the-raw-kit-read, oq/thirty-five-measurements-the-elevation-states-as-literals, oq/two-id-namespaces, oq/which-rooms-take-the-hearth).
  The tally counts every HALF CLOSED entry as open, because a half-closed
  question is an open one. **THIS SENTENCE SAID "the three HALF CLOSED entries (18, 68, 98)" AND
  THERE ARE EIGHT** -- 18, 39, 68, 91, 92, 98,
  `oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it` and
  `oq/an-exterior-door-is-drawn-on-the-footprints-wall-and-not-its-rooms` (corrected WP-11.14, by
  reading every status line rather than the sentence). It was wrong before this package and each
  reader who half-closed a question added one to the truth and none to the count: a countable
  claim about the register that `check_counts.py` does not police, because the register is not a
  corpus figure. The COUNT of open questions was right throughout -- the derived-list test holds
  that -- so nothing downstream was wrong; the enumeration beside it was decoration nobody
  checked. That list is DERIVED from the register by
  `tests/test_wp46_packs.py::test_claude_md_open_question_list_is_derived_from_the_file_not_asserted_against_a_literal`,
  which reads `build/check_ids.py`'s own reader rather than re-parsing anything -- the
  status vocabulary is spelled in ONE place. It requires the ids to be a bare
  comma-separated list on ONE line; prose inside the parentheses makes its regex match
  nothing and the assertion fires on an empty set.
  **THE NUMBERS ARE FROZEN AT 99 AND EVERY NEW QUESTION IS NAMED** — ruled 28 Aug 2026, closing
  OQ 99. A sequential id has to be issued from somewhere, and the only
  shared state two parallel sessions have is the repo they both branched from, so both read the
  highest number in THEIR copy and whoever merges second renumbers: FIVE times in four days.
  A slug is derived from the subject rather than issued, so two sessions picking one have raised
  the same question and the conflict is the one you want. `check_citations.py` refuses a numbered
  entry above 99 and `check_ids.py` refuses a numbered FILE above 99, so the old mechanism is
  unavailable rather than discouraged. The legacy numbers
  are NOT migrated and the reason is worth carrying: nothing parses an OQ id -- all 1,640
  citations are prose -- but commit messages carry the old numbers and cannot be rewritten, so a
  uniform scheme was never available and the only choice was which inconsistency to keep.
  **The two mechanisms are complementary and both are needed.** The directory makes a duplicate
  id an add/add conflict git REFUSES instead of a text conflict it merges by juxtaposition; the
  slug makes the id underivable from the working tree in the first place. The fifth collision --
  two different WP-8.1s and two different OQ 99s, 28 Aug -- landed between them.
  The tally counts every HALF CLOSED entry as open, because a half-closed question
  is an open one. That list is DERIVED from the register by
  `tests/test_wp46_packs.py::test_claude_md_open_question_list_is_derived_from_the_file_not_asserted_against_a_literal`,
  which reads `build/check_ids.py`'s own reader rather than re-parsing anything — the status
  vocabulary is spelled in ONE place now, because it used to be spelled in two,
  which also requires the ids to be a bare comma-separated list on ONE line — putting prose
  inside the parentheses makes its regex match nothing and the assertion fires on an empty set,
  which is how this line was broken and caught while writing it.
  **A THIRD PARALLEL-SESSION COLLISION LANDED 28 AUG, and it renumbered twelve.** Two sessions
  again issued from 72. **Main's 72-77 keep their numbers** — the atlas's fine coastline tier and
  the five from the infrastructure audit — because main merged first and its own reports cite
  them. **The dormer and geometry block moved by six: 72-83 are now 78-89**, and the conversion
  table is in the register. `f768c02` and `426ed35` are the two commit messages that carry the
  old numbers and cannot be changed; every reference inside the tree has been converted. Three
  collisions in three days is the procedure, not bad luck — the next session that reads the file
  and adds one will collide a fourth time. **The work-package numbers collided too and were NOT
  renumbered: there are two different WP-5.7s** (main's atlas, this branch's geometry layer), kept
  apart only by their report filenames. That is **OQ 90**, and until it is ruled, cite the report
  and never the number.
  **AND PHASE 9 THEN RAN TWICE IN PARALLEL, WHICH IS OQ 90 AT FOUR TIMES THE SCALE.** Two
  sessions each opened a Phase 9 on 1 Sep 2026 and each numbered from 9.1: one is ARRANGEMENT
  (the arbiter, the precedents, the unit of composition), the other THE CRITIQUE AND THE
  CORRECTIVE REVISIONS (the analyst, the move registry, the revision loop). **There are two
  WP-9.1s, two WP-9.2s, two WP-9.3s and two WP-9.4s**, and neither line is renumbered because
  pushed commit subjects on both branches name them. All eleven Phase 9 reports carry distinct
  slugs and coexist, which is the only reason nothing had to be renamed --
  `PLAN-OF-ACTION.md`'s Phase 9 header carries the number-to-filename table. **Cite the report
  by FILENAME.** The two lines also met in the CODE at the PR #19 / PR #20 merge, and neither
  side was dropped: `plan_check`'s findings carry the critique line's structured evidence
  (`kind=`, `need_ft=`, `axis=`) AND the arrangement line's shape and furniture checks;
  `compose.repair` is the critique line's revision loop; and the arrangement line's style-layer
  passage-floor branch was **PORTED into the move registry** as
  `passage-to-the-styles-own-floor` rather than dropped with the forty-line hill-climb that
  held it. That port is the one thing a "take main's side" resolution would have silently
  lost -- main's registry has `passage-to-its-band`, which widens to the CATALOGUE's 6 ft, and
  a Georgian kit asks for 10; the fault between them is fatal, so the loss would have shown up
  as a Tidewater Georgian brief handed to a side-hall townhouse.
  **88 and 89 came from WP-5.14's own adversarial audit: the sill scope it fixed on one node
  reaches 27 masonry nodes and two more pack rules have the same shape (88), and three
  measurements are still withheld to work around gaps `applies_when` now covers while
  `total_shutter_leaves` is supplied as an unconditional constant of 2.0 whether or not the style
  carries shutters (89).** **84 and 85 closed 27 Aug (WP-5.14) and raised 86 and 87 between them:
  86 is 62 addresses where a node's own MEASURED parameter contradicts a pack rule, which OQ 48's
  pack-versus-pack measurement could not see because the two are written under different names;
  87 is that a slot bound `open` — the style declining to constrain it — inherits its ancestor's
  constraints in full, because `resolve_slots` stops its walk only on `specified` or `forbidden`.**
  **78, 79 and 80 were WP-5.11's, about the geometry layer: the entablature's datum, two sourced
  rules disagreeing about the cornice's projection, and the front elevation that could not draw
  its own chimneys. 78 and 80 are closed — 80 by WP-5.13, which found the renderer still asserting
  in a twelve-line comment the flat-eave-line behaviour the roof layer had stopped having earlier
  in the same package, and two invented constants underneath it putting a brick bar in the sky.**
  **84 and 85 are WP-5.13's, from the dormer layer: `cornice-that-is-a-fascia`'s two rival
  secondaries, where whichever is right the other convicts the house — inert today only because
  it tests on a measurement name nothing supplies — and a gable-end-exterior stack standing on
  the centre line of a gable end whose elevation puts a window there, with no layer asking
  **A FOURTH COLLISION LANDED AT THIS MERGE, AND IT HIT THE SAME BLOCK TWICE.** The third one
  (above) moved the plan-semantics and Phase 7 questions from 72-79 to **78-85**. While that was
  being written, the dormer/geometry session was independently moving ITS twelve into **78-89**
  for the same reason, and merged first as PR #14. So 78-85 collided a second time, in the same
  file, over the same rule, four days running. **Main keeps 78-90; this branch's eight moved
  again, to 91-98**, and the register carries a fourth conversion table showing both hops.
  **A bare "OQ 78" in this branch's history is now ambiguous BY DATE** — it means one thing before
  the third collision and another after it — which is the sharpest argument yet that an id must
  not be issued from the working tree.
  **91-98 are this branch's.** OQ 91 (raised 72): two layers decide — the window grammar says a
  window's ROLE, the kit its SASH KIND, 119 of 159 styles answering *through the lineage* where
  only 39 answer in the flat kit file; the vocabulary half is merged and ratcheted and the AXIS
  half remains. OQ 92 (raised 73): furniture sizing REFUSED ("the tail wagging the dog"),
  arrangement to the rooms' own words — five wall runs, not the one the register claimed.
  **OQ 95 and OQ 97 are CLOSED by WP-7.4**: both engines charge declared stacking and over-capacity
  spans, 27/49 broken stacks -> 15/49. **OQ 98 is new from the WP-7.5 audit** — `span_check`
  still credits a bearing wall across the whole plate however short it is, and `plan_check` has
  no span finding at all.
  whether they collide.** **69, 70 and 71 were raised AND
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
  or report written before the merge still carries the old number. OQ 48, OQ 50, OQ 51 and OQ 16 closed on
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
  - **Environment-blocked, not unstarted: OQ 7, OQ 8, OQ 9, OQ 10, OQ 11**, and the source half of **OQ 18**.
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
  - **OQ 51 — RE-RULED 3 SEP 2026: FLIP TO OPT-IN NOW, and this reverses the 25 Aug ruling's
    second half.** The lineage cascade delivers packs nobody bound. Lucas's ruling of 25 Aug was
    *adjudicate first, flip second* — work the unjudged gaps, then add `inherits_packs` when
    `unendorsed` approaches zero, "at which point it is a safety net rather than a cliff that
    strands 287 gaps in one commit". **That is no longer the ruling.** Build `inherits_packs` and
    make pack inheritance opt-in NOW, accepting the stranding.
    **The one new fact that moved it is the measured cost of the alternative**: WP-8.7 read the
    backlog end to end three times and the refill is geometric — **244 → 73 → 50 → 36**, each pass
    surfacing about three quarters of the last, because declining a pack re-attributes the role to
    the next ancestor. Three passes bought `judged` 48 → 249 and left 223 unendorsed; the remainder
    is of the order of a hundred more adjudications over a dozen passes. Adjudicate-first is
    finishable, at a price that now outweighs the stranding it was preferred to.
    **Three things the ruling does NOT say**, because each is a way to over-read it: the 249
    judgments are not wasted (they are why the flip lands on a corpus a quarter of which a person
    has read); the 181 tabled cases in `oq/the-adjudication-cases-the-records-do-not-decide` stay
    open; and the flip does NOT close the second delivery path — a baked snapshot in an ancestor's
    kit file is not a cascade delivery, so `inherits_packs` cannot stop one.
    **THE FLIP MUST STRAND LOUDLY.** A node that stops receiving a pack it was silently receiving
    loses dimensions on real slots, and the failure mode is a slot reading as undimensioned rather
    than as refused — OQ 51's own silent corruption arriving from the other direction.
    **MEASURED 3 SEP 2026, AND THE NUMBER RE-RULED THE RULING.** `--stranding` sweeps all 132
    buildable nodes: gating delivery on a vouch stops **2,963 of 3,158 arrivals** and takes
    **7,830 dimensioned slots to 4,931 — 2,899 losing ALL dimensioning, 37%, over 124 of 132
    nodes**, `egyptian-revival` 65 → 1 and `tidewater-georgian` (a shipped reference plan) −17.
    The ruling had been taken on ~223, which counts ROLE GAPS and not deliveries: a factor of
    thirteen. Put back with the numbers, Lucas ruled **stage it pack by pack** and **a separate
    field, not `applies_to`** — that field already arms five live gates and 57 of the 223 gaps sit
    on them, so gating delivery there would make one endorsement mean three things.
    **THE FIRST PACK IS FLIPPED (WP-8.10, 3 Sep): `trim-classical` declares `delivery: opt-in`,
    six nodes name it in `inherits_packs`, and 10 slots over 10 nodes lost their dimensioning.**
    A pack declares `delivery: opt-in` (`schema/proportion-pack.schema.json`, indexed into
    `dist/taxonomy.json` as `_packs` so the resolver does no I/O); a node names it in
    `inherits_packs` (beside `declined_packs`, whose lie-check `check_opt_ins` mirrors exactly);
    one conditional in `resolve_packs`.
    **THE METER'S GATE IS NOT THE MECHANISM'S GATE, AND THE PUBLISHED NUMBER IS NOT WHAT A FLIP
    LANDS.** `--stranding` drops what `applies_to` does not vouch for; `resolve_packs` drops what
    `inherits_packs` does not name. On `trim-classical` that is **10 against 15** -- the five
    extra are vouched nodes, one of them `tidewater-georgian`, a shipped reference plan. Writing
    the opt-ins first is what keeps the landed cost at the measured one. On `facade-gable` the
    same gap is 32 → 33. **It is a property of the pack: measure it per pack.**
    **A STRANDED SLOT NAMES THE PACK NOW** -- `choose_pack` returns `how: "opt-in.withheld"` with
    the reason, on 2,889 of 2,889. It is tested AFTER `kit.forbidden` and that order is measured:
    testing it first relabelled `scottish-baronial.trim_family`, which binds the slot `forbidden`,
    and offered its author a remedy that would not have dimensioned the slot. Found only by the
    gap between two counters (11 reported withheld, 10 losing dimensioning), which is why the
    sweep prints both.
    **THE CEILINGS FELL WITHOUT ONE CASE BEING ADJUDICATED** -- 264/3158/223 → 258/3123/217,
    because 35 arrivals stopped. **`judged` did not move, at 249**, and that is the entire way the
    two are told apart; `--strict` prints a `withheld` line beside the three saying so. Read that
    before quoting a falling `unendorsed` as progress.
    **READ `--stranding <pack>` BEFORE FLIPPING ONE: the backlog count is a bad guide.**
    `storey-graduation` has 23 unendorsed gaps and flipping it strands **9** slots while **45**
    survive it via inherited slot-level `packs` rulings; `facade-gable` has 16 and strands **32**
    with none surviving. A staging order taken off gap counts alone picks the ineffective pack
    first. **111 slots corpus-wide survive the flip whatever it does** (179 before
    `trim-classical` flipped and took 119 of them out of the counterfactual), for that same
    reason — `choose_pack` reads the slot record's own `packs` block before the rows, and no
    mechanism about DELIVERY can reach a slot record naming a pack directly.
    **AND A CORPUS-LEVEL WRITER COUNT IS NOT A FACT ABOUT A NODE, WHICH IS HOW THIS FLIP WAS
    SOLD.** `facade-gable` was set aside as the corpus's SOLE writer of `cornice_return` (29 of
    its 32 stranded slots) and `trim-classical` preferred because `trim_family` has three writers.
    Measured per node, **zero of the ten stranded nodes have either other writer in their
    cascade** — all ten lose the only account they can reach, exactly the condition `facade-gable`
    was refused for. Size is the only real discriminator (10 / 32 / 70). It is the SAME wrong-grain
    error as `unendorsed`-for-deliveries one package earlier, and the meter had already answered
    it: `stranded` IS the per-node measure and `rehoused` is its complement.
    `oq/a-pack-can-be-the-only-writer-a-node-has` — **RULED AND CLOSED the same day: no new rule,
    stage by size.** Sole-writer status is not a precondition on flipping, because a stranded slot
    now names the pack withheld and why, so the author gets a located question instead of a silent
    wrong dimension. Order is ascending stranded count: `trim-classical` 10, **`facade-gable` 32
    (WP-8.11, flipped)**, `sash-light` 70, the five live-gate packs last. The two options refused —
    a standing sole-writer precondition, and adjudicating each pack's nodes before its flip — are
    recorded in the entry with the costs that refused them.
    **AND A FLIP REFILLS THE BACKLOG EXACTLY AS A DECLINE DOES, which is not what it was ruled
    for.** Withholding `trim-classical` from ten nodes promoted `trim-sawn` and `trim-craftsman`
    into the interior role on four of them -- four live unendorsed gaps nobody has read, created
    by the flip. The refill is a property of the CASCADE, not of adjudication: anything that stops
    a delivery hands the role to the next ancestor. Caught by `test_wp87_adjudication.py`, which
    was written for declines and needed no change to catch a flip.
    **Ten tabled cases were WITHDRAWN and not one was decided** -- the `trim-classical` section of
    `oq/the-adjudication-cases-the-records-do-not-decide` was exactly the ten stranded nodes. Kept
    verbatim under a heading saying so, because a flip is reversible and deleting them would
    destroy ten readings.
    **THE SECOND FLIP IS IN (WP-8.11): `facade-gable`, two opt-ins, 32 slots over 29 nodes.**
    The two-gate gap was 32 against 33 — `applies_to` names 14 nodes but **12 BIND the pack
    themselves**, so only `gothic-revival-american` and `queen-anne-british` are gated at all and
    only the second loses a slot. **29 of the 32 are `cornice_return`, whose only writer corpus-wide
    is this pack** — that is the ruling being exercised, not a surprise. Ratchets 258/3123/217 →
    **256/3056/215**, `FORBIDDEN_RATCHET` 761 → **723**, `STRANDING` before 7820 → **7788**,
    stranded 2889 → **2857**; `rehoused` 1980 and `dimensioned_after` 4931 both UNMOVED, the latter
    for the third package running — the end state was always this corpus.
    **`judged` is STILL 249 after two flips and 102 withheld arrivals.**
    **AND THE REFILL IS NOT FALLING: four new gaps from a ten-slot flip, THIRTEEN from a
    thirty-two-slot one** — and three of the thirteen promote `facade-classical`, one of the five
    packs whose `applies_to` arms a LIVE GATE, so a flip can hand a reader a row where ruling
    authorises a behaviour change rather than restoring a dimension. Marked ⚡ in the register.
    **A DRIVEN TEST FIXTURE MUST NAME A PACK NOBODY HAS FLIPPED**: `test_opt_in_packs.py` and
    `test_loud_stranding.py` both drove the gate through `facade-gable` precisely because the
    corpus left it on `cascade`, and flipping it would have turned every assertion into a statement
    about the shipped corpus — green, and vacuous. Both moved to `trim-craftsman` on
    `mediterranean-revival`; **check this before flipping `sash-light`.**
    And the meter had a scoping defect WP-8.10 shipped: `--stranding <pack>` printed "32 slot(s)
    over 36 node(s)" because the slot counter was scoped to the pack and the node counter was not.
    More nodes than slots is impossible for one pack, which is how it showed.
    Reports: `docs/reports/wp-8.10-the-flip-that-was-sold-on-the-wrong-count.md` and
    `docs/reports/wp-8.11-the-second-flip-and-the-fixture-that-would-have-gone-quiet.md`.
    **The meter, corrected 28 Aug 2026 (WP-8.2) and read the correction before any older figure.**
    `build/check_inheritance.py` pins three ceilings that may only go down -- **256 role_gaps**,
    **3,056 inherited_packs**, **215 unendorsed** -- and one FLOOR that may only go up,
    **judged 249** (endorsed + declined). **THE BACKLOG HAS BEEN READ END TO END THREE TIMES AND IT REFILLED EVERY TIME
    (WP-8.7, 2-3 Sep 2026)**: 367 adjudications one node at a time, **211 judged into the corpus**
    (208 declines, 3 endorsements) and **181 put to a ruling** in
    `oq/the-adjudication-cases-the-records-do-not-decide`, which carries a SECOND heading for the
    36 gaps nobody has read -- calling those cases the records cannot settle would be false.
    Declining a pack re-attributes the role to the next ancestor, so **244 read produced 73, those
    73 produced 50, and those 50 produced 36**. **THREE POINTS MAKE IT A CURVE AND THE CURVE IS
    GEOMETRIC**: each pass surfaces about three quarters of what the last one did, so the tail is
    long rather than short -- of the order of a hundred more adjudications over a dozen passes,
    each costing a reader and a check. It terminates; it does not terminate cheaply, and anyone
    costing this work from "36 left" will be wrong by a factor of three.
    **30 of the proposed data changes were overturned by an independent adversarial check**, about
    one in six, and THE RATE HAS NOT MOVED ACROSS THREE PASSES (23 of 317, then 7 of 50) -- which
    is the argument for keeping the check rather than trusting a reader who has read forty of
    these. Two of the third pass's seven were verdicts that were RIGHT resting on records that
    were FALSE (a `soft` constraint called hard; a node said to bind a pack that governs zero of
    its 64 slots), which no rate over verdicts alone would have caught.
    `appalachian-log-house` needs 26 declines over 9 rounds to reach fixpoint on its own.
    Read `oq/a-node-that-refuses-a-category-must-decline-it-twenty-six-times` before costing this
    work from the headline. **`--pair NODE PACK`** is the screen an adjudication needs: the pack's
    own stated subject beside the node's own words, then `--impact`. The published 294/3,367/233 and 293/3,366/222 were both
    wrong in the flattering direction: `measure()`'s ROLE loop lacked the `pack not in own_ids`
    guard its PACK loop had, so 39 role gaps were attributed to a delivery `resolve_packs` can
    never make -- the node binds that pack itself at chain[0] -- and the endorsement test then
    asked the wrong pack's `applies_to`, which named the node precisely because the node binds
    it. **222 unendorsed was really 249; 71 endorsed was really 38.** The floor exists because
    ten correct declines moved `unendorsed` by ZERO: each role re-attributed to the next
    unjudged ancestor. `unendorsed` is a work list, not a score. The split matters — a gap whose
    pack `applies_to` already names the node is the cascade delivering what an author INTENDED, and
    counting those 71 as faults would make the work list wrong. `--unendorsed` prints the list by
    pack, because adjudicating one pack settles every node under it: `opening-proportion` 24,
    `storey-graduation` 23, `facade-gable` 16, `trim-classical` 14, `timber-bay` 12,
    `sash-light` 11. (Re-measured 28 Aug 2026; the earlier list was the pre-WP-8.2 meter's.)
    **The accepted risk, stated because it is real:** wrong dimensions keep arriving while the
    backlog is worked. `--slots ranch-style` shows 69 of 78 dimensioned slots governed by packs it
    never bound. That is tolerable only because it is counted.

## Conventions

Commits are written in the project's own voice: what changed, what was found, and what was
deliberately not done. Findings belong in the message, not just the diff. Branch is `main`,
remote is `origin` (github.com/codex-lux/Traditional-Design-Language, private).
