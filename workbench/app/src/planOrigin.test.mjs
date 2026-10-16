/* AN EVALUATION IS OF A PLAN AND OF WHERE THAT PLAN CAME FROM (audit follow-up, 16 Oct 2026;
   ruled app-side by Lucas over the composer-side alternative).

   A composed plan's id is `{parti}-{briefId}`. The same parti from a later compose, or from another
   candidate slot, is a different house with the same id, and every id-keyed matcher kept the old
   one's verdict: `App.jsx` cleared the last evaluation only when the id changed, so the earlier
   verdict sat beside the new record until the next solve replaced it (up to about 25 s); and a
   pasted or ingested record that happened to share a candidate's id inherited the candidate's
   `planFrom` and with it a Next to the Plan step that was not its to have. Ids are stable by rule
   and cited in files, so none is changed: the origin is the second half of the key.

   What each test is for, in the order a mutation of the code would meet it:

     originKeyOf / evalOriginOf / stampEval / evalIsOf   the key, its stamp and its one reader;
     journeyState                                        the screen the key exists to prevent;
     answerIsForHere                                     an answer for one house is dropped when it
                                                         lands against another;
     the census of `planDoc.load(`                       the other half, a load with no origin to
                                                         record clears the old one;
     the joins                                           the bench stamps at SUBMIT, the shell asks
                                                         `evalIsOf`, the session keeps the job's
                                                         brief. A React component cannot be rendered
                                                         under `node --test` here, so the decisions
                                                         are in the leaves above and the joins are
                                                         pinned by reading the sources, with the
                                                         browser walk driving the whole. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, statSync } from 'node:fs';
import {
  originKeyOf, evalOriginOf, stampEval, evalIsOf, journeyState, answerIsForHere, unstampEval,
} from './journey/journey.js';
import { stripComments } from './sourceReader.mjs';

const PLAN = { id: 'centre-passage-double-pile-new-brief', style: 'tidewater-georgian', levels: [] };
const BRIEF = { id: 'new-brief', name: 'Smith House', style: 'tidewater-georgian' };
const cand = (jobId, n) => ({ kind: 'candidate', planId: PLAN.id, jobId, n });
const EV = { plan: PLAN.id, check: { plan: PLAN.id, counts: { fatal: 0, serious: 43, minor: 9 } },
  placement: { geometry_report: { refused: null } } };

test('the key is the kind, the job and the slot, and empty where no origin is recorded', () => {
  assert.equal(originKeyOf(PLAN.id, cand('j1', 0)), 'candidate|j1|0');
  assert.equal(originKeyOf(PLAN.id, cand('j1', 3)), 'candidate|j1|3');
  assert.equal(originKeyOf(PLAN.id, cand('j2', 3)), 'candidate|j2|3', 'another job is another house');
  assert.equal(originKeyOf(PLAN.id, { kind: 'example', planId: PLAN.id }), 'example||');
  assert.equal(originKeyOf(PLAN.id, { kind: 'traced', planId: PLAN.id }), 'traced||');
  // an origin is trusted only where it names THIS plan, exactly as `originOf` reads it
  assert.equal(originKeyOf(PLAN.id, { ...cand('j1', 0), planId: 'another-plan' }), '');
  for (const none of [null, undefined, 'x', 3, [], {}, { kind: 'candidate' }, { planId: PLAN.id }]) {
    assert.equal(originKeyOf(PLAN.id, none), '', JSON.stringify(none));
  }
  for (const noPlan of [null, undefined, '', '  ', 7]) {
    assert.equal(originKeyOf(noPlan, cand('j1', 0)), '', `plan id ${JSON.stringify(noPlan)}`);
  }
  // a slot that is not an index is no slot, not a slot 0
  assert.equal(originKeyOf(PLAN.id, { ...cand('j1', 0), n: -1 }), 'candidate|j1|');
  assert.equal(originKeyOf(PLAN.id, { ...cand('j1', 0), n: 'two' }), 'candidate|j1|');
});

test('an evaluation is stamped with the origin it was asked for, and unstamped is of no origin', () => {
  const stamped = stampEval(EV, PLAN.id, cand('j1', 2));
  assert.equal(evalOriginOf(stamped), 'candidate|j1|2');
  assert.notEqual(stamped, EV, 'the response is copied, never written into');
  assert.equal(evalOriginOf(EV), '', 'no stamp is the empty origin');
  assert.equal(stampEval(EV, PLAN.id, null).evaluated_from, '');
  for (const notObj of [null, undefined, 'x', 3]) assert.equal(stampEval(notObj, PLAN.id, cand('j', 0)), notObj);
  for (const bad of [null, 3, {}, { evaluated_from: 7 }, { evaluated_from: null }]) {
    assert.equal(evalOriginOf(bad), '', JSON.stringify(bad));
  }
});

test('an evaluation is of a plan only from where it now came: the id AND the origin', () => {
  const from = cand('j1', 2);
  const ev = stampEval(EV, PLAN.id, from);
  assert.equal(evalIsOf(ev, PLAN.id, from), true);
  // the same id from another compose is another house
  assert.equal(evalIsOf(ev, PLAN.id, cand('j2', 2)), false, 'a later compose, the same slot');
  assert.equal(evalIsOf(ev, PLAN.id, cand('j1', 3)), false, 'the same compose, another slot');
  assert.equal(evalIsOf(ev, PLAN.id, { kind: 'example', planId: PLAN.id }), false, 'an example of that id');
  assert.equal(evalIsOf(ev, PLAN.id, null), false, 'a record whose origin was cleared');
  assert.equal(evalIsOf(ev, 'another-plan', from), false, 'and the id half still holds');
  // an evaluation nobody stamped is of no origin: not of a plan whose origin is recorded ...
  assert.equal(evalIsOf(EV, PLAN.id, from), false);
  // ... and of a plan whose origin is not
  assert.equal(evalIsOf(EV, PLAN.id, null), true);
  assert.equal(evalIsOf(stampEval(EV, PLAN.id, null), PLAN.id, null), true);
  // an evaluation whose check errored names its plan at the top of the response (WP-14.20)
  assert.equal(evalIsOf(stampEval({ plan: PLAN.id, check: { error: 'x' } }, PLAN.id, from), PLAN.id, from), true);
  for (const noPlan of [null, '', undefined]) assert.equal(evalIsOf(ev, noPlan, from), false);
});

test('the screen this prevents: a later compose\'s candidate read as already evaluated', () => {
  /* Candidate 2 of job j1 was evaluated: 43 serious, no fatal. The reader composes again and opens
     candidate 2 of job j2, the same parti, therefore the same plan id. Before the key the shell
     held j1's verdict beside j2's record, and the journey read the plan as EVALUATED. */
  const j1 = cand('j1', 2);
  const verdict = stampEval(EV, PLAN.id, j1);
  const step = (st, id) => st.steps.find((x) => x.id === id);
  const before = journeyState({ session: { brief: BRIEF, jobId: 'j1', planFrom: j1, result: { candidates: [{}, {}, {}] } },
    plan: PLAN, lastEval: verdict });
  assert.equal(step(before, 'plan').state, 'evaluated');
  const j2 = cand('j2', 2);
  const after = journeyState({ session: { brief: BRIEF, jobId: 'j2', planFrom: j2, result: { candidates: [{}, {}, {}] } },
    plan: PLAN, lastEval: verdict });
  assert.equal(step(after, 'plan').state, 'unevaluated', 'j1\'s verdict is not j2\'s house\'s');
  assert.equal(step(after, 'plan').counts, null, 'and no counts of it are shown beside the new record');
  // the new house evaluated gets its own
  const mine = journeyState({ session: { brief: BRIEF, jobId: 'j2', planFrom: j2, result: { candidates: [{}, {}, {}] } },
    plan: PLAN, lastEval: stampEval(EV, PLAN.id, j2) });
  assert.equal(step(mine, 'plan').state, 'evaluated');
});

