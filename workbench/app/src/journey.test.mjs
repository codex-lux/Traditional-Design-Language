/* THE HOUSE JOURNEY, DRIVEN STATE BY STATE (WP-14.6).

   Every body here is hand-built to the contracts the pieces already answer — `session` as
   `state/session.js` holds it plus PRD §G.1's two additions, `lastEval` as
   `workbench/server/evaluate.py` returns it, a refusal as `refusal.test.mjs` builds one — because
   the surfaces that will feed this (WP-14.10) land in another lane, and because the branch that
   matters most, a refused house, is one no shipped record reaches on demand.

   The subjects, each a way the journey could lie to a reader:
   - a failed compose must say it failed and why, not "none yet";
   - a refused house must never offer its drawings or its export;
   - unjudged is counted apart from fatal and serious, and "not counted" is not zero;
   - no plan means the later steps need one, not that they are ready;
   - a plan whose recorded origin is another plan's says so rather than borrowing it;
   - an evaluation of the house before is not an evaluation of this one. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, existsSync, statSync } from 'node:fs';
import {
  JOURNEY, ALTERNATE, JOURNEY_WORDS, JOURNEY_TERMS, journeyState, stepOfSurface, countsOf,
  evalPlanOf, pickedCandidate, stampEval,
} from './journey/journey.js';
import { barView } from './journey/bar.js';
import { SURFACE_PATHS, parseHash } from './router.js';

const ROOT = new URL('../../../', import.meta.url);
const step = (st, id) => st.steps.find((s) => s.id === id);

const BRIEF = { style: 'tidewater-georgian', target_area_sf: 3200 };
const PLAN = { id: 'p-1', style: 'tidewater-georgian', levels: [] };
const check = (over = {}) => ({ plan: PLAN.id, counts: { fatal: 2, serious: 5, minor: 9 },
  constraint_summary: { present: 1, clear: 3, unjudged: 4 }, ...over });
const EVALUATED = { check: check(), placement: { geometry_report: { refused: null } } };
/* An evaluation as the bench files it: stamped with the plan's origin at the time of the request
   (`stampEval`). One whose plan came from somewhere is of that place alone. */
const evalFrom = (planFrom, ev = EVALUATED) => stampEval(ev, PLAN.id, planFrom);
const REFUSAL = {
  kind: 'type-fact-downgraded', facts: ['stacks'],
  conflicts: [{ kind: 'stack', key: ['primary', 'drawing'], why: 'released' }],
  lines: ['the Drawing Room does not stand under the Primary Bedroom it is declared to carry'],
  engine: 'cp-sat', status: 'OPTIMAL',
};
// the two routes the verdict arrives by — the evaluate route's 200, and a placed record
const REFUSED_BY_ROUTE = { check: check(), placement_refused: REFUSAL };
const REFUSED_ON_RECORD = { check: check(), placement: { geometry_report: { refused: REFUSAL } } };
const SKETCH = { check: check(), placement: { geometry_report: { refused: null },
  sketch: { working: true, refused: null, reason: 'a wall drag' } } };

test('the five steps are the contract’s, numbered from their order, each at its own address', () => {
  assert.deepEqual(JOURNEY.map((j) => j.id), ['brief', 'candidates', 'plan', 'drawings', 'export']);
  assert.deepEqual({ ...ALTERNATE }, { transcription: 'plan' });
  const st = journeyState({ session: {}, plan: null, lastEval: null });
  st.steps.forEach((s, i) => {
    assert.equal(s.n, i + 1, 'a step number is its index plus one, never a literal');
    assert.ok(s.surface in SURFACE_PATHS, `${s.surface} is a surface the router knows`);
    assert.equal(parseHash(s.href).surface, s.surface, `${s.id}'s href reaches its own surface`);
  });
  assert.equal(parseHash(st.alternate.href).surface, 'transcription');
  assert.equal(st.alternate.joins, 'plan');
  assert.equal(stepOfSurface('transcription'), 'plan');
  assert.equal(stepOfSurface('workbench'), 'plan');
  assert.equal(stepOfSurface('proportions'), null);
});

test('with nothing begun, every step says so and nothing is offered as ready', () => {
  const st = journeyState({ session: {}, plan: null, lastEval: null });
  assert.deepEqual(st.steps.map((s) => s.state), ['todo', 'none', 'empty', 'needs-plan', 'needs-plan']);
  assert.equal(step(st, 'drawings').words, JOURNEY_WORDS.drawings['needs-plan']);
  assert.equal(step(st, 'export').words, JOURNEY_WORDS.export['needs-plan']);
  assert.ok(st.steps.every((s) => !s.canProceed));
  assert.equal(step(st, 'brief').reason, JOURNEY_WORDS.reasons.brief);
  assert.equal(st.resume, null);
});

