# oq/a-clearance-is-sometimes-a-companions-place-and-sometimes-a-prohibition — one field, two opposite meanings

*Status: OPEN · Raised in: WP-13.6, furniture to its own grammar (16 September 2026)*

**`clearance_in` is on all 278 catalogue items and it means two opposite things, and no field
says which.** `schema/room.schema.json` defines it as *"the gap this item needs beyond its own
footprint"*, and read straight that is a PROHIBITION: nothing else may stand there. But a
third of the sentences that explain a clearance describe the floor a COMPANION takes, and the
companion is another item in the same room's own list:

* `rooms/living-room.json` furniture[coffee table].note — *"16 to 18 in from the sofa"*. The
  sofa's clearance is 30 in. The record puts the coffee table INSIDE it, by name and by figure.
* `rooms/dining-room.json` furniture[dining table, seats 8].note — *"36 in chair pull plus 18 in
  passage"*. The table's 54 in IS the chairs' floor: the chairs the same room lists.
* `rooms/study.json` furniture[desk].note — *"42 in behind, not 36, because the shelving behind
  the chair takes 12 in and a person must be able to rise and turn"*. Here it is a prohibition
  and the sentence says why, twice over.
* `rooms/primary-bedroom.json` furniture[king bed].note — *"30 in each side, not 24"*. Not in
  front at all: a DIRECTION the field does not carry either, which WP-13.6 answered separately
  with `fg-bed-aisle` because two records state the direction in words.

**WP-13.6 executed the field and had to choose a scope, and it chose by measuring.**
`fg-clear-in-front` reserves the strip against later POSITIONED items and against nothing else.
**The measurement is a LADDER of three scopes, all over the sixteen plans on the deterministic
engine, and each rung is named so no figure can be read at the wrong one:**

| scope | placed | refused | drawn items lost against the shipped scope |
|---|---|---|---|
| **A — later POSITIONED items only (shipped)** | **648** | **152** | — |
| B — and the freestanding items and the table's chairs | 569 | 203 | **79 over 39 rooms** |
| C — and the wall pack too (a `front_ft` spec field gated as `aisle_ft` is, so the fixture layouts stay byte-identical by construction) | 560 | 212 | **88 over 44 rooms** |

B loses the living room's coffee table, against that table's own sentence, which is why a
freestanding item is exempt. C loses 32 dining chairs, 7 hall chairs, 4 dining tables, 4 coffee
tables and 4 games tables besides: a chest's 36 in and a sofa's 30 in overlap across any room
under about 7 ft. WP-13.6 first published a 41 it inherited from the pass before and an
"87 over 43" measured with the `front_ft` field alone — which leaks the strips into `placed` and
so silently blocks the freestanding items too, making it neither B nor C. Both are superseded
here: **a figure without its scope is a figure the next reader applies to the wrong one.**

Neither scope is derivable from the records. **The figure is a reading and the scope is ours**,
which is why `fg-clear-in-front` is graded `reading` for the number and says in its own rule
text exactly which items it reaches — and why the wider reading was refused with its cost
published rather than netted off.

## What has to be ruled

1. **Does a clearance carry a direction?** Today it does not, and two rules read one in
   different ways: `fg-clear-in-front` reads IN FRONT (off the face away from the wall) and
   `fg-bed-aisle` reads EACH SIDE, the second only because two bed records say so in words.
   A `clearance_of: front | each-side | around` field would state it once; authoring one means
   reading all 278 notes, and about two hundred of them state no direction at all.
2. **Does a clearance exclude, or does it name a companion's place?** A `clearance_kind:
   prohibition | companion-floor` would let the packer refuse the second wall item and admit
   the coffee table on the record's own authority rather than on a rule's scope. The trap is
   the one this corpus names first: a field with two values is an invitation to author the one
   that makes a checker green, and the sentences that decide it are not always there.
3. **If a companion is named, is it named?** `rooms/living-room.json` says *"from the sofa"* and
   `rooms/dining-room.json` says *"chair pull"* — the companion has a name in the room's own
   list. A `clearance_shared_with: <item>` would make the relation checkable
   (`build/check_rooms.py` could hold it to an item that exists), and would turn WP-13.6's
   freestanding exemption from a scope into a reading.

**Do not close this by tightening the scope until one of the three is authored.** The scope is
the only lever the code has today, and every setting of it is wrong about some item: that is
the question, not a defect in the setting.
