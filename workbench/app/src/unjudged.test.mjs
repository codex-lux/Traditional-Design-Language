// The bench's reason for a fault it could not judge (faults/unjudged.js, WP-16.1). Each clause
// is driven with the row shape `mcp_server/core.py` and `build/plan_check.py` actually serve.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { unjudgedReason, STATE_WORD } from './faults/unjudged.js';

test('a row that names only its missing measurements says so', () => {
  assert.equal(unjudgedReason({ needs: ['a_in', 'b_in'] }), 'needs a_in, b_in');
  assert.equal(unjudgedReason({ needs: [] }), 'no test of this fault could be evaluated');
});

test('an errored test is said as an error and never as a missing number', () => {
  assert.equal(unjudgedReason({ needs: ['a_in'], errors: ['float division by zero'] }),
    'a test errored: float division by zero');
});

test('an exception judged both ways says both verdicts in the bench words', () => {
  const s = unjudgedReason({ exception_unjudged: {
    style: 'cape-dutch', because: 'the wall is not stated',
    under_the_exception: 'clear', under_the_general_rule: 'present' } });
  assert.match(s, /cape-dutch exception could not be judged \(the wall is not stated\)/);
  assert.match(s, /under its own test the fault is clear where under the general rule it is present/);
  assert.equal(STATE_WORD.needed, 'could not be judged');
});

test('R4: a governing test that could not run names what it wanted and keeps the rest as evidence', () => {
  const row = { needs: ['brick_stretcher_length_in'],
    governing_not_run: { expression: 'jamb_reveal_depth_in / brick_stretcher_length_in',
                         missing: ['brick_stretcher_length_in'] },
    ran: [{ expression: 'reveal_depth_in', passes: true }] };
  assert.equal(unjudgedReason(row),
    'its governing test could not run (needs brick_stretcher_length_in); the 1 that ran are ' +
    'evidence, not a verdict');
  // without a test that ran, it is the historical case, not an evidence row
  assert.equal(unjudgedReason({ ...row, ran: [] }), 'needs brick_stretcher_length_in');
});

test('R12: a figure withheld on this house carries the elevation reason, once, whichever clause applies', () => {
  const why = '4 declared window unit(s) on the S front were not drawn (4 on the ground storey), ' +
    'so the drawn front is not the one the record describes';
  const held = [
    { name: 'count_of_openings_without_a_mirror_twin_about_the_facade_centreline',
      by: 'elevation.front.withheld', why },
    { name: 'width_of_the_largest_asymmetric_element_in', by: 'elevation.front.withheld', why }];
  const plain = unjudgedReason({ needs: held.map((w) => w.name), withheld: held });
  assert.ok(plain.endsWith('; withheld on this house: ' + why), plain);
  assert.equal(plain.split(why).length, 2, 'one reason shared by two figures is said once');
  const gov = unjudgedReason({ needs: ['max_abs_offset_between_upper_and_lower_opening_centrelines_in'],
    governing_not_run: { missing: ['max_abs_offset_between_upper_and_lower_opening_centrelines_in'] },
    ran: [{ expression: 'bay_count_on_the_principal_front', passes: true }],
    withheld: [{ name: 'max_abs_offset_between_upper_and_lower_opening_centrelines_in', why }] });
  assert.match(gov, /^its governing test could not run/);
  assert.ok(gov.endsWith('; withheld on this house: ' + why), gov);
  // a row with nothing withheld carries no such clause
  assert.doesNotMatch(unjudgedReason({ needs: ['a_in'], withheld: [] }), /withheld/);
});