/* ------------------------------------------------------------------ the sources */

const SRC = new URL('./', import.meta.url);
const files = [];
(function walk(dir) {
  for (const f of readdirSync(dir).sort()) {
    const u = new URL(f, dir);
    if (statSync(u).isDirectory()) walk(new URL(f + '/', dir));
    else if (/\.(m?js|jsx)$/.test(f) && !/\.test\.mjs$/.test(f)) files.push(u);
  }
}(SRC));
const code = (u) => stripComments(readFileSync(u, 'utf8'));
const rel = (u) => u.pathname.slice(SRC.pathname.length);

/* the argument text of every `planDoc.load(` call in a source, parentheses balanced */
function loadCalls(src) {
  const out = [];
  let at = src.indexOf('planDoc.load(');
  while (at !== -1) {
    let depth = 0;
    let i = at + 'planDoc.load'.length;
    const start = i + 1;
    for (; i < src.length; i += 1) {
      if (src[i] === '(') depth += 1;
      else if (src[i] === ')') { depth -= 1; if (depth === 0) break; }
    }
    out.push(src.slice(start, i).trim());
    at = src.indexOf('planDoc.load(', i);
  }
  return out;
}

test('an answer for one house is dropped when it lands against another', () => {
  const A = cand('j1', 0);
  // the same house, from where it came: kept
  assert.equal(answerIsForHere(PLAN.id, A, PLAN.id, { ...A }), true);
  assert.equal(answerIsForHere(PLAN.id, null, PLAN.id, null), true, 'no origin recorded at either end');
  // the reader opened another house with another id
  assert.equal(answerIsForHere(PLAN.id, A, 'another-plan', null), false);
  // ... and when NEITHER end records an origin the two keys are both empty, so only the id can say
  // they are different houses (an example, then a pasted record, then another example)
  assert.equal(answerIsForHere(PLAN.id, null, 'another-plan', null), false, 'the id alone separates two origin-less houses');
  assert.equal(answerIsForHere('p-one', { kind: 'example', planId: 'p-one' }, 'p-two', { kind: 'example', planId: 'p-two' }), false);
  // the same id from a later compose, or another slot: a different house
  assert.equal(answerIsForHere(PLAN.id, A, PLAN.id, cand('j2', 0)), false, 'another job');
  assert.equal(answerIsForHere(PLAN.id, A, PLAN.id, cand('j1', 1)), false, 'another slot');
  // a candidate replaced by a pasted record of the same id (its origin was cleared)
  assert.equal(answerIsForHere(PLAN.id, A, PLAN.id, null), false);
  // an origin that names ANOTHER plan is no origin (as `originKeyOf` reads it), at both ends
  assert.equal(answerIsForHere(PLAN.id, { ...A, planId: 'other' }, PLAN.id, null), true);
  // no plan on the bench, or none asked of: nothing is filed
  for (const none of [null, undefined, '', '  ', 4]) {
    assert.equal(answerIsForHere(none, A, none, A), false, JSON.stringify(none));
    assert.equal(answerIsForHere(PLAN.id, A, none, A), false);
  }
});

