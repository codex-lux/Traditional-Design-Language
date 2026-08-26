/* The layout store, which is the one piece of WP-5.7 that can strand a reader.

   A pane width is a preference, and a preference that survives a reload is a preference
   that can survive into a window it no longer fits. Every case below is either a defect
   that would have shipped or a guarantee that would otherwise be enforced only by a
   comment. `npm test` in workbench/app; build/check_all.py runs it (COULD NOT EVALUATE
   without node, never a pass). */
import { test } from 'node:test';
import assert from 'node:assert/strict';

/* A localStorage stand-in, installed BEFORE the store is imported — the store reads it at
   module scope, and a static import would be hoisted above the assignment. */
function stub(seed) {
  const map = new Map(Object.entries(seed || {}));
  globalThis.localStorage = {
    getItem: (k) => (map.has(k) ? map.get(k) : null),
    setItem: (k, v) => map.set(k, String(v)),
    removeItem: (k) => map.delete(k),
  };
  return map;
}

const KEY = 'tdl-workbench-layout';
let seq = 0;
// Each case gets its own module instance: the store is a singleton by design, and tests
// that share one would be testing the order they happen to run in.
const fresh = async (seed) => {
  const store = stub(seed);
  const mod = await import(`./state/layout.js?case=${seq += 1}`);
  return { ...mod, store };
};

test('a pane starts at its shipped width, open', async () => {
  const { layout, PANES } = await fresh();
  assert.equal(layout.width('nav'), PANES.nav.def);
  assert.equal(layout.isOpen('nav'), true);
  assert.equal(layout.get().full, null);
});

test('a stored width is clamped on READ, not only on write', async () => {
  // The shipped hazard: 900px of nav saved on a 2560px display, opened on a laptop.
  const { layout, PANES } = await fresh({
    [KEY]: JSON.stringify({ widths: { nav: 900, rail: 12 }, collapsed: {} }),
  });
  assert.equal(layout.width('nav'), PANES.nav.max);
  assert.equal(layout.width('rail'), PANES.rail.min);
});

test('a corrupt entry gives a working shell rather than a broken one', async () => {
  const { layout, PANES } = await fresh({ [KEY]: '{not json' });
  assert.equal(layout.width('nav'), PANES.nav.def);
  assert.equal(layout.isOpen('rail'), true);
});

test('a collapsed pane is remembered; `full` deliberately is not', async () => {
  const { layout, store } = await fresh();
  layout.setCollapsed('rail', true);
  layout.setFull('phylogeny');
  const saved = JSON.parse(store.get(KEY));
  assert.equal(saved.collapsed.rail, true);
  assert.ok(!('full' in saved),
    'full screen must not outlive the tab — a reader who closes it in full screen and '
    + 'comes back must get the instrument, not a chrome-less shell they have to remember '
    + 'the escape key for');
});

test('dragging a pane below its floor folds it and keeps the width for its return', async () => {
  const { layout, PANES } = await fresh();
  layout.setWidth('nav', 300);
  layout.dragTo('nav', 40);                       // hauled past the floor
  assert.equal(layout.isOpen('nav'), false);
  assert.equal(layout.width('nav'), 300, 'unfolding must return the size they chose');
  layout.setCollapsed('nav', false);
  assert.equal(layout.width('nav'), 300);
  // and a drag that merely goes small stops at the floor rather than folding
  layout.dragTo('nav', PANES.nav.min + 2);
  assert.equal(layout.isOpen('nav'), true);
  assert.equal(layout.width('nav'), PANES.nav.min + 2);
});

test('dragging a folded pane back out unfolds it', async () => {
  const { layout } = await fresh();
  layout.setCollapsed('rail', true);
  layout.dragTo('rail', 400);
  assert.equal(layout.isOpen('rail'), true);
  assert.equal(layout.width('rail'), 400);
});

test('no pane may take a third of the window, and the two rails never take half', async () => {
  const { layout } = await fresh();
  layout.setWidth('nav', 420);
  layout.setWidth('rail', 620);
  layout.clampAll(1000);
  assert.ok(layout.width('nav') <= 334, `nav ${layout.width('nav')} over a third of 1000`);
  assert.ok(layout.width('rail') <= 334, `rail ${layout.width('rail')} over a third of 1000`);
  assert.ok(layout.width('nav') + layout.width('rail') <= 500,
    'the canvas between the rails is the thing being read');
});

test('clampAll leaves a layout that already fits completely alone', async () => {
  const { layout } = await fresh();
  layout.setWidth('nav', 200);
  layout.setWidth('rail', 300);
  layout.clampAll(1920);
  assert.equal(layout.width('nav'), 200);
  assert.equal(layout.width('rail'), 300);
});

test('an unknown pane name is inert rather than a new pane', async () => {
  const { layout } = await fresh();
  layout.setWidth('sidebar', 400);
  layout.setCollapsed('sidebar', true);
  layout.dragTo('sidebar', 400);
  assert.equal(layout.width('sidebar'), undefined);
  assert.equal(layout.get().collapsed.sidebar, undefined);
});

test('subscribers hear every change and nothing else', async () => {
  const { layout } = await fresh();
  let n = 0;
  const off = layout.subscribe(() => { n += 1; });
  layout.setWidth('nav', 210);
  assert.equal(n, 1);
  layout.setWidth('nav', 210);            // same value — no event
  assert.equal(n, 1);
  layout.toggle('nav');
  assert.equal(n, 2);
  off();
  layout.setWidth('nav', 220);
  assert.equal(n, 2);
});

test('a private window that refuses to store still gets a working layout', async () => {
  stub();
  globalThis.localStorage.setItem = () => { throw new Error('QuotaExceededError'); };
  const { layout } = await import(`./state/layout.js?case=${seq += 1}`);
  layout.setWidth('nav', 260);            // must not throw
  assert.equal(layout.width('nav'), 260);
});
