# The deciding pass over the pool: one worker returns a house that may be drawn

*26 November 2026. The second package of the day on the stock brief, after
`docs/reports/the-prover-decides-2026-11-26.md`. That package left its acceptance bar unmet in two
places: on one worker nothing in the returned set could be drawn, and the native double pile was
refused. This one takes the first. The second is the garage and the service wing, and it is not in
this package (§VII).*

Every figure was measured on one four-core container on 26 November 2026. A solve under a wall
clock is a draw, so each figure carries its worker count. The measuring scripts were scratch files
and are not in the tree.

## I. The finding

The composer fills a short set from its ranked pool, a whole placement each, in score order, and
stops after four placements that were not proven impossible. On the stock brief the pool, in score
order, is:

| | diagram | at its derived depth, one worker |
|---|---|---|
| 1 | octagon-radial | refuted, 1.1 s |
| 2 | connected-farmstead | refuted, 1.5 s |
| 3 | courtyard-and-portal | undecided at 25 s |
| 4 | foursquare-quadrant | undecided at 25 s |
| 5 | **side-hall-townhouse** | **holds every fact posed, 10 to 11 s** |
| 6 | tower-villa | refuted, 8.7 to 9.1 s |
| 7 | ranch-tripartite | undecided at 25 s |
| 8 | great-hall-h-plan | refuted, 0.6 to 0.7 s |
| 9 | charleston-single-piazza | refuted, 15.6 to 16.3 s |

The one house that holds stands fifth. The four placements ahead of it took the cap or the set's
time, and on one worker the side hall was not reached: the one-worker run on the last package's
final code returned no house drawable where judged.

## II. The rulings

Lucas answered four direct questions on 26 November 2026, each as its own act. The question and
the answer were written separately.

1. **The double pile: the garage is its own mass.** Not built here (§VII).
2. **The pool order: a short deciding pass.** Probe each pool diagram first, place the ones that
   hold every fact before the rest, and say on the card that the pool was probed.
3. **The pass order stands**: first placements, the pool-fill, then repairs and retries.
4. **Watch PR #47**, attribute its CI by test id, and fix only what is this branch's.

One thing in my wording of option 2 was wrong, and I told Lucas when I measured it: I called the
probe "a few seconds". It cannot be. The side hall takes 10 to 16 s on one worker, so the cap is
25 s (§III).

## III. What was built

**The probe** (`geometry_cp.probe_all_facts`). It asks one question of a composed record: does it
hold every type fact posed at its derived depth. It is the portfolio's own first walls-released
hard step. `_hard_model` builds that step for `_solve_cp` and for the probe, so there is one model
and not two. Its answers are `held`, `refuted-at-the-derived-depth`, `undecided` and
`could-not-evaluate` with a reason.

- **A refutation at one depth is never called proven.** The portfolio goes on to try 2 and 4 ft
  deeper, and `solver.all_facts` says proven only where all three are infeasible. WP-17.5
  measured the reason on another brief: the composed foursquare was undecided at its derived
  depth at 30 s and held every fact two feet deeper.
- **The cap is 25 s, measured.** One worker, the stock brief's pool: held in 3.1 s (living hall)
  and 10 to 16 s (side hall); refuted in 0.2 to 21 s; six undecided at 25 s. A 5 s cap finds the
  living hall alone.

**The answer carries into the placement.** Where the composer asks, the answer is kept under a
hash of the exact model: its constraints, the line grid's, the hint and the seed. The placement
that follows builds the same model and does not solve it again.

- An infeasible answer is a proof and stands.
- A placement found is a placement of that very model, and goes straight to the polish.
- An undecided answer stands in only where the probe had at least the step's time and workers.
  It stays tagged `H:UNKNOWN`, so `geometry._cp_undecided` still reads the solve as undecided and
  the solve cache does not keep it.
- The attempt reads `probed`, with the probe's own seconds and workers.
- The answers are forgotten when the fill ends, in a `finally`. Nothing crosses a request.

Measured through the composer's own call (`revise.revise`), one worker: the living hall's, the side
hall's and the double pile's placements each read `hard1 probed` and did not re-solve the step.

**The pass** (`compose.probe_the_pool`, `compose.pool_probe_order`).

- Before the fill places anything, the pool is probed in score order.
- The pass may spend half of what the set has left (`POOL_PROBE_SHARE`), and it stops as soon as
  it has found as many holders as the set is short.
