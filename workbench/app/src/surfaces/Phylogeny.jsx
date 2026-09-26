/* Surface ② — the Phylogeny, live. 164 taxa on a broken time axis (nearly all the
   density sits in 1600–2026; the classical tail is compressed and the break is drawn,
   not implied). Both hierarchies at once: filing (`member_of`) as the indent by rank, lineage
   as edges — kit-carrying edges structurally heavier than claimed ancestry. Shift-click a
   second taxon and the two open side by side on the Compare page (`#/compare/<a>/<b>`,
   WP-14.26), which is a place with an address; the side-panel comparison it replaces held the
   pair in component state and printed an entry it did not recognise as JSON.

   WHICH EDGES CARRY THE KIT IS THE SERVER'S FLAG, NOT A TABLE OF TYPES (WP-14.11). This file
   had `CARRIES = { descends_from, regional_of }` and drew, filtered and grouped every edge by it,
   so the 42 `hybridizes_with` edges that carry the kit were drawn light, hidden with the claims,
   and listed under "claims only". Each edge's `inherits_kit` (and `slots`) from `/api/phylogeny`
   decides now, through `lineage/carry.js`; the tradition hues are `styles/taxa.js`'s. */
import React from 'react';
import { api } from '../api/client.js';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { EdgeGlyph } from '../components/EdgeGlyph.jsx';
import { Term } from '../components/Term.jsx';
import { TRADITION_HUES, traditionOf } from '../styles/taxa.js';
import { carriesKit, glyphEdge, filingEdgeOf, groupByCarry } from '../lineage/carry.js';
import { nav } from '../state/nav.js';
import { FilterStrip, Chip, ChipGroup, PaneStub, FoldControl, ActionChip } from '../Chrome.jsx';
import { Splitter } from '../components/Splitter.jsx';
import { layout } from '../state/layout.js';
import { FilterInput } from '../components/FilterInput.jsx';
import { useSurfaceFilters } from '../filters/useFilters.js';
import { matches } from '../search/match.js';
import { MapView } from './phylo/MapView.jsx';
import { MarkGlyph } from '../components/MarkGlyph.jsx';
import { useGlossary } from '../api/useGlossary.js';
import { describeTerm, wordOf } from '../glossary/termView.js';
import { NoRecordChosen } from '../components/NoRecordChosen.jsx';

const EMPTY = [];

const BREAK_AT = 1600, BREAK_FRAC = 0.18;
function tScale(y) {
  if (y <= BREAK_AT) return ((y + 700) / (BREAK_AT + 700)) * BREAK_FRAC;
  return BREAK_FRAC + ((y - BREAK_AT) / (2026 - BREAK_AT)) * (1 - BREAK_FRAC);
}
const RANK_INDENT = { tradition: 0, family: 10, style: 20, variant: 30 };
const yr = (v) => (v == null ? '?' : v < 0 ? Math.abs(v) + ' BC' : String(v));

const PHYLO_SPEC = { view: { widens: true }, rank: {}, q: { type: 'text' }, claims: { type: 'bool' } };

/* The selected taxon's own edges, grouped by what each CARRIES and never by its type: the drawer
   it is filed in first, then the lineage edges that hand the kit down, then those that hand
   nothing down. Each group is omitted when empty, and every word is a glossary record's — the
   heading is the `section-lineage` record, and each glyph names its own carry. `from` is dropped
   because the taxon is the panel's subject. */
function Lineage({ taxon, edges }) {
  const filed = filingEdgeOf(taxon);
  const groups = groupByCarry((edges || []).filter((e) => e.from === taxon.id)
    .map((e) => ({ ...glyphEdge(e), from: null })));
  if (!filed && groups.length === 0) return null;
  return (
    <section data-lineage-of={taxon.id} style={{ marginTop: 18 }}>
      <Eyebrow style={{ marginBottom: 8 }}><Term id="section-lineage" /></Eyebrow>
      {filed && (
        <div data-carry-group="member-of" style={{ marginBottom: 11 }}>
          <EdgeGlyph edge={{ ...filed, from: null }} width={44} />
        </div>
      )}
      {groups.map((g, gi) => (
        <div key={g.carry} data-carry-group={g.carry}
          style={{ marginTop: gi || filed ? 10 : 0, paddingTop: gi || filed ? 10 : 0,
            borderTop: gi || filed ? '1px solid var(--rule-soft)' : 'none' }}>
          {g.edges.map((e, i) => (
            <div key={e.type + ':' + e.target + ':' + i} style={{ marginBottom: 11 }}>
              <EdgeGlyph edge={e} width={44} />
            </div>
          ))}
        </div>
      ))}
    </section>
  );
}

