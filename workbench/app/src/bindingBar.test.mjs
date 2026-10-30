/* WHO BINDS A SLOT ACROSS EVERY STYLE (Phase 17, WP-17.13). */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { bindingBar } from './elements/bindingBar.js';

test('the four segments sum to every style, the extended taken out of the specified', () => {
  const bar = bindingBar({ specified: ['a', 'b', 'c'], extends: ['c'], forbidden: ['d'], open: ['e', 'f'], of: 6 });
  assert.deepEqual(bar.map((s) => [s.id, s.n]), [['specified', 2], ['extends', 1], ['forbidden', 1], ['open', 2]]);
  assert.equal(bar.reduce((a, s) => a + s.n, 0), 6);
  assert.ok(Math.abs(bar.reduce((a, s) => a + s.share, 0) - 1) < 1e-9);
});

test('a payload missing a part draws no bar rather than three parts read as the whole', () => {
  assert.equal(bindingBar({ specified: [], forbidden: [], open: [], of: 3 }), null);
  assert.equal(bindingBar(null), null);
});

/* Phase 17's audit: the fixture's `open` equalled of - specified - forbidden, so a bar that counted
   the open styles itself read exactly like one that took the route's. The route's list is the word. */
test('the open part is the route\'s own list, never the remainder the bar could count', () => {
  const bar = bindingBar({ specified: ['a'], extends: [], forbidden: ['b'], open: ['c'], of: 5 });
  assert.equal(bar.find((s) => s.id === 'open').n, 1, 'one open style, though five less two is three');
  assert.equal(bindingBar({ specified: [], extends: [], forbidden: [], of: 3 }), null, 'no open list, no bar');
});