- The fill then places the holders first, the diagrams nobody could call next, and the ones
  refuted at that depth last, each group in score order. Nothing is dropped.
- `POOL_FILL_PLACEMENTS`, the proven-uses-no-slot rule and the set's deadline are unchanged.
- The search is not probed, and neither is a full set.

**What a reader sees.** `pool_fill.probed` lists each diagram asked, in the order asked, with its
verdict and its seconds. `pool_fill.probe` says the cap, the share, the seconds spent and what
ended the pass. A reading line says it in words. The Candidate Set shows the list under a glossary
record, `pool-probed-first`; `held` is the only verdict inked as a finding, and a refutation at one
depth is never inked as a refusal.

## IV. The stock brief, before and after

`compose(briefs/family-georgian.json, 4)`, the app's own call, set budget 560 s.

| workers | | runs | not refused | drawable where judged | leads the set |
|---|---|---|---|---|---|
| 1 | before | 1 | 2 | 0 | the living hall, placed and not drawable |
| 1 | **after** | 3 | 3, 3, 3 | **1, 1, 1** | **side-hall town house, all three** |
| 4 | before | 2 | 2 and 3 | 0 and 1 | side hall in one of two |
| 4 | **after** | 3 | 4, 3, 4 | **1, 1, 1** | **side-hall town house, all three** |

The "before" rows are the acceptance runs of `docs/reports/the-prover-decides-2026-11-26.md`, on
its final code.

**On one worker the three runs agree to the diagram.** The pass asked all nine, in 114 to 116 s.
The fill then placed the side hall (not refused, drawable where judged), the courtyard (not
refused, not drawable) and the foursquare (refused for bearing, stacks and tiling), and stopped on
the set's time with six diagrams not reached.

**On four workers** the pass took 96 to 100 s and found the same single holder each time, in 6.2
to 8.2 s. The fill placed the side hall, the courtyard, the foursquare and the ranch. The ranch was
not refused in two runs and refused for tiling in the third, which is the run that returned three.
The second run had brief contention from this session's own checks; its figures are in the same
band as the other two.

**One thing the order costs.** A diagram refuted at its depth is placed last now. Before, the
octagon and its like were placed early, refused, read PROVEN and used no slot of the cap, so the
card named them with that word. In the second four-worker run the cap stopped the fill before
them, and five diagrams read "not placed" where they would have read "proven". The probed list
still names each with its verdict.

**What it costs.**

- The pass spends about 100 to 115 s of the set's 560 s. On four workers the fill would have
  reached the side hall without it in one run of two.
- The retries of the two undecided native diagrams were not begun in any run, before or after:
  the set had under a placement left by then.
- **The set's time is now spent to the end on one worker.** The runs took 603 to 606 s of wall
  clock: about 43 s for the declared pass over every diagram, which is before the set's clock
  starts, and then the whole 560 s. Before, the fill stopped on its cap with 47 s unspent.
  I first read the 603 s as an overrun of the budget and it is not one: the deadline is taken
  after the declared pass.

## V. The second brief

`compose(briefs/bungalow-small.json, 4)`, one run each, before on a worktree of merged main.

| workers | | wall | not refused | drawable where judged | pool placements |
|---|---|---|---|---|---|
| 1 | before | 502 s | 5 | 4 | 8, four of them proven and free |
| 1 | after | 437 s | 5 | 5 | 3 |
| 4 | before | 264 s | 4 | 4 | 2 |
| 4 | after | 298 s | 4 | 4 | 2 |

- **One worker.** The pass asked nine diagrams in 37 s: two held in a tenth of a second each (the
  dogtrot and the shotgun), six were refuted in under four seconds, and the single pile was
  undecided at 25 s. The fill placed the two holders and then the single pile, which came back
  drawable where judged. Before, the single pile's placement was refused for stacks and tiling.
  By the rule its placement skips the derived depth on the probe's undecided answer, since the
  step's allowance is under the probe's 25 s, and that leaves the deeper steps more time. I did
  not read the record to confirm it, and one run does not show that it is why.
- **Four workers.** The pass found two holders in 6.7 s and stopped. The set is the same as
  before. The 34 s of extra wall clock is one run against one run.
- On both, the set already held two drawable houses of the four asked, so this brief was never
  the failing case.

## VI. PR #47's CI, attributed

