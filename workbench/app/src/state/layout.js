/* How much of the window each pane gets, and which of them are folded away.

   Same external-store idiom as planDoc and session; localStorage, because a pane width
   is a preference about this browser and this screen, not a place. It deliberately does
   NOT go in the URL: a link to `#/kit/craftsman/cornice` is a citation, and a citation
   that also carried the sender's rail width would be handing the reader the sender's
   monitor.

   TWO NUMBERS PER PANE, AND THE DISTINCTION IS THE WHOLE FILE.

     `widths[p]`    what the reader CHOSE. Persisted. Changed only by a deliberate act —
                    a drag, an arrow key, a reset.
     `effective[p]` what fits in THIS window right now. Derived, never stored, and what
                    `width()` returns.

   The first version had one number and let the window overwrite it. An adversarial audit
   found what that costs: narrow the window for a moment to put a PDF beside the workbench
   and every one of the eight panes is written to its floor and committed — including the
   five that belong to surfaces you were not even looking at, because the fit runs over
   every pane rather than the mounted ones. Widening back restored nothing, because a
   clamp that only shrinks has no counterpart. A week of tuning, gone to a window drag,
   silently. Preference and fit have to be different numbers or that is unavoidable.

   THE FIT MAY GO BELOW A PANE'S `min`, AND MUST. `min` is a floor on what the reader may
   CHOOSE, not a claim about what the window can hold. The audit's second finding was that
   re-imposing `min` inside the fit made the stated guarantee — no pane over a third, the
   two rails never over half — silently void exactly when it binds: at 390px, nav.min plus
   rail.min is 390, so the two rails took the entire window and the canvas between them,
   which is the thing being read, was zero pixels wide. The fit now has its own hard floor
   and the guarantee holds at every width. */

const KEY = 'tdl-workbench-layout';

/* min/max are what the READER may choose. `foldable` is the difference between chrome and
   subject: the two shell rails and the Phylogeny's record are things a reader may not want
   on screen at all; a surface's own index — the fault list, the slot list, the pack list —
   IS the surface, and a drag past the floor there stops at the floor. */
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

/* The narrowest a pane may be squeezed BY THE WINDOW (as opposed to by the reader). Below
   this it is not a pane, it is a stripe, and the reader should fold it instead.

   It SCALES with the window, and it has to: a fixed floor of 90px means two rails cannot
   fit inside half of a 320px window, so the stated guarantee would be false at the widths
   where it matters most. A sixth of the window keeps two rails inside a half at every
   size, so the canvas — the thing being read — is never squeezed below a third. */
const hardMin = (windowWidth) => Math.max(24, Math.min(90, Math.floor(windowWidth / 6)));

const clamp = (name, px) => {
  const p = PANES[name];
  if (!p) return 0;
  // `Number([])` is 0 and `Number('')` is 0, either of which would silently clamp a
  // nonsense stored value to the pane's minimum rather than fall back to its default.
  const n = typeof px === 'number' ? px : (typeof px === 'string' && px.trim() !== '' ? Number(px) : NaN);
  if (!Number.isFinite(n)) return p.def;
  return Math.round(Math.min(p.max, Math.max(p.min, n)));
};

/* What actually fits, given the reader's preferences and this window.

   Two rules, both stated in the order they bind: no pane may take more than a third of the
   window, and the two SHELL rails together no more than half — the canvas between them is
   the thing being read. A folded pane is 0 and takes part in neither. */
function fit(widths, collapsed, windowWidth) {
  const eff = {};
  Object.keys(PANES).forEach((k) => { eff[k] = collapsed[k] ? 0 : widths[k]; });
  if (!Number.isFinite(windowWidth) || windowWidth <= 0) return eff;

  const floor = hardMin(windowWidth);
  const third = Math.floor(windowWidth / 3);
  Object.keys(PANES).forEach((k) => {
    if (eff[k] > third) eff[k] = Math.max(floor, third);
  });

  const half = Math.floor(windowWidth / 2);
  const pair = eff.nav + eff.rail;
  if (pair > half) {
    // Proportionally, so the reader's sense of which rail is the wider one survives.
    const share = Math.max(floor, Math.min(half - floor, Math.round(half * (eff.nav / pair))));
    eff.nav = eff.nav ? Math.min(eff.nav, share) : 0;
    eff.rail = eff.rail ? Math.min(eff.rail, half - eff.nav) : 0;
  }
  return eff;
}

function readStored() {
  const widths = {};
  const collapsed = {};
  Object.keys(PANES).forEach((k) => { widths[k] = PANES[k].def; collapsed[k] = false; });
  try {
    const saved = JSON.parse(localStorage.getItem(KEY) || 'null');
    if (saved && typeof saved === 'object' && !Array.isArray(saved)) {
      const sw = saved.widths, sc = saved.collapsed;
      Object.keys(PANES).forEach((k) => {
        if (sw && typeof sw === 'object' && sw[k] != null) widths[k] = clamp(k, sw[k]);
        // A pane that is the surface's own subject has no folded state to be put into,
        // and a stored `true` for one must be ignored rather than honoured. The guard in
        // setCollapsed does not reach here, and an audit found this the one hostile
        // localStorage shape that got through: it left Splitter believing a pane that
        // renders at full width is 0 wide, so the first drag snapped it to its minimum
        // and aria-valuenow told a screen reader 0 about a pane that was on screen.
        if (sc && typeof sc === 'object' && sc[k] === true && PANES[k].foldable) collapsed[k] = true;
      });
    }
  } catch { /* a corrupt entry is not worth a broken shell — start from the defaults */ }
  return { widths, collapsed };
}

