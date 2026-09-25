/* WHAT THE SESSION IS TOLD ABOUT A HOUSE'S JOURNEY, AND WHAT IT KEEPS (WP-14.10, PRD §G.1).

   `journey/sessionWrites.js` is every write of the two facts PRD §G.1 adds -- where the plan on
   the bench came from, and a compose that failed or expired -- and `state/session.js` holds and
   persists them. Both are importable here: the writes are pure, and the store touches
   `localStorage` only inside a `try`, so it loads under node with a stand-in installed first.

   The subjects:
   - a stored entry written by an older build, or a hostile one, costs that field and not the
     session;
   - the key is unchanged and the persisted object is exactly `{ brief, jobId, planFrom, jobError }`
     (PRD §J.4 forbids renaming the key);
   - a plan with no id records no provenance, because it could never be matched to one;
   - the server's word on a job decides whether it failed, expired, or is still the reader's. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  PLAN_FROM_KINDS, JOB_ERROR_STATES, readPlanFrom, readJobError, planFromOf, briefNameOf,
  composeStart, jobFailed, reattach, jobExpired,
} from './journey/sessionWrites.js';

const KEY = 'tdl-workbench-session';

test('a stored planFrom is read back only in the shape the journey can use', () => {
  assert.deepEqual([...PLAN_FROM_KINDS], ['candidate', 'example', 'traced']);
  const good = { kind: 'candidate', planId: 'p', jobId: 'j', n: 0, briefName: 'B' };
  assert.deepEqual(readPlanFrom(good), good);
  for (const bad of [null, 'x', [], { kind: 'pasted', planId: 'p' }, { kind: 'example' },
    { kind: 'example', planId: '' }, { kind: 'example', planId: 7 }]) {
    assert.equal(readPlanFrom(bad), null, JSON.stringify(bad));
  }
  // a field of the wrong type is dropped to null, and the provenance survives it
  assert.deepEqual(readPlanFrom({ kind: 'candidate', planId: 'p', jobId: 3, n: -1, briefName: {} }),
    { kind: 'candidate', planId: 'p', jobId: null, n: null, briefName: null });
  assert.equal(readPlanFrom({ kind: 'candidate', planId: 'p', n: 1.5 }).n, null, 'n is an index');
});

test('a stored jobError is read back only as failed or expired', () => {
  assert.deepEqual([...JOB_ERROR_STATES], ['failed', 'expired']);
  assert.deepEqual(readJobError({ state: 'expired', reason: 'gone', jobId: 'j' }),
    { state: 'expired', reason: 'gone', jobId: 'j' });
  assert.equal(readJobError({ state: 'running' }), null);
  assert.equal(readJobError('failed'), null);
  assert.deepEqual(readJobError({ state: 'failed', reason: '  ' }), { state: 'failed', reason: null, jobId: null });
});

test('a plan opened on the bench records where it came from, and a plan with no id records nothing', () => {
  assert.deepEqual(planFromOf('candidate', { id: 'p' }, { jobId: 'j', n: 3, briefName: 'B' }),
    { kind: 'candidate', planId: 'p', jobId: 'j', n: 3, briefName: 'B' });
  // only a candidate carries a job, an index and a brief -- an example or a tracing has none
  assert.deepEqual(planFromOf('example', { id: 'p' }, { jobId: 'j', n: 3, briefName: 'B' }),
    { kind: 'example', planId: 'p', jobId: null, n: null, briefName: null });
  assert.deepEqual(planFromOf('traced', { id: 'p' }),
    { kind: 'traced', planId: 'p', jobId: null, n: null, briefName: null });
  assert.equal(planFromOf('example', { name: 'no id' }), null);
  assert.equal(planFromOf('example', null), null);
  assert.equal(planFromOf('pasted', { id: 'p' }), null, 'a kind the journey has no words for');
});

test('the brief is named only where the draft in hand IS the brief the result names', () => {
  assert.equal(briefNameOf({ brief: 'family-georgian' }, { id: 'family-georgian', name: 'Family house' }), 'Family house');
  assert.equal(briefNameOf({ brief: 'family-georgian' }, { id: 'new-brief', name: 'Something else' }), null);
  assert.equal(briefNameOf({ brief: 'family-georgian' }, { id: 'family-georgian', name: '' }), null);
  assert.equal(briefNameOf(null, { id: 'x', name: 'X' }), null);
});

test('an accepted compose clears everything the last one said, and names the new job', () => {
  assert.deepEqual(composeStart('j2'), { result: null, progress: [], jobError: null, jobId: 'j2' });
  assert.deepEqual(jobFailed('j2', { error: 'boom' }), { state: 'failed', reason: 'boom', jobId: 'j2' });
});

test('on a reattach the server decides: done brings the result, error and 404 forget the job', () => {
  assert.deepEqual(reattach('j', { status: 'done', result: { candidates: [] } }),
    { patch: { result: { candidates: [] }, jobError: null }, stream: false });
  assert.deepEqual(reattach('j', { status: 'error', error: 'the composer raised' }),
    { patch: { jobId: null, jobError: { state: 'failed', reason: 'the composer raised', jobId: 'j' } }, stream: false });
  // running: the job is alive, so a failure recorded off a dropped stream is withdrawn
  for (const status of ['running', 'queued', undefined]) {
    assert.deepEqual(reattach('j', { status }), { patch: { jobError: null }, stream: true }, String(status));
  }
  assert.deepEqual(jobExpired('j', "no job 'j'"),
    { jobId: null, jobError: { state: 'expired', reason: "no job 'j'", jobId: 'j' } });
});

test('the session store keeps its key, persists the four facts, and survives a hostile entry', async () => {
  const store = new Map();
  store.set(KEY, JSON.stringify({
    brief: { style: 'craftsman' }, jobId: 'j1', result: { should: 'not persist' },
    planFrom: { kind: 'candidate', planId: 'p1', jobId: 'j1', n: 'two' },
    jobError: { state: 'exploded' },
  }));
  const prior = globalThis.localStorage;
  globalThis.localStorage = { getItem: (k) => (store.has(k) ? store.get(k) : null), setItem: (k, v) => store.set(k, v) };
  try {
    const { session, recordPlanFrom } = await import('./state/session.js');
    const s = session.get();
    assert.deepEqual(s.brief, { style: 'craftsman' });
    assert.equal(s.jobId, 'j1');
    assert.equal(s.result, null, 'the result is re-fetched, never read back from storage');
    assert.deepEqual(s.planFrom, { kind: 'candidate', planId: 'p1', jobId: 'j1', n: null, briefName: null });
    assert.equal(s.jobError, null, 'a state the journey has no words for is dropped, not kept');

    const plan = { id: 'p2' };
    assert.equal(recordPlanFrom('example', plan), plan, 'it hands back the plan it recorded, to be loaded');
    const saved = JSON.parse(store.get(KEY));
    assert.deepEqual(Object.keys(saved).sort(), ['brief', 'jobError', 'jobId', 'planFrom']);
    assert.deepEqual(saved.planFrom, { kind: 'example', planId: 'p2', jobId: null, n: null, briefName: null });

    session.set(jobExpired('j1', 'gone'));
    assert.deepEqual(JSON.parse(store.get(KEY)).jobError, { state: 'expired', reason: 'gone', jobId: 'j1' });
    assert.equal(JSON.parse(store.get(KEY)).jobId, null);
  } finally {
    if (prior === undefined) delete globalThis.localStorage; else globalThis.localStorage = prior;
  }
});
