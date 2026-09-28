/* The sheet's marks, measured where a reader would measure them (WP-14.4).

   `sheet/marks.js` is the geometry the bench sheet draws its openings and its stair from, lifted
   out of the JSX so it can be held to the record without a browser. The lift moved no ink: all 22
   bench plates of the sixteen shipped plans were server-rendered before and after it and compared
   byte for byte. Each test below is a behaviour the lift made testable and the package changed. */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

import { doorFrame, windowMark, stairArrow, bayLabel, leafOf, pairOf, sweepFlag, exteriorDoorMark,
         interiorDoorMark, breastOpening } from './sheet/marks.js';
import { bayLines, doors, levelRooms, wallOf, windows } from './sheet/derive.js';

const HERE = dirname(fileURLToPath(import.meta.url));

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
  // AND IT STANDS OVER THE FLIGHT'S MIDDLE (WP-14.6, auditor C). Everything above reads which
  // way the shaft runs, so an arrow drawn a flight's width off to the side -- or across the
  // landing -- passed it. The shaft's midpoint is the flight's own centre, in the sheet's
  // coordinates (y flipped), and it runs over the middle 68 per cent of the flight's length.
  const cx = f.x_ft + f.width_ft / 2, cy = -(f.y_ft + f.depth_ft / 2);
  for (const [dir, len] of [['N', f.depth_ft], ['S', f.depth_ft], ['E', f.width_ft], ['W', f.width_ft]]) {
    const [x0, y0, x1, y1] = stairArrow({ ...f, direction: dir }).shaft;
    assert.ok(Math.abs((x0 + x1) / 2 - cx) < 1e-9 && Math.abs((y0 + y1) / 2 - cy) < 1e-9,
      `the ${dir} arrow's middle is (${(x0 + x1) / 2}, ${(y0 + y1) / 2}), the flight's is (${cx}, ${cy})`);
    assert.ok(Math.abs(Math.hypot(x1 - x0, y1 - y0) - 0.68 * len) < 1e-9,
      `the ${dir} arrow runs ${Math.hypot(x1 - x0, y1 - y0)} ft over a ${len} ft flight`);
  }
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

/* ------------------------------------------------------------------ the leaf (WP-14.6's second audit)

   THE BENCH'S DOOR LEAF, ARC AND WINDOW WERE GUARDED BY NOTHING. Six mutations of the geometry
   below left all 279 app tests green: the jambs of a vertical wall swapped, the jambs of a
   horizontal wall swapped, a vertical wall's swing turned the other way, the sweep flag inverted,
   the glazing moved onto the wall's face, and a W or E sill moved into the room. The tests before
   these read the break's EXTENT and never which jamb a leaf hangs from, where it opens to, which
   way its arc turns, or where the glazing and the sill stand. */

const model = (p) => [p[0], -p[1]];                       // screen feet -> model feet
const near = (p, q, tol = 1e-6) => Math.abs(p[0] - q[0]) < tol && Math.abs(p[1] - q[1]) < tol;

/* The W3C SVG implementation notes, F.6.5, for a circle (rx = ry = r, no rotation): the CENTRE a
   renderer draws an arc about, given the arc's two ends, its radius and its flags. Reading the
   drawn arc back through this is what tests/test_drawn_geometry.py does for the profiles, and it
   is the one check that tells an arc from its own mirror about the chord -- the sweep bug that
   drew every horizontal-wall leaf in the Python sheet inside out for seven phases. */
function arcCentre([x1, y1], [x2, y2], r, sweep, large = 0) {
  const x1p = (x1 - x2) / 2, y1p = (y1 - y2) / 2;
  const d2 = x1p * x1p + y1p * y1p;
  const rr = Math.max(r, Math.sqrt(d2));
  const k = (large !== sweep ? 1 : -1) * Math.sqrt(Math.max(0, (rr * rr - d2) / d2));
  return [k * y1p + (x1 + x2) / 2, -k * x1p + (y1 + y2) / 2];
}

