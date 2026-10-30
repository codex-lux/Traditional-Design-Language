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
   only where `evalIsOf(lastEval, plan.id, planFrom)` (the plan's id AND where it came from,
   16 Oct 2026: two composes of one parti share an id). Otherwise the plan is UNEVALUATED — never
   "0 fatal", which would be a pass nobody measured. `evalPlanOf` is the ONE reader of which plan
   an evaluation was of (WP-14.20): the evaluate route states it at the top of its response, before
   the early return a check that ERRORED takes — `plan_check` writes the id only on a completed
   check, so an errored check carrying `placement_refused` used to name no plan, read here as
   "not yet evaluated", and left the drawings and the export as ready links over a refused house
   (`oq/an-evaluation-whose-check-errored-names-no-plan`). The check's own id is read second, for
   an evaluation from anywhere that does not state the top-level one.

   THREE COUNTS, NEVER ONE. Fatal, serious and unjudged are three numbers and stay three: an
   unjudged constraint is not a failure and not a pass, and adding it to either would say
   something about the house nobody measured. A severity key absent from a completed check is a
   real zero (`plan_check` writes a key only when a finding carries that severity); an absent
   `counts` object or an absent `unjudged` is NOT a zero, and reads as not counted.

   "k OF N" WHERE THE STREAM STATES N, AND "k SCORED" WHERE IT DOES NOT (WP-14.25). Until WP-14.19
   the compose job's events carried an arrival index and no total, so N was not knowable and was
   not printed. Every `stage` event now carries `total` -- the length of `compose.considered`, the
   one list the composer works through -- and every diagram in it is heard from exactly once,
   as a `candidate` event or as a `dropped` stage, each carrying `considered`, the running count
   (`workbench/server/jobs.py`). So k is the stream's own `considered` and N its own `total`, both
   read and neither counted here; a diagram the lot drops is considered and never scored, which is
   why k counts it and "scored" would not. A stream stating no total (a job from before the field)
   keeps the old words, and N is never guessed.

   Every word the journey shows is in JOURNEY_WORDS, one spelling. The four that are also glossary
   terms (refused, fatal, serious, unjudged) are named in JOURNEY_TERMS so the bar can render them as
   `Term`s, and `journey.test.mjs` holds each word to its record's `term` wherever the records are
   on the tree.

   Pure: no React, no DOM. */
import { evaluateRefusal, placementRefusal, sketchOf } from '../sheet/refusal.js';
import { formatHash } from '../router.js';
import { standingOf, standingOfSet } from '../candidateStanding.js';

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
    composing: (k, total) => (Number.isInteger(total) && total > 0
      ? `composing · ${k} of ${total}`
      : `composing · ${k} scored`),
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
  /* What the Candidate Set says about the column a reader has picked: a click selects, and the
     way on to the bench is a separate act, so each state of the pick says which act is available.
     `held` is the refusal's own verdict in a clause (never a sentence about a fact written here);
     the facts it follows are the refusal's. */
  selection: Object.freeze({
    none: 'select a candidate to open it on the bench',
    open: (name) => `open ${name} on the bench`,
    // not placed by the composer's loop, or placed with no verdict this app can read: the bench
    // places the house and may refuse it, which the link should not promise away
    unjudged: (name) => `open ${name} · not judged for drawing, so it may be refused`,
    refused: (name, why) => `${name} is refused, so it cannot be drawn${why ? ` · ${why}` : ''}`,
    held: (kind, k) => (kind === 'infeasible' ? (k === 1 ? 'cannot hold' : 'cannot all hold') : 'not held'),
    // nothing in the set can be put on the bench: the act the bar and the strip name is not there
    allRefused: 'every candidate is refused · change the brief or the parti',
    empty: 'no candidate was returned · the brief is what changes',
    opening: 'opening…',
    gone: 'could not open · the server no longer keeps this compose',
    failed: (why) => `could not open it${why ? `: ${why}` : ''}`,
    tallyUnjudged: (k, of) => (Number.isInteger(of) && of >= k ? `${k} of ${of} not judged for drawing` : `${k} not judged for drawing`),
  }),
  separator: ' · ',
  // WP-17.6: a diagram the pool-fill did not reach is named, never left out in silence. WHY it was
  // not reached is the bound the composer says stopped the fill, worded by a glossary record
  // (`candidateOrder.POOL_STOP_TERMS`, the audit's finding 26): this word claims no cause, and is
  // what is said alone where the result names no bound this app knows
  notPlaced: 'not placed',
  next: 'next',   // the bar's link on to the following step (WP-14.10)
  reasons: Object.freeze({
    brief: 'compose the brief first',
    candidates: 'open a candidate on the bench',
    // the pick is the reader's and the bench holds another: Next goes to the plan on the bench
    picked: 'open the candidate you picked on the bench',
    // no longer than `picked` above: the bar's Next is one unbroken run that jumps to a row of its
    // own when it does not fit beside the steps, and the longer words did exactly that at 1680 px
    // with a plan on the bench -- the page moved 21 px under the pointer on every pick that changed
    // between a refused column and an open one (measured, 16 Oct 2026)
    pickedRefused: 'this pick is refused and cannot be drawn',
    allRefused: 'every candidate is refused, so none can be drawn',
    empty: 'no candidate was returned',
  }),
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

