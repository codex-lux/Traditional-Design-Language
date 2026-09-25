# oq/a-fault-gauge-has-no-extent-the-record-states — a gauge needs both ends of its scale, and a finding carries one number and a threshold

*Status: OPEN · Raised in: WP-14.16 (25 September 2026)*

**The question.** Tranche 2's list, in `PLAN-OF-ACTION.md` and in
`docs/reports/ux-first-principles-2026-09-24.md` §IX, names a *FaultGauge*: a small drawing per
fault showing where a house stands against the rule it breaks. The idea is the natural one for a
practitioner: a porch drawn 4 ft deep beside a line at 6 ft says more than the sentence does.

**Nothing in the record says where such a gauge would begin or end.** A finding carries its
evidence as numbers. `build/plan_check.py`'s constraint finding, for example, carries `value`,
`required`, `direction` and `threshold`. That is one measurement and one limit. The scale a gauge
draws them on also needs a floor and a ceiling, and neither exists in any record:

- no fault states a range of values the question makes sense over;
- no room record states the smallest or largest porch anybody has built;
- the image records hold no drawing of a fault (1,777 of 1,850 are still wanted, and the 73 sourced
  ones are the proportion plates).

So each end of the scale would be a number the app chose. That is the invented dimension this
corpus refuses.

## What each answer would change

1. **The fault record states its own scale.** An optional field on a fault test would give the
   range the question is asked over, sourced or `kind: editorial` like any other figure. That moves
   `schema/fault.schema.json`, 210 records at the author's discretion, and `build/check_faults.py`.
2. **A gauge drawn only between the two numbers the finding has.** The value and the threshold are
   drawn as a pair of ticks with the gap between them, and there is no scale. This is honest, but it
   is closer to a dimension string than a gauge.
3. **No gauge.** The finding's sentence stands alone, as it does today.

## What tranche 2 does meanwhile

It draws no gauge, per ruling default 5 in `docs/prd/phase-14-tranche-2.md` §0.3. The package is
deferred to tranche 3, and this question gates it.
