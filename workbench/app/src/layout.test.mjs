/* The layout store, which is the one piece of WP-5.7 that can strand a reader.

   Every case below is a defect that shipped or was caught before it did. The ones marked
   AUDIT were found by an adversarial pass over the first version of this file, which had
   eleven assertions that passed on the code they were supposed to guard — a ceiling that
   could be deleted, a `reset` that could be made a no-op, an invariant asserted at the one
   window width where it happened to hold. Each of those is now driven at a width or in a
   shape where it actually binds.

   `npm test` in workbench/app; build/check_all.py runs it (COULD NOT EVALUATE without
   node, never a pass). */
import { test } from 'node:test';
import assert from 'node:assert/strict';

/* A localStorage stand-in, installed BEFORE the store is imported — the store reads it at
   module scope, and a static import would be hoisted above the assignment. */
function stub(seed) {
  const map = new Map(Object.entries(seed || {}));
  let writes = 0;
  globalThis.localStorage = {
    getItem: (k) => (map.has(k) ? map.get(k) : null),
    setItem: (k, v) => { writes += 1; map.set(k, String(v)); },
    removeItem: (k) => map.delete(k),
  };
  return { map, writes: () => writes };
}

const KEY = 'tdl-workbench-layout';
let seq = 0;
// Each case gets its own module instance: the store is a singleton by design, and tests
// that shared one would be testing the order they happen to run in. NOTE: `localStorage`
// is a single global, so this is safe only because node:test runs these sequentially —
// do not add `concurrency` to this file without giving each case its own global.
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

test('nonsense that coerces to a number is rejected, not honoured', async () => {
  // AUDIT: `Number([])` and `Number('')` are both 0, which used to clamp silently to the
  // pane's MINIMUM rather than fall back to its default — a stored value that means
  // nothing must not look like a deliberate choice of the narrowest possible pane.
  const { layout, PANES } = await fresh({
    [KEY]: JSON.stringify({ widths: { nav: [], rail: '', phylo: {}, kit: 'abc' }, collapsed: {} }),
  });
  ['nav', 'rail', 'phylo', 'kit'].forEach((k) => {
    assert.equal(layout.width(k), PANES[k].def, `${k} fell back to its default`);
  });
});

test('a stored fold is refused for a pane that cannot fold', async () => {
  // AUDIT: setCollapsed guards this and readStored did not, so a stored `true` left
  // Splitter believing a pane that renders at full width was 0 wide — the first drag
  // snapped it to its floor, and aria-valuenow told a screen reader 0 about a visible pane.
  const { layout, PANES } = await fresh({
    [KEY]: JSON.stringify({ widths: {}, collapsed: { faults: true, kit: true, nav: true } }),
  });
  Object.keys(PANES).forEach((k) => {
    if (!PANES[k].foldable) assert.equal(layout.isOpen(k), true, `${k} must not be foldable`);
  });
  assert.equal(layout.isOpen('nav'), false, 'a foldable pane still honours its stored fold');
});

test('a collapsed pane is remembered; `full` deliberately is not', async () => {
  const { layout, store } = await fresh();
  layout.setCollapsed('rail', true);
  layout.setFull('phylogeny');
  layout.flush();
  const saved = JSON.parse(store.map.get(KEY));
  assert.equal(saved.collapsed.rail, true);
  assert.ok(!('full' in saved),
    'full screen must not outlive the tab — a reader who closes it in full screen and '
    + 'comes back must get the instrument, not a chrome-less shell they have to remember '
    + 'the escape key for');
});

test('a transient act does not write another tab\'s widths over this one\'s', async () => {
  // AUDIT: setFull called the same emit() as a width change, so toggling full screen in a
  // stale tab serialised THAT tab's whole {widths, collapsed} over a width another tab had
  // just set. Last-writer-wins over the whole object, from a state this file says is not
  // persisted at all.
  const { layout, store } = await fresh();
  layout.setWidth('nav', 300);
  layout.flush();
  // COUNT the writes, do not compare the bytes: this tab would write the SAME bytes, and
  // the harm is that it writes at all — the other tab's newer value is what gets lost.
  const before = store.writes();
  layout.setFull('phylogeny');
  layout.setFull(null);
  layout.flush();
  assert.equal(store.writes(), before, 'full screen must not touch storage at all');
});

