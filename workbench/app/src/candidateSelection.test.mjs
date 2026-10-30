/* WHAT A PICKED COLUMN CAN DO (the Candidate Set's selection, `candidateCard.js::selectionAction`,
   over what the type's own facts have been asked of each candidate, `candidateStanding.js`).

   A click on a candidate column SELECTS it -- the decision log follows it and the address records
   it -- and loads nothing. The act that puts a plan on the bench is a second one, and the strip
   above the columns names which is available for the column picked. Each state is a way the strip
   could mislead a reader who picked the candidate they preferred:

     none      nothing is picked: it says how to pick, and offers nothing that would act on no one;
     empty     no candidate was returned, and stuck: every one was refused. "Pick one" is not an
               instruction a reader can follow there, and the strip says what is true instead;
     open      a candidate the composer's loop placed and the type did not turn down;
     unjudged  a candidate nobody has asked the type's facts of (`refused` is null on it too, and
               it is a different null: a first-pass candidate, one the set's revise budget did not
               reach, a compose that ran without the loop). Loadable, because the bench is where
               the house is placed, and worded so as not to promise a plan;
     refused   a candidate the type's own facts turned down. Not loadable (WP-13.4), so the strip
               says WHY in the refusal's own facts, and never offers a link that does nothing.
               It is also the case "0 fatal" cannot see: findings and facts are two measures.

   The surface decides none of this: it renders `selectionView` and the tally, and this file holds
   those. A React component cannot be rendered under `node --test` here, so the logic that a mutation
   of the surface would have to survive is in the leaf, and the surface is held to consuming it. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import {
  adaptCandidate, selectionAction, selectionView, setStanding, tallyView, drawabilityView,
} from './candidateCard.js';
import { standingOf, standingOfSet, PLACEMENT_UNJUDGED } from './candidateStanding.js';
import { JOURNEY_WORDS } from './journey/journey.js';

const PLACED = { stop_reason: 'converged', summary: { rounds: 2, moves_applied: 0 } };
const served = (over = {}) => ({ parti: 'centre-passage-double-pile', parti_name: 'Centre Passage Double Pile',
  score: 70, counts: { serious: 19, minor: 65 }, revision: PLACED, refused: null, ...over });
const card = (c, i = 2) => adaptCandidate(c, i, null, null);
const REFUSED = { kind: 'type-fact-downgraded', facts: ['stacks', 'tiling'], conflicts: [],
  lines: ['a declared stack is drawn clear of the room it names'] };

test('what the type\'s facts have been asked of a candidate: refused, placed, or never judged', () => {
  assert.equal(standingOf(served({ refused: REFUSED })), 'refused');
  assert.equal(standingOf(served()), 'placed');
  // the same `refused: null`, a different null: nobody asked
  assert.equal(standingOf(served({ revision: null })), 'unjudged', 'a compose that ran without the loop');
  assert.equal(standingOf(served({ revision: null, revision_skipped: 'the set\'s revise budget was spent' })),
    'unjudged', 'a candidate the set\'s revise budget did not reach');
  assert.equal(standingOf({ parti: 'x' }), 'unjudged', 'a declared-pass candidate carries neither field');
  assert.equal(standingOf(served({ revision: { stop_reason: PLACEMENT_UNJUDGED } })), 'unjudged',
    'a loop whose first placement could not be evaluated judged nothing');
  // a verdict was given and this app cannot read it: not a refusal, and not a pass either
  assert.equal(standingOf(served({ refused: { kind: 'nonsense' } })), 'unjudged');
  assert.equal(standingOf(served({ refused: 'refused' })), 'unjudged');
  for (const bad of [null, undefined, 'x', 3, []]) assert.equal(standingOf(bad), 'unjudged', String(bad));
  // a refusal is read wherever it is carried, whether or not the loop's report came with it
  assert.equal(standingOf(served({ refused: REFUSED, revision: null })), 'refused');
});

/* The index just past the `</span>` that closes the `<span` opening at `open`, by counting nested
   spans; -1 if it never closes. A first `</span>` after a marker is the inner span's. */
function closeOfSpan(src, open) {
  const re = /<span\b|<\/span>/g;
  re.lastIndex = open;
  let depth = 0;
  for (let m = re.exec(src); m; m = re.exec(src)) {
    depth += m[0] === '</span>' ? -1 : 1;
    if (depth === 0) return m.index + m[0].length;
  }
  return -1;
}

