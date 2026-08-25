/* Surface ⑪ — Transcription (WP-5.5). A drawing goes in, a record comes out,
   and a human makes every judgment on the way: trace room rectangles over a
   scanned drawing (or start from a drafter's DXF, whose extraction arrives as
   candidates with its gaps named), give each room its type from the catalog,
   place windows and doors, say where the record came from and how much to
   trust it — then check it as a record and put it on the bench.

   The draft is not a record. Trace positions are working state (they derive
   clear dims, exterior walls and door suggestions); the record that leaves is
   dims + topology + provenance, the same shape as every record in plans/.
   The backdrop image never leaves the browser. */
import React from 'react';
import { api } from '../api/client.js';
import { planDoc } from '../state/planDoc.js';
import { draftDoc, emptyDraft, completeness, toRecord, exteriorWalls, neighbours }
  from '../state/draftDoc.js';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { FilterStrip, Chip } from '../Chrome.jsx';

const SNAP = 0.5;
const snap = (v) => Math.round(v / SNAP) * SNAP;

const label = { display: 'block', font: 'var(--type-data-s)', color: 'var(--ink-3)', margin: '8px 0 2px' };
const input = { width: '100%', font: 'var(--fw-reg) 12.5px/1.4 var(--mono, monospace)',
  color: 'var(--ink)', background: 'var(--paper-deep)', border: '1px solid var(--rule)',
  padding: '4px 6px' };
const row = { display: 'flex', gap: 8 };

function Field({ name, value, onChange, list, type, placeholder, w }) {
  return (
    <span style={{ flex: w || 1, minWidth: 0 }}>
      <label style={label}>{name}</label>
      <input style={input} value={value ?? ''} type={type || 'text'} list={list}
        placeholder={placeholder || ''} onChange={(e) => onChange(e.target.value)} />
    </span>
  );
}

/* ---------------- the tracing canvas ---------------- */

