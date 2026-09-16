/* The furniture key, pinned where a browser is not needed (WP-13.2).

   `sheet/furnitureKey.js` is the browser sheet's port of build/render_plan.py's key fitter,
   in feet rather than sheet px. tests/test_furniture_key.py drives the Python side over the
   SAME hand-built room (a 20 x 15 ft room with a sofa in its NW corner and a label across its
   middle) and expects the same corner, the same orientation and the same size to the px, so
   the two fitters cannot quietly disagree about where a key goes. The fixtures are hand-built
   on purpose: a shipped plan re-solves on `auto` and would pin the machine. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  KEY, PX_PER_FT, keyCount, keyEntries, keyLines, blockSize, clearFloor, place, fitKey,
  numeralAt, furnitureKeyPlan, monoWidth,
} from './sheet/furnitureKey.js';

const px = (v) => v / PX_PER_FT;

test('a count is read from the record\'s own words by a closed rule and never guessed', () => {
  assert.equal(keyCount('nightstands, pair'), 2);
  assert.equal(keyCount('sofas, pair, facing'), 2);
  assert.equal(keyCount('two chairs and a table'), null, 'a conjunction joins a second item');
  assert.equal(keyCount('six to eight side chairs, set against the walls'), null, 'a band is not a count');
  assert.equal(keyCount('eight to twelve chairs, movable'), null);
  assert.equal(keyCount('shelf, 14 in deep'), null, 'a figure inside the name is a dimension');
  assert.equal(keyCount('table, seats 4'), null, 'seats are not tables');
  assert.equal(keyCount('queen bed'), null);
  assert.equal(keyCount('four hall chairs'), 4);
  assert.equal(keyCount(''), null);
});

const room = () => ({
  id: 'parlor', name: 'Parlor', x: 10, y: 5, w: 20, h: 15,
  fixture_layout: [{ item: 'small sink', x_ft: 28, y_ft: 5, width_ft: 1.5, depth_ft: 1.3, wall: 'S' },
                   { item: 'unplaced basin', unplaced: { reason: 'no wall' } }],
  furniture_layout: [
    { item: 'sofa, pair', x_ft: 10, y_ft: 17.2, width_ft: 7, depth_ft: 2.8, wall: 'N', marks: [{ rect: [10, 17.2, 7, 2.8] }] },
    { item: 'tea table', x_ft: 18, y_ft: 11, width_ft: 3.5, depth_ft: 2.5, marks: [{ rect: [18, 11, 3.5, 2.5] }] },
    { item: 'unplaced chair', unplaced: { reason: 'no floor' } },
  ],
});

test('entries are numbered in drawing order, fixtures first, and the unplaced take no numeral', () => {
  const e = keyEntries(room());
  assert.deepEqual(e.map((x) => [x.n, x.item, x.kind]),
    [[1, 'small sink', 'fixture'], [2, 'sofa, pair', 'furniture'], [3, 'tea table', 'furniture']]);
});

/* WP-13.6: the pieces of one counted item are ONE key line and ONE numeral. The fixture is
   spelled here and in tests/test_furniture_grammar.py in the same words, and both files expect
   the same two lines, so the two spellings of `_key_groups` cannot quietly disagree about what
   a set of chairs is keyed as. */
const counted = () => ({
  id: 'dining', name: 'Dining Room', x: 0, y: 0, w: 20, h: 15,
  furniture_layout: [
    { item: 'dining chairs', piece: 1, of: 8, x_ft: 0, y_ft: 0, width_ft: 1, depth_ft: 1, marks: [{ rect: [0, 0, 1, 1] }] },
    { item: 'dining chairs', piece: 2, of: 8, x_ft: 2, y_ft: 0, width_ft: 1, depth_ft: 1, marks: [{ rect: [2, 0, 1, 1] }] },
    { item: 'sideboard', x_ft: 4, y_ft: 0, width_ft: 1, depth_ft: 1, marks: [{ rect: [4, 0, 1, 1] }] },
  ],
});

