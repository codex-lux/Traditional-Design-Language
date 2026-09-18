/* THE REFUSAL LEAF, DRIVEN BRANCH BY BRANCH (WP-13.4).

   `sheet/refusal.js` is the app's one reader of `build/typefacts.py::refusal`, and the server
   slice of this package was being built in a worktree beside this one while these were written
   — so every body here is HAND-BUILT to the contract both slices were given, exactly as
   `engineClaim.test.mjs` drives its own leaf. That is deliberate and not a stopgap: a test that
   could only run against a live solve would be a statement about a 25 s budget, and the branch
   that matters most (a refused placement) is one no shipped record reaches on demand.

   THE THREE STATES ARE THE SUBJECT. `refused`, `drawable` and `unstated` are asserted against
   each other in both directions, because collapsing the third into either of the first two is
   what this whole package exists to stop: reading `unstated` as `drawable` draws a house the
   server refused, and reading it as `refused` blacks out every surface against a server that has
   not shipped the contract yet. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  REFUSAL_KINDS, REFUSAL_STATES, readRefusal, conflictLines, unstatedConflicts, namesSomething,
  refusalHeadline, refusalState, placementRefusal, sketchOf, mayDraw, mayExport, errorText,
  refusalFromError, isMissingLibrary, evaluateRefusal,
} from './sheet/refusal.js';

/* The contract's own shape, as `typefacts.refusal(plan)` returns it. */
const DOWNGRADED = {
  kind: 'type-fact-downgraded',
  facts: ['stacks', 'hearth'],
  conflicts: [
    { kind: 'stack', key: ['primary', 'drawing'], why: 'the claim was released' },
    { kind: 'hearth', key: ['dining'], why: 'the wall the flue names was released' },
  ],
  lines: [
    'the Drawing Room does not stand under the Primary Bedroom it is declared to carry',
    'the Dining Room fire does not stand on a wall the massing puts a flue on',
  ],
  engine: 'cp-sat',
  status: 'OPTIMAL (hard-only) — kept hard-only phase A',
};

const INFEASIBLE = {
  kind: 'infeasible',
  facts: [],
  conflicts: ['Dining Room and Butler’s Pantry share a door'],
  lines: [],
  engine: 'cp-sat',
  status: 'INFEASIBLE',
};

test('both kinds the server mints are read, and nothing else is', () => {
  assert.deepEqual([...REFUSAL_KINDS], ['infeasible', 'type-fact-downgraded']);
  assert.equal(readRefusal(DOWNGRADED).kind, 'type-fact-downgraded');
  assert.equal(readRefusal(INFEASIBLE).kind, 'infeasible');
  // an object with a kind this app does not know is NOT a refusal: it is unstated, and drawing
  // an empty conflict set over it would be worse than drawing the house
  assert.equal(readRefusal({ kind: 'something-new', lines: ['x'] }), null);
  assert.equal(readRefusal({ facts: ['stacks'] }), null);
  for (const junk of [null, undefined, 0, '', 'infeasible', [], [DOWNGRADED]]) {
    assert.equal(readRefusal(junk), null, `${JSON.stringify(junk)} is not a refusal`);
  }
});

test('the 422 wrapper is unwrapped once, and its error sentence travels with the verdict', () => {
  // `corpus._placed`'s own return, which the routes hand out as the 422 detail
  const detail = {
    error: 'the placement breaks two hard facts of the type and is refused, not drawn',
    refused_placement: DOWNGRADED,
    unsolved: true,
  };
  const r = readRefusal(detail);
  assert.equal(r.kind, 'type-fact-downgraded');
  assert.deepEqual(r.facts, ['stacks', 'hearth']);
  assert.equal(r.error, detail.error);
  // and the bare form gives the same verdict, so no caller has to know which layer carries it
  assert.equal(readRefusal(DOWNGRADED).kind, r.kind);
  // a wrapper whose inner body is unreadable is unreadable, not a refusal with an error on it
  assert.equal(readRefusal({ error: 'x', refused_placement: { kind: 'nope' } }), null);
});

