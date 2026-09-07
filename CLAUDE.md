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

**AND READ `docs/reports/tidewater-layout-diagnosis-2026-09-04.md` BEFORE TOUCHING THE PLACER, THE
SHEET OR THE PARTI (4 Sep 2026).** Lucas put the bench's own Tidewater sheet in front of a session
and asked for the diagnosis before his own list. Fifty-one findings, eight root causes, four strata
(Part IX says which fixes are everybody's, the instrument's, the parti's, or the style's), and the
finding that decides the order: the plate's *"PLACEMENT PROVED (CP-SAT) AGAINST THE RECORD'S
DECLARED FACTS"* sits over a placement that set aside SIXTEEN declared exterior walls, both ends of
the passage among them, with `objective: null` -- the compositional objective never ran, so every
soft term the corpus has was inert on the engine the bench draws, and the search it refuses to draw
scores 712.6 against the proof's 835.0. **Relaxed is not proved.** The declared record is
infeasible in one rectangle because its `exterior_walls` are the exposures of a five-part house.
There is no hearth anywhere in the plan layer and no axis vocabulary anywhere in the code. The
work is `PLAN-OF-ACTION.md` Phase 11, WP-11.1 through 11.11, nothing started; three are
unblocked and the container waits on four rulings the phase recommends answers to.

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
proportion packs; 1777 still wanted, and 858 of those can never be harvested) · 14 reference plans · 26 MCP tools · **48 checks, 1,897 tests**
(plus the workbench app suite, **78** under `node --test`). Those figures were 970/36 before the
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
43, read "44 of 47 checks passed" after WP-8.9's stranding sweep against a `len(CHECKS)` of 44,
and reads "45 of 48 checks passed" after WP-11.2's plan-against-parti check, against a
`len(CHECKS)` of 45. **Two sessions each added a check and each published 44**, which is the fifth time
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
cascade delivers proportion packs nobody bound, and `ranch-style` had 69 of its 78 dimensioned slots
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

**Phase 11 — the house the sheet should have drawn — is IN PROGRESS (4–5 Sep 2026): WP-11.1
through 11.9 and 11.11 are complete; 11.10 is PART-BUILT (the container question answered and refused; its three shape terms remain).** (**This line said "11.1, 11.2 and 11.3
are complete, 11.4 through 11.11 are planned" for two days after 11.4, 11.5 and 11.6 had shipped**,
above entries describing all three — the same staleness the "READ THIS FIRST" heading records about
itself, two headings up.) Raised by Lucas against the workbench's own
sheet, with the instruction to diagnose before building; the diagnosis is
`docs/reports/tidewater-layout-diagnosis-2026-09-04.md` and all five of the phase's questions were
ruled the same day. Reports: `docs/reports/wp-11.{1,2,3,4,5,6,7,8,9}-*.md`. **Read WP-11.3's refusal
before proposing a score term for the axis**, WP-11.2's cost table before quoting any fatal count on
the Tidewater plan, and **WP-11.6's item-4 section before quoting a downgrade count on either
engine** — the number is a property of the number of massing elements the record states.
**WP-11.9's §IV sets out all twenty of the diagnosis's prose rules ROW BY ROW -- 6 already
executable, 5 executed there, 9 not done, each of the nine with the fact that would have to exist
first.** Do not propose one of the nine without reading it. **Its first draft said "seven, six and
seven" and left three rows in no bucket at all**, which is the arithmetic looking right (7+6+7=20)
while the enumeration was never done -- caught by counting the table's rows instead of re-reading
the sentence, which is WP-9.5's technique and is still the only thing that catches these.

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

- **THE DEPTH A ROOF NEEDS IS DERIVABLE FROM THE FAULT'S OWN RULE, AND DERIVING IT IS WHAT SHOWS
  IT CANNOT BE ENFORCED (WP-11.10).** `derive_footprint` bounds depth from ABOVE
  (`H <= depth_for(W) * 1.18`) and from below by NOTHING, so moving a programme into a wing makes
  the block shallower without limit -- measured, a main block of 45 x 28.89 ft convicted at 0.4066.
  **THREE FRAMINGS OF THE FIX WERE FALSIFIED IN A ROW, EACH BY MEASUREMENT AND NONE BY READING.**
  A floor at the massing's pile moves `spec-builder-colonial`, a SHIPPED plan, 30.75 → 36.0 ft --
  **262 sf of empty floor, 17.1% over programme** -- to satisfy a rule not convicting it; a pile is
  a TYPICAL depth, and reading a typical value as a hard one is what the 3 Sep ruling removed 35
  proportion floors for. `build/depth_floor.py` inverts
  `faults/truss-flattened-pitch.json`'s own test instead (a LEAF, for `storeys.py`'s reason; the
  threshold READ from the record and an AST guard failing if it appears as a constant; agrees with
  the fault's forward verdict **2–0, 14 unjudged**).
  **AND THE DERIVATION IS THE REFUSAL**: `good-05-lobby-gallery-mansion`, a `good-*` reference
  plan, is convicted FATALLY at **0.2509** by a licence naming `italianate-american` where its
  style is `italian-renaissance-revival` -- `oq/a-licence-matches-the-style-id-exactly-and-never-its-descendants`
  -- and the floor that implies is **69.31 ft against a drawn 38.64**. A cap would make a
  known-broken licence a hard constraint on the placer. Only **3 of 16** plans have a style with a
  migrated pitch at all. It is reported by the INSTRUMENT and read by nothing;
  `oq/the-depth-a-roof-needs-is-known-and-cannot-be-enforced`.
  **`spec-builder-colonial` does not PASS that fault -- it is UNJUDGED** (no migrated pitch, so no
  ridge height). I wrote "passes" and that is the collapse this corpus names first.
- **A THIRD COPY OF A SHARED READING WAS WRONG TWO WAYS ON ITS FIRST RUN (WP-11.10).**
  `_style_roof_pitch` is spelled identically in `structure.py` and `roof.py` (roof.py's comment
  says so) and `depth_floor.py` needed a third because it must stay a leaf. Mine walked
  `constraints/*.json` on `applies_to_styles` where the real one reads the constraints ON THE STYLE
  NODE, and dropped the `direction == "between"` branch -- `None` where structure returns 8.0.
  **Caught by comparing against the function it was copied from, not by reading it**; the guard is
  agreement on all 164 styles. **Do not add a fourth without extending that test.**
- **A SIGNATURE THAT LETS A CALLER SUPPLY THE WRONG NUMBER WILL BE HANDED THE WRONG NUMBER
  (WP-11.10).** `wall_height_ft` first took a list of heights and its OWN CLI passed
  `floor_to_ceiling_ft` (21 ft) where the fault's denominator wants the STOREY heights
  `storeys.py` derives (23.44) -- an 11.6% error in the direction that makes the floor look
  smaller and the house look better. It takes the PLAN now and derives them itself.
- **A TEST THAT MUTATES A TRACKED CORPUS FILE AND RESTORES IT IN A `finally` IS A DATA-LOSS BUG
  (WP-11.10).** To prove a threshold is read rather than transcribed, the first version wrote to
  `faults/truss-flattened-pitch.json` in place. **A `finally` does not run if the process is
  killed, and this session alone had two container restarts mid-run** -- leaving a corrupted
  threshold in the corpus, looking exactly like an authored change, in the file every other reader
  of that fault trusts. Redirect the module's path constant at a temp COPY instead; nothing a test
  does may write inside the repository.
- **SOLVE A RULE BOTH WAYS AND COMPARE -- IT IS THE ONLY REAL CORRECTNESS TEST FOR AN INVERSION,
  AND IT FOUND THE THIRD TEST LOCATION (WP-11.10).** The floor's first run agreed with the fault
  on 2 plans and DISAGREED on `good-03`, which the fault convicted at *"22.6 against between 33.7
  and 39.8"* -- a band in different units, because `greek-revival-american` carries an
  `exceptions[].bounds_test` that SUBSTITUTES for the primary. **A fault's tests live in three
  places and the third is the one that bites**; the floor was right about the primary and the
  primary was not the rule in force.
- **THE WP-11.6 FINDING DIGEST IS OVER EVERY FINDING, NOT ONLY THE DRAWN ONES, AND WP-11.9 SHIPPED
  RED ON IT (found by the build, 6 Sep 2026).** `test_a_one_rectangle_plan_is_UNTOUCHED_finding_
  for_finding` hashes `PC.check(q)["findings"]` ENTIRE, so a new ROOM-layer finding moves it just
  as a drawn one does. WP-11.9 was committed at about 10% of the suite at a stop hook's request
  and the run failed here **forty-nine minutes in**. **That is the mechanism working exactly as
  this file records it**: a package that commits before its build finishes learns what it broke
  from the build. Nothing was wrong with the change -- the pin's job is to make a movement
  ACCOUNTED FOR rather than accepted. Tidewater `de953067f3b99ad2 -> 70be99010403c9f3` (192 -> 208
  rows), spec Colonial `5c76fc98f526d55a -> b5b33adeb258e516` (225 -> 238), every row attributed
  in the test's own docstring.
  **TWO ROWS LEAVE BOTH PLANS AND THAT IS THE SHARPER HALF**: the two `centre-passage-core` rules
  that GAINED a test stopped being handed to a reader, and on the Tidewater record both evaluate
  and PASS, so they emit nothing at all.
  **AND THE FIRST DIFF READ "+23 -7" AND LOOKED ALARMING.** Seven of those were the hand-off
  REWORDED (`check by hand:` -> `check by hand (strong, no machine test):`), counted once as a
  removal and once as an addition. **Normalise a rewording before reading a diff, or a real
  removal hides inside the noise of a cosmetic one** -- two real removals survived the
  normalisation and they are the two that matter.
- **A PART VI IS ENUMERATION AND A PART II IS RESEARCH, AND ONLY ONE OF THEM CAN BE GENERATED
  (WP-11.11).** `build/parti_prose.py <parti-id> [--md] [--all]` reads a parti's own groupings,
  massing and room records and sorts every sentence into `executed` / `reported` / `by hand`, plus
  the prose figures no band carries. The Tidewater diagnosis's twenty-row Part VI took a session by
  hand; **for that same parti the generated table is FIFTY rows -- 24 executed, 6 reported, 20 by
  hand, 7 prose figures** -- because the hand table was a reading of ONE SHEET and caught what that
  sheet broke, while the generated one is the whole surface. `--all` prints one line per parti
  (`five-part-palladian` largest at 30/9/26, `single-cell-hall` smallest at 12 rows).
  **A ROW THAT HAS LEFT THE TABLE IS THE ONLY EVIDENCE IT IS WORTH GENERATING**: all twenty of
  this parti's room-orientation rows moved out of `by hand` at WP-11.9 (15 executed, 5 reported).
  **The prose meter is `check_grouping_rules`'s, IMPORTED**, with a source-reading test that fails
  if this file grows `re.finditer` or its own `_WORDS` -- a second crude regex is how a corpus ends
  up with two upper bounds for one question. **A rule with no test is NOT a defect**: one is a
  REPORT by ruling, several are a reader's, and WP-11.9's §IV refuses nine with reasons; a file
  calling them all debt would argue for the mechanical execution the facade ruling refused.
- **A BLIND MUTATION IS A MEASUREMENT AND IS WORTH RECORDING RATHER THAN PATCHING (WP-11.11).**
  One of six mutations left the suite green: widening `room_figures`' room filter to the whole
  corpus changes nothing, because `prose_meter`'s room population is keyed on the GROUPINGS it is
  handed, so the grouping scope already constrains it (it reaches `bedroom` and `centre-passage`,
  both named by the parti). The filter is KEPT with its reason written above it and a test pins
  the equality, whose failure message says the comment has become wrong -- so the day the meter
  grows a room-side population, the claim stops being true loudly instead of the line quietly
  starting to matter. Patching it with a test that passed for the wrong reason was the available
  alternative and is the thing this corpus keeps catching.
