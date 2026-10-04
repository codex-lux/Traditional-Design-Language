/* WHY A COULD-NOT-EVALUATE FAULT COULD NOT BE EVALUATED (lifted from the Plan Workbench at WP-16.1
   so each clause can be driven under `node --test`; the surface imports React and cannot be).

   Several shapes reach the bench's unjudged list, and only one of them is "a number is missing":

     needs[]              -- the historical case: name the measurements.
     errors[]             -- a test raised; say so, never render it as a missing number.
     exception_unjudged   -- WP-8.4: this style carries an exception whose own bounds_test would
                             REPLACE the fault's primary test, and whose condition could not be
                             resolved, so the two rules disagree about this house and nobody can
                             say which governs. The bench used to render the bare word "needs"
                             for it -- an unjudged whose reason is on the record and not on the
                             screen, which reads to the user exactly like a bug in the bench.
     governing_not_run    -- WP-16.1 (R4, ruled 29 Sep 2026): the fault's GOVERNING test could
                             not run while others did. It read clear on those others until then;
                             they ride on the row as `ran`, evidence and never a verdict, and the
                             reason names what the governing test wanted.
     withheld[]           -- WP-16.1 (R12): a figure the elevation declined to measure on THIS
                             house -- the symmetry and alignment figures of a front whose declared
                             windows were not all drawn -- with the elevation's own reason. Said
                             beside whichever clause above applies, or the reader is handed a
                             work item for a figure that was withheld on purpose.

   Pure; imports nothing. */

export const STATE_WORD = Object.freeze({
  needed: 'could not be judged', present: 'present', clear: 'clear',
  not_applicable: 'not applicable',
});

export function unjudgedReason(u) {
  const x = u.exception_unjudged
  if (x) {
    const said = (v) => STATE_WORD[v] || v || '?'
    return 'the ' + (x.style || 'style') + ' exception could not be judged (' +
      (x.because || 'no reason given') + '), and under its own test the fault is ' +
      said(x.under_the_exception) + ' where under the general rule it is ' +
      said(x.under_the_general_rule)
  }
  if (u.errors && u.errors.length) return 'a test errored: ' + u.errors.join('; ')
  const held = [...new Set((u.withheld || []).map((w) => w && w.why).filter(Boolean))]
  const because = held.length ? '; withheld on this house: ' + held.join('; ') : ''
  const g = u.governing_not_run
  if (g && (u.ran || []).length) {
    const want = (g.missing || []).join(', ')
    return 'its governing test could not run' + (want ? ' (needs ' + want + ')' : '') +
      '; the ' + u.ran.length + ' that ran are evidence, not a verdict' + because
  }
  const n = u.needs || []
  return (n.length ? 'needs ' + n.join(', ') : 'no test of this fault could be evaluated') + because
}
