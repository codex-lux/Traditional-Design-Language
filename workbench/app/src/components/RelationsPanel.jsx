/* How this style stands to the rest, beside its dossier (WP-14.12).

   Four relations, each a list of links a reader can follow and come back from:

     Filed under       the `member_of` chain, root first -- the dossier payload's `chain`
     Filed under this  the records filed directly inside this one -- the payload's `members`
     Neighbours        the records filed under the same parent (`dossier/relations.js`)
     On the bench      the plan open in the Plan step, and whether it is this style

   FILING, NEVER LINEAGE. All three taxonomy relations read `member_of`; lineage -- where a style's
   forms came from -- is a different relation, drawn in the dossier's own Lineage section with
   its edge types. Crumbs follow `member_of` for the same reason (PRD §F.3).

   The panel NAMES the plan on the bench and does not open it: what a reader holds on the bench is
   theirs, and a panel on a style's page that swapped it would be deciding for them. */
import React from 'react';
import { planDoc } from '../state/planDoc.js';
import { formatHash } from '../router.js';
import { Term } from './Term.jsx';
import { RecordLink } from './RecordLink.jsx';
import { Eyebrow } from './Eyebrow.jsx';
import { siblingsOf, benchOf } from '../dossier/relations.js';

const block = { marginBottom: 20 };
const note = { font: 'var(--type-data-s)', color: 'var(--ink-2)', margin: 0 };

function Links({ nodes, attr }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      {nodes.map((n) => (
        <span key={n.id} {...{ [attr]: n.id }}>
          <RecordLink cite={'style:' + n.id}>{n.name || n.id}</RecordLink>
        </span>
      ))}
    </div>
  );
}

export function RelationsPanel({ dossier, styleId, taxa }) {
  const plan = React.useSyncExternalStore(planDoc.subscribe, planDoc.get);
  const chain = (dossier && dossier.chain) || [];
  const members = (dossier && dossier.members) || [];
  const neighbours = taxa ? siblingsOf(styleId, taxa) : null;
  const bench = benchOf(plan, styleId);
  return (
    <aside aria-label="relations" data-relations={styleId} style={{ padding: '16px 14px 24px' }}>
      <section style={block} data-relation="filed-under">
        <Eyebrow style={{ marginBottom: 7 }}><Term id="member-of" /></Eyebrow>
        {chain.length ? <Links nodes={chain} attr="data-filed-under" /> : <p style={note}>—</p>}
      </section>

      {members.length > 0 && (
        <section style={block} data-relation="members">
          <Eyebrow style={{ marginBottom: 7 }}><Term id="section-members" /> · {members.length}</Eyebrow>
          <Links nodes={members} attr="data-filed-here" />
        </section>
      )}

      <section style={block} data-relation="neighbours">
        <Eyebrow style={{ marginBottom: 7 }}>Neighbours{neighbours ? ` · ${neighbours.length}` : ''}</Eyebrow>
        {neighbours === null && <p style={note}>…</p>}
        {neighbours && neighbours.length === 0 && <p style={note}>—</p>}
        {neighbours && neighbours.length > 0 && <Links nodes={neighbours} attr="data-neighbour" />}
      </section>

      <section style={block} data-relation="bench" data-bench-here={bench && bench.here ? '' : undefined}>
        <Eyebrow style={{ marginBottom: 7 }}><Term id="on-the-bench" /></Eyebrow>
        {!bench && <p style={note}>—</p>}
        {bench && (
          <>
            <p style={{ margin: '0 0 3px' }}>
              <a href={formatHash('workbench', {}, {})} style={{ font: 'var(--fw-reg) 14px/1.4 var(--serif)', color: 'var(--ink)' }}>
                {bench.title || bench.id || 'the plan'}
              </a>
            </p>
            {bench.style && (
              <p style={note}>
                {bench.here ? 'in this style' : <>in <RecordLink cite={'style:' + bench.style} /></>}
              </p>
            )}
          </>
        )}
      </section>
    </aside>
  );
}
