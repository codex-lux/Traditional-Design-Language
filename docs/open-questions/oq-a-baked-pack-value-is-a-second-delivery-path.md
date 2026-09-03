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
a kit file. `build/check_addresses.py::baked_vs_refused` measures the collision: **71 pairs today**,
over **29 nodes** and **seven packs** — `opening-proportion` 13, `gibbs-ionic` 13,
`storey-graduation` 12, `trim-classical` 11, `facade-classical` 11, `sash-light` 7,
`brick-course` 4.

**Split by WHICH refusal the baked value escapes, because that is what makes it more than one
problem:** **51 escape a DECLINE — a refusal a person wrote by hand** — and 20 escape OQ 88's
construction scope. The decline group is the sharpest and was invisible until 28 Aug 2026:
`ranch-style` and `minimal-traditional` each declare `declined_packs: [storey-graduation]`, and
each still resolves baked parameters sourced from it, so
`check_inheritance.py --impact ranch-style storey-graduation` names the declined pack as the
governing pack of a slot.

**This paragraph has now been wrong four times, in the same direction each time, and the reason is
worth more than the number.** It published 18, then 20, then stayed at 20 while the meter moved to
32, then stayed at 32 while three adjudication passes took it to 71 — every correction lagging
either an improvement to the INSTRUMENT or a change somewhere else in the corpus.
`check_counts.py` polices figures derived from the corpus and a ratchet is not one, so nothing here
goes stale loudly. **Quote `check_addresses.py --strict` rather than this sentence if the two ever
disagree** — that instruction was in this paragraph the whole time it was wrong, which is worth
knowing about instructions of that kind.

**And the 71 is a function of the decline count, not a regression.** 114 declines carried 65
parameters, 168 carried 66, 208 carry 71; measured on the DECLINES rather than the parameters it is
20 of 168 and then 21 of 208, roughly one decline in ten and falling. Re-pinning the ratchet as the
backlog is worked is the meter following the work.

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
change and a new reader inside the hottest function in `build/`. The count is ratcheted so it
cannot grow in silence while that is decided.

**The general shape is worth stating separately from the count.** A derived snapshot is a cached
computation with no cache invalidation: it was true of the pack on the day it was written and
nothing re-derives it. `check_addresses` can now see the case where the rule is refused; it
cannot see the case where the rule's VALUE has changed and the snapshot has not.

## THE PREDICTED CASE HAPPENED, 2 Sep 2026, four days after the sentence above was written

WP-9.6 moved `storey-graduation.json`'s `stair_type` expression from `ceil(module / 7.25)` to
`ceil(module / 7.5)` on Lucas's ruling. The baked copy in
`kits/georgian-colonial-american.kit.json` at `/slots/stair_type/parameters/risers_per_storey`
carries **both** the expression and the value the expression produced, and the edit moved the
expression and left the value: the same object then read `"expr": "ceil(module / 7.5)"` and
`"value": 17` on a stated 120 in module, where the expression gives **16**.

**Both instruments were run with the defect in place and neither moved.** `check_kits.py` came
back OK — it holds the `computed_at` CONTEXT keys consistent across a slot family and explicitly
`continue`s on `"value"`. `check_addresses.py --strict` came back at its ratchet of 32 — it
measures a snapshot delivering a value the live rule REFUSES, which is a different question from
a snapshot contradicting its own expression.

**The size of the class, measured across all 159 kits: 143 baked derived parameters carry both an
`expr` and a `computed_at.value`.** Of those, **exactly one** is of a shape a narrow reader can
evaluate (`ceil(module / D)` against a stated `storey_height_in`) — and that one is the one that
broke. **The other 142 are UNJUDGED, not passing.** Their expressions and contexts are shapes no
reader in the tree parses, so the honest count of stale snapshots in this corpus is *unknown*,
not zero.

