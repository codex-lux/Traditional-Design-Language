/* The transcription draft — the working state of a record being traced from a
   drawing (WP-5.5). Deliberately a SEPARATE store from planDoc: a draft is not
   a record. It carries trace geometry (room rectangles in model feet, x east,
   y north, origin SW) that the finished record will NOT carry — positions are
   working state used to derive clear dims, exterior walls and door
   suggestions; the record that leaves is dims + topology, like every other
   record in plans/. Same external-store shape as planDoc: subscribe/get,
   undo, localStorage so a refresh loses no tracing. The backdrop image is an
   object URL and deliberately NOT persisted — a scan can be tens of MB;
   losing it on refresh loses no data, only the tracing aid. */

const KEY = 'tdl-transcription-draft';
let draft = null;
let undoStack = [];
const listeners = new Set();

export function emptyDraft() {
  return {
    meta: { id: '', name: '', style: '', massing: '' },
    context: { date_of_representation: '', entrance_faces: 'S' },
    provenance: { source: '', method: 'traced', transcription_confidence: 'medium',
                  style_reasoning: '', traced_by: '' },
    levels: [{ id: 'ground', index: 0, floor_to_ceiling_ft: 9 }],
    rooms: [],          // {key, level, id, type, name, x, y, w, h, windows, doors, name_hint}
    seq: 1,             // next room number, so ids never collide after deletes
  };
}

try {
  const saved = localStorage.getItem(KEY);
  if (saved) draft = JSON.parse(saved);
} catch { /* private windows etc. */ }

function emit() {
  try { localStorage.setItem(KEY, JSON.stringify(draft)); } catch { /* best effort */ }
  listeners.forEach((fn) => fn());
}

export const draftDoc = {
  subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); },
  get() { return draft; },
  load(next) { if (draft) undoStack.push(draft); draft = next; emit(); },
  update(fn) {
    if (!draft) return;
    undoStack.push(draft);
    if (undoStack.length > 100) undoStack.shift();
    draft = fn(JSON.parse(JSON.stringify(draft)));
    emit();
  },
  /* Same mutation without an undo entry — for the many pointer-moves inside one
     drag. The gesture pushes ONE snapshot at pointer-down (via update), then
     coalesces here, so undo steps by gesture, not by pixel. */
  mutate(fn) {
    if (!draft) return;
    draft = fn(JSON.parse(JSON.stringify(draft)));
    emit();
  },
  undo() { if (undoStack.length) { draft = undoStack.pop(); emit(); } },
  canUndo: () => undoStack.length > 0,
  clear() { draft = null; undoStack = []; try { localStorage.removeItem(KEY); } catch {} emit(); },
};

/* ---- deriving the record ------------------------------------------------ */

const TOUCH_TOL = 0.6;   // build/render_plan.py's own exterior-wall tolerance

/* Exterior walls a traced rect touches, against its level's own envelope. */
export function exteriorWalls(room, rooms) {
  const lv = rooms.filter((r) => r.level === room.level);
  if (!lv.length) return [];
  const minX = Math.min(...lv.map((r) => r.x));
  const maxX = Math.max(...lv.map((r) => r.x + r.w));
  const minY = Math.min(...lv.map((r) => r.y));
  const maxY = Math.max(...lv.map((r) => r.y + r.h));
  const out = [];
  if (room.y <= minY + TOUCH_TOL) out.push('S');
  if (room.y + room.h >= maxY - TOUCH_TOL) out.push('N');
  if (room.x <= minX + TOUCH_TOL) out.push('W');
  if (room.x + room.w >= maxX - TOUCH_TOL) out.push('E');
  return out;
}

/* Rooms on the same level whose traced rects share enough edge for a door —
   suggestions for the door editor, never auto-written into the record. */
export function neighbours(room, rooms) {
  const out = [];
  for (const o of rooms) {
    if (o.key === room.key || o.level !== room.level) continue;
    const vx = Math.abs(room.x + room.w - o.x) <= 0.4 || Math.abs(o.x + o.w - room.x) <= 0.4;
    const vy = Math.abs(room.y + room.h - o.y) <= 0.4 || Math.abs(o.y + o.h - room.y) <= 0.4;
    if (vx && Math.min(room.y + room.h, o.y + o.h) - Math.max(room.y, o.y) > 3.2) out.push(o.id);
    else if (vy && Math.min(room.x + room.w, o.x + o.w) - Math.max(room.x, o.x) > 3.2) out.push(o.id);
  }
  return out;
}

