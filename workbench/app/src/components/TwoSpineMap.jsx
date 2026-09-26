/* THE TWO SPINES AND THE LIBRARY, DRAWN AS RULED ROWS OF LINKS (WP-14.14, PRD §F).

   The front door shows the whole workbench once, the way the rail holds it, so the navigation is
   learned on arrival rather than by clicking round it: a ruled row per group — the front door, the
   styles, a house in its five steps, the library — and in each row that group's places as links,
   with the step numbers and the live figures the rail shows beside them.

   IT IS THE SITE MAP, NOT A PICTURE OF ONE. Every row and every link is `frontdoor/spineMap.js`'s
   reading of the `navModel()` it is handed, so the rail and this map cannot come to disagree about
   what a place is called, where it goes or which group it is in — which is exactly how the three
   catalogues this replaces went wrong. There is no address, surface id, record id or label in this
   file; `src/frontDoor.test.mjs` reads it to keep it so. Links, not a drawing engine: an `<a>`
   with a real href is a place a reader can open in a new tab, copy, and read with a screen reader,
   and a diagram would have to re-derive the same table to draw it.

   A group heading is a `Term` (the group's own record, and its definition on a click). A link may
   not hold a Term (a button inside an anchor is not valid HTML), so a link carries its record's
   definition as `aria-describedby` and a title instead (`useTermDescription`, PRD §I.1). A record
   the glossary lacks is printed as `noEntry(id)`, visibly, as the rail prints it. */
import React from 'react';
import { mapRows } from '../frontdoor/spineMap.js';
import { Term, noEntry, useTermDescription } from './Term.jsx';

/* One cell per top-level item, holding the items nested under it (Trace a drawing under the Plan
   step), so a row reads left to right and a nested place stays beside its parent. */
function cellsOf(items) {
  const cells = [];
  for (const it of items) {
    if (it.depth === 0 || !cells.length) cells.push([it]);
    else cells[cells.length - 1].push(it);
  }
  return cells;
}

function Label({ it }) {
  if (it.label) return <span>{it.label}</span>;
  if (it.missing) return <span data-missing="" style={{ font: 'var(--type-data-s)' }}>{noEntry(it.missing)}</span>;
  return null;
}

function Inner({ it }) {
  return (
    <>
      {it.step != null && (
        <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)', marginRight: 6 }}>{it.step}</span>
      )}
      <Label it={it} />
      {it.meta != null && (
        <span data-meta="" style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)', marginLeft: 7 }}>
          {String(it.meta)}
        </span>
      )}
    </>
  );
}

const linkStyle = (it) => ({
  display: 'inline-block',
  font: it.depth > 0 ? 'var(--fw-reg) var(--fs-body-s)/1.35 var(--serif)' : 'var(--fw-reg) var(--fs-body)/1.35 var(--serif)',
  color: 'var(--ink)',
  textDecoration: 'none',
  borderBottom: it.current ? '2px solid var(--gilt-deep)' : '1px solid var(--link-underline)',
  paddingBottom: 1,
});

function DescribedLink({ it }) {
  const d = useTermDescription(it.termId);
  return (
    <>
      <a href={it.href} data-map-item={it.id} aria-current={it.current ? 'page' : undefined}
        aria-describedby={d.describedBy} title={d.title} style={linkStyle(it)}>
        <Inner it={it} />
      </a>
      {d.element}
    </>
  );
}

function PlainLink({ it }) {
  return (
    <a href={it.href} data-map-item={it.id} aria-current={it.current ? 'page' : undefined}
      style={linkStyle(it)}>
      <Inner it={it} />
    </a>
  );
}

function MapLink({ it }) {
  const link = it.termId ? <DescribedLink it={it} /> : <PlainLink it={it} />;
  return (
    <div style={{ marginLeft: it.depth > 0 ? 14 : 0, marginTop: it.depth > 0 ? 4 : 0 }}>
      {link}
      {/* names first, the id as a margin note — only for a place named by its record's name */}
      {it.note && <span className="tdl-record-note">{it.note}</span>}
    </div>
  );
}

export function TwoSpineMap({ model }) {
  const rows = mapRows(model);
  return (
    <dl data-spine-map="" style={{ margin: 0 }}>
      {rows.map((row) => (
        <div key={row.id} data-spine-row={row.id} style={{
          display: 'grid', gridTemplateColumns: 'minmax(5.5rem, 7.5rem) 1fr', gap: '4px 16px',
          padding: '10px 0 11px', borderTop: '1px solid var(--rule-soft)', alignItems: 'baseline',
        }}>
          <dt style={{ font: 'var(--type-eyebrow)', letterSpacing: 'var(--tr-eyebrow)',
            textTransform: 'uppercase', color: 'var(--ink-2)' }}>
            {row.termId ? <Term id={row.termId} /> : null}
          </dt>
          <dd style={{ margin: 0, display: 'flex', flexWrap: 'wrap', gap: '6px 22px', minWidth: 0 }}>
            {cellsOf(row.items).map((cell) => (
              <div key={cell[0].id} data-map-cell={cell[0].id}>
                {cell.map((it) => <MapLink key={it.id} it={it} />)}
              </div>
            ))}
          </dd>
        </div>
      ))}
    </dl>
  );
}

export default TwoSpineMap;
