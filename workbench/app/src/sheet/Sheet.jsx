/* The sheet — a mounted plate in The Drawn Language, drawn ONLY from the plan record
   and its placement (P6): rooms, walls, bay lines, windows on exterior walls, doors
   with swing arcs, dimensions, scale bar, north arrow, lot and setback where the site
   is declared. Units are FEET; strokes are px and non-scaling — a pen is a pen.

   Model frame per build/render_plan.py: x east, y north, origin SW. Screen y is
   flipped inside <Model>. Ported from the mockup Sheet; generalised from its one
   hardcoded 64×44 plan to any footprint. */
import React from 'react';
import { WALL_T, PART_T, levelRooms, partitions, windows, doors, bayLines, litWalls,
         divergence, interpunctTitle, relaxationMarks, ft } from './derive.js';
import { fitLabel, fitLine, useFontMetrics } from './label.js';

function DimRun({ from, to, at, vertical, stops }) {
  const marks = stops || [from, to];
  return (
    <g>
      {vertical
        ? <line x1={at} y1={-to} x2={at} y2={-from} stroke="var(--draw-dim)" strokeWidth=".7" vectorEffect="non-scaling-stroke" />
        : <line x1={from} y1={at} x2={to} y2={at} stroke="var(--draw-dim)" strokeWidth=".7" vectorEffect="non-scaling-stroke" />}
      {marks.map((m, i) => vertical
        ? <line key={'t' + i} x1={at - 0.55} y1={-m - 0.55} x2={at + 0.55} y2={-m + 0.55}
            stroke="var(--draw-dim)" strokeWidth=".9" vectorEffect="non-scaling-stroke" />
        : <line key={'t' + i} x1={m - 0.55} y1={at + 0.55} x2={m + 0.55} y2={at - 0.55}
            stroke="var(--draw-dim)" strokeWidth=".9" vectorEffect="non-scaling-stroke" />)}
      {marks.slice(0, -1).map((m, i) => {
        const mid = (m + marks[i + 1]) / 2;
        const label = ft(marks[i + 1] - m);
        return vertical
          ? <text key={'v' + i} x={at - 0.7} y={-mid} fontSize=".95" fill="var(--ink-2)"
              fontFamily="var(--serif)" letterSpacing=".14" textAnchor="middle" dominantBaseline="middle"
              transform={`rotate(-90 ${at - 0.7} ${-mid})`}>{label}</text>
          : <text key={'h' + i} x={mid} y={at - 0.8} fontSize=".95" fill="var(--ink-2)"
              fontFamily="var(--serif)" letterSpacing=".14" textAnchor="middle">{label}</text>;
      })}
    </g>
  );
}

/* The opening resolved into a wall-local frame: the two jambs A and B, the direction the
   leaf swings, and the arc's sweep flag. Both wall orientations reduce to this, so a door
   TYPE is drawn once rather than twice — which is why every type below is a few lines. */
function doorFrame(d) {
  const w = d.w;
  const vert = d.horiz === false || d.wall === 'W' || d.wall === 'E';
  if (vert) {
    const x = d.x, y0 = -d.y - w / 2;
    const s = d.swingRight === false ? -1 : 1;
    return { w, vert, A: [x, y0], B: [x, y0 + w], nrm: [s, 0], sweep: s > 0 ? 1 : 0,
             rect: { x: x - 0.35, y: y0, width: 0.7, height: w } };
  }
  const x0 = d.x - w / 2, y = -d.y;
  const t = d.swingUp !== false ? -1 : 1;
  return { w, vert, A: [x0, y], B: [x0 + w, y], nrm: [0, t], sweep: t < 0 ? 1 : 0,
           rect: { x: x0, y: y - 0.35, width: w, height: 0.7 } };
}

const add = (p, v, k) => [p[0] + v[0] * k, p[1] + v[1] * k];
const mid = (a, b) => [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];

function Leaf({ hinge, nrm, len, to, sweep }) {
  const open = add(hinge, nrm, len);
  return (
    <g>
      <line x1={hinge[0]} y1={hinge[1]} x2={open[0]} y2={open[1]}
        stroke="var(--ink)" strokeWidth="1.4" vectorEffect="non-scaling-stroke" />
      <path d={`M ${open[0]} ${open[1]} A ${len} ${len} 0 0 ${sweep} ${to[0]} ${to[1]}`}
        fill="none" stroke="var(--hair)" strokeWidth=".8" vectorEffect="non-scaling-stroke" />
    </g>
  );
}

/* Jamb ticks: the reveal drawn across the wall, which is how a cased opening — an
   opening with a lining and NO leaf — is distinguished from a doorway on a plan. */
function Jambs({ A, B, vert }) {
  const t = 0.55;
  const tick = (p, i) => vert
    ? <line key={i} x1={p[0] - t} y1={p[1]} x2={p[0] + t} y2={p[1]}
        stroke="var(--ink)" strokeWidth="1.2" vectorEffect="non-scaling-stroke" />
    : <line key={i} x1={p[0]} y1={p[1] - t} x2={p[0]} y2={p[1] + t}
        stroke="var(--ink)" strokeWidth="1.2" vectorEffect="non-scaling-stroke" />;
  return <g>{[A, B].map(tick)}</g>;
}

