/* What the keys are, and — in the same card — how a thing is addressed.

   The two belong together. The citation grammar is how the rail cites, how a URL is
   written, and what the palette prints beside every result; a reader who has noticed
   `fault:porch-too-shallow-to-inhabit` in three places deserves one card that says what
   it is. It is also the honest answer to "can I link someone to this?" — yes, and here
   is the form. */
import React from 'react';
import { SHORTCUTS } from '../keys.js';
import { Eyebrow } from '../components/Eyebrow.jsx';

export function ShortcutCard({ open, onClose }) {
  if (!open) return null;
  return (
    <div role="presentation" onMouseDown={(e) => { if (e.target === e.currentTarget) onClose(); }}
      style={{ position: 'fixed', inset: 0, zIndex: 60, background: 'var(--wash-2, rgba(40,36,28,.28))',
        display: 'flex', justifyContent: 'center', alignItems: 'flex-start', paddingTop: '13vh' }}>
      <div role="dialog" aria-modal="true" aria-label="Keyboard shortcuts and addressing"
        style={{ width: 'min(560px, calc(100vw - 32px))', maxHeight: '72vh', overflow: 'auto',
          background: 'var(--paper)', border: '1px solid var(--rule)',
          boxShadow: '0 10px 34px rgba(40,36,28,.24)', padding: '18px 20px 20px' }}>

        <Eyebrow>keys</Eyebrow>
        <table style={{ borderCollapse: 'collapse', width: '100%', margin: '9px 0 20px' }}>
          <tbody>
            {SHORTCUTS.map((s) => (
              <tr key={s.keys}>
                <td style={{ font: 'var(--type-data)', fontFamily: 'var(--mono)', color: 'var(--ink)',
                  padding: '3px 14px 3px 0', whiteSpace: 'nowrap', verticalAlign: 'baseline', width: 1 }}>
                  {s.keys}
                  {s.alt && <span style={{ color: 'var(--ink-4)' }}> · {s.alt}</span>}
                </td>
                <td style={{ font: 'var(--fw-reg) 13px/1.5 var(--body)', color: 'var(--ink-2)',
                  padding: '3px 0', verticalAlign: 'baseline' }}>{s.does}</td>
              </tr>
            ))}
          </tbody>
        </table>

        <Eyebrow>how a thing is addressed</Eyebrow>
        <p style={{ font: 'var(--fw-reg) 13px/1.6 var(--body)', color: 'var(--ink-2)',
          margin: '9px 0 10px', maxWidth: '62ch' }}>
          Everything in the corpus has one address, written <span style={{ fontFamily: 'var(--mono)' }}>kind:id</span>.
          The rail cites in it, the palette prints it beside every result, and a URL is that
          address written down — so any view can be refreshed, gone back from, or handed to
          somebody else.
        </p>
        <table style={{ borderCollapse: 'collapse', width: '100%', marginBottom: 16 }}>
          <tbody>
            {[
              ['style:tidewater-georgian', 'the full style record'],
              ['kit:tidewater-georgian#cornice', 'one slot in that style’s kit'],
              ['fault:porch-too-shallow-to-inhabit', 'a named error'],
              ['pack:brick-course', 'a proportioning system'],
              ['#/cite/style:craftsman', 'the same address, as a link'],
            ].map(([ref, what]) => (
              <tr key={ref}>
                <td style={{ font: 'var(--type-data-s)', fontFamily: 'var(--mono)', color: 'var(--gilt-deep)',
                  padding: '2px 14px 2px 0', whiteSpace: 'nowrap', verticalAlign: 'baseline' }}>{ref}</td>
                <td style={{ font: 'var(--fw-reg) 12.5px/1.5 var(--body)', color: 'var(--ink-3)',
                  padding: '2px 0', verticalAlign: 'baseline' }}>{what}</td>
              </tr>
            ))}
          </tbody>
        </table>

        <p style={{ font: 'var(--fw-reg) 12.5px/1.55 var(--body)', color: 'var(--ink-4)',
          margin: 0, maxWidth: '62ch' }}>
          The palette searches names, ids and akas — not the prose of a tell or a remedy.
          For a half-remembered phrase, ask the rail: it reads the records properly, and
          says what it could not evaluate.
        </p>

        <div style={{ marginTop: 16, textAlign: 'right' }}>
          <button type="button" onClick={onClose}
            style={{ font: 'var(--type-data-s)', color: 'var(--gilt-deep)',
              borderBottom: '1px solid var(--link-underline)' }}>close · esc</button>
        </div>
      </div>
    </div>
  );
}
