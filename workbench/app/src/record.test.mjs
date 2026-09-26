/* THE RECORD PAGES, HELD TO ONE TABLE (WP-14.23, tranche 2 PRD §B, §C.6).

   `record/kinds.js` says which kinds of record have a page, which surface shows each, which
   selection key names the record there, which citation kind names it and which glossary record
   says what it is. Five other places carry their half of those facts, each in its own form: the
   router (`SURFACE_PATHS`), the citation grammar (`routeCite` and its inverse `citeFor`), the site
   map (`navModel.UNDER`), the trail (`crumbsFor`) and the shell's surface table in `App.jsx`. This
   file holds every one of them to the table, so a kind added in one place and not the others
   fails here rather than on screen.

   Read with `node:fs` and nothing else: the glossary from `glossary/*.json`, a record of each
   kind from its own corpus file, and `App.jsx` as text, because it is JSX and not importable
   here. The subjects:
   - a citation of each kind lands on its own page, and the page cites it back;
   - each kind's page is a routed surface, and the shell draws a component for it (an unmapped
     surface falls back to the plan bench, which is exactly where a room used to land);
   - each kind's page stands under Elements in the site map, and its trail says so;
   - each kind's glossary records exist, and the kind surface's `try` example lands on a page of
     that kind (§A.2);
   - the retired "searched" card is gone and nothing names it. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, existsSync, statSync } from 'node:fs';
import { PAGE_KINDS, RECORD_KINDS, SLOT_KIND, kindOfSurface, kindOfCite, recordIdOf } from './record/kinds.js';
import { routeCite, citeFor } from './citations.js';
import { SURFACE_PATHS, parseHash, formatHash, hrefFor } from './router.js';
import { UNDER } from './nav/navModel.js';
import { crumbsFor } from './nav/crumbs.js';
import { indexTerms } from './glossary/lookup.js';

const ROOT = new URL('../../../', import.meta.url);
const SRC = new URL('./', import.meta.url);
const read = (rel) => JSON.parse(readFileSync(new URL(rel, ROOT), 'utf8'));
const dir = (rel) => (existsSync(new URL(rel, ROOT))
  ? readdirSync(new URL(rel, ROOT)).filter((f) => f.endsWith('.json')).sort() : []);
const RECS = dir('glossary/').map((f) => read(`glossary/${f}`));
const BY_ID = new Map(RECS.map((r) => [r.id, r]));
const LOOKUP = indexTerms({ terms: RECS, count: RECS.length });

const SLOT_IDS = read('elements/slots.json').groups.flatMap((g) => g.slots).map((s) => s.id);

/* One real record of each kind, read from its own corpus file -- the first by id, so the choice
   is the corpus's order and not a name typed here. */
function firstId(kind) {
  if (kind.cite === 'slot') {
    return SLOT_IDS.slice().sort()[0];
  }
  if (kind.cite === 'massing') {
    const cat = read('massings/catalog.json');
    return (Array.isArray(cat) ? cat : cat.massings).map((m) => m.id).sort()[0];
  }
  const folder = { room: 'rooms/', grouping: 'groupings/', parti: 'partis/' }[kind.cite];
  return read(folder + dir(folder)[0]).id;
}
const SPECIMENS = PAGE_KINDS.map((k) => [k, firstId(k)]);

test('the table is the five kinds tranche 2 names, and every row is complete', () => {
  assert.deepEqual(PAGE_KINDS.map((k) => k.cite).sort(), ['grouping', 'massing', 'parti', 'room', 'slot']);
  assert.equal(PAGE_KINDS[0], SLOT_KIND);
  assert.deepEqual(PAGE_KINDS.slice(1), RECORD_KINDS);
  for (const k of PAGE_KINDS) {
    for (const f of ['surface', 'key', 'cite', 'termId']) assert.ok(k[f], `${k.cite}: no ${f}`);
    assert.equal(kindOfSurface(k.surface), k);
    assert.equal(kindOfCite(k.cite), k);
  }
  assert.equal(new Set(PAGE_KINDS.map((k) => k.surface)).size, PAGE_KINDS.length, 'two kinds share a surface');
  assert.ok(Object.isFrozen(PAGE_KINDS) && PAGE_KINDS.every(Object.isFrozen));
});

