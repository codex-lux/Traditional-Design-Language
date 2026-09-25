/* Lineage — where the style comes from and what came of it (WP-14.12, PRD §D.1 row 2).

   The lineage block of `surfaces/StyleRecord.jsx`, extracted with its EdgeGlyph call exactly as it
   was, and the cascade ladder from `surfaces/KitSurface.jsx`'s side panel beside it: the edges say
   which relations a style claims, the ladder says which of them actually hand it a kit, and
   "carries is not claims" is read off the two together. The dossier's lineage count is the
   record's own edges plus the edges that name it as a target, which is what this draws -- the
   record's `lineage` and its `descendants`.

   A descendant is a LINK to that record now, written to the URL, where it was a button that
   swapped the record in place and left the address saying the old one. */
import React from 'react';
import { api } from '../api/client.js';
import { EdgeGlyph } from '../components/EdgeGlyph.jsx';
import { ProvenanceTrace } from '../components/ProvenanceTrace.jsx';
import { RecordLink } from '../components/RecordLink.jsx';
import { Term } from '../components/Term.jsx';
import { Section, quiet } from './parts.jsx';
import { cascadeRows } from './relations.js';

const CARRIES = { descends_from: 1, regional_of: 1 };

export function Lineage({ rec, styleId, onCite }) {
  const [cascade, setCascade] = React.useState(null);
  React.useEffect(() => {
    setCascade(null);
    api.cascade(styleId).then(setCascade).catch(() => setCascade(null));
  }, [styleId]);
  const ladder = cascadeRows(cascade);

  return (
    <div data-dossier-section="lineage" style={{ display: 'flex', gap: 34, alignItems: 'flex-start', flexWrap: 'wrap' }}>
      <div style={{ flex: '1 1 380px', minWidth: 320, maxWidth: 620 }}>
        {(rec.lineage || []).length > 0 && (
          <Section eyebrow="lineage · carries ≠ claims">
            {rec.lineage.map((e, i) => (
              <div key={i} style={{ marginBottom: 10 }}>
                <EdgeGlyph edge={e} width={44} />
              </div>
            ))}
          </Section>
        )}
        {(rec.descendants || []).length > 0 && (
          <Section eyebrow={<>descendants · {rec.descendants.length}</>}>
            {rec.descendants.map((d) => (
              <p key={d.id + d.type} data-descendant={d.id} data-carries={CARRIES[d.type] ? '' : undefined}
                style={{ ...quiet, marginBottom: 5 }}>
                <RecordLink cite={'style:' + d.id} />{' '}
                <span style={{ font: 'var(--type-data-s)', color: CARRIES[d.type] ? 'var(--gilt-deep)' : 'var(--ink-3)' }}>
                  <Term field="lineage.type" value={d.type} />
                </span>
              </p>
            ))}
          </Section>
        )}
      </div>
      {ladder.length > 0 && (
        <div style={{ flex: '0 1 320px', minWidth: 260 }}>
          <Section>
            <ProvenanceTrace cascade={ladder} collapseFrom={7}
              onSelect={(s) => { onCite && onCite('style:' + s); }} />
          </Section>
        </div>
      )}
    </div>
  );
}