- **SIXTY ROOM RECORDS STATE AN ASPECT AND NOTHING READ ONE, AND THE READING IS AUTHORED RATHER
  THAN PARSED (WP-11.9).** `daylight.orientation` is on every record in `rooms/` and had ZERO
  readers -- the same shape as `structural_logic`'s zero and `grows_by`'s one. `daylight.aspect`
  is the compass reading beside each sentence, `build/compass.py` is the ONE reader, and
  `check_rooms.py` holds each `basis` against the prose it quotes. **A regex was refused and the
  reason is one layer over**: WP-11.4's `opening_width_in` searched `servicing.heat` for `NN in`
  and gave `rooms/closet.json` -- *"None required and none wanted"* -- a 30.0 in MEASURED
  fireplace opening off a sentence about a drywall hatch. Four jobs share this syntax too:
  `larder`'s governing *"NORTH, and it is not a preference"*, `terrace`'s CLIMATE-CONDITIONAL
  aspect whose two branches point opposite ways, `breezeway`'s axis of DOORS across the breeze,
  and `garage`'s *"Any"*, which is an ANSWER. **35 state an aspect, 5 hard, 25 answer with
  something that is not a compass** -- and `applies: false` is the state a two-state reader loses,
  WP-11.4's `wants_a_hearth` lesson exactly. **A CAPITALISED PREFERENCE IS STILL A PREFERENCE**:
  the library's NORTH is shouted and licensed two sentences later, so `strength: hard` is taken
  only from words like *"and it is not a preference"* and *"HARD CONSTRAINT"*.
  **The first version of the refusal check exempted the short ones by a LIST OF FIVE LITERAL
  STRINGS** -- it fitted the corpus that existed rather than stating a rule. Five notes were
  written and the exemption deleted.
- **PLAN-N IS TRUE-N UNLESS A BEARING SAYS OTHERWISE, AND THE COST IS PAID IN THE FINDING RATHER
  THAN IN THE CODE (ruled 5 Sep 2026, built WP-11.9).** The convention `render_plan.py` has
  printed as **NORTH IS UP** since WP-2.4, made a rule. `compass.assumption()` returns one sentence
  and **all 63 aspect findings carry it**, because a reader told a library faces south deserves to
  know whether the record said so or the checker assumed it; a mutation deleting it turns the suite
  red. `site.street_bearing_deg` is the bearing that says otherwise and **0 of 16 plan records
  state one** -- `oq/no-plan-record-states-its-bearing`, which names the two readings the corpus
  cannot separate and forbids defaulting a bearing (zero is not a measured north).
  **A STATED BEARING WITH NO STATED FRONT IS COULD-NOT-EVALUATE, not the S default**: taking
  `axis.DEFAULT_FRONT` there would silently turn a real house by whatever the difference happened
  to be. `SECTOR_TOL_DEG = 22.5` is editorial and decides NOTHING on an unrotated plan -- every
  face lands exactly on a cardinal -- so widening it to lower a count would be tuning the wrong
  instrument. It is also the only route to an intercardinal at all: a window's `wall` enum is
  N/E/S/W, so `NE` cannot be written on a wall and arrives only by rotation.
- **THE ASPECT CHECK IS A ROOM-LAYER CHECK, AND THAT IS WHY IT IS NOT SILENT ON 94% OF THE CORPUS
  (WP-11.9).** A window's `wall` is AUTHORED and a door's is solver output, so an aspect is a fact
  of the DECLARED record -- WP-11.4's rule, ask what a check READS. It therefore speaks on **16 of
  16** plans instead of joining `oq/fifteen-of-sixteen-plans-name-no-parti` and
  `oq/fourteen-of-sixteen-plans-name-no-massing` in speaking on one or two. Measured: **40 rooms
  take none of the light their record asks for, 23 are glazed on an aspect it rules out, and
  exactly ONE is serious** -- `good-04`'s enclosed porch is a NORTH sunroom, which
  `rooms/sunroom.json` calls a cold glass box unusable in January. **Serious and fatal are UNMOVED
  on both shipped plans**, as for WP-9.6 and WP-11.4 -- three packages running; every movement is a minor or an info and
  every one is attributed in the report's §III.
- **TWENTY-EIGHT OF EIGHTY-SIX GROUPING RULES WERE EMITTING NOTHING AT ALL (WP-11.9).** The
  grouping layer's no-test branch read `elif hard`: a hard rule with no test was handed to a human
  by name, a rule with `measures.reported_by` said so (WP-11.7) -- and **every `strong` and
  `preferred` rule with neither was silent**, which reads exactly like a rule that passed. 28 carry
  a test, 1 reports, and 57 are now named with their severity. **It was found by a test asserting
  that a split rule's untested half was named, which came back empty**, and the guard is a COUNT of
  all three states rather than an assertion about one rule -- WP-11.7's own lesson, where a removed
  serious and an added duplicate cancelled and 63 stayed 63.
- **BOTH PASSAGE VARIABLES READ THE FLATTERING WAY, IN THE FUNCTION WHOSE OWN COMMENT FORBIDS IT
  (audit, 7 Sep 2026).** `passage_ends_with_a_door` counted qualifying DOORS against a rule whose
  `measures.quantity` is `passage_ends_reached`, and accepted any threshold-class room whether or
  not it had a way out: **two doors into one porch scored 2.0, and a porch plus a LANDLOCKED
  vestibule scored 2.0** — false passes on a `hard` rule, three statements below the comment
  saying *"reporting the best would be the flattering direction, which is the OQ 52 family"*. It
  counts DISTINCT reaches now and a threshold room must itself door the outside; both driven cases
  read 1.0 and the shipped record is unmoved at 2.0. **And what it measures is a NECESSARY and not
  a sufficient condition, which is a property of the LAYER**: a door's `wall` and `position_ft` are
  solver output and only its `to` is authored, so the declared record can say a passage reaches
  outdoors twice and cannot say those reaches are at its two ENDS — which is the alignment half,
  split out at WP-11.9, untested, and named to the reader.
  **`stair_hall_opens_off_the_passage` was the same error with the opposite fix**: it took the BEST
  of several halls, so a principal stair off the passage excused a service hall reached only from
  the dining room. **`min` is not the answer either** — a service stair that does not open off the
  passage is correct in a house of this kind, and this model cannot tell one from the other. Where
  the ground-floor stair halls DISAGREE the variable is withheld and `plan_check` reports the rule
  unjudged naming the variable it could not get. Three states, not a corrected second one.
- **THE PASSAGE RULES PASS ON THE TIDEWATER RECORD, AND THAT IS THE FINDING (WP-11.9).** The
  diagnosis's B4 -- *a centre passage whose rear door read as a window* -- is a defect of the
  DRAWING: `passage_ends_with_a_door` is 2.0 and `stair_hall_opens_off_the_passage` is 1.0. A
  package assuming the record was at fault would have "fixed" a correct record. **An end counts as
  doored through a THRESHOLD ROOM as well as directly**, because that passage's front door is
  `to: porch` -- counting only `to: exterior` reports B4 against a record that does not commit it.
  **The rule was SPLIT** (count vs alignment) exactly as rule 2 was split out of the facade share,
  and the alignment half carries no test and is named to the reader, which is what stops the count
  passing from reading as the alignment passing. And *"the stair rises in the passage"* is tested
  only in its SECOND half: `openings.stair_pass` puts a stair in a `stair-hall` and nowhere else,
  so the first half is true by construction and a test of it would be an instrument that cannot
  fail.
- **A CHECKER'S FINDINGS ENTER THE COMPOSER'S FITNESS FUNCTION THE DAY THEY STOP BEING `info`, AND
  WP-11.9'S REPORT DOES NOT CONTAIN THE WORD `score` (audit, 7 Sep 2026).** The aspect findings are
  `serious`/`minor`; `compose.SCORE_LAYERS` already maps `daylight` to the 18-point `rooms` axis;
  so the composer began ranking houses on the compass the day that layer landed. **Measured: the
  rooms axis moves −3.00 of 18 on `good-05-lobby-gallery-mansion`, −2.16 on the Tidewater plan and
  0.00 on six of the sixteen** — and on a real compose at 8 candidates the WINNER is unchanged on
  both shipped briefs while the ORDER BELOW IT MOVES (`family-georgian` swaps positions 3 and 4,
  `bungalow-small` reshuffles 4 through 7). **The penalty lands hardest on the cleanest candidate**,
  because `_axis_from_layers` takes `min(per_room, credit)` and a room already carrying a finding
  absorbs the aspect finding free. Not reverted, and the argument is in
  `oq/the-composer-ranks-on-an-assumed-bearing`: it reads the DECLARED record, every candidate is
  judged under the same north, and plan-N-is-true-N is a ruling. What is unruled is that the ruling
  was taken about a CHECKER, which reports, and this is a fitness function, which decides — on a
  site fact 0 of 16 records state. **When a layer's findings are not `info`, say what they do to
  the score in the report that adds them.**
- **AND THE FIRST MEASUREMENT OF THAT SAID 0.00 EVERYWHERE, BECAUSE THE SUPPRESSION NEVER LANDED
  (audit, 7 Sep 2026).** `plan_check` reaches `compass` through its own `_load`, which delegates to
  a `modcache` imported inside that function; a harness that loads `modcache` with raw `importlib`
  gets a SECOND cache and a second module object, so monkeypatching `compass.read` there patched
  nothing and every delta read zero — indistinguishable from an inert term, and believed once.
  **Patch what the code under test is actually holding** (`PC._load("compass", ...)`), and assert
  the suppression bit before reading any delta: `tests/test_compass.py` asserts the finding count
  falls to 0 first, for exactly this reason. This is the repo's own *a mutation that silently does
  not apply looks exactly like a guard that works*, met in a measurement rather than a test.
- **A FINDING'S IDENTITY MOVES WHEN AN UNRELATED SIBLING CLEARS, AND THE FIX WAS BUILT, MEASURED
  AND REVERTED (audit, 7 Sep 2026).** `Findings.add` separates two findings of different kinds
  about one room in one layer by an insertion ORDINAL, and its docstring calls that ordinal
  *"stable for a given plan and a given checker, which is what a diff between two evaluations of
  the same record needs."* **Driven, and that sentence is false**: shrink `backhall` until its
  depth finding clears and the aspect finding beneath it, unchanged in kind, room, layer and
  statement, moves `daylight:backhall#1` → `daylight:backhall`, so the bench
  (`PlanWorkbench.jsx` diffs on `f.id`) reports a row cleared and a new one opened for a finding
  nothing touched. Six ids churned that way at WP-11.9's merge with byte-identical statements;
  472 of 1,620 ids carry an ordinal.
  **PUTTING `kind` IN THE KEY FIXES IT (472 → 395, 0 collisions) AND WAS TAKEN BACK OUT**, because
  `tests/test_critique.py::test_the_finding_id_is_unchanged_by_the_evidence_it_carries` states the
  opposite contract citing OQ 32 -- *"evidence ... must never enter it"* -- and lists `kind` among
  the evidence beside `need_ft` and `axis`. **The full build caught it**, and changing a pinned
  contract on one session's reading is the move this same audit criticised WP-11.9 for making to
  the score. It also cost citability: finding ids expressible as a `finding:<id>` citation
  **55 → 12 of 1,620**, because `ID_CHARS` excludes the colon each segment adds
  (`oq/a-finding-citation-cannot-name-a-finding`). The twelve grouping `F.add` calls KEEP the
  `kind` they gained -- it is useful and enters no id.
  `oq/a-findings-ordinal-is-not-an-identity` asks the real question: is `kind` evidence, or is it
  identity? The test does not draw the distinction and there is one -- `need_ft` moves as the plan
  moves, a kind does not.
- **A NEW FINDING KIND COSTS MORE THAN ITS CHECK, AND THE COST LANDED IN `critique._intended_move`
  (WP-11.9).** All nine aspect findings reached the critique as `architect` -- the right class,
  since rotating a house is not a move -- **carrying "the depth rule does not govern this room
  type"**, the `daylight` layer's fall-through, a true sentence about a DIFFERENT rule handed to a
  finding it was not written for. WP-11.4's *a refusal with one message for three causes* in a new
  place, arriving the moment a second kind joined that layer. **Found by running `classify` on the
  plan, not by reading the file.** When adding a finding kind, run the critique and read the `why`
  it comes back with.
