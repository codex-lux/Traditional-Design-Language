/* Where you are, held in the URL. Same external-store idiom as planDoc and session,
   but the storage is location.hash rather than localStorage — so the back button, a
   refresh, a copied link and a citation are all the same mechanism.

   The snapshot identity is stable between navigations: useSyncExternalStore compares by
   reference, and rebuilding the object on every read would loop forever. */

import { parseHash, formatHash, DEFAULT_SURFACE } from '../router.js';
import { routeCite } from '../citations.js';

const listeners = new Set();
let state = read();

function read() {
  try {
    return parseHash(typeof location === 'undefined' ? '' : location.hash);
  } catch {
    return { surface: DEFAULT_SURFACE, selection: {}, params: {} };
  }
}

function emit() { listeners.forEach((fn) => fn()); }

/* `#/cite/style:craftsman` is an address a machine writes; `#/style/craftsman` is the
   one the app lives at. Rewriting it in place — without a history entry — means a link
   pasted from the rail, a commit message or a chat resolves and then stays resolved, so
   copying the URL back out gives the same place rather than the redirect that reached it.

   Only a citation that actually resolved is rewritten. A broken one is left standing in
   the address bar: it did not navigate anywhere (nav.cite refuses), and quietly replacing
   it with the default surface would disguise a dead link as a working one. */
function canonicalize() {
  if (typeof location === 'undefined' || typeof history === 'undefined') return;
  const hash = location.hash || '';
  if (!hash.startsWith('#/cite/')) return;
  const ref = decodeURIComponent(hash.slice('#/cite/'.length).split('?')[0]);
  if (!routeCite(ref)) return;
  const want = formatHash(state.surface, state.selection, state.params);
  if (want !== hash && history.replaceState) history.replaceState(null, '', want);
}

function sync() {
  const next = read();
  const same = next.surface === state.surface
    && JSON.stringify(next.selection) === JSON.stringify(state.selection)
    && JSON.stringify(next.params) === JSON.stringify(state.params);
  if (same) { canonicalize(); return; }
  state = next;
  canonicalize();
  emit();
}

if (typeof window !== 'undefined') {
  window.addEventListener('hashchange', sync);
  canonicalize();          // a cold load straight onto a #/cite/ link
}

/* push for a change of place (the back button should undo it); replace for a change of
   view on the same place (chipping through filters must not fill the history). */
function write(surface, selection, params, replace) {
  const hash = formatHash(surface, selection, params);
  if (typeof location === 'undefined') return;
  if (hash === location.hash) { sync(); return; }
  if (replace && typeof history !== 'undefined' && history.replaceState) {
    history.replaceState(null, '', hash);
    sync();
  } else {
    location.hash = hash;                 // fires hashchange → sync()
  }
}

export const nav = {
  subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); },
  get() { return state; },

  /* Move to a surface. Selection and filters do not follow you across a surface
     boundary — carrying one surface's filters onto the next is how the strip got
     confusing in the first place. */
  go(surface, selection) {
    write(surface, selection || {}, {}, false);
  },

  /* Stay on this surface, name a different record. */
  select(patch) {
    write(state.surface, { ...state.selection, ...patch }, state.params, false);
  },

  /* Filters. Replace by default: a filter is a view of the place, not a new place.
     A null or false value clears the key. */
  setParams(patch, opts) {
    const next = { ...state.params };
    Object.entries(patch || {}).forEach(([k, v]) => {
      if (v == null || v === '' || v === false) delete next[k];
      else next[k] = v;
    });
    write(state.surface, state.selection, next, !(opts && opts.push));
  },

  clearParams() {
    write(state.surface, state.selection, {}, true);
  },

  /* A citation navigates. This is the one entry point the rail, the findings and every
     cross-surface link share. An unresolvable ref does nothing at all — landing the
     reader somewhere arbitrary is worse than not moving, and the server has already
     downgraded anything it could not validate to plain text before it got here. */
  cite(ref) {
    const target = routeCite(ref);
    if (!target) return;
    write(target.surface, target.selection || {}, {}, false);
  },
};
