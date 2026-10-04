# oq/an-extends-delta-is-applied-to-a-base-it-was-not-written-against — the cascade chooses a delta's base, and the author chose another

*Status: OPEN · Raised in: WP-14.1, the ink read back (27 September 2026), as question 3 of `oq/an-inherited-ban-decides-what-the-elevation-may-draw`; given its own entry by WP-16.4 (30 September 2026), when that question closed*

**The question.** A kit slot bound `extends` is a DELTA: it adds, removes or re-rates variants on a
base record. The cascade takes that base from the nearest ancestor that binds the slot, and the
delta's author may have written it against a different ancestor. Should `extends` take its base
from the node the delta was written against, rather than the nearest ancestor that binds the slot?
That is OQ 87's question ("`open` does not mean open") on the `extends` side.

**The instance that raised it.** `colonial-revival`'s `door_surround` was an `extends` delta whose
own note read *"The inherited pilasters-and-entablature binding (english-georgian) is the right
assembly."* The cascade took its base from `gothic-revival-british`, the nearest ancestor that
binds the slot. That base makes a pointed-arch, hood-moulded, buttressed porch canonical and
forbids `pilasters-and-entablature`, so the delta's author and the resolved record said opposite
things about one doorcase.

**Why it stayed open when its parent closed.** Lucas answered the parent's questions 1 and 2 on
29 September 2026: decision 4 stands, and each wrong inherited ban is corrected in the style's own
kit, case by case. That instance was corrected exactly that way. WP-16.2 bound colonial-revival's
`door_surround` `specified` in its own record (30 September 2026), so it no longer reads any
base. The mechanism is untouched: every other `extends` delta still takes the nearest binder's
record, whoever its author wrote against.

**Not measured.** How many `extends` deltas name, in their own notes, a base other than the one the
cascade delivers is not counted. A delta's intended base is stated in prose, when it is stated at
all, and a reader that pattern-matched notes for node ids would be the prose meter this corpus
refuses to build blind (`check_grouping_rules.py`'s lesson). A count needs either a field on the
delta naming its base, or a read-through by hand.

**What would have to be ruled.**

1. Whether a delta names its base in a field (for example `extends_from: <node>`), so the
   cascade can apply it to that base and a checker can hold the two to each other.
2. If it does, what the cascade does when the named base is not an ancestor, or does not bind the
   slot.
3. If it does not, whether the nearest-binder rule is kept and every delta whose author meant
   another base is corrected in its own kit, as WP-16.2 corrected colonial-revival's.
