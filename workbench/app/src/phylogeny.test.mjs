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

/* Phase 17's audit: the corpus's one exception is 150 years early, so any slack from 25 to 149 and a
   rule that dropped `regional_of` both passed. The boundary and the second kind are driven here. */
test('the slack is exactly twenty-five years, and a regional edge is lineage too', () => {
  const taxa = [{ id: 'p', floruit_start: 1700 }, { id: 'at25', floruit_start: 1675 },
    { id: 'at26', floruit_start: 1674 }, { id: 'reg', floruit_start: 1600 }];
  const edges = [{ from: 'at25', to: 'p', type: 'descends_from' }, { from: 'at26', to: 'p', type: 'descends_from' },
    { from: 'reg', to: 'p', type: 'regional_of' }];
  assert.deepEqual(chronologyExceptions(taxa, edges).map((e) => e.from).sort(), ['at26', 'reg']);
});
