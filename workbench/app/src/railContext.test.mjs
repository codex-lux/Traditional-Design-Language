/* WHAT THE ASSISTANT IS SENT ABOUT THE PAGE (WP-14.22, PRD tranche 2 §C.8).

   `rail/railContext.js` builds the `context` a turn posts. Three properties are held here:

     1. the citation is the page's own `citeFor(...)` -- the same answer the router's inverse
        gives, for every place `routeCite` can reach -- and it is ABSENT where the page names no
        record, never an empty string or a guess;
     2. the candidate set arrives as whole rows under the stated budget, each carrying the index
        a `candidate:<index>` citation names, with a refusal read through the one reader of it;
     3. the four keys the pane sent before this package are built exactly as they were, so an
        older server reads what it always read.

   The server half -- which of these reach the prompt, and only a citation its own validator
   accepts -- is `workbench/server/tests/test_rail_loop.py`. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { citeFor, routeCite } from './citations.js';
import { railContext, pageCite, candidateSummaries, candidateSummary,
  CANDIDATE_BUDGET_CHARS } from './rail/railContext.js';

const PLACES = [
  { surface: 'proportions', selection: { pack: 'trim-classical' }, params: {} },
  { surface: 'faults', selection: { fault: 'porch-too-shallow-to-inhabit' }, params: {} },
  { surface: 'style', selection: { style: 'tidewater-georgian', section: 'rules' }, params: {} },
  { surface: 'style', selection: { style: 'tidewater-georgian', section: 'kit', slot: 'cornice' }, params: {} },
  { surface: 'glossary', selection: { term: 'assistant' }, params: {} },
  { surface: 'brief', selection: {}, params: { example: 'family-georgian' } },
];

test('the cite is the page\'s own citeFor, and it routes back to the page', () => {
  for (const place of PLACES) {
    const want = citeFor(place.surface, place.selection, place.params);
    assert.ok(want, `the premise: ${place.surface} names a record here`);
    assert.equal(pageCite(place), want);
    const ctx = railContext({ surface: place.surface, place });
    assert.equal(ctx.cite, want, `${place.surface}: the context names the record on screen`);
    // The identity the router holds for every kind: the cite sent is one that opens this page.
    assert.equal(routeCite(ctx.cite).surface, place.surface);
  }
});

test('a page naming no record sends no cite key at all', () => {
  for (const place of [
    { surface: 'proportions', selection: {}, params: {} },
    { surface: 'workbench', selection: {}, params: {} },
    { surface: 'overview', selection: {}, params: {} },
    undefined,
  ]) {
    const ctx = railContext({ surface: place?.surface, place });
    assert.equal(Object.prototype.hasOwnProperty.call(ctx, 'cite'), false,
      `${place?.surface}: no cite, and not an empty one`);
    assert.equal(pageCite(place), null);
  }
});

test('the keys the pane always sent are built exactly as before', () => {
  const plan = { id: 'p', levels: [] };
  const lastEval = { check: { counts: { fatal: 1 }, constraint_summary: { a: 1 },
    fault_summary: { b: 2 }, findings: ['not sent'] } };
  const candidates = [{ parti: 'a' }, { parti: 'b' }];
  const ctx = railContext({ surface: 'workbench', place: { surface: 'workbench' }, plan, lastEval,
    candidates });
  assert.equal(ctx.surface, 'workbench');
  assert.equal(ctx.plan, plan);
  assert.deepEqual(ctx.last_eval, { counts: { fatal: 1 }, constraint_summary: { a: 1 },
    fault_summary: { b: 2 } });
  assert.equal(ctx.candidate_count, candidates.length);
  const empty = JSON.parse(JSON.stringify(railContext({ surface: 'workbench' })));
  assert.deepEqual(empty, { surface: 'workbench' }, 'absent inputs send nothing, as before');
});

test('each candidate row carries the index its citation names, and only what the record states', () => {
  const c = { parti: 'centre-passage-double-pile', parti_name: 'Centre-passage double pile',
    nativity: 'native', score: 56.5, counts: { fatal: 2, serious: 40, minor: 90, info: 3 },
    trades_away: ['long prose the prompt is not sent'], plan: { heavy: true } };
  const row = candidateSummary(c, 3);
  assert.deepEqual(row, { candidate: 3, parti: 'centre-passage-double-pile',
    name: 'Centre-passage double pile', nativity: 'native', score: 56.5, fatal: 2, serious: 40,
    minor: 90 });
  // A refusal is read through sheet/refusal.js, and named only where the record states one.
  const refused = candidateSummary({ parti: 'x', refused: { kind: 'type-fact-downgraded',
    facts: ['bearing', 'stacks'] } }, 0);
  assert.deepEqual(refused.refused, { kind: 'type-fact-downgraded', facts: ['bearing', 'stacks'] });
  assert.equal('refused' in candidateSummary({ parti: 'x', refused: null }, 0), false);
  assert.equal('refused' in candidateSummary({ parti: 'x', refused: { kind: 'no-such' } }, 0), false);
});

test('the set is sent in whole rows under the stated budget, in order, and says what it left out', () => {
  const many = Array.from({ length: 400 }, (_, i) => ({ parti: `parti-${i}`, parti_name: `Parti ${i}`,
    nativity: 'borrowed', score: i, counts: { fatal: 0, serious: i, minor: i } }));
  const { rows, omitted } = candidateSummaries(many);
  assert.ok(rows.length > 0 && omitted > 0, 'the premise: the fixture crosses the budget');
  assert.equal(rows.length + omitted, many.length);
  const used = rows.reduce((n, r) => n + JSON.stringify(r).length + 1, 0);
  assert.ok(used <= CANDIDATE_BUDGET_CHARS, `${used} characters against ${CANDIDATE_BUDGET_CHARS}`);
  const next = JSON.stringify(candidateSummary(many[rows.length], rows.length)).length + 1;
  assert.ok(used + next > CANDIDATE_BUDGET_CHARS, 'the first row left out is the one that would cross');
  rows.forEach((r, i) => assert.equal(r.candidate, i, 'rows keep the set\'s own order and index'));
  const ctx = railContext({ surface: 'candidates', place: { surface: 'candidates' }, candidates: many });
  assert.deepEqual(ctx.candidate_summaries, rows);
  assert.equal(ctx.candidate_count, many.length, 'the count is the set\'s, not the rows\'');
  assert.equal('candidate_summaries' in railContext({ surface: 'candidates', candidates: [] }), false);
});
