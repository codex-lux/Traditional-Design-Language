/* THE READER IS NOT TOLD THE BUILD'S HISTORY (WP-14.31).

   A work-package numeral ("WP-9.2"), an open-question number ("OQ 54") and a circled surface
   numeral ("⑤ → ⑥", the order the surfaces were BUILT in) are the project's bookkeeping. They
   were written into the page -- in tooltips, captions and a card's footer ("forthcoming —
   WP-5.3 is not built") -- where they tell a reader which package made a thing and nothing about
   the thing. A reader cannot look one up: the app has no page for a work package and the open
   questions live in the repository. So the page carries none, and this file refuses one BY
   IDENTITY: a row is (file, the literal text), the baseline may only shrink, and it shrinks in
   the commit that earns it -- the copy ratchet's own mechanism, for a third kind of copy.

   WHAT IS READ is what reaches the page: JSX text and every string literal in the live source of
   a `.jsx` or `.js` file under `src/` -- comments are the project talking to itself and are
   stripped first, tests are not source. A literal that is code and not copy (an import path, a
   key) does not carry one of these patterns, which is measured: the scan over the tree finds only
   copy.

   THE BASELINE IS EMPTY, SO THIS IS A BAN (WP-14.33's audit). Its one row was the order plate's
   caption in `surfaces/Proportions.jsx`, which named OQ 65 twice and told a reader "the corpus
   uses both" -- a corpus fact, and a closed question cited to someone who cannot look it up. It was
   left because the plate was another package's; the audit's copy fix took the citation and the
   claim out together. `READER_COPY_PRINT=1 node --test src/readerCopy.test.mjs` prints the current rows.

   AND THE PALETTE'S KIND TABLE IS HELD TO THE GLOSSARY HERE, because it is where the palette's
   group headings come from now (`search/match.js::KIND_TERM`): every kind the search orders has
   a record, and every record it names exists. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, statSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { KIND_ORDER, KIND_TERM } from './search/match.js';
import { stripComments } from './sourceReader.mjs';

const SRC = fileURLToPath(new URL('./', import.meta.url));
const GLOSSARY = fileURLToPath(new URL('../../../glossary/', import.meta.url));

export const HISTORY = /\bWP-\d|\bOQ\s*\d|[①-⑳⓪-⓿❶-➓]/;

/* Comments are not copy, and they are stripped by `sourceReader.mjs`, the lexer both copy
   ratchets share (WP-14.33's audit): the pair of regular expressions this file carried read the
   file-type pattern in `Transcription.jsx`'s `accept=` attribute as the start of a comment and was
   blind to the 79 lines after it. */
const squash = (s) => s.replace(/\s+/g, ' ').trim();

/* source → the history rows: every line of LIVE source carrying a work package, an
   open-question number or a circled numeral, squashed. With the comments gone, none of the three
   can be code -- `WP-2` is no identifier and `⑤` no operator -- so a line that carries one is
   carrying copy, whether it is a string literal, JSX text or a template. A LINE and not a parsed
   text run, because the first version parsed runs and was blind twice on its own fixtures: a run
   holding `;` was set aside as code, and both an HTML entity (`DXF &amp; IFC (WP-5.1)`) and prose
   with a semicolon in it ("cannot wait for a proof; every other edit ... (OQ 54)") hold one. */
export function historyRows(source) {
  return stripComments(source).split('\n').filter((l) => HISTORY.test(l)).map(squash);
}

function sourceFiles(dir = SRC, out = []) {
  for (const f of readdirSync(dir).sort()) {
    const p = join(dir, f);
    if (statSync(p).isDirectory()) sourceFiles(p, out);
    else if (/\.(jsx|js)$/.test(f)) out.push(p);
  }
  return out;
}

function current() {
  const rows = [];
  for (const p of sourceFiles()) {
    for (const r of historyRows(readFileSync(p, 'utf8'))) rows.push([p.slice(SRC.length), r]);
  }
  return rows;
}

// BASELINE-BEGIN
const BASELINE = [];
// BASELINE-END

function minus(a, b) {
  const left = new Map();
  for (const r of b) left.set(JSON.stringify(r), (left.get(JSON.stringify(r)) || 0) + 1);
  const out = [];
  for (const r of a) {
    const k = JSON.stringify(r);
    if (left.get(k)) left.set(k, left.get(k) - 1);
    else out.push(r);
  }
  return out;
}

