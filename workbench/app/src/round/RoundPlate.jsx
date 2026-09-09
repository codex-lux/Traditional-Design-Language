/* The Round's sheet chrome: the view bar, the caption, the plate overlay and the record card.

   WP-12.4, brief §§7.3, 7.8, 7.10. The furniture is the Sheet's, by REUSE where the Sheet
   exports it (`interpunctTitle`, `ft`) and by matching where it does not — the title block,
   the 150 px rule and the `data-plate-title` / `data-plate-note` caption row are inline in
   Sheet.jsx, and DrawingSet.jsx had already re-typed a near-copy of them carrying neither data
   attribute. This file states them once for the model plate and the flat plates both. */
import React from 'react';

import { Chip, ChipGroup } from '../Chrome.jsx';
import { ft, interpunctTitle } from '../sheet/derive.js';
import {
  caption, chipLabel, modifierLine, notModelledLine, overlaysFor, plateKeyFor,
} from './annotate.js';
import { namedViews, plateTransform, poseFor } from './frame.js';
import {
  FREE_VIEW_OVERLAYS, bayGrid, cutPlane, datumLines, daylightVolumes,
  explodeOffsets, privacyWashes, relaxationMarks, wetPrisms,
} from './overlays.js';
import {
  DAYLIGHT_OPACITY, DAYLIGHT_TOKEN, PRIVACY_TOKEN, WET_OPACITY, WET_TOKEN,
} from '../sheet/overlayRules.js';
import { Round, readTokens } from './Round.jsx';
import { extent } from './solids.js';

/* The plate's own frame, as build/sheet_style.py::frame_attr wrote it. Read rather than
   re-derived: the renderer states what its pixels mean and this believes it, which is the
   whole reason the attribute exists. */
export function frameOf(svgText, view) {
  const m = /data-frame='([^']*)'/.exec(svgText || '');
  if (!m) return null;
  let parsed;
  try {
    parsed = JSON.parse(m[1].replace(/&apos;/g, "'"));
  } catch (e) {
    return null;
  }
  const plates = (parsed && parsed.plates) || [];
  if (!plates.length) return null;
  const lvl = /^plan-l(\d+)$/.exec(view || '');
  if (lvl) return plates.find((p) => String(p.level) === lvl[1]) || plates[0];
  if (/^[snew]$/.test(view || '')) return plates.find((p) => p.id === view.toUpperCase()) || plates[0];
  return plates[0];
}

function TitleBlock({ title, styleName, subtitle }) {
  return (
    <div style={{ textAlign: 'center', padding: '2px 0 10px' }}>
      <div style={{
        font: 'var(--fw-med) 17px/1.35 var(--serif)', letterSpacing: 'var(--tr-drawing)',
        textTransform: 'uppercase', color: 'var(--ink)',
      }}>{interpunctTitle(title)}</div>
      <div style={{
        font: '11px/1.4 var(--serif)', letterSpacing: 'var(--tr-caps)', textTransform: 'uppercase',
        color: 'var(--ink-2)', marginTop: 4,
      }}>{styleName}&nbsp;·&nbsp;{subtitle}</div>
      <div style={{ width: 150, height: 0, borderTop: '1px solid var(--rule)', margin: '9px auto 0' }} />
    </div>
  );
}

function RecordCard({ solid, onClose }) {
  if (!solid) return null;
  const e = extent(solid);
  const size = [e.max[0] - e.min[0], e.max[1] - e.min[1], e.max[2] - e.min[2]];
  const src = (solid.source && solid.source.record) || '';
  return (
    <div
      data-round-card=""
      style={{
        position: 'absolute', right: 10, top: 10, maxWidth: 300, background: 'var(--paper)',
        border: '1px solid var(--ink-3)', boxShadow: 'var(--shadow-plate)', padding: '10px 12px',
        font: '12px/1.5 var(--serif)', color: 'var(--ink)',
      }}
    >
      <div style={{ letterSpacing: 'var(--tr-eyebrow)', textTransform: 'uppercase', fontSize: 10, color: 'var(--ink-2)' }}>
        {solid.class} · {solid.kind}
      </div>
      <div style={{ marginTop: 3 }}>{solid.id}</div>
      <div style={{ marginTop: 3, color: 'var(--ink-2)' }}>
        {ft(size[0])} × {ft(size[1])} × {ft(size[2])}
      </div>
      {src ? (
        <div style={{ marginTop: 6, font: '11px/1.4 var(--mono, monospace)', color: 'var(--ink-3)', wordBreak: 'break-all' }}>
          {src}
        </div>
      ) : null}
      {solid.note ? <div style={{ marginTop: 6, fontStyle: 'italic', color: 'var(--ink-2)' }}>{solid.note}</div> : null}
      <button
        type="button"
        onClick={onClose}
        style={{ marginTop: 8, background: 'none', border: 'none', padding: 0, cursor: 'pointer', font: 'inherit', color: 'var(--gilt-deep, var(--ink-2))' }}
      >close</button>
    </div>
  );
}

