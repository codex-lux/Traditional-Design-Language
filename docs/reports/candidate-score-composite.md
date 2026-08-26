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

**A fatal finding disqualifies a candidate**, carried *beside* the score rather than inside
it: `disqualified` is true, `disqualified_because` says so in words, every ordering puts it
last, and no score is a case for building it. The guarantee — that a disqualified plan never
outranks a clean one — lives in the sort's primary key, which is the fatal count, so the
score does not have to enforce it a second time.

This was first built the other way, withholding the score on a fatal, and **measuring it
killed the idea**: composed across eight briefs, five returned sets in which *every*
candidate carried a fatal (`cape-cod-colonial` and `greek-revival` among them — OQ 63 already
records them as styles that cannot clear the fault corpus under their own native diagram).
Every column read "—" and the four plans could not be told apart, which is strictly less than
the demerit total gave.

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

## Fidelity at 25, and the ranking that did change

**The commit that opened this work claimed the composite was "the old ranking made legible
rather than a different one." That claim was false, and the adversarial audit caught it.** The
two identity pins in `tests/test_composer.py` cover position 1 only. Below it, the returned
*set* moved on both shipped briefs: `family-georgian` came back with `tower-villa` and
`octagon-radial` (fit 2.0, both borrowed) in place of `side-hall-townhouse` (fit 3.6, native)
and `foursquare-quadrant`. **An octagon returned for a Tidewater Georgian brief is the exact
sentence WP-4.5's own `NATIVITY_W` comment uses to describe the bug it was written to fix.**

The composite cannot be made order-equivalent to the demerit total at any weighting, and a
sweep over fidelity from 18 to 60 confirmed it: `demerits` charges 1 a minor without limit,
while an axis charges half a room however many minors land on it. Nothing reconciles those.
So WP-4.5's ruling had to be preserved deliberately rather than inherited.

**The weight comes from a measurement, not from the answer it produces.** Across both briefs'
full pick windows, the spread of the whole non-fidelity subtotal between clean candidates is
**18.0 points on `family-georgian` and 22.0 on `bungalow-small`**. Fidelity's full swing is
its weight — so at 18 it could not span the field it exists to outweigh. At 25 it clears the
larger measured spread. The returned sets are now fit 7.0 / 7.0 / 3.6 / 2.0 and 7.0 / 3.6 /
3.6 — more native than the demerit total's own answer on both briefs, not merely different.

`tests/test_score.py::test_the_returned_set_is_native_dominated_not_merely_tidy` is the guard,
and it fails when a weight moves. Re-measure with the script in the audit rather than
re-pinning whatever the corpus next says.

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

**The weights were not tuned against anything except fidelity's.** Seven of the eight are
editorial, stated once in `SCORE_AXES` with the reasoning beside them, and never measured
against a set of plans a fluent reader ranked by hand. That is OQ 64. Fidelity's 25 is the
one measured weight, and it is measured against a *spread*, not against a preferred answer.

**No axis was added for the elevation.** `plan_check.py` folds `elevation.py`'s measurements
into the fault layer rather than emitting its own findings, so elevation quality is already
inside `solecisms` and giving it a second axis would score it twice.

**`demerits` was not deleted.** Removing it would break the one honest continuity between
this record and every report written before today.

## The adversarial audit, 26 August 2026

Four independent auditors were run over the diff — regressions and consumers, whether the new
tests could fail, second-order risk, and second occurrences of the same bug pattern. They
found more than the change did.

**The set regression above was the blocker.** Two more were close behind. `area` clamped only
its lower end while `schema/brief.schema.json` declared `area_tolerance` with no minimum, so a
schema-valid brief published **902.8 "out of 100"** in a 26px numeral; the schema now carries
bounds on six numeric fields and the ceiling is enforced at one point in `score_candidate`
rather than at eight. And `workbench/app/src/surfaces/BriefIntake.jsx` told users that **"93 of
132 styles have none"** — the pre-WP-4.5 figure, wrong by 90, contradicted by every other
record in the repo, shipped as reassurance to users hitting one of the three real cases.

