/* The generated coastline tiers, and the thing that reads them.

   These files are 1.4 MB of machine-written path data that nobody will ever proofread,
   and the map draws them without checking. So the checks are here: that a tier really is
   finer than the one below it (a level-of-detail scheme whose levels are the same detail
   is an expensive way to draw one outline), that every declared bounding box actually
   contains its ring (the culler trusts them, and a wrong box is a hole in the world), and
   that nothing in them steps across the whole plate.

   The path data is parsed rather than pattern-matched. A regex over an SVG path proves
   the bytes look right; walking the deltas proves the drawing is.

   `npm test` in workbench/app; build/check_all.py runs it. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { COAST_COARSE, COASTLINES } from './data/coastlines.js';
import { COAST_MEDIUM } from './data/coastlines-medium.js';
import { COAST_FINE } from './data/coastlines-fine.js';
import { TIERS, tierFor, visibleRings } from './surfaces/phylo/coastTiers.js';

const ALL = [COAST_COARSE, COAST_MEDIUM, COAST_FINE];

/* Walk one delta-encoded ring back into points. The generator writes `M x,y` then a run
   of relative `l dx,dy`, with the comma dropped wherever the sign or the decimal point
   already separates the pair — so this is also the test that that shortcut is legal. */
function walk(d) {
  const nums = d.match(/-?(?:\d+\.?\d*|\.\d+)/g) || [];
  assert.equal(nums.length % 2, 0, `odd coordinate count in ${d.slice(0, 40)}…`);
  assert.ok(d.startsWith('M'), 'a ring starts with a moveto');
  assert.ok(d.endsWith('Z'), 'a ring closes');
  // every command between them is a relative lineto — no curves, no absolute jumps
  assert.equal(/[^\-\d.,MlZ]/.test(d), false, `unexpected command in ${d.slice(0, 40)}…`);
  let x = Number(nums[0]), y = Number(nums[1]);
  const pts = [[x, y]];
  for (let i = 2; i < nums.length; i += 2) {
    x += Number(nums[i]);
    y += Number(nums[i + 1]);
    pts.push([x, y]);
  }
  return pts;
}

test('the tiers get finer, and each is finer than the one below it', () => {
  for (let i = 1; i < ALL.length; i += 1) {
    assert.ok(ALL[i].tolerance < ALL[i - 1].tolerance,
      `${ALL[i].name} must be simplified less than ${ALL[i - 1].name}`);
    assert.ok(ALL[i].points > ALL[i - 1].points * 2,
      `${ALL[i].name} has ${ALL[i].points} points against ${ALL[i - 1].name}'s ${ALL[i - 1].points} `
      + '— a level of detail that is not more detailed is a chunk fetched for nothing');
  }
});

test('the declared counts are the real ones', () => {
  ALL.forEach((t) => {
    assert.equal(t.paths.length, t.rings, `${t.name}: rings`);
    assert.equal(t.bounds.length, t.rings * 4, `${t.name}: four bounds numbers per ring`);
  });
});

test('every bounding box contains its own ring', () => {
  // The culler drops a ring whose box misses the view. A box that does not contain its
  // ring is land that vanishes at some scales and not others — the kind of defect that
  // looks like a rendering glitch and is a data one.
  ALL.forEach((t) => {
    for (let i = 0; i < t.paths.length; i += 1) {
      const pts = walk(t.paths[i]);
      const [bx0, by0, bx1, by1] = t.bounds.slice(i * 4, i * 4 + 4);
      let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
      pts.forEach(([x, y]) => {
        if (x < x0) x0 = x; if (x > x1) x1 = x;
        if (y < y0) y0 = y; if (y > y1) y1 = y;
      });
      const slop = 1.01;         // the boxes are rounded outward to whole degrees
      assert.ok(bx0 <= x0 + slop && bx1 >= x1 - slop && by0 <= y0 + slop && by1 >= y1 - slop,
        `${t.name} ring ${i}: box [${bx0},${by0},${bx1},${by1}] does not hold `
        + `[${x0.toFixed(2)},${y0.toFixed(2)},${x1.toFixed(2)},${y1.toFixed(2)}]`);
    }
  });
});

