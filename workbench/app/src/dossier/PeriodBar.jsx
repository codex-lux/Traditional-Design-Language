/* The period bar, drawn (Phase 17, WP-17.9). `periodBar` decides; this draws it: the floruit in
   the page's full ink, the lead-in and the tail as thinner lines, a revival in the gilt, and a
   date the record does not state named under the bar as unstated, with its ring.

   ITS INKS FOLLOW THE GROUND (26 Nov 2026). The floruit was drawn in `--paper`, which is full ink
   on the instrument and no ink at all on a page: on vellum the bar's one heavy segment was
   invisible. It takes the body-text duty now, which is paper on the dark ground and ink on the
   page; each word in the key stands beside a swatch of the segment it names. */
import React from 'react';
import { periodBar } from './periodBar.js';
import { Term } from '../components/Term.jsx';
import { MarkGlyph } from '../components/MarkGlyph.jsx';

const H = { origin: 3, floruit: 12, decline: 3, revival: 7 };
const INK = { origin: 'var(--border-paper)', floruit: 'var(--text-body)', decline: 'var(--border-paper)', revival: 'var(--gilt)' };

export function PeriodBar({ period }) {
  const bar = periodBar(period);
  if (!bar) return null;
  return (
    <div data-period-bar={bar.segments.map((s) => s.id).join(' ')} style={{ margin: '0 0 8px', maxWidth: 720 }}>
      <svg viewBox="0 0 600 44" style={{ display: 'block', width: '100%' }} aria-hidden="true">
        <line x1="0" y1="16" x2="600" y2="16" style={{ stroke: 'var(--border-hairline)', strokeWidth: 1 }} />
        {bar.segments.map((s, i) => (
          <g key={i} data-period-segment={s.id}>
            <rect x={s.x0 * 600} y={16 - H[s.id] / 2} width={Math.max(2, (s.x1 - s.x0) * 600)} height={H[s.id]}
              style={{ fill: INK[s.id] }} />
            {/* the decline begins where the floruit ends, and that year is already lettered there:
                a second label at the same x set "17801780" under the bar the first time it was drawn */}
            {s.id !== 'decline' && (
              <text x={s.x0 * 600} y={38} style={{ font: 'var(--type-data-s)', fontSize: 10.5, fill: 'var(--text-secondary)' }}>{s.from}</text>
            )}
          </g>
        ))}
        {bar.segments.filter((s) => s.id === 'floruit').map((s) => (
          <text key="fe" x={s.x1 * 600} y={38} textAnchor="end" style={{ font: 'var(--type-data-s)', fontSize: 10.5, fill: 'var(--text-secondary)' }}>{s.to}</text>
        ))}
      </svg>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px 18px', marginTop: 4, font: 'var(--type-data-s)', color: 'var(--text-secondary)' }}>
        {[...new Set(bar.segments.map((s) => s.id))].map((id) => (
          <span key={id} data-period-key={id} style={{ display: 'inline-flex', gap: 6, alignItems: 'center' }}>
            <span aria-hidden="true" style={{ width: 14, height: Math.max(2, H[id] - 2), background: INK[id], flex: 'none' }} />
            <Term id={`period-${id}`} />
          </span>
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
