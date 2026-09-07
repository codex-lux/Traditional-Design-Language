# WP-8.12 — the third flip, and the refill that was not proportional

*3 September 2026. `sash-light` declares `delivery: opt-in`. Third of the staged flips.*

## The flip

**70 slots over 34 nodes**, the measured figure exactly. Seven nodes opted in first — every one
vouched by the pack's own `applies_to` and receiving it by descent.

**The two-gate gap was 70 against 84, the largest yet**, and each of the seven vouched-by-descent
nodes loses exactly two slots. Three data points now:

| flip | meter's figure | what a flip without opt-ins strands |
|---|---|---|
| `trim-classical` | 10 | 15 (+50%) |
| `facade-gable` | 32 | 33 (+3%) |
| `sash-light` | **70** | **84 (+20%)** |

Nothing like stable. `applies_to` names 40 nodes here, but **33 of them BIND the pack themselves**
and are never gated — the vouched-and-gated population is what matters and it is not a fixed
fraction of anything.

## THE FIXTURE MOVE WAS DONE FIRST, AND IT SHOULD HAVE BEEN DONE DIFFERENTLY TWICE

WP-8.11's finding was that a driven test fixture must name a pack nobody has flipped. It then
pointed `test_stranding.py`'s staging case at **`sash-light` — the pack next in the flip order**,
which guarantees moving it again one package later. Which is exactly what happened.

**The rule is sharper than WP-8.11 stated it: a driven counterfactual should name a pack scheduled
LAST, not one scheduled next.** `opening-proportion` is one of the five whose `applies_to` arms a
live behavioural gate, so the ruling puts it at the end of the order — it stays on `cascade` longer
than anything else, which is precisely what a fixture wants. It also makes the case stronger: 146
slots over 61 nodes against `sash-light`'s 70 over 34.

The move was made and verified green **before any data changed**, which is the only reason it is a
paragraph here rather than a defect.

## THE REFILL IS NOT PROPORTIONAL, AND TWO POINTS SAID IT WAS

WP-8.11 measured 4 new gaps from a 10-slot flip and 13 from a 32-slot one and called the rate
"roughly proportional, not decaying". The third point falsifies it: **10 from a 70-slot flip.**

| flip | slots stranded | gaps promoted |
|---|---|---|
| `trim-classical` | 10 | 4 |
| `facade-gable` | 32 | 13 |
| `sash-light` | **70** | **10** |

What refills is a function of how many ROLES the withheld pack was filling and what sits behind it
in each node's chain — not of how many slots it dimensioned. Two points make a line; three made it
a different shape. That is this repository's own recurring lesson arriving on my own published
claim, one package after I published it.

## AND THE REFILL IS CONCENTRATING ON THE GATED PACKS

Three of WP-8.11's thirteen promoted a live-gate pack. **Ten of ten do here — every one
`opening-proportion`.**

This follows from the flip order rather than from chance. The ruling puts the five gated packs
LAST, so they are what is still delivering once everything else has been withheld, and they inherit
each role a flip vacates. **The order chosen to make the early flips safe back-loads exactly the
rows whose adjudication carries a behavioural consequence** — a reader ruling on one of those ten
is authorising `graduation_check` or the elevation generator to switch on, not merely restoring a
dimension. They are marked ⚡ in the register.

Worth putting to Lucas before the gated packs come up, because it means the remaining flips are not
more of the same.

## A MAGIC-NUMBER FLOOR REPLACED BY A CROSS-CHECK

`test_wp87_adjudication.py`'s vacuity guard asserted the ruling table parses **at least 150 rows**.
Three flips have now withdrawn 10 + 13 + 11 = 34, and it reached 147. Lowering the number every
flip is the anti-pattern this repository argues against in `test_construction_scope.py` and in
`check_inheritance`'s own ratchet comments: a floor that drops whenever somebody does the ruled
thing protects nothing by the end.

So the guard is a **cross-check** now, and it is strictly stronger. Each pack heading states its own
row count beside the rows it heads; the heading regex and the row regex are independent, so a broken
row pattern makes the two disagree, and a heading that went stale when rows were withdrawn is caught
by the same assertion. Mutation-checked both ways — breaking the row regex fails it, and adding one
to a single heading's count fails it.

## And the whole suite earned itself a fourth time

`pytest tests/` was the only red check, and the two failures were the same illustrative pin in two
files: **`ranch-style: 68 slot(s) dimensioned, 61 by a pack it never bound` is now 66 / 59**, because
`sash-light` was dimensioning two of that node's slots.

That figure is OQ 51's own founding illustration — the entry opens with "`ranch-style` has 69 of its
78 dimensioned slots governed by packs it never bound". **It is now false as a present-tense claim,
and correcting it to 59 of 66 without saying why would be worse than leaving it**, because the fall
is the flips REMOVING deliveries, not the node becoming better bound. `CLAUDE.md` states it in the
past tense with both numbers and the reason, which is the only honest form: it is what raised the
question, and what the question is about is no longer true of the corpus in the same way.

## Counts

`RATCHET` 256/3056/215 → **255/3022/214** · `FORBIDDEN_RATCHET` 723 → **721** (only two pairs, against
15 and 38 for the first two flips — this meter and the stranding meter are not proxies for each
other) · `STRANDING` before 7788 → **7718**, stranded 2857 → **2787** · `baked_vs_refused` 71 → **67**,
which is *not* the second delivery path closing: those four went because the live rule they were
measured against no longer reaches those nodes.

`rehoused` is **1980 for the third package running** and `dimensioned_after` is **4931 for the
fourth**. The end state has never moved, whichever pack flips and in whatever order — the plainest
demonstration that these pins describe a path being walked, not a corpus getting better.

**`judged` is 249.** Three flips, 136 withheld arrivals, zero cases read.

## Deliberately not done

The five live-gate packs. On the evidence above they are a different kind of decision from the
three flips so far, and the refill is now depositing rows onto them faster than anything is taking
rows off. The 181 tabled cases, the 63 unread gaps, the 96 addresses that survive any flip, and the
8 unjudgeable baked snapshots are all unchanged.
