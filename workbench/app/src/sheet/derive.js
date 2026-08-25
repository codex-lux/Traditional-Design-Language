/* Record + placement → drawable geometry, in the model frame render_plan.py fixed:
   x east, y north, origin at the building's SW corner, units FEET. Every function here
   is a port of build/render_plan.py logic (the _shared edge test, the window spacing,
   the swing direction) so the two renders of the same record cannot quietly disagree.
   Nothing is derived that is not in the record. */

export const WALL_T = 0.75;      // exterior wall thickness drawn (poché band)
export const PART_T = 0.42;      // partition thickness drawn

/* Rooms of one level as rects in model feet. */
export function levelRooms(plan, placement, levelIndex) {
  const byId = new Map();
  for (const r of placement?.rooms || []) {
    if (r.level === levelIndex && r.geometry) byId.set(r.id, r.geometry);
  }
  const lv = (plan.levels || []).find((l) => (l.index ?? 0) === levelIndex);
  if (!lv) return [];
  return lv.rooms
    .filter((r) => byId.has(r.id))
    .map((r) => {
      const g = byId.get(r.id);
      return {
        id: r.id, type: r.type, name: r.name || r.id,
        x: g.x_ft, y: g.y_ft, w: g.width_ft, h: g.depth_ft,
        windows: r.windows || [], doors: r.doors || [],
        exterior_walls: r.exterior_walls || [],
        window_head_ft: r.window_head_ft,
        record: r,
      };
    });
}

/* build/render_plan.py::_shared — where two rooms touch enough for a door. */
export function sharedEdge(a, b, tol = 0.4) {
  if (Math.abs(a.x + a.w - b.x) <= tol || Math.abs(b.x + b.w - a.x) <= tol) {
    const x = Math.abs(a.x + a.w - b.x) <= tol ? b.x : a.x;
    const lo = Math.max(a.y, b.y), hi = Math.min(a.y + a.h, b.y + b.h);
    if (hi - lo > 3.2) return { p: [x, (lo + hi) / 2], horiz: false };
  }
  if (Math.abs(a.y + a.h - b.y) <= tol || Math.abs(b.y + b.h - a.y) <= tol) {
    const y = Math.abs(a.y + a.h - b.y) <= tol ? b.y : a.y;
    const lo = Math.max(a.x, b.x), hi = Math.min(a.x + a.w, b.x + b.w);
    if (hi - lo > 3.2) return { p: [(lo + hi) / 2, y], horiz: true };
  }
  return null;
}

/* Interior partition segments: each room edge not on the footprint boundary, deduped.
   Returned as rects (model feet) centred on the shared line. */
export function partitions(rooms, W, H, tol = 0.6) {
  const segs = [];
  const seen = new Set();
  const key = (x0, y0, x1, y1) =>
    [x0, y0, x1, y1].map((v) => Math.round(v * 4) / 4).join(',');
  for (const r of rooms) {
    const edges = [
      { x0: r.x, y0: r.y + r.h, x1: r.x + r.w, y1: r.y + r.h, horiz: true, boundary: r.y + r.h >= H - tol },
      { x0: r.x, y0: r.y, x1: r.x + r.w, y1: r.y, horiz: true, boundary: r.y <= tol },
      { x0: r.x, y0: r.y, x1: r.x, y1: r.y + r.h, horiz: false, boundary: r.x <= tol },
      { x0: r.x + r.w, y0: r.y, x1: r.x + r.w, y1: r.y + r.h, horiz: false, boundary: r.x + r.w >= W - tol },
    ];
    for (const e of edges) {
      if (e.boundary) continue;
      const k = key(e.x0, e.y0, e.x1, e.y1);
      if (seen.has(k)) continue;
      seen.add(k);
      segs.push(e.horiz
        ? { x: e.x0, y: e.y0 - PART_T / 2, w: e.x1 - e.x0, h: PART_T }
        : { x: e.x0 - PART_T / 2, y: e.y0, w: PART_T, h: e.y1 - e.y0 });
    }
  }
  return segs;
}

