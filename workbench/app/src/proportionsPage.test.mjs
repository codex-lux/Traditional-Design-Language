/* THE PROPORTIONS PAGE: ITS ORDER, ITS VERDICTS AND ITS ADDRESSES, DRIVEN (WP-14.9).

   `surfaces/Proportions.jsx` imports React and cannot run under `node --test`, so what the page
   DECIDES is `proportions/page.js` and is driven here, and what the page must never SAY — a
   truthiness verdict on an invariant, a remembered default pack, a curve built in JavaScript — is
   held by reading the two component files (the weaker form, and used only for what a file says).

   The fixtures are small hand-built payloads in the served shape (PRD §H.1-§H.3). No count a
   pack has is written here: the walk holds the real page to the real payload. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import {
  PAGE_SECTIONS, PROOF_FOLD, FILTER_SPEC, DEFAULT_DIAMETER_IN, RANGES, measureParam, requestFor,
  sliderAt, plateKind, faceCount, pageSections, authorityLines, invariantMark, invariantTally,
  proofOpen, ruleState, figureWords, rangeWords, usedByGroups, reachOf, packsOfStyle, packGroups,
  packHref, assemblyWords, orderOf, authorityWords,
} from './proportions/page.js';
import { parseHash } from './router.js';

const SRC = fileURLToPath(new URL('./', import.meta.url));
const read = (rel) => readFileSync(SRC + rel, 'utf8');
const live = (s) => s.replace(/\/\*[\s\S]*?\*\//g, '').replace(/(^|[\s;,{}()])\/\/[^\n]*/g, '$1');
const GLOSSARY = new URL('../../../glossary/', import.meta.url);

/* ---- the order ---- */

test('the page reads what the pack is, the drawing, the warnings, the rules, and the proof last', () => {
  assert.deepEqual([...PAGE_SECTIONS],
    ['head', 'plate', 'conflicts', 'rules', 'authorities', 'used-by', 'sources', 'proof']);
  const at = (s) => PAGE_SECTIONS.indexOf(s);
  assert.ok(at('plate') < at('proof') && at('plate') < at('rules'), 'the drawing comes before any table');
  assert.ok(at('conflicts') < at('rules'), 'what goes wrong today before the figures');
  assert.equal(at('proof'), PAGE_SECTIONS.length - 1, 'how it was checked is read last');
  assert.ok(Object.isFrozen(PAGE_SECTIONS));
});

