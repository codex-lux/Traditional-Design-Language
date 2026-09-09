/* The Round's camera and its captions (WP-12.4).

   THE ASSERTION THIS FILE EXISTS FOR IS THE HANDEDNESS ONE. A camera convention can be
   exactly backwards and every model test still pass: the house is the right shape, the
   scale is right, the projection is self-consistent, and every elevation is drawn as its
   own mirror. That is WP-5.11's inverted SVG sweep flag one dimension up -- 245 arcs drawn
   as their own reflection through 34 checks, 970 tests and a browser walk, because every
   one of them interrogated the model and none asked where the ink went. So the tests below
   do not check that `project` is consistent; they check that EAST IS ON THE RIGHT of the
   south elevation and on the LEFT of the north one, which is a fact about drawings and not
   about arithmetic, and which a mirrored convention fails immediately.

   The fixture's numbers are the Tidewater plan's own, measured off build/scene.py rather
   than invented, so a bound that is negative by one exterior wall thickness (-1.292) is
   exercised rather than rounded away. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import {
  AXON_ELEVATION_DEG,
  MARGIN_FT,
  NAMED_TOL_DEG,
  basis,
  defaultAxon,
  framing,
  isNamed,
  namedViews,
  planLevel,
  poseFor,
  project,
  shortestTurn,
  tween,
  unproject,
} from './round/frame.js';
import { caption, chipLabel, furnitureFor, notModelledLine, plateKeyFor } from './round/annotate.js';
import { edges, extent, facesOf, normalOf, triangles } from './round/solids.js';

const SCENE = {
  bounds: { min: [-1.292, -1.292, 0], max: [64.288, 39.458, 39.03] },
  cut_height_ft: 4,
  entrance_face: 'S',
  storeys: [
    { id: 'ground', index: 0, floor_z_ft: 2.0, ceiling_z_ft: 13.0 },
    { id: 'upper', index: 1, floor_z_ft: 14.279, ceiling_z_ft: 24.279 },
  ],
  faces: {
    S: { label: 'SOUTH ELEVATION', token: 'S', role: 'THE ENTRANCE FRONT' },
    N: { label: 'NORTH ELEVATION', token: 'N' },
    E: { label: 'EAST ELEVATION', token: 'E' },
    W: { label: 'WEST ELEVATION', token: 'W' },
  },
  not_modelled: [{ what: 'chimney stacks' }],
};

const VIEWPORT = { width: 1200, height: 900 };
const px = (view, p) => project(poseFor(view, SCENE), VIEWPORT, p);

/* ------------------------------------------------------------------ handedness */

test('east is on the right of the south elevation and on the left of the north', () => {
  // Two points a foot apart on the x axis, at the same height. Which way they fall on the
  // plate is the whole question; the magnitude is not.
  const west = [10, 20, 10];
  const east = [11, 20, 10];
  const s = [px('s', west)[0], px('s', east)[0]];
  const n = [px('n', west)[0], px('n', east)[0]];
  assert.ok(s[1] > s[0], `south elevation: east should be right of west, got ${s[0]} → ${s[1]}`);
  assert.ok(n[1] < n[0], `north elevation: east should be LEFT of west, got ${n[0]} → ${n[1]}`);
});

test('north is on the right of the east elevation and on the left of the west', () => {
  const south = [30, 10, 10];
  const north = [30, 11, 10];
  const e = [px('e', south)[0], px('e', north)[0]];
  const w = [px('w', south)[0], px('w', north)[0]];
  assert.ok(e[1] > e[0], `east elevation: north should be right of south, got ${e[0]} → ${e[1]}`);
  assert.ok(w[1] < w[0], `west elevation: north should be LEFT of south, got ${w[0]} → ${w[1]}`);
});

