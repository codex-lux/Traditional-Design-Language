/* CLEAR AND STRUCTURAL DIMENSIONS, DRAWN (Phase 17, WP-17.8). A schematic in the drawing's own
   language and NOT engine output: two rooms between an exterior wall drawn outward from the block
   and a partition centred on the line they share, with the two dimension strings a builder must
   tell apart. Its words are the `modelling-conventions` record's; the drawing carries none but its
   two dimension marks. A drawing, so its inks are pigments on vellum. */
import React from 'react';
import { Plate } from '../components/Plate.jsx';
import { Term } from '../components/Term.jsx';

const ink = { stroke: 'var(--ink)', fill: 'none', strokeWidth: 'var(--lw-medium)' };
const dim = { stroke: 'var(--ink-2)', fill: 'none', strokeWidth: 'var(--lw-construction)' };

export function ConventionsPlate() {
  return (
    <Plate data-conventions="" caption={<Term id="modelling-conventions" />} style={{ maxWidth: 520 }}>
      <svg viewBox="0 0 300 120" style={{ display: 'block', width: '100%' }} aria-hidden="true">
        {/* the exterior wall, outside the block, and the partition on the shared line */}
        <rect x="14" y="28" width="12" height="62" style={{ ...ink, fill: 'var(--salmon)' }} vectorEffect="non-scaling-stroke" />
        <rect x="155" y="28" width="6" height="62" style={{ ...ink, fill: 'var(--sepia-pale)' }} vectorEffect="non-scaling-stroke" />
        <rect x="274" y="28" width="12" height="62" style={{ ...ink, fill: 'var(--salmon)' }} vectorEffect="non-scaling-stroke" />
        <line x1="26" y1="28" x2="274" y2="28" style={ink} vectorEffect="non-scaling-stroke" />
        <line x1="26" y1="90" x2="274" y2="90" style={ink} vectorEffect="non-scaling-stroke" />
        <line x1="158" y1="20" x2="158" y2="98" style={{ ...dim, strokeDasharray: 'var(--dash-centre)' }} vectorEffect="non-scaling-stroke" />
        {/* clear: inside face to inside face; to the centre: inside face to the shared line */}
        <line x1="26" y1="106" x2="158" y2="106" style={dim} vectorEffect="non-scaling-stroke" />
        <line x1="26" y1="100" x2="26" y2="112" style={dim} vectorEffect="non-scaling-stroke" />
        <line x1="158" y1="100" x2="158" y2="112" style={dim} vectorEffect="non-scaling-stroke" />
        <line x1="26" y1="14" x2="274" y2="14" style={dim} vectorEffect="non-scaling-stroke" />
        <line x1="26" y1="8" x2="26" y2="20" style={dim} vectorEffect="non-scaling-stroke" />
        <line x1="274" y1="8" x2="274" y2="20" style={dim} vectorEffect="non-scaling-stroke" />
      </svg>
    </Plate>
  );
}
