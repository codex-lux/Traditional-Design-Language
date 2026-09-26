/* The persistent rail beside the canvas — never a modal, never a separate page. Rules it
   enforces structurally rather than by instruction:
   - every claim carries a citation that navigates the canvas
   - it says which findings it could not evaluate
   - it refuses out loud, as a card
   - it never calls a plan good

   Rewritten from precompiled React.createElement output in WP-5.6. It was the one place
   left where a fix meant editing a decompiled bundle, and it needed two: the tool count
   was the hardcoded string "24 tools", which is a claim about the server written into the
   client and free to go stale the moment a tool is added; and a citation was a <button>,
   so the one thing in the product most worth copying or opening in a second tab could be
   neither. */
import React from 'react';
import { ToolTrace } from './ToolTrace.jsx';
import { citeHref } from '../router.js';
import { layout } from '../state/layout.js';
import { FoldControl } from '../Chrome.jsx';
import { MarkGlyph } from './MarkGlyph.jsx';
import { JudgmentMark } from './JudgmentMark.jsx';
import { Term } from './Term.jsx';

const EYE = {
  font: 'var(--type-eyebrow)',
  letterSpacing: 'var(--tr-eyebrow)',
  textTransform: 'uppercase',
  color: 'var(--ink-2)',
};

/* A real anchor to the citation's own URL. Left-click still routes in place — the href is
   there so the browser's own affordances work on it: copy link, middle-click, open in a
   new tab. The address it copies is the one the rail would have written anyway. */
function Citation({ cite, onCite }) {
  const href = citeHref(cite);
  return (
    <a href={href || undefined}
      onClick={(e) => {
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;   // let the browser have it
        if (!onCite) return;
        e.preventDefault();
        onCite(cite);
      }}
      title={`go to ${cite}`}
      style={{ font: 'var(--type-data-s)' }}>
      {cite}
    </a>
  );
}

function UserTurn({ text }) {
  return (
    <p style={{ font: 'var(--fw-reg) 13px/1.55 var(--body)', color: 'var(--ink)', margin: 0,
      paddingLeft: 10, borderLeft: '2px solid var(--rule)' }}>{text}</p>
  );
}

function RefusalTurn({ text, reason }) {
  return (
    <div style={{ border: '1px solid var(--rule)', borderLeft: '2px solid var(--refusal)',
      background: 'var(--paper-deep)', padding: '11px 12px' }}>
      <div style={{ ...EYE, color: 'var(--refusal)', marginBottom: 6 }}>refused</div>
      <p style={{ font: 'var(--fw-reg) 13px/1.55 var(--body)', color: 'var(--ink)', margin: 0 }}>{text}</p>
      {reason && (
        <p style={{ font: 'var(--fw-reg) 12.5px/1.55 var(--body)', color: 'var(--ink-2)',
          margin: '7px 0 0' }}>{reason}</p>
      )}
    </div>
  );
}

function QuestionTurn({ text, cite, onCite }) {
  return (
    <div style={{ border: '1px solid var(--rule)', background: 'var(--paper-deep)', padding: '11px 12px' }}>
      {/* A question handed to the reader is a decision left to them, which is the
          yours-to-judge mark and its record's word -- not the could-not-evaluate hatch it wore
          until WP-14.29, which said a rule had failed to run. */}
      <div data-rail-question="" style={{ ...EYE, marginBottom: 6, display: 'flex', alignItems: 'center', gap: 7 }}>
        <MarkGlyph token="--mark-yours-to-judge" size={10} />
        <Term id="judgment-yours-to-judge" />
      </div>
      <p style={{ font: 'var(--fw-reg) 13px/1.55 var(--body)', color: 'var(--ink)', margin: 0 }}>{text}</p>
      {cite && <div style={{ marginTop: 7 }}><Citation cite={cite} onCite={onCite} /></div>}
    </div>
  );
}

function AssistantTurn({ turn, onCite }) {
  return (
    <div>
      {turn.calls && (
        <ToolTrace calls={turn.calls} onCite={onCite} running={turn.running}
          style={{ marginBottom: 9 }} />
      )}
      <p style={{ font: 'var(--fw-reg) 13px/1.6 var(--body)', color: 'var(--ink-2)', margin: 0 }}>
        {turn.text}
      </p>
      {turn.cites && turn.cites.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10, marginTop: 8 }}>
          {turn.cites.map((c) => <Citation key={c} cite={c} onCite={onCite} />)}
        </div>
      )}
      {/* The three-state rule, in the rail: what could not be evaluated is said, and it is
          said with the could-not-evaluate mark rather than a colour, because it is neither pass
          nor fail. `JudgmentMark` carries the state's own word to assistive tech too. */}
      {turn.unjudged && (
        <div data-rail-unjudged="" style={{ margin: '9px 0 0' }}>
          <JudgmentMark state="unjudged" size={11} label={turn.unjudged} showWord={false} />
        </div>
      )}
    </div>
  );
}

