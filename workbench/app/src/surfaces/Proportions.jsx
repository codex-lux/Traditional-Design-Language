/* Surface ⑩ — Proportions & Orders, live. The grammar drawn from the engine's own
   dimension() output — every band on the plate is a member the engine emitted, none
   traced. The non-classical packs (brick course, timber bay, sash light, storey
   graduation, log module) are equal citizens and lead the navigation: most
   traditional buildings were proportioned from a material module, not a column.
   Authorities compare at a common column DIAMETER, never a common module. Rules
   flagged judgment render the hatch, unfilled — the sources do not determine them. */
import React from 'react';
import { api } from '../api/client.js';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { JudgmentMark } from '../components/JudgmentMark.jsx';
import { FilterStrip, Chip } from '../Chrome.jsx';
import { PlateViewer } from '../components/PlateViewer.jsx';
import { ft } from '../sheet/derive.js';

const KIND_LABEL = {
  'module-system': 'material modules', 'trim-system': 'trim systems',
  'opening-system': 'openings', 'room-system': 'rooms', 'facade-system': 'facades',
  'order-system': 'the orders',
};

function inches(v) {
  if (v == null) return '—';
  if (v >= 12) return ft(v / 12);
  const r = Math.round(v * 100) / 100;
  return `${r}″`;
}

/* The plate: the assembly stack drawn at real inches from the members' own y and
   projection values, as a HALF SECTION — every band runs from the column's axis out to
   its own naked plus its projection, which is what an authority means by a projection.
   A band per member, the deepest boundaries carrying dimension ticks. Not the moulding
   profiles of dist/orders.html — those stay in the order tool; this is the engine's
   stack, stated plainly.

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
        {bands.map((b) => (
          <g key={b.key}>
            <path data-asm={b.asm} data-member={b.id}
              d={`M 0 ${sy(b.y0)} L ${b.x0} ${sy(b.y0)} L ${b.x1} ${sy(b.y1)} L 0 ${sy(b.y1)} Z`}
              fill={b.side ? 'var(--sepia-pale)' : 'var(--paper-lit)'}
              stroke="var(--ink)" strokeWidth={b.h > U * 1.2 ? 1.1 : 0.7}
              vectorEffect="non-scaling-stroke">
              <title>{`${b.id} · ${b.name || ''} · ${inches(b.h)} high, ${unrecorded.has(b.key) ? 'no projection recorded — drawn at the naked' : `${inches(b.proj)} projection`}${b.side ? ' · stands beside its neighbour, not on it' : ''}${b.note ? '\n' + b.note : ''}`}</title>
            </path>
            {b.conf && b.conf !== 'high' && (
              <path data-mark="confidence"
                d={`M 0 ${sy(b.y0)} L ${b.x0} ${sy(b.y0)} L ${b.x1} ${sy(b.y1)} L 0 ${sy(b.y1)} Z`}
                fill="none" stroke="var(--judge-unjudged)" strokeWidth="1"
                strokeDasharray="2 2" vectorEffect="non-scaling-stroke" />
            )}
          </g>
        ))}
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
          says so{undeclared ? ' nowhere — that reading is assumed (OQ 65)' : ' (OQ 65: the corpus uses both)'}.
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

function RulesTable({ rules }) {
  return (
    <table style={{ borderCollapse: 'collapse', width: '100%' }}>
      <tbody>
        {rules.map((r, i) => (
          <React.Fragment key={i}>
            <tr>
              <td style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)', padding: '6px 14px 2px 0',
                whiteSpace: 'nowrap', verticalAlign: 'top' }}>
                {r.judgment && (
                  <span aria-hidden="true" style={{ display: 'inline-block', width: 9, height: 9,
                    marginRight: 7, border: '1px solid var(--judge-unjudged)',
                    backgroundImage: 'var(--hatch-unjudged)', verticalAlign: 'baseline' }} />
                )}
                {r.target_slot}
              </td>
              <td style={{ font: 'var(--type-data-s)', color: 'var(--ink-3)', padding: '6px 12px 2px 0',
                verticalAlign: 'top' }}>{r.dimension}</td>
              <td style={{ font: 'var(--type-data-s)', color: 'var(--ink-3)', padding: '6px 12px 2px 0',
                fontFamily: 'var(--mono)', verticalAlign: 'top', maxWidth: 280, overflowWrap: 'break-word' }}>
                {r.expression}
              </td>
              <td style={{ font: 'var(--type-data)', color: r.judgment ? 'var(--ink-3)' : 'var(--ink)',
                padding: '6px 12px 2px 0', whiteSpace: 'nowrap', verticalAlign: 'top' }}>
                {/* `error` is the engine saying it could not evaluate this rule. It was
                    outside core.py's RULE_KEYS until 26 Aug 2026, so it never arrived and
                    this cell drew "null in" — a refusal rendered as a measurement, which is
                    the one direction this corpus must not round in. */}
                {r.judgment ? 'yours to decide'
                  : r.error ? <span style={{ color: 'var(--ink-3)' }}>could not evaluate — {r.error}</span>
                  : r.value == null ? <span style={{ color: 'var(--ink-3)' }}>not evaluated</span>
                  : `${r.value} ${r.units || ''}`}
              </td>
              <td style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)', padding: '6px 0 2px 0',
                whiteSpace: 'nowrap', verticalAlign: 'top' }}>
                {r.range ? `${r.range[0]}–${r.range[1]}` : ''}
                {r.in_range === false ? ' · out of band' : ''}
              </td>
            </tr>
            {r.note && (
              <tr>
                <td colSpan={5} style={{ font: 'var(--fw-reg) 12.5px/1.55 var(--body)', color: 'var(--ink-3)',
                  padding: '0 0 8px 16px', borderBottom: '1px solid var(--rule-soft)',
                  maxWidth: '78ch' }}>{r.note}</td>
              </tr>
            )}
          </React.Fragment>
        ))}
      </tbody>
    </table>
  );
}

