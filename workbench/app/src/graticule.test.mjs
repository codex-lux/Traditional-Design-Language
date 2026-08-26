/* The atlas's grid. Small enough to look obviously right and wrong twice already.

   The first version of `gridStep` took the coarsest step whose line count FITTED, which
   is always the coarsest step in the ladder — so at thirteen degrees of longitude it
   chose thirty, and thirty-degree lines do not intersect a thirteen-degree window at all.
   The grid silently vanished at exactly the zooms WP-5.7 had just made reachable, and it
   took a browser probe counting <line> elements to notice. Everything below is that class
   of defect. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { GRATICULE_STEPS, gridStep, ticks } from './surfaces/phylo/graticule.js';

const lines = (w) => ticks(0, w, gridStep(w)).length;

test('every width the map can be set to draws a grid', () => {
  // MIN_W is 3 and MAX_W is 340; the map is never outside that, and neither is this.
  for (let w = 3; w <= 340; w += 0.25) {
    const n = lines(w);
    assert.ok(n >= 4, `${w}° of longitude drew ${n} meridians — a grid that is not a grid`);
    assert.ok(n <= 40, `${w}° of longitude drew ${n} meridians — that is wallpaper`);
  }
});

test('the step is one of the declared rungs, and gets finer as the view narrows', () => {
  let last = Infinity;
  for (let w = 340; w >= 3; w -= 0.5) {
    const st = gridStep(w);
    assert.ok(GRATICULE_STEPS.includes(st), `${st} is not a rung`);
    assert.ok(st <= last, `step went back up from ${last} to ${st} at ${w}°`);
    last = st;
  }
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
  const out = ticks(-19.78, -6.57, 2);
  assert.deepEqual(out, [-18, -16, -14, -12, -10, -8]);
  // Repeated addition of 0.2 is where a graticule label becomes 39.99999999999999.
  ticks(0, 4, 0.2).forEach((v) => {
    assert.equal(Math.abs(v * 5 - Math.round(v * 5)) < 1e-9, true, `${v} is off the grid`);
  });
  // Both ends are inclusive when they fall exactly on a line.
  assert.deepEqual(ticks(0, 10, 5), [0, 5, 10]);
});
