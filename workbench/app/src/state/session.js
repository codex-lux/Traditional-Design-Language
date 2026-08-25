/* Session state shared across surfaces: the brief being drafted, the current compose
   job and its result, and the rail's conversation. Same external-store pattern as
   planDoc; the brief survives a refresh, the job result does not (the server holds it
   for 30 minutes and the job id is kept, so it can be re-fetched). */

const KEY = 'tdl-workbench-session';
let state = { brief: null, jobId: null, result: null, progress: [], railTurns: [] };
const listeners = new Set();

try {
  const saved = JSON.parse(localStorage.getItem(KEY) || 'null');
  if (saved) state = { ...state, brief: saved.brief || null, jobId: saved.jobId || null };
} catch { /* start empty */ }

function emit() {
  try {
    localStorage.setItem(KEY, JSON.stringify({ brief: state.brief, jobId: state.jobId }));
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