test('up is up in every elevation, and north is up in the plan', () => {
  for (const v of ['s', 'n', 'e', 'w']) {
    const lo = px(v, [30, 20, 5])[1];
    const hi = px(v, [30, 20, 15])[1];
    assert.ok(hi < lo, `${v}: a higher point must plot higher on the plate (${lo} → ${hi})`);
  }
  // Screen-up is model-north on a plan -- the Sheet's own rule, arriving in the camera.
  const south = px('plan-l0', [30, 5, 2])[1];
  const north = px('plan-l0', [30, 35, 2])[1];
  assert.ok(north < south, `plan: north must plot above south (${south} → ${north})`);
  const west = px('plan-l0', [5, 20, 2])[0];
  const east = px('plan-l0', [55, 20, 2])[0];
  assert.ok(east > west, `plan: east must plot right of west (${west} → ${east})`);
});

test('the camera stands where the view says it stands', () => {
  // The convention that is easy to get backwards, asserted directly: the south elevation is
  // drawn from the SOUTH, so its forward vector points north.
  assert.ok(basis(180, 0).forward[1] > 0.99, 'the south elevation looks north');
  assert.ok(basis(0, 0).forward[1] < -0.99, 'the north elevation looks south');
  assert.ok(basis(90, 0).forward[0] < -0.99, 'the east elevation looks west');
  assert.ok(basis(270, 0).forward[0] > 0.99, 'the west elevation looks east');
});

/* ------------------------------------------------------------------ poses */

test('the axon angle is derived and not typed', () => {
  // atan(1/sqrt(2)) is the elevation at which the three axes project equally. A test that
  // asserted 35.264 against a literal 35.264 would prove only that nobody had retyped it.
  const trueIso = (Math.atan(Math.SQRT1_2) * 180) / Math.PI;
  assert.ok(
    Math.abs(AXON_ELEVATION_DEG - trueIso) < 1e-12,
    `the axon elevation must be atan(1/sqrt2) = ${trueIso}, got ${AXON_ELEVATION_DEG}`,
  );
  assert.ok(
    Math.abs(AXON_ELEVATION_DEG - 35.264) < 0.001,
    `and it must still be the 35.264 the brief names, got ${AXON_ELEVATION_DEG}`,
  );
});

test('every named view has the azimuth its own name implies', () => {
  assert.equal(poseFor('s', SCENE).azimuthDeg, 180);
  assert.equal(poseFor('n', SCENE).azimuthDeg, 0);
  assert.equal(poseFor('e', SCENE).azimuthDeg, 90);
  assert.equal(poseFor('w', SCENE).azimuthDeg, 270);
  for (const v of ['s', 'n', 'e', 'w']) {
    assert.equal(poseFor(v, SCENE).elevationDeg, 0, `${v} is a true elevation`);
  }
  assert.equal(poseFor('axon-sw', SCENE).azimuthDeg, 225);
  assert.equal(poseFor('axon-ne', SCENE).azimuthDeg, 45);
  for (const v of ['axon-sw', 'axon-se', 'axon-nw', 'axon-ne']) {
    assert.ok(Math.abs(poseFor(v, SCENE).elevationDeg - AXON_ELEVATION_DEG) < 1e-12);
  }
  assert.equal(poseFor('plan-l0', SCENE).elevationDeg, 90);
  assert.equal(poseFor('roof', SCENE).elevationDeg, 90);
  assert.equal(poseFor('free', SCENE), null, 'free is a reading of the live camera, not a place');
});

test('the plan is cut where the record says, and the roof plan is not cut at all', () => {
  const g = poseFor('plan-l0', SCENE);
  const u = poseFor('plan-l1', SCENE);
  assert.deepEqual(g.cut, { z_ft: 2.0 + 4, level: 0 });
  assert.deepEqual(u.cut, { z_ft: 14.279 + 4, level: 1 });
  assert.equal(poseFor('roof', SCENE).cut, null, 'a roof plan cuts nothing');
  // Driven: the height is READ. A record stating a different cut must move the plane.
  const deeper = poseFor('plan-l0', { ...SCENE, cut_height_ft: 6 });
  assert.equal(deeper.cut.z_ft, 8.0, 'the cut follows scene.cut_height_ft rather than a constant');
});

