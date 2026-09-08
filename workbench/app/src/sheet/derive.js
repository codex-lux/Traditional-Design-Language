/* Record + placement → drawable geometry, in the model frame render_plan.py fixed:
   x east, y north, origin at the building's SW corner, units FEET. Every function here
   is a port of build/render_plan.py logic (the _shared edge test, the window spacing,
   the swing direction) so the two renders of the same record cannot quietly disagree.
   Nothing is derived that is not in the record.

   WP-6.1. Three rules changed here, and all three were the sheet telling a lie:

   (i) A door used to need 3.2 ft of shared wall to be DRAWN while the solver would prove
   one on 2 ft, so a closet door held as a fact and appeared in no drawing (OQ 41/63).
   The test is now the leaf plus its own jambs, which is what a door actually occupies —
   a closet door IS narrower than a parlour's.

   (ii) A door that could not be drawn was `continue`d over in silence. Every one of them
   now leaves by `undrawable`, with the reason, and the sheet prints it. The DXF exporter
   has stated this since WP-5.1 and the SVG sheet did not, which is how a kitchen with
   five declared interior doors could be drawn with none of them.

   (iii) Windows were spaced without looking at the doors, so an exterior door and a
   single window both landed on the wall midpoint and the window — a filled rect — was
   painted over the door. On the shipped Tidewater sheet that happened twice, at the
   front door of the centre passage and the kitchen's back door. Openings now share a
   wall by rule: doors take their position first, windows are distributed into what is
   left, and a window with nowhere to go is reported rather than drawn on top. */

/* THE WALL COMES FROM THE RECORD, AND THESE TWO ARE WHAT IT REPLACED.

   `WALL_T = 0.75` and `PART_T = 0.42` were literals — 9 in of envelope and 5 in of
   partition, a house convention rather than a reading, and matching NO assembly in
   `construction/wall-assemblies.json`. The Tidewater plan declares `solid-masonry-two-wythe`,
   which is 15.5 in and 4.5 in; the spec Colonial declares nothing and takes platform frame's
   8 in and 4.5 in, which the sheet has to SAY rather than assume.

   `build/openings.py::place` writes `footprint.wall` (plan schema 0.5.1) from
   `build/assemblies.py::wall_thickness`, which reads the plan's own
   `declared.construction_type`. `wallOf()` below is the one reader.

   The fallback is kept and is NOT silent: a record placed before 0.5.1 carries no assembly,
   and a sheet that quietly drew 9 in on it would be inventing the thing this change removed.
   `wallOf` returns `stated: false` and the plate says so. */
export const WALL_FALLBACK = { exterior_ft: 0.75, bearing_ft: 0.55, partition_ft: 0.42 };

export function wallOf(footprint) {
  const w = (footprint || {}).wall;
  if (!w || !(w.exterior_in > 0)) return { ...WALL_FALLBACK, stated: false, note: null };
  return {
    exterior_ft: w.exterior_in / 12,
    bearing_ft: (w.bearing_interior_in || w.exterior_in) / 12,
    partition_ft: (w.partition_in || w.exterior_in) / 12,
    stated: true,
    type: w.construction_type,
    note: w.note || null,
  };
}

/* Kept so a caller that has no placement still has a number, and so `partitions()` keeps its
   old signature. Every DRAWN thickness goes through `wallOf`. */
export const WALL_T = WALL_FALLBACK.exterior_ft;
export const PART_T = WALL_FALLBACK.partition_ft;

/* The reveal either side of a leaf. A door is not its leaf: it is the leaf, the jambs it
   hangs in and the lining round them, and a wall run that cannot hold all three cannot
   hold the door. Kept in step with build/render_plan.py and (WP-6.3) with the solver's
   own floor, so the drawing and the proof can never again disagree about what fits. */
export const JAMB_FT = 0.35;
/* Masonry between two openings on one wall. A geometric floor only — the corpus states
   this properly (sash-light's `minimum_solid_between_openings` is opening_width * 1.4)
   and reading it is WP-6.2's job, not this pass's. */
export const MIN_SOLID_FT = 1.0;
/* Used when a door carries no width. Composed plans carry none at all today
   (build/compose.py writes {"to": id} and nothing else), so this is most doors on a
   generated sheet; it is flagged so the caption can say how many. */
export const DEFAULT_DOOR_FT = 3.0;
export const DEFAULT_EXT_DOOR_FT = 3.5;

export function requiredWallFt(widthFt) { return widthFt + 2 * JAMB_FT; }

