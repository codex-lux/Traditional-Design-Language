/* PAPER ON THE INSTRUMENT (Phase 17, WP-17.0, ruled 29 Oct 2026).

   <Vellum as="section" style={...}>…</Vellum>

   The one way content is set on vellum. It marks its box `data-ground="vellum"`, so every duty
   inside it (`--text-body`, `--surface-panel`, `--border-hairline`, `--link`) resolves to its
   paper value whatever ground the page stands on, and paints the paper. A card, a candidate's
   column, a record's body: anything the board draws as the brightest object on the screen. A
   drawing goes in `<Plate>`, which is a Vellum with a frame and a caption. */
import React from 'react';

export function Vellum({ as: Tag = 'div', className, children, ...rest }) {
  return (
    <Tag data-ground="vellum" className={className ? `tdl-vellum ${className}` : 'tdl-vellum'} {...rest}>
      {children}
    </Tag>
  );
}
