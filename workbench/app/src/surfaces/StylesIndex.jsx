/* The Styles index — `#/style` (WP-14.12, PRD §E.2, §I.7).

   An outline to recognise a style by: every tradition, family, style and variant, each filed
   under its own parent (`styles/styleTree.js`, which walks `member_of` and lists an orphan rather
   than dropping it), traditions in the order `/api/overview` serves them, siblings by floruit.
   The Phylogeny indents by rank and sorts by date, which put 111 of 159 rows under a row that was
   not their parent; here each row's nearest shallower row IS its parent, by construction.

   SET AS CHAPTERS SINCE 26 NOV 2026 (the two rooms). The outline was one indented column, a
   hundred and sixty rows down a single margin, each trailed by its id, its rank and a year. It is
   five chapters now, one a tradition, and under each its families set in columns the way an index
   is set in a book: a family's name over the styles filed under it, a variant indented under its
   style, the year a floruit begins at the row's end. The filing is unchanged and so is every
   row's level; the page leads with its own record's line (`PageHero`).

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
import { chaptersOf } from '../styles/chapters.js';
import { TRADITION_HUES, memberChain } from '../styles/taxa.js';
import { matches } from '../search/match.js';
import { RecordLink } from '../components/RecordLink.jsx';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { FilterInput } from '../components/FilterInput.jsx';
import { PageHero } from '../components/PageHead.jsx';

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

  // the outline as chapters and blocks: `styles/chapters.js`, which returns every row exactly once
  const chapters = chaptersOf(rows);
  const year = (id) => { const t = byId.get(id); return t && t.floruit_start != null ? t.floruit_start : null; };
  const Row = ({ r, className, level }) => (
    <div role="treeitem" aria-level={r.depth + 1} data-style-row={r.id} data-depth={level != null ? level : r.depth}
      data-rank={r.rank || undefined} className={className}>
      <RecordLink cite={'style:' + r.id}>{(byId.get(r.id) || {}).name || r.id}</RecordLink>
      {year(r.id) != null && <span className="tdl-year">{year(r.id)}</span>}
    </div>
  );

  return (
    <div data-styles-index="" className="tdl-scroll">
      <div className="tdl-page tdl-page-wide">
        <PageHero termId="surface-style" className="tdl-rise">
          <div className="tdl-hero-acts">
            <FilterInput value={q} onChange={(v) => filters.set('q', v)} count={tree ? rows.length : undefined}
              label="Filter the styles by name or id" placeholder="filter styles" width={300} large />
            <span data-index-shown={tree ? rows.length : undefined} data-index-total={tree ? tree.rows.length : undefined}
              style={{ font: 'var(--type-data-s)', color: 'var(--text-secondary)' }}>
              {tree ? `${rows.length} of ${tree.rows.length}` : '…'}
            </span>
            {filters.activeCount > 0 && (
              <button type="button" onClick={filters.clear} className="tdl-link" style={{ font: 'var(--type-data-s)' }}>clear</button>
            )}
            <span style={{ flex: 1 }} />
            {handed && (
              <span data-style-in-hand={inHand} className="tdl-quiet-link" style={{ color: 'var(--text-secondary)' }}>
                last read · <RecordLink cite={'style:' + inHand}>{handed.name || inHand}</RecordLink>
              </span>
            )}
          </div>
        </PageHero>

        {failed && <p style={{ font: 'var(--type-body)', color: 'var(--text-secondary)' }}>The styles could not be read.</p>}
        {!tree && !failed && <p style={{ font: 'var(--type-data-s)', color: 'var(--text-secondary)' }}>reading the styles…</p>}
        {tree && (
          <div role="tree" aria-label="the styles, filed" className="tdl-rise-2">
            {chapters.map((ch) => {
              const hue = ch.head ? TRADITION_HUES[ch.head.id] : null;
              return (
                <section key={ch.head ? ch.head.id : ch.blocks[0].head.id} className="tdl-tradition"
                  data-tradition-chapter={ch.head ? ch.head.id : ''}>
                  {ch.head && (
                    <div role="treeitem" aria-level={1} data-style-row={ch.head.id} data-depth={0} className="tdl-tradition-head">
                      {hue && <span aria-hidden="true" className="tdl-tradition-swatch" style={{ background: hue }} />}
                      <h2 className="tdl-tradition-name">
                        <RecordLink cite={'style:' + ch.head.id}>{(byId.get(ch.head.id) || {}).name || ch.head.id}</RecordLink>
                      </h2>
                      <span className="tdl-year">
                        {ch.head.rank ? <RankWord rank={ch.head.rank} /> : null}
                        {year(ch.head.id) != null ? ` · ${year(ch.head.id)}` : ''}
                      </span>
                    </div>
                  )}
                  <div className="tdl-families">
                    {ch.blocks.map((b) => (
                      <div key={b.head.id} className="tdl-family">
                        <Row r={b.head} className="tdl-family-name" />
                        {b.rows.map((r) => (
                          <Row key={r.id} r={r} className="tdl-style-row" level={r.depth} />
                        ))}
                      </div>
                    ))}
                  </div>
                </section>
              );
            })}
            {tree.orphans.length > 0 && (
              <div data-orphans={tree.orphans.length} style={{ marginTop: 22, paddingTop: 10, borderTop: '1px solid var(--border-hairline)' }}>
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