/* The leaf the contract states, exactly as tests/test_sheet_symbols.py's ink test states it for
   the printed plate: hung at the record's jamb ("low" is the lower coordinate ALONG the wall),
   open a leaf's width into the room it swings into, closing on the other jamb. Model feet. */
function contractLeaf(horiz, along, across, w, positive, hinge) {
  const [ha, fa] = hinge === 'high' ? [along + w / 2, along - w / 2] : [along - w / 2, along + w / 2];
  const H = horiz ? [ha, across] : [across, ha];
  const F = horiz ? [fa, across] : [across, fa];
  const E = horiz ? [ha, across + (positive ? w : -w)] : [across + (positive ? w : -w), ha];
  return { H, E, F };
}

function assertLeaf(lf, want, what) {
  assert.ok(near(model(lf.hinge), want.H), `${what}: hung at ${model(lf.hinge)}, the contract's hinge is ${want.H}`);
  assert.ok(near(model(lf.tip), want.E), `${what}: open to ${model(lf.tip)}, the contract's leaf ends at ${want.E}`);
  assert.ok(near(model(lf.far), want.F), `${what}: closes on ${model(lf.far)}, the other jamb is ${want.F}`);
  assert.ok(near(arcCentre(lf.tip, lf.far, lf.len, lf.sweep), lf.hinge),
    `${what}: the arc is drawn about ${arcCentre(lf.tip, lf.far, lf.len, lf.sweep)}, not its hinge ${lf.hinge} -- its mirror about the chord`);
}

/* Every case a single leaf can be: a horizontal or a vertical wall, hung low or high, opening to
   the positive side (north / east) or the negative. The last column is the SVG sweep flag, the
   value build/render_plan.py::sweep_flag gives the same three points (tests/test_sheet_symbols.py
   holds this module to that function under node). */
const LEAF_CASES = [
  [true, 'low', true, 1], [true, 'low', false, 0], [true, 'high', true, 0], [true, 'high', false, 1],
  [false, 'low', true, 0], [false, 'low', false, 1], [false, 'high', true, 1], [false, 'high', false, 0],
];

test('a single leaf hangs from the jamb its record names, opens into its room, and turns about its hinge', () => {
  for (const [horiz, hinge, positive, flag] of LEAF_CASES) {
    const d = horiz ? { x: 10, y: 5, w: 3, horiz, hinge, swingUp: positive }
      : { x: 10, y: 5, w: 3, horiz, hinge, swingRight: positive };
    const lf = leafOf(d);
    const what = `${horiz ? 'horizontal' : 'vertical'} wall, hung ${hinge}, opening ${positive ? '+' : '-'}`;
    assertLeaf(lf, contractLeaf(horiz, horiz ? 10 : 5, horiz ? 5 : 10, 3, positive, hinge), what);
    assert.equal(lf.len, 3, `${what}: the arc's radius is the leaf's width`);
    assert.equal(lf.sweep, flag, `${what}: sweep ${lf.sweep}, render_plan.py's rule gives ${flag}`);
  }
});

test('a pair is a half leaf from each jamb, meeting at the middle, each turning about its own hinge', () => {
  for (const horiz of [true, false]) {
    for (const positive of [true, false]) {
      const d = horiz ? { x: 10, y: 5, w: 6, horiz, swingUp: positive, type: 'double' }
        : { x: 10, y: 5, w: 6, horiz, swingRight: positive, type: 'double' };
      const [a, b] = pairOf(d);
      const along = horiz ? 10 : 5, across = horiz ? 5 : 10;
      const M = horiz ? [along, across] : [across, along];
      for (const [lf, jamb] of [[a, along - 3], [b, along + 3]]) {
        const H = horiz ? [jamb, across] : [across, jamb];
        const E = horiz ? [jamb, across + (positive ? 3 : -3)] : [across + (positive ? 3 : -3), jamb];
        assertLeaf(lf, { H, E, F: M }, `a ${horiz ? 'horizontal' : 'vertical'} pair's leaf at ${jamb}`);
        assert.equal(lf.len, 3);
      }
    }
  }
});

