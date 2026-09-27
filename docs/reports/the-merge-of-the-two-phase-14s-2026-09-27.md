# The merge of the two Phase 14s (27 Sep 2026)

*The ink held to its plates* (this branch: WP-14.1 through 14.6 and the audit of the phase) and
*the dossier and the journey* (main: WP-14.0 through 14.33, merged there as far as PR #39) ran in
parallel from `d565dea`. At the merge main was 110 commits ahead of the branch and the branch 38
ahead of main, the last of them the audit's close. This is the record of how the two were joined.
Read it before trusting a figure either line published.

## I. The rule, and the numbers

The rule is the one the three earlier line merges followed
(`docs/reports/the-merge-of-the-two-phase-11s-2026-09-08.md` §I): **where both lines built the
same thing, main's spelling survives and this branch's behaviour is ported into it.**

- **Both Phase 14s stand.** Neither is renumbered, and both boards' rows stand, as the two Phase
  8, 9 and 11 rows do.
- **WP-14.1 through WP-14.6 each name two packages**, one on each line. A report is cited by
  FILENAME.
- **Pushed commit subjects on both lines carry the numbers and cannot be rewritten.** So a
  renumber would buy a tidier board and leave the history saying the old thing.

Seventeen files conflicted on the head that ships, and sixteen in the rehearsal: between the two,
both lines had fixed the same test (§II). Nine more were changed on both sides and merged with no
conflict. Each of those nine was re-read, because a clean merge is where two lines' assumptions
meet unseen. Every resolution was rehearsed in a worktree with `rerere` recording it, and replayed
on the head that ships.

## II. What conflicted, and how each was resolved

- **`build/profiles.py`: main's wall datum, ported into this branch's geometry.** Main's WP-14.4
  gave `pack_geometry` a `datum="wall"` for the 27 packs with no column stack. This branch's
  WP-14.2 had replaced the function's die, its group reading and its output keys. The merged
  function keeps this branch's reading and takes main's datum whole. Under the wall datum:
  - every assembly stands on 0 and reads `"wall"`;
  - the die is the wall plane (`die_naked_in` 0.0, status `"wall"`);
  - the output gains `"datum": "wall"`.

  Main's own wall-datum tests hold this over all 50 (pack, assembly) cases of the 27 stackless
  packs, on the merged tree: every naked is 0, every datum reads "wall", and no face stands
  behind the plane.

  **A case neither line had.** One member under the wall datum publishes no projection:
  `moorish-arch`'s arch. Main drew it flush; the merged tree draws it as this branch's ghost, at
  the naked and dashed. Its ticks need a length where there is no radius, so they take a tenth of
  the greatest published relief, which is `silhouette`'s own default and as linear in the module.
- **`mcp_server/core.py`: both field sets.** This branch's plate fields (`stack_notes`,
  `assembly_datum`, `unpublished`, `bbox_in`) and main's `module_bound_to` are both served. For a
  stackless pack the plate fields are computed the way main dimensions it: one assembly at a
  time, at the wall datum, with `bbox_in` null. Before the merge this branch served those packs
  nothing at all.
- **`workbench/server/corpus.py`: main's pack row, with `overlay_of`.** Main's row carries
  `drawing`, `module_bound_to`, `thumb` and `conflicts`. Its `overlay_on` became `overlay_of`,
  which this branch's WP-14.2 found is the schema's key; no pack carries `overlay_on`.
- **`workbench/app/src/surfaces/Proportions.jsx`: main's page, this branch's order plate.**
  - Main's rewrite survives: the index, `PackList`, `AssemblyPlate` and the URL.
  - `OrderPlate` keeps this branch's reading through `proportions/plate.js`.
  - Main's one edit to the old plate, dropping OQ 65 from its caption, was ported into
    `plate.js::datumWords`, which now holds that sentence, and into the order tool's template.
    Main had ruled, in `readerCopy.test.mjs`, that reader-facing copy states no corpus fact and
    cites no question a reader cannot look up. This branch's sentence did both ("the corpus uses
    both … (OQ 65, OQ 78)").
- **`workbench/app/src/sheet/Sheet.jsx`: this branch's lifted note, with main's fix.** This branch
  moved the plate note into `derive.js::plateNote`. Main's one change to it, reading the
  convention's own figures where it had typed "9 in and 5 in", was ported there. It prints the
  same words today and cannot drift.
- **`workbench/app/src/marks.test.mjs`, added on both sides, as two different files.** They test
  two different modules. Main's stays; this branch's is `src/sheet-marks.test.mjs`, and the two
  comments that named it were changed with it.
- **`workbench/app/e2e/walk.mjs`: main's navigation, this branch's every-pack loop.** Main
  reaches a pack by its link and asserts the address it writes. This branch walks every order pack
  the API lists, where the old walk walked three.
