/* THE GLOSSARY READER AND THE SEVEN BOUND FIELDS (WP-14.6).

   `glossary/lookup.js` is driven here with payloads built to `GET /api/glossary`'s contract (PRD
   §C.1), because the server half (WP-14.3) and the records (WP-14.1, WP-14.2) land in other lanes:
   the same reason `refusal.test.mjs` drove its leaf with hand-built bodies before its server slice
   existed. The payload's bound records are made FROM THE SCHEMAS — every value of every enum
   `glossary/fields.js` points at — so the test is about the fields the corpus really has, and a
   pointer that stopped resolving would fail here rather than in a popover.

   Where the records and the glossary schema DO exist on the tree, the last two tests read them and
   hold `FIELDS` to them; where they do not, those tests SKIP by name, which is not a pass. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { indexTerms, isMissing } from './glossary/lookup.js';
import { FIELDS } from './glossary/fields.js';

const ROOT = new URL('../../../', import.meta.url);
const readJSON = (rel) => JSON.parse(readFileSync(new URL(rel, ROOT), 'utf8'));

function resolvePointer(doc, pointer) {
  let node = doc;
  for (const raw of pointer.replace(/^\//, '').split('/')) {
    const part = raw.replace(/~1/g, '/').replace(/~0/g, '~');
    if (!node || typeof node !== 'object' || !(part in node)) return undefined;
    node = node[part];
  }
  return node;
}

const enumOf = (f) => resolvePointer(readJSON(FIELDS[f].schema), FIELDS[f].pointer)?.enum;

/* The server's by_field rule: every bound value maps to the record binding it. */
function byFieldOf(records) {
  const out = Object.fromEntries(Object.keys(FIELDS).map((k) => [k, {}]));
  for (const r of records) for (const b of r.binds || []) out[b.field][b.value] = r.id;
  return out;
}

function schemaPayload() {
  const terms = [];
  for (const [f, spec] of Object.entries(FIELDS)) {
    enumOf(f).forEach((v, order) => terms.push({
      id: `${spec.family}-${v.replace(/_/g, '-')}`, term: v, family: spec.family, order,
      definition: 'x', kind: 'editorial', basis: 'x',
      binds: [{ field: f, schema: spec.schema, pointer: spec.pointer, value: v }],
    }));
  }
  // two unbound records that collide on their word, as a homonym pair does (PRD §B.6)
  terms.push({ id: 'fixture-homonym-left', term: 'homonym', family: 'rank', sense: 'a',
    confusable_with: ['fixture-homonym-right', 'no-such-record'] });
  terms.push({ id: 'fixture-homonym-right', term: 'homonym', family: 'binding', sense: 'b',
    confusable_with: ['fixture-homonym-left'] });
  return { version: '0.1.0+0123456789abcdef', count: terms.length, terms, by_field: byFieldOf(terms) };
}

test('each of the seven fields points at a real enum in the schema file it names', () => {
  assert.equal(Object.keys(FIELDS).length, 7);
  assert.ok(Object.isFrozen(FIELDS));
  for (const [f, spec] of Object.entries(FIELDS)) {
    assert.ok(existsSync(new URL(spec.schema, ROOT)), `${f}: ${spec.schema} must exist`);
    const e = enumOf(f);
    assert.ok(Array.isArray(e) && e.length > 0, `${f}: ${spec.pointer} must resolve to an enum`);
    assert.ok(typeof spec.family === 'string' && spec.family.length > 0);
  }
  // two fields sharing a family would make a family's records ambiguous about which enum they bind
  const fams = Object.values(FIELDS).map((s) => s.family);
  assert.equal(new Set(fams).size, fams.length);
});

test('every bound enum value resolves through by_field to its record', () => {
  const lk = indexTerms(schemaPayload());
  let n = 0;
  for (const f of Object.keys(FIELDS)) {
    for (const v of enumOf(f)) {
      const r = lk.termFor(f, v);
      assert.ok(!isMissing(r), `${f}=${v} did not resolve`);
      assert.equal(r.binds[0].value, v);
      assert.equal(r.binds[0].field, f);
      n += 1;
    }
  }
  assert.ok(n >= 7);
});

test('a missing record is an answer that names what is missing, never undefined and never a gloss', () => {
  const lk = indexTerms(schemaPayload());
  assert.deepEqual({ ...lk.term('no-such-term') }, { missing: 'no-such-term' });
  assert.ok(isMissing(lk.term('no-such-term')));
  assert.deepEqual({ ...lk.termFor('kit.binding', 'nope') }, { missing: 'kit.binding:nope' });
  assert.deepEqual({ ...lk.termFor('not.a.field', 'open') }, { missing: 'not.a.field:open' });
  // a value the map carries whose record is absent is missing under the RECORD's id
  const p = schemaPayload();
  p.by_field['kit.binding'].open = 'binding-open-unwritten';
  assert.deepEqual({ ...indexTerms(p).termFor('kit.binding', 'open') }, { missing: 'binding-open-unwritten' });
  // and a found record is the record itself, not a copy with anything added
  const rec = p.terms.find((t) => t.id === 'rank-style');
  assert.equal(indexTerms(p).term('rank-style'), rec);
  assert.ok(!isMissing(rec) && !isMissing(null) && !isMissing('x'));
});