test('the page renders by walking that list, so its DOM order is the list’s', () => {
  const src = live(read('surfaces/Proportions.jsx'));
  assert.match(src, /sections\.map\(\(s\) =>/, 'the page walks pageSections’ answer');
  assert.match(src, /pageSections\(data,/);
  for (const s of PAGE_SECTIONS) assert.match(src, new RegExp(`data-section="${s}"`), `${s} is rendered as a section`);
});

const payload = (over = {}) => ({
  pack: 'p', name: 'P', kind: 'trim-system', drawing: 'assemblies', authority: 'Vignola',
  assemblies: [{ id: 'a', authority: null, geometry: { faces: [{}, {}] } }],
  conflicts: [{ with: 'cost' }], derived_rules: [{ value: 1 }], invariants: [{ holds: true }],
  used_by: { own: [] }, ...over,
});

test('a section with nothing to show is left out; the head, the plate and the proof never are', () => {
  assert.deepEqual(pageSections(payload(), { authorities: [{}] }), [...PAGE_SECTIONS]);
  const bare = pageSections({ pack: 'p', drawing: null }, {});
  assert.deepEqual(bare, ['head', 'plate', 'proof'], 'no conflicts, rules, authorities, users or sources');
  assert.deepEqual(pageSections(null), []);
  assert.ok(!pageSections(payload(), { authorities: [] }).includes('authorities'));
});

test('the plate the payload asks for, and a pack with nothing to draw is its own kind', () => {
  assert.equal(plateKind({ drawing: 'stack' }), 'stack');
  assert.equal(plateKind({ drawing: 'assemblies' }), 'assemblies');
  for (const d of [null, undefined, 'something-else']) assert.equal(plateKind({ drawing: d }), 'none');
  assert.equal(faceCount(payload().assemblies), 2, 'the band count is the served faces');
  assert.equal(faceCount([{ geometry: null }, {}]), 0);
});

/* ---- the proof: holds: null is unjudged ---- */

test('an invariant that could not be evaluated is UNJUDGED, never a fail', () => {
  assert.equal(invariantMark(true), 'pass');
  assert.equal(invariantMark(false), 'fail');
  for (const v of [null, undefined, 1, 'true', 0, NaN, {}]) {
    assert.equal(invariantMark(v), 'unjudged', `holds: ${JSON.stringify(v)}`);
  }
  assert.deepEqual(invariantTally([{ holds: true }, { holds: false }, { holds: null }, {}]),
    { passed: 1, failed: 1, unjudged: 2 });
});

test('the page draws an invariant through that reading, and never on the truthiness of holds', () => {
  const src = live(read('surfaces/Proportions.jsx'));
  assert.doesNotMatch(src, /holds\s*\?/, 'a ternary on holds collapses unjudged into fail');
  assert.doesNotMatch(src, /['"]pass['"]\s*:\s*['"]fail['"]/);
  assert.match(src, /state=\{invariantMark\(iv\.holds\)\}/, 'the invariant mark is invariantMark’s');
  assert.match(src, /data-judgment=\{judgmentOf\(iv\.holds\)\}/);
});

test('how it was checked is folded unless the reader opened it', () => {
  assert.equal(PROOF_FOLD, 'proof');
  assert.equal(proofOpen(undefined), false, 'folded by default');
  assert.equal(proofOpen(false), false);
  assert.equal(proofOpen(true), true);
  const src = live(read('surfaces/Proportions.jsx'));
  assert.match(src, /proofOpen\(prefs\.fold\(PROOF_FOLD\)\)/);
  assert.match(src, /prefs\.setFold\(PROOF_FOLD, !open\)/);
});

/* ---- the rules ---- */

test('a rule the sources leave to you, one never evaluated and one out of calibration have no verdict', () => {
  assert.equal(ruleState({ value: 9, in_range: true }), 'passed');
  assert.equal(ruleState({ value: 3, in_range: false }), 'failed');
  assert.equal(ruleState({ value: 9, in_range: null }), 'unjudged');
  assert.equal(ruleState({ value: 9, in_range: true, judgment: true }), 'unjudged');
  assert.equal(ruleState({ value: null, in_range: true }), 'unjudged');
  assert.equal(ruleState({ value: 9, in_range: true, error: 'x' }), 'unjudged');
  assert.equal(ruleState({ value: 9, in_range: false, out_of_calibration: true }), 'unjudged');
  assert.equal(ruleState({ value: 9, in_range: true, scope_unjudged: true }), 'unjudged');
  assert.equal(ruleState(null), 'unjudged');
});

test('figures are in the engine’s notation, and a count is a count', () => {
  assert.equal(figureWords(9, 'in'), '9"');
  assert.equal(figureWords(8.526315789473685, 'in'), '8 1/2"');
  assert.equal(figureWords(114, 'in'), '9\'-6"');
  assert.equal(figureWords(7, 'count'), '7 count');
  assert.equal(figureWords(0.25, 'ratio'), '0.25 ratio');
  assert.equal(figureWords(null, 'in'), null);
  assert.equal(rangeWords({ range: [4.5, 18], units: 'in' }), '4 1/2" – 1\'-6"');
  assert.equal(rangeWords({ units: 'in' }), null);
});

/* ---- the address ---- */

test('the measures are read from the address, and one the address does not name is not sent', () => {
  assert.deepEqual(requestFor({ isOrder: false, params: {} }), { members: true },
    'a pack whose module is bound to the ceiling is dimensioned at its own default');
  assert.deepEqual(requestFor({ isOrder: false, params: { ceiling: '108', opening: '40' } }),
    { members: true, ceiling_height: 108, opening_width: 40 });
  assert.deepEqual(requestFor({ isOrder: true, params: {} }), { members: true, column_diameter: DEFAULT_DIAMETER_IN });
  assert.deepEqual(requestFor({ isOrder: true, params: { diameter: '18' } }), { members: true, column_diameter: 18 });
  for (const bad of ['', 'abc', '-3', '0', 'Infinity']) {
    assert.equal(measureParam(bad), null, `${JSON.stringify(bad)} is not a measure`);
    assert.ok(!('ceiling_height' in requestFor({ isOrder: false, params: { ceiling: bad } })));
  }
});

test('a slider rests at the address, else at what was served, clamped to its own range', () => {
  assert.equal(sliderAt('ceiling', { ceiling: '108' }, 114, 108), 108);
  assert.equal(sliderAt('ceiling', {}, 114, 108), 114, 'with no address it shows what the payload was dimensioned at');
  assert.equal(sliderAt('ceiling', {}, null, 108), 108);
  assert.equal(sliderAt('ceiling', { ceiling: '500' }, 114, 108), RANGES.ceiling.max);
  assert.equal(sliderAt('diameter', { diameter: '1' }, null, 12), RANGES.diameter.min);
});

test('the three measures widen rather than narrow, so the strip does not count them as filters', () => {
  assert.equal(FILTER_SPEC.q.type, 'text');
  for (const k of ['ceiling', 'opening', 'diameter']) assert.equal(FILTER_SPEC[k].widens, true, k);
});

test('a pack’s address keeps the reader’s measures, filter and style, and the router reads it back', () => {
  const href = packHref('trim-classical', { pack: 'gibbs-doric', style: 'tidewater-georgian' },
    { ceiling: '108', q: 'trim' });
  assert.equal(href, '#/proportions/trim-classical?style=tidewater-georgian&ceiling=108&q=trim');
  const back = parseHash(href);
  assert.deepEqual(back.selection, { pack: 'trim-classical', style: 'tidewater-georgian' });
  assert.deepEqual(back.params, { ceiling: '108', q: 'trim' });
});

test('a bare #/proportions is the index: no remembered or default pack is drawn', () => {
  const src = live(read('surfaces/Proportions.jsx'));
  assert.doesNotMatch(src, /DEFAULT_PACK|'gibbs-doric'|"gibbs-doric"/);
  assert.match(src, /if \(!packId\)/, 'the page branches on the address naming a pack');
  assert.match(src, /nav\.select\(\{ pack: id \}\)/, 'a pack click writes the address, not local state');
  assert.doesNotMatch(src, /setPackId/);
});

/* ---- who uses it ---- */

const USED = {
  own: ['a', 'b'],
  delivered: [
    { style: 'c', from: 'a', role: 'interior', opted_in: true },
    { style: 'd', from: 'b', role: 'interior', opted_in: false },
  ],
  applies_to_only: ['e'],
  bound_not_in_applies_to: ['b'],
};

test('users are grouped by how the pack reaches them, each relation a glossary record', () => {
  const g = usedByGroups(USED);
  assert.deepEqual(g.map((x) => [x.key, x.term]),
    [['own', 'pack-own'], ['opted-in', 'pack-opted-in'], ['delivered', 'pack-delivered'], ['applies-to-only', null]]);
  assert.deepEqual(g[1].rows, [{ style: 'c', from: 'a', role: 'interior' }]);
  assert.deepEqual(usedByGroups({ own: ['a'] }).map((x) => x.key), ['own'], 'empty groups are left out');
  assert.deepEqual(usedByGroups(null), []);
});

const SP = {
  style: 's', own: [{ pack: 'own-p' }], opted_in: [{ pack: 'opt-p', from: 'g', from_name: 'G' }],
  delivered: [{ from: 'f', from_name: 'F', packs: [{ pack: 'del-p' }] }],
  withheld: [{ pack: 'wh-p', from: 'g' }], declined: [{ pack: 'dec-p', from: 'g' }],
};

test('how a pack reaches the style in hand, in each of the five provenances or none', () => {
  assert.equal(reachOf(SP, 'own-p').term, 'pack-own');
  assert.deepEqual(reachOf(SP, 'opt-p'), { relation: 'opted_in', term: 'pack-opted-in', from: 'g', fromName: 'G' });
  assert.deepEqual(reachOf(SP, 'del-p'), { relation: 'delivered', term: 'pack-delivered', from: 'f', fromName: 'F' });
  assert.equal(reachOf(SP, 'wh-p').term, 'pack-withheld');
  assert.equal(reachOf(SP, 'dec-p').term, 'pack-declined');
  assert.deepEqual(reachOf(SP, 'nowhere'), { relation: 'none', term: null, from: null, fromName: null });
  assert.equal(reachOf(null, 'own-p'), null, 'not yet read is not "none"');
});

test('a style’s packs are the ones that reach it; withheld and declined packs do not', () => {
  assert.deepEqual([...packsOfStyle(SP)].sort(), ['del-p', 'opt-p', 'own-p']);
});

test('every relation the page names is a record the glossary holds', () => {
  const ids = new Set(existsSync(GLOSSARY)
    ? readdirSync(GLOSSARY).filter((f) => f.endsWith('.json')).map((f) => f.slice(0, -5)) : []);
  assert.ok(ids.size > 50, 'the premise: the glossary was read');
  const named = [...usedByGroups(USED).map((g) => g.term),
    ...['own-p', 'opt-p', 'del-p', 'wh-p', 'dec-p'].map((p) => reachOf(SP, p).term)].filter(Boolean);
  for (const t of named) assert.ok(ids.has(t), `no glossary record ${t}`);
});

/* ---- the list ---- */

/* The LIST route's shape: `authority` is the pack's whole authority record, not the string the
   detail route serves. This fixture carried strings until the index was opened in a browser and
   went blank on the first object -- a fixture in the wrong shape agrees with the defect it should
   catch, so the filter test below passed over a page that could not render. */
const PACKS = [
  { id: 'brick', name: 'Brick', kind: 'module-system',
    authority: { source: 'Measured coursing by a Mason', year: null, strength: 'documented', note: 'n' } },
  { id: 'trim', name: 'Classical Trim', kind: 'trim-system',
    authority: { source: 'Regola', author: 'Vignola', year: 1562, strength: 'documented', note: 'n' } },
  { id: 'sash', name: 'Sash', kind: 'module-system',
    authority: { source: 'Survey', author: 'after a Glazier', year: 1800, strength: 'reconstructed', note: 'n' } },
];

test('the list groups by kind in the server’s order, and keeps the pack on screen whatever filters it', () => {
  const words = (k) => ({ 'module-system': 'material module', 'trim-system': 'trim family' })[k];
  assert.deepEqual(packGroups(PACKS).map((g) => [g.kind, g.packs.map((p) => p.id)]),
    [['module-system', ['brick', 'sash']], ['trim-system', ['trim']]]);
  assert.deepEqual(packGroups(PACKS, { q: 'glaz' }).flatMap((g) => g.packs.map((p) => p.id)), ['sash']);
  assert.deepEqual(packGroups(PACKS, { q: 'trim family', words }).flatMap((g) => g.packs.map((p) => p.id)), ['trim'],
    'a reader typing the kind word they see finds it');
  assert.deepEqual(packGroups(PACKS, { q: 'glaz', keep: 'trim' }).flatMap((g) => g.packs.map((p) => p.id)).sort(),
    ['sash', 'trim'], 'the pack being read survives the filter');
  assert.deepEqual(packGroups(PACKS, { only: new Set(['sash']) }).flatMap((g) => g.packs.map((p) => p.id)), ['sash']);
});

test('a pack’s authority in the index is its author, else its source, then its year, from either route’s shape', () => {
  assert.equal(authorityWords(PACKS[1].authority), 'Vignola, 1562');
  assert.equal(authorityWords(PACKS[0].authority), 'Measured coursing by a Mason', 'no author: the source, and no year the record lacks');
  assert.equal(authorityWords('Vignola’s general rules'), 'Vignola’s general rules', 'the detail route’s string is taken as it is');
  assert.equal(authorityWords(null), '');
  assert.equal(authorityWords({ note: 'only a note' }), '', 'a note is not an authority');
  assert.deepEqual(packGroups(PACKS, { q: 'vignola' }).flatMap((g) => g.packs.map((p) => p.id)), ['trim'],
    'the filter reads the same words the index prints');
  // and the index prints THOSE words: a raw `{p.authority}` is an object as a React child.
  const jsx = live(read('surfaces/Proportions.jsx'));
  assert.doesNotMatch(jsx, /\{\s*p\.authority\s*\}/, 'the list route’s authority is a record, not a string');
  assert.match(jsx, /\{authorityWords\(p\.authority\)\}/);
});

test('the pack’s own words: the authority lines, an assembly’s id as words, an order’s name', () => {
  assert.deepEqual(authorityLines({ authority: 'A', assemblies: [{ authority: 'B' }, { authority: 'A' }, {}] }), ['A', 'B']);
  assert.equal(assemblyWords('wall_section_georgian'), 'wall section georgian');
  assert.equal(orderOf('vignola-composite'), 'composite');
  assert.equal(orderOf('gibbs'), null);
});

/* ---- the plate component ---- */

test('the wall-datum plate draws served paths through a transform and builds no curve', () => {
  const src = live(read('components/AssemblyPlate.jsx'));
  assert.match(src, /d=\{b\.d\}/, 'a band’s d is the served face path');
  assert.match(src, /<g transform=\{it\.transform\}>/, 'placed by the one transform');
  assert.match(src, /data-asm=\{b\.asm\}/);
  for (const banned of ['segments', 'Math.cos', 'Math.sin', 'Math.atan', 'sweep', '.a0', '.a1']) {
    assert.ok(!src.includes(banned), `AssemblyPlate.jsx reads ${banned}`);
  }
  assert.match(src, /wordOf\(lookup, 'member'\)/, 'the key’s words are the glossary’s');
  assert.match(src, /<Term id="figure-drawn-from-record" \/> · <Term id="figure-drawn-upright" \/>/,
    'the foot line is the two records');
});

test('the page says out loud what it will not draw', () => {
  const src = live(read('surfaces/Proportions.jsx'));
  assert.match(src, /data-refused="no-assemblies"/, 'a pack with no assemblies says it has no drawing');
  assert.match(src, /data-refused="zones"/, 'no zone dimension string, and the page says why');
  assert.match(src, /data-plate-at=/, 'whether the plate is at your building is the pack’s to say');
});
