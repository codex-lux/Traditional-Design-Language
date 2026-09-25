# oq/a-shared-flue-cannot-stand-behind-two-centred-breasts — the massing says paired, the record says one

*Status: OPEN · Raised in: WP-13.2, the fire on its flue (15 September 2026)*

**`plans/tidewater-georgian-careful.json` gives the drawing room and the dining room one flue,
`west-stack`. Each hearth states no `position_ft`, so each breast defaults to the centre of its
own wall — 13.5 ft apart on the placed record — and the one 22 in square the plan stands at the
flue's mean is 3.4 ft from either fire. No placement of this record can put one stack behind
both breasts, and WP-13.2's gate row says so on every engine:**

    2 of 3 hearths have no flue behind them: drawing's breast on its W wall stands 0.0 ft from
    the W face, along 5.0–9.9; W stack along 13.3–15.1; dining's breast on its W wall stands
    0.0 ft from the W face, along 18.6–23.3; W stack along 13.3–15.1

The corpus states the answer three times and the record contradicts all three:

- the massing's `hearth` is `gable-end-paired` — two stacks per gable end, one for each pile;
- `tidewater-georgian`'s canonical chimney variant is `paired-and-joined-by-arched-curtain`,
  which `docs/structure.md` records as *"two stacks per gable end joined above the roof by an
  arched brick curtain"* and then says the roof layer *"simplifies to one chimney position per
  gable-end wall"*;
- `faults/window-on-the-chimney-axis.json`'s `correct_practice` reads *"move the stacks apart
  rather than the window"*, and `rooms/drawing-room.json` calls the chimneypiece *"the room's
  compositional centre"* — a fire that is not to be moved off its wall's centre to meet a stack.

So the record's single `west-stack` id is the simplification the roof layer made, written back
into the plan as though it were the house. WP-13.2 disclosed it (`gathered` on the stack and on
each breast row) and did not resolve it, because each resolution changes a different record:

1. **Two shafts per gable end where the massing says paired.** The historical answer and the
   kit's own word. It changes the roof, the elevation (four stacks on the ridge, the arched
   curtain between each pair), the chimney count every fault reads, and `roof.py`'s
   one-position-per-end rule.
2. **Seat shared-flue breasts against the partition** between the two rooms, back to back, so
   one shaft serves both. A real arrangement in narrower houses; on this record it moves the
   drawing room's fire off *"the room's compositional centre"*, which its own record forbids.
3. **Split the record's flue ids** (`west-stack-front`, `west-stack-rear`) and leave the massing
   alone. Cheapest, and it is the record admitting what the massing already said — but it is
   option 1 by another name, because two flues on one gable are two stacks.

**What must not happen:** the gate row must not be loosened to "a stack within N ft of the
breast", and `hearths.py` must not move a breast to meet the stack. WP-13.3 makes "the hearth on
its flue" a hard fact of placement and needs this ruled first: it can pin a hearth room to its
gable wall, but it cannot make one shaft stand behind two fires.

**Measured on the prover (WP-13.3, 16 September 2026).** With the hearth a hard, downgradable
fact of placement, the reference plan's two W-face fires cannot co-hold with the sizes, the
shapes and the doors: INFEASIBLE in 1.8 s with a conflict core naming both hearths, where each
fire alone holds (OPTIMAL in 10.9 to 15.6 s). So the prover now says in a core what WP-13.2's gate
row says in feet, and the plan's hearths are still not edited: option 1, 2 or 3 above is the
ruling this needs, and the hearth row of the gate stays red on the reference plan until it is
taken. Report: `docs/reports/wp-13.3-the-prover-learns-the-type.md`.

## Amendment (WP-14.21, 25 September 2026): option 3 costs nothing, and the refusal is upstream of the flue

WP-14.21 tried to author a Tidewater plan that places. Report:
`docs/reports/wp-14.21-the-worked-house-and-the-dining-fire.md`. It measured two things about this
question.

**Splitting the flue ids needs no code, and it does not move the refusal.** The test was run on the
one variant whose prover placement held all three fires (V3, `engine="cp"`). The record's
`west-stack` was split into `west-stack-front` and `west-stack-rear` in memory; no record was
edited.

| | one west flue | two |
|---|---|---|
| west-gable stacks | one, at 26.25 ft, between the breasts | two, at 19.5 and 33.0 ft, each at its own breast's centre |
| roof chimneys | 2 | 3 |
| refused | bearing, tiling | the same |
| hearth | held | held |

So option 3 already draws what option 1 describes. `plan.hearths` places a stack per flue id and
`roof.py` stands one over each. `typefacts.hearth` does not read the flue id, so the refusal is the
same either way.

**The question upstream of this one is whether the second west fire can stand on the gable at all.**
Under the parti's own arrangement it cannot, with every room inside its own record's bands:

- With its fire on the gable, the dining room must span the west range to reach the passage.
- The butler's pantry must door the dining room, and it then needs a side at least as long as the
  drawing room's sixteen-foot floor, against its own fourteen-foot length ceiling.

The proof is in the report's §III. A solver model agrees, INFEASIBLE with both fires and OPTIMAL
with one.

The prover's INFEASIBLE core naming both hearths (WP-13.3, above) is that conflict, met in a core
before anyone read it as geometry. It is not the flue.

So this question's options only become live once
`oq/a-room-record-names-the-wall-its-fire-stands-on-and-nothing-compares-it` item 4 puts the dining
room's fire on the gable. If that ruling puts it on the interior wall its own record names, this
question dissolves: the west gable then carries one fire.
