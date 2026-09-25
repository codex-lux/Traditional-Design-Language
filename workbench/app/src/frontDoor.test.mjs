/* THE FRONT DOOR AND THE GATE, HELD TO THE RECORDS AND THE SITE MAP THEY READ (WP-14.14).

   Everything here is read with `node:fs` alone — the glossary records from `glossary/*.json`, the
   styles from `styles/*.json`, the example brief from `briefs/`, and three component files as
   text — so no React, no server and nothing from `node_modules`. The subjects, each a way the
   first page a stranger reads could lie to them:

   - THE MAP ↔ THE SITE MAP, BOTH WAYS. Every item `navModel()` gives appears in the front door's
     map, once, with navModel's own label, address, step and figure; and the map carries nothing
     navModel did not give. A place written into the map by hand, or a place the map dropped, fails.
   - THE MAP KEEPS NO LIST. `TwoSpineMap.jsx` carries no address, surface id or record id: a second
     catalogue of places is how the three this replaced came to disagree.
   - WHAT THIS IS, AND FOR WHOM, IS `about-tdl`'S. The definition, the three practitioner readers
     and the "is not" lines are the record's, untouched and complete — no reader added (VISION's
     fourth, the homeowner, is left out by the record, and a page adding one back fails), none
     dropped.
   - THE WORKED EXAMPLE STOPS WHERE THE CORPUS DOES, IN THE RECORD'S WORDS. `guided-example`'s
     citations are the example's links and its `more` is where it stops; with no `more` the page
     says nothing in its place rather than promising a house.
   - THE INVENTORY IS THE API'S `by_rank`, figure for figure, named by the rank records.
   - THE GATE SAYS ONE SENTENCE OR NOTHING. `aboutLine` answers the record's definition or null on
     every failure, and `Gate.jsx` draws that answer and nothing else, asking no other route.
   - THE FRONT DOOR WRITES NO SENTENCE OF ITS OWN, names no style id, and sets no readable text in
     `--ink-4`. (Its count literals are `copy_ratchet.test.mjs`'s to hold, for every page at once.)

   The component guards read source text, which is the weaker form: they say what a file WRITES,
   never how it behaves, and each says so. Behaviour is the walk's (`e2e/walk.mjs`, the front-door
   and Gate blocks). */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { navModel, flatItems, inHandFrom, guidedExampleStyle, NAV } from './nav/navModel.js';
import { indexTerms } from './glossary/lookup.js';
import { journeyState } from './journey/journey.js';
import { parseHash, SURFACE_PATHS } from './router.js';
import { parseCite } from './citations.js';
import { mapRows } from './frontdoor/spineMap.js';
import {
  aboutView, guidedView, rankRows, total, entranceItems, resumeView,
} from './frontdoor/frontDoor.js';
import { aboutLine, lineOf } from './frontdoor/aboutLine.js';

const ROOT = new URL('../../../', import.meta.url);
const SRC = new URL('./', import.meta.url);
const read = (rel) => JSON.parse(readFileSync(new URL(rel, ROOT), 'utf8'));
const dir = (rel) => (existsSync(new URL(rel, ROOT))
  ? readdirSync(new URL(rel, ROOT)).filter((f) => f.endsWith('.json')).sort() : []);
const source = (rel) => readFileSync(new URL(rel, SRC), 'utf8');

const RECS = dir('glossary/').map((f) => read(`glossary/${f}`));
const BY_ID = new Map(RECS.map((r) => [r.id, r]));
const byField = {};
for (const r of RECS) for (const b of r.binds || []) (byField[b.field] ||= {})[b.value] = r.id;
const LOOKUP = indexTerms({ terms: RECS, count: RECS.length, by_field: byField });
const without = (...ids) => indexTerms({ terms: RECS.filter((r) => !ids.includes(r.id)), by_field: byField });
const withRecord = (id, patch) => indexTerms({
  terms: RECS.map((r) => (r.id === id ? { ...r, ...patch } : r)), by_field: byField,
});

const STYLES = dir('styles/').map((f) => read(`styles/${f}`));
const STYLE_NAME = new Map(STYLES.map((s) => [s.id, s.name]));
const nameOf = (id) => STYLE_NAME.get(id) || null;

