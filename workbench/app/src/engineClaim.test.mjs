/* `sheet/engineClaim.js` -- what the bench may claim about the engine that drew a sheet (WP-13.2).

   Every branch is driven by a HAND-BUILT solver record, because the shipped plans reach only
   whichever status the machine and the day allow (the Tidewater plan has come back OPTIMAL,
   `OPTIMAL (hard-only)`, FEASIBLE and a heuristic fallback on different days of this project), so
   a test over the corpus would guard whichever branch the run happened to take. The expected
   verdicts are written by hand from the contract, not computed by the function under test.

   The two source guards at the end hold the callers: the Plan Workbench must READ this leaf
   rather than re-spelling `engine === 'cp-sat'`, and the walk must state its contract from the
   API's `status` rather than from the two phrase regexes that went stale. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { engineClaim, statusHead, PROVED_STATUS, VERDICTS } from './sheet/engineClaim.js';

const HERE = dirname(fileURLToPath(import.meta.url));

/* Comments may QUOTE the retired expression -- the JSX's own note does, because the quote is
   the finding -- so only live code is searched. The first run of the guard below fired on that
   note: a text selector that counts comments is the trap CLAUDE.md records for a call-site
   count that counted docstrings. Same stripper as test_grammar_agreement.py's, in JavaScript. */
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

// ---------------------------------------------------------------- the prover
test('OPTIMAL with an objective is a proof whose composition ran', () => {
  const c = engineClaim({ engine: 'cp-sat', status: 'OPTIMAL — kept polish from the heuristic hint (best of 3 hard-valid placements)', objective: 407.8 });
  assert.equal(c.verdict, 'proved');
  assert.equal(c.proved, true);
  assert.equal(c.objectiveRan, true);
  assert.equal(c.cp, true);
  assert.equal(c.fellBack, false);
});

test('OPTIMAL (hard-only) proves the hard set, evaluates no composition, and is NOT captioned proved', () => {
  // the status the bench draws at its 25 s budget when phase B never starts. The first version
  // of this test expected `proved: true` here -- the status alone -- while the Python plate
  // (`disclosures.py::engine_line`) and the gate's title-block row print NOT PROVED AT THE
  // OPTIMUM for the same record; the leaf takes the plate's rule (WP-13.2, the lead's pass).
  const c = engineClaim({ engine: 'cp-sat', status: 'OPTIMAL (hard-only) — kept hard-only phase A (best of 1 hard-valid placements)', objective: null });
  assert.equal(c.verdict, 'not-proved');
  assert.equal(c.proved, false, 'an optimum of NO objective is not a proof at the optimum');
  assert.equal(c.objectiveRan, false, 'objective null on a CP-SAT record is "did not run"');
  assert.equal(c.cp, true, 'it is still the prover, and the caption names it');
  // and a MISSING key counts the same way as a null -- a record from a solver that never
  // wrote the field must not read as an objective that ran
  const missing = engineClaim({ engine: 'cp-sat', status: 'OPTIMAL (hard-only) — kept hard-only phase A' });
  assert.equal(missing.objectiveRan, false, 'a missing objective key is "did not run"');
  assert.equal(missing.proved, false);
  // the two halves are independent: OPTIMAL with the objective is proved, FEASIBLE with the
  // objective is not, so neither half alone decides it
  assert.equal(engineClaim({ engine: 'cp-sat', status: 'OPTIMAL', objective: 0 }).proved, true,
    'an objective of ZERO ran -- only null and undefined are "did not run"');
  assert.equal(engineClaim({ engine: 'cp-sat', status: 'FEASIBLE', objective: 12.5 }).proved, false);
});

test('a proof over set-aside walls says how many, and a search never counts any', () => {
  // WP-11.1: "PLACEMENT PROVED" over sixteen released wall pins was the first false
  // certification; the leaf carries the count so the sheet's plate note can print it beside
  // the word "proved", as the Python plate does.
  const c = engineClaim({ engine: 'cp-sat', status: 'OPTIMAL', objective: 407.8,
    downgraded_wall_pins: ['L0 drawing W', 'L0 dining W', 'L0 backhall N'] });
  assert.equal(c.proved, true);
  assert.equal(c.wallsSetAside, 3);
  assert.equal(engineClaim({ engine: 'cp-sat', status: 'OPTIMAL', objective: 1 }).wallsSetAside, 0);
  assert.equal(engineClaim({ engine: 'cp-sat', status: 'OPTIMAL', objective: 1, downgraded_wall_pins: 'L0 x W' }).wallsSetAside, 0,
    'a malformed field is read as none rather than as its string length');
  assert.equal(engineClaim({ engine: 'heuristic', reason: 'requested', downgraded_wall_pins: ['x'] }).wallsSetAside, 0,
    'a hill-climb record carries no pins to set aside');
  assert.equal(engineClaim(null).wallsSetAside, 0);
});