test('the sweep flag is the sign of the turn from the tip to the far jamb about the hinge', () => {
  // screen space, y down: a clockwise quarter-turn as a reader sees it is 1
  assert.equal(sweepFlag([0, 0], [0, -3], [3, 0]), 1);
  assert.equal(sweepFlag([0, 0], [3, 0], [0, -3]), 0);
  assert.equal(sweepFlag([0, 0], [0, 3], [3, 0]), 0);
  assert.equal(sweepFlag([0, 0], [-3, 0], [0, -3]), 1);
});

test("a window's glazing is on its own wall's centre line and its sill outside the wall, on every wall", () => {
  const face = { W: -34, E: -7, S: 5.28, N: 31.96 };
  for (const t of [0.667, T]) {
    for (const wall of ['W', 'E', 'S', 'N']) {
      const vert = wall === 'W' || wall === 'E';
      const w = vert ? { wall, x: face[wall], y: 12, w: 3 } : { wall, x: -20, y: face[wall], w: 3 };
      const { glazing: g, sill: s } = windowMark(w, t);
      const [ga, gb] = [model([g[0], g[1]]), model([g[2], g[3]])];
      const centre = { W: face.W - t / 2, E: face.E + t / 2, S: face.S - t / 2, N: face.N + t / 2 }[wall];
      const [gAcross, gAcross2] = vert ? [ga[0], gb[0]] : [ga[1], gb[1]];
      assert.ok(Math.abs(gAcross - centre) < 1e-9 && Math.abs(gAcross2 - centre) < 1e-9,
        `${wall} glazing stands at ${gAcross}, the wall's centre line is ${centre}`);
      const [gLo, gHi] = vert ? [Math.min(ga[1], gb[1]), Math.max(ga[1], gb[1])] : [Math.min(ga[0], gb[0]), Math.max(ga[0], gb[0])];
      const along = vert ? w.y : w.x;
      assert.ok(Math.abs(gLo - (along - 1.5)) < 1e-9 && Math.abs(gHi - (along + 1.5)) < 1e-9,
        `${wall} glazing runs ${gLo}..${gHi} along the wall, the opening ${along - 1.5}..${along + 1.5}`);
      // the sill: parallel to the wall, past its OUTER face, and at least as long as the opening
      const [sa, sb] = [model([s[0], s[1]]), model([s[2], s[3]])];
      const outer = { W: face.W - t, E: face.E + t, S: face.S - t, N: face.N + t }[wall];
      const sAcross = vert ? [sa[0], sb[0]] : [sa[1], sb[1]];
      assert.equal(sAcross[0], sAcross[1], `${wall} sill is parallel to its wall`);
      const out = wall === 'W' || wall === 'S' ? outer - sAcross[0] : sAcross[0] - outer;
      assert.ok(out >= -1e-9, `${wall} sill stands at ${sAcross[0]}, inside the wall's outer face ${outer} -- in the wall or the room`);
      const [sLo, sHi] = vert ? [Math.min(sa[1], sb[1]), Math.max(sa[1], sb[1])] : [Math.min(sa[0], sb[0]), Math.max(sa[0], sb[0])];
      assert.ok(sLo <= along - 1.5 + 1e-9 && sHi >= along + 1.5 - 1e-9, `${wall} sill does not span the opening`);
    }
  }
});