test('the brief is stated only by the schema’s two required fields, read off the schema', () => {
  const schema = JSON.parse(readFileSync(new URL('schema/brief.schema.json', ROOT), 'utf8'));
  assert.deepEqual([...schema.required].sort(), ['style', 'target_area_sf'],
    'the premise: these are the two fields a brief must state');
  const st = (brief) => step(journeyState({ session: { brief } }), 'brief').state;
  assert.equal(st(BRIEF), 'stated');
  for (const b of [null, {}, { style: 'x' }, { target_area_sf: 3000 }, { style: '  ', target_area_sf: 3000 },
    { style: 'x', target_area_sf: 0 }, { style: 'x', target_area_sf: -1 }, { style: 'x', target_area_sf: '3000' },
    { style: 'x', target_area_sf: NaN }]) {
    assert.equal(st(b), 'todo', JSON.stringify(b));
  }
  assert.equal(journeyState({ session: { brief: BRIEF } }).resume.id, 'brief');
});

test('a failed compose says failed and gives its own reason, and never reads as none yet', () => {
  const s = { brief: BRIEF, jobId: null, jobError: { state: 'failed', reason: 'the brief names no style the corpus holds', jobId: 'j1' } };
  const c = step(journeyState({ session: s }), 'candidates');
  assert.equal(c.state, 'failed');
  assert.equal(c.words, JOURNEY_WORDS.candidates.failed);
  assert.equal(c.reason, 'the brief names no style the corpus holds');
  assert.notEqual(c.state, 'none');
  // and it is still a place the reader has been: the brief may proceed to see it
  assert.equal(step(journeyState({ session: s }), 'brief').canProceed, true);
  // expired is its own state, with its own words
  const e = step(journeyState({ session: { jobError: { state: 'expired', reason: 'no job j1' } } }), 'candidates');
  assert.deepEqual([e.state, e.words, e.reason], ['expired', JOURNEY_WORDS.candidates.expired, 'no job j1']);
  // a failure with no words falls back to the step's own reason rather than an empty one
  const mute = step(journeyState({ session: { jobError: { state: 'failed', reason: '' } } }), 'candidates');
  assert.equal(mute.reason, JOURNEY_WORDS.reasons.candidates);
});

test('candidate precedence is ready, failed, expired, composing, none', () => {
  const state = (session) => step(journeyState({ session }), 'candidates').state;
  const failed = { state: 'failed', reason: 'x' };
  const result = { candidates: [{}, {}, {}] };
  assert.equal(state({ result, jobError: failed, jobId: 'j' }), 'ready');
  assert.equal(state({ jobError: failed, jobId: 'j' }), 'failed');
  assert.equal(state({ jobError: { state: 'expired', reason: 'x' }, jobId: 'j' }), 'expired');
  assert.equal(state({ jobId: 'j' }), 'composing');
  assert.equal(state({ result: { candidates: 'not a list' } }), 'none');
  assert.equal(step(journeyState({ session: { result } }), 'candidates').words, JOURNEY_WORDS.candidates.ready(3));
  assert.notEqual(JOURNEY_WORDS.candidates.ready(1), JOURNEY_WORDS.candidates.ready(2).replace('2', '1'));
});

test('composing counts candidates scored and never claims a total the stream does not carry', () => {
  const progress = [
    { stage: 'composing' },
    { n: 1, parti: 'a', score: 60 }, { n: 2, parti: 'b', score: 58 },
    { n: 1, revised: true },                  // a revision of one already counted
    { n: 'three' }, { parti: 'no n' },
  ];
  const c = step(journeyState({ session: { jobId: 'j', progress } }), 'candidates');
  assert.equal(c.state, 'composing');
  assert.equal(c.words, JOURNEY_WORDS.candidates.composing(2));
  assert.match(c.words, /\b2\b/);
  assert.doesNotMatch(c.words, /\bof\b/, 'k of N: this stream states no N, so none is printed');
});

/* "k OF N" FROM THE STREAM'S OWN TOTAL (WP-14.25). The events are the shapes
   `workbench/server/jobs.py` puts since WP-14.19: every stage carries `total`, and every diagram
   considered -- scored as a `candidate`, or dropped for the lot as a `dropped` stage -- carries
   `considered`, the running count. The fixture's N is chosen to be neither the scored count nor
   the event count, so a reading that counted either instead of reading `total` cannot pass. */