test('dragging a pane below its floor folds it and keeps the width for its return', async () => {
  const { layout, PANES } = await fresh();
  layout.setWidth('nav', 300);
  layout.dragTo('nav', 40);                       // hauled past the floor
  assert.equal(layout.isOpen('nav'), false);
  assert.equal(layout.preferred('nav'), 300, 'unfolding must return the size they chose');
  assert.equal(layout.width('nav'), 0, 'a folded pane occupies nothing');
  layout.setCollapsed('nav', false);
  assert.equal(layout.width('nav'), 300);
  // and a drag that merely goes small stops at the floor rather than folding
  layout.dragTo('nav', PANES.nav.min + 2);
  assert.equal(layout.isOpen('nav'), true);
  assert.equal(layout.width('nav'), PANES.nav.min + 2);
});

test('a surface\'s own index stops at its floor and never folds', async () => {
  // AUDIT: the walk's version of this check compared a DOM that is byte-identical either
  // way, so deleting both foldable guards left the whole suite green. The observable
  // difference is the WIDTH: folded leaves it where it was, clamped puts it at the floor.
  const { layout, PANES } = await fresh();
  layout.setWidth('workbench', 520);
  layout.dragTo('workbench', 10);
  assert.equal(layout.isOpen('workbench'), true, 'the fault list IS the Fault Corpus');
  assert.equal(layout.width('workbench'), PANES.workbench.min,
    'a drag past the floor clamps at the floor — 520 would mean it folded instead');
  layout.setCollapsed('workbench', true);
  assert.equal(layout.isOpen('workbench'), true, 'setCollapsed refuses it too');
  layout.toggle('workbench');
  assert.equal(layout.isOpen('workbench'), true, 'and so does toggle');
  assert.equal(layout.canFold('workbench'), false);
  assert.equal(layout.canFold('nav'), true);
});

test('dragging a folded pane back out unfolds it', async () => {
  const { layout } = await fresh();
  layout.setCollapsed('rail', true);
  layout.dragTo('rail', 400);
  assert.equal(layout.isOpen('rail'), true);
  assert.equal(layout.width('rail'), 400);
});

test('a narrow window borrows the width; it does not take it', async () => {
  // THE DEFECT THIS FILE EXISTS FOR. clampAll used to overwrite the stored preference, so
  // one second of a narrow window — a PDF beside the workbench, a rotated tablet — wrote
  // all eight panes to their floors and committed it. Widening back restored nothing,
  // because a clamp that only shrinks has no counterpart.
  const { layout } = await fresh();
  layout.setWidth('nav', 400);
  layout.setWidth('rail', 600);
  layout.setWidth('kit', 600);
  layout.clampAll(700);
  assert.ok(layout.width('nav') < 400, 'the fit gives way to a narrow window');
  assert.equal(layout.preferred('nav'), 400, 'but the choice is untouched');
  assert.equal(layout.preferred('kit'), 600);
  layout.clampAll(2560);
  assert.equal(layout.width('nav'), 400, 'and comes back when the window does');
  assert.equal(layout.width('rail'), 600);
  assert.equal(layout.width('kit'), 600);
});

test('no pane takes a third of the window, at every width, including the narrow ones', async () => {
  // AUDIT: the first version asserted this at 1000px only — the one width where the mins
  // do not bind — so deleting the ceiling left it green. Below 900px `clamp()` used to
  // re-impose `min` after the ceiling and the guarantee was silently void: at 390px
  // nav.min + rail.min IS 390, so the two rails took the whole window and the canvas
  // between them, which is the thing being read, was zero pixels wide.
  const { layout, PANES } = await fresh();
  Object.keys(PANES).forEach((k) => layout.setWidth(k, PANES[k].max));
  for (let w = 200; w <= 2600; w += 7) {
    layout.clampAll(w);
    Object.keys(PANES).forEach((k) => {
      assert.ok(layout.width(k) <= Math.floor(w / 3),
        `${k} is ${layout.width(k)} of a ${w}px window`);
    });
    const pair = layout.width('nav') + layout.width('rail');
    assert.ok(pair <= Math.floor(w / 2), `the two rails are ${pair} of a ${w}px window`);
    assert.ok(w - pair >= Math.floor(w / 2),
      `the canvas is ${w - pair}px of a ${w}px window — it is the thing being read`);
  }
});

test('clampAll leaves a layout that already fits completely alone', async () => {
  const { layout } = await fresh();
  layout.setWidth('nav', 200);
  layout.setWidth('rail', 300);
  layout.clampAll(1920);
  assert.equal(layout.width('nav'), 200);
  assert.equal(layout.width('rail'), 300);
});

