/* The first tests the workbench app has ever had. Every case below is a defect that shipped
   or a guarantee that would otherwise be enforced only by a comment. `npm test` in
   workbench/app, and build/check_all.py runs it (COULD NOT EVALUATE without node, never a
   pass). */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { whyText, isNative, byScore, ORDERS, order } from './candidateOrder.js';

test('whyText joins the reasons list instead of concatenating it', () => {
  const why = ['native to tidewater-georgian',
               'four-over-four is a canonical massing for the style'];
  // The shipped bug: React renders an array of strings with nothing between them.
  assert.equal(why.join(''), 'native to tidewater-georgianfour-over-four is a canonical massing for the style');
  assert.equal(whyText(why),
    'native to tidewater-georgian; four-over-four is a canonical massing for the style');
});

test('whyText drops only the clause the caller already printed, never its sentence', () => {
  const why = ['NOT native to this style — the composer is borrowing a diagram',
               'the style records no affinity for villa-tower'];
  const out = whyText(why, true);
  assert.ok(!/NOT native to this style/i.test(out), 'the duplicated clause must go');
  assert.ok(out.startsWith('the composer is borrowing a diagram'),
    `the rest of that sentence is the part worth reading, got ${JSON.stringify(out)}`);
  assert.ok(out.length > 40, 'stripping the whole sentence throws away the reason');
  assert.ok(out.includes('villa-tower'));
  // and a plain hyphen, which the corpus also uses
  assert.equal(whyText(['NOT native to this style - borrowed'], true), 'borrowed');
});

test('whyText survives the shapes the server can actually send', () => {
  assert.equal(whyText(undefined), '');
  assert.equal(whyText([]), '');
  assert.equal(whyText('a single string'), 'a single string');
  assert.equal(whyText(['a', null, '', 'b']), 'a; b');
});

test('isNative handles both shapes and lets the authoritative set win', () => {
  // Honest scope note: reading the list rather than letting RegExp.test coerce it via
  // Array.prototype.toString is a ROBUSTNESS fix, not a behaviour change — mutating it back
  // does not fail these cases, and no realistic corpus input separates them. What is worth
  // pinning is the contract, which the coerced version got right only by accident.
  const borrowed = { parti: 'octagon-radial',
    why_this_diagram: ['NOT native to this style — borrowing', 'octagon is common'] };
  const native = { parti: 'centre-passage-double-pile',
    why_this_diagram: ['native to tidewater-georgian'] };
  assert.equal(isNative(borrowed, null), false);
  assert.equal(isNative(native, null), true);
  assert.equal(isNative({ parti: 'x' }, null), true, 'no reasons recorded is not "borrowed"');
  assert.equal(isNative(borrowed, new Set(['octagon-radial'])), true,
    'the /api/partis answer outranks the prose fallback');
});

const C = (parti, score, fatal_n = 0, native = false, demerits = 0) =>
  ({ parti, score, fatal_n, native, demerits });

test('byScore is highest first, and deterministic when scores tie', () => {
  const list = [C('b', 50), C('a', 70), C('c', 50)];
  assert.deepEqual(list.slice().sort(byScore).map((c) => c.parti), ['a', 'b', 'c']);
  // a tie falls through to demerits, then to the parti id — never to input order
  // demerits must decide BEFORE the id, so the ids here are chosen to disagree with it:
  // alphabetically 'a' leads, but 'z' carries the lower demerit total and must come first.
  const tied = [C('a', 50, 0, false, 10), C('z', 50, 0, false, 5)];
  assert.deepEqual(tied.slice().sort(byScore).map((c) => c.parti), ['z', 'a']);
  assert.deepEqual(tied.slice().reverse().sort(byScore).map((c) => c.parti), ['z', 'a']);
  // and when score AND demerits tie, the parti id decides — the last guard against the
  // display order being settled by whatever order the composer happened to return
  const dead = [C('m', 50, 0, false, 3), C('f', 50, 0, false, 3), C('t', 50, 0, false, 3)];
  assert.deepEqual(dead.slice().sort(byScore).map((c) => c.parti), ['f', 'm', 't']);
  assert.deepEqual(dead.slice().reverse().sort(byScore).map((c) => c.parti), ['f', 'm', 't']);
});

