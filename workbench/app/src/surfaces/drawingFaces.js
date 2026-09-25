/* THE SHEET AND THE FACE, AS THE ADDRESS HOLDS THEM (WP-14.27, PRD §C.12, tranche 1 §E.4).

   The Drawing Set kept which sheet and which elevation face a reader had chosen in
   `useState`, so a reload, a Back or a link sent to a colleague threw the choice away and
   showed the model again: the one surface whose whole errand is "look at THIS drawing" could
   not be pointed at a drawing. Export had no face at all and drew whichever face the record
   calls the entrance front, so three of the four elevations the generator draws could be seen
   and never taken away. Both surfaces read the choice from the query now -- `sheet` and `face`,
   each a filter axis beside `view` -- and this file is the one place that says what those two
   words may hold and what each is called.

   THE FACES ARE WORDED BY THEIR GLOSSARY RECORDS. The chips said "south", "north", "east" and
   "west" as literals, and "the entrance front" beside the front; each is a record now
   (`face-south` ... `face-west`, `entrance-front`, and `elevation-face` for the group), so the
   chip carries the record's word and its definition says which side of the plan it is and that
   plan north is true north unless a bearing turns the house. The id is the compass letter the
   elevation record and the route both use; nothing here translates it.

   WHAT IS SENT. A face means something only to an elevation: `/api/drawings/elevation` and
   `/api/export/dxf` with `kind: elevation` forward it to `render_elevation` and
   `export_elevation_dxf`, and every other sheet ignores it -- so it is sent with an elevation
   and nowhere else, and an absent face is the server's own default (the entrance front), which
   is not a choice the reader made and is not written into the request.

   Pure: no React, no fetch, no import from node_modules, so `node --test` drives every line. */
import { KINDS } from './drawingKinds.js';
import { wordOf, noGlossary } from '../glossary/termView.js';

export const MODEL_SHEET = 'model';

/* Compass order as `build/elevation.py`'s FACES tuple has it: ("S", "N", "E", "W"). */
export const FACES = Object.freeze([
  Object.freeze({ id: 'S', term: 'face-south' }),
  Object.freeze({ id: 'N', term: 'face-north' }),
  Object.freeze({ id: 'E', term: 'face-east' }),
  Object.freeze({ id: 'W', term: 'face-west' }),
]);
export const FACE_TERM = 'elevation-face';
export const ENTRANCE_FRONT_TERM = 'entrance-front';

const FACE_IDS = FACES.map((f) => f.id);

/** The face the address names, or null -- an unreadable value is no face, never a guess. */
export function parseFace(raw) {
  return typeof raw === 'string' && FACE_IDS.includes(raw) ? raw : null;
}

/** The sheet the address names: the model where it names none or names something the Drawing
 *  Set cannot draw, because the model is what the surface shows a reader who chose nothing. */
export function parseSheet(raw) {
  if (raw === MODEL_SHEET) return MODEL_SHEET;
  return typeof raw === 'string' && KINDS.some((k) => k.id === raw) ? raw : MODEL_SHEET;
}

/** What the address is given for a sheet: nothing for the model, which is the default, so a
 *  reader who picks the model again is at the bare address rather than a longer spelling of it. */
export function sheetParam(kind) {
  return parseSheet(kind) === MODEL_SHEET ? null : kind;
}

/** The body fields `/api/drawings/<kind>` takes beyond the plan: a face, for an elevation. */
export function drawingOpts(kind, face) {
  const f = parseFace(face);
  return kind === 'elevation' && f ? { face: f } : {};
}

/** The body fields `/api/export/<fmt>` takes beyond the plan: the sheet, and a face with an
 *  elevation. The IFC model takes neither -- it is the whole house, not a sheet of it. */
export function cadOpts(fmt, kind, face) {
  if (fmt !== 'dxf' || !kind) return {};
  return { kind, ...drawingOpts(kind, face) };
}

/** The file a sheet is saved as. An elevation carries its face, or the four faces of one house
 *  would all download as the same name and each would overwrite the last. */
export function sheetFileName(planId, kind, face) {
  const f = kind === 'elevation' ? parseFace(face) : null;
  return `${planId}-${kind}${f ? '-' + f : ''}.svg`;
}

/** A face chip's words: the face's record, and the entrance front's beside the face the record
 *  calls the front. `word` is the caller's reader of a record (the glossary's word, or the
 *  state it is in); `sep` is the journey's separator. */
export function faceChipWords(word, faceId, entranceFace, sep) {
  const f = FACES.find((x) => x.id === faceId);
  const own = f ? word(f.term) : String(faceId);
  return entranceFace && entranceFace === faceId ? own + sep + word(ENTRANCE_FRONT_TERM) : own;
}

/** A reader of a record's word over `useGlossary()`'s answer, in its three states: the record's
 *  `term` (or `noEntry`, visibly), the glossary's own failure named, or an ellipsis while it is on
 *  its way -- `JourneyBar`'s rule, for a control a `Term` may not sit inside (a chip is a button). */
export function recordWord(glossary) {
  return (id) => {
    if (glossary && glossary.status === 'ready' && glossary.lookup) return wordOf(glossary.lookup, id);
    if (glossary && glossary.status === 'failed') return noGlossary(id);
    return '…';
  };
}
