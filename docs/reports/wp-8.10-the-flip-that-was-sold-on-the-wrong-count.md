# WP-8.10 — the first flip, the loudness it needed, and a count at the wrong grain again

*3 September 2026. OQ 51's first pack lands: `trim-classical` declares `delivery: opt-in`.*

## What was done

1. **Loud stranding**, which the ruling required and WP-8.9 did not build.
2. **The first flip**: six nodes opt in, `trim-classical` flips, **10 slots over 10 nodes** lose
   their dimensioning — the number measured beforehand, to the slot.
3. **Every count re-pinned**, and one of them fell for a reason that must not be read as progress.

## The finding: the meter's gate was not the mechanism's gate

`--stranding` drops a pack where it arrives by descent and the pack's `applies_to` does not vouch
for the node. `resolve_packs` drops it where it arrives by descent and the node's `inherits_packs`
does not name it. **Different predicates, so the published number was not the number a flip lands.**

| | slots | nodes |
|---|---|---|
| the meter's figure for `trim-classical` | 10 | 10 |
| **a flip with no opt-ins written** | **15** | **15** |

The five extra are all `trim_family`, all on nodes the pack's own `applies_to` vouches for —
`charleston-georgian`, `charleston-single-house`, `mid-atlantic-georgian`, `new-england-georgian`
and **`tidewater-georgian`, a shipped reference plan.** Authoring the six opt-ins is what kept the
landed cost at 10. On `facade-gable` the same gap is 32 → 33; it is a property of the pack, so
**measure it per pack and never assume it is small.**

## THE CORRECTION: I sold the flip on a corpus-level count, and it did not describe a single node

`facade-gable` was the planned first pack and was set aside because it is the corpus's only writer
of `cornice_return`. `trim-classical` was offered in its place on the ground that `trim_family` has
**three** writers corpus-wide, so "no node loses the corpus's only account of anything."

**Measured per node, zero of the ten stranded nodes have `trim-craftsman` or `trim-prairie`
anywhere in their cascade.** All ten lose the only account of `trim_family` they can reach. The
three-writers figure was true and irrelevant, and the distinction I drew between the two packs did
not exist in the form I stated it. What actually separates them is size: 10 against 32 against 70.

**This is the same error as the one that opened the phase, one package later.** WP-8.9's headline
was that OQ 51's ruling had been taken on `unendorsed` — a count of role gaps — when the thing a
gate stops is deliveries, wrong by a factor of thirteen. Here a corpus-wide writer count stood in
for per-node reachability. A count at the wrong grain is the recurring defect in this work, not an
incident. The ruling itself is unaffected: `trim-classical` is still the smallest first flip, and
under the corrected reading it is the *only* discriminator. `oq/a-pack-can-be-the-only-writer-a-node-has`
carries the question.

**And the meter already answered it.** `stranded` *is* the per-node sole-writer measure — a slot
is stranded exactly when no other pack in that node's cascade takes it, and `rehoused` is where one
does. The number was on the screen the whole time under a different name.

## Loud stranding, built on WP-8.3's precedent in WP-8.3's words

Before this, a gated pack was dropped, `eval_packs` built no row, and the address returned a bare
absence — indistinguishable from a slot no pack ever wanted. THE REFUSED RULE IS MARKED, NOT
DELETED, so:

- `resolve_kit.withheld_for()` — the mirror of `refusals_for`, out of band for the reason that
  function's own docstring gives. It returns a **mapping** where `refusals_for` returns a list,
  because these records are fed straight to `eval_packs`; the difference is stated where it lives.
- `eval_packs(withheld=...)` builds those rules and marks them `withheld_by_opt_in`.
- `choose_pack` returns `how: "opt-in.withheld"`, naming the pack and the remedy.

**Measured: 2,889 of 2,889 stranded slots now name the pack that was withheld and why.**

**The branch order is a measurement, not a preference.** It was written to test withheld first and
that relabelled exactly one address: `scottish-baronial.trim_family`, which binds the slot
`forbidden` and had read `kit.forbidden` correctly since WP-8.3. Calling it WITHHELD offers the
author a remedy — write `inherits_packs` — **that would not dimension the slot**, because the kit
forbids it however the pack arrives. The kit's refusal is unconditional and now comes first. It was
found only by the gap between two counters, 11 slots reported withheld against 10 that lost
dimensioning, which is why both are printed.

## Three things that were reported and are now measured

**`measure()` could not see the flip.** It skips a declined pack — its own comment argues that a
meter which does not "would go on describing a corpus nobody resolves" — and did not skip a
withheld one. So `inherited_packs` went on counting 35 arrivals that had stopped: the meter built
to measure OQ 51 could not see OQ 51 being fixed. The identical argument, applied.

