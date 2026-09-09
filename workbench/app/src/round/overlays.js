/* The overlays and modifiers, as arithmetic (WP-12.5).

   The brief is `docs/prd/phase-12-the-sheet-in-the-round.md` §§7.5, 7.6. Everything here is a
   pure function of the scene record, the placed plan and `lastEval.rooms_meta`; nothing here
   knows what a GPU is, which is `build/scene.py`'s own reason for being a leaf and the reason
   `round/solids.js` found a winding defect a picture would only have shown as a wrong sun.

   IT DERIVES NO ANALYTIC RULE OF ITS OWN. The daylight reach, the privacy ramp and the wet
   predicate come from `../sheet/overlayRules.js`, which surface ⑦ also reads, so the two
   surfaces cannot disagree about which rooms are wet or how deep the light goes. The room
   shapes and the lit-wall gate come from `../sheet/derive.js`, which the sheet has used since
   WP-5.2. A second spelling of any of them is this repository's most-repeated defect.

   THREE OF THE PRD'S OWN SENTENCES ARE OVERTAKEN BY THE TREE and are corrected here rather
   than followed, exactly as WP-12.4 had to correct two:

     · §7.5 says the grid draws "bay lines ... `scene.grid`" as though the record held lines.
       It holds `{bays, module_ft}` — a COUNT and a MODULE. The lines come from
       `derive.js::bayLines`, which is the sheet's own spelling of that arithmetic.
     · §7.6 says the exploded drop-line count "matches `geometry_report.vertical`". That field
       is a LIST OF ENGLISH SENTENCES — `build/disclosures.py::transfers` regexes
       `^(\d+) upper wall line` out of it and says in its own docstring that the count "lives
       only inside an English sentence". A count cannot match a list of prose.
     · §7.6 explodes an element "along the axis of its `attached_to` face". A scene element is
       `{id, role, rect}` and carries NO `attached_to`. The direction is derived from the
       rect's own offset from the main block, and REFUSED by name where that offset is zero.
*/

import {
  bayLines, elementBounds, levelRooms, litWalls,
} from '../sheet/derive.js';
import {
  daylightReachFt, isWet, privacyOpacity, privacyRefusal,
} from '../sheet/overlayRules.js';

/* Which overlays are true from any angle. The other four are read off a plan and mean nothing
   turned on their side, which is §7.5's own rule ("overlays do not exist in `free` view except
   grid, relaxations and privacy"). */
export const FREE_VIEW_OVERLAYS = ['grid', 'relaxations', 'privacy'];

export const OVERLAY_IDS = ['grid', 'datums', 'daylight', 'wet', 'privacy', 'relaxations', 'plate'];

function storeys(scene) {
  return (scene && scene.storeys) || [];
}

function storeyAt(scene, level) {
  return storeys(scene).find((s) => s.index === level) || null;
}

function elements(scene) {
  return (scene && scene.elements) || [];
}

/* ------------------------------------------------------------------ grid (§7.5)

   Bay lines on the grade plane and up to the eave. The module is the record's; the LINES are
   `derive.js::bayLines`, handed the shape it already takes. */
export function bayGrid(scene) {
  const g = (scene && scene.grid) || {};
  const el = elements(scene).find((e) => e.role === 'main') || elements(scene)[0];
  if (!el) return { lines: [], refused: 'the scene states no massing element to lay a grid on' };
  if (!g.module_ft) {
    return { lines: [], refused: 'the record states no bay module, so no grid can be drawn' };
  }
  const top = (scene.datums || []).find((d) => d.class === 'eave');
  const z1 = top ? top.z_ft : ((scene.bounds && scene.bounds.max && scene.bounds.max[2]) || 0);
  const xs = bayLines({ width_ft: el.rect.width_ft, bay_module_ft: g.module_ft });
  return {
    lines: xs.map((x) => ({
      x_ft: el.rect.x_ft + x,
      y0_ft: el.rect.y_ft,
      y1_ft: el.rect.y_ft + el.rect.depth_ft,
      z0_ft: 0,
      z1_ft: z1,
    })),
    bays: g.bays,
    module_ft: g.module_ft,
  };
}

/* ------------------------------------------------------------------ datums (§7.5)

   The record's own, with its own label. `build/scene.py::_feet` writes that string precisely
   so a viewer never has to know how this corpus spells a dimension — do not reformat it. */