/* THE COMPOSER RANKS ON THE SAME READING (ruled 16 Oct 2026: refused ranks last). `compose.py`'s
   `placement_standing` and this file's `standingOf` are two languages reading one card, so neither
   can import the other; `tests/fixtures/candidate_standing.json` is the one table both are held to
   (`tests/test_refusal_ranks_last.py` is the Python half). A strip that called a candidate
   "placed" while the ranking demoted it as "unjudged" is the screen the ranking was ruled to remove. */
const FIXTURE = JSON.parse(readFileSync(
  new URL('../../../tests/fixtures/candidate_standing.json', import.meta.url), 'utf8'));

test('the app reads every candidate in the composer\'s shared table as the composer does', () => {
  assert.ok(FIXTURE.cases.length >= 9, 'the table is read, not empty');
  for (const c of FIXTURE.cases) {
    assert.equal(standingOf(c.card), c.standing, c.name);
  }
  // the table covers every standing, and more than one route to unjudged: a table with one
  // unjudged row cannot tell the three nulls apart
  const by = {};
  for (const c of FIXTURE.cases) (by[c.standing] ||= []).push(c.name);
  assert.deepEqual(Object.keys(by).sort(), ['placed', 'refused', 'unjudged']);
  assert.ok(by.unjudged.length >= 4);
});

test('the stop reason the app matches is the revision loop\'s own string', () => {
  const py = readFileSync(new URL('../../../build/revise.py', import.meta.url), 'utf8');
  const m = py.match(/^STOP_PLACEMENT_UNJUDGED = "([^"]+)"/m);
  assert.ok(m, 'revise.py names the constant');
  assert.equal(PLACEMENT_UNJUDGED, m[1]);
});

test('a set\'s standing counts each candidate once, and openable is what the type did not turn down', () => {
  const s = standingOfSet([served({ refused: REFUSED }), served(), served({ revision: null }),
    served({ refused: { kind: 'infeasible', facts: ['bearing'] } }), served({ refused: { kind: 'nonsense' } })]);
  assert.deepEqual(s, { total: 5, refused: 2, placed: 1, unjudged: 2, openable: 3 });
  assert.equal(s.refused + s.placed + s.unjudged, s.total, 'every candidate lands in exactly one bucket');
  assert.deepEqual(standingOfSet([]), { total: 0, refused: 0, placed: 0, unjudged: 0, openable: 0 });
  assert.equal(standingOfSet(null).total, 0);
});

test('nothing picked says how to pick, and offers no act', () => {
  const a = selectionAction(null);
  assert.deepEqual([a.state, a.n, a.refused], ['none', null, null]);
  assert.equal(a.words, JOURNEY_WORDS.selection.none);
  assert.equal(selectionAction(undefined).state, 'none');
  assert.equal(selectionView(a).tag, 'span', 'no link where there is nothing to open');
});

test('a set with nothing to pick says so, instead of asking a reader to pick', () => {
  const none = setStanding([]);
  const empty = selectionAction(null, none);
  assert.deepEqual([empty.state, empty.words], ['empty', JOURNEY_WORDS.selection.empty]);
  const refused = setStanding([card(served({ refused: REFUSED }), 0), card(served({ refused: REFUSED }), 1)]);
  const stuck = selectionAction(null, refused);
  assert.deepEqual([stuck.state, stuck.words], ['stuck', JOURNEY_WORDS.selection.allRefused]);
  assert.match(stuck.words, /every candidate is refused/);
  // one candidate that can be opened is a set with something to pick
  const mixed = setStanding([card(served({ refused: REFUSED }), 0), card(served(), 1)]);
  assert.equal(selectionAction(null, mixed).state, 'none');
  // both are said in the refusal's ink, and neither is a link
  for (const a of [empty, stuck]) {
    const v = selectionView(a);
    assert.deepEqual([v.tag, v.tone], ['span', 'refusal'], a.state);
  }
});

