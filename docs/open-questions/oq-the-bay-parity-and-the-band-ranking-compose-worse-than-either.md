# oq/the-bay-parity-and-the-band-ranking-compose-worse-than-either — two ruled packages, and their composition is worse than either alone

*Status: OPEN · Raised in: the merge of the two Phase 11s (8 September 2026)*

**Main's WP-11.2 sizes the house from the massing's own bay count. This branch's WP-11.8 ranks
each room's own proportion band above the search's score. Each is an improvement on the tree it
was measured on. Together, on the two plans this corpus ships, they draw MORE rooms that cannot
take their own furniture than either does alone.**

## The measurement

Drawn furniture shortfalls over all sixteen plans, `engine="heuristic"`, deterministic, taken on
`git archive` checkouts of both parents and on the merged tree:

| | short axis | long axis |
|---|---|---|
| this branch (WP-11.8's band ranking) | 65 | **65** |
| main (WP-11.2's bay parity) | 86 | **74** |
| merged | 68 | **82** |

**Fourteen of the sixteen plans are byte-identical to this branch's figures.** The whole movement
is on the two SHIPPED plans, which are the only two whose footprint WP-11.2 resizes:

| plan | footprint before | footprint after | long-axis shortfalls: ours / main / merged |
|---|---|---|---|
| `spec-builder-colonial` | 40.0 × 38.44 | 50.0 × 30.75 | 6 / 10 / **18** |
| `tidewater-georgian-careful` | 60.0 × 40.08 | 63 × 38.17 | 6 / 8 / **11** |

## The mechanism, and why it is an interaction rather than an inheritance

`derive_footprint` is **area-neutral in the bay count** — CLAUDE.md carries that measurement
(2,405.0 sf at 4, 5, 6, 7, 8, 9 and 10 bays, identical to a tenth of a square foot), because `H`
is derived as `need / W`. So a house that gains a bay does not get bigger; it gets **wider and
shallower**. `spec-builder-colonial` goes from a 38.44 ft pile to a 30.75 ft one at the same
1,537 sf.

WP-11.8 then makes each room's own proportion band the FIRST key of the candidate acceptance, so
the search draws rooms **squarer**. A squarer room inside a shallower pile is a **shorter** room —
and the long axis is exactly what a dining table (12.33 ft across) and a kitchen island (13.0 ft)
need. The band ranking is doing what it was ruled to do, on a box whose depth the other package
removed.

Neither figure is a defect in its own package. The composition is where the cost appears, and it
appears only where both packages touch the same record.

## What must be ruled

1. **Is the bay parity's area-neutrality the right rule?** A five-bay Georgian that keeps its
   pile is a bigger house than a four-bay one, and the corpus's own massing prose
   (`four-over-four`'s "2-2.5 main") describes a DEPTH in ranges rather than an area to be
   redistributed. Growing the area with the bay count is a change to `derive_footprint` and to
   every plan in the corpus, and is not a merge's to make.
2. **Should a room's furniture set a floor on the pile?** `plan_check.furniture_shortfalls` knows
   the long-axis need for every room before any placement happens; `derive_footprint` does not
   read it. OQ 92 already ruled that furniture sets FLOORS and never sizes — this would be that
   ruling reaching the footprint rather than the room, and is the larger question.
3. **Which axis should the band ranking count when the pile is short?** The key counts
   `band_violations + under_band`. It does not know that the box it is ranking inside has become
   too shallow to hold a conforming room at the needed length, so it optimises the shape it can
   reach.

## What was NOT done, and why

**Neither package is undone and neither number is tuned.** Undoing a ruled package while
reconciling two branches would be a third change hidden inside a second one, and the numbers that
would justify it are exactly the numbers the merge disturbed. The two ceilings in
`tests/test_furniture_drawn.py` are re-baselined UPWARD, in public, with both parents' figures
beside them, so the cost is recorded rather than absorbed — and if either package later recovers
the ground, the ratchet's equality assertion says so.
