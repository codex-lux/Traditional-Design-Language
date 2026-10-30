# oq/the-composer-returns-sets-in-which-nothing-may-be-drawn — the ranking is right and has nothing to rank

*Status: CLOSED · Raised in: the follow-up to the candidate-click audit (16 October 2026)*

**OPEN — on both shipped briefs, `compose` called the way the app calls it returns sets in which most
or all of the candidates are refused by the type's own hard facts (WP-13.4), so a reader who picks any
of them cannot be offered a drawing.** Lucas ruled that a refused house ranks after a drawable one
(`oq/the-composer-ranks-first-a-house-that-may-not-be-drawn`, reading 1, 16 October 2026) and it is
executed; measured against these sets it changes almost nothing, because there is almost nothing
drawable to put first.

## What was measured

`compose(brief, 4, revise=True)` with the defaults (`auto`, the revision loop on, the app's own call),
on this container, twice per brief. The sets are not reproducible, so each row is one draw.

| brief | pass | candidates returned | refused | not placed (budget) | drawable |
|---|---|---|---|---|---|
| `family-georgian` | 1 | 4 | 4 | 0 | 0 |
| `family-georgian` | 2 | 4 | 4 | 0 | 0 |
| `bungalow-small` | 1 | 4 | 4 | 0 | 0 |
| `bungalow-small` | 2 | 4 | 3 | 1 | 0 |

The facts a refusal names, second pass: `family-georgian` — `bearing, stacks, tiling` (cp-sat),
`bearing, stacks` (heuristic), `bearing, stacks` as INFEASIBLE (the least-bad heuristic placement,
labelled), `tiling` (cp-sat, with 2 judged fatals); `bungalow-small` — `tiling`, `bearing, stacks,
tiling`, `stacks, tiling`. Most revision loops stopped on `budget`, not on convergence.

## What is not known

- Whether a drawable candidate exists for these briefs and the loop's budget is what stops it being
  found. Three of four `family-georgian` loops stopped on `budget` while holding a refusal; a
  longer proof held one more fact on a candidate in an earlier measurement and still refused it.
- Whether the refusal is a property of the diagrams (a parti whose `stacks_over` claims the placer
  cannot hold with the programme's rooms) or of the placer's wall-clock engine, which is not
  reproducible: the same diagram read 0 fatals and led in one pass and read 2 and trailed in the other.
- Whether `tiling`, `stacks` and `bearing` recurring here is the same cause as the Phase 13 gate's red
  rows (`tests/test_sheet_coherence.py`), which concern the same facts on the SHIPPED records. They
  are not the same population (composed candidates against two shipped plans) and nothing here
  established that they share a cause.

## What a ruling would choose between

1. **Leave it.** The strip, the tally and the conflict set already say a set is refused; the reader is
   told to change the brief or the parti. Cheapest, and it leaves two shipped briefs that cannot be
   drawn from.
2. **Make the loop work for a drawable result.** `revise._improves` already refuses a round that makes
   a placement newly refused; it does not try to REMOVE a refusal. A move that answers a refused fact
   (give the stack its wall, give the tiling its slack) is a new class of move, and the registry's
   rule is that every move executes a sentence in the corpus.
3. **Return fewer, but drawable.** Keep going past the requested count, down the ranked pool, until
   enough placed candidates are not refused; say how many were passed over and why. The composer's
   guarantees (a named parti has a place, a fatal never displaces a clean one) bear on it.

## Not done

Nothing. The ranking, the strip and the tally are the surfaces saying the current state out loud.

## Ruled and executed, 29 October 2026 (Phase 17, WP-17.6)

**CLOSED.** Lucas chose reading 3 (ruling 3 of 29 Oct 2026, as the recommended option): a short set is
filled from the ranked pool, every passed-over diagram named, and the set keeps the 16 Oct key (ruling 7).
`compose.compose` places down the pool -- at most `POOL_FILL_PLACEMENTS`, inside the set's budget -- and a
house it finds drawable joins the set; `result.pool_fill` names what it added, what it passed over and
why, and what it did not reach. The rest of Phase 17's first tranche is what makes a drawable house there
to find (`docs/reports/wp-17.0-the-house-the-card-describes.md`).

Measured on Lucas's own brief, once, at production defaults: five candidates, TWO of them drawable
(`living-hall-picturesque`, asked; `courtyard-and-portal`, filled from the pool), against none of four
before. Both are borrowed diagrams; every native diagram for a Tidewater Georgian brief is still refused,
and that is carried by `oq/the-side-hall-partis-stacks-cannot-co-hold-in-band` and the report, not by this
question, whose subject -- a ranking with nothing to rank -- is answered.