export function datumLines(scene) {
  return (scene && scene.datums ? scene.datums : []).map((d) => ({
    id: d.id, z_ft: d.z_ft, label: d.label, class: d.class, kind: d.kind,
  }));
}

/* ------------------------------------------------------------------ daylight (§7.5)

   A volume inward from each wall the placement actually LIT, floor to ceiling. Gated on
   `litWalls` for the reason the sheet states: the overlay may never claim daylight from a
   window the drawing does not draw.

   A reach of zero draws nothing — three room records state `depth_multiplier: 0` and that is
   the record's own answer, not a missing value (see overlayRules.js). */
export function daylightVolumes(scene, plan, meta) {
  const out = [];
  const placement = plan;
  for (const st of storeys(scene)) {
    const rooms = levelRooms(plan, placement, st.index);
    if (!rooms.length) continue;
    const fp = (plan.footprint) || {};
    const boxes = elementBounds(rooms, fp);
    const W = fp.width_ft || 0;
    const H = fp.depth_ft || 0;
    const z0 = st.floor_z_ft;
    const z1 = st.ceiling_z_ft;
    if (z0 == null || z1 == null) continue;
    for (const r of rooms) {
      const reach = daylightReachFt(r, (meta || {})[r.type]);
      if (!(reach > 0)) continue;
      for (const wall of litWalls(r, W, H, 0.6, boxes[r.id])) {
        const d = Math.min(wall === 'N' || wall === 'S' ? r.h : r.w, reach);
        const box = wall === 'S' ? { x: r.x, y: r.y, w: r.w, d }
          : wall === 'N' ? { x: r.x, y: r.y + r.h - d, w: r.w, d }
            : wall === 'W' ? { x: r.x, y: r.y, w: d, d: r.h }
              : { x: r.x + r.w - d, y: r.y, w: d, d: r.h };
        out.push({
          room: r.id, level: st.index, wall, reach_ft: reach,
          x_ft: box.x, y_ft: box.y, width_ft: box.w, depth_ft: box.d,
          z0_ft: z0, z1_ft: z1,
        });
      }
    }
  }
  return out;
}

/* ------------------------------------------------------------------ wet (§7.5)

   Floor-to-floor prisms on the rooms `isWet` names — the same predicate surface ⑦ marks with,
   so the two surfaces cannot disagree about which rooms are on the stack. */
export function wetPrisms(scene, meta) {
  const out = [];
  for (const sp of (scene && scene.spaces ? scene.spaces : [])) {
    if (!isWet((meta || {})[sp.type])) continue;
    const g = sp.geometry || {};
    if (g.z0 == null || g.z1 == null) continue;
    out.push({ room: sp.id, level: sp.level, polygon: g.polygon, z0_ft: g.z0, z1_ft: g.z1 });
  }
  return out;
}

/* ------------------------------------------------------------------ privacy (§7.5)

   Each space's FLOOR washed by its rank. Three states: a wash, an unranked room (unjudged),
   and a rank the ramp does not cover (refused) — never two. */
export function privacyWashes(scene, meta) {
  const drawn = [];
  const refused = [];
  for (const sp of (scene && scene.spaces ? scene.spaces : [])) {
    const rank = ((meta || {})[sp.type] || {}).privacy_rank;
    const op = privacyOpacity(rank);
    if (op == null) {
      refused.push({ room: sp.id, rank: rank ?? null, why: privacyRefusal(rank) });
      continue;
    }
    const g = sp.geometry || {};
    drawn.push({ room: sp.id, level: sp.level, polygon: g.polygon, z_ft: g.z0, opacity: op });
  }
  return { drawn, refused };
}

/* ------------------------------------------------------------------ relaxations (§7.5)

   The record's marks, at the record's positions. A mark the placement could not locate is
   NAMED and never placed somewhere plausible — WP-6.3's rule, and the reason `_marks` splits
   them in the first place. */
export function relaxationMarks(scene) {
  const marks = (scene && scene.marks) || [];
  const drawn = marks.filter((m) => m.x_ft != null || m.y_ft != null);
  const unlocated = marks.filter((m) => m.x_ft == null && m.y_ft == null);
  return { drawn, unlocated };
}

/* ------------------------------------------------------------------ explode (§7.6)

   BY LEVEL: each storey lifts by `k × storey_height_ft`, and the roof rides on the top storey
   rather than lifting again — a roof that separates from the storey it sits on is drawing a
   building with an extra floor.

   BY ELEMENT: away from the main block along the axis of its own offset. The record carries no
   `attached_to` (the PRD assumed one), so the direction is DERIVED from the rects and refused
   where it cannot be: an element concentric with the main block has no direction to move in,
   and inventing one would put a wing somewhere the record does not say it is. */
