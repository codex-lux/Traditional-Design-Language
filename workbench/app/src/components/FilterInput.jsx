/* Filter the list in front of you, by typing.

   The palette jumps you across the corpus; this narrows the list you are already reading,
   which is a different need and wants a different thing on screen. 97 slots and 209
   faults were both flat scrolls before.

   It registers itself as the target for `/` while mounted, so the key reaches whichever
   surface is in view without the shell knowing anything about surfaces. Escape clears
   before it closes anything else — clearing the filter is what escape means while you are
   standing in one.

   TYPING IS NOT NAVIGATING, which is why the value is debounced. Filters live in the URL,
   so every keystroke used to write history and re-render the surface underneath: on the
   Phylogeny's map reading that meant a full placement pass per character (17.9 ms measured),
   and in Safari it counted against a hard rate limit on replaceState that throws once passed.
   The field stays instant because it holds its own draft; the URL and the filtering catch up
   a beat later. Found by an adversarial audit. */
import React from 'react';
import { registerFilterFocus } from '../keys.js';

const DEBOUNCE_MS = 160;

export function FilterInput({ value, onChange, label, placeholder, width = 190, count }) {
  const ref = React.useRef(null);
  const [draft, setDraft] = React.useState(value || '');
  const timer = React.useRef(null);

  // An external change — clear-all, a pasted URL, leaving the surface — wins over the draft.
  React.useEffect(() => { setDraft(value || ''); }, [value]);
  React.useEffect(() => () => clearTimeout(timer.current), []);

  const push = React.useCallback((v) => {
    setDraft(v);
    clearTimeout(timer.current);
    timer.current = setTimeout(() => onChange(v), DEBOUNCE_MS);
  }, [onChange]);

  const clear = React.useCallback(() => {
    clearTimeout(timer.current);
    setDraft('');
    onChange('');
  }, [onChange]);

  React.useEffect(() => registerFilterFocus(() => {
    if (ref.current) { ref.current.focus(); ref.current.select(); }
  }), []);

  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 7, flex: 'none' }}>
      <input ref={ref} type="text" value={draft} aria-label={label}
        onChange={(e) => push(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Escape' && draft) { e.stopPropagation(); clear(); }
        }}
        placeholder={placeholder || 'filter'}
        style={{ width, font: 'var(--type-data)', color: 'var(--ink)', padding: '2px 7px',
          background: 'var(--paper-mat)', border: '1px solid var(--rule)', outline: 'none' }} />
      {!draft && (
        <span aria-hidden="true" style={{ font: 'var(--type-data-s)', fontFamily: 'var(--mono)',
          color: 'var(--ink-4)' }}>/</span>
      )}
      {draft && (
        <>
          {/* What the filter did, said plainly. A list that has quietly gone from 209 rows
              to 3 should say so where the typing happened. The count follows the committed
              value, not the draft, so it never contradicts the list below it. */}
          {count != null && value === draft && (
            <span style={{ font: 'var(--type-data-s)', color: count === 0 ? 'var(--ink-3)' : 'var(--ink-4)' }}>
              {count === 0 ? 'none match' : count}
            </span>
          )}
          <button type="button" onClick={clear} aria-label="Clear the filter"
            title="Clear the filter"
            style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)', padding: '0 2px' }}>×</button>
        </>
      )}
    </span>
  );
}
