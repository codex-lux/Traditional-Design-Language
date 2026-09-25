/* THE TRAIL AND THE TAB TITLE, HELD TO THE RECORDS (WP-14.13, PRD §F.3).

   `nav/crumbs.js` says where a page is. Every name here is read from the corpus with `node:fs`:
   styles from `styles/*.json`, slots from `elements/slots.json`, the words from `glossary/*.json`,
   a pack and a fault from their own records — so the trail is verified against what the corpus
   says and not against a copy of it typed into the test. The one literal is the PRD's own
   verified example, asserted equal to what the records produce.

   The subjects:
   - the style chain is the FILING (`member_of`), never the lineage graph;
   - the served dossier's chain and the style list's agree, for every style in the corpus;
   - each place's trail is §F.3's table, ending at the place, which is not a link;
   - the URL alone decides the trail (a surface's fallback record never appears in it);
   - every place has its own tab title. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { crumbsFor, titleFor, chainOf, crumbLabel } from './nav/crumbs.js';
import { indexTerms } from './glossary/lookup.js';
import { noEntry } from './glossary/termView.js';
import { JOURNEY } from './journey/journey.js';
import { parseHash, SURFACE_PATHS } from './router.js';
import { DOSSIER_SECTIONS } from './citations.js';

const ROOT = new URL('../../../', import.meta.url);
const read = (rel) => JSON.parse(readFileSync(new URL(rel, ROOT), 'utf8'));
const dir = (rel) => (existsSync(new URL(rel, ROOT))
  ? readdirSync(new URL(rel, ROOT)).filter((f) => f.endsWith('.json')).sort() : []);

const RECS = dir('glossary/').map((f) => read(`glossary/${f}`));
const TERMS = new Map(RECS.map((r) => [r.id, r]));
const LOOKUP = indexTerms({ terms: RECS });
const TERM = (id) => TERMS.get(id).term;

const NODES = dir('styles/').map((f) => read(`styles/${f}`));
const NODE = new Map(NODES.map((n) => [n.id, n]));
const SLOTS = read('elements/slots.json').groups.flatMap((g) => g.slots);
const PACK = read('proportions/systems/trim-classical.json');
const FAULT = read('faults/porch-too-shallow-to-inhabit.json');
// one record of each plan-type kind, read from its own file (WP-14.23)
const ROOM = read('rooms/parlor.json');
const MASSING = read('massings/catalog.json').find((m) => m.id === 'center-passage-single-pile');
const GROUPING = read('groupings/centre-passage-core.json');
const PARTI = read('partis/centre-passage-double-pile.json');

// the search index's entries, as far as the trail reads them: every style, slot, the pack, the
// fault, and one record of each plan-type kind
const ENTRIES = [
  ...NODES.map((n) => ({ cite: `style:${n.id}`, kind: 'style', id: n.id, name: n.name })),
  ...SLOTS.map((s) => ({ cite: `slot:${s.id}`, kind: 'slot', id: s.id, name: s.name })),
  { cite: `pack:${PACK.id}`, kind: 'pack', id: PACK.id, name: PACK.name },
  { cite: `fault:${FAULT.id}`, kind: 'fault', id: FAULT.id, name: FAULT.name },
  { cite: `room:${ROOM.id}`, kind: 'room', id: ROOM.id, name: ROOM.name },
  { cite: `massing:${MASSING.id}`, kind: 'massing', id: MASSING.id, name: MASSING.name },
  { cite: `grouping:${GROUPING.id}`, kind: 'grouping', id: GROUPING.id, name: GROUPING.name },
  { cite: `parti:${PARTI.id}`, kind: 'parti', id: PARTI.id, name: PARTI.name },
];

/* The filing, walked here on its own from the records — the test's reading, not the module's. */
function filing(id) {
  const out = [];
  let cur = NODE.get(id) && NODE.get(id).member_of;
  while (cur && NODE.has(cur) && !out.includes(cur)) { out.push(cur); cur = NODE.get(cur).member_of; }
  return out.reverse();
}
/* The served dossier's head, built to §H.4 from the records. */
const dossierOf = (id) => ({
  id, name: NODE.get(id).name, rank: NODE.get(id).rank, member_of: NODE.get(id).member_of || null,
  chain: filing(id).map((a) => ({ id: a, name: NODE.get(a).name, rank: NODE.get(a).rank })),
});

