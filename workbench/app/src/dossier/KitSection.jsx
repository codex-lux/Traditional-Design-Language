/* Kit — the dossier's kit section (WP-14.12, PRD §D.1 row 3).

   `surfaces/KitSurface.jsx` embedded, with the dossier's style handed in and the open slot the
   URL's: a slot opens `#/style/<id>/kit/<slot>`, which is `kit:<id>#<slot>`'s place. The kit
   keeps its own filters (`q`, `group`, `all`) in the query, as it did as a surface. */
import React from 'react';
import { KitSurface } from '../surfaces/KitSurface.jsx';

export function KitSection({ styleId, selection, setSelection, onCite }) {
  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
      <KitSurface styleId={styleId} selection={selection} setSelection={setSelection} onCite={onCite} />
    </div>
  );
}
