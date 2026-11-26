# The prover decides: why every candidate was refused, and what was changed

*26 November 2026. Raised by Lucas against the deployed Workbench: the stock brief
`briefs/family-georgian.json` returned 4 of 4 candidates refused, each reading "not proven: out of
time · refused again on a longer attempt".*

Every figure here was measured on one four-core container on 26 November 2026. A solve under a wall
clock is a draw and not a constant, so each is stated with its worker count and its budget. The
measuring scripts were scratch files and are not in the tree; each run is described so it can be
repeated.

## I. The finding

Three things were wrong, and they compounded.

1. **The model could neither find a house nor prove there was none.** `geometry_cp._build` states
   "the rooms of a level tile their element" as a sum of area products over a `NoOverlap2D`. That
   form propagates nothing until nearly every room is fixed. The composed foursquare with every
   type fact held was UNKNOWN at 60 s on four workers, under every solver setting tried.
2. **On one core the deciding step never ran.** WP-17.5 kept the hard steps to a box with more than
   one core. At `TDL_CP_WORKERS=1`, five of five composed diagrams came back refused for bearing,
   stacks and tiling.
3. **The composer spent the set's time on the houses it could not place.** A native diagram the
   prover could not decide took a first placement, a repair and a 120 s retry, about 300 s. Two of
   them took the whole 560 s set, and the pool-fill placed nothing.

## II. The first plan was refuted by its own first measurement

The approved plan was to take the slicer's layouts, pin each one's arrangement onto the ruled
model, and let the solver only size it. The pinning is sound: a placement the free model found,
re-pinned to its own slicing, is feasible. The layouts are not usable.

| diagram | distinct layouts tried | feasible on the basic facts alone |
|---|---|---|
| `centre-passage-double-pile` | 1,023 | 0 |
| `centre-passage-single-pile` | 579 | 0 |
| `foursquare-quadrant` | 569 | 0 |

"The basic facts" are sizes, doors and contested corners, with the type's facts and the bands
released and the other storey left free. Each pinned solve took about 0.02 s. A random slicing puts
a small room in a full-depth strip and a corner room inside the block, so it fails before any type
fact is asked. That stage was not built.

Two more approaches were measured and refused:

- **Solver settings.** The 2D energetic, timetabling and area propagators, a higher linearisation
  level, no hint, interleaved search and eight workers each left the foursquare UNKNOWN at 60 s.
- **A relaxed placement first, then one storey fixed.** On one worker the relaxed placement was
  itself UNKNOWN at 40 s on the bare model.

## III. The line grid

The tiling is restated on the lines the walls stand on. The rooms of one (level, element) have at
most n + 1 distinct coordinates an axis. So there are K ordered lines an axis, every room edge is
one of them, and every cell of that grid is covered by at most one room, and by exactly one where
that group's tiling literal holds.

It is redundant. At K = n + 1, or one line a foot where the box is narrower, every placement the
ruled model admits is still admitted. A FEASIBLE answer is the ruled model's own, and an INFEASIBLE
one is a proof about the ruled model. `TILING`, `COVERAGE`, the bands and `typefacts` are untouched.
It is added after `_build`, on the solve's copy, as `_harden` is, so the model hashes in
`tests/test_cp_elements.py` do not move.

**It rides on the portfolio's hard steps and nowhere else.** That was measured:

- Added at every solve site, the shipped `tidewater-georgian-careful.json` at 40 s came back refused
  for bearing, hearth, stacks and tiling with all 24 room bands released. Its restores were each
  UNKNOWN at their 4 s cap. The bare model on the same run was refused for tiling alone.
- Added to an undecided round's hard retry, the shipped `spec-builder-colonial.json` came back
  unsolved at 40 s, where the bare retry places it.

So the ladder's scouts and retries, the reinstatement pass, the polish and the conflict extraction
solve the model they were tuned on. `TDL_CP_LINE_GRID=0` solves the bare model everywhere.

### What it decides

Every diagram the composer considers for the stock brief, every type fact hard, the authored walls
and the axis released, four workers, 25 s a step, at the derived depth and 2 and 4 ft deeper:

