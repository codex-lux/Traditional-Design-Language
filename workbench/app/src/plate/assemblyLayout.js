/* WHERE EACH ASSEMBLY OF A TRIM PLATE STANDS, AND AT WHAT SCALE (WP-14.6, PRD §I.6).

   A pack that has no order stack still has assemblies — `trim-classical` has three wall sections
   and three door casings — and the Proportions surface drew none of them. `components/AssemblyPlate
   .jsx` (WP-14.9) draws them; this module decides WHERE, and decides it without React, a DOM or a
   font, so the arithmetic that keeps one drawing off another is testable on its own.

   FRAMES BY HEIGHT, AND A FRAME IS A SCALE. Assemblies are taken tallest first, stably by the
   payload's declaration order. An assembly joins the current frame when that frame's tallest is at
   most TWICE its own `height_in`, and otherwise opens a new frame. So a frame never holds two
   things more than 2:1 apart in height — a 114 in wall section and a 6 in casing drawn at one
   scale would make the casing a smudge — and every item in a frame shares the frame's one scale,
   which is the only thing that lets a reader compare two of them by eye. `trim-classical` gives
   two frames: the three wall sections (114 in each) and the three casings (6.9, 6.0 and 4.5 in).
   Within a frame the items stand side by side on ONE BASELINE in declaration order, which is the
   order the pack states and the order the rules table beside the plate lists.

   THE WIDTH IS THE DRAWN EXTENT, MEASURED FROM THE WALL PLANE. A served assembly carries
   `geometry` built under `datum: "wall"` (PRD §H), so every face is measured from x = 0 at the
   wall plane: `x` is the face, `x_from` where the member starts, and a hollow may turn BEHIND the
   plane (a scotia's throat is half its own height inside its members). The extent is read off
   those figures, off every segment's end point, and, for an arc, off the two points where its own
   stated angles cross the horizontal — bounds of a curve the engine constructed, never a curve
   constructed here (OQ 83: JavaScript does not know what a cyma is). Where an assembly arrives with
   no geometry its members' `projection_in` stands in, and the item SAYS which it read
   (`extentFrom`), because a width taken from a stated projection is not the width of a drawing.

   EACH ITEM RESERVES A NOMINAL WALL STRIP BEHIND ITS PLANE AND A GUTTER AFTER ITS FACE. The plate
   draws a hatched strip at the wall plane as interface furniture (§I.6), and leaders to the right
   of each section, so the room for both is allotted here rather than discovered by overlap. Both
   are FRACTIONS OF THE FRAME'S HEIGHT and that is deliberate: every frame is scaled to fill the same
   plate height, so a fraction of the frame's height is a constant number of pixels on the page,
   which is what a label needs. The last item keeps its gutter, because its leaders need it too.

   A STATED SCALE PER FRAME. `scale.barIn` is a length off `SCALE_LADDER_IN` — the longest that is no
   more than `SCALE_BAR_FRAC` of the frame's height — written in the corpus's own notation by
   `feetInches16`, so the bar and the leaders cannot print one inch two ways. Given a `box`
   ({ widthPx, heightPx }) the frame also states `pxPerIn`, one number, fitting the frame whole.

   NOTHING IS DROPPED. An assembly with no usable height cannot be put in any frame; it comes back
   in `unplaced` with the reason, because a plate that silently draws five of six assemblies reads
   exactly like a pack that has five.

   `placeLabels` de-collides the leader labels of one frame: order kept, no two closer than
   `minGapPx` (or than their own heights allow), each moved as little as the others allow, and held
   inside `top`/`bottom` where they fit — `overflow` says so where they do not, rather than
   overlapping them.

   A TURNED ASSEMBLY IS LAID ON ITS SIDE, AND ITS EXTENT IS SWAPPED (WP-14.24, PRD tranche 2 §C.3,
   §C.9). An assembly whose record declares `axis: "across-from-the-jamb"` — `trim-classical`'s
   three casings, each on its own reveal member's note — runs outward from the jamb, so each
   member's `height_in` is a WIDTH. The server's geometry stays upright (`build/profiles.py` is not
   told the axis), and the plate turns it with ONE `rotate` beside its translate and scale, so the
   drawn box is the served box turned: `extentOf` gives such an assembly the swapped extent — its
   horizontal extent is the jamb to the far edge, 0 to `height_in`, and its vertical one (`minY`,
   `maxY`) is what the served figures give as the extent from the wall plane. The plate hangs it
   from the wall plane as a plan section does: the jamb at the left, the members reading outward
   left to right in their own order, the wall above the plane and the profile below it. An
   assembly's frame is decided by its DRAWN height, which for a turned one is its depth off the
   wall plus the wall strip above that plane, so three casings an inch or so deep are not drawn at
   the scale of a nine-foot wall.

   A ZONED ASSEMBLY RESERVES ROOM BEHIND ITS WALL STRIP for the zone dimension line the plate
   draws along the wall (`ZONE_FRAC` of the frame's height, a fraction for the reason the gutter
   is one). Zones are the pack's (`zones: [{name, to_parts}]`, held to the members by
   `build/check_orders.py`); nothing here reads where one ends.

   Pure; imports only the corpus's notation. */
