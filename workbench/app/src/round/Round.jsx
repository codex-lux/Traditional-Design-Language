/* The model plate: a canvas, a camera, and a tween between named views.

   WP-12.4. This component owns the browser — the pointer, the resize, the animation frame —
   and delegates every decision to a leaf: where the camera stands to `frame.js`, what a
   triangle is to `solids.js`, what the drawing is called to `annotate.js`, and what a colour
   is to tokens.css. It loads `three-scene.js` with a DYNAMIC import, which is what keeps
   `three` out of the entry chunk and out of `no_bare_imports.test.mjs`'s walk.

   AN IDLE PLATE RENDERS NOTHING. The frame loop runs while a tween or a drag is in flight and
   stops when it settles: a 3D view that spins its GPU over a still drawing is a laptop fan in
   a reading room, and this surface is a drawing before it is a viewer. */
import React from 'react';

import { basis, defaultAxon, isNamed, poseFor, tween, unproject } from './frame.js';

/* The tokens the model draws in. Read once from the live document, so the Round is in the same
   palette as every plate beside it and a re-ruled token moves both. */
const TOKEN_NAMES = [
  'paper', 'paper-mat', 'paper-lit', 'paper-deep', 'salmon', 'salmon-deep', 'sepia', 'sepia-pale',
  'coal', 'ink', 'ink-2', 'ink-3', 'ink-4',
  'draw-cut', 'draw-profile', 'draw-seen', 'draw-fine', 'draw-hidden', 'draw-grid', 'draw-dim',
  'lw-cut', 'lw-heavy', 'lw-medium', 'lw-fine', 'lw-construction',
  'shadow-angle', 'shadow-flat', 'axon-elevation-deg', 'dur-4',
];

export function readTokens(el) {
  const cs = getComputedStyle(el || document.documentElement);
  const out = {};
  for (const n of TOKEN_NAMES) out[n] = (cs.getPropertyValue(`--${n}`) || '').trim();
  // `three-scene.js` asks for this name; tokens.css states the flat step as --shadow-flat.
  out['shadow-strength'] = out['shadow-flat'];
  return out;
}

const DUR_MS = (tokens) => parseFloat(tokens['dur-4']) || 520;

