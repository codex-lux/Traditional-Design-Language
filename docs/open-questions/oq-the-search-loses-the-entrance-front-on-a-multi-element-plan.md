# oq/the-search-loses-the-entrance-front-on-a-multi-element-plan — the hill-climb draws the tagged Tidewater back to front

*Status: OPEN · Raised in: WP-11.16, the record edit (15 September 2026)*

Tagging `plans/tidewater-georgian-careful.json`'s service programme into a west dependency costs
the SEARCH its entrance and costs the PROVER nothing. Measured on the same record, same commit:

| | `engine="heuristic"` | `engine="cp"` |
|---|---|---|
| entry porch | **(32.07, 31.51)** — the REAR wall | (31.0, 0.0) — the S front |
| flight goes to | `passage` | `porch` |
| kitchen centroid | 15.92 of a 37.24 ft depth — the FRONT half | 24.92 of 37.0 — the rear |
| pantry centroid | 15.92 — the front half | 25.36 — the rear |
| primary bath | 9 × 11 = 99 sf | 15 × 9 = 135 sf |
| fixtures refused | **1** (`primarybath`, shower with bench) | 0 |

`plan["context"]["entrance_faces"]` is `"S"` and unchanged. The house is drawn **back to front**:
the entrance on the rear wall, the service programme in front of the principal rooms.

## It is one defect, not four

The threshold layer, the composition acceptance clause, the axis census and the fixture packer
each report it in their own vocabulary, and all four are downstream of the placement:

- `build/threshold.py` hands the flight to whichever room the entrance door is really in. Under
  the search that room is the `passage`, so `platform_is_the_room` is False and a platform is
  correctly drawn. **The layer is behaving.**
- `plan_check`'s axis census reads `spine: off-centre` under the search and `on-centre` under CP.
- `primarybath` loses 53% of its area and its fourth fixture has nowhere to stand — an honest
  refusal with a full reason, not a silent drop.

## What is NOT established

**Why.** The search's `entrance_score` still charges the entrance front, and the same record with
its tags stripped places the porch at (35.51, 0) correctly. So it is the presence of a second
massing element that changes which candidate wins, and the mechanism has not been read. Two
candidates worth measuring before anything is changed:

1. `exterior_score` is handed per-element `bounds` (WP-11.6 layer 4). If `entrance_score` is not,
   the two are scoring against different rectangles and the entrance term is being outweighed
   rather than dropped.
2. `derive_footprint` sizes the main block from the rooms that stay in it, so the block is
   45 × 37.24 instead of 63 × 38.17 — the pile is squarer, and a squarer pile makes the front and
   rear faces more nearly interchangeable to a term that charges depth.

**Whether it is worth fixing rather than accepting.** The sheet is drawn on `auto`, which takes
the proof, so no shipped drawing is wrong today. What is wrong is that the two engines disagree
about which way the house faces, and this corpus's own rule is that the search and the arbiter
must not convict and acquit the same house.

## Why it was not fixed in WP-11.16

Ruled 15 September 2026: **name it, do not fix it.** Repairing the search is a placement change
with a corpus-wide blast radius — every ratchet and both corpus digests would be re-derived
against a moving base — and WP-11.16's subject is a record edit. A package that does two things
can only be reasoned about as one.

**Do not repair it by re-pointing the guards at the broken sequence.** Six tests assert that the
entrance sequence is drawn right; re-pointing them at `passage` and `platform_is_the_room is
False` converts them into tests asserting the defect, at which point a green suite is evidence
*for* it. They run on the proving engine instead, and the search's failure is pinned by name in
`tests/test_threshold_pass.py::TestTheStoop::test_THE_SEARCH_LOSES_THE_ENTRANCE_AND_THAT_IS_A_MEASURED_COST`,
`tests/test_composition.py` and `tests/test_axis.py` — each with an assertion message saying that
if it ever reads the correct value, this question has been answered and should be closed rather
than the line deleted.

## A correction to WP-11.16's own report

`docs/reports/wp-11.16-the-record-edit.md` published *"severed entrance sequence | predicted |
**did not reproduce**"*. That was measured on CP alone and printed with no engine named. On the
search it reproduces exactly as WP-11.13 predicted. An unlabelled engine figure is a trap this
corpus already records — it cost two numbers at WP-11.8 — and this is the same shape.

## Related

`oq/a-placement-rule-is-free-at-a-pool-the-server-cannot-afford` is the neighbouring question
about the search's pool. `oq/the-parti-dissolved-its-own-dependencies` is why the tagging was
worth making at all.
