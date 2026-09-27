/* What this browser remembers about its reader, and nothing it may decide (WP-14.8, PRD §I.10).

   THE RULE UNDER EVERY LINE: THE URL DECIDES WHAT IS READ; THIS STORE ONLY OFFERS. A bare
   `#/style` shows the Styles index and never the style this browser last read, because a link
   somebody pastes must open the same page for them as for the sender. So nothing here is read
   into a URL, a selection or `useFilters`, and this module imports none of them —
   `src/prefs.test.mjs` reads the source to keep it so. What it holds are three kinds of
   convenience a reader would be annoyed to lose and would be misled by if they travelled:

     styleInHand  the style this browser last read in full, OFFERED by the rail and the indexes
                  as a link, never applied
     seen         things shown once: `front-door`, and `head:<termId>` for a page head's
                  "how to read this page", open on the first visit and folded afterwards
     folds        a reader's own open-or-closed choice for a disclosure, which outranks `seen`

   `state/layout.js`'s idiom, which it records the reasons for: read once at load; a corrupt or
   absent entry gives the defaults and never a broken shell; a write that fails (a private
   window, a full quota) keeps a working in-memory store, so the reader loses the memory and not
   the page. Each key is checked on read BY ITSELF, so one malformed key costs that key and not
   the other two. A package adding a `seen` or `folds` key names it in its report. */

const KEY = 'tdl-workbench-prefs';

const plainObject = (o) => Boolean(o) && typeof o === 'object' && !Array.isArray(o);
const isKey = (k) => typeof k === 'string' && k.trim() !== '';

function defaults() {
  return { styleInHand: null, seen: {}, folds: {} };
}

/* Anything → a well-formed prefs object. Exported so the three shapes a hostile or stale entry
   can take are tested directly rather than through localStorage. */
export function sanitize(raw) {
  const out = defaults();
  if (!plainObject(raw)) return out;
  if (isKey(raw.styleInHand)) out.styleInHand = raw.styleInHand;
  if (plainObject(raw.seen)) {
    for (const [k, v] of Object.entries(raw.seen)) if (isKey(k) && v === true) out.seen[k] = true;
  }
  if (plainObject(raw.folds)) {
    for (const [k, v] of Object.entries(raw.folds)) if (isKey(k) && typeof v === 'boolean') out.folds[k] = v;
  }
  return out;
}

function readStored() {
  try {
    return sanitize(JSON.parse(localStorage.getItem(KEY) || 'null'));
  } catch {
    return defaults();       // a corrupt entry, or no localStorage at all
  }
}

let state = Object.freeze(readStored());
const listeners = new Set();

function commit(next) {
  state = Object.freeze(next);
  try {
    localStorage.setItem(KEY, JSON.stringify(state));
  } catch { /* the memory is lost; the page is not */ }
  listeners.forEach((fn) => fn());
}

if (typeof window !== 'undefined' && typeof window.addEventListener === 'function') {
  // Another tab's choice is picked up rather than overwritten by this tab's next write.
  window.addEventListener('storage', (ev) => {
    if (ev.key !== KEY) return;
    state = Object.freeze(readStored());
    listeners.forEach((fn) => fn());
  });
}

export const prefs = {
  subscribe(fn) { listeners.add(fn); return () => { listeners.delete(fn); }; },
  get() { return state; },

  /* A style id, or null to forget it. Anything else is refused rather than stored. */
  setStyleInHand(id) {
    const next = isKey(id) ? id : null;
    if (id != null && next === null) return;
    if (state.styleInHand === next) return;
    commit({ ...state, styleInHand: next });
  },

  markSeen(key) {
    if (!isKey(key) || state.seen[key] === true) return;
    commit({ ...state, seen: { ...state.seen, [key]: true } });
  },
  isSeen(key) { return isKey(key) && state.seen[key] === true; },

  setFold(key, open) {
    if (!isKey(key) || typeof open !== 'boolean' || state.folds[key] === open) return;
    commit({ ...state, folds: { ...state.folds, [key]: open } });
  },
  /* true, false, or undefined when the reader never chose — three answers, because "never
     chose" is what lets a first visit open a disclosure a later visit folds. */
  fold(key) {
    return isKey(key) && Object.prototype.hasOwnProperty.call(state.folds, key)
      ? state.folds[key] : undefined;
  },
};

/* Is a page head's "how to read this page" open? The reader's own choice when there is one;
   otherwise open exactly when this is the first visit. Pure, so the rule is tested without a
   store — and so a component cannot read `seen` AFTER marking it and fold the head it is
   showing for the first time, which is the order the one-line version gets wrong. */
export function disclosureOpen(fold, firstVisit) {
  return typeof fold === 'boolean' ? fold : Boolean(firstVisit);
}