/* `core.overview()`'s own rule for `by_rank` (mcp_server/core.py): one per style record, by rank. */
const BY_RANK = {};
for (const s of STYLES) BY_RANK[s.rank] = (BY_RANK[s.rank] || 0) + 1;
/* A counts object in the served shape, figures made up for the test and named as such: the meta
   rule is that whatever figure the API gives is the one shown, so any figure will do. */
const COUNTS = { styles: STYLES.length, by_rank: BY_RANK, proportion_packs: { a: 3, b: 4 }, faults: 11 };

const at = (hash) => { const p = parseHash(hash); return { surface: p.surface, selection: p.selection }; };

/* The front door's own call: what `Overview.jsx` hands navModel. */
function frontModel({ lookup = LOOKUP, held = null, plan = null, session = {}, lastEval = null,
  place = at('#/'), dossier = null } = {}) {
  const journey = journeyState({ session, plan, lastEval });
  return navModel({ lookup, counts: COUNTS, glossaryCount: lookup.count,
    inHand: inHandFrom(held, lookup, nameOf), dossier, journey, place });
}

const FIELDS = ['surface', 'href', 'termId', 'label', 'missing', 'step', 'meta', 'current', 'note'];

/* The model's items and the map's entries, compared both ways. Returns [missing, extra, differs]. */
function compare(model) {
  const want = flatItems(model);
  const got = mapRows(model).flatMap((r) => r.items);
  const wantIds = want.map((i) => i.id);
  const gotIds = got.map((i) => i.id);
  const missing = wantIds.filter((id) => !gotIds.includes(id));
  const extra = gotIds.filter((id) => !wantIds.includes(id));
  const dup = gotIds.filter((id, k) => gotIds.indexOf(id) !== k);
  const differs = [];
  for (const g of got) {
    const w = want.find((i) => i.id === g.id);
    if (!w) continue;
    for (const f of FIELDS) {
      if (JSON.stringify(g[f] ?? null) !== JSON.stringify(w[f] ?? null)) differs.push(`${g.id}.${f}`);
    }
  }
  return { missing, extra: [...extra, ...dup], differs, order: JSON.stringify(gotIds) === JSON.stringify(wantIds) };
}

test('the premise: the records, the styles and the example brief the front door reads are on this tree', () => {
  assert.ok(RECS.length > 0, 'COULD NOT EVALUATE without glossary/*.json — and a front door with no words is not a pass');
  for (const id of ['about-tdl', 'guided-example', 'surface-style', 'surface-brief']) {
    assert.ok(BY_ID.has(id), `the record ${id} exists`);
  }
  assert.ok(STYLES.length > 0 && Object.keys(BY_RANK).length > 0, 'the style records carry ranks');
});

/* ------------------------------------------------------------------ the map and the site map */

test('every item the site map gives is in the front door’s map, once, as navModel gives it — and nothing else is', () => {
  const guided = guidedExampleStyle(LOOKUP);
  const states = {
    'the front door, nothing held': frontModel(),
    'a style held': frontModel({ held: 'craftsman' }),
    'a plan on the bench': frontModel({ plan: { id: 'p', name: 'A plan', levels: [] } }),
    // the in-hand style's sections are items too, and a map that dropped nested items would pass
    // every state above: this one has them
    'the in-hand dossier': frontModel({ place: at(`#/style/${guided}/kit`),
      dossier: { id: guided, sections: [{ id: 'identify' }, { id: 'kit', count: 5 }, { id: 'faults', count: 2 }] } }),
    'a glossary missing a record': frontModel({ lookup: without('surface-faults', 'nav-group-library') }),
  };
  for (const [name, model] of Object.entries(states)) {
    const items = flatItems(model);
    assert.ok(items.length > 0, `${name}: the denominator — a model with no items makes the comparison vacuous`);
    const c = compare(model);
    assert.deepEqual(c.missing, [], `${name}: navModel items the map dropped`);
    assert.deepEqual(c.extra, [], `${name}: map entries navModel did not give (or gave once)`);
    assert.deepEqual(c.differs, [], `${name}: map entries that say something navModel did not`);
    assert.ok(c.order, `${name}: the map reads in navModel's order`);
    assert.deepEqual(mapRows(model).map((r) => [r.id, r.termId, r.label, r.missing]),
      model.groups.map((g) => [g.id, g.termId, g.label, g.missing]), `${name}: one row per group, as navModel heads it`);
  }
  const nested = mapRows(states['the in-hand dossier']).flatMap((r) => r.items).filter((i) => i.depth > 0);
  assert.ok(nested.some((i) => i.id === 'transcription') && nested.some((i) => i.id.startsWith('in-hand:')),
    'the premise: nested items are exercised — Trace a drawing and the in-hand sections');
});