The run on `cc98832` failed four corpus shards and the workbench job. Every red was read by test
id.

| where | red | whose |
|---|---|---|
| shard 3 | `check_partis.py`, and `test_parti_composability` | the known pair: 19 of 21, the cape's chimney unjudged and the side hall's front convicted |
| shard 4 | `test_compose_budget::test_the_set_loop_and_the_named_diagram_read_the_one_share` | the 19 Nov repair's (`fdfb0ff`). **Fixed here** |
| shard 5 | 15 rows of `test_sheet_coherence.py` | the gate, red by design |
| shard 6 | `test_solver`'s half bound, 18 of 35 | known, not loosened |
| workbench | the walk, three failures | one this branch's and **fixed here**; two a placement's draw |

**The compose-budget test.** It refuses the string that asks a placement under the whole compose
budget whatever its share. The repair's commit wrote that string back for the repair's own
placement, and the test has been red since. The repair is ruled a placement at the compose budget,
so the figure is right. Its limit is derived from the repair's share by `placement_time_limit_s`
now, the one spelling, and it is the same 60 s. The test is unchanged.

**The walk.** PR #47 was merged while this package was in progress, so there are three walks to
read: main before the merge (`323ad8a`, 5 failures), the PR's head (3) and the merge commit (2).
The walk's subject is `good-03`, placed on the prover under a wall clock.

