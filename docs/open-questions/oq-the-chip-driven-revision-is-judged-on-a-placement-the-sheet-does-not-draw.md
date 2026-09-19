# oq/the-chip-driven-revision-is-judged-on-a-placement-the-sheet-does-not-draw — the job route strips its record and the bench re-solves it, so the panel's key and the plate are two houses

*Status: OPEN · Raised in: WP-13.9 (19 Sep 2026)*

**The finding.** WP-13.9 made the bench's SOLVE path run its corrective rounds inline and draw
the record the loop ended on, so the sheet, the findings and the panel's key are one building
(WP-6.4's rule). **The two CHIP paths still work the old way**: `POST /api/plan/revise` runs the
loop as a job, `jobs.revised_plan` returns the record with its placement stripped
(`openings.strip_placement`), the bench loads it, and the 400 ms debounce solves it again from
scratch. The panel then says so in as many words — *"The sheet above is a fresh solve of the
revised record; the loop's own key was measured on the proved placement, and the two can
differ"* — which is honest and is not the same as being right.

**What it looked like on the screen that raised WP-13.9.** Sixty drawn findings tagged *on the
searched placement*, every one of them a property of a hill-climb placement `typefacts` had
refused, beside `Key unchanged (on the proved placement, 25.1 s)` from a job that had solved the
same record separately and got a proof. Both statements were true. Neither could be checked
against the other, because the loop's report carries no list of the findings IT saw — only
counts by class — so the 135 handed to the architect cannot be matched to the rows on the left.

**Why it was not fixed with the solve path.** Three reasons, and the third is the one that
matters. The job's record is stripped for a real purpose: a placement travels on `placement`,
and two copies of one placement in one response is how two readers of one house come to
disagree. The job may outlive the record it was submitted against — the bench already refuses to
apply a revision when `planDoc.get() !== submitted` — so a placement carried back from a job is
a claim about a document that may no longer exist. And changing what a job returns is a second
surface's contract, on a package that had already changed one.

**The question.** Should `GET /api/jobs/{id}/plan` (or a sibling) return the loop's own
placement summary beside the stripped record, so the bench can draw the house the key was
measured on instead of re-solving? And if so, what does the bench draw when the record HAS
changed underneath — the divergence is real in that case, and a stale plate would be worse than
a re-solve.

**Three things that must not be done to close it.** Do not make the chips run inline: they exist
because 6 rounds at 60 s and 4 rounds at 120 s are a job, not a wait. Do not carry the placement
back and draw it without re-checking the submitted-record identity. And do not delete the "the
two can differ" sentence while the two can still differ — it is the only thing standing between
a reader and a silent disagreement.

**What is already true.** `revise()` takes `surfaced` and the panel reads it, so the two paths
already print different sentences and a third state would cost one string rather than a design.