test('an exterior door opens into its room off every wall, and its break is the wall outward from the face', () => {
  const t = T;
  for (const [wall, positive] of [['S', true], ['N', false], ['W', true], ['E', false]]) {
    const horiz = wall === 'S' || wall === 'N';
    const d = { wall, x: horiz ? 12 : 30, y: horiz ? 30 : 12, w: 3, type: 'swing', hinge: 'low' };
    const desc = exteriorDoorMark(d, t);
    assert.equal(desc.horiz, horiz, `${wall}: orientation`);
    const across = horiz ? d.y : d.x, along = horiz ? d.x : d.y;
    assertLeaf(leafOf(desc), contractLeaf(horiz, along, across, 3, positive, 'low'), `exterior ${wall} door`);
    const e = extent(doorFrame(desc).rect);
    const [lo, hi] = horiz ? [e.y0, e.y1] : [e.x0, e.x1];
    const want = wall === 'S' || wall === 'W' ? [across - t, across] : [across, across + t];
    assert.ok(Math.abs(lo - want[0]) < 1e-9 && Math.abs(hi - want[1]) < 1e-9, `${wall} door break ${lo}..${hi}, the wall is ${want}`);
  }
});

test("a door onto an at-grade appendage is cut through the room's exterior wall, outward from its face", () => {
  // good-02's family room and the terrace placed against its W face (build/appendages.py): the
  // door is an INTERIOR entry, because the terrace is a room, standing in the house's exterior wall
  const family = { id: 'family', x: 0, y: 20, w: 16, h: 16, exterior_walls: ['W'], windows: [],
    doors: [{ to: 'terrace', width_ft: 6, type: 'double', wall: 'W', position_ft: 27.98 }] };
  const terrace = { id: 'terrace', x: -10, y: 11.96, w: 10, h: 24 };
  const t = 0.6667;
  const got = doors([family], 50, 40, 0.6, [terrace]);
  assert.equal(got.undrawable.length, 0, 'the door is seated and must be drawn');
  const d = got.interior[0];
  assert.equal(d.exteriorWall, 'W', 'the entry says which exterior wall it stands in');
  const e = extent(doorFrame(interiorDoorMark(d, t)).rect);
  assert.ok(Math.abs(e.x0 - -t) < 1e-9 && Math.abs(e.x1 - 0) < 1e-9, `the break runs ${e.x0}..${e.x1}, the wall -${t}..0`);
  assert.ok(Math.abs(e.y0 - 24.98) < 1e-9 && Math.abs(e.y1 - 30.98) < 1e-9, 'over the door\'s own 6 ft');
  // and it still swings out onto the terrace, which is the room it opens into
  for (const lf of pairOf(interiorDoorMark(d, t))) assert.ok(model(lf.tip)[0] < 0, 'a leaf onto the terrace opens west');
  // an interior door between two rooms keeps the 0.7 ft break centred on the line they share
  const plain = { x: 12, y: 20, w: 3, horiz: true, swingUp: true, pair: ['a', 'b'], hinge: 'low' };
  assert.deepEqual(interiorDoorMark(plain, t), plain);
});

test('the fireplace opening is on the breast\'s room face, centred, the stated width long', () => {
  // the Tidewater dining room's breast on its W wall, and the same breast turned onto the others
  const W_ = { wall: 'W', x_ft: 0, y_ft: 28.551, width_ft: 1.807, depth_ft: 4.758 };
  const [x1, y1, x2, y2] = breastOpening(W_, 41.1);
  assert.equal(x1, 1.807, 'on the room-side face of a W breast');
  assert.equal(x2, 1.807);
  const mid = 28.551 + 4.758 / 2;
  assert.ok(Math.abs((-y1 + -y2) / 2 - mid) < 1e-9 && Math.abs(Math.abs(y2 - y1) - 41.1 / 12) < 1e-9);
  const E_ = { ...W_, wall: 'E', x_ft: 43.269 };
  assert.equal(breastOpening(E_, 39.8)[0], 43.269, 'on the room-side face of an E breast');
  const S_ = { wall: 'S', x_ft: 10, y_ft: 0, width_ft: 4.9, depth_ft: 1.9 };
  const s = breastOpening(S_, 36);
  assert.equal(-s[1], 1.9, 'on the room-side face of an S breast');
  assert.ok(Math.abs((s[0] + s[2]) / 2 - 12.45) < 1e-9 && Math.abs(s[2] - s[0] - 3) < 1e-9);
  assert.equal(-breastOpening({ ...S_, wall: 'N', y_ft: 20 }, 36)[1], 20, 'on the room-side face of an N breast');
  assert.equal(breastOpening(W_, undefined), null, 'no stated opening, no opening drawn -- not a conventional 36 in');
});

