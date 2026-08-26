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

const EYE = {
  font: 'var(--type-eyebrow)',
  letterSpacing: 'var(--tr-eyebrow)',
  textTransform: 'uppercase',
  color: 'var(--ink-3)',
};

const UNJUDGED_SWATCH = {
  border: '1px solid var(--judge-unjudged)',
  backgroundImage: 'var(--hatch-unjudged)',
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
      style={{ font: 'var(--type-data-s)', color: 'var(--gilt-deep)',
        borderBottom: '1px solid var(--link-underline)', textDecoration: 'none' }}>
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
      <div style={{ ...EYE, marginBottom: 6, display: 'flex', alignItems: 'center', gap: 7 }}>
        <span aria-hidden="true" style={{ width: 10, height: 10, ...UNJUDGED_SWATCH }} />
        for you to decide
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
          said with the hatch rather than a colour, because it is neither pass nor fail. */}
      {turn.unjudged && (
        <p style={{ display: 'flex', gap: 8, alignItems: 'flex-start',
          font: 'var(--fw-reg) 12.5px/1.55 var(--body)', color: 'var(--ink-3)', margin: '9px 0 0' }}>
          <span aria-hidden="true" style={{ width: 11, height: 11, flex: 'none', marginTop: 3,
            ...UNJUDGED_SWATCH }} />
          {turn.unjudged}
        </p>
      )}
    </div>
  );
}

function AiRail({ turns, onCite, onSend, placeholder, width, style, toolCount }) {
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

      <header style={{ height: 'var(--substrip-h)', flex: 'none', display: 'flex',
        alignItems: 'center', gap: 10, padding: '0 6px 0 12px',
        borderBottom: '1px solid var(--rule)' }}>
        <span style={EYE}>the rail</span>
        <span style={{ flex: 1 }} />
        {/* Counted by the server, which is the only thing that knows. Absent rather than
            guessed while /api/health is still in flight. */}
        <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)' }}>
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
        <input aria-label="Ask the corpus" placeholder={placeholder || 'Ask the corpus…'}
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
