/* THE CONFLICT SET, WHERE THE PLATE WOULD BE (WP-13.4).

   Lucas ruled on 15 Sep 2026 that a placement breaking a hard fact of the type is REFUSED, not
   drawn, and that the bench shows the conflict set: the brief or the parti is what changes.
   This is what stands in the plate's place. It is NOT a toast and NOT a red banner — same
   rectangle, same weight, same padding as a result, on `components/RefusalCard.jsx`'s
   precedent, because a refusal is content and not an error.

   IT RENDERS THREE STATES AND NEVER COLLAPSES THEM.

     a refusal   the server's own verdict (`build/typefacts.py::refusal`), read through
                 `sheet/refusal.js` and re-derived nowhere. Nothing is drawn beside it.
     infeasible  a `geometry_report.infeasible` block on a record from a server that does not
                 yet answer the refusal contract. It is the conflict set WP-2.3 has always
                 shown, and `drawnBelow` decides whether it may say a drawing is below it —
                 that sentence was unconditional before this package and becomes a lie the
                 moment a surface stops drawing (WP-6.4's rule, in its own panel).
     neither     nothing renders. A panel that appears with nothing in it reads as "not much
                 wrong", which is the shape a refusal must never take.

   WHAT IT NAMES IS PUBLISHED, NOT ONLY PRINTED. `data-conflict-set`, `data-refusal-kind`,
   `data-refusal-facts` and `data-refusal-lines` carry what this panel decided, so
   `e2e/walk.mjs` reads the count rather than matching a phrase: a guard that reads a selector
   or a wording rather than a property is this repository's most-repeated way of going blind,
   and WP-13.2's own engine check had gone red on a rewording for exactly that reason.

   AND IT SAYS WHEN IT NAMES NOTHING. `namesSomething` is false where the refusal carries no
   fact, no conflict and no sentence — a bare error wearing the word "refused" — and the panel
   prints that in as many words instead of showing an empty rule. Likewise `unstatedConflicts`
   counts the entries no sentence covers, so four sentences over six conflicts cannot read as
   six. */
import React from 'react';
import { Eyebrow } from './Eyebrow.jsx';
import { conflictLines, unstatedConflicts, namesSomething, refusalHeadline } from '../sheet/refusal.js';

const PANEL = {
  border: '1px solid var(--rule)',
  borderLeft: '2px solid var(--refusal)',
  background: 'var(--paper)',
  padding: '14px 16px',
  maxWidth: 1000,
  margin: '0 0 14px',
};
const LEAD = { font: 'var(--fw-reg) 13.5px/1.6 var(--body)', color: 'var(--ink)', margin: '7px 0 0' };
const LIST = { font: 'var(--fw-reg) 12.5px/1.6 var(--body)', color: 'var(--ink-2)',
  margin: '8px 0 0', paddingLeft: 18 };
const FINE = { font: 'var(--type-data-s)', color: 'var(--ink-2)', margin: '9px 0 0' };

export function ConflictSet({ refusal, infeasible, drawnBelow = false, where = 'the drawing', note }) {
  if (refusal) {
    const lines = conflictLines(refusal);
    const unstated = unstatedConflicts(refusal);
    const named = namesSomething(refusal);
    return (
      <div data-conflict-set="refusal" data-refusal-kind={refusal.kind}
        data-refusal-facts={refusal.facts.length} data-refusal-lines={lines.length}
        data-refusal-unstated={unstated} style={PANEL}>
        <Eyebrow tone="secondary">
          {where} is refused — {refusalHeadline(refusal)}
        </Eyebrow>
        {refusal.error && <p style={LEAD}>{refusal.error}</p>}
        {refusal.facts.length > 0 && (
          <p style={{ ...FINE, color: 'var(--ink-2)' }}>
            hard fact{refusal.facts.length === 1 ? '' : 's'} of the type not held:{' '}
            <span style={{ fontFamily: 'var(--mono)' }}>{refusal.facts.join(', ')}</span>
          </p>
        )}
        {lines.length > 0 && (
          <ul style={LIST}>{lines.map((l, i) => <li key={i}>{l}</li>)}</ul>
        )}
        {unstated > 0 && (
          <p style={FINE}>
            and {unstated} further conflict{unstated === 1 ? '' : 's'} the refusal states no
            sentence for.
          </p>
        )}
        {!named && (
          <p style={FINE}>
            This refusal names no fact, no conflict and no sentence. That is a defect in the
            refusal, not a small refusal: it is being shown as it arrived rather than dressed up.
          </p>
        )}
        <p style={FINE}>
          Nothing is drawn from this placement. The record still carries the search&rsquo;s
          least-bad arrangement — it is what the conflict set above is an explanation of — and no
          surface draws it and no export may take it.{' '}
          <strong>The brief or the parti is what changes.</strong>
          {refusal.engine
            ? ` Refused on ${refusal.engine === 'cp-sat' ? 'the proof (CP-SAT)' : refusal.engine}${refusal.status ? `, ${refusal.status}` : ''}.`
            : ''}
        </p>
        {note && <p style={FINE}>{note}</p>}
      </div>
    );
  }

  if (infeasible) {
    const conflicts = Array.isArray(infeasible.conflicts) ? infeasible.conflicts : [];
    return (
      <div data-conflict-set="infeasible" data-refusal-kind="" data-refusal-facts={0}
        data-refusal-lines={conflicts.length} style={{ ...PANEL, borderLeft: '2px solid var(--sev-serious)' }}>
        <Eyebrow tone="secondary">
          infeasible as declared — proven ({conflicts.length} conflict{conflicts.length === 1 ? '' : 's'})
        </Eyebrow>
        <ul style={LIST}>
          {conflicts.map((c, i) => <li key={i}>{typeof c === 'string' ? c : JSON.stringify(c)}</li>)}
        </ul>
        <p style={FINE}>
          {infeasible.note}
          {/* The sentence "the drawing below is the heuristic's least-bad relaxation" was
              unconditional here until WP-13.4, and it becomes a false statement the instant a
              surface stops drawing one. It is conditioned on the drawing actually being below
              now, and where nothing is drawn the panel says THAT instead. */}
          {drawnBelow
            ? ' The drawing below is the heuristic’s least-bad relaxation, labelled — not a solution.'
            : ' This record was placed by a server that does not state a refusal verdict, so nothing here'
              + ' is drawn from it and nothing here claims it could be.'}
        </p>
      </div>
    );
  }

  return null;
}

export default ConflictSet;
