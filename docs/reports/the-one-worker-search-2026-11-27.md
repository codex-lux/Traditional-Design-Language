# The one-worker search, and the two branches joined (27 November 2026)

*Status: built. On the stock brief the acceptance bar is met on one worker and on four.*

## I. The result

Lucas's bar for `briefs/family-georgian.json` is two candidates that may be drawn, the native
centre-passage double pile among them, every run, on one core.

`compose(family-georgian, 4)`, one run at a time on a quiet four-core container:

| tree | workers | runs | not refused | drawable where judged | the native double pile |
|---|---|---|---|---|---|
| joined, before this change | 4 | 3 | 4, 4, 4 | 2, 2, 2 | first, 3 of 3 |
| joined, before this change | 1 | 3 | 3, 3, 3 | 1, 1, 1 | refused UNDECIDED, 3 of 3 |
| with the one-worker search | 1 | 3 | 4, 4, 4 | 2, 2, 2 | first, 3 of 3 |
| with the one-worker search | 4 | 1 | 4 | 2 | first |

On every run that met the bar the set was, in order: the double pile and the side-hall town house,
both DRAWABLE WHERE JUDGED with the hearth unjudged; the living hall and the courtyard, placed and
NOT DRAWABLE; the five-part and the single pile, refused and not proven.

The cost is on the second brief and is one run each. `bungalow-small` on one worker went from 5
not refused and 5 drawable in 439 s to 4 and 3 in 287 s (§VI).

## II. The two branches joined

Two sessions answered the same complaint in parallel from PR #47's merge:

- **The deciding pass over the pool** (`docs/reports/the-deciding-pass-over-the-pool-2026-11-26.md`).
  The pool is probed before it is placed, and the probe's answer carries into the placement.
- **The garage is its own mass** (`docs/reports/the-garage-is-its-own-mass-2026-11-26.md`). The
  garage is its own element, the one range stands against the rear wall, and the prover sizes the
  wing.

