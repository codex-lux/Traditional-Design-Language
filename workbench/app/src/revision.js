/* The revision loop's account of itself, adapted for the bench (WP-9.3).

   Pure and React-free on purpose: the node --test suite imports this file with no npm
   install, and the panel, the candidate column and the progress strip all read the same
   sentences from here rather than each spelling its own. Every function takes the server's
   record as it is and returns what a surface shows; none reaches for a field that may be
   absent without saying what its absence means.

   Two words the code keeps apart: an ENGINE is what placed the house ('heuristic' searched,
   'cp-sat' proved); a KEY is [fatal, serious, minor, faults present], and the loop accepts a
   round only when it falls lexicographically. */

const KEY_NAMES = ['fatal', 'serious', 'minor', 'faults'];

export const CLASSES = ['actionable', 'placement', 'critic_suspect', 'architect', 'advisory'];

/* What placed the house -- the engine that RAN, never the one requested. `auto` is a
   request, not a result, and a caller that stores it would label a search as a proof. */
export function engineLabel(engine) {
  if (engine === 'cp-sat' || engine === 'cp') return 'on the proved placement';
  if (engine === 'heuristic') return 'on the searched placement';
  return 'placement not evaluated';
}

/* Where a finding stands after the analyst has read it. */
export function classTag(cls, item = {}) {
  switch (cls) {
    case 'actionable': return item.move ? `a move answers this: ${item.move}` : 'a move answers this';
    case 'placement': return item.lever ? `the engine's — lever: ${item.lever}` : "the engine's";
    case 'critic_suspect': return "the critic's own — reads a literal";
    case 'architect': return "the architect's";
    case 'advisory': return 'advisory';
    default: return null;
  }
}

/* A map of finding id -> { cls, item } from a critique's assessment. */
export function classesById(assessment) {
  const out = new Map();
  if (!assessment) return out;
  for (const cls of CLASSES) {
    for (const item of assessment[cls] || []) if (item && item.id) out.set(item.id, { cls, item });
  }
  return out;
}

/* "fatal 3 → 0 · serious 44 → 40", only the axes that moved; "unchanged" when none did.
   Never an arrow between two equal numbers. */
export function keyDelta(before, after) {
  if (!Array.isArray(before) || !Array.isArray(after)) return 'key not measured';
  const parts = [];
  for (let i = 0; i < KEY_NAMES.length; i++) {
    if (before[i] !== after[i]) parts.push(`${KEY_NAMES[i]} ${before[i]} → ${after[i]}`);
  }
  return parts.length ? parts.join(' · ') : 'unchanged';
}

export function keyText(key) {
  return Array.isArray(key) ? `[${key.join(', ')}]` : '—';
}

const STOP = {
  converged: 'converged — nothing left a move could answer',
  'no-applicable-move': 'stopped: no applicable move',
  'round-cap': 'stopped: round cap',
  budget: 'stopped: budget',
  oscillation: 'stopped: oscillation — the declared record repeated',
  'no-rounds': 'no rounds were asked for',
  'placement-could-not-be-evaluated': 'stopped before the first round: the placement could not be evaluated, so no round could be judged',
};
export function stopLabel(reason) {
  return STOP[reason] || (reason ? `stopped: ${reason}` : 'stopped: reason not stated');
}

/* One line per round for the progress strip while the loop runs. A round with no move is
   said so; a rolled-back round says so; nothing here ever reads "undefined". */
export function roundLine(ev) {
  if (!ev || typeof ev.n !== 'number') return 'round —';
  const moves = Array.isArray(ev.moves) ? ev.moves : [];
  const applied = moves.filter((m) => !m.refused && !m.refused_by_measurement);
  const verdict = ev.accepted ? 'accepted' : moves.length ? 'rolled back' : 'no move applied';
  const count = moves.length
    ? `${applied.length} move${applied.length === 1 ? '' : 's'}${moves.length - applied.length ? `, ${moves.length - applied.length} refused` : ''}`
    : 'no move applied';
  const keys = Array.isArray(ev.key_before) && Array.isArray(ev.key_after)
    ? ` · ${keyText(ev.key_before)} → ${keyText(ev.key_after)}` : '';
  return `round ${ev.n} · ${verdict} · ${count}${keys}`;
}

