/* THE JOURNEY BAR'S DECISIONS, DRIVEN (WP-14.10, PRD §I.5).

   `components/JourneyBar.jsx` cannot be imported here -- it is JSX over React, and this suite
   runs with no npm install -- so what the bar DECIDES lives in `journey/bar.js`, pure, and is
   driven below state by state over `journeyState`'s own output. What the component does with
   each decision is held by reading its source, narrowly, and by the walk (`e2e/walk.mjs`), which
   reads the rendered bar against a live server.

   The subjects, each a way the bar could lie to a reader:
   - a refused house must never offer its drawings or its export as a link;
   - Next is a link only where the step in view can proceed, and otherwise says why;
   - a plan from an earlier compose must not link to the Candidate Set's CURRENT job;
   - the bar is on the six house surfaces and nowhere else, and never in full screen;
   - every word it draws is a glossary record's, and the ids it asks for exist. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { JOURNEY, ALTERNATE, JOURNEY_WORDS, journeyState } from './journey/journey.js';
import { STEP_TERMS, BAR_TERMS, showJourneyBar, barView } from './journey/bar.js';
import { SURFACE_PATHS, parseHash } from './router.js';

const ROOT = new URL('../../../', import.meta.url);
const read = (rel) => readFileSync(new URL(rel, import.meta.url), 'utf8');
const item = (v, id) => v.items.find((i) => i.id === id);

const BRIEF = { style: 'tidewater-georgian', target_area_sf: 3200 };
const PLAN = { id: 'p-1', name: 'The house', style: 'tidewater-georgian', levels: [] };
const check = { plan: PLAN.id, counts: { fatal: 1, serious: 2 }, constraint_summary: { unjudged: 3 } };
const REFUSAL = { kind: 'type-fact-downgraded', facts: ['stacks'], conflicts: [], lines: ['x'] };
const REFUSED = { check, placement_refused: REFUSAL };
const EVALUATED = { check, placement: { geometry_report: { refused: null } } };
const SKETCH = { check, placement: { geometry_report: { refused: null },
  sketch: { working: true, refused: null, reason: 'a wall drag' } } };
const RESULT = { brief: 'b', candidates: [{}, {}] };

const view = (session, plan, lastEval, surface, jobId = session.jobId || null) =>
  barView(journeyState({ session, plan, lastEval }), { surface, jobId });

test('the bar is on the six house surfaces, nowhere else, and never in full screen', () => {
  const house = [...JOURNEY.map((j) => j.surface), ...Object.keys(ALTERNATE)];
  assert.deepEqual(house.slice().sort(),
    ['brief', 'candidates', 'drawings', 'export', 'transcription', 'workbench']);
  for (const s of Object.keys(SURFACE_PATHS)) {
    assert.equal(showJourneyBar(s, null), house.includes(s), s);
    // full screen is the shell's `full`: the surface's own id when that surface has the window
    assert.equal(showJourneyBar(s, s), false, `${s} in full screen`);
  }
});

test('App mounts the bar once, above <main>, and only where showJourneyBar says', () => {
  /* LIVE CODE, NOT PROSE (WP-14.30). This read the raw file, so the first `<main` it found could
     be a COMMENT: WP-14.30's width effect names `<main>` in its comment above the JSX and turned
     this guard red on an edit that moved no element. A selector over the source text goes red on a
     rewording as readily as it goes blind on one; the element is what the rule is about. */
  const app = read('./App.jsx').replace(/\/\*[\s\S]*?\*\//g, '').replace(/(^|[^:])\/\/.*$/gm, '$1');
  const mounts = [...app.matchAll(/<JourneyBar\b/g)];
  assert.equal(mounts.length, 1, 'mounted once, by App');
  const at = mounts[0].index;
  assert.ok(at < app.indexOf('<main'), 'above <main>, so it is not part of any surface');
  assert.match(app.slice(at - 80, at), /showJourneyBar\(surface, full\)\s*&&\s*$/,
    'guarded by the one rule for where it is shown');
});