/* ------------------------------------------------------------------ every door in the contract

   Held per fixture door to the SAME points tests/test_sheet_symbols.py's ink test holds the printed
   plate's leaves to, so the two sheets hang one record's doors alike. Three hangings of every
   fixture: as frozen (every door low, because `openings.place` writes low on every door it
   seats), every door high, and MIXED -- alternate doors hung high -- because a fixture hung one
   way cannot tell a leaf that reads the record from one that always answers that way. And a
   fourth with every door UNSEATED and mixed, which reaches the two paths no frozen door does. */
const FIX = join(HERE, '..', '..', '..', 'tests', 'fixtures', 'sheet_symbols');
const FIXTURES = readdirSync(FIX).filter((f) => f.endsWith('.json')).sort()
  .map((f) => JSON.parse(readFileSync(join(FIX, f), 'utf8')));

const doorKey = (roomId, d) => (d.to === 'exterior' ? `ext|${roomId}` : `int|${[roomId, d.to].sort().join('|')}`);

function rehang(levels, mode, unseat) {
  const lv2 = JSON.parse(JSON.stringify(levels));
  const keys = [...new Set(lv2.flatMap((lv) => lv.rooms.flatMap((r) => (r.doors || []).map((d) => doorKey(r.id, d)))))].sort();
  const hingeOf = (k) => (mode === 'high' ? 'high' : mode === 'mixed' ? (keys.indexOf(k) % 2 ? 'high' : 'low') : null);
  const record = new Map();
  for (const lv of lv2) for (const r of lv.rooms) for (const d of (r.doors || [])) {
    const k = doorKey(r.id, d);
    if (mode !== 'frozen') d.hinge = hingeOf(k);
    if (unseat) { delete d.wall; delete d.position_ft; delete d.unplaced; }
    record.set(k, d.hinge || 'low');
  }
  return { levels: lv2, record };
}