/* Rooms of one level as rects in model feet. */
export function levelRooms(plan, placement, levelIndex) {
  // The PLACED room record, where there is one. This is the distinction the sheet was
  // missing: `plan` is the record the client holds and has never been placed, while the
  // placement carries the same rooms with build/openings.py's walls, positions and fixture
  // layouts written onto them. Reading openings off `plan` meant the workbench went on
  // inventing every position from an unplaced record while the placement sat beside it
  // holding the answer.
  const byId = new Map();
  const placedRec = new Map();
  for (const r of placement?.rooms || []) {
    if (r.level === levelIndex && r.geometry) {
      byId.set(r.id, r.geometry);
      placedRec.set(r.id, r);
    }
  }
  // the placement may also arrive as the plan itself, with geometry written onto the
  // rooms in place (build/geometry.py::write_record does exactly that)
  for (const lv of placement?.levels || []) {
    if ((lv.index ?? 0) !== levelIndex) continue;
    for (const r of lv.rooms || []) {
      if (r.geometry) { byId.set(r.id, r.geometry); placedRec.set(r.id, r); }
    }
  }
  const lv = (plan.levels || []).find((l) => (l.index ?? 0) === levelIndex);
  if (!lv) return [];
  return lv.rooms
    .filter((r) => byId.has(r.id))
    .map((r) => {
      const g = byId.get(r.id);
      const p = placedRec.get(r.id) || {};
      return {
        id: r.id, type: r.type, name: r.name || r.id,
        x: g.x_ft, y: g.y_ft, w: g.width_ft, h: g.depth_ft,
        windows: p.windows || r.windows || [],
        doors: p.doors || r.doors || [],
        fixture_layout: p.fixture_layout || r.fixture_layout || [],
        furniture_layout: p.furniture_layout || r.furniture_layout || [],
        exterior_walls: r.exterior_walls || [],
        window_head_ft: r.window_head_ft,
        declared_width_ft: r.width_ft, declared_length_ft: r.length_ft,
        record: r,
      };
    });
}

/* build/render_plan.py::_shared — where two rooms touch, and over how much run.
   Returns the whole shared extent; whether it is ENOUGH is the caller's question now,
   because the answer depends on the door's own width. */
export function sharedEdge(a, b, tol = 0.4) {
  if (Math.abs(a.x + a.w - b.x) <= tol || Math.abs(b.x + b.w - a.x) <= tol) {
    const x = Math.abs(a.x + a.w - b.x) <= tol ? b.x : a.x;
    const lo = Math.max(a.y, b.y), hi = Math.min(a.y + a.h, b.y + b.h);
    if (hi > lo) return { horiz: false, at: x, lo, hi, run: hi - lo };
  }
  if (Math.abs(a.y + a.h - b.y) <= tol || Math.abs(b.y + b.h - a.y) <= tol) {
    const y = Math.abs(a.y + a.h - b.y) <= tol ? b.y : a.y;
    const lo = Math.max(a.x, b.x), hi = Math.min(a.x + a.w, b.x + b.w);
    if (hi > lo) return { horiz: true, at: y, lo, hi, run: hi - lo };
  }
  return null;
}

/* Interior partition segments: each room edge not on the footprint boundary, deduped.
   Returned as rects (model feet) centred on the shared line. */
export function partitions(rooms, W, H, tol = 0.6, t = PART_T) {
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
        ? { x: e.x0, y: e.y0 - t / 2, w: e.x1 - e.x0, h: t }
        : { x: e.x0 - t / 2, y: e.y0, w: t, h: e.y1 - e.y0 });
    }
  }
  return segs;
}

/* Which boundary wall of the footprint a room's edge lies on, for the walls it declares. */
/* WP-11.14. `box` is [x, y, W, H] of the massing element this room stands in; without one the
   footprint is the element, which is what every plan in the corpus is. `at` is the coordinate
   ACROSS the wall and it has always been returned here -- both callers below ignored it and
   recomputed `0`/`W`/`H` inline, so an opening on a dependency's face was drawn on the main
   block's. build/render_plan.py::_boundary_wall is the twin and takes `box` in the same place. */
