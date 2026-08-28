/* The workbench renderer, held to the same contract as the Python one (WP-6.1).
   The other half is tests/test_sheet_symbols.py; the fixtures and the reason they carry a
   frozen placement are in tests/fixtures/sheet_symbols/README.md.

   Change one renderer without the other and both suites fail. That is the whole design:
   derive.js has claimed since WP-5.2 to be a port of build/render_plan.py "so the two
   renders of the same record cannot quietly disagree", and at WP-6.1 they disagreed about
   exterior doors, about door width and about door type — the claim was in a comment and
   nothing held it. */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

import { doors, windows, divergence, requiredWallFt, sharedEdge, interpunctTitle,
         relaxationMarks } from './sheet/derive.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const FIX = join(HERE, '..', '..', '..', 'tests', 'fixtures', 'sheet_symbols');

/* The fixture stores a level's rooms as records with `geometry`; derive.js works on the
   flattened rects levelRooms() produces. This is that flattening, and nothing more —
   if it grew a rule it would be a third renderer, which is what we are avoiding. */
function toRects(rooms) {
  return rooms.map((r) => ({
    id: r.id, type: r.type, name: r.name || r.id,
    x: r.geometry.x_ft, y: r.geometry.y_ft,
    w: r.geometry.width_ft, h: r.geometry.depth_ft,
    windows: r.windows || [], doors: r.doors || [],
    exterior_walls: r.exterior_walls || [],
    declared_width_ft: r.width_ft, declared_length_ft: r.length_ft,
  }));
}

const fixtures = readdirSync(FIX)
  .filter((f) => f.endsWith('.json'))
  .map((f) => JSON.parse(readFileSync(join(FIX, f), 'utf8')));

test('there are fixtures to check against', () => {
  assert.ok(fixtures.length > 0, 'no sheet-symbol fixtures found');
});

for (const fx of fixtures) {
  const W = fx.footprint.width_ft, H = fx.footprint.depth_ft;

  test(`${fx.plan}: the same doors are drawn as the Python renderer draws`, () => {
    for (const lv of fx.levels) {
      const rects = toRects(lv.rooms);
      const got = doors(rects, W, H);
      const exp = lv.expected;

      assert.equal(got.interior.length, exp.interior.length,
        `${lv.id}: interior door count`);
      assert.equal(got.exterior.length, exp.exterior.length,
        `${lv.id}: exterior door count`);
      assert.equal(got.undrawable.length, exp.undrawable.length,
        `${lv.id}: undrawable count — ${JSON.stringify(got.undrawable.map((u) => `${u.from}-${u.to}`))}`);

      // the same PAIRS, not merely the same tally: two renderers can agree on how many
      // doors they drew while drawing different ones
      const gotPairs = got.interior.map((d) => d.pair.slice().sort().join('|')).sort();
      const expPairs = exp.interior.map((d) => d.pair.slice().sort().join('|')).sort();
      assert.deepEqual(gotPairs, expPairs, `${lv.id}: interior door pairs`);

      const gotUn = got.undrawable.map((u) => [u.from, u.to].sort().join('|')).sort();
      const expUn = exp.undrawable.map((u) => [u.from, u.to].sort().join('|')).sort();
      assert.deepEqual(gotUn, expUn, `${lv.id}: undrawable door pairs`);

      // width and type must survive to the drawing, which is the whole of the fix
      for (const d of got.interior) {
        const key = d.pair.slice().sort().join('|');
        const e = exp.interior.find((x) => x.pair.slice().sort().join('|') === key);
        assert.ok(e, `${lv.id}: ${key} not in the contract`);
        assert.equal(d.w, e.width_ft, `${lv.id}: ${key} width`);
        assert.equal(d.type, e.type, `${lv.id}: ${key} type`);
      }
      for (const d of got.exterior) {
        const e = exp.exterior.find((x) => x.room === d.room && x.wall === d.wall);
        assert.ok(e, `${lv.id}: exterior door on ${d.room}/${d.wall} not in the contract`);
        assert.equal(d.w, e.width_ft, `${lv.id}: ${d.room} exterior width`);
      }
    }
  });

  test(`${fx.plan}: the same windows are placed as the Python renderer places`, () => {
    for (const lv of fx.levels) {
      const rects = toRects(lv.rooms);
      const drs = doors(rects, W, H);
      const got = windows(rects, W, H, 0.6, drs.exterior);
      const exp = lv.expected;
      assert.equal(got.length, exp.windows.length, `${lv.id}: window count`);
      assert.equal(got.offFootprint, exp.windows_off_footprint, `${lv.id}: off-footprint`);
      assert.equal(got.crowded, exp.windows_crowded, `${lv.id}: crowded`);
      // compared as (room, wall, position along that wall) — a room may be lit on two
      // walls, and sorting by screen x/y puts its E window among another room's S ones
      const along = (w) => ((w.wall === 'S' || w.wall === 'N') ? w.x : w.y);
      const key = (room, wall, at) => `${room}|${wall}|${at.toFixed(4)}`;
      const gotKeys = got.map((w) => key(w.room, w.wall, along(w))).sort();
      const expKeys = exp.windows.map((w) => key(w.room, w.wall, w.at_ft)).sort();
      assert.deepEqual(gotKeys, expKeys, `${lv.id}: window positions`);
    }
  });

  test(`${fx.plan}: no window is drawn over a door`, () => {
    for (const lv of fx.levels) {
      const rects = toRects(lv.rooms);
      const drs = doors(rects, W, H);
      const wins = windows(rects, W, H, 0.6, drs.exterior);
      const spans = new Map();
      const push = (room, wall, kind, a, b) => {
        const k = `${room}|${wall}`;
        if (!spans.has(k)) spans.set(k, []);
        spans.get(k).push([kind, a, b]);
      };
      for (const d of drs.exterior) push(d.room, d.wall, 'door', d.span[0], d.span[1]);
      for (const w of wins) {
        const along = (w.wall === 'S' || w.wall === 'N') ? w.x : w.y;
        push(w.room, w.wall, 'window', along - w.w / 2, along + w.w / 2);
      }
      for (const [k, items] of spans) {
        items.sort((p, q) => p[1] - q[1]);
        for (let i = 1; i < items.length; i++) {
          assert.ok(items[i][1] >= items[i - 1][2] - 1e-6,
            `${lv.id} ${k}: ${items[i - 1][0]} overlaps ${items[i][0]}`);
        }
      }
    }
  });

  test(`${fx.plan}: the same rooms are flagged as drawn off their declaration`, () => {
    for (const lv of fx.levels) {
      const got = divergence(toRects(lv.rooms)).map((d) => d.id).sort();
      assert.deepEqual(got, [...lv.expected_divergence].sort(), `${lv.id}: divergence`);
    }
  });
}

