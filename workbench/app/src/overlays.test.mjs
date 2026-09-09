/* The overlays and the modifiers (WP-12.5).

   THE ASSERTIONS THIS FILE EXISTS FOR ARE THE TWO THAT CANNOT FIRE ON THE SHIPPED CORPUS.
   Lifting the three analytic rules out of `Sheet.jsx`'s JSX found both, and neither is
   reachable from any record in the tree:

     · three room records state `daylight.depth_multiplier: 0` — a MEASURED ZERO — and
       `mult || 2.25` turned it into the default. Those types are placed 12 times across 6
       plans including both shipped ones, and **0 of the 12 draw a wash**, because none of them
       declares a window and the overlay is gated on `litWalls`. Real in the code, authorised
       by the records, unreachable from the corpus.
     · the privacy ramp has NO BOUND IN EITHER DIRECTION. `if (!rank) return null` catches
       rank 0 as falsy and nothing catches anything else: rank −1 washes at **−0.06**, a
       negative opacity, and rank 6 at **0.29**, darker than the deepest legitimate room.
       `check_rooms.py::PRIVACY_BANDS` admits 0 (*"0 street"*) and no record carries it, so
       rank 0 is separately an EVALUATED rank rendered as unjudged.

   THE FIRST VERSION OF THE RANK TEST WAS ABOUT NOTHING, AND A MUTATION SAID SO. It asserted
   `privacyOpacity(0) === null`, which the shipped expression ALSO returns — reverting the
   whole function left 24 of 24 green. The value cannot distinguish them; the out-of-band ranks
   can, and they are what the test drives now.

   So both are DRIVEN by hand (WP-8.11's rule), and each test asserts its own premise, so the
   day a record does state one the suite says so rather than the fixture quietly becoming
   redundant.

   The fixture is two elements at NEGATIVE x on purpose, on WP-11.15's precedent: a wing at
   positive x lets a wrong sign look plausible. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import {
  DAYLIGHT_MULTIPLIER_FALLBACK,
  PRIVACY_BASE,
  PRIVACY_RAMP_MAX,
  PRIVACY_RAMP_MIN,
  PRIVACY_RANGE,
  daylightReachFt,
  isWet,
  privacyOpacity,
  privacyRefusal,
} from './sheet/overlayRules.js';
import {
  ELEMENT_STEP_FT,
  FREE_VIEW_OVERLAYS,
  bayGrid,
  cutPlane,
  datumLines,
  daylightVolumes,
  explodeOffsets,
  privacyWashes,
  relaxationMarks,
  transferCount,
  wetPrisms,
} from './round/overlays.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, '..', '..', '..');

/* ------------------------------------------------------------------ fixtures */

const META = {
  parlor: { privacy_rank: 2, daylight_multiplier: 2.25, plumbing: 'none', function_class: 'public' },
  bath: { privacy_rank: 5, daylight_multiplier: 1.6, plumbing: 'heavy', function_class: 'sanitary' },
  kitchen: { privacy_rank: 3, daylight_multiplier: 1.8, plumbing: 'heavy', function_class: 'service' },
  // the shape the three real records have: a STATED zero, not a missing value
  closet: { privacy_rank: 4, daylight_multiplier: 0, plumbing: 'none', function_class: 'storage' },
  // the rank check_rooms.py's band admits and no record carries
  street: { privacy_rank: 0, daylight_multiplier: 2.0, plumbing: 'none', function_class: 'outdoor' },
  // a type the catalogue does not hold at all
  unknown: {},
};

