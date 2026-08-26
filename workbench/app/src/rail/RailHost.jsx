/* The persistent rail, wired to the server's agent loop. The client owns the
   conversation (API-shaped history replayed each turn) and renders the SSE events
   into the AiRail's turn model: tool traces with a pending state, validated
   citations that navigate the canvas, unjudged lines, questions, refusals. */
import React from 'react';
import { railTurn } from '../api/client.js';
import { session } from '../state/session.js';
import { AiRail } from '../components/AiRail.jsx';

export function RailHost({ onCite, surface, plan, lastEval, railAvailable, toolCount }) {
  const s = React.useSyncExternalStore(session.subscribe, session.get);
  const historyRef = React.useRef([]);   // API-shaped [{role, content: string}]
  const [busy, setBusy] = React.useState(false);

  const turns = s.railTurns.length ? s.railTurns : [{
    role: 'assistant',
    text: railAvailable === false
      ? 'No ANTHROPIC_API_KEY is attached to the server, so the rail is off. Everything ' +
        'else works without it — set the key and restart to turn the rail on.'
      : 'Ask the corpus. Every claim I make carries a citation that navigates this ' +
        'canvas, the tools I consult are shown as I use them, and I will say what I ' +
        'could not evaluate — unjudged is not passed.',
    unjudged: railAvailable === false ? 'I cannot evaluate anything: the rail is off.' : undefined,
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
        context: {
          surface,
          plan: plan || undefined,
          last_eval: lastEval?.check ? {
            counts: lastEval.check.counts,
            constraint_summary: lastEval.check.constraint_summary,
            fault_summary: lastEval.check.fault_summary,
          } : undefined,
          candidate_count: s.result?.candidates?.length,
        },
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
      toolCount={toolCount}
      placeholder={railAvailable === false ? 'the rail is off — no key attached' : 'Ask the corpus…'} />
  );
}