test('FEASIBLE is a placement found and NOT a proof -- the false certification', () => {
  // the status the gate measured on the reference plan at the 40 s batch budget
  const c = engineClaim({ engine: 'cp-sat', status: 'FEASIBLE — kept polish from the heuristic hint (best of 2 hard-valid placements)', objective: 541.2 });
  assert.equal(c.verdict, 'not-proved');
  assert.equal(c.proved, false);
  assert.equal(c.cp, true, 'it is still the prover that drew it, and the caption names it');
  assert.equal(c.objectiveRan, true, 'FEASIBLE from the polish phase carries an objective');
});

test('a CP-SAT record with no status is not a proof: unjudged is not passed', () => {
  for (const status of [undefined, null, '', 42]) {
    const c = engineClaim({ engine: 'cp-sat', status, objective: 1 });
    assert.equal(c.proved, false, `status ${String(status)} must not read as proved`);
    assert.equal(c.verdict, 'not-proved');
    assert.equal(c.status, null);
  }
});

test('the discriminator is the WORD at the head of the status, not a substring', () => {
  assert.equal(PROVED_STATUS.test('OPTIMAL'), true);
  assert.equal(PROVED_STATUS.test('OPTIMAL (hard-only) — kept hard-only phase A'), true);
  assert.equal(PROVED_STATUS.test('FEASIBLE — kept polish'), false);
  assert.equal(PROVED_STATUS.test('not OPTIMAL'), false, 'must be anchored at the start');
  assert.equal(PROVED_STATUS.test('OPTIMALITY unknown'), false, 'must be the whole word');
  assert.equal(PROVED_STATUS.test('UNKNOWN'), false);
});

// ---------------------------------------------------------------- the search
test('the hill-climb asked for by name is searched, and did not fall back', () => {
  const c = engineClaim({ engine: 'heuristic', reason: 'requested' });
  assert.equal(c.verdict, 'searched');
  assert.equal(c.proved, false);
  assert.equal(c.fellBack, false);
  assert.equal(c.objectiveRan, true, "the hill-climb's score is its objective");
});

test('auto falling back to the hill-climb is searched AND fell back, carrying the reason', () => {
  const reason = 'CP-SAT returned no solution in 25s (UNKNOWN); fell back to the hill-climb';
  const c = engineClaim({ engine: 'heuristic', fallback: 'budget', status: 'UNKNOWN', reason });
  assert.equal(c.verdict, 'searched');
  assert.equal(c.fellBack, true);
  assert.equal(c.reason, reason);
  assert.equal(c.proved, false, 'a heuristic record carrying a status word is still not a proof');
});

test('the least-bad relaxation after an INFEASIBLE proof is searched, never proved', () => {
  const c = engineClaim({ engine: 'heuristic (least-bad, labelled)',
    reason: 'CP-SAT proved the declared facts cannot all hold; this drawing is the heuristic\'s least-bad relaxation' });
  assert.equal(c.verdict, 'searched');
  assert.equal(c.proved, false);
  assert.equal(c.fellBack, true);
});

// ---------------------------------------------------------------- no record
test('no solver block at all is unjudged, not searched and not proved', () => {
  for (const s of [undefined, null, {}, { engine: '' }, 'cp-sat']) {
    const c = engineClaim(s);
    assert.equal(c.verdict, 'unjudged', `for ${JSON.stringify(s)}`);
    assert.equal(c.proved, false);
    assert.equal(c.engine, null);
  }
});

test('every verdict the function can return is in the published vocabulary', () => {
  const seen = new Set([
    engineClaim({ engine: 'cp-sat', status: 'OPTIMAL', objective: 1 }).verdict,
    engineClaim({ engine: 'cp-sat', status: 'FEASIBLE', objective: 1 }).verdict,
    engineClaim({ engine: 'heuristic', reason: 'requested' }).verdict,
    engineClaim(null).verdict,
  ]);
  assert.deepEqual([...seen].sort(), [...VERDICTS].sort());
});

// ---------------------------------------------------------------- the printed status
test('statusHead prints the solver word and drops the " — kept …" tail', () => {
  assert.equal(statusHead('OPTIMAL (hard-only) — kept hard-only phase A (best of 1 hard-valid placements)'), 'optimal (hard-only)');
  assert.equal(statusHead('FEASIBLE — kept polish from the heuristic hint'), 'feasible');
  assert.equal(statusHead('OPTIMAL'), 'optimal');
  assert.equal(statusHead(''), null);
  assert.equal(statusHead(undefined), null);
  assert.equal(statusHead(' — '), null, 'a status that is only a separator prints as none');
});

