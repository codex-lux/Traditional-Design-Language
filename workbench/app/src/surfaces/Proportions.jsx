/* Surface ⑩ — Proportions, plates first (WP-14.9; the page Lucas read on `trim-classical`).

   A practitioner reads a pack in one order and the page is that order, top to bottom:
   what the pack is (its name, its id beside it, its kind as a glossary word), the drawing,
   what goes wrong with it today, the rules worked out at the reader's building, whose figures
   they are, who uses the pack, where it comes from — and only then HOW IT WAS CHECKED, folded,
   because a proof is what a reader asks for second. The order is `proportions/page.js`'s
   `PAGE_SECTIONS`, and this file renders by walking it; every other decision the page makes
   about a payload is a pure function there, driven under `node --test`.

   THE URL DECIDES WHAT IS READ. A pack click, the filter, the ceiling, the opening and the
   column diameter all live in the address (`useSurfaceFilters`, replace), so a pack page is a
   link somebody can send and Back goes where it should. A bare `#/proportions` is the INDEX —
   it never shows a remembered or hard-coded pack (PRD §E, `DEFAULT_PACK` is gone). `?style=`
   narrows the index to that style's packs and, on a pack, marks the style in "used by" and says
   how the pack reaches it (`GET /api/styles/<id>/packs`).

   TWO PLATES. An order pack's stack is `OrderPlate`, below, UNCHANGED by this package. Every
   other pack with assemblies is `components/AssemblyPlate.jsx`, from served paths through a
   transform only. A pack with nothing to draw says so and draws nothing.

   Material modules lead the list: most traditional buildings were proportioned from a unit of
   material, not a column. Authorities compare at a common column DIAMETER, never a common
   module. */
import React from 'react';
import { api } from '../api/client.js';
import { useGlossary } from '../api/useGlossary.js';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { JudgmentMark } from '../components/JudgmentMark.jsx';
import { FilterStrip, Chip, FilterGroup } from '../Chrome.jsx';
import { FilterInput } from '../components/FilterInput.jsx';
import { matches } from '../search/match.js';
import { PlateViewer } from '../components/PlateViewer.jsx';
import { PullPane } from '../components/PullPane.jsx';
import { Term } from '../components/Term.jsx';
import { RecordLink } from '../components/RecordLink.jsx';
import { AssemblyPlate, AssemblyThumb, THUMB_W } from '../components/AssemblyPlate.jsx';
import { useSurfaceFilters } from '../filters/useFilters.js';
import { nav } from '../state/nav.js';
import { prefs } from '../state/prefs.js';
import { isPlainPrimaryClick } from '../names/recordLink.js';
import { ft } from '../sheet/derive.js';
import { feetInches16 } from '../fmt.js';
import { judgmentOf } from '../judgment.js';
import {
  FILTER_SPEC, RANGES, PROOF_FOLD, DEFAULT_DIAMETER_IN, requestFor, sliderAt, plateKind,
  pageSections, authorityLines, sourceLines, authorityWords, invariantMark, invariantTally, proofOpen, ruleState, figureWords,
  rangeWords, usedByGroups, reachOf, packsOfStyle, packGroups, packHref, orderOf,
  classASlider, zonesByAssembly, assemblyWords, ruleMark,
} from '../proportions/page.js';

function inches(v) {
  if (v == null) return '—';
  if (v >= 12) return ft(v / 12);
  const r = Math.round(v * 100) / 100;
  return `${r}″`;
}

/* The plate: the assembly stack drawn at real inches from the members' own y and
   projection values, as a HALF SECTION — every band runs from the column's axis out to
   its own naked plus its projection, which is what an authority means by a projection.
   A band per member, the deepest boundaries carrying dimension ticks.

   RULING OVERTURNED 26 Aug 2026 (WP-5.11). This comment used to end "Not the moulding profiles
   of dist/orders.html — those stay in the order tool; this is the engine's stack, stated
   plainly." That was a defensible line while the only moulding geometry in the corpus was a
   set of hand-tuned Beziers that belonged to one page. It is not defensible now: the profiles
   are CONSTRUCTED, in build/profiles.py, from the same member data this plate already draws,
   and a plate that shows a cyma recta as a straight line is not stating the engine's stack
   plainly — it is withholding the half of it a reader came for. The bands still carry every
   dimension, tick, hover and confidence mark they did; their outer edge is now the moulding.
   The plate still constructs nothing itself: it scales what the engine built.

   Two things this plate got wrong until 26 Aug 2026, both visible at a glance and both
   in the reading of the engine's output rather than in the engine:

   1. `y_bottom_in` and `y_top_in` are ABSOLUTE positions in the stack — proportion_engine
      .dimension() has already run the cumulative sum. Adding each assembly's own base to
      them a second time floated the base 90 inches clear of the plinth it sits on, the
      shaft another 108 above that, and drove the cornice out through the top of the
      frame. The captions down the left were drawn from a separate, correct running total,
      so the plate labelled a gap CAPITAL and pointed at nothing.
   2. Every band was drawn 16 units wide plus its projection, whatever the order's
      diameter — so the shaft, whose whole business is to be one diameter thick, came out
      a stick with mouldings wider than itself. The datum rule is the order tool's
      (build/orders_template.html::buildGeometry): the pedestal projects from the die's
      naked, base, shaft and capital from the column's radius AT THAT HEIGHT (which
      diminishes, and each authority says where the diminution begins), and the
      entablature from the naked of the frieze.

   Every annotation is sized in hundredths of the stack, so the plate is identical at
   any column diameter — which is the claim a proportional system makes. It cannot
   overflow its frame at 36 inches because it does not change shape at 36 inches. */