- **"the sheet states the doors it could not draw" is this branch's.** It failed on the PR's head
  and on the merge commit and passed before. The check demanded an undrawable-door line. With the
  line grid the prover places every door of `good-03` (measured here: 21 door records, none
  unplaced; the walk drew 11 marks where main's drew 5 and named 6), so the sheet rightly prints no
  such line. The check is re-cut onto its property: every declared door pair is drawn or named. It
  passes in both states and fails a sheet that does neither. **The walk was not run here** after
  the re-cut; its arithmetic was checked against the record (11 pairs) and both logs.
  *(Corrected 27 Nov 2026: it has been run twice since. See §VIII.)*
- **The two porch-label failures are one placement's.** They are on the PR's head and not on the
  merge commit, which is the same tree. The porch was drawn 8 by 35 ft in that draw and its label
  did not fit. A label that cannot fit a slot room is a real defect of the sheet and an old class;
  it is not fixed here.
- "every classified finding row carries its class tag" failed on main before and after the merge
  and not on the PR's head. It is older than this branch.

The walk also still ends red on other draws. That is the 16 October ruling's state, and it is not
this package's.

## VII. What was not done

- **The garage as its own mass, and the service wing.** Ruled the same day. A second session
  (titled "Rule on and fix the double pile's service wing") was started on it from a task card
  before this package began, on a branch of its own, so this session left `compose.attach_garage`,
  `geometry.flank_sizes`, `geometry.blocks_for` and the parti alone, and told that session which
  ruling had been given. **So the native double pile is still refused on the stock brief, proven,
  and the acceptance bar of two drawable houses with the native one among them is still not met.**
- **The probe asks one depth.** A diagram that holds only two feet deeper reads undecided or
  refuted and is placed after the holders. Probing three depths would triple the pass.
- **The five-part and the single pile** are still undecided in their time.
- **The living hall** still reads not drawable, for its cross-level landing-to-stair door.
- **The whole build was not run** in this package: see §VIII for what was.

## VIII. Tests

`tests/test_pool_probe.py`, 22 tests, in two halves.

- **The prover's**: the four verdicts and that none is the word proven; the record is not written
  to; one worker with the grid off is could-not-evaluate and marked as the box's; a record with no
  footprint is the record's; nothing is kept unless asked; the key moves with the record and the
  seed; the kept placement satisfies a fresh build of its model (bounded by deterministic time);
  the placement takes the answer and says `probed`; a refutation at one depth leaves the two
  deeper steps asked; an undecided answer stands in only with the step's time and workers; a
  skipped undecided step is still read as undecided.
- **The composer's**: the pass asks in score order and stops at enough holders; it is held to its
  share and a probe never gets more than is left; it says when it reached the end of the pool; a
  box with no prover ends it with no verdict on any diagram; the fill order; the reading line; and,
  through the composer with every verdict stated by a spy, that a holder far down the pool is
  placed first inside the cap, that the search and a full set are not probed, and that the answers
  are forgotten whatever ends the fill.

One app test (`everyPick.test.mjs`) holds the Candidate Set's reader. Three spy-based composing
tests that compose on `auto` now state that no probe can run (`conftest.stub_pool_probe`), because
their placer is a spy and the probe would otherwise put the real prover to each pool diagram.

**Mutations.** Twenty-four, each a defect injected into the code, asserted landed, and restored
byte for byte: ten in the prover's half, twelve in the composer's, two in the app's reader. All
twenty-four went red on the first run. Among them: a refutation worded as proven; an undecided
answer standing in whatever the step's time; a one-depth refutation answering the deeper steps; a
kept placement that is not the model's; the answers outliving the fill; the search probed; the
fill ignoring the probed order; the pass taking all of what the set has left.

The walk's re-cut check has no mutation run behind it.

**The walk, run twice on 27 Nov 2026** on this tree, the app built, one four-core box, the
fallback face (no route to the webfonts here).

| run | ok | failed | the re-cut door check |
|---|---|---|---|
| 1 | 696 | 26 | failed: 0 drawn + 0 named of 11 pairs |
| 2 | 722 | 2 | passed: 5 drawn + 6 named of 11 pairs |

- **Run 1 drew no sheet.** After the re-solve the bench showed a refused placement for the full
  150 s wait, so 24 checks that read the sheet failed together, the re-cut one among them. That
  is the check doing its job on a sheet that draws nothing. The same wait ran out twice on
  PR #45's runner (the walk's own comment of 19 Nov records it). It is one placement's draw.
- **Run 2 drew the sheet and the re-cut check passed** in the state where six pairs are named and
  five drawn. The other state, every pair drawn, was not met in either run.
- **The two failures of run 2** are "the class counts sum to the findings the sheet shows" and
  "every classified finding row carries its class tag". Both fail on main's CI walk of `323ad8a`,
  and the second on main's `ea25d12` too. They are older than this branch.

**What was run.** `tests/test_pool_probe.py` and `tests/test_compose_budget.py`: 37 passed. The
neighbouring files (`test_compose_passes`, `test_joint_proof`, `test_refusal_repair`,
`test_refusal_retry`, `test_line_grid`, `test_cp_portfolio`, `test_cp_elements`,
`test_determinism`, `test_modcache`): 121 passed. `everyPick.test.mjs`: 22 passed.
`check_glossary`, `check_counts`, `check_citations` and `check_ids` are green. ~~The whole
`check_all.py` was not run on this tree; CI on the pushed branch is the first whole run.~~
*(Corrected 27 Nov 2026: CI runs on a pull request only, and these commits have none. The whole
build was run here the same night; see below.)*

**The whole build, 27 Nov 2026.** `build/check_all.py` in four `git worktree` shards of `3ed01a5`,
run together on one four-core box. Each shard reads `1 of N checks failed`.

- `tests/`: 18 failed, 4,138 passed, 147 skipped. The server suite: 506 passed, 19 skipped. The
  app suite: 902 of 902.
- Three checks could not be evaluated: `check_frontend.py` (no built `dist/`), and the DXF and IFC
  selftests (neither library is installed here).

Every red, by id:

| red | whose |
|---|---|
| 15 rows of `tests/test_sheet_coherence.py` | the gate's, red by design. The same 15 ids as PR #47's CI run, compared by id |
| `tests/test_parti_composability.py` and `check_partis.py` (2 errors) | the known pair: one finding, two readers |
| `tests/test_solver.py`'s half bound | known, not loosened |
| `tests/test_axis.py::TestTheCriticReadsIt::test_the_shipped_passage_is_on_centre_after_wp_11_2` | the prover's draw under a wall clock; older than this branch |

`tests/test_compose_budget.py` is green, as fixed in §VI.

**The axis row was attributed by running it.** It pins the proved Tidewater spine at
`could-not-evaluate` and read `on-centre` in the shard. Run alone on a quiet box, alternating this
tree and a worktree of main's `ea25d12`, three rounds:

| round | this tree | main |
|---|---|---|
| 1 | passed | **failed, `on-centre`** |
| 2 | passed | passed |
| 3 | passed | passed |

Main's own tree gives the second reading one time in three with nothing else running. So the two
readings are two draws of one wall-clock solve, and the red is not this branch's. The test is not
re-pinned and its open question is not closed: its message asks for that only where `on-centre`
is the house's reading, and here it is one draw of several.
