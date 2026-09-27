/* The Styles index as an outline, held to the corpus it indexes (WP-14.6, PRD §I.7).

   Every expectation here is read off `styles/*.json`, `mcp_server/core.py`, `build/render_html.py`,
   the tracked plate `dist/taxonomy.html` or `surfaces/Phylogeny.jsx` — never a count typed in —
   and the orphan branch, which the shipped corpus never reaches, is DRIVEN on hand-built taxa with
   its premise asserted, because a guard that runs only where the defect cannot occur guards nothing. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { styleTree, traditionOrderOf } from './styles/styleTree.js';
import {
  TRADITION_HUES, taxonOf, floruitOf, compareTaxa, memberChain, traditionOf, membersOf,
} from './styles/taxa.js';

const ROOT = new URL('../../../', import.meta.url);
const read = (p) => readFileSync(new URL(p, ROOT), 'utf8');

// every style record, projected to the taxon `/api/phylogeny` serves (`corpus.phylogeny`'s fields)
const RECORDS = readdirSync(new URL('styles/', ROOT)).filter((f) => f.endsWith('.json')).sort()
  .map((f) => JSON.parse(read(`styles/${f}`)));
const TAXA = RECORDS.map((n) => ({
  id: n.id, name: n.name, rank: n.rank, member_of: n.member_of ?? null,
  floruit_start: n.period ? n.period.floruit_start : null,
}));
const BY_ID = new Map(TAXA.map((t) => [t.id, t]));

// the tradition order as the server states it (`/api/overview`'s cards), read from its source
function listAfter(src, anchor) {
  const at = src.indexOf(anchor);
  assert.ok(at >= 0, `${anchor} not found`);
  const open = src.indexOf('[', at + anchor.length), close = src.indexOf(']', open);
  return [...src.slice(open, close).matchAll(/"([a-z0-9-]+)"/g)].map((m) => m[1]);
}
const ORDER = listAfter(read('mcp_server/core.py'), '"traditions": [_style_card(S[i]) for i in');
const PLATE_ORDER = listAfter(read('build/render_html.py'), 'TRAD_ORDER =');

// the ancestors of a record, walked off the RAW `member_of` fields rather than through taxa.js
function rawChain(id) {
  const out = [];
  let n = BY_ID.get(id);
  while (n && n.member_of) { out.unshift(n.member_of); n = BY_ID.get(n.member_of); }
  return out;
}

test('the server and the static plate state one tradition order, and it names every tradition', () => {
  assert.deepEqual(ORDER, PLATE_ORDER);
  const traditions = TAXA.filter((t) => t.rank === 'tradition').map((t) => t.id).sort();
  assert.ok(traditions.length > 0);
  assert.deepEqual([...ORDER].sort(), traditions);
  // and the reader of the payload returns it in the order it was served
  const overview = { traditions: ORDER.map((id) => ({ id, name: BY_ID.get(id).name })) };
  assert.deepEqual(traditionOrderOf(overview), ORDER);
  assert.deepEqual(traditionOrderOf(null), []);
  assert.deepEqual(traditionOrderOf({ traditions: ['a', { id: 'b' }, 7, null] }), ['a', 'b']);
});

test('every node in styles/ is a row exactly once, and none is an orphan', () => {
  const { rows, orphans } = styleTree(TAXA, ORDER);
  assert.deepEqual(orphans, []);
  const ids = rows.map((r) => r.id);
  assert.equal(new Set(ids).size, ids.length, 'a node appears twice');
  assert.deepEqual([...ids].sort(), TAXA.map((t) => t.id).sort());
});

test("each row's nearest shallower row is its member_of parent, and its depth is its filing depth", () => {
  const { rows } = styleTree(TAXA, ORDER);
  let deep = 0;
  rows.forEach((r, i) => {
    const t = BY_ID.get(r.id);
    assert.equal(r.rank, t.rank);
    assert.equal(r.depth, rawChain(r.id).length, `${r.id} drawn at the wrong depth`);
    if (r.depth === 0) { assert.equal(t.member_of, null, `${r.id} is a root and is filed`); return; }
    let j = i - 1;
    while (j >= 0 && rows[j].depth >= r.depth) j -= 1;
    assert.ok(j >= 0, `${r.id} has no shallower row above it`);
    assert.equal(rows[j].depth, r.depth - 1, `${r.id} skips a level`);
    assert.equal(rows[j].id, t.member_of, `${r.id} sits under ${rows[j].id}, filed under ${t.member_of}`);
    deep = Math.max(deep, r.depth);
  });
  assert.ok(deep >= 2, 'the corpus no longer files anything below a family; the check is vacuous');
});

test('siblings run by floruit and then by id; the roots run in the served order', () => {
  const { rows } = styleTree(TAXA, ORDER);
  assert.deepEqual(rows.filter((r) => r.depth === 0).map((r) => r.id), ORDER);
  const kids = new Map();
  for (const r of rows) {
    const p = BY_ID.get(r.id).member_of;
    if (!p) continue;
    if (!kids.has(p)) kids.set(p, []);
    kids.get(p).push(BY_ID.get(r.id));
  }
  let ties = 0;
  for (const [p, ks] of kids) {
    for (let i = 1; i < ks.length; i += 1) {
      const a = ks[i - 1], b = ks[i];
      assert.ok(a.floruit_start <= b.floruit_start, `under ${p}: ${a.id} (${a.floruit_start}) before ${b.id} (${b.floruit_start})`);
      if (a.floruit_start === b.floruit_start) { ties += 1; assert.ok(a.id < b.id, `under ${p}: tie ${a.id}/${b.id} not by id`); }
    }
  }
  assert.ok(ties > 0, 'no two siblings share a floruit, so the id tie-break is not exercised by the corpus');
});

test('the port agrees with the static plate row for row, which recurses three levels by hand', () => {
  const line = read('dist/taxonomy.html').split('\n').find((l) => l.startsWith('const DATA = {'));
  assert.ok(line, 'dist/taxonomy.html carries no DATA line');
  const DATA = JSON.parse(line.slice('const DATA = '.length).replace(/;\s*$/, ''));
  assert.deepEqual(DATA.traditions, ORDER);
  assert.deepEqual(DATA.orphans, []);
  const { rows } = styleTree(TAXA, DATA.traditions);
  assert.deepEqual(rows.map((r) => r.id), DATA.rows.map((r) => r.id));
  const depthOf = { tradition: [0], family: [1], node: [2, 3] };
  DATA.rows.forEach((pr, i) => assert.ok(depthOf[pr.kind].includes(rows[i].depth), `${pr.id}: ${pr.kind} at ${rows[i].depth}`));
});

// ---------------------------------------------------------------------------- the orphans, driven
const T = (id, rank, member_of, floruit_start = 1700) => ({ id, rank, member_of, floruit_start });

test('a filing the walk cannot reach is LISTED as an orphan and never dropped', () => {
  const taxa = [
    T('t', 'tradition', null), T('f', 'family', 't'), T('s', 'style', 'f'),
    T('dangle', 'family', 'no-such-tradition'), T('dangle-child', 'style', 'dangle'),
    T('loop-a', 'family', 'loop-b'), T('loop-b', 'family', 'loop-a'),
    T('self', 'family', 'self'),
    T('unlisted', 'tradition', null), T('unlisted-kid', 'family', 'unlisted'),
  ];
  const { rows, orphans } = styleTree(taxa, ['t']);
  // the premise: the reachable half is walked, so what is missing is missing for the stated reason
  assert.deepEqual(rows.map((r) => r.id), ['t', 'f', 's']);
  assert.deepEqual(orphans, ['dangle', 'dangle-child', 'loop-a', 'loop-b', 'self', 'unlisted', 'unlisted-kid']);
  // and nothing is lost between the two lists
  assert.equal(rows.length + orphans.length, taxa.length);
});

test('a node named in the order that is itself filed is placed by its parent, never hoisted', () => {
  const taxa = [T('t', 'tradition', null), T('f', 'family', 't'), T('s', 'style', 'f')];
  const { rows } = styleTree(taxa, ['s', 't', 'f']);
  assert.deepEqual(rows, [{ id: 't', rank: 'tradition', depth: 0 }, { id: 'f', rank: 'family', depth: 1 }, { id: 's', rank: 'style', depth: 2 }]);
});

test('a reversed order reverses the roots; an undated sibling follows every dated one', () => {
  const taxa = [
    T('a', 'tradition', null), T('b', 'tradition', null),
    T('x', 'family', 'a', null), T('y', 'family', 'a', 1900), T('w', 'family', 'a', 1900), T('z', 'family', 'a', 1500),
  ];
  assert.deepEqual(styleTree(taxa, ['b', 'a']).rows.filter((r) => r.depth === 0).map((r) => r.id), ['b', 'a']);
  assert.deepEqual(styleTree(taxa, ['a', 'b']).rows.map((r) => r.id), ['a', 'z', 'w', 'y', 'x', 'b']);
  // a duplicate id is one row, and junk is not a row
  const dup = styleTree([...taxa, T('a', 'tradition', null, 1), null, { name: 'no id' }], ['a']);
  assert.equal(dup.rows.filter((r) => r.id === 'a').length, 1);
  assert.deepEqual(styleTree(null, null), { rows: [], orphans: [] });
});

// ------------------------------------------------------------------------------------- taxa.js
/* RE-CUT AT WP-14.11, NOT DELETED. Until then Phylogeny.jsx carried its own copy of the hues and
   this held the two copies equal; the surface IMPORTS the table now, so the property is that there
   is one table — the import is asserted, and so is the absence of any second table in the file
   (a local `TRADITION_HUES` or a literal tradition swatch map), because an import beside a copy
   that shadows it would pass an import-only check. */