/* The report as the panel reads it. */
export function adaptRevision(report) {
  if (!report) return null;
  const s = report.summary || {};
  const rounds = (report.rounds || []).map((r) => ({
    n: r.n,
    engine: r.engine_after || r.engine,
    accepted: !!r.accepted,
    keyBefore: r.key_before, keyAfter: r.key_after,
    delta: keyDelta(r.key_before, r.key_after),
    moves: (r.moves || []).map((m) => ({
      move: m.move, finding: m.finding, basis: m.basis || null, log: m.log || null,
      cleared: !!m.cleared,
      refused: m.refused || null,
      refusedByMeasurement: !!m.refused_by_measurement,
    })),
    opened: r.opened || [], cleared: r.cleared || [],
    tabuForgotten: r.tabu_forgotten || 0,
  }));
  const remaining = {};
  for (const cls of CLASSES) remaining[cls] = (report.remaining && report.remaining[cls]) || [];
  const rec = report.reclaimed;
  return {
    mode: report.mode || 'placed',
    engine: report.engine || {},
    engineText: engineLabel(report.engine && report.engine.final),
    keyBefore: report.key_before, keyAfter: report.key_after,
    delta: keyDelta(report.key_before, report.key_after),
    stop: stopLabel(report.stop_reason),
    roundsN: s.rounds ?? rounds.length,
    applied: s.moves_applied ?? rounds.reduce((n, r) => n + (r.accepted ? r.moves.filter((m) => !m.refused).length : 0), 0),
    refused: s.moves_refused ?? (report.refused || []).length,
    seconds: s.seconds,
    rounds,
    remaining,
    handed: report.handed_to_architect || [],
    suspects: report.suspects || [],
    refusedList: report.refused || [],
    // a report written before the reclaim guard carried the bare log list; an array is an
    // object to typeof, so the list is asked for first
    reclaimed: Array.isArray(rec)
      ? { rolledBack: false, why: null, delta: 'unchanged', log: rec }
      : rec && typeof rec === 'object'
        ? { rolledBack: !!rec.rolled_back, why: rec.why || null,
            delta: keyDelta(rec.key_before, rec.key_after), log: rec.log || [] }
        : null,
    note: report.note || null,
  };
}

/* The line under a candidate's score: what the loop bought on THIS candidate. null where
   the compose ran --no-revise (no `revision` on the candidate); when nothing moved, say so
   rather than "was X" against the same X. */
export function revisedLine(c) {
  if (!c || !c.revision) return null;
  const rv = c.revision;
  const s = rv.summary || rv;
  const rounds = s.rounds ?? (rv.rounds ? rv.rounds.length : 0);
  const applied = s.moves_applied ?? 0;
  const before = typeof c.score_before === 'number' ? c.score_before : null;
  const after = typeof c.score === 'number' ? c.score : null;
  const drawn = Array.isArray(c.drawn_key_before) && Array.isArray(c.drawn_key_after)
    ? ` · drawn ${keyText(c.drawn_key_before)} → ${keyText(c.drawn_key_after)}` : '';
  if (!applied) return `revised: nothing moved in ${rounds} round${rounds === 1 ? '' : 's'}${drawn}`;
  const was = before !== null && after !== null && before !== after ? `was ${before.toFixed(1)} · ` : '';
  return `${was}revised in ${rounds} round${rounds === 1 ? '' : 's'}, ${applied} move${applied === 1 ? '' : 's'}${drawn}`;
}

/* A `revised` SSE event as the progress strip shows it. */
export function revisedEventLine(ev) {
  return `revised ${ev.parti_name || ev.parti || '?'}: ${revisedLine({
    revision: { summary: { rounds: ev.rounds, moves_applied: ev.moves_applied } },
    score_before: ev.score_before, score: ev.score,
    drawn_key_before: ev.drawn_key_before, drawn_key_after: ev.drawn_key_after,
  })}`;
}
