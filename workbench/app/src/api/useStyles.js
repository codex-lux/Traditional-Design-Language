/* The style list, fetched once for the whole app.

   Six surfaces each called api.styles({limit: 200}) on mount and each kept its own copy.
   The GET cache in client.js meant only one request went out, but every surface still
   held its own array and sorted it its own way — two of them by id, one not at all, so
   the same 164 styles came out in different orders depending which surface you were on.

   One hook, one order, names included. The id alone was what the <select>s showed, which
   asked a reader to know that `english-georgian-country-house` is the country house — the
   name is right there in the record. */

import React from 'react';
import { api } from './client.js';

let cache = null;      // resolved [{id, name, rank}]
let inflight = null;

function load() {
  if (cache) return Promise.resolve(cache);
  if (!inflight) {
    inflight = api.styles({ limit: 250 })
      .then((r) => {
        cache = (r.results || [])
          .map((s) => ({ id: s.id, name: s.name || s.id, rank: s.rank }))
          .sort((a, b) => a.name.localeCompare(b.name));
        return cache;
      })
      .catch(() => {
        inflight = null;         // let a later mount try again
        return [];
      });
  }
  return inflight;
}

export function useStyles() {
  const [styles, setStyles] = React.useState(cache || []);
  React.useEffect(() => {
    let live = true;
    load().then((s) => { if (live) setStyles(s); });
    return () => { live = false; };
  }, []);
  return styles;
}