test('a candidate with no score sorts last rather than as a zero', () => {
  // The fixture has to be able to SEPARATE -Infinity from 0, and the first version could
  // not: with only a null and a positive score, `a.score || 0` orders them identically. An
  // independent mutation audit made exactly that substitution and this test passed under
  // its own name. A candidate scoring zero is now in the list, between the two.
  const list = [C('none', null), C('zero', 0), C('low', 1)];
  assert.deepEqual(list.slice().sort(byScore).map((c) => c.parti), ['low', 'zero', 'none']);
  assert.deepEqual(list.slice().reverse().sort(byScore).map((c) => c.parti), ['low', 'zero', 'none']);
});

test('EVERY ordering puts a disqualified candidate last, whatever it scores', () => {
  // The guarantee the score no longer enforces on its own. A disqualified plan can carry the
  // highest number on the screen; under "highest score first" it must still not head the list.
  const ringer = C('ringer', 99.9, 2, true);
  for (const [name, o] of Object.entries(ORDERS)) {
    const list = [ringer, C('clean-a', 60), C('clean-b', 55, 0, true)];
    const got = list.slice().sort(order(o.cmp)).map((c) => c.parti);
    assert.equal(got[got.length - 1], 'ringer', `${name} let a disqualified plan rank above a clean one`);
  }
});

test('within the disqualified group, fewer fatals still ranks higher', () => {
  const list = [C('two', 90, 2), C('one', 10, 1), C('clean', 5, 0)];
  assert.deepEqual(list.slice().sort(order(ORDERS.fatal.cmp)).map((c) => c.parti),
    ['clean', 'one', 'two']);
});

test('the native ordering puts native diagrams first, then falls through to score', () => {
  const list = [C('borrowed-high', 90), C('native-low', 10, 0, true), C('native-high', 20, 0, true)];
  assert.deepEqual(list.slice().sort(order(ORDERS.native.cmp)).map((c) => c.parti),
    ['native-high', 'native-low', 'borrowed-high']);
});

test('every ordering names itself, because the column ordinal is a position not a verdict', () => {
  // Length checks alone let an audit SWAP the score and native chip labels — the UI would
  // have labelled the score ordering "native to the style" and nothing failed. Each chip and
  // each sentence now has to be about its own ordering.
  assert.match(ORDERS.score.chip, /score/i);
  assert.match(ORDERS.native.chip, /native/i);
  assert.match(ORDERS.fatal.chip, /fatal/i);
  assert.match(ORDERS.score.says, /score, highest first/i);
  assert.match(ORDERS.native.says, /native to the style/i);
  assert.match(ORDERS.fatal.says, /fatal findings decide the order/i);
  for (const [name, o] of Object.entries(ORDERS)) {
    assert.ok(o.chip && o.chip.length > 3, `${name} has no chip label`);
    assert.ok(o.says && o.says.length > 30, `${name} does not say what it did`);
  }
  // the two orderings that are not fatal-first must warn that a fatal plan is demoted
  for (const k of ['score', 'native']) {
    assert.ok(/fatal/i.test(ORDERS[k].says), `${k} does not mention the disqualified rule`);
  }
});

test('the disqualified group is still ordered by the chosen ordering, not by fatal count', () => {
  // order() must apply a BOOLEAN demotion. An audit replaced it with a numeric difference,
  // which silently re-sorts the disqualified group by fatal count under every ordering —
  // contradicting ORDERS.score.says, which promises the group is ordered by score. The
  // earlier test used a single ringer, so a two-candidate disqualified group never existed.
  const list = [C('dq-two-fatals-high-score', 90, 2), C('dq-one-fatal-low-score', 10, 1),
                C('clean', 50)];
  assert.deepEqual(list.slice().sort(order(ORDERS.score.cmp)).map((c) => c.parti),
    ['clean', 'dq-two-fatals-high-score', 'dq-one-fatal-low-score'],
    'under "highest score first" the disqualified group must be ordered by score');
  assert.deepEqual(list.slice().sort(order(ORDERS.fatal.cmp)).map((c) => c.parti),
    ['clean', 'dq-one-fatal-low-score', 'dq-two-fatals-high-score'],
    'under "fatal first" the disqualified group must be ordered by fatal count');
});
