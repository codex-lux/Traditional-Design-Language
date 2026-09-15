/* The furniture key: a numeral on every mark and a key in the room (WP-13.2).

   Until this package a furniture mark on the browser sheet was a rectangle with a <title>
   tooltip -- invisible in print, in a PDF and on the plate Lucas read, where fifty-six of
   fifty-six placed items were unnamed. What a draughtsman does is a numeral on the mark and
   a key. Every item the plate draws takes a small numeral inside its own rectangle (or beside
   it, on the room side, where the rectangle is too thin to hold one), and the room carries a
   KEY: one line per item, the numeral and the item's own name AS RECORDED, whole and never
   abbreviated, in the mono face, in a clear corner of the room. Where no corner holds it at
   the smallest legible size, flat or turned, the key goes to the plate's caption under the
   room's name, and that is a refusal the caption states rather than a silence.

   This is the port of build/render_plan.py's `furniture_key_plan` and its helpers, the same
   arithmetic in FEET rather than sheet px, so both sheets name the same items and refuse the
   same keys. The sizes are the Python sheet's px floors stated at the standard's own
   `--px-per-ft` of 13 (tokens.css), because a floor of legibility is a property of the
   printed plate and the browser sheet is the same plate in model units. A LEAF: it imports
   nothing, so `node --test` can hold it to the Python side without a bundle or a browser. */

export const PX_PER_FT = 13;
export const KEY = {
  preferred: 6.0 / PX_PER_FT,    // never larger than a room name at its own floor
  floor: 4.6 / PX_PER_FT,        // the smallest lettering the Python sheet sets (the void tail)
  lead: 1.25,
  pad: 3.0 / PX_PER_FT,          // air between the key and the wall body, and other ink
  numeral: 5.5 / PX_PER_FT,      // the numeral on the mark
  pushStates: 48,                // how far a key may be pushed off its corner (positions tried)
};
const MONO_EM = 0.6;             // Courier Prime's advance, the same estimate render_plan uses

export function monoWidth(text, size) { return MONO_EM * String(text).length * size; }

const COUNT_WORDS = { two: 2, three: 3, four: 4, five: 5, six: 6, seven: 7, eight: 8,
                      nine: 9, ten: 10, eleven: 11, twelve: 12 };

/* A count the RECORD states in an item's own name, read by a closed rule and never guessed:
   'pair' is two; a name opening with a number word or a numeral is that many, unless it
   states a band ('six to eight side chairs') or joins a second item ('two chairs and a
   table'). null is unjudged and never one. The key line carries the name whole, so the
   record's own words reach the reader whatever this returns. */