test("TRADITION_HUES is one table: Phylogeny.jsx imports it from taxa.js, over exactly the corpus's traditions", () => {
  const src = read('workbench/app/src/surfaces/Phylogeny.jsx');
  const live = src.replace(/\/\*[\s\S]*?\*\//g, '').replace(/(^|[\s;,{}()])\/\/[^\n]*/g, '$1');
  assert.match(live, /import\s*\{[^}]*\bTRADITION_HUES\b[^}]*\}\s*from\s*'\.\.\/styles\/taxa\.js'/,
    'Phylogeny.jsx must take its tradition hues from styles/taxa.js');
  assert.doesNotMatch(live, /\b(?:const|let|var)\s+TRADITION_HUES\b/, 'a second table would shadow the import');
  for (const id of Object.keys(TRADITION_HUES)) {
    assert.doesNotMatch(live, new RegExp(`['"]${id}['"]\\s*:`), `Phylogeny.jsx keys a swatch by ${id} itself`);
  }
  assert.deepEqual(Object.keys(TRADITION_HUES).sort(), TAXA.filter((t) => t.rank === 'tradition').map((t) => t.id).sort());
  assert.ok(Object.isFrozen(TRADITION_HUES));
});

test('memberChain, traditionOf and membersOf agree with the raw filing on every node', () => {
  for (const t of TAXA) {
    const chain = rawChain(t.id);
    assert.deepEqual(memberChain(t.id, BY_ID), chain, t.id);
    assert.equal(traditionOf(t.id, BY_ID), chain.length ? chain[0] : t.id, t.id);
    const kids = membersOf(t.id, TAXA);
    assert.deepEqual(kids.map((k) => k.id).sort(), TAXA.filter((k) => k.member_of === t.id).map((k) => k.id).sort());
    for (let i = 1; i < kids.length; i += 1) assert.ok(kids[i - 1].floruit_start <= kids[i].floruit_start);
  }
  // a plain object and a Map answer alike, and an inherited key is not a taxon
  const obj = Object.fromEntries(TAXA.map((t) => [t.id, t]));
  const some = TAXA.find((t) => rawChain(t.id).length >= 2);
  assert.deepEqual(memberChain(some.id, obj), memberChain(some.id, BY_ID));
  assert.equal(taxonOf('constructor', obj), null);
  assert.equal(taxonOf(7, BY_ID), null);
});

