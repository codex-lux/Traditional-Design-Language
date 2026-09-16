# oq/the-search-loses-the-entrance-front-on-a-multi-element-plan — the hill-climb draws the tagged Tidewater back to front

*Status: CLOSED · Raised in: WP-11.16, the record edit (15 September 2026) · Closed in: WP-11.17, the stated entrance front (15 September 2026)*

Tagging `plans/tidewater-georgian-careful.json`'s service programme into a west dependency cost
the SEARCH its entrance and cost the PROVER nothing. Measured on the same record, same commit:

| | `engine="heuristic"` | `engine="cp"` |
|---|---|---|
| entry porch | **(32.07, 31.51)** — the REAR wall | (31.0, 0.0) — the S front |
| flight goes to | `passage` | `porch` |
| kitchen centroid | 15.92 of a 37.24 ft depth — the FRONT half | 24.92 of 37.0 — the rear |
| pantry centroid | 15.92 — the front half | 25.36 — the rear |
| primary bath | 9 × 11 = 99 sf | 15 × 9 = 135 sf |
| fixtures refused | **1** (`primarybath`, shower with bench) | 0 |

`plan["context"]["entrance_faces"]` is `"S"` and unchanged. The house was drawn **back to front**:
the entrance on the rear wall, the service programme in front of the principal rooms.

## It was one defect, not four

The threshold layer, the composition acceptance clause, the axis census and the fixture packer
each reported it in their own vocabulary, and all four are downstream of the placement:

- `build/threshold.py` hands the flight to whichever room the entrance door is really in. Under
  the search that room was the `passage`, so `platform_is_the_room` was False and a platform was
  correctly drawn. **The layer was behaving.**
- `plan_check`'s axis census read `spine: off-centre` under the search and `on-centre` under CP.
- `primarybath` lost 53% of its area and its fourth fixture had nowhere to stand — an honest
  refusal with a full reason, not a silent drop.

## BOTH STATED CANDIDATES WERE WRONG, AND MEASURING THEM WAS THE WHOLE VALUE OF THIS ENTRY

The question named two mechanisms "worth measuring before anything is changed". Neither is it,
and neither would have been caught by reading:

1. *"`entrance_score` is not handed per-element `bounds`"* — true, and **irrelevant to this
   defect**. The porch stands in the MAIN block, whose element box IS `(0, 0, 45, 37.24)`, so a
   `bounds=` argument would change nothing for it. And `_touches_wall(rect, "S", W, H)` is
   `y <= tol`, which does not read `H` at all. (The missing `bounds=` is real and is named
   below, under a different symptom.)
2. *"a squarer pile makes the front and rear more nearly interchangeable"* — the effect is
   **categorical, not marginal**, and no charge that merely weighed the two faces could produce
   it.

## What it was: two independent causes, both measured over 250 candidates

### 1. The pool held no candidate with the porch on the front at all

`hyphen_anchors` returns `{'main': {'W': ['butlers']}}` once a second element exists, because the
butler's pantry doors into the back hall, which the tagging put in the hyphen. `flank_slice` then
lays the pantry as a full-depth strip at `(0, 0, 4.95, 37.24)` and hands the remaining six
main-block rooms a narrowed `40.05 × 37.24`, in which the porch never reaches `y = 0`:

| | porch on S | min porch y | winner y |
|---|---|---|---|
| tagged, as shipped | **0 / 250** | 21.32 | 31.51 |
| tagged, `hyphen_anchors → {}` | 60 / 250 | 0.00 | 27 |
| tags stripped | 159 / 250 | 0.00 | 0 |

The butler's pantry sat at `(0, 0, 4.95, 37.24)` in **250 of 250** candidates, so
`entrance_score` charged its 100 points on every one of them and **had nothing to prefer**.

### 2. And where a mixed pool does exist, the charge is never read

`_key` is `(viol, tot)` and `entrance_score` lives inside `tot`. Measured with cause 1
suppressed so that a mixed pool exists:

- front-porch candidates: n = 60, **minimum `viol` 3**
- back-porch candidates: n = 190, **minimum `viol` 1** ← wins on the first key
- ground score, front against back: **−92.3 points in favour of the front**, never read.

