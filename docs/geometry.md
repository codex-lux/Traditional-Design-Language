# Geometry

Room rectangles placed in a footprint, both levels solved together.

```
python3 build/geometry.py plans/tidewater-georgian-careful.json \
  --parti centre-passage-double-pile --candidates 900 --svg dist/plans/out.svg
```

## Bay-grid slicing, with the relaxations counted

Rooms snap to the structural bay module the parti declares, because traditional houses **are** built on one — joists span it, windows centre on it, the facade composes from it. Placement is recursive guillotine subdivision along bay lines.

Where a room cannot be made to fit on the grid the cut is allowed off it, and **every such relaxation is counted and reported**. A cut off the bay line is a joist run that does not land on a bearing wall and a window bay that will not centre, so it is a compromise rather than a detail.

## The move that turns a treemap into a plan

The first working version produced perfectly valid rectangles in entirely wrong places. The fix was one rule:

**A circulation room with exterior walls on opposite sides spans the plan.** That is what a centre passage *is* — a slab from front door to back door dividing the house in two, with rooms sliced either side. Treating it as one more rectangle to pack produces a treemap; treating it as a slab produces a Georgian plan.

Two related constraints followed: only circulation may span (a porch with three exterior walls wants the south edge, not a slab through the middle), and a room whose *type* is a centre passage is placed near the centre, because that is what it is named for.

## Both levels together, not one after the other

Candidate layouts are generated for each level and scored **in pairs** on vertical alignment — upper wall lines that continue to a wall below, wet rooms that sit over wet rooms, the stair landing over the stair. An upper layout that would score better on its own is rejected when it leaves walls unsupported.

Every misalignment that survives is named in the report: *"11 upper wall lines do not continue to a wall below; each is a transfer beam."* That is a cost, and it should be visible before anyone prices it.

## When it will not fit

Grow the footprint first — add a bay before compromising a room. A room below its furniture minimum is a defect that survives the whole life of the building; a slightly larger house is just a slightly larger house. Only then shrink rooms toward their bands, and only then drop optional rooms.

Footprint depth comes from the **massing's own pile** — single-pile 22 ft, double-pile 36 ft — rather than from an invented aspect ratio. Getting that wrong produces a house of the right area and the wrong shape, which was the first version's most obvious failure.

## The drawing is a render of the data

`build/render_plan.py` emits SVG from the coordinates: rooms, walls, bay lines, windows on exterior walls, door marks where two rooms share an edge, dimensions, a scale bar. Nothing is drawn that is not in the plan record, so the drawing and the data cannot disagree — the same discipline as the order tool.

## What this does not yet do, stated plainly

It produces **valid, dimensioned, drawable plans with every compromise reported**. It does not yet produce plans an architect would sign.

