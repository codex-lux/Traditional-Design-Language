/* The pieces every record page shares (WP-14.23).

   A record page is headed by the shell's `PageHead`, whose eyebrow is the KIND (`surface-room`,
   `surface-massing` ... tranche 2 §B.4); below it `RecordHead` gives the record's own name first,
   its id as a Courier margin note, and the other names the record itself lists. Every section
   heading is a glossary record's word through `Term`; every other word on these pages is the
   record's own. */
import React from 'react';
import { RecordLink } from '../components/RecordLink.jsx';
import { useNames } from '../names/useNames.js';
import { prose, quiet, data } from '../dossier/parts.jsx';

export { Section, prose, quiet, data } from '../dossier/parts.jsx';

export function RecordHead({ name, id, aka, meta }) {
  const others = Array.isArray(aka) ? aka.filter((a) => typeof a === 'string' && a.trim()) : [];
  return (
    <div data-record-head={id} style={{ marginBottom: 18 }}>
      <h2 style={{ font: 'var(--fw-reg) var(--fs-d2, 28px)/1.1 var(--display)', letterSpacing: 'var(--tr-display)',
        margin: '0 0 4px' }}>
        {name || id}<span className="tdl-record-note">{id}</span>
      </h2>
      {others.length > 0 && <p style={{ ...quiet, fontStyle: 'italic' }}>{others.join(' · ')}</p>}
      {meta && <p style={{ ...data, margin: '4px 0 0' }}>{meta}</p>}
    </div>
  );
}

/* A citation drawn as a link where the corpus holds the record, and as the record's own token
   where it does not: a room record's adjacency may name a circulation type rather than a room,
   and a link to a page that does not exist is worse than a word that says it is not one. */
export function KnownLink({ cite, children }) {
  const names = useNames();
  if (names.status === 'ready' && !names.index.has(cite)) {
    return <span style={data} data-not-a-record={cite}>{cite.slice(cite.indexOf(':') + 1)}</span>;
  }
  return <RecordLink cite={cite}>{children}</RecordLink>;
}

/* A paragraph of the record's own prose, or nothing. */
export function Prose({ text, ...rest }) {
  if (typeof text !== 'string' || !text.trim()) return null;
  return <p style={prose} {...rest}>{text}</p>;
}

/* A list of links, one per row, each with an optional note of the record's own. */
export function LinkRows({ rows, attr }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
      {rows.map((r) => (
        <div key={r.cite} {...{ [attr]: r.id }} style={{ display: 'flex', gap: 10, alignItems: 'baseline', flexWrap: 'wrap' }}>
          <KnownLink cite={r.cite}>{r.name}</KnownLink>
          {r.aside}
          {r.note && <span style={{ ...quiet, fontSize: 12.5 }}>{r.note}</span>}
        </div>
      ))}
    </div>
  );
}

/* Reading, failed, or the record: one frame for all five pages. */
export function Reading({ error, cite, children, ready }) {
  if (error) {
    return (
      <p style={quiet} data-record-error={cite}>
        {error.status === 404 ? <>The corpus holds no record <code>{cite}</code>.</> : <>The record could not be read.</>}
      </p>
    );
  }
  if (!ready) return <p style={data}>reading the record…</p>;
  return children;
}
