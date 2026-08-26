# The candidate score: from a demerit total to a composite out of 100

*26 Aug 2026. Raised by Lucas from the workbench itself: "Clearly, the 82 is the highest
score, but then it goes to a 36 for second place, and then back up from 74 to a 78. The
100 fatal, 8 serious, 1 minor, right below the score, also doesn't seem to bear any
relationship to anything."*

## What was wrong

Three separate defects, and the screenshot showed all three at once.

**1. The number ran the wrong way.** `compose.py` published a DEMERIT TOTAL under the label
`score`: 100 a fatal, 8 a serious, 1 a minor, less 20 a point of style fidelity, and the
candidates were sorted ASCENDING. The workbench then set it in a 26px numeral under the
word SCORE. Every reader takes the biggest number for the winner; on that screenshot 82 was
the WORST of the four plans.

**2. The sequence was not the ranking.** The columns were sorted by the "native to the
style" chip, which reordered them while the ordinal in each column's corner was recomputed
from the display position. So a column numbered 1 was the most native, not the best plan,
and nothing on the surface said so. The heading said only "ranked". That is where 82, 36,
74, 78 came from: the score order was 36, 74, 78, 82 — ascending, best first — read through
a different sort.

**3. The line under the number was a legend, not arithmetic.** `100/fatal · 8/serious ·
1/minor − fidelity (7)` is the rulebook. It reads as a count of a hundred fatal findings,
it never showed this candidate's own sum, and the `(7)` was a fit value that was silently
multiplied by 20 before it entered the total.

There was a fourth defect underneath those, and it is the one that decided the fix. **The
total had no ceiling and its magnitude tracked corpus density rather than quality.** The
same formula gives 36 on a Richardsonian brief and 208 on `family-georgian`, because a
bigger house is simply checked more times — 27 rooms against 18. A figure like that is only
ever comparative, which is exactly what a big numeral labelled SCORE promises it is not.

## What replaced it

**A weighted composite out of 100, higher is better, where every axis is a SHARE of its own
denominator** — what came back clean out of what was actually checked. Size cancels: a
bigger house puts more rooms in the numerator and the same rooms in the denominator.

| axis | weight | denominator |
|---|---|---|
| solecisms | 22 | the faults the corpus could judge on this plan |
| rooms | 20 | every room, against its catalogue band, furniture, daylight, servicing |
| connections | 17 | every room, against adjacency, circulation, privacy, completeness |
| fidelity | 18 | `pick_partis` fit, out of a possible 7.0 |
| area | 8 | how far off target, against the brief's own tolerance |
| bedrooms | 4 | the bedrooms the brief asked for |
| canon | 6 | declared slots, groupings, evaluated constraints, massing affinity |
| buildability | 5 | the two footprint tests |

A room is spent by a serious finding, halved by a minor, left whole by an advisory or an
info. **The code layer is deliberately unscored** — `plan_check.py`'s own note calls code
findings advisory and jurisdictional, so scoring a house on them would score it against a
jurisdiction nobody named. It is the only layer mapped to `None`, and a test pins that it
is the only one.

**Unjudged is not passed, and here that has teeth.** An axis with no evidence neither scores
zero nor scores full marks: its weight is DROPPED and the total renormalised over the weight
that could be evaluated, with the dropped weight published as `score_weight_unevaluated`.
The workbench prints, in each column, the axes carrying checks the corpus could not judge —
*"129 solecisms, 17 canon could not be evaluated on this plan. They are outside the
fraction, not counted as passed."* On `family-georgian` that is 129 unjudged faults against
76 judged; folding them in as clear would have put every solecisms axis over 90%.

**A fatal finding forfeits the score rather than lowering it.** `score` is null,
`score_forfeit` says why, the axes are still measured, and the candidate sorts last. A fatal
is a thing that is wrong, not a thing that is worse, and averaging it into a share would let
a native diagram with a broken plan outscore a sound borrowed one — the exact failure
WP-4.5's `NATIVITY_W` comment argues against.

`demerits` stays on the record. It is a real quantity and earlier reports quote it. It ranks
nothing now.

## The order, and the three of them

The composer RETURNS fatal-free first and then by score. That key is a selection rule and it
is the one never traded away: a plan carrying a fatal never displaces a clean one from the
returned set, however native its diagram. WP-4.5's guarantee used to rest on a sort key
sitting in front of a weighted total that could, at fit 7.0, out-credit a fatal by 40 points;
it now rests on a key in front of a score a fatal forfeits outright.

How the returned set is then ORDERED FOR READING is a separate choice, and the workbench has
three: **highest score first** (the default), **native to the style**, **fatal first**. Each
one prints the sentence that says what it did, above the columns, because the ordinal in a
column's corner is a position in the current order and nothing more.

## What was found on the way

**`why_this_diagram` was rendered wrong, in both branches, in the shipped workbench.** It is
a LIST of reasons. React concatenates an array of strings with nothing between them, so the
native case read *"native to tidewater-georgianfour-over-four is a canonical massing for the
style"*. The borrowed case interpolated the array into a template literal, which joins on
commas AND repeats the "NOT native to this style" the surrounding span had just said in
gold. Both are visible in the screenshot that raised this report. Joined on "; " now, with
the duplicated clause stripped where the caller has already made that point.

**The nativity weight moved from a sum into a share, and the ranking it was raised to fix
still holds.** `NATIVITY_W = 20` is still what computes `demerits`; the composite reaches
the same conclusion through an 18-point fidelity axis. `tests/test_composer.py`'s two
identity pins — the centre-passage double pile first on `family-georgian`, the open linear
bungalow first on `bungalow-small` — pass unchanged, which is the evidence that the new
ranking is the old ranking made legible rather than a different one.

**The constraint layer barely evaluates anything, and now it is visible.** Every candidate
on `family-georgian` returns `constraint_summary {present: 1, clear: 0, unjudged: 4}`. Four
of five style constraints cannot be evaluated on a composed plan. That was always true and
was reported nowhere a reader would meet it; it now appears in the canon axis's unjudged
count on every column.

## What was deliberately not done

**The weights were not tuned against anything.** They are editorial, stated once in
`SCORE_AXES` with the reasoning beside them, and never measured against a set of plans a
fluent reader ranked by hand. That is OQ 64.

**No axis was added for the elevation.** `plan_check.py` folds `elevation.py`'s measurements
into the fault layer rather than emitting its own findings, so elevation quality is already
inside `solecisms` and giving it a second axis would score it twice.

**`demerits` was not deleted.** Removing it would break the one honest continuity between
this record and every report written before today.
