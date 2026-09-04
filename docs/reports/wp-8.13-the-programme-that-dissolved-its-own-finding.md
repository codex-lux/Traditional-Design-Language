# WP-8.13 — the last five packs, and the finding the flip dissolved

*4 September 2026. OQ 51's delivery half, finished. Read
`docs/reports/wp-8.{10,11,12}-*.md` first if you are about to trust a figure here — this package
re-pins every number those three published, and two of them for reasons that are not improvement.*

---

## I. What Lucas ruled, and why the shape changed

The 3 September ruling staged the flip **pack by pack, in ascending stranded count**:
`trim-classical` 10, `facade-gable` 32, `sash-light` 70, and the five packs whose `applies_to`
arms a live behavioural gate last. Three packages executed that.

WP-8.12 then measured something the staging order had produced rather than discovered: **the
refill was concentrating entirely on the gated packs** — 3 of 13 new gaps at the second flip,
**10 of 10** at the third. That follows mechanically. The gated packs flip last, so they are what
is still delivering once everything else is withheld, and they inherit each role a flip vacates.
**The order chosen to make the early flips safe back-loaded exactly the rows whose adjudication
authorises a behaviour change.**

Put to Lucas as a question, he ruled on 4 September: **all five in one package.** Staging them
singly would have spread across five packages the one decision that mattered.

## II. The five, and both their gates

| pack | strands (meter) | nodes | opt-ins written | what its `applies_to` arms |
|---|---|---|---|---|
| `opening-proportion` | 146 | 61 | 4 | half of an AND in `elevation.py`'s `build_elevation` scope gate |
| `facade-classical` | 25 | 12 | 4 | the other half of that AND |
| `storey-graduation` | 9 | 8 | 13 | `structure.py::graduation_check` — storey ratios checked at all |
| `timber-bay` | 1 | 1 | 1 | `structure.py::span_check`, and `geometry_cp.py` reads the same list |
| `gibbs-ionic` | 0 | 0 | 4 | `elevation.py::gibbs_applies` — read OQ 84 first |

The gates are enumerated in `check_inheritance.GATES`, and `tests/test_wp46_packs.py` already
asserts each pack id still occurs in the file that table names, so a gate that MOVES fails a test.

## III. THE COMBINED FLIP STRANDS MORE THAN THE SUM OF ITS PARTS

Measured before the flip, and it is the number the package was planned on:

```
per-pack stranded   146 + 25 + 9 + 1 + 0  =  181
COMBINED stranded                            202
```

**+21 against the sum, and the DIRECTION is the surprise.** The naive expectation is that the
combined figure is LOWER — a node losing the same slot to two packs is counted once by each
per-pack sweep. It is higher, and the mechanism is **rehousing between the five**: a slot stranded
by `opening-proportion` alone is picked up by `facade-classical`, so neither single-pack sweep ever
counts it; withhold both and it strands. Each per-pack figure measures a world in which the other
four are still delivering.

So the sum is not a bound in either direction — **and this report first asserted that from one
measurement, which only showed the from-below sum under-stating.** Restoring each of the five one
at a time FROM the all-withheld corpus (the opposite counterfactual) gives 167 + 46 + 9 + 1 + 0 =
**223**, over-stating by 21:

```
    181   sum of marginal costs, measured from below
    202   the flip, measured jointly
    223   sum of marginal restorations, measured from above
```

The inequality inverts with the direction of measurement, so **a per-pack figure is a property of
the corpus it was measured against and not of the pack.** The two-directional claim is now
supported rather than asserted; it was true when written and the evidence for it was not here.
(Every published per-pack figure — 10 / 32 / 70 / 146 / 25 / 9 / 1 / 0 — re-derives exactly under
the condition its own package measured, and un-flipping all eight returns the corpus to 7,830,
which is the pre-flip baseline to the slot.)

Landed: `dimensioned_before` **7718 → 7516**, which is 202 exactly.

This is the third instance of the same wrong-grain shape — `unendorsed` for deliveries (WP-8.9), a
corpus writer count for a node fact (WP-8.10) — and **the first caught before publication rather
than after.**

## IV. THE FLIP DISSOLVED WP-8.12's OWN FINDING

