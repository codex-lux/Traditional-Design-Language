# oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it — six layers read the main block as the whole building

*Status: HALF CLOSED 6 September 2026 (WP-11.9) — the four rulings are taken and all six layers are taught; the roof, the CP engine and the composer remain · Raised in: From the adversarial audit of OQ 40's block machinery (3 Sep 2026)*

**OPEN — the placer states two massing elements and SIX layers below it read
`footprint.width_ft`/`depth_ft` as the whole building. Each is wrong in its own direction on a
dependency room, and every one was measured rather than supposed.**

OQ 40 was ruled on 3 Sep 2026: a dependency is a second massing element, not a second plan level.
`build/geometry.py::blocks_for` places it, `blocks_record` writes it, and both plan renderers draw
it. The layers underneath were written when a house was one rectangle and none of them was told.

| layer | what it reads | what it does to a dependency room |
|---|---|---|
| `openings` | `_boundary_walls(W, H)` from the main block | a garage at x 84–105 on a 70 ft block reports its east face as a footprint boundary; both renderers and `export_dxf` then draw the window at `x = W`, **fourteen feet from the room** |
| `structure` | `wall_lines(rooms, W, H)` over every placed room | a dependency partition landing on the bay grid becomes a bearing line beyond `W` and manufactures a clear span **across the gap** between the house and the dependency; conversely the dependency gets no exterior envelope walls of its own, so its structure is unmodelled |
| `vertical_score` | `wall_lines(g)` over all ground rects | an upper wall within 0.75 ft of a dependency wall line scores as "continues to a wall below", where **there is no upper floor at all** |
| lot cap | `derive_footprint` caps the MAIN block at `lot_usable_width_ft` | a house reporting `lot_capped: true` was measured **34 ft wider than its whole lot** at the built extent |
| `plan_check.drawn` | `fp_w`/`fp_h` for the four `touches` tests | a dependency room with declared windows is convicted of *"drawn in the middle of the house: it reaches no exterior wall on any side"* — the critic and the renderer wrong in **opposite directions about the same wall** |
| `export_ifc` | slab `W + 2*t_ext` centred on the main block | the dependency's `IfcSpace`s float clear of the slab under them |

**What was done instead of a fix, and why.** `geometry.multi_element_disclosure()` writes
`geometry_report.multi_element` on any placement with more than one element: the count, the six
layer names, and the sentence **COULD NOT EVALUATE** in the corpus's own words. The composer emits
no `block` on any room today — the packages that would have taught it to were reverted the same day
— so the only way to reach this state is a caller-supplied record, and a caller-supplied record is
exactly the reader who has no way to know. A record that reports numbers from six instruments
pointed at one rectangle while describing two is the thing this project exists to stop.

**A seventh is closed rather than disclosed, because it could be.** `geometry_cp.py` builds every
room as `x = NewIntVar(0, Wi)` with `x + w <= Wi`: one rectangle, one non-negative coordinate
space. Handed a plan with a dependency it did not fail — it placed the garage at x = 50 of a 0–70
block while `footprint.blocks` described an element at x = 84–114, and it **flattered the fatal
count**, because rooms crammed into one rectangle are all trivially reachable. `engine="cp"` now
refuses and names the cause; `auto` falls back to the hill-climb with the reason in
`geometry_report.solver`. The consequence is worth stating: on a plan with a dependency, the engine
that PROVES is unavailable and the engine that SEARCHES is what carries the findings.

**What must be ruled before anything is built.** Not whether to teach the six layers about
elements — that is obvious — but the shape of the thing they are taught:

1. **Does an element have its own envelope, or is the envelope the union?** `structure` needs four
   walls per element to model a dependency at all; `export_ifc` needs a slab per element. But the
   roof spans something, and the lot must hold something, and neither is per-element.
2. **What is the lot cap ON?** The main block, the built extent, or the union bounding box
   including the hyphen gap — which is open ground the building does not stand on.
