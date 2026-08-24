# WP-2.3 — A real solver

*24 August 2026. Closes Phase 2.*

The geometry pass placed rooms by generating 250 randomised guillotine slicings and keeping
the best. Every compositional rule WP-2.2 added was scored inside it, and scored heavily — but
a scored preference is not an enforced constraint, and `docs/geometry.md` said so plainly. The
consequence that mattered was not aesthetic. When a brief could not be built, the search
returned its least-bad plan rather than saying *what conflicts*, and telling a builder early
that a brief cannot be built, and why, is the thing a plan-development partner most needs.

`build/solver.py` states the same problem to CP-SAT. It is a new module, not a rewrite of
`build/geometry.py`: the heuristic is kept, run first, and used three ways — as the hint the
solver opens on, as the cross-check that decides which layout is actually better, and as the
fallback when OR-Tools is absent.

## What was built

**`build/solver.py`** — `solve(plan, parti, seed, time_budget_s, mode, heuristic_candidates,
workers)`, returning the same record shape as `geometry.solve` plus a `geometry_report.solver`
block, or `{"error", "conflict"}` when the rooms cannot be housed.

**Two tiers, because there are two different questions.**

1. *Does this brief fit at all?* Only the room minimums are asserted; every placement
   requirement is soft. An infeasibility here means one thing — the rooms asked for do not fit
   at the sizes that keep them the rooms they are named as — and CP-SAT's assumption core names
   which. This is asked as a pure feasibility question, with no objective, because that is what
   it is.
2. *Where do the walls go?* The heuristic proposes a slicing topology; CP-SAT places every cut
   in it to proven optimality. Up to six topologies from different heuristic seeds are tried
   and the best result by `geometry.py`'s own scoring wins.

**A named minimal conflict set.** CP-SAT's core is *sufficient*, not minimal, so it is
minimised by deletion — drop one requirement, re-solve, keep it only if the infeasibility
needs it. A drop that times out is kept and the report says the set is minimal *up to the time
budget*, never claiming a minimality it did not prove. The prose reads:

> a 2-bay, 20 x 25.96 ft single pile house (519 sf a floor) cannot hold the dining-room,
> drawing-room and library at their stated minimums at once, and the lot allows no more bays
> after its side setbacks, so the house cannot be made wider. Drop a room, widen a room's band,
> or change the massing.

No geometry is written for a plan that cannot be built. The machine-readable requirement names
travel beside the sentence, not instead of it.

**`unmet_requirements`** — measured from the finished rectangles rather than from what the
solver stopped insisting on. A demotion says what the solver gave up asking for; this says what
the drawing in your hand actually fails. Both are reported, and the difference between them is
the difference between could-not-evaluate and evaluated-and-failed.

**Shared with the heuristic.** `geometry.py` gained `prepare_rooms()`, `derive_footprint()` and
`write_record()`, extracted verbatim from `solve()`, so both engines derive the footprint by
the same rule and emit the same record. Its numeric behaviour is unchanged — the pinned
relaxation count of 11 in `tests/test_geometry.py` is what proves it.

**Interfaces.** `geometry.py --solver cp|heuristic|both`, `solver.py` as a standalone script,
and `place_plan(..., solver=...)` on the MCP server. The default everywhere is the heuristic,
so nothing changes for a caller that does not ask.

## Results

Measured at the default 60 s budget, one worker, seed 7. Both layouts scored by
`geometry.py`'s own scoring functions, so this is one metric and not two engines grading
themselves.

| case | heuristic (best of 800) | cp-sat | better by | relaxations | unmet requirements | wall time |
|---|---|---|---|---|---|---|
| `tidewater-georgian-careful` | 540.4 | **469.8** | 13.1% | 15 → 7 | 22 → 21 | 51.9 s |
| `spec-builder-colonial` | 509.2 | **433.8** | 14.8% | 10 → 13 | 20 → 18 | 54.1 s |
| brief `bungalow-small` | 502.5 | **383.7** | 23.6% | 9 → 9 | 14 → 12 | 22.3 s |
| brief `family-georgian` | 350.7 | **316.8** | 9.7% | 7 → 8 | 16 → 13 | 53.4 s |

Against the package's acceptance: the outputs are the same shape as the heuristic's; the CP
solution scores better than the best of 800 heuristic candidates on both briefs *and* both
shipped plans; an infeasible brief returns a named conflict set rather than a bad plan; and
every solve is inside 60 s. On the Tidewater plan the transfer-beam count — upper wall lines
landing on nothing below — fell from 16 to 7.

## What was found