test('nothing steps across the plate, and nothing leaves the earth', () => {
  // The seam bug this catches: Natural Earth cuts Eurasia and Antarctica at 180 degrees,
  // which leaves a segment jumping from +180 to -180 inside an ordinary ring. Drawn
  // literally that is a hairline ruled straight across the map.
  ALL.forEach((t) => {
    t.paths.forEach((d, i) => {
      const pts = walk(d);
      for (let k = 1; k < pts.length; k += 1) {
        assert.ok(Math.abs(pts[k][0] - pts[k - 1][0]) < 180,
          `${t.name} ring ${i} steps ${Math.abs(pts[k][0] - pts[k - 1][0]).toFixed(1)}° of longitude`);
      }
      pts.forEach(([x, y]) => {
        assert.ok(x >= -181 && x <= 181, `${t.name} ring ${i}: longitude ${x}`);
        assert.ok(y >= -91 && y <= 91, `${t.name} ring ${i}: latitude ${-y}`);
      });
    });
  });
});

test('COASTLINES still names the coarse tier, for anything that predates the tiers', () => {
  assert.equal(COASTLINES, COAST_COARSE.paths);
});

test('tierFor picks the finest tier a width has earned, and never runs off the end', () => {
  assert.equal(tierFor(300).name, 'coarse');
  assert.equal(tierFor(134).name, 'coarse');          // the home view
  assert.equal(tierFor(70).name, 'medium');
  assert.equal(tierFor(16).name, 'fine');
  assert.equal(tierFor(3).name, 'fine');
  assert.equal(tierFor(0).name, 'fine');
  assert.equal(tierFor(Infinity).name, 'coarse');
});

test('the thresholds are ordered, so no tier is unreachable', () => {
  const uptos = TIERS.map((t) => t.upto);
  for (let i = 1; i < uptos.length; i += 1) {
    assert.ok(uptos[i] < uptos[i - 1], `tier ${TIERS[i].name} can never be selected`);
  }
});

test('culling keeps what is on screen and drops what is not', () => {
  // Britain, roughly: lon -8..2, lat 50..59 → y -59..-50 in drawn space.
  const british = visibleRings(COAST_COARSE, { x: -8, y: -59, w: 10, h: 9 });
  assert.ok(british.length > 0, 'an island must survive being looked at');
  assert.ok(british.length < COAST_COARSE.rings,
    'culling that keeps everything is not culling');
  // Every kept ring must genuinely overlap; every dropped one must genuinely not.
  const view = { x: -8, y: -59, w: 10, h: 9 };
  const kept = new Set(british);
  for (let i = 0; i < COAST_COARSE.rings; i += 1) {
    const [x0, y0, x1, y1] = COAST_COARSE.bounds.slice(i * 4, i * 4 + 4);
    const overlaps = x0 <= view.x + view.w && x1 >= view.x && y0 <= view.y + view.h && y1 >= view.y;
    assert.equal(kept.has(i), overlaps, `ring ${i} kept=${kept.has(i)} overlaps=${overlaps}`);
  }
  // The whole world keeps the whole world.
  assert.equal(visibleRings(COAST_COARSE, { x: -180, y: -90, w: 360, h: 180 }).length,
    COAST_COARSE.rings);
  // Two degrees of mid-Pacific keeps almost nothing — "almost", not "nothing", and the
  // difference is the honest limit of culling by box: the Americas are one ring whose
  // box spans 135 degrees of longitude, so a square of open ocean inside that box is
  // kept. Being conservative is the correct direction to be wrong in; the cost is one
  // clipped path and the alternative error is missing land.
  assert.ok(visibleRings(COAST_COARSE, { x: -140, y: -34, w: 2, h: 2 }).length < 4);
  assert.deepEqual(visibleRings(null, { x: 0, y: 0, w: 1, h: 1 }), []);
});

test('the fine tier is worth its megabyte at the scale it is fetched for', () => {
  // 16 degrees of longitude is where the medium tier is handed over. Its 0.06° tolerance
  // is about four pixels across a thousand-pixel pane there; the fine tier's is under one.
  const pane = 1000;
  const px = (tier, w) => (tier.tolerance / w) * pane;
  assert.ok(px(COAST_MEDIUM, 16) > 3, 'the handover happens once the medium tier shows');
  assert.ok(px(COAST_FINE, 16) < 1, 'and the tier it hands to must not show at all there');
  assert.ok(px(COAST_FINE, 3) < 6, 'nor badly at the floor on how far in the map will go');
});
