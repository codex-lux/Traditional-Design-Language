# OQ 51, first adjudication pass — eleven judged, and the finding that the other half cannot be judged at all

*26 August 2026. The ruling of 25 August is adjudicate-first: work the role gaps nobody has
judged, in leverage order; where the inherited pack is right for the node, add the node to that
pack's `applies_to`, which IS the adjudication; where it is wrong, bind the right pack or scope
the edge. This is the first pass against that ruling. It moved the meter — **unendorsed 233 →
222, endorsed 61 → 72** — and it found something about the ruling's own feasibility that is worth
more than the eleven.*

---

## What was adjudicated, and on what evidence

`storey-graduation` heads the leverage list at 38 nodes. All 38 gaps are the **massing** role,
and 24 of them arrive through one ancestor, `english-georgian`.

Every endorsement below was made by reading the node's own record and quoting it. That
discipline is the whole point: an endorsement is permanent, it writes a pack's dimensions into a
node's kit for good, and endorsing on an architectural hunch would be exactly the laundering of a
guess this corpus forbids. Where the record did not decide the question, the node was left
unendorsed — eleven of thirty-eight is a deliberate result, not an incomplete one.

| node | the node's own words |
|---|---|
| `carpenter-gothic` | "a central gable rising through the eave line of an otherwise symmetrical **two-storey farmhouse**"; the i-house — the two-storey single-pile — is canonical for it |
| `greek-revival-upland-vernacular` | "the ordinary **two-storey** single-pile farmhouse", and "the **frieze-to-storey-height** and trim-width ratios are what make the building legible as classical" |
| `gothic-revival-british` | states its own storey heights directly |
| `queen-anne-british` | states its own storey heights directly |
| `chateauesque` | its own typical_ratios graduate the stack: a storey at **0.8 times the height of the storey immediately below** |
| `dutch-colonial-revival` | the gambrel stretched to "**a full second storey**", letting a builder "sell a two-storey house" |
| `octagon-house` | its own ratios are storey-based — "0.4 times the side length **per storey**" |
| `scottish-baronial` | measures its tower against the main ridge in **full storeys** |
| `shingle-style` | a continuous skin "running **across storey lines**" — a stacked house |
| `tudor-revival` | dimensions a **second-storey** jetty at 8–16 in |
| `prairie-school` | "vertical proportion is handled by **ceiling height differentiation**, not by facade ratio" — which is this pack's rule in the node's own words |

### One node was deliberately not endorsed, and it is the instructive one

`english-baroque` looked like a clear endorsement: its own typical_ratios carry "rusticated
basement 0.5 to 0.75 the height of the principal storey above it", which is a graduation ratio.
But its `distinguished_from` prose says that the Queen Anne house of 1700 and the Georgian house
of 1760 share a plan and a construction and that **Georgian is the one with graduated storey
heights**. The node uses the absence of this pack's rule as a distinguishing tell. Endorsing it
would hand the node the very trait its own record says separates it from its neighbour. Two
statements in one file point opposite ways; that is a question for a human, not a judgment for
this pass, and it is left unendorsed and stated here rather than decided quietly.

---

## The finding: the backlog is asymmetric, and only half of it can be worked

The ruling gives three moves for a gap: endorse it, bind the right pack instead, or scope the
edge. Working the first pack showed that **only the first move exists.**

- **Endorsing is one line.** Add the node to `applies_to`. Cheap, and it is what the eleven above
  did.
- **Binding a different pack does not remove the wrong one.** The cascade still delivers
  `storey-graduation`; a new binding competes with it on precedence rather than displacing it.
- **Scoping the edge is not implementable today.** A lineage edge carries `inherits_kit`, which
  governs the KIT cascade, and nothing that governs the PACK cascade. `inherits_packs` — the
  mechanism the ruling names — does not exist in the schema, in `build/`, or anywhere but the
  register's own text. Verified by grep.

So a node that the pack genuinely fits can be settled in a line, and a node it genuinely does not
fit **cannot be settled at all.** And the clearest examples are not marginal:

