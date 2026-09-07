# oq/a-surveyors-prose-may-source-an-envelope-figure — may a HABS written-data quote source a `measured` kit parameter?

*Status: RULED 5 Sep 2026 · Raised in: WP-11.1, the precedent bench (4 Sep 2026)*

**RULED 5 SEP 2026 BY LUCAS: YES, FOR THE ENVELOPE CLASS, QUOTE-CHECKED.** A survey measurement may
source a `measured` kit parameter of the envelope class at `confidence: medium`. Dated from when the
ruling arrived, not from when it was asked -- the discipline
`oq/a-baked-pack-value-is-a-second-delivery-path`'s neighbour records after PR #26 published an
authorisation that did not yet exist.

**Three things measured while putting the question, each of which corrects something above.**

1. **It needs no schema change and no new mechanism.** `schema/kit.schema.json`'s `$defs/parameter`
   already types `source` as a free string and `confidence` as `high|medium|low`, and
   `check_precedents.py`'s `KIT_POINTER_RE` already resolves BOTH `precedents/<id>#survey.<field>`
   and `precedents/<id>#measurements[<n>]`. The checker has printed `0 kit figure(s) cite a survey`
   on every run since WP-11.1. What was missing was permission, not machinery.

2. **This entry's own estimate of the yield was wrong by an order of magnitude.** It says the
   yes-reading "makes 272 read-slot figures sourceable from each node's own exemplars". Classified
   by hand across 155 surveys and 240 survey-against-kit readings from two tranches, the figures
   where a survey states a number IN THE PARAMETER'S OWN QUANTITY are **of the order of a dozen**.
   196 of the 240 readings are SILENT and most of the 27 agreements agree in KIND and are silent on
   the NUMBER -- a categorical agreement cannot source a figure at all. The case for the ruling is
   not this year's dozen; it is that a corpus where a figure CAN cite its building is a different
   corpus, and that Europe's listing descriptions are richer than HABS.

3. **The trap this entry names closes MECHANICALLY, and the fix is to point at a MEASUREMENT.**
   The entry says *"a source pointer that resolves is not a source that agrees ... that comparison
   is a reader's"*. It need not be. `measurements[]` carries a typed `value` and a `unit` from a
   closed enum (`ft`, `in`, `count`, `ratio`, `deg`, `rise_in_12`) that matches the kit's own units,
   so a checker CAN hold the parameter's number against the measurement's number. Therefore: a
   `kind: measured` parameter citing a precedent must use the `#measurements[<n>]` form, and the
   `#survey.<field>` form stays legal only for a parameter that is NOT `measured` -- a number cites
   a number. `check_precedents.py::kit_source_agrees` decides it in three verdicts, never a bool.

**What the ruling does NOT license.** A band is not a fact about one building: a survey quote sources
a BAND only where the band is the fact restated, or where several surveyed exemplars agree. Where one
building's figure sits INSIDE a band it did not set -- `neoclassical-revival.porch_depth.depth_min_ft`
8 ft against Whitehall's 18 ft portico -- that is a NON-VIOLATION, not a source, and citing it would
be the laundering this ruling exists to avoid. And it reaches no moulding profile: OQ 7-11 and OQ 18's
source half still need legible facsimiles, and this is a surveyor's own recorded measurement.


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
