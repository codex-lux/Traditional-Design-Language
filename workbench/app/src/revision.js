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

/* Where a finding stands after the analyst has read it.

   WP-13.9 (ruled 19 Sep 2026): a stranded room with a placed neighbour is `actionable` on
   EITHER engine, so the reading a reader used to get from the class alone -- a proof might
   have seated the door the author declared -- now rides on the row as `lever`/`lever_move`.
   This renders it wherever it is carried. Until the audit of that package it was rendered for
   `placement` only, so the field travelled the whole way from `critique.classify` through the
   report to the panel and was then dropped on the floor for exactly the two classes the
   ruling added it to. */
function _lever(item) {
  if (!item || !item.lever) return '';
  return ` — or the engine: ${item.lever_move || item.lever}`;
}

export function classTag(cls, item = {}) {
  switch (cls) {
    case 'actionable': return (item.move ? `a move answers this: ${item.move}` : 'a move answers this') + _lever(item);
    case 'placement': return item.lever
      ? `the engine's — lever: ${item.lever}` + (item.move ? ` (${item.move})` : '')
      : "the engine's";
    case 'critic_suspect': return "the critic's own — reads a literal";
    case 'architect': return "the architect's" + _lever(item);
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
/* `ctx` is optional and carries the counts the report already holds. THE SECOND ARGUMENT IS
   WHY THIS IS ONE FUNCTION AND NOT TWO: `no-applicable-move` is `revise.py:263`'s word for
   "picks is empty while actionable findings remain", and `_choose`'s picks empty TWO ways --
   no move answers what is left, or every move that does was tried, refused by the acceptance
   rule and marked tabu. On the search engine the second is the common one, because
   `add-the-grammar-door` carries `requires: "re-place"` and the re-placement moves the whole
   house; the stock label then tells a reader no move applies while eight were applied and
   rolled back. Measured on `briefs/family-georgian.json`, round 3 of one candidate went
   [9,69,118,24] -> [6,62,117,23] -- a LOWER fatal count -- and was still refused, because
   `_improves` also forbids a fatal id that was not there before. */
export function stopLabel(reason, ctx) {
  const refused = ctx && typeof ctx.refused === 'number' ? ctx.refused : 0;
  if (reason === 'no-applicable-move' && refused > 0)
    return `stopped: every move that answers a finding here was tried and refused (${refused})`;
  return STOP[reason] || (reason ? `stopped: ${reason}` : 'stopped: reason not stated');
}

/* What "nothing moved" MEANS, from the two counts the summary already carries. A round that
   offered no move and a round whose every move was rolled back are different facts about the
   house and read identically on the card today; this is the discriminator, and it is stated
   in counts rather than in a cause, because which of the acceptance rule's four gates refused
   a given move is in `rounds[].moves[]` and not in the summary. */
export function nothingMovedWhy(s) {
  /* THREE STATES. The `revised` SSE event carries `rounds` and `moves_applied` and NOT
     `moves_refused` (workbench/server/jobs.py), so the progress strip genuinely does not know
     which of the two happened -- and a two-state reader there would print "no move was
     offered" over a round that offered six and rolled back six, which is the flattering
     direction and the fake-pass shape this corpus names first. Absent is `null` and the
     caller omits the clause; 0 and >0 are the two it may assert. Found by this package's own
     first run, on the two pins below. */
  if (!s || typeof s.moves_refused !== 'number') return null;
  return s.moves_refused > 0
    ? `${s.moves_refused} move${s.moves_refused === 1 ? '' : 's'} tried and refused`
    : 'no move was offered';
}

/* One line per round for the progress strip while the loop runs. A round with no move is
   said so; a rolled-back round says so; nothing here ever reads "undefined". */
export function roundLine(ev) {
  if (!ev || typeof ev.n !== 'number') return 'round —';
  const moves = Array.isArray(ev.moves) ? ev.moves : [];
  // the entry's own verdict where the server states it; the by-absence rule only for a
  // report written before it did
  const applied = moves.filter((m) => ('accepted' in m ? m.accepted : (!m.refused && !m.refused_by_measurement)));
  /* WHY it was rolled back, live (WP-13.9's audit). The report that lands at the end of the
     loop distinguishes a round refused because the placement may not be DRAWN from one
     refused because the key rose; the strip that runs while the loop works did not, so one
     round had two accounts on one surface a few seconds apart. */
  const verdict = ev.accepted
    ? (ev.refused_after ? 'accepted — the placement it kept is still refused' : 'accepted')
    : moves.length
      ? (ev.rolled_back_by_refusal ? 'rolled back — the placement it produced may not be drawn' : 'rolled back')
      : 'no move applied';
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
      accepted: !!m.accepted,
      cleared: !!m.cleared,
      refused: m.refused || null,
      refusedByMeasurement: !!m.refused_by_measurement,
      refusedTheDrawing: !!m.refused_the_drawing,
    })),
    opened: r.opened || [], cleared: r.cleared || [],
    tabuForgotten: r.tabu_forgotten || 0,
    refusedAfter: !!r.refused_after,
    rolledBackByRefusal: !!r.rolled_back_by_refusal,
  }));
  const remaining = {};
  for (const cls of CLASSES) remaining[cls] = (report.remaining && report.remaining[cls]) || [];
  const rec = report.reclaimed;
  /* WHERE THIS REPORT IS BEING READ (WP-13.9). `with-its-own-placement` is the bench's solve
     path, where the rounds ran inside the evaluate and the sheet above the panel IS the
     placement the loop's key was measured on. The chip path still strips its record and
     re-solves it, so there the two really can differ and the panel must go on saying so --
     one field, two sentences, rather than a second panel that would drift from this one. */
  const ownPlacement = report.surfaced === 'with-its-own-placement';
  const pr = report.placement_refused || {};
  const refusedBefore = pr.before || null;
  const refusedAfter = pr.after || null;
  return {
    mode: report.mode || 'placed',
    surfaced: report.surfaced || null,
    ownPlacement,
    /* The DRAWING's own verdict, which a falling key says nothing about (WP-13.4): a house
       that breaks a hard fact of the type is refused and nothing draws it, however far the
       findings fell. Both ends, because the pair is the information -- cleared, carried, or
       (guarded by the acceptance rule and so never seen) newly made. */
    refusedBefore,
    refusedAfter,
    /* ONE DERIVATION. The audit of this package mutated `refusedBefore` to `null` and all 215
       JS tests stayed green, because `refusalCleared` read `pr.before` again rather than the
       field beside it -- one quantity, two readings, which is the defect this corpus names
       first and which no test could see while both happened to be right. */
    refusalCleared: !!refusedBefore && !refusedAfter,
    engine: report.engine || {},
    engineText: engineLabel(report.engine && report.engine.final),
    keyBefore: report.key_before, keyAfter: report.key_after,
    delta: keyDelta(report.key_before, report.key_after),
    stop: stopLabel(report.stop_reason, { refused: s.moves_refused ?? (report.refused || []).length }),
    roundsN: s.rounds ?? rounds.length,
    applied: s.moves_applied ?? rounds.reduce((n, r) => n + r.moves.filter((m) => m.accepted).length, 0),
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
  // the set's revise budget was spent before this candidate: it is as composed and SAYS so,
  // rather than reading as a compose that ran --no-revise (the session's audit)
  if (c && !c.revision && c.revision_skipped) return `not revised: ${c.revision_skipped}`;
  if (!c || !c.revision) return null;
  const rv = c.revision;
  const s = rv.summary || rv;
  const rounds = s.rounds ?? (rv.rounds ? rv.rounds.length : 0);
  const applied = s.moves_applied ?? 0;
  const before = typeof c.score_before === 'number' ? c.score_before : null;
  const after = typeof c.score === 'number' ? c.score : null;
  const drawn = Array.isArray(c.drawn_key_before) && Array.isArray(c.drawn_key_after)
    ? ` · drawn ${keyText(c.drawn_key_before)} → ${keyText(c.drawn_key_after)}` : '';
  /* WHY nothing moved, and HOW it stopped. Both facts are already on the candidate --
     `revision.summary.moves_refused` and `revision.stop_reason` (build/compose.py:1746) --
     and neither reached this line, so "nothing moved in 2 rounds" could not be told from
     "no move existed" or from "the budget stopped it". `stopLabel` is the one spelling and
     is called here rather than restated. */
  if (!applied) {
    const s2 = rv.stop_reason ?? s.stop_reason;
    const why = nothingMovedWhy(s);
    const stopped = s2 ? ` · ${stopLabel(s2, { refused: s.moves_refused ?? 0 })}` : '';
    return `revised: nothing moved in ${rounds} round${rounds === 1 ? '' : 's'}`
      + (why ? ` — ${why}` : '') + drawn + stopped;
  }
  const was = before !== null && after !== null && before !== after ? `was ${before.toFixed(1)} · ` : '';
  return `${was}revised in ${rounds} round${rounds === 1 ? '' : 's'}, ${applied} move${applied === 1 ? '' : 's'}${drawn}`;
}

/* A `revised` SSE event as the progress strip shows it. */
export function revisedEventLine(ev) {
  return `revised ${ev.parti_name || ev.parti || '?'}: ${revisedLine({
    revision: { stop_reason: ev.stop_reason,
                summary: { rounds: ev.rounds, moves_applied: ev.moves_applied,
                           // absent on a job whose server predates WP-14.1: `nothingMovedWhy`
                           // returns null for that and the clause is omitted rather than guessed
                           moves_refused: ev.moves_refused } },
    score_before: ev.score_before, score: ev.score,
    drawn_key_before: ev.drawn_key_before, drawn_key_after: ev.drawn_key_after,
  })}`;
}