test('the default axon shows the entrance face and the face to its left', () => {
  assert.equal(defaultAxon('S'), 'axon-sw');
  assert.equal(defaultAxon('N'), 'axon-ne');
  assert.equal(defaultAxon('E'), 'axon-se');
  assert.equal(defaultAxon('W'), 'axon-nw');
  // FOUR tokens, not the eight the brief names: a window's `wall` is an N/E/S/W enum, so an
  // intercardinal entrance cannot be written in this corpus and an eight-way table would be
  // four branches nothing can reach. An unknown token falls back and says so by returning
  // the same axon a south front gets, which is the commonest front in the corpus.
  assert.equal(defaultAxon('NE'), 'axon-sw');
  assert.equal(defaultAxon(undefined), 'axon-sw');
});

test('the view bar offers one plan per stated level and nothing for a level the record lacks', () => {
  assert.deepEqual(namedViews(SCENE).slice(0, 2), ['plan-l0', 'plan-l1']);
  const oneStorey = { ...SCENE, storeys: [SCENE.storeys[0]] };
  assert.deepEqual(namedViews(oneStorey).slice(0, 2), ['plan-l0', 's']);
  assert.equal(planLevel('plan-l1'), 1);
  assert.equal(planLevel('roof'), null);
});

/* ------------------------------------------------------------------ framing */

test('framing fits the whole house with the sheet’s own margins', () => {
  const h = framing(SCENE, 's', 4 / 3);
  const modelH = SCENE.bounds.max[2] - SCENE.bounds.min[2];
  assert.ok(2 * h > modelH, `the house (${modelH} ft) must fit in the frame (${2 * h} ft)`);
  const air = 2 * h - modelH;
  assert.ok(
    air >= MARGIN_FT.top + MARGIN_FT.bottom - 1e-9,
    `and the margins must survive: ${air} ft of air against ${MARGIN_FT.top + MARGIN_FT.bottom}`,
  );
  // A wider plate needs no more height; a narrower one does. Driven both ways, because a
  // framing that ignores aspect fits on a 4:3 pane and clips on a 21:9 one.
  assert.ok(framing(SCENE, 's', 3) <= framing(SCENE, 's', 4 / 3) + 1e-9);
  assert.ok(framing(SCENE, 's', 0.6) > framing(SCENE, 's', 4 / 3));
});

/* ------------------------------------------------------------------ tween */

test('a tween starts where it starts and ends where it ends, exactly', () => {
  const a = poseFor('s', SCENE);
  const b = poseFor('axon-sw', SCENE);
  assert.equal(tween(a, b, 0), a, 't=0 must return the pose itself, not a copy of it');
  assert.equal(tween(a, b, 1), b, 't=1 must return the pose itself, not a copy of it');
  const mid = tween(a, b, 0.5);
  assert.ok(mid.elevationDeg > 0 && mid.elevationDeg < b.elevationDeg);
  assert.equal(mid.view, 'free', 'mid-tween is not a named view');
});

test('a tween takes the short way round', () => {
  assert.equal(shortestTurn(350, 10), 20);
  assert.equal(shortestTurn(10, 350), -20);
  assert.equal(shortestTurn(0, 180), 180);
  // The west elevation (270) to the north one (0) is a quarter turn, not three quarters.
  const w = poseFor('w', SCENE);
  const n = poseFor('n', SCENE);
  const q = tween(w, n, 0.5).azimuthDeg;
  assert.ok(q > 270 || q < 360.001, `expected the short arc through 315, got ${q}`);
  assert.ok(Math.abs(shortestTurn(w.azimuthDeg, n.azimuthDeg)) === 90);
});

/* ------------------------------------------------------------------ projection */

test('project and unproject round-trip on a stated plane', () => {
  for (const v of ['plan-l0', 'axon-sw', 'axon-ne', 'roof']) {
    const pose = poseFor(v, SCENE);
    const p = [17.5, 23.25, 6];
    const s = project(pose, VIEWPORT, p);
    const back = unproject(pose, VIEWPORT, [s[0], s[1]], 6);
    assert.ok(back, `${v}: the plane z=6 must be reachable`);
    assert.ok(
      Math.abs(back[0] - p[0]) < 1e-6 && Math.abs(back[1] - p[1]) < 1e-6,
      `${v}: round trip lost the point — ${p} → ${back}`,
    );
  }
});

