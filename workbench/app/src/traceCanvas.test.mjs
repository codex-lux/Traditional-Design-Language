/* The Transcription canvas draws the person's own tracing and nothing else (WP-14.4). */
import test from 'node:test';
import assert from 'node:assert/strict';

import { backdropBox, canvasSize, gridSteps, roomRect } from './traceCanvas.js';

test('a traced room is drawn at its own feet, y flipped into the screen', () => {
  const r = { x: 12, y: 3.5, w: 16.5, h: 14 };
  assert.deepEqual(roomRect(r), { x: 12, y: -17.5, width: 16.5, height: 14 });
});

test('the backdrop keeps its own aspect: the height is the width times the ratio', () => {
  const b = { wFt: 60, hFt: 60 * 0.7083, ratio: 0.7083 };
  const box = backdropBox(b);
  assert.equal(box.width, 60);
  assert.ok(Math.abs(box.height / box.width - b.ratio) < 1e-9);
  assert.equal(box.y + box.height, 0, 'the backdrop stands on the canvas origin');
});

test('the canvas holds every traced room and the backdrop', () => {
  const { W, H } = canvasSize([{ x: 40, y: 30, w: 20, h: 10 }], { wFt: 70, hFt: 50 });
  assert.ok(W >= 64 && W >= 72 && H >= 44 && H >= 52);
  assert.deepEqual(canvasSize([], null), { W: 44, H: 32 });
});

test('the reference grid is every 5 ft, every 10 ft heavier', () => {
  const { v, h } = gridSteps(20, 10);
  assert.deepEqual(v.map((s) => [s.at, s.heavy]), [[0, true], [5, false], [10, true], [15, false], [20, true]]);
  assert.deepEqual(h.map((s) => s.at), [0, 5, 10]);
});
