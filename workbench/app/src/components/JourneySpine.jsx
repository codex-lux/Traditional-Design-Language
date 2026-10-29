/* WHERE THE HOUSE STANDS, AS STATIONS ON A LINE (Phase 17, WP-17.2; the journey bar of WP-14.10
   redrawn, ruled 29 Oct 2026, docs/ui-redesign-2026-10-29.md).

   <JourneySpine surface={surface} lastEval={lastEval} selection={selection} compact={bool} />

   Until Phase 17 this was a bar above `<main>` on the six house surfaces, and the rail listed the
   same five steps again in a group of its own, so the navigation said the journey twice and the
   bar wrapped onto a second row whenever its Next was long
   (`oq/the-journeys-bar-next-jumps-rows-when-the-strip-wraps`). The house is now one block of the
   sidebar, on every page: its five steps as stations on a vertical rule, each carrying the
   journey's mark (`journey/spine.js`) and its state in italic prose, then Next and where the plan
   came from. On a library page it is five marks in a row (`compact`), still links.

   IT DECIDES NOTHING, AS THE BAR DID NOT. Where the house stands is `journeyState`; which step is a
   link, which is blocked, what Next offers and whether the origin is linked are `journey/bar.js`'s
   `barView`; which mark a station carries is `journey/spine.js`'s. A station's anchor carries the
   site map's `data-nav` (its surface's nav id) beside the journey's `data-step`, because it is the
   one control for both, and a blocked step is a `<span data-blocked>`, never an anchor.

   EVERY WORD IS A RECORD'S: a step's name is its surface's glossary record, the four state words
   that are glossary terms are drawn as `Term`s, and the rest are the journey's words, each held to
   its `journey-state-*` record by `src/journey.test.mjs`. */
import React from 'react';
import { session } from '../state/session.js';
import { planDoc } from '../state/planDoc.js';
import { journeyState, pickedCandidate, JOURNEY_TERMS, JOURNEY_WORDS } from '../journey/journey.js';
import { barView, BAR_TERMS, showJourneyBar } from '../journey/bar.js';
import { stations } from '../journey/spine.js';
import { MarkGlyph } from './MarkGlyph.jsx';
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
  font: (item.current ? 'var(--fw-med)' : 'var(--fw-reg)') + ' 14px/1.35 var(--body)',
  color: item.current ? 'var(--text-body)' : (item.link ? 'var(--link)' : 'var(--text-secondary)'),
  borderBottom: 'none',
  whiteSpace: 'nowrap',
});

const num = { font: 'var(--type-data-s)', color: 'var(--text-secondary)', marginRight: 6 };
// the state is a sentence about the house, so it is italic prose and never mono (Phase 17)
const words = { font: 'italic var(--fw-reg) 13px/1.35 var(--body)', color: 'var(--text-secondary)' };
const NAV_OF = Object.freeze({ plan: 'workbench' });
const navId = (id) => NAV_OF[id] || id;

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

