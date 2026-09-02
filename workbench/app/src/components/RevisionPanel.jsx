import React from 'react';
import { Eyebrow } from './Eyebrow.jsx';
import { adaptRevision, roundLine, CLASSES, classTag } from '../revision.js';

/* The loop's account of itself, on the bench (WP-9.3).

   Written in JSX where most of components/ is compiled React.createElement; it is new and
   there is no build step that would compile it, so it reads the way the surfaces do.

   What it shows, in order: what the loop bought (the key before and after, the engine its
   key was measured on, why it stopped); the rounds, each move as what it did, which finding
   it answered and on what basis -- the quoted sentence, in the receipt face the decision
   log uses -- and whether the round was accepted or rolled back; what REMAINS by class,
   with the architect's list and the suspects styled as neither verdict: a suspect is a
   finding the critic invented, and colouring it clear or failed would be a verdict the
   loop refused to give. The refusals are folded, not hidden.

   `live` is the in-flight job's rounds (the `round` events) and is cleared when the plan
   changes underneath the panel, so the panel is the record's -- undo takes it away. */

const CLASS_WORD = {
  actionable: 'a move could still answer (tabu this run)',
  placement: "the engine's",
  critic_suspect: "the critic's own",
  architect: "the architect's",
  advisory: 'advisory',
};

const body = { font: 'var(--fw-reg) 12.5px/1.55 var(--body)', color: 'var(--ink-2)', margin: 0 };
const quiet = { font: 'var(--type-data-s)', color: 'var(--ink-3)' };
const receipt = { font: 'var(--fw-reg) 12px/1.5 var(--receipt, var(--mono))', color: 'var(--ink-3)' };

function Move({ m, findingText, onCite }) {
  const tone = m.refused || m.refusedByMeasurement ? 'var(--brick)' : m.cleared ? 'var(--gilt-deep)' : 'var(--ink-3)';
  const verdict = m.refused ? `refused: ${m.refused}`
    : m.refusedByMeasurement ? 'made the plan worse on this engine — rolled back'
      : m.cleared ? 'cleared its finding' : 'applied; its finding persisted';
  return (
    <li style={{ margin: '0 0 7px', paddingLeft: 10, borderLeft: `2px solid ${tone}` }}>
      <div style={{ display: 'flex', gap: 8, alignItems: 'baseline', flexWrap: 'wrap' }}>
        <span style={{ font: 'var(--type-data-s)', color: 'var(--ink)' }}>{m.move}</span>
        <span style={{ ...quiet, color: tone }}>{verdict}</span>
      </div>
      {m.log && <p style={body}>{m.log}</p>}
      {m.finding && (
        <div style={quiet}>
          answered{' '}
          {onCite
            ? <button type="button" onClick={() => onCite(m.finding)}
                style={{ font: 'inherit', color: 'var(--ink-2)', textDecoration: 'underline dotted' }}>
                {findingText(m.finding)}</button>
            : findingText(m.finding)}
        </div>
      )}
      {m.basis && <div style={receipt}>{m.basis}</div>}
    </li>
  );
}

