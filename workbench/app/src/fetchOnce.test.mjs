/* ONE READ, THREE STATES, AND NO EMPTY SUCCESS (WP-14.8, PRD §I.2).

   `api/fetchOnce.js` is the state machine behind `useGlossary` and `useNames`, and
   `api/adapters.js` decides what an unusable body is. Every state is driven here with a loader
   that is a plain function, so nothing touches the network, React or `node_modules`.

   The case this file exists for is the one `api/useStyles.js` records shipping once: a failed
   read returned as an empty success, so a picker drew "no styles" for a server that was down.
   A glossary that could not be read must say so, and a glossary that answered with no terms
   must say so too — that second shape is the one a `.catch(() => [])` cannot even see. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createFetchOnce } from './api/fetchOnce.js';
import { adaptGlossary, adaptSearchIndex } from './api/adapters.js';
import { isMissing } from './glossary/lookup.js';

const deferred = () => {
  let resolve; let reject;
  const promise = new Promise((res, rej) => { resolve = res; reject = rej; });
  return { promise, resolve, reject };
};

test('it starts loading, and a loading state claims nothing', () => {
  const s = createFetchOnce(() => new Promise(() => {}));
  const st = s.get();
  assert.equal(st.status, 'loading');
  assert.equal(st.value, null);
  assert.equal(st.error, null);
  assert.ok(Object.isFrozen(st), 'the snapshot is frozen, so no reader can edit the shared one');
});

test('a read that answers becomes ready with the ADAPTED value, and listeners hear it', async () => {
  const d = deferred();
  const s = createFetchOnce(() => d.promise, (body) => ({ wrapped: body }));
  let heard = 0;
  s.subscribe(() => { heard += 1; });
  const p = s.load();
  assert.equal(s.get().status, 'loading');
  d.resolve({ n: 1 });
  const v = await p;
  assert.deepEqual(v, { wrapped: { n: 1 } });
  assert.equal(s.get().status, 'ready');
  assert.deepEqual(s.get().value, { wrapped: { n: 1 } });
  assert.equal(heard, 1);
});

test('a read that fails becomes failed WITH ITS REASON, never ready with nothing', async () => {
  const s = createFetchOnce(() => Promise.reject(new Error('GET /api/glossary -> 503')));
  const v = await s.load();
  assert.equal(v, null);
  assert.equal(s.get().status, 'failed');
  assert.match(s.get().error.message, /503/);
  assert.equal(s.get().value, null);
});

test('a thrown non-Error still arrives as an Error with its text', async () => {
  const s = createFetchOnce(() => { throw 'refused'; }); // eslint-disable-line no-throw-literal
  await s.load();
  assert.equal(s.get().status, 'failed');
  assert.ok(s.get().error instanceof Error);
  assert.equal(s.get().error.message, 'refused');
});

test('a hundred readers make one request', async () => {
  let calls = 0;
  const d = deferred();
  const s = createFetchOnce(() => { calls += 1; return d.promise; });
  const ps = Array.from({ length: 100 }, () => s.load());
  d.resolve({});
  await Promise.all(ps);
  assert.equal(calls, 1, 'a read in flight is shared, not repeated');
  await s.load();
  assert.equal(calls, 1, 'a ready read is not re-read');
});

test('a later load retries a failed read, publishing loading first', async () => {
  let calls = 0;
  const s = createFetchOnce(() => {
    calls += 1;
    return calls === 1 ? Promise.reject(new Error('down')) : Promise.resolve('up');
  });
  await s.load();
  assert.equal(s.get().status, 'failed');
  const seen = [];
  s.subscribe(() => seen.push(s.get().status));
  const p = s.load();
  assert.equal(s.get().status, 'loading', 'a retry is not reported as the old failure');
  await p;
  assert.equal(calls, 2);
  assert.deepEqual(seen, ['loading', 'ready']);
  assert.equal(s.get().value, 'up');
});

test('the snapshot is stable between changes, which useSyncExternalStore requires', async () => {
  const s = createFetchOnce(() => Promise.resolve(1));
  const a = s.get();
  assert.equal(s.get(), a, 'two reads with no change return the same object');
  await s.load();
  const b = s.get();
  assert.notEqual(b, a);
  assert.equal(s.get(), b);
});

test('an unsubscribed listener hears nothing more', async () => {
  const s = createFetchOnce(() => Promise.resolve(1));
  let heard = 0;
  const off = s.subscribe(() => { heard += 1; });
  off();
  await s.load();
  assert.equal(heard, 0);
});

/* ---- the adapters: what a body must carry to count as an answer ---- */

test('adaptGlossary refuses a body with no terms list, so an empty 200 is a failure', async () => {
  for (const junk of [null, undefined, 'x', 3, {}, { terms: 'no' }, { count: 0 }]) {
    assert.throws(() => adaptGlossary(junk), /without a terms list/);
  }
  // and through the machine, that refusal is a failed state with that reason
  const s = createFetchOnce(() => Promise.resolve({ version: 'x' }), adaptGlossary);
  await s.load();
  assert.equal(s.get().status, 'failed');
  assert.match(s.get().error.message, /terms list/);
});

test('adaptGlossary indexes a real payload into the frozen lookup', () => {
  const body = {
    version: '0.1.0+abc', count: 1, by_family: { rank: ['rank-style'] }, by_field: {},
    terms: [{ id: 'rank-style', term: 'style', family: 'rank', definition: 'd', kind: 'editorial' }],
  };
  const lk = adaptGlossary(body);
  assert.ok(Object.isFrozen(lk));
  assert.equal(lk.version, '0.1.0+abc');
  assert.equal(lk.term('rank-style').term, 'style');
  assert.ok(isMissing(lk.term('nope')));
  // an EMPTY list whose count agrees is the server's answer and not a failure: the adapter
  // refuses a shape, never a number it cannot check
  assert.equal(adaptGlossary({ terms: [], count: 0 }).count, 0);
});

test('a terms list that disagrees with the payload’s own count is a failure, not a thinner glossary', () => {
  const t = { id: 'rank-style', term: 'style', family: 'rank', definition: 'd', kind: 'editorial' };
  assert.throws(() => adaptGlossary({ terms: [t], count: 121 }), /1 terms under a count of 121/);
  assert.equal(adaptGlossary({ terms: [t], count: 1 }).count, 1);
  assert.equal(adaptGlossary({ terms: [t] }).count, 1, 'a body stating no count is not convicted of one');
});

test('adaptSearchIndex refuses a body with no entries list and indexes one that has it', () => {
  for (const junk of [null, {}, { entries: {} }]) {
    assert.throws(() => adaptSearchIndex(junk), /without an entries list/);
  }
  const idx = adaptSearchIndex({ entries: [{ cite: 'style:x', name: 'The X' }] });
  assert.ok(idx instanceof Map);
});
