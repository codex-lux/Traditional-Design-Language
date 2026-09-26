/* WHAT THIS BROWSER REMEMBERS, AND THAT IT DECIDES NOTHING (WP-14.8, PRD §I.10).

   `state/prefs.js` in `state/layout.js`'s idiom, driven the way `layout.test.mjs` drives that
   store: a localStorage stand-in installed BEFORE a fresh module instance is imported, because
   the store reads it at module scope. Each case gets its own instance (`?case=`), and this file
   must stay sequential for the reason `layout.test.mjs` states — `localStorage` is one global.

   The corrupt-entry case is the one the package names: a reader whose stored prefs are
   unreadable must get the defaults and a working page, never a broken one. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const KEY = 'tdl-workbench-prefs';

function stub(seed, { failWrites = false } = {}) {
  const map = new Map(Object.entries(seed || {}));
  let writes = 0;
  globalThis.localStorage = {
    getItem: (k) => (map.has(k) ? map.get(k) : null),
    setItem: (k, v) => {
      writes += 1;
      if (failWrites) throw new Error('QuotaExceededError');
      map.set(k, String(v));
    },
    removeItem: (k) => map.delete(k),
  };
  return { map, writes: () => writes };
}

let seq = 0;
const fresh = async (seed, opts) => {
  const store = stub(seed, opts);
  const mod = await import(`./state/prefs.js?case=${seq += 1}`);
  return { ...mod, store };
};

const DEFAULTS = { styleInHand: null, seen: {}, folds: {} };
const plain = (o) => JSON.parse(JSON.stringify(o));

test('an absent entry gives the defaults', async () => {
  const { prefs } = await fresh();
  assert.deepEqual(plain(prefs.get()), DEFAULTS);
});

test('a corrupt entry gives the defaults and a working store, never a broken page', async () => {
  for (const junk of ['{not json', 'null', '42', '"a string"', '[1,2]']) {
    const { prefs, store } = await fresh({ [KEY]: junk });
    assert.deepEqual(plain(prefs.get()), DEFAULTS, `for ${junk}`);
    prefs.markSeen('head:surface-glossary');
    assert.ok(prefs.isSeen('head:surface-glossary'), 'the store still works after a corrupt read');
    assert.deepEqual(JSON.parse(store.map.get(KEY)).seen, { 'head:surface-glossary': true },
      'and its first write replaces the corrupt entry with a well-formed one');
  }
});

test('no localStorage at all gives the defaults', async () => {
  globalThis.localStorage = undefined;             // every read and write now throws
  const mod = await import(`./state/prefs.js?case=${seq += 1}`);
  assert.deepEqual(plain(mod.prefs.get()), DEFAULTS);
  mod.prefs.setFold('proof', true);                 // a write with nowhere to go
  assert.equal(mod.prefs.fold('proof'), true, 'the reader loses the memory, not the page');
});

test('each key is checked by itself, so one malformed key costs that key alone', async () => {
  const { prefs } = await fresh({
    [KEY]: JSON.stringify({
      styleInHand: 7, seen: { 'front-door': true, bad: 'yes', '': true }, folds: { proof: false, x: 1 },
    }),
  });
  const st = prefs.get();
  assert.equal(st.styleInHand, null, 'a non-string style is dropped');
  assert.deepEqual(plain(st.seen), { 'front-door': true }, 'only literal trues on real keys survive');
  assert.deepEqual(plain(st.folds), { proof: false }, 'only booleans survive, false included');
});

test('the sanitizer is total over anything a stale or hostile entry can hold', async () => {
  const { sanitize } = await fresh();
  for (const junk of [null, undefined, 1, 'x', [], { seen: [], folds: 'no' }]) {
    assert.deepEqual(plain(sanitize(junk)), DEFAULTS);
  }
  assert.equal(sanitize({ styleInHand: '  ' }).styleInHand, null, 'a blank id is not an id');
  assert.equal(sanitize({ styleInHand: 'tidewater-georgian' }).styleInHand, 'tidewater-georgian');
});

test('a write that fails keeps the in-memory store', async () => {
  const { prefs, store } = await fresh(undefined, { failWrites: true });
  prefs.setStyleInHand('tidewater-georgian');
  assert.equal(prefs.get().styleInHand, 'tidewater-georgian');
  assert.ok(store.writes() >= 1, 'the premise: a write was attempted and threw');
  assert.equal(store.map.has(KEY), false);
});

test('the style in hand: an id or null, and anything else is refused rather than stored', async () => {
  const { prefs } = await fresh();
  prefs.setStyleInHand('tidewater-georgian');
  assert.equal(prefs.get().styleInHand, 'tidewater-georgian');
  prefs.setStyleInHand(12);
  assert.equal(prefs.get().styleInHand, 'tidewater-georgian', 'a number does not clear it');
  prefs.setStyleInHand({ id: 'x' });
  assert.equal(prefs.get().styleInHand, 'tidewater-georgian');
  prefs.setStyleInHand(null);
  assert.equal(prefs.get().styleInHand, null, 'null is the one way to forget it');
});

test('seen is remembered, per key, and persisted under the one key', async () => {
  const { prefs, store } = await fresh();
  assert.equal(prefs.isSeen('front-door'), false);
  prefs.markSeen('front-door');
  assert.equal(prefs.isSeen('front-door'), true);
  assert.equal(prefs.isSeen('head:surface-glossary'), false);
  assert.deepEqual([...store.map.keys()], [KEY]);
  const writes = store.writes();
  prefs.markSeen('front-door');
  assert.equal(store.writes(), writes, 'marking what is already seen writes nothing');
  // and a second instance reading the same storage sees it
  const again = await import(`./state/prefs.js?case=${seq += 1}`);
  assert.equal(again.prefs.isSeen('front-door'), true);
});

test('a fold has three answers: open, closed, and never chosen', async () => {
  const { prefs } = await fresh();
  assert.equal(prefs.fold('head:surface-glossary'), undefined);
  prefs.setFold('head:surface-glossary', false);
  assert.equal(prefs.fold('head:surface-glossary'), false);
  prefs.setFold('head:surface-glossary', true);
  assert.equal(prefs.fold('head:surface-glossary'), true);
  prefs.setFold('head:surface-glossary', 'yes');
  assert.equal(prefs.fold('head:surface-glossary'), true, 'a non-boolean is refused');
  assert.equal(prefs.fold('toString'), undefined, 'an inherited name is not a stored fold');
});

test('subscribers hear a change and stop hearing once they leave', async () => {
  const { prefs } = await fresh();
  let heard = 0;
  const off = prefs.subscribe(() => { heard += 1; });
  prefs.markSeen('front-door');
  assert.equal(heard, 1);
  off();
  prefs.markSeen('head:x');
  assert.equal(heard, 1);
  assert.ok(Object.isFrozen(prefs.get()), 'the snapshot is frozen');
});

test('the disclosure rule: the reader’s choice outranks the first visit, and neither is guessed', async () => {
  const { disclosureOpen } = await fresh();
  assert.equal(disclosureOpen(undefined, true), true, 'first visit, never chosen: open');
  assert.equal(disclosureOpen(undefined, false), false, 'a later visit, never chosen: folded');
  assert.equal(disclosureOpen(false, true), false, 'the reader folded it: folded, even first time');
  assert.equal(disclosureOpen(true, false), true, 'the reader opened it: open');
});

test('the store imports nothing and reads no address: nothing in it can enter the URL', () => {
  /* PRD §I.10: "Nothing in it enters the URL or useFilters." The cheapest way that could break
     is this module learning about the router, the nav store or the filters, so its source is
     held to importing nothing at all. */
  const src = readFileSync(new URL('state/prefs.js', import.meta.url), 'utf8')
    .replace(/\/\*[\s\S]*?\*\//g, '').replace(/^\s*\/\/.*$/gm, '');
  assert.doesNotMatch(src, /^\s*import\b/m);
  assert.doesNotMatch(src, /\blocation\b|\bhistory\b|useFilters|router|\bnav\b/);
  assert.match(src, /const KEY = 'tdl-workbench-prefs'/, 'the key is the PRD’s, spelled once');
});
