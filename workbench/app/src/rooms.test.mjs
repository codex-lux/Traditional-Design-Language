/* THE TWO ROOMS, AND READER FIRST (ruled 26 Nov 2026). What this file holds:

     1. the styles outline set as chapters returns every row once, in order
     2. the thesis is the record's one sentence, in two sizes, with nothing dropped
     3. the page head is folded into the top bar and is never open unasked
     4. a machine id is folded until wanted: the rule that hides it, the rule that shows it, and
        the store the shell marks the page from
     5. the drafting room is not in the entry chunk
     6. a page plays its entrance once, and no motion ignores a reader who asked for none

   `grounds.test.mjs` §5 holds which surface is in which room, and reads `theme/rooms.css` with the
   readers it reads `theme/tokens.css` with. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chaptersOf, rowsOf } from './styles/chapters.js';
import { thesisParts } from './frontdoor/frontDoor.js';
import { ROOM_OF } from './grounds.js';
import { stripComments } from './sourceReader.mjs';

const SRC = fileURLToPath(new URL('./', import.meta.url));
const read = (f) => readFileSync(join(SRC, f), 'utf8');
const code = (f) => stripComments(read(f));
const ROOMS_CSS = read('theme/rooms.css').replace(/\/\*[\s\S]*?\*\//g, '');

/* ── 1. the outline as chapters ─────────────────────────────────────────────────────────── */
const row = (id, depth) => ({ id, depth });
test('every row of the outline comes back exactly once, in the order it was given', () => {
  const rows = [row('t1', 0), row('f1', 1), row('s1', 2), row('v1', 3), row('s2', 2), row('f2', 1),
    row('t2', 0), row('s3', 1), row('t3', 0)];
  const ch = chaptersOf(rows);
  assert.deepEqual(rowsOf(ch).map((r) => r.id), rows.map((r) => r.id));
  assert.deepEqual(ch.map((c) => c.head.id), ['t1', 't2', 't3'], 'a tradition heads a chapter');
  assert.deepEqual(ch[0].blocks.map((b) => b.head.id), ['f1', 'f2'], 'what is filed under it heads a block');
  assert.deepEqual(ch[0].blocks[0].rows.map((r) => r.id), ['s1', 'v1', 's2'], 'and the deeper rows are read in it');
  assert.deepEqual(ch[2].blocks, [], 'a tradition with nothing filed under it is still a chapter');
});
test('a filtered outline that begins below a tradition, or skips a level, drops nothing', () => {
  // no tradition above: a chapter with no head; a depth-2 row with no block above: a block of its own
  const rows = [row('s9', 2), row('v9', 3), row('t1', 0), row('v1', 3), row('f1', 1)];
  const ch = chaptersOf(rows);
  assert.deepEqual(rowsOf(ch).map((r) => r.id), rows.map((r) => r.id));
  assert.equal(ch[0].head, null);
  assert.equal(ch[0].blocks[0].head.id, 's9');
  assert.equal(ch[1].blocks[0].head.id, 'v1', 'a row deeper than a block, with no block above it, heads one');
  assert.deepEqual(chaptersOf(null), []);
  assert.deepEqual(chaptersOf([]), []);
});
test('the Styles index draws the chapters this module makes, and builds none of its own', () => {
  const s = code('surfaces/StylesIndex.jsx');
  assert.match(s, /const chapters = chaptersOf\(rows\);/);
  assert.doesNotMatch(s, /chapters\.push\(/, 'a second spelling of where a chapter begins');
  // each of the three places a row can stand is drawn as a tree item with the row's own level
  assert.equal((s.match(/role="treeitem"/g) || []).length, 2, 'the chapter head, and the one Row both others use');
  assert.match(s, /aria-level=\{r\.depth \+ 1\}/);
});

/* ── 2. the thesis ──────────────────────────────────────────────────────────────────────── */
test('the thesis is the one sentence in two sizes: nothing dropped, nothing reordered', () => {
  const d = 'A pattern book for traditional houses, written so that a machine can read it and a person can still argue with it.';
  const t = thesisParts(d);
  assert.equal(t.head, 'A pattern book for traditional houses,');
  assert.equal(`${t.head} ${t.rest}`, d, 'the two parts, in order, are the sentence');
  // the corpus's own record, read from the file the server serves it from
  const about = JSON.parse(readFileSync(join(SRC, '..', '..', '..', 'glossary', 'about-tdl.json'), 'utf8'));
  const real = thesisParts(about.definition);
  assert.equal([real.head, real.rest].filter(Boolean).join(' '), about.definition);
  assert.ok(real.rest.length > 0, 'the premise: the record\'s sentence has a clause to set as the lede');
});
test('a sentence with no clause to break at is all headline, and never an empty one', () => {
  assert.deepEqual(thesisParts('A pattern book for houses.'), { head: 'A pattern book for houses.', rest: '' });
  assert.deepEqual(thesisParts('Yes, it is a pattern book for traditional houses.').rest, '', 'a comma too near the start is not a break');
  assert.deepEqual(thesisParts('A pattern book for traditional houses, yes.').rest, '', 'nor one too near the end');
  assert.deepEqual(thesisParts(null), { head: '', rest: '' });
});

/* ── 3. the page head ───────────────────────────────────────────────────────────────────── */
test('the page head is mounted in the top bar, and is not a band above the page', () => {
  const app = code('App.jsx');
  assert.match(app, /<TopBar[^>]*help=\{<PageHead termId=\{headTermFor\(place\)\} \/>\}/s);
  assert.equal((app.match(/<PageHead\b/g) || []).length, 1, 'mounted once');
  assert.doesNotMatch(app, /\{!full && <PageHead/, 'the band above <main> is gone');
});
test('the page head is never open unasked: its state is its own, and starts folded', () => {
  const s = code('components/PageHead.jsx');
  assert.match(s, /const \[open, setOpen\] = React\.useState\(false\);/);
  assert.doesNotMatch(s, /prefs|disclosureOpen|isSeen|markSeen/, 'no stored state opens it: not a first visit, not a remembered fold');
  assert.doesNotMatch(s, /location|nav\.get|selection/, 'and no address does');
  assert.match(s, /React\.useEffect\(\(\) => \{ setOpen\(false\); \}, \[termId\]\);/, 'leaving the page folds it');
  assert.match(s, /hidden=\{!open\}/, 'folded, its words stay in the document for a reader of the page\'s text');
});

/* ── 4. machine ids ─────────────────────────────────────────────────────────────────────── */
test('a record\'s id is hidden by default and shown when pointed at, in its own head, or on demand', () => {
  assert.match(ROOMS_CSS, /\.tdl-record-note\{display:none\}/);
  const show = /([^{}]*)\{display:inline\}/.exec(ROOMS_CSS);
  assert.ok(show, 'a rule shows it again');
  for (const sel of ['.tdl-record-link:hover>.tdl-record-note', '.tdl-record-link:focus-visible>.tdl-record-note',
    '[data-id-shown] .tdl-record-note', '#root[data-ids] .tdl-record-note']) {
    assert.ok(show[1].includes(sel), `${sel} shows the note`);
  }
});
test('the shell marks the page from the store the control writes, and the URL carries none of it', () => {
  const app = code('App.jsx');
  const chrome = code('Chrome.jsx');
  assert.match(chrome, /export const IDS_PREF = 'machine-ids';/);
  assert.match(chrome, /prefs\.setFold\(IDS_PREF, !on\)/, 'the control writes the store');
  assert.match(chrome, /aria-pressed=\{on\}/, 'and says which way it stands');
  assert.match(app, /const showIds = memory\.folds\[IDS_PREF\] === true;/);
  assert.match(app, /root\.toggleAttribute\('data-ids', showIds\)/);
  assert.doesNotMatch(read('router.js'), /machine-ids|data-ids/, 'a preference about this browser is not a place');
});
test('a dossier prints its own id once, in its head', () => {
  const s = code('surfaces/StyleDossier.jsx');
  assert.equal((s.match(/data-dossier-id=""/g) || []).length, 1);
  assert.match(s, /className="tdl-record-id" data-dossier-id=""/, 'in a class the fold does not hide');
  assert.doesNotMatch(ROOMS_CSS, /\.tdl-record-id\{[^}]*display:none/);
});

/* ── 5. the drafting room is loaded when it is entered ──────────────────────────────────── */
test('no house surface is imported statically by the shell', () => {
  const app = code('App.jsx');
  const table = /const SURFACES = \{([\s\S]*?)\n\};/.exec(app);
  assert.ok(table, 'App.jsx has no SURFACES table to read');
  const componentOf = {};
  for (const m of table[1].matchAll(/^\s*([a-z]+): ([A-Za-z]+),/gm)) componentOf[m[1]] = m[2];
  const house = Object.keys(ROOM_OF).filter((s) => ROOM_OF[s] === 'house');
  assert.ok(house.length >= 5, 'the premise: the house has its steps');
  for (const surface of house) {
    const comp = componentOf[surface];
    assert.ok(comp, `${surface} has a component`);
    assert.doesNotMatch(app, new RegExp(`^import \\{[^}]*\\b${comp}\\b[^}]*\\} from`, 'm'), `${comp} is imported statically`);
    assert.match(app, new RegExp(`const ${comp} = lazyNamed\\(\\(\\) => import\\(`), `${comp} is loaded when first opened`);
  }
  // what a reader arrives in stays in the entry chunk: a lazy front door would be a blank first paint
  assert.match(app, /^import \{ Overview \} from '\.\/surfaces\/Overview\.jsx';/m);
});

/* ── 6. motion ──────────────────────────────────────────────────────────────────────────── */
function timedParts(css) {
  const out = [];
  for (const m of css.matchAll(/(?<![\w-])(?:animation|transition):([^;}]*)/g)) {
    // split on the commas between parts, not the ones inside cubic-bezier() or var()
    let depth = 0, part = '';
    for (const c of m[1]) {
      if (c === '(') depth += 1;
      if (c === ')') depth -= 1;
      if (c === ',' && depth === 0) { out.push(part.trim()); part = ''; } else part += c;
    }
    if (part.trim()) out.push(part.trim());
  }
  return out;
}
function literalDurations(css) {
  return timedParts(css).filter((part) => {
    const first = /var\(--(?:dur|t)-[a-z0-9]+\)|(?<![\w.-])\d*\.?\d+m?s\b/.exec(part);
    return Boolean(first) && !first[0].startsWith('var(');
  });
}
test('a page plays its entrance once per surface, and every motion is a duration token', () => {
  const app = code('App.jsx');
  assert.match(app, /<main data-ground=\{groundOf\([^)]*\)\} key=\{surface\}\s+className="tdl-room"/,
    'the <main> is keyed by the surface, so opening a page mounts it afresh');
  assert.match(ROOMS_CSS, /main\.tdl-room\{animation:tdl-page-in var\(--dur-3\)/);
  // A literal duration ignores `prefers-reduced-motion`, which tokens.css answers by zeroing the
  // duration tokens. In each comma-separated part of an `animation` or `transition`, the FIRST time
  // is the duration and must be a token; a second time is the delay, and a delay on a zero-length
  // animation moves nothing.
  assert.deepEqual(literalDurations(ROOMS_CSS), [], 'a duration written as a number');
  assert.ok(timedParts(ROOMS_CSS).length > 10, 'the premise: the file does move things');
  assert.deepEqual(literalDurations('.x{animation:a 300ms ease both}'), ['a 300ms ease both']);
  assert.deepEqual(literalDurations('.x{transition:color .2s,transform var(--dur-2) ease}'), ['color .2s']);
  assert.deepEqual(literalDurations('.x{animation:a var(--dur-4) var(--ease-ink) 70ms both;transition:var(--t-hover)}'), [],
    'a token duration with a literal delay, and a transition token, are not literal durations');
  // the page-in keyframes move nothing sideways and transform nothing: a transform on <main> would
  // re-base every fixed popover inside it and repaint a plate's text (WP-14.15)
  assert.match(ROOMS_CSS, /@keyframes tdl-page-in\{from\{opacity:0\}to\{opacity:1\}\}/);
});

/* ── 7. the period bar is handed a period ───────────────────────────────────────────────── */
test('the dossier hands its period bar the period the dossier route serves', () => {
  /* WP-17.9's bar read `rec.period`, and `GET /api/styles/{id}` has never served a `period`, so
     it drew for no style from the day it was written. Nothing read the rendered page for it: the
     bar's arithmetic was tested (`periodBar.test.mjs`) and its input was not. The server suite
     holds the route to the record (`test_the_dossier_serves_the_records_own_period`), the walk
     counts the bar on the page, and this holds the join between them. */
  const dossier = code('surfaces/StyleDossier.jsx');
  const identify = code('dossier/Identify.jsx');
  assert.match(dossier, /<Identify rec=\{rec\} period=\{dossier\.period\}/);
  assert.match(identify, /export function Identify\(\{ rec, period, styleId, cards \}\)/);
  assert.match(identify, /<PeriodBar period=\{period\} \/>/);
  assert.doesNotMatch(identify, /rec\.period/, 'the key the style route does not serve');
  // and its one heavy segment is drawn in an ink that is an ink on a page
  const bar = code('dossier/PeriodBar.jsx');
  assert.match(bar, /floruit: 'var\(--text-body\)'/);
  assert.doesNotMatch(bar, /fill: [^}]*var\(--paper\)/, 'paper is no ink on paper');
});