function boundaryWall(r, wall, W, H, tol, box) {
  const [bx, by, bW, bH] = box || [0, 0, W, H];
  if (wall === 'S' && r.y <= by + tol) return { wall: 'S', lo: r.x, hi: r.x + r.w, at: by };
  if (wall === 'N' && r.y + r.h >= by + bH - tol) return { wall: 'N', lo: r.x, hi: r.x + r.w, at: by + bH };
  if (wall === 'W' && r.x <= bx + tol) return { wall: 'W', lo: r.y, hi: r.y + r.h, at: bx };
  if (wall === 'E' && r.x + r.w >= bx + bW - tol) return { wall: 'E', lo: r.y, hi: r.y + r.h, at: bx + bW };
  return null;
}

/* Where an EXTERIOR opening in this room's wall is drawn across the wall: the element's own
   face where the element is known, the room's otherwise. The twin of _edge_of in
   build/render_plan.py, and the same ordering for the same reason -- the exterior wall is
   drawn outward from the element's edge, and a boundary room may sit a tolerance inside it. */
// ROUNDED TO 3 dp, BECAUSE THE PYTHON SPELLING IS. `render_plan.py` writes every `edge_ft`
// through `round(edge, 3)` and this file wrote the raw float, so a room set back a non-binary
// fraction from its element face gave 32.6 in one renderer and 32.599999999999994 in the other
// -- two answers to the question WP-11.14 exists to make them answer once. Found by a guard
// written for a different gap, in the audit of that package. On every shipped plan the edge is
// 0/W/H exactly and this is the identity.
function edge3(v) { return Math.round(v * 1000) / 1000; }

function edgeOf(r, wall, box) {
  if (box) {
    const [bx, by, bW, bH] = box;
    return wall === 'S' ? by : wall === 'N' ? by + bH : wall === 'W' ? bx : bx + bW;
  }
  return wall === 'S' ? r.y : wall === 'N' ? r.y + r.h : wall === 'W' ? r.x : r.x + r.w;
}

/* Subtract the blocked spans from [lo, hi]. */
function freeIntervals(lo, hi, blocked) {
  let free = [[lo, hi]];
  for (const [a, b] of blocked) {
    const next = [];
    for (const [s, e] of free) {
      if (b <= s || a >= e) { next.push([s, e]); continue; }
      if (a > s) next.push([s, Math.min(a, e)]);
      if (b < e) next.push([Math.max(b, s), e]);
    }
    free = next;
  }
  return free.filter(([s, e]) => e - s > 1e-6);
}

/* Distribute n openings of width `unitW` into the free run, evenly over the space that
   can actually hold them — the k+1 of n+1 spacing render_plan.py has always used, but
   measured against what is LEFT after the doors rather than against the whole wall.
   Returns the positions it could place; the caller reports the shortfall. */
function distribute(free, n, unitW) {
  const centres = free
    .map(([s, e]) => [s + unitW / 2, e - unitW / 2])
    .filter(([s, e]) => e - s >= -1e-9);
  if (!centres.length) return [];
  const total = centres.reduce((t, [s, e]) => t + Math.max(0, e - s), 0);
  const out = [];
  for (let k = 0; k < n; k++) {
    const t = total * ((k + 1) / (n + 1));
    let acc = 0, pos = centres[0][0];
    for (const [s, e] of centres) {
      const len = Math.max(0, e - s);
      if (t <= acc + len + 1e-9) { pos = s + (t - acc); break; }
      acc += len;
    }
    out.push(pos);
  }
  // two openings may not occupy the same masonry: keep those that clear the last kept one
  const kept = [];
  for (const p of out) {
    if (!kept.length || p - kept[kept.length - 1] >= unitW + MIN_SOLID_FT - 1e-9) kept.push(p);
  }
  return kept;
}

/* Interior doors on shared edges, with the swing into the `to` room (render_plan's
   convention), plus exterior doors as openings on the footprint edge.

   Returns `undrawable` beside them: every declared door this placement gives no way to
   draw, with the reason, so the sheet can say so. It is never empty quietly. */
/* Where the RECORD says an opening is. Since plan schema 0.3.0 (WP-6.2) build/openings.py
   writes a wall and a centreline onto every opening it can place, and a renderer that reads
   them draws the plan rather than guessing a plan of its own. Null means the record is
   silent — a hand-authored 0.2.0 record — and the caller invents as it always did. */
const WALLS = new Set(['N', 'E', 'S', 'W']);
function placedAt(d) {
  if (!WALLS.has(d.wall) || d.position_ft == null) return null;
  return { wall: d.wall, pos: Number(d.position_ft) };
}

