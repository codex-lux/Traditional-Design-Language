# Project review — where the language stands against its own vision, 3 September 2026

*A second comprehensive review, at Lucas's request, eight days after
`docs/reports/project-review-2026-08-26.md`: read the vision and the UI/UX documents, say where
execution stands against them, and say what is left. Phases 6, 7 and 8 and two parallel Phase 9s
have run in between — thirty-one work packages and forty-two reports since the last review.*

*Where a number here was produced by a run on 3 Sep it says so and gives the command's conditions.
Where it comes from a package report it names the report. **Nothing in this review is quoted from
`CLAUDE.md` alone**, which is a summary of summaries and is the one document in the tree whose
figures nothing polices.*

**The condition of the container, stated first because it bounds every measurement below.**
`jsonschema`, `ortools`, `ezdxf` and `ifcopenshell` are absent. So `compose.py` and `plan_check.py`
cannot be driven from their own CLIs at all — both die at `import jsonschema` inside `main()`
before doing any work, and this review drove them in process instead. Every placement below is the
**labelled** heuristic fall-back, never CP-SAT. DXF and IFC report COULD NOT EVALUATE with exit 3
and write nothing, which is the designed behaviour and is the third state working. **Any figure in
the Phase 9 reports that was measured on `auto` is therefore not reproducible here**, and the
sharpest of them is not: the 7.0 x 27.0 ft breakfast room that Lucas's second complaint is about
is an `auto` outcome, and on the heuristic the same room draws 12.6 x 15.4 and is fine
(`docs/reports/wp-9.6-the-check-that-could-not-see-the-drawing.md`).

---

## I — The verdict, in one paragraph

**The checker has arrived. The generator has not, and the last eight days were spent making the
critic able to say so.** The alphabet, the grammar, the vocabulary, the bindings, the solecisms and
the phrase layer are complete on the data. The critic now reads executable constraints, the fault
corpus with its exception preconditions, the drawn placement, the furniture against the rectangle
actually drawn, the arrangement variables and the elevation; `unjudged` is a real third state
wherever it has been measured, and a fourth (`not_applicable`) was added where the question does
not arise. The workbench meets all eight of its stated principles and every one of Lucas's five
rounds of interface feedback has been closed end to end. A brief goes in and a house comes out in
every format the vision names except a priced one. But the house that comes out is the one Lucas
read in August and called *"colorless green ideas sleeping furiously"* and read again on 1
September and called *"procedurally generated at a lower level than the idiom"* — and the package
he ruled the centrepiece that day, grouping-as-unit composition, **is not started**. The three
authoring decisions it waits on are recorded, and each says in its own entry that it must be
settled before any code.

---

## II — Distance to `VISION.md`

### §V, the compiler table