test('a refusal is content: the sentences are the corpus’s and nothing is stringified', () => {
  const r = readRefusal(DOWNGRADED);
  assert.deepEqual(conflictLines(r), DOWNGRADED.lines);
  assert.equal(unstatedConflicts(r), 0);
  assert.ok(namesSomething(r));
  // no sentences, string conflicts: those ARE the corpus's own words (WP-2.3's list items)
  const i = readRefusal(INFEASIBLE);
  assert.deepEqual(conflictLines(i), INFEASIBLE.conflicts);
  assert.equal(unstatedConflicts(i), 0);
  // no sentences, OBJECT conflicts: counted, never turned into prose nobody wrote
  const mute = readRefusal({ ...DOWNGRADED, lines: [] });
  assert.deepEqual(conflictLines(mute), []);
  assert.equal(unstatedConflicts(mute), 2);
  assert.ok(namesSomething(mute), 'it still names two facts');
  // fewer sentences than conflicts: the remainder is counted, not silently dropped
  const partial = readRefusal({ ...DOWNGRADED, lines: [DOWNGRADED.lines[0]] });
  assert.equal(conflictLines(partial).length, 1);
  assert.equal(unstatedConflicts(partial), 1);
});

test('a refusal that names nothing says so rather than drawing an empty panel', () => {
  const bare = readRefusal({ kind: 'infeasible', facts: [], conflicts: [], lines: [] });
  assert.ok(bare, 'it is still a refusal');
  assert.equal(namesSomething(bare), false);
  assert.equal(conflictLines(bare).length, 0);
  assert.equal(namesSomething(null), false);
});

test('the headline counts what was named, in both kinds', () => {
  assert.equal(refusalHeadline(readRefusal(DOWNGRADED)),
    '2 hard facts of the type downgraded (2 conflicts)');
  assert.equal(refusalHeadline(readRefusal(INFEASIBLE)),
    'infeasible as declared — proven (1 conflict)');
  assert.equal(refusalHeadline(readRefusal({ kind: 'infeasible' })),
    'infeasible as declared — proven');
  assert.equal(refusalHeadline(null), null);
  // an object conflict with no sentence is still COUNTED in the headline: a refusal that named
  // two conflicts must not announce itself as naming none
  assert.equal(refusalHeadline(readRefusal({ ...DOWNGRADED, lines: [] })),
    '2 hard facts of the type downgraded (2 conflicts)');
});

test('THREE STATES, and the third is not either of the other two', () => {
  assert.deepEqual([...REFUSAL_STATES], ['refused', 'drawable', 'unstated']);
  assert.equal(refusalState({ geometry_report: { refused: DOWNGRADED } }), 'refused');
  // the server judged and found nothing to refuse -- the KEY is what says so
  assert.equal(refusalState({ geometry_report: { refused: null } }), 'drawable');
  // no key: a server that does not answer this contract. Not a pass.
  assert.equal(refusalState({ geometry_report: { solver: { engine: 'cp-sat' } } }), 'unstated');
  assert.equal(refusalState({}), 'unstated');
  assert.equal(refusalState(null), 'unstated');
  // a body under the key that this app cannot read is unstated too, never refused-with-nothing
  assert.equal(refusalState({ geometry_report: { refused: { kind: 'later-kind' } } }), 'unstated');
});

test('placementRefusal returns the verdict, and refusalState tells its two nulls apart', () => {
  assert.equal(placementRefusal({ geometry_report: { refused: DOWNGRADED } }).kind,
    'type-fact-downgraded');
  const judged = { geometry_report: { refused: null } };
  const unjudged = { geometry_report: {} };
  assert.equal(placementRefusal(judged), null);
  assert.equal(placementRefusal(unjudged), null);
  // identical nulls, different states: this is the whole reason refusalState exists
  assert.notEqual(refusalState(judged), refusalState(unjudged));
});

