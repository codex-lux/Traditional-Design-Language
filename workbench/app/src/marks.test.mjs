/* The sheet's marks, measured where a reader would measure them (WP-14.4).

   `sheet/marks.js` is the geometry the bench sheet draws its openings and its stair from, lifted
   out of the JSX so it can be held to the record without a browser. The lift moved no ink: all 22
   bench plates of the sixteen shipped plans were server-rendered before and after it and compared
   byte for byte. Each test below is a behaviour the lift made testable and the package changed. */
import test from 'node:test';
import assert from 'node:assert/strict';

import { doorFrame, windowMark, stairArrow, bayLabel } from './sheet/marks.js';
import { bayLines, doors } from './sheet/derive.js';

const T = 1.2917;                     // the Tidewater envelope, 15.5 in

/* the rect's extent in MODEL feet: x as drawn, y un-flipped */
const extent = (r) => ({ x0: r.x, x1: r.x + r.width, y0: -(r.y + r.height), y1: -r.y });

test('a window stands in its OWN wall, outside its own face, whichever wall it is on', () => {
  // a dependency at negative x: a face that is not the footprint's on every side
  const face = { W: -34, E: -7, S: 5.28, N: 31.96 };
  for (const wall of ['W', 'E', 'S', 'N']) {
    const w = wall === 'W' || wall === 'E'
      ? { wall, x: face[wall], y: 12, w: 3 } : { wall, x: -20, y: face[wall], w: 3 };
    const e = extent(windowMark(w, T).rect);
    const out = { W: [e.x0, e.x1], E: [e.x0, e.x1], S: [e.y0, e.y1], N: [e.y0, e.y1] }[wall];
    const want = { W: [face.W - T, face.W], E: [face.E, face.E + T],
                   S: [face.S - T, face.S], N: [face.N, face.N + T] }[wall];
    assert.ok(Math.abs(out[0] - want[0]) < 1e-9 && Math.abs(out[1] - want[1]) < 1e-9,
      `${wall} window drawn across ${out.map((v) => v.toFixed(2))} where its wall is ${want.map((v) => v.toFixed(2))}`);
  }
});

test('the window is as deep as the wall it is cut in, and the sill stands outside it', () => {
  for (const t of [0.667, T]) {
    const { rect, sill } = windowMark({ wall: 'S', x: 10, y: 0, w: 3 }, t);
    assert.equal(rect.height, t);
    assert.ok(sill[1] > rect.y + rect.height, 'the sill is past the wall\'s outer face');
  }
});

test("an exterior door's break is the wall, outward from the room's face", () => {
  const cases = { S: [0, 12], N: [30, 12], W: [0, 12], E: [40, 12] };
  for (const [wall, [edge, at]] of Object.entries(cases)) {
    const horiz = wall === 'S' || wall === 'N';
    const d = { x: horiz ? at : edge, y: horiz ? edge : at, w: 3, wall, horiz, exterior: true, t: T };
    const e = extent(doorFrame(d).rect);
    const [lo, hi] = horiz ? [e.y0, e.y1] : [e.x0, e.x1];
    const want = { S: [-T, 0], N: [30, 30 + T], W: [-T, 0], E: [40, 40 + T] }[wall];
    assert.ok(Math.abs(lo - want[0]) < 1e-9 && Math.abs(hi - want[1]) < 1e-9,
      `${wall} door break ${lo.toFixed(2)}..${hi.toFixed(2)} where the wall is ${want}`);
  }
});

test("an interior door's break is unchanged: 0.7 ft centred on the shared line", () => {
  const r = doorFrame({ x: 12, y: 20, w: 3, horiz: true }).rect;
  assert.deepEqual([r.height, -(r.y + r.height / 2)], [0.7, 20]);
});

test('the exterior door carries the jamb the record hangs it from', () => {
  const room = { id: 'hall', x: 0, y: 0, w: 10, h: 10, exterior_walls: ['S'], windows: [],
    doors: [{ to: 'exterior', width_ft: 3, wall: 'S', position_ft: 5, hinge: 'high' }] };
  const got = doors([room], 10, 10).exterior;
  assert.equal(got.length, 1);
  assert.equal(got[0].hinge, 'high', 'the record says high and the entry must too');
  room.doors[0].hinge = undefined;
  assert.equal(doors([room], 10, 10).exterior[0].hinge, 'low', 'and low where it says nothing, as the interior branch');
});

test('the stair arrow points the way the flight runs, over its middle', () => {
  const f = { x_ft: 18, y_ft: 24.62, width_ft: 3.5, depth_ft: 7.5 };
  const n = stairArrow({ ...f, direction: 'N' });
  assert.ok(n.shaft[3] < n.shaft[1], 'a flight running north points up the screen');
  const s = stairArrow({ ...f, direction: 'S' });
  assert.ok(s.shaft[3] > s.shaft[1]);
  const e = stairArrow({ ...f, direction: 'E' });
  assert.ok(e.shaft[2] > e.shaft[0] && e.shaft[1] === e.shaft[3]);
  // the head is at the shaft's end
  assert.deepEqual([n.head[2], n.head[3]], [n.shaft[2], n.shaft[3]]);
  assert.equal(stairArrow({ ...f }), null, 'a flight stating no direction gets no arrow');
});

test("a bay line is labelled with the record's own figure, not a rounded one", () => {
  assert.equal(bayLabel(36.51), '36.51');
  assert.equal(bayLabel(9), '9');
  const xs = bayLines({ width_ft: 60.85, bay_module_ft: 12.17 });
  assert.deepEqual(xs.map(bayLabel), ['12.17', '24.34', '36.51', '48.68']);
});

test('a record stating no bay module gets no bay lines, not a 10 ft grid', () => {
  assert.deepEqual(bayLines({ width_ft: 40 }), []);
  assert.deepEqual(bayLines({ width_ft: 40, bay_module_ft: 0 }), []);
  assert.deepEqual(bayLines({ width_ft: 40, bay_module_ft: 10 }), [10, 20, 30]);
});
