# oq/a-shipped-plan-needs-thirty-seconds-and-the-budget-is-twenty-five — the proof is there and the clock is not

*Status: CLOSED 5 September 2026 (WP-11.8) — the budget is split, batch from interactive · Raised in: WP-11.7, the shape band and the ranked ladder (5 September 2026)*

**OPEN — with the room proportion band held hard, `plans/spec-builder-colonial.json` solves to
OPTIMAL in 29.6 s. `geometry.solve()`'s budget is 25 s. So a shipped reference plan that CP-SAT
used to prove now falls back to the heuristic, by five seconds.**

## The measurement

Both figures on the same machine, all wall pins released, with the heuristic hint:

| plan | status | wall clock | budget |
|---|---|---|---|
| `tidewater-georgian-careful` | OPTIMAL | **11.3 s** | 25 s — fits |
| `spec-builder-colonial` | OPTIMAL | **29.6 s** | 25 s — **does not fit** |

It is not infeasibility. Given 90 s the model is OPTIMAL; given 25 s it returns UNKNOWN, the
round loop exhausts, and `geometry.solve()` labels the drawing *"heuristic (least-bad,
labelled)"* — which the plate has printed since WP-6.4, so the sheet does not lie about it.

What that costs on the shipped record, measured before and after:

| `spec-builder-colonial` | fatal | serious | minor |
|---|---|---|---|
| CP-SAT, before WP-11.7 | 4 | 132 | 87 |
| heuristic fallback, after | 10 | 97 | 90 |

Not a clean loss — six more fatal findings, thirty-five fewer serious — but the plan loses its
PROOF, and a proof is the thing the CP engine exists to give.

## Why the model got slower, stated so it is not re-litigated

The band is a hard, downgradable pin per room, and the first infeasible round releases all the
wall pins (WP-11.7's ruling). Wall pins are strong propagators — each one fixes a coordinate to
a boundary — so releasing 13 of them and adding 21 ratio constraints trades a heavily-pruned
search for a much larger one. The Tidewater plan absorbs that and this one does not.

**The obvious speed-up was tried and is slower.** `max(w,h) <= c * min(w,h)` is exactly
`w <= c*h AND h <= c*w`, which needs no `AddMaxEquality`/`AddMinEquality` pair and reads as
strictly cheaper. Measured: spec-builder 29.6 → **48.2** s, tidewater 11.3 → **20.4** s. CP-SAT's
max/min propagators are stronger here than two reified linear constraints, by about 1.7x. The
comment above the constraint carries those numbers so the rewrite is not attempted a third time.

## What must be ruled

1. **Raise the default budget, and by how much?** `PLAN-OF-ACTION.md`'s own WP-11.7 text
   anticipates exactly this — *"raise the budget on the reference plans or state the fallback"*.
   WP-11.7 stated the fallback, because the budget is not free: `workbench/server`'s
   `/api/plan/evaluate` is the route the infrastructure audit measured as **the whole server's
   bound**, and its worst case is a CP solve that runs the budget out. 25 → 35 s would cover this
   plan with margin and would lengthen that worst case by 40%.
2. **Or a budget that is not one number?** A per-plan budget scaled by room count (21 rooms here
   against 25 on the Tidewater) is defensible and is a new mechanism, with its own failure mode:
   a plan that is slow for a reason other than size gets no more time than one that is not.
3. **Or should the bench and the batch differ?** `check_all.py`, `corpus.drawing()` and the CLI
   have no latency budget worth the name; the interactive route does. A batch budget and an
   interactive budget is the honest shape if the answer to (1) is "not on the bench".

Until it is ruled: **the fallback is stated, on the plate and in `geometry_report.solver`, and
one of the two shipped reference plans is drawn by the search rather than the proof.**

---

## Ruled 5 September 2026 (WP-11.8): split it — a batch budget and an interactive one

Option 3 of the four above. `build/geometry.py` states two:

```python
BUDGET_BATCH_S = 40.0          # the default `solve()` carries
BUDGET_INTERACTIVE_S = 25.0    # passed BY NAME by the two routes a person waits on
```

`check_all.py`, `corpus.drawing()`, the CLI and the reference plans take the default, where a
proof is worth waiting for. `workbench/server/evaluate.py` and `mcp_server/core.py`'s
`place_plan` pass the interactive one by name — the route the infrastructure audit measured as
the whole server's bound, behind a 400 ms debounce, where a longer worst case is a worse
instrument.

**Measured the moment it landed: `plans/spec-builder-colonial.json` is CP-solved again** —
`FEASIBLE — kept polish from the heuristic hint`, in 40.7 s, with **0 rooms outside their own
band**. Both shipped reference plans are drawn by the proof again.

Neither of the two refused options is dead: a per-plan budget scaled by room count (option 4)
remains the answer if a plan is ever slow for a reason other than size, and raising the
interactive number (option 1) remains available if the audit's measurement of the evaluate route
ever changes. What is settled is that ONE number may not serve both callers.
