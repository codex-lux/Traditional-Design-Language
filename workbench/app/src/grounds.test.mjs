/* THE TWO GROUNDS HOLD (Phase 17, WP-17.0, ruled 29 Oct 2026: a dark instrument, vellum plates).

   Four properties, each with a driven twin so a reader that went blind would go red:

   1. THE BLOCKS MOVE DUTIES, NEVER PIGMENTS. Every token either ground block declares is a
      semantic duty, and no primitive (--paper, --ink, --coal, a hue) is redeclared, so a pigment
      means one thing on every ground and a token resolved for its contrast is resolved truly.
   2. VELLUM RESTORES WHAT THE INSTRUMENT MOVES. The two blocks name the same duties, and the
      vellum block's value for each is the :root value, so a plate set inside the instrument reads
      exactly as the page read before the instrument existed.
   3. EVERY TEXT DUTY READS ON ITS GROUND. 4.5 : 1 on each paper for vellum, and on --coal,
      --heavy, --heavy-2 and --coal-deep for the instrument.
   4. AN INTERFACE SETS NO COLOUR PRIMITIVE. Outside the drawing files a component asks for
      --text-body, --surface-panel and --border-hairline, never --ink, --paper or --rule, because
      only a duty follows the ground. The rows that remain are held BY FILE AND COUNT and may only
      fall; the phase audit holds them at zero. A drawing's ink is a pigment on paper, and the
      drawing files are named below with the reason. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { GROUNDS, contrast, groundTokens, groundValue, rootTokens, stripGrounds } from './grounds.js';
import { stripComments } from './sourceReader.mjs';

const SRC = fileURLToPath(new URL('./', import.meta.url));
const CSS = readFileSync(join(SRC, 'theme', 'tokens.css'), 'utf8');

// the ladders' duties joined the list with the second audit of Phase 17 (binding, variant, affinity,
// a figure's kind, a lineage edge): each names a rung, not a pigment, and each must follow its ground
const DUTY = /^--(surface|text|border|link|sev|refusal-text|receipt|judge|mark|bind|var|aff|kind|edge)(-|$)/;

test('the premise: both ground blocks exist and each moves duties', () => {
  for (const g of GROUNDS) assert.ok(Object.keys(groundTokens(CSS, g)).length >= 10, `${g} block is read`);
});

test('a ground block declares duties only, never a primitive', () => {
  for (const g of GROUNDS) {
    const stray = Object.keys(groundTokens(CSS, g)).filter((n) => !DUTY.test(n));
    assert.deepEqual(stray, [], `${g} redeclares a pigment or an undeclared kind of token`);
  }
  // and the reader sees a stray one
  const bad = CSS.replace('[data-ground="instrument"]{', '[data-ground="instrument"]{\n  --paper:#000000;');
  assert.ok(Object.keys(groundTokens(bad, 'instrument')).some((n) => !DUTY.test(n)));
});

function restoreRows(css) {
  const ins = groundTokens(css, 'instrument'), vel = groundTokens(css, 'vellum'), root = rootTokens(css);
  const rows = [];
  for (const n of Object.keys(ins)) {
    if (!(n in vel)) rows.push(`${n} is moved on the instrument and not restored on vellum`);
    else if (vel[n] !== root[n]) rows.push(`${n} is restored as ${vel[n]}, where :root says ${root[n]}`);
  }
  for (const n of Object.keys(vel)) if (!(n in ins)) rows.push(`${n} is restated on vellum and never moved`);
  return rows;
}

test('vellum restores every duty the instrument moves, to its :root value', () => {
  assert.deepEqual(restoreRows(CSS), []);
});

test('the restore reader sees a duty left dark and a duty restored to the wrong value', () => {
  const vellum = CSS.indexOf('[data-ground="vellum"]{');
  const cut = CSS.slice(0, vellum) + CSS.slice(vellum).replace('  --text-body:var(--ink);\n', '');
  assert.match(restoreRows(cut).join('\n'), /--text-body is moved on the instrument and not restored/);
  const wrong = CSS.slice(0, vellum) + CSS.slice(vellum).replace('  --text-body:var(--ink);', '  --text-body:var(--ink-2);');
  assert.match(restoreRows(wrong).join('\n'), /--text-body is restored as var\(--ink-2\)/);
});

const SURFACES = {
  vellum: ['--paper', '--paper-mat', '--paper-deep', '--paper-lit'],
  instrument: ['--coal', '--heavy', '--heavy-2', '--coal-deep'],
};
/* EVERY duty a word is set in, on both grounds (widened by Phase 17's audit). The first version
   held four on vellum and seven on the instrument, and a severity word, an accent and a refusal --
   which the rendered page sets as type hundreds of times -- were judged on neither. The rendered
   measurement found `--sev-serious` at 4.43 and `--sev-fatal` at 3.43 on the dark ground. */
