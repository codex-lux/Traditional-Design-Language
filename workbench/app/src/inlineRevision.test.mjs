/* WP-13.9's own adversarial audit: the three client-side defects it found, each pinned.

   All three were invisible to every suite that existed, and for one reason worth naming: every
   assertion about the inline rounds was about the RESPONSE -- the report, the counts, the
   fields -- and these are properties of what the surface DOES with it. `planDoc` is pure and is
   driven directly; the surface's two are source properties, which is the weaker form and says
   so, because the behaviour needs a browser and the walk is where that is asserted. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const live = (rel) => readFileSync(resolve(HERE, rel), 'utf8');

/* ---------------------------------------------------------------- the document guard */
test('the inline revision is applied only to the document it was computed from', () => {
  /* `seq` asks "has another REQUEST started?" and `planDoc.get() !== submitted` asks "has the
     DOCUMENT changed?". The audit found two live paths where the answers differ, because
     `evalRef` advances only inside `runEvaluate` and `runEvaluate` runs only after the 400 ms
     debounce: an edit in the last 400 ms of a 36 s revise, and a sustained wall drag, whose
     every step clears the pending timer so `runEvaluate` is never called at all. Either would
     replace the reader's edit with a record computed before it, silently. */
  const src = live('surfaces/PlanWorkbench.jsx');
  assert.match(src, /const submitted = p;/,
    'runEvaluate must hold the document it was given');
  assert.match(src, /if \(planDoc\.get\(\) !== submitted\) \{[\s\S]{0,400}?setReviseError\([\s\S]{0,200}?\} else \{[\s\S]{0,300}?planDoc\.load\(res\.revised_plan\)/,
    'the inline load must be gated on the document and must SAY so when it is not applied');
  // and the job path's own guard is still there: one defect, two paths, and fixing one of
  // them is how the other comes to look fixed
  assert.match(src, /if \(planDoc\.get\(\) !== submitted\) \{[\s\S]*?planDoc\.load\(revised\)/,
    'the job path keeps its own guard');
});

test('the loop’s two failure states reach the screen and not only the response', () => {
  /* `revision_error` and `revision_skipped` were produced by the server and asserted by the
     server's tests, and no surface read either -- so a reader who pressed re-solve, waited,
     and got a sheet with no panel saw exactly the screen that caused this package. */
  const src = live('surfaces/PlanWorkbench.jsx');
  assert.match(src, /lastEval\?\.revision_error/, 'a loop that raised must be stated');
  assert.match(src, /lastEval\?\.revision_skipped/, 'a loop that was declined must be stated');
});

/* ---------------------------------------------------------------- what is persisted */
const planDocSrc = live('state/planDoc.js');

test('the loop’s report is kept out of localStorage, and the record is not', () => {
  /* Measured by the audit on `tidewater-georgian-careful` after the bench's default two
     rounds: the declared record is 13,892 bytes and `revision_report` is 146,733 more.
     `emit()` stringifies synchronously on the main thread on EVERY mutation, and a mutation is
     every step of a wall drag -- the one interaction whose own comment says it "cannot afford
     the wait". */
  assert.match(planDocSrc, /function persisted\(p\)/, 'there must be one reader of what is persisted');
  assert.match(planDocSrc, /revision_report: _drop/, 'and it must drop the report');
  assert.match(planDocSrc, /setItem\(KEY, JSON\.stringify\(persisted\(plan\)\)\)/,
    'emit must persist through it');
  // the RECORD still goes to storage: dropping the whole document would lose a refresh
  assert.doesNotMatch(planDocSrc, /setItem\(KEY, JSON\.stringify\(\{\}\)\)/);
});

test('load caps its undo stack as update always has', () => {
  /* `update` has capped at 100 since it was written. `load` was the once-an-hour act of
     opening a record and had no cap -- and then the bench's solve began loading the loop's
     revised record on every explicit solve, so the stack grew one full record per re-solve
     press, unbounded. */
  const body = planDocSrc.slice(planDocSrc.indexOf('  load(next) {'),
    planDocSrc.indexOf('  update(fn) {'));
  assert.match(body, /undoStack\.length > 100/, 'load must cap the stack it now writes to');
});

test('the persisted copy is a COPY: dropping the report does not mutate the document', () => {
  /* The rest-spread is what makes this true, and a `delete p.revision_report` would pass every
     assertion above while taking the panel off the live record on the first drag step. Driven
     rather than read, because that is the difference the source cannot show. */
  const fn = new Function('p', planDocSrc.slice(planDocSrc.indexOf('function persisted(p)'),
    planDocSrc.indexOf('function emit()')).replace('function persisted(p) {', '').replace(/\}\s*$/, '')
    .replace(/^\s*\/\*[\s\S]*?\*\/\s*/, ''));
  const doc = { id: 'x', revision_report: { summary: { rounds: 2 } } };
  const out = fn(doc);
  assert.equal(out.revision_report, undefined, 'the persisted copy carries no report');
  assert.ok(doc.revision_report, 'and the live document still does');
  assert.equal(out.id, 'x', 'and keeps the record');
});
