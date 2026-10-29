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

const DUTY = /^--(surface|text|border|link|sev|refusal-text|receipt|judge|mark)(-|$)/;

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
const TEXT = {
  vellum: ['--text-body', '--text-secondary', '--link', '--text-on-paper'],
  instrument: ['--text-body', '--text-secondary', '--text-tertiary', '--text-accent', '--link', '--refusal-text', '--mark-loading'],
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
const KNOWN = ['--text-secondary on vellum reads 4.32 : 1 on --paper-deep'];

test('every text duty reads 4.5 : 1 on every surface of its own ground', () => {
  assert.deepEqual(contrastRows(CSS), KNOWN);
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
   scan above reads only JS). A rule outside the :root and ground blocks names a duty; the four
   that are paper by construction -- the vellum box, the plate, the body before a ground is set, and
   the Term's popover card -- are named here with that reason. */
const PAPER_RULES = ['.tdl-vellum', '.tdl-plate', 'body', '.tdl-term-pop', 'main[data-ground="vellum"]'];
function cssRuleRows(css) {
  const live = css.replace(/\/\*[\s\S]*?\*\//g, '');
  const rows = [];
  for (const m of live.matchAll(/([^{}]+)\{([^{}]*)\}/g)) {
    const sel = m[1].trim();
    if (sel.startsWith(':root') || sel.startsWith('[data-ground') || PAPER_RULES.some((p) => sel.startsWith(p))) continue;
    const n = [...m[2].matchAll(PRIM)].length;
    if (n) rows.push(`${sel.replace(/\s+/g, ' ').slice(0, 60)}: ${n}`);
  }
  return rows;
}

test('no class rule in the stylesheet names a colour primitive, but the paper ones', () => {
  assert.deepEqual(cssRuleRows(CSS), []);
  assert.deepEqual(cssRuleRows('.x{color:var(--ink-2)}'), ['.x: 1'], 'the reader sees a pigment in a rule');
});

test('the primitive reader counts a primitive in code and none in a comment', () => {
  const s = "style={{ color: 'var(--ink-2)', background: 'var(--paper, #fff)' }} /* var(--rule) */";
  assert.equal([...s.replace(/\/\*[\s\S]*?\*\//g, '').matchAll(PRIM)].length, 2);
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
