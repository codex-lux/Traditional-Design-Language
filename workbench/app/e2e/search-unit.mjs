/* The matcher, on node, with no DOM:  node e2e/search-unit.mjs

   What is pinned here is mostly the ORDER. A palette that finds the right thing and puts
   it fourth is a palette people stop using, so the ranking ladder is asserted with real
   corpus-shaped names rather than left to whatever sort happened to be stable. */

import assert from 'node:assert/strict';
import { score, search, matches, SCORE, KIND_ORDER } from '../src/search/match.js';
import { STATIC_ENTRIES, SURFACE_ENTRIES } from '../src/search/staticEntries.js';

let checks = 0;
const ok = (fn) => { fn(); checks += 1; };

const E = (kind, id, name, hay) => ({ kind, id, name, cite: `${kind}:${id}`, hay: (hay || `${name} ${id}`).toLowerCase() });

/* ── the ladder ────────────────────────────────────────────────────────────────── */

ok(() => {
  const e = E('style', 'tidewater-georgian', 'Tidewater Georgian', 'tidewater georgian tidewater-georgian virginia');
  assert.equal(score(e, 'Tidewater Georgian'), SCORE.NAME_EXACT);
  assert.equal(score(e, 'tidewater-georgian'), SCORE.NAME_EXACT);   // the id, exactly
  assert.equal(score(e, 'tide'), SCORE.NAME_PREFIX);
  assert.equal(score(e, 'georgian'), SCORE.NAME_CONTAINS);
  assert.equal(score(e, 'virginia'), SCORE.HAY);
  assert.equal(score(e, 'gothic'), 0);
  assert.equal(score(e, ''), 0);
});

/* An id prefix outranks a name that merely contains the word: typing the start of an id
   is deliberate, finding a word buried in a name is a coincidence. */
ok(() => {
  const byId = E('pack', 'brick-course', 'The Brick Course', 'the brick course brick-course');
  assert.equal(score(byId, 'brick-c'), SCORE.ID_PREFIX);
});

/* ── ranking ───────────────────────────────────────────────────────────────────── */

ok(() => {
  const pool = [
    E('fault', 'georgian-window-wrong', 'A Georgian window in the wrong wall'),
    E('style', 'georgian-colonial-american', 'Georgian Colonial (American)'),
    E('style', 'georgian', 'Georgian'),
    E('style', 'tidewater-georgian', 'Tidewater Georgian'),
  ];
  const { hits } = search(pool, 'georgian');
  assert.equal(hits[0].id, 'georgian', 'the exact name must come first');
  assert.equal(hits[1].id, 'georgian-colonial-american', 'then the name that starts with it');
  // The fault beats Tidewater Georgian here, and should: its ID starts with the word,
  // where Tidewater only contains it. The ladder outranks the kind, deliberately —
  // kind is a tie-break, not a thumb on the scale.
  assert.equal(hits[2].id, 'georgian-window-wrong');
  assert.equal(hits[3].id, 'tidewater-georgian');
});

/* Kind breaks an actual tie: same rung of the ladder, same name length. */
ok(() => {
  const pool = [
    E('fault', 'cape-thing', 'Cape thing'),
    E('style', 'cape-thing', 'Cape thing'),
  ];
  const { hits } = search(pool, 'cape');
  assert.equal(hits[0].kind, 'style', 'a style should come before a fault at an equal score');
});

/* The shorter of two equally-scored names first — it is the more likely target. */
ok(() => {
  const pool = [
    E('room', 'dining-room-formal', 'Dining Room, Formal and Separate'),
    E('room', 'dining-room', 'Dining Room'),
  ];
  assert.equal(search(pool, 'dining').hits[0].id, 'dining-room');
});

/* Every kind the palette can show has a place in the order, or ties sort arbitrarily. */
ok(() => {
  ['surface', 'action', 'style', 'slot', 'pack', 'fault', 'room', 'massing', 'parti', 'grouping']
    .forEach((k) => assert.ok(KIND_ORDER.includes(k), `${k} has no rank`));
});

/* ── words in any order, but all of them ───────────────────────────────────────── */

