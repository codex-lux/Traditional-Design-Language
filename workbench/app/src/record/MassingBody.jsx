/* One massing's page — `#/massing/<id>` (WP-14.23, tranche 2 §B.1, §C.6).

   The skeleton a house type is built on: its plan shape, storeys and bays as the catalogue states
   them, why the volume is that shape, how it grows, and the styles that name it among their
   massing affinities, each at the affinity that style gives it. That last list is `used_by`, which
   core reads off every style's own `massing_affinities`, so a style's Plan types and this page
   cannot disagree about one affinity (`workbench/server/tests/test_record_pages.py`). */
import React from 'react';
import { Term } from '../components/Term.jsx';
import { VariantPill } from '../components/VariantPill.jsx';
import { RecordHead, Section, Prose, LinkRows, data } from './parts.jsx';

/* The affinity ladder's order, strongest first -- the order of the schema's own enum
   (`schema/style-node.schema.json`, massing_affinities), which VariantPill's `affinity` ladder
   draws. A value outside it sorts last rather than being dropped. */
const AFFINITY = ['canonical', 'common', 'possible', 'atypical', 'forbidden'];
const rankOf = (a) => { const i = AFFINITY.indexOf(a); return i === -1 ? AFFINITY.length : i; };

const FACTS = [
  ['footprint', 'massing-plan-shape'],
  ['stories', 'massing-storeys'],
  ['bays', 'massing-bays'],
];

export function MassingBody({ rec }) {
  const m = rec.massing || {};
  const users = (Array.isArray(rec.used_by) ? rec.used_by : [])
    .slice().sort((a, b) => rankOf(a.affinity) - rankOf(b.affinity) || String(a.style).localeCompare(String(b.style)));
  const facts = FACTS.filter(([k]) => typeof m[k] === 'string' && m[k].trim());
  return (
    <div data-record-body="massing" style={{ maxWidth: 820 }}>
      <RecordHead name={m.name} id={m.id} aka={m.aka} />
      {facts.length > 0 && (
        <dl data-massing-facts="" style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: '3px 18px', margin: '0 0 16px' }}>
          {facts.map(([k, termId]) => (
            <React.Fragment key={k}>
              <dt style={data}><Term id={termId} /></dt>
              <dd style={{ ...data, color: 'var(--ink)', margin: 0 }}>{m[k]}</dd>
            </React.Fragment>
          ))}
        </dl>
      )}
      <Prose text={m.description} />
      {m.structural_logic && (
        <Section eyebrow={<Term id="structural-logic" />}><Prose text={m.structural_logic} /></Section>
      )}
      {m.expansion_logic && (
        <Section eyebrow={<Term id="expansion-logic" />}><Prose text={m.expansion_logic} /></Section>
      )}
      {users.length > 0 && (
        <Section eyebrow={<><Term id="rank-style" /> · {users.length}</>} data-inverse="style" data-count={users.length}>
          <LinkRows attr="data-style" rows={users.map((u) => ({
            cite: 'style:' + u.style, id: u.style,
            aside: <VariantPill ladder="affinity" status={u.affinity} />,
          }))} />
        </Section>
      )}
    </div>
  );
}
