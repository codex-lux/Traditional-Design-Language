# oq/the-servicing-layer-does-not-know-about-massing-elements — a wet pair across a 27 ft gap

*Status: OPEN · Raised in: WP-11.16, the record edit (14 September 2026)*

`plan_check`'s **servicing** layer asks whether a wet room has another wet room *adjacent or
below* it — a plumbing-chase question. It reads the DECLARED door graph, and it is
**element-blind**: it does not ask whether the two rooms it calls adjacent stand in the same
massing element.

## The measurement

Driven on `plans/tidewater-georgian-careful.json`, tagged, on `engine="heuristic"`:

| | wet-room findings |
|---|---|
| before the tagging | `powder` |
| tagged, direct `butlers↔kitchen` door **KEPT** | `powder` |
| tagged, that door **DROPPED** | `butlers`, `kitchen`, `powder` |

The middle row is the finding. With the door kept, the butler's pantry sits in the **main block**
and the kitchen in a **detached dependency 27 ft away**, and the servicing layer calls them a wet
pair — a shared chase between two buildings. The two rooms cannot share a stack, and the check
says nothing.

WP-11.16 dropped that door for other reasons (`rooms/butlers-pantry.json`'s OQ 59 clause, and both
engines reporting it permanently unplaced), so the **shipped record is not in the false-pass state
today**. What remains is that the layer would accept the next one.

## Why it is not simply a defect to fix

WP-11.4's rule for choosing a layer is *ask what a check READS*. This one reads the declared
record, and a declared door is authored — so by that rule it belongs where it is. The six layers
WP-11.9 taught, and the seventh WP-11.14 taught, are all layers that read PLACEMENT.
`geometry_report.multi_element`'s `not_element_aware` list is empty, and this layer was never on
it, because the list was of placement readers.

So the question is not "teach it" but **what a declared adjacency means once a record declares
massing elements**:

1. Is a `block` tag a DECLARED fact (available to the declared layers) or a PLACEMENT outcome?
   It is authored, so it is the former — which would make this a real gap in a declared-layer
   check rather than a layer boundary doing its job.
2. `geometry_cp` already refuses to model a door between elements that do not abut, and states it
   in `refinements` — *"a detached dependency is detached"*. Should the DECLARED layers read that
   same rule, or is it the prover's alone?
3. If they should, the same question reaches every other declared-record adjacency check, not just
   the wet stack. That is the reason this is a question and not a patch.