They were merged at `00b9fab`. Four files conflicted (`CLAUDE.md`, `PLAN-OF-ACTION.md`,
`docs/geometry.md`, `build/geometry_cp.py`'s imports) and both sides' entries stand.

**One interaction, fixed in the merge.** `_solve_cp` sizes a wing before it poses a house, and
`probe_all_facts` did not. So on a house with a wing the probe would have posed a different model
from the placement, and its kept answer would never have been found. `geometry_cp.wing_sized` is
the one call both make. A wing whose box the sizing did not decide leaves the probe
could-not-evaluate. Four tests in `tests/test_pool_probe.py`, six mutations, all red.

The test count at the merge was 4,336, reconciled by name against both parents.

## III. What was measured on the joined tree

All runs one at a time. Wall-clock CP is a draw, so every row says how many runs it is.

**The stock brief, before the change** (`00b9fab`):

| workers | run | wall | returned | not refused | drawable | the double pile's hard steps |
|---|---|---|---|---|---|---|
| 1 | a | 608 s | 6 | 3 | 1 | +0, +2, +4 ft all UNKNOWN |
| 1 | b | 607 s | 6 | 3 | 1 | the same |
| 1 | c | 606 s | 6 | 3 | 1 | the same |
| 4 | a | 565 s | 6 | 4 | 2 | OPTIMAL at +0 |
| 4 | b | 525 s | 6 | 4 | 2 | OPTIMAL at +0 |
| 4 | c | 554 s | 6 | 4 | 2 | UNKNOWN at +0, OPTIMAL at +2 |

On one worker the retry Lucas ruled on 30 Oct was not begun on any run: the set's time was spent.

**`bungalow-small`, before the change**, one run each: one worker, 7 returned, 5 not refused, 5
drawable, 439 s; four workers, 6 returned, 4 and 4, 307 s.

**Both shipped plans**, `geometry.solve(engine="auto")`, four workers, one run each, on the merge
and on both parents. `tidewater-georgian-careful` is refused PROVEN on all three, its hard steps
INFEASIBLE at all three depths. `spec-builder-colonial` is refused UNDECIDED on all three.

## IV. Why one worker did not decide

The wing report gave the declared loop's thirteen resizes as the cause and said a longer budget
was not the lever. Measured on the joined tree, neither holds.

**The record holds on one worker. It is slow, not undecidable.** One walls-released hard step,
one worker, seed 7, the line grid on:

| record | +0 ft | +2 ft | +4 ft |
|---|---|---|---|
| as first composed | INFEASIBLE 3.3 s | INFEASIBLE 29.2 s | OPTIMAL 8.2 s |
| as the declared loop hands it on | OPTIMAL 88.9 s | OPTIMAL 46.9 s | UNKNOWN at 120 s |

The composer gives those three steps about 16, 15 and 10 s.

**No resize is the cost.** The thirteen resizes in five groups, each undone alone from the
handed-on record (posed at +2 ft, 100 s cap) and each added alone to the first-composed record
(posed at +4 ft, 60 s cap):

| group | handed-on record without it | first-composed record with it |
|---|---|---|
| the three chamber closets and the linen press | OPTIMAL 14.3 s | UNKNOWN at 60 s |
| the dressing room | UNKNOWN at 100 s | OPTIMAL 18.5 s |
| the butler's pantry | OPTIMAL 35.1 s | OPTIMAL 36.6 s |
| the two passages | OPTIMAL 32.5 s | OPTIMAL 51.4 s |
| the mudroom, hall bath, porch and powder room | OPTIMAL 9.2 s | OPTIMAL 45.8 s |

Against 46.9 s with all of them and 8.2 s with none. Undoing the dressing room's resize makes the
house slower. The time moves with any change to the record and in no direction.

**The seed decides as much as the record.** The handed-on record at +2 ft, one worker:

| seed | default search |
|---|---|
| 7 | OPTIMAL 46.9 s |
| 3 | OPTIMAL 31.5 s |
| 1 | UNKNOWN at 100 s |
| 2 | UNKNOWN at 100 s |

**The search is the lever.** With several workers CP-SAT runs three full-problem searches side by
side on this model (its own log names them: `default_lp`, `max_lp`, `no_lp`). With one worker it
runs `default_lp` alone. The handed-on record, one worker, 45 s cap:

| search | +0 ft, seeds 7, 1, 2 | +2 ft, seeds 7, 1, 2 |
|---|---|---|
| no LP (`linearization_level = 0`) | OPTIMAL 9.2, 8.7, 8.0 s | OPTIMAL 8.6, 8.6, 8.2 s |
| max LP (`linearization_level = 2`) | UNKNOWN, UNKNOWN, UNKNOWN | UNKNOWN, UNKNOWN, UNKNOWN |
| four workers, seed 7 | OPTIMAL 5.0 s | OPTIMAL 14.3 s |

`interleave_search` on one worker was also tried: UNKNOWN at 119 s at +0 ft, OPTIMAL in 24.3 s at
+2 ft.

**Over the whole pool.** All fourteen diagrams composed for the brief and both shipped plans, one
worker, seed 7, 25 s a step, a step asked only where the one before did not hold:

| record | default search | no-LP search |
|---|---|---|
| centre-passage-double-pile | UNKNOWN, UNKNOWN, UNKNOWN | OPTIMAL 10.7 s at +0 |
| side-hall-townhouse | OPTIMAL 11.2 s | OPTIMAL 7.5 s |
| living-hall-picturesque | OPTIMAL 3.7 s | OPTIMAL 2.3 s |
| gable-front-and-wing | UNKNOWN, INFEASIBLE 21.9 s, UNKNOWN | UNKNOWN, INFEASIBLE 7.8 s, INFEASIBLE 16.5 s |
| cape-central-chimney | INFEASIBLE 21.9 s, UNKNOWN, INFEASIBLE 24.8 s | INFEASIBLE 19.4, 2.2, 1.9 s |
| tower-villa | INFEASIBLE 9.0, 21.0, 23.3 s | INFEASIBLE 7.7, 22.7 s, UNKNOWN |
| hall-and-parlor | INFEASIBLE 18.9 s, UNKNOWN, UNKNOWN | INFEASIBLE 24.9 s, UNKNOWN, UNKNOWN |
| octagon-radial | INFEASIBLE 1.1, 1.3, 1.7 s | INFEASIBLE 1.1, 1.1, 1.4 s |
| connected-farmstead | INFEASIBLE 1.5, 2.8, 1.3 s | INFEASIBLE 1.4, 1.8, 1.7 s |
| five-part, single pile, courtyard, foursquare, ranch | UNKNOWN at every depth | UNKNOWN at every depth |
| shipped `tidewater-georgian-careful` | INFEASIBLE 0.2, 0.2, 0.3 s | INFEASIBLE 0.1, 0.2, 0.4 s |
| shipped `spec-builder-colonial` | UNKNOWN at every depth | UNKNOWN at every depth |

No LP gains one house, is faster on the two other holders, proves three more depths impossible
and loses one at the cap. The shipped Tidewater refusal stays proven at all three depths.

## V. The ruling, and what was built

**Asked of Lucas, 27 Nov 2026, with the tables above:** how should the one-worker gap be closed?
The four options were the no-LP search on one worker; splitting each step's time between the two
searches; leaving the prover and deploying on four cores; and recording only.

**Answered:** "No-LP on one worker (Recommended)".

Built in `build/geometry_cp.py`:

- `hard_step_search(workers)` names the search: `portfolio` above one worker, `no-lp` on one,
  `default` on one where `TDL_CP_ONE_WORKER_SEARCH=default` asks for the control.
- `hard_step_solver(cp_model, cap_s, workers, seed)` builds the solver for one walls-released
  hard step. On one worker it sets `linearization_level = 0`. On several it sets nothing.
- **One spelling, two callers.** The portfolio's walls-released steps in `_solve_cp` and
  `probe_all_facts`. So a kept probe answer is an answer by the search the placement would run.
- **Scoped to what was measured.** The everything-held step, the wing sizing, the ladder, the
  restores, the polish and the undecided round's retry are unchanged.
- **Nothing about the model changes.** A placement found is the ruled model's and a refutation is
  a proof about it. `tests/test_cp_elements.py`'s hashes do not move.
- **The record says it.** The attempt's tag reads `1w no-lp`. The probe's result carries
  `search`. `/api/health`'s `prover` block reports `hard_step_search`.

## VI. The bar re-measured, and what it cost

**The stock brief on the new code** (`7e1cdb0`), one run at a time:

| workers | run | wall | returned | not refused | drawable | the double pile |
|---|---|---|---|---|---|---|
| 1 | a | 560 s | 6 | 4 | 2 | first; OPTIMAL at the derived depth |
| 1 | b | 561 s | 6 | 4 | 2 | the same |
| 1 | c | 555 s | 6 | 4 | 2 | the same |
| 4 | a | 568 s | 6 | 4 | 2 | first; UNKNOWN at +0, OPTIMAL at +2 ft |

On one worker the side hall's probe answered in 7.0 to 8.4 s where it had taken 10.3 to 10.6 s.

**`bungalow-small` on one worker, one run:** 6 returned, 4 not refused, 3 drawable, 287 s. Before:
7, 5 and 5 in 439 s. Two things moved.

- `bungalow-open-linear` held at its derived depth under the default search and was drawable. Under
  no LP that step was UNKNOWN, the +2 ft step held, and the house placed there is NOT DRAWABLE.
- The set filled at four not refused, so the pool-fill placed two diagrams and not three, and
  `shotgun-linear` was not reached.

That diagram's step, on the record the compose places, one worker, 30 s cap, seeds 7, 1 and 2:

| depth | default search | no-LP search |
|---|---|---|
| +0 ft | OPTIMAL 26.4, 21.5, 4.5 s | UNKNOWN, OPTIMAL 21.8 s, OPTIMAL 1.0 s |
| +2 ft | UNKNOWN, OPTIMAL 8.4 s, UNKNOWN | OPTIMAL 11.3, 3.2, 19.7 s |

So at the derived depth the two searches are a draw by seed on this house, and at seed 7 the draw
went against no LP. A survey of the bungalow brief's fourteen diagrams at 25 s a step (composed
at fourteen candidates, so not the same records the compose of four places) found every step the
default decided also decided by no LP within two seconds of it, and two steps decided by no LP
alone. The loss is one diagram's draw at one seed and it is real:
`oq/one-worker-runs-one-search-and-the-seed-decides-as-much-as-the-house`.