test('a step is named by its surface\'s own glossary record, and every id the bar asks for exists', (t) => {
  for (const j of JOURNEY) assert.ok(STEP_TERMS[j.id], `${j.id} has a record`);
  for (const id of Object.keys(ALTERNATE)) assert.ok(STEP_TERMS[id], `${id} has a record`);
  // each step's record is the record of the surface it stands on, not a word chosen for the bar
  for (const j of JOURNEY) {
    assert.equal(STEP_TERMS[j.id], `surface-${j.surface}`, `${j.id} is named by its surface's record`);
  }
  const dir = new URL('glossary/', ROOT);
  const ids = [...Object.values(STEP_TERMS), ...Object.values(BAR_TERMS)];
  const have = existsSync(dir) ? new Set(readdirSync(dir).map((f) => f.replace(/\.json$/, ''))) : new Set();
  if (!have.size) { t.skip('COULD NOT EVALUATE: no glossary/ on this tree'); return; }
  for (const id of ids) assert.ok(have.has(id), `glossary/${id}.json does not exist`);
});

test('a refused house shows its drawings and its export as blocked: refused, and neither is a link', () => {
  for (const lastEval of [REFUSED, { check, placement: { geometry_report: { refused: REFUSAL } } }]) {
    const v = view({ brief: BRIEF, result: RESULT }, PLAN, lastEval, 'workbench');
    for (const id of ['drawings', 'export']) {
      assert.equal(item(v, id).link, false, `${id} is not a link`);
      assert.equal(item(v, id).blocked, 'refused', `${id} says it is blocked because refused`);
      assert.equal(item(v, id).words, JOURNEY_WORDS[id].refused);
    }
    // the steps before the plan are places a reader can stand, refused or not
    for (const id of ['brief', 'candidates', 'plan']) assert.equal(item(v, id).link, true, id);
    // and the bench's Next says why it cannot go on, rather than offering the drawings
    assert.deepEqual([v.next.link, v.next.id, v.next.reason],
      [false, 'drawings', JOURNEY_WORDS.drawings.refused]);
  }
});

test('an evaluated house offers both, and a working sketch blocks the export alone', () => {
  const ok = view({ brief: BRIEF, result: RESULT }, PLAN, EVALUATED, 'workbench');
  assert.equal(item(ok, 'drawings').link, true);
  assert.equal(item(ok, 'export').link, true);
  assert.deepEqual([ok.next.link, ok.next.id, parseHash(ok.next.href).surface], [true, 'drawings', 'drawings']);

  const sk = view({ brief: BRIEF, result: RESULT }, PLAN, SKETCH, 'drawings');
  assert.equal(item(sk, 'drawings').link, true, 'a sketch does not block the drawings (PRD §G)');
  assert.equal(item(sk, 'export').link, false);
  assert.equal(item(sk, 'export').blocked, 'sketch');
  assert.deepEqual([sk.next.link, sk.next.reason], [false, JOURNEY_WORDS.export.sketch]);
});

test('with no plan the drawings and the export need one, and say so rather than linking', () => {
  const v = view({ brief: BRIEF }, null, null, 'brief');
  for (const id of ['drawings', 'export']) {
    assert.equal(item(v, id).link, false, id);
    assert.equal(item(v, id).blocked, 'needs-plan', id);
  }
  // nothing composed: the brief's Next is its reason, not a link to an empty Candidate Set
  assert.deepEqual([v.next.link, v.next.reason], [false, JOURNEY_WORDS.reasons.brief]);
  // an evaluation of no plan cannot unblock them either
  const stale = view({ brief: BRIEF }, null, EVALUATED, 'brief');
  assert.equal(item(stale, 'drawings').link, false);
});

test('Next is a link exactly where the step in view can proceed, and the last step has none', () => {
  const composing = view({ brief: BRIEF, jobId: 'j1', progress: [] }, null, null, 'brief');
  assert.deepEqual([composing.next.link, composing.next.id], [true, 'candidates']);
  const waiting = view({ brief: BRIEF, result: RESULT }, null, null, 'candidates');
  assert.deepEqual([waiting.next.link, waiting.next.reason], [false, JOURNEY_WORDS.reasons.candidates]);
  assert.equal(view({ brief: BRIEF, result: RESULT }, PLAN, EVALUATED, 'export').next, null);
  // the surface that JOINS the journey has no next: its act is sending a plan to the bench
  const traced = view({}, null, null, 'transcription');
  assert.equal(traced.next, null);
  assert.equal(traced.alternate.current, true);
  assert.ok(traced.items.every((i) => !i.current), 'no step claims the tracing surface');
});