**One extra out-of-band room outranks a fatal-tier entrance violation, unconditionally**, which
is why suppressing cause 1 alone still left the winner at y = 27. It is not specific to
multi-element plans; on a one-rectangle plan it merely happens not to bite.

This contradicts `entrance_score`'s own docstring — *"weighted heavily enough … that no candidate
with the porch off the entrance wall can win against one that has it right"*. WP-11.8's
band-first ruling silently won.

## How it is closed: the front is STATED, so the key never adjudicates it

`build/geometry.py::entrance_anchors` names the one ground room that must stand on the entrance
front, and `_partial_flank` gives it a rectangle of its own area on that face before the
guillotine runs — `flank_slice`'s own move, and `courtyard_slice`'s before it. **Cause 2 is not
fixed and does not need to be**: every candidate now has the anchor on the entrance face, so the
band-first key is never asked about the entrance and WP-11.8 stands untouched.

Measured, `engine="heuristic"`, 250 candidates, on all six plans the selector reaches:

| plan | anchor | on the front | drawn | declared |
|---|---|---|---|---|
| `tidewater-georgian-careful` | `porch` | **250 / 250** (was 0) | 12.00 × 6.00 | 6 × 12 |
| `spec-builder-colonial` | `porch` | 250 / 250 (was 246) | 5.50 × 5.50 | 4 × 6 |
| `good-01-veranda-gallery-estate` | `entry-portico` | 250 / 250 (was 150) | 16.00 × 10.00 | 10 × 16 |
| `good-03-parlor-drawing-room-house` | `foyer` | **250 / 250** (was 118) | 9.00 × 12.00 | 9 × 12 |
| `good-04-rambling-porch-farmhouse` | `entry` | 250 / 250 (was 105) | 8.00 × 6.00 | 6 × 8 |
| `good-07-diamond-plan-house` | `foyer` | 250 / 250 (was 212) | 18.00 × 16.00 | 16 × 18 |

The Tidewater porch is drawn at exactly its declared rectangle, centred on its 45 ft front, and
`porch-nobody-can-sit-on` — a fault WP-7.4 cleared and the tagging re-broke — is cleared again.

## What this leaves open, named rather than netted off

**The two anchors genuinely compete, and three ways of having both were built, measured and
reverted.** The tagged main block carries an S entrance anchor and a W hyphen anchor; the caller
takes the first anchor that lays and the entrance is laid first, so the butler's pantry loses the
strip that had been pulling it onto the block's shared face. Measured on that record, doors the
placement cannot draw:

| | doors unplaced |
|---|---|
| hyphen anchor alone (the house drawn back to front) | **12** |
| neither anchor | 18 |
| entrance anchor alone (what ships) | **23** |

`_partial_flank`'s `P` and `R` slabs stand on the element's own W and E faces, so a slab receiving
the pantry could take the ordinary full-face `flank_slice`. None of the three routes to that was
worth shipping:

- **Letting `partition` decide is inert.** The pantry declares `exterior_walls: ["N"]`, so its
  x-bias is exactly 0, and the W slab held it in **0 of 841 draws**.
- **Adding the anchor's stated direction to that bias** did not move it either — `partition`
  ranks door connectivity above bias and the pantry's other door is to the dining room — and
  cost **6 serious findings**.
- **Putting it in that slab outright**, held out of the split with the slab's target area reduced
  by its own, works and is worse: a pantry laid as a full-face strip down a 16.5 ft slab is a
  worse room than one the guillotine places, and it took the score 672.3 → 753.5, serious
  55 → 62 and doors 23 → 24.

The corpus's own arbiter prefers the entrance across the trade — serious 60 → 55 and minor
111 → 105 on that record, against the one new fatal `unreachable: butlers`.
`oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it` is where a real fix
belongs.