/* Named gaps between this draft and a schema-valid record. Empty list = ready. */
export function completeness(d) {
  const gaps = [];
  if (!d.meta.id) gaps.push('the record has no id');
  if (!d.meta.name) gaps.push('the record has no name');
  if (!d.meta.style) gaps.push('style is unset — a judgment; record the reasoning in provenance');
  if (!d.rooms.length) gaps.push('no rooms traced');
  const ids = new Map();
  for (const r of d.rooms) {
    if (!r.type) gaps.push(`room “${r.name || r.id}” has no type from the catalog`);
    ids.set(r.id, (ids.get(r.id) || 0) + 1);
  }
  for (const [id, n] of ids) if (n > 1) gaps.push(`room id “${id}” is used ${n} times`);
  for (const lv of d.levels) {
    if (!lv.floor_to_ceiling_ft) gaps.push(`level ${lv.id} has no floor_to_ceiling_ft`);
    if (!d.rooms.some((r) => r.level === lv.index) && d.rooms.length)
      gaps.push(`level ${lv.id} has no rooms`);
  }
  for (const r of d.rooms) {
    for (const dr of r.doors || []) {
      if (dr.to !== 'exterior' && !d.rooms.some((o) => o.id === dr.to && o.level === r.level))
        gaps.push(`room “${r.id}” has a door to “${dr.to}”, which is not on its level`);
    }
  }
  if (d.provenance.method !== 'authored' && !d.provenance.source)
    gaps.push('provenance.source is empty — say what drawing this was traced from');
  return gaps;
}

/* Draft -> plan record. Trace positions are dropped; what leaves is dims +
   topology + provenance, the shape every record in plans/ has. */
export function toRecord(d) {
  const rec = {
    id: d.meta.id, name: d.meta.name, style: d.meta.style,
    levels: d.levels.map((lv) => ({
      id: lv.id, index: lv.index,
      floor_to_ceiling_ft: Number(lv.floor_to_ceiling_ft) || undefined,
      rooms: d.rooms.filter((r) => r.level === lv.index).map((r) => {
        const room = {
          id: r.id, type: r.type,
          name: r.name || undefined,
          width_ft: Math.round(r.w * 2) / 2,
          length_ft: Math.round(r.h * 2) / 2,
        };
        const ext = exteriorWalls(r, d.rooms);
        if (ext.length) room.exterior_walls = ext;
        if (r.windows?.length) room.windows = r.windows;
        if (r.doors?.length) room.doors = r.doors;
        return room;
      }),
    })),
  };
  if (d.meta.massing) rec.massing = d.meta.massing;
  const ctx = {};
  if (d.context.date_of_representation) ctx.date_of_representation = Number(d.context.date_of_representation);
  if (d.context.entrance_faces) ctx.entrance_faces = d.context.entrance_faces;
  if (Object.keys(ctx).length) rec.context = ctx;
  const prov = Object.fromEntries(Object.entries(d.provenance).filter(([, v]) => v));
  if (Object.keys(prov).length) rec.provenance = prov;
  return rec;
}

/* THE BACKDROP LIVES HERE, not in Transcription's component state.

   It holds the uploaded scan's object URL and — the part that costs real work to recreate —
   the width in feet and the opacity the reader hand-tuned against it. That was plain
   `useState`, which was harmless while App.jsx kept all eleven surfaces mounted forever. This
   session made the shell render only the active surface, so navigating away (including by the
   surface's own "send to the workbench" button) destroyed it: you came back to a blank canvas
   and re-uploaded and re-calibrated. An adversarial audit found it.

   The object URL is deliberately NOT persisted to localStorage — a blob URL is dead the
   moment the tab reloads, and storing one would promise a scan that is not there. It survives
   navigation within a session, which is the loss that was actually happening. */
let backdrop = null;
const backdropListeners = new Set();

export const backdropStore = {
  subscribe(fn) { backdropListeners.add(fn); return () => backdropListeners.delete(fn); },
  get() { return backdrop; },
  set(next) {
    // revoke the old blob before dropping it, or every re-upload leaks one
    if (backdrop && backdrop.url && (!next || next.url !== backdrop.url)) {
      try { URL.revokeObjectURL(backdrop.url); } catch (e) { /* not a blob URL */ }
    }
    backdrop = next;
    backdropListeners.forEach((fn) => fn());
  },
};
