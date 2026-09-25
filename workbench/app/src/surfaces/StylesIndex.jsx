/* The Styles index — `#/style` (WP-14.12, PRD §E.2, §I.7).

   An outline to recognise a style by: every tradition, family, style and variant, each filed
   under its own parent (`styles/styleTree.js`, which walks `member_of` and lists an orphan rather
   than dropping it), traditions in the order `/api/overview` serves them, siblings by floruit.
   The Phylogeny indents by rank and sorts by date, which put 111 of 159 rows under a row that was
   not their parent; here each row's nearest shallower row IS its parent, by construction.

   IT NEVER SHOWS A RECORD. It is what a bare `#/style` is, and a bare `#/style` must open the
   same page for everybody who follows the link. What this browser last read in full is OFFERED,
   as a link, from `state/prefs.js`'s `styleInHand`, and never applied: the store only offers.

   `?q=` narrows the outline and keeps each match's filing chain above it, so a matched variant is
   still read under its style and family. Rows are `RecordLink`s, which navigate by citation and so
   drop this page's `q` rather than carrying it into the dossier as a kit filter (PRD §E.4). */
import React from 'react';
import { api } from '../api/client.js';
import { prefs } from '../state/prefs.js';
import { useSurfaceFilters } from '../filters/useFilters.js';
import { useGlossary } from '../api/useGlossary.js';
import { termView } from '../glossary/termView.js';
import { styleTree, traditionOrderOf } from '../styles/styleTree.js';
import { TRADITION_HUES, memberChain } from '../styles/taxa.js';
import { matches } from '../search/match.js';
import { Term } from '../components/Term.jsx';
import { RecordLink } from '../components/RecordLink.jsx';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { FilterInput } from '../components/FilterInput.jsx';
import { FilterStrip } from '../Chrome.jsx';

const SPEC = { q: { type: 'text' } };

function RankWord({ rank }) {
  const glossary = useGlossary();
  const v = termView(glossary, { field: 'style.rank', value: rank });
  if (v.state === 'ready') return <>{v.word}</>;
  return v.state === 'loading' ? null : <>{v.text}</>;
}

export function StylesIndex() {
  const [taxa, setTaxa] = React.useState(null);
  const [order, setOrder] = React.useState(null);
  const [failed, setFailed] = React.useState(false);
  const filters = useSurfaceFilters(SPEC);
  const q = filters.values.q || '';
  const inHand = React.useSyncExternalStore(prefs.subscribe, () => prefs.get().styleInHand);

  React.useEffect(() => {
    Promise.all([api.phylogeny(), api.overview()])
      .then(([p, o]) => { setTaxa(p.taxa || []); setOrder(traditionOrderOf(o)); })
      .catch(() => setFailed(true));
  }, []);

  const byId = React.useMemo(() => new Map((taxa || []).map((t) => [t.id, t])), [taxa]);
  const tree = React.useMemo(() => (taxa && order ? styleTree(taxa, order) : null), [taxa, order]);

  const keep = React.useMemo(() => {
    if (!tree || !q.trim()) return null;
    const out = new Set();
    for (const r of tree.rows) {
      const t = byId.get(r.id);
      if (t && matches(t, q, ['name', 'id'])) {
        out.add(r.id);
        memberChain(r.id, byId).forEach((a) => out.add(a));
      }
    }
    return out;
  }, [tree, q, byId]);

  const rows = tree ? tree.rows.filter((r) => !keep || keep.has(r.id)) : [];
  const handed = inHand && byId.get(inHand);

  return (
    <div data-styles-index="" style={{ display: 'flex', flexDirection: 'column', minHeight: 0, flex: 1 }}>
      <FilterStrip filters={filters} right={
        <span data-index-shown={tree ? rows.length : undefined} data-index-total={tree ? tree.rows.length : undefined}
          style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)' }}>
          {tree ? `${rows.length} of ${tree.rows.length}` : '…'}
        </span>
      }>
        <Eyebrow as="span"><Term id="surface-style" /></Eyebrow>
        <FilterInput value={q} onChange={(v) => filters.set('q', v)} count={tree ? rows.length : undefined}
          label="Filter the styles by name or id" placeholder="filter styles" width={200} />
        {handed && (
          <span data-style-in-hand={inHand} style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)', whiteSpace: 'nowrap' }}>
            last read · <RecordLink cite={'style:' + inHand}>{handed.name || inHand}</RecordLink>
          </span>
        )}
      </FilterStrip>

      <div style={{ flex: 1, overflow: 'auto', minHeight: 0, padding: '16px 26px 40px' }}>
        {failed && <p style={{ font: 'var(--type-body)', color: 'var(--ink-2)' }}>The styles could not be read.</p>}
        {!tree && !failed && <p style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)' }}>reading the styles…</p>}
        {tree && (
          <div role="tree" aria-label="the styles, filed">
            {rows.map((r) => {
              const t = byId.get(r.id) || {};
              const hue = r.depth === 0 ? TRADITION_HUES[r.id] : null;
              return (
                <div key={r.id} role="treeitem" aria-level={r.depth + 1} data-style-row={r.id} data-depth={r.depth}
                  style={{ display: 'flex', alignItems: 'baseline', gap: 10, padding: r.depth === 0 ? '12px 0 4px' : '2px 0',
                    paddingLeft: r.depth * 20,
                    borderTop: r.depth === 0 ? '1px solid var(--rule)' : 'none' }}>
                  {hue && <span aria-hidden="true" style={{ width: 10, height: 10, background: hue, flex: 'none', alignSelf: 'center' }} />}
                  <span style={{ font: r.depth === 0 ? 'var(--fw-reg) 17px/1.3 var(--display)' : 'var(--fw-reg) 14px/1.45 var(--serif)' }}>
                    <RecordLink cite={'style:' + r.id}>{t.name || r.id}</RecordLink>
                  </span>
                  <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)' }}>
                    {r.rank ? <RankWord rank={r.rank} /> : null}
                    {t.floruit_start != null ? ` · ${t.floruit_start}` : ''}
                  </span>
                </div>
              );
            })}
            {tree.orphans.length > 0 && (
              <div data-orphans={tree.orphans.length} style={{ marginTop: 22, paddingTop: 10, borderTop: '1px solid var(--rule)' }}>
                <Eyebrow style={{ marginBottom: 6 }}>filed under nothing this outline reaches · {tree.orphans.length}</Eyebrow>
                {tree.orphans.map((id) => (
                  <div key={id} data-style-row={id} data-orphan="" style={{ padding: '2px 0' }}>
                    <RecordLink cite={'style:' + id} />
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
