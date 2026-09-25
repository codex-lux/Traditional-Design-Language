/* THE APP WRITES FEWER EXPLANATIONS AND FEWER COUNTS, NEVER MORE (WP-14.8, PRD §J.4).

   Ruled 24 Sep 2026: every definition the workbench shows is a glossary record, and figures come
   from the API or the payload in hand. Two kinds of app-written copy break that and both already
   exist in the tree, so neither can simply be forbidden — they are RATCHETED, BY IDENTITY:

     EXPLANATIONS  a `title=` whose string literals carry EIGHT or more words. A tooltip that
                   long is explaining something, and an explanation belongs in a glossary record
                   a checker reads rather than in a JSX attribute nothing does. Eight is where
                   the shipped tree's labels end and its explanations begin, measured: the
                   longest title naming an act ("Give the atlas the whole window") is seven
                   words, and the shortest explanation is eight.
     COUNTS        a number, or a number word up to twenty, followed by a plural noun, in a
                   `.jsx` file's live source — `9 sections`, `209 faults`, `five authorities`
                   (the PRD's own list). A count typed into the page is true on the day it is
                   typed and silently false after, which is how the Kit's header said 95 slots
                   against an ontology holding 97.

   BY IDENTITY, NOT BY COUNT, so one change cannot net out another: removing an old explanation
   and adding a new one in the same commit leaves a total unchanged and is still a new
   explanation. Every current row must be in the baseline (a new one fails, naming itself), and
   every baseline row must still exist (a removed one fails too, asking for the baseline line to
   be deleted) — so the baseline can only shrink, and it shrinks in the commit that earns it.
   A row is (file, the literal text), so a moved line is not a new row and an edited one is.

   `COPY_RATCHET_PRINT=1 node --test src/copy_ratchet.test.mjs` prints the current rows as the
   baseline's JSON, for the commit that removes one. Adding a row to the baseline to make a new
   explanation pass is the move this file exists to refuse; the glossary is where it goes.

   THE BASELINE IS EMPTY (WP-14.31), SO THE RATCHET IS A BAN NOW. Its last fourteen titles became
   glossary records read through `describeTerm`/`useTermDescription`, and its six counts were
   either read from the payload in hand ("100 points" is the score's own two halves, "eight axes"
   the result's `score_model`) or went with the sentence that carried them.
   AND THE SCANNERS WERE WIDENED FIRST, BECAUSE AN EMPTY LIST FROM A BLIND READER IS NOT EMPTY.
   Measured on the tree before this package, the old readers missed a tooltip written as a
   `title:` property (the compiled components pass props as an object -- FindingRow's two), a
   count with an irregular plural ("filter 164 taxa"), one with adjectives between the number and
   its noun ("all 262 recorded pack conflicts", "660 style constraints"), and one written as a
   share ("86 of them", "295 of 660"). Each form is a fixture below, and a word that merely ends
   in s ("1 is", "100 and higher is") is not a plural. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const SRC = fileURLToPath(new URL('./', import.meta.url));
const TITLE_WORDS = 8;

/* Comments are not copy. Block comments, and line comments whether they start a line or trail
   code; a `//` after `:` is a URL inside a string and is kept. Line-based on purpose: a
   tokenizer that tracked quotes would be thrown by every apostrophe in JSX text. */
const stripComments = (s) => s.replace(/\/\*[\s\S]*?\*\//g, (m) => m.replace(/[^\n]/g, ' '))
  .replace(/(^|[\s;,{}()])\/\/[^\n]*/g, '$1');

/* The `{ ... }` expression starting at `i`, braces balanced and strings skipped. */
function balanced(src, i) {
  let depth = 0;
  for (let j = i; j < src.length; j += 1) {
    const c = src[j];
    if (c === "'" || c === '"' || c === '`') {
      let k = j + 1;
      while (k < src.length && src[k] !== c) { if (src[k] === '\\') k += 1; k += 1; }
      j = k;
      continue;
    }
    if (c === '{') depth += 1;
    else if (c === '}') { depth -= 1; if (depth === 0) return src.slice(i, j + 1); }
  }
  return src.slice(i);
}

function literals(expr) {
  const out = [];
  for (const m of expr.matchAll(/'((?:\\.|[^'\\\n])*)'|"((?:\\.|[^"\\\n])*)"|`((?:\\.|[^`\\])*)`/g)) {
    out.push(m[1] ?? m[2] ?? (m[3] || '').replace(/\$\{[^}]*\}/g, ' '));
  }
  return out;
}

const letterWords = (s) => s.split(/\s+/).filter((w) => /[A-Za-z]/.test(w)).length;
const squash = (s) => s.replace(/\s+/g, ' ').trim();

/* The value of an object property starting at `i`: up to the first comma, `}` or `)` at its own
   depth, strings skipped -- `title: on ? 'a' : 'b',` is the whole conditional. */
