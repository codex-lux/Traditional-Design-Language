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

## The real solver (WP-2.3)

`geometry.solve()` now dispatches to **CP-SAT** (`build/geometry_cp.py`, OR-Tools) by default, with the randomised slicing kept as the fallback and cross-check the package text asked for. The division of labour, per the 25 Aug rulings:

**HARD — satisfiable or refused, never traded:** no-overlap, containment, near-total coverage; declared doors imply geometrically touching rooms (a shared run at least the pair's programme-scaled door overlap — all four interval bounds, since two end-gap inequalities alone admit a sliver narrower than the door); a threshold room with an exterior door is the entry and must reach the entrance front; each room at roughly its program size; each room's declared exterior walls. The absorb pass that tiles the ≤3% coverage void is capped at each room's own size band — residual void stays honest empty floor rather than a closet drawn at 3x its proof.

**Wall pins carry a stated refinement**, because `exterior_walls` speaks *exposure in the fully-massed house* — porches protrude, wings hold their own corners — which one flat rectangle cannot always hold (10 of 12 partis double-claim a corner on some level):

- a **protruding** room (3+ walls, or a non-circulation opposite pair) and a room in a **contested corner** harden to "reach at least one declared wall", the rest scored at the heuristic's own 14 points;
- any other wall pin stays fully hard **unless the solver proves a set of pins cannot co-hold** — exactly those pins downgrade the same way, and every downgrade is stated in `geometry_report.solver.refinements`. Doors, program sizes, the entrance and capacity **never** downgrade: they are what infeasibility is for. Because a solver core is *sufficient, not minimal*, a **reinstatement pass** then restores each downgraded pin alone at the footprint actually drawn: a pin that holds returns to being a hard fact, a pin that provably cannot keeps its downgrade with an individual proof, and a pin the budget could not re-prove says "carried, not proven" in its refinement note — never "(proven)".

**SOFT — the WP-2.2 compositional terms**, now weighted objectives rather than search preferences: bay snapping (relaxations stay counted, never forbidden), zoning, ceremonial depth, wet-over-wet stacking, symmetry-adjacent nudges, plus the level-score terms (area error, aspect sanity) mirrored term for term.

**On infeasibility** the caller gets both halves of the ruling: a **plain-language minimal conflict set** (CP-SAT's assumption cores, iterated to a fixpoint then greedily minimized within a budget — a set that ran out of minimization budget says so) *and* the heuristic's least-bad drawing, labelled `INFEASIBLE AS DECLARED` on the sheet itself. The footprint grows a bay before any requirement is blamed. A non-planar door graph — five rooms all pairwise doored — is the canonical true refusal: no arrangement of touching rectangles can realize K5, and the conflict set names the door pairs.

Solving is two-phase: a hard-only pass finds or refutes a placement fast, then the weighted objective polishes it, hinted both by the full heuristic search (soft-optimized, hard-repairable) and by the hard-only placement; every hard-valid result is scored with the heuristic's own scorers and the best is kept, the status saying which. Determinism: one worker, fixed seed — the same record yields the same drawing (exact reproducibility holds when the solve reaches OPTIMAL; a wall-clock-limited polish can land differently under different machine load, and the status says when that is the case).

**The workbench runs the heuristic per edit gesture, deliberately** — a proof takes seconds and the bench re-scores on a 400 ms debounce — and carries a *prove placement (CP-SAT)* control for the explicit act, which surfaces the conflict panel. The CLI, MCP `tdl_place_plan` and everything non-interactive default to the real solver.

## What this does not yet do, stated plainly

It produces **valid, dimensioned, drawable plans with every compromise reported**. It does not yet produce plans an architect would sign.
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
- ~~**This remains a heuristic hill-climb.**~~ No longer — WP-2.3 built the CP-SAT engine (see "The real solver" above); the slicing search remains as the fallback and cross-check, and as the interactive engine the workbench re-scores with per edit gesture.

## Next

WP-2.3 landed (see "The real solver" above and `docs/reports/wp-2.3-the-real-solver.md`). What the solver still does not model — wings and ells as real geometry (OQ 40), door position by rule, `room-harmonic` proportions — is stated in that report's "deliberately not done".