export function Round({ scene, view, onView, onPick, selected, height = 'clamp(420px, 74vh, 960px)' }) {
  const canvasRef = React.useRef(null);
  const wrapRef = React.useRef(null);
  const api = React.useRef(null);
  const raf = React.useRef(0);
  const live = React.useRef(null);          // the pose actually on screen
  const anim = React.useRef(null);          // { from, to, t0, ms }
  const drag = React.useRef(null);
  const [size, setSize] = React.useState({ width: 1, height: 1 });
  const [failed, setFailed] = React.useState(null);
  const [ready, setReady] = React.useState(false);
  const tokens = React.useRef({});

  const aspect = size.width / Math.max(size.height, 1);

  /* ---------------------------------------------------------------- mount */
  React.useEffect(() => {
    let dead = false;
    const el = canvasRef.current;
    if (!el) return undefined;
    tokens.current = readTokens(el);

    // A machine with no WebGL is a COULD NOT EVALUATE and says so on the plate, rather than
    // showing an empty rectangle that reads as a house with nothing in it.
    const probe = el.getContext('webgl2') || el.getContext('webgl');
    if (!probe) {
      setFailed('this browser reports no WebGL context, so the model cannot be drawn here — the flat plates below are unaffected');
      return undefined;
    }

    import('./three-scene.js')
      .then((mod) => {
        if (dead) return;
        api.current = mod.mount(el, tokens.current);
        setReady(true);
      })
      .catch((e) => { if (!dead) setFailed(`the model viewer could not be loaded: ${e.message || e}`); });

    return () => {
      dead = true;
      if (api.current) api.current.dispose();
      api.current = null;
    };
  }, []);

  /* ---------------------------------------------------------------- size */
  React.useEffect(() => {
    const el = wrapRef.current;
    if (!el || typeof ResizeObserver === 'undefined') return undefined;
    const ro = new ResizeObserver(() => {
      const w = Math.max(1, el.clientWidth);
      const h = Math.max(1, el.clientHeight);
      setSize({ width: w, height: h });
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  /* ---------------------------------------------------------------- the record */
  React.useEffect(() => {
    if (!ready || !api.current || !scene) return;
    api.current.load(scene);
    draw();
  }, [ready, scene]);

  const opts = React.useCallback(
    () => ({ aspect, axonElevationDeg: parseFloat(tokens.current['axon-elevation-deg']) || undefined }),
    [aspect],
  );

  const draw = React.useCallback(() => {
    const a = api.current;
    if (!a || !live.current) return;
    a.resize(size.width, size.height);
    a.setPose(live.current, aspect);
    a.setClip(live.current.cut ? live.current.cut.z_ft : null);
    a.render();
  }, [size.width, size.height, aspect]);

  /* ---------------------------------------------------------------- the tween */
  const step = React.useCallback(() => {
    const an = anim.current;
    if (!an) return;
    const ms = an.ms;
    const t = ms <= 0 ? 1 : Math.min(1, (performance.now() - an.t0) / ms);
    live.current = tween(an.from, an.to, t);
    draw();
    if (t >= 1) { anim.current = null; live.current = an.to; draw(); return; }
    raf.current = requestAnimationFrame(step);
  }, [draw]);

  React.useEffect(() => {
    if (!ready || !scene || !view) return;
    const to = poseFor(view, scene, null, opts());
    if (!to) return;                                   // `free` is held by the pointer
    if (!live.current) { live.current = to; draw(); return; }
    // prefers-reduced-motion turns the tween into a cut, which is the setting's whole point.
    const reduce = typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduce) { live.current = to; draw(); return; }
    anim.current = { from: live.current, to, t0: performance.now(), ms: DUR_MS(tokens.current) };
    cancelAnimationFrame(raf.current);
    raf.current = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf.current);
  }, [ready, view, scene, opts, step, draw]);

  React.useEffect(() => { draw(); }, [size.width, size.height, draw]);
  React.useEffect(() => () => cancelAnimationFrame(raf.current), []);

  /* ---------------------------------------------------------------- the pointer

     The teardown discipline is PlateViewer.jsx's, deliberately: listeners held in a ref and
     removed on pointerup, pointercancel AND unmount, because a drag that outlives its element
     keeps a dead component alive and answering. */
  const endDrag = React.useCallback(() => {
    const d = drag.current;
    if (!d) return;
    window.removeEventListener('pointermove', d.move);
    window.removeEventListener('pointerup', d.up);
    window.removeEventListener('pointercancel', d.up);
    drag.current = null;
  }, []);
  React.useEffect(() => endDrag, [endDrag]);

  const onPointerDown = (e) => {
    if (e.button !== 0 || drag.current || !live.current) return;
    const start = { x: e.clientX, y: e.clientY, pose: live.current, moved: false };
    const move = (ev) => {
      const dx = ev.clientX - start.x;
      const dy = ev.clientY - start.y;
      if (!start.moved && Math.hypot(dx, dy) < 3) return;      // PAN_SLOP, as the loupe uses
      start.moved = true;
      anim.current = null;
      cancelAnimationFrame(raf.current);
      const p = start.pose;
      live.current = {
        ...p,
        view: 'free',
        azimuthDeg: p.azimuthDeg - dx * 0.4,
        // clamped, because past the poles the up vector flips and the house turns over
        elevationDeg: Math.max(-10, Math.min(90, p.elevationDeg + dy * 0.3)),
      };
      draw();
    };
    const up = () => {
      const moved = start.moved;
      endDrag();
      if (moved && onView && !isNamed(live.current, view, scene, opts())) onView('free');
      if (!moved && onPick && api.current) {
        const r = canvasRef.current.getBoundingClientRect();
        onPick(api.current.pick(start.x - r.left, start.y - r.top));
      }
    };
    drag.current = { move, up };
    window.addEventListener('pointermove', move);
    window.addEventListener('pointerup', up);
    window.addEventListener('pointercancel', up);
  };

  return (
    <div
      ref={wrapRef}
      data-nopan=""
      style={{ position: 'relative', width: '100%', height, background: 'var(--paper)' }}
    >
      <canvas
        ref={canvasRef}
        role="img"
        data-round-canvas=""
        aria-label={`the model, seen at ${view || 'a free view'}`}
        onPointerDown={onPointerDown}
        style={{ display: 'block', width: '100%', height: '100%', cursor: drag.current ? 'grabbing' : 'grab' }}
      />
      {failed ? (
        <div
          data-round-unavailable=""
          style={{
            position: 'absolute', inset: 0, display: 'flex', alignItems: 'center',
            justifyContent: 'center', padding: '0 12%', textAlign: 'center',
            font: 'italic var(--fw-reg) 13px/1.5 var(--serif)', color: 'var(--ink-2)',
          }}
        >
          COULD NOT EVALUATE — {failed}
        </div>
      ) : null}
    </div>
  );
}

export default Round;