test('the pieces of a counted item share one numeral and one key line, and say the shortfall', () => {
  const es = keyEntries(counted());
  assert.deepEqual(es.map((e) => [e.n, (e.rects || [e.rect]).length]), [[1, 2], [2, 1]],
    'two chairs are one entry with two rectangles; the sideboard is the next numeral');
  assert.deepEqual(keyLines(es), ['1 DINING CHAIRS x2 OF 8', '2 SIDEBOARD']);
  // a set drawn whole says x2 and no shortfall
  const whole = counted();
  whole.furniture_layout[0].of = 2; whole.furniture_layout[1].of = 2;
  assert.deepEqual(keyLines(keyEntries(whole)), ['1 DINING CHAIRS x2', '2 SIDEBOARD']);
  // and one numeral stands on EVERY piece
  const { byRoom } = furnitureKeyPlan([counted()]);
  const nums = byRoom.get('dining').numerals;
  assert.equal(nums.length, 3, 'three marks carry a numeral');
  assert.deepEqual(nums.map((u) => u.n), [1, 1, 2]);
});

test('a key line is the numeral and the name whole, in capitals, never abbreviated', () => {
  const lines = keyLines(keyEntries(room()));
  assert.deepEqual(lines, ['1 SMALL SINK', '2 SOFA, PAIR', '3 TEA TABLE']);
  const long = keyLines([{ n: 7, item: '  desk (any bedroom   occupied by anyone under twenty-five) ' }]);
  assert.equal(long[0], '7 DESK (ANY BEDROOM OCCUPIED BY ANYONE UNDER TWENTY-FIVE)');
});

test('the floor is the room less the wall bodies on its edges, decided by each strip\'s shape', () => {
  // a partition along the TOP crosses the left edge too; it must shrink the top, not the left
  const floor = clearFloor([0, 0, 20, 15], [[-3, -0.2, 25, 0.2], [-0.2, -3, 0.2, 20], [19.8, 2, 20.2, 9]]);
  assert.deepEqual(floor.map((v) => +v.toFixed(3)), [0.2, 0.2, 19.8, 15]);
});

test('a key sits flush in a clear corner at the preferred size, and moves corner when one is taken', () => {
  const lines = ['1 SOFA', '2 TEA TABLE'];
  const clear = fitKey([0, 0, 20, 15], [], lines);
  assert.equal(clear.corner, 'NW');
  assert.equal(clear.turned, false);
  assert.ok(Math.abs(clear.size - KEY.preferred) < 1e-9);
  assert.ok(Math.abs(clear.x0 - KEY.pad) < 1e-9 && Math.abs(clear.y0 - KEY.pad) < 1e-9);
  // a sofa filling the NW corner: the key is pushed, and the nearest clear place wins
  const sofa = [0, 0, 7, 2.8];
  const pushed = fitKey([0, 0, 20, 15], [sofa], lines);
  assert.equal(pushed.turned, false);
  assert.ok(Math.abs(pushed.size - KEY.preferred) < 1e-9, 'the size does not fall for a push');
  assert.ok(pushed.y0 >= 2.8 + KEY.pad - 1e-9 || pushed.x0 >= 7 + KEY.pad - 1e-9, 'it is clear of the sofa');
});

test('a slot room turns the key only where turning earns a materially larger letter', () => {
  const lines = ['1 HALL CHAIRS IN A ROW DOWN ONE SIDE', '2 SETTEE OR BENCH'];
  const [bw] = blockSize(lines, KEY.preferred);
  // a passage narrower than the widest line flat, and long: the key runs with the room
  const passage = fitKey([0, 0, bw * 0.6, 40], [], lines);
  assert.equal(passage.turned, true);
  assert.ok(Math.abs(passage.size - KEY.preferred) < 1e-9);
  // a room that holds it flat at the preferred size is never turned
  const square = fitKey([0, 0, bw * 1.5, bw * 1.5], [], lines);
  assert.equal(square.turned, false);
});

test('a key no corner can hold at the floor, flat or turned, is refused and not squeezed', () => {
  const lines = ['1 HOT WATER CYLINDER, WHERE THE ROOM IS AN AIRING CUPBOARD'];
  const [bw, bh] = blockSize(lines, KEY.floor);
  assert.equal(fitKey([0, 0, bw * 0.8, bw * 0.8], [], lines), null);
  // and the refusal is about the room, not the size: a room a hair larger holds it
  assert.ok(fitKey([0, 0, bw + 2 * KEY.pad + 0.1, bh + 2 * KEY.pad + 0.1], [], lines));
});

