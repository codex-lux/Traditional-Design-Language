/* ONE DEFINITION OPEN AT A TIME, AND NONE ACROSS A CHANGE OF PLACE (WP-14.8, PRD §I.1, §K).

   A `Term` opens a non-modal popover. Non-modal means the page behind it stays live, so the
   reader can open a second word while the first is showing — and two definitions stacked on a
   page are two answers to "what does this mean" with nothing saying which word each belongs
   to. So opening one closes the other, and the rule is held here rather than in each Term,
   because a rule every instance keeps for itself is a rule one instance forgets.

   THREE THINGS CLOSE EVERY POPOVER, and each is a moment the popover's word has left the
   reader's attention:

     a change of place    `hashchange` — the word was on the page the reader just left
     the palette opening  ⌘K / ctrl-K, and focus arriving inside any `aria-modal` dialog — the
                          palette is modal, and a non-modal definition left floating over it
                          belongs to a page the reader is no longer reading

   The second is detected TWICE on purpose: the key is how the palette usually opens and is
   caught before the palette mounts; the focus arriving in a modal is how it opens from the
   masthead's search button or any other caller, and it is the only signal the palette gives
   that does not require the palette to know this store exists (`CommandPalette.jsx` belongs to
   later packages, and a definition primitive that needed the palette to call it would be one
   more thing to forget).

   Pure store, plus `bindPopoverDom`, which takes the event targets it listens to as arguments so
   `src/popoverStore.test.mjs` drives it with bare `EventTarget`s under `node --test`. No
   tooltip or popover library: PRD §J.4 refuses one, and this is the whole rule. */

/* The PRD's hover delay, and the grace a pointer gets to cross from the word to its popover. */
export const HOVER_OPEN_MS = 400;
export const HOVER_CLOSE_MS = 200;

export function createPopoverStore() {
  let open = null;
  const listeners = new Set();
  const emit = () => listeners.forEach((fn) => fn());
  return Object.freeze({
    subscribe(fn) { listeners.add(fn); return () => { listeners.delete(fn); }; },
    /* The key of the popover that is open, or null. */
    get() { return open; },
    isOpen(key) { return key != null && open === key; },
    /* Opening one closes whichever was open: there is one slot. */
    open(key) {
      if (key == null || open === key) return;
      open = key;
      emit();
    },
    /* Closing is by key, so a popover closing itself late (a hover timer firing after another
       word was clicked) cannot close the one that replaced it. */
    close(key) {
      if (key == null || open !== key) return;
      open = null;
      emit();
    },
    closeAll() {
      if (open === null) return;
      open = null;
      emit();
    },
  });
}

export const popovers = createPopoverStore();

/* ⌘K / ctrl-K — the palette's own key, as `keys.js` spells it. */
export function isPaletteKey(ev) {
  return Boolean(ev) && Boolean(ev.metaKey || ev.ctrlKey) && (ev.key === 'k' || ev.key === 'K');
}

/* Is this element inside a modal dialog? `closest` where the target has it; a target that is
   not an element (a text node, the document) is inside nothing. */
export function isInsideModal(target) {
  return Boolean(target && typeof target.closest === 'function'
    && target.closest('[aria-modal="true"]'));
}

/* The capture flag as an OPTIONS OBJECT, in both the add and the remove. A browser treats a bare
   `true` and `{ capture: true }` as one flag; Node's own `EventTarget` does not match a bare
   `true` in `removeEventListener`, so the unbind below removed nothing under `node --test` and
   `src/popoverStore.test.mjs` caught the store still closing after it was unbound. The object
   form is the one spelling both honour. */
const CAPTURE = Object.freeze({ capture: true });

/* Listen on `win` for hashchange and the palette key, and on `doc` for focus arriving inside a
   modal. Returns the function that stops listening. Capture phase for both, so the palette's
   own handler (which opens it) cannot run first and leave a frame with both on screen. */
export function bindPopoverDom(store, { win, doc } = {}) {
  const onHash = () => store.closeAll();
  const onKey = (ev) => { if (isPaletteKey(ev)) store.closeAll(); };
  const onFocus = (ev) => { if (isInsideModal(ev && ev.target)) store.closeAll(); };
  if (win) {
    win.addEventListener('hashchange', onHash);
    win.addEventListener('keydown', onKey, CAPTURE);
  }
  if (doc) doc.addEventListener('focusin', onFocus, CAPTURE);
  return () => {
    if (win) {
      win.removeEventListener('hashchange', onHash);
      win.removeEventListener('keydown', onKey, CAPTURE);
    }
    if (doc) doc.removeEventListener('focusin', onFocus, CAPTURE);
  };
}

/* Bound once, to the real window, the first time a Term renders in a browser. */
let bound = false;
export function ensurePopoverDom() {
  if (bound || typeof window === 'undefined' || typeof document === 'undefined') return;
  bound = true;
  bindPopoverDom(popovers, { win: window, doc: document });
}

/* A click with `detail === 0` came from the keyboard (Enter or Space on a focused button),
   which is when opening should move focus INTO the popover: a pointer user is looking at it
   already, and a keyboard or screen-reader user otherwise has no way to know it opened. */
export function openedByKeyboard(ev) {
  return Boolean(ev) && ev.detail === 0;
}
