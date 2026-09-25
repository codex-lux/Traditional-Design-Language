/* The first tests the workbench app has ever had. Every case below is a defect that shipped
   or a guarantee that would otherwise be enforced only by a comment. `npm test` in
   workbench/app, and build/check_all.py runs it (COULD NOT EVALUATE without node, never a
   pass). */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { whyText, isNative, nativityOf, NATIVITY_TERMS, byScore, ORDERS, order } from './candidateOrder.js';

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
  // the /api/partis answer outranks the prose fallback -- read as the row's own served
  // nativity since WP-14.25, never as whether the id is on the list
  assert.equal(isNative(borrowed, new Map([['octagon-radial', 'native']])), true,
    'the /api/partis answer outranks the prose fallback');
});

/* A LINEAGE PARTI IS NOT NATIVE, AND THE LIST IT IS ON IS NOT THE ANSWER (WP-14.25).

   `/api/partis?style=` lists a style's lineage partis beside its native ones since WP-14.19, each
   row carrying `nativity`. `isNative` used to read that list as a set of ids -- on it, native --
   so a lineage candidate flipped from not native to native the moment the list resolved. The
   fixture is a real relation: `five-part-palladian` is lineage to `adam-style` (WP-14.19's own
   census names the pair), and the reasons line is the composer's own lineage clause from
   `build/compose.py`. */
test('a lineage parti reads as lineage and never as native, from the candidate or from the list', () => {
  const why = ['native to an ancestor or relative of the style'];
  const lineage = { parti: 'five-part-palladian', nativity: 'lineage', why_this_diagram: why };
  const rows = new Map([['five-part-palladian', 'lineage'], ['centre-passage-double-pile', 'native']]);
  // the premise: the fixture IS on the list, so an id-in-list reading would call it native
  assert.ok(rows.has(lineage.parti), 'the lineage parti is on the list /api/partis gave');
  assert.equal(nativityOf(lineage, rows), 'lineage');
  assert.equal(isNative(lineage, rows), false, 'a lineage parti read as native because it was listed');
  assert.equal(isNative(lineage, null), false, "the candidate's own nativity decides with no list");
  // a candidate carrying no nativity of its own is read off its row, still never by membership
  const bare = { parti: 'five-part-palladian', why_this_diagram: why };
  assert.equal(nativityOf(bare, rows), 'lineage');
  assert.equal(isNative(bare, rows), false, 'the row on the list read as native because it was listed');
  // and a native one is native, by the same reading
  assert.equal(isNative({ parti: 'centre-passage-double-pile' }, rows), true);
  // the candidate's own statement outranks the list: it is the composer's, for this brief
  assert.equal(nativityOf({ parti: 'centre-passage-double-pile', nativity: 'borrowed' }, rows), 'borrowed');
  // a parti absent from a list that did not ask for borrowed rows is unknown, not borrowed
  assert.equal(nativityOf({ parti: 'octagon-radial' }, rows), null);
  // a value the relation does not have is not an answer, and neither is a list of bare ids
  assert.equal(nativityOf({ parti: 'x', nativity: 'native-ish' }, null), null);
  assert.equal(nativityOf(bare, new Set(['five-part-palladian'])), null);
});

test("every nativity is worded by a glossary record that exists, in the composer's own order", () => {
  assert.deepEqual(Object.keys(NATIVITY_TERMS), ['native', 'lineage', 'borrowed'],
    "compose.nativity's three answers, in its own order");
  for (const [n, id] of Object.entries(NATIVITY_TERMS)) {
    const f = new URL(`../../../glossary/${id}.json`, import.meta.url);
    assert.ok(existsSync(f), `${n} is worded by ${id}, which has no record`);
    assert.equal(JSON.parse(readFileSync(f, 'utf8')).id, id);
  }
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

test('the Candidate Set hands the served nativity to its reader and reads the named parti the server wrote', () => {
  /* WP-14.25. Two things this surface reads and must not rebuild: the style's own partis as an
     id -> nativity MAP (a Set of ids is what made every listed lineage parti read as native), and
     the composer's `named_by_brief` / `named_parti` fields, worded by the `named-by-the-brief`
     record. A source guard because the surface is a React component the node suite cannot mount;
     the behaviour it feeds is held by the two tests above. */
  const src = readFileSync(new URL('./surfaces/CandidateSet.jsx', import.meta.url), 'utf8');
  assert.match(src, /new Map\(\(r\.partis \|\| \[\]\)\.map\(\(p\) => \[p\.id, p\.nativity\]\)\)/,
    'the partis effect must build an id -> nativity Map from the served rows');
  assert.doesNotMatch(src, /new Set\(\(r\.partis/, 'a Set of ids reads a lineage parti as native');
  assert.match(src, /nativity: nativityOf\(c, nativePartis\)/);
  assert.match(src, /named_by_brief: !!c\.named_by_brief/);
  assert.match(src, /c\.named_by_brief && \(/);
  assert.match(src, /result\.named_parti\.returned === false/);
  assert.match(src, /\{result\.named_parti\.why\}/, "a named parti the set lacks says why, in the composer's words");
  // WP-14.27 added the third: the strip names the candidate the brief's parti APPENDED past the
  // set, by the same record, rather than counting it among the ones asked for.
  const flags = src.match(/<Term id="named-by-the-brief" \/>/g) || [];
  assert.equal(flags.length, 3,
    'the flag on the candidate, the line for a missing one and the strip\'s appended one all read the record');
  assert.ok(existsSync(new URL('../../../glossary/named-by-the-brief.json', import.meta.url)));
});