/* `full` is NOT persisted, and that is the point of the word "temporarily" in the
   affordance that sets it: a reader who fills the screen with the atlas, closes the tab
   and comes back tomorrow should get the instrument back, not a map with no way out that
   they have to remember the escape key for. Neither is `windowWidth`, which belongs to
   this window and this moment. */
const stored = readStored();
let state = {
  ...stored,
  full: null,
  windowWidth: null,
  effective: fit(stored.widths, stored.collapsed, null),
};

const listeners = new Set();

/* PERSISTENCE IS DEBOUNCED, AND THE RENDER IS NOT.

   A drag calls dragTo on every pointermove — measured at 115 for one 1.5 s pull on a
   120 Hz display — and each one used to be a synchronous localStorage write and a
   `storage` event broadcast to every other tab of the origin, for a value only the last
   of which matters. Listeners still fire immediately, so the pane tracks the hand; only
   the write waits. `flush` exists for the two callers that cannot wait: a test, and the
   page going away. */
let pending = null;

function persist() {
  pending = null;
  try {
    localStorage.setItem(KEY, JSON.stringify({ widths: state.widths, collapsed: state.collapsed }));
  } catch { /* best effort — a private window still gets a working layout, just not a kept one */ }
}

function emit(save = true) {
  if (save && pending === null) pending = setTimeout(persist, 150);
  listeners.forEach((fn) => fn());
}

if (typeof window !== 'undefined') {
  // A drag that ends with the tab closing must not lose its last pixel.
  window.addEventListener('pagehide', () => { if (pending !== null) { clearTimeout(pending); persist(); } });
  /* Another tab's write is picked up rather than clobbered. Without this, last-writer-wins
     over the WHOLE object: narrow the nav in tab A, then toggle full screen in tab B — a
     state this file says is not persisted — and B's stale 236 overwrote A's 160. */
  window.addEventListener('storage', (ev) => {
    if (ev.key !== KEY) return;
    const next = readStored();
    state = { ...state, ...next, effective: fit(next.widths, next.collapsed, state.windowWidth) };
    listeners.forEach((fn) => fn());
  });
}

/* Recompute the fit and publish, but only if something a reader could see changed.

   The identity check matters: the first version rebuilt `widths` into a NEW object with
   IDENTICAL values on every resize below 900px, so `widths !== state.widths` passed, emit
   fired, localStorage was written and the whole surface tree re-rendered — twenty times
   for twenty resize events, which is what dragging a window edge produces continuously. */
function publish(widths, collapsed, windowWidth, save = true) {
  const eff = fit(widths, collapsed, windowWidth);
  const same = windowWidth === state.windowWidth
    && Object.keys(PANES).every((k) => widths[k] === state.widths[k]
      && collapsed[k] === state.collapsed[k] && eff[k] === state.effective[k]);
  if (same) return;
  state = { ...state, widths, collapsed, windowWidth, effective: eff };
  emit(save);
}

export const layout = {
  subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); },
  get() { return state; },

  /* What fits. Callers render with this. */
  width(name) { return state.effective[name]; },
  /* What the reader chose. Only the splitter's own arithmetic wants this. */
  preferred(name) { return state.widths[name]; },
  isOpen(name) { return !state.collapsed[name]; },
  flush() { if (pending !== null) { clearTimeout(pending); persist(); } },

  setWidth(name, px) {
    if (!PANES[name]) return;
    publish({ ...state.widths, [name]: clamp(name, px) }, state.collapsed, state.windowWidth);
  },

  /* Dragging a foldable pane below its floor is a request to fold it away, not an error —
     that is the gesture every editor uses, and refusing it leaves the reader hauling at a
     handle that has stopped moving with no idea why. The width is left where it was, so
     unfolding returns the pane to the size they had chosen rather than to the default. */
  dragTo(name, px) {
    const p = PANES[name];
    if (!p) return;
    if (p.foldable && px < p.min * 0.6) { layout.setCollapsed(name, true); return; }
    const collapsed = state.collapsed[name] ? { ...state.collapsed, [name]: false } : state.collapsed;
    publish({ ...state.widths, [name]: clamp(name, px) }, collapsed, state.windowWidth);
  },

  setCollapsed(name, on) {
    if (!PANES[name] || state.collapsed[name] === !!on) return;
    // Said here as well as in readStored and dragTo, because `toggle`, the key map and a
    // stored preference all reach this and none of them goes through dragTo.
    if (on && !PANES[name].foldable) return;
    publish(state.widths, { ...state.collapsed, [name]: !!on }, state.windowWidth);
  },

  toggle(name) { layout.setCollapsed(name, !state.collapsed[name]); },
  /* Whether pressing Enter on this pane's handle will do anything. The handle's own title
     used to advertise a fold on five panes that cannot fold. */
  canFold(name) { return !!(PANES[name] && PANES[name].foldable); },

  reset(name) {
    if (!PANES[name]) return;
    publish({ ...state.widths, [name]: PANES[name].def },
      { ...state.collapsed, [name]: false }, state.windowWidth);
  },

  /* One surface, filling the window. `null` is the instrument; a surface id is that
     surface with the masthead and both rails out of the way. NOT PERSISTED — `save` is
     false, so a transient act in one tab cannot write this tab's widths over another's. */
  setFull(surface) {
    if (state.full === (surface || null)) return;
    state = { ...state, full: surface || null };
    emit(false);
  },

  /* The window changed. Only the FIT moves; what the reader chose is untouched, so
     widening back restores it. Called by the shell on mount and on every resize. */
  clampAll(windowWidth) {
    if (!Number.isFinite(windowWidth) || windowWidth <= 0) return;
    publish(state.widths, state.collapsed, windowWidth, false);
  },
};
