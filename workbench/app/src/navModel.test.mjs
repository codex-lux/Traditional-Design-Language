/* THE SITE MAP, HELD TO THE RECORDS IT NAMES AND THE CONTRACT IT IS (WP-14.13, PRD §F).

   `nav/navModel.js` is the one account of the workbench's places. Every word it hands the rail is
   a glossary record's, read here from `glossary/*.json` with `node:fs` alone — no fetch, no
   server, no React — so a label that stopped being its record's word, a record the table names
   and the corpus does not hold, or a figure typed into the module instead of passed from the API
   fails here rather than on screen.

   The subjects, each a way the map could lie to a reader:
   - a rail label that is not its record's `term` (the app writing a word);
   - a missing record printed as nothing, or as a guess, instead of named;
   - a link that does not reach its own surface, or carries more than it names;
   - a step number written down rather than read off the journey's order;
   - a count written into the module rather than taken from the API;
   - the in-hand style's sections listed under a page that is not its dossier;
   - two items marked as "you are here" at once. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import {
  NAV, navModel, headTermFor, guidedExampleStyle, inHandFrom, flatItems, normalizePlace, wordFor,
} from './nav/navModel.js';
import { indexTerms } from './glossary/lookup.js';
import { JOURNEY, journeyState } from './journey/journey.js';
import { parseHash, formatHash, SURFACE_PATHS } from './router.js';
import { DOSSIER_SECTIONS } from './citations.js';

const ROOT = new URL('../../../', import.meta.url);
const GLOSSARY = new URL('glossary/', ROOT);

function records() {
  const files = existsSync(GLOSSARY)
    ? readdirSync(GLOSSARY).filter((f) => f.endsWith('.json')).sort() : [];
  return files.map((f) => JSON.parse(readFileSync(new URL(f, GLOSSARY), 'utf8')));
}
const RECS = records();
const BY_ID = new Map(RECS.map((r) => [r.id, r]));
const LOOKUP = indexTerms({ terms: RECS, count: RECS.length });
const without = (...ids) => indexTerms({ terms: RECS.filter((r) => !ids.includes(r.id)) });
const TERM = (id) => BY_ID.get(id).term;

const STYLES = new URL('styles/', ROOT);
const styleName = (id) => JSON.parse(readFileSync(new URL(`${id}.json`, STYLES), 'utf8')).name;

const at = (hash) => {
  const p = parseHash(hash);
  return { surface: p.surface, selection: p.selection };
};
const byId = (model, id) => flatItems(model).find((it) => it.id === id);

test('the premise: the records the map names are on this tree', () => {
  assert.ok(RECS.length > 0, 'COULD NOT EVALUATE without glossary/*.json — and a map with no words is not a pass');
});

test('the groups and items are §F.1’s, in order, and every record they name exists', () => {
  assert.deepEqual(NAV.map((g) => g.id), ['start', 'styles', 'a-house', 'library']);
  assert.deepEqual(NAV.map((g) => g.items.map((i) => i.id)), [
    ['overview'],
    ['style', 'in-hand', 'phylogeny'],
    ['brief', 'candidates', 'workbench', 'drawings', 'export'],
    ['proportions', 'faults', 'glossary'],
  ]);
  const wb = NAV[2].items.find((i) => i.id === 'workbench');
  assert.deepEqual(wb.children.map((c) => c.id), ['transcription'], 'Trace a drawing is nested under the plan');
  for (const g of NAV) {
    assert.ok(BY_ID.has(g.termId), `${g.id}: its heading record ${g.termId} exists`);
    assert.equal(BY_ID.get(g.termId).family, 'nav-group', g.termId);
    const items = g.items.flatMap((i) => [i, ...(i.children || [])]);
    for (const it of items) {
      assert.ok(it.surface in SURFACE_PATHS, `${it.id}: ${it.surface} is a surface the router knows`);
      if (it.id === 'in-hand') { assert.equal(it.termId, null, 'the in-hand item is named by its style'); continue; }
      assert.equal(it.termId, `surface-${it.surface}`, `${it.id} is called by its own surface record`);
      assert.ok(BY_ID.has(it.termId), `${it.id}: ${it.termId} exists`);
      assert.equal(BY_ID.get(it.termId).family, 'surface', it.termId);
    }
  }
  assert.ok(Object.isFrozen(NAV) && NAV.every((g) => Object.isFrozen(g) && Object.isFrozen(g.items)));
});

test('every label is its record’s term, and a record the glossary lacks is named as missing, never guessed', () => {
  const m = navModel({ lookup: LOOKUP, place: at('#/') });
  for (const g of m.groups) {
    assert.equal(g.label, TERM(g.termId));
    assert.equal(g.missing, null);
  }
  for (const it of flatItems(m)) {
    if (it.id === 'in-hand' || !it.termId) continue;
    assert.equal(it.label, TERM(it.termId), `${it.id}'s label is ${it.termId}'s term`);
    assert.equal(it.missing, null);
  }
  const holed = navModel({ lookup: without('surface-faults', 'nav-group-library'), place: at('#/') });
  const faults = byId(holed, 'faults');
  assert.equal(faults.label, null, 'no word is made up for a record the glossary does not hold');
  assert.equal(faults.missing, 'surface-faults');
  const lib = holed.groups.find((g) => g.id === 'library');
  assert.equal(lib.label, null);
  assert.equal(lib.missing, 'nav-group-library');
  // with no glossary yet, nothing is known and nothing is claimed
  const none = navModel({ lookup: null, place: at('#/') });
  assert.ok(flatItems(none).every((it) => it.label === null && it.missing === null));
  assert.deepEqual(wordFor(null, 'surface-style'), { label: null, missing: null });
});

test('every link reaches its own surface and carries exactly what it names — nothing more', () => {
  const m = navModel({ lookup: LOOKUP, place: at('#/') });
  for (const it of flatItems(m)) {
    if (it.id === 'in-hand') continue;
    assert.equal(it.href, formatHash(it.surface, {}, {}), `${it.id} is its surface's bare address`);
    const p = parseHash(it.href);
    assert.equal(p.surface, it.surface, `${it.id} → ${it.href} reaches ${it.surface}`);
    assert.deepEqual(p.selection, {}, `${it.id} selects nothing`);
    assert.ok(!it.href.includes('?'), `${it.id}: a rail link carries no query`);
  }
  assert.equal(byId(m, 'overview').href, formatHash('overview', {}, {}));
});

test('step numbers are the journey’s order plus one, read off JOURNEY, and Trace a drawing has none', () => {
  const m = navModel({ lookup: LOOKUP, place: at('#/') });
  const house = m.groups.find((g) => g.id === 'a-house');
  for (const it of flatItems({ groups: [house] })) {
    const i = JOURNEY.findIndex((j) => j.surface === it.surface);
    assert.equal(it.step, i === -1 ? null : i + 1, `${it.id}'s step`);
  }
  assert.equal(byId(m, 'transcription').step, null);
  for (const it of flatItems(m)) {
    if (!JOURNEY.some((j) => j.surface === it.surface)) assert.equal(it.step, null, `${it.id} is not a step`);
  }
  // premise: the five steps are really numbered, so a null everywhere cannot pass
  assert.deepEqual(house.items.map((i) => i.step), [1, 2, 3, 4, 5]);
});

test('a meta is the API’s figure, whatever figure it is, and absent when the API gave none', () => {
  const place = at('#/');
  const a = navModel({ lookup: LOOKUP, place, glossaryCount: 121,
    counts: { styles: 164, faults: 210, proportion_packs: { orders: 26, systems: 20, modules: 11 } } });
  const b = navModel({ lookup: LOOKUP, place, glossaryCount: 3,
    counts: { styles: 7, faults: 11, proportion_packs: { x: 2 } } });
  assert.equal(byId(a, 'style').meta, 164);
  assert.equal(byId(a, 'faults').meta, 210);
  assert.equal(byId(a, 'proportions').meta, 57, 'the sum of the pack counts by kind');
  assert.equal(byId(a, 'glossary').meta, 121);
  // a second corpus reads as itself: a figure written into the module would not move
  assert.equal(byId(b, 'style').meta, 7);
  assert.equal(byId(b, 'faults').meta, 11);
  assert.equal(byId(b, 'proportions').meta, 2);
  assert.equal(byId(b, 'glossary').meta, 3);
  const none = navModel({ lookup: LOOKUP, place });
  for (const it of flatItems(none)) assert.equal(it.meta, null, `${it.id} states no figure it was not given`);
});

test('a house item’s meta is the journey’s own words for its step', () => {
  const journey = journeyState({ session: {}, plan: null, lastEval: null });
  const m = navModel({ lookup: LOOKUP, place: at('#/'), journey });
  for (const s of journey.steps) {
    const it = flatItems(m).find((x) => x.surface === s.surface);
    assert.equal(it.meta, s.words, `${it.id}`);
  }
  assert.equal(byId(m, 'transcription').meta, null, 'the alternate route states no step words');
  const plan = { id: 'p1', levels: [] };
  const evaluated = journeyState({ session: {}, plan,
    lastEval: { check: { plan: 'p1', counts: { fatal: 1 }, constraint_summary: { unjudged: 3 } } } });
  const m2 = navModel({ lookup: LOOKUP, place: at('#/'), journey: evaluated });
  assert.equal(byId(m2, 'workbench').meta, evaluated.steps.find((s) => s.id === 'plan').words);
  assert.notEqual(byId(m2, 'workbench').meta, byId(m, 'workbench').meta, 'the words move with the house');
});

test('the module writes no figure of its own: every numeric literal in its code is 0 or 1', () => {
  const src = readFileSync(new URL('nav/navModel.js', import.meta.url), 'utf8')
    .replace(/\/\*[\s\S]*?\*\//g, '').replace(/(^|[^:])\/\/[^\n]*/g, '$1')
    .replace(/'(?:[^'\\\n]|\\.)*'|"(?:[^"\\\n]|\\.)*"|`[^`]*`/g, "''");
  const nums = src.match(/(?<![\w.$])\d+(?:\.\d+)?(?![\w.])/g) || [];
  assert.ok(nums.length > 0, 'premise: the scan reads the code (i + 1 is in it)');
  assert.deepEqual([...new Set(nums)].filter((n) => n !== '0' && n !== '1'), [],
    'a count, a step or a section figure typed into the map');
});

