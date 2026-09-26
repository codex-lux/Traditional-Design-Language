/* One parti's page — `#/parti/<id>` (WP-14.23, tranche 2 §B.1, §C.6).

   A plan diagram states TOPOLOGY AND ROLES ONLY, and this page draws none: its rooms are a TABLE
   -- each room's type, the floor it is on, which of its walls face outside, and what it opens
   into -- because a diagram drawn from a record that states no positions would be a drawing of
   what the record does not hold (§G). Then its massing, the groupings it carries, how it grows,
   what it gives up, and the styles it is native or lineage to. That last is `nativity_by_style`,
   read through `compose.nativity`, the one spelling of the relation a style's own Plan types also
   read, so the two pages cannot disagree (`workbench/server/tests/test_record_pages.py`). */
import React from 'react';
import { Term } from '../components/Term.jsx';
import { RecordLink } from '../components/RecordLink.jsx';
import { RecordHead, Section, Prose, LinkRows, KnownLink, data } from './parts.jsx';

const cell = { padding: '4px 14px 4px 0', verticalAlign: 'baseline', textAlign: 'left' };

export function PartiBody({ rec }) {
  const p = rec.parti || {};
  const rooms = Array.isArray(p.rooms) ? p.rooms : [];
  const byId = new Map(rooms.map((r) => [r.id, r]));
  const massings = [p.massing, ...(Array.isArray(p.alternate_massings) ? p.alternate_massings : [])].filter(Boolean);
  const groupings = Array.isArray(p.groupings) ? p.groupings : [];
  const scaling = p.scaling || {};
  const grows = Array.isArray(scaling.grows_by) ? scaling.grows_by : [];
  const nat = rec.nativity_by_style || {};
  return (
    <div data-record-body="parti" style={{ maxWidth: 900 }}>
      <RecordHead name={p.name} id={p.id} aka={p.aka} meta={p.circulation_parti} />
      <Prose text={p.description} />

      {rooms.length > 0 && (
        <Section eyebrow={<><Term id="room" /> · {rooms.length}</>} data-parti-rooms={rooms.length}>
          <table data-parti-topology="" style={{ borderCollapse: 'collapse', width: '100%' }}>
            <thead>
              <tr style={{ borderBottom: 'var(--rule-hair)' }}>
                <th style={{ ...cell, ...data }} scope="col"><Term id="room" /></th>
                <th style={{ ...cell, ...data }} scope="col"><Term id="parti-level" /></th>
                <th style={{ ...cell, ...data }} scope="col"><Term id="outside-walls" /></th>
                <th style={{ ...cell, ...data }} scope="col"><Term id="parti-doors" /></th>
              </tr>
            </thead>
            <tbody>
              {rooms.map((r) => (
                <tr key={r.id} data-parti-room={r.id} style={{ borderBottom: 'var(--rule-hair-soft)' }}>
                  <td style={cell}>
                    {r.type ? <KnownLink cite={'room:' + r.type}>{r.name || r.id}</KnownLink> : <span>{r.name || r.id}</span>}
                  </td>
                  <td style={{ ...cell, ...data }}>{r.level != null ? String(r.level) : null}</td>
                  <td style={{ ...cell, ...data }}>{(r.exterior_walls || []).join(' ')}</td>
                  <td style={{ ...cell, ...data }}>
                    {(r.doors || []).map((d) => (byId.has(d) ? (byId.get(d).name || d) : d)).join(' · ')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Section>
      )}

      {massings.length > 0 && (
        <Section eyebrow={<><Term id="massing" /> · {massings.length}</>} data-parti-massing={p.massing}>
          <LinkRows attr="data-massing" rows={massings.map((m) => ({ cite: 'massing:' + m, id: m }))} />
        </Section>
      )}

      {groupings.length > 0 && (
        <Section eyebrow={<><Term id="grouping" /> · {groupings.length}</>} data-parti-groupings={groupings.length}>
          <LinkRows attr="data-grouping" rows={groupings.map((g) => ({ cite: 'grouping:' + g, id: g }))} />
        </Section>
      )}

      {(grows.length > 0 || scaling.note) && (
        <Section eyebrow={<Term id="expansion-logic" />}>
          {grows.length > 0 && <p style={{ ...data, margin: '0 0 6px' }}>{grows.join(' · ')}</p>}
          <Prose text={scaling.note} />
        </Section>
      )}

      {p.trades_away && (
        <Section eyebrow={<Term id="trades-away" />}><Prose text={p.trades_away} /></Section>
      )}

      {['native', 'lineage'].map((n) => {
        const styles = Array.isArray(nat[n]) ? nat[n] : [];
        if (!styles.length) return null;
        return (
          <Section key={n} eyebrow={<><Term id={'parti-' + n} /> · {styles.length}</>} data-inverse={'style-' + n} data-count={styles.length}>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px 16px' }}>
              {styles.map((s) => <span key={s} data-style={s}><RecordLink cite={'style:' + s} /></span>)}
            </div>
          </Section>
        );
      })}
    </div>
  );
}
