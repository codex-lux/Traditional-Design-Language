/* Plan types — the house types this style is built as (WP-14.12, PRD §D.1 row 5).

   A LIST, AND ONLY A LIST. The massing affinities come from the node (they were in both the Style
   Record and the Kit's side panel), the native partis from `core.list_partis`, and the groupings
   whose own `style_variation` names this style -- all three served by the dossier payload, whose
   `plans` count is their total. Nothing here starts a brief from a parti: the brief schema admits
   no parti and the compose route passes only the brief, which is
   `oq/a-brief-cannot-name-a-parti`, so a control offering to would promise what the next page
   cannot do. The partis and groupings are named, with their ids beside them, and not linked. */
import React from 'react';
import { Term } from '../components/Term.jsx';
import { VariantPill } from '../components/VariantPill.jsx';
import { Section, quiet, data } from './parts.jsx';

function Named({ name, id, note, attr }) {
  return (
    <div {...{ [attr]: id }} style={{ padding: '3px 0' }}>
      <span style={{ font: 'var(--fw-reg) 14px/1.4 var(--serif)', color: 'var(--ink)' }}>{name || id}</span>
      <span className="tdl-record-note">{id}</span>
      {note && <p style={{ ...quiet, fontSize: 12.5, marginTop: 2 }}>{note}</p>}
    </div>
  );
}

export function PlanTypes({ dossier }) {
  const pt = dossier.plan_types || {};
  const affs = pt.massing_affinities || [];
  const partis = pt.partis || [];
  const groupings = pt.groupings || [];
  return (
    <div data-dossier-section="plans">
      {affs.length > 0 && (
        <Section eyebrow={<><Term id="massing" /> · {affs.length}</>}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 7 }}>
            {affs.map((m) => (
              <span key={m.massing} data-massing={m.massing} style={{ display: 'flex', gap: 10, alignItems: 'baseline' }}>
                <VariantPill ladder="affinity" name={'massing:' + m.massing} status={m.affinity} />
                {m.massing_name && <span style={data}>{m.massing_name}</span>}
              </span>
            ))}
          </div>
        </Section>
      )}
      {partis.length > 0 && (
        <Section eyebrow={<><Term id="parti" /> · {partis.length}</>}>
          {partis.map((p) => <Named key={p.id} id={p.id} name={p.name} attr="data-parti" />)}
        </Section>
      )}
      {groupings.length > 0 && (
        <Section eyebrow={<><Term id="grouping" /> · {groupings.length}</>}>
          {groupings.map((g) => <Named key={g.id} id={g.id} name={g.name} note={g.note} attr="data-grouping" />)}
        </Section>
      )}
    </div>
  );
}
