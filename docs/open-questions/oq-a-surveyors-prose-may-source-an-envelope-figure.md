# oq/a-surveyors-prose-may-source-an-envelope-figure — may a HABS written-data quote source a `measured` kit parameter?

*Status: OPEN · Raised in: WP-11.1, the precedent bench (4 Sep 2026)*

**OPEN — a ruling, not a mechanism.** The Historic American Buildings Survey's written historical and
descriptive data is reachable as text from this project's tiers (`oq/fetching-through-a-tier-the-proxy-denies`),
follows a fixed outline (Part II.B exterior: over-all dimensions, foundations, walls, structural system,
porches, chimneys, openings, roof; II.C interior: plan, stairways, finishes), and states, for Gunston Hall,
*"a rectangle of 40 feet 11-1/2 inches by 60 feet 10 inches, exterior foundation measurements … 33'-1" high
… walls about two feet thick … four tall chimney stacks, two at each end"*, and for Westover, *"hipped roof;
two chimneys each end; front seven bays; all sash 9-over-9 lights; five hipped dormers."* Those are the
figures `tidewater-georgian`'s kit states as `measured` with no source (`oq/a-measured-parameter-with-no-source-is-not-metered`),
stated by a surveyor, in text.

**What is already ruled, and what it was ruled about.** `docs/open-questions/018-kind-editorial-carrying-parameters.md`:
*"none of the 162 may be given a source from a secondary work or a modern redrawing."* CLAUDE.md, on the
`tile.loc.gov` route: *"This does NOT close OQ 7-11 or OQ 18's source half: those need legible FACSIMILES and
this is prose about the plates."* Both were written for the ORDERS — moulding profiles and entablature
parts, where the figure is on the plate and the prose is about it. A survey's `Over-all dimensions` is not
prose about a plate; it is the surveyor's own measurement, recorded in the survey's data sheet. And the
study's caution stands with it: HABS text is a POOR source for ROOM dimensions
(`wp-9.2-what-the-tradition-actually-does.md` §7 Q10); those live on the measured drawings.

**The question, precisely.** May a kit parameter of the ENVELOPE class — roof pitch, storeys, chimney
position and count, bay count, wall thickness, water table, sash lights, overall dimensions, dormer count —
carry `source: "precedents/<id>#survey.<field>"` and keep `kind: measured`, at `confidence: medium`, where
the quoted span states the figure? Three readings:

- **Yes, for the envelope class, quote-checked.** The parameter cites the record; the record quotes the
  survey verbatim with the page; a reader can hold the two together. The kit pointer convention exists
  (`check_precedents.py` resolves it) and this reading makes 272 read-slot figures sourceable from each
  node's own exemplars, which is what "the style is its exemplars" means operationally.
- **No — a facsimile or nothing**, extending OQ 18's rule to every kind of figure. Consistent, and it
  leaves the 542 unsourced until a library is reachable, which is the current state.
- **Yes, but as `editorial` with the quote as basis** — the survey informs a convention rather than
  measures a parameter. This is the weakest reading: it turns a surveyor's measurement into an editorial
  call to satisfy a label.

**The trap, stated in advance.** One exemplar is one building. `tidewater-georgian.roof_pitch.pitch_typical`
is `8:12` as a band over a population; Westover's roof is one hipped roof, and the 1939 sheet does not even
state its pitch. A survey quote can source a FACT about a building; it can source a BAND about a style only
where the band is the fact restated, or where several surveyed exemplars agree. The D6 table in
`docs/reports/wp-11.1-the-bench-without-a-literature.md` lists, per node, which parameters a survey speaks
to and whether it agrees, contradicts or is silent; nothing was applied.