function scene(opts = {}) {
  const els = opts.elements || [{ id: 'main', role: 'main', rect: { x_ft: 0, y_ft: 0, width_ft: 40, depth_ft: 30 } }];
  return {
    scene_version: '0.1.0',
    grid: { bays: 4, module_ft: 10, source: 'footprint' },
    bounds: { min: [-1.292, -1.292, 0], max: [40, 30, 28] },
    datums: [
      { id: 'grade', label: "0'-0\"", z_ft: 0, class: 'grade', kind: 'editorial' },
      { id: 'floor-g', label: "1'-6\"", z_ft: 1.5, class: 'floor', kind: 'derived' },
      { id: 'eave', label: "22'-0\"", z_ft: 22, class: 'eave', kind: 'derived' },
    ],
    storeys: [
      { id: 'g', index: 0, floor_z_ft: 1.5, ceiling_z_ft: 11.5, storey_height_ft: 11 },
      { id: 'u', index: 1, floor_z_ft: 12.5, ceiling_z_ft: 21.5, storey_height_ft: 10 },
    ],
    elements: els,
    spaces: opts.spaces || [
      { id: 'p1', type: 'parlor', level: 0, element: 'main', geometry: { type: 'prism', polygon: [[0, 0], [16, 0], [16, 14], [0, 14]], z0: 1.5, z1: 11.5 } },
      { id: 'b1', type: 'bath', level: 1, element: 'main', geometry: { type: 'prism', polygon: [[0, 0], [8, 0], [8, 8], [0, 8]], z0: 12.5, z1: 21.5 } },
      { id: 'k1', type: 'kitchen', level: 0, element: 'main', geometry: { type: 'prism', polygon: [[16, 0], [30, 0], [30, 14], [16, 14]], z0: 1.5, z1: 11.5 } },
      { id: 'c1', type: 'closet', level: 0, element: 'main', geometry: { type: 'prism', polygon: [[30, 0], [34, 0], [34, 4], [30, 4]], z0: 1.5, z1: 11.5 } },
    ],
    marks: opts.marks || [
      { id: 'relaxation-0', x_ft: 12, y_ft: 0, level: 0 },
      { id: 'relaxation-1', why: 'the placement recorded this cut with no position' },
    ],
    cut_height_ft: 4.0,
  };
}

/* A placed plan in the shape `levelRooms` reads: rooms carrying `geometry` in place, which is
   what `build/geometry.py::write_record` writes. */
function plan(rooms) {
  return {
    id: 'fixture',
    footprint: { width_ft: 40, depth_ft: 30, bay_module_ft: 10, bays: 4, blocks: [] },
    levels: [{ index: 0, rooms }],
  };
}

const LIT_PARLOR = {
  id: 'p1', type: 'parlor', width_ft: 16, length_ft: 14, window_head_ft: 8,
  windows: [{ wall: 'S', count: 3 }],
  geometry: { x_ft: 0, y_ft: 0, width_ft: 16, depth_ft: 14 },
};

/* ------------------------------------------------------------------ the ramp */

test('the privacy ramp is byte-for-byte the one the sheet has drawn since WP-5.2', () => {
  // The lift must not move a wash a reader has been looking at. These five are the shipped
  // expression `0.04 + ((rank - 1) / 4) * 0.20` evaluated by hand.
  const want = { 1: 0.04, 2: 0.09, 3: 0.14, 4: 0.19, 5: 0.24 };
  for (const [rank, op] of Object.entries(want)) {
    assert.ok(Math.abs(privacyOpacity(Number(rank)) - op) < 1e-12,
      `rank ${rank} washes ${privacyOpacity(Number(rank))}, and the sheet drew ${op}`);
  }
  assert.equal(PRIVACY_RAMP_MIN, 1);
  assert.equal(PRIVACY_RAMP_MAX, 5);
  // a tolerance, because 0.04 + 0.20 is 0.24000000000000002 in IEEE-754 and the top of the
  // ramp is a drawing decision rather than a number anyone reads back
  assert.ok(Math.abs((PRIVACY_BASE + PRIVACY_RANGE) - 0.24) < 1e-12);
});

test('an unranked room is unjudged and a street-rank room is REFUSED, and the two say different things', () => {
  assert.equal(privacyOpacity(undefined), null, 'an unranked room may not be washed');
  assert.match(privacyRefusal(undefined), /states no privacy_rank/);

  // Rank 0 is AUTHORISED by check_rooms.py's band and carried by no record. The shipped
  // expression also returns null here -- `!0` is true -- so this assertion is about the
  // REASON and not the value, and `privacyRefusal` is the only thing that can tell them apart.
  assert.equal(privacyOpacity(0), null);
  assert.match(privacyRefusal(0), /outside the ramp/);
  assert.notEqual(privacyRefusal(0), privacyRefusal(undefined),
    'unjudged and refused must not be the same sentence — three states, never two');
});