/* Which plan an evaluation was of: the route's own statement first, then the check's. It answers
   only the id half; `evalIsOf` below is the matcher every site asks, and it reads this. */
export function evalPlanOf(lastEval) {
  if (!isObj(lastEval)) return null;
  return str(lastEval.plan) ?? (isObj(lastEval.check) ? str(lastEval.check.plan) : null);
}

/* WHERE AN EVALUATION'S PLAN CAME FROM, as a key (audit follow-up, 16 Oct 2026; ruled app-side by
   Lucas). A composed plan's id is `{parti}-{briefId}`, so the same parti opened from a later
   compose, or from another candidate slot, is a different house with the same id; an evaluation
   matched to a plan by id alone survived that swap and sat beside the new record (up to one solve,
   about 25 s) with the old house's counts. An evaluation is therefore of a plan AND where that
   plan came from, and the origin it names is the one the bench held when the request was sent --
   not when the answer landed, which can be after the reader has opened something else.

   The key is `planFrom` as `originOf` reads it (trusted only where it names this plan): the kind,
   the job and the slot for a candidate; the kind alone for an example or a tracing; `''` where no
   origin is recorded. An evaluation that carries no stamp is of `''`, so it is never taken for
   the evaluation of a plan whose origin is recorded. The id is unchanged: ids are stable by rule
   and cited in files, and nothing here edits one. */
export function originKeyOf(planId, planFrom) {
  const pf = isObj(planFrom) ? planFrom : null;
  if (!pf || !str(planId) || pf.planId !== planId || !str(pf.kind)) return '';
  const n = Number.isInteger(pf.n) && pf.n >= 0 ? pf.n : '';
  return [pf.kind, str(pf.jobId) ?? '', n].join('|');
}

/* The origin key an evaluation was stamped with (`stampEval`), `''` for none. */
export function evalOriginOf(lastEval) {
  return isObj(lastEval) && typeof lastEval.evaluated_from === 'string' ? lastEval.evaluated_from : '';
}

/* An evaluation response, marked with the plan and origin it was REQUESTED for. The one writer. */
export function stampEval(res, planId, planFrom) {
  if (!isObj(res)) return res;
  return { ...res, evaluated_from: originKeyOf(planId, planFrom) };
}

/* An evaluation without the stamp, for anything that leaves the app: the stamp is this app's
   bookkeeping about WHERE the request was asked from, and a saved check report is the server's
   answer and nothing else. */
export function unstampEval(ev) {
  if (!isObj(ev) || !Object.prototype.hasOwnProperty.call(ev, 'evaluated_from')) return ev;
  const { evaluated_from: _stamp, ...rest } = ev;
  return rest;
}

/* Is this evaluation of this plan, from where it now came? The one reader of "does an evaluation
   belong to the plan on the bench": the stale-evaluation clear in `App.jsx`, the journey below
   and the assistant's context all ask this and nothing else, so they cannot disagree. */
export function evalIsOf(lastEval, planId, planFrom) {
  return Boolean(str(planId)) && evalPlanOf(lastEval) === planId
    && evalOriginOf(lastEval) === originKeyOf(planId, planFrom);
}

/* Does an answer that was requested for one plan and origin still belong on the bench? A request
   takes up to a solve (about 25 s) and the reader can open another house meanwhile; the answer
   then lands against a plan it was not of. The bench filed it anyway and the shell cleared it only
   at the NEXT plan change, so the bench drew the old house's verdict beside the new record until
   the new record's own debounce fired. The ids and the origin keys are the same two readers
   `evalIsOf` uses, taken at request time and at answer time. */
export function answerIsForHere(requestedId, requestedFrom, nowId, nowFrom) {
  return Boolean(str(requestedId)) && requestedId === nowId
    && originKeyOf(requestedId, requestedFrom) === originKeyOf(nowId, nowFrom);
}

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

/* How far a compose has got, from the stream's own events: `scored`, the candidate events heard
   (a revision is the loop's second word on one already counted, and is not counted again);
   `considered`, the highest running count any event states; `total`, the N the stage events
   state. Each is null where no event states it -- never a zero, which would be a count nobody
   made. */
