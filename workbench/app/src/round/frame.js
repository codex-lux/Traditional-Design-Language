/* The camera for the Round — and nothing in this file knows what three.js is.

   WP-12.4. The brief is docs/prd/phase-12-the-sheet-in-the-round.md §7.4.

   This is a LEAF, for the reason build/scene.py is one: everything a camera can show is
   already in the record, so the arithmetic that decides where a point lands on the plate
   must be testable without a bundle, a browser or a GPU. `round.test.mjs` runs it under
   `node --test` with no npm install, which is how build/check_all.py runs the app suite.
   It may import nothing but its siblings and ../sheet/derive.js.

   THE ONE CONVENTION TO READ BEFORE ANYTHING ELSE. Azimuth is the compass bearing of the
   CAMERA from the target -- where the viewer stands, not where they look. Standing south of
   a house to draw its south elevation is azimuth 180, not 0. Getting this backwards draws
   every elevation as its own opposite and every axon mirrored, and the drawing looks
   plausible either way, which is the WP-5.11 sweep-flag defect one dimension up: a model
   test cannot see it and only the ink can.

   The model frame is build/scene.py's and is not re-derived here: x east, y north, z up,
   feet, the origin the main block's SW corner at grade. A viewer sets its up vector to +z
   and transforms nothing. */

/* True isometric: the elevation at which the three model axes project to equal lengths.
   DERIVED rather than typed -- atan(1/sqrt(2)) -- because a bare 35.264 in this file is a
   dimension with no source, which is what build/scene.py's own source-reading test refuses
   one layer down. tokens.css carries --axon-elevation-deg so a dimetric 30 can be ruled
   later without a code change; Round.jsx reads that token and passes it in. */
export const AXON_ELEVATION_DEG = (Math.atan(1 / Math.SQRT2) * 180) / Math.PI;

/* The plate's margins, in feet, as Sheet.jsx reserves them. Framing must leave the same
   air round the model that the flat plate leaves round the drawing, or the 2D plate laid
   over the model at the same view will not sit on it. */
export const MARGIN_FT = { left: 11, right: 15, top: 15, bottom: 9 };

/* Where the viewer stands for each named view. */
const FACE_AZIMUTH = { N: 0, E: 90, S: 180, W: 270 };
const AXON_AZIMUTH = { ne: 45, se: 135, sw: 225, nw: 315 };

/* Facing a face, the axon that shows it AND the face to the viewer's left: facing the south
   front you look north, your left hand points west, and you see S and W. */
const AXON_FOR_ENTRANCE = { S: 'sw', N: 'ne', E: 'se', W: 'nw' };

const RAD = Math.PI / 180;
const DEFAULT_ASPECT = 4 / 3;

export const isFaceView = (v) => typeof v === 'string' && /^[snew]$/.test(v);
export const isAxonView = (v) => typeof v === 'string' && /^axon-(sw|se|nw|ne)$/.test(v);
export const isPlanView = (v) => typeof v === 'string' && /^plan-l\d+$/.test(v);

export function planLevel(view) {
  const m = /^plan-l(\d+)$/.exec(view || '');
  return m ? +m[1] : null;
}

export function defaultAxon(entranceFace) {
  return 'axon-' + (AXON_FOR_ENTRANCE[entranceFace] || 'sw');
}

/* ---------------------------------------------------------------- vectors */

const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a, b) => [
  a[1] * b[2] - a[2] * b[1],
  a[2] * b[0] - a[0] * b[2],
  a[0] * b[1] - a[1] * b[0],
];
const norm = (a) => {
  const L = Math.hypot(a[0], a[1], a[2]) || 1;
  return [a[0] / L, a[1] / L, a[2] / L];
};

/* The unit vector from the target toward the camera. */
export function eyeDirection(azimuthDeg, elevationDeg) {
  const a = azimuthDeg * RAD;
  const e = elevationDeg * RAD;
  return [Math.sin(a) * Math.cos(e), Math.cos(a) * Math.cos(e), Math.sin(e)];
}

/* The camera's own right/up/forward, given where it stands.

   AT ELEVATION 90 THE WORLD'S UP IS THE CAMERA'S FORWARD and the cross product degenerates,
   so a plan view takes model-north as its up. That is not a special case bolted on: it is
   the Sheet's own rule -- north is up on every plate this tree draws -- arriving in the
   camera. */
