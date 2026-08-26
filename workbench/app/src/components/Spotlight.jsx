/* "You searched for this; here is where it lives."

   The palette indexes 665 named things and dispatches every one by citation. Four kinds —
   room, massing, parti, grouping — route to a surface that has no detail view for them, so
   `routeCite` handed over a selection key nothing read: 138 of 665 results dumped the reader
   on an unrelated surface showing whatever had been there before, indistinguishable from a
   search that did nothing. An adversarial audit found it; `test_search_index.py` had passed
   throughout because it only checked that the ids exist server-side.

   Building four detail surfaces is not this fix. Saying plainly what was asked for, where it
   sits, and what this surface can show of it — that is, and it is the same discipline the rest
   of the product uses for a thing it cannot draw. The alternative considered and rejected was
   dropping those 117 records from the index: a corpus you cannot search is worse than one that
   admits where its records are only named. */
import React from 'react';
import { Eyebrow } from './Eyebrow.jsx';

export function Spotlight({ kind, id, note, onDismiss }) {
  if (!id) return null;
  return (
    <div style={{ margin: '10px 14px 0', padding: '9px 12px', border: '1px solid var(--rule)',
      background: 'var(--paper-deep)', display: 'flex', alignItems: 'baseline', gap: 10 }}>
      <Eyebrow tone="accent" as="span">searched</Eyebrow>
      <span style={{ font: 'var(--type-data)', color: 'var(--ink)' }}>
        <span style={{ fontFamily: 'var(--mono)', color: 'var(--ink-3)' }}>{kind}:</span>{id}
      </span>
      <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-3)', flex: 1 }}>{note}</span>
      {onDismiss && (
        <button type="button" onClick={onDismiss}
          style={{ font: 'var(--type-data-s)', color: 'var(--gilt-deep)' }}>dismiss</button>
      )}
    </div>
  );
}
