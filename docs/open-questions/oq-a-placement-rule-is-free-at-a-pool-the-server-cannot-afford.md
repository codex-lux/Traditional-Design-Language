# oq/a-placement-rule-is-free-at-a-pool-the-server-cannot-afford — the candidate count is a design input nobody has priced

*Status: OPEN · Raised in: WP-11.5, stacking as a rule (4 September 2026)*

## The measurement that raised it

WP-11.5 made a declared `stacks_over` claim a rule in the hill-climb rather than a 40-point
charge. Its cost turned out to be a pure function of the candidate pool, on one seed of
`spec-builder-colonial`:

| candidates | placement score | what the rule cost |
|---|---|---|
| **250 — the shipped default** | 651.5 | **70.5 points** |
| 500 | 605.9 | 24.9 |
| 1,000 | 543.1 | **nothing** |
| 2,000 | 508.9 | **nothing** |

At 1,000 the unconstrained winner already satisfies every declared claim, so the rule changes
nothing and costs nothing. At 250 it forces a materially worse candidate. **The rule is not
expensive; the pool is too thin to contain a good candidate that satisfies it.**

Broken claims tell the same story from the other side: 4 → 1 at 250 and 4 → 0 at 1,000 on the spec
plan, 8 → 2 and 3 → 0 on the Tidewater plan.

## Why this is a question rather than a patch

**Raising the pool is the obvious answer and it lands on the server's measured bound.** The
infrastructure audit found that editing a plan is the deployment's ceiling: one evaluate costs
338 ms of CPU at the shipped 250 candidates, and one person dragging a wall already consumes about
85% of the server's entire evaluate capacity. Throughput is flat across the whole concurrency
ladder because it is one core, fully serialised. **Four times the search is four times that
number**, and the workbench's wall drag calls `solve_heuristic` by name on every gesture.

**And this is not one rule's problem.** WP-7.4 found the same shape on a WEIGHT: its stacking term
looked inert over 250 candidates at one seed and moved 12 candidates past the winner over 2,000.
WP-11.3 refused a `centre_bay_score` after finding it *"paid at every weight and moving the winner
at none"* at 250 — and that its behaviour changed at 1,500. **Three packages have now measured a
term or a rule whose verdict depends on the pool, and the pool has never been the subject.**

## What must be ruled

1. **Is 250 a measured number or an inherited one?** Nothing in the tree records why it is 250.
   If it was chosen against a latency budget, that budget should be written down beside it.
2. **Should the pool differ by caller?** The wall drag needs a fast answer and is explicitly the
   one caller that asks for the hill-climb by name; a composed candidate set, a sheet render and a
   `revise` round are not interactive and could afford more. One constant serves four callers with
   different tolerances.
3. **Should a rule that cannot be satisfied in the pool raise the pool for that solve alone?**
   `geometry_report.stacking` already reports when no strict candidate exists. Retrying once at a
   larger pool when that happens is cheap in the common case and bounded in the rare one — but it
   makes solve time data-dependent, which the bench's 400 ms debounce was not designed for.
4. **What is the honest way to publish a measurement taken at a pool the product does not use?**
   This report states both 250 and 1,000 figures. A reader who quotes the 1,000 number as the
   shipped behaviour would be wrong, and nothing stops them.

## The trap

**Do not settle this by raising the constant and re-running the suites.** Several ratchets and
pinned counts in `tests/` are placement outcomes at 250 — `test_geometry.py`'s relaxation count,
`test_furniture_drawn.py`'s 86/69, the under-band pins — and every one of them would move at once,
which is a corpus-wide re-baseline dressed as a one-line change. The pool is a published input and
moving it is its own package.
