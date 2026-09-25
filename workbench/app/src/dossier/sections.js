/* WHAT THE STYLE SURFACE SHOWS, DECIDED WITHOUT REACT (WP-14.12, PRD §D, §E.2).

   The style surface is three places on one path, and which one a selection names is decided ONCE,
   in the PRD's order (§E.2). The one spelling is `nav/navModel.js::stylePlaceKind` (WP-14.13), and
   `placeOf` below reads it. The two packages were built in parallel and each wrote the rule, and
   they met at the merge of the lead's tip. They agreed on every address a router writes and parted
   on ones it can read: a whitespace-only style id (`#/style/%20`) or slot id. On `#/style/%20` the
   shell's crumbs said the Styles index and this surface fetched a record named " ". The shell's
   reading is kept, because a blank id names no record:

     a style present                       -> the DOSSIER (no section means `identify`)
     no style, section `kit`, a slot       -> the SLOT PANEL (one slot across every style)
     anything else                         -> the STYLES INDEX

   THE INDEX NEVER SHOWS A RECORD. A bare `#/style` used to open Tidewater Georgian because the
   surface carried a DEFAULT_STYLE, so a link somebody pasted opened a record the link did not name
   and the back button left the last record on screen (the walk's W5). What this browser last read
   is `state/prefs.js`'s `styleInHand`, and the index OFFERS it as a link; nothing here reads it.

   THE SECTION STRIP IS THE PAYLOAD'S. `/api/styles/{id}/dossier` lists a section only when its
   count is greater than zero (`corpus.style_dossier`, §D.2) and `listedSections` holds that rule a
   second time on the way in, so a section the server ever serves at zero is still not offered: a
   strip that promises a section the section cannot deliver is the one thing it exists not to do.
   The order is `DOSSIER_SECTIONS`, whatever order the rows arrive in. `identify` is always listed
   and never counted. Every count a reader sees is the payload's -- none is computed here, and none
   is written in JSX (`copy_ratchet.test.mjs`).

   A SECTION THE URL NAMES AND THE STRIP DOES NOT LIST IS REFUSED, NOT RENDERED. `sectionInView`
   answers identify with `refused` naming what was asked for, so the surface can say so; rendering
   the kit of a tradition, which has none, would draw an empty table under a heading that claims a
   kit. The label of a section is its `section-<id>` glossary record's `term`, and this file writes
   no word a reader sees.

   Pure; imports the grammar's vocabulary, the router's address writer and the site map's one
   reading of a style place. */
import { DOSSIER_SECTIONS } from '../citations.js';
import { formatHash } from '../router.js';
import { stylePlaceKind } from '../nav/navModel.js';

export const IDENTIFY = 'identify';
export const KIT = 'kit';

/* The glossary record naming a section. */
export function sectionTermId(id) {
  return 'section-' + id;
}

const named = (v) => typeof v === 'string' && v !== '';

/* selection -> 'dossier' | 'slot' | 'index' (§E.2), as the site map reads it: the rail, the
   crumbs, the page head and this surface answer one question about one address with one function. */
export function placeOf(selection) {
  return stylePlaceKind(selection);
}

/* The dossier payload -> [{ id, count }] in DOSSIER_SECTIONS order: `identify` first and always,
   with no count; every other section only where the payload lists it with a count above zero. A
   row the vocabulary does not hold is dropped, and a repeated row is read once. */
export function listedSections(dossier) {
  const served = new Map();
  const rows = dossier && Array.isArray(dossier.sections) ? dossier.sections : [];
  for (const row of rows) {
    if (row && named(row.id) && !served.has(row.id)) served.set(row.id, row.count);
  }
  const out = [];
  for (const id of DOSSIER_SECTIONS) {
    if (id === IDENTIFY) { out.push({ id, count: null }); continue; }
    if (!served.has(id)) continue;
    const n = served.get(id);
    if (typeof n === 'number' && Number.isFinite(n) && n > 0) out.push({ id, count: n });
  }
  return out;
}

/* The section the URL asks for -> the one drawn: { id, refused }. An absent or `identify` request
   is identify; a listed one is itself; anything else is identify, with `refused` naming the
   request -- never the unlisted section drawn empty. */
export function sectionInView(requested, listed) {
  const want = named(requested) ? requested : IDENTIFY;
  if (want === IDENTIFY) return { id: IDENTIFY, refused: null };
  if ((listed || []).some((s) => s && s.id === want)) return { id: want, refused: null };
  return { id: IDENTIFY, refused: want };
}

/* Identify's summary cards: one per OTHER listed section, each carrying its own count. */
export function summaryCards(listed) {
  return (listed || []).filter((s) => s && s.id !== IDENTIFY);
}

/* The slot a selection opens in the kit section, or null: `slot` is honoured only there. */
export function slotInView(selection, sectionId) {
  const s = selection || {};
  return sectionId === KIT && named(s.slot) ? s.slot : null;
}

/* The address of a section of a style's dossier. Identify is written as the bare dossier -- a
   writer never emits `#/style/<id>/identify` (§E.2). */
export function sectionAddress(styleId, sectionId) {
  const sel = { style: styleId };
  if (named(sectionId) && sectionId !== IDENTIFY) sel.section = sectionId;
  return formatHash('style', sel, {});
}
