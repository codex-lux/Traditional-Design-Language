/* THE HOUSE JOURNEY, STEP BY STEP, IN WORDS (WP-14.6, PRD §G).

   Brief → candidates → plan → drawings → export was split across three rail groups with no stepper
   and no account of where the reader had got to: a failed compose went to a no-op handler, a plan
   opened from a candidate forgot which one, and nothing said that a refused house has no drawings
   to go to. `journeyState` is the ONE reading of where a house stands, from the three things the
   shell already holds — the `session` store, the plan on the bench, and the last evaluation — and
   every surface that shows the journey (the bar, the rail's metas, the front door's "Continue")
   reads it rather than deciding for itself.

   MAY THIS BE DRAWN IS NOT DECIDED HERE. The refused state is `evaluateRefusal(lastEval) ||
   placementRefusal(lastEval.placement)` — the same two readers the bench and the export surface
   call — and the working sketch is `sketchOf`, all three from `../sheet/refusal.js`, the app's one
   reader of the server's verdict. `refusal.test.mjs` lists this file among its READERS, so it is
   held to importing that leaf and to re-deriving nothing from the record's own fact blocks.

   AN EVALUATION COUNTS ONLY FOR THE PLAN IT WAS OF. `lastEval` is the shell's, and it outlives a
   plan change; a verdict about the house before is not a verdict about this one, so it is read
   only where `lastEval.check.plan === plan.id` (`plan_check` returns the plan id). Otherwise the
   plan is UNEVALUATED — never "0 fatal", which would be a pass nobody measured.

   THREE COUNTS, NEVER ONE. Fatal, serious and unjudged are three numbers and stay three: an
   unjudged constraint is not a failure and not a pass, and adding it to either would say
   something about the house nobody measured. A severity key absent from a completed check is a
   real zero (`plan_check` writes a key only when a finding carries that severity); an absent
   `counts` object or an absent `unjudged` is NOT a zero, and reads as not counted.

   "k SCORED", NEVER "k OF N". The compose job's `candidate` event carries its arrival index and no
   total (`workbench/server/jobs.py`), so N is not knowable from the stream and is not printed.

   Every word the journey shows is in JOURNEY_WORDS, one spelling. The four that are also glossary
   terms (refused, fatal, serious, unjudged) are named in JOURNEY_TERMS so the bar can render them as
   `Term`s, and `journey.test.mjs` holds each word to its record's `term` wherever the records are
   on the tree.

   Pure: no React, no DOM. */
import { evaluateRefusal, placementRefusal, sketchOf } from '../sheet/refusal.js';
import { formatHash } from '../router.js';

export const JOURNEY = Object.freeze([
  Object.freeze({ id: 'brief', surface: 'brief' }),
  Object.freeze({ id: 'candidates', surface: 'candidates' }),
  Object.freeze({ id: 'plan', surface: 'workbench' }),
  Object.freeze({ id: 'drawings', surface: 'drawings' }),
  Object.freeze({ id: 'export', surface: 'export' }),
]);

/* A surface that is not a step joins the journey at one: tracing a drawing produces a plan. */
export const ALTERNATE = Object.freeze({ transcription: 'plan' });

const plural = (k, one, many) => `${k} ${k === 1 ? one : many}`;

export const JOURNEY_WORDS = Object.freeze({
  brief: Object.freeze({ todo: 'to do', stated: 'stated' }),
  candidates: Object.freeze({
    ready: (k) => plural(k, 'candidate', 'candidates'),
    failed: 'failed',
    expired: 'expired',
    composing: (k) => `composing · ${k} scored`,
    none: 'none yet',
  }),
  plan: Object.freeze({
    empty: 'no plan on the bench',
    refused: 'refused',
    unevaluated: 'not yet evaluated',
  }),
  drawings: Object.freeze({ 'needs-plan': 'needs a plan', refused: 'blocked: refused', ready: 'ready' }),
  export: Object.freeze({
    'needs-plan': 'needs a plan',
    refused: 'blocked: refused',
    sketch: 'blocked: a working sketch',
    ready: 'ready',
  }),
  counts: Object.freeze({ fatal: 'fatal', serious: 'serious', unjudged: 'unjudged', notCounted: 'not counted' }),
  separator: ' · ',
  reasons: Object.freeze({ brief: 'compose the brief first', candidates: 'open a candidate on the bench' }),
  origin: Object.freeze({
    candidate: (n) => (Number.isInteger(n) && n >= 0 ? `candidate ${n + 1}` : 'a candidate'),
    example: 'the example',
    traced: 'traced from a drawing',
    unrecorded: 'origin not recorded',
  }),
});

