# oq/three-hard-room-rules-forbid-a-detached-kitchen — the room records assume one rectangle

*Status: RULED 5 Sep 2026 · Raised in: WP-11.6, re-authoring `centre-passage-double-pile` (5 September 2026)*

**Lucas's ruling, 5 September 2026, on both halves.**

**1. YES — an element boundary IS a thing a hard `must_adjoin` may cross, THROUGH A HYPHEN.** A
hard `must_adjoin` may be satisfied through a hyphen room rather than only by a direct shared wall.
That is one field on the rule and it settles all three refusals at once, and it is the reading the
corpus already half-states: `rooms/breezeway.json`'s own exception names *"the Palladian hyphen,
whose two sides are the main block and the dependency"*.

**The ruling is a widening and says so.** Every `must_adjoin` in this corpus was authored before
the model could say a kitchen is in a separate building, so the field must be AUTHORED per rule and
never inferred — a blanket "any must_adjoin may cross any hyphen" would licence a stair hall
reached through a breezeway, which is not what any of these records mean. The three rules this
question names are the three to author it on; the rest of the corpus keeps the reading it has.

**And the trap, which is this ruling's own version of the one the facade ruling walks toward**: a
door satisfied through a hyphen is a door the drawn layer must still be able to PLACE. The
measurement in this entry is that a cross-element door is unplaceable unless the rooms abut, 5 of 5
— so a rule satisfied through a link and a leaf that cannot be drawn is a hard fact passing on
paper. `geometry.flank_slice` is what makes the link's own rooms abut, and it is stated rather than
searched for; where it cannot, the opening must be `unplaced` with its reason and the rule must NOT
report satisfied.

**Options 2 and 3 were refused, with their reasons.** Retyping the butler's pantry AS the hyphen is
cheaper and touches no rule, but it makes a circulation room carry a service room's fixtures and it
settles this one parti rather than the class. Leaving the rules alone and keeping one rectangle
costs the measured 17 → 10 fatal improvement and leaves `five-part-palladian` passing for the wrong
reason — because nothing reads its composition — which is a green tick on a diagram nobody checked.

**2. YES — `compose.score_candidate` must see massing elements, AND IT IS ITS OWN PACKAGE.** It
rates the better house seven points worse (73.5 → 66.5) while the critic's fatal count nearly
halves. Recorded as `oq/the-candidate-score-cannot-see-a-massing-element` and built after the parti
lands, so the parti change is measured on the critic's key rather than on a score known to be blind
to the thing that changed. **The parti is NOT blocked on it**, and the cost of that is stated:
until that package ships the composer will rank a materially better house lower, so a brief that
could take a five-part scheme may come back with a one-rectangle one and no reader will be told
why.

## What is now to be built (WP-11.6 item 3, unblocked and NOT YET BUILT)

The field on the rule; the three `butlers-pantry` / `gallery-corridor` rules authored with it; the
re-authored `centre-passage-double-pile`; `check_partis.py` green on it; and the drawn-layer
guard that a rule satisfied through a link whose door cannot be placed does not report satisfied.
Measured against the 17 → 10 in the table below, which is this entry's own baseline.

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

## What was put, and how it was answered (kept as asked, 5 Sep 2026)

Items 1 and 4 are RULED above. **Items 2 and 3 fall out rather than being answered**: option 2
was the alternative to item 1 and was refused with its reason, and item 3 — what type a service
hyphen is — no longer decides anything, because a `must_adjoin` satisfied through a link does not
care which type the link is. `gallery-corridor`'s own hard rule is one of the three being
authored, so both types remain available and the parti picks by style, which is what WP-11.6's
package text asked for.

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
