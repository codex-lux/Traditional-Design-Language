/* The one place you can type a name and arrive at the thing.

   It dispatches by citation, never by surface-plus-guess: every corpus result carries a
   `cite`, and clicking one calls the same nav.cite() the rail's chips call. So the
   palette cannot reach a place a citation could not name, and the citation is shown in
   the row — after a few visits you have learned the grammar without being taught it,
   which is the same grammar the rail speaks and the URL serializes.

   Drawn in the tokens vocabulary: paper, one hairline, EB Garamond for names, Courier
   Prime for ids. No shadow beyond the wash the frame already uses. */
import React from 'react';
import { api } from '../api/client.js';
import { nav } from '../state/nav.js';
import { search, KIND_ORDER } from '../search/match.js';
import { STATIC_ENTRIES } from '../search/staticEntries.js';
import { Eyebrow } from '../components/Eyebrow.jsx';

const KIND_LABEL = {
  surface: 'surfaces', action: 'actions', style: 'styles', slot: 'element slots',
  pack: 'proportion packs', fault: 'faults', room: 'rooms', massing: 'massings',
  parti: 'partis', grouping: 'groupings', kit: 'kits',
};

/* What to show before anything is typed: the surfaces, in rail order. An empty palette
   that says nothing teaches nothing. */
const OPENING_HAND = STATIC_ENTRIES.filter((e) => e.kind === 'surface');

