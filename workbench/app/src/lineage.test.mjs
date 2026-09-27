/* WHAT AN EDGE CARRIES, HELD TO THE CORPUS AND TO THE SERVER'S ONE SPELLING (WP-14.11, PRD §H.6, §I.13).

   `lineage/carry.js` answers "what does this edge hand down?" from the edge's served
   `inherits_kit` and `slots`, and `components/EdgeGlyph.jsx` draws the answer's glossary record.
   Every expectation here is DERIVED — from `styles/*.json` read with `node:fs`, projected to the
   edge `/api/phylogeny` serves by the rule `workbench/server/corpus.py` states (read from its
   source, not retyped), and from `glossary/*.json` — never a count typed in. The finding this
   package exists for (a table of types captioned every kit-carrying `hybridizes_with` edge "carries
   nothing") is re-derived rather than quoted: the edges the old table and the flag disagree on are
   computed, and asserted to be exactly those co-parents.

   And because EdgeGlyph, Phylogeny.jsx and MapView.jsx import React and cannot run here, the rule
   that they read the flag and carry no table of their own is held by reading their source — the
   weaker form, used only for what a file SAYS; what the drawing DOES is the browser walk's
   lineage block. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import {
  FILING, CARRY_TERM_IDS, namedSlotsOf, carriesKit, carryTermOf, strokeOf, glyphEdge,
  filingEdgeOf, groupByCarry,
} from './lineage/carry.js';

const ROOT = new URL('../../../', import.meta.url);
const read = (p) => readFileSync(new URL(p, ROOT), 'utf8');
const live = (s) => s.replace(/\/\*[\s\S]*?\*\//g, '').replace(/(^|[\s;,{}()])\/\/[^\n]*/g, '$1');

const NODES = readdirSync(new URL('styles/', ROOT)).filter((f) => f.endsWith('.json')).sort()
  .map((f) => JSON.parse(read(`styles/${f}`)));

/* The server's rule, read off `corpus.phylogeny`'s own source: the tuple of cascade-carrying types
   and the line that serves the flag. If either changes shape this fails here, rather than the
   test quietly modelling a server that no longer exists. */
const CORPUS = read('workbench/server/corpus.py');
const CASCADE_EDGES = (() => {
  const m = CORPUS.match(/^CASCADE_EDGES\s*=\s*\(([^)]*)\)/m);
  assert.ok(m, 'corpus.py states CASCADE_EDGES');
  return [...m[1].matchAll(/"([a-z_]+)"/g)].map((x) => x[1]);
})();

function servedEdges() {
  assert.match(CORPUS, /"inherits_kit":\s*bool\(e\.get\("inherits_kit"\)\)\s*or\s*e\["type"\]\s*in\s*CASCADE_EDGES/,
    'the premise: corpus.phylogeny serves inherits_kit as the record flag OR a cascade type');
  assert.match(CORPUS, /"slots":\s*e\.get\("slots"\)/, 'the premise: corpus.phylogeny serves each edge’s slots');
  const out = [];
  for (const n of NODES) {
    for (const e of n.lineage || []) {
      out.push({
        from: n.id, to: e.target, type: e.type, weight: e.weight ?? null,
        inherits_kit: Boolean(e.inherits_kit) || CASCADE_EDGES.includes(e.type),
        slots: e.slots ?? null,
      });
    }
  }
  return out;
}
const SERVED = servedEdges();
const RAW = NODES.flatMap((n) => (n.lineage || []).map((e) => ({ ...e, from: n.id })));

function records() {
  return readdirSync(new URL('glossary/', ROOT)).filter((f) => f.endsWith('.json')).sort()
    .map((f) => JSON.parse(read(`glossary/${f}`)));
}

test('the premise: the corpus has lineage edges, filed nodes, and both kinds of co-parent', () => {
  assert.ok(SERVED.length > 0 && SERVED.length === RAW.length);
  assert.ok(NODES.filter((n) => n.member_of).length > 0);
  const hy = SERVED.filter((e) => e.type === 'hybridizes_with');
  assert.ok(hy.some((e) => e.inherits_kit) && hy.some((e) => !e.inherits_kit),
    'a co-parent may carry the kit or not: the fact is per edge, which is why a type table cannot hold it');
});