export function Phylogeny({ onCite, selection, setSelection, full, onFull, onExitFull }) {
  const [graph, setGraph] = React.useState(null);
  const [sel, setSel] = React.useState(selection?.style || null);
  const [selInfo, setSelInfo] = React.useState(null);
  // the low-confidence mark's word, its record's (WP-14.29); nothing while the glossary loads
  const glossary = useGlossary();
  const confidenceWord = glossary.status === 'ready' ? wordOf(glossary.lookup, 'mark-low-confidence') : '';

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
  /* The URL owns this, so an ABSENT selection must reset rather than leave the last one showing.
   Guarding the sync with `if (selection?.x)` meant pressing Back to a bare #/phylogeny left the
   panel displaying the record you had just left — the address bar and the screen disagreeing,
   which is the one thing the router exists to prevent. Found by an adversarial audit.
   AND ABSENT MEANS NONE (WP-14.27). It reset to a hard-coded `tidewater-georgian`, so a bare
   #/phylogeny showed one taxon's record under an address that named no taxon -- the default
   record tranche 1 removed from the Styles index and the pack index, surviving here. A bare
   address draws the tree and says no record is chosen, in the words of its glossary record. */
  React.useEffect(() => { setSel(selection?.style || null); }, [selection?.style]);
  React.useEffect(() => {
    if (!sel) { setSelInfo(null); return; }
    api.style(sel, 'summary').then(setSelInfo).catch(() => setSelInfo(null));
  }, [sel]);

  const derived = React.useMemo(() => {
    if (!graph) return null;
    const byId = {};
    graph.taxa.forEach((t) => { byId[t.id] = t; });
    const rows = graph.taxa.map((t) => ({
      ...t,
      from: t.floruit_start ?? t.origin ?? 1800,
      to: t.floruit_end ?? t.decline_end ?? (t.floruit_start ?? 1800) + 60,
      tradition: traditionOf(t.id, byId),
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
    return <div style={{ padding: 24, font: 'var(--type-body)', color: 'var(--ink-2)' }}>reading the graph…</div>;
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
  const lit = (id) => id === sel || ancestors[id] || descendants[id];
  const edges = graph.edges.filter((e) => {
    if (!showClaims && !carriesKit(e)) return false;
    return lit(e.from) && lit(e.to) && rowIndex[e.from] != null && rowIndex[e.to] != null;
  });

  const ROW = 20, PAD = 8;
  // With nothing chosen no lineage is lit, and no row is dimmed for not being part of one.
  const bright = (id) => !sel || lit(id);
  const H = rows.length * ROW + PAD * 2;
  const selNode = allRows[index[sel]];
  const summary = selInfo?.summary || {};

  const pick = (ev, id) => {
    // A second taxon opens the two side by side, at an address (WP-14.26).
    if (ev.shiftKey) { if (id !== sel) nav.go('compare', { style: sel, compare: id }); }
    // Selecting writes the URL, so a taxon — in either reading — is a link.
    else { setSel(id); setSelection && setSelection({ style: id }); }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: 0, flex: 1 }}>
      <FilterStrip wrap filters={filters} right={
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
              title={describeTerm(glossary, 'full-screen').title}>
              ⤡ leave full screen · esc
            </ActionChip>
          )}
          <Chip on={showClaims} onClick={() => filters.set('claims', showClaims)}>
            show claimed ancestry
          </Chip>
          {/* The gesture and what it opens are the `shift-click-to-compare` record's (WP-14.31). */}
          <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)' }}><Term id="shift-click-to-compare" /></span>
        </span>
      }>
        {/* Two readings of one graph. Which one you are looking at is part of the
            address, so a map view can be linked to. */}
        <ChipGroup label="reading">
          <Chip radio on={!isMap} onClick={() => filters.set('view', null)}
            title={describeTerm(glossary, 'reading-tree').title}>tree</Chip>
          <Chip radio on={isMap} onClick={() => filters.set('view', 'map')}
            title={describeTerm(glossary, 'reading-map').title}>map</Chip>
        </ChipGroup>
        <span style={{ width: 1, height: 18, background: 'var(--rule)' }} />
        <FilterInput value={q} onChange={(v) => filters.set('q', v)} count={rows.length}
          label="Filter the taxa by name, rank or region" placeholder={`filter ${allRows.length} taxa`} width={165} />
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
          <MapView rows={rows} edges={edges} sel={sel} onPick={pick}
            traditionHue={(r) => TRADITION_HUES[r.tradition] || 'var(--hair)'}
            lit={bright} showClaims={showClaims} rankFilter={rankFilter}
            full={!!full} onExitFull={onExitFull}
            onFull={onFull ? () => onFull('phylogeny') : undefined} />
        ) : (
        <div style={{ flex: 1, overflow: 'auto', minHeight: 0, padding: '14px 18px 26px' }}>
          <div style={{ position: 'relative', height: 26, marginLeft: 210, marginBottom: 4 }}>
            {[-700, 1600, 1700, 1800, 1900, 2000].map((y) => (
              <span key={y} style={{ position: 'absolute', left: tScale(y) * 100 + '%', top: 0,
                transform: 'translateX(-50%)', font: 'var(--type-data-s)', color: 'var(--ink-2)' }}>
                {y < 0 ? Math.abs(y) + ' BC' : y}
              </span>
            ))}
            <span style={{ position: 'absolute', left: BREAK_FRAC * 100 + '%', top: 16, bottom: -6,
              width: 0, borderLeft: '1px dashed var(--rule)' }} />
            <span style={{ position: 'absolute', left: BREAK_FRAC * 100 + '%', top: 15,
              transform: 'translate(-50%,0)', font: 'var(--type-data-s)', color: 'var(--gilt-deep)' }}>‖</span>
          </div>
          <div style={{ marginLeft: 210, display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap',
            gap: '2px 16px', marginBottom: 10 }}>
            <Eyebrow as="span" style={{ whiteSpace: 'nowrap' }}>compressed · 700 BC–1600</Eyebrow>
            <Eyebrow as="span" style={{ whiteSpace: 'nowrap' }}>expanded · 1600–2026</Eyebrow>
          </div>

          <div style={{ position: 'relative', height: H }}>
            <svg style={{ position: 'absolute', left: 210, right: 0, top: 0, height: H, width: 'calc(100% - 210px)' }}
              preserveAspectRatio="none" viewBox={'0 0 1000 ' + H}>
              {edges.map((e, i) => {
                const a = rows[rowIndex[e.from]], b = rows[rowIndex[e.to]];
                if (!a || !b) return null;
                const x1 = tScale(a.from) * 1000, y1 = rowIndex[e.from] * ROW + PAD + ROW / 2;
                const x2 = tScale(b.to) * 1000, y2 = rowIndex[e.to] * ROW + PAD + ROW / 2;
                const carries = carriesKit(e);
                const mx = (x1 + x2) / 2;
                return (
                  <path key={i} d={`M${x2} ${y2} C ${mx} ${y2}, ${mx} ${y1}, ${x1} ${y1}`}
                    data-edge-from={e.from} data-edge-to={e.to} data-edge-type={e.type}
                    fill="none" stroke={carries ? 'var(--edge-carries)' : 'var(--edge-claims)'}
                    strokeWidth={carries ? 1.6 : 0.8} strokeDasharray={carries ? 'none' : '3 3'}
                    vectorEffect="non-scaling-stroke" opacity={carries ? 0.8 : 0.65} />
                );
              })}
            </svg>

            {rows.map((r, i) => {
              const on = r.id === sel;
              const isLit = bright(r.id);
              const hue = TRADITION_HUES[r.tradition] || 'var(--hair)';
              const left = tScale(r.from) * 100, right = tScale(Math.min(r.to, 2026)) * 100;
              return (
                <div key={r.id} style={{ position: 'absolute', left: 0, right: 0, top: i * ROW + PAD, height: ROW }}>
                  <button type="button" onClick={(ev) => pick(ev, r.id)}
                    style={{ position: 'absolute', left: RANK_INDENT[r.rank] || 0,
                      width: 200 - (RANK_INDENT[r.rank] || 0),
                      textAlign: 'left', height: ROW, display: 'flex', alignItems: 'center', gap: 6 }}>
                    <span style={{ font: (on ? 'var(--fw-med)' : 'var(--fw-reg)') + ' 12px/1.2 var(--display)',
                      color: on || isLit ? 'var(--ink)' : 'var(--ink-2)',
                      whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{r.name}</span>
                    {/* LOW CONFIDENCE IS ONE MARK AND ONE WORD (WP-14.29): a dashed square, the
                        record's word to assistive tech and to the pointer. A medium node is not
                        marked -- medium is the style schema's own default, the unmarked case -- and
                        its square no longer wears the open outline yours-to-judge draws. */}
                    {r.confidence === 'low' && (
                      <span data-low-confidence="" title={confidenceWord}
                        style={{ display: 'inline-flex', flex: 'none' }}>
                        <MarkGlyph token="--mark-low-confidence" size={7} />
                        <span className="tdl-sr-only">{confidenceWord}</span>
                      </span>
                    )}
                  </button>
                  <div style={{ position: 'absolute', left: 210, right: 0, top: 0, height: ROW }}>
                    <button type="button" onClick={(ev) => pick(ev, r.id)}
                      title={`${r.name} · ${r.rank} · ${yr(r.from)}–${yr(r.to)}`}
                      style={{ position: 'absolute', left: left + '%', width: Math.max(right - left, 0.7) + '%',
                        top: 6, height: 8, background: hue, opacity: on ? 1 : (isLit ? 0.7 : 0.26),
                        border: on ? '1px solid var(--ink)' : 'none', transition: 'var(--t-finding)' }} />
                  </div>
                </div>
              );
            })}
          </div>

          <div style={{ marginLeft: 210, marginTop: 18, border: '1px solid var(--rule)',
            color: 'var(--ink-2)', backgroundImage: 'var(--mark-wanted)', padding: '14px 16px' }}>
            <div style={{ background: 'var(--paper)', display: 'inline-block', padding: '4px 8px' }}>
              <Eyebrow tone="secondary" as="span">acknowledged missing peer trunks</Eyebrow>
              <p style={{ font: 'var(--fw-reg) 12.5px/1.55 var(--body)', color: 'var(--ink-2)', margin: '6px 0 0',
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
          {!sel && <NoRecordChosen surface="phylogeny" />}
          {selNode && (
            <>
              <Eyebrow>{selNode.rank}</Eyebrow>
              <h3 data-taxon-record={selNode.id} style={{ font: 'var(--fw-reg) var(--fs-d3)/1.12 var(--display)', fontVariationSettings: '"opsz" 48',
                letterSpacing: 'var(--tr-display)', margin: '6px 0 3px' }}>{selNode.name}</h3>
              <div style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)' }}>
                {selNode.id} · {yr(selNode.from)}–{yr(selNode.to)}
                {selNode.confidence ? ` · confidence ${selNode.confidence}` : ''}
              </div>
              {selNode.short && (
                <p style={{ font: 'var(--fw-reg) 13px/1.6 var(--body)', color: 'var(--ink-2)', margin: '11px 0 0' }}>
                  {selNode.short}
                </p>
              )}
              {summary.regions && (
                <div style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)', marginTop: 8 }}>
                  {(summary.regions || []).join(' · ')}
                </div>
              )}

              <Lineage taxon={selNode} edges={graph.edges} />

              <div style={{ marginTop: 16, paddingTop: 14, borderTop: '1px solid var(--rule)' }}>
                <Eyebrow style={{ marginBottom: 7 }}>descent</Eyebrow>
                {graph.edges.filter((e) => e.to === sel).map((e, i) => (
                  /* A descent is a pick like any other: it writes the address (WP-14.27), so
                     Back returns to the taxon it was reached from and a reload keeps it. */
                  <button key={i} type="button" data-descent={e.from}
                    onClick={() => { setSel(e.from); setSelection && setSelection({ style: e.from }); }}
                    style={{ display: 'block', font: 'var(--type-data-s)', textAlign: 'left',
                      color: carriesKit(e) ? 'var(--ink)' : 'var(--ink-2)', padding: '2px 0' }}>
                    {e.from} <span style={{ color: 'var(--ink-2)' }}>· {e.type}</span>
                  </button>
                ))}
                {graph.edges.filter((e) => e.to === sel).length === 0 && (
                  <p style={{ font: 'var(--fw-reg) 12.5px/1.5 var(--body)', color: 'var(--ink-2)', margin: 0 }}>
                    Nothing descends from this node in the corpus.
                  </p>
                )}
              </div>

              <button type="button" onClick={() => onCite && onCite('style:' + sel)}
                style={{ marginTop: 16, marginRight: 16, font: 'var(--type-data-s)', color: 'var(--link)',
                  borderBottom: '1px solid var(--link-underline)' }}>
                full record →
              </button>
              <button type="button" onClick={() => onCite && onCite('kit:' + sel)}
                style={{ marginTop: 16, font: 'var(--type-data-s)', color: 'var(--link)',
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