test('every specimen was read from the corpus (the premise of the tests below)', () => {
  for (const [k, id] of SPECIMENS) assert.ok(typeof id === 'string' && id.length > 0, `no ${k.cite} record read`);
});

test('a citation of each kind lands on its own page, holding that record, and cites it back', () => {
  for (const [k, id] of SPECIMENS) {
    const cite = `${k.cite}:${id}`;
    const t = routeCite(cite);
    assert.deepEqual(t, { surface: k.surface, selection: { [k.key]: id } },
      `${cite} lands on ${JSON.stringify(t)} and not on its record page`);
    assert.equal(citeFor(k.surface, { [k.key]: id }, {}), cite, `the ${k.surface} page does not cite ${cite}`);
    const href = hrefFor(cite);
    assert.equal(parseHash(href).surface, k.surface, href);
    assert.equal(recordIdOf(k, parseHash(href).selection), id, `${href} does not hold ${id}`);
    // the bare page is the kind's index, which names no record
    assert.equal(recordIdOf(k, parseHash(formatHash(k.surface, {}, {})).selection), null);
    assert.equal(citeFor(k.surface, {}, {}), null, `the bare ${k.surface} index cites a record`);
  }
});

test('each kind\'s page is a routed surface keyed by the kind\'s own selection key', () => {
  for (const k of PAGE_KINDS) {
    assert.ok(SURFACE_PATHS[k.surface], `${k.surface} is not a routed surface`);
    assert.deepEqual(SURFACE_PATHS[k.surface].keys, [k.key], k.surface);
  }
});

/* `App.jsx` draws `SURFACES[surface] || SURFACES.workbench`, so a routed surface the table omits
   is drawn as the PLAN BENCH -- a room record's URL showing an empty bench, which is the defect
   tranche 2 retires. Read as text because JSX is not importable under `node --test`: the keys of
   the one object literal, and nothing else in the file. */
test('the shell draws a surface for every routed surface, so none falls back to the bench', () => {
  const src = readFileSync(new URL('App.jsx', SRC), 'utf8');
  const m = /const SURFACES = \{([\s\S]*?)\n\};/.exec(src);
  assert.ok(m, 'App.jsx has no SURFACES table to read');
  const keys = [...m[1].matchAll(/^\s*([a-z]+):\s*[A-Za-z]+,?\s*$/gm)].map((x) => x[1]);
  assert.ok(keys.includes('workbench'), 'the reader matched nothing: the table\'s shape moved');
  const missing = Object.keys(SURFACE_PATHS).filter((s) => !keys.includes(s));
  assert.deepEqual(missing, [], `routed and not drawn (they would show the bench): ${missing.join(', ')}`);
});

test('the four plan-type pages stand under Elements, and the slot page IS Elements', () => {
  assert.equal(SLOT_KIND.surface, 'elements');
  // Compare stands under Find a style (WP-14.26), not Elements; every page that stands under
  // Elements is a record kind, and every record kind stands there.
  const underElements = Object.keys(UNDER).filter((s) => UNDER[s] === 'elements');
  assert.deepEqual(underElements.sort(), RECORD_KINDS.map((k) => k.surface).sort());
  for (const k of RECORD_KINDS) assert.equal(UNDER[k.surface], 'elements', k.surface);
});

test('each kind\'s trail runs through Elements and ends at the record, which is not a link', () => {
  const names = SPECIMENS.map(([k, id]) => ({ cite: `${k.cite}:${id}`, kind: k.cite, id, name: `the ${k.cite} ${id}` }));
  for (const [k, id] of SPECIMENS) {
    const cs = crumbsFor(parseHash(hrefFor(`${k.cite}:${id}`)), { lookup: LOOKUP, names });
    assert.ok(cs.some((c) => c.termId === 'surface-elements'), `${k.cite}: no Elements crumb`);
    const last = cs[cs.length - 1];
    assert.equal(last.cite, `${k.cite}:${id}`, `${k.cite}: the trail does not end at the record`);
    assert.equal(last.href, null);
  }
});

test('each kind names glossary records that exist: its surface\'s and its own word', () => {
  for (const k of PAGE_KINDS) {
    const surf = BY_ID.get(`surface-${k.surface}`);
    assert.ok(surf, `no glossary record surface-${k.surface}`);
    assert.equal(surf.family, 'surface', k.surface);
    assert.ok(BY_ID.get(k.termId), `no glossary record ${k.termId}`);
  }
  assert.ok(BY_ID.get('surface-elements'));
});

