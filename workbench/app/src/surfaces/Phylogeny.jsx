/* Surface ② — the Phylogeny, live. 164 taxa on a broken time axis (nearly all the
   density sits in 1600–2026; the classical tail is compressed and the break is drawn,
   not implied). Both hierarchies at once: rank as indent (browsing only), lineage as
   edges — cascade-carrying edges structurally heavier than claimed ancestry. Select
   two to compare, and the comparison shows the corpus's real tells. */
import React from 'react';
import { api } from '../api/client.js';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { EdgeGlyph } from '../components/EdgeGlyph.jsx';
import { nav } from '../state/nav.js';
import { Spotlight } from '../components/Spotlight.jsx';
import { FilterStrip, Chip, ChipGroup, PaneStub, FoldControl, ActionChip } from '../Chrome.jsx';
import { Splitter } from '../components/Splitter.jsx';
import { layout } from '../state/layout.js';
import { FilterInput } from '../components/FilterInput.jsx';
import { useSurfaceFilters } from '../filters/useFilters.js';
import { matches } from '../search/match.js';
import { MapView } from './phylo/MapView.jsx';

const DEFAULT_TAXON = 'tidewater-georgian';
const EMPTY = [];

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

const PHYLO_SPEC = { view: { widens: true }, rank: {}, q: { type: 'text' }, claims: { type: 'bool' } };