test('THE RAMP IS BOUNDED IN BOTH DIRECTIONS, which is the half a mutation can see', () => {
  // The shipped expression has no bound at all and `if (!rank)` covers exactly one bad case
  // by accident. These two are what actually distinguish it, and they are why the rank test
  // above could be reverted with the suite staying green.
  const shipped = (rank) => (!rank ? null : PRIVACY_BASE + ((rank - 1) / 4) * PRIVACY_RANGE);

  assert.ok(shipped(-1) < 0, `the shipped ramp gives ${shipped(-1)} for rank −1`);
  assert.equal(privacyOpacity(-1), null, 'a negative opacity is not a drawing decision');
  assert.match(privacyRefusal(-1), /outside the ramp/);

  assert.ok(shipped(6) > PRIVACY_BASE + PRIVACY_RANGE,
    `the shipped ramp gives ${shipped(6)} for rank 6, darker than the deepest legitimate room`);
  assert.equal(privacyOpacity(6), null);
  assert.match(privacyRefusal(6), /outside the ramp/);
});

test('the corpus really does not carry rank 0, so the case above is driven and not measured', () => {
  const fs = readFileSync(join(ROOT, 'build', 'check_rooms.py'), 'utf8');
  assert.match(fs, /0 street, 1 threshold/,
    'check_rooms.py no longer states the band this test rests on');
});

/* ------------------------------------------------------------------ daylight */

test('daylight reach is the room\'s own head times its own multiplier', () => {
  assert.equal(daylightReachFt({ window_head_ft: 8 }, { daylight_multiplier: 2.25 }), 18);
  assert.ok(Math.abs(daylightReachFt({ window_head_ft: 7 }, { daylight_multiplier: 1.6 }) - 11.2) < 1e-12,
    '1.6 * 7 is 11.200000000000001 in IEEE-754; the reach is a length, not a byte');
  // a type the catalogue does not hold falls back, and the fallback is named
  assert.equal(daylightReachFt({ window_head_ft: 8 }, {}), 8 * DAYLIGHT_MULTIPLIER_FALLBACK);
  assert.equal(daylightReachFt({ window_head_ft: 8 }, undefined), 8 * DAYLIGHT_MULTIPLIER_FALLBACK);
});

test('A STATED ZERO IS NOT A MISSING VALUE: depth_multiplier 0 reaches nothing', () => {
  // THE DRIVEN CASE. `mult || 2.25` gave 18 ft of wash to a closet whose record says none.
  assert.equal(daylightReachFt({ window_head_ft: 8 }, META.closet), 0);
  const naive = (META.closet.daylight_multiplier || DAYLIGHT_MULTIPLIER_FALLBACK) * 8;
  assert.equal(naive, 18, 'the shipped `||` expression washed a stated zero to 18 ft');
});

test('the daylight volume is drawn only on walls the placement lit, and never for a zero reach', () => {
  const vols = daylightVolumes(scene(), plan([LIT_PARLOR]), META);
  assert.ok(vols.length > 0, 'the fixture must actually reach the code under test');
  assert.equal(vols.length, 1, 'one lit wall, one volume');
  const v = vols[0];
  assert.equal(v.wall, 'S');
  assert.equal(v.reach_ft, 18);
  // clamped to the room, which is 14 ft deep against an 18 ft reach
  assert.equal(v.depth_ft, 14);
  assert.equal(v.z0_ft, 1.5);
  assert.equal(v.z1_ft, 11.5);

  // the same room with a zero multiplier draws nothing at all
  const zero = daylightVolumes(scene(), plan([{ ...LIT_PARLOR, type: 'closet' }]), META);
  assert.equal(zero.length, 0, 'a stated zero reach must draw no volume');
});

/* ------------------------------------------------------------------ wet */

test('the wet predicate is the sheet\'s, and both of its clauses are reachable', () => {
  assert.equal(isWet(META.kitchen), true, 'plumbing: heavy');
  assert.equal(isWet(META.bath), true, 'function_class: sanitary');
  assert.equal(isWet(META.parlor), false);
  assert.equal(isWet({ plumbing: 'light' }), false, 'a bar sink is not a stack');
  assert.equal(isWet(undefined), false);
});

test('the wet prisms are exactly the spaces the sheet would mark, at their own storey heights', () => {
  const p = wetPrisms(scene(), META);
  assert.deepEqual(p.map((x) => x.room).sort(), ['b1', 'k1']);
  const bath = p.find((x) => x.room === 'b1');
  assert.equal(bath.z0_ft, 12.5);
  assert.equal(bath.z1_ft, 21.5);
  // the parlor and the closet are dry and must not appear
  assert.equal(p.find((x) => x.room === 'p1'), undefined);
});

