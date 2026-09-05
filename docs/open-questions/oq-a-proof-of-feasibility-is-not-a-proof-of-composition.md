# oq/a-proof-of-feasibility-is-not-a-proof-of-composition — the bench draws the proof, and on this plan the proof carries no composition at all

*Status: RULED 4 Sep 2026 · Raised in: `docs/reports/tidewater-layout-diagnosis-2026-09-04.md` J2 (4 Sep 2026)*

**Lucas's ruling, 4 September 2026: WP-6.3's principle does not transfer.** A CP-SAT placement
outranks a hill-climb placement on FEASIBILITY and on nothing else. Where the compositional
objective did not run, the bench draws both and labels both, and the plate says which it drew and
why.

## The measurement the ruling is taken on

`build/geometry.py --engine cp` on `plans/tidewater-georgian-careful.json`, 4 Sep 2026, default
25 s budget, `geometry_report.solver`:

```
status:    OPTIMAL (hard-only) — kept hard-only phase A (best of 1 hard-valid placements)
objective: null
attempts:  6b r0 INFEASIBLE · r1 INFEASIBLE · r2 INFEASIBLE · r3 UNKNOWN · r3+ OPTIMAL ·
           restore backhall N OPTIMAL · restore backhall S INFEASIBLE · restore butlers N UNKNOWN ·
           restore dining N UNKNOWN · restore dining W UNKNOWN · polish-h UNKNOWN
```

Phase A proves the hard set. Phase B — which carries every compositional term the corpus has, the
100-point portico-inside charge among them — timed out. So the drawn house is whatever CP-SAT
reached first. The heuristic, which runs all of those terms, scores **712.6** against the proof's
**835.0** on the corpus's own demerit total, and is the better house in every tier of that
report's Part III.

**And the hard set it proved is not the record.** Sixteen declared exterior walls were set aside to
reach feasibility, both ends of the centre passage among them. `docs/reports/wp-6.3-geometry-truth.md`
established that a reader must be able to tell a proof from a search; this entry establishes the
sharper thing, that a reader must be able to tell WHAT was proved.

## BUILT BY WP-11.8 (5 Sep 2026), and the case moved to the other plan

**The ruling was taken on `tidewater-georgian-careful` and on this machine that plan no longer
reaches CP at all** — `auto` spends its 25 s and falls back to the hill-climb (`fallback: budget`).
The case is live on **`spec-builder-colonial`** instead: `cp-sat`, `OPTIMAL (hard-only)`,
**`objective: null`**, five declared exterior walls set aside. Which plan demonstrates a
budget-dependent defect is itself budget-dependent, and quoting the Tidewater run as the live
example would now be wrong.

**AND THE RULING'S "with its demerit score" NEEDED A SECOND NUMBER.** Measured on that plan: the
search scores **592.3** against the proof's **789.3** — 197 points better — and buys it by breaking
**sixteen** declared facts the proof holds (0 against 16, judged against the same downgrade list,
because a heuristic record carries none of its own). The score alone reads as "the search is the
better house"; it is the cheaper one. `hard_fact_violations`' own docstring already said so. Both
numbers travel together in `geometry_report.solver.alternative` and no surface may print one
without the other — which is this ruling's own intent, since telling a reader that they are
choosing a better composition over a proved feasibility requires both halves of the trade.

Built: `geometry._offer_the_alternative` (the CP branch only, and only where the objective is
null), `disclosures.alternative_offered` (the plate line, immediately after `objective_not_run`
because it is the second half of one disclosure), `corpus._placed`'s `solver.drawn_by` with an
`input_digest` taken BEFORE the solve — finding J6 — and `PlanWorkbench.jsx`, which said
*"proved, not searched"* over exactly this placement and says **proved feasible** now.
Report: `docs/reports/wp-11.8-the-bench-chooses-and-says-which.md`.

## The ruling's two halves

**1. Draw both, label both, where the objective did not run.** `workbench/server/corpus.py::_placed`
records which placement it drew and why in `geometry_report.solver`; the bench offers the other
with its demerit score beside it. A reader choosing the search over the proof is choosing a better
composition over a proved feasibility and should be told that is the choice.

**2. `objective: null` is a disclosure, not an internal.** `build/render_plan.py`'s banner says
FIRST FEASIBLE PLACEMENT — THE COMPOSITIONAL OBJECTIVE DID NOT RUN, and the engine line names how
many of the record's declared exterior walls survived. That is **WP-11.1** and needs no ruling; it
shipped first for that reason.

## What is NOT ruled, and is the interesting half

**Whether the budget should simply be larger.** 26 s of a 25 s default, three infeasible rounds and
five restore attempts before phase B gets what is left. A budget that reliably reaches phase B on a
twenty-five-room plan may cost a minute, and the infrastructure audit measured this server's whole
evaluate capacity as one core. The trade is real and is not made here: it is cheaper to fix the
CONTAINER (**WP-11.6**), after which the record is feasible without downgrades and phase A stops
consuming the budget proving that a five-part house is not a box.

**Nor is the deeper question**: whether a placement that had to set aside sixteen declared facts
should be drawn at all, rather than refused with the conflict named. `geometry_cp.py` already
refuses a multi-element plan outright rather than flattening it; the same discipline applied here
would refuse to draw a house whose passage cannot reach its own front door. That is a bigger
ruling, it would leave the bench with nothing to draw for this plan until WP-11.6 lands, and it is
recorded here rather than taken.