| diagram | nativity | result |
|---|---|---|
| `living-hall-picturesque` | borrowed | +0 OPTIMAL 2.7 s |
| `side-hall-townhouse` | lineage | +0 OPTIMAL 10.3 s |
| `centre-passage-double-pile` | native | INFEASIBLE 0.3, 0.3, 0.4 s |
| `octagon-radial` | borrowed | INFEASIBLE 1.1, 1.4, 1.5 s |
| `connected-farmstead` | borrowed | INFEASIBLE 1.8, 1.8, 3.6 s |
| `cape-central-chimney` | borrowed | INFEASIBLE 7.4, 11.2, 2.5 s |
| `tower-villa` | borrowed | INFEASIBLE 6.5, 14.9, 15.4 s |
| `gable-front-and-wing` | borrowed | INFEASIBLE 24.4, 6.2, 10.6 s |
| `hall-and-parlor` | borrowed | +0 INFEASIBLE 17.7 s; +2, +4 UNKNOWN |
| `five-part-palladian` | native | UNKNOWN at all three |
| `centre-passage-single-pile` | native | UNKNOWN at all three |
| `foursquare-quadrant` | borrowed | UNKNOWN at all three |
| `courtyard-and-portal` | borrowed | UNKNOWN at all three |
| `ranch-tripartite` | borrowed | UNKNOWN at all three |

Two hold every fact, six are proven impossible as composed, six are undecided. The foursquare is
proven impossible at +2 ft in 80 s on four workers, outside this table's 25 s.

On one worker with the grid, the hard step holds every fact of the living hall in 3.9 s and of the
side hall in 19.1 s. On one core with four workers the same two took 13.3 and 21.0 s, so a
one-core box is better served by one worker.

## IV. What was built

**`build/geometry_cp.py`**

- `LINE_GRID`, `line_grid_on`, `_level_elements`, `_line_grid`: the grid, on the hard steps.
- `hard_steps = workers > 1 or line_grid_on()`: the portfolio's hard steps run on one worker too.
  The restores, the polish and the undecided round's hard retry keep WP-17.5's own gate.
- `PORTFOLIO_SHARE_DERIVED_DEPTH = 0.4`: the walls-released step at the derived depth had a quarter
  of what was left, about 11 s of a 60 s budget, which cut the side hall's 10 to 19 s solve short.
- `all_facts_account`, `all_facts_note`, `solver.all_facts`: what the hard steps said of every type
  fact held together. `held`, `proven-impossible` or `undecided`. It is `proven-impossible` only
  where the walls-released step came back INFEASIBLE at every depth the prover tries.
- `ladder_window`, `_reinstate_deadline(window_end=)`: the reinstatement pass's ruled share.

**`build/typefacts.py`**

- `all_facts_verdict`, `JOINT_PROOF_LINE`, `refusal.jointly_proven`. A jointly proven refusal's
  class is PROVEN. Each fact's own class is unchanged.

**`build/compose.py`**

- The passes are ordered: a first placement for every asked candidate, then the pool-fill, then the
  repairs and retries on what the set has left. `_revise_one(acts=)` and the `_first` stash.
- A pool diagram proven impossible does not use a slot of `POOL_FILL_PLACEMENTS`.

**Elsewhere**

- `build/geometry.py`: `cp_run` carries `all_facts`.
- `workbench/server/app.py`: `/api/health` reports `prover` (workers, line grid).
- `workbench/app/src/sheet/refusal.js`, `glossary/refusal-proven-together.json`: the joint proof's
  own record.

## V. The rulings

Each was put as a direct question and answered as its own act, on 26 November 2026.

1. The screenshot was the deployed Railway server's.
2. Done means at least two drawable candidates, one of them the native double pile, on every run
   and on one core. **This package does not reach it.** See §VII.
3. The reinstatement pass may take a share carved from the ladder's, total time unchanged. This
   re-rules a clause of R12 (30 October).
4. A refusal whose facts are proven impossible together reads as proven and is not retried.
5. A pool diagram proven impossible does not count against the pool-fill's cap.
6. The double pile's service wing is reported and fixed separately.