/* The overlays a reader may ask for, in the order the chip strip prints them. `plate` is a
   chip of its own beside the view bar and is not in this list, because it is the one overlay
   that is a DRAWING rather than an analysis. */
const OVERLAY_CHIPS = ['grid', 'datums', 'daylight', 'wet', 'privacy', 'relaxations'];

export function RoundPlate({
  scene, plan, meta, plates, platesRefused, view, onView, plateOn, onPlate,
  ov, onOv, explode, onExplode, cut, onCut,
  title, styleName, subtitle, disclosures,
}) {
  const [picked, setPicked] = React.useState(null);
  const [box, setBox] = React.useState({ width: 0, height: 0 });
  const mountRef = React.useRef(null);
  const views = React.useMemo(() => (scene ? namedViews(scene) : []), [scene]);

  React.useEffect(() => {
    const el = mountRef.current;
    if (!el || typeof ResizeObserver === 'undefined') return undefined;
    const ro = new ResizeObserver(() => setBox({ width: el.clientWidth, height: el.clientHeight }));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  React.useEffect(() => {
    const onKey = (e) => { if (e.key === 'Escape') setPicked(null); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  const key = plateKeyFor(view);
  const svg = key && plates && plates[key] ? plates[key].svg : null;
  const refusedWhy = key && platesRefused ? platesRefused[key] : null;

  const overlay = React.useMemo(() => {
    if (!plateOn || !svg || !scene || !box.width) return null;
    const tokens = typeof document === 'undefined' ? {} : readTokens(document.documentElement);
    const pose = poseFor(view, scene, null, {
      aspect: box.width / Math.max(box.height, 1),
      axonElevationDeg: parseFloat(tokens['axon-elevation-deg']) || undefined,
    });
    const fr = frameOf(svg, view);
    if (!pose || !fr) return null;
    return plateTransform(view, scene, pose, box, fr);
  }, [plateOn, svg, scene, view, box.width, box.height]);

  /* WHICH OVERLAYS THIS VIEW MAY CARRY. Four of the six are read off a plan and mean nothing
     on a model turned in the hand (§7.5); a free view keeps the three that are true from any
     angle, and the ones it drops are NAMED rather than silently ceasing to work. */
  const wanted = React.useMemo(() => ov || [], [ov]);
  const { active: ovActive, dropped: ovDropped } =
    React.useMemo(() => overlaysFor(view, wanted, FREE_VIEW_OVERLAYS), [view, wanted]);

  const explodeResult = React.useMemo(
    () => (scene ? explodeOffsets(scene, explode) : null), [scene, explode],
  );
  const cutResult = React.useMemo(
    () => (scene && cut && cut.axis ? cutPlane(scene, cut) : null), [scene, cut],
  );

  const payload = React.useMemo(() => {
    if (!scene) return null;
    const on = new Set(ovActive);
    const b = scene.bounds || {};
    return {
      grid: on.has('grid') ? bayGrid(scene) : null,
      datums: on.has('datums') ? datumLines(scene) : null,
      extent: b.min && b.max ? [b.min[0], b.min[1], b.max[0], b.max[1]] : null,
      daylight: on.has('daylight') && plan ? daylightVolumes(scene, plan, meta) : null,
      daylightToken: DAYLIGHT_TOKEN, daylightOpacity: DAYLIGHT_OPACITY,
      wet: on.has('wet') ? wetPrisms(scene, meta) : null,
      wetToken: WET_TOKEN, wetOpacity: WET_OPACITY,
      privacy: on.has('privacy') ? privacyWashes(scene, meta).drawn : null,
      privacyToken: PRIVACY_TOKEN,
      relaxations: on.has('relaxations') ? relaxationMarks(scene).drawn : null,
    };
  }, [scene, plan, meta, ovActive]);

  const cap = scene ? caption(view, scene) : '';
  const nm = scene ? notModelledLine(scene) : null;
  const mods = scene ? modifierLine({ explode, cut: cutResult }, explodeResult) : null;
  /* A mark the placement could not locate is NAMED here rather than drawn somewhere
     plausible — WP-6.3's rule, and the reason `relaxationMarks` splits them at all. */
  const unlocated = scene && ovActive.includes('relaxations')
    ? relaxationMarks(scene).unlocated.length : 0;

  return (
    <div style={{
      position: 'relative', background: 'var(--paper)', border: '1px solid var(--ink-2)',
      boxShadow: 'var(--shadow-plate)', padding: '16px 18px 10px',
    }}>
      <TitleBlock title={title} styleName={styleName} subtitle={subtitle} />

      <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap', marginBottom: 8 }}>
        <ChipGroup label="view">
          {views.map((v) => (
            <Chip key={v} radio on={view === v} onClick={() => onView(v)} title={caption(v, scene)}>
              {chipLabel(v, scene)}
            </Chip>
          ))}
        </ChipGroup>
        {key ? (
          <Chip on={!!plateOn} onClick={() => onPlate(!plateOn)} title="lay the drawn plate over the model at this view">
            plate
          </Chip>
        ) : null}
      </div>

      <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap', marginBottom: 8 }}>
        <ChipGroup label="overlay">
          {OVERLAY_CHIPS.map((o) => (
            <Chip
              key={o}
              on={wanted.includes(o)}
              onClick={() => onOv(wanted.includes(o) ? wanted.filter((x) => x !== o) : [...wanted, o])}
              title={ovDropped.includes(o)
                ? `${o} is read off a plan and is not drawn in a free view`
                : `show ${o}`}
            >
              {ovDropped.includes(o) ? `${o} ·` : o}
            </Chip>
          ))}
        </ChipGroup>
        <ChipGroup label="explode">
          {['levels', 'elements'].map((m) => (
            <Chip
              key={m}
              radio
              on={(explode || {}).mode === m}
              onClick={() => onExplode((explode || {}).mode === m ? { mode: 'none', k: 0 } : { mode: m, k: 1 })}
              title={`separate the model by ${m}`}
            >
              {m}
            </Chip>
          ))}
        </ChipGroup>
        <ChipGroup label="cut">
          {['level', 'x', 'y'].map((a) => (
            <Chip
              key={a}
              radio
              on={(cut || {}).axis === a}
              onClick={() => onCut((cut || {}).axis === a ? {} : { axis: a, at: a === 'level' ? undefined : 20 })}
              title="a section plane through the model, derived from the model and not from a plate"
            >
              {a}
            </Chip>
          ))}
        </ChipGroup>
      </div>

      <div ref={mountRef} style={{ position: 'relative' }}>
        <Round scene={scene} view={view} onView={onView} onPick={setPicked}
          overlays={payload} explode={explodeResult} cut={cutResult} />
        {overlay && svg ? (
          <div
            data-round-overlay=""
            aria-hidden="true"
            style={{
              position: 'absolute', left: 0, top: 0, transformOrigin: '0 0',
              transform: `translate(${overlay.dx}px, ${overlay.dy}px) scale(${overlay.scale})`,
              opacity: 0.6, pointerEvents: 'none',
            }}
            dangerouslySetInnerHTML={{ __html: svg }}
          />
        ) : null}
        <RecordCard solid={picked} onClose={() => setPicked(null)} />
      </div>

      <div style={{
        borderTop: '1px solid var(--rule)', margin: '8px 2px 0', padding: '8px 0 4px',
        display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: 24, flexWrap: 'wrap',
      }}>
        <div data-plate-title="" style={{
          font: '10.5px/1.4 var(--serif)', letterSpacing: '.3em', textTransform: 'uppercase',
          color: 'var(--ink)', flex: '1 0 auto',
        }}>{cap}{mods ? ` · ${mods}` : ''}</div>
        <div data-plate-note="" style={{
          font: 'italic var(--fw-reg) 13px/1.45 var(--serif)', color: 'var(--ink-2)',
          textAlign: 'right', flex: '1 1 34ch', minWidth: '22ch',
        }}>
          {plateOn && !svg && refusedWhy
            ? `the flat plate for this view was refused: ${refusedWhy}`
            : [
              nm,
              unlocated ? `${unlocated} relaxation mark${unlocated === 1 ? '' : 's'} the placement could not locate — named, not placed` : null,
              ovDropped.length ? `${ovDropped.join(', ')} withheld: read off a plan, and this is a free view` : null,
            ].filter(Boolean).join(' · ')}
        </div>
      </div>

      {(disclosures || []).length ? (
        <div style={{ font: '11px/1.5 var(--serif)', color: 'var(--ink-2)', margin: '2px 2px 0' }}>
          {disclosures.map((d, i) => <div key={i}>{d}</div>)}
        </div>
      ) : null}
    </div>
  );
}

export default RoundPlate;
