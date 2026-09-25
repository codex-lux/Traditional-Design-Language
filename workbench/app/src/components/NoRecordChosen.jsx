/* WHAT A RECORD PANE SAYS WHEN THE ADDRESS NAMES NO RECORD (WP-14.27, PRD §C.12).

   The Fault Corpus and the family tree each fell back to a record typed into the component --
   a Georgian porch fault, a Tidewater taxon -- so a bare `#/faults` or `#/phylogeny` showed one
   record's card under an address that named none, which is the default record tranche 1
   removed from the Styles index and the pack index (docs/workbench.md). Both panes now say that
   nothing is chosen, and every word of it is the `no-record-chosen` glossary record's: its term
   as the heading, its definition as the sentence. Nothing here is written in the app, so a
   loading or unreadable glossary shows the Term's own states rather than a gloss of ours. */
import React from 'react';
import { useGlossary } from '../api/useGlossary.js';
import { termView } from '../glossary/termView.js';
import { Eyebrow } from './Eyebrow.jsx';
import { Term } from './Term.jsx';

export function NoRecordChosen({ surface }) {
  const glossary = useGlossary();
  const v = termView(glossary, { id: 'no-record-chosen' });
  return (
    <div data-no-record={surface || ''} style={{ padding: '14px 2px', maxWidth: '60ch' }}>
      <Eyebrow style={{ marginBottom: 6 }}><Term id="no-record-chosen" /></Eyebrow>
      {v.state === 'ready' && (
        <p data-term-definition="no-record-chosen"
          style={{ font: 'var(--fw-reg) 12.5px/1.6 var(--body)', color: 'var(--ink-3)', margin: 0 }}>
          {v.definition}
        </p>
      )}
    </div>
  );
}
