# oq/the-terraces-declared-faces-were-written-for-a-house-its-room-has-left — a terrace on the east of a west wing

*Status: OPEN · Raised in: WP-11.16, the record edit (14 September 2026)*

`plans/tidewater-georgian-careful.json`'s terrace declares `exterior_walls: ["E", "N", "S"]`.
WP-11.10's rule admits a face the record declares whose OPPOSITE it does not, so the both-readings
set is `{E}` alone — N and S each have their opposite declared too. That was written when the
breakfast room stood at the east end of the main block. **WP-11.16 tagged the breakfast room into
a west dependency, and its east face now looks back across the gap at the house** — which
`openings.faces_across_a_gap` calls *"exterior to the weather and interior to the view"*. The
intersection with the faces the placement put outside (`S`, `W`) is empty, so the terrace is
UNJUDGED and named: `no-face-both-readings-admit`.

## The measurement

| | heuristic | cp |
|---|---|---|
| before the tagging | **placed**, E face, 14 × 22 ft | **refused**, `no-face-both-readings-admit` |
| after the tagging | refused, same code | refused, same code |

**The prover had already refused it.** Only the hill-climb placed this terrace, so the shipped
sheet — drawn on `auto`, which takes the proof — never had it. WP-11.10 published *"4 placed, 2
refused"*; that was one engine's figure and this is the first time anyone has read the other's.
The edit did not lose a placement; it made the two engines agree.

## What has to be ruled

Re-authoring `exterior_walls` to `["W", "N", "S"]` (or to `["S"]`) would place it immediately, and
that is **exactly the edit this corpus forbids**: changing a record so a checker goes green. But
the declaration is now describing a house the room has left, so leaving it is not obviously right
either. The question is which:

1. **Is `exterior_walls` on an at-grade appendage a statement about the TERRACE (which sides are
   free) or about the HOUSE (which side it stands on)?** WP-11.10 could not separate the two
   readings and took the line both admit. A terrace whose served room moves between massing
   elements is the first case where the two readings come apart *over time*.
2. **If the record should follow the room, what says which face?** `rooms/terrace.json`'s aspect is
   CLIMATE-CONDITIONAL and its two branches point opposite ways (WP-11.9), so the corpus does not
   settle it. The plan's `context.climate_zone` is `3A`; nothing reads it for this.
3. **Should an appendage whose served room is in a dependency be placed against the DEPENDENCY's
   free faces at all**, or is a terrace off a detached service wing a thing this type does not
   have? The kitchen dependency of a Tidewater plantation house is a working yard, not a terrace.

## What must NOT be done

Do not widen the both-readings rule until the intersection is non-empty. The rule is the one thing
that stopped WP-11.10 guessing a face, and it is doing its job here: it refused, by name, with both
readings printed on the record. A refusal that states its reason is the deliverable.
