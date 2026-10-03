# oq/the-even-bay-fault-judges-the-drawn-parity-of-an-incomplete-front — the parity of what was drawn, on a front the record says is not the one drawn

*Status: OPEN · Raised in: WP-16.6, the pier and the alignment (1 October 2026)*

**`even-bay-front` (fatal) judges the upper storey's DRAWN opening count, and on an incomplete front
that count is a parity of which units the placer happened to refuse.** Its governing test is
`upper_floor_opening_count % 2` equals 1. R12 (ruled 29 Sep 2026) makes an incomplete front
unjudged for symmetry and alignment everywhere, and WP-16.1 executed it by withholding five figures
(`elevation._MIRROR_FIGURES` and `_ALIGNMENT_FIGURES`). The upper opening count is not among them,
so this fault is judged on a front the record says is not the one drawn.

**WP-16.6 moved it both ways on one record**, measured on the heuristic placement:

- the shipped, tagged `tidewater-georgian-careful`: the record declares 5 upper units on its S
  front. 4 were drawn before WP-16.6 (even: FATAL, "The Front With No Centre"); R6 refuses the
  primary chamber's second sash, whose axis below is the passage door's on the chamber's own wall,
  so 3 are drawn now (odd: clear). The front stays incomplete, 6 units undrawn where it was 5.
- the same record with its container stripped (`tests/test_element_awareness.py`'s fixture): 5
  were drawn (odd: clear); R6 refuses the third chamber's second sash, so 4 are drawn (even: FATAL).

Neither parity is the record's, which is 5 on both readings. A fatal that flips with the placer's
refusals, on a front the elevation itself calls incomplete, is the shape R12 was ruled against.

**The fault's own note calls it a symmetry fault:** *"Even is the fault on any style whose declared
symmetry class is strict-bilateral."* Whether R12 reaches it is not settled by R12's words, which
name symmetry and alignment and were executed as five figures. Extending a ruling by analogy is not
this corpus's to do.

**What is wanted.** Whether `upper_floor_opening_count` is withheld from the faults on an
incomplete front, as R12's five figures are -- so `even-bay-front` reads could-not-evaluate there
-- or is judged on the drawn count, as it is today. Measure before ruling: the fault convicts or
clears composed candidates too, so withholding it moves the composer's ranking (R13 ranks judged
fatals before unjudged ones), and `check_partis.py`'s standing red is this fault's band on the
side-hall front (`oq/a-side-hall-front-is-convicted-by-a-band-written-for-centred-fronts`).

*Taken as recommended under Lucas's standing instruction of 1 Oct 2026, never put: raised and left
open rather than executed inside WP-16.6, because executing it moves the composer's ranking and
`check_partis.py`'s known red for a reason that is not the pier or the alignment.*