const at = (hash) => {
  const p = parseHash(hash);
  return { surface: p.surface, selection: p.selection };
};
const labels = (cs) => cs.map(crumbLabel);

test('the premise: the records the trail reads are on this tree', () => {
  assert.ok(RECS.length > 0 && NODES.length > 0 && SLOTS.length > 0, 'COULD NOT EVALUATE without the corpus');
});

test('the PRD’s own example, verified against styles/*.json and elements/slots.json', () => {
  const place = at('#/style/tidewater-georgian/kit/cornice');
  const expected = [
    TERM('nav-group-styles'),
    ...filing('tidewater-georgian').map((a) => NODE.get(a).name),
    NODE.get('tidewater-georgian').name,
    TERM('section-kit'),
    SLOTS.find((s) => s.id === 'cornice').name,
  ];
  // the example PRD §F.3 states, which the records must produce
  assert.equal(expected.join(' › '),
    'Styles › North American › American Colonial › Georgian Colonial American › Tidewater Georgian › Kit › Main cornice');
  const fromList = crumbsFor(place, { lookup: LOOKUP, names: ENTRIES, styles: NODES });
  const fromDossier = crumbsFor(place, { lookup: LOOKUP, names: ENTRIES, dossier: dossierOf('tidewater-georgian') });
  assert.deepEqual(labels(fromList), expected);
  assert.deepEqual(labels(fromDossier), expected);
  assert.deepEqual(fromList, fromDossier, 'the served chain and the list’s are one trail');
});

test('the chain is the filing and never the lineage: the premise, then every style in the corpus', () => {
  // premise: on the example the two readings differ, so a trail read off lineage would show
  const lineageWalk = [];
  let cur = NODE.get('tidewater-georgian');
  while (cur && cur.lineage && cur.lineage.length && lineageWalk.length < 6) {
    const t = cur.lineage[0].target;
    if (lineageWalk.includes(t)) break;
    lineageWalk.push(t); cur = NODE.get(t);
  }
  assert.notDeepEqual(lineageWalk.reverse(), filing('tidewater-georgian'),
    'premise: lineage and filing disagree on the example');
  let walked = 0;
  for (const n of NODES) {
    const got = chainOf(n.id, NODES);
    assert.deepEqual(got.map((c) => c.id), filing(n.id), `${n.id}'s chain is its member_of filing`);
    got.forEach((c) => assert.equal(c.name, NODE.get(c.id).name));
    // the served head and the list give one trail for every style
    const place = { surface: 'style', selection: { style: n.id } };
    assert.deepEqual(crumbsFor(place, { lookup: LOOKUP, names: ENTRIES, styles: NODES }),
      crumbsFor(place, { lookup: LOOKUP, names: ENTRIES, dossier: dossierOf(n.id) }), n.id);
    walked += got.length;
  }
  assert.ok(walked > NODES.length, 'premise: most styles are filed under something');
  // the list as /api/styles serves it names the parent `in`
  const served = NODES.map((n) => ({ id: n.id, name: n.name, rank: n.rank, in: n.member_of }));
  assert.deepEqual(chainOf('tidewater-georgian', served), chainOf('tidewater-georgian', NODES));
  assert.equal(chainOf('no-such-style', NODES), null);
  assert.deepEqual(chainOf('a', [{ id: 'a', member_of: 'b' }, { id: 'b', member_of: 'a' }]).map((c) => c.id), ['b'],
    'a cycle ends the walk');
});

test('each chain crumb links to its own dossier, the style to its own, the section to its section, and the place is no link', () => {
  const cs = crumbsFor(at('#/style/tidewater-georgian/kit/cornice'), { lookup: LOOKUP, names: ENTRIES, styles: NODES });
  assert.equal(cs[0].group, true);
  assert.equal(cs[0].href, null, 'a group heading is not a place');
  const chain = filing('tidewater-georgian');
  chain.forEach((id, i) => {
    const p = parseHash(cs[1 + i].href);
    assert.equal(p.surface, 'style');
    assert.deepEqual(p.selection, { style: id });
  });
  const style = parseHash(cs[1 + chain.length].href);
  assert.deepEqual(style.selection, { style: 'tidewater-georgian' });
  const section = parseHash(cs[2 + chain.length].href);
  assert.deepEqual(section.selection, { style: 'tidewater-georgian', section: 'kit' });
  assert.equal(cs[cs.length - 1].href, null, 'the last crumb is where you are');
  // the section is the last crumb when there is no slot; identify adds none
  const kit = crumbsFor(at('#/style/tidewater-georgian/kit'), { lookup: LOOKUP, names: ENTRIES, styles: NODES });
  assert.equal(crumbLabel(kit[kit.length - 1]), TERM('section-kit'));
  assert.equal(kit[kit.length - 1].href, null);
  const ident = crumbsFor(at('#/style/tidewater-georgian'), { lookup: LOOKUP, names: ENTRIES, styles: NODES });
  assert.equal(crumbLabel(ident[ident.length - 1]), NODE.get('tidewater-georgian').name);
  for (const s of DOSSIER_SECTIONS.filter((x) => x !== 'identify')) {
    const cs2 = crumbsFor({ surface: 'style', selection: { style: 'craftsman', section: s } },
      { lookup: LOOKUP, names: ENTRIES, styles: NODES });
    assert.equal(crumbLabel(cs2[cs2.length - 1]), TERM(`section-${s}`), s);
  }
});

