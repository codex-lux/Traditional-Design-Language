# oq/the-elevation-measures-a-front-the-drawn-layer-refuses-to-judge — one front, two answers

*Status: OPEN · Raised in: WP-15.8, the audit of Phase 15 (28 September 2026)*

**OPEN — `plan_check`'s drawn layer refuses to judge symmetry and alignment on a front the record
does not describe, and the elevation measures both on that same front and hands the figures to two
fatal faults.** Auditor A found this in WP-15.8's audit, and it is older than Phase 15.

- **The refusal (WP-11.3).** The drawn layer judges the mirror and the storey alignment only on a
  complete front: *"A facade missing seven of its eleven declared units is not the facade the
  record describes, and convicting it of asymmetry would charge the house twice for one cause."*
- **The measurement.** `build/elevation.py` reads `axis.mirror` and `storey_alignment` on every
  front and publishes five figures:
  - the mirror count and the largest asymmetric element, which `one-bay-symmetry-break` tests;
  - the storey-over-storey trio, which `storeys-out-of-vertical-alignment` tests, and whose
    missing-or-off count `closet-on-the-exterior-wall` also reads.

So one house carries both answers. On `tidewater-georgian-careful`, placed on the heuristic, the
drawn layer says *"Facade symmetry could not be judged: 4 declared window unit(s) on the entrance
front were not drawn"*. Beside it, *"The Bay That Broke the Symmetry: 3 against at-most 0"* and
*"Windows That Do Not Stand On Each Other: 90.0 against at-most 2.0"*, both fatal. The spec
Colonial is the same with 2 units undrawn.

**It cuts the other way too: a refused window can clear the fatal by vanishing.** The composer's `living-hall-picturesque`, composed for `family-georgian`, was measured on both
trees:

- **Before WP-15.6 (`e8668e6`)** its front read not-mirrored: one opening unmatched and one
  declared unit undrawn. `one-bay-symmetry-break` fired.
- **WP-15.6's doorcase reservation then refused the porch's south window**, *"the wall has no
  clear run left beside its doors and the chimney stack and the entrance doorcase"*.
- **At `2467585`** the same front reads mirrored: none unmatched and two undrawn. The one
  unmatched opening was the window that vanished, and the fatal clears.

The set the composer returns changed with it. `centre-passage-double-pile` was in it on
`e8668e6` and is not at `2467585`; `living-hall-picturesque` is. Auditor A found this, and both
halves were reproduced before anything was written here.

**The fix that was planned, measured before it was applied, and why it was not applied.** One
reader, `axis.front_complete(mirror)`, was to decide for both layers, and the elevation was to
withhold the five figures, with the reason, wherever it answered no. Measured at `2467585` against
a clean worktree, over the sixteen shipped plans placed on `engine="heuristic"`, the declared
records, and the composer's `family-georgian` set with the repair budget lifted:

| | the plans that move | the composer's returned set |
|---|---|---|
| before | — | side-hall-townhouse, living-hall-picturesque, courtyard-and-portal, ranch-tripartite |
| the fix as planned | 6 of 16: the two shipped plans, `bad-03`, `bad-05`, `good-02`, `good-05` | side-hall-townhouse, **centre-passage-double-pile**, five-part-palladian, tower-villa |
| narrowed to where the drawn layer refuses | 2 of 16: the two shipped plans | **centre-passage-double-pile**, side-hall-townhouse, living-hall-picturesque, courtyard-and-portal |

The gate set before the measurement was: apply only if the symmetry and alignment faults alone
move, and only on fronts the drawn layer already calls incomplete. **Neither reading passes it, for
three reasons.**

1. **It acquits.** Withholding the offset and the matching count leaves
   `storeys-out-of-vertical-alignment` one test to run, `bay_count_on_the_principal_front
   at-least 3`. That test passes, so the fault goes from PRESENT to **CLEAR**, not to unjudged:
   on four plans under the planned fix and two under the narrow one. The cause is `core`'s own
   rule, that a fault is clear when every test that ran passed, whatever did not run.
   `oq/a-fault-reads-clear-when-its-governing-test-could-not-run` measures it across the corpus
   and asks for the ruling that must come first. `one-bay-symmetry-break` and
   `closet-on-the-exterior-wall` do go to unjudged, because all of their tests read withheld
   figures.
2. **The planned fix reaches fronts the drawn layer never judges.** The drawn layer's whole axis
   block runs only where the diagram wants a centre bay (`geometry.wants_a_centre_bay`). On
   `bad-03`, `bad-05`, `good-02` and `good-05` the front is also incomplete (1, 1, 3 and 2 declared
   units undrawn), and the drawn layer says nothing about symmetry there at all. Their fatal faults
   would be withheld on a rule the drawn layer does not apply to them. That is a new policy, not
   the removal of a contradiction.
3. **It reorders the composer through the verdicts that became unjudged.** Under both readings the
   native diagram, `centre-passage-double-pile`, comes back into the set: first under the narrow
   reading, second under the planned one. It gets there by losing two of its three fatal findings.
   One, the symmetry fault, becomes unjudged, and `compose._sort_key` reads an unjudged fatal as
   none. The other, the alignment fault, becomes a false clear. The house it returns is the one a
   Tidewater Georgian brief should get, and it is returned for the wrong reason.

**What must be ruled:**

- **Whether an incomplete front is judged for symmetry and alignment at all, everywhere,** or only
  where the diagram wants a centre bay, as the drawn layer does now. The refusal's own reason,
  charging the house twice for one cause, is not about the diagram.
- **What the fault corpus says on a front nobody can judge.** It must say unjudged, never clear,
  and that waits on the other question.
- **What an unjudged fatal costs a candidate.** It costs nothing today. That is
  `oq/the-composer-ranks-first-a-house-that-may-not-be-drawn`'s family, and deciding it inside
  this fix would decide which house a person is offered.

The measurement is reproducible from the three probes in WP-15.8's report. The contradiction
stands on the shipped plans until this is ruled, and each of its two answers is stated where it
is made.

## Corrected 28 September 2026 (the audit of WP-15.8's own diff)

Two sentences above are wrong, and both are left as written:

- **"The spec Colonial is the same with 2 units undrawn."** It carries the same contradiction, but
  not with the same severity. Its drawn layer says symmetry could not be judged, with 2 declared
  units undrawn. Beside that, *"Windows That Do Not Stand On Each Other: 178.8 against at-most
  2.0"* is fatal, and *"The Bay That Broke the Symmetry: 2 against at-most 0"* is **serious**, not
  fatal. Re-read off `plan_check.check` on the heuristic placement.
- **"The measurement is reproducible from the three probes in WP-15.8's report."** The report
  names no such probes. The measurement was taken with scratch scripts, and they are not in the
  tree. Only the fault-clear half can be re-derived from anything committed, with
  `tests/fault_clears.py`. The plan table and the composer's set must be measured again by
  applying the planned fix in a `git worktree`.
