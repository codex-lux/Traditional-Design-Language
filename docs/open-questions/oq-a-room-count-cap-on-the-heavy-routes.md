# oq/a-room-count-cap-on-the-heavy-routes — nothing bounds how many rooms a heavy route will solve, and the body cap is 2,000 times too loose to be the bound

*Status: OPEN · Raised in: the triage of 2 Sep 2026, from a paragraph an audit deferred*

**OPEN — every heavy route's cost scales with a number no layer bounds.** `schema/plan.schema.json`
carries no `maxItems` anywhere; `levels[].rooms` is a bare array. The 8 MB body cap is the only
ceiling above it, and it admits roughly **52,700 rooms** of the shape the corpus's own plans use.
The largest plan this project has ever needed is **25 rooms**.

## Measured

`build/geometry.py::solve_heuristic`, 250 candidates, a fresh plan id per call so `_SOLVE_CACHE`
is not what gets measured. Both distributions, because they differ and the difference decides
what a cap should count:

| rooms | one level (s) | two levels (s) | render (s) | body |
|---|---|---|---|---|
| ~25 (largest real plan) | 0.37 | 0.34 | 0.00 | 6.5 KB |
| 50 | 0.62 | 0.55 | 0.00 | — |
| 100 | 1.52 | 1.27 | 0.01 | — |
| 200 | 4.68 | 3.14 | 0.01 | — |
| 400 | 15.46 | 9.51 | 0.02 | — |
| 800 | 56.34 | 33.97 | 0.03 | 125.3 KB |

Doubling the rooms roughly triples the cost.

**Splitting the same rooms over two levels is CHEAPER, and that is a fact about the cap rather
than a curiosity.** The expensive term is an O(n^2) shared-segment scan run per level, so two
levels of 400 cost about half of one level of 800. A cap counting a plan's TOTAL rooms therefore
bounds the cheap case and the expensive case alike at one number, when the worst case is rooms
concentrated on a single level. Whatever site a ruling picks, the figure it counts should be the
LARGEST LEVEL's room count rather than the sum -- or the same cap admits twice the work depending
on how the author happened to distribute it. **800 rooms is 56 seconds of CPU on one request, from
a body at 1.5% of the cap** — and the heavy meter admits 60 such calls an hour per identity, which
is 56 minutes of a single core per hour from one caller who is inside every limit the deployment
has. The infrastructure audit measured that core as the whole of the deployment's evaluate capacity
(`docs/reports/infrastructure-audit.md`): one person editing a plan already consumes about 85% of
it at 338 ms a call.

The cost is in the placement, not the drawing. `build/geometry.py` runs an O(n²) shared-segment
scan inside the candidate loop, and the candidate loop is itself clamped only at 2,000. The label
fitter is no longer the term that matters — `MAX_WORDS` and `MAX_CHARS` closed that in the same
audit — but its comment is where this question was first written down, in its own words:

> *twelve words of a thousand characters cost 74 ms and twelve words of twenty thousand cost
> 1466 ms — per room, with room count unbounded by the schema, on one POST /api/drawings.*

That sentence has been in `build/render_plan.py` since the audit that wrote it. The room count is
still unbounded.

## What is bounded today, and what is not

Bounded: the body at 8 MB (`workbench/server/app.py`), the search width at 2,000 candidates
(`_candidates`), any integer a body supplies (`_clamp`), the label fitter's search, and the rate of
calls at 60/hour per identity on six routes (`workbench/server/limits.py`). **Not bounded: the
number of rooms**, on `POST /api/plan/evaluate`, `POST /api/drawings/{kind}` and
`POST /api/export/{fmt}`, each of which takes `body.plan` verbatim and solves it.

Every existing bound in this server caps the SEARCH and never the SUBJECT. That is a deliberate
rule, stated where the label fitter enforces it: *a name is drawn whole or not at all.* A room-count
cap is the first bound that would have to refuse a record rather than shorten what is done to it,
which is why it is a ruling and not a patch.

## Three places it could go, and they mean different things

1. **`maxItems` on `levels[].rooms` in `schema/plan.schema.json`.** A 900-room plan becomes an
   invalid record everywhere — the CLI, `plan_check`, the composer, the corpus's own fixtures — not
   merely a request the server declines. It is the strongest and the least reversible: it says the
   language cannot express such a house.
2. **A `_rooms(body)` guard beside `_candidates()` in `workbench/server/app.py`, returning 422 on
   the routes that take a plan.** A valid record the server declines to solve. This is the shape
   every existing clamp in that file takes, and the words of the paragraph that deferred the
   question point at it: *a room-count cap on the routes.*
3. **A per-consumer bound inside `build/geometry.py`,** in the manner of `MAX_WORDS` — solve what
   the budget allows and report the rest as unevaluated. It keeps the record valid and the route
   open, at the cost of a partial answer, and **unjudged is not passed**: it would have to report
   COULD NOT EVALUATE for the rooms it did not place, never a placement that silently omits them.

**The revision loop has since landed on `main` (PR #19), and this paragraph used to say it was
on another branch.** That is corrected here rather than left, because "until X lands" stops being
true the moment X lands. The loop adds a further pass over the same submitted body — `critique()`
is quadratic in plan size through `answering()`'s deep copy per matching move per finding, measured
at 90 s on an 800-room record by that package's own audit — so it MULTIPLIES the cost tabled above
rather than changing its shape, and it does so on the same unbounded body. **The table above was
taken without it and is now a floor rather than the worst case.** Anyone ruling on this should
re-measure with the loop in the path; the argument for a cap is strictly stronger than when it was
written, and the site question is unchanged.

## The question for a ruling

**Which site, and what number?** A cap has to be justified against the largest plan the corpus has
ever legitimately held, which is 25 rooms, and against the largest a person might plausibly author,
which nobody has measured because nobody has tried.

**What I would do, stated so the ruling has something to push against:** site 2, at 250 rooms. It
refuses at ten times the largest real plan and one-tenth of where the cost becomes absurd; it keeps
the schema describing what a house can be rather than what a server will do about it, which is the
distinction the model has held everywhere else; and it is the only one of the three that can be
changed by a deployment without invalidating a record anybody already has. Site 1 is tempting
because it is one line, and it is the one that cannot be walked back — a corpus fixture that
exceeds it stops validating everywhere, and this project has already learned what a schema change
costs when the thing it forbids turns out to be legitimate.

**What this question does NOT settle:** whether the 250-candidate default and the 2,000 cap are
themselves right, and whether the per-identity meter is the right ceiling for the deployment. Both
are live elsewhere and neither is this.
