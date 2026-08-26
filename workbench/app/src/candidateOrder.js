/* The Candidate Set's pure logic, lifted out of the React files so it can be TESTED.
   It had no tests at all, and every function here has a stated failure mode that shipped:

   - whyText: `why_this_diagram` is a LIST of reasons and was handed to React whole. React
     concatenates an array of strings with nothing between them, so the native case read
     "native to tidewater-georgianfour-over-four is a canonical massing for the style"; the
     borrowed case interpolated the array into a template literal, which joins on commas AND
     repeats the "NOT native to this style" the surrounding span had just said in gold.
   - isNative's fallback ran a regex straight at that array and worked only because
     RegExp.test coerces via Array.prototype.toString.
   - the orderings decide which column reads as first, which is the whole subject of the
     change these were written for.

   No React import, no JSX: `node --test` runs this file's suite directly. */

/** The reasons list, joined as prose. `dropNativity` strips only the clause the caller has
 *  already printed in its own colour — never the sentence it opens, because "the composer is
 *  borrowing a diagram" is the part worth reading. */
export function whyText(why, dropNativity) {
  return (Array.isArray(why) ? why : [why]).filter(Boolean).map(String)
    .map((w) => (dropNativity ? w.replace(/^NOT native to this style\s*[—-]\s*/i, '') : w))
    .filter((w) => w.trim())
    .join('; ');
}

/** True when the diagram belongs to the brief's own style. `nativePartis` is authoritative
 *  when /api/partis has resolved; the reasons list is the fallback until it does. */
export function isNative(candidate, nativePartis) {
  if (nativePartis) return nativePartis.has(candidate.parti);
  const lines = Array.isArray(candidate.why_this_diagram)
    ? candidate.why_this_diagram : [candidate.why_this_diagram].filter(Boolean);
  return !lines.some((w) => /NOT native to this style/i.test(String(w)));
}

/** Highest score first, then the superseded demerit total, then the parti id. The last two
 *  are there so no ordering is ever settled by the order the composer happened to return —
 *  the same list drawn twice must be the same list. A candidate with no score sorts last. */
export function byScore(a, b) {
  const as = typeof a.score === 'number' ? a.score : -Infinity;
  const bs = typeof b.score === 'number' ? b.score : -Infinity;
  return (bs - as) || ((a.demerits || 0) - (b.demerits || 0))
    || String(a.parti || '').localeCompare(String(b.parti || ''));
}

const DQ_LAST = 'Any plan carrying a fatal finding sorts last whatever it scores, and says '
              + 'so on its own column.';

export const ORDERS = {
  score: {
    chip: 'highest score first',
    says: `Ordered by score, highest first. ${DQ_LAST}`,
    cmp: byScore,
  },
  native: {
    chip: 'native to the style',
    says: 'Ordered by whether the diagram is native to the style, then by score — so the '
        + `column numbered 1 is the most native, not the highest scoring. ${DQ_LAST}`,
    cmp: (a, b) => ((b.native ? 1 : 0) - (a.native ? 1 : 0)) || byScore(a, b),
  },
  fatal: {
    chip: 'fatal first',
    says: 'Fatal findings decide the order before the score does — a plan carrying two '
        + 'sorts below a plan carrying one, and both below a plan carrying none.',
    cmp: (a, b) => ((a.fatal_n || 0) - (b.fatal_n || 0)) || byScore(a, b),
  },
};

/** ONE RULE OUTRANKS ALL THREE ORDERINGS: a disqualified candidate sorts last under every one
 *  of them, whatever it scores and however native it is. It has to, because a disqualified
 *  plan is scored like any other and its number can be the highest on the screen; letting it
 *  head the columns under "highest score first" would rebuild, in the ordering, exactly the
 *  misreading this surface was fixed to prevent. Applied OUTSIDE each comparator so a new
 *  ordering cannot forget it. */
export function order(cmp) {
  return (a, b) => ((a.fatal_n ? 1 : 0) - (b.fatal_n ? 1 : 0)) || cmp(a, b);
}
