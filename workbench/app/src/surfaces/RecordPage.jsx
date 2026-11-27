/* The record pages — `#/room/<id>`, `#/massing/<id>`, `#/grouping/<id>`, `#/parti/<id>`
   (WP-14.23, tranche 2 PRD §B.1, §C.6).

   Until these existed a `room:`, `massing:`, `grouping:` or `parti:` citation landed on a surface
   that was about something else -- the bench, the family tree, the candidate set -- and a
   "searched" card floated the record over it. Each kind has a page of its own now: the shell's
   `PageHead` names the kind (`surface-<kind>`), `record/parts.jsx::RecordHead` names the record,
   and `record/<Kind>Body.jsx` shows it with its relations from the other side.

   A BARE RECORD SURFACE IS THAT KIND'S INDEX AND NEVER A DEFAULT RECORD (§B.1): `#/room` lists
   every room type and opens none, because a bare address must open the same page for everybody
   who follows it. The list is the names index the palette already holds (`GET /api/search/index`,
   through `useNames`), filtered to the kind -- every record of the kind, each with the short
   categorical field that index carries -- and `?q=` narrows it by name or id. */
import React from 'react';
import { api } from '../api/client.js';
import { useNames } from '../names/useNames.js';
import { useSurfaceFilters } from '../filters/useFilters.js';
import { matches } from '../search/match.js';
import { kindOfSurface, recordIdOf } from '../record/kinds.js';
import { RecordLink } from '../components/RecordLink.jsx';
import { FilterInput } from '../components/FilterInput.jsx';
import { PageHero } from '../components/PageHead.jsx';
import { Reading, data } from '../record/parts.jsx';
import { RoomBody } from '../record/RoomBody.jsx';
import { MassingBody } from '../record/MassingBody.jsx';
import { GroupingBody } from '../record/GroupingBody.jsx';
import { PartiBody } from '../record/PartiBody.jsx';

/* surface -> how its one record is read and drawn. */
const READERS = {
  room: { read: (id) => api.room(id), Body: RoomBody },
  massing: { read: (id) => api.massing(id), Body: MassingBody },
  grouping: { read: (id) => api.grouping(id), Body: GroupingBody },
  parti: { read: (id) => api.parti(id), Body: PartiBody },
};

const SPEC = { q: { type: 'text' } };

function KindIndex({ kind }) {
  const names = useNames();
  const filters = useSurfaceFilters(SPEC);
  const q = filters.values.q || '';
  const all = React.useMemo(() => [...names.index.values()]
    .filter((e) => e && e.kind === kind.cite)
    .sort((a, b) => String(a.name || a.id).localeCompare(String(b.name || b.id))), [names.index, kind.cite]);
  const rows = q.trim() ? all.filter((e) => matches(e, q, ['name', 'id'])) : all;
  const ready = names.status === 'ready';
  return (
    <div data-record-index={kind.surface} className="tdl-scroll">
      <div className="tdl-page tdl-page-wide">
        <PageHero termId={`surface-${kind.surface}`} className="tdl-rise">
          <div className="tdl-hero-acts">
            <FilterInput value={q} onChange={(v) => filters.set('q', v)} count={ready ? rows.length : undefined}
              label="Filter by name or id" placeholder="filter" width={300} large />
            <span data-index-shown={ready ? rows.length : undefined} data-index-total={ready ? all.length : undefined}
              style={data}>
              {ready ? `${rows.length} of ${all.length}` : '…'}
            </span>
            {filters.activeCount > 0 && (
              <button type="button" onClick={filters.clear} className="tdl-link" style={{ font: 'var(--type-data-s)' }}>clear</button>
            )}
          </div>
        </PageHero>
        <div className="tdl-rule-double" style={{ marginBottom: 14 }} />
        {!ready && names.status !== 'error' && <p style={data}>reading the index…</p>}
        {names.status === 'error' && <p style={{ font: 'var(--type-body)', color: 'var(--text-secondary)' }}>The index could not be read.</p>}
        {ready && (
          <div className="tdl-columns tdl-rise-2">
            {rows.map((e) => (
              <div key={e.cite} data-index-row={e.id} className="tdl-index-row">
                <RecordLink cite={e.cite} />
                {e.meta && <span className="tdl-index-meta">{Array.isArray(e.meta) ? e.meta.join(' · ') : String(e.meta)}</span>}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function OneRecord({ kind, id }) {
  const reader = READERS[kind.surface];
  const [rec, setRec] = React.useState(null);
  const [error, setError] = React.useState(null);
  React.useEffect(() => {
    let live = true;
    setRec(null); setError(null);
    reader.read(id).then((r) => { if (live) setRec(r); }).catch((e) => { if (live) setError(e); });
    return () => { live = false; };
  }, [reader, id]);
  const cite = `${kind.cite}:${id}`;
  const { Body } = reader;
  return (
    <div data-record-page={cite} className="tdl-scroll">
      <div className="tdl-page">
        <Reading error={error} cite={cite} ready={Boolean(rec)}>
          {rec && <Body rec={rec} />}
        </Reading>
      </div>
    </div>
  );
}

export function RecordPage({ surface, selection }) {
  const kind = kindOfSurface(surface);
  if (!kind || !READERS[surface]) return null;
  const id = recordIdOf(kind, selection);
  return id ? <OneRecord key={id} kind={kind} id={id} /> : <KindIndex kind={kind} />;
}

/* One component per surface, for the shell's surface table, which hands a surface its selection
   and not its own name. */
export const RoomPage = (props) => <RecordPage surface="room" {...props} />;
export const MassingPage = (props) => <RecordPage surface="massing" {...props} />;
export const GroupingPage = (props) => <RecordPage surface="grouping" {...props} />;
export const PartiPage = (props) => <RecordPage surface="parti" {...props} />;
