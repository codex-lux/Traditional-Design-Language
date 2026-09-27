/* WHAT THE ASSISTANT IS TOLD ABOUT THE PAGE (WP-14.22, PRD tranche 2 §C.8).

   Until this, the pane sent a surface id, the bench plan, a three-key cut of the last
   evaluation and a candidate COUNT -- and nothing naming the record on screen, so a reader on
   `#/proportions/trim-classical` asking "why is the dado so low?" was described to the model as
   "looking at the proportions surface". And the server read `candidate_summaries`, a key no
   client produced, so the candidate set a reader was comparing never reached the prompt at all
   (`oq/the-assistant-is-blind-to-the-page`).

   Ruled 25 Sep 2026: the page's CITATION, and the model fetches the record itself with the tools
   it already has. So this file adds exactly two keys and changes none of the old ones:

     cite                  the page's own `citeFor(...)` -- the ONE inverse of `routeCite`, in
                           citations.js, read and never re-spelled here (a fourth spelling of the
                           citation grammar is the one thing this phase forbids). Absent where the
                           page names no record; the server writes its line only for a citation
                           its own validator accepts, so this file is not the guard and does not
                           try to be.
     candidate_summaries   one compact row per candidate in the session's set, under a stated
                           character budget, each carrying the index a `candidate:<index>`
                           citation names. A candidate's refusal is read through
                           `sheet/refusal.js::readRefusal`, the one reader of that body.

   Pure: no React, no DOM, nothing from node_modules; `railContext.test.mjs` drives it. */
import { citeFor } from '../citations.js';
import { readRefusal } from '../sheet/refusal.js';

/* The candidate rows ride in the prompt on every billed round, so they are budgeted: rows are
   added whole, in the set's order, while the JSON of the rows so far plus one separator each
   stays within this many characters. A row that would cross it is left out and so is every row
   after it, and `candidateSummaries` says how many.

   It is stated BELOW the server's own budget (`rail.CANDIDATE_BUDGET_CHARS`), which cuts by
   whole rows too, so a set this file sends whole reaches the prompt whole -- the server writes
   each row with compact separators, which is the length JSON.stringify measures here.
   `workbench/server/tests/test_rail_loop.py` reads this line and holds the two in that order. */
export const CANDIDATE_BUDGET_CHARS = 3000;

const num = (v) => (typeof v === 'number' && Number.isFinite(v) ? v : null);
const str = (v) => (typeof v === 'string' && v.trim() ? v : null);

/* The citation naming the record this place shows, or null. */
export function pageCite(place) {
  const p = place && typeof place === 'object' ? place : {};
  const c = citeFor(p.surface, p.selection, p.params);
  return typeof c === 'string' && c ? c : null;
}

/* One candidate as the prompt sees it. Only what the record states is written: a field the row
   does not carry is left out rather than filled, and a refusal is named only where the record
   states one (a row with no `refused` says nothing about whether the house may be drawn). */
export function candidateSummary(c, index) {
  const row = { candidate: index };
  if (!c || typeof c !== 'object') return row;
  if (str(c.parti)) row.parti = c.parti;
  if (str(c.parti_name)) row.name = c.parti_name;
  if (str(c.nativity)) row.nativity = c.nativity;
  if (num(c.score) !== null) row.score = c.score;
  const counts = c.counts && typeof c.counts === 'object' ? c.counts : null;
  if (counts) {
    for (const k of ['fatal', 'serious', 'minor']) if (num(counts[k]) !== null) row[k] = counts[k];
  }
  if (c.disqualified === true) row.disqualified = true;
  const refused = readRefusal(c.refused);
  if (refused) row.refused = { kind: refused.kind, facts: refused.facts };
  return row;
}

/* The set's rows under the budget: { rows, omitted }. */
export function candidateSummaries(candidates, budget = CANDIDATE_BUDGET_CHARS) {
  const list = Array.isArray(candidates) ? candidates : [];
  const rows = [];
  let used = 0;
  for (let i = 0; i < list.length; i += 1) {
    const row = candidateSummary(list[i], i);
    const size = JSON.stringify(row).length + 1;
    if (used + size > budget) break;
    rows.push(row);
    used += size;
  }
  return { rows, omitted: list.length - rows.length };
}

/* The whole `context` a turn posts. The four keys the pane sent before this package are built
   exactly as RailHost built them, so what an older server reads is unchanged; `cite` and
   `candidate_summaries` are added only where there is something to say. */
export function railContext({ surface, place, plan, lastEval, candidates } = {}) {
  const ctx = {
    surface,
    plan: plan || undefined,
    last_eval: lastEval?.check ? {
      counts: lastEval.check.counts,
      constraint_summary: lastEval.check.constraint_summary,
      fault_summary: lastEval.check.fault_summary,
    } : undefined,
    candidate_count: Array.isArray(candidates) ? candidates.length : undefined,
  };
  const cite = pageCite(place);
  if (cite) ctx.cite = cite;
  const { rows } = candidateSummaries(candidates);
  if (rows.length) ctx.candidate_summaries = rows;
  return ctx;
}
