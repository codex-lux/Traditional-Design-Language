# WP-8.8 — the evaluator that was already there, twice

*3 September 2026. Closes half of `oq/a-baked-pack-value-is-a-second-delivery-path` and records
Lucas's re-ruling of OQ 51.*

## What was asked for

`oq/a-baked-pack-value-is-a-second-delivery-path` ended: *"a checker over all 143 needs an
expression evaluator and a decision about what to do with a snapshot whose context no longer
exists, which is what this question is for."* Its published state was that **143** kit parameters
carry both an `expr` and the `computed_at.value` that expression produced, that **exactly one** was
of a shape a narrow reader could evaluate, and that the count of stale snapshots was therefore
**unknown, not zero**.

## What was actually missing

**Not an evaluator. A verdict.**

`proportion_engine.evaluate_expr` is a general AST-walking safe evaluator, and it parses every
expression shape in use — there was never a parsing problem. Normalising all 143 expressions to
their shapes gives ordinary arithmetic over named bindings with `ceil`, `floor`, `round` and `max`;
the engine has handled that since the packs were built.

Worse for the question's own account: **`resolve_kit.eval_parameters` has been re-deriving every
baked parameter and comparing it against `computed_at.value` all along.** Lines 652-658 evaluate
the expression, compare, and set `r["stored"] = ca["value"]` on a disagreement greater than 0.01.
`stored` is a display field. Nothing reads it. Nothing fails on it.

So the sentence that closed the question was wrong about the obstacle, and the obstacle it named
had been solved twice. That is worth more than the fix: **a question can stay open for want of a
thing that already exists, because the question describes the gap in terms of what would be needed
rather than in terms of what is already there.**

## The measurement

`build/check_kits.py::check_baked_snapshots` re-derives every snapshot **at the context the
snapshot itself records** and compares it to the stored value.

| | |
|---|---|
| baked snapshots (`expr` + `computed_at.value`) | **143** |
| judged, and agreeing with their own expression | **135** |
| **stale** | **0** |
| could not be judged | **8** |

It lives in `check_kits.py` rather than in a new checker because that is the file the question
names as the one that should have caught the defect and did not — `check_derived_module_family`
holds the `computed_at` CONTEXT keys consistent across a slot family and explicitly `continue`s on
`"value"`, the one key that had gone wrong. It also keeps `check_all`'s check count at 46.

## Why 8 cannot be judged, and why that is not a footnote

`computed_at` records **three** bindings — `ceiling_height_in`, `storey_height_in`,
`opening_width_in` — and the expressions read **five**. Seven snapshots read `span`, one reads
`room_width`, and neither is ever recorded.

All eight reconcile at a span of 540, which is `check_kits.REF_CTX`'s value and evidently what they
were baked at. **That is a reconstruction of the context, not a record of it**, and a check may not
convict or acquit on a number nobody wrote down. They are reported UNJUDGED, counted, and
ratcheted. All eight are on `georgian-colonial-american`, where the `facade-classical` and
`trim-classical` rules were baked.

`module`, `part` and `column_height` are *not* in `computed_at` and do not need to be: they are
functions of the pack the parameter names in `source`, so they are recoverable rather than assumed.
That distinction is the whole of what makes 135 judgeable.

**The remedy is one field.** The reader maps `<name>_in` to the binding `<name>` for any key rather
than for a list of three, so writing `span_in: 540.0` on those seven makes them judgeable with no
code change. `test_recording_the_binding_closes_the_gap_without_touching_the_checker` proves it
both ways: the snapshot becomes judged, and a wrong value then fails. **The remaining open half of
the question is now narrow** — should `computed_at` be required to record every binding its
expression reads? That is a kit-schema change and a regeneration of eight records, and it would
take the unjudged count to 0 honestly rather than by looking away.

## The guard's own ratchets cannot guard it

This is the finding to carry.

`check_baked_snapshots` pins a ceiling on the unjudged count (8) and a floor on the judged count
(135). **Deleting the gap detection satisfies both while destroying the honesty.** Measured, with
the detection removed:

- the 8 are judged against `DEFAULT_BINDINGS`, whose `span` is **240** where they were baked at 540
- **seven are convicted as stale** — *unjudged reported as failed*, this corpus's own named
  dangerous direction
- the eighth, which reads `room_width` where the default happens to match, **passes in silence**
- `baked_judged` rises 135 → 143, **above** its floor; `baked_unjudged` falls 8 → 0, **below** its
  ceiling; neither ratchet fires

Both wrong directions from one deletion, with the build green. So `tests/test_baked_snapshots.py`
pins the **identity** of the eight as a set, not their count, and every branch is entered by
mutation. Four of its nine tests go red on that deletion.

**A ratchet on a number cannot guard the instrument that produces the number.** The check-count
guard has been earning itself for a week on exactly this principle; this is the same lesson on a
measurement rather than a tally.

## It catches what it was written for

Restoring WP-9.6's defect — `ceil(module / 7.5)` beside a stored `17` — makes `check_kits` fail,
naming the value, the expression and the recomputation. `check_addresses.py --strict` stays green
with the defect in place, confirming the question's account that the two measure different things.

## The other half is untouched, and the two must not be quoted for each other

`check_addresses.py::baked_vs_refused` measures a snapshot delivering a value the **live rule
refuses** — a scope, a decline, or a `forbidden` binding. Re-deriving a snapshot against its own
expression says nothing about that: **a snapshot can be perfectly faithful to its expression and
still be a delivery nobody authorised.**

That meter was also stale in the question's own body, which said 32 while the checker read 71 — in
the same paragraph that instructs the reader to *"quote `check_addresses.py --strict` rather than
this sentence if the two ever disagree"*. It has now been wrong four times in the same direction.
Corrected and re-measured: **71 pairs over 29 nodes and seven packs; 51 escape a decline, 20 escape
the construction scope.**

## OQ 51 was re-ruled, and it reverses the 25 Aug ruling's second half

Recorded here because it governs the next package. **Lucas, 3 Sep 2026: flip pack inheritance to
opt-in NOW**, accepting that the unjudged gaps are stranded in one commit rather than adjudicated.
The 25 Aug ruling refused exactly that, on the argument that it "strands 287 gaps in one commit".

**The single new fact is the measured cost of the alternative.** WP-8.7 read the backlog end to end
three times: **244 → 73 → 50 → 36**, geometric, each pass surfacing about three quarters of the
last. Three passes bought `judged` 48 → 249 and left 223 unendorsed; the remainder is of the order
of a hundred more adjudications over a dozen passes, each costing a reader and an adversarial
check. Adjudicate-first is finishable, at a price that now outweighs the stranding.

**Stated in the register and in CLAUDE.md so the next package does not over-read it:** the 249
judgments are not wasted, the 181 tabled cases stay open, and **the flip does not close the baked
path** — a snapshot in an ancestor's kit file is not a cascade delivery, so `inherits_packs` cannot
stop one. And the flip **must strand loudly**: a node that stops receiving a pack it was silently
receiving loses dimensions on real slots, and a slot reading as undimensioned rather than as
refused is OQ 51's own silent corruption arriving from the other direction.

## Files

`build/check_kits.py` (`check_baked_snapshots`, its two ratchets and the report) ·
`build/check_counts.py` (three computed values, five claims, read from the checker that owns the
judgment rather than re-derived) · `tests/test_baked_snapshots.py` (new, nine tests,
mutation-checked) · `docs/open-questions/oq-a-baked-pack-value-is-a-second-delivery-path.md` ·
`docs/open-questions/051-lineage-cascade-delivers-proportion-packs-nobody-bound-bou.md` ·
`CLAUDE.md`.

## Deliberately not done

The `inherits_packs` flip itself — ruled, not built, and it wants the loud-stranding meter first.
The kit-schema change that would let `computed_at` record every binding its expression reads. And
the 71 baked-versus-refused pairs, which are the other half of the same question and need the
parameter-level scope the entry has always said they need.