test('a resize that changes nothing notifies nobody and writes nothing', async () => {
  // AUDIT: below 900px the old fit rebuilt `widths` into a NEW object with IDENTICAL
  // values every call, so the identity test passed, emit fired, localStorage was written
  // and the whole surface tree re-rendered — for every one of the dozens of resize events
  // that dragging a window edge produces.
  const { layout, store } = await fresh();
  layout.clampAll(800);
  layout.flush();
  let n = 0;
  const off = layout.subscribe(() => { n += 1; });
  const writesBefore = store.writes();
  for (let i = 0; i < 20; i += 1) layout.clampAll(800);
  layout.flush();
  off();
  assert.equal(n, 0, `20 identical resizes produced ${n} notifications`);
  assert.equal(store.writes(), writesBefore, 'and no writes');
});

test('reset returns a pane to its shipped width and unfolds it', async () => {
  // AUDIT: making reset() a no-op left the whole suite green, and it is both the
  // double-click affordance and the Home key.
  const { layout, PANES } = await fresh();
  layout.setWidth('phylo', 500);
  layout.setCollapsed('phylo', true);
  layout.reset('phylo');
  assert.equal(layout.width('phylo'), PANES.phylo.def);
  assert.equal(layout.isOpen('phylo'), true);
});

test('the splitter\'s key arithmetic moves the pane the way the hand does', async () => {
  // AUDIT: `onKeyDown` was written, documented in three places and NEVER ATTACHED, and the
  // walk's check asserted the element existed rather than that the keys did anything. This
  // drives the same arithmetic the handler runs, in both directions, for a left-hand pane
  // (dir +1) and a right-hand one (dir -1).
  const { layout, PANES } = await fresh();
  const key = (pane, k, dir, shift) => {
    const step = shift ? 48 : 8;
    const w = layout.width(pane);
    if (k === 'ArrowLeft') layout.dragTo(pane, w - step * dir);
    else if (k === 'ArrowRight') layout.dragTo(pane, w + step * dir);
  };
  layout.setWidth('nav', 236);
  key('nav', 'ArrowRight', 1);
  assert.equal(layout.width('nav'), 244, 'right widens a left-hand pane');
  key('nav', 'ArrowLeft', 1);
  assert.equal(layout.width('nav'), 236);
  key('nav', 'ArrowRight', 1, true);
  assert.equal(layout.width('nav'), 284, 'shift strides');
  // a right-hand pane grows when the separator goes LEFT
  layout.setWidth('rail', 344);
  key('rail', 'ArrowLeft', -1);
  assert.equal(layout.width('rail'), 352);
  // and the keys stop at the same floors and ceilings the hand does
  for (let i = 0; i < 60; i += 1) key('nav', 'ArrowRight', 1, true);
  assert.equal(layout.width('nav'), PANES.nav.max);
});

test('an unknown pane name is inert rather than a new pane', async () => {
  const { layout } = await fresh();
  layout.setWidth('sidebar', 400);
  layout.setCollapsed('sidebar', true);
  layout.dragTo('sidebar', 400);
  layout.reset('sidebar');
  assert.equal(layout.width('sidebar'), undefined);
  assert.equal(layout.get().collapsed.sidebar, undefined);
  assert.equal(layout.canFold('sidebar'), false);
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

test('a drag costs one write, not one per pixel', async () => {
  // AUDIT: measured at 115 synchronous localStorage writes for a single 1.5s pull on a
  // 120Hz display, each one also a `storage` event broadcast to every other tab of the
  // origin, for a value only the last of which matters.
  const { layout, store } = await fresh();
  layout.flush();
  const before = store.writes();
  for (let px = 236; px < 400; px += 1) layout.dragTo('nav', px);
  assert.equal(store.writes(), before, 'nothing is written while the hand is moving');
  layout.flush();
  assert.equal(store.writes(), before + 1, 'and exactly one write settles it');
  assert.equal(JSON.parse(store.map.get(KEY)).widths.nav, 399);
});

test('a private window that refuses to store still gets a working layout', async () => {
  stub();
  globalThis.localStorage.setItem = () => { throw new Error('QuotaExceededError'); };
  const { layout } = await import(`./state/layout.js?case=${seq += 1}`);
  layout.setWidth('nav', 260);            // must not throw
  layout.flush();
  assert.equal(layout.width('nav'), 260);
  // leave the global in a usable state for anything that runs after this file
  stub();
});
