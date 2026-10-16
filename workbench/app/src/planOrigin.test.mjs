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
  originKeyOf, evalOriginOf, stampEval, evalIsOf, journeyState,
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

test('the shell clears a stale evaluation on an origin change, and the journey and rail read the same matcher', () => {
  const app = code(new URL('App.jsx', SRC));
  assert.match(app, /const planKey = `\$\{planId \?\? ''\}\\u0000\$\{originKeyOf\(planId, planFrom\)\}`/);
  assert.match(app, /\[planKey\]\);/, 'the effect runs when the KEY changes, not only the id');
  assert.match(app, /evalIsOf\(ev, planId, planFrom\)/);
  assert.doesNotMatch(app, /evalPlanOf\(ev\) === planId/, 'the id-only clear is gone');
  const journey = code(new URL('journey/journey.js', SRC));
  assert.match(journey, /evalIsOf\(lastEval, planId, s\.planFrom\)/);
});

test('the candidates\' brief name is the job\'s, not the draft\'s', () => {
  const set = code(new URL('surfaces/CandidateSet.jsx', SRC));
  assert.equal((set.match(/briefNameOf\(result, s\.jobBrief\)/g) || []).length, 2);
  assert.doesNotMatch(set, /briefNameOf\(result, s\.brief\)/);
  const intake = code(new URL('surfaces/BriefIntake.jsx', SRC));
  assert.match(intake, /composeStart\(job_id, brief\)/, 'the brief the job was accepted with is kept');
});
