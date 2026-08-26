/* How much of the window each pane gets, and which of them are folded away.

   Same external-store idiom as planDoc and session; localStorage, because a pane width
   is a preference about this browser and this screen, not a place. It deliberately does
   NOT go in the URL: a link to `#/kit/craftsman/cornice` is a citation, and a citation
   that also carried the sender's rail width would be handing the reader the sender's
   monitor.

   Every pane is declared once, here, with its default, its floor and its ceiling. That
   table is the whole clamping rule, and it is applied on READ as well as on write — a
   width stored on a 2560px display must not strand the nav off the side of a laptop, and
   a hand-edited localStorage entry must not be able to put a pane at 4000px either. */

const KEY = 'tdl-workbench-layout';

/* min/max are in px. `max` is also capped against the live window in `clampAll` — these
   are the absolute bounds, the window supplies the situational one. */
/* `foldable` is the difference between chrome and subject. The two shell rails and the
   Phylogeny's record are things a reader may not want on screen at all; a surface's own
   index — the fault list, the slot list, the pack list — IS the surface, and a drag past
   the floor there should stop at the floor rather than fold the subject away. */
export const PANES = {
  nav: { def: 236, min: 150, max: 420, label: 'the surface list', foldable: true },
  rail: { def: 344, min: 240, max: 620, label: 'the rail', foldable: true },
  phylo: { def: 320, min: 220, max: 560, label: "the taxon's record", foldable: true },

  // the surfaces' own index panels — pull, but never fold
  faults: { def: 330, min: 220, max: 560, label: 'the fault list' },
  kit: { def: 340, min: 240, max: 620, label: "the style's record" },
  workbench: { def: 430, min: 300, max: 700, label: 'the findings' },
  proportions: { def: 250, min: 180, max: 460, label: 'the pack list' },
  transcription: { def: 360, min: 260, max: 640, label: 'the record' },
};

const clamp = (name, px) => {
  const p = PANES[name];
  if (!p || !Number.isFinite(px)) return p ? p.def : 0;
  return Math.round(Math.min(p.max, Math.max(p.min, px)));
};

function readStored() {
  const widths = {};
  const collapsed = {};
  Object.keys(PANES).forEach((k) => { widths[k] = PANES[k].def; collapsed[k] = false; });
  try {
    const saved = JSON.parse(localStorage.getItem(KEY) || 'null') || {};
    Object.keys(PANES).forEach((k) => {
      if (saved.widths && saved.widths[k] != null) widths[k] = clamp(k, Number(saved.widths[k]));
      if (saved.collapsed && typeof saved.collapsed[k] === 'boolean') collapsed[k] = saved.collapsed[k];
    });
  } catch { /* a corrupt entry is not worth a broken shell — start from the defaults */ }
  return { widths, collapsed };
}

/* `full` is NOT persisted, and that is the point of the word "temporarily" in the
   affordance that sets it: a reader who fills the screen with the atlas, closes the tab
   and comes back tomorrow should get the instrument back, not a map with no way out that
   they have to remember the escape key for. */
let state = { ...readStored(), full: null };

const listeners = new Set();

function emit() {
  try {
    localStorage.setItem(KEY, JSON.stringify({ widths: state.widths, collapsed: state.collapsed }));
  } catch { /* best effort — a private window still gets a working layout, just not a kept one */ }
  listeners.forEach((fn) => fn());
}

export const layout = {
  subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); },
  get() { return state; },

  width(name) { return state.widths[name]; },
  isOpen(name) { return !state.collapsed[name]; },

  setWidth(name, px) {
    if (!PANES[name]) return;
    const next = clamp(name, px);
    if (next === state.widths[name]) return;
    state = { ...state, widths: { ...state.widths, [name]: next } };
    emit();
  },

  /* Dragging a pane below its floor is a request to fold it away, not an error — that is
     the gesture every editor uses, and refusing it leaves the reader hauling at a handle
     that has stopped moving with no idea why. The width is left where it was, so
     unfolding returns the pane to the size they had chosen rather than to the default. */
  dragTo(name, px) {
    const p = PANES[name];
    if (!p) return;
    if (p.foldable && px < p.min * 0.6) { layout.setCollapsed(name, true); return; }
    if (state.collapsed[name]) layout.setCollapsed(name, false);
    layout.setWidth(name, px);
  },

  setCollapsed(name, on) {
    if (!PANES[name] || state.collapsed[name] === !!on) return;
    // A pane that is the surface's own subject has no folded state to be put into. Said
    // here as well as in dragTo, because `toggle`, the key map and a stored preference
    // from a hand-edited localStorage all reach this and none of them goes through dragTo.
    if (on && !PANES[name].foldable) return;
    state = { ...state, collapsed: { ...state.collapsed, [name]: !!on } };
    emit();
  },

  toggle(name) { layout.setCollapsed(name, !state.collapsed[name]); },

  reset(name) {
    if (!PANES[name]) return;
    state = {
      ...state,
      widths: { ...state.widths, [name]: PANES[name].def },
      collapsed: { ...state.collapsed, [name]: false },
    };
    emit();
  },

  /* One surface, filling the window. `null` is the instrument; a surface id is that
     surface with the masthead and both rails out of the way. */
  setFull(surface) {
    if (state.full === (surface || null)) return;
    state = { ...state, full: surface || null };
    emit();
  },

  /* A stored width from a wider screen has to be brought back inside this one. Called by
     the shell on mount and on every window resize. No pane may take more than a third of
     the window, and the two shell rails together no more than half — the canvas between
     them is the thing being read. */
  clampAll(windowWidth) {
    if (!Number.isFinite(windowWidth) || windowWidth <= 0) return;
    const ceiling = Math.max(120, Math.floor(windowWidth / 3));
    let widths = state.widths;
    Object.keys(PANES).forEach((k) => {
      const want = Math.min(widths[k], ceiling);
      if (want !== widths[k]) widths = { ...widths, [k]: clamp(k, want) };
    });
    const half = Math.floor(windowWidth / 2);
    const pair = (state.collapsed.nav ? 0 : widths.nav) + (state.collapsed.rail ? 0 : widths.rail);
    if (pair > half && !state.collapsed.nav && !state.collapsed.rail) {
      const share = Math.floor(half * (widths.nav / pair));
      widths = { ...widths, nav: clamp('nav', share), rail: clamp('rail', half - share) };
    }
    if (widths !== state.widths) { state = { ...state, widths }; emit(); }
  },
};
