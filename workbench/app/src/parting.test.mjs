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

test('the parting node is the same whichever style is named first (Phase 17 audit)', () => {
  // two cascades flattened from one graph hold their shared nodes in different orders: the first
  // version answered `p` for A then B and `q` for B then A
  const A = c('a', 'p', 'x', 'q', 'root');
  const B = c('b', 'q', 'y', 'z', 'p', 'root');
  const ab = partingOf(A, B), ba = partingOf(B, A);
  assert.equal(ab.common, ba.common);
  assert.equal(ab.common, 'q', 'q sits 3 + 1 levels up, p sits 1 + 4');
  assert.deepEqual(ab.aOwn, ba.bOwn);
  assert.deepEqual(ab.aOwn, ['a', 'x'], 'its own levels are the ones the other cascade lacks');
});

test('a tie between two shared nodes is broken by name, not by order', () => {
  const ab = partingOf(c('a', 'n', 'm'), c('b', 'm', 'n'));
  assert.equal(ab.common, 'm');
  assert.equal(partingOf(c('b', 'm', 'n'), c('a', 'n', 'm')).common, 'm');
});