test('the wall drag’s sketch is read, and `working` is what marks it', () => {
  const drag = { geometry_report: { refused: null },
    sketch: { working: true, refused: DOWNGRADED, reason: 'a wall drag asks for the search by name' } };
  const s = sketchOf(drag);
  assert.equal(s.working, true);
  assert.equal(s.reason, 'a wall drag asks for the search by name');
  assert.equal(s.refused.kind, 'type-fact-downgraded');
  // a sketch with no refusal behind it is still a sketch: a gesture's placement is not a drawing
  const clean = sketchOf({ sketch: { working: true, refused: null, reason: 'the drag' } });
  assert.ok(clean);
  assert.equal(clean.refused, null);
  // and nothing else is one
  for (const junk of [{}, { sketch: null }, { sketch: {} }, { sketch: { working: false } },
    { sketch: { working: 'true' } }, { sketch: [] }, null]) {
    assert.equal(sketchOf(junk), null, `${JSON.stringify(junk)} is not a sketch`);
  }
});

test('MAY THIS BE DRAWN, and may it leave as a file: one verdict each, and they differ', () => {
  const refused = { geometry_report: { refused: INFEASIBLE } };
  const clean = { geometry_report: { refused: null } };
  const unstated = { geometry_report: {} };
  const drag = { geometry_report: { refused: null }, sketch: { working: true, refused: null } };
  const dragRefused = { geometry_report: { refused: null }, sketch: { working: true, refused: INFEASIBLE } };

  assert.equal(mayDraw(refused), false);
  assert.equal(mayExport(refused), false);
  assert.equal(mayDraw(clean), true);
  assert.equal(mayExport(clean), true);
  // unstated DRAWS: there is no verdict to honour and this leaf may not invent one
  assert.equal(mayDraw(unstated), true);
  assert.equal(mayExport(unstated), true);
  // THE SKETCH IS THE ONE PLACE THE TWO VERDICTS DIVERGE. The bench draws it under a WORKING
  // banner; no other surface draws it, and it may never be handed to a drafter.
  assert.equal(mayDraw(drag), false, 'no surface draws a sketch unless it asked for one');
  assert.equal(mayDraw(drag, { allowSketch: true }), true, 'the bench asks for one');
  assert.equal(mayExport(drag), false, 'and a sketch is never a file');
  assert.equal(mayExport(drag, { allowSketch: true }), false,
    'mayExport takes no such option -- a sketch is never exportable');
  assert.equal(mayDraw(dragRefused, { allowSketch: true }), true);
  assert.equal(mayExport(dragRefused), false);
});

test('one reader of a thrown client error, in every shape the client throws', () => {
  // postJSON's own throw: FastAPI's HTTPException detail
  assert.equal(errorText({ status: 422, body: { detail: { error: 'a sentence' } } }), 'a sentence');
  // a detail that is a bare string (FastAPI's default for a raised string)
  assert.equal(errorText({ status: 422, body: { detail: 'a bare detail' } }), 'a bare detail');
  // a body with error at the top (corpus returns shaped this way reach some routes)
  assert.equal(errorText({ status: 422, body: { error: 'top-level' } }), 'top-level');
  assert.equal(errorText({ message: 'POST /x → 500', body: {} }), 'POST /x → 500');
  assert.equal(errorText('a string'), 'a string');
  assert.equal(errorText(null), null);
  // an empty string in detail.error must fall through rather than blanking the panel
  assert.equal(errorText({ body: { detail: { error: '   ' }, error: 'the real one' } }), 'the real one');
});

test('a refused placement arrives through the error, and a missing library does not', () => {
  const e422 = { status: 422, body: { detail: { error: 'refused', refused_placement: DOWNGRADED } } };
  assert.equal(refusalFromError(e422).kind, 'type-fact-downgraded');
  assert.equal(isMissingLibrary(e422), false);
  // 501 + `refusal` is app.py's MISSING LIBRARY, and reading it as a refused house would show a
  // conflict set with no conflicts in it on a machine that simply has no ezdxf
  const e501 = { status: 501, body: { detail: { error: 'ezdxf is not installed', refusal: true } } };
  assert.equal(refusalFromError(e501), null);
  assert.equal(isMissingLibrary(e501), true);
  assert.equal(errorText(e501), 'ezdxf is not installed');
  // and neither reader fires on an ordinary failure
  const e500 = { status: 500, body: {}, message: 'boom' };
  assert.equal(refusalFromError(e500), null);
  assert.equal(isMissingLibrary(e500), false);
  assert.equal(refusalFromError(null), null);
  assert.equal(isMissingLibrary(null), false);
});

