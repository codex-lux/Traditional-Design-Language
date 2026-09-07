# oq/the-coverage-floor-is-an-exact-cover-per-element — 0.97 of each box, and the boxes have no slack

*Status: OPEN · Raised in: WP-11.11, the prover learns the massing (7 September 2026)*

**OPEN — `geometry_cp` holds each level's rooms to `COVERAGE = 0.97` of the block, and WP-11.11
made that a floor on EACH massing element rather than on their union. `geometry.dependency_sizes`
sizes a dependency's box from the sum of its own rooms' declared areas, so the box has no slack in
it at all. 0.97 of a box that is already exactly full is an exact cover, and on the hand-tagged
`tidewater-georgian-careful` it is infeasible with every declared requirement dropped.**

## The measurement

Six service rooms as a west dependency, the back hall as its hyphen, `engine="cp"`:

| `COVERAGE` | verdict | minimized core |
|---|---|---|
| **0.97** (shipped) | INFEASIBLE | *"the rooms cannot tile any footprint this parti and lot allow, even with every declared requirement dropped"* |
| 0.90 | INFEASIBLE | *"Dining Room and Butler's Pantry share a door"* |
| 0.75 | INFEASIBLE | the same one door |
| 0.50 | INFEASIBLE | the same one door |

Enlarging the dependency's box does not help and the reason is worth stating: the floor is a
FRACTION of the box, so scaling the box scales the requirement with it. Measured at ×1.10, ×1.25
and ×1.50 — infeasible at all three, with the same all-requirements-dropped core.

So at the shipped setting the coverage floor binds BEFORE any declared fact does, and a reader of
the conflict set is told about the tiling rather than about the door. Below it, the engine says
the architecturally meaningful thing.

## Why it was made per element rather than left on the union

A floor over the union lets a dependency sit half empty while the main block over-fills to make
up the total — which is the "two elements flattened into one" reading the whole of WP-11.11
exists to remove. Per element is right in principle. What is not established is the NUMBER.

## What must be ruled

1. **Is 0.97 the right floor for an element that is not the main block?** It was chosen for one
   rectangle whose depth `derive_footprint` grows until the programme fits. A dependency's box is
   not derived that way: `dependency_sizes` returns the rooms' own area exactly, with a width
   rounded to the bay and a depth that follows from it. The two boxes are not the same kind of
   object and they carry the same constant.
2. **Or should the DEPENDENCY BOX carry the slack instead of the floor carrying it?** Sizing a
   dependency at, say, 1.05 of its rooms' area would leave the floor alone and put the tolerance
   where the main block already has it. That changes `blocks_for`, which the heuristic also reads,
   so it moves a search result as well as a proof — measure both.
3. **Does the answer differ for a HYPHEN?** A hyphen's box is one room by construction, so 0.97 of
   it is nearly the identity, and nothing here has shown it binding. Stated so a later reader does
   not assume all three elements have the same problem.

**Do not lower the floor to make a refusal go away.** The refusal below 0.97 is a real door in the
record (`oq/the-parti-dissolved-its-own-dependencies`), and a coverage number chosen so that a
particular plan passes is the shape of thing this corpus refuses everywhere else.
