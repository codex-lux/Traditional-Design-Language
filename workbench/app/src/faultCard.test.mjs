/* WHAT A FAULT CARD ANSWERS FIRST, AND WHOSE VERDICT IT SHOWS ON A LICENCE (WP-14.11).

   `faults/licence.js` holds the card's two decisions: the reading order (the right way and how to
   spot it before anything else) and the licence verdict (the server's `granted` / `refused` /
   `unjudged`, never collapsed). Every expectation is derived — from `faults/*.json` read with
   `node:fs`, from the verdict vocabulary `mcp_server/core.py` actually writes (read from its
   source), and from `glossary/*.json` — never a count typed in. The component itself imports React
   and cannot run here; what it SAYS is held by reading it, and what it DRAWS is the browser walk's
   fault-card block. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import {
  LICENCE_STATES, LICENCE_TERM, FAULT_CARD_ORDER, licenceOf, faultSections,
  FAULT_SECTION_TERM, COST_SAVED_TERM, FIX_TIERS, FIX_TIER_TERM, FAULT_AXES, FAULT_AXIS_TERM, inUseOf,
} from './faults/licence.js';

const ROOT = new URL('../../../', import.meta.url);
const read = (p) => readFileSync(new URL(p, ROOT), 'utf8');
const live = (s) => s.replace(/\/\*[\s\S]*?\*\//g, '').replace(/(^|[\s;,{}()])\/\/[^\n]*/g, '$1');

const FAULTS = readdirSync(new URL('faults/', ROOT)).filter((f) => f.endsWith('.json')).sort()
  .map((f) => JSON.parse(read(`faults/${f}`)));
const STYLES = new Set(readdirSync(new URL('styles/', ROOT)).filter((f) => f.endsWith('.json'))
  .map((f) => f.replace(/\.json$/, '')));

/* The card the server writes (`core._exception_card`) for a verdict, on a real exception record. */
const served = (exc, granted, because = 'the server says why') => ({
  ...exc, granted, granted_because: because, precondition_not_evaluated: [],
});

/* The fault as `FaultCorpus` hands it to the card: `fix` from `fixes`, each exception's `why` as its
   `statement` (that surface's own adapter, unchanged by this package). */
const asCard = (f, forThisStyle) => ({
  ...f, fix: f.fixes,
  exceptions: (f.exceptions || []).map((e) => ({ ...e, statement: e.why })),
  ...(forThisStyle === undefined ? {} : { for_this_style: forThisStyle }),
});