test('every NAV item reaches the map on the front door, so a place added to the site map arrives with no edit here', () => {
  const ids = new Set(mapRows(frontModel()).flatMap((r) => r.items.map((i) => i.id)));
  const nav = NAV.flatMap((g) => g.items.flatMap((i) => [i, ...(i.children || [])])).map((i) => i.id);
  assert.deepEqual(nav.filter((id) => !ids.has(id)), [],
    'on the front door the style in hand is the guided example, so every NAV item — in-hand included — is drawn');
  for (const r of mapRows(frontModel())) {
    for (const it of r.items) {
      assert.ok(SURFACE_PATHS[parseHash(it.href).surface], `${it.id}: ${it.href} is an address the router writes`);
    }
  }
  const here = mapRows(frontModel()).flatMap((r) => r.items).filter((i) => i.current).map((i) => i.id);
  assert.deepEqual(here, ['overview'], 'on the front door, the front door is the one place marked current');
});

test('TwoSpineMap.jsx draws mapRows(model) and keeps no list of its own (a source guard)', () => {
  const src = source('components/TwoSpineMap.jsx');
  const live = src.replace(/\/\*[\s\S]*?\*\//g, '').replace(/(^|[\s;,{}()])\/\/[^\n]*/g, '$1');
  assert.match(live, /import\s*\{\s*mapRows\s*\}\s*from\s*'\.\.\/frontdoor\/spineMap\.js'/, 'it reads the map from spineMap.js');
  assert.match(live, /mapRows\(model\)/, 'and hands it the model it was given');
  assert.doesNotMatch(live, /navModel\(|NAV\b/, 'it does not build or walk a model of its own');
  assert.doesNotMatch(live, /href=["'{]\s*['"`]?#/, 'no address is written into it');
  assert.doesNotMatch(live, /['"`]#\//, 'no hash path in any string');
  const strings = [...live.matchAll(/'([^'\n]*)'|"([^"\n]*)"|`([^`]*)`/g)].map((m) => m[1] ?? m[2] ?? m[3]);
  const names = new Set([
    ...Object.keys(SURFACE_PATHS),
    ...NAV.flatMap((g) => [g.id, g.termId, ...g.items.flatMap((i) => [i.id, i.termId,
      ...(i.children || []).flatMap((c) => [c.id, c.termId])])]).filter(Boolean),
  ]);
  assert.deepEqual(strings.filter((s) => names.has(s)), [], 'no surface id, item id or record id is spelled in it');
  assert.doesNotMatch(live, /<Term\s+id=["'{]\s*['"`]/, 'a group heading is its row’s record, never a literal id');
});

/* ------------------------------------------------------------------ what this is, for whom */

test('what this is, who it is for and what it is not are about-tdl’s own, complete and untouched', () => {
  const rec = BY_ID.get('about-tdl');
  const v = aboutView(LOOKUP);
  assert.equal(v.state, 'ready');
  assert.equal(v.term, rec.term);
  assert.equal(v.definition, rec.definition);
  assert.deepEqual(v.readers, rec.readers.map((r) => ({ who: r.who, line: r.line })),
    'the readers are the record’s, every one and no other — a homeowner line added here would be the app’s');
  assert.ok(v.readers.length > 0, 'the premise: the record has readers to show');
  assert.deepEqual(v.isNot, rec.is_not);
  assert.deepEqual(aboutView(null), { state: 'loading' }, 'a glossary that has not answered claims nothing');
  assert.deepEqual(aboutView(without('about-tdl')), { state: 'missing', missing: 'about-tdl' },
    'a missing record is named, never replaced');
});

/* ------------------------------------------------------------------ the worked example */

test('the guided example is its record’s: the definition, the citations in order, and the style navModel offers', () => {
  const rec = BY_ID.get('guided-example');
  const v = guidedView(LOOKUP);
  assert.equal(v.state, 'ready');
  assert.equal(v.word, rec.term);
  assert.equal(v.definition, rec.definition);
  assert.deepEqual(v.cites, rec.see, 'every citation, in the record’s order');
  assert.equal(v.styleCite, `style:${guidedExampleStyle(LOOKUP)}`, 'the same style the rail offers, by the same reader');
  assert.ok(v.briefCite && parseCite(v.briefCite).kind === 'brief');
  assert.ok(existsSync(new URL(`briefs/${v.briefId}.json`, ROOT)), `the example brief ${v.briefId} is on this tree`);
  assert.equal(guidedView(without('guided-example')).state, 'missing');
});

test('the example says where it stops in the record’s words, and says nothing in their place when the record does not', () => {
  const rec = BY_ID.get('guided-example');
  assert.ok(typeof rec.more === 'string' && rec.more.trim(),
    'the premise: guided-example carries `more`, the sentence saying where the example stops '
    + '(oq/the-worked-house-has-no-plan-that-places) — without it the front door would promise a house by silence');
  assert.equal(guidedView(LOOKUP).more, rec.more.trim());
  const { more, ...rest } = rec;
  const bare = indexTerms({ terms: RECS.map((r) => (r.id === 'guided-example' ? rest : r)) });
  assert.equal(guidedView(bare).more, null, 'no sentence is put where the record has none');
});

/* ------------------------------------------------------------------ what it holds */

test('the inventory is counts.by_rank, figure for figure, named by the rank records in their order', () => {
  const rows = rankRows(COUNTS, LOOKUP);
  assert.ok(rows.length > 0, 'the denominator');
  assert.deepEqual(Object.fromEntries(rows.map((r) => [r.key, r.figure])), BY_RANK, 'every rank the API counts, and its figure');
  for (const r of rows) assert.equal(r.termId, byField['style.rank'][r.key], `${r.key} is named by the record that binds it`);
  const orders = rows.map((r) => BY_ID.get(r.termId).order);
  assert.deepEqual(orders, [...orders].sort((a, b) => a - b), 'in the order the records state');
  // a rank the glossary does not name is still counted, and named as missing
  const odd = rankRows({ by_rank: { ...BY_RANK, cryptid: 1 } }, LOOKUP);
  assert.deepEqual(odd.find((r) => r.key === 'cryptid'), { key: 'cryptid', figure: 1, termId: null, missing: 'style.rank:cryptid' });
  assert.deepEqual(rankRows({}, LOOKUP), [], 'no by_rank, no rows — never zeros');
  assert.equal(total({ a: 3, b: 4, c: 'x' }), 7);
  assert.equal(total(null), null);
});

/* ------------------------------------------------------------------ the entrances */

test('the two entrances are the site map’s own items, and the style in hand is offered, never applied', () => {
  const model = frontModel();
  const d = entranceItems(model);
  const items = flatItems(model);
  assert.equal(d.style, items.find((i) => i.id === 'style'));
  assert.equal(d.brief, items.find((i) => i.id === 'brief'));
  assert.equal(d.inHand, items.find((i) => i.id === 'in-hand'));
  assert.equal(d.style.href, '#/style', 'read a style: the Styles index, bare');
  assert.equal(d.brief.href, '#/brief', 'write a house: the first step, bare');
  assert.equal(parseHash(d.inHand.href).selection.style, guidedExampleStyle(LOOKUP),
    'with nothing held, the offer is the guided example');
  assert.equal(parseHash(entranceItems(frontModel({ held: 'craftsman' })).inHand.href).selection.style, 'craftsman');
});

test('where a house is under way, the resume is the journey’s, named by the site map', () => {
  assert.equal(resumeView(journeyState({ session: {}, plan: null }), frontModel()), null, 'nothing under way, nothing offered');
  const plan = { id: 'p', name: 'A plan', levels: [] };
  const model = frontModel({ plan });
  const r = resumeView(journeyState({ session: {}, plan }), model);
  const wb = flatItems(model).find((i) => i.id === 'workbench');
  assert.equal(r.id, 'plan');
  assert.ok(r.plan);
  assert.equal(r.href, wb.href);
  assert.equal(r.label, wb.label);
  assert.equal(r.n, wb.step);
});

/* ------------------------------------------------------------------ the Gate */

test('aboutLine is the record’s definition, or null for every failure — never a sentence of its own', async () => {
  const def = BY_ID.get('about-tdl').definition;
  assert.equal(await aboutLine(async () => ({ term: { id: 'about-tdl', definition: def } })), def);
  assert.equal(await aboutLine(async () => { throw new Error('401'); }), null, 'a refused read');
  assert.equal(await aboutLine(() => Promise.reject(new TypeError('offline'))), null, 'a network failure');
  assert.equal(await aboutLine(() => { throw new Error('sync'); }), null, 'a request that throws before it starts');
  assert.equal(await aboutLine(async () => ({ detail: { error: 'no' } })), null, 'a body with no record');
  assert.equal(await aboutLine(async () => ({ term: { id: 'about-tdl', definition: '  ' } })), null, 'an empty definition');
  assert.equal(await aboutLine(async () => null), null);
  assert.equal(lineOf({ term: { definition: 7 } }), null);
});

test('Gate.jsx draws aboutLine’s answer and nothing else, and asks no route but login and about-tdl (a source guard)', () => {
  const src = source('Gate.jsx');
  const live = src.replace(/\/\*[\s\S]*?\*\//g, '').replace(/(^|[\s;,{}()])\/\/[^\n]*/g, '$1');
  assert.match(live, /import\s*\{\s*aboutLine\s*\}\s*from\s*'\.\/frontdoor\/aboutLine\.js'/);
  const calls = [...live.matchAll(/\bapi\.(\w+)\(([^)]*)\)/g)].map((m) => `${m[1]}(${m[2].trim()})`);
  assert.deepEqual([...new Set(calls)].sort(), ["glossaryTerm('about-tdl')", 'login(password)'],
    'signed out, the Gate may read exactly one corpus path, and it is about-tdl');
  const sets = [...live.matchAll(/\bsetAbout\(([^)]*)\)/g)].map((m) => m[1].trim());
  assert.equal(sets.length, 1, 'one place sets the sentence');
  assert.match(sets[0], /^\w+$/, 'and it sets it to a bare name — no fallback, no literal, no expression');
  assert.match(live, new RegExp(String.raw`aboutLine\([\s\S]*?\)\.then\(\(\s*${sets[0]}\s*\)\s*=>`),
    'that name is what aboutLine resolved to');
  const shown = [...live.matchAll(/<p\b[^>]*data-about-tdl[^>]*>([\s\S]*?)<\/p>/g)].map((m) => m[1].trim());
  assert.deepEqual(shown, ['{about}'], 'the sentence element holds the answer and nothing else');
  assert.doesNotMatch(live, /\babout\s*(\|\||\?\?|\?(?!\.))/, 'the answer is never defaulted to anything');
  assert.match(live, /\{about\s*&&/, 'and it is drawn only where there is one');
});

/* ------------------------------------------------------------------ what the page writes */

/* JSX text a file writes: the runs after a tag's `>` or an expression's `}`, up to the next `<` or
   `{`, with letters in. A run carrying code punctuation, or opening with a keyword, is JavaScript
   between two braces rather than text on the page, and is not counted. A reader of text, not a
   parser: it can miss a phrase written with a colon or a quote in it, and says so here. */
function jsxText(src) {
  const live = src.replace(/\/\*[\s\S]*?\*\//g, '').replace(/\{\/\*[\s\S]*?\*\/\}/g, '')
    .replace(/(^|[\s;,{}()])\/\/[^\n]*/g, '$1');
  return [...live.matchAll(/[>}]([^<>{}]*)(?=[<{])/g)].map((m) => m[1].replace(/\s+/g, ' ').trim())
    .filter((t) => /[A-Za-z]/.test(t) && !/[;=()'"`]/.test(t)
      && !/^(else|return|from|import|const|let|if|finally)\b/.test(t));
}

test('the front door writes no sentence of its own: its words are records’, its one label is the search', () => {
  const texts = [...jsxText(source('surfaces/Overview.jsx')), ...jsxText(source('components/TwoSpineMap.jsx'))];
  assert.deepEqual(jsxText('<p>a b c</p><a>{x} d</a>'), ['a b c', 'd'],
    'the premise: the reader finds JSX text, after a tag and after an expression');
  assert.deepEqual(texts, ['Search the corpus', '⌘K'],
    'every word a reader sees on the front door comes from a glossary record or the API; the one '
    + 'phrase it writes is the invitation to search, which is an act and not a definition');
  const liveOverview = source('surfaces/Overview.jsx').replace(/\/\*[\s\S]*?\*\//g, '')
    .replace(/(^|[\s;,{}()])\/\/[^\n]*/g, '$1');
  const tpl = [...liveOverview.matchAll(/`([^`]*)`/g)].map((m) => m[1].replace(/\$\{[^}]*\}/g, '').trim())
    .filter((t) => /[A-Za-z]{3}/.test(t) && !/^var\(/.test(t));
  assert.deepEqual(tpl, ['ontology'], 'the template text is the ontology version’s label and nothing else');
});

test('the front door names no style id, no longer reads what_this_is, and keeps no DOORS', () => {
  const src = source('surfaces/Overview.jsx');
  const live = src.replace(/\/\*[\s\S]*?\*\//g, '').replace(/(^|[\s;,{}()])\/\/[^\n]*/g, '$1');
  const strings = [...live.matchAll(/'([^'\n]*)'|"([^"\n]*)"/g)].map((m) => m[1] ?? m[2]);
  assert.deepEqual(strings.filter((s) => STYLE_NAME.has(s)), [],
    'the guided example is read from its record’s citations; no style id is written here (PRD §B)');
  assert.doesNotMatch(live, /what_this_is/, 'the agent’s orientation string stays served and is not this page’s paragraph');
  assert.doesNotMatch(live, /\bDOORS\b/, 'the app-written doors are retired');
  for (const f of ['surfaces/Overview.jsx', 'components/TwoSpineMap.jsx']) {
    const l = source(f).replace(/\/\*[\s\S]*?\*\//g, '');
    assert.doesNotMatch(l, /--ink-4/, `${f}: no readable text in --ink-4 in new code`);
  }
});

/* WHAT IT HOLDS AND WHAT IT IS NOT EACH CARRY A HEADING, AND THE HEADING'S WORD IS A RECORD
   (WP-14.17, tranche 2's PRD §A.4). The two lower sections were a column of figures under a
   version string and a list of refusals, with nothing naming either region. A source guard, the
   weaker form, and it says so: it reads what the file WRITES inside each section. The walk reads
   the page. */
function sectionOf(src, attr) {
  const live = src.replace(/\/\*[\s\S]*?\*\//g, '').replace(/\{\/\*[\s\S]*?\*\/\}/g, '');
  const at = live.search(new RegExp(`<section\\s+${attr}=`));
  if (at < 0) return null;
  const end = live.indexOf('</section>', at);
  return end < 0 ? null : live.slice(at, end);
}

const HEADINGS = [['data-inventory', 'front-door-holds'], ['data-is-not-section', 'front-door-is-not']];

test('what it holds and what it is not each open with an h2 whose word is a record', () => {
  const src = source('surfaces/Overview.jsx');
  assert.equal(sectionOf('<section data-x="">a<Eyebrow as="h2"><Term id="r" /></Eyebrow></section>', 'data-x'),
    '<section data-x="">a<Eyebrow as="h2"><Term id="r" /></Eyebrow>',
    'the premise: the reader cuts one section out of a file');
  for (const [attr, id] of HEADINGS) {
    const sec = sectionOf(src, attr);
    assert.ok(sec, `${attr}: the section is in Overview.jsx`);
    const h2 = sec.match(/<Eyebrow\s+as="h2"[^>]*>([\s\S]*?)<\/Eyebrow>/);
    assert.ok(h2, `${attr}: the section opens with an h2`);
    assert.equal(sec.indexOf(h2[0]), sec.search(/<Eyebrow\b/), `${attr}: the h2 is the section's first eyebrow`);
    assert.deepEqual([...h2[1].matchAll(/<Term\s+id="([^"]+)"\s*\/>/g)].map((m) => m[1]), [id],
      `${attr}: the heading draws exactly one record, ${id}`);
    assert.doesNotMatch(h2[1].replace(/<Term[^>]*\/>/g, ''), /[A-Za-z]/,
      `${attr}: nothing but the Term in the h2 -- no word typed beside it`);
    const rec = BY_ID.get(id);
    assert.ok(rec, `${id} is a glossary record`);
    assert.equal(rec.family, 'product', `${id} is the product's own word, beside about-tdl`);
  }
  assert.match(sectionOf(src, 'data-is-not-section'), /<ul\s+data-is-not=/,
    'the is-not list sits inside its headed section, keeping the attribute the walk reads');
});