- **`tests/test_hearths.py` and `tests/test_hearths_on_flue.py`: main's re-cuts survive.** Both
  lines found the same solve-cache poisoning and the same breast test fed its answer, on the same
  day. Main's fix also has a general guard in `test_determinism.py`. What main lacked was ported:
  the working plate's ghost of a refused fire, which main's re-cut never read. This branch's
  duplicate private cache was dropped.
- **`workbench/server/tests/test_parti_confinement.py`: main's, word for word, and the one conflict
  the rehearsal did not have.** Both lines found that the up-and-back escape target typed the
  repository's directory name, so the test went red in any checkout of another name while the
  code was right. Main found it at its WP-14.9, the ink line in the audit's own whole build. Both
  replaced the literal with the SAME line, reading the checkout's own name. Only the comments
  differed, and main's survives.
- **`build/build.py`**, where both lines found `dist/orders.html` unregenerated, keeps both
  paragraphs. **`schema/proportion-pack.schema.json`** keeps both field sets, `alternative_to`
  and `alternative_note` beside `axis` and `zones`, with no path from either parent lost.
  **`workbench/server/tests/test_grammar_agreement.py`** reads both surfaces.
- **`CLAUDE.md` and `PLAN-OF-ACTION.md`**: both lines' entries and rows stand, under a header
  saying there are two Phase 14s.
- **`dist/orders.html` and `docs/open-questions.md` are generated**, and were regenerated rather
  than merged.

## III. What the clean merge would have let through

- **Main's copy ratchet** (`copy_ratchet.test.mjs`) pins every app sentence of twelve or more
  words, by identity, to its file. It failed three ways on the merged tree:
  - nine STRING rows had moved from `sheet/Sheet.jsx` to `sheet/derive.js` with the note this
    branch lifted;
  - this branch had edited three rows;
  - this branch had added eight.

  **Every row was read before it was classed.** The moved rows keep their class. The edited
  Drawing Set caption keeps `voice`. The eight new rows are statements about the payload in hand,
  so `disclosure`. None states a corpus fact. The baseline's own header records the move.
- **Main's pin on every order's MCP payload moved, and the first merged value was wrong.**
  `STACKED_DIGEST` hashes every stacked pack's `tdl_get_proportions` payload, byte for byte. Its
  comment says no ruling in main's tranche 2 permits a move. It moved, and the movement is the
  ink line's. The harness was proved against both parents first:
  - it reproduces main's value on main's tree and on the common base, because main changed no
    stacked payload at all;
  - on all 175 payloads the merged one equals the base's plus the ink line's own changes, with
    none left over;
  - it reproduces the ink line's own value on that line's tree.

  **The first merged value was still a third value, and the cause was key order.** The
  `core.py` resolution wrote `projection_datum` before `stack_notes`, which changes no field and
  every byte. The keys are in the ink line's order now, the merged payloads hash to the ink line's
  value, and the pin moved there with its proof written beside it.
- **Main's count of a stackless assembly's faces** assumed a side-by-side member after the first
  has no face. The ink line's WP-14.2 gives each one a face flagged `beside`, for a plate that
  draws band by band, and adds nothing to the section. So `moorish-arch`'s arch counted 2 against 1.
  The test now counts section faces and `beside` faces apart.
- **Main's wall-datum test read a key this branch removed.** It asserted `unrecorded == []`. It
  was re-cut against the property the key stood for, that nothing the record states is ghosted
  under the wall datum, and the dead key was not restored.
- **Main's glossary record `figure-drawn-from-record`** quoted two sentences this branch had
  rewritten, and defined the plate as drawing an unconstructable profile "plain". Its definition
  and its basis now say what the drawing does.

  **Chasing it found a stale line of this branch's own.** `docs/proportion.md` still said the
  volute and the acanthus "draw as a swelling", forty-eight lines above the paragraph saying
  WP-14.2 made them envelopes. It is corrected, dated.
- **Main's solve-cache guard convicted eleven of the ink line's tests of the defect they exist to
  prevent.** Main's WP-14.33 scans every test for a function that patches something and then
  solves, and requires the cache isolated: a `setattr(GEO, "_SOLVE_CACHE", {})` call before the
  solve, or a `.clear()` in a `finally`. The ink line's audit isolates by hand instead:
  - it saves the cache, assigns a private `{}`, solves inside a `try`, and puts the saved cache
    back in the `finally`;
  - eleven of its functions do exactly that and patch nothing else.

  The scanner read each assignment to the cache as a patch, found neither of its two spellings,
  and convicted all eleven. **The scanner was taught the third spelling rather than the eleven
  re-spelled**, because the idiom is isolation. It counts as isolation only with both halves:
  the empty dict before the first solve, and the saved cache put back in the `finally` of a
  `try` whose body solves. Without the restore, the private dict stays the module's cache,
  holding whatever was solved under the patch. So that shape is still convicted, and so is a
  dict assigned with entries in it. Both ways are driven, and four mutations are red, one per
  half of the rule.