if (process.env.READER_COPY_PRINT) console.log(JSON.stringify(current(), null, 2));

test('the scanner finds the build history in every form copy takes, and not in a comment', () => {
  const fixture = [
    '<a title="WP-2.3: prove the placement" />',
    "const t = 'forthcoming — WP-5.3 is not built';",
    '<p>compose candidates from a brief (⑤ → ⑥)</p>',
    '<span>{x} rather than silently (OQ 54). A plan</span>',
    '<h3>DXF &amp; IFC (WP-5.1)</h3>',
    '<p>a gesture cannot wait for a proof; the rest (OQ 54) can</p>',
    '/* WP-9.1: a comment is the project talking to itself */',
    '// OQ 52 in a line comment',
    'const n = 1; // WP-6.4 trailing a line of code',
    '{/* ⑦ in a JSX comment */}',
    "const tag = 'wp-guide';",                                  // lower case, not a package
    "const q = 'OQ';",                                          // no number
  ].join('\n');
  assert.deepEqual(historyRows(fixture), [
    '<a title="WP-2.3: prove the placement" />',
    "const t = 'forthcoming — WP-5.3 is not built';",
    '<p>compose candidates from a brief (⑤ → ⑥)</p>',
    '<span>{x} rather than silently (OQ 54). A plan</span>',
    '<h3>DXF &amp; IFC (WP-5.1)</h3>',
    '<p>a gesture cannot wait for a proof; the rest (OQ 54) can</p>',
  ]);
});

test('a comment\'s characters inside a string do not hide the lines after it (WP-14.33\'s audit)', () => {
  // The shipped shape: an attribute holding a slash-star opened a "comment" the regex strip ran to
  // the next star-slash, and every line between was unread -- a work package there passed.
  const fixture = [
    '<input accept="image/' + '*" />',
    '<p>forthcoming — WP-5.3 is not built</p>',
    '{/' + '* a real comment naming OQ 12 *' + '/}',
  ].join('\n');
  assert.deepEqual(historyRows(fixture), ['<p>forthcoming — WP-5.3 is not built</p>']);
});

test('the premise: the scan reads the app’s sources, and the circled numerals it refuses are real', () => {
  const files = sourceFiles();
  assert.ok(files.length > 50, 'the walk found the sources');
  assert.ok(HISTORY.test('⑤') && HISTORY.test('⑪') && HISTORY.test('⓫') && HISTORY.test('❼'),
    'the three circled-number blocks are all covered');
  assert.ok(!HISTORY.test('WPA-2') && !HISTORY.test('OQ') && !HISTORY.test('HOQ 5'),
    'and a word that merely contains the letters is not a numeral');
});

test('no new work package, open-question number or circled numeral in reader copy', () => {
  const added = minus(current(), BASELINE);
  assert.deepEqual(added, [],
    'the page carries no build history: name the thing by what it is (a glossary record if it '
    + 'needs a definition), and leave the package that built it to the commit and the report');
});

test('the baseline only shrinks: a row that is gone must leave the baseline in the same commit', () => {
  const gone = minus(BASELINE, current());
  assert.deepEqual(gone, [],
    'these baseline rows no longer exist; delete them from BASELINE so the list cannot be refilled');
});

test('every kind the palette groups by is headed by a glossary record that exists', () => {
  assert.ok(existsSync(GLOSSARY), 'the premise: the glossary directory is where this file looks');
  assert.deepEqual(Object.keys(KIND_TERM).sort(), [...KIND_ORDER].sort(),
    'KIND_TERM names a record for exactly the kinds KIND_ORDER orders');
  for (const [kind, id] of Object.entries(KIND_TERM)) {
    assert.ok(existsSync(join(GLOSSARY, `${id}.json`)), `the ${kind} heading names ${id}, which has no record`);
  }
  assert.equal(new Set(Object.values(KIND_TERM)).size, Object.keys(KIND_TERM).length,
    'no two kinds share a heading: a group headed like another is not told apart from it');
});

test('the search invitation’s label is the search record’s own term', () => {
  const rec = JSON.parse(readFileSync(join(GLOSSARY, 'search-the-corpus.json'), 'utf8'));
  for (const f of ['Chrome.jsx', 'surfaces/Overview.jsx']) {
    const live = stripComments(readFileSync(join(SRC, f), 'utf8'));
    assert.ok(live.includes(rec.term), `${f} writes the invitation as the record states it ("${rec.term}")`);
  }
});