- **THE PLAN LAYER HAS A FIRE NOW, AND FOURTEEN OF THE SIXTEEN PLAN RECORDS CANNOT BE JUDGED BY
  IT (WP-11.4).** `hearth` is an ARRAY on a plan room (schema **0.7.0**), `build/hearths.py` reads
  it, `render_plan.py` draws the breast as poché, and `roof.py` stands its stacks over stated flues
  instead of at the centre of each gable end -- the Tidewater stacks moved 6.2 and 8.6 ft onto real
  fires. **A HEARTH IS AUTHORED AND NEVER INFERRED**, because `rooms/bedchamber.json` says an
  unheated chamber is historically normal and *"should be said out loud rather than quietly given a
  register"*: a checker demanding a fire wherever a type usually has one invents what that sentence
  forbids. `wants_a_hearth` returns **FOUR** verdicts -- `stated` 12, `optional` 1, `none` 5,
  `unstated` 42 of 60 records -- and `none` is the one a two-state reader loses, because
  *"Historically none"* carries no fireplace word, so the centre passage would be filed `unstated`
  and hunted for a fire the corpus positively refuses it. **The 42 are not a gap**: the records
  speak two vocabularies, period rooms stating a fire and modern rooms stating ductwork, so a
  Georgian plan built from modern room types has no room-level statement about its fires at all.
  **The massing is read conservatively -- six forms, everything else refused BY NAME** (a compound
  like *"gable-end-paired or central-stack"* is a statement about a type that admits both, and
  resolving it is authoring), which is `massing_bays`' discipline and the same reason.
  **AND FOURTEEN OF SIXTEEN PLAN RECORDS STATE NO `massing` AT ALL** -- every record in
  `plans/reference/`, the seven `good-*` included -- so every massing-gated check is silent on
  87.5% of them, and two more do not say so (`plan_check.py`'s grouping `attaches_to` branch and
  its style `massing_affinities` branch). Corpus census: 3 stated, 1 absent, 15 declined, **219 unjudged of 238 rooms**.
  `oq/fourteen-of-sixteen-plans-name-no-massing`. **Do not close it by deriving the massing from
  the parti**: that would make all three checks live on a fact the author declined to state.
- **A TABLE IS NOT THE RULE, AND INTERPOLATING ONE CLAMPS AT BOTH ENDS (WP-11.4).** The
  fireplace opening came off two rows of Morris 1734's chimney table with a LINEAR interpolation
  clamped by `max(0, min(1, t))`, so every room under a 12 ft cube got 36.0 in flat and every room
  over a 22 ft cube 49.0 flat: **6.6 in too wide on a small room, 7.9 too narrow on a large one,
  and 0.3 out in the middle** where a fixture probing one point would have called the change
  cosmetic. Morris introduces the table as *"a Table of all the foregoing Proportions calculated in
  the [preceding] Manner"* -- the rule is the source and the table is its arithmetic. **Lecture VI
  Rule II is recoverable from the 1734 first edition** (`sqrt(L + B + H) / 2` in feet, the room's
  three dimensions) and reproduces both discarded anchors to a quarter inch, which is a CONSISTENCY
  CHECK and not an independent corroboration -- where those anchors came from is unrecorded, so a
  common origin cannot be excluded. **And Rule II wants a ceiling the plan STATES**
  (`floor_to_ceiling_ft`, 11 and 10 on the Tidewater plan; `build/storeys.py` has read that field
  for two packages) while the code reached for an editorial constant on every room, one function
  from the comment refusing exactly that. The three authored openings moved 46.3/43.7/41.8 ->
  42.8/41.1/39.8 and a test holds each against the rule, which is what makes an authored figure
  checkable at all. **Still `judgment: true`, and recovering the rule does not weaken that**: no
  facsimile page has been read here, and a rule read correctly out of an English treatise is still
  an English rule. **RULE I IS CORRUPT IN THE ONLY REACHABLE TEXT** (*"add the Length 1 Bo Height of
  the Room together"*), so the DEPTH keeps its two anchors and the constant records that the rule
  behind them is UNRECOVERED rather than absent -- a third state, not a gap.
- **THE ONE GATE THAT WAS COMPILED WAS THE CHEAP ONE, AND THE ROUTE VALIDATED TWICE (audit,
  7 Sep 2026; pre-existing since WP-10.1).** `app._plan_validator` compiled the plan validator at
  the door and recorded in its own docstring that `jsonschema.validate(instance, schema)` rebuilds
  it on every call — *"the `copy_json` lesson in the other direction"*. The lesson stopped at the
  door: `core.check_plan`, `core.critique_plan` and `core.revise_plan` each still called the
  uncompiled form, so **`/api/plan/evaluate` paid 4.2 ms at the gate and then 79.1 ms again inside
  `check_plan`, on the same document — 23% of the whole server's measured 338 ms bound, spent
  re-deriving a verdict it already had.** `core.validator(name)` is the one compiled spelling now
  (`_schema_error` is its reader, three call sites), `app._plan_validator` delegates to it, and
  `corpus.invalidate()` clears it — **which `test_invalidate_clears_every_cache_that_exists_and_
  not_only_the_named_ones` demanded on the first run, naming the new cache**: that guard walks
  `core`'s module dict rather than listing caches, and it is the fourth time it has earned itself.
- **AN ABSENT OPTIONAL DEPENDENCY WAS REPORTED AS A FAILURE, AND IT HAD BEEN MASKING REAL ONES
  (found 4 Sep 2026).** Three `workbench/server/tests` asserted through packages this machine does
  not have -- two import `anthropic` (not in `requirements.txt`) and one posts to an ingest route
  that answers **501 Not Implemented** without `ezdxf`, which is the CORRECT answer and not the
  422 the test is about. All three FAILED rather than skipping, so `check_all.py` reported
  `FAIL pytest workbench/server/tests` for a reason with nothing to do with the code. **That is
  the direction this corpus names as the dangerous one, and it had a measured cost**: the build
  was red anyway, which is exactly the noise that let WP-11.4's two REAL pin failures sit
  unnoticed in the same run. Every sibling that needs an optional package already used
  `pytest.importorskip` -- `test_export_cad.py` for ezdxf and ifcopenshell, `conftest.py` for
  fastapi -- so the convention existed and these three were outside it. **A red build nobody can
  act on is worse than no build**, because the next real failure arrives inside it.
- **AND THE TWO REAL FAILURES WERE WP-11.4'S, BOTH PINS DOING THEIR JOB (4 Sep 2026).** The plan
  schema version pin in `test_ingest.py` (0.6.0 against a schema at 0.7.0 -- **caught by that pin
  for the third time in two days**) and `spec-builder-colonial`'s declared minor count in
  `test_plan_validator.py` (74 -> 75, the dining room with no fire under a massing that draws
  paired end stacks). WP-11.4 measured that movement on the PLACED key and did not run either
  suite. **Both are the same root cause as the layer-map miss**: a package that commits before its
  build finishes learns what it broke from the next package's build.
- **`openings` READS THE ROOM'S OWN MASSING ELEMENT NOW, AND THE DISCLOSURE FELL FROM SIX TO FIVE
  (WP-11.6, layer 1 of 6; it is at ZERO after layer 6 -- read `not_element_aware` in the record,
  never a count written in a sentence, including this one).** `oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it` is RULED
  (4 Sep: an element has its own envelope and its own roof; the lot cap is on the BUILT EXTENT
  hyphen included; the hyphen is a THIRD ELEMENT carrying one room; the drawn layer measures
  `touches` against the room's OWN element) and **the ruling's operative half is the ORDER**:
  openings first, then structure, vertical_score, the lot cap, plan_check.drawn, export_ifc,
  measuring after each -- because an element-aware `openings` makes a dependency's windows real
  and therefore turns `structure`'s missing envelope into a DRAWN collision rather than a silent
  absence. **The check is a FALLING COUNT in `geometry_report.multi_element`**, six names down to
  none; do not remove a name until the layer it names reads the element.
  **THE OLD READING DID NOT LOSE THE DEPENDENCY'S WALLS, IT ASSERTED ONE FORTY-ONE FEET AWAY** --
  `x <= tol` is satisfied by any x at or west of 0.6, so a room at x = -41 tested as sitting on
  the main block's WEST face, which is the mechanism behind the entry's "a window drawn fourteen
  feet from the room". Measured on the reference fixture, refused dependency openings **9 -> 5**,
  and the five that remain are honest. **The join is the room's own `block` tag, NOT a room list
  on the block**: `blocks_record` writes id, role, x, y, width, depth and area and no membership,
  so a first version read `b["rooms"]`, found nothing on every plan, and left all nine refusals in
  place while reporting success.
- **`structure` IS PER ELEMENT NOW, AND THE DEPENDENCY'S OWN SPANS FAIL THE MOMENT THEY EXIST
  (WP-11.6, layer 2 of 6).** `build_section` runs `wall_lines`/`bearing_lines`/`span_check` ONCE
  PER ELEMENT over that element's own rooms at that element's own origin, tagging each wall and
  span. Measured: walls tagged `main` outside the main block **1 -> 0** (a dependency partition at
  x -23.3 on a 0-63 block), the dependency's own envelope walls **0 of 2 -> 2 of 2**, and a span
  across the gap is now IMPOSSIBLE BY CONSTRUCTION rather than filtered. **And its structure,
  judged for the first time, immediately fails** -- 27.0 and 20.07 ft against a 20 ft hand-framed
  cap. That is the ruling's own predicted shield lesson: teaching openings made its windows real,
  teaching structure makes its spans real. A one-element plan takes the same path with one element,
  so the sixteen one-rectangle records stay byte-identical by construction rather than by a branch,
  and neither grows an `element` key.
- **`vertical_score` IS ELEMENT-AWARE, AND HALF OF WHAT THE ENTRY SAID ABOUT IT WAS NEVER
  REACHABLE (WP-11.6, layer 3 of 6).** The entry's support credit -- an upper wall within 0.75 ft
  of a dependency line scoring as "continues to a wall below" -- **CANNOT FIRE**: `blocks_for` lays
  only level 0 into elements, so every upper room is inside the main block and every dependency
  line outside it, 14 ft away at the closest (the hyphen's own default gap) against a 0.75 ft
  tolerance. Measured, not reasoned, and PINNED so that if the placer ever lays an upper level into
  an element the claim becomes real. **What WAS reachable is the opposite sign**: a `stacks_over`
  claim naming a room in another element was CHARGED 40 points and told "is drawn clear of it",
  for a failure no placement could avoid -- the OQ 52 family. COULD NOT EVALUATE now, with its
  reason; `vertical_score` 114 -> 74 on the driven fixture. **The wet-stack test needed no change
  and that was measured too**: an upper bath over a kitchen that has moved into a detached
  dependency really does sit over no wet room. **The check lives in the ONE spelling** --
  `declared_stack_breaks` returns both states and `stack_breaks_only` is what a charge or a
  rejection may act on, so WP-11.5's hard rule and this charge cannot disagree about one claim.
  **And the join is the room's own `block` tag, NOT `footprint.blocks`**: `blocks_record` writes
  that list inside `write_record`, AFTER the search loop the map is used in, so a first version
  built an empty map exactly where the charge is decided.
- **THE LOT CAP IS ON THE BUILT EXTENT, AND ITS BYPASS WAS NEVER ABOUT MASSING ELEMENTS AT ALL
  (WP-11.6, layer 4 of 6; disclosure at TWO).** Ruling 2: *"the hyphen is roofed ground; a building
  whose covered area overruns its lot has overrun it"*, so the flank is `gap + width` per element
  and never width alone. `flank_sizes` is the sizing `blocks_for` already did, LIFTED OUT so the
  cap reads one spelling -- a dependency's width comes from its own rooms over a single-pile depth
  and never from `fp["W"]`, which is what makes the flank computable BEFORE the main block's bay
  count is chosen. Measured at an 80 ft lot: main block **63 -> 45 ft**, built extent
  **104 -> 86 ft**, `lot_capped` **false -> true**.
  **THE BASELINE WAS ITSELF WRONG -- THE THIRD PROBE OF SIX TO BE WRONG, AND THE SECOND TO READ A
  KEY THAT IS NOT THERE** (the structure probe read `bearing_lines_x`, which the section does not
  carry). The table published `lot_capped: null`; there is no such value, the probe had read
  `footprint.lot_capped`, and the record carries it at `geometry_report.lot_capped` as **`false`**.
  **That is worse than the `null` it was reported as**: `null` reads as a record declining to
  judge, `false` is the placer ASSERTING the lot did not constrain a house 24 ft wider than its
  lot. A false positive reported as an unjudged state -- the OQ 52 family in the instrument
  instead of in the code.
  **AND CHASING IT FOUND A SECOND BYPASS ON EVERY PLAN IN THIS CORPUS, WITH NO DEPENDENCY
  INVOLVED**: the centre-bay parity bump (`if odd_wanted and start % 2 == 0: start += 1`) never
  consulted the cap, so a lot holding six bays got a SEVEN-bay one-rectangle house, 3 ft over.
  **It had also made a named refusal unreachable** -- `bay_count_forced_even`'s own comment says
  *"today the only way here is a lot too narrow to hold the odd count"*, and the bump forced the
  count odd before the lot was consulted while both loops step by two, so `bays % 2 == 0` could
  never happen. Clamped to `lot_maxbay`; it fires for the first time (60 ft lot, six bays, 54 ft).
  **The massing's own stated minimum bay count STILL outranks the lot and that residue is
  DISCLOSED rather than capped**: `start = max(mb["min"], from_area)` does not consult `maxbay`, so
  a five-bay diagram on a lot holding four is 9 ft over -- shrinking below a diagram's own floor is
  decision #11's ordering run backwards and nobody has ruled it.
  `geometry_report.lot` answers in THREE states (no lot -> COULD NOT EVALUATE, never a fit) and its
  note names the floor, the lot's count and
  `oq/a-lot-too-narrow-for-the-diagrams-own-minimum-bay-count`. A lot the flank has already eaten
  refuses NAMING THE FLANK, because *"50 ft cannot hold two bays (18 ft)"* is absurd on its face.
- **THE CRITIC READS THE ROOM'S OWN ELEMENT NOW, AND IT IS THE LAYER WHOSE SYMPTOM HAD ALREADY
  GONE (WP-11.6, layer 5 of 6; disclosure at ONE).** `plan_check`'s landlocked test short-circuits
  at `if seated: continue` -- it runs ONLY on a room whose windows are all unplaced. Seating the
  dependency's windows at layer 1 took "reaches no exterior wall" findings from **2 to 0** while
  the `touches` arithmetic four lines below still read `fp_w`/`fp_h` and was still wrong. **A meter
  watching the FINDING would have crossed this layer off four commits early.** Drive the condition
  instead -- strip the placement from those windows and the test runs.
  **THE CONTROL IS WHAT MAKES IT A FIX RATHER THAN A LOOSENING**: `kitchen` and `breakfast` read
  `[]` against the main block and **`['S','W']`** and **`['S','E']`** against their own element,
  while `chamber2` and `stair` read `[]` on BOTH -- two false convictions removed and two true ones
  kept. A change that moved all four would have been a check switched off.
  **RULING 4'S SECOND HALF IS REACHABLE HERE RATHER THAN UNREPRODUCED** (contrast layer 3):
  `openings.faces_across_a_gap` returns `{face: neighbour_element}`, so the breakfast room's east
  wall reads *"exterior to the weather and interior to the view: they look across the gap at the
  main element"* while the kitchen's south and west faces, which look at open ground, take no such
  note. **The diagonal case is REFUSED rather than modelled, in one condition** -- a face counts
  only where the other element overlaps it on the perpendicular axis, because a block past the
  corner is yard.
  **The regression is pinned as a DIGEST over every finding's kind, room and statement**, not a
  count: both shipped plans are identical before and after, which is what `envelopes` returning
  `{}` below two elements buys. **When a symptom vanishes after you changed something else, find
  out which.**
- **`export_ifc` GETS A SLAB PER ELEMENT, AND THE FIX HAD TO BE WRITTEN WHERE IT COULD BE MEASURED
  (WP-11.6, layer 6 of 6; DISCLOSURE AT ZERO).** `ifcopenshell` is optional, absent here and absent
  in CI, so `export_ifc.py selftest` reports COULD NOT EVALUATE in every run `check_all.py` has ever
  made -- **a slab rule written inside the writer would have been "fixed" against a check that
  never runs.** `export_ifc.slab_boxes(plan, section, t_ext)` is PURE ARITHMETIC over the section
  and the blocks and only the entity emission needs the library: computed where a test can read it,
  emitted where it cannot. The defect: ONE slab per storey sized `W + 2t` on the MAIN BLOCK while
  every `IfcSpace` is placed from its room's own ABSOLUTE rectangle, so the main slab spanning
  `x[-1.29, 64.29]` left three rooms at `x[-41.0, -14.0]` over nothing -- **3 -> 0**. **The
  single-slab baseline is reconstructed as a test of its own**, so the pair has something to be
  measured against rather than being one number standing alone. A dependency gets a GROUND slab and
  no upper one, which is the building rather than an omission (`blocks_for` lays only level 0 into
  elements) -- the function reads the placed ROOMS rather than crossing every element with every
  storey, which makes that true by construction. The main block's slab keeps its old name and
  `tdl_id` exactly; only a second element's carries a suffix.
- **THE DISCLOSURE REACHED ZERO AND THE BLOCK DID NOT VANISH WITH IT (WP-11.6).** The ruling's check
  was a falling count -- "six today and must name five, then four, then none" -- and
  `not_element_aware` is `[]`. **The note may no longer say COULD NOT EVALUATE**, and that is the
  harder half: with nothing unjudged those words are a FAKE UNJUDGED, which this corpus treats as
  exactly as dishonest as a fake pass. The block kept TWO facts that outlive the six layers and
  **ITEM 4 KILLED ONE OF THEM IN THE SAME PACKAGE**: it said `engine="cp"` refuses a multi-element
  plan, "so the engine that PROVES is unavailable" -- and the prover places per element now, so
  that sentence became a false statement about the engine in the FLATTERING direction, the same
  fake-unjudged shape one paragraph up. What survives is that **the roof is still derived for the
  main block alone** with no stated ridge relation per element, and that the abutment between two
  ADJACENT elements is nobody's rule (refusing a door across a gap and stating why is honest, and
  is not the same as knowing when two elements ought to touch).
  **AN EMPTY LIST IS NOT THE QUESTION CLOSED**: two of the ruling's four items are unbuilt (the
  per-element roof, and the abutment between adjacent elements), and
  `oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it` stays open on them.
- **CP-SAT PLACES PER ELEMENT, AND TWELVE DOWNGRADED WALL PINS BECOME FOUR (WP-11.6 item 4).**
  `geometry_cp._boxes` gives each room its own element box, read from `geometry.blocks_for` -- the
  ONE spelling both engines share, taken from the plan rather than passed by the caller because
  seven `_build` call sites would each have had to pass one and a reader that forgot would model a
  wing inside the house, which is the very defect the refusal existed to prevent arriving through
  its fix. **With one element every room maps to `(0, 0, Wi, Hi)`**, the pair the model spelled
  inline at every site, so the sixteen one-rectangle records take the same path -- and the guard is
  the MODEL, not a placement: the serialised `_build` proto is **byte-identical on all sixteen,
  hard and objective**, which is stronger than sixteen ninety-second solves and costs nothing.
  **AND THAT SENTENCE WAS PUBLISHED ONCE BEFORE IT WAS TRUE, ON AN INSTRUMENT THAT COULD NOT
  FAIL.** The harness called `m.Proto().SerializeToString()`, which this build of ortools does not
  have (`CpModelProto` is the C++-backed helper here); it threw `AttributeError` on BOTH sides, so
  `diff` compared two identical tracebacks and printed BYTE-IDENTICAL. Believed three times, and it
  reached this file and the report. Re-derived with `str(m.Proto())` -- plus an assertion that a
  model serialises to more than 5 KB, so an empty read cannot pass again -- **the objective model
  had moved on seven of the sixteen**: `_EXT` widened four variable domains unconditionally, on the
  argument that a looser domain cannot change an answer. **A DOMAIN IS AN INPUT TO PRESOLVE, NOT A
  COMMENT.** `_wide` widens only above one element and
  `test_no_shipped_plan_gets_a_WIDENED_domain` computes the bound the way `_build` does rather than
  quoting it, with a multi-element control so it cannot pass by never widening.
  Measured on the Tidewater record at 90 s, seed 7: one rectangle **12** downgrades, the same
  record with the three service rooms tagged into a west dependency and NOTHING else changed
  **4**, the package's fixture (tagged and walls re-declared) 5. **Twelve to four with not one
  declared fact touched** -- the diagnosis's own sentence measured, because a service room
  declaring N/S/W is declaring the exposures of a WING.
  **THE HYPHEN'S ABUTMENT NEEDED NO NEW CONSTRAINT, WHICH THE PLAN TEXT HAD CALLED "THE SEVENTH
  DEFECT"**: `_build`'s door rule is already a hard abutment (`a.x + a.w == b.x`), vacuous while
  every room shared one rectangle and real the moment the elements are. What it needed was the
  OTHER half -- a door between elements that do NOT touch is not the model's fact, stated in
  `refinements`, because a detached dependency is detached and proving a buildable house
  impossible is the one thing a hard constraint here must never do. `_abuts` is the test and a
  shared CORNER is not one: no leaf fits in a point.
- **A SEARCH THAT TOLERATES AN OVER-SIZE AND A PROVER THAT REFUSES IT ARE THE SAME DEFECT READ
  TWICE, AND ONLY ONE OF THE TWO SAYS SO (WP-11.6 item 4).** `derive_footprint`'s
  `a0 = sum(r["_area"] for r in prep[0])` counted a dependency's rooms into the MAIN block while
  `flank_sizes` sized that dependency from the same rooms and laid it BESIDE the block -- the
  wing's area counted twice, **2,405 sf of main block for 1,863 sf of main-block rooms, 29% over**.
  The hill-climb absorbed it silently as empty floor. CP-SAT, which has a coverage floor, reported
  the house INFEASIBLE at every bay count *"even with every declared requirement dropped"*. Sizing
  it from its own rooms moved the main block 63 x 38.17 -> 45 x 41.4 **and every measurement
  WP-11.6 had published on its own fixture with it**: layer 1's refusals 9 -> 5 became 9 -> 5 ->
  **0**, layer 5's landlocked control fell from two rooms to one (`chamber2` reaches its east wall
  in an honestly-sized block), the kitchen's lit walls went `["S","W"]` -> `["N","S","W"]`, and the
  three-element built extent 118 -> 100 ft with `flanking_ft` unmoved at 55. **The identities held
  and the literals moved**, which is the difference between a guard and a measurement.
  And the multi-element DISCLOSURE was attached in `write_record` only -- the heuristic's writer --
  so the one engine every multi-element plan was SENT AWAY FROM was the only one that disclosed
  anything about them; the first proved dependency placement came back `multi_element: null` on a
  record carrying two blocks. Also found: `_score` never passed `bounds` to `exterior_score` while
  the hill-climb has since layer 4, so a wing room's declared walls were charged against the WING
  on one engine and the main block on the other.
