/* Filter the list in front of you, by typing.

   The palette jumps you across the corpus; this narrows the list you are already reading,
   which is a different need and wants a different thing on screen. 97 slots and 209
   faults were both flat scrolls before.

   It registers itself as the target for `/` while mounted, so the key reaches whichever
   surface is in view without the shell knowing anything about surfaces. Escape clears
   before it closes anything else — clearing the filter is what escape means while you are
   standing in one. */
import React from 'react';
import { registerFilterFocus } from '../keys.js';

export function FilterInput({ value, onChange, label, placeholder, width = 190, count }) {
  const ref = React.useRef(null);

  React.useEffect(() => registerFilterFocus(() => {
    if (ref.current) { ref.current.focus(); ref.current.select(); }
  }), []);

  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 7, flex: 'none' }}>
      <input ref={ref} type="text" value={value || ''} aria-label={label}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Escape' && value) { e.stopPropagation(); onChange(''); }
        }}
        placeholder={placeholder || 'filter'}
        style={{ width, font: 'var(--type-data)', color: 'var(--ink)', padding: '2px 7px',
          background: 'var(--paper-mat)', border: '1px solid var(--rule)', outline: 'none' }} />
      {!value && (
        <span aria-hidden="true" style={{ font: 'var(--type-data-s)', fontFamily: 'var(--mono)',
          color: 'var(--ink-4)' }}>/</span>
      )}
      {value && (
        <>
          {/* What the filter did, said plainly. A list that has quietly gone from 209 rows
              to 3 should say so where the typing happened. */}
          {count != null && (
            <span style={{ font: 'var(--type-data-s)', color: count === 0 ? 'var(--ink-3)' : 'var(--ink-4)' }}>
              {count === 0 ? 'none match' : count}
            </span>
          )}
          <button type="button" onClick={() => onChange('')} aria-label="Clear the filter"
            title="Clear the filter"
            style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)', padding: '0 2px' }}>×</button>
        </>
      )}
    </span>
  );
}