test('an absent or broken payload gives a lookup where everything is missing, not an error', () => {
  for (const junk of [null, undefined, {}, { terms: 'x' }, { terms: [null, 3, { term: 'no id' }] }]) {
    const lk = indexTerms(junk);
    assert.ok(Object.isFrozen(lk));
    assert.equal(lk.count, 0);
    assert.equal(lk.version, null);
    assert.ok(isMissing(lk.term('about-tdl')));
    assert.ok(isMissing(lk.termFor('style.rank', 'style')));
    assert.deepEqual(lk.confusables('about-tdl'), []);
    assert.deepEqual(lk.family('rank'), []);
  }
});

test('confusables come back in declared order, a missing one in its place rather than dropped', () => {
  const lk = indexTerms(schemaPayload());
  const c = lk.confusables('fixture-homonym-left');
  assert.equal(c.length, 2);
  assert.equal(c[0].id, 'fixture-homonym-right');
  assert.deepEqual({ ...c[1] }, { missing: 'no-such-record' });
  assert.deepEqual(lk.confusables('fixture-homonym-right').map((r) => r.id), ['fixture-homonym-left']);
  assert.deepEqual(lk.confusables('rank-style'), [], 'a record declaring none has none');
});

test('a family is its records in the payload’s order, and a repeated id is one term', () => {
  const p = schemaPayload();
  const lk = indexTerms(p);
  const want = p.terms.filter((t) => t.family === 'rank').map((t) => t.id);
  assert.deepEqual(lk.family('rank').map((t) => t.id), want);
  assert.ok(want.includes('fixture-homonym-left'), 'the premise: an unbound record joins its family too');
  const dup = { ...p, terms: [...p.terms, { id: 'rank-style', term: 'impostor', family: 'rank' }] };
  const lk2 = indexTerms(dup);
  assert.equal(lk2.term('rank-style').term, 'style', 'the first record under an id is the term');
  assert.equal(lk2.family('rank').filter((t) => t.id === 'rank-style').length, 1);
  assert.equal(lk2.version, p.version);
  assert.equal(lk2.count, lk.count);
});

test('the reader writes no word of its own', () => {
  /* PRD §I.2: "no strings of its own". Every string literal left in the live code must be a key or
     a separator, never a phrase — a phrase here would be the app writing what a record says. */
  const src = readFileSync(new URL('glossary/lookup.js', import.meta.url), 'utf8')
    .replace(/\/\*[\s\S]*?\*\//g, '').replace(/^\s*\/\/.*$/gm, '');
  const literals = [...src.matchAll(/'([^'\n]*)'|`([^`\n]*)`/g)].map((m) => m[1] ?? m[2]);
  assert.ok(literals.length > 0, 'the premise: the scan found the literals the file does carry');
  const phrases = literals.filter((s) => /[A-Za-z]{2,}\s+[A-Za-z]{2,}/.test(s));
  assert.deepEqual(phrases, [], 'lookup.js may carry no words for a reader');
});

const GLOSSARY_DIR = new URL('glossary/', ROOT);
const GLOSSARY_SCHEMA = new URL('schema/glossary-term.schema.json', ROOT);

test('FIELDS names exactly the fields the glossary schema lets a record bind', (t) => {
  if (!existsSync(GLOSSARY_SCHEMA)) {
    t.skip('COULD NOT EVALUATE: schema/glossary-term.schema.json is not on this tree (WP-14.1)');
    return;
  }
  const schema = JSON.parse(readFileSync(GLOSSARY_SCHEMA, 'utf8'));
  const allowed = schema.$defs.bind.properties.field.enum;
  assert.deepEqual([...allowed].sort(), Object.keys(FIELDS).sort());
});

test('every bind on a real glossary record names its field’s own schema and pointer', (t) => {
  const files = existsSync(GLOSSARY_DIR)
    ? readdirSync(GLOSSARY_DIR).filter((f) => f.endsWith('.json')).sort() : [];
  if (!files.length) {
    t.skip('COULD NOT EVALUATE: no glossary/*.json records on this tree (WP-14.1, WP-14.2)');
    return;
  }
  const recs = files.map((f) => JSON.parse(readFileSync(new URL(f, GLOSSARY_DIR), 'utf8')));
  const lk = indexTerms({ terms: recs, by_field: byFieldOf(recs) });
  for (const r of recs) {
    for (const b of r.binds || []) {
      assert.ok(b.field in FIELDS, `${r.id} binds ${b.field}, which FIELDS does not name`);
      assert.equal(b.schema, FIELDS[b.field].schema, r.id);
      assert.equal(b.pointer, FIELDS[b.field].pointer, r.id);
      assert.equal(lk.termFor(b.field, b.value).id, r.id);
    }
  }
});
