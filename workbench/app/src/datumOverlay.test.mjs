/* THE DATUM OVERLAY REGISTERS THROUGH THE PLATE'S OWN FRAME (Phase 17, WP-17.7). */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { datumLines, frameOf, viewBoxOf } from './sheet/datumOverlay.js';

const frame = { plates: [{ id: 'S', proj: 'elevation', face: 'S', px_per_ft: 6, origin_px: [46, 400], at_origin_ft: [0, 0] }] };
const svg = `<svg viewBox="0 0 800 520" data-frame='${JSON.stringify(frame)}'></svg>`;

test('the frame and the viewBox are read off the plate itself', () => {
  assert.equal(frameOf(svg).plates[0].px_per_ft, 6);
  assert.deepEqual(viewBoxOf(svg), { x: 0, y: 0, w: 800, h: 520 });
  assert.equal(frameOf('<svg></svg>'), null);
});

test('a datum stands where the frame puts its height above grade', () => {
  const lines = datumLines(svg, [{ id: 'grade', v_ft: 0 }, { id: 'ground-floor', v_ft: 2 }, { id: 'eave', v_ft: 17.35 }]);
  assert.equal(lines[0].y, 400, 'grade on the frame origin');
  assert.equal(lines[1].y, 400 - 12, 'two feet up is twelve pixels up at six to the foot');
  assert.ok(Math.abs(lines[2].y - (400 - 17.35 * 6)) < 1e-9);
  assert.equal(lines[0].x1, 46);
});

test('no frame, no datums, or a datum with no figure draws nothing in its place', () => {
  assert.equal(datumLines('<svg viewBox="0 0 1 1"></svg>', [{ id: 'grade', v_ft: 0 }]), null);
  assert.equal(datumLines(svg, []), null);
  assert.deepEqual(datumLines(svg, [{ id: 'eave', v_ft: null }]), []);
});
