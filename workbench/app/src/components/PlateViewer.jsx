/* The loupe — pan and zoom over a mounted plate.

   A drawing whose dimensions cannot be read is not a drawing, and every plate in this
   instrument was previously fixed at whatever width its column of the layout happened to
   be: a 60-foot plan and a 37-foot order both squeezed into 330 px, with their figures
   set at a tenth of a point. This frame scales the WHOLE plate — title block, sheet and
   caption together, as a sheet moves under a loupe — rather than the SVG alone, so the
   lettering never drifts out of register with the drawing it labels.

   The scale is a CSS transform, which means `getScreenCTM()` still maps screen pixels
   back to model feet correctly: the plan's wall-drag handles keep working at any
   magnification. That it magnifies the pen along with the drawing is OQ 66 (it was raised as 64 and reissued at the 26 Aug merge).

   Fit is the resting state and is recomputed as the pane resizes; once the reader
   chooses a magnification it is held until they ask to fit again. Panning is by drag,
   by scrollbar, or by wheel; a drag that begins on a mark the plate owns (anything
   carrying data-nopan — a resize handle) is left to that mark. */
import React from 'react';
import { Eyebrow } from './Eyebrow.jsx';

const STEPS = [0.5, 0.75, 1, 1.5, 2, 3, 4, 6, 8];
const MAX = STEPS[STEPS.length - 1];
const PAN_SLOP = 3;              // px below which a drag is a click, not a pan

const NOTE = '⌘/ctrl-scroll zooms · drag pans';

function Key({ onClick, children, title, disabled }) {
  return (
    <button type="button" onClick={onClick} title={title} disabled={disabled}
      style={{ font: 'var(--type-data-s)', padding: '1px 7px', minWidth: 22, flex: 'none',
        border: '1px solid var(--rule)', color: disabled ? 'var(--ink-4)' : 'var(--ink-3)',
        background: 'transparent', cursor: disabled ? 'default' : 'pointer',
        transition: 'var(--t-hover)' }}>{children}</button>
  );
}