Refill across the four flips: **4** new gaps from 10 slots, **13** from 32, **10** from 70,
**36** from 202. Still not proportional, and now the largest.

But the composition inverted completely. WP-8.12 found 10 of 10 new gaps landing on live-gate
packs. Here: **0 of 36.** All five are flipped and deliver nothing, so no vacated role can reach
them. The refill is now `opening-mullioned` 13, `brick-course` 11, `facade-arcade` 3,
`facade-peristyle` 3, `opening-pointed` 3, `timber-panel` 2, `facade-picturesque` 1.

**The concentration was a property of the staging order and finishing the programme ended it.**
That is the ruling being vindicated by the thing it was ruled about, which is rarer than it sounds
and worth saying plainly rather than claiming as foresight: the question was put because the
concentration looked dangerous, and the answer removed the mechanism producing it.

## V. `judged` MOVED, AND THE CODE SAID IT COULD NOT

`measure()`'s own comment reads **"IT MUST NOT MOVE `judged`"**, with a paragraph explaining why
the withhold branch sits where it does. `judged` went **249 → 250** on this flip, with no case
adjudicated, no `declined_packs` entry written, and no style file touched except `inherits_packs`.

**The route is `endorsed`, not `declined` — the half the comment did not consider.** Withholding a
pack VACATES the role it filled, and the role re-attributes to the next ancestor: the same
non-monotonicity that makes `unendorsed` a work list rather than a score. Where that next pack both
ARRIVES (the node opted into it) and VOUCHES (its `applies_to` names the node), the re-attributed
gap lands in `endorsed`.

Exactly one instance, pinned by name in `tests/test_opt_in_packs.py` because a count could not tell
this from an adjudication: **`american-farmhouse-vernacular` / role `opening`**, vacated by
`opening-proportion` (which that node does not opt into) and landing on `sash-light`, which it
opted into in WP-8.12 and whose `applies_to` names it.

The FLOOR is not violated — it forbids only going down — and the classification is not wrong: an
author really did vouch for that pack on that node. **What died is the reading three packages
rested on**, that `judged` is the one number telling a flip from an adjudication. It is not. Read
`--strict`'s `withheld` line for that. The comment is corrected in the same commit, under WP-6.4's
rule.

## VI. AN OPT-IN NEEDS TWO CONDITIONS AND THIS PACKAGE FIRST WROTE ONE

The opt-in list was derived from each pack's `applies_to`, minus the nodes that bind or decline it:
**40 entries over 30 nodes**. `check_opt_ins` refused **14 of them** — 35% of the list — because
`applies_to` says the pack is FOR this style and says **nothing about whether the cascade delivers
it there.** The two are independent, and WP-8.10's own rule had stated both conditions.

All 14 were no-ops, and that is provable rather than asserted: removing them left
`dimensioned_before`, `stranded`, `rehoused`, `unreached` and `nodes_touched` **byte-identical**.
Nothing but this check would ever have reported them, and an opt-in that admits nothing while
reading as a considered delivery is the failure mode `check_opt_ins` was written for.

Final: **26 written, 41 entries over 24 nodes** corpus-wide. `mid-atlantic-georgian` carries six,
`charleston-georgian` and `new-england-georgian` five apiece, `tidewater-georgian` four — the
Georgian cluster sits deep in a chain that delivered most of what got flipped.

**A second defect in the same hour, worth recording because it is the tester's own clothes again.**
The script written to REMOVE the 14 used `(keep if not errs else None) and keep.append(p)`, and
`keep` starts as `[]` — falsy — so the `and` short-circuited and nothing was ever appended. It
deleted every opt-in in the corpus, the 15 pre-existing ones included. Caught by the very next
assertion (`0 node(s) opt in`), reverted, and re-authored with both conditions in the loop.

## VII. The fixture rule expires here

`tests/test_stranding.py`'s driven case has moved three times: `facade-gable` → `sash-light`
(WP-8.11) → `opening-proportion` (WP-8.12, under "name a pack scheduled LAST") → and
`opening-proportion` is one of the five, so it would have gone vacuous for the third package
running.