test('the step in view is the one marked current, and only it', () => {
  for (const j of JOURNEY) {
    const v = view({ brief: BRIEF, result: RESULT }, PLAN, EVALUATED, j.surface);
    assert.deepEqual(v.items.filter((i) => i.current).map((i) => i.id), [j.id]);
    assert.equal(v.alternate.current, false);
  }
});

test('a failed compose is said on the candidates step, and its Next is the job\'s own reason', () => {
  const s = { brief: BRIEF, jobId: 'j1', jobError: { state: 'failed', reason: 'no parti fits', jobId: 'j1' } };
  const v = view(s, null, null, 'candidates');
  assert.equal(item(v, 'candidates').state, 'failed');
  assert.equal(item(v, 'candidates').words, JOURNEY_WORDS.candidates.failed);
  assert.deepEqual([v.next.link, v.next.reason], [false, 'no parti fits']);
});

test('the origin links back only where the place it came from is still there', () => {
  const pf = (over) => ({ kind: 'candidate', planId: PLAN.id, jobId: 'j1', n: 2, briefName: 'Family house', ...over });
  const same = view({ jobId: 'j1', result: RESULT, planFrom: pf() }, PLAN, null, 'workbench');
  assert.equal(same.origin.words, JOURNEY_WORDS.origin.candidate(2));
  assert.deepEqual(parseHash(same.origin.href), { surface: 'candidates', selection: { candidate: 2 }, params: {} });
  assert.equal(same.origin.briefName, 'Family house');

  // a plan from an EARLIER compose: the Candidate Set shows the current job, so no link to it
  const other = view({ jobId: 'j9', result: RESULT, planFrom: pf() }, PLAN, null, 'workbench');
  assert.equal(other.origin.words, JOURNEY_WORDS.origin.candidate(2), 'still named');
  assert.equal(other.origin.href, null, 'and not linked to somebody else\'s candidates');
  assert.equal(view({ result: RESULT, planFrom: pf() }, PLAN, null, 'workbench').origin.href, null,
    'a session holding no job links to no job');

  const ex = view({ planFrom: pf({ kind: 'example', jobId: null, n: null, briefName: null }) }, PLAN, null, 'workbench');
  assert.deepEqual([ex.origin.words, ex.origin.href, ex.origin.briefName], [JOURNEY_WORDS.origin.example, null, null]);
  const tr = view({ planFrom: pf({ kind: 'traced', jobId: null, n: null, briefName: null }) }, PLAN, null, 'workbench');
  assert.equal(parseHash(tr.origin.href).surface, 'transcription');
  // an origin recorded for another plan is not borrowed
  const un = view({ planFrom: pf({ planId: 'p-other' }) }, PLAN, null, 'workbench');
  assert.deepEqual([un.origin.kind, un.origin.words, un.origin.href], ['unrecorded', JOURNEY_WORDS.origin.unrecorded, null]);
  // and no plan, no origin line
  assert.equal(view({ planFrom: pf() }, null, null, 'workbench').origin, null);
});

test('the component draws a step as an anchor only where the bar says it is a link', () => {
  const src = read('./components/JourneyBar.jsx');
  // a blocked step is a span carrying data-blocked, in the branch taken when item.link is false
  assert.match(src, /\{item\.link\s*\?\s*\(\s*<a\b[^>]*data-step=\{item\.id\}[\s\S]*?\)\s*:\s*\(\s*<span\b[^>]*data-blocked=\{item\.blocked\}/,
    'Step renders <a data-step> when item.link and <span data-step data-blocked> otherwise');
  assert.match(src, /if \(next\.link\)\s*\{\s*return \(\s*<a\b/, 'Next is an anchor only where next.link');
  assert.match(src, /<nav aria-label="house journey"/);
  // a Term is never inside an anchor: every <a>…</a> in the file is free of <Term
  for (const m of src.matchAll(/<a\b[\s\S]*?<\/a>/g)) {
    assert.doesNotMatch(m[0], /<Term\b/, `a Term inside an anchor: ${m[0].slice(0, 60)}`);
  }
});