export function basis(azimuthDeg, elevationDeg) {
  const d = eyeDirection(azimuthDeg, elevationDeg);
  const forward = [-d[0], -d[1], -d[2]];
  const worldUp = Math.abs(forward[2]) > 0.999 ? [0, 1, 0] : [0, 0, 1];
  const right = norm(cross(forward, worldUp));
  const up = norm(cross(right, forward));
  return { forward, right, up };
}

/* ---------------------------------------------------------------- framing */

function corners(bounds) {
  const { min, max } = bounds;
  const out = [];
  for (const x of [min[0], max[0]]) {
    for (const y of [min[1], max[1]]) {
      for (const z of [min[2], max[2]]) out.push([x, y, z]);
    }
  }
  return out;
}

/* The half-height in feet that fits `scene.bounds` at this view with the sheet's margins.
   Measured on the projected corners rather than on the bounding box's diagonal: a house is
   not a sphere, and framing it as one leaves an axon floating in the middle of the plate. */
export function framing(scene, view, aspect = DEFAULT_ASPECT, opts = {}) {
  const pose = orientationFor(view, scene, opts);
  const b = basis(pose.azimuthDeg, pose.elevationDeg);
  const t = targetFor(view, scene, opts);
  let halfW = 0;
  let halfH = 0;
  for (const c of corners(scene.bounds)) {
    const v = sub(c, t);
    halfW = Math.max(halfW, Math.abs(dot(v, b.right)));
    halfH = Math.max(halfH, Math.abs(dot(v, b.up)));
  }
  // The margins are asymmetric, so they widen the extent rather than scaling it.
  const wantW = 2 * halfW + MARGIN_FT.left + MARGIN_FT.right;
  const wantH = 2 * halfH + MARGIN_FT.top + MARGIN_FT.bottom;
  return Math.max(wantH, wantW / Math.max(aspect, 1e-6)) / 2;
}

/* ---------------------------------------------------------------- poses */

function storeyAt(scene, level) {
  const ss = scene.storeys || [];
  return ss.find((s) => s.index === level) || ss[0] || null;
}

function orientationFor(view, scene, opts = {}) {
  const axonEl = opts.axonElevationDeg == null ? AXON_ELEVATION_DEG : opts.axonElevationDeg;
  if (isPlanView(view) || view === 'roof') return { azimuthDeg: 0, elevationDeg: 90 };
  if (isFaceView(view)) {
    return { azimuthDeg: FACE_AZIMUTH[view.toUpperCase()], elevationDeg: 0 };
  }
  if (isAxonView(view)) {
    return { azimuthDeg: AXON_AZIMUTH[view.slice(5)], elevationDeg: axonEl };
  }
  // `free` has no named orientation; the caller carries the live one.
  return null;
}

function targetFor(view, scene, opts = {}) {
  const { min, max } = scene.bounds;
  const cx = (min[0] + max[0]) / 2;
  const cy = (min[1] + max[1]) / 2;
  const lvl = planLevel(view);
  if (lvl != null) {
    const st = storeyAt(scene, lvl);
    const cut = (st ? st.floor_z_ft : 0) + (scene.cut_height_ft || 0);
    return [cx, cy, cut];
  }
  if (view === 'roof') return [cx, cy, max[2]];
  return [cx, cy, (min[2] + max[2]) / 2];
}

/* A named pose. Returns null for `free`, which is a reading of the live camera and not a
   place this function can name. */
export function poseFor(view, scene, level = null, opts = {}) {
  const v = level == null ? view : `plan-l${level}`;
  const o = orientationFor(v, scene, opts);
  if (!o) return null;
  const target = targetFor(v, scene, opts);
  const lvl = planLevel(v);
  const st = lvl == null ? null : storeyAt(scene, lvl);
  return {
    view: v,
    azimuthDeg: o.azimuthDeg,
    elevationDeg: o.elevationDeg,
    target,
    halfHeightFt: framing(scene, v, opts.aspect == null ? DEFAULT_ASPECT : opts.aspect, opts),
    /* A plan is a cut, and the cut is where scene.cut_height_ft says -- read, never typed.
       The roof plan is the same camera with nothing cut away, which is the whole difference
       between the two views and is why they share an orientation. */
    cut: lvl == null || !st ? null : { z_ft: st.floor_z_ft + (scene.cut_height_ft || 0), level: lvl },
  };
}