import { feetInches16 } from '../fmt.js';

export const JOIN_RATIO = 2;          // a frame's tallest is at most twice a joining assembly's height
export const GUTTER_FRAC = 0.35;      // room after each item's face for its leaders, of the frame height
export const WALL_STRIP_FRAC = 0.06;  // the nominal hatched wall strip behind the plane, of the frame height
export const ZONE_FRAC = 0.1;         // room behind a zoned item's wall strip for its zone dimension line
export const SCALE_BAR_FRAC = 0.25;   // the scale bar is at most this share of the frame height
/* The one axis value that turns an assembly (schema/proportion-pack.schema.json's `axis` enum);
   absent, or `up-the-wall`, it rises up the wall as every stack does. */
export const TURNED_AXIS = 'across-from-the-jamb';
export const SCALE_LADDER_IN = Object.freeze([
  1 / 16, 1 / 8, 1 / 4, 1 / 2, 1, 2, 3, 6, 12, 18, 24, 36, 48, 72, 96, 120, 144, 240,
]);

const TAU = 2 * Math.PI;
const num = (v) => (typeof v === 'number' && Number.isFinite(v) ? v : null);

/* Is the angle `t` swept on the way from a0 to a1 (either direction)? */
function swept(a0, a1, t) {
  const lo = Math.min(a0, a1), hi = Math.max(a0, a1);
  const k = Math.ceil((lo - t) / TAU);
  return t + k * TAU <= hi + 1e-12;
}

/* Does the record turn this assembly? Only the pack's own `axis` says so. */
export function isTurned(asm) {
  return Boolean(asm) && asm.axis === TURNED_AXIS;
}

/* Does the record divide this assembly into zones? At least two, as the schema requires; a
   malformed list is not a division and reserves nothing. */
export function hasZones(asm) {
  return Boolean(asm) && Array.isArray(asm.zones) && asm.zones.length >= 2;
}

/* The extent a served assembly draws. Upright: the horizontal extent, measured from the wall
   plane. Turned: SWAPPED — `minX`/`maxX` run from the jamb (0) to `height_in`, and `minY`/`maxY`
   are the served figures' extent from the wall plane, which the plate lays down the page. */
export function extentOf(asm) {
  const e = wallExtentOf(asm);
  if (!isTurned(asm)) return e;
  const h = num(asm.height_in);
  return { minX: 0, maxX: h !== null && h > 0 ? h : 0, minY: e.minX, maxY: e.maxX, extentFrom: e.extentFrom, turned: true };
}

