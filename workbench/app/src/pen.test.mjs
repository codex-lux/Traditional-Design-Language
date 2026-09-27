/* The pen ladder is the grammar, so it is not allowed to be re-spelled per mark.

   `Sheet.jsx` carried nineteen inline stroke widths and not one of the standard's five named
   weights. This reads the source and holds it to `pen.js` — the same shape of guard
   `tests/test_parti_confinement.py` uses to stop a fourth copy of a path join appearing, and
   the same reason: a value two places can set is a value two places can disagree about.

   It reads SOURCE rather than a rendered DOM on purpose. The rendered sheet resolves every
   `var()` to a number, so a DOM check would see 3px whether it came from the ladder or from a
   literal that happened to match — which is exactly the kind of guard that passes on the bug. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const SHEET = join(HERE, 'sheet', 'Sheet.jsx');

/* A mark inside a <pattern> is exempt, and the exemption is not a loophole: a pattern's
   contents are in PATTERN units, so a pixel weight from the ladder would be meaningless
   there. `e2e/walk.mjs`'s pen check already makes exactly this exemption for exactly this
   reason (`if (el.closest('pattern')) return;`), and it is spelled the same way here so the
   two cannot drift into disagreeing about what a pattern is. */
function outsidePatterns(src) {
  return src.replace(/<pattern[\s\S]*?<\/pattern>/g, m => m.replace(/strokeWidth/g, 'inPattern'));
}

test('the sheet states no stroke width of its own', () => {
  const src = outsidePatterns(readFileSync(SHEET, 'utf8'));
  // a literal is `strokeWidth="1.4"` or `strokeWidth={1.4}`; the ladder is `style={PEN.x}`
  const literals = [...src.matchAll(/strokeWidth\s*=\s*[{"']\s*\.?\d/g)].map(m => {
    const at = src.slice(0, m.index).split('\n').length;
    return `${at}: ${src.slice(m.index, m.index + 40).split('\n')[0]}`;
  });
  assert.deepEqual(literals, [],
    'stroke widths belong to pen.js and Graphic Standard No. 1\'s five weights:\n  '
    + literals.join('\n  '));
});

test('the pattern exemption is exactly one mark, and it is not a way in', () => {
  const src = readFileSync(SHEET, 'utf8');
  const inside = [...src.matchAll(/<pattern[\s\S]*?<\/pattern>/g)]
    .flatMap(m => [...m[0].matchAll(/strokeWidth\s*=\s*[{"']\s*\.?\d/g)]);
  assert.equal(inside.length, 1,
    `${inside.length} stroke widths inside <pattern> elements -- the exemption is for the `
    + 'ghost hatch, whose units are the pattern\'s, and a second one wants a reason');
});

test('and this guard is reading the file it thinks it is', () => {
  const src = readFileSync(SHEET, 'utf8');
  assert.ok(src.length > 5000, 'Sheet.jsx has moved -- this guard is reading air');
  assert.ok(/from '\.\/pen\.js'/.test(src), 'Sheet.jsx does not import the pen at all');
  // the detector must be able to see a literal: prove it on a synthetic one rather than
  // trusting that an empty result means a clean file
  const probe = 'x <line strokeWidth="1.4" />';
  assert.equal([...probe.matchAll(/strokeWidth\s*=\s*[{"']\s*\.?\d/g)].length, 1,
    'the literal detector matches nothing, so its empty result above means nothing');
});

/* WP-14.4: THE TWO PLAN SHEETS POCHE ONE RECORD'S WALLS IN ONE INK. `build/sheet_style.py::POCHE`
   is the printed plate's; this reads it and holds the bench's to it, token for token, because the
   bench drew partitions in `--sepia-pale` for eleven packages after the plate had measured that
   ink as a hollow tube at plan scale and moved to `--sepia`. */
test("the bench's poche is the printed plate's, token for token", async () => {
  const { readFileSync } = await import('node:fs');
  const { fileURLToPath } = await import('node:url');
  const { dirname, join } = await import('node:path');
  const { POCHE } = await import('./sheet/pen.js');
  const here = dirname(fileURLToPath(import.meta.url));
  const py = readFileSync(join(here, '..', '..', '..', 'build', 'sheet_style.py'), 'utf8');
  const block = /POCHE = \{([\s\S]*?)\n\}/.exec(py);
  assert.ok(block, 'the premise: sheet_style.py states a POCHE table');
  const tokenOf = (kind) => {
    const m = new RegExp(`"${kind}":\\s*LIGHT\\["([a-z_]+)"\\]`).exec(block[1]);
    assert.ok(m, `the premise: sheet_style.POCHE states a ${kind} ink`);
    return `var(--${m[1].replace(/_/g, '-')})`;
  };
  assert.equal(POCHE.partition.fill, tokenOf('partition'));
  // The masonry token is spelled through its DUTY name on the bench and its COLOUR on the plate,
  // so the duty name is resolved through the standard's own declaration before the two are
  // compared. The first version asserted each side against its own literal -- `var(--poche-masonry)`
  // and `var(--salmon)` -- and related them by nothing, so re-pointing `--poche-masonry` at another
  // ink in tokens.css left it green while the two sheets drew two colours (WP-14.6).
  const css = readFileSync(join(here, 'theme', 'tokens.css'), 'utf8');
  const decls = [...css.matchAll(/--poche-masonry\s*:\s*([^;]+);/g)].map(m => m[1].trim());
  assert.equal(decls.length, 1, `the premise: tokens.css declares --poche-masonry once (${decls.length})`);
  const resolve = (fill) => {
    const name = /^var\((--[a-z-]+)\)$/.exec(fill);
    assert.ok(name, `the bench's masonry fill is not a token: ${fill}`);
    return name[1] === '--poche-masonry' ? decls[0] : fill;
  };
  assert.equal(resolve(POCHE.masonry.fill), tokenOf('masonry'));
});
