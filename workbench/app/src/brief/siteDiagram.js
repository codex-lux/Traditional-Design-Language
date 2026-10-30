/* THE SITE, DRAWN (Phase 17, WP-17.6; docs/ui-redesign-2026-10-29.md, board 4).

   The Brief asked for the lot as two numbers and the entrance as a row of eight chips. The board
   draws the site: the lot to scale, its street edge, and a compass whose eight points ARE the
   control -- diagonals included, because a brief's `entrance_faces` admits them
   (`schema/brief.schema.json`). This leaf turns the brief's own fields into that drawing and
   decides nothing else:

     - a lot stated in both dimensions is drawn to scale in a fixed box; a lot with either missing
       is UNSTATED and drawn as a dashed square that says so, never a default lot;
     - the street edge is the side the entrance faces, where the entrance faces a cardinal; a
       diagonal entrance stands on a corner, and the corner is drawn instead of an edge;
     - north is up, which is the plan's convention (`build/compass.py`), stated on the drawing.

   Pure geometry in a 120 x 120 box. */
export const COMPASS = Object.freeze(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']);
const BOX = 120, PAD = 26;
const DIR = Object.freeze({ N: [0, -1], NE: [1, -1], E: [1, 0], SE: [1, 1], S: [0, 1], SW: [-1, 1], W: [-1, 0], NW: [-1, -1] });

export function siteDiagram({ lotW = null, lotD = null, entrance = null } = {}) {
  const stated = Number.isFinite(lotW) && lotW > 0 && Number.isFinite(lotD) && lotD > 0;
  const room = BOX - 2 * PAD;
  let lot;
  if (stated) {
    const k = room / Math.max(lotW, lotD);
    const w = lotW * k, h = lotD * k;
    lot = { x: (BOX - w) / 2, y: (BOX - h) / 2, w, h, stated: true };
  } else {
    lot = { x: PAD, y: PAD, w: room, h: room, stated: false };
  }
  const cx = BOX / 2, cy = BOX / 2;
  // the eight compass points, on a ring outside the lot, each a control
  const ringR = BOX / 2 - 9;
  const points = COMPASS.map((d) => {
    const [dx, dy] = DIR[d];
    const n = Math.hypot(dx, dy);
    return { d, x: cx + (dx / n) * ringR, y: cy + (dy / n) * ringR, on: d === entrance };
  });
  // the street: the lot edge (or corner) the entrance faces
  let street = null;
  if (entrance && DIR[entrance]) {
    const [dx, dy] = DIR[entrance];
    const x0 = lot.x, x1 = lot.x + lot.w, y0 = lot.y, y1 = lot.y + lot.h;
    if (dx === 0 || dy === 0) {
      street = dy === -1 ? { x1: x0, y1: y0, x2: x1, y2: y0 } : dy === 1 ? { x1: x0, y1: y1, x2: x1, y2: y1 }
        : dx === -1 ? { x1: x0, y1: y0, x2: x0, y2: y1 } : { x1: x1, y1: y0, x2: x1, y2: y1 };
      street.corner = false;
    } else {
      const px = dx > 0 ? x1 : x0, py = dy > 0 ? y1 : y0;
      street = { x1: px - dx * 10, y1: py, x2: px, y2: py - dy * 10, corner: true };
    }
  }
  return { box: BOX, lot, points, street, entrance: entrance && DIR[entrance] ? entrance : null };
}
