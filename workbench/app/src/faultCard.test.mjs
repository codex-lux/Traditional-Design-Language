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
import { LICENCE_STATES, LICENCE_TERM, FAULT_CARD_ORDER, licenceOf, faultSections } from './faults/licence.js';

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