**The exact-tiling formulation does not work, and the evidence is unambiguous.** The obvious
model is loose rectangles that may not overlap and whose areas sum to the footprint, which is
exactly a tiling. Stated that way it needs `sum(w_i * h_i) == W * H` over a dozen nonlinear
products, and on the shipped spec Colonial CP-SAT could not decide it **in 240 s with four
workers and a hint that was itself a valid tiling** — the snapped heuristic layout matched the
footprint area to the unit. Not "solved it badly": could not determine whether a solution
existed, while holding one. With the objective attached it did no better, and unhinted it never
found a feasible point at all. The bound stayed roughly 10× from the incumbent throughout, so
the model was never optimising, only repairing its hint.

**Reading the slicing structure fixes it completely.** `geometry.py`'s slicer produces
guillotine layouts by construction, so the slicing tree can be read back off a finished layout
without touching the slicer or changing a number it computes. Given the tree, tiling is free:
a tree of cuts tiles whatever it covers at *any* cut position, so the constraint disappears
rather than being solved. What remains — where each cut goes — is linear in the cut variables,
and CP-SAT proves it optimal in well under a second. The heuristic proposes the topology; the
solver proves the geometry. That is the whole package in one sentence, and it is not the
sentence the plan of action anticipated.

**The heuristic silently builds rooms below their band.** On the spec Colonial it places the
dining room at 91 sf against a 122 sf minimum — 26% short — on every one of the six seeds
tried. It can do this because `level_score` charges a flat 12 points for a room under its band
and a candidate can win while paying it. Nothing downstream reports it, because the plan
*record* still says 12 × 12; only the placement shrinks it. The solver refuses, which is why
its first hint had to be rejected and a minimum-satisfying one hunted for across seeds.

**A plan's `exterior_walls` are aspirations, not rectangle edges.** Asserting every declared
exterior wall as a hard constraint makes the Tidewater plan infeasible outright: `passage`,
`backhall` and `kitchen` each declare walls on *opposite* sides, so each must run the full depth
of the house, while `porch` declares both E and W and so must run the full width across the
front. Those cannot all be true of rectangles in one footprint. The records are not wrong —
a real plan delivers that exposure with an ell, a bay, or a wall that is not the bounding box's
— but read literally they are wishes, and `geometry.py` has always been right to treat them as
a 14-point preference. They stay weights. Room minimums, the entrance front and the spanning
passage are the constraints.

**Growing the footprint had no end, so no brief could ever be infeasible.** The footprint is
derived *from* the rooms it contains, so the rooms always fit by construction and no conflict
could ever be reported. Worse, when the lot caps the bay count, depth grows without limit: the
overstuffed probe came back as a perfectly "feasible" 20 × 75 ft single-pile house, which is
not a single-pile house but a different massing wearing the name. The solver now bounds depth
at the massing's own pile times the same 1.18 slack `geometry.py`'s growth loop already allows.
That bound is what makes "grow the footprint before compromising a room" a statement with an
end — grow it in bays, up to the ceiling the parti and the lot allow, and when that runs out,
say so.

**`make check` was skipping tests and reporting success.** `check_all.py` ran the suite as the
bare `pytest` on PATH while every checker beside it ran under `sys.executable`. In this
environment those are different interpreters with different packages, and all sixteen
OR-Tools-dependent tests skipped — reported as a pass. Fixed to `sys.executable -m pytest`. Any
future dependency would have hit the same trap.

## What was deliberately not done

- **`room-harmonic` proportion checking**, **door placement by rule**, and the **whole-plan
  ceremonial traversal** stay deferred, as `docs/geometry.md` already recorded. Nothing here
  changed their standing.
- **`compose.py` still uses its own footprint estimate** when ranking candidates and does not
  call the solver. Putting a 20–55 s solve inside candidate ranking would make composition cost
  minutes; the solver is for placing a chosen plan.
- **Levels above the first floor** are still not placed, as before.
- **The free-packing model is kept** as the feasibility oracle even though it cannot be used
  for placement. It is the only formulation that can answer "these rooms do not fit *in any
  arrangement*"; the sliced model, given one topology, could only ever say "not in this one".
  Its cost is bounded by a short budget, and when it cannot settle the question the report says
  the question was not settled rather than implying it passed.
- **Optimality is per topology, not global.** CP-SAT proves the best cut positions for the
  topologies it is given; it does not prove those are the best topologies. Six is a sampling,
  not a search, and the report says so rather than claiming an optimum the solver never
  established.

## Open question raised

**OQ 32 — the heuristic's silent under-band placement.** The spec Colonial's dining room is
placed at 91 sf against a 122 sf minimum, and neither `plan_check.py` nor the geometry report
says so, because the plan record still declares 12 × 12 and only the placement shrinks it. The
solver refuses to do it; the heuristic still does it on every run and remains the default
engine. Should `level_score`'s flat 12-point charge become a hard refusal in the heuristic too,
should the geometry report carry an explicit under-band list the way the solver's
`unmet_requirements` does, or should the validator learn to read `room.geometry` — which today
it never does? Appended to `docs/open-questions.md`.
