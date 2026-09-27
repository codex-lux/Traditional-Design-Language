/* Lineage — where the style comes from and what came of it (WP-14.12, PRD §D.1 row 2).

   The lineage block of `surfaces/StyleRecord.jsx`, extracted with its EdgeGlyph call as WP-14.11
   left it (`edge={e}`: the glyph reads the edge's own `inherits_kit`), and the cascade ladder from
   `surfaces/KitSurface.jsx`'s side panel beside it: the edges say which relations a style claims,
   the ladder says which of them actually hand it a kit, and "carries is not claims" is read off
   the two together. The dossier's lineage count is the record's own edges plus the edges that
   name it as a target, which is what this draws -- the record's `lineage` and its `descendants`.

   A descendant is a LINK to that record now, written to the URL, where it was a button that
   swapped the record in place and left the address saying the old one. What its edge carries is
   the SERVED flag (`/api/styles/{id}` serves each descendant's `inherits_kit` and `slots`, held to
   `/api/phylogeny` edge by edge in `test_dossier_routes.py`), read through `lineage/carry.js` --
   StyleRecord coloured these rows from a table keyed on the edge's TYPE, a fourth copy of the
   table WP-14.11 removed, and wrong on every `hybridizes_with` edge that carries the kit. */
import React from 'react';
import { api } from '../api/client.js';
import { EdgeGlyph } from '../components/EdgeGlyph.jsx';
import { ProvenanceTrace } from '../components/ProvenanceTrace.jsx';
import { RecordLink } from '../components/RecordLink.jsx';
import { Term } from '../components/Term.jsx';
import { carriesKit, carryTermOf } from '../lineage/carry.js';
import { Section, quiet } from './parts.jsx';
import { cascadeRows, descendantEdge } from './relations.js';

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
            {rec.descendants.map((d) => {
              const edge = descendantEdge(d, styleId);
              const carries = carriesKit(edge);
              return (
                <p key={d.id + d.type} data-descendant={d.id} data-carries={carries ? '' : undefined}
                  data-carry={carryTermOf(edge)} style={{ ...quiet, marginBottom: 5 }}>
                  <RecordLink cite={'style:' + d.id} />{' '}
                  <span style={{ font: 'var(--type-data-s)', color: carries ? 'var(--gilt-deep)' : 'var(--ink-2)' }}>
                    <Term field="lineage.type" value={d.type} /> · <Term id={carryTermOf(edge)} />
                  </span>
                </p>
              );
            })}
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
