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
  // ONE subpath per ring. The char class permits `M` anywhere, so two subpaths in one `d`
  // would be walked as one continuous ring — an absolute moveto read as a relative delta —
  // and every point after it displaced. The generator emits one; this is what says so.
  assert.equal((d.match(/M/g) || []).length, 1, `more than one subpath in ${d.slice(0, 40)}…`);
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

test('the declared counts are the real ones, measured from the geometry', () => {
  /* THE POINT COUNT IS WALKED, NOT READ. `points` and `tolerance` are metadata the
     generator writes into the file it generates, and the first version of this suite
     compared them only against each other — so replacing the fine tier's entire `paths`
     and `bounds` with the COARSE tier's 102 rings, leaving `points: 116623` and
     `tolerance: 0.012` untouched, left all 36 tests green. The map would then have printed
     "land-10m.json, simplified at 0.012°" over 110m facets, which is precisely the
     "letting a facet pass for a shore" this layer exists to forbid. */
  ALL.forEach((t) => {
    assert.equal(t.paths.length, t.rings, `${t.name}: rings`);
    assert.equal(t.bounds.length, t.rings * 4, `${t.name}: four bounds numbers per ring`);
    const walked = t.paths.reduce((n, d) => n + walk(d).length, 0);
    assert.equal(walked, t.points,
      `${t.name} declares ${t.points} points and its paths hold ${walked} — the file's own `
      + 'header is a claim about geometry it may not be making');
  });
});

