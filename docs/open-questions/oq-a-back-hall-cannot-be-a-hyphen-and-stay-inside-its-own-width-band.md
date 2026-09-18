# oq/a-back-hall-cannot-be-a-hyphen-and-stay-inside-its-own-width-band — two records, one dimension, no overlap

*Status: OPEN · Raised in: WP-13.5, the container (16 September 2026)*

**`plans/tidewater-georgian-careful.json` now carries `hyphen: true` on its back hall, and
`geometry.flank_sizes` reads a hyphen room's own `width_ft` as the gap between the two masses —
so the link this house is placed with is 7.0 ft long. `groupings/dependency-and-hyphen.json`
states `hyphen_length_ft between 12 and 20`, with the reason in its own prose: *"Shorter and the
two volumes collide; longer and the connection stops being used."* `rooms/back-hall.json` bands
`width_ft` at `[3.5, 7]`, with its own reason — 42 in is the corridor that carries loads. The two
bands do not overlap at any value, so a back hall used as a hyphen breaks one record or the
other, whatever number it is given.**

Measured on the placed record (`engine="heuristic"`, deterministic): the three elements come out
as a 45.0 × 37.24 ft main block, a **7.0 × 18.0 ft hyphen** and a 27.0 × 26.68 ft west dependency.

## Nothing convicts it today, and that is the second half of the question

The rule is never evaluated, because `plan_check`'s grouping layer reads the plan's own
`groupings` list and this plan names `centre-passage-core`, `georgian-service-core`,
`entry-sequence` and `public-enfilade` — not `dependency-and-hyphen`. A house that demonstrably
has a hyphen, with the rule that governs one sitting unread, is a check that cannot fire reading
exactly like a check that passed.

**And naming the grouping is not the fix, because it makes the sheet carry two numbers for one
dimension.** `build/roof.py::wing_step_down` is gated on that same list, and the figure it
publishes is `round(sum(hyphen_band) / 2.0, 2)` — the band's MIDPOINT, **16.0 ft** — computed
from the grouping rather than measured off the placement. So the moment the plan names the
grouping, the roof record states a 16 ft link and `footprint.blocks` states a 7 ft one, in the
same file, for the same house. WP-13.5 declined to name it for exactly that reason and recorded
the measurement instead.

## The three ways out, and what each costs

1. **Change the hyphen room's type to `gallery-corridor`,** whose own `width_ft` band is
   `[4, 22]` and which therefore admits 12–20. `schema/plan.schema.json` already says this is
   how the type is chosen — *"`gallery-corridor` where the link is enclosed"* — and
   `partis/five-part-palladian.json` uses `gallery-corridor` for both of its hyphens. The cost is
   that the back hall is a room with its own adjacency rules (`must_adjoin kitchen`, hard, no
   `via`) and the plan's own name for it is "Back Hall (Hyphen)"; swapping the type is authoring
   a different room, which WP-13.5's brief forbids.
2. **Widen the link to 12 ft.** That breaks `rooms/back-hall.json`'s own ceiling of 7 and invents
   a dimension no record states.
3. **Rule that `hyphen_length_ft` is a property of the GAP and not of the room in it.** The gap
   is a dimension of the house; the room's `width_ft` is a dimension of the room. `flank_sizes`
   reads one as the other, deliberately and with a comment saying why — *"this is the whole
   reason the hyphen is a ROOM"* — and it is the only reason that rule has ever been evaluable on
   any plan. If they are two quantities, the record needs a field for the second.

This is `oq/a-grouping-rule-and-a-room-record-can-disagree`'s family, and its standing rule
applies: **do not reconcile it by editing whichever number makes a checker green.** Both bands
carry a stated reason and neither is the obvious one to move.
