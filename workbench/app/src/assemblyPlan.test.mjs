/* THE WALL-DATUM PLATE'S PIXELS, DRIVEN WITHOUT A BROWSER (WP-14.9, PRD §I.6).

   `components/AssemblyPlate.jsx` imports React and cannot run here, so everything it decides
   about a frame is `plate/assemblyPlan.js` and is driven on hand-built assemblies. The fixtures
   are SYNTHETIC on purpose: a test that read the shipped `trim-classical` would pin one pack's
   member count, which is the payload's to state (the walk holds the real plate's band count to
   the served faces). Every property below is one a reader would see break: a band that is not the
   face the server sent, two labels on top of each other, a label outside its frame, leaders that
   cross, a numeral with no key row. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { assemblyLayout } from './plate/assemblyLayout.js';
import {
  planFrame, partTicks, planLegend, PAD_TOP, PAD_BOTTOM, LINE_PX, MIN_FONT_PX, MAX_PART_TICKS,
} from './plate/assemblyPlan.js';

const measure = (t, px) => String(t).length * px * 0.55;

/* A rectangular face, as `profiles.py` would serve a flat member on the wall datum. */
function face(id, y0, y1, x) {
  return {
    id, x, x_from: 0, y0, y1,
    segments: [{ kind: 'line', to: [x, y0] }, { kind: 'line', to: [x, y1] }],
    path: `M 0,${y0} L ${x},${y0} L ${x},${y1} L 0,${y1} Z`,
  };
}

/* An assembly from [id, name, height_in, projection_in] rows, stacked bottom to top. */
function assembly(id, rows, { drop = [] } = {}) {
  let y = 0;
  const members = [];
  const faces = [];
  for (const [mid, name, h, p] of rows) {
    members.push({ id: mid, name, height_in: h, projection_in: p });
    if (!drop.includes(mid)) faces.push(face(mid, y, y + h, p));
    y += h;
  }
  return { id, height_in: y, members, geometry: { faces }, unconstructed: [] };
}

const WALL = [
  ['plinth', 'Base board', 6.9, 0.9], ['cap', 'Base cap', 1.6, 1.2], ['fillet', 'Fillet', 0.5, 1.3],
  ['dado', 'Dado', 12.0, 0.6], ['surbase', 'Surbase', 2.0, 1.4], ['listel', 'Listel', 0.4, 1.5],
  ['field', 'Wall field', 72.0, 0], ['bed', 'Bed mould', 3.0, 2.0], ['fascia', 'Fascia', 6.0, 2.6],
  ['cyma', 'Cyma recta', 4.6, 4.8], ['crown', 'Crown fillet', 5.0, 5.0],
];
const CASING = [
  ['reveal', 'Reveal', 0.6, 0.3], ['fascia1', 'First fascia', 2.0, 0.6], ['bead', 'Bead', 0.4, 0.8],
  ['fascia2', 'Second fascia', 2.2, 0.8], ['backband', 'Backband', 1.7, 1.2],
];

function fixture() {
  return [
    assembly('wall_a', WALL),
    assembly('wall_b', WALL.map(([i, n, h, p]) => [`${i}_b`, n, h, p])),
    assembly('casing_a', CASING),
  ];
}

function plans(assemblies, box = { widthPx: 900, heightPx: 520 }, opt = {}) {
  const byId = new Map(assemblies.map((a) => [a.id, a]));
  const { frames } = assemblyLayout(assemblies, { box });
  return frames.map((f) => planFrame(f, byId, { partIn: 6, measure, ...opt }));
}

test('a frame without a scale is not planned: there is nothing to put pixels on', () => {
  const { frames } = assemblyLayout(fixture());
  assert.ok(frames.length > 0, 'the premise: the fixture lays out');
  assert.equal(planFrame(frames[0], new Map(), { measure }), null);
});

