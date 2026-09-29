# oq/a-leaf-refused-for-a-neighbour-that-is-itself-refused — 232 of 255 leaved windows lose their shutters, and 82 of them only to leaves that are not drawn

*Status: IN PROGRESS (ruled 29 September 2026; executed by Phase 16) · Raised in: WP-14.6's second audit (27 Sep 2026), re-derived by the audit of Phase 14 (27 Sep 2026)*

## The rule as it stands

WP-14.6 taught `elevation._clearances` that a shutter leaf is a real thing that swings onto real
wall. A pair that would lie over the next opening, over another window's leaves, or past the
corner of the face is REFUSED and said, and never narrowed, because a narrower leaf would be a
figure no record states. That part is not in question.

What is in question is one sentence of the rule's arithmetic. **Every refusal is decided against
the leaves AS COMPOSED**: a window's pair is judged against every neighbour's pair as if that
neighbour's pair were hung, including a neighbour whose own pair the same pass refuses. So a
window can lose its shutters to leaves that are never drawn. `tests/test_clearances.py` pins
today's reading with its reason, and says it changes with a ruling.

## The measurement

Re-derived on the audit's tree, over the census's 63 elevation sheets that carry leaved windows:
the 24 shipped-plan faces, and the 39 style fronts of the sweep.

| reading | windows refused their leaves |
|---|---:|
| today's rule: judged against every pair as composed | **232 of 255** |
| one pass in the rects' own order: a refused pair is withdrawn before the next window is judged (the second audit's mutation M3c) | **150** |
| the best ANY order can do: the largest set of pairs that can all be hung, per sheet, found exhaustively | **150** |

**82 windows** differ between the two readings.

- **4** are on the shipped-plan faces, 37 → 33 of 60, one window each on `bad-01-grilling-porch-ranch`
  S, `good-05-lobby-gallery-mansion` W, `good-07-diamond-plan-house` E and `spec-builder-colonial` S.
- **78** are on the style fronts.

On every one of the 63 sheets the one-pass reading in the rects' own order (along the face)
reaches the optimum COUNT. It does not follow that the order is immaterial: on **43 of the 63
sheets more than one set of that size exists**, so the order decides WHICH windows keep their
shutters, even where it cannot change how many.

How the optimum was found, so it can be re-run (the probe is not committed). A window refused for
an opening or for a corner cannot keep its leaves in any order, so it is out. Among the rest, two
windows whose leaves would overlap (on the same storey band, by more than 0.01 in, `_clearances`'
own thresholds) cannot both be hung. The largest set with no such pair was found exhaustively on
each sheet, from `elevation.opening_rects` on the face each sheet's frame states. The one-pass
count is the same probe on a copy of the tree with M3c applied, which withdraws a refused pair
before the next window is judged.

## Why it is not decided in code

Both readings are defensible, and they answer different questions.

- **Today's reading** says what the composition ASKED FOR and could not have. Every pair it
  refuses would overlap a pair the composition put there.
- **The one-pass reading** says what the drawing could carry. A pair it keeps overlaps nothing
  drawn.

A sheet reader is closer to the second question. The record's refusal reasons ("its leaves and the
next window's would lie over one another") are phrased in the first. Choosing is a ruling about
what the refusal MEANS, so `build/elevation.py` is not edited.

## What must be ruled

1. **Does a refused pair still stand in its neighbour's way?** If it does, today's 232 stands. If
   it does not, 150.
2. **If withdrawn, in what order, and which of equals?** The rects' own order reaches the optimum
   count on all 63 sheets measured. But on 43 of them several sets of that size exist, and the
   order picks one. A rule stated as "the largest set that can all be hung" is order-free about
   the count and still owes a tie-break: along the face, from the entrance outward, symmetry
   about the centre line, or another. That choice is architectural. A symmetric front that keeps
   its shutters on one side only is its own defect.
3. **Neither reading is the cause.** A pier narrower than two leaves is a placement that set two
   openings too close. Lucas's review of 27 Sep names exactly this: *"there's still no concept of
   how close windows can be to doors"*. A pier rule between openings is the next phase's work,
   planned but not yet written into `PLAN-OF-ACTION.md`. It addresses the cause and will move both
   counts. Rule this question with that in view: it decides how the symptom is REPORTED meanwhile,
   not whether the house is right.

## Ruled 29 September 2026 (Lucas, asked directly): withdraw, and prefer symmetry

Asked: *when a window's shutter pair is refused because it would overlap its neighbour's, should
that refused pair still block the next window?* Lucas chose **Withdraw, prefer symmetry**:

> A refused pair no longer blocks its neighbour. Among equally good sets, prefer one symmetric
> about the front's centre line, then work outward from the entrance, so a symmetric front never
> keeps shutters on one side only.

Questions 1 and 2 are answered.

- **Read, not ruled:** on a face with no seated entrance, the centre of composition is the face's
  own centre, the same reading the pier ruling uses.
- **Symmetry tolerance:** `axis.mirror`'s, so that there is one spelling.

Executed by WP-16.7, after the pier ruling re-seats the windows. The 232 and 150 above are
re-derived there on the new placement.
