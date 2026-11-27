/* Elements — `#/elements` and `#/elements/<slot>` (WP-14.23, tranche 2 PRD §B.1, §B.4, §C.6).

   THE INDEX is every element slot the ontology names, filed under its slot group in the
   ontology's own order, each with the count of styles whose RESOLVED kit specifies it --
   `GET /api/slots`'s `specified_by`, computed on the server and never typed here. Above the slots,
   the four plan-type kinds, each a link to its own index (`#/massing`, `#/parti`, `#/grouping`,
   `#/room`), because the Elements page is where their record pages stand (the site map's `UNDER`).
   `?q=` narrows the slots by name or id.

   SET AS A BOOK'S INDEX SINCE 27 NOV 2026 (WP-18.1). The page leads with its own record's line
   (`PageHero`), the four plan-type kinds are four cards with their counts, and each slot group is
   a block in columns: a slot's name, and the one figure beside it. Every hook the walk reads is
   where it was.

   A SLOT is `dossier/SlotPanel.jsx`, which tranche 1 built as the interim page for a slot with no
   style and parked under the Styles index; its address there, `#/style/-/kit/<slot>`, is read as
   this one and rewritten (router.js, LEGACY_PLACES). */
import React from 'react';
import { api } from '../api/client.js';
import { formatHash } from '../router.js';
import { useNames } from '../names/useNames.js';
import { useSurfaceFilters } from '../filters/useFilters.js';
import { matches } from '../search/match.js';
import { RECORD_KINDS } from '../record/kinds.js';
import { Term } from '../components/Term.jsx';
import { RecordLink } from '../components/RecordLink.jsx';
import { FilterInput } from '../components/FilterInput.jsx';
import { PageHero, usePageHead } from '../components/PageHead.jsx';
import { SlotPanel } from '../dossier/SlotPanel.jsx';
import { data } from '../record/parts.jsx';

const SPEC = { q: { type: 'text' } };

/* A kind as a way in: its count, its own surface record's word as the link, and that record's
   line about what the page is. Nothing here is written by the app. */
function KindCard({ kind, count }) {
  const { view, what } = usePageHead(`surface-${kind.surface}`);
  const word = view.state === 'ready' ? view.word : view.state === 'loading' ? null : view.text;
  return (
    <div data-kind-index={kind.surface} className="tdl-card tdl-kind-card">
      <span className="tdl-card-figure">{count != null ? count : ' '}</span>
      <a href={formatHash(kind.surface, {}, {})} className="tdl-record-name tdl-card-title tdl-stretch">{word}</a>
      {what && <p className="tdl-card-text">{what}</p>}
    </div>
  );
}

function ElementsIndex() {
  const [body, setBody] = React.useState(null);
  const [failed, setFailed] = React.useState(false);
  const names = useNames();
  const filters = useSurfaceFilters(SPEC);
  const q = filters.values.q || '';

  React.useEffect(() => {
    let live = true;
    api.slots().then((b) => { if (live) setBody(b); }).catch(() => { if (live) setFailed(true); });
    return () => { live = false; };
  }, []);

  const slots = body && Array.isArray(body.slots) ? body.slots : [];
  const shown = q.trim() ? slots.filter((s) => matches(s, q, ['name', 'id'])) : slots;
  const groups = body && Array.isArray(body.groups) ? body.groups : [];
  const perKind = React.useMemo(() => {
    if (names.status !== 'ready') return {};
    const out = {};
    for (const e of names.index.values()) if (e && e.kind) out[e.kind] = (out[e.kind] || 0) + 1;
    return out;
  }, [names.status, names.index]);

  return (
    <div data-elements-index="" className="tdl-scroll">
      <div className="tdl-page tdl-page-wide">
        <PageHero termId="surface-elements" className="tdl-rise">
          <div className="tdl-hero-acts">
            <FilterInput value={q} onChange={(v) => filters.set('q', v)} count={body ? shown.length : undefined}
              label="Filter the slots by name or id" placeholder="filter slots" width={300} large />
            <span data-index-shown={body ? shown.length : undefined} data-index-total={body ? slots.length : undefined}
              style={data}>
              {body ? `${shown.length} of ${slots.length}` : '…'}
            </span>
            {filters.activeCount > 0 && (
              <button type="button" onClick={filters.clear} className="tdl-link" style={{ font: 'var(--type-data-s)' }}>clear</button>
            )}
          </div>
        </PageHero>

        <nav data-record-kinds="" aria-label="records" className="tdl-grid tdl-rise-2"
          style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(13.5rem, 1fr))', margin: '0 0 44px' }}>
          {RECORD_KINDS.map((k) => <KindCard key={k.surface} kind={k} count={perKind[k.cite]} />)}
        </nav>

        {failed && <p style={{ font: 'var(--type-body)', color: 'var(--text-secondary)' }}>The slots could not be read.</p>}
        {!body && !failed && <p style={data}>reading the slots…</p>}
        {body && (
          <div className="tdl-families tdl-rise-3" style={{ margin: 0 }}>
            {groups.map((g) => {
              const rows = shown.filter((s) => s.group === g.id);
              if (!rows.length) return null;
              return (
                <section key={g.id} data-slot-group={g.id} className="tdl-family" role="table" aria-label={g.name || g.id}
                  style={{ marginBottom: 34 }}>
                  <div role="row" className="tdl-family-name" style={{ borderBottom: '2px solid var(--text-body)', paddingBottom: 7 }}>
                    <h3 role="columnheader" style={{ font: 'var(--fw-reg) var(--fs-d4)/1.2 var(--display)', margin: 0 }}>
                      {g.name || g.id}<span className="tdl-record-note">{g.id}</span>
                    </h3>
                    <span role="columnheader" className="tdl-year"><Term id="binding-specified" /></span>
                  </div>
                  {rows.map((s) => (
                    <div role="row" key={s.id} data-slot-row={s.id} data-specified-by={s.specified_by} className="tdl-style-row">
                      <span role="cell"><RecordLink cite={'slot:' + s.id}>{s.name || s.id}</RecordLink></span>
                      <span role="cell" className="tdl-year">{s.specified_by}</span>
                    </div>
                  ))}
                </section>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

export function Elements({ selection }) {
  const slot = selection && typeof selection.slot === 'string' && selection.slot.trim() ? selection.slot.trim() : null;
  return slot ? <SlotPanel key={slot} slot={slot} /> : <ElementsIndex />;
}
