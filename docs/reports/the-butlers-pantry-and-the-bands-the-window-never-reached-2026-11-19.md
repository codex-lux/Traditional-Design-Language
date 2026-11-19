# The butler's pantry, and the room bands the window never reached (19 Nov 2026)

*Status: built, `37b9886` (the prover) and `4c7de6d` (the walk). Raised by PR #45's CI, where Lucas
ruled the same day that `tests/test_composition.py`'s service-room row asks the rear of every room
the corpus classes as service or work. Done as the suggested task "Fix the proof's butler's pantry
on the entrance front", in this session.*

## I. What was asked

Under that ruling the row went red on a true conviction. On `plans/tidewater-georgian-careful.json`
the proof (`engine="cp"`) drew the butler's pantry at y 0..14 of a 37 ft depth, on the entrance
front, inside the main block. `rooms/butlers-pantry.json` says it "must not be on or visible from the
entry sequence". On `6fcc665`, Phase 17's base, the proof drew it at y 23..37. The task: find why it
moved, and fix the placement without loosening the test.

## II. What was found: the pantry was one symptom of a house drawn with no room bands

Read off the solver's own record (`attempts`, `downgrade_rounds`), one run on `cbc714a`:

- **The ladder.** It released every rank down to shape: round 0 walls, 1 axis, 2 tiling, 3 hearth,
  4 shape. Round 4 released all 24 shape pins on a conflict core naming 3 of them. That is WP-11.7's
  whole-rank release, measured there as converging where the narrow release does not.
- **The reinstatement pass.** It offered the kinds back highest rank first:
  - `restore shape x24` came back INFEASIBLE;
  - `restore hearth x3` came back OPTIMAL;
  - then single pins, until its 6 s window closed after two shape pins.

**22 of 24 room bands stayed released** for want of time, not on any proof. So the drawing room was
drawn 45 x 10 across the whole rear, the dining room moved to the middle, and the butler's pantry
moved to the front. The lower-ranked hearth was held. That inverts `geometry_cp._RANK`, which ranks a
room's own band above the hearth. A rank orders conflicts, and here it was the clock that decided.

The base `6fcc665` drew the drawing room 18 x 22 at the front and the butler's pantry at the rear.
Swapping only `geometry.flank_sizes` and `geometry.blocks_for` back to the base's did not restore it.
So the movement is the Phase 17 prover (`01f11b2`), not the wing's re-sizing that moved the search's
entrance rows the same day.

## III. What was built

`geometry_cp._solve_cp` keeps `cored`: for each kind, the pins any round's conflict core actually
named. In `_reinstate`'s whole phase, when a kind's whole restore fails, the kind **less its cored
pins** is offered back in one solve, labelled `restore {kind} xN outside the cores`, before the
singles.

A core is sufficient and not minimal, so this is a guess and not a proof. Failing costs one solve,
and the singles run as before. A pin restored this way is restored on its own evidence at this
footprint, like any other.

## IV. What it measured

On the Tidewater record, `engine="cp"`:

| | before (`cbc714a`) | after (`37b9886`) |
|---|---|---|
| shape pins released | 22 to 23 of 24 | 6 to 7 of 24 |
| objective | 1041.6 | 384.8 |
| drawing room | 45 x 10 at the rear | 18 x 22 at the front |
| butler's pantry | x 0, y 0..14 | x 0, y 23..37 |
| refused for | tiling | **hearth, tiling** |
| service-room row | red | green, 3 runs of 3 |

**The cost is the last row but one.** The extra solve takes the half-window the hearth's whole
restore used, so the proof holds the room bands and not the hearth. That is `_RANK`'s stated order,
and it is recorded here rather than netted off. The house was refused before and is refused after,
so its drawability does not move.

## V. Its reach, measured

- **The sixteen shipped plans.** Swept serially on each tree, only the Tidewater record takes the new
  step: `outside the cores` appears in no other plan's attempts. The wall-count movement seen on
  others is the prover's wall clock, and it shows on both trees.
- **The model.** `_build` is untouched, and `tests/test_cp_elements.py`'s model hashes are unmoved
  (12 of 12).
- **The prover-touching test files.** All 25 files that solve with the prover were run on the change:
  15 failed / 638 passed / 37 skipped.
  - 14 are `tests/test_sheet_coherence.py` gate rows, exactly the 14 CI's shard 1 failed on `668b877`
    before the change, row for row.
  - The 15th is `test_solver`'s half bound, ruled to stay red.
- **CI on `37b9886`.** It agrees with that attribution:
  - shard 6 is the spec Colonial's half bound;
  - shard 5 holds the gate after the new file repacked the shards, and has only gate rows, with the
    Tidewater hearth row down from 2 of 3 fires to 1 of 3;
  - shard 3 is `check_partis`.
- **The composer.** It was composed on each tree; see §VII.

## VI. The guard

`tests/test_reinstate_outside_the_cores.py` makes two assertions on the pass's own record. They are
COULD NOT EVALUATE where the proof is not reached.

- Where `restore shape x24` fails, the next attempt is the kind less its cored pins.
- At most 12 of 24 bands stay released; it was 22 or 23 before and is 6 or 7 now.

Two mutations were tried, and both turned both assertions red:
- the step removed (`if False:`);
- the cores never recorded.

## VII. The walk, which the same CI raised

PR #45's workbench job died twice on `cbc714a`, at `walk.mjs:915` and then at `walk.mjs:567`, before
the check that commit changed. Both were timeouts waiting on the bench.

- A reload of the bench boots a CP-SAT evaluate. The walk's own comment measures it at 28.1 s before
  the sheet arrives, and an explicit solve's rounds add about 36 s.
- The reload waited for `networkidle` inside Playwright's default 30 s, and the loupe click used the
  same 30 s default.
- `37b9886`'s job died at line 567 a third time, which settles the cause.
- `4c7de6d` gives the two bench reloads `load` and lets their existing 150 s and 90 s selector waits
  wait, and makes the loupe click wait for the sheet. No assertion changes.

The composer comparison (§V) is appended below when it lands.

## VIII. Not done

- **The hearth.** Holding both the bands and the hearth wants either more time in the reinstatement
  window or a different first step. That window has no share of its own by R12 of 30 Oct 2026, and
  changing it is a ruling: `oq/the-reinstatement-pass-gets-no-time-after-an-undecided-portfolio`.
- **The search's own butler's pantry** is not touched; the row asks it of the proof.
- **The six cored shape pins** stay released. They are the rooms the cores named, and freeing them
  needs a footprint or a programme change, which is the house's question and not the pass's.