test('THE FINDING, RE-DERIVED: the old type table and the served flag disagree on exactly the kit-carrying co-parents', () => {
  const TYPE_TABLE = new Set(['descends_from', 'regional_of']);       // EdgeGlyph.jsx:6-9 before WP-14.11
  const wrong = SERVED.filter((e) => TYPE_TABLE.has(e.type) !== e.inherits_kit);
  const kitCoParents = SERVED.filter((e) => e.type === 'hybridizes_with' && e.inherits_kit === true);
  assert.ok(kitCoParents.length > 0, 'the premise: some co-parent carries the kit');
  assert.deepEqual(wrong.map((e) => `${e.from}>${e.to}`).sort(), kitCoParents.map((e) => `${e.from}>${e.to}`).sort(),
    'every edge the type table got wrong is a kit-carrying hybridizes_with edge, and every such edge it got wrong');
  // …and every one of them now reads as carrying, the whole kit or the slots it names
  for (const e of kitCoParents) {
    const want = namedSlotsOf(e).length ? 'carries-named-slots' : 'carries-the-kit';
    assert.equal(carryTermOf(e), want, `${e.from} hybridizes_with ${e.to}`);
  }
  assert.ok(kitCoParents.some((e) => carryTermOf(e) === 'carries-named-slots'),
    'the premise: the corpus carries a scoped co-parent, so the named-slots branch is exercised');
  assert.ok(kitCoParents.some((e) => carryTermOf(e) === 'carries-the-kit'));
});

test('every served edge resolves to the carry its flag and slot list state, and no edge to member-of', () => {
  const tally = Object.fromEntries(CARRY_TERM_IDS.map((id) => [id, 0]));
  for (const e of SERVED) {
    const got = carryTermOf(e);
    tally[got] += 1;
    if (!e.inherits_kit) assert.equal(got, 'carries-nothing', `${e.from} ${e.type} ${e.to}`);
    else assert.equal(got, Array.isArray(e.slots) && e.slots.length ? 'carries-named-slots' : 'carries-the-kit');
    assert.equal(strokeOf(e), e.inherits_kit ? 'carries' : 'claims');
  }
  assert.equal(tally['member-of'], 0, 'a lineage edge is never filing');
  assert.equal(tally['carries-nothing'], SERVED.filter((e) => !e.inherits_kit).length);
  assert.ok(tally['carries-nothing'] > 0 && tally['carries-the-kit'] > 0 && tally['carries-named-slots'] > 0);
});

test('every member_of filing resolves to member-of, and is drawn as filing rather than as a claim', () => {
  const filed = NODES.filter((n) => typeof n.member_of === 'string' && n.member_of);
  const edges = filed.map((n) => filingEdgeOf({ id: n.id, member_of: n.member_of }));
  assert.equal(edges.length, filed.length);
  assert.ok(edges.length > 0);
  for (const e of edges) {
    assert.equal(e.type, FILING);
    assert.equal(carryTermOf(e), 'member-of', `${e.from} filed under ${e.target}`);
    assert.equal(strokeOf(e), 'filing');
    assert.equal(carriesKit(e), false, 'filing carries no lineage flag; what it carries is the member-of record’s to say');
  }
  // …even where a payload set the flag on a filing edge, filing is filing
  assert.equal(carryTermOf({ type: FILING, inherits_kit: true }), 'member-of');
  // a taxon filed under nothing (a tradition) has no filing edge
  const roots = NODES.filter((n) => !n.member_of);
  assert.ok(roots.length > 0);
  for (const n of roots) assert.equal(filingEdgeOf({ id: n.id, member_of: n.member_of }), null);
});