test('unproject refuses the plane an elevation cannot meet', () => {
  // An elevation looks along the horizon; z = const is parallel to its view direction and
  // is met nowhere. Returning a plausible coordinate here would hand the cut handle a
  // position the reader would believe.
  for (const v of ['s', 'n', 'e', 'w']) {
    const got = unproject(poseFor(v, SCENE), VIEWPORT, [600, 450], 6);
    assert.equal(got, null, `${v} must refuse, got ${JSON.stringify(got)}`);
  }
});

test('depth grows away from the camera, so a label can be hidden behind the house', () => {
  const pose = poseFor('s', SCENE);
  const near = project(pose, VIEWPORT, [30, 0, 10])[2];
  const far = project(pose, VIEWPORT, [30, 38, 10])[2];
  assert.ok(far > near, `the far wall must be deeper: ${near} → ${far}`);
});

/* ------------------------------------------------------------------ named or free */

test('a pose that has drifted is free, and half a degree is the line', () => {
  const s = poseFor('s', SCENE);
  assert.ok(isNamed(s, 's', SCENE), 'the named pose is named');
  const nudged = { ...s, azimuthDeg: s.azimuthDeg + NAMED_TOL_DEG / 2 };
  assert.ok(isNamed(nudged, 's', SCENE), 'inside the tolerance it is still the south elevation');
  const orbited = { ...s, azimuthDeg: s.azimuthDeg + NAMED_TOL_DEG + 0.01 };
  assert.ok(!isNamed(orbited, 's', SCENE), 'past it, the drawing is no longer that drawing');
  const tilted = { ...s, elevationDeg: s.elevationDeg + NAMED_TOL_DEG + 0.01 };
  assert.ok(!isNamed(tilted, 's', SCENE), 'elevation counts as much as azimuth');
  assert.ok(!isNamed(s, 'free', SCENE), 'free is never named');
});

/* ------------------------------------------------------------------ captions */

test('a face caption carries the record’s own role, and only where the record states one', () => {
  assert.equal(caption('s', SCENE), 'SOUTH ELEVATION · THE ENTRANCE FRONT');
  assert.equal(caption('n', SCENE), 'NORTH ELEVATION');
  // Driven the other way: move the entrance and the phrase must move with it, or the
  // caption is a literal wearing a record's clothes.
  const northFront = {
    ...SCENE,
    faces: { ...SCENE.faces, S: { label: 'SOUTH ELEVATION', token: 'S' }, N: { label: 'NORTH ELEVATION', token: 'N', role: 'THE ENTRANCE FRONT' } },
  };
  assert.ok(!caption('s', northFront).includes('ENTRANCE'));
  assert.ok(caption('n', northFront).includes('THE ENTRANCE FRONT'));
});

test('a plan caption names its storey in the corpus’s own word and states the cut', () => {
  assert.equal(caption('plan-l0', SCENE), 'GROUND FLOOR PLAN · CUT AT 4′-0″ ABOVE FINISHED FLOOR');
  assert.equal(caption('plan-l1', SCENE), 'UPPER FLOOR PLAN · CUT AT 4′-0″ ABOVE FINISHED FLOOR');
  // A record that states no cut height says so rather than printing a default as a fact.
  const noCut = { ...SCENE, cut_height_ft: null };
  assert.ok(caption('plan-l0', noCut).includes('NOT STATED BY THE RECORD'));
  // A level the storeys do not name falls back to its index rather than borrowing a word.
  const odd = { ...SCENE, storeys: [] };
  assert.ok(caption('plan-l1', odd).startsWith('LEVEL 1 FLOOR PLAN'));
});