test('the guided example is the first style cited by its own record', () => {
  const rec = BY_ID.get('guided-example');
  const first = rec.see.find((c) => c.startsWith('style:')).slice('style:'.length);
  assert.equal(guidedExampleStyle(LOOKUP), first);
  assert.equal(guidedExampleStyle(without('guided-example')), null);
  assert.equal(guidedExampleStyle(null), null);
  const reordered = indexTerms({ terms: RECS.map((r) => (r.id === 'guided-example'
    ? { ...r, see: ['brief:family-georgian', 'style:craftsman#kit', 'style:craftsman', 'style:tidewater-georgian'] } : r)) });
  assert.equal(guidedExampleStyle(reordered), 'craftsman', 'the first plain style cite, read by the grammar');
});

test('the style in hand: the guided example when nothing is held, named, with the term after the name', () => {
  const g = guidedExampleStyle(LOOKUP);
  const hand = inHandFrom(null, LOOKUP, (id) => styleName(id));
  assert.deepEqual(hand, { id: g, name: styleName(g), guided: true });
  const m = navModel({ lookup: LOOKUP, inHand: hand, place: at('#/') });
  const it = byId(m, 'in-hand');
  assert.equal(it.label, `${styleName(g)} · ${TERM('guided-example')}`);
  assert.equal(it.termId, 'guided-example', 'described by the record that says why it is offered');
  assert.equal(it.note, g, 'the id as a margin note, after the name');
  assert.equal(it.href, formatHash('style', { style: g }, {}));
  assert.deepEqual(it.children, [], 'no sections off its own dossier');
  const held = inHandFrom('craftsman', LOOKUP, (id) => styleName(id));
  assert.deepEqual(held, { id: 'craftsman', name: styleName('craftsman'), guided: false });
  const it2 = byId(navModel({ lookup: LOOKUP, inHand: held, place: at('#/') }), 'in-hand');
  assert.equal(it2.label, styleName('craftsman'), 'a style the reader chose is not called the guided example');
  assert.equal(it2.termId, null);
  // an unnamed style reads as its id, never as a name made from it
  const bare = byId(navModel({ lookup: LOOKUP, inHand: inHandFrom('craftsman', LOOKUP, () => null), place: at('#/') }), 'in-hand');
  assert.equal(bare.label, 'craftsman');
  assert.equal(bare.note, null);
  // nothing held and no glossary: no in-hand item at all
  assert.equal(inHandFrom(null, null, styleName), null);
  assert.equal(byId(navModel({ lookup: LOOKUP, place: at('#/') }), 'in-hand'), undefined);
});

