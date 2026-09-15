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