- ~~**Search is shallow.**~~ **Fixed in WP-2.3** — see "The solver" below. `build/geometry.py`'s own search is still a hill-climb and is still the default engine; `build/solver.py` states the same problem to CP-SAT, enforces the room minimums instead of scoring them, and returns a named conflict set when a brief cannot be housed. It beats the best of 800 heuristic candidates by 10–24% on both shipped plans and both briefs.
- **No wall thickness, no structural grid, no roof.** Rooms are clear dimensions. Turning them into a framed building is WP-3.1.
- **Doors are centred on the shared wall and now drawn with a swing arc**, but door position is still not placed *by rule* in the fuller sense PLAN-OF-ACTION.md's WP-2.2 brief describes — never in a window bay, never visible from a lavatory. See "What was deliberately not done" below.
- **`room-harmonic` proportions are not checked.** A style that binds that proportion pack does not yet have its principal rooms scored against it — that is a materially separate integration (reading a resolved proportion pack's ratio into a placement score) and is deferred, not silently skipped without a record.

## Compositional scoring (WP-2.2)

`build/geometry.py`'s `solve()` now reads `entrance_faces` from the plan's own `context` (mapped to this file's four-wall N/S/E/W model — a diagonal entrance such as `SE` is satisfied by either adjacent cardinal) and adds four scoring terms to the candidate search, alongside the pre-existing `level_score`/`exterior_score`/`adjacency_score`:

- **`entrance_score`** — the entry-porch (`function_class: threshold`) and whatever circulation room it opens into must reach the entrance-facing wall. This is the specific defect PLAN-OF-ACTION.md's WP-2.2 brief names — *"the current rendered Tidewater plan puts the portico inside the footprint"* — and it is weighted at the same order of magnitude `compose.py`'s own `SEV_W["fatal"]` uses (100), so no candidate in the 250-candidate search can win with the porch off the entrance wall when any candidate has it right.
- **`principal_and_service_score`** — a soft preference (3.5/2.0/3.0 points, an order of magnitude below `entrance_score`): principal rooms (`function_class` `public`/`living`/`dining`) toward the entrance front, service rooms (`function_class` `service`/`work`) toward the wall opposite it, with a room actually sitting ON the entrance wall penalised harder than one merely not-at-the-rear.
- **`ceremonial_score`** — checks the door-connected hop from a room to a higher-`privacy_rank` room actually goes spatially deeper into the plan (farther from the entrance wall), not just that a door connects them. Scoped to hops where privacy rank actually increases, not an arbitrary-length whole-plan traversal — see "What was deliberately not done."
- **`centre_hall_symmetry_score`** — gated on the same spanning-circulation-room test the bay-grid slicer already uses for a centre passage (`spanning()`): rewards a same-type room roughly mirrored across the spanning room's centreline within `18%` of the footprint's own width, with a small (not punitive) penalty per unmirrored room, since plenty of correct centre-hall plans carry one asymmetric service room.

**Verified against `plans/tidewater-georgian-careful.json`**, PLAN-OF-ACTION.md's own acceptance example (entrance faces S): the entry porch lands on the S wall, `kitchen` and `pantry` land in the rear half, and the relaxation count stays at 11 — unchanged from the pre-WP-2.2 baseline, well inside the "no more than two more" acceptance bar. `tests/test_composition.py`'s `TestSolveIntegration` pins all three.

The acceptance example's third clause — *"the drawing room and dining room flank the passage on the front"* — does **not** hold on this specific plan, and this package did not force it to. `dining`'s own record in `tidewater-georgian-careful.json` declares `"exterior_walls": ["N", "W"]` — the rear — which is real, hand-authored intent (dining paired with the breakfast room and kitchen at the back is a legitimate period Georgian arrangement), not an oversight this solver should paper over. A room's own declared `exterior_walls` is authoritative over every compositional preference in this package by design: `exterior_score`'s existing 14-point-per-missing-wall penalty already dominates `principal_and_service_score`'s much softer 3.5-point front preference, and it should — the room stated what it needs, and a soft compositional nudge does not get to override that. `tests/test_composition.py::TestSolveIntegration::test_dining_room_front_claim_is_a_documented_data_conflict_not_silently_forced` pins the conflict itself as a finding, not a bug: whoever next touches this reference plan (or the acceptance text) has an explicit, evidenced choice to make, rather than a silently-missed clause.

**`composition_parti` is read from the resolved kit** (`C["kits"][style]["slots"]["composition_parti"]`), per the brief's own task list, but as of this package no style's kit actually specifies it (`status: empty` across all 132) — so nothing in the scoring above branches on its value yet. It is read and named in the solve so the moment a future kit-authoring pass gives it real content, this file already has the hook.

**On the reference corpus.** PLAN-OF-ACTION.md's acceptance also asks that "the solver's re-placement of a good plan's topology scores within one severity band of the transcription." This is not independently meaningful in the current architecture: `plan_check.py` validates a plan record's own declared `width_ft`/`length_ft`/`exterior_walls`/`doors` — the fields a transcription or the composer already fixed — and never reads `room.geometry` or `geometry_report` at all. Running `solve()` on a reference-corpus plan cannot change what `plan_check.py` reports, because solving only adds coordinates for rendering; it does not touch, drop, or retype a single room. The clause is trivially true under the current separation between the critic and the geometry pass (nothing solving does can move a plan between severity bands), which is worth stating plainly rather than fabricating a before/after score that has no mechanism to differ.

### What was deliberately not done

- **`room-harmonic` proportion checking.** Reading a resolved proportion pack's ratio into a placement score is a materially separate integration from the scoring terms above and was not attempted this pass.
- **Door placement beyond centring.** Doors are still centred on the shared wall (unchanged) and now drawn with a swing arc, but "never visible from the lavatory" and "never in the bay a window occupies" are not checked — both need the elevation-scale bay/window layout WP-3.2 (the elevation generator) actually produces; attempting them against clear-dimension room rectangles alone would be guessing at a bay grid that does not exist yet at this layer.
- **`ceremonial_score` is scoped to direct, rank-increasing door hops**, not an arbitrary-length path search across the whole plan for "no backtracking anywhere." A full graph traversal is a reasonable next step but a distinctly separate piece of work from the direct porch→hall→principal-room case PLAN-OF-ACTION.md's own acceptance example names.
- **This remains a heuristic hill-climb**, per "what this does not yet do" above — the compositional terms are strongly-weighted preferences a 250-candidate random search converges toward, not hard constraints a solver enforces or proves infeasible. That is WP-2.3, and it is now built: see below.

---

## The solver (WP-2.3)

```
python3 build/solver.py plans/tidewater-georgian-careful.json --time 60 --svg dist/plans/out.svg
python3 build/geometry.py plans/<id>.json --solver cp          # same thing through the old CLI
```

`build/solver.py` states the placement problem to CP-SAT over the same bay grid. The heuristic
above is kept and is still the default engine; the solver runs it first and uses it three ways —
as the hint it opens on, as the cross-check that decides which layout is really better, and as
the fallback when OR-Tools is not installed.

### Two questions, two tiers

**Does this brief fit at all?** Only the room minimums are asserted, every placement
requirement is soft, and no objective is attached, because feasibility is what is being asked.
An infeasibility here means the rooms asked for do not fit at the sizes that keep them the
rooms they are named as — and CP-SAT's assumption core names which ones. The set is then
minimised by deletion, and where a drop cannot be decided in time it is kept and the report
says the set is minimal *up to the time budget*.

**Where do the walls go?** The heuristic proposes a slicing topology; CP-SAT places every cut
in it to proven optimality. Up to six topologies from different seeds are tried and the best by
this file's own scoring wins.

### Why the obvious model does not work

Loose rectangles that may not overlap, with areas summing to the footprint, *is* a tiling — and
it is unusable. It needs `sum(w*h) == W*H` over a dozen nonlinear products, and on the spec
Colonial CP-SAT could not decide it in 240 s with four workers **while holding a hint that was
itself a valid tiling**. Not solved badly: could not tell whether a solution existed, with one
in hand.

Reading the slicing structure removes the problem instead of solving it. This file's slicer
produces guillotine layouts by construction, so the tree can be read back off a finished layout
— `guillotine_tree()` — without touching the slicer or changing a number it computes. A tree of
cuts tiles whatever it covers at *any* cut position, so the tiling constraint disappears, and
what remains — where each cut goes — is linear and solves in well under a second. The heuristic
proposes the topology; the solver proves the geometry.

### What is a constraint and what is a weight

Room minimums, the entrance front, and the spanning passage are **constraints**. Exterior walls,
doors and wet stacks are **weights**, at exactly the weights this file already charged.

That split is a finding, not a preference. Asserting every declared exterior wall makes the
Tidewater plan infeasible outright: `passage`, `backhall` and `kitchen` each declare walls on
opposite sides, so each must run the full depth, while `porch` declares both E and W and so must
run the full width across the front. A plan record's `exterior_walls` means "this room has
exposure on these sides" — which a real plan delivers with an ell or a bay — and read literally
as rectangle edges they are wishes. The 14-point preference was always the right reading.

### Disclosures

- **The footprint's depth is bounded** by the massing's own pile times 1.18. Without that
  bound, a lot-capped footprint grows deeper without limit and the overstuffed brief comes back
  as a "feasible" 20 × 75 ft single-pile house, which is a different massing wearing the name.
  The bound is also what makes an infeasible brief reachable at all: while the footprint is
  derived from the rooms it holds, the rooms always fit and no conflict could ever be reported.
- **Coordinates are quarter-foot integers**, and the footprint depth is written back at the
  quarter foot the solver worked in, so the rooms tile the outline exactly rather than leaving
  an inch of nothing along the back wall.
- **Relaxations are recounted** from the finished layout as distinct off-grid wall lines, where
  this file counts them per cut during generation. The two are close, not equal, by
  construction.
- **The CP objective is never the reported score.** Both layouts are re-scored by this file's
  own scoring functions and the better one is kept, so the comparison is one metric rather than
  two engines grading themselves. The objective uses linear proxies where CP-SAT needs one
  (notably for aspect ratio), which is precisely why it is not trusted as the score.
- **Optimality is per topology.** The solver proves the best cut positions for the topologies
  it is given; it does not prove those are the best topologies. Six is a sampling, not a search.
- **The fallback is always reported** in `geometry_report.solver` — engine, status, and a
  stated reason. A plan placed by a different engine than the caller believes is a lie about
  the drawing.

### Measured

Default 60 s budget, one worker, seed 7, against the best of 800 heuristic candidates:

| case | heuristic | cp-sat | better by |
|---|---|---|---|
| `tidewater-georgian-careful` | 540.4 | **469.8** | 13.1% |
| `spec-builder-colonial` | 509.2 | **433.8** | 14.8% |
| brief `bungalow-small` | 502.5 | **383.7** | 23.6% |
| brief `family-georgian` | 350.7 | **316.8** | 9.7% |

On the Tidewater plan the transfer-beam count fell from 16 to 7.

## Next

`compose.py` still ranks candidates on its own footprint estimate and does not call the solver;
putting a 20–55 s solve inside candidate ranking would make composition cost minutes. Whether
the heuristic should refuse to place a room below its band the way the solver does — it puts the
spec Colonial's dining room at 91 sf against a 122 sf minimum, on every seed — is OQ 32.

