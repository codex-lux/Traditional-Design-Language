/* The type and the section frame the dossier's sections share (WP-14.12).

   Lifted out of `surfaces/StyleRecord.jsx`, which carried them as module constants and a local
   `Section`, when that surface was split into the dossier's sections. They are one file so the
   sections cannot drift apart in the one respect a reader sees at once: the measure of a line.

   `SectionWord` is a section's own name in a place a `Term` may not sit -- a summary card, a
   strip entry, both anchors. It prints the `section-<id>` record's `term` and writes none. */
import React from 'react';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { useGlossary } from '../api/useGlossary.js';
import { termView } from '../glossary/termView.js';
import { sectionTermId } from './sections.js';

export const prose = { font: 'var(--type-prose)', color: 'var(--text-body)', margin: '0 0 12px', maxWidth: '68ch' };
export const quiet = { font: 'var(--fw-reg) var(--fs-body)/1.55 var(--body)', color: 'var(--text-secondary)', margin: 0, maxWidth: '68ch' };
export const data = { font: 'var(--type-data-s)', color: 'var(--text-secondary)' };

export function Section({ eyebrow, children, style, ...rest }) {
  return (
    <section style={{ marginBottom: 38, ...style }} {...rest}>
      {eyebrow != null && <Eyebrow className="tdl-section-head" style={{ display: 'block' }}>{eyebrow}</Eyebrow>}
      {children}
    </section>
  );
}

/* The word a section is called, from its glossary record; `noEntry` where there is none, and
   nothing while the glossary has not answered. */
export function SectionWord({ id }) {
  const glossary = useGlossary();
  const v = termView(glossary, { id: sectionTermId(id) });
  if (v.state === 'ready') return <>{v.word}</>;
  if (v.state === 'loading') return null;
  return <>{v.text}</>;
}
