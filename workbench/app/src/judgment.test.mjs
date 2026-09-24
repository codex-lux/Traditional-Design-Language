/* THREE STATES, HELD FROM BOTH ENDS (WP-14.6).

   The subject is that `unjudged` is its own state. Every assertion that a value maps to
   `unjudged` is paired with one that it maps to neither of the others, because the two ways to
   collapse the third state — into a pass, or into a fail — are different defects, and a test that
   only checked `!== 'passed'` would bless the second. `Proportions.jsx`'s `holds ? 'pass' : 'fail'`
   is the second, and it is what this module replaces. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import {
  JUDGMENT_STATES, judgmentOf, JUDGMENT_MARK, judgmentTermId, CONSTRAINT_STATES, constraintStateOf,
} from './judgment.js';

const ROOT = new URL('../../../', import.meta.url);

test('true passes, false fails, and an absent verdict is unjudged — never either of the others', () => {
  assert.equal(judgmentOf(true), 'passed');
  assert.equal(judgmentOf(false), 'failed');
  for (const absent of [null, undefined]) {
    const got = judgmentOf(absent);
    assert.equal(got, 'unjudged', `${absent} must read as unjudged`);
    assert.notEqual(got, 'failed', `${absent} is not a failure: nothing was evaluated`);
    assert.notEqual(got, 'passed', `${absent} is not a pass: nothing was evaluated`);
  }
  assert.equal(judgmentOf(), 'unjudged', 'no argument at all is an absent verdict');
});

test('a value that is not a boolean is not a verdict, in either direction', () => {
  // Truthiness would turn each of these into a pass or a fail. None of them is a judgment.
  for (const v of [1, 0, -1, 'true', 'false', '', 'passed', NaN, {}, [], [true]]) {
    assert.equal(judgmentOf(v), 'unjudged', `${JSON.stringify(v)} must not be read as a verdict`);
  }
});

test('exactly three states are reachable, and they are the ones the module names', () => {
  const seen = new Set([true, false, null, undefined, 0, 'x'].map(judgmentOf));
  assert.deepEqual([...seen].sort(), [...JUDGMENT_STATES].sort());
  assert.equal(JUDGMENT_STATES.length, 3);
  assert.ok(Object.isFrozen(JUDGMENT_STATES) && Object.isFrozen(JUDGMENT_MARK));
});

test('the term id of a judgment is the glossary id the PRD names, for each state', () => {
  assert.deepEqual(JUDGMENT_STATES.map(judgmentTermId),
    ['judgment-passed', 'judgment-failed', 'judgment-unjudged']);
});

test('JUDGMENT_MARK speaks JudgmentMark’s own three states, read off the component', () => {
  /* The mark is a React component the corpus job cannot import; its states are read out of its
     source instead. The premise is asserted first: if the component stopped comparing `state`
     against these strings, this test would otherwise be comparing JUDGMENT_MARK with nothing. */
  const src = readFileSync(new URL('components/JudgmentMark.jsx', import.meta.url), 'utf8');
  const compared = [...src.matchAll(/state === '([a-z]+)'/g)].map((m) => m[1]);
  assert.ok(compared.length >= 2, 'JudgmentMark must still branch on its state prop');
  const wordsBlock = /const words = \{([^}]*)\}/.exec(src);
  assert.ok(wordsBlock, 'JudgmentMark must still word each state it draws');
  const worded = [...wordsBlock[1].matchAll(/([a-z]+):\s*'/g)].map((m) => m[1]);
  assert.equal(worded.length, 3, `JudgmentMark words ${worded.length} states`);
  const markStates = new Set([...compared, ...worded]);
  assert.deepEqual([...markStates].sort(), Object.values(JUDGMENT_MARK).sort(),
    'every judgment must map onto a state JudgmentMark draws, and no state may be left without one');
  // and the two collapses, stated as the mark's own states
  assert.notEqual(JUDGMENT_MARK[judgmentOf(null)], 'fail');
  assert.notEqual(JUDGMENT_MARK[judgmentOf(null)], 'pass');
});

function corpusConstraints() {
  const dir = new URL('styles/', ROOT);
  const out = [];
  for (const f of readdirSync(dir).filter((n) => n.endsWith('.json')).sort()) {
    const node = JSON.parse(readFileSync(new URL(f, dir), 'utf8'));
    for (const c of node.constraints || []) out.push(c);
  }
  return out;
}

test('every constraint in the corpus takes exactly one of the three states', () => {
  const cs = corpusConstraints();
  assert.ok(cs.length > 0, 'the premise: the corpus carries constraints to classify');
  const counts = Object.fromEntries(CONSTRAINT_STATES.map((s) => [s, 0]));
  for (const c of cs) {
    const s = constraintStateOf(c);
    assert.ok(CONSTRAINT_STATES.includes(s), `${c.id} took ${s}`);
    counts[s] += 1;
    // the rule, stated as its two halves rather than re-run: a test is decisive...
    if ('test' in c) assert.equal(s, 'constraint-executable', `${c.id} carries a test`);
    // ...and a judgment-scope record with no test is never drawn as executable
    if (!('test' in c) && c.scope === 'judgment') assert.equal(s, 'judgment-yours-to-judge', c.id);
  }
  assert.equal(Object.values(counts).reduce((a, b) => a + b, 0), cs.length);
  assert.ok(counts['constraint-executable'] > 0 && counts['judgment-yours-to-judge'] > 0,
    `the corpus must exercise both populated states: ${JSON.stringify(counts)}`);
});

test('the third constraint state is one the schema permits, so it is named rather than assumed empty', () => {
  const schema = JSON.parse(readFileSync(new URL('schema/constraint.schema.json', ROOT), 'utf8'));
  assert.ok(!schema.required.includes('test'), 'the premise: a constraint may carry no test');
  assert.ok(schema.properties.scope.enum.includes('judgment'), 'and judgment is a scope');
  const other = schema.properties.scope.enum.find((s) => s !== 'judgment');
  // a record in a measurable scope with no test yet: executable would be a lie about it
  assert.equal(constraintStateOf({ id: 'x.c01', scope: other }), 'constraint-no-test-yet');
  assert.notEqual(constraintStateOf({ id: 'x.c01', scope: other }), 'constraint-executable');
  // and a test outranks the scope that says the sources do not determine it
  assert.equal(constraintStateOf({ id: 'x.c02', scope: 'judgment', test: { expression: 'a' } }),
    'constraint-executable');
  assert.equal(constraintStateOf(null), 'constraint-no-test-yet');
});
