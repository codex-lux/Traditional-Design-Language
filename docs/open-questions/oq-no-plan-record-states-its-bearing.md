# oq/no-plan-record-states-its-bearing — the compass rule is executed under an assumption on 16 of 16 plans

*Status: OPEN · Raised in: WP-11.9, executing the compass rules the room records already state (6 September 2026)*

**Plan-N is true-N unless a bearing says otherwise, and on every plan record in this tree nothing
says otherwise.** Ruled by Lucas on 5 September 2026, with the cost stated when it was taken: the
checker must print the assumption in every finding it makes, not merely hold it. That is built —
`build/compass.py::assumption` — and `build/plan_check.py` prints it on all 63 aspect findings the
corpus produces. The question is what remains after that.

| | records |
|---|---|
| state `site.street_bearing_deg` | **0** of 16 |
| judged under the assumption | **16** of 16 |
| aspect findings carrying the assumption sentence | 63 of 63 |

The schema has carried `site.street_bearing_deg` since WP-2.4, described as *"Compass bearing
(0 = north, clockwise) of the street the principal front faces"*. Nothing has ever written one.
`render_plan.py` has printed **NORTH IS UP** on the plate since the same package and prints the
bearing beside it where a record states one, which is where the convention came from; the ruling
made it a rule.

## What is actually uncertain

Not whether the convention is right — it is ruled, and it is the only convention a drawing with a
north arrow can honestly have. What is open is **what a finding under it is worth**, and there are
two readings and no measurement to separate them:

1. **The reading that makes the 63 real.** A window's `wall` is authored. An author who wrote `S`
   wrote south, the plate says north is up, and a south library is a south library. On this
   reading the 63 findings are 63 true statements about the records as written.
2. **The reading that makes them soft.** The reference plans were authored between WP-0.1 and
   WP-5.13, years before any layer read a compass, and their window walls were chosen to make a
   drawing legible rather than to state an aspect. On this reading the check is convicting the
   records of a fact their authors never meant to assert — the shape `plan.exterior_walls` is
   already recorded as having (*"aspirations, not rectangle edges"*), one field over.

**The two readings are not distinguishable from inside the corpus**, because nothing anywhere
records what a window wall was authored FOR. Both are consistent with every byte in the tree.

## Why it is not closed by writing a bearing into the sixteen records

Because that is authoring, and it would author the answer. A bearing is a fact about a SITE, and
fifteen of these records have no site: they are type specimens, not houses on lots. Writing
`street_bearing_deg: 180` into `good-03` to make its parlour come out right is choosing the number
that clears the finding, which is the move `check_grouping_rules.py`'s prose meter exists to
refuse, in a new place.

## What a ruling has to decide

- Whether an aspect finding on a record with no stated bearing is a finding at all, or an
  `info` that becomes a finding only once a bearing is stated. (**Beware the flattening**: an
  `info` on sixteen records is close to invisible, which is the argument
  `oq/fifteen-of-sixteen-plans-name-no-parti` already makes about its own severity.)
- Whether `context.entrance_faces` — which 0 of 16 plan records state either, all of them taking
  `axis.DEFAULT_FRONT` of S — should be required before the aspect layer speaks at all. It is
  already required before a stated BEARING is honoured: `plan_north` refuses to rotate a plan
  whose front it does not know, because taking the S default there would silently turn a real
  house by whatever the difference happened to be.
- Whether a brief may state a bearing that the composer then writes onto the plan it makes, which
  is the only route by which a generated house would ever carry one.

## What must not be done to close it

- **Do not default a bearing.** Zero is not a measured north; it is the absence of a measurement,
  and the assumption sentence is what keeps those two apart.
- **Do not soften the reading by widening `SECTOR_TOL_DEG`.** At 22.5 degrees it decides nothing
  on an unrotated plan — every face lands exactly on a cardinal — so widening it to reduce the
  count would be tuning an instrument that is not the cause.
- **Do not read the count as a verdict on the reference plans' authors.** It is a measure of how
  long the corpus stated sixty compass rules with nothing reading one.
