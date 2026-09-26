/* COMPARE, A PLACE WITH AN ADDRESS AND NO CITATION (WP-14.26, tranche 2 PRD §B.1, §B.2, §B.4, §C.7).

   `#/compare/<a>/<b>[/<section>]` is two styles side by side. This file holds the place to every
   table that names it -- the router, the citation grammar's inverse, the site map, the trail and the
   shell -- and holds `compare/view.js`'s decisions, which the page draws and does not re-make.
   Read with `node:fs` and nothing else: the glossary from `glossary/*.json`, the style names from
   `styles/*.json`, the JSX as text. No count is typed here.

   The subjects:
   - the address parses and formats, section and all, and `compare` is the LAST selection key;
   - `citeFor` answers null for every compare place, and no regex learned a two-style kind;
   - the place stands under Find a style: its rail item is current there, its trail is
     Styles > <a> > compare with <b>, and its page head is the `surface-compare` record;
   - the page's words are records that exist, and its `try` example opens a dossier, whose head
     carries the way in;
   - the family tree's shift-click goes to the address and no longer holds a comparison itself;
   - the page reads its kit rows from `/api/compare` and from nowhere else. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { parseHash, formatHash, SURFACE_PATHS, SELECTION_KEYS } from './router.js';
import { citeFor, routeCite, DOSSIER_SECTIONS } from './citations.js';
import { UNDER, navModel, flatItems, headTermFor } from './nav/navModel.js';
import { crumbsFor, crumbLabel } from './nav/crumbs.js';
import { indexTerms } from './glossary/lookup.js';
import {
  COMPARE_SECTIONS, compareSectionOf, compareSectionHref, kitGroups, authorOf, stylesOf,
} from './compare/view.js';

const ROOT = new URL('../../../', import.meta.url);
const SRC = new URL('./', import.meta.url);
const read = (rel) => JSON.parse(readFileSync(new URL(rel, ROOT), 'utf8'));
const text = (rel) => readFileSync(new URL(rel, SRC), 'utf8');
const RECS = readdirSync(new URL('glossary/', ROOT)).filter((f) => f.endsWith('.json')).sort()
  .map((f) => read(`glossary/${f}`));
const TERMS = new Map(RECS.map((r) => [r.id, r]));
const LOOKUP = indexTerms({ terms: RECS, count: RECS.length });
const NODES = readdirSync(new URL('styles/', ROOT)).filter((f) => f.endsWith('.json')).sort()
  .map((f) => read(`styles/${f}`));
const NODE = new Map(NODES.map((n) => [n.id, n]));
const NAMES = NODES.map((n) => ({ cite: `style:${n.id}`, kind: 'style', id: n.id, name: n.name }));
const [A, B] = ['craftsman', 'tidewater-georgian'];
const at = (hash) => { const p = parseHash(hash); return { surface: p.surface, selection: p.selection }; };
/* Live source: comments removed, so a sentence ABOUT a thing is not the thing. */
const live = (s) => s.replace(/\/\*[\s\S]*?\*\//g, '').replace(/^\s*\/\/.*$/gm, '');

test('the premise: the two styles this file compares are in the corpus', () => {
  assert.ok(NODE.has(A) && NODE.has(B), 'COULD NOT EVALUATE without the two style records');
});

// ── the router ──────────────────────────────────────────────────────────────────────────────
test('the address parses and formats, section and all', () => {
  assert.deepEqual(SURFACE_PATHS.compare, { path: 'compare', keys: ['style', 'compare', 'section'] });
  for (const section of [undefined, ...COMPARE_SECTIONS.filter((s) => s !== 'identify')]) {
    const sel = section ? { style: A, compare: B, section } : { style: A, compare: B };
    const hash = formatHash('compare', sel, {});
    assert.equal(hash, `#/compare/${A}/${B}` + (section ? `/${section}` : ''));
    const p = parseHash(hash);
    assert.equal(p.surface, 'compare');
    assert.deepEqual(p.selection, sel);
  }
  // one style, or none: the address says so and names nothing it was not given
  assert.deepEqual(parseHash(`#/compare/${A}`).selection, { style: A });
  assert.deepEqual(parseHash('#/compare').selection, {});
  assert.equal(formatHash('compare', { compare: B }, {}), `#/compare/-/${B}`);
});

test('compare is the LAST selection key, appended and never inserted', () => {
  assert.equal(SELECTION_KEYS[SELECTION_KEYS.length - 1], 'compare');
  // off its own surface it travels in the query, as every selection key does
  assert.equal(parseHash(`#/phylogeny?compare=${B}`).selection.compare, B);
});

// ── the citation grammar ────────────────────────────────────────────────────────────────────
test('a compare place has no citation, and the grammar gained no two-style kind', () => {
  for (const section of [undefined, ...COMPARE_SECTIONS]) {
    assert.equal(citeFor('compare', { style: A, compare: B, section }), null, String(section));
  }
  assert.equal(citeFor('compare', { style: A }), null);
  assert.equal(citeFor('compare', {}), null);
  // the explicit case, not a fall-through: a reader finds the decision where it is made
  assert.match(live(text('citations.js')), /case 'compare': return null;/);
  // no citation routes to the compare surface
  for (const ref of [`style:${A}`, `compare:${A}`, `compare:${A}/${B}`, `style:${A}#compare`]) {
    const t = routeCite(ref);
    assert.ok(!t || t.surface !== 'compare', `${ref} routes to compare`);
  }
});

// ── the site map, the trail, the head ───────────────────────────────────────────────────────
test('compare stands under Find a style, whose rail item is current there', () => {
  assert.equal(UNDER.compare, 'style');
  const items = flatItems(navModel({ lookup: LOOKUP, place: at(`#/compare/${A}/${B}`) }));
  const current = items.filter((it) => it.current).map((it) => it.id);
  assert.deepEqual(current, ['style'], `current on compare: ${current}`);
  // and the style item is NOT current on some other surface for the same reason
  const elsewhere = flatItems(navModel({ lookup: LOOKUP, place: at('#/faults') }));
  assert.ok(!elsewhere.find((it) => it.id === 'style').current);
});

test('the trail is Styles > <a> > compare with <b>, every word a record\'s', () => {
  const cs = crumbsFor(at(`#/compare/${A}/${B}/kit`), { lookup: LOOKUP, names: NAMES, styles: NODES });
  assert.deepEqual(cs.map(crumbLabel), [
    TERMS.get('nav-group-styles').term,
    NODE.get(A).name,
    `${TERMS.get('compare-with').term} ${NODE.get(B).name}`,
  ]);
  assert.equal(cs[1].href, formatHash('style', { style: A }, {}), 'the first style is a link to its dossier');
  assert.equal(cs[1].cite, `style:${A}`);
  assert.equal(cs[2].href, null, 'the place itself is not a link');
  assert.equal(cs[2].cite, `style:${B}`);
  // one style only: the trail ends at the word, and names no second style it was not given
  const one = crumbsFor(at(`#/compare/${A}`), { lookup: LOOKUP, names: NAMES, styles: NODES });
  assert.deepEqual(one.map(crumbLabel), [TERMS.get('nav-group-styles').term, NODE.get(A).name,
    TERMS.get('compare-with').term]);
});

test('the page head is the surface-compare record, whose try opens a dossier that has the way in', () => {
  assert.equal(headTermFor(at(`#/compare/${A}/${B}`)), 'surface-compare');
  const rec = TERMS.get('surface-compare');
  assert.ok(rec && rec.surface && rec.surface.try, 'surface-compare carries no try');
  const t = routeCite(rec.surface.try);
  assert.ok(t && t.surface === 'style' && t.selection.style, `the try lands on ${JSON.stringify(t)}`);
  assert.match(live(text('surfaces/StyleDossier.jsx')), /<CompareWith styleId=\{styleId\} \/>/,
    'the dossier head no longer offers the way in');
  assert.match(live(text('surfaces/StyleDossier.jsx')), /nav\.go\('compare', \{ style: styleId, compare: other \}\)/);
});

test('every word the page and its way in use is a record that exists', () => {
  const ids = new Set();
  for (const f of ['surfaces/Compare.jsx', 'surfaces/StyleDossier.jsx', 'nav/crumbs.js']) {
    for (const m of live(text(f)).matchAll(/<Term id="([^"]+)"/g)) ids.add(m[1]);
    for (const m of live(text(f)).matchAll(/\{ id: '([^']+)' \}/g)) ids.add(m[1]);
    for (const m of live(text(f)).matchAll(/wordFor\(lookup, '([^']+)'\)/g)) ids.add(m[1]);
  }
  for (const s of COMPARE_SECTIONS) ids.add(`section-${s}`);
  assert.ok(ids.has('compare-with') && ids.has('kit-same-answer') && ids.has('shared-ancestry'),
    `the reader matched too little: ${[...ids]}`);
  const missing = [...ids].filter((id) => !TERMS.has(id));
  assert.deepEqual(missing, [], `words with no record: ${missing}`);
  assert.ok(COMPARE_SECTIONS.every((s) => DOSSIER_SECTIONS.includes(s)));
});

// ── compare/view.js ─────────────────────────────────────────────────────────────────────────
test('the section in view is the named compare section, and Identify otherwise', () => {
  for (const s of COMPARE_SECTIONS) assert.equal(compareSectionOf({ section: s }), s);
  assert.equal(compareSectionOf({}), 'identify');
  assert.equal(compareSectionOf({ section: 'rules' }), 'identify', 'a dossier section compare does not draw');
  assert.equal(compareSectionOf(null), 'identify');
  assert.equal(compareSectionHref(A, B, 'identify'), `#/compare/${A}/${B}`);
  assert.equal(compareSectionHref(A, B, 'plans'), `#/compare/${A}/${B}/plans`);
  assert.deepEqual(stylesOf({ style: A, compare: B }), { a: A, b: B });
  assert.deepEqual(stylesOf({ style: ' ', compare: null }), { a: null, b: null });
});

test('the kit rows split on the payload\'s own differs_on, every row in exactly one group', () => {
  const rows = [
    { slot: 's1', differs_on: ['binding', 'source'] },
    { slot: 's2', differs_on: ['source'] },
    { slot: 's3', differs_on: ['canonical'] },
    { slot: 's4', differs_on: ['forbidden', 'source'] },
  ];
  const g = kitGroups({ rows });
  assert.deepEqual(g.answer.map((r) => r.slot), ['s1', 's3', 's4']);
  assert.deepEqual(g.source.map((r) => r.slot), ['s2']);
  assert.equal(g.answer.length + g.source.length, rows.length);
  assert.deepEqual(kitGroups(null), { answer: [], source: [] });
});

test('a disambiguation is credited to the style whose record wrote it', () => {
  assert.equal(authorOf({ node: B }, A, B), A);
  assert.equal(authorOf({ node: A }, A, B), B);
  assert.equal(authorOf({ node: 'someone-else' }, A, B), null);
  // against the corpus: craftsman's record names prairie-school, and prairie-school's names craftsman
  const cr = (NODE.get('craftsman').distinguished_from || []).find((d) => d.node === 'prairie-school');
  assert.ok(cr, 'premise: craftsman distinguishes itself from prairie-school');
  assert.equal(authorOf(cr, 'craftsman', 'prairie-school'), 'craftsman');
});

// ── the family tree, and where the page reads its rows ──────────────────────────────────────
test('the family tree sends a shift-click to the address and holds no comparison itself', () => {
  const s = live(text('surfaces/Phylogeny.jsx'));
  assert.match(s, /if \(ev\.shiftKey\) \{ if \(id !== sel\) nav\.go\('compare', \{ style: sel, compare: id \}\); \}/);
  assert.doesNotMatch(s, /compareStyles|cmpData|setCompare|JSON\.stringify/, 'the panel comparison is back');
  assert.doesNotMatch(s, /compare=\{/, 'the map is still handed a comparison');
});

test('the page reads its rows from /api/compare and from no kit of its own', () => {
  const s = live(text('surfaces/Compare.jsx'));
  assert.match(s, /api\.compare\(a, b\)/);
  assert.doesNotMatch(s, /api\.(kit|kitSlot|cascade|compareStyles|stylePacks|styleDossier)\(/,
    'the page fetches a second reading of something the compare payload already carries');
  assert.match(s, /data-kit-rows=\{\(payload\.kit\.rows \|\| \[\]\)\.length\}/, 'the row count is not the payload\'s');
  assert.match(text('api/client.js'), /compare: \(a, b\) => getJSON\(`\/api\/compare\/\$\{seg\(a\)\}\/\$\{seg\(b\)\}`\)/);
});