export function PlateViewer({ children, height = 'clamp(380px, 70vh, 880px)', label = 'loupe', note }) {
  const frameRef = React.useRef(null);     // the fixed pane: measured, never scrolled
  const scrollRef = React.useRef(null);    // the scroller
  const stageRef = React.useRef(null);     // the plate at scale 1
  const [frame, setFrame] = React.useState({ w: 0, h: 0 });
  const [natH, setNatH] = React.useState(0);
  const [zoom, setZoom] = React.useState(null);   // null = fitted to the pane

  // The pane is measured, NOT the scroller: a scrollbar appearing inside the scroller
  // would narrow it, which would re-fit the plate, which could make the scrollbar go
  // away again. Measuring the outer box breaks that loop before it can oscillate, and
  // `scrollbar-gutter: stable` below keeps the two from disagreeing by a scrollbar's
  // width (which used to raise a phantom horizontal bar at magnifications near 1:1).
  React.useLayoutEffect(() => {
    const el = frameRef.current;
    if (!el || typeof ResizeObserver === 'undefined') return undefined;
    const read = () => {
      const sc = scrollRef.current;
      setFrame({ w: sc ? sc.clientWidth : el.clientWidth, h: el.clientHeight });
    };
    const ro = new ResizeObserver(read);
    ro.observe(el);
    read();
    return () => ro.disconnect();
  }, []);

  // the plate's own height at scale 1 — a transform does not change layout, so
  // offsetHeight is the natural height whatever the magnification
  React.useLayoutEffect(() => {
    const el = stageRef.current;
    if (!el || typeof ResizeObserver === 'undefined') return undefined;
    const ro = new ResizeObserver(() => setNatH(el.offsetHeight));
    ro.observe(el);
    setNatH(el.offsetHeight);
    return () => ro.disconnect();
  }, []);

  // fit is NOT clamped to the ladder's floor. Clamping it meant that a plate more than
  // twice the pane's height "fitted" at 50% with its foot still off the bottom, while
  // the fit button sat disabled — the one state with no way out.
  const fit = natH > 0 && frame.h > 0 ? Math.min(1, frame.h / natH) : 1;
  const z = zoom == null ? fit : zoom;
  const fitted = zoom == null;
  // fit is a FLOOR, not a rung. Putting it in the ladder meant the first press of + moved
  // 93% to 93% — the rung was a rounded copy of where the reader already was, and the
  // press did nothing they could see.
  const floor = Math.min(STEPS[0], fit);
  const ladder = React.useMemo(
    () => (fit < STEPS[0] - 1e-6 ? [fit, ...STEPS] : STEPS), [fit]);

  const contentW = Math.max(0, frame.w * z);
  const contentH = Math.max(0, natH * z);

  // Two quick taps on + used to land on the same rung: both handlers closed over the z of
  // the render they were created in, so the second computed its step from the first's
  // starting point and set the same value. The ladder is walked from a ref, which is
  // always the committed scale.
  const zRef = React.useRef(z);
  zRef.current = z;

  /* Hold the point under the cursor still across a zoom. The correction cannot run in a
     rAF: that races React's commit and clamps against the OLD scroll extent, so the
     anchor drifts on every step. It runs in a layout effect keyed on the new scale,
     after the content div has its new size — and it accounts for the auto margin, which
     centres the content whenever it is narrower than the pane. */
  const pending = React.useRef(null);
  const zoomTo = React.useCallback((next, anchor) => {
    const sc = scrollRef.current;
    const nz = Math.min(MAX, Math.max(floor, next));
    if (sc && anchor) {
      const off = Math.max(0, (sc.clientWidth - contentW) / 2);
      pending.current = { cx: (sc.scrollLeft + anchor.x - off) / z,
                          cy: (sc.scrollTop + anchor.y) / z, ax: anchor.x, ay: anchor.y };
    }
    setZoom(nz);
  }, [z, contentW, floor]);

  React.useLayoutEffect(() => {
    const sc = scrollRef.current, p = pending.current;
    if (!sc || !p) return;
    pending.current = null;
    const off = Math.max(0, (sc.clientWidth - frame.w * z) / 2);
    sc.scrollLeft = p.cx * z + off - p.ax;
    sc.scrollTop = p.cy * z - p.ay;
  }, [z, frame.w]);

  const step = (dir) => {
    const cur = zRef.current;
    const next = dir > 0
      ? ladder.find((s) => s > cur + 1e-6) ?? MAX
      : [...ladder].reverse().find((s) => s < cur - 1e-6) ?? floor;
    const sc = scrollRef.current;
    zoomTo(next, sc ? { x: sc.clientWidth / 2, y: sc.clientHeight / 2 } : null);
  };

  // React registers wheel at the root as passive, so preventDefault there is a no-op and
  // the browser's own page zoom would win. The listener has to be native and explicit.
  React.useEffect(() => {
    const sc = scrollRef.current;
    if (!sc) return undefined;
    const onWheel = (e) => {
      if (!(e.ctrlKey || e.metaKey)) return;      // a plain wheel still scrolls the sheet
      e.preventDefault();
      const r = sc.getBoundingClientRect();
      zoomTo(z * Math.exp(-e.deltaY * 0.0022), { x: e.clientX - r.left, y: e.clientY - r.top });
    };
    sc.addEventListener('wheel', onWheel, { passive: false });
    return () => sc.removeEventListener('wheel', onWheel);
  }, [z, zoomTo]);

  /* One drag's worth of window listeners, held in a ref so they can be torn down from
     anywhere: on pointerup, on POINTERCANCEL (a touch gesture the browser takes over
     never sends an up, and the old code then kept writing scrollLeft for the rest of the
     session), and on unmount mid-drag. The sibling DragHandle in sheet/Sheet.jsx has
     always handled cancel; this did not. */
  const drag = React.useRef(null);
  const [grabbing, setGrabbing] = React.useState(false);
  const endDrag = React.useCallback(() => {
    const d = drag.current;
    if (!d) return;
    drag.current = null;
    window.removeEventListener('pointermove', d.move);
    window.removeEventListener('pointerup', d.up);
    window.removeEventListener('pointercancel', d.up);
    setGrabbing(false);
    return d;
  }, []);
  React.useEffect(() => endDrag, [endDrag]);

  const canPan = () => {
    const sc = scrollRef.current;
    return !!sc && (sc.scrollWidth > sc.clientWidth + 1 || sc.scrollHeight > sc.clientHeight + 1);
  };

  function onPointerDown(e) {
    const sc = scrollRef.current;
    if (!sc || e.button !== 0 || drag.current) return;
    // a mark that owns its own drag (a wall handle) keeps it
    if (e.target.closest && e.target.closest('[data-nopan]')) return;
    if (!canPan()) return;
    e.preventDefault();               // a pan is not a text selection
    const x0 = e.clientX, y0 = e.clientY, l0 = sc.scrollLeft, t0 = sc.scrollTop;
    const move = (ev) => {
      const dx = ev.clientX - x0, dy = ev.clientY - y0;
      const d = drag.current;
      if (!d) return;
      if (!d.moved && Math.abs(dx) + Math.abs(dy) < PAN_SLOP) return;
      d.moved = true;
      setGrabbing(true);
      sc.scrollLeft = l0 - dx;
      sc.scrollTop = t0 - dy;
    };
    const up = () => {
      const d = endDrag();
      if (!d || !d.moved) return;
      /* A pan is not a pick: swallow the click the drag would otherwise deliver. Armed
         on WINDOW in capture phase and disarmed on the next tick, because a pan very
         often ends with the pointer outside the pane — the click is then dispatched to
         an ancestor, a listener bound to the scroller never fires, `once` never spends
         it, and the reader's NEXT genuine click is eaten instead. */
      const swallow = (ev) => ev.stopPropagation();
      window.addEventListener('click', swallow, true);
      setTimeout(() => window.removeEventListener('click', swallow, true), 0);
    };
    drag.current = { move, up, moved: false };
    window.addEventListener('pointermove', move);
    window.addEventListener('pointerup', up);
    window.addEventListener('pointercancel', up);
  }

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '0 0 7px',
        flexWrap: 'nowrap' }}>
        <span style={{ flex: 'none', whiteSpace: 'nowrap' }}><Eyebrow as="span">{label}</Eyebrow></span>
        <Key onClick={() => step(-1)} title="smaller" disabled={z <= floor + 1e-6}>−</Key>
        <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)', minWidth: 44,
          flex: 'none', textAlign: 'center' }}>{Math.round(z * 100)}%</span>
        <Key onClick={() => step(1)} title="larger" disabled={z >= MAX - 1e-6}>+</Key>
        <Key onClick={() => setZoom(null)} title="the whole plate in the pane"
          disabled={fitted}>fit</Key>
        <Key onClick={() => zoomTo(1)} title="the plate at the pane's own width">1:1</Key>
        <span style={{ flex: 1, minWidth: 10 }} />
        <span title={note || NOTE} style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)',
          textAlign: 'right', minWidth: 0, whiteSpace: 'nowrap', overflow: 'hidden',
          textOverflow: 'ellipsis' }}>
          {note || NOTE}
        </span>
      </div>
      <div ref={frameRef} style={{ position: 'relative', height, border: '1px solid var(--rule)',
        background: 'var(--paper-mat)' }}>
        {/* NOT overscroll-behavior: contain. The pane is up to 74vh tall and every surface
            carries content BELOW it — on Proportions, the rules table this very commit
            moved down there. Containing the scroll meant a reader wheeling down the page
            with the cursor over the plate simply stopped, and had to move the pointer off
            a two-thirds-of-a-screen element to carry on reading. */}
        <div ref={scrollRef} onPointerDown={onPointerDown}
          style={{ position: 'absolute', inset: 0, overflow: 'auto', scrollbarWidth: 'thin',
            scrollbarGutter: 'stable',
            cursor: grabbing ? 'grabbing' : (canPan() ? 'grab' : 'default'),
            userSelect: grabbing ? 'none' : undefined }}>
          <div style={{ width: contentW || '100%', height: contentH || '100%',
            position: 'relative', margin: '0 auto' }}>
            <div ref={stageRef} style={{ position: 'absolute', top: 0, left: 0,
              width: frame.w || '100%', transform: `scale(${z})`, transformOrigin: '0 0' }}>
              {children}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
