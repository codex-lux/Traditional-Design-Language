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

## Where the work stands (27 Aug 2026)

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

**Phase 8 is COMPLETE** (WP-8.1 through 8.4 and 8.6, 28 Aug) — the register as a directory and
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
a closed question and never had a number. The series is 8.1, 8.2, 8.3, 8.4, 8.6. Renumbering 8.6
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
proportion packs; 1777 still wanted, and 858 of those can never be harvested) · 14 reference plans · 24 MCP tools · **43 checks, 1,295 tests**
(plus the workbench app suite, **62** under `node --test`). Those figures were 970/36 before the
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
`len(CHECKS)` of 34, and reads "40 of 43 checks passed" after WP-9.1's arrangement selftest against a
`len(CHECKS)` of 40.
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
**every number in this paragraph goes stale silently** -- nor are numbers written into JSX, which
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

**Phase 8 is COMPLETE (28 Aug 2026)** — the register, the refusal half of OQ 51, the forbidden
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

**Next, in order:**
1. **WP-4.4** is **environment-blocked**, not deferred — the proxy answers 403 to CONNECT for
   www.loc.gov. `build/harvest_habs.py` is written, dry-run exercised and queued against the day
   the network opens; its own status block in `PLAN-OF-ACTION.md` carries the verbatim denial. The
   network-free next step there is giving the 322 asset records their `provenance.building` names,
   without which every harvest query degrades to a style-name search. Then Phase 5.

WP-2.3 closed Phase 2 on 25 Aug 2026: `build/geometry_cp.py` states placement to CP-SAT, enforces
room minimums instead of scoring them, and returns a named conflict set when a brief cannot be
housed. Read `docs/reports/wp-2.3-the-real-solver.md` before touching geometry — the exact-tiling
formulation the plan of action named does not work (CP-SAT could not decide it in 240 s while
holding a valid solution), and the solver reads the slicing tree off a heuristic layout instead.
`build/geometry.py` remains the default engine everywhere.

## Traps worth knowing before you hit them

- **Module loading.** Everything in `build/` and `mcp_server/` loads siblings *by file path*
  so each script also runs standalone. That returns a fresh module per call and the loads
  nest — one `check()` used to execute plan_check 16x, geometry 8x. `build/modcache.py` now
  caches by realpath and every local `_mod`/`_load` delegates to it. **Do not reinstate a
  local loader**; `tests/test_modcache.py` counts module executions to catch it.
