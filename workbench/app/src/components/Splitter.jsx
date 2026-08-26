/* The margin between two panes, as something you can pull.

   A drawing instrument whose proportions are fixed is one that fits exactly one screen
   and one errand. The atlas wants width, the rail wants width while you are reading an
   answer, and the surface list wants almost none once you know where things are — so the
   margins move.

   Three things this is careful about, because a drag handle is easy to get half-right:

   1. It is a real separator to a screen reader, and it works from the keyboard. A
      control that can only be dragged is a control a lot of people do not have. Arrows
      nudge, shift-arrows stride, Home returns the pane to its shipped width, Enter folds
      it away.
   2. It captures the pointer. Without capture, a drag that outruns the cursor — and it
      will, because the layout reflows under it — drops the handle mid-pull and the pane
      stops moving while the button is still down.
   3. Its hit area is wider than its ink. The rule between two panes is a hairline
      because that is what the drawing wants; nine pixels of invisible grab either side
      is what the hand wants, and the two do not have to be the same object.

   It renders as a zero-width flex child so it can sit between panes without changing the
   arithmetic of the row it is in; the hit strip is absolutely positioned over the
   neighbouring pane's own border. */
import React from 'react';
import { layout, PANES } from '../state/layout.js';

const STRIDE = 48;
const NUDGE = 8;

export function Splitter({ pane, grows = 'left' }) {
  const spec = PANES[pane];
  const dir = grows === 'left' ? 1 : -1;    // px of pointer travel → px of pane width
  const drag = React.useRef(null);
  const [pulling, setPulling] = React.useState(false);
  const [near, setNear] = React.useState(false);
  const width = React.useSyncExternalStore(layout.subscribe, () => layout.width(pane));
  const open = React.useSyncExternalStore(layout.subscribe, () => layout.isOpen(pane));

  const onPointerDown = (ev) => {
    if (ev.button !== 0) return;
    drag.current = { x: ev.clientX, w: open ? width : 0 };
    setPulling(true);
    ev.currentTarget.setPointerCapture(ev.pointerId);
    ev.preventDefault();          // no text selection dragging along behind the handle
  };
  const onPointerMove = (ev) => {
    if (!drag.current) return;
    layout.dragTo(pane, drag.current.w + (ev.clientX - drag.current.x) * dir);
  };
  const onPointerUp = (ev) => {
    if (!drag.current) return;
    drag.current = null;
    setPulling(false);
    try { ev.currentTarget.releasePointerCapture(ev.pointerId); } catch { /* already gone */ }
  };

  /* WIRED TO THE ELEMENT BELOW, and it was not.

     This handler was written, documented in this file's own header, in docs/workbench.md
     and in the package report, asserted in the e2e walk as "the margin is a real
     separator, and focusable" — and never attached. A separator that is focusable and
     deaf is worse than one that is not focusable at all: a keyboard user tabs to it and
     nothing happens. The walk's check passed because it asserted the ELEMENT existed
     rather than that the KEYS did anything, which is the vacuous shape this project keeps
     finding. `layout.test.mjs` now drives the handler directly and the walk presses the
     keys and measures the pane. */
  const onKeyDown = (ev) => {
    const step = ev.shiftKey ? STRIDE : NUDGE;
    if (ev.key === 'ArrowLeft') { layout.dragTo(pane, width - step * dir); }
    else if (ev.key === 'ArrowRight') { layout.dragTo(pane, width + step * dir); }
    else if (ev.key === 'Home') { layout.reset(pane); }
    // Enter folds — but only where folding is a thing this pane does. It used to call
    // toggle() on all eight, and `setCollapsed` refused for the five that are a surface's
    // own subject while `preventDefault` ran anyway: the key was swallowed and nothing
    // happened, which is indistinguishable from a broken control.
    else if ((ev.key === 'Enter' || ev.key === ' ') && layout.canFold(pane)) { layout.toggle(pane); }
    else return;
    ev.preventDefault();
  };

  return (
    <div style={{ width: 0, flex: 'none', position: 'relative', zIndex: 6 }}>
      <div role="separator" tabIndex={0} aria-orientation="vertical"
        aria-label={`resize ${spec ? spec.label : pane}`}
        aria-valuenow={open ? width : 0}
        aria-valuemin={spec ? (spec.foldable ? 0 : spec.min) : 0}
        aria-valuemax={spec ? spec.max : 0}
        aria-valuetext={open ? `${width} pixels` : 'folded away'}
        onPointerDown={onPointerDown} onPointerMove={onPointerMove}
        onPointerUp={onPointerUp} onPointerCancel={onPointerUp}
        onKeyDown={onKeyDown}
        onDoubleClick={() => layout.reset(pane)}
        title={`Drag to resize ${spec ? spec.label : pane} · arrows nudge, shift-arrows stride, `
          + `Home or double-click for its shipped width${spec && spec.foldable ? ', Enter folds' : ''}`}
        /* Asymmetric, and biased the SAME way whichever side the pane is on. A centred
           10px strip put 5px of itself over its left neighbour's right edge — which in a
           left-to-right layout is exactly where that neighbour's vertical scrollbar lives,
           so pressing the scrollbar resized the pane instead of scrolling it. Two pixels
           there and eight on the other side keeps the target generous while leaving a
           classic scrollbar grabbable.

           `-2` regardless of `grows`, and that is not an oversight: the neighbour whose
           SCROLLBAR is adjacent is always the one on the left, because that is the edge a
           scrollbar sits on. Making this depend on `grows` — which I did first — moves the
           eight pixels onto the canvas's right edge in the `right` case and reintroduces
           the same defect mirrored. */
        style={{ position: 'absolute', top: 0, bottom: 0, left: -2, width: 10,
          cursor: 'col-resize', touchAction: 'none',
          // The ink: nothing at rest — the pane's own hairline is already there — a
          // thread under the hand, and gilt while a pull is in progress even after the
          // cursor has left the strip. Held in state rather than written onto the node:
          // an inline style and a hand-set `element.style` are two authorities over one
          // property, and React wins the next render whether or not the hand is still
          // there.
          background: pulling ? 'var(--gilt-deep)' : (near ? 'var(--rule)' : 'transparent'),
          transition: pulling ? 'none' : 'background var(--t-hover, .12s)' }}
        onPointerEnter={() => setNear(true)}
        onPointerLeave={() => setNear(false)}
        onFocus={() => setNear(true)}
        onBlur={() => setNear(false)} />
    </div>
  );
}
