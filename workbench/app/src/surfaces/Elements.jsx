/* Elements — `#/elements` and `#/elements/<slot>` (WP-14.23, tranche 2 PRD §B.1, §B.4, §C.6).

   THE INDEX is every element slot the ontology names, filed under its slot group in the
   ontology's own order, each with the count of styles whose RESOLVED kit specifies it --
   `GET /api/slots`'s `specified_by`, computed on the server and never typed here. Above the slots,
   the four plan-type kinds, each a link to its own index (`#/massing`, `#/parti`, `#/grouping`,
   `#/room`), because the Elements page is where their record pages stand (the site map's `UNDER`).
   `?q=` narrows the slots by name or id.

   A SLOT is `dossier/SlotPanel.jsx`, which tranche 1 built as the interim page for a slot with no
   style and parked under the Styles index; its address there, `#/style/-/kit/<slot>`, is read as
   this one and rewritten (router.js, LEGACY_PLACES). */
import React from 'react';
import { api } from '../api/client.js';
import { formatHash } from '../router.js';
import { useNames } from '../names/useNames.js';
import { useGlossary } from '../api/useGlossary.js';
import { termView } from '../glossary/termView.js';
import { useSurfaceFilters } from '../filters/useFilters.js';
import { matches } from '../search/match.js';
import { RECORD_KINDS } from '../record/kinds.js';
import { Term } from '../components/Term.jsx';
import { RecordLink } from '../components/RecordLink.jsx';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { FilterInput } from '../components/FilterInput.jsx';
import { FilterStrip } from '../Chrome.jsx';
import { SlotPanel } from '../dossier/SlotPanel.jsx';
import { data } from '../record/parts.jsx';

const SPEC = { q: { type: 'text' } };

/* A kind's own surface record's word, as a link to that kind's index. */
function KindLink({ kind, count }) {
  const glossary = useGlossary();
  const v = termView(glossary, { id: `surface-${kind.surface}` });
  const word = v.state === 'ready' ? v.word : v.state === 'loading' ? null : v.text;
  return (
    <span data-kind-index={kind.surface} style={{ display: 'inline-flex', gap: 6, alignItems: 'baseline' }}>
      <a href={formatHash(kind.surface, {}, {})} className="tdl-record-name"
        style={{ font: 'var(--fw-reg) 15px/1.4 var(--serif)' }}>{word}</a>
      {count != null && <span style={data}>{count}</span>}
    </span>
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
    <div data-elements-index="" style={{ display: 'flex', flexDirection: 'column', minHeight: 0, flex: 1 }}>
      <FilterStrip filters={filters} right={
        <span data-index-shown={body ? shown.length : undefined} data-index-total={body ? slots.length : undefined}
          style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)' }}>
          {body ? `${shown.length} of ${slots.length}` : '…'}
        </span>
      }>
        <Eyebrow as="span"><Term id="slot" /></Eyebrow>
        <FilterInput value={q} onChange={(v) => filters.set('q', v)} count={body ? shown.length : undefined}
          label="Filter the slots by name or id" placeholder="filter slots" width={200} />
      </FilterStrip>

      <div style={{ flex: 1, overflow: 'auto', minHeight: 0, padding: '16px 26px 40px' }}>
        <nav data-record-kinds="" aria-label="records"
          style={{ display: 'flex', flexWrap: 'wrap', gap: '6px 26px', padding: '0 0 14px', marginBottom: 6,
            borderBottom: 'var(--rule-hair)' }}>
          {RECORD_KINDS.map((k) => <KindLink key={k.surface} kind={k} count={perKind[k.cite]} />)}
        </nav>

        {failed && <p style={{ font: 'var(--type-body)', color: 'var(--ink-2)' }}>The slots could not be read.</p>}
        {!body && !failed && <p style={data}>reading the slots…</p>}
        {body && groups.map((g) => {
          const rows = shown.filter((s) => s.group === g.id);
          if (!rows.length) return null;
          return (
            <section key={g.id} data-slot-group={g.id} style={{ marginTop: 18 }}>
              <h3 style={{ font: 'var(--fw-reg) 17px/1.3 var(--display)', margin: '0 0 6px' }}>
                {g.name || g.id}<span className="tdl-record-note">{g.id}</span>
              </h3>
              <div role="table" style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) auto', gap: '2px 22px',
                alignItems: 'baseline', maxWidth: 760 }}>
                <div role="row" style={{ display: 'contents' }}>
                  <span role="columnheader" style={data}><Term id="slot" /></span>
                  <span role="columnheader" style={data}><Term id="binding-specified" /></span>
                </div>
                {rows.map((s) => (
                  <div role="row" key={s.id} data-slot-row={s.id} data-specified-by={s.specified_by} style={{ display: 'contents' }}>
                    <span role="cell" style={{ font: 'var(--fw-reg) 14px/1.45 var(--serif)' }}>
                      <RecordLink cite={'slot:' + s.id}>{s.name || s.id}</RecordLink>
                    </span>
                    <span role="cell" style={{ ...data, textAlign: 'right' }}>{s.specified_by}</span>
                  </div>
                ))}
              </div>
            </section>
          );
        })}
      </div>
    </div>
  );
}

export function Elements({ selection }) {
  const slot = selection && typeof selection.slot === 'string' && selection.slot.trim() ? selection.slot.trim() : null;
  return slot ? <SlotPanel key={slot} slot={slot} /> : <ElementsIndex />;
}