export function keyCount(name) {
  const words = String(name || '').toLowerCase().split(/\s+/)
    .map((w) => w.replace(/^[,.;:()/'"]+|[,.;:()/'"]+$/g, '')).filter(Boolean);
  if (!words.length) return null;
  if (words.includes('pair')) return 2;
  if (words.includes('to') || words.includes('and')) return null;
  if (words[0] in COUNT_WORDS) return COUNT_WORDS[words[0]];
  if (/^\d+$/.test(words[0])) return parseInt(words[0], 10);
  return null;
}

/* Every mark this plate draws in `room`, numbered in drawing order -- the wet fixtures first,
   then the furniture. An unplaced fixture and a furniture entry with no marks are not on the
   plate and take no numeral. Rooms are `derive.js::levelRooms` rooms (model feet). */
export function keyEntries(room) {
  const out = [];
  let n = 0;
  for (const f of room.fixture_layout || []) {
    if (f.unplaced || f.x_ft == null) continue;
    n += 1;
    out.push({ n, item: f.item, kind: 'fixture', wall: f.wall || null,
               rect: { x: f.x_ft, y: f.y_ft, w: f.width_ft, h: f.depth_ft } });
  }
  for (const f of room.furniture_layout || []) {
    if (!f.marks || !f.marks.length) continue;
    n += 1;
    out.push({ n, item: f.item, kind: 'furniture', wall: f.wall || null,
               rect: { x: f.x_ft, y: f.y_ft, w: f.width_ft, h: f.depth_ft } });
  }
  return out;
}

/* One line per entry: the numeral and the item's name as recorded, whitespace normalised,
   in capitals like everything lettered on the sheet. Never abbreviated. */
export function keyLines(entries) {
  return entries.map((e) => `${e.n} ${String(e.item).trim().split(/\s+/).join(' ').toUpperCase()}`);
}

export function blockSize(lines, size, lead = KEY.lead) {
  return [Math.max(...lines.map((l) => monoWidth(l, size))), lines.length * size * lead];
}

const hits = (b, o, pad) => b[0] < o[2] + pad && b[2] > o[0] - pad && b[1] < o[3] + pad && b[3] > o[1] - pad;

export function isClear(box, obstacles, pad) {
  return !obstacles.some((o) => hits(box, o, pad));
}

/* The room's box less the wall bodies drawn on its edges (the partitions, centred on the
   shared line and taking half their thickness from this room). Each side shrinks by the
   deepest strip intruding on it; a strip is a wall on the left or right when it is a thin
   VERTICAL strip and on the top or bottom when horizontal -- decided by its own shape,
   because a band along the top of a room also crosses its left edge. */
export function clearFloor(box, bands) {
  const [x0, y0, x1, y1] = box;
  let left = 0, right = 0, top = 0, bottom = 0;
  for (const [bx0, by0, bx1, by1] of bands) {
    const ox0 = Math.max(bx0, x0), oy0 = Math.max(by0, y0), ox1 = Math.min(bx1, x1), oy1 = Math.min(by1, y1);
    if (ox1 <= ox0 || oy1 <= oy0) continue;
    if (ox1 - ox0 < oy1 - oy0) {
      if (ox0 <= x0 + 1e-9) left = Math.max(left, ox1 - x0);
      if (ox1 >= x1 - 1e-9) right = Math.max(right, x1 - ox0);
    } else {
      if (oy0 <= y0 + 1e-9) top = Math.max(top, oy1 - y0);
      if (oy1 >= y1 - 1e-9) bottom = Math.max(bottom, y1 - oy0);
    }
  }
  return [x0 + left, y0 + top, x1 - right, y1 - bottom];
}

/* The nearest clear position to `corner` for a bw x bh block, pushed inward past the
   obstacles in its way, or null. Returns [x0, y0, distance]. */
export function place(corner, bw, bh, floor, obstacles, pad, states = KEY.pushStates) {
  const [rx0, ry0, rx1, ry1] = floor;
  const sx = corner[1] === 'W' ? 1 : -1;
  const sy = corner[0] === 'N' ? 1 : -1;
  const start = [sx > 0 ? rx0 : rx1 - bw, sy > 0 ? ry0 : ry1 - bh];
  const key = (p) => `${p[0].toFixed(4)},${p[1].toFixed(4)}`;
  const seen = new Set([key(start)]);
  const frontier = [start];
  let tried = 0;
  while (frontier.length && tried < states) {
    frontier.sort((a, b) => (Math.abs(a[0] - start[0]) + Math.abs(a[1] - start[1]))
                          - (Math.abs(b[0] - start[0]) + Math.abs(b[1] - start[1])));
    const [x0, y0] = frontier.shift();
    tried += 1;
    if (x0 < rx0 - 1e-9 || y0 < ry0 - 1e-9 || x0 + bw > rx1 + 1e-9 || y0 + bh > ry1 + 1e-9) continue;
    const box = [x0, y0, x0 + bw, y0 + bh];
    const hit = obstacles.find((o) => hits(box, o, pad));
    if (!hit) return [x0, y0, Math.abs(x0 - start[0]) + Math.abs(y0 - start[1])];
    const nx = sx > 0 ? hit[2] + pad : hit[0] - pad - bw;
    const ny = sy > 0 ? hit[3] + pad : hit[1] - pad - bh;
    for (const cand of [[nx, y0], [x0, ny]]) {
      const k = key(cand);
      if (!seen.has(k)) { seen.add(k); frontier.push(cand); }
    }
  }
  return null;
}

/* Where a room's key goes -- or null, a refusal the caller must state. `floor` is the room's
   clear floor [x0, y0, x1, y1] in room-local feet, y DOWN; obstacles are boxes in the same
   frame. Every size from the preferred down to the floor, four corners each pushed inward,
   nearest clear place at the largest size; TURNED only where it earns a materially larger
   letter or nothing flat fits -- the room labels' own rule. */
export function fitKey(floor, obstacles, lines, opt = {}) {
  const { preferred = KEY.preferred, floor: min = KEY.floor, lead = KEY.lead, pad = KEY.pad } = opt;
  const rx0 = floor[0] + pad, ry0 = floor[1] + pad, rx1 = floor[2] - pad, ry1 = floor[3] - pad;
  if (rx1 <= rx0 || ry1 <= ry0 || !lines.length) return null;
  const step = 0.2 / PX_PER_FT;
  const steps = Math.round((preferred - min) / step);
  const sizes = Array.from({ length: steps + 1 }, (_, k) => preferred - step * k);
  const attempt = (turned) => {
    for (const size of sizes) {
      let [bw, bh] = blockSize(lines, size, lead);
      if (turned) [bw, bh] = [bh, bw];
      if (bw > rx1 - rx0 || bh > ry1 - ry0) continue;
      let best = null;
      for (const corner of ['NW', 'NE', 'SW', 'SE']) {
        const got = place(corner, bw, bh, [rx0, ry0, rx1, ry1], obstacles, pad);
        if (got && (!best || got[2] < best.got[2])) best = { corner, got };
      }
      if (best) {
        const [x0, y0] = best.got;
        return { corner: best.corner, turned, size, x0, y0, x1: x0 + bw, y1: y0 + bh };
      }
    }
    return null;
  };
  const flat = attempt(false);
  const turned = attempt(true);
  if (turned && (!flat || turned.size > flat.size * 1.15)) return turned;
  return flat;
}

/* Where an item's numeral goes: inside its own rectangle where that can hold it, else beside
   it on the room side -- off the wall it was seated against, or above a freestanding one. A
   numeral that would land on `avoid` (the room's label) goes beside instead where a clear
   side exists; a beside-numeral that would leave the room takes the opposite side.
   Returns { x, y, anchor, size, box }. */
export function numeralAt(itemBox, wallSide, n, roomBox, size = KEY.numeral, avoid = []) {
  const [x0, y0, x1, y1] = itemBox;
  const dw = monoWidth(String(n), size);
  const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
  let inside = null;
  if (x1 - x0 >= dw + 2 / PX_PER_FT && y1 - y0 >= size + 1 / PX_PER_FT) {
    inside = { x: cx, y: cy + 0.35 * size, anchor: 'middle', size,
               box: [cx - dw / 2, cy - 0.5 * size, cx + dw / 2, cy + 0.5 * size] };
    if (isClear(inside.box, avoid, 0)) return inside;
  }
  const pad = 1.5 / PX_PER_FT;
  const below = () => { const by = y1 + pad + 0.75 * size;
    return { x: cx, y: by, anchor: 'middle', size, box: [cx - dw / 2, y1 + pad, cx + dw / 2, by + 0.25 * size] }; };
  const above = () => { const by = y0 - pad - 0.25 * size;
    return { x: cx, y: by, anchor: 'middle', size, box: [cx - dw / 2, by - 0.75 * size, cx + dw / 2, y0 - pad] }; };
  const right = () => ({ x: x1 + pad, y: cy + 0.35 * size, anchor: 'start', size,
    box: [x1 + pad, cy - 0.5 * size, x1 + pad + dw, cy + 0.5 * size] });
  const left = () => ({ x: x0 - pad, y: cy + 0.35 * size, anchor: 'end', size,
    box: [x0 - pad - dw, cy - 0.5 * size, x0 - pad, cy + 0.5 * size] });
  const order = { N: [below, above], S: [above, below], W: [right, left], E: [left, right] }[wallSide]
    || [above, below];
  const [rx0, ry0, rx1, ry1] = roomBox;
  for (const cand of order) {
    const c = cand();
    const [bx0, by0, bx1, by1] = c.box;
    if (bx0 >= rx0 && by0 >= ry0 && bx1 <= rx1 && by1 <= ry1 && isClear(c.box, avoid, 0)) return c;
  }
  return inside || order[0]();
}

const toBox = (r) => [r.x, r.y, r.x + r.w, r.y + r.h];

/* Every room's key on one level, fitted or refused. `opt.partitions`, `opt.swings` and
   `opt.stairRects` are {x, y, w, h} in MODEL feet (y up); `opt.labelBox(room)` returns the
   room label's ink extent {w, h} in feet, already swapped where the label is turned, or null.
   Returns { byRoom: Map(id -> {entries, lines, numerals, fit}), margin: [{id, name, lines}] },
   everything in the ROOM'S OWN frame -- feet from its NW corner, y down -- so the plate adds
   the room's corner and nothing else. */
export function furnitureKeyPlan(rooms, opt = {}) {
  const partitions = (opt.partitions || []).map(toBox);
  const swings = (opt.swings || []).map(toBox);
  const stairRects = (opt.stairRects || []).map(toBox);
  const byRoom = new Map();
  const margin = [];
  for (const r of rooms) {
    const entries = keyEntries(r);
    if (!entries.length) continue;
    // model (x0, y0, x1, y1) -> room-local, y down from the room's NW corner
    const loc = ([mx0, my0, mx1, my1]) => [mx0 - r.x, r.y + r.h - my1, mx1 - r.x, r.y + r.h - my0];
    const roomBox = [0, 0, r.w, r.h];
    const obstacles = entries.map((e) => loc(toBox(e.rect)));
    for (const s of stairRects) obstacles.push(loc(s));
    for (const s of swings) obstacles.push(loc(s));
    const floor = clearFloor(roomBox, partitions.map(loc));
    const lab = opt.labelBox ? opt.labelBox(r) : null;
    const labelBox = [];
    if (lab) {
      const cx = r.w / 2, cy = r.h / 2;
      labelBox.push([cx - lab.w / 2, cy - lab.h / 2, cx + lab.w / 2, cy + lab.h / 2]);
      obstacles.push(labelBox[0]);
    }
    const numerals = entries.map((e) => {
      const nu = numeralAt(loc(toBox(e.rect)), e.wall, e.n, roomBox, KEY.numeral, labelBox);
      obstacles.push(nu.box);
      return { n: e.n, ...nu };
    });
    const lines = keyLines(entries);
    const fit = fitKey(floor, obstacles, lines);
    byRoom.set(r.id, { entries, lines, numerals, fit });
    if (!fit) margin.push({ id: r.id, name: (r.name || r.id).toUpperCase(), lines });
  }
  return { byRoom, margin };
}