for (const fx of FIXTURES) {
  const W = fx.footprint.width_ft, H = fx.footprint.depth_ft;
  const t = wallOf(fx.footprint).exterior_ft;
  for (const [mode, unseat] of [['frozen', false], ['high', false], ['mixed', false], ['mixed', true]]) {
    test(`${fx.plan}: every leaf the bench draws stands where the contract stands it (${mode}${unseat ? ', unseated' : ''})`, () => {
      const { levels, record } = rehang(fx.levels, mode, unseat);
      let seen = 0;
      const hinges = new Set();
      for (const lv of levels) {
        const plan = { levels };
        const rooms = levelRooms(plan, plan, lv.index);
        const got = doors(rooms, W, H);
        const exp = fx.levels.find((l) => l.index === lv.index).expected;
        for (const d of got.interior) {
          if ((d.type || 'swing') !== 'swing') continue;
          const hinge = record.get(`int|${d.pair.slice().sort().join('|')}`);
          let want;
          if (unseat) {
            // no frozen position on this path: the bench's own, with the record's hinge
            want = contractLeaf(d.horiz, d.horiz ? d.x : d.y, d.horiz ? d.y : d.x, d.w,
              d.horiz ? d.swingUp : d.swingRight, hinge);
          } else {
            const e = exp.interior.find((x) => x.pair.slice().sort().join('|') === d.pair.slice().sort().join('|'));
            assert.ok(e, `${lv.id}: ${d.pair.join('|')} is not in the contract`);
            want = contractLeaf(e.horiz, e.pos_ft, e.at_ft, e.width_ft, e.swing_positive, hinge);
          }
          assertLeaf(leafOf(interiorDoorMark(d, t)), want, `${lv.id} ${d.pair.join('|')} hung ${hinge}`);
          hinges.add(hinge);
          seen += 1;
        }
        for (const d of got.exterior) {
          if ((d.type || 'swing') !== 'swing') continue;
          const hinge = record.get(`ext|${d.room}`);
          const horiz = d.wall === 'S' || d.wall === 'N';
          let want;
          if (unseat) {
            want = contractLeaf(horiz, (d.span[0] + d.span[1]) / 2, d.edge_ft, d.w, d.wall === 'S' || d.wall === 'W', hinge);
          } else {
            const e = exp.exterior.find((x) => x.room === d.room && x.wall === d.wall);
            assert.ok(e, `${lv.id}: the ${d.room}/${d.wall} exterior door is not in the contract`);
            want = contractLeaf(horiz, e.at_ft, e.edge_ft, e.width_ft, e.wall === 'S' || e.wall === 'W', hinge);
          }
          assertLeaf(leafOf(exteriorDoorMark(d, t)), want, `${lv.id} ${d.room}/${d.wall} hung ${hinge}`);
          hinges.add(hinge);
          seen += 1;
        }
      }
      assert.ok(seen > 10, `only ${seen} leaves read -- the check would pass on a sheet with none`);
      if (mode === 'mixed') {
        assert.deepEqual([...hinges].sort(), ['high', 'low'],
          'the premise: a mixed hanging reaches both jambs, or it cannot tell a leaf that reads the record from one that does not');
      }
    });
  }

  test(`${fx.plan}: every window the bench draws is glazed where the contract glazes it`, () => {
    let seen = 0;
    for (const lv of fx.levels) {
      const plan = { levels: fx.levels };
      const rooms = levelRooms(plan, plan, lv.index);
      const wins = windows(rooms, W, H, 0.6, doors(rooms, W, H).exterior);
      for (const e of lv.expected.windows) {
        const w = wins.find((x) => x.room === e.room && x.wall === e.wall
          && Math.abs(((x.wall === 'S' || x.wall === 'N') ? x.x : x.y) - e.at_ft) < 1e-3);
        assert.ok(w, `${lv.id}: the ${e.room}/${e.wall} window at ${e.at_ft} is not drawn`);
        const g = windowMark(w, t).glazing;
        const [a, b] = [model([g[0], g[1]]), model([g[2], g[3]])];
        const mid = e.wall === 'S' || e.wall === 'W' ? e.edge_ft - t / 2 : e.edge_ft + t / 2;
        const M = e.wall === 'S' || e.wall === 'N' ? [e.at_ft, mid] : [mid, e.at_ft];
        assert.ok(near([(a[0] + b[0]) / 2, (a[1] + b[1]) / 2], M, 1e-6)
          && Math.abs(Math.hypot(a[0] - b[0], a[1] - b[1]) - e.width_ft) < 1e-6,
          `${lv.id}: the ${e.width_ft} ft ${e.wall} window of ${e.room} is glazed at ${[(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]}, the contract at ${M}`);
        // and its sill stands outside the wall's outer face, where the plate stands its own (the
        // plate's is ON that face; the bench's is a hair past it, which is outside too)
        const s = windowMark(w, t).sill;
        const sAcross = e.wall === 'S' || e.wall === 'N' ? -s[1] : s[0];
        const outer = e.wall === 'S' || e.wall === 'W' ? e.edge_ft - t : e.edge_ft + t;
        assert.ok(e.wall === 'S' || e.wall === 'W' ? sAcross <= outer + 1e-9 : sAcross >= outer - 1e-9,
          `${lv.id}: the ${e.wall} sill of ${e.room} stands at ${sAcross}, inside the wall's outer face ${outer}`);
        seen += 1;
      }
    }
    assert.ok(seen > 5, `only ${seen} windows read`);
  });
}
