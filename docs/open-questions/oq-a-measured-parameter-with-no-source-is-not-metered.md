# oq/a-measured-parameter-with-no-source-is-not-metered — 542 kit figures claim to have been measured and nothing on the record says where

*Status: HALF CLOSED 5 Sep 2026 — part 2 ruled, part 1 still open · Raised in: WP-11.1, the precedent bench (4 Sep 2026)*

**PART 2 RULED 5 SEP 2026 BY LUCAS: YES -- REFUSE A NEW `measured` PARAMETER THAT CARRIES NO SOURCE.**
Part 3 is answered by `oq/a-surveyors-prose-may-source-an-envelope-figure`, ruled the same day.
**PART 1 IS NOT RULED AND NOTHING IS RE-KINDED**: the existing 542 keep their label and the meter
stays the honest interim, exactly as this entry proposes.

**THE GATE HALF-EXISTED AND ITS HOLE IS THIS REPOSITORY'S FAVOURITE SHAPE.**
`check_research.RATCHET["measured_unsourced"]` is a CEILING at 542 and the comparison is
`got[key] > pin`, so adding a new unsourced `measured` parameter already reddens the build at 543.
Nobody had said so. But it is a **net count**: source one figure and add an unsourced one in the same
commit and the total is still 542 and the build stays green -- a counter that nets out, which is the
family this corpus keeps meeting. So the ruling is a real package and not a no-op, and the gate must
be **per-parameter** rather than arithmetic: `check_kits.py` refuses a `measured` parameter with no
source unless its `(node, slot, parameter)` triple is in a FROZEN grandfathered set built once from
today's 542. Adding one is then refused by identity; removing one from the set is a one-way door.

**And the message matters as much as the gate.** The current failure reads `measured_unsourced: 542
-> 543`, which tells an author neither which parameter nor what to do. It must name the node, the
slot and the parameter, and state the two legitimate remedies: cite a
`precedents/<id>#measurements[<n>]`, or mark it `editorial` with a note saying what it rests on.


**OPEN — the provenance census counted the other kind for a year.** `build/check_kits.py::provenance_census`
prints `editorial with NEITHER a source NOR a note` on every run and pins it at 0 (`tests/test_provenance.py`).
It never counted `measured` with no source. The kit schema's own words for `measured` are *"from surviving
fabric or a documented standard"*, and measured on 4 Sep 2026: **672 of 1,161 `measured` parameters carry no
`source` on the parameter, and 542 sit on a slot with no `sources[]` either.** `tidewater-georgian`, the
flagship, is 31 of 31. By slot, the unsourced ones lead exactly where the generators read: `height_proportion`
34, `chimney` 24, `ceiling_height_rule` 24, `window_proportion` 21, `belt_course` 13 — **272 of the 542 are on
one of the 35 slots the generators or the critic read**, an upper bound derived from the generators' own
string constants by `build/check_research.py`.

VISION.md §VII: *laundering a guess as a measurement is the worst thing that can be done to this corpus,
because it is undetectable later.* It was undetectable. The numbers are probably defensible — the node
cites five books and the slot carries a `rule` and a `note` — but nothing says WHICH book gives 7:12, so a
reader cannot check, and a parameter that cannot be checked is not measured in the sense the schema means.

**What is built (WP-11.1).** The census prints `measured-bare` and `measured-bare-slot` beside
`editorial-bare`; `check_research.py` ratchets 542 and 272 as ceilings that may only fall and splits them by
node and by read slot; `check_precedents.py` resolves a kit `source` of the form
`precedents/<id>#survey.<field>` so a figure can cite a survey quote that exists. Nothing is re-kinded and
nothing is sourced by this package.

**What wants ruling, in three parts.**
1. Is a `measured` parameter with no source to be re-kinded? Bulk re-kinding to `editorial` destroys the
   claim that it was measured (and moves `test_provenance.py`'s 202); leaving it lets the label mean two
   things. The honest interim is the meter: labelled, counted, falling only when somebody sources one.
2. Should a NEW `measured` parameter be refused without a `source`? That is the rule the schema already
   implies and nothing enforces. It would be `check_kits.py`'s to enforce and would bite only authors.
3. Which sources count — see `oq/a-surveyors-prose-may-source-an-envelope-figure`. OQ 18's ruling that none
   of the 162 editorial figures may be sourced from a secondary work or a modern redrawing was written for
   the orders; a roof pitch a HABS surveyor recorded is a different class of claim.

**The trap.** A source pointer that resolves is not a source that agrees. `check_precedents.py` verifies
that the quoted field exists; it cannot verify that the quote states the figure the parameter claims. That
comparison is a reader's, and the first tranche's D6 table (`docs/reports/wp-11.1-the-bench-without-a-literature.md`)
is where it is done by hand, with every disagreement listed and none reconciled.
