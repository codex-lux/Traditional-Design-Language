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
import { assemblyLayout, extentOf, TURNED_AXIS } from './plate/assemblyLayout.js';
import {
  planFrame, partTicks, planLegend, PAD_TOP, PAD_BOTTOM, LINE_PX, MIN_FONT_PX, MAX_PART_TICKS,
  zoneString, planThumb, bandTransform,
} from './plate/assemblyPlan.js';
import { feetInches16 } from './fmt.js';

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

/* ───────────── WP-14.24: plates at the pack's word — turned casings and zone strings ─────────────

   The ruling (25 Sep 2026, `oq/casings-are-measured-across-and-drawn-upright`): an assembly's
   `axis` and `zones` are data, and the plate draws casings turned and prints the zone string.
   Every figure below is read off a fixture's own served fields; the only typed string is the one
   the Georgian wall's record implies, and it is typed where the test shows it is derived. */

const PART = 6;
// a wall whose members land on the Georgian division: 24 in of pedestal, 72 of field, 18 of top
const GEORGIAN = [
  ['plinth', 'Base board', 6.9, 0.9], ['cap', 'Base cap', 1.62, 1.2], ['fillet', 'Fillet', 0.48, 1.3],
  ['dado', 'Dado', 12.6, 0.6], ['surbase', 'Surbase', 2.0, 1.4], ['listel', 'Listel', 0.4, 1.5],
  ['field', 'Wall field', 72.0, 0], ['bed', 'Bed mould', 3.0, 2.0], ['fascia', 'Fascia', 6.0, 2.6],
  ['cyma', 'Cyma recta', 4.0, 4.8], ['crown', 'Crown fillet', 5.0, 5.0],
];
const GEORGIAN_ZONES = [
  { name: 'pedestal', to_parts: 4 }, { name: 'wall field', to_parts: 16 }, { name: 'entablature', to_parts: 19 },
];
const rowsOf = (id, rows) => rows.map(([i, n, h, p]) => [`${id}_${i}`, n, h, p]);
const zonedWall = (id) => ({ ...assembly(id, rowsOf(id, GEORGIAN)), zones: GEORGIAN_ZONES });
// the Federal wall: the same kind of wall, and its record gives it no zones
const federalWall = (id) => assembly(id, rowsOf(id, GEORGIAN));
const turnedCasing = (id) => ({ ...assembly(id, rowsOf(id, CASING)), axis: TURNED_AXIS });
const diffs = (zs) => zs.map((z, i) => z.to_parts - (i ? zs[i - 1].to_parts : 0));

test('the zone string is the differences of the served to_parts, each figure in inches through feetInches16', () => {
  const z = zoneString(GEORGIAN_ZONES, PART);
  assert.equal(z.parts, diffs(GEORGIAN_ZONES).map(String).join(' + '), 'derived from the record, not typed');
  assert.equal(z.parts, '4 + 12 + 3', 'which, for the Georgian wall’s own record, is the pack’s 4 + 12 + 3');
  assert.equal(z.inches, diffs(GEORGIAN_ZONES).map((d) => feetInches16(d * PART)).join(' + '));
  assert.deepEqual(z.runs.map((r) => r.name), GEORGIAN_ZONES.map((g) => g.name), 'each run is its zone, by name');
  // not a lookup of the one case: another division reads as its own differences
  const other = [{ name: 'a', to_parts: 3.75 }, { name: 'b', to_parts: 16.25 }, { name: 'c', to_parts: 19 }];
  assert.equal(zoneString(other, PART).parts, '3.75 + 12.5 + 2.75');
  assert.equal(zoneString(other, null).inches, null, 'no part served: parts only, no inches guessed');
  // a list the checker would refuse is not a division, and is not drawn as a guess
  for (const bad of [null, [], [{ to_parts: 4 }], [{ to_parts: 4 }, { to_parts: 4 }], [{ to_parts: 4 }, { to_parts: 'x' }]]) {
    assert.equal(zoneString(bad, PART), null, JSON.stringify(bad));
  }
  // and the plate draws exactly that string, a tick at every boundary and each run's figure
  const [p] = plans([zonedWall('wall_g')]);
  const it = p.items[0];
  assert.equal(it.zones.parts, zoneString(GEORGIAN_ZONES, PART).parts);
  assert.deepEqual(it.zones.figures.map((f) => f.run.parts), diffs(GEORGIAN_ZONES).map(String));
  const tickYs = it.zones.ticks.map((t) => t[1]);
  const wantYs = [0, ...GEORGIAN_ZONES.map((g) => g.to_parts)].map((t) => p.base - t * PART * p.pxPerIn);
  tickYs.forEach((y, i) => assert.ok(Math.abs(y - wantYs[i]) < 1e-9, 'a tick at every boundary, at the served to_parts'));
  assert.equal(tickYs.length, wantYs.length);
  assert.ok(it.zones.line.x1 < it.strip.x, 'the zone line runs behind the wall strip');
  assert.ok(it.zones.line.x1 >= it.leftX, 'inside the room the layout reserved for it');
  assert.ok(it.zones.string && it.zones.string.y > p.base, 'the string is drawn under the assembly');
  assert.ok(p.legend.entries.some((e) => e.kind === 'zone'), 'the key has a zone mark where zones are drawn');
});

