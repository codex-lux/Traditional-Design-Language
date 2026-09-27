/* The persistent rail, wired to the server's agent loop. The client owns the
   conversation (API-shaped history replayed each turn) and renders the SSE events
   into the AiRail's turn model: tool traces with a pending state, validated
   citations that navigate the canvas, unjudged lines, questions, refusals. */
import React from 'react';
import { railTurn } from '../api/client.js';
import { session } from '../state/session.js';
import { AiRail } from '../components/AiRail.jsx';
import { useGlossary } from '../api/useGlossary.js';
import { termView } from '../glossary/termView.js';
import { PANES } from '../state/layout.js';
import { nav } from '../state/nav.js';
import { railContext } from './railContext.js';
import { startersFor } from './starters.js';

/* The pane's name, from the `assistant` glossary record (ruled 24 Sep 2026, PRD §I.11): its
   `term` once the glossary has answered; the pane's own label while it has not; and, where it
   answered without the record, `noEntry('assistant')` — said, never guessed. Exported so the
   folded spine (App.jsx) reads the same name the open pane shows. */
export function assistantName(glossary) {
  const v = termView(glossary, { id: 'assistant' });
  if (v.state === 'ready') return v.word;
  if (v.state === 'loading') return PANES.rail.label;
  return v.text;
}

export function RailHost({ onCite, surface, plan, lastEval, railAvailable, toolCount }) {
  const s = React.useSyncExternalStore(session.subscribe, session.get);
  const glossary = useGlossary();
  /* WP-14.22: the page the reader is on, read from the nav store here rather than threaded
     through App.jsx, so the assistant is told the record on screen (`railContext`'s `cite`) and
     offers that page's own starter questions. App's `surface` prop is this same store's. */
  const place = React.useSyncExternalStore(nav.subscribe, nav.get);
  const starters = startersFor(glossary, place.surface);
  const historyRef = React.useRef([]);   // API-shaped [{role, content: string}]
  const [busy, setBusy] = React.useState(false);

  const turns = s.railTurns.length ? s.railTurns : [{
    role: 'assistant',
    /* Worded to say what it is — an AI assistant, a language model reading the corpus — which
       the pane never said (the ux analysis's finding 14). What it is SENT changed at WP-14.22:
       the page's citation and the candidate set's summaries (`railContext.js`), which closed
       `oq/the-assistant-is-blind-to-the-page`. */
    text: railAvailable === false
      ? 'No ANTHROPIC_API_KEY is attached to the server, so the AI assistant is off. ' +
        'Everything else works without it — set the key and restart to turn the assistant on.'
      : 'I am an AI assistant: a language model reading this corpus for you. Ask the corpus. ' +
        'Every claim I make carries a citation that navigates this canvas, the tools I ' +
        'consult are shown as I use them, and I will say what I could not evaluate — ' +
        'unjudged is not passed.',
    unjudged: railAvailable === false ? 'I cannot evaluate anything: the AI assistant is off.' : undefined,
  }];

  function send(text) {
    if (!text || busy) return false;   // refuse (and keep the input) while a turn runs
    run(text);
    return true;
  }

  async function run(text) {
    setBusy(true);
    historyRef.current.push({ role: 'user', content: text });
    session.pushTurn({ role: 'user', text });
    session.pushTurn({ role: 'assistant', text: '', calls: [], cites: [], running: true });

    const finals = [];   // extra typed turns (question/refusal) appended after
    try {
      await railTurn({
        messages: historyRef.current,
        context: railContext({ surface, place, plan, lastEval, candidates: s.result?.candidates }),
      }, (event, data) => {
        if (event === 'tool_call') {
          session.patchLastTurn((t) => ({ ...t, calls: [...(t.calls || []), { tool: data.tool, detail: data.detail, pending: true }] }));
        } else if (event === 'tool_done') {
          session.patchLastTurn((t) => {
            let flipped = false;   // flip only the FIRST pending call of that tool
            return { ...t, calls: (t.calls || []).map((c) => {
              if (!flipped && c.tool === data.tool && c.pending) { flipped = true; return { ...c, pending: false }; }
              return c;
            }) };
          });
        } else if (event === 'text') {
          session.patchLastTurn((t) => ({ ...t, text: (t.text ? t.text + '\n\n' : '') + data.text }));
        } else if (event === 'cites') {
          session.patchLastTurn((t) => ({ ...t, cites: data.refs }));
        } else if (event === 'unjudged') {
          session.patchLastTurn((t) => ({ ...t, unjudged: data.text }));
        } else if (event === 'question') {
          finals.push({ role: 'question', text: data.text, cite: data.cite });
        } else if (event === 'refusal') {
          finals.push({ role: 'refusal', text: data.text, reason: data.reason });
        } else if (event === 'error') {
          session.patchLastTurn((t) => ({ ...t, text: (t.text || '') + (t.text ? '\n\n' : '') + '— ' + data.error }));
        }
      });
    } catch (e) {
      session.patchLastTurn((t) => ({ ...t, text: (t.text || '') + ' — rail request failed: ' + e.message }));
    }
    session.patchLastTurn((t) => ({ ...t, running: false }));
    finals.forEach((f) => session.pushTurn(f));
    // fold the assistant's visible text back into the API history for the next turn
    const lastAssistant = session.get().railTurns.filter((t) => t.role !== 'user').slice(-1 - finals.length);
    historyRef.current.push({
      role: 'assistant',
      content: lastAssistant.map((t) => t.text).join('\n') || '…',
    });
    setBusy(false);
  }

  return (
    <AiRail turns={turns} onCite={(ref) => onCite(ref.replace(/^«|»$/g, ''))} onSend={send}
      toolCount={toolCount} title={assistantName(glossary)} starters={starters}
      placeholder={railAvailable === false ? 'the AI assistant is off — no key attached' : 'Ask the corpus…'} />
  );
}
