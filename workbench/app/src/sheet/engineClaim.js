/* WHAT THE BENCH MAY CLAIM ABOUT THE ENGINE THAT DREW A SHEET, in one spelling (WP-13.2).

   Read from the record's own `geometry_report.solver` block and decided nowhere else in the
   app. Until this file the Plan Workbench's caption decided `proved` from `engine === 'cp-sat'`
   alone, inline in its JSX -- so a CP-SAT solve that ran out of budget and returned FEASIBLE (a
   placement found, optimality never established) was captioned "proved feasible". That is the
   bench half of the false certification Phase 13 names -- *a green PLACEMENT PROVED over a
   FEASIBLE truncation* -- and the walk that was meant to catch it matched a PHRASE the caption
   had stopped printing, so main's CI was red on a wording and green on nothing.

   THE RULE: a proof is claimed only where the solver's status begins with OPTIMAL. A FEASIBLE
   truncation is not a proof; a hill-climb is not a proof; a CP-SAT record with no status is not
   a proof (unjudged is not passed). Whether the OBJECTIVE ran is a separate fact carried beside
   it, because `OPTIMAL (hard-only)` proves the hard set and evaluates no compositional term.

   THE FACTS ARE READ, NOT DERIVED. `engine`, `status`, `objective` and `reason` are the solver's
   own words (`build/geometry.py` and `build/geometry_cp.py` write them). What this file adds is
   the VERDICT the caption prints, and it lives here rather than in the JSX so that every branch
   can be driven by `engineClaim.test.mjs` with a hand-built record, without a bundle, a browser
   or a 25 s solve. `e2e/walk.mjs` then holds the RENDERED caption to the API's own solver block
   on a live server, stating the same contract from the other side.

   Python prints the PLATE's own line from the same record (`build/disclosures.py::engine_line`,
   drawn by `build/render_plan.py`); one is Python and one is JavaScript, so the two are held
   together by the walk and by the gate (`tests/test_sheet_coherence.py`) rather than by import.
   `sheet/Sheet.jsx`'s plate note is the bench's own twin of that Python line and is NOT wired to
   this function here -- it belongs with the false-certification fix, and the walk's plate check
   holds it to the same contract regardless.

   No React, no DOM: a leaf, like `derive.js` and `overlayRules.js` beside it. */

/* The one discriminator. `OPTIMAL`, `OPTIMAL (hard-only) — kept …` and `OPTIMAL — kept polish
   …` all begin with the word; `FEASIBLE — kept polish from the heuristic hint` does not. */
export const PROVED_STATUS = /^OPTIMAL\b/;

export const VERDICTS = Object.freeze(['proved', 'not-proved', 'searched', 'unjudged']);

export function engineClaim(solver) {
  if (!solver || typeof solver !== 'object' || !solver.engine) {
    return { engine: null, cp: false, status: null, proved: false, objectiveRan: null,
      fellBack: false, reason: null, verdict: 'unjudged' };
  }
  const engine = String(solver.engine);
  const cp = engine === 'cp-sat';
  const status = typeof solver.status === 'string' && solver.status ? solver.status : null;
  const proved = cp && status !== null && PROVED_STATUS.test(status);
  // The hill-climb's score IS its objective, summed for every candidate it looked at; only
  // CP-SAT can leave the objective unevaluated (`disclosures.py::objective_not_run` says the
  // same and prints the plate's line for it).
  const objectiveRan = cp ? (solver.objective !== null && solver.objective !== undefined) : true;
  const reason = typeof solver.reason === 'string' && solver.reason ? solver.reason : null;
  // `requested` is the hill-climb asked for by name (a wall drag); anything else is `auto`
  // having tried the proof and not got one, which is the case worth saying out loud.
  const fellBack = !cp && reason !== null && reason !== 'requested';
  const verdict = cp ? (proved ? 'proved' : 'not-proved') : 'searched';
  return { engine, cp, status, proved, objectiveRan, fellBack, reason, verdict };
}

/* The status as the caption prints it: the solver's own status word, lower-cased, without the
   " — kept …" tail the prover appends. `OPTIMAL (hard-only) — kept hard-only phase A (best of 1
   hard-valid placements)` -> `optimal (hard-only)`. Null where there is none, so a caller prints
   its own "no status" rather than an empty string that reads as a field somebody forgot. */
export function statusHead(status) {
  if (typeof status !== 'string' || !status) return null;
  return status.split('—')[0].trim().toLowerCase() || null;
}