`tests/test_storeys.py::test_the_baked_kit_copy_agrees_with_its_own_expression` guards the one
rule WP-9.6 moved, and deliberately does not generalise: a checker over all 143 needs an
expression evaluator and a decision about what to do with a snapshot whose context no longer
exists, which is what this question is for. What the instance settles is that the shape is real
and reachable in ordinary work, not merely conceivable.

## MEASURED, 3 Sep 2026 — the count is not unknown any more, and it is 0

**Of the 143 snapshots, 135 can be judged from their own record and every one of them agrees with
its own expression. The other 8 cannot be judged, and that is a different sentence from passing.**
`build/check_kits.py::check_baked_snapshots` re-derives each snapshot's expression **at the context
the snapshot itself records** and compares it to the stored value.

**The evaluator this question asked for already existed, in two places, and neither was wired to a
verdict.** `proportion_engine.evaluate_expr` is a general safe evaluator that parses every one of
the shapes in use — there was never a parsing problem. And `resolve_kit.eval_parameters` has been
re-deriving every baked parameter and comparing it against `computed_at.value` all along, setting
`r["stored"]` when the two disagree. `stored` is a display field: nothing reads it, nothing fails
on it. So the sentence "a checker over all 143 needs an expression evaluator" was wrong about what
was missing. What was missing was a check.

**What the record cannot answer, and why those 8 are unjudged.** `computed_at` carries three
bindings — `ceiling_height_in`, `storey_height_in`, `opening_width_in` — and the expressions read
five. Seven snapshots read `span` and one reads `room_width`, neither of which is ever recorded.
All eight reconcile at a span of 540, which is `check_kits.REF_CTX`'s value and evidently what they
were baked at — **but that is a reconstruction of the context, not a record of it**, and a check
may not convict or acquit on a number nobody wrote down. All eight are on
`georgian-colonial-american`, where the `facade-classical` and `trim-classical` rules were baked.

**The remedy is one field, not a schema argument.** Recording the binding in `computed_at` closes
the gap: the reader maps `<name>_in` to the binding `<name>` for any key rather than for a list of
three, so writing `span_in: 540.0` on those seven makes them judgeable with no code change.
`tests/test_baked_snapshots.py::test_recording_the_binding_closes_the_gap_without_touching_the_checker`
proves it both ways — the snapshot becomes judged, and a wrong value then fails. **The open half of
this question is therefore now narrow: should `computed_at` be required to record every binding its
expression reads?** That is a kit-schema change and a regeneration of eight records, and it would
take `baked_unjudged` to 0 honestly rather than by looking away.

**The guard's own ratchets cannot guard it, which is worth knowing before anyone tightens them.**
Deleting the gap detection sends the 8 to be judged against `DEFAULT_BINDINGS`, whose `span` is
240.0 — measured, that **convicts seven of them as stale** and lets the eighth pass in silence.
*Unjudged reported as failed* in seven cases, and reported as passed in one, from a single
deletion. Meanwhile `baked_judged` rises 135 → 143 (above its floor) and `baked_unjudged` falls
8 → 0 (below its ceiling), so neither ratchet notices. `tests/test_baked_snapshots.py` pins the
identity of the eight as a SET for exactly that reason.

**And it catches what it was written for.** Restoring WP-9.6's defect — `ceil(module / 7.5)` beside
a stored `17` — makes `check_kits` fail with the value, the expression and the recomputation named;
`check_addresses.py --strict` stays green with the defect in place, confirming this entry's account
that the two measure different things.

**Still open, and unchanged by this:** the ORIGINAL subject of this question — a scope, a decline or
a `forbidden` binding refusing a live rule while the ancestor's snapshot of it still delivers. That
is `check_addresses.py::baked_vs_refused`, ratcheted at 71, and no amount of re-deriving a snapshot
against its own expression touches it. A snapshot can be perfectly faithful to its expression and
still be a delivery nobody authorised. **The two halves are now measured separately and neither
should be quoted for the other.**
