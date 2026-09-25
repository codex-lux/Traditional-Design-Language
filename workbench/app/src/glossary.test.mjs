/* EVERY WORD THE APP ASKS THE GLOSSARY FOR IS A WORD THE GLOSSARY HOLDS (WP-14.8, PRD §I.1, §I.2, §K).

   `components/Term.jsx` renders `noEntry(id)` — "no entry: <id>", visibly — for a record the
   glossary does not hold. That is the honest thing for a Term to do and it is never what shipped
   code should reach, so this file reads every literal glossary id in the app's shipped source and
   holds it to `glossary/*.json`, read here with `node:fs` alone (no fetch, no server, no bundle):

     <Term id="…" />                      <Term field="…" value="…" />
     useTermDescription('…')              <PageHead termId="…" />
     lookup.term('…')                     lookup.termFor('…', '…')
     termView(…, { id: '…' })             describeTerm(…, '…')
     wordOf(…, '…')                       wordForCite(…, 'term:…')
     api.glossaryTerm('…')                (the one-record route; the Gate reads `about-tdl`
                                           through it signed out — WP-14.14)

   A literal inside a comment is not shipped code and is not held (Term.jsx's own docstring
   carries examples). An id reached through a VARIABLE is not a literal and cannot be checked
   here; where it comes from a record (a confusable, a `see` cite) the record's own checker holds
   it (`build/check_glossary.py`). The scanner is driven on a fixture carrying every shape, so a
   shape it stops recognising fails here rather than going quiet.

   And `glossary/fields.js`'s `FIELDS` is held to the records BOTH WAYS (PRD §I.2): every field it
   names is bound by at least one record, with that field's own schema and pointer; and every
   field a record binds is one it names, at a value that field's enum really has. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, statSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { FIELDS } from './glossary/fields.js';

const SRC = fileURLToPath(new URL('./', import.meta.url));
const ROOT = new URL('../../../', import.meta.url);
const GLOSSARY = new URL('glossary/', ROOT);

function records() {
  const files = existsSync(GLOSSARY)
    ? readdirSync(GLOSSARY).filter((f) => f.endsWith('.json')).sort() : [];
  return files.map((f) => JSON.parse(readFileSync(new URL(f, GLOSSARY), 'utf8')));
}

/* The server's by_field rule (PRD §C.1), for the literal field+value pairs. */
function byField(recs) {
  const out = {};
  for (const r of recs) for (const b of r.binds || []) (out[b.field] ||= {})[b.value] = r.id;
  return out;
}

