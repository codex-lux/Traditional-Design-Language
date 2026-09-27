/* DEFINITIONS ON SCREEN: THE DECISIONS, AND THE RULES THE COMPONENTS MUST NOT BREAK (WP-14.8).

   `components/Term.jsx`, `RecordLink.jsx`, `PageHead.jsx` and `surfaces/Glossary.jsx` import
   React and cannot run under `node --test` (`no_bare_imports.test.mjs`). So every decision they
   make lives in a pure module — `glossary/termView.js`, `names/recordLink.js`,
   `glossary/listing.js` — and is driven here; and the rules that are about the COMPONENTS
   themselves (no definition prop, no fallback gloss, no inline `outline: none`, no readable
   `--ink-4`, the focus ring, no glossary JSON in the bundle's import graph) are held by reading
   their source. A source guard is the weaker form and says so: it is used here only for
   properties that are a matter of what the file SAYS, never for behaviour. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { indexTerms } from './glossary/lookup.js';
import {
  noEntry, noGlossary, keyFor, provenanceOf, termHref, termView, describeTerm, wordOf, wordForCite,
  wordForValue,
} from './glossary/termView.js';
import { linkView, isPlainPrimaryClick } from './names/recordLink.js';
import { glossaryListing, matchesQuery, haystackOf } from './glossary/listing.js';
import { hrefFor, citeHref } from './router.js';

const SRC = fileURLToPath(new URL('./', import.meta.url));
const read = (rel) => readFileSync(join(SRC, rel), 'utf8');
// Block comments, and line comments whether they start a line or trail code (a `//` after `:` is
// a URL inside a string and is kept).
const stripComments = (s) => s.replace(/\/\*[\s\S]*?\*\//g, '')
  .replace(/(^|[\s;,{}()])\/\/[^\n]*/g, '$1');

/* A payload in §C.1's shape, small enough to reason about in the test. */
function payload() {
  const terms = [
    { id: 'rank-style', term: 'style', family: 'rank', order: 0, definition: 'A buildable style.',
      kind: 'editorial', basis: 'x', reads: ['schema/style-node.schema.json'] },
    { id: 'binding-forbidden', term: 'forbidden', family: 'binding', order: 3, sense: 'in a kit',
      definition: 'The style refuses this slot.', analogy: 'Like a crossed-out box.',
      kind: 'sourced', sources: ['Ware 1756', 'Kerr 1864'], reads: [],
      confusable_with: ['binding-open', 'no-such-record'],
      binds: [{ field: 'kit.binding', value: 'forbidden' }] },
    { id: 'binding-open', term: 'open', family: 'binding', order: 2, sense: 'in a kit',
      definition: 'The style declines to constrain this slot.', kind: 'editorial', basis: 'x',
      reads: ['schema/kit.schema.json', 'docs/inheritance.md'],
      aka: ['unbound'], binds: [{ field: 'kit.binding', value: 'open' }] },
  ];
  return {
    version: '0.1.0+test', count: terms.length, terms,
    by_family: { product: [], rank: ['rank-style'], binding: ['binding-open', 'binding-forbidden'] },
    by_field: { 'kit.binding': { open: 'binding-open', forbidden: 'binding-forbidden' } },
  };
}
const ready = () => ({ status: 'ready', lookup: indexTerms(payload()), error: null });

/* ---- termView: what a Term shows, in four states ---- */

test('noEntry is the PRD’s one spelling, and its sibling names the other failure', () => {
  assert.equal(noEntry('binding-open'), 'no entry: binding-open');
  assert.equal(noGlossary('binding-open'), 'glossary unavailable: binding-open');
  assert.notEqual(noEntry('x'), noGlossary('x'), 'a gap in the records and a failed read read differently');
});

test('loading claims nothing: no word, no text, no definition', () => {
  for (const g of [{ status: 'loading' }, undefined, null, { status: 'ready', lookup: null }]) {
    const v = termView(g, { id: 'binding-open' });
    assert.equal(v.state, 'loading');
    assert.equal(v.key, 'binding-open');
    assert.deepEqual(Object.keys(v).sort(), ['key', 'state']);
  }
});

test('a glossary that could not be read says so, with the reason, and is not "no entry"', () => {
  const err = new Error('503');
  const v = termView({ status: 'failed', lookup: null, error: err }, { id: 'binding-open' });
  assert.equal(v.state, 'failed');
  assert.equal(v.text, 'glossary unavailable: binding-open');
  assert.equal(v.error, err);
});

