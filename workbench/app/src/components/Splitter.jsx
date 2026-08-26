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

  const onKeyDown = (ev) => {
    const step = ev.shiftKey ? STRIDE : NUDGE;
    if (ev.key === 'ArrowLeft') { layout.dragTo(pane, width - step * dir); }
    else if (ev.key === 'ArrowRight') { layout.dragTo(pane, width + step * dir); }
    else if (ev.key === 'Home') { layout.reset(pane); }
    else if (ev.key === 'Enter' || ev.key === ' ') { layout.toggle(pane); }
    else return;
    ev.preventDefault();
  };

  return (
    <div style={{ width: 0, flex: 'none', position: 'relative', zIndex: 6 }}>
      <div role="separator" tabIndex={0} aria-orientation="vertical"
        aria-label={`resize ${spec ? spec.label : pane}`}
        aria-valuenow={open ? width : 0} aria-valuemin={0} aria-valuemax={spec ? spec.max : 0}
        onPointerDown={onPointerDown} onPointerMove={onPointerMove}
        onPointerUp={onPointerUp} onPointerCancel={onPointerUp}
        onDoubleClick={() => layout.reset(pane)}
        title={`Drag to resize ${spec ? spec.label : pane} · double-click for its shipped width`}
        style={{ position: 'absolute', top: 0, bottom: 0, left: -5, width: 10,
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