test('a saved check report is the server\'s answer and carries none of the app\'s bookkeeping', () => {
  const stamped = stampEval(EV, PLAN.id, cand('j1', 2));
  assert.equal(evalOriginOf(stamped), 'candidate|j1|2', 'the premise: it was stamped');
  const clean = unstampEval(stamped);
  assert.deepEqual(clean, EV, 'the same answer the server gave');
  assert.equal('evaluated_from' in clean, false);
  assert.equal(evalOriginOf(clean), '');
  assert.equal('evaluated_from' in stamped, true, 'the held evaluation keeps its stamp');
  for (const x of [null, undefined, 'x', 3, [], EV]) assert.equal(unstampEval(x), x, 'nothing to remove, nothing copied');
  const src = code(new URL('surfaces/ExportDetails.jsx', SRC));
  assert.match(src, /save\(`\$\{plan\?\.id \|\| 'plan'\}-check\.json`, unstampEval\(lastEval\)\)/);
});

test('every load of a whole, different document records its origin or clears it', () => {
  /* `planFrom` names its plan by id and the journey trusts it while that id is the bench's, so a
     load that records nothing leaves the previous origin standing for whatever has the same id. The
     two loads that CONTINUE the same document -- the loop's revised record, which has the id and
     the origin of what was submitted -- are the exceptions, and they are named here so a third
     cannot join them by being forgotten. */
  const CONTINUATIONS = new Set(['res.revised_plan', 'revised']);
  const sites = [];
  for (const u of files) for (const arg of loadCalls(code(u))) sites.push({ file: rel(u), arg });
  assert.ok(sites.length >= 7, `the census reached ${sites.length} load sites`);
  const bare = sites.filter((s) => !/\b(recordPlanFrom|clearPlanFrom)\(/.test(s.arg) && !CONTINUATIONS.has(s.arg));
  assert.deepEqual(bare, [], 'these put a document on the bench and say nothing about where it came from');
  const named = sites.filter((s) => CONTINUATIONS.has(s.arg));
  assert.equal(named.length, 2, 'the two continuations exist, so the allowance is not an empty one');
  assert.ok(named.every((s) => s.file === 'surfaces/PlanWorkbench.jsx'));
  // the census sees the three kinds: a recorded origin, a cleared one, and the continuation
  assert.ok(sites.some((s) => /recordPlanFrom\('candidate'/.test(s.arg)));
  assert.ok(sites.some((s) => /clearPlanFrom\(rec\)/.test(s.arg)), 'a pasted record');
  assert.ok(sites.some((s) => /clearPlanFrom\(res\.record\)/.test(s.arg)), 'an ingested drawing');
});

test('the census cannot be walked round: planDoc is only ever used by its own name and a known method', () => {
  /* The census above reads the text `planDoc.load(`. An alias (`const doc = planDoc`, `const { load }
     = planDoc`, `planDoc['load'](...)`, `import { planDoc as d }`) loads a whole document and is
     invisible to it, so this holds the OTHER half: every use of the store in every source is its
     own name followed by one of the five methods it has, and no source renames it on import. */
  const users = [];
  for (const u of files) {
    const src = code(u);
    if (!/\bplanDoc\b/.test(src) || /export const planDoc\b/.test(src)) continue;
    users.push(rel(u));
    // an import renames nothing
    for (const m of src.matchAll(/import\s*\{([^}]*)\}\s*from\s*['"][^'"]*planDoc\.js['"]/g)) {
      assert.ok(!/\bplanDoc\s+as\b/.test(m[1]), `${rel(u)} renames planDoc on import`);
    }
    // every other occurrence is `planDoc.<method>`
    // (not the file name in an import path, and not the import's own binding)
    const bad = [...src.matchAll(/(?<!\/)\bplanDoc\b(?!\.(?:get|subscribe|update|undo|redo|load)\b)(?![^\n]*from\s*['"][^'"]*planDoc\.js['"])/g)]
      .map((m) => src.slice(Math.max(0, m.index - 20), m.index + 40).replace(/\s+/g, ' '));
    assert.deepEqual(bad, [], `${rel(u)} uses the store other than as planDoc.<method>`);
  }
  assert.ok(users.length >= 5, `the census reached ${users.length} users of the store`);
  // and the driven case: the aliases it exists to catch ARE caught by the same pattern
  const probe = (txt) => [...txt.matchAll(/\bplanDoc\b(?!\.(?:get|subscribe|update|undo|redo|load)\b)/g)].length;
  assert.equal(probe('const doc = planDoc; doc.load(x)'), 1);
  assert.equal(probe('const { load } = planDoc;'), 1);
  assert.equal(probe("planDoc['load'](x)"), 1);
  assert.equal(probe('planDoc.load(x); planDoc.get()'), 0);
});

test('the bench stamps an evaluation with the origin it held when it ASKED', () => {
  /* Read at submit, not at the answer: a reader can open another house with the same id while the
     solve runs, and an answer stamped when it landed would be filed against it. The decision (the
     key, the stamp) is in the leaf above; this is the join. */
  const src = code(new URL('surfaces/PlanWorkbench.jsx', SRC));
  const submit = src.indexOf('const fromAtSubmit = session.get().planFrom');
  const ask = src.indexOf('api.evaluate(p,');
  assert.ok(submit !== -1 && ask !== -1, 'both reads exist');
  assert.ok(submit < ask, 'the origin is read before the request goes');
  assert.match(src, /setLastEval\(stampEval\(res, submitted && submitted\.id, fromAtSubmit\)\)/);
  assert.doesNotMatch(src, /setLastEval\(res\)/, 'no evaluation is filed unstamped');
  assert.equal((src.match(/setLastEval\(/g) || []).length, 1, 'one writer of the shell\'s evaluation');
});

test('the bench drops an answer that lands against another house, before it files anything', () => {
  const src = code(new URL('surfaces/PlanWorkbench.jsx', SRC));
  const guard = src.search(/answerIsForHere\(submitted && submitted\.id, fromAtSubmit, /);
  assert.ok(guard !== -1, 'the answer is asked whether it is for this house');
  const first = src.indexOf('setPrevKeys(lastFindingsRef.current)');
  assert.ok(first !== -1 && guard < first, 'the question comes before the first thing the answer sets');
  assert.ok(guard < src.indexOf('setEvalError(res?.check?.error'), 'and before its error line');
  assert.ok(guard < src.indexOf('setLastEval(stampEval('), 'and before the shell is handed it');
  // the question reads the origin the bench holds NOW, not the one it asked with, and a no returns
  assert.match(src, /answerIsForHere\([^)]*session\.get\(\)\.planFrom\)\)\s*return;/);
  assert.doesNotMatch(src, /if \(!answerIsForHere\([^)]*\)\) \{\s*\}/, 'and the branch is not empty');
});