- **AN UNREACHABLE BOUND LOOKS EXACTLY LIKE NO BOUND, AND A SATISFIABILITY TEST CANNOT SEE A
  LOOSER MODEL (WP-11.6 item 4).** Every site in `_build` that read the footprint as the whole
  building had to become the room's own element; all but one were found by reading, and the one
  that was not is `m.NewIntervalVar(x, w, m.NewIntVar(0, Wi, ""))` -- **the interval's END
  variable**, which
  carries no constraint of its own, so nothing in the source reads as a bound on where a room may
  be. A west wing's rooms end at x = -14 and that domain cannot hold a negative number, so the
  model came back INFEASIBLE with every assumption cleared and NO CONFLICT TO NAME. Found by
  bisecting the model, not by re-reading it.
  **SEVENTEEN MUTATIONS. THE FIRST SWEEP OF FIFTEEN CAUGHT ELEVEN, THE FOUR MISSES SHARED ONE
  SHAPE, AND RE-RUNNING THE CONTAINMENT MUTATION AGAINST ITS NEW GUARD EXPOSED A FIFTH** (the DEPTH
  bound, unreachable from the corpus because a dependency is centred on the main block's axis and
  never deeper than it, so it is DRIVEN by replacing `blocks_for` as layer 6's garage branch had to
  be; seventeen of seventeen on the re-run). The shape of the four:
  the tests asserted that the tagged model is SATISFIABLE and that the returned solution sits
  inside the wing, and satisfiability is a weak instrument -- a LOOSER model is still satisfiable
  and a returned solution can happen to be contained, so every mutation that merely WIDENED a
  bound passed. Three lessons: an **assumption literal is invisible to a test that clears
  assumptions** (the wall pins); a suite that only ever builds the HARD model **has not tested the
  objective at all** (the bay grid, whose `ev` domain of `[0, span]` makes a negative edge
  infeasible rather than merely worse); and **a west wing tests only the lower half of every
  bound** -- `x + w <= Wi` is LOOSER than the wing's own east face at negative x, so the first
  containment guard passed under mutation for the wrong reason (the coverage floor refused the
  intruding rectangle). An EAST wing is the discriminator and there is a fixture for it now; the
  DEPTH bound is the fifth miss named at the head of this entry, and has none.
