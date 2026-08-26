/* The loupe — pan and zoom over a mounted plate.

   A drawing whose dimensions cannot be read is not a drawing, and every plate in this
   instrument was previously fixed at whatever size its column of the layout happened to
   be: a 60-foot plan and a 37-foot order both squeezed into 330 px, with their figures
   set at a tenth of a point. This frame scales the WHOLE plate — title block, sheet and
   caption together, as a sheet moves under a loupe — rather than the SVG alone, so the
   lettering never drifts out of register with the drawing it labels.

   The scale is a CSS transform, which means `getScreenCTM()` still maps screen pixels
   back to model feet correctly: the plan's wall-drag handles keep working at any
   magnification, and a stroke declared non-scaling stays a pen line, only larger.

   Fit is the resting state and is recomputed as the pane resizes; once the reader
   chooses a magnification it is held until they ask to fit again. Panning is by drag,
   by scrollbar, or by wheel; a drag that begins on a mark the plate owns (anything
   carrying data-nopan — a resize handle) is left to that mark. */
import React from 'react';
import { Eyebrow } from './Eyebrow.jsx';

const STEPS = [0.5, 0.75, 1, 1.5, 2, 3, 4, 6, 8];
const MIN = STEPS[0], MAX = STEPS[STEPS.length - 1];
const clamp = (z) => Math.min(MAX, Math.max(MIN, z));

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
  // away again. Measuring the outer box breaks that loop before it can oscillate.
  React.useLayoutEffect(() => {
    const el = frameRef.current;
    if (!el || typeof ResizeObserver === 'undefined') return undefined;
    const ro = new ResizeObserver(() => setFrame({ w: el.clientWidth, h: el.clientHeight }));
    ro.observe(el);
    setFrame({ w: el.clientWidth, h: el.clientHeight });
    return () => ro.disconnect();
  }, []);

  // the plate's own height at scale 1 and the pane's width — a transform does not
  // change layout, so offsetHeight is the natural height whatever the magnification
  React.useLayoutEffect(() => {
    const el = stageRef.current;
    if (!el || typeof ResizeObserver === 'undefined') return undefined;
    const ro = new ResizeObserver(() => setNatH(el.offsetHeight));
    ro.observe(el);
    setNatH(el.offsetHeight);
    return () => ro.disconnect();
  }, []);

  const fit = natH > 0 && frame.h > 0 ? clamp(Math.min(1, frame.h / natH)) : 1;
  const z = zoom == null ? fit : zoom;
  const fitted = zoom == null;

  const zoomTo = React.useCallback((next, anchor) => {
    const sc = scrollRef.current;
    const nz = clamp(next);
    if (sc && anchor) {
      // hold the point under the cursor still: it is at content coordinate
      // (scroll + offset) / z before, and must land on the same coordinate after
      const cx = (sc.scrollLeft + anchor.x) / z, cy = (sc.scrollTop + anchor.y) / z;
      requestAnimationFrame(() => {
        sc.scrollLeft = cx * nz - anchor.x;
        sc.scrollTop = cy * nz - anchor.y;
      });
    }
    setZoom(nz);
  }, [z]);

  const step = (dir) => {
    const next = dir > 0
      ? STEPS.find((s) => s > z + 1e-6) ?? MAX
      : [...STEPS].reverse().find((s) => s < z - 1e-6) ?? MIN;
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

  const [grabbing, setGrabbing] = React.useState(false);
  function onPointerDown(e) {
    const sc = scrollRef.current;
    if (!sc || e.button !== 0) return;
    // a mark that owns its own drag (a wall handle) keeps it
    if (e.target.closest && e.target.closest('[data-nopan]')) return;
    const canPan = sc.scrollWidth > sc.clientWidth + 1 || sc.scrollHeight > sc.clientHeight + 1;
    if (!canPan) return;
    const x0 = e.clientX, y0 = e.clientY, l0 = sc.scrollLeft, t0 = sc.scrollTop;
    let moved = false;
    const move = (ev) => {
      const dx = ev.clientX - x0, dy = ev.clientY - y0;
      if (!moved && Math.abs(dx) + Math.abs(dy) < 3) return;
      moved = true;
      setGrabbing(true);
      sc.scrollLeft = l0 - dx;
      sc.scrollTop = t0 - dy;
    };
    const up = () => {
      window.removeEventListener('pointermove', move);
      window.removeEventListener('pointerup', up);
      setGrabbing(false);
      // a pan is not a pick: swallow the click the drag would otherwise deliver
      if (moved) sc.addEventListener('click', (ev) => ev.stopPropagation(), { capture: true, once: true });
    };
    window.addEventListener('pointermove', move);
    window.addEventListener('pointerup', up);
  }

  const contentW = Math.max(0, frame.w * z);
  const contentH = Math.max(0, natH * z);

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '0 0 7px',
        flexWrap: 'nowrap' }}>
        <span style={{ flex: 'none', whiteSpace: 'nowrap' }}><Eyebrow as="span">{label}</Eyebrow></span>
        <Key onClick={() => step(-1)} title="smaller" disabled={z <= MIN + 1e-6}>−</Key>
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
        <div ref={scrollRef} onPointerDown={onPointerDown}
          style={{ position: 'absolute', inset: 0, overflow: 'auto', scrollbarWidth: 'thin',
            cursor: grabbing ? 'grabbing' : 'default', overscrollBehavior: 'contain' }}>
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