const SEV = ['--sev-fatal', '--sev-serious', '--sev-minor', '--sev-cleared', '--sev-advisory', '--sev-info'];
const TEXT = {
  vellum: ['--text-body', '--text-secondary', '--text-tertiary', '--text-accent', '--link', '--text-on-paper',
    '--refusal-text', ...SEV],
  instrument: ['--text-body', '--text-secondary', '--text-tertiary', '--text-accent', '--link', '--refusal-text',
    '--mark-loading', ...SEV],
};

function contrastRows(css) {
  const rows = [];
  for (const g of GROUNDS) {
    for (const t of TEXT[g]) {
      const ink = groundValue(css, g, t);
      if (!/^#[0-9a-f]{6}$/i.test(ink || '')) { rows.push(`${t} on ${g} resolves to ${ink}, not an ink`); continue; }
      for (const s of SURFACES[g]) {
        const r = contrast(ink, groundValue(css, null, s));
        if (r < 4.5) rows.push(`${t} on ${g} reads ${r.toFixed(2)} : 1 on ${s}`);
      }
    }
  }
  return rows;
}

/* The one row the vellum ground already carried before the instrument existed, measured and
   recorded by `components/Eyebrow.jsx` since WP-14.8: --ink-2 reads 4.85 : 1 on --paper and 4.32
   on --paper-deep. It is held here by identity so it cannot grow a sibling. */
/* AND THE ROWS THE WIDENED TABLE FOUND ON VELLUM, every one older than Phase 17 and moved by none of
   it: a severity word, an accent, a refusal and the tertiary grey set in their pigments on paper.
   Three are `oq/two-inks-set-as-small-text-read-below-aa`'s (the refusal, the gilt, the green); the
   severity words and the tertiary grey are amended into it, dated, by Phase 17's audit. Held by
   identity, so none may grow a sibling and a fix must remove its row. */
const KNOWN = [
  '--text-secondary on vellum reads 4.32 : 1 on --paper-deep',
  '--refusal-text on vellum reads 3.11 : 1 on --paper-deep',
  '--refusal-text on vellum reads 3.29 : 1 on --paper-mat',
  '--refusal-text on vellum reads 3.50 : 1 on --paper',
  '--refusal-text on vellum reads 3.72 : 1 on --paper-lit',
  '--sev-advisory on vellum reads 4.32 : 1 on --paper-deep',
  '--sev-cleared on vellum reads 3.37 : 1 on --paper-deep',
  '--sev-cleared on vellum reads 3.55 : 1 on --paper-mat',
  '--sev-cleared on vellum reads 3.78 : 1 on --paper',
  '--sev-cleared on vellum reads 4.03 : 1 on --paper-lit',
  '--sev-fatal on vellum reads 3.11 : 1 on --paper-deep',
  '--sev-fatal on vellum reads 3.29 : 1 on --paper-mat',
  '--sev-fatal on vellum reads 3.50 : 1 on --paper',
  '--sev-fatal on vellum reads 3.72 : 1 on --paper-lit',
  '--sev-info on vellum reads 2.80 : 1 on --paper-deep',
  '--sev-info on vellum reads 2.96 : 1 on --paper-mat',
  '--sev-info on vellum reads 3.15 : 1 on --paper',
  '--sev-info on vellum reads 3.35 : 1 on --paper-lit',
  '--sev-minor on vellum reads 3.64 : 1 on --paper-deep',
  '--sev-minor on vellum reads 3.84 : 1 on --paper-mat',
  '--sev-minor on vellum reads 4.09 : 1 on --paper',
  '--sev-minor on vellum reads 4.35 : 1 on --paper-lit',
  '--sev-serious on vellum reads 2.41 : 1 on --paper-deep',
  '--sev-serious on vellum reads 2.54 : 1 on --paper-mat',
  '--sev-serious on vellum reads 2.71 : 1 on --paper',
  '--sev-serious on vellum reads 2.88 : 1 on --paper-lit',
  '--text-accent on vellum reads 3.64 : 1 on --paper-deep',
  '--text-accent on vellum reads 3.84 : 1 on --paper-mat',
  '--text-accent on vellum reads 4.09 : 1 on --paper',
  '--text-accent on vellum reads 4.35 : 1 on --paper-lit',
  '--text-tertiary on vellum reads 2.80 : 1 on --paper-deep',
  '--text-tertiary on vellum reads 2.96 : 1 on --paper-mat',
  '--text-tertiary on vellum reads 3.15 : 1 on --paper',
  '--text-tertiary on vellum reads 3.35 : 1 on --paper-lit',
];

test('every text duty reads 4.5 : 1 on every surface of its own ground', () => {
  assert.deepEqual([...contrastRows(CSS)].sort(), [...KNOWN].sort());
});

test('the contrast reader refuses a faint ink on the dark ground, which is the one this ground forbids', () => {
  const bad = CSS.replace('  --text-secondary:var(--ink-4);\n  --text-tertiary', '  --text-secondary:var(--ink-3);\n  --text-tertiary');
  assert.match(contrastRows(bad).join('\n'), /--text-secondary on instrument reads 3\.\d+ : 1 on --heavy/);
  // and --ink-4 on the dark is the measured 6.10 on coal and 5.30 on heavy, which pass
  assert.ok(contrast(groundValue(CSS, null, '--ink-4'), groundValue(CSS, null, '--heavy')) > 5.2);
});

test('stripping the ground blocks leaves the :root answer, and a ground block never leaks into it', () => {
  assert.equal(rootTokens(CSS)['--text-body'], 'var(--ink)');
  assert.equal(groundValue(CSS, 'instrument', '--text-body'), groundValue(CSS, null, '--paper'));
  assert.doesNotMatch(stripGrounds(CSS), /--surface-app:var\(--heavy\)/);
});

/* ── 4. the interface sets no colour primitive ─────────────────────────────────────────── */

const PRIM = /var\(\s*(--(?:paper(?:-deep|-mat|-lit)?|ink(?:-[234])?|rule(?:-soft)?|graphite|hair))\s*[,)]/g;

/* A DRAWING'S INK IS A PIGMENT, and these files draw: the plan sheet and its marks, the Round,
   the order plates, the atlas, the mark forms, the edge glyphs and the relaxation marker. Each is
   mounted on vellum, and a duty there would make a drawing's line follow the page round it. */
const DRAWING = [
  /^sheet\//, /^round\//, /^components\/AssemblyPlate\.jsx$/, /^surfaces\/phylo\/MapView\.jsx$/,
  /^marks\.js$/, /^components\/EdgeGlyph\.jsx$/, /^components\/RelaxationMarker\.jsx$/,
  // the chips' pigment table: a pale fill is the chip's own paper on either ground, by design
  /^chips\.js$/,
  // the Brief's site plate (Phase 17, WP-17.6)
  /^brief\/SiteDiagram\.jsx$/,
  // the export page's conventions schematic (Phase 17, WP-17.8)
  /^export\/ConventionsPlate\.jsx$/,
  // the dossier's period bar (Phase 17, WP-17.9)
  /^dossier\/PeriodBar\.jsx$/,
];

/* What remains, BY FILE AND COUNT, measured when WP-17.0 landed. A count may only fall, and a file
   at zero leaves the table in the same commit. The table is EMPTY since WP-17.13: the last file,
   `surfaces/Proportions.jsx`, moved its order plate onto the drawing duties (`--draw-*`) and its
   page onto the text and border duties, and a new primitive anywhere outside DRAWING fails. */
const REMAINING = {};

function primitiveRows(dir = SRC, out = {}) {
  for (const f of readdirSync(dir).sort()) {
    const p = join(dir, f);
    if (statSync(p).isDirectory()) { primitiveRows(p, out); continue; }
    if (!/\.(jsx|js)$/.test(f) || /\.test\./.test(f)) continue;
    const rel = relative(SRC, p);
    if (DRAWING.some((r) => r.test(rel))) continue;
    // THE SHARED LEXER, NOT A REGEX (found at WP-17.14): `/\*[\s\S]*?\*\//` read Transcription's
    // `accept="image/*"` as opening a comment and blanked three primitives the ratchet never saw --
    // the trap WP-14.33's audit recorded for the copy scanners, met again in a guard written after it.
    const live = stripComments(readFileSync(p, 'utf8'));
    const n = [...live.matchAll(PRIM)].length;
    if (n) out[rel] = n;
  }
  return out;
}

test('no interface file sets a colour primitive beyond the table, and the table only shrinks', () => {
  const now = primitiveRows();
  const over = Object.entries(now).filter(([f, n]) => n > (REMAINING[f] || 0)).map(([f, n]) => `${f}: ${n}`);
  assert.deepEqual(over, [], 'a component sets --ink, --paper or --rule where a duty would follow the ground');
  const stale = Object.entries(REMAINING).filter(([f, n]) => (now[f] || 0) < n).map(([f, n]) => `${f}: ${now[f] || 0} < ${n}`);
  assert.deepEqual(stale, [], 'a file fell below its row: lower the table in the same commit');
});

/* AND THE STYLESHEET'S OWN CLASS RULES (found by looking at the first dark render: the page head's
   sentence was drawn in --ink on --heavy, because `.tdl-page-head-what` named the pigment and the
   scan above reads only JS). A rule outside the :root and ground blocks names a duty; the ones
   that are paper by construction -- the vellum box, the plate, the body before a ground is set, and
   the Term's popover card -- are named here with that reason. */
const PAPER_RULES = ['.tdl-vellum', '.tdl-plate', 'body', 'main[data-ground="vellum"]'];
/* A FAMILY whose every rule lives inside its paper card: the Term's popover. Matched by prefix on
   purpose, and only these. The others match a selector EXACTLY (Phase 17's audit): by prefix,
   `.tdl-plate` exempted `.tdl-plate-caption`, which sits below the plate, on the instrument, and a
   mutation setting that caption in --ink-2 stayed green. */
const PAPER_FAMILIES = ['.tdl-term-pop'];
const esc = (x) => x.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
export const isPaperRule = (sel) => PAPER_RULES.some((p) => new RegExp('^' + esc(p) + '(?![\\w-])').test(sel))
  || PAPER_FAMILIES.some((f) => sel === f || sel.startsWith(f + '-'));
function cssRuleRows(css) {
  const live = css.replace(/\/\*[\s\S]*?\*\//g, '');
  const rows = [];
  for (const m of live.matchAll(/([^{}]+)\{([^{}]*)\}/g)) {
    const sel = m[1].trim();
    // EXACT, not by prefix (the second audit of Phase 17): `[data-ground="instrument"] .x{color:var(--brick)}`
    // began with a ground block's name and was exempt, and so was `.x` in a list that began with a paper rule
    if (/^(:root|\[data-ground="(instrument|vellum)"\])$/.test(sel)) continue;
    if (sel.split(',').every((part) => isPaperRule(part.trim()))) continue;
    // and a hue set as a word, which the instrument cannot read (Phase 17's audit)
    const hue = [...m[2].matchAll(/(?<![\w-])color:\s*var\(--(?:gilt(?:-deep)?|green(?:-deep)?|brick|salmon(?:-deep)?|sepia|refusal)\)/g)].length;
    const n = [...m[2].matchAll(PRIM)].length + hue;
    if (n) rows.push(`${sel.replace(/\s+/g, ' ').slice(0, 60)}: ${n}`);
  }
  return rows;
}

test('no class rule in the stylesheet names a colour primitive, but the paper ones', () => {
  assert.deepEqual(cssRuleRows(CSS), []);
  assert.deepEqual(cssRuleRows('.x{color:var(--ink-2)}'), ['.x: 1'], 'the reader sees a pigment in a rule');
  assert.deepEqual(cssRuleRows('.x{color:var(--gilt-deep)}'), ['.x: 1'], 'and a hue set as a word');
  assert.deepEqual(cssRuleRows('[data-ground="instrument"] .x{color:var(--brick)}').length, 1, 'a rule under a ground is not the ground block');
  assert.deepEqual(cssRuleRows('.tdl-plate, .x{color:var(--ink-2)}').length, 1, 'a list is paper only if every part is');
  assert.deepEqual(cssRuleRows('.x{border-color:var(--gilt-deep);color:var(--refusal-text)}'), [], 'but not an edge, or a duty');
  assert.deepEqual(cssRuleRows('.tdl-plate-caption{color:var(--ink-2)}'), ['.tdl-plate-caption: 1'],
    'a rule whose name begins with a paper one is not paper: the caption stands on the instrument');
  assert.deepEqual(cssRuleRows('.tdl-plate{color:var(--ink)} .tdl-plate svg{fill:var(--ink)} .tdl-term-pop-word{color:var(--ink)}'), [],
    'the paper rules themselves, a descendant of one, and the popover family are paper');
});

test('the primitive reader counts a primitive in code and none in a comment', () => {
  // the reader the ratchet uses, not a regex beside it (Phase 17's audit: this twin drove the old one)
  const s = "<input accept=\"image/*\" style={{ color: 'var(--ink-2)', background: 'var(--paper, #fff)' }} /> {/* var(--rule) */}";
  assert.equal([...stripComments(s).matchAll(PRIM)].length, 2);
  assert.equal([..."var(--ink-2-x)".matchAll(PRIM)].length, 0, 'a longer name is not the primitive');
});

test('every surface the width table knows has a ground, and the table names no other', async () => {
  const { SURFACE_WIDTH } = await import('./state/layout.js');
  const { SURFACE_GROUND, SHELL_GROUND, groundOf } = await import('./grounds.js');
  assert.deepEqual(Object.keys(SURFACE_GROUND).sort(), Object.keys(SURFACE_WIDTH).sort());
  for (const g of [SHELL_GROUND, ...Object.values(SURFACE_GROUND)]) assert.ok(GROUNDS.includes(g), g);
  assert.equal(groundOf('no-such-surface'), 'vellum', 'a page nobody moved is a page nobody redrew');
});

test('App marks the shell and each <main> from the one table', () => {
  const app = readFileSync(join(SRC, 'App.jsx'), 'utf8');
  assert.match(app, /root\.setAttribute\('data-ground', SHELL_GROUND\)/);
  assert.match(app, /<main data-ground=\{groundOf\(/);
});

/* ── 5. every surface stands on the instrument (WP-17.14), and nothing moves one back unsaid ── */
test('every surface is on the instrument since WP-17.14', async () => {
  const { SURFACE_GROUND, SHELL_GROUND } = await import('./grounds.js');
  assert.equal(SHELL_GROUND, 'instrument');
  assert.deepEqual(Object.entries(SURFACE_GROUND).filter(([, g]) => g !== 'instrument'), [],
    'a surface moved back to vellum is a decision about the whole page: say so here, by name');
});

/* ── 6. A WORD IS SET IN A DUTY, NEVER A PIGMENT (Phase 17's audit) ───────────────────────────
   The rendered page measured 1,000-odd words below 4.5 : 1 on the instrument while every token
   above passed: a CSS `color:` naming a pigment (`--gilt-deep`, `--brick`, `--green-deep`) or a
   neutral primitive bypasses the ground, and the DRAWING exemption let HTML captions in drawing
   files set `--ink` on a dark page. `color` is type in every file, drawing files included; a
   drawing's ink is its `fill` and `stroke`. */
const TYPE_PIGMENT = /(?<![\w-])color:\s*([^,}\n]*)/g;
const RAW = /var\(\s*--(?:paper(?:-deep|-mat|-lit)?|ink(?:-[234])?|rule(?:-soft)?|graphite|hair|coal|heavy|gilt(?:-deep)?|green(?:-deep|-pale)?|brick|salmon(?:-deep)?|sepia(?:-pale)?|blue(?:-deep|-pale)?|violet|refusal)\s*[,)]/;
export function typePigmentRows(src) {
  const rows = [];
  for (const m of stripComments(src).matchAll(TYPE_PIGMENT)) if (RAW.test(m[1])) rows.push(m[1].trim().slice(0, 50));
  return rows;
}
function typeRowsIn(dir = SRC, out = {}) {
  for (const f of readdirSync(dir).sort()) {
    const p = join(dir, f);
    if (statSync(p).isDirectory()) { typeRowsIn(p, out); continue; }
    if (!/\.(jsx|js)$/.test(f) || /\.test\./.test(f)) continue;
    const rows = typePigmentRows(readFileSync(p, 'utf8'));
    if (rows.length) out[relative(SRC, p)] = rows;
  }
  return out;
}
test('no file sets a word in a pigment: a word takes a duty that follows its ground', () => {
  assert.deepEqual(typeRowsIn(), {});
});
test('the type reader sees a pigment word, a primitive word and a ternary, and passes a duty and a fill', () => {
  assert.deepEqual(typePigmentRows("style={{ color: 'var(--gilt-deep)' }}"), ["'var(--gilt-deep)'"]);
  assert.equal(typePigmentRows("style={{ color: on ? 'var(--text-accent)' : 'var(--ink-2)' }}").length, 1);
  assert.deepEqual(typePigmentRows("style={{ color: 'var(--text-body)', fill: 'var(--ink)', borderColor: 'var(--brick)' }}"), []);
  assert.deepEqual(typePigmentRows("style={{ color: 'var(--refusal-text)' }}"), [], 'a duty whose name begins with a pigment is a duty');
});

/* ── 7. A WORD ON ITS OWN SEVERITY FIELD READS (Phase 17's audit) ─────────────────────────────
   A finding row is its severity's field washed over the panel, and the rendered page measured the
   minor word at 3.89 on its own row and the secondary grey at 4.47. Each severity word, and the
   body and secondary text set beside it, read 4.5 : 1 on every severity field over every surface of
   the instrument. */
function over(rgba, hex) {
  const m = /rgba\((\d+),\s*(\d+),\s*(\d+),\s*([.\d]+)\)/.exec(rgba || '');
  if (!m) return null;
  const a = Number(m[4]);
  const b = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16));
  return '#' + [1, 2, 3].map((i, k) => Math.round(a * Number(m[i]) + (1 - a) * b[k]).toString(16).padStart(2, '0')).join('');
}
export function fieldRows(css) {
  const rows = [];
  for (const sev of ['fatal', 'serious', 'minor', 'cleared']) {
    const field = groundValue(css, 'instrument', `--sev-${sev}-field`);
    for (const s of SURFACES.instrument) {
      const bg = over(field, groundValue(css, null, s));
      if (!bg) { rows.push(`--sev-${sev}-field is not a wash`); continue; }
      for (const t of [`--sev-${sev}`, '--text-body', '--text-secondary']) {
        const r = contrast(groundValue(css, 'instrument', t), bg);
        if (r < 4.5) rows.push(`${t} reads ${r.toFixed(2)} : 1 on the ${sev} field over ${s}`);
      }
    }
  }
  return rows;
}
test('a severity word, and the text beside it, reads on its own field on the instrument', () => {
  assert.deepEqual(fieldRows(CSS), []);
  // WP-17.0's own value, gilt, which reads 4.57 on --heavy and 3.99 on its field
  const before = CSS.replace('  --sev-minor:var(--gilt-lit);', '  --sev-minor:var(--gilt);');
  assert.notEqual(before, CSS, 'the instrument block states the minor word');
  assert.ok(fieldRows(before).some((r) => r.startsWith('--sev-minor reads')), 'the plain gilt, on its own row, fails');
});

/* ── 8. EVERY TOKEN A WORD IS SET IN READS ON THE INSTRUMENT, or says why not (Phase 17's audit) ──
   Section 6 refuses a raw pigment as a word; this reads every token a `color:` names, ladders and
   duties alike, at its instrument value. The rendered page found `--bind-forbidden` (brick, 3.43)
   set as the cascade's ban mark after the pigment sweep: a ladder token resolved at :root follows no
   ground. The exceptions are named by identity, each with its reason, and may only shrink. */
const COLOR_EXCEPT = {
  '--text-disabled': 'an inactive control: WCAG 1.4.3 does not apply to one',
  '--text-on-gilt': 'set on its own gilt fill, 5.26 : 1 on either ground',
  '--surface-panel': 'Gate.jsx sets it on its own inverted fill, the body text duty',
  '--fix-right': 'FaultCard.jsx, on the fault card, which is vellum: oq/two-inks-set-as-small-text-read-below-aa',
};
function colorTokenRows() {
  const toks = new Map();
  const walkTok = (d) => {
    for (const f of readdirSync(d).sort()) {
      const p = join(d, f);
      if (statSync(p).isDirectory()) { walkTok(p); continue; }
      if (!/\.(jsx|js)$/.test(f) || /\.test\./.test(f)) continue;
      for (const m of stripComments(readFileSync(p, 'utf8')).matchAll(TYPE_PIGMENT)) {
        for (const t of m[1].matchAll(/var\(--([a-z0-9-]+)\)/g)) toks.set('--' + t[1], relative(SRC, p));
      }
    }
  };
  walkTok(SRC);
  const rows = [];
  for (const [t] of [...toks].sort()) {
    const v = groundValue(CSS, 'instrument', t);
    if (!/^#[0-9a-f]{6}$/i.test(v || '')) continue;   // a wash or a gradient is not an ink
    const r = Math.min(...SURFACES.instrument.map((s) => contrast(v, groundValue(CSS, null, s))));
    if (r < 4.5) rows.push(t);
  }
  return rows;
}
test('every token a word is set in reads 4.5 : 1 on the instrument, but the named exceptions', () => {
  assert.deepEqual(colorTokenRows(), Object.keys(COLOR_EXCEPT).sort());
});

/* ── 9. AN ELEMENT THAT PAINTS PAPER SAYS IT IS VELLUM (the second audit of Phase 17) ───────────
   The atlas's legend and hover card painted `--paper` on the instrument without marking their
   ground, so the text duties inside them took the instrument's light values: 2.26 : 1, and the
   coastline-failure line about 1 : 1. A drawing (`svg`) is exempt, because its words are `fill`s. */
import { elements } from './sourceReader.mjs';
/* AND A CLASS WHOSE RULE PAINTS PAPER counts as painting it (the second audit: the definition
   popover, `.tdl-term-pop`, paints paper in the stylesheet and carried no ground mark, so its links
   took the instrument's `--link`, which is paper: 1.00 : 1 on every Term on every page). `tdl-vellum`
   and `tdl-plate` are not marks on their own: an element carrying one marks its ground as well. */
export function paperClasses(css) {
  const out = new Set();
  for (const m of css.replace(/\/\*[\s\S]*?\*\//g, '').matchAll(/([^{}]+)\{([^{}]*)\}/g)) {
    if (!/background(?:-color)?:\s*var\(--paper/.test(m[2])) continue;
    for (const sel of m[1].split(',')) {
      const c = /^\s*\.([A-Za-z0-9_-]+)\s*$/.exec(sel);
      if (c) out.add(c[1]);
    }
  }
  return out;
}
const PAPER_CLASSES = paperClasses(CSS);
export function unmarkedPaper(src, classes = PAPER_CLASSES) {
  return elements(src).filter((e) => {
    if (e.name === 'svg') return false;
    const head = e.head || '';
    const cls = (/className=["'`{]([^"'`}]*)/.exec(head) || [])[1] || '';
    const paints = /background(?:Color)?:\s*['"`]?var\(--paper/.test(head)
      || cls.split(/\s+/).some((c) => classes.has(c));
    return paints && !/data-ground=/.test(head);
  }).map((e) => e.name);
}
test('every HTML element that paints paper marks itself vellum', () => {
  const out = {};
  const walkP = (d) => {
    for (const f of readdirSync(d).sort()) {
      const p = join(d, f);
      if (statSync(p).isDirectory()) { walkP(p); continue; }
      if (!/\.(jsx|js)$/.test(f) || /\.test\./.test(f)) continue;
      const rows = unmarkedPaper(readFileSync(p, 'utf8'));
      if (rows.length) out[relative(SRC, p)] = rows;
    }
  };
  walkP(SRC);
  assert.deepEqual(out, {});
  assert.deepEqual(unmarkedPaper("<div style={{ background: 'var(--paper)' }}>x</div>"), ['div']);
  assert.deepEqual(unmarkedPaper("<div data-ground=\"vellum\" style={{ background: 'var(--paper)' }}>x</div><svg style={{ background: 'var(--paper-lit)' }} />"), []);
  assert.ok(PAPER_CLASSES.has('tdl-term-pop'), 'the premise: the popover paints paper in the stylesheet');
  assert.deepEqual(unmarkedPaper('<span className="tdl-term-pop">x</span>'), ['span'], 'a paper class unmarked is caught');
});

/* ── 10. EVERY LADDER DUTY READS ON THE INSTRUMENT (the second audit of Phase 17) ─────────────────
   The affinity ladder's words (`VariantPill`, `color: colour` off a map, which §8's scan of literal
   tokens cannot see), the binding bars' fills and the kit-carrying edges' strokes were set in ladder
   tokens resolved at :root -- gilt-deep, green-deep, brick and `--ink`, 1.26 : 1 at worst. A ladder
   token is a word or a mark wherever it is used, so each reads 4.5 : 1 on every dark surface. */
test('every binding, variant, affinity, kind, edge and judgment duty reads 4.5 : 1 on the instrument', () => {
  const rows = [];
  for (const [n, v] of Object.entries(groundTokens(CSS, 'instrument'))) {
    if (!/^--(bind|var|aff|kind|edge|judge)-/.test(n)) continue;
    const ink = groundValue(CSS, 'instrument', n);
    if (!/^#[0-9a-f]{6}$/i.test(ink || '')) continue;      // a field wash or a width is not an ink
    for (const s of SURFACES.instrument) {
      const r = contrast(ink, groundValue(CSS, null, s));
      if (r < 4.5) rows.push(`${n} (${v}) reads ${r.toFixed(2)} on ${s}`);
    }
  }
  assert.deepEqual(rows, []);
  const ladders = Object.keys(groundTokens(CSS, 'instrument')).filter((n) => /^--(aff|bind|var|kind|edge)-/.test(n));
  assert.ok(ladders.includes('--aff-common') && ladders.includes('--bind-specified') && ladders.includes('--edge-carries'),
    'the premise: the ladders are rebound on the instrument at all');
});

/* ── 11. A WORD'S COLOUR NAMED THROUGH A VARIABLE OR A MAP (the second audit of Phase 17) ─────────
   §6 reads literals inside a `color:`; `color: tone` and `color: INK[k]` hid brick and gilt-deep
   words on the dark (RevisionPanel's verdict, the affinity ladder's map). Every identifier a `color:`
   names, or the map it indexes, is followed to its `const` in the same file, and that definition is
   held to §6's rule. */
export function namedPigmentRows(src) {
  const live = stripComments(src);
  const rows = [];
  for (const m of live.matchAll(/(?<![\w-])color:\s*\(?\s*([A-Za-z_$][\w$]*)/g)) {
    const name = m[1];
    if (/^(on|off|true|false|null|undefined)$/.test(name)) continue;
    const def = new RegExp(`(?:const|let|var)\\s+${name.replace(/\$/g, '\\$')}\\s*=\\s*([\\s\\S]*?)(?:;\\n|\\n\\n)`).exec(live);
    if (def && RAW.test(def[1])) rows.push(name);
  }
  return [...new Set(rows)];
}
test('a colour named through a variable or a map is a duty too', () => {
  const out = {};
  const walkN = (d) => {
    for (const f of readdirSync(d).sort()) {
      const p = join(d, f);
      if (statSync(p).isDirectory()) { walkN(p); continue; }
      if (!/\.(jsx|js)$/.test(f) || /\.test\./.test(f)) continue;
      const rel = relative(SRC, p);
      if (DRAWING.some((r) => r.test(rel))) continue;   // a drawing's fills and strokes are pigments
      const rows = namedPigmentRows(readFileSync(p, 'utf8'));
      if (rows.length) out[rel] = rows;
    }
  };
  walkN(SRC);
  // named by identity, each measured, and the list only shrinks
  const NAMED = {
    // the decision log is a vellum receipt; its sepia and gilt kinds are paper rows that predate the
    // phase (oq/two-inks-set-as-small-text-read-below-aa), and its judgment and refusal are duties
    'surfaces/CandidateSet.jsx': ['TONE'],
    // the bench's disclosure list is on the instrument, where its `copper`, --sepia, reads 5.00 : 1
    'surfaces/PlanWorkbench.jsx': ['TONE'],
  };
  assert.deepEqual(out, NAMED);
  assert.deepEqual(namedPigmentRows("const tone = x ? 'var(--brick)' : 'var(--text-body)';\nconst s = { color: tone };\n"), ['tone']);
  assert.deepEqual(namedPigmentRows("const INK = { a: 'var(--gilt-deep)' };\nconst s = { color: INK[k] };\n"), ['INK']);
  assert.deepEqual(namedPigmentRows("const tone = 'var(--refusal-text)';\nconst s = { color: tone };\n"), []);
});

/* ── 12. A MARK IS A GRAPHIC, AND A GRAPHIC READS 3 : 1 (the second audit of Phase 17) ───────────
   The mark and judgment duties draw glyphs, rings and strokes, so WCAG 1.4.11's 3 : 1 is their
   floor. Set `--mark-yours-to-judge` to gilt-deep (2.93) or `--judge-unjudged` to coal and nothing
   above failed. A hatch or a field is not one ink and is not judged here. */
export function markRows(css) {
  const rows = [];
  for (const n of Object.keys({ ...rootTokens(css), ...groundTokens(css, 'instrument') })) {
    if (!/^--(mark|judge)-/.test(n)) continue;
    const ink = groundValue(css, 'instrument', n);
    if (!/^#[0-9a-f]{6}$/i.test(ink || '')) continue;
    for (const s of SURFACES.instrument) {
      const r = contrast(ink, groundValue(css, null, s));
      if (r < 3) rows.push(`${n} reads ${r.toFixed(2)} on ${s}`);
    }
  }
  return rows;
}
test('every mark and judgment ink reads 3 : 1 on the instrument', () => {
  assert.deepEqual(markRows(CSS), []);
  const dim = CSS.replace('  --mark-yours-to-judge:var(--gilt);', '  --mark-yours-to-judge:var(--gilt-deep);');
  assert.notEqual(dim, CSS, 'the instrument block states the mark');
  assert.ok(markRows(dim).some((r) => r.startsWith('--mark-yours-to-judge')), 'gilt-deep on the dark is refused');
});