const DOSSIER = {
  id: 'tidewater-georgian',
  sections: [{ id: 'identify', count: null }, { id: 'lineage', count: 5 }, { id: 'kit', count: 94 },
    { id: 'faults', count: 206 }],
};

test('the in-hand style’s sections are listed only on its own dossier, in the dossier’s order, with its counts', () => {
  const hand = { id: 'tidewater-georgian', name: 'Tidewater Georgian', guided: false };
  const on = navModel({ lookup: LOOKUP, inHand: hand, dossier: DOSSIER, place: at('#/style/tidewater-georgian/kit') });
  const it = byId(on, 'in-hand');
  assert.deepEqual(it.children.map((c) => c.id), DOSSIER.sections.map((s) => `in-hand:${s.id}`));
  it.children.forEach((c, i) => {
    const s = DOSSIER.sections[i];
    assert.equal(c.label, TERM(`section-${s.id}`));
    assert.equal(c.termId, `section-${s.id}`);
    assert.equal(c.meta, s.id === 'identify' ? null : s.count, 'the section count, none for identify');
    const p = parseHash(c.href);
    assert.equal(p.surface, 'style');
    assert.equal(p.selection.style, 'tidewater-georgian');
    assert.equal(p.selection.section, s.id === 'identify' ? undefined : s.id, 'identify is never written');
  });
  // on another style's page, under another style's dossier, or with no dossier: no sections
  for (const [place, dossier] of [
    [at('#/style/craftsman'), { ...DOSSIER, id: 'craftsman' }],
    [at('#/style/tidewater-georgian'), { ...DOSSIER, id: 'craftsman' }],
    [at('#/style/tidewater-georgian'), null],
    [at('#/proportions/trim-classical'), DOSSIER],
    [at('#/style'), DOSSIER],
  ]) {
    const m = navModel({ lookup: LOOKUP, inHand: hand, dossier, place });
    assert.deepEqual(byId(m, 'in-hand').children, [], JSON.stringify(place));
  }
  // a section id outside the vocabulary is not a place and is not listed
  const odd = navModel({ lookup: LOOKUP, inHand: hand, place: at('#/style/tidewater-georgian'),
    dossier: { ...DOSSIER, sections: [...DOSSIER.sections, { id: 'nonsense', count: 1 }] } });
  assert.ok(!byId(odd, 'in-hand').children.some((c) => c.id === 'in-hand:nonsense'));
});