**The rule is not "scheduled last", it is "not scheduled at all", and it only became stateable
when the schedule emptied.** The programme covered eight packs and is finished; the other 49 are
on `cascade` because nothing plans to move them. The case is `timber-panel` now (131 slots over
91 nodes), with `brick-course` as the contrast — **1 slot stranded against 66 surviving** an
inherited `slot.packs` ruling the flip cannot reach, on backlog counts of 9 and 15 that point the
opposite way to what a flip is worth.

`brick-course` measured 0 stranded before this flip and 1 after, and **1 is the better pin**: a
zero is what this finding looks like and also what a broken instrument prints.

## VII½. And the whole suite earned itself a fifth time, in `tests/test_gate_packs.py`

A file this package had no reason to touch, and both failures are the same shape as §VII.

**The sweeper test's vacuity guard became unsatisfiable.** `sweep_gates.py` restyles a reference
plan onto every style a pack REACHES. Before the flip that was all 128 for `storey-graduation` — 43
in its `applies_to` and 85 not — so one pack showed both verdicts and `not all(verdicts.values())`
was a real guard against the wrong-key bug that shipped once. The gate stops the pack everywhere it
is not opted into, so **the swept population is now exactly the 43, and all 43 are armed because
the two populations have become the same set.** The sweeper is right; the assertion's discriminating
power came from a difference the flip removed.

Fixed by giving it two controls instead of one: ARMED on the gate pack, UNARMED on `timber-panel`,
which the programme does not cover and which arms nothing over 23 styles. The per-style equality —
`armed == (style in applies_to)` — is unchanged and is the real property. A new assertion states the
condition that made the old guard redundant, so if the gate is ever lifted the test asks for its
`not all(...)` back.

**And `ARMS_IF_ENDORSED["facade-classical"]` went back to empty.** On 2 September that set stopped
being empty — sixteen declines had re-attributed the facade role on `folk-victorian` and
`greek-revival-upland-vernacular` onto `facade-classical`, both already inside
`opening-proportion`, so endorsing either would have switched the whole elevation generator on.
Both packs are now opt-in and reach neither node, so no pending gap is attributed there. **Nothing
was decided and the two are not endorsed** — the question simply stopped being reachable through
this pack, and the set stays pinned rather than asserted empty because the refill can put a node
back into it at any flip.

## VIII. Counts

| | before | after | note |
|---|---|---|---|
| `role_gaps` | 255 | **222** | |
| `inherited_packs` | 3022 | **2762** | |
| `unendorsed` | 214 | **180** | 70 gone, 36 new |
| `judged` (floor) | 249 | **250** | §V — moved without an adjudication |
| `FORBIDDEN_RATCHET` | 721 | **712** | |
| `STRANDING.dimensioned_before` | 7718 | **7516** | −202, the measured figure exactly |
| `STRANDING.stranded` | 2787 | **2585** | |
| `STRANDING.rehoused` | 1980 | **1895** | 1980 for three packages; the five moved it at last |
| `STRANDING.unreached` | 96 | **47** | |
| `baked_vs_refused` | 67 | **60** | the live rule no longer reaches those nodes |
| `STRANDING.dimensioned_after` | 4931 | **4931** | **unmoved for a fifth package** |

Every one of these falls **for the wrong-looking reason: measuring less, not improving.** That is
why `STRANDING` is a set of equalities rather than ratchets — a ceiling that may only fall is
satisfied by measuring less, and every figure here does exactly that.

`dimensioned_after` has now been 4931 through four flips and five packages. The end state was
always this corpus, whichever order the packs flipped in.

## IX. Deliberately not done

- **The 180 unendorsed gaps.** The flip was ruled to strand them, and it did. `judged` is 250
  against 367 adjudications' worth of reading in WP-8.7; the flip has never read a case and does
  not claim to.
- **The 47 `unreached` addresses.** A slot record naming a pack directly is outside anything the
  delivery mechanism can reach — stated since WP-8.9 and unchanged.
- **A checker for §V's class.** Nothing in the tree can verify that a conversation happened. The
  trap is written into `CLAUDE.md` and the remedy is procedural: write the question and the answer
  as two acts, and date the second from when it arrived.
