/* WP-9.3 -- the revision adapter. Each test is named for the sentence it forbids the bench
   from showing. No imports beyond node: the corpus job runs this suite with no npm install
   (no_bare_imports.test.mjs walks from here). */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  engineLabel, classTag, classesById, keyDelta, roundLine, adaptRevision, revisedLine,
  revisedEventLine, stopLabel, CLASSES,
} from './revision.js';

test('the engine label reads the engine that RAN, never the one requested', () => {
  assert.equal(engineLabel('cp-sat'), 'on the proved placement');
  assert.equal(engineLabel('heuristic'), 'on the searched placement');
  // `auto` is a request; a report carrying it as the final engine has not said what ran
  assert.equal(engineLabel('auto'), 'placement not evaluated');
  assert.equal(engineLabel(undefined), 'placement not evaluated');
});

test('equal keys read "unchanged", never an arrow between two equal numbers', () => {
  assert.equal(keyDelta([3, 44, 70, 19], [3, 44, 70, 19]), 'unchanged');
  assert.equal(keyDelta([3, 44, 70, 19], [0, 40, 70, 19]), 'fatal 3 → 0 · serious 44 → 40');
  assert.equal(keyDelta(null, [0, 0, 0, 0]), 'key not measured');
});

test('a round with no moves never renders "undefined"', () => {
  const line = roundLine({ n: 2, accepted: false, moves: [] });
  assert.equal(line, 'round 2 · no move applied · no move applied');
  assert.ok(!/undefined/.test(line));
  assert.ok(!/undefined/.test(roundLine({})));
  assert.ok(!/undefined/.test(roundLine(null)));
});

test('a rolled-back round says so and counts its refusals', () => {
  const line = roundLine({ n: 3, accepted: false, key_before: [1, 2, 3, 0], key_after: [1, 3, 3, 0],
    moves: [{ move: 'widen-for-furniture', refused_by_measurement: true },
            { move: 'raise-window-head', cleared: true }] });
  assert.equal(line, 'round 3 · rolled back · 1 move, 1 refused · [1, 2, 3, 0] → [1, 3, 3, 0]');
});

test('a suspect is neither cleared nor failed: it has its own tag and no verdict word', () => {
  const tag = classTag('critic_suspect', { id: 'fault:x' });
  assert.ok(/the critic's own/.test(tag));
  assert.ok(!/clear|fail|pass/i.test(tag));
  assert.equal(classTag('actionable', { move: 'widen-for-furniture' }), 'a move answers this: widen-for-furniture');
  assert.equal(classTag('placement', { lever: 'prove-it' }), "the engine's — lever: prove-it");
  assert.equal(classTag('nonsense'), null);
});

test('the class key is critic_suspect with an underscore, as critique.py spells it', () => {
  assert.ok(CLASSES.includes('critic_suspect'));
  const m = classesById({ critic_suspect: [{ id: 'a' }], architect: [{ id: 'b' }], actionable: [] });
  assert.equal(m.get('a').cls, 'critic_suspect');
  assert.equal(m.get('b').cls, 'architect');
  assert.equal(classesById(null).size, 0);
});

test('a rolled-back reclaim is reported with both keys, not hidden in the flattering one', () => {
  const r = adaptRevision({ mode: 'placed', engine: { final: 'heuristic' }, rounds: [],
    key_before: [3, 36, 46, 0], key_after: [3, 36, 46, 0], stop_reason: 'round-cap',
    reclaimed: { rolled_back: true, why: 'reclaim opened a fatal on this engine',
                 key_before: [3, 36, 46, 0], key_after: [4, 23, 49, 0], log: ['x'] },
    summary: { rounds: 0, moves_applied: 0, moves_refused: 0 } });
  assert.equal(r.reclaimed.rolledBack, true);
  assert.equal(r.reclaimed.delta, 'fatal 3 → 4 · serious 36 → 23 · minor 46 → 49');
  assert.equal(r.engineText, 'on the searched placement');
  assert.equal(r.stop, 'stopped: round cap');
  // a report written before the reclaim guard carried a bare log list; still renders
  const old = adaptRevision({ rounds: [], reclaimed: ['RECLAIMED: x'] });
  assert.equal(old.reclaimed.rolledBack, false);
  assert.deepEqual(old.reclaimed.log, ['RECLAIMED: x']);
});

test('every class is present in remaining even when the report omits it', () => {
  const r = adaptRevision({ rounds: [], remaining: { architect: [{ id: 'z' }] } });
  for (const c of CLASSES) assert.ok(Array.isArray(r.remaining[c]), c);
  assert.equal(r.remaining.architect.length, 1);
  assert.equal(adaptRevision(null), null);
});

test('revisedLine is null where the compose ran --no-revise, and says nothing moved rather than "was X" against the same X', () => {
  assert.equal(revisedLine({ score: 71.1 }), null);
  assert.equal(revisedLine({ score: 71.1, score_before: 71.1,
    revision: { summary: { rounds: 2, moves_applied: 0 } } }), 'revised: nothing moved in 2 rounds');
  const moved = revisedLine({ score: 73.7, score_before: 71.1,
    drawn_key_before: [10, 51, 73, 21], drawn_key_after: [0, 25, 71, 20],
    revision: { summary: { rounds: 2, moves_applied: 3 } } });
  assert.equal(moved, 'was 71.1 · revised in 2 rounds, 3 moves · drawn [10, 51, 73, 21] → [0, 25, 71, 20]');
  // one move applied and the score unchanged: no "was", the rounds and the move still said
  assert.equal(revisedLine({ score: 71.1, score_before: 71.1,
    revision: { summary: { rounds: 1, moves_applied: 1 } } }), 'revised in 1 round, 1 move');
});

test('a revised SSE event renders as a sentence, never as "tried undefined"', () => {
  const line = revisedEventLine({ parti_name: 'Five-Part Palladian', rounds: 2, moves_applied: 0,
    score_before: 63.6, score: 63.6 });
  assert.equal(line, 'revised Five-Part Palladian: revised: nothing moved in 2 rounds');
  assert.ok(!/undefined/.test(revisedEventLine({})));
});

test('a stop reason the adapter has not heard of is still stated, not swallowed', () => {
  assert.equal(stopLabel('something-new'), 'stopped: something-new');
  assert.equal(stopLabel(undefined), 'stopped: reason not stated');
});
