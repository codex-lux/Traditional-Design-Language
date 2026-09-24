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

export function useGlossary() {
  const s = React.useSyncExternalStore(store.subscribe, store.get);
  React.useEffect(() => { store.load(); }, []);
  return React.useMemo(() => ({
    status: s.status,
    lookup: s.status === 'ready' ? s.value : null,
    error: s.error,
  }), [s]);
}
