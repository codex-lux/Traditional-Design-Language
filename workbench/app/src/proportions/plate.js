/* The Proportions plate's ARITHMETIC, lifted out of surfaces/Proportions.jsx (WP-14.1).

   A plate whose extents, datum and counts are computed inside a React component can only be read
   back by a browser, so the only check it ever had was the walk's, over three of twenty-six
   packs. Lifted here as a pure function with no imports, it runs under `node --test` with no
   bundle, no npm install and no GPU -- the reason `round/frame.js` and `sheet/overlayRules.js` are
   leaves too -- and `tests/svg_census.py` reads its output against the ink Python serves.

   THE LIFT CHANGES NOTHING, AND THAT WAS PROVED RATHER THAN ASSERTED: every order pack at 6, 12,
   24 and 36 in of column diameter, 104 plates, was rendered to static markup before and after,
   and all 104 are byte-identical. What this function computes, and what it computes WRONG, is
   the census's business (docs/fidelity.md): nothing here is corrected in the commit that moved
   it, because a move and a fix in one commit can only be reasoned about as one. */

/* The plate: the assembly stack drawn at real inches from the members' own y and
   projection values, as a HALF SECTION — every band runs from the column's axis out to
   its own naked plus its projection, which is what an authority means by a projection.
   A band per member, the deepest boundaries carrying dimension ticks.

   RULING OVERTURNED 26 Aug 2026 (WP-5.11). This comment used to end "Not the moulding profiles
   of dist/orders.html — those stay in the order tool; this is the engine's stack, stated
   plainly." That was a defensible line while the only moulding geometry in the corpus was a
   set of hand-tuned Beziers that belonged to one page. It is not defensible now: the profiles
   are CONSTRUCTED, in build/profiles.py, from the same member data this plate already draws,
   and a plate that shows a cyma recta as a straight line is not stating the engine's stack
   plainly — it is withholding the half of it a reader came for. The bands still carry every
   dimension, tick, hover and confidence mark they did; their outer edge is now the moulding.
   The plate still constructs nothing itself: it scales what the engine built.

   Two things this plate got wrong until 26 Aug 2026, both visible at a glance and both
   in the reading of the engine's output rather than in the engine:

   1. `y_bottom_in` and `y_top_in` are ABSOLUTE positions in the stack — proportion_engine
      .dimension() has already run the cumulative sum. Adding each assembly's own base to
      them a second time floated the base 90 inches clear of the plinth it sits on, the
      shaft another 108 above that, and drove the cornice out through the top of the
      frame. The captions down the left were drawn from a separate, correct running total,
      so the plate labelled a gap CAPITAL and pointed at nothing.
   2. Every band was drawn 16 units wide plus its projection, whatever the order's
      diameter — so the shaft, whose whole business is to be one diameter thick, came out
      a stick with mouldings wider than itself. The datum rule is the order tool's
      (build/orders_template.html::buildGeometry): the pedestal projects from the die's
      naked, base, shaft and capital from the column's radius AT THAT HEIGHT (which
      diminishes, and each authority says where the diminution begins), and the
      entablature from the naked of the frieze.

   Every annotation is sized in hundredths of the stack, so the plate is identical at
   any column diameter — which is the claim a proportional system makes. It cannot
   overflow its frame at 36 inches because it does not change shape at 36 inches. */