test('the verdict vocabulary is the one core.grant_exception writes, and each word is a glossary record', () => {
  const core = read('mcp_server/core.py');
  const written = new Set([...core.matchAll(/verdict="([a-z]+)"|"verdict":\s*"([a-z]+)"/g)].map((m) => m[1] ?? m[2]));
  assert.deepEqual([...written].sort(), [...LICENCE_STATES].sort(),
    'core.grant_exception writes exactly the three verdicts licence.js reads');
  assert.match(core, /"granted":\s*g\["verdict"\],\s*"granted_because":\s*g\["why"\]/,
    'the premise: _exception_card serves the verdict as `granted` and its reason as `granted_because`');
  assert.match(core, /out\["for_this_style"\]\s*=\s*\{[\s\S]{0,300}"exception":\s*_exception_card\(f, style\)/,
    'the premise: get_fault serves the card under for_this_style.exception');
  const ids = new Set(readdirSync(new URL('glossary/', ROOT)).filter((f) => f.endsWith('.json'))
    .map((f) => JSON.parse(read(`glossary/${f}`)).id));
  for (const s of LICENCE_STATES) assert.ok(ids.has(LICENCE_TERM[s]), `no glossary record ${LICENCE_TERM[s]}`);
  assert.equal(LICENCE_TERM.unjudged, 'judgment-unjudged');
});

test('every licence in the corpus shows the verdict it was served, and never "granted" unless served so', () => {
  let n = 0;
  for (const f of FAULTS) {
    for (const e of f.exceptions || []) {
      if (!STYLES.has(e.style)) continue;               // the construction:/region: pseudo-ids
      n += 1;
      for (const v of LICENCE_STATES) {
        const l = licenceOf(asCard(f, { exception: served(e, v) }), e.style);
        assert.equal(l.state, v, `${f.id} for ${e.style}: served ${v}`);
        assert.equal(l.termId, LICENCE_TERM[v]);
        assert.equal(l.statement, e.why, 'the licence’s own words, beside the verdict');
        assert.equal(l.because, 'the server says why');
        assert.equal(l.served, true);
      }
      // no verdict in hand: the fetch carried no for_this_style, or it is about another style
      for (const fts of [undefined, null, {}, { exception: null },
        { exception: served({ ...e, style: e.style + '-other' }, 'granted') },
        { exception: { ...served(e, 'granted'), granted: true } },
        { exception: { ...served(e, 'granted'), granted: 'GRANTED' } }]) {
        const l = licenceOf(asCard(f, fts), e.style);
        assert.equal(l.state, 'unjudged', `${f.id} for ${e.style}: ${JSON.stringify(fts)?.slice(0, 60)}`);
        assert.equal(l.termId, 'judgment-unjudged');
      }
    }
  }
  assert.ok(n > 0, 'the premise: the corpus carries licences for real styles');
});

test('no licence where no style is in view or the style holds none', () => {
  const f = FAULTS.find((x) => (x.exceptions || []).length > 0);
  assert.ok(f);
  assert.equal(licenceOf(asCard(f), ''), null);
  assert.equal(licenceOf(asCard(f), undefined), null);
  assert.equal(licenceOf(asCard(f, { exception: null }), 'no-such-style'), null);
  assert.equal(licenceOf(null, 'x'), null);
  // a served card with no record in the array still shows, and still with its verdict
  const only = licenceOf({ exceptions: [], for_this_style: { exception: { style: 's', why: 'w', granted: 'refused' } } }, 's');
  assert.equal(only.state, 'refused');
  assert.equal(only.statement, 'w');
});

test('the right way and how to spot it come first, on every fault the corpus holds', () => {
  assert.deepEqual(FAULT_CARD_ORDER.slice(0, 2), ['correct_practice', 'detection']);
  assert.equal(new Set(FAULT_CARD_ORDER).size, FAULT_CARD_ORDER.length);
  const both = FAULTS.filter((f) => typeof f.correct_practice === 'string' && f.correct_practice.trim()
    && typeof f.detection === 'string' && f.detection.trim());
  assert.ok(both.length > 0 && both.length === FAULTS.length,
    'the premise: every fault record carries both answers (the card rendered neither)');
  for (const f of FAULTS) {
    const secs = faultSections(asCard(f), undefined);
    assert.deepEqual(secs.slice(0, 2), ['correct_practice', 'detection'], f.id);
    assert.ok(!secs.includes('licence'), 'no style in view, no licence');
    const withStyle = (f.exceptions || []).find((e) => STYLES.has(e.style));
    if (withStyle) {
      const s2 = faultSections(asCard(f, { exception: served(withStyle, 'unjudged') }), withStyle.style);
      assert.equal(s2.indexOf('licence'), 2, `${f.id}: the licence follows the answers and leads the rule`);
    }
  }
  // a field the record leaves empty is omitted, never an empty heading
  assert.deepEqual(faultSections({ correct_practice: '  ', detection: 'd', symptom: '' }, null), ['detection']);
});

test('the card draws the verdict by literal glossary id, takes the order from licence.js, and reads no licence itself', () => {
  const src = live(read('workbench/app/src/components/FaultCard.jsx'));
  assert.match(src, /from '\.\.\/faults\/licence\.js'/);
  assert.match(src, /licenceOf\(fault, styleInView\)/);
  assert.match(src, /faultSections\(fault, styleInView\)\.map/, 'the sections render in licence.js’s order');
  for (const s of LICENCE_STATES) assert.match(src, new RegExp(`<Term id="${LICENCE_TERM[s]}" />`), s);
  assert.doesNotMatch(src, /\.exceptions\b/, 'the card filtering the raw exceptions itself would bypass the verdict');
  assert.match(src, /fault\.correct_practice/);
  assert.match(src, /fault\.detection/);
  assert.doesNotMatch(src, /--ink-4/, 'no readable text in --ink-4');
});

/* ---- the card's own words are records (WP-14.17, tranche 2's PRD §A.3) ---- */

const GLOSSARY_IDS = new Set(readdirSync(new URL('glossary/', ROOT)).filter((f) => f.endsWith('.json'))
  .map((f) => JSON.parse(read(`glossary/${f}`)).id));
const FAULT_SCHEMA = JSON.parse(read('schema/fault.schema.json'));

test('every heading, tier word and axis label the card draws names a glossary record that exists', () => {
  assert.deepEqual(Object.keys(FAULT_SECTION_TERM), [...FAULT_CARD_ORDER],
    'one heading per section, keyed and ordered by FAULT_CARD_ORDER');
  assert.deepEqual(Object.keys(FIX_TIER_TERM), [...FIX_TIERS]);
  assert.deepEqual(Object.keys(FAULT_AXIS_TERM), [...FAULT_AXES]);
  const ids = [...Object.values(FAULT_SECTION_TERM), COST_SAVED_TERM, ...Object.values(FIX_TIER_TERM),
    ...Object.values(FAULT_AXIS_TERM)];
  assert.ok(ids.length > FAULT_CARD_ORDER.length, 'the premise: the tables name more than the headings');
  assert.deepEqual(ids.filter((id) => !GLOSSARY_IDS.has(id)), [],
    'each of these would render "no entry: …" on the card; write the record or fix the id');
  assert.equal(new Set(ids).size, ids.length, 'no record labels two parts of the card');
});

test('the tiers are the schema’s own fixes, in its order, and each axis reads a field the record really has', () => {
  assert.deepEqual([...FIX_TIERS], Object.keys(FAULT_SCHEMA.properties.fixes.properties));
  for (const field of FAULT_AXES) {
    const [head, sub] = field.split('.');
    const prop = FAULT_SCHEMA.properties[head];
    assert.ok(prop, `${field}: the fault schema has no ${head}`);
    if (sub) assert.ok(prop.properties && prop.properties[sub], `${field}: the fault schema has no ${field}`);
  }
  /* The second severity axis is the in-use severity and not the frequency (the label sat over the
     wrong field until WP-14.17): each is its own record, and the in-use one reads severity_in_use. */
  assert.equal(FAULT_AXIS_TERM.severity_in_use, 'fault-axis-how-it-lives');
  assert.equal(FAULT_AXIS_TERM.frequency, 'fault-axis-frequency');
  const stated = FAULTS.filter((f) => inUseOf(f) !== null);
  assert.ok(stated.length > 0 && stated.length < FAULTS.length,
    'the premise: some faults state how they live and some do not, so both branches are real');
  for (const f of FAULTS) {
    assert.equal(inUseOf(f), typeof f.severity_in_use === 'string' ? f.severity_in_use : null, f.id);
  }
  assert.equal(inUseOf(null), null);
  assert.equal(inUseOf({ severity_in_use: '' }), null, 'an empty value states nothing');
});

/* JSX text the card writes: runs after a tag's `>` or an expression's `}`, up to the next `<` or `{`,
   carrying a letter. A run that opens with a comma is the next key of an object literal
   (`}, refused: {`), not text on the page. A reader of text, not a parser; the fixture below
   proves what it finds and what it leaves. */
function jsxText(src) {
  return [...src.matchAll(/(?<!=)[>}]([^<>{}]*)(?=[<{])/g)].map((m) => m[1].replace(/\s+/g, ' ').trim())
    .filter((t) => /[A-Za-z]/.test(t) && !/[;=()'"`]/.test(t) && !/^,/.test(t)
      && !/^(else|return|from|import|const|let|if|finally)\b/.test(t));
}

test('the card writes no word about its own parts: every label is a Term, drawn from licence.js’s tables', () => {
  assert.deepEqual(jsxText('<div style={EYE}>symptom</div><span>{a} — {b}</span>'
    + '<div>cause — driver: {x}</div>const F = { a: {x: 1}, refused: {y: 2} };'), ['symptom', 'cause — driver:'],
    'the premise: the reader finds a label typed as JSX text, and not punctuation or an object key');
  const src = live(read('workbench/app/src/components/FaultCard.jsx'));
  assert.deepEqual(jsxText(src), [],
    'a word typed into the card is a definition nothing checks: make it a glossary record');
  assert.doesNotMatch(src, /\blabel="/, 'an axis label as a string');
  assert.doesNotMatch(src, /three tiers|beside the statement/, 'the retired self-explanations');
  assert.doesNotMatch(src, /\['right', 'cheap', 'dishonest'\]/, 'the tiers are FIX_TIERS, one list');
  assert.match(src, /<Term id=\{FAULT_SECTION_TERM\[section\]\} \/>/, 'a heading is its section’s record');
  assert.match(src, /<Term id=\{FIX_TIER_TERM\[tier\]\} \/>/, 'a tier word is its tier’s record');
  assert.match(src, /<Term id=\{FAULT_AXIS_TERM\[field\]\} \/>/, 'an axis label is its field’s record');
  assert.match(src, /<Term id=\{COST_SAVED_TERM\} \/>/);
  assert.match(src, /inUseOf\(fault\)/, 'how it lives is drawn from the record’s severity_in_use');
  for (const k of FAULT_CARD_ORDER.filter((s) => s !== 'licence' && s !== 'cause')) {
    assert.match(src, new RegExp(`<Head section="${k}"`), `${k}: its heading is drawn through Head`);
  }
});
