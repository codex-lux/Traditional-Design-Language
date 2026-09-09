/* What a view is called, and what furniture is true in it.

   WP-12.4. The brief is docs/prd/phase-12-the-sheet-in-the-round.md §§7.3, 7.7.

   A LEAF, like frame.js, and for the same reason. It may import ../sheet/derive.js and its
   siblings and nothing else -- in particular NOT ../sheet/label.js, which imports React and
   reaches for a 2d canvas: a static edge from round.test.mjs to that file turns
   no_bare_imports.test.mjs red AND breaks the corpus CI job, which runs the app suite with
   no npm install. That is the coastTiers.js trap, and it is written here rather than in a
   commit message because the next reader who wants a fitted label in a caption will reach
   for exactly that import. Fit labels in RoundPlate.jsx, which is allowed to.

   EVERY NAME HERE IS READ AND NOT INVENTED. The face's label and its role come off
   scene.faces; the storey's word comes off scene.storeys[].id, which build/scene.py takes
   from the section -- so a house whose storeys the corpus calls `ground` and `upper` gets
   those words and this file never has to decide whether L1 is the first floor or the
   second, which is a question the answer to depends on which side of the Atlantic the
   reader learned to draw. */

import { ft } from '../sheet/derive.js';

const COMPASS = {
  sw: 'SOUTH-WEST',
  se: 'SOUTH-EAST',
  nw: 'NORTH-WEST',
  ne: 'NORTH-EAST',
};

/* The plan cut is a fact about the drawing and the reader is told it, every time. A plan
   that does not say where it was cut is the commonest silent lie in an architectural set. */
function planCaption(view, scene) {
  const m = /^plan-l(\d+)$/.exec(view);
  const lvl = +m[1];
  const st = (scene.storeys || []).find((s) => s.index === lvl);
  const word = st && st.id ? String(st.id).toUpperCase() : `LEVEL ${lvl}`;
  const h = scene.cut_height_ft;
  const where =
    h == null
      ? 'CUT HEIGHT NOT STATED BY THE RECORD'
      : `CUT AT ${ft(h)} ABOVE FINISHED FLOOR`;
  return `${word} FLOOR PLAN · ${where}`;
}

function faceCaption(view, scene) {
  const F = view.toUpperCase();
  const f = (scene.faces || {})[F] || {};
  const label = f.label || `${F} ELEVATION`;
  /* The role is the record's own -- `THE ENTRANCE FRONT` -- and is appended only where the
     record states one. A face with no role gets its label alone rather than an invented
     description of what it faces. */
  return f.role ? `${label} · ${f.role}` : label;
}

export function caption(view, scene) {
  if (!view || view === 'free') {
    /* The one caption that is a refusal. A free view is not a named drawing, so nothing on
       it may be read as a dimension: an orbited house is still true about what it is made
       of and no longer true about what it measures. */
    return 'FREE VIEW · NOT A NAMED DRAWING · DIMENSIONS WITHHELD';
  }
  if (/^plan-l\d+$/.test(view)) return planCaption(view, scene);
  if (/^[snew]$/.test(view)) return faceCaption(view, scene);
  if (/^axon-(sw|se|nw|ne)$/.test(view)) {
    return `AXONOMETRIC · FROM THE ${COMPASS[view.slice(5)]}`;
  }
  if (view === 'roof') return 'ROOF PLAN';
  return 'FREE VIEW · NOT A NAMED DRAWING · DIMENSIONS WITHHELD';
}

/* The short name the view bar prints on the chip itself. */
export function chipLabel(view, scene) {
  const m = /^plan-l(\d+)$/.exec(view);
  if (m) return `PLAN·L${m[1]}`;
  if (/^[snew]$/.test(view)) return view.toUpperCase();
  if (/^axon-/.test(view)) return `AXON·${view.slice(5).toUpperCase()}`;
  return view.toUpperCase();
}

/* What is drawn in each view, per the brief's own table. A view shows exactly the furniture
   that is TRUE in it, which is the whole reason this is a table and not one set of
   annotations shown everywhere:

   - a scale bar is honest in a parallel projection along an axis and nowhere else, so an
     axon gets three axis rules and never a single bar;
   - room names belong to a plan, because a plan is the only view in which a room is a shape
     rather than an edge;
   - dimension strings are withheld in `free` for the reason the caption gives. */
const FURNITURE = {
  plan: { roomNames: true, dimRuns: true, north: true, scaleBar: true, marks: true },
  face: { bayTicks: true, overallWidth: true, datums: true, scaleBar: true },
  axon: { axisRules: true, compass: true },
  roof: { roofLines: true, chimneys: true, north: true, scaleBar: true },
  free: { compass: true },
};

export function furnitureFor(view) {
  if (/^plan-l\d+$/.test(view || '')) return { ...FURNITURE.plan };
  if (/^[snew]$/.test(view || '')) return { ...FURNITURE.face };
  if (/^axon-/.test(view || '')) return { ...FURNITURE.axon };
  if (view === 'roof') return { ...FURNITURE.roof };
  return { ...FURNITURE.free };
}

/* The plate that overlays this view, keyed as workbench/server/corpus.py's SCENE_PLATES
   keys it, so the scene response's `plates` map is read by the same string the server
   wrote. There is ONE spelling of this key and it is this function -- a second one in the
   surface is how the two come to disagree about `elevation:S`.

   A view with no plate returns null and says so; an axon is not a drawing this project
   makes flat, and pretending otherwise would put a plate on a view it was not drawn for. */
export function plateKeyFor(view) {
  if (/^plan-l\d+$/.test(view || '')) return 'plan';
  if (/^[snew]$/.test(view || '')) return `elevation:${view.toUpperCase()}`;
  if (view === 'roof') return 'roof';
  return null;
}

/* The model's own disclosure, after the banner lines the server sends. Counts rather than
   lists, because the list is in the record card -- but it is never silent when there is
   something to say, and it says nothing at all when there is not, rather than printing a
   reassuring zero. */
export function notModelledLine(scene) {
  const n = (scene.not_modelled || []).length;
  if (!n) return null;
  return `${n} thing${n === 1 ? '' : 's'} the record holds ${n === 1 ? 'is' : 'are'} not modelled — listed in the card`;
}
