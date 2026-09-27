/* Where a trim plate's assemblies stand, held by properties rather than by pictures (WP-14.6,
   PRD §I.6). The corpus case is built from `proportions/systems/trim-classical.json` itself; every
   other case is a seeded synthetic payload, so a failure prints the seed and reproduces. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import {
  assemblyLayout, placeLabels, extentOf, scaleBarIn,
  JOIN_RATIO, GUTTER_FRAC, WALL_STRIP_FRAC, SCALE_BAR_FRAC, SCALE_LADDER_IN,
} from './plate/assemblyLayout.js';
import { feetInches16 } from './fmt.js';

const ROOT = new URL('../../../', import.meta.url);
const EPS = 1e-9;

// a small seeded generator (mulberry32), so a red property names a reproducible input
function rng(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6D2B79F5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// `trim-classical`'s assemblies as the server serves them at no ceiling: the module is its stated
// default, every height is height_modules of it, every projection is projection_parts of a part
function trimClassical() {
  const pk = JSON.parse(readFileSync(new URL('proportions/systems/trim-classical.json', ROOT), 'utf8'));
  const module = pk.module.default_size_in;
  const part = module / pk.module.parts;
  const asm = Array.isArray(pk.assemblies) ? pk.assemblies : Object.entries(pk.assemblies).map(([id, a]) => ({ id, ...a }));
  return asm.map((a) => ({
    id: a.id,
    height_in: a.height_modules * module,
    members: a.members.map((m) => ({ id: m.id, projection_in: (m.projection_parts ?? 0) * part })),
    geometry: null,
  }));
}

// the ×2 rule restated as an oracle: heights tallest first, a new frame whenever the frame's first
// is more than twice the next
function oracleFrames(asms) {
  const sorted = asms.map((a, index) => ({ id: a.id, h: a.height_in, index }))
    .sort((p, q) => (q.h - p.h) || (p.index - q.index));
  const out = [];
  for (const p of sorted) {
    if (out.length && out[out.length - 1][0].h <= 2 * p.h) out[out.length - 1].push(p);
    else out.push([p]);
  }
  return out.map((g) => g.sort((p, q) => p.index - q.index).map((p) => p.id));
}

function checkLayout(asms, layout, box) {
  const placed = layout.frames.flatMap((f) => f.items.map((it) => it.id));
  // no frame overlap: every assembly is in exactly one frame or named in `unplaced`
  assert.equal(new Set(placed).size, placed.length, 'an assembly is in two frames');
  assert.equal(placed.length + layout.unplaced.length, asms.length, 'an assembly was dropped');
  assert.deepEqual(layout.frames.map((f) => f.items.map((it) => it.id)), oracleFrames(asms.filter((a) => placed.includes(a.id))));
  layout.frames.forEach((f, k) => {
    assert.equal(f.index, k);
    const hs = f.items.map((it) => it.heightIn);
    assert.equal(f.heightIn, Math.max(...hs));
    assert.ok(f.heightIn <= JOIN_RATIO * Math.min(...hs) + EPS, `frame ${k} holds heights more than 2:1 apart`);
    if (k + 1 < layout.frames.length) {
      assert.ok(f.heightIn > JOIN_RATIO * layout.frames[k + 1].heightIn, `frame ${k + 1} could have joined frame ${k}`);
    }
    // declaration order on one baseline, and no two items (with their wall strips) overlap
    for (let i = 1; i < f.items.length; i += 1) {
      const a = f.items[i - 1], b = f.items[i];
      assert.ok(a.index < b.index, 'items are not in declaration order');
      assert.ok(a.rightIn + f.gutterIn <= b.leftIn + EPS, `${a.id} and ${b.id} overlap`);
    }
    for (const it of f.items) {
      assert.ok(it.leftIn >= -EPS && it.rightIn <= f.widthIn + EPS, `${it.id} leaves its frame`);
      assert.ok(it.xIn - it.leftIn >= f.wallIn - EPS, `${it.id} has no room for its wall strip`);
      assert.ok(it.heightIn <= f.heightIn + EPS);
    }
    const last = f.items[f.items.length - 1];
    assert.ok(Math.abs(last.rightIn + f.gutterIn - f.widthIn) < 1e-6, 'the last item has no room for its leaders');
    // a stated scale
    assert.ok(SCALE_LADDER_IN.includes(f.scale.barIn));
    assert.equal(f.scale.words, feetInches16(f.scale.barIn));
    if (box) {
      assert.equal(typeof f.scale.pxPerIn, 'number');
      assert.ok(f.widthIn * f.scale.pxPerIn <= box.widthPx + 1e-6 && f.heightIn * f.scale.pxPerIn <= box.heightPx + 1e-6);
      const tight = Math.max(f.widthIn * f.scale.pxPerIn / box.widthPx, f.heightIn * f.scale.pxPerIn / box.heightPx);
      assert.ok(Math.abs(tight - 1) < 1e-9, 'the frame does not fill its box on either axis');
      assert.ok(Math.abs(f.scale.barPx - f.scale.barIn * f.scale.pxPerIn) < 1e-9);
    } else {
      assert.equal(f.scale.pxPerIn, undefined);
    }
  });
}

test('trim-classical gives two frames: the three wall sections, then the three casings', () => {
  const asms = trimClassical();
  // the premise, off the pack: six assemblies, three of them the full module and three far smaller
  const walls = asms.filter((a) => a.id.startsWith('wall_section')).map((a) => a.id);
  const casings = asms.filter((a) => a.id.startsWith('casing')).map((a) => a.id);
  assert.equal(walls.length + casings.length, asms.length);
  assert.ok(walls.length > 0 && casings.length > 0);
  const layout = assemblyLayout(asms, { box: { widthPx: 900, heightPx: 600 } });
  assert.deepEqual(layout.unplaced, []);
  assert.deepEqual(layout.frames.map((f) => f.items.map((it) => it.id)), [walls, casings]);
  checkLayout(asms, layout, { widthPx: 900, heightPx: 600 });
  // the casings are declared 6.0, 4.5, 6.9 and stand in that order, not tallest first
  const casingHeights = layout.frames[1].items.map((it) => it.heightIn);
  assert.deepEqual(casingHeights, casings.map((id) => asms.find((a) => a.id === id).height_in));
  assert.notDeepEqual(casingHeights, [...casingHeights].sort((p, q) => q - p));
  // with no geometry served, the width is read off the members and the item says so
  for (const f of layout.frames) for (const it of f.items) assert.equal(it.extentFrom, 'members');
});

test('the ×2 rule at its boundary: exactly twice joins, a hair over opens a frame, and greed is by the first', () => {
  const mk = (hs) => hs.map((h, i) => ({ id: `a${i}`, height_in: h }));
  assert.deepEqual(assemblyLayout(mk([10, 5])).frames.map((f) => f.items.map((i) => i.id)), [['a0', 'a1']]);
  assert.deepEqual(assemblyLayout(mk([10, 5 - 1e-9])).frames.length, 2);
  // 10 then 6 then 4.5: 6 joins 10, and 4.5 is measured against 10 (the frame's tallest), not 6
  assert.deepEqual(assemblyLayout(mk([4.5, 10, 6])).frames.map((f) => f.items.map((i) => i.id)), [['a1', 'a2'], ['a0']]);
  assert.equal(JOIN_RATIO, 2);
});

test('property: random payloads lay out with no overlap, one scale per frame, nothing dropped', () => {
  for (let seed = 1; seed <= 300; seed += 1) {
    const r = rng(seed);
    const n = 1 + Math.floor(r() * 9);
    const asms = [];
    for (let i = 0; i < n; i += 1) {
      const h = Math.exp(Math.log(0.5) + r() * (Math.log(200) - Math.log(0.5)));
      const faces = [];
      let y = 0;
      const k = Math.floor(r() * 5);
      for (let j = 0; j < k; j += 1) {
        const y1 = y + h / Math.max(1, k);
        const x = (r() - 0.2) * h * 0.2, xf = (r() - 0.2) * h * 0.2;
        const segs = [{ kind: 'line', to: [x, y1] }];
        if (r() < 0.5) {
          const rx = r() * h * 0.1, a0 = (r() - 0.5) * 4, a1 = a0 + (r() - 0.5) * 3;
          const cx = (r() - 0.3) * h * 0.1;
          segs.push({ kind: 'arc', cx, cy: y, rx, ry: rx, a0, a1, to: [cx + rx * Math.cos(a1), y1] });
        }
        faces.push({ id: `m${j}`, x, x_from: xf, y0: y, y1, segments: segs });
        y = y1;
      }
      const shape = r();
      if (shape < 0.08) asms.push({ id: `s${seed}-${i}`, height_in: shape < 0.04 ? 0 : null });
      else asms.push({ id: `s${seed}-${i}`, height_in: h, geometry: faces.length ? { faces } : null, members: [{ projection_in: r() * 2 }] });
    }
    const box = seed % 2 ? { widthPx: 300 + r() * 900, heightPx: 200 + r() * 600 } : null;
    const layout = assemblyLayout(asms, { box });
    try {
      checkLayout(asms, layout, box);
      // the extent holds every figure a face states
      for (const f of layout.frames) {
        for (const it of f.items) {
          const a = asms.find((x) => x.id === it.id);
          for (const face of (a.geometry && a.geometry.faces) || []) {
            for (const v of [face.x, face.x_from]) assert.ok(v >= it.minXIn - EPS && v <= it.maxXIn + EPS);
          }
        }
      }
    } catch (e) {
      e.message = `seed ${seed}: ${e.message}`;
      throw e;
    }
  }
});

test('an arc is bounded where its own angles cross the horizontal, and nowhere else', () => {
  const sample = (s) => {
    const xs = [];
    for (let i = 0; i <= 2000; i += 1) xs.push(s.cx + s.rx * Math.cos(s.a0 + (s.a1 - s.a0) * (i / 2000)));
    return [Math.min(...xs), Math.max(...xs)];
  };
  const cases = [
    { kind: 'arc', cx: 1, cy: 0, rx: 2, ry: 2, a0: -0.5, a1: 0.5, to: [0, 0] },            // crosses 0
    { kind: 'arc', cx: 1, cy: 0, rx: 2, ry: 2, a0: 2.5, a1: 3.8, to: [0, 0] },             // crosses π
    { kind: 'arc', cx: 1, cy: 0, rx: 2, ry: 2, a0: 0.3, a1: 1.2, to: [0, 0] },             // crosses neither
    { kind: 'arc', cx: 1, cy: 0, rx: 2, ry: 2, a0: 7.0, a1: 6.0, to: [0, 0] },             // clockwise past 2π
  ];
  for (const s of cases) {
    const [lo, hi] = sample(s);
    const ends = [s.cx + s.rx * Math.cos(s.a0), s.cx + s.rx * Math.cos(s.a1)];
    const e = extentOf({ geometry: { faces: [{ x: ends[0], x_from: ends[1], segments: [s] }] } });
    assert.equal(e.extentFrom, 'geometry');
    // the extent reaches the arc's far side (0 is always in it: the wall plane)
    assert.ok(Math.abs(e.maxX - Math.max(0, hi)) < 1e-5, `a0 ${s.a0}: max ${e.maxX} against ${hi}`);
    assert.ok(Math.abs(e.minX - Math.min(0, lo)) < 1e-5, `a0 ${s.a0}: min ${e.minX} against ${lo}`);
  }
  // a hollow that turns behind the wall plane reserves the room behind it
  const hollow = extentOf({ geometry: { faces: [{ x: 1, x_from: 2, segments: [{ kind: 'line', to: [-0.75, 3] }] }] } });
  assert.equal(hollow.minX, -0.75);
  const lay = assemblyLayout([{ id: 'h', height_in: 1, geometry: { faces: [{ x: 1, x_from: 2, segments: [{ kind: 'line', to: [-0.75, 3] }] }] } }]);
  assert.ok(lay.frames[0].items[0].xIn >= 0.75 - EPS);
});

test('geometry outranks members, and a record with neither is drawn at no width and says so', () => {
  assert.equal(extentOf({ geometry: { faces: [{ x: 3, x_from: 0 }] }, members: [{ projection_in: 9 }] }).maxX, 3);
  const m = extentOf({ geometry: null, members: [{ projection_in: 1.5 }, { projection_in: 0.25 }] });
  assert.deepEqual(m, { minX: 0, maxX: 1.5, extentFrom: 'members' });
  assert.deepEqual(extentOf({ id: 'bare' }), { minX: 0, maxX: 0, extentFrom: 'none' });
  assert.deepEqual(extentOf(null), { minX: 0, maxX: 0, extentFrom: 'none' });
});

test('an assembly that cannot be placed is named with its reason, never dropped', () => {
  const asms = [
    { id: 'ok', height_in: 12 }, { id: 'zero', height_in: 0 }, { id: 'neg', height_in: -3 },
    { id: 'nan', height_in: NaN }, { id: 'missing' }, { height_in: 5 }, null,
  ];
  const { frames, unplaced } = assemblyLayout(asms);
  assert.deepEqual(frames.flatMap((f) => f.items.map((i) => i.id)), ['ok']);
  assert.deepEqual(unplaced.map((u) => [u.id, u.index]), [['zero', 1], ['neg', 2], ['nan', 3], ['missing', 4], [null, 5], [null, 6]]);
  for (const u of unplaced) assert.ok(typeof u.reason === 'string' && u.reason.length > 0);
  assert.deepEqual(assemblyLayout(undefined), { frames: [], unplaced: [] });
});

test("the gutter and the wall strip are the frame's own fractions, so a label gets the same pixels in every frame", () => {
  const asms = trimClassical();
  const box = { widthPx: 100000, heightPx: 600 };            // height-limited, as a plate row is
  const { frames } = assemblyLayout(asms, { box });
  assert.ok(frames.length >= 2);
  const gutters = frames.map((f) => f.gutterIn * f.scale.pxPerIn);
  const walls = frames.map((f) => f.wallIn * f.scale.pxPerIn);
  for (const g of gutters) assert.ok(Math.abs(g - GUTTER_FRAC * box.heightPx) < 1e-9);
  for (const w of walls) assert.ok(Math.abs(w - WALL_STRIP_FRAC * box.heightPx) < 1e-9);
  assert.ok(WALL_STRIP_FRAC > 0 && WALL_STRIP_FRAC < GUTTER_FRAC && GUTTER_FRAC < 1);
});

test('the scale bar is the longest ladder length within its share of the frame, printed as the corpus prints it', () => {
  for (let i = 1; i < SCALE_LADDER_IN.length; i += 1) assert.ok(SCALE_LADDER_IN[i] > SCALE_LADDER_IN[i - 1]);
  for (const v of SCALE_LADDER_IN) assert.ok(Number.isInteger(v * 16), `${v} is not a whole sixteenth`);
  for (const h of [0.2, 1, 4.5, 6.9, 12, 114, 400, 2000]) {
    const bar = scaleBarIn(h);
    const cap = SCALE_BAR_FRAC * h;
    if (SCALE_LADDER_IN[0] <= cap) {
      assert.ok(bar <= cap);
      const next = SCALE_LADDER_IN[SCALE_LADDER_IN.indexOf(bar) + 1];
      assert.ok(next === undefined || next > cap, `${h}: ${next} also fits`);
    } else {
      assert.equal(bar, SCALE_LADDER_IN[0]);                // the shortest rung, and never nothing
    }
  }
  const { frames } = assemblyLayout(trimClassical());
  assert.deepEqual(frames.map((f) => f.scale.words), frames.map((f) => feetInches16(scaleBarIn(f.heightIn))));
});

// --------------------------------------------------------------------------------- placeLabels
function checkLabels(input, out, { minGapPx, top = null, bottom = null }) {
  assert.equal(out.labels.length, input.length);
  const hs = input.map((l) => (l.h > 0 ? l.h : minGapPx));
  const order = input.map((l, i) => i).sort((a, b) => (input[a].y - input[b].y) || (a - b));
  for (let k = 1; k < order.length; k += 1) {
    const a = order[k - 1], b = order[k];
    const need = Math.max(minGapPx, (hs[a] + hs[b]) / 2);
    assert.ok(out.labels[b].y - out.labels[a].y >= need - 1e-6, `labels ${a} and ${b} collide or swap`);
  }
  out.labels.forEach((l, i) => { assert.equal(l.id, input[i].id); assert.equal(l.desiredY, input[i].y); });
  const span = order.reduce((acc, i, k) => acc + (k ? Math.max(minGapPx, (hs[order[k - 1]] + hs[i]) / 2) : 0), 0)
    + (order.length ? (hs[order[0]] + hs[order[order.length - 1]]) / 2 : 0);
  if (top !== null && bottom !== null) {
    const fits = span <= bottom - top + 1e-9;
    assert.equal(out.overflow, !fits);
    if (fits) {
      out.labels.forEach((l, i) => assert.ok(l.y - hs[i] / 2 >= top - 1e-6 && l.y + hs[i] / 2 <= bottom + 1e-6, `label ${i} leaves its bounds`));
    }
  } else {
    assert.equal(out.overflow, false);
  }
}

test('property: labels keep their order, never collide, and stay inside their bounds when they fit', () => {
  for (let seed = 1; seed <= 400; seed += 1) {
    const r = rng(1000 + seed);
    const n = Math.floor(r() * 14);
    const minGapPx = 6 + r() * 10;
    const labels = Array.from({ length: n }, (_, i) => ({ id: `l${i}`, y: r() * 300, h: r() < 0.5 ? 4 + r() * 20 : undefined }));
    const bounded = seed % 3 !== 0;
    const opts = bounded ? { minGapPx, top: 0, bottom: 150 + r() * 300 } : { minGapPx };
    try {
      checkLabels(labels, placeLabels(labels, opts), opts);
    } catch (e) {
      e.message = `seed ${seed}: ${e.message}`;
      throw e;
    }
  }
});

test('a label with room to spare does not move, and two that collide share the displacement', () => {
  const clear = [{ id: 'a', y: 10 }, { id: 'b', y: 40 }, { id: 'c', y: 100 }];
  assert.deepEqual(placeLabels(clear, { minGapPx: 12 }).labels.map((l) => l.y), [10, 40, 100]);
  const pair = placeLabels([{ id: 'a', y: 50 }, { id: 'b', y: 50 }], { minGapPx: 12 }).labels;
  assert.deepEqual(pair.map((l) => l.y), [44, 56]);
  // a tie keeps the input order; bounds push a cluster in without reordering it
  const pushed = placeLabels([{ id: 'a', y: 0 }, { id: 'b', y: 2 }], { minGapPx: 10, top: 0, bottom: 100 });
  assert.deepEqual(pushed.labels.map((l) => l.y), [5, 15]);
  assert.equal(pushed.overflow, false);
  const over = placeLabels([{ id: 'a', y: 0 }, { id: 'b', y: 0 }, { id: 'c', y: 0 }], { minGapPx: 10, top: 0, bottom: 20 });
  assert.equal(over.overflow, true);
  assert.deepEqual(over.labels.map((l) => l.y), [5, 15, 25]);    // spaced, overflowing, not overlapped
  assert.deepEqual(placeLabels([], { minGapPx: 10 }), { labels: [], overflow: false });
});
