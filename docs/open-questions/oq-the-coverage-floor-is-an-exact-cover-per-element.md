# oq/the-coverage-floor-is-an-exact-cover-per-element — 0.97 of each box, and the boxes have no slack

*Status: CLOSED — answered by measurement in WP-11.13, and not by choosing a number (7 September 2026) · Raised in: WP-11.11, the prover learns the massing (7 September 2026)*

**CLOSED, AND THE READING BELOW IS KEPT AS WRITTEN BECAUSE THE ARGUMENT IS WHY — it is
right about the symptom and aimed one layer above the cause; the closing section at the
foot of this file is the answer.** `geometry_cp` holds each level's rooms to `COVERAGE = 0.97` of the block, and WP-11.11
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


---

## Closed by WP-11.13 (7 September 2026), and the question was aimed one layer too high

**The floor was never the binding thing, and its number was the wrong variable.** Two defects
sat underneath it and both are fixed:

**1. The floor and containment read two different boxes.** `_build`'s coverage loop computed the
element's box with `int(round(...))` while every room's containment was bounded by
`_element_boxes`, which `ceil`s the low edge and `floor`s the high one. One quantity, two
roundings — so the model demanded 97% of the LARGER be packed inside the SMALLER. On the
hand-tagged Tidewater's hyphen that is **108.6 sf into a box holding 105**: infeasible by
construction, before a single declared fact was read, which is exactly why the conflict core
talked about tiling. The rule now lives in `elements.integer_box`, the leaf both the model and
`geometry.multi_element_disclosure` load, so a second transcription is not available.

**2. The box was sized to exactly its rooms' area and then rounded inward.**
`dependency_sizes` set `H = need / W`, and the grid then takes up to two quanta off each axis —
`blocks_for` centres a dependency on the main block's axis, so its origin is a half-foot and
BOTH roundings bite. Measured, needed coverage against a floor of 0.97:

| element | integer box | its rooms | coverage needed |
|---|---|---|---|
| dependency | 690 sf | 701 sf | **1.016** |
| hyphen | 105 sf | 112 sf | **1.067** |

The rooms could not fit *at all*, at any floor. `dependency_sizes` carries
`grid_allowance_ft()` now — two quanta per axis, one per inward-rounded edge, derived by
solving `(W − 2g)(H − 2g) ≥ need` and not chosen.

### The three things this question asked, answered

1. **Is 0.97 right for a non-main element?** The wrong question. Below the two fixes the floor
   is unreachable whatever its value; above them it is satisfied with room to spare (0.86 and
   0.94). `COVERAGE` is **not changed**.
2. **Should the box carry the slack instead?** Yes — and the reason is the GRID, not a
   tolerance. The question's own note predicted that scaling the box cannot help, because the
   floor is a fraction of it; re-measured here at ×1.10, ×1.25, ×1.50, ×1.75 and ×2.00, all
   still infeasible. What works is sizing the box so its *rounded* form still holds the rooms.
   And the floor for such an element is now stated against **the rooms' own declared area**
   rather than against the box: a box derived FROM its rooms cannot also be the yardstick for
   whether the rooms fill it, and the quantised answer cannot be made to land — the floor needs
   the box within 3% of the rooms' area and one foot of a 30 ft dependency is 5%. The main
   block, whose box `derive_footprint` grows independently, keeps the box floor.
3. **Does it differ for a hyphen?** It is the WORST of the three (1.067), and for a different
   reason: a hyphen's box is its own room's declared rectangle exactly, with no `need/W`
   arithmetic in it at all. It takes the same allowance in DEPTH only — its width is the gap
   between two masses, a real dimension of the house, and its origin is integral by
   construction.

### What it bought

The hand-tagged `tidewater-georgian-careful` — its service programme in a west dependency
joined by the back hall as a hyphen — is **proved OPTIMAL in 12.3 s with zero pins downgraded**,
where before every tagging returned INFEASIBLE with an all-requirements-dropped core. The
conflict set became diagnostic rather than blaming the tiling; see
`docs/reports/wp-11.13-the-box-that-could-not-hold-its-own-rooms.md` for the three-rung ladder.

**The shipped record is still not tagged**, and that is now a record question rather than an
engine one: `oq/the-parti-dissolved-its-own-dependencies`.