test('composing says k of N, with N the total the stream states and k the diagrams considered', () => {
  const N = 7;
  const progress = [
    { stage: 'seeding', total: N, note: 'reading the brief' },
    { stage: 'composing', total: N, note: 'seeding, repairing and scoring' },
    { n: 1, parti: 'a', score: 60, considered: 1, total: N },
    { stage: 'dropped', parti: 'b', note: 'B: the lot', considered: 2, total: N },
    { n: 2, parti: 'c', score: 58, considered: 3, total: N },
    { n: 1, revised: true, parti: 'a' },      // the loop's second word on one already counted
  ];
  const c = step(journeyState({ session: { jobId: 'j', progress } }), 'candidates');
  assert.equal(c.state, 'composing');
  // the premise: scored (2) and events (6) are both different from the diagrams considered (3)
  assert.equal(progress.filter((e) => Number.isInteger(e.n) && !e.revised).length, 2);
  assert.equal(c.words, JOURNEY_WORDS.candidates.composing(3, N));
  assert.match(c.words, new RegExp(`\\b3 of ${N}\\b`), 'the diagrams considered, of the total the stream states');
  assert.notEqual(JOURNEY_WORDS.candidates.composing(3, N), JOURNEY_WORDS.candidates.composing(3),
    'a total changes the words');
  // before any diagram is heard from, k is nought of N -- counted, and not the old "scored"
  const early = step(journeyState({ session: { jobId: 'j', progress: progress.slice(0, 2) } }), 'candidates');
  assert.equal(early.words, JOURNEY_WORDS.candidates.composing(0, N));
  // a total that is not a count is no total
  for (const t of [0, -1, 2.5, '7', null]) {
    assert.equal(JOURNEY_WORDS.candidates.composing(1, t), JOURNEY_WORDS.candidates.composing(1), String(t));
  }
});

