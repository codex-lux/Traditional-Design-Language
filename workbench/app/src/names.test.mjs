/* NAMES OFF THE INDEX, AND THE ID WHERE THERE IS NONE (WP-14.6).

   The entries below are built from the corpus's own files in the shape
   `workbench/server/corpus.py::search_index` serves — `{cite, kind, id, name}` per style, slot and
   fault — so every expected name is the record's own `name` and none is written here. The subject
   has two halves and the second is the one that matters: a cite the index holds comes back with
   the record's name, and a cite it does not hold comes back as ITSELF, marked unresolved, and never
   with a name that looks right. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { nameFor, nameIndex } from './names/names.js';

const ROOT = new URL('../../../', import.meta.url);
const readJSON = (rel) => JSON.parse(readFileSync(new URL(rel, ROOT), 'utf8'));
const jsonIn = (dir) => readdirSync(new URL(dir, ROOT)).filter((f) => f.endsWith('.json')).sort()
  .map((f) => readJSON(dir + f));

const STYLES = jsonIn('styles/');
const FAULTS = jsonIn('faults/');
const SLOTS = readJSON('elements/slots.json').groups.flatMap((g) => g.slots);

const ENTRIES = [
  ...STYLES.map((s) => ({ cite: 'style:' + s.id, kind: 'style', id: s.id, name: s.name })),
  ...SLOTS.map((s) => ({ cite: 'slot:' + s.id, kind: 'slot', id: s.id, name: s.name })),
  ...FAULTS.map((f) => ({ cite: 'fault:' + f.id, kind: 'fault', id: f.id, name: f.name })),
];
const ALL_NAMES = new Set(ENTRIES.map((e) => e.name));

test('the premise: the corpus files carry the records the index is built from', () => {
  assert.ok(STYLES.length > 0 && SLOTS.length > 0 && FAULTS.length > 0);
  assert.ok(ENTRIES.every((e) => typeof e.name === 'string' && e.name.length > 0));
});

test('every record in the index is named by its own name, with its id as the note', () => {
  for (const e of ENTRIES) {
    const r = nameFor(e.cite, ENTRIES);
    assert.equal(r.resolved, true, e.cite);
    assert.equal(r.name, e.name, e.cite);
    assert.equal(r.note, e.id, e.cite);
    assert.equal(r.via, 'exact');
  }
});

test('a constraint takes its style’s name and keeps its own id as the note, for every constraint', () => {
  let n = 0;
  for (const s of STYLES) {
    for (const c of s.constraints || []) {
      const r = nameFor('constraint:' + c.id, ENTRIES);
      assert.equal(r.resolved, true, c.id);
      assert.equal(r.name, s.name, `${c.id} belongs to ${s.id}`);
      assert.equal(r.note, c.id, 'the note is the constraint, so it is never called by its style’s name alone');
      assert.equal(r.via, 'style-of-constraint');
      n += 1;
    }
  }
  assert.ok(n > 0, 'the premise: the corpus carries constraints');
});

test('an unknown cite comes back bare and unresolved, and never with a name that looks right', () => {
  const style = STYLES[0];
  const unknown = [
    'style:' + style.id + '-that-does-not-exist',   // a plausible id, one edit from a real one
    'fault:no-such-fault',
    'pack:trim-classical',                          // a real pack, absent from THIS index
    'constraint:no-such-style.c01',
    'constraint:nodot',                             // names no style at all
    'kit:no-such-style#cornice',
    'style:no-such-style#lineage',
    'candidate:3',
  ];
  for (const cite of unknown) {
    const r = nameFor(cite, ENTRIES);
    assert.equal(r.resolved, false, cite);
    assert.equal(r.name, cite, `${cite} must come back as itself`);
    assert.equal(r.note, null);
    assert.ok(!ALL_NAMES.has(r.name), `${cite} was given a record's name`);
  }
});

test('what the grammar cannot read is returned as it was handed in, unresolved', () => {
  for (const junk of ['not a cite', '', 'Style:craftsman', 'style:', ':craftsman', 'style:a b']) {
    const r = nameFor(junk, ENTRIES);
    assert.deepEqual(r, { name: junk, note: null, resolved: false, via: null }, JSON.stringify(junk));
  }
  assert.equal(nameFor(null, ENTRIES).name, '');
  assert.equal(nameFor(undefined, ENTRIES).resolved, false);
  // and an index that is not there resolves nothing rather than failing
  assert.equal(nameFor('style:' + STYLES[0].id, null).resolved, false);
  assert.equal(nameFor('style:' + STYLES[0].id, {}).resolved, false);
});

test('a kit cite and a section fragment take the record’s name and keep the fragment in the note', () => {
  const s = STYLES.find((x) => x.rank === 'style');
  const slot = SLOTS[0];
  const kit = nameFor(`kit:${s.id}#${slot.id}`, ENTRIES);
  assert.deepEqual([kit.name, kit.note, kit.resolved, kit.via],
    [s.name, `${s.id}#${slot.id}`, true, 'style-of-kit']);
  const bareKit = nameFor(`kit:${s.id}`, ENTRIES);
  assert.deepEqual([bareKit.name, bareKit.note], [s.name, s.id]);
  const section = nameFor(`style:${s.id}#lineage`, ENTRIES);
  assert.deepEqual([section.name, section.note, section.via], [s.name, `${s.id}#lineage`, 'record-of-fragment']);
});

test('the three forms an index arrives in give the same answer', () => {
  const payload = { count: ENTRIES.length, entries: ENTRIES };
  const index = nameIndex(ENTRIES);
  assert.ok(index instanceof Map && index.size === ENTRIES.length);
  assert.equal(nameIndex(ENTRIES), index, 'an array is indexed once and the index reused');
  for (const cite of ['style:' + STYLES[1].id, 'fault:' + FAULTS[0].id, 'constraint:x.c01']) {
    const a = nameFor(cite, ENTRIES);
    assert.deepEqual(nameFor(cite, payload), a, cite);
    assert.deepEqual(nameFor(cite, index), a, cite);
  }
  // an entry with no usable name is not a name
  const nameless = [{ cite: 'style:ghost', kind: 'style', id: 'ghost', name: '  ' }];
  assert.equal(nameFor('style:ghost', nameless).resolved, false);
});

test('the grammar is read through parseCite and spelled nowhere in this module', () => {
  /* PRD §J.4: no regex in names.js — a fourth spelling of the grammar is how it came to disagree
     with itself about a dot. Comments are stripped first, because they may quote a pattern. */
  const src = readFileSync(new URL('names/names.js', import.meta.url), 'utf8')
    .replace(/\/\*[\s\S]*?\*\//g, '').replace(/^\s*\/\/.*$/gm, '');
  assert.match(src, /import \{ parseCite \} from '\.\.\/citations\.js'/);
  assert.match(src, /parseCite\(/);
  assert.doesNotMatch(src, /RegExp|\.exec\(|\.test\(|\.match\(|ID_CHARS|FRAG_CHARS/,
    'names.js must not carry a pattern of its own');
});