test('a door is measured by its own leaf and jambs, not a flat 3.2 ft', () => {
  // OQ 41/63, the renderer half — kept identical to test_sheet_symbols.py's version
  assert.ok(Math.abs(requiredWallFt(2.2) - 2.9) < 1e-9);
  const a = { x: 0, y: 0, w: 10, h: 10 };
  const b = { x: 10, y: 0, w: 10, h: 3.0 };
  const seg = sharedEdge(a, b);
  assert.ok(seg, 'the rooms do share a wall');
  assert.ok(seg.run >= requiredWallFt(2.2), 'a 2.2 ft closet door fits 3.0 ft of wall');
  assert.ok(seg.run < requiredWallFt(3.5), 'a 3.5 ft leaf does not');
});

test('the plate title folds only at word boundaries', () => {
  const t = interpunctTitle('Tidewater Georgian, five bays, carefully planned');
  assert.ok(t.includes('​'), 'a zero-width space follows each interpunct');
  // the words themselves survive intact — a caption that folds mid-word turned this
  // title into 'WATER GEORGIAN, FIVE CAREFULLY PLANNED', which is a different house
  assert.equal(t.replace(/[·​]/g, ' ').replace(/\s+/g, ' ').trim(),
    'Tidewater Georgian, five bays, carefully planned');
});

/* A relaxation mark goes on a wall or it goes in the caption. Both renderers decide this
   the same way — the Python half is tests/test_sheet_symbols.py. The case that mattered:
   a CP mark carries `runs` and not a from/to extent, and the sheet used to drop it at the
   middle of the plan, which on the Tidewater placement put it inside the drawing room. */
test('a relaxation mark is drawn on the wall it is true of, or not drawn', () => {
  const W = 60, H = 40;
  const heur = { off_ft: 2, axis: 'y', at_ft: 27, level: 0, from_ft: 10, to_ft: 20 };
  const cp = { off_ft: 3, axis: 'y', at_ft: 27, level: 0, runs: [[51, 60], [0, 4]] };
  const nowhere = { off_ft: 4, axis: 'y', at_ft: 27, level: 0 };
  const other = { off_ft: 5, axis: 'x', at_ft: 13, level: 1, runs: [[0, 40]] };
  const r = relaxationMarks([heur, cp, nowhere, other], 0, W, H);

  assert.equal(r.drawn.length, 2, 'the level-1 mark belongs to the other plate');
  assert.equal(r.unlocated.length, 1);
  assert.equal(r.unlocated[0].off_ft, 4, 'a mark on no wall is named, never placed');

  const [d0, d1] = r.drawn;
  assert.deepEqual(d0.runs, [[10, 20]], 'a heuristic mark keeps the cut it recorded');
  assert.equal(d0.at, 15);
  // the △ hangs on the LONGEST real run, and 51–60 is nine feet against four
  assert.equal(d1.at, 55.5);
  assert.equal(d1.runs.length, 2, 'both measured pieces of the line are drawn');
  // and never at the middle of the plan, which is where the drawing room was
  assert.notEqual(d1.at, W / 2);
});

test('a relaxation run that leaves the sheet is clipped, and one with nothing left is not drawn', () => {
  const r = relaxationMarks([
    { off_ft: 2, axis: 'x', at_ft: 5, level: 0, runs: [[-8, 12]] },
    { off_ft: 2, axis: 'x', at_ft: 6, level: 0, runs: [[80, 96]] },
  ], 0, 60, 40);
  assert.deepEqual(r.drawn.map((d) => d.runs), [[[0, 12]]]);
  assert.equal(r.unlocated.length, 1, 'a run wholly off the plate locates nothing');
});