function valueEnd(src, i) {
  let depth = 0;
  for (let j = i; j < src.length; j += 1) {
    const c = src[j];
    if (c === "'" || c === '"' || c === '`') {
      let k = j + 1;
      while (k < src.length && src[k] !== c) { if (src[k] === '\\') k += 1; k += 1; }
      j = k;
      continue;
    }
    if (c === '(' || c === '[' || c === '{') depth += 1;
    else if (c === ')' || c === ']' || c === '}') { if (depth === 0) return src.slice(i, j); depth -= 1; }
    else if (c === ',' && depth === 0) return src.slice(i, j);
  }
  return src.slice(i);
}

/* source → the title rows: [text] for every tooltip whose literals total `min` words or more --
   a JSX `title=` attribute, or a `title:` property (a compiled component passes its props as an
   object, which is how FindingRow's two explanations were invisible to this reader). */
function titleRows(source, min = TITLE_WORDS) {
  const src = stripComments(source);
  const rows = [];
  for (const m of src.matchAll(/\btitle(=|:\s*)/g)) {
    const at = m.index + m[0].length;
    let lits = [];
    if (m[1] === '=') {
      if (src[at] === '"' || src[at] === "'") lits = [src.slice(at + 1, src.indexOf(src[at], at + 1))];
      else if (src[at] === '{') lits = literals(balanced(src, at));
    } else {
      lits = literals(valueEnd(src, at));
    }
    if (lits.reduce((n, l) => n + letterWords(l), 0) >= min) rows.push(squash(lits.join(' | ')));
  }
  return rows;
}

const NUMBER_WORDS = 'two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen'
  + '|fifteen|sixteen|seventeen|eighteen|nineteen|twenty';
const N = String.raw`(?<![\w.$#\-/])(?:\d+|${NUMBER_WORDS})`;
/* A word ending in s that is not a plural: a count is never followed by one of these. */
const NOT_PLURAL = String.raw`(?!(?:is|was|has|this|its|as|us|thus|yes|his|less|always|plus|across|perhaps|whereas|unless|does|goes)\b)`;
/* The words that join a phrase and never qualify a noun, so "100 and higher is" is not a count. */
const JOIN = String.raw`(?!(?:and|or|of|the|a|an|to|in|on|at|by|for|is|are|was|be|than|then|if|as|so|but|with|from|that|this|it)\b)`;
const PLURAL = String.raw`${NOT_PLURAL}[a-z][a-z-]*s\b`;
const COUNT_FORMS = [
  new RegExp(String.raw`${N}\s+${PLURAL}`, 'gi'),                               // 9 sections
  new RegExp(String.raw`${N}\s+(?:taxa|criteria|data|people|feet|inches|men|women|children)\b`, 'gi'),
  new RegExp(String.raw`${N}(?:\s+${JOIN}[a-z][a-z-]*){1,2}\s+${PLURAL}`, 'gi'), // 262 recorded pack conflicts
  new RegExp(String.raw`${N}\s+of\s+(?:\d+|them|these|those|${NUMBER_WORDS})\b`, 'gi'), // 86 of them
];

/* source → the count rows: [phrase] for every count in the live source, in source order, one row
   per place (the first form to match a place names it). */
function countRows(source) {
  const src = stripComments(source);
  const at = new Map();
  for (const re of COUNT_FORMS) {
    for (const m of src.matchAll(re)) if (!at.has(m.index)) at.set(m.index, squash(m[0]));
  }
  return [...at.entries()].sort((a, b) => a[0] - b[0]).map(([, t]) => t);
}

function jsxFiles(dir = SRC, out = []) {
  for (const f of readdirSync(dir).sort()) {
    const p = join(dir, f);
    if (statSync(p).isDirectory()) jsxFiles(p, out);
    else if (f.endsWith('.jsx')) out.push(p);
  }
  return out;
}

function current(minTitle = TITLE_WORDS) {
  const titles = [];
  const counts = [];
  for (const p of jsxFiles()) {
    const rel = p.slice(SRC.length);
    const src = readFileSync(p, 'utf8');
    for (const t of titleRows(src, minTitle)) titles.push([rel, t]);
    for (const c of countRows(src)) counts.push([rel, c]);
  }
  return { titles, counts };
}

/* The baseline, measured on this tree at WP-14.8. It may only lose rows. WP-14.13 took out six:
   the masthead's unjudged tooltip (the count is a `Term` now), the rail's "9 sections" and
   "4 formats" (its figures are the API's), and the three stale "209 faults" against a corpus
   of 210 (read from the API). WP-14.17 took out one more: the Fault Card's "three tiers" went with
   the heading that carried it, every label on the card being a glossary record now. WP-14.25 took
   out Brief Intake's "132 styles": the advisory that carried it said three styles had no native
   parti, and since WP-14.19 lists lineage partis all three have plan types, so the sentence, its
   typed count and its three hand-named styles went together. WP-14.31 took out the last fourteen
   titles and six counts, and the eight rows the widened scanners found on the way (two `title:`
   properties and six counts, every one of them removed rather than baselined). */
// BASELINE-BEGIN
const BASELINE = {
  titles: [],
  counts: [],
};
// BASELINE-END

/* a − b as multisets of rows, so two identical rows in one file are two rows. */
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

if (process.env.COPY_RATCHET_PRINT) {
  console.log(JSON.stringify(current(), null, 2));
}

