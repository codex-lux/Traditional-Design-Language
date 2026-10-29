/* THE FAMILY TREE IN LANES, AND THE CHRONOLOGY EXCEPTION (Phase 17, WP-17.12). */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { lanesOf, chronologyExceptions } from './lineage/lanes.js';

test('lanes partition every taxon, in the order given, each in date order, the unknown kept at the end', () => {
  const rows = [{ id: 'b', tradition: 't1', from: 1800 }, { id: 'a', tradition: 't0', from: 1700 },
    { id: 'c', tradition: 't0', from: 1600 }, { id: 'x', tradition: undefined, from: 1500 }];
  const lanes = lanesOf(rows, ['t0', 't1', 't2']);
  assert.deepEqual(lanes.map((l) => l.id), ['t0', 't1', 't2', null]);
  assert.deepEqual(lanes[0].rows.map((r) => r.id), ['c', 'a']);
  assert.equal(lanes[2].rows.length, 0, 'a tradition with no taxon is an empty lane, not a missing one');
  assert.equal(lanes.flatMap((l) => l.rows).length, rows.length, 'nothing dropped');
});

test('the chronology exception is the validator\'s rule: a descendant flourishing 25 years before its ancestor', () => {
  const taxa = [{ id: 'child', floruit_start: 1650 }, { id: 'parent', floruit_start: 1700 },
    { id: 'near', floruit_start: 1680 }];
  const edges = [{ from: 'child', to: 'parent', type: 'descends_from' },
    { from: 'near', to: 'parent', type: 'descends_from' },
    { from: 'child', to: 'parent', type: 'hybridizes_with' }];
  assert.deepEqual(chronologyExceptions(taxa, edges).map((e) => [e.from, e.to]), [['child', 'parent']],
    'twenty years early is within the slack, and a hybrid edge is not lineage of descent');
});