test('the style record’s own lineage item and the served edge give one carry word on every edge', () => {
  /* StyleRecord passes the record's lineage item (its raw `inherits_kit`); the Phylogeny passes the
     served edge (`raw OR a cascade type`). `build/build.py`'s cascade walks the RAW flag alone. The
     three agree only while no descends_from / regional_of edge omits the flag — true of this corpus,
     and asserted, so the day one does the two surfaces cannot silently print different words. */
  assert.match(read('build/build.py'), /if not e\.get\("inherits_kit"\): continue/,
    'the premise: the builder’s cascade walks the raw flag');
  assert.equal(RAW.length, SERVED.length);
  const byKey = new Map(SERVED.map((e) => [`${e.from}|${e.type}|${e.to}`, e]));
  const disagree = RAW.filter((r) => carryTermOf(r) !== carryTermOf(byKey.get(`${r.from}|${r.type}|${r.target}`)));
  assert.deepEqual(disagree.map((r) => `${r.from} ${r.type} ${r.target}`), [],
    'a lineage item whose raw flag differs from the served rule: the Style Record and the Phylogeny would disagree');
});

test('carryTermOf is strict: only the boolean true carries, and only a list of names is a slot list', () => {
  for (const v of ['true', 1, {}, [], null, undefined, false, 'yes']) {
    assert.equal(carryTermOf({ type: 'hybridizes_with', inherits_kit: v }), 'carries-nothing', String(v));
    assert.equal(carriesKit({ type: 'descends_from', inherits_kit: v }), false,
      'the type is not read: a descent edge the server did not flag is not drawn as carrying');
  }
  assert.equal(carryTermOf({ type: 'references', inherits_kit: true }), 'carries-the-kit',
    'the type is not read in the other direction either');
  assert.equal(carryTermOf({ type: 'x', inherits_kit: true, slots: ['porch_type'] }), 'carries-named-slots');
  for (const s of [[], null, undefined, 'porch_type', [''], ['a', 3], {}]) {
    assert.equal(carryTermOf({ type: 'x', inherits_kit: true, slots: s }), 'carries-the-kit', JSON.stringify(s));
  }
  assert.deepEqual(namedSlotsOf({ slots: ['a', 'b'] }), ['a', 'b']);
  for (const junk of [null, undefined, 7, 'descends_from']) assert.equal(carryTermOf(junk), 'carries-nothing');
  assert.equal(strokeOf(null), 'claims');
});

test('glyphEdge carries the served facts under the glyph’s names, and a grouping follows the flag', () => {
  const g = glyphEdge({ from: 'a', to: 'b', type: 'hybridizes_with', inherits_kit: true, slots: ['s'], weight: 1 });
  assert.deepEqual(g, { type: 'hybridizes_with', inherits_kit: true, slots: ['s'], from: 'a', target: 'b', note: undefined });
  assert.equal(glyphEdge({ type: 't', target: 'c', note: 'n' }).target, 'c', 'a style record’s item keeps its target');
  assert.equal(glyphEdge(null), null);
  // every style's own edges, grouped: the groups come in CARRY_TERM_IDS order, each non-empty,
  // each edge in the group its carry word names, and none dropped
  let seenMixed = 0;
  for (const n of NODES) {
    const mine = SERVED.filter((e) => e.from === n.id).map(glyphEdge);
    const groups = groupByCarry(mine);
    assert.equal(groups.reduce((k, gr) => k + gr.edges.length, 0), mine.length, n.id);
    const order = groups.map((gr) => CARRY_TERM_IDS.indexOf(gr.carry));
    assert.deepEqual(order, [...order].sort((a, b) => a - b), n.id);
    for (const gr of groups) {
      assert.ok(gr.edges.length > 0);
      for (const e of gr.edges) assert.equal(carryTermOf(e), gr.carry);
    }
    if (mine.some((e) => e.type === 'hybridizes_with' && e.inherits_kit)
      && groups.every((gr) => gr.carry !== 'carries-nothing' || !gr.edges.some((e) => e.type === 'hybridizes_with' && e.inherits_kit))) {
      seenMixed += 1;
    }
  }
  assert.ok(seenMixed > 0, 'the premise: some style has a kit-carrying co-parent, and it is never grouped with the claims');
  assert.deepEqual(groupByCarry([null, 'x', { type: 'references' }]).map((gr) => gr.carry), ['carries-nothing']);
});