function Canvas({ draft, level, sel, setSel, backdrop, mode }) {
  const svgRef = React.useRef(null);
  const drag = React.useRef(null);
  const [, force] = React.useReducer((x) => x + 1, 0);

  const rooms = draft.rooms.filter((r) => r.level === level);
  const W = Math.max(44, ...rooms.map((r) => r.x + r.w + 4), backdrop?.wFt + 2 || 0);
  const H = Math.max(32, ...rooms.map((r) => r.y + r.h + 4), backdrop?.hFt + 2 || 0);

  const toModel = (e) => {
    const pt = svgRef.current.createSVGPoint();
    pt.x = e.clientX; pt.y = e.clientY;
    const m = pt.matrixTransform(svgRef.current.getScreenCTM().inverse());
    return { x: m.x, y: -m.y };   // screen y down -> model y north
  };

  function down(e) {
    const p = toModel(e);
    const hitHandle = e.target.dataset?.handle;
    const hitRoom = e.target.dataset?.room;
    if (hitHandle && sel) {
      draftDoc.update((d) => d);   // one undo snapshot for the whole gesture
      drag.current = { kind: 'resize', handle: hitHandle, start: p };
    } else if (hitRoom) {
      const r = draft.rooms.find((x) => x.key === hitRoom);
      setSel(hitRoom);
      draftDoc.update((d) => d);   // one undo snapshot for the whole gesture
      drag.current = { kind: 'move', start: p, orig: { x: r.x, y: r.y } };
    } else if (mode === 'draw') {
      drag.current = { kind: 'new', start: p, ghost: { x: p.x, y: p.y, w: 0, h: 0 } };
    } else {
      setSel(null);
    }
    e.currentTarget.setPointerCapture?.(e.pointerId);
  }

  function move(e) {
    const d = drag.current;
    if (!d) return;
    const p = toModel(e);
    if (d.kind === 'new') {
      d.ghost = { x: Math.min(d.start.x, p.x), y: Math.min(d.start.y, p.y),
                  w: Math.abs(p.x - d.start.x), h: Math.abs(p.y - d.start.y) };
      force();
    } else if (d.kind === 'move' && sel) {
      const dx = snap(p.x - d.start.x), dy = snap(p.y - d.start.y);
      draftDoc.mutate((dr) => {
        const r = dr.rooms.find((x) => x.key === sel);
        if (r) { r.x = Math.max(0, d.orig.x + dx); r.y = Math.max(0, d.orig.y + dy); }
        return dr;
      });
      drag.current = { ...d, moved: true };
    } else if (d.kind === 'resize' && sel) {
      draftDoc.mutate((dr) => {
        const r = dr.rooms.find((x) => x.key === sel);
        if (!r) return dr;
        const x2 = r.x + r.w, y2 = r.y + r.h;
        if (d.handle.includes('e')) r.w = Math.max(3, snap(p.x - r.x));
        if (d.handle.includes('n')) r.h = Math.max(3, snap(p.y - r.y));
        if (d.handle.includes('w')) { const nx = Math.min(snap(p.x), x2 - 3); r.w = x2 - nx; r.x = nx; }
        if (d.handle.includes('s')) { const ny = Math.min(snap(p.y), y2 - 3); r.h = y2 - ny; r.y = ny; }
        return dr;
      });
    }
  }

  function up() {
    const d = drag.current;
    drag.current = null;
    if (d?.kind === 'new' && d.ghost.w >= 3 && d.ghost.h >= 3) {
      draftDoc.update((dr) => {
        const key = 'r' + dr.seq;
        dr.rooms.push({ key, level, id: `room-${dr.seq}`, type: '', name: '',
          x: snap(d.ghost.x), y: snap(d.ghost.y), w: snap(d.ghost.w), h: snap(d.ghost.h),
          windows: [], doors: [] });
        dr.seq += 1;
        return dr;
      });
    } else { force(); }
  }

  const gridLines = [];
  for (let g = 0; g <= W; g += 5) gridLines.push(
    <line key={'v' + g} x1={g} y1={-H} x2={g} y2={0}
      stroke={g % 10 ? 'var(--rule)' : 'var(--ink-4)'} strokeWidth={g % 10 ? 0.4 : 0.7}
      vectorEffect="non-scaling-stroke" opacity={0.5} />);
  for (let g = 0; g <= H; g += 5) gridLines.push(
    <line key={'h' + g} x1={0} y1={-g} x2={W} y2={-g}
      stroke={g % 10 ? 'var(--rule)' : 'var(--ink-4)'} strokeWidth={g % 10 ? 0.4 : 0.7}
      vectorEffect="non-scaling-stroke" opacity={0.5} />);

  return (
    <svg ref={svgRef} viewBox={`-2 ${-H - 2} ${W + 4} ${H + 4}`}
      style={{ width: '100%', height: '100%', display: 'block', background: 'var(--paper-deep)',
        cursor: mode === 'draw' ? 'crosshair' : 'default', touchAction: 'none' }}
      onPointerDown={down} onPointerMove={move} onPointerUp={up}>
      {backdrop?.url && (
        <image href={backdrop.url} x={0} y={-backdrop.hFt} width={backdrop.wFt}
          height={backdrop.hFt} opacity={backdrop.opacity}
          preserveAspectRatio="none" style={{ pointerEvents: 'none' }} />
      )}
      {gridLines}
      {draft.rooms.filter((r) => r.level === level).map((r) => {
        const on = r.key === sel;
        return (
          <g key={r.key}>
            <rect data-room={r.key} x={r.x} y={-r.y - r.h} width={r.w} height={r.h}
              fill={on ? 'var(--paper-lit)' : 'var(--paper)'} fillOpacity={0.55}
              stroke={on ? 'var(--gilt-deep)' : r.type ? 'var(--ink)' : 'var(--judge-unjudged)'}
              strokeWidth={on ? 1.6 : 1.1} vectorEffect="non-scaling-stroke"
              strokeDasharray={r.type ? undefined : '3 3'} style={{ cursor: 'move' }} />
            <text x={r.x + r.w / 2} y={-r.y - r.h / 2} textAnchor="middle" fontSize="1.35"
              fill="var(--ink)" fontFamily="var(--body)" style={{ pointerEvents: 'none' }}>
              {r.name || r.name_hint || r.id}
            </text>
            <text x={r.x + r.w / 2} y={-r.y - r.h / 2 + 1.9} textAnchor="middle" fontSize="1"
              fill={r.type ? 'var(--ink-3)' : 'var(--judge-unjudged)'} fontFamily="var(--mono, monospace)"
              style={{ pointerEvents: 'none' }}>
              {r.type || 'type unset'} · {r.w}×{r.h} ft
            </text>
            {on && ['ne', 'nw', 'se', 'sw'].map((h) => {
              const hx = h.includes('e') ? r.x + r.w : r.x;
              const hy = h.includes('n') ? r.y + r.h : r.y;
              return <rect key={h} data-handle={h} x={hx - 0.8} y={-hy - 0.8} width={1.6} height={1.6}
                fill="var(--gilt-deep)" style={{ cursor: h === 'ne' || h === 'sw' ? 'nesw-resize' : 'nwse-resize' }} />;
            })}
          </g>
        );
      })}
      {drag.current?.kind === 'new' && drag.current.ghost.w > 0.5 && (
        <rect x={drag.current.ghost.x} y={-drag.current.ghost.y - drag.current.ghost.h}
          width={drag.current.ghost.w} height={drag.current.ghost.h} fill="none"
          stroke="var(--gilt-deep)" strokeDasharray="2 2" strokeWidth="1"
          vectorEffect="non-scaling-stroke" />
      )}
    </svg>
  );
}