test('the evaluate 200 carries its refusal beside a check that still ran', () => {
  const res = { check: { findings: [], counts: {} }, placement_refused: INFEASIBLE,
    error: 'the placement was refused' };
  const r = evaluateRefusal(res);
  assert.equal(r.kind, 'infeasible');
  assert.equal(r.error, 'the placement was refused');
  assert.equal(res.placement, undefined, 'the contract sends no placement with a refusal');
  // an ordinary evaluate carries none
  assert.equal(evaluateRefusal({ check: {}, placement: { geometry_report: {} } }), null);
  assert.equal(evaluateRefusal(null), null);
  // and a refusal whose own `error` is set wins over the body's, because it is the nearer word
  assert.equal(evaluateRefusal({ placement_refused: { ...INFEASIBLE, error: 'nearer' },
    error: 'further' }).error, 'nearer');
});

// ------------------------------------------------- the callers, read as source
/* ONE SPELLING, AND THESE ARE WHAT HOLD IT. The verdict "may this be drawn" is
   `build/typefacts.py::refusal`'s, read through `sheet/refusal.js`, and a surface that counted
   downgraded `type_facts` for itself would be a second answer to one question — the defect this
   repository has met under four other names (the citation grammar's three spellings,
   `required_wall_ft`'s three, the proof verdict's three at WP-13.2, the element comprehension's
   five at WP-11.15).

   A SOURCE GUARD IS A GUARD ON ONE ROUTE IN, and WP-12.2 says so: it catches the second reader
   that spells the field's NAME and cannot see one that spells the arithmetic out. It is kept
   because the cheap defect is the cheap one to catch, and because the behavioural half — a
   refused body reaching a surface and no plate coming back — needs a live server and lives in
   `e2e/walk.mjs`. */
const HERE = dirname(fileURLToPath(import.meta.url));

function stripComments(src) {
  let out = '', i = 0;
  const n = src.length;
  while (i < n) {
    if (src.startsWith('/*', i)) { const j = src.indexOf('*/', i + 2); i = j < 0 ? n : j + 2; }
    else if (src.startsWith('//', i)) { const j = src.indexOf('\n', i); i = j < 0 ? n : j; }
    else { out += src[i]; i += 1; }
  }
  return out;
}

const live = (rel) => stripComments(readFileSync(resolve(HERE, rel), 'utf8'));

/* Every surface that decides whether to draw or to export. `Sheet.jsx` reads the leaf for the
   WORKING banner alone and is listed with the rest, because a sheet that stopped importing it
   would draw a wall drag's sketch as a drawing. */
const READERS = [
  ['surfaces/PlanWorkbench.jsx', '../sheet/refusal.js'],
  ['surfaces/DrawingSet.jsx', '../sheet/refusal.js'],
  ['surfaces/ExportDetails.jsx', '../sheet/refusal.js'],
  ['surfaces/CandidateSet.jsx', '../sheet/refusal.js'],
  ['sheet/Sheet.jsx', './refusal.js'],
];

test('every surface that decides whether to draw READS the leaf', () => {
  for (const [rel, spec] of READERS) {
    assert.ok(live(rel).includes(`from '${spec}'`),
      `${rel} must import the refusal leaf from '${spec}'`);
  }
});

