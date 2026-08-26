/* The React side of the coastline tiers: which outline is on the plate right now.

   Split from `coastTiers.js` so that file imports nothing from node_modules — see the
   note there. Everything below needs React; everything there does not. */
import React from 'react';
import { TIERS, BY_DETAIL, tierFor, chooseTier } from './coastTiers.js';
import { COAST_COARSE } from '../../data/coastlines.js';

/* Module-scope, not component state: the fine tier is a megabyte and remounting the map
   — every trip to the tree reading and back — must not fetch it again. */
const loaded = new Map([['coarse', COAST_COARSE]]);
const failed = new Map();
const inflight = new Map();

/* The tier the view deserves, the tier that is actually on the plate, and whether the
   difference is a fetch in flight or a fetch that failed. Never conflates the two: a
   coastline that could not be fetched is a stated gap, not a coarser drawing passed off
   as the right one. */
export function useCoastline(width) {
  const wanted = tierFor(width);
  const [, bump] = React.useReducer((n) => n + 1, 0);

  React.useEffect(() => {
    if (loaded.has(wanted.name) || failed.has(wanted.name)) return;
    if (inflight.has(wanted.name)) return;
    const p = wanted.load().then(
      (tier) => { loaded.set(wanted.name, tier); inflight.delete(wanted.name); bump(); },
      (err) => {
        // Recorded, not retried in a loop: a chunk that will not load will not load on
        // the next pointer move either, and a hundred failed fetches a second is worse
        // than a coarse coastline.
        failed.set(wanted.name, err && err.message ? err.message : String(err));
        inflight.delete(wanted.name);
        bump();
      },
    );
    inflight.set(wanted.name, p);
  }, [wanted.name]);

  /* Best available means NEAREST TO WANTED on the ladder — not the coarsest that will do,
     and not the finest in hand either. Both of those were tried and both were wrong.

     The first version refused any tier finer than the scale asked for, so zooming past the
     medium band and back out drew 110m facets while the 10m data sat in the module cache:
     the legend reported the coarse tier as what the scale deserved, and it was not.
     Correcting that to "finest in hand" over-corrected — the e2e walk caught it —
     because once the fine tier is fetched, returning to a hemisphere view mounted 827
     rings including the 25,000-point Afro-Eurasia path, for a drawing indistinguishable at
     0.134 degrees per pixel from one with 42.

     Nearest, with a tie going to the FINER tier, gives the right answer in both: at a
     hemisphere the wanted tier is loaded and is used; at forty degrees, with medium not
     fetched and fine in hand, fine is one rung away and coarse is one rung away, and the
     finer of the two is the honest one to draw. */
  const wantIdx = BY_DETAIL.indexOf(wanted);
  const inHand = BY_DETAIL.filter((t) => loaded.has(t.name));
  const drawn = inHand.slice().sort((a, b) => {
    const da = Math.abs(BY_DETAIL.indexOf(a) - wantIdx);
    const db = Math.abs(BY_DETAIL.indexOf(b) - wantIdx);
    return da - db || BY_DETAIL.indexOf(a) - BY_DETAIL.indexOf(b);   // tie → the finer
  })[0] || TIERS[0];
  return {
    wanted,
    drawn: loaded.get(drawn.name) || COAST_COARSE,
    drawnName: drawn.name,
    pending: drawn.name !== wanted.name && !failed.has(wanted.name) && !loaded.has(wanted.name),
    failed: failed.get(wanted.name) || null,
    /* A failed fetch is recorded rather than retried in a loop, but it must not be a life
       sentence: the chunk filename is content-hashed, so ANY redeploy 404s it for every
       tab that is already open, and without this the map is stuck on a coarser outline
       until the reader thinks to reload the whole page. The legend offers this; nothing
       calls it on a timer. */
    retry: () => { failed.delete(wanted.name); bump(); },
  };
}
