/* THE NOTATION PORT, HELD TO THE ENGINE FROM BOTH SIDES (WP-14.6).

   The table between the two marker comments below is read by TWO readers and must stay a JSON
   array literal — double quotes, no trailing comma, no comment inside it:

   - this file, which asks `feetInches16` for each string; and
   - `tests/test_fmt_parity.py`, which extracts the same text with `json.loads` and asks
     `build/proportion_engine.py::_fmt_in` for each string.

   So a vector here is a claim about BOTH functions, and neither side's author can make it true by
   editing the other side. Numbers the parity test must read as Python FLOATS are written with an
   exponent (`1e+20`): `json.loads` reads `100000000000000000000` as an int, and `_fmt_in` of an int
   takes Python's exact integer divmod, which is a different function past 2**53.

   Every row was produced by `_fmt_in` itself, and the four behaviours a natural port gets wrong
   each have rows that fail it: round-half-UP fails 0.03125, 0.15625 and 0.40625; a carry that
   stops at the inch fails 23.99, 11.97, 11.96875 and 35.97 (and a carry into the foot taken too
   early fails 0.96875, which is an inch); a carry tested on the sixteenth rather than on the inch
   fails -1e-20 and -5e-324, whose remainder is exactly 12.0 with no sixteenth at all; a truncating
   divmod fails every negative row; and `String()` in place of the exact integer fails 1e+20. The
   parity test's sweep is the wider net; these are the cases a reader can see.

   THE CARRY ROWS CHANGED AT WP-14.20, ON BOTH SIDES IN ONE COMMIT. Until then the engine carried a
   sixteenth into the inch and stopped, so 23.99 printed `1'-12"` and this table reproduced it
   (PRD §I.8: "reproduced, not endorsed"). A twelve-inch figure is a foot, and both formatters
   carry it there now; the seven rows that moved are the seven whose remainder reaches twelve. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { feetInches16 } from './fmt.js';

const VECTORS = /* VECTORS-BEGIN */ [
  [6.875, "6 7/8\""],
  [114, "9'-6\""],
  [8.526315789473685, "8 1/2\""],
  [8.5263, "8 1/2\""],
  [24, "2'-0\""],
  [12.5, "1'-0 1/2\""],
  [0, "0\""],
  [0.03125, "0\""],
  [0.53125, "0 1/2\""],
  [0.59375, "0 5/8\""],
  [23.99, "2'-0\""],
  [11.97, "1'-0\""],
  [-3.5, "-1'-8 1/2\""],
  [null, "-"],
  [0.15625, "0 1/8\""],
  [0.28125, "0 1/4\""],
  [0.40625, "0 3/8\""],
  [0.46875, "0 1/2\""],
  [0.96875, "1\""],
  [11.96875, "1'-0\""],
  [11.9375, "11 15/16\""],
  [0.09375, "0 1/8\""],
  [3.03125, "3\""],
  [7.34375, "7 3/8\""],
  [-0.5, "-1'-11 1/2\""],
  [-12, "-1'-0\""],
  [-0.03125, "0\""],
  [35.97, "3'-0\""],
  [-1e-20, "0\""],
  [-5e-324, "0\""],
  [5e-324, "0\""],
  [-0.0, "0\""],
  [1e+20, "8333333333333332992'-4\""],
  [-1e+20, "-8333333333333332992'-8\""],
  [123456789.123, "10288065'-9 1/8\""],
  [108, "9'-0\""],
  [102.3157894736842, "8'-6 5/16\""],
  [true, "1\""],
  [false, "0\""]
] /* VECTORS-END */;

test('every vector prints exactly what the engine printed', () => {
  assert.ok(VECTORS.length >= 14, 'the table must carry at least the PRD §I.8 rows');
  const wrong = [];
  for (const [x, want] of VECTORS) {
    const got = feetInches16(x);
    if (got !== want) wrong.push(`${JSON.stringify(x)}: got ${JSON.stringify(got)}, _fmt_in says ${JSON.stringify(want)}`);
  }
  assert.deepEqual(wrong, [], wrong.join('\n'));
});