**The Tidewater spine becomes COULD NOT EVALUATE under the search, and the cause is that a porch
is drawn inside the block.** The axis census read `spine: off-centre` before and reads
`could-not-evaluate` now: the passage is drawn directly behind its own porch — the sequence the
record describes — and therefore no longer spans S to N, so there is no spine to measure. Under
the proof it is still `on-centre`. The placer tiles the footprint exactly, so a porch on the S
wall takes that stretch of wall from whatever stands behind it; in a real Georgian house the
portico projects in FRONT of the block. That is the question
`oq/an-at-grade-appendage-is-drawn-and-not-judged` asks about the terrace, one room over.

**`good-02-portico-library-house` gets no anchor and that is the record, not a gap.** Its portico
and its foyer both declare the entrance wall, neither declares a door to the exterior, and the
two door into each other, so no door graph breaks the tie either. Choosing the portico by its
TYPE would be this reader inventing the answer the record declines to give.

**`entrance_score`'s second clause is now unsatisfiable on the plans the anchor serves.** It
charges 40 for the circulation room a threshold room opens into unless that room also touches the
entrance wall — and a passage standing directly behind its own porch cannot. On
`good-07-diamond-plan-house` the figure went **0 → 40** for exactly this reason, which is cause 2
acting on the clause the anchor does not state. Whether the clause should read *"reaches the
entrance front"* or *"is entered from the entrance front"* is a question about the rule, not
about this placement.

**`principal_and_service_score` measures wing rooms against the main block.** A dependency room
at x = −34 satisfies `_touches_wall(…, "W", …)` (`x <= 0.6`) and can satisfy N, S or E for no
placement whatever, so each service room is charged a flat 2.0 for "not at the rear" and the 3.0
for *service ON the front* **can never fire** — which is why service programme landing in the
front half goes unpunished. This is the missing `bounds=` of hypothesis 1, under its real
symptom. `geometry_cp._score` states the asymmetry deliberately (*"they measure the main
block"*), so changing it is its own package.

## A correction to WP-11.16's own report

`docs/reports/wp-11.16-the-record-edit.md` published *"severed entrance sequence | predicted |
**did not reproduce**"*. That was measured on CP alone and printed with no engine named. On the
search it reproduced exactly as WP-11.13 predicted. An unlabelled engine figure is a trap this
corpus already records — it cost two numbers at WP-11.8 — and this was the same shape. Corrected
in that report's §VIII rather than silently overwritten.

## And the cost WP-11.17 shipped was recovered at WP-11.18 (15 September 2026)

That package's one named cost was `unreachable: butlers` — the hyphen anchor pre-empted, its
doors undrawable, 12 → 23 on this record. **It is cleared, and the three recoveries this entry
records as measured-and-reverted were not the only routes.** `hyphen_anchors` had the
neighbouring element's whole rectangle in hand when it chose the face and returned the FACE
ALONE; `anchor_span` carries the extent now and `_partial_flank` positions the strip inside it,
with the entrance anchor CHAINED into a rest-rectangle rather than pre-empting the hyphen one.

The pantry is drawn **7.00 × 12.00 = 84 sf at (0.00, 12.62)** — its declared rectangle — over
**12.00 ft** of the hyphen's 9.62–27.62 band against the 3.50 ft `openings.required_wall_ft`
asks. Both its doors place. Corpus-wide: fatal 153 → 145, serious 712 → 707, unplaced doors
235 → 213, on the six plans this selector reaches and byte-identical on the other ten.

**The residue is four draws in 250**, not a door: porch-on-the-entrance-front reads 246/250 on
this record where WP-11.17 read 250/250, because a hosted anchor is best-effort. Two ways of
closing those four were built and reverted — an atomic chain restores the census and loses the
door (fatal 7 → 9, doors 20 → 32); a full-face strip fall-back restores it and the winner takes
a 222.8 sf veranda (serious 57 → 65).

**Cause 2 is untouched and this entry stays open on it.** `_key` is still `(viol, tot)` and still
never reads `entrance_score`; stating the front means the key is never asked.
`docs/reports/wp-11.18-the-anchor-that-kept-a-face.md`.

## Related

`oq/a-placement-rule-is-free-at-a-pool-the-server-cannot-afford` is the neighbouring question
about the search's pool. `oq/the-parti-dissolved-its-own-dependencies` is why the tagging was
worth making at all.