test('the journey writes no total of its own: N comes from the stream and nowhere else', () => {
  const src = readFileSync(new URL('./journey/journey.js', import.meta.url), 'utf8')
    .replace(/\/\*[\s\S]*?\*\//g, ' ');
  // the composing words are a function of the stream's numbers, with no count literal in them
  const line = src.split('\n').find((l) => /composing:\s*\(k, total\)/.test(l));
  assert.ok(line, 'the composing words take the total they print');
  assert.doesNotMatch(src.slice(src.indexOf(line), src.indexOf(line) + 200), /of \d/,
    'a count literal in the composing words');
});

test('a refused house never proceeds to its drawings or its export, whichever route the verdict took', () => {
  for (const lastEval of [REFUSED_BY_ROUTE, REFUSED_ON_RECORD]) {
    const st = journeyState({ session: {}, plan: PLAN, lastEval });
    const [p, d, e] = ['plan', 'drawings', 'export'].map((id) => step(st, id));
    assert.equal(p.state, 'refused');
    assert.equal(d.state, 'refused');
    assert.equal(e.state, 'refused');
    assert.equal(p.canProceed, false, 'the plan may not go on to drawings');
    assert.equal(d.canProceed, false, 'the drawings may not go on to export');
    assert.equal(p.reason, JOURNEY_WORDS.drawings.refused);
    assert.equal(d.reason, JOURNEY_WORDS.export.refused);
    assert.notEqual(d.words, JOURNEY_WORDS.drawings.ready);
    assert.notEqual(e.words, JOURNEY_WORDS.export.ready);
    assert.equal(p.stateTerm, JOURNEY_TERMS.refused);
    assert.ok(p.words.startsWith(JOURNEY_WORDS.plan.refused), 'the refusal leads, then the counts');
    assert.deepEqual(p.counts, { fatal: 2, serious: 5, unjudged: 4 });
  }
});

test('the verdict is the refusal leaf’s, so a body that leaf cannot read is not a refusal', () => {
  /* A body whose `refused` has a kind the leaf does not know is UNSTATED to the leaf, and must be
     unstated here too: re-deriving "refused" from the record's own fact blocks would be a second
     answer to one question, which is what `refusal.test.mjs`'s READERS guard exists to stop. */
  const odd = { check: check(), placement: { geometry_report: { refused: { kind: 'something-new', facts: ['x'] } } } };
  const st = journeyState({ session: {}, plan: PLAN, lastEval: odd });
  assert.equal(step(st, 'plan').state, 'evaluated');
  assert.equal(step(st, 'drawings').state, 'ready');
});

test('a working sketch blocks the export and not the drawings', () => {
  const st = journeyState({ session: {}, plan: PLAN, lastEval: SKETCH });
  assert.equal(step(st, 'drawings').state, 'ready', 'the Drawing Set re-places the record itself');
  assert.equal(step(st, 'export').state, 'sketch');
  assert.equal(step(st, 'export').words, JOURNEY_WORDS.export.sketch);
  assert.equal(step(st, 'plan').canProceed, true);
  assert.equal(step(st, 'drawings').canProceed, false);
  assert.equal(step(st, 'drawings').reason, JOURNEY_WORDS.export.sketch);
});

test('unjudged is counted apart from fatal and serious, and not counted is not zero', () => {
  const st = journeyState({ session: {}, plan: PLAN, lastEval: EVALUATED });
  const p = step(st, 'plan');
  assert.equal(p.state, 'evaluated');
  assert.deepEqual(p.counts, { fatal: 2, serious: 5, unjudged: 4 });
  assert.equal(p.counts.fatal + p.counts.serious, 7, 'the minor count and the unjudged are in neither severity');
  assert.match(p.words, /\b2 fatal\b/);
  assert.match(p.words, /\b5 serious\b/);
  assert.match(p.words, /\b4 unjudged\b/);
  // an absent severity key after a completed check is a real zero...
  assert.deepEqual(countsOf({ counts: { minor: 3 }, constraint_summary: { unjudged: 0 } }),
    { fatal: 0, serious: 0, unjudged: 0 });
  // ...and an absent counts object or unjudged figure is NOT
  assert.deepEqual(countsOf({ constraint_summary: {} }), { fatal: null, serious: null, unjudged: null });
  const q = step(journeyState({ session: {}, plan: PLAN,
    lastEval: { check: { plan: PLAN.id, counts: { fatal: 1 } } } }), 'plan');
  assert.equal(q.counts.unjudged, null);
  assert.match(q.words, new RegExp(`${JOURNEY_WORDS.counts.unjudged} ${JOURNEY_WORDS.counts.notCounted}`));
  assert.doesNotMatch(q.words, /\b0 unjudged\b/, 'a figure nobody stated is not a zero');
});

test('an evaluation of another plan is not an evaluation of this one', () => {
  const other = { ...REFUSED_BY_ROUTE, check: check({ plan: 'some-other-plan' }) };
  const st = journeyState({ session: {}, plan: PLAN, lastEval: other });
  assert.equal(step(st, 'plan').state, 'unevaluated');
  assert.equal(step(st, 'plan').counts, null, 'no borrowed counts');
  assert.equal(step(st, 'drawings').state, 'ready', 'and no borrowed refusal');
  // a plan with no id can be matched to nothing
  const anon = journeyState({ session: {}, plan: { levels: [] }, lastEval: { check: { counts: {} } } });
  assert.equal(step(anon, 'plan').state, 'unevaluated');
});

test('an evaluation whose check errored names its plan at the top, and a refusal on it blocks the drawings (WP-14.20)', () => {
  /* `oq/an-evaluation-whose-check-errored-names-no-plan`. `core.check_plan`'s error payloads carry
     no plan id, and the evaluate route keeps `placement_refused` alive through that early return;
     since WP-14.20 the route states the id at the top of its response. Read only off the check,
     this body named no plan, so the journey said "not yet evaluated" and offered the drawings and
     the export as ready LINKS over a refused house. Dropping the `lastEval.plan` read from
     `evalPlanOf` turns every assertion below red. */
  const errored = { plan: PLAN.id, check: { error: 'plan does not match the plan schema' },
    placement_refused: REFUSAL };
  assert.equal(errored.check.plan, undefined, 'the premise: the check itself names no plan');
  assert.equal(evalPlanOf(errored), PLAN.id);
  const st = journeyState({ session: {}, plan: PLAN, lastEval: errored });
  const [p, d, e] = ['plan', 'drawings', 'export'].map((id) => step(st, id));
  assert.equal(p.state, 'refused');
  assert.equal(d.state, 'refused');
  assert.equal(e.state, 'refused');
  assert.deepEqual(p.counts, { fatal: null, serious: null, unjudged: null },
    'an errored check counted nothing, and nothing it did not count reads as zero');
  const v = barView(st, { surface: 'workbench' });
  const item = (id) => v.items.find((i) => i.id === id);
  assert.equal(item('drawings').link, false, 'the drawings of a refused house are not a link');
  assert.equal(item('export').link, false, 'nor is its export');
  assert.equal(item('drawings').blocked, 'refused');
  assert.equal(item('export').blocked, 'refused');
  // and the identity rule still holds on this path: an errored evaluation of ANOTHER plan
  const other = { ...errored, plan: 'some-other-plan' };
  assert.equal(step(journeyState({ session: {}, plan: PLAN, lastEval: other }), 'drawings').state, 'ready',
    'a refusal of the house before must not block the drawings of this one');
});

test('evalPlanOf reads the route\'s id first and the check\'s second, and nothing else', () => {
  assert.equal(evalPlanOf({ check: { plan: 'a' } }), 'a', 'a completed check names its plan');
  assert.equal(evalPlanOf({ plan: 'b', check: { error: 'x' } }), 'b', 'the route names it on an error');
  assert.equal(evalPlanOf({ plan: 'b', check: { plan: 'b' } }), 'b');
  for (const nothing of [null, undefined, {}, { check: {} }, { plan: '', check: {} }, { plan: 7 },
    { check: { plan: ['a'] } }, 'p-1']) {
    assert.equal(evalPlanOf(nothing), null, `${JSON.stringify(nothing)} names no plan`);
  }
});

test('every site that matches an evaluation to a plan reads evalPlanOf, and none reads the check by hand', () => {
  /* Two sites matched an evaluation to a plan -- this module and `App.jsx`'s stale-evaluation
     clear -- and each spelled `check.plan` itself, which is how the errored path came to be read
     one way in one place. The walk is over the app's own sources, tests excluded. */
  const SRC = new URL('./', import.meta.url);
  const files = [];
  const walk = (dir) => {
    for (const f of readdirSync(dir).sort()) {
      const u = new URL(f, dir);
      if (statSync(u).isDirectory()) walk(new URL(f + '/', dir));
      else if (/\.(m?js|jsx)$/.test(f) && !/\.test\.mjs$/.test(f)) files.push(u);
    }
  };
  walk(SRC);
  const byHand = /\bcheck\s*\??\.\s*plan\b/;
  const offenders = files.filter((u) => !u.pathname.endsWith('/journey/journey.js'))
    .filter((u) => byHand.test(readFileSync(u, 'utf8').replace(/\/\*[\s\S]*?\*\//g, '')))
    .map((u) => u.pathname.slice(SRC.pathname.length));
  assert.deepEqual(offenders, [], 'these read an evaluation\'s plan off its check by hand');
  assert.ok(files.length > 50, 'the walk reached the app\'s sources');
  assert.match(readFileSync(new URL('App.jsx', SRC), 'utf8'), /evalIsOf\(ev, planId, planFrom\)/,
    'App.jsx\'s stale-evaluation clear reads evalIsOf (built on evalPlanOf)');
});

test('no plan: drawings and export need one, and the candidates step offers the way', () => {
  const st = journeyState({ session: { brief: BRIEF, result: { candidates: [{}] } }, plan: null, lastEval: EVALUATED });
  assert.equal(step(st, 'plan').state, 'empty');
  assert.equal(step(st, 'drawings').state, 'needs-plan');
  assert.equal(step(st, 'export').state, 'needs-plan');
  assert.equal(step(st, 'drawings').words, JOURNEY_WORDS.drawings['needs-plan']);
  assert.equal(step(st, 'candidates').canProceed, false);
  assert.equal(step(st, 'candidates').reason, JOURNEY_WORDS.reasons.candidates);
  assert.equal(step(st, 'plan').origin, null);
  assert.equal(st.resume.id, 'candidates');
});

test('the origin is the session’s only when it names this plan, and says so when it does not', () => {
  const candidate = { kind: 'candidate', planId: PLAN.id, jobId: 'j1', n: 2, briefName: 'family-georgian' };
  const p = step(journeyState({ session: { planFrom: candidate }, plan: PLAN }), 'plan');
  assert.equal(p.origin, candidate);
  assert.equal(p.originWords, JOURNEY_WORDS.origin.candidate(2));
  assert.match(p.originWords, /\b3\b/, 'the bar shows n + 1');
  assert.equal(parseHash(p.originHref).selection.candidate, 2);
  const stale = step(journeyState({ session: { planFrom: { ...candidate, planId: 'another-plan' } }, plan: PLAN }), 'plan');
  assert.deepEqual(stale.origin, { kind: 'unrecorded' });
  assert.equal(stale.originWords, JOURNEY_WORDS.origin.unrecorded);
  assert.equal(stale.originHref, null);
  const none = step(journeyState({ session: {}, plan: PLAN }), 'plan');
  assert.deepEqual(none.origin, { kind: 'unrecorded' });
  const traced = step(journeyState({ session: { planFrom: { kind: 'traced', planId: PLAN.id } }, plan: PLAN }), 'plan');
  assert.equal(parseHash(traced.originHref).surface, 'transcription');
  const example = step(journeyState({ session: { planFrom: { kind: 'example', planId: PLAN.id } }, plan: PLAN }), 'plan');
  assert.equal(example.originWords, JOURNEY_WORDS.origin.example);
  // a plan with no id cannot claim any origin, even from a planFrom with no id either
  const anon = step(journeyState({ session: { planFrom: { kind: 'example' } }, plan: {} }), 'plan');
  assert.deepEqual(anon.origin, { kind: 'unrecorded' });
});

test('a clean evaluated house proceeds step to step, and the export step is the last', () => {
  // the plan came from a candidate of the compose in hand: that is what lets the candidates step
  // hand on to the bench (a plan from anywhere else does not -- the next test)
  const from = { kind: 'candidate', planId: PLAN.id, jobId: 'j1', n: 0 };
  const st = journeyState({ session: { brief: BRIEF, jobId: 'j1', planFrom: from, result: { candidates: [{}] } },
    plan: PLAN, lastEval: EVALUATED });
  assert.deepEqual(st.steps.map((s) => s.canProceed), [true, true, true, true, false]);
  assert.deepEqual(st.steps.map((s) => s.reason), [null, null, null, null, null]);
  assert.equal(step(st, 'export').state, 'ready');
  assert.deepEqual(st.resume, { id: 'plan', n: 3, href: step(st, 'plan').href });
  // an unevaluated plan still lets the reader see its drawings: the Drawing Set places it itself
  const un = journeyState({ session: {}, plan: PLAN, lastEval: null });
  assert.equal(step(un, 'plan').state, 'unevaluated');
  assert.equal(step(un, 'plan').words, JOURNEY_WORDS.plan.unevaluated);
  assert.equal(step(un, 'drawings').state, 'ready');
});

test('a plan on the bench carries the candidates step on only where it came from THIS compose', () => {
  /* The bench keeps its record across a refresh and across a whole compose, so "a plan on the
     bench" was true of an example opened last week when the candidates arrived -- and Next from
     the Candidate Set then led from the candidate a reader had just picked to that example. The
     step proceeds only for a candidate of the job in hand; every other origin is a place a plan
     can come from and none of them is the pick. */
  const result = { candidates: [{}, {}] };
  const at = (planFrom, jobId = 'j2') => step(journeyState({
    session: { brief: BRIEF, jobId, planFrom, result }, plan: PLAN, lastEval: EVALUATED }), 'candidates');
  const ok = at({ kind: 'candidate', planId: PLAN.id, jobId: 'j2', n: 1 });
  assert.deepEqual([ok.canProceed, ok.reason], [true, null]);
  const stale = {
    'the example': { kind: 'example', planId: PLAN.id },
    'a tracing': { kind: 'traced', planId: PLAN.id },
    // `readPlanFrom` reads a job id for ANY kind off storage, so the kind is its own condition
    'an example whose stored entry carries this job': { kind: 'example', planId: PLAN.id, jobId: 'j2' },
    'a tracing whose stored entry carries this job': { kind: 'traced', planId: PLAN.id, jobId: 'j2' },
    'a candidate of an EARLIER job': { kind: 'candidate', planId: PLAN.id, jobId: 'j1', n: 1 },
    'a candidate recording no job': { kind: 'candidate', planId: PLAN.id, jobId: null, n: 1 },
    'no origin recorded': null,
    'an origin that names ANOTHER plan': { kind: 'candidate', planId: 'p-other', jobId: 'j2', n: 1 },
  };
  for (const [what, pf] of Object.entries(stale)) {
    const c = at(pf);
    assert.equal(c.canProceed, false, what);
    assert.equal(c.reason, JOURNEY_WORDS.reasons.candidates, what);
  }
  // the session holding NO job cannot match a candidate to one either
  assert.equal(at({ kind: 'candidate', planId: PLAN.id, jobId: 'j2', n: 1 }, null).canProceed, false);
  /* and it moves nothing else. The plan, drawings and export are judged on the plan and its
     evaluation, as before: a refused example stays refused, a clean one stays ready. */
  const exFrom = { kind: 'example', planId: PLAN.id };
  const st = journeyState({ session: { brief: BRIEF, jobId: 'j2', result, planFrom: exFrom },
    plan: PLAN, lastEval: evalFrom(exFrom) });
  assert.deepEqual(st.steps.map((x) => x.state), ['stated', 'ready', 'evaluated', 'ready', 'ready']);
  assert.deepEqual(st.steps.slice(2).map((x) => x.canProceed), [true, true, false]);
  const refused = journeyState({ session: { brief: BRIEF, jobId: 'j2', result, planFrom: exFrom },
    plan: PLAN, lastEval: evalFrom(exFrom, { check: check(), placement_refused: REFUSAL }) });
  assert.deepEqual(refused.steps.slice(2).map((x) => x.state), ['refused', 'refused', 'refused']);
});

test('the candidates step is held by a null job only when BOTH sides are null, and trims both sides alike', () => {
  /* The guard `str(origin.jobId) &&` is the only thing between a candidate recorded with no job and
     a session that has none: null === null is true, and the step would proceed for a plan nobody
     can place in any compose. (Found by mutation: deleting it left every test green.) */
  const result = { candidates: [{}, {}] };
  const at = (jobId, pfJob) => step(journeyState({
    session: { brief: BRIEF, jobId, result, planFrom: { kind: 'candidate', planId: PLAN.id, jobId: pfJob, n: 0 } },
    plan: PLAN, lastEval: EVALUATED }), 'candidates').canProceed;
  for (const none of [null, undefined, '', '   ']) {
    assert.equal(at(none, null), false, `session job ${JSON.stringify(none)} against an origin with no job`);
    assert.equal(at(none, undefined), false);
  }
  // the readers disagree about whitespace (`sessionWrites` keeps it, this file trims): both sides are
  // trimmed here, so an id that differs only by a stray space is the same compose
  assert.equal(at('j2', 'j2 '), true);
  assert.equal(at(' j2 ', 'j2'), true);
  assert.equal(at('j2', 'j3'), false);
});

test('a plan opened from THIS compose leaves the step whatever its evaluation says, and a refused one is still refused', () => {
  /* Whether the candidate may be drawn is the Plan step's to say. The candidates step asks only
     whether the plan on the bench is the reader's: a refused candidate opened from this compose
     (the bench placed it and turned it down) goes on to the Plan step, where the refusal is. */
  const result = { candidates: [{}, {}] };
  const session = { brief: BRIEF, jobId: 'j2', result, planFrom: { kind: 'candidate', planId: PLAN.id, jobId: 'j2', n: 0 } };
  const unevaluated = journeyState({ session, plan: PLAN, lastEval: null });
  assert.equal(step(unevaluated, 'candidates').canProceed, true);
  assert.equal(step(unevaluated, 'plan').state, 'unevaluated');
  const refused = journeyState({ session, plan: PLAN,
    lastEval: evalFrom(session.planFrom, { check: check(), placement_refused: REFUSAL }) });
  assert.equal(step(refused, 'candidates').canProceed, true);
  assert.equal(step(refused, 'plan').state, 'refused');
  assert.equal(step(refused, 'drawings').state, 'refused');
});

test('where a candidate is picked, Next goes on only with the candidate that was picked', () => {
  /* The compose-level test stops a stale example. It cannot tell candidate 0 on the bench from the
     candidate 3 a reader has just picked, and Next led them to the plan of the one they did not
     pick: the original complaint, with the right job. */
  const ref = { kind: 'type-fact-downgraded', facts: ['stacks'], conflicts: [], lines: [] };
  const placed = { revision: { stop_reason: 'converged' }, refused: null };
  const result = { candidates: [placed, placed, { ...placed, refused: ref }, placed] };
  const bench = (n, session = {}) => ({ brief: BRIEF, jobId: 'j2', result,
    planFrom: { kind: 'candidate', planId: PLAN.id, jobId: 'j2', n }, ...session });
  const at = (picked, n = 1, session = {}) => step(journeyState({
    session: bench(n, session), plan: PLAN, lastEval: evalFrom(bench(n, session).planFrom), picked }), 'candidates');
  // no pick in the address: a reader returning to the set is not held
  assert.equal(at(null).canProceed, true);
  // the pick is what is on the bench
  const same = at(1);
  assert.deepEqual([same.canProceed, same.reason], [true, null]);
  // the pick is another candidate of this compose: say so, and what to do
  const other = at(3);
  assert.deepEqual([other.canProceed, other.reason], [false, JOURNEY_WORDS.reasons.picked]);
  // the pick is one the type turned down: "open it" cannot be followed, so the reason says why not
  const turned = at(2);
  assert.deepEqual([turned.canProceed, turned.reason], [false, JOURNEY_WORDS.reasons.pickedRefused]);
  // a pick with nothing on the bench from this compose
  const noPlan = step(journeyState({ session: { brief: BRIEF, jobId: 'j2', result }, plan: null, picked: 3 }), 'candidates');
  assert.deepEqual([noPlan.canProceed, noPlan.reason], [false, JOURNEY_WORDS.reasons.picked]);
  // a pick that names no candidate of the set is no pick the reader could follow: the plain reason
  assert.equal(at(9).reason, JOURNEY_WORDS.reasons.candidates);
  // the Plan, Drawings and Export steps do not read the pick
  const st = journeyState({ session: bench(1), plan: PLAN, lastEval: evalFrom(bench(1).planFrom), picked: 3 });
  assert.deepEqual(st.steps.slice(2).map((x) => x.canProceed), [true, true, false]);
});

test('the two reasons a pick can change between are no longer than one another, so the bar does not reflow', () => {
  /* The bar's Next is one unbroken run, and a run that does not fit beside the steps jumps to a row
     of its own. With a plan on the bench at 1680 px the longer words (58 characters against 42) did
     that: the page moved 21 px under the pointer on each pick that changed between a refused column
     and an open one. The walk measures the grid; this holds the cause where a unit test can see it. */
  assert.ok(JOURNEY_WORDS.reasons.pickedRefused.length <= JOURNEY_WORDS.reasons.picked.length,
    `${JOURNEY_WORDS.reasons.pickedRefused.length} > ${JOURNEY_WORDS.reasons.picked.length}`);
});

test('a set with nothing to open says so in the step\'s reason, instead of telling a reader to open one', () => {
  const ref = { kind: 'infeasible', facts: ['bearing'], conflicts: [], lines: [] };
  const reasonFor = (candidates, picked = null) => step(journeyState({
    session: { brief: BRIEF, jobId: 'j2', result: { candidates } }, plan: null, picked }), 'candidates').reason;
  const placed = { revision: { stop_reason: 'converged' }, refused: null };
  assert.equal(reasonFor([]), JOURNEY_WORDS.reasons.empty);
  assert.equal(reasonFor([{ refused: ref }, { refused: ref }]), JOURNEY_WORDS.reasons.allRefused);
  assert.equal(reasonFor([{ refused: ref }, { refused: ref }], 1), JOURNEY_WORDS.reasons.allRefused,
    'nothing to open outranks which one was picked');
  // one openable candidate among refused ones: the plain instruction can be followed
  assert.equal(reasonFor([{ refused: ref }, placed]), JOURNEY_WORDS.reasons.candidates);
  // a candidate nobody judged is openable: it is not a refusal, and the bench is where it is placed
  assert.equal(reasonFor([{ refused: ref }, {}]), JOURNEY_WORDS.reasons.candidates);
  // no compose in hand: the plain instruction, as before
  assert.equal(step(journeyState({ session: { brief: BRIEF }, plan: null }), 'candidates').reason,
    JOURNEY_WORDS.reasons.candidates);
});

test('a pick means something only on the Candidate Set, and only as an index', () => {
  assert.equal(pickedCandidate('candidates', { candidate: 2 }), 2);
  assert.equal(pickedCandidate('candidates', { candidate: 0 }), 0, 'candidate 0 is a pick');
  assert.equal(pickedCandidate('workbench', { candidate: 2 }), null);
  for (const bad of [null, undefined, {}, { candidate: null }, { candidate: -1 }, { candidate: 1.5 }, { candidate: '2' }]) {
    assert.equal(pickedCandidate('candidates', bad), null, JSON.stringify(bad));
  }
});

test('the shell and the bar read the same pick: both hand the journey the address\'s candidate', () => {
  /* Two components build the journey (`App.jsx` for the sidebar and crumbs, `JourneySpine.jsx` for
     the stations -- the bar until Phase 17), and a pick one of them did not pass would make the bar and the rest of the shell disagree
     about whether Next is on. The component cannot be rendered under `node --test`, so what is held
     is the join: each takes the pick through `pickedCandidate` from the surface and its selection. */
  const app = readFileSync(new URL('./App.jsx', import.meta.url), 'utf8');
  const bar = readFileSync(new URL('./components/JourneySpine.jsx', import.meta.url), 'utf8');
  assert.match(app, /journeyState\(\{[^}]*picked: pickedCandidate\(surface, selection\)[^}]*\}\)/);
  assert.match(app, /<JourneySpine surface=\{surface\} lastEval=\{lastEval\} selection=\{selection\}/);
  assert.match(bar, /export function JourneySpine\(\{ surface, lastEval, selection, compact = false \}\)/);
  assert.match(bar, /journeyState\(\{[^}]*picked: pickedCandidate\(surface, selection\)[^}]*\}\)/);
  assert.match(bar, /\[s, plan, lastEval, surface, selection\]/, 'the memo is keyed on the pick');
});

test('the words that are glossary terms say what their records say', (t) => {
  const dir = new URL('glossary/', ROOT);
  const ids = Object.values(JOURNEY_TERMS);
  const found = existsSync(dir)
    ? readdirSync(dir).filter((f) => ids.includes(f.replace(/\.json$/, ''))) : [];
  if (found.length < ids.length) {
    t.skip(`COULD NOT EVALUATE: ${ids.length - found.length} of ${ids.length} records `
      + `(${ids.join(', ')}) are not on this tree yet (WP-14.2)`);
    return;
  }
  const termOf = (id) => JSON.parse(readFileSync(new URL(id + '.json', dir), 'utf8')).term;
  assert.equal(JOURNEY_WORDS.plan.refused, termOf(JOURNEY_TERMS.refused));
  for (const k of ['fatal', 'serious', 'unjudged']) {
    assert.equal(JOURNEY_WORDS.counts[k], termOf(JOURNEY_TERMS[k]), k);
  }
});
