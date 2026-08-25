/* The sheet — a mounted plate in The Drawn Language, drawn ONLY from the plan record
   and its placement (P6): rooms, walls, bay lines, windows on exterior walls, doors
   with swing arcs, dimensions, scale bar, north arrow, lot and setback where the site
   is declared. Units are FEET; strokes are px and non-scaling — a pen is a pen.

   Model frame per build/render_plan.py: x east, y north, origin SW. Screen y is
   flipped inside <Model>. Ported from the mockup Sheet; generalised from its one
   hardcoded 64×44 plan to any footprint. */
import React from 'react';
import { WALL_T, levelRooms, partitions, windows, doors, bayLines, litWalls, ft } from './derive.js';

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

/* A door opening: vellum break in the wall, leaf at medium, swing at hairline. */
function DoorMark({ d }) {
  const w = d.w;
  if (d.horiz === false || d.wall === 'W' || d.wall === 'E') {
    const y0 = -d.y - w / 2, x = d.x;
    const leafDir = d.swingRight === false ? -w : w;
    return (
      <g>
        <rect x={x - 0.35} y={y0} width={0.7} height={w} fill="var(--paper-lit)" />
        <line x1={x} y1={y0} x2={x + leafDir} y2={y0} stroke="var(--ink)" strokeWidth="1.4" vectorEffect="non-scaling-stroke" />
        <path d={`M ${x + leafDir} ${y0} A ${w} ${w} 0 0 ${leafDir > 0 ? 1 : 0} ${x} ${y0 + w}`}
          fill="none" stroke="var(--hair)" strokeWidth=".8" vectorEffect="non-scaling-stroke" />
      </g>
    );
  }
  const x0 = d.x - w / 2, y = -d.y;
  const up = d.swingUp !== false;
  return (
    <g>
      <rect x={x0} y={y - 0.35} width={w} height={0.7} fill="var(--paper-lit)" />
      <line x1={x0} y1={y} x2={x0} y2={y + (up ? -w : w)} stroke="var(--ink)" strokeWidth="1.4" vectorEffect="non-scaling-stroke" />
      <path d={`M ${x0} ${y + (up ? -w : w)} A ${w} ${w} 0 0 ${up ? 1 : 0} ${x0 + w} ${y}`}
        fill="none" stroke="var(--hair)" strokeWidth=".8" vectorEffect="non-scaling-stroke" />
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
    const move = (ev) => {
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
      <rect x={hx - 0.8} y={axis === 'y' ? -hy - 0.8 : -room.y - room.h / 2 - 0.8}
        width={1.6} height={1.6}
        fill="var(--paper-lit)" stroke="var(--gilt-deep)" strokeWidth="1.2"
        vectorEffect="non-scaling-stroke"
        style={{ cursor: axis === 'x' ? 'ew-resize' : 'ns-resize' }}
        onPointerDown={down} />
    </g>
  );
}

export function Sheet({ plan, placement, levelIndex = 0, overlays, ghost, selectedRoom,
                        onPickRoom, onResizeRoom, title, subtitle, styleName }) {
  const ov = overlays || {};
  const fp = placement?.footprint || {};
  const W = fp.width_ft || 40, H = fp.depth_ft || 30;
  const rooms = levelRooms(plan, placement, levelIndex);
  const parts = partitions(rooms, W, H);
  const wins = windows(rooms, W, H);
  const drs = doors(rooms, W, H);
  const bays = bayLines(fp);
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
  const interpunct = (title || '').trim().split(/\s+/).join('·');
  const relax = placement?.geometry_report?.relaxations;

  return (
    <div style={{ position: 'relative', background: 'var(--paper)', border: '1px solid var(--ink-2)',
      boxShadow: 'var(--shadow-plate)', padding: '18px 22px 14px' }}>
      <div style={{ textAlign: 'center', margin: '4px 0 2px' }}>
        <div style={{ font: 'var(--fw-med) 17px/1.25 var(--serif)', letterSpacing: 'var(--tr-drawing)',
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
        {ov.privacy && rooms.map((r) => {
          const rank = roomsMeta[r.type]?.privacy_rank || 1;
          return <rect key={'pv' + r.id} x={r.x} y={-r.y - r.h} width={r.w} height={r.h}
            fill="var(--sepia)" opacity={0.04 + (rank / 6) * 0.20} />;
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
          const nameSize = Math.max(0.8, 1.25 * Math.min(1, r.w / 12.5));
          const showDims = r.w >= 9 && r.h >= 6;
          return (
            <g key={r.id} onClick={onPickRoom ? () => onPickRoom(r) : undefined}
              style={{ cursor: onPickRoom ? 'pointer' : 'default' }}>
              <rect x={r.x} y={-r.y - r.h} width={r.w} height={r.h}
                fill={sel ? 'var(--wash-salmon-1)' : 'transparent'}
                stroke={sel ? 'var(--salmon-deep)' : 'transparent'} strokeWidth="1.2" vectorEffect="non-scaling-stroke" />
              <text x={r.x + r.w / 2} y={-r.y - r.h / 2 + (showDims ? -0.3 : 0.4)} fontSize={nameSize}
                fontFamily="var(--serif)" letterSpacing={nameSize * 0.3} fill="var(--ink)"
                textAnchor="middle">{r.name.toUpperCase()}</text>
              {showDims && (
                <text x={r.x + r.w / 2} y={-r.y - r.h / 2 + 1.8} fontSize=".9" fontFamily="var(--serif)"
                  letterSpacing=".12" fill="var(--ink-2)" textAnchor="middle">{ft(r.w)} × {ft(r.h)}</text>
              )}
            </g>
          );
        })}

        {/* drag a wall on the bay grid: handles on the selected room's east and north
            edges; release writes back to the record and the validator re-scores */}
        {onResizeRoom && rooms.filter((r) => r.id === selectedRoom).map((r) => (
          <g key={'h' + r.id}>
            <DragHandle x={r.x + r.w} y={r.y + r.h / 2} axis="x" room={r} bays={bays}
              onCommit={(axis, size) => onResizeRoom(r, 'x', size)} />
            <DragHandle x={r.x + r.w / 2} y={r.y + r.h} axis="y" room={r} bays={bays}
              onCommit={(axis, size) => onResizeRoom(r, 'y', size)} />
          </g>
        ))}

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

        {/* openings */}
        {wins.map((w, i) => <WindowMark key={'w' + i} w={w} />)}
        {drs.exterior.map((d, i) => (
          <DoorMark key={'ed' + i} d={{ x: d.wall === 'W' || d.wall === 'E' ? d.x : d.x,
            y: d.y, w: d.w, horiz: !(d.wall === 'W' || d.wall === 'E'),
            wall: d.wall, swingUp: d.wall === 'S', swingRight: d.wall === 'W' }} />
        ))}
        {drs.interior.map((d, i) => <DoorMark key={'d' + i} d={d} />)}

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
      </svg>

      {/* plate caption */}
      <div style={{ borderTop: '1px solid var(--rule)', margin: '4px 2px 0', padding: '8px 0 4px',
        display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: 24 }}>
        <div style={{ font: 'var(--fw-med) 10.5px/1.3 var(--serif)', letterSpacing: '.3em',
          textTransform: 'uppercase', color: 'var(--ink)', whiteSpace: 'nowrap' }}>{interpunct}</div>
        <div style={{ font: 'italic var(--fw-reg) 13px/1.45 var(--serif)', color: 'var(--ink-2)',
          textAlign: 'right' }}>
          {relax
            ? `${relax.count} cut(s) off the bay line${relax.count ? `, worst ${relax.max_off_grid_ft} ft` : ''}. `
            : ''}
          {wins.dropped
            ? `${wins.dropped} declared window(s) not situated on this footprint — declared, not drawn. `
            : ''}
          Exterior door openings are drawn at conventional mid-wall position.
          The grid remains — evidence the plan was composed, not arranged.
        </div>
      </div>
    </div>
  );
}

export { ft };
