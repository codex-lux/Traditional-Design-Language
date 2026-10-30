/* THE SITE, DRAWN (Phase 17, WP-17.6). A drawing on vellum, so its inks are pigments: the lot,
   the street and the compass are `brief/siteDiagram.js`'s geometry, and this draws them. */
import React from 'react';
import { siteDiagram } from './siteDiagram.js';

/* The site as a plate: the drawing is `siteDiagram`'s, and each compass point is a button that sets
   (or clears) the entrance face, so a keyboard reaches it as the chips it replaces were reached. */
export function SiteDiagram({ lotW, lotD, entrance, onFace }) {
  const d = siteDiagram({ lotW, lotD, entrance });
  const { lot } = d;
  return (
    <div data-ground="vellum" className="tdl-plate" data-site-diagram={lot.stated ? 'stated' : 'unstated'}
      style={{ padding: 8, marginTop: 4 }}>
      <svg viewBox={`0 0 ${d.box} ${d.box}`} style={{ display: 'block', width: '100%', maxWidth: 260, margin: '0 auto' }}
        role="group" aria-label="the site and its entrance face">
        <rect x={lot.x} y={lot.y} width={lot.w} height={lot.h}
          style={{ fill: lot.stated ? 'var(--paper-lit)' : 'none', stroke: 'var(--ink)', strokeWidth: 'var(--lw-medium)',
            strokeDasharray: lot.stated ? 'none' : '3 3' }} vectorEffect="non-scaling-stroke" />
        {!lot.stated && <MarkGlyphSvg x={d.box / 2} y={d.box / 2} />}
        {d.street && (
          <line x1={d.street.x1} y1={d.street.y1} x2={d.street.x2} y2={d.street.y2} data-street=""
            style={{ stroke: 'var(--gilt)', strokeWidth: 'var(--lw-cut)' }} vectorEffect="non-scaling-stroke" />
        )}
        {d.points.map((p) => (
          <g key={p.d} role="button" tabIndex={0} aria-pressed={p.on} aria-label={p.d} data-compass={p.d}
            onClick={() => onFace(p.d)}
            onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onFace(p.d); } }}
            style={{ cursor: 'pointer' }}>
            <circle cx={p.x} cy={p.y} r={6.5} style={{ fill: p.on ? 'var(--gilt)' : 'var(--paper)',
              stroke: p.on ? 'var(--gilt-deep)' : 'var(--ink-2)', strokeWidth: 'var(--lw-fine)' }} vectorEffect="non-scaling-stroke" />
            <text x={p.x} y={p.y + 2} textAnchor="middle"
              style={{ font: 'var(--fw-med) 5.5px/1 var(--mono)', fill: p.on ? 'var(--coal)' : 'var(--ink)' }}>{p.d}</text>
          </g>
        ))}
      </svg>
    </div>
  );
}

/* The unjudged ring drawn in the site's own frame: a lot not stated is said, never defaulted. */
function MarkGlyphSvg({ x, y }) {
  return (
    <g aria-hidden="true">
      <circle cx={x} cy={y} r={5} style={{ fill: 'none', stroke: 'var(--ink-3)', strokeWidth: 'var(--lw-fine)' }} vectorEffect="non-scaling-stroke" />
      <line x1={x - 3.5} y1={y + 3.5} x2={x + 3.5} y2={y - 3.5} style={{ stroke: 'var(--ink-3)', strokeWidth: 'var(--lw-construction)' }} vectorEffect="non-scaling-stroke" />
    </g>
  );
}