export function composeProgress(progress) {
  const evs = Array.isArray(progress) ? progress.filter(isObj) : [];
  const nat = (v) => (Number.isInteger(v) && v >= 0 ? v : null);
  const scored = evs.filter((e) => count(e.n) !== null && !e.revised).length;
  const totals = evs.map((e) => nat(e.total)).filter((t) => t !== null && t > 0);
  const heard = evs.map((e) => nat(e.considered)).filter((c) => c !== null);
  return {
    scored,
    considered: heard.length ? Math.max(...heard) : null,
    total: totals.length ? totals[totals.length - 1] : null,
  };
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
    const p = composeProgress(session.progress);
    const k = p.total !== null && p.considered !== null ? p.considered : p.scored;
    return { state: 'composing', words: W.candidates.composing(k, p.total) };
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

/* The candidate a reader has picked on the Candidate Set, or null: the address's numeric
   `candidate` key (an index in the SERVER's order), and only on the surface where a pick means
   something. Every caller that builds the journey for a bar passes this, so the bar and the
   shell cannot read two different picks. */
export function pickedCandidate(surface, selection) {
  if (surface !== 'candidates' || !isObj(selection)) return null;
  const n = selection.candidate;
  return Number.isInteger(n) && n >= 0 ? n : null;
}

/* Why the candidates step cannot go on, in words a reader can follow. The step's one reason used
   to be "open a candidate on the bench", which is an instruction with nothing behind it when no
   candidate was returned or every one was turned down by the type's own facts -- the screen this
   change exists for, reached again by a reader told to do what could not be done. */
function candidatesReason(session, picked) {
  const result = isObj(session.result) && Array.isArray(session.result.candidates) ? session.result : null;
  if (!result) return W.reasons.candidates;
  const set = standingOfSet(result.candidates);
  if (set.total === 0) return W.reasons.empty;
  if (set.openable === 0) return W.reasons.allRefused;
  if (picked !== null && picked < set.total) {
    return standingOf(result.candidates[picked]) === 'refused' ? W.reasons.pickedRefused : W.reasons.picked;
  }
  return W.reasons.candidates;
}

export function journeyState({ session, plan, lastEval, picked = null } = {}) {
  const s = isObj(session) ? session : {};
  const hasPlan = isObj(plan);
  const planId = hasPlan ? str(plan.id) : null;
  // the evaluation of THIS plan, or nothing
  const ev = planId && isObj(lastEval) && isObj(lastEval.check) && evalIsOf(lastEval, planId, s.planFrom)
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

  /* A PLAN ON THE BENCH LEAVES THE CANDIDATES STEP ONLY WHERE IT CAME FROM THIS COMPOSE. The bench
     keeps its record across a refresh and across a whole compose, so an example opened last week
     is "a plan on the bench" when the candidates arrive -- and "next: Plan" then carried a reader
     from the candidate they had just picked to that example, refused by the type's own facts,
     under a bar that said the plan was theirs to continue with. The origin is the session's own
     record of where the plan came from (`planFrom`, trusted only where it names this plan), and a
     candidate counts only for the job the Candidate Set is showing: the example, a tracing and an
     earlier job's candidate are all places a plan can come from and none of them is the one picked
     here. The step's own reason ("open a candidate on the bench") is what the bar then says. */
  const originJob = hasPlan && origin.origin && origin.origin.kind === 'candidate' ? str(origin.origin.jobId) : null;
  const fromThisCompose = Boolean(originJob && originJob === str(s.jobId));
  /* AND WHERE THE READER HAS PICKED A CANDIDATE, ONLY THE ONE THEY PICKED. The compose-level test
     above stops a stale example; it cannot tell candidate 0 on the bench from the candidate 3 the
     reader has just selected, and Next then carried them to the plan of the one they did not pick
     -- the same complaint (a click that was supposed to lead to the drawings) with the right job.
     `picked` is the address's pick on the Candidate Set (`pickedCandidate`) and null everywhere a
     pick means nothing, so a reader who comes back to the set with no pick in the address is not
     held. The index the bench's plan was fetched at is `planFrom.n`, recorded at the open. */
  const isThePick = picked === null || (origin.origin && origin.origin.n === picked);
  const proceed = {
    brief: candidates.state !== 'none',
    candidates: plan_.state !== 'empty' && fromThisCompose && Boolean(isThePick),
    plan: drawings.state === 'ready',
    drawings: exp.state === 'ready',
    export: false,
  };
  const blocked = {
    brief: W.reasons.brief,
    candidates: candidatesReason(s, picked),
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
