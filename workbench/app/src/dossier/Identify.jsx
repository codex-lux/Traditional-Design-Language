/* Identify — what the style is, and how to tell it (WP-14.12, PRD §D.1 row 0).

   The identity column of `surfaces/StyleRecord.jsx`, extracted: the description, the diagnostic
   tells (given the room -- they are the job, "is this Federal or Greek Revival?"), the
   distinguished-from cards, the defining characteristics. What changed is only what the record
   already had and did not use: a neighbour in `distinguished_from` is a LINK to that record now,
   through `RecordLink`, instead of a button that knew one kind; and one summary card per other
   section the dossier lists, each with the count the dossier payload gives it. No count here is
   computed or written; every one is the payload's. */
import React from 'react';
import { Term } from '../components/Term.jsx';
import { RecordLink } from '../components/RecordLink.jsx';
import { Section, SectionWord, prose, quiet } from './parts.jsx';
import { sectionAddress } from './sections.js';

/* A `distinguished_from` node is a style id, or `massing:<id>` for a massing -- a different
   namespace, cited as its own kind. */
const citeOfNeighbour = (node) => {
  const n = String(node || '');
  return n.startsWith('massing:') ? n : 'style:' + n;
};

export function Identify({ rec, styleId, cards }) {
  const desc = rec.description || {};
  const tells = rec.diagnostic_tells || [];
  const others = rec.distinguished_from || [];
  const chars = rec.defining_characteristics || [];
  return (
    <div data-dossier-section="identify">
      {desc.short && <p style={{ ...prose, fontStyle: 'italic', color: 'var(--ink-2)', marginTop: 4 }}>{desc.short}</p>}
      {desc.long && String(desc.long).split(/\n\n+/).map((p, i) => <p key={i} style={prose}>{p}</p>)}

      {cards.length > 0 && (
        <nav aria-label="the other sections" style={{ display: 'flex', flexWrap: 'wrap', gap: 10, margin: '18px 0 24px' }}>
          {cards.map((s) => (
            <a key={s.id} href={sectionAddress(styleId, s.id)} data-summary-card={s.id} data-count={s.count}
              style={{ display: 'flex', flexDirection: 'column', gap: 3, minWidth: 128, padding: '9px 12px',
                border: '1px solid var(--rule)', background: 'var(--paper-deep)', textDecoration: 'none' }}>
              <span style={{ font: 'var(--fw-reg) 14px/1.2 var(--display)', color: 'var(--ink)' }}><SectionWord id={s.id} /></span>
              <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)' }}>{s.count}</span>
            </a>
          ))}
        </nav>
      )}

      {tells.length > 0 && (
        <Section eyebrow={<><Term id="diagnostic-tell" /> · {tells.length}</>} style={{ marginTop: 24 }}>
          {tells.map((t, i) => (
            <p key={i} data-tell="" style={{ ...prose, paddingLeft: 14, borderLeft: '2px solid var(--gilt-deep)',
              marginBottom: 9 }}>{typeof t === 'string' ? t : t.tell || t.statement}</p>
          ))}
        </Section>
      )}

      {others.length > 0 && (
        <Section eyebrow="distinguished from · the nearest neighbours">
          {others.map((d, i) => (
            <div key={i} data-distinguished-from={d.node} style={{ border: '1px solid var(--rule)',
              background: 'var(--paper-deep)', padding: '11px 13px', marginBottom: 11 }}>
              <div style={{ font: 'var(--fw-reg) 15px/1.2 var(--display)', marginBottom: 6 }}>
                <RecordLink cite={citeOfNeighbour(d.node)} />
              </div>
              <p style={quiet}>{d.difference}</p>
            </div>
          ))}
        </Section>
      )}

      {chars.length > 0 && (
        <Section eyebrow={<>defining characteristics · {chars.length}</>}>
          {chars.map((c, i) => (
            <p key={i} style={{ ...quiet, marginBottom: 7 }}>· {c}</p>
          ))}
        </Section>
      )}
    </div>
  );
}
