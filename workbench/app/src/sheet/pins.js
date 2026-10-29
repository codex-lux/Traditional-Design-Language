/* FINDINGS PINNED WHERE THEY FALL (Phase 17, WP-17.5; docs/ui-redesign-2026-10-29.md, board 3).

   The bench listed its findings beside the plate and drew nothing on it, so a reader had to carry
   a room's name from the list to the drawing. A pin is the findings about ONE room, gathered: drawn
   at that room's north-east corner (clear of the room's own label, which is centred), carrying how
   many findings and the worst severity among them. A finding that names no room on this level has
   no locus and is never placed -- it stays in the list, where it always was.

   `rooms` are `derive.levelRooms`'s (model feet, y up); the pin's `x`/`y` are in the sheet's own
   screen frame (y negated), the frame every mark on the sheet is drawn in. Pure. */
export const SEVERITY_ORDER = Object.freeze(['fatal', 'serious', 'minor', 'advisory', 'info']);

const roomOf = (f) => (f && (f.at || f.room)) || null;

export function pinsOf(findings, rooms) {
  const byRoom = new Map((rooms || []).map((r) => [r.id, r]));
  const pins = new Map();
  for (const f of findings || []) {
    const id = roomOf(f);
    const r = id ? byRoom.get(id) : null;
    if (!r) continue;
    const p = pins.get(id) || { room: id, n: 0, worst: null, ids: [],
      // the north-east corner, inset by a pin's own size so it sits inside the room
      x: r.x + r.w - Math.min(1.4, r.w / 4), y: -(r.y + r.h) + Math.min(1.4, r.h / 4) };
    p.n += 1;
    p.ids.push(f.id);
    const rank = SEVERITY_ORDER.indexOf(f.severity);
    if (rank >= 0 && (p.worst === null || rank < SEVERITY_ORDER.indexOf(p.worst))) p.worst = f.severity;
    pins.set(id, p);
  }
  return [...pins.values()];
}

/* How many findings the pins carry and how many have no locus, so the sheet can say both. */
export function pinTally(findings, rooms) {
  const pinned = pinsOf(findings, rooms).reduce((a, p) => a + p.n, 0);
  return { pinned, unplaced: (findings || []).length - pinned };
}