/* The words above that are also glossary records, by the record's id. */
export const JOURNEY_TERMS = Object.freeze({
  refused: 'judgment-refused',
  fatal: 'severity-fatal',
  serious: 'severity-serious',
  unjudged: 'judgment-unjudged',
});

const W = JOURNEY_WORDS;
const str = (v) => (typeof v === 'string' && v.trim() ? v.trim() : null);
const isObj = (v) => Boolean(v) && typeof v === 'object' && !Array.isArray(v);
const count = (v) => (typeof v === 'number' && Number.isFinite(v) ? v : null);

/* The step a surface belongs to, or null — `transcription` joins at the plan. */
export function stepOfSurface(surface) {
  const s = JOURNEY.find((j) => j.surface === surface);
  if (s) return s.id;
  return Object.prototype.hasOwnProperty.call(ALTERNATE, surface) ? ALTERNATE[surface] : null;
}

/* {fatal, serious, unjudged} off a completed check. */
export function countsOf(check) {
  const c = isObj(check) && isObj(check.counts) ? check.counts : null;
  const sev = (k) => (c ? (c[k] === undefined ? 0 : count(c[k])) : null);
  const cs = isObj(check) && isObj(check.constraint_summary) ? check.constraint_summary : null;
  return { fatal: sev('fatal'), serious: sev('serious'), unjudged: cs ? count(cs.unjudged) : null };
}

/* The three counts in words, each apart. */
export function countsWords(counts) {
  const one = (k) => {
    const n = counts ? counts[k] : null;
    return n === null || n === undefined ? `${W.counts[k]} ${W.counts.notCounted}` : `${n} ${W.counts[k]}`;
  };
  return ['fatal', 'serious', 'unjudged'].map(one).join(W.separator);
}

function briefStep(session) {
  const b = isObj(session.brief) ? session.brief : null;
  const area = b ? b.target_area_sf : null;
  const stated = Boolean(b && str(b.style) && typeof area === 'number' && Number.isFinite(area) && area > 0);
  return { state: stated ? 'stated' : 'todo', words: stated ? W.brief.stated : W.brief.todo };
}

function candidatesStep(session) {
  const result = isObj(session.result) ? session.result : null;
  const err = isObj(session.jobError) ? session.jobError : null;
  if (result && Array.isArray(result.candidates)) {
    return { state: 'ready', words: W.candidates.ready(result.candidates.length) };
  }
  if (err && err.state === 'failed') return { state: 'failed', words: W.candidates.failed, failure: str(err.reason) };
  if (err && err.state === 'expired') return { state: 'expired', words: W.candidates.expired, failure: str(err.reason) };
  if (str(session.jobId)) {
    const progress = Array.isArray(session.progress) ? session.progress : [];
    const k = progress.filter((e) => isObj(e) && count(e.n) !== null && !e.revised).length;
    return { state: 'composing', words: W.candidates.composing(k) };
  }
  return { state: 'none', words: W.candidates.none };
}

