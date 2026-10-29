/* WHERE TWO STYLES PART (Phase 17, WP-17.13). */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { partingOf } from './compare/parting.js';

const c = (...ids) => ({ cascade: ids.map((id) => ({ id })) });

test('two styles part at the nearest node both cascades hold', () => {
  const p = partingOf(c('craftsman', 'arts-and-crafts', 'english-vernacular', 'root'),
    c('tudor-revival', 'english-vernacular', 'root'));
  assert.equal(p.common, 'english-vernacular');
  assert.deepEqual(p.aOwn, ['craftsman', 'arts-and-crafts']);
  assert.deepEqual(p.bOwn, ['tudor-revival']);
});

test('a pair sharing nothing parts at no node, and a missing cascade is no answer', () => {
  assert.equal(partingOf(c('a', 'b'), c('x', 'y')).common, null);
  assert.equal(partingOf(null, c('x')), null);
});