test('a numeral goes inside a mark that can hold it, beside a mark that cannot, on the room side', () => {
  const roomBox = [0, 0, 20, 15];
  const inside = numeralAt([2, 2, 5, 5], 'N', 3, roomBox);
  assert.equal(inside.anchor, 'middle');
  assert.ok(inside.x > 2 && inside.x < 5 && inside.y > 2 && inside.y < 5);
  // a hook rail 0.4 ft wide against the west wall: the numeral stands to its right, on the floor
  const thin = numeralAt([0, 3, 0.4, 7], 'W', 2, roomBox);
  assert.equal(thin.anchor, 'start');
  assert.ok(thin.x > 0.4, 'beside it, off the wall');
  // seated on the north wall (top of the room, y down): beside means below
  const north = numeralAt([3, 0, 9, 0.3], 'N', 1, roomBox);
  assert.ok(north.y > 0.3, 'below the rail, on the room side');
  // a numeral that would land on the label goes beside the mark instead: the label covers
  // the mark's centre and its top, so the numeral stands below it
  const label = [[1, 1, 9, 4]];
  const dodged = numeralAt([2, 2, 5, 5], null, 4, roomBox, KEY.numeral, label);
  assert.ok(dodged.box[1] >= 4, `off the label: ${dodged.box}`);
  assert.ok(dodged.y > 5, 'below the mark');
  // and where every side is under the label too, it stays INSIDE the mark rather than
  // wandering: the mark is the one place a numeral is never read as somebody else's
  const smothered = numeralAt([2, 2, 5, 5], null, 4, roomBox, KEY.numeral, [[1, 1, 9, 6]]);
  assert.equal(smothered.anchor, 'middle');
  assert.ok(smothered.y > 2 && smothered.y < 5);
});

test('the plan names every drawn item and refuses to the margin by room', () => {
  const r = room();
  const plan = furnitureKeyPlan([r], {
    partitions: [{ x: 10, y: 4.8, w: 20, h: 0.4 }],
    labelBox: () => ({ w: 6, h: 1 }),
  });
  const kr = plan.byRoom.get('parlor');
  assert.equal(kr.lines.length, 3);
  assert.equal(kr.numerals.length, 3);
  assert.ok(kr.fit, 'a 20 x 15 parlour holds a three-line key');
  assert.deepEqual(plan.margin, []);
  // the same room with a name no corner can hold: refused, named, not squeezed
  const cramped = { ...r, w: 4, h: 4,
    furniture_layout: [{ item: 'hot water cylinder, where the room is an airing cupboard',
      x_ft: 10, y_ft: 5, width_ft: 2, depth_ft: 2, marks: [{ rect: [10, 5, 2, 2] }] }],
    fixture_layout: [] };
  const p2 = furnitureKeyPlan([cramped], {});
  assert.equal(p2.byRoom.get('parlor').fit, null);
  assert.equal(p2.margin.length, 1);
  assert.equal(p2.margin[0].name, 'PARLOR');
  assert.match(p2.margin[0].lines[0], /^1 HOT WATER CYLINDER, WHERE THE ROOM IS AN AIRING CUPBOARD$/);
});

/* THE PARITY FIXTURE. tests/test_furniture_key.py builds this exact room in px and asserts
   the same answers; the numbers here are the ones that file states, so a change to either
   fitter that moves a key is caught on both sides. */
export const PARITY = {
  floor: [0, 0, 20, 15],
  // a sofa in the NW corner, a piano in the NE, chairs in the SW, a table in the SE, and the
  // label across the middle: every corner has something in it, and the NW push is the shortest
  obstacles: [[0, 0, 7, 2.8], [13, 0, 20, 5], [0, 10, 6, 15], [14, 10, 20, 15], [7, 7, 13, 8]],
  lines: ['1 SOFAS, PAIR, FACING', '2 GRAND PIANO', '3 TEA TABLE'],
};

test('the parity fixture: NW, flat, at the preferred size, pushed below the sofa', () => {
  const fit = fitKey(PARITY.floor, PARITY.obstacles, PARITY.lines);
  assert.equal(fit.corner, 'NW');
  assert.equal(fit.turned, false);
  assert.ok(Math.abs(fit.size * PX_PER_FT - 6.0) < 1e-9);
  assert.ok(Math.abs(fit.x0 * PX_PER_FT - 3.0) < 1e-6, `x0 ${fit.x0 * PX_PER_FT} px`);
  assert.ok(Math.abs(fit.y0 * PX_PER_FT - (2.8 * PX_PER_FT + 3.0)) < 1e-6, `y0 ${fit.y0 * PX_PER_FT} px`);
  assert.ok(Math.abs(monoWidth(PARITY.lines[0], px(6)) * PX_PER_FT - 0.6 * 21 * 6) < 1e-9);
  // the sofa alone, and the NE corner is free: the nearest clear corner wins over a push
  assert.equal(fitKey(PARITY.floor, [PARITY.obstacles[0]], PARITY.lines).corner, 'NE');
});
