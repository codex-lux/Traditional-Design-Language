/* WHAT A PICKED COLUMN CAN DO (the Candidate Set's selection, `candidateCard.js::selectionAction`).

   A click on a candidate column SELECTS it -- the decision log follows it and the address records
   it -- and loads nothing. The act that puts a plan on the bench is a second one, and the strip
   above the columns names which is available for the column picked. The states are three, and
   each is a way the strip could mislead a reader who picked the candidate they preferred:

     none     nothing is picked: it says how to pick, and offers nothing that would act on no one;
     open     a drawable candidate: the act is loading it on the bench;
     refused  a candidate the type's own facts turned down. It is not loadable (WP-13.4), so the
              strip says WHY in the refusal's own facts, and never offers a link that does nothing.
              It is also the case "0 fatal" cannot see: findings and facts are two measures, and a
              candidate with no fatal finding at all can still be one the placer may not draw. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { adaptCandidate, selectionAction, refusedCount } from './candidateCard.js';
import { JOURNEY_WORDS } from './journey/journey.js';

const served = (over = {}) => ({ parti: 'centre-passage-double-pile', parti_name: 'Centre Passage Double Pile',
  score: 70, counts: { serious: 19, minor: 65 }, ...over });
const card = (c, i = 2) => adaptCandidate(c, i, null, null);
const REFUSED = { kind: 'type-fact-downgraded', facts: ['stacks', 'tiling'], conflicts: [],
  lines: ['a declared stack is drawn clear of the room it names'] };

test('nothing picked says how to pick, and offers no act', () => {
  const a = selectionAction(null);
  assert.deepEqual([a.state, a.n, a.refused], ['none', null, null]);
  assert.equal(a.words, JOURNEY_WORDS.selection.none);
  assert.equal(selectionAction(undefined).state, 'none');
});

test('a drawable candidate offers to open it, at the index the server is asked for', () => {
  const a = selectionAction(card(served(), 3));
  assert.deepEqual([a.state, a.n, a.refused], ['open', 3, null]);
  assert.equal(a.words, JOURNEY_WORDS.selection.open('Centre Passage Double Pile'));
  // a candidate with no name still names itself by its diagram, then by nothing invented
  assert.match(selectionAction(card(served({ parti_name: undefined }))).words, /centre-passage-double-pile/);
  assert.match(selectionAction({ n: 0 }).words, /this candidate/);
});

test('a refused candidate says it cannot be drawn and names the facts the placement did not hold', () => {
  const c = card(served({ refused: REFUSED, counts: { serious: 19, minor: 65 } }));
  assert.equal(c.fatal_n, 0, 'the premise: no fatal finding, and refused all the same');
  const a = selectionAction(c);
  assert.equal(a.state, 'refused');
  assert.match(a.words, /Centre Passage Double Pile is refused, so it cannot be drawn/);
  assert.match(a.words, /stacks, tiling not held/);
  assert.equal(a.refused.kind, 'type-fact-downgraded');
  // a proven infeasibility is the stronger statement and is worded as one
  const inf = selectionAction(card(served({ refused: { ...REFUSED, kind: 'infeasible', facts: ['bearing'] } })));
  assert.match(inf.words, /bearing cannot all hold/);
  // a refusal naming no fact says only what is true: refused, and so not drawable
  const bare = selectionAction(card(served({ refused: { kind: 'infeasible', facts: [], lines: ['x'] } })));
  assert.equal(bare.state, 'refused');
  assert.doesNotMatch(bare.words, / · /);
});

test('a set says how many of its candidates were refused, and counts only a refusal that was read', () => {
  const set = [served({ refused: REFUSED }), served(), served({ refused: { ...REFUSED, kind: 'infeasible' } }),
    // a body this app cannot read as a refusal is no refusal: unjudged is not refused, nor passed
    served({ refused: { kind: 'nonsense' } }), served({ refused: null })].map((c, i) => card(c, i));
  assert.equal(refusedCount(set), 2);
  assert.equal(refusedCount([]), 0);
  assert.equal(refusedCount(null), 0);
  assert.equal(refusedCount([card(served())]), 0, 'a clean set says nothing is refused');
  assert.equal(refusedCount(Array.from({ length: 4 }, (_, i) => card(served({ refused: REFUSED }), i))), 4,
    'every candidate refused is a set in which nothing may be drawn, and the count says so');
});

test('the surface acts on the card it adapted: it reads the pick through this decision', () => {
  /* The click that loads a plan and the strip that says it will must not disagree, so the surface
     takes both from `selectionAction` over the column picked. Read narrowly: the import, the
     decision over the picked card, and a link drawn only in the `open` state. */
  const src = readFileSync(new URL('./surfaces/CandidateSet.jsx', import.meta.url), 'utf8');
  assert.match(src, /import \{[^}]*\bselectionAction\b[^}]*\} from '\.\.\/candidateCard\.js';/);
  assert.match(src, /selectionAction\(picked\)/);
  assert.match(src, /action\.state === 'open'/);
  assert.match(src, /refusedCount\(cands\)/);
  assert.doesNotMatch(src, /function\s+selectionAction\b|selectionAction\s*=/, 'defines none of its own');
});
