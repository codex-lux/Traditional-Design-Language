/* EVERY PICK WRITES THE ADDRESS, AND NO SURFACE SHOWS A DEFAULT RECORD (WP-14.27, PRD §C.12).

   Tranche 1's rule (§E.4, §F.4) is that the URL decides what is read and memory only offers
   links. Four surfaces broke it: the Fault Corpus and the family tree fell back to a record typed
   into the component, the family tree's descent list and the Candidate Set's columns chose a
   record without writing it anywhere, and the Drawing Set held its sheet and face in `useState`
   while Export had no face at all. What each now decides is a pure module, driven here; what each
   surface DRAWS is the browser walk's (the "every pick" blocks), because a React component cannot
   be mounted under `node --test`. Where a component's source is read below it is the JOIN that is
   held -- that the surface calls the module, and does not keep a default beside it -- not a
   wording, and each such guard names the mutation it exists for.

   Every expectation is derived: the faces from `build/elevation.py`'s own tuple, the sheets from
   `drawingKinds.js`, the words' records from `glossary/*.json`. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import {
  FACES, FACE_TERM, ENTRANCE_FRONT_TERM, MODEL_SHEET, parseFace, parseSheet, sheetParam,
  drawingOpts, cadOpts, sheetFileName, faceChipWords, recordWord,
} from './surfaces/drawingFaces.js';
import { KINDS } from './surfaces/drawingKinds.js';
import { FAULT_GROUPS, faultGroups, groupRows, styleFaultIds } from './faults/groups.js';
import { nativityLine, setSize, NATIVITY_TERMS } from './candidateOrder.js';

const ROOT = new URL('../../../', import.meta.url);
const read = (p) => readFileSync(new URL(p, ROOT), 'utf8');
const live = (s) => s.replace(/\/\*[\s\S]*?\*\//g, '').replace(/(^|[\s;,{}()])\/\/[^\n]*/g, '$1');
const RECORDS = new Map(readdirSync(new URL('glossary/', ROOT)).filter((f) => f.endsWith('.json')).sort()
  .map((f) => JSON.parse(read('glossary/' + f))).map((r) => [r.id, r]));

// ---------------------------------------------------------------- the sheet and the face