/* WP-11.10. `appendages` is `[{id, x, y, w, h}]` for the at-grade appendages placed OUTSIDE
   the block on this level -- a terrace, today. Their rooms carry no geometry (that is the whole
   mechanism of the ruling; see build/appendages.py), so the lookup below found nothing and
   called a door the record says is SEATED "the other room is not placed on this level": the
   record and the sheet holding two answers about one door, which is WP-6.1's own finding.
   `build/render_plan.py::derive_openings` takes the same argument in the same place. */
export function doors(rooms, W, H, tol = 0.6, appendages = null, bounds = null) {
  const idx = new Map(rooms.map((r) => [r.id, r]));
  for (const a of appendages || []) if (!idx.has(a.id)) idx.set(a.id, a);
  const handled = new Set();
  const interior = [];
  const exterior = [];
  const undrawable = [];
  let inferredWidths = 0;
  let inferredPositions = 0;
  for (const r of rooms) {
    const usedWalls = new Set();
    for (const d of r.doors) {
      const isExt = d.to === 'exterior';
      const declaredW = d.width_ft;
      const width = declaredW || (isExt ? DEFAULT_EXT_DOOR_FT : DEFAULT_DOOR_FT);
      if (declaredW == null) inferredWidths += 1;
      const type = d.type || 'swing';
      // an opening the placement pass could not seat says so in the record, and the
      // drawing repeats it rather than quietly leaving a wall blank
      if (d.unplaced) {
        const k = [r.id, d.to].sort().join('|');
        if (!isExt) {
          if (handled.has(k)) continue;
          handled.add(k);
        }
        undrawable.push({ from: r.id, to: d.to, width_ft: width, type,
          reason: d.unplaced.reason });
        continue;
      }
      const seat = placedAt(d);
      if (isExt && seat) {
        usedWalls.add(seat.wall);
        // WP-11.14: across the wall from the ROOM's own element, not from the footprint. The
        // interior branch below has always taken its `at` from the room's rectangle; this one
        // took `0`/`W`/`H`, and on a plan with a dependency it drew the door in open space.
        const edge = edgeOf(r, seat.wall, (bounds || {})[r.id]);
        exterior.push({
          wall: seat.wall, w: width, type, room: r.id, inferredWall: false,
          inferredWidth: declaredW == null, edge_ft: edge3(edge),
          span: [seat.pos - width / 2, seat.pos + width / 2],
          x: seat.wall === 'W' || seat.wall === 'E' ? edge : seat.pos,
          y: seat.wall === 'S' || seat.wall === 'N' ? edge : seat.pos,
        });
        continue;
      }
      if (!isExt && seat) {
        const k = [r.id, d.to].sort().join('|');
        if (handled.has(k)) continue;
        handled.add(k);
        const to = idx.get(d.to);
        if (!to) {
          undrawable.push({ from: r.id, to: d.to, width_ft: width, type,
            reason: 'the other room is not placed on this level' });
          continue;
        }
        const horiz = seat.wall === 'N' || seat.wall === 'S';
        const at = seat.wall === 'N' ? r.y + r.h
          : seat.wall === 'S' ? r.y
            : seat.wall === 'E' ? r.x + r.w : r.x;
        if (horiz) {
          interior.push({ x: seat.pos, y: at, w: width, type, horiz: true,
            swingUp: (to.y + to.h / 2) > (r.y + r.h / 2), pair: [r.id, d.to] });
        } else {
          interior.push({ x: at, y: seat.pos, w: width, type, horiz: false,
            swingRight: (to.x + to.w / 2) > (r.x + r.w / 2), pair: [r.id, d.to] });
        }
        continue;
      }
      inferredPositions += 1;
      if (isExt) {
        // the record does not say WHICH wall an exterior door is on (there is no field
        // for it until WP-6.2), so the wall is inferred: the first declared exterior
        // wall this placement actually put on the boundary. `usedWalls` stops a second
        // exterior door landing on top of the first, which the old loop did.
        const walls = r.exterior_walls.length ? r.exterior_walls : ['S', 'N', 'W', 'E'];
        let seat = null;
        for (const wl of walls) {
          if (usedWalls.has(wl)) continue;
          const b = boundaryWall(r, wl, W, H, tol, (bounds || {})[r.id]);
          if (b) { seat = b; break; }
        }
        if (!seat) {
          undrawable.push({ from: r.id, to: 'exterior', width_ft: width, type,
            reason: 'no declared exterior wall of this room is on its own '
              + "massing element's boundary here" });
          continue;
        }
        usedWalls.add(seat.wall);
        const mid = (seat.lo + seat.hi) / 2;
        exterior.push({
          wall: seat.wall, w: width, type, room: r.id, inferredWall: true,
          inferredWidth: declaredW == null, edge_ft: edge3(seat.at),
          span: [mid - width / 2, mid + width / 2],
          x: seat.wall === 'W' || seat.wall === 'E' ? seat.at : mid,
          y: seat.wall === 'S' || seat.wall === 'N' ? seat.at : mid,
        });
        continue;
      }
      const to = idx.get(d.to);
      const k = [r.id, d.to].sort().join('|');
      if (handled.has(k)) continue;
      handled.add(k);
      if (!to) {
        undrawable.push({ from: r.id, to: d.to, width_ft: width, type,
          reason: 'the other room is not placed on this level' });
        continue;
      }
      const seg = sharedEdge(r, to);
      if (!seg) {
        undrawable.push({ from: r.id, to: d.to, width_ft: width, type,
          reason: 'the placement leaves these two rooms no shared wall' });
        continue;
      }
      const need = requiredWallFt(width);
      if (seg.run < need) {
        undrawable.push({ from: r.id, to: d.to, width_ft: width, type,
          reason: `they share ${seg.run.toFixed(1)} ft; this leaf and its jambs need ${need.toFixed(1)} ft` });
        continue;
      }
      const mid = (seg.lo + seg.hi) / 2;
      if (seg.horiz) {
        interior.push({ x: mid, y: seg.at, w: width, type, horiz: true,
          swingUp: (to.y + to.h / 2) > (r.y + r.h / 2), pair: [r.id, d.to] });
      } else {
        interior.push({ x: seg.at, y: mid, w: width, type, horiz: false,
          swingRight: (to.x + to.w / 2) > (r.x + r.w / 2), pair: [r.id, d.to] });
      }
    }
  }
  return { interior, exterior, undrawable, inferredWidths, inferredPositions };
}

