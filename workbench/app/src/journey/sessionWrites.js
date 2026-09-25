/* WHAT THE SESSION IS TOLD ABOUT A HOUSE'S JOURNEY, SPELLED ONCE (WP-14.10, PRD §G.1).

   Two facts the journey needs were thrown away until this package. A compose job that failed went
   to `error: () => {}` on the Candidate Set's reattach stream, so the step read "composing" for
   ever over a job the server had already given up on; and a plan opened on the bench forgot where
   it came from, so nothing could say which candidate, example or tracing it was. PRD §G.1 names
   the two fields — `session.jobError` and `session.planFrom` — and the table of who writes them.
   This module is every one of those writes, as pure functions over a store that has `set` and
   `pushProgress`, so each can be driven under `node --test` with a hand-built store and the
   surfaces that call them (`BriefIntake`, `CandidateSet`, the bench's example load,
   Transcription's "send to the bench") are left to call and nothing else.

   ONE HANDLER SET FOR EVERY COMPOSE STREAM. `jobEvents` subscribes ONLY to the names it is handed,
   so a name missing at one call site is an event dropped with no error (WP-9.4 found `revised`
   gone that way for a whole package). Two call sites each writing their own object literal is how
   one of them came to hand `error` a no-op while the other showed it. `composeHandlers` is the one
   object both pass, and `src/sse_handlers.test.mjs` drives it event by event and holds both call
   sites to passing it.

   A FAILURE IS RECORDED, NEVER SWALLOWED, AND NEVER INVENTED. The reason is the job's own words
   (`jobs.py` puts `{error: <text>}`; `jobEvents` synthesises `{error: 'stream closed'}` when the
   connection drops before a terminal event). Where the event carries no text, the reason is
   `null` and the journey falls back to its own rule — this file writes no sentence of its own.

   A STREAM THAT CLOSED IS NOT A JOB THAT FAILED FOR GOOD. The job keeps running on the server, so
   `jobId` is kept on a stream failure and the next reattach asks the server: a job still running
   clears the failure (its new stream is the truth), a finished one brings its result, an errored
   one is `failed` with the server's reason and a 404 is `expired`. Only those last two forget the
   job, because only they are the server saying the job is gone.

   Pure: no React, no DOM, no import. */

export const PLAN_FROM_KINDS = Object.freeze(['candidate', 'example', 'traced']);
export const JOB_ERROR_STATES = Object.freeze(['failed', 'expired']);

const str = (v) => (typeof v === 'string' && v.trim() ? v : null);
const isObj = (v) => Boolean(v) && typeof v === 'object' && !Array.isArray(v);
const idx = (v) => (Number.isInteger(v) && v >= 0 ? v : null);

/* A stored `planFrom` or null. A persisted entry comes back through here, so a stale or hostile
   one costs the provenance and never the session. */
export function readPlanFrom(v) {
  if (!isObj(v) || !PLAN_FROM_KINDS.includes(v.kind) || !str(v.planId)) return null;
  return {
    kind: v.kind,
    planId: v.planId,
    jobId: str(v.jobId),
    n: idx(v.n),
    briefName: str(v.briefName),
  };
}

/* A stored `jobError` or null. */
export function readJobError(v) {
  if (!isObj(v) || !JOB_ERROR_STATES.includes(v.state)) return null;
  return { state: v.state, reason: str(v.reason), jobId: str(v.jobId) };
}

/* The `planFrom` a plan opened on the bench carries. `kind` 'candidate' takes the job and the
   0-based index `api.candidatePlan` was called with (the bar shows n + 1); 'example' and
   'traced' take neither. A plan with no id cannot be matched to its origin later (§G's rule is
   `planFrom.planId === plan.id`), so it records nothing rather than a provenance for no plan. */
export function planFromOf(kind, plan, { jobId = null, n = null, briefName = null } = {}) {
  if (!PLAN_FROM_KINDS.includes(kind) || !isObj(plan) || !str(plan.id)) return null;
  const candidate = kind === 'candidate';
  return {
    kind,
    planId: plan.id,
    jobId: candidate ? str(jobId) : null,
    n: candidate ? idx(n) : null,
    briefName: candidate ? str(briefName) : null,
  };
}

/* The NAME of the brief a compose result was made from, or null. The result carries the brief's
   id only (`compose.py`: `"brief": brief.get("id") or brief.get("name")`), so the name is read off
   the drafted brief in the session — and only where that draft IS the brief the result names:
   a draft edited since, or another brief altogether, would put a wrong name on a candidate. */
export function briefNameOf(result, brief) {
  const id = isObj(result) ? str(result.brief) : null;
  if (!id || !isObj(brief) || brief.id !== id) return null;
  return str(brief.name);
}

/* A compose that has just been accepted: everything the last one said is cleared. */
export function composeStart(jobId) {
  return { result: null, progress: [], jobError: null, jobId: str(jobId) };
}

/* A job the stream reports as failed. */
export function jobFailed(jobId, event) {
  const reason = isObj(event) ? str(event.error) : null;
  return { state: 'failed', reason, jobId: str(jobId) };
}

/* The one handler set every compose stream is given. `after` runs a surface's own local
   reaction AFTER the session write (Brief Intake's spinner), and can add nothing to or take
   nothing from what the session is told. */
export function composeHandlers(store, jobId, after = {}) {
  const then = (k, d) => { if (isObj(after) && typeof after[k] === 'function') after[k](d); };
  return {
    stage: (d) => { store.pushProgress(d); then('stage', d); },
    candidate: (d) => { store.pushProgress(d); then('candidate', d); },
    // the loop's second word on a candidate, marked so the journey does not count it again
    revised: (d) => { store.pushProgress({ ...d, revised: true }); then('revised', d); },
    done: (d) => { store.set({ result: d, jobError: null }); then('done', d); },
    error: (d) => { store.set({ jobError: jobFailed(jobId, d) }); then('error', d); },
  };
}

/* What a reattach learns from `GET /api/jobs/<id>`, as the patch it writes and whether a stream
   should be opened. */
export function reattach(jobId, job) {
  const status = isObj(job) ? job.status : null;
  if (status === 'done') return { patch: { result: job.result, jobError: null }, stream: false };
  if (status === 'error') {
    return { patch: { jobId: null, jobError: { state: 'failed', reason: str(job.error), jobId: str(jobId) } },
      stream: false };
  }
  // running or queued: the job is alive, so a failure recorded off a dropped stream is withdrawn
  return { patch: { jobError: null }, stream: true };
}

/* The server no longer knows the job (404). */
export function jobExpired(jobId, reason) {
  return { jobId: null, jobError: { state: 'expired', reason: str(reason), jobId: str(jobId) } };
}