export function RevisionPanel({ report, live, statements, onCiteFinding }) {
  const r = adaptRevision(report);
  const findingText = (id) => (statements && statements[id]) || id;
  if (!r && !(live && live.length)) return null;
  return (
    <div data-panel="revision" style={{ maxWidth: 1000, border: '1px solid var(--rule)',
      borderLeft: '3px solid var(--gilt-deep)', padding: '10px 14px', margin: '0 0 14px' }}>
      {r ? (
        <>
          <Eyebrow tone="secondary">
            revised · {r.roundsN} round{r.roundsN === 1 ? '' : 's'} · {r.applied} move{r.applied === 1 ? '' : 's'} applied
            {r.refused ? `, ${r.refused} refused` : ''} · {r.stop}
          </Eyebrow>
          <p style={{ ...body, marginTop: 6 }}>
            Key {r.delta} <span style={quiet}>({r.engineText}{typeof r.seconds === 'number' ? `, ${r.seconds} s` : ''})</span>.
            The sheet above is a fresh solve of the revised record; the loop's own key was
            measured {r.engineText}, and the two can differ.
          </p>
          {r.reclaimed && (
            <p style={{ ...quiet, marginTop: 6, color: r.reclaimed.rolledBack ? 'var(--brick)' : 'var(--ink-3)' }}>
              {r.reclaimed.rolledBack
                ? `reclaim rolled back — ${r.reclaimed.why || 'it opened a fatal'} (${r.reclaimed.delta})`
                : `reclaim after the loop: ${r.reclaimed.log.length} line${r.reclaimed.log.length === 1 ? '' : 's'}, key ${r.reclaimed.delta}`}
            </p>
          )}
        </>
      ) : (
        <Eyebrow tone="secondary">revising… round {live[live.length - 1].n}</Eyebrow>
      )}

      {live && live.length > 0 && !r && (
        <div style={{ marginTop: 6 }}>
          {live.map((ev, i) => <div key={i} style={quiet}>{roundLine(ev)}</div>)}
        </div>
      )}

      {r && r.rounds.length > 0 && (
        <div style={{ marginTop: 10 }}>
          <Eyebrow tone="quiet">rounds</Eyebrow>
          {r.rounds.map((rd) => (
            <div key={rd.n} style={{ margin: '6px 0 0', paddingLeft: 10,
              borderLeft: `2px solid ${rd.accepted ? 'var(--gilt-deep)' : 'var(--brick)'}` }}>
              <div style={{ ...quiet, color: rd.accepted ? 'var(--ink-2)' : 'var(--brick)' }}>
                round {rd.n} · {rd.accepted ? 'accepted' : 'rolled back'} · {rd.delta}
                {rd.engine ? ` · ${rd.engine}` : ''}
                {rd.tabuForgotten ? ` · ${rd.tabuForgotten} refusal${rd.tabuForgotten === 1 ? '' : 's'} forgotten with the engine change` : ''}
              </div>
              <ul style={{ margin: '4px 0 0', padding: 0, listStyle: 'none' }}>
                {rd.moves.map((m, i) => <Move key={i} m={m} findingText={findingText} onCite={onCiteFinding} />)}
              </ul>
              {rd.opened.length > 0 && (
                <div style={quiet}>opened: {rd.opened.slice(0, 4).map(findingText).join(' · ')}{rd.opened.length > 4 ? ' · …' : ''}</div>
              )}
            </div>
          ))}
        </div>
      )}

      {r && (
        <div style={{ marginTop: 12 }}>
          <Eyebrow tone="quiet">what remains, by class</Eyebrow>
          <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap', marginTop: 4 }}>
            {CLASSES.map((c) => (
              <span key={c} style={{ ...quiet, color: r.remaining[c].length ? 'var(--ink-2)' : 'var(--ink-4)' }}>
                {CLASS_WORD[c]} {r.remaining[c].length}
              </span>
            ))}
          </div>
          {r.handed.length > 0 && (
            <div style={{ marginTop: 8 }}>
              <Eyebrow tone="quiet">handed to the architect</Eyebrow>
              <ul style={{ ...body, margin: '4px 0 0', paddingLeft: 18 }}>
                {r.handed.slice(0, 8).map((h) => (
                  <li key={h.id} style={{ marginBottom: 4 }}>
                    <span style={{ ...quiet, color: 'var(--sev-' + h.severity + ', var(--ink-3))' }}>{h.severity}</span>{' '}
                    {h.statement}
                    {(h.fix_right || h.fix_cheap || h.rule_why) && (
                      <div style={quiet}>
                        {h.fix_right ? `right: ${h.fix_right}` : h.fix_cheap ? `cheap: ${h.fix_cheap}` : h.rule_why}
                      </div>
                    )}
                  </li>
                ))}
                {r.handed.length > 8 && <li style={quiet}>… and {r.handed.length - 8} more</li>}
              </ul>
            </div>
          )}
          {r.suspects.length > 0 && (
            <div style={{ marginTop: 8 }}>
              <Eyebrow tone="quiet">the critic's own — neither clear nor failed</Eyebrow>
              <ul style={{ ...body, margin: '4px 0 0', paddingLeft: 18, color: 'var(--ink-3)' }}>
                {r.suspects.slice(0, 6).map((s) => (
                  <li key={s.id} style={{ marginBottom: 3 }}>
                    {s.statement}
                    {s.evidence && <div style={quiet}>{typeof s.evidence === 'string' ? s.evidence : (s.evidence.why || classTag('critic_suspect'))}</div>}
                  </li>
                ))}
                {r.suspects.length > 6 && <li style={quiet}>… and {r.suspects.length - 6} more</li>}
              </ul>
            </div>
          )}
          {r.refusedList.length > 0 && (
            <details style={{ marginTop: 8 }}>
              <summary style={{ ...quiet, cursor: 'pointer' }}>{r.refusedList.length} refusal{r.refusedList.length === 1 ? '' : 's'}</summary>
              <ul style={{ ...body, margin: '4px 0 0', paddingLeft: 18, color: 'var(--ink-3)' }}>
                {r.refusedList.map((m, i) => (
                  <li key={i}>{m.move}{m.finding ? ` on ${findingText(m.finding)}` : ''}: {m.refused || 'made the plan worse on this engine'}</li>
                ))}
              </ul>
            </details>
          )}
          {r.note && <p style={{ ...quiet, marginTop: 8 }}>{r.note}</p>}
        </div>
      )}
    </div>
  );
}

export default RevisionPanel;
