# oq/a-refused-candidates-record-is-served-for-diagnosis-and-the-candidate-set-will-not-load-it — two WP-13.4 statements about one record disagree, and a reader who picks a refused candidate is told which one won

*Status: OPEN · Raised in: the adversarial audit of the candidate-click change (16 October 2026)*

**OPEN — the route that serves a composed candidate's record and the surface that loads one say
opposite things about a refused record, both in WP-13.4's words, and nothing rules between them.**

- `workbench/server/app.py`, the docstring of `job_candidate_plan` (`GET /api/jobs/{id}/candidates/{n}/plan`):
  the record is *"NOT refused here and that is deliberate ... a refused record is exactly what a
  reader diagnosing a refusal needs to open -- the conflict set is ABOUT this placement."*
- `workbench/app/src/surfaces/CandidateSet.jsx`, `openInWorkbench`: *"A refused candidate is not
  loaded. ... loading it would put a record on the bench that no surface there may draw, which
  reads as the bench being broken rather than as the candidate being refused."*

The route was built so that a refused record could be opened; the surface was built so that it
never is. Today the surface wins, and a reader who picks a refused candidate is told it cannot be
drawn and why (the strip, the column's counts line and foot, the conflict set below the columns),
and is offered no way to put it on the bench.

## What is known

- The conflict set is drawn on the Candidate Set itself, from the candidate's own `refused`, in the
  same component the bench and the Drawing Set use (`ConflictSet`). A reader can read WHY without
  opening the record.
- What opening would add is the bench's own account: the placement drawn as the heuristic's
  labelled relaxation, the findings, the stacks and strips located on a plate. The bench shows a
  refused record as a refusal and a status line (WP-13.4), never as a sheet, so the addition is
  the locations and the findings, not a drawing.
- `build/compose.py` flags `refused` only on a candidate the placed revision loop reached. A
  candidate it did not reach (`revision_skipped`, or a compose with the loop off) carries no
  verdict at all, is OPENABLE by this surface, and may be refused on the bench. That is a third
  reader's road to the same screen, and it is the strip's `not judged for drawing` state
  (`candidateStanding.js`), not this question.

## What is not known

- Whether a reader diagnosing a refusal is better served by a refused candidate on the bench or by
  the conflict set where it already is. The two statements are both WP-13.4's, and the only
  reader whose account of it exists is the one this change was written for, who picked a
  candidate and found the plan refused. (Their report is paraphrased here and is not a ruling.)
- Whether the answer differs for a candidate refused as `infeasible` (the prover showed the
  declared facts cannot all hold) and one refused as `type-fact-downgraded`.

## What a ruling would choose between

1. **Keep it as it is**: a refused candidate is never loaded; correct the route's docstring to say
   the record is served for a client that already knows what it will do with it. Cheapest.
2. **Load it, to be read**: the bench opens it as a refusal (it already knows how), the strip says
   so, and Next stays blocked because the Plan step is refused. The route's docstring is then true
   and the surface's comment is not.
3. **A reading mode of its own**: the candidate opens in the Candidate Set's conflict panel with
   the located strips and stacks drawn, never on the bench's sheet. The most work, and the only
   one that keeps "the bench never holds a record it may not draw".

## Not done

Nothing about it. The strip's wording, the tally and the refused column line are the surface saying
the current rule out loud; they do not take a side. See also
`oq/the-composer-ranks-first-a-house-that-may-not-be-drawn`, whose ruling decides how often a
reader meets this: on one measured run of `family-georgian` no candidate could be drawn at all.