function originOf(planId, planFrom) {
  const pf = isObj(planFrom) ? planFrom : null;
  const origin = pf && planId && pf.planId === planId ? pf : { kind: 'unrecorded' };
  let words, href = null;
  if (origin.kind === 'candidate') {
    words = W.origin.candidate(origin.n);
    if (Number.isInteger(origin.n) && origin.n >= 0) href = formatHash('candidates', { candidate: origin.n }, {});
  } else if (origin.kind === 'example') {
    words = W.origin.example;
  } else if (origin.kind === 'traced') {
    words = W.origin.traced;
    href = formatHash('transcription', {}, {});
  } else {
    words = W.origin.unrecorded;
  }
  return { origin, originWords: words, originHref: href };
}

export function journeyState({ session, plan, lastEval } = {}) {
  const s = isObj(session) ? session : {};
  const hasPlan = isObj(plan);
  const planId = hasPlan ? str(plan.id) : null;
  // the evaluation of THIS plan, or nothing
  const ev = planId && isObj(lastEval) && isObj(lastEval.check) && lastEval.check.plan === planId
    ? lastEval : null;
  const refusal = ev ? (evaluateRefusal(ev) || placementRefusal(ev.placement)) : null;
  const sketch = ev ? sketchOf(ev.placement) : null;

  const brief = briefStep(s);
  const candidates = candidatesStep(s);

  let plan_;
  if (!hasPlan) {
    plan_ = { state: 'empty', words: W.plan.empty, counts: null, stateTerm: null };
  } else if (refusal) {
    const counts = countsOf(ev.check);
    plan_ = { state: 'refused', words: W.plan.refused + W.separator + countsWords(counts), counts,
      stateTerm: JOURNEY_TERMS.refused };
  } else if (ev) {
    const counts = countsOf(ev.check);
    plan_ = { state: 'evaluated', words: countsWords(counts), counts, stateTerm: null };
  } else {
    plan_ = { state: 'unevaluated', words: W.plan.unevaluated, counts: null, stateTerm: null };
  }
  const origin = hasPlan ? originOf(planId, s.planFrom) : { origin: null, originWords: null, originHref: null };

  const dState = !hasPlan ? 'needs-plan' : refusal ? 'refused' : 'ready';
  const eState = !hasPlan ? 'needs-plan' : refusal ? 'refused' : sketch ? 'sketch' : 'ready';
  const drawings = { state: dState, words: W.drawings[dState] };
  const exp = { state: eState, words: W.export[eState] };

  const byId = { brief, candidates, plan: plan_, drawings, export: exp };

  const proceed = {
    brief: candidates.state !== 'none',
    candidates: plan_.state !== 'empty',
    plan: drawings.state === 'ready',
    drawings: exp.state === 'ready',
    export: false,
  };
  const blocked = {
    brief: W.reasons.brief,
    candidates: W.reasons.candidates,
    plan: drawings.words,
    drawings: exp.words,
    export: null,
  };

  const steps = JOURNEY.map((j, i) => {
    const st = byId[j.id];
    const canProceed = proceed[j.id];
    // a failed or expired compose carries its own words, which say more than any rule here can
    const reason = (j.id === 'candidates' && st.failure) ? st.failure : (canProceed ? null : blocked[j.id]);
    return {
      id: j.id,
      surface: j.surface,
      n: i + 1,
      href: formatHash(j.surface, {}, {}),
      state: st.state,
      words: st.words,
      canProceed,
      reason,
      counts: j.id === 'plan' ? plan_.counts : null,
      origin: j.id === 'plan' ? origin.origin : null,
      originWords: j.id === 'plan' ? origin.originWords : null,
      originHref: j.id === 'plan' ? origin.originHref : null,
      stateTerm: j.id === 'plan' ? plan_.stateTerm : null,
    };
  });

  const step = (id) => steps.find((x) => x.id === id);
  const pick = hasPlan ? step('plan')
    : candidates.state !== 'none' ? step('candidates')
      : brief.state === 'stated' ? step('brief') : null;
  const resume = pick ? { id: pick.id, n: pick.n, href: pick.href } : null;

  return {
    steps,
    alternate: { id: 'transcription', surface: 'transcription', joins: ALTERNATE.transcription,
      href: formatHash('transcription', {}, {}) },
    resume,
  };
}
