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
  const first = Math.ceil(lo / step) * step;
  for (let v = first; v <= hi + step * 1e-9 && out.length < cap; v += step) {
    // Rounded back onto the grid: repeated addition of 0.2 drifts, and a graticule whose
    // labels would read 39.99999999999999 is a graticule that has stopped being one.
    out.push(Math.round(v / step) * step);
  }
  return out;
}
