/* Every keyboard shortcut in the product, in one file.

   There were none before this. That is worth keeping in mind: nothing in the corpus, the
   rail or any surface expects a key, so the whole map is what is written here, and it is
   short on purpose. Six keys, no chords, no modal sequences:

     ⌘K / ctrl-K   the palette — the one way to jump anywhere
     /             focus the filter bar on this surface
     [             fold the surface list away, or bring it back
     ]             fold the rail away, or bring it back
     ?             what these keys are, and the citation grammar
     esc           close whatever is open, leave full screen, or clear the filter bar

   A fourth needed a reason and WP-5.7 had one for two of them. The rails are 580px of
   permanent furniture between the reader and the drawing; a fold that can only be reached
   by finding a 12px glyph at the foot of the thing you want gone is a fold nobody uses.
   `[` and `]` are the brackets around the canvas, which is what they do. A `g then k`
   chord would still be a second, worse jump mechanism that has to be memorised, and is
   still not here.

   The rule about typing: while the caret is in a field, only ⌘K and escape are keys.
   Everything else is a character, including `?` and `/` — a slash typed into the fault
   filter must be a slash. */

import React from 'react';

const FIELD = /^(input|textarea|select)$/i;

export function isTyping(el) {
  if (!el) return false;
  if (el.isContentEditable) return true;
  return FIELD.test(el.tagName || '');
}

/* handlers: {onPalette, onHelp, onSlash, onEscape, onFoldNav, onFoldRail} — each
   optional. */
export function useGlobalKeys(handlers) {
  const ref = React.useRef(handlers);
  ref.current = handlers;

  React.useEffect(() => {
    function onKeyDown(ev) {
      const h = ref.current || {};
      const typing = isTyping(ev.target);

      // ⌘K / ctrl-K reaches through a focused field: it is how you leave one.
      if ((ev.metaKey || ev.ctrlKey) && (ev.key === 'k' || ev.key === 'K')) {
        ev.preventDefault();
        h.onPalette && h.onPalette();
        return;
      }

      if (ev.key === 'Escape') {
        // Not prevented: a native picker or the browser's own find bar may want it too.
        h.onEscape && h.onEscape(ev);
        return;
      }

      if (typing) return;                       // from here down, keys are characters
      if (ev.metaKey || ev.ctrlKey || ev.altKey) return;

      if (ev.key === '/') {
        ev.preventDefault();
        h.onSlash && h.onSlash();
      } else if (ev.key === '?') {
        ev.preventDefault();
        h.onHelp && h.onHelp();
      } else if (ev.key === '[') {
        ev.preventDefault();
        h.onFoldNav && h.onFoldNav();
      } else if (ev.key === ']') {
        ev.preventDefault();
        h.onFoldRail && h.onFoldRail();
      }
    }

    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, []);
}

/* `/` has to reach a filter bar the shell knows nothing about — each surface mounts its
   own, and only when it has a list worth filtering. A one-line bus rather than a context:
   the bar registers while mounted, the shell asks, and if nothing is listening the key
   does nothing rather than stealing focus to somewhere arbitrary. */
let focusFilter = null;

export function registerFilterFocus(fn) {
  focusFilter = fn;
  return () => { if (focusFilter === fn) focusFilter = null; };
}

export function requestFilterFocus() {
  if (focusFilter) { focusFilter(); return true; }
  return false;
}

/* The map, as data, so the help card and the tests read the same source the handler does. */
export const SHORTCUTS = [
  { keys: '⌘K', alt: 'ctrl K', does: 'Search everything — styles, slots, faults, packs, rooms, surfaces' },
  { keys: '/', does: 'Filter the list in front of you' },
  { keys: '[', does: 'Fold the surface list away, or bring it back' },
  { keys: ']', does: 'Fold the rail away, or bring it back' },
  { keys: '?', does: 'This card' },
  { keys: 'esc', does: 'Close, leave full screen, or clear the filter' },
];
