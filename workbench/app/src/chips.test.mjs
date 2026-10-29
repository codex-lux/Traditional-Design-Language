/* THE CHIPS READ ON BOTH GROUNDS (Phase 17, WP-17.1).

   `chips.js` holds four ladders. Three properties, each with a driven twin:

   1. EVERY RUNG OF EVERY LADDER HAS ITS GLOSSARY WORD. A source kind is a `param-kind-*` record, a
      binding a `binding-*`, a variant's rank a `variant-status-*`, and the three verdict
      severities `severity-*`. A rung with no record has no word a reader can look up.
   2. EVERY CHIP'S WORD READS 4.5 : 1, on the chip's own fill where it has one and on every
      surface of both grounds where it has none.
   3. A STRONG PIGMENT IS NEVER THE WORD'S GROUND. Where the board fills a chip in --green-deep,
      --green or --brick, the pigment is a swatch and the word sits beside it. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { join } from 'node:path';
import { LADDERS, chipOf, chipStyle } from './chips.js';
import { contrast, groundValue } from './grounds.js';

const SRC = fileURLToPath(new URL('./', import.meta.url));
const CSS = readFileSync(join(SRC, 'theme', 'tokens.css'), 'utf8');
const GLOSSARY = fileURLToPath(new URL('../../../glossary/', import.meta.url));
const IDS = new Set(readdirSync(GLOSSARY).filter((f) => f.endsWith('.json')).map((f) => f.slice(0, -5)));

const RECORD = { source: 'param-kind-', binding: 'binding-', variant: 'variant-status-', severity: 'severity-' };
const SURFACES = { vellum: ['--paper', '--paper-mat', '--paper-lit'], instrument: ['--coal', '--heavy', '--heavy-2'] };
const STRONG = new Set(['--green-deep', '--green', '--brick']);

const tokenOf = (v) => (/^var\((--[a-z0-9-]+)\)$/i.exec(v || '') || [])[1];

function wordRows(ladders = LADDERS, css = CSS) {
  const rows = [];
  for (const [ladder, rungs] of Object.entries(ladders)) {
    for (const [rung, look] of Object.entries(rungs)) {
      for (const g of ['vellum', 'instrument']) {
        const ink = groundValue(css, g, tokenOf(look.ink));
        const grounds = look.fill ? [tokenOf(look.fill)] : SURFACES[g];
        for (const s of grounds) {
          const r = contrast(ink, groundValue(css, g, s));
          if (r < 4.5) rows.push(`${ladder}.${rung} on ${g}: its word reads ${r.toFixed(2)} : 1 on ${s}`);
        }
      }
    }
  }
  return rows;
}

test('every rung of a ladder with a vocabulary has its glossary word', () => {
  const missing = [];
  for (const [ladder, rungs] of Object.entries(LADDERS)) {
    for (const rung of Object.keys(rungs)) {
      // advisory and info are a finding's weight with no record yet: the severity family holds
      // the three verdicts, and a non-verdict's chip prints the finding's own word
      if (ladder === 'severity' && (rung === 'advisory' || rung === 'info')) continue;
      if (!IDS.has(RECORD[ladder] + rung)) missing.push(`${ladder}.${rung}`);
    }
  }
  assert.deepEqual(missing, []);
});

test('every chip’s word reads 4.5 : 1 on its own fill, or on every surface of both grounds', () => {
  assert.deepEqual(wordRows(), []);
});

test('the word reader convicts a word set in paper on a green-deep fill', () => {
  const bad = { variant: { canonical: { ...LADDERS.variant.canonical, fill: 'var(--green-deep)', ink: 'var(--paper)' } } };
  assert.match(wordRows(bad).join('\n'), /variant\.canonical on vellum: its word reads 3\.78/);
});

test('a strong pigment is a swatch beside the word and never the word’s ground', () => {
  for (const [ladder, rungs] of Object.entries(LADDERS)) {
    for (const [rung, look] of Object.entries(rungs)) {
      assert.ok(!STRONG.has(tokenOf(look.fill)), `${ladder}.${rung} fills in ${look.fill}`);
    }
  }
  assert.ok(chipStyle(chipOf('variant', 'canonical')).swatch, 'canonical carries its swatch');
  assert.equal(chipOf('variant', 'no-such-rung'), null, 'an unknown rung is the bare word, not another rung');
});


/* Phase 17's audit: only canonical's swatch was held, so a forbidden binding drawn unstruck stayed
   green. A ban is the ladder's loudest rung on both ladders, and the two forms are pinned by rung. */
test('a forbidden rung is struck through on both ladders, and the forbidden variant is hatched', async () => {
  const { BINDING, VARIANT } = await import('./chips.js');
  assert.equal(BINDING.forbidden.struck, true);
  assert.equal(VARIANT.forbidden.struck, true);
  assert.ok(VARIANT.forbidden.hatch, 'the forbidden variant carries the forbidden hatch');
  for (const [k, look] of Object.entries({ ...BINDING, ...VARIANT })) {
    if (k !== 'forbidden') assert.equal(look.struck, false, k);
  }
});