export function plateGeometry(data) {
  const asms = data.assemblies || [];
  const stated = data.totals?.stack_height_in || 0;

  // assembly extents read off the members that are actually drawn, so a caption
  // brackets what is on the plate and not a parallel arithmetic of its own
  const rows = [];
  let cursor = 0;
  for (const a of asms) {
    const ms = a.members || [];
    const y0 = ms.length ? Math.min(...ms.map((m) => m.y_bottom_in ?? 0)) : cursor;
    const y1 = ms.length ? Math.max(...ms.map((m) => m.y_top_in ?? 0)) : cursor + (a.height_in || 0);
    rows.push({ id: a.id, stated_in: a.height_in, y0, y1, ms });
    cursor = Math.max(cursor, y1);
  }
  const H = Math.max(stated, cursor);
  if (!H) return null;

  const R = (data.totals?.lower_diameter_in || 0) / 2;
  const nominal = !R;                       // no published diameter: say so, do not imply one
  const r0 = R || H / 25;
  const r1 = (data.totals?.upper_diameter_in || 0) / 2 || r0;
  const col = data.column || {};
  const shaft = rows.find((x) => x.id === 'shaft');
  const entStart = col.entasis_begins_at ?? 1 / 3;
  const radiusAt = (y) => {
    if (!shaft || shaft.y1 <= shaft.y0) return r0;
    if (y <= shaft.y0) return r0;
    if (y >= shaft.y1) return r1;
    const t = (y - shaft.y0) / (shaft.y1 - shaft.y0);
    if (t <= entStart) return r0;
    const u = (t - entStart) / (1 - entStart);
    return r0 - (r0 - r1) * (u * u * (3 - 2 * u));   // cylindrical below, then smooth
  };
  /* WHICH WAY IS A PROJECTION MEASURED? The corpus answers two different ways — thirteen
     packs record a member's `projection_parts` as an offset FROM ITS OWN NAKED (Gibbs's
     Doric shaft body: 0) and twelve as an absolute radius FROM THE AXIS (Vignola's Ionic
     shaft body: exactly the semidiameter) — and until 26 Aug 2026 no pack said which, so
     a consumer had to guess. Adding a naked to a figure that is already a radius draws
     the shaft's own apophyge and astragal a whole semidiameter clear of the shaft they
     sit on. OQ 65 was ruled: the pack DECLARES it, `check_orders.py` verifies the
     declaration against the pack's own shaft, and this plate reads it rather than
     deriving it. A pack that reaches here without one is drawn the way the older half of
     the corpus is written, and says so on the sheet. */
  const fromAxis = data.projection_datum === 'axis';
  const undeclared = !data.projection_datum;

  const baseRow = rows.find((x) => x.id === 'base');
  const basePlinth = baseRow && baseRow.ms.length
    ? Math.max(0, ...baseRow.ms.map((m) => m.projection_in || 0)) : 0;
  // the pedestal die is naked to the base plinth that lands on it, read the pack's own way
  const dieNaked = basePlinth
    ? Math.max(r0, fromAxis ? basePlinth : r0 + basePlinth)
    : r0 * 1.2;
  const naked = (id, y) => {
    if (id === 'pedestal' || id === 'subplinth') return dieNaked;
    if (id === 'base' || id === 'shaft' || id === 'capital') return radiusAt(y);
    return r1;                                        // entablature: from the frieze naked
  };

  /* Under the radius reading a recorded 0 is not "at the axis" — it is NO PROJECTION
     RECORDED, and drawing the band to the centreline would collapse it. Those members
     take their naked instead and are counted, so the plate can say how many of its own
     edges the pack does not give rather than drawing a cornice that recedes behind the
     column. Under the offset reading 0 means flush with the naked, which is a statement
     the pack is making, and it is drawn as one. */
  const unrecorded = new Set();
  const outer = (id, key, y, proj) => {
    const nk = naked(id, y);
    if (!fromAxis) return nk + proj;
    if (!(proj > 0)) { unrecorded.add(key); return nk; }
    return Math.max(proj, nk);
  };

  /* WP-5.11: the member's own moulded edge, constructed by build/profiles.py and served with the
     pack. This plate does not know what a cyma is and must not learn: every copy of that
     knowledge this corpus has kept in two languages has eventually disagreed with itself. All
     that happens here is scale, flip, and emit. `f` is the ratio of the module the plate is
     drawing to the module the geometry was constructed at — pack geometry is linear in the
     module, which tests/test_profiles.py proves. */
  const geom = data.geometry;
  const f = geom && geom.module_in ? (data.module_in || geom.module_in) / geom.module_in : 1;
  const segsFor = {};
  if (geom) {
    for (const a of geom.assemblies) {
      for (const fc of a.faces || []) segsFor[`${a.id}.${fc.id}`] = fc;
    }
  }
  /* THE PATHS COME FROM PYTHON, in MODEL inches (x out from the axis, y up), and this plate
     applies an SVG transform instead of walking the segments (OQ 83, ruled 27 Aug 2026).

     What used to be here was `edgeCmds`, one of two JavaScript copies of the SVG sweep rule, and
     both copies were wrong: they emitted the inverse of the correct flag, so every arc on this
     plate drew as its own mirror — an ovolo as a cavetto, a torus as a hollow. A model-space path
     has no handedness for a consumer to get wrong; `<g transform="scale(1,-1)">` flips it and SVG
     mirrors the arcs correctly, which is its job and not this file's.

     One member as a closed band: out along its own foot, up its constructed profile, back to the
     axis. Falls back to the straight edge when a pack reaches here without geometry, so a plate
     is still drawn rather than blanked. */
  const bandPath = (b) => {
    const g = segsFor[b.key];
    if (!g || !g.path) {
      return { d: `M 0 ${sy(b.y0)} L ${b.x0} ${sy(b.y0)} L ${b.x1} ${sy(b.y1)} L 0 ${sy(b.y1)} Z`,
               transform: null };
    }
    // sy(y) = H - y, so the group is a y-flip about H, and f scales the module.
    return { d: g.path, transform: `translate(0,${H}) scale(${f},${-f})` };
  };

  const bands = [];
  for (const row of rows) {
    const span = row.y1 - row.y0;
    // The engine flags side_by_side off an assembly's sums_check, and a DERIVED shaft
    // (an authority that publishes a column height and no shaft) carries sums_check:false
    // with a single member. One member cannot stand beside anything, and filling it as
    // though it did would have the plate claim a triglyph-and-metope where there is only
    // a shaft nobody published. Its own medium confidence already draws the dashed mark
    // that says so.
    const group = row.ms.length > 1 ? row.ms.filter((m) => m.side_by_side) : [];
    // a side-by-side pair stands at the same height; draw the deeper one first so the
    // shallower reads as a step in front of it rather than a rectangle on top of it
    const ordered = group.length
      ? [...row.ms].sort((a, b) => (b.projection_in || 0) - (a.projection_in || 0))
      : row.ms;
    for (const m of ordered) {
      const y0 = m.y_bottom_in ?? row.y0, y1 = m.y_top_in ?? y0;
      const isShaftBody = row.id === 'shaft' && (y1 - y0) > span * 0.6;
      const proj = m.projection_in || 0;
      bands.push({
        key: `${row.id}.${m.id}`, asm: row.id, id: m.id, name: m.name, note: m.note,
        conf: m.confidence, side: m.side_by_side && row.ms.length > 1, y0, y1,
        // the shaft body is the column: it takes the naked at each height, which is what
        // makes it taper, and never a projection on top of the radius it already is
        x0: isShaftBody ? naked(row.id, y0) : outer(row.id, `${row.id}.${m.id}`, y0, proj),
        x1: isShaftBody ? naked(row.id, y1) : outer(row.id, `${row.id}.${m.id}`, y1, proj),
        h: y1 - y0, proj,
      });
    }
  }
  const maxX = Math.max(dieNaked, ...bands.map((b) => Math.max(b.x0, b.x1)));

  const U = H / 100;                    // one annotation unit: a hundredth of the stack
  const CAP = 30 * U, RIGHT = 16 * U;   // caption gutter, dimension gutter
  const sy = (y) => H - y;              // model up, screen down
  const dimX = maxX + 6 * U;
  return {
    rows,
    H,
    R,
    nominal,
    r0,
    r1,
    radiusAt,
    fromAxis,
    undeclared,
    dieNaked,
    naked,
    unrecorded,
    outer,
    f,
    segsFor,
    bandPath,
    bands,
    maxX,
    U,
    CAP,
    RIGHT,
    sy,
    dimX,
  };
}