ok(() => {
  const e = E('style', 'tidewater-georgian', 'Tidewater Georgian');
  assert.ok(score(e, 'georgian tidewater') > 0, 'half-remembered order should still find it');
  assert.equal(score(e, 'tidewater gothic'), 0, 'a word that is not there means no match');
});

/* ── the cut is reported, never silent ─────────────────────────────────────────── */

ok(() => {
  const pool = Array.from({ length: 50 }, (_, i) => E('fault', `f-${i}`, `Fault number ${i}`));
  const r = search(pool, 'fault', 10);
  assert.equal(r.hits.length, 10);
  assert.equal(r.total, 50);
  assert.equal(r.cut, 40, 'the palette must be able to say how many it did not show');
});

ok(() => {
  const r = search([], 'anything');
  assert.deepEqual(r, { hits: [], total: 0, cut: 0 });
  assert.deepEqual(search(null, 'x').hits, []);
  assert.deepEqual(search([E('style', 'a', 'A')], '  ').hits, []);
});

/* ── matches(), for filtering a list already on screen ─────────────────────────── */

ok(() => {
  const row = { id: 'roof_pitch', group: 'massing-and-roof', name: 'Roof pitch', aka: ['slope', 'rake'] };
  assert.ok(matches(row, 'roof', ['id', 'name']));
  assert.ok(matches(row, 'massing', ['group']));
  assert.ok(matches(row, 'slope', ['aka']), 'array fields should be searched');
  assert.ok(matches(row, 'roof massing', ['name', 'group']), 'all words, any field');
  assert.ok(!matches(row, 'cornice', ['id', 'name']));
  assert.ok(matches(row, '', ['id']), 'an empty filter shows everything');
  assert.ok(matches(row, 'pitch', [(r) => r.name]), 'a function field');
  assert.ok(!matches(row, 'x', []), 'no fields means nothing to match');
});

/* ── the static entries earn their synonyms ────────────────────────────────────── */

/* This is the whole reason the file exists: the words a newcomer types are not the words
   on the rail. If these stop matching, the palette silently becomes an index of labels. */
ok(() => {
  const wanted = [
    ['mistakes', 'faults'], ['errors', 'faults'], ['solecisms', 'faults'],
    ['ancestry', 'phylogeny'], ['origins', 'phylogeny'], ['map', 'phylogeny'],
    ['download', 'export'], ['dxf', 'export'], ['cad', 'export'],
    ['start', 'brief'], ['requirements', 'brief'],
    ['floor plan', 'workbench'], ['layout', 'workbench'],
    ['import', 'transcription'], ['trace', 'transcription'],
    ['ratios', 'proportions'], ['orders', 'proportions'],
    ['elements', 'kit'], ['bindings', 'kit'],
    ['sheets', 'drawings'], ['elevation', 'drawings'],
    ['options', 'candidates'],
    ['shortcuts', 'help'], ['keyboard', 'help'],
  ];
  wanted.forEach(([typed, id]) => {
    const { hits } = search(STATIC_ENTRIES, typed);
    assert.ok(hits.some((h) => h.id === id),
      `typing "${typed}" should offer ${id}; it offered ${hits.map((h) => h.id).join(', ') || 'nothing'}`);
  });
});

/* Every surface entry names a surface, and every action names a handler. */
ok(() => {
  SURFACE_ENTRIES.forEach((e) => {
    assert.equal(e.kind, 'surface');
    assert.ok(e.surface, `${e.id} has no surface to go to`);
    // Typing the label on the rail must find the surface it labels. Asserted through
    // search() rather than against the haystack, because the name is matched directly:
    // "Details & Export" is findable without the ampersand ever being indexed.
    const { hits } = search(STATIC_ENTRIES, e.name);
    assert.equal(hits[0] && hits[0].id, e.id, `typing "${e.name}" should offer ${e.id} first`);
  });
  STATIC_ENTRIES.filter((e) => e.kind === 'action')
    .forEach((e) => assert.ok(e.run, `${e.id} has no action to run`));
});

/* A static entry must never carry a cite it cannot honour — the palette dispatches on
   cite first, and a wrong one would navigate somewhere unrelated. */
ok(() => {
  STATIC_ENTRIES.forEach((e) => assert.ok(!e.cite, `${e.id} should not carry a citation`));
});

console.log(`search-unit: ${checks} checks passed`);
