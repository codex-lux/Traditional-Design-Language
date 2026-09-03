# oq/a-pack-can-be-the-only-writer-a-node-has — flipping a pack can remove the only account of a slot a node can reach

*Status: CLOSED · Raised in: WP-8.10, the first opt-in flip (3 September 2026) · Ruled the same day*

> **RULED 3 SEPTEMBER 2026 (Lucas): no new rule. Stage the flip by size and keep going.**
> Sole-writer status is not a precondition on flipping. The ruling turns on what WP-8.10 built: a
> stranded slot now NAMES the pack withheld and why (`how: "opt-in.withheld"`, on 2,889 of 2,889),
> so a node with no alternative writer is not a casualty of the flip — it is a node whose author
> has an explicit, located question where a silent wrong dimension used to be. Order of flipping is
> ascending stranded count: `trim-classical` 10 (done), **`facade-gable` 32**, `sash-light` 70, and
> the five packs whose `applies_to` arms a live behavioural gate last.

**The two options refused, recorded because what was decided against is part of the decision.**
A *standing precondition* — no flip while any stranded slot has no other writer reaching that node —
was refused on its measured cost: it disqualifies `facade-gable` and `sash-light`, and would have
disqualified `trim-classical` retroactively, so the staged flip halts after one pack and the
remaining 2,889 slots return to adjudicate-first, which the 3 Sep re-ruling had just moved away from
because its tail is geometric. *Adjudicating each pack's stranded nodes before flipping it* was
refused on the same ground at a smaller scale: ~29 readings for `facade-gable` and ~34 for
`sash-light`, each with an adversarial check at the ~1-in-6 overturn rate that held across three
WP-8.7 passes.

**The question as it was asked, kept below because the measurement is the entry's value and stays
true whatever was ruled:** should a pack be refused the flip where the nodes it strands have no
other writer of that slot in their own cascade? OQ 51 was re-ruled on 3 Sep to flip pack inheritance to opt-in,
staged pack by pack. A flip is supposed to stop a delivery nobody vouched for. Sometimes it does
something else: it removes the only rule the corpus can offer that node for that slot, and the
slot goes from wrongly-dimensioned to undimensioned.

## The measurement that raised it, and the correction that sharpened it

`facade-gable` was the planned first flip. It is the corpus's **only** writer of `cornice_return`,
and **29 of its 32 stranded slots are that one slot** — so flipping it leaves 29 nodes with no
cornice-return rule available anywhere. `sash-light` is the same shape: sole writer of
`window_type` and `shutter`, which are 66 of the 70 slots it strands. On that basis
`trim-classical` was flipped first, because `trim_family` has **three** writers corpus-wide
(`trim-classical`, `trim-craftsman`, `trim-prairie`).

**THAT BASIS WAS WRONG, AND THE ERROR IS THE ENTRY'S REAL SUBJECT.** A corpus-level writer count is
not a fact about any node. Measured per node, of the ten nodes the `trim-classical` flip stranded,
**zero have `trim-craftsman` or `trim-prairie` anywhere in their own cascade.** All ten lose the
only account of `trim_family` they can reach — exactly the condition `facade-gable` was set aside
for. The three-writers figure was true and irrelevant.

**The same shape as the mis-statement that started this phase**, one package later: `unendorsed`
(a count of role gaps) stood in for deliveries and was wrong by a factor of thirteen; here a
corpus-wide writer count stood in for per-node reachability and was wrong about every case. A
count at the wrong grain is the recurring error, not a one-off.

## And the meter already answers it, which is why this is a question and not a patch

`--stranding`'s **`stranded`** bucket *is* the per-node sole-writer measure: a slot is stranded
precisely when no other pack in that node's cascade takes it, and **`rehoused`** is the count where
one does. Corpus-wide that is 2,889 against 1,980. So the condition needs no new instrument — the
question is what to *do* about it:

- **A standing precondition** — a pack may not flip while any slot it strands has no other writer
  reaching that node. Refuses `facade-gable` and `sash-light` outright, and would have refused
  `trim-classical` too, which means it refuses **every candidate measured so far** and the flip
  stops after one pack. That is a serious cost for a ruling whose whole point was to stop waiting.
- **A staging preference** — flip in ascending order of stranded slots, which is what happened
  here anyway (10 before 32 before 70) and needs no rule at all.
- **Nothing.** The ruling already accepts stranding, `--stranding` already counts it, and WP-8.10
  made every stranded slot NAME the pack withheld and why. Under that reading a node with no
  alternative writer is simply a node whose author now has an explicit, located question to answer.

**What is not in dispute:** the flip must not be sold as safe on a corpus-level count. Whatever is
ruled, `--stranding <pack>` before the flip and the per-node `stranded` figure are the numbers.

## The trap in the obvious fix

A checker for "is this pack the only writer of the slot" is four lines and would measure the wrong
thing — it is the corpus-level count that has already been wrong once here. The honest test walks
each stranded node's own cascade, which is what `governed()` already does twice per node in the
sweep. Anyone building this should extend `--stranding`, never write a second walk.

## Adjacent

`oq/a-baked-pack-value-is-a-second-delivery-path` — a baked snapshot in an ancestor's kit file is
not a cascade delivery, so a flip cannot stop one, and a node stranded here may still be carrying
the old number. OQ 87 (`open` inherits in full) is the same cascade seen from the kit side. And the
**179 → 111** addresses that survive any flip via an inherited slot-level `packs` ruling are the
mirror image of this question: there the pack keeps governing after delivery stops.
