/* One grouping's page — `#/grouping/<id>` (WP-14.23, tranche 2 §B.1, §C.6).

   A cluster of rooms designed as one: the rooms it holds and the part each plays, the rules it
   keeps among them, the massings it can be laid into, how it grows, and the plan diagrams that
   carry it. That last list is `carried_by`, which `corpus.grouping` reads off every parti's own
   `groupings`, so a parti's page and this one cannot disagree about which diagrams carry a
   grouping (`workbench/server/tests/test_record_pages.py`). */
import React from 'react';
import { Term } from '../components/Term.jsx';
import { VariantPill } from '../components/VariantPill.jsx';
import { RecordHead, Section, Prose, LinkRows, data, quiet } from './parts.jsx';

export function GroupingBody({ rec }) {
  const rooms = Array.isArray(rec.rooms) ? rec.rooms : [];
  const rules = Array.isArray(rec.internal_rules) ? rec.internal_rules : [];
  const attaches = Array.isArray(rec.attaches_to) ? rec.attaches_to : [];
  const carried = Array.isArray(rec.carried_by) ? rec.carried_by : [];
  return (
    <div data-record-body="grouping" style={{ maxWidth: 820 }}>
      <RecordHead name={rec.name} id={rec.id} aka={rec.aka} meta={rec.scale} />
      <Prose text={rec.description} />

      {rooms.length > 0 && (
        <Section eyebrow={<><Term id="room" /> · {rooms.length}</>} data-grouping-rooms={rooms.length}>
          <LinkRows attr="data-grouping-room" rows={rooms.map((x) => ({
            cite: 'room:' + x.room, id: x.room,
            aside: <span style={data}>{[x.role, x.count].filter(Boolean).join(' · ')}</span>,
            note: x.note,
          }))} />
        </Section>
      )}

      {rules.length > 0 && (
        <Section eyebrow={<><Term id="internal-rules" /> · {rules.length}</>} data-grouping-rules={rules.length}>
          {rules.map((r, i) => (
            <div key={i} data-grouping-rule={i} style={{ display: 'flex', gap: 12, alignItems: 'baseline', padding: '3px 0' }}>
              <span style={{ ...data, width: 76, flex: 'none' }}>{[r.severity, r.kind].filter(Boolean).join(' · ')}</span>
              <p style={{ ...quiet, color: 'var(--ink)' }}>{r.statement}</p>
            </div>
          ))}
        </Section>
      )}

      {attaches.length > 0 && (
        <Section eyebrow={<><Term id="attaches-to" /> · {attaches.length}</>} data-grouping-attaches={attaches.length}>
          <LinkRows attr="data-attaches-to" rows={attaches.map((a) => ({
            cite: 'massing:' + a.massing, id: a.massing,
            aside: a.fit ? <VariantPill ladder="affinity" status={a.fit} /> : null,
            note: [a.position, a.note].filter(Boolean).join(' — ') || null,
          }))} />
        </Section>
      )}

      {rec.expansion_logic && (
        <Section eyebrow={<Term id="expansion-logic" />}><Prose text={rec.expansion_logic} /></Section>
      )}

      {carried.length > 0 && (
        <Section eyebrow={<><Term id="parti" /> · {carried.length}</>} data-inverse="parti" data-count={carried.length}>
          <LinkRows attr="data-parti" rows={carried.map((p) => ({ cite: 'parti:' + p.id, id: p.id, name: p.name }))} />
        </Section>
      )}
    </div>
  );
}