/* Windows from the record, spaced along the room's exterior edge exactly as
   build/render_plan.py spaces them: k+1 of n+1 along the wall. */
export function windows(rooms, W, H, tol = 0.6) {
  const out = [];
  for (const r of rooms) {
    for (const win of r.windows) {
      const n = win.count || 1;
      const wallW = win.width_ft || 3;
      for (let k = 0; k < n; k++) {
        const t = (k + 1) / (n + 1);
        if (win.wall === 'S' && r.y <= tol) out.push({ wall: 'S', x: r.x + r.w * t, y: 0, w: wallW });
        else if (win.wall === 'N' && r.y + r.h >= H - tol) out.push({ wall: 'N', x: r.x + r.w * t, y: H, w: wallW });
        else if (win.wall === 'W' && r.x <= tol) out.push({ wall: 'W', x: 0, y: r.y + r.h * t, w: wallW });
        else if (win.wall === 'E' && r.x + r.w >= W - tol) out.push({ wall: 'E', x: W, y: r.y + r.h * t, w: wallW });
      }
    }
  }
  return out;
}

/* Interior doors on shared edges, with the swing into the `to` room (render_plan's
   convention), plus exterior doors as openings on the footprint edge. */
export function doors(rooms, W, H, tol = 0.6) {
  const idx = new Map(rooms.map((r) => [r.id, r]));
  const drawn = new Set();
  const interior = [];
  const exterior = [];
  for (const r of rooms) {
    for (const d of r.doors) {
      if (d.to === 'exterior') {
        // opening on whichever of the room's edges lies on the footprint boundary,
        // preferring the declared exterior walls in order
        const walls = r.exterior_walls.length ? r.exterior_walls : ['S', 'N', 'W', 'E'];
        for (const wl of walls) {
          if (wl === 'S' && r.y <= tol) { exterior.push({ wall: 'S', x: r.x + r.w / 2, y: 0, w: d.width_ft || 3.5 }); break; }
          if (wl === 'N' && r.y + r.h >= H - tol) { exterior.push({ wall: 'N', x: r.x + r.w / 2, y: H, w: d.width_ft || 3.5 }); break; }
          if (wl === 'W' && r.x <= tol) { exterior.push({ wall: 'W', x: 0, y: r.y + r.h / 2, w: d.width_ft || 3.5 }); break; }
          if (wl === 'E' && r.x + r.w >= W - tol) { exterior.push({ wall: 'E', x: W, y: r.y + r.h / 2, w: d.width_ft || 3.5 }); break; }
        }
        continue;
      }
      const to = idx.get(d.to);
      const k = [r.id, d.to].sort().join('|');
      if (!to || drawn.has(k)) continue;
      drawn.add(k);
      const seg = sharedEdge(r, to);
      if (!seg) continue;
      const [px, py] = seg.p;
      if (seg.horiz) {
        interior.push({ x: px, y: py, w: d.width_ft || 3, horiz: true, swingUp: (to.y + to.h / 2) > (r.y + r.h / 2) });
      } else {
        interior.push({ x: px, y: py, w: d.width_ft || 3, horiz: false, swingRight: (to.x + to.w / 2) > (r.x + r.w / 2) });
      }
    }
  }
  return { interior, exterior };
}

/* Vertical bay lines from the footprint's own module. */
export function bayLines(footprint) {
  const W = footprint?.width_ft || 0;
  const bm = footprint?.bay_module_ft || 10;
  const xs = [];
  for (let b = bm; b < W - 0.01; b += bm) xs.push(Math.round(b * 100) / 100);
  return xs;
}

/* Feet-and-inches with primes — never decimal feet in a drawing context. */
export function ft(v) {
  if (typeof v === 'string') return v;
  let whole = Math.floor(v + 1e-9);
  let inches = Math.round((v - whole) * 12);
  if (inches === 12) { whole += 1; inches = 0; }
  return `${whole}′-${inches}″`;
}
