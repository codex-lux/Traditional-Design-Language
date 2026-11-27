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
import { PeriodBar } from './PeriodBar.jsx';

/* A `distinguished_from` node is a style id, or `massing:<id>` for a massing -- a different
   namespace, cited as its own kind. */
const citeOfNeighbour = (node) => {
  const n = String(node || '');
  return n.startsWith('massing:') ? n : 'style:' + n;
};

/* `period` is the DOSSIER's (`GET /api/styles/{id}/dossier`), the record's own block. Until
   26 Nov 2026 this read `rec.period`, a key `GET /api/styles/{id}` has never served, so the bar
   below was drawn for no style at all. */
export function Identify({ rec, period, styleId, cards }) {
  const desc = rec.description || {};
  const tells = rec.diagnostic_tells || [];
  const others = rec.distinguished_from || [];
  const chars = rec.defining_characteristics || [];
  return (
    <div data-dossier-section="identify">
      {/* The period, drawn; then the tells and the neighbours, which are the job, BEFORE the
          description (Phase 17, board 7). */}
      <PeriodBar period={period} />

      {tells.length > 0 && (
        <Section eyebrow={<><Term id="diagnostic-tell" /> · {tells.length}</>} style={{ marginTop: 34 }}>
          <ol className="tdl-numbered">
            {tells.map((t, i) => (
              <li key={i} data-tell="">{typeof t === 'string' ? t : t.tell || t.statement}</li>
            ))}
          </ol>
        </Section>
      )}

      {others.length > 0 && (
        <Section eyebrow="distinguished from · the nearest neighbours">
          <div className="tdl-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(19rem, 1fr))' }}>
            {others.map((d, i) => (
              <div key={i} data-distinguished-from={d.node} className="tdl-neighbour">
                <div style={{ font: 'var(--fw-med) 18px/1.2 var(--display)', marginBottom: 8 }}>
                  <RecordLink cite={citeOfNeighbour(d.node)} />
                </div>
                <p style={quiet}>{d.difference}</p>
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* The short description is the page's lede, in the dossier's head; the long one is here. */}
      {desc.long && (
        <div data-description="" style={{ margin: '0 0 38px' }}>
          {String(desc.long).split(/\n\n+/).map((p, i) => <p key={i} style={prose}>{p}</p>)}
        </div>
      )}

      {chars.length > 0 && (
        <Section eyebrow={<>defining characteristics · {chars.length}</>}>
          <ul style={{ listStyle: 'none', margin: 0, padding: 0, columns: '2 22rem', columnGap: 36 }}>
            {chars.map((c, i) => (
              <li key={i} style={{ ...quiet, padding: '5px 0 5px 16px', position: 'relative', breakInside: 'avoid' }}>
                <span aria-hidden="true" style={{ position: 'absolute', left: 0 }}>·</span>{c}
              </li>
            ))}
          </ul>
        </Section>
      )}

      {/* ONWARD: one card per other section the dossier lists, with the payload's count. They led
          the page until 26 Nov 2026, above the tells, saying what the section strip already said;
          they close it now, as the way on from here. */}
      {cards.length > 0 && (
        <nav aria-label="the other sections" className="tdl-onward" style={{ marginTop: 8 }}>
          {cards.map((s) => (
            <a key={s.id} href={sectionAddress(styleId, s.id)} data-summary-card={s.id} data-count={s.count}>
              <span style={{ font: 'var(--fw-reg) 17px/1.2 var(--display)', color: 'var(--text-body)' }}><SectionWord id={s.id} /></span>
              <span style={{ font: 'var(--type-data-s)', color: 'var(--text-secondary)' }}>{s.count}</span>
            </a>
          ))}
        </nav>
      )}
    </div>
  );
}