test('one band per served face, its path the face’s own string, placed by one translate and scale', () => {
  const asms = fixture();
  const ps = plans(asms);
  const served = asms.reduce((n, a) => n + a.geometry.faces.length, 0);
  const drawn = ps.reduce((n, p) => n + p.items.reduce((m, it) => m + it.bands.length, 0), 0);
  assert.equal(drawn, served, 'every face is a band and no band is anything else');
  for (const p of ps) {
    for (const it of p.items) {
      const a = asms.find((x) => x.id === it.id);
      it.bands.forEach((b, i) => {
        assert.equal(b.d, a.geometry.faces[i].path, 'the band IS the served path, not a curve built here');
        assert.equal(b.asm, it.id);
        assert.equal(b.member, a.geometry.faces[i].id);
      });
      assert.equal(it.transform, `translate(${it.wallX},${p.base}) scale(${p.pxPerIn},${-p.pxPerIn})`);
    }
  }
});

function eachItemLabels(p, fn) {
  for (const it of p.items) fn(it, p.labels.filter((l) => l.asm === it.id));
}

test('no two labels of an item overlap, and every label is inside its frame', () => {
  for (const p of plans(fixture())) {
    assert.ok(p.labels.length > 0, 'the premise: the frame carries labels');
    const frameBottom = p.height - PAD_BOTTOM;
    eachItemLabels(p, (it, ls) => {
      const spans = ls.map((l) => [l.y - l.h / 2, l.y + l.h / 2]).sort((a, b) => a[0] - b[0]);
      for (let i = 1; i < spans.length; i += 1) {
        assert.ok(spans[i][0] >= spans[i - 1][1] - 1e-6, `${it.id}: labels ${i - 1} and ${i} overlap`);
      }
      for (const l of ls) {
        assert.ok(l.y - l.h / 2 >= PAD_TOP - 1e-6, `${l.member}: above the frame's top`);
        assert.ok(l.y + l.h / 2 <= frameBottom + 1e-6, `${l.member}: below the frame's foot`);
        const w = Math.max(...l.lines.map((s) => measure(s, l.font)));
        assert.ok(l.x + w <= p.width, `${l.member}: runs off the frame's right edge`);
        if (l.kind === 'letter') assert.ok(l.x + w <= it.colRight + 1e-6, `${l.member}: runs out of its column`);
      }
    });
  }
});

test('leaders elbow at one knee per item and keep their order, so none crosses another', () => {
  for (const p of plans(fixture())) {
    eachItemLabels(p, (it, ls) => {
      for (const l of ls) {
        assert.equal(l.leader.length, 3);
        assert.equal(l.leader[1][0], it.kneeX, 'the elbow is the item’s one knee');
        assert.equal(l.leader[1][1], l.leader[0][1], 'the first run is horizontal, at the face');
        assert.equal(l.leader[2][0], it.colX, 'and ends at the label column');
        assert.ok(l.leader[0][0] <= it.kneeX, 'the anchor is on the drawing, left of the knee');
      }
      const byAnchor = [...ls].sort((a, b) => a.leader[0][1] - b.leader[0][1]);
      for (let i = 1; i < byAnchor.length; i += 1) {
        assert.ok(byAnchor[i].y >= byAnchor[i - 1].y, `${it.id}: two leaders cross`);
      }
    });
  }
});

test('a member too thin to letter takes a numeral, and the key names every numeral', () => {
  const ps = plans(fixture());
  let thin = 0;
  for (const p of ps) {
    const numerals = p.labels.filter((l) => l.kind === 'numeral');
    assert.deepEqual(numerals.map((l) => l.numeral), numerals.map((_, i) => i + 1), 'numbered 1, 2, 3 … per frame');
    const keyed = p.key.filter((k) => k.numeral != null);
    assert.deepEqual(keyed.map((k) => k.numeral), numerals.map((l) => l.numeral));
    for (const k of keyed) {
      const l = numerals.find((x) => x.numeral === k.numeral);
      assert.equal(k.member, l.member);
      assert.ok(k.name && k.words, 'a key row carries the member’s name and height');
    }
    for (const it of p.items) {
      for (const b of it.bands) {
        const l = p.labels.find((x) => x.member === b.member);
        if (b.bandPx < LINE_PX) { thin += 1; assert.equal(l.kind, 'numeral', `${b.member} is ${b.bandPx}px high`); }
        if (l.kind === 'letter') assert.ok(l.font >= MIN_FONT_PX);
      }
    }
  }
  assert.ok(thin > 0, 'the premise: the fixture has a member too thin to letter');
});