test('a placed candidate offers to open it, at the index the server is asked for', () => {
  const a = selectionAction(card(served(), 3));
  assert.deepEqual([a.state, a.n, a.refused], ['open', 3, null]);
  assert.equal(a.words, JOURNEY_WORDS.selection.open('Centre Passage Double Pile'));
  // a candidate with no name still names itself by its diagram, then by nothing invented
  assert.match(selectionAction(card(served({ parti_name: undefined }))).words, /centre-passage-double-pile/);
  assert.match(selectionAction({ n: 0 }).words, /this candidate/);
  const v = selectionView(a);
  assert.deepEqual([v.tag, v.state, v.tone, v.words], ['button', 'open', 'quiet', a.words]);
});

test('a candidate nobody judged is openable and does not promise a plan', () => {
  const c = card(served({ revision: null }), 1);
  assert.equal(c.refused, null, 'the premise: no refusal on the card, and it is still not a pass');
  const a = selectionAction(c);
  assert.equal(a.state, 'unjudged');
  assert.equal(a.n, 1);
  assert.equal(a.words, JOURNEY_WORDS.selection.unjudged('Centre Passage Double Pile'));
  assert.match(a.words, /not judged for drawing/);
  assert.match(a.words, /may be refused/);
  const v = selectionView(a);
  assert.deepEqual([v.tag, v.state, v.tone], ['button', 'unjudged', 'quiet'], 'loadable: the bench is where it is placed');
});

test('a refused candidate says it cannot be drawn and names the facts the placement did not hold', () => {
  const c = card(served({ refused: REFUSED, counts: { serious: 19, minor: 65 } }));
  assert.equal(c.fatal_n, 0, 'the premise: no fatal finding, and refused all the same');
  const a = selectionAction(c);
  assert.equal(a.state, 'refused');
  assert.match(a.words, /Centre Passage Double Pile is refused, so it cannot be drawn/);
  assert.match(a.words, /stacks, tiling not held/);
  assert.equal(a.refused.kind, 'type-fact-downgraded');
  // a proven infeasibility is the stronger statement and is worded as one -- agreeing with its count
  const inf = selectionAction(card(served({ refused: { ...REFUSED, kind: 'infeasible', facts: ['bearing'] } })));
  assert.match(inf.words, /bearing cannot hold\b/);
  const inf2 = selectionAction(card(served({ refused: { ...REFUSED, kind: 'infeasible', facts: ['bearing', 'stacks'] } })));
  assert.match(inf2.words, /bearing, stacks cannot all hold/);
  // a refusal naming no fact says only what is true: refused, and so not drawable
  const bare = selectionAction(card(served({ refused: { kind: 'infeasible', facts: [], lines: ['x'] } })));
  assert.equal(bare.state, 'refused');
  assert.doesNotMatch(bare.words, / · /);
  // never a link, in the refusal's own ink -- the one place a "0 fatal" candidate must not be openable
  const v = selectionView(a);
  assert.deepEqual([v.tag, v.state, v.tone], ['span', 'refused', 'refusal']);
});

test('the two measures are independent in BOTH directions: a fatal finding is not a refusal', () => {
  // fatal findings and no refusal: disqualified in the order, still a candidate the bench may place
  const fatal = card(served({ counts: { fatal: 3, serious: 4 }, disqualified: true }));
  assert.equal(fatal.fatal_n, 3);
  assert.equal(selectionAction(fatal).state, 'open');
  assert.equal(setStanding([fatal]).refused, 0, 'a fatal finding is not counted as a refusal');
  // a refusal and no fatal finding: the case the original complaint was about
  const refused = card(served({ refused: REFUSED, counts: { serious: 43 } }));
  assert.equal(refused.fatal_n, 0);
  assert.equal(selectionAction(refused).state, 'refused');
  assert.equal(setStanding([refused]).refused, 1);
});

