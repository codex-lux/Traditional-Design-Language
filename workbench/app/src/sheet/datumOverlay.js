/* THE GOVERNING DATUMS, OVER THE ELEVATION PLATE (Phase 17, WP-17.7; board 5).

   The elevation states its datums -- grade, the floors, the water table, the eave -- and the
   server forwards them beside the plate (`corpus.elevation_datums`). This leaf maps each through
   the plate's own `data-frame` (`build/sheet_style.frame_attr`):

       px_y = origin_px[1] + (at_origin_ft[1] - v) * px_per_ft

   and returns one construction line per datum across the plate's width, in the plate's own pixel
   frame, so an overlay SVG laid over the plate with the plate's viewBox registers by construction.
   Nothing here reads the SVG's marks; a plate whose frame cannot be read draws no overlay, and the
   toggle is absent rather than empty. Pure. */
export function frameOf(svg) {
  if (typeof svg !== 'string') return null;
  const m = /data-frame='([^']*)'/.exec(svg);
  if (!m) return null;
  try {
    const f = JSON.parse(m[1].replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&amp;/g, '&'));
    return f && Array.isArray(f.plates) ? f : null;
  } catch { return null; }
}

export function viewBoxOf(svg) {
  const m = typeof svg === 'string' ? /viewBox="([\d.\s-]+)"/.exec(svg) : null;
  if (!m) return null;
  const [x, y, w, h] = m[1].trim().split(/\s+/).map(Number);
  return [x, y, w, h].every(Number.isFinite) ? { x, y, w, h } : null;
}

/* The elevation plate of the frame: the one whose projection is an elevation. */
function elevationPlate(frame) {
  return frame ? frame.plates.find((p) => p.proj === 'elevation') || null : null;
}

export function datumLines(svg, datums) {
  const plate = elevationPlate(frameOf(svg));
  const box = viewBoxOf(svg);
  if (!plate || !box || !Array.isArray(datums) || !datums.length) return null;
  const k = plate.px_per_ft, [ox, oy] = plate.origin_px || [], [, av] = plate.at_origin_ft || [];
  if (![k, ox, oy, av].every(Number.isFinite)) return null;
  return datums.filter((d) => Number.isFinite(d.v_ft)).map((d) => ({
    id: d.id,
    v_ft: d.v_ft,
    y: oy + (av - d.v_ft) * k,
    x1: ox,
    x2: box.x + box.w - 8,
    from: d.from,
    pack: d.pack || null,
  }));
}