- **Main's `AssemblyPlate.jsx` draws SVG the ink line's census had never registered, and the
  census then judged a plate the page never draws.** Main draws a pack with no column stack by
  that component, chosen by `page.js::plateKind` from the served `drawing`. After the merge the
  server serves `moorish-arch`, the one order pack with no stack, as assemblies. The census ran
  the order plate's own reading on it anyway and reported two disagreements, R2 and R3, about a
  drawing no reader ever sees. It now judges only what the page draws with `OrderPlate`, which
  is still 25 packs. `AssemblyPlate.jsx` is registered as a producer, and its row says no census
  check reads it.

## IV. The counts, re-collected, each a third value

| figure | the ink line | main | merged | reconciled |
|---|---:|---:|---:|---|
| tests (`pytest --collect-only`) | 3,090 | 2,824 | **3,239** | by name: 149 the ink line's own and 416 main's. The only test either parent has and the merge lacks is main's copy of a base transom test, which the ink line re-cut |
| app suite (`node --test`) | 316 | 659 | **754** | by name: 95 the ink line's and 439 main's. The only one missing is the ink line's copy of a base compose-events test, which main re-cut |
| checks (`TOTAL_CHECKS`) | 53 | 54 | **54** | main's `check_glossary.py` |
| open-question register | 224 / 127 open | 240 / 130 open | **252 / 140 open** | derived by `check_ids.read_questions()` |

## V. Verification

**How the merge was made.** The resolutions were rehearsed in a worktree: the audit's code
(`843b1a3`) merged with main (`08959a2`), with `rerere` recording each resolution. They were then
replayed here, on the head that ships (`72c9458`, the audit's close):

- sixteen conflicts took the recorded resolution;
- the seventeenth is §II's confinement test, where main's file was taken.

The rehearsed tree was then taken whole, and the audit's close was layered on top of it. The only
files the audit's close touched that the merge also changed are `CLAUDE.md` and
`PLAN-OF-ACTION.md`:

- the counts line keeps the merge's third value;
- the ink line's board row keeps the audit's sentence beside main's row;
- the sentence pointing at the counts line was corrected to the merge's figure.

**On the rehearsal, with its fixes in:**

- `tests/test_svg_census.py` and `tests/test_determinism.py`: 116 of 116.
- The whole server suite first came back 2 failed / 412 passed / 15 skipped. Both failures were in
  `workbench/server/tests/test_pack_plates.py`. With the pin moved and the face count re-cut, that
  file passes 23 of 23.

**On this merge, before it was committed:**

- **The prose checkers.** `check_ids` passes. `check_citations` checks 3,201 citations over 808
  files, none dangling. `check_counts` checks 137 claims over 16 files, none stale. Main's
  `check_glossary` verifies 252 records and 768 quotations. The open-question register is
  current.
- **The app suite, run bare:** 754 of 754.
- **`vite build`** is clean but for one warning older than both lines: the atlas's fine coastline
  tier is 1,190 kB.
  - The entry chunk is 679.25 kB against `check_frontend`'s ceiling of 700,000 bytes, and
    `check_frontend.py` passes.
  - Main alone builds the entry at 671.37 kB and the ink line alone at 514.59 kB. So the merge
    adds 7.9 kB to main's entry and leaves 20.75 kB under the ceiling. The next package to add to
    the entry should know that.
- **The targeted set: 266 tests over the files the merge moved and the ones the audit's close
  touched.** 263 passed. The three that did not are one reading.
  - Census O1 holds the orders page to the COMMITTED `dist/orders.html`. That is the audit's C6,
    so that `build.py` regenerating the page first cannot make it agree.
  - Before the commit, that page was the ink line's, which the merged engine no longer produces.
  - The fidelity doc's row and the known-disagreements check moved with it.

**And the first take of the rehearsed tree was one commit short.** The rehearsal's last commit was
made on a detached HEAD. So the branch ref the merge was taken from did not carry it: not main's
scanner taught the third spelling, not `AssemblyPlate.jsx`'s registry row, and not the order-plate
checks' scope. The first targeted run found it by reproducing that commit's reds exactly. The
commit was then applied, and the ref moved to it. **A ref is not a worktree's HEAD: take a
rehearsal by its commit, not by its name.**

**The whole build and the walk were not run before this commit.** They run on it, and CI runs its
six shards on the push.

## VI. What was not done

- **No census check reads main's `AssemblyPlate.jsx`.** It is registered as a producer, and its row
  says every figure it draws is unjudged by the census. Its faces are Python's, held over all 50
  (pack, assembly) cases by main's own wall-datum tests, one assertion of which the merge re-cut
  (§III). Its layout is held by main's `plate/assembly*.test.mjs`.
- **The eleven functions that isolate the cache by hand were not re-spelled** in main's
  `monkeypatch` idiom. The scanner learned their spelling instead (§III).
- **Nothing was renumbered**, and WP-14.1 through 14.6 still name two packages each.
- **Decision 4 still waits on Lucas, and so does the leaf-order question.** The merge changed
  neither.
