// The bench sheet's opening marks, computed for the census (WP-14.4).
//
// Reads {case_key: {plan, placement, level}} on stdin -- `placement` exactly as
// mcp_server/core.py::placement_summary serves it -- and writes, per case, the window and exterior
// door marks the bench sheet draws: each one's room, wall, position along the wall, the face
// `derive.js` stands it on, and the across-extent of the mark `sheet/marks.js` draws, in model feet
// (screen y un-flipped). It imports the modules the sheet imports and re-derives nothing: the JSX
// only copies these numbers into elements, and that copy was proved byte-identical when the marks
// were lifted out of it.
import { levelRooms, elementBounds, doors, windows, wallOf } from '../../workbench/app/src/sheet/derive.js';
import { windowMark, doorFrame } from '../../workbench/app/src/sheet/marks.js';

let raw = '';
process.stdin.setEncoding('utf8');
for await (const chunk of process.stdin) raw += chunk;
const cases = JSON.parse(raw);
const out = {};
const across = (r, wall) => (wall === 'W' || wall === 'E')
  ? [r.x, r.x + r.width] : [-(r.y + r.height), -r.y];
for (const [key, c] of Object.entries(cases)) {
  const fp = c.placement.footprint || {};
  const W = fp.width_ft, H = fp.depth_ft;
  const wall = wallOf(fp);
  const rooms = levelRooms(c.plan, c.placement, c.level);
  const el = elementBounds(rooms, fp);
  const drs = doors(rooms, W, H, 0.6, null, el);
  const wins = windows(rooms, W, H, 0.6, drs.exterior, el);
  out[key] = {
    t: wall.exterior_ft,
    windows: wins.map((w) => ({ room: w.room, wall: w.wall, edge_ft: w.edge_ft,
      along: (w.wall === 'S' || w.wall === 'N') ? w.x : w.y,
      across: across(windowMark(w, wall.exterior_ft).rect, w.wall) })),
    exterior: drs.exterior.map((d) => ({ room: d.room, wall: d.wall, edge_ft: d.edge_ft, hinge: d.hinge,
      along: (d.span[0] + d.span[1]) / 2,
      across: across(doorFrame({ x: d.x, y: d.y, w: d.w, horiz: !(d.wall === 'W' || d.wall === 'E'),
        wall: d.wall, exterior: true, t: wall.exterior_ft }).rect, d.wall) })),
  };
}
process.stdout.write(JSON.stringify(out));
