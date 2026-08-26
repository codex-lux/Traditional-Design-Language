/* Filters, held in the URL rather than in twelve copies of the same useState.

   Two things were wrong before this, and they compounded. Every surface hand-rolled
   `setX(x === v ? null : v)` — the same four tokens, twelve times, each free to drift —
   and the state died the moment you navigated away, so filtering the fault list, going to
   read a style, and coming back meant setting it up again. There was one clear-all in the
   whole product, hand-built on one surface.

   Putting them in the query string fixes both at once and buys a third thing: a filtered
   view is now a link. "The serious faults driven by budget" is a URL somebody can send.

   Filters REPLACE the history entry rather than pushing one — chipping through four chips
   should not cost four presses of the back button. The place is what pushes.

   The spec names the axes so the store knows what to clear and what to count:
     useSurfaceFilters({ sev: {}, driver: {}, q: {type: 'text'} }) */

import React from 'react';
import { nav } from '../state/nav.js';

export function useSurfaceFilters(spec) {
  const place = React.useSyncExternalStore(nav.subscribe, nav.get);
  const keys = React.useMemo(() => Object.keys(spec || {}), [spec]);

  const values = React.useMemo(() => {
    const out = {};
    keys.forEach((k) => {
      const raw = place.params[k];
      const kind = (spec[k] || {}).type;
      if (kind === 'bool') out[k] = raw === '1' || raw === 'true';
      else out[k] = raw == null ? null : raw;
    });
    return out;
  }, [place.params, keys, spec]);

  const set = React.useCallback((axis, value) => {
    const kind = (spec[axis] || {}).type;
    if (kind === 'bool') nav.setParams({ [axis]: value ? '1' : null });
    else nav.setParams({ [axis]: value == null || value === '' ? null : String(value) });
  }, [spec]);

  /* The idiom this replaces: click the chip that is on, and it goes off. */
  const toggle = React.useCallback((axis, value) => {
    const current = place.params[axis] == null ? null : place.params[axis];
    set(axis, current === String(value) ? null : value);
  }, [place.params, set]);

  const clear = React.useCallback(() => {
    const patch = {};
    keys.forEach((k) => { patch[k] = null; });
    nav.setParams(patch);
  }, [keys]);

  /* How many axes are narrowing what you see. A boolean that is off is not a filter;
     neither is an axis nobody has touched. This is the number the strip prints, and the
     reason it prints it is that a filter you have forgotten is worse than no filter —
     it makes a short list look like the whole corpus. */
  const activeCount = keys.reduce((n, k) => {
    const v = values[k];
    if (v == null || v === '' || v === false) return n;
    return n + 1;
  }, 0);

  return { values, set, toggle, clear, activeCount, params: place.params };
}
