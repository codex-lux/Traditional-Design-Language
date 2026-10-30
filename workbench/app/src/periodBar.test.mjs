/* A STYLE'S PERIOD, DRAWN (Phase 17, WP-17.9): the stated dates on one axis, and a date the record
   does not state named and never interpolated. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { periodBar } from './dossier/periodBar.js';

test('the four dates and the revivals become segments in order along the axis', () => {
  const b = periodBar({ origin: 1798, floruit_start: 1825, floruit_end: 1860, decline_end: 1875, circa: true,
    revival_periods: [{ start: 1893, end: 1945, revival_node: 'neoclassical-revival' }] });
  assert.deepEqual(b.segments.map((s) => s.id), ['origin', 'floruit', 'decline', 'revival']);
  for (const s of b.segments) assert.ok(s.x0 >= 0 && s.x1 <= 1 && s.x0 <= s.x1);
  assert.equal(b.segments[3].node, 'neoclassical-revival');
  assert.deepEqual(b.unstated, []);
});

test('a date the record does not state is not drawn and is said', () => {
  const b = periodBar({ floruit_start: 1700, floruit_end: 1780, origin: null, decline_end: null });
  assert.deepEqual(b.segments.map((s) => s.id), ['floruit']);
  assert.deepEqual(b.unstated, ['origin', 'decline']);
});

test('no floruit, no bar: the schema requires it, and a record without it draws nothing', () => {
  assert.equal(periodBar({ origin: 1700 }), null);
  assert.equal(periodBar(null), null);
});