test('the faces are the elevation record\'s own four, in its order, each worded by a record', () => {
  const tuple = /^FACES\s*=\s*\(([^)]*)\)/m.exec(read('build/elevation.py'));
  assert.ok(tuple, 'build/elevation.py states its FACES tuple');
  const want = tuple[1].split(',').map((x) => x.trim().replace(/^["']|["']$/g, '')).filter(Boolean);
  assert.deepEqual(FACES.map((f) => f.id), want);
  for (const id of [FACE_TERM, ENTRANCE_FRONT_TERM, ...FACES.map((f) => f.term)]) {
    assert.ok(RECORDS.has(id), `no glossary record ${id}`);
  }
  assert.equal(new Set(FACES.map((f) => f.term)).size, FACES.length, 'one record per face');
});

test('an address holds a face or none, and a sheet or the model -- never a guess', () => {
  for (const f of FACES) assert.equal(parseFace(f.id), f.id);
  for (const bad of [null, undefined, '', 'south', 's', 'NE', 'X', 7]) assert.equal(parseFace(bad), null);
  for (const k of KINDS) assert.equal(parseSheet(k.id), k.id);
  assert.equal(parseSheet(MODEL_SHEET), MODEL_SHEET);
  for (const bad of [null, undefined, '', 'Elevation', 'axon', 3]) assert.equal(parseSheet(bad), MODEL_SHEET);
  // a sheet written to the address reads back as itself; the model is the bare address
  for (const k of [MODEL_SHEET, ...KINDS.map((x) => x.id)]) assert.equal(parseSheet(sheetParam(k)), k);
  assert.equal(sheetParam(MODEL_SHEET), null);
});

test('a face is sent with an elevation and with nothing else, on both routes', () => {
  for (const f of FACES) {
    assert.deepEqual(drawingOpts('elevation', f.id), { face: f.id });
    assert.deepEqual(cadOpts('dxf', 'elevation', f.id), { kind: 'elevation', face: f.id });
  }
  // no face chosen is the server's own default, the entrance front: nothing is written
  assert.deepEqual(drawingOpts('elevation', null), {});
  assert.deepEqual(cadOpts('dxf', 'elevation', null), { kind: 'elevation' });
  for (const k of KINDS.filter((x) => x.id !== 'elevation')) {
    assert.deepEqual(drawingOpts(k.id, 'N'), {}, `${k.id} takes no face`);
    assert.deepEqual(cadOpts('dxf', k.id, 'N'), { kind: k.id }, `${k.id} dxf takes no face`);
  }
  assert.deepEqual(cadOpts('ifc', undefined, 'N'), {}, 'the model is the whole house, not a sheet');
  assert.deepEqual(drawingOpts('elevation', 'south'), {}, 'an unreadable face is not sent');
});

test('the four elevations of one house save as four files', () => {
  const names = FACES.map((f) => sheetFileName('p', 'elevation', f.id));
  assert.equal(new Set(names).size, FACES.length);
  assert.equal(sheetFileName('p', 'section', 'N'), sheetFileName('p', 'section', null));
});

test('a face chip is its record\'s word, and the entrance front\'s beside the front', () => {
  const word = (id) => `<${id}>`;
  const [front, other] = FACES;
  assert.equal(faceChipWords(word, other.id, front.id, ' · '), `<${other.term}>`);
  assert.equal(faceChipWords(word, front.id, front.id, ' · '), `<${front.term}> · <${ENTRANCE_FRONT_TERM}>`);
  assert.equal(faceChipWords(word, front.id, null, ' · '), `<${front.term}>`, 'no front stated, none claimed');
  // the reader of a word has the glossary's three states and invents none
  assert.equal(recordWord({ status: 'loading', lookup: null })(front.term), '…');
  assert.match(recordWord({ status: 'failed', lookup: null })(front.term), new RegExp(front.term));
  const lookup = { term: (id) => (RECORDS.has(id) ? RECORDS.get(id) : { missing: id }) };
  assert.equal(recordWord({ status: 'ready', lookup })(front.term), RECORDS.get(front.term).term);
});

test('the Drawing Set and Export read the sheet and face from the address and send them', () => {
  /* The join. Mutations this bites: `sheet`/`face` back to `useState` (the spec lines go), the
     face dropped from either request (the `drawingOpts`/`cadOpts` calls go), and a second
     spelling of which face is sent (the old inline `kind === 'elevation' && face` returns). */
  const ds = live(read('workbench/app/src/surfaces/DrawingSet.jsx'));
  assert.match(ds, /sheet:\s*\{\s*widens:\s*true\s*\},\s*face:\s*\{\s*widens:\s*true\s*\}/);
  assert.match(ds, /const kind = parseSheet\(F\.values\.sheet\)/);
  assert.match(ds, /const face = parseFace\(F\.values\.face\)/);
  assert.doesNotMatch(ds, /useState\(\s*'model'\s*\)/, 'the sheet is not component state');
  assert.match(ds, /api\.drawing\(kind, plan, drawingOpts\(kind, face\)\)/);
  assert.doesNotMatch(ds, /kind === 'elevation' && face \?/, 'one spelling of what is sent');
  const ex = live(read('workbench/app/src/surfaces/ExportDetails.jsx'));
  assert.match(ex, /const face = parseFace\(F\.values\.face\)/);
  assert.match(ex, /api\.drawing\(kind, plan, drawingOpts\(kind, face\)\)/);
  assert.match(ex, /api\.exportCad\(fmt, plan, cadOpts\(fmt, kind, face\)\)/);
  for (const [name, src] of [['DrawingSet.jsx', ds], ['ExportDetails.jsx', ex]]) {
    assert.doesNotMatch(src, /label:\s*'(south|north|east|west)'/, `${name} words a face itself`);
    assert.doesNotMatch(src, /'\s*·\s*the entrance front'/, `${name} words the entrance front itself`);
  }
});

// ---------------------------------------------------------------- no default record

test('a bare Fault Corpus and a bare family tree name no record', () => {
  /* The mutation this exists for: restoring `DEFAULT_FAULT` or `DEFAULT_TAXON` -- or any literal
     after the `||` -- in the initial state or the reset. The walk holds what the page then shows. */
  const fc = live(read('workbench/app/src/surfaces/FaultCorpus.jsx'));
  const ph = live(read('workbench/app/src/surfaces/Phylogeny.jsx'));
  for (const [name, src, key] of [['FaultCorpus.jsx', fc, 'fault'], ['Phylogeny.jsx', ph, 'style']]) {
    const falls = [...src.matchAll(new RegExp(`selection\\?\\.${key}\\s*\\|\\|\\s*([^)\\s;]+)`, 'g'))].map((m) => m[1]);
    assert.ok(falls.length >= 2, `${name} reads its selection in the initial state and the reset`);
    assert.deepEqual([...new Set(falls)], ['null'], `${name} falls back to ${falls.join(', ')}`);
    assert.doesNotMatch(src, /DEFAULT_(FAULT|TAXON)/);
    assert.match(src, /<NoRecordChosen surface=/, `${name} says no record is chosen`);
  }
  assert.ok(RECORDS.has('no-record-chosen'));
});

test('a descent in the family tree is a pick, and writes the address', () => {
  const ph = live(read('workbench/app/src/surfaces/Phylogeny.jsx'));
  const at = ph.indexOf('data-descent={e.from}');
  assert.ok(at > 0, 'the descent buttons carry their target');
  const handler = /onClick=\{\(\) => \{([^\n]*)\}\}/.exec(ph.slice(at, at + 240));
  assert.ok(handler, 'a descent button has a click handler');
  assert.match(handler[1], /setSelection\s*&&\s*setSelection\(\{\s*style:\s*e\.from\s*\}\)/);
});

test('a hollow hearth on the map is picked across its whole disc, not only on its stroke', () => {
  // SVG's default `pointer-events` is `visiblePainted`, and a country-precision mark is drawn
  // `fill="none"`: a click in its middle fell through to the coastline and panned the map. The
  // walk measures the pick; this holds the one attribute that makes the disc the target.
  const mv = live(read('workbench/app/src/surfaces/phylo/MapView.jsx'));
  const at = mv.indexOf('fill={coarse ? \'none\' : hue}');
  assert.ok(at > 0, 'the hearth circle is drawn hollow where the precision is a country');
  const circle = mv.lastIndexOf('<circle', at);
  assert.match(mv.slice(circle, at), /pointerEvents="visible"/);
});

// ---------------------------------------------------------------- faults for one style

test('the three groups are the dossier\'s, each headed by its record', () => {
  assert.deepEqual(FAULT_GROUPS.map((g) => g.id), ['here', 'lineage', 'universal']);
  for (const g of FAULT_GROUPS) assert.ok(RECORDS.has(g.term), `no glossary record ${g.term}`);
  assert.equal(new Set(FAULT_GROUPS.map((g) => g.term)).size, FAULT_GROUPS.length);
});

test('the universal group is the style\'s list less the two named, and is held to the served count', () => {
  const partition = { verdict_here: ['a'], lineage: ['b', 'c'], universal_count: 2, matches: 5 };
  const g = faultGroups(partition, ['a', 'b', 'c', 'd', 'e']);
  assert.equal(g.state, 'ready');
  assert.deepEqual([g.here, g.lineage, g.universal], [['a'], ['b', 'c'], ['d', 'e']]);
  assert.deepEqual([...styleFaultIds(g)].sort(), ['a', 'b', 'c', 'd', 'e']);
  // a list and a partition that disagree are not grouped -- the heading would stop being true
  assert.equal(faultGroups({ ...partition, universal_count: 3 }, ['a', 'b', 'c', 'd', 'e']).state, 'unjudged');
  assert.equal(faultGroups({ ...partition, matches: 6 }, ['a', 'b', 'c', 'd', 'e']).state, 'unjudged');
  assert.equal(faultGroups({ ...partition, verdict_here: ['z'], matches: 4, universal_count: 2 },
    ['b', 'c', 'd', 'e']).state, 'unjudged', 'a named fault the list does not hold');
  assert.equal(faultGroups(null, ['a']).state, 'unjudged');
  assert.equal(faultGroups(partition, null).state, 'unjudged');
  assert.equal(styleFaultIds(faultGroups(null, [])), null, 'nothing unjudged narrows the list');
});

test('rows keep the list\'s order under each group, and an emptied group is omitted', () => {
  const g = faultGroups({ verdict_here: ['a'], lineage: ['b'], universal_count: 2, matches: 4 },
    ['a', 'b', 'c', 'd']);
  const list = ['d', 'b', 'c'].map((id) => ({ id }));   // filtered: `a` hidden, order the page's
  const rows = groupRows(list, g);
  assert.deepEqual(rows.map((r) => [r.id, r.rows.map((x) => x.id)]), [['lineage', ['b']], ['universal', ['d', 'c']]]);
  assert.deepEqual(rows.map((r) => r.term), ['fault-group-lineage', 'fault-group-universal']);
  assert.equal(groupRows(list, { state: 'unjudged' }), null);
});

test('the Fault Corpus groups by the served partition and derives none', () => {
  const fc = live(read('workbench/app/src/surfaces/FaultCorpus.jsx'));
  assert.match(fc, /api\.styleDossier\(styleInView\)/);
  assert.match(fc, /faultGroups\(d && d\.faults,/);
  assert.match(fc, /<Term id=\{g\.term\} \/>/);
  assert.doesNotMatch(fc, /applies_to|severity_by_style|inverted_by/, 'the partition is the server\'s rule');
});

// ---------------------------------------------------------------- the candidate set

test('the strip counts the set asked for, and names the one the brief\'s parti appended', () => {
  const cands = [{ parti: 'own' }, { parti: 'named', parti_name: 'Named' }];
  const appended = { candidates: cands, named_parti: { parti: 'named', returned: true, appended: true } };
  assert.deepEqual(setSize(appended, 1), { own: 1, asked: 1, appended: { parti: 'named', name: 'Named', index: 1 } });
  // returned by the ranking itself: counted in the set, not appended
  const ranked = { candidates: cands, named_parti: { parti: 'named', returned: true, appended: false } };
  assert.deepEqual(setSize(ranked, 2), { own: 2, asked: 2, appended: null });
  // not returned at all, or nothing named: the set is what came back
  assert.deepEqual(setSize({ candidates: cands, named_parti: { parti: 'x', returned: false } }, 4),
    { own: 2, asked: 4, appended: null });
  assert.deepEqual(setSize({ candidates: cands }, 4), { own: 2, asked: 4, appended: null });
  assert.deepEqual(setSize(null, 4), { own: 0, asked: 4, appended: null });
  // never "returned 2 of 1": the set's own count cannot pass what was asked when one was appended
  assert.ok(setSize(appended, 1).own <= 1);
});

test('a lineage column reads as lineage, and nothing is worded before an unserved nativity', () => {
  const why = (first) => [first, 'four-over-four is a canonical massing for the style'];
  const lin = nativityLine({ nativity: 'lineage', why: why('native to an ancestor or relative of the style') });
  assert.equal(lin.term, NATIVITY_TERMS.lineage);
  assert.doesNotMatch(lin.prose, /NOT native/);
  const bor = nativityLine({ nativity: 'borrowed',
    why: why('NOT native to this style — the composer is borrowing a diagram') });
  assert.equal(bor.term, NATIVITY_TERMS.borrowed);
  assert.match(bor.prose, /^the composer is borrowing a diagram/, 'the record says borrowed; the clause is not doubled');
  const nat = nativityLine({ nativity: 'native', why: why('native to tidewater-georgian') });
  assert.equal(nat.term, NATIVITY_TERMS.native);
  const none = nativityLine({ nativity: null, why: why('NOT native to this style — the composer is borrowing a diagram') });
  assert.equal(none.term, null);
  assert.match(none.prose, /^NOT native to this style/, 'unserved: the composer\'s own sentence, whole');
  for (const id of Object.values(NATIVITY_TERMS)) assert.ok(RECORDS.has(id));
});

test('the column words its nativity from the record and the picked column is the address\'s', () => {
  /* Mutations: the typed "NOT native to this style" back in the column, or the column's pick back
     in `useState` (`setSel`), or the click no longer writing the numeric `candidate` key. */
  const col = live(read('workbench/app/src/components/CandidateColumn.jsx'));
  assert.doesNotMatch(col, /"NOT native to this style"/);
  assert.match(col, /nativityLine\(c\)/);
  assert.match(col, /React\.createElement\(Term, \{\s*id: line\.term\s*\}\)/);
  const cs = live(read('workbench/app/src/surfaces/CandidateSet.jsx'));
  assert.doesNotMatch(cs, /setSel\b/, 'the pick is not component state');
  assert.match(cs, /const sel = selection\?\.candidate != null \? 'c' \+ selection\.candidate : null/);
  assert.match(cs, /setSelection\(\{ candidate: c\.n \}\)/);
  assert.match(cs, /const size = setSize\(result, askedFor\)/);
  assert.doesNotMatch(cs, /returned \{cands\.length\}/, 'the strip counts the set, not every column');
});
