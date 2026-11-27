/* The pieces every record page shares (WP-14.23).

   `RecordHead` gives the record's own name at display size, its id printed once beside it (the
   one place a record's page prints it, ruled 26 Nov 2026), and the other names the record itself
   lists; the kind and the record's one categorical word stand over it in the letter. Every section
   heading is a glossary record's word through `Term`; every other word on these pages is the
   record's own. */
import React from 'react';
import { RecordLink } from '../components/RecordLink.jsx';
import { useNames } from '../names/useNames.js';
import { prose, quiet, data } from '../dossier/parts.jsx';

export { Section, prose, quiet, data } from '../dossier/parts.jsx';

export function RecordHead({ name, id, aka, meta, kicker }) {
  const others = Array.isArray(aka) ? aka.filter((a) => typeof a === 'string' && a.trim()) : [];
  return (
    <header data-record-head={id} className="tdl-hero tdl-rise" style={{ marginBottom: 34 }}>
      {(kicker || meta) && (
        <div className="tdl-hero-kicker">
          {kicker}
          {kicker && meta ? <span aria-hidden="true">·</span> : null}
          {meta ? <span data-record-meta="">{meta}</span> : null}
        </div>
      )}
      <h2 className="tdl-record-title">
        {name || id}<span className="tdl-record-id" data-record-id="">{id}</span>
      </h2>
      {others.length > 0 && <p className="tdl-aka">{others.join(' · ')}</p>}
      <div className="tdl-rule-double" style={{ marginTop: 26 }} />
    </header>
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
export function Prose({ text, lede, ...rest }) {
  if (typeof text !== 'string' || !text.trim()) return null;
  return <p className={lede ? 'tdl-lede' : undefined} style={lede ? undefined : prose} {...rest}>{text}</p>;
}

/* A list of links, one per row, each with an optional note of the record's own. */
export function LinkRows({ rows, attr }) {
  const reasoned = rows.some((r) => r.note);
  if (!reasoned) {
    return (
      <div className="tdl-columns">
        {rows.map((r) => (
          <div key={r.cite} {...{ [attr]: r.id }} className="tdl-index-row">
            <KnownLink cite={r.cite}>{r.name}</KnownLink>
            {r.aside}
          </div>
        ))}
      </div>
    );
  }
  return (
    <div>
      {rows.map((r) => (
        <div key={r.cite} {...{ [attr]: r.id }} className="tdl-reason-row">
          <span className="tdl-reason-name"><KnownLink cite={r.cite}>{r.name}</KnownLink>{r.aside}</span>
          {r.note ? <p className="tdl-reason">{r.note}</p> : <span />}
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
