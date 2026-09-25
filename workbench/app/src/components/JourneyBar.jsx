/* WHERE THE HOUSE STANDS, ON EVERY STEP OF MAKING ONE (WP-14.10, PRD §I.5).

   <JourneyBar surface={surface} lastEval={lastEval} />

   Brief → candidates → plan → drawings → export was spread over three rail groups with static
   metas and one sentence on the Overview saying the order, so a reader on the Drawing Set could
   not tell that the house they were looking at had been refused, that the candidates it came from
   had failed to compose, or which candidate the bench's plan even was. This is one bar, mounted
   once by App above `<main>` on the six house surfaces, that says in words where the house stands
   — refused and unjudged included — and where it came from.

   IT DECIDES NOTHING. Where the house stands is `journey/journey.js`'s `journeyState`, which reads
   the refusal only through `sheet/refusal.js`; which step is a link, which is blocked, what Next
   offers and whether the origin may be linked are `journey/bar.js`'s. Both are pure and driven
   under `node --test` (`src/journey.test.mjs`, `src/journeyBar.test.mjs`). This file reads the two
   stores the journey needs — the session and the plan on the bench — and draws the answer.

   EVERY WORD IS A RECORD'S. A step's name is its surface's glossary record; the group's is
   `nav-group-a-house`; the states, reasons and origins are the journey's one table of words. A
   state word that is itself a glossary term (refused, fatal, serious, unjudged) is drawn as a
   `Term`, and a Term never sits inside an anchor — the step's anchor carries its definition
   through `useTermDescription` instead, and the state words stand OUTSIDE it. A blocked step is a
   `<span data-blocked>`, never an anchor, because a link to a drawing the contract forbids should
   not be on the page to be followed. */
import React from 'react';
import { session } from '../state/session.js';
import { planDoc } from '../state/planDoc.js';
import { journeyState, JOURNEY_TERMS, JOURNEY_WORDS } from '../journey/journey.js';
import { barView, BAR_TERMS, showJourneyBar } from '../journey/bar.js';
import { useGlossary } from '../api/useGlossary.js';
import { wordOf, noGlossary } from '../glossary/termView.js';
import { Term, useTermDescription } from './Term.jsx';

export { showJourneyBar };

const W = JOURNEY_WORDS;

/* The word a record calls itself, in the bar's three states: the record's `term` (or
   `noEntry`), the glossary's own failure named, or an ellipsis while it is on its way. */
function useWord(id) {
  const g = useGlossary();
  if (g.status === 'ready') return wordOf(g.lookup, id);
  if (g.status === 'failed') return noGlossary(id);
  return '…';
}

const stepStyle = (item) => ({
  font: 'var(--fw-reg) 14px/1.35 var(--body)',
  color: item.current ? 'var(--ink)' : (item.link ? 'var(--link)' : 'var(--ink-2)'),
  borderBottom: item.current ? '2px solid var(--gilt)' : (item.link ? '1px solid var(--link-underline)' : 'none'),
  fontWeight: item.current ? 600 : 400,
  whiteSpace: 'nowrap',
});

const num = { font: 'var(--type-data-s)', color: 'var(--ink-2)', marginRight: 4 };
const words = { font: 'italic var(--fw-reg) 13px/1.35 var(--body)', color: 'var(--ink-2)' };

/* The plan step's words, with the four that are glossary terms drawn as Terms. The text reads
   exactly as the journey's `words` does — `journey.test.mjs` holds each term's record `term` to
   the journey's own word — so a reader of the bar and a reader of the string see one sentence. */
function PlanWords({ item }) {
  const parts = [];
  if (item.stateTerm) parts.push(<Term key="state" id={item.stateTerm} />);
  if (item.counts) {
    for (const k of ['fatal', 'serious', 'unjudged']) {
      const n = item.counts[k];
      parts.push(n === null || n === undefined
        ? <React.Fragment key={k}><Term id={JOURNEY_TERMS[k]} /> {W.counts.notCounted}</React.Fragment>
        : <React.Fragment key={k}>{n} <Term id={JOURNEY_TERMS[k]} /></React.Fragment>);
    }
  }
  return parts.map((p, i) => <React.Fragment key={i}>{i > 0 && W.separator}{p}</React.Fragment>);
}