/* ---------------------------------------------------------------- tween */

const easeOutCubic = (t) => 1 - Math.pow(1 - t, 3);

/* Shortest way round: 350° to 10° is +20°, not −340°. Without this an orbit from the west
   elevation to the north one spins the house three quarters of the way round the wrong way,
   which reads as a bug in the model rather than in the interpolation. */
export function shortestTurn(from, to) {
  let d = (to - from) % 360;
  if (d > 180) d -= 360;
  if (d < -180) d += 360;
  return d;
}

export function tween(a, b, t) {
  if (t <= 0) return a;
  if (t >= 1) return b;
  const k = easeOutCubic(t);
  const lerp = (p, q) => p + (q - p) * k;
  return {
    view: 'free',
    azimuthDeg: a.azimuthDeg + shortestTurn(a.azimuthDeg, b.azimuthDeg) * k,
    elevationDeg: lerp(a.elevationDeg, b.elevationDeg),
    target: [
      lerp(a.target[0], b.target[0]),
      lerp(a.target[1], b.target[1]),
      lerp(a.target[2], b.target[2]),
    ],
    halfHeightFt: lerp(a.halfHeightFt, b.halfHeightFt),
    cut: k < 1 ? a.cut : b.cut,
  };
}

/* ---------------------------------------------------------------- projection */

/* Model feet to plate pixels. Orthographic: the scale is one number for the whole plate,
   which is what makes a scale bar honest and a perspective one a lie. Returns depth in feet
   along the view direction so a label can be hidden behind the building it names. */
export function project(pose, viewport, p) {
  const b = basis(pose.azimuthDeg, pose.elevationDeg);
  const v = sub(p, pose.target);
  const k = viewport.height / (2 * pose.halfHeightFt);
  return [
    viewport.width / 2 + dot(v, b.right) * k,
    viewport.height / 2 - dot(v, b.up) * k,
    dot(v, b.forward),
  ];
}

/* The inverse, on a stated horizontal plane. Returns null where the plane cannot be hit --
   an elevation looks along the horizon and never meets z = const -- because an invented
   intersection is a coordinate the reader would believe. */
export function unproject(pose, viewport, px, zFt) {
  const b = basis(pose.azimuthDeg, pose.elevationDeg);
  const k = viewport.height / (2 * pose.halfHeightFt);
  const sx = (px[0] - viewport.width / 2) / k;
  const sy = (viewport.height / 2 - px[1]) / k;
  const o = [
    pose.target[0] + b.right[0] * sx + b.up[0] * sy,
    pose.target[1] + b.right[1] * sx + b.up[1] * sy,
    pose.target[2] + b.right[2] * sx + b.up[2] * sy,
  ];
  if (Math.abs(b.forward[2]) < 1e-9) return null;
  const t = (zFt - o[2]) / b.forward[2];
  return [o[0] + b.forward[0] * t, o[1] + b.forward[1] * t];
}

/* ---------------------------------------------------------------- named or free */

/* Half a degree, because that is below what a reader can see and above what a rounding can
   produce. A pose that has drifted is FREE and the caption must say so: a free view that
   still calls itself SOUTH ELEVATION is a drawing lying about its own projection. */
export const NAMED_TOL_DEG = 0.5;

export function isNamed(pose, view, scene, opts = {}) {
  if (!pose || !view || view === 'free') return false;
  const named = poseFor(view, scene, null, { ...opts, aspect: opts.aspect });
  if (!named) return false;
  return (
    Math.abs(shortestTurn(pose.azimuthDeg, named.azimuthDeg)) < NAMED_TOL_DEG &&
    Math.abs(pose.elevationDeg - named.elevationDeg) < NAMED_TOL_DEG
  );
}

/* Every view this package can name, in the order the view bar prints them. APPROACH is
   deliberately absent: the 8 Sep ruling puts a 5'-6" perspective view in v1 and WP-12.7
   lands it, beside the entrance and porch it exists to show. Adding it here would put a
   second projection kind in this file before there is anything dressed to look at. */
export function namedViews(scene) {
  const out = (scene.storeys || []).filter((s) => s.index >= 0).map((s) => `plan-l${s.index}`);
  return out.concat(['s', 'n', 'e', 'w', 'axon-sw', 'axon-se', 'axon-nw', 'axon-ne', 'roof']);
}
