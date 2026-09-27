// The bench sheet's opening marks, computed for the census (WP-14.4).
//
// Reads {case_key: {plan, placement, level}} on stdin -- `placement` exactly as
// mcp_server/core.py::placement_summary serves it -- and writes, per case, the window and exterior
// door marks the bench sheet draws: each one's room, wall, position along the wall, the face
// `derive.js` stands it on, and the across-extent of the mark `sheet/marks.js` draws, in model feet
// (screen y un-flipped). It imports the modules the sheet imports and re-derives nothing: the JSX
// only copies these numbers into elements, and that copy was proved byte-identical when the marks
// were lifted out of it.
//
// WP-14.6's second audit: this passed `null` for the appendages where the sheet passes the
// served `placement.appendages.placed`, and wrote the exterior door's descriptor out a third time.
// Both are the sheet's own functions now (`derive.levelAppendages`/`appendageRects`,
// `marks.exteriorDoorMark`/`interiorDoorMark`), so the census reads the doors the sheet draws. And
// it reports the INTERIOR doors as well, because a door onto an at-grade appendage is an interior
// entry standing in an exterior wall, and census B1 holds those too.
import { levelRooms, elementBounds, doors, windows, wallOf, levelAppendages, appendageRects }
  from '../../workbench/app/src/sheet/derive.js';
import { windowMark, doorFrame, exteriorDoorMark, interiorDoorMark }
  from '../../workbench/app/src/sheet/marks.js';

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
  const drs = doors(rooms, W, H, 0.6, appendageRects(levelAppendages(c.placement, c.level)), el);
  const wins = windows(rooms, W, H, 0.6, drs.exterior, el);
  out[key] = {
    t: wall.exterior_ft,
    windows: wins.map((w) => ({ room: w.room, wall: w.wall, edge_ft: w.edge_ft,
      along: (w.wall === 'S' || w.wall === 'N') ? w.x : w.y,
      across: across(windowMark(w, wall.exterior_ft).rect, w.wall) })),
    exterior: drs.exterior.map((d) => ({ room: d.room, wall: d.wall, edge_ft: d.edge_ft, hinge: d.hinge,
      along: (d.span[0] + d.span[1]) / 2,
      across: across(doorFrame(exteriorDoorMark(d, wall.exterior_ft)).rect, d.wall) })),
    // every interior door the sheet draws, with the extent of its break ACROSS the line it stands
    // on (x on a vertical wall, y on a horizontal one), in model feet
    interior: drs.interior.map((d) => ({ pair: d.pair, horiz: d.horiz, exterior_wall: d.exteriorWall || null,
      along: d.horiz ? d.x : d.y,
      across: across(doorFrame(interiorDoorMark(d, wall.exterior_ft)).rect, d.horiz ? 'S' : 'W') })),
  };
}
process.stdout.write(JSON.stringify(out));