- **Inheritance transmits more than anyone bound, in three places.** `hybridizes_with` transmits a
  donor's whole kit (OQ 58 scoped it); a BINDING used to transmit a pack's whole rule set (OQ 49
  scoped it); and `descends_from` still transmits an ancestor's whole set of proportion packs, which
  is **OQ 51** and is the one with 3,356 instances. Read it before trusting "132 of 132 bound".
  OQ 51 is now RULED and HALF-BUILT (WP-8.2) -- a node may DECLINE a pack, and the live backlog is 249 unjudged gaps, not the 233 published --
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
- **THE CORPUS FORBIDS THE SQUARE AND THE TRADITION PREFERS IT (WP-9.2).** 35 of 60 room records
  carry a `proportion` LOWER bound above 1.0 and **29 of those are NON-CIRCULATION** (35 minus the
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
  records still tell the next package to build it again. The ceiling is the well-sourced half and
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
- **THE FURNITURE CHECK READS THE DECLARED RECORD AND NEVER THE DRAWING, AND ONE PLACED ROOM IN
  FIVE CANNOT BE FURNISHED (WP-9.2).** `plan_check.py:1250-1288` is a good check pointed at the
  wrong record: `w, l = r.get("width_ft"), r.get("length_ft")`. Swept over all 16 plans, not the 2
  that ship: **231 placed rooms and 73 across-fails on the DECLARED record, both deterministic.**
  The DRAWN figure **depends on the engine and the default one is not reproducible**:
  `engine="heuristic"` gives **86 drawn fails and 25 rooms (11%)** failing an item their own record
  passes, identical on three cold runs; `engine="auto"` gives **130, 132, 133** on one unchanged
  tree, because it solves 15 of 16 plans with CP-SAT and CP-SAT under a time budget is not
  deterministic under load. **An earlier version of this entry published 133 and 50 with no engine
  named.** `bedroom` 13/19, `dining-room` **8/13**, `kitchen` 6/16, `breakfast-room` 3/5.
  **And the engine comparison is a finding in itself: CP-SAT, the engine that PROVES, draws about
  131 unfurnishable items where the hill-climb draws 86** -- it proves what it is told and nothing
  tells it about shape, which sits exactly opposite WP-9.4's result that the same engine change
  takes fatals 123 -> 36. **RATCHET THE DETERMINISTIC FIGURES (86 and 25), never the `auto` ones**:
  a ratchet on a number that drifts +/-3 is a build that fails for no reason. A dining table needs
  (40 + 2 x 54)/12 = 12.33 ft across; the slicer draws dining rooms 10, 11, 6 ft wide against
  records declaring 14-18. `spec-builder-colonial` draws a bedroom **6.0 x 38.0 ft** and two
  closets **1.0 ft wide**. Where the check DOES fire it quotes the declared figure, so every
  shortfall in the set is understated (the OQ 52 family). Fix in the `drawn` layer — the only layer
  that may read placement (OQ 54) — as ONE function with two callers, never a second
  transcription; and ratchet -- see the corrected figures above, NOT 50/133 -- because they are the honest measure
  of whether a placement change helps. **Second defect: `fw, fl = sorted(it["footprint_in"])`
  assumes every item rotates**, so the kitchen island `[84, 27]` is turned sideways and a 10 ft
  kitchen passes at 9.25 ft where an island along its counter run needs 14.0 — which is why the
  10 x 30 kitchen Lucas called far too narrow survives its own furniture check. Needs a typed
  orientation field, AUTHORED (WP-7.2 already paid for guessing `placement` from a name regex).
  **The relation itself is right and is not the bug: furniture sets FLOORS, never sizes** (OQ 92,
  "the tail wagging the dog"). A whole-room furnishability test was tried and REFUSED with its
  number — against-wall runs summed against the room perimeter flag nothing (the kitchen's five
  appliances are 12.75 ft against an 80 ft perimeter) because perimeter is not available wall; a
  real one needs the placed openings. `docs/reports/wp-9.2-the-parti-is-not-the-type.md` §8.
- **A SLUG IN A CODE SPAN IS NOT CHECKED, AND THAT IS 65% OF THE LIVE NAMESPACE (WP-9.2 audit).**
  `check_citations.py` blanks inline code spans before scanning -- deliberately, so a document can
  write `OQ 82 and 84` to illustrate a bug. **That exemption was written for the NUMBERED namespace
  where prose is the citation form; for slugs the convention is inverted** and
  `` `oq/the-raw-kit-read` `` in backticks IS how this corpus cites a named question. Measured **at `84314fa`: 113 inside code spans (unchecked), 56 in plain prose (checked), 169
  total, and 10 of the unchecked name no entry.** The figure MOVES as documents discuss it -- it
  was 100/53/153 with 5 unresolved two commits earlier, and the entry raising the question added
  five more illustrative slugs of its own, which is the finding demonstrating itself. Quote it with
  a commit or not at all. Mutation-tested
  -- a fake slug in prose is caught, the same fake slug in backticks passes silently. **Do not just
  delete the exemption**: of the 100 unchecked, 95 resolve and the 5 that do not are all deliberate
  -- `oq/no-such-question` is this checker's own test fixture and `oq/span-partial-bearing-wall` is
  the illustrative slug `oq-two-id-namespaces` uses to explain the scheme. The blind spot is
  load-bearing, which is why this is a question and not a patch.
  `oq/a-slug-in-a-code-span-is-not-checked`. Nothing is dangling today; the guard would not notice
  if it were.
- **A GROUPING RULE AND A ROOM RECORD CAN DISAGREE AND NOTHING CHECKS THE CLASS (WP-9.2 audit).**
  `check_addresses.py` polices pack-vs-pack and kit-vs-pack at one address and **does not see
  groupings at all**. FIVE instances, all pre-existing, found by hand:
  the passage (four floors across four files, and `passage-that-is-a-corridor`'s own note
  contradicting its own unconditional test); **the piazza**, where `piazza-and-single-house-core`
  demands `piazza_depth_ft at-least 10` HARD while `rooms/piazza.json` bands [8,14] and cites
  *"the measured Charleston piazzas run 8 to 12 ft"* -- so a 9 ft piazza is inside the band, inside
  the cited measurement, and fails a hard rule; **the bedroom**, where the grouping says at-least
  10, the band floor is 11 and the record's own prose says the ABSOLUTE floor is 9 -- on
  `secondary-bedroom-cluster`, which **14 partis carry, more than any other**; the sleeping porch,
  where an unconditional at-least 8 meets a record whose floor is conditional ("NINE FEET IF THE
  BED RUNS ACROSS, seven if it runs along"); and the ridge pair under two names.
  `oq/a-grouping-rule-and-a-room-record-can-disagree`. **The WP-9.2 report originally called the
  ridge pair "the first instance found in it" -- extending the method found three more in twenty
  minutes**, which is WP-8.6's lesson applied to that report's own author.
  **Do not reconcile any of them by picking the stricter or the looser number to make a checker
  green**: three of the five have a source on one side only and it is not consistently the same
  side, and at least one is a conditional floor with no axis to be conditional on, which is
  `oq/register-is-not-style`'s first customer.
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
  named exemplars have six enclosed spaces apiece** — Drayton Hall 70'-5" x 52'-2" (HABS SC-377),
  Gunston Hall 60'-10" x 40'-11½" (VA-141), Hammond-Harwood **49 ft wide on the house's own institution's
  figure** (MD-251's 1940 "approximately 44x42'" is an approximation and is low). The placed
  Tidewater plan is 60.0 x 40.0 ft — **within a foot of Gunston Hall on both dimensions** — and
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
- **WP-9.5 AUDITED WP-9.1 AND WP-9.2 AND FOUND 7 BLOCKING DEFECTS, ALL IN THIS SESSION'S OWN WORK
  AND FOUR OF THEM IN CORRECTIONS IT HAD ALREADY MADE.**
  `docs/reports/wp-9.5-the-adversarial-audit.md`, and the one to read first before trusting a
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
  run `build/gen_open_questions.py`. It holds **118 entries, of which 44 are open**
  (7, 8, 9, 10, 11, 18, 36, 37, 38, 39, 40, 64, 66, 67, 68, 72, 73, 74, 75, 76, 77, 79, 86, 87, 91, 92, 93, 94, 96, 98, oq/a-baked-pack-value-is-a-second-delivery-path, oq/a-daily-route-is-an-editorial-model, oq/a-grouping-rule-and-a-room-record-can-disagree, oq/a-kit-binding-propagates-to-descendants-nobody-read, oq/a-licence-conditioned-on-the-wrong-axis, oq/a-massing-states-its-structure-and-nothing-reads-it, oq/a-material-neutral-assembly-decides-a-material-question, oq/a-slug-in-a-code-span-is-not-checked, oq/applies-when-means-two-things, oq/the-parti-dissolved-its-own-dependencies, oq/the-passage-is-divided-and-the-corpus-has-no-word-for-it, oq/the-proportion-band-forbids-the-square, oq/the-raw-kit-read, oq/two-id-namespaces).
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
  - **OQ 51 (RULED 25 Aug, and the largest thing outstanding — this is the next work)** — the
    lineage cascade delivers packs nobody bound. **Ruling: adjudicate first, flip second.** Work the
    gaps nobody has judged, in leverage order; where the inherited pack is right for the node, add
    the node to that pack's `applies_to` — that IS the adjudication, and it moves the gap from
    unendorsed to endorsed; where it is wrong, bind the right pack or scope the edge. When
    `unendorsed` approaches zero, add `inherits_packs` and make inheritance opt-in, at which point
    it is a safety net rather than a cliff that strands 287 gaps in one commit. Doing it the other
    way round was costed and refused: opt-in now is a morning of mechanism and a corpus-wide
    stranding.
    **The meter, corrected 28 Aug 2026 (WP-8.2) and read the correction before any older figure.**
    `build/check_inheritance.py` pins three ceilings that may only go down -- **287 role_gaps**,
    **3,356 inherited_packs**, **249 unendorsed** -- and one FLOOR that may only go up,
    **judged 48** (endorsed + declined). The published 294/3,367/233 and 293/3,366/222 were both
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
