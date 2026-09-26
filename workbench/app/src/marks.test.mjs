/* ONE MEANING PER HATCH, ONE PRODUCT KEY (WP-14.29, ruled 25 Sep 2026; PRD tranche 2 §D).

   Until this package the unjudged hatch drew five things and the 45° hatch six, and the brick of
   the UI's fatal was also the colour of a whole tradition. Four properties keep that from coming
   back, and each is held here from the files themselves rather than from a list typed into the
   test, so the day a new mark or a new hatch lands the test reads it without being edited:

     1. every STATE hatch in `theme/tokens.css` carries exactly one duty -- one `--mark-*` reads
        it -- and the named MATERIAL hatches carry none (they are drawing materials, keyed on the
        sheet that draws them);
     2. no shipped file draws a hatch by name: `var(--hatch-...)` appears nowhere outside the
        stylesheet, and inside it only in a `--mark-*` declaration;
     3. the `--mark-*` properties, the glossary records carrying `mark`, and `marks.js`'s forms
        correspond one to one, so the product key cannot show a mark with no word or a word with
        no mark;
     4. `--t3` is an existing ink of the palette, named rather than typed, and is not brick.

   No count literals: every population is derived from the stylesheet, the records or the code,
   and each is asserted non-empty first, so a parser that stopped matching cannot pass by
   reading nothing. Imports nothing outside `node:` and the pure modules under test. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, statSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { MARK_FORMS, JUDGMENT_MARKS, markGlyph, markKeyGroups } from './marks.js';
import { JUDGMENT_MARK, styleFindingMark } from './judgment.js';
import { ruleMark, ruleState } from './proportions/page.js';
import { indexTerms } from './glossary/lookup.js';

const SRC = fileURLToPath(new URL('.', import.meta.url));
const ROOT = new URL('../../../', import.meta.url);
const TOKENS = join(SRC, 'theme', 'tokens.css');

/* The four drawing materials. Each is one material with one meaning, keyed where the sheet keys
   it (PRD tranche 2 §D), and carries no on-screen duty. Named here because the PRD names them;
   every OTHER hatch the stylesheet declares is a state hatch and owes exactly one duty. */
const MATERIALS = Object.freeze(['--hatch-masonry', '--hatch-crosshatch', '--hatch-water', '--stipple-lawn']);
/* A hatch the stylesheet declares that nothing draws. It carries no duty, and property 2 keeps
   any code from starting to draw it by name. */
const UNUSED = Object.freeze(['--hatch-cross']);