// Block comments and line comments, leading or trailing (a `//` after `:` is a URL and is kept).
const stripComments = (s) => s.replace(/\/\*[\s\S]*?\*\//g, (m) => m.replace(/[^\n]/g, ' '))
  .replace(/(^|[\s;,{}()])\/\/[^\n]*/g, '$1');

/* A string literal written as an attribute value: "x", 'x', {'x'}, {"x"} or {`x`} with no
   interpolation. Anything else (a variable, an expression) is not a literal. */
const LIT = String.raw`(?:"([^"\n]*)"|'([^'\n]*)'|\{\s*(?:"([^"\n]*)"|'([^'\n]*)'|\x60([^\x60$\n]*)\x60)\s*\})`;
const litOf = (m, from) => m.slice(from, from + 5).find((x) => x !== undefined);

function attr(tag, name) {
  const m = tag.match(new RegExp(String.raw`\b${name}=` + LIT));
  return m ? litOf(m, 1) : undefined;
}

/* source text → [{ id } | { field, value }], each with the shape that found it. */
function scan(source) {
  const src = stripComments(source);
  const hits = [];
  for (const m of src.matchAll(/<Term\b([^>]*)>/g)) {
    const tag = m[1];
    const id = attr(tag, 'id');
    const field = attr(tag, 'field');
    const value = attr(tag, 'value');
    if (id !== undefined) hits.push({ shape: '<Term id>', id });
    else if (field !== undefined && value !== undefined) hits.push({ shape: '<Term field value>', field, value });
  }
  for (const m of src.matchAll(/<PageHead\b([^>]*)>/g)) {
    const id = attr(m[1], 'termId');
    if (id !== undefined) hits.push({ shape: '<PageHead termId>', id });
  }
  const q = String.raw`(?:'([^'\n]*)'|"([^"\n]*)"|\x60([^\x60$\n]*)\x60)`;
  const one = (re, shape) => {
    for (const m of src.matchAll(re)) hits.push({ shape, id: m[1] ?? m[2] ?? m[3] });
  };
  one(new RegExp(String.raw`\buseTermDescription\(\s*` + q, 'g'), 'useTermDescription');
  one(new RegExp(String.raw`\.term\(\s*` + q + String.raw`\s*\)`, 'g'), '.term');
  one(new RegExp(String.raw`\bdescribeTerm\([^,()]*,\s*` + q, 'g'), 'describeTerm');
  one(new RegExp(String.raw`\btermView\([^,()]*,\s*\{\s*id:\s*` + q, 'g'), 'termView');
  one(new RegExp(String.raw`\bwordOf\([^,()]*,\s*` + q, 'g'), 'wordOf');
  one(new RegExp(String.raw`\bglossaryTerm\(\s*` + q + String.raw`\s*\)`, 'g'), 'glossaryTerm');
  // A literal CITE handed to wordForCite: only its `term:` form names a glossary record.
  for (const m of src.matchAll(new RegExp(String.raw`\bwordForCite\([^,()]*,\s*` + q, 'g'))) {
    const cite = m[1] ?? m[2] ?? m[3];
    if (cite.startsWith('term:')) hits.push({ shape: 'wordForCite', id: cite.slice('term:'.length) });
  }
  for (const m of src.matchAll(new RegExp(String.raw`\.termFor\(\s*` + q + String.raw`\s*,\s*` + q + String.raw`\s*\)`, 'g'))) {
    hits.push({ shape: '.termFor', field: m[1] ?? m[2] ?? m[3], value: m[4] ?? m[5] ?? m[6] });
  }
  return hits;
}

function shippedFiles(dir = SRC, out = []) {
  for (const f of readdirSync(dir).sort()) {
    const p = join(dir, f);
    if (statSync(p).isDirectory()) shippedFiles(p, out);
    else if (/\.(jsx|js)$/.test(f)) out.push(p);          // `*.test.mjs` is not shipped
  }
  return out;
}

test('the scanner recognises every shape a literal glossary id is written in, and ignores comments', () => {
  const fixture = [
    '<Term id="a-dq" />', "<Term id='a-sq'/>", "<Term id={'a-brace'}>word</Term>",
    '<Term id={`a-tpl`} />', '<Term field="kit.binding" value="open" />',
    "<Term value={'forbidden'} field='kit.binding'>x</Term>",
    "const d = useTermDescription('a-desc');", '<PageHead termId="a-head" />',
    "lookup.term('a-lookup')", "glossary.lookup.termFor('fault.severity', 'fatal')",
    "termView(glossary, { id: 'a-view' })", "describeTerm(g, 'a-describe')",
    "wordOf(lookup, 'a-word')", "wordForCite(lookup, 'term:a-cite')",
    "api.glossaryTerm('a-route')",
    "wordForCite(lookup, 'style:not-a-term')",                // another kind: not a glossary id
    "<Term id={c.id} />", "useTermDescription(someId)",       // variables: not literals
    '/* <Term id="in-a-block-comment" /> */', "// <Term id='in-a-line-comment' />",
    "x = 1; // lookup.term('trailing-comment')",
  ].join('\n');
  const got = scan(fixture).map((h) => h.id ?? `${h.field}=${h.value}`);
  assert.deepEqual(got.sort(), [
    'a-brace', 'a-cite', 'a-describe', 'a-desc', 'a-dq', 'a-head', 'a-lookup', 'a-route', 'a-sq',
    'a-tpl', 'a-view', 'a-word',
    'fault.severity=fatal', 'kit.binding=forbidden', 'kit.binding=open',
  ].sort());
});

test('every literal glossary id in the shipped app resolves to a record', (t) => {
  const recs = records();
  if (!recs.length) {
    t.skip('COULD NOT EVALUATE: no glossary/*.json records on this tree (WP-14.1, WP-14.2)');
    return;
  }
  const ids = new Set(recs.map((r) => r.id));
  const bf = byField(recs);
  const hits = [];
  for (const p of shippedFiles()) {
    for (const h of scan(readFileSync(p, 'utf8'))) hits.push({ ...h, file: p.slice(SRC.length) });
  }
  /* The premise: the scan reached a literal the app really ships. Without it a scanner that
     matched nothing would pass every tree. It read Glossary.jsx's own page head until WP-14.13
     moved every page head into the shell, where the id is `headTermFor(place)` — a variable,
     held to its records by `navModel.test.mjs` instead — so it reads the assistant's name now,
     the one literal the shell's own files ask the glossary for by id. */
  assert.ok(hits.some((h) => h.file === 'rail/RailHost.jsx' && h.id === 'assistant'
    && h.shape === 'termView'), 'the premise: RailHost’s assistant record was found');
  const unresolved = hits.filter((h) => (h.id !== undefined
    ? !ids.has(h.id)
    : !(bf[h.field] && typeof bf[h.field][h.value] === 'string' && ids.has(bf[h.field][h.value]))));
  assert.deepEqual(unresolved.map((h) => `${h.file}: ${h.shape} ${h.id ?? `${h.field}=${h.value}`}`), [],
    'each of these would render "no entry: …" on screen; write the record or fix the id');
});

/* ---- FIELDS, both ways ---- */

function resolvePointer(doc, pointer) {
  let node = doc;
  for (const raw of pointer.replace(/^\//, '').split('/')) {
    const part = raw.replace(/~1/g, '/').replace(/~0/g, '~');
    if (!node || typeof node !== 'object' || !(part in node)) return undefined;
    node = node[part];
  }
  return node;
}

test('every field FIELDS names is bound by at least one record, with that field’s own schema and pointer', (t) => {
  const recs = records();
  if (!recs.length) { t.skip('COULD NOT EVALUATE: no glossary/*.json records on this tree'); return; }
  const unbound = Object.entries(FIELDS).filter(([f, spec]) => !recs.some((r) => (r.binds || [])
    .some((b) => b.field === f && b.schema === spec.schema && b.pointer === spec.pointer)));
  assert.deepEqual(unbound.map(([f]) => f), [],
    'a field no record binds is a field whose every value would render "no entry"');
});

test('every field a record binds is one FIELDS names, at a value its enum really has', (t) => {
  const recs = records();
  if (!recs.length) { t.skip('COULD NOT EVALUATE: no glossary/*.json records on this tree'); return; }
  let n = 0;
  for (const r of recs) {
    for (const b of r.binds || []) {
      n += 1;
      assert.ok(b.field in FIELDS, `${r.id} binds ${b.field}, which FIELDS does not name`);
      const schema = JSON.parse(readFileSync(new URL(FIELDS[b.field].schema, ROOT), 'utf8'));
      const e = resolvePointer(schema, FIELDS[b.field].pointer)?.enum;
      assert.ok(Array.isArray(e) && e.includes(b.value), `${r.id}: ${b.field} has no value ${b.value}`);
    }
  }
  assert.ok(n >= Object.keys(FIELDS).length, 'the premise: the records carry binds to check');
});