One decision was mine and was not put: the composer's passes run in the order first placements,
pool-fill, second acts. No ruling orders the retry against the pool-fill. The repair and the retry
keep their ruled order and their gates. It is one block in `compose.compose` and can be reversed.

## VI. The stock brief, before and after

`compose(family-georgian, 4)`, defaults, one run each. "Not refused" is `placement_standing ==
"placed"`: a card that may be opened and drawn. "Drawable where judged" is `drawability.assess`.

| | wall time | returned | not refused | drawable where judged |
|---|---|---|---|---|
| one worker, before (the deciding steps skipped) | 604 s | 4 | 0 | 0 |
| one worker, after | 550 s | 5 | 2 | 0 |
| four workers, after | 556 s | 6 | 3 | 1 |

One worker, after: the living hall and the courtyard house (added from the pool) are not refused.
The five-part and the single pile are refused and their retries were not begun, with 47 s left. The
double pile is refused, proven, and not retried. The pool-fill placed four and stopped on its cap,
so the side hall, eighth in the pool, was not reached.

Four workers, after: the side-hall townhouse is added from the pool and leads the set, drawable
where judged. The living hall and the courtyard house are not refused. The pool-fill placed five,
one of them (the octagon) proven impossible and not counted against the cap. The three native
diagrams are refused as on one worker, with 40 s left and no retry begun.

An earlier four-worker run of the same code, before the pool-fill read the refusal's own `proven`
flag, returned 5 with 2 not refused and 0 drawable where judged: the octagon is proven by the
ladder's own conflict set and not by the joint verdict, so it used a slot and the cap stopped the
fill one diagram short of the side hall.

On one worker neither house that is not refused reads drawable where judged, and the side hall is
not reached. The living hall's reason is one door: its `landing` declares a door to the ground-floor `stair`, which no placement can seat on one
level, and `drawability.assess` counts an unplaced door. That is the borrowed parti's record and
was not changed.

## VII. What was not done

- **The native double pile is still refused on this brief.** It is now labelled proven, with its
  conflict named. Its main block holds every fact on both storeys in 7.4 s. Its service wing cannot
  tile in any box tried. `oq/the-double-piles-service-wing-cannot-tile-on-its-hyphens-face` carries
  the conflict core and three measured changes, one of which draws the whole house in 18.7 s
  without the garage. Each is a statement about the type and none was applied.
- **Six diagrams are still undecided at 25 s a step**, the native five-part and single pile among
  them. The grid moved them from never answering to sometimes answering. None is claimed fixed.
- **The pool is placed in score order.** On one worker the side hall, which is drawable where
  judged, is not reached. A short deciding pass over the pool before the full placements would
  find it; it was not built, because it changes what "the ranked pool" means.
- **The caps on a single restore are unchanged.** How many facts the reinstatement window wins back
  on an undecided composed house was not measured.
- The slicer-topology stage of the first plan: refuted in §II.
- No change to what refuses a drawing, to `TILING`, `COVERAGE`, the bands, or `rank_key`.

## VIII. Tests

- `tests/test_line_grid.py`, new: the grid is redundant in both directions on two fixtures; the
  bare and the gridded model give the same decided answer over seven release sets, which hold both
  answers; the full-cover half follows the tiling literal and nothing else; `_build` does not move;
  `all_facts_account`'s verdicts; one worker runs the hard step with the grid and not without.
  Seven mutations, each restored and each red.
- `tests/test_joint_proof.py`, new: the verdict off structure, the class, the per-fact classes
  unmoved, the retry and the repair decisions, the pool-fill's cap driven over a real compose.
- `tests/test_compose_passes.py`, new: the order of the composer's own calls to the placed loop.
- Re-cut, because they pinned WP-17.5's one-worker path rather than their subject: two in
  `tests/test_cp_portfolio.py`, the `solved_on_one_worker` fixture in
  `tests/test_type_facts_hard.py`, and a shape pin in `tests/test_solve_cache_workers.py`. Each
  drives the ladder with the grid off, where it still runs.
- `workbench/app/src/refusal.test.mjs`: the joint record.

Verification status is in the commit message of the commit that carries this report.
