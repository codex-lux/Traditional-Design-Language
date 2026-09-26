/* ONE READ OF ONE CORPUS DOCUMENT FOR THE WHOLE APP, WITH THREE STATES AND NEVER TWO (WP-14.8).

   `api/useStyles.js` is the idiom: fetched once, shared by every component that asks, and a
   failure REPORTED rather than returned as an empty result — that file records why, because
   its first version did `return []` on a failed read and every picker then drew "no styles",
   indistinguishable from a corpus containing none. The glossary and the search index are read
   the same way now (`api/useGlossary.js`, `names/useNames.js`), and a third copy of that
   hand-rolled cache is how the three would come to disagree about what a failure looks like.
   So the state machine is here, once, and it is pure: no React, no `fetch`, nothing but the
   loader it is handed, which is what lets `src/fetchOnce.test.mjs` drive every state under
   `node --test`.

   THE STATES. `loading` until the first read settles; `ready` with the adapted value; `failed`
   with the error. There is no `ready` with nothing in it: the ADAPTER decides what an unusable
   body is and throws, so a 200 whose body carries no terms list is a failure with a reason and
   not an empty glossary — the empty-success this idiom exists to refuse, arriving through a body
   instead of through a catch.

   A LATER READ MAY RETRY A FAILED ONE, as `useStyles` lets a later mount retry: `load()` after
   a failure starts one new read and the state goes back to `loading`. It never retries a read
   in flight and never re-reads a ready one, so a page mounting a hundred readers makes one
   request. */

export function createFetchOnce(loader, adapt = (x) => x) {
  let state = Object.freeze({ status: 'loading', value: null, error: null });
  let inflight = null;
  let started = false;
  const listeners = new Set();

  const publish = (next) => {
    state = Object.freeze(next);
    listeners.forEach((fn) => fn());
  };

  function load() {
    if (state.status === 'ready') return Promise.resolve(state.value);
    if (inflight) return inflight;
    if (started && state.status === 'failed') publish({ status: 'loading', value: null, error: null });
    started = true;
    inflight = Promise.resolve()
      .then(() => loader())
      .then((body) => adapt(body))
      .then(
        (value) => { inflight = null; publish({ status: 'ready', value, error: null }); return value; },
        (error) => {
          inflight = null;
          publish({ status: 'failed', value: null, error: error instanceof Error ? error : new Error(String(error)) });
          return null;
        },
      );
    return inflight;
  }

  return Object.freeze({
    subscribe(fn) { listeners.add(fn); return () => { listeners.delete(fn); }; },
    /* The snapshot. Stable between changes, because `useSyncExternalStore` compares by
       reference and a fresh object per read would render for ever. */
    get() { return state; },
    load,
  });
}
