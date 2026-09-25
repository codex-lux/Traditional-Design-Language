/* Filed under this — `member_of` inverted (WP-14.12, PRD §D.1 row 1).

   The Style Record had no such section, so a family or a tradition -- a record that exists to
   hold others -- opened on a page with nothing on it but its description: the records filed under
   it were one click away on the Phylogeny and none on the record itself. The dossier payload
   serves them (`members`), and for a tradition or a family every buildable style and variant
   filed anywhere beneath it (`buildable_at`), in reading order. Both lists are the payload's, and
   the walk holds their lengths to `/api/styles/{id}/dossier`. */
import React from 'react';
import { Term } from '../components/Term.jsx';
import { RecordLink } from '../components/RecordLink.jsx';
import { Section, data } from './parts.jsx';

function Row({ node, attr }) {
  return (
    <div {...{ [attr]: node.id }} style={{ display: 'flex', gap: 10, alignItems: 'baseline', padding: '3px 0' }}>
      <span style={{ ...data, width: 74, flex: 'none' }}>
        {node.rank ? <Term field="style.rank" value={node.rank} /> : null}
      </span>
      <RecordLink cite={'style:' + node.id}>{node.name || node.id}</RecordLink>
    </div>
  );
}

export function Members({ dossier }) {
  const members = dossier.members || [];
  const buildable = dossier.buildable_at || [];
  return (
    <div data-dossier-section="members">
      {members.length > 0 && (
        <Section eyebrow={<><Term id="section-members" /> · {members.length}</>}>
          {members.map((m) => <Row key={m.id} node={m} attr="data-member" />)}
        </Section>
      )}
      {buildable.length > 0 && (
        <Section eyebrow={<>buildable beneath it · {buildable.length}</>}>
          {buildable.map((m) => <Row key={m.id} node={m} attr="data-buildable" />)}
        </Section>
      )}
    </div>
  );
}
