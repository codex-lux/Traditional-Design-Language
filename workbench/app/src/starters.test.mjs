/* THE STARTER QUESTIONS ARE THE RECORDS' OWN, VERBATIM (WP-14.22, PRD tranche 2 §C.8, §C.10).

   `rail/starters.js` returns a page's `surface-*` glossary record's `ask`. The guard reads every
   such record FROM DISK -- the files `build/check_glossary.py` holds to the schema -- builds the
   lookup the app builds (`glossary/lookup.js::indexTerms`), and requires each page's starters to
   be that record's questions exactly: the same strings, the same order, none added. A starter
   rewritten by one word in the app is the app writing copy, and this test is what refuses it.

   The other half is the states in which NOTHING is offered -- loading, failed, no record, a
   record with no `ask` -- because each of those is a page one round trip, one server fault or
   one authoring gap away from being offered a question about somewhere else. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { indexTerms } from './glossary/lookup.js';
import { startersFor, starterRecordId } from './rail/starters.js';

const GLOSSARY = new URL('../../../glossary/', import.meta.url);

function surfaceRecords() {
  return readdirSync(GLOSSARY)
    .filter((f) => f.startsWith('surface-') && f.endsWith('.json'))
    .sort()
    .map((f) => JSON.parse(readFileSync(new URL(f, GLOSSARY), 'utf8')));
}

const ready = (terms) => ({ status: 'ready', lookup: indexTerms({ terms }), error: null });

test('every page offers exactly its own record\'s questions, verbatim and in order', () => {
  const recs = surfaceRecords();
  const withAsk = recs.filter((r) => Array.isArray(r.surface?.ask) && r.surface.ask.length);
  // The premise: the records carry questions at all, or every assertion below is about nothing.
  assert.ok(withAsk.length > 0, 'no surface-* record on disk carries an `ask`');
  const g = ready(recs);
  for (const r of recs) {
    const surface = r.id.slice('surface-'.length);
    assert.equal(starterRecordId(surface), r.id, `${surface} is read from its own record`);
    assert.deepEqual(startersFor(g, surface), r.surface?.ask ?? [],
      `${r.id}: the pane must offer the record's questions exactly as written`);
  }
});

test('the questions are the record\'s own strings, not copies that happen to match', () => {
  const recs = surfaceRecords();
  const r = recs.find((x) => Array.isArray(x.surface?.ask) && x.surface.ask.length);
  const g = ready(recs);
  const got = startersFor(g, r.id.slice('surface-'.length));
  // Each word of each question, compared one by one, so a single changed word names itself.
  r.surface.ask.forEach((q, i) => {
    assert.deepEqual(got[i].split(/\s+/), q.split(/\s+/), `${r.id} ask[${i}]`);
  });
  assert.equal(got.length, r.surface.ask.length);
});

test('nothing is offered while the glossary loads, or where it failed', () => {
  assert.deepEqual(startersFor({ status: 'loading', lookup: null }, 'proportions'), []);
  assert.deepEqual(startersFor({ status: 'failed', lookup: null, error: 'x' }, 'proportions'), []);
  assert.deepEqual(startersFor(undefined, 'proportions'), []);
  // A lookup present under a status that is not `ready` is not read: useGlossary never hands
  // one out, and a reader that trusted it would offer questions on a half-answered glossary.
  const recs = surfaceRecords();
  const early = { status: 'loading', lookup: indexTerms({ terms: recs }) };
  assert.deepEqual(startersFor(early, 'proportions'), []);
});

test('a page with no record, or a record with no `ask`, offers nothing rather than another page\'s', () => {
  const recs = surfaceRecords();
  const g = ready(recs);
  assert.deepEqual(startersFor(g, 'no-such-surface'), []);
  assert.deepEqual(startersFor(g, ''), []);
  assert.deepEqual(startersFor(g, null), []);
  const bare = ready([{ id: 'surface-bare', term: 'Bare', family: 'surface',
    surface: { what: 'x' } }]);
  assert.deepEqual(startersFor(bare, 'bare'), []);
  // The drive for the branch above is real: the same record WITH an ask offers it.
  const asked = ready([{ id: 'surface-bare', term: 'Bare', family: 'surface',
    surface: { what: 'x', ask: ['Is this a question?'] } }]);
  assert.deepEqual(startersFor(asked, 'bare'), ['Is this a question?']);
});