/* ---------------- the room editor ---------------- */

function RoomEditor({ draft, room, roomTypes }) {
  const up = (fn) => draftDoc.update((d) => {
    const r = d.rooms.find((x) => x.key === room.key);
    if (r) fn(r, d);
    return d;
  });
  const others = draft.rooms.filter((r) => r.level === room.level && r.key !== room.key);
  const near = neighbours(room, draft.rooms);
  const ext = exteriorWalls(room, draft.rooms);
  return (
    <div>
      <Eyebrow style={{ margin: '14px 0 4px' }}>selected room</Eyebrow>
      <div style={row}>
        <Field name="id" value={room.id} onChange={(v) => up((r) => { r.id = v; })} />
        <Field name="name" value={room.name} placeholder={room.name_hint || ''}
          onChange={(v) => up((r) => { r.name = v; })} />
      </div>
      <div style={row}>
        <Field name="type (catalog)" value={room.type} list="tdl-room-types"
          onChange={(v) => up((r) => { r.type = v; })} />
        <Field name="level" value={room.level} type="number" w="0 0 70px"
          onChange={(v) => up((r) => { r.level = Number(v) || 0; })} />
      </div>
      <p style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)', margin: '6px 0 0' }}>
        {room.w}×{room.h} ft · exterior: {ext.join(' ') || 'none'} ·
        shares a wall with: {near.join(', ') || 'nothing yet'}
      </p>

      <Eyebrow style={{ margin: '12px 0 2px' }}>windows</Eyebrow>
      {(room.windows || []).map((w, i) => (
        <div key={i} style={{ ...row, alignItems: 'flex-end' }}>
          <Field name="wall" value={w.wall} list="tdl-walls" w="0 0 52px"
            onChange={(v) => up((r) => { r.windows[i].wall = v; })} />
          <Field name="w ft" value={w.width_ft} type="number" w="0 0 62px"
            onChange={(v) => up((r) => { r.windows[i].width_ft = Number(v) || undefined; })} />
          <Field name="h ft" value={w.height_ft} type="number" w="0 0 62px"
            onChange={(v) => up((r) => { r.windows[i].height_ft = Number(v) || undefined; })} />
          <Field name="sill ft" value={w.sill_ft} type="number" w="0 0 62px"
            onChange={(v) => up((r) => { r.windows[i].sill_ft = Number(v) || undefined; })} />
          <Field name="count" value={w.count} type="number" w="0 0 58px"
            onChange={(v) => up((r) => { r.windows[i].count = Number(v) || undefined; })} />
          <Chip onClick={() => up((r) => { r.windows.splice(i, 1); })}>×</Chip>
        </div>
      ))}
      <Chip onClick={() => up((r) => { (r.windows = r.windows || []).push({ wall: ext[0] || 'S', width_ft: 3, height_ft: 5, count: 1 }); })}>
        + window
      </Chip>

      <Eyebrow style={{ margin: '12px 0 2px' }}>doors</Eyebrow>
      {(room.doors || []).map((d, i) => (
        <div key={i} style={{ ...row, alignItems: 'flex-end' }}>
          <span style={{ flex: 1 }}>
            <label style={label}>to</label>
            <select style={input} value={d.to}
              onChange={(e) => up((r) => { r.doors[i].to = e.target.value; })}>
              <option value="exterior">exterior</option>
              {others.map((o) => <option key={o.key} value={o.id}>{o.id}</option>)}
            </select>
          </span>
          <Field name="w ft" value={d.width_ft} type="number" w="0 0 62px"
            onChange={(v) => up((r) => { r.doors[i].width_ft = Number(v) || undefined; })} />
          <Chip onClick={() => up((r) => { r.doors.splice(i, 1); })}>×</Chip>
        </div>
      ))}
      <span style={{ display: 'inline-flex', gap: 6, flexWrap: 'wrap', marginTop: 4 }}>
        <Chip onClick={() => up((r) => { (r.doors = r.doors || []).push({ to: near[0] || 'exterior' }); })}>
          + door
        </Chip>
        {near.filter((n) => !(room.doors || []).some((d) => d.to === n)).map((n) => (
          <Chip key={n} onClick={() => up((r) => { (r.doors = r.doors || []).push({ to: n }); })}>
            + door to {n}
          </Chip>
        ))}
      </span>
      <div style={{ marginTop: 12 }}>
        <Chip tone="var(--iron, #c33)" onClick={() => draftDoc.update((d) => {
          d.rooms = d.rooms.filter((x) => x.key !== room.key);
          return d;
        })}>delete room</Chip>
      </div>
    </div>
  );
}