test('the tally says how many of a set were refused and how many were never judged, and is silent at zero', () => {
  const set = [served({ refused: REFUSED }), served(), served({ refused: { ...REFUSED, kind: 'infeasible' } }),
    served({ revision: null }), served({ refused: { kind: 'nonsense' } })].map((c, i) => card(c, i));
  // "of N" is the columns shown -- the population the two counts are over, which the set's
  // "returned X of Y asked for" is not (it leaves out the diagram the brief named, appended after)
  assert.deepEqual(tallyView(setStanding(set)), { refused: 2, unjudged: 2, of: 5 });
  assert.deepEqual(tallyView(setStanding([])), { refused: 0, unjudged: 0, of: 0 });
  assert.deepEqual(tallyView(setStanding(null)), { refused: 0, unjudged: 0, of: 0 });
  assert.deepEqual(tallyView(setStanding([card(served())])), { refused: 0, unjudged: 0, of: 1 }, 'a clean set carries no tally');
  assert.deepEqual(tallyView(null), { refused: 0, unjudged: 0, of: 0 });
  assert.equal(tallyView(setStanding(Array.from({ length: 4 }, (_, i) => card(served({ refused: REFUSED }), i)))).refused, 4,
    'every candidate refused is a set in which nothing may be drawn, and the count says so');
  assert.equal(JOURNEY_WORDS.selection.tallyUnjudged(3), '3 not judged for drawing');
  assert.equal(JOURNEY_WORDS.selection.tallyUnjudged(3, 5), '3 of 5 not judged for drawing');
  // a denominator that cannot be a population of that count is not printed
  for (const bad of [2, 'five', null, undefined, 3.5]) {
    assert.equal(JOURNEY_WORDS.selection.tallyUnjudged(3, bad), '3 not judged for drawing', String(bad));
  }
});

test('a column is selected from the keyboard by a real button, and the pick is announced', () => {
  /* The click sat on the <section>, which no key reaches, so the strip's "select a candidate" could
     not be followed without a mouse. The title is a button in the tab order that says whether it is
     the one picked, and the strip is a polite live region (audit follow-up, 16 Oct 2026). Held as
     joins: the decision of what a pick does is `selectionAction`, above. */
  const col = readFileSync(new URL('./components/CandidateColumn.jsx', import.meta.url), 'utf8');
  assert.match(col, /"data-candidate-select": c\.n/);
  assert.match(col, /"aria-pressed": selected \? "true" : "false"/);
  assert.match(col, /type: "button"/);
  assert.match(col, /e\.stopPropagation\(\);\s*onSelect\(c\);/, 'a click on the button selects once');
  assert.match(col, /\}, c\.parti_name\) : c\.parti_name\)\)/, 'a column with no handler stays plain text');
  const set = readFileSync(new URL('./surfaces/CandidateSet.jsx', import.meta.url), 'utf8');
  assert.match(set, /<span role="status" aria-live="polite" data-selection-live="">/);
  assert.match(set, /\{tally\.refused\} of \{tally\.of\} <Term id="judgment-refused" \/>/);
  assert.match(set, /tallyUnjudged\(tally\.unjudged, tally\.of\)/);
  // the act has a row of its own beneath the strip's other items, with a floor of two lines: the
  // grid moved 27 px (at 1100) and 47 px (at 1680) between a refused pick and an open one
  assert.match(set, /\} below=\{/, 'the row is the strip\'s own `below`, after `right` in the document too');
  assert.match(set, /data-selection-row="" style=\{\{ flex: '1 1 100%', minHeight: '2\.9em'/);
  // and that floor is two lines of the row's own type: 2 x the line height `--type-data-s` states
  const tokens = readFileSync(new URL('./theme/tokens.css', import.meta.url), 'utf8');
  const lh = tokens.match(/--type-data-s:[^;]*\/([0-9.]+)\s+var\(--mono\)/);
  assert.ok(lh, 'the token states a unitless line height');
  assert.equal(Number((2 * Number(lh[1])).toFixed(2)), 2.9, 'the floor in em is two lines of --type-data-s');
  assert.doesNotMatch(set, /minHeight: '2lh'/, 'the newer `lh` unit is not used');
  const chrome = readFileSync(new URL('./Chrome.jsx', import.meta.url), 'utf8');
  assert.match(chrome, /export function FilterStrip\(\{ children, right, filters, wrap, below \}\)/);
  assert.match(chrome, /\{right\}[\s\S]*\{wrap && below\}/, '`below` follows `right`');
  // the error stays its own alert, outside the polite region (two live regions would say it twice)
  const open = set.indexOf('<span role="status" aria-live="polite" data-selection-live="">');
  const err = set.indexOf('role="alert" data-selection-error');
  assert.ok(open !== -1 && err !== -1);
  const end = closeOfSpan(set, open);
  assert.ok(end !== -1, 'the region\'s closing tag is found by counting spans, not by the first one');
  assert.ok(err > end, 'the error is after the region closes');
  assert.ok(set.indexOf('data-selection-action', open) < end, 'and the act is inside it');
  // a working act stays in the tab order: `disabled` would drop the focus a keyboard reader had
  // just pressed it with, so both open acts say they are working with aria-disabled and refuse a
  // second press in the handler (asserted above)
  assert.doesNotMatch(set, /\bdisabled=\{opening\}/);
  assert.equal((set.match(/aria-disabled=\{opening \? 'true' : undefined\}/g) || []).length, 2);
});

