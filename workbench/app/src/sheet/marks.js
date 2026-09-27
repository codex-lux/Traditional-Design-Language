/* The geometry of the sheet's marks, in the model frame, with no React in it (WP-14.4).

   `Sheet.jsx` drew its doors, windows and stair from arithmetic written inline in its components,
   so none of it could be tested without a browser: the window symbol stood on the footprint's
   face while `windows()` had already computed the room's own element face, and nothing under
   `node --test` could see it. The arithmetic lives here now, as pure functions returning plain
   numbers, and the components only turn them into elements. The lift itself moved no ink -- the
   bench sheet was server-rendered for all 22 plates of the sixteen shipped plans before and after
   and compared byte for byte -- and every behaviour change that followed has a test here.

   Frame: model feet, x east; `y` is SCREEN y (north up is negative), as everything inside the
   sheet's <svg> is drawn. */

export const add = (p, v, k) => [p[0] + v[0] * k, p[1] + v[1] * k];
export const mid = (a, b) => [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];

/* The opening resolved into a wall-local frame: the two jambs A and B and the direction the
   leaf swings. Both wall orientations reduce to this, so a door TYPE is drawn once rather
   than twice — which is why every type below is a few lines.

   WP-13.2: A is the LOW jamb in MODEL terms — west on a horizontal wall, SOUTH on a vertical
   one (the larger screen y) — because that is what the record's `hinge: "low"` names, and
   `render_plan.py::_door` and the DXF read the same word. Until Phase 13 this frame put A at
   the top-left jamb on screen, so a vertical-wall single leaf hung from the NORTH jamb here
   and from the south in the DXF. The sweep flag is no longer carried: `Leaf` derives it. */
export function doorFrame(d) {
  const w = d.w;
  const vert = d.horiz === false || d.wall === 'W' || d.wall === 'E';
  // THE BREAK IN THE WALL (WP-14.4). An interior door's is the 0.7 ft it always was, centred on
  // the line the two rooms share. An EXTERIOR door's is the wall itself: from the room's face
  // outward by the wall's own thickness, which is where the plate cuts the hole -- a fixed
  // 0.7 ft centred on the face left most of a 15.5 in wall standing across the doorway.
  const t = d.exterior && d.t > 0 ? d.t : null;
  if (vert) {
    const x = d.x, y0 = -d.y - w / 2;                       // screen y of the NORTH jamb
    const s = d.swingRight === false ? -1 : 1;
    const rect = t ? { x: d.wall === 'W' ? x - t : x, y: y0, width: t, height: w }
      : { x: x - 0.35, y: y0, width: 0.7, height: w };
    return { w, vert, A: [x, y0 + w], B: [x, y0], nrm: [s, 0], rect };
  }
  const x0 = d.x - w / 2, y = -d.y;
  const tt = d.swingUp !== false ? -1 : 1;
  const rect = t ? { x: x0, y: d.wall === 'S' ? y : y - t, width: w, height: t }
    : { x: x0, y: y - 0.35, width: w, height: 0.7 };
  return { w, vert, A: [x0, y], B: [x0 + w, y], nrm: [0, tt], rect };
}

/* The SVG sweep flag for a leaf drawn from its open tip to the far jamb about the hinge, in
   screen space: 1 when the quarter-turn runs clockwise as a reader sees it, which is the sign
   of the cross product. `render_plan.py::sweep_flag` is the same rule; a table with one wrong
   row drew every horizontal-wall leaf in the Python sheet as its own mirror for seven phases. */
export function sweepFlag(hinge, tip, far) {
  const c = (tip[0] - hinge[0]) * (far[1] - hinge[1]) - (tip[1] - hinge[1]) * (far[0] - hinge[0]);
  return c > 0 ? 1 : 0;
}

/* A window: the break in the wall, the glazing on its centre line, and the sill projecting past
   the jambs. Returns the three as numbers; `WindowMark` draws them.

   WP-14.4: AT THE ROOM'S OWN FACE AND AT THE WALL'S OWN THICKNESS. `windows()` has computed the
   face (`w.x` on a W or E wall, `w.y` on an S or N one) since WP-11.14, and this drew a W window
   at x = 0 and an S window at y = 0 regardless -- the footprint's edges -- so every window a
   dependency has on its west or south wall stood on the main block. And the symbol was 0.75 ft
   deep on every house, where the Tidewater envelope is 15.5 in. `t` is the wall's thickness
   (`wallOf(footprint).exterior_ft`); 0.75 is kept only for a caller that has none. */
export function windowMark(w, t = 0.75) {
  const vert = w.wall === 'W' || w.wall === 'E';
  const r = vert
    ? { x: w.wall === 'W' ? w.x - t : w.x, y: -w.y - w.w / 2, width: t, height: w.w }
    : { x: w.x - w.w / 2, y: w.wall === 'S' ? -w.y : -w.y - t, width: w.w, height: t };
  const sill = vert
    ? [r.x + (w.wall === 'W' ? -0.35 : t + 0.35), r.y - 0.5,
       r.x + (w.wall === 'W' ? -0.35 : t + 0.35), r.y + r.height + 0.5]
    : [r.x - 0.5, r.y + (w.wall === 'S' ? t + 0.35 : -0.35),
       r.x + r.width + 0.5, r.y + (w.wall === 'S' ? t + 0.35 : -0.35)];
  const glazing = vert
    ? [r.x + t / 2, r.y, r.x + t / 2, r.y + r.height]
    : [r.x, r.y + t / 2, r.x + r.width, r.y + t / 2];
  return { vert, rect: r, sill, glazing };
}

/* The stair's arrow (WP-14.4): along the first flight, in the flight's own stated direction,
   over its middle two thirds -- `render_plan.py`'s arrow, which has said which way is up since
   WP-9.6 while the bench printed "UP 20R" over a set of parallel lines that did not. Returns the
   shaft and the two barbs in screen coordinates, or null for a flight with no direction. */
const HEADING = { N: [0, -1], S: [0, 1], E: [1, 0], W: [-1, 0] };

export function stairArrow(f) {
  const d = HEADING[f && f.direction];
  if (!d) return null;
  const [dx, dy] = d;
  const cx = f.x_ft + f.width_ft / 2, cy = -f.y_ft - f.depth_ft / 2;
  const run = (f.direction === 'E' || f.direction === 'W' ? f.width_ft : f.depth_ft) * 0.34;
  const hx = cx + dx * run, hy = cy + dy * run;
  const barb = 0.45, spread = 0.27;
  return {
    shaft: [cx - dx * run, cy - dy * run, hx, hy],
    head: [hx - dx * barb - dy * spread, hy - dy * barb + dx * spread, hx, hy,
           hx - dx * barb + dy * spread, hy - dy * barb - dx * spread],
  };
}

/* The label on a bay line: the record's own figure, to the hundredth the placer states it at.
   `Math.round` printed a 12.17 ft module's lines as 12, 24, 37 -- figures the record does not
   hold -- where `render_plan.py` prints 12.17, 24.34, 36.51. */
export function bayLabel(x) {
  return String(Math.round(x * 100) / 100);
}
