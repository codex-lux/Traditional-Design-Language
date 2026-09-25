/* Session state shared across surfaces: the brief being drafted, the current compose
   job and its result, and the rail's conversation. Same external-store pattern as
   planDoc; the brief survives a refresh, the job result does not (the server holds it
   for 30 minutes and the job id is kept, so it can be re-fetched).

   WP-14.10 (PRD §G.1) ADDS TWO FACTS THE HOUSE JOURNEY READS, AND BOTH SURVIVE A REFRESH:

     planFrom  where the plan on the bench came from — candidate k of a job, an example, a
               tracing — or null. It names the plan by id, and the journey trusts it only while
               `planFrom.planId` is the id of the plan on the bench, so a plan loaded any other
               way reads "origin not recorded" rather than borrowing another plan's origin.
     jobError  a compose job that failed or expired, with the job's own reason, or null.

   The key is unchanged (`'tdl-workbench-session'`, which PRD §J.4 forbids renaming), and the
   persisted object is `{ brief, jobId, planFrom, jobError }`. Both new fields are read back
   through `journey/sessionWrites.js`'s sanitisers, so an entry written by an older build, or a
   hostile one, costs that field and not the session. Every WRITE of either field is spelled in
   that same module; this file only holds them. */
import { readPlanFrom, readJobError, planFromOf } from '../journey/sessionWrites.js';

const KEY = 'tdl-workbench-session';
let state = { brief: null, jobId: null, result: null, progress: [], railTurns: [],
  planFrom: null, jobError: null };
const listeners = new Set();

try {
  const saved = JSON.parse(localStorage.getItem(KEY) || 'null');
  if (saved) {
    state = { ...state, brief: saved.brief || null, jobId: saved.jobId || null,
      planFrom: readPlanFrom(saved.planFrom), jobError: readJobError(saved.jobError) };
  }
} catch { /* start empty */ }

function emit() {
  try {
    localStorage.setItem(KEY, JSON.stringify({ brief: state.brief, jobId: state.jobId,
      planFrom: state.planFrom, jobError: state.jobError }));
  } catch { /* best effort */ }
  listeners.forEach((fn) => fn());
}

export const session = {
  subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); },
  get() { return state; },
  set(patch) { state = { ...state, ...patch }; emit(); },
  pushProgress(ev) { state = { ...state, progress: [...state.progress, ev] }; emit(); },
  pushTurn(turn) { state = { ...state, railTurns: [...state.railTurns, turn] }; emit(); },
  patchLastTurn(patch) {
    const t = state.railTurns.slice();
    if (!t.length) return;
    t[t.length - 1] = typeof patch === 'function' ? patch(t[t.length - 1]) : { ...t[t.length - 1], ...patch };
    state = { ...state, railTurns: t };
    emit();
  },
};

/* Record where a plan put on the bench came from, BEFORE it is loaded, so the journey's first
   look at the new plan already knows its origin. One call for every surface that puts a plan on
   the bench — the bench's example load and Transcription's "send to the bench" are one line each,
   by PRD §J.3's budget — and it returns the plan, so a caller can load what it recorded. */
export function recordPlanFrom(kind, plan, extra) {
  session.set({ planFrom: planFromOf(kind, plan, extra) });
  return plan;
}
