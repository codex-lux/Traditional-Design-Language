# oq/the-composers-footprint-is-not-the-placed-one — two derivations of one house's width, and the card publishes the one nobody builds

*Status: OPEN · Raised in: WP-13.7's verification pass, from a mutation that stayed green (17 September 2026)*

**`compose.footprint()` and `geometry.derive_footprint()` are two independent derivations of the
same house's bay count and width. They disagree on the composer's own default Georgian parti at
every lot measured, in both directions; the candidate card publishes the first, the house is placed
at the second, `score_candidate` RANKS on the first, and nothing in the tree compares them.**

Each has its own lot cap, written out separately:

    compose.footprint()          lot_mx = max(1, int(usable // bm));  mx = min(mx, lot_mx)
    geometry.derive_footprint()  lot_maxbay = int(for_main // bay);   maxbay = min(maxbay, max(1, lot_maxbay))
                                 ... and two more enforcement sites, at the growth step and growth_ceiling

`compose`'s divides the whole usable width by the bay module. `geometry`'s divides `for_main`,
which has already had the FLANK taken out of it — WP-11.6's layer 4 ruling, *"the lot cap is on the
BUILT EXTENT, elements only"*. So the moment a parti states a container the two are answering
different questions, and before that they were answering the same question with different
arithmetic.

## Measured

`briefs/family-georgian.json`, `revise=False`, `candidates=12`, `engine="heuristic"`, the plan
solved and its own `geometry_report.lot` read back:

| tree | lot | parti | compose card | placed | `flanking_ft` | `lot_capped` |
|---|---|---|---|---|---|---|
| `c39f3f8` before the container | 80 | `centre-passage-double-pile` | 6 bays, **54 ft** | 7 bays, **63 ft** | 0.0 | false |
| `c39f3f8` before the container | 100 | `centre-passage-double-pile` | 6 bays, **54 ft** | 7 bays, **63 ft** | 0.0 | false |
| `1392439` the container | 100 | `centre-passage-double-pile` | 6 bays, **54 ft** | 5 bays, **45 ft** | **41.0** | **true** |
| either | 80, 100 | `five-part-palladian` | 7 bays, 63 ft | 7 bays, 63 ft | 0.0 | false |

**The card says 54 ft in every row and the house is 63 ft, then 45 ft.** The container did not
create the disagreement — it reversed its sign and left the magnitude at 9 ft. `five-part-palladian`
agrees only because the composer writes it no `block` tag, so its flank is 0 and both readers reduce
to the same sum; `centre-passage-double-pile` is the one parti WP-13.5 gave a container to, which is
why it is the one that shows.

## Why nothing caught it

`tests/test_site.py`'s whole `TestComposerHonoursLotWidth` class reads `c["footprint"]`, which is
`compose.footprint()`'s dict. **It cannot reach `geometry`'s cap at all**, and that was measured
rather than reasoned: mutating `geometry.derive_footprint`'s `maxbay = min(maxbay, max(1,
lot_maxbay))` to a no-op left
`test_five_part_palladian_never_reaches_its_usual_seven_bays_on_this_lot` GREEN; so did
`lot_maxbay = 999`, which defeats all three of that function's enforcement sites at once. Mutating
`compose.footprint()`'s own `mx = min(mx, lot_mx)` turned it RED at once. The lot suite guards one
of the two spellings and the other is unguarded by anything.

**And it is not merely a card.** `compose.py:1729-1730` computes `fp2 = footprint(plan2, parti_rec)`
and hands it straight to `score_candidate`, so the composer RANKS partly on a width the placer will
not use.

## What has to be ruled

1. **Is `compose.footprint()` an ESTIMATE or a CLAIM?** If it is openly a pre-placement estimate,
   the defect is that nothing says so on the card, in the score, or in the tests that guard it — and
   `test_site.py`'s class is then asserting that the lot is honoured by an estimate rather than by a
   house.
2. **If it is a claim, which reader wins?** `geometry`'s knows about the flank and WP-11.6's ruling
   is explicit that the cap is on the built extent; that argues for deleting compose's arithmetic
   and reading the placement. The cost is that the composer would have to place before it can card,
   which is the infrastructure audit's own bound.
3. **Either way, what compares them?** A candidate whose card and whose placement disagree by 9 ft
   is the shape `openings.required_wall_ft` was lifted to remove, and this corpus's most-repeated
   defect.

## What must not happen

- **Do not reconcile them by editing one number to match the other.** They are different
  derivations, not a typo; that is `oq/a-grouping-rule-and-a-room-record-can-disagree`'s standing
  rule one layer up.
- **Do not delete `compose.footprint()`'s lot cap because geometry has one.** It is the only cap on
  the path the candidate card and `dropped_lot_infeasible` are built from, and the mutation above
  shows it is the one currently doing the work the site suite checks.
- **Do not read `five-part-palladian`'s agreement as evidence the readers agree.** It agrees because
  its flank is zero, which is the one case in which the two sums are identical by construction.
