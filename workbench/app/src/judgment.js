/* THE THREE STATES OF A JUDGMENT, IN ONE PLACE (WP-14.6).

   This corpus's first rule is that UNJUDGED IS NOT PASSED, and its sharpest corollary is that
   unjudged is not FAILED either: a checker that could not evaluate has said nothing about the
   house, and a mark that reads as a fail convicts it of something nobody measured. The
   Proportions surface drew every invariant as `holds ? 'pass' : 'fail'` (`Proportions.jsx:530` at
   the time this was written), so an invariant whose evaluation crashed — `holds: null`, which the
   engine writes for exactly that case — would have been drawn as a broken invariant. None is null
   today; the mapping was wrong before any record could show it, which is the only time a
   three-state rule is cheap to get right.

   `judgmentOf(holds)` is the one reading. It is STRICT in both directions: only the boolean `true`
   is a pass and only the boolean `false` is a fail. `null` and `undefined` are unjudged by the
   contract, and so is anything else a payload might carry in that field — `1`, `'true'`, `NaN`,
   an object — because a value that is not a verdict is not a verdict, and truthiness would turn
   each of them into one. The term id of a judgment is `'judgment-' + state`, and those records are
   the glossary's (`judgment-passed`, `judgment-failed`, `judgment-unjudged`); this file writes no
   word a reader sees.

   `constraintStateOf(c)` answers the same question for a style's constraint, which has its own
   three states and is not the same three: a constraint with a `test` is EXECUTABLE (whether it
   passes is a separate verdict about a house); one with `scope: judgment` is YOURS TO JUDGE, the
   corpus's own statement that the sources do not determine it; and one with neither has NO TEST
   YET — the state `schema/constraint.schema.json` permits and no record takes today. It is named
   so that the day a record lands in it, it is not drawn as executable.

   Pure, and imports nothing. */

export const JUDGMENT_STATES = Object.freeze(['passed', 'failed', 'unjudged']);

/* `holds` → the judgment it records. Never two states. */
export function judgmentOf(holds) {
  if (holds === true) return 'passed';
  if (holds === false) return 'failed';
  return 'unjudged';
}

/* The `state` prop `components/JudgmentMark.jsx` distinguishes, for each judgment. */
export const JUDGMENT_MARK = Object.freeze({ passed: 'pass', failed: 'fail', unjudged: 'unjudged' });

/* The glossary record naming a judgment state. */
export function judgmentTermId(state) {
  return 'judgment-' + state;
}

export const CONSTRAINT_STATES = Object.freeze([
  'constraint-executable', 'judgment-yours-to-judge', 'constraint-no-test-yet',
]);

/* A constraint record → the glossary id of its state. A `test` decides first: a record carrying
   one is executable whatever its scope says. */
export function constraintStateOf(c) {
  const rec = c && typeof c === 'object' ? c : {};
  if (rec.test !== undefined && rec.test !== null) return 'constraint-executable';
  if (rec.scope === 'judgment') return 'judgment-yours-to-judge';
  return 'constraint-no-test-yet';
}

/* A style-layer finding the plan check could not settle → the `JudgmentMark` state it is drawn
   with, or null for any other finding (WP-14.29). The Plan Workbench drew both kinds with the
   could-not-evaluate hatch, which said a rule had failed to run about a rule the corpus hands to
   the reader on purpose. `build/plan_check.py` says which by the finding's `kind`:
   `constraint-unjudged` is a test that could not be evaluated for want of a figure, and
   `constraint-unformalised` is a hard constraint with no test -- which
   `build/check_constraints.py` admits only as `scope: judgment`, the sources declining to settle
   it -- so it is yours to judge. A finding reaching this without a `kind` is read by the two
   statements `plan_check` writes for them, and anything else is not one of these rows. */
export function styleFindingMark(f) {
  const rec = f && typeof f === 'object' ? f : {};
  if (rec.layer !== undefined && rec.layer !== 'style') return null;
  if (rec.kind === 'constraint-unjudged') return 'unjudged';
  if (rec.kind === 'constraint-unformalised') return 'yours-to-judge';
  if (rec.kind !== undefined && rec.kind !== null) return null;
  const s = typeof rec.statement === 'string' ? rec.statement : '';
  if (/^cannot evaluate\b/i.test(s)) return 'unjudged';
  if (/^check by hand\b/i.test(s)) return 'yours-to-judge';
  return null;
}
