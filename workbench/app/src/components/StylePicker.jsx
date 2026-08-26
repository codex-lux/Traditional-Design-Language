/* Choosing one of 164 styles, by typing rather than by scrolling.

   This replaces a <select> holding 164 alphabetical ids. A native select over that many
   options is a scroll to nowhere: you cannot search it beyond the first-letter jump, it
   showed ids rather than names, and on the surfaces that mattered it was the ONLY way to
   change what you were looking at.

   A combobox instead — type a few letters, arrow to it, enter. The same scored matcher
   the palette uses, so "tidewater", "tide" and "georgian tidewater" all behave the same
   way here as there. */
import React from 'react';
import { useStyles } from '../api/useStyles.js';
import { search } from '../search/match.js';

export function StylePicker({ value, onChange, label = 'Style', allowNone, noneLabel = 'no style in view', width = 200 }) {
  const { styles, failed } = useStyles();
  const [open, setOpen] = React.useState(false);
  const [q, setQ] = React.useState('');
  const [cursor, setCursor] = React.useState(0);
  const boxRef = React.useRef(null);
  const inputRef = React.useRef(null);

  const current = styles.find((s) => s.id === value);
  const shown = current ? current.name : (value || '');

  const hits = React.useMemo(() => {
    const pool = styles.map((s) => ({ ...s, kind: 'style', hay: (s.name + ' ' + s.id).toLowerCase() }));
    if (!q.trim()) return pool.slice(0, 60);
    return search(pool, q, 60).hits;
  }, [styles, q]);

  const options = allowNone ? [{ id: '', name: noneLabel }, ...hits] : hits;

  React.useEffect(() => { setCursor(0); }, [q, open]);

  // Close when the focus or the click goes elsewhere.
  React.useEffect(() => {
    if (!open) return undefined;
    const away = (ev) => { if (boxRef.current && !boxRef.current.contains(ev.target)) setOpen(false); };
    document.addEventListener('mousedown', away);
    return () => document.removeEventListener('mousedown', away);
  }, [open]);

  const pick = (opt) => {
    if (!opt) return;
    onChange(opt.id);
    setOpen(false);
    setQ('');
  };

  const onKeyDown = (ev) => {
    if (ev.key === 'ArrowDown') { ev.preventDefault(); setOpen(true); setCursor((c) => Math.min(c + 1, options.length - 1)); }
    else if (ev.key === 'ArrowUp') { ev.preventDefault(); setCursor((c) => Math.max(c - 1, 0)); }
    else if (ev.key === 'Enter') { ev.preventDefault(); pick(options[cursor]); }
    else if (ev.key === 'Escape' && open) { ev.stopPropagation(); setOpen(false); setQ(''); }
  };

  return (
    <span ref={boxRef} style={{ position: 'relative', display: 'inline-flex', alignItems: 'center', flex: 'none' }}>
      {failed && (
        <span title={String(failed)}
          style={{ font: 'var(--type-data-s)', color: 'var(--sev-fatal, var(--ink-3))' }}>
          the style list could not be read
        </span>
      )}
      <input ref={inputRef} type="text" role="combobox" aria-expanded={open} aria-autocomplete="list"
        aria-controls="stylepicker-list" aria-label={label}
        value={open ? q : shown}
        placeholder={allowNone ? noneLabel : 'a style…'}
        onFocus={() => { setOpen(true); setQ(''); }}
        onChange={(e) => { setQ(e.target.value); setOpen(true); }}
        onKeyDown={onKeyDown}
        style={{ width, font: 'var(--type-data)', color: 'var(--ink-2)', padding: '2px 7px',
          background: 'var(--paper-mat)', border: '1px solid ' + (open ? 'var(--gilt-deep)' : 'var(--rule)'),
          outline: 'none' }} />

      {open && (
        <div id="stylepicker-list" role="listbox" aria-label={label}
          style={{ position: 'absolute', top: '100%', left: 0, zIndex: 40, marginTop: 2,
            width: Math.max(width, 260), maxHeight: 320, overflow: 'auto', background: 'var(--paper)',
            border: '1px solid var(--rule)', boxShadow: '0 6px 20px rgba(40,36,28,.18)' }}>
          {options.length === 0 && (
            <p style={{ font: 'var(--fw-reg) 12.5px/1.5 var(--body)', color: 'var(--ink-4)',
              margin: 0, padding: '8px 10px' }}>No style is called that.</p>
          )}
          {options.map((s, i) => {
            const on = i === cursor;
            return (
              <div key={s.id || '__none'} role="option" aria-selected={on}
                onMouseMove={() => setCursor(i)}
                onMouseDown={(e) => { e.preventDefault(); pick(s); }}
                style={{ display: 'flex', alignItems: 'baseline', gap: 8, padding: '3px 10px',
                  cursor: 'pointer', background: on ? 'var(--paper-deep)' : 'transparent',
                  borderLeft: '2px solid ' + (s.id === value ? 'var(--gilt-deep)' : 'transparent') }}>
                <span style={{ font: 'var(--fw-reg) 13px/1.35 var(--body)', color: 'var(--ink)' }}>{s.name}</span>
                <span style={{ flex: 1 }} />
                {s.id && (
                  <span style={{ font: 'var(--type-data-s)', fontFamily: 'var(--mono)', color: 'var(--ink-4)' }}>
                    {s.id}
                  </span>
                )}
              </div>
            );
          })}
        </div>
      )}
    </span>
  );
}