/* Windows from the record, distributed along the room's exterior wall into the run the
   doors have left. `extDoors` is doors().exterior — pass it, or the two passes will put
   an opening in the same masonry twice (which is exactly what used to happen). */
export function windows(rooms, W, H, tol = 0.6, extDoors = [], bounds = null) {
  const out = [];
  let offFootprint = 0;      // the solver put this room on no such boundary wall
  let crowded = 0;           // the wall has no clear run left beside its doors
  const blockedBy = new Map();
  for (const d of extDoors) {
    const key = `${d.room}|${d.wall}`;
    const arr = blockedBy.get(key) || [];
    arr.push([d.span[0] - MIN_SOLID_FT, d.span[1] + MIN_SOLID_FT]);
    blockedBy.set(key, arr);
  }
  for (const r of rooms) {
    for (const win of r.windows) {
      const n = win.count || 1;
      const wallW = win.width_ft || 3;
      const seat = boundaryWall(r, win.wall, W, H, tol, (bounds || {})[r.id]);
      if (!seat) { offFootprint += n; continue; }
      let pos;
      if (win.positions_ft && win.positions_ft.length) {
        // the record carries one centreline per unit; read them, do not re-space them
        pos = win.positions_ft.map(Number);
        crowded += Math.max(0, n - pos.length);
      } else {
        const free = freeIntervals(seat.lo, seat.hi, blockedBy.get(`${r.id}|${win.wall}`) || []);
        pos = distribute(free, n, wallW);
        crowded += n - pos.length;
      }
      for (const p of pos) {
        out.push({
          // WP-11.14: `seat.at` is the room's own element's face. It was already being
          // returned and both callers here threw it away for `0`/`W`/`H`.
          wall: seat.wall, w: wallW, room: r.id, edge_ft: edge3(seat.at),
          x: seat.wall === 'W' || seat.wall === 'E' ? seat.at : p,
          y: seat.wall === 'S' || seat.wall === 'N' ? seat.at : p,
        });
      }
    }
  }
  out.dropped = offFootprint;      // kept: the caption has said this since WP-5.2
  out.offFootprint = offFootprint;
  out.crowded = crowded;
  return out;
}

/* Which of a room's declared window-walls the placement actually put on the footprint
   boundary — the daylight overlay must agree with the DRAWN windows, not the declared
   list, or the overlay and the drawing contradict each other on the same sheet. */
export function litWalls(r, W, H, tol = 0.6, box = null) {
  const walls = new Set((r.windows || []).map((w) => w.wall));
  const out = [];
  for (const wl of ['S', 'N', 'W', 'E']) {
    // WP-11.14: the room's own element, so the overlay agrees with the drawn windows on a
    // multi-element plan too -- which is the reason this function reads `boundaryWall` at all.
    if (walls.has(wl) && boundaryWall(r, wl, W, H, tol, box)) out.push(wl);
  }
  return out;
}

