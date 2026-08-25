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

/* The plate: the assembly stack drawn at real inches from members' own y/projection
   values. A band per member, its projection stepping the silhouette; the deepest
   assembly boundaries carry dimension ticks. Not the moulding profiles of
   dist/orders.html — those stay in the order tool; this is the engine's stack,
   stated plainly. */
function OrderPlate({ data }) {
  const asms = data.assemblies || [];
  const total = data.totals?.stack_height_in || asms.reduce((a, x) => a + (x.height_in || 0), 0);
  if (!total) return null;
  const maxProj = Math.max(6, ...asms.flatMap((a) => (a.members || []).map((m) => m.projection_in || 0)));
  const W = 46 + maxProj + 60, H = total;
  const cx = 30;                    // column centreline offset for band left edge
  let y = 0;                        // build from the bottom of the stack upward
  const bands = [];
  // assemblies arrive bottom-up (pedestal … cornice); draw bottom at H
  for (const a of asms) {
    for (const m of (a.members || [])) {
      bands.push({
        asm: a.id, id: m.id, name: m.name, note: m.note, conf: m.confidence,
        y0: y + (m.y_bottom_in || 0), h: (m.y_top_in ?? 0) - (m.y_bottom_in ?? 0) || m.height_in || 0,
        proj: m.projection_in || 0, side: m.side_by_side,
      });
    }
    a._y0 = y; a._y1 = y + (a.height_in || 0);
    y += a.height_in || 0;
  }
  return (
    <div style={{ background: 'var(--paper)', border: '1px solid var(--ink-2)',
      boxShadow: 'var(--shadow-plate)', padding: '18px 20px 12px' }}>
      <svg viewBox={`-8 -6 ${W + 40} ${H + 14}`} style={{ display: 'block', width: '100%', maxHeight: '72vh' }}
        role="img" aria-label={data.name}>
        {/* centre line of the stack */}
        <line x1={cx} y1={-4} x2={cx} y2={H + 4} stroke="var(--hair)" strokeWidth=".7"
          strokeDasharray="14 4 2.5 4" vectorEffect="non-scaling-stroke" />
        {bands.map((b, i) => (
          <g key={i}>
            <rect x={cx} y={H - b.y0 - b.h} width={16 + b.proj} height={Math.max(b.h, 0.05)}
              fill={b.side ? 'var(--sepia-pale)' : 'var(--paper-lit)'}
              stroke="var(--ink)" strokeWidth={b.h > 2 ? 1.1 : 0.7}
              vectorEffect="non-scaling-stroke">
              <title>{`${b.id} · ${b.name || ''} · ${inches(b.h)} high, ${inches(b.proj)} projection${b.note ? '\n' + b.note : ''}`}</title>
            </rect>
            {b.conf && b.conf !== 'high' && (
              <rect x={cx} y={H - b.y0 - b.h} width={16 + b.proj} height={Math.max(b.h, 0.05)}
                fill="none" stroke="var(--judge-unjudged)" strokeWidth="1"
                strokeDasharray="2 2" vectorEffect="non-scaling-stroke" />
            )}
          </g>
        ))}
        {/* assembly extents + names on the left, ticks not arrowheads */}
        {asms.map((a) => (
          <g key={a.id}>
            <line x1={cx - 8} y1={H - a._y0} x2={cx - 8} y2={H - a._y1}
              stroke="var(--draw-dim)" strokeWidth=".7" vectorEffect="non-scaling-stroke" />
            {[a._y0, a._y1].map((yy, i) => (
              <line key={i} x1={cx - 8 - 1.4} y1={H - yy + 1.4} x2={cx - 8 + 1.4} y2={H - yy - 1.4}
                stroke="var(--draw-dim)" strokeWidth=".9" vectorEffect="non-scaling-stroke" />
            ))}
            <text x={cx - 11} y={H - (a._y0 + a._y1) / 2} fontSize={Math.min(4.2, Math.max(2.6, a.height_in / 8))}
              fontFamily="var(--serif)" letterSpacing=".08em" fill="var(--ink-2)" textAnchor="end"
              dominantBaseline="middle" style={{ textTransform: 'uppercase' }}>
              {a.id}
            </text>
            <text x={cx - 11} y={H - (a._y0 + a._y1) / 2 + 4.6} fontSize="2.8" fontFamily="var(--mono)"
              fill="var(--ink-4)" textAnchor="end" dominantBaseline="middle">
              {inches(a.height_in)}
            </text>
          </g>
        ))}
        {/* overall stack dimension on the right */}
        <line x1={cx + 22 + maxProj} y1={0} x2={cx + 22 + maxProj} y2={H}
          stroke="var(--draw-dim)" strokeWidth=".7" vectorEffect="non-scaling-stroke" />
        {[0, H].map((yy, i) => (
          <line key={i} x1={cx + 22 + maxProj - 1.4} y1={yy + 1.4} x2={cx + 22 + maxProj + 1.4} y2={yy - 1.4}
            stroke="var(--draw-dim)" strokeWidth=".9" vectorEffect="non-scaling-stroke" />
        ))}
        <text x={cx + 25 + maxProj} y={H / 2} fontSize="3.4" fontFamily="var(--serif)"
          fill="var(--ink-2)" transform={`rotate(-90 ${cx + 25 + maxProj} ${H / 2})`}
          textAnchor="middle">{inches(total)} stack</text>
      </svg>
      <div style={{ borderTop: '1px solid var(--rule)', marginTop: 8, paddingTop: 8,
        display: 'flex', justifyContent: 'space-between', gap: 18, flexWrap: 'wrap' }}>
        <span style={{ font: 'var(--fw-med) 10.5px/1.3 var(--serif)', letterSpacing: '.3em',
          textTransform: 'uppercase', color: 'var(--ink)' }}>
          {(data.pack || '').split('-').join('·')}
        </span>
        <span style={{ font: 'italic var(--fw-reg) 12.5px/1.45 var(--serif)', color: 'var(--ink-2)' }}>
          Every band is a member the engine emitted — none traced. Hover a band for its record.
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
                {r.judgment ? 'yours to decide' : `${r.value} ${r.units || ''}`}
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
            <div style={{ display: 'flex', gap: 26, alignItems: 'flex-start', flexWrap: 'wrap' }}>
              <div style={{ flex: '0 1 380px', minWidth: 330 }}>
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

              {isOrder && (data.assemblies || []).some((a) => (a.members || []).length) && (
                <div style={{ flex: '0 1 330px', minWidth: 280 }}>
                  <OrderPlate data={data} />
                </div>
              )}

              <div style={{ flex: '1 1 460px', minWidth: 420, maxWidth: 780 }}>
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
