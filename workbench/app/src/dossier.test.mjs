/* THE STYLE DOSSIER'S DECISIONS, DRIVEN WITHOUT REACT (WP-14.12, PRD §D, §E.2).

   The dossier is three places on one path and a strip of sections, and every decision about which
   place, which sections and which section is in view is made in `dossier/sections.js`; every
   reading of another record is in `dossier/relations.js`. Both are pure, so this file drives them
   directly and holds the surfaces that call them to the few source facts a render test would need
   a browser for:

     - a bare `#/style` is the INDEX and never a record -- the store's `styleInHand` is written by
       the dossier and offered by the index, and read into a render by nothing;
     - a section whose count is zero is not listed, and a URL naming an unlisted section is
       REFUSED by name rather than drawn empty;
     - every word the strip and the pack groups show is a glossary record that exists;
     - no surface on this path carries a default style, and none sets its text in `--ink-4`.

   Expectations are read off the corpus (`glossary/`) or built by hand where the branch they drive
   is one the corpus cannot reach, with the premise asserted. No count here is a count of the
   corpus. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import {
  IDENTIFY, KIT, sectionTermId, placeOf, listedSections, sectionInView, summaryCards, slotInView,
  sectionAddress,
} from './dossier/sections.js';
import {
  siblingsOf, packGroups, splitDelivered, deliveredOpen, cascadeRows, benchOf,
} from './dossier/relations.js';
import { DOSSIER_SECTIONS } from './citations.js';
import { CONSTRAINT_STATES } from './judgment.js';
import { parseHash } from './router.js';

const ROOT = new URL('../../../', import.meta.url);
const SRC = new URL('./', import.meta.url);
const src = (p) => readFileSync(new URL(p, SRC), 'utf8');
const glossaryHas = (id) => existsSync(new URL(`glossary/${id}.json`, ROOT));

// ── which place a selection names (§E.2) ───────────────────────────────────────────────────────

test('a bare #/style is the index, and so is every selection naming no style and no slot', () => {
  for (const hash of ['#/style', '#/style/', '#/style?q=georgian', '#/style/-/kit']) {
    assert.equal(placeOf(parseHash(hash).selection), 'index', `${hash} opened something other than the index`);
  }
  assert.equal(placeOf(undefined), 'index');
  assert.equal(placeOf({}), 'index');
  assert.equal(placeOf({ style: '' }), 'index', 'an empty style id is not a style');
  assert.equal(placeOf({ section: 'lineage' }), 'index', 'a section with no style names no record');
});

test('a style names its dossier, whatever section or slot rides with it', () => {
  for (const hash of ['#/style/craftsman', '#/style/craftsman/kit', '#/style/craftsman/kit/cornice',
    '#/style/craftsman/rules?constraint=craftsman.eave-overhang']) {
    assert.equal(placeOf(parseHash(hash).selection), 'dossier', hash);
  }
});

test('no style, the kit section and a slot is the slot panel -- and only that combination', () => {
  assert.equal(placeOf(parseHash('#/style/-/kit/cornice').selection), 'slot');
  assert.equal(placeOf({ section: 'kit', slot: 'cornice' }), 'slot');
  assert.equal(placeOf({ section: 'lineage', slot: 'cornice' }), 'index',
    'a slot outside the kit section opened the slot panel');
  assert.equal(placeOf({ slot: 'cornice' }), 'index');
});

// ── the strip: the payload's sections, in the vocabulary's order, never at zero ────────────────

test('identify is listed first, always, and carries no count', () => {
  for (const d of [null, {}, { sections: [] }, { sections: [{ id: 'kit', count: 4 }] }]) {
    const listed = listedSections(d);
    assert.equal(listed[0].id, IDENTIFY);
    assert.equal(listed[0].count, null, 'identify was given a count');
    assert.equal(listed.filter((s) => s.id === IDENTIFY).length, 1);
  }
});

test('a section served at zero, or at no number at all, is not listed', () => {
  const listed = listedSections({ sections: [
    { id: 'kit', count: 0 }, { id: 'rules', count: 3 }, { id: 'faults', count: -1 },
    { id: 'evidence', count: null }, { id: 'lineage', count: '5' }, { id: 'plans', count: NaN },
  ] });
  // premise: the fixture really serves sections at zero and at non-numbers, and one that is real
  assert.ok(listed.some((s) => s.id === 'rules'), 'the fixture lists nothing, so it proves nothing');
  assert.deepEqual(listed.map((s) => s.id), ['identify', 'rules']);
});

test('the order is DOSSIER_SECTIONS whatever order the rows arrive in, and a stray row is dropped', () => {
  const shuffled = [...DOSSIER_SECTIONS].filter((s) => s !== IDENTIFY).reverse()
    .map((id, i) => ({ id, count: i + 1 }));
  shuffled.push({ id: 'not-a-section', count: 9 }, { id: 'kit', count: 99 });
  const listed = listedSections({ sections: shuffled });
  assert.deepEqual(listed.map((s) => s.id), DOSSIER_SECTIONS);
  assert.equal(listed.find((s) => s.id === 'kit').count, shuffled.find((r) => r.id === 'kit').count,
    'a repeated row was read twice, or read last');
});

test('the summary cards are the listed sections other than identify, each with its own count', () => {
  const listed = listedSections({ sections: [{ id: 'faults', count: 7 }, { id: 'kit', count: 2 }] });
  assert.deepEqual(summaryCards(listed), [{ id: 'kit', count: 2 }, { id: 'faults', count: 7 }]);
  assert.deepEqual(summaryCards(listedSections({})), [], 'a record with nothing but identify has no cards');
});

// ── the section in view: listed, or refused by name ────────────────────────────────────────────

test('an unlisted section is refused by name and identify is drawn instead', () => {
  const listed = listedSections({ sections: [{ id: 'lineage', count: 2 }] });
  assert.deepEqual(sectionInView('kit', listed), { id: IDENTIFY, refused: 'kit' });
  assert.deepEqual(sectionInView('nonsense', listed), { id: IDENTIFY, refused: 'nonsense' });
  assert.deepEqual(sectionInView('lineage', listed), { id: 'lineage', refused: null });
  assert.deepEqual(sectionInView(undefined, listed), { id: IDENTIFY, refused: null });
  assert.deepEqual(sectionInView(IDENTIFY, listed), { id: IDENTIFY, refused: null });
});

test('a section served at zero is refused when the URL asks for it -- never drawn empty', () => {
  const listed = listedSections({ sections: [{ id: 'kit', count: 0 }] });
  assert.deepEqual(sectionInView('kit', listed), { id: IDENTIFY, refused: 'kit' });
});

test('a slot is honoured in the kit section and nowhere else', () => {
  assert.equal(slotInView({ slot: 'cornice' }, KIT), 'cornice');
  assert.equal(slotInView({ slot: 'cornice' }, 'lineage'), null);
  assert.equal(slotInView({}, KIT), null);
});

test('a section address is the router\'s, and identify is written as the bare dossier', () => {
  assert.equal(sectionAddress('craftsman', IDENTIFY), '#/style/craftsman');
  assert.equal(sectionAddress('craftsman', null), '#/style/craftsman');
  assert.equal(sectionAddress('craftsman', 'rules'), '#/style/craftsman/rules');
  for (const id of DOSSIER_SECTIONS) {
    const sel = parseHash(sectionAddress('craftsman', id)).selection;
    assert.equal(sel.style, 'craftsman');
    assert.equal(sel.section || IDENTIFY, id, `${id} does not route back to itself`);
  }
});

// ── every word shown is a glossary record ──────────────────────────────────────────────────────

test('every section, constraint state and pack provenance the dossier names is a glossary record', () => {
  const ids = [
    ...DOSSIER_SECTIONS.map(sectionTermId),
    ...CONSTRAINT_STATES,
    'pack-own', 'pack-opted-in', 'pack-delivered', 'pack-withheld', 'pack-declined',
    'member-of', 'surface-style', 'on-the-bench', 'thin-kit', 'diagnostic-tell',
  ];
  const missing = ids.filter((id) => !glossaryHas(id));
  assert.deepEqual(missing, [], `the dossier names words the glossary does not hold: ${missing.join(', ')}`);
});

// ── relations ──────────────────────────────────────────────────────────────────────────────────

const TAXA = [
  { id: 'trad', rank: 'tradition', member_of: null, floruit_start: 1600 },
  { id: 'trad-b', rank: 'tradition', member_of: null, floruit_start: 1500 },
  { id: 'fam', rank: 'family', member_of: 'trad', floruit_start: 1700 },
  { id: 'a', rank: 'style', member_of: 'fam', floruit_start: 1750 },
  { id: 'b', rank: 'style', member_of: 'fam', floruit_start: 1720 },
  { id: 'c', rank: 'style', member_of: 'fam', floruit_start: 1780 },
  { id: 'elsewhere', rank: 'style', member_of: 'trad', floruit_start: 1730 },
];

test('neighbours are filed under the same parent, the record itself excluded', () => {
  const sib = siblingsOf('a', TAXA).map((t) => t.id);
  assert.deepEqual([...sib].sort(), ['b', 'c']);
  assert.ok(!sib.includes('elsewhere'), 'a taxon under a different parent was called a neighbour');
  assert.deepEqual(siblingsOf('trad', TAXA).map((t) => t.id), ['trad-b'], 'roots are each other\'s neighbours');
  assert.deepEqual(siblingsOf('nobody', TAXA), []);
  assert.deepEqual(siblingsOf('a', null), []);
});

test('the pack groups are five, the empty delivered group is dropped, and the total counts packs', () => {
  const g = packGroups({
    own: [{ pack: 'p1' }], opted_in: [{ pack: 'p2' }, { pack: 'p3' }],
    delivered: [{ from: 'x', packs: [{ pack: 'p4' }, { pack: 'p5' }] }, { from: 'y', packs: [] },
      { from: 'z', packs: [{ pack: 'p6' }] }],
    withheld: [{ pack: 'p7' }], declined: [],
  });
  assert.deepEqual(Object.keys(g).sort(), ['declined', 'delivered', 'opted_in', 'own', 'total', 'withheld']);
  assert.deepEqual(g.delivered.map((d) => d.from), ['x', 'z'], 'a delivered group with no packs survived');
  assert.equal(g.total, 1 + 2 + 3 + 1 + 0, 'the total counted groups rather than packs');
  const empty = packGroups(undefined);
  assert.equal(empty.total, 0);
  assert.deepEqual(empty.delivered, []);
});

test('the nearest delivered group is set apart, and the farther ones are folded until opened', () => {
  assert.deepEqual(splitDelivered([]), { near: null, far: [] });
  const s = splitDelivered([{ from: 'x' }, { from: 'y' }, { from: 'z' }]);
  assert.equal(s.near.from, 'x');
  assert.deepEqual(s.far.map((g) => g.from), ['y', 'z']);
  assert.equal(deliveredOpen(undefined), false, 'a fold nobody chose was read as open');
  assert.equal(deliveredOpen(false), false);
  assert.equal(deliveredOpen(true), true);
});

test('the cascade ladder counts a level\'s bindings and says what it holds', () => {
  const rows = cascadeRows({ cascade: [
    { distance: 0, id: 'a', specified: 2, extends: 1, forbidden: 0, has_kit: true },
    { distance: 1, id: 'b', specified: 0, extends: 0, forbidden: 0, has_kit: true },
    { distance: 2, id: 'c', specified: 0, extends: 0, forbidden: 0, has_kit: false },
  ] });
  assert.deepEqual(rows.map((r) => r.bindings), [3, 0, 0]);
  assert.deepEqual(rows.map((r) => r.detail), ['2 specified, 1 extends', 'nothing of its own', 'no kit']);
  assert.deepEqual(cascadeRows(null), []);
});

test('the bench says whether its plan is of this style, and nothing when there is no plan', () => {
  assert.equal(benchOf(null, 'a'), null);
  assert.deepEqual(benchOf({ id: 'p', title: 'T', style: 'a' }, 'a'), { id: 'p', title: 'T', style: 'a', here: true });
  assert.equal(benchOf({ id: 'p', style: 'b' }, 'a').here, false);
  assert.equal(benchOf({ id: 'p' }, 'a').here, false, 'a plan stating no style was called this one');
});

// ── the surfaces on this path, held to the facts a render test would need a browser for ────────

const code = (s) => s.replace(/\/\*[\s\S]*?\*\//g, '').replace(/^\s*\/\/.*$/gm, '')
  .replace(/\{\s*\/\*[\s\S]*?\*\/\s*\}/g, '');

test('the dossier writes the style in hand and reads it into nothing', () => {
  const s = code(src('surfaces/StyleDossier.jsx'));
  assert.match(s, /prefs\.setStyleInHand\(styleId\)/, 'the dossier no longer records what it showed');
  assert.doesNotMatch(s, /prefs\.get\(/, 'the dossier reads the preference store');
  assert.equal((s.match(/setStyleInHand/g) || []).length, 1, 'the style in hand is written more than once');
  assert.doesNotMatch(s, /\bstyleInHand\b/, 'the dossier reads the styleInHand field');
  // the write is gated on the RESOLVED payload for the id the page names
  assert.match(s, /dossier\s*&&\s*dossier\.id\s*===\s*styleId/);
});

test('the index never fetches a record, and offers the style in hand only as a link', () => {
  const s = code(src('surfaces/StylesIndex.jsx'));
  assert.doesNotMatch(s, /api\.style\(|api\.styleDossier\(|api\.kit\(/, 'the index fetches a record');
  assert.doesNotMatch(s, /setStyleInHand/, 'the index writes the style in hand');
  assert.match(s, /RecordLink cite=\{'style:' \+ inHand\}/, 'the style in hand is no longer offered as a link');
});

test('the style surface routes on placeOf and nothing else', () => {
  const s = code(src('surfaces/StyleDossier.jsx'));
  assert.match(s, /const place = placeOf\(selection\);/);
  assert.match(s, /if \(place === 'index'\) return <StylesIndex \/>;/);
  assert.doesNotMatch(s, /selection\.style\s*\|\|/, 'a missing style is filled in from somewhere');
});

test('no surface on the style path carries a default style', () => {
  for (const f of ['surfaces/StyleDossier.jsx', 'surfaces/StylesIndex.jsx', 'surfaces/KitSurface.jsx',
    'dossier/SlotPanel.jsx', 'dossier/KitSection.jsx']) {
    const s = code(src(f));
    assert.doesNotMatch(s, /DEFAULT_STYLE|tidewater-georgian/, `${f} names a style nobody chose`);
  }
});

test('the files this package added set no text in --ink-4', () => {
  const files = ['surfaces/StyleDossier.jsx', 'surfaces/StylesIndex.jsx', 'components/RelationsPanel.jsx',
    'dossier/parts.jsx', 'dossier/Identify.jsx', 'dossier/Members.jsx', 'dossier/Lineage.jsx',
    'dossier/KitSection.jsx', 'dossier/ProportionsSection.jsx', 'dossier/PlanTypes.jsx',
    'dossier/Rules.jsx', 'dossier/Faults.jsx', 'dossier/Evidence.jsx', 'dossier/SlotPanel.jsx'];
  const offenders = files.filter((f) => /--ink-4/.test(code(src(f))));
  assert.deepEqual(offenders, []);
});

test('the dossier draws only the section in view, chosen by sectionInView over listedSections', () => {
  const s = code(src('surfaces/StyleDossier.jsx'));
  assert.match(s, /const listed = listedSections\(dossier\);/);
  assert.match(s, /const view = sectionInView\(selection\.section, listed\);/);
  // every section component is guarded by view.id; none is drawn unconditionally
  for (const name of ['Identify', 'Members', 'Lineage', 'KitSection', 'ProportionsSection', 'PlanTypes',
    'Rules', 'Faults', 'Evidence']) {
    const at = s.indexOf(`<${name} `);
    assert.ok(at >= 0, `${name} is not drawn at all`);
    assert.match(s.slice(Math.max(0, at - 60), at), /view\.id === [^&]+&&\s*$/, `${name} is drawn outside the view guard`);
  }
});

test('StyleRecord.jsx is gone and nothing imports it', () => {
  assert.equal(existsSync(new URL('surfaces/StyleRecord.jsx', SRC)), false);
  assert.doesNotMatch(src('App.jsx'), /StyleRecord/);
});