// ---------------------------------------------------------------- the plate's own rule
test('the leaf states the same proof rule as the Python plate, read from both sources', () => {
  // Three spellings of one verdict -- `build/disclosures.py::engine_line` (the printed plate),
  // this leaf (the bench) and the gate's title-block row -- and an audit of WP-13.2's slices
  // found the bench one saying "proved" on the status alone. Nothing imports across the
  // language boundary, so both sources are read: the Python must test the objective beside the
  // status word, and the leaf's `proved` must be gated on `objectiveRan`.
  const py = readFileSync(resolve(HERE, '../../../build/disclosures.py'), 'utf8');
  assert.match(py, /status\.upper\(\)\.startswith\("OPTIMAL"\) and s\.get\("objective"\) is not None/,
    'the Python plate must decide PROVED on the status word AND the objective');
  const js = stripComments(readFileSync(resolve(HERE, 'sheet/engineClaim.js'), 'utf8'));
  assert.match(js, /const proved = [^;]*PROVED_STATUS\.test\(status\)[^;]*&&[^;]*objectiveRan/,
    'the leaf must gate `proved` on `objectiveRan`, as the plate does');
  const gate = readFileSync(resolve(HERE, '../../../tests/test_sheet_coherence.py'), 'utf8');
  assert.match(gate, /startswith\("OPTIMAL"\) and sv\.get\("objective"\) is not None/,
    'the gate row must hold the same rule');
});

// ---------------------------------------------------------------- the callers
test('the Plan Workbench reads the leaf and does not re-spell the proof decision', () => {
  const raw = readFileSync(resolve(HERE, 'surfaces/PlanWorkbench.jsx'), 'utf8');
  const src = stripComments(raw);
  // the stripper is exercised, not assumed: the JSX's note quotes the retired line on purpose
  assert.match(raw, /engine\s*===\s*['"]cp-sat['"]/, 'the retired expression should still be QUOTED in a comment (the finding)');
  assert.match(src, /import \{[^}]*\bengineClaim\b[^}]*\} from '\.\.\/sheet\/engineClaim\.js'/,
    'PlanWorkbench.jsx must import engineClaim from sheet/engineClaim.js');
  assert.match(src, /engineClaim\(/, 'and call it');
  assert.doesNotMatch(src, /engine\s*===\s*['"]cp-sat['"]/,
    "a second spelling of `engine === 'cp-sat'` in live code is how the FEASIBLE truncation came to be captioned proved");
  // the caption carries its verdict for the walk to read against the API
  assert.match(src, /data-engine-claim=\{/, 'the caption paragraph must publish its verdict');
});

test("the sheet's own plate note reads the leaf and does not re-spell the proof decision", () => {
  const raw = readFileSync(resolve(HERE, 'sheet/Sheet.jsx'), 'utf8');
  const src = stripComments(raw);
  assert.match(src, /import \{[^}]*\bengineClaim\b[^}]*\} from '\.\/engineClaim\.js'/,
    'Sheet.jsx must import engineClaim from ./engineClaim.js');
  assert.match(src, /engineClaim\(/, 'and call it');
  assert.doesNotMatch(src, /engine\s*===\s*['"]cp-sat['"]/,
    "the plate note's own `engine === 'cp-sat'` is how a FEASIBLE truncation was captioned proved on the PLATE");
  assert.match(src, /data-plate-note/, 'the plate note element the walk reads must still be published');
  // and the four states the plate prints are all present in the live code, so a reader of
  // the sheet sees the same vocabulary as a reader of the Python plate
  for (const phrase of ['Placement proved (CP-SAT)', 'not proved at the optimum',
                        'compositional objective did not run', 'searched, not proved', 'set aside']) {
    assert.ok(src.includes(phrase), `the plate note must be able to print: ${phrase}`);
  }
});

test('the walk states its contract from the API status, not from the two retired phrases', () => {
  const src = readFileSync(resolve(HERE, '../e2e/walk.mjs'), 'utf8');
  assert.match(src, /mayClaimProof = cp && \/\^OPTIMAL\\b\/\.test\(status\) && objectiveRan/,
    'the walk may expect a proof only where the status is OPTIMAL AND the objective ran');
  assert.doesNotMatch(src, /was\\s\+proved,\\s\+not\\s\+searched/,
    'the retired "was proved, not searched" regex is back: it matched a phrase the caption stopped printing at WP-11.8');
  assert.doesNotMatch(src, /came from the\\s\+fast search/,
    'the retired "came from the fast search" regex is back');
  assert.match(src, /\^OPTIMAL\\b/, 'the walk must discriminate a proof on the status word, as the leaf does');
  assert.match(src, /solver\.objective/, 'and read whether the objective ran');
  assert.match(src, /data-engine-claim/, 'and read the caption\'s published verdict against the API');
});
