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
/** WHICH HOUSE THE COUNTS ARE OF (WP-14.1). Three states and never two.
 *
 *  `counts`, `disqualified` and every score axis on this card USED TO BE `plan_check.check`
 *  on the candidate's record with its placement STRIPPED (build/compose.py), while
 *  `plan_check.py:2593` derived the elevation from a fresh heuristic placement solved inside
 *  the critic -- so the verdict was of a house nobody drew, and the `drawn [...]` key two lines
 *  above it on the same card was the loop's, of the house the sheet draws. Measured on
 *  briefs/family-georgian.json, `centre-passage-double-pile` read declared [3, 25, 91, 24]
 *  against drawn [11, 71, 117, 24], and `truss-flattened-pitch` was FATAL on the first at
 *  0.4488 against at-least 0.45 and passed on the second.
 *
 *  WP-14.2 CLOSED THAT on the revised path: both readings are the placed house now and
 *  `counts` reconciles with `drawn_key_after` element for element. The field STAYS, and this
 *  paragraph stays in the past tense rather than being deleted, for two reasons -- a compose
 *  run with `--no-revise` still publishes the declared reading, so the three states are still
 *  three; and a field that says which house a number is of must not stop being said the moment
 *  the answer becomes uniform, or the next reader never learns it was a question.
 *
 *  `null` is not "declared". A record whose elevation could not be derived at all, and a
 *  server that predates this field, both arrive here as null, and asserting either reading
 *  over them is the fake-pass shape. */
export function verdictBasis(basis) {
  if (basis === 'placement') return 'counts measured on the placement this record carries';
  if (basis === 'declared')
    return 'counts measured on a fresh heuristic placement — not the house the drawn key is of';
  return 'counts: which placement they were measured on is not stated';
}

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
