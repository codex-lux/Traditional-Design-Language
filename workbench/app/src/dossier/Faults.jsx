/* Faults — the named errors as they bear on this style (WP-14.12, PRD §D.1 row 7, §H.4).

   Three lists, in the order they matter to a reader of THIS style: the faults the corpus reads for
   it by name (an exception, an inversion, a severity its record states for it), then the faults
   written for its lineage rather than for every house, then a COUNT of the universal rest with a
   link to the Fault Corpus narrowed to this style. The partition is the dossier payload's and
   nothing here re-derives it. At a tradition or a family the universal line is not drawn: a
   universal fault is about a house, a tradition is not built, and the dossier's own count for the
   section leaves them out for exactly that reason (§D.2) -- drawing them would make the page and
   its strip disagree.

   THE THREE HEADINGS ARE THE FAULT CORPUS'S OWN RECORDS (WP-14.31): `fault-group-here`,
   `-lineage` and `-universal` head the same three groups on that surface, and this section wrote
   its own three phrases for them, one of which ("written for every house") restated the
   universal record's definition in a link. A reader who met the groups here and there met two
   vocabularies for one partition. */
import React from 'react';
import { RecordLink } from '../components/RecordLink.jsx';
import { Term } from '../components/Term.jsx';
import { useGlossary } from '../api/useGlossary.js';
import { wordOf } from '../glossary/termView.js';
import { formatHash } from '../router.js';
import { Section, data } from './parts.jsx';

const BUILT = { style: 1, variant: 1 };

function FaultList({ ids, styleId, attr }) {
  return ids.map((id) => (
    <div key={id} {...{ [attr]: id }} style={{ padding: '3px 0' }}>
      <RecordLink cite={'fault:' + id} ctx={{ style: styleId }} />
    </div>
  ));
}

export function Faults({ dossier, styleId }) {
  const f = dossier.faults || {};
  const here = f.verdict_here || [];
  const lineage = f.lineage || [];
  const universal = BUILT[dossier.rank] ? f.universal_count : null;
  const glossary = useGlossary();
  const corpusWord = glossary.status === 'ready' && glossary.lookup ? wordOf(glossary.lookup, 'surface-faults') : '';
  return (
    <div data-dossier-section="faults" style={{ maxWidth: 760 }}>
      {here.length > 0 && (
        <Section eyebrow={<><Term id="fault-group-here" /> · {here.length}</>}>
          <FaultList ids={here} styleId={styleId} attr="data-fault-here" />
        </Section>
      )}
      {lineage.length > 0 && (
        <Section eyebrow={<><Term id="fault-group-lineage" /> · {lineage.length}</>}>
          <FaultList ids={lineage} styleId={styleId} attr="data-fault-lineage" />
        </Section>
      )}
      {typeof universal === 'number' && universal > 0 && (
        <Section eyebrow={<><Term id="fault-group-universal" /> · {universal}</>}>
          <a href={formatHash('faults', { style: styleId }, {})} data-fault-universal={universal}
            style={{ font: 'var(--type-data-s)', color: 'var(--gilt-deep)' }}>
            {corpusWord} →
          </a>
          <p style={{ ...data, marginTop: 4 }}>{f.matches} in all</p>
        </Section>
      )}
    </div>
  );
}
