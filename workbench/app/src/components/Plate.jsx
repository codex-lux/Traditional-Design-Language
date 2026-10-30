/* A DRAWING ON THE INSTRUMENT (Phase 17, WP-17.0).

   <Plate caption={…} head={…}>{svg or <PlateViewer>}</Plate>

   A vellum mat ten pixels deep, a double border (the profile ink outside a hairline), and a
   shadow only to lift it off the dark ground (`.tdl-plate` in tokens.css). `head` is the plate's
   own header, where the loupe's fit · 1:1 · ± go; `caption` sits below the plate, on whatever
   ground the page is, in mono capitals. The plate itself is `data-ground="vellum"`, so a server
   sheet re-tokenized to the Drawn Language reads its inks at their paper values. */
import React from 'react';

export function Plate({ caption, head, children, style, ...rest }) {
  return (
    <figure data-plate="" style={{ margin: 0, minWidth: 0, ...style }} {...rest}>
      <div data-ground="vellum" className="tdl-plate">
        {head && <div data-plate-head="" style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, marginBottom: 6 }}>{head}</div>}
        {children}
      </div>
      {caption && <figcaption className="tdl-plate-caption">{caption}</figcaption>}
    </figure>
  );
}
