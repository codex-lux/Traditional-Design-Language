# WP-8.9 — the ruling that was taken on the wrong number

*3 September 2026. OQ 51's delivery half: the stranding meter, and the opt-in mechanism, staged.*

## What happened

Lucas re-ruled OQ 51 on 3 Sep: pack inheritance becomes opt-in, now, accepting that the unjudged
gaps are stranded in one commit. The record of that ruling — written here, from the plan that
offered it — said the cost was **~223**.

**It is 2,899.** Measuring before building found that the ruling had been taken on a count of ROLE
GAPS, and a role gap is not a delivery. Put back with the measurement, the ruling changed twice:
stage it pack by pack, and use a separate field.

**The mis-statement was mine.** The option I put to him said "accepting that the ~223 unjudged gaps
are stranded in one commit". `unendorsed` is a count of `(node, role)` pairs no pack author has
vouched for; the thing a delivery gate stops is `(node, pack)` arrivals, of which there are 3,158.
The two numbers had sat one line apart in the meter's own output for a week.

## The measurement

Swept over all 132 buildable nodes, gating delivery on "the node binds it, or the pack's own
`applies_to` names it":

| | |
|---|---|
| arrivals purely by descent | **3,158** |
| of those, vouched | **195** |
| deliveries stopped | **2,963** |
| slots dimensioned, before → after | **7,830 → 4,931** |
| **slots losing ALL dimensioning** | **2,899 (37%)** |
| re-housed on another pack | 1,982 |
| **surviving the flip entirely** | **179** |
| nodes touched | **124 of 132** |

`egyptian-revival` goes from 65 dimensioned slots to **1**. `tidewater-georgian`, one of the two
shipped reference plans, loses 17.

## The per-pack numbers are the useful part, and they invert the obvious staging order

The backlog count is a bad guide to what a flip does:

| pack | unendorsed gaps | slots stranded | slots surviving the flip |
|---|---|---|---|
| `storey-graduation` | 23 | **9** | **45** |
| `facade-gable` | 16 | **32** | **0** |

`storey-graduation` leaves five times more addresses standing than it moves, because
`choose_pack` reads the resolved slot record's own `packs` block **before** the rows and that block
cascades — so a pack keeps governing an address after the cascade stops delivering it. **A staging
order taken off gap counts alone picks the ineffective pack first.** Corpus-wide that condition
covers **179 slots**, and no mechanism about delivery can reach it: the slot record names the pack
directly.

## Why not `applies_to`

It is already a live behavioural gate on five packs — `storey-graduation`, `timber-bay`,
`opening-proportion`, `facade-classical`, `gibbs-ionic` — and **57 of the 223 gaps sit on them**.
Gating delivery there would make one endorsement mean three things at once: an author vouched, the
pack is delivered, and a generator switches on. Restoring a dimension would silently arm
`graduation_check` or the elevation generator. Lucas ruled them apart.

## What was built

**The meter.** `check_inheritance.py --stranding [PACK]`, corpus-wide or scoped to one pack for
staging. `governed()`'s `drop` was generalised from an id to a set — `--impact` asks the one-pack
question, this asks the many-pack one, and they are the same function because the second is the
first summed. 6.5 s, in `check_all.py` beside the 4.4 s `--forbidden` sweep it is modelled on.

**The mechanism, inert.** A pack declares `delivery: opt-in`; a node names it in `inherits_packs`.
One conditional in `resolve_packs`, beside the `declined` set, because they are the same question
answered opposite ways. Per-**node**, and that grain is measured rather than chosen: a per-edge
opt-in mirroring `inherits_kit` was costed and refused in OQ 51 — only about half of all gaps reach
their delivering ancestor through a direct edge at all, and `_cascade` is flattened, so the
delivering edge is not recoverable from the chain.

**The lie-check**, `check_pack_bindings.check_opt_ins`, the exact mirror of `check_declines` in the
same words: an opt-in that admits nothing reads exactly like a considered one. Four branches — a
pack that does not reach the node, one the node already binds (taken at `chain[0]` anyway), one it
also declines, and a duplicate.

