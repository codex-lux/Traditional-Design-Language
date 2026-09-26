# oq/the-tiling-fact-cannot-hold-on-a-rounded-or-derived-massing-element — the prover is asked to tile a box it cannot reach and a box it drew around its own rooms

*Status: OPEN · Raised in: WP-14.21, the worked house, attempted (25 September 2026)*

**The finding.** WP-14.21 tried to write a Tidewater plan that places. On every prover placement
whose residue it read strip by strip, the tiling fact came back downgraded:

- five variants of the careful record and its two controls;
- the careful record's own placement.

The residue had two parts in the service wing that no arrangement of rooms can remove. A third part,
in the main block, follows the hearth and is not this question's.
`docs/reports/wp-14.21-the-worked-house-and-the-dining-fire.md` §IV has the figures.

## The hyphen: the rounding is never given back

`geometry_cp._element_boxes` rounds a massing element **inward** to the 1 ft grid, so that anything
proved inside it is really inside. Its comment states the other half of the arrangement: *"`_absorb`
afterwards works in float space against the element's true edges and grows the room back out to
them."*

WP-13.3 then skips `_absorb` on any level where a bearing or stack fact is held. Its reason, in the
comment beside the skip, is *"with the tiling fact held there is no leftover to absorb anyway"*.

That sentence is true of the main block, which `_snap_fpd` makes integral. It is false of any element
the rounding moved. `blocks_for` centres the hyphen and the dependency on the main block's axis, so
their edges land on half-feet whenever the depths differ by an odd number.

`typefacts.tiling` then reads the rounding strips against the element's true edges, at a tolerance
of 0.05 sf, as floor in no room.

**Measured:**

- The hyphen's residue is exactly two 0.5 ft strips, **7.0 sf**, on V3, on D4 and on the careful
  record's own placement.
- Landing both service elements on whole feet by sizing alone (the report's D3, a control and never
  a candidate) takes it to **0.0**.

So the prover can hold the tiling fact in its model and have it read downgraded on the record, on
any house whose hyphen is centred on a half-foot and whose upper floor carries a held bearing or
stack fact.

## The dependency: the fact asks a derived box about itself

A dependency's box is not declared. `geometry.dependency_sizes` derives it from its own rooms' areas
plus a grid allowance (WP-11.13).

The prover's coverage floor for such an element is therefore stated against the rooms' declared
area, and the model's comment says why: *"asking whether those rooms fill it is asking the box about
itself"*. `TILING = 1.0` (WP-13.3) asks exactly that question again, element by element.

**Measured:**

- The dependency's residue is **77–118 sf** on the four placements read, including D3's integer
  box.
- Offered back alone by the reinstatement pass, the dependency's tiling was proven **INFEASIBLE** on
  V3, D3 and D4.
- The search tiles the same element on every variant, by drawing rooms past the prover's size
  tolerance. The breakfast room is 259 sf against 168 declared on V1.

## What must be ruled

1. **Against what is the tiling fact stated on a derived element?** There are two readings:
   - against the rooms' declared area, as the coverage floor already is;
   - the element is derived so that its own rooms can tile it at the prover's tolerances.

   The first makes the fact weaker than on the main block. The second changes `dependency_sizes`,
   and with it every placed multi-element record.
2. **Does the absorb skip belong to the level or to the element?** A single-storey element carries
   no bearing line and no stack, so growing its rooms into their own rounding strips cannot unprove
   anything the skip protects. But `_absorb`'s growth is not confined to the strips, and WP-13.3
   measured it unproving a stack.
3. **Or should `typefacts.tiling` read the integer box the prover was given?** That would make the
   gate and the model agree by making the gate read the instrument, which is the wrong direction for
   a gate.

## What must not happen

- `TILING`, `COVERAGE` and `TILING_TOL_SF` must not be loosened until the residue passes. The 7.0 sf
  is real floor inside a stated mass, and nothing is drawn on it.
- A plan record must not be sized to land its elements on whole feet. That is the report's D3, and it
  is exactly the edit-to-clear-a-refusal the WP-14.21 ruling calls laundering.
