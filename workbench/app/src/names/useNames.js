/* The names of things, fetched once for the whole app (WP-14.8, PRD §I.3).

   `useNames()` → { status, index, error, nameFor(cite) }.

   `names/names.js` turns a citation into what a person calls the thing, over the entries
   `GET /api/search/index` already serves; this is its React hook. The index is the palette's
   own (`CommandPalette.jsx` reads the same endpoint, and the GET cache in `api/client.js` makes
   the two one request), so a link and a search result can never name one record two ways.

   While the index is loading, or if it could not be read, `nameFor` still answers — with the
   citation itself, `resolved: false`, which is `names.js`'s rule for a name it does not hold:
   the reader sees the id and can tell it is one. It never guesses a name from the id. */
import React from 'react';
import { api } from '../api/client.js';
import { createFetchOnce } from '../api/fetchOnce.js';
import { adaptSearchIndex } from '../api/adapters.js';
import { nameFor } from './names.js';

const store = createFetchOnce(() => api.searchIndex(), adaptSearchIndex);
const EMPTY = new Map();

/* `enabled`: see `api/useGlossary.js` — the shell's lock, and nothing else. */
export function useNames(enabled = true) {
  const s = React.useSyncExternalStore(store.subscribe, store.get);
  React.useEffect(() => { if (enabled) store.load(); }, [enabled]);
  return React.useMemo(() => {
    const index = s.status === 'ready' ? s.value : EMPTY;
    return { status: s.status, index, error: s.error, nameFor: (cite) => nameFor(cite, index) };
  }, [s]);
}
