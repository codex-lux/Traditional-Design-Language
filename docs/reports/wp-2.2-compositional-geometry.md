# WP-2.2 — Compositional constraints in the geometry solver

Full technical detail lives in `docs/geometry.md`'s "Compositional scoring (WP-2.2)" section, which this report points at rather than duplicates. This is the "what was found" record the hand-off brief asks for.

## What was built

Four new scoring terms in `build/geometry.py`'s `solve()`, keyed off `entrance_faces` (read from the plan's own `context`, mapped to the file's four-wall N/S/E/W model): `entrance_score` (fatal-weighted — the entry-porch and its hall must reach the entrance wall), `principal_and_service_score` (soft — principal rooms toward the front, service toward the rear), `ceremonial_score` (a door-connected hop to higher privacy rank must go spatially deeper into the plan), and `centre_hall_symmetry_score` (mirror-tolerance scoring gated on the existing `spanning()` centre-passage test). `composition_parti` is read from the resolved kit, per the task list, though nothing branches on it yet (see below). `build/render_plan.py` gained door swing arcs. 22 new tests in `tests/test_composition.py`, mostly unit-level against hand-built room rectangles rather than only through the full stochastic `solve()` — see "What was found" for why that mattered.

## What was found

**The acceptance example's own reference plan already satisfied two of its three clauses before any code changed.** Running `geometry.solve()` on `plans/tidewater-georgian-careful.json` *before* this package's scoring additions showed the entry porch already on the S (entrance) wall and service rooms already toward the rear — both driven entirely by the pre-existing `exterior_score` mechanism honouring each room's own hand-declared `exterior_walls`, with no compositional scoring involved at all. The "portico inside the footprint" defect PLAN-OF-ACTION.md's brief describes did not reproduce on this plan with this solver as it stands. `entrance_score` was still built and weighted at fatal scale, both because the brief asks for the term explicitly and because a plan or parti with a less carefully hand-declared porch (most real composer output, where exterior_walls comes from a parti template rather than careful individual authorship) is exactly the case it protects — but it is worth recording plainly that the specific bug named in the brief was not caught in the act on the named example.

**The third acceptance clause — dining flanking the passage on the front — does not hold, and cannot be made to hold without either overriding a room's own declared data or editing that data.** `dining`'s record in `tidewater-georgian-careful.json` explicitly states `"exterior_walls": ["N", "W"]`. This is not an omission the new scoring could fill in; it is a contradiction between what the brief's illustrative text expects and what this specific hand-authored "careful" reference plan actually declares. Raising `principal_and_service_score`'s weight to try to force the outcome would mean a soft compositional preference overriding a room's own explicit stated requirement — which is backwards, and would have been a worse regression than leaving the acceptance clause unmet. This is recorded as a genuine, evidenced finding (`tests/test_composition.py`'s `test_dining_room_front_claim_is_a_documented_data_conflict_not_silently_forced` pins it) for whoever next has standing to make the call: edit `dining`'s `exterior_walls` on this reference plan, or treat the brief's illustrative example as one valid Georgian arrangement among others and leave the plan as authored. Not decided here, per the session's practice of not making corpus-wide-blast-radius judgment calls unilaterally.

**`plan_check.py` does not read `geometry.py`'s output at all.** The acceptance clause about the reference corpus scoring "within one severity band" between transcription and re-placement has no mechanism to be false under the current architecture — `plan_check.py` validates a plan record's own declared fields, never `room.geometry` or `geometry_report`. Solving cannot move a plan between severity bands because nothing solving does touches, drops, or retypes a room. Recorded in `docs/geometry.md` rather than fabricating a before/after benchmark that cannot actually differ.

**No style's kit specifies `composition_parti` yet** (checked across all 132 resolved kits: `status: empty` everywhere) — the same shape of finding WP-2.4 made about the site-and-settlement slots. The read is wired in for when kit authoring reaches it.

## What was deliberately not done

- `room-harmonic` proportion checking (a separate integration: reading a resolved proportion pack's ratio into a placement score).
- Door placement beyond centring — "never visible from the lavatory," "never in a window bay" — both need a bay/window layout at the elevation scale this layer does not have yet (WP-3.2's territory).
- `ceremonial_score`'s no-backtracking check is scoped to direct, rank-increasing door hops, not an arbitrary-length whole-plan traversal.
- WP-2.3 (a real CP-SAT solver) is untouched; every term above is still a search preference in a 250-candidate hill-climb, not a hard constraint a solver enforces or proves infeasible against.
- The reference-corpus "topology score" benchmark the acceptance criterion names was not fabricated (see "What was found" above) rather than silently omitted.

## New open questions

None raised. The dining-room finding above has a clear owner and a clear pair of options; it is not a judgment call this package needed a ruling to proceed past.