| Compiler part | 26 Aug | 3 Sep | What moved, and what is still missing |
|---|---|---|---|
| Language specification | the schemas | plan schema **0.4.0** | 0.2.0 → 0.3.0 admitted placed geometry and placed openings (WP-6.2); 0.4.0 admits the revision report (the critique line's WP-9.1) |
| Linters | 30 checks | **46** — 43 in the loop plus three appended suites | citations, ids, moves, critic-suspects, grouping rules, openings, gazetteer, assets. Read the runner's own second number, never `len(CHECKS)` |
| Type checker | seven layers, geometry-blind | a **`drawn`** layer, arrangement variables, furniture against the drawn rectangle, the shape band | Twenty-seven of the twenty-eight plan-measurable faults were UNJUDGED until the arrangement line's WP-9.1, because nothing had ever supplied a plan-arrangement variable |
| Front end | search default, proof opt-in | `auto` everywhere a user sees a drawing; a revision loop on by default | **It still programs the wrong number of rooms into the block.** §IV |
| Intermediate representation | declared record | placed openings with wall, position, hinge and rank; the stair; fixtures; relaxations located | An opening the placement cannot realise is marked unplaced with a reason and never deleted |
| Back end | walls, roof, elevation | unchanged in scope; one placement per drawing set (WP-6.4) | The elevation still states **44 numeric literals and 7 ratios** as its own measurements; they are metered by `build/critic_suspects.py`, not removed — `oq/thirty-five-measurements-the-elevation-states-as-literals` |
| Object code | SVG, DXF, IFC | unchanged | *"drawings a builder can price"* is still false, and gated on a partner by design |
| Runtime | 24 tools, 11 surfaces | **26 tools, 12 surfaces**, critique and revise routes | The ceiling is about **one editor**: one evaluate is 338 ms of CPU against a 400 ms debounce (`docs/reports/infrastructure-audit.md`) |

### §VII, the commitments

| Commitment | 26 Aug | 3 Sep |
|---|---|---|
| Unjudged is not passed | met structurally, **breached live** in the elevation | **Met, and extended.** OQ 52 closed; a fourth state for the question that does not arise; 331 exception preconditions read for the first time (WP-8.4); a placed revision loop refuses to accept a placement it could not judge. The residue is the 44 elevation literals, metered rather than withheld |
| A rule the sources do not determine is deferred | met | Met — and `oq/register-is-not-style` states its own trap in advance: *a licence to condition a band is a licence to invent* |
| Sources, or an honest mark | met | Met. OQ 18's source half and OQ 7 through OQ 11 remain environment-blocked. The plan-layer study carries a caveat on **every figure**, not only every quotation: transcribed, checked against a reproduction, **no facsimile read here** |
| Prose stays beside the test | met | Met |
| Open questions numbered, not silently decided | met | Met, and the mechanism was rebuilt after five id collisions in four days: a directory, one file per question, numbers frozen at 99, every new question named by a slug. The residue is that the citation guard validates about a sixth of the named namespace — `oq/a-slug-in-a-code-span-is-not-checked` |
| Findings matter as much as code | met, two lapses | Met. **68 reports**, counted on disk and including this one. The audit-of-the-audit has become the tradition (WP-6.4, WP-7.5, WP-8.6, and both Phase 9 lines' fourth packages) and is now the highest-yield technique in the repository |
| The drawing is a render of the data | met | Met — and a drawing set is now **one building**, which it was not: the plan sheet, the downloaded DXF and the section were three different placements of the same house until WP-6.4 |
| Several candidates, never one, never good | met | Met |
| The generator refuses, and refusals are content | met | Met in the corpus and the move registry (nine stated refusals). **Not met in the decision log** — see §IV |
| Compromises are counted and reported | **half met**, P7 unmet | **Met.** Relaxations carry a position and both renderers draw the mark where the cut falls |

### §XI, the horizon

1. **Proof, not preference** — delivered, and the default flipped: `auto` is now what a reader sees, and the plate names the engine that ran rather than asserting one.
2. **Leaving the system** — half delivered still. Drawings and IFC yes; the details library and the generated guidelines no (WP-5.3, and its stated precondition closed on 25 August).
3. **Reading drawings** — delivered (WP-5.5).
4. **Peer trunks** — unstarted; even the scoping note WP-4.7 asks for is unwritten.
5. **Cost** — deferred on purpose.

---

## III — Distance to the UI/UX specification

*The specification bundle itself was never committed and exists on no reachable disk; the 26
August review records this and it is still true. What survives in-repo is authoritative: the layer
spec, the product spec and its "what it will not claim" list, Graphic Standard № 1 verbatim in
`tokens.css`, the P1 through P8 statements quoted in the nineteen component headers, the
per-surface intent in the twelve surface headers, and the executable assertions in the browser
walk.*

**All eight principles are met.** P7 — a compromise is counted *and appears on the drawing, at its
location* — was the one the last review found knowingly unmet, and it closed the same day.

**Twelve surfaces are live**; the thirteenth, the Console, was struck by ruling rather than built,
and the component header that named it says so in place rather than deleting the reference.

**The only genuinely unbuilt interface** is the pair of hatched cards on Details & Export: the
per-style design guidelines book and the details library, both WP-5.3, both stating that ranked
substitution sets are planned structure the corpus does not yet hold. Every other disabled control
in the application is state-gated, not stub-gated.

**Every round of Lucas's interface feedback has been closed**, and each is worth naming because the
pattern in them is the same:

- *"extraordinarily overwhelming … no apparent search bar"* → the URL became the citation grammar
  written down, a palette over every named thing in the corpus, filters in the query string, an
  Overview to land on. Machine usability was proved undamaged by showing four server files byte-identical.
- *"you can never really actually read the dimensions … room labels cut off by walls"* → the
  loupe, the label fitter that breaks before it shrinks and never truncates, and one
  double-counting line that was causing four separate plate defects at once.
- *"the map is VERY crude and doesn't take well to zooming in"* → **two defects wearing one
  symptom**: `vector-effect` set on a group, where it does not inherit, so the coastline's pen was
  0.7 degrees of longitude wide; and genuinely one outline for every scale, now three tiers with
  the legend printing what is actually on the plate.
- *"the 82 is the highest score, then a 36 for second place, then back up"* → the number ran the
  wrong way, the sequence was not the ranking, and the line under it was a legend rather than
  arithmetic. All three fixed; the order is now named on the surface.
- The two rendered sheets that were meaningless → Phases 6 and 9.

**Recorded and deliberately open**: the loupe magnifies the pen along with the drawing (OQ 66); the
rail's tools are not in the palette, by ruling, because the rail is a conversation and not a menu;
no per-surface layout memory; the drawn-label guard covers one of five SVG emitters; a component
that renders a structured decision log is dead code; and the wall drag still writes a *placed*
dimension into the *declared* record, which WP-6.1 named as wanting a ruling and which has not had
one.

**Audience coverage against §IX.** The architect and the classicist are served: every claim reaches
its source, the cascade is a first-class object, and disagreeing with the corpus is a supported
act. The drafter is served in both directions. The production builder is unserved on cost, by
design. **The plan-development lead is served for reading and criticising and is not yet served for
the promise the vision makes them** — *"they can ask for four plans and get four plans"* — because
of §IV.

---

## IV — Live wrongness, ranked above absence

*As in the last review: things the system says that are not true outrank things it does not yet do.
The order has changed completely, because the last review's four items are all closed.*

### 1. The parti is not the type, and no score term can fix it

`centre-passage-double-pile` names eleven enclosed ground rooms and a porch, and the generator
places twelve enclosed spaces. **Its three named exemplars hold six each where the count is
established** — Gunston Hall's six are enumerated by the survey, Drayton Hall's six are named in
its own — in a clear extent about three feet *smaller* on each dimension than what the generator
draws. Six of the parti's eleven rooms are service, and all three exemplars put their service in a
basement, an outbuilding or a wing.

Halve every compartment in a house whose depth is fixed and the compartments become slivers.
**Nine of eleven slivers are inside their area band and outside their width or proportion band** —
the kitchen at 10 x 30 sits comfortably inside `area_sf [120, 340]` while standing 67% over its
proportion ceiling. Area was never the binding constraint, which is why the whole of the critique
line's sweeps moved nothing: they re-ranked candidates drawn from a pool that had already accepted
the wrong number of rooms.

**Ruled 2 September**: strip the service out of the diagram and teach the generator to build the
dependency. That needs a hyphen and a wing in the placement, which nothing today can produce, and
it turns the footprint's single growth mode into a choice.
`oq/the-parti-dissolved-its-own-dependencies`.

### 2. The model is a good checker and a bad generator, and the diagnosis is precise

*"An area band plus a width band plus a proportion band plus adjacency edges is a good CHECKER and
a bad GENERATOR, because a band carries no direction of causation."* Four bands over two free
variables is under-determined; a thousand rectangles satisfy it; **area was satisfiable at any
shape, so area is what the generator satisfied**. The tradition never had that freedom because it
never chose two numbers at once: four period sources describe a *sequence of commitments* in which
each step removes freedom from the next, and the facade is a **result** rather than an input.

The corpus already contains that model, in English, in one sentence of `room-vernacular.json`, and
nothing derives from it. Every room carries its length arithmetic in `critical_dimension` and
nothing parses it — one function hand-ports the stair hall's copy of it while its own docstring
says it has been read by nothing.

**And the largest missing thing is an object rather than a rule: the circulation system.** Kerr
opens on thoroughfares with *"These the skeleton of plan"* and hangs rooms off the route. This
corpus has rooms with door lists and lets circulation emerge, which is what §V's measurement below
shows: **121 of 123 heuristic fatals read *cannot be reached from outside the house***.

`docs/reports/wp-9.2-what-the-tradition-actually-does.md`, and read its §6 — eleven things that
must not be coded yet — before building anything from it.

### 3. Two axes the corpus cannot say, and one band pointing the wrong way

**Register** is ruled a first-class axis and nothing is built; four consequences are explicitly
undecided, and until they are, any single passage floor convicts one population to acquit the
other. **Establishment** is the same question wearing a different hat and has not been put.

And **29 non-circulation room records forbid the square that the tradition was aiming at**. Mount
Vernon's Front Parlor is 1.015 and its Dining Room 1.133; both are below their own bands. No
period source found states a minimum room ratio. The critique line's fourth package nearly built
that charge, watched it convict both good reference plans, and deleted it as unsupported — the
truer reason being that it is backwards, **and 29 records still tell the next package to build it
again**. `oq/the-proportion-band-forbids-the-square`, and it wants a ruling rather than a commit.

### 4. A licence that never reaches the flagship style

All three exception-selection sites test the style id for equality, so a licence written on
`georgian-colonial-american` never reaches `tidewater-georgian`. The Tidewater plan's porch fault
is not the Georgian licence failing; it is the licence never being consulted.
`oq/a-licence-matches-the-style-id-exactly-and-never-its-descendants`, unruled, and it must not be
"fixed" by copying exceptions down the tree.

### 5. Both reference plans fail their own span capacity and the validator has no span finding

Between the three real bearing lines the clear span on the reference plan is 49.93 ft against a
20 ft capacity. The plans now fail loudly, which is the check working; what is missing is that
`plan_check` says nothing about span at all, and the credit a short bearing wall gets across the
whole plate is still wrong. OQ 98.

---

## V — What this review measured, on 3 September

*Commands and conditions as stated in the preamble. Times are wall clock in this container.*

**The composer, both briefs, revision off.** `family-georgian` returned four candidates in 27.5 s
and `bungalow-small` three in 14.7 s. No errors, no dropped candidates.

| brief | candidate | parti | score | fatal | serious | minor |
|---|---|---|---|---|---|---|
| family-georgian | 1 | `centre-passage-double-pile` | 73.6 | 0 | 24 | 73 |
| family-georgian | 2 | `five-part-palladian` | 63.7 | 0 | 30 | 97 |
| family-georgian | 3 | `side-hall-townhouse` | 61.0 | 0 | 21 | 57 |
| family-georgian | 4 | `foursquare-quadrant` | 56.9 | 0 | 22 | 62 |
| bungalow-small | 1 | `bungalow-open-linear` | 67.9 | 0 | 4 | 47 |
| bungalow-small | 2 | `connected-farmstead` | 63.0 | 0 | 9 | 54 |
| bungalow-small | 3 | `hall-and-parlor` | 60.8 | 0 | 8 | 45 |

Seven authored, genuinely contrasting `trades_away` statements came back with them. That half of
§V works as written.

**But the score prints to one decimal over a large silence.** Per candidate, between **124 and 130
solecism rules and between 17 and 29 canon rules go unjudged**. The candidates carry the count;
this review's point is that the decimal and the silence sit in the same column.

**The revision loop, on the same brief, four rounds.** 50.3 s.

| | value |
|---|---|
| moves applied | **5** |
| rounds refused | **37** |
| total score movement, four candidates | **+0.4** |

The loop is real, it rolls back byte-identically, and it is very nearly inert on this brief at this
engine — which is the loop working as ruled against a program that does not fit its type, not the
loop failing.

**No refusal ever reached the decision log.** Across seven candidates and 105 decision entries:
77 `assumption`, 2 `unsolved`, and **0 of kind `refusal`**, a kind the log's own reader defines.
The commitment in §VII is met in the corpus and in the move registry and is not visible here.

**The two shipped reference plans, declared and then placed.**

| plan | fatal declared | fatal placed | rooms unreachable | faults unjudged |
|---|---|---|---|---|
| `spec-builder-colonial` | 4 | **10** | 6 of 21 | 126 |
| `tidewater-georgian-careful` | 0 | **3** | 3 of 24 | 120 |

Every added fatal is the same sentence: *"X cannot be reached from outside the house on the
drawing."* That is §IV.2's missing object, reproduced on the corpus's own benchmarks.

**The analyst.** `build/critique.py` runs from its own CLI in about 1.5 s and sorts what it finds:

| plan | actionable | placement | critic-suspect | architect | advisory |
|---|---|---|---|---|---|
| `tidewater-georgian-careful` | 14 | 28 | 6 | **102** | 0 |
| `spec-builder-colonial` | 46 | 26 | 5 | **119** | 2 |

The triage works. It triages roughly two thirds of what it sees to a person, which is the division
of labour the vision asks for and is also a measure of how little a registry move can currently
reach.

**The drawings.** All five sheets render in about 1.2 s in process. Two of the renderers — the plan
sheet and the section — **have no CLI at all**; they are modules the workbench drives, so "the full
drawing set from the command line" is not available today and the last review's pipeline sentence
overstates it. The elevation and the roof do have CLIs and both succeed. DXF and IFC refuse
cleanly, exit 3, nothing written.

The careful reference plan carries **7 relaxations, worst 4.81 ft off the bay grid**.

---

## VI — The road, in order

*The judgment this review is prepared to defend: **the disease before the symptoms**, which is
Lucas's own phrase from 1 September. Every item in §IV.1 through §IV.3 is one problem seen from
three sides, and none of it is reachable by another score term.*

**Tier 1 — three rulings, then the centrepiece.**

1. **The three authoring decisions, each of which its own entry says must be settled before code.**
   (a) `oq/the-parti-dissolved-its-own-dependencies`: is a dependency a second plan level, a second
   massing element, or a new record kind; is the hyphen a room or a connector with its own schema;
   what does a brief say when the site cannot take one. (b) `oq/register-is-not-style`: where
   register lives, how many values it takes and whether they are ordered, whether it conditions a
   band or selects between bands. (c) `oq/the-proportion-band-forbids-the-square`: remove the
   floors, set them to 1.0, or replace them with a *direction* — the study's own reading favours
   the third, and it changes what `proportion` means in 54 records. Three more sit beside them
   unanswered in the study's §7: whether the facade is a result, whether the ordering is the
   compiler's architecture or only its explanation, and whether the corpus takes the
   ceiling-height fault.
2. **The unit of composition** — the arrangement line's WP-9.4, not started, and named the
   centrepiece at planning. A `parti_slice()` that *states* the macro-plan the way
   `courtyard_slice()` states a ring, because the heuristic cannot search for either; the
   dependency and the hyphen as placeable elements, with `five-part-palladian` as the working model
   it should be read against; and `expansion_logic` and `grows_by` getting their first real
   readers. Then the arrangement line's WP-9.3 remainder: the passage clamped to the **cascaded**
   kit's own floor, and an arrival-aware stair.
3. **The precedents' image half**, which is the only thing that turns Tier 1 from editorial into
   sourced. The wanted list is written and waiting on a download only Lucas can do; then five to
   ten transcribed plans, the measuring script that does not yet exist, and the calibration run.
   *A critic that convicts Drayton Hall is wrong until proven otherwise.*

**Tier 2 — truth repairs still standing.** The licence that never reaches its descendants; a span
finding in the validator (OQ 98); the 44 elevation literals the critic scores the generator on;
the node parameter that contradicts a pack rule at one address (OQ 86) and the slot bound `open`
that inherits anyway (OQ 87); the six readers pointed at a raw kit where the answer is in the
cascade; the reference plan that fails its own style's hard rule (OQ 94, wants a ruling); the
unranked tie reported as the author's decision (OQ 38); and the eight score weights that have
never been tested against a plan anyone ranked by hand (OQ 66).

**Tier 3 — the last mile that exists on paper.** WP-8.7's tail: 181 cases already grouped by the
pack that settles them all at once, 36 unread, and a curve that says roughly a hundred more over a
dozen passes before the flip to opt-in inheritance is honest. **WP-5.3** — the guidelines book, the
details library, the modelling conventions — is the largest unstarted named deliverable, is
generatable from data so it cannot drift, and its stated precondition closed on 25 August, so the
deferral can be lifted whenever it is wanted. The harvest workflow that `oq/fetching-through-a-tier-the-proxy-denies`
ruled for and nobody built, which is what unblocks the images. And the deployment items before a
second person ever opens the bench.

**Gated by design and unchanged**: the cost layer, which must not have numbers authored for it, and
the peer trunks, which are scope-only.

---

## VII — Doc drift found by this review

**Fixed here:**

- `PLAN-OF-ACTION.md`'s progress board: the Arrangement row said *"9.2, 9.3, 9.4, 9.5 not
  started"* against a WP-9.5 that is complete, a WP-9.2 half done, a WP-9.3 part built and two
  more packages (9.6, 9.7) that shipped without sections. The board's own date, five packages
  stale. §0's "six phases and twenty-two work packages", which the file outgrew long ago.
- WP-5.3 and WP-5.4 had **no Status line at all**, in a document whose first rule is that every
  package carries one.
- `CLAUDE.md`'s "Where the work stands" heading, dated 27 August above entries dated 2 September.

**Found, not fixed, because this review could not tell which figure is right:** the search index's
own size is published as **665** in the layer doc and the product README and as **666** in
`CLAUDE.md`. Deriving it needs the server, which needs libraries this container lacks. It is one
of the numbers `check_counts.py` does not police, because it is not derived from the corpus.

**Left, with the reason:**

- Every count and status inside a historical package report. Reports are records of their moment
  and are never retro-edited; this one will be a record of its moment too.
- The last review's pipeline sentence, which reads as though the drawing set comes out of the CLI.
  Correcting a previous review's prose would be rewriting the record rather than adding to it;
  §V states the finding instead.

---

## VIII — What this review deliberately did not do

- **It adjudicated nothing and ruled nothing.** The three decisions in §VI.1 belong to Lucas and
  each is already written down with its options costed.
- **It fixed no defect and moved no number in the corpus.** §IV describes five things; it patches
  none of them, for the reason the 26 August review gave and this one repeats: a review that
  quietly moved a reference-plan count would be the exact failure the fault corpus exists to
  prevent.
- **It raised no new open question.** Everything found is already named. That is itself a finding
  about the register: on this reading, the project's problem is no longer that it does not know
  what is wrong with it.
- **It ran no full check suite** (forty minutes) and **could not evaluate the proof engine, the
  CAD exports or the workbench server suite**, for want of four libraries. Those are named as
  unevaluated in §V rather than assumed to be as they were.
- **It re-derived what it could and attributed the rest.** Every figure in §V came out of a run
  made for this document; the Phase 9 figures it quotes are attributed to the report that measured
  them, because re-deriving them here would need an engine this container does not have.
