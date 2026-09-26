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

const SRC = fileURLToPath(new URL('./', import.meta.url));
const TOKENS = join(SRC, 'theme', 'tokens.css');

/* Comments are not ink. Block comments (which covers a JSX comment in braces) and line comments
   that start a line or trail code; a `//` after `:` is a URL inside a string and is kept. Every
   comment is blanked to spaces rather than removed, so an offset in the stripped source is the
   same offset in the file. */
const stripComments = (s) => s.replace(/\/\*[\s\S]*?\*\//g, (m) => m.replace(/[^\n]/g, ' '))
  .replace(/(^|[\s;,{}()])\/\/[^\n]*/g, (m, lead) => lead + ' '.repeat(m.length - lead.length));

/* ── the stylesheet's own answer: which tokens are a faint ink ── */
export function faintTokens(css) {
  const live = css.replace(/\/\*[\s\S]*?\*\//g, '');
  const defs = {};
  for (const m of live.matchAll(/(--[a-z0-9-]+)\s*:\s*([^;}]+)[;}]/gi)) {
    if (!(m[1] in defs)) defs[m[1]] = m[2].trim();
  }
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
  const live = css.replace(/\/\*[\s\S]*?\*\//g, '');
  const defs = {};
  for (const m of live.matchAll(/(--[a-z0-9-]+)\s*:\s*([^;}]+)[;}]/gi)) {
    if (!(m[1] in defs)) defs[m[1]] = m[2].trim();
  }
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
    seen += (stripComments(src).match(/var\(--link-underline\)/g) || []).length;
    for (const r of linkUnderlineRows(src, css)) rows.push([p.slice(SRC.length), ...r]);
  }
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
