/* THE CANDIDATE CARD, as the Candidate Set renders it: the composer's served candidate adapted to
   the column's fields, in a leaf so `node --test` can run it (the audit of WP-16.8's own diff,
   3 Oct 2026, auditor C's M2). It lived inside `surfaces/CandidateSet.jsx`, where no test can
   import it, and the guard that R13's count is read off the served card was a regex over that
   file's source: it went red on a change that kept the count and green on a later
   `unjudged_fatal_n: 0` that broke it -- WP-16.8's E45 defect, the guard pinned to a spelling.
   Moved verbatim; `candidateOrder.test.mjs` drives it now. */
import { isNative, nativityOf, unjudgedFatalsOf } from './candidateOrder.js';
import { readRefusal } from './sheet/refusal.js';
import { revisedLine } from './revision.js';
import { JOURNEY_WORDS } from './journey/journey.js';

/* WHAT A PICKED COLUMN CAN DO, in one place so the strip that says it and the click that does it
   cannot disagree (the Candidate Set's selection is a click that SELECTS -- it reads the decision
   log and writes the address -- and loading the plan onto the bench is a second act).

     none     no column is picked: say how to pick one.
     open     a drawable candidate: the act is loading it on the bench, where the placement is
              proved and drawn.
     refused  a candidate the type's own facts turned down. NOT loadable, by WP-13.4's ruling
              (a record no surface on the bench may draw reads as the bench being broken), so the
              strip says WHY it cannot go on rather than offering a link that does nothing -- and
              says it in the refusal's own words (the facts it names), because a candidate can
              carry no fatal finding at all and still be refused: findings and facts are two
              measures, and "0 fatal" has never meant "may be drawn".

   `n` is the index the server's `/candidates/{n}/plan` is asked for. */
export function selectionAction(candidate) {
  const W = JOURNEY_WORDS.selection;
  if (!candidate) return { state: 'none', words: W.none, n: null, refused: null };
  const name = candidate.parti_name || candidate.parti || 'this candidate';
  const r = candidate.refused || null;
  if (r) {
    const why = Array.isArray(r.facts) && r.facts.length
      ? `${r.facts.join(', ')} ${r.kind === 'infeasible' ? 'cannot all hold' : 'not held'}`
      : null;
    return { state: 'refused', words: W.refused(name, why), n: candidate.n, refused: r };
  }
  return { state: 'open', words: W.open(name), n: candidate.n, refused: null };
}

/* How many of a set's cards the type's own facts turned down, off the cards in hand. A card is
   refused where `readRefusal` found a refusal on it -- a missing or unreadable one is not counted,
   because a verdict nobody gave is not a refusal (and is not a pass either). */
export function refusedCount(cards) {
  return Array.isArray(cards) ? cards.filter((c) => c && c.refused).length : 0;
}

/* `what` — the sentence saying what an axis measures — rides on the RESULT once rather than
   on eight rows per candidate, because it is constant across a run and the MCP tool bills a
   model for the payload. Merged back onto the rows here so the column stays a pure function
   of its own candidate, and defaulted so a result composed before this shipped still renders. */
export function adaptCandidate(c, i, nativePartis, axisWhat) {
  // WP-14.25: the served nativity, read off the candidate or the style's own list, never an
  // id's presence in a list -- a lineage parti is on the list and is not native
  const native = isNative(c, nativePartis);
  return {
    id: 'c' + i,
    // the index in the SERVER's order, which is what the `candidate` address key names
    n: i,
    parti: c.parti, parti_name: c.parti_name,
    score: c.score ?? null,
    score_axes: (c.score_axes || []).map((a) => (
      a.what || !axisWhat?.[a.axis] ? a : { ...a, what: axisWhat[a.axis] })),
    disqualified: !!c.disqualified,
    disqualified_because: c.disqualified_because,
    score_unscored_because: c.score_unscored_because,
    score_weight_evaluated: c.score_weight_evaluated,
    score_weight_unevaluated: c.score_weight_unevaluated,
    demerits: c.demerits,
    counts: c.counts,
    fatal_n: (c.counts && c.counts.fatal) || 0,
    // R13 (29 Sep 2026): the fatal faults the corpus could not judge on this candidate. They
    // break ties AGAINST it and are never a fatal: `disqualified` does not read them.
    unjudged_fatal: unjudgedFatalsOf(c),
    unjudged_fatal_n: unjudgedFatalsOf(c).length,
    native,
    nativity: nativityOf(c, nativePartis),
    named_by_brief: !!c.named_by_brief,
    why: c.why_this_diagram,
    trades_away: c.trades_away,
    area: `${(c.area_sf || 0).toLocaleString()} sf (${c.area_miss_pct}% off target)`,
    footprint: c.footprint
      ? `${c.footprint.footprint_ft?.[0]} × ${c.footprint.footprint_ft?.[1]} ft`
      : '',
    bays: c.footprint?.bays,
    warnings: (c.footprint?.notes || []),
    worst: c.worst || [],
    plan_rooms: c.plan_rooms,
    /* WP-13.4. A composed candidate whose placement breaks a hard fact of the type carries the
       refusal the composer's own placer wrote; `sheet/refusal.js` reads it and this surface
       derives nothing. Until this, `open in the workbench` loaded such a candidate straight
       onto the bench, where the reader met a blank plate and a status line — the refusal was on
       the record the whole time and no surface had read it. */
    refused: readRefusal(c.refused),
    // WP-9.2/9.3: what the placed revision loop bought on this candidate. `score_before` is
    // the same instrument as `score` (both on the stripped declared record); `rank_before`
    // is the SERVER's order before revision and is labelled as such, because `rank` on
    // this surface is a position in the current order and a bare number would be read as
    // one. null everywhere when the compose ran --no-revise.
    score_before: typeof c.score_before === 'number' ? c.score_before : null,
    counts_before: c.counts_before || null,
    rank_before: c.rank_before ?? null,
    drawn_key_before: c.drawn_key_before || null,
    drawn_key_after: c.drawn_key_after || null,
    revision: c.revision || null,
    revision_skipped: c.revision_skipped || null,
    revised: !!c.revision,
    revisedLine: revisedLine(c),
    raw: c,
  };
}