test('a record the glossary does not hold is noEntry, under the id the caller asked for', () => {
  const v = termView(ready(), { id: 'no-such-word' });
  assert.equal(v.state, 'missing');
  assert.equal(v.text, 'no entry: no-such-word');
  const f = termView(ready(), { field: 'kit.binding', value: 'extends' });
  assert.equal(f.state, 'missing');
  assert.equal(f.text, 'no entry: kit.binding:extends', 'a bound value with no record names the field and value');
});

test('a ready record shows only the record’s own words, and the confusables as links to their pages', () => {
  const v = termView(ready(), { id: 'binding-forbidden' });
  assert.equal(v.state, 'ready');
  assert.equal(v.word, 'forbidden');
  assert.equal(v.sense, 'in a kit');
  assert.equal(v.definition, 'The style refuses this slot.');
  assert.equal(v.analogy, 'Like a crossed-out box.');
  assert.equal(v.moreHref, '#/cite/term:binding-forbidden', 'the PRD’s address for "more"');
  assert.equal(v.confusables.length, 2, 'a declared confusable with no record is kept in its place');
  assert.deepEqual({ ...v.confusables[0] }, {
    id: 'binding-open', term: 'open', sense: 'in a kit', href: '#/cite/term:binding-open' });
  assert.deepEqual({ ...v.confusables[1] }, { missing: 'no-such-record', text: 'no entry: no-such-record' });
  // the same view through the bound field and value
  const b = termView(ready(), { field: 'kit.binding', value: 'forbidden' });
  assert.equal(b.key, 'binding-forbidden');
  assert.equal(b.definition, v.definition);
});

