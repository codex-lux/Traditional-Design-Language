/* Surface ② — the Phylogeny, live. 164 taxa on a broken time axis (nearly all the
   density sits in 1600–2026; the classical tail is compressed and the break is drawn,
   not implied). Both hierarchies at once: rank as indent (browsing only), lineage as
   edges — cascade-carrying edges structurally heavier than claimed ancestry. Select
   two to compare, and the comparison shows the corpus's real tells. */
import React from 'react';
import { api } from '../api/client.js';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { EdgeGlyph } from '../components/EdgeGlyph.jsx';
import { FilterStrip, Chip } from '../Chrome.jsx';

const BREAK_AT = 1600, BREAK_FRAC = 0.18;
function tScale(y) {
  if (y <= BREAK_AT) return ((y + 700) / (BREAK_AT + 700)) * BREAK_FRAC;
  return BREAK_FRAC + ((y - BREAK_AT) / (2026 - BREAK_AT)) * (1 - BREAK_FRAC);
}
const CARRIES = { descends_from: 1, regional_of: 1 };
const RANK_INDENT = { tradition: 0, family: 10, style: 20, variant: 30 };
const TRADITION_HUES = {
  'classical-mediterranean': 'var(--t0)',
  'british-isles': 'var(--t1)',
  'northern-european-vernacular': 'var(--t2)',
  'iberian-mediterranean': 'var(--t3)',
  'north-american': 'var(--t4)',
};
const yr = (v) => (v == null ? '?' : v < 0 ? Math.abs(v) + ' BC' : String(v));