**Both shipped plans on one worker**, one run each, the control switch off and on:

| plan | default search | no-LP search |
|---|---|---|
| `tidewater-georgian-careful` | refused PROVEN; INFEASIBLE at all three depths | the same |
| `spec-builder-colonial` | no proof in the budget; placed by the search; refused, class SEARCH | prover placement, FEASIBLE; refused UNDECIDED |

The Colonial's hard steps were UNKNOWN under both, so its difference is the ladder's draw after
them and not the search's.

## VII. Tests

- `tests/test_one_worker_search.py`, 15 tests: the rule's branches, the control switch, the tag,
  both callers through the one helper (a spy), the first step keeping the default, a source
  reading that `linearization_level` is written in one function called from two, and one real
  solve of the composed double pile's hard step on one worker.
- `workbench/server/tests/test_health_prover.py`: one test added, one widened.
- `tests/test_pool_probe.py`: one pin of the deciding pass's own asserted the solved step's tag
  ends in `1w`. It is re-cut onto `hard_step_tag`.
- Twelve mutations of the new guards. All landed, all red, all restored.

**The whole build**, four shards in `git worktree`s of `3ccc78f`, run together on four cores:

| | |
|---|---|
| `tests/` | 17 failed / 4,176 passed / 148 skipped |
| server suite | 507 passed / 19 skipped |
| app suite | 902 of 902 |
| could not be evaluated | no `dist/`; the DXF and IFC selftests (no `ezdxf`, no `ifcopenshell` here) |

