/* The style list, fetched once for the whole app.

   Six surfaces each called api.styles({limit: 200}) on mount and each kept its own copy.
   The GET cache in client.js meant only one request went out, but every surface still
   held its own array and sorted it its own way — two of them by id, one not at all, so
   the same 164 styles came out in different orders depending which surface you were on.

   One hook, one order, names included. The id alone was what the <select>s showed, which
   asked a reader to know that `english-georgian-country-house` is the country house — the
   name is right there in the record.

   A FAILURE IS REPORTED, NOT RETURNED AS AN EMPTY CORPUS. The catch used to `return []`,
   which every StylePicker then rendered as "no styles" — indistinguishable from a corpus
   containing none, and silent. That is the same swallow this session found in parseCite and
   fixed, reintroduced in a new shared cache; an adversarial audit caught it. Callers get the
   error and can say the list could not be read. */

import React from 'react';
import { api } from './client.js';

let cache = null;      // resolved [{id, name, rank}]
let inflight = null;
let failure = null;
const listeners = new Set();
const emit = () => listeners.forEach((fn) => fn());

function load() {
  if (cache) return Promise.resolve(cache);
  if (!inflight) {
    inflight = api.styles({ limit: 250 })
      .then((r) => {
        cache = (r.results || [])
          .map((s) => ({ id: s.id, name: s.name || s.id, rank: s.rank }))
          .sort((a, b) => a.name.localeCompare(b.name));
        failure = null;
        emit();
        return cache;
      })
      .catch((e) => {
        inflight = null;         // let a later mount try again
        failure = e;
        emit();
        return [];
      });
  }
  return inflight;
}

/* → {styles, failed}. `failed` is the Error, so a caller can name what went wrong rather
   than drawing an empty list. */
export function useStyles() {
  const [, bump] = React.useReducer((n) => n + 1, 0);
  React.useEffect(() => {
    listeners.add(bump);
    load();
    return () => { listeners.delete(bump); };
  }, []);
  return { styles: cache || [], failed: failure };
}