- **A NEW FINDING IN THE DRAWN LAYER MUST GO THROUGH `_add`, AND A RULE THAT BECOMES A REPORT MUST
  NOT GO SILENT (WP-11.7/11.8, found by a RED BUILD after a hook-driven commit).** Four failures,
  all mine, all caught by guards that already existed. **`F.add` instead of `_add`**: WP-9.1 set
  the engine once in `drawn_layer` and passed it through one wrapper *"so no call site can omit
  it"*, and the facade block's two `info` findings omitted it -- `test_evaluate_matches_cli` fails
  because the bench's drag path places with the SEARCH by name while everything else takes the
  proof, so a drawn finding with no engine breaks the parity that stops a mid-drag fatal reading as
  the house changing. There is a source guard now (the layer holds exactly ONE `F.add(`, the
  wrapper's own definition) beside a behavioural one.
  **AND A RULE THAT LOST ITS TEST WENT SILENT**: turning `centre-passage-core`'s facade-share test
  into a report left it emitting nothing at all in the grouping layer -- no evaluation, no unjudged
  note. `measures.reported_by` was added for exactly that and its schema description says *"it
  exists so that a rule with no `test` cannot read as a rule nobody executes"*; **the field's
  purpose was written and then not honoured.** `plan_check` emits `REPORTED, not required` naming
  the reporter and the advisory band. The other two were an unsorted directory read in a new test
  and the WP-11.6 finding digest moving by exactly the facade rows (+13 Tidewater, +1 spec
  Colonial) -- re-pinned with the count, because **a digest that moved by MORE than the change
  accounts for is the failure that pin exists to catch**.
- **A PROOF OF FEASIBILITY IS NOT A PROOF OF COMPOSITION, AND THE DEMERIT SCORE ALONE LIES ABOUT
  WHICH HOUSE IS BETTER (WP-11.8).** CP-SAT's phase A proves the hard set; phase B carries every
  compositional term the corpus has, and when it times out `objective` is null and the drawn house
  is whatever the solver reached FIRST -- no term for the front, the axis, the mirror pair or the
  stack was evaluated on it. `geometry._offer_the_alternative` then runs the hill-climb (~0.3 s,
  that branch only) and records `geometry_report.solver.alternative`.
  **IT RECORDS TWO NUMBERS AND THE SECOND ONE IS THE POINT.** On `spec-builder-colonial` the search
  scores **592.3** against the proof's **789.3** -- 197 points better -- and buys it by breaking
  **SIXTEEN declared facts the proof holds** (0 against 16). The ruling says to offer the search
  "with its demerit score" and that score ALONE reads as the better house; it is the cheaper one.
  The comparison is judged against the PROOF'S downgrade list, because a heuristic record carries
  none of its own and charging it for pins CP-SAT proved impossible would rig it the other way --
  `hard_fact_violations` takes `extra_downgraded` for exactly this and its docstring already said
  so. **No surface may print one number without the other**, and the plate line, the bench
  paragraph and the record all carry both.
  **THE BENCH SAID "PROVED, NOT SEARCHED" OVER EXACTLY THAT PLACEMENT** -- `PlanWorkbench.jsx`,
  the diagnosis's J2 -- and says **proved feasible** now, with the composition's absence stated.
  `corpus._placed` records `solver.drawn_by` including an `input_digest` taken BEFORE the solve,
  which is J6: two CP runs of one record agree to the foot, so when two sheets of "the same house"
  disagree the INPUT differed, and the plate carried nothing that would let a reader tell.
- **WHICH PLAN DEMONSTRATES A BUDGET-DEPENDENT DEFECT IS ITSELF BUDGET-DEPENDENT (WP-11.8).**
  `oq/a-proof-of-feasibility-is-not-a-proof-of-composition` was ruled on
  `tidewater-georgian-careful`, and on this machine that plan no longer reaches CP at all: `auto`
  spends its 25 s and falls back to the hill-climb (`fallback: budget`). The live case is
  **`spec-builder-colonial`** -- the OTHER shipped reference plan, which the diagnosis never named
  for this. **Quoting the Tidewater run as the live example would now be wrong**, and the register
  entry is corrected rather than left to read as current. The same reason makes the test fixture
  DRIVEN rather than the corpus: a fixture that IS a shipped plan would make these tests
  statements about a 25-second budget.
- **THE FACADE IS A RESULT NOW, AND THE FINDING OF THE PACKAGE IS A COINCIDENCE (WP-11.7).**
  `build/facade.py` derives the rhythm the plan's own `footprint.bays` imply, compares the drawn
  front against it and REPORTS -- it composes nothing, because the ruling's second half is that the
  commitment sequence is how findings are EXPLAINED and not how they are resolved (Glassie's own
  rule sets are order-independent). It lives in `plan_check`'s **drawn** layer because everything
  it reads is a placement, which is WP-11.4's rule for choosing a layer.
  **MEASURED on `tidewater-georgian-careful`: serious 63 -> 62, minor 88 -> 101.** The serious is
  the ruling's own first commitment landing: `centre-passage-core`'s facade-share test was HARD and
  convicted this house at a measured **0.136** against 0.18-0.27, and under the ruling the share is
  a CONSEQUENCE reported rather than an input the passage may be sized from. Its `test` is gone,
  its severity is `preferred`, the band survives as `measures.advisory_band` -- and the 8 ft floor
  is a DIFFERENT rule and stays hard. `passage-that-is-a-corridor`'s `correct_practice` no longer
  opens *"Size the passage from the facade"*. The thirteen new minors are seven bays of the front
  carrying no opening and six rooms whose declared window count disagrees with the bays their front
  wall spans -- `chamber2` spans two bays and declares none.
  **`elevation._face_bays` COMPOSED THE FRONT FROM A PACK FORMULA AND NEVER READ `footprint.bays`**
  -- two records built from different rules with nothing comparing them, OQ 85's shape, four hundred
  lines from OQ 85's own fix. **They AGREE on both shipped plans (7/7 and 5/5)**, so the elevation
  takes the plan's count now and the corpus output is byte-identical: a second rule removed, not a
  new answer. Only the faces spanning the WIDTH take it -- a gable end's span is the depth and
  handing it the width's count is the OQ 48 error in a new place. **And because they agree, the
  corpus cannot test the join**: a mutation deleting it leaves every natural assertion green, so
  the guard DRIVES the plan to nine bays, which the formula would never pick (WP-8.11's rule).
- **A BAND STATED IN A RECORD AND TRANSCRIBED INTO ITS READER, FOUND BY `check_rooms.py` AND NOT
  BY `validate.py` (WP-11.7).** Adding `advisory_band`/`reported_by` to a grouping rule's
  `measures` failed `check_rooms.py` -- the sub-schema is `additionalProperties: false` -- **while
  `validate.py` passed**, which is worth knowing: the two do not check the same things about a
  grouping. Chasing it found the code half: `facade_share` had the pair written into it as a
  literal beside the rule that states it, one rule in two places, **committed inside the function
  whose whole subject is one rule in two places**. The schema is widened and its field description
  says a rule carrying `advisory_band` may NOT also carry a `test` on the same quantity, because
  that is requiring and reporting one number at once.
  **AND THE GUARD AGAINST IT FLAGGED THE FIX'S OWN COMMENT**, which quoted the figures to explain
  the defect -- the note demonstrating the finding by committing it. Reworded rather than exempted,
  which is the move this file already records for the citation guard. Its first version was also a
  bad instrument, flagging any file containing both numbers anywhere and matching three unrelated
  files' constants; it searches for the literal pair's SHAPE now.
- **TWO ERRORS CANCELLED AND THE TOTAL DID NOT MOVE, WHICH IS HOW THEY WERE FOUND (WP-11.7).**
  The first draft of `facade.compare` emitted `front-door-off-the-centre-bay` while `plan_check`
  already emits `drawn-door-off-the-centre-bay` from WP-11.3's axis reading -- **the same rule
  spelled twice, in the package whose own ruling is about not saying one thing in two
  vocabularies** -- and the two DISAGREED about the number, because `axis.door_bay` returns a
  ZERO-based index and the older finding adds one for the reader. A sheet carrying both would have
  given one door two bay numbers. It was invisible in the totals: removing the facade-share hard
  test took one `serious` away and the duplicate put one back, so 63 stayed 63. **Found by asking
  why a serious finding had been added and the serious count had not moved**, then reading the
  findings rather than the totals.
- **FIFTEEN OF SIXTEEN PLAN RECORDS NAME NO PARTI, so the facade layer is silent on 94% of this
  corpus (WP-11.7).** `facade.rhythm` derives for ONE record -- `tidewater-georgian-careful`, which
  WP-11.2 authored. Every reference plan **and `spec-builder-colonial`** name none, so the whole
  block is one `info` naming the reason, which is not a pass. **The refusal is correct and the
  count is the deliverable**; `oq/fifteen-of-sixteen-plans-name-no-parti` is the sibling of
  `oq/fourteen-of-sixteen-plans-name-no-massing` one field over, and it forbids deriving the parti
  from the massing, the style or the room list in the same words the massing entry uses. **Do not
  close either by lowering the finding's severity**: an `info` on fifteen records is already close
  to invisible.
- **A PARTI MAY STATE ITS OWN MASSING ELEMENTS NOW, AND THE CORPUS REFUSED THE FIRST DIAGRAM THAT
  DID, THREE TIMES (WP-11.6).** A parti room carries `block` and `hyphen` (parti schema),
  `compose.py` copies both onto the plan record exactly as it copies `stacks_over` -- **the
  composer wrote no `block` on any room until this**, so the only route into the multi-element
  machinery was a caller-supplied record. Re-authoring `centre-passage-double-pile` with its
  service in a dependency was then refused by `check_partis.py` in all THREE arrangements, each
  time by a HARD room rule: all six service rooms out -> *"Butler's Pantry does not reach a dining
  room through a direct door"*; butler's pantry kept in the main block with a `gallery-corridor`
  hyphen -> *"Hyphen does not reach a stair hall through a direct door"*; the same with a
  `breezeway` -> *"Butler's Pantry does not reach a kitchen through a direct door"*. **The three
  are jointly unsatisfiable once the elements are real**: the butler's pantry must directly door
  BOTH the dining room and the kitchen, a door between two elements cannot be placed unless the
  rooms abut (measured 5 of 5 unplaced, one reason), and any boundary between dining and kitchen
  cuts one of the two. **`five-part-palladian` appears to do this correctly and only appears to** --
  it satisfies every rule because NOTHING READS ITS COMPOSITION, and the rules were never tested
  against a diagram whose elements exist. `oq/three-hard-room-rules-forbid-a-detached-kitchen`.
  **The change is worth making and that is measured**: on `family-georgian`, fatal findings
  **17 -> 10**, serious 76 -> 72, cross-element doors unplaced **0 of 1**, the whole service block
  and the stair no longer unreachable -- **while `compose.score_candidate` rates the better house
  SEVEN POINTS WORSE**, 73.5 -> 66.5, which is its own question. The parti is reverted until ruled.
- **THE FLANK IS STATED RATHER THAN SEARCHED FOR, WHICH IS `courtyard_slice`'S OWN MOVE (WP-11.6).**
  `geometry.hyphen_anchors` reads the door graph for a crossing THROUGH A LINK and
  `geometry.flank_slice` lays those rooms against the element's shared face as a strip, then slices
  the rest -- *"the search is good at slicing a range and has no way to know which of its edges
  matters."* **The search really cannot find it and that was SWEPT**: `adjacency_score` already
  charges every non-touching door pair, so the placement pays at every candidate, and at the
  shipped **250** the butler's pantry never reaches the shared face on either seed, at **1,000** it
  does on both, at **2,000** on one. **Four packages have now measured a placement rule whose
  verdict is a property of the pool** (`oq/a-placement-rule-is-free-at-a-pool-the-server-cannot-afford`),
  and this is the sharpest, because here the pool decides whether the house is drawn CONNECTED.
  **SCOPED TO THE LINK, and the scoping is what keeps the fixture honest**: a first version
  anchored on any cross-element door, and four of them on this package's own fixture cross OPEN
  GROUND with no hyphen room, where no laying of rooms can place a door -- a detached dependency is
  detached. Unscoped it moved the placement for nothing and turned FIVE of the package's own
  published measurements red; scoped, that fixture is byte-identical and the fixture that has a
  link keeps every gain (`butlers -> hyphen` places, `butlers -> kitchen` correctly does not).
  **The centre passage is not available as a house-side anchor**: stating a strip for it put the
  passage **5.85 ft outside the main block** and took the composed house from 11 fatal findings to
  14, so `flank_slice` takes the anchors that FIT, smallest first, and refuses the rest.
  **And the garage joins the element its anchor is in** -- `attach_garage` doors its mudroom onto
  the kitchen, which may now be in a wing. **That branch is unreachable from the corpus and a
  mutation deleting it left the whole suite green** until a driven test existed (WP-8.11's rule);
  six of six caught on the re-run.
- **A MULTI-EDIT SCRIPT THAT ASSERTS BETWEEN ITS EDITS WRITES NEITHER, AND THE COMMIT SAYS IT WROTE
  BOTH (WP-11.6, found at layer 6).** Two replacements went into one `PLAN-OF-ACTION.md` script,
  the SECOND assertion failed, and the script died before `write_text` -- so the first did not land
  either. Re-running only the second put the layer-5 section in **beneath a status line still
  saying "layers 1 through 4" and "two"**, and that shipped in a pushed commit whose message says
  the plan board was updated. It is `65901a2`'s shape exactly, which this file records as *"the
  hand correction itself failed to land"*. **Assert before editing anything, or write what
  succeeded -- and RE-READ THE FILE after correcting a number in it**, which is still the only
  thing that has ever caught one of these.
- **TWO OF THE SIX PROBES READ ZERO ON THEIR FIRST RUN AND NEITHER ZERO WAS A DEFECT'S ABSENCE
  (WP-11.6).** The openings probe looked for a window drawn FAR FROM its room and found none,
  because the real defect is a window REFUSED outright ("the placement puts this room on no such
  boundary wall"); the structure probe read a `bearing_lines_x` key that does not exist. **A probe
  pointed at the wrong defect and a probe reading a missing key both report 0, and 0 reads as
  nothing-wrong** -- the same shape as the stacking meter's missing `vertical` key one package
  earlier, twice in two packages. **A THIRD was wrong and was only caught at its own layer**: the
  lot probe read 0 honestly on the shipped 140 ft lot and needed an 80 ft one to fire, and then
  published `lot_capped: null` off `footprint.lot_capped`, which does not exist -- the record says
  `false` at `geometry_report.lot_capped`, which is worse (see the lot-cap entry above). So of six
  probes, three were wrong and two of those read a key that is not there.
  `vertical_score`'s probe read 0 and was recorded as NOT REPRODUCED rather than as absent, and
  that judgment SURVIVED layer 3 -- the support credit it looked for really cannot fire -- but the
  layer had a defect of the opposite sign the probe was not pointed at.
  **Before believing a meter's zero, make it report non-zero once** -- and before believing its
  non-zero, check the key it read.
- **DECLARED STACKING IS A RULE IN THE SEARCH NOW, AND ITS COST IS A PROPERTY OF THE POOL RATHER
  THAN OF THE RULE (WP-11.5).** `geometry.declared_stack_breaks` is the ONE reader of a
  `stacks_over` claim against a placement, on `plan_check`'s own strict-intersection rule; the
  search keeps TWO incumbents (best overall, best breaking no declared claim) and prefers the
  second when it exists. **It is not a rejection**: an emptied pool is a placement failure where
  the corpus wants a stated compromise, and when no strict candidate exists
  `geometry_report.stacking` SAYS SO and names the count -- a hard rule that quietly becomes a
  charge is worse than the charge. `geometry.STACK_HARD` is the switch; clear `_SOLVE_CACHE`
  between settings. **MEASURED: 70.5 points at the shipped 250 candidates, 24.9 at 500, and
  NOTHING at 1,000**, where the unconstrained winner already satisfies every claim. Broken claims
  4 -> 1 at 250 and 4 -> 0 at 1,000 on the spec Colonial, 8 -> 2 and 3 -> 0 on the Tidewater.
  **IT SHIPS DEFAULTED OFF (`STACK_HARD = False`) AND THE NUMBER THAT DECIDED THAT IS
  STRUCTURAL**: on `spec-builder-colonial` the strict candidate introduces **two over-capacity
  clear spans where there were NONE, the worst 40.0 ft against a 20 ft capacity**, while on the
  Tidewater plan the same rule takes spans 2 -> 4 with the worst falling **53.9 -> 36.0 ft**. Two
  shipped plans, opposite structural verdicts. Better rooms against worse structure is a trade for
  a person; `tests/test_stacking_rule.py` DRIVES the flag rather than reading the corpus's own
  state (WP-8.11), so the other setting is guarded rather than dead. **The one blind guard of the
  package was the no-strict-candidate DISCLOSURE** -- both shipped plans always find a strict
  candidate at 250, so that branch never ran and deleting it left the suite green. A pool of ONE
  forces it; six of six mutations caught on the re-run.
  **THREE PACKAGES HAVE NOW MEASURED A TERM WHOSE VERDICT DEPENDS ON THE POOL** -- WP-7.4's
  stacking weight looked inert at 250 and moved 12 candidates at 2,000, WP-11.3's centre-bay term
  changed behaviour at 1,500 -- **and the pool has never been the subject**:
  `oq/a-placement-rule-is-free-at-a-pool-the-server-cannot-afford`.
  **AND THE CRITIC'S KEY DOES NOT SEE THE BENEFIT, WHICH IS IN THE ROOM SIZES.** On the spec
  Colonial, rule off against on: the **Stair Hall goes from 36 sf against a 76 sf floor (53%
  SHORT) to 64 sf (16%)**, the Mud Room 16% -> 6%, the Study joins at 16%, total shortfall
  **46 sf -> 30 sf**. The minor-finding count ROSE while the house got materially better, because
  a finding count weights a waste stack landing on nothing the same as a label. **Read the rooms
  before quoting the key on a placement change.**
  **The massing selector this package was written around DOES NOT EXIST**: all 40 massings carry a
  `structural_logic` string and NOT ONE says the upper floor repeats the lower. The corpus's one
  such sentence is on a parti, and one instance is not a population a prose reader may be built
  on. `stacks_over` is the authored, machine-readable statement and it needs no selector.
  **OQ 95's refusal of the CP HARD PIN STILL STANDS** -- the downgrade loop reads
  `kind == "wall"`, so a stack pin outranks every authored exterior wall and a stack-only core
  reports infeasible rather than relaxing. Teaching it a second kind needs an ORDERING ruling
  between an authored `stacks_over` and an authored `exterior_walls`, and the corpus says both
  things: exterior walls "are aspirations, not rectangle edges", and OQ 95 MEASURED an authored
  kitchen wall being downgraded to serve a stack.
- **A NEW FINDING LAYER MUST BE MAPPED TO A SCORING AXIS, AND WP-11.4 PUSHED WITHOUT DOING IT
  (found by WP-11.5).** `plan_check` gained a `hearth` layer and `compose.SCORE_LAYERS` did not
  gain a `hearth` key, so both findings landed in `score_unclassified_layers` and no axis counted
  them. **The guard worked exactly as designed** --
  `test_score.py::test_every_layer_the_validator_emitted_is_classified` went red naming the layer
  AND the remedy in its own assertion message -- and the reason it was not seen before the push is
  the process, not the guard: **a stop hook asked for a commit while the full build was still
  running, and the build was the only thing that could have caught it.** A `check_all.py` that has
  not finished is not a green build; if a push has to go out first, say so and re-run.
  **`SCORE_LAYERS` IS PINNED BY A TEST WHOSE MESSAGE IS AN INSTRUCTION**: *"Re-measure the returned
  sets before re-pinning"*, because a layer is worth a different number of points on a different
  axis and an independent audit once moved `grouping` from canon to rooms and got a DIFFERENT
  returned set with the whole suite green. Measured three ways on family-georgian before re-pinning
  -- unmapped / rooms / canon return the SAME SET IN THE SAME ORDER, and only the two candidates
  carrying hearth findings move (78.7/68.7, 78.4/68.4, 78.1/68.3). The axis choice changes nothing
  today, so the argument decides it: `rooms`, because a room's fire is read from that room's own
  `servicing.heat` and `servicing` already maps to `rooms`. The compromise is stated beside the
  mapping -- `hearth-off-the-stack-wall` is a record-against-massing fact that belongs on `canon`,
  and splitting one layer across two axes is the re-weighting the `drawn` note declines.
- **THE HEARTH CHECK WENT INTO THE ONE LAYER THAT CANNOT RUN IT (WP-11.4).** It was written into
  `plan_check.drawn_layer`, which early-returns on a record with no placement -- and NOTHING
  `hearth_report` reads is a placement: the room's authored `hearth`, the massing's `hearth`, the
  room type's `servicing.heat`. So `spec-builder-colonial`'s dining room, which has no fire under a
  massing that draws paired end stacks, produced **no finding, no census and no reason** until
  somebody placed it -- a check that could not fire reading exactly like a check that passed, in
  the package written to stop that. It runs beside the other declared-record layers now and
  `hearth_summary` is published on an unplaced record; the finding kinds lost their `drawn-` prefix
  (`room-without-a-hearth`, `hearth-off-the-stack-wall`). **`breast` and `stack_axes` DO read
  placement** and belong to the renderer and the roof; a placed hearth check -- a breast
  overlapping a door or a furniture run -- would belong in `drawn_layer` and is not built. **Ask
  what a check READS before choosing its layer**, not what it is about.
- **THE ROOF'S HEARTH RECONCILIATION SWALLOWED ITS OWN FAILURES, AND `hearth_report`'S BRANCH
  ORDER IS LOAD-BEARING (WP-11.4).** `roof.py` wrapped `stack_axes` in a bare
  `except Exception: axes = None`, which reverts to the centre-line rule SILENTLY and then says
  *"this record states no hearth"* about a record carrying three -- the sheet drawing stacks over
  nothing while the plate asserts there is nothing to stand over. That is WP-9.1's `except: pass`
  exactly. **Four note states now**: positioned over N stated flues / states N and none could be
  positioned / COULD NOT BE READ, with the exception text / states none, *"not a house with no
  fires"*. And in `hearth_report`, **`none` is tested BEFORE the unreadable-massing branch**, so a
  room the corpus positively refuses a fire (`rooms/centre-passage.json`: *"Historically none. The
  passage is the unheated buffer between two heated rooms"*) stays `declined` whatever the massing
  says; reversed, the corpus's own refusal is downgraded to "nobody could tell", which is the
  fake-unjudged direction and is as dishonest as a fake pass. WP-8.11's `kit.forbidden` ordering
  lesson in a new place, with its own guard, because the test that happened to catch the mutation
  was about the readable case.
- **A NOTE ON A DATA RECORD CAN CLAIM A CHECK THAT DOES NOT EXIST, AND THIS ONE WAS WRITTEN BY THE
  PACKAGE REMOVING THE SAME SHAPE ONE LAYER DOWN (WP-11.4).** The Tidewater dining hearth was
  authored on the W gable with a note saying its disagreement with `rooms/dining-room.json`'s
  *"interior wall opposite the sideboard"* *"is reported by build/hearths.py rather than resolved
  silently."* **It is not.** The only comparison made is against the MASSING's stack walls, and W
  is exactly where `gable-end-paired` puts them, so it passes in silence. Corrected, and
  `tests/test_hearths.py` pins the actual scope so an absent finding cannot be read as a comparison
  that came back clean. **The obvious fix was measured and refused**: a prose reader over
  `servicing.heat` for a named wall returns five hits of which **two** are the thing sought --
  `dining-room` and `bedchamber` real, `drawing-room`'s *"compositional centre"*, `library`'s
  *"clear of the chimney breast"* and `breezeway`'s *"each pen has its own gable-end hearth"* three
  different jobs sharing one syntax. That is
  `oq/a-room-records-prose-states-a-floor-its-own-band-does-not` exactly.
  `oq/a-room-record-names-the-wall-its-fire-stands-on-and-nothing-compares-it`.
- **A FIGURE LIFTED OUT OF PROSE ABOUT SOMETHING ELSE WAS PUBLISHED AS MEASURED, BY THE PACKAGE
  WRITTEN TO STOP A VERSION OF THAT (WP-11.4).** `opening_width_in` searched a room record's
  `servicing.heat` for `NN in` and took the first hit. `rooms/closet.json` opens *"None required
  and none wanted"* and four clauses later describes a closet ceiling *"drywalled from a stepladder
  through a 30 in opening"* -- an air barrier, about a DOORWAY -- so a room that wants no heat at
  all published **30.0 in at `judgment: false`**, a measured fireplace opening. **The gate is
  `wants_a_hearth`'s verdict, NOT a tighter regex**: a pattern cannot tell a doorway from a
  chimneypiece and the verdict already can, and tightening the pattern until the number looks right
  is the move `check_grouping_rules.py`'s prose meter exists to refuse. After the gate,
  `bedchamber`'s *"30-36 in opening"* is the ONE own-figure in all 60 records, which is what
  `build/hearths.py`'s docstring had been claiming while there were two. **It was found by
  re-DERIVING a claim in the package's own report rather than re-reading it** -- WP-9.5's
  technique, and still the only thing that has ever caught one of these here.
- **A REFUSAL WITH ONE MESSAGE FOR THREE CAUSES TELLS MOST OF ITS READERS THE WRONG THING
  (WP-11.4).** `flue_walls` refused with *"a compound is a statement about a type that admits both
  arrangements"* and handed that to every plan stating no massing at all -- a true sentence about a
  different situation, on 14 of 16 records. The three cases call for three different actions
  (author a `massing`; author the `hearth` field in the catalogue; rule on the compound), so there
  are three messages, held distinct by a test. **A refusal's value is its reason; one reason for
  three causes is a refusal that has stopped being one.**
- **THE PHASE'S SIX NUMBERS DID NOT SEE TWO CHIMNEYS MOVE EIGHT FEET (WP-11.4).** `key`,
  `diverged`, `windows_unplaced`, `downgraded`, `transfers` and `score` were byte-identical on both
  plans across eight seeds while `roof.py` moved the Tidewater stacks 6.2 and 8.6 ft off the gable
  centre line onto stated flues. They are a PLAN-LAYER instrument and a roof or elevation change is
  invisible to them. The one movement they did report was real -- the spec plan's minor count
  `89-98 -> 90-99`, its dining room having no fire under a massing that draws paired end stacks.
- **A DRIVEN FIXTURE MUST NOT ACCIDENTALLY BE THE SHIPPED CORPUS, AND THAT IS NOW THE SECOND
  PACKAGE IT HAS BITTEN (WP-11.4, after WP-8.11).** Twelve mutations, three blind on the first
  pass: the breast guard asserted only that the breast lies INSIDE the room's x-extent, which is
  true of either wall, so swapping east for west stayed green; `drawn-hearth-off-the-stack-wall`
  had no fixture driving it, because all three shipped hearths sit on E/W, which is exactly where
  `gable-end-paired` puts its stacks; and nothing validated a plan against `plan.schema.json` at
  all, so the `wall` enum could have become a bare string. **And the harness itself had a typo**
  (`_h` for `h`), so one mutation reported NO MATCH -- this repo's own lesson, *a mutation that
  silently does not apply looks exactly like a guard that works*, met while applying it. Assert the
  match count before believing the colour.
- **THE SHEET NOW SAYS WHAT THE PLACEMENT GAVE UP, AND THE FIVE COUNTS WERE ALL ALREADY IN THE
  RECORD (WP-11.1).** The plate read *"PLACEMENT PROVED (CP-SAT) AGAINST THE RECORD'S DECLARED
  FACTS"* over a placement carrying `downgraded_wall_pins` of length SIXTEEN and `objective: null`.
  `build/disclosures.py` is the ONE spelling of every banner line; `render_plan.py` draws them and
  the bench renders the same list through `placement.disclosures`. **Do not add a third.** The
  lines: declared exterior walls set aside, the objective that did not run (gated on
  `engine == "cp-sat"` — the hill-climb's score IS its objective and a first draft published the
  opposite about it), undrawn window units, transfer beams, a style/title disagreement, and a table
  under the plates giving every ∗ room's declared figure. **A banner line WRAPS rather than
  truncating** and `top` reserves per ROW, not per line: the first draft ran 160 characters off the
  canvas edge, which is a disclosure the sheet does not make, produced by the package sent to make
  the sheet disclose.
- **A PLAN NAMES ITS PARTI NOW, AND THAT IS HOW THE DIAGRAM REACHES THE PLACER (WP-11.2, plan
  schema 0.6.0).** An id, never a record, through `core.load_parti` — not a fourth copy of that
  join. Until it, `centre-passage-double-pile`'s 9 ft module could not reach `derive_footprint` at
  all: the CLI, the bench's drawing route and both shipped plans passed no parti, so every sheet was
  drawn on the placer's 10 ft default. `massing_bays()` reads the massing's own `bays` (two forms
  accepted, five prose forms refused BY NAME — `"5-7 main"` is refused because `main` is doing work)
  and growth steps by TWO where the diagram wants a centre bay. **`build/check_plans.py` holds a
  hand-authored plan to the parti it names**: the shipped Tidewater record had dropped two of its
  five `stacks_over` claims and nothing could notice, because `compose.py` copies them and NOTHING
  CHECKED A PLAN THE COMPOSER DID NOT WRITE. **The cost is stated**: the odd bay count costs about
  three fatal findings on the hill-climb (8-seed means 6.2 → 9.2) and zero on CP-SAT, and the drawn
  furniture along-axis ratchet went 69 → 74. **The parti's 9 ft module contradicts its own
  exemplars** (Gunston measures 12.17 over five bays) — `oq/the-partis-bay-module-contradicts-its-own-exemplars`.
- **A SINGLE-SEED COMPARISON OF A HILL-CLIMB NUMBER COMPARES TWO DRAWS (WP-11.2).** The first
  before-and-after of the bay change read fatal 3 → 8 and looked decisive; at three seeds the same
  footprints gave 3–8 and 8–10, and at eight they gave two overlapping distributions whose means
  differ by three. `build/diagnose_sheet.py --seeds` reports every column as a spread, and
  `--baseline` prints the six numbers every Phase 11 package is held to, on BOTH engines. WP-9.6's
  rule (ratchet the deterministic figures, never the ones that drift) one layer up.
- **THERE IS AN AXIS VOCABULARY NOW, AND A SCORE TERM FOR IT WAS REFUSED WITH THE MEASUREMENT
  (WP-11.3).** `build/axis.py`: the footprint's centre line, the bay a door stands in, the mirror,
  vertical alignment — each COULD NOT EVALUATE with a reason rather than a zero, and an EVEN bay
  count is that state rather than a pass, because six bays have no middle bay for any door to stand
  in. The tolerance is half a bay module, **editorial, ruled 4 Sep 2026**, marked in the field that
  carries it. **Symmetry and alignment are REFUSED on an incomplete front** — seven undrawn window
  units on the Tidewater plan — because convicting that facade of asymmetry charges the house twice
  for one cause. A `centre_bay_score` was built and swept: paid at every weight, moving the winner
  at none, and at 1,500 candidates it moves the door to the wrong side of the centre. **A door in
  the centre bay is a property of a plan organised about an axis, not of a placement scored for
  one.** Deleted rather than left inert at weight zero.
- **THREE OF ONE SESSION'S OWN NEW GUARDS WERE BLIND, ALL THREE FOUND BY MUTATION AND NONE BY
  RE-READING (WP-11.1 through 11.3).** A canvas-height comparison that held for a second reason (a
  plan with no diverged rooms also loses a banner line); an `all(... for b in [])` over a growth
  loop that never ran on the fixture; and a refusal test that accepted the right answer for the
  wrong reason (delete the gable guard and the reader returns COULD NOT EVALUATE anyway, because
  the E wall has no openings). **Assert the REASON, not only the verdict, and check the fixture
  enters the code under test.**

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
  whose `block` tag the placer does not read. `engine="cp"` REFUSED a multi-element plan outright
  (one rectangle, `x = NewIntVar(0, Wi)`) and `auto` fell back saying why -- so on a plan with a
  dependency the engine that PROVES was unavailable and the engine that SEARCHES carried the
  findings. **That is no longer true: WP-11.6 item 4 gives each room its own element box and the
  prover places per element** (see the CP-SAT entry above). The sentence is kept in the past tense
  because it is what WP-10.1 measured, not because it still holds. **The composer writes no `block` on any room**: C2/C3 were reverted when the audit found
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
  is **OQ 51** and is the one with 2,762 instances. Read it before trusting "132 of 132 bound".
  OQ 51 is now RULED and HALF-BUILT (WP-8.2) -- a node may DECLINE a pack, and the live backlog is **180 unjudged** gaps, not the 233 published --
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
- **THE ONE FIGURE A CHECKER DID NOT DERIVE IS THE ONE THAT ROTTED (WP-8.14, 4 Sep 2026).**
  `check_counts.py` derives SIX values for OQ 51 -- `role_gaps`, `inherited_packs`, `unendorsed`,
  `endorsed`, `declined`, `judged` -- and holds this file's prose to each. **`unreached` was not
  among them**, and it is the one that went wrong: this file said **111 slots survive a flip
  whatever it does** for three flips after it stopped being true (179 → 111 → 96 → **47**), while
  `tests/test_stranding.py` was re-pinned at every one. **The test knew and the prose did not** --
  WP-9.5's second-commonest shape, occurring inside the register entry that documents that shape.
  Of seven figures the layer publishes, exactly one was unpoliced and exactly that one rotted;
  nothing about that is coincidence.
  **Closed as a three-link chain rather than a re-pin**: `unreached` joins `STRANDING`, where the
  sweep's drift check -- generic over `STRANDING.items()`, which is why adding the key was the
  whole of the fix -- holds it to the corpus; `check_counts.py` reads the constant and holds the
  prose to it (88 → 89 claims); `test_stranding.py` asserts the key is IN the dict, so a future
  flip cannot unguard the prose by dropping it. The middle link reads a constant rather than
  re-running a 6.5 s sweep every build -- a deliberate weaker link, complete because the first
  link closes it.
  **The general rule: when a layer publishes N figures and a checker derives N-1, name the one it
  does not.** It is not safe by being small; it is the one nobody will re-measure.
  And the same audit found the staging paragraph carrying THREE spent instructions in the present
  tense -- advice for a decision nobody can make again -- which is WP-6.4's *"until X lands is a
  lie the moment X lands"* at the scale of a whole entry: four packages of guidance accumulated
  and none retired when the thing it guided finished.
  **AND THE COMPANION RULE, WHICH THE AUDIT EARNED BY BREAKING THE FIRST ONE: NAME THE SURFACE THE
  CHECKER DOES NOT READ.** Correcting those three instructions here and not sweeping for them left
  SIX live across five files, the substantive one being what `check_inheritance.py` PRINTS on every
  `--strict` run -- a superseded ruling (*"flip NOW, one pack at a time"*, after the 4 Sep ruling
  flipped five together), a spent instruction (*"read `--stranding <pack>` before flipping"*, with
  nothing left to flip) and TWO counterfactuals that re-derive to **0** (`storey-graduation` 9 of
  23 gaps, `facade-gable` 32 of 16 -- a flipped pack has nothing left to withhold). Forty lines
  above them, `judged` *"does NOT move here"* -- the claim WP-8.13 falsified and corrected at
  `measure()`, 700 lines away IN THE SAME FILE. The sixth is the same file's `--stranding`
  ARGPARSE HELP (*"the flip may not land without ... which is how the flip IS staged"*): two
  printed surfaces in one file, neither of them prose any checker opens.
  **`check_counts.py`'s `CLAIMS` list is
  (file, key, regex) over MARKDOWN and never opens `build/*.py`**, so a number a checker prints is
  outside every guard in the tree for exactly the structural reason `unreached` was -- and it
  carries the authority of having been computed while being hand-typed.
  **The fix carries no number**: the footer states the programme finished and the two
  illustrations are DELETED rather than restated in the past tense. They stay past-tense HERE,
  where they are the record of why the flip order was chosen; a CLI says what is true now, and an
  illustration with no reader is an instruction to the next one. Removing a rottable number beats
  guarding it where the number has no live use. **No checker was extended to scan `build/*.py`** --
  telling a live claim from a historical one inside a print string is the code-span exemption in a
  new place, and inventing a mechanism late in a session is how WP-9.4 shipped four guards that
  could not fail.
  **And the correction to two test docstrings carried the same defect a third time**: the new
  prose for `test_loud_stranding.py` claimed the rule was held by *"the assert below"* and that
  file has none -- `test_opt_in_packs.py` does. Caught by RUNNING the mutation (flipping
  `trim-craftsman` for real in the pack file and `dist/taxonomy.json`, reading it back first)
  rather than by re-reading the sentence, which is the only thing that has ever caught one of
  these.
  Report: `docs/reports/wp-8.14-the-number-nobody-policed.md`.
- **AN UNVERIFIED RULING READS EXACTLY LIKE A RULING, AND NOTHING HERE CHECKS ONE (WP-8.13,
  4 Sep 2026).** PR #26's body was published carrying *"(Ruled 4 Sep: flip all five remaining packs
  in ONE package)"* when no such ruling had been made: the refill's concentration on the gated packs
  was a FINDING and the next step was a question standing to be asked. Lucas ruled exactly that
  hours later, which does not make the sentence true when it was written -- it asserted an
  authorisation that did not exist. Corrected in the PR's own Amendment 2 rather than silently
  overwritten, on PR #21's precedent.
  **THE CLASS IS THE POINT AND IT IS UNGUARDED.** `check_counts.py` polices numbers derived from
  the corpus, `check_citations.py` polices ids, `check_openings.py` verifies a quoted sentence
  against the record it names, and `check_moves.py` holds every move's `basis` to a sentence really
  in the record -- **the corpus checks its sources harder than it checks its authorisations.**
  Every "RULED BY LUCAS", "ruled 25 Aug", "re-ruled 3 Sep" line in this file is unguarded prose,
  and a wrong one is worse than a wrong measurement: a measurement can be re-derived from the
  corpus, and a ruling exists only in a conversation the corpus cannot read. *Sources or
  `kind: editorial`* is the rule for facts; there is no equivalent for permissions.
  **The remedy is not a checker** -- nothing in the tree can verify a conversation -- it is to
  write the question and the answer as two separate acts, and to date the second from when it
  arrived rather than from when it was expected. First known instance, and it was Claude's.
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
  run `build/gen_open_questions.py`. It holds **147 entries, of which 61 are open**
  (7, 8, 9, 10, 11, 18, 36, 37, 38, 39, 64, 66, 67, 68, 72, 73, 74, 75, 76, 77, 79, 86, 87, 91, 92, 93, 94, 96, 98, oq/a-baked-pack-value-is-a-second-delivery-path, oq/a-daily-route-is-an-editorial-model, oq/a-declared-measurement-and-a-window-record-state-one-width-twice, oq/a-finding-citation-cannot-name-a-finding, oq/a-findings-ordinal-is-not-an-identity, oq/a-kit-binding-propagates-to-descendants-nobody-read, oq/a-licence-conditioned-on-the-wrong-axis, oq/a-licence-matches-the-style-id-exactly-and-never-its-descendants, oq/a-lot-too-narrow-for-the-diagrams-own-minimum-bay-count, oq/a-massing-states-its-structure-and-nothing-reads-it, oq/a-material-neutral-assembly-decides-a-material-question, oq/a-node-that-refuses-a-category-must-decline-it-twenty-six-times, oq/a-placement-finding-is-classed-by-what-the-engine-is-for-five-kinds, oq/a-placement-rule-is-free-at-a-pool-the-server-cannot-afford, oq/a-room-count-cap-on-the-heavy-routes, oq/a-room-record-names-the-wall-its-fire-stands-on-and-nothing-compares-it, oq/a-room-records-prose-states-a-floor-its-own-band-does-not, oq/a-round-is-accepted-on-the-key-and-not-on-the-rule-each-move-executed, oq/a-slug-in-a-code-span-is-not-checked, oq/applies-when-means-two-things, oq/fifteen-of-sixteen-plans-name-no-parti, oq/fourteen-of-sixteen-plans-name-no-massing, oq/no-plan-record-states-its-bearing, oq/the-adjudication-cases-the-records-do-not-decide, oq/the-canon-axis-counts-two-grains-as-one, oq/the-composer-ranks-on-an-assumed-bearing, oq/the-depth-a-roof-needs-is-known-and-cannot-be-enforced, oq/the-partis-bay-module-contradicts-its-own-exemplars, oq/the-passage-is-divided-and-the-corpus-has-no-word-for-it, oq/the-raw-kit-read, oq/thirty-five-measurements-the-elevation-states-as-literals, oq/two-id-namespaces).
  The tally counts the two HALF CLOSED entries (18, 68) as open, because a half-closed
  question is an open one. That list is DERIVED from the register by
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
  The tally counts the two HALF CLOSED entries (18, 68) as open, because a half-closed question
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
    **THE BACKLOG COUNT WAS A BAD GUIDE TO WHAT A FLIP COST, and this paragraph is the record of
    why the order was chosen rather than advice for a decision anyone can still make** — the
    programme is finished and every pack it named is flipped. The figures below were measured
    against corpora that no longer exist and are kept in the past tense: `storey-graduation` HAD
    23 unendorsed gaps and stranded **9** slots while **45** survived it via inherited slot-level
    `packs` rulings; `facade-gable` HAD 16 and stranded **32** with none surviving. `--stranding
    <pack>` reports 0 for both now, because a flipped pack has nothing left to drop.
    **The corpus-wide figure for slots that survive a flip whatever it does is 47** — it was 179
    before any pack flipped, 111 after the first, and it fell through 96 to 47 as the rest landed,
    because each flip takes its own survivors out of the counterfactual. **This file said 111 for
    three flips after it stopped being true**, while `tests/test_stranding.py` carried 96 and then
    47: a number corrected in the test and not in its prose neighbour, which is WP-9.5's
    second-commonest shape appearing inside the entry that documents it. The mechanism is
    unchanged and is the durable half — `choose_pack` reads the slot record's own `packs` block
    before the rows, and no mechanism about DELIVERY can reach a slot record naming a pack
    directly.
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
    `mediterranean-revival`. That instruction read *check this before flipping `sash-light`* until `sash-light` was flipped; the durable form of it is in the fixture rule below.
    And the meter had a scoping defect WP-8.10 shipped: `--stranding <pack>` printed "32 slot(s)
    over 36 node(s)" because the slot counter was scoped to the pack and the node counter was not.
    More nodes than slots is impossible for one pack, which is how it showed.
    **THE THIRD FLIP IS IN (WP-8.12): `sash-light`, seven opt-ins, 70 slots over 34 nodes.**
    Two-gate gap **70 against 84**, the largest yet — 40 vouched names but 33 of them BIND the
    pack, so the vouched-and-gated population is what matters and it is no fixed fraction of
    anything. Ratchets 256/3056/215 → **255/3022/214**, `FORBIDDEN_RATCHET` 723 → **721** (two
    pairs, against 15 and 38 — the forbidden meter and the stranding meter are NOT proxies),
    `STRANDING` before 7788 → **7718**, stranded 2857 → **2787**, `baked_vs_refused` 71 → **67**
    (which is NOT the second delivery path closing: those four went because the live rule they
    were measured against no longer reaches those nodes). `rehoused` **1980** for the third
    package running and `dimensioned_after` **4931 for the FOURTH** — the end state has never
    moved. **`judged` is 249 after three flips and 136 withheld arrivals.**
    **THE REFILL IS NOT PROPORTIONAL AND MY OWN TWO POINTS SAID IT WAS**: 4 gaps from a 10-slot
    flip, 13 from a 32-slot one, **10 from a 70-slot one**. WP-8.11 called it "roughly
    proportional" on two points; the third falsified it one package later. What refills is how
    many ROLES the pack was filling and what sits behind it in each chain, not how many slots it
    dimensioned.
    **AND THE REFILL IS CONCENTRATING ON THE GATED PACKS — ten of ten here, every one
    `opening-proportion`, against three of thirteen last time.** It follows from the order: the
    five gated packs flip LAST, so they are what is still delivering when everything else has been
    withheld and they inherit each vacated role. **The order chosen to make the early flips safe
    back-loads exactly the rows whose adjudication authorises a behaviour change.** It was put to
    Lucas as a ruling rather than continued, and he ruled the five go together (WP-8.13, below),
    which ended the concentration: 0 of 36 refill gaps land on a gated pack.
    **A DRIVEN FIXTURE SHOULD NAME A PACK SCHEDULED LAST, NOT ONE SCHEDULED NEXT** — WP-8.11 moved
    `test_stranding.py`'s case to `sash-light`, the very next pack, guaranteeing another move one
    package later. It is `opening-proportion` now (gated, therefore last, therefore stable).
    **And a magic-number floor became a cross-check**: the ruling table's vacuity guard asserted
    ">= 150 rows" and three flips have withdrawn 34, so it is now the pack headings' own counts
    held against the parsed rows — two independent regexes that must agree, mutation-checked both
    ways.
    **THE PROGRAMME IS FINISHED (WP-8.13, 4 Sep): all five live-gate packs flipped TOGETHER --
    `opening-proportion`, `facade-classical`, `storey-graduation`, `timber-bay`, `gibbs-ionic` --
    26 opt-ins, 202 slots over 62 nodes.** Lucas re-ruled the staging when the refill's
    concentration on the gated packs was put to him: staging them singly would have spread over
    five packages the one decision that mattered. All eight packs the programme named are flipped
    and the other 49 are on `cascade` because nothing plans to move them.
    **THE COMBINED FLIP STRANDS MORE THAN THE SUM OF ITS PARTS, and the DIRECTION is the
    surprise**: per-pack 146+25+9+1+0 = **181**, combined **202**. The naive expectation is LOWER
    (a node losing one slot to two packs is counted by each), and it is higher because the five
    REHOUSE EACH OTHER -- a slot stranded by `opening-proportion` alone is picked up by
    `facade-classical`, so neither single-pack sweep counts it. Each per-pack figure measures a
    world in which the other four still deliver. **The sum is a bound in neither direction --
    and WP-8.14 measured the OTHER direction to establish that**, because 181 < 202 alone only
    shows the from-below sum under-stating. Restoring each of the five one at a time FROM the
    all-withheld corpus gives 167+46+9+1+0 = **223**, over-stating by 21 in the other
    direction: 181 < 202 < 223. A per-pack figure is a property of the corpus it was measured
    against, not of the pack. Third
    instance of the wrong-grain shape (`unendorsed` for deliveries, a corpus writer count for a
    node fact) and the FIRST caught before publication.
    **THE FLIP DISSOLVED WP-8.12'S OWN FINDING.** Refill 4 / 13 / 10 / **36** across the four
    flips -- still not proportional, now the largest -- but **0 of 36 land on a live-gate pack**
    against 10 of 10 last time, because all five are flipped and deliver nothing. The
    concentration was a property of the staging order and finishing the programme ended it.
    **`judged` MOVED, 249 -> 250, AND `measure()`'s OWN COMMENT SAID IT COULD NOT.** The route is
    `endorsed`, not `declined` -- the half the comment did not consider. Withholding a pack VACATES
    its role, the role re-attributes to the next ancestor, and where that pack both ARRIVES (the
    node opted in) and VOUCHES (`applies_to` names it) the gap lands in `endorsed`. One instance,
    pinned BY NAME because a count cannot tell it from an adjudication:
    `american-farmhouse-vernacular`/`opening`, vacated by `opening-proportion` and landing on
    `sash-light`. The floor is not violated and the classification is not wrong; **what died is the
    reading three packages rested on, that `judged` tells a flip from an adjudication.** Read
    `--strict`'s `withheld` line for that instead.
    **AN OPT-IN NEEDS TWO CONDITIONS AND WP-8.13 FIRST WROTE ONE.** The list came from each pack's
    `applies_to` minus binders and decliners -- 40 entries -- and `check_opt_ins` refused **14**,
    because `applies_to` says the pack is FOR a style and says nothing about whether the cascade
    DELIVERS it there. All 14 were no-ops, PROVED: removing them left every stranding figure
    byte-identical. 26 written; 41 entries over 24 nodes corpus-wide.
    **And the fixture rule expires**: "name a pack scheduled LAST" had nowhere to point once the
    schedule emptied, so it is "not scheduled at all" now -- `timber-panel` (131 slots) against
    `brick-course` (1 stranded, 66 surviving).
    Reports: `docs/reports/wp-8.10-the-flip-that-was-sold-on-the-wrong-count.md`,
    `docs/reports/wp-8.11-the-second-flip-and-the-fixture-that-would-have-gone-quiet.md`,
    `docs/reports/wp-8.12-the-refill-that-was-not-proportional.md` and
    `docs/reports/wp-8.13-the-programme-that-dissolved-its-own-finding.md`.
    **The meter, corrected 28 Aug 2026 (WP-8.2) and read the correction before any older figure.**
    `build/check_inheritance.py` pins three ceilings that may only go down -- **222 role_gaps**,
    **2,762 inherited_packs**, **180 unendorsed** -- and one FLOOR that may only go up,
    **judged 250** (endorsed + declined). **THE BACKLOG HAS BEEN READ END TO END THREE TIMES AND IT REFILLED EVERY TIME
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
    backlog is worked. `--slots ranch-style` showed 69 of 78 dimensioned slots governed by packs
    it never bound when OQ 51 was raised; after three flips it reads **59 of 66**, and the fall is
    the flips REMOVING deliveries rather than the node being any better bound. The illustration is
    kept in the past tense because it is what raised the question. That is tolerable only because it is counted.

## Conventions

Commits are written in the project's own voice: what changed, what was found, and what was
deliberately not done. Findings belong in the message, not just the diff. Branch is `main`,
remote is `origin` (github.com/codex-lux/Traditional-Design-Language, private).
