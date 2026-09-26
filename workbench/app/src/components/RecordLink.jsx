/* A LINK TO A RECORD: ITS NAME FIRST, ITS ID IN THE MARGIN (WP-14.8, PRD §I.3).

   <RecordLink cite="pack:trim-classical" ctx={{ style: 'tidewater-georgian' }} />

   The workbench printed machine ids where the corpus serves names. This draws a citation the
   way a practitioner reads one: the record's name in the serif, from the search index the
   palette already reads (`names/useNames.js`), then the id as a Courier margin note in ink-2 —
   present, because the id is what a reader cites, and second, because it is not what the thing
   is called. `children` replaces the name only; the id still stands beside it.

   IT IS A REAL ANCHOR WITH A REAL HREF, so a middle click, a ⌘-click and "copy link" all work;
   a plain primary click is intercepted and goes through `nav.cite(cite, ctx)`, the one entry
   point every cross-record link shares, so the context this page carries (a style, into a
   surface that honours one — `router.js`'s CONTEXT_KEYS) travels exactly as a rail chip's would.
   The href and the click land in one place because both are `router.js`'s composition.

   A citation the router cannot read is plain text with `data-unresolved`, never an anchor: a
   link to nowhere that looks like a link is worse than a word that says it is not one. The
   decisions are `names/recordLink.js`'s, pure and tested; this file draws them. */
import React from 'react';
import { nav } from '../state/nav.js';
import { useNames } from '../names/useNames.js';
import { linkView, isPlainPrimaryClick } from '../names/recordLink.js';

export function RecordLink({ cite, ctx, children }) {
  const names = useNames();
  const v = linkView(cite, ctx, names.index);
  const label = children ?? v.name;
  if (!v.href) {
    return (
      <span className="tdl-record-link" data-unresolved="" data-cite={cite}>
        <span className="tdl-record-name">{label}</span>
      </span>
    );
  }
  const onClick = (ev) => {
    if (!isPlainPrimaryClick(ev)) return;
    ev.preventDefault();
    nav.cite(cite, ctx);
  };
  return (
    <span className="tdl-record-link">
      <a className="tdl-record-name" href={v.href} data-cite={cite} onClick={onClick}>{label}</a>
      {v.note && <span className="tdl-record-note">{v.note}</span>}
    </span>
  );
}