function Step({ item }) {
  const word = useWord(item.termId);
  const d = useTermDescription(item.termId);
  const current = item.current ? 'step' : undefined;
  const label = <><span style={num}>{item.n}</span>{word}</>;
  const structured = item.id === 'plan' && (item.stateTerm || item.counts);
  return (
    <li data-journey-step={item.id} style={{ display: 'inline-flex', alignItems: 'baseline', gap: 6 }}>
      {item.link
        ? (
          <a href={item.href} data-step={item.id} aria-current={current}
            aria-describedby={d.describedBy} title={d.title} style={stepStyle(item)}>{label}</a>
        ) : (
          <span data-step={item.id} data-blocked={item.blocked} aria-current={current}
            aria-describedby={d.describedBy} title={d.title} style={stepStyle(item)}>{label}</span>
        )}
      {d.element}
      <span data-step-words={item.id} data-state={item.state}
        style={{ ...words, color: item.state === 'refused' ? 'var(--refusal)' : words.color }}>
        {structured ? <PlanWords item={item} /> : item.words}
      </span>
    </li>
  );
}

function Alternate({ alt, planN }) {
  const word = useWord(alt.termId);
  const d = useTermDescription(alt.termId);
  const item = { current: alt.current, link: true };
  return (
    <li data-journey-step={alt.id} style={{ display: 'inline-flex', alignItems: 'baseline', gap: 6,
      borderLeft: '1px solid var(--rule)', paddingLeft: 12 }}>
      <a href={alt.href} data-step={alt.id} aria-current={alt.current ? 'step' : undefined}
        aria-describedby={d.describedBy} title={d.title} style={stepStyle(item)}>{word}</a>
      {d.element}
      {/* where it joins: the number of the step it produces */}
      <span aria-hidden="true" style={num}>→ {planN}</span>
    </li>
  );
}

function Next({ next }) {
  const word = useWord(next.termId);
  if (next.link) {
    return (
      <a href={next.href} data-next={next.id}
        style={{ font: 'var(--fw-reg) 14px/1.35 var(--body)', whiteSpace: 'nowrap' }}>
        {W.next}: {word} <span aria-hidden="true">→</span>
      </a>
    );
  }
  return (
    <span data-next={next.id} data-next-blocked="" style={{ ...words, whiteSpace: 'nowrap' }}>
      {next.reason}
    </span>
  );
}

export function JourneyBar({ surface, lastEval }) {
  const s = React.useSyncExternalStore(session.subscribe, session.get);
  const plan = React.useSyncExternalStore(planDoc.subscribe, planDoc.get);
  const view = React.useMemo(
    () => barView(journeyState({ session: s, plan, lastEval }), { surface, jobId: s.jobId }),
    [s, plan, lastEval, surface]);
  const planItem = view.items.find((i) => i.id === 'plan');
  return (
    <nav aria-label="house journey" data-journey=""
      style={{ flex: 'none', display: 'flex', flexWrap: 'wrap', alignItems: 'baseline',
        columnGap: 18, rowGap: 4, padding: '7px 16px 6px', borderBottom: '1px solid var(--rule)',
        background: 'var(--paper)' }}>
      <span style={{ font: 'var(--type-eyebrow)', letterSpacing: 'var(--tr-eyebrow)',
        textTransform: 'uppercase', color: 'var(--ink-2)' }}>
        <Term id={BAR_TERMS.group} />
      </span>
      <ol style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'baseline', columnGap: 16,
        rowGap: 4, margin: 0, padding: 0, listStyle: 'none' }}>
        {view.items.map((item) => <Step key={item.id} item={item} />)}
        {view.alternate && <Alternate alt={view.alternate} planN={planItem ? planItem.n : ''} />}
      </ol>
      <span style={{ flex: 1 }} />
      {view.next && <Next next={view.next} />}
      {view.origin && <Origin origin={view.origin} plan={plan} />}
    </nav>
  );
}

function Origin({ origin, plan }) {
  const name = plan && typeof plan.name === 'string' && plan.name.trim() ? plan.name : null;
  const id = plan && typeof plan.id === 'string' ? plan.id : null;
  return (
    <p data-journey-origin={origin.kind}
      style={{ flexBasis: '100%', margin: 0, font: 'var(--fw-reg) 13px/1.4 var(--body)', color: 'var(--ink-2)' }}>
      <Term id={BAR_TERMS.bench} />
      {': '}
      <span style={{ color: 'var(--ink)' }}>{name || id}</span>
      {name && id && <code style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)', marginLeft: 6 }}>{id}</code>}
      {W.separator}
      {origin.href
        ? <a href={origin.href} data-origin-link="">{origin.words}</a>
        : <span>{origin.words}</span>}
      {origin.briefName && <>{W.separator}{origin.briefName}</>}
    </p>
  );
}