/* ------------------------------------------------------------------ privacy washes */

test('a privacy wash is refused by name rather than dropped in silence', () => {
  const withStreet = scene({
    spaces: [
      { id: 's1', type: 'street', level: 0, geometry: { polygon: [[0, 0], [4, 0], [4, 4], [0, 4]], z0: 0, z1: 1 } },
      { id: 'u1', type: 'unknown', level: 0, geometry: { polygon: [[4, 0], [8, 0], [8, 4], [4, 4]], z0: 0, z1: 1 } },
      { id: 'p1', type: 'parlor', level: 0, geometry: { polygon: [[8, 0], [20, 0], [20, 14], [8, 14]], z0: 1.5, z1: 11.5 } },
    ],
  });
  const { drawn, refused } = privacyWashes(withStreet, META);
  assert.deepEqual(drawn.map((d) => d.room), ['p1']);
  assert.equal(drawn[0].opacity, 0.09);
  assert.deepEqual(refused.map((r) => r.room).sort(), ['s1', 'u1']);
  const s = refused.find((r) => r.room === 's1');
  const u = refused.find((r) => r.room === 'u1');
  assert.notEqual(s.why, u.why, 'a refused rank and an unranked type are different findings');
});

/* ------------------------------------------------------------------ grid */

test('the grid is derive.js::bayLines, on the element\'s own rect, up to the eave', () => {
  const g = bayGrid(scene());
  assert.equal(g.refused, undefined);
  assert.deepEqual(g.lines.map((l) => l.x_ft), [10, 20, 30]);
  assert.equal(g.lines[0].z1_ft, 22, 'the grid rises to the eave datum');
  assert.equal(g.lines[0].y0_ft, 0);
  assert.equal(g.lines[0].y1_ft, 30);
});

test('a record with no bay module is refused, not defaulted', () => {
  const s = scene();
  s.grid = { bays: null, module_ft: null, source: 'footprint' };
  const g = bayGrid(s);
  assert.equal(g.lines.length, 0);
  assert.match(g.refused, /no bay module/);
});

test('the grid is laid on the element\'s rect and not on the origin', () => {
  // a west wing at NEGATIVE x: a grid laid from 0 would miss it entirely
  const s = scene({
    elements: [{ id: 'w', role: 'main', rect: { x_ft: -34, y_ft: 0, width_ft: 40, depth_ft: 30 } }],
  });
  assert.deepEqual(bayGrid(s).lines.map((l) => l.x_ft), [-24, -14, -4]);
});

/* ------------------------------------------------------------------ datums */

test('the datum label is the record\'s own string and is not reformatted', () => {
  const d = datumLines(scene());
  assert.equal(d.length, 3);
  assert.equal(d.find((x) => x.class === 'eave').label, "22'-0\"");
});

/* ------------------------------------------------------------------ explode */

test('explode by level lifts each storey by k times ITS OWN height, cumulatively', () => {
  const e = explodeOffsets(scene(), { mode: 'levels', k: 1 });
  assert.deepEqual(e.byLevel[0], [0, 0, 0], 'the ground storey does not move');
  assert.deepEqual(e.byLevel[1], [0, 0, 11], 'the upper storey lifts by the GROUND storey height');
  const half = explodeOffsets(scene(), { mode: 'levels', k: 0.5 });
  assert.deepEqual(half.byLevel[1], [0, 0, 5.5]);
});

test('the roof rides on the top storey rather than lifting again', () => {
  const e = explodeOffsets(scene(), { mode: 'levels', k: 1 });
  assert.equal(e.roofRidesOn, 1,
    'a roof that separates from its own storey draws a building with an extra floor');
});

test('a one-element scene reports that there is nothing to separate', () => {
  const e = explodeOffsets(scene(), { mode: 'elements', k: 1 });
  assert.deepEqual(e.byElement, {});
  assert.equal(e.note, 'one element — nothing to separate');
});