/* THE PAGE'S STARTER QUESTIONS (WP-14.22, PRD tranche 2 §C.10). Each is a glossary record's
   `ask`, handed in by RailHost through `rail/starters.js` and shown verbatim; this component
   writes no question of its own. A click FILLS the input and never sends: the reader may edit
   the question first, and a turn is billed only when they press Enter. So a click calls no
   `onSend` -- `e2e/walk.mjs` asserts that no `/api/rail/messages` request leaves on one. */
function Starters({ starters, onPick }) {
  if (!starters || !starters.length) return null;
  return (
    <div data-rail-starters="" style={{ display: 'flex', flexDirection: 'column', gap: 5,
      marginBottom: 8 }}>
      {starters.map((q) => (
        <button key={q} type="button" data-rail-starter="" onClick={() => onPick(q)}
          style={{ textAlign: 'left', background: 'var(--paper-deep)',
            border: '1px solid var(--rule-soft)', color: 'var(--ink-2)',
            font: 'var(--fw-reg) 12.5px/1.45 var(--body)', padding: '5px 8px', cursor: 'pointer' }}>
          {q}
        </button>
      ))}
    </div>
  );
}

function AiRail({ turns, onCite, onSend, placeholder, width, style, toolCount, title, starters }) {
  const inputRef = React.useRef(null);
  const fill = (q) => {
    const el = inputRef.current;
    if (!el) return;
    el.value = q;
    el.focus();
  };
  /* The rail's own width, pulled from the shell's layout store rather than a token, so
     the splitter on its left edge and the aside itself cannot disagree about it.

     The `width` prop still wins where one is passed. NOTHING PASSES ONE — `RailHost` is
     the only mount site — and the comment here used to claim "the shortcut card and the
     tests mount this at a fixed size", which an audit found to be true of neither. The
     escape hatch is kept because a fixed-width mount is a reasonable thing to want; the
     claim that something already does it is not kept. */
  const pulled = React.useSyncExternalStore(layout.subscribe, () => layout.width('rail'));
  return (
    <aside aria-label="the rail — ask the corpus"
      style={{ width: width || pulled, flex: 'none', display: 'flex',
        flexDirection: 'column', borderLeft: '1px solid var(--rule)', background: 'var(--paper)',
        minHeight: 0, ...style }}>

      <header style={{ minHeight: 'var(--substrip-h)', flex: 'none', display: 'flex',
        alignItems: 'center', gap: 10, padding: '4px 6px 4px 12px',
        borderBottom: '1px solid var(--rule)' }}>
        {/* The assistant's NAME, from its glossary record (WP-14.13, PRD §I.11): the host passes
            the record's term, so nothing here says what the pane is. The aside's label and the
            fold's stay "the rail" — they are how the walk and a screen reader find the pane.
            The name WRAPS rather than truncating, and the head grows to hold it: at the pane's
            shipped 344 px the record's term, letterspaced, read "ASK THE CORPUS · AI ASSIS…",
            which is a name the reader was not given. */}
        <span style={{ ...EYE, color: 'var(--ink-2)', minWidth: 0 }} data-rail-head="">{title}</span>
        <span style={{ flex: 1 }} />
        {/* Counted by the server, which is the only thing that knows. Absent rather than
            guessed while /api/health is still in flight. */}
        <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)', flex: 'none', whiteSpace: 'nowrap' }}>
          {toolCount == null ? '' : `${toolCount} tools`}
        </span>
        <FoldControl pane="rail" label="the rail" side="right" />
      </header>

      <div style={{ flex: 1, overflow: 'auto', padding: 12, display: 'flex',
        flexDirection: 'column', gap: 14, minHeight: 0 }}>
        {turns.map((t, i) => {
          if (t.role === 'user') return <UserTurn key={i} text={t.text} />;
          if (t.role === 'refusal') return <RefusalTurn key={i} text={t.text} reason={t.reason} />;
          if (t.role === 'question') return <QuestionTurn key={i} text={t.text} cite={t.cite} onCite={onCite} />;
          return <AssistantTurn key={i} turn={t} onCite={onCite} />;
        })}
      </div>

      <form onSubmit={(e) => e.preventDefault()}
        style={{ flex: 'none', borderTop: '1px solid var(--rule)', padding: 10 }}>
        <Starters starters={starters} onPick={fill} />
        <input ref={inputRef} aria-label="Ask the corpus" placeholder={placeholder || 'Ask the corpus…'}
          onKeyDown={onSend ? (e) => {
            if (e.key === 'Enter') {
              // only clear when the host accepted the message — a busy rail must not
              // silently eat what the user typed
              if (onSend(e.currentTarget.value) !== false) e.currentTarget.value = '';
            }
          } : undefined}
          style={{ width: '100%', background: 'var(--paper-mat)', border: '1px solid var(--rule-soft)',
            color: 'var(--ink)', font: 'var(--fw-reg) 13px/1.5 var(--body)', padding: '7px 9px' }} />
      </form>
    </aside>
  );
}

export default AiRail;
export { AiRail };