test('the table is the one the parity test reads, and it is JSON', () => {
  /* The Python side extracts the text between the markers and hands it to json.loads. If this
     file's table stopped being JSON — a trailing comma, a single-quoted string — the JS half would
     still run and the Python half would fail to parse, so the same extraction is done here and must
     agree with the array the test above iterated. */
  const src = readFileSync(new URL('./fmt.test.mjs', import.meta.url), 'utf8');
  const begin = src.indexOf('/* VECTORS-BEGIN */');
  const end = src.indexOf('/* VECTORS-END */');
  assert.ok(begin > 0 && end > begin, 'both marker comments must be present, in order');
  const text = src.slice(begin + '/* VECTORS-BEGIN */'.length, end);
  const parsed = JSON.parse(text);
  assert.equal(parsed.length, VECTORS.length);
  parsed.forEach(([x, want], i) => {
    assert.ok(Object.is(x, VECTORS[i][0]) || x === VECTORS[i][0], `row ${i} parses to the same input`);
    assert.equal(want, VECTORS[i][1]);
  });
  // PRD §I.8 names fourteen rows; every one of them is in the table. Its two carry rows are the
  // PRD's inputs with WP-14.20's answers: the PRD printed `1'-12"` and `12"` as the engine's
  // behaviour "reproduced, not endorsed", and WP-14.20 carried the inch into the foot on both sides.
  const required = [
    [6.875, "6 7/8\""], [114, "9'-6\""], [8.526315789473685, "8 1/2\""], [8.5263, "8 1/2\""],
    [24, "2'-0\""], [12.5, "1'-0 1/2\""], [0, "0\""], [0.03125, "0\""], [0.53125, "0 1/2\""],
    [0.59375, "0 5/8\""], [23.99, "2'-0\""], [11.97, "1'-0\""], [-3.5, "-1'-8 1/2\""], [null, "-"],
  ];
  for (const [x, want] of required) {
    assert.ok(parsed.some(([px, pw]) => px === x && pw === want), `PRD row ${JSON.stringify(x)} → ${want}`);
  }
});

test('an absent figure prints the corpus mark for absent; a broken one is refused', () => {
  assert.equal(feetInches16(null), '-');
  assert.equal(feetInches16(undefined), '-');
  // Python raises on these; printing '-' would make a broken figure read as an absent one
  for (const x of [NaN, Infinity, -Infinity]) {
    assert.throws(() => feetInches16(x), RangeError, `${x} must be refused`);
  }
  for (const x of ['8.5', {}, [], 8n]) {
    assert.throws(() => feetInches16(x), TypeError, `${typeof x} must be refused`);
  }
});

test('the notation is ASCII and the fraction is always reduced', () => {
  for (let i = -400; i <= 400; i += 1) {
    const s = feetInches16(i / 32);
    assert.match(s, /^(-?\d+'-)?\d+( \d+\/\d+)?"$/, `${i / 32} printed ${s}`);
    const m = / (\d+)\/(\d+)"$/.exec(s);
    if (m) {
      const [n, d] = [Number(m[1]), Number(m[2])];
      assert.ok(n > 0 && n < d && [2, 4, 8, 16].includes(d) && n % 2 === 1,
        `${s}: a sixteenth must be written in lowest terms`);
    }
  }
});

test('twelve inches is a foot: no figure prints an inch of twelve (WP-14.20)', () => {
  /* The carry row the old engine printed as `1'-12"` is 2'-0" now, and the rule under it is that
     NO output ends in twelve inches -- swept over every sixty-fourth of an inch across eighty
     inches and each side of every carry, so a port that carries only on the sixteenth (and misses
     divmod's own 12.0 remainder on a vanishing negative) cannot pass by the table's luck. */
  assert.equal(feetInches16(23.99), "2'-0\"");
  assert.equal(feetInches16(-1e-20), '0"', 'a remainder of exactly 12.0 carries with no sixteenth');
  const twelve = [];
  const probe = (x) => { const s = feetInches16(x); if (/(^|-)12"$/.test(s)) twelve.push(`${x} -> ${s}`); };
  for (let k = -40 * 64; k <= 40 * 64; k += 1) probe(k / 64);
  for (let w = -24; w <= 24; w += 1) {
    for (const d of [1e-9, 1e-6, 0.001, 0.01, 0.03]) {
      probe(w + 1 - d); probe(w + 15.5 / 16 - d); probe(w + 15.5 / 16 + d);
    }
  }
  for (const x of [-1e-20, -5e-324, -1e-300]) probe(x);
  assert.deepEqual(twelve.slice(0, 5), [], `${twelve.length} outputs print twelve inches`);
});