test('the shell clears a stale evaluation on an origin change, and the journey and rail read the same matcher', () => {
  const app = code(new URL('App.jsx', SRC));
  assert.match(app, /const planKey = `\$\{planId \?\? ''\}\\u0000\$\{originKeyOf\(planId, planFrom\)\}`/);
  assert.match(app, /\[planKey\]\);/, 'the effect runs when the KEY changes, not only the id');
  assert.match(app, /evalIsOf\(ev, planId, planFrom\)/);
  assert.doesNotMatch(app, /evalPlanOf\(ev\) === planId/, 'the id-only clear is gone');
  const journey = code(new URL('journey/journey.js', SRC));
  assert.match(journey, /evalIsOf\(lastEval, planId, s\.planFrom\)/);
  // and in the interval before that clear runs, every reader of the shell's evaluation is handed
  // the filtered one: the surface in view and the assistant (the journey asks `evalIsOf` itself)
  assert.match(app, /const lastEvalHere = evalIsOf\(lastEval, planId, planFrom\) \? lastEval : null;/);
  assert.match(app, /<Active \{\.\.\.shared\} lastEval=\{lastEvalHere\} \/>/);
  assert.match(app, /<RailHost[^>]*lastEval=\{lastEvalHere\}/s);
  // (the journey bar is handed the raw one on purpose: `journeyState` asks `evalIsOf` itself, which
  // is what the next assertion above holds)
});

test('the candidates\' brief name is the job\'s, not the draft\'s', () => {
  const set = code(new URL('surfaces/CandidateSet.jsx', SRC));
  assert.equal((set.match(/briefNameOf\(result, s\.jobBrief\)/g) || []).length, 2);
  assert.doesNotMatch(set, /briefNameOf\(result, s\.brief\)/);
  /* and so are the count it was asked for and the household beside the columns: both read the
     job's brief where the job kept one, and the draft only where it did not */
  assert.match(set, /const jobBrief = s\.jobBrief && s\.jobBrief\.id === result\.brief \? s\.jobBrief : null;/);
  assert.match(set, /const askedFor = \(jobBrief \? jobBrief\.candidates : s\.brief\?\.candidates\) \|\| 4;/);
  assert.match(set, /const household = jobBrief \? jobBrief\.household : s\.brief\?\.household;/);
  assert.doesNotMatch(set, /\{s\.brief\.household\}/, 'the household is not read off the draft after the job');
  const intake = code(new URL('surfaces/BriefIntake.jsx', SRC));
  assert.match(intake, /composeStart\(job_id, brief\)/, 'the brief the job was accepted with is kept');
});