**The test suite was audited by mutation and it failed.** Twenty deliberately wrong scorers
were run against the first `tests/test_score.py`; **thirteen survived** — including counting
unjudged faults as clear (the exact leak one test was *named* for, whose assertion turned out
to be an algebraic identity), scoring an unevaluated axis as a full pass, a minor finding
costing nothing, the rooms and connections axes measuring nothing at all, and swapping two
weights, which changes which plans the composer recommends. The suite was rewritten against
the mutants: **twelve of twelve now die.** One of them, the central ceiling clamp, could only
be made killable by *deleting* the redundant per-axis clamps — with both in place no test
could see the difference, and one enforcement point that is tested beats two that are not.

**The workbench app had no tests of any kind.** `workbench/app/src/candidateOrder.js` now
holds the pure ranking logic — the reasons-list join, the nativity fallback, the three
orderings and the disqualified-last rule — with `candidateOrder.test.mjs` beside it, ten cases,
six of six mutants killed. `npm test`, wired into both `build/check_all.py` (N/EV without node,
never a pass) and CI. Writing it exposed that CI's own **"Build app" step carried no
`working-directory`**, so it had been running `npm run build` at a repo root with no
`package.json` since the workbench shipped.

**A pre-existing determinism bug surfaced because calibration needs stable numbers and did not
get them.** The plan record took a *reference* to the parti's own `groupings` list and
`attach_garage()` appended to it — so one brief asking for a garage left five of twenty-one
partis declaring a garage grouping for every later brief in the process. Composing
`bungalow-small`, then `family-georgian`, then `bungalow-small` again moved a candidate's
demerits from 146.0 to 155.0. The workbench runs every compose job on one long-lived worker,
which is exactly where it bites. One `list()` fixes it; `tests/test_score.py` now pins both
that no parti is mutated and that one brief cannot change another's result.

**Second occurrences of the same pattern, found and fixed.** `geometry_report.score` is the
identical defect one layer down — a demerit total published as `score`, argmin-selected, with
its direction stated nowhere and the MCP docstring actively reinforcing the wrong reading
("an upper layout that would score *better*" means *lower*). The engine is untouched, because
`tests/test_solver.py` benchmarks that quantity; what it MEANS is now stated wherever it is
printed or published. Beyond it: 40 faults carry a two-sided `between` bound and the fault
corpus rendered only one edge, so a reader could not tell whether a value passed; the
proportion engine's `error` key was outside `RULE_KEYS`, so an unevaluable rule reached the
workbench as `null in` — a refusal rendered as a measurement; the privacy overlay divided by 6
where `privacy_rank` runs 1–5 and drew an unranked room exactly like the least private one;
and the elevation caption printed one style's fault coverage beneath every style's elevation.

**Deliberately not fixed.** `docs/reports/wp-5.2-the-workbench.md` still quotes a candidate
score of 472.0 on the old scale. Reports in this project are left as written; the scale it
belongs to is named here and in the changelog.

**And one defect the ranking change flushed out by moving a diagram into view.**
`tests/test_garage.py` asserts that a placed garage must record the grouping that placed it —
WP-4.3 made `garage-and-hyphen` the one attachment mechanism. Two partis, `five-part-palladian`
and `ranch-tripartite`, write a `garage` room into their own `rooms` list without declaring the
grouping, so `attach_garage()` sees the room already there and returns before it can record
anything: a garage that no grouping placed and no grouping governs. Neither had ever been
returned by the two shipped briefs, so the test had never seen them. Fidelity at 25 put
`five-part-palladian` into family-georgian's four and it failed on the first run. Both partis
now declare the grouping (its `attaches_to` already records their massings as canonical and
common, and both carry its primary room), and a new data-level test checks the class across all
twenty-one partis rather than across whichever ones a brief happens to rank. Declaring it
surfaced one honest warning that was previously invisible: `check_partis.py` now reports that
`ranch-tripartite`'s open-plan circulation is not among the values `garage-and-hyphen` expects.
Additive, errors 0 — the corpus saying something true that nothing had asked it before.