test('an element separates along the axis of its OWN offset, derived from the rects', () => {
  // the record carries no `attached_to`; a WEST wing must move west
  const s = scene({
    elements: [
      { id: 'main', role: 'main', rect: { x_ft: 0, y_ft: 0, width_ft: 40, depth_ft: 30 } },
      { id: 'dep', role: 'dependency', rect: { x_ft: -34, y_ft: 5, width_ft: 20, depth_ft: 20 } },
    ],
  });
  const e = explodeOffsets(s, { mode: 'elements', k: 1 });
  assert.deepEqual(e.byElement.main, [0, 0, 0]);
  assert.deepEqual(e.byElement.dep, [-ELEMENT_STEP_FT, 0, 0],
    'a west wing must move WEST; a fixture at positive x would let a wrong sign look plausible');
});

test('an element concentric with the main block is refused rather than sent somewhere plausible', () => {
  const s = scene({
    elements: [
      { id: 'main', role: 'main', rect: { x_ft: 0, y_ft: 0, width_ft: 40, depth_ft: 30 } },
      { id: 'core', role: 'dependency', rect: { x_ft: 10, y_ft: 7.5, width_ft: 20, depth_ft: 15 } },
    ],
  });
  const e = explodeOffsets(s, { mode: 'elements', k: 1 });
  assert.deepEqual(e.byElement.core, [0, 0, 0]);
  assert.equal(e.refused.length, 1);
  assert.match(e.refused[0].why, /no direction/);
});

/* ------------------------------------------------------------------ cut */

test('the level cut takes the height the record already states', () => {
  const c = cutPlane(scene(), { axis: 'level' });
  assert.deepEqual(c, { axis: 'z', at_ft: 4.0, from: 'scene.cut_height_ft' });
});

test('a cut with no position is refused', () => {
  assert.match(cutPlane(scene(), { axis: 'x' }).refused, /needs a position/);
  assert.equal(cutPlane(scene(), {}), null);
});

/* ------------------------------------------------------------------ relaxations */

test('a mark the placement could not locate is named and never placed somewhere plausible', () => {
  const { drawn, unlocated } = relaxationMarks(scene());
  assert.equal(drawn.length, 1);
  assert.equal(unlocated.length, 1);
  assert.equal(unlocated[0].id, 'relaxation-1');
});

/* ------------------------------------------------------------------ transfers */

test('the transfer count is READ out of the disclosure and never recomputed', () => {
  assert.equal(transferCount([
    { id: 'transfers', text: '14 UPPER WALL LINE(S) LAND ON NO WALL BELOW — EACH IS A TRANSFER BEAM' },
  ]), 14);
  assert.equal(transferCount([{ id: 'other', text: 'something else' }]), 0,
    'no transfer disclosure means no transfer beams');
  assert.equal(transferCount([]), 0);
  assert.equal(transferCount([{ id: 'transfers', text: 'MANY UPPER WALL LINES' }]), null,
    'a disclosure whose figure cannot be read is unjudged, not zero');
});

/* ------------------------------------------------------------------ the free view */

test('only the overlays true from any angle survive a free view', () => {
  assert.deepEqual([...FREE_VIEW_OVERLAYS].sort(), ['grid', 'privacy', 'relaxations']);
  for (const id of ['datums', 'daylight', 'wet', 'plate']) {
    assert.ok(!FREE_VIEW_OVERLAYS.includes(id), `${id} is read off a plan and means nothing turned`);
  }
});

/* ------------------------------------------------------------------ one rule, not two */

test('neither surface spells an analytic rule of its own', () => {
  const sheet = readFileSync(join(HERE, 'sheet', 'Sheet.jsx'), 'utf8');
  const round = readFileSync(join(HERE, 'round', 'overlays.js'), 'utf8');
  // the ramp's shipped expression, the `||` that ate a stated zero, and the wet predicate
  for (const [src, name] of [[sheet, 'Sheet.jsx'], [round, 'overlays.js']]) {
    assert.ok(!/\(\s*rank\s*-\s*1\s*\)\s*\/\s*4/.test(src),
      `${name} re-spells the privacy ramp; overlayRules.js owns it`);
    assert.ok(!/daylight_multiplier\s*\|\|/.test(src),
      `${name} re-spells the daylight fallback with \`||\`, which eats a stated zero`);
    assert.ok(!/plumbing\s*===\s*'heavy'/.test(src),
      `${name} re-spells the wet predicate; overlayRules.js owns it`);
  }
  const rules = readFileSync(join(HERE, 'sheet', 'overlayRules.js'), 'utf8');
  assert.match(rules, /plumbing === 'heavy'/, 'the guard above must be exercised, not vacuous');
});