test('the addresses are the router’s: termHref is citeHref, never a template of its own', () => {
  assert.equal(termHref('binding-open'), citeHref('term:binding-open'));
  const src = stripComments(read('glossary/termView.js'));
  assert.doesNotMatch(src, /#\/cite\//, 'termView.js must not spell the citation address itself');
  assert.doesNotMatch(src, /new RegExp|\/\^?\(?[a-z]+:/i, 'and must hold no pattern of the grammar');
});

test('provenance: the kind, then the first source of a sourced record or the files an editorial one read', () => {
  const lk = indexTerms(payload());
  assert.deepEqual(provenanceOf(lk.term('binding-forbidden')), { kind: 'sourced', items: ['Ware 1756'] });
  assert.deepEqual(provenanceOf(lk.term('binding-open')),
    { kind: 'editorial', items: ['schema/kit.schema.json', 'docs/inheritance.md'] });
  assert.deepEqual(provenanceOf({ kind: 'editorial' }), { kind: 'editorial', items: [] },
    'a record served without reads says none, and the app does not parse its basis for them');
  assert.deepEqual(provenanceOf({}), { kind: null, items: [] });
});

test('keyFor: the id, or field:value, and nothing invented', () => {
  assert.equal(keyFor({ id: 'x' }), 'x');
  assert.equal(keyFor({ field: 'kit.binding', value: 'open' }), 'kit.binding:open');
  assert.equal(keyFor({}), '');
});

test('describeTerm, for a control a Term may not sit inside', () => {
  assert.deepEqual(describeTerm(ready(), 'binding-open'), {
    state: 'ready', text: 'The style declines to constrain this slot.',
    title: 'The style declines to constrain this slot.' });
  assert.deepEqual(describeTerm({ status: 'loading' }, 'binding-open'),
    { state: 'loading', text: '', title: undefined }, 'loading describes nothing');
  assert.equal(describeTerm(ready(), 'nope').text, 'no entry: nope');
  assert.equal(describeTerm({ status: 'failed' }, 'nope').title, 'glossary unavailable: nope');
});

test('a link to a glossary record is worded by the record, or by noEntry, and any other cite is left to the name layer', () => {
  const { lookup } = ready();
  assert.equal(wordOf(lookup, 'binding-open'), 'open');
  assert.equal(wordOf(lookup, 'no-such-record'), 'no entry: no-such-record');
  assert.equal(wordForCite(lookup, 'term:binding-forbidden'), 'forbidden');
  assert.equal(wordForCite(lookup, 'term:no-such-record'), 'no entry: no-such-record',
    'a term: cite with no record says so, under its own id, and is never left to print raw');
  // Another kind is the name layer's to word; `undefined` children are what hand it there.
  assert.equal(wordForCite(lookup, 'style:tidewater-georgian'), undefined);
  assert.equal(wordForCite(lookup, 'not a cite'), undefined);
  assert.equal(wordForCite(lookup, null), undefined);
});

test('a bound value is worded through by_field, and a value no record names says which is missing (WP-14.17)', () => {
  const { lookup } = ready();
  // the Glossary's family chips: a button a Term may not sit inside, worded by the value's record
  assert.equal(wordForValue(lookup, 'kit.binding', 'forbidden'), 'forbidden');
  assert.equal(wordForValue(lookup, 'kit.binding', 'extends'), 'no entry: kit.binding:extends',
    'a value by_field does not carry is missing under field:value, never printed raw');
  assert.equal(wordForValue(lookup, 'glossary.family', 'rank'), 'no entry: glossary.family:rank',
    'the id is by_field’s: a record named family-rank is not reached by building its id');
  const withFamily = indexTerms({ ...payload(),
    terms: [...payload().terms, { id: 'family-rank', term: 'Ranks', family: 'family', order: 5,
      definition: 'x', kind: 'editorial', basis: 'x' }],
    by_field: { ...payload().by_field, 'glossary.family': { rank: 'family-rank' } } });
  assert.equal(wordForValue(withFamily, 'glossary.family', 'rank'), 'Ranks');
});

/* ---- recordLink: a name first, an address from the router ---- */

test('a link to a record takes the router’s address and the index’s name, with the id as its note', () => {
  const idx = [{ cite: 'pack:trim-classical', id: 'trim-classical', name: 'Classical Trim' }];
  const v = linkView('pack:trim-classical', { style: 'tidewater-georgian' }, idx);
  assert.equal(v.href, hrefFor('pack:trim-classical', { style: 'tidewater-georgian' }));
  assert.ok(v.href && v.href.startsWith('#/'), 'the premise: the router can read a pack cite');
  assert.equal(v.name, 'Classical Trim');
  assert.equal(v.note, 'trim-classical');
  assert.equal(v.resolved, true);
});

test('a cite the index does not name shows itself and carries no second copy as a note', () => {
  const v = linkView('pack:not-in-the-index', undefined, []);
  assert.equal(v.name, 'pack:not-in-the-index');
  assert.equal(v.note, null);
  assert.equal(v.resolved, false);
  assert.ok(v.href, 'an unnamed record is still an address the router can read');
});

test('a cite the router cannot read has no address, so it is drawn as text and never as a link', () => {
  for (const bad of ['not a cite', '', 'nosuchkind:x', null, 7]) {
    assert.equal(linkView(bad, undefined, []).href, null, `for ${JSON.stringify(bad)}`);
  }
});

test('only a plain primary click is the app’s; every modified click is the browser’s', () => {
  const base = { button: 0, defaultPrevented: false, metaKey: false, ctrlKey: false, shiftKey: false, altKey: false };
  assert.ok(isPlainPrimaryClick(base));
  for (const k of ['metaKey', 'ctrlKey', 'shiftKey', 'altKey']) assert.ok(!isPlainPrimaryClick({ ...base, [k]: true }), k);
  assert.ok(!isPlainPrimaryClick({ ...base, button: 1 }), 'middle click opens a tab');
  assert.ok(!isPlainPrimaryClick({ ...base, defaultPrevented: true }));
  assert.ok(!isPlainPrimaryClick(null));
});

/* ---- listing: the Glossary index as data ---- */

test('the index lists families in by_family’s order and drops the empty ones', () => {
  const g = glossaryListing(indexTerms(payload()), {});
  assert.deepEqual(g.map((x) => x.family), ['rank', 'binding'], 'product is empty and is not drawn');
  assert.deepEqual(g[1].terms.map((t) => t.id), ['binding-forbidden', 'binding-open'],
    'records keep the payload’s order within a family');
});

test('a query narrows by the words a reader types — term, other words, sense and id — never by the definition', () => {
  const lk = indexTerms(payload());
  const ids = (q) => glossaryListing(lk, { q }).flatMap((x) => x.terms.map((t) => t.id));
  assert.deepEqual(ids('unbound'), ['binding-open'], 'aka is searched');
  assert.deepEqual(ids('forbid'), ['binding-forbidden']);
  assert.deepEqual(ids('KIT'), ['binding-forbidden', 'binding-open'], 'case-folded, and the sense is searched');
  assert.deepEqual(ids('declines'), [], 'the definition is not in the haystack');
  assert.deepEqual(ids('in kit open'), ['binding-open'], 'every token must appear');
  assert.ok(matchesQuery({ term: 'x' }, '   '), 'a blank query matches everything');
  assert.doesNotMatch(haystackOf(lk.term('binding-open')), /declines/);
});

test('a family filter narrows to that family, and an unknown one to nothing', () => {
  const lk = indexTerms(payload());
  assert.deepEqual(glossaryListing(lk, { family: 'rank' }).map((x) => x.family), ['rank']);
  assert.deepEqual(glossaryListing(lk, { family: 'nope' }), []);
  assert.deepEqual(glossaryListing(null, {}), []);
});

/* ---- the components, held by what their source says ---- */

/* The props a function component destructures, read from its own `export function Name({ ... })`. */
function destructuredProps(src, name) {
  const m = src.match(new RegExp(`export function ${name}\\(\\{([^}]*)\\}\\)`));
  assert.ok(m, `the premise: ${name} destructures its props in its signature`);
  return m[1].split(',').map((s) => s.trim()).filter(Boolean).sort();
}

test('Term takes id, or field and value, and children — and there is no definition prop and no fallback', () => {
  const src = read('components/Term.jsx');
  assert.deepEqual(destructuredProps(src, 'Term'), ['children', 'field', 'id', 'value']);
  const live = stripComments(src);
  assert.doesNotMatch(live, /\bprops\b|\.\.\.rest|arguments\b/, 'Term may not read props it did not name');
  /* No phrase of the app's own. The popover's two labels are the PRD's; everything else a Term
     shows is the record's, reached through termView. A literal with two or more words in the
     live code is the app writing a gloss. */
  const allowed = new Set(['not to be confused with', 'more']);
  const literals = [...live.matchAll(/'([^'\n]*)'|"([^"\n]*)"|`([^`\n]*)`/g)].map((m) => m[1] ?? m[2] ?? m[3]);
  // JSX text: after a tag's closing `>` (never an arrow's `=>`), up to the next tag or expression.
  const jsxText = [...live.matchAll(/(?<!=)>([^<>{}();=]*[A-Za-z][^<>{}();=]*)(?=[<{])/g)]
    .map((m) => m[1].replace(/\s+/g, ' ').trim());
  const phrases = [...literals, ...jsxText]
    .filter((s) => /[A-Za-z]{2,}\s+[A-Za-z]{2,}/.test(s) && !allowed.has(s.trim()));
  assert.deepEqual(phrases, [], 'Term.jsx may carry no words for a reader but its two labels');
  assert.ok(jsxText.includes('not to be confused with') && jsxText.includes('more'),
    'the premise: the scan reads the JSX text the popover does carry');
});

test('PageHead takes one prop, and RecordLink the three the PRD names', () => {
  assert.deepEqual(destructuredProps(read('components/PageHead.jsx'), 'PageHead'), ['termId']);
  assert.deepEqual(destructuredProps(read('components/RecordLink.jsx'), 'RecordLink'), ['children', 'cite', 'ctx']);
});

test('a link to a cite a glossary record carries is worded through wordForCite, never left bare', () => {
  /* PageHead's "Try" and the Glossary's "See" and "Try" link to cites a RECORD supplies, and a
     `term:` cite has no entry in the search index, so a bare `<RecordLink cite={…} />` prints the
     raw cite (four surface records' `try` is a `term:`). A source guard, because the components
     import React; the arithmetic it relies on is `wordForCite`, driven above. */
  for (const f of ['components/PageHead.jsx', 'surfaces/Glossary.jsx']) {
    const src = stripComments(read(f));
    assert.doesNotMatch(src, /<RecordLink\b[^>]*\/>/, `${f}: a self-closing RecordLink leaves a term: cite unworded`);
    assert.match(src, /wordForCite\(/, `${f}: the premise — it words its cites through wordForCite`);
  }
});

function jsxFiles(dir = SRC, out = []) {
  for (const f of readdirSync(dir).sort()) {
    const p = join(dir, f);
    if (statSync(p).isDirectory()) jsxFiles(p, out);
    else if (f.endsWith('.jsx')) out.push(p);
  }
  return out;
}

test('no component sets an inline outline: none, which would beat the focus ring the stylesheet draws', () => {
  const files = jsxFiles();
  assert.ok(files.length > 20, 'the premise: the walk found the app’s components');
  const hits = files.filter((p) => /outline:\s*['"]none['"]|outline:\s*0\b/.test(stripComments(readFileSync(p, 'utf8'))));
  assert.deepEqual(hits.map((p) => p.slice(SRC.length)), []);
});

test('the stylesheet draws a focus ring for everything, holds no floor on the shell for a reflowing page, and marks a Term', () => {
  const css = read('theme/tokens.css');
  assert.match(css, /(^|\n):focus-visible\{outline:2px solid var\(--border-focus\)/, 'a GLOBAL :focus-visible, not a:focus-visible alone');
  /* THE PROPERTY, NOT THE RULE THAT ONCE HELD IT (re-cut by WP-14.30). This asserted the literal
     `#root[data-reflow]{min-width:0}`, which released a 1380 px floor on `#root`. The floor is
     gone, so the release has nothing to release; what a reflowing page is owed is that no rule
     styling `#root` ITSELF -- bare or under any attribute -- gives it a minimum width. A floor,
     where the PRD keeps one, is on `<main>` (layout.test.mjs holds that half). */
  const live = css.replace(/\/\*[\s\S]*?\*\//g, '');
  const onRoot = [...live.matchAll(/(^|[},\s])(#root(?:\[[^\]]*\])*)\s*\{([^}]*)\}/g)];
  assert.ok(onRoot.length > 0, 'the premise: the scan finds the rules that style #root itself');
  const floors = onRoot.filter(([, , , body]) => /min-width\s*:\s*(?!0(px)?\s*(;|$))/.test(body))
    .map(([, , sel, body]) => `${sel}{${body}}`);
  assert.deepEqual(floors, [], 'a width floor on the shell makes every page scroll sideways below it');
  assert.match(css, /\.tdl-term\{[^}]*text-decoration:underline dotted var\(--ink-2\)/);
  const block = css.slice(css.indexOf('DEFINITIONS ON SCREEN (WP-14.8)'));
  assert.ok(block.length > 1000, 'the premise: the package’s block is where this test looks');
  assert.doesNotMatch(block.replace(/\/\*[\s\S]*?\*\//g, ''), /#[0-9A-Fa-f]{3,8}\b|rgba?\(|hsla?\(/,
    'the package adds no colour: every colour in its block is a token');
});

test('no readable text in --ink-4 in the new components or the package’s stylesheet block', () => {
  const files = ['components/Term.jsx', 'components/PageHead.jsx', 'components/RecordLink.jsx',
    'surfaces/Glossary.jsx', 'components/Eyebrow.jsx'];
  for (const f of files) {
    const live = stripComments(read(f));
    const uses = [...live.matchAll(/--ink-4/g)].length;
    // Eyebrow kept `quiet: 'var(--ink-4)'` for a caller who asked for it by name until WP-14.31,
    // which removed the tone: an eyebrow is always text. The whole of src is held by
    // src/inks.test.mjs now; this file keeps its stricter rule for its own files (no --ink-4 at
    // all, text or not).
    assert.equal(uses, 0, `${f} uses --ink-4 ${uses} time(s)`);
  }
  const css = read('theme/tokens.css');
  const block = css.slice(css.indexOf('DEFINITIONS ON SCREEN (WP-14.8)')).replace(/\/\*[\s\S]*?\*\//g, '');
  assert.doesNotMatch(block, /--ink-4/);
});

test('the eyebrow’s default ink is --ink-2', () => {
  const src = stripComments(read('components/Eyebrow.jsx'));
  assert.match(src, /tone = 'secondary'/);
  assert.match(src, /secondary: 'var\(--ink-2\)'/);
  assert.match(src, /tones\[tone\] \|\| tones\.secondary/);
});

test('the glossary is fetched, never imported: no source file reaches glossary/*.json', () => {
  const offenders = [];
  const walk = (dir) => {
    for (const f of readdirSync(dir).sort()) {
      const p = join(dir, f);
      if (statSync(p).isDirectory()) { walk(p); continue; }
      if (!/\.(jsx?|mjs)$/.test(f) || f.endsWith('.test.mjs')) continue;
      const live = stripComments(readFileSync(p, 'utf8'));
      if (/import[^;]*['"][^'"]*glossary\/[^'"]*\.json['"]/.test(live)
        || /import\([^)]*glossary\/[^)]*\.json/.test(live)) offenders.push(p.slice(SRC.length));
    }
  };
  walk(SRC);
  assert.deepEqual(offenders, []);
  const hook = stripComments(read('api/useGlossary.js'));
  assert.match(hook, /api\.glossary\(\)/, 'useGlossary reads GET /api/glossary through the client');
});

test('the client names the two glossary routes the server contract gives', () => {
  const src = read('api/client.js');
  assert.match(src, /glossary: \(\) => getJSON\('\/api\/glossary'\)/);
  assert.match(src, /glossaryTerm: \(id\) => getJSON\(`\/api\/glossary\/\$\{seg\(id\)\}`\)/);
});
