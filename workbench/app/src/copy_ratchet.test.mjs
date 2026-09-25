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
   explanation pass is the move this file exists to refuse; the glossary is where it goes. */
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

/* source → the title rows: [text] for every title= whose literals total TITLE_WORDS or more. */
function titleRows(source) {
  const src = stripComments(source);
  const rows = [];
  for (const m of src.matchAll(/\btitle=/g)) {
    const at = m.index + m[0].length;
    let lits = [];
    if (src[at] === '"' || src[at] === "'") lits = [src.slice(at + 1, src.indexOf(src[at], at + 1))];
    else if (src[at] === '{') lits = literals(balanced(src, at));
    if (lits.reduce((n, l) => n + letterWords(l), 0) >= TITLE_WORDS) rows.push(squash(lits.join(' | ')));
  }
  return rows;
}

const NUMBER_WORDS = 'two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen'
  + '|fifteen|sixteen|seventeen|eighteen|nineteen|twenty';
const COUNT = new RegExp(String.raw`(?<![\w.$#\-/])(\d+|${NUMBER_WORDS})\s+([a-z][a-z-]*s)\b`, 'gi');

/* source → the count rows: [phrase] for every number-then-plural in the live source. */
function countRows(source) {
  return [...stripComments(source).matchAll(COUNT)].map((m) => squash(m[0]));
}

function jsxFiles(dir = SRC, out = []) {
  for (const f of readdirSync(dir).sort()) {
    const p = join(dir, f);
    if (statSync(p).isDirectory()) jsxFiles(p, out);
    else if (f.endsWith('.jsx')) out.push(p);
  }
  return out;
}

function current() {
  const titles = [];
  const counts = [];
  for (const p of jsxFiles()) {
    const rel = p.slice(SRC.length);
    const src = readFileSync(p, 'utf8');
    for (const t of titleRows(src)) titles.push([rel, t]);
    for (const c of countRows(src)) counts.push([rel, c]);
  }
  return { titles, counts };
}

/* The baseline, measured on this tree at WP-14.8. It may only lose rows. WP-14.13 took out six:
   the masthead's unjudged tooltip (the count is a `Term` now), the rail's "9 sections" and
   "4 formats" (its figures are the API's), and the three stale "209 faults" against a corpus
   of 210 (read from the API). */
// BASELINE-BEGIN
const BASELINE = {
  titles: [
    ["Chrome.jsx", "Search styles, slots, faults, packs and rooms — ⌘K"],
    ["components/Splitter.jsx", "Drag to resize · arrows nudge, shift-arrows stride, | Home or double-click for its shipped width"],
    ["round/RoundPlate.jsx", "lay the drawn plate over the model at this view"],
    ["round/RoundPlate.jsx", "is read off a plan and is not drawn in a free view | show"],
    ["round/RoundPlate.jsx", "a section plane through the model, derived from the model and not from a plate"],
    ["surfaces/Phylogeny.jsx", "Where each style arose, and where its lineage travelled"],
    ["surfaces/PlanWorkbench.jsx", "the completeness layer: treat absent room types as failures (--strict)"],
    ["surfaces/PlanWorkbench.jsx", "WP-2.3: prove the placement with CP-SAT — hard constraints on the record's declared facts, a named conflict set if they cannot all hold. Takes seconds; per-drag re-scores stay on the fast search."],
    ["surfaces/PlanWorkbench.jsx", "WP-9.1: the analyst — place once, check, and sort every finding into what it means to a generator: a move answers it, the engine's, the critic's own invention, or the architect's. One heavy call; not run per edit."],
    ["surfaces/PlanWorkbench.jsx", "WP-9.2: the corrective revisions on the fast search — up to 6 rounds, 60 s. Accepts a round only on a strict improvement, rolls back otherwise, and loads the result as one undo step. Refusals on the search are usually the engine's noise; read the panel's engine line."],
    ["surfaces/PlanWorkbench.jsx", "WP-9.2: the corrective revisions proof-backed — CP-SAT is asked for before any declared move; up to 4 rounds, 120 s. Minutes, not seconds; the panel shows each round as it lands."],
    ["surfaces/PlanWorkbench.jsx", "see this record as a model, in the Drawing Set"],
    ["surfaces/PlanWorkbench.jsx", "CP-SAT proved this placement; re-solving takes seconds and should return the same one | this placement came from the hill-climb; results differ across runs | — and runs corrective rounds on what the critic finds before drawing (WP-13.9)"],
    ["surfaces/phylo/MapView.jsx", "Give the instrument back — or press escape | Give the atlas the whole window — escape brings the instrument back"],
  ],
  counts: [
    ["components/CandidateColumn.jsx", "100 points"],
    ["components/ConflictSet.jsx", "six reads"],
    ["components/FaultCard.jsx", "three tiers"],
    ["surfaces/BriefIntake.jsx", "132 styles"],
    ["surfaces/CandidateSet.jsx", "eight axes"],
    ["surfaces/KitSurface.jsx", "two namespaces"],
    ["surfaces/PlanWorkbench.jsx", "6 rounds"],
    ["surfaces/PlanWorkbench.jsx", "4 rounds"],
    ["surfaces/Proportions.jsx", "five authorities"],
    ["surfaces/Proportions.jsx", "three inches"],
    ["surfaces/StyleRecord.jsx", "660 constraints"],
  ],
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

test('the premise: the scan reads the app’s components and finds the copy they already carry', () => {
  const files = jsxFiles();
  assert.ok(files.length > 20, 'the walk found the components');
  const { titles, counts } = current();
  assert.ok(BASELINE.titles.length > 0 && BASELINE.counts.length > 0,
    'the baseline records the tree’s existing rows; an empty one would make the ratchet a ban');
  assert.ok(titles.length > 0 && counts.length > 0, 'a scanner that finds nothing passes every tree');
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