Every red is on the last whole build's list by id (`3ed01a5`, 18 reds), and none is new:

- 14 rows of the gate, `tests/test_sheet_coherence.py`. One gate row that was red there passed
  here, `test_every_upper_bearing_line_stands_on_a_ground_bearing_line[careful-cp]`, a prover row.
  The wing package's own `test_the_sheet_is_drawn_at_all[candidate-cp]` is among the 14.
- `test_parti_composability`, with `check_partis.py` (2 errors): one finding through two readers.
- `tests/test_solver.py`'s half bound.
- `tests/test_axis.py`'s proved-passage test, which read the Tidewater spine `on-centre` in the
  shard. Run alone on a quiet box straight after, it passed 3 of 3. It is the prover's draw under
  load, as it was in the last build, and it is not re-pinned.

The collection is 4,337 in this container (no `ezdxf`) against 4,322 at the merge: the 15 added.

## VIII. What was not done

- **The five-part, the single pile, the courtyard, the foursquare and the ranch** are undecided
  at every depth under both searches. They are refused and not proven, on one worker and on four.
- **The one-worker search is still one search.** Its time is heavy-tailed by seed, and §VI's
  bungalow is what that costs. The option Lucas did not take, splitting each step's time between
  two searches, is the open question's first candidate.
- **The declared loop, the step order, every share and cap, the bands, `TILING`, `COVERAGE` and
  `typefacts` are unchanged.**
- **The gate's `candidate-cp` rows at the 40 s batch budget** were not re-measured alone.
- The living hall's cross-level door, the linen press's door, and a roof for the garage's element.

## IX. How to reproduce

```bash
TDL_CP_WORKERS=1 python3 -c "import json,sys; sys.path.insert(0,'build'); import compose; r=compose.compose(json.load(open('briefs/family-georgian.json')),candidates=4); print(r['drawability'])"
```

```bash
TDL_CP_WORKERS=1 TDL_CP_ONE_WORKER_SEARCH=default python3 -c "import json,sys; sys.path.insert(0,'build'); import compose; r=compose.compose(json.load(open('briefs/family-georgian.json')),candidates=4); print(r['drawability'])"
```

Each takes about ten minutes. Run one at a time: two solves sharing a core are not a control.