function OrderPlate({ data }) {
  const asms = data.assemblies || [];
  const stated = data.totals?.stack_height_in || 0;

  // assembly extents read off the members that are actually drawn, so a caption
  // brackets what is on the plate and not a parallel arithmetic of its own
  const rows = [];
  let cursor = 0;
  for (const a of asms) {
    const ms = a.members || [];
    const y0 = ms.length ? Math.min(...ms.map((m) => m.y_bottom_in ?? 0)) : cursor;
    const y1 = ms.length ? Math.max(...ms.map((m) => m.y_top_in ?? 0)) : cursor + (a.height_in || 0);
    rows.push({ id: a.id, stated_in: a.height_in, y0, y1, ms });
    cursor = Math.max(cursor, y1);
  }
  const H = Math.max(stated, cursor);
  if (!H) return null;

  const R = (data.totals?.lower_diameter_in || 0) / 2;
  const nominal = !R;                       // no published diameter: say so, do not imply one
  const r0 = R || H / 25;
  const r1 = (data.totals?.upper_diameter_in || 0) / 2 || r0;
  const col = data.column || {};
  const shaft = rows.find((x) => x.id === 'shaft');
  const entStart = col.entasis_begins_at ?? 1 / 3;
  const radiusAt = (y) => {
    if (!shaft || shaft.y1 <= shaft.y0) return r0;
    if (y <= shaft.y0) return r0;
    if (y >= shaft.y1) return r1;
    const t = (y - shaft.y0) / (shaft.y1 - shaft.y0);
    if (t <= entStart) return r0;
    const u = (t - entStart) / (1 - entStart);
    return r0 - (r0 - r1) * (u * u * (3 - 2 * u));   // cylindrical below, then smooth
  };
  /* WHICH WAY IS A PROJECTION MEASURED? The corpus answers two different ways — thirteen
     packs record a member's `projection_parts` as an offset FROM ITS OWN NAKED (Gibbs's
     Doric shaft body: 0) and twelve as an absolute radius FROM THE AXIS (Vignola's Ionic
     shaft body: exactly the semidiameter) — and until 26 Aug 2026 no pack said which, so
     a consumer had to guess. Adding a naked to a figure that is already a radius draws
     the shaft's own apophyge and astragal a whole semidiameter clear of the shaft they
     sit on. OQ 65 was ruled: the pack DECLARES it, `check_orders.py` verifies the
     declaration against the pack's own shaft, and this plate reads it rather than
     deriving it. A pack that reaches here without one is drawn the way the older half of
     the corpus is written, and says so on the sheet. */
  const fromAxis = data.projection_datum === 'axis';
  const undeclared = !data.projection_datum;

  const baseRow = rows.find((x) => x.id === 'base');
  const basePlinth = baseRow && baseRow.ms.length
    ? Math.max(0, ...baseRow.ms.map((m) => m.projection_in || 0)) : 0;
  // the pedestal die is naked to the base plinth that lands on it, read the pack's own way
  const dieNaked = basePlinth
    ? Math.max(r0, fromAxis ? basePlinth : r0 + basePlinth)
    : r0 * 1.2;
  const naked = (id, y) => {
    if (id === 'pedestal' || id === 'subplinth') return dieNaked;
    if (id === 'base' || id === 'shaft' || id === 'capital') return radiusAt(y);
    return r1;                                        // entablature: from the frieze naked
  };

  /* Under the radius reading a recorded 0 is not "at the axis" — it is NO PROJECTION
     RECORDED, and drawing the band to the centreline would collapse it. Those members
     take their naked instead and are counted, so the plate can say how many of its own
     edges the pack does not give rather than drawing a cornice that recedes behind the
     column. Under the offset reading 0 means flush with the naked, which is a statement
     the pack is making, and it is drawn as one. */
  const unrecorded = new Set();
  const outer = (id, key, y, proj) => {
    const nk = naked(id, y);
    if (!fromAxis) return nk + proj;
    if (!(proj > 0)) { unrecorded.add(key); return nk; }
    return Math.max(proj, nk);
  };

  /* WP-5.11: the member's own moulded edge, constructed by build/profiles.py and served with the
     pack. This plate does not know what a cyma is and must not learn: every copy of that
     knowledge this corpus has kept in two languages has eventually disagreed with itself. All
     that happens here is scale, flip, and emit. `f` is the ratio of the module the plate is
     drawing to the module the geometry was constructed at — pack geometry is linear in the
     module, which tests/test_profiles.py proves. */
  const geom = data.geometry;
  const f = geom && geom.module_in ? (data.module_in || geom.module_in) / geom.module_in : 1;
  const segsFor = {};
  if (geom) {
    for (const a of geom.assemblies) {
      for (const fc of a.faces || []) segsFor[`${a.id}.${fc.id}`] = fc;
    }
  }
  /* THE PATHS COME FROM PYTHON, in MODEL inches (x out from the axis, y up), and this plate
     applies an SVG transform instead of walking the segments (OQ 83, ruled 27 Aug 2026).

     What used to be here was `edgeCmds`, one of two JavaScript copies of the SVG sweep rule, and
     both copies were wrong: they emitted the inverse of the correct flag, so every arc on this
     plate drew as its own mirror — an ovolo as a cavetto, a torus as a hollow. A model-space path
     has no handedness for a consumer to get wrong; `<g transform="scale(1,-1)">` flips it and SVG
     mirrors the arcs correctly, which is its job and not this file's.

     One member as a closed band: out along its own foot, up its constructed profile, back to the
     axis. Falls back to the straight edge when a pack reaches here without geometry, so a plate
     is still drawn rather than blanked. */
  const bandPath = (b) => {
    const g = segsFor[b.key];
    if (!g || !g.path) {
      return { d: `M 0 ${sy(b.y0)} L ${b.x0} ${sy(b.y0)} L ${b.x1} ${sy(b.y1)} L 0 ${sy(b.y1)} Z`,
               transform: null };
    }
    // sy(y) = H - y, so the group is a y-flip about H, and f scales the module.
    return { d: g.path, transform: `translate(0,${H}) scale(${f},${-f})` };
  };

  const bands = [];
  for (const row of rows) {
    const span = row.y1 - row.y0;
    // The engine flags side_by_side off an assembly's sums_check, and a DERIVED shaft
    // (an authority that publishes a column height and no shaft) carries sums_check:false
    // with a single member. One member cannot stand beside anything, and filling it as
    // though it did would have the plate claim a triglyph-and-metope where there is only
    // a shaft nobody published. Its own medium confidence already draws the dashed mark
    // that says so.
    const group = row.ms.length > 1 ? row.ms.filter((m) => m.side_by_side) : [];
    // a side-by-side pair stands at the same height; draw the deeper one first so the
    // shallower reads as a step in front of it rather than a rectangle on top of it
    const ordered = group.length
      ? [...row.ms].sort((a, b) => (b.projection_in || 0) - (a.projection_in || 0))
      : row.ms;
    for (const m of ordered) {
      const y0 = m.y_bottom_in ?? row.y0, y1 = m.y_top_in ?? y0;
      const isShaftBody = row.id === 'shaft' && (y1 - y0) > span * 0.6;
      const proj = m.projection_in || 0;
      bands.push({
        key: `${row.id}.${m.id}`, asm: row.id, id: m.id, name: m.name, note: m.note,
        conf: m.confidence, side: m.side_by_side && row.ms.length > 1, y0, y1,
        // the shaft body is the column: it takes the naked at each height, which is what
        // makes it taper, and never a projection on top of the radius it already is
        x0: isShaftBody ? naked(row.id, y0) : outer(row.id, `${row.id}.${m.id}`, y0, proj),
        x1: isShaftBody ? naked(row.id, y1) : outer(row.id, `${row.id}.${m.id}`, y1, proj),
        h: y1 - y0, proj,
      });
    }
  }
  const maxX = Math.max(dieNaked, ...bands.map((b) => Math.max(b.x0, b.x1)));

  const U = H / 100;                    // one annotation unit: a hundredth of the stack
  const CAP = 30 * U, RIGHT = 16 * U;   // caption gutter, dimension gutter
  const sy = (y) => H - y;              // model up, screen down
  const dimX = maxX + 6 * U;

  return (
    <div style={{ background: 'var(--paper)', border: '1px solid var(--ink-2)',
      boxShadow: 'var(--shadow-plate)', padding: '18px 20px 12px' }}>
      <svg viewBox={`${-CAP} ${-3 * U} ${CAP + maxX + RIGHT} ${H + 6 * U}`}
        style={{ display: 'block', width: '100%' }} role="img" aria-label={data.name}>
        {/* the axis the whole order is measured from */}
        <line x1={0} y1={sy(-2 * U)} x2={0} y2={sy(H + 2 * U)} stroke="var(--hair)" strokeWidth=".7"
          strokeDasharray="14 4 2.5 4" vectorEffect="non-scaling-stroke" />
        {bands.map((b) => {
          const bp = bandPath(b);
          return (
          <g key={b.key} transform={bp.transform || undefined}>
            <path data-asm={b.asm} data-member={b.id}
              d={bp.d}
              fill={b.side ? 'var(--sepia-pale)' : 'var(--paper-lit)'}
              stroke="var(--ink)" strokeWidth={b.h > U * 1.2 ? 1.1 : 0.7}
              vectorEffect="non-scaling-stroke">
              <title>{`${b.id} · ${b.name || ''} · ${inches(b.h)} high, ${unrecorded.has(b.key) ? 'no projection recorded — drawn at the naked' : `${inches(b.proj)} projection`}${b.side ? ' · stands beside its neighbour, not on it' : ''}${b.note ? '\n' + b.note : ''}`}</title>
            </path>
            {b.conf && b.conf !== 'high' && (
              <path data-mark="confidence"
                d={bp.d}
                fill="none" stroke="var(--judge-unjudged)" strokeWidth="1"
                strokeDasharray="2 2" vectorEffect="non-scaling-stroke" />
            )}
          </g>
          );
        })}
        {/* assembly extents + names on the left, ticks not arrowheads */}
        {rows.map((a) => (
          <g key={a.id}>
            <line x1={-2.5 * U} y1={sy(a.y0)} x2={-2.5 * U} y2={sy(a.y1)}
              stroke="var(--draw-dim)" strokeWidth=".7" vectorEffect="non-scaling-stroke" />
            {[a.y0, a.y1].map((yy, i) => (
              <line key={i} x1={-2.5 * U - U} y1={sy(yy) + U} x2={-2.5 * U + U} y2={sy(yy) - U}
                stroke="var(--draw-dim)" strokeWidth=".9" vectorEffect="non-scaling-stroke" />
            ))}
            <text x={-4 * U} y={sy((a.y0 + a.y1) / 2) - 0.6 * U} fontSize={2.3 * U}
              fontFamily="var(--serif)" letterSpacing={0.18 * U} fill="var(--ink-2)" textAnchor="end"
              dominantBaseline="middle" style={{ textTransform: 'uppercase' }}>
              {a.id}
            </text>
            <text x={-4 * U} y={sy((a.y0 + a.y1) / 2) + 2.2 * U} fontSize={1.9 * U}
              fontFamily="var(--serif)" fill="var(--ink-4)" textAnchor="end" dominantBaseline="middle">
              {inches(a.y1 - a.y0)}
            </text>
          </g>
        ))}
        {/* overall stack dimension on the right */}
        <line x1={dimX} y1={sy(0)} x2={dimX} y2={sy(H)} stroke="var(--draw-dim)" strokeWidth=".7"
          vectorEffect="non-scaling-stroke" />
        {[0, H].map((yy, i) => (
          <line key={i} x1={dimX - U} y1={sy(yy) + U} x2={dimX + U} y2={sy(yy) - U}
            stroke="var(--draw-dim)" strokeWidth=".9" vectorEffect="non-scaling-stroke" />
        ))}
        <text x={dimX + 2.6 * U} y={sy(H / 2)} fontSize={2.4 * U} fontFamily="var(--serif)"
          fill="var(--ink-2)" transform={`rotate(-90 ${dimX + 2.6 * U} ${sy(H / 2)})`}
          textAnchor="middle">{inches(H)} stack</text>
        {/* the diameter the whole plate is drawn against, at the foot of the shaft */}
        {!nominal && (
          <g>
            <line x1={0} y1={sy(-1.4 * U)} x2={r0} y2={sy(-1.4 * U)} stroke="var(--draw-dim)"
              strokeWidth=".7" vectorEffect="non-scaling-stroke" />
            <text x={r0 + 1.2 * U} y={sy(-1.4 * U)} fontSize={1.9 * U} fontFamily="var(--serif)"
              fill="var(--ink-4)" dominantBaseline="middle">½ diameter {inches(r0)}</text>
          </g>
        )}
      </svg>
      <div style={{ borderTop: '1px solid var(--rule)', marginTop: 8, paddingTop: 8,
        display: 'flex', justifyContent: 'space-between', gap: 18, flexWrap: 'wrap' }}>
        <span style={{ font: 'var(--fw-med) 10.5px/1.3 var(--serif)', letterSpacing: '.3em',
          textTransform: 'uppercase', color: 'var(--ink)' }}>
          {(data.pack || '').split('-').join('·')}
        </span>
        <span style={{ font: 'italic var(--fw-reg) 12.5px/1.45 var(--serif)', color: 'var(--ink-2)',
          textAlign: 'right', maxWidth: '46ch' }}>
          Half the order in section: every band is a member the engine emitted, run from the
          axis to the outer face this pack states — none traced. This pack measures its
          projections{fromAxis ? ' from the axis' : ' from each member’s own naked'}, and
          says so{undeclared ? ' nowhere — that reading is assumed' : ''}.
          {nominal ? ' This pack publishes no column diameter; the naked is drawn nominal.' : ''}
          {unrecorded.size
            ? ` ${unrecorded.size} member${unrecorded.size === 1 ? '' : 's'} state no projection at all and are drawn at the naked — that is an absent figure, not a flush face.`
            : ''}
          {' '}Hover a band for its record.
        </span>
      </div>
    </div>
  );
}