export function CommandPalette({ open, onClose, onAction }) {
  const [q, setQ] = React.useState('');
  const [cursor, setCursor] = React.useState(0);
  const [entries, setEntries] = React.useState(null);   // null = not fetched yet
  const [failed, setFailed] = React.useState(false);
  const inputRef = React.useRef(null);
  const listRef = React.useRef(null);

  /* Fetched once, on first open — 665 records is a lot to carry for a session that
     never searches, and nothing to carry for one that does. */
  React.useEffect(() => {
    if (!open || entries || failed) return;
    let live = true;
    api.searchIndex()
      .then((ix) => { if (live) setEntries(ix.entries || []); })
      .catch(() => { if (live) setFailed(true); });
    return () => { live = false; };
  }, [open, entries, failed]);

  React.useEffect(() => {
    if (open) {
      setQ(''); setCursor(0);
      // after paint, or the input is not in the document yet
      const t = setTimeout(() => inputRef.current && inputRef.current.focus(), 0);
      return () => clearTimeout(t);
    }
    return undefined;
  }, [open]);

  const pool = React.useMemo(
    () => [...STATIC_ENTRIES, ...(entries || [])],
    [entries],
  );

  const result = React.useMemo(() => {
    if (!q.trim()) return { hits: OPENING_HAND, total: OPENING_HAND.length, cut: 0 };
    return search(pool, q, 40);
  }, [pool, q]);

  const hits = result.hits;
  React.useEffect(() => { setCursor(0); }, [q]);

  /* Keep the cursor in view without scrolling the page behind it. */
  React.useEffect(() => {
    const el = listRef.current && listRef.current.querySelector('[data-on="1"]');
    if (el && el.scrollIntoView) el.scrollIntoView({ block: 'nearest' });
  }, [cursor, q]);

  const dispatch = React.useCallback((entry) => {
    if (!entry) return;
    onClose();
    if (entry.cite) nav.cite(entry.cite);
    else if (entry.surface) nav.go(entry.surface);
    else if (entry.run && onAction) onAction(entry.run);
  }, [onClose, onAction]);

  const onKeyDown = (ev) => {
    if (ev.key === 'ArrowDown') {
      ev.preventDefault(); setCursor((c) => Math.min(c + 1, hits.length - 1));
    } else if (ev.key === 'ArrowUp') {
      ev.preventDefault(); setCursor((c) => Math.max(c - 1, 0));
    } else if (ev.key === 'Enter') {
      ev.preventDefault(); dispatch(hits[cursor]);
    } else if (ev.key === 'Home') {
      ev.preventDefault(); setCursor(0);
    } else if (ev.key === 'End') {
      ev.preventDefault(); setCursor(Math.max(0, hits.length - 1));
    }
    // Escape is handled globally in keys.js, so it closes from anywhere in the dialog.
  };

  if (!open) return null;

  // Group headers, in the reader's order rather than by score, while the rows inside
  // stay in score order.
  const groups = [];
  const seen = {};
  hits.forEach((h, i) => {
    if (!seen[h.kind]) { seen[h.kind] = []; groups.push([h.kind, seen[h.kind]]); }
    seen[h.kind].push({ ...h, _i: i });
  });
  groups.sort((a, b) => KIND_ORDER.indexOf(a[0]) - KIND_ORDER.indexOf(b[0]));

  return (
    <div role="presentation" onMouseDown={(e) => { if (e.target === e.currentTarget) onClose(); }}
      style={{ position: 'fixed', inset: 0, zIndex: 60, background: 'var(--wash-2, rgba(40,36,28,.28))',
        display: 'flex', justifyContent: 'center', alignItems: 'flex-start', paddingTop: '11vh' }}>
      <div role="dialog" aria-modal="true" aria-label="Search the corpus"
        style={{ width: 'min(620px, calc(100vw - 32px))', maxHeight: '74vh', display: 'flex',
          flexDirection: 'column', background: 'var(--paper)', border: '1px solid var(--rule)',
          boxShadow: '0 10px 34px rgba(40,36,28,.24)' }}>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '11px 14px',
          borderBottom: '1px solid var(--rule)' }}>
          <Eyebrow tone="secondary" as="span">find</Eyebrow>
          <input ref={inputRef} value={q} onChange={(e) => setQ(e.target.value)} onKeyDown={onKeyDown}
            role="combobox" aria-expanded="true" aria-controls="palette-list" aria-autocomplete="list"
            aria-activedescendant={hits[cursor] ? `palette-opt-${cursor}` : undefined}
            aria-label="Search styles, slots, faults, packs, rooms and surfaces"
            placeholder="a style, a slot, a fault, a room, a surface…"
            style={{ flex: 1, font: 'var(--fw-reg) 16px/1.3 var(--body)', color: 'var(--ink)',
              background: 'transparent', border: 'none', outline: 'none' }} />
          {entries === null && !failed && (
            <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)' }}>reading the corpus…</span>
          )}
        </div>

        <div ref={listRef} id="palette-list" role="listbox" aria-label="Results"
          style={{ overflow: 'auto', minHeight: 0, padding: '6px 0 8px' }}>

          {failed && (
            <p style={{ font: 'var(--fw-reg) 13px/1.5 var(--body)', color: 'var(--ink-3)',
              margin: 0, padding: '12px 16px' }}>
              The index could not be read, so this is searching the surfaces only — not the
              corpus. Nothing is missing from the corpus itself; this palette simply cannot
              see it right now.
            </p>
          )}

          {!hits.length && (
            <p style={{ font: 'var(--fw-reg) 13px/1.55 var(--body)', color: 'var(--ink-3)',
              margin: 0, padding: '14px 16px' }}>
              Nothing in the corpus is called that.
              {entries !== null && (
                <>
                  {' '}This searches names, ids and akas — not the prose. For a phrase from a
                  tell or a remedy, ask the rail.
                </>
              )}
            </p>
          )}

          {groups.map(([kind, rows]) => (
            <div key={kind} role="group" aria-label={KIND_LABEL[kind] || kind}>
              <Eyebrow style={{ padding: '9px 16px 4px' }}>{KIND_LABEL[kind] || kind}</Eyebrow>
              {rows.map((h) => {
                const on = h._i === cursor;
                return (
                  <div key={h.cite || h.id} id={`palette-opt-${h._i}`} role="option" aria-selected={on}
                    data-on={on ? '1' : '0'}
                    onMouseMove={() => setCursor(h._i)}
                    onMouseDown={(e) => { e.preventDefault(); dispatch(h); }}
                    style={{ display: 'flex', alignItems: 'baseline', gap: 10, padding: '5px 16px',
                      cursor: 'pointer', background: on ? 'var(--paper-deep)' : 'transparent',
                      borderLeft: on ? '2px solid var(--gilt-deep)' : '2px solid transparent' }}>
                    <span style={{ font: (on ? 'var(--fw-med)' : 'var(--fw-reg)') + ' 14px/1.35 var(--body)',
                      color: 'var(--ink)', flex: 'none' }}>{h.name}</span>
                    {h.short && (
                      <span style={{ font: 'var(--fw-reg) 12px/1.4 var(--body)', color: 'var(--ink-4)',
                        flex: 1, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap' }}>{h.short}</span>
                    )}
                    {!h.short && <span style={{ flex: 1 }} />}
                    {h.meta && (
                      <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)', flex: 'none' }}>
                        {h.meta}
                      </span>
                    )}
                    {/* The citation, shown plainly. It is the address of this thing
                        everywhere else in the product — here is where you meet it. */}
                    {h.cite && (
                      <span style={{ font: 'var(--type-data-s)', fontFamily: 'var(--mono)',
                        color: on ? 'var(--gilt-deep)' : 'var(--ink-4)', flex: 'none' }}>{h.cite}</span>
                    )}
                  </div>
                );
              })}
            </div>
          ))}

          {result.cut > 0 && (
            <p style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)', margin: 0,
              padding: '9px 16px 2px' }}>
              {result.total} match — {result.cut} more not listed. Type more of the name.
            </p>
          )}
        </div>

        <div style={{ flex: 'none', display: 'flex', gap: 16, padding: '7px 14px',
          borderTop: '1px solid var(--rule)', font: 'var(--type-data-s)', color: 'var(--ink-4)' }}>
          <span>↑↓ move</span><span>↵ open</span><span>esc close</span>
          <span style={{ flex: 1 }} />
          <span>names and ids, not prose</span>
        </div>
      </div>
    </div>
  );
}
