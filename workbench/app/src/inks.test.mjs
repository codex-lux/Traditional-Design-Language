/* NO READABLE TEXT IN A FAINT INK, ANYWHERE IN THE APP (WP-14.31).

   Measured on paper: `--ink-4` reads 2.26 : 1 and `--ink-3` 3.15 : 1, and a line of type needs
   4.5 : 1 below large sizes; `--ink-2` reads 4.85 : 1. The standard keeps the two faint inks for
   rules, hairlines, disabled states and marks, and five earlier packages each held THEIR OWN files
   to that (`definitions`, `dossier`, `faultCard`, `frontDoor`, `lineage` tests) while the rest of
   the tree set about a hundred and eighty lines of text in them. This file holds all of `src` to
   it at once, BY IDENTITY and not by count, so a new faint line cannot hide behind a fixed old one.

   WHAT IT READS. Every occurrence of a faint ink — `--ink-3`, `--ink-4`, and every token
   `theme/tokens.css` resolves to either value, found by resolving the stylesheet rather than by a
   list typed here (`--forthcoming`, `--unsourced`, `--sev-info`, `--hair` ...) — in every `.js`,
   `.jsx` and `.css` file under `src`, comments stripped. Each occurrence is owned by the property
   or attribute whose value holds it, innermost first, and judged by that owner:

     text     `color`, and `fill` on an SVG `<text>`/`<tspan>`: any faint ink is a row
     mark     `border*`, `background*`, `outline`, `stroke`, `fill` on a shape, `boxShadow`,
              `textDecoration*`: a rule, a hairline or a mark, and never a row
     unknown  anything else — a lookup table's entry, a fallback after `||`, a prop handed on:
              a row, unless the token is one the stylesheet names for a LINE (`--rule`,
              `--hair`, the border and grid aliases), because a table entry is how a faint ink
              reaches a text span without ever being written beside `color`

   `--text-disabled` is the disabled state's own token, named for its duty, and is never a row:
   a disabled control is exactly what the faint ink is for.

   THE LIST IS EXPECTED TO BE THE THREE PLATE ROWS BELOW AND NOTHING ELSE. Each is drawing ink,
   not interface type, and each is held elsewhere: two are inside `OrderPlate`, which the tranche's
   contract forbids any change to, and one is the plan sheet's bay figures, drawn in the construction
   ink the Python plate draws them in (`build/render_plan.py`, the bay module labels), where a change
   would part the two renderers. A row that is gone must leave the list in the same commit.

   `INK_RATCHET_PRINT=1 node --test src/inks.test.mjs` prints the current rows. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { stripComments } from './sourceReader.mjs';

const SRC = fileURLToPath(new URL('./', import.meta.url));
const TOKENS = join(SRC, 'theme', 'tokens.css');

/* Comments are not ink. They are blanked to spaces by `sourceReader.mjs`, the lexer the copy
   ratchets share, so an offset in the stripped source is the same offset in the file. The pair of
   regular expressions this file carried read the file-type pattern in `Transcription.jsx`'s
   `accept=` attribute as the start of a comment, and was blind to the 79 lines after it
   (WP-14.33's audit). */

/* A stylesheet's custom properties, LAST DECLARATION WINNING as CSS has it (WP-14.33's audit: this
   file took the first, so a second `:root{--link:...}` appended below the first passed every
   verdict here while the page drew the second). The reduced-motion durations are the one
   legitimate redeclaration, and `test_no colour token is declared twice` holds the rest. */
export function cssTokens(css) {
  const live = css.replace(/\/\*[\s\S]*?\*\//g, '');
  const defs = {};
  for (const m of live.matchAll(/(--[a-z0-9-]+)\s*:\s*([^;}]+)[;}]/gi)) defs[m[1]] = m[2].trim();
  return defs;
}

/* ── the stylesheet's own answer: which tokens are a faint ink ── */
export function faintTokens(css) {
  const defs = cssTokens(css);
  const resolve = (name, seen = new Set()) => {
    if (seen.has(name) || defs[name] == null) return null;
    seen.add(name);
    const r = /^var\((--[a-z0-9-]+)\)$/i.exec(defs[name]);
    return r ? resolve(r[1], seen) : defs[name].toUpperCase();
  };
  const faint = new Set([resolve('--ink-3'), resolve('--ink-4')].filter(Boolean));
  const out = new Set();
  for (const n of Object.keys(defs)) if (faint.has(resolve(n))) out.add(n);
  return out;
}