test('at most one item is current, and it is the one §F.2 names', () => {
  const hand = { id: 'tidewater-georgian', name: 'Tidewater Georgian', guided: true };
  const cases = [
    ['#/', null, 'overview'],
    ['#/style', null, 'style'],
    ['#/style/-/kit', null, 'style'],
    ['#/style/-/kit/cornice', null, 'style'],
    ['#/style/tidewater-georgian', DOSSIER, 'in-hand:identify'],
    ['#/style/tidewater-georgian/kit/cornice', DOSSIER, 'in-hand:kit'],
    ['#/style/tidewater-georgian/faults', DOSSIER, 'in-hand:faults'],
    ['#/style/tidewater-georgian/rules', DOSSIER, 'in-hand'],
    ['#/style/tidewater-georgian/kit', null, 'in-hand'],
    ['#/style/craftsman', { ...DOSSIER, id: 'craftsman' }, null],
    ['#/kit/tidewater-georgian/cornice', DOSSIER, 'in-hand:kit'],
    ['#/kit/-/cornice', null, 'style'],
    ['#/phylogeny/craftsman', null, 'phylogeny'],
    ['#/brief', null, 'brief'],
    ['#/candidates/2', null, 'candidates'],
    ['#/workbench', null, 'workbench'],
    ['#/transcription', null, 'transcription'],
    ['#/drawings', null, 'drawings'],
    ['#/export', null, 'export'],
    ['#/proportions/trim-classical', null, 'proportions'],
    ['#/faults?sev=serious', null, 'faults'],
    ['#/glossary/judgment-unjudged', null, 'glossary'],
  ];
  for (const [hash, dossier, want] of cases) {
    const m = navModel({ lookup: LOOKUP, inHand: hand, dossier, place: at(hash) });
    const cur = flatItems(m).filter((it) => it.current).map((it) => it.id);
    assert.ok(cur.length <= 1, `${hash}: ${cur.join(', ')}`);
    assert.deepEqual(cur, want ? [want] : [], hash);
  }
});

test('the page head is read from the record §F.2 names, and every one it can name exists', () => {
  assert.equal(headTermFor(at('#/')), 'surface-overview');
  assert.equal(headTermFor(at('#/style')), 'surface-style');
  assert.equal(headTermFor(at('#/style/-/kit')), 'surface-style');
  assert.equal(headTermFor(at('#/style/-/kit/cornice')), 'section-kit');
  assert.equal(headTermFor(at('#/style/craftsman')), 'section-identify');
  assert.equal(headTermFor(at('#/style/craftsman/lineage')), 'section-lineage');
  assert.equal(headTermFor(at('#/kit/craftsman/cornice')), 'section-kit');
  assert.equal(headTermFor(at('#/proportions/trim-classical')), 'surface-proportions');
  assert.equal(headTermFor(at('#/glossary/about-tdl')), 'surface-glossary');
  const names = new Set();
  for (const s of Object.keys(SURFACE_PATHS)) names.add(headTermFor({ surface: s, selection: {} }));
  for (const s of DOSSIER_SECTIONS) names.add(headTermFor({ surface: 'style', selection: { style: 'x', section: s } }));
  for (const id of names) assert.ok(BY_ID.has(id), `the head for some place reads ${id}, which exists`);
});

test('the legacy kit address is read as the place it names', () => {
  assert.deepEqual(normalizePlace(at('#/kit/craftsman/cornice')),
    { surface: 'style', selection: { style: 'craftsman', slot: 'cornice', section: 'kit' } });
  assert.deepEqual(normalizePlace(at('#/kit')), { surface: 'style', selection: {} });
  assert.deepEqual(normalizePlace(at('#/faults')), { surface: 'faults', selection: {} });
});