export function explodeOffsets(scene, opts) {
  const mode = (opts && opts.mode) || 'none';
  const k = (opts && opts.k) || 0;
  if (mode === 'none' || !k) return { mode: 'none', byLevel: {}, byElement: {}, note: null };

  if (mode === 'levels') {
    const byLevel = {};
    let below = 0;
    for (const st of [...storeys(scene)].sort((a, b) => a.index - b.index)) {
      byLevel[st.index] = [0, 0, below];
      below += k * (st.storey_height_ft || 0);
    }
    const top = [...storeys(scene)].sort((a, b) => b.index - a.index)[0];
    return {
      mode, byLevel,
      roofRidesOn: top ? top.index : null,
      byElement: {},
      note: `each storey lifted by ${k.toFixed(2)} × its own height; the roof rides on the top storey`,
    };
  }

  const els = elements(scene);
  const main = els.find((e) => e.role === 'main') || els[0];
  if (!main || els.length < 2) {
    return {
      mode, byLevel: {}, byElement: {},
      note: 'one element — nothing to separate',
    };
  }
  const cx = main.rect.x_ft + main.rect.width_ft / 2;
  const cy = main.rect.y_ft + main.rect.depth_ft / 2;
  const byElement = {};
  const refused = [];
  for (const e of els) {
    if (e.id === main.id) { byElement[e.id] = [0, 0, 0]; continue; }
    const dx = (e.rect.x_ft + e.rect.width_ft / 2) - cx;
    const dy = (e.rect.y_ft + e.rect.depth_ft / 2) - cy;
    if (Math.abs(dx) < 1e-9 && Math.abs(dy) < 1e-9) {
      refused.push({ element: e.id, why: 'concentric with the main block: the record states no direction to separate it along' });
      byElement[e.id] = [0, 0, 0];
      continue;
    }
    // the DOMINANT axis, so a wing beside the house moves sideways rather than diagonally
    const along = Math.abs(dx) >= Math.abs(dy) ? [Math.sign(dx), 0, 0] : [0, Math.sign(dy), 0];
    byElement[e.id] = [along[0] * k * ELEMENT_STEP_FT, along[1] * k * ELEMENT_STEP_FT, 0];
  }
  return {
    mode, byLevel: {}, byElement, refused,
    note: `${els.length} elements separated by ${k.toFixed(2)} × ${ELEMENT_STEP_FT} ft`,
  };
}

/* §7.6's own figure, and it is EDITORIAL: a separation distance is a reading aid and no record
   states one. Named rather than inline so it cannot read as a dimension of the building. */
export const ELEMENT_STEP_FT = 12;

/* ------------------------------------------------------------------ cut (§7.6)

   A section plane through the model. `level` takes the plan cut the record already states, so
   the Round's plan view and the plates below it cut at the same height. */
export function cutPlane(scene, opts) {
  const axis = (opts && opts.axis) || null;
  if (!axis) return null;
  if (axis === 'level') {
    const z = scene && scene.cut_height_ft;
    if (z == null) return { refused: 'the scene states no cut height' };
    return { axis: 'z', at_ft: z, from: 'scene.cut_height_ft' };
  }
  const at = opts && opts.at;
  if (at == null) return { refused: `a ${axis} cut needs a position` };
  return { axis, at_ft: at, from: 'the reader' };
}

/* ------------------------------------------------------------------ transfer beams (§7.6)

   THE COUNT IS READ, NOT RECOMPUTED. `build/disclosures.py::transfers` already states it, and
   WP-11.12's rule is that a second computation of a charged quantity can convict a placement
   on numbers it was not chosen by. The disclosure carries the figure inside its own sentence,
   which is `oq/the-transfer-count-lives-only-inside-an-english-sentence`; this reads that one
   sentence rather than re-deriving the walls.

   Returns `null` where the record makes no such disclosure — which is a house with no transfer
   beams AND a record that did not say, and those are told apart by the caller having the
   disclosure list at all. */
export function transferCount(disclosures) {
  for (const d of (disclosures || [])) {
    if (d && d.id === 'transfers') {
      const m = /^(\d+)\s+UPPER WALL LINE/i.exec(String(d.text || ''));
      if (m) return parseInt(m[1], 10);
      return null;
    }
  }
  return 0;
}