export function Phylogeny({ onCite, selection }) {
  const [graph, setGraph] = React.useState(null);
  const [sel, setSel] = React.useState(selection?.style || 'tidewater-georgian');
  const [compare, setCompare] = React.useState(null);
  const [cmpData, setCmpData] = React.useState(null);
  const [selInfo, setSelInfo] = React.useState(null);
  const [showClaims, setShowClaims] = React.useState(true);
  const [rankFilter, setRankFilter] = React.useState(null);

  React.useEffect(() => { api.phylogeny().then(setGraph).catch(() => {}); }, []);
  React.useEffect(() => { if (selection?.style) setSel(selection.style); }, [selection?.style]);
  React.useEffect(() => {
    api.style(sel, 'summary').then(setSelInfo).catch(() => setSelInfo(null));
  }, [sel]);
  React.useEffect(() => {
    if (!compare) { setCmpData(null); return; }
    api.compareStyles(sel, compare).then(setCmpData).catch(() => setCmpData(null));
  }, [sel, compare]);

  const derived = React.useMemo(() => {
    if (!graph) return null;
    const byId = {};
    graph.taxa.forEach((t) => { byId[t.id] = t; });
    const traditionOf = (id, depth = 0) => {
      const n = byId[id];
      if (!n || depth > 8) return null;
      if (n.rank === 'tradition') return n.id;
      return traditionOf(n.member_of, depth + 1);
    };
    const rows = graph.taxa.map((t) => ({
      ...t,
      from: t.floruit_start ?? t.origin ?? 1800,
      to: t.floruit_end ?? t.decline_end ?? (t.floruit_start ?? 1800) + 60,
      tradition: traditionOf(t.id),
    })).sort((a, b) => a.from - b.from || a.id.localeCompare(b.id));
    const index = {};
    rows.forEach((r, i) => { index[r.id] = i; });
    return { rows, index, byId };
  }, [graph]);

  if (!derived) {
    return <div style={{ padding: 24, font: 'var(--type-body)', color: 'var(--ink-3)' }}>reading the graph…</div>;
  }

  const { rows: allRows, index } = derived;
  const rows = rankFilter ? allRows.filter((r) => r.rank === rankFilter || r.id === sel) : allRows;
  const rowIndex = {};
  rows.forEach((r, i) => { rowIndex[r.id] = i; });

  const ancestors = {}, descendants = {};
  {
    const up = (id, depth) => {
      graph.edges.filter((e) => e.from === id).forEach((e) => {
        if (!ancestors[e.to] && depth < 9) { ancestors[e.to] = e.type; up(e.to, depth + 1); }
      });
    };
    const down = (id, depth) => {
      graph.edges.filter((e) => e.to === id).forEach((e) => {
        if (!descendants[e.from] && depth < 9) { descendants[e.from] = e.type; down(e.from, depth + 1); }
      });
    };
    up(sel, 0); down(sel, 0);
  }
  const lit = (id) => id === sel || id === compare || ancestors[id] || descendants[id];
  const edges = graph.edges.filter((e) => {
    if (!showClaims && !CARRIES[e.type]) return false;
    return lit(e.from) && lit(e.to) && rowIndex[e.from] != null && rowIndex[e.to] != null;
  });

  const ROW = 20, PAD = 8;
  const H = rows.length * ROW + PAD * 2;
  const selNode = allRows[index[sel]];
  const cmpNode = compare ? allRows[index[compare]] : null;
  const summary = selInfo?.summary || {};

  const pick = (ev, id) => {
    if (ev.shiftKey) setCompare(id === compare ? null : id);
    else setSel(id);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: 0, flex: 1 }}>
      <FilterStrip right={
        <span style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <Chip on={showClaims} onClick={() => setShowClaims(!showClaims)}>show claimed ancestry</Chip>
          {compare
            ? <Chip on onClick={() => setCompare(null)}>comparing {compare} ×</Chip>
            : <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)' }}>shift-click a second taxon to compare</span>}
        </span>
      }>
        <Eyebrow as="span">rank</Eyebrow>
        {['tradition', 'family', 'style', 'variant'].map((r) => (
          <Chip key={r} on={rankFilter === r} onClick={() => setRankFilter(rankFilter === r ? null : r)}>{r}</Chip>
        ))}
        <span style={{ width: 1, height: 18, background: 'var(--rule)' }} />
        <Eyebrow as="span">traditions</Eyebrow>
        {Object.entries(TRADITION_HUES).map(([id, hue]) => (
          <span key={id} title={id} style={{ width: 10, height: 10, background: hue, flex: 'none' }} />
        ))}
      </FilterStrip>

      <div style={{ flex: 1, display: 'flex', minHeight: 0 }}>
        <div style={{ flex: 1, overflow: 'auto', minHeight: 0, padding: '14px 18px 26px' }}>
          <div style={{ position: 'relative', height: 26, marginLeft: 210, marginBottom: 4 }}>
            {[-700, 1600, 1700, 1800, 1900, 2000].map((y) => (
              <span key={y} style={{ position: 'absolute', left: tScale(y) * 100 + '%', top: 0,
                transform: 'translateX(-50%)', font: 'var(--type-data-s)', color: 'var(--ink-4)' }}>
                {y < 0 ? Math.abs(y) + ' BC' : y}
              </span>
            ))}
            <span style={{ position: 'absolute', left: BREAK_FRAC * 100 + '%', top: 16, bottom: -6,
              width: 0, borderLeft: '1px dashed var(--rule)' }} />
            <span style={{ position: 'absolute', left: BREAK_FRAC * 100 + '%', top: 15,
              transform: 'translate(-50%,0)', font: 'var(--type-data-s)', color: 'var(--gilt-deep)' }}>‖</span>
          </div>
          <div style={{ marginLeft: 210, display: 'flex', justifyContent: 'space-between', marginBottom: 10 }}>
            <Eyebrow tone="quiet" as="span" style={{ whiteSpace: 'nowrap' }}>compressed · 700 BC–1600</Eyebrow>
            <Eyebrow tone="quiet" as="span" style={{ whiteSpace: 'nowrap' }}>expanded · 1600–2026</Eyebrow>
          </div>

          <div style={{ position: 'relative', height: H }}>
            <svg style={{ position: 'absolute', left: 210, right: 0, top: 0, height: H, width: 'calc(100% - 210px)' }}
              preserveAspectRatio="none" viewBox={'0 0 1000 ' + H}>
              {edges.map((e, i) => {
                const a = rows[rowIndex[e.from]], b = rows[rowIndex[e.to]];
                if (!a || !b) return null;
                const x1 = tScale(a.from) * 1000, y1 = rowIndex[e.from] * ROW + PAD + ROW / 2;
                const x2 = tScale(b.to) * 1000, y2 = rowIndex[e.to] * ROW + PAD + ROW / 2;
                const carries = !!CARRIES[e.type];
                const mx = (x1 + x2) / 2;
                return (
                  <path key={i} d={`M${x2} ${y2} C ${mx} ${y2}, ${mx} ${y1}, ${x1} ${y1}`}
                    fill="none" stroke={carries ? 'var(--edge-carries)' : 'var(--edge-claims)'}
                    strokeWidth={carries ? 1.6 : 0.8} strokeDasharray={carries ? 'none' : '3 3'}
                    vectorEffect="non-scaling-stroke" opacity={carries ? 0.8 : 0.65} />
                );
              })}
            </svg>

            {rows.map((r, i) => {
              const on = r.id === sel, cmp = r.id === compare;
              const isLit = lit(r.id);
              const hue = TRADITION_HUES[r.tradition] || 'var(--ink-4)';
              const left = tScale(r.from) * 100, right = tScale(Math.min(r.to, 2026)) * 100;
              return (
                <div key={r.id} style={{ position: 'absolute', left: 0, right: 0, top: i * ROW + PAD, height: ROW }}>
                  <button type="button" onClick={(ev) => { pick(ev, r.id); if (!ev.shiftKey && onCite) onCite('style:' + r.id); }}
                    style={{ position: 'absolute', left: RANK_INDENT[r.rank] || 0,
                      width: 200 - (RANK_INDENT[r.rank] || 0),
                      textAlign: 'left', height: ROW, display: 'flex', alignItems: 'center', gap: 6 }}>
                    <span style={{ font: (on || cmp ? 'var(--fw-med)' : 'var(--fw-reg)') + ' 12px/1.2 var(--display)',
                      color: on ? 'var(--ink)' : (isLit ? 'var(--ink-2)' : 'var(--ink-4)'),
                      whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{r.name}</span>
                    {r.confidence && r.confidence !== 'high' && (
                      <span title={'confidence: ' + r.confidence}
                        style={{ width: 7, height: 7, flex: 'none', border: '1px solid var(--ink-4)',
                          backgroundImage: r.confidence === 'low' ? 'var(--hatch-unjudged)' : 'none' }} />
                    )}
                  </button>
                  <div style={{ position: 'absolute', left: 210, right: 0, top: 0, height: ROW }}>
                    <button type="button" onClick={(ev) => pick(ev, r.id)}
                      title={`${r.name} · ${r.rank} · ${yr(r.from)}–${yr(r.to)}`}
                      style={{ position: 'absolute', left: left + '%', width: Math.max(right - left, 0.7) + '%',
                        top: 6, height: 8, background: hue, opacity: on || cmp ? 1 : (isLit ? 0.7 : 0.26),
                        border: on || cmp ? '1px solid var(--ink)' : 'none', transition: 'var(--t-finding)' }} />
                  </div>
                </div>
              );
            })}
          </div>

          <div style={{ marginLeft: 210, marginTop: 18, border: '1px solid var(--rule)',
            color: 'var(--ink-4)', backgroundImage: 'var(--hatch-45)', padding: '14px 16px' }}>
            <div style={{ background: 'var(--paper)', display: 'inline-block', padding: '4px 8px' }}>
              <Eyebrow tone="secondary" as="span">acknowledged missing peer trunks</Eyebrow>
              <p style={{ font: 'var(--fw-reg) 12.5px/1.55 var(--body)', color: 'var(--ink-3)', margin: '6px 0 0',
                maxWidth: '68ch' }}>
                Japanese, Islamic, South Asian and African traditions are absent. The schema extends to
                them without modification, and one node — <span style={{ fontFamily: 'var(--mono)' }}>cape-dutch</span> —
                already points at an ancestor the graph cannot name.
              </p>
            </div>
          </div>
        </div>

        <div style={{ width: 320, flex: 'none', borderLeft: '1px solid var(--rule)', overflow: 'auto',
          minHeight: 0, padding: '16px 14px 24px', background: 'var(--paper)' }}>
          {selNode && (
            <>
              <Eyebrow>{selNode.rank}</Eyebrow>
              <h3 style={{ font: 'var(--fw-reg) var(--fs-d3)/1.12 var(--display)', fontVariationSettings: '"opsz" 48',
                letterSpacing: 'var(--tr-display)', margin: '6px 0 3px' }}>{selNode.name}</h3>
              <div style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)' }}>
                {selNode.id} · {yr(selNode.from)}–{yr(selNode.to)}
                {selNode.confidence ? ` · confidence ${selNode.confidence}` : ''}
              </div>
              {selNode.short && (
                <p style={{ font: 'var(--fw-reg) 13px/1.6 var(--body)', color: 'var(--ink-2)', margin: '11px 0 0' }}>
                  {selNode.short}
                </p>
              )}
              {summary.regions && (
                <div style={{ font: 'var(--type-data-s)', color: 'var(--ink-3)', marginTop: 8 }}>
                  {(summary.regions || []).join(' · ')}
                </div>
              )}

              {cmpNode && (
                <div style={{ marginTop: 14, padding: '10px 11px', border: '1px solid var(--rule)',
                  background: 'var(--paper-deep)' }}>
                  <Eyebrow tone="accent">distinguished from</Eyebrow>
                  <div style={{ font: 'var(--fw-reg) 14px/1.2 var(--display)', margin: '5px 0 6px' }}>{cmpNode.name}</div>
                  {Array.isArray(cmpData?.explicit_disambiguation) && cmpData.explicit_disambiguation.length > 0
                    ? cmpData.explicit_disambiguation.map((d, i) => (
                        <p key={i} style={{ font: 'var(--fw-reg) 12.5px/1.55 var(--body)', color: 'var(--ink-2)',
                          margin: '0 0 7px' }}>{d.tell || d.note || JSON.stringify(d)}</p>
                      ))
                    : (
                      <>
                        <p style={{ font: 'var(--fw-reg) 12.5px/1.5 var(--body)', color: 'var(--ink-3)', margin: '0 0 6px' }}>
                          No explicit disambiguation recorded — fall back on the tells:
                        </p>
                        {(cmpData?.tells_a || []).slice(0, 2).map((t, i) => (
                          <p key={'a' + i} style={{ font: 'var(--fw-reg) 12.5px/1.5 var(--body)',
                            color: 'var(--ink-2)', margin: '0 0 5px' }}>
                            <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)' }}>{sel} · </span>
                            {typeof t === 'string' ? t : t.tell || t.statement}
                          </p>
                        ))}
                        {(cmpData?.tells_b || []).slice(0, 2).map((t, i) => (
                          <p key={'b' + i} style={{ font: 'var(--fw-reg) 12.5px/1.5 var(--body)',
                            color: 'var(--ink-2)', margin: '0 0 5px' }}>
                            <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)' }}>{compare} · </span>
                            {typeof t === 'string' ? t : t.tell || t.statement}
                          </p>
                        ))}
                      </>
                    )}
                  {cmpData?.shared_ancestry?.length > 0 && (
                    <div style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)', marginTop: 6 }}>
                      shared ancestry · {cmpData.shared_ancestry.slice(0, 4).join(', ')}
                      {cmpData.shared_ancestry.length > 4 ? '…' : ''}
                    </div>
                  )}
                </div>
              )}

              <div style={{ marginTop: 18 }}>
                <Eyebrow style={{ marginBottom: 8 }}>lineage · carries the cascade</Eyebrow>
                {graph.edges.filter((e) => e.from === sel && CARRIES[e.type]).map((e, i) => (
                  <div key={i} style={{ marginBottom: 11 }}>
                    <EdgeGlyph type={e.type} width={44} to={e.to} note={e.note} />
                  </div>
                ))}
              </div>
              <div style={{ marginTop: 12 }}>
                <Eyebrow style={{ marginBottom: 8 }}>lineage · claims only</Eyebrow>
                {graph.edges.filter((e) => e.from === sel && !CARRIES[e.type]).map((e, i) => (
                  <div key={i} style={{ marginBottom: 11 }}>
                    <EdgeGlyph type={e.type} width={44} to={e.to} note={e.note} />
                  </div>
                ))}
                {graph.edges.filter((e) => e.from === sel && !CARRIES[e.type]).length === 0 && (
                  <p style={{ font: 'var(--fw-reg) 12.5px/1.5 var(--body)', color: 'var(--ink-4)', margin: 0 }}>
                    None recorded.
                  </p>
                )}
              </div>

              <div style={{ marginTop: 16, paddingTop: 14, borderTop: '1px solid var(--rule)' }}>
                <Eyebrow style={{ marginBottom: 7 }}>descent</Eyebrow>
                {graph.edges.filter((e) => e.to === sel).map((e, i) => (
                  <button key={i} type="button" onClick={() => setSel(e.from)}
                    style={{ display: 'block', font: 'var(--type-data-s)', textAlign: 'left',
                      color: CARRIES[e.type] ? 'var(--ink-2)' : 'var(--ink-4)', padding: '2px 0' }}>
                    {e.from} <span style={{ color: 'var(--ink-4)' }}>· {e.type}</span>
                  </button>
                ))}
                {graph.edges.filter((e) => e.to === sel).length === 0 && (
                  <p style={{ font: 'var(--fw-reg) 12.5px/1.5 var(--body)', color: 'var(--ink-4)', margin: 0 }}>
                    Nothing descends from this node in the corpus.
                  </p>
                )}
              </div>

              <button type="button" onClick={() => onCite && onCite('kit:' + sel)}
                style={{ marginTop: 16, font: 'var(--type-data-s)', color: 'var(--gilt-deep)',
                  borderBottom: '1px solid var(--link-underline)' }}>
                resolve this style's kit →
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
