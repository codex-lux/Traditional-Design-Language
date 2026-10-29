# oq/a-shipped-record-files-a-wet-stack-as-structural — ruling 5 reached the partis and not the shipped plans

*Status: OPEN · Raised in: Phase 17, WP-17.1 (29 October 2026)*

**OPEN — Lucas ruled (29 Oct 2026, ruling 5) that a bath-over-wet-room claim is a SERVICING claim
(`wet_stack_with`, WP-11.6's split) and not a structural one, and seventeen such claims were moved in
thirteen partis. `plans/tidewater-georgian-careful.json` still files `primarybath stacks_over
butlers`, the same claim its parti now files as `wet_stack_with`, and it is left so on purpose.**

## Why it was not re-filed

`geometry.bias` reads `stacks_over` while the search SLICES the level (the shape of
`oq/a-withdrawn-claim-still-steers-the-placer`), so re-filing the claim moves the shipped
placement. Measured: with the record re-filed, the whole build's failures went from the known 20 to
108, almost all of them pins on the Tidewater placement (the hearths on their flues, the census, the
threshold, the drawn geometry). That is a record edit moving a shipped placement, which WP-11.13
ruled is its own package, and the plan of Phase 17 says the shipped records are not edited in it.

## What holds it meanwhile

`build/check_plans.py` reports the disagreement as `wet-stack-filed-as-structural`, a REPORTED kind
with its own ceiling of one (`WET_FILED_AS_STRUCTURAL_CEILING`), so a new plan filing such a claim
structurally fails the build; a plan that drops the claim altogether is a topology finding as before.

## What a ruling would choose between

1. **Re-file it in its own package**, re-deriving every pin on the Tidewater placement per plan.
2. **Leave it**, accepting that this one record asks the structural layer for 90% containment its
   own parti no longer claims.
