# oq/a-baked-pack-value-is-a-second-delivery-path — a scope on a rule cannot reach the copy of it in a kit

*Status: OPEN · Raised in: From WP-8.4, the construction scope (28 Aug 2026)*

> **MEASURED AGAINST HUMAN JUDGMENTS, 2 Sep 2026 (WP-8.7).** This entry was raised from scope
> refusals. Adjudicating OQ 51's backlog put 88 declines into the corpus — refusals a person wrote,
> each quoting the node's own record — and **18 of them have a baked survivor**, which took
> `baked_vs_refused` from 32 to 64 (44 of the 64 across 15 nodes: `storey-graduation` 12,
> `facade-classical` 11, `trim-classical` 10, `gibbs-ionic` 8, `brick-course` 3). So the second
> delivery path is not only a scope problem: **roughly one decline in five is half-defeated by it**,
> the live rule refused and an ancestor's authored snapshot still standing. That is the number this
> question was missing, and it is now taken on the records somebody actually ruled on.


**OPEN — 3,176 kit parameters are snapshots of pack rules, and no scope, refusal or precedence
rule reaches any of them.**

A kit parameter marked `kind: derived` with `source: <pack>` is a pack rule's value copied into
a kit file. `build/check_addresses.py::baked_vs_refused` measures the collision: **32 pairs today**, over
**18 nodes** and **three packs** — `opening-proportion`'s `exterior_head_assembly_in` on 13,
`storey-graduation` on 12 across four parameters, and `sash-light`'s `projection_in` on 7
(`chateauesque`, `cotswold-cottage-revival`, `egyptian-revival`, `french-eclectic`,
`french-normandy-revival`, `italian-renaissance-revival`, `italianate-townhouse`,
`jacobethan-revival`, `mid-atlantic-georgian`, `queen-anne-patterned-masonry`,
`renaissance-revival-american`, `ranch-style`, `tudor-revival` among them).

**Split by WHICH refusal the baked value escapes, because that is what makes it three problems
and not one:** 18 escape a kit that binds the slot `forbidden`, 2 escape OQ 88's construction
scope, and **12 escape a DECLINE — a refusal a person wrote by hand.** The last group is the
sharpest and was invisible until 28 Aug 2026: `ranch-style` and `minimal-traditional` each
declare `declined_packs: [storey-graduation]`, and each still resolves baked parameters sourced
from it, so `check_inheritance.py --impact ranch-style storey-graduation` names the declined
pack as the governing pack of a slot.

**This paragraph has now been wrong three times, in the same direction each time, and the reason
is worth more than the number.** It published 18, then 20, then stayed at 20 while the meter
moved to 32 — every correction lagged an improvement to the INSTRUMENT rather than a change in
the corpus. `check_counts.py` polices figures derived from the corpus and a ratchet is not one,
so nothing here goes stale loudly. Quote `check_addresses.py --strict` rather than this
sentence if the two ever disagree.

**The measurement itself had to be fixed to see them, and that is worth recording.** The two
refusals are reported two different ways: WP-8.3's kit refusal MARKS the row
(`refused_by_kit`) and OQ 88's scope DROPS it, recording the drop in `scope_dropped`. Reading
only the marked rows made this count report **0** the moment the scope started biting — the
number went to zero because the evidence had been removed, not because the collision had.

Every one is a masonry node resolving `georgian-colonial-american`'s baked `projection_in`
(`expr: "module * 0.25"`, value 2.25 in, `source: sash-light`) or its baked head assembly,
where OQ 88's scope has just ruled the live rule out. **The rule is refused and its snapshot is
delivered.**

**Why it is not patched.** Deleting the baked parameter on the ancestor removes it from every
descendant, and 30 of the 33 nodes that resolve it are frame nodes the rule is right for. What
is wanted is a scope on the PARAMETER, read where `resolve_slots` assembles it — a kit-schema
change and a new reader inside the hottest function in `build/`. The 32 is ratcheted so it
cannot grow in silence while that is decided.

**The general shape is worth stating separately from the 32.** A derived snapshot is a cached
computation with no cache invalidation: it was true of the pack on the day it was written and
nothing re-derives it. `check_addresses` can now see the case where the rule is refused; it
cannot see the case where the rule's VALUE has changed and the snapshot has not.