/* ───────────────────────────── the page's parts ───────────────────────────── */

const SECTION_GAP = { marginTop: 30 };
const H3 = {
  font: 'var(--type-eyebrow)', letterSpacing: 'var(--tr-eyebrow)', textTransform: 'uppercase',
  color: 'var(--ink-2)', fontWeight: 500, margin: '0 0 10px',
};
const NOTE = { font: 'var(--fw-reg) 12.5px/1.55 var(--body)', color: 'var(--ink-2)', maxWidth: '76ch' };
const CELL = { font: 'var(--type-data-s)', color: 'var(--ink-2)', padding: '5px 14px 3px 0', verticalAlign: 'top',
  overflowWrap: 'anywhere' };
const TH = {
  font: 'var(--type-eyebrow)', letterSpacing: 'var(--tr-eyebrow)', textTransform: 'uppercase',
  color: 'var(--ink-2)', textAlign: 'left', padding: '0 14px 6px 0', fontWeight: 500,
  borderBottom: '1px solid var(--rule)',
};

/* A pack, named first with its id beside it, as a real link to its address on this surface.
   A plain click names a different pack on the SAME page (`nav.select`, which keeps the reader's
   measures, filter and style); a modified click is the browser's. `RecordLink` is not used here
   because it navigates through `nav.cite`, which drops the measures — right for a link into
   another surface, wrong for the next pack on this one. */
