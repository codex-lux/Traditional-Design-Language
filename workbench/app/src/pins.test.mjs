/* FINDINGS PINNED WHERE THEY FALL (Phase 17, WP-17.5): `sheet/pins.js` gathers a room's findings
   into one pin at its north-east corner, in the worst severity among them, and places none it
   cannot locate. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { pinsOf, pinTally } from './sheet/pins.js';

const rooms = [{ id: 'hall', x: 0, y: 0, w: 10, h: 8 }, { id: 'dining', x: 10, y: 0, w: 14, h: 12 }];

test('one pin per room, carrying its count and its worst severity', () => {
  const pins = pinsOf([
    { id: 'a', at: 'dining', severity: 'minor' },
    { id: 'b', at: 'dining', severity: 'fatal' },
    { id: 'c', room: 'hall', severity: 'serious' },
  ], rooms);
  const by = Object.fromEntries(pins.map((p) => [p.room, p]));
  assert.equal(by.dining.n, 2);
  assert.equal(by.dining.worst, 'fatal', 'the worst of the room\'s findings, whatever the order');
  // and in the other order (the second audit: minor-then-fatal let "the last finding's" pass)
  const rev = pinsOf([{ id: 'b', at: 'dining', severity: 'fatal' }, { id: 'a', at: 'dining', severity: 'minor' }], rooms);
  assert.equal(rev[0].worst, 'fatal', 'fatal first and minor last is still fatal');
  assert.deepEqual(by.dining.ids, ['a', 'b']);
  assert.equal(by.hall.worst, 'serious', 'a finding\'s room is read from `at` or `room`');
});

test('a pin stands inside its room, at its north-east corner, in the sheet\'s screen frame', () => {
  const [p] = pinsOf([{ id: 'a', at: 'dining', severity: 'minor' }], rooms);
  assert.ok(p.x > 10 && p.x < 24, 'inside the room across');
  assert.ok(p.x > 10 + 14 / 2, 'east of the centre, clear of the label');
  assert.ok(p.y < 0 && p.y > -12, 'y is negated, as every mark on the sheet');
  assert.ok(p.y < -6, 'north of the centre');
});

test('a finding with no room on this level is never placed, and the tally says so', () => {
  const findings = [{ id: 'a', at: 'garage', severity: 'fatal' }, { id: 'b', severity: 'minor' },
    { id: 'c', at: 'hall', severity: 'minor' }];
  assert.deepEqual(pinsOf(findings, rooms).map((p) => p.room), ['hall']);
  assert.deepEqual(pinTally(findings, rooms), { pinned: 1, unplaced: 2 });
});

test('the bench hands the sheet the findings in view, and a pin is the room\'s own filter', () => {
  const src = readFileSync(new URL('./surfaces/PlanWorkbench.jsx', import.meta.url), 'utf8');
  assert.match(src, /pins=\{placement \? pinsOf\(shown, levelRooms\(plan, placement, level\)\) : \[\]\}/);
  assert.match(src, /onPickPin=\{\(id\) => \{ setRoom\(room === id \? null : id\)/);
});