## Three things that could have shipped silently, and what stops each

**A gate that cannot fire.** `resolve_packs` reads `graph["_packs"]`, built into
`dist/taxonomy.json` so the resolver does no I/O. An **absent** index and a corpus with nothing
flipped read identically there — a stale `dist/taxonomy.json` would disable the gate rather than
fail. The index is required to exist and to name every pack on disk.

**A mechanism that changes nothing on the day it ships is indistinguishable from one that does not
work.** Nothing is flipped, so the corpus is pinned unchanged *and* the gate is driven directly
through four states: default delivers, flipped does not, opting in re-admits, and a node that BINDS
a pack is never gated. Three mutations — the gate off, the gate ignoring the opt-in, the gate
hitting the node's own binding — are each caught by the test written for them.

**A bucket that cannot move.** The first draft of the sweep printed "of those, on a slot the kit
FORBIDS: 0". It is structurally always zero: a forbidden slot never enters `before`, because
`eval_packs` marks its rows `refused_by_kit` and `choose_pack` returns no `chosen`. A zero looks
like information. Removed, with the reason recorded where the bucket was.

## The direction of a lie is measured, not assumed

The plan for this package predicted that omitting the "still governed by the dropped pack" branch
would make the sweep **over-report relief** — because that is what the same omission did in
`--impact`, where the empty post-drop source lookup made a slot read as re-housed. Run, it does the
opposite: those 179 slots fall into `stranded`, **2,899 → 3,078**, over-reporting the **cost**.

One omission, two instruments, opposite lies. The comment in the code states the measured direction
and says the plan guessed the other one. And the headline cannot see it either way:
`dimensioned_before` and `dimensioned_after` are byte-identical under that mutation, so only the
bucket split shows it — which is why `tests/test_stranding.py` pins the buckets and not the totals.

## And WP-8.8 had shipped a corpus-wide bound on a filtered run

Found here, by a test about something else. The baked-snapshot check's two bounds — 135 judged, 8
unjudged — are claims about the whole corpus, and they were asserted unconditionally: so
`check_kits.py <one-style>` saw about ten snapshots against a floor of 135 and **errored on every
node in the corpus**. The floor was working correctly on a question nobody had asked it.

It did not show on `check_kits.py` with no argument, which is how WP-8.8 verified. It showed on
`test_kit_cascade.py`'s dangling-replace test, whose *cleanup* re-runs one kit and asserts the
corpus is clean again — a test about `replace` ops, on the full suite, after the targeted suites
were green. **The same shape as the unsorted glob WP-8.7 shipped**, and the same argument for
running the whole suite before pushing rather than after.

Both bounds are scoped to a whole-corpus run now, and a single-kit run **says** they were not
judged rather than silently skipping them — unjudged is not passed, including about itself.

## Counts

These are pinned as **equalities, not ratchets**. A ceiling that may only fall is satisfied by
measuring less, and every one of these falls as the flip lands — which is the flip working, not the
corpus improving. `RATCHET_FLOOR`'s own comment makes the same argument one layer up.

`check_all` goes 46 → **47** checks and the suite 1,505 → **1,515** tests; the identity CI prints
becomes "44 of 47 checks passed" against a `len(CHECKS)` of 44.

## Deliberately not done

**No pack is flipped.** The mechanism and the meter exist; the first flip is a separate, deliberate
edit that re-pins the stranding counts in the same commit. On the measurement `facade-gable` is the
candidate — 32 stranded, none surviving, and not one of the five live gates.

**The 179 that survive any flip.** Not a delivery problem, so not this mechanism's to solve; it
wants a ruling about whether an inherited slot-level `packs` block should outlive the cascade that
justified it. Adjacent to OQ 87 and to `oq/a-baked-pack-value-is-a-second-delivery-path`, which is
the same shape at the parameter layer.

**The 181 tabled cases and the 36 unread gaps** — still a human ruling.
