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
     useSurfaceFilters({ sev: {}, driver: {}, q: {type: 'text'} })

   AN AXIS MAY BE A SELECTION KEY, and the Fault Corpus is why. "Which style's exceptions am
   I reading" is genuinely both a filter and a named record, so `style` appears in a filter
   spec AND in the router's SELECTION_KEYS. The router puts such a key in `selection`, never
   in `params` — so a spec that named one used to read `params.style` forever and get
   `undefined`: the picker snapped back the instant you chose a style, the style-specific
   exception set was never fetched, and clear-all could not clear it. Found by an adversarial
   audit; the surface had shipped with its style filter inert.

   So each axis is routed by where the router actually keeps it. Selection-key axes read from
   `selection` and write with `nav.select`, the rest read from `params`. Writes stay REPLACE
   in both cases, because narrowing a list is a view of the place, not a new place. */

import React from 'react';
import { nav } from '../state/nav.js';
import { SELECTION_KEYS } from '../router.js';

const isSelectionAxis = (k) => SELECTION_KEYS.includes(k);

export function useSurfaceFilters(spec) {
  const place = React.useSyncExternalStore(nav.subscribe, nav.get);
  const keys = React.useMemo(() => Object.keys(spec || {}), [spec]);

  const values = React.useMemo(() => {
    const out = {};
    keys.forEach((k) => {
      const raw = isSelectionAxis(k) ? place.selection[k] : place.params[k];
      const kind = (spec[k] || {}).type;
      if (kind === 'bool') out[k] = raw === '1' || raw === 'true' || raw === true;
      else out[k] = raw == null ? null : raw;
    });
    return out;
  }, [place.params, place.selection, keys, spec]);

  const set = React.useCallback((axis, value) => {
    const kind = (spec[axis] || {}).type;
    const v = kind === 'bool'
      ? (value ? '1' : null)
      : (value == null || value === '' ? null : String(value));
    if (isSelectionAxis(axis)) nav.select({ [axis]: v }, { replace: true });
    else nav.setParams({ [axis]: v });
  }, [spec]);

  /* The idiom this replaces: click the chip that is on, and it goes off. */
  const toggle = React.useCallback((axis, value) => {
    const raw = isSelectionAxis(axis) ? place.selection[axis] : place.params[axis];
    const current = raw == null ? null : String(raw);
    set(axis, current === String(value) ? null : value);
  }, [place.params, place.selection, set]);

  const clear = React.useCallback(() => {
    const params = {};
    const sel = {};
    // A reading is not a filter: clearing must not switch the map back to the tree.
    keys.filter((k) => !(spec[k] || {}).widens)
      .forEach((k) => { (isSelectionAxis(k) ? sel : params)[k] = null; });
    if (Object.keys(sel).length) nav.select(sel, { replace: true });
    if (Object.keys(params).length) nav.setParams(params);
  }, [keys, spec]);

  /* How many axes are NARROWING what you see. A boolean that is off is not a filter;
     neither is an axis nobody has touched. This is the number the strip prints, and the
     reason it prints it is that a filter you have forgotten is worse than no filter —
     it makes a short list look like the whole corpus.

     `widens: true` in the spec marks a control that does the opposite, and it exists because
     the counter was lying on two surfaces: the Kit's `all` shows every slot rather than the
     specified ones, so turning it ON printed "1 narrowing" against the longest list the
     surface can draw, and the Phylogeny's `view=map` is a choice of reading rather than a
     filter at all — switching to the map printed "1 narrowing", and the strip's own clear
     button then silently threw you back to the tree. Both found by an adversarial audit. */
  const activeCount = keys.reduce((n, k) => {
    if ((spec[k] || {}).widens) return n;
    const v = values[k];
    if (v == null || v === '' || v === false) return n;
    return n + 1;
  }, 0);

  return { values, set, toggle, clear, activeCount, params: place.params };
}