test('the balanced scan that holds the live region finds the right closing tag', () => {
  /* The guard above counts nested spans. The first version took the first `</span>` after a
     marker, which is the closing tag of the INNER span -- so the error could sit inside the region
     and the guard still pass. Driven on a source where the inner span closes first. */
  const src = '<span role="status"><span a>x</span>{y}</span><span role="alert">e</span>';
  const open = src.indexOf('<span role="status"');
  assert.equal(closeOfSpan(src, open), src.indexOf('</span><span role="alert"') + '</span>'.length);
  assert.ok(src.indexOf('role="alert"') > closeOfSpan(src, open) - 1);
  const inside = '<span role="status"><span a>x</span><span role="alert">e</span></span>';
  assert.ok(inside.indexOf('role="alert"') < closeOfSpan(inside, 0), 'an alert inside the region is found to be inside');
  assert.equal(closeOfSpan('<span a>never closed', 0), -1);
});

test('the surface renders these decisions and decides none of its own', () => {
  /* The component cannot be rendered here, so what is held is the join: it takes the strip's
     element and ink from `selectionView`, the tally from `tallyView(setStanding(...))`, opens a
     card at the index the card carries, and does not offer the open act while one is in flight.
     The branches themselves are driven above and in the walk, which reads them off the page. */
  const src = readFileSync(new URL('./surfaces/CandidateSet.jsx', import.meta.url), 'utf8');
  assert.match(src, /import \{[^}]*\bselectionAction\b[^}]*\bselectionView\b[^}]*\} from '\.\.\/candidateCard\.js';/);
  assert.match(src, /selectionView\(selectionAction\(picked, standing\)\)/);
  assert.match(src, /tallyView\(standing\)/);
  assert.match(src, /setStanding\(cands\)/);
  assert.match(src, /view\.tag === 'button'/);
  assert.match(src, /api\.candidatePlan\(s\.jobId, c\.n\)/, 'the index is the card\'s own, in the server\'s order');
  assert.match(src, /if \(!c \|\| c\.refused \|\| opening\) return;/, 'a refused card is never fetched, nor a second click while one is in flight');
  assert.match(src, /catch \(e\)/, 'a failed open is said, not dropped');
  assert.match(src, /setOpenError\(e && e\.status === 404\s*\?\s*JOURNEY_WORDS\.selection\.gone\s*:\s*JOURNEY_WORDS\.selection\.failed\(errorText\(e\)\)\)/);
  assert.match(src, /\{openError && \(\s*<span role="alert" data-selection-error=""/);
  // the tally renders where the leaf says there is something to tally, and not otherwise
  assert.match(src, /\{tally\.refused > 0 && \(\s*<span data-set-refused=\{tally\.refused\}/);
  assert.match(src, /\{tally\.unjudged > 0 && \(\s*<span data-set-unjudged=\{tally\.unjudged\}/);
  // the refusal is said on the column's own counts line, where "fatal 0" is read
  const col = readFileSync(new URL('./components/CandidateColumn.jsx', import.meta.url), 'utf8');
  assert.match(col, /c\.refused && \/\*#__PURE__\*\/React\.createElement\("span", \{\s*"data-candidate-refused-mark": c\.refused\.kind/);
  assert.match(col, /id: "judgment-refused"/);
  assert.doesNotMatch(src, /function\s+(selectionAction|selectionView|setStanding|tallyView)\b|(selectionAction|selectionView)\s*=/,
    'defines none of its own');
});

/* R10 (ruled by Lucas, 30 Oct 2026): the set is read by TWO counts, "n not refused, m drawable
   where judged (hearth unjudged)", and an unjudged fact is never called held. The counts are the
   composer's (`result.drawability`, `compose.set_drawability`); the leaf reads them and the surface
   renders the leaf. */
test('the drawability tally reads both of the composer\'s counts and names each unjudged fact', () => {
  // R10's own example: three not refused, one drawable where judged, the fire unjudged on all three
  const v = drawabilityView({ returned: 4, not_refused: 3, drawable_where_judged: 1, unjudged_facts: { hearth: 3 } });
  assert.deepEqual(v, { returned: 4, notRefused: 3, whereJudged: 1, unjudged: [{ fact: 'hearth', on: null }] });
  // a fact unjudged on fewer than every not-refused candidate carries its own count, sorted by name
  const w = drawabilityView({ returned: 3, not_refused: 3, drawable_where_judged: 2,
    unjudged_facts: { stacks: 1, hearth: 3, bearing: 0 } });
  assert.deepEqual(w.unjudged, [{ fact: 'hearth', on: null }, { fact: 'stacks', on: 1 }],
    'a fact unjudged on none is not named; one unjudged on some says on how many');
  // nothing unjudged: nothing in brackets, and zero is a count the composer measured
  assert.deepEqual(drawabilityView({ returned: 2, not_refused: 0, drawable_where_judged: 0, unjudged_facts: {} }),
    { returned: 2, notRefused: 0, whereJudged: 0, unjudged: [] });
  // no reading -- a compose that placed nothing, an older result, a malformed one -- is no count,
  // never a zero: a count of drawable houses the composer never measured is not a count
  for (const d of [undefined, null, [], 'x', {}, { not_refused: 2 }, { drawable_where_judged: 1 },
    { not_refused: -1, drawable_where_judged: 0 }, { not_refused: 1.5, drawable_where_judged: 0 }]) {
    assert.equal(drawabilityView(d), null, JSON.stringify(d));
  }
  // the leaf does not count the cards: the composer's number stands even where cards would differ
  assert.equal(drawabilityView({ returned: 9, not_refused: 7, drawable_where_judged: 5 }).notRefused, 7);
});

test('the strip says both counts in R10\'s order, each word a glossary record', () => {
  /* Mutations: the strip renders one count, reads the counts off the cards, or calls an unjudged
     fact held (drops the `judgment-unjudged` word) -- each goes red here. */
  const src = readFileSync(new URL('./surfaces/CandidateSet.jsx', import.meta.url), 'utf8');
  assert.match(src, /import \{[^}]*\bdrawabilityView\b[^}]*\} from '\.\.\/candidateCard\.js';/);
  assert.match(src, /const drawn = drawabilityView\(result\.drawability\);/);
  const at = src.indexOf('{drawn && (');
  assert.ok(at > 0, 'the strip renders the drawability tally where the leaf gives one');
  const span = src.slice(at, src.indexOf('</span>', at));
  const order = ['{drawn.notRefused} <Term id="placed-and-not-refused" />',
    '{drawn.whereJudged} <Term id="drawable-where-judged" />',
    '{u.fact} <Term id="judgment-unjudged" />'].map((s) => span.indexOf(s));
  assert.ok(order.every((i) => i >= 0), `each count and its word: ${order}`);
  assert.deepEqual(order, order.slice().sort((a, b) => a - b), 'in R10\'s order: not refused, drawable where judged, unjudged');
  assert.match(span, /data-set-not-refused=\{drawn\.notRefused\} data-set-drawable-where-judged=\{drawn\.whereJudged\}/);
  // the words are the records' own: R10's "not refused" and "drawable where judged"
  const term = (id) => JSON.parse(readFileSync(new URL(`../../../glossary/${id}.json`, import.meta.url), 'utf8')).term;
  assert.equal(term('placed-and-not-refused'), 'not refused');
  assert.equal(term('drawable-where-judged'), 'drawable where judged');
  assert.equal(term('judgment-unjudged'), 'unjudged');
  // the composer writes the three keys the leaf reads
  const co = readFileSync(new URL('../../../build/compose.py', import.meta.url), 'utf8');
  assert.match(co, /return \{"returned": len\(cards\), "not_refused": len\(placed\), "drawable_where_judged": len\(where\),\s*"unjudged_facts":/);
  assert.doesNotMatch(src, /function\s+drawabilityView\b/, 'defines none of its own');
});