/* A door opening: vellum break in the wall, then whatever the record's `type` says it is.
   WP-6.1 — until now `type` was read by NOTHING in any renderer, so the Tidewater plan's
   5 ft pair of doors between drawing room and dining room and the 6 ft cased opening into
   the stair hall were both drawn as one enormous hinged leaf with an arc to match. Those
   two marks are what a reader called "a massive door" and "no rhyme or reason". */
function DoorMark({ d }) {
  const f = doorFrame(d);
  const type = d.type || 'swing';
  const M = mid(f.A, f.B);
  const common = { 'data-door-type': type, 'data-door-w': d.w };
  const brk = <rect {...f.rect} fill="var(--paper-lit)" />;

  if (type === 'double') {
    return (
      <g {...common}>
        {brk}
        <Leaf hinge={f.A} nrm={f.nrm} len={f.w / 2} to={M} sweep={f.sweep} />
        <Leaf hinge={f.B} nrm={f.nrm} len={f.w / 2} to={M} sweep={1 - f.sweep} />
      </g>
    );
  }
  if (type === 'cased-opening' || type === 'open') {
    return <g {...common}>{brk}<Jambs A={f.A} B={f.B} vert={f.vert} /></g>;
  }
  if (type === 'pocket') {
    // the leaf slides into the wall: shown as the slot it runs in, not as a swing
    const slot = f.vert
      ? { x: f.rect.x, y: f.A[1] - f.w, width: 0.7, height: f.w }
      : { x: f.A[0] - f.w, y: f.rect.y, width: f.w, height: 0.7 };
    return (
      <g {...common}>
        {brk}
        <rect {...slot} fill="none" stroke="var(--ink-2)" strokeWidth=".7"
          strokeDasharray="1.4 1" vectorEffect="non-scaling-stroke" />
        <Jambs A={f.A} B={f.B} vert={f.vert} />
      </g>
    );
  }
  if (type === 'garage' || type === 'bulkhead') {
    // an overhead or a cellar door: no plan swing to draw, so the leaf is shown in its
    // closed position on the wall line and the opening is left otherwise clear
    return (
      <g {...common}>
        {brk}
        <line x1={f.A[0]} y1={f.A[1]} x2={f.B[0]} y2={f.B[1]}
          stroke="var(--ink)" strokeWidth="1.4"
          strokeDasharray={type === 'bulkhead' ? '1.6 1.1' : undefined}
          vectorEffect="non-scaling-stroke" />
        <Jambs A={f.A} B={f.B} vert={f.vert} />
      </g>
    );
  }
  return (
    <g {...common}>
      {brk}
      <Leaf hinge={f.A} nrm={f.nrm} len={f.w} to={f.B} sweep={f.sweep} />
    </g>
  );
}

/* A window: vellum break, glazing bar at fine weight, sill projecting past the jambs. */
function WindowMark({ w }) {
  const t = 0.75;
  const vert = w.wall === 'W' || w.wall === 'E';
  const r = vert
    ? { x: w.wall === 'W' ? -t : w.x, y: -w.y - w.w / 2, width: t, height: w.w }
    : { x: w.x - w.w / 2, y: w.wall === 'S' ? 0 : -w.y - t, width: w.w, height: t };
  const sill = vert
    ? <line x1={r.x + (w.wall === 'W' ? -0.35 : t + 0.35)} y1={r.y - 0.5}
        x2={r.x + (w.wall === 'W' ? -0.35 : t + 0.35)} y2={r.y + r.height + 0.5}
        stroke="var(--ink)" strokeWidth="1.2" vectorEffect="non-scaling-stroke" />
    : <line x1={r.x - 0.5} y1={r.y + (w.wall === 'S' ? t + 0.35 : -0.35)}
        x2={r.x + r.width + 0.5} y2={r.y + (w.wall === 'S' ? t + 0.35 : -0.35)}
        stroke="var(--ink)" strokeWidth="1.2" vectorEffect="non-scaling-stroke" />;
  return (
    <g>
      <rect {...r} fill="var(--paper-lit)" stroke="var(--ink)" strokeWidth="1" vectorEffect="non-scaling-stroke" />
      {vert
        ? <line x1={r.x + t / 2} y1={r.y} x2={r.x + t / 2} y2={r.y + r.height}
            stroke="var(--ink-2)" strokeWidth=".8" vectorEffect="non-scaling-stroke" />
        : <line x1={r.x} y1={r.y + t / 2} x2={r.x + r.width} y2={r.y + t / 2}
            stroke="var(--ink-2)" strokeWidth=".8" vectorEffect="non-scaling-stroke" />}
      {sill}
    </g>
  );
}

/* Drag handle on a selected room's edge. Deltas are computed in model feet via the
   SVG's own CTM; on release the new size is handed back so the WORKBENCH writes it
   into the record — the geometry itself is never edited (P6). Snaps to the half-foot,
   and harder to a bay line when within 0.75 ft of one. */