export function Proportions({ onCite, selection }) {
  const [packs, setPacks] = React.useState([]);
  const [packId, setPackId] = React.useState(selection?.pack || 'gibbs-doric');
  const [data, setData] = React.useState(null);
  const [compare, setCompare] = React.useState(null);
  const [diameter, setDiameter] = React.useState(12);
  const [ceiling, setCeiling] = React.useState(108);
  const [opening, setOpening] = React.useState(36);

  React.useEffect(() => {
    fetch('/api/proportions').then((r) => r.json()).then((r) => setPacks(r.packs || []));
  }, []);
  React.useEffect(() => { if (selection?.pack) setPackId(selection.pack); }, [selection?.pack]);

  const meta = packs.find((p) => p.id === packId);
  const isOrder = meta?.kind === 'order-system';

  React.useEffect(() => {
    if (!packId) return;
    setData(null);
    api.proportions(packId, {
      members: true,
      column_diameter: isOrder ? diameter : undefined,
      ceiling_height: ceiling, opening_width: opening,
    }).then(setData).catch(() => setData(null));
  }, [packId, diameter, ceiling, opening, isOrder]);

  React.useEffect(() => {
    if (!isOrder || !packId) { setCompare(null); return; }
    const order = packId.split('-').slice(1).join('-');
    api.authorities(order, { column_diameter: diameter }).then(setCompare).catch(() => setCompare(null));
  }, [packId, diameter, isOrder]);

  const byKind = [];
  for (const p of packs) {
    const g = byKind.find((x) => x.kind === p.kind);
    if (g) g.items.push(p); else byKind.push({ kind: p.kind, items: [p] });
  }
  const judgment = new Set(data?.judgment_rules || []);
  const rules = data?.derived_rules || [];
  const hasPlate = isOrder && (data?.assemblies || []).some((a) => (a.members || []).length);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: 0, flex: 1 }}>
      <FilterStrip right={
        <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)' }}>
          comparisons at a common column diameter · never a common module
        </span>
      }>
        {isOrder ? (
          <>
            <Eyebrow as="span">column diameter</Eyebrow>
            <input type="range" min="6" max="36" step="1" value={diameter}
              onChange={(e) => setDiameter(+e.target.value)}
              style={{ width: 110, accentColor: 'var(--gilt-deep)' }} />
            <span style={{ font: 'var(--type-data)', color: 'var(--ink)' }}>{diameter}″</span>
          </>
        ) : (
          <>
            <Eyebrow as="span">ceiling</Eyebrow>
            <input type="range" min="84" max="144" step="2" value={ceiling}
              onChange={(e) => setCeiling(+e.target.value)}
              style={{ width: 90, accentColor: 'var(--gilt-deep)' }} />
            <span style={{ font: 'var(--type-data)', color: 'var(--ink)' }}>{inches(ceiling)}</span>
            <Eyebrow as="span">opening</Eyebrow>
            <input type="range" min="18" max="96" step="2" value={opening}
              onChange={(e) => setOpening(+e.target.value)}
              style={{ width: 90, accentColor: 'var(--gilt-deep)' }} />
            <span style={{ font: 'var(--type-data)', color: 'var(--ink)' }}>{inches(opening)}</span>
          </>
        )}
      </FilterStrip>

      <div style={{ flex: 1, display: 'flex', minHeight: 0 }}>
        {/* pack navigation — material modules lead */}
        <div style={{ width: 250, flex: 'none', borderRight: '1px solid var(--rule)', overflow: 'auto',
          minHeight: 0, padding: '12px 0 20px' }}>
          {byKind.map((g) => (
            <div key={g.kind} style={{ marginBottom: 14 }}>
              <Eyebrow style={{ padding: '0 12px 6px' }}>{KIND_LABEL[g.kind] || g.kind}</Eyebrow>
              {g.items.map((p) => {
                const on = p.id === packId;
                return (
                  <button key={p.id} type="button" onClick={() => setPackId(p.id)}
                    style={{ display: 'block', width: '100%', textAlign: 'left', padding: '3px 12px',
                      borderLeft: '2px solid ' + (on ? 'var(--gilt-deep)' : 'transparent'),
                      background: on ? 'var(--paper-deep)' : 'transparent',
                      font: 'var(--type-data-s)', color: on ? 'var(--ink)' : 'var(--ink-2)' }}>
                    {p.id}
                    {p.overlay_on && <span style={{ color: 'var(--ink-4)' }}> · overlay</span>}
                  </button>
                );
              })}
            </div>
          ))}
        </div>

        {/* the pack, dimensioned */}
        <div style={{ flex: 1, overflow: 'auto', minHeight: 0, padding: '18px 24px 34px' }}>
          {!data ? (
            <p style={{ font: 'var(--type-body)', color: 'var(--ink-3)' }}>dimensioning…</p>
          ) : (
            /* The plate is the instrument on this surface, so it gets a column of its own
               beside the record rather than a place in a wrapping row: at any pane narrower
               than about 830px the old flex row put it BELOW the invariants and the
               authorities table, a screen and a half down, where a reader looking for the
               drawing would not find it. The rules table spans the full width underneath,
               which is what a five-column table with a paragraph of note per row wanted
               all along. */
            /* `minmax(300px, …)` twice is a hard 626px floor with no query to relax it,
               and at the app's own enforced minimum (#root min-width 1380, less the 236px
               rail, the 344px AI rail, the 250px pack nav and the padding) this pane gets
               502px — so the fix for "the plate ends up below the tables" bought a
               horizontal scrollbar. `auto-fit` with a 290px track drops to one column
               when it must, which is the wrap the old layout had, without the wrap
               putting the drawing a screen and a half down. */
            <div style={{ display: 'grid', gap: 26, alignItems: 'start', maxWidth: 1240,
              gridTemplateColumns: hasPlate
                ? 'repeat(auto-fit, minmax(min(290px, 100%), 1fr))' : 'minmax(0, 1fr)' }}>
              <div>
                <Eyebrow>{meta?.kind}{data.resolved_from?.length > 1 ? ` · overlay resolved through ${data.resolved_from.join(' → ')}` : ''}</Eyebrow>
                <h2 style={{ font: 'var(--fw-reg) var(--fs-d3)/1.12 var(--display)',
                  letterSpacing: 'var(--tr-display)', margin: '6px 0 3px' }}>{data.name}</h2>
                {data.authority && (
                  <p style={{ font: 'italic var(--fw-reg) 13px/1.5 var(--serif)', color: 'var(--ink-2)',
                    margin: '4px 0 0' }}>{data.authority}</p>
                )}
                <div style={{ font: 'var(--type-data-s)', color: 'var(--ink-3)', marginTop: 8 }}>
                  module {inches(data.module_in)} · {data.parts} parts of {data.part_in}″
                  {isOrder ? ` · ${data.diameters_per_module} diameters/module` : ''}
                </div>

                {isOrder && data.totals && (
                  <div style={{ marginTop: 12, borderTop: '1px solid var(--rule)', paddingTop: 10 }}>
                    {Object.entries(data.totals).map(([k, v]) => (
                      <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '1px 0' }}>
                        <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-3)' }}>{k.replace(/_/g, ' ')}</span>
                        <span style={{ font: 'var(--type-data-s)', color: 'var(--ink)' }}>
                          {k.includes('_in') ? inches(v) : v}
                        </span>
                      </div>
                    ))}
                  </div>
                )}

                {(data.invariants || []).length > 0 && (
                  <div style={{ marginTop: 14 }}>
                    <Eyebrow style={{ marginBottom: 8 }}>invariants · proved against the data</Eyebrow>
                    {data.invariants.map((iv, i) => (
                      <div key={i} style={{ marginBottom: 8 }}>
                        <JudgmentMark state={iv.holds ? 'pass' : 'fail'} label={iv.statement}
                          reason={iv.expression} />
                      </div>
                    ))}
                  </div>
                )}

                {compare?.authorities && (
                  <div style={{ marginTop: 16 }}>
                    <Eyebrow style={{ marginBottom: 8 }}>
                      five authorities · at {compare.at_common_column_diameter_in}″ diameter
                    </Eyebrow>
                    <table style={{ borderCollapse: 'collapse' }}>
                      <thead>
                        <tr>
                          {['authority', 'year', 'column', 'entablature', 'ratio'].map((h) => (
                            <th key={h} style={{ font: 'var(--type-eyebrow)', letterSpacing: 'var(--tr-eyebrow)',
                              textTransform: 'uppercase', color: 'var(--ink-4)', textAlign: 'left',
                              padding: '0 14px 5px 0', fontWeight: 500 }}>{h}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {compare.authorities.map((a) => {
                          const on = a.pack === packId;
                          return (
                            <tr key={a.pack} style={{ cursor: 'pointer',
                              background: on ? 'var(--paper-deep)' : 'transparent' }}
                              onClick={() => setPackId(a.pack)}>
                              <td style={{ font: 'var(--type-data-s)', color: on ? 'var(--gilt-deep)' : 'var(--ink-2)',
                                padding: '2px 14px 2px 0' }}>{a.authority}</td>
                              <td style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)', padding: '2px 14px 2px 0' }}>{a.year}</td>
                              <td style={{ font: 'var(--type-data-s)', color: 'var(--ink)', padding: '2px 14px 2px 0' }}>{inches(a.column_in)}</td>
                              <td style={{ font: 'var(--type-data-s)', color: 'var(--ink)', padding: '2px 14px 2px 0' }}>{inches(a.entablature_in)}</td>
                              <td style={{ font: 'var(--type-data-s)', color: 'var(--ink-3)', padding: '2px 0' }}>{a.entablature_over_column}</td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>

              {hasPlate && (
                <div style={{ minWidth: 0 }}>
                  <PlateViewer label="the plate" height="clamp(400px, 72vh, 900px)"
                    note="a cyma is three inches — ⌘/ctrl-scroll to zoom · drag to pan">
                    <OrderPlate data={data} />
                  </PlateViewer>
                </div>
              )}

              <div style={{ gridColumn: '1 / -1', minWidth: 0 }}>
                {rules.length > 0 && (
                  <>
                    <Eyebrow style={{ marginBottom: 4 }}>
                      how the pack governs · {rules.length} rules
                      {judgment.size ? ` · ${judgment.size} deferred to you` : ''}
                    </Eyebrow>
                    <p style={{ font: 'var(--fw-reg) 12.5px/1.5 var(--body)', color: 'var(--ink-3)',
                      margin: '0 0 10px', maxWidth: '72ch' }}>
                      A hatched mark is a rule the sources do not determine — the pack asks rather
                      than inventing a number.
                    </p>
                    <RulesTable rules={rules} />
                  </>
                )}

                {(data.conflicts || []).length > 0 && (
                  <div style={{ marginTop: 22 }}>
                    <Eyebrow style={{ marginBottom: 8 }}>
                      conflicts with building today · {data.conflicts.length}
                    </Eyebrow>
                    {data.conflicts.map((c, i) => (
                      <div key={i} style={{ border: '1px solid var(--rule)',
                        borderLeft: '2px solid var(--sev-serious)', padding: '11px 13px', marginBottom: 12 }}>
                        <div style={{ font: 'var(--type-eyebrow)', letterSpacing: 'var(--tr-eyebrow)',
                          textTransform: 'uppercase', color: 'var(--sev-serious)', marginBottom: 6 }}>
                          against {c.with}{c.severity ? ` · ${c.severity}` : ''}
                        </div>
                        <p style={{ font: 'var(--fw-reg) 13.5px/1.6 var(--body)', color: 'var(--ink)',
                          margin: 0, maxWidth: '76ch' }}>{c.statement}</p>
                        {c.resolution && (
                          <p style={{ font: 'var(--fw-reg) 13px/1.6 var(--body)', color: 'var(--ink-2)',
                            margin: '8px 0 0', maxWidth: '76ch' }}>
                            <span style={{ font: 'var(--type-eyebrow)', letterSpacing: 'var(--tr-eyebrow)',
                              textTransform: 'uppercase', color: 'var(--ink-3)', marginRight: 8 }}>resolution</span>
                            {c.resolution}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