test('§F.3’s table, place by place', () => {
  const opts = { lookup: LOOKUP, names: ENTRIES, styles: NODES };
  const L = (hash) => labels(crumbsFor(at(hash), opts));
  assert.deepEqual(L('#/'), []);
  assert.deepEqual(L('#/style'), [TERM('nav-group-styles'), TERM('surface-style')]);
  // a slot with no style is its record page in the Elements index (WP-14.23, tranche 2 §B.4),
  // and its tranche-1 address reads as that place
  assert.deepEqual(L('#/elements/cornice'),
    [TERM('nav-group-library'), TERM('surface-elements'), 'Main cornice']);
  assert.deepEqual(L('#/style/-/kit/cornice'), L('#/elements/cornice'));
  assert.deepEqual(L('#/elements'), [TERM('nav-group-library'), TERM('surface-elements')]);
  // a plan-type record: Library > Elements > the record; its kind is the page head's eyebrow
  for (const [path, rec] of [['room', ROOM], ['massing', MASSING], ['grouping', GROUPING], ['parti', PARTI]]) {
    assert.deepEqual(L(`#/${path}/${rec.id}`), [TERM('nav-group-library'), TERM('surface-elements'), rec.name], path);
    // the bare surface is its kind's index, named by the kind's own surface record
    assert.deepEqual(L(`#/${path}`), [TERM('nav-group-library'), TERM('surface-elements'), TERM(`surface-${path}`)], path);
    const cs = crumbsFor(at(`#/${path}/${rec.id}`), opts);
    assert.equal(cs[1].href, '#/elements', `${path}: the Elements crumb does not lead to the index`);
    assert.equal(cs[cs.length - 1].href, null);
    assert.equal(cs[cs.length - 1].cite, `${path === 'room' ? 'room' : path}:${rec.id}`);
  }
  // and a kept tranche-1 record address reads as the record page's trail
  assert.deepEqual(L(`#/workbench?roomType=${ROOM.id}`), L(`#/room/${ROOM.id}`));
  assert.deepEqual(L(`#/phylogeny?massing=${MASSING.id}`), L(`#/massing/${MASSING.id}`));
  assert.deepEqual(L('#/phylogeny'), [TERM('nav-group-styles'), TERM('surface-phylogeny')]);
  assert.deepEqual(L('#/phylogeny/craftsman'),
    [TERM('nav-group-styles'), TERM('surface-phylogeny'), NODE.get('craftsman').name]);
  for (const j of JOURNEY) {
    assert.deepEqual(L(`#/${SURFACE_PATHS[j.surface].path}`), [TERM('nav-group-a-house'), TERM(`surface-${j.surface}`)]);
  }
  assert.deepEqual(L('#/transcription'), [TERM('nav-group-a-house'), TERM('surface-transcription')]);
  assert.deepEqual(L('#/proportions'), [TERM('nav-group-library'), TERM('surface-proportions')]);
  assert.deepEqual(L(`#/proportions/${PACK.id}`), [TERM('nav-group-library'), TERM('surface-proportions'), PACK.name]);
  assert.deepEqual(L('#/faults'), [TERM('nav-group-library'), TERM('surface-faults')]);
  assert.deepEqual(L(`#/faults/${FAULT.id}`), [TERM('nav-group-library'), TERM('surface-faults'), FAULT.name]);
  assert.deepEqual(L('#/glossary'), [TERM('nav-group-library'), TERM('surface-glossary')]);
  assert.deepEqual(L('#/glossary/judgment-unjudged'),
    [TERM('nav-group-library'), TERM('surface-glossary'), TERM('judgment-unjudged')]);
  // the older kit address reads as the place it names
  assert.deepEqual(crumbsFor(at('#/kit/tidewater-georgian/cornice'), opts),
    crumbsFor(at('#/style/tidewater-georgian/kit/cornice'), opts));
  // a surface's own crumb links back to its bare address when a record follows it
  const pk = crumbsFor(at(`#/proportions/${PACK.id}`), opts);
  assert.equal(parseHash(pk[1].href).surface, 'proportions');
  assert.deepEqual(parseHash(pk[1].href).selection, {});
});

