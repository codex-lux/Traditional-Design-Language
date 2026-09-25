/* The glossary, fetched once for the whole app (WP-14.8, PRD §I.2).

   `useGlossary()` → { status: 'loading' | 'ready' | 'failed', lookup, error }.

   Every definition the workbench shows is a glossary record (ruled 24 Sep 2026), so every
   `Term`, page head and rail description asks this one hook, and `GET /api/glossary` goes out
   once however many of them mount — `api/useStyles.js`'s idiom, whose state machine is
   `api/fetchOnce.js` now so the readers cannot come to disagree about a failure.

   `lookup` IS NULL UNTIL THE GLOSSARY HAS ANSWERED. An empty lookup would answer "missing" for
   every id while the request is still in flight, and a reader that forgot to check `status`
   would print "no entry" over a page whose records are one round trip away — a claim about the
   records made on the strength of a pending request. Null makes that reader fail loudly
   instead. `glossary/termView.js` turns the three states into what a `Term` shows.

   A BODY WITH NO TERMS IS A FAILURE, NOT AN EMPTY GLOSSARY (`api/adapters.js`). */
import React from 'react';
import { api } from './client.js';
import { createFetchOnce } from './fetchOnce.js';
import { adaptGlossary } from './adapters.js';

const store = createFetchOnce(() => api.glossary(), adaptGlossary);

/* `enabled` (default on) exists for the shell alone (WP-14.15). App mounts this hook before it
   knows whether the browser is signed in, and a hook that loads on mount fetched a gated corpus
   route behind the Gate, where PRD §C.3 allows exactly one path to be asked. It also loaded ONCE,
   so the 401 it got there stood as a failure after the reader signed in. The shell passes
   `locked === false`: nothing is asked until the lock is known, and the read happens when the
   Gate opens. Every other caller mounts after that and keeps the default. */
export function useGlossary(enabled = true) {
  const s = React.useSyncExternalStore(store.subscribe, store.get);
  React.useEffect(() => { if (enabled) store.load(); }, [enabled]);
  return React.useMemo(() => ({
    status: s.status,
    lookup: s.status === 'ready' ? s.value : null,
    error: s.error,
  }), [s]);
}
