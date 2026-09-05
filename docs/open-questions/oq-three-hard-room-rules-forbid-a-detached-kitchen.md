# oq/three-hard-room-rules-forbid-a-detached-kitchen — the room records assume one rectangle

*Status: OPEN · Raised in: WP-11.6, re-authoring `centre-passage-double-pile` (5 September 2026)*

**The corpus refused the same diagram three times, in three different arrangements, and each
refusal was a HARD rule of a room record. A parti cannot state a service dependency while the
room records assume every room is in one rectangle.**

WP-11.6's own package text asks for `centre-passage-double-pile` to be re-authored: *"four
principal rooms and a passage in the main block … and the six service rooms in a dependency
reached through a hyphen room (`breezeway` or `gallery-corridor`, by style)"*. It was authored
three ways and `build/check_partis.py` — which composes each parti against its own first native
style and fails on a fatal — refused all three.

| arrangement | the rule that refused it |
|---|---|
| all six service rooms in the dependency | *"Butler's Pantry does not reach a dining room through a direct door"* — `rooms/butlers-pantry.json`, hard |
| butler's pantry back in the main block, hyphen typed `gallery-corridor`, dooring only to the pantry and the kitchen | *"Hyphen does not reach a stair hall through a direct door"* — `rooms/gallery-corridor.json`, hard, `via: [entrance-hall, centre-passage, vestibule]` |
| the same, hyphen typed `breezeway` | *"Butler's Pantry does not reach a kitchen through a direct door"* — hard |

**The three rules are jointly unsatisfiable once the elements are stated.** The butler's pantry
must directly door BOTH the dining room and the kitchen; a detached kitchen puts an element
boundary between them, and **a door between two elements cannot be placed unless the two rooms
abut** — measured, 5 of 5 unplaced with the same reason, *"the placement leaves these two rooms no
shared wall"*, against a same-element control that placed with 15.82 ft of shared run. Any
boundary between the dining room and the kitchen cuts one of the two hard doors.

**`partis/five-part-palladian.json` appears to do this correctly and only appears to.** Its west
hyphen doors `passage`, `butlers` and `kitchen`, and its own note explains the arrangement at
length. It satisfies every rule because **nothing reads its composition**: no parti carried a
`block` until WP-11.6, so its "dependency" is placed inside one rectangle like everything else.
The rules were never tested against a diagram whose elements are real.

## What the measurement showed the change is worth

It is worth doing. On the `family-georgian` brief, with the service rooms in a dependency reached
through a hyphen and the placer laying the hyphen's house-side room against the shared face:

| | shipped parti, one rectangle | re-authored, elements stated |
|---|---|---|
| **fatal findings** | **17** | **10** |
| serious | 76 | 72 |
| cross-element doors unplaced | — | **0 of 1** |
| composer's candidate score | 73.5 | 66.5 |

The rooms that stop being unreachable are exactly the service block — `backhall`, `butlers`,
`kitchen`, `powder`, `garage`, `garage-mudroom` — plus `stair` and `landing`. **And the composer's
own score moves the other way**, which is its own question: the critic's fatal count halves while
`compose.score_candidate` rates the diagram seven points worse, so the composer would rank a
materially better house lower.

**The centre passage is not available as the hyphen's house-side room, and that was swept rather
than argued.** Copying five-part-palladian's `passage` door asks the CENTRE passage to sit on the
block's flank: over 250, 1,000 and 2,000 candidates on two seeds it abuts the shared face at none
of them, correctly. Stating it as a strip anyway put the passage **5.85 ft outside the main block**
and took the house from 11 fatal findings to 14.

## What must be ruled

1. **Does a hard `must_adjoin` hold across a massing element?** The honest reading of
   `butlers-pantry`'s two rules is that they were written about rooms in one house, before the
   corpus could say a kitchen is in a separate building — which is what a five-part house IS, and
   what `rooms/breezeway.json`'s own exception already names (*"the Palladian hyphen, whose two
   sides are the main block and the dependency"*). If a `must_adjoin` may be satisfied THROUGH a
   hyphen, that is one field on the rule and it settles all three refusals at once.
2. **Or is the butler's pantry the hyphen?** In a real five-part house the link often IS the
   service passage. That is a typing question about one room, not a rule change, and it is
   cheaper — but it makes a circulation room carry a service room's fixtures.
3. **What type is a service hyphen?** `gallery-corridor` hard-requires a stair hall (via the
   passage) and states `must_not_adjoin: kitchen`; `breezeway` carries the Palladian-hyphen
   exception but is open at both ends by its own `critical_dimension` while being modelled as a
   heated solid — which `oq/the-parti-dissolved-its-own-dependencies` already records.
4. **Does the composer's candidate score need to see elements?** It rates the better house worse.

**Do not settle this by deleting a rule to make a checker green.** Each of the three has a stated
reason in its own record and each is right about a house in one rectangle. The question is whether
an element boundary is a thing a `must_adjoin` may cross, and that is a ruling about the model.

## What shipped anyway, and why it is separable

The PLACER's half is built and guarded, because it is a prerequisite for any answer above: a parti
room may carry `block` and `hyphen` (parti schema), `build/compose.py` copies both onto the plan
record, `geometry.hyphen_anchors` reads the door graph for crossings **through a link**, and
`geometry.flank_slice` lays those rooms against the shared face as a stated strip — which is
`courtyard_slice`'s own move and its own reason: *"the search is good at slicing a range and has no
way to know which of its edges matters."* The parti itself is reverted until this is ruled.
