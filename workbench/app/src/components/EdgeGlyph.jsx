/* WHAT AN EDGE CARRIES, DRAWN (WP-14.11, PRD §I.13).

   <EdgeGlyph edge={{ type, inherits_kit, slots, from, target, note }} width={44} />

   The single most important modelling decision in the project, made visible: claimed ancestry is
   not transmitted practice, and only the second one inherits. The weight of the line is the carry
   — solid and heavy where the edge hands the kit down, dashed and light where it hands nothing
   down, dotted where the edge is filing — and beneath it the carry word says which.

   IT READS THE SERVED FLAG, NEVER THE EDGE'S TYPE. This component carried its own table
   (`CARRIES = { descends_from, regional_of }`) and its own verbs, and captioned every other type
   "carries nothing" — which is false of 42 `hybridizes_with` edges that carry the kit, two of them
   only the slots they name (OQ 58). It also printed "browsing only — carries no inheritance"
   under a `member_of` edge, which `build/build.py` has falsified since WP-4.2: the family a style
   is filed under joins its kit cascade. Both tables are gone. `lineage/carry.js` reads
   `inherits_kit` and `slots` off the edge as the server serves them (`corpus.phylogeny`, the one
   spelling of "this edge carries the cascade") and returns a glossary id; every word here is that
   record's, or the `lineage.type` record the server's `by_field` names for the verb, through
   `Term`. There is no caption string in this file and `lineage.test.mjs` reads it to keep it so.

   A filing edge has one word, not two: "filed under" is both the relation and what it carries. The
   `member-of` record says filing is not lineage and does NOT say it hands nothing down, which it
   does: a family's own kit reaches the styles filed under it, and `section-members` says so.
   The target is a `RecordLink`, so the reader sees the style's name with its id beside it, and can
   follow it. */
import React from 'react';
import { Term } from './Term.jsx';
import { RecordLink } from './RecordLink.jsx';
import { carryTermOf, namedSlotsOf, strokeOf, FILING } from '../lineage/carry.js';

const LINE = {
  carries: 'var(--edge-carries-w) solid var(--edge-carries)',
  claims: 'var(--edge-claims-w) dashed var(--edge-claims)',
  filing: 'var(--edge-claims-w) dotted var(--edge-claims)',
};

/* The carry word, by literal id, so `glossary.test.mjs` can hold every one to a record. */
function CarryWord({ carry }) {
  if (carry === 'member-of') return <Term id="member-of" />;
  if (carry === 'carries-the-kit') return <Term id="carries-the-kit" />;
  if (carry === 'carries-named-slots') return <Term id="carries-named-slots" />;
  return <Term id="carries-nothing" />;
}

function EdgeGlyph({ edge, width = 96, style }) {
  const e = edge && typeof edge === 'object' ? edge : {};
  const carry = carryTermOf(e);
  const stroke = strokeOf(e);
  const slots = carry === 'carries-named-slots' ? namedSlotsOf(e) : [];
  const filing = e.type === FILING;
  const target = typeof e.target === 'string' && e.target ? e.target : null;
  const from = typeof e.from === 'string' && e.from ? e.from : null;
  return (
    <span data-edge={e.type} data-edge-target={target || undefined} data-carry={carry}
      style={{ display: 'inline-flex', alignItems: 'baseline', gap: 10, minWidth: 0, ...style }}>
      <span aria-hidden="true" data-edge-line={stroke}
        style={{ width, flex: 'none', height: 0, alignSelf: 'center', borderTop: LINE[stroke] }} />
      <span style={{ minWidth: 0 }}>
        <span style={{ font: 'var(--fw-reg) 13px/1.5 var(--body)', color: 'var(--ink)' }}>
          {from && <><RecordLink cite={'style:' + from} />{' '}</>}
          <span data-edge-verb="">
            {filing
              ? <span data-edge-carry=""><CarryWord carry={carry} /></span>
              : <Term field="lineage.type" value={e.type} />}
          </span>
          {target && <>{' '}<RecordLink cite={'style:' + target} /></>}
        </span>
        {!filing && (
          <span data-edge-carry="" style={{ display: 'block', font: 'var(--type-data-s)',
            color: stroke === 'carries' ? 'var(--ink)' : 'var(--ink-2)', marginTop: 1 }}>
            <CarryWord carry={carry} />
            {slots.length > 0 && (
              <span data-edge-slots={slots.join(' ')}>
                {' · '}
                {slots.map((s, i) => (
                  <React.Fragment key={s}>
                    {i > 0 && ', '}
                    <RecordLink cite={'slot:' + s} />
                  </React.Fragment>
                ))}
              </span>
            )}
          </span>
        )}
        {typeof e.note === 'string' && e.note && (
          <span style={{ display: 'block', font: 'var(--fw-reg) 12.5px/1.5 var(--body)',
            color: 'var(--ink-2)', maxWidth: 'var(--measure-note)', marginTop: 3 }}>{e.note}</span>
        )}
      </span>
    </span>
  );
}

export default EdgeGlyph;
export { EdgeGlyph };