function Step({ item, compact }) {
  const word = useWord(item.termId);
  const d = useTermDescription(item.termId);
  const current = item.current ? 'step' : undefined;
  const structured = item.id === 'plan' && (item.stateTerm || item.counts);
  const mark = <MarkGlyph token={item.mark} size={compact ? 11 : 12} />;
  if (compact) {
    const props = { 'data-step': item.id, 'data-nav': item.link ? navId(item.id) : undefined,
      'aria-current': current, title: d.title, 'aria-describedby': d.describedBy,
      style: { display: 'inline-flex', padding: 3, borderBottom: 'none' } };
    return (
      <li data-journey-step={item.id} style={{ listStyle: 'none' }}>
        {item.link
          ? <a href={item.href} {...props}>{mark}<span className="tdl-sr-only">{word}</span></a>
          : <span data-blocked={item.blocked} {...props}>{mark}<span className="tdl-sr-only">{word}</span></span>}
        {d.element}
        <span data-step-words={item.id} data-state={item.state} className="tdl-sr-only">
          {structured ? <PlanWords item={item} /> : item.words}
        </span>
      </li>
    );
  }
  const label = <span style={{ display: 'flex', alignItems: 'baseline', gap: 0 }}><span data-step-n="" style={num}>{item.n}</span><span>{word}</span></span>;
  return (
    <li data-journey-step={item.id} style={{ display: 'grid', gridTemplateColumns: '18px 1fr',
      columnGap: 8, alignItems: 'start', padding: '5px 0', position: 'relative', listStyle: 'none' }}>
      <span style={{ display: 'flex', justifyContent: 'center', paddingTop: 3, zIndex: 1,
        background: 'var(--surface-chrome)' }}>{mark}</span>
      <span style={{ display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        {item.link
          ? (
            <a href={item.href} data-step={item.id} data-nav={navId(item.id)} aria-current={current}
              aria-describedby={d.describedBy} title={d.title} style={stepStyle(item)}>{label}</a>
          ) : (
            <span data-step={item.id} data-blocked={item.blocked} aria-current={current}
              aria-describedby={d.describedBy} title={d.title} style={stepStyle(item)}>{label}</span>
          )}
        {d.element}
        <span data-step-words={item.id} data-state={item.state}
          style={{ ...words, color: item.state === 'refused' ? 'var(--refusal-text)' : words.color }}>
          {structured ? <PlanWords item={item} /> : item.words}
        </span>
      </span>
    </li>
  );
}

function Alternate({ alt, planN, compact }) {
  const word = useWord(alt.termId);
  const d = useTermDescription(alt.termId);
  const item = { current: alt.current, link: true };
  if (compact) return null;
  return (
    <li data-journey-step={alt.id} style={{ listStyle: 'none', padding: '0 0 4px 26px' }}>
      <a href={alt.href} data-step={alt.id} data-nav={alt.id} aria-current={alt.current ? 'step' : undefined}
        aria-describedby={d.describedBy} title={d.title}
        style={{ ...stepStyle(item), font: 'var(--fw-reg) 13px/1.35 var(--body)' }}><span>{word}</span></a>
      {d.element}
      {/* where it joins: the number of the step it produces */}
      <span aria-hidden="true" style={{ ...num, marginLeft: 6 }}>→ {planN}</span>
    </li>
  );
}

function Next({ next }) {
  const word = useWord(next.termId);
  if (next.link) {
    return (
      <a href={next.href} data-next={next.id}
        style={{ font: 'var(--fw-reg) 13.5px/1.35 var(--body)', alignSelf: 'flex-start' }}>
        {W.next}: {word} <span aria-hidden="true">→</span>
      </a>
    );
  }
  return (
    <span data-next={next.id} data-next-blocked="" style={words}>
      {next.reason}
    </span>
  );
}

export function JourneySpine({ surface, lastEval, selection, compact = false }) {
  const s = React.useSyncExternalStore(session.subscribe, session.get);
  const plan = React.useSyncExternalStore(planDoc.subscribe, planDoc.get);
  const state = React.useMemo(
    () => journeyState({ session: s, plan, lastEval, picked: pickedCandidate(surface, selection) }),
    [s, plan, lastEval, surface, selection]);
  const view = React.useMemo(() => barView(state, { surface, jobId: s.jobId }), [state, surface, s.jobId]);
  const items = React.useMemo(() => stations(view, state.resume), [view, state.resume]);
  const planItem = items.find((i) => i.id === 'plan');
  if (compact) {
    return (
      <nav aria-label="house journey" data-journey="" data-compact="">
        <ol style={{ display: 'flex', gap: 4, margin: 0, padding: 0 }}>
          {items.map((item) => <Step key={item.id} item={item} compact />)}
        </ol>
      </nav>
    );
  }
  return (
    <nav aria-label="house journey" data-journey=""
      style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      <ol style={{ margin: 0, padding: 0, position: 'relative' }}>
        {/* the rule the stations stand on */}
        <span aria-hidden="true" style={{ position: 'absolute', left: 8.5, top: 12, bottom: 18,
          borderLeft: '1px solid var(--border-paper)' }} />
        {items.map((item) => (
          <React.Fragment key={item.id}>
            <Step item={item} />
            {item.id === 'plan' && view.alternate
              && <Alternate alt={view.alternate} planN={planItem ? planItem.n : ''} />}
          </React.Fragment>
        ))}
      </ol>
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
      style={{ margin: 0, font: 'var(--fw-reg) 12.5px/1.4 var(--body)', color: 'var(--text-secondary)' }}>
      <Term id={BAR_TERMS.bench} />
      {': '}
      <span style={{ color: 'var(--text-body)' }}>{name || id}</span>
      {name && id && <code style={{ font: 'var(--type-data-s)', color: 'var(--text-secondary)', marginLeft: 6 }}>{id}</code>}
      {W.separator}
      {origin.href
        ? <a href={origin.href} data-origin-link="">{origin.words}</a>
        : <span>{origin.words}</span>}
      {origin.briefName && <>{W.separator}{origin.briefName}</>}
    </p>
  );
}