function PackLink({ id, name, selection, params, on, children }) {
  const href = packHref(id, selection, params);
  const onClick = (ev) => {
    if (!isPlainPrimaryClick(ev)) return;
    ev.preventDefault();
    nav.select({ pack: id });
  };
  return (
    <span className="tdl-record-link" data-on={on ? '' : undefined}>
      <a className="tdl-record-name" href={href} data-cite={`pack:${id}`} onClick={onClick}
        aria-current={on ? 'page' : undefined}
        style={{ borderBottom: on ? '2px solid var(--link-underline-hover)' : undefined }}>{children ?? name ?? id}</a>
      {(children ?? name) && name !== id && <span className="tdl-record-note">{id}</span>}
    </span>
  );
}

/* The list of packs by kind, the kind named by its glossary record. On the index it is the
   page; beside a pack it is the navigation. */
function PackList({ groups, selection, params, packId, compact }) {
  return (
    <div data-pack-list="">
      {groups.map((g) => (
        <div key={g.kind} style={{ marginBottom: compact ? 14 : 24 }}>
          <h3 data-kind-heading={g.kind} style={{ ...H3, padding: compact ? '0 12px' : 0, marginBottom: 6 }}>
            <Term field="pack.kind" value={g.kind} />
          </h3>
          {g.packs.map((p) => (
            <div key={p.id} data-pack-row={p.id} style={{ padding: compact ? '2px 12px' : '4px 0',
              borderLeft: compact ? `2px solid ${p.id === packId ? 'var(--gilt-deep)' : 'transparent'}` : 'none',
              background: compact && p.id === packId ? 'var(--paper-deep)' : 'transparent',
              font: compact ? 'var(--type-data-s)' : 'var(--fw-reg) 14px/1.5 var(--serif)',
              display: compact ? 'block' : 'flex', gap: 12, alignItems: 'flex-start' }}>
              {/* WP-14.24: the pack's first assembly at the wall datum, from the list route's served
                  geometry; a row whose pack has none keeps the column and draws nothing in it */}
              {!compact && (p.thumb
                ? <AssemblyThumb pack={p.id} thumb={p.thumb} />
                : <span data-thumb-none={p.drawing || 'none'} aria-hidden="true" style={{ width: THUMB_W, flex: 'none' }} />)}
              <div style={{ minWidth: 0 }}>
                <PackLink id={p.id} name={p.name} selection={selection} params={params} on={p.id === packId} />
                {!compact && authorityWords(p.authority) && (
                  <div data-pack-authority="" style={{ ...NOTE, font: 'var(--fw-reg) 12px/1.45 var(--body)', maxWidth: '90ch' }}>
                    {authorityWords(p.authority)}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

function Head({ data, meta, isOrder }) {
  const resolved = Array.isArray(data.resolved_from) && data.resolved_from.length > 1 ? data.resolved_from : null;
  return (
    <header data-section="head">
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 12, flexWrap: 'wrap' }}>
        <h2 data-pack-name="" style={{ font: 'var(--fw-reg) var(--fs-d3)/1.12 var(--display)',
          letterSpacing: 'var(--tr-display)', margin: '0 0 2px' }}>{data.name}</h2>
        <span className="tdl-record-note" data-pack-id="">{data.pack}</span>
      </div>
      <div style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)', marginTop: 4 }}>
        <Term field="pack.kind" value={data.kind || meta?.kind} />
        {resolved && <> · an overlay, read through {resolved.join(' → ')}</>}
      </div>
      <div data-module="" style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)', marginTop: 8, maxWidth: '90ch' }}>
        <Term id="module" /> {feetInches16(data.module_in)}
        {data.module_name && <span style={{ fontFamily: 'var(--serif)', fontSize: 13 }}> — {data.module_name}</span>}
        {' · '}{data.parts} <Term id="part">parts</Term> of {feetInches16(data.part_in)}
        {isOrder && data.diameters_per_module != null ? ` · ${data.diameters_per_module} diameters to the module` : ''}
      </div>
      {isOrder && data.totals && (
        <div style={{ marginTop: 10, maxWidth: 360 }}>
          {Object.entries(data.totals).map(([k, v]) => (
            <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '1px 0' }}>
              <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)' }}>{k.replace(/_/g, ' ')}</span>
              <span style={{ font: 'var(--type-data-s)', color: 'var(--ink)' }}>
                {k.endsWith('_in') ? feetInches16(v) : v}
              </span>
            </div>
          ))}
        </div>
      )}
    </header>
  );
}

/* The plate, or the sentence that says there is none. For the wall-datum plate, whether the
   drawing is at the reader's building is the PACK's to say (`module_bound_to`), and a pack that
   does not bind its module to the building is drawn at its own module and says so. */
function Plate({ data }) {
  const kind = plateKind(data);
  if (kind === 'stack') {
    return (
      <section data-section="plate" style={SECTION_GAP}>
        <PlateViewer label="the plate" height="clamp(400px, 72vh, 900px)"
          note="⌘/ctrl-scroll to zoom · drag to pan">
          <OrderPlate data={data} />
        </PlateViewer>
      </section>
    );
  }
  if (kind === 'assemblies') {
    const bound = data.module_bound_to;
    const at = data.at || {};
    return (
      <section data-section="plate" style={SECTION_GAP}>
        <p data-plate-at={bound || 'pack-module'} style={{ ...NOTE, margin: '0 0 10px' }}>
          {bound
            ? <>Drawn <Term id="your-building" />: the module is the {bound.replace(/_/g, ' ')}, {feetInches16(at[bound] ?? data.module_in)}.</>
            : <>Drawn at the pack’s own <Term id="module" />, {feetInches16(data.module_in)}: the pack does not
              bind its module to a measure of your building, so no slider moves this drawing.</>}
        </p>
        <AssemblyPlate data={data} />
        <ZonesNote assemblies={data.assemblies} />
      </section>
    );
  }
  return (
    <section data-section="plate" style={SECTION_GAP}>
      <p data-refused="no-assemblies" style={{ ...NOTE, margin: 0 }}>
        The record holds no <Term id="assembly" /> to draw: this pack gives rules, not an assembly, and no
        plate is drawn.
      </p>
    </section>
  );
}

/* What is true of zones on THIS plate, assembly by assembly (WP-14.24): the ones whose record
   gives the pack's division carry its zone string on the plate, and the ones whose record gives
   none are named as drawing none. Tranche 1's one sentence for every plate ("nothing in the
   record says where a zone ends") became false of the Georgian wall the day WP-14.18 declared it. */
function ZonesNote({ assemblies }) {
  const { zoned, unzoned } = zonesByAssembly(assemblies);
  const names = (ids) => ids.map((id) => assemblyWords(id)).join(', ');
  return (
    <div data-zones-note="" style={{ margin: '8px 2px 0' }}>
      {zoned.length > 0 && (
        <p data-zones-drawn={zoned.map((z) => z.id).join(' ')} style={{ ...NOTE, margin: 0 }}>
          Divided into <Term id="zone">zones</Term> as the record states:{' '}
          {zoned.map((z, i) => (
            <React.Fragment key={z.id}>{i > 0 && '; '}{assemblyWords(z.id)}, {z.parts}</React.Fragment>
          ))}.
        </p>
      )}
      {unzoned.length > 0 && (
        <p data-refused="zones" data-assemblies={unzoned.join(' ')} style={{ ...NOTE, margin: zoned.length ? '4px 0 0' : 0 }}>
          {zoned.length > 0
            ? <>No zone string where the record gives an assembly no <Term id="zone">zones</Term>: {names(unzoned)}.</>
            : <>No zone string: the record gives no assembly of this pack <Term id="zone">zones</Term>.</>}
        </p>
      )}
    </div>
  );
}

function Conflicts({ conflicts }) {
  return (
    <section data-section="conflicts" style={SECTION_GAP}>
      <h3 style={H3} data-conflicts-count={conflicts.length}>
        <Term id="pack-conflict" /> · {conflicts.length}
      </h3>
      {conflicts.map((c, i) => (
        <div key={i} data-conflict={c.with || ''} style={{ border: '1px solid var(--rule)',
          borderLeft: '2px solid var(--sev-serious)', padding: '11px 13px', marginBottom: 12, maxWidth: '84ch' }}>
          <div style={{ font: 'var(--type-eyebrow)', letterSpacing: 'var(--tr-eyebrow)',
            textTransform: 'uppercase', color: 'var(--sev-serious)', marginBottom: 6 }}>
            against {c.with}{c.severity ? ` · ${c.severity}` : ''}
          </div>
          <p style={{ font: 'var(--fw-reg) 13.5px/1.6 var(--body)', color: 'var(--ink)', margin: 0 }}>{c.statement}</p>
          {c.resolution && (
            <p style={{ font: 'var(--fw-reg) 13px/1.6 var(--body)', color: 'var(--ink-2)', margin: '8px 0 0' }}>
              <span style={{ font: 'var(--type-eyebrow)', letterSpacing: 'var(--tr-eyebrow)',
                textTransform: 'uppercase', color: 'var(--ink-2)', marginRight: 8 }}>resolution</span>
              {c.resolution}
            </p>
          )}
        </div>
      ))}
    </section>
  );
}

/* The rules at the reader's building, with a header row. A rule's value is a figure in the
   engine's notation; a rule the sources leave to the reader, one the engine could not evaluate
   and one worked outside the rooms it was calibrated for each carry the unjudged mark and say
   which, and none of them is drawn as a verdict. */
function Rules({ rules, styleId }) {
  return (
    <section data-section="rules" style={SECTION_GAP}>
      <h3 style={H3}><Term id="derived-rule">rules</Term> <Term id="your-building" /></h3>
      {/* A FIXED layout, because an auto one sizes each column to its longest unbreakable word
          (an expression in mono, a slot id) and the five together ran past the pane at 1440 px,
          clipping the range column and every note under the rail. Fixed, the table is the pane's
          width and a long word wraps inside its own column. */}
      <table data-rules="" style={{ borderCollapse: 'collapse', width: '100%', maxWidth: 1100, tableLayout: 'fixed' }}>
        {/* The slot and its dimension share a column: the slot's id is a margin note that does
            not wrap (WP-14.8's RecordLink), so its column must be wide enough to hold the
            longest one, and a fifth column for one short word was what the table could not
            afford. */}
        <colgroup>
          <col style={{ width: '32%' }} /><col style={{ width: '26%' }} />
          <col style={{ width: '24%' }} /><col style={{ width: '18%' }} />
        </colgroup>
        <thead>
          <tr data-rules-head="">
            <th style={TH}><Term id="slot" /> · dimension</th>
            <th style={TH}><Term id="derived-rule" /></th>
            <th style={TH}>value</th>
            <th style={TH}>range</th>
          </tr>
        </thead>
        <tbody>
          {rules.map((r, i) => {
            const state = ruleState(r);
            return (
              <React.Fragment key={i}>
                <tr data-rule={`${r.target_slot}.${r.dimension}`} data-quantity={r.quantity || undefined}
                  data-judgment={state}>
                  <td style={CELL}>
                    <RecordLink cite={`slot:${r.target_slot}`} ctx={styleId ? { style: styleId } : undefined} />
                    <div data-dimension="">{String(r.dimension || '').replace(/_/g, ' ')}</div>
                  </td>
                  <td style={{ ...CELL, fontFamily: 'var(--mono)', overflowWrap: 'anywhere' }}>
                    {r.expression}
                  </td>
                  <td data-value="" style={{ ...CELL, color: 'var(--ink)' }}>
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 7, flexWrap: 'wrap' }}>
                      <JudgmentMark state={ruleMark(r)} />
                      {r.judgment ? <Term id="judgment-yours-to-judge" />
                        : r.error ? <span>could not evaluate — {r.error}</span>
                          : r.value == null ? <Term id="judgment-unjudged">not evaluated</Term>
                            : <span data-figure="">{figureWords(r.value, r.units)}</span>}
                      {r.out_of_calibration && <span>· <Term id="your-building">out of calibration</Term></span>}
                      {r.scope_unjudged && <span>· <Term id="judgment-unjudged">scope not judged</Term></span>}
                    </span>
                  </td>
                  <td style={CELL}>
                    {rangeWords(r) || ''}{r.in_range === false ? ' · out of band' : ''}
                  </td>
                </tr>
                {r.note && (
                  <tr>
                    <td colSpan={4} style={{ ...NOTE, padding: '0 0 9px 16px', borderBottom: '1px solid var(--rule-soft)' }}>
                      {r.note}
                    </td>
                  </tr>
                )}
              </React.Fragment>
            );
          })}
        </tbody>
      </table>
    </section>
  );
}

function Authorities({ compare, packId, selection, params }) {
  const rows = compare.authorities || [];
  return (
    <section data-section="authorities" style={SECTION_GAP}>
      <h3 style={H3} data-authorities-count={rows.length}>
        <Term id="authority">authorities</Term> · {rows.length} · at {feetInches16(compare.at_common_column_diameter_in)} diameter
      </h3>
      <table style={{ borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={TH}><Term id="authority" /></th>
            <th style={TH}>year</th>
            <th style={TH}>column</th>
            <th style={TH}>entablature</th>
            <th style={TH}>ratio</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((a) => (
            <tr key={a.pack} data-authority-row={a.pack}
              style={{ background: a.pack === packId ? 'var(--paper-deep)' : 'transparent' }}>
              <td style={CELL}>
                <PackLink id={a.pack} name={a.authority} selection={selection} params={params} on={a.pack === packId} />
              </td>
              <td style={CELL}>{a.year}</td>
              <td style={{ ...CELL, color: 'var(--ink)' }}>{feetInches16(a.column_in)}</td>
              <td style={{ ...CELL, color: 'var(--ink)' }}>{feetInches16(a.entablature_in)}</td>
              <td style={CELL}>{a.entablature_over_column}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

function UsedBy({ usedBy, styleId }) {
  const groups = usedByGroups(usedBy);
  return (
    <section data-section="used-by" style={SECTION_GAP}>
      <h3 style={H3}>used by</h3>
      {groups.length === 0 && <p style={{ ...NOTE, margin: 0 }}>No style binds, receives or names this pack.</p>}
      {groups.map((g) => (
        <div key={g.key} data-used-by={g.key} style={{ marginBottom: 12 }}>
          <div style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)', marginBottom: 4 }}>
            {g.term ? <Term id={g.term} /> : <>named in the pack’s <code>applies_to</code>, not reached by it</>}
            {' · '}{g.rows.length}
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '3px 18px' }}>
            {g.rows.map((row) => (
              <span key={row.style} data-used-by-style={row.style}
                data-in-hand={row.style === styleId ? '' : undefined}
                style={{ font: 'var(--fw-reg) 13.5px/1.5 var(--serif)',
                  borderBottom: row.style === styleId ? '1px solid var(--gilt-deep)' : undefined }}>
                <RecordLink cite={`style:${row.style}`} />
                {row.from && <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)' }}>
                  {' '}from <RecordLink cite={`style:${row.from}`} /></span>}
              </span>
            ))}
          </div>
        </div>
      ))}
    </section>
  );
}

/* How the pack reaches the style the reader holds (`?style=`). */
function Reach({ reach, styleId, error }) {
  if (error) {
    return <p data-reach="unjudged" style={{ ...NOTE, margin: '10px 0 0' }}>Could not read which packs reach <RecordLink cite={`style:${styleId}`} />: {error}</p>;
  }
  if (!reach) return <p data-reach="loading" style={{ ...NOTE, margin: '10px 0 0' }}>reading how this pack reaches <RecordLink cite={`style:${styleId}`} />…</p>;
  return (
    <p data-reach={reach.relation} style={{ ...NOTE, margin: '10px 0 0' }}>
      <RecordLink cite={`style:${styleId}`} />
      {reach.term
        ? <>: <Term id={reach.term} />{reach.from && <> from <RecordLink cite={`style:${reach.from}`} /></>}</>
        : <>: this pack does not reach it.</>}
    </p>
  );
}

function Sources({ data }) {
  const lines = authorityLines(data);
  const works = sourceLines(data);
  const line = { font: 'italic var(--fw-reg) 13.5px/1.55 var(--serif)', color: 'var(--ink)',
    margin: '0 0 6px', maxWidth: '84ch' };
  return (
    <section data-section="sources" style={SECTION_GAP}>
      {lines.length > 0 && <h3 style={H3}><Term id="authority" /></h3>}
      {lines.map((s, i) => <p key={i} data-authority-line="" style={line}>{s}</p>)}
      {works.length > 0 && <h3 style={H3}><Term id="bibliographic-source" /></h3>}
      {works.map((s, i) => <p key={i} data-source-line="" style={line}>{s}</p>)}
    </section>
  );
}

/* "How this was checked": the pack's invariants, folded by default (prefs `folds.proof`), and
   counted in all three states while folded — a check that is hidden is not a check that is
   absent. `holds: null` is UNJUDGED: `invariantMark` is `JUDGMENT_MARK[judgmentOf(holds)]`,
   never a ternary on truthiness. */
function Proof({ invariants }) {
  React.useSyncExternalStore(prefs.subscribe, prefs.get);
  const open = proofOpen(prefs.fold(PROOF_FOLD));
  const tally = invariantTally(invariants);
  const bodyId = 'tdl-proportions-proof';
  return (
    <section data-section="proof" style={{ ...SECTION_GAP, borderTop: '1px solid var(--rule)', paddingTop: 14 }}>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 16, flexWrap: 'wrap' }}>
        <button type="button" data-proof-toggle="" aria-expanded={open} aria-controls={bodyId}
          onClick={() => prefs.setFold(PROOF_FOLD, !open)}
          style={{ ...H3, margin: 0, border: 'none', background: 'none', cursor: 'pointer', padding: 0 }}>
          <span aria-hidden="true" style={{ marginRight: 8 }}>{open ? '−' : '+'}</span>How this was checked
        </button>
        <span data-proof-tally="" style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)' }}>
          <Term id="invariant">invariants</Term>: {tally.passed} <Term id="judgment-passed" />
          {' · '}{tally.failed} <Term id="judgment-failed" />
          {' · '}{tally.unjudged} <Term id="judgment-unjudged" />
        </span>
      </div>
      {open && (
        <div id={bodyId} data-proof="" style={{ marginTop: 12 }}>
          {invariants.map((iv, i) => (
            <div key={i} data-invariant="" data-judgment={judgmentOf(iv.holds)} style={{ marginBottom: 8 }}>
              <JudgmentMark state={invariantMark(iv.holds)} label={iv.statement} reason={iv.expression} />
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

/* ───────────────────────────── the surface ───────────────────────────── */

export function Proportions({ selection }) {
  const f = useSurfaceFilters(FILTER_SPEC);
  const params = f.params;
  const sel = selection || {};
  const packId = sel.pack || null;
  const styleId = sel.style || null;
  const glossary = useGlossary();

  const [packs, setPacks] = React.useState(null);
  const [listError, setListError] = React.useState(null);
  React.useEffect(() => {
    let live = true;
    // through the client (WP-14.20), so a 401 raises the Gate; the line below still says why
    // the list is empty, in the client's own words for the failed request
    api.proportionPacks()
      .then((r) => { if (live) setPacks(r.packs || []); })
      .catch((e) => { if (live) { setListError(String(e.message || e)); setPacks([]); } });
    return () => { live = false; };
  }, []);

  const meta = (packs || []).find((p) => p.id === packId) || null;
  const isOrder = meta ? meta.kind === 'order-system' : false;
  // the class-A input goes only to the pack whose module IS it -- read off the list row, so the
  // first request already knows (the payload's own `module_bound_to` says the same)
  const req = requestFor({ isOrder, params: f.values, bound: meta ? meta.module_bound_to : null });
  const reqKey = JSON.stringify(req);

  /* The pack, dimensioned. The previous payload stays on screen while the SAME pack is
     re-dimensioned (a slider moving), so the plate does not blink; a different pack clears it. */
  const [got, setGot] = React.useState({ pack: null, data: null, error: null });
  React.useEffect(() => {
    if (!packId || packs === null) return undefined;
    let live = true;
    setGot((g) => (g.pack === packId ? g : { pack: packId, data: null, error: null }));
    api.proportions(packId, req)
      .then((d) => { if (live) setGot({ pack: packId, data: d, error: null }); })
      .catch((e) => { if (live) setGot({ pack: packId, data: null, error: String(e.message || e) }); });
    return () => { live = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [packId, reqKey, packs === null]);
  const data = got.pack === packId ? got.data : null;

  const diameter = req.column_diameter ?? DEFAULT_DIAMETER_IN;
  const [compare, setCompare] = React.useState(null);
  React.useEffect(() => {
    if (!isOrder || !packId) { setCompare(null); return undefined; }
    let live = true;
    const order = orderOf(packId);
    api.authorities(order, { column_diameter: diameter })
      .then((c) => { if (live) setCompare({ pack: packId, ...c }); })
      .catch(() => { if (live) setCompare(null); });
    return () => { live = false; };
  }, [packId, diameter, isOrder]);
  const compareHere = compare && compare.pack === packId && Array.isArray(compare.authorities) ? compare : null;

  const [styleGot, setStyleGot] = React.useState({ style: null, packs: null, error: null });
  React.useEffect(() => {
    if (!styleId) return undefined;
    let live = true;
    setStyleGot({ style: styleId, packs: null, error: null });
    api.stylePacks(styleId)
      .then((sp) => { if (live) setStyleGot({ style: styleId, packs: sp, error: null }); })
      .catch((e) => { if (live) setStyleGot({ style: styleId, packs: null, error: String(e.message || e) }); });
    return () => { live = false; };
  }, [styleId]);
  const stylePacks = styleGot.style === styleId ? styleGot.packs : null;
  const styleError = styleGot.style === styleId ? styleGot.error : null;

  const lookup = glossary.status === 'ready' ? glossary.lookup : null;
  const kindWord = React.useCallback((k) => {
    if (!lookup) return null;
    const rec = lookup.termFor('pack.kind', k);
    return rec && typeof rec.term === 'string' ? rec.term : null;
  }, [lookup]);
  const only = styleId && stylePacks ? packsOfStyle(stylePacks) : null;
  const groups = packGroups(packs || [], { q: f.values.q || '', keep: packId, only, words: kindWord, matches });
  const listed = groups.reduce((n, g) => n + g.packs.length, 0);

  const ceiling = sliderAt('ceiling', f.values, data?.at?.ceiling_height, 108);
  const opening = sliderAt('opening', f.values, data?.at?.opening_width, 36);
  const diamAt = sliderAt('diameter', f.values, null, DEFAULT_DIAMETER_IN);
  // WP-14.24: a class-A pack's own building input, driven by the served `module_bound_to` and
  // resting at what the payload was worked at; no slider at all on a pack whose module is not bound
  const classA = classASlider((data && data.module_bound_to) || (meta && meta.module_bound_to));
  const classAAt = classA
    ? sliderAt(classA.key, f.values, data?.at?.[classA.dimension] ?? data?.module_in, RANGES[classA.key].min) : null;

  const clearStyle = () => nav.select({ style: null }, { replace: true });

  const strip = (
    <FilterStrip filters={f}>
      <FilterInput value={f.values.q || ''} onChange={(v) => f.set('q', v)} count={listed}
        label="Filter the proportion packs by name, kind or authority"
        placeholder="filter the packs" width={165} />
      {styleId && (
        <span data-style-in-hand={styleId} style={{ display: 'inline-flex', alignItems: 'center', gap: 6,
          font: 'var(--type-data-s)', color: 'var(--ink-2)', whiteSpace: 'nowrap' }}>
          for <RecordLink cite={`style:${styleId}`} />
          <Chip on onClick={clearStyle} title="read every pack again">×</Chip>
        </span>
      )}
      {packId && <span style={{ width: 1, height: 18, background: 'var(--rule)' }} />}
      {packId && (isOrder ? (
        <FilterGroup label="at" summary={`${feetInches16(diamAt)} column`}>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
            <Eyebrow as="span">column diameter</Eyebrow>
            <input type="range" {...RANGES.diameter} value={diamAt} aria-label="column diameter, inches"
              onChange={(e) => f.set('diameter', e.target.value)}
              style={{ width: 110, accentColor: 'var(--gilt-deep)' }} />
            <span style={{ font: 'var(--type-data)', color: 'var(--ink)' }}>{feetInches16(diamAt)}</span>
          </span>
        </FilterGroup>
      ) : (
        <FilterGroup label="at" summary={`${feetInches16(ceiling)} ceiling · ${feetInches16(opening)} opening`
          + (classA ? ` · ${feetInches16(classAAt)} ${classA.words}` : '')}>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
            <Eyebrow as="span">ceiling</Eyebrow>
            <input type="range" {...RANGES.ceiling} value={ceiling} aria-label="ceiling height, inches"
              onChange={(e) => f.set('ceiling', e.target.value)}
              style={{ width: 90, accentColor: 'var(--gilt-deep)' }} />
            <span style={{ font: 'var(--type-data)', color: 'var(--ink)' }}>{feetInches16(ceiling)}</span>
            <Eyebrow as="span">opening</Eyebrow>
            <input type="range" {...RANGES.opening} value={opening} aria-label="opening width, inches"
              onChange={(e) => f.set('opening', e.target.value)}
              style={{ width: 90, accentColor: 'var(--gilt-deep)' }} />
            <span style={{ font: 'var(--type-data)', color: 'var(--ink)' }}>{feetInches16(opening)}</span>
            {classA && (
              <span data-class-a={classA.dimension} style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
                <Eyebrow as="span">{classA.words}</Eyebrow>
                <input type="range" {...RANGES[classA.key]} value={classAAt} aria-label={`${classA.words}, inches`}
                  onChange={(e) => f.set(classA.key, e.target.value)}
                  style={{ width: 90, accentColor: 'var(--gilt-deep)' }} />
                <span style={{ font: 'var(--type-data)', color: 'var(--ink)' }}>{feetInches16(classAAt)}</span>
              </span>
            )}
          </span>
        </FilterGroup>
      ))}
    </FilterStrip>
  );

  const listState = packs === null ? <p style={NOTE}>reading the packs…</p>
    : listError ? <p style={NOTE}>The pack list could not be read: {listError}</p>
      : styleId && !stylePacks && !styleError ? <p style={NOTE}>reading which packs reach the style…</p>
        : null;

  /* THE INDEX: no pack named, so no pack drawn. */
  if (!packId) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', minHeight: 0, flex: 1 }}>
        {strip}
        <div data-proportions-index="" style={{ flex: 1, overflow: 'auto', minHeight: 0, padding: '18px 24px 34px' }}>
          {styleError && <p style={NOTE}>Could not read which packs reach <RecordLink cite={`style:${styleId}`} />: {styleError}</p>}
          {listState || <PackList groups={groups} selection={sel} params={params} packId={null} />}
        </div>
      </div>
    );
  }

  const sections = data ? pageSections(data, { authorities: compareHere ? compareHere.authorities : null }) : [];
  const render = {
    head: () => <Head key="head" data={data} meta={meta} isOrder={isOrder} />,
    plate: () => <Plate key="plate" data={data} />,
    conflicts: () => <Conflicts key="conflicts" conflicts={data.conflicts} />,
    rules: () => <Rules key="rules" rules={data.derived_rules} styleId={styleId} />,
    authorities: () => <Authorities key="authorities" compare={compareHere} packId={packId} selection={sel} params={params} />,
    'used-by': () => <UsedBy key="used-by" usedBy={data.used_by} styleId={styleId} />,
    sources: () => <Sources key="sources" data={data} />,
    proof: () => <Proof key="proof" invariants={data.invariants || []} />,
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: 0, flex: 1 }}>
      {strip}
      <div style={{ flex: 1, display: 'flex', minHeight: 0 }}>
        <PullPane pane="proportions" side="left"
          style={{ borderRight: '1px solid var(--rule)', overflow: 'auto', padding: '12px 0 20px' }}>
          {listState || <PackList groups={groups} selection={sel} params={params} packId={packId} compact />}
        </PullPane>
        <div data-pack-page={packId} style={{ flex: 1, overflow: 'auto', minHeight: 0, padding: '18px 24px 34px' }}>
          {got.error && got.pack === packId ? (
            <p style={NOTE}>This pack could not be dimensioned: {got.error}</p>
          ) : !data ? (
            <p style={{ ...NOTE, font: 'var(--type-body)' }}>dimensioning…</p>
          ) : (
            <div style={{ maxWidth: 1240 }}>
              {sections.map((s) => (
                <React.Fragment key={s}>
                  {render[s]()}
                  {s === 'head' && styleId && (
                    <Reach reach={stylePacks ? reachOf(stylePacks, packId) : null} styleId={styleId} error={styleError} />
                  )}
                </React.Fragment>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
