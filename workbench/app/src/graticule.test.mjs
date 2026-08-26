/* The atlas's grid. Small enough to look obviously right and wrong twice already.

   The first version of `gridStep` took the coarsest step whose line count FITTED, which is
   always the coarsest step in the ladder — so at thirteen degrees of longitude it chose
   thirty, and thirty-degree lines do not intersect a thirteen-degree window at all. The
   grid silently vanished at exactly the zooms WP-5.7 had just made reachable.

   The first version of THIS FILE then failed to pin it. An adversarial mutation pass found
   that `MIN_LINES` could be tripled, the drift rounding deleted and the inclusive endpoint
   removed, all three with the suite staying green: the density bounds were 4..40 against a
   real range of 6..16, the drift tolerance was 1e-9 against a real error of 4e-16, and the
   endpoint was only ever exercised at a case where the arithmetic is exact. Each assertion
   below is now driven where it binds. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { GRATICULE_STEPS, gridStep, ticks } from './surfaces/phylo/graticule.js';

const lines = (w) => ticks(0, w, gridStep(w)).length;

test('every width the map can be set to draws a usable grid, and not wallpaper', () => {
  // MIN_W is 3 and MAX_W is 340; the map is never outside that, and neither is this. The
  // bounds are the REAL range the rule produces, not a comfortable margin around it: at
  // 4..40 the rule could be tripled without a test noticing.
  let lo = Infinity, hi = 0;
  for (let w = 3; w <= 340; w += 0.25) {
    const n = lines(w);
    lo = Math.min(lo, n); hi = Math.max(hi, n);
  }
  assert.ok(lo >= 5, `the sparsest grid the rule can draw is ${lo} lines — that is not a grid`);
  assert.ok(hi <= 17, `the densest grid the rule can draw is ${hi} lines — that is wallpaper`);
});

test('the step is one of the declared rungs, and gets finer as the view narrows', () => {
  let last = Infinity;
  let changes = 0;
  for (let w = 340; w >= 3; w -= 0.5) {
    const st = gridStep(w);
    assert.ok(GRATICULE_STEPS.includes(st), `${st} is not a rung`);
    assert.ok(st <= last, `step went back up from ${last} to ${st} at ${w}°`);
    if (st !== last) changes += 1;
    last = st;
  }
  // Every rung between the coarsest the map can reach and the finest must actually be
  // used; a ladder with unreachable rungs is a ladder with the wrong thresholds.
  assert.ok(changes >= 6, `only ${changes} of the ${GRATICULE_STEPS.length} rungs are ever selected`);
});

test('the home view keeps the ten-degree grid it shipped with', () => {
  assert.equal(gridStep(134), 10);
});

test('a degenerate width does not divide by zero or hang', () => {
  assert.equal(gridStep(0), GRATICULE_STEPS[0]);
  assert.equal(gridStep(-5), GRATICULE_STEPS[0]);
  assert.equal(gridStep(NaN), GRATICULE_STEPS[0]);
  assert.deepEqual(ticks(0, 10, 0), []);
  assert.deepEqual(ticks(10, 0, 1), []);          // hi before lo
  assert.equal(ticks(-1e6, 1e6, 0.1).length, 60); // capped rather than unbounded
});

test('ticks land on the grid, inside the window, and do not drift', () => {
  assert.deepEqual(ticks(-19.78, -6.57, 2), [-18, -16, -14, -12, -10, -8]);
  // Repeated addition of 0.2 is where a graticule label becomes 39.99999999999999. The
  // tolerance has to be TIGHTER than the drift it is looking for: raw accumulation over
  // this range is about 4e-16, so 1e-9 could not see it and 0 is what the rounding gives.
  ticks(0, 20, 0.2).forEach((v) => {
    assert.equal(v * 5, Math.round(v * 5), `${v} is off the grid — the rounding is gone`);
  });
  // Both ends are inclusive when they fall on a line — including when floating-point
  // accumulation lands a hair PAST the end, which is the case the epsilon exists for and
  // the case `ticks(0, 10, 5)` (exact in binary) can never exercise.
  assert.deepEqual(ticks(0, 10, 5), [0, 5, 10]);
  assert.deepEqual(ticks(0, 0.6, 0.2), [0, 0.2, 0.4, 0.6],
    '0.2+0.2+0.2 is 0.6000000000000001; without the epsilon the last line is dropped');
  assert.deepEqual(ticks(0, 2.1, 0.7), [0, 0.7, 1.4, 2.1]);
});