3. **Is a hyphen a third element or the joint between two?** It is written as an element today
   (`role: "hyphen"`), which makes a three-element house of every two-element one, and every count
   in the table above then has to say which it means. **And a seventh measured defect lives inside
   this one**: `blocks_for` centres each element on the main block's axis and then slices each with
   an independent `slice_rect` call, so **nothing makes the house-side room abut the hyphen or the
   hyphen abut the dependency's anchor**. Measured on the one parti whose door graph was correct:
   the hyphen at y 9.36–29.36 against a stair at y 30.0–38.71 (missing by 0.64 ft) and a
   dependency anchor twenty-one feet further on, both its doors `unplaced`, and the hyphen itself
   fatal-unreachable. **The one room whose entire reason for existing is to connect two elements
   connected neither.** It is not fixed and not disclosed, because it is only reachable by hand
   once the composer stopped writing `hyphen`; it belongs to whichever answer this item takes.
4. **What does `plan_check`'s drawn layer measure `touches` against?** A dependency room's own
   element is the obvious answer and it is not obviously right: a room on the dependency's east
   face looks across the hyphen at the house, and calling that an exterior wall is true of the
   weather and false of the view.

**The predictable trap, stated because this session met its twin.** Fixing one layer removes the
shield the others were hiding behind. Teaching `openings` about elements makes the dependency's
windows real, which makes `structure`'s missing envelope walls a drawn collision rather than a
silent absence — the same shape as WP-7.4's fixture packer, where turning the corner produced five
overlapping pairs immediately because the fixtures had previously been wrong *together*. Any
package here has to take the layers in an order it can state, and measure after each.

**Do not close this by narrowing the schema.** `block` on a room and `blocks` on a footprint are
the record OQ 40 ruled for; removing them would make the disclosure unnecessary by making the
feature unreachable, which is a different decision and belongs to OQ 40, not here.


---

## Ruled 5 September 2026, and built the same day (WP-11.9)

All four items of "What must be ruled" were put to Lucas with the measurements above and ruled
in one sitting:

1. **Per-element envelope, union reported beside it.** Each element has its own four walls, its
   own boundary for openings and its own slab; `elements.union_bbox` is written beside them for
   the readers that are not per-element.
2. **The lot cap is on the BUILT EXTENT, elements only, gap excluded.** Open ground between two
   detached elements is not the building. `elements.extent_width_ft` measures the union of the
   elements' x-intervals; a hyphen that fills the gap makes it the total.
3. **A hyphen is an element, and abutment becomes a constraint.** `role: "hyphen"` stays.
4. **`touches` is measured against the room's own element's face.** Exterior is exterior; a face
   across a gap is exterior too and is counted separately as `faces_across_a_gap`.

`build/elements.py` is the one reader, a LEAF on `stacking.py`'s precedent. All six layers are
taught, each measured, and **the whole shipped corpus is byte-identical** — placement, footprint,
openings, fixtures, furniture and findings — because every plan here is one rectangle. Report:
`docs/reports/wp-11.9-the-six-layers-that-read-one-rectangle.md`.

**Item 3's seventh defect could not be reproduced, and that is worth more than a fix would have
been.** This entry records a hyphen missing its neighbour by 0.64 ft with both doors unplaced.
Tried at five hyphen depths on a hand-tagged Tidewater and on a composed `five-part-palladian`
with two dependencies and two hyphens — FIVE elements — the count is zero every time, and
deleting the new ranking term changes no outcome anywhere in the tree. `blocks_for` clamps the
hyphen's depth to the dependency's (`hh = min(H, …)`) and centres all three on one axis, so the
hyphen's y-range lies inside both neighbours' and the slicer tiles each element exactly: a shared
wall exists by construction. The constraint shipped as a **guard against a regression in
`blocks_for`**, said so in its test's own name, and the detector is proved to bite on a
hand-built record.

**What is left, and it is a shorter list than six.** The roof spans the UNION bounding box rather
than being modelled per element — ruling 1 gave it that, and it is a stated approximation on a
multi-element house. The composer still writes no `block` tag. And the CP engine still refuses a
multi-element plan outright, which is now the thing that BLOCKS tagging the shipped record:
`oq/the-proving-engine-cannot-place-a-second-massing-element`.