function DragHandle({ x, y, axis, room, bays, onCommit }) {
  const ref = React.useRef(null);
  const [delta, setDelta] = React.useState(0);

  function toModel(e) {
    const svg = ref.current.ownerSVGElement;
    const pt = new DOMPoint(e.clientX, e.clientY).matrixTransform(svg.getScreenCTM().inverse());
    return { x: pt.x, y: -pt.y };
  }
  function down(e) {
    e.stopPropagation();
    e.target.setPointerCapture(e.pointerId);
    const start = toModel(e);
    const px = { x: e.clientX, y: e.clientY };
    let moved = false;
    const move = (ev) => {
      if (Math.abs(ev.clientX - px.x) + Math.abs(ev.clientY - px.y) >= 3) moved = true;
      const now = toModel(ev);
      setDelta(axis === 'x' ? now.x - start.x : now.y - start.y);
    };
    const detach = () => {
      setDelta(0);
      e.target.removeEventListener('pointermove', move);
      e.target.removeEventListener('pointerup', up);
      e.target.removeEventListener('pointercancel', cancel);
      e.target.removeEventListener('lostpointercapture', cancel);
    };
    const cancel = () => detach();   // touch-scroll or capture loss: drop the drag cleanly
    const up = (ev) => {
      /* A CLICK IS NOT A RESIZE. This committed unconditionally, and with a zero delta it
         still rewrote the record twice over: `Math.round(size * 2) / 2` quantised an
         off-grid dimension to the half-foot, and the bay snap below moved it by up to
         0.75 ft — from a gesture nobody made. It also writes the PLACEMENT's dimension
         onto the DECLARED record, so a stray click baked the solver's own relaxation in
         and the sheet's △ marks quietly went away. It never fired while the handle was
         painted over by its partition; making the handle reachable made it live. */
      if (!moved) {
        try { e.target.releasePointerCapture(ev.pointerId); } catch { /* already lost */ }
        detach();
        return;
      }
      const now = toModel(ev);
      let d = axis === 'x' ? now.x - start.x : now.y - start.y;
      let size = Math.max(4, (axis === 'x' ? room.w : room.h) + d);
      size = Math.round(size * 2) / 2;
      if (axis === 'x') {
        for (const b of bays) {
          if (Math.abs(room.x + size - b) < 0.75) { size = b - room.x; break; }
        }
      }
      try { e.target.releasePointerCapture(ev.pointerId); } catch { /* already lost */ }
      detach();
      onCommit(axis, size);
    };
    e.target.addEventListener('pointermove', move);
    e.target.addEventListener('pointerup', up);
    e.target.addEventListener('pointercancel', cancel);
    e.target.addEventListener('lostpointercapture', cancel);
  }

  const hx = axis === 'x' ? x + delta : x;
  const hy = axis === 'y' ? y + delta : y;
  return (
    <g ref={ref}>
      {delta !== 0 && (axis === 'x'
        ? <line x1={hx} y1={-room.y} x2={hx} y2={-room.y - room.h}
            stroke="var(--gilt-deep)" strokeWidth="1.2" strokeDasharray="2 2" vectorEffect="non-scaling-stroke" />
        : <line x1={room.x} y1={-hy} x2={room.x + room.w} y2={-hy}
            stroke="var(--gilt-deep)" strokeWidth="1.2" strokeDasharray="2 2" vectorEffect="non-scaling-stroke" />)}
      <rect data-nopan="" x={hx - 0.8} y={axis === 'y' ? -hy - 0.8 : -room.y - room.h / 2 - 0.8}
        width={1.6} height={1.6}
        fill="var(--paper-lit)" stroke="var(--gilt-deep)" strokeWidth="1.2"
        vectorEffect="non-scaling-stroke"
        style={{ cursor: axis === 'x' ? 'ew-resize' : 'ns-resize' }}
        onPointerDown={down} />
    </g>
  );
}

/* Room lettering, fitted to the room it names. The pad is the partition drawn on the
   room's own edge plus a hair of air: a label that touches the wall reads as running
   into it even when it stops short. A room too small for its name and its dimensions
   keeps the name — the dimension string is on the dimension lines as well, the name is
   nowhere else. */
const LABEL_PAD = PART_T / 2 + 0.55;
const DIM_GAP = 0.42;

function layLabel(r, boxW, boxH) {
  if (boxW <= 0.5 || boxH <= 0.5) return null;
  const dim = fitLine(`${ft(r.w)} × ${ft(r.h)}`, boxW, { preferred: 0.9, min: 0.55 });
  const wantDim = Math.min(r.w, r.h) >= 5.5 && Math.max(r.w, r.h) >= 8 && dim.size >= 0.62;
  const reserve = wantDim ? dim.size * 1.15 + DIM_GAP : 0;
  const name = fitLabel(r.name.toUpperCase(), boxW, Math.max(1, boxH - reserve),
    { preferred: 1.25, min: 0.55, track: 0.3, lead: 1.24, maxLines: 3 });
  if (!name) return null;
  // the dimensions go only where the name still reads at a working size beside them
  const showDim = wantDim && name.size >= 0.7;
  return { name, dim: showDim ? dim : null,
           block: name.height + (showDim ? DIM_GAP + dim.size * 1.15 : 0) };
}

function roomLabel(r) {
  const flat = layLabel(r, r.w - LABEL_PAD * 2, r.h - LABEL_PAD * 2);
  // A closet, a stair or a hyphen is a slot: its name will not go across it at any size
  // that can still be read, and the draughtsman's answer has always been to turn the
  // lettering to run with the room. Turned only when it earns a materially larger
  // letter — a label turned for a few percent is a label the reader has to work at.
  const turned = r.h > r.w * 1.3
    ? layLabel(r, r.h - LABEL_PAD * 2, r.w - LABEL_PAD * 2) : null;
  const useTurned = turned && (!flat || turned.name.size > flat.name.size * 1.15);
  const L = useTurned ? turned : flat;
  if (!L) return null;
  return { ...L, turned: !!useTurned, cx: r.x + r.w / 2, cy: -r.y - r.h / 2 };
}

