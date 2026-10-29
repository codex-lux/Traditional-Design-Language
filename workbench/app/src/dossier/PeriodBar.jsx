/* The period bar, drawn (Phase 17, WP-17.9). `periodBar` decides; this draws it in the drawing's
   pigments: the floruit in full ink, the lead-in and the tail as thinner lines, a revival in the
   gilt, and a date the record does not state named under the bar as unstated, with its ring. */
import React from 'react';
import { periodBar } from './periodBar.js';
import { Term } from '../components/Term.jsx';
import { MarkGlyph } from '../components/MarkGlyph.jsx';

const H = { origin: 3, floruit: 10, decline: 3, revival: 6 };
const INK = { origin: 'var(--border-paper)', floruit: 'var(--paper)', decline: 'var(--border-paper)', revival: 'var(--gilt)' };

export function PeriodBar({ period }) {
  const bar = periodBar(period);
  if (!bar) return null;
  return (
    <div data-period-bar={bar.segments.map((s) => s.id).join(' ')} style={{ margin: '4px 0 20px', maxWidth: 640 }}>
      <svg viewBox="0 0 600 46" style={{ display: 'block', width: '100%' }} aria-hidden="true">
        <line x1="0" y1="20" x2="600" y2="20" style={{ stroke: 'var(--border-hairline)', strokeWidth: 1 }} />
        {bar.segments.map((s, i) => (
          <g key={i} data-period-segment={s.id}>
            <rect x={s.x0 * 600} y={20 - H[s.id] / 2} width={Math.max(2, (s.x1 - s.x0) * 600)} height={H[s.id]}
              style={{ fill: s.id === 'floruit' ? 'var(--paper)' : INK[s.id] }} />
            <text x={s.x0 * 600} y={40} style={{ font: 'var(--type-data-s)', fontSize: 10, fill: 'var(--text-secondary)' }}>{s.from}</text>
          </g>
        ))}
        {bar.segments.filter((s) => s.id === 'floruit').map((s) => (
          <text key="fe" x={s.x1 * 600} y={40} textAnchor="end" style={{ font: 'var(--type-data-s)', fontSize: 10, fill: 'var(--text-secondary)' }}>{s.to}</text>
        ))}
      </svg>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px 14px', font: 'var(--type-data-s)', color: 'var(--text-secondary)' }}>
        {[...new Set(bar.segments.map((s) => s.id))].map((id) => (
          <span key={id} data-period-key={id}><Term id={`period-${id}`} /></span>
        ))}
        {bar.unstated.map((id) => (
          <span key={'u' + id} data-period-unstated={id} style={{ display: 'inline-flex', gap: 5, alignItems: 'center' }}>
            <MarkGlyph token="--mark-unjudged" size={10} /><Term id={`period-${id}`} />
          </span>
        ))}
      </div>
    </div>
  );
}