/* ---------------- the surface ---------------- */

export function Transcription({ go }) {
  const draft = React.useSyncExternalStore(draftDoc.subscribe, draftDoc.get);
  const [sel, setSel] = React.useState(null);
  const [level, setLevel] = React.useState(0);
  const [mode, setMode] = React.useState('draw');
  const [backdrop, setBackdrop] = React.useState(null);
  const [roomTypes, setRoomTypes] = React.useState([]);
  const [styles, setStyles] = React.useState([]);
  const [ingest, setIngest] = React.useState(null);     // last DXF extraction report
  const [checked, setChecked] = React.useState(null);   // last evaluate result
  const [busy, setBusy] = React.useState(false);

  React.useEffect(() => {
    api.rooms({ limit: 200 }).then((r) => setRoomTypes((r.results || r.rooms || []).map((x) => x.id).sort())).catch(() => {});
    api.styles({ limit: 200 }).then((r) => setStyles((r.results || []).map((s) => s.id).sort())).catch(() => {});
  }, []);

  if (!draft) {
    return (
      <div style={{ padding: '26px 30px', maxWidth: 720 }}>
        <Eyebrow>transcription</Eyebrow>
        <h2 style={{ font: 'var(--fw-reg) var(--fs-d2)/1.1 var(--display)', margin: '8px 0 10px' }}>
          A drawing goes in; a record comes out
        </h2>
        <p style={{ font: 'var(--fw-reg) 14px/1.6 var(--body)', color: 'var(--ink-2)', margin: '0 0 16px' }}>
          Trace rooms over a scanned drawing, or start from a drafter's DXF — its
          extraction arrives as candidates with the gaps named, and a human fills
          every one. Nothing is guessed into the record.
        </p>
        <Chip onClick={() => draftDoc.load(emptyDraft())}>start a draft</Chip>
      </div>
    );
  }

  const selRoom = draft.rooms.find((r) => r.key === sel);
  const gaps = completeness(draft);
  const meta = (k, v) => draftDoc.update((d) => { d.meta[k] = v; return d; });
  const prov = (k, v) => draftDoc.update((d) => { d.provenance[k] = v; return d; });
  const ctx = (k, v) => draftDoc.update((d) => { d.context[k] = v; return d; });

  function loadBackdrop(file) {
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => setBackdrop({ url, wFt: 60, hFt: 60 * img.height / img.width,
      ratio: img.height / img.width, opacity: 0.5, name: file.name });
    img.src = url;
  }

  function loadDxf(file) {
    setBusy(true); setIngest(null);
    file.text().then((text) => api.ingestDxf(text))
      .then((res) => {
        setIngest(res);
        if (res.complete) {
          planDoc.load(res.record);
          return;
        }
        draftDoc.update((d) => {
          for (const c of res.candidates.rooms) {
            d.rooms.push({ key: 'r' + d.seq, level, id: `room-${d.seq}`,
              type: '', name: '', name_hint: c.name_hint,
              x: c.x, y: c.y, w: c.w, h: c.h, windows: [], doors: [],
              note: c.note || undefined });
            d.seq += 1;
          }
          if (!d.provenance.source) d.provenance.source = file.name;
          d.provenance.method = 'dxf-import';
          return d;
        });
      })
      .catch((e) => setIngest({ error: e.body?.detail?.error || e.message,
        units: e.body?.detail?.units }))
      .finally(() => setBusy(false));
  }

  function checkRecord() {
    setBusy(true);
    api.evaluate(toRecord(draft), { place: true })
      .then(setChecked)
      .catch((e) => setChecked({ check: { error: e.body?.detail?.error || e.message } }))
      .finally(() => setBusy(false));
  }

  const save = (name, content) => {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([JSON.stringify(content, null, 1)], { type: 'application/json' }));
    a.download = name; a.click(); URL.revokeObjectURL(a.href);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: 0, flex: 1 }}>
      <datalist id="tdl-room-types">{roomTypes.map((t) => <option key={t} value={t} />)}</datalist>
      <datalist id="tdl-styles">{styles.map((s) => <option key={s} value={s} />)}</datalist>
      <datalist id="tdl-walls">{['S', 'N', 'E', 'W'].map((w) => <option key={w} value={w} />)}</datalist>
      <FilterStrip right={
        <span style={{ display: 'flex', gap: 8 }}>
          <Chip onClick={() => draftDoc.undo()} title="undo">undo</Chip>
          <Chip tone="var(--iron, #c33)" onClick={() => { draftDoc.clear(); setSel(null); }}>discard draft</Chip>
        </span>
      }>
        <Eyebrow as="span">transcription</Eyebrow>
        <Chip on={mode === 'draw'} onClick={() => setMode('draw')}>draw rooms</Chip>
        <Chip on={mode === 'select'} onClick={() => setMode('select')}>select</Chip>
        <span style={{ width: 12 }} />
        {draft.levels.map((lv) => (
          <Chip key={lv.index} on={level === lv.index} onClick={() => setLevel(lv.index)}>
            {lv.id}
          </Chip>
        ))}
        <Chip onClick={() => draftDoc.update((d) => {
          const idx = d.levels.length;
          d.levels.push({ id: idx === 1 ? 'upper' : `level-${idx}`, index: idx, floor_to_ceiling_ft: 8 });
          return d;
        })}>+ level</Chip>
      </FilterStrip>

      <div style={{ flex: 1, display: 'flex', minHeight: 0 }}>
        <div style={{ flex: 1, minWidth: 0, position: 'relative' }}>
          <Canvas draft={draft} level={level} sel={sel} setSel={setSel}
            backdrop={backdrop} mode={mode} />
          <div style={{ position: 'absolute', left: 10, bottom: 10, display: 'flex', gap: 8,
            alignItems: 'center', background: 'var(--paper)', border: '1px solid var(--rule)',
            padding: '6px 10px' }}>
            <label style={{ ...label, margin: 0 }}>
              backdrop
              <input type="file" accept="image/*" style={{ display: 'block', font: 'var(--type-data-s)' }}
                onChange={(e) => e.target.files[0] && loadBackdrop(e.target.files[0])} />
            </label>
            {backdrop && (
              <>
                <label style={{ ...label, margin: 0 }}>width ft
                  <input style={{ ...input, width: 64 }} type="number" value={backdrop.wFt}
                    onChange={(e) => {
                      const wFt = Number(e.target.value) || 1;
                      setBackdrop({ ...backdrop, wFt, hFt: wFt * backdrop.ratio });
                    }} />
                </label>
                <label style={{ ...label, margin: 0 }}>opacity
                  <input type="range" min="0.1" max="1" step="0.1" value={backdrop.opacity}
                    onChange={(e) => setBackdrop({ ...backdrop, opacity: Number(e.target.value) })} />
                </label>
              </>
            )}
            <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)' }}>
              stays in this browser — never uploaded
            </span>
          </div>
        </div>

        <div style={{ width: 360, flex: 'none', borderLeft: '1px solid var(--rule)',
          overflow: 'auto', padding: '14px 16px 40px' }}>
          <Eyebrow>the record</Eyebrow>
          <div style={row}>
            <Field name="id" value={draft.meta.id} onChange={(v) => meta('id', v)} />
            <Field name="name" value={draft.meta.name} onChange={(v) => meta('name', v)} />
          </div>
          <div style={row}>
            <Field name="style" value={draft.meta.style} list="tdl-styles"
              onChange={(v) => meta('style', v)} />
            <Field name="date" value={draft.context.date_of_representation} type="number" w="0 0 84px"
              onChange={(v) => ctx('date_of_representation', v)} />
            <span style={{ flex: '0 0 84px' }}>
              <label style={label}>entrance</label>
              <select style={input} value={draft.context.entrance_faces}
                onChange={(e) => ctx('entrance_faces', e.target.value)}>
                {['S', 'N', 'E', 'W', 'SE', 'SW', 'NE', 'NW'].map((f) => <option key={f}>{f}</option>)}
              </select>
            </span>
          </div>

          <Eyebrow style={{ margin: '16px 0 2px' }}>provenance — where this came from</Eyebrow>
          <div style={row}>
            <Field name="source (drawing / sheet / file)" value={draft.provenance.source}
              onChange={(v) => prov('source', v)} />
          </div>
          <div style={row}>
            <span style={{ flex: 1 }}>
              <label style={label}>method</label>
              <select style={input} value={draft.provenance.method}
                onChange={(e) => prov('method', e.target.value)}>
                {['traced', 'dxf-import', 'authored', 'multimodal-reading'].map((m) => <option key={m}>{m}</option>)}
              </select>
            </span>
            <span style={{ flex: 1 }}>
              <label style={label}>confidence</label>
              <select style={input} value={draft.provenance.transcription_confidence}
                onChange={(e) => prov('transcription_confidence', e.target.value)}>
                {['high', 'medium', 'low'].map((c) => <option key={c}>{c}</option>)}
              </select>
            </span>
            <Field name="traced by" value={draft.provenance.traced_by}
              onChange={(v) => prov('traced_by', v)} />
          </div>
          <label style={label}>why this style — the reasoning rides with the record</label>
          <textarea rows={2} style={{ ...input, resize: 'vertical' }}
            value={draft.provenance.style_reasoning}
            onChange={(e) => prov('style_reasoning', e.target.value)} />

          <Eyebrow style={{ margin: '16px 0 2px' }}>from a drafter's DXF</Eyebrow>
          <input type="file" accept=".dxf" style={{ font: 'var(--type-data-s)' }}
            onChange={(e) => e.target.files[0] && loadDxf(e.target.files[0])} />
          {busy && <p style={{ font: 'var(--type-data-s)', color: 'var(--ink-3)' }}>working…</p>}
          {ingest && ingest.error && (
            <p style={{ font: 'var(--type-data-s)', color: 'var(--forthcoming)', margin: '6px 0 0' }}>
              refused — {ingest.error}
              {ingest.units?.scores && ` (heuristic: ${JSON.stringify(ingest.units.scores)})`}
            </p>
          )}
          {ingest && !ingest.error && ingest.complete && (
            <p style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)', margin: '6px 0 0' }}>
              a TDL-emitted sheet — the complete record went straight to the bench (⑦)
            </p>
          )}
          {ingest && !ingest.error && !ingest.complete && (
            <div style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)', margin: '6px 0 0' }}>
              {ingest.counts.kept} candidate room(s), units {ingest.units.units} ({ingest.units.basis},
              plausibility {ingest.units.plausibility}){ingest.units.note ? ` — ${ingest.units.note}` : ''}
              <div style={{ color: 'var(--ink-3)', marginTop: 4 }}>
                gaps the extractor names:
                {ingest.gaps.map((g, i) => <div key={i}>· {g}</div>)}
              </div>
            </div>
          )}

          {selRoom
            ? <RoomEditor draft={draft} room={selRoom} roomTypes={roomTypes} />
            : <p style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)', margin: '14px 0 0' }}>
                drag on the canvas to trace a room; click one to edit it
              </p>}

          <Eyebrow style={{ margin: '18px 0 4px' }}>
            {gaps.length ? `not yet a record — ${gaps.length} gap(s)` : 'ready — every gap filled'}
          </Eyebrow>
          {gaps.map((g, i) => (
            <div key={i} style={{ font: 'var(--type-data-s)', color: 'var(--judge-unjudged, var(--ink-3))' }}>
              · {g}
            </div>
          ))}

          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 12 }}>
            <Chip onClick={gaps.length ? undefined : checkRecord}
              title={gaps.length ? 'fill the named gaps first' : ''}>check as record</Chip>
            <Chip onClick={gaps.length ? undefined : () => { planDoc.load(toRecord(draft)); go?.('workbench'); }}
              title={gaps.length ? 'fill the named gaps first' : ''}>send to the bench</Chip>
            <Chip onClick={gaps.length ? undefined : () => save(`${draft.meta.id || 'record'}.json`, toRecord(draft))}>
              download record
            </Chip>
            <Chip onClick={() => save(`${draft.meta.id || 'draft'}.draft.json`, draft)}>download draft</Chip>
          </div>
          {checked && (
            <p style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)', margin: '10px 0 0' }}>
              {checked.check?.error
                ? `could not check — ${checked.check.error}`
                : `checked: ${(checked.check?.findings || []).length} finding(s) · ` +
                  `${checked.check?.constraint_summary?.unjudged ?? '?'} unjudged — ` +
                  'the full critique lives on the bench (⑦)'}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