test('each tier really is drawn from its own source, not a copy of a coarser one', () => {
  // Two tiers that share a ring, byte for byte, are one tier fetched twice.
  const first = (t) => t.paths[0];
  assert.notEqual(first(COAST_MEDIUM), first(COAST_COARSE));
  assert.notEqual(first(COAST_FINE), first(COAST_MEDIUM));
  // and the declared tolerance must match what the geometry can actually resolve: the
  // median segment of a finer tier has to be shorter than the coarser tier's tolerance.
  const medianStep = (t) => {
    const p = walk(t.paths[0]);
    const d = [];
    for (let i = 1; i < p.length; i += 1) d.push(Math.hypot(p[i][0] - p[i - 1][0], p[i][1] - p[i - 1][1]));
    d.sort((a, b) => a - b);
    return d[Math.floor(d.length / 2)];
  };
  const [c, m, f] = ALL.map(medianStep);
  assert.ok(m < c, `medium's median segment ${m.toFixed(4)}° is not finer than coarse's ${c.toFixed(4)}°`);
  assert.ok(f < m, `fine's median segment ${f.toFixed(4)}° is not finer than medium's ${m.toFixed(4)}°`);
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
      /* NO SLOP IN THE CONTAINMENT DIRECTION. The generator rounds each box OUTWARD with
         floor/ceil, so a correct box contains its ring exactly and needs no slack — and
         the first version added 1.01° to the right-hand side, which LOOSENED it: a box
         whose western edge sat a full degree INSIDE its ring passed. That is the hole in
         the world this test names, at up to 110 km, invisible. Shifting a ring 0.9° east
         with its bounds untouched left the suite green. */
      /* EPS is float-reconstruction noise, not slack in the rule. The generator takes the
         box from the ring's full-precision coordinates and the path is then quantised to
         three decimals, so walking the deltas back can land a few 1e-13 outside the box at
         a coordinate of 180. A degree of tolerance would hide the defect this test names;
         a millionth of a degree — a tenth of a metre — cannot hide anything. */
      const EPS = 1e-6;
      assert.ok(bx0 <= x0 + EPS && bx1 >= x1 - EPS && by0 <= y0 + EPS && by1 >= y1 - EPS,
        `${t.name} ring ${i}: box [${bx0},${by0},${bx1},${by1}] does not hold `
        + `[${x0.toFixed(2)},${y0.toFixed(2)},${x1.toFixed(2)},${y1.toFixed(2)}]`);
      /* And no looser than the outward rounding explains, or the cull stops culling. One
         degree is the floor/ceil; the extra thousandth is that the box is taken from the
         ring's full-precision coordinates while this walks the quantised ones, so a true
         edge at -78.00004 floors to -79 and reads back as exactly -78. */
      assert.ok(x0 - bx0 <= 1.001 && bx1 - x1 <= 1.001 && y0 - by0 <= 1.001 && by1 - y1 <= 1.001,
        `${t.name} ring ${i}: the box is more than a degree wider than its ring `
        + `— [${bx0},${by0},${bx1},${by1}] around `
        + `[${x0.toFixed(3)},${y0.toFixed(3)},${x1.toFixed(3)},${y1.toFixed(3)}]`);
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
  /* THE LATITUDE HALF OF THE PREDICATE HAS TO BE EXERCISED. At the British view above,
     every ring that overlaps in longitude also overlaps in latitude, so deleting the two
     latitude clauses from `visibleRings` left the whole suite green. A view over Britain's
     longitudes but far to the south separates them: Africa and South America are under
     that meridian band and nowhere near that parallel. */
  {
    const southOfBritain = { x: -8, y: -10, w: 10, h: 8 };   // lon -8..2, lat 2..10 N
    const keptS = visibleRings(COAST_COARSE, southOfBritain);
    const lonOnly = [];
    for (let i = 0; i < COAST_COARSE.rings; i += 1) {
      const [x0, , x1] = COAST_COARSE.bounds.slice(i * 4, i * 4 + 4);
      if (x0 <= southOfBritain.x + southOfBritain.w && x1 >= southOfBritain.x) lonOnly.push(i);
    }
    assert.ok(lonOnly.length > keptS.length,
      `latitude excluded ${lonOnly.length - keptS.length} rings — if it excludes none, `
      + 'half the predicate is untested');
    // the two views must not agree about what is on screen, or neither tests the other
    assert.notDeepEqual(keptS, british);
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

test('the tier drawn is the one nearest what the scale asked for', () => {
  /* Two defects, one on each side of this rule, both found after the first commit.

     "Never finer than wanted" drew 110m facets on zoom-OUT while the 10m data sat in the
     module cache. "Finest in hand" then mounted 827 rings — including the 25,000-point
     Afro-Eurasia path — at a hemisphere view where 42 are indistinguishable. Nearest, tie
     to the finer, is right in both. This drives the same choice `useCoastline` makes,
     against an explicit set of tiers in hand, because the hook itself cannot be unit
     tested without a DOM. */
  const order = ['fine', 'medium', 'coarse'];          // BY_DETAIL
  const pick = (wantedName, inHandNames) => {
    const wantIdx = order.indexOf(wantedName);
    return inHandNames.slice().sort((a, b) => {
      const da = Math.abs(order.indexOf(a) - wantIdx);
      const db = Math.abs(order.indexOf(b) - wantIdx);
      return da - db || order.indexOf(a) - order.indexOf(b);
    })[0];
  };
  // a cold load: only the coarse tier exists
  assert.equal(pick('coarse', ['coarse']), 'coarse');
  assert.equal(pick('fine', ['coarse']), 'coarse', 'and it is honest about it');
  // the wanted tier is in hand — always used, however much else is loaded
  assert.equal(pick('coarse', ['fine', 'medium', 'coarse']), 'coarse',
    'a hemisphere must not mount the 10m outline just because it was once fetched');
  assert.equal(pick('medium', ['fine', 'medium', 'coarse']), 'medium');
  assert.equal(pick('fine', ['fine', 'medium', 'coarse']), 'fine');
  // the gap the first version got wrong: medium never fetched, fine in hand
  assert.equal(pick('medium', ['fine', 'coarse']), 'fine',
    'facets must not appear on zoom OUT while finer data sits in the cache');
});