test('a chain stops at a parent nobody holds, and a loop yields no chain and no tradition', () => {
  const m = new Map([['a', T('a', 'style', 'b')], ['b', T('b', 'family', 'a')], ['c', T('c', 'style', 'gone')]]);
  assert.deepEqual(memberChain('a', m), []);
  assert.equal(traditionOf('a', m), null);
  assert.deepEqual(memberChain('c', m), []);
  assert.equal(traditionOf('c', m), null);
  assert.equal(traditionOf('nope', m), null);
  const m2 = new Map([['t', T('t', 'tradition', null)], ['f', T('f', 'family', 't')], ['s', T('s', 'style', 'f')], ['v', T('v', 'variant', 's')]]);
  assert.deepEqual(memberChain('v', m2), ['t', 'f', 's']);
  assert.equal(traditionOf('v', m2), 't');
  // a chain whose root is not a tradition names no tradition rather than the root it reached
  const m3 = new Map([['f', T('f', 'family', null)], ['s', T('s', 'style', 'f')]]);
  assert.equal(traditionOf('s', m3), null);
});

test('floruit is one fact in either shape, and an undated taxon sorts last rather than first', () => {
  assert.equal(floruitOf({ floruit_start: 1720 }), 1720);
  assert.equal(floruitOf({ period: { floruit_start: -500 } }), -500);
  assert.equal(floruitOf({ floruit_start: null, period: { floruit_start: 1600 } }), 1600);
  assert.equal(floruitOf({ floruit_start: 'soon' }), null);
  assert.equal(floruitOf(null), null);
  const rec = RECORDS.find((n) => n.period && typeof n.period.floruit_start === 'number');
  assert.equal(floruitOf(rec), rec.period.floruit_start);
  assert.ok(compareTaxa({ id: 'b', floruit_start: 2000 }, { id: 'a', floruit_start: null }) < 0);
  assert.ok(compareTaxa({ id: 'a', floruit_start: null }, { id: 'b', floruit_start: 2000 }) > 0);
  assert.ok(compareTaxa({ id: 'a', floruit_start: 1 }, { id: 'b', floruit_start: 1 }) < 0);
  assert.equal(compareTaxa({ id: 'a', floruit_start: 1 }, { id: 'a', floruit_start: 1 }), 0);
});
