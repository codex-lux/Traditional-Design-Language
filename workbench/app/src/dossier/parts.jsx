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

export const prose = { font: 'var(--fw-reg) 14px/1.62 var(--body)', color: 'var(--ink)', margin: '0 0 10px', maxWidth: '74ch' };
export const quiet = { font: 'var(--fw-reg) 13px/1.55 var(--body)', color: 'var(--ink-2)', margin: 0, maxWidth: '72ch' };
export const data = { font: 'var(--type-data-s)', color: 'var(--ink-2)' };

export function Section({ eyebrow, children, style, ...rest }) {
  return (
    <section style={{ marginBottom: 26, ...style }} {...rest}>
      {eyebrow != null && <Eyebrow style={{ marginBottom: 9 }}>{eyebrow}</Eyebrow>}
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
