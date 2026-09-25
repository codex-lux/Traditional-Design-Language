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
   - isNative read a SET OF IDS from `/api/partis` as the answer, which was right while that
     list held native partis alone. WP-14.19 made it list a style's lineage partis beside its
     native ones, each carrying `nativity`, so a lineage candidate read as native the moment the
     list resolved (WP-14.25). The relation is served now -- on the candidate itself, and on
     every row of the list -- and `nativityOf` reads it and never re-derives it: which diagram
     belongs to which style is `compose.nativity`'s answer, the one spelling there is.

   No React import, no JSX: `node --test` runs this file's suite directly. */

/* The three answers `compose.nativity` gives, each to the glossary record that says what it
   means. Every surface that labels a parti's nativity -- the Brief's select, the dossier's plan
   types, a candidate's column -- takes the word from here, so there is one map and no surface
   words a nativity of its own. */
export const NATIVITY_TERMS = Object.freeze({
  native: 'parti-native',
  lineage: 'parti-lineage',
  borrowed: 'parti-borrowed',
});

const NATIVITIES = Object.keys(NATIVITY_TERMS);
const served = (v) => (typeof v === 'string' && NATIVITIES.includes(v) ? v : null);

/** The nativity the server stated for this candidate's diagram, or null where nothing did.
 *  The candidate's own `nativity` first (the composer writes it on every candidate), then the
 *  row `/api/partis` gave for its parti (`rows`, a Map of parti id to that row's `nativity`).
 *  A row the list does not hold is NOT read as borrowed: the list may simply not have been
 *  asked for borrowed rows, and an absence is not an answer. */
export function nativityOf(candidate, rows) {
  const own = served(candidate && candidate.nativity);
  if (own) return own;
  if (rows instanceof Map && candidate && rows.has(candidate.parti)) return served(rows.get(candidate.parti));
  return null;
}

/** The reasons list, joined as prose. `dropNativity` strips only the clause the caller has
 *  already printed in its own colour — never the sentence it opens, because "the composer is
 *  borrowing a diagram" is the part worth reading. */
export function whyText(why, dropNativity) {
  return (Array.isArray(why) ? why : [why]).filter(Boolean).map(String)
    .map((w) => (dropNativity ? w.replace(/^NOT native to this style\s*[—-]\s*/i, '') : w))
    .filter((w) => w.trim())
    .join('; ');
}

/** True when the diagram was drawn for the brief's own style -- `native`, and never `lineage`,
 *  which is a diagram drawn for a style this one answers to. The served nativity decides
 *  (`nativityOf`); the reasons list is the fallback only where nothing served one. */
export function isNative(candidate, rows) {
  const n = nativityOf(candidate, rows);
  if (n) return n === 'native';
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

/** THE NATIVITY LINE A COLUMN PRINTS (WP-14.27). The column typed "NOT native to this style" in
 *  gold before every candidate that was not native, and a LINEAGE diagram is not native -- so a
 *  plan type drawn for the style's own ancestor read "NOT native to this style — native to an
 *  ancestor or relative of the style", which contradicts itself in one line and says the one
 *  thing about the diagram that is false. The served nativity decides the word now, and the word
 *  is its glossary record's (`NATIVITY_TERMS`); the composer's reasons follow it, with only the
 *  borrowed clause the record already says dropped. Where nothing served a nativity there is no
 *  record to name, and the composer's own sentence is printed whole with no word of ours before it. */
export function nativityLine(candidate) {
  const n = served(candidate && candidate.nativity);
  return {
    nativity: n,
    term: n ? NATIVITY_TERMS[n] : null,
    prose: whyText(candidate ? candidate.why : null, n === 'borrowed'),
  };
}

/** WHAT THE STRIP ABOVE THE COLUMNS COUNTS (WP-14.27). It printed `returned {candidates.length}
 *  of {asked} asked for`, and since WP-14.19 a parti the brief names is APPENDED after the set
 *  when the composer's own ranking passes it over -- so asking for one returned two and the strip
 *  read "returned 2 of 1 asked for", a count that cannot be true of anything. The composer says
 *  which candidate it appended (`named_parti`: `returned`, `appended`, and which parti), so the
 *  set's own count is the candidates less that one, and the appended one is named beside it by
 *  the record that says what it is. `asked` is the caller's -- the brief's own count. */
export function setSize(result, asked) {
  const cands = Array.isArray(result && result.candidates) ? result.candidates : [];
  const np = result && result.named_parti;
  const at = np && np.returned === true && np.appended === true
    ? cands.findIndex((c) => c && c.parti === np.parti) : -1;
  const extra = at >= 0 ? cands[at] : null;
  return {
    own: cands.length - (extra ? 1 : 0),
    asked,
    appended: extra ? { parti: extra.parti, name: extra.parti_name || extra.parti, index: at } : null,
  };
}