test('no zone string without zones: a Federal wall draws none, beside a Georgian one or alone', () => {
  const [both] = plans([zonedWall('wall_g'), federalWall('wall_f')]);
  const fed = both.items.find((it) => it.id === 'wall_f');
  assert.equal(fed.zones, null, 'the Federal wall’s record gives no zones, so none is drawn');
  assert.equal(both.items.find((it) => it.id === 'wall_g').zones.parts, '4 + 12 + 3', 'the premise: its neighbour carries one');
  const [alone] = plans([federalWall('wall_f')]);
  assert.ok(alone.items.every((it) => it.zones === null), 'no string, no tick, no figure');
  assert.ok(!alone.legend.entries.some((e) => e.kind === 'zone'), 'and no zone mark in the key');
  // and nothing is reserved for a line that is not drawn
  const lay = assemblyLayout([federalWall('wall_f')], { box: { widthPx: 900, heightPx: 520 } });
  assert.equal(lay.frames[0].items[0].zoneReserveIn, 0);
});

test('a turned assembly is drawn by one rotate, and its drawn box is wider than it is tall', () => {
  const asm = turnedCasing('casing_a');
  const [p] = plans([asm]);
  const it = p.items[0];
  assert.equal(it.turned, true);
  assert.ok(it.box.width > it.box.height, `drawn ${it.box.width} wide by ${it.box.height} tall`);
  assert.ok(Math.abs(it.box.width - asm.height_in * p.pxPerIn) < 1e-6, 'its width is its height_in: measured across');
  assert.equal(it.transform, bandTransform({ x: it.wallX, y: it.planeY, k: p.pxPerIn, turned: true }));
  assert.equal(it.transform, `translate(${it.wallX},${it.planeY}) rotate(90) scale(${p.pxPerIn},${-p.pxPerIn})`,
    'the translate and the scale, and ONE rotate between them');
  assert.equal((it.transform.match(/rotate/g) || []).length, 1);
  it.bands.forEach((b, i) => assert.equal(b.d, asm.geometry.faces[i].path, 'the served path, turned by the transform only'));
  // the control: the same record without its axis stands upright and taller than wide
  const [u] = plans([assembly('casing_u', CASING)]);
  assert.equal(u.items[0].turned, false);
  assert.ok(u.items[0].box.height > u.items[0].box.width);
  assert.doesNotMatch(u.items[0].transform, /rotate/);
  assert.deepEqual([p.orientations.upright, p.orientations.turned], [false, true], 'its frame is captioned drawn turned');
  assert.deepEqual([u.orientations.upright, u.orientations.turned], [true, false], 'and the control drawn upright');
});

test('a turned assembly’s members take numerals, in their own order from the jamb, none on another', () => {
  const [p] = plans([turnedCasing('casing_a'), turnedCasing('casing_b')]);
  for (const it of p.items) {
    const ls = p.labels.filter((l) => l.asm === it.id);
    assert.equal(ls.length, it.bands.length, 'a label per band');
    assert.ok(ls.every((l) => l.kind === 'numeral'), 'side by side, a name would run across its neighbours');
    for (let i = 1; i < ls.length; i += 1) {
      assert.ok(ls[i].x >= ls[i - 1].x + ls[i - 1].w - 1e-6, `${it.id}: numerals ${i - 1} and ${i} overlap or swap`);
    }
    for (const l of ls) {
      assert.equal(l.leader[0][0], l.leader[1][0], 'the first run drops straight from the face');
      assert.equal(l.leader[1][1], it.kneeY, 'to the item’s one knee');
      assert.ok(l.leader[0][1] <= it.kneeY, 'the anchor is on the drawing, above the knee');
      assert.ok(l.x >= 0 && l.x + l.w <= p.width, `${l.member}: off the frame`);
      assert.ok(l.y + l.h / 2 <= p.height - PAD_BOTTOM + 1e-6, `${l.member}: below the frame’s foot`);
    }
    const ax = it.bands.map((b) => b.anchor.x);
    for (let i = 1; i < ax.length; i += 1) assert.ok(ax[i] > ax[i - 1], 'the jamb is at the left and the members read outward');
  }
  const keyed = p.key.filter((k) => k.numeral != null).map((k) => k.numeral);
  assert.deepEqual(keyed, p.labels.map((l) => l.numeral), 'the key names every numeral');
});

