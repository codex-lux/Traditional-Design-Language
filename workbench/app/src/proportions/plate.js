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

  /* EVERYTHING BELOW IS PYTHON'S (WP-14.2). This plate used to carry its own copy of the datum
     rule, the column's taper, the die and the outer face -- a second implementation of
     build/profiles.py's arithmetic, in a second language -- and it disagreed with the ink it drew
     beside: on twelve of the fourteen packs that declare the axis its frame was narrower than the
     mouldings (vignola-ionic 11.67 in against 15.33), on thirteen it said members "state no
     projection" that Python had drawn flush, on nine packs that publish none for a member it said
     nothing, and on all thirteen of those its caption named one datum for assemblies Python had
     read on the other. The pedestal's die was `r0 * 1.2` where the base publishes nothing --
     a figure nobody states. Now the served geometry says where every member's face is, which
     members publish no projection, which datum each assembly was read on and how far the ink
     reaches, and this function only scales.

     `f` is the ratio of the module the plate is drawing to the module the geometry was constructed
     at -- pack geometry is linear in the module, which tests/test_profiles.py proves. */
  const geom = data.geometry || null;
  const f = geom && geom.module_in ? (data.module_in || geom.module_in) / geom.module_in : 1;
  const segsFor = {};
  if (geom) {
    for (const a of geom.assemblies || []) {
      for (const fc of a.faces || []) segsFor[`${a.id}.${fc.id}`] = fc;
    }
  }
  /* WHICH WAY IS A PROJECTION MEASURED? The pack DECLARES one datum (OQ 65) and it is not true
     of every assembly: gibbs-ionic declares the axis, true of its shaft, while its frieze records
     a projection of 0, and a frieze cannot stand on the column's centre line. Python reads each
     assembly group on its own figures (OQ 78) and serves the reading; the caption states it per
     assembly, and says separately what the pack declares. */
  const fromAxis = data.projection_datum === 'axis';
  const undeclared = !data.projection_datum;
  const datum = { axis: [], naked: [], unjudged: [] };
  for (const r of rows) {
    const d = (geom?.assembly_datum || {})[r.id];
    if (datum[d]) datum[d].push(r.id);
  }
  // exactly the members Python drew no face for: a ghost at the naked, never a flush face
  const unrecorded = new Set((geom?.unpublished || []).map((u) => `${u.assembly}.${u.id}`));
  const dieNaked = geom && geom.die_naked === 'derived' ? geom.die_naked_in * f : null;
  const dieReason = geom ? geom.die_naked_reason || null : null;

  /* THE PATHS COME FROM PYTHON, in MODEL inches (x out from the axis, y up), and this plate
     applies an SVG transform instead of walking the segments (OQ 83, ruled 27 Aug 2026).

     What used to be here was `edgeCmds`, one of two JavaScript copies of the SVG sweep rule, and
     both copies were wrong: they emitted the inverse of the correct flag, so every arc on this
     plate drew as its own mirror — an ovolo as a cavetto, a torus as a hollow. A model-space path
     has no handedness for a consumer to get wrong; `<g transform="scale(1,-1)">` flips it and SVG
     mirrors the arcs correctly, which is its job and not this file's.

     One member as a closed band: out along its own foot, up its constructed profile, back to the
     axis. A pack reaching here without geometry is drawn at the column's radius, every band a
     straight edge, and the caption says there is no constructed geometry rather than implying one. */
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
      ? [...row.ms].sort((a, b) => ((segsFor[`${row.id}.${b.id}`] || {}).x || 0)
                                   - ((segsFor[`${row.id}.${a.id}`] || {}).x || 0))
      : row.ms;
    for (const m of ordered) {
      const y0 = m.y_bottom_in ?? row.y0, y1 = m.y_top_in ?? y0;
      const key = `${row.id}.${m.id}`;
      const fc = segsFor[key];
      bands.push({
        key, asm: row.id, id: m.id, name: m.name, note: m.note,
        conf: m.confidence, side: m.side_by_side && row.ms.length > 1, y0, y1,
        // the member's face as Python constructed it: a tapered shaft body runs from its foot's
        // radius to its head's, every other member stands at its own face
        x0: fc ? (fc.tapered ? fc.x_from : fc.x) * f : r0,
        x1: fc ? fc.x * f : r0,
        h: y1 - y0, proj: m.projection_in, unpublished: unrecorded.has(key),
      });
    }
  }
  // THE FRAME IS THE INK'S OWN EXTENT, as Python measured it, ghosts' brackets included
  const maxX = geom && geom.bbox_in
    ? geom.bbox_in.x1 * f
    : Math.max(r0, ...bands.map((b) => Math.max(b.x0, b.x1)));
  const noGeometry = !geom || !Object.keys(segsFor).length;

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
    fromAxis,
    undeclared,
    datum,
    datumWords: datumWords(datum, undeclared),
    stackWords: stackWords(data.stack_notes),
    dieNaked,
    dieReason,
    unrecorded,
    noGeometry,
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

function andList(xs) {
  return xs.length < 2 ? xs.join('') : `${xs.slice(0, -1).join(', ')} and ${xs[xs.length - 1]}`;
}

/* What the stack left out, and why, in the words the orders page uses (WP-14.2): Benjamin's
   subplinth offered instead of the pedestal, and an entablature drawn whole because the triplet it
   inherits contradicts it. Read off `stack_notes` as proportion_engine serves it. */
export function stackWords(notes) {
  const out = [];
  for (const n of notes || []) {
    if (n.kind === 'alternative') {
      out.push(`The ${n.assembly} is not drawn: it is offered instead of the ${n.instead_of}, never on it.`);
    } else if (n.kind === 'entablature-whole') {
      const from = [...new Set(Object.values(n.triplet_owners || {}))];
      out.push(`The entablature is drawn whole, as ${n.owner} states it: the architrave, frieze and cornice it inherits from ${andList(from)} add up to a different height, so they are not drawn here.`);
    }
  }
  return out.join(' ');
}

/* The caption's datum sentence, per assembly as Python read it (WP-14.2). One function, so the
   plate and the census read the same words: tests/svg_census.py (R3) holds each assembly the plate
   draws to the datum this sentence names for it. It said "the corpus uses both" and cited two
   questions by number until the two Phase 14s met (27 Sep 2026): the other line had ruled that
   reader-facing copy states no corpus fact and cites no question a reader cannot look up
   (`readerCopy.test.mjs`), and had taken the same words out of this plate's caption. */
export function datumWords(datum, undeclared) {
  const cl = [];
  if (datum.axis.length) cl.push(`from the axis for the ${andList(datum.axis)}`);
  if (datum.naked.length) cl.push(`from each member’s own naked for the ${andList(datum.naked)}`);
  let out = cl.length
    ? `Projections are measured ${cl.join('; and ')} — each assembly is read on its own figures${undeclared ? '; this pack declares no datum at all' : ''}.`
    : '';
  if (datum.unjudged.length) {
    out += `${out ? ' ' : ''}No datum can be read for the ${andList(datum.unjudged)}: no member there publishes a projection.`;
  }
  return out;
}