/* §A.2: a kind surface's record carries a `try` -- one real record to open -- and it must land on
   a page of THAT kind, holding a record the corpus has. A `try` pointing at the bench, or at a
   record deleted since, would be the page's own example leading nowhere. */
test('each kind surface\'s example lands on a page of its own kind, at a record the corpus holds', () => {
  const held = {
    slot: new Set(SLOT_IDS),
    room: new Set(dir('rooms/').map((f) => read(`rooms/${f}`).id)),
    grouping: new Set(dir('groupings/').map((f) => read(`groupings/${f}`).id)),
    parti: new Set(dir('partis/').map((f) => read(`partis/${f}`).id)),
    massing: new Set((() => { const c = read('massings/catalog.json'); return (Array.isArray(c) ? c : c.massings).map((m) => m.id); })()),
  };
  for (const k of PAGE_KINDS) {
    const eg = BY_ID.get(`surface-${k.surface}`).surface?.try;
    assert.ok(typeof eg === 'string' && eg, `surface-${k.surface} carries no try`);
    const t = routeCite(eg);
    assert.equal(t && t.surface, k.surface, `surface-${k.surface}'s try (${eg}) lands on ${t && t.surface}`);
    assert.ok(held[k.cite].has(t.selection[k.key]), `surface-${k.surface}'s try names ${eg}, which the corpus does not hold`);
  }
});

/* The "searched" card (`components/Spotlight.jsx`) acknowledged a record the surface under it could
   not show. Every record it was drawn for has a page now, so it is DELETED, and nothing may name it:
   a restored call site would draw a card saying "this surface does not hold the record" over the
   one surface that does. Walked over `src/` by name, the tests excepted (this file names it). */
test('the searched card is retired: no component file, no import, no call site', () => {
  assert.ok(!existsSync(new URL('components/Spotlight.jsx', SRC)), 'components/Spotlight.jsx is back');
  const offenders = [];
  const walk = (u) => {
    for (const f of readdirSync(u).sort()) {
      const p = new URL(f, u);
      if (statSync(p).isDirectory()) { walk(new URL(f + '/', u)); continue; }
      if (!/\.(jsx?|mjs)$/.test(f) || /\.test\.mjs$/.test(f)) continue;
      if (/\bSpotlight\b/.test(readFileSync(p, 'utf8'))) offenders.push(p.pathname.slice(SRC.pathname.length));
    }
  };
  walk(SRC);
  assert.deepEqual(offenders, [], `the searched card is named in: ${offenders.join(', ')}`);
});

/* A PARTI'S `note` IS FOR MAINTAINERS AND THE PAGE DOES NOT SHOW IT (WP-14.33, R6 of 26 Sep 2026).
   The parti schema's own description says so and nothing held it (WP-14.33's audit): `/api/partis`
   serves the record whole, so the day `PartiBody` reads `p.note` the build history R6 moved out of
   the description is on the page again. Read as source, the way this file reads `App.jsx`: the
   parti the page draws is `p` (`rec.parti`), and `scaling.note` -- the record's statement of how
   the plan grows -- is a different field the page is meant to show. */
test('the parti page reads no top-level `note` from the record it draws', () => {
  const src = readFileSync(new URL('./record/PartiBody.jsx', import.meta.url), 'utf8')
    .replace(/\/\*[\s\S]*?\*\//g, ' ').replace(/(^|[^:'"`])\/\/[^\n]*/g, '$1');
  assert.match(src, /const p = rec\.parti/, 'the premise: the page names the parti `p`');
  assert.match(src, /scaling\.note/, 'the premise: the growth note is read, so a read of `note` is visible');
  for (const shape of [/\bp\s*\??\.\s*note\b/, /\brec\.parti\s*\??\.\s*note\b/, /\bp\s*\[\s*['"]note['"]\s*\]/,
    /\{[^}=]*\bnote\b[^}=]*\}\s*=\s*(?:p|rec\.parti)\b/]) {
    assert.doesNotMatch(src, shape, `PartiBody reads the parti's maintainer note (${shape})`);
  }
});