test('the scanner finds an explanation in every form a title is written, and not in a label or a comment', () => {
  const twelve = 'this tooltip explains in twelve words what the glossary should be saying instead';
  const fixture = [
    `<a title="${twelve}" />`,
    `<a title='${twelve}' />`,
    `<a title={'${twelve}'} />`,
    `<a title={on ? '${twelve}' : 'short'} />`,
    `<a title={\`${twelve} \${n}\`} />`,
    '<a title="Give the atlas the whole window" />',           // seven words: a label
    `/* <a title="${twelve}" /> */`,
    `// <a title="${twelve}" />`,
    '<a title={someVariable} />',
  ].join('\n');
  const rows = titleRows(fixture);
  assert.equal(rows.length, 5, `found ${JSON.stringify(rows)}`);
  assert.ok(rows.every((r) => r.startsWith('this tooltip explains')));
});

test('the scanner finds a tooltip written as a title: property, which is how a compiled component writes one', () => {
  const twelve = 'this tooltip explains in twelve words what the glossary should be saying instead';
  const fixture = [
    `React.createElement("span", { "data-tag": "", title: "${twelve}", style: { font: 'x' } })`,
    `h("a", { title: on ? '${twelve}' : 'short', href: x })`,
    "h('b', { title: describeTerm(glossary, 'finding-class').title })",   // a record's: nothing to find
    "const card = { title: 'The plan record' };",                        // a label
  ].join('\n');
  const rows = titleRows(fixture);
  assert.equal(rows.length, 2, `found ${JSON.stringify(rows)}`);
  assert.ok(rows.every((r) => r.startsWith('this tooltip explains')));
});

test('the scanner finds a count written as a digit or a word, and not a size, a time or a comment', () => {
  const fixture = [
    '<p>the 9 sections of a dossier</p>',
    "const meta = '4 formats';",
    '<span>five authorities · at</span>',
    "style={{ width: 12, padding: '2px 7px' }}",               // sizes are not counts
    "<p>{n} faults</p>",                                        // a count from data: the point
    '// 36 styles in a comment',
    '<p>1.5 metres</p>',                                        // a decimal is a measurement
  ].join('\n');
  assert.deepEqual(countRows(fixture), ['9 sections', '4 formats', 'five authorities']);
});

test('the scanner finds the counts the first reader missed, and not a word that merely ends in s', () => {
  const fixture = [
    '<input placeholder="filter 164 taxa" />',                               // an irregular plural
    "'with all 262 recorded pack conflicts'",                                // adjectives between
    '<p>corpus-wide, 295 of 660 style constraints carry no test</p>',        // a share
    '<span>(86 of them priced in dollars)</span>',
    '<p>column numbered 1 is the most native</p>',                           // "is" is not a plural
    '<p>Score is out of 100 and higher is better</p>',                       // nor is a joined phrase
    '<p>{n} of {m} findings shown</p>',                                      // counts from data
  ].join('\n');
  assert.deepEqual(countRows(fixture),
    ['164 taxa', '262 recorded pack conflicts', '295 of 660', '660 style constraints', '86 of them']);
});

/* THE BASELINE IS EMPTY, SO THIS IS WHAT STOPS AN EMPTY RESULT FROM BEING A BLIND ONE. A scanner
   that read no file, or no title, or no count-shaped text, would report the same empty lists as
   a clean tree. So: the walk reads the components; the title reader, asked for shorter titles,
   finds the labels the tree does carry (they are what an explanation would be written beside);
   and the tree carries counts written from DATA -- `{n} findings` -- which the count reader
   deliberately passes, so it is reading JSX text and choosing. */
test('the premise: the scan reads the app’s components, its titles and its count-shaped text', () => {
  const files = jsxFiles();
  assert.ok(files.length > 20, 'the walk found the components');
  assert.ok(current(3).titles.length > 10, 'the title reader sees the short titles the tree carries');
  const fromData = files.map((p) => stripComments(readFileSync(p, 'utf8')))
    .reduce((n, s) => n + [...s.matchAll(/\}\s+[a-z][a-z-]*s\b/g)].length, 0);
  assert.ok(fromData > 10, 'the tree writes counts from data, which the count reader passes by design');
});

test('no new app-written explanation in a title=', () => {
  const added = minus(current().titles, BASELINE.titles);
  assert.deepEqual(added, [],
    'a title= of eight or more words is an explanation: write it as a glossary record and show it '
    + 'with <Term> or useTermDescription, not as a tooltip nothing checks');
});

test('no new count literal in JSX', () => {
  const added = minus(current().counts, BASELINE.counts);
  assert.deepEqual(added, [],
    'a count typed into a page goes stale silently: take it from the API or the payload in hand');
});

test('the baseline only shrinks: a row that is gone must leave the baseline in the same commit', () => {
  const now = current();
  const gone = [...minus(BASELINE.titles, now.titles), ...minus(BASELINE.counts, now.counts)];
  assert.deepEqual(gone, [],
    'these baseline rows no longer exist in the tree; delete them from BASELINE so the ratchet '
    + 'cannot be refilled by a new row of the same text');
});