test('an axon is named by the compass and a free view withholds its dimensions', () => {
  assert.equal(caption('axon-sw', SCENE), 'AXONOMETRIC · FROM THE SOUTH-WEST');
  assert.equal(caption('axon-ne', SCENE), 'AXONOMETRIC · FROM THE NORTH-EAST');
  assert.equal(caption('roof', SCENE), 'ROOF PLAN');
  const free = caption('free', SCENE);
  assert.ok(free.includes('NOT A NAMED DRAWING') && free.includes('DIMENSIONS WITHHELD'), free);
  assert.equal(caption(null, SCENE), free, 'no view is the free view, and says the same thing');
});

test('the chip prints a short name and the caption prints the drawing’s', () => {
  assert.equal(chipLabel('plan-l0', SCENE), 'PLAN·L0');
  assert.equal(chipLabel('s', SCENE), 'S');
  assert.equal(chipLabel('axon-sw', SCENE), 'AXON·SW');
  assert.equal(chipLabel('roof', SCENE), 'ROOF');
});

/* ------------------------------------------------------------------ furniture and plates */

test('a view shows the furniture that is true in it and no more', () => {
  assert.ok(furnitureFor('plan-l0').roomNames, 'a plan names its rooms');
  assert.ok(!furnitureFor('s').roomNames, 'an elevation does not — a room is an edge there');
  // A scale bar is honest in a parallel projection along an axis and nowhere else.
  assert.ok(furnitureFor('axon-sw').axisRules, 'an axon rules its three axes');
  assert.ok(!furnitureFor('axon-sw').scaleBar, 'and carries no single scale bar');
  assert.ok(furnitureFor('s').scaleBar, 'an elevation does carry one');
  assert.deepEqual(Object.keys(furnitureFor('free')), ['compass'], 'a free view measures nothing');
});

test('the plate key is the one the server wrote', () => {
  // workbench/server/corpus.py::SCENE_PLATES keys its map exactly this way. One spelling.
  assert.equal(plateKeyFor('plan-l0'), 'plan');
  assert.equal(plateKeyFor('plan-l1'), 'plan');
  assert.equal(plateKeyFor('s'), 'elevation:S');
  assert.equal(plateKeyFor('w'), 'elevation:W');
  assert.equal(plateKeyFor('roof'), 'roof');
  // An axon is not a drawing this project makes flat, and says so rather than borrowing one.
  assert.equal(plateKeyFor('axon-sw'), null);
  assert.equal(plateKeyFor('free'), null);
});

test('the not-modelled line counts, and is silent when there is nothing to say', () => {
  assert.equal(notModelledLine(SCENE), '1 thing the record holds is not modelled — listed in the card');
  assert.equal(notModelledLine({ ...SCENE, not_modelled: [{}, {}] }).startsWith('2 things'), true);
  assert.equal(notModelledLine({ ...SCENE, not_modelled: [] }), null, 'no reassuring zero');
});

/* ------------------------------------------------------------------ solids */

/* Two REAL solids off build/scene.py's Tidewater record, not invented ones: a ground-floor
   sash on the south front and the east gable. Their numbers are what make the contract
   assertions below mean something -- 1.292 is one exterior wall thickness, and where that
   1.292 goes is the whole of WP-12.2's third finding. */
const SASH = {
  id: 'S-0-ground-window',
  class: 'opening-frame',
  geometry: {
    type: 'extrude', plane: 'xz', at: -1.292, thickness: 1.292,
    outline: [[1.782, 4.5], [5.003, 4.5], [5.003, 11.263], [1.782, 11.263]],
  },
};
const GABLE_E = {
  id: 'gable-E',
  class: 'gable',
  geometry: {
    type: 'extrude', plane: 'yz', at: 62.997, thickness: 1.292,
    outline: [[-1.292, 25.44], [19.083, 39.03], [39.458, 25.44]],
  },
};
const WALL_S = {
  id: 'L0-wall-0',
  class: 'wall',
  geometry: { type: 'box', origin: [0.0, -1.292, 2.0], size: [63.0, 1.292, 11] },
};

test('a box occupies exactly the extent it declares', () => {
  const e = extent(WALL_S);
  assert.deepEqual(e.min, [0.0, -1.292, 2.0]);
  assert.deepEqual(e.max.map((n) => +n.toFixed(6)), [63.0, 0.0, 13.0]);
  assert.equal(triangles(WALL_S).length, 12, 'six faces, two triangles each');
  assert.equal(edges(WALL_S).length, 12, 'twelve edges, each drawn once, not twice');
});