test('and not one of them re-derives the verdict from type_facts', () => {
  // The premise first: `type_facts` really is the key a second reader would reach for, so this
  // is not a pattern that could never match whatever the surfaces do.
  const py = readFileSync(resolve(HERE, '../../../build/typefacts.py'), 'utf8');
  assert.match(py, /type_facts/, 'the record key this guard is about must still exist');
  for (const [rel] of READERS) {
    assert.doesNotMatch(live(rel), /type_facts/,
      `${rel} must not read type_facts: the refusal verdict is typefacts.refusal's, read once`);
    assert.doesNotMatch(live(rel), /['"]downgraded['"]/,
      `${rel} must not count downgraded facts for itself`);
  }
});

test('the plate is gated on the leaf’s verdict and not on a placement being present', () => {
  /* The defect this whole package removes, stated as a source property: `<Sheet>` rendered under
     `{placement && …}` draws whatever the record carries, refusal and all. It renders under
     `drawable` now, and `drawable` is `mayDraw`'s answer.

     THIS IS THE WEAKER HALF AND SAYS SO. A guard reading which NAME gates the element cannot see
     a `drawable` that has been redefined to something else, and the behavioural assertion — post a
     record the server refuses, require no `svg[role="img"]` and a conflict panel in its place — is
     `e2e/walk.mjs`'s, because it needs a live server answering the contract. */
  const src = live('surfaces/PlanWorkbench.jsx');
  assert.match(src, /const drawable = [^;]*\bmayDraw\(placement, \{ allowSketch: true \}\)/,
    'drawable must be the leaf’s verdict, with the bench asking for the wall drag’s sketch by name');
  assert.match(src, /\{drawable && \(/, 'and the plate must render under it');
  assert.doesNotMatch(src, /\{placement && \(\s*\n\s*<div[^\n]*maxWidth: 1120/,
    'the plate must not be gated on a placement merely existing');
  assert.match(src, /<ConflictSet /, 'and the conflict set must stand where the plate would be');
});

test('no surface reads the key that means a MISSING LIBRARY as a refused house', () => {
  /* `workbench/server/app.py` maps a body carrying `refusal` to 501 Not Implemented — "this
     server has no ezdxf". The contract names the placement verdict `refused_placement` /
     `placement_refused` for exactly that reason, and `isMissingLibrary` is the separate reader.
     A surface testing `detail.refusal` by hand would show a conflict set with no conflicts in it
     on a machine that simply lacks a CAD library. */
  const app = readFileSync(resolve(HERE, '../../server/app.py'), 'utf8');
  assert.match(app, /res\.get\("refusal"\)/, 'the 501 branch this guard is about must still exist');
  for (const [rel] of READERS) {
    assert.doesNotMatch(live(rel), /detail[?.\s]*\.\s*refusal\b/,
      `${rel} must read a missing library through isMissingLibrary, never by hand`);
  }
});

test('the Drawing Set reads engineClaim rather than re-spelling the engine test', () => {
  /* WP-13.4 found the third spelling WP-13.2 did not: this plate decided "proof (CP-SAT)" on the
     engine's NAME in a three-state ternary, so it printed a proof over a FEASIBLE truncation and
     over an `OPTIMAL (hard-only)` whose objective never ran — the same claim the bench and the
     Python plate had both stopped making at WP-13.2. It is the leaf's verdict now. */
  const src = live('surfaces/DrawingSet.jsx');
  assert.match(src, /import \{[^}]*\bengineClaim\b[^}]*\} from '\.\.\/sheet\/engineClaim\.js'/,
    'DrawingSet.jsx must import engineClaim');
  assert.match(src, /engineClaim\(/, 'and call it');
  assert.doesNotMatch(src, /solver\.engine\s*===/,
    'a second spelling of the engine test is how a FEASIBLE truncation came to be captioned proved');
  assert.match(src, /not proved at the optimum/i,
    'and the plate must be able to print the state the name-test could not express');
});

test('both export controls go through api/client.js and are blocked on a refusal', () => {
  const src = live('surfaces/ExportDetails.jsx');
  assert.match(src, /api\.drawing\(/, 'the SVG save must use the client wrapper');
  assert.match(src, /api\.exportCad\(/, 'and so must the CAD save');
  assert.doesNotMatch(src, /\bfetch\(/,
    'a raw fetch here is how a 422 was swallowed with no else-branch at all');
  /* BOTH SAVERS, SEPARATELY, AND THE FIRST VERSION OF THIS ASSERTION WAS BLIND FOR THE REASON
     CLAUDE.md already records: it matched the guard ONCE anywhere in the file, so deleting it
     from `saveSvg` left it green on `saveCad`'s copy. A mutation found it; re-reading would not
     have. Each function's own head is read now. */
  for (const fn of ['saveSvg', 'saveCad']) {
    const head = new RegExp(`async function ${fn}\\([^)]*\\) \\{\\s*if \\(!plan \\|\\| blocked\\) return;`);
    assert.match(src, head,
      `${fn} must refuse to run while the bench holds a refused placement or a working sketch`);
  }
  assert.match(live('api/client.js'), /exportCad:/,
    'api/client.js must expose the export route it was given');
});