/* Rooms drawn at a materially different size from the one the record declares.
   The sheet prints the PLACED rectangle — it must, it is what was drawn — and until
   now said nothing about the declaration it departs from, so a kitchen declared
   16 × 20 and drawn at 63% of that area read as a measured fact. */
export function divergence(rooms, tolFt = 0.5) {
  const out = [];
  for (const r of rooms) {
    const dw = r.declared_width_ft, dl = r.declared_length_ft;
    if (!dw || !dl) continue;
    const short = Math.min(r.w, r.h), long = Math.max(r.w, r.h);
    const dShort = Math.min(dw, dl), dLong = Math.max(dw, dl);
    if (Math.abs(short - dShort) <= tolFt && Math.abs(long - dLong) <= tolFt) continue;
    const da = dw * dl, pa = r.w * r.h;
    out.push({ id: r.id, name: r.name, declared_sf: da, placed_sf: pa,
               pct: da ? ((pa - da) / da) * 100 : 0 });
  }
  out.sort((a, b) => Math.abs(b.pct) - Math.abs(a.pct));
  return out;
}

/* Where a relaxation mark may be drawn — and, just as important, where it may not.

   A relaxation is one wall line that missed the structural bay. The heuristic records the
   cut it made, so the mark has a `from_ft`/`to_ft` extent and is drawn along it. The CP
   engine records only the line, and the sheet used to draw such a mark as a 5 ft tick
   CENTRED ON THE PLAN — which is how, on the Tidewater placement, a dashed tick and a
   triangle came to sit in the middle of the drawing room with no wall under either. That
   is the "arrows over walls between spaces … they seem to point to anything and
   everything" of Lucas's review: the mark was not over a wall at all.

   `runs` (geometry_cp.py) is the measured answer — the room faces that actually lie on
   that line, as disjoint intervals. A mark with runs is drawn along them. A mark with
   neither extent nor runs is NOT drawn: it is returned in `unlocated` for the caption to
   name. Guessing a position for it would be the same error in a smaller place. */
export function relaxationMarks(marks, levelIndex, W, H) {
  const drawn = [], unlocated = [];
  for (const m of (marks || [])) {
    if ((m.level ?? 0) !== levelIndex) continue;
    let runs = null;
    if (m.from_ft != null && m.to_ft != null) runs = [[m.from_ft, m.to_ft]];
    else if (Array.isArray(m.runs) && m.runs.length) runs = m.runs;
    if (!runs) { unlocated.push(m); continue; }
    // clip to the sheet, drop anything with no length left, and hang the △ on the
    // longest surviving piece — one line, one mark, on the widest wall it is true of
    const span = m.axis === 'x' ? H : W;
    const clipped = runs
      .map(([lo, hi]) => [Math.max(0, Math.min(lo, hi)), Math.min(span, Math.max(lo, hi))])
      .filter(([lo, hi]) => hi - lo > 0.05);
    if (!clipped.length) { unlocated.push(m); continue; }
    const best = clipped.reduce((a, b) => (b[1] - b[0] > a[1] - a[0] ? b : a));
    drawn.push({ mark: m, runs: clipped, at: (best[0] + best[1]) / 2 });
  }
  return { drawn, unlocated };
}

/* Vertical bay lines from the footprint's own module. */
export function bayLines(footprint) {
  const W = footprint?.width_ft || 0;
  const bm = footprint?.bay_module_ft || 10;
  const xs = [];
  for (let b = bm; b < W - 0.01; b += bm) xs.push(Math.round(b * 100) / 100);
  return xs;
}

/* A title that may fold at a word boundary and never inside a word. Extracted so the
   sheet's header and its plate caption cannot disagree about it — they did, and the
   caption folded 'TIDEWATER·GEORGIAN,·FIVE·BAYS,·CAREFULLY·PLANNED' into something that
   read as a different house. */
export function interpunctTitle(title) {
  return (title || '').trim().split(/\s+/).join('·\u200B');
}

/* Feet-and-inches with primes — never decimal feet in a drawing context. */
export function ft(v) {
  if (typeof v === 'string') return v;
  let whole = Math.floor(v + 1e-9);
  let inches = Math.round((v - whole) * 12);
  if (inches === 12) { whole += 1; inches = 0; }
  return `${whole}′-${inches}″`;
}
