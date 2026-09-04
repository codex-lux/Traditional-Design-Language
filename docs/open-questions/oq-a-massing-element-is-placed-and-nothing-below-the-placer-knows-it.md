# oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it — six layers read the main block as the whole building

*Status: RULED 4 Sep 2026 · Raised in: From the adversarial audit of OQ 40's block machinery (3 Sep 2026)*

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

## Lucas's ruling, 4 September 2026 — all four items

Taken against `docs/reports/tidewater-layout-diagnosis-2026-09-04.md`, whose Part V finds the
container to be the root of twenty-two of its fifty-one findings: the declared Tidewater record is
INFEASIBLE in one rectangle because its `exterior_walls` are the exposures of a five-part house,
and the CP engine's remedy is to delete sixteen of them and keep the box. The four items were put
with a recommendation apiece and all four recommendations were taken.

**1. An element has its own envelope, and the roof is per element too.** Not the union. `structure`
gets four walls per element, `export_ifc` a slab per element, and each element carries a stated
ridge relation to the main block — which `groupings/georgian-service-core.json` already states as a
rule and tests (`wing_ridge_ft / main_ridge_ft at-most 0.85`) and which has never had a reader.
*The consequence to watch:* a per-element roof means the massing's `roof_default` is a fact about
the MAIN element and the dependency's is a choice, and the corpus has nowhere to say the second.
That gap is named here and not filled.

**2. The lot cap is on the BUILT EXTENT, hyphen included.** The hyphen is roofed ground; a building
whose covered area overruns its lot has overrun it. The union bounding box is the wrong measure
only where two elements sit diagonally and the box counts open yard between them; that case does
not arise on an axial five-part scheme and is refused rather than modelled.

**3. The hyphen is a THIRD ELEMENT carrying one room.** Not a joint between two. Every count in the
table above then says "elements" and means it, and the seventh defect recorded in item 3 above —
that nothing makes the house-side room abut the hyphen or the hyphen abut the dependency's anchor —
becomes a placement constraint between adjacent elements rather than an accident of two independent
`slice_rect` calls. It does NOT reopen the 3 Sep ruling that the hyphen is a room: it is a room,
and its element is the thing the room is placed in.

**4. `plan_check`'s drawn layer measures `touches` against the room's OWN element.** And where a
room's exterior wall faces the hyphen gap, the finding says so in its own words rather than
convicting a landlocked room: exterior to the weather, interior to the view, which is a distinction
the corpus has the vocabulary for (`lit_from` is about light, `exterior_walls` about exposure).

**The order the layers are taught, and it is the ruling's operative half.** The entry's own trap —
fixing one layer removes the shield the others hide behind — sets the order: `openings` first
(which makes the dependency's windows real and therefore makes `structure`'s missing envelope a
DRAWN collision rather than a silent absence), then `structure`, then `vertical_score`, then the
lot cap, then `plan_check.drawn`, then `export_ifc`. **Measure after each**, and the measurement is
the six-number baseline `PLAN-OF-ACTION.md` Phase 11 states.

Built by **WP-11.6**. Nothing about the disclosure is removed until the layer it discloses is
taught: `geometry_report.multi_element` names six layers today and must name five, then four, then
none — a falling count, in the record, is how this ruling is checked rather than claimed.
