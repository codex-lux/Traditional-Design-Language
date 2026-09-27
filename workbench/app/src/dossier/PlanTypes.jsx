/* Plan types — the house types this style is built as (WP-14.12, PRD §D.1 row 5).

   A LIST, AND ONLY A LIST. The massing affinities come from the node (they were in both the Style
   Record and the Kit's side panel), the style's own partis from `core.list_partis` -- native and
   lineage since WP-14.19, each carrying the `nativity` `compose.nativity` gave it -- and the
   groupings whose own `style_variation` names this style -- all three served by the dossier
   payload, whose `plans` count is their total.

   A PARTI ROW STARTS A BRIEF (WP-14.25). Until the brief schema admitted a `parti` (0.2.0, ruled
   25 Sep 2026) nothing here could, and a control offering to would have promised what the next
   page could not do. It can now: each parti row links to Brief Intake with the style and the
   parti named (`formatHash('brief', {style, parti})`), and the composer guarantees the named
   diagram a place among the candidates. The link's word and its description are the glossary
   record `start-a-brief-from-a-plan-type`'s; an anchor cannot hold a `Term`, which is a button,
   so the word is read as the record's own `term`, as the journey bar's steps read theirs. Each
   row's nativity is the served one, worded by its own record, never decided here. Each massing,
   parti and grouping is a RecordLink to its own record page since WP-14.23 (tranche 2 §B.1): the
   name first, the id beside it. */
import React from 'react';
import { Term, useTermDescription } from '../components/Term.jsx';
import { VariantPill } from '../components/VariantPill.jsx';
import { useGlossary } from '../api/useGlossary.js';
import { termView } from '../glossary/termView.js';
import { formatHash } from '../router.js';
import { NATIVITY_TERMS } from '../candidateOrder.js';
import { RecordLink } from '../components/RecordLink.jsx';
import { Section, quiet, data } from './parts.jsx';

export const START_BRIEF_TERM = 'start-a-brief-from-a-plan-type';

/* The link from one plan type to the brief that names it (WP-14.25). Its word is the record's own
   `term` -- `noEntry` or the glossary's failure where the record cannot be shown, nothing while it
   is on its way -- and the record's definition is the link's description. */
function StartBrief({ styleId, partiId }) {
  const v = termView(useGlossary(), { id: START_BRIEF_TERM });
  const d = useTermDescription(START_BRIEF_TERM);
  const word = v.state === 'ready' ? v.word : v.state === 'loading' ? '…' : v.text;
  return (
    <>
      <a href={formatHash('brief', { style: styleId, parti: partiId })} data-start-brief={partiId}
        aria-describedby={d.describedBy} title={d.title}
        style={{ font: 'var(--fw-reg) 13px/1.4 var(--body)' }}>{word}</a>
      {d.element}
    </>
  );
}

function Named({ cite, name, id, note, attr }) {
  return (
    <div {...{ [attr]: id }} style={{ padding: '3px 0' }}>
      <span style={{ font: 'var(--fw-reg) 14px/1.4 var(--serif)' }}>
        <RecordLink cite={cite}>{name || undefined}</RecordLink>
      </span>
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
                <RecordLink cite={'massing:' + m.massing}>{m.massing_name || undefined}</RecordLink>
                <VariantPill ladder="affinity" status={m.affinity} />
              </span>
            ))}
          </div>
        </Section>
      )}
      {partis.length > 0 && (
        <Section eyebrow={<><Term id="parti" /> · {partis.length}</>}>
          {partis.map((p) => (
            <React.Fragment key={p.id}>
              <Named cite={'parti:' + p.id} id={p.id} name={p.name} attr="data-parti" />
              <div data-parti-start={p.id} data-nativity={p.nativity || undefined}
                style={{ display: 'flex', gap: 12, alignItems: 'baseline', margin: '0 0 6px' }}>
                {NATIVITY_TERMS[p.nativity] && <Term id={NATIVITY_TERMS[p.nativity]} />}
                <StartBrief styleId={dossier.id} partiId={p.id} />
              </div>
            </React.Fragment>
          ))}
        </Section>
      )}
      {groupings.length > 0 && (
        <Section eyebrow={<><Term id="grouping" /> · {groupings.length}</>}>
          {groupings.map((g) => <Named key={g.id} cite={'grouping:' + g.id} id={g.id} name={g.name} note={g.note} attr="data-grouping" />)}
        </Section>
      )}
    </div>
  );
}