const stripCss = (s) => s.replace(/\/\*[\s\S]*?\*\//g, ' ');
const stripJs = (s) => s.replace(/\/\*[\s\S]*?\*\//g, ' ').replace(/(^|[^:'"`\\])\/\/[^\n]*/g, '$1');

/* Every custom property the stylesheet declares, as [name, value] in order. A declaration is a
   name after `{`, `;` or a line start, then a colon -- the same reading `build/check_glossary.py`
   rule 13 makes -- and a `var(--x)` is a use, never a declaration. */
function declarations(css) {
  const out = [];
  for (const m of stripCss(css).matchAll(/(?:^|[{;])\s*(--[A-Za-z0-9_-]+)\s*:\s*([^;{}]*)/gm)) {
    out.push([m[1], m[2].trim()]);
  }
  return out;
}

function readTokens(css = readFileSync(TOKENS, 'utf8')) {
  const decls = declarations(css);
  assert.ok(decls.length > 0, 'the premise: tokens.css declares custom properties this reader can see');
  const byName = new Map();
  for (const [n, v] of decls) if (!byName.has(n)) byName.set(n, v);
  return { css, decls, byName };
}

const isHatch = (n) => /^--(hatch|stipple)-/.test(n);
const readsVar = (value) => [...value.matchAll(/var\(\s*(--[A-Za-z0-9_-]+)/g)].map((m) => m[1]);

/* Every glossary record, read with node:fs alone. */
function records() {
  const dir = new URL('glossary/', ROOT);
  if (!existsSync(dir)) return [];
  return readdirSync(dir).filter((f) => f.endsWith('.json')).sort()
    .map((f) => JSON.parse(readFileSync(new URL(f, dir), 'utf8')));
}

/* Every shipped source file under src/: .js and .jsx, never a test. */
function shipped(dir = SRC) {
  const out = [];
  for (const name of readdirSync(dir).sort()) {
    const full = join(dir, name);
    if (statSync(full).isDirectory()) { out.push(...shipped(full)); continue; }
    if (/\.(js|jsx)$/.test(name) && !/\.test\./.test(name)) out.push(full);
  }
  return out;
}

/* ─────────────────────────── 1. one duty per hatch ─────────────────────────── */

function dutiesOf(css) {
  const { byName } = readTokens(css);
  const hatches = [...byName.keys()].filter(isHatch);
  const marks = [...byName.keys()].filter((n) => n.startsWith('--mark-'));
  const readers = Object.fromEntries(hatches.map((h) => [h, []]));
  for (const m of marks) {
    const read = readsVar(byName.get(m)).filter(isHatch);
    assert.ok(read.length <= 1, `${m} paints with ${read.length} hatches (${read}); a mark is one form`);
    for (const h of read) (readers[h] || (readers[h] = [])).push(m);
  }
  return { hatches, marks, readers };
}

test('every state hatch carries exactly one duty, and no material or unused hatch carries any', () => {
  const { hatches, readers } = dutiesOf();
  const state = hatches.filter((h) => !MATERIALS.includes(h) && !UNUSED.includes(h));
  assert.ok(state.length > 0, 'the premise: the stylesheet declares state hatches');
  // the named materials and the unused hatch are really declared, or naming them exempts nothing
  for (const h of [...MATERIALS, ...UNUSED]) assert.ok(hatches.includes(h), `${h} is named here and not declared`);
  for (const h of state) {
    assert.equal(readers[h].length, 1,
      `${h} carries ${readers[h].length} duties (${readers[h].join(', ') || 'none'}): one meaning per hatch`);
  }
  for (const h of [...MATERIALS, ...UNUSED]) {
    assert.deepEqual(readers[h], [], `${h} is a material or unused hatch and a mark reads it: ${readers[h]}`);
  }
});

test('the one-duty reader fails a stylesheet where two marks share a hatch, or a hatch has none', () => {
  // driven, so the assertion above cannot pass by never finding a second reader
  const base = ':root{--hatch-a:linear-gradient(red,red);--hatch-b:linear-gradient(red,red);'
    + '--mark-x:var(--hatch-a);}';
  assert.deepEqual(dutiesOf(base).readers, { '--hatch-a': ['--mark-x'], '--hatch-b': [] });
  const two = base.replace('}', '--mark-y:var(--hatch-a);}');
  assert.deepEqual(dutiesOf(two).readers['--hatch-a'], ['--mark-x', '--mark-y']);
  // a mark named inside a comment is not a reader
  const commented = base.replace('}', '/* --mark-z:var(--hatch-b); */}');
  assert.deepEqual(dutiesOf(commented).readers['--hatch-b'], []);
});

/* ─────────────────────────── 2. no hatch drawn by name ─────────────────────────── */

function rawHatchUses(src) {
  return [...stripJs(src).matchAll(/var\(\s*(--(?:hatch|stipple)-[A-Za-z0-9_-]+)/g)].map((m) => m[1]);
}

test('no shipped file draws a hatch by name: a state is drawn through its duty token', () => {
  const files = shipped();
  assert.ok(files.length > 0, 'the premise: the shipped sources are on this tree');
  let dutyUses = 0;
  const offenders = [];
  for (const f of files) {
    const src = readFileSync(f, 'utf8');
    for (const h of rawHatchUses(src)) {
      if (!MATERIALS.includes(h)) offenders.push(`${f.slice(SRC.length)}: var(${h})`);
    }
    dutyUses += (stripJs(src).match(/var\(--mark-[a-z0-9-]+\)/g) || []).length;
  }
  assert.deepEqual(offenders, [], 'a raw hatch in shipped code gives a hatch a second meaning');
  // and the consumers really do draw through the duty tokens, so the zero above is a zero of
  // hatches and not a zero of files read
  assert.ok(dutyUses > 0, 'no shipped file draws a --mark-* duty token: the scan above is reading nothing');
});

test('inside the stylesheet a hatch is read only by a --mark-* declaration', () => {
  const { decls } = readTokens();
  const stray = decls
    .filter(([n, v]) => !n.startsWith('--mark-') && !isHatch(n) && readsVar(v).some(isHatch))
    .map(([n]) => n);
  assert.deepEqual(stray, [], `these properties read a hatch without being a duty: ${stray}`);
  // the rule-level CSS below the :root blocks (a selector's own background-image) as well
  const rules = stripCss(readFileSync(TOKENS, 'utf8'))
    .split('}').filter((b) => !/:root\s*\{/.test(b) && /var\(\s*--(hatch|stipple)-/.test(b));
  assert.deepEqual(rules, [], 'a selector in tokens.css paints a hatch by name');
});

test('the raw-hatch reader sees a use in code and ignores one in a comment', () => {
  assert.deepEqual(rawHatchUses("style={{ backgroundImage: 'var(--hatch-45)' }}"), ['--hatch-45']);
  assert.deepEqual(rawHatchUses("// backgroundImage: 'var(--hatch-45)'\n/* var(--hatch-135) */"), []);
  assert.deepEqual(rawHatchUses("backgroundImage: 'var(--mark-wanted)'"), []);
});

/* ─────────────────────────── 3. tokens, records and forms, one to one ─────────────────────────── */

test('each --mark-* property is named by exactly one record, each record names a declared one', (t) => {
  const recs = records();
  if (!recs.length) { t.skip('COULD NOT EVALUATE: no glossary/*.json records on this tree'); return; }
  const { marks } = dutiesOf();
  assert.ok(marks.length > 0, 'the premise: the stylesheet declares duty tokens');
  const named = new Map();
  for (const r of recs.filter((x) => typeof x.mark === 'string')) {
    named.set(r.mark, [...(named.get(r.mark) || []), r.id]);
  }
  for (const m of marks) {
    const who = named.get(m) || [];
    assert.equal(who.length, 1, `${m} is named by ${who.length} records (${who.join(', ') || 'none'}): `
      + 'a mark with no record has no word for the key, and two records give it two');
  }
  for (const m of named.keys()) {
    assert.ok(marks.includes(m), `a record names ${m}, which tokens.css does not declare`);
  }
});

test('marks.js gives a form to exactly the duty tokens the stylesheet declares', () => {
  const { marks } = dutiesOf();
  assert.deepEqual(Object.keys(MARK_FORMS).sort(), [...marks].sort(),
    'a token with no form cannot be drawn; a form for an undeclared token draws nothing');
  for (const token of marks) {
    const style = markGlyph(token, 13);
    assert.ok(style && typeof style === 'object', `${token} draws nothing`);
    // every form paints from its own token, never from another mark's or a hatch's
    const paints = JSON.stringify(style).match(/var\(--(?:mark|hatch|stipple)-[a-z0-9-]+\)/g) || [];
    assert.deepEqual([...new Set(paints)], [`var(${token})`], `${token} paints with ${paints}`);
  }
  assert.equal(markGlyph('--mark-nothing-by-this-name'), null, 'an unknown token draws nothing, not another mark');
});

test('the three that are not a verdict are never drawn as one another, nor as a verdict', () => {
  const form = (state) => MARK_FORMS[JUDGMENT_MARKS[state].token];
  const nonVerdicts = ['unjudged', 'yours-to-judge', 'not-applicable'];
  const forms = nonVerdicts.map(form);
  assert.equal(new Set(forms).size, forms.length, `two of ${nonVerdicts} share a form: ${forms}`);
  const verdictForms = new Set(['pass', 'fail'].map(form));
  for (const s of nonVerdicts) assert.ok(!verdictForms.has(form(s)), `${s} is drawn in a verdict's form`);
  // and the marks that are not a state of a house borrow no judgment's form either
  const judgmentForms = new Set(Object.keys(JUDGMENT_MARKS).map(form));
  for (const r of records().filter((x) => x.family === 'mark' && x.mark)) {
    assert.ok(!judgmentForms.has(MARK_FORMS[r.mark]), `${r.id} is drawn in a judgment's form`);
  }
});

test('every state JudgmentMark draws has its record, and that record names its token', (t) => {
  const recs = records();
  if (!recs.length) { t.skip('COULD NOT EVALUATE: no glossary/*.json records on this tree'); return; }
  const byId = new Map(recs.map((r) => [r.id, r]));
  for (const [state, { token, record }] of Object.entries(JUDGMENT_MARKS)) {
    assert.ok(byId.has(record), `${state}'s record ${record} does not exist`);
    assert.equal(byId.get(record).mark, token, `${record} does not name ${token}`);
  }
  // and the other direction: a judgment record carrying a mark is a state JudgmentMark can draw
  const drawn = new Set(Object.values(JUDGMENT_MARKS).map((m) => m.record));
  for (const r of recs.filter((x) => x.family === 'judgment' && x.mark)) {
    assert.ok(drawn.has(r.id), `${r.id} carries a mark JudgmentMark has no state for`);
  }
  // every judgment `judgment.js` can return is one of JudgmentMark's states
  for (const s of Object.values(JUDGMENT_MARK)) assert.ok(s in JUDGMENT_MARKS, `${s} has no mark`);
});

/* The server's order: the schema's family enum, then `order`, then id. */
function payload(recs) {
  const fams = JSON.parse(readFileSync(new URL('schema/glossary-term.schema.json', ROOT), 'utf8'))
    .properties.family.enum;
  const sorted = [...recs].sort((a, b) => fams.indexOf(a.family) - fams.indexOf(b.family)
    || (a.order ?? 1e9) - (b.order ?? 1e9) || (a.id < b.id ? -1 : a.id > b.id ? 1 : 0));
  const byFamily = Object.fromEntries(fams.map((f) => [f, sorted.filter((r) => r.family === f).map((r) => r.id)]));
  return { terms: sorted, by_family: byFamily };
}

test('the product key is every marked record, once, grouped under its family, and nothing else', (t) => {
  const recs = records();
  if (!recs.length) { t.skip('COULD NOT EVALUATE: no glossary/*.json records on this tree'); return; }
  const groups = markKeyGroups(indexTerms(payload(recs)));
  const shown = groups.flatMap((g) => g.rows.map((r) => r.id));
  const marked = recs.filter((r) => typeof r.mark === 'string').map((r) => r.id);
  assert.ok(marked.length > 0, 'the premise: some record carries a mark');
  assert.deepEqual([...shown].sort(), [...marked].sort(), 'the key shows exactly the marked records');
  assert.equal(new Set(shown).size, shown.length, 'no record is shown twice');
  for (const g of groups) for (const r of g.rows) assert.equal(r.family, g.family);
  // and the key's every row can be drawn
  for (const g of groups) for (const r of g.rows) assert.ok(markGlyph(r.mark), `${r.id}'s mark has no form`);
  assert.deepEqual(markKeyGroups(null), [], 'no glossary, no key -- never an invented one');
});

/* ─────────────────────────── 4. --t3 ─────────────────────────── */

/* A palette ink: a custom property the stylesheet declares with a hex literal. */
function resolve(byName, name, seen = new Set()) {
  assert.ok(!seen.has(name), `${name} refers to itself`);
  seen.add(name);
  const v = byName.get(name);
  assert.ok(v !== undefined, `${name} is not declared`);
  const ref = /^var\(\s*(--[A-Za-z0-9_-]+)\s*\)$/.exec(v);
  return ref ? resolve(byName, ref[1], seen) : v.toUpperCase();
}

function t3Verdict(css) {
  const { byName } = readTokens(css);
  const v = byName.get('--t3');
  const ref = v && /^var\(\s*(--[A-Za-z0-9_-]+)\s*\)$/.exec(v);
  if (!ref) return `--t3 is ${v}, a colour typed where an existing ink should be named`;
  const ink = ref[1];
  const inkValue = byName.get(ink);
  if (!/^#[0-9A-Fa-f]{6}$/.test(inkValue || '')) return `--t3 names ${ink}, which is not a palette ink`;
  if (/^--t\d$/.test(ink)) return `--t3 names another tradition, ${ink}`;
  if (resolve(byName, '--t3') === resolve(byName, '--brick')) return '--t3 resolves to the brick of the UI\'s fatal';
  return null;
}

test('--t3 names an existing ink of the palette, and that ink is not brick', () => {
  assert.equal(t3Verdict(), null);
});

test('the --t3 verdict refuses the brick, a typed colour and a non-ink, each for its own reason', () => {
  const css = readFileSync(TOKENS, 'utf8');
  const decl = /--t3:[^;]+;/;
  assert.ok(decl.test(stripCss(css)), 'the premise: --t3 is declared where this reader looks');
  assert.match(t3Verdict(css.replace(decl, '--t3:var(--brick);')), /brick/);
  assert.match(t3Verdict(css.replace(decl, '--t3:#AF6B50;')), /typed/);
  assert.match(t3Verdict(css.replace(decl, '--t3:#123456;')), /typed/);
  assert.match(t3Verdict(css.replace(decl, '--t3:var(--judge-fail);')), /not a palette ink/);
});

/* ─────────────────────────── 5. --refusal ─────────────────────────── */

/* RULED 26 Sep 2026 (oq/a-refusal-is-drawn-in-two-inks-and-one-is-a-traditions-hue, closed): a
   refusal is brick everywhere. The mark in the masthead (`--mark-refused`) and every refusal card,
   banner and plate (`--refusal`) were two inks, and the card's violet was byte for byte `--t4`,
   the hue every North American style is drawn in. Both are resolved from the stylesheet here, so
   a colour typed into either, or a tradition taking the refusal's ink, fails by name. */
function refusalVerdict(css) {
  const { byName } = readTokens(css);
  const card = resolve(byName, '--refusal');
  const mark = resolve(byName, '--mark-refused');
  if (card !== mark) return `--refusal resolves to ${card} and --mark-refused to ${mark}: a refusal is drawn in two inks`;
  if (card !== resolve(byName, '--brick')) return `--refusal resolves to ${card}, not the brick of the UI's fatal`;
  const t = [...byName.keys()].filter((n) => /^--t\d$/.test(n)).find((n) => resolve(byName, n) === card);
  if (t) return `${t}, a tradition's hue, resolves to the refusal's ink`;
  return null;
}

test('a refusal is one ink, the brick of the fatal, and no tradition is drawn in it', () => {
  assert.equal(refusalVerdict(), null);
});

test('the refusal verdict refuses the old violet, a second ink, and a tradition in brick', () => {
  const css = readFileSync(TOKENS, 'utf8');
  const decl = /--refusal:[^;]+;/;
  assert.ok(decl.test(stripCss(css)), 'the premise: --refusal is declared where this reader looks');
  assert.match(refusalVerdict(css.replace(decl, '--refusal:var(--violet);')), /two inks/);
  const mark = /--mark-refused:[^;]+;/;
  assert.match(refusalVerdict(css.replace(decl, '--refusal:var(--salmon);').replace(mark, '--mark-refused:var(--salmon);')),
    /not the brick/);
  assert.match(refusalVerdict(css.replace(/--t4:[^;]+;/, '--t4:var(--brick);')), /--t4, a tradition/);
});

/* ─────────────────────────── the readers that choose a mark ─────────────────────────── */

test('a style finding the check could not settle takes the mark its own kind names', () => {
  assert.equal(styleFindingMark({ layer: 'style', kind: 'constraint-unjudged', statement: 'x' }), 'unjudged');
  assert.equal(styleFindingMark({ layer: 'style', kind: 'constraint-unformalised', statement: 'x' }),
    'yours-to-judge');
  // the kind decides, not the words
  assert.equal(styleFindingMark({ layer: 'style', kind: 'constraint-unformalised',
    statement: 'Cannot evaluate this' }), 'yours-to-judge');
  assert.equal(styleFindingMark({ layer: 'style', kind: 'variant-forbidden', statement: 'Check by hand' }), null);
  // a finding with no kind is read by the two sentences the check writes, and nothing else
  assert.equal(styleFindingMark({ layer: 'style', statement: 'Cannot evaluate c.1 (kind): s' }), 'unjudged');
  assert.equal(styleFindingMark({ layer: 'style', statement: 'Check by hand: s' }), 'yours-to-judge');
  assert.equal(styleFindingMark({ layer: 'style', statement: 'A forbidden variant' }), null);
  // another layer is not this panel's
  assert.equal(styleFindingMark({ layer: 'fault', kind: 'constraint-unjudged' }), null);
  assert.equal(styleFindingMark(null), null);
});

test('a derived rule the sources leave to the reader is drawn as that, while its verdict stays unjudged', () => {
  const judged = { judgment: true, value: 3 };
  assert.equal(ruleState(judged), 'unjudged', 'the tally still counts it as no verdict');
  assert.equal(ruleMark(judged), 'yours-to-judge', 'and the mark says it is handed to the reader');
  assert.equal(ruleMark({ value: 3, in_range: true }), 'pass');
  assert.equal(ruleMark({ value: 3, in_range: false }), 'fail');
  assert.equal(ruleMark({ value: null }), 'unjudged');
  assert.equal(ruleMark({ value: 3, in_range: true, out_of_calibration: true }), 'unjudged');
  for (const r of [judged, { value: 3, in_range: true }, { value: null }]) {
    assert.ok(ruleMark(r) in JUDGMENT_MARKS, `${JSON.stringify(r)} takes a state JudgmentMark cannot draw`);
  }
});

test('JudgmentMark carries the state word to assistive tech on both of its branches', () => {
  /* The component imports React and cannot be loaded here; its source is read. Each branch must
     put the word in the DOM -- visibly or as visually hidden text -- beside a glyph that is
     aria-hidden, so passed and failed are never told apart by colour alone. */
  const src = readFileSync(join(SRC, 'components', 'JudgmentMark.jsx'), 'utf8');
  assert.match(src, /JUDGMENT_MARKS\[known\]/, 'JudgmentMark reads its states from marks.js');
  const bare = /if \(!label\) \{([\s\S]*?)\n  \}/.exec(src);
  assert.ok(bare, 'the premise: JudgmentMark still has a branch for a mark with no label');
  assert.match(bare[1], /className="tdl-sr-only" data-judgment-word="">\{word\}/,
    'the bare glyph must carry its word as visually hidden text');
  const labelled = src.slice(bare.index + bare[0].length);
  assert.match(labelled, /data-judgment-word=""[\s\S]*?<Term id=\{mark\.record\} \/>/,
    'the labelled mark must show its record\'s word');
  assert.match(labelled, /className="tdl-sr-only" data-judgment-word="">\{word\}/,
    'and where the visible word is withheld, it still reaches assistive tech');
  const glyph = readFileSync(join(SRC, 'components', 'MarkGlyph.jsx'), 'utf8');
  assert.match(glyph, /aria-hidden="true" data-duty=\{token\}/, 'a glyph is decorative; its word says it');
});
