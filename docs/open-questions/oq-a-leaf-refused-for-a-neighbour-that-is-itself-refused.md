# oq/a-leaf-refused-for-a-neighbour-that-is-itself-refused — 232 of 255 leaved windows lose their shutters, and 82 of them only to leaves that are not drawn

*Status: CLOSED 1 October 2026 (ruled 29 September 2026; U5–U7 taken as recommended under a standing instruction; executed by WP-16.7; the one refusal left is a corner's, `oq/the-wall-at-the-corner-is-ruled-by-nothing`) · Raised in: WP-14.6's second audit (27 Sep 2026), re-derived by the audit of Phase 14 (27 Sep 2026)*

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

## Executed 1 October 2026 (WP-16.7)

`elevation._clearances` reads the ruling. One pass decides the face:

1. **What no choice can give is refused first, as before.** A leaf over another opening as it is
   drawn, or past the corner of the face. This is the question's own measurement method: such a
   window "cannot keep its leaves in any order, so it is out". Its leaves stand in nobody's way.
2. **Leaf against leaf is a choice.** `elevation._hang` hangs the largest set of the remaining
   windows whose leaves can all be hung.
3. **Ties go to symmetry, then outward.** Among equal sets it takes the one symmetric about the
   face's centre line (`axis.MIRROR_TOL_FT`, lifted out of `axis.mirror`'s default so there is one
   spelling). Then it takes the one hanging the windows nearest the centre of composition
   (`elevation.composition_centre`): the entrance where the face draws one, otherwise the face's
   centre, and a garage door is no entrance (U4's reading, the placer's own).
4. **A refusal names only neighbours whose leaves are hung.** Every contended window carries
   `shutters_decided_by`: `count`, `symmetry`, `outward` or `face-order`, the first key at which the set
   drawn beats the best set that would have done otherwise for it.

**Three further questions arose in the code. Each is taken as recommended under Lucas's standing
instruction of 1 October 2026, and none was put to him.**

- **U5, where no largest set is symmetric:** the set breaking the fewest mirror pairs is taken. A
  pair is two windows on one storey within the tolerance of each other's reflection, and it is
  broken where one hangs and the other does not. The ruling says "prefer one symmetric"; this is
  that preference graded, so a front that cannot be symmetric is made as nearly so as it can be.
  The alternative was to let the symmetry key fall silent and the outward key decide.
- **U6, where the ruled keys do not decide** (two windows mirrored about the centre and too close
  to hang both, at one distance from it): the order along the face, from its left as drawn,
  decides.
  - It is a key for determinism alone, which no ruling states.
  - Every window it decides says so in its refusal.
  - The sheet and the DXF print `SHUTTERS CHOSEN BY ORDER ALONG THE FACE ON n WINDOW(S)` naming
    the rooms, and census V27 holds that line to the record both ways.
- **U7, the bound:** each group of contending windows is searched whole up to
  `SHUTTER_GROUP_BOUND`, 16 windows. Past it the group's pairs are refused as composed, the rule
  before WP-16.7, under their own class (`bound`), which every surface says. No sheet in the
  corpus reaches it, and a driven test does.

**Read, not ruled, and stated in the code:**

- **A face with no width has no centre line.** The symmetry key is then not judged, and the
  windows it could have decided carry `shutters_symmetry_unjudged`, which the sheet says. Where
  no entrance is drawn either, there is no centre of composition, and the order decides, saying
  so.
- **The symmetric reading is the face's own centre line**, the main block's face the elevation
  draws.

### The figures, re-derived on WP-16.6's placement

On the census's 63 sheets that carry leaved windows, the population this question was measured
on:

| tree | leaved windows | refused as composed | one pass | refused by the record |
|---|---:|---:|---:|---:|
| this question's, 27 Sep (as published above) | 255 | 232 | 150 | 232 |
| `bb3c6de`, before WP-16.6 | 255 | 193 | 111 | 193 |
| WP-16.6, and WP-16.7 | 206 | 1 | 1 | 1 |

- **The one refusal left is a corner's**, on good-05's upper east face: a 60 in window 18 in from
  the corner, whose leaf would hang past it. It is refused in every set, and no tie-break decided
  anything on any sheet.
- **WP-16.6's pier floor moved both counts first**, as point 3 above expected. A wall of 1.0 x the
  wider window holds both neighbours' half-width leaves exactly.
- **What R7 does where pairs contend** was measured by laying it over the placement before WP-16.6
  (`bb3c6de` with this package's two changed modules), where 82 pairs contend.
  - It refuses 111 windows, against 193. So 82 windows keep leaves the old rule refused for a
    neighbour's leaves that were never drawn: 82, the figure this question measured between its
    two readings.
  - A tie-break decided on 43 sheets, as this question measured: `outward` for 162 contended
    windows and `symmetry` for 2. `face-order` decided none.
  - Symmetry held wherever it could. The contended windows fell into 39 groups of four, each two
    clashing pairs mirrored about the centre, and 4 lone pairs. All 39 groups of four were hung
    symmetrically. Their windows record `outward`, the key that chose among the symmetric sets,
    because a window records the first key at which the set drawn beats the best set that would
    have done otherwise for it.
  - An independent exhaustive count over the same clash graph, written for this check, agrees:
    111 refused, and 43 sheets with more than one largest set.
- Both columns fell by the same 39 between 27 Sep and `bb3c6de`, for causes WP-16.7 did not
  measure. The 82 the ruling decides are untouched by them.

`tests/shutter_sets.py` re-derives them. It is committed, where the question's own probe was not.

### What stays open

Nothing of this question. Its own third point stands: neither reading was the cause. WP-16.6's
pier floor addressed the cause, and moved both counts before this package moved either.
