/* The Compare page's decisions, pure (WP-14.26, tranche 2 PRD §B.1, §C.7).

   `surfaces/Compare.jsx` draws; this file decides, so `src/compare.test.mjs` can hold every
   decision without a browser. The page is `#/compare/<a>/<b>[/<section>]`, and what it shows is
   `GET /api/compare/<a>/<b>` -- never a second reading of either kit.

   THE SECTIONS ARE DOSSIER SECTIONS. Identify, kit, proportions and plans are four of the style
   dossier's own sections, so each is worded by the same `section-*` record and a reader moving
   between a dossier and a compare meets one word for one thing. The page draws all four, one
   under another, and the section in the address is the one scrolled to: a comparison is read
   down the page, and a section alone would hide the other three halves of the answer. */
import { DOSSIER_SECTIONS } from '../citations.js';
import { formatHash } from '../router.js';

export const COMPARE_SECTIONS = Object.freeze(['identify', 'kit', 'proportions', 'plans']);
export const COMPARE_IDENTIFY = 'identify';

/* The two styles a place names, or null for either it does not. */
export function stylesOf(selection) {
  const s = selection && typeof selection === 'object' ? selection : {};
  const id = (v) => (typeof v === 'string' && v.trim() ? v.trim() : null);
  return { a: id(s.style), b: id(s.compare) };
}

/* The section to scroll to: the one the address names where it is a compare section, and
   Identify otherwise -- which is the top of the page, where a reader with no section begins. */
export function compareSectionOf(selection) {
  const s = selection && typeof selection === 'object' ? selection.section : null;
  return COMPARE_SECTIONS.includes(s) ? s : COMPARE_IDENTIFY;
}

/* A section's address. Identify is the bare form, as it is on the dossier. */
export function compareSectionHref(a, b, section) {
  const sel = { style: a, compare: b };
  if (section && section !== COMPARE_IDENTIFY) sel.section = section;
  return formatHash('compare', sel, {});
}

/* The kit rows in the two groups the page draws them in: the slots where the two styles give a
   different answer, and those where they give the same answer from different sources. The
   payload's own `differs_on` decides; nothing is compared here. */
export function kitGroups(kit) {
  const rows = kit && Array.isArray(kit.rows) ? kit.rows : [];
  const sourceOnly = (r) => Array.isArray(r.differs_on) && r.differs_on.length === 1
    && r.differs_on[0] === 'source';
  return { answer: rows.filter((r) => !sourceOnly(r)), source: rows.filter(sourceOnly) };
}

/* Which of the two styles wrote an explicit disambiguation: each entry is one style's record
   naming the other (`distinguished_from`), so an entry naming `b` is `a`'s, and the reverse. */
export function authorOf(entry, a, b) {
  const node = entry && typeof entry === 'object' ? entry.node : null;
  if (node === b) return a;
  if (node === a) return b;
  return null;
}

/* The compare sections are dossier sections, asserted where the module loads so a renamed
   section fails on import rather than drawing a word for a record that does not exist. */
for (const s of COMPARE_SECTIONS) {
  if (!DOSSIER_SECTIONS.includes(s)) throw new Error(`compare section ${s} is not a dossier section`);
}
