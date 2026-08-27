/* The grid behind the atlas, at whatever spacing the view can carry.

   It was every ten degrees at every scale, which is two lines at continental zoom and —
   once WP-5.7 let the reader down to three degrees of longitude — none at all. A grid
   that disappears exactly when the reader is closest to the drawing is not a grid.

   Its own file, and plain JavaScript rather than JSX, because the first version of the
   step rule shipped INVERTED — it took the largest step whose line count fitted, which is
   always the coarsest step in the ladder, which drew nothing. A browser probe caught it;
   a unit test would have caught it sooner, and now does. */

/* Degrees between lines, coarsest first. */
export const GRATICULE_STEPS = [30, 10, 5, 2, 1, 0.5, 0.2, 0.1];

/* The coarsest step that still puts at least MIN_LINES across the view. Coarsest, not
   finest: a grid is a scale reference, and eight lines read where forty are wallpaper. */
const MIN_LINES = 5;

export function gridStep(width) {
  if (!(width > 0)) return GRATICULE_STEPS[0];
  return GRATICULE_STEPS.find((st) => width / st >= MIN_LINES)
    || GRATICULE_STEPS[GRATICULE_STEPS.length - 1];
}

/* The multiples of `step` inside [lo, hi]. Capped, because a hand-set view box and a
   0.1 degree step could otherwise ask for thousands of lines; the cap is far above what
   `gridStep` will ever produce and exists so a bad caller degrades rather than hangs. */
export function ticks(lo, hi, step, cap = 60) {
  const out = [];
  if (!(step > 0) || !(hi >= lo)) return out;
  /* Counted in MULTIPLES of the step and multiplied out once, rather than accumulated.

     The first version added `step` repeatedly and then "rounded back onto the grid" with
     `Math.round(v / step) * step` — which recovers the right multiple and then puts the
     error straight back, because `3 * 0.2` is 0.6000000000000001 in binary floating point
     and `3 * 0.7` is 2.0999999999999996. The rounding looked like a fix and was not; the
     test that was supposed to prove it carried a 1e-9 tolerance against a 4e-16 error and
     could not see the difference. `toFixed` at nine places is what actually lands the
     value on the number a reader would write down, and a graticule at 1e-9 of a degree is
     a graticule at a tenth of a millimetre. */
  const first = Math.ceil(lo / step);
  const last = hi / step;
  for (let k = first; k <= last + 1e-9 && out.length < cap; k += 1) {
    out.push(Number((k * step).toFixed(9)));
  }
  return out;
}