test('a lettered label says the member’s name and its height in the engine’s notation', () => {
  const [p] = plans(fixture());
  const field = p.labels.find((l) => l.member === 'field');
  assert.equal(field.kind, 'letter', 'the premise: a seventy-two inch band is lettered');
  assert.deepEqual(field.lines, ['Wall field', '6\'-0"']);
});

test('where the labels cannot fit, lettering gives way first and the frame grows last — never an overlap', () => {
  const asms = [assembly('crowded', Array.from({ length: 24 }, (_, i) => [`m${i}`, `Member ${i}`, 0.25, 0.5]))];
  const [p] = plans(asms, { widthPx: 400, heightPx: 40 });
  assert.ok(p.labels.every((l) => l.kind === 'numeral'), 'lettering gave way');
  const lowest = Math.max(...p.labels.map((l) => l.y + l.h / 2));
  assert.ok(lowest > p.base, 'the premise: twenty-four numerals do not fit in forty pixels');
  assert.ok(p.height - PAD_BOTTOM >= lowest - 1e-6, 'the frame grew to hold them');
  assert.ok(p.scale.y > lowest, 'and the scale bar sits below the last of them');
});

test('a member a side-by-side assembly does not draw is in the key and says so', () => {
  const asms = [assembly('pair', [['a', 'Arch', 20, 3], ['b', 'Alfiz', 20, 4]], { drop: ['b'] })];
  const [p] = plans(asms);
  assert.equal(p.items[0].bands.length, 1);
  const b = p.key.find((k) => k.member === 'b');
  assert.ok(b, 'the undrawn member is keyed');
  assert.equal(b.drawn, false);
  assert.equal(b.numeral, null);
});

test('part ticks up the wall where there are sixty or fewer, and none where there would be more', () => {
  assert.deepEqual(partTicks(19, 6), [0, 6, 12, 18]);
  assert.deepEqual(partTicks(114, 6).length, 20);
  assert.deepEqual(partTicks(MAX_PART_TICKS - 1, 1).length, MAX_PART_TICKS);
  assert.deepEqual(partTicks(MAX_PART_TICKS, 1), [], 'sixty-one ticks are a smear, not a scale');
  for (const bad of [[0, 6], [10, 0], [10, null], [null, 6], [10, -1]]) assert.deepEqual(partTicks(...bad), []);
});

test('the in-frame key places the glossary’s words and writes none of its own', () => {
  const words = { member: 'member', wallPlane: 'wall plane', part: 'part' };
  const withTicks = planLegend({ x: 0, y: 0, words, measure, ticks: true });
  assert.deepEqual(withTicks.entries.map((e) => [e.kind, e.word]), [['member', 'member'], ['chain', 'wall plane'], ['tick', 'part']]);
  const noTicks = planLegend({ x: 0, y: 0, words, measure, ticks: false });
  assert.deepEqual(noTicks.entries.map((e) => e.kind), ['member', 'chain'], 'no tick in the key where no tick is drawn');
  const loading = planLegend({ x: 0, y: 0, words: {}, measure, ticks: true });
  assert.ok(loading.entries.every((e) => e.word === null), 'a word that has not arrived is not guessed');
});

test('the plan holds no arc arithmetic and no word a reader sees', () => {
  const src = readFileSync(fileURLToPath(new URL('./plate/assemblyPlan.js', import.meta.url)), 'utf8')
    .replace(/\/\*[\s\S]*?\*\//g, '').replace(/(^|[\s;,{}()])\/\/[^\n]*/g, '$1');
  for (const banned of ['segments', 'Math.cos', 'Math.sin', 'Math.atan', 'sweep', 'a0', 'a1']) {
    assert.ok(!src.includes(banned), `assemblyPlan.js reads ${banned}: a curve is the server's, never rebuilt here`);
  }
  const phrases = [...src.matchAll(/'([^'\n]*)'|"([^"\n]*)"|`([^`\n]*)`/g)].map((m) => m[1] ?? m[2] ?? m[3])
    .filter((s) => /[A-Za-z]{2,}\s+[A-Za-z]{2,}/.test(s));
  assert.deepEqual(phrases, [], 'every word on the plate is the payload’s or a glossary record’s');
});