/* The extent measured from the wall plane, whichever way the assembly runs. */
function wallExtentOf(asm) {
  const xs = [];
  const faces = asm && asm.geometry && Array.isArray(asm.geometry.faces) ? asm.geometry.faces : null;
  if (faces && faces.length) {
    for (const f of faces) {
      for (const v of [f.x, f.x_from]) if (num(v) !== null) xs.push(v);
      for (const s of Array.isArray(f.segments) ? f.segments : []) {
        if (Array.isArray(s.to) && num(s.to[0]) !== null) xs.push(s.to[0]);
        if (s.kind === 'arc' && [s.cx, s.rx, s.a0, s.a1].every((v) => num(v) !== null)) {
          if (swept(s.a0, s.a1, 0)) xs.push(s.cx + s.rx);
          if (swept(s.a0, s.a1, Math.PI)) xs.push(s.cx - s.rx);
        }
      }
    }
    if (xs.length) return { minX: Math.min(0, ...xs), maxX: Math.max(0, ...xs), extentFrom: 'geometry' };
  }
  const members = asm && Array.isArray(asm.members) ? asm.members : [];
  for (const m of members) if (m && num(m.projection_in) !== null) xs.push(m.projection_in);
  if (xs.length) return { minX: Math.min(0, ...xs), maxX: Math.max(0, ...xs), extentFrom: 'members' };
  return { minX: 0, maxX: 0, extentFrom: 'none' };
}

/* The longest length off the ladder that is no more than SCALE_BAR_FRAC of `heightIn`. */
export function scaleBarIn(heightIn) {
  const cap = SCALE_BAR_FRAC * heightIn;
  let best = null;
  for (const v of SCALE_LADDER_IN) if (v <= cap) best = v;
  return best === null ? SCALE_LADDER_IN[0] : best;
}

/* The height a frame must be to hold a TURNED assembly hung from its wall plane: the wall strip
   (or anything behind the plane, whichever is deeper) and any zone reserve above the plane, the
   profile below it. Both reserves are fractions of the frame's own height, so the height is the
   least H with max(WALL_STRIP_FRAC·H, behind) + ZONE_FRAC·H·[zoned] + depth ≤ H — each branch of
   the max solved on its own. */
function turnedNeed(ext, zoned) {
  const depth = Math.max(0, ext.maxY), behind = Math.max(0, -ext.minY);
  const z = zoned ? ZONE_FRAC : 0;
  return Math.max(depth / (1 - WALL_STRIP_FRAC - z), (behind + depth) / (1 - z));
}

export function assemblyLayout(assemblies, { box = null } = {}) {
  const list = Array.isArray(assemblies) ? assemblies : [];
  const placeable = [];
  const unplaced = [];
  list.forEach((a, index) => {
    const id = a && typeof a.id === 'string' ? a.id : null;
    const h = a ? num(a.height_in) : null;
    if (id === null) unplaced.push({ id: null, index, reason: 'the assembly states no id' });
    else if (h === null) unplaced.push({ id, index, reason: 'the assembly states no height_in' });
    else if (h <= 0) unplaced.push({ id, index, reason: `height_in is ${h}; nothing to draw at no height` });
    else {
      const ext = extentOf(a);
      const turned = ext.turned === true;
      const zoned = hasZones(a);
      // the page height the item needs: upright, its height; turned, its depth hung from the wall
      const need = turned ? turnedNeed(ext, zoned) : h;
      if (turned && !(need > 0)) {
        unplaced.push({ id, index, reason: 'turned across the jamb, it projects nothing from the wall plane; nothing to draw at no depth' });
      } else placeable.push({ a, id, index, h, ext, turned, zoned, need });
    }
  });

  // tallest (as drawn) first, stably by declaration
  const byHeight = [...placeable].sort((p, q) => (q.need - p.need) || (p.index - q.index));
  const groups = [];
  for (const p of byHeight) {
    const cur = groups[groups.length - 1];
    if (cur && cur[0].need <= JOIN_RATIO * p.need) cur.push(p);
    else groups.push([p]);
  }

  const frames = groups.map((g, fi) => {
    const heightIn = g[0].need;
    const gutterIn = GUTTER_FRAC * heightIn;
    const wallIn = WALL_STRIP_FRAC * heightIn;
    const zoneIn = ZONE_FRAC * heightIn;
    const inOrder = [...g].sort((p, q) => p.index - q.index);
    let cursor = 0;
    const items = inOrder.map((p) => {
      const { ext } = p;
      const zoneReserveIn = p.zoned ? zoneIn : 0;
      let item;
      if (!p.turned) {
        // behind the plane: the wall strip, or a hollow deeper than it, then the zone reserve
        const stripIn = Math.max(wallIn, -ext.minX);
        const xIn = cursor + stripIn + zoneReserveIn;
        item = {
          id: p.id,
          index: p.index,
          turned: false,
          xIn,
          heightIn: p.h,
          sizeIn: p.h,
          leftIn: cursor,
          rightIn: xIn + ext.maxX,
          minXIn: ext.minX,
          maxXIn: ext.maxX,
          stripIn,
          zoneReserveIn,
          extentFrom: ext.extentFrom,
        };
      } else {
        // hung from its wall plane: the jamb at the item's left, the plane `planeIn` below the
        // frame's top (the strip and the zone reserve above it), the profile below the plane
        const stripIn = Math.max(wallIn, -ext.minY);
        const planeIn = stripIn + zoneReserveIn;
        item = {
          id: p.id,
          index: p.index,
          turned: true,
          xIn: cursor,
          heightIn: p.h,
          sizeIn: planeIn + Math.max(0, ext.maxY),
          leftIn: cursor,
          rightIn: cursor + p.h,
          planeIn,
          minXIn: ext.minY,
          maxXIn: ext.maxY,
          stripIn,
          zoneReserveIn,
          extentFrom: ext.extentFrom,
        };
      }
      cursor = item.rightIn + gutterIn;
      return item;
    });
    const widthIn = cursor;
    const barIn = scaleBarIn(heightIn);
    const scale = { barIn, words: feetInches16(barIn) };
    if (box && num(box.widthPx) > 0 && num(box.heightPx) > 0) {
      scale.pxPerIn = Math.min(box.widthPx / widthIn, box.heightPx / heightIn);
      scale.barPx = barIn * scale.pxPerIn;
    }
    return { index: fi, heightIn, widthIn, gutterIn, wallIn, zoneIn, items, scale };
  });

  return { frames, unplaced };
}

