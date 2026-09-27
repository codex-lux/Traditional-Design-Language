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
import { FilterStrip, Chip, FilterGroup } from '../Chrome.jsx';
import { FilterInput } from '../components/FilterInput.jsx';
import { matches } from '../search/match.js';
import { PlateViewer } from '../components/PlateViewer.jsx';
import { ft } from '../sheet/derive.js';
import { PullPane } from '../components/PullPane.jsx';
import { plateGeometry } from '../proportions/plate.js';

const DEFAULT_PACK = 'gibbs-doric';

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

/* The plate's arithmetic -- extents, datum, the pedestal die's naked, which members state no
   projection, the bands and the frame -- lives in proportions/plate.js, a leaf with no imports,
   so it can be read without React (WP-14.1). This component draws what that function returns.
   The long account of how the plate is measured moved with the arithmetic it describes. */
function OrderPlate({ data }) {
  const P = plateGeometry(data);
  if (!P) return null;
  const { rows, H, nominal, r0, datumWords, stackWords, unrecorded, noGeometry, dieNaked, dieReason,
    bands, maxX, U, CAP, RIGHT, sy, dimX, bandPath } = P;
  const hasPedestal = rows.some((r) => r.id === 'pedestal' || r.id === 'subplinth');

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
            {/* A member whose projection nobody published is drawn at its naked, DASHED: its
                band is real and stands at least that far out, and a solid outline there would
                say it had been measured flush (WP-14.2). */}
            <path data-asm={b.asm} data-member={b.id} data-unpublished={b.unpublished ? '' : undefined}
              d={bp.d}
              fill={b.side ? 'var(--sepia-pale)' : 'var(--paper-lit)'}
              stroke={b.unpublished ? 'var(--judge-unjudged)' : 'var(--ink)'}
              strokeDasharray={b.unpublished ? '3 2' : undefined}
              strokeWidth={b.h > U * 1.2 ? 1.1 : 0.7}
              vectorEffect="non-scaling-stroke">
              <title>{`${b.id} · ${b.name || ''} · ${inches(b.h)} high, ${b.unpublished ? 'no projection published — drawn dashed at the naked' : `${inches(b.proj)} projection`}${b.side ? ' · stands beside its neighbour, not on it' : ''}${b.note ? '\n' + b.note : ''}`}</title>
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
        {/* named, so the walk can hold the ink to the near side of the gutter it opens */}
        <line data-mark="stack-dimension" x1={dimX} y1={sy(0)} x2={dimX} y2={sy(H)}
          stroke="var(--draw-dim)" strokeWidth=".7" vectorEffect="non-scaling-stroke" />
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
          axis to the outer face the engine constructed for it — none traced.
          {' '}{datumWords}
          {nominal ? ' This pack publishes no column diameter; the naked is drawn nominal.' : ''}
          {noGeometry ? ' No constructed geometry was served: every member is drawn at the column’s radius as a straight edge.' : ''}
          {unrecorded.size
            ? ` ${unrecorded.size} member(s) publish no projection and are drawn dashed at the naked — an absent figure, not a flush face.`
            : ` All ${bands.length} member(s) publish a projection.`}
          {hasPedestal && dieNaked == null && dieReason ? ` The pedestal’s die is not derived: ${dieReason}.` : ''}
          {stackWords ? ` ${stackWords}` : ''}
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
  const [packId, setPackId] = React.useState(selection?.pack || DEFAULT_PACK);
  const [packFilter, setPackFilter] = React.useState('');
  const [data, setData] = React.useState(null);
  const [compare, setCompare] = React.useState(null);
  const [diameter, setDiameter] = React.useState(12);
  const [ceiling, setCeiling] = React.useState(108);
  const [opening, setOpening] = React.useState(36);

  React.useEffect(() => {
    fetch('/api/proportions').then((r) => r.json()).then((r) => setPacks(r.packs || []));
  }, []);
  /* The URL owns this, so an ABSENT selection must reset to the default rather than leave the
   last one showing. Guarding the sync with `if (selection?.x)` meant pressing Back to a bare
   #/proportions left the panel displaying the record you had just left — the address bar and the
   screen disagreeing, which is the one thing the router exists to prevent. Found by an
   adversarial audit. */
  React.useEffect(() => { setPackId(selection?.pack || DEFAULT_PACK); }, [selection?.pack]);

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

  // The selected pack always survives the filter: the plate on the right is reading it,
  // and hiding its row while continuing to draw it would be a lie about where you are.
  const listed = packs.filter((p) => p.id === packId
    || matches(p, packFilter, ['id', 'name', 'kind', 'authority']));
  const byKind = [];
  for (const p of listed) {
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
        <FilterInput value={packFilter} onChange={setPackFilter} count={listed.length}
          label="Filter the proportion packs by name, kind or authority"
          placeholder={`filter ${packs.length} packs`} width={165} />
        <span style={{ width: 1, height: 18, background: 'var(--rule)' }} />
        {/* The sliders fold, and the fold shows the figures they are set to — which is
            what a reader wants from them nine visits in ten. */}
        {isOrder ? (
          <FilterGroup label="at" summary={`${diameter}″ column`}>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
              <Eyebrow as="span">column diameter</Eyebrow>
              <input type="range" min="6" max="36" step="1" value={diameter} aria-label="column diameter, inches"
                onChange={(e) => setDiameter(+e.target.value)}
                style={{ width: 110, accentColor: 'var(--gilt-deep)' }} />
              <span style={{ font: 'var(--type-data)', color: 'var(--ink)' }}>{diameter}″</span>
            </span>
          </FilterGroup>
        ) : (
          <FilterGroup label="at" summary={`${inches(ceiling)} ceiling · ${inches(opening)} opening`}>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
              <Eyebrow as="span">ceiling</Eyebrow>
              <input type="range" min="84" max="144" step="2" value={ceiling} aria-label="ceiling height, inches"
                onChange={(e) => setCeiling(+e.target.value)}
                style={{ width: 90, accentColor: 'var(--gilt-deep)' }} />
              <span style={{ font: 'var(--type-data)', color: 'var(--ink)' }}>{inches(ceiling)}</span>
              <Eyebrow as="span">opening</Eyebrow>
              <input type="range" min="18" max="96" step="2" value={opening} aria-label="opening width, inches"
                onChange={(e) => setOpening(+e.target.value)}
                style={{ width: 90, accentColor: 'var(--gilt-deep)' }} />
              <span style={{ font: 'var(--type-data)', color: 'var(--ink)' }}>{inches(opening)}</span>
            </span>
          </FilterGroup>
        )}
      </FilterStrip>

      <div style={{ flex: 1, display: 'flex', minHeight: 0 }}>
        {/* pack navigation — material modules lead */}
        <PullPane pane="proportions" side="left"
          style={{ borderRight: '1px solid var(--rule)', overflow: 'auto', padding: '12px 0 20px' }}>
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
                    {p.overlay_of && <span style={{ color: 'var(--ink-4)' }}> · overlay</span>}
                  </button>
                );
              })}
            </div>
          ))}
        </PullPane>

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