test('an opening is extruded INTO its wall, on every plane', () => {
  // WP-12.2's finding, asserted as the CONTRACT rather than as a consequence: `at` is the LOW
  // face and the sweep always runs along the plane's POSITIVE axis. The first version of the
  // scene put `at` on the OUTSIDE face with an always-positive thickness, so south and west
  // openings went in and north and east ones stood proud -- and the test that was green over
  // it compared `at` against exactly where the wrong contract had put it.
  const s = extent(SASH);
  assert.equal(+s.min[1].toFixed(6), -1.292, 'the sash starts on the wall’s outside face');
  assert.equal(+s.max[1].toFixed(6), 0.0, 'and ends on its clear face — inside the wall');

  const g = extent(GABLE_E);
  assert.equal(+g.min[0].toFixed(6), 62.997, 'the east gable starts on its wall’s low face');
  assert.equal(+g.max[0].toFixed(6), 64.289, 'and sweeps east through the wall, not past it');

  // Driven on the third plane too, since a prism is the same sweep with a different pair.
  const sp = { geometry: { type: 'prism', polygon: [[0, 0], [4, 0], [4, 3]], z0: 2, z1: 13 } };
  const pe = extent(sp);
  assert.equal(pe.min[2], 2, 'a space stands on its floor');
  assert.equal(pe.max[2], 13, 'and stops at its ceiling');
});

test('a swept solid is closed, and a plane is not', () => {
  // A triangle swept through a wall is a prism: 2 ends + 3 sides.
  assert.equal(facesOf(GABLE_E).length, 5, 'two ends and three sides');
  // A roof plane is one polygon with no thickness -- it is a surface, and saying otherwise
  // would give the roof a soffit the record does not state.
  const rp = { geometry: { type: 'plane', vertices: [[0, 0, 25], [10, 0, 25], [10, 5, 30], [0, 5, 30]] } };
  assert.equal(facesOf(rp).length, 1);
  const e = extent(rp);
  assert.ok(e.max[0] - e.min[0] > 0 && e.max[2] - e.min[2] > 0, 'it has extent in its own plane');
  assert.equal(triangles(rp).length, 2, 'a quadrilateral fans to two triangles');
});

test('a SWEPT solid’s faces point outward too — on every plane', () => {
  // The assertion the box test could not make. `PLANES.xz` is (x, z, y) and x cross z is
  // MINUS y, so that frame is left-handed while the other two are right-handed: an outline
  // wound one way faces out in a gable and IN in a wall. A mutation of the cap winding stayed
  // green until this existed, and the consequence on the plate is a flat sun lighting half
  // the openings from inside the house.
  for (const [name, solid] of [['sash (xz)', SASH], ['gable (yz)', GABLE_E]]) {
    const c = extent(solid);
    const mid = [(c.min[0] + c.max[0]) / 2, (c.min[1] + c.max[1]) / 2, (c.min[2] + c.max[2]) / 2];
    for (const tri of triangles(solid)) {
      const n = normalOf(tri);
      const a = tri[0];
      const away = [a[0] - mid[0], a[1] - mid[1], a[2] - mid[2]];
      const facing = n[0] * away[0] + n[1] * away[1] + n[2] * away[2];
      assert.ok(facing >= -1e-9, `${name}: a face is wound inward (${facing.toFixed(4)})`);
    }
  }
  // And a space, which is the third plane and the one a reader looks through.
  const sp = { geometry: { type: 'prism', polygon: [[35.51, 0], [40.91, 0], [40.91, 9], [35.51, 9]], z0: 2, z1: 13 } };
  const e = extent(sp);
  const mid = [(e.min[0] + e.max[0]) / 2, (e.min[1] + e.max[1]) / 2, (e.min[2] + e.max[2]) / 2];
  for (const tri of triangles(sp)) {
    const n = normalOf(tri);
    const away = [tri[0][0] - mid[0], tri[0][1] - mid[1], tri[0][2] - mid[2]];
    assert.ok(n[0] * away[0] + n[1] * away[1] + n[2] * away[2] >= -1e-9, 'a space is wound inward');
  }
});