test('every carry word and every lineage verb a glyph asks for is a glossary record', () => {
  const recs = records();
  const ids = new Set(recs.map((r) => r.id));
  for (const id of CARRY_TERM_IDS) assert.ok(ids.has(id), `no glossary record ${id}`);
  const byField = {};
  for (const r of recs) for (const b of r.binds || []) (byField[b.field] ||= {})[b.value] = r.id;
  for (const type of new Set(SERVED.map((e) => e.type))) {
    const id = (byField['lineage.type'] || {})[type];
    assert.ok(typeof id === 'string' && ids.has(id), `lineage.type ${type} has no record: its verb would read "no entry"`);
  }
  // and no record binds member_of as a lineage type: filing's word is the member-of record, asked by id
  assert.equal((byField['lineage.type'] || {})[FILING], undefined);
});

/* ---- the source guards: what the three React files SAY ---- */

test('EdgeGlyph carries no table and no caption of its own, and asks carry.js and the glossary', () => {
  const src = live(read('workbench/app/src/components/EdgeGlyph.jsx'));
  assert.doesNotMatch(src, /\bCARRIES\b/, 'a type table of what carries');
  assert.doesNotMatch(src, /\bVERB\b/, 'a table of verbs: the verb is termFor(lineage.type)');
  assert.doesNotMatch(src, /descends_from|regional_of|hybridizes_with|references|reacts_against|revives/,
    'a lineage type named in the glyph is a type being read');
  // no caption written in the app: no string literal of two or more words in the live source
  const lits = [...src.matchAll(/'((?:\\.|[^'\\\n])*)'|"((?:\\.|[^"\\\n])*)"|>([^<>{}\n]*[A-Za-z][^<>{}\n]*)</g)]
    .map((m) => (m[1] ?? m[2] ?? m[3] ?? '').trim())
    .filter((s) => /[A-Za-z]{2,}\s+[A-Za-z]{2,}/.test(s) && !/^var\(|^\d|px|solid|dashed|dotted|inline-flex/.test(s));
  assert.deepEqual(lits, [], 'an app-written caption: every word here is a glossary record’s');
  assert.match(src, /from '\.\.\/lineage\/carry\.js'/);
  assert.match(src, /carryTermOf\(/);
  assert.match(src, /<Term field="lineage\.type" value=\{e\.type\} \/>/, 'the verb is the lineage.type record');
  for (const id of CARRY_TERM_IDS) assert.match(src, new RegExp(`<Term id="${id}" />`), `the ${id} word`);
  assert.doesNotMatch(src, /--ink-4/, 'no readable text in --ink-4');
});

test('the Phylogeny and its map read the flag per edge and hold no table of types', () => {
  for (const f of ['surfaces/Phylogeny.jsx', 'surfaces/phylo/MapView.jsx']) {
    const src = live(read(`workbench/app/src/${f}`));
    assert.doesNotMatch(src, /\bCARRIES\b/, `${f}: a type table of what carries`);
    assert.doesNotMatch(src, /\[\s*e\.type\s*\]/, `${f}: a lookup keyed on an edge's type`);
    assert.doesNotMatch(src, /descends_from|regional_of/, `${f}: a cascade type named in the surface`);
    assert.match(src, /\bcarriesKit\(e\)/, `${f}: reads the served flag`);
  }
  const ph = live(read('workbench/app/src/surfaces/Phylogeny.jsx'));
  assert.match(ph, /groupByCarry\(/, 'the panel groups by carry');
  assert.doesNotMatch(ph, /claims only|carries the cascade|None recorded/, 'the retired app-written headings');
  assert.doesNotMatch(ph, /tone="quiet"/, 'a readable eyebrow in --ink-4');
});