test('extentOf swaps the extent of a turned assembly, and its frame is set by its depth', () => {
  const up = assembly('c', CASING);
  const t = turnedCasing('c');
  const e0 = extentOf(up), e1 = extentOf(t);
  assert.deepEqual([e1.minX, e1.maxX], [0, t.height_in], 'across the page: the jamb to the far edge');
  assert.deepEqual([e1.minY, e1.maxY], [e0.minX, e0.maxX], 'down the page: what the wall plane gave across it');
  assert.equal(e1.turned, true);
  const lay = assemblyLayout([zonedWall('w'), t], { box: { widthPx: 900, heightPx: 520 } });
  assert.deepEqual(lay.frames.map((f) => f.items.map((i) => i.id)), [['w'], ['c']],
    'a casing an inch deep is not drawn at a wall’s scale');
  const it = lay.frames[1].items[0];
  assert.ok(it.sizeIn <= lay.frames[1].heightIn + 1e-9, 'its wall strip and its depth fit its frame');
  assert.ok(Math.abs(it.rightIn - it.leftIn - t.height_in) < 1e-9);
  // a turned record that projects nothing is named, never drawn at no depth
  const none = assemblyLayout([{ id: 'flat', height_in: 6, axis: TURNED_AXIS, members: [{ projection_in: 0 }] }]);
  assert.deepEqual(none.frames, []);
  assert.equal(none.unplaced[0].id, 'flat');
});

test('the shipped trim-classical record: its casings turned, its Georgian wall zoned, the others neither', () => {
  const pk = JSON.parse(readFileSync(new URL('../../../proportions/systems/trim-classical.json', import.meta.url), 'utf8'));
  const part = pk.module.default_size_in / pk.module.parts;
  const asms = Object.entries(pk.assemblies).map(([id, a]) => ({
    id, height_in: a.height_modules * pk.module.default_size_in, axis: a.axis, zones: a.zones,
    members: a.members.map((m) => ({ id: m.id, projection_in: (m.projection_parts ?? 0) * part })),
    geometry: null,
  }));
  const turned = asms.filter((a) => a.axis === TURNED_AXIS).map((a) => a.id);
  const zoned = asms.filter((a) => a.zones).map((a) => a.id);
  assert.ok(turned.length > 0 && zoned.length > 0, 'the premise: the record declares both');
  const lay = assemblyLayout(asms, { box: { widthPx: 900, heightPx: 520 } });
  for (const f of lay.frames) {
    for (const it of f.items) assert.equal(it.turned, turned.includes(it.id), `${it.id}: turned as the record says`);
  }
  const frameOf = (id) => lay.frames.findIndex((f) => f.items.some((it) => it.id === id));
  assert.ok(turned.every((id) => frameOf(id) !== frameOf(zoned[0])), 'the casings are not drawn at the walls’ scale');
  for (const a of asms) {
    const z = zoneString(a.zones, part);
    if (zoned.includes(a.id)) assert.equal(z.parts, diffs(a.zones).map(String).join(' + '));
    else assert.equal(z, null, `${a.id} carries no zone string`);
  }
});

test('a thumbnail is the served first assembly made small: one scale, centred, turned where the record turns it', () => {
  const W = 40, H = 52;
  const wall = zonedWall('w');
  const tw = planThumb(wall, { widthPx: W, heightPx: H });
  assert.ok(Math.abs(tw.box.height - H) < 1e-9 && tw.box.width <= W + 1e-9, 'a tall wall fills the height');
  assert.ok(tw.box.x >= -1e-9 && tw.box.y >= -1e-9 && tw.box.x + tw.box.width <= W + 1e-9 && tw.box.y + tw.box.height <= H + 1e-9);
  assert.deepEqual(tw.paths.map((q) => q.d), wall.geometry.faces.map((f) => f.path), 'the served paths and nothing else');
  assert.doesNotMatch(tw.transform, /rotate/);
  const tc = planThumb(turnedCasing('c'), { widthPx: W, heightPx: H });
  assert.equal(tc.turned, true);
  assert.ok(tc.box.width > tc.box.height, 'a turned casing is wider than tall in the index as on the plate');
  assert.ok(Math.abs(tc.box.width - W) < 1e-9);
  assert.equal((tc.transform.match(/rotate/g) || []).length, 1);
  // nothing to draw is nothing drawn
  assert.equal(planThumb({ id: 'x', height_in: 10, geometry: { faces: [] } }, { widthPx: W, heightPx: H }), null);
  assert.equal(planThumb(null, { widthPx: W, heightPx: H }), null);
  assert.equal(planThumb({ id: 'x', height_in: 0, geometry: wall.geometry }, { widthPx: W, heightPx: H }), null);
});