test('a box’s faces point outward, so a flat sun shades the turned ones', () => {
  const tris = triangles(WALL_S);
  const ns = tris.map(normalOf);
  const has = (v) => ns.some((n) => Math.abs(n[0] - v[0]) < 1e-9 && Math.abs(n[1] - v[1]) < 1e-9 && Math.abs(n[2] - v[2]) < 1e-9);
  for (const v of [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]]) {
    assert.ok(has(v), `no face points ${JSON.stringify(v)} — a wound-inward face is lit backwards`);
  }
});

test('a primitive this viewer does not know is refused by name, never skipped', () => {
  // An absence is the one thing a drawing must not report silently: a solid quietly dropped
  // is a house missing a piece with nothing anywhere saying so.
  assert.throws(
    () => facesOf({ geometry: { type: 'lathe', profile: [] } }),
    /cannot build a 'lathe'/,
    'an unknown primitive must name itself',
  );
  assert.throws(() => facesOf({ geometry: { type: 'extrude', plane: 'zz', outline: [], at: 0, thickness: 1 } }), /cannot sweep the plane 'zz'/);
});

/* ------------------------------------------------------------------ the two source rules */

const SRC = dirname(fileURLToPath(import.meta.url));

function allSources(dir = SRC, out = []) {
  for (const f of readdirSync(dir)) {
    const p = join(dir, f);
    if (statSync(p).isDirectory()) { if (f !== 'data') allSources(p, out); continue; }
    if (/\.(js|jsx|mjs)$/.test(f)) out.push(p);
  }
  return out;
}

test('three is imported in exactly one file, and that file is loaded lazily', () => {
  // The bundle rule, as a property rather than as a build artefact. `three` reaches the app
  // ONLY through `round/three-scene.js`, and that module is reached only by a dynamic import
  // -- which is what keeps it out of the entry chunk AND out of no_bare_imports.test.mjs's
  // walk, since that walker deliberately does not follow `import()`.
  const importers = [];
  for (const f of allSources()) {
    if (/round[/\\]three-scene\.js$/.test(f)) continue;
    const src = readFileSync(f, 'utf8');
    if (/\bfrom\s+['"]three(\/|['"])/.test(src) || /\bimport\s+['"]three(\/|['"])/.test(src)) {
      importers.push(f.slice(SRC.length + 1));
    }
  }
  assert.deepEqual(importers, [], `three must be imported only by round/three-scene.js, not by ${importers}`);

  // and the one file that does import it is only ever reached dynamically
  const statics = [];
  for (const f of allSources()) {
    const src = readFileSync(f, 'utf8');
    if (/^\s*import[^\n]*from\s+['"][^'"]*three-scene\.js['"]/m.test(src)) statics.push(f.slice(SRC.length + 1));
  }
  assert.deepEqual(statics, [], `three-scene.js must be loaded with import(), but ${statics} import it statically`);
});

test('the model carries no colour of its own', () => {
  // Every ink and tone reaches three-scene.js through `tokens`, resolved from tokens.css. A
  // hex typed here would be a second palette that no token can move, and the Drawn Language
  // is one palette -- which is the rule WP-11.1 enforced on the four Python renderers when it
  // took them from 52 hex literals to none.
  const src = readFileSync(join(SRC, 'round', 'three-scene.js'), 'utf8');
  const hex = src.match(/#[0-9a-fA-F]{3,8}\b/g) || [];
  const hexy = src.match(/\b0x[0-9a-fA-F]+\b/g) || [];
  assert.deepEqual(hex, [], `three-scene.js carries hex colours: ${hex}`);
  assert.deepEqual(hexy, [], `three-scene.js carries 0x colours: ${hexy}`);
  // and it really does read the palette, so the assertion above is not vacuous
  assert.ok(/tokens\[/.test(src), 'three-scene.js must resolve its colours from tokens');
});
