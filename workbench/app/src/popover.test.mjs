/* A DEFINITION'S POPOVER, PLACED AT EVERY EDGE OF A LAPTOP SCREEN (WP-14.6).

   1280 x 720 is the window this phase was asked to work on. The properties are asserted over a
   grid of anchors covering all four edges, all four corners and the middle, for three popover
   sizes — so a rule that only works in the middle of the screen, which is where a person testing
   by hand clicks, cannot pass. Each property is stated as the thing a reader would see go wrong:
   a popover off the screen, a popover over the word it explains, a popover that flipped to the
   side with less room. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { placePopover } from './help/placePopover.js';

const VP = { x: 0, y: 0, width: 1280, height: 720 };
const WORD = { width: 64, height: 18 };
const MARGIN = 8, GAP = 6;

const drawn = (r, pop) => ({
  left: r.left, top: r.top,
  right: r.left + (r.maxWidth ?? pop.width), bottom: r.top + (r.maxHeight ?? pop.height),
});
const overlaps = (a, b) => a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom;

function anchorsAt(vp) {
  const xs = [vp.x, vp.x + 3, vp.x + vp.width / 2, vp.x + vp.width - WORD.width - 3, vp.x + vp.width - WORD.width];
  const ys = [vp.y, vp.y + 3, vp.y + vp.height / 2, vp.y + vp.height - WORD.height - 3, vp.y + vp.height - WORD.height];
  return xs.flatMap((x) => ys.map((y) => ({ x, y, ...WORD })));
}

const POPOVERS = [{ width: 320, height: 180 }, { width: 420, height: 340 }, { width: 1400, height: 800 }];

test('at every edge and corner, the popover stays inside the viewport less its margin', () => {
  for (const vp of [VP, { x: 140, y: 60, width: 640, height: 360 }]) {   // and a pinch-zoomed view
    for (const pop of POPOVERS) {
      for (const anchor of anchorsAt(vp)) {
        const r = placePopover({ anchor, popover: pop, viewport: vp });
        const d = drawn(r, pop);
        const where = `anchor ${anchor.x},${anchor.y} popover ${pop.width}x${pop.height}`;
        assert.ok(d.left >= vp.x + MARGIN - 1e-9, `${where}: off the left edge`);
        assert.ok(d.right <= vp.x + vp.width - MARGIN + 1e-9, `${where}: off the right edge`);
        assert.ok(d.top >= vp.y + MARGIN - 1e-9, `${where}: off the top`);
        assert.ok(d.bottom <= vp.y + vp.height - MARGIN + 1e-9, `${where}: off the bottom`);
        assert.ok(r.side === 'below' || r.side === 'above');
      }
    }
  }
});

test('the popover never covers the word it explains', () => {
  for (const pop of POPOVERS) {
    for (const anchor of anchorsAt(VP)) {
      const r = placePopover({ anchor, popover: pop, viewport: VP });
      const word = { left: anchor.x, top: anchor.y, right: anchor.x + anchor.width, bottom: anchor.y + anchor.height };
      assert.ok(!overlaps(drawn(r, pop), word), `anchor ${anchor.x},${anchor.y} popover ${pop.width}x${pop.height}`);
      if (r.side === 'below') assert.ok(r.top >= word.bottom + GAP - 1e-9);
      else assert.ok(drawn(r, pop).bottom <= word.top - GAP + 1e-9);
    }
  }
});

test('below by default, above at the bottom edge, and never to the side with less room', () => {
  const pop = { width: 320, height: 180 };
  const top = placePopover({ anchor: { x: 600, y: 10, ...WORD }, popover: pop, viewport: VP });
  assert.equal(top.side, 'below');
  assert.equal(top.top, 10 + WORD.height + GAP, 'directly under the word');
  assert.equal(top.maxHeight, null);
  const mid = placePopover({ anchor: { x: 600, y: 300, ...WORD }, popover: pop, viewport: VP });
  assert.equal(mid.side, 'below', 'room on both sides: below, the default');
  const bottom = placePopover({ anchor: { x: 600, y: 690, ...WORD }, popover: pop, viewport: VP });
  assert.equal(bottom.side, 'above', 'no room below at the bottom edge: it flips');
  assert.equal(bottom.top + 180, 690 - GAP, 'and sits directly over the word');
  // too tall for either side: it takes the roomier one and scrolls inside itself
  const tall = { width: 320, height: 600 };
  const nearTop = placePopover({ anchor: { x: 600, y: 200, ...WORD }, popover: tall, viewport: VP });
  assert.equal(nearTop.side, 'below');
  assert.equal(nearTop.maxHeight, 720 - MARGIN - (200 + WORD.height + GAP));
  const nearBottom = placePopover({ anchor: { x: 600, y: 480, ...WORD }, popover: tall, viewport: VP });
  assert.equal(nearBottom.side, 'above');
  assert.equal(nearBottom.maxHeight, 480 - GAP - MARGIN);
  assert.ok(nearBottom.maxHeight > 720 - MARGIN - (480 + WORD.height + GAP), 'the roomier side was chosen');
});

test('horizontally it starts at the word, and a word at the right edge opens leftward', () => {
  const pop = { width: 320, height: 180 };
  const left = placePopover({ anchor: { x: 200, y: 100, ...WORD }, popover: pop, viewport: VP });
  assert.equal(left.left, 200);
  assert.equal(left.maxWidth, null);
  const edge = placePopover({ anchor: { x: 1280 - WORD.width, y: 100, ...WORD }, popover: pop, viewport: VP });
  assert.equal(edge.left, 1280 - MARGIN - 320);
  const origin = placePopover({ anchor: { x: 0, y: 100, ...WORD }, popover: pop, viewport: VP });
  assert.equal(origin.left, MARGIN);
});

test('a popover wider than the screen is narrowed to it, and the viewport offset is honoured', () => {
  const r = placePopover({ anchor: { x: 500, y: 100, ...WORD }, popover: { width: 1400, height: 100 }, viewport: VP });
  assert.equal(r.maxWidth, 1280 - 2 * MARGIN);
  assert.equal(r.left, MARGIN);
  const zoomed = { x: 140, y: 60, width: 640, height: 360 };
  const z = placePopover({ anchor: { x: 150, y: 70, ...WORD }, popover: { width: 320, height: 100 }, viewport: zoomed });
  assert.equal(z.left, 150);
  assert.equal(z.top, 70 + WORD.height + GAP);
  const zr = placePopover({ anchor: { x: 140 + 640 - WORD.width, y: 70, ...WORD }, popover: { width: 320, height: 100 }, viewport: zoomed });
  assert.equal(zr.left, 140 + 640 - MARGIN - 320, 'clamped to the VISUAL viewport, not the page');
});

test('gap and margin are the caller’s when given, and the defaults are the PRD’s', () => {
  const r = placePopover({ anchor: { x: 0, y: 0, ...WORD }, popover: { width: 100, height: 50 }, viewport: VP, gap: 12, margin: 20 });
  assert.equal(r.left, 20);
  assert.equal(r.top, WORD.height + 12);
  const d = placePopover({ anchor: { x: 0, y: 0, ...WORD }, popover: { width: 100, height: 50 }, viewport: VP });
  assert.equal(d.left, 8);
  assert.equal(d.top, WORD.height + 6);
});