/* labels: [{ id, y, h? }] (y the desired centre, px) → { labels: [{ id, y, desiredY, h }], overflow }.
   Returned in the input's order. Two neighbours stand at least max(minGapPx, (hA + hB) / 2) apart,
   centre to centre; a label's own `h` defaults to minGapPx. */
export function placeLabels(labels, { minGapPx = 12, top = null, bottom = null } = {}) {
  const src = (Array.isArray(labels) ? labels : []).map((l, i) => ({
    i, id: l && l.id, desiredY: num(l && l.y) ?? 0, h: num(l && l.h) > 0 ? l.h : minGapPx,
  }));
  const sorted = [...src].sort((p, q) => (p.desiredY - q.desiredY) || (p.i - q.i));
  const gap = (a, b) => Math.max(minGapPx, (a.h + b.h) / 2);
  const lo = num(top), hi = num(bottom);

  // a cluster is a run of labels packed at their gaps; `offs` are centres relative to its first
  const clusters = sorted.map((l) => ({ ls: [l], offs: [0] }));
  let overflow = false;
  const place = (c) => {
    const n = c.ls.length;
    let s = c.ls.reduce((acc, l, k) => acc + (l.desiredY - c.offs[k]), 0) / n;
    const span = c.offs[n - 1];
    const min = lo === null ? -Infinity : lo + c.ls[0].h / 2;
    const max = hi === null ? Infinity : hi - c.ls[n - 1].h / 2 - span;
    if (min > max) { overflow = true; s = min; } else s = Math.min(Math.max(s, min), max);
    c.s = s;
  };
  for (;;) {
    overflow = false;
    clusters.forEach(place);
    let merged = false;
    for (let k = 0; k + 1 < clusters.length; k += 1) {
      const a = clusters[k], b = clusters[k + 1];
      const aLast = a.ls[a.ls.length - 1];
      const need = a.s + a.offs[a.offs.length - 1] + gap(aLast, b.ls[0]);
      if (need > b.s + 1e-9) {
        const base = a.offs[a.offs.length - 1] + gap(aLast, b.ls[0]);
        a.ls.push(...b.ls);
        a.offs.push(...b.offs.map((o) => o + base));
        clusters.splice(k + 1, 1);
        merged = true;
        break;
      }
    }
    if (!merged) break;
  }
  const out = new Array(src.length);
  for (const c of clusters) c.ls.forEach((l, k) => { out[l.i] = { id: l.id, y: c.s + c.offs[k], desiredY: l.desiredY, h: l.h }; });
  return { labels: out, overflow };
}
