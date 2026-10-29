/* WHICH MARK EACH STATION OF THE JOURNEY CARRIES (Phase 17, WP-17.2).

   The sidebar and the front door draw the house's five steps as stations on a line, and each
   station carries one of the journey marks (`marks.js`, ruled 29 Oct 2026): a vellum disc for a
   step done, a gilt ring round a gilt dot for the step in hand, a dashed ring for one not yet
   reached. A refused plan carries the refused ring, because a station that says only "not yet"
   over a house the corpus will not draw would say less than the bar it replaces.

   DONE IS READ OFF THE STEP'S OWN STATE AND NEVER INFERRED FROM A VISIT: a brief is done when it is
   stated, the candidates when a set came back, the plan when it has been placed and judged and not
   refused. A drawing and an export have no state that records their being made, so neither is
   ever drawn done; they are ready, which is a different word, carried beside the mark.

   THE STEP IN HAND is the step whose own surface is in view; where none is (a library page, the
   front door), it is the step the journey would resume at. Pure: no React. */
export const STATION_MARKS = Object.freeze({
  done: '--mark-journey-done',
  current: '--mark-journey-current',
  notYet: '--mark-journey-not-yet',
  refused: '--mark-refused',
});

const DONE = Object.freeze({ brief: 'stated', candidates: 'ready', plan: 'evaluated' });

/* `item` is one of `barView(...).items`; `resume` the journey's own `resume` (or null). */
export function stationMark(item, { anyCurrent = false, resume = null } = {}) {
  if (!item) return STATION_MARKS.notYet;
  if (item.id === 'plan' && item.state === 'refused') return STATION_MARKS.refused;
  const inHand = item.current || (!anyCurrent && resume && resume.id === item.id);
  if (inHand) return STATION_MARKS.current;
  if (DONE[item.id] && DONE[item.id] === item.state) return STATION_MARKS.done;
  return STATION_MARKS.notYet;
}

/* Every station's mark at once, from `barView(...)` and the journey's `resume`. */
export function stations(bar, resume = null) {
  const items = bar && Array.isArray(bar.items) ? bar.items : [];
  const anyCurrent = items.some((i) => i.current);
  return items.map((i) => ({ ...i, mark: stationMark(i, { anyCurrent, resume }) }));
}