| node | its own words | why the pack cannot apply |
|---|---|---|
| `ranch-style` | "everything about it is horizontal: **a single storey**" | a rule for graduating a stack has no stack to graduate |
| `craftsman-bungalow` | "**one to one and a half storeys**, 800 to 1,400 sq ft" | same |
| `california-bungalow` | the bungalow type — low, broad, mainly single-storey | same |
| `minimal-traditional` | "the house is a compact rectangle… **one storey or one and a half**" | same |

`ranch-style` is the register's own worst-case example — 69 of its 78 dimensioned slots governed
by packs it never bound — and this pass can do nothing about the storey-graduation half of it.

**Why this matters to the ruling rather than merely to the work.** Working the backlog in leverage
order will systematically settle the endorsable half and leave the refusable half untouched. The
meter will fall, and it will fall *fastest* on the nodes where the cascade was already right —
because those are the easy ones to evidence. The corruption the meter exists to measure is
concentrated in exactly the cases the meter cannot currently be moved on. A falling `unendorsed`
therefore does not mean a corpus getting more correct at the same rate, and nobody reading the
number would know that from the number.

**What would fix it, cheaply and without the flip.** The ruling defers `inherits_packs` to the
end because flipping inheritance to opt-in strands 294 gaps in one commit. That reasoning holds.
But the refusal half needs no flip: an additive, per-node **declined-packs** list — a node naming
a pack that reaches it by descent and does not belong, with a stated reason — would let the wrong
half be adjudicated now, strand nothing, and let `check_inheritance` count a declined gap as
judged. It is the same shape as the endorsement it mirrors, and it would make "adjudicate first"
a thing that can actually be finished. **This is a proposal, not a decision** — the mechanism is a
schema change and the ruling's sequencing is Lucas's; it is recorded in OQ 51 for a ruling rather
than built here.

---

## What was deliberately not done

- **The other 27 storey-graduation gaps.** Their records do not decide the question, and this pass
  would have had to supply the judgment from outside the corpus to close them. `arts-and-crafts-american`,
  `craftsman`, `queen-anne-american`, `stick-style`, `jacobethan-revival`, `french-eclectic`,
  `rural-gothic-villa`, `egyptian-revival` and the rest are left for a session that can read them
  properly, or for a ruling.
- **The other six packs on the leverage list** — `opening-proportion` (23), `trim-classical` (16),
  `chambers-ionic` (15), `facade-gable` (14), `sash-light` (12), `brick-course` (11). One clean
  sub-case is worth naming for whoever takes it: **all 13 of `facade-gable`'s unendorsed gaps
  arrive from a single ancestor, `gothic-revival-british`**, which makes it one judgment about one
  edge rather than thirteen about thirteen nodes.
- **No refusal was recorded as data**, because there is nowhere to record it. The four in the table
  above live in this report and in OQ 51, which is the honest place for them until a mechanism
  exists.

## Where the ancestors sit, for the next pass

Grouping the whole 233 by the ancestor that delivers the gap, rather than by pack, shows where the
leverage really is:

| ancestor | unendorsed gaps it delivers | the packs |
|---|---|---|
| `english-georgian` | 46 | storey-graduation 24, chambers-ionic 15, trim-classical 7 |
| `roman-classical` | 18 | opening-proportion 8, facade-peristyle 8, room-harmonic 2 |
| `colonial-revival` | 18 | gibbs-ionic 5, gibbs-doric 5, storey-graduation 5, trim-classical 3 |
| `greek-revival-american` | 15 | vignola-ionic 5, opening-proportion 2, trim-classical 2 |
| `richardsonian-romanesque` | 15 | brick-course 5, facade-picturesque 4, sash-light 4 |
| `gothic-revival-british` | 13 | facade-gable 13 |

`english-georgian` alone delivers a fifth of the entire backlog. If `inherits_packs` is ever
built, that is the first edge to look at — and this table is the argument for looking at the
backlog by ancestor as well as by pack, because an ancestor is where a scope would be written.