export function Phylogeny({ onCite, selection, setSelection, full, onFull, onExitFull }) {
  const [graph, setGraph] = React.useState(null);
  const [sel, setSel] = React.useState(selection?.style || DEFAULT_TAXON);
  const [compare, setCompare] = React.useState(null);
  const [cmpData, setCmpData] = React.useState(null);
  const [selInfo, setSelInfo] = React.useState(null);

  const filters = useSurfaceFilters(PHYLO_SPEC);
  /* The record beside the drawing pulls too. It is 320px of prose against a map whose
     whole errand is extent, and on a laptop that was the difference between seeing both
     coasts of the Atlantic and seeing one. In full screen it is gone entirely: the atlas
     asked for the window, and leaving a third of it as a panel would be answering a
     different question. */
  const panel = React.useSyncExternalStore(layout.subscribe, () => layout.width('phylo'));
  const panelOpen = React.useSyncExternalStore(layout.subscribe, () => layout.isOpen('phylo'));
  const isMap = filters.values.view === 'map';
  const rankFilter = filters.values.rank;
  const q = filters.values.q;
  // Claimed ancestry shows by default; the URL carries the deliberate act of hiding it.
  const showClaims = !filters.values.claims;

  React.useEffect(() => { api.phylogeny().then(setGraph).catch(() => {}); }, []);
  /* The URL owns this, so an ABSENT selection must reset to the default rather than leave the
   last one showing. Guarding the sync with `if (selection?.x)` meant pressing Back to a bare
   #/phylogeny left the panel displaying the record you had just left — the address bar and the
   screen disagreeing, which is the one thing the router exists to prevent. Found by an
   adversarial audit. */
  React.useEffect(() => { setSel(selection?.style || DEFAULT_TAXON); }, [selection?.style]);
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

  /* MEMOISED, and the map is why. MapView guards its whole placement pass with
     useMemo([rows]) — reference identity — so building `rows` fresh during every render made
     that guard a no-op: every keystroke in the filter box, every chip, every hover-driven
     re-render re-placed all 164 styles. An adversarial audit measured the pass at 17.9 ms and
     the memo at zero effect. The same applies to `edges` below.

     ABOVE the `if (!derived)` return, and it has to be: hooks may not run conditionally, and
     putting these after the early return changed the hook count between the loading render
     and the loaded one — React error #310, a blank surface. */
  const allRows = derived ? derived.rows : EMPTY;
  const rows = React.useMemo(() => allRows.filter((r) => (
    (!rankFilter || r.rank === rankFilter || r.id === sel)
    // The selected taxon always survives a filter: hiding the thing you are reading
    // about, and its detail panel with it, is not filtering, it is losing your place.
    && (r.id === sel || matches(r, q, ['name', 'id', 'rank', 'regions', 'short']))
  )), [allRows, rankFilter, sel, q]);
  const rowIndex = React.useMemo(() => {
    const ix = {};
    rows.forEach((r, i) => { ix[r.id] = i; });
    return ix;
  }, [rows]);
  const graphEdges = derived ? graph.edges : EMPTY;

  if (!derived) {
    return <div style={{ padding: 24, font: 'var(--type-body)', color: 'var(--ink-3)' }}>reading the graph…</div>;
  }

  const { index } = derived;

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
    // Selecting writes the URL, so a taxon — in either reading — is a link.
    else { setSel(id); setSelection && setSelection({ style: id }); }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: 0, flex: 1 }}>
      <Spotlight kind="massing" id={selection?.massing}
        note="a massing from the catalogue — a style's affinities for it are listed on its full record"
        onDismiss={() => nav.select({ massing: null })} />
      <FilterStrip filters={filters} right={
        <span style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          {/* THE WAY OUT LIVES HERE, not only in the atlas's legend.

              It was only in `MapView`, and the FilterStrip is rendered in full screen —
              so entering full screen on the map and then pressing the `tree` chip
              unmounted MapView, taking the one visible exit with it, and left a
              chrome-less shell whose only escape was a key nobody had been told about.
              Two adversarial auditors found it independently. The strip survives both
              readings, so the control belongs to the strip. */}
          {full && (
            <ActionChip affix={null} onClick={onExitFull}
              title="Give the instrument back — or press escape">
              ⤡ leave full screen · esc
            </ActionChip>
          )}
          <Chip on={showClaims} onClick={() => filters.set('claims', showClaims)}>
            show claimed ancestry
          </Chip>
          {compare
            ? <Chip on onClick={() => setCompare(null)}>comparing {compare} ×</Chip>
            : <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)' }}>shift-click a second taxon to compare</span>}
        </span>
      }>
        {/* Two readings of one graph. Which one you are looking at is part of the
            address, so a map view can be linked to. */}
        <ChipGroup label="reading">
          <Chip radio on={!isMap} onClick={() => filters.set('view', null)}
            title="Descent against time">tree</Chip>
          <Chip radio on={isMap} onClick={() => filters.set('view', 'map')}
            title="Where each style arose, and where its lineage travelled">map</Chip>
        </ChipGroup>
        <span style={{ width: 1, height: 18, background: 'var(--rule)' }} />
        <FilterInput value={q} onChange={(v) => filters.set('q', v)} count={rows.length}
          label="Filter the taxa by name, rank or region" placeholder="filter 164 taxa" width={165} />
        <span style={{ width: 1, height: 18, background: 'var(--rule)' }} />
        <ChipGroup label="rank">
          <Eyebrow as="span">rank</Eyebrow>
          {['tradition', 'family', 'style', 'variant'].map((r) => (
            <Chip key={r} radio on={rankFilter === r}
              onClick={() => filters.toggle('rank', r)}>{r}</Chip>
          ))}
        </ChipGroup>
        <span style={{ width: 1, height: 18, background: 'var(--rule)' }} />
        <Eyebrow as="span">traditions</Eyebrow>
        {Object.entries(TRADITION_HUES).map(([id, hue]) => (
          <span key={id} title={id} style={{ width: 10, height: 10, background: hue, flex: 'none' }} />
        ))}
      </FilterStrip>

      <div style={{ flex: 1, display: 'flex', minHeight: 0 }}>
        {isMap ? (
          /* The same edge set the tree draws — already narrowed by `showClaims` and lit to
             the selection's ancestry and descent. Drawing all 476 at once would be a ball
             of wool, and the two readings should agree about what is on screen. */
          <MapView rows={rows} edges={edges} sel={sel} compare={compare} onPick={pick}
            traditionHue={(r) => TRADITION_HUES[r.tradition] || 'var(--ink-4)'}
            lit={lit} carries={CARRIES} showClaims={showClaims} rankFilter={rankFilter}
            full={!!full} onExitFull={onExitFull}
            onFull={onFull ? () => onFull('phylogeny') : undefined} />
        ) : (
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
                  <button type="button" onClick={(ev) => pick(ev, r.id)}
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
        )}

        {!full && panelOpen && <Splitter pane="phylo" grows="right" />}
        {!full && panelOpen && (
        <div style={{ width: panel, flex: 'none', borderLeft: '1px solid var(--rule)',
          minHeight: 0, background: 'var(--paper)', display: 'flex', flexDirection: 'column' }}>
        <div style={{ flex: 'none', height: 24, display: 'flex', alignItems: 'center',
          justifyContent: 'flex-end' }}>
          <FoldControl pane="phylo" label="the taxon's record" side="right" />
        </div>
        <div style={{ flex: 1, overflow: 'auto', minHeight: 0, padding: '2px 14px 24px' }}>
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

              <button type="button" onClick={() => onCite && onCite('style:' + sel)}
                style={{ marginTop: 16, marginRight: 16, font: 'var(--type-data-s)', color: 'var(--gilt-deep)',
                  borderBottom: '1px solid var(--link-underline)' }}>
                full record →
              </button>
              <button type="button" onClick={() => onCite && onCite('kit:' + sel)}
                style={{ marginTop: 16, font: 'var(--type-data-s)', color: 'var(--gilt-deep)',
                  borderBottom: '1px solid var(--link-underline)' }}>
                resolve this style's kit →
              </button>
            </>
          )}
        </div>
        </div>
        )}
        {/* Folded, the record is a spine rather than nothing: a pull past the floor is a
            request to fold, and a fold with no visible way back is a trapdoor. */}
        {!full && !panelOpen && (
          <PaneStub pane="phylo" label="the taxon's record" spine="the record" side="right" />
        )}
      </div>
    </div>
  );
}
