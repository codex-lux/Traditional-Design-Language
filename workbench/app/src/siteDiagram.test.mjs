/* THE SITE, DRAWN (Phase 17, WP-17.6): the lot to scale or said unstated, the street on the side
   the entrance faces, and the eight compass points as the control. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { siteDiagram, COMPASS } from './brief/siteDiagram.js';

test('a stated lot is drawn to its own proportion, inside the box', () => {
  const d = siteDiagram({ lotW: 60, lotD: 120 });
  assert.ok(d.lot.stated);
  assert.ok(Math.abs(d.lot.h / d.lot.w - 2) < 1e-9, 'deep lot, twice as deep as wide');
  assert.ok(d.lot.x >= 0 && d.lot.y >= 0 && d.lot.x + d.lot.w <= d.box && d.lot.y + d.lot.h <= d.box);
});

test('a lot missing either dimension is unstated, never a default lot', () => {
  for (const args of [{}, { lotW: 60 }, { lotD: 90 }, { lotW: 0, lotD: 90 }]) {
    assert.equal(siteDiagram(args).lot.stated, false, JSON.stringify(args));
  }
});

test('the compass offers all eight points, diagonals included, and marks the one chosen', () => {
  const d = siteDiagram({ lotW: 60, lotD: 90, entrance: 'SE' });
  assert.deepEqual(d.points.map((p) => p.d), [...COMPASS]);
  assert.deepEqual(d.points.filter((p) => p.on).map((p) => p.d), ['SE']);
});

test('the street is the edge the entrance faces, or the corner for a diagonal', () => {
  const s = siteDiagram({ lotW: 60, lotD: 60, entrance: 'S' });
  assert.equal(s.street.corner, false);
  assert.equal(s.street.y1, s.lot.y + s.lot.h, 'the south edge');
  const ne = siteDiagram({ lotW: 60, lotD: 60, entrance: 'NE' });
  assert.equal(ne.street.corner, true);
  assert.equal(siteDiagram({ lotW: 60, lotD: 60, entrance: 'X' }).street, null, 'an unknown face draws no street');
});