**The ceilings fell without a single case being adjudicated.** `role_gaps` 264 → 258,
`inherited_packs` 3158 → 3123, `unendorsed` 223 → 217 — all because deliveries stopped, none
because anyone read anything. **`judged` did not move, at 249**, and that is the whole of how the
two are told apart. `--strict` now prints a `withheld` line beside the three saying so, so a reader
need not already know it. This is the first real test of a floor added in WP-8.2 for exactly this.

**The drift message could never show the new value.** As shipped in WP-8.9 the comprehension took
`v` from `STRANDING` on both sides, so it printed `stranded 2899 -> 2899` — it could say a count
had moved and never what to. Found by using it, on the first flip.

## A FLIP REFILLS THE BACKLOG EXACTLY AS A DECLINE DOES, and that was not expected

WP-8.7 measured the refill on declines and made it the argument for flipping at all: reading the
backlog produced 244 → 73 → 50 → 36, geometric at about three quarters, so adjudicating to the end
costs of the order of a hundred more readings over a dozen passes. The flip was ruled as the way
out of that loop.

**It is not out of it.** Withholding `trim-classical` from ten nodes promoted `trim-sawn` and
`trim-craftsman` into the interior role on four of them — `jacobethan-revival`,
`mediterranean-revival`, `queen-anne-patterned-masonry`, `ranch-style` — four live unendorsed gaps
that did not exist before the flip and that nobody has read. **The refill is a property of the
CASCADE, not of adjudication:** any mechanism that stops a delivery hands the role to the next
ancestor, and a flip is such a mechanism. Found by `test_wp87_adjudication.py`, which was written
for declines and caught a flip without being changed.

That does not overturn the ruling — a flip still stops many deliveries per reading where a decline
stops one — but the refill ratio is now a property to measure per flip rather than a cost the flip
avoids.

## Ten tabled cases were WITHDRAWN, and not one of them was decided

`oq/the-adjudication-cases-the-records-do-not-decide` carried a `trim-classical` section of exactly
ten rows: the ten nodes this flip stranded. They are no longer live gaps, so the table's own guard
refused to carry them — correctly. **Nobody ruled on any of them.** They are kept verbatim under a
separate heading saying they were withdrawn rather than answered, because a flip is reversible:
writing `inherits_packs` on any of those nodes, or returning the pack to `cascade`, makes all ten
live again, and deleting them would have destroyed ten readings for a later session to redo.

`scottish-baronial` is the exception and is the same finding as the branch-order defect above from
the other side: its kit binds `trim_family` **forbidden**, so its slot reports `kit.forbidden`, and
a binding that predates the flip had already settled what its row was asking.

## Two interactions the flip creates

**A decline on a flipped pack refuses nothing.** Six nodes decline `trim-classical`; the gate now
stops it first, so `test_every_decline_is_proved_against_the_undeclared_corpus` fired. The decline
is not refuted, it is **superseded** — a decline is a person's judgment, a flip is a delivery
mechanism, and deleting the six would destroy six adjudications and take `judged` through its own
floor. The counterfactual now lifts both the decline and the gate, so the property still bites;
mutation-checked with a decline naming an unreachable pack, which still fails.

**`--stranding <a flipped pack>` prints a bare zero**, because the counterfactual has become the
status quo. A reader would conclude the flip cost nothing. The sweep now prints an ALREADY WITHHELD
block first, naming the realised loss.

## Counts

`RATCHET` 258/3123/217 · `RATCHET_FLOOR` 249 (unmoved) · `FORBIDDEN_RATCHET` 776 → 761 ·
`STRANDING` before 7820, after 4931, stranded 2889, rehoused 1980, nodes 124 · corpus `unreached`
179 → 111, because `trim-classical` carried 119 of those addresses and a gated pack is no longer in
the counterfactual. `check_counts` 88 claims, 0 stale. New suite `tests/test_loud_stranding.py`
(21), mutation-checked three ways — removing the `choose_pack` branch, dropping instead of marking,
and emptying `withheld_for` — each mutation asserted to have LANDED before the colour was read.

## Deliberately not done

**No second pack is flipped.** `facade-gable` and `sash-light` both want
`oq/a-pack-can-be-the-only-writer-a-node-has` ruled first, since the correction above applies to
them with more force, not less.

**The 111 addresses that survive any flip**, the 181 tabled cases, the 36 unread gaps, and the 71
baked-versus-refused pairs — all unchanged, all still where their own entries put them.