export function Sheet({ plan, placement, levelIndex = 0, overlays, ghost, selectedRoom,
                        onPickRoom, onResizeRoom, title, subtitle, styleName }) {
  useFontMetrics();          // re-fit every label once EB Garamond itself has arrived
  const ov = overlays || {};
  const fp = placement?.footprint || {};
  const W = fp.width_ft || 40, H = fp.depth_ft || 30;
  const rooms = levelRooms(plan, placement, levelIndex);
  const parts = partitions(rooms, W, H);
  // doors first, then windows into what the doors have left: an opening may not be drawn
  // over another opening, and on this sheet the door is the one that keeps its place
  const drs = doors(rooms, W, H);
  const wins = windows(rooms, W, H, 0.6, drs.exterior);
  const diverged = divergence(rooms);
  const divergedIds = new Set(diverged.map((d) => d.id));
  const bays = bayLines(fp);
  // plan schema 0.3.0 (WP-6.2): the stair is an object on the record, or it is absent —
  // never an empty room presented as a finished one
  const stair = placement?.stair || plan?.stair;
  const ghostRooms = ghost != null ? levelRooms(plan, placement, ghost) : [];
  const roomsMeta = ov.meta || {};

  const site = plan.site || plan.context || {};
  const lotW = site.lot_width_ft, lotD = site.lot_depth_ft;
  const hasLot = !!(lotW && lotD);
  const xOff = hasLot ? (site.setback_side_ft ?? Math.max(0, (lotW - W) / 2)) : 0;
  const yOff = hasLot ? (site.setback_front_ft || 0) : 0;

  // viewBox in model feet (y already negated screenward): margins for street, dims, bar
  const mL = 11, mR = 15, mT = hasLot ? Math.max(15, lotD - H - yOff + 8) : 15, mB = hasLot ? Math.max(9, yOff + 7) : 9;
  const view = { x: -mL, y: -H - mT, w: W + mL + mR, h: H + mT + mB + 6 };
  // a zero-width space after each interpunct: the title may fold at a word boundary,
  // and never inside a word — without it 'TIDEWATER·GEORGIAN,·FIVE·BAYS,·CAREFULLY·
  // PLANNED' is one unbreakable word and the plate clips whatever does not fit
  const interpunct = interpunctTitle(title);
  const relax = placement?.geometry_report?.relaxations;
  const rxMarks = relaxationMarks(relax?.marks, levelIndex, W, H);

  return (
    <div style={{ position: 'relative', background: 'var(--paper)', border: '1px solid var(--ink-2)',
      boxShadow: 'var(--shadow-plate)', padding: '18px 22px 14px' }}>
      <div style={{ textAlign: 'center', margin: '4px 0 2px' }}>
        <div style={{ font: 'var(--fw-med) 17px/1.35 var(--serif)', letterSpacing: 'var(--tr-drawing)',
          textTransform: 'uppercase', color: 'var(--ink)' }}>{interpunct}</div>
        <div style={{ font: 'var(--fw-reg) 11px/1.4 var(--serif)', letterSpacing: 'var(--tr-caps)',
          textTransform: 'uppercase', color: 'var(--ink-2)', marginTop: 4 }}>
          {styleName} &nbsp;·&nbsp; {subtitle}
        </div>
        <div style={{ width: 150, height: 0, borderTop: '1px solid var(--rule)', margin: '9px auto 0' }} />
      </div>

      <svg viewBox={`${view.x} ${view.y} ${view.w} ${view.h}`}
        style={{ display: 'block', width: '100%' }} role="img" aria-label={title}>
        <defs>
          <pattern id="ghosthatch" width="1.6" height="1.6" patternTransform="rotate(45)" patternUnits="userSpaceOnUse">
            <line x1="0" y1="0" x2="0" y2="1.6" stroke="var(--hair)" strokeWidth=".2" />
          </pattern>
        </defs>

        {/* street, lot and setback envelope — only when the record declares a site */}
        {hasLot && (
          <g>
            <line x1={-xOff - 2} y1={yOff + 2.5} x2={lotW - xOff + 2} y2={yOff + 2.5}
              stroke="var(--ink-2)" strokeWidth="1.2" vectorEffect="non-scaling-stroke" />
            <text x={-xOff - 2} y={yOff + 4.2} fontSize="1" fontFamily="var(--serif)" fill="var(--ink-2)"
              letterSpacing=".3">STREET · LOT {ft(lotW)} WIDE</text>
            <rect x={-xOff} y={-(lotD - yOff)} width={lotW} height={lotD} fill="none"
              stroke="var(--hair)" strokeWidth=".8" strokeDasharray="1.5 5" strokeLinecap="round"
              vectorEffect="non-scaling-stroke" />
            <text x={-xOff + 0.6} y={-(lotD - yOff) - 0.7} fontSize=".85" fontFamily="var(--serif)"
              fontStyle="italic" fill="var(--ink-2)">setback envelope</text>
          </g>
        )}

        {/* the construction grid — left visible, at hairline */}
        {bays.map((x) => (
          <g key={'b' + x}>
            <line x1={x} y1={-H - 3} x2={x} y2={4} stroke="var(--hair)" strokeWidth=".7" vectorEffect="non-scaling-stroke" />
            <text x={x} y={-H - 3.8} fontSize=".8" fontFamily="var(--serif)" fill="var(--hair)"
              textAnchor="middle">{Math.round(x)}′</text>
          </g>
        ))}

        {/* ghost of the other level — dashed, at hairline */}
        {ghostRooms.length > 0 && (
          <g opacity=".9">
            {ghostRooms.map((r) => (
              <rect key={'g' + r.id} x={r.x} y={-r.y - r.h} width={r.w} height={r.h} fill="url(#ghosthatch)"
                stroke="var(--hair)" strokeWidth=".6" strokeDasharray="3 2" vectorEffect="non-scaling-stroke" />
            ))}
          </g>
        )}

        {/* interior floor: reserved vellum */}
        <rect x={0} y={-H} width={W} height={H} fill="var(--paper-lit)" />

        {/* analytic overlays, glazed on the sheet */}
        {/* privacy_rank runs 1-5 across rooms/, not 1-6, so dividing by 6 meant the most
            private room never reached the top of the ramp. And `|| 1` drew a room type the
            catalogue has no rank for exactly like the LEAST private one — unjudged rendered
            as evaluated, on a sheet. An unranked room is now left unglazed. */}
        {ov.privacy && rooms.map((r) => {
          const rank = roomsMeta[r.type]?.privacy_rank;
          if (!rank) return null;
          return <rect key={'pv' + r.id} x={r.x} y={-r.y - r.h} width={r.w} height={r.h}
            fill="var(--sepia)" opacity={0.04 + ((rank - 1) / 4) * 0.20} />;
        })}
        {ov.daylight && rooms.map((r) => litWalls(r, W, H).map((wall) => {
          // gated on the walls the placement actually lit — the overlay may never
          // claim daylight from a window the sheet does not draw
          const head = r.window_head_ft || 7;
          const mult = roomsMeta[r.type]?.daylight_multiplier || 2.25;
          const reach = mult * head;
          let box;
          if (wall === 'S') box = { x: r.x, y: -r.y - Math.min(r.h, reach), width: r.w, height: Math.min(r.h, reach) };
          else if (wall === 'N') box = { x: r.x, y: -r.y - r.h, width: r.w, height: Math.min(r.h, reach) };
          else if (wall === 'W') box = { x: r.x, y: -r.y - r.h, width: Math.min(r.w, reach), height: r.h };
          else box = { x: Math.max(r.x, r.x + r.w - reach), y: -r.y - r.h, width: Math.min(r.w, reach), height: r.h };
          return <rect key={'dl' + r.id + wall} {...box} fill="var(--green)" opacity=".16" />;
        }))}
        {ov.wet && rooms.filter((r) => {
          const m = roomsMeta[r.type] || {};
          return m.plumbing === 'heavy' || m.function_class === 'sanitary';
        }).map((r) => (
          <g key={'wt' + r.id}>
            <rect x={r.x} y={-r.y - r.h} width={r.w} height={r.h} fill="var(--blue)" opacity=".2" />
            <circle cx={r.x + r.w / 2} cy={-r.y - r.h / 2} r="1.1" fill="none" stroke="var(--blue-deep)"
              strokeWidth="1.1" vectorEffect="non-scaling-stroke" />
          </g>
        ))}

        {/* rooms — clickable, because every mark reaches its record (P6) */}
        {rooms.map((r) => {
          const sel = selectedRoom === r.id;
          // ∗ — this room is DRAWN at a size its own record does not declare. The sheet
          // has always printed the placed rectangle (it must; it is what was drawn) and
          // never said what it departed from, so a kitchen declared 16 × 20 and placed at
          // 63% of that area read as a measurement of the declared room.
          const off = divergedIds.has(r.id);
          const lab = roomLabel(r);
          const decl = off && r.declared_width_ft && r.declared_length_ft
            ? ` — the record declares ${ft(r.declared_width_ft)} × ${ft(r.declared_length_ft)}`
            : '';
          return (
            <g key={r.id} data-room={r.id} data-diverged={off ? '' : undefined}
              onClick={onPickRoom ? () => onPickRoom(r) : undefined}
              style={{ cursor: onPickRoom ? 'pointer' : 'default' }}>
              <title>{`${r.name} — ${ft(r.w)} × ${ft(r.h)}${decl}`}</title>
              <rect x={r.x} y={-r.y - r.h} width={r.w} height={r.h}
                fill={sel ? 'var(--wash-salmon-1)' : 'transparent'}
                stroke={sel ? 'var(--salmon-deep)' : 'transparent'} strokeWidth="1.2" vectorEffect="non-scaling-stroke" />
              {lab && (
                <g transform={lab.turned ? `rotate(-90 ${lab.cx} ${lab.cy})` : undefined}>
                  {lab.name.lines.map((ln, i) => (
                    <text key={'n' + i} x={lab.cx + lab.name.track / 2}
                      y={lab.cy - lab.block / 2 + (i + 0.5) * lab.name.lead}
                      fontSize={lab.name.size} fontFamily="var(--serif)"
                      letterSpacing={lab.name.track} fill="var(--ink)"
                      textAnchor="middle" dominantBaseline="middle">{ln}</text>
                  ))}
                  {lab.dim && (
                    <text x={lab.cx + lab.dim.track / 2}
                      y={lab.cy - lab.block / 2 + lab.name.height + DIM_GAP + lab.dim.size * 0.6}
                      fontSize={lab.dim.size} fontFamily="var(--serif)" letterSpacing={lab.dim.track}
                      fill="var(--ink-2)" textAnchor="middle" dominantBaseline="middle">{lab.dim.text}</text>
                  )}
                  {/* the ∗ sits BESIDE the fitted dimension, never inside it — a mark
                      added to the string shrinks the fit until the dimension drops out
                      of every narrow room, which is what happened to the void
                      disclosure and what the Python renderer's line is frozen against */}
                  {off && lab.dim && (
                    <text x={lab.cx + lab.dim.width / 2 + lab.dim.size * 0.45}
                      y={lab.cy - lab.block / 2 + lab.name.height + DIM_GAP + lab.dim.size * 0.6}
                      fontSize={lab.dim.size} fontFamily="var(--serif)"
                      fill="var(--gilt-deep)" dominantBaseline="middle">∗</text>
                  )}
                </g>
              )}
              {/* the divergence mark for a room too small to carry its dimension string.
                  OUTSIDE the label group on purpose: that group may be rotated -90 for a
                  slot room, and a mark placed in the room's corner inside it is rotated
                  about the label's centre and lands outside the room. e2e/walk.mjs caught
                  it twice — first under the name on a 9 x 5 cellar stair, then in the
                  corner of a 4 x 25 butler's pantry — because it measures where the glyph
                  actually is rather than where it was meant to be. */}
              {off && !(lab && lab.dim) && (
                <text x={r.x + r.w - LABEL_PAD} y={-r.y - r.h + LABEL_PAD}
                  fontSize={Math.min(0.75, r.w * 0.3, r.h * 0.3)}
                  fontFamily="var(--serif)" fill="var(--gilt-deep)"
                  textAnchor="end" dominantBaseline="hanging">∗</text>
              )}
            </g>
          );
        })}

        {/* partitions — pale sepia flesh, ink skin */}
        {parts.map((p, i) => (
          <rect key={'pt' + i} x={p.x} y={-p.y - p.h} width={p.w} height={p.h} fill="var(--poche-partition)"
            stroke="var(--ink)" strokeWidth="1.4" vectorEffect="non-scaling-stroke" />
        ))}

        {/* poché — salmon flesh, coal skin. The cut line bounds all poche. */}
        <path d={`M${-WALL_T} ${WALL_T} L${W + WALL_T} ${WALL_T} L${W + WALL_T} ${-H - WALL_T} L${-WALL_T} ${-H - WALL_T} Z ` +
                 `M0 0 L0 ${-H} L${W} ${-H} L${W} 0 Z`}
          fillRule="evenodd" fill="var(--poche-masonry)" stroke="var(--draw-cut)"
          strokeWidth="2.6" vectorEffect="non-scaling-stroke" />

        {/* openings. Windows are laid into the run the doors left, so a door is never
            painted over by a window again — but the doors are still drawn AFTER, because
            a break in the poché belongs on top of the wall it breaks. */}
        {wins.map((w, i) => <WindowMark key={'w' + i} w={w} />)}
        {drs.exterior.map((d, i) => (
          <DoorMark key={'ed' + i} d={{ x: d.x, y: d.y, w: d.w, type: d.type,
            horiz: !(d.wall === 'W' || d.wall === 'E'),
            wall: d.wall, swingUp: d.wall === 'S', swingRight: d.wall === 'W' }} />
        ))}
        {drs.interior.map((d, i) => <DoorMark key={'d' + i} d={d} />)}

        {/* WP-6.2 — the stair, drawn from plan.stair and from nothing else. There has never
            been a line of stair-drawing code in this system: a stair hall was an empty
            rectangle with lettering in it, while rooms/stair-hall.json carried the flight
            itself as furniture ([120, 78] in, "dog-leg with half landing") and
            build/structure.py computed its risers into a section no plan ever saw. */}
        {stair && (stair.level ?? 0) === levelIndex && (stair.flights || []).length > 0 && (
          <g data-stair="">
            {stair.flights.map((f, i) => {
              const across = f.direction === 'E' || f.direction === 'W';
              const n = Math.max(1, f.treads || 1);
              const ticks = [];
              for (let t = 1; t < n; t++) {
                if (across) {
                  const tx = f.x_ft + f.width_ft * (t / n);
                  ticks.push(<line key={t} x1={tx} y1={-f.y_ft} x2={tx} y2={-f.y_ft - f.depth_ft}
                    stroke="var(--ink-2)" strokeWidth=".6" vectorEffect="non-scaling-stroke" />);
                } else {
                  const ty = f.y_ft + f.depth_ft * (t / n);
                  ticks.push(<line key={t} x1={f.x_ft} y1={-ty} x2={f.x_ft + f.width_ft} y2={-ty}
                    stroke="var(--ink-2)" strokeWidth=".6" vectorEffect="non-scaling-stroke" />);
                }
              }
              return (
                <g key={'fl' + i}>
                  <rect x={f.x_ft} y={-f.y_ft - f.depth_ft} width={f.width_ft} height={f.depth_ft}
                    fill="none" stroke="var(--ink-2)" strokeWidth=".9" vectorEffect="non-scaling-stroke" />
                  {ticks}
                </g>
              );
            })}
            <text x={stair.flights[0].x_ft + stair.flights[0].width_ft / 2}
              y={-stair.flights[0].y_ft - stair.flights[0].depth_ft / 2}
              fontSize="1" fontFamily="var(--serif)" letterSpacing=".18"
              fill="var(--gilt-deep)" textAnchor="middle" dominantBaseline="middle">
              UP {stair.risers}R
            </text>
          </g>
        )}
        {stair && (stair.level ?? 0) === levelIndex && stair.unplaced && stair.well && (
          <text data-stair="refused" x={stair.well.x_ft + stair.well.width_ft / 2}
            y={-stair.well.y_ft - stair.well.depth_ft / 2 + 1.6}
            fontSize=".85" fontFamily="var(--serif)" fill="var(--gilt-deep)"
            textAnchor="middle" dominantBaseline="middle">
            <title>{stair.unplaced.reason}</title>
            stair not drawn — see record
          </text>
        )}

        {/* fixtures, from room.fixture_layout and from nothing else */}
        {rooms.map((r) => (r.fixture_layout || [])
          .filter((f) => !f.unplaced && f.x_ft != null)
          .map((f, i) => (
            <rect key={r.id + 'fx' + i} x={f.x_ft} y={-f.y_ft - f.depth_ft}
              width={f.width_ft} height={f.depth_ft} fill="none" stroke="var(--ink-2)"
              strokeWidth=".6" strokeDasharray="1.4 1" vectorEffect="non-scaling-stroke">
              <title>{f.item}</title>
            </rect>
          )))}

        {/* dimensions — ticks, primes, never decimal feet */}
        <DimRun from={0} to={W} at={2.6} stops={[0, ...bays, W]} />
        <DimRun from={0} to={W} at={5.2} stops={[0, W]} />
        <DimRun from={0} to={H} at={W + 3} vertical stops={[0, H]} />

        {/* north — an instrument, not an ornament: screen-up is model-north */}
        <g transform={`translate(${W + 10},${-H + 2})`}>
          <circle cx="0" cy="0" r="2.6" fill="none" stroke="var(--ink)" strokeWidth="1" vectorEffect="non-scaling-stroke" />
          <line x1="0" y1="2.6" x2="0" y2="-2.6" stroke="var(--ink)" strokeWidth=".9" vectorEffect="non-scaling-stroke" />
          <path d="M0 -2.6 L-0.55 -0.6 L0.55 -0.6 Z" fill="var(--coal)" />
          <text x="0" y="-3.4" fontSize="1" fontFamily="var(--serif)" letterSpacing=".2"
            fill="var(--ink-2)" textAnchor="middle">N</text>
        </g>

        {/* P7 — a compromise is counted AND appears on the drawing, at its location (OQ 33).
            Until 26 Aug 2026 the solvers recorded a relaxation as a bare number, so this sheet
            could print an honest tally and had nothing to place a mark with: the count was true
            and the drawing was silent about where the truth applied. Each mark is a cut that
            missed the structural bay — a joist run that does not land on a bearing wall — drawn
            as a hollow triangle on the line itself, in ink and not in colour, because colour in
            this system names a material and never flags a condition. Where the mark goes is
            `relaxationMarks` in derive.js — and an unlocatable one is named in the caption
            rather than drawn somewhere plausible.

            The dashed run is `pointerEvents: none`. It is an annotation, not a control: a
            hairline drawn across a room was swallowing the click that selects the room under
            it, and an affordance defeated by a tick over it is an affordance that does not
            exist. The triangle keeps its pointer events, because it is a visible glyph with a
            tooltip of its own and clicking a mark is a thing a reader means to do. */}
        {rxMarks.drawn.map(({ mark: m, runs, at }, i) => {
          const isV = m.axis === 'x';
          const [gx, gy] = isV ? [m.at_ft, -at] : [at, -m.at_ft];
          return (
            <g key={'rx' + i}>
              {runs.map(([lo, hi], j) => {
                const [x1, y1, x2, y2] = isV
                  ? [m.at_ft, -lo, m.at_ft, -hi]
                  : [lo, -m.at_ft, hi, -m.at_ft];
                return (
                  <line key={j} x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--ink-2)"
                    strokeWidth=".55" strokeDasharray="1.2 1.2" pointerEvents="none"
                    vectorEffect="non-scaling-stroke" />
                );
              })}
              <path d={`M ${gx} ${gy - 1.15} L ${gx + 1.0} ${gy + 0.75} L ${gx - 1.0} ${gy + 0.75} Z`}
                fill="var(--paper)" stroke="var(--ink)" strokeWidth=".45"
                vectorEffect="non-scaling-stroke" />
              <title>{`${m.off_ft} ft off the bay line — this cut is a joist run that does not land on a bearing wall`}</title>
            </g>
          );
        })}

        {/* scale bar — drawn, alternating, never merely stated */}
        <g transform={`translate(${-mL + 2},${mB - 2.6})`}>
          {[0, 1, 2, 3].map((i) => (
            <rect key={i} x={i * 8} y="0" width="8" height=".8" fill={i % 2 ? 'none' : 'var(--ink)'}
              stroke="var(--ink)" strokeWidth=".5" vectorEffect="non-scaling-stroke" />
          ))}
          {[0, 8, 16, 24, 32].map((x) => (
            <line key={'sb' + x} x1={x} y1="-.6" x2={x} y2="1.4" stroke="var(--ink)" strokeWidth=".6" vectorEffect="non-scaling-stroke" />
          ))}
          <text x="0" y="3" fontSize=".9" fontFamily="var(--serif)" letterSpacing=".18" fill="var(--ink-2)">0</text>
          <text x="16" y="3" fontSize=".9" fontFamily="var(--serif)" letterSpacing=".18" fill="var(--ink-2)" textAnchor="middle">16</text>
          <text x="32" y="3" fontSize=".9" fontFamily="var(--serif)" letterSpacing=".18" fill="var(--ink-2)" textAnchor="middle">32 FT</text>
        </g>

        {/* Legend for the △. The mark has been drawn since WP-5.2 and named only in the
            caption's running prose, where a reader meeting it on the drawing had nothing
            to read it BY — reported as arrows that "seem to point to anything and
            everything". A symbol a drawing uses is a symbol the drawing has to define. */}
        {relax?.count ? (
          <g data-legend="relaxation" transform={`translate(${W - 16},${mB - 2.2})`}>
            <path d="M 0 -1.15 L 1.0 0.75 L -1.0 0.75 Z" fill="var(--paper)"
              stroke="var(--ink)" strokeWidth=".45" vectorEffect="non-scaling-stroke" />
            <text x="2.1" y="0.7" fontSize=".95" fontFamily="var(--serif)" letterSpacing=".1"
              fill="var(--ink-2)">a cut off the bay line — no bearing wall under it</text>
          </g>
        ) : null}

        {/* Drag a wall on the bay grid: handles on the selected room's east and north
            edges; release writes back to the record and the validator re-scores.
            LAST in the sheet, and that is the fix rather than the habit — a handle
            drawn with the rooms sat under the partition on the very wall line it was
            offered for, so `elementFromPoint` at the handle returned the partition and
            the gesture the caption promised could not be started at all. An affordance
            painted over is an affordance that does not exist. */}
        {onResizeRoom && rooms.filter((r) => r.id === selectedRoom).map((r) => (
          <g key={'h' + r.id}>
            <DragHandle x={r.x + r.w} y={r.y + r.h / 2} axis="x" room={r} bays={bays}
              onCommit={(axis, size) => onResizeRoom(r, 'x', size)} />
            <DragHandle x={r.x + r.w / 2} y={r.y + r.h} axis="y" room={r} bays={bays}
              onCommit={(axis, size) => onResizeRoom(r, 'y', size)} />
          </g>
        ))}
      </svg>

      {/* plate caption. The title takes the space it needs and the note yields: with the
          title on `flex: 0 1 auto` beside a `1 1 34ch` note, a narrow plate folded
          'TIDEWATER·GEORGIAN,·FIVE·BAYS,·CAREFULLY·PLANNED' at its interpuncts and a
          reader saw 'WATER GEORGIAN, FIVE CAREFULLY PLANNED' — a different house, with
          nothing on the sheet to say the name had been cut. */}
      <div style={{ borderTop: '1px solid var(--rule)', margin: '4px 2px 0', padding: '8px 0 4px',
        display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: 24,
        flexWrap: 'wrap' }}>
        <div data-plate-title="" style={{ font: 'var(--fw-med) 10.5px/1.4 var(--serif)',
          letterSpacing: '.3em', textTransform: 'uppercase', color: 'var(--ink)',
          flex: '1 0 auto' }}>{interpunct}</div>
        <div data-plate-note="" style={{ font: 'italic var(--fw-reg) 13px/1.45 var(--serif)',
          color: 'var(--ink-2)', textAlign: 'right', flex: '1 1 34ch', minWidth: '22ch' }}>
          {/* "each marked \u25B3 where it falls" was a claim about every mark, and a mark the
              solver located nowhere is now not drawn at all rather than dropped at the
              middle of the plan. So the sentence counts what it actually marked. */}
          {relax
            ? `${relax.count} cut(s) off the bay line${relax.count ? `, worst ${relax.max_off_grid_ft} ft, ${rxMarks.drawn.length} marked \u25B3 on this level where it falls` : ''}. `
            : ''}
          {rxMarks.unlocated.length
            ? `${rxMarks.unlocated.length} cut(s) the solver located on no wall of this level \u2014 counted, not drawn. `
            : ''}
          {drs.undrawable.length
            ? `${drs.undrawable.length} declared door(s) without a drawable opening — in the record, not the linework: `
              + drs.undrawable.map((u) => `${u.from}–${u.to}`).join(', ') + '. '
            : ''}
          {wins.offFootprint
            ? `${wins.offFootprint} declared window(s) not situated on this footprint — declared, not drawn. `
            : ''}
          {wins.crowded
            ? `${wins.crowded} declared window(s) had no clear run left on their wall beside its doors — declared, not drawn. `
            : ''}
          {diverged.length
            ? `${diverged.length} room(s) are drawn at a size the record does not declare — worst `
              + `${diverged[0].name} ${diverged[0].pct > 0 ? '+' : ''}${diverged[0].pct.toFixed(0)}% by area, marked \u2217. `
            : ''}
          {drs.inferredWidths
            ? `${drs.inferredWidths} door(s) declare no width; drawn at the conventional leaf. `
            : ''}
          Exterior door openings are drawn at conventional mid-wall position, on a wall
          inferred from the room's declared exterior walls — the record does not state which.
          The grid remains — evidence the plan was composed, not arranged.
        </div>
      </div>
    </div>
  );
}

export { ft };
