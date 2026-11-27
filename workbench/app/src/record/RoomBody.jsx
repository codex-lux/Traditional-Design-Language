/* One room type's page — `#/room/<id>` (WP-14.23, tranche 2 §B.1, §C.6).

   What the room is for, what has to fit in it with its clearances, what it must and must not sit
   beside, and the groupings that contain it. `GET /api/rooms/{id}` serves the record and its
   `appears_in_groupings`, which core reads from the groupings themselves, so the room page and a
   grouping page cannot disagree about which rooms a grouping holds
   (`workbench/server/tests/test_record_pages.py`). */
import React from 'react';
import { Term } from '../components/Term.jsx';
import { RecordHead, Section, Prose, LinkRows, data } from './parts.jsx';

const ADJACENCY = [
  ['must_adjoin', 'must-adjoin'],
  ['should_adjoin', 'should-adjoin'],
  ['must_not_adjoin', 'must-not-adjoin'],
];

const inches = (v) => (typeof v === 'number' ? `${v} in` : null);

export function RoomBody({ rec }) {
  const furniture = Array.isArray(rec.furniture) ? rec.furniture : [];
  const adj = rec.adjacency || {};
  const groupings = Array.isArray(rec.appears_in_groupings) ? rec.appears_in_groupings : [];
  return (
    <div data-record-body="room">
      <RecordHead name={rec.name} id={rec.id} aka={rec.aka} meta={rec.function_class} kicker={<Term id="room" />} />
      <Prose text={rec.description} lede />

      {furniture.length > 0 && (
        <Section eyebrow={<><Term id="furniture" /> · {furniture.length}</>} data-room-furniture={furniture.length}>
          <table className="tdl-table" style={{ maxWidth: '46rem' }}>
            <thead>
              <tr>
                <th scope="col"><Term id="furniture" /></th>
                <th scope="col"><Term id="furniture-footprint" /></th>
                <th scope="col"><Term id="clearance" /></th>
              </tr>
            </thead>
            <tbody>
              {furniture.map((it, i) => (
                <tr key={`${it.item}-${i}`} data-furniture-item={it.item}>
                  <td>{it.item}</td>
                  <td className="tdl-num">
                    {Array.isArray(it.footprint_in) ? `${it.footprint_in.join(' × ')} in` : null}
                  </td>
                  <td className="tdl-num">{inches(it.clearance_in)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Section>
      )}

      {ADJACENCY.map(([key, termId]) => {
        const rows = Array.isArray(adj[key]) ? adj[key] : [];
        if (!rows.length) return null;
        return (
          <Section key={key} eyebrow={<><Term id={termId} /> · {rows.length}</>} data-room-adjacency={key}>
            <LinkRows attr="data-adjoins" rows={rows.map((a) => ({
              cite: 'room:' + a.room, id: a.room, note: a.why,
            }))} />
          </Section>
        );
      })}

      {groupings.length > 0 && (
        <Section eyebrow={<><Term id="grouping" /> · {groupings.length}</>} data-inverse="grouping" data-count={groupings.length}>
          <LinkRows attr="data-grouping" rows={groupings.map((g) => ({ cite: 'grouping:' + g, id: g }))} />
        </Section>
      )}
    </div>
  );
}
