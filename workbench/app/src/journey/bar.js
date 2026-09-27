/* WHAT THE JOURNEY BAR DRAWS, DECIDED WITHOUT REACT (WP-14.10, PRD §I.5).

   `journeyState` (./journey.js) is the one reading of where a house stands; this file is the
   handful of decisions the BAR makes on top of it, as pure functions, so each can be driven under
   `node --test` and `components/JourneyBar.jsx` is left to draw them:

     WHERE IT IS SHOWN   on the six house surfaces — the five steps and the one surface that joins
                         them (tracing a drawing joins at the plan) — and never in full screen,
                         whose whole point is that the chrome goes. `stepOfSurface` is the one list
                         of those surfaces; nothing here restates it.
     WHICH STEP IS A LINK
                         every step up to the plan is a place a reader can stand in: the brief is
                         where a house starts, the candidates page shows a compose running or
                         failed and points back, and the bench loads an example or a paste. The
                         steps MADE FROM the plan — the drawings and the export — exist only when
                         the plan may be drawn, so each is a link only while the step before it
                         can proceed. Otherwise it is BLOCKED: text saying why, and never an
                         anchor. A refused house therefore shows "blocked: refused" on both, and a
                         link to a drawing the contract forbids is not on the page to be followed.
     NEXT                a link to the following step only where the current step can proceed;
                         otherwise the reason it cannot, in the journey's own words. The surface
                         that JOINS the journey has no next: its act is "send to the bench".
     THE ORIGIN          where the plan on the bench came from, linked back where the place it
                         came from still exists. A candidate's link opens the Candidate Set, which
                         shows the session's CURRENT job — so a plan from an earlier compose says
                         which candidate it was and does not link to somebody else's.

   EVERY WORD IS A GLOSSARY RECORD'S OR THE JOURNEY'S. A step is named by its surface's own record
   (`STEP_TERMS`), which `src/journeyBar.test.mjs` holds to `glossary/*.json`; the states, reasons
   and origins are `JOURNEY_WORDS`. This file writes no word a reader sees.

   Pure: no React, no DOM. */
import { JOURNEY, stepOfSurface } from './journey.js';

/* The glossary record that names each step — the surface record of the surface it stands on. */
export const STEP_TERMS = Object.freeze({
  brief: 'surface-brief',
  candidates: 'surface-candidates',
  plan: 'surface-workbench',
  drawings: 'surface-drawings',
  export: 'surface-export',
  transcription: 'surface-transcription',
});

/* The group the steps belong to, and the plan they are about. */
export const BAR_TERMS = Object.freeze({ group: 'nav-group-a-house', bench: 'on-the-bench' });

/* Shown on the house surfaces only, and never in full screen. `full` is the shell's own reading
   of `layout.full` for the surface in view (App.jsx), so a truthy value is full screen here. */
export function showJourneyBar(surface, full) {
  return !full && stepOfSurface(surface) !== null;
}

const PLAN_AT = JOURNEY.findIndex((j) => j.id === 'plan');

/* The drawn bar, from `journeyState(...)`, the surface in view and the session's job id. */
export function barView(state, { surface, jobId = null } = {}) {
  const steps = (state && Array.isArray(state.steps)) ? state.steps : [];
  const items = steps.map((s, i) => {
    const blocked = i > PLAN_AT && !steps[i - 1].canProceed;
    return {
      id: s.id,
      n: s.n,
      href: s.href,
      state: s.state,
      words: s.words,
      counts: s.counts,
      stateTerm: s.stateTerm,
      termId: STEP_TERMS[s.id],
      current: s.surface === surface,
      link: !blocked,
      blocked: blocked ? s.state : null,
    };
  });

  const alt = state && state.alternate ? state.alternate : null;
  const alternate = alt ? {
    id: alt.id,
    href: alt.href,
    joins: alt.joins,
    termId: STEP_TERMS[alt.id],
    current: alt.surface === surface,
  } : null;

  // the next step, from the step whose OWN surface is in view; a joining surface has none
  const at = steps.findIndex((s) => s.surface === surface);
  let next = null;
  if (at >= 0 && at < steps.length - 1) {
    const here = steps[at];
    const there = items[at + 1];
    next = here.canProceed
      ? { link: true, id: there.id, href: there.href, termId: there.termId }
      : { link: false, id: there.id, termId: there.termId, reason: here.reason };
  }

  const plan = steps.find((s) => s.id === 'plan');
  let origin = null;
  if (plan && plan.state !== 'empty' && plan.origin) {
    const o = plan.origin;
    // a candidate's link opens the job in hand; one from another job is named and not linked
    const stale = o.kind === 'candidate' && (!o.jobId || o.jobId !== jobId);
    origin = {
      kind: o.kind,
      words: plan.originWords,
      href: stale ? null : plan.originHref,
      briefName: o.kind === 'candidate' ? (o.briefName || null) : null,
    };
  }

  return { items, alternate, next, origin };
}