test('the URL alone decides the trail: filters and the dossier of another style do not enter it', () => {
  const opts = { lookup: LOOKUP, names: ENTRIES, styles: NODES };
  assert.deepEqual(labels(crumbsFor(at('#/faults?sev=serious&style=craftsman'), opts)),
    [TERM('nav-group-library'), TERM('surface-faults')], 'a bare fault list names no fault, whatever it draws');
  // a dossier payload for another style is not this style's chain
  const wrong = crumbsFor(at('#/style/craftsman'), { ...opts, styles: null, dossier: dossierOf('tidewater-georgian') });
  assert.ok(!labels(wrong).includes('Tidewater Georgian'));
  assert.equal(crumbLabel(wrong[wrong.length - 1]), NODE.get('craftsman').name);
});

test('a name nobody holds reads as its citation, and a missing record as noEntry — never a guess', () => {
  const cs = crumbsFor(at('#/style/tidewater-georgian/kit/cornice'), { lookup: LOOKUP, names: [], styles: null });
  assert.deepEqual(labels(cs), [TERM('nav-group-styles'), 'style:tidewater-georgian', TERM('section-kit'), 'slot:cornice']);
  const holed = indexTerms({ terms: RECS.filter((r) => r.id !== 'section-kit') });
  const h = crumbsFor(at('#/style/tidewater-georgian/kit'), { lookup: holed, names: ENTRIES, styles: NODES });
  const last = h[h.length - 1];
  assert.equal(last.label, null);
  assert.equal(last.missing, 'section-kit');
  assert.equal(crumbLabel(last), noEntry('section-kit'));
});

test('the title reads the trail backwards to the product’s name; the front door is the name alone', () => {
  const about = TERM('about-tdl');
  const opts = { lookup: LOOKUP, names: ENTRIES, styles: NODES };
  assert.equal(titleFor(crumbsFor(at('#/'), opts), LOOKUP), about);
  assert.equal(titleFor(crumbsFor(at('#/style/tidewater-georgian/kit/cornice'), opts), LOOKUP),
    `Main cornice · ${TERM('section-kit')} · Tidewater Georgian · Georgian Colonial American · American Colonial · North American — ${about}`);
  assert.equal(titleFor(crumbsFor(at('#/proportions'), opts), LOOKUP), `${TERM('surface-proportions')} — ${about}`);
  assert.equal(titleFor([], null), null, 'no title of missing words while the glossary is out');
});

test('no two places share a title', () => {
  const opts = { lookup: LOOKUP, names: ENTRIES, styles: NODES };
  const hashes = [
    '#/', '#/style', '#/style/-/kit/cornice', '#/phylogeny', '#/phylogeny/craftsman',
    '#/style/craftsman', '#/style/tidewater-georgian', '#/style/tidewater-georgian/kit/cornice',
    '#/style/tidewater-georgian/kit/door-main-entry',
    ...DOSSIER_SECTIONS.filter((s) => s !== 'identify').map((s) => `#/style/tidewater-georgian/${s}`),
    ...DOSSIER_SECTIONS.filter((s) => s !== 'identify').map((s) => `#/style/craftsman/${s}`),
    '#/brief', '#/candidates', '#/workbench', '#/transcription', '#/drawings', '#/export',
    '#/proportions', `#/proportions/${PACK.id}`, '#/faults', `#/faults/${FAULT.id}`,
    '#/glossary', '#/glossary/judgment-unjudged', '#/glossary/about-tdl',
  ];
  const seen = new Map();
  for (const h of hashes) {
    const t = titleFor(crumbsFor(at(h), opts), LOOKUP);
    assert.ok(t, h);
    assert.ok(!seen.has(t), `${h} and ${seen.get(t)} both read "${t}"`);
    seen.set(t, h);
  }
});