/* Tokens whose NAME is a line's duty. In an owner this file cannot place, one of these is taken
   at its word; in a `color` it is still a row, because a text span in hairline ink is the defect
   whatever the token is called. */
const LINE_TOKENS = new Set(['--rule', '--hair', '--draw-grid', '--border-hairline', '--border-paper',
  '--bistre-4', '--vellum-edge', '--edge-claims', '--mark-low-confidence', '--judge-unjudged']);
const DISABLED = '--text-disabled';

/* The value expression that starts at `i`: up to the first top-level `,` `;` or closing
   bracket, strings and template literals skipped whole. */
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
    else if (c === ')' || c === ']' || c === '}') {
      if (depth === 0) return j;
      depth -= 1;
      if (depth === 0 && src[i] === '{' && c === '}') return j + 1;   // a JSX attr's `{...}`
    } else if ((c === ',' || c === ';') && depth === 0) return j;
  }
  return src.length;
}

/* Every owner in a source: object keys, CSS declarations and JSX attributes, with the span of
   the value each owns. */
function owners(src, isCss) {
  const out = [];
  const keyRe = isCss
    ? /(?<=[{;]\s*)(--[a-z0-9-]+|[a-z-]+)\s*:(?!:)/g
    : /(?<=(?:^|[{,(])\s*)([A-Za-z_$][\w$]*|'[^'\n]+'|"[^"\n]+")\s*:(?!:)/gm;
  for (const m of src.matchAll(keyRe)) {
    const start = m.index + m[0].length;
    let s = start;
    while (/\s/.test(src[s] || '')) s += 1;
    out.push({ name: m[1].replace(/^['"]|['"]$/g, ''), at: m.index, start: s, end: valueEnd(src, s) });
  }
  if (!isCss) {
    for (const m of src.matchAll(/(?<=\s)([A-Za-z][\w-]*)=(?=["'{])/g)) {
      const s = m.index + m[0].length;
      let end;
      if (src[s] === '{') end = valueEnd(src, s);
      else end = src.indexOf(src[s], s + 1) + 1;
      out.push({ name: m[1], at: m.index, start: s, end, attr: true });
    }
  }
  return out;
}

/* The element an owner sits on, where it can be told: the nearest JSX tag or createElement
   call opened before it. Only `fill` asks, to tell a text span from a shape. */
function elementAt(src, at) {
  const before = src.slice(Math.max(0, at - 600), at);
  let tag = null;
  for (const m of before.matchAll(/<([A-Za-z][\w.]*)|createElement\(\s*["']([\w.]+)["']|\bh\(\s*["']([\w.]+)["']/g)) {
    tag = m[1] || m[2] || m[3];
  }
  return tag;
}

const MARK = /^(border|background|outline|stroke|boxShadow|box-shadow|textDecoration|text-decoration|columnRule|column-rule|stopColor|stop-color|floodColor|scrollbar)/;
const TEXT_TAGS = new Set(['text', 'tspan', 'textPath']);

function classify(owner, src) {
  if (!owner) return 'unknown';
  const n = owner.name;
  if (n.startsWith('--')) return 'definition';
  if (n === 'color' || n === 'WebkitTextFillColor' || n === '-webkit-text-fill-color') return 'text';
  if (n === 'fill') return TEXT_TAGS.has(elementAt(src, owner.at)) ? 'text' : 'mark';
  if (MARK.test(n)) return 'mark';
  return 'unknown';
}

const squash = (s) => s.replace(/\s+/g, ' ').trim();

/* source → rows: [owner, the owner's value] for every faint ink a reader may be asked to read. */
export function inkRows(source, faint, isCss = false) {
  const src = stripComments(source);
  const all = owners(src, isCss);
  const rows = [];
  for (const m of src.matchAll(/var\(\s*(--[a-z0-9-]+)/gi)) {
    const token = m[1];
    if (!faint.has(token) || token === DISABLED) continue;
    const k = m.index;
    let own = null;
    for (const o of all) {
      if (o.start <= k && k < o.end && (!own || (o.end - o.start) < (own.end - own.start))) own = o;
    }
    const kind = classify(own, src);
    if (kind === 'definition' || kind === 'mark') continue;
    if (kind === 'unknown' && LINE_TOKENS.has(token)) continue;
    const value = own ? squash(src.slice(own.start, own.end)) : squash(src.slice(Math.max(0, k - 40), k + 20));
    rows.push([own ? own.name : '(bare)', value]);
  }
  return rows;
}

function files(dir = SRC, out = []) {
  for (const f of readdirSync(dir).sort()) {
    const p = join(dir, f);
    if (statSync(p).isDirectory()) files(p, out);
    else if (/\.(jsx|js|css)$/.test(f)) out.push(p);
  }
  return out;
}

function current() {
  const faint = faintTokens(readFileSync(TOKENS, 'utf8'));
  const rows = [];
  for (const p of files()) {
    const rel = p.slice(SRC.length);
    for (const r of inkRows(readFileSync(p, 'utf8'), faint, p.endsWith('.css'))) rows.push([rel, ...r]);
  }
  return rows;
}

// BASELINE-BEGIN
const BASELINE = [
  ['sheet/Sheet.jsx', 'fill', '"var(--hair)"'],
  ['surfaces/Proportions.jsx', 'fill', '"var(--ink-4)"'],
  ['surfaces/Proportions.jsx', 'fill', '"var(--ink-4)"'],
];
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

if (process.env.INK_RATCHET_PRINT) console.log(JSON.stringify(current(), null, 1));

test('the faint inks are the stylesheet’s own answer, aliases included, and the line ink is among them', () => {
  const faint = faintTokens(readFileSync(TOKENS, 'utf8'));
  for (const t of ['--ink-3', '--ink-4', '--hair', '--forthcoming', '--unsourced', '--sev-info', DISABLED]) {
    assert.ok(faint.has(t), `${t} resolves to a faint ink`);
  }
  for (const t of ['--ink', '--ink-2', '--gilt-deep', '--brick']) assert.ok(!faint.has(t), `${t} is not faint`);
});

test('the scanner owns each faint ink by its property, and reads text, a table and a fallback as rows', () => {
  const faint = new Set(['--ink-3', '--ink-4', '--hair', '--rule', DISABLED]);
  const fixture = [
    "<span style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)' }}>x</span>",       // text
    "<span style={{ color: on ? 'var(--ink)' : 'var(--ink-3)' }}>x</span>",                // text, conditional
    '<text x={1} fill="var(--ink-4)">label</text>',                                         // svg text
    "const T = { quiet: 'var(--ink-4)', body: 'var(--ink)' };",                             // a table
    "const hue = HUES[id] || 'var(--ink-3)';",                                              // a fallback
    "<div style={{ borderTop: '1px solid var(--ink-4)', background: 'var(--ink-3)' }} />",  // marks
    '<rect fill="var(--ink-4)" stroke="var(--ink-3)" />',                                   // shape marks
    "<span style={{ color: disabled ? 'var(--text-disabled)' : 'var(--ink-2)' }}>x</span>", // disabled
    "const L = { claims: 'var(--rule)' };",                                                 // a line token
    "/* <span style={{ color: 'var(--ink-4)' }} /> */",                                     // a comment
    "<span style={{ color: 'var(--hair)' }}>x</span>",                                      // hairline as text
  ].join('\n');
  const rows = inkRows(fixture, faint);
  assert.deepEqual(rows.map((r) => r[0]), ['color', 'color', 'fill', 'quiet', '(bare)', 'color']);
});

test('the premise: the scan reads the whole app and finds the marks it must leave alone', () => {
  const all = files();
  assert.ok(all.length > 60, 'the walk found the app’s sources');
  const faint = faintTokens(readFileSync(TOKENS, 'utf8'));
  let seen = 0;
  for (const p of all) {
    const src = stripComments(readFileSync(p, 'utf8'));
    for (const m of src.matchAll(/var\(\s*(--[a-z0-9-]+)/g)) if (faint.has(m[1])) seen += 1;
  }
  assert.ok(seen > current().length, 'the faint inks still draw rules and marks, which are not rows');
});

test('no new readable text in a faint ink anywhere in src', () => {
  assert.deepEqual(minus(current(), BASELINE), [],
    'text in --ink-3 or --ink-4 (or a token that resolves to either) reads below 4.5 : 1 on paper; '
    + 'set it in --ink-2, or --text-disabled for a disabled control');
});

test('the list only shrinks: a row that is gone must leave it in the same commit', () => {
  assert.deepEqual(minus(BASELINE, current()), [],
    'these rows no longer exist in the tree; delete them from BASELINE');
});

/* ─────────────────── LINKS READ IN INK (WP-14.33, ruled 26 Sep 2026) ───────────────────

   oq/the-link-ink-reads-below-aa, closed: every link was set in --gilt-deep, 4.09 : 1 on --paper
   and 3.64 on --paper-deep, under the 4.5 a line of small type needs. The ruling keeps the gilt as
   the link's MARK -- the hairline underline -- and sets the text in the working ink. Two readers
   hold it, both from the stylesheet's own values rather than a list typed here:
     1. `--link` reads 4.5 : 1 or better on each of the four paper grounds, and the `a` rule is
        underlined in the gilt `--link-underline`;
     2. every style in `src` that draws the link underline sets its own text colour, and every ink
        that colour can take (both arms of a conditional) reads 4.5 : 1 on --paper. A link-styled
        button left in --gilt-deep is exactly the shape the ruling removed. */
const PAPERS = ['--paper', '--paper-mat', '--paper-deep', '--paper-lit'];

function tokenValues(css) {
  const defs = cssTokens(css);
  const hex = (name, seen = new Set()) => {
    if (seen.has(name) || defs[name] == null) return null;
    seen.add(name);
    const r = /^var\((--[a-z0-9-]+)\)$/i.exec(defs[name]);
    if (r) return hex(r[1], seen);
    return /^#[0-9a-f]{6}$/i.test(defs[name]) ? defs[name].toUpperCase() : null;
  };
  return { defs, hex };
}

export function contrast(a, b) {
  const lum = (h) => {
    const c = [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16) / 255)
      .map((v) => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4));
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
  };
  const [hi, lo] = [lum(a), lum(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
}

export function linkTokenVerdict(css) {
  const { defs, hex } = tokenValues(css);
  const ink = hex('--link');
  if (!ink) return `--link resolves to ${defs['--link']}, which is not an ink of the palette`;
  for (const p of PAPERS) {
    const r = contrast(ink, hex(p));
    if (r < 4.5) return `--link reads ${r.toFixed(2)} : 1 on ${p}, under 4.5`;
  }
  const live = css.replace(/\/\*[\s\S]*?\*\//g, '');
  const aRule = /(^|\n)a\{([^}]*)\}/.exec(live);
  if (!aRule || !/border-bottom:[^;]*var\(--link-underline\)/.test(aRule[2])) {
    return 'the `a` rule does not draw the link underline, so a link in ink reads as plain text';
  }
  if (!/175\s*,\s*141\s*,\s*73|var\(--gilt/i.test(defs['--link-underline'] || '')) {
    return `--link-underline is ${defs['--link-underline']}, which is not the gilt`;
  }
  // THE HOVER HALF (WP-14.33's audit): the ruling's "on hover a full gilt rule" was held by nothing,
  // and `--link-underline-hover: var(--ink)` passed. It resolves to a gilt, and both the `a` rule and
  // `.tdl-link` -- the class a button that is a link takes -- switch to it on hover.
  const gilts = new Set(['--gilt', '--gilt-deep'].map((n) => hex(n)).filter(Boolean));
  if (!gilts.has(hex('--link-underline-hover'))) {
    return `--link-underline-hover is ${defs['--link-underline-hover']}, which is not the gilt`;
  }
  for (const sel of ['a:hover', '.tdl-link:hover']) {
    const r = new RegExp(`(^|\\n)${sel.replace('.', '\\.')}\\{([^}]*)\\}`).exec(live);
    if (!r || !/border-bottom-color:\s*var\(--link-underline-hover\)/.test(r[2])) {
      return `the \`${sel}\` rule does not draw the gilt rule on hover`;
    }
  }
  const cls = /(^|\n)\.tdl-link\{([^}]*)\}/.exec(live);
  if (!cls || !/color:\s*var\(--link\)/.test(cls[2]) || !/border-bottom:[^;]*var\(--link-underline\)/.test(cls[2])) {
    return 'the `.tdl-link` class does not set the link ink and its underline';
  }
  return null;
}

/* The innermost `{ ... }` enclosing offset `at`, braces inside strings not special-cased: the
   style objects this reads carry none. */
function enclosing(src, at) {
  let depth = 0; let open = -1;
  for (let i = at; i >= 0; i -= 1) {
    if (src[i] === '}') depth += 1;
    else if (src[i] === '{') { if (depth === 0) { open = i; break; } depth -= 1; }
  }
  if (open < 0) return null;
  depth = 0;
  for (let j = open; j < src.length; j += 1) {
    if (src[j] === '{') depth += 1;
    else if (src[j] === '}') { depth -= 1; if (depth === 0) return src.slice(open, j + 1); }
  }
  return null;
}

export function linkUnderlineRows(src, css) {
  const { hex } = tokenValues(css);
  const paper = hex('--paper');
  const rows = [];
  const live = stripComments(src);
  for (const m of live.matchAll(/var\(--link-underline\)/g)) {
    const block = enclosing(live, m.index);
    if (!block) { rows.push(['(no block)', m.index]); continue; }
    const colour = /(?:^|[{\s,;])color\s*:\s*([^,;}\n]+(?:\?[^,;}\n]+)?)/.exec(block);
    if (!colour) { rows.push(['(no colour of its own)', block.slice(0, 60)]); continue; }
    const names = [...colour[1].matchAll(/var\((--[a-z0-9-]+)\)/g)].map((x) => x[1]);
    if (!names.length) { rows.push(['(a typed colour)', colour[1].trim()]); continue; }
    for (const n of names) {
      const h = hex(n);
      const r = h ? contrast(h, paper) : 0;
      if (r < 4.5) rows.push([n, r.toFixed(2)]);
    }
  }
  return rows;
}

test('the link is set in ink that reads on every paper, and marked by the gilt underline', () => {
  assert.equal(linkTokenVerdict(readFileSync(TOKENS, 'utf8')), null);
});

test('the link verdict refuses the old gilt text and an `a` rule with no underline', () => {
  const css = readFileSync(TOKENS, 'utf8');
  const decl = /--link:var\([^)]*\);/;
  assert.ok(decl.test(css), 'the premise: --link is declared where this reader looks');
  assert.match(linkTokenVerdict(css.replace(decl, '--link:var(--gilt-deep);')), /under 4\.5/);
  assert.match(linkTokenVerdict(css.replace(/\na\{[^}]*\}/, '\na{color:var(--link)}')), /does not draw/);
});

test('every style that draws the link underline sets its own text in an ink that reads', () => {
  const css = readFileSync(TOKENS, 'utf8');
  const rows = [];
  let seen = 0;
  for (const p of files()) {
    const src = readFileSync(p, 'utf8');
    const live = stripComments(src);
    seen += (live.match(/var\(--link-underline\)/g) || []).length;
    seen += (live.match(/className[=:]\s*[^,}\n]*tdl-link/g) || []).length;
    for (const r of linkUnderlineRows(src, css)) rows.push([p.slice(SRC.length), ...r]);
  }
  // Inline, or through the `.tdl-link` class most controls took at WP-14.33's audit.
  assert.ok(seen >= 10, `the premise: the underline is drawn in many places (${seen})`);
  assert.deepEqual(rows, [], 'a link-styled element reads below 4.5 : 1; set it in var(--link)');
});

test('the underline reader finds gilt text, a conditional arm, and a missing colour', () => {
  const css = readFileSync(TOKENS, 'utf8');
  const f = (s) => linkUnderlineRows(s, css).map((r) => r[0]);
  assert.deepEqual(f("<b style={{ color: 'var(--gilt-deep)', borderBottom: '1px solid var(--link-underline)' }} />"),
    ['--gilt-deep']);
  assert.deepEqual(f("<b style={{ color: on ? 'var(--link)' : 'var(--ink-4)', borderBottom: '1px solid var(--link-underline)' }} />"),
    ['--ink-4']);
  assert.deepEqual(f("<b style={{ borderBottom: '1px solid var(--link-underline)' }} />"), ['(no colour of its own)']);
  assert.deepEqual(f("<b style={{ color: 'var(--link)', borderBottom: '1px solid var(--link-underline)' }} />"), []);
});

/* An `<a>` takes the `a` rule's ink unless it sets its own, and three did, in --gilt-deep, which
   put those links back under the floor the ruling raised them to. Every colour an anchor sets
   for itself -- in JSX or in a compiled `createElement("a", ...)` -- is held to the same 4.5. */
export function anchorColourRows(src, css) {
  const { hex } = tokenValues(css);
  const paper = hex('--paper');
  const live = stripComments(src);
  const rows = [];
  for (const m of live.matchAll(/<a\b|createElement\(\s*["']a["']/g)) {
    const seg = live.slice(m.index, m.index + 600);
    const stop = seg.startsWith('<a') ? seg.search(/>(?![^{]*\})/) : seg.indexOf('}, ');
    const head = stop > 0 ? seg.slice(0, stop + 1) : seg;
    const colour = /(?:^|[{\s,;])color\s*:\s*([^,;}\n]+(?:\?[^,;}\n]+)?)/.exec(head);
    if (!colour) continue;
    for (const x of colour[1].matchAll(/var\((--[a-z0-9-]+)\)/g)) {
      const h = hex(x[1]);
      const r = h ? contrast(h, paper) : 0;
      if (r < 4.5) rows.push([x[1], r.toFixed(2)]);
    }
  }
  return rows;
}

test('no anchor sets its own text in an ink under 4.5 : 1', () => {
  const css = readFileSync(TOKENS, 'utf8');
  const rows = [];
  let anchors = 0;
  for (const p of files()) {
    const src = readFileSync(p, 'utf8');
    anchors += (stripComments(src).match(/<a\b|createElement\(\s*["']a["']/g) || []).length;
    for (const r of anchorColourRows(src, css)) rows.push([p.slice(SRC.length), ...r]);
  }
  assert.ok(anchors >= 10, `the premise: the app has anchors to read (${anchors})`);
  assert.deepEqual(rows, [], 'an anchor sets its text below 4.5 : 1; let it take var(--link)');
});

test('the anchor reader sees a gilt anchor and passes one in the link ink', () => {
  const css = readFileSync(TOKENS, 'utf8');
  assert.deepEqual(anchorColourRows("<a href=\"#x\" style={{ color: 'var(--gilt-deep)' }}>x</a>", css).map((r) => r[0]),
    ['--gilt-deep']);
  assert.deepEqual(anchorColourRows("<a href=\"#x\" style={{ color: on ? 'var(--gilt-deep)' : undefined }}>x</a>", css)
    .map((r) => r[0]), ['--gilt-deep']);
  assert.deepEqual(anchorColourRows("<a href=\"#x\" style={{ color: 'var(--link)' }}>x</a>", css), []);
  assert.deepEqual(anchorColourRows("<a href=\"#x\">x</a><span style={{ color: 'var(--gilt-deep)' }}/>", css), []);
});

/* ─────────── A CONTROL'S OWN TEXT INK, AND THE LINK CLASS (WP-14.33's audit) ───────────

   The two readers above see an element that draws the link underline and an `<a>`. A button that
   NAVIGATES and draws no underline was invisible to both, and three were still in --gilt-deep at
   4.09 : 1: FaultCard's slot names, SlotRow's fault names and ToolTrace's "open", each calling
   `onCite` on the way. And a control converted at R3 could be reverted to exactly its pre-ruling
   state with both readers green. So every CLICKABLE element in src -- JSX, or a compiled
   `createElement(tag, { onClick ... })` -- whose own `color` can take an ink under 4.5 : 1 on paper
   is a row, held BY IDENTITY with a class:
     action   it acts in place -- a fold, a compose, a revoke, a request, "show on drawing"
     chip     a bordered chip, whose ink is `Chrome.jsx`'s own
   There is no `link` class: a control that navigates is set in `var(--link)`, and a row whose
   handler reaches `onCite`, `onFault`, `onSlot`, `go(` or a `href` fails whatever it is classed.
   The remainder in gilt is the same shape as the links were, below AA; it is the open question
   `oq/two-inks-set-as-small-text-read-below-aa`, not a pass. `--text-disabled` is the disabled
   state's own token and is never a row. */
function span(src, i, open, close) {
  let d = 0;
  for (let j = i; j < src.length; j += 1) {
    const c = src[j];
    if (c === '"' || c === "'" || c === '`') {
      let k = j + 1;
      while (k < src.length && src[k] !== c) { if (src[k] === '\\') k += 1; k += 1; }
      j = k;
      continue;
    }
    if (c === open) d += 1;
    else if (c === close) { d -= 1; if (d === 0) return j + 1; }
  }
  return src.length;
}

/* The opening tag of the JSX element at `i`, attributes and their `{...}` whole. */
function tagHead(src, i) {
  for (let j = i + 1; j < src.length; j += 1) {
    const c = src[j];
    if (c === '"' || c === "'") { let k = j + 1; while (k < src.length && src[k] !== c) k += 1; j = k; continue; }
    if (c === '{') { j = span(src, j, '{', '}') - 1; continue; }
    if (c === '>') return src.slice(i, j + 1);
  }
  return src.slice(i);
}

/* Every element head in a source: [tag, head], a JSX opening tag or a createElement props object.
   A head is cut at the first nested `<`, so an attribute holding another element's JSX is not read
   as this element's own. */
function heads(live) {
  const out = [];
  for (const m of live.matchAll(/<([A-Za-z][\w.]*)\b/g)) {
    let h = tagHead(live, m.index);
    const inner = h.indexOf('<', 1);
    if (inner > 0) h = h.slice(0, inner);
    out.push([m[1], h]);
  }
  // The tag is any first argument, `onCite ? "button" : "span"` included: requiring a literal or a
  // bare name left FindingRow's rule reference unread (found by this file's own first run).
  for (const m of live.matchAll(/createElement\(\s*([^,{}()]+?)\s*,\s*\{/g)) {
    const o = m.index + m[0].length - 1;
    out.push([m[1].replace(/\s+/g, ' ').replace(/["']/g, ''), live.slice(o, span(live, o, '{', '}'))]);
  }
  return out;
}

const COLOUR = /(?:^|[{\s,;])color\s*:\s*([^,;}\n]+(?:\?[^,;}\n]+)?)/;
export function clickableInkRows(src, css) {
  const { hex } = tokenValues(css);
  const paper = hex('--paper');
  const rows = [];
  for (const [tag, head] of heads(stripComments(src))) {
    const oc = /\bonClick\s*[=:]\s*/.exec(head);
    if (!oc) continue;
    const colour = COLOUR.exec(head);
    if (!colour) continue;
    const handler = head.slice(oc.index + oc[0].length).replace(/\s+/g, ' ').trim().slice(0, 60);
    for (const x of colour[1].matchAll(/var\((--[a-z0-9-]+)\)/g)) {
      if (x[1] === DISABLED) continue;
      const h = hex(x[1]);
      const r = h ? contrast(h, paper) : 0;
      if (r < 4.5) rows.push([tag, x[1], handler]);
    }
  }
  return rows;
}

/* An element carrying `.tdl-link` that sets its own colour or underline inline defeats the class's
   hover, which is the defect the class exists to remove. */
export function linkClassOverrides(src) {
  const rows = [];
  for (const [tag, head] of heads(stripComments(src))) {
    if (!/className\s*[=:]\s*[^,}\n]*tdl-link/.test(head)) continue;
    const style = /\bstyle\s*[=:]\s*/.exec(head);
    if (!style) continue;
    const body = head.slice(style.index);
    if (/(?:^|[{\s,;])(?:color|borderBottom|borderColor|border|textDecoration)\s*:/.test(body)) rows.push([tag, body.slice(0, 80)]);
  }
  return rows;
}

function clickableRows() {
  const css = readFileSync(TOKENS, 'utf8');
  const rows = [];
  for (const p of files()) {
    if (!/\.(jsx|js)$/.test(p)) continue;
    for (const r of clickableInkRows(readFileSync(p, 'utf8'), css)) rows.push([p.slice(SRC.length), ...r]);
  }
  return rows;
}

const NAVIGATES = /\bonCite\s*\(|\bonFault\s*\(|\bonSlot\s*\(|\bgo\s*\(|\bhref\b|location\.hash/;

// CLICKABLE-BEGIN
/* [file, tag, token, handler, class]: `action` or `chip`, and never `link`. */
const CLICKABLE = [
  ["Chrome.jsx", "button", "--gilt-deep",
    "{onClick} title={title} {...aria} style={{ font: 'var(--type", "chip"],
  ["Chrome.jsx", "button", "--gilt-deep",
    "{onClick} title={title} disabled={disabled} style={{ font: '", "chip"],
  ["Chrome.jsx", "button", "--gilt-deep",
    "{() => setOpen(!open)} aria-expanded={open} title={open ? `F", "action"],
  ["components/FindingRow.jsx", "button", "--gilt-deep",
    "function () { onLocate(finding); }, style: { font: 'var(--ty", "action"],
  ["components/FindingRow.jsx", "button", "--green-deep",
    "function () { onAssert(finding); }, style: { font: 'var(--ty", "action"],
  ["components/ProvenanceTrace.jsx", "button", "--gilt-deep",
    "function () { setAll(true); }, style: { ...EYE, color: 'var(", "action"],
  ["components/SlotRow.jsx", "button", "--gilt-deep",
    "function () { onSource(slot.source.id); }, style: { ...EYE, ", "action"],
  ["components/UnsourcedImageRecord.jsx", "button", "--gilt-deep",
    "function () { onRequest(record); }, style: { font: 'var(--ty", "action"],
  ["dossier/ProportionsSection.jsx", "button", "--gilt-deep",
    "{() => prefs.setFold('delivered', !open)} style={{ font: 'va", "action"],
  ["surfaces/BriefIntake.jsx", "button", "--gilt-deep",
    "{compose} disabled={composing || !ready} aria-busy={composin", "action"],
  ["surfaces/PlanWorkbench.jsx", "button", "--gilt-deep",
    "{() => planDoc.update(mutations.revokeRelation(i))} style={{", "action"],
];
// CLICKABLE-END

if (process.env.INK_RATCHET_PRINT) console.log(JSON.stringify(clickableRows(), null, 1));

test('the clickable reader finds a gilt control in JSX and compiled form, and passes the link ink', () => {
  const css = readFileSync(TOKENS, 'utf8');
  const f = (x) => clickableInkRows(x, css).map((r) => [r[0], r[1]]);
  assert.deepEqual(f("<button onClick={() => onSlot(s)} style={{ color: 'var(--gilt-deep)' }}>s</button>"),
    [['button', '--gilt-deep']]);
  assert.deepEqual(f('React.createElement("button", { onClick: function () { onCite(c); }, '
    + "style: { font: 'x', color: 'var(--gilt-deep)' } }, 'open')"), [['button', '--gilt-deep']]);
  assert.deepEqual(f("<button onClick={go} style={{ color: on ? 'var(--ink)' : 'var(--green-deep)' }} />"),
    [['button', '--green-deep']]);
  assert.deepEqual(f("<button onClick={go} className=\"tdl-link\" style={{ font: 'x' }} />"), []);
  assert.deepEqual(f("<button onClick={go} style={{ color: 'var(--text-disabled)' }} />"), []);
  assert.deepEqual(f("<span style={{ color: 'var(--gilt-deep)' }}>not clickable</span>"), []);
  // another element's JSX inside an attribute is not this element's own
  assert.deepEqual(f("<Strip right={<b onClick={x} style={{ color: 'var(--gilt-deep)' }} />}>"),
    [['b', '--gilt-deep']]);
});

test('a control that navigates is set in the link ink, and the gilt remainder only shrinks', () => {
  const now = clickableRows();
  assert.ok(files().length > 60, 'the premise: the walk found the sources');
  const key = (r) => JSON.stringify(r.slice(0, 4));
  const base = CLICKABLE.map((r) => r.slice(0, 4));
  assert.deepEqual(minus(now, base), [],
    'a clickable element sets its text below 4.5 : 1. If it navigates, give it className="tdl-link" '
    + 'and drop its colour; if it acts in place, add it to CLICKABLE with its class');
  assert.deepEqual(minus(base, now), [], 'these rows are gone; delete them from CLICKABLE');
  const navigating = CLICKABLE.filter((r) => NAVIGATES.test(r[3]));
  assert.deepEqual(navigating, [], 'a control that navigates is a link and may not be held as a remainder');
  assert.deepEqual(CLICKABLE.filter((r) => !['action', 'chip'].includes(r[4])), [], 'class is action or chip');
  assert.equal(new Set(CLICKABLE.map(key)).size <= CLICKABLE.length, true);
});

test('an element with the link class sets neither its colour nor its underline inline', () => {
  const rows = [];
  let uses = 0;
  for (const p of files()) {
    if (!/\.(jsx|js)$/.test(p)) continue;
    const src = readFileSync(p, 'utf8');
    uses += (stripComments(src).match(/className[=:]\s*[^,}\n]*tdl-link/g) || []).length;
    for (const r of linkClassOverrides(src)) rows.push([p.slice(SRC.length), ...r]);
  }
  assert.ok(uses >= 10, `the premise: the class is in use (${uses})`);
  assert.deepEqual(rows, [], 'an inline colour or underline beats the class and its hover state');
  assert.deepEqual(linkClassOverrides("<button className=\"tdl-link\" style={{ borderBottom: 'none' }} />").length, 1);
});

test('no colour token is declared twice, so the reader and the page agree on every ink', () => {
  const css = readFileSync(TOKENS, 'utf8').replace(/\/\*[\s\S]*?\*\//g, '');
  const seen = {};
  for (const m of css.matchAll(/(--[a-z0-9-]+)\s*:/g)) seen[m[1]] = (seen[m[1]] || 0) + 1;
  const twice = Object.keys(seen).filter((k) => seen[k] > 1 && !k.startsWith('--dur-'));
  assert.deepEqual(twice, [], 'a token declared twice is read by CSS at its last declaration');
  // and the reader is last-wins, as CSS is
  assert.equal(cssTokens(':root{--x:#111111}\n:root{--x:#222222}')['--x'], '#222222');
});
