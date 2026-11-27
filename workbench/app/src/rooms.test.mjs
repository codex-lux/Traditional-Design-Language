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

/* ── 7. THE REST OF THE ROOMS (WP-18.1 to 18.4, 27 Nov 2026) ─────────────────────────────── */
import { kitSections } from './dossier/kitSections.js';
import { contrast } from './grounds.js';

const TOKENS_CSS = read('theme/tokens.css');
const hexOf = (name) => {
  const m = new RegExp(`${name}:(#[0-9A-Fa-f]{6})`).exec(TOKENS_CSS);
  return m ? m[1].toUpperCase() : null;
};

test('a kit\'s rows stand under their groups: every row once, the ontology\'s order, a stray group kept', () => {
  const groups = [{ id: 'roof', name: 'Massing & Roof' }, { id: 'wall', name: 'Envelope & Wall' }, { id: 'empty', name: 'Nothing' }];
  const rows = [{ id: 'a', group: 'wall' }, { id: 'b', group: 'roof' }, { id: 'c', group: 'nobody-named-this' }, { id: 'd', group: 'wall' }];
  const secs = kitSections(groups, rows);
  assert.deepEqual(secs.map((s) => s.id), ['roof', 'wall', 'nobody-named-this'], 'the ontology\'s order, then the stray');
  assert.deepEqual(secs.map((s) => s.name), ['Massing & Roof', 'Envelope & Wall', 'nobody-named-this']);
  assert.deepEqual(secs.flatMap((s) => s.rows.map((r) => r.id)).sort(), ['a', 'b', 'c', 'd'], 'every row exactly once');
  assert.deepEqual(secs.find((s) => s.id === 'wall').rows.map((r) => r.id), ['a', 'd'], 'a group keeps its rows\' order');
  assert.ok(!secs.some((s) => s.id === 'empty'), 'a group with no row draws no heading');
  assert.deepEqual(kitSections(null, rows).flatMap((s) => s.rows).length, 4, 'no groups served: nothing is dropped');
  assert.deepEqual(kitSections(groups, null), []);
  // the join: the surface draws the leaf's sections and keeps no grouping of its own
  const kit = code('surfaces/KitSurface.jsx');
  assert.match(kit, /const sections = kitSections\(groups, rows\);/);
  assert.match(kit, /sections\.map\(\(sec\) =>/);
  assert.doesNotMatch(kit, /(?<!sec\.)rows\.map\(\(s\) => \(\s*<SlotRow/, 'the rows are drawn outside their groups again');
});

test('the kit row leads with the slot\'s name, and each id it prints is a margin note', () => {
  const row = code('components/SlotRow.jsx');
  assert.match(row, /\{slot\.name \|\| slot\.id\}<span className="tdl-record-note">\{slot\.id\}<\/span>/);
  assert.match(row, /\{slot\.sourceName \|\| src\.id\}/, 'the source is a style\'s name, and its id where no name is held');
  const kit = code('surfaces/KitSurface.jsx');
  assert.match(kit, /name: nameOf\('slot:' \+ row\.slot\)/, 'the name is the names index\'s, not typed here');
  const trace = code('components/ProvenanceTrace.jsx');
  assert.match(trace, /\{nameOf\(l\.id\)\}<span className="tdl-record-note">\{l\.id\}<\/span>/);
  assert.match(trace, /<details data-cascade-bans=\{l\.id\}/, 'a level\'s bans fold under their count');
});

/* The six paper inks are COMPUTED: each is its pigment mixed toward --coal by the least hundredth
   that reads 4.5 : 1 on all four papers. Recomputed here, so an ink typed by eye, or a paper that
   moved under one, fails. */
const mixHex = (a, b, t) => '#' + [1, 3, 5].map((i) => Math.round(parseInt(a.slice(i, i + 2), 16) * (1 - t)
  + parseInt(b.slice(i, i + 2), 16) * t).toString(16).padStart(2, '0')).join('').toUpperCase();
const PAPERS = ['--paper', '--paper-deep', '--paper-mat', '--paper-lit'];
const PAPER_INKS = { '--gilt-ink': '--gilt-deep', '--brick-ink': '--brick', '--salmon-ink': '--salmon-deep',
  '--green-ink': '--green-deep', '--ink-3-ink': '--ink-3', '--ink-2-ink': '--ink-2' };
function leastStep(pigment) {
  const coal = hexOf('--coal');
  const worst = (c) => Math.min(...PAPERS.map((p) => contrast(c, hexOf(p))));
  for (let i = 0; i <= 100; i += 1) { const c = mixHex(pigment, coal, i / 100); if (worst(c) >= 4.5) return c; }
  return null;
}

test('each paper ink is its pigment at the least step toward coal that reads on every paper', () => {
  for (const p of PAPERS) assert.ok(hexOf(p), `the premise: ${p} is a hex in tokens.css`);
  for (const [ink, pigment] of Object.entries(PAPER_INKS)) {
    assert.ok(hexOf(pigment), `the premise: ${pigment} is a hex`);
    assert.equal(hexOf(ink), leastStep(hexOf(pigment)), `${ink} is not ${pigment} at its least reading step`);
    for (const p of PAPERS) assert.ok(contrast(hexOf(ink), hexOf(p)) >= 4.5, `${ink} on ${p}`);
  }
  // the pigments did not move: a fill, a stroke and a swatch keep their colour
  assert.equal(hexOf('--gilt-deep'), '#8A6D33'); assert.equal(hexOf('--brick'), '#AF6B50');
  assert.equal(hexOf('--salmon-deep'), '#C08066'); assert.equal(hexOf('--green-deep'), '#6B7C5C');
});

test('on paper a word\'s duty is bound to a paper ink, at :root and under vellum alike', () => {
  const want = { '--text-accent': '--gilt-ink', '--sev-minor': '--gilt-ink', '--sev-fatal': '--brick-ink',
    '--refusal-text': '--brick-ink', '--sev-serious': '--salmon-ink', '--sev-cleared': '--green-ink',
    '--text-tertiary': '--ink-3-ink', '--sev-info': '--ink-3-ink', '--text-secondary': '--ink-2-ink',
    '--sev-advisory': '--ink-2-ink' };
  for (const [duty, ink] of Object.entries(want)) {
    const n = (TOKENS_CSS.match(new RegExp(`${duty}:var\\(${ink}\\);`, 'g')) || []).length;
    assert.equal(n, 2, `${duty} is bound to ${ink} ${n} time(s): once at :root and once under vellum`);
  }
  assert.match(TOKENS_CSS, /--fix-right:var\(--green-ink\); --fix-cheap:var\(--gilt-ink\); --fix-dishonest:var\(--salmon-ink\);/);
});

test('the plan page draws its sheet before the panels that disclose what the placement gave up', () => {
  const src = code('surfaces/PlanWorkbench.jsx');
  const sheet = src.indexOf('<PlateViewer label="the sheet"');
  const gaveUp = src.indexOf('{gaveUp.length > 0 && (');
  const critique = src.indexOf('data-panel="critique"');
  const revision = src.indexOf('<RevisionPanel');
  const caption = src.indexOf('<p data-engine-claim=');
  for (const [n, at] of Object.entries({ sheet, gaveUp, critique, revision, caption })) assert.ok(at > 0, `the premise: ${n} is found`);
  assert.ok(sheet < gaveUp && sheet < critique && sheet < revision, 'a disclosure panel stands above the sheet again');
  assert.ok(gaveUp < caption && critique < caption, 'the caption says "above" of the panels, so it follows them');
  assert.equal(src.split('{gaveUp.length > 0 && (').length - 1, 1, 'the panel is drawn once: moved, not copied');
});

test('an empty station of the journey says what it waits for and offers a way on', () => {
  for (const [f, name] of [['surfaces/CandidateSet.jsx', 'candidates'], ['surfaces/PlanWorkbench.jsx', 'workbench'],
    ['surfaces/DrawingSet.jsx', 'drawings'], ['surfaces/Transcription.jsx', 'transcription']]) {
    assert.match(code(f), new RegExp(`className="tdl-waiting tdl-rise" data-waiting="${name}"`), f);
  }
  assert.match(ROOMS_CSS, /\.tdl-waiting\{/);
  // the brief's one act is the page's primary act, and is still a button that composes
  const brief = code('surfaces/BriefIntake.jsx');
  assert.match(brief, /<button type="button" data-compose="" onClick=\{compose\} disabled=\{composing \|\| !ready\}\s+aria-busy=\{composing \|\| undefined\} className="tdl-act tdl-act-primary">/);
});

test('a heading the walk holds to a glossary word carries that word and nothing else', () => {
  const src = code('surfaces/Proportions.jsx');
  assert.match(src, /<span data-kind-heading=\{g\.kind\}><Term field="pack\.kind" value=\{g\.kind\} \/><\/span>/);
  assert.doesNotMatch(src, /data-kind-heading=\{g\.kind\}[^>]*>\s*<Term[^>]*\/>\s*<span className="tdl-section-count"/,
    'a count inside the heading is read as part of the word');
});

test('the small controls answer the pointer through a class, and a filter strip is one row of 40 px', () => {
  const chrome = code('Chrome.jsx');
  assert.match(chrome, /\{\.\.\.aria\} className="tdl-chip"/);
  assert.match(chrome, /disabled=\{disabled\} className="tdl-action"/);
  for (const sel of ['.tdl-chip:hover', '.tdl-action:not(:disabled):hover', '.tdl-field:hover']) {
    assert.ok(ROOMS_CSS.includes(sel + '{'), `${sel} has no rule`);
  }
  assert.match(TOKENS_CSS, /--substrip-h:40px;/, 'the walk holds a one-row strip to 40 px');
});


/* ---- §8: the drafting room's interiors (WP-18.5, 27 Nov 2026) --------------------------------- */
import { labelWidth, LABEL_MAX, LABEL_MIN } from './surfaces/phylo/labelWidth.js';

test('a candidate column says its number, then why and what it trades away, then the working', () => {
  const col = code('components/CandidateColumn.jsx');
  const at = (needle) => { const i = col.lastIndexOf(needle); assert.ok(i > 0, `missing: ${needle}`); return i; };
  const order = [at('React.createElement(StandingBand, { c: c })'), at('React.createElement(ScoreBlock, {'),
    at('"data-candidate-why": ""'), at('}, "trades away")'), at('React.createElement(ScoreWorking, {'),
    at("['fatal', 'serious', 'minor'].map("), at('"data-unjudged-fatal": c.unjudged_fatal_n'),
    at('"data-candidate-facts": ""')];
  assert.deepEqual(order, [...order].sort((a, b) => a - b), 'the column\'s order');
  // rule 1 of the column: the trade stands next to the score, with one block (the why) between
  assert.doesNotMatch(col.slice(order[1], order[3]), /ScoreWorking|"how it scores"/, 'the working is not between them');
  // the working is still drawn, and is not behind a disclosure
  const working = col.slice(col.indexOf('function ScoreWorking('), col.indexOf('function StandingBand('));
  assert.match(working, /"how it scores"/);
  assert.doesNotMatch(working, /"details"/, 'the score\'s working is never folded');
});

test('the fatal faults nobody judged keep their mark and count in view, and only their names fold', () => {
  const col = code('components/CandidateColumn.jsx');
  const a = col.indexOf('"data-unjudged-fatal": c.unjudged_fatal_n');
  const d = col.indexOf('React.createElement("details", {', a);
  const mark = col.indexOf('label: "fatal " + c.unjudged_fatal_n', a);
  assert.ok(a > 0 && mark > a && d > mark, 'the mark and its count come before the disclosure, outside it');
  assert.match(col.slice(d, d + 1400), /"data-unjudged-fatal-names": c\.unjudged_fatal\.length[\s\S]*x\.name \|\| x\.fault/);
  assert.doesNotMatch(col.slice(a, d), /x\.name \|\| x\.fault/, 'the names are inside the disclosure only');
});

test('a finding row gives its statement the width, and says its layer on a quiet line under it', () => {
  const row = code('components/FindingRow.jsx');
  const st = row.indexOf('"data-finding-statement": ""');
  const meta = row.indexOf('"data-finding-meta": ""');
  assert.ok(st > 0 && meta > st, 'the statement, then the line under it');
  const metaBlock = row.slice(meta, row.indexOf('open && /*#__PURE__*/React.createElement("div"', meta));
  for (const part of ['finding.layer', '"data-engine-tag": ""', '"data-class-tag": ""', 'finding.at']) {
    assert.ok(metaBlock.includes(part), `the line under the statement carries ${part}`);
  }
  assert.doesNotMatch(row, /width: 76/, 'the layer is not a fixed column beside the statement');
  assert.match(row, /"data-finding-severity": sev,\s*style: \{\s*font: 'var\(--type-eyebrow\)'/);
});

test('the family tree\'s name column is a share of its chart, between a floor and 260 px', () => {
  assert.equal(labelWidth(null), LABEL_MAX);
  assert.equal(labelWidth(NaN), LABEL_MAX);
  assert.equal(labelWidth(0), LABEL_MAX, 'unmeasured is the wide chart');
  assert.equal(labelWidth(336), LABEL_MIN, 'the pane the walk measured');
  assert.equal(labelWidth(500), 180);
  assert.equal(labelWidth(1100), LABEL_MAX);
  for (let w = 1; w < 1400; w += 7) {
    const l = labelWidth(w);
    assert.ok(l >= LABEL_MIN && l <= LABEL_MAX);
    assert.ok(labelWidth(w + 7) >= l, 'never narrower in a wider pane');
  }
  const src = code('surfaces/Phylogeny.jsx');
  assert.match(src, /const LABEL_W = labelWidth\(chartW\);/);
  assert.doesNotMatch(src, /const LABEL_W = \d/, 'no fixed width beside the measured one');
});

test('the export page leads with its record\'s line, and its cards are one even grid', () => {
  const src = code('surfaces/ExportDetails.jsx');
  assert.match(src, /<PageHero termId="surface-export"/);
  assert.match(src, /<div data-export-cards="" style=\{GRID\}>/);
  assert.match(src, /const GRID = \{ display: 'grid', gridTemplateColumns: 'repeat\(auto-fit, minmax\(min\(100%, 400px\), 1fr\)\)'/);
  assert.doesNotMatch(src, /maxWidth: 420/, 'a card has no width of its own');
});

test('the Drawing Set and the tracing panel set no prose in the data face', () => {
  const ds = code('surfaces/DrawingSet.jsx');
  assert.match(ds, /<span data-drawing-of=\{plan\.id\} className="tdl-record-note"/, 'the two ids are an on-demand note');
  assert.doesNotMatch(ds, /font: 'var\(--type-data-s\)'[^>]*>\s*\{plan\.id\} · \{plan\.style\}/);
  const tr = code('surfaces/Transcription.jsx');
  assert.doesNotMatch(tr, /font: 'var\(--type-data-s\)'/, 'a label, a note and a gap are read, not parsed');
  assert.doesNotMatch(tr, /const input = \{[^}]*var\(--mono/, 'a field is typed in the reading face');
});

import { groundValue } from './grounds.js';

test('the affinity ladder\'s words read 4.5 : 1 on every paper, at :root and under vellum', () => {
  /* A rendered read of twenty-eight paper pages found what the token table never read: the ladder
     duties are held on the instrument (grounds.test §10) and were held on paper by nothing. The
     affinity rungs have one reader, `VariantPill`'s map, and it sets each as a word. */
  const pill = code('components/VariantPill.jsx');
  const rungs = ['--aff-canonical', '--aff-common', '--aff-possible', '--aff-forbidden'];
  for (const n of rungs) assert.ok(pill.includes(`'var(${n})'`), `the premise: ${n} is a word's colour in the pill`);
  for (const n of [...rungs, '--aff-atypical']) {
    for (const g of [null, 'vellum']) {
      const ink = groundValue(TOKENS_CSS, g, n);
      assert.match(ink || '', /^#[0-9a-f]{6}$/i, `${n} resolves to an ink on ${g || ':root'}`);
      for (const p of PAPERS) {
        assert.ok(contrast(ink, hexOf(p)) >= 4.5, `${n} on ${g || ':root'} reads ${contrast(ink, hexOf(p)).toFixed(2)} on ${p}`);
      }
    }
  }
});
