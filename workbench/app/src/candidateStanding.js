/* WHETHER THE TYPE'S OWN FACTS HAVE EVER BEEN ASKED OF A SERVED CANDIDATE, in one place.

   A composed candidate carries `refused` and the field means three different things, and the
   audit of the candidate-click change (15 Oct 2026) found the app reading two of them as one:

     refused    a refusal this app can read: the placement broke a hard fact of the type
                (WP-13.4) and the candidate cannot be drawn.
     placed     the placed revision loop ran on this candidate (`revision` is the loop's report),
                it came back with a placement and that placement is not refused.
     unjudged   NOBODY ASKED, or the answer cannot be read. `refused` is `null` here too, and it
                is a different null: `compose.py` writes the declared pass's `refused` as `None`
                on purpose ("a refusal about a house nobody has placed would be a verdict with no
                subject"), a candidate the set's revise budget did not reach is returned as
                composed, a compose that ran without the loop (`revise: false`) places nothing, a
                loop whose first placement could not be evaluated judged nothing, and a body whose
                `kind` this app does not know is not a verdict either.

   Reading `refused === null` as "may be drawn" collapses the third into the second, which is the
   one thing this corpus will not do (unjudged is not passed) and which was also the screen the
   candidate-click change was written to prevent: a reader opens a candidate the strip called
   openable and meets the bench's refusal. The bench places the house and may refuse it; the
   strip says so for an `unjudged` candidate instead of promising a plan.

   Pure: no React, no DOM. The only reader of the refusal's own shape is `readRefusal`. */
import { readRefusal } from './sheet/refusal.js';

const isObj = (v) => Boolean(v) && typeof v === 'object' && !Array.isArray(v);

/* The revision report's `stop_reason` when the loop's first placement could not be judged
   (`build/revise.py`): the loop ran, produced a record, and said it had nothing to hold a
   verdict against. The string is the server's and is matched, never composed. */
export const PLACEMENT_UNJUDGED = 'placement-could-not-be-evaluated';

/* 'refused' | 'placed' | 'unjudged' for one served (raw) candidate. */
export function standingOf(c) {
  if (!isObj(c)) return 'unjudged';
  if (readRefusal(c.refused)) return 'refused';
  // a verdict was given and this app cannot read it: not a refusal, and not a pass either
  if (c.refused !== null && c.refused !== undefined) return 'unjudged';
  const rv = c.revision;
  if (isObj(rv) && rv.stop_reason !== PLACEMENT_UNJUDGED) return 'placed';
  return 'unjudged';
}

/* {total, refused, placed, unjudged, openable} over a list of served candidates. `openable` is
   what a reader can put on the bench: everything the type has not already turned down. */
export function standingOfSet(cands) {
  const list = Array.isArray(cands) ? cands : [];
  const out = { total: list.length, refused: 0, placed: 0, unjudged: 0, openable: 0 };
  for (const c of list) out[standingOf(c)] += 1;
  out.openable = out.placed + out.unjudged;
  return out;
}
